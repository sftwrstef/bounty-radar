from __future__ import annotations

import multiprocessing as mp
import os
import signal
import sys
from pathlib import Path

from bounty_radar.config import env_bool


class BrowserFetchError(RuntimeError):
    pass


def _multiprocessing_context() -> mp.context.BaseContext:
    # Chromium/Playwright is not fork-safe on macOS. A spawned worker avoids a
    # deadlocked browser child after the parent has imported networking modules.
    if os.name == "posix" and sys.platform == "darwin":
        return mp.get_context("spawn")
    if "fork" in mp.get_all_start_methods():
        return mp.get_context("fork")
    return mp.get_context("spawn")


def _fetch_rendered_html_inner(
    url: str,
    *,
    headless: bool,
    user_data_dir: str,
    user_agent: str,
    wait_ms: int = 5000,
    timeout_ms: int = 45000,
    fail_on_challenge: bool = True,
) -> str:
    try:
        from playwright.sync_api import Error as PlaywrightError
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise BrowserFetchError(
            "Playwright is not installed. Run `pip install -r requirements.txt` "
            "and `python -m playwright install chromium`."
        ) from exc

    try:
        with sync_playwright() as playwright:
            close_target = None
            try:
                if user_data_dir:
                    context = playwright.chromium.launch_persistent_context(
                        str(Path(user_data_dir).expanduser()),
                        headless=headless,
                        user_agent=user_agent,
                        viewport={"width": 1440, "height": 1200},
                    )
                    page = context.pages[0] if context.pages else context.new_page()
                    close_target = context
                else:
                    browser = playwright.chromium.launch(headless=headless)
                    context = browser.new_context(
                        user_agent=user_agent,
                        viewport={"width": 1440, "height": 1200},
                    )
                    page = context.new_page()
                    close_target = browser

                page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
                if wait_ms > 0:
                    # Some anti-bot or JS-heavy pages never reach a clean
                    # "networkidle" state, which can stall the whole daily scan.
                    page.wait_for_timeout(min(wait_ms, timeout_ms))
                html = page.content()
                if fail_on_challenge and looks_like_challenge_page(html):
                    raise BrowserFetchError(
                        "browser received an anti-bot challenge page. Try a one-time headed "
                        "warm-up with `BOUNTY_RADAR_BROWSER_HEADLESS=false python -m "
                        "bounty_radar warm-source <source-name>` and keep "
                        "`BOUNTY_RADAR_BROWSER_USER_DATA_DIR` stable."
                    )
                return html
            finally:
                if close_target is not None:
                    close_target.close()
    except PlaywrightError as exc:
        raise BrowserFetchError(str(exc)) from exc


def _browser_fetch_worker(
    conn: mp.connection.Connection,
    *,
    url: str,
    headless: bool,
    user_data_dir: str,
    user_agent: str,
    wait_ms: int,
    timeout_ms: int,
    fail_on_challenge: bool,
) -> None:
    if os.name == "posix":
        try:
            # Put the worker and Chromium children in their own process group so
            # a wall-clock timeout can clean up the entire browser tree.
            os.setsid()
        except OSError:
            pass
    try:
        html = _fetch_rendered_html_inner(
            url,
            headless=headless,
            user_data_dir=user_data_dir,
            user_agent=user_agent,
            wait_ms=wait_ms,
            timeout_ms=timeout_ms,
            fail_on_challenge=fail_on_challenge,
        )
        conn.send(("ok", html))
    except Exception as exc:
        conn.send(("err", str(exc)))
    finally:
        conn.close()


def _terminate_worker_tree(proc: mp.Process) -> None:
    if not proc.is_alive():
        return

    if os.name == "posix":
        try:
            os.killpg(proc.pid, signal.SIGTERM)
        except (ProcessLookupError, PermissionError):
            proc.terminate()
    else:
        proc.terminate()

    proc.join(5)
    if not proc.is_alive():
        return

    if os.name == "posix":
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            proc.kill()
    else:
        proc.kill()
    proc.join(5)


def fetch_rendered_html(
    url: str,
    *,
    wait_ms: int = 5000,
    timeout_ms: int = 45000,
    fail_on_challenge: bool = True,
) -> str:
    headless = env_bool("BOUNTY_RADAR_BROWSER_HEADLESS", True)
    user_data_dir = os.getenv(
        "BOUNTY_RADAR_BROWSER_USER_DATA_DIR",
        "/Users/sftwr/.codex/browser-profiles/vesper-bounty-radar",
    )
    user_agent = os.getenv(
        "BOUNTY_RADAR_BROWSER_USER_AGENT",
        (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
    )
    wall_timeout_ms = int(
        os.getenv(
            "BOUNTY_RADAR_BROWSER_WALL_TIMEOUT_MS",
            str(
                max(
                    30000,
                    min(timeout_ms + min(wait_ms, timeout_ms) + 5000, 70000),
                )
            ),
        )
    )

    ctx = _multiprocessing_context()
    parent_conn, child_conn = ctx.Pipe(duplex=False)
    proc = ctx.Process(
        target=_browser_fetch_worker,
        kwargs={
            "conn": child_conn,
            "url": url,
            "headless": headless,
            "user_data_dir": user_data_dir,
            "user_agent": user_agent,
            "wait_ms": wait_ms,
            "timeout_ms": timeout_ms,
            "fail_on_challenge": fail_on_challenge,
        },
    )
    proc.start()
    child_conn.close()
    proc.join(wall_timeout_ms / 1000)
    try:
        if proc.is_alive():
            _terminate_worker_tree(proc)
            raise BrowserFetchError(
                f"browser fetch exceeded {wall_timeout_ms}ms wall-clock timeout"
            )

        if parent_conn.poll():
            status, payload = parent_conn.recv()
            if status == "ok":
                return payload
            raise BrowserFetchError(payload)

        raise BrowserFetchError(
            f"browser fetch exited without result (exit code {proc.exitcode})"
        )
    finally:
        parent_conn.close()


def looks_like_challenge_page(html: str) -> bool:
    lowered = html.lower()
    return (
        "just a moment" in lowered
        and "cf-chl" in lowered
        and "cloudflare" in lowered
    )
