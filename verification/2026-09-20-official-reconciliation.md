# 2026-09-20 official source reconciliation

Reviewed at `2026-09-20T04:35Z`.

## Saved radar coverage

- The local-only scan completed `15/18` attempted source fetches and sent no
  alerts.
- `broad-hackenproof-programs`, `hackenproof-programs`, and
  `hackenproof-audits` each exceeded the 58-second browser wall timeout.
  Coverage is degraded, not quiet.
- The six broad-feed changes are five historical Sherlock contest rows and one
  Intel VDP row. They are scope/metadata churn rather than fresh paid contest
  launches. For example, the official Sherlock record places ZKP2P V2 in April
  2025 and Extra Finance in November 2024.
- The Telegram outbox remained healthy at `148 total / 0 pending / 0 errored`.

## Official HackenProof reconciliation

- `https://hackenproof.com/programs` returned HTTP 200 and `324 Results`, the
  same total as September 19. The newest visible regular program remains
  Hotcoin, started September 14 with a maximum reward of `$1,000`; no September
  20 standing smart-contract launch appeared.
- Hinkal remains live with a `$10,000` maximum and a September 3 start date. It
  is not a same-day launch or scope delta.
- `https://hackenproof.com/audit-programs` returned HTTP 200. RAIN-USDR remains
  the sole live audit, ending October 1 with a `$14,000` pool. It is a
  time-bounded audit contest, not a new standing-bounty lead. Europeum API is
  ended.
- Direct page SHA-256 values were
  `e0c68706e474599fd19e8137535e9613d4c2eeaf84cd60d56375ec9c2339bd7c`
  for the standing index and
  `d2d2ca6eb5e3611ed0a93e243478a9be33f0c9b9bcbd340393cec16a04a7e733`
  for the audit index.

## Selection consequence

Hinkal was rechecked because it remains the newest visible standing
smart-contract program with a material headline. Its source pin is still
`61b6839aa80fc0c33bfdcde0323753c83cb2ce67`, unchanged since August 31,
after a completed Quantstamp audit and four Vesper closeouts at the same pin.
Its surviving lanes remain proof-bound, recoverable, excluded, or exact
collisions; the current snapshot is **KILL / ROTATE** absent a post-audit live
implementation delta.

No new source-clean paid target displaces the current common_codes iOS wallet
candidate. Continue its released-build, verifier-role, and delivery falsifiers;
rotate only if one of those gates is contradicted or cannot be tested.

No login, account action, transaction, signature, fee, report, project contact,
submission, disclosure, clone, dependency installation, or public-chain write
occurred.

## Final daily-hunt refresh

Refreshed at `2026-09-20T13:34:26Z` after the completed local radar run.

- Direct read-only fetches still returned HTTP 200 and `324 Results` for the
  standing-program index. The response SHA-256 was
  `d361479a18e893f84c6d9a02cb86da858424891a4d1d799ed2a08cb3cb0556db`.
- The audit index still exposed RAIN-USDR as the live paid audit and no new
  regular smart-contract program. Its response SHA-256 was
  `af5dea8837d394f8e15817c56e3b6460fe4d6cb9c7a54614a4c1d1b2de671416`.
- The completed local scan remained degraded at `15/18`: all three
  HackenProof browser lanes timed out. Independent official reconciliation
  restores selection visibility but does not relabel the saved run healthy.
- SQLite recorded one new paid HackerOne launch signal: `common_codes`, the
  d-you App and German EUDI Wallet Ecosystem. The other same-day changes were
  VDPs, old contest metadata, or non-Web3 program churn. Telegram delivery
  finished at `151 total / 0 pending / 0 errored`.

The sole selected target was the current d-you iOS Test application. A bounded
released-build diagnostic reproduced the suspected retained-consent UI after
rejecting a second verifier, but neither that branch nor a brand-new A-only
production control produced any verifier-side response. The exact lane is
therefore `PARK 2/5 / ROTATE`, not a finding. Reopen only after an ordinary
A-only presentation succeeds with a known-good credential and valid relying
party, then rerun fresh candidate and control transactions and separately
establish an economically untrusted valid relying-party role.
