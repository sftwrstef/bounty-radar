# 2026-09-19 official source reconciliation

Reviewed at `2026-09-19T13:39:18Z`.

## Saved radar coverage

- The generated digest completed `15/18` attempted source fetches.
- `broad-hackenproof-programs`, `hackenproof-programs`, and
  `hackenproof-audits` each exceeded the 58-second browser wall timeout.
  Coverage is degraded, not quiet.
- SQLite recorded 19 source-item changes: 11 Bugcrowd marketplace/VDP rows,
  one Intigriti VDP, one older YesWeHack web/API program, and six broad rows.
  The four Sherlock rows are historical contest backfill; the remaining broad
  rows are an older huntr contest and age/reward churn.
- Telegram outbox is healthy at `148 total / 0 pending / 0 errored`.

## Official HackenProof reconciliation

- `https://hackenproof.com/programs` returned HTTP 200 and `324 Results`.
  No September 19 regular smart-contract launch appeared.
- The apparent September 18 ADI Predictstreet update is not a source delta:
  `git ls-remote` still resolves the sole scoped repository to the already
  worked `c9a05365b6ecdb9748daa28928e08d1269916871` commit. Its page now shows
  39 submissions; the source, fixed rewards, fee, and eligibility gates are
  unchanged from the prior Vesper closeout.
- `https://hackenproof.com/audit-programs` returned HTTP 200. RAIN-USDR is the
  sole live audit entry and is excluded as a time-bounded, fee-bearing contest.
  Europeum API ended September 17.
- Direct page SHA-256 values were
  `f9fd1d0766f14baa442e4d7a220a318926ec250c33308f9cd05f6961de4383b9`
  for the standing index and
  `ee89d67e68ccf3352c69f0375685310d57d7888aa5a0f3fc13b3e91282ef7eee`
  for the audit index.

## Repository deltas and selection

- Optimism's September 18 commits remove legacy import commands, bound
  development-stack readiness probes, reject simultaneous configured fork
  activations, and enforce Lagoon span-batch slot rules. The security-relevant
  roots are unreleased `develop` fixes already disclosed by their PRs, so they
  lack a collision-clean live primary-chain delta.
- Hyperlane Registry PR #1712 is a genuine September 19 production-
  configuration delta. It replaces the advertised Eclipse, Solana, and Sonic
  SVM multisig ISM addresses because the prior deployments used stale validator
  snapshots. It was selected as today's one target because it is newer and more
  deployment-proximate than the Optimism queue.
- Finalized live reads show that Solana and Eclipse still use the old ISMs,
  Sonic SVM uses a third existing ISM, and all three new addresses are deployed
  but not active. The PR explicitly records pending privileged activation.

Selected target: Hyperlane SVM multisig-ISM rotation. Terminal result:
**KILL exact lane / ROTATE — strict 1/5; SCOPE CONTRADICTED**. See
`audit_targets/hyperlane-svm-ism-rotation-immunefi-20260919/HUNT_STATUS.md`.

No login, account, signature, transaction, fee, report, project contact,
submission, disclosure, clone, dependency installation, or public-chain write
occurred.

