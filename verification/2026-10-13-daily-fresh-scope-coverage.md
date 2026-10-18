# 2026-10-13 daily fresh-scope coverage

Review window: 2026-10-13 13:35–13:45 UTC.

## Automated coverage

The canonical command completed with exit code `0` and rewrote
[`digests/2026-10-13.md`](../digests/2026-10-13.md):

```sh
./.venv/bin/python -B -u -m bounty_radar scan --progress --json
```

Coverage was **15/18**, so this run is degraded rather than quiet. The three failed
sources were:

- `broad-hackenproof-programs`: browser fetch exceeded the 58,000 ms wall-clock timeout;
- `hackenproof-programs`: browser fetch exceeded the 58,000 ms wall-clock timeout; and
- `hackenproof-audits`: browser fetch exceeded the 58,000 ms wall-clock timeout.

The scan emitted one internal source-delta alert for Mateco. Its exact database
change is only `Last changed 11 days ago` to `12 days ago`; the asset count remained
89 and the listed reward remained `No paid bounty (VDP)`. The current official
Intigriti page independently confirms that Mateco is an open public VDP with no
monetary bounty. Savvas is new to the feed but is likewise listed as an unpaid VDP.
The other apparent changes are relative-date/countdown or submission-count churn.

## Bounded official reconciliation

- [HackenProof programs](https://hackenproof.com/programs) remains led by Ult
  (started 2026-09-28), followed by Hotcoin and Hinkal on the visible first page.
  The index exposes 33 pages. No newer visible paid launch was established.
- [HackenProof audit programs](https://hackenproof.com/audit-programs) currently
  reports 102 programs and remains led by DreamX (started 2026-10-12), Digital Oro
  (2026-10-05), and EverValue (2026-10-02). Yesterday's bounded record said 101;
  the exact added historical row is **UNKNOWN** because the owning automated lane
  failed and the visible newest row is unchanged. This count discrepancy is not
  promoted as a fresh eligible target or as repaired full-index coverage.

## Verified fresh delta used for routing

The official Immunefi catalog changed Optimism's `updatedDate` from
`2026-09-01T16:28:12.432Z` to `2026-10-13T10:50:37.987Z` and added Blockchain/DLT
impact `6396`, **High — Malicious sequencer/batcher stealing user funds**. The
current catalog file SHA-256 is
`30ab627d1adbd5a73d96318308d543fa0e4cab26deb080a0bb2ce45d582e5c99`.
This authoritative scope delta routed the run to Optimism despite degraded
HackenProof coverage.

Disposition: **degraded-coverage / verified fresh-delta branch**. Full HackenProof
catalog sameness remains UNKNOWN. No production testing, login, enrollment, fee,
submission, project contact, signature, or transaction occurred.
