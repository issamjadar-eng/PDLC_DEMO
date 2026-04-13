# FDA Guidance: Multiple Function Device Products

**Full Title**: Multiple Function Device Products: Policy and Considerations
**Document Date**: July 29, 2020 (draft issued April 27, 2018)
**Status**: Final (Contains Nonbinding Recommendations)
**PDF Source**: https://www.fda.gov/media/112671/download
**Issuing Body**: CDRH, CBER, CDER, Office of Combination Products
**Statutory Basis**: 21st Century Cures Act section 520(o)(2) of the FD&C Act
**Risk Management Alignment**: ANSI/AAMI/ISO 14971

## Scope

This guidance addresses how FDA handles products that contain multiple functions, some of which are devices (subject to FDA oversight) and some of which are not. Under the Cures Act (section 520(o)(2)):

- FDA **shall not regulate** non-device software functions as devices
- However, FDA **may assess the impact** that non-device functions have on device functions when evaluating safety and effectiveness

FDA extends this principle to **all** multiple function device products, whether functions are software-based, hardware-based, or both.

The guidance does NOT cover:
- Products where all functions are device functions under review (standard device review applies)
- How to determine whether a function is a device (see CDS guidance, Policy for Device Software Functions guidance)

## Key Requirements

### Core Terminology

| Term | Definition |
|------|-----------|
| **Device function** | Function meeting the device definition under section 201(h) of the FD&C Act |
| **"Other function"** | Function that: (a) does not meet the device definition, OR (b) meets the device definition but is not subject to premarket review (e.g., 510(k)-exempt), OR (c) meets the device definition but FDA has expressed intention not to enforce compliance |
| **Device function-under-review** | The specific device function for which FDA is conducting premarket review |
| **Multiple function device product** | Product with at least one device function and at least one "other function" |

### What FDA Reviews vs. Does Not Review

- FDA reviews the **device function-under-review** only
- "Other functions" are NOT reviewed merely because they coexist in the same product
- FDA does NOT review device functions subject to enforcement discretion policies merely because they are part of a multiple function device product
- Example: If a product has an analysis function (under review) and a trend function (enforcement discretion), FDA reviews only the analysis function

### When "Other Functions" Get Reviewed

Non-device and "other functions" are reviewed **only** when they could impact the device function-under-review:

1. **Negative impact** -- If the "other function" could adversely affect safety or effectiveness of the device function, FDA reviews the relevant aspects
2. **Labeled positive impact** -- If a positive impact is included in the device function's labeling, FDA reviews that aspect
3. **No impact** -- If the "other function" has no impact, no documentation about it is needed

### Two-Step Impact Assessment Process

**(A) Is there an impact** on safety or effectiveness of the device function as a result of the "other function"?

Consider whether the functions share:
- Computational resources (processor, memory)
- Data dependencies (input data from "other function" used in critical calculations)
- Code necessary for proper execution
- Memory or storage
- Output screen or GUI
- Programming pointers

Specific assessment questions:
- Does the "other function" provide input data for a critical calculation?
- Does the device function rely on results from the "other function"?
- Does the "other function" affect processing time when sharing a processor?
- Does the "other function" affect memory requirements when sharing memory?
- Does the device function need privileges to prevent delays from the "other function"?
- Does the "other function" directly modify configuration of the device function?

**(B) If impact exists, could it result in increased risk or adverse effect on performance** (negative impact)?

**Safety (increased risk):**
- The "other function" introduces a new hazardous situation or new cause of existing hazardous situation
- The "other function" increases severity of harm
- The "other function" serves as or impacts a risk control measure for the device function

**Effectiveness (performance):**
- Performance/clinical functionality depends on the "other function"
- The device function fails to meet specified performance level due to the "other function"

**Positive impacts:**
- Manufacturer must confirm no adverse impact if the "other function" fails to operate as intended
- Only included in premarket submission if reflected in labeling ("labeled positive impact")

**Cybersecurity considerations:**
- Assume "other functions" may be employed (maliciously or unintentionally) to adversely impact the device function
- Unavailability of device function due to cyberattack on "other function" is a risk
- SBOM aids identification of dependencies and vulnerable components

### Architectural Separation

The guidance strongly recommends architectural separation of device functions from "other functions":

- Logical separation, architectural separation, code and data partitioning should be used to the extent possible
- Higher separation leads to easier independent review of safety and effectiveness
- Higher separation means less dependency on "other functions"
- **Architecture decisions early in the design cycle** facilitate optimal separation
- When separation is not achievable, interconnections and interdependencies must be explained in the hazard analysis with appropriate risk controls
- Modular/separation architectures reduce the possibility that a cybersecurity threat to an "other function" could impact the device function

### Premarket Submission Requirements

When an "other function" could adversely impact (or has labeled positive impact on) the device function-under-review:

**A. Indications for Use:**
- Include only indications for the device function-under-review
- Do not include indications for "other functions" unless labeled positive impact

**B. Device Description:**
- Describe the device's functions
- Include description of "other functions" that could adversely impact the device function
- Address how the device function is impacted by each "other function"

**C. Labeling:**
- Description of "other functions" adequate to ensure appropriate use
- May need: contraindications, warnings, precautions, adverse reactions related to "other functions"

**D. Architecture and Design:**
- Architecture/design documents appropriate to the software level
- Adequate detail showing how/if "other functions" interact with or impact the device function
- Demonstrate independence or document shared resources

**E. Device Hazard Analysis:**
- Risk-based assessment of adverse impact or labeled positive impact of "other functions"
- Document risk mitigations
- Can use ISO 14971 or the 2005 Device Hazard Analysis approach

**F. Requirements and Specifications:**
- Adequate detail describing expected relationship, utility, reliance, or interoperability with "other functions"

**G. Performance Testing:**
- Testing considering aspects of "other functions" that impact performance
- Follow relevant regulations, guidances, and FDA-recognized consensus standards

**H. Submission Summary:**
- Must clarify the extent of FDA's assessment
- FDA provides a template statement indicating the product has functions both subject to and not subject to FDA premarket review

### Modifications to "Other Functions"

When an "other function" is modified:

1. Assess whether the modification could significantly impact safety or effectiveness of the device function
2. If adverse impact (or labeled positive impact): reference applicable guidance to determine if a new premarket submission is required
3. If only positive impact (without labeled positive impact): FDA does not intend to enforce premarket requirements
4. Document the impact assessment per the quality system

### Postmarket Requirements

- General controls apply to all device functions
- Design controls (21 CFR Part 820) apply to device functions
- Adverse event reporting (21 CFR 803.50): must investigate and report when information suggests the device function may have caused/contributed to death or serious injury
- If uncertain whether device function or "other function" caused a reportable event, still required to report
- FDA does not enforce general controls for functions under enforcement discretion

## Key Definitions

| Term | Definition |
|------|-----------|
| **Multiple function device product** | Product with at least one device function and at least one "other function" |
| **Device function** | Function meeting the device definition under section 201(h) |
| **"Other function"** | Non-device function, or device function not subject to premarket review or under enforcement discretion |
| **Device function-under-review** | The specific device function undergoing FDA premarket review |
| **Negative impact** | "Other function" adversely affects safety (increased risk) or effectiveness (performance) of device function |
| **Labeled positive impact** | Positive impact of "other function" that is reflected in the device function's labeling |

## Submission Requirements

For multiple function device products, the premarket submission should include:
- Indications for use (device function only)
- Device description covering all functions and relationships
- Architecture/design documents showing function interactions and separation
- Hazard analysis covering cross-function impacts
- Requirements documenting inter-function dependencies
- Performance testing with "other functions" present and active
- Labeling addressing "other functions" as needed
- Submission summary with FDA template statement about non-reviewed functions

## Cross-References

- **Clinical Decision Support Guidance**: "Clinical Decision Support Software" -- for determining if a software function is a device
- **Policy for Device Software Functions**: "Policy for Device Software Functions and Mobile Medical Applications"
- **Premarket Software Guidance**: "Content of Premarket Submissions for Device Software Functions"
- **Cybersecurity Guidance**: "Cybersecurity in Medical Devices" -- for cross-function cybersecurity risks
- **Device Modifications Guidances**: "Deciding When to Submit a 510(k) for a Change to an Existing Device" and software change variant
- **PMA Modifications Guidance**: "Modifications to Devices Subject to PMA"
- **ISO 14971**: Risk management for medical devices
- **21 CFR Part 820**: Quality System Regulation (design controls)
