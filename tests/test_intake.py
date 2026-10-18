from __future__ import annotations

import json
import unittest

from bounty_radar.intake import build_intake_receipt
from bounty_radar.models import Signal


def signal(
    *,
    fingerprint: str,
    signal_type: str = "scope_changed",
    title: str = "Bridge authorization contracts changed",
    details: str = "LayerZero OFT permit and nonce handling changed",
    metadata: dict | None = None,
    severity: int = 5,
) -> Signal:
    return Signal(
        signal_type=signal_type,
        key=fingerprint,
        title=title,
        severity=severity,
        details=details,
        fingerprint=fingerprint,
        url="https://example.test/program",
        metadata=metadata or {},
    )


class IntakeReceiptTests(unittest.TestCase):
    def test_receipt_is_explicitly_hypothesis_only_and_routes_from_text(self) -> None:
        receipt = build_intake_receipt(
            subject_kind="repository",
            subject_name="example/bridge",
            signals=[signal(fingerprint="repo:bridge-change")],
            alert_worthy=True,
        )

        self.assertEqual(receipt["schema_version"], "vesper.intake/v1")
        self.assertIs(receipt["hypothesis_only"], True)
        self.assertEqual(receipt["finding_status"], "not_a_finding")
        self.assertEqual(receipt["freshness"], "unassessed")
        self.assertEqual(receipt["severity"], "unassessed")
        self.assertEqual(
            receipt["suggested_adapter_families"],
            ["semantic_binding", "oft_bridge"],
        )
        self.assertEqual(receipt["source_coverage"]["status"], "unassessed")
        self.assertIsNone(receipt["source_coverage"]["degraded"])
        self.assertIs(receipt["automation"]["auto_hunt"], False)
        self.assertIs(receipt["automation"]["auto_submit"], False)

    def test_source_coverage_degradation_is_propagated(self) -> None:
        receipt = build_intake_receipt(
            subject_kind="source",
            subject_name="hackenproof-programs",
            signals=[signal(fingerprint="source:scope-change")],
            source_coverage=[
                {
                    "source_name": "hackenproof-programs",
                    "coverage_ok": False,
                    "errors": ["browser fetch exceeded 58000ms"],
                },
                {
                    "source_name": "immunefi-programs",
                    "coverage_ok": True,
                },
            ],
            alert_worthy=True,
        )

        coverage = receipt["source_coverage"]
        self.assertEqual(coverage["status"], "degraded")
        self.assertIs(coverage["degraded"], True)
        self.assertEqual(coverage["degraded_sources"], ["hackenproof-programs"])
        failed = next(
            item
            for item in coverage["sources"]
            if item["source_name"] == "hackenproof-programs"
        )
        self.assertEqual(failed["status"], "degraded")
        self.assertEqual(failed["errors"], ["browser fetch exceeded 58000ms"])

    def test_storage_success_coverage_shape_is_reported_ok(self) -> None:
        receipt = build_intake_receipt(
            subject_kind="source",
            subject_name="immunefi-programs",
            signals=[signal(fingerprint="source:new-program")],
            source_coverage=[
                {
                    "source_name": "immunefi-programs",
                    "attempted_at": "2026-08-30T14:00:00+00:00",
                    "error": "",
                }
            ],
            alert_worthy=True,
        )

        self.assertEqual(receipt["source_coverage"]["status"], "reported_ok")
        self.assertIs(receipt["source_coverage"]["degraded"], False)

    def test_storage_coverage_timestamp_must_be_real_and_zoned(self) -> None:
        for attempted_at in ("replace-with-time", "2026-08-30T14:00:00"):
            with self.subTest(attempted_at=attempted_at), self.assertRaises(ValueError):
                build_intake_receipt(
                    subject_kind="source",
                    subject_name="immunefi-programs",
                    signals=[signal(fingerprint=f"source:{attempted_at}")],
                    source_coverage=[
                        {
                            "source_name": "immunefi-programs",
                            "attempted_at": attempted_at,
                            "error": "",
                        }
                    ],
                    alert_worthy=True,
                )

    def test_stable_id_ignores_order_while_content_hash_tracks_content(self) -> None:
        first_signal = signal(fingerprint="a", metadata={"tags": ["oracle", "proof"]})
        second_signal = signal(
            fingerprint="b",
            title="EVM precompile and governance update",
            details="Cosmos mirrored balance verifier now reads a Chainlink oracle",
            metadata={"adapter_families": ["cross_runtime"]},
        )
        coverage = [
            {"source_name": "two", "coverage_ok": True},
            {"source_name": "one", "coverage_ok": True},
        ]

        first = build_intake_receipt(
            subject_kind="repository",
            subject_name="example/runtime",
            signals=[first_signal, second_signal],
            source_coverage=coverage,
            alert_worthy=True,
        )
        reordered = build_intake_receipt(
            subject_kind="repository",
            subject_name="example/runtime",
            signals=[second_signal, first_signal],
            source_coverage=list(reversed(coverage)),
            alert_worthy=True,
        )
        changed = build_intake_receipt(
            subject_kind="repository",
            subject_name="example/runtime",
            signals=[
                signal(
                    fingerprint="a",
                    details="LayerZero OFT permit and nonce handling changed again",
                    metadata={"tags": ["oracle", "proof"]},
                ),
                second_signal,
            ],
            source_coverage=coverage,
            alert_worthy=True,
        )

        self.assertEqual(first["intake_id"], reordered["intake_id"])
        self.assertEqual(first["receipt_sha256"], reordered["receipt_sha256"])
        self.assertEqual(first["intake_id"], changed["intake_id"])
        self.assertNotEqual(first["receipt_sha256"], changed["receipt_sha256"])
        self.assertEqual(
            first["suggested_adapter_families"],
            [
                "semantic_binding",
                "oft_bridge",
                "cross_runtime",
                "governance_authority",
                "verifier",
                "oracle",
            ],
        )

    def test_radar_priority_and_reserved_claims_are_not_propagated(self) -> None:
        receipt = build_intake_receipt(
            subject_kind="source",
            subject_name="test-source",
            signals=[
                signal(
                    fingerprint="source:item",
                    severity=99,
                    metadata={
                        "severity": "critical",
                        "freshness": "fresh",
                        "finding_status": "confirmed",
                        "summary": "New oracle program",
                        "nested": {"severity": "high", "domain": "oracle"},
                    },
                )
            ],
            alert_worthy=True,
        )

        observed_signal = receipt["signals"][0]
        self.assertNotIn("severity", observed_signal)
        self.assertNotIn("severity", observed_signal["metadata"])
        self.assertNotIn("freshness", observed_signal["metadata"])
        self.assertNotIn("finding_status", observed_signal["metadata"])
        self.assertNotIn("severity", observed_signal["metadata"]["nested"])
        self.assertEqual(receipt["severity"], "unassessed")
        self.assertEqual(receipt["freshness"], "unassessed")
        self.assertEqual(receipt["finding_status"], "not_a_finding")

    def test_receipt_is_json_serializable_and_hash_is_deterministic(self) -> None:
        kwargs = {
            "subject_kind": "repository",
            "subject_name": "example/contracts",
            "signals": [
                signal(
                    fingerprint="repo:proof",
                    title="Verifier release",
                    details="Merkle proof nullifier handling changed",
                    metadata={"tags": {"proof", "verifier"}},
                )
            ],
            "alert_worthy": True,
        }
        first = build_intake_receipt(**kwargs)
        second = build_intake_receipt(**kwargs)

        self.assertEqual(first, second)
        self.assertIsInstance(json.dumps(first, sort_keys=True), str)
        self.assertRegex(first["intake_id"], r"^vesper-intake:[0-9a-f]{24}$")
        self.assertRegex(first["receipt_sha256"], r"^[0-9a-f]{64}$")

    def test_non_alert_or_empty_input_fails_closed(self) -> None:
        with self.assertRaises(ValueError):
            build_intake_receipt(
                subject_kind="repository",
                subject_name="example/contracts",
                signals=[signal(fingerprint="repo:quiet")],
                alert_worthy=False,
            )
        with self.assertRaises(ValueError):
            build_intake_receipt(
                subject_kind="source",
                subject_name="test-source",
                signals=[],
                alert_worthy=True,
            )


if __name__ == "__main__":
    unittest.main()
