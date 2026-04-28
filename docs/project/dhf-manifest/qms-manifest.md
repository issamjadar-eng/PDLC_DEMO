# PDLC_DEMO QMS — DHF Obligations Mapping

_Demo sample data — not for clinical use._

Maps regulatory obligations (Tier 1 `OBL-*`) to MedTech Company QMS procedures that govern producing DHF deliverables satisfying them. Project-agnostic — reusable across any program built on the GlobalLogic QMS scaffold under `docs/internal/source-md/`.

**Generated**: 2026-04-27 (hand-authored under tasks ben/035 + ben/036)
**Total QMS obligations**: 20
**Source documents**: 18 — GL-SOP-DC-001, GL-SOP-DC-002, GL-SOP-DC-003, GL-SOP-DC-004, GL-SOP-DC-005, GL-SOP-DC-006, GL-SOP-DC-008, GL-SOP-RM-001, GL-SOP-SW-001, GL-SOP-PM-001, GL-WI-DC-001, GL-WI-DC-002, GL-WI-SW-003, GL-WI-SW-004, GL-SOP-RA-001, GL-WI-RA-001, GL-SOP-UC-001, GL-SOP-UC-002 (plus standards GL-STD-RM-001, GL-STD-RM-002 cited)
**DHF topics covered**: All 16 — architecture, requirements, design-outputs, design-reviews, verification, validation, configuration-change, risk-management, software-lifecycle, post-market, traceability, cybersecurity, regulatory-submission, human-factors, clinical, labeling-ifu

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

---

## GL-WI-DC-001 — Design History File Process

_1 QMS obligation covering DHF assembly._

| ID | Section | Topic | Applies To | Regulatory Grounding |
|----|---------|-------|-----------|----------------------|
| <a id="qms-arch-003"></a>[`QMS-ARCH-003` · Design History File Process](#qms-arch-003) — Maintain a DHF Index at the root of every device DHF. | GL-WI-DC-001 §4-§5 — Design History File Process | `architecture` | DHF Index; Phase-gate freeze evidence | [`OBL-13485-001` · Design & Development Planning](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-001) — Document the stages of design and development with defined entry/exit criteria |

<!-- QMS-DATA
records:
  - id: "QMS-ARCH-003"
    title: "Design History File Process"
    source: "GL-WI-DC-001 §4-§5"
    source_title: "Design History File Process"
    topic: "architecture"
    artifact_type: "record"
    dhf_owner: "system"
    applies_to:
      - "DHF Index"
      - "Phase-gate freeze evidence"
    regulatory_grounding:
      - "OBL-13485-001"
    verbatim: |
      "Every DHF starts with a DHF Index (one markdown / spreadsheet file
      at the DHF root) listing every controlled artifact. Required columns:
      Doc ID, Title, Type, Phase, Status, Revision, Effective Date, Owner,
      Path, Trace. The DHF lives under docs/project/dhfs/<dhf-name>/ with
      this canonical layout: design-controls / risk-management /
      cybersecurity / usability / clinical / postmarket subfolders."
    extracted_requirements:
      - "Maintain a DHF Index at the root of every device DHF."
      - "Use the canonical folder layout (design-controls, risk-management, cybersecurity, usability, clinical, postmarket)."
      - "Freeze the DHF at phase gates per GL-FORM-DC-002."
      - "Apply submission freeze when an RA submission package is assembled."
      - "Apply release freeze at design transfer."
    context: |
      The WI is the practitioner-level companion to GL-SOP-DC-001 — the
      latter establishes that a DHF exists, the WI tells you how to
      build one. The freeze-point convention (phase / submission /
      release) is the most-cited audit pattern.
-->

---

## GL-WI-DC-002 — Design Traceability Matrix

_1 QMS obligation covering trace-matrix process._

| ID | Section | Topic | Applies To | Regulatory Grounding |
|----|---------|-------|-----------|----------------------|
| <a id="qms-trc-001"></a>[`QMS-TRC-001` · Design Traceability Matrix](#qms-trc-001) — Author a Design Traceability Matrix per device DHF. | GL-WI-DC-002 §3-§6 — Design Traceability Matrix | `traceability` | Trace Matrix (markdown + JSON sidecar); Phase-gate orphan checks | [`OBL-13485-004` · Design Reviews](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-004) — Conduct design reviews at planned stages per the DDP; [`OBL-62304-001` · Software Safety Classification](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-001) — Assign IEC 62304 safety class (A, B, or C) to each software item before development begins |

<!-- QMS-DATA
records:
  - id: "QMS-TRC-001"
    title: "Design Traceability Matrix"
    source: "GL-WI-DC-002 §3-§6"
    source_title: "Design Traceability Matrix"
    topic: "traceability"
    artifact_type: "record"
    dhf_owner: "both"
    applies_to:
      - "Trace Matrix (markdown + JSON sidecar)"
      - "Phase-gate orphan checks"
    regulatory_grounding:
      - "OBL-13485-004"
      - "OBL-62304-001"
    verbatim: |
      "The five-column trace shape is required for every device DHF:
      User Need (UN) → Design Input (DI) → Design Output (DO) → V&V
      (Verification or Validation Activity) → Risk Control (if any).
      Every User Need shall trace forward to at least one Design Input.
      Every V&V activity shall trace backward to at least one Design Input."
    extracted_requirements:
      - "Author a Design Traceability Matrix per device DHF."
      - "Establish baseline at Gate 2 (UN ↔ DI) and complete by Gate 4."
      - "Run forward-orphan and backward-orphan checks at every phase gate."
      - "Update the DTM in lockstep with every design change (per GL-SOP-DC-008)."
    context: |
      Trace-matrix gaps are the primary failure surface at audit because
      they betray missing requirements, missing tests, or un-validated
      risk controls. Building it once at the end is the canonical
      anti-pattern.
-->

---

## GL-WI-SW-003 — Threat Modeling

_1 QMS obligation covering cybersecurity threat modeling._

| ID | Section | Topic | Applies To | Regulatory Grounding |
|----|---------|-------|-----------|----------------------|
| <a id="qms-cyb-001"></a>[`QMS-CYB-001` · Threat Modeling](#qms-cyb-001) — Produce a Data-Flow Diagram showing asset flows + trust boundaries. | GL-WI-SW-003 §3-§5 — Threat Modeling | `cybersecurity` | Asset inventory; Data-flow diagram; Trust-boundary list; STRIDE-derived threat list; Mitigation map | [`OBL-81001-001` · Security Risk Management Plan](../../../.claude/skills/dhf-manifest/data/standards/iec-81001-5-1.md#OBL-81001-001) — Integrate security risk management with the ISO 14971 risk management process — security risks must appear in the device risk file; [`OBL-81001-002` · Secure Development Plan](../../../.claude/skills/dhf-manifest/data/standards/iec-81001-5-1.md#OBL-81001-002) — Include security activities in the SDP: threat modeling, secure design, security testing, vulnerability management |

<!-- QMS-DATA
records:
  - id: "QMS-CYB-001"
    title: "Threat Modeling"
    source: "GL-WI-SW-003 §3-§5"
    source_title: "Threat Modeling"
    topic: "cybersecurity"
    artifact_type: "record"
    dhf_owner: "both"
    applies_to:
      - "Asset inventory"
      - "Data-flow diagram"
      - "Trust-boundary list"
      - "STRIDE-derived threat list"
      - "Mitigation map"
    regulatory_grounding:
      - "OBL-81001-001"
      - "OBL-81001-002"
    verbatim: |
      "A complete threat model produces five artifacts: Asset inventory,
      Data-flow diagram (DFD), Trust-boundary list, Threat list (STRIDE-
      derived), and Mitigation map. For each asset crossing each trust
      boundary, walk the STRIDE categories and identify plausible threats.
      Threats whose successful exploitation maps to patient harm receive
      attack-tree drilldown."
    extracted_requirements:
      - "Produce a Data-Flow Diagram showing asset flows + trust boundaries."
      - "Enumerate threats via STRIDE per asset per trust boundary."
      - "Map each threat to a control + V&V evidence (per GL-WI-SW-004)."
      - "Update the model at every phase gate and every CVE disclosure."
      - "Pen-test scope derives from the threat model, not vice versa."
    context: |
      FDA's 2023 cybersecurity guidance specifically requires the threat
      model as a pre-market deliverable — its absence is a frequent AI
      Hold reason. Pen-test findings outside the model indicate the
      model has gaps.
-->

---

## GL-WI-SW-004 — Software Verification and Validation

_1 QMS obligation covering software V&V depth by class._

| ID | Section | Topic | Applies To | Regulatory Grounding |
|----|---------|-------|-----------|----------------------|
| <a id="qms-ver-002"></a>[`QMS-VER-002` · Software V&V (per IEC 62304 Class)](#qms-ver-002) — Author test protocols + reports for unit, integration, and system tests per Software Safety Class. | GL-WI-SW-004 §3-§6 — Software Verification and Validation | `verification` | Unit Test Protocol & Report; Integration Test Protocol & Report; System Test Protocol & Report | [`OBL-62304-005` · SRS Content Requirements](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-005) — SRS must cover: functional/capability requirements, I/O requirements, external interfaces; [`OBL-62304-006` · SRS Risk Control Trace](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-006) — Re-evaluate risk after SRS is established — update risk file if new hazards emerge |

<!-- QMS-DATA
records:
  - id: "QMS-VER-002"
    title: "Software V&V (per IEC 62304 Class)"
    source: "GL-WI-SW-004 §3-§6"
    source_title: "Software Verification and Validation"
    topic: "verification"
    artifact_type: "protocol"
    dhf_owner: "item"
    applies_to:
      - "Unit Test Protocol & Report"
      - "Integration Test Protocol & Report"
      - "System Test Protocol & Report"
    regulatory_grounding:
      - "OBL-62304-005"
      - "OBL-62304-006"
    verbatim: |
      "Three test levels are defined; their required execution depends
      on Software Safety Class: Unit Test, Integration Test, System Test.
      For Class B and C: statement coverage ≥ 80% (target 100% on Class C);
      branch coverage ≥ 70% (target 100% on Class C). Software tools used
      in V&V that impact the test result shall be validated for their
      intended use per IEC 62304 §6.1."
    extracted_requirements:
      - "Author test protocols + reports for unit, integration, and system tests per Software Safety Class."
      - "Class C software requires negative testing of every safety-critical input."
      - "Class C software requires independent code review."
      - "Tool-validate any V&V tool that affects the test result (coverage analyzers, test runners, static analyzers)."
    context: |
      Per-class test depth is the IEC 62304 lever. Class A is required
      to do system test only; Class C must do all three with high
      coverage and independent review. Misclassification (claiming A
      when the code drives a safety control) is a frequent finding.
-->

---

## GL-SOP-RA-001 — Regulatory Operations

_1 QMS obligation covering regulatory operations + pathway determination._

| ID | Section | Topic | Applies To | Regulatory Grounding |
|----|---------|-------|-----------|----------------------|
| <a id="qms-rs-001"></a>[`QMS-RS-001` · Regulatory Operations](#qms-rs-001) — Author Regulatory Strategy memo at Gate 1; update at every gate. | GL-SOP-RA-001 §5.1, §5.4 — Regulatory Operations | `regulatory-submission` | Regulatory Strategy memo; Regulatory Communications Register | [`OBL-510K-001` · Substantial Equivalence Argument](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-510k.md#OBL-510K-001) — Demonstrate same intended use as the predicate device — intended use is the general purpose/function, encompassing indications for use; [`OBL-510K-002` · Predicate Device Selection](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-510k.md#OBL-510K-002) — Select a primary predicate with intended use and technological characteristics most similar to MedTech Project |

<!-- QMS-DATA
records:
  - id: "QMS-RS-001"
    title: "Regulatory Operations"
    source: "GL-SOP-RA-001 §5.1, §5.4"
    source_title: "Regulatory Operations"
    topic: "regulatory-submission"
    artifact_type: "plan"
    dhf_owner: "system"
    applies_to:
      - "Regulatory Strategy memo"
      - "Regulatory Communications Register"
    regulatory_grounding:
      - "OBL-510K-001"
      - "OBL-510K-002"
    verbatim: |
      "For each new device program, the Regulatory Affairs Lead produces
      a Regulatory Strategy memo at Gate 1 (Concept → Feasibility) of the
      project. The strategy classifies the device per the product code
      system, recommends a pathway (510(k) traditional / abbreviated /
      special, De Novo, PMA, MDR Annex IX or X), identifies predicates,
      and identifies whether a Pre-Submission interaction is recommended."
    extracted_requirements:
      - "Author Regulatory Strategy memo at Gate 1; update at every gate."
      - "Maintain Regulatory Communications Register for all agency interactions."
      - "Apply pathway-specific submission WIs (e.g., GL-WI-RA-001 for 510(k))."
      - "Apply change-significance test (FDA 2017 510(k) flowchart) at every post-clearance change."
    context: |
      Regulatory strategy is a living document, not a one-time deliverable.
      The strategy memo + Communications Register are the two artifacts an
      agency inspection looks for when assessing the regulatory function.
-->

---

## GL-WI-RA-001 — 510(k) Submission Process

_1 QMS obligation covering 510(k) submission assembly._

| ID | Section | Topic | Applies To | Regulatory Grounding |
|----|---------|-------|-----------|----------------------|
| <a id="qms-rs-002"></a>[`QMS-RS-002` · 510(k) Submission Process](#qms-rs-002) — Confirm pre-assembly requirements complete before opening eSTAR. | GL-WI-RA-001 §4-§7 — 510(k) Submission Process | `regulatory-submission` | 510(k) Submission Package (eSTAR); Predicate Comparison Table; Substantial-Equivalence Narrative | [`OBL-510K-001` · Substantial Equivalence Argument](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-510k.md#OBL-510K-001) — Demonstrate same intended use as the predicate device — intended use is the general purpose/function, encompassing indications for use; [`OBL-510K-002` · Predicate Device Selection](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-510k.md#OBL-510K-002) — Select a primary predicate with intended use and technological characteristics most similar to MedTech Project; [`OBL-510K-003` · Performance Data for SE](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-510k.md#OBL-510K-003) — Apply the least-burdensome principle: provide the minimum data necessary to demonstrate SE |

<!-- QMS-DATA
records:
  - id: "QMS-RS-002"
    title: "510(k) Submission Process"
    source: "GL-WI-RA-001 §4-§7"
    source_title: "510(k) Submission Process"
    topic: "regulatory-submission"
    artifact_type: "protocol"
    dhf_owner: "system"
    applies_to:
      - "510(k) Submission Package (eSTAR)"
      - "Predicate Comparison Table"
      - "Substantial-Equivalence Narrative"
    regulatory_grounding:
      - "OBL-510K-001"
      - "OBL-510K-002"
      - "OBL-510K-003"
    verbatim: |
      "The eSTAR template (FDA-provided PDF form) is the canonical
      container. Required sections include: Cover Sheet, Indications for
      Use, 510(k) Summary, Standards, Software (if applicable per FDA
      software guidance), Cybersecurity (per FDA 2023 guidance),
      Performance — Bench / Animal / Clinical, Substantial Equivalence
      Discussion, Labeling. Each attached document is a PDF derived from
      the controlled DHF artifact at the cited revision."
    extracted_requirements:
      - "Confirm pre-assembly requirements complete before opening eSTAR."
      - "Produce Predicate Comparison Table with same/different framework."
      - "Author SE narrative: intended use, indications, technological characteristics, performance, conclusion."
      - "Internal sign-off (RA Lead + Quality + VP RA) before transmittal."
      - "Track in Regulatory Communications Register through clearance."
      - "Activate post-market surveillance per GL-SOP-PM-001 on clearance."
    context: |
      The eSTAR submission shape is mandatory since October 2023.
      Pre-assembly readiness (DHF baselined, V&V complete, RMF approved,
      cybersecurity docs complete) is the load-bearing check — submitting
      with stale or missing DHF references guarantees AI Hold cycles.
-->

---

## GL-SOP-UC-001 — Usability Engineering

_1 QMS obligation covering human-factors / usability engineering._

| ID | Section | Topic | Applies To | Regulatory Grounding |
|----|---------|-------|-----------|----------------------|
| <a id="qms-hf-001"></a>[`QMS-HF-001` · Usability Engineering](#qms-hf-001) — Author a Usability Engineering Plan at project start (per GL-TMP-DC-001). | GL-SOP-UC-001 §6 — Usability Engineering | `human-factors` | Usability Engineering File; Use Specification; Use-Related Risk Analysis; Formative Evaluation Report; Summative Evaluation Report | [`OBL-62366-001` · Usability Engineering Plan](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-001) — Establish a usability engineering process and maintain it throughout the development lifecycle; [`OBL-62366-002` · Use Specification](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-002) — Identify and characterize the intended users for each use scenario; [`OBL-62366-003` · User Profiles & Environments](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-003) — Document the intended use environment for each module; [`OBL-62366-004` · Use-Related Risk Analysis](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-004) — Identify all potential use errors per module — perception errors, cognitive errors, action errors |

<!-- QMS-DATA
records:
  - id: "QMS-HF-001"
    title: "Usability Engineering"
    source: "GL-SOP-UC-001 §6"
    source_title: "Usability Engineering"
    topic: "human-factors"
    artifact_type: "plan"
    dhf_owner: "system"
    applies_to:
      - "Usability Engineering File"
      - "Use Specification"
      - "Use-Related Risk Analysis"
      - "Formative Evaluation Report"
      - "Summative Evaluation Report"
    regulatory_grounding:
      - "OBL-62366-001"
      - "OBL-62366-002"
      - "OBL-62366-003"
      - "OBL-62366-004"
    verbatim: |
      "Apply a Usability Engineering (UE) process to identify and mitigate
      use-related risks for MedTech Company medical devices, per IEC
      62366-1:2015 and the FDA 2016 HFE/UE Guidance. The Usability
      Engineering File (UEF) compiles records produced by the UE process:
      Use Specification (intended users, use environments, primary
      operating functions), Use-Related Risk Analysis, formative
      evaluations during design, and summative evaluation pre-market."
    extracted_requirements:
      - "Author a Usability Engineering Plan at project start (per GL-TMP-DC-001)."
      - "Maintain a Usability Engineering File per device under GL-TMP-UC-002."
      - "Author a Use Specification (GL-TMP-UC-001) covering intended users / environments / primary operating functions."
      - "Conduct formative evaluations iteratively during design."
      - "Conduct a summative usability evaluation pre-market (per GL-TMP-UC-003) on production-equivalent units in the intended use environment."
      - "Integrate use-related risks into the Risk Management File (GL-SOP-RM-001)."
    context: |
      HFE outputs feed three downstream artifacts: Design Inputs (use-
      derived requirements), the Risk Management File (use-related
      hazards), and the labeling pipeline (warnings, IFU, training).
      Summative evaluation is part of design validation per GL-SOP-DC-006.
-->

---

## GL-SOP-UC-002 — Clinical Evaluation

_1 QMS obligation covering clinical evaluation._

| ID | Section | Topic | Applies To | Regulatory Grounding |
|----|---------|-------|-----------|----------------------|
| <a id="qms-clin-001"></a>[`QMS-CLIN-001` · Clinical Evaluation](#qms-clin-001) — Author a Clinical Evaluation Plan per GL-TMP-UC-004 covering scope, methodology, and acceptance criteria. | GL-SOP-UC-002 §6 — Clinical Evaluation | `clinical` | Clinical Evaluation Plan; Clinical Evaluation Report; Post-Market Clinical Follow-up Plan | [`OBL-13485-007` · Design Transfer Procedure](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-007) — Define and follow a documented design transfer procedure |

<!-- QMS-DATA
records:
  - id: "QMS-CLIN-001"
    title: "Clinical Evaluation"
    source: "GL-SOP-UC-002 §6"
    source_title: "Clinical Evaluation"
    topic: "clinical"
    artifact_type: "plan"
    dhf_owner: "system"
    applies_to:
      - "Clinical Evaluation Plan"
      - "Clinical Evaluation Report"
      - "Post-Market Clinical Follow-up Plan"
    regulatory_grounding:
      - "OBL-13485-007"
    verbatim: |
      "Establish the process for planning and conducting Clinical
      Evaluation of MedTech Company medical devices to demonstrate safety,
      clinical performance, and clinical benefit — per EU MDR 2017/745
      Art. 61 and Annex XIV, informed by MDCG 2020-6 and MDCG 2020-13.
      Where clinical investigation is conducted, align with ISO 14155:2020
      and (for US) 21 CFR Part 812. Sources of clinical data: clinical
      investigations, scientific literature, clinical experience, and PMS."
    extracted_requirements:
      - "Author a Clinical Evaluation Plan per GL-TMP-UC-004 covering scope, methodology, and acceptance criteria."
      - "Conduct systematic literature search and appraisal."
      - "Author a Clinical Evaluation Report per GL-TMP-UC-005 with clinical-data appraisal and benefit-risk conclusion."
      - "Maintain a Post-Market Clinical Follow-up plan; feed PMCF data back into CER updates."
      - "Update CER at defined cadences (typically annually for novel devices, every 2–5 years for stable devices)."
    context: |
      Clinical evidence is the second leg of the regulatory submission
      (alongside non-clinical V&V). The CEP/CER are MDR-mandatory
      artifacts; for US 510(k) the level of clinical evidence is pathway-
      and risk-class dependent.
-->

---

## GL-SOP-DC-004 — Design Outputs (Labeling Extension)

_1 QMS obligation covering labeling-IFU outputs._

| ID | Section | Topic | Applies To | Regulatory Grounding |
|----|---------|-------|-----------|----------------------|
| <a id="qms-lbl-001"></a>[`QMS-LBL-001` · Labeling and IFU Outputs](#qms-lbl-001) — Author IFU as a Design Output; route through GL-SOP-DC-005 design review. | GL-SOP-DC-004 §6 (Labeling) — Design Outputs | `labeling-ifu` | Instructions for Use (IFU); Package label; UDI carrier and database submission; AI-disclosure labeling (if AI-enabled); Translations per market | [`OBL-AI-LIFE-002` · AI Device Labeling](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-ai-lifecycle.md#OBL-AI-LIFE-002) — IFU must state that AI is included and describe its role in the device; [`OBL-82304-007` · Post-Market Problem Resolution](../../../.claude/skills/dhf-manifest/data/standards/iec-82304.md#OBL-82304-007) — IFU / user documentation must explicitly state: intended use, intended operating environment (hardware, OS, network requirements) |

<!-- QMS-DATA
records:
  - id: "QMS-LBL-001"
    title: "Labeling and IFU Outputs"
    source: "GL-SOP-DC-004 §6 (Labeling)"
    source_title: "Design Outputs"
    topic: "labeling-ifu"
    artifact_type: "labeling"
    dhf_owner: "system"
    applies_to:
      - "Instructions for Use (IFU)"
      - "Package label"
      - "UDI carrier and database submission"
      - "AI-disclosure labeling (if AI-enabled)"
      - "Translations per market"
    regulatory_grounding:
      - "OBL-AI-LIFE-002"
      - "OBL-82304-007"
    verbatim: |
      "Labeling — including IFU, package label, UDI, and any
      accompanying training materials — is a Design Output (per
      GL-SOP-DC-004) and shall be approved before V&V validation
      activities depending on labeling content. For AI/ML-enabled
      devices, IFU shall disclose: that the device uses AI/ML, the
      device's performance metrics with confidence intervals from the
      validation study, the demographic breakdown of training and test
      datasets, and which patient types are at the boundary of the
      validated use."
    extracted_requirements:
      - "Author IFU as a Design Output; route through GL-SOP-DC-005 design review."
      - "Validate labeling content via summative usability (per GL-SOP-UC-001)."
      - "Maintain UDI per 21 CFR 830 / EU MDR Article 27 and submit to FDA GUDID / Eudamed."
      - "For AI/ML devices: include AI disclosure, validation performance metrics with CIs, and training-data demographics."
      - "Maintain market-specific translations of IFU per regulation (EU MDR Annex I §23, FDA 21 CFR 801)."
      - "Update labeling on every change that affects use; route changes through GL-SOP-DC-008."
    context: |
      Labeling is currently distributed across GL-SOP-DC-004 (as a
      design output) and GL-SOP-PM-001 (post-market labeling updates).
      Task ben/026 considers whether labeling deserves its own dedicated
      SOP / WI under a future expansion. Until then this record grounds
      to the design-outputs SOP for the labeling content path.
-->


