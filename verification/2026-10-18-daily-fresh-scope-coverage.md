# Daily fresh-scope coverage — 2026-10-18

Reviewed at 2026-10-18 10:57 EDT.

## Coverage health

- Canonical scanner: **degraded, 15/18**.
- Failed sources: `broad-hackenproof-programs`, `hackenproof-programs`, and
  `hackenproof-audits`; each exceeded the 58-second browser wall-clock limit.
- Digest: [`../digests/2026-10-18.md`](../digests/2026-10-18.md), generated at
  `2026-10-18T13:26:18.663149Z`.
- Both official HackenProof indexes were separately reconciled. This restores
  target-selection visibility but does not upgrade scanner coverage to healthy.

## Official-index reconciliation

- [HackenProof programs](https://hackenproof.com/programs/): ZMO Exchange
  remains the newest standing program (started and last updated 2026-10-14).
  No newer standing-program row was present.
- [HackenProof audit programs](https://hackenproof.com/audit-programs/): the
  official index remains at 103 entries. Europeum V2 API remains the newest
  audit (opened 2026-10-16); no entry was added after the 2026-10-17 baseline.
- The repeated Rain row is the already-reconciled 2026-10-16 Cantina launch.
  The Bugcrowd rows were 3–10 days old, the HackerOne row was an unpaid VDP,
  and Revert v4lend changed only its countdown. These are churn, not fresh
  scope deltas.

Disposition: `NO_MATERIAL_SCOPE_DELTA` with degraded canonical coverage.
Current official visibility is sufficient for the selected queued target only.

## Routing and selected target

This run followed the **degraded-coverage / queued-target branch**. Arcadia
Finance ranked first because the previous run had an exact executable next
question blocked only by the configured external-storage gate, and the Extreme
SSD is now mounted with the expected encrypted UUID
`D98BA803-94E7-4B08-8594-7EEB06B2288E`.

Arcadia's [official program](https://hackenproof.com/programs/arcadia-finance-company-smart-contracts)
was independently verified active on 2026-10-18. `accounts-v2`, `lending-v2`,
and `asset-managers` remain listed; Robinhood Chain is explicitly covered;
Medium is paid up to `$2,000`; and the program requires current live-state
preconditions and a runnable Foundry PoC for High/Critical. The official
address documentation pins the Robinhood WETH and USDG creditors and tranches
to `lending-v2` tag `v2.0.0` (`82398b0f4aeac29d9d2b05bd44b6169a63f074ea`).

The frozen Extra Finance same-asset liquidation package remains a separate
`SUBMIT NARROWER / Medium / 5-of-5` approval boundary and was not modified.

