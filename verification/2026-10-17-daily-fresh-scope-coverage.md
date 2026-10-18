# Daily fresh-scope coverage — 2026-10-17

Reviewed at 2026-10-17 17:24 EDT.

## Coverage health

- Canonical scanner: **degraded, 15/18**.
- Failed sources: `broad-hackenproof-programs`, `hackenproof-programs`, and
  `hackenproof-audits`; each exceeded the 58-second browser wall-clock limit.
- Digest: [`../digests/2026-10-17.md`](../digests/2026-10-17.md).
- Both official HackenProof indexes were separately reconciled. This restores
  target-selection visibility but does not upgrade scanner coverage to healthy.

## Official-index reconciliation

- [HackenProof programs](https://hackenproof.com/programs/): ZMO Exchange
  remains the newest standing program (started 2026-10-14). Arcadia's
  2026-10-15 update and changing submission counts do not establish another
  material scope delta.
- [HackenProof audit programs](https://hackenproof.com/audit-programs): the
  index increased from 102 to 103 entries. **Europeum V2 API DualDefense
  Audit** is genuinely new: live 2026-10-16 through 2026-10-21, exact final
  commit `d22970541483fa7729d0add5709a05d767d4f5ab`, Critical-only rewards from
  `$0-$2,000`, and 22 submissions at review time.
- [Europeum V2 official page](https://hackenproof.com/audit-programs/europeum-v2-api-dualdefense-audit)
  and [published final audit](https://hacken.io/audits/europeum/pt-europeum-api-aug2026/)
  identify the same final commit. The final audit records 28 findings: 25
  resolved, two accepted, and one mitigated.

## Other genuine delta

- Cantina's official public-bounties API identifies **Rain Bug Bounty** as live
  from 2026-10-16. Its scoped reward bands top out at `$25,000` for Critical,
  not the aggregator's `$100,000` top-reward label; the API separately reports
  a `$100,000` total reward pot.
- The only listed assets are the production domains `rain.xyz`,
  `raincards.xyz`, and `raincards.com`, including subdomains. Medium through
  Critical rewards are published, but mainnet testing is prohibited and no
  source repository, fork target, or unsigned local fixture is listed.
- Official participation metadata conflicts: the prose says KYC is not
  required, while the structured API field says `kycRequired: true`; this is
  `CONFLICTING` and was not resolved by login or enrollment.

Repeated HackerOne/Bugcrowd relative-age changes and the Revert v4lend
countdown decrement were normalized as churn, not scope deltas.

## Routing

**Degraded-coverage / verified fresh-delta branch.** Rain was ranked first for
Medium eligibility and higher rewards but blocked before testing by the
production-only/no-source boundary. Europeum V2 ranked second because its exact
source pin was already present locally and allowed a bounded differential.
