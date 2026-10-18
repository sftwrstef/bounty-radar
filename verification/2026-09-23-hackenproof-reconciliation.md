# Official HackenProof reconciliation — 2026-09-23

Reviewed at `2026-09-24T00:17:07Z` (`2026-09-23` America/New_York).

## Coverage health

- The saved radar digest completed 15 of 18 sources. `broad-hackenproof-programs`,
  `hackenproof-programs`, and `hackenproof-audits` each exceeded the 58-second
  browser-fetch limit. This remains degraded collector coverage, not a quiet-day
  conclusion.
- A direct read of the official standing-program API returned 324 programs.
  Raw response SHA-256 for the first 10 programs sorted by `updated_at desc`:
  `38fedd37545f1e5a76b6f1ee6c1f1383a406fa5d641b08c7e09e56e7bf410afb`.
- A direct read of the official audit-program API returned 99 historical and
  current audit programs. Raw response SHA-256 for its first 20 entries:
  `f0f876cd971f71257d4a1ac98037b0c4b96dec33f5578657760c0e68ce7cd7b1`.

Official sources:

- `https://hackenproof.com/programs`
- `https://hackenproof.com/programs-api/programs?not_audits=true&page=1&per_page=10&order_by%5Bupdated_at%5D=desc`
- `https://hackenproof.com/audit-programs`
- `https://hackenproof.com/programs-api/audits?page=1&per_page=20`

## Standing-program delta

The official `updated_at desc` cohort began with:

| Program | State | Updated | Maximum | Reconciliation |
| --- | --- | --- | ---: | --- |
| EXMO | Completed | 2026-09-23 | USD 3,000 | Terminal status change; not selectable. |
| HTX | Completed | 2026-09-23 | USD 100,000 | Terminal status change; not selectable. |
| ADI Foundation Smart Contracts | Active | 2026-09-23 | USD 10,000 | Exact asset/source pin unchanged and already covered. |
| BingX Exchange | Active | 2026-09-22 | USD 4,000 | Web/exchange program; no source-backed smart-contract delta. |
| Treehouse Smart Contracts | Active | 2026-09-22 | USD 50,000 | Same 68-address scope; deployed V3/Fastlane V2 remain unlisted. |

### ADI Foundation Smart Contracts

The current official detail still lists:

- in scope: `l1-contracts` and `l2-contracts` at Critical and `da-contracts`
  at High;
- out of scope: `system-contracts`;
- exact commit `04346d566e7625ae42ec74861da409329f9f4a3d`, tag
  `zkos-v0.29.11`; and
- Critical USD 10,000, High USD 5,000, 108 submissions, KYC, PoC, 150
  reputation, and a USD 7 submission fee.

This is identical to the exact scope and economics already captured in
`audit_targets/adi-stack-contracts-hackenproof-20260921/HUNT_STATUS.md`. That
dossier also establishes that the live ADI deployment is v0.30.2 while the
only eligible source is v0.29.11, and it closes the public bridge/replay,
legacy-payer, initialization, governance/restriction, DA, upgrade, and verifier
families. The date change supplies no new source, asset, deployment parity, or
ordinary-caller transition and therefore does not satisfy any recorded reopen
condition.

Official detail:
`https://hackenproof.com/programs/adi-foundation-smart-contracts`

Raw detail API SHA-256:
`3505b27147632c1dbc6ab5c680cadb5b94f8d021eb7e26d748b8ca477d484d05`.

### Treehouse Smart Contracts

The current official detail API still contains exactly 68 scoped addresses.
It continues to list `TreehouseRedemptionV2`
`0xcd63a29FAfF07130d3Af89bB4f40778938AaBB85` and the old Fastlane
`0x829525417Cd78CBa0f99A8736426fC299506C0d6`. It does not list the deployed
`TreehouseRedemptionV3` `0x62fB2022C4Be4586432f298dE9a404dA92D9Dd90`,
Fastlane V2 `0xB64F47Ba404565917f2cC9bF5825d9415328ba40`, or
`NftExemptionGate` `0xc74dcf053145752F558C0a601ffcfCc30Cc4EA20`.

That is the same 68-address scope and exact V3 exclusion recorded in
`audit_targets/treehouse-teth-redemption-sideways-hackenproof-20260827/HUNT_STATUS.md`.
The September 22 date does not reopen the unlisted V3 transition or the already
falsified scoped redemption/NAV/PnL lanes.

Official detail: `https://hackenproof.com/programs/treehouse-smart-contracts`

Raw detail API SHA-256:
`2d6edb4e264ce5b1276e3fa6c3c10bb2b7b0381aa578abfe1dd2da5c444e2b11`.

## Audit-program delta

RAIN-USDR remains the only active audit program: 14 September through
1 October 2026, reward pool up to 14,000 USDT, and 388 submissions at this
check. It is not selectable because report `RAINUSDR-1512` is already pending,
and the worked-target registry separately records that exact-source access to
the private contest pin is unresolved. All other first-page audit entries are
ended. There is no new live audit launch.

Official detail:
`https://hackenproof.com/audit-programs/rain-usdr-smart-contract-audit-contest-sept-2026`

## PUMB no-login check

The private-program listing and all four known private detail routes returned
HTTP `401`, a 49-byte body, and the same message: `You need to sign in or sign
up before continuing.` No cookie, browser profile, credential, login form,
locked account, or authenticated API was used.

- `https://dashboard.hackenproof.com/user/programs?tab=private`
- `https://dashboard.hackenproof.com/user/programs/pumb-online-corporate`
- `https://dashboard.hackenproof.com/user/programs/pumb-online-mobile`
- `https://dashboard.hackenproof.com/user/programs/pumb-external-services`
- `https://dashboard.hackenproof.com/user/programs/payhub`

The public PUMB company page exposes only the public historical programs
Payhub Web and Pumb Tacsk (ended) and PUMB Web (live, last updated 15 May 2026).
It does not expose the private Online Corporate, Online Mobile, External
Services, or Payhub asset/rule tables. Therefore no material private PUMB scope
change is publicly observable, and none of the parked private lanes reopens.

Public company page: `https://hackenproof.com/companies/pumb-dot-ua`.

## Selection and bounded diagnostic decision

**NO SELECT.** No fresh source-backed High/Critical-shaped public-input
value/authority transition survived the official-source and worked-target
collision gate:

- ADI is the identical exhausted old pin with a live-version mismatch;
- Treehouse is the identical 68-address scope and still excludes the only new
  deployed transition;
- RAIN-USDR is already submitted and lacks authorized exact-source access;
- BingX is not a source-backed smart-contract delta; and
- EXMO and HTX are completed.

No mechanics-first exploit diagnostic was run. Each source-backed candidate
met a permitted pre-test terminal condition: the complete eligible surface was
already covered without a changed reopen fact, the potentially fresh deployed
surface is explicitly unlisted, or the exact audit lane is already submitted.
Repeating an old PoC under a changed page date would not be new evidence.

No target was initialized or promoted. No report, fee, submission, login,
credential use, contact, production transaction, or cleanup was performed.
