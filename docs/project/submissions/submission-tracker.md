# PP3500 510(k) + PCCP — Submission Package Tracker

**Filing**: K210345 (demo) — PainEase PCA Advanced (PP3500)
**Lead DHF**: `pca-device`
**Additional DHFs pulled**: `connectivity-adapter` (cyber only), `cloud-suite/dhfs/drug-library-manager` (bundled accessory — posture TBD)
**Last updated**: 2026-05-12 — ben/047 Stage 1+2 (chrome scaffold per `/tracker init` + engineering.yml live)

> **Do not hand-edit the HTML dashboard.** Edit this markdown, then run `/tracker render`.
> **Before editing this file**, load `.claude/skills/tracker/SKILL.md` — it defines the column conventions, valid values, and the Context & Sources that inform every row.
> **Editorial split**: per-Phase row tables + Engineering Prerequisites are generator-emitted (`/tracker generate --candidate` writes to `submission-tracker.candidate.md`; merge into this canonical when content changes). Chrome sections (Context & Sources, Legends, Cross-Milestone Summary, Reviewer Sign-off, Changelog, Deliverable Details, end-of-file Scale tables) are hand-managed — they survive generator regenerations because `emit_full_markdown()` only owns the row tables (`--write-canonical` overwrites everything; do NOT use it until upstream chrome-preservation lands).

## Context & Sources


### 1. Composition Manifest (source of truth for what's included)
- [`docs/project/submissions/510k/composition-manifest.md`](../510k/composition-manifest.md) — PP3500 510(k) filing composition
- `docs/project/submissions/qsub/composition-manifest.md` — pre-submission package (planned, Stage 3 of ben/047)
- `docs/project/submissions/pccp/composition-manifest.md` — PCCP additive composition (planned, Stage 4 of ben/047)

### 2. Project Manifest — DHFs in this filing
| DHF | Role in filing | Path |
|---|---|---|
| `pca-device` | Lead DHF (full) | [`docs/project/dhfs/pca-device/`](../../dhfs/pca-device/) |
| `connectivity-adapter` | Cybersecurity posture only (MDDS) | [`docs/project/dhfs/connectivity-adapter/`](../../dhfs/connectivity-adapter/) |
| `cloud-suite/dhfs/drug-library-manager` | Bundled accessory (Class II SaMD) — TBD | [`docs/project/dhfs/cloud-suite/dhfs/drug-library-manager/`](../../dhfs/cloud-suite/dhfs/drug-library-manager/) |

### 3. System SADs (drive Scope and per-module splits)
- [`docs/project/dhfs/pca-device/design-controls/architecture/pca-device-system-sad.md`](../../dhfs/pca-device/design-controls/architecture/pca-device-system-sad.md) — 7 modules (M1–M7)
- [`docs/project/dhfs/connectivity-adapter/design-controls/architecture/connectivity-adapter-system-sad.md`](../../dhfs/connectivity-adapter/design-controls/architecture/connectivity-adapter-system-sad.md) — 7 modules (A1–A7)
- [`docs/project/dhfs/cloud-suite/dhfs/drug-library-manager/design-controls/architecture/drug-library-manager-system-sad.md`](../../dhfs/cloud-suite/dhfs/drug-library-manager/design-controls/architecture/drug-library-manager-system-sad.md) — 7 modules (D1–D7)

### 4. Regulatory Strategy
- [`docs/project/strategies/regulatory-strategy.md`](../../strategies/regulatory-strategy.md) — shared; Filing Scope (PCA alone), Critical-Requirement Carve-out, Component Classification & Filing Posture, DHF Filing Composition Pattern

### 5. Milestone Catalog
- [`docs/project/milestones/regulatory.yml`](../../milestones/regulatory.yml) — 4 filing milestones (QSub → 510k+PCCP → LMR1 → LMR2) with per-(DHF, doc, version) bindings
- [`docs/project/milestones/engineering.yml`](../../milestones/engineering.yml) — 20 cross-cutting engineering prerequisites (ENG1–ENG20) for `pccp-release` + `lmr2-release` milestones

### 6. FDA Guidance Documents (shared)
- [`docs/external/fda-guidance/`](../../../external/fda-guidance/) — `510k-se.md`, `sw-functions.md`, `sw-changes.md`, `cybersecurity.md`, `pccp-general.md`, `pccp-aiml.md`, `ai-dsf-lifecycle.md`, `cds.md`, `mfd.md`, `qsub.md`

## Status Legend


| Status | Meaning |
|---|---|
| **Approved** | Substantially complete; reviewed and signed off |
| **In Review** | Reviewed; revisions in flight |
| **Drafted** | Initial draft exists, pending review |
| **Drafting** | Author is in the B6 Create Draft authoring workflow |
| **Needs Revision** | Reviewed; revisions required |
| **Not Started** | No work product exists |
| **Inherited** | Evidence lives in a different DHF (e.g., privacy/SOUP from platform DHF) |
| **N/A** | Binding not applicable to this scope |

## Scope Legend


| Scope | Meaning |
|---|---|
| **Suite** | System-level deliverable applying to the whole PP3500 filing |
| **pca-device** | pca-device DHF-scoped evidence (most current rows) |
| **(submission)** | Filing-narrative content authored under `submissions/<filing>/` (cover letter, summary, indications, predicate, PCCP narrative) |

Future per-module scopes when bindings expand: `connectivity-adapter`, `drug-library-manager` (with `a`/`b`/`c` letter suffixes on row IDs — see Two-Level Deliverable Model).

## Phase Legend


| Phase | Meaning |
|---|---|
| **QSub** | Pre-submission meeting (`qsub-release` milestone) — validate PCCP scope, predicate, module classification before formal filing |
| **510k+PCCP** | Filing event (`pccp-release` milestone) — K210345 demo. NOT the version that ships to customers. |
| **LMR1** | First commercial release (`lmr1-release` milestone) — what ships; built in parallel with the FDA review window |
| **LMR2** | Second commercial release (`lmr2-release` milestone) — further PCCP envelope expansion, AI/ML envelope |

## REF Priority


Single citation per row in priority order: **FDA → IEC → other Standards → QMS**. Full applicable list goes in the Deliverable Details appendix.

## Two-Level Deliverable Model


Deliverables are tracked at two levels where the architecture demands it:
- **Device-level** items apply across the whole filing.
- **Per-Module** items split into one row per component with letter suffixes:
  - **a** = pca-device
  - **b** = drug-library-manager
  - **c** = connectivity-adapter (cyber-only evidence)

Generator-emitted rows currently use `PC` (pca-device) prefix only; cross-DHF letter suffixes appear when milestone bindings expand to additional DHFs (Stage 5 of ben/047).

## Phase: QSub


### (submission)


_Filing-narrative pieces authored under `submissions/qsub/`. Each carries the disabled `tracker-action-btn` placeholder in the Path column — `render.py` wires it into a live B6 Create Draft button when status is `Not Started` / `Drafting` / `Drafted` / `Needs Revision`._

| # | Deliverable | Scope | Phase | REF | Effort | Status | Path |
|---|---|---|---|---|---|---|---|
| Q4 | Q-Sub cover letter | Suite | QSub | FDA Q-Sub Guidance Appendix 1 | Low | **Not Started** | <button class="tracker-action-btn" disabled>Create Draft</button> |
| Q5 | Device description (Q-Sub formal) | Suite | QSub | FDA Q-Sub Guidance § Content requirements | Med | **Not Started** | <button class="tracker-action-btn" disabled>Create Draft</button> |
| Q6 | Proposed indications for use | Suite | QSub | FDA Q-Sub Guidance § Content requirements | Low | **Not Started** | <button class="tracker-action-btn" disabled>Create Draft</button> |
| Q7 | Predicate device analysis (Q-Sub summary) | Suite | QSub | FDA SE Guidance (2014) §III | Med | **Not Started** | <button class="tracker-action-btn" disabled>Create Draft</button> |
| Q8 | PCCP summary for FDA feedback | Suite | QSub | FDA AI/ML PCCP (Sept 2023) §V | Med | **Not Started** | <button class="tracker-action-btn" disabled>Create Draft</button> |

### Suite (system DHF, IEC 62304 Class C)


| # | Deliverable | Scope | Phase | REF | Effort | Status | Path |
|---|---|---|---|---|---|---|---|
| Q-PC1 | System Software Architecture Document (SAD) | Suite | QSub | — | — | **Not Started** | [`pca-device-system-sad.md`](docs/project/dhfs/pca-device/design-controls/architecture/pca-device-system-sad.md) |
| Q-PC26 | Design & Development Plan | Suite | QSub | — | — | **Not Started** | [`GL-TMP-DC-001-design-and-development-plan.md`](docs/project/dhfs/pca-device/design-controls/plans/GL-TMP-DC-001-design-and-development-plan.md) |
| Q-PC25 | Use Specification (User Needs) | Suite | QSub | — | — | **Not Started** | [`GL-TMP-UC-001-use-specification.md`](docs/project/dhfs/pca-device/design-controls/user-needs/GL-TMP-UC-001-use-specification.md) |
| Q-PC2 | Design Input Specification (SRS) | Suite | QSub | — | — | **Not Started** | [`GL-TMP-DC-002-design-input-specification.md`](docs/project/dhfs/pca-device/design-controls/requirements/GL-TMP-DC-002-design-input-specification.md) |
| Q-PC27 | Verification & Validation Protocol & Report | Suite | QSub | — | — | **Not Started** | [`GL-TMP-DC-003-verification-protocol-report.md`](docs/project/dhfs/pca-device/design-controls/vnv/GL-TMP-DC-003-verification-protocol-report.md) |
| Q-PC28 | Design Trace Matrix (UN ↔ DI ↔ Arch ↔ V&V) | Suite | QSub | — | — | **Not Started** | [`GL-SOP-DC-003-trace-matrix-overview.md`](docs/project/dhfs/pca-device/design-controls/trace-matrix/GL-SOP-DC-003-trace-matrix-overview.md) |
| Q-PC16 | Tool Validation Records | Suite | QSub | — | — | **Not Started** | [`GL-TMP-DC-003-tool-validation-record.md`](docs/project/dhfs/pca-device/design-controls/tool-validation/GL-TMP-DC-003-tool-validation-record.md) |
| Q-PC9 | Risk Management Report (ISO 14971) | Suite | QSub | — | — | **Not Started** | [`GL-TMP-RM-002-risk-management-report.md`](docs/project/dhfs/pca-device/risk-management/GL-TMP-RM-002-risk-management-report.md) |
| Q-PC23 | Clinical Evaluation Report | Suite | QSub | — | — | **Not Started** | [`clinical`](docs/project/dhfs/pca-device/clinical/) |
| Q-PC24 | Periodic Safety Update Report (PSUR) | Suite | QSub | — | — | **Not Started** | [`GL-SOP-PM-001-psur.md`](docs/project/dhfs/pca-device/postmarket/GL-SOP-PM-001-psur.md) |
| Q-PC12 | Cybersecurity Vulnerability Management Plan | Suite | QSub | — | — | **Not Started** | [`GL-SOP-SW-004-vulnerability-management-plan.md`](docs/project/dhfs/pca-device/cybersecurity/GL-SOP-SW-004-vulnerability-management-plan.md) |

### Adapter (item DHF, SaMD Class I, IEC 62304 Class B)


| # | Deliverable | Scope | Phase | REF | Effort | Status | Path |
|---|---|---|---|---|---|---|---|
| Q-CA1 | architecture | Adapter | QSub | — | — | **Not Started** | [`connectivity-adapter-system-sad.md`](docs/project/dhfs/connectivity-adapter/design-controls/architecture/connectivity-adapter-system-sad.md) |
| Q-CA26 | plans | Adapter | QSub | — | — | **Not Started** | [`GL-TMP-DC-001-design-and-development-plan.md`](docs/project/dhfs/connectivity-adapter/design-controls/plans/GL-TMP-DC-001-design-and-development-plan.md) |
| Q-CA25 | user-needs | Adapter | QSub | — | — | **Not Started** | [`GL-TMP-UC-001-use-specification.md`](docs/project/dhfs/connectivity-adapter/design-controls/user-needs/GL-TMP-UC-001-use-specification.md) |
| Q-CA2 | requirements | Adapter | QSub | — | — | **Not Started** | [`GL-TMP-DC-002-design-input-specification.md`](docs/project/dhfs/connectivity-adapter/design-controls/requirements/GL-TMP-DC-002-design-input-specification.md) |
| Q-CA27 | vnv | Adapter | QSub | — | — | **Not Started** | [`GL-TMP-DC-003-verification-protocol-report.md`](docs/project/dhfs/connectivity-adapter/design-controls/vnv/GL-TMP-DC-003-verification-protocol-report.md) |
| Q-CA28 | trace-matrix | Adapter | QSub | — | — | **Not Started** | [`GL-SOP-DC-003-trace-matrix-overview.md`](docs/project/dhfs/connectivity-adapter/design-controls/trace-matrix/GL-SOP-DC-003-trace-matrix-overview.md) |
| Q-CA16 | tool-validation | Adapter | QSub | — | — | **Not Started** | [`GL-TMP-DC-003-tool-validation-record.md`](docs/project/dhfs/connectivity-adapter/design-controls/tool-validation/GL-TMP-DC-003-tool-validation-record.md) |
| Q-CA9 | risk-management | Adapter | QSub | — | — | **Not Started** | [`GL-TMP-RM-002-risk-management-report.md`](docs/project/dhfs/connectivity-adapter/risk-management/GL-TMP-RM-002-risk-management-report.md) |
| Q-CA23 | clinical | Adapter | QSub | — | — | **Not Started** | [`clinical`](docs/project/dhfs/connectivity-adapter/clinical/) |
| Q-CA24 | postmarket | Adapter | QSub | — | — | **Not Started** | [`GL-SOP-PM-001-psur.md`](docs/project/dhfs/connectivity-adapter/postmarket/GL-SOP-PM-001-psur.md) |
| Q-CA12 | cybersecurity | Adapter | QSub | — | — | **Not Started** | [`GL-SOP-SW-004-vulnerability-management-plan.md`](docs/project/dhfs/connectivity-adapter/cybersecurity/GL-SOP-SW-004-vulnerability-management-plan.md) |

---

### Cloud (system DHF)


| # | Deliverable | Scope | Phase | REF | Effort | Status | Path |
|---|---|---|---|---|---|---|---|
| Q-CS1 | architecture | Cloud | QSub | — | — | **Not Started** | [`architecture`](docs/project/dhfs/cloud-suite/design-controls/architecture/) |
| Q-CS26 | plans | Cloud | QSub | — | — | **Not Started** | [`GL-TMP-DC-001-design-and-development-plan.md`](docs/project/dhfs/cloud-suite/design-controls/plans/GL-TMP-DC-001-design-and-development-plan.md) |
| Q-CS25 | user-needs | Cloud | QSub | — | — | **Not Started** | [`GL-TMP-UC-001-use-specification.md`](docs/project/dhfs/cloud-suite/design-controls/user-needs/GL-TMP-UC-001-use-specification.md) |
| Q-CS2 | requirements | Cloud | QSub | — | — | **Not Started** | [`GL-TMP-DC-002-design-input-specification.md`](docs/project/dhfs/cloud-suite/design-controls/requirements/GL-TMP-DC-002-design-input-specification.md) |
| Q-CS27 | vnv | Cloud | QSub | — | — | **Not Started** | [`GL-TMP-DC-003-verification-protocol-report.md`](docs/project/dhfs/cloud-suite/design-controls/vnv/GL-TMP-DC-003-verification-protocol-report.md) |
| Q-CS28 | trace-matrix | Cloud | QSub | — | — | **Not Started** | [`GL-SOP-DC-003-trace-matrix-overview.md`](docs/project/dhfs/cloud-suite/design-controls/trace-matrix/GL-SOP-DC-003-trace-matrix-overview.md) |
| Q-CS16 | tool-validation | Cloud | QSub | — | — | **Not Started** | [`GL-TMP-DC-003-tool-validation-record.md`](docs/project/dhfs/cloud-suite/design-controls/tool-validation/GL-TMP-DC-003-tool-validation-record.md) |
| Q-CS9 | risk-management | Cloud | QSub | — | — | **Not Started** | [`GL-TMP-RM-002-risk-management-report.md`](docs/project/dhfs/cloud-suite/risk-management/GL-TMP-RM-002-risk-management-report.md) |
| Q-CS23 | clinical | Cloud | QSub | — | — | **Not Started** | [`clinical`](docs/project/dhfs/cloud-suite/clinical/) |
| Q-CS24 | postmarket | Cloud | QSub | — | — | **Not Started** | [`GL-SOP-PM-001-psur.md`](docs/project/dhfs/cloud-suite/postmarket/GL-SOP-PM-001-psur.md) |
| Q-CS12 | cybersecurity | Cloud | QSub | — | — | **Not Started** | [`GL-SOP-SW-004-vulnerability-management-plan.md`](docs/project/dhfs/cloud-suite/cybersecurity/GL-SOP-SW-004-vulnerability-management-plan.md) |

---

## Phase: 510k+PCCP


### (submission)


_PCCP Core + Support narrative pieces. Authored under `dhfs/pca-device/design-controls/pccp/` once the B6 Create Draft workflow lands content; each carries the disabled `tracker-action-btn` placeholder until then._

| # | Deliverable | Scope | Phase | REF | Effort | Status | Path |
|---|---|---|---|---|---|---|---|
| PCCP1 | PCCP Cover Section | Suite | 510k+PCCP | FDA PCCP General §IV.A | Low | **Not Started** | <button class="tracker-action-btn" disabled>Create Draft</button> |
| PCCP2 | PCCP — Description of Modifications | Suite | 510k+PCCP | FDA PCCP General §IV.B | High | **Not Started** | <button class="tracker-action-btn" disabled>Create Draft</button> |
| PCCP3 | PCCP — Modification Protocol | Suite | 510k+PCCP | FDA PCCP General §V | High | **Not Started** | <button class="tracker-action-btn" disabled>Create Draft</button> |
| PCCP4 | PCCP — Impact Assessment | Suite | 510k+PCCP | FDA PCCP General §VI | Med | **Not Started** | <button class="tracker-action-btn" disabled>Create Draft</button> |
| PCCP5 | PCCP Traceability Table | Suite | 510k+PCCP | FDA PCCP General §VII | Med | **Not Started** | <button class="tracker-action-btn" disabled>Create Draft</button> |
| PCCP6 | PCCP Public Summary | Suite | 510k+PCCP | FDA PCCP General §VIII | Low | **Not Started** | <button class="tracker-action-btn" disabled>Create Draft</button> |
| PS1 | Drug Library Update Protocol | Suite | 510k+PCCP | FDA PCCP General §V | High | **Not Started** | <button class="tracker-action-btn" disabled>Create Draft</button> |
| PS2 | Drug Library V&V Plan | Suite | 510k+PCCP | FDA PCCP General §V.B | Med | **Not Started** | <button class="tracker-action-btn" disabled>Create Draft</button> |
| PS3 | Drug Library Acceptance Criteria | Suite | 510k+PCCP | FDA PCCP General §V.C | Med | **Not Started** | <button class="tracker-action-btn" disabled>Create Draft</button> |
| PS4 | Firmware Update Protocol | Suite | 510k+PCCP | FDA PCCP General §V | Med | **Not Started** | <button class="tracker-action-btn" disabled>Create Draft</button> |
| PS5 | Firmware Update V&V Plan | Suite | 510k+PCCP | FDA PCCP General §V.B | Med | **Not Started** | <button class="tracker-action-btn" disabled>Create Draft</button> |

### Suite (system DHF, IEC 62304 Class C)


| # | Deliverable | Scope | Phase | REF | Effort | Status | Path |
|---|---|---|---|---|---|---|---|
| PC1 | System Software Architecture Document (SAD) | Suite | 510k+PCCP | — | — | **Not Started** | [`pca-device-system-sad.md`](docs/project/dhfs/pca-device/design-controls/architecture/pca-device-system-sad.md) |
| PC26 | Design & Development Plan | Suite | 510k+PCCP | — | — | **Not Started** | [`GL-TMP-DC-001-design-and-development-plan.md`](docs/project/dhfs/pca-device/design-controls/plans/GL-TMP-DC-001-design-and-development-plan.md) |
| PC25 | Use Specification (User Needs) | Suite | 510k+PCCP | — | — | **Not Started** | [`GL-TMP-UC-001-use-specification.md`](docs/project/dhfs/pca-device/design-controls/user-needs/GL-TMP-UC-001-use-specification.md) |
| PC2 | Design Input Specification (SRS) | Suite | 510k+PCCP | — | — | **Not Started** | [`GL-TMP-DC-002-design-input-specification.md`](docs/project/dhfs/pca-device/design-controls/requirements/GL-TMP-DC-002-design-input-specification.md) |
| PC27 | Verification & Validation Protocol & Report | Suite | 510k+PCCP | — | — | **Not Started** | [`GL-TMP-DC-003-verification-protocol-report.md`](docs/project/dhfs/pca-device/design-controls/vnv/GL-TMP-DC-003-verification-protocol-report.md) |
| PC28 | Design Trace Matrix (UN ↔ DI ↔ Arch ↔ V&V) | Suite | 510k+PCCP | — | — | **Not Started** | [`GL-SOP-DC-003-trace-matrix-overview.md`](docs/project/dhfs/pca-device/design-controls/trace-matrix/GL-SOP-DC-003-trace-matrix-overview.md) |
| PC16 | Tool Validation Records | Suite | 510k+PCCP | — | — | **Not Started** | [`GL-TMP-DC-003-tool-validation-record.md`](docs/project/dhfs/pca-device/design-controls/tool-validation/GL-TMP-DC-003-tool-validation-record.md) |
| PC9 | Risk Management Report (ISO 14971) | Suite | 510k+PCCP | — | — | **Not Started** | [`GL-TMP-RM-002-risk-management-report.md`](docs/project/dhfs/pca-device/risk-management/GL-TMP-RM-002-risk-management-report.md) |
| PC23 | Clinical Evaluation Report | Suite | 510k+PCCP | — | — | **Not Started** | [`clinical`](docs/project/dhfs/pca-device/clinical/) |
| PC24 | Periodic Safety Update Report (PSUR) | Suite | 510k+PCCP | — | — | **Not Started** | [`GL-SOP-PM-001-psur.md`](docs/project/dhfs/pca-device/postmarket/GL-SOP-PM-001-psur.md) |
| PC12 | Cybersecurity Vulnerability Management Plan | Suite | 510k+PCCP | — | — | **Not Started** | [`GL-SOP-SW-004-vulnerability-management-plan.md`](docs/project/dhfs/pca-device/cybersecurity/GL-SOP-SW-004-vulnerability-management-plan.md) |

### Adapter (item DHF, SaMD Class I, IEC 62304 Class B)


| # | Deliverable | Scope | Phase | REF | Effort | Status | Path |
|---|---|---|---|---|---|---|---|
| CA1 | architecture | Adapter | 510k+PCCP | — | — | **Not Started** | [`connectivity-adapter-system-sad.md`](docs/project/dhfs/connectivity-adapter/design-controls/architecture/connectivity-adapter-system-sad.md) |
| CA26 | plans | Adapter | 510k+PCCP | — | — | **Not Started** | [`GL-TMP-DC-001-design-and-development-plan.md`](docs/project/dhfs/connectivity-adapter/design-controls/plans/GL-TMP-DC-001-design-and-development-plan.md) |
| CA25 | user-needs | Adapter | 510k+PCCP | — | — | **Not Started** | [`GL-TMP-UC-001-use-specification.md`](docs/project/dhfs/connectivity-adapter/design-controls/user-needs/GL-TMP-UC-001-use-specification.md) |
| CA2 | requirements | Adapter | 510k+PCCP | — | — | **Not Started** | [`GL-TMP-DC-002-design-input-specification.md`](docs/project/dhfs/connectivity-adapter/design-controls/requirements/GL-TMP-DC-002-design-input-specification.md) |
| CA27 | vnv | Adapter | 510k+PCCP | — | — | **Not Started** | [`GL-TMP-DC-003-verification-protocol-report.md`](docs/project/dhfs/connectivity-adapter/design-controls/vnv/GL-TMP-DC-003-verification-protocol-report.md) |
| CA28 | trace-matrix | Adapter | 510k+PCCP | — | — | **Not Started** | [`GL-SOP-DC-003-trace-matrix-overview.md`](docs/project/dhfs/connectivity-adapter/design-controls/trace-matrix/GL-SOP-DC-003-trace-matrix-overview.md) |
| CA16 | tool-validation | Adapter | 510k+PCCP | — | — | **Not Started** | [`GL-TMP-DC-003-tool-validation-record.md`](docs/project/dhfs/connectivity-adapter/design-controls/tool-validation/GL-TMP-DC-003-tool-validation-record.md) |
| CA9 | risk-management | Adapter | 510k+PCCP | — | — | **Not Started** | [`GL-TMP-RM-002-risk-management-report.md`](docs/project/dhfs/connectivity-adapter/risk-management/GL-TMP-RM-002-risk-management-report.md) |
| CA23 | clinical | Adapter | 510k+PCCP | — | — | **Not Started** | [`clinical`](docs/project/dhfs/connectivity-adapter/clinical/) |
| CA24 | postmarket | Adapter | 510k+PCCP | — | — | **Not Started** | [`GL-SOP-PM-001-psur.md`](docs/project/dhfs/connectivity-adapter/postmarket/GL-SOP-PM-001-psur.md) |
| CA12 | cybersecurity | Adapter | 510k+PCCP | — | — | **Not Started** | [`GL-SOP-SW-004-vulnerability-management-plan.md`](docs/project/dhfs/connectivity-adapter/cybersecurity/GL-SOP-SW-004-vulnerability-management-plan.md) |

---

### Cloud (system DHF)


| # | Deliverable | Scope | Phase | REF | Effort | Status | Path |
|---|---|---|---|---|---|---|---|
| CS1 | architecture | Cloud | 510k+PCCP | — | — | **Not Started** | [`architecture`](docs/project/dhfs/cloud-suite/design-controls/architecture/) |
| CS26 | plans | Cloud | 510k+PCCP | — | — | **Not Started** | [`GL-TMP-DC-001-design-and-development-plan.md`](docs/project/dhfs/cloud-suite/design-controls/plans/GL-TMP-DC-001-design-and-development-plan.md) |
| CS25 | user-needs | Cloud | 510k+PCCP | — | — | **Not Started** | [`GL-TMP-UC-001-use-specification.md`](docs/project/dhfs/cloud-suite/design-controls/user-needs/GL-TMP-UC-001-use-specification.md) |
| CS2 | requirements | Cloud | 510k+PCCP | — | — | **Not Started** | [`GL-TMP-DC-002-design-input-specification.md`](docs/project/dhfs/cloud-suite/design-controls/requirements/GL-TMP-DC-002-design-input-specification.md) |
| CS27 | vnv | Cloud | 510k+PCCP | — | — | **Not Started** | [`GL-TMP-DC-003-verification-protocol-report.md`](docs/project/dhfs/cloud-suite/design-controls/vnv/GL-TMP-DC-003-verification-protocol-report.md) |
| CS28 | trace-matrix | Cloud | 510k+PCCP | — | — | **Not Started** | [`GL-SOP-DC-003-trace-matrix-overview.md`](docs/project/dhfs/cloud-suite/design-controls/trace-matrix/GL-SOP-DC-003-trace-matrix-overview.md) |
| CS16 | tool-validation | Cloud | 510k+PCCP | — | — | **Not Started** | [`GL-TMP-DC-003-tool-validation-record.md`](docs/project/dhfs/cloud-suite/design-controls/tool-validation/GL-TMP-DC-003-tool-validation-record.md) |
| CS9 | risk-management | Cloud | 510k+PCCP | — | — | **Not Started** | [`GL-TMP-RM-002-risk-management-report.md`](docs/project/dhfs/cloud-suite/risk-management/GL-TMP-RM-002-risk-management-report.md) |
| CS23 | clinical | Cloud | 510k+PCCP | — | — | **Not Started** | [`clinical`](docs/project/dhfs/cloud-suite/clinical/) |
| CS24 | postmarket | Cloud | 510k+PCCP | — | — | **Not Started** | [`GL-SOP-PM-001-psur.md`](docs/project/dhfs/cloud-suite/postmarket/GL-SOP-PM-001-psur.md) |
| CS12 | cybersecurity | Cloud | 510k+PCCP | — | — | **Not Started** | [`GL-SOP-SW-004-vulnerability-management-plan.md`](docs/project/dhfs/cloud-suite/cybersecurity/GL-SOP-SW-004-vulnerability-management-plan.md) |

---

## Phase: LMR1


### Suite (system DHF, IEC 62304 Class C)


| # | Deliverable | Scope | Phase | REF | Effort | Status | Path |
|---|---|---|---|---|---|---|---|
| L1-PC1 | System Software Architecture Document (SAD) | Suite | LMR1 | — | — | **Not Started** | [`pca-device-system-sad.md`](docs/project/dhfs/pca-device/design-controls/architecture/pca-device-system-sad.md) |
| L1-PC26 | Design & Development Plan | Suite | LMR1 | — | — | **Not Started** | [`GL-TMP-DC-001-design-and-development-plan.md`](docs/project/dhfs/pca-device/design-controls/plans/GL-TMP-DC-001-design-and-development-plan.md) |
| L1-PC25 | Use Specification (User Needs) | Suite | LMR1 | — | — | **Not Started** | [`GL-TMP-UC-001-use-specification.md`](docs/project/dhfs/pca-device/design-controls/user-needs/GL-TMP-UC-001-use-specification.md) |
| L1-PC2 | Design Input Specification (SRS) | Suite | LMR1 | — | — | **Not Started** | [`GL-TMP-DC-002-design-input-specification.md`](docs/project/dhfs/pca-device/design-controls/requirements/GL-TMP-DC-002-design-input-specification.md) |
| L1-PC27 | Verification & Validation Protocol & Report | Suite | LMR1 | — | — | **Not Started** | [`GL-TMP-DC-003-verification-protocol-report.md`](docs/project/dhfs/pca-device/design-controls/vnv/GL-TMP-DC-003-verification-protocol-report.md) |
| L1-PC28 | Design Trace Matrix (UN ↔ DI ↔ Arch ↔ V&V) | Suite | LMR1 | — | — | **Not Started** | [`GL-SOP-DC-003-trace-matrix-overview.md`](docs/project/dhfs/pca-device/design-controls/trace-matrix/GL-SOP-DC-003-trace-matrix-overview.md) |
| L1-PC16 | Tool Validation Records | Suite | LMR1 | — | — | **Not Started** | [`GL-TMP-DC-003-tool-validation-record.md`](docs/project/dhfs/pca-device/design-controls/tool-validation/GL-TMP-DC-003-tool-validation-record.md) |
| L1-PC9 | Risk Management Report (ISO 14971) | Suite | LMR1 | — | — | **Not Started** | [`GL-TMP-RM-002-risk-management-report.md`](docs/project/dhfs/pca-device/risk-management/GL-TMP-RM-002-risk-management-report.md) |
| L1-PC23 | Clinical Evaluation Report | Suite | LMR1 | — | — | **Not Started** | [`clinical`](docs/project/dhfs/pca-device/clinical/) |
| L1-PC24 | Periodic Safety Update Report (PSUR) | Suite | LMR1 | — | — | **Not Started** | [`GL-SOP-PM-001-psur.md`](docs/project/dhfs/pca-device/postmarket/GL-SOP-PM-001-psur.md) |
| L1-PC12 | Cybersecurity Vulnerability Management Plan | Suite | LMR1 | — | — | **Not Started** | [`GL-SOP-SW-004-vulnerability-management-plan.md`](docs/project/dhfs/pca-device/cybersecurity/GL-SOP-SW-004-vulnerability-management-plan.md) |

### Adapter (item DHF, SaMD Class I, IEC 62304 Class B)


| # | Deliverable | Scope | Phase | REF | Effort | Status | Path |
|---|---|---|---|---|---|---|---|
| L1-CA1 | architecture | Adapter | LMR1 | — | — | **Not Started** | [`connectivity-adapter-system-sad.md`](docs/project/dhfs/connectivity-adapter/design-controls/architecture/connectivity-adapter-system-sad.md) |
| L1-CA26 | plans | Adapter | LMR1 | — | — | **Not Started** | [`GL-TMP-DC-001-design-and-development-plan.md`](docs/project/dhfs/connectivity-adapter/design-controls/plans/GL-TMP-DC-001-design-and-development-plan.md) |
| L1-CA25 | user-needs | Adapter | LMR1 | — | — | **Not Started** | [`GL-TMP-UC-001-use-specification.md`](docs/project/dhfs/connectivity-adapter/design-controls/user-needs/GL-TMP-UC-001-use-specification.md) |
| L1-CA2 | requirements | Adapter | LMR1 | — | — | **Not Started** | [`GL-TMP-DC-002-design-input-specification.md`](docs/project/dhfs/connectivity-adapter/design-controls/requirements/GL-TMP-DC-002-design-input-specification.md) |
| L1-CA27 | vnv | Adapter | LMR1 | — | — | **Not Started** | [`GL-TMP-DC-003-verification-protocol-report.md`](docs/project/dhfs/connectivity-adapter/design-controls/vnv/GL-TMP-DC-003-verification-protocol-report.md) |
| L1-CA28 | trace-matrix | Adapter | LMR1 | — | — | **Not Started** | [`GL-SOP-DC-003-trace-matrix-overview.md`](docs/project/dhfs/connectivity-adapter/design-controls/trace-matrix/GL-SOP-DC-003-trace-matrix-overview.md) |
| L1-CA16 | tool-validation | Adapter | LMR1 | — | — | **Not Started** | [`GL-TMP-DC-003-tool-validation-record.md`](docs/project/dhfs/connectivity-adapter/design-controls/tool-validation/GL-TMP-DC-003-tool-validation-record.md) |
| L1-CA9 | risk-management | Adapter | LMR1 | — | — | **Not Started** | [`GL-TMP-RM-002-risk-management-report.md`](docs/project/dhfs/connectivity-adapter/risk-management/GL-TMP-RM-002-risk-management-report.md) |
| L1-CA23 | clinical | Adapter | LMR1 | — | — | **Not Started** | [`clinical`](docs/project/dhfs/connectivity-adapter/clinical/) |
| L1-CA24 | postmarket | Adapter | LMR1 | — | — | **Not Started** | [`GL-SOP-PM-001-psur.md`](docs/project/dhfs/connectivity-adapter/postmarket/GL-SOP-PM-001-psur.md) |
| L1-CA12 | cybersecurity | Adapter | LMR1 | — | — | **Not Started** | [`GL-SOP-SW-004-vulnerability-management-plan.md`](docs/project/dhfs/connectivity-adapter/cybersecurity/GL-SOP-SW-004-vulnerability-management-plan.md) |

---

### Cloud (system DHF)


| # | Deliverable | Scope | Phase | REF | Effort | Status | Path |
|---|---|---|---|---|---|---|---|
| L1-CS1 | architecture | Cloud | LMR1 | — | — | **Not Started** | [`architecture`](docs/project/dhfs/cloud-suite/design-controls/architecture/) |
| L1-CS26 | plans | Cloud | LMR1 | — | — | **Not Started** | [`GL-TMP-DC-001-design-and-development-plan.md`](docs/project/dhfs/cloud-suite/design-controls/plans/GL-TMP-DC-001-design-and-development-plan.md) |
| L1-CS25 | user-needs | Cloud | LMR1 | — | — | **Not Started** | [`GL-TMP-UC-001-use-specification.md`](docs/project/dhfs/cloud-suite/design-controls/user-needs/GL-TMP-UC-001-use-specification.md) |
| L1-CS2 | requirements | Cloud | LMR1 | — | — | **Not Started** | [`GL-TMP-DC-002-design-input-specification.md`](docs/project/dhfs/cloud-suite/design-controls/requirements/GL-TMP-DC-002-design-input-specification.md) |
| L1-CS27 | vnv | Cloud | LMR1 | — | — | **Not Started** | [`GL-TMP-DC-003-verification-protocol-report.md`](docs/project/dhfs/cloud-suite/design-controls/vnv/GL-TMP-DC-003-verification-protocol-report.md) |
| L1-CS28 | trace-matrix | Cloud | LMR1 | — | — | **Not Started** | [`GL-SOP-DC-003-trace-matrix-overview.md`](docs/project/dhfs/cloud-suite/design-controls/trace-matrix/GL-SOP-DC-003-trace-matrix-overview.md) |
| L1-CS16 | tool-validation | Cloud | LMR1 | — | — | **Not Started** | [`GL-TMP-DC-003-tool-validation-record.md`](docs/project/dhfs/cloud-suite/design-controls/tool-validation/GL-TMP-DC-003-tool-validation-record.md) |
| L1-CS9 | risk-management | Cloud | LMR1 | — | — | **Not Started** | [`GL-TMP-RM-002-risk-management-report.md`](docs/project/dhfs/cloud-suite/risk-management/GL-TMP-RM-002-risk-management-report.md) |
| L1-CS23 | clinical | Cloud | LMR1 | — | — | **Not Started** | [`clinical`](docs/project/dhfs/cloud-suite/clinical/) |
| L1-CS24 | postmarket | Cloud | LMR1 | — | — | **Not Started** | [`GL-SOP-PM-001-psur.md`](docs/project/dhfs/cloud-suite/postmarket/GL-SOP-PM-001-psur.md) |
| L1-CS12 | cybersecurity | Cloud | LMR1 | — | — | **Not Started** | [`GL-SOP-SW-004-vulnerability-management-plan.md`](docs/project/dhfs/cloud-suite/cybersecurity/GL-SOP-SW-004-vulnerability-management-plan.md) |

---

## Phase: LMR2


### (submission)


_AI/ML PCCP-driven documentation. Surfaces with LMR2 since the AI/ML envelope ships in that release per regulatory strategy._

| # | Deliverable | Scope | Phase | REF | Effort | Status | Path |
|---|---|---|---|---|---|---|---|
| AI1 | AI-DSF Description of Modifications | Suite | LMR2 | FDA PCCP AI/ML §IV | Med | **Not Started** | <button class="tracker-action-btn" disabled>Create Draft</button> |
| AI2 | AI Re-Training Practices Protocol | Suite | LMR2 | FDA PCCP AI/ML §V.A | Med | **Not Started** | <button class="tracker-action-btn" disabled>Create Draft</button> |
| AI3 | AI Data Management Practices | Suite | LMR2 | FDA PCCP AI/ML §V.B | Med | **Not Started** | <button class="tracker-action-btn" disabled>Create Draft</button> |
| AI4 | AI Performance Evaluation Plan | Suite | LMR2 | FDA PCCP AI/ML §V.C | High | **Not Started** | <button class="tracker-action-btn" disabled>Create Draft</button> |
| AI5 | AI Update Procedures & User Communication | Suite | LMR2 | FDA PCCP AI/ML §V.D | Med | **Not Started** | <button class="tracker-action-btn" disabled>Create Draft</button> |
| AI6 | AI Drift Monitoring Plan | Suite | LMR2 | FDA PCCP AI/ML §V.E; AI-DSF | Med | **Not Started** | <button class="tracker-action-btn" disabled>Create Draft</button> |

### Suite (system DHF, IEC 62304 Class C)


| # | Deliverable | Scope | Phase | REF | Effort | Status | Path |
|---|---|---|---|---|---|---|---|
| L2-PC1 | System Software Architecture Document (SAD) | Suite | LMR2 | — | — | **Not Started** | [`pca-device-system-sad.md`](docs/project/dhfs/pca-device/design-controls/architecture/pca-device-system-sad.md) |
| L2-PC26 | Design & Development Plan | Suite | LMR2 | — | — | **Not Started** | [`GL-TMP-DC-001-design-and-development-plan.md`](docs/project/dhfs/pca-device/design-controls/plans/GL-TMP-DC-001-design-and-development-plan.md) |
| L2-PC25 | Use Specification (User Needs) | Suite | LMR2 | — | — | **Not Started** | [`GL-TMP-UC-001-use-specification.md`](docs/project/dhfs/pca-device/design-controls/user-needs/GL-TMP-UC-001-use-specification.md) |
| L2-PC2 | Design Input Specification (SRS) | Suite | LMR2 | — | — | **Not Started** | [`GL-TMP-DC-002-design-input-specification.md`](docs/project/dhfs/pca-device/design-controls/requirements/GL-TMP-DC-002-design-input-specification.md) |
| L2-PC27 | Verification & Validation Protocol & Report | Suite | LMR2 | — | — | **Not Started** | [`GL-TMP-DC-003-verification-protocol-report.md`](docs/project/dhfs/pca-device/design-controls/vnv/GL-TMP-DC-003-verification-protocol-report.md) |
| L2-PC28 | Design Trace Matrix (UN ↔ DI ↔ Arch ↔ V&V) | Suite | LMR2 | — | — | **Not Started** | [`GL-SOP-DC-003-trace-matrix-overview.md`](docs/project/dhfs/pca-device/design-controls/trace-matrix/GL-SOP-DC-003-trace-matrix-overview.md) |
| L2-PC16 | Tool Validation Records | Suite | LMR2 | — | — | **Not Started** | [`GL-TMP-DC-003-tool-validation-record.md`](docs/project/dhfs/pca-device/design-controls/tool-validation/GL-TMP-DC-003-tool-validation-record.md) |
| L2-PC9 | Risk Management Report (ISO 14971) | Suite | LMR2 | — | — | **Not Started** | [`GL-TMP-RM-002-risk-management-report.md`](docs/project/dhfs/pca-device/risk-management/GL-TMP-RM-002-risk-management-report.md) |
| L2-PC23 | Clinical Evaluation Report | Suite | LMR2 | — | — | **Not Started** | [`clinical`](docs/project/dhfs/pca-device/clinical/) |
| L2-PC24 | Periodic Safety Update Report (PSUR) | Suite | LMR2 | — | — | **Not Started** | [`GL-SOP-PM-001-psur.md`](docs/project/dhfs/pca-device/postmarket/GL-SOP-PM-001-psur.md) |
| L2-PC12 | Cybersecurity Vulnerability Management Plan | Suite | LMR2 | — | — | **Not Started** | [`GL-SOP-SW-004-vulnerability-management-plan.md`](docs/project/dhfs/pca-device/cybersecurity/GL-SOP-SW-004-vulnerability-management-plan.md) |

### Adapter (item DHF, SaMD Class I, IEC 62304 Class B)


| # | Deliverable | Scope | Phase | REF | Effort | Status | Path |
|---|---|---|---|---|---|---|---|
| L2-CA1 | architecture | Adapter | LMR2 | — | — | **Not Started** | [`connectivity-adapter-system-sad.md`](docs/project/dhfs/connectivity-adapter/design-controls/architecture/connectivity-adapter-system-sad.md) |
| L2-CA26 | plans | Adapter | LMR2 | — | — | **Not Started** | [`GL-TMP-DC-001-design-and-development-plan.md`](docs/project/dhfs/connectivity-adapter/design-controls/plans/GL-TMP-DC-001-design-and-development-plan.md) |
| L2-CA25 | user-needs | Adapter | LMR2 | — | — | **Not Started** | [`GL-TMP-UC-001-use-specification.md`](docs/project/dhfs/connectivity-adapter/design-controls/user-needs/GL-TMP-UC-001-use-specification.md) |
| L2-CA2 | requirements | Adapter | LMR2 | — | — | **Not Started** | [`GL-TMP-DC-002-design-input-specification.md`](docs/project/dhfs/connectivity-adapter/design-controls/requirements/GL-TMP-DC-002-design-input-specification.md) |
| L2-CA27 | vnv | Adapter | LMR2 | — | — | **Not Started** | [`GL-TMP-DC-003-verification-protocol-report.md`](docs/project/dhfs/connectivity-adapter/design-controls/vnv/GL-TMP-DC-003-verification-protocol-report.md) |
| L2-CA28 | trace-matrix | Adapter | LMR2 | — | — | **Not Started** | [`GL-SOP-DC-003-trace-matrix-overview.md`](docs/project/dhfs/connectivity-adapter/design-controls/trace-matrix/GL-SOP-DC-003-trace-matrix-overview.md) |
| L2-CA16 | tool-validation | Adapter | LMR2 | — | — | **Not Started** | [`GL-TMP-DC-003-tool-validation-record.md`](docs/project/dhfs/connectivity-adapter/design-controls/tool-validation/GL-TMP-DC-003-tool-validation-record.md) |
| L2-CA9 | risk-management | Adapter | LMR2 | — | — | **Not Started** | [`GL-TMP-RM-002-risk-management-report.md`](docs/project/dhfs/connectivity-adapter/risk-management/GL-TMP-RM-002-risk-management-report.md) |
| L2-CA23 | clinical | Adapter | LMR2 | — | — | **Not Started** | [`clinical`](docs/project/dhfs/connectivity-adapter/clinical/) |
| L2-CA24 | postmarket | Adapter | LMR2 | — | — | **Not Started** | [`GL-SOP-PM-001-psur.md`](docs/project/dhfs/connectivity-adapter/postmarket/GL-SOP-PM-001-psur.md) |
| L2-CA12 | cybersecurity | Adapter | LMR2 | — | — | **Not Started** | [`GL-SOP-SW-004-vulnerability-management-plan.md`](docs/project/dhfs/connectivity-adapter/cybersecurity/GL-SOP-SW-004-vulnerability-management-plan.md) |

---

### Cloud (system DHF)


| # | Deliverable | Scope | Phase | REF | Effort | Status | Path |
|---|---|---|---|---|---|---|---|
| L2-CS1 | architecture | Cloud | LMR2 | — | — | **Not Started** | [`architecture`](docs/project/dhfs/cloud-suite/design-controls/architecture/) |
| L2-CS26 | plans | Cloud | LMR2 | — | — | **Not Started** | [`GL-TMP-DC-001-design-and-development-plan.md`](docs/project/dhfs/cloud-suite/design-controls/plans/GL-TMP-DC-001-design-and-development-plan.md) |
| L2-CS25 | user-needs | Cloud | LMR2 | — | — | **Not Started** | [`GL-TMP-UC-001-use-specification.md`](docs/project/dhfs/cloud-suite/design-controls/user-needs/GL-TMP-UC-001-use-specification.md) |
| L2-CS2 | requirements | Cloud | LMR2 | — | — | **Not Started** | [`GL-TMP-DC-002-design-input-specification.md`](docs/project/dhfs/cloud-suite/design-controls/requirements/GL-TMP-DC-002-design-input-specification.md) |
| L2-CS27 | vnv | Cloud | LMR2 | — | — | **Not Started** | [`GL-TMP-DC-003-verification-protocol-report.md`](docs/project/dhfs/cloud-suite/design-controls/vnv/GL-TMP-DC-003-verification-protocol-report.md) |
| L2-CS28 | trace-matrix | Cloud | LMR2 | — | — | **Not Started** | [`GL-SOP-DC-003-trace-matrix-overview.md`](docs/project/dhfs/cloud-suite/design-controls/trace-matrix/GL-SOP-DC-003-trace-matrix-overview.md) |
| L2-CS16 | tool-validation | Cloud | LMR2 | — | — | **Not Started** | [`GL-TMP-DC-003-tool-validation-record.md`](docs/project/dhfs/cloud-suite/design-controls/tool-validation/GL-TMP-DC-003-tool-validation-record.md) |
| L2-CS9 | risk-management | Cloud | LMR2 | — | — | **Not Started** | [`GL-TMP-RM-002-risk-management-report.md`](docs/project/dhfs/cloud-suite/risk-management/GL-TMP-RM-002-risk-management-report.md) |
| L2-CS23 | clinical | Cloud | LMR2 | — | — | **Not Started** | [`clinical`](docs/project/dhfs/cloud-suite/clinical/) |
| L2-CS24 | postmarket | Cloud | LMR2 | — | — | **Not Started** | [`GL-SOP-PM-001-psur.md`](docs/project/dhfs/cloud-suite/postmarket/GL-SOP-PM-001-psur.md) |
| L2-CS12 | cybersecurity | Cloud | LMR2 | — | — | **Not Started** | [`GL-SOP-SW-004-vulnerability-management-plan.md`](docs/project/dhfs/cloud-suite/cybersecurity/GL-SOP-SW-004-vulnerability-management-plan.md) |

---

## Engineering Prerequisites


Cross-cutting engineering capabilities required for filing readiness. Source: [`milestones/engineering.yml`](../milestones/engineering.yml). Each row lists the design-control rows it unblocks.

| # | Prerequisite | Scope | Phase | Effort | Status | Unblocks |
|---|---|---|---|---|---|---|
| ENG1 | Hardware Design Freeze (pump mechanism, sensors, enclosure) | Suite | 510k+PCCP | V.High | **Not Started** | RM2a, RM3a, SW6a, CL2 |
| ENG2 | RTOS + Device Platform Baseline (M7) | Suite | 510k+PCCP | High | **Not Started** | SW3a, SW4a, SW5a, SW6a, SW11, CY2a, CY7a |
| ENG3 | Drug Library Payload Format Finalized | Suite | 510k+PCCP | Med | **Not Started** | SW2a, SW2b, RM2a, RM2b, PS1, PS2, PS3 |
| ENG4 | Crypto / Signing Stack (KMS, cert store, HSM) | Suite | 510k+PCCP | High | **Not Started** | CY2a, CY2b, CY4a, CY4b, PS1, PS4 |
| ENG5 | Cyber Comms Stack (TLS 1.3, mutual auth, cert provisioning) | Suite | 510k+PCCP | High | **Not Started** | CY5, CY7a, CY7c, MS5 |
| ENG6 | Drug Library Authoring Workflow (D1–D3) | Suite | 510k+PCCP | High | **Not Started** | SW2b, HF2b, HF3b, HF4b |
| ENG7 | Drug Library Signing Service (D4) | Suite | 510k+PCCP | Med | **Not Started** | CY2b, PS1, PS2 |
| ENG8 | Audit Log Infrastructure (D6, 21 CFR Part 11) | Suite | 510k+PCCP | Med | **Not Started** | SW2b, SW6b |
| ENG9 | 21 CFR Part 11 Conformance (D2 + D6) | Suite | 510k+PCCP | Med | **Not Started** | SW2b, LB3 |
| ENG10 | Adapter Pass-Through Architecture (A3, A4) | Suite | 510k+PCCP | Med | **Not Started** | MS5, CY7c |
| ENG16 | Drug Library Validation Rule Engine (D3) | Suite | 510k+PCCP | Med | **Not Started** | SW2b, RM2b, PS1 |
| ENG17 | Firmware Update Verifier (M6/M7 secure boot) | Suite | 510k+PCCP | Med | **Not Started** | CY2a, CY7a, PS4, PS5 |
| ENG18 | Time Sync / Trusted Time Source (M7) | Suite | 510k+PCCP | Low | **Not Started** | RM2a, CY7a |
| ENG13 | HIL Test Rig + System V&V Harness | Suite | 510k+PCCP | V.High | **Not Started** | SW6a, SW6b, CY7a |
| ENG15 | SBOM Generation Pipeline | Suite | 510k+PCCP | Low | **Not Started** | CY4a, CY4b, CY4c, MS7 |
| ENG11 | Occlusion / Air-in-Line Sensor Calibration | Suite | 510k+PCCP | High | **Not Started** | RM2a, CL2, SW6a |
| ENG12 | Alarm System IEC 60601-1-8 Conformance | Suite | 510k+PCCP | High | **Not Started** | RM2a, HF3a, SW6a |
| ENG14 | Usability Test Cohort Recruitment | Suite | 510k+PCCP | Med | **Not Started** | HF4a, HF4b |
| ENG19 | AI/ML Training Infrastructure (predictive alarms) | Suite | LMR2 | V.High | **Not Started** | AI1, AI2, AI3, AI4 |
| ENG20 | AI/ML Drift Monitoring Pipeline | Suite | LMR2 | High | **Not Started** | AI5, AI6 |

---

## Deliverable Details


_Per-ID detail entries surface as inline click-row expansion in the dashboard. Populated by `/tracker enrich-details` (Stage 6) into `submission-tracker.details.json` — the sidecar overrides any inline content here when present. Until that action runs, this section is empty._

## Cross-Milestone Summary


_Rollup table — populated as rows land. See per-row Status above; run `/tracker status` for live counts._

| Milestone | Deliverable rows | Done | In Progress | Drafted | Not Started |
|---|---|---|---|---|---|
| QSub | 38 | 0 | 0 | 0 | 38 |
| 510k+PCCP | 44 | 0 | 0 | 0 | 44 |
| LMR1 | 33 | 0 | 0 | 0 | 33 |
| LMR2 | 39 | 0 | 0 | 0 | 39 |
| **Engineering Prereqs** | 20 | 0 | 0 | 0 | 20 |
| **Totals** | **174** | **0** | **0** | **0** | **174** |

## Notable Findings


_Surfaced during build / review. None yet._

## Status Scale


| Status | Definition |
|---|---|
| **Approved** | Substantially complete; reviewed and signed off |
| **In Review** | Reviewed; revisions in flight |
| **Drafted** | Initial draft exists, pending review |
| **Drafting** | Author is in the B6 Create Draft authoring workflow |
| **Needs Revision** | Reviewed; revisions required |
| **Not Started** | No work product exists |
| **N/A** | Binding not applicable to this scope |

## Effort Scale


| Effort | Definition |
|---|---|
| **Low** | < 1 engineer-week |
| **Med** | 1–3 engineer-weeks |
| **High** | 3–8 engineer-weeks |
| **V.High** | > 8 engineer-weeks |

## Phase Scale


| Phase | Definition |
|---|---|
| **QSub** | Pre-submission meeting (`qsub-release` milestone) — validate PCCP scope, predicate, module classification |
| **510k+PCCP** | Filing event (`pccp-release` milestone) — K210345 demo |
| **LMR1** | First commercial release (`lmr1-release` milestone) |
| **LMR2** | Second commercial release (`lmr2-release` milestone) — AI/ML envelope |

## Reviewer Sign-off


_Roles required per QMS separation-of-duties (ISO 13485 §7.3). Author/contributor tracking lives in the Changelog table below, NOT here._

| Role | Reviewer | Date | Status |
|---|---|---|---|
| R&D Lead | — | — | Pending |
| Regulatory Affairs Lead | — | — | Pending |
| Quality Assurance Lead | — | — | Pending |

## Changelog


| Date | Author | Summary |
|---|---|---|
| 2026-05-12 | Claude (ben/047 Stage 1+2) | Scaffolded chrome per `/tracker init` spec — Context & Sources (6 source listings), Status/Scope/Phase/REF Priority Legends + end-of-file Scale tables, Cross-Milestone Summary with rollups, Notable Findings + Deliverable Details placeholders, Reviewer Sign-off. Authored `docs/project/milestones/engineering.yml` with all 20 ENG rows (ENG1–ENG20) from the archived legacy backup, split across two engineering milestones (`engineering-pccp-release` for ENG1–18, `engineering-lmr2-release` for ENG19–20). Fixed regulatory.yml: `510(k)+PCCP Release` → `510k+PCCP Release` to match sister-project phase naming. Added `tracker.display.phase_label_overrides` to project.yml so ENG rows render readable phases instead of milestone IDs (workaround for upstream generate.py:248 bug where ENG rows pass milestone_id as both args to `_phase_for_milestone()`). |
| 2026-05-11 | Claude (ben/044 reset) | Regenerated from upstream v11 generator after dropping v17 local fork. 44 generator-derived rows; chrome lost in subsequent `--write-canonical` run (the v11-documented destructive path); recovered via Stage 1 of ben/047. |
| 2026-04-14 | Claude — `/tracker build` (v2) | Restructured with `### N.N` category headings and renamed P→PC/PS/AI prefixes so the render script classifies rows correctly. 18 engineering prerequisites split across 4.1/4.2/4.3/4.4/4.5. Task ben/013. |
| 2026-04-14 | Claude — `/tracker build` (v1) | First-stab population of Parts 1–4 from 10 FDA guidance docs + 3 SADs + composition manifest + regulatory strategy. Task ben/013. |
| 2026-04-14 | Claude — `/tracker init` | Initial scaffold. Context & Sources populated. Task ben/013. |
