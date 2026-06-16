# FDA Guidance: PCCP for Medical Devices (General)

🔎 **Finding aid — NOT the authoritative source.** Distilled summary for quick orientation and early analysis. Ground and cite the authoritative full text [`source-md/pccp-general.md`](source-md/pccp-general.md); verify any quote against the byte-correct `source/` PDF before treating it as verbatim. This paraphrases and omits (appendices/worked examples are routinely dropped) — a section's absence here is never evidence the source is silent.

**Full Title**: Predetermined Change Control Plans for Medical Devices
**Document Date**: August 22, 2024
**Status**: Draft -- Not for Implementation
**PDF Source**: https://www.fda.gov/media/180978/download
**Issuing Body**: CDRH, CBER (in consultation with CDER and OCP)
**Document Number**: GUI00007026

## Scope

This is the **general PCCP guidance** applicable to **all device types** -- not limited to AI/ML devices. It covers medical devices requiring PMA, 510(k), or De Novo authorization, including hardware devices, software devices, combination products, IVDs, implantables, and any other regulated medical device.

The statutory basis is **Section 515C of the FD&C Act** ("Predetermined Change Control Plans for Devices"), added by FDORA (Section 3308, enacted December 29, 2022).

A PCCP is documentation describing:
- **What modifications** will be made to a device
- **How the modifications** will be assessed (methodology to develop, validate, and implement)
- **The impact** of those modifications on safety and effectiveness

### What This Guidance Does NOT Cover

- Modifications that would NOT require a new marketing submission (handled by QSR/quality system alone)
- Complete marketing submission content requirements (refer to other guidances)
- A comprehensive list of all possible modifications for PCCPs (provides types and examples, not exhaustive)

### Applicable Pathways

- **PMA**: Original, Modular, 180-Day Supplement, 135-Day Supplement for manufacturing changes, Panel Track Supplement, Real-Time Supplement for minor changes
- **510(k)**: Traditional, Abbreviated
- **De Novo**: Original request

### Combination Products

Recommendations generally apply to the **device constituent part** of device-led combination products. Recommendations do NOT apply to the drug or biologic constituent part. Early engagement strongly encouraged.

### Relationship to AI/ML PCCP Guidance

| Aspect | This Guidance (General) | AI/ML PCCP Guidance |
|--------|------------------------|---------------------|
| **Scope** | ALL device types | Only AI/ML-enabled device software functions |
| **Purpose** | General PCCP policy, structure, and recommendations | Specific PCCP content recommendations for AI/ML modifications |
| **Relationship** | Parent/general guidance | Device-type-specific guidance for AI/ML |

Both share the same three-component PCCP structure. Upon finalization, the AI/ML PCCP guidance may be updated for consistency with this guidance.

## Key Requirements

### Five Guiding Principles

**Principle 1: Reasonable Assurance of Safety and Effectiveness.** A PCCP is part of the device marketing authorization. The totality of information must enable FDA to assess reasonable assurance of safety and effectiveness (or substantial equivalence).

**Principle 2: Least Burdensome Option.** PCCPs are intended to be a least burdensome way to implement modifications. They are optional. FDA reviews using a risk-based approach.

**Principle 3: Part of Marketing Authorization.** The manufacturer is required to implement modifications consistent with the authorized PCCP. The PCCP is referenced in the letter of authorization (title and version number).

**Principle 4: Specific.** A PCCP must include specific modifications the manufacturer intends to make -- not any/all possible modifications. Should include only a few, specific modifications that can be verified and validated. Overly broad or numerous modifications may prevent FDA determination.

**Principle 5: Harmonize with Existing Device Modifications Guidances.** PCCPs work alongside the existing Device Modifications guidances, which still apply for modifications not covered by or not consistent with the PCCP.

### PCCP Structure: Three Required Components

| Component | Purpose |
|-----------|---------|
| **Description of Modifications** | Outlines specific, planned modifications; defines specifications for characteristics and performance |
| **Modification Protocol** | Describes V&V activities, including pre-defined acceptance criteria |
| **Impact Assessment** | Identifies benefits and risks; addresses how V&V assures continued safety and effectiveness |

### Description of Modifications Content

- Enumerate each individual proposed modification
- Provide specific rationale for each change
- Reference labeling sections anticipated to be impacted
- Present at detail level permitting understanding of specific modifications
- Link each modification to a specific performance evaluation activity
- Keep to a limited number of specific, verifiable/validatable modifications

### Modification Protocol Content

**Performance Evaluation Methods:**
- Plans to V&V the modified device meets specifications for each modification
- Plans to verify unmodified specifications are not impacted
- Plans for V&V of entire device following each individual modification AND in aggregate
- Study design, performance metrics, pre-defined acceptance criteria, and statistical tests
- Reference applicable FDA guidances
- Describe how methods compare to original marketing submission methods (justify differences)
- Affirmative statement: unresolvable performance failures prevent implementation
- Root cause analysis may allow re-testing if failure is unrelated to PCCP-specific aspects

**Update Procedures:**
- How devices will be updated consistent with QSR
- Transparency to users and updated user training
- Post-market surveillance plans (real-world monitoring, notification requirements)
- How labeling will be updated
- New UDIs required for new versions/models
- Labeling must NOT include information about modifications not yet implemented

**Traceability:** A traceability table linking each modification to its performance evaluation methods and update procedures is required.

### Impact Assessment Content

1. Compare the version with each modification to the version without any modifications
2. Discuss benefits and risks (including risks of harm) of each individual modification
3. Discuss how V&V activities continue to ensure safety and effectiveness
4. Discuss interactions -- how implementation of one modification impacts another
5. Describe cumulative impact of implementing all modifications together
6. Discuss impact on overall device functionality (other software functions, hardware)
7. For combination products: impact on biologic/drug constituent parts
8. For multiple function device products: consider MFD guidance
9. Cross-reference relevant sections elsewhere in the marketing submission

### Risk-Based Assessment for 510(k)/De Novo Devices

FDA recommends a risk-based assessment process:

1. **Could the modification be a major change to the intended use?** -- If YES: generally NOT appropriate for PCCP
2. **Could the modification significantly affect safety or effectiveness?** -- If NO: not a PCCP matter (no submission needed anyway)
3. **Could the modification introduce a NEW risk?** -- If YES: generally NOT appropriate for PCCP
4. **Could the modification significantly MODIFY an existing risk?** -- If YES and risks adequately mitigated: generally MAY be appropriate

### Risk-Based Assessment for PMA Devices

1. **Could the modification be a major change to the intended use?** -- If YES: generally NOT appropriate
2. **Could the modification affect safety or effectiveness?** -- If NO: generally not appropriate
3. **Is the modification a minor change?** -- If YES: generally MAY be appropriate
4. **Is the modification a manufacturing change?** -- If YES: generally MAY be appropriate; if NO: generally NOT appropriate

### Types of Modifications Generally Appropriate for 510(k)/De Novo PCCP

- Certain design changes (dimensions, performance specs, wireless, components/accessories, patient/user interface)
- Change in sterilization, packaging, transport, or expiration dating using well-established methods
- Certain material/component changes (different raw materials, reagents, hardware components)
- Certain software changes for compatibility/interoperability (additional OS support, new data vendors/sources, additional device compatibility)
- Certain software changes consistent with intended use to improve performance
- Certain labeling changes to describe a subset of the already-indicated patient population
- Certain labeling/indications changes to specify use with additional device, component, or human genetic variant
- Certain changes in indications regarding use in the home setting

### Types of Modifications Generally NOT Appropriate for 510(k)/De Novo PCCP

- Change to control mechanism, operating principle, or energy type
- Change in design that could affect intended use
- Change from single use to reusable
- Change to or removal of contraindications
- Change from prescription to OTC
- Changes from "general to specific" indications
- Change in labeling/indications to include a new patient population
- Changes that may need new clinical data (exception: method comparison data for IVDs)
- Change to address a recall or safety issue
- Change to device constituent part impacting biologic or drug constituent part

> **Worked examples (not reproduced here).** The guidance carries **§ VIII — Examples of Modifications for PCCPs** (10 worked examples, each with "May be appropriate" / "Generally not appropriate" dispositions) and **§ IX — Sample of 510(k) Summary Information Regarding the PCCP**. Both are dropped from this finding aid — read `source-md/pccp-general.md` §§ VIII–IX for the full examples and the sample summary text.

### PCCP Deviation Policy

**What constitutes a deviation:** The PCCP is not followed or cannot be followed.

**What is NOT a deviation:** Choosing not to implement modifications, or choosing to submit a new marketing submission instead.

**Consequences:** Device generally considered adulterated and misbranded. FDA may take legal/regulatory action including seizure or injunction. Significant modifications not consistent with the PCCP likely require a new marketing submission.

### Version Control and Maintenance

- Only one version of an authorized PCCP should exist per device at any time
- Only one version should be under review at any time
- A PCCP can evolve over time through future marketing submissions
- FDA does not intend to re-review adequacy of modifications already implemented consistent with an authorized PCCP
- For PMA devices: Annual Reports must include a section describing PCCP-implemented changes
- For 510(k) devices: Predicate comparison is to the version pre-PCCP changes; subsequent clearances incorporating PCCP modifications can serve as predicates

## Key Definitions

Same core definitions as the AI/ML PCCP guidance: PCCP, Description of Modifications, Modification Protocol, Impact Assessment. The general guidance extends these to all device types, not just AI-DSFs.

## Submission Requirements

### Formatting in the Marketing Submission

- PCCP as a standalone section with title and version number
- Prominently discussed in cover letter
- Listed in table of contents as "Predetermined Change Control Plan"
- Discussed in device description, labeling, and relevant assessment sections
- Cross-referenced when PCCP content appears outside the PCCP section

### Labeling Requirements

- Statement that the device has an authorized PCCP (in most circumstances)
- As modifications are implemented: description of modifications, how they were implemented, how users will be informed
- Must NOT include information about unimplemented modifications

### Public-Facing Documents

510(k) summary, De Novo decision summary, or SSED should include: planned modifications, testing methods, validation activities and performance requirements, and means of informing users.

### Modifying a Previously Authorized PCCP

- Generally requires a new marketing submission
- Must include appropriate marketing submission requirements AND the proposed modified PCCP
- FDA recommends providing a summary of changes and tracked-changes version
- FDA focuses review on the most significantly modified aspects

## Cross-References

- **AI/ML PCCP Guidance**: "Marketing Submission Recommendations for a PCCP for AI/ML-Enabled Device Software Functions"
- **Device Modifications Guidances**: "Modifications to Devices Subject to PMA" and "Deciding When to Submit a 510(k) for a Change to an Existing Device" and "Deciding When to Submit a 510(k) for a Software Change to an Existing Device"
- **The 510(k) Program**: "Evaluating Substantial Equivalence in Premarket Notifications [510(k)]"
- **The Least Burdensome Provisions**: Concept and Principles
- **Q-Submission Program**: Requests for Feedback and Meetings
- **Benefit-Risk Determinations**: Factors to Consider When Making Benefit-Risk Determinations
- **Multiple Function Device Products**: Policy and Considerations
- **Premarket Software Guidance**: Content of Premarket Submissions for Device Software Functions
- **ISO 14971**: Risk Management for Medical Devices
- **ISO 13485**: Quality Management Systems (effective as QSR February 2, 2026)
