from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class RepoRef:
    owner: str
    name: str

    @classmethod
    def from_full_name(cls, full_name: str) -> "RepoRef":
        owner, name = full_name.strip().split("/", 1)
        return cls(owner=owner, name=name)

    @property
    def full_name(self) -> str:
        return f"{self.owner}/{self.name}"


@dataclass
class Signal:
    signal_type: str
    key: str
    title: str
    severity: int
    details: str
    fingerprint: str
    url: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class VelocityMetrics:
    commit_count: int
    baseline_commit_count: int
    baseline_per_window: float
    multiplier: float
    lookback_hours: int
    baseline_days: int


@dataclass
class ScoreResult:
    heat_score: int
    reasons: list[str]
