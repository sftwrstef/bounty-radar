# Official source reconciliation - 2026-10-02

Latest bounded refresh: 2026-10-02T09:40:06-04:00.

## Coverage

- The latest saved radar completed 15/18 source fetches and wrote
  `digests/2026-10-02.md` plus terminal JSON.
- The three HackenProof feeds exceeded the 58-second browser timeout.
- This is degraded coverage, not a quiet/no-change result.
- The saved database records source-delta alerts for the new HackenProof audit,
  Bugcrowd changes, and Intigriti changes. No Telegram delivery row was observed
  in the current database query.

## Official HackenProof reconciliation

- Standing index: https://hackenproof.com/programs/ was independently readable
  on 2026-10-02 and showed 324 results. The current top live rows include Ult,
  Hotcoin, Hinkal, ADI Predictstreet, the three Starknet programs, Arcadia,
  Hyperbridge, Cetus Web, and Ample. Ult remains the newest visible launch,
  dated 2026-09-28. Starknet Blockchain/DLT remains visibly updated
  2026-10-01. No newer regular-bounty launch was visible.
- Audit index: https://hackenproof.com/audit-programs was independently
  readable on the latest refresh and showed 100 results. The new top row is the
  live EverValue SCA DualDefense Audit, running 2026-10-02 through 2026-10-16.
  Its final pin is `869ce44932964450a57c804b636387f293903745`, and only
  `EVALocker.sol`, `PositionMarket.sol`, and `RevenueRouter.sol` are in scope.
- Independent official-page visibility restores listing awareness for target
  selection, but it does not make the saved radar fetches healthy.

## Fresh delta

- EverValue is a genuine new audit-program delta, not a timestamp-only change.
  It requires 50 reputation points, KYC, and a runnable PoC. Only Critical
  findings causing direct fund theft/loss or permanent fund lock qualify for
  the USD 2,500 pool; Medium and High rewards are USD 0. The official page
  already showed 12 submissions and a September 2026 Hacken audit.
- This is a valid fresh listing but a poor replacement for the active serious
  survivors: it is Critical-only, participation-gated, collision-heavy on day
  one, and capped at a shared USD 2,500 pool.

## Deltas and routing

- Repository activity signals were observed for Hyperlane packages/registry and
  Optimism, but none established a new scoped deployment or eligible runtime.
- The platform collector emitted five `scope_changed` rows: three Bugcrowd and
  two Intigriti in the earlier pass, followed by seven more age/summary rows in
  the later pass. These are discovery signals only and did not beat the active
  survivor on verified scope, impact, or collision posture.
- Routing is therefore **degraded coverage with one genuine fresh audit delta**.
  The fresh listing was verified and filtered, while the current serious
  survivor remains the selected target because ordinary rotation already
  stopped at a stronger evidence-backed lane.

## Selection

The current selected target is Circle Arc Remote Signer v1.7.8 on HackerOne,
candidate `ARC-RS-178-01`, at commit
`a95f05b2d8e90af0bc9e890efd9ee7bc8b51b5b0`.

- The live official scope CSV still lists `circlefin/arc-remote-signer` and
  `circlefin/arc-node` as bounty- and submission-eligible, with Critical maximum
  severity.
- The same-day combined local diagnostic remains PASS: two focused tests prove
  the attacker-selected KMS authority and attacker-first gRPC initialization
  composition at a `diagnostic_only` boundary.
- The next decisive experiment is the preserved two-branch real Nitro/KMS run.
  It requires explicit AWS account/resource authorization and an explicit USD 3
  prebuilt or USD 5 builder cap. It was not executed in this refresh.
- Ordinary rotation remains stopped. Separately, the same-day Secure Custom
  Fields 6.9.5 finding remains a 5/5 report-ready strong Medium and was not
  submitted.

No public-chain action, AWS action, submission, fee, terms acceptance,
enrollment, signature, or project contact occurred.
