# BQ-03 — Recurring mix today vs the Y5 plan — and what the target is made of

_Demo sample data — not for clinical use._

**Verdict**: Recurring revenue is 10.8% of revenue today (FY2026H1) vs 68.6% planned for FY2030; of the $350.0M target, $128.0M rides on already-cleared products, $12.0M on letter-to-file changes, and $210.0M (60.0%) sits behind FDA decisions not yet received — and within the $240.0M recurring proxy itself, $210.0M (87.5%) is behind those decisions [derived: v-main] [src: commercial/internal-financials@2026-09-21] [src: commercial/internal-revenue-plan@2026-09-21]

## Recurring share — actuals by fiscal year

_Recurring = subscription revenue only (consumables re-order but are not counted;
conservative, per the analysis plan). The current fiscal year is a half-year of
actuals and is labeled as such, never annualized._

| Fiscal year | Total revenue | Subscription revenue | Recurring share |
|---|---|---|---|
| FY2024 [src: commercial/internal-financials@2026-09-21] | $69.9M | $3.5M | 5.0% |
| FY2025 [src: commercial/internal-financials@2026-09-21] | $80.5M | $6.4M | 7.9% |
| FY2026H1 [src: commercial/internal-financials@2026-09-21] | $46.3M | $5.0M | 10.8% |

## Plan trajectory — recurring proxy per plan year

- Plan recurring is proxied by the cloud-suite line [config: commercial.yml] [src: commercial/internal-revenue-plan@2026-09-21]:

| Plan year | Plan total | Cloud-suite (recurring proxy) | Share |
|---|---|---|---|
| FY2026 [src: commercial/internal-revenue-plan@2026-09-21] | $105.0M | $13.0M | 12.4% |
| FY2027 [src: commercial/internal-revenue-plan@2026-09-21] | $130.0M | $25.0M | 19.2% |
| FY2028 [src: commercial/internal-revenue-plan@2026-09-21] | $170.0M | $60.0M | 35.3% |
| FY2029 [src: commercial/internal-revenue-plan@2026-09-21] | $245.0M | $130.0M | 53.1% |
| FY2030 [src: commercial/internal-revenue-plan@2026-09-21] | $350.0M | $240.0M | 68.6% |

## The FY2030 target decomposed — contracted / modeled / aspiration

_Buckets are defined against each plan row's regulatory_dependency (see the analysis
plan): cleared revenue needs no permission; letter-to-file needs execution and internal
documentation only; the rest needs FDA decisions that have not been received._

| Bucket | Dependency | Revenue | Share of target |
|---|---|---|---|
| contracted (upper bound — cleared today, not contractually committed) [src: commercial/internal-revenue-plan@2026-09-21] [derived: y5-decomposition] | cleared | $128.0M | 36.6% |
| modeled [src: commercial/internal-revenue-plan@2026-09-21] [derived: y5-decomposition] | letter-to-file | $12.0M | 3.4% |
| aspiration [src: commercial/internal-revenue-plan@2026-09-21] [derived: y5-decomposition] | pccp-enabled + new-submission | $210.0M | 60.0% |

- Pinned FY2030 plan total $350.0M vs catalog target constant $350.0M (delta $0.0M) [derived: y5-decomposition] [config: commercial.yml]

### The recurring bet specifically — the same buckets within the cloud-suite proxy

_The blended decomposition above spans all 6 lines [src: commercial/internal-revenue-plan@2026-09-21]; the question is about recurring
revenue, so the same cut is shown for the recurring proxy line alone — both figures
stand together, neither replaces the other._

- Within the FY2030 recurring proxy (cloud-suite, $240.0M): $210.0M (87.5%) sits behind FDA decisions not yet received, vs 60.0% blended across all lines — $30.0M cleared and $0.0M letter-to-file [derived: y5-recurring-decomposition] [src: commercial/internal-revenue-plan@2026-09-21] [config: commercial.yml]
- Of the blended $128.0M cleared bucket, $98.0M (76.6%) is non-recurring (device) revenue — the cleared cushion mostly sits outside the recurring story [derived: y5-recurring-decomposition] [derived: y5-decomposition] [src: commercial/internal-revenue-plan@2026-09-21]

## Assumptions & expectations — plan vs actual

_`unvalidated` means the expectation itself is a stand-in that has not been grounded
in a plan of record or the risk file — challenge the assumption, not just the actual._

| ID | Expectation | Expected | Actual | Verdict | Basis |
|---|---|---|---|---|---|
| E-03.1 | Recurring (subscription) revenue share grows every fiscal year toward the Y5 model [derived: recurring-share-trend] [config: commercial.yml] | recurring share strictly increasing FY2024 -> FY2026 | FY2024: 5.0%; FY2025: 7.9%; FY2026H1: 10.8% — strictly increasing | met (unvalidated) | implied by the razor+recurring strategy (D-COMM); no numeric milestone set |

## Narrative — Risks / Mitigations / Issues

### Risks (potential — mitigation identified)

- **R1 (high)** — 60.0% of the FY2030 target ($210.0M) is aspiration — revenue behind pccp-enabled and new-submission FDA decisions not yet received — and the blended figure understates the recurring-specific bet: within the cloud-suite recurring proxy alone, 87.5% ($210.0M of $240.0M) sits behind those decisions; the regulatory-exposure and slip arithmetic is BQ-05's answer [derived: y5-decomposition] [derived: y5-recurring-decomposition] [src: commercial/internal-revenue-plan@2026-09-21]
  - _Mitigation_: Hold the aspiration bucket against BQ-05's exposure threshold and slip scenarios; require a contingency line in the plan narrative [derived: y5-decomposition] [derived: y5-recurring-decomposition] [src: commercial/internal-revenue-plan@2026-09-21]

### Watch

- **W1 (medium)** — Plan-side recurring uses the cloud-suite proxy (the plan carries no revenue type) — device-line service contracts that recur are not counted, and any non-recurring cloud-suite revenue is; both directions stated [config: commercial.yml] [src: commercial/internal-revenue-plan@2026-09-21]

## Method & provenance

- Actual shares measured from [src: commercial/internal-financials@2026-09-21] (revenue_type = subscription ÷ total, per
  fiscal year on file); plan shares and the decomposition from [src: commercial/internal-revenue-plan@2026-09-21].
- Bucket definitions and the recurring proxy are committed in the analysis plan and
  parameterized in [config: commercial.yml].
- No contract/backlog dataset exists — the contracted bucket is an upper bound (stated);
  prior plan versions are not snapshotted, so target-evolution history is a stated gap.
