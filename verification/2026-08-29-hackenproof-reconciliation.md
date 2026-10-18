# HackenProof reconciliation — 2026-08-29

## Coverage disposition

Today's generated digest is **degraded at 15/18**, not quiet. These three
configured browser sources timed out after 58 seconds:

- `broad-hackenproof-programs`
- `hackenproof-audits`
- `hackenproof-programs`

The generic Playwright wrapper is also unwired in this workspace
(`playwright-cli: command not found`). The radar's pinned Playwright runtime did
complete one direct official `/programs` fetch (317,341 HTML bytes and 20
visible program links), but the immediate clean retry received Cloudflare HTTP
429. Current browser health is therefore intermittent and the digest remains
historically incomplete even though the official indexes were reconciled
read-only through independently fetched current pages.

## Official-index reconciliation

- The official regular-program index exposes 321 results. No 29 August regular
  Web3 program launch, smart-contract asset addition, scope expansion,
  deployment change, or reward increase was visible. The newest visible regular
  updates were earlier (including Cronos Web on 27 August).
- The official audit index has one live competition, Zendex SC DualDefense,
  ending 9 September. This is an audit competition, not the one regular-bounty
  target required by this run.
- The non-HackenProof database deltas were Web2/VDP listings plus Dovecot on
  YesWeHack. They did not add a fresh regular smart-contract bounty lane.

## Collision-corrected selection

Phemex was excluded because the existing `vesper-brain` intake already closed
it at 2/5 (source/authentication boundary). BingX and CEX.IO were lower-value,
high-collision exchange-web lanes. Previously worked smart-contract families
were removed through the worked-target registry, directory manifest, collision
ledger, and target-local status files.

The sole selected target was Monday Trade Web. Its official page was live,
publicly reachable, and scoped exactly to `https://app.monday.trade/`; it was
absent from the local registries and brain. Its current program metrics were 253
submissions, 141 hackers, $400 paid, Critical $1,500–$3,000, and High
$500–$1,500. The page showed no public submission fee. The resulting production
authorization probe closed the lane at **KILL / ROTATE — 2/5**; see
`audit_targets/monday-trade-web-hackenproof-20260829/HUNT_STATUS.md`.

## Repair trigger

Restore a callable generic Playwright CLI and make the radar's pinned browser
fetch tolerate or report official-index HTTP 429 distinctly. A later successful
repair does not retroactively make this 15/18 digest complete.
