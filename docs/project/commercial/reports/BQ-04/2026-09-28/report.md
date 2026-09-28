# BQ-04 — Subscription unit economics: LTV vs cost-to-serve, and the discount signal

_Demo sample data — not for clinical use._

**Verdict**: Unit economics fail the guardrail: LTV per connected pump $2,237 vs $2,720 cost-to-serve over the same 5-year horizon (ratio 0.82 vs the 3.0 floor); 28 of 39 active sites run ARR below cost-to-serve — concentrated in small sites — and the mean hardware discount at subscribed sites is 5.8% vs the 5% tolerance [derived: v-main] [src: commercial/internal-subscriptions@2026-09-28] [config: commercial.yml]

## Fleet-wide unit economics (active subscribed sites)

_LTV model (stated, deliberately simple): per-pump ARR × the configured horizon —
undiscounted, no churn decrement, no growth. Churned sites are excluded from the rates
but counted below; their existence means the no-churn horizon OVERSTATES LTV._

- ARR per connected pump: $447/yr; cost-to-serve per pump: $544/yr [derived: unit-econ-stat] [src: commercial/internal-subscriptions@2026-09-28]
- LTV over 5 years: $2,237 vs $2,720 cost — ratio 0.82 (guardrail 3.0) [derived: unit-econ-stat] [config: commercial.yml]
- Basis: 39 active sites, 295 connected pumps; 3 churned sites (7.1% of register rows) [src: commercial/internal-subscriptions@2026-09-28]
- Fleet context: 331 connected devices in the installed base; 4 connected sites with no subscription (attach gap) [derived: attach-gap] [src: commercial/internal-fleet@2026-09-28]

## Site-size profitability split

- Bands on connected-pump count [config: commercial.yml]:

| Band | Sites | Pumps | ARR/pump/yr | Cost/pump/yr | Margin/pump/yr | ARR-below-cost sites | Mean hw discount |
|---|---|---|---|---|---|---|---|
| small (<= 6 pumps) [src: commercial/internal-subscriptions@2026-09-28] [derived: band-economics] | 24 | 92 | $453 | $913 | $-460 | 24 | 5.6% |
| mid (7-11 pumps) [src: commercial/internal-subscriptions@2026-09-28] [derived: band-economics] | 6 | 47 | $452 | $516 | $-64 | 4 | 6.4% |
| large (>= 12 pumps) [src: commercial/internal-subscriptions@2026-09-28] [derived: band-economics] | 9 | 156 | $443 | $334 | $108 | 0 | 5.6% |

- 28 of 39 active sites run ARR below annual cost-to-serve [derived: band-economics] [src: commercial/internal-subscriptions@2026-09-28]

## Hardware-discount signal (cannibalization)

- Mean hardware discount at active subscribed sites: 5.8% vs the 5% tolerance [derived: discount-by-band] [config: commercial.yml] [src: commercial/internal-subscriptions@2026-09-28]
- Threshold sensitivity (disclosed): the miss is +0.8pp on an n=39 mean with SE ≈ 0.4pp — a knife-edge flagged on |miss| ≤ 1pp (the miss is 2.1 standard errors from the stand-in tolerance); the verdict is fragile to the unvalidated threshold choice (see W3) [derived: discount-sensitivity] [config: commercial.yml]
- No unsubscribed-site discount baseline exists in the corpus, so this is a signal at
  subscribed sites, not a causal cannibalization claim (stated in the analysis plan).

## Assumptions & expectations — plan vs actual

_`unvalidated` means the expectation itself is a stand-in that has not been grounded
in a plan of record or the risk file — challenge the assumption, not just the actual._

| ID | Expectation | Expected | Actual | Verdict | Basis |
|---|---|---|---|---|---|
| E-04.1 | Lifetime value per connected pump covers cost-to-serve at a healthy multiple [derived: unit-econ-stat] [config: commercial.yml] | LTV : cost-to-serve >= 3.0 | ratio 0.82 (ARR $447/pump/yr vs cost $544/pump/yr, active sites; ratio computed on raw sums, rounded for display) | not-met (unvalidated) | generic SaaS unit-economics heuristic; no underwritten target |
| E-04.2 | Cloud Suite attach does not erode hardware pricing beyond tolerance [derived: discount-by-band] [derived: discount-sensitivity] [config: commercial.yml] | avg hardware discount at subscribed sites <= 5% | mean hardware discount 5.8% across 39 active subscribed sites — +0.8pp vs the 5% stand-in line; KNIFE-EDGE on |miss| ≤ 1pp (miss = 2.1 SE, SE ≈ 0.4pp, n=39) against an unvalidated threshold — verdict fragile to the stand-in choice | not-met (unvalidated) | stand-in tolerance; pricing policy sets no explicit cap |

## Narrative — Risks / Mitigations / Issues

### Issues (materialized — needs action)

- **I1 (high)** — Small sites are negative at unit level: 24 sites (<= 6 pumps) run $460/pump/yr below water (24 of them ARR-below-cost individually) [derived: band-economics] [src: commercial/internal-subscriptions@2026-09-28] [config: commercial.yml]
  - _Action_: Set a minimum-deal-size or platform-fee floor for new subscriptions; review the serve model (remote-first) for the existing small-site tail [derived: band-economics] [src: commercial/internal-subscriptions@2026-09-28] [config: commercial.yml]
- **I2 (medium)** — Mean hardware discount at subscribed sites is 5.8%, over the 5% tolerance — the subscription may be being bought with hardware price [derived: discount-by-band] [src: commercial/internal-subscriptions@2026-09-28] [config: commercial.yml]
  - _Action_: Pull deal-level pricing for subscribed vs unsubscribed sites; without an unsubscribed baseline in the corpus, causality stays unproven either way [derived: discount-by-band] [src: commercial/internal-subscriptions@2026-09-28] [config: commercial.yml]

### Risks (potential — mitigation identified)

- **R1 (high)** — Fleet-wide LTV:cost-to-serve is 0.82, under the 3.0 floor — and the LTV side is flattered by the model (no churn decrement, no discounting) while 3 churned sites already exist [derived: unit-econ-stat] [src: commercial/internal-subscriptions@2026-09-28] [config: commercial.yml]
  - _Mitigation_: Fix the cost side (serve model) before growing the small-site tail; re-underwrite the floor once a churn-adjusted LTV is possible [derived: unit-econ-stat] [src: commercial/internal-subscriptions@2026-09-28] [config: commercial.yml]

### Watch

- **W1 (medium)** — Attach gap: 4 connected sites carry no subscription (S-APAC-08, S-EMEA-08, S-EMEA-13, S-NA-21) — expansion revenue that needs no new hardware [derived: attach-gap] [src: commercial/internal-fleet@2026-09-28] [src: commercial/internal-subscriptions@2026-09-28]
- **W2 (medium)** — Churn on file: 3 of 42 register rows (7.1%) — direct evidence that the no-churn 5-year horizon overstates LTV [derived: unit-econ-stat] [src: commercial/internal-subscriptions@2026-09-28]
- **W3 (medium)** — E-04.2 is a knife-edge: the mean hardware discount misses the 5% stand-in tolerance by +0.8pp on an n=39 mean (SE ≈ 0.4pp; the miss is 2.1 standard errors from the line; flagged on |miss| ≤ 1pp) — the verdict is fragile to the unvalidated stand-in threshold choice; treat it as a watch signal, not a breach finding, until pricing policy sets a real cap [derived: discount-sensitivity] [derived: discount-by-band] [config: commercial.yml] [src: commercial/internal-subscriptions@2026-09-28]

## Method & provenance

- ARR, cost-to-serve, status, and discounts measured from [src: commercial/internal-subscriptions@2026-09-28]; connectivity and the attach gap from [src: commercial/internal-fleet@2026-09-28].
- LTV, ratios, bands, and means are arithmetic derivations with methods declared per series [derived: unit-econ-stat] [derived: band-economics].
- The ARR-build history is derived from active sites' start dates at current ARR — survivor-biased (churned sites' past ARR is absent) and stated as such [derived: arr-build] [src: commercial/internal-subscriptions@2026-09-28]. True economics history needs recurring register snapshots (stated gap).
