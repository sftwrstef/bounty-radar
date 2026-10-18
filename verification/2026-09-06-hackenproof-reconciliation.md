# HackenProof reconciliation — 2026-09-06

Run time: `2026-09-06T09:41:27-04:00`

## Coverage health

- Local radar digest: **15/18** successful source fetches.
- Degraded sources: `broad-hackenproof-programs`, `hackenproof-programs`, and
  `hackenproof-audits`; each exceeded the 58-second browser wall-clock limit.
- Database delta: 16 `scope_changed` rows, all ordinary web/VDP listings; source
  alerts were HackerOne Essity and Intigriti challenge0826.
- Telegram outbox: zero pending rows.

## Official live reconciliation

- Programs page: <https://hackenproof.com/programs> — 323 results observed.
- New regular entries: Bullbit (September 4, max $50) and Hinkal (September 3/4,
  smart contracts, max $10,000).
- Recently updated smart-contract entries included Cetus, FlowX CLMM, Snowbridge,
  and Turbos. Cetus, Snowbridge, Turbos, and Hinkal already have local worked/collision
  state; FlowX did not.
- Audit programs: <https://hackenproof.com/audit-programs> — Alberich (ends
  September 8, max $3,000) and Zendex (ends September 9, max $2,000) are live
  competitions and were excluded by the regular-bounty-only policy.

## Selection

Selected exactly one regular target: FlowX CLMM Smart Contracts. The current
program details were pinned from
<https://hackenproof.com/programs/flowx-clmm-smart-contracts>, and the public
source was pinned at `87c6943fededfc7fd20e1ac65d8b142665799716`.

Terminal result: **BLOCKED / ROTATE at source/runtime preflight; exact pause-bypass
claim KILL at 2/5**. See the target-local `HUNT_STATUS.md`.
