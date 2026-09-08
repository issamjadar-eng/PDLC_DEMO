# FQ-01 — Gross margin by line and region; standard-vs-actual cost variance

_Demo sample data — not for clinical use._

**Verdict**: H1 2026 gross margin 51.5% vs 50.6% H1 2025 (+1.0 pts) — BELOW the 55% floor; 2 of 6 lines eroding (GM down 1 pt or more YoY); eroding: PP3000 -1.5 pts, IP5000 -1.5 pts; standard-cost variance beyond ±5% on 0 of 6 lines (all revenue types); hardware-only variance beyond ±5% on 2 of 5 device lines — unfavorable PP3000 +11.0%, IP5000 +10.9% [derived: v-main] [src: commercial/internal-financials@2026-07-27] [src: finance/internal-standard-costs@2026-09-08] [config: finance.yml]

## Gross margin by product line

_Window: 2026-Q1, 2026-Q2 (closed quarters in the pinned actuals) vs 2025-Q1, 2025-Q2 [src: commercial/internal-financials@2026-07-27]; erosion threshold -1.0 pts YoY and margin floor 55% [config: finance.yml]._

| Product line | Revenue $M (H1 2026) | GM % | GM % prior year | Δ pts |
|---|---|---|---|---|
| IP5000 [src: commercial/internal-financials@2026-07-27] | 4.00 | 45.6% | 47.1% | -1.5 pts ⚠️ |
| PP3000 [src: commercial/internal-financials@2026-07-27] | 6.41 | 44.9% | 46.4% | -1.5 pts ⚠️ |
| PP3500 [src: commercial/internal-financials@2026-07-27] | 22.40 | 49.5% | 49.5% | +0.0 pts |
| SP6000 [src: commercial/internal-financials@2026-07-27] | 5.02 | 49.1% | 49.1% | +0.0 pts |
| SP6500 [src: commercial/internal-financials@2026-07-27] | 3.49 | 48.9% | 49.0% | -0.1 pts |
| cloud-suite [src: commercial/internal-financials@2026-07-27] | 5.00 | 78.0% | 78.0% | +0.0 pts |
| **Company** [src: commercial/internal-financials@2026-07-27] | 46.32 | 51.5% | 50.6% | +1.0 pts |

## Gross margin by region

| Region | Revenue $M | GM % | GM % prior year | Δ pts |
|---|---|---|---|---|
| APAC [src: commercial/internal-financials@2026-07-27] | 7.01 | 51.5% | 50.4% | +1.1 pts |
| EMEA [src: commercial/internal-financials@2026-07-27] | 13.84 | 51.5% | 50.5% | +0.9 pts |
| NA [src: commercial/internal-financials@2026-07-27] | 25.48 | 51.5% | 50.6% | +0.9 pts |

## Standard-vs-actual cost variance by line

_Actual unit cost = COGS ÷ units per quarter × line × revenue type, summed over regions [src: commercial/internal-financials@2026-07-27]; standard from the cost roll-up [src: finance/internal-standard-costs@2026-09-08]; variance = (actual − standard) × units over the window, positive = unfavorable; review tolerance ±5% applied to the line total (all revenue types) [config: finance.yml]. The hardware-only column is the leading indicator the line total dilutes._

| Product line | Variance $K | Variance % of standard (all types) | Hardware-only variance % |
|---|---|---|---|
| IP5000 [src: commercial/internal-financials@2026-07-27] [src: finance/internal-standard-costs@2026-09-08] | +96 | +4.6% | +10.9% ⚠️ |
| PP3000 [src: commercial/internal-financials@2026-07-27] [src: finance/internal-standard-costs@2026-09-08] | +165 | +4.9% | +11.0% ⚠️ |
| PP3500 [src: commercial/internal-financials@2026-07-27] [src: finance/internal-standard-costs@2026-09-08] | -132 | -1.2% | -2.8% |
| SP6000 [src: commercial/internal-financials@2026-07-27] [src: finance/internal-standard-costs@2026-09-08] | +16 | +0.6% | +0.0% |
| SP6500 [src: commercial/internal-financials@2026-07-27] [src: finance/internal-standard-costs@2026-09-08] | +11 | +0.6% | +0.1% |
| cloud-suite [src: commercial/internal-financials@2026-07-27] [src: finance/internal-standard-costs@2026-09-08] | +14 | +1.3% | n/a |

## Standard-cost variance by region: not computable (stated, not approximated)

- The standard-cost roll-up carries no region dimension [src: finance/internal-standard-costs@2026-09-08]; actual COGS is regional
  [src: commercial/internal-financials@2026-07-27], but a regional variance needs a regional standard or a regional actual-cost feed.
  Published as an unavailable series [derived: cost-variance-by-region].

## Assumptions & expectations — plan vs actual

_`unvalidated` means the expectation itself is a stand-in that has not been grounded
in a plan of record or the risk file — challenge the assumption, not just the actual._

| ID | Expectation | Expected | Actual | Verdict | Basis |
|---|---|---|---|---|---|
| E-01.1 | Company gross margin holds at or above the floor over the fiscal-year window [derived: gm-stat] [derived: gm-by-line] [config: finance.yml] | gross margin >= 55% | 51.5% (H1 2026); 2 of 6 lines eroding | not-met (unvalidated) | board-deck target carried forward; no plan of record names a floor [VERIFY] |
| E-01.2 | No product line's standard-cost variance exceeds the review tolerance [derived: cost-variance-by-line] [config: finance.yml] | |actual vs standard| <= 5% per line over the window | 0 of 6 lines beyond ±5% (all revenue types); hardware-only 2 of 5: PP3000 +11.0%, IP5000 +10.9% | met (unvalidated) | cost-accounting review trigger; no controller policy names a tolerance [VERIFY] |

## Narrative — Risks / Mitigations / Issues

### Issues (materialized — needs action)

- **I1 (medium)** — PP3000 gross margin 44.9% in H1 2026 vs 46.4% in H1 2025 (-1.5 pts) while its hardware unit cost runs +11.0% above standard (line total +4.9%, diluted by consumables and service) [derived: gm-by-line] [derived: cost-variance-by-line] [src: commercial/internal-financials@2026-07-27] [src: finance/internal-standard-costs@2026-09-08] [config: finance.yml]
  - _Action_: Cost review of the line: reset the standard to actual, then decide price action vs run-down at the quarterly margin review [derived: gm-by-line] [derived: cost-variance-by-line] [src: commercial/internal-financials@2026-07-27] [src: finance/internal-standard-costs@2026-09-08] [config: finance.yml]
- **I2 (medium)** — IP5000 gross margin 45.6% in H1 2026 vs 47.1% in H1 2025 (-1.5 pts) while its hardware unit cost runs +10.9% above standard (line total +4.6%, diluted by consumables and service) [derived: gm-by-line] [derived: cost-variance-by-line] [src: commercial/internal-financials@2026-07-27] [src: finance/internal-standard-costs@2026-09-08] [config: finance.yml]
  - _Action_: Cost review of the line: reset the standard to actual, then decide price action vs run-down at the quarterly margin review [derived: gm-by-line] [derived: cost-variance-by-line] [src: commercial/internal-financials@2026-07-27] [src: finance/internal-standard-costs@2026-09-08] [config: finance.yml]

### Risks (potential — mitigation identified)

- **R1 (medium)** — Company gross margin 51.5% sits below the 55% floor — the floor is a stand-in (no plan of record names one), so the miss is only as firm as an unratified target [derived: gm-stat] [config: finance.yml]
  - _Mitigation_: Have finance ratify a margin floor in the plan of record and mark E-01.1 validated [derived: gm-stat] [config: finance.yml]
- **R2 (medium)** — Margin reporting on standards flatters IP5000, PP3000 — hardware unit cost runs above standard (PP3000 +11.0%, IP5000 +10.9%), so booked unit costs understate actual cost [derived: cost-variance-by-line] [derived: cost-variance-trend] [src: commercial/internal-financials@2026-07-27] [src: finance/internal-standard-costs@2026-09-08]
  - _Mitigation_: Standard reset at the next standards cycle; interim margin reporting on actual unit cost [derived: cost-variance-by-line] [derived: cost-variance-trend] [src: commercial/internal-financials@2026-07-27] [src: finance/internal-standard-costs@2026-09-08]

### Watch

- **W1 (medium)** — Mix masking: company margin is up +1.0 pts YoY while 2 line(s) erode — the aggregate is lifted by mix, not by line health [derived: gm-stat] [derived: gm-by-line]

## Method & provenance

- Gross margin = (revenue − COGS) ÷ revenue from [src: commercial/internal-financials@2026-07-27]; window and prior-year quarters matched one-to-one; thresholds [config: finance.yml].
- Historical view: quarterly gross margin for the company and the largest 3 lines is charted [derived: gm-trend] [src: commercial/internal-financials@2026-07-27]; hardware unit-cost variance per quarter is charted [derived: cost-variance-trend] [src: commercial/internal-financials@2026-07-27] [src: finance/internal-standard-costs@2026-09-08].
- Verdict and expectation actuals carry the eroding-line and variance-breach counts so a rollup cannot drop them [derived: v-main].
