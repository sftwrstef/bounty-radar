# HackenProof reconciliation verification — 2026-07-29 ET

Live official check: both `https://hackenproof.com/programs` and
`https://hackenproof.com/audit-programs` were independently opened. The audit
index exposed the LIVE `Push Chain Core Contracts SC DualDefense Audit` listing
at
`https://hackenproof.com/audit-programs/push-chain-core-contracts-sc-dualdefense-audit`.
Direct local HTTP remained Cloudflare-blocked (`403`, `cf-mitigated: challenge`).

## Regression command

```bash
./.venv/bin/python -B -u -m unittest discover -s tests -v
```

Result: `4` tests passed in `0.049s`. The tests cover official-listing detection,
false-empty degradation through the digest, and fallback record/digest behavior.

## Isolated fallback dry-run

```bash
radar_final_dry_run_dir="$(mktemp -d /tmp/bounty-radar-hackenproof-final.XXXXXX)"
./.venv/bin/python -B -u -m bounty_radar record-source hackenproof-audits \
  --title 'Push Chain Core Contracts SC DualDefense Audit' \
  --url 'https://hackenproof.com/audit-programs/push-chain-core-contracts-sc-dualdefense-audit' \
  --summary 'Official NEW/LIVE listing; up to $10,000' \
  --db "$radar_final_dry_run_dir/radar.sqlite" \
  --digest-dir "$radar_final_dry_run_dir/digests" \
  --no-alerts
# Repeat the identical record-source command once.
sqlite3 -header -column "$radar_final_dry_run_dir/radar.sqlite" \
  "select source_name, signal_key, occurrences from source_signals;"
rg -n 'Push Chain Core Contracts' "$radar_final_dry_run_dir"/digests/*.md
```

Result:

```text
dry_run_dir=/tmp/bounty-radar-hackenproof-final.brRHVB
first:  new=true,  alert_sent=false
second: new=false, alert_sent=false
source_signals.occurrences=2
digest_path=/tmp/bounty-radar-hackenproof-final.brRHVB/digests/2026-07-30.md
digest contains Push Chain Core Contracts SC DualDefense Audit
```

`--no-alerts` prevented a duplicate real listing alert during the dry-run.

## Independent Telegram delivery

```bash
perl -e 'alarm shift; exec @ARGV' 30 \
  ./.venv/bin/python -B -u -m bounty_radar check-telegram --send-test
```

Result:

```text
Telegram enabled: True
Sent Telegram test message
```
