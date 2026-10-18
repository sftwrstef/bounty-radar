# Official coverage reconciliation — 2026-10-06

## Coverage health

- Bounded local scan completed at `2026-10-06T13:33:19Z` with `15/18` source fetches healthy.
- Degraded sources: `broad-hackenproof-programs`, `hackenproof-programs`, and `hackenproof-audits` (local Playwright unavailable in the automation environment).
- This is degraded coverage, not a no-delta result.

## Official HackenProof reconciliation

- Official standing-program index: `324 Results`; newest regular listing remains **Ult: Trade Stocks & Crypto**, started `2026-09-28`. No new standing HackenProof program was established today.
- Official audit index: `101 Results`; the new first-party listing is **Digital Oro International SCA DualDefense Audit**.
- Digital Oro official page: live `2026-10-05` through `2026-10-26`; Critical-only; `$0-$3,000` pool; 50 reputation points, KYC, PoC, and invite-only participation; public scoped repository `hackenproof-public/sweepstakes`; 12 submissions at review time.
- The program requires findings to apply to the protocol as currently deployed. The repository's generated Sepolia manifest was therefore checked read-only before promotion.

Official URLs:

- <https://hackenproof.com/programs>
- <https://hackenproof.com/audit-programs>
- <https://hackenproof.com/audit-programs/digital-oro-international-sca-dualdefense-audit>

## Other scanner deltas

- DAWN's local `scope_changed` event was only the relative text transition `today` to `1 day ago`; its official Immunefi page remains `Last Updated 28 September 2026`. The October 5 DAWN dossier already reviewed and parked the actual scoped surfaces.
- Walt.io, the four Bugcrowd rows, and the three Intigriti rows changed only relative-age text (`N days ago` to `N+1 days ago`). They are not genuine program, asset, reward, or scope deltas.
- The three Intigriti rows included two unpaid VDPs; none displaced the verified fresh Solidity audit for this run.

## Routing

Branch: **degraded coverage / fresh-delta**. Digital Oro was selected because it was the only verified genuine fresh program/source delta with Critical eligibility, public Solidity source, a runnable local suite, and a published deployment manifest. DAWN was already exhausted for its current scope, ADI was closed on October 5, and Golem remains held behind its existing scope question.
