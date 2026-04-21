---
source_file: "N/A — authored-in-markdown"
source_path: "software-cybersecurity/soup-management-sop.md"
doc_id: "GL-SOP-SW-002"
doc_type: "SOP"
title: "SOUP / Off-the-Shelf Software Management"
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
  - doc_id: "IEC 62304 §5.3.3, §5.3.4, §8"
    title: null
    resolved: true
    match: null
    note: null
  - doc_id: "FDA — Off-The-Shelf Software Use in Medical Devices (2019)"
    title: null
    resolved: true
    match: null
    note: null
conversion_history:
  - date: "2026-04-21"
    source: "v1 — initial draft under task ben/022"
notes: null
---

# GL-SOP-SW-002 — SOUP / Off-the-Shelf Software Management

_Demo sample data — not for clinical use._

**Document ID:** GL-SOP-SW-002
**Revision:** 1.0
**Parent SOP:** GL-SOP-SW-001

---

## 1. Purpose

Control the incorporation and ongoing management of **Software Of Unknown Provenance (SOUP)** and **Off-the-Shelf (OTS)** software in GlobalLogic medical device software, per IEC 62304 and FDA 2019 OTS guidance.

## 2. Scope

All third-party software included in a medical device software build — open-source libraries, commercial libraries, OSes, runtime platforms, compilers, build tools whose failure could affect device safety.

## 3. Responsibilities

- **SOUP Owner** — per software product
- **Configuration Manager** — SBOM and version pinning
- **Cybersecurity Lead** — CVE monitoring (also per GL-SOP-SW-004)
- **Software Lead** — integration and verification of SOUP components

## 4. Procedure

### 4.1 Pre-Adoption Assessment

Before adopting a SOUP component, document in the SOUP inventory:

- Name, supplier/project, version, license, source URL
- Functional specification of how SOUP is used
- Functional and performance requirements to be met by the SOUP (IEC 62304 §5.3.3)
- System hardware and software required by the SOUP (§5.3.4)
- Known anomaly / issue list review outcome
- Security posture and CVE history
- Alternatives considered; rationale for selection

### 4.2 Integration and Verification

- Pin version in the build (lockfile, submodule, checksum)
- Verify the SOUP's functional and performance requirements are met in integration tests
- Verify that any required system resources are present

### 4.3 Ongoing Monitoring

- **Periodic review** (at minimum quarterly, or at release candidate) of the project's anomaly / issue list for new anomalies that affect risk
- **CVE monitoring** for security vulnerabilities (GL-SOP-SW-004)
- **Update decisions** via GL-SOP-DC-008 change control, including risk-management re-assessment

### 4.4 SOUP Inventory

Maintained as part of the SBOM (GL-WI-SW-002). Each entry carries the SOUP pre-adoption assessment record and a current-status note.

### 4.5 Retirement

A SOUP component is retired from a product via change control (GL-SOP-DC-008), with migration plan to a replacement or removal.

## 5. Records Generated

| Record | Retained by | Retention |
|---|---|---|
| SOUP inventory (per product) | DHF | Per GL-SOP-QM-001 |
| SOUP pre-adoption assessments | DHF | Per GL-SOP-QM-001 |
| Periodic review records | DHF | Per GL-SOP-QM-001 |

## 6. Revision History

| Rev | Date | Author | Summary |
|---|---|---|---|
| 1.0 | 2026-04-21 | Ben Xavier (via Claude, task ben/022) | Initial demo SOP. |
