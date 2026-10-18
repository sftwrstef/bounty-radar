# HackenProof official-index reconciliation — 2026-08-28

The 2026-08-28 radar digest completed `15/18` source fetches. The three failed
feeds were degraded coverage, not evidence of a quiet day:

- `broad-hackenproof-programs`
- `hackenproof-programs`
- `hackenproof-audits`

All three failures had the same local cause: Playwright `1.61.0` could not find
its matching `chromium_headless_shell-1228` executable.

The missing browser dependency was repaired after the digest when the data
volume had approximately `26 GiB` free:

```bash
bounty-radar/.venv/bin/python -m playwright install chromium-headless-shell
```

The install downloaded Chrome Headless Shell `149.0.7827.55` / Playwright
revision `1228` and FFmpeg revision `1011`. A clean headless launch then loaded
both official indexes with HTTP `200`:

```text
https://hackenproof.com/programs       200  Crypto Bug Bounty Programs 2026 | HackenProof
https://hackenproof.com/audit-programs 200  Audit programs 2026 | HackenProof
```

This validates the repaired browser runtime. The already-generated digest
remains accurately labeled `15/18`; no full radar rerun was performed because
that can mutate notification/outbox state. End-of-run dependency health is
therefore repaired, while the digest's historical coverage is still degraded.

Independent read-only reconciliation of the official indexes found:

- the standing-program index reported 321 programs;
- no regular program showed a genuine 28 August launch or scope addition;
- the newest visible standing-program change remained Cronos Web on 27 August;
- the audit index showed Zendex as its only live entry, a time-bounded
  DualDefense competition rather than a regular bounty;
- the Bugcrowd, HackerOne, and Intigriti database deltas were age/countdown or
  ordinary Web2 churn, not a new Web3 smart-contract surface.

Official-page and local-registry reconciliation excluded the strongest queue
alternatives: Arcadia, Ample, Cronos Smart Contracts, STBL, Ember Vaults, and
Bluefin were already worked; Calyx, Kai, ZO, and Zynk were paused; DoubleUp had
ended; FlowX was invite-only with a lower ceiling. No genuinely new Web3
regular-bounty program or scope expansion survived.

Two initially plausible fallbacks were rejected during continuity validation:

- Solv Smart Contracts already had a 28 July vault/withdrawal closeout in the
  worked-target registry and collision ledger under the offloaded directory
  `solv-smart-contracts-hackenproof-20260728`;
- Chainstack had a complete 17 August two-account REST/MCP authorization
  closeout in `vesper-brain`, even though it was not normalized into the central
  registry.

Zoomex Web & Mobile was the first genuinely untouched live standing target
after those collisions. It was selected for the run because its program is
public, funded, has 138 submissions / 78 hackers, has paid `$3,300`, and pays
up to `$10,000`. It was not a same-day scope delta. The web target returned an
Akamai-style HTTP `403 Access Denied` from this environment, so it failed the
runtime/preflight gate before authenticated or mobile testing.
