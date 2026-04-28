# PDLC_DEMO QMS — DHF Obligations Mapping

_Demo sample data — not for clinical use._

Maps regulatory obligations (Tier 1 `OBL-*`) to MedTech Company QMS procedures that govern producing DHF deliverables satisfying them. Project-agnostic — reusable across any program built on the GlobalLogic QMS scaffold under `docs/internal/source-md/`.

**Generated**: 2026-04-27 (hand-authored under task ben/035)
**Total QMS obligations**: 10
**Source documents**: 10 — GL-SOP-DC-001, GL-SOP-DC-002, GL-SOP-DC-003, GL-SOP-DC-004, GL-SOP-DC-005, GL-SOP-DC-006, GL-SOP-DC-008, GL-SOP-RM-001, GL-SOP-SW-001, GL-SOP-PM-001
**DHF topics covered**: architecture, requirements, design-outputs, design-reviews, verification, validation, configuration-change, risk-management, software-lifecycle, post-market

---

## How to read this file

- Each H2 section covers one MedTech Company source document (SOP / WI / FORM / POL).
- Each section shows a compact markdown table summarising the obligations distilled from that source.
- Structured data per obligation lives in the `<!-- QMS-DATA ... -->` HTML comment block immediately after each table — hidden in rendered markdown, available to `build-qms`.
- `qms-manifest.json` (sibling, built by `/dhf-manifest build-qms`) is the programmatic sidecar with cross-maps.

---

## GL-SOP-DC-001 — Design Control (Master)

_1 QMS obligation covering architecture / design-controls overall._

| ID | Section | Topic | Applies To | Regulatory Grounding |
|----|---------|-------|-----------|----------------------|
| <a id="qms-arch-001"></a>[`QMS-ARCH-001` · Design Control Master](#qms-arch-001) — Author and maintain a Design History File (DHF) per device program. | GL-SOP-DC-001 §6 — Design Control (Master) | `architecture` | Design History File; Phase-gate evidence | [`OBL-13485-001` · Design & Development Planning](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-001) — Document the stages of design and development with defined entry/exit criteria; [`OBL-13485-002` · Design Input Documentation](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-002) — Document design inputs covering: functional, performance, and safety requirements |

<!-- QMS-DATA
records:
  - id: "QMS-ARCH-001"
    title: "Design Control Master"
    source: "GL-SOP-DC-001 §6"
    source_title: "Design Control (Master)"
    topic: "architecture"
    artifact_type: "plan"
    dhf_owner: "system"
    applies_to:
      - "Design History File"
      - "Phase-gate evidence"
    regulatory_grounding:
      - "OBL-13485-001"
      - "OBL-13485-002"
    verbatim: |
      "Define how MedTech Company plans, executes, reviews, and transfers
      product designs across the lifecycle — per ISO 13485:2016 §7.3 and
      21 CFR 820.30. Applies to all medical device products, SaMD, SiMD,
      hardware, firmware, accessories, and labeling."
    extracted_requirements:
      - "Author and maintain a Design History File (DHF) per device program."
      - "Operate via phase gates with go/no-go reviews; outcomes Pass / Conditional / Hold."
      - "Capture design-control evidence at each phase: plan, inputs, outputs, reviews, V&V, transfer."
    context: |
      Master SOP — anchors every other Design Controls SOP. The DHF index
      lists every controlled document with rev and effective date. Phase
      gates are the primary control point against drift.
-->

---

## GL-SOP-DC-002 — Design and Development Planning

_1 QMS obligation covering design planning._

| ID | Section | Topic | Applies To | Regulatory Grounding |
|----|---------|-------|-----------|----------------------|
| <a id="qms-arch-002"></a>[`QMS-ARCH-002` · Design and Development Plan](#qms-arch-002) — Author a Design and Development Plan from template GL-TMP-DC-001 at project initiation. | GL-SOP-DC-002 §6.2 — Design and Development Planning | `architecture` | Design and Development Plan | [`OBL-13485-002` · Design Input Documentation](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-002) — Document design inputs covering: functional, performance, and safety requirements |

<!-- QMS-DATA
records:
  - id: "QMS-ARCH-002"
    title: "Design and Development Plan"
    source: "GL-SOP-DC-002 §6.2"
    source_title: "Design and Development Planning"
    topic: "architecture"
    artifact_type: "plan"
    dhf_owner: "system"
    applies_to:
      - "Design and Development Plan"
    regulatory_grounding:
      - "OBL-13485-002"
    verbatim: |
      "The plan shall describe or reference: (a) Stages of design and
      development (Concept → Feasibility → Design → V&V → Transfer →
      Release); (b) Reviews required at each stage — who, what, go/no-go
      criteria; (c) Verification, validation, and design transfer
      activities appropriate to each stage."
    extracted_requirements:
      - "Author a Design and Development Plan from template GL-TMP-DC-001 at project initiation."
      - "Approve the DDP before any Design Inputs work begins."
      - "Update the DDP at each phase gate."
    context: |
      First DHF artifact authored. Functional leads (Systems, HW, FW, SW,
      Quality, Regulatory, Clinical, Usability, Risk, Cyber, Ops) each
      contribute sections and confirm resource commitments.
-->

---

## GL-SOP-DC-003 — Design Inputs

_1 QMS obligation covering requirements._

| ID | Section | Topic | Applies To | Regulatory Grounding |
|----|---------|-------|-----------|----------------------|
| <a id="qms-req-001"></a>[`QMS-REQ-001` · Design Input Specification](#qms-req-001) — Author a User Needs register and a Design Input Specification from GL-TMP-DC-002. | GL-SOP-DC-003 §6 — Design Inputs | `requirements` | User Needs register; Design Input Specification | [`OBL-13485-003` · Design Output Documentation](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-003) — Design outputs must demonstrably meet the design inputs — traceability is required |

<!-- QMS-DATA
records:
  - id: "QMS-REQ-001"
    title: "Design Input Specification"
    source: "GL-SOP-DC-003 §6"
    source_title: "Design Inputs"
    topic: "requirements"
    artifact_type: "spec"
    dhf_owner: "system"
    applies_to:
      - "User Needs register"
      - "Design Input Specification"
    regulatory_grounding:
      - "OBL-13485-003"
    verbatim: |
      "Design Inputs derive from User Needs and the Intended Use. Every
      Design Input shall be: unambiguous, testable, traceable to a User
      Need, and approved before downstream design work begins. Conflicts
      between inputs are resolved in writing and documented in the DHF."
    extracted_requirements:
      - "Author a User Needs register and a Design Input Specification from GL-TMP-DC-002."
      - "Every Design Input traces to at least one User Need."
      - "Every Design Input is testable (objective acceptance criterion stated)."
      - "Approve Design Inputs before authoring Design Outputs."
    context: |
      Inputs are the contractual surface between users and engineering.
      The trace matrix (UN ↔ DI) anchored here is the seed for every
      downstream verification artifact.
-->

---

## GL-SOP-DC-004 — Design Outputs

_1 QMS obligation covering design outputs._

| ID | Section | Topic | Applies To | Regulatory Grounding |
|----|---------|-------|-----------|----------------------|
| <a id="qms-dout-001"></a>[`QMS-DOUT-001` · Design Outputs](#qms-dout-001) — Author a System Architecture Document for each system DHF. | GL-SOP-DC-004 §6 — Design Outputs | `design-outputs` | System Architecture Document (SAD); Software Design Specification (SDS); Hardware Design Specification | [`OBL-13485-004` · Design Reviews](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-004) — Conduct design reviews at planned stages per the DDP |

<!-- QMS-DATA
records:
  - id: "QMS-DOUT-001"
    title: "Design Outputs"
    source: "GL-SOP-DC-004 §6"
    source_title: "Design Outputs"
    topic: "design-outputs"
    artifact_type: "spec"
    dhf_owner: "both"
    applies_to:
      - "System Architecture Document (SAD)"
      - "Software Design Specification (SDS)"
      - "Hardware Design Specification"
    regulatory_grounding:
      - "OBL-13485-004"
    verbatim: |
      "Design Outputs are the form in which design is implemented. Each
      output shall: (a) meet the Design Inputs; (b) provide enough detail
      to enable manufacturing, V&V, and clinical use; (c) reference
      acceptance criteria; (d) identify outputs that are essential for
      proper functioning of the device."
    extracted_requirements:
      - "Author a System Architecture Document for each system DHF."
      - "Author Software / Hardware design specifications for each item DHF."
      - "Identify and flag essential outputs (those required for proper functioning)."
      - "Approve outputs before V&V begins."
    context: |
      Outputs are the implementation contract. The SAD also serves as
      input to verification planning and to risk-control mapping.
-->

---

## GL-SOP-DC-005 — Design Review

_1 QMS obligation covering design reviews._

| ID | Section | Topic | Applies To | Regulatory Grounding |
|----|---------|-------|-----------|----------------------|
| <a id="qms-dr-001"></a>[`QMS-DR-001` · Design Review](#qms-dr-001) — Hold design reviews at each phase gate per the DDP. | GL-SOP-DC-005 §6 — Design Review | `design-reviews` | Design Review Record; Phase-gate minutes | [`OBL-13485-005` · Design Verification Planning](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-005) — Plan design verification at each development stage per the DDP |

<!-- QMS-DATA
records:
  - id: "QMS-DR-001"
    title: "Design Review"
    source: "GL-SOP-DC-005 §6"
    source_title: "Design Review"
    topic: "design-reviews"
    artifact_type: "record"
    dhf_owner: "system"
    applies_to:
      - "Design Review Record"
      - "Phase-gate minutes"
    regulatory_grounding:
      - "OBL-13485-005"
    verbatim: |
      "Design reviews shall be held at appropriate stages of the design
      process per the DDP. Each review shall include representatives of
      all functions concerned with the stage being reviewed plus an
      independent reviewer who has no direct responsibility for the stage.
      Outcomes (Pass / Conditional / Hold) and any actions are recorded."
    extracted_requirements:
      - "Hold design reviews at each phase gate per the DDP."
      - "Include an independent reviewer with no direct responsibility for that stage."
      - "Record outcomes on GL-FORM-DC-001 and capture actions with owners + due dates."
    context: |
      Reviews are the primary go/no-go control. Independence requirement
      is the most-cited audit finding — verify the reviewer's role is
      genuinely independent of the design work being reviewed.
-->

---

## GL-SOP-DC-006 — Design Verification and Validation

_2 QMS obligations covering verification and validation._

| ID | Section | Topic | Applies To | Regulatory Grounding |
|----|---------|-------|-----------|----------------------|
| <a id="qms-ver-001"></a>[`QMS-VER-001` · Design Verification](#qms-ver-001) — Author a Verification Protocol per GL-TMP-DC-003 covering all Design Inputs. | GL-SOP-DC-006 §6 (Verification) — Design Verification and Validation | `verification` | Verification Protocol; Verification Report | [`OBL-13485-006` · Design Validation Planning](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-006) — Plan design validation per the DDP — plan must precede execution |
| <a id="qms-val-001"></a>[`QMS-VAL-001` · Design Validation](#qms-val-001) — Author a Validation Protocol per GL-TMP-DC-004 covering all User Needs. | GL-SOP-DC-006 §6 (Validation) — Design Verification and Validation | `validation` | Validation Protocol; Validation Report | [`OBL-13485-007` · Design Transfer Procedure](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-007) — Define and follow a documented design transfer procedure |

<!-- QMS-DATA
records:
  - id: "QMS-VER-001"
    title: "Design Verification"
    source: "GL-SOP-DC-006 §6 (Verification)"
    source_title: "Design Verification and Validation"
    topic: "verification"
    artifact_type: "protocol"
    dhf_owner: "both"
    applies_to:
      - "Verification Protocol"
      - "Verification Report"
    regulatory_grounding:
      - "OBL-13485-006"
    verbatim: |
      "Verification confirms that Design Outputs meet Design Inputs.
      Verification methods include inspection, analysis, demonstration,
      and test. Each Design Input shall be verified by at least one
      method; the verification record shall cite the input ID, the method
      used, the acceptance criterion, and the result."
    extracted_requirements:
      - "Author a Verification Protocol per GL-TMP-DC-003 covering all Design Inputs."
      - "Every Design Input has at least one verification method (I/A/D/T)."
      - "Record results with input ID, method, acceptance criterion, and pass/fail."
    context: |
      Verification answers 'did we build the device right' against the
      input contract. The trace matrix (DI ↔ V&V) anchors here.
  - id: "QMS-VAL-001"
    title: "Design Validation"
    source: "GL-SOP-DC-006 §6 (Validation)"
    source_title: "Design Verification and Validation"
    topic: "validation"
    artifact_type: "protocol"
    dhf_owner: "system"
    applies_to:
      - "Validation Protocol"
      - "Validation Report"
    regulatory_grounding:
      - "OBL-13485-007"
    verbatim: |
      "Validation confirms that the device meets User Needs and intended
      use under simulated or actual use conditions. Validation shall be
      performed on production-equivalent units in the intended use
      environment with representative users. Summative usability
      evaluation (per IEC 62366-1) is part of validation for any device
      with user interfaces."
    extracted_requirements:
      - "Author a Validation Protocol per GL-TMP-DC-004 covering all User Needs."
      - "Use production-equivalent units in the intended use environment."
      - "Recruit representative users for any human-factors evaluation."
    context: |
      Validation answers 'did we build the right device' against User
      Needs. Distinct from V&V verification — validation must reflect
      actual or simulated use, not bench testing alone.
-->

---

## GL-SOP-DC-008 — Design Change Control

_1 QMS obligation covering configuration & change control._

| ID | Section | Topic | Applies To | Regulatory Grounding |
|----|---------|-------|-----------|----------------------|
| <a id="qms-cc-001"></a>[`QMS-CC-001` · Design Change Control](#qms-cc-001) — File a Document Change Request for every change to a released design. | GL-SOP-DC-008 §6 — Design Change Control | `configuration-change` | Document Change Request; 510(k) Change Determination | [`OBL-13485-009` · Design History File](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-009) — Maintain a Design History File (DHF) for each device type or family; [`OBL-510K-002` · Predicate Device Selection](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-510k.md#OBL-510K-002) — Select a primary predicate with intended use and technological characteristics most similar to MedTech Project |

<!-- QMS-DATA
records:
  - id: "QMS-CC-001"
    title: "Design Change Control"
    source: "GL-SOP-DC-008 §6"
    source_title: "Design Change Control"
    topic: "configuration-change"
    artifact_type: "record"
    dhf_owner: "system"
    applies_to:
      - "Document Change Request"
      - "510(k) Change Determination"
    regulatory_grounding:
      - "OBL-13485-009"
      - "OBL-510K-002"
    verbatim: |
      "Every change to a released design shall be (a) documented on a
      Document Change Request, (b) reviewed by impact analysis covering
      regulatory, risk, V&V, labeling, and post-market implications, (c)
      verified, and (d) approved by the change board before
      implementation. For cleared devices, FDA's 510(k) change-significance
      analysis (per the 2017 Guidance) shall be applied to determine
      whether a new 510(k) is required."
    extracted_requirements:
      - "File a Document Change Request for every change to a released design."
      - "Conduct impact analysis covering regulatory, risk, V&V, labeling, and post-market."
      - "Apply FDA's 2017 510(k) change guidance to cleared devices."
      - "Approve via change board before implementation."
    context: |
      Change control is the boundary between design controls and
      production / post-market. The 510(k) change-significance analysis
      is the most consequential output — wrong call = enforcement risk.
-->

---

## GL-SOP-RM-001 — Risk Management (Master)

_1 QMS obligation covering risk management._

| ID | Section | Topic | Applies To | Regulatory Grounding |
|----|---------|-------|-----------|----------------------|
| <a id="qms-rm-001"></a>[`QMS-RM-001` · Risk Management Master](#qms-rm-001) — Author a Risk Management Plan per GL-TMP-RM-001 at project initiation. | GL-SOP-RM-001 §6 — Risk Management (Master) | `risk-management` | Risk Management Plan; Hazard Analysis; Design FMEA / Process FMEA; Risk Management Report | [`OBL-14971-001` · Risk Management Plan](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-001) — Produce a Risk Management Plan before risk management activities begin; [`OBL-14971-002` · RM Plan Content](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-002) — Define the scope — which device, which functions, which lifecycle phases |

<!-- QMS-DATA
records:
  - id: "QMS-RM-001"
    title: "Risk Management Master"
    source: "GL-SOP-RM-001 §6"
    source_title: "Risk Management (Master)"
    topic: "risk-management"
    artifact_type: "plan"
    dhf_owner: "system"
    applies_to:
      - "Risk Management Plan"
      - "Hazard Analysis"
      - "Design FMEA / Process FMEA"
      - "Risk Management Report"
    regulatory_grounding:
      - "OBL-14971-001"
      - "OBL-14971-002"
    verbatim: |
      "Establish the risk-management process for MedTech Company medical
      devices and medical device software throughout the product
      lifecycle, in accordance with ISO 14971:2019 and guided by
      ISO/TR 24971:2020. Maintain a Risk Management File (RMF) per device,
      covering hazard identification, risk estimation, risk evaluation,
      risk control, residual-risk evaluation, and benefit-risk analysis."
    extracted_requirements:
      - "Author a Risk Management Plan per GL-TMP-RM-001 at project initiation."
      - "Maintain a Risk Management File: Plan, Hazard Analysis, FMEAs, Report."
      - "Update the RMF with post-market and use-related risks across the lifecycle."
      - "Conduct benefit-risk analysis when residual risk exceeds acceptability criteria."
    context: |
      RMF is the connective tissue across design, usability, cybersecurity,
      and post-market. Use-related risks (IEC 62366-1) and security risks
      (IEC 81001-5-1) flow into the same RMF, not separate silos.
-->

---

## GL-SOP-SW-001 — Medical Device Software Lifecycle

_1 QMS obligation covering software lifecycle._

| ID | Section | Topic | Applies To | Regulatory Grounding |
|----|---------|-------|-----------|----------------------|
| <a id="qms-sw-001"></a>[`QMS-SW-001` · Medical Device Software Lifecycle](#qms-sw-001) — Author a Software Development Plan per GL-TMP-SW-001 for each software-item DHF. | GL-SOP-SW-001 §6 — Medical Device Software Lifecycle | `software-lifecycle` | Software Development Plan; Software Architecture; SOUP Register | [`OBL-62304-001` · Software Safety Classification](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-001) — Assign IEC 62304 safety class (A, B, or C) to each software item before development begins; [`OBL-62304-002` · Software Development Plan](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-002) — Establish a Software Development Plan (SDP) before beginning software development |

<!-- QMS-DATA
records:
  - id: "QMS-SW-001"
    title: "Medical Device Software Lifecycle"
    source: "GL-SOP-SW-001 §6"
    source_title: "Medical Device Software Lifecycle"
    topic: "software-lifecycle"
    artifact_type: "plan"
    dhf_owner: "item"
    applies_to:
      - "Software Development Plan"
      - "Software Architecture"
      - "SOUP Register"
    regulatory_grounding:
      - "OBL-62304-001"
      - "OBL-62304-002"
    verbatim: |
      "Apply IEC 62304:2006+A1:2015 across the software lifecycle for every
      medical device software item. The Software Safety Class
      (A / B / C per §4.3) drives the depth of required activities;
      Class C demands integration testing per item, unit testing, and
      detailed design documentation. SOUP / OTS components shall be
      identified, risk-assessed, and tracked in the SOUP register."
    extracted_requirements:
      - "Author a Software Development Plan per GL-TMP-SW-001 for each software-item DHF."
      - "Assign a Software Safety Class (A / B / C) per IEC 62304 §4.3 with rationale."
      - "Maintain a SOUP register listing all third-party components."
    context: |
      The Software Safety Class is the load-bearing determination — it
      sets the V&V depth, documentation, and audit-readiness scope.
      Class C requires the most evidence; misclassification underwater
      is a frequent finding.
-->

---

## GL-SOP-PM-001 — Post-Market Surveillance

_1 QMS obligation covering post-market surveillance._

| ID | Section | Topic | Applies To | Regulatory Grounding |
|----|---------|-------|-----------|----------------------|
| <a id="qms-pm-001"></a>[`QMS-PM-001` · Post-Market Surveillance](#qms-pm-001) — Author a PMS Plan per GL-TMP-PM-001 for each device program. | GL-SOP-PM-001 §6 — Post-Market Surveillance | `post-market` | PMS Plan; Periodic Safety Update Report | [`OBL-13485-010` · SOUP Supplier Qualification](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-010) — Evaluate and qualify SOUP/third-party software components as suppliers (for IEC 62304 Class B/C, SOUP evaluation is also an IEC 62304 §8.1.2 obligation) |

<!-- QMS-DATA
records:
  - id: "QMS-PM-001"
    title: "Post-Market Surveillance"
    source: "GL-SOP-PM-001 §6"
    source_title: "Post-Market Surveillance"
    topic: "post-market"
    artifact_type: "plan"
    dhf_owner: "system"
    applies_to:
      - "PMS Plan"
      - "Periodic Safety Update Report"
    regulatory_grounding:
      - "OBL-13485-010"
    verbatim: |
      "Establish a post-market surveillance system for each device — per
      EU MDR Articles 83–86 + Annex III, ISO 13485:2016 §8.2.1, and
      ISO/TR 20416. PMS data shall feed the Risk Management File, the
      Clinical Evaluation Plan, and the design change-control loop.
      Periodic Safety Update Reports (PSURs) are produced per the device
      class cadence."
    extracted_requirements:
      - "Author a PMS Plan per GL-TMP-PM-001 for each device program."
      - "Define data sources: complaints, vigilance, literature, registries, field service."
      - "Feed PMS findings into RMF and CEP at defined cadences."
      - "Produce PSUR / PMSR per device class cadence."
    context: |
      PMS closes the loop from field back into design controls. The
      'feedback into RMF' clause is the one most likely to surface in
      audit — projects often have PMS data but no documented feedback
      pathway into the risk file.
-->
