#!/usr/bin/env python3
"""Quiet delta monitor for the first public Chainlink CCIP v2 USDC lane.

This file is deliberately standalone. It can run even when the main radar
package or SQLite database is unavailable, and it only reads Chainlink's public
documentation data plus its own local state file.
"""

from __future__ import annotations

import argparse
import json
import os
import ssl
import stat
import tempfile
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


LANES_URL = (
    "https://raw.githubusercontent.com/smartcontractkit/documentation/main/"
    "src/config/data/ccip/v1_2_0/mainnet/lanes.json"
)
TOKENS_URL = (
    "https://raw.githubusercontent.com/smartcontractkit/documentation/main/"
    "src/config/data/ccip/v1_2_0/mainnet/tokens.json"
)
DIRECTORY_URL = "https://docs.chain.link/ccip/directory/mainnet"
PROXY_VERSION = "USDCTokenPoolProxy 2.0.0"
REOPEN_EVIDENCE = (
    "a nonzero siloed lock/release child plus a mechanism transition and at least one of: "
    "old OnRamp removal before safe completion; excluded claims above recoverable lockbox "
    "liquidity; public cross-child bypass of an enabled bucket; or authenticated credit above "
    "burn/lock"
)
TOKEN_ENV_KEYS = (
    "TELEGRAM_BOT_TOKEN",
    "TELEGRAM_TOKEN",
    "AUDIT_TELEGRAM_BOT_TOKEN",
    "AUDIT_TELEGRAM_TOKEN",
    "BOUNTY_RADAR_TELEGRAM_BOT_TOKEN",
    "BOUNTY_RADAR_TELEGRAM_TOKEN",
)
CHAT_ENV_KEYS = (
    "TELEGRAM_CHAT_ID",
    "AUDIT_TELEGRAM_CHAT_ID",
    "BOUNTY_RADAR_TELEGRAM_CHAT_ID",
)
VESPER_ROOT = Path(__file__).resolve().parents[2]
FALLBACK_ENV_FILES = (
    VESPER_ROOT / ".env.audit-notify",
    VESPER_ROOT / ".env",
    Path.home() / "Code" / "Vesper" / ".env.audit-notify",
    Path.home() / "Code" / "Vesper" / ".env",
)


def _fetch_json(url: str, *, timeout: int = 30) -> dict[str, Any]:
    request = urllib.request.Request(url, headers={"User-Agent": "bounty-radar/ccip-usdc-watch"})
    context = ssl.create_default_context()
    with urllib.request.urlopen(request, timeout=timeout, context=context) as response:
        payload = json.load(response)
    if not isinstance(payload, dict):
        raise ValueError(f"Expected a JSON object from {url}")
    return payload


def _token_metadata(tokens: dict[str, Any], chain: str) -> dict[str, Any]:
    usdc = tokens.get("USDC", {})
    if not isinstance(usdc, dict):
        return {}
    metadata = usdc.get(chain, {})
    return metadata if isinstance(metadata, dict) else {}


def _positive_capacity(config: dict[str, Any]) -> bool:
    if not config.get("isEnabled", False):
        return False
    try:
        return int(config.get("capacity", "0")) > 0
    except (TypeError, ValueError):
        return False


def _route_id(source_chain: Any, destination_chain: Any) -> str:
    """Identify a logical route independently of replaceable ramp deployments."""
    return f"{source_chain}|{destination_chain}"


def _destination_off_ramp(
    lanes: dict[str, Any], source_chain: Any, destination_chain: Any
) -> dict[str, Any]:
    """Return the destination-chain OffRamp for a source-to-destination route.

    Chainlink's lane entry is keyed by the OnRamp direction. Its ``offRamp``
    lives on that entry's source chain and receives the reverse direction. The
    OffRamp that receives ``source_chain -> destination_chain`` therefore lives
    in the opposite ``destination_chain -> source_chain`` entry.
    """
    reverse_destinations = lanes.get(destination_chain, {})
    if not isinstance(reverse_destinations, dict):
        return {}
    reverse_lane = reverse_destinations.get(source_chain, {})
    if not isinstance(reverse_lane, dict):
        return {}
    off_ramp = reverse_lane.get("offRamp") or {}
    return off_ramp if isinstance(off_ramp, dict) else {}


def find_v2_usdc_lanes(lanes: dict[str, Any], tokens: dict[str, Any]) -> list[dict[str, Any]]:
    """Return public v2 USDC lanes, annotated for migration-candidate relevance."""
    matches: list[dict[str, Any]] = []
    for source_chain, destinations in lanes.items():
        if not isinstance(destinations, dict):
            continue
        for destination_chain, lane in destinations.items():
            if not isinstance(lane, dict):
                continue
            on_ramp = lane.get("onRamp") or {}
            source_side_off_ramp = lane.get("offRamp") or {}
            destination_off_ramp = _destination_off_ramp(
                lanes, source_chain, destination_chain
            )
            supported_tokens = lane.get("supportedTokens") or {}
            if (
                on_ramp.get("version") != "2.0.0"
                or destination_off_ramp.get("version") != "2.0.0"
            ):
                continue
            if not isinstance(supported_tokens, dict) or "USDC" not in supported_tokens:
                continue

            usdc_lane = supported_tokens.get("USDC") or {}
            rate_limits = usdc_lane.get("rateLimiterConfig") or {}
            inbound = rate_limits.get("in") or {}
            source_token = _token_metadata(tokens, source_chain)
            destination_token = _token_metadata(tokens, destination_chain)
            source_is_proxy = source_token.get("typeAndVersion") == PROXY_VERSION
            destination_is_proxy = destination_token.get("typeAndVersion") == PROXY_VERSION
            deployment_id = "|".join(
                (
                    str(source_chain),
                    str(destination_chain),
                    str(on_ramp.get("address", "")),
                    str(destination_off_ramp.get("address", "")),
                )
            )
            matches.append(
                {
                    "id": _route_id(source_chain, destination_chain),
                    "deployment_id": deployment_id,
                    "source_chain": source_chain,
                    "destination_chain": destination_chain,
                    "on_ramp": on_ramp.get("address", ""),
                    "off_ramp": destination_off_ramp.get("address", ""),
                    "source_side_off_ramp": source_side_off_ramp.get("address", ""),
                    "source_pool": source_token.get("poolAddress", ""),
                    "destination_pool": destination_token.get("poolAddress", ""),
                    "source_pool_type": source_token.get("typeAndVersion", ""),
                    "destination_pool_type": destination_token.get("typeAndVersion", ""),
                    "proxy_candidate": source_is_proxy and destination_is_proxy,
                    "inbound_rate_limit_enabled": _positive_capacity(inbound),
                    "inbound_capacity": str(inbound.get("capacity", "0")),
                    "directory_url": DIRECTORY_URL,
                }
            )
    return sorted(matches, key=lambda item: item["id"])


def _prior_by_route(previous: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Normalize both legacy deployment-keyed state and route-keyed state."""
    stored = previous.get("lanes", {}) if isinstance(previous, dict) else {}
    if not isinstance(stored, dict):
        return {}
    normalized: dict[str, dict[str, Any]] = {}
    for legacy_key, lane in stored.items():
        if not isinstance(lane, dict):
            continue
        source_chain = lane.get("source_chain")
        destination_chain = lane.get("destination_chain")
        if source_chain is None or destination_chain is None:
            key_parts = str(legacy_key).split("|")
            if len(key_parts) < 2:
                continue
            source_chain, destination_chain = key_parts[:2]
        normalized[_route_id(source_chain, destination_chain)] = lane
    return normalized


def diff_matches(previous: dict[str, Any], current: list[dict[str, Any]]) -> list[dict[str, Any]]:
    prior_by_id = _prior_by_route(previous)
    changes: list[dict[str, Any]] = []
    for lane in current:
        prior = prior_by_id.get(lane["id"])
        reason = None
        onchain_reopen_check = False
        legacy_off_ramp_orientation = (
            isinstance(prior, dict)
            and "source_side_off_ramp" not in prior
            and prior.get("off_ramp") == lane.get("source_side_off_ramp")
            and prior.get("off_ramp") != lane.get("off_ramp")
        )
        if not isinstance(prior, dict):
            reason = "new_v2_usdc_route"
            onchain_reopen_check = True
        elif not prior.get("proxy_candidate") and lane.get("proxy_candidate"):
            reason = "usdc_proxy_candidate_activated"
            onchain_reopen_check = True
        elif not prior.get("inbound_rate_limit_enabled") and lane.get("inbound_rate_limit_enabled"):
            reason = "inbound_rate_limit_activated"
            onchain_reopen_check = True
        elif (
            prior.get("source_pool") != lane.get("source_pool")
            or prior.get("destination_pool") != lane.get("destination_pool")
        ):
            reason = "usdc_pool_changed"
            onchain_reopen_check = True
        elif (
            prior.get("on_ramp") != lane.get("on_ramp")
            or (
                prior.get("off_ramp") != lane.get("off_ramp")
                and not legacy_off_ramp_orientation
            )
        ):
            reason = "ramp_changed_confirmation_only"
        if reason:
            changes.append(
                {
                    **lane,
                    "change_reason": reason,
                    "onchain_reopen_check": onchain_reopen_check,
                }
            )
    return changes


def _load_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        raw = json.load(handle)
    return raw if isinstance(raw, dict) else {}


def update_reopen_checks(
    previous: dict[str, Any],
    changes: list[dict[str, Any]],
    checked_at: str,
    *,
    current: list[dict[str, Any]] | None = None,
) -> dict[str, dict[str, Any]]:
    """Persist actionable deltas until research records an explicit disposition."""
    stored = previous.get("reopen_checks", {}) if isinstance(previous, dict) else {}
    checks = {
        str(route_id): dict(check)
        for route_id, check in stored.items()
        if isinstance(check, dict)
    } if isinstance(stored, dict) else {}
    for change in changes:
        if not change.get("onchain_reopen_check"):
            continue
        route_id = str(change["id"])
        prior = checks.get(route_id, {})
        checks[route_id] = {
            "route_id": route_id,
            "status": "pending",
            "first_triggered_at": prior.get("first_triggered_at", checked_at),
            "last_triggered_at": checked_at,
            "trigger_count": int(prior.get("trigger_count", 0)) + 1,
            "change_reason": change["change_reason"],
            "source_chain": change["source_chain"],
            "destination_chain": change["destination_chain"],
            "on_ramp": change["on_ramp"],
            "off_ramp": change["off_ramp"],
            "source_side_off_ramp": change.get("source_side_off_ramp", ""),
            "source_pool": change["source_pool"],
            "destination_pool": change["destination_pool"],
            "proxy_candidate": change["proxy_candidate"],
            "inbound_rate_limit_enabled": change["inbound_rate_limit_enabled"],
            "inbound_capacity": change["inbound_capacity"],
            "directory_url": change["directory_url"],
        }
    current_by_id = {
        str(lane["id"]): lane
        for lane in current or []
        if isinstance(lane, dict) and "id" in lane
    }
    for route_id, check in checks.items():
        lane = current_by_id.get(route_id)
        if (
            lane
            and "source_side_off_ramp" not in check
            and check.get("off_ramp") == lane.get("source_side_off_ramp")
        ):
            check["off_ramp"] = lane.get("off_ramp", "")
            check["source_side_off_ramp"] = lane.get("source_side_off_ramp", "")
    return checks


def pending_reopen_checks(checks: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        (check for check in checks.values() if check.get("status") == "pending"),
        key=lambda check: str(check.get("route_id", "")),
    )


def resolve_reopen_check(
    previous: dict[str, Any], route_id: str, resolution: str, note: str, resolved_at: str
) -> dict[str, dict[str, Any]]:
    checks = update_reopen_checks(previous, [], resolved_at)
    if route_id not in checks or checks[route_id].get("status") != "pending":
        raise ValueError(f"No pending onchain confirmation for route {route_id}")
    checks[route_id] = {
        **checks[route_id],
        "status": "resolved",
        "resolution": resolution,
        "resolution_note": note,
        "resolved_at": resolved_at,
    }
    return checks


def _write_state(
    path: Path,
    lanes: list[dict[str, Any]],
    checked_at: str,
    reopen_checks: dict[str, dict[str, Any]] | None = None,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "checked_at": checked_at,
        "lanes": {lane["id"]: lane for lane in lanes},
        "reopen_checks": reopen_checks or {},
        "source_urls": {"lanes": LANES_URL, "tokens": TOKENS_URL},
    }
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=path.parent, prefix=f".{path.name}.", delete=False
    ) as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
        temporary = Path(handle.name)
    os.replace(temporary, path)


def _first_env(keys: tuple[str, ...]) -> str | None:
    return next((os.environ[key] for key in keys if os.environ.get(key)), None)


def _load_env_file(path: Path) -> bool:
    """Load a simple dotenv file without blocking on an evicted FileProvider item."""
    if not path.exists():
        return False
    file_stat = path.stat()
    if file_stat.st_flags & getattr(stat, "SF_DATALESS", 0):
        return False
    with path.open("r", encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip("\"").strip("'")
            if key:
                os.environ.setdefault(key, value)
    return True


def _load_alert_environment(explicit_path: Path | None, repo_root: Path) -> bool:
    """Load the monitor's alert credentials from the radar's normal env chain."""
    candidates = (
        (explicit_path,)
        if explicit_path is not None
        else (repo_root / ".env", *FALLBACK_ENV_FILES)
    )
    loaded = False
    for path in candidates:
        try:
            loaded = _load_env_file(path) or loaded
        except OSError:
            if explicit_path is not None:
                raise
    return loaded


def _format_alert(changes: list[dict[str, Any]]) -> str:
    lines = [
        "CHAINLINK CCIP v2 USDC LANE DELTA",
        "This is a confirmation signal, not an automatic reopen.",
        "",
    ]
    for lane in changes[:6]:
        lines.extend(
            (
                f"- {lane['source_chain']} -> {lane['destination_chain']}",
                f"  Reason: {lane['change_reason']}",
                "  Onchain reopen check: "
                f"{'YES' if lane.get('onchain_reopen_check') else 'NO - ramp-only confirmation'}",
                f"  Proxy path: {'YES' if lane['proxy_candidate'] else 'not yet confirmed'}",
                "  Inbound limit: "
                f"{'enabled' if lane['inbound_rate_limit_enabled'] else 'disabled/unconfirmed'} "
                f"(capacity {lane['inbound_capacity']})",
                f"  OnRamp: {lane['on_ramp']}",
                f"  OffRamp: {lane['off_ramp']}",
            )
        )
    lines.extend(
        (
            "",
            f"Reopen only with onchain evidence of {REOPEN_EVIDENCE}.",
            "Do not submit from this alert alone: verify getPools(), mechanism history, "
            "excluded in-flight USDC, both child buckets, and destination OffRamp acceptance onchain.",
            DIRECTORY_URL,
        )
    )
    return "\n".join(lines)


def _send_telegram(message: str, *, timeout: int = 20) -> bool:
    token = _first_env(TOKEN_ENV_KEYS)
    chat_id = _first_env(CHAT_ENV_KEYS)
    if not token or not chat_id or os.getenv("DISABLE_TELEGRAM", "").lower() in {"1", "true", "yes", "on"}:
        return False
    body = json.dumps(
        {"chat_id": chat_id, "text": message[:3900], "disable_web_page_preview": True}
    ).encode("utf-8")
    request = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data=body,
        headers={"Content-Type": "application/json", "User-Agent": "bounty-radar/ccip-usdc-watch"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        payload = json.load(response)
    return bool(payload.get("ok"))


def build_parser() -> argparse.ArgumentParser:
    repo_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lanes-url", default=LANES_URL)
    parser.add_argument("--tokens-url", default=TOKENS_URL)
    parser.add_argument("--state", type=Path, default=repo_root / "data/chainlink_ccip_v2_usdc_watch.json")
    parser.add_argument("--env-file", type=Path)
    parser.add_argument("--resolve-route", help="Resolve one pending route, e.g. source|destination")
    parser.add_argument("--resolution", choices=("REOPEN", "RE-PARK", "KILL"))
    parser.add_argument("--resolution-note", default="")
    parser.add_argument("--no-alerts", action="store_true")
    parser.add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    checked_at = datetime.now(timezone.utc).isoformat()
    try:
        if args.resolve_route:
            if not args.resolution or not args.resolution_note.strip():
                raise ValueError("--resolve-route requires --resolution and a nonempty --resolution-note")
            previous = _load_state(args.state)
            checks = resolve_reopen_check(
                previous,
                args.resolve_route,
                args.resolution,
                args.resolution_note.strip(),
                checked_at,
            )
            lanes = list(_prior_by_route(previous).values())
            _write_state(args.state, lanes, checked_at, checks)
            result = {
                "coverage_ok": True,
                "checked_at": checked_at,
                "resolved_route": args.resolve_route,
                "resolution": args.resolution,
                "pending_onchain_confirmations": len(pending_reopen_checks(checks)),
                "pending_reopen_checks": pending_reopen_checks(checks),
                "state_file": str(args.state),
            }
            print(json.dumps(result, sort_keys=True) if args.json else f"Resolved {args.resolve_route}: {args.resolution}")
            return 0
        lanes = _fetch_json(args.lanes_url)
        tokens = _fetch_json(args.tokens_url)
        matches = find_v2_usdc_lanes(lanes, tokens)
        previous = _load_state(args.state)
        changes = diff_matches(previous, matches)
        reopen_checks = update_reopen_checks(
            previous, changes, checked_at, current=matches
        )
        pending_checks = pending_reopen_checks(reopen_checks)
        _write_state(args.state, matches, checked_at, reopen_checks)
        env_loaded = _load_alert_environment(
            args.env_file, Path(__file__).resolve().parents[1]
        )
        alert_sent = False
        if changes and not args.no_alerts:
            alert_sent = _send_telegram(_format_alert(changes))
        result = {
            "coverage_ok": True,
            "checked_at": checked_at,
            "matches": len(matches),
            "new_or_upgraded": len(changes),
            "pending_onchain_confirmations": len(pending_checks),
            "pending_reopen_checks": pending_checks,
            "alert_sent": alert_sent,
            "telegram_env_loaded": env_loaded,
            "state_file": str(args.state),
            "changes": changes,
        }
    except Exception as exc:
        result = {
            "coverage_ok": False,
            "checked_at": checked_at,
            "error": f"{type(exc).__name__}: {exc}",
            "state_file": str(args.state),
        }
        if args.json:
            print(json.dumps(result, sort_keys=True))
        else:
            print(f"CCIP v2 USDC monitor degraded: {result['error']}")
        return 1

    if args.json:
        print(json.dumps(result, sort_keys=True))
    elif changes:
        print(_format_alert(changes))
        print(f"Telegram sent: {alert_sent}")
    elif pending_checks:
        print(
            f"CCIP v2 USDC monitor unchanged: {len(matches)} matching lanes; "
            f"{len(pending_checks)} onchain confirmation(s) still pending"
        )
    else:
        print(f"CCIP v2 USDC monitor quiet: {len(matches)} matching lanes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
