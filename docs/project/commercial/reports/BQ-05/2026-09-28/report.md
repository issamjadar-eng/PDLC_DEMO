# BQ-05 — Plan revenue behind FDA decisions not yet received

_Demo sample data — not for clinical use._

_The plan data is demo-fabricated; the FDA review-interval context below is real
openFDA public data._

**Verdict**: $366.0M of the $1,000.0M five-year plan sits behind FDA decisions not yet received; exposure crosses the 40% threshold in FY2029, FY2030 (peak 60.0% in FY2030) [derived: v-main] [src: commercial/internal-revenue-plan@2026-09-28] [config: commercial.yml]

## Plan revenue by regulatory dependency per plan year

_Dependent = pccp-enabled + new-submission per [config: commercial.yml] — revenue behind
an FDA decision not yet received. letter-to-file needs internal documentation, not an
FDA decision, and is deliberately not counted (see the analysis plan)._

| Plan year | cleared | letter-to-file | pccp-enabled | new-submission | Total | Dependent | Exposure |
|---|---|---|---|---|---|---|---|
| FY2026 [src: commercial/internal-revenue-plan@2026-09-28] [derived: exposure-by-year] | $103.0M | $2.0M | $0.0M | $0.0M | $105.0M | $0.0M | 0.0% |
| FY2027 [src: commercial/internal-revenue-plan@2026-09-28] [derived: exposure-by-year] | $115.0M | $4.0M | $8.0M | $3.0M | $130.0M | $11.0M | 8.5% |
| FY2028 [src: commercial/internal-revenue-plan@2026-09-28] [derived: exposure-by-year] | $122.0M | $8.0M | $30.0M | $10.0M | $170.0M | $40.0M | 23.5% |
| FY2029 [src: commercial/internal-revenue-plan@2026-09-28] [derived: exposure-by-year] | $130.0M | $10.0M | $75.0M | $30.0M | $245.0M | $105.0M | 42.9% ⚠️ |
| FY2030 [src: commercial/internal-revenue-plan@2026-09-28] [derived: exposure-by-year] | $128.0M | $12.0M | $140.0M | $70.0M | $350.0M | $210.0M | 60.0% ⚠️ |

- Threshold: 40% of plan-year revenue [config: commercial.yml]; five-year dependent total $366.0M of $1,000.0M [derived: exposure-by-year] [src: commercial/internal-revenue-plan@2026-09-28]

## Slip scenarios (derived — method stated)

- Method: dependent revenue is treated as earned uniformly within its plan year; a slip
  of M months moves M/12 of each year's dependent revenue into the following year [derived: slip-scenarios] [config: commercial.yml];
  revenue pushed past the final plan year leaves the five-year window and is reported as
  the window shortfall [derived: slip-scenarios] [config: commercial.yml]

| Plan year | Plan of record | 6-month slip | 12-month slip |
|---|---|---|---|
| FY2026 [src: commercial/internal-revenue-plan@2026-09-28] [derived: slip-scenarios] | $105.0M | $105.0M | $105.0M |
| FY2027 [src: commercial/internal-revenue-plan@2026-09-28] [derived: slip-scenarios] | $130.0M | $124.5M | $119.0M |
| FY2028 [src: commercial/internal-revenue-plan@2026-09-28] [derived: slip-scenarios] | $170.0M | $155.5M | $141.0M |
| FY2029 [src: commercial/internal-revenue-plan@2026-09-28] [derived: slip-scenarios] | $245.0M | $212.5M | $180.0M |
| FY2030 [src: commercial/internal-revenue-plan@2026-09-28] [derived: slip-scenarios] | $350.0M | $297.5M | $245.0M |

- Five-year window shortfall (revenue pushed past the last plan year): 6-month slip $105.0M; 12-month slip $210.0M [derived: slip-scenarios]

## Context: how long one FDA review cycle runs (real public data)

- Median FRN infusion-pump 510(k) review interval, received to decision: 214.0 days across 30 clearances since 2021 [derived: fda-review-stat] [src: commercial/openfda-510k-infusion@2026-09-28]
- Scope stated: traditional/special 510(k) clearances for product code FRN only [src: commercial/openfda-510k-infusion@2026-09-28] — NOT a PCCP or
  De Novo/PMA timeline, and not our own history (our demo K-numbers are fabricated).

## Assumptions & expectations — plan vs actual

_`unvalidated` means the expectation itself is a stand-in that has not been grounded
in a plan of record or the risk file — challenge the assumption, not just the actual._

| ID | Expectation | Expected | Actual | Verdict | Basis |
|---|---|---|---|---|---|
| E-05.1 | Regulatory-dependent revenue stays below the exposure threshold in every plan year [derived: exposure-by-year] [config: commercial.yml] | <= 40% of plan-year revenue behind not-yet-received FDA decisions | FY2026: 0.0%; FY2027: 8.5%; FY2028: 23.5%; FY2029: 42.9%; FY2030: 60.0% — over threshold in FY2029, FY2030 | not-met (unvalidated) | stand-in risk-appetite threshold; the plan of record sets none |

## Narrative — Risks / Mitigations / Issues

### Issues (materialized — needs action)

- **I1 (high)** — FY2029 exposure is 42.9% — $105.0M of $245.0M sits behind pccp-enabled or new-submission decisions, over the 40% threshold [derived: exposure-by-year] [src: commercial/internal-revenue-plan@2026-09-28] [config: commercial.yml]
  - _Action_: Require a formal contingency in the plan narrative for the year; tie each dependent revenue block to a named submission milestone so slips become trackable events [derived: exposure-by-year] [src: commercial/internal-revenue-plan@2026-09-28] [config: commercial.yml]
- **I2 (high)** — FY2030 exposure is 60.0% — $210.0M of $350.0M sits behind pccp-enabled or new-submission decisions, over the 40% threshold [derived: exposure-by-year] [src: commercial/internal-revenue-plan@2026-09-28] [config: commercial.yml]
  - _Action_: Require a formal contingency in the plan narrative for the year; tie each dependent revenue block to a named submission milestone so slips become trackable events [derived: exposure-by-year] [src: commercial/internal-revenue-plan@2026-09-28] [config: commercial.yml]

### Risks (potential — mitigation identified)

- **R1 (medium)** — A uniform 6-month slip of all dependent revenue cuts FY2030 by $52.5M and pushes $105.0M past FY2030 — out of the five-year window entirely [derived: slip-scenarios] [src: commercial/internal-revenue-plan@2026-09-28] [config: commercial.yml]
  - _Mitigation_: The slip is arithmetic, not probability — pair it with the regulatory team's submission-timeline confidence before treating either scenario as the planning case [derived: slip-scenarios] [src: commercial/internal-revenue-plan@2026-09-28] [config: commercial.yml]
- **R2 (high)** — A uniform 12-month slip of all dependent revenue cuts FY2030 by $105.0M and pushes $210.0M past FY2030 — out of the five-year window entirely [derived: slip-scenarios] [src: commercial/internal-revenue-plan@2026-09-28] [config: commercial.yml]
  - _Mitigation_: The slip is arithmetic, not probability — pair it with the regulatory team's submission-timeline confidence before treating either scenario as the planning case [derived: slip-scenarios] [src: commercial/internal-revenue-plan@2026-09-28] [config: commercial.yml]

### Watch

- **W1 (medium)** — Public base rate: median FRN 510(k) review runs 214.0 days received-to-decision across 30 clearances since 2021 — one review cycle (214.0 days) vs ≈182 days for the smallest (6-month) slip scenario, and that measures cleared traditional/special 510(k)s, not PCCP or novel pathways [derived: fda-review-stat] [src: commercial/openfda-510k-infusion@2026-09-28]
- **W2 (medium)** — The slip method moves all dependent revenue uniformly — the plan data has no submission-event linkage, so per-program slips are not computable (stated gap; a submission register dataset would fix it) [derived: slip-scenarios]

## Method & provenance

- Plan revenue and dependency tags measured from [src: commercial/internal-revenue-plan@2026-09-28]; review intervals computed from public decision/received dates in [src: commercial/openfda-510k-infusion@2026-09-28].
- Dependent-category definition, threshold, and slip months live in [config: commercial.yml]; the slip arithmetic is declared per series.
- Exposure history across plan versions is unavailable — only one plan version is
  snapshotted; the history series states the gap rather than faking a trend
  [derived: exposure-history].
