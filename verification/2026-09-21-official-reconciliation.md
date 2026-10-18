# Official reconciliation — 2026-09-21

## Coverage health

The local run completed 15 of 18 sources. `broad-hackenproof-programs`,
`hackenproof-programs`, and `hackenproof-audits` each exceeded the 58-second
browser-fetch limit. This is degraded coverage, not a quiet HackenProof day.

The durable database recorded 19 item changes across five aggregator sources:
11 Bugcrowd, four Intigriti, two broad BountyHunters, one HackerOne, and one
YesWeHack. The Telegram outbox contained 156 total rows, zero pending, and zero
errored after the run.

## Official HackenProof fallback

The official standing-program index was opened directly and contained 324
programs. Its newest visible regular Web3 entries remained Hotcoin (September
14), Hinkal (September 3), and other already recorded programs. No post-
September-20 regular-program launch or scope addition absent from the local
ledger was identified.

The official audit-program index showed RAIN-USDR as the only live audit window
(September 14 through October 1; 312 submissions; reward up to 14,000 USDT).
That lane is excluded from today's selection because Vesper already has
submission `RAINUSDR-1512` pending. Other visible audits had ended.

## Fresh delta classification

- Tenbin and d-you were tracker resurfacing, not unworked launches; both already
  have target-local dossiers and terminal reopen conditions.
- The Huntr entry is a contest, not a regular Web3 bounty.
- The visible Bugcrowd, Intigriti, PowerDNS, and Kiteworks changes were Web2,
  VDP, or challenge entries and did not add a regular smart-contract asset.
- No genuinely new paid Web3 regular-bounty scope delta survived official and
  local collision reconciliation.

## Selected rotation target

GMGN Web & Mobile was the best unworked regular-bounty rotation target because
its live wildcard scope includes the public OpenAPI host, the product exposes
fund-moving automated trading, the official client is public and recently
updated, and the local worked-target registry had no GMGN dossier. The resulting
method/host signature-domain hypothesis was tested and killed at strict 1/5;
see
[`HUNT_STATUS.md`](../../audit_targets/gmgn-openapi-signature-domain-hackenproof-20260921/HUNT_STATUS.md).
