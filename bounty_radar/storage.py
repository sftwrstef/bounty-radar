from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from bounty_radar.models import ScoreResult, Signal, VelocityMetrics


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class Storage:
    def __init__(self, db_path: str | Path) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row

    def close(self) -> None:
        self.conn.close()

    def initialize(self) -> None:
        schema_path = Path(__file__).with_name("schema.sql")
        self.conn.executescript(schema_path.read_text(encoding="utf-8"))
        self.conn.commit()

    def upsert_repo(self, repo: dict[str, Any], scanned_at: str) -> None:
        owner, name = repo["full_name"].split("/", 1)
        self.conn.execute(
            """
            INSERT INTO repos (
                full_name, owner, name, html_url, description, default_branch,
                archived, pushed_at, last_seen_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(full_name) DO UPDATE SET
                html_url=excluded.html_url,
                description=excluded.description,
                default_branch=excluded.default_branch,
                archived=excluded.archived,
                pushed_at=excluded.pushed_at,
                last_seen_at=excluded.last_seen_at
            """,
            (
                repo["full_name"],
                owner,
                name,
                repo.get("html_url"),
                repo.get("description"),
                repo.get("default_branch"),
                1 if repo.get("archived") else 0,
                repo.get("pushed_at"),
                scanned_at,
            ),
        )
        self.conn.commit()

    def get_repo_state(self, full_name: str) -> dict[str, str]:
        rows = self.conn.execute(
            "SELECT key, value FROM repo_state WHERE repo_full_name = ?",
            (full_name,),
        ).fetchall()
        return {str(row["key"]): str(row["value"]) for row in rows}

    def set_repo_state(self, full_name: str, key: str, value: str, updated_at: str) -> None:
        self.conn.execute(
            """
            INSERT INTO repo_state(repo_full_name, key, value, updated_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(repo_full_name, key) DO UPDATE SET
                value=excluded.value,
                updated_at=excluded.updated_at
            """,
            (full_name, key, value, updated_at),
        )
        self.conn.commit()

    def get_last_scan(self, full_name: str) -> dict[str, Any] | None:
        row = self.conn.execute(
            """
            SELECT * FROM repo_scans
            WHERE repo_full_name = ?
            ORDER BY scanned_at DESC
            LIMIT 1
            """,
            (full_name,),
        ).fetchone()
        return dict(row) if row else None

    def insert_scan(
        self,
        *,
        full_name: str,
        scanned_at: str,
        score: ScoreResult,
        previous_heat_score: int | None,
        metrics: VelocityMetrics,
        errors: list[str],
    ) -> int:
        score_delta = score.heat_score - (previous_heat_score or 0)
        summary = {
            "reasons": score.reasons,
            "errors": errors,
            "metrics": {
                "commit_count": metrics.commit_count,
                "baseline_commit_count": metrics.baseline_commit_count,
                "baseline_per_window": metrics.baseline_per_window,
                "multiplier": metrics.multiplier,
                "lookback_hours": metrics.lookback_hours,
                "baseline_days": metrics.baseline_days,
            },
        }
        cursor = self.conn.execute(
            """
            INSERT INTO repo_scans (
                repo_full_name, scanned_at, heat_score, previous_heat_score, score_delta,
                commit_count_24h, baseline_commit_count, velocity_multiplier, summary_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                full_name,
                scanned_at,
                score.heat_score,
                previous_heat_score,
                score_delta,
                metrics.commit_count,
                metrics.baseline_commit_count,
                metrics.multiplier,
                json.dumps(summary, sort_keys=True),
            ),
        )
        self.conn.commit()
        return int(cursor.lastrowid)

    def upsert_signal(
        self,
        *,
        full_name: str,
        scan_id: int,
        signal: Signal,
        seen_at: str,
    ) -> bool:
        metadata_json = json.dumps(signal.metadata, sort_keys=True)
        cursor = self.conn.execute(
            """
            INSERT OR IGNORE INTO signals (
                repo_full_name, fingerprint, signal_type, signal_key, severity,
                title, details, url, metadata_json, first_seen_at, last_seen_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                full_name,
                signal.fingerprint,
                signal.signal_type,
                signal.key,
                signal.severity,
                signal.title,
                signal.details,
                signal.url,
                metadata_json,
                seen_at,
                seen_at,
            ),
        )
        is_new = cursor.rowcount == 1
        if not is_new:
            self.conn.execute(
                """
                UPDATE signals
                SET last_seen_at = ?, occurrences = occurrences + 1,
                    title = ?, details = ?, url = ?, metadata_json = ?
                WHERE repo_full_name = ? AND fingerprint = ?
                """,
                (
                    seen_at,
                    signal.title,
                    signal.details,
                    signal.url,
                    metadata_json,
                    full_name,
                    signal.fingerprint,
                ),
            )

        signal_id = self.conn.execute(
            "SELECT id FROM signals WHERE repo_full_name = ? AND fingerprint = ?",
            (full_name, signal.fingerprint),
        ).fetchone()["id"]
        self.conn.execute(
            """
            INSERT OR REPLACE INTO scan_signals(scan_id, signal_id, is_new)
            VALUES (?, ?, ?)
            """,
            (scan_id, signal_id, 1 if is_new else 0),
        )
        self.conn.commit()
        return is_new

    def record_alert(
        self,
        *,
        full_name: str,
        scan_id: int,
        alert_type: str,
        title: str,
        message: str,
        sent_at: str,
    ) -> None:
        self.conn.execute(
            """
            INSERT INTO alerts(repo_full_name, scan_id, alert_type, title, message, sent_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (full_name, scan_id, alert_type, title, message, sent_at),
        )
        self.conn.commit()

    def latest_scans_since(self, since_iso: str) -> list[dict[str, Any]]:
        rows = self.conn.execute(
            """
            SELECT s.*
            FROM repo_scans s
            JOIN (
                SELECT repo_full_name, MAX(scanned_at) AS max_scanned_at
                FROM repo_scans
                WHERE scanned_at >= ?
                GROUP BY repo_full_name
            ) latest
            ON latest.repo_full_name = s.repo_full_name
            AND latest.max_scanned_at = s.scanned_at
            ORDER BY s.heat_score DESC, s.score_delta DESC
            """,
            (since_iso,),
        ).fetchall()
        return [dict(row) for row in rows]

    def new_signals_since(self, since_iso: str) -> list[dict[str, Any]]:
        rows = self.conn.execute(
            """
            SELECT * FROM signals
            WHERE first_seen_at >= ?
            ORDER BY severity DESC, first_seen_at DESC
            """,
            (since_iso,),
        ).fetchall()
        return [dict(row) for row in rows]

    def alerts_since(self, since_iso: str) -> list[dict[str, Any]]:
        rows = self.conn.execute(
            """
            SELECT * FROM alerts
            WHERE sent_at >= ?
            ORDER BY sent_at DESC
            """,
            (since_iso,),
        ).fetchall()
        return [dict(row) for row in rows]

    def upsert_source(self, *, name: str, url: str, kind: str, seen_at: str) -> None:
        self.conn.execute(
            """
            INSERT INTO sources(name, url, kind, last_seen_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(name) DO UPDATE SET
                url=excluded.url,
                kind=excluded.kind,
                last_seen_at=excluded.last_seen_at
            """,
            (name, url, kind, seen_at),
        )
        self.conn.commit()

    def get_source_state(self, source_name: str) -> dict[str, str]:
        rows = self.conn.execute(
            "SELECT key, value FROM source_state WHERE source_name = ?",
            (source_name,),
        ).fetchall()
        return {str(row["key"]): str(row["value"]) for row in rows}

    def set_source_state(self, source_name: str, key: str, value: str, updated_at: str) -> None:
        self.conn.execute(
            """
            INSERT INTO source_state(source_name, key, value, updated_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(source_name, key) DO UPDATE SET
                value=excluded.value,
                updated_at=excluded.updated_at
            """,
            (source_name, key, value, updated_at),
        )
        self.conn.commit()

    def upsert_source_signal(
        self,
        *,
        source_name: str,
        signal: Signal,
        seen_at: str,
    ) -> bool:
        metadata_json = json.dumps(signal.metadata, sort_keys=True)
        cursor = self.conn.execute(
            """
            INSERT OR IGNORE INTO source_signals (
                source_name, fingerprint, signal_type, signal_key, severity,
                title, details, url, metadata_json, first_seen_at, last_seen_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                source_name,
                signal.fingerprint,
                signal.signal_type,
                signal.key,
                signal.severity,
                signal.title,
                signal.details,
                signal.url,
                metadata_json,
                seen_at,
                seen_at,
            ),
        )
        is_new = cursor.rowcount == 1
        if not is_new:
            self.conn.execute(
                """
                UPDATE source_signals
                SET last_seen_at = ?, occurrences = occurrences + 1,
                    title = ?, details = ?, url = ?, metadata_json = ?
                WHERE source_name = ? AND fingerprint = ?
                """,
                (
                    seen_at,
                    signal.title,
                    signal.details,
                    signal.url,
                    metadata_json,
                    source_name,
                    signal.fingerprint,
                ),
            )
        self.conn.commit()
        return is_new

    def record_source_alert(
        self,
        *,
        source_name: str,
        alert_type: str,
        title: str,
        message: str,
        sent_at: str,
    ) -> None:
        self.conn.execute(
            """
            INSERT INTO source_alerts(source_name, alert_type, title, message, sent_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (source_name, alert_type, title, message, sent_at),
        )
        self.conn.commit()

    def source_signals_since(self, since_iso: str) -> list[dict[str, Any]]:
        rows = self.conn.execute(
            """
            SELECT * FROM source_signals
            WHERE first_seen_at >= ?
            ORDER BY severity DESC, first_seen_at DESC
            """,
            (since_iso,),
        ).fetchall()
        return [dict(row) for row in rows]

    def source_alerts_since(self, since_iso: str) -> list[dict[str, Any]]:
        rows = self.conn.execute(
            """
            SELECT * FROM source_alerts
            WHERE sent_at >= ?
            ORDER BY sent_at DESC
            """,
            (since_iso,),
        ).fetchall()
        return [dict(row) for row in rows]

    def source_coverage_since(self, since_iso: str) -> list[dict[str, Any]]:
        rows = self.conn.execute(
            """
            SELECT
                attempt.source_name,
                attempt.value AS attempted_at,
                COALESCE(error.value, '') AS error
            FROM source_state attempt
            LEFT JOIN source_state error
                ON error.source_name = attempt.source_name
                AND error.key = 'last_error'
            WHERE attempt.key = 'last_attempt_at'
                AND attempt.updated_at >= ?
            ORDER BY attempt.source_name
            """,
            (since_iso,),
        ).fetchall()
        return [dict(row) for row in rows]
