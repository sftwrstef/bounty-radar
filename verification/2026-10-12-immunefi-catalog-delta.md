# Immunefi official-catalog delta — 2026-10-12

Read-only fetch at `2026-10-12T14:39:03Z` from the official
[`bounties.json`](https://immunefi.com/public-api/bounties.json):

- bytes: `6,460,542`
- SHA-256: `92af204502a95330c644cf0a888f33dee2fa02989af70ac8147aacac1143c9a2`
- prior preserved October 10/11 baseline: `6,460,188` bytes,
  `fb1f931ff1c979097ea625247f800149c2519fafe61ff17448a520eeb9a0d32f`

The program set is unchanged. Three records differ:

1. **Enzyme Onyx:** one asset row was added, ID `101352`, pointing to
   `SyncRedeemHandler.sol` at pin
   `d8a522d6ca58af9dbb831dad2b8045a88952e468` in `protocol-onyx`. The prior
   catalog already contained the same file and pin through a mistaken
   `protocol-onyx-dev` URL (ID `101351`). This is a URL/source-repository
   correction, not a new code revision or deployment delta. The existing
   October 11 nested-redemption diagnostic already uses this handler family.
2. **Twyne:** `updatedDate` and reward-row IDs changed; severities and payout
   amounts are identical. No asset or impact changed.
3. **Babylon Labs:** `isPaused` changed from false to true.

Disposition: **verified catalog delta, no queue-changing fresh code asset.**
Do not route Enzyme ahead of a stronger distinct candidate solely because its
duplicate source URL was corrected. Preserve Babylon as paused and Twyne as a
non-semantic reward-row refresh.

No login, enrollment, target contact, transaction, fee, report, or submission
occurred.

