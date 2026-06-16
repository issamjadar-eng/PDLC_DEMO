# NIST Cybersecurity Framework (CSF)

🔎 **Finding aid — NOT the authoritative source.** Paraphrased distillation of an external standard/framework; no faithful full-text copy exists in this repository (copyrighted). The original document named in the header above is the sole authority — if a clause-level question isn't answered here, state that the original must be consulted; do not infer clause content. `[VERIFY]` marks are unconfirmed against the source.

**Framework**: NIST Cybersecurity Framework 2.0 (February 2024)
**Source**: National Institute of Standards and Technology
**Referenced In**: FDA Cybersecurity guidance

## Overview

The NIST CSF provides a structured approach for organizations to manage cybersecurity risk. Version 2.0 expanded the framework to all organizations (not just critical infrastructure) and added a Govern function. FDA's cybersecurity guidance references the CSF as a recommended framework for medical device security risk management.

## Core Functions

The CSF is organized around 6 core functions, each containing categories and subcategories.

### GOVERN (GV) — New in CSF 2.0

Establish and monitor the organization's cybersecurity risk management strategy, expectations, and policy.

| Category | ID | Key Requirements |
|----------|-----|-----------------|
| Organizational Context | GV.OC | Understand the organizational mission and stakeholder expectations regarding cybersecurity |
| Risk Management Strategy | GV.RM | Establish risk management strategy including risk appetite and tolerance |
| Roles, Responsibilities, Authorities | GV.RR | Establish and communicate cybersecurity roles and responsibilities |
| Policy | GV.PO | Establish and enforce cybersecurity policy |
| Oversight | GV.OV | Ensure appropriate oversight of cybersecurity activities |
| Cybersecurity Supply Chain Risk Management | GV.SC | Manage cybersecurity risk in the supply chain |

### IDENTIFY (ID)

Understand the organization's cybersecurity risk to systems, assets, data, and capabilities.

| Category | ID | Key Requirements |
|----------|-----|-----------------|
| Asset Management | ID.AM | Identify and manage assets (hardware, software, data, systems) |
| Risk Assessment | ID.RA | Understand cybersecurity risk to operations, assets, and individuals |
| Improvement | ID.IM | Identify improvements to organizational cybersecurity risk management |

### PROTECT (PR)

Implement safeguards to ensure delivery of services and limit the impact of potential cybersecurity events.

| Category | ID | Key Requirements |
|----------|-----|-----------------|
| Identity Management, Authentication, and Access Control | PR.AA | Manage identities, credentials, and access |
| Awareness and Training | PR.AT | Ensure personnel are trained on cybersecurity |
| Data Security | PR.DS | Protect data confidentiality, integrity, and availability |
| Platform Security | PR.PS | Protect hardware, software, and services |
| Technology Infrastructure Resilience | PR.IR | Manage security of network and technology infrastructure |

### DETECT (DE)

Develop and implement activities to identify cybersecurity events.

| Category | ID | Key Requirements |
|----------|-----|-----------------|
| Continuous Monitoring | DE.CM | Monitor assets to detect anomalies, indicators of compromise, and other adverse events |
| Adverse Event Analysis | DE.AE | Analyze detected events to characterize and understand them |

### RESPOND (RS)

Take action regarding a detected cybersecurity incident.

| Category | ID | Key Requirements |
|----------|-----|-----------------|
| Incident Management | RS.MA | Manage incidents from detection through resolution |
| Incident Analysis | RS.AN | Investigate incidents to understand scope and impact |
| Incident Response Reporting and Communication | RS.CO | Coordinate response activities with internal and external stakeholders |
| Incident Mitigation | RS.MI | Contain and mitigate the effects of incidents |

### RECOVER (RC)

Restore capabilities or services impaired due to a cybersecurity incident.

| Category | ID | Key Requirements |
|----------|-----|-----------------|
| Incident Recovery Plan Execution | RC.RP | Execute recovery plans |
| Incident Recovery Communication | RC.CO | Coordinate restoration activities |

## Mapping to FDA Cybersecurity Guidance

| FDA Requirement | CSF Function(s) | Notes |
|----------------|-----------------|-------|
| Threat model | ID.RA | Systematic identification of threats and vulnerabilities |
| Security architecture | PR.AA, PR.DS, PR.PS | Controls mapped to architecture |
| SBOM | ID.AM | Asset inventory including all software components |
| Cybersecurity risk assessment | GV.RM, ID.RA | Risk evaluation with severity and likelihood |
| Security testing | PR.PS, DE.CM | Verification of security controls |
| Vulnerability management | ID.RA, RS.MA | Post-market vulnerability monitoring and response |
| Patch/update mechanism | PR.PS | Secure update capability |
| Incident response | RS.MA, RS.AN, RS.CO | Response plan for security events |

## Mapping to IEC 81001-5-1

The CSF categories align with IEC 81001-5-1 lifecycle processes:

| CSF Function | IEC 81001-5-1 Clause |
|-------------|---------------------|
| Govern | Clause 4 (General requirements) |
| Identify | Clause 7 (Security risk management) |
| Protect | Clause 5 (Development security), Clause 8 (Configuration management) |
| Detect | Clause 6.1 (Security monitoring) |
| Respond | Clause 9 (Problem resolution) |
| Recover | Clause 6.2 (Patch management) |
