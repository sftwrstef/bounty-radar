from __future__ import annotations

from collections import defaultdict

from bounty_radar.models import ScoreResult, Signal, VelocityMetrics


WEIGHTS = {
    "security_doc_new": 35,
    "security_doc_changed": 25,
    "security_doc_present": 8,
    "bounty_reference": 25,
    "security_policy_reference": 18,
    "audit_reference": 12,
    "bridge_reference": 8,
    "velocity_spike": 22,
    "release_new": 10,
}

CATEGORY_CAPS = {
    "bounty_reference": 40,
    "security_policy_reference": 25,
    "audit_reference": 25,
    "bridge_reference": 30,
}


def score_repository(signals: list[Signal], metrics: VelocityMetrics) -> ScoreResult:
    score = 0
    reasons: list[str] = []
    category_totals: dict[str, int] = defaultdict(int)

    for signal in signals:
        weight = WEIGHTS.get(signal.signal_type, signal.severity * 3)
        cap = CATEGORY_CAPS.get(signal.signal_type)
        if cap is not None:
            available = max(0, cap - category_totals[signal.signal_type])
            weight = min(weight, available)
            category_totals[signal.signal_type] += weight
        score += weight
        if weight > 0 and len(reasons) < 8:
            reasons.append(f"+{weight}: {signal.title} ({signal.key})")

    activity_points = min(10, metrics.commit_count // 2)
    if activity_points:
        score += activity_points
        reasons.append(f"+{activity_points}: recent commit activity")

    if metrics.multiplier >= 1.5 and metrics.commit_count >= 5:
        score += 5
        reasons.append(f"+5: activity is {metrics.multiplier:.1f}x baseline")

    return ScoreResult(heat_score=min(score, 100), reasons=reasons)
