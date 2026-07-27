# BQ-01 — Funding map: which lines fund the company, which consume it

_Demo sample data — not for clinical use._

**Verdict**: PP3500 and cloud-suite fund the company — 59.8% of trailing-4Q gross margin ($27.0M of the portfolio's $45.2M GM on $88.2M revenue, window 2025-Q3..2026-Q2); all 6 lines gross-margin positive; margins compressing on IP5000, PP3000 [derived: v-main] [src: commercial/internal-financials@2026-07-27]

## Trailing-4Q economics by line (window 2025-Q3..2026-Q2 [src: commercial/internal-financials@2026-07-27])

| Line | Revenue | Gross margin | GM % | Share of total GM | GM % vs prior 4Q |
|---|---|---|---|---|---|
| PP3500 [src: commercial/internal-financials@2026-07-27] [derived: gm-by-line] | $40.9M | $20.3M | 49.5% | 44.8% | +0.1 pts |
| cloud-suite [src: commercial/internal-financials@2026-07-27] [derived: gm-by-line] | $8.6M | $6.7M | 78.0% | 14.9% | +0.0 pts |
| PP3000 [src: commercial/internal-financials@2026-07-27] [derived: gm-by-line] | $13.2M | $6.0M | 45.3% | 13.2% | -1.5 pts |
| SP6000 [src: commercial/internal-financials@2026-07-27] [derived: gm-by-line] | $10.1M | $4.9M | 49.1% | 10.9% | +0.0 pts |
| IP5000 [src: commercial/internal-financials@2026-07-27] [derived: gm-by-line] | $8.3M | $3.8M | 45.9% | 8.5% | -1.5 pts |
| SP6500 [src: commercial/internal-financials@2026-07-27] [derived: gm-by-line] | $7.0M | $3.4M | 48.9% | 7.6% | +0.0 pts |

- Window = trailing 4 quarters anchored at the latest period in the pinned snapshot (2026-Q2) — no clocks [config: commercial.yml] [src: commercial/internal-financials@2026-07-27]
- Totals: revenue $88.2M, gross margin $45.2M (51.2%) [derived: totals-stat] [src: commercial/internal-financials@2026-07-27]
- Quarterly revenue trajectory is charted for the top 3 lines by trailing-4Q revenue, remaining lines aggregated as one series to respect the chart-line cap [config: commercial.yml] [derived: revenue-trend]

## Assumptions & expectations — plan vs actual

_`unvalidated` means the expectation itself is a stand-in that has not been grounded
in a plan of record or the risk file — challenge the assumption, not just the actual._

| ID | Expectation | Expected | Actual | Verdict | Basis |
|---|---|---|---|---|---|
| E-01.1 | Every product line is gross-margin positive over the trailing four quarters [derived: gm-by-line] [config: commercial.yml] | gross margin > 0 per line, trailing 4Q | all lines positive; thinnest is PP3000 at 45.3% | met (unvalidated) | generic portfolio guardrail; no board-adopted floor |

## Narrative — Risks / Mitigations / Issues

### Risks (potential — mitigation identified)

- **R1 (medium)** — IP5000 gross margin is compressing — 45.9% in the trailing window vs 47.4% in the prior four quarters (-1.5 pts) [derived: gm-trend] [src: commercial/internal-financials@2026-07-27] [config: commercial.yml]
  - _Mitigation_: Review pricing and COGS drivers for the line; set a floor at which the phase-out conversation formally opens [derived: gm-trend] [src: commercial/internal-financials@2026-07-27] [config: commercial.yml]
- **R2 (medium)** — PP3000 gross margin is compressing — 45.3% in the trailing window vs 46.8% in the prior four quarters (-1.5 pts) [derived: gm-trend] [src: commercial/internal-financials@2026-07-27] [config: commercial.yml]
  - _Mitigation_: Review pricing and COGS drivers for the line; set a floor at which the phase-out conversation formally opens [derived: gm-trend] [src: commercial/internal-financials@2026-07-27] [config: commercial.yml]

### Watch

- **W1 (medium)** — Gross margin only — no opex allocation exists per line, so a GM-positive line can still consume the company at operating level (stated data gap) [derived: opex-by-line]

## Data gap (stated, not papered over)

- No per-line operating-expense allocation exists in the corpus — "consumes the
  company" is asserted at gross-margin level only; the opex series is marked
  unavailable [derived: opex-by-line].

## Method & provenance

- Revenue and COGS measured from [src: commercial/internal-financials@2026-07-27] (all regions, all revenue types);
  gross margin, shares, and margin drift are arithmetic derivations
  [derived: gm-by-line] [derived: gm-trend].
- Funds-vs-consumes rule and the trend-chart grouping are committed in the analysis
  plan; window length and grouping constants live in [config: commercial.yml].
