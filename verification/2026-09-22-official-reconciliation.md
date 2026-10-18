# Official fresh-scope reconciliation — 2026-09-22

## Coverage health

- The saved radar digest completed 15 of 18 sources.
- `hackenproof-programs`, `hackenproof-programs-page-2`, and
  `hackenproof-audit-programs` each timed out after 58 seconds. This run treats
  those feeds as degraded coverage, not as evidence of no change.
- Independent reads of the official HackenProof indexes showed 324 standing
  programs and one live audit program, RAIN-USDR. RAIN-USDR was excluded from
  selection because submission `RAINUSDR-1512` is already pending.
- The database delta since the previous automation run contained 21 broad,
  Web2, VDP, challenge, or tracker changes and no new regular smart-contract
  target. Telegram delivery was healthy at 159 total, zero pending, zero errors.

## Genuine fresh scope

The strongest same-day regular-bounty delta was the ZKsync OS Immunefi update:

- Official last-updated date: 22 September 2026.
- Maximum bounty: USD 100,000; Smart Contract Critical USD 50,000–100,000,
  High USD 10,000–25,000, Medium USD 1,000–5,000.
- The scope now lists 232 assets, including the production ZKsync OS execution
  surface and the L1 protocol contracts. Listed impacts include direct theft,
  insolvency, permanent fund freeze, permanent priority-queue stoppage, and
  proof-system underconstraints.
- Official source resource: `matter-labs/era-contracts`; exact scoped checkout
  pinned locally at `e8e5d893b74363f9ef47bb139c06e78663ad17ed`.
- Only the production feature set is eligible. Ethereum-STF/test-only behavior
  and findings requiring Gateway as the active settlement layer are excluded.
- The program requires a PoC and KYC. No fee, submission, login, signature,
  transaction, project contact, or public testing was performed.

## Selection and bounded work

Exactly one target was selected: ZKsync OS Smart Contracts. It beat the queue
because it is the only verified same-day on-chain scope expansion, has exact
source, public L1 entrypoints, material listed impacts, and lower collision than
the repeatedly worked Optimism, 0x, Aera, Zerion, ADI, and RAIN lanes.

The target was already claimed by another active Vesper task during this run.
To avoid conflicting edits or duplicate testing, this automation preserved its
target-local dossier and limited itself to official-scope, repository-pin, and
read-only deployment preflight. The current bounded lanes are:

1. permissionless legacy `bridgedOut` population;
2. atomic settlement versus timeout/refund identity;
3. priority-operation upgrade lower-bound initialization; and
4. failed-transfer asset/beneficiary identity binding.

No lane has yet produced an end-to-end state divergence, production-executable
same-state control, material incremental loss, or attacker economics. Therefore
there is no serious candidate and no report/control matrix to promote today.

## Disposition

**PARK / CONTINUE IN THE ACTIVE TARGET TASK — UNSCORED.** The strongest current
dismissals are non-production/Gateway-only reachability, authenticated-state
derivation, or complete semantic binding. Duplicate risk is medium-high because
the repository and prior audits are public, but no exact complete-composition
collision has yet been established. Reopen/promote only when one bounded lane
produces a public production path plus an exact exploit/control final-state
delta and survives the audit/known-issue comparison.

## Evening fresh-scope coverage check — 2026-09-22

This is a coverage statement, not a finding or a claim that every program was
audited. The saved 18:15 UTC radar run fetched 15/18 configured sources; all
three HackenProof browser feeds timed out. Its two Immunefi feeds fetched index
links and summaries from only the directory's first ten visible programs out
of 172 public listings, not every program's asset, impact, or exclusion page.
CoW was absent from those ten. Their success cannot establish complete
scope-delta coverage.

- Current official [Immunefi program listings](https://immunefi.com/bug-bounty/)
  showed three September 22 updates needing individual checks: CoW Protocol,
  ZKsync OS, and Enzyme Blue. CoW's [scope](https://immunefi.com/bug-bounty/cowprotocol/scope/)
  added eight Web & App assets at 16:10 UTC; its new signing surface was
  independently explored in
  `audit_targets/cow-web-signing-immunefi-20260922/HUNT_STATUS.md` and remains
  parked without a promoted finding. ZKsync OS added the pinned L1 contracts
  surface; `audit_targets/zksync-os-smart-contracts-sep22-immunefi-20260922/HUNT_STATUS.md`
  records its bounded closeout without a candidate. Enzyme Blue's
  [scope](https://immunefi.com/bug-bounty/enzymefinance/scope/) still has 304
  assets, none added in September 2026, and its selected `dev` source remains
  `da3b870f4d9619e082cb599b172b8b108a62298d`, matching the September 14
  dossier. No payout-relevant Enzyme delta was identified; the precise
  editorial reason for the updated date is not established without an archived
  earlier page. The September 21 0x and Zerion updates had no newly added
  September asset rows; their current paths are recorded in
  `audit_targets/0x-sep21-deployed-delta-immunefi-20260921/HUNT_STATUS.md` and
  `audit_targets/zerion-extension-stale-send-immunefi-20260922/HUNT_STATUS.md`.
- Independent current reads of the official HackenProof
  [bounty index](https://hackenproof.com/programs) and
  [audit index](https://hackenproof.com/audit-programs) found Hotcoin still the
  newest listed bounty and RAIN-USDR the sole live audit. Both were already
  recorded; RAIN-USDR report `RAINUSDR-1512` was already submitted. This
  restores visibility to the newest index cohorts, but does not repair the
  three collector failures or compare every older program's scope page.
- The current [Sherlock bug-bounty index](https://audits.sherlock.xyz/bug-bounties)
  lists Babylon (launched September 21) as its most recent bounty. The exact
  v4.4.0 scope has two local dossiers, including
  `audit_targets/babylon-v440-sherlock-400-20260921/HUNT_STATUS.md`, which
  source-killed the injected-checkpoint hypothesis. Sherlock's
  [contest index](https://audits.sherlock.xyz/contests) showed zero active
  contests at this check.

**Coverage conclusion:** no unreviewed launch or substantive scope expansion
was found among these current newest listings, but an exhaustive all-program
scope-page comparison was not performed. The next radar improvement is a
per-program asset/impact/exclusion snapshot and a repaired HackenProof browser
collector; until then, index success alone must not be reported as complete
fresh-scope coverage. No report, fee, contact, production transaction, or
cleanup was performed in this reconciliation.
