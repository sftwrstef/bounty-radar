# 2026-10-05 official-source reconciliation

## Coverage health

The scheduled radar run was **degraded at 15/18 sources**. These three sources
failed with the same bounded browser timeout and therefore cannot support a
"quiet day" conclusion:

- `broad-hackenproof-programs`
- `hackenproof-programs`
- `hackenproof-audits`

At the morning check, the official HackenProof indexes were reconciled directly
for target selection. The programs index showed 324 results and Ult as the
newest regular launch (2026-09-28). The audit-programs index showed 100 results
and EverValue as the newest live audit (2026-10-02 through 2026-10-16).
Submission counts changed but no new asset, deployment, reward, or scope delta
was established for either at that time. See the later same-day check below.

The same-day SQLite `scope_changed` rows were relative-age/status wording churn.
Hyperlane release alerts concerned package releases and were not independently
established as bounty-scope changes.

## Genuine fresh delta

The official programs index marked **ADI Foundation Smart Contracts** as last
updated on 2026-10-05. Its official page advanced the exact accepted source from
`zkos-v0.29.11` / `04346d566e7625ae42ec74861da409329f9f4a3d` to the stated
ADI-mainnet version `zkos-v0.30.2` /
`9ddc915c85d1f44c79b5d55e160d384138ed5105`.

Current exact in-scope assets:

- `l1-contracts` — through Critical;
- `l2-contracts` — through Critical;
- `da-contracts` — through High.

The page excludes `system-contracts`, proof-verification algorithms, unmodified
third-party/vendor code, theoretical-only issues, and vendor-shared issues
publicly fixed before submission. Current rewards are Critical `$10,000`, High
`$5,000`, Medium `$2,000`, and Low `$200`; the submission fee is `$7`. A working
end-to-end PoC and continuous video are mandatory, and public-network testing is
forbidden.

This is a genuine scope/deployment delta because the retained ADI dossier's
explicit reopen condition was advancement of the exact program pin to deployed
v0.30.2. The run therefore followed the **fresh-delta branch** and selected ADI
ahead of the queued XOXNO item.

## Later same-day check — 17:55 ET

The official audit-programs index now shows **101 results** and a new live
Digital Oro International SCA DualDefense Audit (2026-10-05 through
2026-10-26, advertised maximum $3,000). Its sole listed smart-contract source
is `hackenproof-public/sweepstakes`, marked **invite-only/request access**;
the public repository URL returned 404. The official detail requires KYC,
50 reputation points, a working PoC, and a Critical impact involving direct
fund loss or permanent lock. Source and participation access are **UNKNOWN**;
no enrollment, access request, source acquisition, or testing was attempted.
The launch is a real fresh-scope addition, but the available evidence does not
establish that it was visible at the morning check.

The regular-programs index still shows 324 results at this check. No additional
material regular-program delta was established from the visible cards; this is
not a complete assertion about every program detail page. The earlier audit
index link `/audits` was incorrect (404); the configured official route is
`/audit-programs`.

## Sources

- Official program: <https://hackenproof.com/programs/adi-foundation-smart-contracts>
- Official programs index: <https://hackenproof.com/programs>
- Official audit-programs index: <https://hackenproof.com/audit-programs>
- Digital Oro official audit detail: <https://hackenproof.com/audit-programs/digital-oro-international-sca-dualdefense-audit>
- Local radar digest: [`../digests/2026-10-05.md`](../digests/2026-10-05.md)
