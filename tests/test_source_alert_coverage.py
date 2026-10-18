from __future__ import annotations

import unittest
from unittest.mock import Mock, patch

from bounty_radar.config import SourceTarget
from bounty_radar.scanners.sources import fetch_source_items
from bounty_radar.telegram import TelegramClient, format_source_alert_message
from bounty_radar.models import Signal


CARD_HTML = """
<section>
  <article>
    <a aria-label="Open Example" href="/programs/example"></a>
    <div>YesWeHack bounty New Example</div>
    <a aria-label="Open on YesWeHack" href="https://yeswehack.com/programs/example">Open on YesWeHack</a>
  </article>
  <article>
    <a aria-label="Open Other" href="/programs/other"></a>
    <div>HackerOne bounty New Other</div>
    <a aria-label="Open on HackerOne" href="https://hackerone.com/other">Open on HackerOne</a>
  </article>
  <article>
    <a aria-label="Open Generic" href="/programs/generic"></a>
    <div>Open generic bounty</div>
    <a aria-label="Open Generic Site" href="https://generic.test/programs/generic">Open Generic Site</a>
  </article>
</section>
"""


class SourceRoutingTests(unittest.TestCase):
    def test_broad_bountyhunters_keeps_one_source_link_per_unmonitored_card(self) -> None:
        source = SourceTarget(
            name="broad-bountyhunters-recent",
            url="https://bountyhunte.rs/programs?date=tracked_recently",
            kind="html",
            url_terms=["bountyhunte.rs/programs/"],
            exclude_terms=["yeswehack", "hackerone"],
            max_items=100,
        )

        with patch("bounty_radar.scanners.sources.requests.get") as get:
            get.return_value.text = CARD_HTML
            get.return_value.raise_for_status = Mock()
            items, errors = fetch_source_items(source)

        self.assertEqual(errors, [])
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].url, "https://bountyhunte.rs/programs/generic")

    def test_yeswehack_feed_selects_external_card_link_only(self) -> None:
        source = SourceTarget(
            name="bountyhunters-yeswehack-recent",
            url="https://bountyhunte.rs/programs?date=tracked_recently&platform=yeswehack",
            kind="html",
            include_terms=["yeswehack"],
            url_terms=["yeswehack.com/programs/"],
            max_items=100,
        )

        with patch("bounty_radar.scanners.sources.requests.get") as get:
            get.return_value.text = CARD_HTML
            get.return_value.raise_for_status = Mock()
            items, errors = fetch_source_items(source)

        self.assertEqual(errors, [])
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].url, "https://yeswehack.com/programs/example")


class TelegramSourceAlertTests(unittest.TestCase):
    def test_source_alert_message_includes_all_signals(self) -> None:
        signals = [
            Signal(
                signal_type="source_launch",
                key=f"item-{index}",
                title="Fresh bounty source item detected",
                severity=4,
                details="test",
                fingerprint=f"item-{index}",
                url=f"https://example.test/{index}",
                metadata={},
            )
            for index in range(12)
        ]
        message = format_source_alert_message(
            source_name="test-source",
            source_url="https://example.test",
            signals=signals,
        )

        self.assertIn("item-0", message)
        self.assertIn("item-11", message)

    def test_telegram_splits_long_source_alerts_instead_of_truncating(self) -> None:
        client = TelegramClient(token="token", chat_id="chat")
        response = Mock()
        with patch("requests.post", return_value=response) as post:
            self.assertTrue(client.send_message("line\n" * 1000))

        self.assertGreater(post.call_count, 1)
        for call in post.call_args_list:
            self.assertLessEqual(len(call.kwargs["json"]["text"]), 3900)


if __name__ == "__main__":
    unittest.main()
