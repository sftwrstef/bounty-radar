# HackenProof reconciliation — 2026-08-30

## Coverage disposition

The saved `2026-08-30` digest is **degraded at 15/18**, not quiet. All three
configured HackenProof browser sources exceeded the 58-second wall-clock limit:

- `broad-hackenproof-programs`
- `hackenproof-audits`
- `hackenproof-programs`

The generic Playwright skill wrapper remains unwired (`playwright-cli: command
not found`). A separate read-only run through the radar's pinned Playwright
environment succeeded at `2026-08-30T13:41Z`; this reconciles the official
indexes but does not retroactively make the saved digest complete.

## Official-index reconciliation

- `https://hackenproof.com/programs` returned 317,183 rendered bytes, 20
  first-page program links, and `321 Results`. No listing showed an August 30
  regular-program launch or update; the newest visible standing-program update
  remained Cronos Web on August 27.
- `https://hackenproof.com/audit-programs` returned 322,629 rendered bytes and
  ten first-page audit links. Zendex SC DualDefense was the only visible `LIVE`
  competition (August 18–September 9, up to `$2,000`); the other nine visible
  Europeum competitions were `ENDED`.
- The database recorded 25 item changes today. They were ENS audit-competition,
  Vercel Sandbox, ordinary Web2/VDP, and Dovecot changes; none introduced a new
  regular smart-contract bounty. `telegram_outbox` had zero pending rows.

## Genuine Web3 delta and sole selection

The only current repository signal with a genuinely new deployed Web3 surface
was Hyperlane Registry `v25.6.0`, tag commit
`32171f7889f6ec42fde083208685c7c2e0a58f0f`, released August 29 at 17:16 UTC.
It added five production Moonpay USDT-to-USDC atomic local rebalancing bridges.
This beat the queue because it was a same-day deployed value-bearing delta,
whereas the HackenProof pages were unchanged and the other database changes
were competitions, VDPs, or ordinary Web2 programs.

The selected lane is terminal **KILL / ROTATE — 1/5**. All five live source
routers authorize only operator EOA `0xa394...8FE3` and their local bridge; a
public outsider is rejected. The five bridge addresses are absent from
Hyperlane's 222-asset fixed Immunefi table, and the program excludes attacks
requiring privileged addresses and configuration-only impact. See
`audit_targets/hyperlane-registry-v2560-sideways-immunefi-20260830/HUNT_STATUS.md`.

## Non-actions

No account, platform login, signature, transaction, fee, submission, project
contact, disclosure, public-deployment mutation, or exploit call was made.
Only public page reads, local source inspection, and ordinary read-only getters
were used.
