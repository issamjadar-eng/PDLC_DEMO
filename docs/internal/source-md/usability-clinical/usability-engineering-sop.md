---
source_file: "N/A — authored-in-markdown"
source_path: "usability-clinical/usability-engineering-sop.md"
doc_id: "GL-SOP-UC-001"
doc_type: "SOP"
title: "Usability Engineering"
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
  - doc_id: "IEC 62366-1:2015"
    title: "Medical devices — Application of usability engineering to medical devices"
    resolved: true
    match: null
    note: "Primary anchor"
  - doc_id: "IEC/TR 62366-2:2016"
    title: "Guidance on the application of usability engineering"
    resolved: true
    match: null
    note: "Guidance"
  - doc_id: "FDA — Applying Human Factors and Usability Engineering to Medical Devices (2016)"
    title: null
    resolved: true
    match: null
    note: null
conversion_history:
  - date: "2026-04-21"
    source: "v1 — initial draft under task ben/022"
notes: null
---

# GL-SOP-UC-001 — Usability Engineering

_Demo sample data — not for clinical use._

**Document ID:** GL-SOP-UC-001
**Revision:** 1.0
**Effective Date:** 2026-04-21
**Owner:** Human Factors Lead, GlobalLogic MedTech

---

## 1. Purpose

Apply a Usability Engineering (UE) process to identify and mitigate use-related risks for GlobalLogic medical devices, per **IEC 62366-1:2015** and the **FDA 2016 HFE/UE Guidance**.

## 2. Scope

All medical devices under the GlobalLogic QMS, including hardware, firmware, SaMD, SiMD, and accessories.

## 3. Responsibilities

| Role | Responsibility |
|---|---|
| Human Factors Lead | Own Usability Engineering File; plan; lead evaluations |
| Design Owner | Integrate UE outputs into Design Inputs |
| Risk Manager | Integrate use-related risks with RMF (GL-SOP-RM-001) |
| Clinical Affairs | Provide clinician input; validate clinical use |
| Regulatory Affairs | Align on HFE submission expectations |

## 4. Definitions (IEC 62366-1 §3)

- **Use-related hazard** — A source of harm arising from use or foreseeable misuse.
- **Use error** — Action or lack of action by the user that leads to a different result than intended.
- **Normal use** — Operation including routine inspection, adjustment, and actions of the operator per IFU.
- **Reasonably foreseeable misuse** — Use in a way not intended, but that results from readily predictable human behavior.
- **Primary Operating Function** — Function that is essential for the correct operation of a safety-related function.
- **Hazard-related use scenario** — A use scenario that could lead to harm.
- **Usability Engineering File (UEF)** — The compilation of records and other documents produced by the UE process.

## 5. References

- IEC 62366-1:2015 (and IEC 62366-1:2015 AMD1:2020 where applicable)
- IEC/TR 62366-2:2016
- FDA — "Applying Human Factors and Usability Engineering to Medical Devices" (2016)
- ISO 14971:2019 — integration with risk management

## 6. Procedure

### 6.1 Usability Engineering Plan

A plan is drafted at project start (part of or referenced by the Design & Development Plan — GL-TMP-DC-001). Contents: scope, roles, deliverables, evaluation strategy (formative + summative), participant strategy.

### 6.2 Use Specification (§5.1)

A Use Specification (**GL-TMP-UC-001**) documents:

- Intended medical indication
- Intended patient population(s)
- Intended part of the body or tissue applied to / interacted with
- Intended user profile(s)
- Intended use environment(s)
- Operating principle of the device

### 6.3 User-Interface (UI) Characteristics Related to Safety (§5.2)

Identify the parts of the UI (hardware controls, displays, sounds, alarms, software screens, labels, IFU) that could contribute to hazards.

### 6.4 Hazards and Hazardous Situations Related to Use (§5.3)

Identify use errors and resulting hazardous situations. Flow into Hazard Analysis (GL-WI-RM-001).

### 6.5 Hazard-Related Use Scenarios (§5.4)

Document scenarios where the user can cause or fail to prevent a hazardous situation. Flag which scenarios are subject to summative evaluation.

### 6.6 Summative Evaluation Planning (§5.5)

Plan a summative usability evaluation for hazard-related use scenarios: participant profile(s), number, training, environment, scenarios, success criteria. Aligns with FDA 2016 guidance: typically 15+ representative users per distinct user group.

### 6.7 User-Interface Specification and Design (§5.6, §5.7)

UI requirements become Design Inputs (GL-SOP-DC-003). UI design outputs are Design Outputs (GL-SOP-DC-004).

### 6.8 Formative Evaluation (§5.8)

Iterative, exploratory — identifies use issues during design. Results feed back into UI design.

### 6.9 Summative Evaluation (§5.9)

Executed on a near-final (validation-equivalent) device, with a representative IFU, training, and environment. Objectives: demonstrate that hazard-related use scenarios can be performed successfully by representative users. Use errors are analyzed, root-caused, and risks re-estimated. Results are an input to Design Validation (GL-SOP-DC-006).

### 6.10 Usability Engineering File (UEF)

The **Usability Engineering File (GL-TMP-UC-002)** compiles §5.1–§5.9 records and references Formative and Summative protocols/reports (**GL-TMP-UC-003**). The UEF is part of the DHF.

## 7. Records Generated

| Record | Retained by | Retention |
|---|---|---|
| Usability Engineering File (GL-TMP-UC-002) | DHF | Per GL-SOP-QM-001 |
| Use Specification (GL-TMP-UC-001) | DHF | Per GL-SOP-QM-001 |
| Formative / Summative protocols and reports (GL-TMP-UC-003) | DHF | Per GL-SOP-QM-001 |

## 8. Revision History

| Rev | Date | Author | Summary |
|---|---|---|---|
| 1.0 | 2026-04-21 | Ben Xavier (via Claude, task ben/022) | Initial demo SOP. |
