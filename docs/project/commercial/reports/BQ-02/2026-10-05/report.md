# BQ-02 — Concentration: GPOs, accounts, franchise — and the anchor-GPO loss scenario

_Demo sample data — not for clinical use._

**Verdict**: Meridian Health Alliance carries 38.4% of FY2025 direct-book revenue — above the 30% guardrail on the direct-book basis, and basis-sensitive: the direct book covers 50.6% of total FY2025 revenue, and Meridian Health Alliance's floor share of TOTAL revenue is 19.4% (under the guardrail); top-3 accounts 25.5%, PCA franchise 74.5%; losing the anchor GPO dents every plan year by $15.6M (14.9% of the FY2026 plan) under the stated constant-dent scenario [derived: v-main] [src: commercial/internal-sales-accounts@2026-10-05] [src: commercial/internal-revenue-plan@2026-10-05] [config: commercial.yml]

## FY2025 direct-book revenue by GPO [src: commercial/internal-sales-accounts@2026-10-05]

_Basis: the account-attributed direct book (hardware + subscription) — consumables and
service flow through distributors and are not in these shares (see the analysis plan)._

| GPO | Revenue | Share |
|---|---|---|
| independent [src: commercial/internal-sales-accounts@2026-10-05] | $19.9M | 48.9% |
| Meridian Health Alliance [src: commercial/internal-sales-accounts@2026-10-05] | $15.6M | 38.4% ⚠️ |
| Cascadia Health Partners [src: commercial/internal-sales-accounts@2026-10-05] | $2.8M | 6.9% |
| AtlasPoint Purchasing [src: commercial/internal-sales-accounts@2026-10-05] | $1.4M | 3.3% |
| NovaBridge Alliance [src: commercial/internal-sales-accounts@2026-10-05] | $1.0M | 2.4% |

- Guardrail: no GPO above 30% of annual revenue [config: commercial.yml]
- FY2025 direct-book total: $40.7M [src: commercial/internal-sales-accounts@2026-10-05]

## Basis sensitivity (disclosed, not absorbed)

_The E-02.1 guardrail is worded against **annual revenue**, but the only account-attributed denominator is the direct book — the verdict is basis-dependent and both bases are shown [derived: basis-sensitivity]._

- The direct book ($40.7M) covers 50.6% of total FY2025 revenue ($80.5M) [derived: basis-sensitivity] [src: commercial/internal-sales-accounts@2026-10-05] [src: commercial/internal-financials@2026-10-05]
- Meridian Health Alliance's floor share of TOTAL FY2025 revenue is 19.4% — a lower bound: it takes none of the distributor-routed consumables/service book, whose account attribution does not exist in the corpus; the true share is unknowable above that floor [derived: basis-sensitivity] [src: commercial/internal-financials@2026-10-05]
- Verdict by basis: direct book 38.4% — BREACHES the 30% guardrail; floor-of-total 19.4% — does NOT breach it [derived: basis-sensitivity] [config: commercial.yml]

## Top-3 accounts (FY2025) [src: commercial/internal-sales-accounts@2026-10-05]

| Account | Revenue | Share |
|---|---|---|
| Northgate Health System [src: commercial/internal-sales-accounts@2026-10-05] | $4.5M | 11.0% |
| Clearwater Health Alliance [src: commercial/internal-sales-accounts@2026-10-05] | $3.3M | 8.0% |
| Redwing Health System [src: commercial/internal-sales-accounts@2026-10-05] | $2.6M | 6.5% |

- Top-3 combined: 25.5% of FY2025 direct-book revenue [derived: top-accounts]

## Franchise concentration

- PCA franchise (PP3500 + PP3000 + cloud-suite per [config: commercial.yml]): 74.5% of FY2025 direct book; pumps alone (PP3500 + PP3000) 58.8% [derived: franchise-share] [src: commercial/internal-sales-accounts@2026-10-05]

## Anchor-GPO loss scenario vs the plan trajectory

- Method (stated): subtract Meridian Health Alliance's FY2025 direct-book revenue ($15.6M), held constant, from each plan year — a deliberate floor: the dent is not grown with the plan and covers the direct book only [derived: plan-loss-scenario] [src: commercial/internal-revenue-plan@2026-10-05] [src: commercial/internal-sales-accounts@2026-10-05]

| Plan year | Plan of record | Minus anchor GPO | Dent |
|---|---|---|---|
| FY2026 [src: commercial/internal-revenue-plan@2026-10-05] [derived: plan-loss-scenario] | $105.0M | $89.4M | 14.9% |
| FY2027 [src: commercial/internal-revenue-plan@2026-10-05] [derived: plan-loss-scenario] | $130.0M | $114.4M | 12.0% |
| FY2028 [src: commercial/internal-revenue-plan@2026-10-05] [derived: plan-loss-scenario] | $170.0M | $154.4M | 9.2% |
| FY2029 [src: commercial/internal-revenue-plan@2026-10-05] [derived: plan-loss-scenario] | $245.0M | $229.4M | 6.4% |
| FY2030 [src: commercial/internal-revenue-plan@2026-10-05] [derived: plan-loss-scenario] | $350.0M | $334.4M | 4.5% |

## Assumptions & expectations — plan vs actual

_`unvalidated` means the expectation itself is a stand-in that has not been grounded
in a plan of record or the risk file — challenge the assumption, not just the actual._

| ID | Expectation | Expected | Actual | Verdict | Basis |
|---|---|---|---|---|---|
| E-02.1 | No single GPO carries more than 30% of annual revenue [derived: share-by-gpo] [derived: basis-sensitivity] [config: commercial.yml] | <= 30% of FY revenue per GPO | Meridian Health Alliance at 38.4% of FY2025 direct-book revenue; all other GPOs within the guardrail — BASIS-SENSITIVE: the expectation says annual revenue, but the test denominator is the direct book (50.6% of total FY2025 revenue); Meridian Health Alliance's floor share of total revenue is 19.4%, which does NOT breach the guardrail (distributor-routed revenue unattributed) | not-met (unvalidated) | generic concentration guardrail; no board-adopted limit |

## Narrative — Risks / Mitigations / Issues

### Issues (materialized — needs action)

- **I1 (high)** — Meridian Health Alliance holds 38.4% of FY2025 direct-book revenue — over the 30% concentration guardrail [derived: share-by-gpo] [src: commercial/internal-sales-accounts@2026-10-05] [config: commercial.yml]
  - _Action_: Bring contract-renewal timeline and diversification options to the board; acquire GPO contract terms as a corpus dataset so exposure gets a date [derived: share-by-gpo] [src: commercial/internal-sales-accounts@2026-10-05] [config: commercial.yml]

### Risks (potential — mitigation identified)

- **R1 (medium)** — Top-3 accounts hold 25.5% of FY2025 direct-book revenue — account-level concentration compounds the GPO concentration (largest: Northgate Health System at 11.0%) [derived: top-accounts] [src: commercial/internal-sales-accounts@2026-10-05]
  - _Mitigation_: Named-account retention plans for the top accounts; monitor share annually alongside the GPO read [derived: top-accounts] [src: commercial/internal-sales-accounts@2026-10-05]
- **R2 (medium)** — The loss scenario is a floor, not a forecast: the dent is held constant at the FY2025 anchor book ($15.6M) while the plan grows, and it covers the direct book only — the true dent of losing Meridian Health Alliance grows with the plan [derived: plan-loss-scenario] [src: commercial/internal-revenue-plan@2026-10-05]
  - _Mitigation_: Re-run with anchor-share-of-plan scaling once GPO-level plan attribution exists; treat the charted scenario as the minimum impact [derived: plan-loss-scenario] [src: commercial/internal-revenue-plan@2026-10-05]
- **R3 (medium)** — The E-02.1 verdict is basis-sensitive: the guardrail is worded against annual revenue but tested on the direct book, which covers 50.6% of total FY2025 revenue — Meridian Health Alliance breaches on the direct book (38.4%) while its floor share of total revenue (19.4%) does not breach [derived: basis-sensitivity] [src: commercial/internal-sales-accounts@2026-10-05] [src: commercial/internal-financials@2026-10-05]
  - _Mitigation_: Acquire account-attributed consumables/service revenue (or GPO attribution on the distributor book) to close the denominator gap; until then read the verdict on both bases, not one [derived: basis-sensitivity] [src: commercial/internal-sales-accounts@2026-10-05] [src: commercial/internal-financials@2026-10-05]

### Watch

- **W1 (medium)** — PCA-franchise dependence (74.5% of FY2025 direct book incl. Cloud Suite; pumps alone 58.8%) — single-franchise exposure rides on top of the customer concentration [derived: franchise-share] [src: commercial/internal-sales-accounts@2026-10-05]

## Method & provenance

- Shares measured from the account book [src: commercial/internal-sales-accounts@2026-10-05]; plan trajectory from the plan of record [src: commercial/internal-revenue-plan@2026-10-05]; guardrail and franchise definition in [config: commercial.yml].
- GPO-share history across the fiscal years on file is charted [derived: gpo-share-trend] [src: commercial/internal-sales-accounts@2026-10-05].
- Contract terms, renewal dates, and total-P&L (consumables/service) concentration are
  stated data gaps — no series is faked for them (see the analysis plan).
