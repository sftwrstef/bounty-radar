# Official source reconciliation — 2026-09-29

Verified both official HackenProof indexes independently after the local scan:

- Bounties: <https://hackenproof.com/programs>
- Audits: <https://hackenproof.com/audit-programs>

## Result

- No bounty or audit launched after the prior automation run at
  `2026-09-28T13:00:50.453Z`.
- `Ult: Trade Stocks & Crypto` remains the newest `NEW / LIVE` bounty. It
  started and was last updated on 2026-09-28, now shows 36 submissions, and
  remains capped at $20,000. It was already recorded on 2026-09-28.
- `RAIN-USDR Smart Contract Audit Contest (Sept 2026)` remains the only `LIVE`
  audit. It started on 2026-09-14, ends on 2026-10-01, now shows 659
  submissions, and remains capped at $14,000. It was already recorded.
- Active-shortlist `Arcadia Finance Smart Contracts` remains at 131
  submissions and a $25,000 maximum. `Cetus Web` rose from 163 to 166
  submissions and remains capped at $10,000. No verified shortlist
  scope/reward change or queue reorder was warranted.
- No `record-source` backfill was needed.

## Coverage

The scanner returned terminal JSON and wrote `digests/2026-09-29.md`, but local
coverage remains degraded at 15/18 because `broad-hackenproof-programs`,
`hackenproof-programs`, and `hackenproof-audits` each exceeded their 58-second
browser timeout. This official-page reconciliation restores current listing
visibility but does not erase the local source failures.

The Chainlink CCIP v2 USDC monitor separately returned `coverage_ok: true`,
`new_or_upgraded: 0`, 36 known matches, and 18 pending onchain confirmations.

## Post-digest Wormhole official-program update

The live Wormhole Immunefi payload was updated at
`2026-09-29T14:53:52.773Z`, after this digest's `13:00:30Z` generation time.
Current official pages:

- <https://immunefi.com/bug-bounty/wormhole/information/>
- <https://immunefi.com/bug-bounty/wormhole/scope/>

Compared with the official page cached on 2026-09-28 (`Last Updated 12 August
2026`), the active/user-visible Low cap changed from `$2,000` to `$1,000` for
both Blockchain/DLT and Smart Contract, and the prohibited-testing language
was migrated/expanded. The program still has 12 assets and 36 impacts.
Critical (`$100,000-$1,000,000`), High (`$10,000-$100,000`), and Medium
(`$2,000-$10,000`) are unchanged. No new asset or favorable Medium-or-higher
scope expansion was found. `payToSubmitFeeUsdc` remains `null`.

The only Wormhole repository commit in the radar window is
`d537d528343201ec6abae024e7b9505df3675ddf`; an executable complete-diff
assertion proves it changes only the Discord link in
`.github/ISSUE_TEMPLATE/config.yml` (`+1/-1`). It is not released or deployed
runtime code. See
`audit_targets/wormhole-current-delta-immunefi-20260929/HUNT_STATUS.md`.

## Continued-run Hyperlane collision revalidation

The Immunefi-linked Hyperlane Explorer commit
`d4c0ac845eceb39a0fadb6c960f94523b7576a64` was already identified in the
2026-09-28 reconciliation as a public fix for Immunefi `#92002`. Current
official scope remains unchanged at 222 assets: 220 exact contract addresses
plus only `https://www.hyperlane.xyz/` and `https://www.usenexus.org/`.
`https://explorer.hyperlane.xyz` is not a formal asset.

PR `#364` publicly discloses the complete issue as a crafted `?chains=`
duplicate-domain override causing a persistent but self-recoverable
browser-profile crash, with no funds, server-side effect, or cross-user impact;
it records the report as informational. The exact runnable gate
`node analysis/verify_scope_collision.mjs` passed from
`audit_targets/hyperlane-domainid-consumer-immunefi-20260929`, also confirming
that the scoped warp UI has no equivalent remote `chains` query writer and the
current shared SDK rejects duplicate domains before provider execution.

Terminal result: `KILL`, best hypothesis `1/5`, severity none/informational.
No fresh Medium-or-higher scope or code path survives.

## 21:46 EDT late refresh

The end-of-day refresh ran with external alerts disabled:

```text
./.venv/bin/python -B -u -m bounty_radar scan --progress --json --no-alerts
```

The scanner completed at `2026-09-30T01:46:10.781084Z` (still September 29
in `America/New_York`). It scanned 18 repositories and returned 18 source
results. Coverage remained degraded at `15/18`: the same three HackenProof
browser lanes timed out. The generator therefore wrote
`digests/2026-09-30.md` under its UTC date even though this reconciliation is
for the September 29 local run.

### Genuine official scope delta: Walt.io

The current official HackerOne program at <https://hackerone.com/walt_io>
shows three asset additions on September 29:

- `walt.io`, added at `07:50 UTC`, in scope and bounty-eligible, maximum Low;
- `http://t.me/wallet`, added at `07:52 UTC`, in scope and bounty-eligible,
  maximum Critical; and
- `http://t.me/walt`, added at `07:59 UTC`, in scope and bounty-eligible,
  maximum Critical.

The current table has 13 rows, 10 of them in scope. The policy update at
`08:19 UTC` is a Wallet-on-Telegram -> Walt branding/test-link migration; the
official policy diff does not change the reward table. Current ranges remain
Low `$100-$200`, Medium `$200-$500`, High `$500-$3,000`, Critical
`$3,000-$100,000`, with the program's separate `Extreme` label covering
`$30,000-$100,000` impact examples.

This is a real `MATERIAL_SCOPE_DELTA`. HackerOne's current platform Code of
Conduct permits and encourages responsible AI-assisted reconnaissance,
discovery, PoC development, and report improvement, and recognizes
human-operated Hackbots as bounty-eligible. It also says that programs may add
their own rules and that Hackbots must comply with the applicable program
policy. Walt's narrower current policy still expressly states that AI agents
may not search for vulnerabilities. The September 29 policy revision retained
that sentence unchanged while updating the Walt branding and Telegram test
link, so it cannot be treated as removed or superseded merely from HackerOne's
platform-wide permission. Walt remains blocked for Vesper's autonomous search
unless the program removes or clarifies that rule. The program also describes
itself as private and requires confidentiality. No testing was performed.

### Other launch and change signals

- The official Autoliv Intigriti page confirms that Autoliv VDP is a
  vulnerability-disclosure program with no promised or guaranteed monetary
  rewards. Its September 29 activity is not a payout-eligible fresh target.
- Every late `scope_changed` item emitted from the BountyHunters HackerOne,
  Bugcrowd, and Intigriti feeds was relative-age text drift (for example,
  `5 days ago` -> `6 days ago`). The stored previous/current snapshots retain
  the same asset counts and reward values; none is an authoritative material
  scope delta.
- The Optimism repository produced a new
  `op-deployer/v0.9.0-dev-test.1` release signal. The tag is explicitly a
  development-test release and no official program/deployment mapping pins it
  as new live bounty scope, so it remains a code-change signal rather than a
  scope expansion.
- The current Immunefi listing lanes returned 11 items each with zero new
  signals. No additional official Immunefi program launch or asset expansion
  was detected after the Wormhole reward-only change recorded above.

### Chainlink deployment-directory delta pending confirmation

The official CCIP directory monitor first observed 26 new USDC route rows
since the earlier 36-lane baseline: six bidirectional Ethereum-mainnet lanes
for 0G, BOB, Monad, NeoX, Ronin, and Wemix; six bidirectional Unichain lanes
for Avalanche, Arbitrum, Base, Optimism, Ethereum mainnet, and Polygon; and the
bidirectional Arbitrum/Hyperliquid lane. The state now contains 62 directory
lanes and 44 pending onchain reopen checks.

An immediate idempotence run returned `coverage_ok: true`,
`new_or_upgraded: 0`, and `pending_onchain_confirmations: 44`. These are
official directory/deployment signals, but they are not yet promoted as a
confirmed live bounty-scope expansion because the monitor's onchain
confirmation gate remains pending. The next bounded action is to resolve those
checks before selecting any one Chainlink lane for research.

### Fresh official-index check

The independently opened HackenProof indexes still show no September 29
launch. `Ult: Trade Stocks & Crypto` remains the newest live bounty (started
September 28; now 51 submissions; `$20,000` cap). `RAIN-USDR` remains the only
live audit (ends October 1; now 673 submissions; `$14,000` cap).

Disposition: `MATERIAL_SCOPE_DELTA` for Walt.io, but Vesper autonomous research
is program-rule-blocked under Walt's still-published AI-agent restriction;
this is not a HackerOne-wide AI prohibition. `DEPLOYMENT_DELTA_PENDING` for the
26 Chainlink directory routes. No newly confirmed, autonomous,
payout-eligible Medium-or-higher target is ready for selection from this late
refresh.
