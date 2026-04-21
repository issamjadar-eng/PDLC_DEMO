---
source_file: "N/A — authored-in-markdown"
source_path: "quality-management/quality-manual.md"
doc_id: "GL-MAN-QM-001"
doc_type: "MAN"
title: "GlobalLogic Medical Device Quality Manual"
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
  - doc_id: "ISO 13485:2016"
    title: "Medical devices — Quality management systems — Requirements for regulatory purposes"
    resolved: true
    match: null
    note: "Primary QMS anchor"
  - doc_id: "21 CFR Part 820"
    title: "FDA Quality System Regulation"
    resolved: true
    match: null
    note: "US regulatory anchor"
  - doc_id: "EU MDR 2017/745"
    title: "Regulation on medical devices"
    resolved: true
    match: null
    note: "EU regulatory anchor"
conversion_history:
  - date: "2026-04-21"
    source: "v1 — initial draft under task ben/022"
notes: "Demo manual for PDLC_DEMO; parent company GlobalLogic; anchors to ISO 13485:2016 clauses. Not controlled; not for real submission."
---

# GL-MAN-QM-001 — GlobalLogic Medical Device Quality Manual

_Demo sample data — not for clinical use._

**Document ID:** GL-MAN-QM-001
**Revision:** 1.0
**Effective Date:** 2026-04-21
**Owner:** GlobalLogic MedTech Quality Function
**Approved By:** VP Quality, GlobalLogic MedTech

---

## 1. Purpose

This Quality Manual defines the Quality Management System (QMS) operated by **GlobalLogic** for the development, production, installation, and servicing of medical devices and medical device software. It establishes the policies, processes, scope, and documentation hierarchy required to meet applicable regulatory requirements worldwide.

## 2. Scope

The GlobalLogic QMS covers the full lifecycle of medical devices and medical device software, including:

- Product planning and design controls
- Risk management
- Software lifecycle (including SaMD and SiMD)
- Usability engineering
- Clinical evaluation
- Manufacturing and supplier controls
- Installation and servicing
- Post-market surveillance, complaint handling, and adverse event reporting

**Scope exclusions** permitted by ISO 13485:2016 §1.2 are documented in §10 of this manual with justification.

## 3. Regulatory Framework

| Standard / Regulation | Jurisdiction / Domain | Applicability |
|---|---|---|
| ISO 13485:2016 | International | Primary QMS standard |
| 21 CFR Part 820 | United States (FDA) | Quality System Regulation |
| 21 CFR Part 11 | United States (FDA) | Electronic records and signatures |
| EU MDR 2017/745 | European Union | Medical Device Regulation |
| ISO 14971:2019 | International | Risk management |
| IEC 62304:2006+A1:2015 | International | Medical device software lifecycle |
| IEC 62366-1:2015 | International | Usability engineering |
| IEC 81001-5-1:2021 | International | Health software — cybersecurity |
| ISO 14155:2020 | International | Clinical investigation |
| 21 CFR Part 803 | United States | Medical Device Reporting (MDR) |

## 4. Terms, Definitions, and Abbreviations

| Term | Definition |
|---|---|
| CAPA | Corrective Action / Preventive Action |
| DHF | Design History File |
| DMR | Device Master Record |
| DHR | Device History Record |
| MDR | Medical Device Reporting (21 CFR 803) or Medical Device Regulation (EU 2017/745) — context-dependent |
| NCR | Nonconformance Report |
| PMS | Post-Market Surveillance |
| QMS | Quality Management System |
| SOP | Standard Operating Procedure |
| SOUP | Software of Unknown Provenance (IEC 62304 §3.30) |
| WI | Work Instruction |

Full glossary: `docs/internal/glossary.md`.

## 5. Quality Management System (ISO 13485 §4)

### 5.1 General Requirements (§4.1)

GlobalLogic has documented, implemented, and maintains a QMS that:

1. Determines processes needed for the QMS and their application throughout the organization
2. Applies a risk-based approach to control of QMS processes
3. Determines sequence and interaction of these processes
4. Determines criteria and methods to ensure effective operation and control
5. Ensures availability of resources and information
6. Monitors, measures (where applicable), and analyzes these processes
7. Implements actions necessary to achieve planned results and maintain effectiveness

### 5.2 Documentation Requirements (§4.2)

The QMS documentation hierarchy is:

```
Level 1  —  Quality Manual (this document)                       GL-MAN-QM-001
Level 2  —  Policies                                             GL-POL-*
Level 3  —  Standard Operating Procedures (SOPs)                 GL-SOP-*
Level 4  —  Work Instructions (WIs)                              GL-WI-*
Level 5  —  Forms, Templates, and Records                        GL-FORM-* / GL-TMP-*
```

Document and record control is defined in **GL-SOP-QM-001 — Document and Records Control**.

## 6. Management Responsibility (ISO 13485 §5)

### 6.1 Quality Policy

> GlobalLogic is committed to developing and delivering safe, effective, and regulatorily compliant medical devices and medical device software. We operate a risk-based Quality Management System that meets or exceeds ISO 13485:2016, 21 CFR Part 820, and EU MDR requirements; we foster a culture of quality, continuous improvement, and transparency with regulators, customers, and patients.

### 6.2 Quality Objectives

Objectives are established annually by the Management Representative, measurable, and reviewed during Management Review (**GL-SOP-QM-002**). Typical objective categories:

- Product safety — e.g., post-market complaint rate
- Process effectiveness — e.g., design verification first-pass yield
- Regulatory compliance — e.g., audit findings closed on-time
- Supplier quality — e.g., incoming inspection nonconformance rate
- Customer satisfaction — e.g., field issue MTTR

### 6.3 Responsibility and Authority

| Role | Responsibility |
|---|---|
| Top Management | Provide resources, set policy, conduct Management Review |
| Management Representative (VP Quality) | QMS effectiveness; regulatory interface; report to Top Management |
| Design Owner (per product) | DHF integrity; design controls execution |
| Quality Engineering | CAPA, audit, nonconformance, verification support |
| Regulatory Affairs | Submissions, registrations, post-market reporting |
| Clinical Affairs | Clinical evaluation, PMCF, clinical literature |
| Software / Engineering | IEC 62304 lifecycle execution |
| Manufacturing / Operations | DMR execution, DHR creation, production controls |
| Supplier Quality | Supplier qualification, monitoring, SCAR |
| Post-Market Surveillance Lead | PMS plan, trending, signal detection |

## 7. Resource Management (ISO 13485 §6)

- **GL-SOP-QM-003 — Training** — competence, training, awareness
- Infrastructure (facilities, workspace, equipment) controlled via the applicable Production SOP (Phase 6)
- Work environment and contamination control per applicable Production WIs

## 8. Product Realization (ISO 13485 §7)

| Process | Governing SOP | ISO 13485 § |
|---|---|---|
| Planning | GL-SOP-DC-002 Design Planning | §7.1, §7.3.2 |
| Customer-related processes | GL-SOP-DC-003 Design Inputs | §7.2, §7.3.3 |
| Design & development | GL-SOP-DC-001 Design Control | §7.3 |
| Purchasing | GL-SOP-SP-002 Purchasing Controls | §7.4 |
| Production & service provision | GL-SOP-SP-003 Production & Process Controls | §7.5 |
| Control of monitoring & measuring equipment | GL-SOP-SP-003 | §7.6 |

## 9. Measurement, Analysis, and Improvement (ISO 13485 §8)

| Process | Governing SOP | ISO 13485 § |
|---|---|---|
| Feedback / PMS | GL-SOP-PM-001 Post-Market Surveillance | §8.2.1 |
| Complaint handling | GL-SOP-PM-002 Complaint Handling | §8.2.2 |
| Regulatory reporting | GL-SOP-PM-003 Adverse Event / MDR Reporting | §8.2.3 |
| Internal audit | GL-SOP-QM-004 Internal Audit | §8.2.4 |
| Monitoring & measurement of processes & product | Product-specific V&V plans | §8.2.5, §8.2.6 |
| Control of nonconforming product | GL-SOP-SP-004 Nonconformance Control | §8.3 |
| Analysis of data | GL-SOP-QM-002 Management Review, §8.4 input | §8.4 |
| Improvement / CAPA | GL-SOP-QM-005 CAPA | §8.5 |

## 10. Permitted Scope Exclusions

Exclusions are evaluated annually and documented in an Exclusion Rationale record (GL-FORM-QM-010 — _to be issued in a future revision_). No exclusions apply at the effective date of this Manual revision.

## 11. Revision History

| Rev | Date | Author | Summary |
|---|---|---|---|
| 1.0 | 2026-04-21 | Ben Xavier (via Claude, task ben/022) | Initial demo Quality Manual for PDLC_DEMO. |
