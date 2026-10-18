from __future__ import annotations

import hashlib
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse

import requests

from bounty_radar.browser_fetch import BrowserFetchError, fetch_rendered_html
from bounty_radar.config import SourceTarget, requests_verify_path
from bounty_radar.models import Signal


LAUNCH_TERMS = (
    "new",
    "fresh",
    "freshly tracked",
    "launch",
    "launched",
    "live",
    "starts",
    "started",
    "opening",
    "upcoming",
)

BOUNTY_TERMS = (
    "bug bounty",
    "bounty",
    "competition",
    "audit contest",
    "contest",
    "security review",
    "public review",
    "scope",
    "reward",
    "payout",
    "prize",
)

PLATFORM_TERMS = (
    "hackenproof",
    "cantina",
    "sherlock",
    "code4rena",
    "codehawks",
    "immunefi",
    "hackerone",
    "bugcrowd",
    "intigriti",
    "yeswehack",
)

DIRECT_SUBMIT_BLOCK_TERMS = (
    "deposit required",
    "points required",
    "kyc required",
    "kyc",
    "private bounty",
    "private program",
    "private",
    "invite only",
    "invitation only",
    "application required",
    "apply to join",
    "request access",
    "waitlist",
)

PLATFORM_HOST_SUFFIXES = (
    "bountyhunte.rs",
    "hackenproof.com",
    "cantina.xyz",
    "immunefi.com",
    "intigriti.com",
    "app.intigriti.com",
    "yeswehack.com",
    "hackerone.com",
    "bugcrowd.com",
    "code4rena.com",
    "codehawks.cyfrin.io",
    "audits.sherlock.xyz",
)

HACKENPROOF_OFFICIAL_INDEX_PATHS = {
    "/programs",
    "/audit-programs",
}


@dataclass
class SourceItem:
    title: str
    url: str
    summary: str = ""
    published_at: str | None = None


class _LinkParser(HTMLParser):
    def __init__(self, base_url: str) -> None:
        super().__init__()
        self.base_url = base_url
        self._href: str | None = None
        self._fallback_title: str = ""
        self._chunks: list[str] = []
        self._article_depth = 0
        self._article_chunks: list[str] = []
        self._article_link_start = 0
        self.links: list[SourceItem] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() == "article":
            if self._article_depth == 0:
                self._article_chunks = []
                self._article_link_start = len(self.links)
            self._article_depth += 1
            return
        if tag.lower() != "a":
            return
        attr_map = {key.lower(): value for key, value in attrs}
        href = attr_map.get("href")
        if not href:
            return
        self._href = urljoin(self.base_url, href)
        self._fallback_title = attr_map.get("aria-label") or attr_map.get("title") or ""
        self._chunks = []

    def handle_data(self, data: str) -> None:
        if self._article_depth:
            self._article_chunks.append(data)
        if self._href:
            self._chunks.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "article":
            self._article_depth = max(0, self._article_depth - 1)
            if self._article_depth == 0:
                summary = " ".join("".join(self._article_chunks).split())[:1000]
                for item in self.links[self._article_link_start :]:
                    item.summary = summary
                self._article_chunks = []
            return
        if tag.lower() != "a" or not self._href:
            return
        title = " ".join("".join(self._chunks).split()) or self._fallback_title
        if title:
            summary = " ".join("".join(self._article_chunks).split())
            self.links.append(SourceItem(title=title, url=self._href, summary=summary[:1000]))
        self._href = None
        self._fallback_title = ""
        self._chunks = []


def _node_text(node: ET.Element, names: tuple[str, ...]) -> str:
    for child in list(node):
        local_name = child.tag.rsplit("}", 1)[-1].lower()
        if local_name in names and child.text:
            return " ".join(child.text.split())
    return ""


def _node_link(node: ET.Element, fallback_url: str) -> str:
    for child in list(node):
        local_name = child.tag.rsplit("}", 1)[-1].lower()
        if local_name != "link":
            continue
        href = child.attrib.get("href")
        if href:
            return href
        if child.text:
            return " ".join(child.text.split())
    return fallback_url


def _parse_feed(text: str, url: str) -> list[SourceItem]:
    root = ET.fromstring(text)
    items: list[SourceItem] = []
    for node in root.iter():
        local_name = node.tag.rsplit("}", 1)[-1].lower()
        if local_name not in {"item", "entry"}:
            continue
        title = _node_text(node, ("title",)) or "untitled item"
        item_url = _node_link(node, url)
        summary = _node_text(node, ("summary", "description", "content"))
        published_at = _node_text(node, ("published", "updated", "pubdate"))
        items.append(
            SourceItem(
                title=title,
                url=item_url,
                summary=summary,
                published_at=published_at or None,
            )
        )
    return items


def _parse_html(text: str, url: str) -> list[SourceItem]:
    parser = _LinkParser(url)
    parser.feed(text)
    return parser.links


def _infer_kind(source: SourceTarget, response_text: str) -> str:
    if source.kind in {"browser", "browser-html"}:
        return "html"
    if source.kind != "auto":
        return source.kind.lower()
    prefix = response_text.lstrip()[:120].lower()
    if prefix.startswith("<?xml") or prefix.startswith("<rss") or prefix.startswith("<feed"):
        return "feed"
    return "html"


def _matches_any(text: str, terms: list[str]) -> bool:
    lowered = text.lower()
    return any(term.lower() in lowered for term in terms)


def _is_platform_hosted_url(url: str) -> bool:
    host = urlparse(url).netloc.lower()
    if not host:
        return False
    return any(host == suffix or host.endswith(f".{suffix}") for suffix in PLATFORM_HOST_SUFFIXES)


def _is_hackenproof_official_index(url: str) -> bool:
    parsed = urlparse(url)
    host = parsed.netloc.lower().split(":", 1)[0]
    path = parsed.path.rstrip("/") or "/"
    return host in {"hackenproof.com", "www.hackenproof.com"} and (
        path in HACKENPROOF_OFFICIAL_INDEX_PATHS
    )


def _should_keep(source: SourceTarget, item: SourceItem) -> bool:
    text = f"{item.title}\n{item.summary}".lower()
    if source.url_terms and not _matches_any(item.url, source.url_terms):
        return False
    if source.include_terms and not _matches_any(text, source.include_terms):
        return False
    if source.exclude_terms and _matches_any(text, source.exclude_terms):
        return False
    if source.require_direct_submit and _matches_any(text, list(DIRECT_SUBMIT_BLOCK_TERMS)):
        return False
    if source.require_external_program_url and _is_platform_hosted_url(item.url):
        return False
    return True


def _fingerprint(item: SourceItem) -> str:
    key = item.url or item.title
    digest = hashlib.sha256(key.encode("utf-8")).hexdigest()[:20]
    return f"source-item:{digest}"


def _classify(item: SourceItem) -> tuple[str, int, list[str]]:
    text = f"{item.title}\n{item.summary}\n{item.url}".lower()
    matches: list[str] = []
    severity = 2

    for term in BOUNTY_TERMS:
        if term in text:
            matches.append(term)
            severity = max(severity, 4)

    for term in LAUNCH_TERMS:
        if term in text:
            matches.append(term)
            severity = min(5, max(severity, 3) + 1)
            break

    for term in PLATFORM_TERMS:
        if term in text:
            matches.append(term)
            severity = max(severity, 4)

    if re.search(r"\$[0-9][0-9,]*(?:\.[0-9]+)?\s*(?:k|m|b)?", text):
        matches.append("reward_amount")
        severity = max(severity, 4)

    signal_type = "source_launch" if severity >= 4 else "source_item"
    return signal_type, severity, sorted(set(matches))[:8]


def fetch_source_items(source: SourceTarget) -> tuple[list[SourceItem], list[str]]:
    errors: list[str] = []
    if source.browser:
        try:
            text = fetch_rendered_html(source.url, wait_ms=source.browser_wait_ms)
        except BrowserFetchError as exc:
            message = str(exc).replace("<source-name>", source.name)
            return [], [f"{source.name}: browser fetch failed: {message}"]
    else:
        try:
            response = requests.get(
                source.url,
                headers={"User-Agent": "bounty-radar/0.1"},
                timeout=30,
                verify=requests_verify_path(),
            )
            response.raise_for_status()
            text = response.text
        except requests.RequestException as exc:
            return [], [f"{source.name}: fetch failed: {exc}"]

    kind = _infer_kind(source, text)
    try:
        if kind in {"feed", "rss", "atom"}:
            items = _parse_feed(text, source.url)
        elif kind == "html":
            items = _parse_html(text, source.url)
        else:
            return [], [f"{source.name}: unsupported source kind '{source.kind}'"]
    except (ET.ParseError, ValueError) as exc:
        return [], [f"{source.name}: parse failed: {exc}"]

    kept: list[SourceItem] = []
    seen: set[str] = set()
    for item in items:
        if not _should_keep(source, item):
            continue
        fingerprint = _fingerprint(item)
        if fingerprint in seen:
            continue
        seen.add(fingerprint)
        kept.append(item)
        if len(kept) >= source.max_items:
            break
    if _is_hackenproof_official_index(source.url) and not kept:
        errors.append(
            f"{source.name}: official index verification unavailable: "
            "no qualifying listing links found; coverage degraded"
        )
    return kept, errors


def scan_source(source: SourceTarget) -> tuple[list[Signal], list[str]]:
    items, errors = fetch_source_items(source)
    signals = [signal_from_source_item(source.name, item) for item in items]
    return signals, errors


def signal_from_source_item(source_name: str, item: SourceItem) -> Signal:
    signal_type, severity, matches = _classify(item)
    return Signal(
        signal_type=signal_type,
        key=item.title[:120],
        title="Fresh bounty source item detected",
        severity=severity,
        details=f"{source_name} surfaced: {item.title}",
        fingerprint=_fingerprint(item),
        url=item.url,
        metadata={
            "source": source_name,
            "published_at": item.published_at,
            "matches": matches,
            "summary": item.summary[:500],
        },
    )
