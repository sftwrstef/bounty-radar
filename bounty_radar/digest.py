from __future__ import annotations

import json
from datetime import datetime, time, timezone
from pathlib import Path

from bounty_radar.storage import Storage


def _start_of_day(now: datetime) -> datetime:
    return datetime.combine(now.date(), time.min, tzinfo=timezone.utc)


def write_daily_digest(storage: Storage, digest_dir: str | Path, now: datetime | None = None) -> Path:
    now = now or datetime.now(timezone.utc)
    since = _start_of_day(now)
    since_iso = since.isoformat()
    scans = storage.latest_scans_since(since_iso)
    signals = storage.new_signals_since(since_iso)
    alerts = storage.alerts_since(since_iso)
    source_signals = storage.source_signals_since(since_iso)
    source_alerts = storage.source_alerts_since(since_iso)
    source_coverage = storage.source_coverage_since(since_iso)

    output_dir = Path(digest_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"{now.date().isoformat()}.md"

    lines = [
        f"# Bounty Radar Digest - {now.date().isoformat()}",
        "",
        f"Generated: {now.isoformat()}",
        "",
        "## Top Heat",
        "",
    ]

    if scans:
        lines.extend(
            [
                "| Repo | Heat | Delta | Commits | Velocity | Notes |",
                "| --- | ---: | ---: | ---: | ---: | --- |",
            ]
        )
        for scan in scans[:25]:
            summary = json.loads(scan["summary_json"])
            reasons = "; ".join(summary.get("reasons", [])[:3]) or "No notable signals"
            lines.append(
                "| {repo} | {heat} | {delta:+d} | {commits} | {velocity:.1f}x | {notes} |".format(
                    repo=scan["repo_full_name"],
                    heat=scan["heat_score"],
                    delta=scan["score_delta"],
                    commits=scan["commit_count_24h"],
                    velocity=scan["velocity_multiplier"],
                    notes=reasons.replace("|", "\\|"),
                )
            )
    else:
        lines.append("No scans recorded today.")

    lines.extend(["", "## New Signals", ""])
    if signals:
        for signal in signals[:50]:
            url = f" [{signal['url']}]({signal['url']})" if signal.get("url") else ""
            lines.append(
                f"- **{signal['repo_full_name']}** [{signal['signal_type']}] "
                f"{signal['title']} - `{signal['signal_key']}`{url}"
            )
    else:
        lines.append("No new signals recorded today.")

    lines.extend(["", "## Platform And Announcement Signals", ""])
    if source_signals:
        for signal in source_signals[:50]:
            url = f" [{signal['url']}]({signal['url']})" if signal.get("url") else ""
            lines.append(
                f"- **{signal['source_name']}** [{signal['signal_type']}] "
                f"{signal['signal_key']}{url}"
            )
    else:
        lines.append("No source signals recorded today.")

    lines.extend(["", "## Source Coverage", ""])
    if source_coverage:
        failed_sources = [item for item in source_coverage if item.get("error")]
        lines.append(
            f"{len(source_coverage) - len(failed_sources)}/{len(source_coverage)} "
            "attempted source fetches completed successfully."
        )
        for item in failed_sources:
            lines.append(f"- **{item['source_name']}** degraded: {item['error']}")
    else:
        lines.append("No source coverage recorded today.")

    lines.extend(["", "## Alerts", ""])
    if alerts:
        for alert in alerts[:50]:
            lines.append(
                f"- **{alert['repo_full_name']}** [{alert['alert_type']}] "
                f"{alert['title']} at {alert['sent_at']}"
            )
    if source_alerts:
        for alert in source_alerts[:50]:
            lines.append(
                f"- **{alert['source_name']}** [{alert['alert_type']}] "
                f"{alert['title']} at {alert['sent_at']}"
            )
    if not alerts and not source_alerts:
        lines.append("No alerts sent today.")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path
