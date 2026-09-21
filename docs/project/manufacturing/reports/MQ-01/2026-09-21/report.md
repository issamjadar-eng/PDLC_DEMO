# MQ-01 — First-pass yield, scrap and rework: where is yield eroding, and since when?

_Demo sample data — not for clinical use._

**Verdict**: Trailing 3-month window 2026-06..2026-08: portfolio first-pass yield 96.6% on 10970 units started (down 0.1 pts vs the prior 3 months); 0 of 5 lines below the 95% floor; 2 of 20 line×station cells below the floor: PP3500 · test 93.5% since 2026-04, IP5000 · test 94.9% since 2026-04; erosion is rev-specific — PP3500 rev C at test 92.5% vs other revs 96.1%, below the floor since 2026-04; scrap 1.0%, rework 2.4% of units started [derived: v-main] [src: manufacturing/internal-production-lots@2026-09-21] [config: manufacturing.yml]

## Headline

- Window: trailing 3 months 2026-06..2026-08, anchored on the snapshot as-of 2026-08-31 [src: manufacturing/internal-production-lots@2026-09-21] [config: manufacturing.yml]; FPY = units passed first time ÷ units started, unit-weighted [derived: fpy-stat].
- Portfolio FPY 96.6% (prior window 96.7%), scrap 1.0%, rework 2.4% [derived: fpy-stat] [src: manufacturing/internal-production-lots@2026-09-21].

## By product line

| Product line | FPY % | Scrap % | Rework % | Units started |
|---|---|---|---|---|
| IP5000 [src: manufacturing/internal-production-lots@2026-09-21] | 96.1 | 1.1 | 2.7 | 882 |
| PP3000 [src: manufacturing/internal-production-lots@2026-09-21] | 96.7 | 1.0 | 2.3 | 943 |
| PP3500 [src: manufacturing/internal-production-lots@2026-09-21] | 96.5 | 1.0 | 2.5 | 7136 |
| SP6000 [src: manufacturing/internal-production-lots@2026-09-21] | 97.4 | 0.8 | 1.9 | 1065 |
| SP6500 [src: manufacturing/internal-production-lots@2026-09-21] | 97.1 | 1.0 | 1.9 | 944 |

## By station

| Station | FPY % | Scrap % | Rework % | Units started |
|---|---|---|---|---|
| SMT [src: manufacturing/internal-production-lots@2026-09-21] | 96.9 | 1.3 | 1.9 | 2647 |
| final-assembly [src: manufacturing/internal-production-lots@2026-09-21] | 96.3 | 1.1 | 2.6 | 2746 |
| test [src: manufacturing/internal-production-lots@2026-09-21] | 94.4 ⚠️ | 1.3 | 4.3 | 2919 |
| pack [src: manufacturing/internal-production-lots@2026-09-21] | 99.1 | 0.2 | 0.7 | 2658 |

## By site

| Site | FPY % | Scrap % | Rework % | Units started |
|---|---|---|---|---|
| Eastbrook [src: manufacturing/internal-production-lots@2026-09-21] | 96.4 | 1.0 | 2.6 | 6141 |
| Westfield [src: manufacturing/internal-production-lots@2026-09-21] | 96.9 | 0.9 | 2.2 | 4829 |

## Where yield is eroding — line × station cells below the floor

| Cell | FPY % | Below floor since |
|---|---|---|
| PP3500 · test [src: manufacturing/internal-production-lots@2026-09-21] | 93.5 | 2026-04 |
| IP5000 · test [src: manufacturing/internal-production-lots@2026-09-21] | 94.9 | 2026-04 |

## PP3500 by hardware revision and station

| Station | rev B FPY % | rev C FPY % |
|---|---|---|
| SMT [src: manufacturing/internal-production-lots@2026-09-21] | 98.3 | 97.0 |
| final-assembly [src: manufacturing/internal-production-lots@2026-09-21] | 95.8 | 96.5 |
| test [src: manufacturing/internal-production-lots@2026-09-21] | 96.1 | 92.5 |
| pack [src: manufacturing/internal-production-lots@2026-09-21] | 99.6 | 99.0 |

- Widest rev gap: rev C at test 92.5% vs 96.1% for the other rev(s); rev C at test has sat below the floor every month since 2026-04 [derived: pp3500-rev-by-station] [src: manufacturing/internal-production-lots@2026-09-21].

## Assumptions & expectations — plan vs actual

_`unvalidated` means the expectation itself is a stand-in that has not been grounded
in a plan of record, a procedure, or the risk file — challenge the assumption, not just the actual._

| ID | Expectation | Expected | Actual | Verdict | Basis |
|---|---|---|---|---|---|
| E-01.1 | Every product line holds first-pass yield at or above the floor over the trailing window [derived: fpy-by-line] [config: manufacturing.yml] | FPY >= 95% per line, trailing 3 months | 0 of 5 lines below 95% in 2026-06..2026-08 | met (unvalidated) | stand-in yield floor; no per-line target is on record in a manufacturing plan or the pFMEA [VERIFY] |

## Narrative — Risks / Mitigations / Issues

### Issues (materialized — needs action)

- **I1 (medium)** — PP3500 · test first-pass yield 93.5% in 2026-06..2026-08, below the 95% floor every month since 2026-04 [derived: erosion-cells] [src: manufacturing/internal-production-lots@2026-09-21] [config: manufacturing.yml]
  - _Action_: Open / link the NCR and containment for the cell; confirm whether the failure mode is fixture, process, or component (see MQ-03 / MQ-05) [derived: erosion-cells] [src: manufacturing/internal-production-lots@2026-09-21] [config: manufacturing.yml]
- **I2 (medium)** — IP5000 · test first-pass yield 94.9% in 2026-06..2026-08, below the 95% floor every month since 2026-04 [derived: erosion-cells] [src: manufacturing/internal-production-lots@2026-09-21] [config: manufacturing.yml]
  - _Action_: Open / link the NCR and containment for the cell; confirm whether the failure mode is fixture, process, or component (see MQ-03 / MQ-05) [derived: erosion-cells] [src: manufacturing/internal-production-lots@2026-09-21] [config: manufacturing.yml]

### Risks (potential — mitigation identified)

- **R1 (high)** — PP3500 rev C yields 92.5% at test against 96.1% for the other rev(s) at the same station — a revision-specific defect, not a station drift; rev C share of PP3500 lots keeps rising so portfolio FPY follows it [derived: pp3500-rev-by-station] [derived: fpy-trend] [src: manufacturing/internal-production-lots@2026-09-21]
  - _Mitigation_: Hold rev-specific FPY as a release-readiness input for the rev C ramp; tie the test-station failure Pareto to the rev C fixture PQ (MQ-08) [derived: pp3500-rev-by-station] [derived: fpy-trend] [src: manufacturing/internal-production-lots@2026-09-21]
- **R2 (medium)** — The 95% floor is a stand-in — no yield target is on record in a manufacturing plan or the pFMEA, so 'below floor' is only as good as an unratified threshold [config: manufacturing.yml]
  - _Mitigation_: Have manufacturing engineering ratify per-line FPY targets and mark E-01.1 validated [config: manufacturing.yml]

### Watch

- **W1 (medium)** — Site cut: Eastbrook is the lower-yield plant at 96.4% in 2026-06..2026-08 — check whether the gap is mix (which lines run there) or process [derived: fpy-by-site] [src: manufacturing/internal-production-lots@2026-09-21]

## Method & provenance

- All figures from the pinned lot records [src: manufacturing/internal-production-lots@2026-09-21]; the window and the floor are plan constants [config: manufacturing.yml].
- Rates are unit-weighted (sum of units over the cell), not lot-averaged, so large lots count for what they are; rework and scrap are the two exits from first-pass failure and sum to the first-pass failure rate [derived: fpy-stat].
- 'Since when' is the first month of the unbroken run of months whose rolling 3-month FPY sits below the floor, ending at the as-of month — a cell that dipped and recovered is not reported as eroding [derived: erosion-cells].
- Monthly history is charted for the portfolio and for the rev/station cell with the widest gap [derived: fpy-trend].
