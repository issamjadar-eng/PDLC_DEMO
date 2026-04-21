---
source_file: "N/A — authored-in-markdown"
source_path: "quality-management/templates/capa-form.md"
doc_id: "GL-FORM-QM-001"
doc_type: "FORM"
title: "CAPA Form"
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
  - doc_id: "GL-SOP-QM-005"
    title: "Corrective Action / Preventive Action (CAPA)"
    resolved: true
    match: null
    note: "Parent SOP"
  - doc_id: "ISO 13485:2016 §8.5"
    title: null
    resolved: true
    match: null
    note: null
  - doc_id: "21 CFR 820.100"
    title: null
    resolved: true
    match: null
    note: null
conversion_history:
  - date: "2026-04-21"
    source: "v1 — initial draft under task ben/022"
notes: null
---

# GL-FORM-QM-001 — CAPA Form

_Demo sample data — not for clinical use._

**Form ID:** GL-FORM-QM-001 (template)
**Revision:** 1.0
**Parent SOP:** GL-SOP-QM-005

---

## 1. Identification

| Field | Value |
|---|---|
| CAPA ID | `GL-CAPA-{{YYYY}}-{{NNN}}` |
| Date Opened | `{{YYYY-MM-DD}}` |
| Source | ☐ Complaint ☐ Internal audit ☐ External audit ☐ Supplier ☐ NCR ☐ PMS ☐ Management Review ☐ Other: `{{}}` |
| Related Event ID(s) | `{{IDs}}` |
| CAPA Owner | `{{NAME, ROLE}}` |
| CAPA Classification | ☐ Minor ☐ Major ☐ Critical |
| Product(s) Affected | `{{PRODUCT, MODEL, LOT/SN}}` |

## 2. Issue Description

**Observed condition:**
`{{What was observed, when, where, how it was detected}}`

**Deviation from requirement:**
`{{Which requirement / SOP / spec was not met}}`

**Immediate containment / correction:**
`{{Interim action to stop further impact — e.g., hold, quarantine, patch}}`

## 3. Risk / Impact Assessment

| Dimension | Assessment |
|---|---|
| Patient safety impact | `{{None / Potential / Confirmed}}` |
| Product quality impact | `{{None / Potential / Confirmed}}` |
| Regulatory reportability (21 CFR 803, EU MDR Art. 87) | ☐ Yes ☐ No ☐ Under review — See GL-SOP-PM-003 |
| Field correction / recall potential | ☐ Yes ☐ No |
| Impact on risk management file | `{{File ID, update required Y/N}}` |

## 4. Investigation and Root-Cause Analysis

**Technique used:** ☐ 5 Whys ☐ Ishikawa ☐ Fault Tree ☐ Other: `{{}}`

**Investigation summary:**
`{{What was investigated, by whom, data sources, sample size}}`

**Root cause(s):**
1. `{{Root cause 1}}`
2. `{{Root cause 2}}`

## 5. Action Plan

| # | Action Type | Description | Owner | Due Date | Status |
|---|---|---|---|---|---|
| 1 | Correction | `{{}}` | | | ☐ Open ☐ Complete |
| 2 | Corrective Action | `{{}}` | | | ☐ Open ☐ Complete |
| 3 | Preventive Action | `{{}}` | | | ☐ Open ☐ Complete |

## 6. Effectiveness Verification Plan

**Method:** `{{How effectiveness will be verified — trend metric, re-audit, re-verification}}`
**Monitoring window:** `{{Duration and criteria for success}}`
**Verifier:** `{{Name, independent of action execution where feasible}}`

## 7. Effectiveness Results

`{{Objective evidence that the root cause has been eliminated — attach data, reports, audit results}}`

**Effectiveness conclusion:** ☐ Effective ☐ Partially effective — reopen ☐ Not effective — reopen

## 8. Closure

| Signoff | Name | Role | Date | Signature |
|---|---|---|---|---|
| CAPA Owner | | | | |
| CAPA Review Board / MR | | | | |
| Regulatory (if reportable) | | | | |

## 9. Revision History

| Rev | Date | Author | Summary |
|---|---|---|---|
| 1.0 | 2026-04-21 | Ben Xavier (via Claude, task ben/022) | Initial form template. |
