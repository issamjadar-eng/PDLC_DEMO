# BQ-26 — Service capacity outlook for the remaining waves

_Demo sample data — not for clinical use._

**Verdict**: Capacity gap to hit the 2026-09-30 close — EMEA: needs 5.6/wk vs current 0.2/wk (34 on-site remaining); NA: needs 4.2/wk vs current 0.0/wk (25 on-site remaining) [derived: v-main] [src: commercial/internal-upgrade-campaign@2026-07-22.2] [config: commercial.yml]

## Required vs current completion rate

| Region | Remaining | Of which on-site | Current rate/wk | Required rate/wk | Evidence |
|---|---|---|---|---|---|
| APAC | 42 | 38 | 4.5 | 4.0 | [derived: required-rate] [src: commercial/internal-upgrade-campaign@2026-07-22.2] |
| EMEA | 59 | 34 | 0.2 | 5.6 | [derived: required-rate] [src: commercial/internal-upgrade-campaign@2026-07-22.2] |
| NA | 44 | 25 | 0.0 | 4.2 | [derived: required-rate] [src: commercial/internal-upgrade-campaign@2026-07-22.2] |

- Weekly completion trend per region is charted (zero-filled) — stalls are visible as flatlines [derived: weekly-trend] [src: commercial/internal-upgrade-campaign@2026-07-22.2]

## Assumptions & expectations — plan vs actual

_`unvalidated` means the expectation itself is a stand-in that has not been grounded
in a plan of record or the risk file — challenge the assumption, not just the actual._

| ID | Expectation | Expected | Actual | Verdict | Basis | Evidence |
|---|---|---|---|---|---|---|
| E-26.1 | Existing field-service capacity absorbs the remaining waves without surge or slip | current run-rate >= required rate through 2026-09-30 in every region | EMEA: 0.2/wk vs 5.6 required; NA: 0.0/wk vs 4.2 required | not-met (unvalidated) | implicit in the wave plan; never validated against an FSE roster (dataset gap) | [derived: required-rate] [config: commercial.yml] |

## Narrative — Risks / Mitigations / Issues

### Issues (materialized — needs action)

- **I1 (high)** — NA wave has stalled — zero completions in the trailing four weeks (last completion 2026-05-11) [src: commercial/internal-upgrade-campaign@2026-07-22.2] [derived: weekly-trend]
  - _Action_: Re-engage site scheduling this week; re-baseline the wave or assign surge FSE capacity; confirm root cause (scheduling vs the failure cluster) [src: commercial/internal-upgrade-campaign@2026-07-22.2] [derived: weekly-trend]

### Risks (potential — mitigation identified)

- **R1 (medium)** — EMEA misses the 2026-09-30 close at current rate (0.2/wk vs 5.6/wk required) [derived: required-rate] [src: commercial/internal-upgrade-campaign@2026-07-22.2] [config: commercial.yml]
  - _Mitigation_: Convert on-site backlog to remote where connected (34 on-site remaining), add contract labor for the delta, or slip the close with customer notification [derived: required-rate] [src: commercial/internal-upgrade-campaign@2026-07-22.2] [config: commercial.yml]
- **R2 (medium)** — The hire/contract/slip decision is being made on run-rate projections alone — FSE roster, utilization, and visits-per-day are not yet a corpus dataset [derived: fse-capacity]
  - _Mitigation_: Acquire an internal service-roster dataset; until then treat capacity conclusions as directional [derived: fse-capacity]

### Watch

- **W1 (medium)** — Completion-rate trend by region (weekly, zero-filled) — a flatline is a stall, not missing data [derived: weekly-trend]

## Data gap (stated, not papered over)

- Field-service-engineer roster, utilization, and visits-per-day are NOT yet a corpus
  dataset — the hire/contract/slip decision needs them. This outlook is a run-rate
  projection only [derived: required-rate]; the FSE-capacity series is marked unavailable.

## Method & provenance

- Remaining counts measured, rates derived from [src: commercial/internal-upgrade-campaign@2026-07-22.2]; close date and expectations [config: commercial.yml].
