# Immunefi non-Ethereum live-diff screen — 2026-10-10

**Disposition:** One real scoped configuration transition found, but no outsider-to-victim path or accepted High/Critical harm survived the bounded diagnostic. No report, fee, privileged transaction, live exploit, or contact occurred. This is not a claim that these chains or programs are exhausted.

## Scope and pins

- [Immunefi public bounty catalog](https://immunefi.com/public-api/bounties.json) fetched again at **2026-10-10 21:21:08 UTC**: HTTP 200, 6,460,188 bytes, SHA-256 `fb1f931ff1c979097ea625247f800149c2519fafe61ff17448a520eeb9a0d32f`, ETag `W/"2026-10-09T13:53:37.555Z:232:232"`. Kept active, non-invite, non-ended programs and `smart_contract` rows with exact 40-hex addresses on each chain's explorer. Asset rows can repeat an address.
- [Exactly's current official scope](https://immunefi.com/bug-bounty/exactly/scope/) was read on 2026-10-10; it lists Optimism `ProposalManager` (`0x6817974ca2c354f2fa40d8349b725b5bf81c8338`) in the catalog, accepts only the published High/Critical impacts, and excludes attacks needing privileged addresses. A changed allowlist alone is not an impact.
- Read-only Optimism RPC: `https://mainnet.optimism.io`; Arbitrum RPC: `https://arb1.arbitrum.io/rpc`; Base RPC: `https://mainnet.base.org`. The historical call probes below used `eth_call`, not transactions.

## Standard proxy-upgrade and Base implementation gates

`Upgraded(address)` topic `0xbc7cd75a20ee27fd9adebab32041f755214dbc6bffa90cc0225b39da2e5c2d3b` was queried with exact scoped address arrays in nonoverlapping 10,000-block windows. Every listed window returned a valid log array and **zero exact emitter matches**:

| Chain | Address count | Blocks / UTC time | Successful windows | Matches |
| --- | ---: | --- | ---: | ---: |
| Optimism | 166 | `157734069–158034068`, Oct 3 22:35:15–Oct 10 21:15:13 | 30 | 0 |
| Arbitrum | 419 | `511527674–513627673`, Oct 4 05:58:15–Oct 10 21:15:12 | 210 | 0 |

Optimism end-block hash: `0x67b9222ca49211b585f7179928057d2999291d1d8fb79a15a3f2330f9e3459e9`. Arbitrum end-block hash: `0x0dea287c6552683578b2c74b1e67c73c6a69f9ad578b0e777fbc94a3071d2987`.

For Base, compared EIP-1967 implementation slot `0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc` at blocks `52138783` (Oct 3 22:35:13, hash `0x2361610b5bc2bf33a4f86bac7cfc91e318f363d35279442f70aef5678c246bdd`) and `52438783` (Oct 10 21:15:13, hash `0xece34b206556cdfd2fb73603f224e7a802f14240829411225b5c2733997c6b93`). All **146** exact active addresses outside already-covered Compound/Hyperlane/Spark/Aera/Ether.fi/Ondo/Folks lanes returned successfully; **29** held a nonzero implementation at both blocks and **117** held zero at both, with **zero slot changes**. This does not cover beacon or custom proxy upgrades, configuration changes, or contracts outside these address filters. Public Base and BSC `eth_getLogs` limits prevented a comparable broad event-history scan there; BSC historical `eth_getStorageAt` returned missing-trie-node or archive-access errors. Those coverage gaps remain **UNKNOWN**.

## Exactly KBTC target allowlist transition

The scoped Optimism `ProposalManager` emitted `TargetAllowed(address,address,bool)` (`0x0f89b9b3f51b332e771731693eb2252fedd0db543f62b3fb654a1e459bec49ad`) in [tx `0x3ae8e05e...e6189d4d4`](https://optimism.blockscout.com/tx/0x3ae8e05e45d3f1bba3fd18292c8b833135de13995921e9e976d10ebe6189d4d4), block **157808824**, **2026-10-05 16:07:05 UTC**. Target `0x73e0c0d45e048d25fc26fa3159b0aa04bfa4db98` is the verified KBTC proxy; admin `0x6561b09d5d6012d416dfdf9befe37228ae89434c` is a Safe proxy. Event value `allowed=true`. The [verified ProposalManager source](https://optimism.blockscout.com/api/v2/smart-contracts/0x6817974ca2c354f2fa40d8349b725b5bf81c8338) shows `allowTarget` requires `DEFAULT_ADMIN_ROLE`. Its `preExecutionChecker` rejects a non-market, non-special target unless `allowlist[target]` is true, then accepts any selector for that target when called by `PROPOSER_ROLE`.

**Historical differential.** `allowlist(KBTC)` was `false` at block `157808823` and `true` at `157808824`; the scoped [ExaPlugin](https://optimism.blockscout.com/api/v2/smart-contracts/0x3d73D0fb9e63c49ba8e9cd738964D5E08C047f3e) had `PROPOSER_ROLE` before the event. With a read-only `eth_call` *from that plugin address*, `preExecutionChecker(account, KBTC, 0xa9059cbb, 0x)` reverted `Unauthorized()` (`0x82b42900`) before and returned `0x` after. This proves the target-check change; an `eth_call` caller override is not an ability an outsider has in a real transaction.

**Outsider/victim falsifier.** A real Exa account `0xb3563e8870810ece56cf494c8bd16784d32adfb3` appeared as an account in a prior `ProposalManager.Proposed` event and resolves to the [verified UpgradeableModularAccount](https://optimism.blockscout.com/api/v2/smart-contracts/0x0046000000000151008789797b54fdb500e2a61e). From unrelated EOA `0x000000000000000000000000000000000000dEaD`, a read-only call to that victim account's `execute(KBTC, 0, transfer(attacker, 0))` reverted **identically before and after** the allowlist change: outer `RuntimeValidationFunctionReverted` (`0x10b2d36b`) identified its [WebauthnOwnerPlugin](https://optimism.blockscout.com/api/v2/smart-contracts/0x8f498c8240E621f8050249D1C2F5f2AAeE484ca0) and nested `NotAuthorized()` (`0xea8e4eb5`). A direct EOA call to victim `executeFromPluginExternal` after the change reverted `ExecFromPluginExternalNotPermitted` (`0x808e3b3c`). Direct EOA call to `ProposalManager.preExecutionChecker` reverted `AccessControlUnauthorizedAccount` (`0xe2517d3f`). The zero transfer probes authorization without moving any token or requiring the victim to hold KBTC.

The verified ExaPlugin routes `propose` and `executeProposal` through `msg.sender` as the account identity, and keeper-executable proposal functions use a listed Market, proposal amount/receiver checks, and token/route-specific execution. No observed borrower-supplied argument selects an arbitrary *victim* account plus KBTC selector. The new target allowance lets an already-authorized account/plugin execution interact with KBTC; it does not by itself bypass the account's owner validation. A different attacker-controlled entry point or a victim-side authorization flaw would be new evidence to reopen this lane.

## Bounty gate and continuation

Asset mapping: scoped ProposalManager **supported**. Configuration change: **supported**. Public untrusted actor path to another account: **not demonstrated and specifically rejected by the calls above**. Accepted direct theft/freeze/insolvency/bad debt impact: **not demonstrated**. This is a deployment/configuration diff, not a reportable finding. Do not promote or submit without a materially different outsider/victim transition and a qualifying harm path. Continue with future verified in-scope live changes rather than replaying this target-allowlist check.
