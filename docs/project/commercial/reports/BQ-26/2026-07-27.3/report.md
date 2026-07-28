# BQ-26 — Service capacity outlook for the remaining waves

_Demo sample data — not for clinical use._

**Verdict**: Capacity gap to hit the 2026-09-30 close — EMEA, NA STALLED (zero completions in the four weeks to 2026-07-27; EMEA needs 6.4/wk; NA needs 4.7/wk); APAC behind (3.5/wk vs 4.5/wk required); remote conversion covers 0 of 97 on-site-remaining devices today [derived: v-main] [src: commercial/internal-upgrade-campaign@2026-07-27] [src: commercial/internal-fleet@2026-07-27] [config: commercial.yml]

## Required vs current completion rate

_Anchor: 2026-07-27, the pinned snapshot's as-of date [src: commercial/internal-upgrade-campaign@2026-07-27]. Status sets: completed = `completed` | `completed-after-retry`; remaining = every other status (`scheduled` | `failed-pending-retry` | `rolled-back`); on-site-remaining = remaining rows with method `onsite`. Stall criterion, applied uniformly to every region: zero completions in the trailing four weeks with work remaining [derived: required-rate]._

| Region | Remaining | On-site rem. | Remote-convertible now | Current rate/wk | Required rate/wk | FSE-days left (labor-only) |
|---|---|---|---|---|---|---|
| APAC [derived: required-rate] [derived: remote-convertible] [src: commercial/internal-upgrade-campaign@2026-07-27] | 42 | 38 | 0 | 3.5 | 4.5 | 7.7 |
| EMEA — STALLED [derived: required-rate] [derived: remote-convertible] [src: commercial/internal-upgrade-campaign@2026-07-27] | 59 | 34 | 0 | 0.0 | 6.4 | 6.9 |
| NA — STALLED [derived: required-rate] [derived: remote-convertible] [src: commercial/internal-upgrade-campaign@2026-07-27] | 44 | 25 | 0 | 0.0 | 4.7 | 5.1 |

- Weekly completion trend per region is charted (zero-filled) — stalls are visible as flatlines [derived: weekly-trend] [src: commercial/internal-upgrade-campaign@2026-07-27]
- Remote-convertible = on-site-remaining devices whose fleet record is connected: 0 of 97 across all regions [derived: remote-convertible] [src: commercial/internal-fleet@2026-07-27]
- FSE-days = on-site-remaining × mean completed on-site duration (97.6 min, n=101) ÷ 480 min/day — labor time only, travel excluded (lower bound) [derived: fse-days-remaining] [src: commercial/internal-upgrade-campaign@2026-07-27] [config: commercial.yml]

## Anchor sensitivity (disclosed, not absorbed)

_Primary anchor 2026-07-27 (snapshot as-of) vs alternative 2026-07-18 (latest completion in the pin). The latest-completion anchor excludes trailing zero-completion days and is the optimistic choice [derived: anchor-sensitivity]._

| Region | Current rate/wk (as-of anchor) | Current (latest-completion anchor) | Required (as-of) | Required (latest-completion) |
|---|---|---|---|---|
| APAC [derived: anchor-sensitivity] | 3.5 | 4.5 | 4.5 | 4.0 |
| EMEA [derived: anchor-sensitivity] | 0.0 | 0.2 | 6.4 | 5.6 |
| NA [derived: anchor-sensitivity] | 0.0 | 0.0 | 4.7 | 4.2 |

- Verdict under the alternative anchor: CHANGES — anchor choice flips at least one region's shortfall classification; treat the capacity verdict as anchor-sensitive [derived: anchor-sensitivity].

## Assumptions & expectations — plan vs actual

_`unvalidated` means the expectation itself is a stand-in that has not been grounded
in a plan of record or the risk file — challenge the assumption, not just the actual._

| ID | Expectation | Expected | Actual | Verdict | Basis |
|---|---|---|---|---|---|
| E-26.1 | Existing field-service capacity absorbs the remaining waves without surge or slip [derived: required-rate] [derived: weekly-trend] [config: commercial.yml] | current run-rate >= required rate through 2026-09-30 in every region | EMEA: stalled (6.4/wk required); NA: stalled (4.7/wk required); APAC: 3.5/wk vs 4.5 required | not-met (unvalidated) | implicit in the wave plan; never validated against an FSE roster (dataset gap) |

## Narrative — Risks / Mitigations / Issues

### Issues (materialized — needs action)

- **I1 (high)** — EMEA wave is stalled under the uniform criterion — zero completions in the four weeks to 2026-07-27 (last completion 2026-06-22, 59 devices remaining, 6.4/wk now required) [src: commercial/internal-upgrade-campaign@2026-07-27] [derived: weekly-trend] [derived: required-rate]
  - _Action_: Re-engage site scheduling this week; re-baseline the wave or assign surge FSE capacity; confirm root cause (scheduling vs the failure cluster) [src: commercial/internal-upgrade-campaign@2026-07-27] [derived: weekly-trend] [derived: required-rate]
- **I2 (high)** — NA wave is stalled under the uniform criterion — zero completions in the four weeks to 2026-07-27 (last completion 2026-05-11, 44 devices remaining, 4.7/wk now required) [src: commercial/internal-upgrade-campaign@2026-07-27] [derived: weekly-trend] [derived: required-rate]
  - _Action_: Re-engage site scheduling this week; re-baseline the wave or assign surge FSE capacity; confirm root cause (scheduling vs the failure cluster) [src: commercial/internal-upgrade-campaign@2026-07-27] [derived: weekly-trend] [derived: required-rate]

### Risks (potential — mitigation identified)

- **R1 (medium)** — APAC misses the 2026-09-30 close at current rate (3.5/wk vs 4.5/wk required) [derived: required-rate] [derived: remote-convertible] [src: commercial/internal-upgrade-campaign@2026-07-27] [config: commercial.yml]
  - _Mitigation_: Add contract labor for the delta, convert connected on-site backlog to remote (0 devices convertible), or slip the close with customer notification [derived: required-rate] [derived: remote-convertible] [src: commercial/internal-upgrade-campaign@2026-07-27] [config: commercial.yml]
- **R2 (high)** — The remote-conversion recovery lever is sized at 0 of 97 on-site-remaining devices — the fleet connectivity join shows the on-site backlog is unconnected, so conversion first requires connectivity (adapters), it is not a scheduling change [derived: remote-convertible] [src: commercial/internal-upgrade-campaign@2026-07-27] [src: commercial/internal-fleet@2026-07-27]
  - _Mitigation_: Price the adapter retrofit against continued on-site visits (the BQ-30 upgrade-economics answer); otherwise the levers are contract labor or slip — noting the remote path carried the implicated failure mode (4 of 4 rollbacks were remote installs), so converted devices inherit that exposure until the failure cluster is resolved [derived: remote-convertible] [src: commercial/internal-upgrade-campaign@2026-07-27] [src: commercial/internal-fleet@2026-07-27]
- **R3 (medium)** — The hire/contract/slip decision is being made on run-rate projections plus a labor-time-only workload floor (19.7 FSE-days) — FSE roster, utilization, travel, and visits-per-day are not yet a corpus dataset [derived: fse-days-remaining] [derived: fse-capacity]
  - _Mitigation_: Acquire an internal service-roster dataset; until then treat capacity conclusions as directional [derived: fse-days-remaining] [derived: fse-capacity]

### Watch

- **W1 (medium)** — Completion-rate trend by region (weekly, zero-filled) — a flatline is a stall, not missing data [derived: weekly-trend]

## Data gap (stated, not papered over)

- Field-service-engineer roster, utilization, travel time, and visits-per-day are NOT yet
  a corpus dataset — the hire/contract/slip decision needs them. This outlook is a
  run-rate projection plus a labor-time-only workload floor [derived: fse-days-remaining];
  the FSE-capacity series stays marked unavailable.

## Method & provenance

- Remaining counts and durations measured from [src: commercial/internal-upgrade-campaign@2026-07-27]; connectivity joined from [src: commercial/internal-fleet@2026-07-27] by device_serial; close date, headroom guard, and FSE-day length [config: commercial.yml].
- Anchor convention: trailing 28-day window ends at the snapshot as-of date [derived: anchor-sensitivity]; the sensitivity table shows the alternative.
- Status sets (self-sufficient for re-derivation from the pin alone): completed = status `completed` or `completed-after-retry`; remaining = status `scheduled`, `failed-pending-retry`, or `rolled-back`; on-site-remaining = remaining with method `onsite` [src: commercial/internal-upgrade-campaign@2026-07-27].
