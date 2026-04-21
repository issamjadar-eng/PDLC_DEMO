---
source_file: "N/A — authored-in-markdown"
source_path: "design-controls/templates/design-review-record.md"
doc_id: "GL-FORM-DC-001"
doc_type: "FORM"
title: "Design Review Record"
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
  - doc_id: "GL-SOP-DC-005"
    title: "Design Review"
    resolved: true
    match: null
    note: "Parent SOP"
  - doc_id: "21 CFR 820.30(e)"
    title: null
    resolved: true
    match: null
    note: null
conversion_history:
  - date: "2026-04-21"
    source: "v1 — initial draft under task ben/022"
notes: null
---

# GL-FORM-DC-001 — Design Review Record

_Demo sample data — not for clinical use._

**Form ID:** GL-FORM-DC-001 (template)
**Revision:** 1.0
**Parent SOP:** GL-SOP-DC-005

---

## 1. Meeting Identification

| Field | Value |
|---|---|
| Review ID | `GL-DR-{{PROJECT}}-{{NNN}}` |
| Project | `{{}}` |
| Stage | ☐ Plan Approval ☐ Inputs-Complete ☐ Architecture ☐ V&V-Readiness ☐ Pre-Transfer ☐ Release ☐ For-Cause — `{{reason}}` |
| Date | `{{YYYY-MM-DD}}` |
| Chair | `{{Design Owner}}` |

## 2. Attendees and Independence

| Name | Role | Function | Independent of stage? |
|---|---|---|---|
| | | | ☐ Yes ☐ No |

At least one **Independent Reviewer** is required per 21 CFR 820.30(e).

## 3. Pre-Read Package

`{{list of documents distributed ≥ 3 business days in advance}}`

## 4. Items Evaluated

| # | Item | Status | Notes |
|---|---|---|---|
| 1 | Design Inputs coverage | ☐ OK ☐ Issue | |
| 2 | Design Outputs coverage | ☐ OK ☐ Issue | |
| 3 | Verification coverage | ☐ OK ☐ Issue ☐ N/A (stage) | |
| 4 | Validation coverage | ☐ OK ☐ Issue ☐ N/A (stage) | |
| 5 | Risk Management File currency | ☐ OK ☐ Issue | |
| 6 | Usability Engineering File currency | ☐ OK ☐ Issue | |
| 7 | Software lifecycle artifacts | ☐ OK ☐ Issue ☐ N/A | |
| 8 | Cybersecurity artifacts | ☐ OK ☐ Issue ☐ N/A | |
| 9 | Trace matrix orphans | ☐ 0 ☐ `{{count}}` — see action | |
| 10 | Open CAPAs affecting design | | |
| 11 | Regulatory / standards position | | |
| 12 | Previous review action-item status | | |

## 5. Problems Identified and Proposed Solutions

| # | Problem | Proposed Solution |
|---|---|---|
| 1 | | |

## 6. Actions

| # | Action | Owner | Due Date | Status |
|---|---|---|---|---|
| 1 | | | | ☐ Open ☐ Complete |

## 7. Decision

☐ **Pass** — proceed to next stage
☐ **Conditional Pass** — proceed, but listed actions must close by `{{date}}`
☐ **Hold** — cannot proceed until actions close and re-review

## 8. Signatures

| Role | Name | Date | Signature |
|---|---|---|---|
| Chair | | | |
| Independent Reviewer | | | |
| Quality Engineering | | | |

## 9. Revision History

| Rev | Date | Author | Summary |
|---|---|---|---|
| 1.0 | 2026-04-21 | Ben Xavier (via Claude, task ben/022) | Initial template. |
