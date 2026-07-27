# FDA Guidance: Content of Premarket Submissions for Device Software Functions

🔎 **Finding aid — NOT the authoritative source.** Distilled summary for quick orientation and early analysis. Ground and cite the authoritative full text [`source-md/sw-functions.md`](source-md/sw-functions.md); verify any quote against the byte-correct `source/` PDF before treating it as verbatim. This paraphrases and omits (appendices/worked examples are routinely dropped) — a section's absence here is never evidence the source is silent.

**Full Title**: Content of Premarket Submissions for Device Software Functions
**Document Date**: June 14, 2023
**Status**: Final
**PDF Source**: https://www.fda.gov/media/153781/download
**Issuing Bodies**: CDRH, CBER, CDER, Office of Combination Products
**Replaces**: 2005 guidance "Content of Premarket Submissions for Software Contained in Medical Devices" (May 11, 2005)

## Scope

This guidance identifies the software documentation recommended for inclusion in **premarket submissions** to evaluate the safety and effectiveness of device software functions. It applies to:

- All premarket submission types (510(k), PMA, De Novo, HDE, IDE, BLA) containing one or more device software functions
- Device constituent parts of combination products that include device software functions

It does **not** apply to:

- Software excluded under 21st Century Cures Act section 520(o) (non-device software)
- Automated manufacturing and quality system software
- Post-market software device issues
- Detailed cybersecurity documentation (deferred to the separate Cybersecurity guidance — though cybersecurity risk still informs the risk assessment and Documentation Level determination here)

The guidance does **not** prescribe how software should be developed -- only what documentation to submit. Developers are free to use any software lifecycle model or methodology.

## Key Requirements

### Documentation Levels

The 2023 guidance replaces the former three-tier "Level of Concern" (minor, moderate, major) with a simplified **two-tier system**:

#### Enhanced Documentation

Required when failure or latent flaw of **any** device software function could present a **hazardous situation with a probable risk of death or serious injury** to a patient, user, or others, assessed **prior to implementing risk control measures**.

Also generally recommended for:
- Class III devices and device constituent parts of combination products
- Blood donation testing, donor/recipient compatibility, blood cell separator, and blood establishment computer software

#### Basic Documentation

Applies when enhanced documentation does not apply. Many devices previously classified as "moderate level of concern" under the retired three-tier scheme now fall under basic.

**Key Clarifications:**
- Device class alone does not determine the level; a Class II device may be basic or enhanced depending on its risk
- Class III devices and device constituents of combination products are generally recommended for enhanced documentation
- The sponsor determines the level based on risk assessment and must provide a rationale

### Required Documentation Elements

#### 1. Documentation Level Evaluation
- Statement of chosen documentation level (basic or enhanced)
- Rationale leveraging the device's risk assessment and intended use

#### 2. Software Description
- Comprehensive overview: significant features, analyses, inputs, outputs, hardware platforms
- Curated set of questions to help prepare focused description
- For modified devices: description of changes from previous submission

#### 3. Risk Management File (Basic and Enhanced)
- **Risk Management Plan** -- approach to risk assessment, evaluation of overall residual risk vs. benefit
- **Risk Assessment** -- tabular format: hazards, hazardous situations, initial risk evaluation, risk control measures, residual risk, traceability
- **Risk Management Report** -- demonstrates plan was appropriately implemented
- Should reference FDA-recognized version of ISO 14971 and the Multiple Function Device Products guidance

#### 4. Software Requirements Specification (SRS) (Basic and Enhanced)
- Complete documentation of software requirements
- Organized format with traceability to other documentation elements
- May include: stories, use cases, textual descriptions, screen mockups, control flows
- Highlight safety-critical requirements and requirements modified since prior clearance

#### 5. System and Software Architecture Diagram (Basic and Enhanced)
- Detailed diagrams of modules, layers, interfaces
- Data inputs, outputs, and flow
- User/external product interactions (IT infrastructure, peripherals)

#### 6. Software Design Specification (SDS)
- **Basic:** Not required in submission (document in Design History File)
- **Enhanced:** Include SDS showing technical design details, how design implements SRS, and traceability from SDS to SRS

#### 7. Software Development, Configuration Management, and Maintenance Practices
**Option 1:** Declaration of Conformity to FDA-recognized IEC 62304 (specific sections for basic vs. enhanced)
**Option 2:** Without IEC 62304 conformity:
- **Basic:** Summary of SW lifecycle development, configuration/change management, maintenance processes
- **Enhanced:** Complete configuration management and maintenance plan + the summary documentation

#### 8. Software Testing (Verification and Validation)
- **Basic:** Summary of unit, integration, and system-level testing + complete system-level test protocols and reports
- **Enhanced:** Same as basic + full unit and integration level test protocols and reports
- Reference performance testing material across submission sections to reduce duplication

#### 9. Software Version History (Basic and Enhanced)
- History of tested software revisions: date, version number, brief description of changes
- Begin with the version subject to design controls (21 CFR 820.30)
- Last entry = final released version, including differences from tested version and safety/effectiveness assessment
- Does not need every revision -- focus on milestones associated with bench, animal, and clinical testing

#### 10. Unresolved Software Anomalies (Basic and Enhanced)
- List of remaining unresolved anomalies in tabular format
- For each: description, how discovered, root cause, impact on safety/effectiveness, outcome of evaluation, risk-based rationale for not fixing
- Reference: ANSI/AAMI SW91 for classification of defects

### Documentation Summary Table

| Element | Basic | Enhanced |
|---------|-------|----------|
| Documentation level statement + rationale | Required | Required |
| Software description | Required | Required |
| Risk management file (plan, assessment, report) | Required | Required |
| Software requirements specification (SRS) | Required | Required |
| System and software architecture diagram | Required | Required |
| Software design specification (SDS) | In DHF only | Required |
| SW development / config mgmt / maintenance (or IEC 62304 DoC) | Summary | Summary + complete plan |
| System-level test protocols and reports | Required | Required |
| Unit and integration test protocols and reports | Summary only | Required |
| Software version history | Required | Required |
| Unresolved software anomalies | Required | Required |

### Multi-Module / Suite Products

- Evaluate each device individually to determine documentation level
- The documentation level reflects the device as a whole -- if any software function's failure could cause death/serious injury, enhanced documentation applies to the entire submission
- Architecture diagrams should show how modules/functions interact, including shared resources, data flows, and interfaces
- Leverage the Multiple Function Device Products guidance for handling "other functions"

## Key Definitions

| Term | Definition |
|------|-----------|
| **Device Software Function** | A software function that meets the device definition under section 201(h) of the FD&C Act; aligns with 21st Century Cures Act section 520(o) |
| **Basic Documentation** | Documentation level for software where failure does not present probable risk of death or serious injury |
| **Enhanced Documentation** | Documentation level for software where failure could present a hazardous situation with probable risk of death or serious injury (assessed pre-risk controls) |
| **Software Requirements Specification (SRS)** | Complete documentation of software requirements (needs/expectations) |
| **Software Design Specification (SDS)** | Technical design details showing how design implements the SRS |
| **Design History File (DHF)** | Complete design documentation maintained per 21 CFR 820.30 |

### IEC 62304 Mapping

- The guidance was harmonized with IEC 62304 but intentional differences remain
- IEC 62304 software safety classes A, B, C do **not** map to basic/enhanced; the guidance deliberately declines to equate the two schemes, citing known differences in how device software functions are categorized
- A Declaration of Conformity to IEC 62304 can substitute for the SW development practices section
- Risk terminology harmonized with ISO 14971
- Traceability must be evidenced throughout the documentation; the guidance notes it may be presented in a separate traceability document and is maintained in the DHF

## Submission Requirements

All elements listed in the documentation summary table above are expected in premarket submissions. The level of detail depends on basic vs. enhanced classification. For 510(k) submissions involving software changes to previously cleared devices, the software description should describe changes from the previous submission.

## Cross-References

- **Multiple Function Device Products**: "Multiple Function Device Products: Policy and Considerations" -- for handling device + non-device functions
- **Clinical Decision Support**: "Clinical Decision Support Software" -- for determining if a software function is a device
- **Cybersecurity**: "Cybersecurity in Medical Devices" -- for cybersecurity-specific documentation
- **Policy for Device Software Functions**: "Policy for Device Software Functions and Mobile Medical Applications"
- **Software Changes**: "Deciding When to Submit a 510(k) for a Software Change to an Existing Device"
- **Digital Health Policy Navigator**: FDA interactive tool for determining whether a software function is a device
- **IEC 62304**: Medical device software -- Software life cycle processes
- **ISO 14971**: Risk management for medical devices
- **ANSI/AAMI SW91**: Guidance on medical device software defect classification
