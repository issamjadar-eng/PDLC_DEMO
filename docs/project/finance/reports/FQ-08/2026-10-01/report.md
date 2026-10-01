# FQ-08 — Budget vs actual YTD by function; headcount variance; breach drivers

_Demo sample data — not for clinical use._

**Verdict**: YTD 2026 (2026-01..2026-08) opex $28.84M vs budget $28.40M (+1.5%, within the ±3% total tolerance); 3 of 6 functions breach the ±5% band; Regulatory/Quality +16.7% (driver RQ-EXT +$427K (+76.2%)); Sales & Marketing -9.8% (driver SM-NA -$401K (-11.9%); headcount 45 vs 53 budget at 2026-08 — hiring lag); R&D +6.6% (driver RD-FW +$524K (+17.2%); headcount 48 vs 45 budget at 2026-08) [derived: v-main] [src: finance/internal-gl-budget@2026-09-28] [config: finance.yml]

## Variance by function

_Window: 2026-01..2026-08 (every period in the pin) [src: finance/internal-gl-budget@2026-09-28]; tolerances ±5% per function, ±3% total [config: finance.yml]; headcount at 2026-08._

| Function | Budget $M | Actual $M | Variance % | Variance $K | Heads budget | Heads actual |
|---|---|---|---|---|---|---|
| G&A [src: finance/internal-gl-budget@2026-09-28] | 3.60 | 3.65 | +1.3% | +$47K | 16 | 18 |
| Manufacturing [src: finance/internal-gl-budget@2026-09-28] | 4.00 | 4.02 | +0.5% | +$21K | 30 | 29 |
| R&D [src: finance/internal-gl-budget@2026-09-28] | 8.00 | 8.53 | +6.6% ⚠️ | +$526K | 45 | 48 |
| Regulatory/Quality [src: finance/internal-gl-budget@2026-09-28] | 2.80 | 3.27 | +16.7% ⚠️ | +$468K | 14 | 12 |
| Sales & Marketing [src: finance/internal-gl-budget@2026-09-28] | 7.20 | 6.50 | -9.8% ⚠️ | -$703K | 53 | 45 |
| Service [src: finance/internal-gl-budget@2026-09-28] | 2.80 | 2.88 | +2.8% | +$77K | 21 | 20 |
| **Total** [src: finance/internal-gl-budget@2026-09-28] | 28.40 | 28.84 | +1.5% | +$436K | 179 | 172 |

## Breach drivers — cost centers inside breaching functions

### Regulatory/Quality (+16.7%) [src: finance/internal-gl-budget@2026-09-28]

| Cost center | Budget $M | Actual $M | Variance $K | Variance % |
|---|---|---|---|---|
| RQ-EXT [src: finance/internal-gl-budget@2026-09-28] | 0.56 | 0.99 | +$427K | +76.2% |
| RQ-REG [src: finance/internal-gl-budget@2026-09-28] | 1.04 | 1.06 | +$21K | +2.1% |
| RQ-QA [src: finance/internal-gl-budget@2026-09-28] | 1.20 | 1.22 | +$19K | +1.6% |
- driver RQ-EXT +$427K (+76.2%) [src: finance/internal-gl-budget@2026-09-28] [derived: cost-center-drivers]

### Sales & Marketing (-9.8%) [src: finance/internal-gl-budget@2026-09-28]

| Cost center | Budget $M | Actual $M | Variance $K | Variance % |
|---|---|---|---|---|
| SM-NA [src: finance/internal-gl-budget@2026-09-28] | 3.36 | 2.96 | -$401K | -11.9% |
| SM-INTL [src: finance/internal-gl-budget@2026-09-28] | 2.24 | 1.99 | -$250K | -11.1% |
| SM-MKT [src: finance/internal-gl-budget@2026-09-28] | 1.60 | 1.55 | -$53K | -3.3% |
- driver SM-NA -$401K (-11.9%); headcount 45 vs 53 budget at 2026-08 — hiring lag [src: finance/internal-gl-budget@2026-09-28] [derived: cost-center-drivers]

### R&D (+6.6%) [src: finance/internal-gl-budget@2026-09-28]

| Cost center | Budget $M | Actual $M | Variance $K | Variance % |
|---|---|---|---|---|
| RD-FW [src: finance/internal-gl-budget@2026-09-28] | 3.04 | 3.56 | +$524K | +17.2% |
| RD-SW [src: finance/internal-gl-budget@2026-09-28] | 2.56 | 2.61 | +$50K | +2.0% |
| RD-HW [src: finance/internal-gl-budget@2026-09-28] | 2.40 | 2.35 | -$49K | -2.0% |
- driver RD-FW +$524K (+17.2%); headcount 48 vs 45 budget at 2026-08 [src: finance/internal-gl-budget@2026-09-28] [derived: cost-center-drivers]

## Spend by project: not in the ledger (stated, not approximated)

- The GL export carries function and cost center only [src: finance/internal-gl-budget@2026-09-28]; program attribution and the capitalization view need a project dimension (roadmap FQ-10) [derived: variance-by-project].

## Assumptions & expectations — plan vs actual

_`unvalidated` means the expectation itself is a stand-in that has not been grounded
in a plan of record or the risk file — challenge the assumption, not just the actual._

| ID | Expectation | Expected | Actual | Verdict | Basis |
|---|---|---|---|---|---|
| E-08.1 | Every function's year-to-date spend is within tolerance of budget [derived: variance-pct-by-function] [config: finance.yml] | within +/- 5% of YTD budget per function | 3 of 6 functions beyond ±5%: Regulatory/Quality +16.7%, Sales & Marketing -9.8%, R&D +6.6% | not-met (unvalidated) | standard variance-review trigger; the budget book names no tolerance [VERIFY] |
| E-08.2 | Total operating spend year to date is within the company tolerance [derived: ytd-variance-stat] [config: finance.yml] | within +/- 3% of YTD budget in total | +1.5% total (YTD 2026 (2026-01..2026-08)) | met (unvalidated) | board reporting convention carried forward; not in the budget book [VERIFY] |

## Narrative — Risks / Mitigations / Issues

### Issues (materialized — needs action)

- **I1 (high)** — Regulatory/Quality is +16.7% over budget YTD 2026 (2026-01..2026-08) ($3.27M vs $2.80M) — driver RQ-EXT +$427K (+76.2%) [derived: variance-by-function] [derived: cost-center-drivers] [src: finance/internal-gl-budget@2026-09-28] [config: finance.yml]
  - _Action_: Re-plan the driving cost center at the monthly close: confirm the spend is buying a milestone, then reforecast or re-phase [derived: variance-by-function] [derived: cost-center-drivers] [src: finance/internal-gl-budget@2026-09-28] [config: finance.yml]
- **I2 (medium)** — R&D is +6.6% over budget YTD 2026 (2026-01..2026-08) ($8.53M vs $8.00M) — driver RD-FW +$524K (+17.2%); headcount 48 vs 45 budget at 2026-08 [derived: variance-by-function] [derived: cost-center-drivers] [src: finance/internal-gl-budget@2026-09-28] [config: finance.yml]
  - _Action_: Re-plan the driving cost center at the monthly close: confirm the spend is buying a milestone, then reforecast or re-phase [derived: variance-by-function] [derived: cost-center-drivers] [src: finance/internal-gl-budget@2026-09-28] [config: finance.yml]
- **I3 (medium)** — Sales & Marketing is -9.8% under budget YTD 2026 (2026-01..2026-08) ($6.50M vs $7.20M) — driver SM-NA -$401K (-11.9%); headcount 45 vs 53 budget at 2026-08 — hiring lag [derived: variance-by-function] [derived: headcount-by-function] [src: finance/internal-gl-budget@2026-09-28] [config: finance.yml]
  - _Action_: Treat the under-spend as deferred work, not savings: confirm hiring pipeline vs plan and the revenue-plan dependency on the missing heads [derived: variance-by-function] [derived: headcount-by-function] [src: finance/internal-gl-budget@2026-09-28] [config: finance.yml]

### Risks (potential — mitigation identified)

- **R1 (medium)** — The ±5% per-function and ±3% total tolerances are stand-ins — the budget book names no variance trigger, so the breach list is only as firm as an unratified band [config: finance.yml]
  - _Mitigation_: Have the controller ratify the tolerances in the budget book and mark E-08.1 / E-08.2 validated [config: finance.yml]

### Watch

- **W1 (medium)** — Netting inside the total: Regulatory/Quality +16.7%, R&D +6.6% over is offset by Sales & Marketing -9.8% under — the company total understates both [derived: variance-by-function] [derived: ytd-variance-stat]
- **W2 (medium)** — The ledger export carries no program / project dimension — an R&D overrun cannot be attributed to a milestone or assessed for capitalization here [derived: variance-by-project] [src: finance/internal-gl-budget@2026-09-28]

## Method & provenance

- Budget and actual summed from [src: finance/internal-gl-budget@2026-09-28] over every period in the pin; variance = (actual − budget) ÷ budget; tolerances [config: finance.yml]; breach drivers ranked by absolute dollar variance.
- Historical view: monthly variance for the total and the 3 largest-variance functions is charted [derived: monthly-variance-trend] [src: finance/internal-gl-budget@2026-09-28].
- Verdict and expectation actuals carry the breaching functions and their drivers so a rollup cannot drop them [derived: v-main].
