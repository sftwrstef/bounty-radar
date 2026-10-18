# Official source reconciliation — 2026-09-07

Run time: `2026-09-07T10:03:58-04:00`

## Coverage health

- Local radar digest: **15/18** successful sources.
- Degraded sources: `broad-hackenproof-programs`, `hackenproof-programs`, and
  `hackenproof-audits`; each exceeded the 58-second browser timeout.
- SQLite added only three non-Web3 item changes since the prior run: two
  HackerOne VDP records and one private Intigriti challenge.
- Hyperlane's 31-commit heat burst was relayer/validator/infra work outside the
  fixed Immunefi contract assets. Optimism's two commits were metrics/CI only.

## Official reconciliation

- HackenProof programs: no post-September-4 regular-program change. The newest
  smart-contract entries were already present and worked locally.
- HackenProof audits: Alberich (ends September 8, `$3,000`) and Zendex (ends
  September 9, `$2,000`) were live competitions and excluded.
- Immunefi: no post-September-6 catalog refresh or asset delta.
- Sherlock: the apparent broad launch bundle was a backfill/reset. The official
  live bounty directory had no September-7 update.

## Selection

Selected exactly one untouched regular bounty: Inverse Finance on Sherlock,
live with a `100,000 DOLA` maximum. The current deployment and release branch
were runtime-pinned and audited. Terminal result: **PARK one pre-liquidation
oracle-value slashing composition at Incubate 3/5; KILL the exact remaining
lanes**. See the target-local `HUNT_STATUS.md`.
