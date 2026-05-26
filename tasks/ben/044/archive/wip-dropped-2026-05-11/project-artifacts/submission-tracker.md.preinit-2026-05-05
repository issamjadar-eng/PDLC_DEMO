# PP3500 510(k) + PCCP — Submission Package Tracker

**Filing**: K210345 (demo) — PainEase PCA Advanced (PP3500)
**Lead DHF**: `pca-device`
**Additional DHFs pulled**: `connectivity-adapter` (cyber only), `cloud-suite/dhfs/drug-library-manager` (bundled accessory — posture TBD)
**Status**: First-stab populated tracker (`/tracker build` output, task 013)
**Last updated**: 2026-04-14

> **Do not hand-edit the HTML dashboard.** Edit this markdown, then run `/tracker render`.
> **Before editing this file**, load `.claude/skills/tracker/SKILL.md` — it defines the column conventions, valid values, and the Context & Sources that inform every row.

## Context & Sources

### 1. Composition Manifest (source of truth for what's included)
- `docs/project/submissions/510k/composition-manifest.md` — PP3500 510(k) filing composition

### 2. Project Manifest — DHFs in this filing
| DHF | Role in filing | Path |
|---|---|---|
| `pca-device` | Lead DHF (full) | `docs/project/dhfs/pca-device/` |
| `connectivity-adapter` | Cybersecurity posture only (MDDS) | `docs/project/dhfs/connectivity-adapter/` |
| `cloud-suite/dhfs/drug-library-manager` | Bundled accessory (Class II SaMD) — TBD | `docs/project/dhfs/cloud-suite/dhfs/drug-library-manager/` |

### 3. System SADs (drive Scope and per-module splits)
- `docs/project/dhfs/pca-device/design-controls/architecture/pca-device-system-sad.md` — 7 modules (M1–M7)
- `docs/project/dhfs/connectivity-adapter/design-controls/architecture/connectivity-adapter-system-sad.md` — 7 modules (A1–A7)
- `docs/project/dhfs/cloud-suite/dhfs/drug-library-manager/design-controls/architecture/drug-library-manager-system-sad.md` — 7 modules (D1–D7)

### 4. Regulatory Strategy
- `docs/project/strategies/regulatory-strategy.md` — shared; Filing Scope (PCA alone), Critical-Requirement Carve-out, Component Classification & Filing Posture, DHF Filing Composition Pattern

### 5. Submission Tracker Task
- `tasks/ben/013-tracker-prerequisites.md` — scaffold origin
- `tasks/ben/006-architecture-regulatory-strategy.md` — strategy source task

### 6. FDA Guidance Documents (shared)
- `docs/external/fda-guidance/510k-se.md`, `sw-functions.md`, `sw-changes.md`, `cybersecurity.md`, `pccp-general.md`, `pccp-aiml.md`, `ai-dsf-lifecycle.md`, `cds.md`, `mfd.md`, `qsub.md`

## Two-Level Deliverable Model

Deliverables are tracked at two levels where the architecture demands it:
- **Device-level** items apply across the whole filing.
- **Per-Module** items split into one row per component with letter suffixes:
  - **a** = pca-device
  - **b** = drug-library-manager
  - **c** = connectivity-adapter (cyber-only evidence)

## Status Legend

| Status | Meaning |
|---|---|
| **Not Started** | No work product exists |
| **Partial** | Legacy or fragmentary content exists |
| **In Progress** | Actively being authored |
| **Done** | Substantially complete |

## Effort Scale

| Effort | Definition |
|---|---|
| **Low** | < 1 engineer-week |
| **Med** | 1–3 engineer-weeks |
| **High** | 3–8 engineer-weeks |
| **V.High** | > 8 engineer-weeks |

## Phase Scale

| Phase | Meaning |
|---|---|
| **Filing** | Must reach filing quality by K210345 submission |
| **Filing (proto)** | Prototype-quality at filing; full by Release 1 |
| **Release 1** | First commercial release |
| **Release 2** | Planned post-launch (includes AI/ML PCCP envelope) |
| **Release 3** | Further PCCP envelope expansion |

## Part 1 — Base 510(k) Requirements

### 1.1 Administrative & Cover

| # | Deliverable | Scope | Effort | Phase | FDA Reference | Project Location | Status | Evidence |
|---|---|---|---|---|---|---|---|---|
| A1 | Cover Letter | Device | Low | Filing | 21 CFR 807.87 | `docs/project/submissions/510k/cover-letter.md` | Not Started | — |
| A2 | 510(k) Summary / Statement | Device | Med | Filing | 21 CFR 807.92 | `docs/project/submissions/510k/510k-summary.md` | Not Started | — |
| A3 | Indications for Use (FDA Form 3881) | Device | Low | Filing | 21 CFR 807.87(e) | `docs/project/submissions/510k/indications-for-use.md` | Not Started | — |
| A4 | Truthful and Accurate Statement | Device | Low | Filing | 21 CFR 807.87(k) | `docs/project/submissions/510k/truthful-accurate.md` | Not Started | — |
| A5 | User Fee Cover Sheet (Form 3601) | Device | Low | Filing | FDASIA | `docs/project/submissions/510k/user-fee.md` | Not Started | — |
| A6 | Submission Table of Contents | Device | Low | Filing | eCopy | `docs/project/submissions/510k/toc.md` | Not Started | — |
| A9 | MFD Submission Summary | Device | Low | Filing | MFD §IV | `docs/project/submissions/510k/mfd-summary.md` | Not Started | PCA + DLM + Adapter cyber |

### 1.2 Device Description & Intended Use

| # | Deliverable | Scope | Effort | Phase | FDA Reference | Project Location | Status | Evidence |
|---|---|---|---|---|---|---|---|---|
| DD1 | Device Description Document | Device | Med | Filing | 21 CFR 807.92(a)(4) | `docs/project/dhfs/pca-device/design-controls/device-description.md` | Not Started | — |
| DD2 | Device Block Diagram | Device | Low | Filing | sw-functions §V.A | `docs/project/dhfs/pca-device/design-controls/architecture/block-diagram.md` | Partial | Context diagram in pca-device SAD §2 |

### 1.3 Predicate Comparison & Substantial Equivalence

| # | Deliverable | Scope | Effort | Phase | FDA Reference | Project Location | Status | Evidence |
|---|---|---|---|---|---|---|---|---|
| PR1 | Predicate Device Comparison Table | Device | Med | Filing | 510(k) SE §V | `docs/project/submissions/510k/predicate-comparison.md` | Partial | PP3000 context in `docs/project/input-analysis/predicate-analysis/` |
| PR2 | Substantial Equivalence Discussion | Device | Med | Filing | 510(k) SE §VI | `docs/project/submissions/510k/se-discussion.md` | Not Started | — |

### 1.4 Software Documentation (Enhanced Level)

| # | Deliverable | Scope | Effort | Phase | FDA Reference | Project Location | Status | Evidence |
|---|---|---|---|---|---|---|---|---|
| SW1 | Software Documentation Level Statement | Device | Low | Filing | sw-functions §IV | `docs/project/dhfs/pca-device/design-controls/software/doc-level-statement.md` | Not Started | Enhanced expected (Class C) |
| SW2a | SRS — PCA Device | Per-Module | High | Filing | sw-functions §V.B; IEC 62304 §5.2 | `docs/project/dhfs/pca-device/design-controls/requirements/srs.md` | Not Started | Modules in SAD §4 |
| SW2b | SRS — Drug Library Manager | Per-Module | High | Filing | sw-functions §V.B; IEC 62304 §5.2 | `docs/project/dhfs/cloud-suite/dhfs/drug-library-manager/design-controls/requirements/srs.md` | Not Started | Modules in DLM SAD §4 |
| SW3a | System & Software Architecture — PCA Device | Per-Module | Med | Filing | sw-functions §V.C; IEC 62304 §5.3 | `docs/project/dhfs/pca-device/design-controls/architecture/pca-device-system-sad.md` | Partial | First-stab SAD drafted (task 013) |
| SW3b | System & Software Architecture — DLM | Per-Module | Med | Filing | sw-functions §V.C; IEC 62304 §5.3 | `docs/project/dhfs/cloud-suite/dhfs/drug-library-manager/design-controls/architecture/drug-library-manager-system-sad.md` | Partial | First-stab SAD drafted (task 013) |
| SW4a | Software Design Specification — PCA Device | Per-Module | V.High | Filing | sw-functions §V.D; IEC 62304 §5.4 | `docs/project/dhfs/pca-device/design-controls/design-outputs/sds.md` | Not Started | Enhanced doc level |
| SW4b | Software Design Specification — DLM | Per-Module | High | Filing | sw-functions §V.D; IEC 62304 §5.4 | `docs/project/dhfs/cloud-suite/dhfs/drug-library-manager/design-controls/design-outputs/sds.md` | Not Started | — |
| SW5a | Unit & Integration Tests — PCA Device | Per-Module | V.High | Filing | sw-functions §V.E; IEC 62304 §5.6 | `docs/project/dhfs/pca-device/design-controls/verification-validation/unit-integration/` | Not Started | — |
| SW5b | Unit & Integration Tests — DLM | Per-Module | High | Filing | sw-functions §V.E; IEC 62304 §5.6 | `docs/project/dhfs/cloud-suite/dhfs/drug-library-manager/design-controls/verification-validation/unit-integration/` | Not Started | — |
| SW6a | System-Level Test Protocols & Reports — PCA Device | Per-Module | V.High | Filing | sw-functions §V.F | `docs/project/dhfs/pca-device/design-controls/verification-validation/system-test/` | Not Started | — |
| SW6b | System-Level Test Protocols & Reports — DLM | Per-Module | High | Filing | sw-functions §V.F | `docs/project/dhfs/cloud-suite/dhfs/drug-library-manager/design-controls/verification-validation/system-test/` | Not Started | — |
| SW7 | Software Development Plan / IEC 62304 DoC | Device | Med | Filing | IEC 62304 §5.1 | `docs/project/dhfs/pca-device/design-controls/plans/sdp.md` | Not Started | — |
| SW8 | Configuration Management Plan | Device | Med | Filing | IEC 62304 §8 | `docs/project/dhfs/pca-device/design-controls/plans/cm-plan.md` | Not Started | — |
| SW9a | Software Version History — PCA Device | Per-Module | Low | Filing | sw-functions §V.G | `docs/project/dhfs/pca-device/design-controls/software/version-history.md` | Not Started | — |
| SW9b | Software Version History — DLM | Per-Module | Low | Filing | sw-functions §V.G | `docs/project/dhfs/cloud-suite/dhfs/drug-library-manager/design-controls/software/version-history.md` | Not Started | — |
| SW10a | Unresolved Anomalies — PCA Device | Per-Module | Low | Filing | sw-functions §V.H | `docs/project/dhfs/pca-device/design-controls/software/anomalies.md` | Not Started | — |
| SW10b | Unresolved Anomalies — DLM | Per-Module | Low | Filing | sw-functions §V.H | `docs/project/dhfs/cloud-suite/dhfs/drug-library-manager/design-controls/software/anomalies.md` | Not Started | — |
| SW11 | SOUP / OTS Software List | Device | Med | Filing | IEC 62304 §8.1.2 | `docs/project/dhfs/pca-device/design-controls/software/soup-list.md` | Not Started | RTOS + crypto (M7) |
| SW12 | Traceability Matrix (UN↔DI↔SRS↔V&V) | Device | High | Filing | 21 CFR 820.30 | `docs/project/dhfs/pca-device/design-controls/trace-matrix.md` | Not Started | Filing Scope column per Ct* carve-out |

### 1.5 Risk Management

| # | Deliverable | Scope | Effort | Phase | FDA Reference | Project Location | Status | Evidence |
|---|---|---|---|---|---|---|---|---|
| RM1 | Risk Management Plan | Device | Med | Filing | ISO 14971 §4.4 | `docs/project/dhfs/pca-device/risk-management/risk-mgmt-plan.md` | Not Started | — |
| RM2a | Preliminary Hazard Analysis — PCA Device | Per-Module | High | Filing | ISO 14971 §5 | `docs/project/dhfs/pca-device/risk-management/pha.md` | Not Started | Hazard chains owned by M2 |
| RM2b | Preliminary Hazard Analysis — DLM | Per-Module | Med | Filing | ISO 14971 §5 | `docs/project/dhfs/cloud-suite/dhfs/drug-library-manager/risk-management/pha.md` | Not Started | — |
| RM3a | Software FMEA — PCA Device | Per-Module | High | Filing | ISO 14971; IEC 62304 §7 | `docs/project/dhfs/pca-device/risk-management/fmea.md` | Not Started | — |
| RM3b | Software FMEA — DLM | Per-Module | Med | Filing | ISO 14971; IEC 62304 §7 | `docs/project/dhfs/cloud-suite/dhfs/drug-library-manager/risk-management/fmea.md` | Not Started | — |
| RM4 | Risk Management Report | Device | Med | Filing | ISO 14971 §8 | `docs/project/dhfs/pca-device/risk-management/risk-mgmt-report.md` | Not Started | — |
| RM5 | Benefit-Risk Analysis | Device | Med | Filing | ISO 14971 §7 | `docs/project/dhfs/pca-device/risk-management/benefit-risk.md` | Not Started | — |
| RM6 | Multi-Function Hazard Impact Assessment | Device | Med | Filing | MFD §V | `docs/project/dhfs/pca-device/risk-management/mfd-impact.md` | Not Started | PCA × DLM × Adapter interaction |

### 1.6 Performance Testing & Clinical Data

| # | Deliverable | Scope | Effort | Phase | FDA Reference | Project Location | Status | Evidence |
|---|---|---|---|---|---|---|---|---|
| CL1 | Clinical Evaluation Summary | Device | High | Filing | 510(k) SE §VII | `docs/project/dhfs/pca-device/clinical/clinical-evaluation.md` | Partial | Clinical corpus in `dhfs/pca-device/clinical/` |
| CL2 | Bench Performance Data Summary | Device | High | Filing | 510(k) SE §VII | `docs/project/dhfs/pca-device/design-controls/verification-validation/bench-performance.md` | Not Started | Flow accuracy, occlusion, air-in-line |
| CL3 | Animal Performance Data | Device | Med | Release 1 | 510(k) SE §VII | `docs/project/dhfs/pca-device/clinical/animal-data.md` | Not Started | Likely not required |

### 1.7 Labeling

| # | Deliverable | Scope | Effort | Phase | FDA Reference | Project Location | Status | Evidence |
|---|---|---|---|---|---|---|---|---|
| LB1 | Proposed Device Labeling / IFU | Device | Med | Filing | 21 CFR 801 | `docs/project/dhfs/pca-device/design-controls/labeling/ifu.md` | Not Started | — |
| LB2 | Directions for Use | Device | Med | Filing | 21 CFR 801.5 | `docs/project/dhfs/pca-device/design-controls/labeling/dfu.md` | Not Started | — |
| LB3 | Hazard / Warnings Labeling | Device | Low | Filing | 21 CFR 801.15 | `docs/project/dhfs/pca-device/design-controls/labeling/warnings.md` | Not Started | — |

### 1.8 Cybersecurity

| # | Deliverable | Scope | Effort | Phase | FDA Reference | Project Location | Status | Evidence |
|---|---|---|---|---|---|---|---|---|
| CY1 | Cybersecurity Management Plan | Device | Med | Filing | FDA Cyber 2023 §V; §524B | `docs/project/dhfs/pca-device/cybersecurity/cyber-mgmt-plan.md` | Not Started | — |
| CY2a | Threat Model — PCA Device | Per-Module | High | Filing | FDA Cyber 2023 §VI.A | `docs/project/dhfs/pca-device/cybersecurity/threat-model.md` | Not Started | — |
| CY2b | Threat Model — DLM | Per-Module | High | Filing | FDA Cyber 2023 §VI.A | `docs/project/dhfs/cloud-suite/dhfs/drug-library-manager/cybersecurity/threat-model.md` | Not Started | — |
| CY2c | Threat Model — Connectivity Adapter | Per-Module | High | Filing | FDA Cyber 2023 §VI.A | `docs/project/dhfs/connectivity-adapter/cybersecurity/threat-model.md` | Not Started | Pulled via composition manifest §3.2 |
| CY3a | Cyber Risk Assessment — PCA Device | Per-Module | Med | Filing | FDA Cyber 2023 §VI.B | `docs/project/dhfs/pca-device/cybersecurity/cyber-risk-assessment.md` | Not Started | Exploitability-based |
| CY3b | Cyber Risk Assessment — DLM | Per-Module | Med | Filing | FDA Cyber 2023 §VI.B | `docs/project/dhfs/cloud-suite/dhfs/drug-library-manager/cybersecurity/cyber-risk-assessment.md` | Not Started | — |
| CY3c | Cyber Risk Assessment — Connectivity Adapter | Per-Module | Med | Filing | FDA Cyber 2023 §VI.B | `docs/project/dhfs/connectivity-adapter/cybersecurity/cyber-risk-assessment.md` | Not Started | — |
| CY4a | SBOM — PCA Device | Per-Module | Med | Filing | FDA Cyber 2023 §VII; NTIA | `docs/project/dhfs/pca-device/cybersecurity/sbom.md` | Not Started | — |
| CY4b | SBOM — DLM | Per-Module | Med | Filing | FDA Cyber 2023 §VII; NTIA | `docs/project/dhfs/cloud-suite/dhfs/drug-library-manager/cybersecurity/sbom.md` | Not Started | — |
| CY4c | SBOM — Connectivity Adapter | Per-Module | Med | Filing | FDA Cyber 2023 §VII; NTIA | `docs/project/dhfs/connectivity-adapter/cybersecurity/sbom.md` | Not Started | — |
| CY5 | Security Architecture Views (4 required) | Both | High | Filing | FDA Cyber 2023 §VI.C | `docs/project/dhfs/pca-device/cybersecurity/security-architecture.md` | Not Started | Global, multi-patient harm, updateability, use cases |
| CY6a | Third-Party Vuln Assessment — PCA Device | Per-Module | Med | Filing | FDA Cyber 2023 §VII.B | `docs/project/dhfs/pca-device/cybersecurity/third-party-assessment.md` | Not Started | — |
| CY6b | Third-Party Vuln Assessment — DLM | Per-Module | Med | Filing | FDA Cyber 2023 §VII.B | `docs/project/dhfs/cloud-suite/dhfs/drug-library-manager/cybersecurity/third-party-assessment.md` | Not Started | — |
| CY6c | Third-Party Vuln Assessment — Adapter | Per-Module | Med | Filing | FDA Cyber 2023 §VII.B | `docs/project/dhfs/connectivity-adapter/cybersecurity/third-party-assessment.md` | Not Started | — |
| CY7a | Cybersecurity Testing — PCA Device | Per-Module | V.High | Filing | FDA Cyber 2023 §VIII | `docs/project/dhfs/pca-device/cybersecurity/test-results.md` | Not Started | Req + threat + vuln + pen test |
| CY7b | Cybersecurity Testing — DLM | Per-Module | High | Filing | FDA Cyber 2023 §VIII | `docs/project/dhfs/cloud-suite/dhfs/drug-library-manager/cybersecurity/test-results.md` | Not Started | — |
| CY7c | Cybersecurity Testing — Connectivity Adapter | Per-Module | High | Filing | FDA Cyber 2023 §VIII | `docs/project/dhfs/connectivity-adapter/cybersecurity/test-results.md` | Not Started | — |
| CY8 | Vulnerability & Patch Management Plan | Device | Med | Filing | FDA Cyber 2023 §IX; §524B | `docs/project/dhfs/pca-device/cybersecurity/vuln-patch-plan.md` | Not Started | — |
| CY9 | Coordinated Disclosure Policy | Device | Low | Filing | §524B(b)(2) | `docs/project/dhfs/pca-device/cybersecurity/disclosure-policy.md` | Not Started | — |
| CY10 | Cybersecurity Labeling | Device | Low | Filing | FDA Cyber 2023 §X | `docs/project/dhfs/pca-device/design-controls/labeling/cyber-labeling.md` | Not Started | — |
| CY11 | Interoperability Considerations | Device | Med | Filing | FDA Cyber 2023 §VI.D | `docs/project/dhfs/pca-device/cybersecurity/interoperability.md` | Not Started | HL7/FHIR via Adapter |

### 1.9 Human Factors & Usability

| # | Deliverable | Scope | Effort | Phase | FDA Reference | Project Location | Status | Evidence |
|---|---|---|---|---|---|---|---|---|
| HF1 | Usability Engineering Plan | Device | Med | Filing | IEC 62366-1 §5.1 | `docs/project/dhfs/pca-device/design-controls/usability/ue-plan.md` | Not Started | — |
| HF2a | Use Specification — PCA Device | Per-Module | Med | Filing | IEC 62366-1 §5.1 | `docs/project/dhfs/pca-device/design-controls/usability/use-specification.md` | Not Started | Clinician + patient (M4, M5) |
| HF2b | Use Specification — DLM | Per-Module | Low | Filing | IEC 62366-1 §5.1 | `docs/project/dhfs/cloud-suite/dhfs/drug-library-manager/design-controls/usability/use-specification.md` | Not Started | Pharmacist workflow (D1, D2) |
| HF3a | Task Analysis & Use-Related Risk — PCA Device | Per-Module | High | Filing | IEC 62366-1 §5.2 | `docs/project/dhfs/pca-device/design-controls/usability/task-analysis.md` | Not Started | — |
| HF3b | Task Analysis & Use-Related Risk — DLM | Per-Module | Med | Filing | IEC 62366-1 §5.2 | `docs/project/dhfs/cloud-suite/dhfs/drug-library-manager/design-controls/usability/task-analysis.md` | Not Started | — |
| HF4a | Summative Usability Study — PCA Device | Per-Module | V.High | Filing | IEC 62366-1 §5.9 | `docs/project/dhfs/pca-device/design-controls/usability/summative-study.md` | Not Started | — |
| HF4b | Summative Usability Study — DLM | Per-Module | High | Filing | IEC 62366-1 §5.9 | `docs/project/dhfs/cloud-suite/dhfs/drug-library-manager/design-controls/usability/summative-study.md` | Not Started | — |
| HF5 | Usability Engineering File Summary | Device | Med | Filing | IEC 62366-1 §5.10 | `docs/project/dhfs/pca-device/design-controls/usability/ue-file-summary.md` | Not Started | — |

### 1.10 Standards & Conformity

| # | Deliverable | Scope | Effort | Phase | FDA Reference | Project Location | Status | Evidence |
|---|---|---|---|---|---|---|---|---|
| ST1 | Standards Data Report / Declarations of Conformity | Device | Med | Filing | FDA recognized standards | `docs/project/submissions/510k/standards-conformity.md` | Not Started | 62304, 14971, 62366-1, 60601-1/-1-2/-1-8/-2-24 |

## Part 2 — PCCP Additive Requirements

### 2.1 PCCP Core Document

| # | Deliverable | Scope | Effort | Phase | FDA Reference | Project Location | Status | Evidence |
|---|---|---|---|---|---|---|---|---|
| PC1 | PCCP Cover Section | Device | Low | Filing | PCCP General §IV.A | `docs/project/dhfs/pca-device/design-controls/pccp/cover.md` | Not Started | — |
| PC2 | PCCP — Description of Modifications | Device | High | Filing | PCCP General §IV.B | `docs/project/dhfs/pca-device/design-controls/pccp/modifications.md` | Not Started | Drug library, firmware, future ML |
| PC3 | PCCP — Modification Protocol | Device | High | Filing | PCCP General §V | `docs/project/dhfs/pca-device/design-controls/pccp/protocol.md` | Not Started | V&V + acceptance criteria |
| PC4 | PCCP — Impact Assessment | Device | Med | Filing | PCCP General §VI | `docs/project/dhfs/pca-device/design-controls/pccp/impact-assessment.md` | Not Started | — |
| PC5 | PCCP Traceability Table | Device | Med | Filing | PCCP General §VII | `docs/project/dhfs/pca-device/design-controls/pccp/trace-table.md` | Not Started | — |
| PC6 | PCCP Public Summary | Device | Low | Filing | PCCP General §VIII | `docs/project/dhfs/pca-device/design-controls/pccp/public-summary.md` | Not Started | — |

### 2.4 PCCP Support Documentation

| # | Deliverable | Scope | Effort | Phase | FDA Reference | Project Location | Status | Evidence |
|---|---|---|---|---|---|---|---|---|
| PS1 | Drug Library Update Protocol | Device | High | Filing | PCCP General §V | `docs/project/dhfs/pca-device/design-controls/pccp/drug-lib-protocol.md` | Not Started | Primary PCCP change envelope |
| PS2 | Drug Library V&V Plan | Device | Med | Filing | PCCP General §V.B | `docs/project/dhfs/pca-device/design-controls/pccp/drug-lib-vv.md` | Not Started | — |
| PS3 | Drug Library Acceptance Criteria | Device | Med | Filing | PCCP General §V.C | `docs/project/dhfs/pca-device/design-controls/pccp/drug-lib-acceptance.md` | Not Started | — |
| PS4 | Firmware Update Protocol | Device | Med | Filing | PCCP General §V | `docs/project/dhfs/pca-device/design-controls/pccp/firmware-protocol.md` | Not Started | Signed update, quiescent boot |
| PS5 | Firmware Update V&V Plan | Device | Med | Filing | PCCP General §V.B | `docs/project/dhfs/pca-device/design-controls/pccp/firmware-vv.md` | Not Started | — |

### 2.5 AI/ML-Specific Documentation (PCCP-Driven)

| # | Deliverable | Scope | Effort | Phase | FDA Reference | Project Location | Status | Evidence |
|---|---|---|---|---|---|---|---|---|
| AI1 | AI-DSF Description of Modifications | Device | Med | Release 2 | PCCP AI/ML §IV | `docs/project/dhfs/pca-device/design-controls/pccp/aiml-modifications.md` | Not Started | Predictive alarms slot |
| AI2 | AI Re-Training Practices Protocol | Device | Med | Release 2 | PCCP AI/ML §V.A | `docs/project/dhfs/pca-device/design-controls/pccp/aiml-retraining.md` | Not Started | — |
| AI3 | AI Data Management Practices | Device | Med | Release 2 | PCCP AI/ML §V.B | `docs/project/dhfs/pca-device/design-controls/pccp/aiml-data-mgmt.md` | Not Started | — |
| AI4 | AI Performance Evaluation Plan | Device | High | Release 2 | PCCP AI/ML §V.C | `docs/project/dhfs/pca-device/design-controls/pccp/aiml-performance.md` | Not Started | Subgroup analysis |
| AI5 | AI Update Procedures & User Communication | Device | Med | Release 2 | PCCP AI/ML §V.D | `docs/project/dhfs/pca-device/design-controls/pccp/aiml-update.md` | Not Started | — |
| AI6 | AI Drift Monitoring Plan | Device | Med | Release 2 | PCCP AI/ML §V.E; AI-DSF | `docs/project/dhfs/pca-device/design-controls/pccp/aiml-drift.md` | Not Started | — |

## Part 3 — Management Services (Non-Submission)

### 3.1 Management Services (Non-Submission)

| # | Deliverable | Scope | Effort | Phase | FDA Reference | Project Location | Status | Evidence |
|---|---|---|---|---|---|---|---|---|
| MS1 | Adapter MDDS Classification Record | Device | Low | Filing | 21 CFR 880.6310; MFD | `docs/project/dhfs/connectivity-adapter/design-controls/classification-record.md` | Partial | Drafted in Adapter SAD §3–§4 |
| MS2 | Adapter QMS Evidence Summary | Device | Med | Filing | 21 CFR 820 | `docs/project/dhfs/connectivity-adapter/design-controls/qms-summary.md` | Not Started | — |
| MS3 | Adapter §524B Compliance Record | Device | Med | Filing | FD&C §524B | `docs/project/dhfs/connectivity-adapter/cybersecurity/524b-compliance.md` | Not Started | — |
| MS4 | Cloud Suite Non-Device Classification Records | Device | Med | Filing | MFD; sw-functions | `docs/project/dhfs/cloud-suite/classification-records.md` | Not Started | Fleet Mgmt, Analytics, Alerts, Inventory, Clinical Interface, Compliance Reports |
| MS5 | Adapter Interoperability Description (HL7/FHIR) | Device | Med | Filing | FDA interop guidance | `docs/project/dhfs/connectivity-adapter/design-controls/interoperability.md` | Partial | Drafted in Adapter SAD §2, §5 |
| MS6 | Adapter Cybersecurity Plan (referenced by PP3500) | Device | Med | Filing | FDA Cyber 2023 | `docs/project/dhfs/connectivity-adapter/cybersecurity/cyber-plan.md` | Not Started | Cross-ref target for CY-series |
| MS7 | Adapter SBOM (referenced by PP3500) | Device | Low | Filing | FDA Cyber 2023 §VII | `docs/project/dhfs/connectivity-adapter/cybersecurity/sbom.md` | Not Started | Same source as CY4c |

## Part 4 — Engineering Prerequisites

### 4.1 Requirements & Architecture

| # | Prerequisite | Scope | Effort | Phase | Status | Gates |
|---|---|---|---|---|---|---|
| ENG1 | Hardware Design Freeze (pump mechanism, sensors, enclosure) | Device | V.High | Filing | Not Started | RM2a, RM3a, SW6a, CL2 |
| ENG2 | RTOS + Device Platform Baseline (M7) | Device | High | Filing | Not Started | SW3a, SW4a, SW5a, SW6a, SW11, CY2a, CY7a |
| ENG3 | Drug Library Payload Format Finalized | Device | Med | Filing | Not Started | SW2a, SW2b, RM2a, RM2b, PS1, PS2, PS3 |

### 4.3 Software Development

| # | Prerequisite | Scope | Effort | Phase | Status | Gates |
|---|---|---|---|---|---|---|
| ENG6 | Drug Library Authoring Workflow (D1–D3) | Device | High | Filing | Not Started | SW2b, HF2b, HF3b, HF4b |
| ENG7 | Drug Library Signing Service (D4) | Device | Med | Filing | Not Started | CY2b, PS1, PS2 |
| ENG8 | Audit Log Infrastructure (D6, 21 CFR Part 11) | Device | Med | Filing | Not Started | SW2b, SW6b |
| ENG9 | 21 CFR Part 11 Conformance (D2 + D6) | Device | Med | Filing | Not Started | SW2b, LB3 |
| ENG10 | Adapter Pass-Through Architecture (A3, A4) | Device | Med | Filing | Not Started | MS5, CY7c |
| ENG16 | Drug Library Validation Rule Engine (D3) | Device | Med | Filing | Not Started | SW2b, RM2b, PS1 |
| ENG17 | Firmware Update Verifier (M6/M7 secure boot) | Device | Med | Filing | Not Started | CY2a, CY7a, PS4, PS5 |
| ENG18 | Time Sync / Trusted Time Source (M7) | Device | Low | Filing | Not Started | RM2a, CY7a |

### 4.4 Testing & Tooling

| # | Prerequisite | Scope | Effort | Phase | Status | Gates |
|---|---|---|---|---|---|---|
| ENG13 | HIL Test Rig + System V&V Harness | Device | V.High | Filing | Not Started | SW6a, SW6b, CY7a |
| ENG15 | SBOM Generation Pipeline | Device | Low | Filing | Not Started | CY4a, CY4b, CY4c, MS7 |

### 4.5 User Research & Cybersecurity

| # | Prerequisite | Scope | Effort | Phase | Status | Gates |
|---|---|---|---|---|---|---|
| ENG4 | Crypto / Signing Stack (KMS, cert store, HSM) | Device | High | Filing | Not Started | CY2a, CY2b, CY4a, CY4b, PS1, PS4 |
| ENG5 | Cyber Comms Stack (TLS 1.3, mutual auth, cert provisioning) | Device | High | Filing | Not Started | CY5, CY7a, CY7c, MS5 |
| ENG11 | Occlusion / Air-in-Line Sensor Calibration | Device | High | Filing | Not Started | RM2a, CL2, SW6a |
| ENG12 | Alarm System IEC 60601-1-8 Conformance | Device | High | Filing | Not Started | RM2a, HF3a, SW6a |
| ENG14 | Usability Test Cohort Recruitment | Device | Med | Filing | Not Started | HF4a, HF4b |

### 4.2 AI/ML Development

| # | Prerequisite | Scope | Effort | Phase | Status | Gates |
|---|---|---|---|---|---|---|
| ENG19 | AI/ML Training Infrastructure (predictive alarms) | Device | V.High | Release 2 | Not Started | AI1, AI2, AI3, AI4 |
| ENG20 | AI/ML Drift Monitoring Pipeline | Device | High | Release 2 | Not Started | AI5, AI6 |

## Summary

Run `/tracker status` for live counts. See Changelog for the latest rendered counts.

## Changelog

| Date | Author | Summary |
|---|---|---|
| 2026-04-14 | Claude — `/tracker build` (v2) | Restructured with `### N.N` category headings and renamed P→PC/PS/AI prefixes so the render script classifies rows correctly. 18 engineering prerequisites split across 4.1/4.2/4.3/4.4/4.5. Task 013. |
| 2026-04-14 | Claude — `/tracker build` (v1) | First-stab population of Parts 1–4 from 10 FDA guidance docs + 3 SADs + composition manifest + regulatory strategy. Task 013. |
| 2026-04-14 | Claude — `/tracker init` | Initial scaffold. Context & Sources populated. Task 013. |
