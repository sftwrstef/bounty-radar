from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from bounty_radar.models import Signal
from bounty_radar.storage import Storage


def item(summary: str) -> Signal:
    return Signal(
        signal_type="source_launch",
        key="Example Program",
        title="Fresh bounty source item detected",
        severity=4,
        details="test-source surfaced Example Program",
        fingerprint="source-item:stable-url",
        url="https://example.test/program",
        metadata={"summary": summary, "published_at": "2026-08-11"},
    )


class SourceChangeTrackingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.storage = Storage(Path(self.tempdir.name) / "radar.sqlite")
        self.storage.initialize()
        self.storage.upsert_source(
            name="test-source",
            url="https://example.test",
            kind="html",
            seen_at="2026-08-11T00:00:00+00:00",
        )

    def tearDown(self) -> None:
        self.storage.close()
        self.tempdir.cleanup()

    def test_first_snapshot_is_baseline_and_repeat_is_quiet(self) -> None:
        first = item("Live reward $10,000; 2 submissions")
        self.assertIsNone(self.storage.record_source_snapshot_change(
            source_name="test-source", signal=first, seen_at="2026-08-11T00:00:00+00:00"
        ))
        self.assertIsNone(self.storage.record_source_snapshot_change(
            source_name="test-source", signal=first, seen_at="2026-08-11T01:00:00+00:00"
        ))

    def test_same_url_reward_and_submission_change_is_classified(self) -> None:
        self.storage.record_source_snapshot_change(
            source_name="test-source",
            signal=item("Live reward $10,000; 2 submissions"),
            seen_at="2026-08-11T00:00:00+00:00",
        )
        change = self.storage.record_source_snapshot_change(
            source_name="test-source",
            signal=item("Live reward $25,000; 7 submissions"),
            seen_at="2026-08-12T00:00:00+00:00",
        )
        self.assertIsNotNone(change)
        assert change is not None
        self.assertEqual(change.signal_type, "program_changed")
        self.assertEqual(
            change.metadata["change_types"],
            ["reward_changed", "submission_count_changed"],
        )
        self.assertEqual(change.severity, 4)

    def test_unclassified_text_change_falls_back_to_scope_change(self) -> None:
        self.storage.record_source_snapshot_change(
            source_name="test-source",
            signal=item("Contracts: 0xabc"),
            seen_at="2026-08-11T00:00:00+00:00",
        )
        change = self.storage.record_source_snapshot_change(
            source_name="test-source",
            signal=item("Contracts: 0xabc and 0xdef"),
            seen_at="2026-08-12T00:00:00+00:00",
        )
        self.assertIsNotNone(change)
        assert change is not None
        self.assertEqual(change.signal_type, "scope_changed")


if __name__ == "__main__":
    unittest.main()
