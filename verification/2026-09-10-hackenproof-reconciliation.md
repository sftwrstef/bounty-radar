# HackenProof reconciliation — 2026-09-10

## Coverage state

- The saved 12:45 UTC digest reported `15/18` successful sources. `broad-hackenproof-programs`, `hackenproof-audits`, and `hackenproof-programs` timed out.
- Manual official-index reconciliation was therefore required before target selection.
- A later 21:08 EDT scanner pass successfully detected the official audit-index launch described below. This repairs selection confidence, but it does not rewrite the earlier degraded digest.

## Official indices

- Regular programs: <https://hackenproof.com/programs> showed 323 results. No September 10 regular smart-contract launch or eligible High/Critical deployment delta was present. Bullbit was the newest visible regular change (September 9), but it was paused, web/application scoped, and capped at $50.
- Audit programs: <https://hackenproof.com/audit-programs> added **Europeum API DualDefense Audit**, live September 10–17 with a $5,000 maximum. It is an audit competition, so the daily regular-bounty workflow excludes it.
- The database alert at `2026-09-11T01:08:00.301069+00:00` independently records the Europeum source launch. The other late source alerts were broad web/VDP listings rather than a fresh High/Critical onchain regular-bounty surface.

## Selection consequence

No official HackenProof launch qualified. The run selected exactly one unworked regular bounty from the durable rotation: Mellow Core Vaults on Sherlock. No audit competition was audited and no external action was taken.

