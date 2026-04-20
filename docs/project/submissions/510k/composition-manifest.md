# PP3500 510(k) — Composition Manifest

**Status**: Draft — first-stab scaffold (task 013)
**Source strategy**: `docs/project/strategies/regulatory-strategy.md`

_Demo artifact — illustrative, not a real submission composition manifest._

> A **composition manifest** is the authoritative list of which DHF pieces a filing includes and why. Filings are not 1:1 with DHFs — they compose selectively per the regulatory strategy's DHF Filing Composition Pattern. This file is the source of truth for `/tracker build` when deciding which deliverables belong in this filing.

## 1. Filing Identification

| Field | Value |
|---|---|
| **Filing name** | PP3500 510(k) + PCCP |
| **Submission number** | K210345 (illustrative — demo data) |
| **Submission type** | Traditional 510(k) with Predetermined Change Control Plan (PCCP) |
| **Device** | PainEase PCA Advanced (PP3500) |
| **Predicate** | PP3000 (K190567) |
| **Product code** | LZG (Pump, infusion, patient-controlled analgesic) |
| **Regulation** | 21 CFR 880.5725 |
| **Device class** | II |
| **Lead DHF** | `pca-device` |
| **Sponsor** | GlobalLogic (demo) |

## 2. Scope Rationale

Per the regulatory strategy's **Filing Scope: PCA Device Alone** and **Component Classification & Filing Posture** decisions:

- The PP3500 510(k) covers **only** the PCA device itself (lead DHF `pca-device`).
- The **Connectivity Adapter** (classified MDDS) is named as adjacent infrastructure; only its **cybersecurity assessment** is pulled into the filing because the PCA's cyber posture depends on what touches it.
- The **Drug Library Manager** (classified Class II SaMD, accessory to PCA) is pulled in as an accessory because it directly mutates the safety table the pump enforces. Filing posture (bundled vs standalone) is TBD — this manifest currently assumes **bundled** and includes the full DLM DHF. Flip to standalone shrinks §3.3 to cyber + signing-trust only.
- All other Cloud Suite components (Fleet Management, Telemetry, Analytics, Surveillance, Update Distribution, Reg Data Pipelines, Customer Portals) are non-medical-device software — **excluded** from this filing.
- Requirements in scope: only those tagged CtS, CtF, CtC, or CtP per the **Critical-Requirement Carve-out** decision. Commercial-only requirements ship post-clearance.

## 3. Included Pieces

### 3.1 From DHF: `pca-device` (full DHF — lead)

| Piece | Location | Rationale |
|---|---|---|
| User Needs (Ct*-tagged subset) | `docs/project/dhfs/pca-device/design-controls/user-needs/` | Source of in-scope requirements |
| Design Inputs (Ct*-tagged subset) | `docs/project/dhfs/pca-device/design-controls/requirements/` | Source of in-scope requirements (medtech-docs convention folds Design Inputs into `requirements/`) |
| System SAD | `docs/project/dhfs/pca-device/design-controls/architecture/` | Module decomposition, classification |
| SRS (per module, Ct*-tagged subset) | `docs/project/dhfs/pca-device/design-controls/requirements/` | IEC 62304 |
| Design Outputs | `docs/project/dhfs/pca-device/design-controls/architecture/` | 820.30(d) (outputs colocated with architecture in demo scaffold) |
| V&V Plan + Reports (filing-scope track) | `docs/project/dhfs/pca-device/design-controls/vnv/` | 820.30(f)(g) |
| Trace Matrix (Filing Scope column) | `docs/project/dhfs/pca-device/design-controls/trace-matrix/` | 820.30 traceability |
| Risk Management File | `docs/project/dhfs/pca-device/risk-management/` | ISO 14971 |
| Usability Engineering File | `docs/project/dhfs/pca-device/design-controls/usability/` | IEC 62366-1 |
| Cybersecurity Plan + Threat Model + SBOM | `docs/project/dhfs/pca-device/cybersecurity/` | FDA Cyber 2023, §524B |
| Clinical Evaluation | `docs/project/dhfs/pca-device/clinical/` | Substantial equivalence support |
| Labeling | `docs/project/dhfs/pca-device/design-controls/labeling/` | 21 CFR 801 |
| PCCP (drug-library + firmware update envelope) | `docs/project/dhfs/pca-device/design-controls/pccp/` | PCCP AI/ML + General guidance |
| Postmarket Surveillance Plan | `docs/project/dhfs/pca-device/postmarket/` | 820.100, MDR |

### 3.2 From DHF: `connectivity-adapter` (cybersecurity posture only)

| Piece | Location | Rationale |
|---|---|---|
| System SAD (classification record) | `docs/project/dhfs/connectivity-adapter/design-controls/architecture/connectivity-adapter-system-sad.md` | MDDS classification rationale + architecture summary |
| Cybersecurity Plan | `docs/project/dhfs/connectivity-adapter/cybersecurity/` | PCA cyber posture depends on Adapter |
| Threat Model + SBOM | `docs/project/dhfs/connectivity-adapter/cybersecurity/` | FDA Cyber 2023 — cross-component threat surface |
| Interoperability description | `docs/project/dhfs/connectivity-adapter/design-controls/architecture/` | HL7v2.5 / FHIR R4 bridge boundary |

**NOT pulled from Adapter**: functional design controls, Adapter V&V, Adapter risk file. Adapter is adjacent evidence, not part of the PP3500 device's design history.

### 3.3 From DHF: `cloud-suite/dhfs/drug-library-manager` (bundled-accessory scenario)

| Piece | Location | Rationale |
|---|---|---|
| System SAD | `docs/project/dhfs/cloud-suite/dhfs/drug-library-manager/design-controls/architecture/drug-library-manager-system-sad.md` | SaMD classification + architecture |
| User Needs + Design Inputs (Ct*-tagged) | `docs/project/dhfs/cloud-suite/dhfs/drug-library-manager/design-controls/` | Accessory-bundle requirements |
| SRS (Validation Engine, Signing Service) | `docs/project/dhfs/cloud-suite/dhfs/drug-library-manager/design-controls/requirements/` | IEC 62304 Class C modules |
| V&V Plan + Reports | `docs/project/dhfs/cloud-suite/dhfs/drug-library-manager/design-controls/vnv/` | Class II SaMD evidence |
| Risk Management File | `docs/project/dhfs/cloud-suite/dhfs/drug-library-manager/risk-management/` | ISO 14971 (clinical-rule failure modes) |
| Usability Engineering File | `docs/project/dhfs/cloud-suite/dhfs/drug-library-manager/design-controls/usability/` | IEC 62366-1 — pharmacist workflow |
| Cybersecurity Plan + Threat Model + Signing Trust Chain | `docs/project/dhfs/cloud-suite/dhfs/drug-library-manager/cybersecurity/` | Signing chain that PCA M3 verifies |
| 21 CFR Part 11 Conformance (D2 workflow, D6 audit log) | `docs/project/dhfs/cloud-suite/dhfs/drug-library-manager/design-controls/part-11/` | Electronic signature + audit |

If filing posture flips to **standalone**: §3.3 collapses to cybersecurity plan + signing-trust chain + classification record only. The rest moves to a separate DLM filing.

## 4. Excluded Pieces

| Component / DHF | Classification | Rationale for exclusion |
|---|---|---|
| Connectivity Adapter — functional design, V&V, risk file | MDDS (non-device) | Not a regulated device; adjacent evidence only |
| Cloud Suite — Fleet Management | Non-device software | No medical purpose |
| Cloud Suite — Analytics Dashboard | Non-device software | No medical purpose |
| Cloud Suite — Inventory Tracker | Non-device software | No medical purpose |
| Cloud Suite — Alerts Engine (baseline) | Non-device software | No medical purpose in cleared baseline |
| Cloud Suite — Clinical Interface (manufacturer-side) | Non-device software | No medical purpose |
| Cloud Suite — Compliance Reports | Non-device software | Internal regulatory data pipeline |
| Future AI/ML SaMDs (predictive alarms, dose optimization) | Class II SaMD candidates | Out of baseline; introduced via PCCP or later filings |
| Commercial-only requirements (no Ct* tag) across all DHFs | — | Carved out per the Critical-Requirement Carve-out decision; ship post-clearance |

## 5. Cross-references

| From | To | Nature |
|---|---|---|
| pca-device M6 (Cybersecurity & Comms) | connectivity-adapter A6 + drug-library-manager D7 | Trust boundary; mutual-TLS; signed-payload verification |
| pca-device M3 (Drug Library Enforcement) | drug-library-manager D4 (Signing Service) | Signing trust chain — PCA verifies DLM signatures |
| pca-device M3 (Drug Library Enforcement) | connectivity-adapter A3 (Drug Library Distributor) | Pass-through distribution path |
| pca-device M6 (Cybersecurity & Comms) | connectivity-adapter A4 (Firmware Update Relay) | Signed firmware pass-through |
| regulatory-strategy.md §1 (Filing Strategy — Critical-Requirement Carve-out) | pca-device trace matrix Filing Scope column | Drives in-scope requirement set |
| regulatory-strategy.md §2 (Component Classification) | §2, §3, §4 of this manifest | Drives what gets pulled from which DHF |

## 6. Reviewer Sign-off

| Role | Name | Date | Signature |
|---|---|---|---|
| Regulatory Affairs Lead | _TBD_ | _pending_ | _pending_ |
| Systems Architecture Lead | _TBD_ | _pending_ | _pending_ |
| Cybersecurity Lead | _TBD_ | _pending_ | _pending_ |
| Quality / Document Control | _TBD_ | _pending_ | _pending_ |
| Submission Manager | _TBD_ | _pending_ | _pending_ |

## 7. Changelog

| Date | Author | Summary |
|---|---|---|
| 2026-04-14 | Claude (first-stab) | Initial scaffold derived from regulatory strategy. Assumes DLM bundled-accessory posture; flag to flip if submission planning chooses standalone. Task 013. |
