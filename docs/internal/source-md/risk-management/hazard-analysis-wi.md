---
source_file: "N/A — authored-in-markdown"
source_path: "risk-management/hazard-analysis-wi.md"
doc_id: "GL-WI-RM-001"
doc_type: "WI"
title: "Hazard Analysis Work Instruction"
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
  - doc_id: "ISO/TR 24971:2020 §5"
    title: null
    resolved: true
    match: null
    note: null
conversion_history:
  - date: "2026-04-21"
    source: "v1 — initial draft under task ben/022"
notes: null
---

# GL-WI-RM-001 — Hazard Analysis Work Instruction

_Demo sample data — not for clinical use._

**Document ID:** GL-WI-RM-001
**Revision:** 1.0
**Parent SOP:** GL-SOP-RM-001

---

## 1. Purpose

Provide step-by-step instruction for performing a Hazard Analysis (HA) per ISO 14971:2019 §5, with guidance drawn from ISO/TR 24971:2020 §5.

## 2. When to Use

- During early design, alongside first Design Inputs
- When the product concept, intended use, or environment changes
- After significant design changes (per GL-SOP-DC-008)
- After significant post-market information changes the risk picture

## 3. Inputs Needed

- Intended use / indications for use / contraindications
- Intended user profile(s) and use environment(s)
- Preliminary architecture / component list
- Energy sources, materials, substances, outputs
- Historical data from predicate / similar devices
- Applicable standards' hazard lists (Annex C of ISO 14971; IEC 60601-1 hazards for EM devices; IEC 81001-5-1 threat catalog for connected)

## 4. Steps

1. **Characterize the device.** Per ISO 14971 Annex A qualitative questions — intended use, materials, energy, information flows, storage/transport, user profile, environment, disposal.
2. **Identify hazards.** Use structured stimulus lists:
   - ISO 14971 Annex C (energy, biological & chemical, operational, information, environmental)
   - IEC 60601-1 §4 / §5 (electrical, mechanical, thermal, radiation, biocompatibility)
   - IEC 81001-5-1 §5 (cyber threats — for connected devices)
   - IEC 62366-1 §5.4–§5.7 (use-related hazards — capture via GL-SOP-UC-001)
   - Historical failures from complaints / PMS / similar predicates
3. **Identify the hazardous situation** each hazard can produce.
4. **Identify the foreseeable sequence of events** from hazard → hazardous situation → harm. Include:
   - Single-fault, multi-fault, and no-fault-but-reasonably-foreseeable-misuse cases
   - Intended and foreseeable unintended uses
5. **Estimate Severity (S)** using the Plan's severity scale.
6. **Estimate Probability (P)** using the Plan's probability scale, informed by historical data where available; use conservative estimates when data are sparse.
7. **Record** in the Hazard Analysis Template (GL-TMP-RM-003).
8. **Evaluate** each risk against acceptability criteria. If above acceptable, proceed to Risk Control (per GL-SOP-RM-001 §6.5).

## 5. Quality Heuristics

- Every hazard row must have at least one clearly stated foreseeable sequence of events
- Do not merge multiple distinct sequences into one row
- Probability estimates must be defensible; note evidence (Annex C, predicate data, test data, expert judgment)
- Severity is a property of the harm, not of the hazard
- Use-related hazards are captured here and cross-linked to the Usability Engineering File
- Cyber hazards are captured here and cross-linked to the Threat Model

## 6. Outputs

- Completed Hazard Analysis table (GL-TMP-RM-003)
- List of Risk Controls required (feeds GL-SOP-DC-003 Design Inputs)
- List of new hazards introduced by controls (iterated until the analysis is stable)

## 7. Revision History

| Rev | Date | Author | Summary |
|---|---|---|---|
| 1.0 | 2026-04-21 | Ben Xavier (via Claude, task ben/022) | Initial demo WI. |
