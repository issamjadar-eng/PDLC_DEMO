# FQ-06 — Working capital: DSO, over-90 AR, inventory days, cash trapped

_Demo sample data — not for clinical use._

**Verdict**: As of 2026-08: company DSO 55.2 days vs 50 target (OVER); Northgate Purchasing Group DSO 80.0 days with over-90 share 32.5% (1 of 4 channels over the 15% threshold); inventory days over the 75-day target on 2 of 5 lines (PP3000 134, IP5000 120); cash trapped $3.36M = $1.77M over-90 AR + $1.59M inventory above target cover [derived: v-main] [src: finance/internal-ar-inventory@2026-09-08] [config: finance.yml]

## Receivables by channel

_Latest period 2026-08 in the pin (history 2025-01..2026-08) [src: finance/internal-ar-inventory@2026-09-08]; DSO aggregated as Σ AR ÷ Σ (AR ÷ DSO); targets [config: finance.yml]._

| Channel | AR $M | DSO days | Over-90 $M | Over-90 share |
|---|---|---|---|---|
| Cascadia Supply Co-op [src: finance/internal-ar-inventory@2026-09-08] | 1.33 | 54.1 | 0.11 | 8.5% |
| Meridian Health Alliance [src: finance/internal-ar-inventory@2026-09-08] | 2.22 | 46.5 | 0.14 | 6.5% |
| Northgate Purchasing Group [src: finance/internal-ar-inventory@2026-09-08] | 3.68 | 80.0 | 1.20 | 32.5% ⚠️ |
| direct [src: finance/internal-ar-inventory@2026-09-08] | 5.73 | 49.2 | 0.31 | 5.5% |
| **Company** [src: finance/internal-ar-inventory@2026-09-08] | 12.97 | 55.2 | 1.77 | 13.6% |

## Receivables by region

| Region | AR $M | DSO days | Over-90 share |
|---|---|---|---|
| APAC [src: finance/internal-ar-inventory@2026-09-08] | 2.05 | 58.2 | 9.9% |
| EMEA [src: finance/internal-ar-inventory@2026-09-08] | 3.99 | 56.4 | 11.8% |
| NA [src: finance/internal-ar-inventory@2026-09-08] | 6.93 | 53.7 | 15.8% |

## Inventory by product line

_Days aggregated as Σ inventory ÷ Σ (inventory ÷ days); excess = value above 75 days of cover [config: finance.yml] [src: finance/internal-ar-inventory@2026-09-08]._

| Product line | Inventory $M | Days of cover | Excess above target $M |
|---|---|---|---|
| IP5000 [src: finance/internal-ar-inventory@2026-09-08] | 1.36 | 120.0 ⚠️ | 0.51 |
| PP3000 [src: finance/internal-ar-inventory@2026-09-08] | 2.45 | 134.1 ⚠️ | 1.08 |
| PP3500 [src: finance/internal-ar-inventory@2026-09-08] | 3.28 | 55.9 | 0.00 |
| SP6000 [src: finance/internal-ar-inventory@2026-09-08] | 0.89 | 63.1 | 0.00 |
| SP6500 [src: finance/internal-ar-inventory@2026-09-08] | 0.60 | 61.4 | 0.00 |

## Cash trapped

- Over-90 receivables $1.77M + inventory above target cover $1.59M = $3.36M at 2026-08 [derived: cash-trapped] [src: finance/internal-ar-inventory@2026-09-08] [config: finance.yml].

## Subscription receivables: not in the cube (stated, not approximated)

- The working-capital cube carries the five device lines only [src: finance/internal-ar-inventory@2026-09-08]; cloud-suite subscription billing needs its own AR feed before it joins the company DSO [derived: subscription-ar].

## Assumptions & expectations — plan vs actual

_`unvalidated` means the expectation itself is a stand-in that has not been grounded
in a plan of record or the risk file — challenge the assumption, not just the actual._

| ID | Expectation | Expected | Actual | Verdict | Basis |
|---|---|---|---|---|---|
| E-06.1 | Company DSO stays at or below target [derived: dso-stat] [derived: dso-by-channel] [config: finance.yml] | DSO <= 50 days | 55.2 days company DSO at 2026-08; worst channel Northgate Purchasing Group 80.0 days | not-met (unvalidated) | treasury working-capital target carried forward; no board-adopted target on file [VERIFY] |
| E-06.2 | No channel's over-90 receivables exceed the escalation threshold [derived: over90-by-channel] [config: finance.yml] | over-90 share <= 15% per channel | 1 of 4 channels over 15%: Northgate Purchasing Group 32.5% | not-met (unvalidated) | credit-policy escalation trigger; not confirmed against the credit policy on file [VERIFY] |
| E-06.3 | Inventory days per product line stay within target cover [derived: inventory-days-by-line] [config: finance.yml] | inventory days <= 75 per line | 2 of 5 lines over 75 days: PP3000 134.1, IP5000 120.0 | not-met (unvalidated) | operations planning target; no S&OP policy names a ceiling [VERIFY] |

## Narrative — Risks / Mitigations / Issues

### Issues (materialized — needs action)

- **I1 (high)** — Northgate Purchasing Group: over-90 receivables $1.20M of $3.68M (32.5%) at 2026-08, DSO 80.0 days — over-90 share was 8.7% at 2025-01 [derived: over90-by-channel] [derived: over90-trend] [src: finance/internal-ar-inventory@2026-09-08] [config: finance.yml]
  - _Action_: Collections escalation with the channel's contracting lead; hold new shipments against a payment plan; assess bad-debt provision [derived: over90-by-channel] [derived: over90-trend] [src: finance/internal-ar-inventory@2026-09-08] [config: finance.yml]
- **I2 (medium)** — PP3000 inventory 134.1 days of cover ($2.45M held, $1.08M above the 75-day target) at 2026-08 [derived: inventory-days-by-line] [derived: inventory-days-trend] [src: finance/internal-ar-inventory@2026-09-08] [config: finance.yml]
  - _Action_: Run-down plan: stop replenishment, redirect demand to the successor line, review obsolescence reserve [derived: inventory-days-by-line] [derived: inventory-days-trend] [src: finance/internal-ar-inventory@2026-09-08] [config: finance.yml]
- **I3 (medium)** — IP5000 inventory 120.0 days of cover ($1.36M held, $0.51M above the 75-day target) at 2026-08 [derived: inventory-days-by-line] [derived: inventory-days-trend] [src: finance/internal-ar-inventory@2026-09-08] [config: finance.yml]
  - _Action_: Run-down plan: stop replenishment, redirect demand to the successor line, review obsolescence reserve [derived: inventory-days-by-line] [derived: inventory-days-trend] [src: finance/internal-ar-inventory@2026-09-08] [config: finance.yml]

### Risks (potential — mitigation identified)

- **R1 (medium)** — The DSO target (50 days), over-90 threshold (15%) and inventory target (75 days) are stand-ins — no treasury, credit, or S&OP policy on file names them [config: finance.yml]
  - _Mitigation_: Ratify the three targets with treasury / credit / operations and mark E-06.1..E-06.3 validated [config: finance.yml]

### Watch

- **W1 (medium)** — Company over-90 share 13.6% of $12.97M receivables — the channel cut, not the total, is where the exposure sits [derived: over90-by-channel] [src: finance/internal-ar-inventory@2026-09-08]
- **W2 (medium)** — Subscription (cloud-suite) receivables are not in the working-capital cube — company DSO covers device lines only [derived: subscription-ar] [src: finance/internal-ar-inventory@2026-09-08]

## Method & provenance

- All figures from [src: finance/internal-ar-inventory@2026-09-08] at the latest period; targets [config: finance.yml]; ratios aggregate by implied daily flow, never by averaging.
- Historical view: monthly over-90 share per channel [derived: over90-trend] and inventory days per line [derived: inventory-days-trend] are charted over the full history [src: finance/internal-ar-inventory@2026-09-08].
- Verdict and expectation actuals carry the channel and line breach counts so a rollup cannot drop them [derived: v-main].
