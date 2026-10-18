# Official fresh-scope reconciliation — 2026-09-23

## Coverage health

- The 13:01 UTC radar run completed 15 of 18 configured source fetches.
- `broad-hackenproof-programs`, `hackenproof-programs`, and
  `hackenproof-audits` each exceeded the 58-second browser timeout. This is
  degraded collector coverage, not evidence that HackenProof had no changes.
- Independent reads of both official HackenProof indexes restored visibility
  for this decision. They do not repair the collectors or establish an
  exhaustive historical comparison of every program page.
- Telegram delivery was healthy at the time of reconciliation: 165 total
  outbox rows, zero pending, and zero with a recorded delivery error.

## Same-day source deltas

The broad-platform alerts do not establish a new paid source target:

- Most `scope_changed` rows were relative-age text churn, such as “7 days ago”
  becoming “8 days ago,” rather than asset, reward, or policy changes.
- Candid, ADAC, Intel, GULP, Challenge 0926, and Posten Bring are unpaid
  vulnerability-disclosure programs or challenges. They do not satisfy the
  paid-target gate.
- Vercel, Common Codes, Blind Trust, PowerDNS, Kiteworks, and Tenbin were
  launched or changed before this run. PowerDNS and Common Codes already have
  local dossiers. Tenbin's alert contains no source or reward delta and its
  existing finding number 16 has already been submitted.
- The database's only item first observed on September 23 was the Bugcrowd
  `VR Public Managed Bug Bounty Engagement`. It transitioned from private to
  public at 09:47 UTC, but the program started October 21, 2025. Its sole
  target is the NodeJS ticketing site `www.vr.fi`; it is not a same-day launch
  or a source-backed Web3 scope.
- Sherlock's newest public bounty remains Babylon number 400, already covered
  by the pinned v4.4.0 local dossiers. No public active contest was identified.
  Code4rena reports that it is winding down and currently lists zero bounties.

## Immunefi official reconciliation

The official directory's only September 23 update is RootstockLabs:

- The current scope contains 20 assets, all at revision zero. The newest asset
  remains RIF Token, added September 3; there is no September 23 asset,
  repository, source-version, or deployment addition.
- The scope still contains 53 impacts and the preserved reward table.
- One critical Blockchain/DLT impact changed from general “significant” direct
  non-recoverable loss to direct non-recoverable loss of at least USD 100,000.
  This narrows the qualifying proof threshold; it does not add an attack
  surface.
- Existing RskJ, PowHSM, Flyover, liquidity-bridge, and RIF lanes already cover
  the relevant Rootstock surfaces. The wording change does not create a fresh
  root cause or reopen a closed lane.

Official sources:

- <https://immunefi.com/bug-bounty/>
- <https://immunefi.com/bug-bounty/rootstocklabs/scope/>
- <https://immunefi.com/bug-bounty/rootstocklabs/information/>

## HackenProof official reconciliation

- The standing index contains 324 programs. Hotcoin Web & Mobile remains the
  newest launch, started and last updated September 14. Its submission count
  increased, but no scope launch occurred today.
- The audit index contains 99 programs. RAIN-USDR remains the sole live audit,
  running September 14 through October 1 with a USD 14,000 pool. Local report
  `RAINUSDR-1512` already covers that target and blocks reselection.
- Treehouse reduced rewards while retaining the same 68-address V2 scope.
  Critical is now USD 25,000–50,000, High USD 5,000–25,000, Medium
  USD 500–5,000, and Low USD 250–500. The live V3/FastlaneV2 contracts remain
  absent from the eligible scope, and the existing V2 roots collide with prior
  material.
- ADI Foundation Smart Contracts is marked updated September 23, but its
  assets, rewards, fee, exclusions, and `zkos-v0.29.11` source pin are
  unchanged. The observed current runtime is v0.30.2, so exact eligible-source
  parity remains contradicted.
- HTX changed to ended status; this is not a new hunting surface.

Official sources:

- <https://hackenproof.com/programs>
- <https://hackenproof.com/audit-programs>
- <https://hackenproof.com/programs/hotcoin-web-and-mobile>
- <https://hackenproof.com/audit-programs/rain-usdr-smart-contract-audit-contest-sept-2026>
- <https://hackenproof.com/programs/treehouse-smart-contracts>
- <https://hackenproof.com/programs/adi-foundation-smart-contracts>

## Selection decision at 09:46 EDT

**NO SELECT at the morning reconciliation.** No candidate then visible had
affirmative evidence for a new paid, source/runtime-backed asset plus a
distinct public attacker path and a rubric-eligible impact outside the existing
collision set.

The next eligible trigger is one of the following:

1. a newly added or revised source asset with an exact commit or deployed
   runtime pin;
2. a newly eligible public attacker role or materially expanded impact;
3. an exclusion removal that makes a previously parked production path
   eligible; or
4. a fresh launch whose root cause, trigger, affected asset, beneficiary,
   impact, and remediation do not collide with a local or public lane.

No report, fee, contact, login, production transaction, or cleanup was
performed during that reconciliation.

## Post-reconciliation release delta and selected target

Celestia Node `v0.33.2` was published at `2026-09-23T11:05:17Z`, after the
morning reconciliation and four minutes after the current Vesper handoff. It
was therefore the one selected fresh regular-bounty target for this run:

- exact tag commit: `d86267081909a04b31a8becde971b19442a931bc`;
- official program: live Celestia HackenProof program, with `celestia-node` and
  the pinned `nmt` dependency explicitly in scope;
- economics: $10 fee, up to $10,000 Critical / $1,000 High / $100 Medium;
- release delta: SHREX cooldown deadlock fix, namespace-data row cap, NMT
  v0.24.5 verifier overflow fix, IPv6 support, and dependency upgrades.

The bounded local diagnostic confirmed that the row cap does not cap shares or
bytes within each row. The exact gap is already stated in the public review of
PR #5229, and no crash or accepted false protocol state was reproduced. The
target therefore closed **KILL exact lane at 1/5 / ROTATE**. See
[`HUNT_STATUS.md`](../../audit_targets/celestia-node-v0332-shrex-nmt-hackenproof-20260923/HUNT_STATUS.md).

Official sources:

- <https://github.com/celestiaorg/celestia-node/releases/tag/v0.33.2>
- <https://github.com/celestiaorg/celestia-node/pull/5229>
- <https://hackenproof.com/programs/celestia>
