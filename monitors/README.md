# Focused bounty monitors

## Chainlink CCIP v2 USDC

`chainlink_ccip_v2_usdc.py` watches the official Chainlink documentation data
for the first public v2.0.0 lane that lists USDC. It cross-references token pool
metadata, records a local deduplication snapshot, and emits an alert when:

- a new v2 USDC lane appears;
- both endpoints become `USDCTokenPoolProxy 2.0.0` candidates;
- a previously disabled inbound limiter becomes enabled; or
- either USDC pool address changes.

Run from the repository root:

```bash
./.venv/bin/python -B monitors/chainlink_ccip_v2_usdc.py --json
```

The state file is `data/chainlink_ccip_v2_usdc_watch.json`. A nonzero exit means
coverage is degraded; it must not be interpreted as a quiet pass.

Actionable lane deltas are also retained in `reopen_checks` until an onchain
review explicitly records `REOPEN`, `RE-PARK`, or `KILL`. Route deduplication
therefore suppresses duplicate Telegram alerts without losing unfinished work.
Resolve a completed check with:

```bash
./.venv/bin/python -B monitors/chainlink_ccip_v2_usdc.py \
  --resolve-route 'source-chain|destination-chain' \
  --resolution RE-PARK \
  --resolution-note 'CCV only; no siloed lock/release child' \
  --json
```

The alert is a reopen trigger, not automatic submission authorization. Confirm
the proxy child pools, mechanism history, excluded in-flight USDC, and both
child rate-limit buckets onchain before recommending submission.

## Robinhood Stock permit domains

`robinhood_stock_permit_domains.py` reconstructs every canonical Robinhood
Stock proxy from Factory events and preserves its ordered EIP-712 domain
separators. It emits a review alert when a proxy returns to an older separator
after an intervening different state, or when an upgrade, role change,
unexpected initializer/domain event, implementation pointer, chain ID, or
runtime-code delta changes the domain-control boundary.

Run from the repository root:

```bash
./.venv/bin/python -B monitors/robinhood_stock_permit_domains.py check
```

The state file is `data/robinhood_stock_permit_domains_watch.json`; security
alerts are appended to `data/robinhood_stock_permit_domain_alerts.jsonl`.
Initialize the reviewed baseline explicitly once with:

```bash
./.venv/bin/python -B monitors/robinhood_stock_permit_domains.py bootstrap
```

`check` refuses to create a missing baseline. A nonzero exit or
`coverage_ok: false` means coverage is degraded and must never be treated as a
quiet pass.

The monitor uses a 128-block confirmation buffer so current EIP-5267 state
remains available from Robinhood's aggressively pruned public RPC. The state
stores the cursor block hash and refuses to advance across a detected reorg.
Run it every three minutes so an implementation transition can be captured
before recent contract state is pruned. The monitor refuses to advance when
the cursor gap exceeds 4,500 blocks; that degraded result requires manual
review instead of being treated as a quiet catch-up.

Every run reads the raw separator and full EIP-5267 tuple from all known Stock
proxies at one canonical block hash. Existing proxy topology is indirectly
covered by this fleet-wide authority sweep plus representative runtime and
implementation anchors; every new proxy additionally gets a direct beacon-slot
and runtime-code check. Any implementation/control alert requires manual review
even when the final separator is unchanged, because multiple transitions in a
single block cannot be reconstructed from the ending state alone.

An alert is a triage trigger, not automatic submission authorization. Recheck
the permit nonce and deadline, economically untrusted reachability, incremental
harm beyond the holder's original authorization, current scope, and collision
posture before promoting the lane.
