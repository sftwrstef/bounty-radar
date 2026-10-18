# Official fresh-scope reconciliation — 2026-09-26

Reviewed on 2026-09-26 (America/New_York).

## Coverage health

- The saved radar completed 15 of 18 sources. `broad-hackenproof-programs`, `hackenproof-programs`, and `hackenproof-audits` each exceeded the 58-second browser-fetch limit. Coverage therefore remains degraded, not quiet.
- Direct official API reads restored decision visibility. The standing index returned 324 programs; the audit index returned 99 programs.
- The source-change database recorded six same-day `scope_changed` rows: Kaltura, VR Group, Blind Trust, Intigriti Challenge 0926, ADAC VDP, and Randstad GULP. They are Web2, VDP, or challenge listings and do not establish a fresh paid onchain target.
- Telegram delivery was healthy: 174 total rows, zero pending, and zero errored.

Official sources:

- <https://hackenproof.com/programs>
- <https://hackenproof.com/programs-api/programs?not_audits=true&page=1&per_page=12&order_by%5Bupdated_at%5D=desc>
- <https://hackenproof.com/audit-programs>
- <https://hackenproof.com/programs-api/audits?page=1&per_page=20>

## Fresh-scope subtraction

- No standing program shows a 2026-09-26 update. Celestia is the newest active standing update at 2026-09-25; NoOnes is completed.
- The remaining leading smart-contract updates are dated 2026-09-24 and already have local dossiers: Sui Protocol, 1inch Aqua, Hyperbridge Protocol, STBL Smart Contracts, Ember EVM, Ember Vaults, and NEAR Intents SDK.
- RAIN-USDR remains the only active audit program, ending 2026-10-01. Existing submission `RAINUSDR-1512` blocks reselection.
- Celestia's current page still lists the same ten in-scope repositories plus the same `celestia-node` exclusions. Current economics are a $10,000 Critical maximum, $1,000 High maximum, $100 Medium maximum, 150 reputation, KYC, PoC, and a $5 submission fee.

## Selected target

Exactly one regular-bounty target was selected: Celestia `celestia-app v10.3.0-corto`, exact tag `861c71c845e155ab8bdbe49a1d1453bdb4a3ccd1`, published 2026-09-25T20:07:55Z.

It beat the queue because it is the newest source-backed active standing-program delta, changes authenticated Fibre upload/storage behavior, and retains a public client input surface. The already-worked ZIP-215 transition is excluded as a public collision. The bounded candidate is the distinct `UploadShard` change that skips shard verification only after the `(commitment, full signed payment-promise hash)` key is already present in storage.

Preflight is not a payout pass: the selected tag is a Corto prerelease created from `rachid/fibre-performance-main`; no Mainnet or Mocha deployment parity is established. The mechanics-first probe is therefore capped at source and local focused tests.

## Verification and disposition

The focused source/test probe closed the candidate. The server validates the full signed payment promise before the dedupe check; the dedupe key and stored key are the same `(commitment, full signed promise hash)` domain; and only a verified shard can reach `Store.Put`. An invalid first delivery neither creates a marker nor receives a validator signature. Corrupt retries skip proof work only after the exact verified payload already exists and cannot replace it.

Exact commands from the pinned source root:

```text
go test ./fibre -run '^TestServerUploadShard(Duplicate|ConcurrentDuplicates)$' -count=1 -v
go test ./fibre -run '^TestServerUploadShard$' -count=1 -v
```

Results: duplicate/concurrency tests passed 2/2; the general upload test passed all 12 subtests, including invalid promise, assignment, proof, size, and shape rejections. Same-state loss, unavailable data, authority change, attacker proceeds, and profit are zero; the attacker only bears request costs.

Terminal daily verdict: **KILL exact `UploadShard` invalid-first dedupe-poisoning lane / broader Celestia v10.3.0-corto remains PARK / WATCH.** Strict payout score 1/5. Reopen only on a supported deployment whose implementation consumes a dedupe key before verification, checks a weaker key than it stores, or signs while serving bytes not verified under that exact promise identity, with material same-state harm.

No report, fee, submission, login, signature, public-chain write, project contact, disclosure, or cleanup was performed.
