# FDA Guidance: PCCP for AI/ML-Enabled Device Software Functions

**Full Title**: Marketing Submission Recommendations for a Predetermined Change Control Plan for Artificial Intelligence-Enabled Device Software Functions
**Document Date**: August 18, 2025 (originally issued December 4, 2024)
**Status**: Final
**PDF Source**: https://www.fda.gov/media/166704/download
**Issuing Body**: CDRH, CBER, CDER, Office of Combination Products
**Document Number**: GUI00020049
**Statutory Authority**: Section 515C of the FD&C Act (added by FDORA, enacted December 29, 2022)

## Scope

This guidance covers Predetermined Change Control Plans (PCCPs) for **AI-Enabled Device Software Functions (AI-DSFs)** that manufacturers intend to modify over time. It addresses modifications implemented automatically (continuous learning), manually (human-in-the-loop), or a combination of both.

A PCCP covers modifications that **would otherwise require a new marketing submission** (i.e., significant changes per 21 CFR 807.81(a)(3) or changes affecting safety/effectiveness per 21 CFR 814.39(a)).

### What This Guidance Does NOT Cover

- Modifications that would not require a new marketing submission (governed by QSR/21 CFR Part 820 alone)
- Complete marketing submission content requirements for an AI-DSF (only the PCCP portion)
- Modifications to the drug or biologic constituent part of device-led combination products
- Non-AI device modifications (though Section 515C applies broadly; see General PCCP guidance)

### Applicable Submission Pathways

| Pathway | Eligible Submission Types |
|---------|--------------------------|
| **PMA** | Original PMA, Modular PMA, 180-Day PMA Supplement, Panel Track PMA Supplement, Real-Time PMA Supplement |
| **510(k)** | Traditional 510(k), Abbreviated 510(k) |
| **De Novo** | Original De Novo Request |

### Combination Products

The guidance generally applies to the **device constituent part** of device-led combination products when that part includes an AI-DSF. If an AI-DSF modification impacts the drug or biologic constituent part, early engagement with FDA is strongly encouraged.

### 510(k) Predicate Considerations

When a predicate device was authorized with a PCCP, the subject device must be compared to the **version of the predicate prior to changes made under the PCCP** (per Section 515C(c) of the FD&C Act). Once a subsequent 510(k) is cleared incorporating PCCP-implemented modifications, that cleared device may serve as a predicate.

## Key Requirements

### PCCP Structure: Three Required Components

A PCCP must contain all three of the following sections:

#### 1. Description of Modifications (Section VI)

- Enumerated list of each planned modification to the AI-DSF
- Specific rationale for each planned change
- Specifications for characteristics and performance of the planned modifications
- Statement whether modifications are implemented **automatically**, **manually**, or **combination**
- Statement whether modifications are **global** (uniform across all devices) or **local** (site/patient-specific)
- For local adaptations: description of what local factors warrant the change
- Expected frequency of updates (e.g., annually, continuously)
- References to labeling sections anticipated to be impacted
- Modifications must maintain the device within its **intended use** and **indications for use**
- Modifications must allow the device to remain substantially equivalent to predicate (for 510(k) devices)

#### 2. Modification Protocol (Section VII)

The Modification Protocol has four primary components:

**Data Management Practices:**
- Collection protocols (inclusion/exclusion criteria, intended data distribution across covariates including sex, age, race, disease conditions, acquisition conditions, prospective vs. retrospective, enrichment/stratified sampling, number and geographic distribution of sites, bias mitigation)
- Data quality assurance (consistency, completeness, authenticity, missing data handling, traceability, obsolete data removal, unauthorized access controls)
- Reference standard determination (justification of method, clinician grading protocol, handling of equivocal/missing results, uncertainty characterization)
- Test data sequestration (strategies to shield test data from development, procedures during re-training, measures to prevent bias from repeated use, descriptive statistics for each dataset)

**Re-Training Practices:**
- Objective of re-training and relationship to planned modifications
- Which parts of the AI-DSF will be modified (preprocessing, augmentation, coefficients, architecture, hyperparameters, loss functions, optimization)
- Whether re-training is needed for each part
- Triggers for re-training (data volume thresholds, drift detection, periodic schedule)
- Overfitting identification and limitation strategies
- Bias risks from re-training and planned mitigations

**Performance Evaluation:**
- Triggers to initiate evaluation (performance threshold on tuning data, test data volume, periodic)
- Assessment metrics (specific metrics, how they demonstrate safe use, comprehensive performance assessment, challenging cases)
- Statistical analysis plans (equivalent/improved performance vs. previous versions, high-risk subpopulations, sensitivity/specificity trade-offs, sample size determination, primary analysis population, reference standard variability, missing data handling)
- Performance targets (acceptance criteria, comparison to authorized version criteria, clinical justification)
- Additional testing needs (clinical usability, hardware integration, user interaction testing)
- Failure handling (unresolvable failures must be recorded and specific modifications must NOT be implemented; root cause analysis for resolvable failures)

**Update Procedures:**
- Software V&V (whether plan differs from original, integrated environment testing, impact on other device functions)
- When and how updates deploy (decision criteria, expected timeline, frequency, mechanism, verification of critical safety features post-update, global vs. local deployment, cybersecurity risk management)
- Communication and transparency (PCCP description in public summary/labeling, update communication to users, version information, option to review labeling before update, bias and performance issue disclosure)
- Device monitoring plan (adverse event tracking, real-world performance monitoring, subpopulation performance changes, response to unknown risks, strategy for unexpected performance deficiencies, misdiagnosis tracking, rollback criteria and plans)

**Traceability:** A traceability table linking each modification to its applicable protocol components is required.

#### 3. Impact Assessment (Section VIII)

- Comparison of each modification (individually) to the unmodified device version
- Discussion of benefits and risks of each modification, including risks of harm and unintended bias
- How V&V activities in the Modification Protocol ensure continued safety and effectiveness
- How implementation of one modification impacts another
- Cumulative impact of implementing all modifications
- Impact on overall device functionality (including non-AI software functions, hardware, and combination product constituents)

### Performance Criteria and Validation

**Acceptance Criteria:**
- Must be pre-defined before modifications are implemented
- Must compare the modified AI-DSF to both the original device and the last modified version
- Performance evaluation must cover the entire device, not just the AI-DSF in isolation
- Must evaluate performance across the intended use population including relevant subgroups (race, ethnicity, sex, age, disease severity)
- Statistical analysis plans must specify sample size, performance metrics, hypothesis tests, and primary analysis population

**Validation Methodology:**
- Test data must be independent of training and tuning data and generally from multiple sites
- Test data must be representative of the intended use population and environments
- If test data are used multiple times, measures must prevent unwanted bias
- More comprehensive testing supports a broader set of proposed modifications
- If acceptance criteria are not met (unresolvable failure), the modification must not be implemented

### Types of Acceptable Modifications

| Modification Type | Example |
|-------------------|---------|
| Quantitative performance improvement | Re-training to reduce false alarm rate while maintaining sensitivity within non-inferiority margin |
| Input expansion | Extending compatibility to additional hardware meeting minimum specifications |
| Subpopulation optimization | Re-training on larger dataset for a specific patient subset within original indications |
| Speed/efficiency improvement | Improving processing speed while maintaining sensitivity/specificity |

## Key Definitions

| Term | Definition |
|------|-----------|
| **Artificial Intelligence (AI)** | A machine-based system that can, for a given set of human-defined objectives, make predictions, recommendations, or decisions influencing real or virtual environments. (Per 15 U.S.C. 9401(3).) |
| **Machine Learning (ML)** | An application of AI characterized by providing systems the ability to automatically learn and improve on the basis of data or experience, without being explicitly programmed. (Per 15 U.S.C. 9401(11).) |
| **Device Software Function (DSF)** | A software function that meets the device definition in section 201(h) of the FD&C Act. Includes both SaMD and SiMD. |
| **AI-Enabled Device Software Function (AI-DSF)** | A DSF that implements an AI model. Used interchangeably with "AI-enabled device." |
| **Predetermined Change Control Plan (PCCP)** | Documentation describing what modifications will be made to a device and how they will be assessed. Includes: Description of Modifications, Modification Protocol, and Impact Assessment. |
| **Authorized PCCP** | A PCCP that has been reviewed and established through a device marketing authorization. It is a technological characteristic of the authorized device. |
| **Modification Protocol** | Documentation of methods for developing, validating, and implementing modifications. Includes V&V activities with pre-defined acceptance criteria. |
| **Impact Assessment** | Documentation assessing benefits and risks of implementing a PCCP, plus risk mitigation plans. |
| **Training Data** | Data used to build the AI model (define weights, connections, components). Must be representative of intended use populations. |
| **Tuning Data** | Data used to evaluate trained AI models across architectures/hyperparameters. Part of the training process. FDA does not use the term "validation" for this phase. |
| **Test Data** | Data used to characterize AI-DSF performance. Never shown during training. Must be independent of training/tuning data and generally from multiple sites. |

## Submission Requirements

### Formatting in the Marketing Submission

- PCCP included as a **standalone section** with title and version number
- Prominently discussed in the **cover letter**
- Listed in the marketing submission **table of contents** as "Predetermined Change Control Plan"
- Discussed in the **device description**, **labeling**, and **safety/effectiveness assessment** sections
- Described in publicly available device summaries (SSED, 510(k) summary, De Novo decision summary)

### Post-Authorization: Modifications Consistent with PCCP

- No new marketing submission required if the modification is specified in the Description of Modifications and implemented per the Modification Protocol
- Manufacturer must document the modification and analysis per quality system (21 CFR Part 820)
- Labeling must be updated as specified in the authorized PCCP
- UDI updates required for new version/model numbers (per 21 CFR 830.50)

### Post-Authorization: Deviations from PCCP

- A deviation occurs when the PCCP is not followed or cannot be followed
- Deviations could significantly affect safety or effectiveness and likely require a new marketing submission
- Deviations generally render the device adulterated and misbranded
- FDA may take enforcement action (seizure, injunction)

### Post-Authorization: Modifications Outside the PCCP

- Must be evaluated under standard Device Modifications guidance
- If significant, a new marketing submission is required
- The submission must include a summary of all prior modifications implemented under the PCCP

### PMA-Specific Reporting

- Modifications not requiring a marketing submission must be reported in post-approval periodic reports (per 21 CFR 814.39(b) and 814.82(a)(7))

### Public Transparency

Public-facing documents should include planned modifications, testing methods, validation activities and performance requirements, and means by which users will be informed.

### Quality System Requirements

- QMS compliance with 21 CFR Part 820 / ISO 13485:2016
- Design control procedures for PCCP modifications (21 CFR 820.30)
- Change management processes for PCCP implementation
- Document and record retention (minimum 2 years from commercial release)
- CAPA procedures applicable to PCCP deviations (21 CFR 820.90, 820.100)
- QSR transition: FDA final rule (February 2, 2024) aligning 21 CFR Part 820 with ISO 13485:2016, effective February 2, 2026

### Labeling Requirements

- Labeling must disclose the authorized PCCP
- Must describe implemented modifications and current device performance
- Must describe how modifications were implemented and how users will be informed
- Must NOT include information about modifications not yet implemented (would be misleading)
- Version information and release notes recommended as communication mechanisms

## Cross-References

- **General PCCP Guidance**: "Predetermined Change Control Plans for Medical Devices" (Draft, August 2024) -- general framework for all device types
- **AI Lifecycle Guidance**: "Artificial Intelligence-Enabled Device Software Functions: Lifecycle Management and Marketing Submission Recommendations" (Draft, January 2025) -- full submission content for AI-enabled devices
- **Device Modifications Guidances**: "Deciding When to Submit a 510(k) for a Change to an Existing Device" and "Deciding When to Submit a 510(k) for a Software Change to an Existing Device"
- **Q-Submission Program**: "Requests for Feedback and Meetings for Medical Device Submissions: The Q-Submission Program"
- **Multiple Function Device Products**: "Multiple Function Device Products: Policy and Considerations"
- **ISO 14971**: Risk Management for Medical Devices
- **ISO 13485**: Quality Management Systems (effective as QSR reference February 2, 2026)
