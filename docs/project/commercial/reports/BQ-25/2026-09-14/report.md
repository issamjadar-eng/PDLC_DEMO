# BQ-25 — Customer struggle & customer cost

_Demo sample data — not for clinical use._

**Verdict**: Tickets per 100 attempted upgrades are highest in NA at 21.7; 4 site(s) rolled back; estimated customer-side cost of the on-site portion so far $7,272–$16,412 [derived: v-main] [src: commercial/internal-upgrade-campaign@2026-09-14] [assume: A-002]

## Tickets per 100 attempted upgrades

_Basis: attempted devices (excludes still-scheduled) for both tickets and denominator —
a consistent basis per the adversarial-verification finding._

| Region | Attempted | Tickets | Tickets per 100 |
|---|---|---|---|
| APAC [src: commercial/internal-upgrade-campaign@2026-09-14] | 34 | 6 | 17.6 |
| EMEA [src: commercial/internal-upgrade-campaign@2026-09-14] | 65 | 14 | 21.5 |
| NA [src: commercial/internal-upgrade-campaign@2026-09-14] | 152 | 33 | 21.7 |

- By method: remote 22.3 vs onsite 19.4 tickets/100 [derived: tickets-by-method] [src: commercial/internal-upgrade-campaign@2026-09-14]
- Rollback sites: S-EMEA-15, S-NA-13, S-NA-18, S-NA-23 [derived: rollback-sites] [src: commercial/internal-upgrade-campaign@2026-09-14]

## Customer cost of taking the update (stated assumption)

- Customer-side biomed effort and rates are NOT in our systems. The estimated range of $7,272–$16,412 for 101 completed on-site updates rests entirely on [assume: A-002] (modeled hours-per-device × benchmark labor rate; confidence: low).

## Method & provenance

- Ticket and rollback counts measured from [src: commercial/internal-upgrade-campaign@2026-09-14].
- Customer cost is an assumed estimate [assume: A-002] — revisit when reference-account
  validation lands (A-002 refresh trigger).
