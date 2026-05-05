# Tier 1 Regulatory Distillation — FDA Device Software Functions (Premarket Submissions)

**Guidance**: Content of Premarket Submissions for Device Software Functions
**Date**: June 14, 2023 (Final)
**Topic coverage**: regulatory-submission, software-lifecycle, verification, validation
**Distillation date**: 2026-04-21
**Source references**:
- `.claude/skills/medtech-docs/references/fda-guidance/sw-functions-distilled.md`

> **Note**: FDA guidance is nonbinding. Obligations represent FDA's stated expectations for premarket submissions.

---

<a id="OBL-SWF-001"></a>

```yaml
id: OBL-SWF-001
title: "Software Documentation Level"
source: FDA SW Functions Guidance (2023) §IV Documentation Levels
section: "Enhanced vs. Basic Documentation Level"
scope_flags: [510k, common-baseline]
topic: regulatory-submission
artifact_type: submission-content
dhf_owner: system
min_iec62304_class: A
canonical_role: submission-authored
criticality: must-have
applies_to:
  - role: submission-authored
    file_pattern: "*510k-submission*.md"
  - role: plans-doc-level
    file_pattern: "*documentation-level-statement*.md"
verbatim: "Enhanced documentation required when failure or latent flaw of ANY device software function could present a hazardous situation with a probable risk of death or serious injury to a patient, user, or others, assessed prior to implementing risk control measures. The documentation level reflects the device as a whole — if any software function's failure could cause death/serious injury, enhanced documentation applies to the entire submission."
extracted_requirements:
  - Determine documentation level (Basic or Enhanced) based on risk assessment — assessed BEFORE risk control measures
  - If ANY software function failure could cause death or serious injury pre-risk-controls → Enhanced documentation required for the entire submission
  - For MedTech Project: Intra-Op failure during surgery (e.g., corrupted guidance data) could cause serious injury → Enhanced documentation applies to the whole submission
  - Provide a written documentation level statement with rationale leveraging risk assessment and intended use
  - Class II is NOT automatically Basic — sponsor determines level based on risk assessment
```

**Context**: MedTech Project requires Enhanced documentation because Intra-Op guidance software, if it fails, could cause serious patient injury (wrong surgical positioning, incorrect implant sizing, etc.) assessed before risk controls. This applies to the entire 510(k) submission, even the Management Services documentation. The documentation level statement must explicitly call out this rationale and reference the risk assessment.

---

<a id="OBL-SWF-002"></a>

```yaml
id: OBL-SWF-002
title: "SW Submission Documentation"
source: FDA SW Functions Guidance (2023) §V Required Documentation Elements
section: "Software Description + SRS + Architecture"
scope_flags: [510k, common-baseline]
topic: regulatory-submission
artifact_type: submission-content
dhf_owner: system
min_iec62304_class: A
canonical_role: submission-authored
criticality: must-have
applies_to:
  - role: submission-authored
    file_pattern: "*510k-submission*.md"
  - role: requirements
    file_pattern: "*software-requirements-specification*.md"
  - role: architecture
    file_pattern: "*software-architecture-document*.md"
verbatim: "Comprehensive overview: significant features, analyses, inputs, outputs, hardware platforms. Software requirements specification — complete documentation of software requirements, organized format with traceability to other documentation elements. System and software architecture diagram — detailed diagrams of modules, layers, interfaces, data inputs/outputs/flow, user/external product interactions."
extracted_requirements:
  - Include a Software Description: overview of significant features, inputs, outputs, hardware platforms
  - For modified devices: description of changes from previous submission
  - Include a complete Software Requirements Specification (SRS) — must cover all requirements with traceability
  - Highlight safety-critical requirements and requirements modified since prior clearance (if applicable)
  - Include system and software architecture diagrams showing: modules, layers, interfaces, data flow, external interactions (IT infrastructure, imaging devices, PACS, tablet)
  - Architecture diagrams must show how all modules/functions interact including shared resources
```

**Context**: For MedTech Project, the software description and architecture diagram must cover all three modules (Pre-Op, Intra-Op, Management Services) and their interactions. The architecture must show: how Pre-Op generates a plan, how the plan is transmitted to Intra-Op, how Intra-Op receives DICOM data from the C-arm, and how Management Services supports both SaMD modules. The SRS covers all three modules — each item DHF has its item-level SRS that feeds the system SRS.

---

<a id="OBL-SWF-003"></a>

```yaml
id: OBL-SWF-003
title: "SW Design Documentation"
source: FDA SW Functions Guidance (2023) §V Required Documentation Elements
section: "Software Design Specification (Enhanced)"
scope_flags: [510k, common-baseline]
topic: design-outputs
artifact_type: submission-content
dhf_owner: both
min_iec62304_class: A
canonical_role: architecture
criticality: must-have
applies_to:
  - role: submission-authored
    file_pattern: "*510k-submission*.md"
  - role: design
    file_pattern: "*software-design-document*.md"
verbatim: "Enhanced: Include SDS showing technical design details, how design implements SRS, and traceability from SDS to SRS. Basic: Not required in submission (document in Design History File)."
extracted_requirements:
  - For Enhanced documentation (MedTech Project): include Software Design Specification in the submission
  - SDS must show: technical design details, how the design implements the SRS requirements, traceability from SDS to SRS
  - SDS traceability links design decisions to requirements — bidirectional trace required
  - For Basic documentation only: SDS stays in DHF, not submitted
```

**Context**: Because MedTech Project is Enhanced, the SDS goes into the 510(k) submission. This is a significant documentation effort — the SDS for Pre-Op and Intra-Op must show how the AI algorithms, surgical measurement logic, image processing pipelines, and device communication protocols are designed to meet each SRS requirement. Plan for SDS authorship as a significant Phase 2 deliverable.

---

<a id="OBL-SWF-004"></a>

```yaml
id: OBL-SWF-004
title: "SW Lifecycle Documentation"
source: FDA SW Functions Guidance (2023) §V Required Documentation Elements
section: "Software Development, CM, and Maintenance (IEC 62304)"
scope_flags: [510k, common-baseline]
topic: software-lifecycle
artifact_type: submission-content
dhf_owner: both
min_iec62304_class: A
canonical_role: submission-authored
criticality: must-have
applies_to:
  - role: submission-authored
    file_pattern: "*510k-submission*.md"
  - role: submission-authored
    file_pattern: "*iec-62304-declaration-of-conformity*.md"
verbatim: "Option 1: Declaration of Conformity to FDA-recognized IEC 62304 (specific sections for basic vs. enhanced). Option 2 Without IEC 62304 conformity (Enhanced): Complete configuration management and maintenance plan + summary documentation."
extracted_requirements:
  - Option 1 (preferred): Submit a Declaration of Conformity to IEC 62304 — this substitutes for the SW development practices documentation section
  - For Enhanced: IEC 62304 conformance for Class C activities is required for the DoC to be accepted
  - If not using IEC 62304 DoC (Option 2, Enhanced): submit complete CM plan + full SW development summary
  - The DoC must reference the specific IEC 62304 edition and list the applicable clauses
```

**Context**: MedTech Project should pursue an IEC 62304 Declaration of Conformity (Option 1) — it simplifies submission documentation and aligns with the project's planned IEC 62304 conformance. Since Pre-Op and Intra-Op are IEC 62304 Class C, the DoC must cover the full Class C requirements. This is why the IEC 62304 compliance records in the item DHFs are submission artifacts, not just internal records.

---

<a id="OBL-SWF-005"></a>

```yaml
id: OBL-SWF-005
title: "SW Testing Documentation"
source: FDA SW Functions Guidance (2023) §V Required Documentation Elements
section: "Software Testing (V&V)"
scope_flags: [510k, common-baseline]
topic: verification
artifact_type: submission-content
dhf_owner: both
min_iec62304_class: A
canonical_role: vnv
criticality: must-have
applies_to:
  - role: submission-authored
    file_pattern: "*510k-submission*.md"
  - role: vnv
    file_pattern: "*test-protocols-and-reports*.md"
verbatim: "Enhanced: Summary of unit, integration, and system-level testing + complete system-level test protocols and reports + full unit and integration level test protocols and reports. Basic: Summary of unit, integration, and system-level testing + complete system-level test protocols and reports only."
extracted_requirements:
  - For Enhanced documentation (MedTech Project): submit complete test protocols and reports at unit, integration, AND system levels
  - System-level test protocols and reports: required for both Basic and Enhanced
  - Unit and integration test protocols/reports: full submission required for Enhanced (not just summary)
  - Reference performance testing material across submission sections to reduce duplication
  - AI performance testing (algorithm validation studies) is part of the submission testing section
```

**Context**: MedTech Project's Enhanced documentation requirement means full test protocols and reports at all levels go into the 510(k). This is a significant documentation burden — unit tests for AI model components, integration tests for the Pre-Op/Intra-Op plan handoff, and system-level tests including usability and clinical performance. Plan for the test documentation as a parallel effort with software development.

---

<a id="OBL-SWF-006"></a>

```yaml
id: OBL-SWF-006
title: "Unresolved Anomalies List"
source: FDA SW Functions Guidance (2023) §V Required Documentation Elements
section: "Software Version History + Unresolved Anomalies"
scope_flags: [510k, common-baseline]
topic: software-lifecycle
artifact_type: submission-content
dhf_owner: both
min_iec62304_class: A
canonical_role: submission-authored
criticality: must-have
applies_to:
  - role: submission-authored
    file_pattern: "*510k-submission*.md"
  - role: submission-authored
    file_pattern: "*unresolved-anomalies-list*.md"
verbatim: "History of tested software revisions: date, version number, brief description of changes. Last entry = final released version, including differences from tested version and safety/effectiveness assessment. List of remaining unresolved anomalies in tabular format. For each: description, how discovered, root cause, impact on safety/effectiveness, outcome of evaluation, risk-based rationale for not fixing."
extracted_requirements:
  - Include software version history from first version under design controls to the final released version
  - Last entry must document any differences between the tested version and the commercially released version with safety/effectiveness assessment
  - Include a complete list of known unresolved anomalies (bugs/defects not fixed at release)
  - For each unresolved anomaly: describe the defect, discovery method, root cause, safety/effectiveness impact, and risk-based rationale for why it was not fixed
  - No unresolved anomaly with patient safety impact can be left unjustified
```

**Context**: The unresolved anomalies list is an important pre-market transparency artifact. For MedTech Project, any known software defect that is being shipped with the initial release must be documented and justified. This drives the practice of risk-based anomaly classification during development — anomalies that could affect patient safety must be fixed before release; cosmetic/minor anomalies may be deferred with documentation.
