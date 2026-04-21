---
source_file: "N/A — authored-in-markdown"
source_path: "design-controls/design-transfer-sop.md"
doc_id: "GL-SOP-DC-007"
doc_type: "SOP"
title: "Design Transfer"
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
  - doc_id: "ISO 13485:2016 §7.3.8"
    title: "Design and development transfer"
    resolved: true
    match: null
    note: null
  - doc_id: "21 CFR 820.30(h)"
    title: "Design transfer"
    resolved: true
    match: null
    note: null
conversion_history:
  - date: "2026-04-21"
    source: "v1 — initial draft under task ben/022"
notes: null
---

# GL-SOP-DC-007 — Design Transfer

_Demo sample data — not for clinical use._

**Document ID:** GL-SOP-DC-007
**Revision:** 1.0
**Effective Date:** 2026-04-21
**Owner:** VP Operations, GlobalLogic MedTech

---

## 1. Purpose

Define how Design Outputs are transferred to production and service provision — per ISO 13485:2016 §7.3.8 and 21 CFR 820.30(h).

## 2. Scope

Covers the formal handoff from R&D to Manufacturing/Operations for products developed under the GlobalLogic QMS.

## 3. Responsibilities

- **Design Owner (R&D)** — owns the outgoing DHF state; attests outputs are complete and verified
- **Manufacturing Engineering** — accepts incoming DMR package; confirms producibility
- **Supplier Quality** — confirms supplier qualification for critical items (GL-SOP-SP-001)
- **Quality Engineering** — verifies Design Transfer Record completeness before release

## 4. Definitions

- **Device Master Record (DMR)** — Compilation of records containing the procedures and specifications for a finished device (21 CFR 820.3(j), §820.181).

## 5. References

- ISO 13485:2016 §7.3.8
- 21 CFR 820.30(h)
- 21 CFR 820.181 Device Master Record
- FDA Design Control Guidance §G

## 6. Procedure

### 6.1 Prerequisites

Before transfer can begin:

- Design Verification complete (GL-SOP-DC-006)
- Design Validation complete (GL-SOP-DC-006)
- Risk Management File updated; residual risks acceptable (GL-SOP-RM-001)
- Usability Validation complete (GL-SOP-UC-001)
- Clinical Evaluation complete (GL-SOP-UC-002) where applicable
- All Design Outputs approved and released under Document Control (GL-SOP-QM-001)
- Process validation(s) complete for applicable processes (GL-SOP-SP-003)
- Suppliers of critical items qualified (GL-SOP-SP-001)

### 6.2 Transfer Package

The DMR package (for each product) includes, or references:

- Device specifications (drawings, BOM, software versions, labeling)
- Manufacturing process specs and work instructions
- Inspection and test procedures and acceptance criteria
- Packaging and labeling specifications
- Installation, maintenance, and servicing procedures (where applicable)

### 6.3 Transfer Review

A formal Design Transfer Review (per GL-SOP-DC-005) confirms:

- The DMR package is complete and internally consistent
- Production is ready (equipment qualified, operators trained, suppliers qualified, first-article build complete)
- Any remaining risks are accepted in writing
- Post-market plan (PMS, complaint handling, adverse-event reporting) is in place

### 6.4 Release Authorization

Top Management (or designee) authorizes Production Release following the Transfer Review. The authorization is recorded and triggers update of the QMS Master Index entry for the product.

### 6.5 First Production Monitoring

First production lots are subject to enhanced monitoring per an approved plan. Deviations trigger NCR and, where warranted, CAPA (GL-SOP-QM-005).

## 7. Records Generated

| Record | Retained by | Retention |
|---|---|---|
| Design Transfer Record | DHF | Per GL-SOP-QM-001 |
| DMR (released version) | Controlled Docs | Per GL-SOP-QM-001 |
| Production Release Authorization | DHF | Per GL-SOP-QM-001 |

## 8. Revision History

| Rev | Date | Author | Summary |
|---|---|---|---|
| 1.0 | 2026-04-21 | Ben Xavier (via Claude, task ben/022) | Initial demo SOP. |
