---
source_file: "N/A — authored-in-markdown"
source_path: "usability-clinical/templates/summative-evaluation-protocol.md"
doc_id: "GL-TMP-UC-003"
doc_type: "TMP"
title: "Summative Usability Evaluation Protocol & Report"
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
  - doc_id: "GL-SOP-UC-001"
    title: null
    resolved: true
    match: null
    note: "Parent SOP"
  - doc_id: "IEC 62366-1 §5.9"
    title: null
    resolved: true
    match: null
    note: null
  - doc_id: "FDA HFE/UE Guidance (2016)"
    title: null
    resolved: true
    match: null
    note: null
conversion_history:
  - date: "2026-04-21"
    source: "v1 — initial draft under task ben/022"
notes: null
---

# GL-TMP-UC-003 — Summative Usability Evaluation Protocol & Report

_Demo sample data — not for clinical use._

**Template ID:** GL-TMP-UC-003
**Revision:** 1.0
**Parent SOP:** GL-SOP-UC-001

---

## 1. Identification

| Field | Value |
|---|---|
| Product | `{{}}` |
| Protocol ID | `GL-HFE-{{PROJECT}}-{{NNN}}` |
| Protocol Revision | `{{X.X}}` |
| Report Revision | `{{X.X}}` |

## 2. Objectives

Demonstrate that representative users can perform hazard-related use scenarios safely and effectively with the device, training, and IFU as they will be delivered at market.

## 3. Participants

| User Group | Inclusion / Exclusion Criteria | Number | Rationale |
|---|---|---|---|

Per FDA 2016 HFE/UE guidance: at least 15 representative users per distinct user group unless justified.

## 4. Device / Build Under Test

| Item | Revision |
|---|---|
| Device (production-equivalent) | `{{}}` |
| IFU / Labeling | `{{}}` |
| Training materials | `{{}}` |

## 5. Use Scenarios

| # | Scenario | Hazard-related? | Associated Hazard ID | Success Criteria |
|---|---|---|---|---|

## 6. Environment

`{{simulated-use conditions representative of intended use environment; realism justification}}`

## 7. Method

- Data collection: ☐ Observation ☐ Think-aloud ☐ Knowledge task ☐ Interview
- Task-performance metrics (completion, time, errors)
- Use-error capture and classification
- Debrief / root-cause interview for each observed use error

## 8. Data Analysis

- Use errors classified per IEC 62366-1 (use error, close call, other)
- Root cause: UI design vs. training vs. IFU vs. other
- Risk re-estimation per GL-SOP-RM-001

## 9. Acceptance

`{{All hazard-related scenarios completed safely by all participants, OR residual risks acceptable after analysis}}`

## 10. Results

| Scenario | # Participants | Successes | Use Errors | Root Causes | Residual Risk |
|---|---|---|---|---|---|

## 11. Conclusions

`{{Overall finding; inputs to Design Validation (GL-SOP-DC-006) and RMF (GL-SOP-RM-001)}}`

## 12. Approvals

### Protocol (before execution)

| Role | Name | Date | Signature |
|---|---|---|---|
| Human Factors Lead | | | |
| Risk Manager | | | |
| Clinical Lead | | | |
| QE Reviewer | | | |

### Report (after execution)

| Role | Name | Date | Signature |
|---|---|---|---|
| Human Factors Lead | | | |
| Independent Reviewer | | | |
| Design Owner | | | |
| VP Quality | | | |
| VP Regulatory | | | |

## 13. Revision History

| Rev | Date | Author | Summary |
|---|---|---|---|
| 1.0 | 2026-04-21 | Ben Xavier (via Claude, task ben/022) | Initial template. |
