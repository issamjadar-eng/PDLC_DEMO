# PDLC_DEMO — DHF Project Manifest

**Generated**: 2026-04-27  
**Tier**: 4 — Project DHF Manifests (Tier 3 Reference DHF → scope-projected)  
**Status**: Initial — all obligations at `GAP` (no location binding yet)  
**Sections**: 1 per DHF (system suite + 3 item DHFs), obligations grouped by topic  

> Run `/dhf-manifest reproject` to scan the DHF tree and bind obligations to actual file paths.

---

## Scope Configuration

| Scope Flag | Value | Derivation |
|-----------|-------|------------|
| `510k` | true | `project.regulatory_pathway` |
| `pccp` | false | `dhfs[].filing` contains `pccp` |
| `ai` | false | any `dhfs[].classification.ai_enabled` |
| `multi-function` | true | `scope.multi_function_device` |
| `cybersecurity` | true | always in scope |
| `common-baseline` | true | always in scope |
| `usability-hf` | true | `scope.usability_hf` |
| `tool-validation` | true | `scope.tool_validation` |
| `hardware` | true | `scope.hardware` |
| `clinical` | true | `scope.clinical_evaluation` |
| `post-market` | true | always in scope |

**Per-item DHF classifications:**

| DHF | Role | SaMD | IEC 62304 | AI | In PCCP |
|-----|------|------|-----------|-----|---------|
| `pca-device` | system | — | — | — | — |
| `connectivity-adapter` | item | ✓ | Class B | ✗ | ✗ |
| `drug-library-manager` | item | ✓ | Class B | ✗ | ✗ |
| `fleet-management` | item | ✗ | Class A | ✗ | ✗ |
| `compliance-reports` | item | ✗ | Class A | ✗ | ✗ |
| `analytics-dashboard` | item | ✗ | Class A | ✗ | ✗ |
| `inventory-tracker` | item | ✗ | Class A | ✗ | ✗ |
| `alerts-engine` | item | ✓ | Class C | ✗ | ✗ |
| `clinical-interface` | item | ✓ | Class C | ✗ | ✗ |

---

## pca-device
*System DHF — device-level, aggregates evidence from all item DHFs*  
**Obligations in this DHF**: 75

### Architecture (4)

| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |
|----|-----------|---------------|------------------------|-----------|---------------|:------:|
| [`OBL-CYBER-004` · Security Architecture Documentation](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-cyber.md#OBL-CYBER-004) | Include all four security architecture view categories in the premarket submission | submission-content | Security Architecture Document; 510(k) Submission — Cybersecurity Section; SAD | [FDA Cybersecurity Guidance (2023) §V Security Architecture](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-cyber.md#OBL-CYBER-004) | — | GAP |
| [`OBL-MFD-002` · MFD Impact Assessment](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-mfd.md#OBL-MFD-002) | Assess shared resources between Management Services and the SaMD modules: computational resources, data dependencies, code, memory/storage, GUI | analysis | MFD Impact Analysis; System Hazard Analysis; Architecture Document | [FDA MFD Guidance (2020) §IV Impact Assessment](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-mfd.md#OBL-MFD-002) | — | GAP |
| [`OBL-MFD-003` · MFD Premarket Requirements](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-mfd.md#OBL-MFD-003) | The system SAD must document the architectural separation between device functions (Pre-Op, Intra-Op) and "other functions" (Management Services) | design-document | System Architecture Document; 510(k) Submission — Architecture; Hazard Analysis | [FDA MFD Guidance (2020) §V Premarket Submission Requirements](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-mfd.md#OBL-MFD-003) | — | GAP |
| [`OBL-81001-004` · Secure Software Architecture](../../../.claude/skills/dhf-manifest/data/standards/iec-81001-5-1.md#OBL-81001-004) | Apply secure design principles in the SAD: defense in depth, least privilege, secure defaults, fail secure, minimize attack surface | design-document | Software Architecture Document; Security Architecture | [IEC 81001-5-1:2021 §5.3](../../../.claude/skills/dhf-manifest/data/standards/iec-81001-5-1.md#OBL-81001-004) | — | GAP |

### Requirements (4)

| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |
|----|-----------|---------------|------------------------|-----------|---------------|:------:|
| [`OBL-81001-003` · Security Requirements](../../../.claude/skills/dhf-manifest/data/standards/iec-81001-5-1.md#OBL-81001-003) | Derive security requirements from security risk assessment + FDA cybersecurity guidance + PHI/PII obligations | specification | Software Requirements Specification; Security Requirements | [IEC 81001-5-1:2021 §5.2](../../../.claude/skills/dhf-manifest/data/standards/iec-81001-5-1.md#OBL-81001-003) | — | GAP |
| [`OBL-82304-003` · Product Validation Planning](../../../.claude/skills/dhf-manifest/data/standards/iec-82304.md#OBL-82304-003) | Define the intended use of the health software product (maps to the FDA Indications for Use Statement) | specification | Device Description; Intended Use Statement; Software Requirements Specification | [IEC 82304-1:2016 §5.1](../../../.claude/skills/dhf-manifest/data/standards/iec-82304.md#OBL-82304-003) | — | GAP |
| [`OBL-82304-004` · Product Validation Execution](../../../.claude/skills/dhf-manifest/data/standards/iec-82304.md#OBL-82304-004) | Safety requirements must be derived from risk management (ISO 14971) activities — not authored independently | specification | Software Requirements Specification; Risk Control Requirements | [IEC 82304-1:2016 §5.2](../../../.claude/skills/dhf-manifest/data/standards/iec-82304.md#OBL-82304-004) | — | GAP |
| [`OBL-13485-002` · Design Input Documentation](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-002) | Document design inputs covering: functional, performance, and safety requirements | specification | Design Inputs Record; Software Requirements Specification; User Needs Document | [ISO 13485:2016 §7.3.3](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-002) | — | GAP |

### Design Outputs (2)

| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |
|----|-----------|---------------|------------------------|-----------|---------------|:------:|
| [`OBL-SWF-003` · SW Design Documentation](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-sw-functions.md#OBL-SWF-003) | For Enhanced documentation (MedTech Project): include Software Design Specification in the submission | submission-content | 510(k) Submission — Software Documentation (Enhanced); Software Design Document | [FDA SW Functions Guidance (2023) §V Required Documentation Elements](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-sw-functions.md#OBL-SWF-003) | — | GAP |
| [`OBL-13485-003` · Design Output Documentation](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-003) | Design outputs must demonstrably meet the design inputs — traceability is required | specification | Design Outputs Record; Software Architecture Document; Software Design Document | [ISO 13485:2016 §7.3.4](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-003) | — | GAP |

### Traceability (1)

| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |
|----|-----------|---------------|------------------------|-----------|---------------|:------:|
| [`OBL-13485-009` · Design History File](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-009) | Maintain a Design History File (DHF) for each device type or family | dhf-file | Design History File; DHF README; DHF Manifest | [ISO 13485:2016 §7.3.10](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-009) | — | GAP |

### Risk Management (16)

| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |
|----|-----------|---------------|------------------------|-----------|---------------|:------:|
| [`OBL-82304-001` · Health Software Requirements](../../../.claude/skills/dhf-manifest/data/standards/iec-82304.md#OBL-82304-001) | Apply ISO 14971 risk management at the product level (IEC 82304-1 mandates this; does not define its own risk process) | plan | Risk Management Plan; Risk Management File | [IEC 82304-1:2016 §4.2](../../../.claude/skills/dhf-manifest/data/standards/iec-82304.md#OBL-82304-001) | — | GAP |
| [`OBL-14971-001` · Risk Management Plan](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-001) | Produce a Risk Management Plan before risk management activities begin | plan | Risk Management Plan | [ISO 14971:2019 §4.4](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-001) | — | GAP |
| [`OBL-14971-002` · RM Plan Content](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-002) | Define the scope — which device, which functions, which lifecycle phases | plan | Risk Management Plan | [ISO 14971:2019 §4.4 (a)–(g)](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-002) | — | GAP |
| [`OBL-14971-003` · Risk Acceptability Criteria](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-003) | Define severity levels (e.g., catastrophic, critical, marginal, negligible) with descriptions | plan | Risk Management Plan; Risk Management File | [ISO 14971:2019 §4.4 — risk acceptability](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-003) | — | GAP |
| [`OBL-14971-004` · Risk Management File](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-004) | Maintain a Risk Management File — a collection of records providing full traceability for each hazard | record | Risk Management File | [ISO 14971:2019 §4.5](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-004) | — | GAP |
| [`OBL-14971-005` · Intended Use & Misuse](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-005) | Document the intended use including: intended patient population, clinical indication, use environment, user profile | record | Intended Use Statement; Risk Analysis; Risk Management Plan | [ISO 14971:2019 §5.2](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-005) | — | GAP |
| [`OBL-14971-006` · Safety Characteristics Identification](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-006) | Systematically identify device characteristics that could contribute to hazards (use ISO 14971 Annex C as a checklist) | record | Risk Analysis; Safety-Related Characteristics Checklist | [ISO 14971:2019 §5.3](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-006) | — | GAP |
| [`OBL-14971-007` · Hazard Identification](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-007) | Identify all foreseeable hazards (energy, biology, data, software, mechanical, chemical, etc.) | record | Preliminary Hazard Analysis; Hazard Analysis; Risk Management File | [ISO 14971:2019 §5.4](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-007) | — | GAP |
| [`OBL-14971-008` · Risk Estimation](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-008) | Estimate risk for each hazardous situation using severity × probability from the risk matrix in the plan | record | Risk Assessment / FMEA; Risk Management File | [ISO 14971:2019 §5.5](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-008) | — | GAP |
| [`OBL-14971-009` · Risk Evaluation](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-009) | Apply the risk matrix from the plan to each estimated risk — classify as acceptable / ALARP / unacceptable | record | Risk Assessment / FMEA; Risk Management File | [ISO 14971:2019 §6](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-009) | — | GAP |
| [`OBL-14971-010` · Risk Control Options](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-010) | Apply risk controls in priority order: (1) design-level elimination, (2) device protective measure, (3) information/labeling | record | Risk Control Measures; Risk Management File | [ISO 14971:2019 §7.1](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-010) | — | GAP |
| [`OBL-14971-011` · Risk Control Verification](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-011) | Verify that each risk control measure is implemented as specified (implementation verification record) | record | Risk Control Measures; Verification Records; Risk Management File | [ISO 14971:2019 §7.2 + §7.3](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-011) | — | GAP |
| [`OBL-14971-012` · Benefit-Risk Analysis](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-012) | Conduct a benefit-risk analysis for any hazardous situation where residual risk exceeds acceptability criteria after all feasible controls are applied | record | Benefit-Risk Analysis; Risk Management File | [ISO 14971:2019 §7.4](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-012) | — | GAP |
| [`OBL-14971-013` · Secondary Hazard Evaluation](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-013) | After applying each risk control, evaluate whether the control creates new hazards (secondary hazards) | record | Risk Management File | [ISO 14971:2019 §7.5 + §7.6](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-013) | — | GAP |
| [`OBL-14971-014` · Overall Residual Risk Evaluation](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-014) | Conduct an Overall Residual Risk Evaluation (ORRE) after all individual risk controls are verified | record | Overall Residual Risk Evaluation; Risk Management Report | [ISO 14971:2019 §8](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-014) | — | GAP |
| [`OBL-14971-015` · Risk Management Review](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-015) | Conduct a Risk Management Review before product release — this is a pre-release gate | report | Risk Management Report | [ISO 14971:2019 §9](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-015) | — | GAP |

### Verification (5)

| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |
|----|-----------|---------------|------------------------|-----------|---------------|:------:|
| [`OBL-CYBER-005` · Cybersecurity Testing](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-cyber.md#OBL-CYBER-005) | Conduct all four types of cybersecurity testing before submission | submission-content | Security Test Report; 510(k) Submission — Cybersecurity Section | [FDA Cybersecurity Guidance (2023) §VI Cybersecurity Testing](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-cyber.md#OBL-CYBER-005) | — | GAP |
| [`OBL-SWF-005` · SW Testing Documentation](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-sw-functions.md#OBL-SWF-005) | For Enhanced documentation (MedTech Project): submit complete test protocols and reports at unit, integration, AND system levels | submission-content | 510(k) Submission — Software Testing; Test Protocols and Reports | [FDA SW Functions Guidance (2023) §V Required Documentation Elements](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-sw-functions.md#OBL-SWF-005) | — | GAP |
| [`OBL-62366-006` · UI Verification](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-006) | Verify the implemented user interface meets the UI specification requirements | test-report | UI Verification Report; V&V Plan | [IEC 62366-1:2015 §5.5](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-006) | — | GAP |
| [`OBL-81001-006` · Secure Implementation Practices](../../../.claude/skills/dhf-manifest/data/standards/iec-81001-5-1.md#OBL-81001-006) | Conduct system-level security testing before release: vulnerability scanning, penetration testing | test-report | Security Test Report; V&V Plan | [IEC 81001-5-1:2021 §5.7](../../../.claude/skills/dhf-manifest/data/standards/iec-81001-5-1.md#OBL-81001-006) | — | GAP |
| [`OBL-13485-005` · Design Verification Planning](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-005) | Plan design verification at each development stage per the DDP | test-report | Verification Plan; Verification Reports; V&V Plan | [ISO 13485:2016 §7.3.6](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-005) | — | GAP |

### Validation (4)

| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |
|----|-----------|---------------|------------------------|-----------|---------------|:------:|
| [`OBL-62366-007` · Formative Usability Evaluation](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-007) | Conduct iterative formative usability evaluations during design | test-report | Formative Evaluation Reports; Usability Engineering File | [IEC 62366-1:2015 §5.6](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-007) | — | GAP |
| [`OBL-62366-008` · Summative Usability Validation](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-008) | Conduct a final summative usability evaluation before market release | test-report | Summative Usability Evaluation Report; 510(k) Submission | [IEC 62366-1:2015 §5.6](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-008) | — | GAP |
| [`OBL-82304-006` · Post-Market Surveillance Plan](../../../.claude/skills/dhf-manifest/data/standards/iec-82304.md#OBL-82304-006) | Validate MedTech Project in the intended operating environment (or validated simulation) — not just on a development server | test-report | Validation Report; Clinical Evaluation; V&V Plan | [IEC 82304-1:2016 §8.2](../../../.claude/skills/dhf-manifest/data/standards/iec-82304.md#OBL-82304-006) | — | GAP |
| [`OBL-13485-006` · Design Validation Planning](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-006) | Plan design validation per the DDP — plan must precede execution | test-report | Validation Plan; Clinical Validation Report; V&V Plan | [ISO 13485:2016 §7.3.7](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-006) | — | GAP |

### Software Lifecycle (8)

| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |
|----|-----------|---------------|------------------------|-----------|---------------|:------:|
| [`OBL-SWF-004` · SW Lifecycle Documentation](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-sw-functions.md#OBL-SWF-004) | Option 1 (preferred): Submit a Declaration of Conformity to IEC 62304 — this substitutes for the SW development practices documentation section | submission-content | 510(k) Submission — Software Documentation; IEC 62304 Declaration of Conformity | [FDA SW Functions Guidance (2023) §V Required Documentation Elements](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-sw-functions.md#OBL-SWF-004) | — | GAP |
| [`OBL-SWF-006` · Unresolved Anomalies List](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-sw-functions.md#OBL-SWF-006) | Include software version history from first version under design controls to the final released version | submission-content | 510(k) Submission — Software Documentation; Unresolved Anomalies List | [FDA SW Functions Guidance (2023) §V Required Documentation Elements](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-sw-functions.md#OBL-SWF-006) | — | GAP |
| [`OBL-81001-002` · Secure Development Plan](../../../.claude/skills/dhf-manifest/data/standards/iec-81001-5-1.md#OBL-81001-002) | Include security activities in the SDP: threat modeling, secure design, security testing, vulnerability management | plan | Software Development Plan; Cybersecurity Plan | [IEC 81001-5-1:2021 §5.1](../../../.claude/skills/dhf-manifest/data/standards/iec-81001-5-1.md#OBL-81001-002) | — | GAP |
| [`OBL-81001-005` · Secure Detailed Design](../../../.claude/skills/dhf-manifest/data/standards/iec-81001-5-1.md#OBL-81001-005) | Follow a defined secure coding standard (e.g., OWASP, CERT C, or equivalent) | process-record | Secure Coding Standard; SOUP List; Software Development Process Records | [IEC 81001-5-1:2021 §5.5](../../../.claude/skills/dhf-manifest/data/standards/iec-81001-5-1.md#OBL-81001-005) | — | GAP |
| [`OBL-82304-002` · Safety Requirements Specification](../../../.claude/skills/dhf-manifest/data/standards/iec-82304.md#OBL-82304-002) | All software development activities must conform to IEC 62304 | process-record | Software Development Plan; IEC 62304 Conformance Records | [IEC 82304-1:2016 §4.3](../../../.claude/skills/dhf-manifest/data/standards/iec-82304.md#OBL-82304-002) | — | GAP |
| [`OBL-82304-005` · Accompanying Documents](../../../.claude/skills/dhf-manifest/data/standards/iec-82304.md#OBL-82304-005) | The SDP (or a companion lifecycle plan) must address the full product lifecycle beyond development: deployment, post-market operation, maintenance, and decommissioning | plan | Software Development Plan; Product Lifecycle Plan | [IEC 82304-1:2016 §6.1](../../../.claude/skills/dhf-manifest/data/standards/iec-82304.md#OBL-82304-005) | — | GAP |
| [`OBL-13485-001` · Design & Development Planning](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-001) | Document the stages of design and development with defined entry/exit criteria | plan | Design and Development Plan; Software Development Plan | [ISO 13485:2016 §7.3.2](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-001) | — | GAP |
| [`OBL-13485-010` · SOUP Supplier Qualification](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-010) | Evaluate and qualify SOUP/third-party software components as suppliers (for IEC 62304 Class B/C, SOUP evaluation is also an IEC 62304 §8.1.2 obligation) | process-record | SOUP List; Supplier Qualification Records; Approved Supplier List | [ISO 13485:2016 §7.4.1](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-010) | — | GAP |

### Configuration & Change Control (3)

| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |
|----|-----------|---------------|------------------------|-----------|---------------|:------:|
| [`OBL-81001-007` · Security Verification Testing](../../../.claude/skills/dhf-manifest/data/standards/iec-81001-5-1.md#OBL-81001-007) | Generate a machine-readable SBOM at release (SPDX or CycloneDX format) | release-record | SBOM; Security Release Notes; Software Release Package | [IEC 81001-5-1:2021 §5.8](../../../.claude/skills/dhf-manifest/data/standards/iec-81001-5-1.md#OBL-81001-007) | — | GAP |
| [`OBL-13485-007` · Design Transfer Procedure](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-007) | Define and follow a documented design transfer procedure | process-record | Design Transfer Record; Release Package; Configuration Baseline | [ISO 13485:2016 §7.3.8](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-007) | — | GAP |
| [`OBL-13485-008` · Design Change Control](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-008) | Design changes must be reviewed, and as appropriate verified and validated, before implementation | change-record | Design Change Records; PCCP Change Records; ECO Records | [ISO 13485:2016 §7.3.9](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-008) | — | GAP |

### Design Reviews (1)

| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |
|----|-----------|---------------|------------------------|-----------|---------------|:------:|
| [`OBL-13485-004` · Design Reviews](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-004) | Conduct design reviews at planned stages per the DDP | review-record | Design Review Records; Phase Gate Records | [ISO 13485:2016 §7.3.5](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-004) | — | GAP |

### Labeling & IFU (1)

| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |
|----|-----------|---------------|------------------------|-----------|---------------|:------:|
| [`OBL-82304-007` · Post-Market Problem Resolution](../../../.claude/skills/dhf-manifest/data/standards/iec-82304.md#OBL-82304-007) | IFU / user documentation must explicitly state: intended use, intended operating environment (hardware, OS, network requirements) | labeling | Instructions for Use; User Documentation; Labeling | [IEC 82304-1:2016 §9.2](../../../.claude/skills/dhf-manifest/data/standards/iec-82304.md#OBL-82304-007) | — | GAP |

### Human Factors (6)

| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |
|----|-----------|---------------|------------------------|-----------|---------------|:------:|
| [`OBL-62366-001` · Usability Engineering Plan](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-001) | Establish a usability engineering process and maintain it throughout the development lifecycle | plan | Usability Engineering Plan; Design and Development Plan | [IEC 62366-1:2015 §4.1](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-001) | — | GAP |
| [`OBL-62366-002` · Use Specification](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-002) | Identify and characterize the intended users for each use scenario | specification | Use Specification; Usability Engineering File | [IEC 62366-1:2015 §5.1.1](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-002) | — | GAP |
| [`OBL-62366-003` · User Profiles & Environments](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-003) | Document the intended use environment for each module | specification | Use Specification; Usability Engineering File | [IEC 62366-1:2015 §5.1.2](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-003) | — | GAP |
| [`OBL-62366-004` · Use-Related Risk Analysis](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-004) | Identify all potential use errors per module — perception errors, cognitive errors, action errors | analysis | Use-Related Risk Analysis; Usability Engineering File; Risk Management File | [IEC 62366-1:2015 §5.2](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-004) | — | GAP |
| [`OBL-62366-005` · User Interface Specification](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-005) | Establish a UI specification derived from the use specification and use-related risk analysis | specification | User Interface Specification; Software Requirements Specification | [IEC 62366-1:2015 §5.3](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-005) | — | GAP |
| [`OBL-62366-009` · UOUP Evaluation](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-009) | If third-party UI frameworks or pre-built components are used in the clinical interface, evaluate them under the UOUP process | analysis | UOUP Evaluation; Usability Engineering File | [IEC 62366-1:2015 §5.7](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-009) | — | GAP |

### Cybersecurity (5)

| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |
|----|-----------|---------------|------------------------|-----------|---------------|:------:|
| [`OBL-CYBER-001` · §524B Statutory Requirements](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-cyber.md#OBL-CYBER-001) | SBOM is a STATUTORY requirement for cyber device premarket submissions (FD&C Act §524B) — not optional | submission-content | 510(k) Submission — Cybersecurity Documentation; Post-Market Cyber Plan; SBOM | [FDA Cybersecurity Guidance (2023) §524B Statutory Requirements](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-cyber.md#OBL-CYBER-001) | — | GAP |
| [`OBL-CYBER-002` · Security Risk Management](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-cyber.md#OBL-CYBER-002) | Include a Security Risk Management Report in the premarket submission (per AAMI TIR57 or equivalent) | submission-content | Security Risk Management Report; Threat Model; 510(k) Submission | [FDA Cybersecurity Guidance (2023) §III Security Risk Management](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-cyber.md#OBL-CYBER-002) | — | GAP |
| [`OBL-CYBER-003` · SBOM Requirements](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-cyber.md#OBL-CYBER-003) | SBOM must be machine-readable (SPDX or CycloneDX format) | submission-content | SBOM; 510(k) Submission — Cybersecurity Section | [FDA Cybersecurity Guidance (2023) §IV SBOM Requirements](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-cyber.md#OBL-CYBER-003) | — | GAP |
| [`OBL-81001-001` · Security Risk Management Plan](../../../.claude/skills/dhf-manifest/data/standards/iec-81001-5-1.md#OBL-81001-001) | Integrate security risk management with the ISO 14971 risk management process — security risks must appear in the device risk file | plan | Security Risk Assessment; Risk Management Plan; Software Development Plan | [IEC 81001-5-1:2021 §4.2](../../../.claude/skills/dhf-manifest/data/standards/iec-81001-5-1.md#OBL-81001-001) | — | GAP |
| [`OBL-81001-009` · Post-Market Security Maintenance](../../../.claude/skills/dhf-manifest/data/standards/iec-81001-5-1.md#OBL-81001-009) | Conduct a systematic threat model covering: assets (patient data, guidance algorithms, system configuration), threat agents (network attackers, malicious insiders, compromised SOUP), and threats (STRIDE categories) | analysis | Threat Model; Security Risk Assessment | [IEC 81001-5-1:2021 §7.1](../../../.claude/skills/dhf-manifest/data/standards/iec-81001-5-1.md#OBL-81001-009) | — | GAP |

### Post-Market (5)

| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |
|----|-----------|---------------|------------------------|-----------|---------------|:------:|
| [`OBL-CYBER-006` · Cybersecurity Management Plan](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-cyber.md#OBL-CYBER-006) | Cybersecurity Management Plan is REQUIRED for cyber device 510(k) submissions under §524B | submission-content | Cybersecurity Management Plan; Post-Market Surveillance Plan; 510(k) Submission | [FDA Cybersecurity Guidance (2023) §VII Cybersecurity Management Plan](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-cyber.md#OBL-CYBER-006) | — | GAP |
| [`OBL-62304-019` · Problem Resolution Process](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-019) | Establish a problem resolution process covering: receipt, investigation, resolution, and closure | record | Problem Resolution Process; Software Maintenance Plan | [IEC 62304:2006+AMD1:2015 §9.1](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-019) | — | GAP |
| [`OBL-81001-008` · Secure Release](../../../.claude/skills/dhf-manifest/data/standards/iec-81001-5-1.md#OBL-81001-008) | Establish a continuous post-market vulnerability monitoring process | plan | Vulnerability Management Plan; Post-Market Surveillance Plan | [IEC 81001-5-1:2021 §6.1](../../../.claude/skills/dhf-manifest/data/standards/iec-81001-5-1.md#OBL-81001-008) | — | GAP |
| [`OBL-81001-010` · Security Records & SBOM](../../../.claude/skills/dhf-manifest/data/standards/iec-81001-5-1.md#OBL-81001-010) | Define and document a security incident response process | plan | Security Incident Response Plan; Post-Market Surveillance Plan | [IEC 81001-5-1:2021 §9](../../../.claude/skills/dhf-manifest/data/standards/iec-81001-5-1.md#OBL-81001-010) | — | GAP |
| [`OBL-82304-008` · Decommissioning Plan](../../../.claude/skills/dhf-manifest/data/standards/iec-82304.md#OBL-82304-008) | Define a decommissioning plan covering: data archival (surgical case records, patient data), migration path for active users, patient safety during service transition | plan | Product Lifecycle Plan; Post-Market Surveillance Plan | [IEC 82304-1:2016 §11](../../../.claude/skills/dhf-manifest/data/standards/iec-82304.md#OBL-82304-008) | — | GAP |

### Regulatory Submission (10)

| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |
|----|-----------|---------------|------------------------|-----------|---------------|:------:|
| [`OBL-510K-001` · Substantial Equivalence Argument](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-510k.md#OBL-510K-001) | Demonstrate same intended use as the predicate device — intended use is the general purpose/function, encompassing indications for use | submission-content | 510(k) Submission — SE Argument; Predicate Device Analysis | [FDA 510(k) SE Guidance (2014) §III Substantial Equivalence Standard](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-510k.md#OBL-510K-001) | — | GAP |
| [`OBL-510K-002` · Predicate Device Selection](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-510k.md#OBL-510K-002) | Select a primary predicate with intended use and technological characteristics most similar to MedTech Project | submission-content | Predicate Device Analysis; 510(k) Submission — Device Description | [FDA 510(k) SE Guidance (2014) §IV Predicate Device Selection](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-510k.md#OBL-510K-002) | — | GAP |
| [`OBL-510K-003` · Performance Data for SE](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-510k.md#OBL-510K-003) | Apply the least-burdensome principle: provide the minimum data necessary to demonstrate SE | submission-content | 510(k) Submission — Performance Testing; V&V Plan | [FDA 510(k) SE Guidance (2014) §V Performance Data](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-510k.md#OBL-510K-003) | — | GAP |
| [`OBL-510K-004` · 510(k) Summary Content](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-510k.md#OBL-510K-004) | Include a 510(k) Summary per 21 CFR 807.92 — required, not optional | submission-content | 510(k) Submission — 510(k) Summary; SE Narrative | [FDA 510(k) SE Guidance (2014) §VI 510(k) Summary](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-510k.md#OBL-510K-004) | — | GAP |
| [`OBL-CDS-001` · CDS Criterion 1 Analysis](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-cds.md#OBL-CDS-001) | Any software function that acquires, processes, or analyzes medical images FAILS criterion 1 and is a device (SaMD) — cannot claim CDS non-device status | analysis | Device Classification Determination; 510(k) Submission — Device Description; CDS Exemption Analysis | [FDA CDS Guidance (2026) §IV Criterion 1](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-cds.md#OBL-CDS-001) | — | GAP |
| [`OBL-CDS-002` · CDS Criteria 3–4 Analysis](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-cds.md#OBL-CDS-002) | For Management Services PostOp Reports: evaluate against all four CDS criteria to confirm non-device status | analysis | Device Classification Determination; 510(k) Submission — Indications for Use; Labeling | [FDA CDS Guidance (2026) §IV Criteria 3 and 4](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-cds.md#OBL-CDS-002) | — | GAP |
| [`OBL-CDS-003` · CDS Device Determination](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-cds.md#OBL-CDS-003) | For any software function where CDS non-device status is uncertain: use a Q-Sub (pre-submission meeting) to get FDA feedback before filing the 510(k) | process-record | Q-Sub Package; Device Classification Documentation | [FDA CDS Guidance (2026) §V Device Determination Process](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-cds.md#OBL-CDS-003) | — | GAP |
| [`OBL-MFD-001` · MFD Core Policy](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-mfd.md#OBL-MFD-001) | MedTech Project is a multiple function device product: Pre-Op (SaMD) + Intra-Op (SaMD) are device functions; Management Services is the "other function" | analysis | 510(k) Submission — Device Description; MFD Impact Analysis | [FDA MFD Guidance (2020) §III Core Policy](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-mfd.md#OBL-MFD-001) | — | GAP |
| [`OBL-SWF-001` · Software Documentation Level](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-sw-functions.md#OBL-SWF-001) | Determine documentation level (Basic or Enhanced) based on risk assessment — assessed BEFORE risk control measures | submission-content | 510(k) Submission — Software Documentation; Documentation Level Statement | [FDA SW Functions Guidance (2023) §IV Documentation Levels](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-sw-functions.md#OBL-SWF-001) | — | GAP |
| [`OBL-SWF-002` · SW Submission Documentation](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-sw-functions.md#OBL-SWF-002) | Include a Software Description: overview of significant features, inputs, outputs, hardware platforms | submission-content | 510(k) Submission — Software Documentation; SRS; Architecture Document | [FDA SW Functions Guidance (2023) §V Required Documentation Elements](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-sw-functions.md#OBL-SWF-002) | — | GAP |

---

## connectivity-adapter
*SaMD · IEC 62304 Class B*  
**Obligations in this DHF**: 49

### Architecture (4)

| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |
|----|-----------|---------------|------------------------|-----------|---------------|:------:|
| [`OBL-62304-007` · Software Architecture Specification](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-007) | Produce a Software Architecture Document (SAD) transforming the SRS into a structural design | spec | Software Architecture Document | [IEC 62304:2006+AMD1:2015 §5.3.1](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-007) | — | GAP |
| [`OBL-62304-008` · SOUP Identification](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-008) | Identify all SOUP (Software of Unknown Provenance) items used in each software item | record | SOUP List; Software Architecture Document | [IEC 62304:2006+AMD1:2015 §5.3.3](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-008) | — | GAP |
| [`OBL-62304-009` · Architecture Verification](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-009) | Conduct and document an architecture verification that confirms all SRS requirements are addressed in the design | record | Software Architecture Document; Architecture Verification Record | [IEC 62304:2006+AMD1:2015 §5.3.4](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-009) | — | GAP |
| [`OBL-81001-004` · Secure Software Architecture](../../../.claude/skills/dhf-manifest/data/standards/iec-81001-5-1.md#OBL-81001-004) | Apply secure design principles in the SAD: defense in depth, least privilege, secure defaults, fail secure, minimize attack surface | design-document | Software Architecture Document; Security Architecture | [IEC 81001-5-1:2021 §5.3](../../../.claude/skills/dhf-manifest/data/standards/iec-81001-5-1.md#OBL-81001-004) | — | GAP |

### Requirements (6)

| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |
|----|-----------|---------------|------------------------|-----------|---------------|:------:|
| [`OBL-62304-004` · Software Requirements Specification](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-004) | Define software requirements traceable to system-level requirements | spec | Software Requirements Specification | [IEC 62304:2006+AMD1:2015 §5.2.1](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-004) | — | GAP |
| [`OBL-62304-005` · SRS Content Requirements](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-005) | SRS must cover: functional/capability requirements, I/O requirements, external interfaces | spec | Software Requirements Specification | [IEC 62304:2006+AMD1:2015 §5.2.2 + §5.2.3](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-005) | — | GAP |
| [`OBL-62304-006` · SRS Risk Control Trace](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-006) | Re-evaluate risk after SRS is established — update risk file if new hazards emerge | record | Software Requirements Specification; Risk Management File | [IEC 62304:2006+AMD1:2015 §5.2.6](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-006) | — | GAP |
| [`OBL-81001-003` · Security Requirements](../../../.claude/skills/dhf-manifest/data/standards/iec-81001-5-1.md#OBL-81001-003) | Derive security requirements from security risk assessment + FDA cybersecurity guidance + PHI/PII obligations | specification | Software Requirements Specification; Security Requirements | [IEC 81001-5-1:2021 §5.2](../../../.claude/skills/dhf-manifest/data/standards/iec-81001-5-1.md#OBL-81001-003) | — | GAP |
| [`OBL-82304-004` · Product Validation Execution](../../../.claude/skills/dhf-manifest/data/standards/iec-82304.md#OBL-82304-004) | Safety requirements must be derived from risk management (ISO 14971) activities — not authored independently | specification | Software Requirements Specification; Risk Control Requirements | [IEC 82304-1:2016 §5.2](../../../.claude/skills/dhf-manifest/data/standards/iec-82304.md#OBL-82304-004) | — | GAP |
| [`OBL-13485-002` · Design Input Documentation](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-002) | Document design inputs covering: functional, performance, and safety requirements | specification | Design Inputs Record; Software Requirements Specification; User Needs Document | [ISO 13485:2016 §7.3.3](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-002) | — | GAP |

### Design Outputs (2)

| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |
|----|-----------|---------------|------------------------|-----------|---------------|:------:|
| [`OBL-SWF-003` · SW Design Documentation](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-sw-functions.md#OBL-SWF-003) | For Enhanced documentation (MedTech Project): include Software Design Specification in the submission | submission-content | 510(k) Submission — Software Documentation (Enhanced); Software Design Document | [FDA SW Functions Guidance (2023) §V Required Documentation Elements](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-sw-functions.md#OBL-SWF-003) | — | GAP |
| [`OBL-13485-003` · Design Output Documentation](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-003) | Design outputs must demonstrably meet the design inputs — traceability is required | specification | Design Outputs Record; Software Architecture Document; Software Design Document | [ISO 13485:2016 §7.3.4](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-003) | — | GAP |

### Traceability (2)

| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |
|----|-----------|---------------|------------------------|-----------|---------------|:------:|
| [`OBL-62304-020` · Software Traceability](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-020) | Maintain bidirectional traceability: system requirements → software requirements → architecture → test cases | record | Trace Matrix; Software Development Plan | [IEC 62304:2006+AMD1:2015 §5.1.6(d)](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-020) | — | GAP |
| [`OBL-13485-009` · Design History File](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-009) | Maintain a Design History File (DHF) for each device type or family | dhf-file | Design History File; DHF README; DHF Manifest | [ISO 13485:2016 §7.3.10](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-009) | — | GAP |

### Risk Management (8)

| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |
|----|-----------|---------------|------------------------|-----------|---------------|:------:|
| [`OBL-62304-016` · Software Hazard Analysis](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-016) | For each hazardous situation in the risk file, identify which software items could contribute to it | record | Risk Management File; Software FMEA; Hazard Analysis | [IEC 62304:2006+AMD1:2015 §7.1.1](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-016) | — | GAP |
| [`OBL-62304-017` · SOUP Risk Evaluation](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-017) | For each SOUP item, obtain and review the supplier's known anomaly list | record | Risk Management File; SOUP Risk Evaluation | [IEC 62304:2006+AMD1:2015 §7.1.3](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-017) | — | GAP |
| [`OBL-14971-007` · Hazard Identification](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-007) | Identify all foreseeable hazards (energy, biology, data, software, mechanical, chemical, etc.) | record | Preliminary Hazard Analysis; Hazard Analysis; Risk Management File | [ISO 14971:2019 §5.4](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-007) | — | GAP |
| [`OBL-14971-008` · Risk Estimation](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-008) | Estimate risk for each hazardous situation using severity × probability from the risk matrix in the plan | record | Risk Assessment / FMEA; Risk Management File | [ISO 14971:2019 §5.5](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-008) | — | GAP |
| [`OBL-14971-009` · Risk Evaluation](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-009) | Apply the risk matrix from the plan to each estimated risk — classify as acceptable / ALARP / unacceptable | record | Risk Assessment / FMEA; Risk Management File | [ISO 14971:2019 §6](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-009) | — | GAP |
| [`OBL-14971-010` · Risk Control Options](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-010) | Apply risk controls in priority order: (1) design-level elimination, (2) device protective measure, (3) information/labeling | record | Risk Control Measures; Risk Management File | [ISO 14971:2019 §7.1](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-010) | — | GAP |
| [`OBL-14971-011` · Risk Control Verification](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-011) | Verify that each risk control measure is implemented as specified (implementation verification record) | record | Risk Control Measures; Verification Records; Risk Management File | [ISO 14971:2019 §7.2 + §7.3](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-011) | — | GAP |
| [`OBL-14971-013` · Secondary Hazard Evaluation](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-013) | After applying each risk control, evaluate whether the control creates new hazards (secondary hazards) | record | Risk Management File | [ISO 14971:2019 §7.5 + §7.6](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-013) | — | GAP |

### Verification (6)

| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |
|----|-----------|---------------|------------------------|-----------|---------------|:------:|
| [`OBL-SWF-005` · SW Testing Documentation](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-sw-functions.md#OBL-SWF-005) | For Enhanced documentation (MedTech Project): submit complete test protocols and reports at unit, integration, AND system levels | submission-content | 510(k) Submission — Software Testing; Test Protocols and Reports | [FDA SW Functions Guidance (2023) §V Required Documentation Elements](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-sw-functions.md#OBL-SWF-005) | — | GAP |
| [`OBL-62304-011` · Unit Verification](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-011) | Verify each software unit through code review, unit testing, or both | record | Unit Verification Records; Code Review Records | [IEC 62304:2006+AMD1:2015 §5.5.2 + §5.5.3](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-011) | — | GAP |
| [`OBL-62304-012` · Integration Testing](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-012) | Produce an integration plan defining the sequence and method for integrating software items | protocol | Integration Test Plan; Integration Test Report | [IEC 62304:2006+AMD1:2015 §5.6.1 + §5.6.3](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-012) | — | GAP |
| [`OBL-62366-006` · UI Verification](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-006) | Verify the implemented user interface meets the UI specification requirements | test-report | UI Verification Report; V&V Plan | [IEC 62366-1:2015 §5.5](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-006) | — | GAP |
| [`OBL-81001-006` · Secure Implementation Practices](../../../.claude/skills/dhf-manifest/data/standards/iec-81001-5-1.md#OBL-81001-006) | Conduct system-level security testing before release: vulnerability scanning, penetration testing | test-report | Security Test Report; V&V Plan | [IEC 81001-5-1:2021 §5.7](../../../.claude/skills/dhf-manifest/data/standards/iec-81001-5-1.md#OBL-81001-006) | — | GAP |
| [`OBL-13485-005` · Design Verification Planning](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-005) | Plan design verification at each development stage per the DDP | test-report | Verification Plan; Verification Reports; V&V Plan | [ISO 13485:2016 §7.3.6](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-005) | — | GAP |

### Validation (2)

| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |
|----|-----------|---------------|------------------------|-----------|---------------|:------:|
| [`OBL-62304-013` · System Testing](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-013) | Test the complete integrated software system against every SRS requirement | protocol | Software System Test Plan; Software System Test Report | [IEC 62304:2006+AMD1:2015 §5.7.1 + §5.7.3](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-013) | — | GAP |
| [`OBL-62366-007` · Formative Usability Evaluation](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-007) | Conduct iterative formative usability evaluations during design | test-report | Formative Evaluation Reports; Usability Engineering File | [IEC 62366-1:2015 §5.6](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-007) | — | GAP |

### Software Lifecycle (10)

| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |
|----|-----------|---------------|------------------------|-----------|---------------|:------:|
| [`OBL-SWF-004` · SW Lifecycle Documentation](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-sw-functions.md#OBL-SWF-004) | Option 1 (preferred): Submit a Declaration of Conformity to IEC 62304 — this substitutes for the SW development practices documentation section | submission-content | 510(k) Submission — Software Documentation; IEC 62304 Declaration of Conformity | [FDA SW Functions Guidance (2023) §V Required Documentation Elements](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-sw-functions.md#OBL-SWF-004) | — | GAP |
| [`OBL-SWF-006` · Unresolved Anomalies List](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-sw-functions.md#OBL-SWF-006) | Include software version history from first version under design controls to the final released version | submission-content | 510(k) Submission — Software Documentation; Unresolved Anomalies List | [FDA SW Functions Guidance (2023) §V Required Documentation Elements](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-sw-functions.md#OBL-SWF-006) | — | GAP |
| [`OBL-62304-001` · Software Safety Classification](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-001) | Assign IEC 62304 safety class (A, B, or C) to each software item before development begins | record | Safety Classification Record; Software Development Plan | [IEC 62304:2006+AMD1:2015 §4.3](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-001) | — | GAP |
| [`OBL-62304-002` · Software Development Plan](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-002) | Establish a Software Development Plan (SDP) before beginning software development | plan | Software Development Plan; Design and Development Plan | [IEC 62304:2006+AMD1:2015 §5.1.1](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-002) | — | GAP |
| [`OBL-62304-003` · SDP Content & Lifecycle](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-003) | SDP must define the SDLC model (waterfall, iterative, agile-within-waterfall, etc.) | plan | Software Development Plan | [IEC 62304:2006+AMD1:2015 §5.1.2 + §5.1.3](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-003) | — | GAP |
| [`OBL-81001-002` · Secure Development Plan](../../../.claude/skills/dhf-manifest/data/standards/iec-81001-5-1.md#OBL-81001-002) | Include security activities in the SDP: threat modeling, secure design, security testing, vulnerability management | plan | Software Development Plan; Cybersecurity Plan | [IEC 81001-5-1:2021 §5.1](../../../.claude/skills/dhf-manifest/data/standards/iec-81001-5-1.md#OBL-81001-002) | — | GAP |
| [`OBL-81001-005` · Secure Detailed Design](../../../.claude/skills/dhf-manifest/data/standards/iec-81001-5-1.md#OBL-81001-005) | Follow a defined secure coding standard (e.g., OWASP, CERT C, or equivalent) | process-record | Secure Coding Standard; SOUP List; Software Development Process Records | [IEC 81001-5-1:2021 §5.5](../../../.claude/skills/dhf-manifest/data/standards/iec-81001-5-1.md#OBL-81001-005) | — | GAP |
| [`OBL-82304-002` · Safety Requirements Specification](../../../.claude/skills/dhf-manifest/data/standards/iec-82304.md#OBL-82304-002) | All software development activities must conform to IEC 62304 | process-record | Software Development Plan; IEC 62304 Conformance Records | [IEC 82304-1:2016 §4.3](../../../.claude/skills/dhf-manifest/data/standards/iec-82304.md#OBL-82304-002) | — | GAP |
| [`OBL-13485-001` · Design & Development Planning](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-001) | Document the stages of design and development with defined entry/exit criteria | plan | Design and Development Plan; Software Development Plan | [ISO 13485:2016 §7.3.2](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-001) | — | GAP |
| [`OBL-13485-010` · SOUP Supplier Qualification](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-010) | Evaluate and qualify SOUP/third-party software components as suppliers (for IEC 62304 Class B/C, SOUP evaluation is also an IEC 62304 §8.1.2 obligation) | process-record | SOUP List; Supplier Qualification Records; Approved Supplier List | [ISO 13485:2016 §7.4.1](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-010) | — | GAP |

### Configuration & Change Control (4)

| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |
|----|-----------|---------------|------------------------|-----------|---------------|:------:|
| [`OBL-62304-014` · Software Release](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-014) | Assign a unique version identifier to the released software (must be traceable in the DHF) | record | Software Release Package; Release Checklist | [IEC 62304:2006+AMD1:2015 §5.8.1 + §5.8.3 + §5.8.7](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-014) | — | GAP |
| [`OBL-62304-018` · Software Configuration Management](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-018) | Establish a Configuration Management Plan (may be part of SDP) | plan | Configuration Management Plan; Software Development Plan | [IEC 62304:2006+AMD1:2015 §8.1.1 + §8.1.2](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-018) | — | GAP |
| [`OBL-13485-007` · Design Transfer Procedure](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-007) | Define and follow a documented design transfer procedure | process-record | Design Transfer Record; Release Package; Configuration Baseline | [ISO 13485:2016 §7.3.8](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-007) | — | GAP |
| [`OBL-13485-008` · Design Change Control](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-008) | Design changes must be reviewed, and as appropriate verified and validated, before implementation | change-record | Design Change Records; PCCP Change Records; ECO Records | [ISO 13485:2016 §7.3.9](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-008) | — | GAP |

### Design Reviews (1)

| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |
|----|-----------|---------------|------------------------|-----------|---------------|:------:|
| [`OBL-13485-004` · Design Reviews](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-004) | Conduct design reviews at planned stages per the DDP | review-record | Design Review Records; Phase Gate Records | [ISO 13485:2016 §7.3.5](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-004) | — | GAP |

### Human Factors (4)

| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |
|----|-----------|---------------|------------------------|-----------|---------------|:------:|
| [`OBL-62366-002` · Use Specification](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-002) | Identify and characterize the intended users for each use scenario | specification | Use Specification; Usability Engineering File | [IEC 62366-1:2015 §5.1.1](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-002) | — | GAP |
| [`OBL-62366-003` · User Profiles & Environments](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-003) | Document the intended use environment for each module | specification | Use Specification; Usability Engineering File | [IEC 62366-1:2015 §5.1.2](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-003) | — | GAP |
| [`OBL-62366-005` · User Interface Specification](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-005) | Establish a UI specification derived from the use specification and use-related risk analysis | specification | User Interface Specification; Software Requirements Specification | [IEC 62366-1:2015 §5.3](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-005) | — | GAP |
| [`OBL-62366-009` · UOUP Evaluation](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-009) | If third-party UI frameworks or pre-built components are used in the clinical interface, evaluate them under the UOUP process | analysis | UOUP Evaluation; Usability Engineering File | [IEC 62366-1:2015 §5.7](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-009) | — | GAP |

---

## cloud-suite
*System DHF — device-level, aggregates evidence from all item DHFs*  
**Obligations in this DHF**: 0

_No obligations scoped to this DHF under the current project scope vector._

---

## drug-library-manager
*SaMD · IEC 62304 Class B*  
**Obligations in this DHF**: 49

### Architecture (4)

| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |
|----|-----------|---------------|------------------------|-----------|---------------|:------:|
| [`OBL-62304-007` · Software Architecture Specification](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-007) | Produce a Software Architecture Document (SAD) transforming the SRS into a structural design | spec | Software Architecture Document | [IEC 62304:2006+AMD1:2015 §5.3.1](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-007) | — | GAP |
| [`OBL-62304-008` · SOUP Identification](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-008) | Identify all SOUP (Software of Unknown Provenance) items used in each software item | record | SOUP List; Software Architecture Document | [IEC 62304:2006+AMD1:2015 §5.3.3](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-008) | — | GAP |
| [`OBL-62304-009` · Architecture Verification](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-009) | Conduct and document an architecture verification that confirms all SRS requirements are addressed in the design | record | Software Architecture Document; Architecture Verification Record | [IEC 62304:2006+AMD1:2015 §5.3.4](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-009) | — | GAP |
| [`OBL-81001-004` · Secure Software Architecture](../../../.claude/skills/dhf-manifest/data/standards/iec-81001-5-1.md#OBL-81001-004) | Apply secure design principles in the SAD: defense in depth, least privilege, secure defaults, fail secure, minimize attack surface | design-document | Software Architecture Document; Security Architecture | [IEC 81001-5-1:2021 §5.3](../../../.claude/skills/dhf-manifest/data/standards/iec-81001-5-1.md#OBL-81001-004) | — | GAP |

### Requirements (6)

| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |
|----|-----------|---------------|------------------------|-----------|---------------|:------:|
| [`OBL-62304-004` · Software Requirements Specification](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-004) | Define software requirements traceable to system-level requirements | spec | Software Requirements Specification | [IEC 62304:2006+AMD1:2015 §5.2.1](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-004) | — | GAP |
| [`OBL-62304-005` · SRS Content Requirements](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-005) | SRS must cover: functional/capability requirements, I/O requirements, external interfaces | spec | Software Requirements Specification | [IEC 62304:2006+AMD1:2015 §5.2.2 + §5.2.3](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-005) | — | GAP |
| [`OBL-62304-006` · SRS Risk Control Trace](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-006) | Re-evaluate risk after SRS is established — update risk file if new hazards emerge | record | Software Requirements Specification; Risk Management File | [IEC 62304:2006+AMD1:2015 §5.2.6](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-006) | — | GAP |
| [`OBL-81001-003` · Security Requirements](../../../.claude/skills/dhf-manifest/data/standards/iec-81001-5-1.md#OBL-81001-003) | Derive security requirements from security risk assessment + FDA cybersecurity guidance + PHI/PII obligations | specification | Software Requirements Specification; Security Requirements | [IEC 81001-5-1:2021 §5.2](../../../.claude/skills/dhf-manifest/data/standards/iec-81001-5-1.md#OBL-81001-003) | — | GAP |
| [`OBL-82304-004` · Product Validation Execution](../../../.claude/skills/dhf-manifest/data/standards/iec-82304.md#OBL-82304-004) | Safety requirements must be derived from risk management (ISO 14971) activities — not authored independently | specification | Software Requirements Specification; Risk Control Requirements | [IEC 82304-1:2016 §5.2](../../../.claude/skills/dhf-manifest/data/standards/iec-82304.md#OBL-82304-004) | — | GAP |
| [`OBL-13485-002` · Design Input Documentation](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-002) | Document design inputs covering: functional, performance, and safety requirements | specification | Design Inputs Record; Software Requirements Specification; User Needs Document | [ISO 13485:2016 §7.3.3](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-002) | — | GAP |

### Design Outputs (2)

| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |
|----|-----------|---------------|------------------------|-----------|---------------|:------:|
| [`OBL-SWF-003` · SW Design Documentation](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-sw-functions.md#OBL-SWF-003) | For Enhanced documentation (MedTech Project): include Software Design Specification in the submission | submission-content | 510(k) Submission — Software Documentation (Enhanced); Software Design Document | [FDA SW Functions Guidance (2023) §V Required Documentation Elements](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-sw-functions.md#OBL-SWF-003) | — | GAP |
| [`OBL-13485-003` · Design Output Documentation](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-003) | Design outputs must demonstrably meet the design inputs — traceability is required | specification | Design Outputs Record; Software Architecture Document; Software Design Document | [ISO 13485:2016 §7.3.4](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-003) | — | GAP |

### Traceability (2)

| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |
|----|-----------|---------------|------------------------|-----------|---------------|:------:|
| [`OBL-62304-020` · Software Traceability](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-020) | Maintain bidirectional traceability: system requirements → software requirements → architecture → test cases | record | Trace Matrix; Software Development Plan | [IEC 62304:2006+AMD1:2015 §5.1.6(d)](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-020) | — | GAP |
| [`OBL-13485-009` · Design History File](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-009) | Maintain a Design History File (DHF) for each device type or family | dhf-file | Design History File; DHF README; DHF Manifest | [ISO 13485:2016 §7.3.10](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-009) | — | GAP |

### Risk Management (8)

| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |
|----|-----------|---------------|------------------------|-----------|---------------|:------:|
| [`OBL-62304-016` · Software Hazard Analysis](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-016) | For each hazardous situation in the risk file, identify which software items could contribute to it | record | Risk Management File; Software FMEA; Hazard Analysis | [IEC 62304:2006+AMD1:2015 §7.1.1](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-016) | — | GAP |
| [`OBL-62304-017` · SOUP Risk Evaluation](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-017) | For each SOUP item, obtain and review the supplier's known anomaly list | record | Risk Management File; SOUP Risk Evaluation | [IEC 62304:2006+AMD1:2015 §7.1.3](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-017) | — | GAP |
| [`OBL-14971-007` · Hazard Identification](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-007) | Identify all foreseeable hazards (energy, biology, data, software, mechanical, chemical, etc.) | record | Preliminary Hazard Analysis; Hazard Analysis; Risk Management File | [ISO 14971:2019 §5.4](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-007) | — | GAP |
| [`OBL-14971-008` · Risk Estimation](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-008) | Estimate risk for each hazardous situation using severity × probability from the risk matrix in the plan | record | Risk Assessment / FMEA; Risk Management File | [ISO 14971:2019 §5.5](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-008) | — | GAP |
| [`OBL-14971-009` · Risk Evaluation](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-009) | Apply the risk matrix from the plan to each estimated risk — classify as acceptable / ALARP / unacceptable | record | Risk Assessment / FMEA; Risk Management File | [ISO 14971:2019 §6](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-009) | — | GAP |
| [`OBL-14971-010` · Risk Control Options](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-010) | Apply risk controls in priority order: (1) design-level elimination, (2) device protective measure, (3) information/labeling | record | Risk Control Measures; Risk Management File | [ISO 14971:2019 §7.1](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-010) | — | GAP |
| [`OBL-14971-011` · Risk Control Verification](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-011) | Verify that each risk control measure is implemented as specified (implementation verification record) | record | Risk Control Measures; Verification Records; Risk Management File | [ISO 14971:2019 §7.2 + §7.3](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-011) | — | GAP |
| [`OBL-14971-013` · Secondary Hazard Evaluation](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-013) | After applying each risk control, evaluate whether the control creates new hazards (secondary hazards) | record | Risk Management File | [ISO 14971:2019 §7.5 + §7.6](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-013) | — | GAP |

### Verification (6)

| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |
|----|-----------|---------------|------------------------|-----------|---------------|:------:|
| [`OBL-SWF-005` · SW Testing Documentation](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-sw-functions.md#OBL-SWF-005) | For Enhanced documentation (MedTech Project): submit complete test protocols and reports at unit, integration, AND system levels | submission-content | 510(k) Submission — Software Testing; Test Protocols and Reports | [FDA SW Functions Guidance (2023) §V Required Documentation Elements](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-sw-functions.md#OBL-SWF-005) | — | GAP |
| [`OBL-62304-011` · Unit Verification](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-011) | Verify each software unit through code review, unit testing, or both | record | Unit Verification Records; Code Review Records | [IEC 62304:2006+AMD1:2015 §5.5.2 + §5.5.3](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-011) | — | GAP |
| [`OBL-62304-012` · Integration Testing](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-012) | Produce an integration plan defining the sequence and method for integrating software items | protocol | Integration Test Plan; Integration Test Report | [IEC 62304:2006+AMD1:2015 §5.6.1 + §5.6.3](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-012) | — | GAP |
| [`OBL-62366-006` · UI Verification](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-006) | Verify the implemented user interface meets the UI specification requirements | test-report | UI Verification Report; V&V Plan | [IEC 62366-1:2015 §5.5](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-006) | — | GAP |
| [`OBL-81001-006` · Secure Implementation Practices](../../../.claude/skills/dhf-manifest/data/standards/iec-81001-5-1.md#OBL-81001-006) | Conduct system-level security testing before release: vulnerability scanning, penetration testing | test-report | Security Test Report; V&V Plan | [IEC 81001-5-1:2021 §5.7](../../../.claude/skills/dhf-manifest/data/standards/iec-81001-5-1.md#OBL-81001-006) | — | GAP |
| [`OBL-13485-005` · Design Verification Planning](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-005) | Plan design verification at each development stage per the DDP | test-report | Verification Plan; Verification Reports; V&V Plan | [ISO 13485:2016 §7.3.6](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-005) | — | GAP |

### Validation (2)

| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |
|----|-----------|---------------|------------------------|-----------|---------------|:------:|
| [`OBL-62304-013` · System Testing](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-013) | Test the complete integrated software system against every SRS requirement | protocol | Software System Test Plan; Software System Test Report | [IEC 62304:2006+AMD1:2015 §5.7.1 + §5.7.3](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-013) | — | GAP |
| [`OBL-62366-007` · Formative Usability Evaluation](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-007) | Conduct iterative formative usability evaluations during design | test-report | Formative Evaluation Reports; Usability Engineering File | [IEC 62366-1:2015 §5.6](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-007) | — | GAP |

### Software Lifecycle (10)

| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |
|----|-----------|---------------|------------------------|-----------|---------------|:------:|
| [`OBL-SWF-004` · SW Lifecycle Documentation](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-sw-functions.md#OBL-SWF-004) | Option 1 (preferred): Submit a Declaration of Conformity to IEC 62304 — this substitutes for the SW development practices documentation section | submission-content | 510(k) Submission — Software Documentation; IEC 62304 Declaration of Conformity | [FDA SW Functions Guidance (2023) §V Required Documentation Elements](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-sw-functions.md#OBL-SWF-004) | — | GAP |
| [`OBL-SWF-006` · Unresolved Anomalies List](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-sw-functions.md#OBL-SWF-006) | Include software version history from first version under design controls to the final released version | submission-content | 510(k) Submission — Software Documentation; Unresolved Anomalies List | [FDA SW Functions Guidance (2023) §V Required Documentation Elements](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-sw-functions.md#OBL-SWF-006) | — | GAP |
| [`OBL-62304-001` · Software Safety Classification](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-001) | Assign IEC 62304 safety class (A, B, or C) to each software item before development begins | record | Safety Classification Record; Software Development Plan | [IEC 62304:2006+AMD1:2015 §4.3](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-001) | — | GAP |
| [`OBL-62304-002` · Software Development Plan](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-002) | Establish a Software Development Plan (SDP) before beginning software development | plan | Software Development Plan; Design and Development Plan | [IEC 62304:2006+AMD1:2015 §5.1.1](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-002) | — | GAP |
| [`OBL-62304-003` · SDP Content & Lifecycle](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-003) | SDP must define the SDLC model (waterfall, iterative, agile-within-waterfall, etc.) | plan | Software Development Plan | [IEC 62304:2006+AMD1:2015 §5.1.2 + §5.1.3](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-003) | — | GAP |
| [`OBL-81001-002` · Secure Development Plan](../../../.claude/skills/dhf-manifest/data/standards/iec-81001-5-1.md#OBL-81001-002) | Include security activities in the SDP: threat modeling, secure design, security testing, vulnerability management | plan | Software Development Plan; Cybersecurity Plan | [IEC 81001-5-1:2021 §5.1](../../../.claude/skills/dhf-manifest/data/standards/iec-81001-5-1.md#OBL-81001-002) | — | GAP |
| [`OBL-81001-005` · Secure Detailed Design](../../../.claude/skills/dhf-manifest/data/standards/iec-81001-5-1.md#OBL-81001-005) | Follow a defined secure coding standard (e.g., OWASP, CERT C, or equivalent) | process-record | Secure Coding Standard; SOUP List; Software Development Process Records | [IEC 81001-5-1:2021 §5.5](../../../.claude/skills/dhf-manifest/data/standards/iec-81001-5-1.md#OBL-81001-005) | — | GAP |
| [`OBL-82304-002` · Safety Requirements Specification](../../../.claude/skills/dhf-manifest/data/standards/iec-82304.md#OBL-82304-002) | All software development activities must conform to IEC 62304 | process-record | Software Development Plan; IEC 62304 Conformance Records | [IEC 82304-1:2016 §4.3](../../../.claude/skills/dhf-manifest/data/standards/iec-82304.md#OBL-82304-002) | — | GAP |
| [`OBL-13485-001` · Design & Development Planning](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-001) | Document the stages of design and development with defined entry/exit criteria | plan | Design and Development Plan; Software Development Plan | [ISO 13485:2016 §7.3.2](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-001) | — | GAP |
| [`OBL-13485-010` · SOUP Supplier Qualification](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-010) | Evaluate and qualify SOUP/third-party software components as suppliers (for IEC 62304 Class B/C, SOUP evaluation is also an IEC 62304 §8.1.2 obligation) | process-record | SOUP List; Supplier Qualification Records; Approved Supplier List | [ISO 13485:2016 §7.4.1](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-010) | — | GAP |

### Configuration & Change Control (4)

| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |
|----|-----------|---------------|------------------------|-----------|---------------|:------:|
| [`OBL-62304-014` · Software Release](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-014) | Assign a unique version identifier to the released software (must be traceable in the DHF) | record | Software Release Package; Release Checklist | [IEC 62304:2006+AMD1:2015 §5.8.1 + §5.8.3 + §5.8.7](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-014) | — | GAP |
| [`OBL-62304-018` · Software Configuration Management](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-018) | Establish a Configuration Management Plan (may be part of SDP) | plan | Configuration Management Plan; Software Development Plan | [IEC 62304:2006+AMD1:2015 §8.1.1 + §8.1.2](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-018) | — | GAP |
| [`OBL-13485-007` · Design Transfer Procedure](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-007) | Define and follow a documented design transfer procedure | process-record | Design Transfer Record; Release Package; Configuration Baseline | [ISO 13485:2016 §7.3.8](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-007) | — | GAP |
| [`OBL-13485-008` · Design Change Control](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-008) | Design changes must be reviewed, and as appropriate verified and validated, before implementation | change-record | Design Change Records; PCCP Change Records; ECO Records | [ISO 13485:2016 §7.3.9](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-008) | — | GAP |

### Design Reviews (1)

| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |
|----|-----------|---------------|------------------------|-----------|---------------|:------:|
| [`OBL-13485-004` · Design Reviews](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-004) | Conduct design reviews at planned stages per the DDP | review-record | Design Review Records; Phase Gate Records | [ISO 13485:2016 §7.3.5](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-004) | — | GAP |

### Human Factors (4)

| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |
|----|-----------|---------------|------------------------|-----------|---------------|:------:|
| [`OBL-62366-002` · Use Specification](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-002) | Identify and characterize the intended users for each use scenario | specification | Use Specification; Usability Engineering File | [IEC 62366-1:2015 §5.1.1](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-002) | — | GAP |
| [`OBL-62366-003` · User Profiles & Environments](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-003) | Document the intended use environment for each module | specification | Use Specification; Usability Engineering File | [IEC 62366-1:2015 §5.1.2](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-003) | — | GAP |
| [`OBL-62366-005` · User Interface Specification](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-005) | Establish a UI specification derived from the use specification and use-related risk analysis | specification | User Interface Specification; Software Requirements Specification | [IEC 62366-1:2015 §5.3](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-005) | — | GAP |
| [`OBL-62366-009` · UOUP Evaluation](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-009) | If third-party UI frameworks or pre-built components are used in the clinical interface, evaluate them under the UOUP process | analysis | UOUP Evaluation; Usability Engineering File | [IEC 62366-1:2015 §5.7](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-009) | — | GAP |

---

## fleet-management
*Non-SaMD · IEC 62304 Class A*  
**Obligations in this DHF**: 41

### Architecture (1)

| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |
|----|-----------|---------------|------------------------|-----------|---------------|:------:|
| [`OBL-81001-004` · Secure Software Architecture](../../../.claude/skills/dhf-manifest/data/standards/iec-81001-5-1.md#OBL-81001-004) | Apply secure design principles in the SAD: defense in depth, least privilege, secure defaults, fail secure, minimize attack surface | design-document | Software Architecture Document; Security Architecture | [IEC 81001-5-1:2021 §5.3](../../../.claude/skills/dhf-manifest/data/standards/iec-81001-5-1.md#OBL-81001-004) | — | GAP |

### Requirements (6)

| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |
|----|-----------|---------------|------------------------|-----------|---------------|:------:|
| [`OBL-62304-004` · Software Requirements Specification](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-004) | Define software requirements traceable to system-level requirements | spec | Software Requirements Specification | [IEC 62304:2006+AMD1:2015 §5.2.1](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-004) | — | GAP |
| [`OBL-62304-005` · SRS Content Requirements](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-005) | SRS must cover: functional/capability requirements, I/O requirements, external interfaces | spec | Software Requirements Specification | [IEC 62304:2006+AMD1:2015 §5.2.2 + §5.2.3](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-005) | — | GAP |
| [`OBL-62304-006` · SRS Risk Control Trace](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-006) | Re-evaluate risk after SRS is established — update risk file if new hazards emerge | record | Software Requirements Specification; Risk Management File | [IEC 62304:2006+AMD1:2015 §5.2.6](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-006) | — | GAP |
| [`OBL-81001-003` · Security Requirements](../../../.claude/skills/dhf-manifest/data/standards/iec-81001-5-1.md#OBL-81001-003) | Derive security requirements from security risk assessment + FDA cybersecurity guidance + PHI/PII obligations | specification | Software Requirements Specification; Security Requirements | [IEC 81001-5-1:2021 §5.2](../../../.claude/skills/dhf-manifest/data/standards/iec-81001-5-1.md#OBL-81001-003) | — | GAP |
| [`OBL-82304-004` · Product Validation Execution](../../../.claude/skills/dhf-manifest/data/standards/iec-82304.md#OBL-82304-004) | Safety requirements must be derived from risk management (ISO 14971) activities — not authored independently | specification | Software Requirements Specification; Risk Control Requirements | [IEC 82304-1:2016 §5.2](../../../.claude/skills/dhf-manifest/data/standards/iec-82304.md#OBL-82304-004) | — | GAP |
| [`OBL-13485-002` · Design Input Documentation](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-002) | Document design inputs covering: functional, performance, and safety requirements | specification | Design Inputs Record; Software Requirements Specification; User Needs Document | [ISO 13485:2016 §7.3.3](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-002) | — | GAP |

### Design Outputs (2)

| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |
|----|-----------|---------------|------------------------|-----------|---------------|:------:|
| [`OBL-SWF-003` · SW Design Documentation](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-sw-functions.md#OBL-SWF-003) | For Enhanced documentation (MedTech Project): include Software Design Specification in the submission | submission-content | 510(k) Submission — Software Documentation (Enhanced); Software Design Document | [FDA SW Functions Guidance (2023) §V Required Documentation Elements](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-sw-functions.md#OBL-SWF-003) | — | GAP |
| [`OBL-13485-003` · Design Output Documentation](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-003) | Design outputs must demonstrably meet the design inputs — traceability is required | specification | Design Outputs Record; Software Architecture Document; Software Design Document | [ISO 13485:2016 §7.3.4](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-003) | — | GAP |

### Traceability (2)

| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |
|----|-----------|---------------|------------------------|-----------|---------------|:------:|
| [`OBL-62304-020` · Software Traceability](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-020) | Maintain bidirectional traceability: system requirements → software requirements → architecture → test cases | record | Trace Matrix; Software Development Plan | [IEC 62304:2006+AMD1:2015 §5.1.6(d)](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-020) | — | GAP |
| [`OBL-13485-009` · Design History File](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-009) | Maintain a Design History File (DHF) for each device type or family | dhf-file | Design History File; DHF README; DHF Manifest | [ISO 13485:2016 §7.3.10](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-009) | — | GAP |

### Risk Management (6)

| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |
|----|-----------|---------------|------------------------|-----------|---------------|:------:|
| [`OBL-14971-007` · Hazard Identification](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-007) | Identify all foreseeable hazards (energy, biology, data, software, mechanical, chemical, etc.) | record | Preliminary Hazard Analysis; Hazard Analysis; Risk Management File | [ISO 14971:2019 §5.4](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-007) | — | GAP |
| [`OBL-14971-008` · Risk Estimation](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-008) | Estimate risk for each hazardous situation using severity × probability from the risk matrix in the plan | record | Risk Assessment / FMEA; Risk Management File | [ISO 14971:2019 §5.5](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-008) | — | GAP |
| [`OBL-14971-009` · Risk Evaluation](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-009) | Apply the risk matrix from the plan to each estimated risk — classify as acceptable / ALARP / unacceptable | record | Risk Assessment / FMEA; Risk Management File | [ISO 14971:2019 §6](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-009) | — | GAP |
| [`OBL-14971-010` · Risk Control Options](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-010) | Apply risk controls in priority order: (1) design-level elimination, (2) device protective measure, (3) information/labeling | record | Risk Control Measures; Risk Management File | [ISO 14971:2019 §7.1](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-010) | — | GAP |
| [`OBL-14971-011` · Risk Control Verification](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-011) | Verify that each risk control measure is implemented as specified (implementation verification record) | record | Risk Control Measures; Verification Records; Risk Management File | [ISO 14971:2019 §7.2 + §7.3](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-011) | — | GAP |
| [`OBL-14971-013` · Secondary Hazard Evaluation](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-013) | After applying each risk control, evaluate whether the control creates new hazards (secondary hazards) | record | Risk Management File | [ISO 14971:2019 §7.5 + §7.6](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-013) | — | GAP |

### Verification (4)

| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |
|----|-----------|---------------|------------------------|-----------|---------------|:------:|
| [`OBL-SWF-005` · SW Testing Documentation](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-sw-functions.md#OBL-SWF-005) | For Enhanced documentation (MedTech Project): submit complete test protocols and reports at unit, integration, AND system levels | submission-content | 510(k) Submission — Software Testing; Test Protocols and Reports | [FDA SW Functions Guidance (2023) §V Required Documentation Elements](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-sw-functions.md#OBL-SWF-005) | — | GAP |
| [`OBL-62366-006` · UI Verification](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-006) | Verify the implemented user interface meets the UI specification requirements | test-report | UI Verification Report; V&V Plan | [IEC 62366-1:2015 §5.5](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-006) | — | GAP |
| [`OBL-81001-006` · Secure Implementation Practices](../../../.claude/skills/dhf-manifest/data/standards/iec-81001-5-1.md#OBL-81001-006) | Conduct system-level security testing before release: vulnerability scanning, penetration testing | test-report | Security Test Report; V&V Plan | [IEC 81001-5-1:2021 §5.7](../../../.claude/skills/dhf-manifest/data/standards/iec-81001-5-1.md#OBL-81001-006) | — | GAP |
| [`OBL-13485-005` · Design Verification Planning](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-005) | Plan design verification at each development stage per the DDP | test-report | Verification Plan; Verification Reports; V&V Plan | [ISO 13485:2016 §7.3.6](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-005) | — | GAP |

### Validation (2)

| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |
|----|-----------|---------------|------------------------|-----------|---------------|:------:|
| [`OBL-62304-013` · System Testing](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-013) | Test the complete integrated software system against every SRS requirement | protocol | Software System Test Plan; Software System Test Report | [IEC 62304:2006+AMD1:2015 §5.7.1 + §5.7.3](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-013) | — | GAP |
| [`OBL-62366-007` · Formative Usability Evaluation](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-007) | Conduct iterative formative usability evaluations during design | test-report | Formative Evaluation Reports; Usability Engineering File | [IEC 62366-1:2015 §5.6](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-007) | — | GAP |

### Software Lifecycle (10)

| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |
|----|-----------|---------------|------------------------|-----------|---------------|:------:|
| [`OBL-SWF-004` · SW Lifecycle Documentation](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-sw-functions.md#OBL-SWF-004) | Option 1 (preferred): Submit a Declaration of Conformity to IEC 62304 — this substitutes for the SW development practices documentation section | submission-content | 510(k) Submission — Software Documentation; IEC 62304 Declaration of Conformity | [FDA SW Functions Guidance (2023) §V Required Documentation Elements](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-sw-functions.md#OBL-SWF-004) | — | GAP |
| [`OBL-SWF-006` · Unresolved Anomalies List](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-sw-functions.md#OBL-SWF-006) | Include software version history from first version under design controls to the final released version | submission-content | 510(k) Submission — Software Documentation; Unresolved Anomalies List | [FDA SW Functions Guidance (2023) §V Required Documentation Elements](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-sw-functions.md#OBL-SWF-006) | — | GAP |
| [`OBL-62304-001` · Software Safety Classification](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-001) | Assign IEC 62304 safety class (A, B, or C) to each software item before development begins | record | Safety Classification Record; Software Development Plan | [IEC 62304:2006+AMD1:2015 §4.3](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-001) | — | GAP |
| [`OBL-62304-002` · Software Development Plan](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-002) | Establish a Software Development Plan (SDP) before beginning software development | plan | Software Development Plan; Design and Development Plan | [IEC 62304:2006+AMD1:2015 §5.1.1](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-002) | — | GAP |
| [`OBL-62304-003` · SDP Content & Lifecycle](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-003) | SDP must define the SDLC model (waterfall, iterative, agile-within-waterfall, etc.) | plan | Software Development Plan | [IEC 62304:2006+AMD1:2015 §5.1.2 + §5.1.3](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-003) | — | GAP |
| [`OBL-81001-002` · Secure Development Plan](../../../.claude/skills/dhf-manifest/data/standards/iec-81001-5-1.md#OBL-81001-002) | Include security activities in the SDP: threat modeling, secure design, security testing, vulnerability management | plan | Software Development Plan; Cybersecurity Plan | [IEC 81001-5-1:2021 §5.1](../../../.claude/skills/dhf-manifest/data/standards/iec-81001-5-1.md#OBL-81001-002) | — | GAP |
| [`OBL-81001-005` · Secure Detailed Design](../../../.claude/skills/dhf-manifest/data/standards/iec-81001-5-1.md#OBL-81001-005) | Follow a defined secure coding standard (e.g., OWASP, CERT C, or equivalent) | process-record | Secure Coding Standard; SOUP List; Software Development Process Records | [IEC 81001-5-1:2021 §5.5](../../../.claude/skills/dhf-manifest/data/standards/iec-81001-5-1.md#OBL-81001-005) | — | GAP |
| [`OBL-82304-002` · Safety Requirements Specification](../../../.claude/skills/dhf-manifest/data/standards/iec-82304.md#OBL-82304-002) | All software development activities must conform to IEC 62304 | process-record | Software Development Plan; IEC 62304 Conformance Records | [IEC 82304-1:2016 §4.3](../../../.claude/skills/dhf-manifest/data/standards/iec-82304.md#OBL-82304-002) | — | GAP |
| [`OBL-13485-001` · Design & Development Planning](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-001) | Document the stages of design and development with defined entry/exit criteria | plan | Design and Development Plan; Software Development Plan | [ISO 13485:2016 §7.3.2](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-001) | — | GAP |
| [`OBL-13485-010` · SOUP Supplier Qualification](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-010) | Evaluate and qualify SOUP/third-party software components as suppliers (for IEC 62304 Class B/C, SOUP evaluation is also an IEC 62304 §8.1.2 obligation) | process-record | SOUP List; Supplier Qualification Records; Approved Supplier List | [ISO 13485:2016 §7.4.1](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-010) | — | GAP |

### Configuration & Change Control (3)

| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |
|----|-----------|---------------|------------------------|-----------|---------------|:------:|
| [`OBL-62304-014` · Software Release](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-014) | Assign a unique version identifier to the released software (must be traceable in the DHF) | record | Software Release Package; Release Checklist | [IEC 62304:2006+AMD1:2015 §5.8.1 + §5.8.3 + §5.8.7](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-014) | — | GAP |
| [`OBL-13485-007` · Design Transfer Procedure](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-007) | Define and follow a documented design transfer procedure | process-record | Design Transfer Record; Release Package; Configuration Baseline | [ISO 13485:2016 §7.3.8](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-007) | — | GAP |
| [`OBL-13485-008` · Design Change Control](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-008) | Design changes must be reviewed, and as appropriate verified and validated, before implementation | change-record | Design Change Records; PCCP Change Records; ECO Records | [ISO 13485:2016 §7.3.9](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-008) | — | GAP |

### Design Reviews (1)

| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |
|----|-----------|---------------|------------------------|-----------|---------------|:------:|
| [`OBL-13485-004` · Design Reviews](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-004) | Conduct design reviews at planned stages per the DDP | review-record | Design Review Records; Phase Gate Records | [ISO 13485:2016 §7.3.5](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-004) | — | GAP |

### Human Factors (4)

| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |
|----|-----------|---------------|------------------------|-----------|---------------|:------:|
| [`OBL-62366-002` · Use Specification](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-002) | Identify and characterize the intended users for each use scenario | specification | Use Specification; Usability Engineering File | [IEC 62366-1:2015 §5.1.1](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-002) | — | GAP |
| [`OBL-62366-003` · User Profiles & Environments](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-003) | Document the intended use environment for each module | specification | Use Specification; Usability Engineering File | [IEC 62366-1:2015 §5.1.2](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-003) | — | GAP |
| [`OBL-62366-005` · User Interface Specification](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-005) | Establish a UI specification derived from the use specification and use-related risk analysis | specification | User Interface Specification; Software Requirements Specification | [IEC 62366-1:2015 §5.3](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-005) | — | GAP |
| [`OBL-62366-009` · UOUP Evaluation](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-009) | If third-party UI frameworks or pre-built components are used in the clinical interface, evaluate them under the UOUP process | analysis | UOUP Evaluation; Usability Engineering File | [IEC 62366-1:2015 §5.7](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-009) | — | GAP |

---

## compliance-reports
*Non-SaMD · IEC 62304 Class A*  
**Obligations in this DHF**: 41

### Architecture (1)

| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |
|----|-----------|---------------|------------------------|-----------|---------------|:------:|
| [`OBL-81001-004` · Secure Software Architecture](../../../.claude/skills/dhf-manifest/data/standards/iec-81001-5-1.md#OBL-81001-004) | Apply secure design principles in the SAD: defense in depth, least privilege, secure defaults, fail secure, minimize attack surface | design-document | Software Architecture Document; Security Architecture | [IEC 81001-5-1:2021 §5.3](../../../.claude/skills/dhf-manifest/data/standards/iec-81001-5-1.md#OBL-81001-004) | — | GAP |

### Requirements (6)

| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |
|----|-----------|---------------|------------------------|-----------|---------------|:------:|
| [`OBL-62304-004` · Software Requirements Specification](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-004) | Define software requirements traceable to system-level requirements | spec | Software Requirements Specification | [IEC 62304:2006+AMD1:2015 §5.2.1](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-004) | — | GAP |
| [`OBL-62304-005` · SRS Content Requirements](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-005) | SRS must cover: functional/capability requirements, I/O requirements, external interfaces | spec | Software Requirements Specification | [IEC 62304:2006+AMD1:2015 §5.2.2 + §5.2.3](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-005) | — | GAP |
| [`OBL-62304-006` · SRS Risk Control Trace](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-006) | Re-evaluate risk after SRS is established — update risk file if new hazards emerge | record | Software Requirements Specification; Risk Management File | [IEC 62304:2006+AMD1:2015 §5.2.6](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-006) | — | GAP |
| [`OBL-81001-003` · Security Requirements](../../../.claude/skills/dhf-manifest/data/standards/iec-81001-5-1.md#OBL-81001-003) | Derive security requirements from security risk assessment + FDA cybersecurity guidance + PHI/PII obligations | specification | Software Requirements Specification; Security Requirements | [IEC 81001-5-1:2021 §5.2](../../../.claude/skills/dhf-manifest/data/standards/iec-81001-5-1.md#OBL-81001-003) | — | GAP |
| [`OBL-82304-004` · Product Validation Execution](../../../.claude/skills/dhf-manifest/data/standards/iec-82304.md#OBL-82304-004) | Safety requirements must be derived from risk management (ISO 14971) activities — not authored independently | specification | Software Requirements Specification; Risk Control Requirements | [IEC 82304-1:2016 §5.2](../../../.claude/skills/dhf-manifest/data/standards/iec-82304.md#OBL-82304-004) | — | GAP |
| [`OBL-13485-002` · Design Input Documentation](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-002) | Document design inputs covering: functional, performance, and safety requirements | specification | Design Inputs Record; Software Requirements Specification; User Needs Document | [ISO 13485:2016 §7.3.3](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-002) | — | GAP |

### Design Outputs (2)

| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |
|----|-----------|---------------|------------------------|-----------|---------------|:------:|
| [`OBL-SWF-003` · SW Design Documentation](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-sw-functions.md#OBL-SWF-003) | For Enhanced documentation (MedTech Project): include Software Design Specification in the submission | submission-content | 510(k) Submission — Software Documentation (Enhanced); Software Design Document | [FDA SW Functions Guidance (2023) §V Required Documentation Elements](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-sw-functions.md#OBL-SWF-003) | — | GAP |
| [`OBL-13485-003` · Design Output Documentation](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-003) | Design outputs must demonstrably meet the design inputs — traceability is required | specification | Design Outputs Record; Software Architecture Document; Software Design Document | [ISO 13485:2016 §7.3.4](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-003) | — | GAP |

### Traceability (2)

| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |
|----|-----------|---------------|------------------------|-----------|---------------|:------:|
| [`OBL-62304-020` · Software Traceability](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-020) | Maintain bidirectional traceability: system requirements → software requirements → architecture → test cases | record | Trace Matrix; Software Development Plan | [IEC 62304:2006+AMD1:2015 §5.1.6(d)](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-020) | — | GAP |
| [`OBL-13485-009` · Design History File](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-009) | Maintain a Design History File (DHF) for each device type or family | dhf-file | Design History File; DHF README; DHF Manifest | [ISO 13485:2016 §7.3.10](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-009) | — | GAP |

### Risk Management (6)

| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |
|----|-----------|---------------|------------------------|-----------|---------------|:------:|
| [`OBL-14971-007` · Hazard Identification](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-007) | Identify all foreseeable hazards (energy, biology, data, software, mechanical, chemical, etc.) | record | Preliminary Hazard Analysis; Hazard Analysis; Risk Management File | [ISO 14971:2019 §5.4](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-007) | — | GAP |
| [`OBL-14971-008` · Risk Estimation](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-008) | Estimate risk for each hazardous situation using severity × probability from the risk matrix in the plan | record | Risk Assessment / FMEA; Risk Management File | [ISO 14971:2019 §5.5](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-008) | — | GAP |
| [`OBL-14971-009` · Risk Evaluation](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-009) | Apply the risk matrix from the plan to each estimated risk — classify as acceptable / ALARP / unacceptable | record | Risk Assessment / FMEA; Risk Management File | [ISO 14971:2019 §6](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-009) | — | GAP |
| [`OBL-14971-010` · Risk Control Options](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-010) | Apply risk controls in priority order: (1) design-level elimination, (2) device protective measure, (3) information/labeling | record | Risk Control Measures; Risk Management File | [ISO 14971:2019 §7.1](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-010) | — | GAP |
| [`OBL-14971-011` · Risk Control Verification](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-011) | Verify that each risk control measure is implemented as specified (implementation verification record) | record | Risk Control Measures; Verification Records; Risk Management File | [ISO 14971:2019 §7.2 + §7.3](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-011) | — | GAP |
| [`OBL-14971-013` · Secondary Hazard Evaluation](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-013) | After applying each risk control, evaluate whether the control creates new hazards (secondary hazards) | record | Risk Management File | [ISO 14971:2019 §7.5 + §7.6](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-013) | — | GAP |

### Verification (4)

| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |
|----|-----------|---------------|------------------------|-----------|---------------|:------:|
| [`OBL-SWF-005` · SW Testing Documentation](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-sw-functions.md#OBL-SWF-005) | For Enhanced documentation (MedTech Project): submit complete test protocols and reports at unit, integration, AND system levels | submission-content | 510(k) Submission — Software Testing; Test Protocols and Reports | [FDA SW Functions Guidance (2023) §V Required Documentation Elements](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-sw-functions.md#OBL-SWF-005) | — | GAP |
| [`OBL-62366-006` · UI Verification](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-006) | Verify the implemented user interface meets the UI specification requirements | test-report | UI Verification Report; V&V Plan | [IEC 62366-1:2015 §5.5](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-006) | — | GAP |
| [`OBL-81001-006` · Secure Implementation Practices](../../../.claude/skills/dhf-manifest/data/standards/iec-81001-5-1.md#OBL-81001-006) | Conduct system-level security testing before release: vulnerability scanning, penetration testing | test-report | Security Test Report; V&V Plan | [IEC 81001-5-1:2021 §5.7](../../../.claude/skills/dhf-manifest/data/standards/iec-81001-5-1.md#OBL-81001-006) | — | GAP |
| [`OBL-13485-005` · Design Verification Planning](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-005) | Plan design verification at each development stage per the DDP | test-report | Verification Plan; Verification Reports; V&V Plan | [ISO 13485:2016 §7.3.6](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-005) | — | GAP |

### Validation (2)

| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |
|----|-----------|---------------|------------------------|-----------|---------------|:------:|
| [`OBL-62304-013` · System Testing](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-013) | Test the complete integrated software system against every SRS requirement | protocol | Software System Test Plan; Software System Test Report | [IEC 62304:2006+AMD1:2015 §5.7.1 + §5.7.3](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-013) | — | GAP |
| [`OBL-62366-007` · Formative Usability Evaluation](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-007) | Conduct iterative formative usability evaluations during design | test-report | Formative Evaluation Reports; Usability Engineering File | [IEC 62366-1:2015 §5.6](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-007) | — | GAP |

### Software Lifecycle (10)

| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |
|----|-----------|---------------|------------------------|-----------|---------------|:------:|
| [`OBL-SWF-004` · SW Lifecycle Documentation](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-sw-functions.md#OBL-SWF-004) | Option 1 (preferred): Submit a Declaration of Conformity to IEC 62304 — this substitutes for the SW development practices documentation section | submission-content | 510(k) Submission — Software Documentation; IEC 62304 Declaration of Conformity | [FDA SW Functions Guidance (2023) §V Required Documentation Elements](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-sw-functions.md#OBL-SWF-004) | — | GAP |
| [`OBL-SWF-006` · Unresolved Anomalies List](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-sw-functions.md#OBL-SWF-006) | Include software version history from first version under design controls to the final released version | submission-content | 510(k) Submission — Software Documentation; Unresolved Anomalies List | [FDA SW Functions Guidance (2023) §V Required Documentation Elements](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-sw-functions.md#OBL-SWF-006) | — | GAP |
| [`OBL-62304-001` · Software Safety Classification](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-001) | Assign IEC 62304 safety class (A, B, or C) to each software item before development begins | record | Safety Classification Record; Software Development Plan | [IEC 62304:2006+AMD1:2015 §4.3](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-001) | — | GAP |
| [`OBL-62304-002` · Software Development Plan](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-002) | Establish a Software Development Plan (SDP) before beginning software development | plan | Software Development Plan; Design and Development Plan | [IEC 62304:2006+AMD1:2015 §5.1.1](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-002) | — | GAP |
| [`OBL-62304-003` · SDP Content & Lifecycle](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-003) | SDP must define the SDLC model (waterfall, iterative, agile-within-waterfall, etc.) | plan | Software Development Plan | [IEC 62304:2006+AMD1:2015 §5.1.2 + §5.1.3](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-003) | — | GAP |
| [`OBL-81001-002` · Secure Development Plan](../../../.claude/skills/dhf-manifest/data/standards/iec-81001-5-1.md#OBL-81001-002) | Include security activities in the SDP: threat modeling, secure design, security testing, vulnerability management | plan | Software Development Plan; Cybersecurity Plan | [IEC 81001-5-1:2021 §5.1](../../../.claude/skills/dhf-manifest/data/standards/iec-81001-5-1.md#OBL-81001-002) | — | GAP |
| [`OBL-81001-005` · Secure Detailed Design](../../../.claude/skills/dhf-manifest/data/standards/iec-81001-5-1.md#OBL-81001-005) | Follow a defined secure coding standard (e.g., OWASP, CERT C, or equivalent) | process-record | Secure Coding Standard; SOUP List; Software Development Process Records | [IEC 81001-5-1:2021 §5.5](../../../.claude/skills/dhf-manifest/data/standards/iec-81001-5-1.md#OBL-81001-005) | — | GAP |
| [`OBL-82304-002` · Safety Requirements Specification](../../../.claude/skills/dhf-manifest/data/standards/iec-82304.md#OBL-82304-002) | All software development activities must conform to IEC 62304 | process-record | Software Development Plan; IEC 62304 Conformance Records | [IEC 82304-1:2016 §4.3](../../../.claude/skills/dhf-manifest/data/standards/iec-82304.md#OBL-82304-002) | — | GAP |
| [`OBL-13485-001` · Design & Development Planning](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-001) | Document the stages of design and development with defined entry/exit criteria | plan | Design and Development Plan; Software Development Plan | [ISO 13485:2016 §7.3.2](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-001) | — | GAP |
| [`OBL-13485-010` · SOUP Supplier Qualification](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-010) | Evaluate and qualify SOUP/third-party software components as suppliers (for IEC 62304 Class B/C, SOUP evaluation is also an IEC 62304 §8.1.2 obligation) | process-record | SOUP List; Supplier Qualification Records; Approved Supplier List | [ISO 13485:2016 §7.4.1](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-010) | — | GAP |

### Configuration & Change Control (3)

| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |
|----|-----------|---------------|------------------------|-----------|---------------|:------:|
| [`OBL-62304-014` · Software Release](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-014) | Assign a unique version identifier to the released software (must be traceable in the DHF) | record | Software Release Package; Release Checklist | [IEC 62304:2006+AMD1:2015 §5.8.1 + §5.8.3 + §5.8.7](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-014) | — | GAP |
| [`OBL-13485-007` · Design Transfer Procedure](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-007) | Define and follow a documented design transfer procedure | process-record | Design Transfer Record; Release Package; Configuration Baseline | [ISO 13485:2016 §7.3.8](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-007) | — | GAP |
| [`OBL-13485-008` · Design Change Control](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-008) | Design changes must be reviewed, and as appropriate verified and validated, before implementation | change-record | Design Change Records; PCCP Change Records; ECO Records | [ISO 13485:2016 §7.3.9](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-008) | — | GAP |

### Design Reviews (1)

| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |
|----|-----------|---------------|------------------------|-----------|---------------|:------:|
| [`OBL-13485-004` · Design Reviews](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-004) | Conduct design reviews at planned stages per the DDP | review-record | Design Review Records; Phase Gate Records | [ISO 13485:2016 §7.3.5](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-004) | — | GAP |

### Human Factors (4)

| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |
|----|-----------|---------------|------------------------|-----------|---------------|:------:|
| [`OBL-62366-002` · Use Specification](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-002) | Identify and characterize the intended users for each use scenario | specification | Use Specification; Usability Engineering File | [IEC 62366-1:2015 §5.1.1](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-002) | — | GAP |
| [`OBL-62366-003` · User Profiles & Environments](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-003) | Document the intended use environment for each module | specification | Use Specification; Usability Engineering File | [IEC 62366-1:2015 §5.1.2](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-003) | — | GAP |
| [`OBL-62366-005` · User Interface Specification](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-005) | Establish a UI specification derived from the use specification and use-related risk analysis | specification | User Interface Specification; Software Requirements Specification | [IEC 62366-1:2015 §5.3](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-005) | — | GAP |
| [`OBL-62366-009` · UOUP Evaluation](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-009) | If third-party UI frameworks or pre-built components are used in the clinical interface, evaluate them under the UOUP process | analysis | UOUP Evaluation; Usability Engineering File | [IEC 62366-1:2015 §5.7](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-009) | — | GAP |

---

## analytics-dashboard
*Non-SaMD · IEC 62304 Class A*  
**Obligations in this DHF**: 41

### Architecture (1)

| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |
|----|-----------|---------------|------------------------|-----------|---------------|:------:|
| [`OBL-81001-004` · Secure Software Architecture](../../../.claude/skills/dhf-manifest/data/standards/iec-81001-5-1.md#OBL-81001-004) | Apply secure design principles in the SAD: defense in depth, least privilege, secure defaults, fail secure, minimize attack surface | design-document | Software Architecture Document; Security Architecture | [IEC 81001-5-1:2021 §5.3](../../../.claude/skills/dhf-manifest/data/standards/iec-81001-5-1.md#OBL-81001-004) | — | GAP |

### Requirements (6)

| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |
|----|-----------|---------------|------------------------|-----------|---------------|:------:|
| [`OBL-62304-004` · Software Requirements Specification](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-004) | Define software requirements traceable to system-level requirements | spec | Software Requirements Specification | [IEC 62304:2006+AMD1:2015 §5.2.1](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-004) | — | GAP |
| [`OBL-62304-005` · SRS Content Requirements](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-005) | SRS must cover: functional/capability requirements, I/O requirements, external interfaces | spec | Software Requirements Specification | [IEC 62304:2006+AMD1:2015 §5.2.2 + §5.2.3](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-005) | — | GAP |
| [`OBL-62304-006` · SRS Risk Control Trace](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-006) | Re-evaluate risk after SRS is established — update risk file if new hazards emerge | record | Software Requirements Specification; Risk Management File | [IEC 62304:2006+AMD1:2015 §5.2.6](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-006) | — | GAP |
| [`OBL-81001-003` · Security Requirements](../../../.claude/skills/dhf-manifest/data/standards/iec-81001-5-1.md#OBL-81001-003) | Derive security requirements from security risk assessment + FDA cybersecurity guidance + PHI/PII obligations | specification | Software Requirements Specification; Security Requirements | [IEC 81001-5-1:2021 §5.2](../../../.claude/skills/dhf-manifest/data/standards/iec-81001-5-1.md#OBL-81001-003) | — | GAP |
| [`OBL-82304-004` · Product Validation Execution](../../../.claude/skills/dhf-manifest/data/standards/iec-82304.md#OBL-82304-004) | Safety requirements must be derived from risk management (ISO 14971) activities — not authored independently | specification | Software Requirements Specification; Risk Control Requirements | [IEC 82304-1:2016 §5.2](../../../.claude/skills/dhf-manifest/data/standards/iec-82304.md#OBL-82304-004) | — | GAP |
| [`OBL-13485-002` · Design Input Documentation](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-002) | Document design inputs covering: functional, performance, and safety requirements | specification | Design Inputs Record; Software Requirements Specification; User Needs Document | [ISO 13485:2016 §7.3.3](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-002) | — | GAP |

### Design Outputs (2)

| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |
|----|-----------|---------------|------------------------|-----------|---------------|:------:|
| [`OBL-SWF-003` · SW Design Documentation](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-sw-functions.md#OBL-SWF-003) | For Enhanced documentation (MedTech Project): include Software Design Specification in the submission | submission-content | 510(k) Submission — Software Documentation (Enhanced); Software Design Document | [FDA SW Functions Guidance (2023) §V Required Documentation Elements](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-sw-functions.md#OBL-SWF-003) | — | GAP |
| [`OBL-13485-003` · Design Output Documentation](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-003) | Design outputs must demonstrably meet the design inputs — traceability is required | specification | Design Outputs Record; Software Architecture Document; Software Design Document | [ISO 13485:2016 §7.3.4](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-003) | — | GAP |

### Traceability (2)

| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |
|----|-----------|---------------|------------------------|-----------|---------------|:------:|
| [`OBL-62304-020` · Software Traceability](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-020) | Maintain bidirectional traceability: system requirements → software requirements → architecture → test cases | record | Trace Matrix; Software Development Plan | [IEC 62304:2006+AMD1:2015 §5.1.6(d)](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-020) | — | GAP |
| [`OBL-13485-009` · Design History File](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-009) | Maintain a Design History File (DHF) for each device type or family | dhf-file | Design History File; DHF README; DHF Manifest | [ISO 13485:2016 §7.3.10](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-009) | — | GAP |

### Risk Management (6)

| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |
|----|-----------|---------------|------------------------|-----------|---------------|:------:|
| [`OBL-14971-007` · Hazard Identification](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-007) | Identify all foreseeable hazards (energy, biology, data, software, mechanical, chemical, etc.) | record | Preliminary Hazard Analysis; Hazard Analysis; Risk Management File | [ISO 14971:2019 §5.4](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-007) | — | GAP |
| [`OBL-14971-008` · Risk Estimation](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-008) | Estimate risk for each hazardous situation using severity × probability from the risk matrix in the plan | record | Risk Assessment / FMEA; Risk Management File | [ISO 14971:2019 §5.5](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-008) | — | GAP |
| [`OBL-14971-009` · Risk Evaluation](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-009) | Apply the risk matrix from the plan to each estimated risk — classify as acceptable / ALARP / unacceptable | record | Risk Assessment / FMEA; Risk Management File | [ISO 14971:2019 §6](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-009) | — | GAP |
| [`OBL-14971-010` · Risk Control Options](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-010) | Apply risk controls in priority order: (1) design-level elimination, (2) device protective measure, (3) information/labeling | record | Risk Control Measures; Risk Management File | [ISO 14971:2019 §7.1](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-010) | — | GAP |
| [`OBL-14971-011` · Risk Control Verification](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-011) | Verify that each risk control measure is implemented as specified (implementation verification record) | record | Risk Control Measures; Verification Records; Risk Management File | [ISO 14971:2019 §7.2 + §7.3](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-011) | — | GAP |
| [`OBL-14971-013` · Secondary Hazard Evaluation](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-013) | After applying each risk control, evaluate whether the control creates new hazards (secondary hazards) | record | Risk Management File | [ISO 14971:2019 §7.5 + §7.6](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-013) | — | GAP |

### Verification (4)

| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |
|----|-----------|---------------|------------------------|-----------|---------------|:------:|
| [`OBL-SWF-005` · SW Testing Documentation](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-sw-functions.md#OBL-SWF-005) | For Enhanced documentation (MedTech Project): submit complete test protocols and reports at unit, integration, AND system levels | submission-content | 510(k) Submission — Software Testing; Test Protocols and Reports | [FDA SW Functions Guidance (2023) §V Required Documentation Elements](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-sw-functions.md#OBL-SWF-005) | — | GAP |
| [`OBL-62366-006` · UI Verification](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-006) | Verify the implemented user interface meets the UI specification requirements | test-report | UI Verification Report; V&V Plan | [IEC 62366-1:2015 §5.5](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-006) | — | GAP |
| [`OBL-81001-006` · Secure Implementation Practices](../../../.claude/skills/dhf-manifest/data/standards/iec-81001-5-1.md#OBL-81001-006) | Conduct system-level security testing before release: vulnerability scanning, penetration testing | test-report | Security Test Report; V&V Plan | [IEC 81001-5-1:2021 §5.7](../../../.claude/skills/dhf-manifest/data/standards/iec-81001-5-1.md#OBL-81001-006) | — | GAP |
| [`OBL-13485-005` · Design Verification Planning](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-005) | Plan design verification at each development stage per the DDP | test-report | Verification Plan; Verification Reports; V&V Plan | [ISO 13485:2016 §7.3.6](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-005) | — | GAP |

### Validation (2)

| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |
|----|-----------|---------------|------------------------|-----------|---------------|:------:|
| [`OBL-62304-013` · System Testing](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-013) | Test the complete integrated software system against every SRS requirement | protocol | Software System Test Plan; Software System Test Report | [IEC 62304:2006+AMD1:2015 §5.7.1 + §5.7.3](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-013) | — | GAP |
| [`OBL-62366-007` · Formative Usability Evaluation](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-007) | Conduct iterative formative usability evaluations during design | test-report | Formative Evaluation Reports; Usability Engineering File | [IEC 62366-1:2015 §5.6](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-007) | — | GAP |

### Software Lifecycle (10)

| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |
|----|-----------|---------------|------------------------|-----------|---------------|:------:|
| [`OBL-SWF-004` · SW Lifecycle Documentation](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-sw-functions.md#OBL-SWF-004) | Option 1 (preferred): Submit a Declaration of Conformity to IEC 62304 — this substitutes for the SW development practices documentation section | submission-content | 510(k) Submission — Software Documentation; IEC 62304 Declaration of Conformity | [FDA SW Functions Guidance (2023) §V Required Documentation Elements](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-sw-functions.md#OBL-SWF-004) | — | GAP |
| [`OBL-SWF-006` · Unresolved Anomalies List](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-sw-functions.md#OBL-SWF-006) | Include software version history from first version under design controls to the final released version | submission-content | 510(k) Submission — Software Documentation; Unresolved Anomalies List | [FDA SW Functions Guidance (2023) §V Required Documentation Elements](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-sw-functions.md#OBL-SWF-006) | — | GAP |
| [`OBL-62304-001` · Software Safety Classification](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-001) | Assign IEC 62304 safety class (A, B, or C) to each software item before development begins | record | Safety Classification Record; Software Development Plan | [IEC 62304:2006+AMD1:2015 §4.3](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-001) | — | GAP |
| [`OBL-62304-002` · Software Development Plan](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-002) | Establish a Software Development Plan (SDP) before beginning software development | plan | Software Development Plan; Design and Development Plan | [IEC 62304:2006+AMD1:2015 §5.1.1](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-002) | — | GAP |
| [`OBL-62304-003` · SDP Content & Lifecycle](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-003) | SDP must define the SDLC model (waterfall, iterative, agile-within-waterfall, etc.) | plan | Software Development Plan | [IEC 62304:2006+AMD1:2015 §5.1.2 + §5.1.3](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-003) | — | GAP |
| [`OBL-81001-002` · Secure Development Plan](../../../.claude/skills/dhf-manifest/data/standards/iec-81001-5-1.md#OBL-81001-002) | Include security activities in the SDP: threat modeling, secure design, security testing, vulnerability management | plan | Software Development Plan; Cybersecurity Plan | [IEC 81001-5-1:2021 §5.1](../../../.claude/skills/dhf-manifest/data/standards/iec-81001-5-1.md#OBL-81001-002) | — | GAP |
| [`OBL-81001-005` · Secure Detailed Design](../../../.claude/skills/dhf-manifest/data/standards/iec-81001-5-1.md#OBL-81001-005) | Follow a defined secure coding standard (e.g., OWASP, CERT C, or equivalent) | process-record | Secure Coding Standard; SOUP List; Software Development Process Records | [IEC 81001-5-1:2021 §5.5](../../../.claude/skills/dhf-manifest/data/standards/iec-81001-5-1.md#OBL-81001-005) | — | GAP |
| [`OBL-82304-002` · Safety Requirements Specification](../../../.claude/skills/dhf-manifest/data/standards/iec-82304.md#OBL-82304-002) | All software development activities must conform to IEC 62304 | process-record | Software Development Plan; IEC 62304 Conformance Records | [IEC 82304-1:2016 §4.3](../../../.claude/skills/dhf-manifest/data/standards/iec-82304.md#OBL-82304-002) | — | GAP |
| [`OBL-13485-001` · Design & Development Planning](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-001) | Document the stages of design and development with defined entry/exit criteria | plan | Design and Development Plan; Software Development Plan | [ISO 13485:2016 §7.3.2](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-001) | — | GAP |
| [`OBL-13485-010` · SOUP Supplier Qualification](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-010) | Evaluate and qualify SOUP/third-party software components as suppliers (for IEC 62304 Class B/C, SOUP evaluation is also an IEC 62304 §8.1.2 obligation) | process-record | SOUP List; Supplier Qualification Records; Approved Supplier List | [ISO 13485:2016 §7.4.1](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-010) | — | GAP |

### Configuration & Change Control (3)

| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |
|----|-----------|---------------|------------------------|-----------|---------------|:------:|
| [`OBL-62304-014` · Software Release](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-014) | Assign a unique version identifier to the released software (must be traceable in the DHF) | record | Software Release Package; Release Checklist | [IEC 62304:2006+AMD1:2015 §5.8.1 + §5.8.3 + §5.8.7](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-014) | — | GAP |
| [`OBL-13485-007` · Design Transfer Procedure](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-007) | Define and follow a documented design transfer procedure | process-record | Design Transfer Record; Release Package; Configuration Baseline | [ISO 13485:2016 §7.3.8](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-007) | — | GAP |
| [`OBL-13485-008` · Design Change Control](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-008) | Design changes must be reviewed, and as appropriate verified and validated, before implementation | change-record | Design Change Records; PCCP Change Records; ECO Records | [ISO 13485:2016 §7.3.9](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-008) | — | GAP |

### Design Reviews (1)

| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |
|----|-----------|---------------|------------------------|-----------|---------------|:------:|
| [`OBL-13485-004` · Design Reviews](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-004) | Conduct design reviews at planned stages per the DDP | review-record | Design Review Records; Phase Gate Records | [ISO 13485:2016 §7.3.5](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-004) | — | GAP |

### Human Factors (4)

| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |
|----|-----------|---------------|------------------------|-----------|---------------|:------:|
| [`OBL-62366-002` · Use Specification](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-002) | Identify and characterize the intended users for each use scenario | specification | Use Specification; Usability Engineering File | [IEC 62366-1:2015 §5.1.1](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-002) | — | GAP |
| [`OBL-62366-003` · User Profiles & Environments](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-003) | Document the intended use environment for each module | specification | Use Specification; Usability Engineering File | [IEC 62366-1:2015 §5.1.2](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-003) | — | GAP |
| [`OBL-62366-005` · User Interface Specification](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-005) | Establish a UI specification derived from the use specification and use-related risk analysis | specification | User Interface Specification; Software Requirements Specification | [IEC 62366-1:2015 §5.3](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-005) | — | GAP |
| [`OBL-62366-009` · UOUP Evaluation](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-009) | If third-party UI frameworks or pre-built components are used in the clinical interface, evaluate them under the UOUP process | analysis | UOUP Evaluation; Usability Engineering File | [IEC 62366-1:2015 §5.7](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-009) | — | GAP |

---

## inventory-tracker
*Non-SaMD · IEC 62304 Class A*  
**Obligations in this DHF**: 41

### Architecture (1)

| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |
|----|-----------|---------------|------------------------|-----------|---------------|:------:|
| [`OBL-81001-004` · Secure Software Architecture](../../../.claude/skills/dhf-manifest/data/standards/iec-81001-5-1.md#OBL-81001-004) | Apply secure design principles in the SAD: defense in depth, least privilege, secure defaults, fail secure, minimize attack surface | design-document | Software Architecture Document; Security Architecture | [IEC 81001-5-1:2021 §5.3](../../../.claude/skills/dhf-manifest/data/standards/iec-81001-5-1.md#OBL-81001-004) | — | GAP |

### Requirements (6)

| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |
|----|-----------|---------------|------------------------|-----------|---------------|:------:|
| [`OBL-62304-004` · Software Requirements Specification](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-004) | Define software requirements traceable to system-level requirements | spec | Software Requirements Specification | [IEC 62304:2006+AMD1:2015 §5.2.1](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-004) | — | GAP |
| [`OBL-62304-005` · SRS Content Requirements](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-005) | SRS must cover: functional/capability requirements, I/O requirements, external interfaces | spec | Software Requirements Specification | [IEC 62304:2006+AMD1:2015 §5.2.2 + §5.2.3](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-005) | — | GAP |
| [`OBL-62304-006` · SRS Risk Control Trace](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-006) | Re-evaluate risk after SRS is established — update risk file if new hazards emerge | record | Software Requirements Specification; Risk Management File | [IEC 62304:2006+AMD1:2015 §5.2.6](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-006) | — | GAP |
| [`OBL-81001-003` · Security Requirements](../../../.claude/skills/dhf-manifest/data/standards/iec-81001-5-1.md#OBL-81001-003) | Derive security requirements from security risk assessment + FDA cybersecurity guidance + PHI/PII obligations | specification | Software Requirements Specification; Security Requirements | [IEC 81001-5-1:2021 §5.2](../../../.claude/skills/dhf-manifest/data/standards/iec-81001-5-1.md#OBL-81001-003) | — | GAP |
| [`OBL-82304-004` · Product Validation Execution](../../../.claude/skills/dhf-manifest/data/standards/iec-82304.md#OBL-82304-004) | Safety requirements must be derived from risk management (ISO 14971) activities — not authored independently | specification | Software Requirements Specification; Risk Control Requirements | [IEC 82304-1:2016 §5.2](../../../.claude/skills/dhf-manifest/data/standards/iec-82304.md#OBL-82304-004) | — | GAP |
| [`OBL-13485-002` · Design Input Documentation](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-002) | Document design inputs covering: functional, performance, and safety requirements | specification | Design Inputs Record; Software Requirements Specification; User Needs Document | [ISO 13485:2016 §7.3.3](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-002) | — | GAP |

### Design Outputs (2)

| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |
|----|-----------|---------------|------------------------|-----------|---------------|:------:|
| [`OBL-SWF-003` · SW Design Documentation](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-sw-functions.md#OBL-SWF-003) | For Enhanced documentation (MedTech Project): include Software Design Specification in the submission | submission-content | 510(k) Submission — Software Documentation (Enhanced); Software Design Document | [FDA SW Functions Guidance (2023) §V Required Documentation Elements](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-sw-functions.md#OBL-SWF-003) | — | GAP |
| [`OBL-13485-003` · Design Output Documentation](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-003) | Design outputs must demonstrably meet the design inputs — traceability is required | specification | Design Outputs Record; Software Architecture Document; Software Design Document | [ISO 13485:2016 §7.3.4](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-003) | — | GAP |

### Traceability (2)

| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |
|----|-----------|---------------|------------------------|-----------|---------------|:------:|
| [`OBL-62304-020` · Software Traceability](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-020) | Maintain bidirectional traceability: system requirements → software requirements → architecture → test cases | record | Trace Matrix; Software Development Plan | [IEC 62304:2006+AMD1:2015 §5.1.6(d)](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-020) | — | GAP |
| [`OBL-13485-009` · Design History File](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-009) | Maintain a Design History File (DHF) for each device type or family | dhf-file | Design History File; DHF README; DHF Manifest | [ISO 13485:2016 §7.3.10](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-009) | — | GAP |

### Risk Management (6)

| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |
|----|-----------|---------------|------------------------|-----------|---------------|:------:|
| [`OBL-14971-007` · Hazard Identification](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-007) | Identify all foreseeable hazards (energy, biology, data, software, mechanical, chemical, etc.) | record | Preliminary Hazard Analysis; Hazard Analysis; Risk Management File | [ISO 14971:2019 §5.4](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-007) | — | GAP |
| [`OBL-14971-008` · Risk Estimation](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-008) | Estimate risk for each hazardous situation using severity × probability from the risk matrix in the plan | record | Risk Assessment / FMEA; Risk Management File | [ISO 14971:2019 §5.5](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-008) | — | GAP |
| [`OBL-14971-009` · Risk Evaluation](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-009) | Apply the risk matrix from the plan to each estimated risk — classify as acceptable / ALARP / unacceptable | record | Risk Assessment / FMEA; Risk Management File | [ISO 14971:2019 §6](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-009) | — | GAP |
| [`OBL-14971-010` · Risk Control Options](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-010) | Apply risk controls in priority order: (1) design-level elimination, (2) device protective measure, (3) information/labeling | record | Risk Control Measures; Risk Management File | [ISO 14971:2019 §7.1](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-010) | — | GAP |
| [`OBL-14971-011` · Risk Control Verification](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-011) | Verify that each risk control measure is implemented as specified (implementation verification record) | record | Risk Control Measures; Verification Records; Risk Management File | [ISO 14971:2019 §7.2 + §7.3](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-011) | — | GAP |
| [`OBL-14971-013` · Secondary Hazard Evaluation](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-013) | After applying each risk control, evaluate whether the control creates new hazards (secondary hazards) | record | Risk Management File | [ISO 14971:2019 §7.5 + §7.6](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-013) | — | GAP |

### Verification (4)

| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |
|----|-----------|---------------|------------------------|-----------|---------------|:------:|
| [`OBL-SWF-005` · SW Testing Documentation](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-sw-functions.md#OBL-SWF-005) | For Enhanced documentation (MedTech Project): submit complete test protocols and reports at unit, integration, AND system levels | submission-content | 510(k) Submission — Software Testing; Test Protocols and Reports | [FDA SW Functions Guidance (2023) §V Required Documentation Elements](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-sw-functions.md#OBL-SWF-005) | — | GAP |
| [`OBL-62366-006` · UI Verification](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-006) | Verify the implemented user interface meets the UI specification requirements | test-report | UI Verification Report; V&V Plan | [IEC 62366-1:2015 §5.5](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-006) | — | GAP |
| [`OBL-81001-006` · Secure Implementation Practices](../../../.claude/skills/dhf-manifest/data/standards/iec-81001-5-1.md#OBL-81001-006) | Conduct system-level security testing before release: vulnerability scanning, penetration testing | test-report | Security Test Report; V&V Plan | [IEC 81001-5-1:2021 §5.7](../../../.claude/skills/dhf-manifest/data/standards/iec-81001-5-1.md#OBL-81001-006) | — | GAP |
| [`OBL-13485-005` · Design Verification Planning](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-005) | Plan design verification at each development stage per the DDP | test-report | Verification Plan; Verification Reports; V&V Plan | [ISO 13485:2016 §7.3.6](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-005) | — | GAP |

### Validation (2)

| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |
|----|-----------|---------------|------------------------|-----------|---------------|:------:|
| [`OBL-62304-013` · System Testing](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-013) | Test the complete integrated software system against every SRS requirement | protocol | Software System Test Plan; Software System Test Report | [IEC 62304:2006+AMD1:2015 §5.7.1 + §5.7.3](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-013) | — | GAP |
| [`OBL-62366-007` · Formative Usability Evaluation](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-007) | Conduct iterative formative usability evaluations during design | test-report | Formative Evaluation Reports; Usability Engineering File | [IEC 62366-1:2015 §5.6](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-007) | — | GAP |

### Software Lifecycle (10)

| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |
|----|-----------|---------------|------------------------|-----------|---------------|:------:|
| [`OBL-SWF-004` · SW Lifecycle Documentation](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-sw-functions.md#OBL-SWF-004) | Option 1 (preferred): Submit a Declaration of Conformity to IEC 62304 — this substitutes for the SW development practices documentation section | submission-content | 510(k) Submission — Software Documentation; IEC 62304 Declaration of Conformity | [FDA SW Functions Guidance (2023) §V Required Documentation Elements](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-sw-functions.md#OBL-SWF-004) | — | GAP |
| [`OBL-SWF-006` · Unresolved Anomalies List](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-sw-functions.md#OBL-SWF-006) | Include software version history from first version under design controls to the final released version | submission-content | 510(k) Submission — Software Documentation; Unresolved Anomalies List | [FDA SW Functions Guidance (2023) §V Required Documentation Elements](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-sw-functions.md#OBL-SWF-006) | — | GAP |
| [`OBL-62304-001` · Software Safety Classification](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-001) | Assign IEC 62304 safety class (A, B, or C) to each software item before development begins | record | Safety Classification Record; Software Development Plan | [IEC 62304:2006+AMD1:2015 §4.3](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-001) | — | GAP |
| [`OBL-62304-002` · Software Development Plan](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-002) | Establish a Software Development Plan (SDP) before beginning software development | plan | Software Development Plan; Design and Development Plan | [IEC 62304:2006+AMD1:2015 §5.1.1](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-002) | — | GAP |
| [`OBL-62304-003` · SDP Content & Lifecycle](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-003) | SDP must define the SDLC model (waterfall, iterative, agile-within-waterfall, etc.) | plan | Software Development Plan | [IEC 62304:2006+AMD1:2015 §5.1.2 + §5.1.3](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-003) | — | GAP |
| [`OBL-81001-002` · Secure Development Plan](../../../.claude/skills/dhf-manifest/data/standards/iec-81001-5-1.md#OBL-81001-002) | Include security activities in the SDP: threat modeling, secure design, security testing, vulnerability management | plan | Software Development Plan; Cybersecurity Plan | [IEC 81001-5-1:2021 §5.1](../../../.claude/skills/dhf-manifest/data/standards/iec-81001-5-1.md#OBL-81001-002) | — | GAP |
| [`OBL-81001-005` · Secure Detailed Design](../../../.claude/skills/dhf-manifest/data/standards/iec-81001-5-1.md#OBL-81001-005) | Follow a defined secure coding standard (e.g., OWASP, CERT C, or equivalent) | process-record | Secure Coding Standard; SOUP List; Software Development Process Records | [IEC 81001-5-1:2021 §5.5](../../../.claude/skills/dhf-manifest/data/standards/iec-81001-5-1.md#OBL-81001-005) | — | GAP |
| [`OBL-82304-002` · Safety Requirements Specification](../../../.claude/skills/dhf-manifest/data/standards/iec-82304.md#OBL-82304-002) | All software development activities must conform to IEC 62304 | process-record | Software Development Plan; IEC 62304 Conformance Records | [IEC 82304-1:2016 §4.3](../../../.claude/skills/dhf-manifest/data/standards/iec-82304.md#OBL-82304-002) | — | GAP |
| [`OBL-13485-001` · Design & Development Planning](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-001) | Document the stages of design and development with defined entry/exit criteria | plan | Design and Development Plan; Software Development Plan | [ISO 13485:2016 §7.3.2](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-001) | — | GAP |
| [`OBL-13485-010` · SOUP Supplier Qualification](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-010) | Evaluate and qualify SOUP/third-party software components as suppliers (for IEC 62304 Class B/C, SOUP evaluation is also an IEC 62304 §8.1.2 obligation) | process-record | SOUP List; Supplier Qualification Records; Approved Supplier List | [ISO 13485:2016 §7.4.1](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-010) | — | GAP |

### Configuration & Change Control (3)

| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |
|----|-----------|---------------|------------------------|-----------|---------------|:------:|
| [`OBL-62304-014` · Software Release](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-014) | Assign a unique version identifier to the released software (must be traceable in the DHF) | record | Software Release Package; Release Checklist | [IEC 62304:2006+AMD1:2015 §5.8.1 + §5.8.3 + §5.8.7](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-014) | — | GAP |
| [`OBL-13485-007` · Design Transfer Procedure](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-007) | Define and follow a documented design transfer procedure | process-record | Design Transfer Record; Release Package; Configuration Baseline | [ISO 13485:2016 §7.3.8](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-007) | — | GAP |
| [`OBL-13485-008` · Design Change Control](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-008) | Design changes must be reviewed, and as appropriate verified and validated, before implementation | change-record | Design Change Records; PCCP Change Records; ECO Records | [ISO 13485:2016 §7.3.9](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-008) | — | GAP |

### Design Reviews (1)

| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |
|----|-----------|---------------|------------------------|-----------|---------------|:------:|
| [`OBL-13485-004` · Design Reviews](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-004) | Conduct design reviews at planned stages per the DDP | review-record | Design Review Records; Phase Gate Records | [ISO 13485:2016 §7.3.5](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-004) | — | GAP |

### Human Factors (4)

| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |
|----|-----------|---------------|------------------------|-----------|---------------|:------:|
| [`OBL-62366-002` · Use Specification](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-002) | Identify and characterize the intended users for each use scenario | specification | Use Specification; Usability Engineering File | [IEC 62366-1:2015 §5.1.1](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-002) | — | GAP |
| [`OBL-62366-003` · User Profiles & Environments](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-003) | Document the intended use environment for each module | specification | Use Specification; Usability Engineering File | [IEC 62366-1:2015 §5.1.2](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-003) | — | GAP |
| [`OBL-62366-005` · User Interface Specification](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-005) | Establish a UI specification derived from the use specification and use-related risk analysis | specification | User Interface Specification; Software Requirements Specification | [IEC 62366-1:2015 §5.3](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-005) | — | GAP |
| [`OBL-62366-009` · UOUP Evaluation](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-009) | If third-party UI frameworks or pre-built components are used in the clinical interface, evaluate them under the UOUP process | analysis | UOUP Evaluation; Usability Engineering File | [IEC 62366-1:2015 §5.7](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-009) | — | GAP |

---

## alerts-engine
*SaMD · IEC 62304 Class C*  
**Obligations in this DHF**: 50

### Architecture (4)

| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |
|----|-----------|---------------|------------------------|-----------|---------------|:------:|
| [`OBL-62304-007` · Software Architecture Specification](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-007) | Produce a Software Architecture Document (SAD) transforming the SRS into a structural design | spec | Software Architecture Document | [IEC 62304:2006+AMD1:2015 §5.3.1](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-007) | — | GAP |
| [`OBL-62304-008` · SOUP Identification](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-008) | Identify all SOUP (Software of Unknown Provenance) items used in each software item | record | SOUP List; Software Architecture Document | [IEC 62304:2006+AMD1:2015 §5.3.3](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-008) | — | GAP |
| [`OBL-62304-009` · Architecture Verification](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-009) | Conduct and document an architecture verification that confirms all SRS requirements are addressed in the design | record | Software Architecture Document; Architecture Verification Record | [IEC 62304:2006+AMD1:2015 §5.3.4](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-009) | — | GAP |
| [`OBL-81001-004` · Secure Software Architecture](../../../.claude/skills/dhf-manifest/data/standards/iec-81001-5-1.md#OBL-81001-004) | Apply secure design principles in the SAD: defense in depth, least privilege, secure defaults, fail secure, minimize attack surface | design-document | Software Architecture Document; Security Architecture | [IEC 81001-5-1:2021 §5.3](../../../.claude/skills/dhf-manifest/data/standards/iec-81001-5-1.md#OBL-81001-004) | — | GAP |

### Requirements (6)

| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |
|----|-----------|---------------|------------------------|-----------|---------------|:------:|
| [`OBL-62304-004` · Software Requirements Specification](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-004) | Define software requirements traceable to system-level requirements | spec | Software Requirements Specification | [IEC 62304:2006+AMD1:2015 §5.2.1](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-004) | — | GAP |
| [`OBL-62304-005` · SRS Content Requirements](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-005) | SRS must cover: functional/capability requirements, I/O requirements, external interfaces | spec | Software Requirements Specification | [IEC 62304:2006+AMD1:2015 §5.2.2 + §5.2.3](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-005) | — | GAP |
| [`OBL-62304-006` · SRS Risk Control Trace](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-006) | Re-evaluate risk after SRS is established — update risk file if new hazards emerge | record | Software Requirements Specification; Risk Management File | [IEC 62304:2006+AMD1:2015 §5.2.6](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-006) | — | GAP |
| [`OBL-81001-003` · Security Requirements](../../../.claude/skills/dhf-manifest/data/standards/iec-81001-5-1.md#OBL-81001-003) | Derive security requirements from security risk assessment + FDA cybersecurity guidance + PHI/PII obligations | specification | Software Requirements Specification; Security Requirements | [IEC 81001-5-1:2021 §5.2](../../../.claude/skills/dhf-manifest/data/standards/iec-81001-5-1.md#OBL-81001-003) | — | GAP |
| [`OBL-82304-004` · Product Validation Execution](../../../.claude/skills/dhf-manifest/data/standards/iec-82304.md#OBL-82304-004) | Safety requirements must be derived from risk management (ISO 14971) activities — not authored independently | specification | Software Requirements Specification; Risk Control Requirements | [IEC 82304-1:2016 §5.2](../../../.claude/skills/dhf-manifest/data/standards/iec-82304.md#OBL-82304-004) | — | GAP |
| [`OBL-13485-002` · Design Input Documentation](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-002) | Document design inputs covering: functional, performance, and safety requirements | specification | Design Inputs Record; Software Requirements Specification; User Needs Document | [ISO 13485:2016 §7.3.3](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-002) | — | GAP |

### Design Outputs (3)

| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |
|----|-----------|---------------|------------------------|-----------|---------------|:------:|
| [`OBL-SWF-003` · SW Design Documentation](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-sw-functions.md#OBL-SWF-003) | For Enhanced documentation (MedTech Project): include Software Design Specification in the submission | submission-content | 510(k) Submission — Software Documentation (Enhanced); Software Design Document | [FDA SW Functions Guidance (2023) §V Required Documentation Elements](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-sw-functions.md#OBL-SWF-003) | — | GAP |
| [`OBL-62304-010` · Detailed Software Design](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-010) | Decompose the architecture into software units (leaf-level components that can be individually implemented and tested) | spec | Software Design Document; Software Detailed Design | [IEC 62304:2006+AMD1:2015 §5.4.1](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-010) | — | GAP |
| [`OBL-13485-003` · Design Output Documentation](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-003) | Design outputs must demonstrably meet the design inputs — traceability is required | specification | Design Outputs Record; Software Architecture Document; Software Design Document | [ISO 13485:2016 §7.3.4](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-003) | — | GAP |

### Traceability (2)

| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |
|----|-----------|---------------|------------------------|-----------|---------------|:------:|
| [`OBL-62304-020` · Software Traceability](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-020) | Maintain bidirectional traceability: system requirements → software requirements → architecture → test cases | record | Trace Matrix; Software Development Plan | [IEC 62304:2006+AMD1:2015 §5.1.6(d)](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-020) | — | GAP |
| [`OBL-13485-009` · Design History File](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-009) | Maintain a Design History File (DHF) for each device type or family | dhf-file | Design History File; DHF README; DHF Manifest | [ISO 13485:2016 §7.3.10](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-009) | — | GAP |

### Risk Management (8)

| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |
|----|-----------|---------------|------------------------|-----------|---------------|:------:|
| [`OBL-62304-016` · Software Hazard Analysis](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-016) | For each hazardous situation in the risk file, identify which software items could contribute to it | record | Risk Management File; Software FMEA; Hazard Analysis | [IEC 62304:2006+AMD1:2015 §7.1.1](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-016) | — | GAP |
| [`OBL-62304-017` · SOUP Risk Evaluation](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-017) | For each SOUP item, obtain and review the supplier's known anomaly list | record | Risk Management File; SOUP Risk Evaluation | [IEC 62304:2006+AMD1:2015 §7.1.3](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-017) | — | GAP |
| [`OBL-14971-007` · Hazard Identification](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-007) | Identify all foreseeable hazards (energy, biology, data, software, mechanical, chemical, etc.) | record | Preliminary Hazard Analysis; Hazard Analysis; Risk Management File | [ISO 14971:2019 §5.4](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-007) | — | GAP |
| [`OBL-14971-008` · Risk Estimation](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-008) | Estimate risk for each hazardous situation using severity × probability from the risk matrix in the plan | record | Risk Assessment / FMEA; Risk Management File | [ISO 14971:2019 §5.5](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-008) | — | GAP |
| [`OBL-14971-009` · Risk Evaluation](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-009) | Apply the risk matrix from the plan to each estimated risk — classify as acceptable / ALARP / unacceptable | record | Risk Assessment / FMEA; Risk Management File | [ISO 14971:2019 §6](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-009) | — | GAP |
| [`OBL-14971-010` · Risk Control Options](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-010) | Apply risk controls in priority order: (1) design-level elimination, (2) device protective measure, (3) information/labeling | record | Risk Control Measures; Risk Management File | [ISO 14971:2019 §7.1](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-010) | — | GAP |
| [`OBL-14971-011` · Risk Control Verification](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-011) | Verify that each risk control measure is implemented as specified (implementation verification record) | record | Risk Control Measures; Verification Records; Risk Management File | [ISO 14971:2019 §7.2 + §7.3](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-011) | — | GAP |
| [`OBL-14971-013` · Secondary Hazard Evaluation](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-013) | After applying each risk control, evaluate whether the control creates new hazards (secondary hazards) | record | Risk Management File | [ISO 14971:2019 §7.5 + §7.6](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-013) | — | GAP |

### Verification (6)

| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |
|----|-----------|---------------|------------------------|-----------|---------------|:------:|
| [`OBL-SWF-005` · SW Testing Documentation](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-sw-functions.md#OBL-SWF-005) | For Enhanced documentation (MedTech Project): submit complete test protocols and reports at unit, integration, AND system levels | submission-content | 510(k) Submission — Software Testing; Test Protocols and Reports | [FDA SW Functions Guidance (2023) §V Required Documentation Elements](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-sw-functions.md#OBL-SWF-005) | — | GAP |
| [`OBL-62304-011` · Unit Verification](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-011) | Verify each software unit through code review, unit testing, or both | record | Unit Verification Records; Code Review Records | [IEC 62304:2006+AMD1:2015 §5.5.2 + §5.5.3](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-011) | — | GAP |
| [`OBL-62304-012` · Integration Testing](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-012) | Produce an integration plan defining the sequence and method for integrating software items | protocol | Integration Test Plan; Integration Test Report | [IEC 62304:2006+AMD1:2015 §5.6.1 + §5.6.3](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-012) | — | GAP |
| [`OBL-62366-006` · UI Verification](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-006) | Verify the implemented user interface meets the UI specification requirements | test-report | UI Verification Report; V&V Plan | [IEC 62366-1:2015 §5.5](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-006) | — | GAP |
| [`OBL-81001-006` · Secure Implementation Practices](../../../.claude/skills/dhf-manifest/data/standards/iec-81001-5-1.md#OBL-81001-006) | Conduct system-level security testing before release: vulnerability scanning, penetration testing | test-report | Security Test Report; V&V Plan | [IEC 81001-5-1:2021 §5.7](../../../.claude/skills/dhf-manifest/data/standards/iec-81001-5-1.md#OBL-81001-006) | — | GAP |
| [`OBL-13485-005` · Design Verification Planning](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-005) | Plan design verification at each development stage per the DDP | test-report | Verification Plan; Verification Reports; V&V Plan | [ISO 13485:2016 §7.3.6](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-005) | — | GAP |

### Validation (2)

| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |
|----|-----------|---------------|------------------------|-----------|---------------|:------:|
| [`OBL-62304-013` · System Testing](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-013) | Test the complete integrated software system against every SRS requirement | protocol | Software System Test Plan; Software System Test Report | [IEC 62304:2006+AMD1:2015 §5.7.1 + §5.7.3](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-013) | — | GAP |
| [`OBL-62366-007` · Formative Usability Evaluation](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-007) | Conduct iterative formative usability evaluations during design | test-report | Formative Evaluation Reports; Usability Engineering File | [IEC 62366-1:2015 §5.6](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-007) | — | GAP |

### Software Lifecycle (10)

| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |
|----|-----------|---------------|------------------------|-----------|---------------|:------:|
| [`OBL-SWF-004` · SW Lifecycle Documentation](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-sw-functions.md#OBL-SWF-004) | Option 1 (preferred): Submit a Declaration of Conformity to IEC 62304 — this substitutes for the SW development practices documentation section | submission-content | 510(k) Submission — Software Documentation; IEC 62304 Declaration of Conformity | [FDA SW Functions Guidance (2023) §V Required Documentation Elements](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-sw-functions.md#OBL-SWF-004) | — | GAP |
| [`OBL-SWF-006` · Unresolved Anomalies List](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-sw-functions.md#OBL-SWF-006) | Include software version history from first version under design controls to the final released version | submission-content | 510(k) Submission — Software Documentation; Unresolved Anomalies List | [FDA SW Functions Guidance (2023) §V Required Documentation Elements](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-sw-functions.md#OBL-SWF-006) | — | GAP |
| [`OBL-62304-001` · Software Safety Classification](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-001) | Assign IEC 62304 safety class (A, B, or C) to each software item before development begins | record | Safety Classification Record; Software Development Plan | [IEC 62304:2006+AMD1:2015 §4.3](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-001) | — | GAP |
| [`OBL-62304-002` · Software Development Plan](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-002) | Establish a Software Development Plan (SDP) before beginning software development | plan | Software Development Plan; Design and Development Plan | [IEC 62304:2006+AMD1:2015 §5.1.1](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-002) | — | GAP |
| [`OBL-62304-003` · SDP Content & Lifecycle](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-003) | SDP must define the SDLC model (waterfall, iterative, agile-within-waterfall, etc.) | plan | Software Development Plan | [IEC 62304:2006+AMD1:2015 §5.1.2 + §5.1.3](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-003) | — | GAP |
| [`OBL-81001-002` · Secure Development Plan](../../../.claude/skills/dhf-manifest/data/standards/iec-81001-5-1.md#OBL-81001-002) | Include security activities in the SDP: threat modeling, secure design, security testing, vulnerability management | plan | Software Development Plan; Cybersecurity Plan | [IEC 81001-5-1:2021 §5.1](../../../.claude/skills/dhf-manifest/data/standards/iec-81001-5-1.md#OBL-81001-002) | — | GAP |
| [`OBL-81001-005` · Secure Detailed Design](../../../.claude/skills/dhf-manifest/data/standards/iec-81001-5-1.md#OBL-81001-005) | Follow a defined secure coding standard (e.g., OWASP, CERT C, or equivalent) | process-record | Secure Coding Standard; SOUP List; Software Development Process Records | [IEC 81001-5-1:2021 §5.5](../../../.claude/skills/dhf-manifest/data/standards/iec-81001-5-1.md#OBL-81001-005) | — | GAP |
| [`OBL-82304-002` · Safety Requirements Specification](../../../.claude/skills/dhf-manifest/data/standards/iec-82304.md#OBL-82304-002) | All software development activities must conform to IEC 62304 | process-record | Software Development Plan; IEC 62304 Conformance Records | [IEC 82304-1:2016 §4.3](../../../.claude/skills/dhf-manifest/data/standards/iec-82304.md#OBL-82304-002) | — | GAP |
| [`OBL-13485-001` · Design & Development Planning](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-001) | Document the stages of design and development with defined entry/exit criteria | plan | Design and Development Plan; Software Development Plan | [ISO 13485:2016 §7.3.2](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-001) | — | GAP |
| [`OBL-13485-010` · SOUP Supplier Qualification](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-010) | Evaluate and qualify SOUP/third-party software components as suppliers (for IEC 62304 Class B/C, SOUP evaluation is also an IEC 62304 §8.1.2 obligation) | process-record | SOUP List; Supplier Qualification Records; Approved Supplier List | [ISO 13485:2016 §7.4.1](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-010) | — | GAP |

### Configuration & Change Control (4)

| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |
|----|-----------|---------------|------------------------|-----------|---------------|:------:|
| [`OBL-62304-014` · Software Release](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-014) | Assign a unique version identifier to the released software (must be traceable in the DHF) | record | Software Release Package; Release Checklist | [IEC 62304:2006+AMD1:2015 §5.8.1 + §5.8.3 + §5.8.7](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-014) | — | GAP |
| [`OBL-62304-018` · Software Configuration Management](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-018) | Establish a Configuration Management Plan (may be part of SDP) | plan | Configuration Management Plan; Software Development Plan | [IEC 62304:2006+AMD1:2015 §8.1.1 + §8.1.2](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-018) | — | GAP |
| [`OBL-13485-007` · Design Transfer Procedure](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-007) | Define and follow a documented design transfer procedure | process-record | Design Transfer Record; Release Package; Configuration Baseline | [ISO 13485:2016 §7.3.8](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-007) | — | GAP |
| [`OBL-13485-008` · Design Change Control](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-008) | Design changes must be reviewed, and as appropriate verified and validated, before implementation | change-record | Design Change Records; PCCP Change Records; ECO Records | [ISO 13485:2016 §7.3.9](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-008) | — | GAP |

### Design Reviews (1)

| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |
|----|-----------|---------------|------------------------|-----------|---------------|:------:|
| [`OBL-13485-004` · Design Reviews](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-004) | Conduct design reviews at planned stages per the DDP | review-record | Design Review Records; Phase Gate Records | [ISO 13485:2016 §7.3.5](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-004) | — | GAP |

### Human Factors (4)

| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |
|----|-----------|---------------|------------------------|-----------|---------------|:------:|
| [`OBL-62366-002` · Use Specification](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-002) | Identify and characterize the intended users for each use scenario | specification | Use Specification; Usability Engineering File | [IEC 62366-1:2015 §5.1.1](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-002) | — | GAP |
| [`OBL-62366-003` · User Profiles & Environments](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-003) | Document the intended use environment for each module | specification | Use Specification; Usability Engineering File | [IEC 62366-1:2015 §5.1.2](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-003) | — | GAP |
| [`OBL-62366-005` · User Interface Specification](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-005) | Establish a UI specification derived from the use specification and use-related risk analysis | specification | User Interface Specification; Software Requirements Specification | [IEC 62366-1:2015 §5.3](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-005) | — | GAP |
| [`OBL-62366-009` · UOUP Evaluation](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-009) | If third-party UI frameworks or pre-built components are used in the clinical interface, evaluate them under the UOUP process | analysis | UOUP Evaluation; Usability Engineering File | [IEC 62366-1:2015 §5.7](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-009) | — | GAP |

---

## clinical-interface
*SaMD · IEC 62304 Class C*  
**Obligations in this DHF**: 50

### Architecture (4)

| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |
|----|-----------|---------------|------------------------|-----------|---------------|:------:|
| [`OBL-62304-007` · Software Architecture Specification](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-007) | Produce a Software Architecture Document (SAD) transforming the SRS into a structural design | spec | Software Architecture Document | [IEC 62304:2006+AMD1:2015 §5.3.1](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-007) | — | GAP |
| [`OBL-62304-008` · SOUP Identification](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-008) | Identify all SOUP (Software of Unknown Provenance) items used in each software item | record | SOUP List; Software Architecture Document | [IEC 62304:2006+AMD1:2015 §5.3.3](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-008) | — | GAP |
| [`OBL-62304-009` · Architecture Verification](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-009) | Conduct and document an architecture verification that confirms all SRS requirements are addressed in the design | record | Software Architecture Document; Architecture Verification Record | [IEC 62304:2006+AMD1:2015 §5.3.4](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-009) | — | GAP |
| [`OBL-81001-004` · Secure Software Architecture](../../../.claude/skills/dhf-manifest/data/standards/iec-81001-5-1.md#OBL-81001-004) | Apply secure design principles in the SAD: defense in depth, least privilege, secure defaults, fail secure, minimize attack surface | design-document | Software Architecture Document; Security Architecture | [IEC 81001-5-1:2021 §5.3](../../../.claude/skills/dhf-manifest/data/standards/iec-81001-5-1.md#OBL-81001-004) | — | GAP |

### Requirements (6)

| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |
|----|-----------|---------------|------------------------|-----------|---------------|:------:|
| [`OBL-62304-004` · Software Requirements Specification](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-004) | Define software requirements traceable to system-level requirements | spec | Software Requirements Specification | [IEC 62304:2006+AMD1:2015 §5.2.1](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-004) | — | GAP |
| [`OBL-62304-005` · SRS Content Requirements](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-005) | SRS must cover: functional/capability requirements, I/O requirements, external interfaces | spec | Software Requirements Specification | [IEC 62304:2006+AMD1:2015 §5.2.2 + §5.2.3](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-005) | — | GAP |
| [`OBL-62304-006` · SRS Risk Control Trace](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-006) | Re-evaluate risk after SRS is established — update risk file if new hazards emerge | record | Software Requirements Specification; Risk Management File | [IEC 62304:2006+AMD1:2015 §5.2.6](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-006) | — | GAP |
| [`OBL-81001-003` · Security Requirements](../../../.claude/skills/dhf-manifest/data/standards/iec-81001-5-1.md#OBL-81001-003) | Derive security requirements from security risk assessment + FDA cybersecurity guidance + PHI/PII obligations | specification | Software Requirements Specification; Security Requirements | [IEC 81001-5-1:2021 §5.2](../../../.claude/skills/dhf-manifest/data/standards/iec-81001-5-1.md#OBL-81001-003) | — | GAP |
| [`OBL-82304-004` · Product Validation Execution](../../../.claude/skills/dhf-manifest/data/standards/iec-82304.md#OBL-82304-004) | Safety requirements must be derived from risk management (ISO 14971) activities — not authored independently | specification | Software Requirements Specification; Risk Control Requirements | [IEC 82304-1:2016 §5.2](../../../.claude/skills/dhf-manifest/data/standards/iec-82304.md#OBL-82304-004) | — | GAP |
| [`OBL-13485-002` · Design Input Documentation](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-002) | Document design inputs covering: functional, performance, and safety requirements | specification | Design Inputs Record; Software Requirements Specification; User Needs Document | [ISO 13485:2016 §7.3.3](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-002) | — | GAP |

### Design Outputs (3)

| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |
|----|-----------|---------------|------------------------|-----------|---------------|:------:|
| [`OBL-SWF-003` · SW Design Documentation](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-sw-functions.md#OBL-SWF-003) | For Enhanced documentation (MedTech Project): include Software Design Specification in the submission | submission-content | 510(k) Submission — Software Documentation (Enhanced); Software Design Document | [FDA SW Functions Guidance (2023) §V Required Documentation Elements](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-sw-functions.md#OBL-SWF-003) | — | GAP |
| [`OBL-62304-010` · Detailed Software Design](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-010) | Decompose the architecture into software units (leaf-level components that can be individually implemented and tested) | spec | Software Design Document; Software Detailed Design | [IEC 62304:2006+AMD1:2015 §5.4.1](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-010) | — | GAP |
| [`OBL-13485-003` · Design Output Documentation](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-003) | Design outputs must demonstrably meet the design inputs — traceability is required | specification | Design Outputs Record; Software Architecture Document; Software Design Document | [ISO 13485:2016 §7.3.4](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-003) | — | GAP |

### Traceability (2)

| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |
|----|-----------|---------------|------------------------|-----------|---------------|:------:|
| [`OBL-62304-020` · Software Traceability](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-020) | Maintain bidirectional traceability: system requirements → software requirements → architecture → test cases | record | Trace Matrix; Software Development Plan | [IEC 62304:2006+AMD1:2015 §5.1.6(d)](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-020) | — | GAP |
| [`OBL-13485-009` · Design History File](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-009) | Maintain a Design History File (DHF) for each device type or family | dhf-file | Design History File; DHF README; DHF Manifest | [ISO 13485:2016 §7.3.10](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-009) | — | GAP |

### Risk Management (8)

| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |
|----|-----------|---------------|------------------------|-----------|---------------|:------:|
| [`OBL-62304-016` · Software Hazard Analysis](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-016) | For each hazardous situation in the risk file, identify which software items could contribute to it | record | Risk Management File; Software FMEA; Hazard Analysis | [IEC 62304:2006+AMD1:2015 §7.1.1](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-016) | — | GAP |
| [`OBL-62304-017` · SOUP Risk Evaluation](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-017) | For each SOUP item, obtain and review the supplier's known anomaly list | record | Risk Management File; SOUP Risk Evaluation | [IEC 62304:2006+AMD1:2015 §7.1.3](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-017) | — | GAP |
| [`OBL-14971-007` · Hazard Identification](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-007) | Identify all foreseeable hazards (energy, biology, data, software, mechanical, chemical, etc.) | record | Preliminary Hazard Analysis; Hazard Analysis; Risk Management File | [ISO 14971:2019 §5.4](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-007) | — | GAP |
| [`OBL-14971-008` · Risk Estimation](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-008) | Estimate risk for each hazardous situation using severity × probability from the risk matrix in the plan | record | Risk Assessment / FMEA; Risk Management File | [ISO 14971:2019 §5.5](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-008) | — | GAP |
| [`OBL-14971-009` · Risk Evaluation](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-009) | Apply the risk matrix from the plan to each estimated risk — classify as acceptable / ALARP / unacceptable | record | Risk Assessment / FMEA; Risk Management File | [ISO 14971:2019 §6](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-009) | — | GAP |
| [`OBL-14971-010` · Risk Control Options](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-010) | Apply risk controls in priority order: (1) design-level elimination, (2) device protective measure, (3) information/labeling | record | Risk Control Measures; Risk Management File | [ISO 14971:2019 §7.1](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-010) | — | GAP |
| [`OBL-14971-011` · Risk Control Verification](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-011) | Verify that each risk control measure is implemented as specified (implementation verification record) | record | Risk Control Measures; Verification Records; Risk Management File | [ISO 14971:2019 §7.2 + §7.3](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-011) | — | GAP |
| [`OBL-14971-013` · Secondary Hazard Evaluation](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-013) | After applying each risk control, evaluate whether the control creates new hazards (secondary hazards) | record | Risk Management File | [ISO 14971:2019 §7.5 + §7.6](../../../.claude/skills/dhf-manifest/data/standards/iso-14971.md#OBL-14971-013) | — | GAP |

### Verification (6)

| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |
|----|-----------|---------------|------------------------|-----------|---------------|:------:|
| [`OBL-SWF-005` · SW Testing Documentation](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-sw-functions.md#OBL-SWF-005) | For Enhanced documentation (MedTech Project): submit complete test protocols and reports at unit, integration, AND system levels | submission-content | 510(k) Submission — Software Testing; Test Protocols and Reports | [FDA SW Functions Guidance (2023) §V Required Documentation Elements](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-sw-functions.md#OBL-SWF-005) | — | GAP |
| [`OBL-62304-011` · Unit Verification](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-011) | Verify each software unit through code review, unit testing, or both | record | Unit Verification Records; Code Review Records | [IEC 62304:2006+AMD1:2015 §5.5.2 + §5.5.3](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-011) | — | GAP |
| [`OBL-62304-012` · Integration Testing](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-012) | Produce an integration plan defining the sequence and method for integrating software items | protocol | Integration Test Plan; Integration Test Report | [IEC 62304:2006+AMD1:2015 §5.6.1 + §5.6.3](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-012) | — | GAP |
| [`OBL-62366-006` · UI Verification](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-006) | Verify the implemented user interface meets the UI specification requirements | test-report | UI Verification Report; V&V Plan | [IEC 62366-1:2015 §5.5](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-006) | — | GAP |
| [`OBL-81001-006` · Secure Implementation Practices](../../../.claude/skills/dhf-manifest/data/standards/iec-81001-5-1.md#OBL-81001-006) | Conduct system-level security testing before release: vulnerability scanning, penetration testing | test-report | Security Test Report; V&V Plan | [IEC 81001-5-1:2021 §5.7](../../../.claude/skills/dhf-manifest/data/standards/iec-81001-5-1.md#OBL-81001-006) | — | GAP |
| [`OBL-13485-005` · Design Verification Planning](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-005) | Plan design verification at each development stage per the DDP | test-report | Verification Plan; Verification Reports; V&V Plan | [ISO 13485:2016 §7.3.6](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-005) | — | GAP |

### Validation (2)

| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |
|----|-----------|---------------|------------------------|-----------|---------------|:------:|
| [`OBL-62304-013` · System Testing](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-013) | Test the complete integrated software system against every SRS requirement | protocol | Software System Test Plan; Software System Test Report | [IEC 62304:2006+AMD1:2015 §5.7.1 + §5.7.3](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-013) | — | GAP |
| [`OBL-62366-007` · Formative Usability Evaluation](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-007) | Conduct iterative formative usability evaluations during design | test-report | Formative Evaluation Reports; Usability Engineering File | [IEC 62366-1:2015 §5.6](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-007) | — | GAP |

### Software Lifecycle (10)

| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |
|----|-----------|---------------|------------------------|-----------|---------------|:------:|
| [`OBL-SWF-004` · SW Lifecycle Documentation](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-sw-functions.md#OBL-SWF-004) | Option 1 (preferred): Submit a Declaration of Conformity to IEC 62304 — this substitutes for the SW development practices documentation section | submission-content | 510(k) Submission — Software Documentation; IEC 62304 Declaration of Conformity | [FDA SW Functions Guidance (2023) §V Required Documentation Elements](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-sw-functions.md#OBL-SWF-004) | — | GAP |
| [`OBL-SWF-006` · Unresolved Anomalies List](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-sw-functions.md#OBL-SWF-006) | Include software version history from first version under design controls to the final released version | submission-content | 510(k) Submission — Software Documentation; Unresolved Anomalies List | [FDA SW Functions Guidance (2023) §V Required Documentation Elements](../../../.claude/skills/dhf-manifest/data/fda-guidance/fda-sw-functions.md#OBL-SWF-006) | — | GAP |
| [`OBL-62304-001` · Software Safety Classification](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-001) | Assign IEC 62304 safety class (A, B, or C) to each software item before development begins | record | Safety Classification Record; Software Development Plan | [IEC 62304:2006+AMD1:2015 §4.3](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-001) | — | GAP |
| [`OBL-62304-002` · Software Development Plan](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-002) | Establish a Software Development Plan (SDP) before beginning software development | plan | Software Development Plan; Design and Development Plan | [IEC 62304:2006+AMD1:2015 §5.1.1](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-002) | — | GAP |
| [`OBL-62304-003` · SDP Content & Lifecycle](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-003) | SDP must define the SDLC model (waterfall, iterative, agile-within-waterfall, etc.) | plan | Software Development Plan | [IEC 62304:2006+AMD1:2015 §5.1.2 + §5.1.3](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-003) | — | GAP |
| [`OBL-81001-002` · Secure Development Plan](../../../.claude/skills/dhf-manifest/data/standards/iec-81001-5-1.md#OBL-81001-002) | Include security activities in the SDP: threat modeling, secure design, security testing, vulnerability management | plan | Software Development Plan; Cybersecurity Plan | [IEC 81001-5-1:2021 §5.1](../../../.claude/skills/dhf-manifest/data/standards/iec-81001-5-1.md#OBL-81001-002) | — | GAP |
| [`OBL-81001-005` · Secure Detailed Design](../../../.claude/skills/dhf-manifest/data/standards/iec-81001-5-1.md#OBL-81001-005) | Follow a defined secure coding standard (e.g., OWASP, CERT C, or equivalent) | process-record | Secure Coding Standard; SOUP List; Software Development Process Records | [IEC 81001-5-1:2021 §5.5](../../../.claude/skills/dhf-manifest/data/standards/iec-81001-5-1.md#OBL-81001-005) | — | GAP |
| [`OBL-82304-002` · Safety Requirements Specification](../../../.claude/skills/dhf-manifest/data/standards/iec-82304.md#OBL-82304-002) | All software development activities must conform to IEC 62304 | process-record | Software Development Plan; IEC 62304 Conformance Records | [IEC 82304-1:2016 §4.3](../../../.claude/skills/dhf-manifest/data/standards/iec-82304.md#OBL-82304-002) | — | GAP |
| [`OBL-13485-001` · Design & Development Planning](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-001) | Document the stages of design and development with defined entry/exit criteria | plan | Design and Development Plan; Software Development Plan | [ISO 13485:2016 §7.3.2](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-001) | — | GAP |
| [`OBL-13485-010` · SOUP Supplier Qualification](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-010) | Evaluate and qualify SOUP/third-party software components as suppliers (for IEC 62304 Class B/C, SOUP evaluation is also an IEC 62304 §8.1.2 obligation) | process-record | SOUP List; Supplier Qualification Records; Approved Supplier List | [ISO 13485:2016 §7.4.1](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-010) | — | GAP |

### Configuration & Change Control (4)

| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |
|----|-----------|---------------|------------------------|-----------|---------------|:------:|
| [`OBL-62304-014` · Software Release](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-014) | Assign a unique version identifier to the released software (must be traceable in the DHF) | record | Software Release Package; Release Checklist | [IEC 62304:2006+AMD1:2015 §5.8.1 + §5.8.3 + §5.8.7](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-014) | — | GAP |
| [`OBL-62304-018` · Software Configuration Management](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-018) | Establish a Configuration Management Plan (may be part of SDP) | plan | Configuration Management Plan; Software Development Plan | [IEC 62304:2006+AMD1:2015 §8.1.1 + §8.1.2](../../../.claude/skills/dhf-manifest/data/standards/iec-62304.md#OBL-62304-018) | — | GAP |
| [`OBL-13485-007` · Design Transfer Procedure](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-007) | Define and follow a documented design transfer procedure | process-record | Design Transfer Record; Release Package; Configuration Baseline | [ISO 13485:2016 §7.3.8](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-007) | — | GAP |
| [`OBL-13485-008` · Design Change Control](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-008) | Design changes must be reviewed, and as appropriate verified and validated, before implementation | change-record | Design Change Records; PCCP Change Records; ECO Records | [ISO 13485:2016 §7.3.9](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-008) | — | GAP |

### Design Reviews (1)

| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |
|----|-----------|---------------|------------------------|-----------|---------------|:------:|
| [`OBL-13485-004` · Design Reviews](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-004) | Conduct design reviews at planned stages per the DDP | review-record | Design Review Records; Phase Gate Records | [ISO 13485:2016 §7.3.5](../../../.claude/skills/dhf-manifest/data/standards/iso-13485.md#OBL-13485-004) | — | GAP |

### Human Factors (4)

| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |
|----|-----------|---------------|------------------------|-----------|---------------|:------:|
| [`OBL-62366-002` · Use Specification](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-002) | Identify and characterize the intended users for each use scenario | specification | Use Specification; Usability Engineering File | [IEC 62366-1:2015 §5.1.1](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-002) | — | GAP |
| [`OBL-62366-003` · User Profiles & Environments](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-003) | Document the intended use environment for each module | specification | Use Specification; Usability Engineering File | [IEC 62366-1:2015 §5.1.2](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-003) | — | GAP |
| [`OBL-62366-005` · User Interface Specification](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-005) | Establish a UI specification derived from the use specification and use-related risk analysis | specification | User Interface Specification; Software Requirements Specification | [IEC 62366-1:2015 §5.3](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-005) | — | GAP |
| [`OBL-62366-009` · UOUP Evaluation](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-009) | If third-party UI frameworks or pre-built components are used in the clinical interface, evaluate them under the UOUP process | analysis | UOUP Evaluation; Usability Engineering File | [IEC 62366-1:2015 §5.7](../../../.claude/skills/dhf-manifest/data/standards/iec-62366.md#OBL-62366-009) | — | GAP |

---

## Summary — Gap Analysis

| DHF | Role | Obligations | GAP | FOUND |
|-----|------|------------|-----|-------|
| `pca-device` | system | 75 | 75 | 0 |
| `connectivity-adapter` | item | 49 | 49 | 0 |
| `cloud-suite` | system | 0 | 0 | 0 |
| `drug-library-manager` | item | 49 | 49 | 0 |
| `fleet-management` | item | 41 | 41 | 0 |
| `compliance-reports` | item | 41 | 41 | 0 |
| `analytics-dashboard` | item | 41 | 41 | 0 |
| `inventory-tracker` | item | 41 | 41 | 0 |
| `alerts-engine` | item | 50 | 50 | 0 |
| `clinical-interface` | item | 50 | 50 | 0 |
| **Total** | | **437** | **437** | **0** |

_All statuses are `GAP` at initial generation. Run `/dhf-manifest reproject` after authoring DHF artifacts to update `FOUND` counts._
