---
source_file: "N/A — authored-in-markdown"
source_path: "software-cybersecurity/templates/cybersecurity-plan.md"
doc_id: "GL-TMP-SW-002"
doc_type: "TMP"
title: "Cybersecurity Plan"
format: "md"
conversion_date: "2026-04-21"
conversion_method: "claude-authored"
conversion_fidelity: "faithful"
pages: null
sheets: null
has_images: false
image_count: 0
has_tables: true
has_form_fields: true
references:
  - doc_id: "GL-SOP-SW-004"
    title: null
    resolved: true
    match: null
    note: "Parent SOP"
  - doc_id: "IEC 81001-5-1 §5"
    title: null
    resolved: true
    match: null
    note: null
conversion_history:
  - date: "2026-04-21"
    source: "v1 — initial draft under task ben/022"
notes: null
---

# GL-TMP-SW-002 — Cybersecurity Plan

_Demo sample data — not for clinical use._

**Template ID:** GL-TMP-SW-002
**Revision:** 1.0
**Parent SOP:** GL-SOP-SW-004

---

## 1. Identification

| Field | Value |
|---|---|
| Product | `{{NAME}}` |
| Plan Revision | `{{X.X}}` |
| Connectivity profile | ☐ Standalone ☐ Local network ☐ Cloud-connected ☐ BLE / wireless |

## 2. Scope

- Device boundaries and trust zones
- External interfaces (APIs, companion apps, services)
- Privileged workflows (admin / service)

## 3. Security Risk Criteria

- Inputs from Risk Management Plan (GL-TMP-RM-001)
- Cyber-specific severity / probability scales if distinct from safety scales
- Integration rule: **if a cyber risk can lead to patient harm, it is tracked as a safety hazard** (per GL-SOP-RM-001)

## 4. Threat Model

- Methodology: ☐ STRIDE ☐ LINDDUN ☐ MITRE ATT&CK-informed ☐ other: `{{}}`
- Scope and dataflow diagrams
- Trust boundaries
- Threats identified per interface / asset
- Mitigations / residuals

Update cadence: architecture complete → design-complete → pre-Release → on material change.

## 5. Security Requirements

Baseline controls (select and tailor):

- Identity, authentication, authorization (MFA where applicable)
- Session management
- Access control / RBAC
- Data at rest / in transit protection (cryptography — approved algorithms and key management)
- Secure update mechanism (signed updates, rollback protection)
- Logging and monitoring
- Resilience (DoS resistance, graceful degradation)
- Physical security considerations (if applicable)

Map each control to Design Inputs (GL-SOP-DC-003) tagged as security-related.

## 6. Secure Development Practices

- Secure-coding standard
- Dependency scanning / pinning
- Secret scanning / CI integration
- Code review (peer + security-specific)

## 7. Verification

- Abuse-case tests
- Penetration testing — scope, frequency, vendor
- Fuzz testing (high-risk interfaces)
- Runtime monitoring in pre-release environments

## 8. SBOM

Per GL-WI-SW-002. Format: ☐ CycloneDX 1.5 ☐ SPDX 2.3

## 9. Vulnerability Management

- Monitoring sources: CVE, CISA KEV, vendor advisories, coordinated disclosure reports
- SLA: Critical `{{days}}`, High `{{}}`, Medium `{{}}`
- Triage and remediation workflow
- Regulatory / customer communication triggers

## 10. Coordinated Vulnerability Disclosure

- Contact: `{{security@...}}`
- security.txt / policy URL
- Researcher acknowledgement

## 11. Incident Response

- Playbooks
- Roles and escalation
- External communications
- Regulatory reporting integration (GL-SOP-PM-003)

## 12. Approvals

| Role | Name | Date | Signature |
|---|---|---|---|
| Cybersecurity Lead | | | |
| Software Lead | | | |
| Risk Manager | | | |
| VP Quality | | | |
| VP Regulatory | | | |

## 13. Revision History

| Rev | Date | Author | Summary |
|---|---|---|---|
| 1.0 | 2026-04-21 | Ben Xavier (via Claude, task ben/022) | Initial template. |
