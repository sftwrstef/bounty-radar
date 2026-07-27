from __future__ import annotations

from datetime import datetime, timedelta, timezone
from collections.abc import Callable
from typing import Any

from bounty_radar.config import RadarSettings, load_tracked_config, resolve_github_token
from bounty_radar.digest import write_daily_digest
from bounty_radar.github_api import GitHubAPIError, GitHubClient
from bounty_radar.models import ScoreResult, Signal, VelocityMetrics
from bounty_radar.scanners.content import (
    scan_code_search,
    scan_commit_messages,
    scan_repository_text,
    scan_security_docs,
)
from bounty_radar.scanners.direct_programs import scan_direct_programs
from bounty_radar.scanners.releases import scan_releases
from bounty_radar.scanners.sources import scan_source
from bounty_radar.scanners.velocity import scan_velocity
from bounty_radar.scoring import score_repository
from bounty_radar.storage import Storage
from bounty_radar.telegram import TelegramClient, format_alert_message, format_source_alert_message


def _repo_text_sources(repo: dict[str, Any], readme: dict[str, Any] | None) -> list[dict[str, str]]:
    sources = [
        {
            "name": "repo_metadata",
            "text": " ".join(
                str(part or "")
                for part in (
                    repo.get("description"),
                    repo.get("homepage"),
                    " ".join(repo.get("topics") or []),
                )
            ),
            "url": repo.get("html_url") or "",
        }
    ]
    if readme:
        sources.append(
            {
                "name": readme.get("path", "README"),
                "text": readme.get("text", ""),
                "url": readme.get("html_url") or repo.get("html_url") or "",
            }
        )
    return sources


def _alert_reasons(
    *,
    score: ScoreResult,
    previous_heat_score: int | None,
    settings: RadarSettings,
    new_signals: list[Signal],
) -> list[str]:
    reasons: list[str] = []
    score_delta = score.heat_score - (previous_heat_score or 0)
    if score_delta >= settings.heat_score_spike_threshold:
        reasons.append(f"heat score spiked by {score_delta} points")
    if any(signal.signal_type in {"security_doc_new", "security_doc_changed"} for signal in new_signals):
        reasons.append("new or changed security policy document")
    if any(signal.signal_type == "bounty_reference" for signal in new_signals):
        reasons.append("new bounty platform/reference keyword")
    if any(signal.signal_type == "velocity_spike" for signal in new_signals):
        reasons.append("unusual commit velocity")
    if any(signal.signal_type == "release_new" for signal in new_signals):
        reasons.append("new GitHub release")
    if not reasons:
        return []
    return reasons + score.reasons[:4]


def _enumerate_repos(
    api: GitHubClient,
    repos: list[str],
    orgs: list[Any],
    settings: RadarSettings,
) -> tuple[list[dict[str, Any]], list[str]]:
    seen: set[str] = set()
    results: list[dict[str, Any]] = []
    errors: list[str] = []

    for full_name in repos:
        if full_name in seen:
            continue
        try:
            repo = api.get_repo(full_name)
        except GitHubAPIError as exc:
            errors.append(f"{full_name}: {exc}")
            continue
        seen.add(repo["full_name"])
        results.append(repo)

    for org in orgs:
        max_repos = org.max_repos or settings.max_org_repos
        try:
            org_repos = api.list_org_repos(
                org.name,
                include_archived=org.include_archived,
                max_repos=max_repos,
            )
        except GitHubAPIError as exc:
            errors.append(f"{org.name}: {exc}")
            continue
        for repo in org_repos:
            if repo["full_name"] in seen:
                continue
            seen.add(repo["full_name"])
            results.append(repo)

    return results, errors


def scan_one_repo(
    *,
    api: GitHubClient,
    storage: Storage,
    telegram: TelegramClient,
    repo: dict[str, Any],
    settings: RadarSettings,
    send_alerts: bool,
    now: datetime,
) -> dict[str, Any]:
    full_name = repo["full_name"]
    scanned_at = now.isoformat()
    storage.upsert_repo(repo, scanned_at)
    state = storage.get_repo_state(full_name)
    errors: list[str] = []

    lookback_start = now - timedelta(hours=settings.lookback_hours)
    baseline_start = now - timedelta(days=settings.baseline_days)

    current_commits = api.list_commits(full_name, since=lookback_start, max_pages=3)
    baseline_commits = api.list_commits(
        full_name,
        since=baseline_start,
        until=lookback_start,
        max_pages=5,
    )

    metrics, velocity_signals = scan_velocity(
        full_name,
        current_commits,
        baseline_commits,
        lookback_hours=settings.lookback_hours,
        baseline_days=settings.baseline_days,
        spike_multiplier=settings.velocity_spike_multiplier,
        min_commits=settings.velocity_min_commits,
        now=now,
    )

    readme = api.get_readme(full_name, ref=repo.get("default_branch"))
    signals, state_updates = scan_security_docs(api, repo, state)
    if settings.enable_release_scan:
        release_signals, release_state_updates = scan_releases(
            api,
            repo,
            state,
            lookback_hours=settings.lookback_hours,
            max_releases=settings.max_releases,
            now=now,
        )
        signals.extend(release_signals)
        state_updates.update(release_state_updates)
    signals.extend(scan_repository_text(full_name, _repo_text_sources(repo, readme)))
    signals.extend(scan_commit_messages(full_name, current_commits))
    signals.extend(velocity_signals)

    if settings.enable_code_search and api.token_provided:
        code_signals, code_errors = scan_code_search(
            api,
            full_name,
            max_terms=settings.max_code_search_terms,
        )
        signals.extend(code_signals)
        errors.extend(code_errors)

    score = score_repository(signals, metrics)
    last_scan = storage.get_last_scan(full_name)
    previous_heat_score = int(last_scan["heat_score"]) if last_scan else None
    scan_id = storage.insert_scan(
        full_name=full_name,
        scanned_at=scanned_at,
        score=score,
        previous_heat_score=previous_heat_score,
        metrics=metrics,
        errors=errors,
    )

    new_signals: list[Signal] = []
    for signal in signals:
        if storage.upsert_signal(full_name=full_name, scan_id=scan_id, signal=signal, seen_at=scanned_at):
            new_signals.append(signal)

    for key, value in state_updates.items():
        storage.set_repo_state(full_name, key, value, scanned_at)
    storage.set_repo_state(full_name, "last_heat_score", str(score.heat_score), scanned_at)
    storage.set_repo_state(full_name, "last_scan_at", scanned_at, scanned_at)

    alert_reasons = _alert_reasons(
        score=score,
        previous_heat_score=previous_heat_score,
        settings=settings,
        new_signals=new_signals,
    )
    score_delta = score.heat_score - (previous_heat_score or 0)
    alert_sent = False
    if send_alerts and alert_reasons:
        message = format_alert_message(
            full_name=full_name,
            repo_url=repo.get("html_url") or f"https://github.com/{full_name}",
            heat_score=score.heat_score,
            previous_heat_score=previous_heat_score,
            score_delta=score_delta,
            alert_reasons=alert_reasons,
            signals=new_signals,
        )
        alert_sent = telegram.send_message(message)
        storage.record_alert(
            full_name=full_name,
            scan_id=scan_id,
            alert_type="repo_heat",
            title="Repository heat alert",
            message=message,
            sent_at=scanned_at,
        )

    return {
        "repo": full_name,
        "heat_score": score.heat_score,
        "score_delta": score_delta,
        "new_signals": len(new_signals),
        "alert_reasons": alert_reasons,
        "alert_sent": alert_sent,
        "errors": errors,
    }


def scan_one_source(
    *,
    storage: Storage,
    telegram: TelegramClient,
    source: Any,
    settings: RadarSettings,
    send_alerts: bool,
    now: datetime,
) -> dict[str, Any]:
    scanned_at = now.isoformat()
    storage.upsert_source(
        name=source.name,
        url=source.url,
        kind=source.kind,
        seen_at=scanned_at,
    )
    signals, errors = scan_source(source)
    new_signals: list[Signal] = []
    for signal in signals:
        if storage.upsert_source_signal(
            source_name=source.name,
            signal=signal,
            seen_at=scanned_at,
        ):
            new_signals.append(signal)

    storage.set_source_state(source.name, "last_attempt_at", scanned_at, scanned_at)
    if errors:
        storage.set_source_state(source.name, "last_error", " | ".join(errors), scanned_at)
        storage.set_source_state(source.name, "last_error_at", scanned_at, scanned_at)
    else:
        storage.set_source_state(source.name, "last_scan_at", scanned_at, scanned_at)
        storage.set_source_state(source.name, "last_success_at", scanned_at, scanned_at)
        storage.set_source_state(source.name, "last_error", "", scanned_at)

    alert_signals = [
        signal for signal in new_signals if signal.severity >= settings.source_alert_min_severity
    ]
    alert_sent = False
    if send_alerts and alert_signals:
        message = format_source_alert_message(
            source_name=source.name,
            source_url=source.url,
            signals=alert_signals,
        )
        alert_sent = telegram.send_message(message)
        storage.record_source_alert(
            source_name=source.name,
            alert_type="source_launch",
            title="Fresh source launch signal",
            message=message,
            sent_at=scanned_at,
        )

    return {
        "source": source.name,
        "items": len(signals),
        "new_signals": len(new_signals),
        "alert_signals": len(alert_signals),
        "alert_sent": alert_sent,
        "coverage_ok": not errors,
        "errors": errors,
    }


def scan_direct_program_discovery(
    *,
    api: GitHubClient,
    storage: Storage,
    telegram: TelegramClient,
    settings: RadarSettings,
    send_alerts: bool,
    now: datetime,
) -> dict[str, Any]:
    """Run the global first-party policy discovery lane through source deduplication."""
    source_name = "github-direct-web3-programs"
    source_url = "https://github.com/search?q=%22bug+bounty%22+%22security%40%22&type=code"
    scanned_at = now.isoformat()
    storage.upsert_source(name=source_name, url=source_url, kind="github-code-search", seen_at=scanned_at)
    signals, errors = scan_direct_programs(api, max_results=settings.max_direct_program_results)
    new_signals = [
        signal
        for signal in signals
        if storage.upsert_source_signal(source_name=source_name, signal=signal, seen_at=scanned_at)
    ]
    storage.set_source_state(source_name, "last_attempt_at", scanned_at, scanned_at)
    if errors:
        storage.set_source_state(source_name, "last_error", " | ".join(errors), scanned_at)
        storage.set_source_state(source_name, "last_error_at", scanned_at, scanned_at)
    else:
        storage.set_source_state(source_name, "last_scan_at", scanned_at, scanned_at)
        storage.set_source_state(source_name, "last_success_at", scanned_at, scanned_at)
        storage.set_source_state(source_name, "last_error", "", scanned_at)

    alert_signals = [signal for signal in new_signals if signal.severity >= settings.source_alert_min_severity]
    alert_sent = False
    if send_alerts and alert_signals:
        message = format_source_alert_message(
            source_name=source_name,
            source_url=source_url,
            signals=alert_signals,
        )
        alert_sent = telegram.send_message(message)
        storage.record_source_alert(
            source_name=source_name,
            alert_type="direct_program_discovered",
            title="Direct bounty program discovered",
            message=message,
            sent_at=scanned_at,
        )

    return {
        "source": source_name,
        "items": len(signals),
        "new_signals": len(new_signals),
        "alert_signals": len(alert_signals),
        "alert_sent": alert_sent,
        "coverage_ok": not errors,
        "errors": errors,
    }


def run_scan(
    *,
    config_path: str,
    db_path: str,
    digest_dir: str,
    send_alerts: bool = True,
    progress: Callable[[str], None] | None = None,
) -> dict[str, Any]:
    def report(message: str) -> None:
        if progress is not None:
            progress(f"[bounty-radar] {message}")

    config = load_tracked_config(config_path)
    storage = Storage(db_path)
    storage.initialize()
    api = GitHubClient(resolve_github_token())
    telegram = TelegramClient()
    now = datetime.now(timezone.utc)
    results: list[dict[str, Any]] = []
    source_results: list[dict[str, Any]] = []
    errors: list[str] = []
    try:
        report("enumerating GitHub targets")
        repos, target_errors = _enumerate_repos(api, config.repos, config.orgs, config.settings)
        errors.extend(target_errors)

        if config.settings.enable_direct_program_discovery:
            report("direct-program discovery")
            direct_result = scan_direct_program_discovery(
                api=api,
                storage=storage,
                telegram=telegram,
                settings=config.settings,
                send_alerts=send_alerts,
                now=now,
            )
            source_results.append(direct_result)
            errors.extend(direct_result["errors"])

        for index, repo in enumerate(repos, start=1):
            full_name = repo.get("full_name", "unknown repository")
            report(f"repo {index}/{len(repos)}: {full_name}")
            try:
                results.append(
                    scan_one_repo(
                        api=api,
                        storage=storage,
                        telegram=telegram,
                        repo=repo,
                        settings=config.settings,
                        send_alerts=send_alerts,
                        now=now,
                    )
                )
            except Exception as exc:
                # One malformed response must not prevent the tracker from writing its digest.
                errors.append(f"{full_name}: unexpected scan failure: {type(exc).__name__}: {exc}")
                report(f"repo failed: {full_name}: {type(exc).__name__}")

        for index, source in enumerate(config.sources, start=1):
            report(f"source {index}/{len(config.sources)}: {source.name}")
            try:
                source_result = scan_one_source(
                    storage=storage,
                    telegram=telegram,
                    source=source,
                    settings=config.settings,
                    send_alerts=send_alerts,
                    now=now,
                )
            except Exception as exc:
                scanned_at = now.isoformat()
                error = f"{source.name}: unexpected scan failure: {type(exc).__name__}: {exc}"
                storage.upsert_source(
                    name=source.name,
                    url=source.url,
                    kind=source.kind,
                    seen_at=scanned_at,
                )
                storage.set_source_state(source.name, "last_attempt_at", scanned_at, scanned_at)
                storage.set_source_state(source.name, "last_error", error, scanned_at)
                storage.set_source_state(source.name, "last_error_at", scanned_at, scanned_at)
                source_result = {
                    "source": source.name,
                    "items": 0,
                    "new_signals": 0,
                    "alert_signals": 0,
                    "alert_sent": False,
                    "coverage_ok": False,
                    "errors": [error],
                }
                report(f"source failed: {source.name}: {type(exc).__name__}")
            source_results.append(source_result)
            errors.extend(source_result["errors"])

        digest_path = write_daily_digest(storage, digest_dir, now=now)
        report(f"digest written: {digest_path}")
        return {
            "scanned": len(results),
            "sources_scanned": len(source_results),
            "results": results,
            "source_results": source_results,
            "source_failures": sum(
                1 for result in source_results if not result.get("coverage_ok", False)
            ),
            "errors": errors,
            "digest_path": str(digest_path),
        }
    finally:
        storage.close()
