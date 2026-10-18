# HackenProof reconciliation — 2026-08-31

## Coverage health

The saved digest at `2026-08-31T13:01:53Z` completed `15/18` sources. The
three HackenProof browser sources failed because Playwright headless-shell
revision `1228` was missing. The binary and FFmpeg were installed successfully,
but a subsequent `hackenproof-programs` warm render still exceeded the
65-second wall-clock timeout. The saved digest is therefore correctly retained
as degraded rather than rewritten as a clean run.

Independent official-page rendering established:

* [standing programs](https://hackenproof.com/programs): 321 results;
* [audit programs](https://hackenproof.com/audit-programs): Zendex is the only
  visible live audit and is a time-boxed competition, not a regular bounty;
* [Enkrypt Wallet](https://hackenproof.com/programs/enkrypt-wallet): live,
  Chrome extension ID `kkpllkodjeloidieedojogacfhpaihoh` and the
  `enkryptcom/enKrypt` repository explicitly in scope;
* [Chainstack](https://hackenproof.com/programs/chainstack): last updated
  2026-08-31.

The local database recorded 25 source-item changes: 17 Bugcrowd, 3 HackerOne,
3 Intigriti, 1 YesWeHack, and 1 broad index item. It emitted five source alerts
and had zero pending Telegram outbox rows. These were Web2/VDP/competition
signals, not a fresh regular smart-contract launch.

## Genuine standing-program delta

Chainstack is the only official same-day standing-program update. Relative to
the August 17 local scope snapshot, the page newly makes
`*.prod-networks.chainstack.com` a High infrastructure target and expands the
Marketplace/add-on entitlement, billing, credential, and metadata language.
The scope description also mentions `*.prod-networks.chainstack.net`, while the
formal target table lists only the `.com` wildcard; the narrower target table
must control until clarified.

This delta was not selected. Chainstack already has a completed two-account
REST/MCP/RPC authorization matrix and an exact reopen condition for a new
public endpoint that accepts cross-tenant IDs without organization scoping.
Its current page shows 519 submissions, 256 hackers, and a `$2,000` maximum.
Differentiating the new infrastructure surface would require authenticated
testing, which this automation does not perform.

## Selected regular-bounty target

Enkrypt Wallet was the best untouched public/local target after collision
subtraction. Its current page shows 305 submissions, 132 hackers, `$1,500`
paid, an 80-reputation/PoC gate, and a `$3,000` maximum. No public fee is shown.

The exact Chrome artifact remains version `2.18.0`, 6,985,600 bytes, SHA-256
`2f32f81d619f95106ccbd5a5bef663cf2e364e94f401cf853290522e19a5592d`.
The dereferenced `v2.18.0` tag and current `main` both resolve to
`b9ba80254f96f98ee5cc87f8c614a4f67c1a85db`.

Terminal result: **KILL / ROTATE — strict 2/5**. Public dispatch and live scope
pass. All examined EVM/Bitcoin signing routes preserve browser-derived
tab/domain identity and require a fresh background-created confirmation whose
request/account/network/payload the page cannot replace. Same-state victim
loss, protocol deficit, attacker proceeds, and attacker profit are all zero.
