# MQ-08 — Validation and calibration posture; PP3500 rev C release blockers

_Demo sample data — not for clinical use._

**Verdict**: At 2026-08-31: 10 overdue and 6 due-within-30-day items across 155 register entries; overdue calibrations Eastbrook 1, Westfield 9 — the cluster is at Westfield; PP3500 rev C release blockers: 3 validation item(s) not validated (PQ in-progress due 2026-09-30, PQ in-progress due 2026-09-30, OQ not-started due 2026-10-15) and 4 DHR-incomplete lot(s); 65 rev C lots already released since 2026-03-25 while the fixture PQ is still in-progress [derived: v-main] [src: manufacturing/internal-process-validation@2026-10-05] [src: manufacturing/internal-production-lots@2026-10-05] [config: manufacturing.yml]

## Headline

- Register statuses are read as recorded at the snapshot as-of 2026-08-31; days overdue = due date vs as-of; the due-soon window is 30 days [src: manufacturing/internal-process-validation@2026-10-05] [config: manufacturing.yml].
- Overdue 10, due soon 6, in progress / not started 3 of 155 entries [derived: posture-stat] [src: manufacturing/internal-process-validation@2026-10-05].

## By site

| Site | Overdue | Due soon | Entries |
|---|---|---|---|
| Eastbrook [src: manufacturing/internal-process-validation@2026-10-05] | 1 | 3 | 77 |
| Westfield [src: manufacturing/internal-process-validation@2026-10-05] | 9 | 3 | 78 |

## By record type

| Type | Overdue | Due soon | Entries |
|---|---|---|---|
| IQ [src: manufacturing/internal-process-validation@2026-10-05] | 0 | 0 | 22 |
| OQ [src: manufacturing/internal-process-validation@2026-10-05] | 0 | 0 | 23 |
| PQ [src: manufacturing/internal-process-validation@2026-10-05] | 0 | 0 | 22 |
| calibration [src: manufacturing/internal-process-validation@2026-10-05] | 10 | 0 | 68 |
| preventive-maintenance [src: manufacturing/internal-process-validation@2026-10-05] | 0 | 6 | 20 |

## By product line

| Product line | Overdue | Due soon | Entries |
|---|---|---|---|
| IP5000 [src: manufacturing/internal-process-validation@2026-10-05] | 1 | 0 | 6 |
| PP3000 [src: manufacturing/internal-process-validation@2026-10-05] | 0 | 0 | 13 |
| PP3500 [src: manufacturing/internal-process-validation@2026-10-05] | 3 | 0 | 47 |
| SP6000 [src: manufacturing/internal-process-validation@2026-10-05] | 1 | 0 | 14 |
| SP6500 [src: manufacturing/internal-process-validation@2026-10-05] | 2 | 0 | 13 |
| shared [src: manufacturing/internal-process-validation@2026-10-05] | 3 | 6 | 62 |

## Overdue calibrations

| Asset | Site | Product line | Due | Days overdue |
|---|---|---|---|---|
| precision balance #04 [src: manufacturing/internal-process-validation@2026-10-05] | Eastbrook | IP5000 | 2026-07-12 | 50 |
| thermocouple set #06 [src: manufacturing/internal-process-validation@2026-10-05] | Westfield | SP6500 | 2026-05-02 | 121 |
| torque driver #01 [src: manufacturing/internal-process-validation@2026-10-05] | Westfield | shared | 2026-05-13 | 110 |
| leak tester reference #05 [src: manufacturing/internal-process-validation@2026-10-05] | Westfield | PP3500 | 2026-05-24 | 99 |
| caliper #07 [src: manufacturing/internal-process-validation@2026-10-05] | Westfield | shared | 2026-06-02 | 90 |
| electrical safety analyzer #08 [src: manufacturing/internal-process-validation@2026-10-05] | Westfield | PP3500 | 2026-06-03 | 89 |
| syringe pump reference #09 [src: manufacturing/internal-process-validation@2026-10-05] | Westfield | PP3500 | 2026-06-13 | 79 |
| precision balance #04 [src: manufacturing/internal-process-validation@2026-10-05] | Westfield | SP6000 | 2026-07-07 | 55 |
| flow meter reference #03 [src: manufacturing/internal-process-validation@2026-10-05] | Westfield | shared | 2026-08-05 | 26 |
| digital pressure gauge #02 [src: manufacturing/internal-process-validation@2026-10-05] | Westfield | SP6500 | 2026-08-10 | 21 |

## PP3500 rev C release blockers

### Validation side

| Asset / process | Type | Site | Status | Due | Owner |
|---|---|---|---|---|---|
| final functional test fixture rev C [src: manufacturing/internal-process-validation@2026-10-05] | PQ | Eastbrook | in-progress | 2026-09-30 | quality |
| final functional test fixture rev C [src: manufacturing/internal-process-validation@2026-10-05] | PQ | Westfield | in-progress | 2026-09-30 | quality |
| occlusion pressure test process rev C [src: manufacturing/internal-process-validation@2026-10-05] | OQ | Westfield | not-started | 2026-10-15 | manufacturing-engineering |

### Lot side

- PP3500 rev C lots in the pinned records: 78 — released 65 (first release 2026-03-25), in process 9, DHR-incomplete (blocked) 4 [derived: revc-lots] [src: manufacturing/internal-production-lots@2026-10-05].
- Blocked: LOT-2026-0188 — Eastbrook, test, started 2026-06-21 [src: manufacturing/internal-production-lots@2026-10-05]
- Blocked: LOT-2026-0223 — Eastbrook, test, started 2026-07-20 [src: manufacturing/internal-production-lots@2026-10-05]
- Blocked: LOT-2026-0231 — Westfield, final-assembly, started 2026-07-10 [src: manufacturing/internal-production-lots@2026-10-05]
- Blocked: LOT-2026-0236 — Westfield, pack, started 2026-07-23 [src: manufacturing/internal-production-lots@2026-10-05]

## Assumptions & expectations — plan vs actual

_`unvalidated` means the expectation itself is a stand-in that has not been grounded
in a plan of record, a procedure, or the risk file — challenge the assumption, not just the actual._

| ID | Expectation | Expected | Actual | Verdict | Basis |
|---|---|---|---|---|---|
| E-08.1 | No production measuring equipment is past its calibration due date [derived: overdue-calibrations] [config: manufacturing.yml] | 0 overdue calibrations | 10 overdue calibration(s) at 2026-08-31 (Eastbrook 1, Westfield 9) | not-met (unvalidated) | stand-in; the calibration procedure on record is not distilled in this project's sources [VERIFY] |
| E-08.2 | PP3500 rev C lots are released only after the rev C test-fixture PQ is complete [derived: revc-blockers] [derived: revc-lots] [config: manufacturing.yml] | PQ validated before the first rev C release | 2 rev C fixture PQ record(s) in-progress; 65 rev C lots released since 2026-03-25 | not-met (unvalidated) | stand-in; the design-transfer plan's validation-before-release gate is not distilled in this project's sources [VERIFY] |

## Narrative — Risks / Mitigations / Issues

### Issues (materialized — needs action)

- **I1 (high)** — 10 calibrations overdue (Eastbrook 1, Westfield 9); the oldest is 121 d past due — measurements taken with out-of-calibration equipment put the affected lot records in question [derived: overdue-calibrations] [src: manufacturing/internal-process-validation@2026-10-05]
  - _Action_: Pull the overdue instruments from use, assess impact on lots measured since the due date, and re-baseline the metrology schedule at the affected site [derived: overdue-calibrations] [src: manufacturing/internal-process-validation@2026-10-05]
- **I2 (medium)** — 4 PP3500 rev C lot(s) cannot be released because the device history record is incomplete: LOT-2026-0188 (Eastbrook, test, started 2026-06-21), LOT-2026-0223 (Eastbrook, test, started 2026-07-20), LOT-2026-0231 (Westfield, final-assembly, started 2026-07-10), LOT-2026-0236 (Westfield, pack, started 2026-07-23) [derived: revc-lots] [src: manufacturing/internal-production-lots@2026-10-05]
  - _Action_: Close the DHR gaps (missing records / signatures) and release, or disposition through an NCR [derived: revc-lots] [src: manufacturing/internal-production-lots@2026-10-05]

### Risks (potential — mitigation identified)

- **R1 (high)** — 65 PP3500 rev C lots have been released since 2026-03-25 while 3 rev C validation item(s) remain open: final functional test fixture rev C PQ (in-progress, due 2026-09-30, Eastbrook), final functional test fixture rev C PQ (in-progress, due 2026-09-30, Westfield), occlusion pressure test process rev C OQ (not-started, due 2026-10-15, Westfield) — the register does not record which fixture tested each lot, so whether those lots ran on the validated rev B fixture or the unvalidated rev C fixture is not determinable from these data [derived: revc-blockers] [derived: revc-lots] [src: manufacturing/internal-process-validation@2026-10-05] [src: manufacturing/internal-production-lots@2026-10-05]
  - _Mitigation_: Confirm the test-fixture routing for released rev C lots from the DHRs; if any ran on the rev C fixture before PQ completion, open a CAPA and assess the released units [derived: revc-blockers] [derived: revc-lots] [src: manufacturing/internal-process-validation@2026-10-05] [src: manufacturing/internal-production-lots@2026-10-05]

### Watch

- **W1 (medium)** — 6 item(s) fall due within 30 days of 2026-08-31: HVAC cleanroom unit (preventive-maintenance, Eastbrook, due 2026-09-02), SMT pick-and-place (preventive-maintenance, Westfield, due 2026-09-08), compressed-air dryer (preventive-maintenance, Westfield, due 2026-09-10), ultrasonic welder (preventive-maintenance, Westfield, due 2026-09-10), conveyor (preventive-maintenance, Eastbrook, due 2026-09-21), pouch sealer (preventive-maintenance, Eastbrook, due 2026-09-25) [derived: posture-by-site] [src: manufacturing/internal-process-validation@2026-10-05] [config: manufacturing.yml]
- **W2 (medium)** — Posture history is not available: this is a single snapshot of a status register, so 'is overdue count rising' cannot be answered until recurring snapshots exist [derived: posture-history]

## Method & provenance

- Validation / calibration statuses and dates from [src: manufacturing/internal-process-validation@2026-10-05]; PP3500 rev C lot release state from [src: manufacturing/internal-production-lots@2026-10-05]; the due-soon window is a plan constant [config: manufacturing.yml].
- Rev C blockers join the two pins on product line + hardware revision: validation records whose asset or process names rev C and is not validated, plus rev C lots without a release date [derived: revc-blockers] [derived: revc-lots].
- Not computed: a posture trend (single snapshot — published as unavailable) [derived: posture-history]; which test fixture each released lot ran on (not in either pin).
