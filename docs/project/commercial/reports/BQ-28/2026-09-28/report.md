# BQ-28 — Revenue vs plan: line, region, timing

_Demo sample data — not for clinical use._

**Verdict**: H1 2026 revenue $46.3M vs plan $48.3M (-4.1%, within the ±5% tolerance overall; 4 of 6 lines breach the band individually on the downside); under plan: cloud-suite -16.4%, SP6500 -15.7%, SP6000 -9.1%, PP3500 -6.3%; masked by IP5000 +24.3%, PP3000 +16.1%; 2026-Q2 alone breached at -5.5% [derived: v-main] [src: commercial/internal-financials@2026-09-28] [src: commercial/internal-revenue-plan@2026-09-28] [config: commercial.yml]

## Variance by product line

_Window: 2026-Q1, 2026-Q2 (closed quarters in the pinned actuals) [src: commercial/internal-financials@2026-09-28]; plan rows from the plan of record [src: commercial/internal-revenue-plan@2026-09-28]; flagging tolerance ±5% [config: commercial.yml]._

| Product line | Actual $M | Plan $M | Variance % | Variance $M |
|---|---|---|---|---|
| IP5000 [src: commercial/internal-financials@2026-09-28] [src: commercial/internal-revenue-plan@2026-09-28] | 4.0 | 3.2 | +24.3% ⚠️ | +0.8 |
| PP3000 [src: commercial/internal-financials@2026-09-28] [src: commercial/internal-revenue-plan@2026-09-28] | 6.4 | 5.5 | +16.1% ⚠️ | +0.9 |
| PP3500 [src: commercial/internal-financials@2026-09-28] [src: commercial/internal-revenue-plan@2026-09-28] | 22.4 | 23.9 | -6.3% ⚠️ | -1.5 |
| SP6000 [src: commercial/internal-financials@2026-09-28] [src: commercial/internal-revenue-plan@2026-09-28] | 5.0 | 5.5 | -9.1% ⚠️ | -0.5 |
| SP6500 [src: commercial/internal-financials@2026-09-28] [src: commercial/internal-revenue-plan@2026-09-28] | 3.5 | 4.1 | -15.7% ⚠️ | -0.6 |
| cloud-suite [src: commercial/internal-financials@2026-09-28] [src: commercial/internal-revenue-plan@2026-09-28] | 5.0 | 6.0 | -16.4% ⚠️ | -1.0 |

## Variance by region

| Region | Actual $M | Plan $M | Variance % | Variance $M |
|---|---|---|---|---|
| APAC [src: commercial/internal-financials@2026-09-28] [src: commercial/internal-revenue-plan@2026-09-28] | 7.0 | 7.2 | -3.2% | -0.2 |
| EMEA [src: commercial/internal-financials@2026-09-28] [src: commercial/internal-revenue-plan@2026-09-28] | 13.8 | 14.5 | -4.5% | -0.7 |
| NA [src: commercial/internal-financials@2026-09-28] [src: commercial/internal-revenue-plan@2026-09-28] | 25.5 | 26.6 | -4.1% | -1.1 |

## Timing — variance by quarter

| Quarter | Actual $M | Plan $M | Variance % |
|---|---|---|---|
| 2026-Q1 [src: commercial/internal-financials@2026-09-28] [src: commercial/internal-revenue-plan@2026-09-28] | 22.5 | 23.1 | -2.6% |
| 2026-Q2 [src: commercial/internal-financials@2026-09-28] [src: commercial/internal-revenue-plan@2026-09-28] | 23.8 | 25.2 | -5.5% ⚠️ |

## Volume vs price: not computable (stated, not approximated)

- The plan of record carries revenue only — NO planned units — so a volume-vs-price
  bridge has no plan side [src: commercial/internal-revenue-plan@2026-09-28]. Actual units exist [src: commercial/internal-financials@2026-09-28], but an
  actual-side ASP alone cannot attribute variance between volume and price. The split is
  published as an unavailable series [derived: price-volume-split] until planned units
  land in the LRP export.

## Assumptions & expectations — plan vs actual

_`unvalidated` means the expectation itself is a stand-in that has not been grounded
in a plan of record or the risk file — challenge the assumption, not just the actual._

| ID | Expectation | Expected | Actual | Verdict | Basis |
|---|---|---|---|---|---|
| E-28.1 | Year-to-date revenue tracks the 2026 plan within tolerance [derived: ytd-variance] [derived: variance-by-line] [config: commercial.yml] | within +/- 5% of plan, YTD | -4.1% YTD (H1 2026) — within tolerance overall; 4 of 6 lines breach the ±5% band individually on the downside | met (unvalidated) | standard reforecast trigger; the plan of record names no tolerance [VERIFY] |

## Narrative — Risks / Mitigations / Issues

### Issues (materialized — needs action)

- **I1 (high)** — cloud-suite is -16.4% under plan for H1 2026 ($5.0M actual vs $6.0M plan) — beyond the ±5% flagging tolerance [derived: variance-by-line] [src: commercial/internal-financials@2026-09-28] [src: commercial/internal-revenue-plan@2026-09-28] [config: commercial.yml]
  - _Action_: Confirm driver with the win/loss and funnel reviews; decide reforecast vs recovery plan for the line at the monthly close [derived: variance-by-line] [src: commercial/internal-financials@2026-09-28] [src: commercial/internal-revenue-plan@2026-09-28] [config: commercial.yml]
- **I2 (high)** — SP6500 is -15.7% under plan for H1 2026 ($3.5M actual vs $4.1M plan) — beyond the ±5% flagging tolerance [derived: variance-by-line] [src: commercial/internal-financials@2026-09-28] [src: commercial/internal-revenue-plan@2026-09-28] [config: commercial.yml]
  - _Action_: Confirm driver with the win/loss and funnel reviews; decide reforecast vs recovery plan for the line at the monthly close [derived: variance-by-line] [src: commercial/internal-financials@2026-09-28] [src: commercial/internal-revenue-plan@2026-09-28] [config: commercial.yml]
- **I3 (medium)** — SP6000 is -9.1% under plan for H1 2026 ($5.0M actual vs $5.5M plan) — beyond the ±5% flagging tolerance [derived: variance-by-line] [src: commercial/internal-financials@2026-09-28] [src: commercial/internal-revenue-plan@2026-09-28] [config: commercial.yml]
  - _Action_: Confirm driver with the win/loss and funnel reviews; decide reforecast vs recovery plan for the line at the monthly close [derived: variance-by-line] [src: commercial/internal-financials@2026-09-28] [src: commercial/internal-revenue-plan@2026-09-28] [config: commercial.yml]
- **I4 (medium)** — PP3500 is -6.3% under plan for H1 2026 ($22.4M actual vs $23.9M plan) — beyond the ±5% flagging tolerance [derived: variance-by-line] [src: commercial/internal-financials@2026-09-28] [src: commercial/internal-revenue-plan@2026-09-28] [config: commercial.yml]
  - _Action_: Confirm driver with the win/loss and funnel reviews; decide reforecast vs recovery plan for the line at the monthly close [derived: variance-by-line] [src: commercial/internal-financials@2026-09-28] [src: commercial/internal-revenue-plan@2026-09-28] [config: commercial.yml]

### Risks (potential — mitigation identified)

- **R1 (medium)** — Quarter-over-quarter timing is deteriorating: 2026-Q1 -2.6% → 2026-Q2 -5.5% — the latest quarter breaches the ±5% band on its own [derived: variance-by-quarter] [src: commercial/internal-financials@2026-09-28] [src: commercial/internal-revenue-plan@2026-09-28] [config: commercial.yml]
  - _Mitigation_: Treat the next monthly close as the reforecast trigger check; do not wait for the YTD composite to breach [derived: variance-by-quarter] [src: commercial/internal-financials@2026-09-28] [src: commercial/internal-revenue-plan@2026-09-28] [config: commercial.yml]
- **R2 (medium)** — The ±5% tolerance is a stand-in — the plan of record names no reforecast trigger, so the within/outside verdict is only as good as an unratified threshold [config: commercial.yml]
  - _Mitigation_: Have finance ratify a tolerance in the plan of record and mark E-28.1 validated [config: commercial.yml]

### Watch

- **W1 (medium)** — Mix masking: IP5000 at +24.3%, PP3000 at +16.1% over plan offsets the under-plan lines inside the composite — the total variance understates the flagship/growth miss [derived: variance-by-line] [derived: variance-contribution]

## Method & provenance

- Actuals summed from [src: commercial/internal-financials@2026-09-28]; plan from [src: commercial/internal-revenue-plan@2026-09-28]; comparison restricted to matching closed quarters; tolerance and fiscal year [config: commercial.yml].
- Variance $M contribution per line/region is charted so the composite's netting is visible [derived: variance-contribution].
- Historical view: quarterly actual revenue vs the 2026 plan phasing is charted [derived: quarterly-trend] [src: commercial/internal-financials@2026-09-28] [src: commercial/internal-revenue-plan@2026-09-28].
