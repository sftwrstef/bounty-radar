from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from bounty_radar.runner import _deliver_telegram_outbox, _queue_telegram_alert, run_scan
from bounty_radar.storage import Storage


class TelegramOutboxTests(unittest.TestCase):
    def test_failed_delivery_stays_pending_and_retries(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            storage = Storage(Path(tmp) / "radar.sqlite")
            storage.initialize()
            try:
                failing = Mock()
                failing.send_message.side_effect = RuntimeError("network down")
                sent, errors = _queue_telegram_alert(
                    storage=storage,
                    telegram=failing,
                    dedupe_key="source:test:item-1",
                    alert_type="source_delta",
                    entity_name="test",
                    title="Test alert",
                    message="hello",
                    created_at="2026-08-12T12:00:00+00:00",
                )

                self.assertFalse(sent)
                self.assertEqual(len(errors), 1)
                self.assertEqual(len(storage.pending_telegram_alerts()), 1)

                working = Mock()
                working.send_message.return_value = True
                retry_count, retry_errors = _deliver_telegram_outbox(
                    storage=storage,
                    telegram=working,
                    attempted_at="2026-08-12T12:05:00+00:00",
                )

                self.assertEqual(retry_count, 1)
                self.assertEqual(retry_errors, [])
                self.assertEqual(storage.pending_telegram_alerts(), [])
                working.send_message.assert_called_once_with("hello")
            finally:
                storage.close()

    def test_alert_enabled_scan_fails_before_database_creation_without_telegram(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = root / "tracked.json"
            database = root / "radar.sqlite"
            config.write_text(json.dumps({"repos": [], "sources": []}), encoding="utf-8")
            disabled = Mock(enabled=False)

            with patch("bounty_radar.runner.TelegramClient", return_value=disabled):
                with self.assertRaisesRegex(RuntimeError, "refusing to write scan state"):
                    run_scan(
                        config_path=str(config),
                        db_path=str(database),
                        digest_dir=str(root / "digests"),
                        send_alerts=True,
                    )

            self.assertFalse(database.exists())


if __name__ == "__main__":
    unittest.main()
