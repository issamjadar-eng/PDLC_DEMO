---
source_file: "N/A — authored-in-markdown"
source_path: "software-cybersecurity/cybersecurity-sop.md"
doc_id: "GL-SOP-SW-004"
doc_type: "SOP"
title: "Medical Device Cybersecurity"
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
  - doc_id: "IEC 81001-5-1:2021"
    title: "Health software and health IT systems safety, effectiveness and security — Part 5-1: Security — Activities in the product life cycle"
    resolved: true
    match: null
    note: "Primary anchor"
  - doc_id: "FDA — Cybersecurity in Medical Devices: QSR and Content of Premarket Submissions (2023)"
    title: null
    resolved: true
    match: null
    note: null
  - doc_id: "AAMI TIR57:2016"
    title: "Principles for medical device security — Risk management"
    resolved: true
    match: null
    note: "Guidance"
  - doc_id: "NIST SP 800-53 Rev 5"
    title: null
    resolved: true
    match: null
    note: "Control catalog reference"
conversion_history:
  - date: "2026-04-21"
    source: "v1 — initial draft under task ben/022"
notes: null
---

# GL-SOP-SW-004 — Medical Device Cybersecurity

_Demo sample data — not for clinical use._

**Document ID:** GL-SOP-SW-004
**Revision:** 1.0
**Effective Date:** 2026-04-21
**Owner:** Cybersecurity Lead, GlobalLogic MedTech

---

## 1. Purpose

Establish cybersecurity activities across the medical device product lifecycle — per **IEC 81001-5-1:2021**, the **FDA 2023 Cybersecurity Premarket Guidance**, and informed by **AAMI TIR57:2016**.

## 2. Scope

All medical device products with software or connectivity — SaMD, SiMD, connected devices, cloud components, companion apps, service/maintenance interfaces, and their supply chain.

## 3. Responsibilities

| Role | Responsibility |
|---|---|
| Cybersecurity Lead | Own Cybersecurity Plan; threat model; coordinate response |
| Software Lead | Integrate security requirements into software lifecycle (GL-SOP-SW-001) |
| Risk Manager | Integrate security risks with safety risk management (GL-SOP-RM-001) |
| Privacy / Regulatory | HIPAA / GDPR / applicable privacy counsel |
| PMS Lead | Cyber-signal monitoring post-market (GL-SOP-PM-001) |

## 4. Definitions

- **Threat** — A potential cause of an unwanted incident that may result in harm to patients, users, or assets.
- **Vulnerability** — A weakness that can be exploited by one or more threats.
- **SBOM** — Software Bill of Materials (GL-WI-SW-002).
- **Security risk** — Combination of probability of a successful threat exploitation and impact on safety / effectiveness / data.

## 5. References

- IEC 81001-5-1:2021
- FDA — Cybersecurity in Medical Devices (2023)
- AAMI TIR57:2016
- NIST SP 800-53 Rev 5 — control catalog
- NIST SP 800-30 — Risk Assessment guidance
- IEC 62304 — Software lifecycle (GL-SOP-SW-001)
- ISO 14971 — Risk management integration (GL-SOP-RM-001)

## 6. Procedure

### 6.1 Cybersecurity Planning (IEC 81001-5-1 §5)

A **Cybersecurity Plan (GL-TMP-SW-002)** is drafted alongside the Software Development Plan. Contents include:

- Security scope and boundaries
- Stakeholders and responsibilities
- Security-related activities per lifecycle phase
- Threat-model scope
- Security controls baseline
- Vulnerability disclosure and response process
- Ongoing post-market monitoring (CVE, CISA KEV, vendor advisories)

### 6.2 Secure Requirements (IEC 81001-5-1 §6)

Security requirements derived from:
- Threat model
- Regulatory requirements (HIPAA, GDPR, MDR GSPR §17, FDA 2023 Guidance attributes)
- Applicable standards (NIST SP 800-53 baseline selections, IEC 62443 for OT interfaces)

Requirements flow into Design Inputs (GL-SOP-DC-003) tagged as security-related.

### 6.3 Secure Architecture (§7)

- Trust boundaries identified
- Identity, authentication, authorization, session management
- Data protection at rest and in transit
- Secure update / patch mechanism
- Logging and monitoring
- Fail-secure behavior

### 6.4 Threat Modeling

Performed iteratively — at architecture, at each major increment, at release, and on material change. Methodology: STRIDE (or equivalent — documented in the Plan). Outputs are inputs to Hazard Analysis (GL-WI-RM-001) — cyber hazards merge into safety-risk tracking where they can lead to patient harm.

### 6.5 Secure Implementation and Verification (§8, §9)

- Secure-coding standard adopted and enforced (e.g., CERT C/C++, OWASP ASVS where applicable)
- Static analysis, dependency scanning, secret scanning in CI
- Security verification: abuse-case tests, penetration testing (scope per risk), fuzzing for high-risk interfaces
- Pen-test reports retained as Design Verification (GL-SOP-DC-006) evidence

### 6.6 SBOM

A **Software Bill of Materials** is produced per GL-WI-SW-002 and updated at each release. Format per FDA 2023 guidance: SPDX or CycloneDX acceptable. SBOM is also provided in premarket submissions.

### 6.7 Vulnerability Management

- Continuous CVE / vendor-advisory monitoring against the SBOM
- Triage: exploitability, reachability, impact on safety / effectiveness
- Remediation timeline aligned to risk (e.g., Critical ≤ 30 days, High ≤ 90 days — product-specific per Plan)
- Regulatory and customer communication per GL-SOP-PM-002, GL-SOP-PM-003, FDA 2023 guidance timelines

### 6.8 Coordinated Vulnerability Disclosure (CVD)

GlobalLogic maintains a coordinated disclosure channel (security.txt; security@globallogic.example). Reports triaged with the same SLAs as internal findings. External researchers acknowledged per the disclosure policy.

### 6.9 Incident Response

Documented playbooks for suspected in-field compromise: containment, investigation, customer notification, regulator notification, post-incident review. Integrated with CAPA (GL-SOP-QM-005) and MDR reporting (GL-SOP-PM-003).

## 7. Records Generated

| Record | Retained by | Retention |
|---|---|---|
| Cybersecurity Plan (GL-TMP-SW-002) | DHF | Per GL-SOP-QM-001 |
| Threat Model | DHF | Per GL-SOP-QM-001 |
| SBOM (per release) | DHF | Per GL-SOP-QM-001 |
| Vulnerability Management records | DHF | Per GL-SOP-QM-001 |
| Pen-test / security test reports | DHF | Per GL-SOP-QM-001 |
| Incident reports | DHF | Per GL-SOP-QM-001 |

## 8. Revision History

| Rev | Date | Author | Summary |
|---|---|---|---|
| 1.0 | 2026-04-21 | Ben Xavier (via Claude, task ben/022) | Initial demo SOP. |
