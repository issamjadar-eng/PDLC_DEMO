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

## Assumptions & expectations — plan vs actual

_`unvalidated` means the expectation itself is a stand-in that has not been grounded
in a plan of record or the risk file — challenge the assumption, not just the actual._

| ID | Expectation | Expected | Actual | Verdict | Basis | Evidence |
|---|---|---|---|---|---|---|
| E-24.1 | No cohort's per-attempt failure rate exceeds the pause threshold | <= 15% per attempted device (cohort n >= 20) | worst cohort 31.4% (hw B / from 3.1.2) | not-met (unvalidated) | demo stand-in for an engineering quality threshold [VERIFY] — not yet derived from the risk file | [derived: failure-by-cohort] [config: commercial.yml] |

## Narrative — Risks / Mitigations / Issues

### Issues (materialized — needs action)

- **I1 (high)** — Cohort hw B / from 3.1.2 fails on 31.4% of attempted devices (11 of 35) — above the pause threshold [derived: failure-by-cohort] [src: commercial/internal-upgrade-campaign@2026-07-22.2] [config: commercial.yml]
  - _Action_: Pause the wave for this cohort; open an engineering investigation on the hw-rev × firmware interaction; resume only with a fixed package or a cohort-specific procedure

### Risks (potential — mitigation identified)

- **R1 (medium)** — The pause threshold itself is a demo stand-in — not derived from the risk file, so the trigger level is unvalidated [config: commercial.yml]
  - _Mitigation_: Derive the threshold from the risk file's acceptability criteria and record it as a validated expectation

## Method & provenance

- Attempt failure = status in `completed-after-retry`, `failed-pending-retry`, `rolled-back`,
  measured from [src: commercial/internal-upgrade-campaign@2026-07-22.2].
