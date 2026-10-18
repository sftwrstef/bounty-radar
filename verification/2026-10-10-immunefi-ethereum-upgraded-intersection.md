# Immunefi Ethereum `Upgraded` intersection — 2026-10-10

**Discovery question.** Does a recent Ethereum EIP-1967-style proxy upgrade intersect an exact currently listed Immunefi smart-contract address and justify one focused same-state diff hunt? This is a read-only cross-program screen, not an audit or a claim that no in-scope contract changed.

## Official catalog and normalization

Fetched Immunefi's [public bounty catalog](https://immunefi.com/public-api/bounties.json) at **2026-10-10 21:07:51 UTC**. It returned **6,460,188 bytes**, SHA-256 `fb1f931ff1c979097ea625247f800149c2519fafe61ff17448a520eeb9a0d32f`, and ETag `W/"2026-10-09T13:53:37.555Z:232:232"`—the same dated catalog revision as today's [fresh-scope reconciliation](2026-10-10-immunefi-fresh-scope-recheck.md). The catalog has 232 program records. I kept only programs with `isPaused=false`, `inviteOnly=false`, and `endDate=null`, then assets with `type=smart_contract` whose URL host was `etherscan.io`, `www.etherscan.io`, or `eth.blockscout.com` and whose path contained an exact 40-hex Ethereum address. This yields **1,046 asset rows / 1,013 unique lowercased Ethereum addresses** across **153 filtered programs**. Multiple asset rows at the same address were retained in the mapping.

The filter intentionally omits paused, invite-only, and ended programs. It also misses implicit/primacy-of-impact scope, contracts listed through a repository or a non-Ethereum explorer URL, and Ethereum assets whose URL has no parsable address. An address match would have been a discovery lead requiring individual scope and deployed-source verification, not an eligibility conclusion.

## Passive event scan receipt

Pinned Ethereum block interval **26,104,625–26,164,624 inclusive** (60,000 blocks), from **2026-10-02 12:25:11 UTC** to **2026-10-10 21:08:11 UTC**. End block hash: `0x3f9be9cdc7b91dac5dc6941572b472d58ddfabd648ce1572cc56784e37a0a06f`. Using `https://eth.drpc.org`, I queried `eth_getLogs` with only topic0 `keccak256("Upgraded(address)") = 0xbc7cd75a20ee27fd9adebab32041f755214dbc6bffa90cc0225b39da2e5c2d3b`, in **600 consecutive, nonoverlapping 100-block windows**. Every window returned a parseable log array; there were no skipped windows, RPC errors, or rate-limit stops at this chunk size. Each emitting `log.address` was lowercased and intersected with the official-catalog map. Larger 500–1,000-block dRPC windows were rejected, so the scan used 100-block windows throughout.

| Block interval | Windows | `Upgraded(address)` logs | Exact catalog-address matches |
| --- | ---: | ---: | ---: |
| 26,104,625–26,114,624 | 100 | 1,843 | 0 |
| 26,114,625–26,124,624 | 100 | 1,332 | 0 |
| 26,124,625–26,134,624 | 100 | 1,279 | 0 |
| 26,134,625–26,139,624 | 50 | 764 | 0 |
| 26,139,625–26,149,624 | 100 | 1,460 | 0 |
| 26,149,625–26,159,624 | 100 | 1,349 | 0 |
| 26,159,625–26,164,624 | 50 | 569 | 0 |
| **Total** | **600** | **8,596** | **0** |

Method is reproducible by looping `eth_getLogs({fromBlock: hex(lo), toBlock: hex(min(lo+99,end)), topics: [topic]})` over the pinned range, checking every JSON result, and comparing each emitter address with the normalized catalog addresses. The complete official catalog was fetched to `/tmp/vesper-immunefi-live-catalog.json`; the normalized map and local scan driver were saved under `/tmp/vesper-immunefi-ethereum-addresses.json` and `/tmp/vesper_scan_immunefi_upgrades.py` for same-host reproduction. Those temporary files are convenience copies; the official URL, content hash, block bounds, topic, normalization rule, and per-range receipt above are the durable evidence.

## Disposition and proof limits

**No exact match in this bounded standard-upgrade event scan.** There is no implementation pair to diff, public value/authority change to trace, same-state local diagnostic to run, or finding-specific public collision to assess. Stop at the requested 60,000-block bound rather than expand by brute force.

This covers only emitting addresses of the standard `Upgraded(address)` event on Ethereum. It does **not** cover beacon upgrades, custom/nonstandard proxy events, direct deployments, implementation-address events whose scoped asset is a different proxy, storage/configuration changes with no upgrade event, other chains, or implicit scope. It does not prove that all Immunefi programs had no material live changes. Reopen on a newly listed exact address, a verified specific upgrade/configuration event outside this topic, or a later dated interval.
