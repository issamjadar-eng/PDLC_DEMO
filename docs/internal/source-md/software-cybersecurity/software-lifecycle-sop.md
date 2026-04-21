---
source_file: "N/A — authored-in-markdown"
source_path: "software-cybersecurity/software-lifecycle-sop.md"
doc_id: "GL-SOP-SW-001"
doc_type: "SOP"
title: "Medical Device Software Lifecycle"
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
  - doc_id: "IEC 62304:2006+A1:2015"
    title: "Medical device software — Software life cycle processes"
    resolved: true
    match: null
    note: "Primary anchor"
  - doc_id: "IEC 82304-1:2016"
    title: "Health software — Part 1: General requirements for product safety"
    resolved: true
    match: null
    note: "Applicable for standalone health software"
  - doc_id: "FDA — General Principles of Software Validation (2002)"
    title: null
    resolved: true
    match: null
    note: null
  - doc_id: "FDA — Content of Premarket Submissions for Device Software Functions (2023)"
    title: null
    resolved: true
    match: null
    note: null
conversion_history:
  - date: "2026-04-21"
    source: "v1 — initial draft under task ben/022"
notes: null
---

# GL-SOP-SW-001 — Medical Device Software Lifecycle

_Demo sample data — not for clinical use._

**Document ID:** GL-SOP-SW-001
**Revision:** 1.0
**Effective Date:** 2026-04-21
**Owner:** VP Engineering, GlobalLogic MedTech

---

## 1. Purpose

Establish the lifecycle processes for medical device software — **SaMD** and **SiMD** — per **IEC 62304:2006+A1:2015** and, where applicable, **IEC 82304-1:2016**.

## 2. Scope

All software that is a medical device or part of a medical device developed under the GlobalLogic QMS.

## 3. Responsibilities

| Role | Responsibility |
|---|---|
| Software Lead | Own Software Development Plan, architecture, and lifecycle outputs |
| Software Developers | Implement per plan; unit-test; participate in reviews |
| Software Verification Lead | Integration + system testing; regression; trace |
| SOUP Owner | Maintain SOUP inventory; monitor anomaly lists (GL-SOP-SW-002) |
| Cybersecurity Lead | Integrate cyber controls per GL-SOP-SW-004 |
| Configuration Manager | Version control, baselines, build reproducibility |

## 4. Definitions

- **Software system** — Integrated collection of software items.
- **Software item** — Any identifiable part of a software system.
- **Software unit** — Not further decomposed for testing purposes (at developer discretion, documented).
- **SOUP** — Software Of Unknown Provenance (IEC 62304 §3.30).
- **Software safety class** — A/B/C per IEC 62304 §4.3.

## 5. References

- IEC 62304:2006+A1:2015
- IEC 82304-1:2016
- ISO 14971:2019 — Risk management (GL-SOP-RM-001)
- IEC 81001-5-1:2021 — Cybersecurity (GL-SOP-SW-004)
- FDA Guidance — "Content of Premarket Submissions for Device Software Functions" (2023)
- FDA Guidance — "General Principles of Software Validation" (2002)

## 6. Procedure

### 6.1 Software Safety Classification (IEC 62304 §4.3)

Each software system (and each identifiable software item where the architecture allows) is assigned a class:

- **Class A** — No injury or damage to health is possible
- **Class B** — Non-serious injury is possible
- **Class C** — Death or serious injury is possible

Classification is determined per **GL-WI-SW-001 — Software Safety Classification** and documented in the Software Development Plan. Risk controls **external** to the software (per GL-SOP-RM-001) may lower the class if they prevent hazardous situations reliably — the rationale is documented.

### 6.2 Software Development Planning (§5.1)

A **Software Development Plan (GL-TMP-SW-001)** is drafted at project start. Contents include:

- Scope, safety class, and lifecycle model (e.g., iterative, agile-as-documented)
- Development standards, methods, and tools
- Verification planning
- Risk management integration (IEC 62304 §7 / ISO 14971)
- Configuration management (§8)
- Problem resolution (§9)

### 6.3 Software Requirements Analysis (§5.2)

- Derived from system Design Inputs (GL-SOP-DC-003)
- Safety-related requirements explicitly identified
- Verifiable, unambiguous, traceable to system inputs
- Reviewed and approved

### 6.4 Software Architectural Design (§5.3)

- System decomposed into software items; interfaces specified
- SOUP identified at this phase (GL-SOP-SW-002)
- Class B/C: architecture supports segregation of hazard-contributing items where feasible

### 6.5 Software Detailed Design (§5.4)

- Class C: detailed design of software units
- Class B: at discretion, but essential for safety-related items
- Interfaces and data flows specified

### 6.6 Software Unit Implementation and Verification (§5.5)

- Acceptance criteria for unit testing (per-item, per-class)
- Class B/C: unit verification evidence retained

### 6.7 Software Integration and Integration Testing (§5.6)

- Integration strategy defined in the plan
- Class B/C: integration tests exercised and results retained
- Regression strategy on change

### 6.8 Software System Testing (§5.7)

- System-level tests vs. software requirements
- Results retained; failures dispositioned to NCR / CAPA as needed

### 6.9 Software Release (§5.8)

Before release:

- All verification activities complete
- All known anomalies evaluated against the risk management file (GL-SOP-RM-001)
- SOUP components evaluated for residual anomalies (GL-SOP-SW-002)
- Software build is reproducible from controlled configuration

### 6.10 Software Maintenance (§6)

Maintenance plan addresses:

- Change classification per IEC 62304 §6.2 / GL-SOP-DC-008
- Problem reports (GL-SOP-SW-003)
- Bug fix vs. new feature segregation where practical

### 6.11 Software Risk Management (§7)

Integrated with GL-SOP-RM-001:

- Software contributions to hazardous situations captured in Hazard Analysis (GL-WI-RM-001)
- Software risk control measures verified (including that implementation does not introduce new risks)

### 6.12 Software Configuration Management (§8)

- Version control (git or equivalent) with tagged baselines
- Build artifacts reproducible from source + dependencies
- SBOM generated and maintained (GL-WI-SW-002)
- Configuration item records per item (software + SOUP)

### 6.13 Software Problem Resolution (§9)

See **GL-SOP-SW-003 — Software Problem Resolution** for the problem report lifecycle.

## 7. Records Generated

| Record | Retained by | Retention |
|---|---|---|
| Software Development Plan (GL-TMP-SW-001) | DHF | Per GL-SOP-QM-001 |
| Software Requirements, Architecture, Design docs | DHF | Per GL-SOP-QM-001 |
| Unit / Integration / System test records | DHF | Per GL-SOP-QM-001 |
| SOUP inventory | DHF | Per GL-SOP-QM-001 |
| SBOM | DHF | Per GL-SOP-QM-001 |
| Problem reports (per GL-SOP-SW-003) | DHF | Per GL-SOP-QM-001 |
| Release record | DHF | Per GL-SOP-QM-001 |

## 8. Revision History

| Rev | Date | Author | Summary |
|---|---|---|---|
| 1.0 | 2026-04-21 | Ben Xavier (via Claude, task ben/022) | Initial demo SOP. |
