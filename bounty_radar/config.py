from __future__ import annotations

import json
import os
import ssl
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - dotenv is optional at import time
    load_dotenv = None

try:
    import certifi
except ImportError:  # pragma: no cover - certifi is optional at import time
    certifi = None


PROJECT_ROOT = Path(__file__).resolve().parents[1]
VESPER_ROOT = PROJECT_ROOT.parent
USER_HOME = Path.home()

DEFAULT_ENV_FILES = (
    str(PROJECT_ROOT / ".env"),
    str(VESPER_ROOT / ".env.audit-notify"),
    str(VESPER_ROOT / ".env"),
    str(VESPER_ROOT / "Vesper_Audit_Lab" / ".env"),
    str(USER_HOME / "Code" / "Polymarket" / ".env"),
    str(USER_HOME / "Code" / "EQXBot" / ".env"),
    str(USER_HOME / "Documents" / "GitHub" / "EQXBot" / ".env"),
)


@dataclass
class OrgTarget:
    name: str
    max_repos: int | None = None
    include_archived: bool = False


@dataclass
class SourceTarget:
    name: str
    url: str
    kind: str = "auto"
    require_direct_submit: bool = False
    require_external_program_url: bool = False
    include_terms: list[str] = field(default_factory=list)
    exclude_terms: list[str] = field(default_factory=list)
    url_terms: list[str] = field(default_factory=list)
    max_items: int = 25
    browser: bool = False
    browser_wait_ms: int = 5000


@dataclass
class RadarSettings:
    lookback_hours: int = 24
    baseline_days: int = 7
    velocity_spike_multiplier: float = 2.0
    velocity_min_commits: int = 8
    heat_score_spike_threshold: int = 25
    enable_code_search: bool = True
    max_code_search_terms: int = 20
    max_org_repos: int = 75
    enable_release_scan: bool = True
    max_releases: int = 5
    source_alert_min_severity: int = 4
    enable_direct_program_discovery: bool = False
    max_direct_program_results: int = 6

    @classmethod
    def from_dict(cls, raw: dict[str, Any] | None) -> "RadarSettings":
        raw = raw or {}
        return cls(
            lookback_hours=int(raw.get("lookback_hours", cls.lookback_hours)),
            baseline_days=int(raw.get("baseline_days", cls.baseline_days)),
            velocity_spike_multiplier=float(
                raw.get("velocity_spike_multiplier", cls.velocity_spike_multiplier)
            ),
            velocity_min_commits=int(raw.get("velocity_min_commits", cls.velocity_min_commits)),
            heat_score_spike_threshold=int(
                raw.get("heat_score_spike_threshold", cls.heat_score_spike_threshold)
            ),
            enable_code_search=_coerce_bool(
                raw.get("enable_code_search"),
                cls.enable_code_search,
            ),
            max_code_search_terms=int(raw.get("max_code_search_terms", cls.max_code_search_terms)),
            max_org_repos=int(raw.get("max_org_repos", cls.max_org_repos)),
            enable_release_scan=_coerce_bool(
                raw.get("enable_release_scan"),
                cls.enable_release_scan,
            ),
            max_releases=int(raw.get("max_releases", cls.max_releases)),
            source_alert_min_severity=int(
                raw.get("source_alert_min_severity", cls.source_alert_min_severity)
            ),
            enable_direct_program_discovery=_coerce_bool(
                raw.get("enable_direct_program_discovery"),
                cls.enable_direct_program_discovery,
            ),
            max_direct_program_results=int(
                raw.get("max_direct_program_results", cls.max_direct_program_results)
            ),
        )


@dataclass
class TrackedConfig:
    orgs: list[OrgTarget] = field(default_factory=list)
    repos: list[str] = field(default_factory=list)
    sources: list[SourceTarget] = field(default_factory=list)
    settings: RadarSettings = field(default_factory=RadarSettings)


def load_environment(env_path: str | None = None) -> None:
    if load_dotenv is None:
        return
    if env_path:
        load_dotenv(env_path, override=False)
        return
    for path in DEFAULT_ENV_FILES:
        load_dotenv(path, override=False)


def resolve_github_token() -> str | None:
    for key in ("BOUNTY_RADAR_GITHUB_TOKEN", "GITHUB_TOKEN", "GH_TOKEN"):
        value = os.getenv(key)
        if value:
            return value

    try:
        result = subprocess.run(
            ["gh", "auth", "token"],
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (FileNotFoundError, subprocess.SubprocessError):
        return None

    token = result.stdout.strip()
    if result.returncode != 0 or not token:
        return None
    return token


def load_tracked_config(path: str | Path) -> TrackedConfig:
    config_path = Path(path)
    with config_path.open("r", encoding="utf-8") as fh:
        raw = json.load(fh)

    orgs: list[OrgTarget] = []
    for entry in raw.get("orgs", []):
        if isinstance(entry, str):
            orgs.append(OrgTarget(name=entry))
        elif isinstance(entry, dict) and entry.get("name"):
            orgs.append(
                OrgTarget(
                    name=str(entry["name"]),
                    max_repos=int(entry["max_repos"]) if entry.get("max_repos") is not None else None,
                    include_archived=bool(entry.get("include_archived", False)),
                )
            )

    repos = [str(repo).strip() for repo in raw.get("repos", []) if str(repo).strip()]
    sources: list[SourceTarget] = []
    for entry in raw.get("sources", []):
        if not isinstance(entry, dict) or not entry.get("name") or not entry.get("url"):
            continue
        sources.append(
            SourceTarget(
                name=str(entry["name"]),
                url=str(entry["url"]),
                kind=str(entry.get("kind", "auto")),
                require_direct_submit=_coerce_bool(entry.get("require_direct_submit"), False),
                require_external_program_url=_coerce_bool(
                    entry.get("require_external_program_url"), False
                ),
                include_terms=[str(term) for term in entry.get("include_terms", [])],
                exclude_terms=[str(term) for term in entry.get("exclude_terms", [])],
                url_terms=[str(term) for term in entry.get("url_terms", [])],
                max_items=int(entry.get("max_items", 25)),
                browser=_coerce_bool(entry.get("browser"), False)
                or str(entry.get("kind", "")).lower() in {"browser", "browser-html"},
                browser_wait_ms=int(entry.get("browser_wait_ms", 5000)),
            )
        )
    return TrackedConfig(
        orgs=orgs,
        repos=repos,
        sources=sources,
        settings=RadarSettings.from_dict(raw.get("settings")),
    )


def env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}


def requests_verify_path() -> str | bool:
    for key in ("BOUNTY_RADAR_CA_BUNDLE", "REQUESTS_CA_BUNDLE", "SSL_CERT_FILE"):
        value = os.getenv(key)
        if value:
            return value

    default_paths = ssl.get_default_verify_paths()
    if default_paths.cafile and Path(default_paths.cafile).exists():
        return default_paths.cafile

    if certifi is not None:
        return certifi.where()

    return True


def _coerce_bool(value: Any, default: bool) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return bool(value)
    return str(value).lower() in {"1", "true", "yes", "on"}
