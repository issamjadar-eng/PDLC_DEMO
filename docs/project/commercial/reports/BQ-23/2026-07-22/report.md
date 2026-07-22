# BQ-23 — Campaign coverage: planned vs actual

_Demo sample data — not for clinical use._

**Verdict**: Campaign C-2026-02 is 62.7% complete; at current run-rate EMEA, NA will miss the 2026-09-30 close [derived: v-main] [src: commercial/internal-upgrade-campaign@2026-07-22.2] [config: commercial.yml]

## Coverage by region

| Region | Target devices | Completed | Coverage | Weekly run-rate | Projected finish | Evidence |
|---|---|---|---|---|---|---|
| APAC | 76 | 34 | 44.7% | 4.5/wk | 2026-09-21 | [src: commercial/internal-upgrade-campaign@2026-07-22.2] [derived: projected-finish] |
| EMEA | 120 | 61 | 50.8% | 0.2/wk | 2031-01-25 | [src: commercial/internal-upgrade-campaign@2026-07-22.2] [derived: projected-finish] |
| NA | 193 | 149 | 77.2% | 0.0/wk | no-recent-completions | [src: commercial/internal-upgrade-campaign@2026-07-22.2] [derived: projected-finish] |

- Plan reference: campaign close 2026-09-30, coverage target 95% [config: commercial.yml]
- Run-rate window: 28 days ending 2026-07-18 (as-of = latest completion in the pinned snapshot) [derived: weekly-run-rate] [src: commercial/internal-upgrade-campaign@2026-07-22.2]

## Method & provenance

- Coverage counts measured from [src: commercial/internal-upgrade-campaign@2026-07-22.2] (statuses `completed`, `completed-after-retry`).
- Projected finish is derived: remaining ÷ trailing four-week completion rate — it
  assumes the recent rate holds [derived: projected-finish].
