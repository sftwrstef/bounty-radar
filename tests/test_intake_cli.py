from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest

from bounty_radar.__main__ import main


def intake_spec() -> dict[str, object]:
    return {
        "subject_kind": "repository",
        "subject_name": "example/bridge",
        "alert_worthy": True,
        "signals": [
            {
                "signal_type": "scope_changed",
                "key": "bridge-change",
                "title": "Bridge authorization changed",
                "details": "LayerZero OFT permit and nonce handling changed",
                "fingerprint": "repo:bridge-change",
                "url": "https://example.test/program",
                "metadata": {},
            }
        ],
        "source_coverage": [
            {
                "source_name": "hackenproof-programs",
                "coverage_ok": False,
                "errors": ["browser fetch exceeded 58000ms"],
            }
        ],
    }


class IntakeCliTests(unittest.TestCase):
    def test_build_intake_emits_hypothesis_only_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            input_path = Path(temp_dir) / "input.json"
            input_path.write_text(json.dumps(intake_spec()), encoding="utf-8")
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                exit_code = main(["build-intake", str(input_path)])

        self.assertEqual(exit_code, 0)
        receipt = json.loads(stdout.getvalue())
        self.assertEqual(receipt["schema_version"], "vesper.intake/v1")
        self.assertIs(receipt["hypothesis_only"], True)
        self.assertIs(receipt["automation"]["auto_hunt"], False)
        self.assertIs(receipt["automation"]["auto_submit"], False)
        self.assertEqual(receipt["source_coverage"]["status"], "degraded")

    def test_build_intake_rejects_duplicate_keys_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            input_path = Path(temp_dir) / "input.json"
            input_path.write_text(
                '{"subject_kind":"source","subject_kind":"repository"}',
                encoding="utf-8",
            )
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                exit_code = main(["build-intake", str(input_path)])

        self.assertEqual(exit_code, 64)
        self.assertIn("duplicate JSON key", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
