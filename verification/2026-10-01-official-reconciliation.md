# Official source reconciliation - 2026-10-01

## Coverage

- Saved radar completed 15/18 source fetches.
- `broad-hackenproof-programs`, `hackenproof-programs`, and
  `hackenproof-audits` each exceeded the 58-second browser timeout. Coverage
  remains degraded even though the official pages were independently read.
- Telegram outbox: 194 total, 0 pending, 0 errored.

## Official HackenProof indexes

- Standing index: https://hackenproof.com/programs - 324 results. Ult remains
  the newest live launch (2026-09-28, up to $20,000). Starknet Blockchain/DLT
  shows a 2026-10-01 update but preserves the scoped Starknet OS and Cairo
  source list. Arcadia Finance shows a 2026-09-30 update and remains the same
  three repositories with current-live-state and strict impact rules. No new
  regular-bounty launch was found.
- Audit index: https://hackenproof.com/audit-programs - 99 results. RAIN-USDR
  remains the only live audit, ending 2026-10-01, with 924 submissions and a
  $14,000 cap. It is a contest and already has pending submission
  `RAINUSDR-1512`, so it was excluded from fresh regular-bounty selection.

## Database deltas

- Today's HackerOne, Bugcrowd, and Intigriti `scope_changed` rows are
  relative-age text churn, not authoritative asset/reward changes.
- Fresh Bugcrowd/Intigriti listings were Web2 marketplace/VDP entries and did
  not displace a source-accessible Medium+ Web3 target.
- Real repository delta: Optimism published five component releases at commit
  `9f76a9d216f2d9aa99c5f45d7aad674acde93c14`.

## Queue monitors

The Chainlink CCIP v2 USDC monitor returned `coverage_ok=true`, 62 matches,
`new_or_upgraded=0`, and 44 pending on-chain confirmations at
2026-10-01T13:35:01Z. No route crossed its reopen gate.

## Selection

Selected exactly one target: the Optimism 2026-10-01 release set under its
regular Immunefi bounty. See
`audit_targets/optimism-oct1-release-delta-immunefi-20261001/HUNT_STATUS.md`.
