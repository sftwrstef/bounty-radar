<div align="center">

```text
██████╗  ██████╗ ██╗   ██╗███╗   ██╗████████╗██╗   ██╗    ██████╗  █████╗ ██████╗  █████╗ ██████╗
██╔══██╗██╔═══██╗██║   ██║████╗  ██║╚══██╔══╝╚██╗ ██╔╝    ██╔══██╗██╔══██╗██╔══██╗██╔══██╗██╔══██╗
██████╔╝██║   ██║██║   ██║██╔██╗ ██║   ██║    ╚████╔╝     ██████╔╝███████║██║  ██║███████║██████╔╝
██╔══██╗██║   ██║██║   ██║██║╚██╗██║   ██║     ╚██╔╝      ██╔══██╗██╔══██║██║  ██║██╔══██║██╔══██╗
██████╔╝╚██████╔╝╚██████╔╝██║ ╚████║   ██║      ██║       ██║  ██║██║  ██║██████╔╝██║  ██║██║  ██║
╚═════╝  ╚═════╝  ╚═════╝ ╚═╝  ╚═══╝   ╚═╝      ╚═╝       ╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝
```

**Passive bounty intelligence for hunters who care about signal, not noise.**

[![Python](https://img.shields.io/badge/Python-3.11%2B-00ff88?style=for-the-badge&labelColor=07110c)](https://www.python.org/)
[![Mode](https://img.shields.io/badge/mode-passive%20recon-00ff88?style=for-the-badge&labelColor=07110c)](#what-it-watches)
[![Alerts](https://img.shields.io/badge/alerts-Telegram-00ff88?style=for-the-badge&labelColor=07110c)](#telegram-alerts)
[![License](https://img.shields.io/badge/license-add%20one-f6c945?style=for-the-badge&labelColor=07110c)](#before-you-publish)

</div>

> [!IMPORTANT]
> **Bounty Radar is a read-only signal layer.** It watches public GitHub and
> public program pages, scores meaningful movement, and alerts only on deltas.
> It does not probe targets, submit reports, or replace human verification.

## `// mission`

Most bounty feeds are noisy. Most repository activity is irrelevant. Bounty
Radar combines both into a local, deduplicated decision feed:

```text
public repos + public bounty feeds
              │
              ├── security policy / release / commit-velocity deltas
              ├── launch / reward / scope-shaped source signals
              └── local SQLite memory + duplicate suppression
                               │
                         Telegram + daily digest
```

It is designed to answer one useful question quickly:

> **What changed that is actually worth opening today?**

## `// what it watches`

| Signal lane | Examples | Why it matters |
| --- | --- | --- |
| Repository heat | `SECURITY.md`, bounty references, audit language, releases, commit velocity | Finds projects whose security posture or code is moving. |
| Platform launches | HackenProof programs and audits, Cantina, Sherlock, Code4rena, CodeHawks, discovery feeds | Surfaces fresh places to hunt before they become crowded. |
| Scope-shaped changes | New URLs, updated listings, bounty/reward language, direct-submit eligibility | Keeps a target board from going stale. |
| Delivery | Telegram alerts, daily Markdown digest, SQLite history | Makes repeated scans quiet unless the underlying state changed. |

## `// quick start`

```bash
git clone https://github.com/YOUR_HANDLE/bounty-radar.git
cd bounty-radar

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m playwright install chromium

cp .env.example .env
cp tracked_orgs.example.json tracked_orgs.json

python -m bounty_radar init-db
DISABLE_TELEGRAM=true python -m bounty_radar scan --progress --json
```

The first scan creates local state in `data/` and a Markdown digest in
`digests/`. Both are intentionally ignored by Git.

## `// operator commands`

```bash
# Run the normal daily pass. Progress writes to stderr; JSON stays script-safe.
python -m bounty_radar scan --progress --json

# Rebuild today's digest from local SQLite state.
python -m bounty_radar digest

# Confirm Telegram is wired without printing secrets.
python -m bounty_radar check-telegram

# Send an explicit Telegram delivery test.
python -m bounty_radar check-telegram --send-test
```

### Browser-backed sources

Some platforms place browser or Cloudflare challenges in front of their public
pages. Keep a stable profile directory and warm it visibly when needed:

```bash
BOUNTY_RADAR_BROWSER_HEADLESS=false \
python -m bounty_radar warm-source hackenproof-programs --headed
```

If an official page verifies a fresh item while the local browser lane is
challenged, record it through the same deduplication and alert path:

```bash
python -m bounty_radar record-source hackenproof-programs \
  --title "Verified program title" \
  --url "https://example.com/program" \
  --summary "Official NEW/LIVE listing; reward and scope verified"
```

## `// configuration`

Copy the templates first:

```bash
cp .env.example .env
cp tracked_orgs.example.json tracked_orgs.json
```

`tracked_orgs.json` controls tracked organizations, repositories, public
sources, thresholds, and the distinction between broad discovery and directly
huntable lanes. Keep it personal: it is ignored so your active watchlist does
not become public by accident.

`.env` is also ignored. Typical values are:

```dotenv
BOUNTY_RADAR_GITHUB_TOKEN=github_pat_or_classic_token
TELEGRAM_BOT_TOKEN=123456:bot-token
TELEGRAM_CHAT_ID=123456789
BOUNTY_RADAR_BROWSER_HEADLESS=true
BOUNTY_RADAR_BROWSER_USER_DATA_DIR=data/browser-profile
TRACKED_CONFIG=tracked_orgs.json
BOUNTY_RADAR_DB=data/bounty_radar.sqlite
DIGEST_DIR=digests
```

`BOUNTY_RADAR_GITHUB_TOKEN` is optional, but increases API headroom for code
search. Telegram credentials are optional; without both, the radar simply
writes local digests.

## `// project map`

```text
bounty_radar/
├── runner.py           scan orchestration and alert flow
├── scoring.py          heat-score rules
├── storage.py          SQLite state and deduplication
├── telegram.py         delivery client
├── digest.py           daily Markdown digest
├── github_api.py       GitHub REST wrapper
├── browser_fetch.py    isolated Chromium fetches
└── scanners/           repository, release, velocity, and source scanners

tracked_orgs.example.json  safe configuration template
.env.example               safe environment template
.github/workflows/         hourly GitHub Actions runner
```

## `// telegram alerts`

1. Create a bot through `@BotFather`.
2. Send the bot one message.
3. Put its token and your chat ID in `.env`.
4. Run `python -m bounty_radar check-telegram --send-test`.

Alerts are sent only for new, deduplicated signals. Re-running a scan should
not repeat the same launch merely because a page is still live.

## `// GitHub Actions`

An hourly workflow is included at
[`.github/workflows/bounty-radar.yml`](.github/workflows/bounty-radar.yml).
Add these repository secrets before enabling live delivery:

- `BOUNTY_RADAR_GITHUB_TOKEN` — optional, improves GitHub API limits.
- `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` — enables alert delivery.

The public workflow runs the safe template configuration by default. In your
private fork, point `TRACKED_CONFIG` at your own copied configuration when you
want repository-specific monitoring. The workflow caches only local radar state
and uploads Markdown digests as run artifacts. Do not put secrets in
`tracked_orgs.json`, digests, or the database.

## `// before you publish`

This repository is configured to keep private operational state out of Git:

- `.env` and virtual environments
- SQLite state, WAL/SHM files, browser profiles, and caches
- generated daily digests
- your active `tracked_orgs.json` watchlist

Commit the supplied templates, not your live state. Review `git status` before
every push — especially after a browser warm-up or a live Telegram test.

---

<div align="center">

`signal > noise` &nbsp;·&nbsp; `verify before hunting` &nbsp;·&nbsp; `dedupe before alerting`

</div>
