from __future__ import annotations

import os

from bounty_radar.config import env_bool, requests_verify_path
from bounty_radar.models import Signal


TOKEN_ENV_KEYS = (
    "TELEGRAM_BOT_TOKEN",
    "TELEGRAM_TOKEN",
    "AUDIT_TELEGRAM_BOT_TOKEN",
    "AUDIT_TELEGRAM_TOKEN",
    "BOUNTY_RADAR_TELEGRAM_BOT_TOKEN",
    "BOUNTY_RADAR_TELEGRAM_TOKEN",
)

CHAT_ENV_KEYS = (
    "TELEGRAM_CHAT_ID",
    "AUDIT_TELEGRAM_CHAT_ID",
    "BOUNTY_RADAR_TELEGRAM_CHAT_ID",
)


def _first_env(keys: tuple[str, ...]) -> str | None:
    for key in keys:
        value = os.getenv(key)
        if value:
            return value
    return None


class TelegramClient:
    def __init__(self, token: str | None = None, chat_id: str | None = None) -> None:
        self.token = token or _first_env(TOKEN_ENV_KEYS)
        self.chat_id = chat_id or _first_env(CHAT_ENV_KEYS)
        self.enabled = bool(self.token and self.chat_id) and not env_bool("DISABLE_TELEGRAM", False)

    def send_message(self, message: str) -> bool:
        if not self.enabled:
            return False
        import requests

        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        response = requests.post(
            url,
            json={
                "chat_id": self.chat_id,
                "text": message[:3900],
                "disable_web_page_preview": True,
            },
            timeout=20,
            verify=requests_verify_path(),
        )
        response.raise_for_status()
        return True


def format_alert_message(
    *,
    full_name: str,
    repo_url: str,
    heat_score: int,
    previous_heat_score: int | None,
    score_delta: int,
    alert_reasons: list[str],
    signals: list[Signal],
) -> str:
    previous = "new" if previous_heat_score is None else str(previous_heat_score)
    lines = [
        "Bounty Radar alert",
        f"Repo: {full_name}",
        f"Heat: {heat_score} (previous {previous}, delta {score_delta:+d})",
        f"URL: {repo_url}",
        "",
        "Why:",
    ]
    lines.extend(f"- {reason}" for reason in alert_reasons[:6])
    if signals:
        lines.append("")
        lines.append("Signals:")
        for signal in signals[:6]:
            suffix = f" ({signal.url})" if signal.url else ""
            lines.append(f"- {signal.title}: {signal.key}{suffix}")
    return "\n".join(lines)


def format_source_alert_message(
    *,
    source_name: str,
    source_url: str,
    signals: list[Signal],
) -> str:
    lines = [
        "Bounty Radar source alert",
        f"Source: {source_name}",
        f"URL: {source_url}",
        "",
        "Fresh items:",
    ]
    for signal in signals[:8]:
        suffix = f" ({signal.url})" if signal.url else ""
        matches = ", ".join(signal.metadata.get("matches", [])[:4])
        match_text = f" [{matches}]" if matches else ""
        lines.append(f"- {signal.key}{match_text}{suffix}")
    return "\n".join(lines)
