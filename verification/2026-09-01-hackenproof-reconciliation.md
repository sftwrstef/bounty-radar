# HackenProof and fresh-scope reconciliation — 2026-09-01

## Coverage health

- Saved digest: `15/18` successful source fetches.
- Degraded feeds: `broad-hackenproof-programs`, `hackenproof-audits`, and
  `hackenproof-programs`; each exceeded the configured 58-second browser wall
  timeout. This run therefore does not treat the saved digest as complete.
- Independent official-page reconciliation succeeded. The standing-program
  index reports `321 Results`. No program displayed a 1 September launch,
  smart-contract scope expansion, or reward increase; the newest visible
  standing update remains Chainstack on 31 August.
- The official audit index has one live entry, Zendex, ending 9 September. It
  is a DualDefense competition and is excluded from the regular-bounty queue.
- The local database recorded `24` source-item changes: 17 Bugcrowd, three
  HackerOne, two Intigriti, one YesWeHack, and one broad/ENS competition row.
  The observed differences are age/status-string churn, Web2/VDP programs, or
  a competition—not a fresh regular smart-contract scope delta.
- Telegram outbox pending count: `0`.

## Genuinely fresh Web3 delta

The only same-day deployed smart-contract delta surviving reconciliation is
Hyperlane Registry's NES route cutover:

- `c389e9fddb893fff07dba764df09c20d685b4648` redeployed the NES synthetics,
  moved the native leg from domain `41443` to Nesachain domain `41444`, and
  changed every route address.
- `a798db20785ae4f5c48a4acff377374d07359913` re-enabled `NES/bsc` in the
  Universal Router allowlist after that cutover.
- Registry head inspected: `49567fb8c22120a3f35008f84937d274aa41c1a4`.
- The Hyperlane SDK package release and Optimism `op-deployer/v0.8.0-rc.1`
  were not selected independently: the former is package/tooling change and
  the latter is release-candidate deployment tooling, not a proved live scoped
  contract deployment.

## Sole target

Selected `Hyperlane NES Warp route / regular Immunefi` for the bounded pass.
See `audit_targets/hyperlane-nes-warp-route-immunefi-20260901/HUNT_STATUS.md`.

