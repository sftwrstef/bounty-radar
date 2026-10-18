# Daily fresh-scope coverage reconciliation — 2026-10-10

Reviewed 2026-10-10 09:40 EDT. This is the bounded coverage gate for the scheduled daily hunt, not a claim of complete catalog history.

## Coverage health

- Radar health is **degraded at 15/18**. `broad-hackenproof-programs`, `hackenproof-programs`, and `hackenproof-audits` each exceeded the 58-second browser limit in the 2026-10-10 13:05 UTC run. Their empty results are not quiet-day evidence.
- A direct read of the official [HackenProof standing-program index](https://hackenproof.com/programs) still showed **Ult: Trade Stocks & Crypto** as the newest visible live launch, started 2026-09-28, now with 84 submissions and a USD 20,000 maximum. No newer standing launch was visible.
- A direct read of the official [HackenProof audit index](https://hackenproof.com/audit-programs) showed **All 101**. Its top live rows remain Digital Oro International SCA DualDefense (2026-10-05 through 2026-10-26, 20 submissions, USD 3,000 maximum) and EverValue SCA DualDefense (2026-10-02 through 2026-10-16, 52 submissions, USD 2,500 maximum). No new audit row appeared above them.
- Database changes for Revert and DAWN were relative-age/countdown metadata already reconciled in earlier runs. The HackerOne, Bugcrowd, and Intigriti rows were primarily changing `days ago` labels or first observations in a refreshed feed, not authoritative asset deltas.
- The apparent Decadis AG `source_launch` was **new-to-feed, not a new program**: the official [Bugcrowd engagement](https://bugcrowd.com/engagements/decadisag) says it started 2020-07-28 and is an ongoing Atlassian Marketplace bounty. Its exact newly changed scope field is `UNKNOWN` because no authoritative prior snapshot was retained. It has no verified local source map and did not beat the surviving Leather candidate.

## Disposition and route

- `DEGRADED_COVERAGE`; `NO_VERIFIED_GENUINE_FRESH_DELTA` from the bounded official reconciliation. This does not establish that every unreadable source was unchanged.
- The run followed the **degraded-coverage / queued-target branch**. The queued target could proceed because current official scope, reward, published version, and local source/package identity were independently reverified.
- Selected target: Leather browser extension v6.114.0, finding `LEATHER-P2A-001`. Current official evidence still lists the browser extension and monorepo, Medium impact 6297 at USD 1,000–2,000, and Chrome Web Store version 6.114.0 updated 2026-10-06.

No login, report, submission, fee, KYC action, enrollment, target contact, public-chain transaction, real-fund test, signature, or disclosure occurred.
