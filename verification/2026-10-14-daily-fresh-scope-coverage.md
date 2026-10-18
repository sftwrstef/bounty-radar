# Daily fresh-scope coverage — 2026-10-14

Reviewed: 2026-10-14 09:39 EDT.

## Coverage health

- Radar digest generated at `2026-10-14T13:05:33Z`.
- Coverage was **degraded: 15/18**.
- Failed sources: `broad-hackenproof-programs`, `hackenproof-programs`, and
  `hackenproof-audits`; each exceeded the 58-second browser-fetch limit.
- A failed source is UNKNOWN coverage, not a quiet source.

## Bounded official reconciliation

- A direct official `GET https://hackenproof.com/programs/` returned HTTP 200
  and included **ZMO Exchange** as a NEW entry dated 14 Oct 2026. The official
  program page independently shows the program active, Web/CEX scope at
  `https://www.zmo.com` and `*.zmo.com`, zero submissions, a `$50-$2,000`
  reward table including Medium, a required PoC, and a 150-reputation gate.
- A direct official `GET https://hackenproof.com/audit-programs/` returned HTTP
  200. The index remains at **102** entries (19 Contest, 83 Dual Defense) and is
  still led by DreamX, followed by Digital Oro and EverValue. No new audit row
  displaced the 2026-10-12 DreamX entry.
- This direct check establishes the ZMO launch and the visible audit-index
  head. It does not repair the three failed radar lanes or prove complete
  equality of every historical row.

## Database delta classification

- `hackenproof-programs`: ZMO Exchange is a genuine `source_launch`, verified
  by the official fallback.
- `broad-bountyhunters-recent`: SP1 is new to that feed but launched on
  2026-09-21; it is not a 2026-10-14 program launch.
- Revert, Cantina countdowns, Bugcrowd/HackerOne/Intigriti relative ages, and
  the Govware countdown are presentation churn, not verified scope changes.
- No other authoritative asset, reward, deployment, or scope delta was
  established in the bounded reconciliation.

## Routing result

Branch: **degraded coverage with a separately verified fresh program**.

ZMO was considered first because it is the only verified fresh launch. It is
not executable inside this automation: the program exposes only production Web
assets, says locally hosted PoCs are not allowed, provides no source or staging
fixture, and this automation forbids public-deployment testing. ZMO is therefore
`BLOCKED` before diagnostics, not falsified or exhausted. The run then resumed
the strongest independently scope-verifiable queued survivor, Extra Finance
XLend.

