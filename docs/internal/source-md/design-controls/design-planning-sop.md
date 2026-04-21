---
source_file: "N/A — authored-in-markdown"
source_path: "design-controls/design-planning-sop.md"
doc_id: "GL-SOP-DC-002"
doc_type: "SOP"
title: "Design and Development Planning"
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
  - doc_id: "ISO 13485:2016 §7.3.2"
    title: "Design and development planning"
    resolved: true
    match: null
    note: null
  - doc_id: "21 CFR 820.30(b)"
    title: "Design and development planning"
    resolved: true
    match: null
    note: null
conversion_history:
  - date: "2026-04-21"
    source: "v1 — initial draft under task ben/022"
notes: null
---

# GL-SOP-DC-002 — Design and Development Planning

_Demo sample data — not for clinical use._

**Document ID:** GL-SOP-DC-002
**Revision:** 1.0
**Effective Date:** 2026-04-21
**Owner:** VP R&D, GlobalLogic MedTech

---

## 1. Purpose

Define how GlobalLogic plans and controls design and development projects — per ISO 13485:2016 §7.3.2 and 21 CFR 820.30(b).

## 2. Scope

Applies at project initiation and is updated as the design evolves.

## 3. Responsibilities

- **Design Owner / Project Manager** — author and maintain the Plan; update at phase gates.
- **Functional Leads** (Systems, HW, FW, SW, Quality, Regulatory, Clinical, Usability, Risk, Cyber, Ops) — contribute sections; confirm resource commitments.

## 4. Definitions

- **Phase Gate** — A formal review point at which the project must demonstrate readiness to proceed; outcomes: Pass / Conditional / Hold.

## 5. References

- ISO 13485:2016 §7.3.2
- 21 CFR 820.30(b)
- FDA Design Control Guidance §A.2

## 6. Procedure

### 6.1 Plan Initiation

A **Design and Development Plan (GL-TMP-DC-001)** is drafted at project initiation and approved before Design Inputs work begins. Use the template.

### 6.2 Required Content (ISO 13485 §7.3.2(a)–(f))

The plan shall describe or reference:

1. **Stages** of design and development (e.g., Concept → Feasibility → Design → V&V → Transfer → Release)
2. **Reviews required at each stage** — who, what, go/no-go criteria
3. **Verification, validation, and design transfer activities** appropriate to each stage
4. **Responsibilities and authorities** for design and development
5. **Methods to ensure traceability** — from inputs to outputs to verification and validation
6. **Resources, including competence of personnel** (GL-SOP-QM-003)

Additional plan content expected:

- Interfaces to Risk Management File (GL-SOP-RM-001), Usability Engineering File (GL-SOP-UC-001), Software Development Plan (GL-SOP-SW-001), Cybersecurity Plan (GL-SOP-SW-004), Clinical Evaluation Plan (GL-SOP-UC-002)
- Regulatory strategy (target markets, pathways) per Regulatory Affairs
- Supplier involvement and applicable supplier controls (GL-SOP-SP-001)
- Software safety classification per IEC 62304 (if software is in scope)
- Schedule / milestones
- Risk-based tailoring rationale (which activities are scaled up/down and why)

### 6.3 Plan Updates

The plan is updated:

- At every phase gate (even if the update is "no change; proceed")
- When scope changes materially
- When regulatory strategy changes
- When a CAPA or risk-management output requires it

Each update triggers Document Change Control per GL-SOP-QM-001.

### 6.4 Phase Gate Reviews

Each phase ends with a formal Design Review per GL-SOP-DC-005. The Review confirms planned activities are complete, outputs are adequate, and residual risks are acceptable to proceed.

## 7. Records Generated

| Record | Retained by | Retention |
|---|---|---|
| Design & Development Plan (all revisions) | DHF | Per GL-SOP-QM-001 |
| Phase Gate Review records | DHF | Per GL-SOP-QM-001 |

## 8. Revision History

| Rev | Date | Author | Summary |
|---|---|---|---|
| 1.0 | 2026-04-21 | Ben Xavier (via Claude, task ben/022) | Initial demo SOP. |
