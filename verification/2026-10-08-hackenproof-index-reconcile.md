# HackenProof official index reconciliation — 2026-10-08

The [daily digest](../digests/2026-10-08.md) recorded 15/18 successful source fetches. `broad-hackenproof-programs`, `hackenproof-programs`, and `hackenproof-audits` timed out, so those feeds remain **degraded**, not quiet.

A bounded direct read of the official [program index](https://hackenproof.com/programs) loaded current listings; the official [audit-program index](https://hackenproof.com/audit-programs/) loaded current live and finished contests. `https://hackenproof.com/audits` returned 404 and is not the current audit-index route. At this read, the audit index labeled Digital Oro International and EverValue as live. No target's detailed scope, participant requirements, source pin, or payout eligibility was inferred from an index card.

This restores **listing awareness for this selection pass only**. It does not prove the scheduled scanner succeeded or repair its three failed sources. If maintaining the radar, inspect and update the configured audit-index route, then rerun the source fetches and require a successful terminal digest before marking coverage healthy.
