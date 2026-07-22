# BQ-24 — Update failure clusters & the pause trigger

_Demo sample data — not for clinical use._

**Verdict**: PAUSE TRIGGER: cohort hw B upgrading from 3.1.2 fails on 31.4% of attempted devices (threshold 15.0%) — pause the wave for this cohort and escalate [derived: v-main] [src: commercial/internal-upgrade-campaign@2026-07-22.2] [config: commercial.yml]

## Attempt-failure rate by cohort (hw rev × from-version)

_Primary metric is per **attempted** device (excludes still-scheduled); the whole-cohort
rate is shown for context — including never-attempted devices understates severity
(adversarial-verification finding)._

| Cohort | Devices | Attempted | Failures | Per-attempt rate | Whole-cohort rate | Evidence |
|---|---|---|---|---|---|---|
| hw A / from 3.1.2 | 98 | 65 | 6 | 9.2% | 6.1% | [src: commercial/internal-upgrade-campaign@2026-07-22.2] |
| hw A / from 3.2.0 | 148 | 88 | 3 | 3.4% | 2.0% | [src: commercial/internal-upgrade-campaign@2026-07-22.2] |
| hw B / from 3.1.2 | 52 | 35 | 11 | 31.4% ⚠️ | 21.2% | [src: commercial/internal-upgrade-campaign@2026-07-22.2] |
| hw B / from 3.2.0 | 91 | 63 | 4 | 6.3% | 4.4% | [src: commercial/internal-upgrade-campaign@2026-07-22.2] |

- Overall per-attempt failure rate: 9.6% [derived: failure-by-cohort] [src: commercial/internal-upgrade-campaign@2026-07-22.2]
- Pause rule: per-attempt cohort rate > 15.0% with attempted n ≥ 20 [config: commercial.yml]

## Method & provenance

- Attempt failure = status in `completed-after-retry`, `failed-pending-retry`, `rolled-back`,
  measured from [src: commercial/internal-upgrade-campaign@2026-07-22.2].
