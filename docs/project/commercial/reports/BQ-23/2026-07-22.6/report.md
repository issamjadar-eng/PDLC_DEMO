# BQ-23 — Campaign coverage: planned vs actual

_Demo sample data — not for clinical use._

**Verdict**: Campaign C-2026-02 is 62.7% complete; at current run-rate EMEA, NA will miss the 2026-09-30 close [derived: v-main] [src: commercial/internal-upgrade-campaign@2026-07-22.2] [config: commercial.yml]

## Coverage by region

| Region | Target devices | Completed | Coverage | Weekly run-rate | Projected finish |
|---|---|---|---|---|---|
| APAC [src: commercial/internal-upgrade-campaign@2026-07-22.2] [derived: projected-finish] | 76 | 34 | 44.7% | 4.5/wk | 2026-09-21 |
| EMEA [src: commercial/internal-upgrade-campaign@2026-07-22.2] [derived: projected-finish] | 120 | 61 | 50.8% | 0.2/wk | 2031-01-25 |
| NA [src: commercial/internal-upgrade-campaign@2026-07-22.2] [derived: projected-finish] | 193 | 149 | 77.2% | 0.0/wk | no-recent-completions |

- Plan reference: campaign close 2026-09-30, coverage target 95% [config: commercial.yml]
- Run-rate window: 28 days ending 2026-07-18 (as-of = latest completion in the pinned snapshot) [derived: weekly-run-rate] [src: commercial/internal-upgrade-campaign@2026-07-22.2]
- Cumulative coverage trend per region is charted weekly toward the 95% target [derived: cumulative-coverage] [config: commercial.yml]

## Assumptions & expectations — plan vs actual

_`unvalidated` means the expectation itself is a stand-in that has not been grounded
in a plan of record or the risk file — challenge the assumption, not just the actual._

| ID | Expectation | Expected | Actual | Verdict | Basis |
|---|---|---|---|---|---|
| E-23.1 | Campaign C-2026-02 reaches 95% coverage by the close date [derived: projected-finish] [derived: coverage-by-region] [config: commercial.yml] | 95% by 2026-09-30 | 62.7% coverage as of the pin; projected finishes: APAC 2026-09-21, EMEA 2031-01-25, NA no-recent-completions | not-met (unvalidated) | demo stand-in for the campaign plan of record [VERIFY] |
| E-23.2 | Every region sustains a completion run-rate sufficient to finish its wave [derived: weekly-run-rate] [config: commercial.yml] | run-rate >= required rate in each region | APAC: 4.5/wk, EMEA: 0.2/wk, NA: 0.0/wk | not-met (unvalidated) | implied by the wave schedule; never explicitly capacity-planned |

## Narrative — Risks / Mitigations / Issues

### Issues (materialized — needs action)

- **I1 (high)** — NA has zero completions in the trailing four-week window with 44 devices remaining — the wave is stalled, not slow [derived: projected-finish] [src: commercial/internal-upgrade-campaign@2026-07-22.2]
  - _Action_: Confirm scheduling vs technical root cause with the regional service lead; restart the wave or formally re-baseline [derived: projected-finish] [src: commercial/internal-upgrade-campaign@2026-07-22.2]

### Risks (potential — mitigation identified)

- **R1 (medium)** — EMEA projects to finish 2031-01-25, past the 2026-09-30 close (59 remaining at 0.2/wk) [derived: projected-finish] [config: commercial.yml]
  - _Mitigation_: Raise the completion rate (remote conversion, surge capacity) or re-baseline the close with customer notification — see the capacity outlook answer for the required-rate math [derived: projected-finish] [config: commercial.yml]

### Watch

- **W1 (medium)** — APAC on track (2026-09-21 projected vs 2026-09-30 close) — verify weekly [derived: projected-finish]

## Method & provenance

- Coverage counts measured from [src: commercial/internal-upgrade-campaign@2026-07-22.2] (statuses `completed`, `completed-after-retry`).
- Projected finish is derived: remaining ÷ trailing four-week completion rate — it
  assumes the recent rate holds [derived: projected-finish].
