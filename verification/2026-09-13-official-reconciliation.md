# 2026-09-13 official source reconciliation

Reviewed at `2026-09-13T15:01:29Z`.

## Saved radar coverage

- Today's saved digest completed `15/18` attempted source fetches.
- `broad-hackenproof-programs`, `hackenproof-programs`, and
  `hackenproof-audits` each exceeded the 58-second browser wall timeout.
- The later database changes were moving relative-age text for Tenbin,
  Kiteworks, old Sherlock competitions, and a Bugcrowd VDP. They are not scope,
  reward, deployment, or accepting-program deltas.
- Coverage therefore remains formally degraded even though the official
  HackenProof pages were independently readable.

## Official HackenProof reconciliation

- `https://hackenproof.com/programs` returned `323 Results`. Its newest visible
  regular smart-contract program remained Hinkal, started September 3 and last
  updated September 4. No September 13 regular on-chain launch, asset addition,
  scope expansion, or reward increase was visible.
- `https://hackenproof.com/audit-programs` showed Europeum API DualDefense as
  the sole live entry. It is a time-bounded audit competition running September
  10-17 and is excluded from this regular-bounty run.
- Kinza was paused; 0G Labs and Swap.io were ended. These do not provide a
  current intake surface despite their historical smart-contract scopes.

## Selected target

Phoenix Legacy was the strongest collision-clean standing fallback because its
first-party bounty still publishes material High/Critical rewards, exact source,
a deployed Solana program, a funded official market, and ordinary trader-controlled
asset transitions. The target-local bounded pass is recorded in
`audit_targets/phoenix-legacy-standing-bounty-20260913/HUNT_STATUS.md`.

The exact focused test command passed `3/3`, but no collision-distinct
attacker-caused asset or authority delta survived. The terminal disposition is
`KILL / ROTATE`. No mainnet write, report, contact, fee, or submission occurred.
