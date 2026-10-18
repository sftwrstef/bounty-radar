# Official source reconciliation - 2026-10-03

Latest bounded refresh: 2026-10-03T09:02:11-04:00.

## Coverage

- The saved radar scan completed 15/18 source fetches and wrote
  `digests/2026-10-03.md`.
- `broad-hackenproof-programs`, `hackenproof-programs`, and
  `hackenproof-audits` each exceeded the 58-second browser timeout.
- This is degraded coverage, not a quiet or no-change result.

## Official HackenProof reconciliation

- The public standing index at <https://hackenproof.com/programs/> was readable
  and showed 324 results. `Ult: Trade Stocks & Crypto` remains the newest live
  launch, dated 2026-09-28. No 2026-10-03 regular-program launch was visible.
- The public audit index at <https://hackenproof.com/audit-programs> was
  readable and showed 100 results. `EverValue SCA DualDefense Audit` remains
  the only new/live top row, running 2026-10-02 through 2026-10-16. Its visible
  submission count increased from 12 in the 2026-10-02 snapshot to 32; this is
  participation churn, not a new asset, reward, or scope delta.
- Independent official-page visibility restores enough listing awareness for
  target selection, but it does not make the saved browser feeds healthy.

## Database deltas

- SQLite recorded 23 same-day `scope_changed` rows from the BountyHunters
  HackerOne, Bugcrowd, and Intigriti feeds.
- All 23 normalize to relative-age text churn. Twenty-two differ only by a day
  counter; Omarchy changed from `today ago` to `1d ago`. No row changed its
  asset count, reward, launch date, program state, or URL.
- No genuine new program, asset, deployment, reward, or scope delta survived
  the bounded comparison.

## Routing and selected target

The run follows the **degraded-coverage / queued-target branch**.

`ARC-RS-178-01` remains the strongest eligible queued target because it is an
existing serious survivor with a current exact source pin, affirmative source
scope, material private-key authority impact, a passing public collision
matrix, and several executable local controls. It outranks EverValue, whose
Critical-only USD 2,500 shared pool, 50-point/KYC gate, September audit, and 32
visible submissions remain materially less favorable.

The Circle Arc scope CSV was fetched again from
<https://hackerone.com/teams/arc-bbp/assets/download_csv.csv>. Its SHA-256
remains `057d50cef40740508ae81b4833ee71d2509f221442889ea58131ebc11d11c1a7`,
and it still marks both `circlefin/arc-node` and
`circlefin/arc-remote-signer` as submission- and bounty-eligible source assets
with a structured Critical maximum.

## Executable evidence and disposition

No settled test was repeated. The target-local 2026-10-03 evidence already
contains the required current local executions:

- the combined attacker-first/operator-first modeled KMS binding package passed
  both focused tests in 0.478 seconds;
- the first-party Arc signing-provider control passed 1/1;
- the exact-current copied-secret vote/proposal authority test at
  `arc-node` `6e764023ee6515fe70573e123ed2db912a7207b4` passed 1/1 and an independent
  cached rerun also passed; and
- the focused validator replacement/removal recovery control passed 2/2.

Current evidence score: **3/5 supported**. Material cloned-key authority,
current scope/configuration, and dismissal resistance are supported. A real
attacker-first Nitro/VSOCK/NSM/KMS transition and one clean end-to-end exploit
chain remain unresolved.

Terminal verdict: **BLOCKED / INCUBATE - serious Medium-or-higher candidate,
severity not yet fixed; not submission-ready**. The strongest dismissal is
that modeled providers do not prove the real Nitro/KMS boundary. Recovery is
privileged but real: an authorized controller can zero or remove the old
validator after replacement, so permanent authority, chain halt, takeover,
finality failure, and fund-loss claims remain unsupported. Public collision
review passes, but the undisclosed private audit behind v1.7.8 leaves material
grouping/private-duplicate risk.

The exact next action crosses the external-action boundary: complete the
pending IAM cleanup, produce a fresh priced and hash-sealed single-use
execution packet, and obtain explicit authorization for the named AWS
resources/APIs, spend ceiling, and fault-tested teardown before running the
paired Nitro/KMS/VSOCK falsifier. No AWS, Arc-chain, submission, fee, signature,
contact, or disclosure action was performed by this run.
