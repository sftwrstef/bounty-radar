# Official source reconciliation — 2026-09-08

Run time: `2026-09-08T13:52:41Z`

## Coverage health

- Local radar digest: **15/18** successful sources.
- Degraded sources: `broad-hackenproof-programs`, `hackenproof-programs`, and
  `hackenproof-audits`; each exceeded the 58-second browser timeout.
- SQLite's five apparent Sherlock launches are historical contests (Extrafi
  XLend, ZKP2P V2, Resolv Core, Extra Finance, and Avantis v1.5), not new
  standing bounties. Their guessed standing-bounty endpoints return `404`.
- Pending Telegram rows: zero.

## Official reconciliation

- HackenProof programs: **323** results. The newest regular entries remain
  Bullbit QA (September 4, `$50`) and Hinkal (September 3, `$10,000`); there is
  no post-September-4 regular smart-contract launch.
- HackenProof audits: Alberich (ends September 8, `$3,000`) and Zendex (ends
  September 9, `$2,000`) are the only live entries and are competitions, so both
  are excluded.
- Immunefi: Alchemix and Strata received September 8 catalog timestamps. Neither
  added a new scoped asset or audit. Alchemix's scoped repository has advanced
  from the prior local pin and includes Base deployment artifacts plus public
  Immunefi-fix commits. Strata's live JRT/SRT action gates remain disabled.
- Rocket Pool's September refresh was already reconciled locally as a
  disclosure-only known-issues update with no new asset or deployment.

## Selection

Selected exactly one regular-bounty target: **Alchemix V3 / Immunefi**. It had
the highest-information current delta: a scoped source change and Base
deployment artifacts, a `$150,000` maximum, `$10` Pay-to-Submit fee, and no KYC.

The planned Base Alchemist, transmuter, and vault addresses have no bytecode at
block `51,042,918`; the broadcast itself embeds the older `e418811` source. The
current `ea6f58b` cover-accounting controls pass `2/2` and produce zero
incremental loss or attacker profit. Terminal result: **KILL exact lane / ROTATE
— strict 1/5**. See the target-local `HUNT_STATUS.md`.

Coverage remains explicitly degraded at **15/18**; official-page reconciliation
restored selection visibility but does not convert the failed local sources
into successful radar coverage.
