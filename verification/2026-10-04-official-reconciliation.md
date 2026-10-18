# Official source reconciliation - 2026-10-04

Latest bounded refresh: `2026-10-04T13:34:08.999887Z`.

## Coverage

- The radar scan completed `15/18` source fetches and rewrote
  `digests/2026-10-04.md`.
- `broad-hackenproof-programs`, `hackenproof-programs`, and
  `hackenproof-audits` each exceeded the 58-second browser timeout.
- This is degraded coverage, not a quiet or no-change result.

## Official HackenProof reconciliation

- The official standing index at <https://hackenproof.com/programs> is readable
  and shows `324 Results`. `Ult: Trade Stocks & Crypto` remains the newest live
  launch, dated `2026-09-28`, with `74` visible submissions and a `$20,000`
  maximum. No October 4 standing-program launch is visible.
- The official audit index at <https://hackenproof.com/audit-programs> is
  readable and shows `100 Results`. `EverValue SCA DualDefense Audit` remains
  the only NEW/LIVE top row, running `2026-10-02` through `2026-10-16`, with
  `42` visible submissions and a `$2,500` maximum. The submission count rose
  from `32` in the October 3 reconciliation; this is participation churn, not
  an asset, scope, deployment, or reward delta.

## Database deltas

- SQLite contains `26` October 4 `scope_changed` rows: `14` Bugcrowd, `7`
  HackerOne, and `5` Intigriti.
- Every previous/current pair differs only in rendered relative-age text. The
  bounded refresh added one Walt.io row changing `Last changed 4 days ago` to
  `5 days ago`; its URL, ten in-scope assets, `$100,000` maximum, paid status,
  and launch date are unchanged.
- No genuine new program, asset, deployment, reward, or scope delta survived.

## Routing

The run follows the **degraded-coverage / queued-target branch**. Golem
Sherlock #412 was selected ahead of Arc Remote Signer because GOL-OUT-001 is
the strongest existing survivor (`4/5` supported), the current official page
still independently exposes exact source pins and Critical terms, and one
bounded local H5 question remained executable. Arc remains `3/5` and its next
decisive Nitro/KMS/VSOCK falsifier requires separately authorized AWS
resources, spend, and teardown.

Current Golem details and exact local verification are recorded in
`audit_targets/golem-provider-sandbox-sherlock-20261003/HUNT_STATUS.md`.
