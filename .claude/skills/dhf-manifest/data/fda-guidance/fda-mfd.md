# Tier 1 Regulatory Distillation — FDA Multiple Function Device Products

**Guidance**: Multiple Function Device Products: Policy and Considerations
**Date**: July 29, 2020 (Final)
**Statutory basis**: 21st Century Cures Act §520(o)(2) of the FD&C Act
**Topic coverage**: regulatory-submission, architecture, risk-management
**Distillation date**: 2026-04-21
**Source references**:
- `.claude/skills/medtech-docs/references/fda-guidance/mfd-distilled.md`

> **Note**: FDA guidance is nonbinding.

---

<a id="OBL-MFD-001"></a>

```yaml
id: OBL-MFD-001
title: "MFD Core Policy"
source: FDA MFD Guidance (2020) §III Core Policy
section: "Core MFD Policy — Device Functions vs. Other Functions"
scope_flags: [multi-function, 510k]
topic: regulatory-submission
artifact_type: analysis
dhf_owner: system
min_iec62304_class: A
applies_to: [510(k) Submission — Device Description, MFD Impact Analysis]
verbatim: "FDA shall not regulate non-device software functions as devices. However, FDA may assess the impact that non-device functions have on device functions when evaluating safety and effectiveness. Non-device and other functions are reviewed only when they could impact the device function-under-review."
extracted_requirements:
  - HipLink is a multiple function device product: Pre-Op (SaMD) + Intra-Op (SaMD) are device functions; Management Services is the "other function"
  - Management Services non-device functions (PostOp Reports, User Management, Account Management) are NOT reviewed unless they could adversely impact Pre-Op or Intra-Op
  - Document in the 510(k): which functions are device functions under review and which are "other functions"
  - Conduct a two-step impact assessment: (A) does the other function have impact on the device function? (B) if yes, could the impact increase risk or degrade performance?
```

**Context**: The HipLink system SAD's 5 enforcement rules (architectural separation between SaMD and non-SaMD) are directly relevant to MFD compliance. The architectural separation limits the impact of Management Services on Pre-Op and Intra-Op — Management Services cannot alter SaMD clinical outputs. This separation is the primary defense for limiting what FDA must review in Management Services.

---

<a id="OBL-MFD-002"></a>

```yaml
id: OBL-MFD-002
title: "MFD Impact Assessment"
source: FDA MFD Guidance (2020) §IV Impact Assessment
section: "Two-Step Impact Assessment — Shared Resources"
scope_flags: [multi-function, 510k]
topic: architecture
artifact_type: analysis
dhf_owner: system
min_iec62304_class: A
applies_to: [MFD Impact Analysis, System Hazard Analysis, Architecture Document]
verbatim: "Consider whether the functions share: computational resources, data dependencies (input data from other function used in critical calculations), code necessary for proper execution, memory or storage, output screen or GUI, programming pointers. Does the other function provide input data for a critical calculation? Does the other function affect processing time when sharing a processor? Does the other function serve as or impact a risk control measure for the device function?"
extracted_requirements:
  - Assess shared resources between Management Services and the SaMD modules: computational resources, data dependencies, code, memory/storage, GUI
  - Assess whether Management Services functions can provide input data to critical calculations in Pre-Op or Intra-Op
  - If Management Services hosts the Pre-Op web application: assess whether Management Services failure affects Pre-Op availability
  - Assess cybersecurity cross-function risks: assume "other functions" may be employed maliciously to adversely impact the device function
  - Document the impact assessment in the hazard analysis (ISO 14971) — cross-function impacts are device hazards
```

**Context**: For HipLink, the key MFD impact paths are: (1) Management Services delivers the Pre-Op plan to Intra-Op — a corrupted plan delivery is a device safety risk; (2) Management Services performs OTA updates to the Intra-Op tablet — a compromised update is a device safety risk; (3) Management Services hosts the Pre-Op web application — Management Services downtime means Pre-Op is unavailable. These must each be assessed for adverse impact on the device function.

---

<a id="OBL-MFD-003"></a>

```yaml
id: OBL-MFD-003
title: "MFD Premarket Requirements"
source: FDA MFD Guidance (2020) §V Premarket Submission Requirements
section: "Architecture Separation Recommendation"
scope_flags: [multi-function, 510k, common-baseline]
topic: architecture
artifact_type: design-document
dhf_owner: system
min_iec62304_class: A
applies_to: [System Architecture Document, 510(k) Submission — Architecture, Hazard Analysis]
verbatim: "Architectural separation strongly recommended. Logical separation, architectural separation, code and data partitioning should be used to the extent possible. Higher separation leads to easier independent review of safety and effectiveness. When separation is not achievable, interconnections and interdependencies must be explained in the hazard analysis with appropriate risk controls."
extracted_requirements:
  - The system SAD must document the architectural separation between device functions (Pre-Op, Intra-Op) and "other functions" (Management Services)
  - Demonstrate that Management Services cannot alter the clinical processing or outputs of Pre-Op or Intra-Op
  - Where interconnections exist (plan delivery, OTA updates), document them explicitly in the hazard analysis with risk controls
  - Submit the architecture/design documents showing how/if "other functions" interact with the device function
  - Higher architectural separation → simpler FDA review of the device functions in isolation
```

**Context**: The 5 enforcement rules already defined in the HipLink system SAD (Section 7 of `hiplink-system-sad.md`) are the architectural separation mechanism that satisfies this MFD guidance requirement. The SAD must be included in the 510(k) submission, and the MFD impact analysis must reference the SAD's enforcement rules as the documented controls. This is a direct connection between the design architecture and the regulatory submission — the SAD IS the MFD architectural separation evidence.

---

<a id="OBL-MFD-004"></a>

```yaml
id: OBL-MFD-004
title: "MFD Change Impact"
source: FDA MFD Guidance (2020) §VI Modifications to Other Functions
section: "Modifications to Other Functions — New Submission Assessment"
scope_flags: [multi-function, 510k, pccp]
topic: configuration-change
artifact_type: process-record
dhf_owner: system
min_iec62304_class: A
applies_to: [Design Change Records, PCCP Change Records, Change Impact Analysis]
verbatim: "When an other function is modified: assess whether the modification could significantly impact safety or effectiveness of the device function. If adverse impact (or labeled positive impact): reference applicable guidance to determine if a new premarket submission is required. Document the impact assessment per the quality system."
extracted_requirements:
  - Every modification to Management Services must be assessed for adverse impact on Pre-Op and Intra-Op safety/effectiveness
  - If a Management Services change could adversely affect either SaMD module, evaluate whether a new 510(k) is required
  - Even if Management Services changes are non-device, they must go through a documented impact assessment (QMS design change process)
  - PCCP changes affecting Management Services: assess cross-function impact before implementing
  - Document all Management Services change impact assessments per the QMS
```

**Context**: This is the ongoing post-market implication of the MFD structure. Every Management Services software update — even "routine" infrastructure updates — must be assessed for cross-function impact on Pre-Op and Intra-Op. The PCCP should address this: if the PCCP authorizes Management Services changes, the Modification Protocol must include a cross-function impact assessment step. This connects the MFD guidance to the day-to-day PCCP implementation workflow.
