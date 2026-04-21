---
source_file: "N/A — authored-in-markdown"
source_path: "design-controls/templates/verification-protocol-report.md"
doc_id: "GL-TMP-DC-003"
doc_type: "TMP"
title: "Design Verification Protocol & Report"
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
  - doc_id: "GL-SOP-DC-006"
    title: "Design Verification and Validation"
    resolved: true
    match: null
    note: "Parent SOP"
  - doc_id: "ISO 13485:2016 §7.3.6"
    title: null
    resolved: true
    match: null
    note: null
  - doc_id: "21 CFR 820.30(f)"
    title: null
    resolved: true
    match: null
    note: null
conversion_history:
  - date: "2026-04-21"
    source: "v1 — initial draft under task ben/022"
notes: null
---

# GL-TMP-DC-003 — Design Verification Protocol & Report

_Demo sample data — not for clinical use._

**Template ID:** GL-TMP-DC-003
**Revision:** 1.0
**Parent SOP:** GL-SOP-DC-006

---

## 1. Identification

| Field | Value |
|---|---|
| Protocol ID | `GL-VER-{{PROJECT}}-{{NNN}}` |
| Project | `{{}}` |
| Protocol Revision | `{{X.X}}` (approved before execution) |
| Report Revision | `{{X.X}}` |
| Design Inputs Verified | `{{DI-IDs}}` |

## 2. Objective

`{{What this protocol demonstrates — map to Design Inputs and acceptance criteria}}`

## 3. Scope

**In scope:** `{{}}`
**Out of scope:** `{{}}`

## 4. Articles Under Test (UUT)

| UUT ID | Build/Rev | Configuration | Serial Number(s) |
|---|---|---|---|
| | | | |

## 5. Test Environment and Equipment

| Item | Model / Spec | Calibration Due (if applicable) |
|---|---|---|
| | | |

## 6. Sample Size and Rationale

`{{Sample size and statistical rationale (tolerance interval, AQL, confidence/reliability), or engineering justification}}`

## 7. Test Method

`{{Step-by-step procedure; data to record; pass/fail logic per step}}`

## 8. Acceptance Criteria

| DI ID | Criterion | Measurement Method | Result Location (report §) |
|---|---|---|---|

## 9. Deviations

`{{Each deviation: description, impact assessment, disposition, approver}}`

## 10. Data

`{{Inline data tables or references to data files}}`

## 11. Results and Conclusion

| DI ID | Acceptance Criterion | Measured | Pass / Fail |
|---|---|---|---|

**Overall Conclusion:** ☐ All DIs verified ☐ Partial — see §12

## 12. Open Items

`{{Residual questions / re-test plans}}`

## 13. Approvals

### Protocol Approval (before execution)

| Role | Name | Date | Signature |
|---|---|---|---|
| Protocol Author | | | |
| Independent Reviewer | | | |
| QE Reviewer | | | |

### Report Approval (after execution)

| Role | Name | Date | Signature |
|---|---|---|---|
| Test Lead | | | |
| Independent Reviewer | | | |
| QE Reviewer | | | |
| Design Owner | | | |

## 14. Revision History

| Rev | Date | Author | Summary |
|---|---|---|---|
| 1.0 | 2026-04-21 | Ben Xavier (via Claude, task ben/022) | Initial template. |
