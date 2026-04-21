---
source_file: "N/A — authored-in-markdown"
source_path: "design-controls/design-review-sop.md"
doc_id: "GL-SOP-DC-005"
doc_type: "SOP"
title: "Design Review"
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
  - doc_id: "ISO 13485:2016 §7.3.5"
    title: "Design and development review"
    resolved: true
    match: null
    note: null
  - doc_id: "21 CFR 820.30(e)"
    title: "Design review"
    resolved: true
    match: null
    note: null
conversion_history:
  - date: "2026-04-21"
    source: "v1 — initial draft under task ben/022"
notes: null
---

# GL-SOP-DC-005 — Design Review

_Demo sample data — not for clinical use._

**Document ID:** GL-SOP-DC-005
**Revision:** 1.0
**Effective Date:** 2026-04-21
**Owner:** VP R&D, GlobalLogic MedTech

---

## 1. Purpose

Define formal, documented, multi-disciplinary Design Reviews — per ISO 13485:2016 §7.3.5 and 21 CFR 820.30(e).

## 2. Scope

All Design Reviews executed as part of any design-control project in scope of the GlobalLogic QMS.

## 3. Responsibilities

- **Design Owner** — chair reviews, own actions to closure
- **Independent Reviewer** — at least one participant who has no direct responsibility for the stage being reviewed (21 CFR 820.30(e))
- **Attendees** — representatives from all functions concerned with the stage under review

## 4. Definitions

- **Design Review** — Documented, comprehensive, and systematic examination of a design to evaluate its adequacy, identify problems, and propose solutions.

## 5. References

- ISO 13485:2016 §7.3.5
- 21 CFR 820.30(e)
- FDA Design Control Guidance §D

## 6. Procedure

### 6.1 Mandatory Review Points

Design Reviews are held at minimum at each phase gate:

1. **Plan Approval** — Design & Development Plan is adequate
2. **Inputs-Complete** — Design Input Specification is baseline-ready
3. **Architecture / Design Complete** — outputs are defined and feasible
4. **V&V-Readiness** — protocols are approved; units under test are ready
5. **Pre-Transfer** — Verification complete, Validation complete, Risk Management complete, Usability Validation complete
6. **Release** — Design Transfer complete; DMR released; post-market plan in place

Additional for-cause reviews may be held any time (e.g., after significant risk-management updates, regulatory-strategy changes, major CAPAs).

### 6.2 Prerequisites

Before each review, the Design Owner issues a Pre-Read package ≥ **3 business days** in advance, containing:

- Review agenda and objectives
- Current DHF inventory (inputs, outputs, V&V status as applicable)
- Open risk items and risk-control traceability
- Open CAPAs affecting the design
- Previous review action-item status

### 6.3 Conduct

The review is recorded on **GL-FORM-DC-001 — Design Review Record**. Minimum content:

- Date, attendees (with role + independence status), chair
- Stage reviewed
- Items evaluated
- Problems identified and proposed solutions
- Actions (with owner + due date)
- **Decision:** Pass / Conditional Pass / Hold

### 6.4 Independence

Every Design Review must include at least one participant who does not have direct responsibility for the stage of design being reviewed (21 CFR 820.30(e)). This is recorded on the Review Record.

### 6.5 Actions and Closure

Actions are tracked to closure. Conditional Pass means the next phase may begin but listed actions must close by a specified checkpoint; Hold means the project cannot proceed until actions close and a re-review is held.

## 7. Records Generated

| Record | Retained by | Retention |
|---|---|---|
| Design Review Records (GL-FORM-DC-001) | DHF | Per GL-SOP-QM-001 |
| Action tracker | DHF | Per GL-SOP-QM-001 |

## 8. Revision History

| Rev | Date | Author | Summary |
|---|---|---|---|
| 1.0 | 2026-04-21 | Ben Xavier (via Claude, task ben/022) | Initial demo SOP. |
