---
source_file: "N/A — authored-in-markdown"
source_path: "design-controls/templates/validation-protocol-report.md"
doc_id: "GL-TMP-DC-004"
doc_type: "TMP"
title: "Design Validation Protocol & Report"
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
  - doc_id: "ISO 13485:2016 §7.3.7"
    title: null
    resolved: true
    match: null
    note: null
  - doc_id: "21 CFR 820.30(g)"
    title: null
    resolved: true
    match: null
    note: null
conversion_history:
  - date: "2026-04-21"
    source: "v1 — initial draft under task ben/022"
notes: null
---

# GL-TMP-DC-004 — Design Validation Protocol & Report

_Demo sample data — not for clinical use._

**Template ID:** GL-TMP-DC-004
**Revision:** 1.0
**Parent SOP:** GL-SOP-DC-006

---

## 1. Identification

| Field | Value |
|---|---|
| Protocol ID | `GL-VAL-{{PROJECT}}-{{NNN}}` |
| Project | `{{}}` |
| Protocol Revision | `{{X.X}}` |
| Report Revision | `{{X.X}}` |
| User Needs Validated | `{{UN-IDs}}` |

## 2. Objective

Demonstrate that the device meets the specified User Needs and Intended Uses in the defined use environment.

## 3. Scope

**In scope:** `{{}}`
**Out of scope:** `{{}}`

## 4. Initial Production Units

Validation shall be performed on **initial production units** or equivalent (21 CFR 820.30(g)). Document the production origin:

| Unit ID | Production Origin | Build/Rev | Lot |
|---|---|---|---|
| | | | |

## 5. Use Environment and Participants

| Dimension | Description |
|---|---|
| Use environment (simulated / actual) | |
| Intended user profile(s) | |
| Number and selection of participants (if applicable) | |
| Training level provided | |

## 6. Method(s)

Validation may combine multiple methods; document each:

- **Functional / performance validation** under intended-use conditions
- **Summative usability evaluation** per IEC 62366-1 §5.9 / FDA HFE/UE Guidance (cross-reference GL-SOP-UC-001)
- **Clinical evaluation / investigation** per ISO 14155 where applicable (cross-reference GL-SOP-UC-002)
- **Risk-control verification** confirming controls from RMF are effective in intended use

## 7. Acceptance Criteria

| UN ID | Criterion (tied to user outcome) | Method | Result Location |
|---|---|---|---|

## 8. Data

`{{Raw observations, outcome data, event logs, recordings}}`

## 9. Results and Conclusion

| UN ID | Criterion | Outcome | Pass / Fail |
|---|---|---|---|

**Overall Conclusion:** ☐ Device conforms to user needs and intended uses ☐ Gaps identified — see §10

## 10. Open Items / Residual Risks

`{{Residual issues; risk-benefit posture; actions}}`

## 11. Approvals

### Protocol Approval (before execution)

| Role | Name | Date | Signature |
|---|---|---|---|
| Protocol Author | | | |
| Usability (if summative) | | | |
| Clinical (if applicable) | | | |
| Risk Management | | | |
| QE Reviewer | | | |

### Report Approval (after execution)

| Role | Name | Date | Signature |
|---|---|---|---|
| Validation Lead | | | |
| Independent Reviewer | | | |
| Design Owner | | | |
| VP Quality | | | |
| VP Regulatory (if filing implications) | | | |

## 12. Revision History

| Rev | Date | Author | Summary |
|---|---|---|---|
| 1.0 | 2026-04-21 | Ben Xavier (via Claude, task ben/022) | Initial template. |
