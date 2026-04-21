---
source_file: "N/A — authored-in-markdown"
source_path: "design-controls/design-control-sop.md"
doc_id: "GL-SOP-DC-001"
doc_type: "SOP"
title: "Design Control (Master)"
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
  - doc_id: "ISO 13485:2016 §7.3"
    title: "Design and development"
    resolved: true
    match: null
    note: "Primary anchor"
  - doc_id: "21 CFR 820.30"
    title: "Design controls"
    resolved: true
    match: null
    note: null
  - doc_id: "FDA Design Control Guidance"
    title: "Design Control Guidance for Medical Device Manufacturers"
    resolved: true
    match: null
    note: null
conversion_history:
  - date: "2026-04-21"
    source: "v1 — initial draft under task ben/022"
notes: null
---

# GL-SOP-DC-001 — Design Control (Master)

_Demo sample data — not for clinical use._

**Document ID:** GL-SOP-DC-001
**Revision:** 1.0
**Effective Date:** 2026-04-21
**Owner:** VP R&D, GlobalLogic MedTech

---

## 1. Purpose

Define the overall Design Control framework by which GlobalLogic develops medical devices and medical device software, ensuring each design meets user needs, intended use, and specified requirements — per ISO 13485:2016 §7.3 and 21 CFR 820.30.

## 2. Scope

All design and development activities for products in scope of the GlobalLogic QMS, including hardware, electromechanical, firmware, SaMD, and SiMD products. Not applicable to research concepts prior to formal project initiation (though good practice encourages early design-controls discipline).

## 3. Responsibilities

| Role | Responsibility |
|---|---|
| Design Owner / Project Manager | Maintain DHF; execute plan; chair reviews |
| Systems Engineering | Author Design Inputs; maintain requirements baseline |
| Design Engineering (HW/FW/SW) | Author Design Outputs; execute verification |
| Usability Engineering | Execute IEC 62366-1 workflow (GL-SOP-UC-001) |
| Risk Management | Execute ISO 14971 workflow (GL-SOP-RM-001) |
| Clinical Affairs | Execute Clinical Evaluation (GL-SOP-UC-002) |
| Quality Engineering | Participate in reviews; verify DHF completeness |
| Regulatory Affairs | Confirm regulatory requirements in Design Inputs; filing-strategy alignment |
| Manufacturing / Operations | Participate in Design Transfer (GL-SOP-DC-007) |

## 4. Definitions

- **Design History File (DHF)** — Compilation of records describing the design history of a finished device (21 CFR 820.3(e)).
- **Design Input** — Physical and performance requirements of a device that are used as a basis for device design (§820.3(f)).
- **Design Output** — Results of a design effort at each design phase and at the end of the total design effort (§820.3(g)).
- **User Need** — A need of a person using the device in the intended context.
- **Verification** — Confirmation by objective evidence that design outputs meet design inputs.
- **Validation** — Confirmation by objective evidence that device conforms to user needs and intended uses.

## 5. References

- ISO 13485:2016 §7.3 Design and development
- 21 CFR 820.30 Design controls
- FDA — "Design Control Guidance for Medical Device Manufacturers" (1997)
- Dependent SOPs: GL-SOP-DC-002 through -008; GL-SOP-RM-001; GL-SOP-UC-001; GL-SOP-SW-001

## 6. Overview of Design Control Process

```
  User Needs            ┌──────────────┐
      │                 │ Risk Mgmt    │  (GL-SOP-RM-001)
      ▼                 │ Usability    │  (GL-SOP-UC-001)
 Design Inputs ◀────────┤ Clinical     │  (GL-SOP-UC-002)
      │                 │ Cybersecurity│  (GL-SOP-SW-004)
      ▼                 └──────┬───────┘
 Design Outputs ◀───────────────┘
      │
      ▼                   Design Reviews at each phase
 Verification               (GL-SOP-DC-005)
      │
      ▼
 Validation (vs. User Needs)
      │
      ▼
 Design Transfer  ──▶  Production (GL-SOP-SP-003)
      │
      ▼
 Design Change Control  (GL-SOP-DC-008)
```

## 7. Design History File (DHF)

The Design Owner maintains a DHF that contains, or refers to, the records necessary to demonstrate that the design was developed in accordance with the approved design plan and with applicable requirements. Minimum contents:

- Design and Development Plan (GL-SOP-DC-002)
- Design Inputs (GL-SOP-DC-003)
- Design Outputs (GL-SOP-DC-004)
- Design Review records (GL-SOP-DC-005)
- Design Verification & Validation records (GL-SOP-DC-006)
- Design Transfer record (GL-SOP-DC-007)
- Design Change records (GL-SOP-DC-008)
- Links to Risk Management File (GL-SOP-RM-001), Usability Engineering File (GL-SOP-UC-001), Clinical Evaluation Report (GL-SOP-UC-002), and Software Development File (GL-SOP-SW-001) where applicable.
- Traceability: User Needs → Design Inputs → Design Outputs → Verification → Validation (Trace Matrix)

## 8. Procedure (Summary — See Detailed SOPs)

| Phase | Detailed SOP | Required Outputs |
|---|---|---|
| Planning | GL-SOP-DC-002 | Design & Development Plan |
| Inputs | GL-SOP-DC-003 | Design Input Specification |
| Outputs | GL-SOP-DC-004 | Design Output Documents, Released DMR subset |
| Reviews | GL-SOP-DC-005 | Formal Design Review records at each phase gate |
| V & V | GL-SOP-DC-006 | Verification Protocols/Reports; Validation Protocols/Reports |
| Transfer | GL-SOP-DC-007 | Design Transfer Record; DMR release |
| Changes | GL-SOP-DC-008 | Design Change Records |

## 9. Records Generated

DHF (complete set) per product. Retention per GL-SOP-QM-001 §6.5 (≥ 10 years from last device placed on market, or per applicable retention).

## 10. Revision History

| Rev | Date | Author | Summary |
|---|---|---|---|
| 1.0 | 2026-04-21 | Ben Xavier (via Claude, task ben/022) | Initial demo SOP. |
