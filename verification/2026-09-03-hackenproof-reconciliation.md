# HackenProof official-index reconciliation — 2026-09-03

Checked at `2026-09-03T09:35:11-04:00` using clean, read-only browser
renders of the official standing-program and audit-program indexes.

## Coverage health

- The saved radar digest is degraded at `15/18`: all three HackenProof browser
  sources exceeded their 58-second wall timeout.
- Independent clean renders succeeded for both official indexes. This repairs
  selection visibility for this run, but it does not relabel the saved digest
  as healthy.
- The standing-program index displayed `322 Results`.
- The audit-program index displayed two live competitions: Alberich Token SC
  DualDefense (`2026-09-01` through `2026-09-08`) and Zendex SC DualDefense
  (`2026-08-18` through `2026-09-09`). Both are contests, not regular bounties.
- SQLite recorded ten ordinary source-item changes, five source alerts, and
  zero pending Telegram rows for 3 September. The non-HackenProof rows were
  Web2/VDP or generic program-page churn, not fresh regular smart-contract
  bounty scope.

## Genuine regular-bounty delta

The standing index confirms **Hinkal Bug Bounty** as `NEW LIVE`, started and
last updated on `2026-09-03`, with 16 submissions, seven visible hackers, zero
paid rewards, and a `$5,000-$10,000` Critical-only range. The exact official
scope is `Hinkal-Protocol/Hinkal-Contracts-Circuits`.

Hinkal was not selected for depth today. The source repository pinned at
`61b6839aa80fc0c33bfdcde0323753c83cb2ce67` contains no tests, deployment
scripts, build manifest, deployed-address list, release tags, or runtime/source
attestation. The official program page likewise names no deployed address or
runtime version. That prevents the required live reachability and
source/runtime parity pin. See the local preflight note.

## Selected target comparison

RootstockLabs added the live RIF Token at
`0x2aCc95758f8b5F583470bA265Eb685a8f45fC9D5` to smart-contract scope on
`2026-09-03`. Unlike Hinkal, its deployed bytecode, verified source, exact
legacy repository, current state, published audit, and live value can all be
reconciled. Its Critical smart-contract reward is 10% of directly affected
funds, `$10,000-$100,000`, and the public program payload reports
`isPayToSubmit: false`.

Rootstock/RIF was therefore the one selected target for the bounded hunt.

