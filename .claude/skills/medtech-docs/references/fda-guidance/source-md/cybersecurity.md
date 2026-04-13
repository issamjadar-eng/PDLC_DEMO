# Cybersecurity in Medical Devices: Quality System Considerations and Content of Premarket Submissions — Final Guidance

## Metadata

| Field | Value |
|-------|-------|
| **Full Title** | Cybersecurity in Medical Devices: Quality System Considerations and Content of Premarket Submissions |
| **Document Type** | Final Guidance |
| **Document Date** | September 27, 2023 |
| **Webinar Date** | November 2, 2023 |
| **Center** | CDRH (Center for Devices and Radiological Health) |
| **Supersedes** | Content of Premarket Submissions for Management of Cybersecurity in Medical Devices (October 2, 2014) |
| **Related Statute** | Section 524B of the FD&C Act (added by FDORA, Consolidated Appropriations Act 2023) |
| **Presenter** | Matthew Hazelett (Cybersecurity Policy Analyst, Clinical and Scientific Policy Staff, OPEQ, CDRH) |
| **Moderator** | CDR Kim Piermatteo, Division of Industry and Consumer Education |
| **Panelists** | Aftin Ross (Acting Deputy Division Director, Division of All Hazards Response, OST); Jessica Wilkerson (Senior Cyber Policy Advisor, Medical Device Cybersecurity Team Lead, OST); Erin Quencer (Regulatory Policy Analyst, CDRH's Office of Policy) |

---

*This document is a transcript of the CDRH webinar held on November 2, 2023, discussing the final guidance on Cybersecurity in Medical Devices issued September 27, 2023.*

---

## Introduction

CDR Kim Piermatteo: Hello, everyone. Thanks for joining us, and welcome to today's CDRH webinar. This is Commander Kim Piermatteo of the United States Public Health Service. And I serve as the Education Program Administrator in the Division of Industry and Consumer Education in CDRH's Office of Communication and Education. I'll be the moderator for today's webinar.

Our topic today is the final guidance titled, Cybersecurity in Medical Devices: Quality System Considerations and Content of Premarket Submissions, which was issued on September 27, 2023. This guidance provides recommendations on medical device cybersecurity considerations and what information to include in premarket submissions. And it replaces the FDA's guidance titled, Content of Premarket Submissions for Management of Cybersecurity in Medical Devices, previously issued on October 2, 2014.

Before we begin, I'd like to provide two quick reminders for the webinar. First, please make sure you've joined us through the Zoom app and not through a web browser to avoid any technical issues. And second, the intended audience for this webinar is industry. Trade press reporters are encouraged to consult with the CDRH Trade Press team at CDRHTradePress@fda.hhs.gov. And members of national media may consult with FDA's Office of Media Affairs at FDAOMA@fda.hhs.gov.

I now have the pleasure of introducing our presenter for today's webinar, Matthew Hazelett, Cybersecurity Policy Analyst on the Clinical and Scientific Policy staff within the Office of Product Evaluation and Quality, or OPEQ, in CDRH.

## Learning Objectives

The learning objectives for today's webinar are to:

1. Describe the scope of the guidance
2. Describe the general principles in the guidance
3. Describe the design and documentation recommendations
4. Describe the transparency recommendations
5. Describe the changes and updates from the 2022 draft guidance

## Scope of the Guidance

This guidance document is applicable to devices that contain software, including firmware, or programmable logic, as well as devices that have device software functions. This includes devices within the meaning of Section 201(h) of the Federal Food, Drug, and Cosmetic Act, or FD&C Act, whether or not they require premarket submission. So, this means that devices that don't require premarket submissions, but meet the definition of a medical device and include software, firmware, or programmable logic, are all included within the scope.

The guidance is not limited to devices that are network-enabled or contain other connected capabilities. This is because devices that have software, firmware, or programmable logic have the potential to have cybersecurity risks; and therefore, the recommendations apply.

### Applicable Submission Types

For devices that do require premarket submission, the applicable submission types to either CDRH or CBER include:

- Premarket notification, or 510(k) submissions
- De Novo classification requests
- Premarket Approval Applications or PMAs, and PMA supplements
- Product Development Protocols
- Investigational Device Exemption submissions
- Humanitarian Device Exemption submissions
- Biologics License Application submissions
- Investigational New Drug submissions

The last two are new compared to the 2022 draft.

### Section 524B of the FD&C Act

The Consolidated Appropriations Act for 2023 was signed into law on December 29, 2022, and includes the Food and Drug Omnibus Reform Act, or FDORA, which adds Section 524B to the Food, Drug, and Cosmetic Act. These requirements went into effect on March 29, 2023.

These requirements apply to prospective submissions for what are identified as **cyber devices** under the 510(k), De Novo, Humanitarian Device Exemption, Product Development Protocol, and PMA pathways. These requirements also apply to special and abbreviated 510(k) applications, as well as PMA and HDE supplements.

### Definition of Cyber Device

Section 524B, subsection c, defines a cyber device as a device that:

- Includes software that a sponsor has validated, installed, or authorized as a device or in a device
- Has the ability to connect to the internet
- Contains any such technological characteristics a sponsor has validated, installed, or authorized that could be vulnerable to cybersecurity threats

### Section 524B Requirements

Section 524B, subsection b, requires sponsors of a cyber device application to provide documentation for the following:

1. **Postmarket cybersecurity plan**: Submit a plan to monitor, identify, and address, as appropriate, in a reasonable time, post-market cybersecurity vulnerabilities and exploits, including coordinated vulnerability disclosure and related procedures
2. **Secure design processes**: Provide documentation on how they design, develop, and maintain processes and procedures to provide a reasonable assurance that the device and related systems are cybersecure
3. **Patch and update capability**: Make available post-market updates and patches to the device and related systems to address on a reasonably justified regular cycle known unacceptable vulnerabilities and, as soon as possible, out of cycle critical vulnerabilities that could cause uncontrolled risks
4. **Software Bill of Materials (SBOM)**: Provide a software bill of materials, including commercial, open-source, and off-the-shelf software components
5. **Other requirements**: Comply with such other requirements as the Secretary may require through regulation to demonstrate a reasonable assurance that the device and related systems are cybersecure

## General Principles

### Principle 1: Cybersecurity is Part of Device Safety and the Quality System Regulation

Cybersecurity is a part of safety and effectiveness. Without appropriate cybersecurity controls, you can't have appropriate safety and effectiveness for the medical device. Cybersecurity also aligns with the Quality System Regulation. A secure product development framework, or SPDF, can be used to fulfill aspects of the Quality System Regulation.

### Principle 2: Designing for Security

Designing in, rather than bolting on, cybersecurity controls results in a more effective design of the device. Key security objectives medical devices should achieve include those that the FDA will review devices against during premarket submission.

### Principle 3: Transparency

End users need cybersecurity information to ensure the continued safe use of the device. This covers the total product lifecycle, from being able to appropriately install and use the device as well as maintaining the device and delivering updates throughout its lifecycle.

### Principle 4: Submission Documentation

The recommendations in this guidance complement and are in addition to the software premarket guidance. The cybersecurity documentation is expected to scale with cybersecurity risks of the device.

## Design and Documentation Recommendations

### Security Objectives

The design recommendations for ensuring appropriate cybersecurity controls focus on the security objectives:

- **Authenticity** (includes integrity controls)
- **Authorization**
- **Availability**
- **Confidentiality**
- **Secure and timely updateability and patchability** of the device

### Security Control Categories

The guidance outlines eight security control categories that manufacturers should consider and implement to help in meeting the security objectives. Appendix 1 provides specific control recommendations and implementation guidance for consideration to avoid common pitfalls in designing medical devices to achieve cybersecurity.

**Important note:** The appendices in this guidance are part of the document recommendations. This is different than some other documents, where the appendices may be informative.

### Documentation Recommendations

The documentation recommendations are covered in Sections 5 and 6 of the guidance:

- **Section 5: Using an SPDF to Manage Cybersecurity Risks** -- covers security risk management, security architecture, and cybersecurity testing
- **Section 6: Cybersecurity Transparency** -- covers labeling recommendations and cybersecurity management plans

### Security Risk Management

The guidance recommends that security risk management be a **system-level assessment**. This is important because if you only consider the device in isolation of the larger system or the environment of use, you're likely to miss the identification of potential risks and potential controls.

Key points:

- Security risk management is distinct from safety risk management, but the two processes should feed into and out of one another
- Known vulnerabilities should be assessed as reasonably foreseeable risks to the system
- Risk transfer should only occur if all relevant information is known, assessed, and communicated to users
- In premarket submissions, provide your security risk management report, such as that described in AAMI TIR57

#### Security Risk Management Subsections

The Security Risk Management section includes six subsections:

1. **Threat modeling documentation**: Should include the full system and the lifecycle of the device; may also include the architecture views
2. **Cybersecurity risk assessment**: Added to more clearly identify the documentation deliverable. Recommends using exploitability instead of probability to assess cybersecurity risks, as these risks depend on a human actor or cybersecurity threat that can't be modeled using traditional deterministic methods
3. **Interoperability considerations**: Added to underscore considerations for cybersecurity controls when having an interoperable device. Cybersecurity controls should not prohibit users from accessing device data but should ensure interoperability can be done safely and securely
4. **Third-party software components**: Recommendations for the Software Bill of Materials, support and end-of-support information, and vulnerability assessment
5. **Security assessment of unresolved anomalies**: Anomalies can present a different vector to safety risks through cybersecurity causes
6. **Total Product Lifecycle Security Risk Management**: Maintain resources and documentation throughout the lifecycle of the device; track and monitor cybersecurity measures and metrics

### Software Bill of Materials (SBOM)

Submission of a Software Bill of Materials is required for cyber device submissions under Section 524B of the FD&C Act.

**Requirements:**

- Provide machine-readable SBOMs
- SBOMs should be consistent with the minimum elements (baseline attributes) identified in the October 2021 NTIA Multistakeholder Process on Software Component Transparency
- When provided to users in labeling, SBOMs should conform with industry-accepted formats

**Accompanying information** (can be provided separately from the SBOM itself):

- Software level of support provided through monitoring and maintenance from the software component manufacturer
- Software components end-of-support date
- Safety and security risk assessment for each known vulnerability, including device and system impacts
- Details of applicable safety and security risk controls to address identified vulnerabilities

**Sources of vulnerability information** may include:

- Information from the software component suppliers
- Vulnerability databases, like the NIST National Vulnerability Database
- CISA's Known Exploited Vulnerability Catalog

### Architecture Views

The guidance recommends four different architecture view categories:

1. **Global system view**
2. **Multi-patient harm view**
3. **Updateability and patchability view**
4. **Security use case views** -- should identify all use cases for the operational states and different clinical use cases

The security architecture views should:

- Identify security-relevant system elements in their interfaces
- Define the security context, domains, boundaries, and external interfaces of the system
- Align the architecture with the system security objectives and requirements, as well as the security design characteristics
- Establish traceability of architecture elements to user and system security requirements

The level of recommended detail for the architecture views is captured in Appendix 2.

### Cybersecurity Testing

Four types of testing are recommended:

1. **Security requirement testing**
2. **Threat mitigation**
3. **Vulnerability testing**
4. **Penetration testing**

This section also makes recommendations on:

- Independence and technical expertise of testers
- Scope of testing (should be system-level and include all elements of the system and use environment considerations)
- When third-party testing is performed
- Submission documentation that should be provided

## Transparency Recommendations

### Labeling

The labeling recommendations are largely similar to the 2022 draft guidance, with some changes in reordering for greater clarity. Cybersecurity labeling can be provided in different locations, depending on the appropriate users for the information (e.g., instructions for use manual vs. security implementation guide for hospital-use devices).

Key points:

- Labeling mitigations and risk transfer items may need to be included as part of human factors testing tasks
- Labeling should focus on ensuring users have sufficient information to integrate the device and manage cybersecurity risks and updates throughout the device lifecycle

### Cybersecurity Management Plans

These plans are required for cyber device submissions under Section 524B. They include:

- How the manufacturer will approach managing cybersecurity throughout the lifecycle of the device, inclusive of responses to vulnerabilities and incidents
- Coordinated vulnerability disclosure processes (such as those described in the 2016 Postmarket Cybersecurity guidance)
- Periodic security testing to test identified vulnerability impact and look for new potential risks
- Timeline to develop and release patches to the device
- Patching capability (rate at which updates can be delivered to devices if needed)

## Key Changes from 2022 Draft Guidance

- **Expanded scope**: Included CBER submission types and considerations for combination products; added elements associated with Section 524B requirements
- **Structural changes**: Added new subsections in Security Risk Management for Cybersecurity Risk Assessments and interoperability considerations; added Appendix 4 to further clarify premarket submission documentation recommendations
- **Updated SBOM recommendations**: Aligned with 2021 NTIA SBOM framing document; clarified that supporting materials can be provided separate from the SBOM documentation itself

### Future Guidance Update

The agency plans to issue a draft select update to provide details on interpretation aspects of Section 524B that could not be included in this final guidance release. When finalized, this select update would be incorporated into the final guidance. The select update is on CDRH's A-list of priorities for fiscal year 2024.

## Questions and Answers

### Q: What kind of transition period is FDA going to provide for the final guidance?

Aftin Ross: There is no official transition period for the guidance. For any submissions made since the guidance issued, FDA may request the documentation identified in the guidance as we transition our internal review processes to align with the 2023 final guidance.

### Q: Which NTIA SBOM document does FDA recommend?

Jessica Wilkerson: We recommend that stakeholders refer to the second edition of the NTIA document, "Framing Software Component Transparency: Establishing a Common Software Bill of Materials," as the correct document. Both the guidance and the FAQ point to this document, which helps understand some of FDA's SBOM recommendations, including minimum elements and depth.

### Q: How does this guidance impact the March 2023 Cybersecurity RTA Policy guidance?

Erin Quencer: This final guidance does not supersede the previously issued Cybersecurity RTA guidance that issued on March 29, 2023. However, the policy in the Cybersecurity RTA Policy guidance expired on October 1 of 2023. Beginning on October 1, 2023, the FDA expects that sponsors of cyber devices will have had sufficient time to prepare premarket submissions that contain information required by Section 524B. The Cybersecurity RTA guidance is considered an expired guidance. This final guidance does supersede the October 2014 final guidance titled, "Content of Premarket Submissions for Management of Cybersecurity and Medical Devices."

### Q: How should resubmissions for legacy devices handle this guidance?

Matthew Hazelett: For submissions for changes to devices that have already been authorized, you should follow the recommendations in the 2023 final guidance, including the elements for documentation associated with Section 524B. We recommend that you provide all of the documentation elements identified in the guidance for submissions of modifications to existing devices -- not just information related to the changes, but all the new information as well.

### Q: Will FDA make changes to 21 CFR 809.10 for cybersecurity-specific IVD labeling?

Matthew Hazelett: The labeling recommendations apply to all device types under Section 201(h). Right now, there are no plans to change any specific regulations to any particular device types. But we do recommend that for all devices reviewed by CDRH that you provide the elements identified in the labeling section of the guidance.

### Q: How do we disclose SBOM findings to the FDA?

Matthew Hazelett: For vulnerabilities identified as part of your premarket development process, those can be a part of your device submission as part of the cybersecurity risk management documentation that accompanies the other elements provided, like the SBOM and the component support information. We recommend that you provide an assessment of the vulnerabilities for third-party software components as a part of that documentation. For vulnerabilities identified postmarket, there is the requirement under Section 524B to have plans for coordinated vulnerability disclosure and related processes. Vulnerabilities identified throughout the lifecycle should be disclosed in a coordinated fashion with the appropriate stakeholders, like CISA.

### Q: Can you clarify the scope difference between slide 5 (not limited to network devices) and slide 9 (connects to the internet)?

Jessica Wilkerson: The difference is related to the fact that one of the slides was discussing the language in Section 524B specifically, which has a statutory definition of what a cyber device is, which includes the requirement that the device have the ability to connect to the internet. This guidance has a broader scope than simply cyber devices to apply to all medical devices that fall within the scope rather than being solely limited to cyber devices.

### Q: What does "personnel responsible" mean in the cybersecurity management plan?

Matthew Hazelett: We're looking for the personnel with particular roles and responsibilities around the postmarket management lifecycle. This can include the identification of different roles within the product team or your postmarket management team that have responsibilities for performing management activities. It's more focused on personnel roles, not necessarily individual staff names or particular ratios.

### Q: Are SBOMs expected to be shared with customers?

Jessica Wilkerson: The guidance recommends that SBOMs be included as part of the labeling. This is distinct from the requirements within 524B that requires the SBOM be provided as part of the premarket submission. Those are two distinct things: providing the SBOM to FDA and providing the SBOM to end users. We recommend that SBOMs be made available to end users to assist them in understanding potential cybersecurity risk.

### Q: How do we address OTS components where we don't know all sub-dependencies?

Jessica Wilkerson: The NTIA framing document includes a discussion of depth. Our recommendation is that SBOMs be complete, meaning they have all transitive dependencies included. Where manufacturers may not know what all of the transitive dependencies are, we recommend providing the justification for why the information is not present.

### Q: To what level do we need to justify the choice of threat modeling or risk assessment methodology (e.g., STRIDE, NIST 800-30)?

Matthew Hazelett: We're looking for you to describe what methodology was used and the reasons why you believe that it is applicable or appropriate based on the elements of your system. There's pros and cons with any selected methodology. We're looking for you to describe why you selected the methodology and why you believe that it is sufficient to ensure you've appropriately captured the threats and applied an appropriate scoring methodology. You should provide a description of why you believe that particular methodology works based on your device characteristics, even for methodologies listed in the FDA guidance.

### Q: What are testing expectations for legacy devices that don't connect to networks?

Matthew Hazelett: Throughout the lifecycle of the device, there should be recurrent testing, especially if you're making changes and coming back to the agency with a new submission for modification. We recommend that all of the testing types identified in the guidance be completed if you're making another submission. This is to demonstrate that the controls that have been implemented are still effective against evolving cybersecurity risks.

All documentation outlined in the guidance would be provided for any submissions moving forward, regardless of whether they are new or making changes to existing devices. This includes all architecture views, even for products that have been in the market for 10-15 or more years where that was never previously provided.

### Q: Is a risk-based approach acceptable for large SBOMs with thousands of third-party components?

Jessica Wilkerson: We recommend that SBOMs include all third-party software and all off-the-shelf software components in order for both the FDA to do the appropriate risk assessment and risk analysis. All software components, all OTS, as well as manufacturer developed components should be included within the SBOM.

### Q: Is FDA harmonizing cybersecurity terminology with NIST and CIS?

Jessica Wilkerson: FDA sees cybersecurity considerations as being somewhat unique. A cybersecurity incident for medical devices may go beyond impacts to information systems and have patient safety considerations that may not be fully covered by NIST language. We used fit-for-purpose definitions and recommendations specifically for FDA's and the sector's needs to capture the larger use cases.

### Q: What does "boundary analysis" refer to in the context of security requirements testing?

Matthew Hazelett: We're looking for you to assess the overall architecture of the device and look for boundaries where there may be differences in trust levels in communications and how those interfaces handle those different boundaries. It's primarily about trust boundaries, but not limited to just the trust aspects -- it also includes what that boundary interface may cause in terms of risks and the appropriate controls.

### Q: For USB-connected Class II devices that are not cyber devices per Section 524B, what cybersecurity documentation is expected?

Matthew Hazelett: We look at all aspects of the system and the overall threat surface. When looking at interfaces like USBs, we look for the possibility of connectivity to a dongle that can enable Bluetooth or Wi-Fi connectivity as a potential vector. We look more holistically at the overall device, its environment of use, and the threat surface. If you have a particular question regarding a specific device type, we encourage you to reach out via a Q-Submission or to your particular review team.

### Q: What about devices not designed to be patchable?

Matthew Hazelett: If you have a device designed without the ability to update or patch it, provide a description of the limitations. But we look more broadly -- are there updates that can be made by service personnel? If the only option for an unacceptable risk is to replace the device, that should be discussed in the cybersecurity management plan. Generally, for devices with software or firmware, the expectation is that there would be some mechanism to patch or update the device.

### Q: Can threat modeling and architecture views be combined?

Matthew Hazelett: The architecture views may be included as part of the threat modeling documentation, but they should include the level of detail outlined in Appendix 2. The architecture view should still be a distinctive element within the threat modeling documentation if included there. There are four different architecture view types to address, not just the global system view.

### Q: Is CVSS appropriate for premarket cybersecurity risk assessment? Should we use CVSS 4.0?

Matthew Hazelett: We recommend using exploitability instead of probability. CVSS is intended as a risk prioritization methodology and not a risk acceptance methodology, which creates challenges for premarket use. Some manufacturers make adaptations to the CVSS scoring methodology. It's important to provide description of your methodology and justification. CVSS 4.0 just finalized, and it may be something people can consider, especially for postmarket risk assessments, but it likely still would not be appropriate as-is out of the box for premarket risk assessment scoring.

### Q: What is the status of SW96 being recognized as an FDA consensus standard?

Matthew Hazelett: We have recognized SW96. We just recently recognized it. So, it is currently in the standards database of FDA-recognized standards.

### Q: Is 524B documentation (SBOM) required for non-device MDDS components within a regulated device system?

Matthew Hazelett: For the particular MDDS components themselves, you wouldn't have to provide an SBOM. What you would need to provide is the cybersecurity considerations on the submitted medical device from those components. This is consistent with the multi-function device products guidance, where those are identified as "other functions," and the cybersecurity considerations from those non-medical device functions need to be considered for how they interact with and interface with the subject medical device submission.

### Q: Are there specific resources for cloud-connected devices?

Matthew Hazelett: There are no specific cloud-focused resources currently available. The security objectives and recommendations in the guidance do apply to devices that exist solely in the cloud (SaMD) or devices that interface with cloud environments. It's important to describe the architecture, the services being leveraged, and how that fits together to achieve the security objectives. Cloud environments have shared responsibility -- describe how you're going to maintain your elements of the architecture throughout the lifecycle.

### Q: How should TPLC security risk management metrics be provided for new devices without history?

Matthew Hazelett: The metrics should be provided if they're available. If it's a brand new device without history, provide a justification for why that information is not possible to provide. If you're submitting an iterative change, you can provide measures and metrics from the prior model. We acknowledge that not every new device will have these metrics available.

### Q: Is the eSTAR updated for this guidance and 524B?

Matthew Hazelett: The current eSTAR template identifies that an update to align with the guidance and 524B submission elements is forthcoming. That update will be made shortly.

## Closing Remarks

Matthew Hazelett: I wanted to thank everyone for attending and for all the questions. We know that there's a moving evolution of cybersecurity in the medical device space and we know that this is a change to how FDA has been evaluating documentation, but we really believe that this is the important documentation in order to provide continued safety and effectiveness for patients.

CDR Kim Piermatteo: Printable slides are currently available on CDRH Learn under the section titled "Specialty Technical Topics" and the subsection "Digital Health." A recording and transcript will be posted in the next few weeks.

If you have additional questions, reach out to DICE at DICE@fda.hhs.gov. For upcoming webinars, visit www.fda.gov/CDRHWebinar.
