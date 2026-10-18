# 2026-10-12 manual source reconciliation

UTC review window: 01:44–01:50. This is a read-only follow-up to [the generated digest](../digests/2026-10-12.md), not a replacement for its raw scan result.

- The radar completed **15/18** source fetches. `broad-hackenproof-programs`, `hackenproof-programs`, and `hackenproof-audits` each timed out at 58 seconds. Their coverage remains **UNKNOWN/degraded**, not quiet.
- Independently opened both official HackenProof indexes: [programs](https://hackenproof.com/programs) and [audit programs](https://hackenproof.com/audit-programs). The visible first-page bounty listings include Ult (started 2026-09-28) and Hotcoin (started 2026-09-14). The audit index shows Digital Oro (started 2026-10-05, ends 2026-10-26) and EverValue (started 2026-10-02, ends 2026-10-16) as live. This was a manual first-page check; it does **not** repair the radar's full-index coverage or establish no changes on other pages.
- The [EverValue audit brief](https://hackenproof.com/audit-programs/evervalue-sca-dualdefense-audit) expressly requires 50 reputation points and a PoC; only Critical fund loss or permanent lock is reward-eligible, with three specified contract files at commit `869ce44932964450a57c804b636387f293903745`. No account-tier check, enrollment, fee, checkout, or diagnostic was undertaken. It is not promoted from the index listing alone.
- The `bountyhunte.rs` entries for Revert v4lend, Verisk VDP, Omarchy, Walt, and the listed Bugcrowd programs were already in the 2026-10-11 digest under the same URLs. Their repeated `scope_changed` labels are **aggregator churn**, not independently verified new scope. The relative-date countdown on Revert is not a material delta. No alert-worthy, queue-changing change was verified in this pass.

Next hunt allocation: continue a scoped, independent local diagnostic; do not retry the three timed-out lanes merely to claim quiet and do not pay, enroll, submit, or test live assets from this index result.

## 10:09–10:13 UTC local-only refresh

- Ran one `scan --no-alerts --progress --json` pass. It rewrote the [same-day digest](../digests/2026-10-12.md); the command exited 0, and each source result reported `alert_sent: false`. No Telegram, email, or other notification was sent.
- Coverage remained **15/18**. The same three HackenProof browser lanes each exceeded the 58-second wall-clock limit. Their full-index coverage is still **UNKNOWN/degraded**; a successful process exit does not make these lanes quiet.
- Independently reopened both current official indexes, [bug bounties](https://hackenproof.com/programs) and [audits](https://hackenproof.com/audit-programs). The visible first-page listings still show Ult and Hotcoin for bounties, Digital Oro and EverValue for live audits. This is a first-page spot check only, not full-index reconciliation.
- This run's five apparent platform changes—Bugcrowd apps-plus2, meetical, bloompeak; Intigriti nxtportvdp; Cantina Revert v4lend—use the same URLs present in the [2026-10-11 digest](../digests/2026-10-11.md). Revert's “ends in 22 days” versus “23 days” is a relative-date countdown. None is independently verified as a new official scope/reward change or queue-changing launch. Repository heat moved +1 for Optimism and Hyperlane registry, with zero new repository signals.

Disposition: **no verified queue-changing delta** from this bounded pass. Preserve the degraded source status and continue the strongest scoped local diagnostic.

## 13:32–13:53 UTC automation refresh and fresh DreamX delta

- Ran `./.venv/bin/python -B -u -m bounty_radar scan --no-alerts --progress --json`. The process exited `0`, rewrote the same-day digest, and sent no alerts. Coverage remained **15/18**: `broad-hackenproof-programs`, `hackenproof-programs`, and `hackenproof-audits` each exceeded the 58-second browser limit. These lanes remain **UNKNOWN/degraded**.
- Independently reconciled both official HackenProof indexes for target selection. A genuine new live audit was visible: [DreamX Marketplace & DEX SCA DualDefense Audit](https://hackenproof.com/audit-programs/dreamx-marketplace-and-dex-sca-dualdefense-audit), started 2026-10-12 and ending 2026-10-26. The official source points to the public `dd-3` branch at `c7cdd792abc2ea7f575d115bc4964dfd60e5434e`. The page lists Critical-only fund loss/permanent lock rewards up to `$2,500`, plus 50-reputation, KYC and runnable-PoC requirements; participation is invite-only.
- The canonical SQLite database contains no DreamX snapshot/change row because the owning HackenProof lanes failed. This manual official-index finding is the verified delta for routing, not repaired automated coverage.
- Repeated Bugcrowd, Intigriti and Cantina rows in the generated digest were already present on 2026-10-11 or reflected relative countdown churn. They were not promoted as independent official deltas.
- Bounded investigation is recorded in [`audit_targets/dreamx-hodlbonds-dd3-hackenproof-20261012/HUNT_STATUS.md`](../../audit_targets/dreamx-hodlbonds-dd3-hackenproof-20261012/HUNT_STATUS.md). The branch built and focused controls passed, but the identifiable Avalanche factory and vault implementation expose an older ABI and different bytecode. No collision-distinct Critical survived, and current `dd-3` deployed parity remains unresolved.

Disposition: **fresh-delta branch, DreamX BLOCKED at best 1/5**. Do not claim quiet coverage or live impact, and do not enroll, complete KYC, pay, submit, or contact the target.
