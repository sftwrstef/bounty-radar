# Immunefi high-bounty Ethereum implementation screen — 2026-10-10

**Result: no EIP-1967 implementation change on the exact listed assets in this bounded interval.** This is a deployment gate for the diff-first hunt, not a claim that these programs have no vulnerabilities or configuration changes. There was no live upgrade to source-diff or test locally in this lane.

The official [Immunefi public catalog](https://immunefi.com/public-api/bounties.json) was freshly fetched on October 10 around 22:24 UTC; its SHA-256 remained `fb1f931ff1c979097ea625247f800149c2519fafe61ff17448a520eeb9a0d32f` (232 records), with ETag `W/"2026-10-09T13:53:37.555Z:232:232"`. The read-only scanner kept active, non-invite programs with a listed maximum bounty of at least USD 1 million, then only `smart_contract` assets having exact 40-hex Ethereum addresses in `etherscan.io` or `eth.blockscout.com` URLs. This produced **20 programs, 499 asset rows, and 474 unique addresses**. A program-level maximum is only a selection filter; it does not establish the reward for an individual asset or impact.

Using `https://eth.drpc.org` archive reads, the [receipt](evidence/2026-10-10-immunefi-eth-high-bounty-eip1967-screen.json) records **948 successful `eth_getStorageAt` reads** of the EIP-1967 implementation slot (`0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc`): one per address at Ethereum block `26143955` (October 7, 23:59:59 UTC; hash `0x848fd4b171e4d60e4c09e6985b94ec2021235e1a2fb14c4110a9b88f4a85bb28`) and one at finalized block `26164957` (October 10, 22:14:47 UTC; hash `0x263ac779d7b4b435cc0f7a959dfe8da931b8595a25c91208a5456c4a682090ed`). **Zero slot values changed**; 132 were nonzero at both endpoints. Every requested address returned a validated response. dRPC's free-tier batch limit was three calls, and the [reproduction script](evidence/immunefi_eth_high_bounty_eip1967_screen_20261010.py) used complete, checked three-call batches with a resumable temporary cache.

The earlier [exact-address `Upgraded(address)` event screen](2026-10-10-immunefi-ethereum-upgraded-intersection.md) had zero matches against a **superset** of 1,013 current-catalog Ethereum addresses through block `26164624` (October 10, 21:08:11 UTC). The present scanner closed its tail to finalized block `26164957` in four nonoverlapping 100-or-fewer-block windows: **33 additional standard upgrade logs, zero exact matches** among the 474 selected addresses. The full standard-event gate and the point-in-time slot comparison therefore agree for this selected set.

**Limits:** an implementation could change and be restored between the two slot snapshots without a standard `Upgraded` event; beacon/custom proxies, direct deployments, configuration transactions, implicit or repository-only scope, other explorer URL forms, and unlisted child contracts are outside this screen. No specific value/authority boundary was advanced to an exact-binary local falsifier because no new exact implementation was observed. Reopen on a newly verified scoped address or exact custom/configuration deployment event. No production write, funds, fee, report, or target contact occurred.

Reproduce with a current official catalog payload:

```sh
curl -fsSL https://immunefi.com/public-api/bounties.json -o /tmp/vesper-immunefi-bounties.json
python3 bounty-radar/verification/evidence/immunefi_eth_high_bounty_eip1967_screen_20261010.py /tmp/vesper-immunefi-bounties.json /tmp/vesper-eth-eip1967-screen.json
```
