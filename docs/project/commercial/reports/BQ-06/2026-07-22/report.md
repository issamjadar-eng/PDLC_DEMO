# BQ-06 — Clearance cycle time: competitors vs our history

**Verdict**: Competitor 510(k) review runs a median 213 days received→decision across 29 infusion-pump clearances since 2021; fastest frequent filer is Baxter Healthcare Corporation at 74 days median [derived: v-main] [src: commercial/openfda-510k-infusion@2026-07-22]

## Review interval by frequent filer (public FDA dates)

| Applicant | Clearances | Median days received→decision | Evidence |
|---|---|---|---|
| Baxter Healthcare Corporation | 9 | 74 | [src: commercial/openfda-510k-infusion@2026-07-22] |
| Icu Medical, Inc. | 3 | 257 | [src: commercial/openfda-510k-infusion@2026-07-22] |
| Fresenius Kabi AG | 2 | 413.0 | [src: commercial/openfda-510k-infusion@2026-07-22] |
| Carefusion 303, Inc. | 2 | 474.5 | [src: commercial/openfda-510k-infusion@2026-07-22] |
| Repro-Medical System, Inc., Dba Koru Medical Systems | 2 | 162.0 | [src: commercial/openfda-510k-infusion@2026-07-22] |
| Zevex, Inc. | 2 | 139.0 | [src: commercial/openfda-510k-infusion@2026-07-22] |

- Overall: median 213 days across 29 clearances [derived: cycle-by-applicant] [src: commercial/openfda-510k-infusion@2026-07-22]

## Our own history (stated gap)

- Our program's K-numbers are demo-fabricated, so OUR received→decision intervals cannot be
  read from public data — the comparison's left side needs the internal regulatory log as a
  corpus dataset. The series is marked no-data rather than estimated.
- Note the metric's scope: received→decision measures FDA review, not develop-to-market —
  concept-pipeline conversion needs the internal concept register (also a stated gap).
- Historical view: median review interval per decision year is charted [derived: cycle-by-year] [src: commercial/openfda-510k-infusion@2026-07-22].

## Method & provenance

- Intervals computed from public `date_received` / `decision_date` in [src: commercial/openfda-510k-infusion@2026-07-22].
