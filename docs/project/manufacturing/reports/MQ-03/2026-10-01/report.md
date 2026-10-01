# MQ-03 — Nonconformance and CAPA: rate, aging, past-due share, effectiveness backlog

_Demo sample data — not for clinical use._

**Verdict**: At 2026-08-31: 32 open CAPAs, 21 past due (66%), 5 critical past due; past-due count rising (6 six months earlier → 21); effectiveness verified on 28 of 47 closed CAPAs (60% vs 90% floor, backlog 19); 19 open NCRs (9 past due, mean age 129 d), NCR intake 11.7/month vs 10.7 prior; supplier NCRs concentrate on SUP-003 (21 of 45, 47%) [derived: v-main] [src: manufacturing/internal-ncr-capa@2026-09-28] [config: manufacturing.yml]

## Headline

- Status is evaluated at the snapshot as-of 2026-08-31: open = no closure date; past due = open and due date passed; effectiveness floor 90% [src: manufacturing/internal-ncr-capa@2026-09-28] [config: manufacturing.yml].
- Open CAPAs 32, past due 21 (65.6%), critical past due 5; median days over due among past-due CAPAs 107 [derived: capa-stat] [src: manufacturing/internal-ncr-capa@2026-09-28].
- Closed CAPAs 47: verified 28, unverified backlog 19 (59.6% verified) [derived: capa-stat] [src: manufacturing/internal-ncr-capa@2026-09-28].
- Open NCRs 19 (9 past due), mean open age 129 d, median 29 d [derived: ncr-open-by-severity] [src: manufacturing/internal-ncr-capa@2026-09-28].

## Open CAPAs by source

| Source | Open | Past due |
|---|---|---|
| production [src: manufacturing/internal-ncr-capa@2026-09-28] | 18 | 11 |
| supplier [src: manufacturing/internal-ncr-capa@2026-09-28] | 4 | 3 |
| complaint [src: manufacturing/internal-ncr-capa@2026-09-28] | 2 | 1 |
| audit [src: manufacturing/internal-ncr-capa@2026-09-28] | 5 | 3 |
| field [src: manufacturing/internal-ncr-capa@2026-09-28] | 3 | 3 |

## Open CAPAs by severity

| Severity | Open | Past due |
|---|---|---|
| minor [src: manufacturing/internal-ncr-capa@2026-09-28] | 12 | 8 |
| major [src: manufacturing/internal-ncr-capa@2026-09-28] | 14 | 8 |
| critical [src: manufacturing/internal-ncr-capa@2026-09-28] | 6 | 5 |

## Open NCRs by severity (aging)

| Severity | Open | Mean age (days) |
|---|---|---|
| minor [src: manufacturing/internal-ncr-capa@2026-09-28] | 14 | 84 |
| major [src: manufacturing/internal-ncr-capa@2026-09-28] | 3 | 231 |
| critical [src: manufacturing/internal-ncr-capa@2026-09-28] | 2 | 290 |

## NCRs opened by source — 2026-06..2026-08

| Source | NCRs opened |
|---|---|
| production [src: manufacturing/internal-ncr-capa@2026-09-28] | 16 |
| supplier [src: manufacturing/internal-ncr-capa@2026-09-28] | 7 |
| complaint [src: manufacturing/internal-ncr-capa@2026-09-28] | 2 |
| audit [src: manufacturing/internal-ncr-capa@2026-09-28] | 5 |
| field [src: manufacturing/internal-ncr-capa@2026-09-28] | 5 |

## Effectiveness verification by closure quarter

| Closure quarter | Verified | Not verified |
|---|---|---|
| 2025-Q1 [src: manufacturing/internal-ncr-capa@2026-09-28] | 3 | 1 |
| 2025-Q2 [src: manufacturing/internal-ncr-capa@2026-09-28] | 7 | 0 |
| 2025-Q3 [src: manufacturing/internal-ncr-capa@2026-09-28] | 7 | 4 |
| 2025-Q4 [src: manufacturing/internal-ncr-capa@2026-09-28] | 9 | 3 |
| 2026-Q1 [src: manufacturing/internal-ncr-capa@2026-09-28] | 1 | 6 |
| 2026-Q2 [src: manufacturing/internal-ncr-capa@2026-09-28] | 0 | 4 |
| 2026-Q3 [src: manufacturing/internal-ncr-capa@2026-09-28] | 1 | 1 |

## Supplier-sourced NCRs by supplier

| Supplier | NCRs |
|---|---|
| SUP-003 [src: manufacturing/internal-ncr-capa@2026-09-28] | 21 |
| SUP-002 [src: manufacturing/internal-ncr-capa@2026-09-28] | 5 |
| SUP-011 [src: manufacturing/internal-ncr-capa@2026-09-28] | 5 |
| SUP-001 [src: manufacturing/internal-ncr-capa@2026-09-28] | 3 |
| SUP-006 [src: manufacturing/internal-ncr-capa@2026-09-28] | 3 |
| SUP-005 [src: manufacturing/internal-ncr-capa@2026-09-28] | 2 |
| SUP-007 [src: manufacturing/internal-ncr-capa@2026-09-28] | 2 |
| SUP-012 [src: manufacturing/internal-ncr-capa@2026-09-28] | 2 |
| SUP-009 [src: manufacturing/internal-ncr-capa@2026-09-28] | 1 |
| SUP-010 [src: manufacturing/internal-ncr-capa@2026-09-28] | 1 |

## Assumptions & expectations — plan vs actual

_`unvalidated` means the expectation itself is a stand-in that has not been grounded
in a plan of record, a procedure, or the risk file — challenge the assumption, not just the actual._

| ID | Expectation | Expected | Actual | Verdict | Basis |
|---|---|---|---|---|---|
| E-03.1 | No critical CAPA is past its due date [derived: capa-open-by-severity] [config: manufacturing.yml] | 0 critical CAPAs past due | 5 critical CAPA(s) past due at 2026-08-31 | not-met (unvalidated) | stand-in; the CAPA procedure on record names no escalation rule for critical past-due items [VERIFY] |
| E-03.2 | Closed CAPAs carry a completed effectiveness verification [derived: effectiveness-by-quarter] [config: manufacturing.yml] | >= 90% of closed CAPAs effectiveness-verified | 60% of closed CAPAs effectiveness-verified (28 of 47) | not-met (unvalidated) | stand-in; the CAPA procedure on record names no verification-completion target [VERIFY] |

## Narrative — Risks / Mitigations / Issues

### Issues (materialized — needs action)

- **I1 (high)** — 5 critical CAPA(s) past due at 2026-08-31: CAPA-2025-0012 (449 d over, production), CAPA-2025-0039 (217 d over, production), CAPA-2026-0003 (152 d over, production), CAPA-2026-0005 (107 d over, supplier), CAPA-2026-0017 (23 d over, audit) [derived: capa-open-by-severity] [src: manufacturing/internal-ncr-capa@2026-09-28]
  - _Action_: Escalate to the management-review agenda; assign owners and re-baselined due dates this week [derived: capa-open-by-severity] [src: manufacturing/internal-ncr-capa@2026-09-28]
- **I2 (high)** — Effectiveness verification is lagging: 60% of closed CAPAs verified against a 90% floor; the backlog of 19 unverified closures grows by closure quarter [derived: effectiveness-by-quarter] [src: manufacturing/internal-ncr-capa@2026-09-28] [config: manufacturing.yml]
  - _Action_: Schedule effectiveness checks for the oldest closures first; do not close new CAPAs without a dated verification plan [derived: effectiveness-by-quarter] [src: manufacturing/internal-ncr-capa@2026-09-28] [config: manufacturing.yml]

### Risks (potential — mitigation identified)

- **R1 (high)** — CAPA aging is rising — past-due open CAPAs went from 6 to 21 over six months; median days over due among past-due items is 107 [derived: capa-pastdue-trend] [src: manufacturing/internal-ncr-capa@2026-09-28]
  - _Mitigation_: Cap concurrent open CAPAs per owner; convert stalled investigations into interim containment + re-scoped CAPAs [derived: capa-pastdue-trend] [src: manufacturing/internal-ncr-capa@2026-09-28]
- **R2 (medium)** — Supplier-sourced NCRs concentrate on SUP-003 (21 of 45) — a single supplier is driving the supplier nonconformance load [derived: supplier-ncr-concentration] [src: manufacturing/internal-ncr-capa@2026-09-28]
  - _Mitigation_: Cross-check with the supplier scorecard and audit currency (MQ-05); consider a supplier corrective action request [derived: supplier-ncr-concentration] [src: manufacturing/internal-ncr-capa@2026-09-28]

### Watch

- **W1 (medium)** — NCR intake 11.7/month in 2026-06..2026-08 vs 10.7/month in the prior three months; 9 open NCRs are past their due date [derived: ncr-trend] [derived: ncr-open-by-severity] [src: manufacturing/internal-ncr-capa@2026-09-28]

## Method & provenance

- All counts from the pinned NCR/CAPA register [src: manufacturing/internal-ncr-capa@2026-09-28]; the effectiveness floor is a plan constant [config: manufacturing.yml].
- The past-due history is reconstructed at each month-end from opened / due / closed dates, so the trend is exact for this register and needs no prior snapshots [derived: capa-pastdue-trend].
- NCR intake is charted monthly (all sources vs supplier-sourced) [derived: ncr-trend]; the supplier concentration uses the register's supplier_id on supplier-sourced NCRs [derived: supplier-ncr-concentration].
- Not computed: an NCR rate per unit produced (needs the lot dataset as a denominator — roadmap MQ-04) and CAPA cost (roadmap MQ-09).
