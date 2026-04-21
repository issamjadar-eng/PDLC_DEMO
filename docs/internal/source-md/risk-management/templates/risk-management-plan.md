---
source_file: "N/A — authored-in-markdown"
source_path: "risk-management/templates/risk-management-plan.md"
doc_id: "GL-TMP-RM-001"
doc_type: "TMP"
title: "Risk Management Plan"
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
  - doc_id: "GL-SOP-RM-001"
    title: "Risk Management (Master)"
    resolved: true
    match: null
    note: "Parent SOP"
  - doc_id: "ISO 14971:2019 §4.4"
    title: null
    resolved: true
    match: null
    note: null
conversion_history:
  - date: "2026-04-21"
    source: "v1 — initial draft under task ben/022"
notes: null
---

# GL-TMP-RM-001 — Risk Management Plan

_Demo sample data — not for clinical use._

**Template ID:** GL-TMP-RM-001
**Revision:** 1.0
**Parent SOP:** GL-SOP-RM-001

---

## 1. Scope

| Field | Value |
|---|---|
| Product / Project | `{{NAME}}` |
| Lifecycle phases covered | `{{Design → Transfer → Post-Market}}` |
| Scope exclusions | `{{e.g., manufacturing process scope handled by pFMEA}}` |

## 2. Responsibilities

| Role | Name | Responsibility |
|---|---|---|
| Risk Manager | | Assemble team; own RMF |
| Design Owner | | Integrate controls into design |
| Usability Lead | | Use-related hazards |
| Cybersecurity Lead | | Cyber hazards (if applicable) |
| Clinical Lead | | Clinical hazard data; benefit assessment |
| VP Quality | | Approve Plan and Report |

## 3. Risk Acceptability Criteria

Define scales and acceptability regions. Example (document rationale):

### Severity (S)

| Level | Description | Example |
|---|---|---|
| S5 — Catastrophic | Death, permanent disability | |
| S4 — Critical | Serious injury requiring intervention | |
| S3 — Serious | Injury requiring medical attention | |
| S2 — Moderate | Minor injury, reversible | |
| S1 — Negligible | Inconvenience, no medical impact | |

### Probability (P)

| Level | Description | Qualitative Range |
|---|---|---|
| P5 — Frequent | | > 10⁻³ |
| P4 — Probable | | 10⁻³ to 10⁻⁴ |
| P3 — Occasional | | 10⁻⁴ to 10⁻⁵ |
| P2 — Remote | | 10⁻⁵ to 10⁻⁶ |
| P1 — Improbable | | < 10⁻⁶ |

### Acceptability Matrix

`{{5×5 matrix with Unacceptable / ALARP / Broadly Acceptable regions}}`

### Acceptability Criteria Rationale

`{{Justification anchored in state-of-the-art, applicable standards, predicate device history, regulatory expectations}}`

## 4. Review Activities

- Risk reviews at each phase gate (GL-SOP-DC-005)
- RMF re-review at pre-Transfer
- Lifecycle re-review triggers: complaint trend, PMS signal, CAPA affecting risk, post-approval change (GL-SOP-DC-008)

## 5. Verification of Risk Controls

For each risk control, identify the Design Input(s) it generates and the Verification or Validation activity that confirms effectiveness (GL-SOP-DC-006).

## 6. Production and Post-Production Information

Inputs to lifecycle risk monitoring:
- Production NCRs, yield, field returns
- Complaints (GL-SOP-PM-002)
- PMS Reports / PSURs (GL-SOP-PM-001)
- Adverse events (GL-SOP-PM-003)
- CAPA outputs (GL-SOP-QM-005)

Update triggers, responsibilities, and cadence defined here.

## 7. Approvals

| Role | Name | Date | Signature |
|---|---|---|---|
| Risk Manager | | | |
| Design Owner | | | |
| VP Quality | | | |

## 8. Revision History

| Rev | Date | Author | Summary |
|---|---|---|---|
| 1.0 | 2026-04-21 | Ben Xavier (via Claude, task ben/022) | Initial template. |
