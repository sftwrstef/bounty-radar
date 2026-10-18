# HackenProof official-index reconciliation — 2026-08-27

The local daily scan completed `15/18` source fetches. These three feeds were
degraded because Playwright's matching `chromium_headless_shell-1228`
executable is absent:

- `broad-hackenproof-programs`
- `hackenproof-programs`
- `hackenproof-audits`

A repair attempt with the radar's own Playwright `1.61.0` environment failed
with `ENOSPC`; the data volume had only `121 MiB` free. No user data or caches
were deleted.

Independent read-only retrieval of the official indexes on 2026-08-27 returned
the live standing-program page and audit-program page. The standing index
reported 321 programs. Cronos Web was the only visible same-day regular-program
update (`Last updated: 27 Aug 2026`) and its current scope lists
`https://moonlander.trade` as a Critical-eligible Web target. The audit index
showed Zendex as the only live entry; it is a DualDefense competition, not a
regular bounty.

Today's database deltas were also reconciled. The HackerOne, Bugcrowd, and most
Intigriti `scope_changed` rows were age/countdown churn. The five new Bugcrowd
items were ordinary Web2 listings, not Web3 smart-contract programs. No
genuinely new Immunefi or Cantina regular-bounty scope delta survived.

Coverage remains **degraded but independently reconciled**, not quiet. The
scanner itself should be repaired only after at least roughly 1 GiB of safe
free disk is available.

