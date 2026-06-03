# Computer Software Assurance for Production and Quality Management System Software

## Metadata

| Field | Value |
|-------|-------|
| **Full Title** | Computer Software Assurance for Production and Quality Management System Software |
| **Document Type** | Final Guidance (Revisions to Final) |
| **Document Date** | February 3, 2026 |
| **Supersedes** | "Computer Software Assurance for Production and Quality System Software," issued September 24, 2025 |
| **Docket Number** | FDA-2022-D-0795 |
| **Document Number** | GUI00017045 |
| **Centers** | CDRH and CBER |
| **Revision Basis** | Aligned with amendments to 21 CFR Part 820 (Quality Management System Regulation, QMSR) incorporating ISO 13485:2016 by reference |

---

## I. Introduction

FDA is issuing this guidance to provide recommendations on computer software assurance for computers and automated data processing systems used as part of medical device production or the quality management system. This guidance:

- Describes "computer software assurance" as a risk-based approach to establish confidence in the automation used for production or quality management systems, and identifies where additional rigor may be appropriate
- Describes various methods and testing activities that may be applied to establish computer software assurance and provide objective evidence to fulfill regulatory requirements, such as computer software validation requirements in quality management system obligations, including requirements in 21 CFR Part 820 (which incorporates by reference ISO 13485:2016)

This guidance supplements FDA's guidance "General Principles of Software Validation" except that it **supersedes Section 6** (Validation of Automated Process Equipment and Quality System Software) of that guidance.

FDA guidance documents describe the Agency's current thinking and are nonbinding recommendations. The word *should* means suggested or recommended, but not required.

---

## II. Background

FDA envisions a future state where the medical device ecosystem is inherently focused on device features and manufacturing practices that promote product quality and patient safety. Quality management system obligations in Part 820 are required for manufacturers of finished medical devices to the extent they engage in operations to which those obligations apply. These include requirements to validate computer software used as part of production or the quality management system.

Advances in manufacturing technologies — automation, robotics, simulation, digital capabilities — allow manufacturers to reduce sources of error, optimize resources, and reduce patient risk. Stakeholder engagement (via MDIC, site visits, benchmarking) has revealed desire for:

- Greater clarity on FDA's expectations for software validation for production/QMS software
- A more iterative, agile approach to validation

Traditional software validation via testing at each SDLC stage is often insufficient alone. FDA's Software Validation guidance recommends "software quality assurance" focus on preventing defect introduction and encourages a risk-based approach.

FDA believes a risk-based approach would better focus manufacturers' quality assurance activities to help ensure product quality while helping to fulfill validation requirements.

---

## III. Scope

This guidance provides recommendations regarding computer software assurance for **computers or automated data processing systems used as part of production or the quality management system for medical devices**.

**In scope:**
- Software used directly as part of production or QMS
- Software used to support production or QMS
- Cloud computing models (IaaS, PaaS, SaaS) when used as part of production or QMS

**Out of scope:**
- Device software functions (software that meets the definition of a device under section 201(h) of the FD&C Act) — see Software Validation guidance for those
- General business processes not specific to production or QMS (e.g., email, accounting)
- General infrastructure not specific to production or QMS (e.g., networking, user authentication, continuity of operations)

---

## IV. Definitions

**Cloud Computing (Cloud):** A model for enabling ubiquitous, convenient, on-demand network access to a shared pool of configurable computing resources (networks, servers, storage, applications, services) that can be rapidly provisioned and released with minimal management effort. Five essential characteristics: on-demand self-service, broad network access, resource pooling, rapid elasticity, measured service. Three service models: SaaS, PaaS, IaaS. Four deployment models: private, community, public, hybrid cloud.

**Infrastructure as a Service (IaaS):** Consumer provisions processing, storage, networks, and other fundamental computing resources; can deploy and run arbitrary software including operating systems and applications. Consumer does not manage the underlying infrastructure but has control over operating systems, storage, deployed applications, and possibly limited control of select networking components.

**Platform as a Service (PaaS):** Consumer deploys consumer-created or acquired applications onto the cloud infrastructure using programming languages, libraries, services, and tools supported by the provider. Consumer does not manage or control underlying infrastructure but has control over deployed applications and possibly configuration settings.

**Software as a Service (SaaS):** Consumer uses the provider's applications running on cloud infrastructure. Applications accessible from client devices via thin client interface (e.g., browser) or program interface. Consumer does not manage or control underlying cloud infrastructure, network, servers, OS, storage, or individual application capabilities, except possibly limited user-specific configuration settings.

---

## V. Computer Software Assurance

Computer software assurance is a **risk-based approach** for establishing and maintaining confidence that software is fit for its intended use. It considers the risk of compromised safety and/or quality of the device (should the software fail to perform as intended) to determine the level of assurance effort and activities. Follows a **least-burdensome approach** — no more burden than necessary to address the risk.

Computer software assurance establishes and maintains that software is in a "validated state" throughout its life cycle. Allows leveraging of: risk-based testing, unscripted testing, continuous performance monitoring, data monitoring, and validation activities performed by other entities (developers, suppliers, cloud service providers).

### A. Computer Software Assurance Risk Framework

A risk-based framework applied throughout the software's life cycle. Applicable to automation tools (BOTS, workflows), data analytic tools, AI/ML tools, and cloud computing when used as part of production or QMS.

#### (1) Identifying the Intended Use

Manufacturers must determine whether the software is or will be used as part of production or the quality management system (whether directly or to support production or QMS).

**Software used DIRECTLY as part of production or QMS:**
- Software intended for automating production processes, inspection, testing, or the collection and processing of production data
- Software intended for automating QMS processes, collection and processing of QMS data, or maintaining a quality record established under applicable QMS obligations

**Software used to SUPPORT production or QMS:**
- Software intended for use as development tools that test or monitor software systems or that automate testing activities for software used as part of production or QMS (e.g., tools used for developing and running scripts or software embedded in production equipment — firmware)
- Software intended for automating general record-keeping for production or QMS that is not part of the quality record

**Software generally NOT considered as part of production or QMS** (validation requirements under ISO 13485 Subclauses 4.1.6, 7.5.6, and 7.6 would not apply):
- Software for general business processes or operations not specific to production or QMS (e.g., email, accounting)
- Software for establishing or supporting infrastructure not specific to production or QMS (e.g., networking, user authentication, continuity of operations — backup and restore)

**Cloud computing note:** Not all cloud models are "directly" used as part of production or QMS. Focus assurance effort on features/functions relevant to the intended use. For example, an IaaS cloud storage solution storing quality records would be considered directly used as part of QMS — assurance effort should focus on integrity of records and 21 CFR Part 11 requirements.

FDA recommends manufacturers document their decision-making process for determining whether a software feature, function, or operation is or will be used as part of production or QMS.

Software may have multiple intended uses depending on individual features, functions, and operations, each presenting different risks. Manufacturers may conduct different assurance activities for individual features, functions, or operations as related to the intended use.

#### (2) Determining the Risk-Based Approach

Once a manufacturer determines that software is used as part of production or QMS, a risk-based analysis is used to determine appropriate assurance activities.

**Important distinction:** Risk-based analysis for production/QMS software under this guidance is **distinct** from risk analysis for a medical device under ISO 14971:2019. The production/QMS software risk analysis focuses on factors that may impact or prevent the software from performing as intended (system configuration, security, data integrity, storage, transfer, operation error), not on patient harm directly.

**Process risk vs. medical device risk:**
- *Process risk*: potential to compromise production or the quality management system
- *Medical device risk*: potential for a device to harm the patient or user

**High process risk** — software feature, function, or operation where **failure to perform as intended may result in a quality problem that foreseeably compromises safety (a medical device risk)**:

Examples of HIGH process risk:
- Maintain process parameters (temperature, pressure, humidity) that affect physical properties of product or manufacturing processes identified as essential to device safety
- Measure, inspect, analyze and/or determine acceptability of product or process with limited or no additional human awareness or review
- Perform process corrections or adjustments of process parameters based on data monitoring or automated feedback without additional human awareness or review
- Produce instructions for use or labeling provided to patients and users necessary for safe device operation
- Automate surveillance, trending, or tracking of data the manufacturer identifies as essential to device safety (e.g., cybersecurity) and quality

**Not high process risk** — failure to perform as intended **would not result in a quality problem that foreseeably compromises safety**:

Examples of NOT HIGH process risk:
- Collect and record data from the process for monitoring and review purposes that do not have direct impact on production or process performance
- Used as part of QMS for CAPA routing, automated logging/tracking of complaints, automated change control management, or automated procedure management
- Intended to manage data (process, store, and/or organize data), automate an existing calculation, increase process monitoring, or provide alerts relevant to managing data when an exception occurs in an established process
- Used to support production or QMS as explained in Section V.A.1

Process risks are on a spectrum; FDA presents them in binary manner ("high process risk" and "not high process risk") for guidance purposes. Manufacturers may determine intermediate levels (moderate, intermediate, low) and apply the "not high process risk" guidance accordingly.

#### (3) Production or Quality Management System Software Changes

For PMA/HDE devices: PMA/HDE supplements generally not required for changes to manufacturing procedure or method of manufacturing that do not affect safety or effectiveness (reported in annual report). Changes affecting safety and effectiveness submitted in 30-day notice.

For additions or changes to software used in production or QMS of PMA/HDE devices: apply principles in Section V.A.2 to determine whether the change may affect safety or effectiveness. If a change may result in a quality problem that foreseeably compromises safety → submit in 30-day notice. If not → appropriate to report in annual report.

#### (4) Determining the Appropriate Assurance Activities

**For HIGH process risk software** (quality problem may foreseeably compromise safety): level of assurance commensurate with the **medical device risk**. Higher risk of compromised safety → greater amount of objective evidence.

**For NOT HIGH process risk software**: level of assurance commensurate with the **process risk**.

Testing methods:

**Unscripted Testing:** Dynamic testing in which the tester's actions are not prescribed by written instructions in a test case.
- *Scenario Testing (Ad-Hoc Testing)*: Specification-based technique based on exercising sequences of interactions between the test item and other systems
- *Experience-Based Testing*: Uses experience of testers to generate test cases; can include:
  - *Error guessing*: Test cases derived from tester's knowledge of past failures or failure modes
  - *Exploratory testing*: Tester spontaneously designs and executes tests based on existing knowledge; looks for hidden properties, unanticipated user behaviors, or accidental use situations

**Scripted Testing:** Test cases recorded (e.g., in a test management tool or spreadsheet) and executed manually or automatically.
- *Robust scripted testing*: Detailed test cases with step-by-step procedures, expected results, independent review and approval
- *Limited scripted testing*: Limited test cases identified, expected results, unscripted testing applied, independent review when appropriate

FDA recommends applying principles of risk-based testing where the management, selection, prioritization, and use of testing activities and resources are consciously based on risk. Unscripted testing may be better suited for some high process risk features; scripted testing may be more effective for some not-high-process risk features.

#### (5) Additional Considerations for Assurance Activities

Manufacturers should consider additional controls and mechanisms in place throughout the QMS that may decrease the impact of compromised safety/quality if software failure were to occur. These can reduce effort of additional assurance activities:

- **Process controls**: Activities and established processes that provide control in production or fully verify processes in which software is involved (procedures for data integrity, subsequent inspection/testing, software QA by other organizational units)
- **Purchasing controls**: Established processes for selecting and monitoring software vendors; may incorporate vendor's existing validation work
- **Cybersecurity controls**: Additional process controls to reduce cybersecurity exposure
- **Monitoring/data collection**: Data periodically or continuously collected by software for detecting issues and anomalies after implementation
- **Development tools**: Bug tracking, anomaly tracking, requirement traceability tools for assurance of software used in production or QMS
- **Iterative testing**: Testing and results done in iterative cycles and continuously throughout the life cycle

**Vendor assessment — risk-based approach:**
- Onsite audits of the vendor (if feasible and appropriate)
- Review of vendor's accreditations and certifications (SOC reports, ISO certifications)
- Review of vendor's practices and documentation for software development, software QA, cybersecurity (security risk assessments, threat modeling, security design and development reviews, SBOM, testing) and risk mitigation
- Review of vendor's or software's data integrity capabilities or controls:
  - Retaining records, archiving data, generating accurate and complete copies of records
  - Securing data at rest and in transit (secure, computer-generated, time-stamped audit trails; encrypting data)
  - Establishing and maintaining access controls, electronic signature controls, and authorization checks

Supporting software often carries lower risk — assurance activities used "directly" in production or QMS often inherently cover performance of supporting software; additional scripted or unscripted testing may be unnecessary.

#### (6) Establishing the Appropriate Record

Manufacturer should capture sufficient objective evidence to demonstrate that the software feature, function, or operation was assessed and performs as intended.

**Record should include:**
- The intended use of the software feature, function, or operation
- The result of the risk-based analysis of the software feature, function, or operation
- Documentation of the assurance activities conducted:
  - A description of the testing conducted based on the assurance activity
  - Issues found during testing (deviations, defects, failures)
  - A conclusion declaring acceptability of the software for its intended use (including resolution of issues found or process controls/risk justification addressing why issues will not impact intended use)
  - Record of who performed testing/assessment and date
  - Established review and approval when appropriate

Documentation need not include more evidence than necessary to show software performs as intended for the risk identified.

**FDA recommends incorporating digital records** — system logs, audit trails, and other data generated and maintained by the software — as opposed to paper documentation, screenshots, or duplicating results already digitally retained.

**Table 1 — Examples of Assurance Activities and Records:**

| Assurance Activity | Test Plan | Test Results | Record (Including Digital) |
|-------------------|-----------|--------------|---------------------------|
| **Scripted Testing: Robust** | Test objectives; Test cases (step-by-step procedure); Expected results; Independent review and approval when appropriate | Result record for each test case; Details regarding any failures/deviations found | Intended use; Risk-based analysis result; Detailed report of testing performed; Result for each test case; Issues found; Conclusion (acceptability + resolution of issues); Record of who performed and date; Review and approval when appropriate |
| **Scripted Testing: Limited** | Limited test cases (step-by-step) identified; Expected results; Identify unscripted testing applied; Independent review when appropriate | Result record for each test case; Details of failures/deviations | Intended use; Risk-based analysis result; Summary of testing; Result for each test case; Issues found; Conclusion; Record of who/when; Review and approval when appropriate |
| **Unscripted Testing: Scenario Testing** | Testing of features and functions with no test plan | Details of failures/deviations found | Intended use; Risk-based analysis result; Summary of features/functions tested and testing performed; Issues found; Conclusion; Record of who/when; Review and approval when appropriate |
| **Unscripted Testing: Error Guessing** | Testing of failure-modes with no test plan | Details of failures/deviations found | Intended use; Risk-based analysis result; Summary of failure-modes tested and testing performed; Issues found; Conclusion; Record of who/when; Review and approval when appropriate |
| **Unscripted Testing: Exploratory Testing** | Establish high level test plan objectives with pass/fail criteria for each objective (no step-by-step procedure necessary) | Details of failures/deviations found | Intended use; Risk-based analysis result; Summary of objectives tested and testing performed; Issues found; Conclusion; Record of who/when; Review and approval when appropriate |

### B. Considerations for Electronic Records Requirements

Manufacturers should refer to the "Part 11, Electronic Records; Electronic Signatures — Scope and Application" guidance (Electronic Records guidance) when determining whether and how to apply 21 CFR Part 11.

**Part 11 applies to:**
- Records in electronic form that are created, modified, maintained, archived, retrieved, or transmitted under any records requirements in Agency regulations
- Electronic records submitted to the Agency under FD&C Act and PHS Act requirements

**Predicate rules** for computer software used as part of production or QMS include those under Part 820. A document required under Part 820 — including a document that requires a signature — maintained in electronic form would generally be an "electronic record" under Part 11.

**When Part 11 applies:** To determine whether a record is required under Part 820, consider whether the record would be necessary as evidence to document required validation. If a manufacturer maintains in electronic form a document required under Part 820, then Part 11 generally applies.

**FDA enforcement discretion:** FDA intends to exercise enforcement discretion regarding specific Part 11 requirements for validation of computerized systems used to create, modify, maintain, or transmit electronic records (21 CFR 11.10(a) and 11.30). However, this enforcement discretion expressly **does not apply** to validation requirements for computer software used as part of production or QMS arising under ISO 13485 Subclauses 4.1.6, 7.5.6, and 7.6.

FDA recommends manufacturers base their approach to computer software assurance on a justified and documented risk assessment and a determination of the potential of the system to affect product quality, patient safety, and record integrity. The risk-based approach in this guidance can provide assurance that software maintaining electronic records subject to Part 11 performs as intended.

---

## Appendix A. Examples

### Example 1: Nonconformance Management System

A manufacturer has purchased and configured COTS software for automating their nonconformance process. Intended to manage the nonconformance process electronically.

**Vendor assessment performed:**
- Evaluation of vendor's software development life cycle
- Review of vendor's quality management system and relevant certifications
- Review of vendor's cybersecurity documentation and life cycle management plans and certifications

**Table 2 — CSA Example for Nonconformance Management System:**

| Feature/Function | Intended Use | Risk-Based Analysis | Assurance Activities | Record |
|-----------------|--------------|--------------------|--------------------|--------|
| Nonconformance Initiation Operations | Manage workflow and error-proof the nonconformance; complete quality record; supplement containment processes | Failure may delay initiation workflow but would not result in quality problem that foreseeably compromises safety (manufacturer has additional containment processes: separation of affected product, alerting line management, labeling affected product) → **Not high process risk** | System capability assessment, supplier evaluation, installation activities + exploratory testing (high level objectives, no unanticipated failures) | Intended use; risk-based analysis; summary of operations tested; testing objectives and pass/fail; issues found; conclusion (acceptability + resolution); record of who/when |
| Electronic Signature Function | Capture and store electronic signature where required; meets requirements for electronic signatures | Failure may compromise or delay compliance with regulatory requirements and established SOPs but would not result in quality problem that foreseeably compromises safety → **Not high process risk** | System capability assessment, supplier evaluation, installation activities + scenario testing with users | Intended use; risk-based analysis; testing performed; issues found; conclusion; record of who/when |
| Product Containment Function | Trigger necessary evaluation and decision-making on whether product correction or removal is needed when nonconformance occurs in distributed product | Failure would result in necessary correction or removal not being initiated → quality problem that foreseeably compromises safety → **High process risk** | System capability assessment, supplier evaluation, installation activities + detailed scripted test protocol (possible interactions and potential failures, repeatability testing) | Intended use; risk-based analysis; detailed test protocol; detailed report of testing; pass/fail results for each test case; issues found; conclusion; record of who/when; signature and date of signatory authority per established SOP |

### Example 2: Learning Management System (LMS)

A manufacturer implementing a COTS LMS intended to manage, record, track, and report on training.

**Vendor assessment:** SDL evaluation; QMS and certifications review.

**Table 3 — CSA Example for LMS:**

| Feature/Function | Intended Use | Risk-Based Analysis | Assurance Activities | Record |
|-----------------|--------------|--------------------|--------------------|--------|
| Access Control, User Management, and Notification Functions | Manage user access, workflow, and user notifications regarding training | Failure would impact integrity of quality record but would not foreseeably compromise safety → **Not high process risk** | System capability assessment, supplier evaluation, installation activities + unscripted testing (error-guessing to attempt to circumvent process flow and verify access controls) | Intended use; risk-based analysis; summary of failure modes tested; issues found; conclusion; record of who/when |
| Record-keeping and Reporting Functions | Capture and maintain evidence of user training completion; generate analytic reports on records | Failure would impact integrity of quality record but would not foreseeably compromise safety → **Not high process risk** | System capability assessment, supplier evaluation, installation + unscripted testing to verify record integrity and report generating functions (e.g., try to delete audit trail) | Intended use; risk-based analysis; summary of failure modes tested; issues found; conclusion; record of who/when |

### Example 3: Business Intelligence Applications

A manufacturer implementing a commercial BI solution for data mining, analytics, and reporting. Intended to better understand product and process performance, identify improvement opportunities.

**Vendor assessment:** SDL evaluation; QMS and certifications; cybersecurity documentation and lifecycle management plans.

**Table 4 — CSA Example for Business Intelligence Application:**

| Feature/Function | Intended Use | Risk-Based Analysis | Assurance Activities | Record |
|-----------------|--------------|--------------------|--------------------|--------|
| Connectivity Functions | Ensure secure and robust capability to connect to appropriate data sources; ensure integrity of the data; prevent data corruption, modify, and store data appropriately | Failure would result in inaccurate or inconsistent trending or analysis, potentially failing to identify quality trends — in some cases, quality problem that foreseeably compromises safety → **High process risk** | Medical device risk-based assurance; system capability assessment, supplier evaluation, installation + detailed scripted test protocol (possible interactions and potential failures, repeatability testing) | Intended use; risk-based analysis; detailed test protocol; detailed report of testing; pass/fail results; issues found; conclusion; record of who/when; signatory authority signature and date per established SOP |
| User Help Feature | Facilitate interaction of the user with the system; provide assistance on all system features | Failure unlikely to result in quality problem leading to compromised safety → **Not high process risk** | No additional assurance effort beyond vendor assessment | Intended use; risk-based analysis; record of who/when; conclusion |
| Reporting Functions | Allow user to query data sources, join data from various sources, perform data mining; allow statistical analysis and data summarization; create graphs and reports | Failure may result in incomplete/inadequate reports but would not foreseeably lead to compromised safety (collection and recording for monitoring and review without direct impact on production or process performance) → **Not high process risk** | Supplier has validated ability to create and perform queries, join data, perform data mining, statistical analysis, data summarization, create graphs and reports. Manufacturer assessed system capability and performed supplier evaluation and installation | Intended use; risk-based analysis; record of who/when; conclusion including resolution, justification, and/or process controls addressing impact of issues |

### Example 4: Software as a Service (SaaS) Product Life Cycle Management System (PLM)

A manufacturer implementing a SaaS-based PLM. Intended to automate intake of project requirements, develop project plans, monitor/track project execution, and maintain relevant records, signatures, and deliverables upon project closing. Does not directly impact patient safety or product quality but does maintain a quality record where integrity of data is needed. No customization needed — basic standard configuration only (user roles, accounts).

**Vendor assessment:** SDL evaluation; QMS and certifications; cybersecurity documentation and lifecycle management plans; infrastructure support including availability and reliability. Manufacturer also establishes a service agreement with SaaS vendor (security, data integrity, privacy, availability, change management, business continuity).

**Automatic Updates:** SaaS vendor provides documentation summarizing changes, testing, and testing results of all automatic updates. Manufacturer performs assessment of changes and effect on intended use, performs risk-based assurance testing appropriate to the impact identified, and maintains a record summarizing the risk assessment and any assurance activities performed.

**Table 5 — CSA Example for SaaS PLM:**

| Feature/Function | Intended Use | Risk-Based Analysis | Assurance Activities | Record |
|-----------------|--------------|--------------------|--------------------|--------|
| Project Initiation and Planning Function | Automate creation of data record for project; maintain user roles; assign responsibilities for key project data to team members; intake project requirements and specifications; develop project plan with tasks, dependencies, milestones, deliverables; monitor changes/updates to project information | Failure would impact integrity of quality record but would not foreseeably compromise safety → **Not high process risk** | System capability assessment, supplier evaluation, service agreements + configuration verification and User Acceptance Testing (UAT) using exploratory unscripted testing | Intended use; risk-based analysis; summary of objectives tested and testing performed; issues found; conclusion including resolution/justification/process controls; record of who/when |
| Electronic Signature Function | Capture and store electronic signature where required; meets requirements for electronic signatures | Failure may compromise or delay compliance with regulatory requirements and SOPs but would not result in quality problem that foreseeably compromises safety → **Not high process risk** | System capability assessment, supplier evaluation, configuration + scenario testing with users | Intended use; risk-based analysis; testing performed; issues found; record of who/when; conclusion including resolution/justification/process controls |
| Access Control and Traceability Functions | Provide appropriate access control; establish user roles; maintain individual user accounts; monitor and maintain records of access and modifications to final data records; produce time-stamped reports of system access, authorization, change, and associated user for modifications to final data records | Failure has significant impact on overall intended use and system operations; may result in QMS integrity and compliance issue. Since functions intended to ensure integrity of data record for QMS requirement only — failure would not foreseeably lead to compromised safety → **Not high process risk** | System capability assessment, supplier evaluation, service agreements + configuration verification + automated test script (to exercise access controls and support verification of future changes) + UAT of reporting capabilities using exploratory unscripted testing | Intended use; risk-based analysis; summary of automated test cases and objectives tested; issues found; conclusion; record of who/when |

---

## Guidance History

| Guidance History | Date | Description |
|-----------------|------|-------------|
| Revisions to Final Guidance | February 2026 | Revisions issued under Level 2 guidance procedures (21 CFR 10.115(g)(4)), including revisions to align with the amendments to 21 CFR 820 (the Quality Management System Regulation (QMSR)). This guidance supersedes the final guidance titled "Computer Software Assurance for Production and Quality System Software," issued September 2025. |
| Level 1 Final Guidance | September 2025 | See Notice of Availability for the guidance "Computer Software Assurance for Production and Quality System Software" for more information. |
