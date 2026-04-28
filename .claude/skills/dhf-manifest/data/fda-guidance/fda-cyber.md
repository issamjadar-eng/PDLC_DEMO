# Tier 1 Regulatory Distillation — FDA Cybersecurity Premarket Guidance

**Guidance**: Cybersecurity in Medical Devices: Quality System Considerations and Content of Premarket Submissions
**Date**: September 27, 2023 (Final)
**Statutory basis**: FD&C Act §524B (added by FDORA; effective March 29, 2023)
**Topic coverage**: cybersecurity, regulatory-submission
**Distillation date**: 2026-04-21
**Source references**:
- `.claude/skills/medtech-docs/references/fda-guidance/cybersecurity-distilled.md`

> **Note**: FDA guidance is nonbinding. §524B requirements are statutory (binding). Obligations reflect both.

---

<a id="OBL-CYBER-001"></a>

```yaml
id: OBL-CYBER-001
title: "§524B Statutory Requirements"
source: FDA Cybersecurity Guidance (2023) §524B Statutory Requirements
section: "Section 524B — Statutory Requirements for Cyber Devices"
scope_flags: [cybersecurity, common-baseline]
topic: cybersecurity
artifact_type: submission-content
dhf_owner: system
min_iec62304_class: A
applies_to: [510(k) Submission — Cybersecurity Documentation, Post-Market Cyber Plan, SBOM]
verbatim: "Sponsors must provide: (1) post-market cybersecurity plan to monitor, identify, and address post-market vulnerabilities and exploits, including coordinated vulnerability disclosure; (2) process documentation for design, development, and maintenance providing reasonable assurance the device is cybersecure; (3) update/patch capability for post-market updates and patches for known unacceptable vulnerabilities; (4) Software Bill of Materials (SBOM) including commercial, open-source, and off-the-shelf software components."
extracted_requirements:
  - SBOM is a STATUTORY requirement for cyber device premarket submissions (FD&C Act §524B) — not optional
  - Post-market cybersecurity plan is STATUTORY — must describe how manufacturer monitors, identifies, and addresses vulnerabilities
  - Process documentation demonstrating cybersecure design, development, and maintenance must be included in the submission
  - Update and patch capability must be built into the device — mechanism for both regular-cycle and out-of-cycle critical vulnerability patches
  - MedTech Project qualifies as a "cyber device" (includes software, internet-connected, vulnerable to cyber threats) — all §524B requirements apply
```

**Context**: MedTech Project is a cyber device under FD&C Act §524B — it includes software, connects to the internet (Management Services cloud), and has characteristics vulnerable to cybersecurity threats. All four §524B requirements are statutory obligations, not just FDA recommendations. The SBOM and post-market cybersecurity plan are mandatory 510(k) submission artifacts. Non-compliance means the submission may be refused to accept (RTA).

---

<a id="OBL-CYBER-002"></a>

```yaml
id: OBL-CYBER-002
title: "Security Risk Management"
source: FDA Cybersecurity Guidance (2023) §III Security Risk Management
section: "Security Risk Management — Documentation"
scope_flags: [cybersecurity, common-baseline]
topic: cybersecurity
artifact_type: submission-content
dhf_owner: system
min_iec62304_class: A
applies_to: [Security Risk Management Report, Threat Model, 510(k) Submission]
verbatim: "Security Risk Management Report (e.g., per AAMI TIR57). Threat Modeling Documentation — full system and lifecycle scope. Cybersecurity Risk Assessment — use exploitability (not probability) to assess risks. Third-Party Software Component Assessment — SBOM, support/end-of-support info, vulnerability assessment."
extracted_requirements:
  - Include a Security Risk Management Report in the premarket submission (per AAMI TIR57 or equivalent)
  - Include Threat Modeling Documentation covering the full system and full lifecycle (not just the device in isolation)
  - Cybersecurity Risk Assessment must use exploitability (not probability) for likelihood assessment — human-actor threats cannot use traditional probabilistic methods
  - Third-party software component assessment: SBOM with support information, end-of-support dates, and vulnerability assessment per component
  - Security risk management is distinct from safety risk management (ISO 14971) but the two must feed each other
```

**Context**: For MedTech Project, the threat model must cover: the cloud-tablet communication link, the DICOM imaging device interface, Management Services APIs, the OTA update mechanism, and the tablet's local storage. Using exploitability (not probability) means the risk assessment must be grounded in what attackers can actually do (CVSS exploitability scores, STRIDE threat vectors) rather than statistical probabilities. The security risk management report is a 510(k) submission artifact, not just an internal document.

---

<a id="OBL-CYBER-003"></a>

```yaml
id: OBL-CYBER-003
title: "SBOM Requirements"
source: FDA Cybersecurity Guidance (2023) §IV SBOM Requirements
section: "SBOM Requirements"
scope_flags: [cybersecurity, common-baseline]
topic: cybersecurity
artifact_type: submission-content
dhf_owner: system
min_iec62304_class: A
applies_to: [SBOM, 510(k) Submission — Cybersecurity Section]
verbatim: "SBOM must be machine-readable. Consistent with NTIA minimum elements (October 2021, second edition). Must be complete — all transitive dependencies included. If transitive dependencies unknown, justify the gap. Accompanying information: software level of support, software component end-of-support date, safety and security risk assessment for each known vulnerability, details of applicable risk controls."
extracted_requirements:
  - SBOM must be machine-readable (SPDX or CycloneDX format)
  - SBOM must include all transitive dependencies — not just direct dependencies
  - SBOM fields (NTIA minimum): component name, version, supplier, dependency relationship, author, timestamp
  - For each SBOM component: document support level, end-of-support date, and vulnerability assessment
  - FDA does NOT accept a risk-based approach to selectively including components — all components must be listed
  - If transitive dependencies are unknown, this gap must be explicitly justified (not silently omitted)
```

**Context**: MedTech Project's system-level SBOM aggregates component-level SBOMs from all three modules. Each item DHF (Pre-Op, Intra-Op, Management Services) generates its own SBOM; the system DHF rolls them up. Machine-readable format (CycloneDX or SPDX) is required — a human-readable spreadsheet is not acceptable as the primary SBOM. Plan for SBOM generation as part of the CI/CD build process, not a manual pre-release effort.

---

<a id="OBL-CYBER-004"></a>

```yaml
id: OBL-CYBER-004
title: "Security Architecture Documentation"
source: FDA Cybersecurity Guidance (2023) §V Security Architecture
section: "Security Architecture Views — Four Categories"
scope_flags: [cybersecurity, common-baseline]
topic: architecture
artifact_type: submission-content
dhf_owner: system
min_iec62304_class: A
applies_to: [Security Architecture Document, 510(k) Submission — Cybersecurity Section, SAD]
verbatim: "Four security architecture view categories: (1) global system view; (2) multi-patient harm view — how a cybersecurity event could affect multiple patients; (3) updateability and patchability view — how patches are delivered; (4) security use case views — all use cases for operational states and clinical scenarios."
extracted_requirements:
  - Include all four security architecture view categories in the premarket submission
  - Global system view: shows all system elements, interfaces, trust boundaries, security domains
  - Multi-patient harm view: analyzes how a single cybersecurity event (e.g., supply chain attack, ransomware) could affect multiple patients simultaneously
  - Updateability/patchability view: diagrams how software updates/patches are delivered, authenticated, and applied
  - Security use case views: covers all operational states (normal, degraded, update, maintenance) and clinical scenarios
  - Architecture views must establish traceability to security requirements
```

**Context**: The multi-patient harm view is particularly important for MedTech Project — a cloud-hosted platform means a single cybersecurity event could affect all hospitals running MedTech Project simultaneously. The updateability view must show the OTA update mechanism for Intra-Op tablets, including how updates are authenticated and how the tablet verifies integrity before applying them. These four views are part of the required 510(k) submission package.

---

<a id="OBL-CYBER-005"></a>

```yaml
id: OBL-CYBER-005
title: "Cybersecurity Testing"
source: FDA Cybersecurity Guidance (2023) §VI Cybersecurity Testing
section: "Cybersecurity Testing — Four Types"
scope_flags: [cybersecurity, common-baseline]
topic: verification
artifact_type: submission-content
dhf_owner: system
min_iec62304_class: A
applies_to: [Security Test Report, 510(k) Submission — Cybersecurity Section]
verbatim: "Four types recommended: (1) security requirement testing — verifying security requirements are met; (2) threat mitigation testing — verifying mitigations are effective; (3) vulnerability testing — identifying vulnerabilities; (4) penetration testing — attempting to exploit vulnerabilities. Testing should be system-level, including all system elements and the use environment."
extracted_requirements:
  - Conduct all four types of cybersecurity testing before submission
  - Security requirement testing: verify each security requirement in the SRS is implemented
  - Threat mitigation testing: verify each threat mitigation from the threat model is effective
  - Vulnerability testing: active vulnerability scanning (automated tools)
  - Penetration testing: attempt to exploit identified vulnerabilities; third-party testing may be appropriate
  - Testing must be system-level — covering all system elements and the use environment (not just isolated components)
  - All four testing types are expected in the 510(k) submission regardless of device age/prior submissions
```

**Context**: Penetration testing is the most effort-intensive requirement. For MedTech Project, pentest must cover: Management Services APIs (authenticated and unauthenticated access), Intra-Op tablet network interfaces, DICOM ingestion pipeline, OTA update mechanism, and cloud-tablet sync link. Plan for a third-party pentest engagement as a late-stage pre-submission activity. Results of all four testing types go into the cybersecurity section of the 510(k).

---

<a id="OBL-CYBER-006"></a>

```yaml
id: OBL-CYBER-006
title: "Cybersecurity Management Plan"
source: FDA Cybersecurity Guidance (2023) §VII Cybersecurity Management Plan
section: "Cybersecurity Management Plan"
scope_flags: [cybersecurity, common-baseline]
topic: post-market
artifact_type: submission-content
dhf_owner: system
min_iec62304_class: A
applies_to: [Cybersecurity Management Plan, Post-Market Surveillance Plan, 510(k) Submission]
verbatim: "Required for cyber device submissions. Should include: how the manufacturer will manage cybersecurity throughout the device lifecycle, response to vulnerabilities and incidents, coordinated vulnerability disclosure processes, periodic security testing, timeline to develop and release patches, patching capability (rate at which updates can be delivered)."
extracted_requirements:
  - Cybersecurity Management Plan is REQUIRED for cyber device 510(k) submissions under §524B
  - Plan must describe: post-market vulnerability monitoring process, incident response procedure, coordinated vulnerability disclosure process
  - Plan must specify: patching timeline (regular cycle and critical/out-of-cycle), patching capability (how frequently updates can be deployed)
  - Plan must identify personnel responsible (organizational roles with accountability — not individual names)
  - Periodic security testing cadence must be defined
  - Cloud-hosted devices: describe the shared responsibility model (what MedTech Company manages vs. cloud provider)
```

**Context**: The Cybersecurity Management Plan is both a 510(k) submission artifact and a living post-market operational document. For MedTech Project, it must specify: how quickly critical vulnerabilities are patched (FDA expects out-of-cycle patches for critical vulnerabilities "as soon as possible"), who is responsible for monitoring (organizational role), and how MedTech Company coordinates with cloud providers (AWS/Azure shared responsibility model). The plan becomes an operational commitment — MedTech Company must actually follow it post-clearance.
