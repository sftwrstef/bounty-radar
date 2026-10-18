# 2026-09-15 official source reconciliation

Reviewed at `2026-09-15T13:33:53Z`.

## Saved radar coverage

- The generated digest completed `15/18` attempted source fetches.
- `broad-hackenproof-programs`, `hackenproof-programs`, and
  `hackenproof-audits` remained degraded because each browser fetch exceeded
  the 58-second wall timeout.
- The database recorded relative-age changes for old Sherlock contests, an
  ADAC VDP, Kiteworks, and low-value or VDP Bugcrowd listings. These are not
  fresh regular smart-contract bounty deltas.
- Telegram outbox state was healthy at `143 total / 0 pending / 0 errored`.

## Official HackenProof reconciliation

- `https://hackenproof.com/programs` returned HTTP 200 and `324 Results`, the
  same count as 2026-09-14. No new regular smart-contract program was present.
- `https://hackenproof.com/audit-programs` returned HTTP 200. The new live
  RAIN-USDR listing started 2026-09-14, ends 2026-10-01, and is a time-bounded
  audit contest. Europeum API is the other live audit and ends 2026-09-17.
  Both are excluded from this regular-bounty run.
- Page SHA-256 values were
  `6bc1649748b9e8ff00ed8399138e5602c54c74de78db608035dfb34831f04e0f`
  for the standing index and
  `f1b4fc67dcefcd5c447b8b87c36510a65cb3b17a4bc9299340bdea4338ca63c9`
  for the audit index.

## Repository deltas

- Hyperlane Registry commit `ee3956bed5c6...` only rotates Starknet RPC URLs.
- Hyperlane Monorepo commits `2a938f308567...` and `55e6699b66a4...` are an
  SDK batch-routing-ISM update and a Radix gateway forwarding fix; neither is a
  demonstrated deployed scoped value transition.
- Optimism's six recent commits include publicly named ancestry,
  interop-filter backfill, and dependency-set membership fixes, plus dependency
  and CI changes. They do not provide a collision-clean released primary-chain
  delta.
- Snowbridge commit `76aeee9fffe8...` is the strongest same-day standing-code
  delta. It publishes a new service-fee API, but the changed component is
  off-chain Web code and is expressly outside the program's on-chain-only
  scope. The related first-party UI PR remains draft.

## Selected target

Exactly one target was selected: Snowbridge PR #1809 service-fee construction.
The exact candidate is `KILL / ROTATE — strict 1/5` at preflight because the
program expressly excludes off-chain code, the first-party UI integration is
not deployed, no contract or pallet runtime changed, and no outsider can alter
another user's signed fee fields. See
`audit_targets/snowbridge-service-fee-delta-hackenproof-20260915/HUNT_STATUS.md`.

No clone, dependency installation, report, fee, login, signature, public-chain
write, project contact, submission, or disclosure occurred.

