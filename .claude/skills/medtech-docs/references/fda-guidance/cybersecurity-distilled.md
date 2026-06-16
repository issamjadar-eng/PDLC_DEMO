# FDA Guidance: Cybersecurity in Medical Devices

🔎 **Finding aid — NOT the authoritative source.** Distilled summary for quick orientation and early analysis. Ground and cite the authoritative full text [`source-md/cybersecurity.md`](source-md/cybersecurity.md); verify any quote against the byte-correct `source/` PDF before treating it as verbatim. This paraphrases and omits (appendices/worked examples are routinely dropped) — a section's absence here is never evidence the source is silent.

**Full Title**: Cybersecurity in Medical Devices: Quality System Considerations and Content of Premarket Submissions
**Document Date**: September 27, 2023
**Status**: Final (Contains Nonbinding Recommendations)
**PDF Source**: https://www.fda.gov/media/173984/download
**Issuing Body**: CDRH (with CBER considerations)
**Supersedes**: "Content of Premarket Submissions for Management of Cybersecurity in Medical Devices" (October 2, 2014)
**Statutory Basis**: Section 524B of FD&C Act (added by FDORA, part of Consolidated Appropriations Act 2023; effective March 29, 2023)

## Scope

This guidance applies to **all devices that contain software (including firmware) or programmable logic**, as well as devices with device software functions. This includes devices whether or not they require a premarket submission. The guidance is **not limited** to network-enabled or internet-connected devices -- any device with software/firmware/programmable logic is in scope.

### Applicable Submission Types

510(k) (including Special and Abbreviated), De Novo, PMA and PMA supplements, Product Development Protocols, IDE, HDE, BLA, and IND submissions.

### Cyber Device Definition (Section 524B)

Section 524B(c) defines a "cyber device" as a device that:
1. Includes software validated, installed, or authorized by the sponsor as/in a device
2. Has the **ability to connect to the internet**
3. Contains technological characteristics that could be **vulnerable to cybersecurity threats**

The statutory requirements under 524B apply specifically to cyber devices. The guidance has a **broader scope** than just cyber devices -- it applies to all software-containing medical devices.

### Cloud-Connected Devices / SaMD

All guidance recommendations apply to devices that exist solely in the cloud (SaMD products) or that interface with cloud environments. Architecture descriptions should describe the cloud environment, services leveraged, and the shared responsibility model (manufacturer vs. cloud service provider).

## Key Requirements

### Section 524B Statutory Requirements (for Cyber Devices)

Sponsors must provide:

1. **Post-market cybersecurity plan**: Monitor, identify, and address post-market vulnerabilities and exploits, including coordinated vulnerability disclosure procedures
2. **Process documentation**: Design, development, and maintenance processes providing reasonable assurance the device is cybersecure
3. **Update/patch capability**: Post-market updates and patches for known unacceptable vulnerabilities on a regular cycle, and critical vulnerabilities as soon as possible out-of-cycle
4. **Software Bill of Materials (SBOM)**: Including commercial, open-source, and off-the-shelf software components
5. **Other requirements**: Comply with such other requirements as the Secretary may require through regulation to demonstrate reasonable assurance of cybersecurity (the statutory catch-all)

### General Principles

**Principle 1: Cybersecurity is Part of Safety.** Cybersecurity is integral to device safety and effectiveness. A Secure Product Development Framework (SPDF) can fulfill aspects of the QS Regulation.

**Principle 2: Design In, Not Bolt On.** Cybersecurity controls should be designed into the device from the start. Key security objectives:
- Authenticity (including integrity controls)
- Authorization
- Availability
- Confidentiality
- Secure and timely updateability and patchability

To meet these objectives, the guidance outlines **eight security control categories** that manufacturers should consider and implement; **Appendix 1** provides specific control recommendations and implementation guidance (the source names the eight categories + Appendix 1 — consult them for the full control set).

**Principle 3: Transparency.** End users need cybersecurity information to ensure continued safe use throughout the total product lifecycle.

**Principle 4: Documentation Scales with Risk.** Cybersecurity documentation recommendations complement and are in addition to software premarket guidance, scaled to the cybersecurity risks of the device.

### Security Risk Management

**System-level assessment required.** Considering the device in isolation risks missing threats and controls.

**Distinct from safety risk management** but the two processes should feed into each other to ensure coverage of both safety and security risks.

**Key documentation deliverables:**
1. Security Risk Management Report (e.g., per AAMI TIR57)
2. Threat Modeling Documentation -- full system and lifecycle scope
3. Cybersecurity Risk Assessment -- use **exploitability** (not probability) to assess risks, as human-actor threats cannot use traditional probabilistic methods
4. Interoperability Considerations -- cybersecurity controls should not prohibit data access
5. Third-Party Software Component Assessment -- SBOM, support/end-of-support info, vulnerability assessment
6. Security Assessment of Unresolved Anomalies
7. Total Product Lifecycle Security Risk Management

**Threat Modeling:**
- Must include the full system and lifecycle
- May include architecture views
- Justify chosen methodology (e.g., STRIDE, NIST 800-30) and explain appropriateness

**Risk Assessment Methodology:**
- Use exploitability instead of probability for likelihood assessment
- CVSS is a risk prioritization tool, not a risk acceptance methodology -- may require adaptation
- Justify selected methodology and fitness for purpose

### SBOM Requirements

**Statutory requirement** for cyber device submissions under Section 524B.

**Format and content:**
- Must be machine-readable
- Consistent with NTIA minimum elements (October 2021, second edition)
- Conform with industry-accepted formats in labeling
- Must be complete -- all transitive dependencies included
- If transitive dependencies unknown, justify the gap

**Accompanying information (may be provided separately):**
1. Software level of support (monitoring/maintenance from component manufacturer)
2. Software component end-of-support date
3. Safety and security risk assessment for each known vulnerability
4. Details of applicable risk controls for identified vulnerabilities

**Vulnerability information sources:** Software component suppliers, NIST NVD, CISA Known Exploited Vulnerability Catalog.

**All components required:** FDA does not accept a risk-based approach to selectively including components.

### Security Architecture Views

Four recommended categories:

1. **Global system view**
2. **Multi-patient harm view** -- how a cybersecurity event could affect multiple patients
3. **Updateability and patchability view** -- how patches are delivered
4. **Security use case views** -- all use cases for operational states and clinical scenarios

Architecture views should identify security-relevant elements and interfaces, define security context/domains/boundaries, align with security objectives, and establish traceability to security requirements. The appendices in the guidance are part of the recommendations (not merely informative).

### Cybersecurity Testing

Four types recommended:

1. **Security requirement testing** -- verifying security requirements are met
2. **Threat mitigation testing** -- verifying mitigations are effective
3. **Vulnerability testing** -- identifying vulnerabilities
4. **Penetration testing** -- attempting to exploit vulnerabilities

Testing should be system-level, including all system elements and the use environment. Independence and technical expertise of testers is recommended. Third-party testing may be appropriate for some elements.

**For legacy/resubmission devices:** All documentation and all testing types should be provided, regardless of whether the device is new or a modification. Architecture views required even for legacy devices that never previously provided them.

### Cybersecurity Management Plan

**Required** for cyber device submissions under Section 524B. Should include:

- How the manufacturer will manage cybersecurity throughout the device lifecycle
- Response to vulnerabilities and incidents
- Coordinated vulnerability disclosure processes
- Periodic security testing
- Timeline to develop and release patches
- Patching capability (rate at which updates can be delivered)
- Personnel responsible (organizational roles with accountability, not individual names)

### Cybersecurity Labeling

- Can be provided in different locations depending on audience (IFU manual vs. security implementation guide)
- Labeling mitigations and risk transfer items may need inclusion in human factors testing
- Must provide sufficient information for device integration, managing cybersecurity risks, and implementing necessary measures
- FDA recommends SBOMs be included in labeling (distinct from 524B requirement to provide SBOM to FDA)

### Devices That Cannot Be Patched

- Document limitations in the submission
- FDA examines whether field service personnel can update the device
- If only option is device replacement, document capabilities and timelines
- General expectation: all new devices with software/firmware should have an update mechanism

### Transition and Enforcement

- No official transition period
- Cybersecurity RTA Policy guidance expired October 1, 2023
- FDA expects sponsors to have had sufficient time to prepare compliant submissions

## Key Definitions

| Term | Definition |
|------|-----------|
| **Cyber device** | A device that includes software, has internet connectivity, and contains characteristics vulnerable to cybersecurity threats (per Section 524B(c)) |
| **SBOM (Software Bill of Materials)** | Machine-readable inventory of all software components including commercial, open-source, and off-the-shelf components with transitive dependencies |
| **SPDF (Secure Product Development Framework)** | Framework for integrating cybersecurity into the device development lifecycle |
| **Exploitability** | Assessment of likelihood of a cybersecurity vulnerability being exploited, used instead of probability for human-actor threats |
| **Coordinated vulnerability disclosure** | Process for publicly sharing information about cybersecurity vulnerabilities |

## Submission Requirements

For all software-containing devices, cybersecurity documentation is expected in premarket submissions:
- Security risk management report
- Threat modeling documentation
- Cybersecurity risk assessment
- SBOM (required for cyber devices under 524B)
- Security architecture views (all four categories)
- Cybersecurity testing results (all four types)
- Cybersecurity labeling
- Cybersecurity management plan (required for cyber devices under 524B)

Documentation should scale with the cybersecurity risks of the device.

## Cross-References

- **Premarket Software Guidance**: "Content of Premarket Submissions for Device Software Functions" -- cybersecurity documentation complements software documentation
- **Postmarket Cybersecurity Guidance**: "Postmarket Management of Cybersecurity in Medical Devices" (2016)
- **AAMI TIR57**: Principles for medical device security -- risk management
- **NTIA SBOM Framework**: "Framing Software Component Transparency" (October 2021, second edition)
- **NIST**: National Vulnerability Database (NVD)
- **CISA**: Known Exploited Vulnerability Catalog
- **STRIDE**: Microsoft threat modeling methodology
- **NIST 800-30**: Guide for Conducting Risk Assessments
- **CVSS**: Common Vulnerability Scoring System
- **Interoperability Guidance**: "Design Considerations and Premarket Submission Recommendations for Interoperable Medical Devices"
