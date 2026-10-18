# 2026-09-12 official source reconciliation

Reviewed at `2026-09-12T13:36:47Z`.

## Saved radar coverage

- Today's saved digest completed `15/18` attempted source fetches.
- `broad-hackenproof-programs`, `hackenproof-programs`, and
  `hackenproof-audits` each exceeded the 58-second browser wall timeout.
- The database recorded 23 same-day source-item changes. The only sent source
  alert was the YesWeHack Kiteworks launch. The Sherlock aggregator changes
  were relative-age or archival metadata churn, not new accepting bounties.
- Coverage therefore remains formally degraded even though the official
  HackenProof pages were independently readable.

## Official HackenProof reconciliation

- `https://hackenproof.com/programs` returned the current standing-program
  index with `323 Results`. The newest visible regular smart-contract program
  remained Hinkal, started 2026-09-03 and last updated 2026-09-04; no September
  12 regular smart-contract launch or expansion was visible.
- `https://hackenproof.com/audit-programs` showed Europeum API DualDefense as
  the sole live entry. It is a time-bounded audit competition running September
  10-17, so it is excluded from this regular-bounty run.

## Genuine fresh deltas and selection

- Optimism's September 12 release set was not a usable semantic delta:
  `op-node/v1.19.7` changes no runtime behavior, `op-reth/v2.4.4` is
  observability-only, Alt-DA changes are expressly excluded, and the remaining
  components/configuration are unlisted or operator-bound.
- The Sherlock feed entries in today's digest were old contests or unchanged
  standing bounties; target-local preflights also closed current Flat Money,
  Napier, Pinto, and Hotstuff intake on value, status, parity, or economics.
- Kiteworks is a genuinely new black-box bounty but currently lacks a pinned
  backend/runtime and already showed extreme private-report saturation.
- Ammalgam's newly scoped `FlashLoanAdaptor`
  (`0x8AD93a30D023bbDB918461eB2F54948Fee09f4E1`) and `SwapAdaptor`
  (`0xab1c7758c13ec9efd36785b70e05737520c68ac8`) were the strongest same-day
  regular-bounty delta: exact deployed assets, public production use, material
  pair value, and a narrow value/authority mismatch to falsify.

## Ammalgam official pin

The current first-party Cantina page returned HTTP 200 and embedded these
current terms: program live; Critical maximum `25,000 USDC`; High maximum
`10,000 USDC`; `50 USDC` submission fee; 70 findings; only High/Critical;
public/external-function PoC and on-chain LP loss required; both adapter
addresses expressly listed. No fee was paid and no live-chain write occurred.
