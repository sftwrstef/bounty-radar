# GMX MultichainVault unrecorded-balance trace — 2026-10-08

Status: **PARK exact hypothesis / NO PICK**. This was a bounded read-only source trace, not an executable PoC, deployed-state check, or target-wide GMX closeout. No live transaction, installation, report, fee, or contact occurred.

## Pin and scope boundary

The archived source snapshot at `audit_targets/gmx-glv-sideways-immunefi-20260831/source` has no `.git`; its target status records `gmx-io/gmx-synthetics` `updates` commit `bf30ebb4cff17b7f92f8c738f145e75b871a1576`. A read-only `ls-remote` check on 2026-10-08 found the public `updates` head still at that commit, but the archive bytes were not independently rehashed against Git. The target root is a symlink into the Extreme SSD recovery archive; no file there was edited or built. [Current GMX program information](https://immunefi.com/bug-bounty/gmx/information/) lists an ongoing paid smart-contract bounty and PoC requirement; [resources](https://immunefi.com/bug-bounty/gmx/resources/) include `gmx-synthetics`. Candidate-specific deployment and eligibility are not established.

## Decisive question and stopping condition

Can a supported ordinary GMX workflow leave tokens in `MultichainVault` unrecorded **across committed transactions**, so a later untrusted caller can call public `MultichainTransferRouter.bridgeIn(account, token)` and credit that preexisting delta to their own account? Stop if normal in-scope ingress transfers and records atomically, leaving only raw mistaken transfers or attacker-chosen misdirection; promote only after a supported cross-transaction source of unrecorded balance and a positive same-state victim delta are shown.

## Read-only result

At the recorded source snapshot, `MultichainTransferRouter:35-43`, `MultichainUtils:63-91`, and `StrictBank:51-56` make the public delta-credit mechanism plausible **if** a positive unrecorded delta already exists. The source trace found no ordinary flow that creates such a delta between transactions:

- The documented same-chain WNT/USDC path uses one delegatecall multicall for `sendWnt`/`sendTokens` and `bridgeIn` (`BaseRouter:37-46`, `PayableMulticall:18-31`, `scripts/multichain/bridgeInSameChain.ts:45-54`, `test/multichain/MultichainTransferRouter.ts:54-63,84-94`).
- LayerZero assets remain with `LayerZeroProvider` until `lzCompose`, which transfers to the vault and calls `recordBridgeIn` in one transaction (`LayerZeroProvider:97-127`). Its native top-up and bridge-out refund paths likewise pair transfer and record (`:267-282,376-385`).
- The mapped claim, cancellation-refund, GM/GLV mint, withdrawal/order output, and execution-fee paths pair arrival with `recordTransferIn` in the same transaction (`MultichainClaimsRouter:50-68,96-108,130-142`; `DepositUtils:165-204`; `GlvDepositUtils:190-255`; `WithdrawalUtils:174-188`; `GlvWithdrawalUtils:340-354`; `OrderUtils:379-393`; `ShiftUtils:387-401`; `ExecuteDepositUtils:525-532`; `ExecuteGlvDepositUtils:86-91`; `ExecuteWithdrawalUtils:332-349`; `SwapOrderUtils:70-85`; `DecreaseOrderUtils:91-119,143-165,337-350`; `GasUtils:183-188`; `MultichainRouter:78-105`). `StrictBank._afterTransferOut` refreshes the checkpoint, and `Bank:85-97` blocks transferring to itself.

Raw ERC-20 transfers to the vault, user-selected receiver misdirection, a deliberately misconfigured external-call refund, rebasing, or unsolicited airdrops could create a positive delta, but none is yet a demonstrated normal GMX ingress/victim-loss path. The source trace was not a runtime test; it does not prove no omitted path exists. Guardian's resolved cross-chain C-02/C-03, H-08, M-08, L-07, and later FeeVault findings are related ingredients, not a verified exact collision with a current supported delta.

**Reopen condition:** identify one supported transfer that commits an unrecorded positive `balanceOf(vault)-tokenBalances[token]` before a separate caller may invoke `bridgeIn`, or a current deployed semantic/configuration change that does so. Then restore the source to an admitted internal working tree, verify its bytes/pin, and run a two-actor same-state local test: normal arrival; attacker `bridgeIn`; final account balances and withdrawal; atomic multicall and direct-transfer controls. Do not build inside the recovery archive.
