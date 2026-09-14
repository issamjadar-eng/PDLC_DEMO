# BQ-06 — Clearance cycle time: competitors vs our history

**Verdict**: Competitor 510(k) review runs a median 214.0 days received→decision across 30 infusion-pump clearances since 2021; fastest frequent filer is Baxter Healthcare Corporation at 74 days median [derived: v-main] [src: commercial/openfda-510k-infusion@2026-09-14]

## Review interval by frequent filer (public FDA dates)

| Applicant | Clearances | Median days received→decision |
|---|---|---|
| Baxter Healthcare Corporation [src: commercial/openfda-510k-infusion@2026-09-14] | 9 | 74 |
| Icu Medical, Inc. [src: commercial/openfda-510k-infusion@2026-09-14] | 3 | 257 |
| Zevex, Inc. [src: commercial/openfda-510k-infusion@2026-09-14] | 2 | 139.0 |
| Carefusion 303, Inc. [src: commercial/openfda-510k-infusion@2026-09-14] | 2 | 474.5 |
| Fresenius Kabi AG [src: commercial/openfda-510k-infusion@2026-09-14] | 2 | 413.0 |
| Repro-Medical System, Inc., Dba Koru Medical Systems [src: commercial/openfda-510k-infusion@2026-09-14] | 2 | 162.0 |

- Overall: median 214.0 days across 30 clearances [derived: cycle-by-applicant] [src: commercial/openfda-510k-infusion@2026-09-14]

## Our own history (stated gap)

- Our program's K-numbers are demo-fabricated, so OUR received→decision intervals cannot be
  read from public data — the comparison's left side needs the internal regulatory log as a
  corpus dataset. The series is marked no-data rather than estimated.
- Note the metric's scope: received→decision measures FDA review, not develop-to-market —
  concept-pipeline conversion needs the internal concept register (also a stated gap).
- Historical view: median review interval per decision year is charted [derived: cycle-by-year] [src: commercial/openfda-510k-infusion@2026-09-14].

## Method & provenance

- Intervals computed from public `date_received` / `decision_date` in [src: commercial/openfda-510k-infusion@2026-09-14].
