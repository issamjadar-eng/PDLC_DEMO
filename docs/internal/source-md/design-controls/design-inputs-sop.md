---
source_file: "N/A — authored-in-markdown"
source_path: "design-controls/design-inputs-sop.md"
doc_id: "GL-SOP-DC-003"
doc_type: "SOP"
title: "Design Inputs"
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
  - doc_id: "ISO 13485:2016 §7.3.3"
    title: "Design and development inputs"
    resolved: true
    match: null
    note: null
  - doc_id: "21 CFR 820.30(c)"
    title: "Design input"
    resolved: true
    match: null
    note: null
conversion_history:
  - date: "2026-04-21"
    source: "v1 — initial draft under task ben/022"
notes: null
---

# GL-SOP-DC-003 — Design Inputs

_Demo sample data — not for clinical use._

**Document ID:** GL-SOP-DC-003
**Revision:** 1.0
**Effective Date:** 2026-04-21
**Owner:** VP R&D, GlobalLogic MedTech

---

## 1. Purpose

Establish the capture, review, and approval of design input requirements — per ISO 13485:2016 §7.3.3 and 21 CFR 820.30(c).

## 2. Scope

All design input work — from elicitation of user needs and intended use through the baseline of the Design Input Specification at the Inputs-complete phase gate.

## 3. Responsibilities

- **Systems Engineering Lead** — owns the Design Input Specification
- **Usability Engineering** — user needs capture and traceability
- **Risk Management** — ensures risk-control inputs are captured
- **Regulatory Affairs** — ensures applicable regulatory and standards requirements are captured
- **Clinical Affairs** — ensures clinical performance needs are captured

## 4. Definitions

- **Intended use** — The purpose for which the manufacturer intends the device to be used, as reflected in labeling, technical documentation, and marketing material.
- **Indications for use** — General description of the disease or condition, patient population, body part, or frequency of use for which the device is intended (21 CFR 814.20(b)(3)(i)).
- **Essential design output** — An output that is essential for the proper functioning of the device (21 CFR 820.30(d)).

## 5. References

- ISO 13485:2016 §7.3.3
- 21 CFR 820.30(c)
- FDA Design Control Guidance §B
- Applicable harmonized standards (ISO 14971, IEC 62304, IEC 62366-1, IEC 60601 family as applicable, IEC 81001-5-1)

## 6. Procedure

### 6.1 Elicitation Sources

Design Inputs are derived from, at minimum:

- **User Needs** (elicited via interviews, observation, voice-of-customer, clinical literature; see GL-SOP-UC-001)
- **Intended use** and **Indications for use**
- **Intended use environment(s)** and **intended user profile(s)**
- Applicable **regulatory requirements** (US, EU, other target markets)
- Applicable **recognized consensus standards**
- Outputs of **Risk Management** (risk-control requirements — GL-SOP-RM-001)
- Outputs of **Usability Engineering** (use-related risk controls — GL-SOP-UC-001)
- **Clinical evaluation** inputs where applicable (GL-SOP-UC-002)
- **Cybersecurity** requirements where applicable (GL-SOP-SW-004)
- Outputs of **previous similar designs** and **post-market surveillance** (GL-SOP-PM-001)

### 6.2 Requirements Quality Criteria

Each Design Input shall be:

- **Unambiguous** — single interpretation
- **Verifiable** — can be tested, inspected, or analyzed
- **Complete** — no obvious gaps for the stated intended use
- **Consistent** — non-conflicting with other inputs
- **Traceable** — linked to a user need or regulatory/risk-management driver
- **Uniquely identified** — assigned a Requirement ID

### 6.3 Review and Approval

The Design Input Specification (GL-TMP-DC-002) is reviewed for adequacy — incomplete, ambiguous, or conflicting requirements are resolved before baseline. Approval is the Inputs-complete phase gate (GL-SOP-DC-005).

### 6.4 Baseline and Change Control

After baseline, changes to Design Inputs are processed per GL-SOP-DC-008.

### 6.5 Traceability

Every Design Input traces to:
- ≥ 1 User Need (or a regulatory / standards driver)
- ≥ 1 Design Output
- ≥ 1 Verification activity
- A Risk Management File entry if it is a risk control

Trace matrix is maintained throughout the project and is part of the DHF.

## 7. Records Generated

| Record | Retained by | Retention |
|---|---|---|
| Design Input Specification (all revisions) | DHF | Per GL-SOP-QM-001 |
| User Needs register | DHF | Per GL-SOP-QM-001 |
| Trace matrix | DHF | Per GL-SOP-QM-001 |

## 8. Revision History

| Rev | Date | Author | Summary |
|---|---|---|---|
| 1.0 | 2026-04-21 | Ben Xavier (via Claude, task ben/022) | Initial demo SOP. |
