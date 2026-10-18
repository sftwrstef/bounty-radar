# Next active targets — 2026-10-06

Disposition: `CURRENT_SCOPE_VERIFIED / RANKED BACKUP QUEUE`

This is a read-only target-selection snapshot. No enrollment, contact, clone,
submission, payment, transaction, account creation, or production test was
performed. Current HackerOne program state, signal gate, bounty table, and asset
records were read from HackerOne's public GraphQL endpoint and official asset
exports on 2026-10-06. Source and release pins came from the first-party GitHub
repositories and release APIs.

The shortlist deliberately excludes the session's exhausted or blocked lanes:
Mozilla/Firefox, WordPress, Anthropic, Exodus Hydra, Folks Finance, Digital Oro,
Golem/Yagna, and Doppler CLI. Mattermost was also excluded after its current
HackerOne `submission_state` returned `disabled`; Discourse was excluded because
its first-party 2026 announcement says rewards are paused. Vercel is a strong
fresh-scope watchlist target, but its current HackerOne `target_signal` is `1.0`,
which matches the user's observed participation barrier.

## Ranked queue

| Rank | Program / boundary | Active bounty evidence | Rewards | Source / shipping pin | Barrier | Collision posture |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | **Omarchy — supported reset and local-to-root OS boundaries** | HackerOne `submission_state=open`, `offers_bounties=true`, target signal `0.0`; sole asset `https://github.com/omacom/omarchy` is bounty/submission eligible through Critical; public launch 2026-10-01 | Medium **$250**, High **$750**, Critical **$1,500** | Required submission target is latest default `quattro`; current head `81145eb1fd41532fcae4310b26f860608e2eaf82`. Latest stable release is `v4.0.4`, commit `c668141e9c42b13c80c9ca4ea108e11708c5e8a5` | Public, no signal gate. Working PoC and manual verification required. Reports must remain confidential; policy excludes privileged prerequisites, development-only tooling, dependency-only bugs, and DoS | **Lowest private-dupe exposure by program age**, but public security-fix churn is high. A prior public issue/fix covers retained password hashes after factory reset, so any reset finding must prove a different persisted secret/path and remediation |
| 2 | **Chia Network — Python/Rust consensus and mempool equivalence** | HackerOne `submission_state=open`, `offers_bounties=true`, target signal `0.0`; six first-party source repos are bounty eligible through Critical | General table: Medium **$1,000–$2,000**, High **$2,500–$4,000**, Critical **$5,000–$10,000**. A separate Critical-only row is **$25,000–$50,000**; the public table does not expose its exact row label, so applicability is `UNKNOWN` until a finding-specific scope gate | Latest stable `chia-blockchain` is `2.7.4`, commit `98aba3d176b24b5814e84a33f9d1c11af67a9cdc` (2026-09-10). Its checked-in `poetry.lock` pins `chia-rs` `0.48.0`, tag commit `e11b3c8aa97af8f5d0915d72d4ac7b3c3da00cc2` | Public, no signal gate. In most cases a working PoC is required. Official policy requires local services to use testnet10/testnet11 and explicitly not mainnet | **Mature/high duplicate risk**, offset by exact current cross-runtime composition and clear consensus/fund-impact categories. No exact public issue surfaced in the bounded phrase search below |
| 3 | **Netflix Atlas — datasource URI boundary in the supported OSS release** | HackerOne `submission_state=open`, `offers_bounties=true`, target signal `0.0`; `Open Source - Atlas` is bounty/submission eligible through Critical and explicitly classified as a Secondary Target | Secondary tier: Medium **$300–$600**, High **$600–$2,000**, Critical **$2,000–$5,000** | Current stable release `v1.8.2`, commit `fdac3d3c98f49cf3918fc13862bfb699afbb88a4` (2026-02-27); default `main` head observed at `46780fb612f0667d6cd59d19970bcef98c8f1bda` | Public, no signal gate. OSS reports require a working PoC script; only current and immediately preceding major versions qualify. DoS/resource exhaustion and unlikely user cooperation are excluded | **Medium duplicate risk**: mature project, but only nine open repo issues at review time and no public issue/security advisory surfaced for the exact `file:` datasource reachability question |

## 1. Omarchy

Official evidence:

- Program: <https://hackerone.com/omarchy?type=team>
- Asset export: <https://hackerone.com/teams/omarchy/assets/download_csv.csv>
- Current policy version timestamp: `2026-10-01T17:46:28.474Z`
- Scoped source: <https://github.com/omacom/omarchy>
- Current required branch pin: <https://github.com/omacom/omarchy/commit/81145eb1fd41532fcae4310b26f860608e2eaf82>
- Latest stable release: <https://github.com/omacom/omarchy/releases/tag/v4.0.4>

Why first: it is the only genuinely new, source-only, zero-signal program found
in the current public directory. It gives the best chance of earning a first
valid signal before mature programs or the signal-gated Vercel scope, despite
the smaller ceiling.

Decisive first hypothesis:

> The supported factory-reset lifecycle preserves at least one prior-owner
> credential-bearing path or Btrfs subvolume not covered by its explicit scrub
> list, allowing the newly provisioned, economically untrusted owner to recover
> a previous owner's token or confidential state.

Minimum diagnostic: trace the exact `v4.0.4`/current-`quattro` snapshot and
subvolume lifecycle, then use a disposable local Btrfs image or Omarchy VM with
unique canaries in browser/keyring, agent CLI, Docker, NetworkManager, Tailscale,
and root-side application state. Run the supported reset, create the new owner,
and search every path/subvolume that owner can access. Compare with a fresh
install control. Kill if no canary survives, if recovery requires root/physical
disk access not granted to the new owner, or if the only survivor is the already
public password-hash class.

Strongest dismissal: factory reset is a privileged owner action and the new
owner may need root to mount old subvolumes. The PoC must therefore show access
available to the ordinary newly provisioned owner and incremental confidential
data, not merely forensic recovery with external media.

Collision notes: public searches found the already fixed
`Factory reset retains the previous owner's password hash` issue/PR pair
([issue #10378](https://github.com/omacom/omarchy/issues/10378)); this is a
related ingredient, not novelty evidence for another path. The target also has
heavy public security-hardening PR activity, so exact remediation comparison is
mandatory before promotion.

## 2. Chia Network

Official evidence:

- Program: <https://hackerone.com/chia_network?type=team>
- Asset export: <https://hackerone.com/teams/chia_network/assets/download_csv.csv>
- Current policy version timestamp: `2024-09-12T18:45:17.614Z`
- Core source: <https://github.com/Chia-Network/chia-blockchain>
- Shipping release: <https://github.com/Chia-Network/chia-blockchain/releases/tag/2.7.4>
- Rust implementation pin: <https://github.com/Chia-Network/chia_rs/releases/tag/0.48.0>

Eligible source assets are `chia-blockchain`, `chia-blockchain-gui`, `clvm_rs`,
`chia_rs`, `chiapos`, and `chiavdf`, all bounty eligible through Critical. The
same program also lists the Chia Vault test site/API and iOS signer, but those
were not used to infer source-code authorization.

Decisive first hypothesis:

> A spend bundle can be normalized or rejected differently by the Python
> mempool/prevalidation path and the pinned Rust `chia-rs` consensus condition
> parser, creating a transaction that one lifecycle stage accepts while block
> validation interprets differently.

Minimum diagnostic: pin `chia-blockchain` `2.7.4` plus locked `chia-rs` `0.48.0`
and differentially execute the same generated spends across mempool admission,
prevalidation, block-generator condition extraction, and final block-body
validation. Compare accept/reject, cost, coin additions/removals, announcements,
timelocks, and signature pairs. Start with non-canonical CLVM encodings and
unknown/duplicate condition combinations. Kill the exact lane if all stages
share the same Rust result or a strongest same-state control proves no ledger,
consensus, or fund delta.

Strongest dismissal: a parser difference that is rejected before inclusion or
only changes diagnostics is not a security vulnerability. Promotion requires a
full lifecycle divergence with a consensus, authorization, or fund consequence.

Collision notes: the bounded GitHub issue search for `mempool consensus
differential` returned no exact public result. This does not lower private
duplicate risk; the program and consensus code are mature.

## 3. Netflix Atlas

Official evidence:

- Program: <https://hackerone.com/netflix?type=team>
- Asset export: <https://hackerone.com/teams/netflix/assets/download_csv.csv>
- Current policy version timestamp: `2026-09-15T14:17:10.260Z`
- Scoped repo: <https://github.com/Netflix/atlas>
- Stable release: <https://github.com/Netflix/atlas/releases/tag/v1.8.2>

The current policy explicitly maps Atlas to the Secondary Target tier and
requires a working PoC script for OSS reports. `StreamContext.findBackendForUri`
in `v1.8.2` treats relative and `file:` URIs as local files and
`FileBackend.source` opens them with `FileIO.fromPath`; the unresolved question
is whether a shipped externally reachable Atlas API lets an untrusted caller
supply that datasource URI.

Decisive first hypothesis:

> A remotely supplied Atlas datasource/subscription URI reaches the local
> `file:` backend, exposing service-readable local bytes through evaluation
> output or diagnostics.

Minimum diagnostic: start unmodified `v1.8.2` standalone with a canary file,
enumerate only documented expression/subscription/evaluation routes, and send
the same valid expression once with an allowed backend URI and once with a
relative/`file:` URI. Require canary bytes or a data-derived oracle outside the
service boundary. Kill if datasource construction is library-only/trusted,
local schemes are unreachable from any shipped API, or the bytes cannot cross
back to the caller.

Strongest dismissal: local sources may be an intentional trusted embedding API,
not an HTTP boundary. The route-to-sink composition must be demonstrated before
calling this SSRF/LFI or assigning severity.

Collision notes: bounded repository issue and GitHub Security Advisory searches
returned no exact `file:` datasource disclosure. Private-known risk remains
unknown.

## Deferred fresh scope: Vercel

Vercel is active and unusually fresh: on 2026-09-21 it added 17 explicit
bounty-eligible source assets, including `next.js`, `vercel`, `ai`, `workflow`,
`nuxt`, `svelte`, and `nitro`. Open-source rewards span $250–$1,000 Medium,
$750–$5,000 High, and $2,750–$10,000 Critical depending on tier. It is not in
the immediate top three because HackerOne currently reports a `target_signal`
requirement of `1.0`, matching the user's observed inability to submit. Reopen
as soon as the account has one qualifying signal.

Official references:

- <https://hackerone.com/vercel?type=team>
- <https://hackerone.com/teams/vercel/assets/download_csv.csv>

## Recommended rotation

1. If Doppler does not survive hardening, start **Omarchy** with the bounded
   reset-state canary audit. Its freshness and zero-signal gate maximize the
   chance of an actionable first result.
2. If that source trace shows the reset baseline cannot preserve post-install
   state, rotate immediately to the **Chia 2.7.4 / chia-rs 0.48.0** differential.
3. Use **Netflix Atlas v1.8.2** only as the short route-to-sink falsifier; do not
   invest in parser fuzzing unless an external datasource URI is reachable.

