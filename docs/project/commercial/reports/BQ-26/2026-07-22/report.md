# BQ-26 — Service capacity outlook for the remaining waves

_Demo sample data — not for clinical use._

**Verdict**: Capacity gap to hit the 2026-09-30 close — EMEA: needs 5.6/wk vs current 0.2/wk (34 on-site remaining); NA: needs 4.2/wk vs current 0.0/wk (25 on-site remaining) [derived: v-main] [src: commercial/internal-upgrade-campaign@2026-07-22.2] [config: commercial.yml]

## Required vs current completion rate

| Region | Remaining | Of which on-site | Current rate/wk | Required rate/wk | Evidence |
|---|---|---|---|---|---|
| APAC | 42 | 38 | 4.5 | 4.0 | [derived: required-rate] [src: commercial/internal-upgrade-campaign@2026-07-22.2] |
| EMEA | 59 | 34 | 0.2 | 5.6 | [derived: required-rate] [src: commercial/internal-upgrade-campaign@2026-07-22.2] |
| NA | 44 | 25 | 0.0 | 4.2 | [derived: required-rate] [src: commercial/internal-upgrade-campaign@2026-07-22.2] |

## Data gap (stated, not papered over)

- Field-service-engineer roster, utilization, and visits-per-day are NOT yet a corpus
  dataset — the hire/contract/slip decision needs them. This outlook is a run-rate
  projection only [derived: required-rate]; the FSE-capacity series is marked unavailable.

## Method & provenance

- Remaining counts measured, rates derived from [src: commercial/internal-upgrade-campaign@2026-07-22.2]; close date [config: commercial.yml].
