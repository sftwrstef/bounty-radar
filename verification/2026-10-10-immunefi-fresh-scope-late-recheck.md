# Immunefi fresh-scope late recheck — 2026-10-10

**Read-only check at 21:15 UTC.** Fetched the official [Immunefi public bounty catalog](https://immunefi.com/public-api/bounties.json) with HTTP 200 and compared its full bytes and parsed asset records against the preserved `/tmp/vesper-immunefi-bounties-20261010.json` (mtime 17:37 UTC). The [public bounty index](https://immunefi.com/bug-bounty/) remained available. No login, target transaction, report, fee, or contact occurred.

| Measure | Earlier complete snapshot | 21:15 UTC official response | Delta |
| --- | ---: | ---: | --- |
| Raw bytes | 6,460,188 | 6,460,188 | 0 |
| SHA-256 | `fb1f931ff1c979097ea625247f800149c2519fafe61ff17448a520eeb9a0d32f` | same | none |
| Program records | 232 | 232 | 0 |
| Asset records | 6,950 | 6,950 | 0 |
| Response ETag | recorded in [earlier recheck](2026-10-10-immunefi-fresh-scope-recheck.md) | `W/"2026-10-09T13:53:37.555Z:232:232"` | none |

The latest `addedAt` in the full catalog remains **2026-10-09T08:02:03.018Z**. Among the 64 assets added since September 25, the only smart-contract groups are [Enzyme Onyx](https://immunefi.com/bug-bounty/enzyme-onyx/scope/) (1), [Folks Finance](https://immunefi.com/bug-bounty/folksfinance/scope/) (21), [Twyne](https://immunefi.com/bug-bounty/twyne/scope/) (2), [USDT0's IOTA route](https://immunefi.com/bug-bounty/usdt0/scope/) (3), and [Ondo](https://immunefi.com/bug-bounty/ondofinance/scope/) (35). The remaining two are [ENS](https://immunefi.com/bug-bounty/ens/scope/) website assets. There are **zero** assets added on October 10. This is a complete current-catalog filter on `addedAt`, not an inference from page-update labels.

The potential sideways pick, USDT0's September 30 IOTA route, is already pinned in [its Ethereum–IOTA target record](../../audit_targets/usdt0-ethereum-iota-fresh-immunefi-20260930/HUNT_STATUS.md) and independently revisited in the [October 9 lockbox target record](../../audit_targets/usdt0-iota-lockbox-immunefi-20261009/HUNT_STATUS.md). Those records include exact scoped Ethereum adapter `0xAEf027F94008430BF4Fc27FFABB49ea6F1dd3414` and IOTA package identifiers, deployed bytecode/function checks, packet/accounting controls, and an explicit changed-peer/cap/source-hash reopening condition. Repeating the same control without a fresh deployed difference would not answer a new security question. The other recent smart-contract groups are the lanes already tracked in the [live-diff ledger](2026-10-10-immunefi-live-diff-hunt.md) or an active independent Folks pass. No newly added smart-contract asset survives this fresh-scope filter for a distinct local diagnostic.

**Disposition: `NO_MATERIAL_SCOPE_DELTA` relative to the dated full-catalog snapshot.** This says nothing about implementation upgrades, mutable configurations, beacon/custom upgrades, private programs, or impact-first coverage lacking an exact catalog row. A new verified deployment/configuration change or changed catalog hash should trigger the next scope intersection. The temporary fetched payload is `/tmp/vesper-immunefi-20261010-fresh.json`; the durable evidence here is its exact hash, count, response ETag/date, and comparison result.
