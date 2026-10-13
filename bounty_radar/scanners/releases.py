from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from bounty_radar.github_api import GitHubClient
from bounty_radar.models import Signal
from bounty_radar.scanners.content import KEYWORD_GROUPS, SEVERITY_BY_TYPE


def _parse_github_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _release_id(release: dict[str, Any]) -> str:
    return str(release.get("id") or release.get("tag_name") or release.get("html_url") or "")


def scan_releases(
    api: GitHubClient,
    repo: dict[str, Any],
    state: dict[str, str],
    *,
    lookback_hours: int,
    max_releases: int,
    now: datetime,
) -> tuple[list[Signal], dict[str, str]]:
    full_name = repo["full_name"]
    releases = api.list_releases(full_name, max_releases=max_releases)
    if not releases:
        return [], {}

    signals: list[Signal] = []
    state_updates: dict[str, str] = {}
    previous_latest_id = state.get("latest_release_id")
    latest_id = _release_id(releases[0])
    if latest_id:
        state_updates["latest_release_id"] = latest_id

    lookback_start = now - timedelta(hours=lookback_hours)

    for release in releases:
        release_id = _release_id(release)
        if not release_id:
            continue
        if previous_latest_id and release_id == previous_latest_id:
            break

        published_at = _parse_github_datetime(release.get("published_at"))
        if previous_latest_id is None and published_at and published_at < lookback_start:
            continue

        title = str(release.get("name") or release.get("tag_name") or "release")
        url = release.get("html_url") or f"https://github.com/{full_name}/releases"
        tag = str(release.get("tag_name") or "")
        body = str(release.get("body") or "")
        text = f"{title}\n{tag}\n{body}".lower()

        signals.append(
            Signal(
                signal_type="release_new",
                key=tag or title,
                title="New GitHub release detected",
                severity=3,
                details=f"{full_name} published release {title}.",
                fingerprint=f"release-new:{release_id}",
                url=url,
                metadata={
                    "release_id": release_id,
                    "tag": tag,
                    "published_at": release.get("published_at"),
                    "prerelease": bool(release.get("prerelease")),
                },
            )
        )

        for signal_type, terms in KEYWORD_GROUPS.items():
            for term in terms:
                if term.lower() not in text:
                    continue
                signals.append(
                    Signal(
                        signal_type=signal_type,
                        key=term,
                        title=f"Release mentions {term}",
                        severity=SEVERITY_BY_TYPE[signal_type],
                        details=f"Release {title} mentions '{term}'.",
                        fingerprint=f"release-text:{release_id}:{signal_type}:{term}",
                        url=url,
                        metadata={
                            "release_id": release_id,
                            "tag": tag,
                            "source": "release",
                            "term": term,
                        },
                    )
                )

    return signals, state_updates
