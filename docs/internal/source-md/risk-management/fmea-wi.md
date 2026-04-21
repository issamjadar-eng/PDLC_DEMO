---
source_file: "N/A — authored-in-markdown"
source_path: "risk-management/fmea-wi.md"
doc_id: "GL-WI-RM-002"
doc_type: "WI"
title: "Failure Mode and Effects Analysis (FMEA) Work Instruction"
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
  - doc_id: "GL-SOP-RM-001"
    title: "Risk Management (Master)"
    resolved: true
    match: null
    note: "Parent SOP"
  - doc_id: "ISO 14971:2019 §5"
    title: null
    resolved: true
    match: null
    note: null
  - doc_id: "IEC 60812:2018"
    title: "Failure modes and effects analysis (FMEA and FMECA)"
    resolved: true
    match: null
    note: "FMEA methodology reference"
conversion_history:
  - date: "2026-04-21"
    source: "v1 — initial draft under task ben/022"
notes: null
---

# GL-WI-RM-002 — Failure Mode and Effects Analysis (FMEA) Work Instruction

_Demo sample data — not for clinical use._

**Document ID:** GL-WI-RM-002
**Revision:** 1.0
**Parent SOP:** GL-SOP-RM-001

---

## 1. Purpose

Provide step-by-step instruction for performing Design FMEA (dFMEA) and Process FMEA (pFMEA) — a bottom-up failure analysis complementing the top-down Hazard Analysis (GL-WI-RM-001). Methodology anchored in **IEC 60812:2018**.

## 2. When to Use

- **dFMEA** — during architecture and detailed design of the device
- **pFMEA** — before pre-Transfer review of manufacturing processes (GL-SOP-DC-007)
- After significant design or process changes

## 3. Inputs Needed

- Architecture (for dFMEA) or Process Flow Diagram (for pFMEA)
- Functional block diagrams with interfaces
- Component lists / BOM
- Historical data (similar products or processes)

## 4. Scoring Scales

Use the scoring scales defined in the product's Risk Management Plan (GL-TMP-RM-001). Typical scales (1–5 or 1–10) for:

- **Severity (S)** — impact on patient, user, or product
- **Occurrence (O)** — probability the failure mode occurs
- **Detection (D)** — probability the existing controls detect the failure before impact

**Risk Priority Number (RPN)** is not used as the sole acceptance criterion (ISO 14971 §5.5 requires risk defined as S×P). GlobalLogic uses S and O to drive acceptability; D is used to prioritize mitigation effort, not to discount unacceptable risks.

## 5. Steps

1. **Define the item under analysis** — function, boundaries, interfaces.
2. **Identify failure modes** for each function or component (loss of function, incorrect function, intermittent function, unintended function, fail-silent vs. fail-loud).
3. For each failure mode: identify **effects** at local, next-higher, and end-effect (patient/user) levels.
4. Identify **causes** for each failure mode.
5. Identify **existing prevention and detection controls**.
6. Score S, O, D.
7. **Link to Hazard Analysis**: every failure mode with potential patient harm must link to a Hazard Analysis row (GL-WI-RM-001).
8. **Recommended actions** for unacceptable risks — design changes, added controls, added V&V.
9. Track actions through Design Review (GL-SOP-DC-005) to closure; re-score after implementation.

## 6. Quality Heuristics

- Effects are expressed at the patient/user level, not just component-level symptoms
- Causes go deep enough to be actionable (e.g., "poor solder quality" → specific root cause)
- Actions that change the design cycle back to Hazard Analysis so new hazards aren't missed
- A dFMEA is not complete until every failure mode with harm potential is either controlled or accepted with documented rationale

## 7. Outputs

- Completed FMEA worksheet (GL-TMP-RM-004)
- Actions tracked in Design Review minutes and the RMF
- Updates to Hazard Analysis (GL-TMP-RM-003) and Risk Management Report (GL-TMP-RM-002)

## 8. Revision History

| Rev | Date | Author | Summary |
|---|---|---|---|
| 1.0 | 2026-04-21 | Ben Xavier (via Claude, task ben/022) | Initial demo WI. |
