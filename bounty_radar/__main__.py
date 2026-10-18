from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from bounty_radar.config import load_environment, load_tracked_config
from bounty_radar.telegram import CHAT_ENV_KEYS, TOKEN_ENV_KEYS, TelegramClient


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="bounty-radar")
    parser.add_argument("--env-file", default=None, help="Optional .env file path")
    subcommands = parser.add_subparsers(dest="command", required=True)

    init_db = subcommands.add_parser("init-db", help="Initialize the SQLite database")
    init_db.add_argument("--db", default=None)

    scan = subcommands.add_parser("scan", help="Run a radar scan and write a digest")
    scan.add_argument("--config", default=None)
    scan.add_argument("--db", default=None)
    scan.add_argument("--digest-dir", default=None)
    scan.add_argument(
        "--no-alerts", action="store_true", help="Do not send Telegram alerts"
    )
    scan.add_argument(
        "--json", action="store_true", help="Print machine-readable results"
    )
    scan.add_argument(
        "--progress",
        action="store_true",
        help="Print per-target scan progress to stderr",
    )

    digest = subcommands.add_parser("digest", help="Regenerate today's markdown digest")
    digest.add_argument("--db", default=None)
    digest.add_argument("--digest-dir", default=None)

    telegram = subcommands.add_parser(
        "check-telegram", help="Check Telegram secret wiring"
    )
    telegram.add_argument(
        "--send-test",
        action="store_true",
        help="Send a short Telegram test message if credentials are present",
    )

    warm = subcommands.add_parser(
        "warm-source",
        help="Open a browser-backed source to warm its persistent profile",
    )
    warm.add_argument("source_name", help="Source name from tracked_orgs.json")
    warm.add_argument("--config", default=None)
    warm.add_argument("--wait-ms", type=int, default=60000)
    warm.add_argument(
        "--headed", action="store_true", help="Force a visible browser window"
    )

    record = subcommands.add_parser(
        "record-source",
        help="Record one independently verified source item with normal deduplication",
    )
    record.add_argument("source_name", help="Source name from tracked_orgs.json")
    record.add_argument("--title", required=True, help="Verified item title")
    record.add_argument("--url", required=True, help="Verified official item URL")
    record.add_argument(
        "--summary", default="", help="Optional verified status/reward summary"
    )
    record.add_argument("--config", default=None)
    record.add_argument("--db", default=None)
    record.add_argument("--digest-dir", default=None)
    record.add_argument(
        "--no-alerts", action="store_true", help="Record without Telegram"
    )

    intake = subcommands.add_parser(
        "build-intake",
        help="Convert explicitly alert-worthy signals into a hypothesis-only Vesper intake receipt",
    )
    intake.add_argument("input", type=Path, help="Strict JSON intake specification")
    intake.add_argument("--output", type=Path, help="Optional receipt output path")

    return parser


def _present_env_key(keys: tuple[str, ...]) -> str | None:
    for key in keys:
        if os.getenv(key):
            return key
    return None


def _option_or_env(value: str | None, env_name: str, fallback: str) -> str:
    return value or os.getenv(env_name, fallback)


def _reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _reject_nonfinite(value: str) -> object:
    raise ValueError(f"non-finite JSON value is not allowed: {value}")


def _load_intake_spec(path: Path) -> dict[str, object]:
    raw = json.loads(
        path.read_text(encoding="utf-8"),
        object_pairs_hook=_reject_duplicate_keys,
        parse_constant=_reject_nonfinite,
    )
    if not isinstance(raw, dict):
        raise TypeError("intake specification must be a JSON object")
    required = {
        "subject_kind",
        "subject_name",
        "signals",
        "source_coverage",
        "alert_worthy",
    }
    missing = sorted(required - set(raw))
    unexpected = sorted(set(raw) - required)
    if missing or unexpected:
        raise ValueError(
            f"intake specification missing={missing} unexpected={unexpected}"
        )
    return raw


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "build-intake":
        from bounty_radar.intake import build_intake_receipt

        try:
            spec = _load_intake_spec(args.input)
            receipt = build_intake_receipt(
                subject_kind=spec["subject_kind"],
                subject_name=spec["subject_name"],
                signals=spec["signals"],
                source_coverage=spec["source_coverage"],
                alert_worthy=spec["alert_worthy"],
            )
            payload = (
                json.dumps(receipt, indent=2, sort_keys=True, allow_nan=False) + "\n"
            )
            if args.output is None:
                print(payload, end="")
            else:
                args.output.parent.mkdir(parents=True, exist_ok=True)
                args.output.write_text(payload, encoding="utf-8")
                print(f"Wrote hypothesis-only intake receipt: {args.output}")
            return 0
        except (OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
            print(f"Invalid intake specification: {exc}", file=sys.stderr)
            return 64

    load_environment(args.env_file)
    if args.command in {"init-db", "digest", "scan", "record-source"}:
        args.db = _option_or_env(args.db, "BOUNTY_RADAR_DB", "data/bounty_radar.sqlite")
    if args.command in {"digest", "scan", "record-source"}:
        args.digest_dir = _option_or_env(args.digest_dir, "DIGEST_DIR", "digests")
    if args.command in {"scan", "warm-source", "record-source"}:
        args.config = _option_or_env(args.config, "TRACKED_CONFIG", "tracked_orgs.json")

    if args.command == "init-db":
        from bounty_radar.storage import Storage

        storage = Storage(args.db)
        storage.initialize()
        storage.close()
        print(f"Initialized SQLite database: {args.db}")
        return 0

    if args.command == "digest":
        from bounty_radar.digest import write_daily_digest
        from bounty_radar.storage import Storage

        storage = Storage(args.db)
        storage.initialize()
        path = write_daily_digest(storage, args.digest_dir)
        storage.close()
        print(f"Wrote digest: {path}")
        return 0

    if args.command == "check-telegram":
        token_key = _present_env_key(TOKEN_ENV_KEYS)
        chat_key = _present_env_key(CHAT_ENV_KEYS)
        client = TelegramClient()
        print(f"Telegram token: {'set via ' + token_key if token_key else 'missing'}")
        print(f"Telegram chat id: {'set via ' + chat_key if chat_key else 'missing'}")
        print(f"Telegram enabled: {client.enabled}")
        if args.send_test:
            if not client.enabled:
                print("Cannot send test: Telegram is not enabled")
                return 1
            client.send_message("Bounty Radar Telegram test: delivery is wired.")
            print("Sent Telegram test message")
        return 0 if client.enabled else 1

    if args.command == "warm-source":
        from bounty_radar.browser_fetch import (
            fetch_rendered_html,
            looks_like_challenge_page,
        )
        from bounty_radar.scanners.sources import scan_source

        config = load_tracked_config(args.config)
        source = next(
            (item for item in config.sources if item.name == args.source_name), None
        )
        if source is None:
            print(f"Unknown source: {args.source_name}")
            return 1
        if args.headed:
            os.environ["BOUNTY_RADAR_BROWSER_HEADLESS"] = "false"
        html = fetch_rendered_html(
            source.url,
            wait_ms=args.wait_ms,
            fail_on_challenge=False,
        )
        if looks_like_challenge_page(html):
            print("Browser warm-up finished, but the challenge page is still present.")
            return 1
        signals, errors = scan_source(source)
        print(f"Browser warm-up succeeded for {source.name}")
        print(f"Source signals visible now: {len(signals)}")
        if errors:
            print("Follow-up scan errors:")
            for error in errors:
                print(f"- {error}")
        return 0

    if args.command == "record-source":
        from bounty_radar.digest import write_daily_digest
        from bounty_radar.scanners.sources import SourceItem, signal_from_source_item
        from bounty_radar.storage import Storage
        from bounty_radar.runner import _queue_telegram_alert
        from bounty_radar.telegram import format_source_alert_message

        config = load_tracked_config(args.config)
        source = next(
            (item for item in config.sources if item.name == args.source_name), None
        )
        if source is None:
            print(f"Unknown source: {args.source_name}")
            return 1

        recorded_at = datetime.now(timezone.utc)
        now = recorded_at.isoformat()
        item = SourceItem(title=args.title, url=args.url, summary=args.summary)
        signal = signal_from_source_item(source.name, item)
        signal.metadata["verified_via"] = "official-web-fallback"
        client = TelegramClient()
        if not args.no_alerts and not client.enabled:
            print(
                "Telegram alerts are enabled, but credentials are missing or disabled; "
                "refusing to record source state",
                file=sys.stderr,
            )
            return 1
        storage = Storage(args.db)
        storage.initialize()
        try:
            storage.upsert_source(
                name=source.name,
                url=source.url,
                kind=source.kind,
                seen_at=now,
            )
            change_signal = storage.record_source_snapshot_change(
                source_name=source.name,
                signal=signal,
                seen_at=now,
            )
            is_new = storage.upsert_source_signal(
                source_name=source.name,
                signal=signal,
                seen_at=now,
            )
            is_changed = bool(
                change_signal
                and storage.upsert_source_signal(
                    source_name=source.name,
                    signal=change_signal,
                    seen_at=now,
                )
            )
            storage.set_source_state(source.name, "last_web_fallback_at", now, now)

            alert_sent = False
            if (is_new or is_changed) and not args.no_alerts:
                alert_signal = change_signal if is_changed and change_signal else signal
                message = format_source_alert_message(
                    source_name=source.name,
                    source_url=source.url,
                    signals=[alert_signal],
                )
                alert_sent, _delivery_errors = _queue_telegram_alert(
                    storage=storage,
                    telegram=client,
                    dedupe_key=f"source:{source.name}:{alert_signal.fingerprint}",
                    alert_type="source_delta",
                    entity_name=source.name,
                    title="Verified official-web source launch or change",
                    message=message,
                    created_at=now,
                )
                if alert_sent:
                    storage.record_source_alert(
                        source_name=source.name,
                        alert_type="source_delta",
                        title="Verified official-web source launch or change",
                        message=message,
                        sent_at=now,
                    )

            digest_path = write_daily_digest(storage, args.digest_dir, now=recorded_at)
            print(
                json.dumps(
                    {
                        "source": source.name,
                        "url": signal.url,
                        "new": is_new,
                        "changed": is_changed,
                        "alert_sent": alert_sent,
                        "digest_path": str(digest_path),
                    },
                    sort_keys=True,
                )
            )
            return 0
        finally:
            storage.close()

    if args.command == "scan":
        from bounty_radar.runner import run_scan

        result = run_scan(
            config_path=args.config,
            db_path=args.db,
            digest_dir=args.digest_dir,
            send_alerts=not args.no_alerts,
            progress=(lambda message: print(message, file=sys.stderr, flush=True))
            if args.progress
            else None,
        )
        if args.json:
            print(json.dumps(result, indent=2, sort_keys=True))
        else:
            print(f"Scanned {result['scanned']} repos")
            print(f"Scanned {result['sources_scanned']} sources")
            print(f"Digest: {result['digest_path']}")
            if result["errors"]:
                print("Errors:")
                for error in result["errors"]:
                    print(f"- {error}")
        return (
            0
            if result["scanned"] or result["sources_scanned"] or not result["errors"]
            else 1
        )

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
