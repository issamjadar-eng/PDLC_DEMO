---
source_file: "N/A — authored-in-markdown"
source_path: "design-controls/design-verification-validation-sop.md"
doc_id: "GL-SOP-DC-006"
doc_type: "SOP"
title: "Design Verification and Validation"
format: "md"
conversion_date: "2026-04-21"
conversion_method: "claude-authored"
conversion_fidelity: "faithful"
pages: null
sheets: null
has_images: false
image_count: 0
has_tables: true
has_form_fields: false
references:
  - doc_id: "ISO 13485:2016 §7.3.6, §7.3.7"
    title: "Design verification; Design validation"
    resolved: true
    match: null
    note: null
  - doc_id: "21 CFR 820.30(f), (g)"
    title: "Design verification; Design validation"
    resolved: true
    match: null
    note: null
conversion_history:
  - date: "2026-04-21"
    source: "v1 — initial draft under task ben/022"
notes: null
---

# GL-SOP-DC-006 — Design Verification and Validation

_Demo sample data — not for clinical use._

**Document ID:** GL-SOP-DC-006
**Revision:** 1.0
**Effective Date:** 2026-04-21
**Owner:** VP R&D, GlobalLogic MedTech

---

## 1. Purpose

Define design verification (outputs vs. inputs) and design validation (device vs. user needs and intended uses) — per ISO 13485:2016 §7.3.6–§7.3.7 and 21 CFR 820.30(f)–(g).

## 2. Scope

All verification and validation activities for products in scope of the GlobalLogic QMS, including software V&V (subject to GL-SOP-SW-001), usability validation (subject to GL-SOP-UC-001), and clinical validation (subject to GL-SOP-UC-002) where applicable.

## 3. Responsibilities

- **V&V Lead** — plan, coordinate, report
- **Protocol Authors** — by domain (HW, FW, SW, Usability, Clinical)
- **Independent Test Engineers** — execute protocols; cannot test what they wrote
- **Quality Engineering** — review protocols/reports for procedural compliance

## 4. Definitions

- **Verification** — Confirmation by objective evidence that design outputs meet design inputs.
- **Validation** — Confirmation by objective evidence that device conforms to user needs and intended uses.
- **Initial production units** — Units, lots, or batches produced under production or equivalent conditions, used for validation (21 CFR 820.30(g)).

## 5. References

- ISO 13485:2016 §7.3.6, §7.3.7
- 21 CFR 820.30(f), (g)
- FDA Design Control Guidance §E, §F
- IEC 62304 §5.6 (software verification), §5.7 (software system testing)
- IEC 62366-1 §5.9 Summative evaluation
- ISO 14155:2020 (clinical validation where applicable)

## 6. Procedure

### 6.1 Verification

Each Design Input with verifiable acceptance criteria has at least one Verification activity. Verification methods:

- **Test** — actual measurement against acceptance criteria
- **Inspection** — visual or dimensional review
- **Analysis** — engineering calculation, simulation, worst-case analysis
- **Demonstration** — functional behavior exercised in representative conditions

**Protocols (GL-TMP-DC-003)** are drafted, reviewed, and approved **before** execution. Protocols state: test objective, items under test (serial numbers / build), acceptance criteria, test environment, sample size and rationale, method, and data-recording plan.

Execution is recorded on a **Verification Report** (using the same template), linked to the protocol. Deviations are dispositioned before report approval. A Verification Summary rolls up coverage by Design Input.

### 6.2 Validation

Validation demonstrates the device meets user needs and intended uses in its defined use environment. Validation:

- Is performed on **initial production units** or equivalents (21 CFR 820.30(g))
- Includes **software validation** (unit, integration, system testing and usability under actual or simulated use conditions)
- Includes **usability (summative) evaluation** per IEC 62366-1 §5.9 and FDA HFE/UE Guidance (see GL-SOP-UC-001)
- Includes **clinical evaluation** or clinical investigation where required (see GL-SOP-UC-002 and ISO 14155 if applicable)
- Includes **risk analysis verification** — risk controls are effective and residual risks are acceptable

**Protocols (GL-TMP-DC-004)** are drafted, reviewed, and approved before execution. Validation environment must represent intended use.

### 6.3 Traceability

Trace matrix links User Need → Design Input → Design Output → Verification → Validation. Gaps (orphaned inputs, missing verification, missing validation for user needs) are addressed before the pre-Transfer Design Review (GL-SOP-DC-005).

### 6.4 Test Article Identification

Each protocol identifies the specific build/revision of units tested. Changes between tested units and to-be-transferred units are assessed per GL-SOP-DC-008; significant changes may require re-verification.

### 6.5 Records and Summary

A **Design Verification Summary Report** and **Design Validation Summary Report** are prepared for the pre-Transfer review. Both reference the individual protocols/reports and include a coverage table.

## 7. Records Generated

| Record | Retained by | Retention |
|---|---|---|
| V&V Plans | DHF | Per GL-SOP-QM-001 |
| Protocols and Reports | DHF | Per GL-SOP-QM-001 |
| Trace matrix | DHF | Per GL-SOP-QM-001 |
| V&V Summary Reports | DHF | Per GL-SOP-QM-001 |

## 8. Revision History

| Rev | Date | Author | Summary |
|---|---|---|---|
| 1.0 | 2026-04-21 | Ben Xavier (via Claude, task ben/022) | Initial demo SOP. |
