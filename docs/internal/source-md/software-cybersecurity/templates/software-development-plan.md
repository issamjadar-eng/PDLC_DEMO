---
source_file: "N/A — authored-in-markdown"
source_path: "software-cybersecurity/templates/software-development-plan.md"
doc_id: "GL-TMP-SW-001"
doc_type: "TMP"
title: "Software Development Plan"
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
  - doc_id: "GL-SOP-SW-001"
    title: null
    resolved: true
    match: null
    note: "Parent SOP"
  - doc_id: "IEC 62304 §5.1"
    title: null
    resolved: true
    match: null
    note: null
conversion_history:
  - date: "2026-04-21"
    source: "v1 — initial draft under task ben/022"
notes: null
---

# GL-TMP-SW-001 — Software Development Plan

_Demo sample data — not for clinical use._

**Template ID:** GL-TMP-SW-001
**Revision:** 1.0
**Parent SOP:** GL-SOP-SW-001

---

## 1. Identification

| Field | Value |
|---|---|
| Product / Software System | `{{NAME}}` |
| Plan Revision | `{{X.X}}` |
| Software Safety Class (overall) | ☐ A ☐ B ☐ C |
| Classification Rationale | `{{per GL-WI-SW-001}}` |

## 2. Scope

Covers software requirements, architecture, detailed design, implementation, verification, release, and maintenance per IEC 62304.

## 3. Lifecycle Model

`{{Describe: e.g., iterative with defined increments; how each increment executes §5.2–§5.7; mapping to QMS design controls phases}}`

## 4. Software Items and Safety Class

| Item | Description | Class | Rationale |
|---|---|---|---|

## 5. Development Standards, Methods, Tools

- Coding standard: `{{e.g., MISRA C, CERT C/C++, internal guide}}`
- Version control: `{{git}}`
- CI/CD: `{{}}`
- Static analysis: `{{}}`
- Dynamic analysis / fuzzing: `{{}}`
- Unit test framework: `{{}}`

## 6. Verification Planning

- Unit tests — coverage targets by class
- Integration strategy
- System testing
- Regression strategy on change
- Traceability: Requirement → Design → Code → Test

## 7. Risk Management Integration

`{{Cross-reference Risk Management Plan (GL-TMP-RM-001) and how software hazards are captured (GL-WI-RM-001)}}`

## 8. Configuration Management (§8)

- Baseline definition and labeling
- Build reproducibility
- SOUP inventory (GL-SOP-SW-002)
- SBOM generation (GL-WI-SW-002)

## 9. Problem Resolution (§9)

Reference GL-SOP-SW-003.

## 10. Release Criteria (§5.8)

- V&V complete
- Anomaly list reviewed against RMF
- SBOM generated and CVE-triaged
- Build reproducibility confirmed
- Release record signed

## 11. Maintenance (§6)

- Change classification (IEC 62304 §6.2) → GL-SOP-DC-008
- Post-release monitoring linkage (GL-SOP-PM-001)

## 12. Approvals

| Role | Name | Date | Signature |
|---|---|---|---|
| Software Lead | | | |
| Design Owner | | | |
| Risk Manager | | | |
| Cybersecurity Lead | | | |
| VP Quality | | | |

## 13. Revision History

| Rev | Date | Author | Summary |
|---|---|---|---|
| 1.0 | 2026-04-21 | Ben Xavier (via Claude, task ben/022) | Initial template. |
