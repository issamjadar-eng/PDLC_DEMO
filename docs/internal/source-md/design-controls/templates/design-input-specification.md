---
source_file: "N/A — authored-in-markdown"
source_path: "design-controls/templates/design-input-specification.md"
doc_id: "GL-TMP-DC-002"
doc_type: "TMP"
title: "Design Input Specification"
format: "md"
conversion_date: "2026-04-21"
conversion_method: "claude-authored"
conversion_fidelity: "faithful"
pages: null
sheets: null
has_images: false
image_count: 0
has_tables: true
has_form_fields: true
references:
  - doc_id: "GL-SOP-DC-003"
    title: "Design Inputs"
    resolved: true
    match: null
    note: "Parent SOP"
  - doc_id: "ISO 13485:2016 §7.3.3"
    title: null
    resolved: true
    match: null
    note: null
conversion_history:
  - date: "2026-04-21"
    source: "v1 — initial draft under task ben/022"
notes: null
---

# GL-TMP-DC-002 — Design Input Specification

_Demo sample data — not for clinical use._

**Template ID:** GL-TMP-DC-002
**Revision:** 1.0
**Parent SOP:** GL-SOP-DC-003

---

## 1. Project Identification

| Field | Value |
|---|---|
| Project / Product | `{{NAME}}` |
| Baseline Revision | `{{X.X}}` |
| Baseline Date | `{{YYYY-MM-DD}}` |

## 2. Intended Use and Indications for Use

- **Intended use:** `{{}}`
- **Indications for use:** `{{}}`
- **Contraindications:** `{{}}`
- **Intended use environment(s):** `{{}}`
- **Intended user profile(s):** `{{}}`

## 3. User Needs (Summary)

| UN ID | User Need | Source | Related Standard / Reg |
|---|---|---|---|
| UN-001 | `{{user need statement}}` | `{{VoC / literature / PMS / clinical}}` | |

(Full user-needs register may be a separate file in the DHF and linked here.)

## 4. Design Inputs (Requirements)

| DI ID | Requirement | Acceptance Criteria | Verification Method | Traces to UN | Traces to Risk Control? |
|---|---|---|---|---|---|
| DI-001 | `{{requirement statement}}` | `{{measurable, unambiguous}}` | ☐ Test ☐ Inspection ☐ Analysis ☐ Demonstration | UN-001 | ☐ Yes (Risk-ID `{{}}`) |

### 4.1 Functional Requirements
### 4.2 Performance Requirements
### 4.3 Safety / Risk-Control Requirements (from GL-SOP-RM-001)
### 4.4 Usability / Use-Related Requirements (from GL-SOP-UC-001)
### 4.5 Software Requirements (if applicable — from GL-SOP-SW-001)
### 4.6 Cybersecurity Requirements (from GL-SOP-SW-004)
### 4.7 Labeling, IFU, and UDI Requirements
### 4.8 Regulatory and Standards Requirements
### 4.9 Environmental, Packaging, and Shelf-Life Requirements

## 5. Standards and Regulations Claimed

| Standard / Reg | Edition | Applicable Clauses | Evidence of Conformance (location) |
|---|---|---|---|
| ISO 13485 | 2016 | all applicable | |
| ISO 14971 | 2019 | all | |
| IEC 62304 | 2006+A1:2015 | applicable per SW Safety Class | |
| IEC 62366-1 | 2015 | all | |
| IEC 81001-5-1 | 2021 | all (if connected device) | |
| IEC 60601-1 / -1-2 | (edition) | applicable | |
| 21 CFR Part 820 | current | applicable | |
| EU MDR 2017/745 | current | GSPR per Annex I | |

## 6. Dependencies and Assumptions

`{{Named dependencies on platforms, suppliers, external services; documented assumptions}}`

## 7. Open Items

`{{Known gaps, unresolved requirements, TBDs — all must be closed before Inputs-complete phase gate}}`

## 8. Approvals

| Role | Name | Date | Signature |
|---|---|---|---|
| Systems Engineering Lead | | | |
| Design Owner | | | |
| Usability Engineering | | | |
| Risk Management | | | |
| Regulatory Affairs | | | |
| Clinical Affairs | | | |
| Quality Engineering | | | |

## 9. Revision History

| Rev | Date | Author | Summary |
|---|---|---|---|
| 1.0 | 2026-04-21 | Ben Xavier (via Claude, task ben/022) | Initial template. |
