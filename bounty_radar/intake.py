"""Pure, fail-closed conversion of radar alerts into Vesper intake receipts.

This module deliberately has no storage, network, runner, or submission hooks.
It records why a radar alert may deserve manual review without asserting that
the target is fresh, the signal is a vulnerability, or any severity applies.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from collections.abc import Iterable, Mapping
from datetime import datetime
from typing import Any


SCHEMA_VERSION = "vesper.intake/v1"

_RESERVED_METADATA_KEYS = {
    "finding",
    "finding_status",
    "fresh",
    "freshness",
    "is_finding",
    "severity",
    "severity_rating",
    "verdict",
}

_ADAPTER_KEYWORDS: tuple[tuple[str, tuple[str, ...]], ...] = (
    (
        "semantic_binding",
        (
            "semantic binding",
            "semantic_binding",
            "authorization",
            "authorisation",
            "authorized principal",
            "caller",
            "signature",
            "permit",
            "nonce",
            "replay",
            "attestation",
            "intent",
        ),
    ),
    (
        "oft_bridge",
        (
            "oft",
            "oft_bridge",
            "layerzero",
            "bridge",
            "cross chain",
            "cross-chain",
            "crosschain",
            "wormhole",
            "hyperlane",
            "ccip",
            "ibc",
            "relayer",
        ),
    ),
    (
        "cross_runtime",
        (
            "cross runtime",
            "cross-runtime",
            "cross_runtime",
            "precompile",
            "cosmos",
            "substrate",
            "runtime",
            "account type",
            "vesting module",
            "staking shares",
            "mirrored balance",
        ),
    ),
    (
        "governance_authority",
        (
            "governance authority",
            "governance_authority",
            "governance",
            "voting",
            "quorum",
            "delegate",
            "delegation",
            "timelock",
            "authority",
            "admin",
            "role",
            "multisig",
        ),
    ),
    (
        "verifier",
        (
            "verifier",
            "verification",
            "proof",
            "fraud proof",
            "zero knowledge",
            "zero-knowledge",
            "zk",
            "merkle",
            "consensus",
            "nullifier",
        ),
    ),
    (
        "oracle",
        (
            "oracle",
            "price feed",
            "price-feed",
            "twap",
            "pyth",
            "chainlink",
            "liquidation price",
        ),
    ),
)

_DEGRADED_STATUSES = {"degraded", "error", "failed", "failure", "partial"}
_OK_STATUSES = {"ok", "complete", "completed", "success", "successful"}


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _json_safe(value: Any, *, path: str, strip_reserved_keys: bool = False) -> Any:
    if value is None or isinstance(value, (bool, int, str)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError(f"{path} must not contain a non-finite number")
        return value
    if isinstance(value, Mapping):
        normalized: dict[str, Any] = {}
        for raw_key, raw_value in value.items():
            key = str(raw_key)
            if strip_reserved_keys and key.strip().lower() in _RESERVED_METADATA_KEYS:
                continue
            normalized[key] = _json_safe(
                raw_value,
                path=f"{path}.{key}",
                strip_reserved_keys=strip_reserved_keys,
            )
        return {key: normalized[key] for key in sorted(normalized)}
    if isinstance(value, (list, tuple)):
        return [
            _json_safe(
                item,
                path=f"{path}[{index}]",
                strip_reserved_keys=strip_reserved_keys,
            )
            for index, item in enumerate(value)
        ]
    if isinstance(value, (set, frozenset)):
        normalized_items = [
            _json_safe(
                item,
                path=f"{path}[]",
                strip_reserved_keys=strip_reserved_keys,
            )
            for item in value
        ]
        return sorted(normalized_items, key=lambda item: _canonical_bytes(item))
    raise TypeError(f"{path} contains unsupported value type {type(value).__name__}")


def _read_field(raw: Any, name: str, default: Any = None) -> Any:
    if isinstance(raw, Mapping):
        return raw.get(name, default)
    return getattr(raw, name, default)


def _required_text(raw: Any, name: str) -> str:
    value = _read_field(raw, name)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"signal {name} must be a non-empty string")
    return value.strip()


def _normalize_metadata(raw_metadata: Any) -> dict[str, Any]:
    if raw_metadata is None:
        return {}
    if not isinstance(raw_metadata, Mapping):
        raise TypeError("signal metadata must be a mapping")
    normalized = _json_safe(
        raw_metadata,
        path="signal.metadata",
        strip_reserved_keys=True,
    )
    assert isinstance(normalized, dict)
    return normalized


def _normalize_signal(raw: Any) -> dict[str, Any]:
    url = _read_field(raw, "url")
    if url is not None and not isinstance(url, str):
        raise TypeError("signal url must be a string or null")
    return {
        "signal_type": _required_text(raw, "signal_type"),
        "key": _required_text(raw, "key"),
        "title": _required_text(raw, "title"),
        "details": _required_text(raw, "details"),
        "fingerprint": _required_text(raw, "fingerprint"),
        "url": url.strip() if isinstance(url, str) and url.strip() else None,
        "metadata": _normalize_metadata(_read_field(raw, "metadata", {})),
    }


def _coverage_name(raw: Mapping[str, Any]) -> str:
    for key in ("source_name", "source", "name"):
        value = raw.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    raise ValueError("coverage source_name/source/name must be a non-empty string")


def _normalize_errors(raw: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    single = raw.get("error")
    if isinstance(single, str) and single.strip():
        errors.append(single.strip())
    elif single not in (None, ""):
        raise TypeError("coverage error must be a string or null")

    multiple = raw.get("errors", ())
    if isinstance(multiple, str):
        if multiple.strip():
            errors.append(multiple.strip())
    elif isinstance(multiple, Iterable):
        for item in multiple:
            if not isinstance(item, str):
                raise TypeError("coverage errors must contain strings")
            if item.strip():
                errors.append(item.strip())
    elif multiple is not None:
        raise TypeError("coverage errors must be an iterable of strings")
    return sorted(set(errors))


def _normalize_coverage_record(raw: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(raw, Mapping):
        raise TypeError("source coverage records must be mappings")

    errors = _normalize_errors(raw)
    explicit_ok = raw.get("coverage_ok")
    explicit_degraded = raw.get("degraded")
    status_value = raw.get("status")
    attempted_at = raw.get("attempted_at")

    if explicit_ok is not None and not isinstance(explicit_ok, bool):
        raise TypeError("coverage_ok must be a boolean or null")
    if explicit_degraded is not None and not isinstance(explicit_degraded, bool):
        raise TypeError("degraded must be a boolean or null")
    if status_value is not None and not isinstance(status_value, str):
        raise TypeError("coverage status must be a string or null")
    if attempted_at is not None and not isinstance(attempted_at, str):
        raise TypeError("coverage attempted_at must be a string or null")
    if isinstance(attempted_at, str) and attempted_at.strip():
        try:
            parsed_attempt = datetime.fromisoformat(
                attempted_at.strip().replace("Z", "+00:00")
            )
        except ValueError as exc:
            raise ValueError(
                "coverage attempted_at must be an ISO-8601 timestamp"
            ) from exc
        if parsed_attempt.tzinfo is None:
            raise ValueError("coverage attempted_at must include a timezone")

    raw_status = status_value.strip().lower() if isinstance(status_value, str) else ""
    degraded = bool(errors) or explicit_ok is False or explicit_degraded is True
    degraded = degraded or raw_status in _DEGRADED_STATUSES

    if degraded:
        status = "degraded"
    elif (
        explicit_ok is True
        or explicit_degraded is False
        or raw_status in _OK_STATUSES
        or (isinstance(attempted_at, str) and bool(attempted_at.strip()))
    ):
        status = "reported_ok"
    else:
        status = "unassessed"

    return {
        "source_name": _coverage_name(raw),
        "status": status,
        "errors": errors,
    }


def _coverage_summary(records: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    normalized = sorted(
        (_normalize_coverage_record(record) for record in records),
        key=lambda item: (item["source_name"], item["status"], item["errors"]),
    )
    if not normalized:
        status = "unassessed"
        degraded: bool | None = None
    elif any(item["status"] == "degraded" for item in normalized):
        status = "degraded"
        degraded = True
    elif any(item["status"] == "unassessed" for item in normalized):
        status = "partially_unassessed"
        degraded = None
    else:
        status = "reported_ok"
        degraded = False

    return {
        "status": status,
        "degraded": degraded,
        "degraded_sources": [
            item["source_name"] for item in normalized if item["status"] == "degraded"
        ],
        "sources": normalized,
    }


def _term_pattern(term: str) -> re.Pattern[str]:
    pieces = [re.escape(piece) for piece in re.split(r"[\s_-]+", term.lower())]
    return re.compile(r"(?<![a-z0-9])" + r"[\s_-]+".join(pieces) + r"(?![a-z0-9])")


def _suggest_adapters(
    signals: list[dict[str, Any]],
) -> tuple[list[str], dict[str, list[str]]]:
    text = "\n".join(
        " ".join(
            (
                signal["signal_type"],
                signal["key"],
                signal["title"],
                signal["details"],
                json.dumps(signal["metadata"], ensure_ascii=False, sort_keys=True),
            )
        ).lower()
        for signal in signals
    )

    suggestions: list[str] = []
    evidence: dict[str, list[str]] = {}
    for family, terms in _ADAPTER_KEYWORDS:
        matched = sorted({term for term in terms if _term_pattern(term).search(text)})
        if matched:
            suggestions.append(family)
            evidence[family] = matched
    return suggestions, evidence


def build_intake_receipt(
    *,
    subject_kind: str,
    subject_name: str,
    signals: Iterable[Any],
    source_coverage: Iterable[Mapping[str, Any]] = (),
    alert_worthy: bool,
) -> dict[str, Any]:
    """Build a deterministic, read-only Vesper intake receipt.

    ``alert_worthy`` must be the literal boolean ``True``. The caller remains
    responsible for the radar alert policy; this function does not infer it
    from the signal's numeric priority and intentionally omits that priority.
    """

    if alert_worthy is not True:
        raise ValueError(
            "an intake receipt requires an explicitly alert-worthy signal set"
        )
    if subject_kind not in {"repository", "source"}:
        raise ValueError("subject_kind must be 'repository' or 'source'")
    if not isinstance(subject_name, str) or not subject_name.strip():
        raise ValueError("subject_name must be a non-empty string")

    normalized_signals = [_normalize_signal(signal) for signal in signals]
    if not normalized_signals:
        raise ValueError("at least one alert-worthy signal is required")
    normalized_signals.sort(key=_canonical_bytes)

    coverage = _coverage_summary(source_coverage)
    suggested_adapters, routing_evidence = _suggest_adapters(normalized_signals)
    subject = {"kind": subject_kind, "name": subject_name.strip()}

    identity_material = {
        "schema_version": SCHEMA_VERSION,
        "subject": subject,
        "signal_fingerprints": sorted(
            {signal["fingerprint"] for signal in normalized_signals}
        ),
    }
    identity_hash = _sha256(identity_material)
    intake_id = f"vesper-intake:{identity_hash[:24]}"

    receipt: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "intake_id": intake_id,
        "hypothesis_only": True,
        "finding_status": "not_a_finding",
        "freshness": "unassessed",
        "severity": "unassessed",
        "subject": subject,
        "trigger": "alert_worthy_radar_signal",
        "signals": normalized_signals,
        "source_coverage": coverage,
        "suggested_adapter_families": suggested_adapters,
        "adapter_routing_evidence": routing_evidence,
        "automation": {
            "auto_hunt": False,
            "auto_submit": False,
            "manual_review_required": True,
        },
    }
    receipt["receipt_sha256"] = _sha256(receipt)
    return receipt
