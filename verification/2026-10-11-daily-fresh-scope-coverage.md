# 2026-10-11 daily fresh-scope coverage validation

Checked at approximately 2026-10-11 13:38-13:42 UTC.

## Coverage health

Today's radar digest and canonical SQLite database report **15/18** completed source fetches. Coverage is **DEGRADED**, not quiet:

- `broad-hackenproof-programs`: browser fetch exceeded the 58-second wall-clock timeout.
- `hackenproof-programs`: browser fetch exceeded the 58-second wall-clock timeout.
- `hackenproof-audits`: browser fetch exceeded the 58-second wall-clock timeout.

The digest contains no new repository signals. The database changes are mostly aggregator re-observations, relative-age changes, or previously consumed rows. Two records were new in the final 13:04 UTC scan:

- Vinted: aggregator snapshot changed the displayed maximum reward from `$4,000` to `$8,000`. The official Bugcrowd engagement redirected to an authentication page, so the governing reward, exact asset/impact delta, effective time, and participation terms are **UNKNOWN**. This is not promoted as a verified fresh target.
- Mateco VDP: the only snapshot difference was `Last changed 9 days ago` to `10 days ago`; it still advertised no paid bounty. This is normalized relative-age churn, not a material scope delta.

## Direct official HackenProof reconciliation

Both official indexes loaded read-only after the automated failures:

- [Standing programs](https://hackenproof.com/programs): Ult remained the newest visible standing launch, started 2026-09-28, with an advertised `$20,000` maximum. Its visible submission count was `88`; submission-count movement is churn, not scope expansion.
- [Audit programs](https://hackenproof.com/audit-programs): the index still showed `101` total and was led by Digital Oro (2026-10-05 through 2026-10-26, 21 visible submissions, `$3,000` maximum) and EverValue (2026-10-02 through 2026-10-16, 53 visible submissions, `$2,500` maximum). Digital Oro was already locally reviewed and parked.

No material new program, asset, deployment, reward, or scope change was affirmatively established from the visible official HackenProof listings. This bounded first-page reconciliation does not repair the automated failure or prove full-catalog and asset-level sameness. The official-page counts and submission increments are retained only to distinguish churn from scope change.

## Branch decision

Branch: **degraded coverage / queued target**.

The potential Vinted reward increase remains unverified because its official page was unavailable without authentication. Mateco is unpaid churn. A queued target may proceed only with independently verified current scope; Monero meets that condition through its first-party VRP, unchanged official repository pins, and the same-day active HackerOne delivery check preserved in its target dossier.

No login was completed, no program terms were accepted, and no enrollment, fee, report, target contact, public-system test, transaction, or disclosure occurred.

## Later signed-in Bugcrowd verification (16:34 UTC)

The earlier Vinted reward delta is now **verified from its [official active Bugcrowd brief](https://bugcrowd.com/engagements/vinted-uab-mbb) and [dated changelog](https://bugcrowd.com/engagements/vinted-uab-mbb/changelog/bd9c0d82-7ff5-4e80-bf9b-a8f337bb5550)**, viewed read-only under the already signed-in researcher account. The engagement is public, in progress, and last updated 2026-10-11 11:23:01 UTC. For the primary group, P1 increased from $2,000–$4,000 to $3,800–$8,000 and P2 from $800–$1,500 to $1,200–$3,000; P3 remains $200–$500. Listed primary targets are `www.vinted.com`, `www.vinted.net`, `www.vintedgo.com`, and the named iOS/Android apps. All other subdomains are out of scope unless individually listed in the secondary group. The program uses production targets, restricts testing to researcher-owned accounts/listings/orders, and says low-effort or AI-generated reports without meaningful human analysis are rejected. No testing, account creation, enrollment, terms acceptance, report, or contact occurred. This is a verified fresh **program/reward signal**, not a vulnerability or authorization to test production.
