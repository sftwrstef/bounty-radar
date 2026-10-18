# 2026-09-28 official-source reconciliation

## Coverage health and fresh deltas

- The saved radar completed `15/18` source fetches. All three HackenProof
  browser sources timed out, so coverage was degraded rather than quiet.
- Direct official reads recovered both HackenProof indexes: `325` regular
  programs and `99` audits. The regular index added the live **Ult: Trade
  Stocks & Crypto** program on 2026-09-28, with a `$20,000` maximum, `150`
  reputation points, KYC, and PoC requirements. Its listed targets are the
  Ult iOS and Android apps (Medium maximum) and `https://api.cronos.com`
  (High maximum). No source repository is listed.
- The only live HackenProof audit remains RAIN-USDR, a time-bounded audit
  contest ending 2026-10-01. It is not a regular bounty and was excluded.
- SQLite recorded `20` third-party source-item changes: one huntr change,
  five HackerOne rows, ten Bugcrowd rows, and four Intigriti rows. They are
  relative-age or generic scope-label changes, not verified source, reward,
  deployment, or smart-contract-asset deltas. The official-web fallback added
  Ult as the one genuine launch. Telegram delivery is healthy at `183` total,
  `0` pending, `0` errored.
- Ult did not enter technical selection because this run forbids live public
  API/app testing and the official page exposes no public source. The mobile
  and API surfaces remain eligible for a separately authorized, non-invasive
  workflow; no favorable source/runtime assumption is made.

## Exactly one selected target

**Coinbase `@coinbase/cdp-sdk` x402 cumulative-spend rollback / regular
HackerOne bounty.** It beat the source-accessible queue because the resolved
Kontinuo handoff had already isolated an ordinary untrusted merchant action,
a configured wallet authority boundary, and a conditional incremental payment
path. The official HackerOne CSV includes `https://github.com/coinbase/*` as
bounty-eligible source code with Critical maximum severity.

Pins:

- historical affected npm `1.55.0`, published 2026-08-04, provenance commit
  `1216e96f250d634d34887177bf12f66f021acbcb`, tarball SHA-256
  `9cae5ac93980ded8c3061722483370de28e12ecf8863bdb2a241d6d8ea058c46`;
- first-party fix commit `71ca771023644deb53c88793ed30e6dc0054d15a`;
- current npm `1.57.0`, published 2026-09-25, provenance commit
  `bf134ab0b645c8b807a0bbb5db3615d10d897c04`, tarball SHA-256
  `9e5d8cfcd32e17fe24a6eccaddadf1fc2ab7c69295a5fb2da8ce61e05dfb8a34`.

## Verification, control, and verdict

In v1.55.0, a merchant could settle a transmitted EIP-3009 authorization and
return a fresh `402`, causing the SDK to remove that amount from its off-chain
cumulative-spend ledger. A later separate top-level request could then receive
a new signature. From the same pre-payment state, the truthful historical
control retains spend `A` and blocks request two, while the malicious branch
forgets `A` and can reach wallet `B-2A` / merchant `+2A`; conditional
incremental principal is `A`, before settlement and operating costs.

The current package fails preflight. Its published runtime always calls
`registry.confirm(ctx.paymentPayload)` after transmission, with the source
comment that a self-reported failure cannot safely release an independently
redeemable authorization. The exact root, trigger, affected spend authority,
victim-loss composition, regression tests, and remedy were publicly disclosed
by Coinbase before this run. No current first-party integration with the old
branch, real repeat behavior, or measured positive net economics was shown.

Strict current gate: public merchant access `contradicted for the disputed
transition`; material current delta `contradicted`; official current affected
runtime `contradicted`; dismissal resistance `contradicted`; clean current
exploit chain `contradicted` — `0/5`.

**Terminal verdict: KILL the exact current Coinbase x402 rollback lane / ROTATE.**
No clone, dependency install, build, local or public payment, signature,
transaction, login, fee, report, submission, contact, or disclosure occurred.

## Follow-up rotation: GitLab Pages

The later radar pass completed `15/18` configured sources. All three
HackenProof browser sources timed out, so coverage was degraded rather than
quiet. The official fallback remained authoritative: `325` regular programs
and `99` audit programs were reconciled. Ult was still the sole genuine launch
for the day, but it exposed no public source and the permitted read-only mobile
and API lanes had no stronger untested path. A new Hyperlane Explorer change
was a public fix tied to Immunefi report `#92002`, so it was collision-burned.

GitLab Pages won the rotation because its current official HackerOne scope
explicitly includes the repository, the source and production version could be
pinned, the default deployment path could be checked, and a deterministic
anonymous confidentiality boundary was testable locally without touching a
public deployment.

Pinned GitLab Pages `v19.4.1` at
`ddf88a1750ea87def401f210f17b7c63e03cf409`. A status-200 splat rewrite can
place `/../secret.txt` into the disk handler subpath, after which an unchecked
`filepath.Join(public, /../secret.txt)` selects a sibling job artifact outside
the configured `pages.publish` root. The final unit and full-process acceptance
tests both passed: direct `/secret.txt` returned `404`, while raw
`/old/../secret.txt` returned `200` and the exact 21-byte sibling artifact.
The bounded public-collision search found boundary documentation and local
ingredients, but not the complete bypass composition.

**Terminal verdict: SUBMIT-READY (Medium), pending the user's explicit approval
for the external submission action.** No public deployment was tested and no
report was submitted, paid, signed, disclosed, or sent to GitLab.
