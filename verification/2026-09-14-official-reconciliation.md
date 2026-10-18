# 2026-09-14 official source reconciliation

Reviewed at `2026-09-14T13:33:35Z`.

## Saved radar coverage

- The regenerated digest completed `15/18` attempted source fetches.
- `broad-hackenproof-programs`, `hackenproof-programs`, and
  `hackenproof-audits` remained degraded by browser/Playwright failures.
- A later local source scan added an ADAC Intigriti VDP and relative-age changes
  for old Sherlock contest cards, Kiteworks, and low-value Bugcrowd programs.
  None is a fresh regular smart-contract bounty.
- Telegram wiring was healthy. The verified Hotcoin source launch was recorded
  with normal deduplication, its alert was sent, and the outbox finished at zero
  pending and zero errored rows.

## Official HackenProof reconciliation

- `https://hackenproof.com/programs` returned `324 Results`. The new first card
  was **Hotcoin Web & Mobile**, `LIVE`, started and updated `14 Sep 2026`, with
  zero submissions and a `$1,000` maximum.
- The prior `323 Results` state therefore missed one genuine regular-bounty
  launch in the local browser-backed feeds. It was backfilled under
  `hackenproof-programs`, then today's digest was regenerated.
- `https://hackenproof.com/audit-programs` still showed Europeum API
  DualDefense as the only live audit. It is a time-bounded audit competition
  ending September 17 and is excluded from this regular-bounty run.

## Selected target

Hotcoin Web & Mobile was selected because it was the only genuinely new paid
regular program on September 14 and had zero submissions. It did not pass the
4-of-5 investment gate. The program exposes only live Web, Android, and iOS
targets; prohibits locally hosted PoCs and reports produced by automated or
active exploit tools; and requires a runnable PoC. This automation prohibits
testing public deployments and has no official source, backend build, or local
test environment. The exact autonomous lane is therefore `KILL / ROTATE`, while
a separately authorized manual-account test could reopen it under the program's
rules. See `audit_targets/hotcoin-web-mobile-hackenproof-20260914/HUNT_STATUS.md`.

No Hotcoin request was sent, no account was created or used, no mobile binary
was downloaded, and no report, fee, contact, or submission occurred.

## Standing-code fallback check

The lowest-collision current HackenProof smart-contract fallback not already
represented by an active local code lane was UACatsDivision. Its live official
page lists one Ethereum contract but publishes a `$0` maximum bounty and zero
severity rewards. It was rejected before clone as a paid-hunt hard blocker and
recorded in
`audit_targets/uacatsdivision-preflight-hackenproof-20260914/HUNT_STATUS.md`.

Zest, Bluefin, and KUB do not provide a fresh paid replacement: Zest's current
public lanes have completed live controls, Bluefin still lacks exact published
source parity with production, and KUB already has submitted report
`KUBCHAIN-277`. No new repository signal appeared in the no-alert radar run.
