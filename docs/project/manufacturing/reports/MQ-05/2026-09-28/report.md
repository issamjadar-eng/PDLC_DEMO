# MQ-05 — Supplier quality: incoming rejects, on-time, scorecards, single-source exposure, audit currency

_Demo sample data — not for clinical use._

**Verdict**: Incoming reject rate 2.3% across 12 suppliers in 2026-06..2026-08 (2639 lots received), on-time 93.4%; 3 supplier(s) above the 3% ceiling: SUP-003 7.9% single-source, SUP-006 6.5% probation, SUP-011 4.3% conditional; 1 audit(s) overdue (SUP-003 by 289 d); 2 single-source supplier(s) (pump-motor, display); scorecards A 4 / B 5 / C 1 / D 2 [derived: v-main] [src: manufacturing/internal-suppliers@2026-09-28] [config: manufacturing.yml]

## Headline

- Window: trailing 3 periods 2026-06..2026-08, anchored on the snapshot as-of 2026-08-31; reject ceiling 3% [src: manufacturing/internal-suppliers@2026-09-28] [config: manufacturing.yml].
- Reject rate 2.3% on 2639 lots, on-time 93.4% (lot-weighted) [derived: supplier-stat] [src: manufacturing/internal-suppliers@2026-09-28].

## By supplier

| Supplier | Family | Status | Single source | Reject % | On-time % | Scorecard | Next audit due |
|---|---|---|---|---|---|---|---|
| SUP-003 Meridian Drive Systems [src: manufacturing/internal-suppliers@2026-09-28] | pump-motor | approved | yes | 7.9 ⚠️ | 88.3 | D | 2025-11-15 (overdue 289 d) |
| SUP-006 Halden Cell Works [src: manufacturing/internal-suppliers@2026-09-28] | battery | probation | no | 6.5 ⚠️ | 82.4 | D | 2026-10-14 |
| SUP-011 Kestrel Electromech [src: manufacturing/internal-suppliers@2026-09-28] | pump-motor | conditional | no | 4.3 ⚠️ | 91.0 | C | 2027-01-08 |
| SUP-010 Lumen Display Group [src: manufacturing/internal-suppliers@2026-09-28] | display | approved | yes | 1.8 | 94.8 | A | 2027-06-18 |
| SUP-009 Riverbend Fluidics [src: manufacturing/internal-suppliers@2026-09-28] | tubing-set | approved | no | 1.5 | 94.6 | A | 2027-05-27 |
| SUP-001 Northwind Circuits [src: manufacturing/internal-suppliers@2026-09-28] | PCB | approved | no | 1.5 | 95.5 | B | 2027-02-10 |
| SUP-002 Coastal PCB Assembly [src: manufacturing/internal-suppliers@2026-09-28] | PCB | approved | no | 1.4 | 93.6 | B | 2026-09-22 |
| SUP-007 Sable Polymer Housings [src: manufacturing/internal-suppliers@2026-09-28] | enclosure | approved | no | 1.2 | 92.2 | B | 2027-03-03 |
| SUP-005 Ardent Moldings [src: manufacturing/internal-suppliers@2026-09-28] | enclosure | approved | no | 1.2 | 94.5 | A | 2026-11-04 |
| SUP-004 Voltaic Power Cells [src: manufacturing/internal-suppliers@2026-09-28] | battery | approved | no | 1.1 | 94.2 | B | 2027-01-20 |
| SUP-008 Clearline Medical Tubing [src: manufacturing/internal-suppliers@2026-09-28] | tubing-set | approved | no | 0.8 | 97.4 | A | 2026-12-09 |
| SUP-012 Brightfield Optics [src: manufacturing/internal-suppliers@2026-09-28] | display | approved | no | 0.8 | 91.4 | B | 2026-10-30 |

## By component family

| Family | Reject % | On-time % | Lots received | Suppliers | Single-source |
|---|---|---|---|---|---|
| PCB [src: manufacturing/internal-suppliers@2026-09-28] | 1.4 | 94.8 | 552 | 2 | 0 |
| battery [src: manufacturing/internal-suppliers@2026-09-28] | 3.3 | 89.3 | 302 | 2 | 0 |
| display [src: manufacturing/internal-suppliers@2026-09-28] | 1.4 | 93.6 | 355 | 2 | 1 |
| enclosure [src: manufacturing/internal-suppliers@2026-09-28] | 1.2 | 93.6 | 421 | 2 | 0 |
| pump-motor [src: manufacturing/internal-suppliers@2026-09-28] | 7.2 | 88.8 | 346 | 2 | 1 |
| tubing-set [src: manufacturing/internal-suppliers@2026-09-28] | 1.1 | 96.3 | 663 | 2 | 0 |

## Scorecard distribution (latest period)

| Grade | Suppliers |
|---|---|
| A [src: manufacturing/internal-suppliers@2026-09-28] | 4 |
| B [src: manufacturing/internal-suppliers@2026-09-28] | 5 |
| C [src: manufacturing/internal-suppliers@2026-09-28] | 1 |
| D [src: manufacturing/internal-suppliers@2026-09-28] | 2 |

## Single-source exposure

| Supplier | Family | Scorecard | Reject % | Audit status |
|---|---|---|---|---|
| SUP-003 Meridian Drive Systems [src: manufacturing/internal-suppliers@2026-09-28] | pump-motor | D | 7.9 | overdue 289 d |
| SUP-010 Lumen Display Group [src: manufacturing/internal-suppliers@2026-09-28] | display | A | 1.8 | current, due 2027-06-18 |

## Assumptions & expectations — plan vs actual

_`unvalidated` means the expectation itself is a stand-in that has not been grounded
in a plan of record, a procedure, or the risk file — challenge the assumption, not just the actual._

| ID | Expectation | Expected | Actual | Verdict | Basis |
|---|---|---|---|---|---|
| E-05.1 | Every supplier on the approved list has a current quality-system audit [derived: audit-currency] [config: manufacturing.yml] | 0 suppliers with next audit due before the as-of date | 1 supplier audit(s) overdue at 2026-08-31: SUP-003 (289 d) | not-met (unvalidated) | stand-in; the approved-supplier procedure on record does not state the audit interval used here [VERIFY] |
| E-05.2 | Incoming reject rate stays under the ceiling for every supplier [derived: reject-by-supplier] [config: manufacturing.yml] | <= 3% of lots rejected per supplier, trailing 3 months | 3 of 12 suppliers above 3% in 2026-06..2026-08: SUP-003 7.9%, SUP-006 6.5%, SUP-011 4.3% | not-met (unvalidated) | stand-in reject ceiling; no supplier-quality target is on record [VERIFY] |

## Narrative — Risks / Mitigations / Issues

### Issues (materialized — needs action)

- **I1 (high)** — SUP-003 Meridian Drive Systems (pump-motor) rejects 7.9% of incoming lots in 2026-06..2026-08 against the 3% ceiling; audit overdue by 289 d [derived: reject-by-supplier] [src: manufacturing/internal-suppliers@2026-09-28] [config: manufacturing.yml]
  - _Action_: Issue a supplier corrective action request; tighten incoming sampling for the family until two clean periods [derived: reject-by-supplier] [src: manufacturing/internal-suppliers@2026-09-28] [config: manufacturing.yml]
- **I2 (high)** — SUP-006 Halden Cell Works (battery) rejects 6.5% of incoming lots in 2026-06..2026-08 against the 3% ceiling; approval status probation [derived: reject-by-supplier] [src: manufacturing/internal-suppliers@2026-09-28] [config: manufacturing.yml]
  - _Action_: Issue a supplier corrective action request; tighten incoming sampling for the family until two clean periods [derived: reject-by-supplier] [src: manufacturing/internal-suppliers@2026-09-28] [config: manufacturing.yml]
- **I3 (medium)** — SUP-011 Kestrel Electromech (pump-motor) rejects 4.3% of incoming lots in 2026-06..2026-08 against the 3% ceiling; approval status conditional [derived: reject-by-supplier] [src: manufacturing/internal-suppliers@2026-09-28] [config: manufacturing.yml]
  - _Action_: Issue a supplier corrective action request; tighten incoming sampling for the family until two clean periods [derived: reject-by-supplier] [src: manufacturing/internal-suppliers@2026-09-28] [config: manufacturing.yml]

### Risks (potential — mitigation identified)

- **R1 (high)** — Single-source exposure on pump-motor: SUP-003 Meridian Drive Systems (pump-motor) is the only approved source; scorecard D, reject 7.9%, next audit due 2025-11-15 (overdue 289 d) [derived: single-source-exposure] [derived: audit-currency] [src: manufacturing/internal-suppliers@2026-09-28]
  - _Mitigation_: Qualify a second source or hold safety stock sized to the requalification lead time; bring the audit current [derived: single-source-exposure] [derived: audit-currency] [src: manufacturing/internal-suppliers@2026-09-28]
- **R2 (medium)** — Single-source exposure on display: SUP-010 Lumen Display Group (display) is the only approved source; scorecard A, reject 1.8%, next audit due 2027-06-18 [derived: single-source-exposure] [derived: audit-currency] [src: manufacturing/internal-suppliers@2026-09-28]
  - _Mitigation_: Qualify a second source or hold safety stock sized to the requalification lead time; bring the audit current [derived: single-source-exposure] [derived: audit-currency] [src: manufacturing/internal-suppliers@2026-09-28]
- **R3 (medium)** — The 3% reject ceiling and the 'no overdue audit' rule are stand-ins — the approved-supplier procedure on record names neither, so the verdict is only as good as an unratified threshold [config: manufacturing.yml]
  - _Mitigation_: Have supplier quality ratify the ceiling and audit-interval rule in the ASL procedure and mark E-05.x validated [config: manufacturing.yml]

### Watch

- **W1 (medium)** — SUP-006 Halden Cell Works (battery) is on probation — scorecard D, reject 6.5%, on-time 82.4% in 2026-06..2026-08 [derived: reject-by-supplier] [derived: ontime-by-supplier] [src: manufacturing/internal-suppliers@2026-09-28]

## Method & provenance

- All figures from the pinned supplier register × incoming-inspection log [src: manufacturing/internal-suppliers@2026-09-28]; window and ceiling are plan constants [config: manufacturing.yml].
- Reject rate is lot-weighted (rejected ÷ received over the window), on-time is lot-weighted; the scorecard distribution uses each supplier's latest-period grade [derived: scorecard-distribution].
- Audit currency = next audit due vs the as-of date (positive = overdue) [derived: audit-currency].
- Monthly reject-rate history is charted for all suppliers and each supplier above the ceiling [derived: reject-trend].
