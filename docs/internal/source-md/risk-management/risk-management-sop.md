---
source_file: "N/A — authored-in-markdown"
source_path: "risk-management/risk-management-sop.md"
doc_id: "GL-SOP-RM-001"
doc_type: "SOP"
title: "Risk Management (Master)"
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
  - doc_id: "ISO 14971:2019"
    title: "Medical devices — Application of risk management to medical devices"
    resolved: true
    match: null
    note: "Primary anchor"
  - doc_id: "ISO/TR 24971:2020"
    title: "Guidance on the application of ISO 14971"
    resolved: true
    match: null
    note: "Guidance"
  - doc_id: "ISO 13485:2016 §7.1"
    title: "Planning of product realization"
    resolved: true
    match: null
    note: "Requires risk-based approach"
conversion_history:
  - date: "2026-04-21"
    source: "v1 — initial draft under task ben/022"
notes: null
---

# GL-SOP-RM-001 — Risk Management (Master)

_Demo sample data — not for clinical use._

**Document ID:** GL-SOP-RM-001
**Revision:** 1.0
**Effective Date:** 2026-04-21
**Owner:** VP Quality, GlobalLogic MedTech

---

## 1. Purpose

Establish the risk-management process for GlobalLogic medical devices and medical device software throughout the product lifecycle, in accordance with **ISO 14971:2019** and guided by **ISO/TR 24971:2020**.

## 2. Scope

All products covered by the GlobalLogic QMS, from concept through post-market retirement. Covers hardware, firmware, SaMD, SiMD, electromechanical products, and their accessories and labeling.

## 3. Responsibilities

| Role | Responsibility |
|---|---|
| Top Management | Provide resources; set risk-acceptability policy; review RMF at Management Review |
| Risk Manager | Assemble the risk management team; maintain the Risk Management File |
| Design Owner | Integrate risk outputs into design (inputs, outputs, V&V) |
| Usability Engineering | Contribute use-related hazards (GL-SOP-UC-001) |
| Cybersecurity | Contribute security-related hazards (GL-SOP-SW-004) |
| Clinical Affairs | Provide clinical hazard data; benefit assessment |
| Post-Market Surveillance | Provide field data for lifecycle risk updates (GL-SOP-PM-001) |

## 4. Definitions (ISO 14971 §3)

- **Harm** — Physical injury or damage to the health of people, or damage to property or the environment.
- **Hazard** — Potential source of harm.
- **Hazardous situation** — Circumstance in which people, property, or environment is exposed to one or more hazards.
- **Foreseeable sequence of events** — Plausible chain leading from a hazard to a hazardous situation to harm.
- **Probability of occurrence of harm (P)** — Likelihood.
- **Severity of harm (S)** — Measure of possible consequences.
- **Risk** — Combination of P and S.
- **Residual risk** — Risk remaining after risk-control measures have been implemented.
- **Benefit-risk analysis** — Assessment whether overall benefits outweigh residual risks.
- **Risk Management File (RMF)** — Set of records for a given device demonstrating application of this process.

## 5. References

- ISO 14971:2019
- ISO/TR 24971:2020
- ISO 13485:2016 §7.1
- FDA Guidance — "Applying Human Factors and Usability Engineering to Medical Devices" (2016) — for use-related risks
- FDA Guidance — "Cybersecurity in Medical Devices: Quality System Considerations and Content of Premarket Submissions" (2023) — for cyber risks
- IEC 62304 §7 — Software risk management

## 6. Procedure

### 6.1 Risk Management Process Overview (ISO 14971 §4)

```
Risk Management Plan
        │
        ▼
  Risk Analysis  ──── Hazard Identification
        │              Hazardous Situation Identification
        │              Foreseeable Sequence Identification
        │              Risk Estimation (P × S)
        ▼
  Risk Evaluation (vs. acceptability criteria)
        │
        ▼
  Risk Control                     (inherently safe design → protective
        │                            measures → information for safety)
        ▼
  Residual Risk Evaluation
        │
        ▼
  Overall Residual Risk / Benefit-Risk
        │
        ▼
  Risk Management Report
        │
        ▼
  Production / Post-Production Activities (Lifecycle monitoring)
```

### 6.2 Risk Management Plan (§4.4)

Each project initiates an RM Plan (GL-TMP-RM-001) containing:

- Scope (product, lifecycle phases covered)
- Responsibilities and authorities
- Criteria for risk acceptability (categorical or matrix-based — documented rationale)
- Review activities (cadence, roles)
- Verification activities (evidence risk controls are implemented and effective)
- Method for collection and review of production and post-production information

The Plan is approved by the VP Quality before risk-analysis begins.

### 6.3 Risk Analysis (§5)

Hazards are identified via multiple techniques; at minimum:

- **Preliminary Hazard Analysis (PHA)** early in Concept/Feasibility
- **Hazard Analysis (HA)** during Design — linked to use, technology, environment
- **Design FMEA (dFMEA)** on architecture and components
- **Use-error analysis** per IEC 62366-1 (from GL-SOP-UC-001)
- **Cyber threat modeling** per IEC 81001-5-1 (from GL-SOP-SW-004) if connected
- **Process FMEA (pFMEA)** at pre-transfer

Each hazard is traced into a **hazardous situation** and one or more **foreseeable sequences of events** leading to harm.

### 6.4 Risk Estimation and Evaluation (§5.5, §6)

Risk is estimated using Probability × Severity. Acceptability is per the Plan's criteria (commonly a matrix with defined Broadly Acceptable / ALARP / Unacceptable regions). Non-acceptable risks require Risk Control.

### 6.5 Risk Control (§7)

Controls are applied in the following order of priority:

1. **Inherently safe design and manufacture**
2. **Protective measures in the device or manufacturing process**
3. **Information for safety** (labeling, training)

Each risk control is documented in the RMF, linked to a Design Input (GL-SOP-DC-003), and verified (GL-SOP-DC-006). The Risk Manager confirms that controls do not introduce new risks, or that any new risks are themselves evaluated.

### 6.6 Residual Risk Evaluation (§7.4–§7.6)

Residual risk of each hazardous situation is re-estimated after controls are applied and compared to acceptability criteria. Non-acceptable residual risks require additional controls or benefit-risk justification.

### 6.7 Overall Residual Risk and Benefit-Risk (§8)

Before commercial release, the team evaluates **overall residual risk** across the device and performs a benefit-risk analysis informed by clinical evidence (GL-SOP-UC-002) and intended use. Overall risk/benefit conclusion is documented in the Risk Management Report.

### 6.8 Risk Management Report (§9)

The RM Report is approved by Risk Manager, Design Owner, and VP Quality before the pre-Transfer Design Review (GL-SOP-DC-005). It summarizes: risk management plan execution, residual risks, benefit-risk conclusion, and provisions for production and post-production information review.

### 6.9 Production and Post-Production Activities (§10)

Lifecycle risk monitoring is integrated with:

- Production NCRs, yield data, supplier quality (GL-SOP-SP-001, GL-SOP-SP-004)
- Complaint handling (GL-SOP-PM-002)
- PMS outputs (GL-SOP-PM-001) — PMS Report / PSUR feeds risk update
- Adverse-event data (GL-SOP-PM-003)
- CAPA outputs (GL-SOP-QM-005)

The RMF is updated when new information changes the risk profile.

## 7. Records Generated

| Record | Retained by | Retention |
|---|---|---|
| Risk Management Plan (per product) | RMF | Per GL-SOP-QM-001 |
| Hazard/Risk Analysis (HA, FMEA, cyber, usability) | RMF | Per GL-SOP-QM-001 |
| Risk Management Report | RMF | Per GL-SOP-QM-001 |
| Lifecycle risk-review records | RMF | Per GL-SOP-QM-001 |

## 8. Revision History

| Rev | Date | Author | Summary |
|---|---|---|---|
| 1.0 | 2026-04-21 | Ben Xavier (via Claude, task ben/022) | Initial demo SOP. |
