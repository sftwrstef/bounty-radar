# HackenProof official-index reconciliation — 2026-09-05

The scheduled radar retained degraded source coverage at **15/18** because all
three Playwright-backed HackenProof sources timed out:

- `broad-hackenproof-programs`
- `hackenproof-programs`
- `hackenproof-audits`

A same-run official-page reconciliation was attempted through the pinned local
browser workflow; both `/programs` and `/audit-programs` again timed out after
58 seconds and produced zero extracted records. Read-only official web-page
retrieval then confirmed the current first page:

- bug bounties: 323 results; Bullbit QA Testing is **NEW/LIVE**, started and
  updated 2026-09-04, Web/Apps only, up to `$50`, paid `$0`; Hinkal is
  **NEW/LIVE**, started 2026-09-03, updated 2026-09-04, up to `$10,000`, paid
  `$0`;
- audit programs: Alberich Token SC is **NEW/LIVE**, 2026-09-01 through
  2026-09-08, 21 submissions, up to `$3,000`; Zendex SC is **LIVE**,
  2026-08-18 through 2026-09-09, 159 submissions, up to `$2,000`.

This reconciles the visible official first-page candidates for selection but
does not rewrite the radar's recorded 15/18 coverage. Treat the browser-backed
source pipeline as degraded until its extraction succeeds normally.
