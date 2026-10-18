# Immunefi Ethereum configuration-event intersection — 2026-10-10

**Discovery question.** Can a recent owner/role/pause/beacon event on an exact currently listed Immunefi Ethereum smart-contract asset reveal a changed public value or authority boundary, missed by a standard `Upgraded(address)` screen? This is a read-only triage scan, not a proof of exploitability or complete configuration-history coverage.

## Catalog and query

The official [public Immunefi catalog](https://immunefi.com/public-api/bounties.json) fetched on 2026-10-10 remained byte-identical to the 17:37 UTC preserved snapshot: 232 programs, 6,950 assets, SHA-256 `fb1f931ff1c979097ea625247f800149c2519fafe61ff17448a520eeb9a0d32f`. Following the [standard-upgrade intersection](2026-10-10-immunefi-ethereum-upgraded-intersection.md), I kept unpaused, non-invite, non-ended programs and exact 40-hex Ethereum address links on Etherscan or Ethereum Blockscout: 1,046 asset rows / 1,013 unique addresses. Duplicate rows were preserved for attribution, not counted as distinct contracts.

I queried `https://eth.drpc.org` read-only `eth_getLogs` over Ethereum blocks **26,104,625–26,164,624 inclusive**, in **600 nonoverlapping 100-block windows**. All windows returned a parseable log array with no errors. Topic0 was an OR filter for standard `BeaconUpgraded(address)`, `AdminChanged(address,address)`, `RoleGranted(bytes32,address,address)`, `RoleRevoked(bytes32,address,address)`, `OwnershipTransferred(address,address)`, `Paused(address)`, and `Unpaused(address)`. Each emitting `log.address` was intersected with the exact normalized catalog map. The [durable receipt](evidence/2026-10-10-ethereum-config-intersection.json) saves the full set of exact matches, counts, and coverage. Same-host scan drivers are `/tmp/vesper_prior_config_intersection.py` and `/tmp/vesper_recent_config_intersection.py`.

| Event | All observed logs | Exact listed-address logs |
| --- | ---: | ---: |
| BeaconUpgraded | 5,364 | 0 |
| AdminChanged | 368 | 0 |
| OwnershipTransferred | 13,735 | 0 |
| RoleGranted | 2,287 | 90 (Ethena) |
| RoleRevoked | 321 | 0 |
| Paused | 167 | 6 (Pareto 5, Decentraland 1) |
| Unpaused | 131 | 4 (Pareto) |
| **Total** | **22,373** | **100** |

The 100 matched logs came from **eight unique addresses**: two Ethena contracts (90 grants), five Pareto Credit contracts (nine pause/unpause events), and one Decentraland Marketplace V4 (one pause). The [Ethena role analysis](../../audit_targets/ethena-mint-cooldown-lifecycle-independent-immunefi-20260926/analysis/20261010_paired_blacklist_role_grants.md) decoded all 90 as 45 paired *restrictive* blacklist grants by a pre-authorized manager, with no recipient authority increase. The [Pareto epoch analysis](../../audit_targets/pareto-credit-epoch-pause-immunefi-20261010/analysis/20261010_epoch_pause_diff.md) found manager-authorized start/stop transitions at the event blocks; the program excludes paused contracts. The Decentraland [adjacent-block owner/source check](../../audit_targets/decentraland-marketplace-v4-immunefi-20260729/analysis/20261010_ethereum_marketplace_pause_diff.md) found a privileged owner pause. None produced an ordinary-user attack path or a report candidate.

## Limits and next action

This only matches seven common event signatures emitted directly by catalog-listed Ethereum addresses. It misses contract-specific configuration events, events emitted by controllers or unlisted implementation contracts, address links the normalization omitted, L2s/non-Ethereum chains, and silent storage or immutable changes. Address matches require individual official scope/rules, deployed source, actor reachability, same-state impact, and prior-art review. No production transaction or exploit call, fee, report, contact, or disclosure occurred.

An additional same-range [standard `DiamondCut` scan](evidence/2026-10-10-ethereum-diamondcut-intersection.json) queried all 600 100-block windows successfully: 43 `DiamondCut((address,uint8,bytes4[])[],address,bytes)` logs, **zero** exact catalog-address intersections. This closes only that standardized facet-change signal on exact listed emitters; repository-scoped or unlisted diamonds and custom upgrade events remain outside the check.
