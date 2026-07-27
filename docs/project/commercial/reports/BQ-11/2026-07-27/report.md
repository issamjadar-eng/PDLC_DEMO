# BQ-11 — Sold but underused: utilization divergence at connected sites

_Demo sample data — not for clinical use._

**Verdict**: 6 connected site(s) ran below 60% of expected infusion hours over 2026-05..2026-07 (worst 34.0%); 2 clear the ≥10-connected-device materiality bar (S-NA-22, S-EMEA-02); the account-revenue tie the question asks for is blocked — no site→account key exists in any pinned dataset [derived: v-main] [src: commercial/internal-telemetry-utilization@2026-07-27] [src: commercial/internal-fleet@2026-07-27] [config: commercial.yml]

## Flagged sites (trailing 3 months: 2026-05..2026-07) [config: commercial.yml]

_Scope: Cloud Suite CONNECTED devices only — unconnected fleet utilization is
unobservable and is a stated gap, not an extrapolation. Site utilization is
hours-weighted: total infusion hours ÷ total expected hours over the window
[src: commercial/internal-telemetry-utilization@2026-07-27]. Materiality = ≥10 connected devices per the fleet registry [src: commercial/internal-fleet@2026-07-27] [config: commercial.yml]._

| Site | Region | Utilization (window) | Connected devices | Tier |
|---|---|---|---|---|
| S-NA-13 [derived: flagged-sites] [src: commercial/internal-telemetry-utilization@2026-07-27] | NA | 34.0% | 5 | below materiality bar — watch |
| S-NA-22 [derived: flagged-sites] [src: commercial/internal-telemetry-utilization@2026-07-27] | NA | 35.3% | 19 | MATERIAL — intervene |
| S-NA-03 [derived: flagged-sites] [src: commercial/internal-telemetry-utilization@2026-07-27] | NA | 36.4% | 8 | below materiality bar — watch |
| S-NA-16 [derived: flagged-sites] [src: commercial/internal-telemetry-utilization@2026-07-27] | NA | 36.5% | 5 | below materiality bar — watch |
| S-EMEA-02 [derived: flagged-sites] [src: commercial/internal-telemetry-utilization@2026-07-27] | EMEA | 36.6% | 16 | MATERIAL — intervene |
| S-APAC-06 [derived: flagged-sites] [src: commercial/internal-telemetry-utilization@2026-07-27] | APAC | 37.0% | 6 | below materiality bar — watch |

- Connected-site median utilization over the window: 89.6% across 46 sites — the flagged sites sit far below the fleet norm [derived: site-utilization] [src: commercial/internal-telemetry-utilization@2026-07-27]

## Churn-risk framing — what the data allows

- Account-level revenue at risk: NOT COMPUTABLE — no site→account key in any pinned
  dataset; published as an unavailable series naming the missing join
  [derived: account-revenue-at-risk].
- Regional context (explicitly context, not attribution): FY2026H1 direct-book revenue APAC $4,898,604, EMEA $7,039,112, NA $13,187,364 — flagged sites sit inside these books [src: commercial/internal-sales-accounts@2026-07-27]

## Monthly trajectory (worst three flagged sites vs fleet median)

- Charted per month across the full snapshot span; pick rule: the three lowest-utilization flagged sites plus the connected-fleet median as reference (≤4 lines) [derived: monthly-utilization] [src: commercial/internal-telemetry-utilization@2026-07-27]

## Assumptions & expectations — plan vs actual

_`unvalidated` means the expectation itself is a stand-in that has not been grounded
in a plan of record or the risk file — challenge the assumption, not just the actual._

| ID | Expectation | Expected | Actual | Verdict | Basis |
|---|---|---|---|---|---|
| E-11.1 | No material account runs its connected fleet below the utilization floor [derived: flagged-sites] [src: commercial/internal-telemetry-utilization@2026-07-27] [src: commercial/internal-fleet@2026-07-27] [config: commercial.yml] | >= 60% of expected hours at every account with >= 10 connected devices | site-level proxy (account join unavailable): 2 site(s) with >= 10 connected devices below 60%: S-NA-22 35.3%; S-EMEA-02 36.6% | not-met (unvalidated) | stand-in utilization floor; contracts set no usage commitment |

## Narrative — Risks / Mitigations / Issues

### Issues (materialized — needs action)

- **I1 (high)** — S-NA-22 runs at 35.3% of expected hours across 19 connected devices over 2026-05..2026-07 — sold-but-underused at material scale (early churn warning) [derived: flagged-sites] [src: commercial/internal-telemetry-utilization@2026-07-27] [src: commercial/internal-fleet@2026-07-27]
  - _Action_: Customer-success intervention this month: confirm case-mix vs shelfware vs connectivity root cause on site; review against renewal timeline [derived: flagged-sites] [src: commercial/internal-telemetry-utilization@2026-07-27] [src: commercial/internal-fleet@2026-07-27]
- **I2 (high)** — S-EMEA-02 runs at 36.6% of expected hours across 16 connected devices over 2026-05..2026-07 — sold-but-underused at material scale (early churn warning) [derived: flagged-sites] [src: commercial/internal-telemetry-utilization@2026-07-27] [src: commercial/internal-fleet@2026-07-27]
  - _Action_: Customer-success intervention this month: confirm case-mix vs shelfware vs connectivity root cause on site; review against renewal timeline [derived: flagged-sites] [src: commercial/internal-telemetry-utilization@2026-07-27] [src: commercial/internal-fleet@2026-07-27]

### Risks (potential — mitigation identified)

- **R1 (high)** — Account-level revenue-at-risk cannot be computed: no pinned dataset carries a site→account key (sales-accounts is account-level with no site list) — the churn-risk framing stops at regional context [derived: account-revenue-at-risk]
  - _Mitigation_: Acquire a site→account mapping (CRM account-hierarchy export) as a corpus dataset; until then intervention priority uses site scale, not dollars [derived: account-revenue-at-risk]
- **R2 (medium)** — expected_hours is the dataset's per-segment norm, not a contract term — a site with a legitimately different case mix looks underused against it [src: commercial/internal-telemetry-utilization@2026-07-27]
  - _Mitigation_: Validate the norm against contracted usage or peer-cohort baselines before escalating beyond customer-success outreach [src: commercial/internal-telemetry-utilization@2026-07-27]

### Watch

- **W1 (medium)** — 4 additional site(s) below the floor but under the 10-device materiality bar: S-NA-13 (34.0%, 5 devices), S-NA-03 (36.4%, 8 devices), S-NA-16 (36.5%, 5 devices), S-APAC-06 (37.0%, 6 devices) — materiality filters priority, not visibility [derived: flagged-sites] [src: commercial/internal-fleet@2026-07-27]

## Method & provenance

- Utilization measured from [src: commercial/internal-telemetry-utilization@2026-07-27]; connected-device counts from the fleet registry [src: commercial/internal-fleet@2026-07-27]; thresholds and window from [config: commercial.yml].
- Regional revenue context from [src: commercial/internal-sales-accounts@2026-07-27] (demo-fabricated direct book).
- E-11.1 is account-scoped but evaluated at site level as a proxy [derived: flagged-sites]
  — the site→account join gap is the reason, and closing it is the named fix.
