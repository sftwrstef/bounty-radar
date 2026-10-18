from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

from bounty_radar.__main__ import main
from bounty_radar.config import RadarSettings, SourceTarget
from bounty_radar.digest import write_daily_digest
from bounty_radar.runner import scan_one_source
from bounty_radar.scanners.sources import fetch_source_items
from bounty_radar.storage import Storage
from bounty_radar.telegram import TelegramClient


class HackenProofIndexCoverageTests(unittest.TestCase):
    def test_official_index_listing_is_detected(self) -> None:
        source = SourceTarget(
            name="hackenproof-audits",
            url="https://hackenproof.com/audit-programs",
            kind="browser",
            browser=True,
            include_terms=["audit"],
            url_terms=["/audit-programs/"],
        )
        html = """
        <a href="/audit-programs/push-chain-core-contracts-sc-dualdefense-audit">
          Push Chain Core Contracts SC DualDefense Audit
        </a>
        """

        with patch(
            "bounty_radar.scanners.sources.fetch_rendered_html",
            return_value=html,
        ):
            items, errors = fetch_source_items(source)

        self.assertEqual(errors, [])
        self.assertEqual(len(items), 1)
        self.assertEqual(
            items[0].url,
            "https://hackenproof.com/audit-programs/"
            "push-chain-core-contracts-sc-dualdefense-audit",
        )

    def test_official_index_false_empty_is_degraded(self) -> None:
        source = SourceTarget(
            name="hackenproof-programs",
            url="https://hackenproof.com/programs",
            kind="browser",
            browser=True,
            include_terms=["program"],
            url_terms=["/programs/"],
        )

        with patch(
            "bounty_radar.scanners.sources.fetch_rendered_html",
            return_value="<html><body><a href='/programs'>Programs</a></body></html>",
        ):
            items, errors = fetch_source_items(source)

        self.assertEqual(items, [])
        self.assertEqual(len(errors), 1)
        self.assertIn("official index verification unavailable", errors[0])
        self.assertIn("coverage degraded", errors[0])

    def test_false_empty_is_visible_in_digest_coverage(self) -> None:
        source = SourceTarget(
            name="hackenproof-programs",
            url="https://hackenproof.com/programs",
            kind="browser",
            browser=True,
            include_terms=["program"],
            url_terms=["/programs/"],
        )
        now = datetime(2026, 7, 30, 2, 0, tzinfo=timezone.utc)

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            storage = Storage(root / "radar.sqlite")
            storage.initialize()
            try:
                with patch(
                    "bounty_radar.scanners.sources.fetch_rendered_html",
                    return_value="<html><body><a href='/programs'>Programs</a></body></html>",
                ):
                    result = scan_one_source(
                        storage=storage,
                        telegram=TelegramClient(token="unused", chat_id="unused"),
                        source=source,
                        settings=RadarSettings(),
                        send_alerts=False,
                        now=now,
                    )
                digest_path = write_daily_digest(storage, root / "digests", now=now)
            finally:
                storage.close()

            self.assertFalse(result["coverage_ok"])
            digest = digest_path.read_text(encoding="utf-8")
            self.assertIn("**hackenproof-programs** degraded:", digest)
            self.assertIn("official index verification unavailable", digest)


class RecordSourceFallbackTests(unittest.TestCase):
    def test_record_source_deduplicates_and_regenerates_digest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config_path = root / "tracked.json"
            db_path = root / "radar.sqlite"
            digest_dir = root / "digests"
            config_path.write_text(
                json.dumps(
                    {
                        "sources": [
                            {
                                "name": "hackenproof-audits",
                                "url": "https://hackenproof.com/audit-programs",
                                "kind": "browser",
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            args = [
                "record-source",
                "hackenproof-audits",
                "--title",
                "Push Chain Core Contracts SC DualDefense Audit",
                "--url",
                (
                    "https://hackenproof.com/audit-programs/"
                    "push-chain-core-contracts-sc-dualdefense-audit"
                ),
                "--summary",
                "Official NEW/LIVE listing; up to $10,000",
                "--config",
                str(config_path),
                "--db",
                str(db_path),
                "--digest-dir",
                str(digest_dir),
                "--no-alerts",
            ]

            first_stdout = io.StringIO()
            with (
                patch("bounty_radar.__main__.load_environment"),
                redirect_stdout(first_stdout),
            ):
                first_exit = main(args)
            first = json.loads(first_stdout.getvalue())

            second_stdout = io.StringIO()
            with (
                patch("bounty_radar.__main__.load_environment"),
                redirect_stdout(second_stdout),
            ):
                second_exit = main(args)
            second = json.loads(second_stdout.getvalue())

            self.assertEqual(first_exit, 0)
            self.assertEqual(second_exit, 0)
            self.assertTrue(first["new"])
            self.assertFalse(second["new"])
            self.assertEqual(first["digest_path"], second["digest_path"])
            digest_path = Path(second["digest_path"])
            self.assertTrue(digest_path.exists())
            self.assertIn(
                "Push Chain Core Contracts SC DualDefense Audit",
                digest_path.read_text(encoding="utf-8"),
            )


if __name__ == "__main__":
    unittest.main()
