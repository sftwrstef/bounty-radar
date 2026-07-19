from __future__ import annotations

from datetime import datetime
from typing import Any

from bounty_radar.models import Signal, VelocityMetrics


def scan_velocity(
    full_name: str,
    current_commits: list[dict[str, Any]],
    baseline_commits: list[dict[str, Any]],
    *,
    lookback_hours: int,
    baseline_days: int,
    spike_multiplier: float,
    min_commits: int,
    now: datetime,
) -> tuple[VelocityMetrics, list[Signal]]:
    current_count = len(current_commits)
    baseline_count = len(baseline_commits)
    baseline_hours = max(lookback_hours, baseline_days * 24 - lookback_hours)
    baseline_windows = max(1.0, baseline_hours / lookback_hours)
    baseline_per_window = baseline_count / baseline_windows
    multiplier = current_count / max(1.0, baseline_per_window)

    metrics = VelocityMetrics(
        commit_count=current_count,
        baseline_commit_count=baseline_count,
        baseline_per_window=baseline_per_window,
        multiplier=multiplier,
        lookback_hours=lookback_hours,
        baseline_days=baseline_days,
    )

    signals: list[Signal] = []
    is_spike = current_count >= min_commits and (
        baseline_per_window == 0 or current_count >= baseline_per_window * spike_multiplier
    )
    if is_spike:
        signals.append(
            Signal(
                signal_type="velocity_spike",
                key="commit_velocity",
                title="Commit velocity spike detected",
                severity=4,
                details=(
                    f"{current_count} commit(s) in {lookback_hours}h vs "
                    f"{baseline_per_window:.1f} baseline/window."
                ),
                fingerprint=f"velocity-spike:{now.date().isoformat()}",
                url=f"https://github.com/{full_name}/commits",
                metadata={
                    "commit_count": current_count,
                    "baseline_commit_count": baseline_count,
                    "baseline_per_window": baseline_per_window,
                    "multiplier": multiplier,
                },
            )
        )

    return metrics, signals
