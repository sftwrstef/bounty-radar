# 2026-09-27 official-source reconciliation

## Coverage health

- Radar completed with `15/18` source coverage.
- All three HackenProof browser feeds exceeded the 58-second fetch limit.
  This run therefore records **degraded coverage**, not a quiet day.
- Direct official API reconciliation recovered both independent indexes:
  - standing programs: `324` total; response SHA-256
    `76687951f0689730d19b3376a02881dcdccf321c0eefe79eca72656096932f`;
  - audits: `99` total; response SHA-256
    `075f7f9eeb798fc915bb03acf5058e806a558bc0db8578bd6539cb8880198166`.
- The newest active standing entry remains Celestia (updated 2026-09-25),
  already worked on September 25 and 26. The only active audit is RAIN-USDR,
  already represented by submitted finding `RAINUSDR-1512` and terminal/collision
  follow-ups.
- The database contains 22 source-item changes; inspection shows age-label
  rollover only. There is no genuine new program, asset, scope, deployment,
  reward, or fee delta in those rows.

## Exactly one selected target

**Optimism `op-challenger/v1.10.0` / Immunefi.** It beat the queue because the
release-documentation commit was the only source-backed same-day Web3 delta,
the release is marked recommended, and Optimism retains a material reward cap.
Celestia was already worked twice, RAIN-USDR is submission-blocked, and the
remaining high-heat entries had no current scope or runtime delta.

Pins:

- radar commit `fe0f79991f90384c331c9c6b46ddce42b51ab174`;
- release tag commit `7e7f1ee3616812fa42ae8fa72afe3843b55e2abf`;
- release JSON SHA-256
  `c5c102e3c8293e8414f7db046bb70ef1f348eba4396d9b95c8588d8817bdc79f`;
- compare JSON SHA-256
  `9fa71f78f5bdb8e72afa4e2386c71e1635250583f344ec93666df6433fb111fa`.

## Verification and verdict

The exact runtime delta is a missing-directory special case in
`op-challenger/game/disk.go`. The release notes disclose that ZK RPC tracing
does not create the directory, the old scheduler therefore logged a cleanup
error each iteration, and ZK support is not running in production. The current
official Immunefi information and scope pages were also checked. The program
remains live, but the visible Blockchain/DLT asset table does not expressly
list `op-challenger`; this exact change has no eligible impact regardless.

The strict gate is `0/5`: no public attacker action, no material impact, no
live affected mode, no dismissal resistance, and no exploit chain. Same-state
comparison changes only whether one operator error is logged. Victim,
attacker, protocol, game, proof, withdrawal, balance, authority, recovery, and
profit deltas are all zero.

**Terminal verdict: KILL the exact v1.10.0 delta / ROTATE.** No clone, build,
dependency install, public-deployment test, signing, platform login, payment,
submission, contact, or disclosure occurred.
