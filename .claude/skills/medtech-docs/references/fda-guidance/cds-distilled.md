# FDA Guidance: Clinical Decision Support Software

🔎 **Finding aid — NOT the authoritative source.** Distilled summary for quick orientation and early analysis. Ground and cite the authoritative full text [`source-md/cds.md`](source-md/cds.md); verify any quote against the byte-correct `source/` PDF before treating it as verbatim. This paraphrases and omits (appendices/worked examples are routinely dropped) — a section's absence here is never evidence the source is silent.

**Full Title**: Clinical Decision Support Software
**Document Date**: January 6, 2026; re-issued January 29, 2026
**Status**: Final
**PDF Source**: https://www.fda.gov/media/191560/download
**Issuing Body**: CDRH Digital Health Center of Excellence
**Docket**: FDA-2017-D-6569
**Statutory Basis**: 21st Century Cures Act (December 2016), amending FD&C Act section 520(o)(1)(E)

## Scope

This guidance clarifies FDA's interpretation of the four statutory criteria under the 21st Century Cures Act that must **all** be met for a clinical decision support (CDS) software function to be considered a **non-device** (not regulated as a medical device).

The 21st Century Cures Act amended the FD&C Act to exclude certain software functions from the device definition (section 520(o)). Five categories of software functions are excluded, including CDS. This guidance addresses only the CDS exemption criteria.

Software that meets all four criteria is **not a device** and is not subject to FDA device regulation. Software that fails any criterion is a **device** (potentially SaMD) and must comply with applicable device requirements.

## Key Requirements

### The Four CDS Exemption Criteria

All four must be met for non-device status:

#### Criterion 1: Not Acquire, Process, or Analyze Certain Data Types

The software function must **not** acquire, process, or analyze:
- **Medical images**
- **Signals from an IVD** (in vitro diagnostic device)
- **Patterns or signals from a signal acquisition system**

**Key definitions:**
- **Signal acquisition system**: A system that measures a parameter from within, attached to, or external to the body for a medical purpose (continuous, near-continuous, or streaming measurement)
- **Pattern**: Multiple, sequential, or repeated measurements of a signal or from a signal acquisition system
- **Not a pattern**: Discrete, episodic, or intermittent point-in-time physiological measurements (e.g., routine vital signs at discrete clinical encounters) generally do not constitute a pattern

**Critical interpretation**: Software that assesses or interprets the clinical implications of a signal, pattern, or medical image fails criterion 1. Any software that directly analyzes X-rays, CT scans, MRI, ultrasound, ECG waveforms, or similar data is a device regardless of whether it meets criteria 2-4.

#### Criterion 2: Display, Analyze, or Print Medical Information

The software must be intended to display, analyze, or print **medical information** about a patient or other medical information.

**Medical information includes:**
- Patient-specific information: demographics, symptoms, certain test results, discharge summaries
- Other medical information: clinical practice guidelines, peer-reviewed studies, textbooks, approved drug/device labeling, government agency recommendations

Medical information is the type of information used in or relating to clinical care, supported by **well-understood and accepted sources** and can be appropriately understood in context.

#### Criterion 3: Supporting or Providing Recommendations to an HCP

The software must be intended for **supporting or providing recommendations** to a healthcare provider (HCP) about prevention, diagnosis, or treatment.

FDA interpretation: The software provides condition-, disease-, or patient-specific information and options to enhance, inform, and/or influence a healthcare decision, but:
- Does **not** provide a specific preventive, diagnostic, or treatment **output or directive**
- Is **not** intended to replace the HCP's judgment

**Acceptable outputs:**
- A list of preventive, diagnostic, or treatment options
- A prioritized list of such options
- A list of follow-up or next-step options for the HCP to consider

**Enforcement Discretion Policy (new in 2026 update):** If a software function fails criterion 3 because it provides a specific output/directive, but **only one clinically appropriate recommendation exists** and the software otherwise meets all other criteria, FDA intends to exercise enforcement discretion (not enforce device requirements). This also applies to software providing a single risk score as output where a single score is clinically appropriate.

#### Criterion 4: Enabling Independent Review by the HCP

The software must enable an HCP to **independently review the basis** for recommendations so the HCP does **not rely primarily** on such recommendations.

**FDA considerations:**
- **Level of automation** -- higher automation increases risk of automation bias
- **Time-critical nature** of decision-making (moved from criterion 3 to criterion 4 in this update) -- insufficient time for independent review undermines this criterion
- **Automation bias** -- propensity to over-rely on automated suggestions; increases in urgent situations

**Software/labeling recommendations to satisfy criterion 4:**
- Provide adequate background information about underlying sources in plain language
- Present information to promote usability and avoid information overload
- Prioritize the most decision-relevant information
- Make additional detail available as appropriate

Usability testing may be requested by FDA if there is a question about whether criterion 4 is satisfied.

### How Specific Data Types Affect Classification

#### Imaging-Based Software = Device
Any software that acquires, processes, or analyzes medical images fails criterion 1 and is a device (SaMD), regardless of criteria 2-4. This includes:
- Software analyzing X-rays, CT, MRI, PET, ultrasound for any clinical purpose
- Software measuring anatomical structures from images
- Software segmenting or annotating images

#### Software Using HCP-Reported Findings = Potentially Non-Device CDS
If software analyzes a radiologist's or HCP's **reported clinical findings** (not the image itself) and meets all four criteria, it may be non-device CDS.

#### Continuous/Streaming Monitoring = Device
Software analyzing continuous, near-continuous, or streaming physiological measurements (from wearables, continuous monitors) fails criterion 1. Examples: hourly pulse oximetry analysis, continuous glucose monitor data analysis, wearable heart rate/SpO2/BP analysis.

#### Discrete/Episodic Measurements = Potentially Non-Device CDS
Discrete, episodic, or intermittent point-in-time physiological measurements generally do not constitute a pattern. Software analyzing such data may qualify as non-device CDS if all four criteria are met.

#### Time-Critical Outputs = Device
Software providing time-critical diagnostic outputs (alerts for life-threatening conditions like stroke, sepsis) fails criteria 3 and 4.

### Enforcement Discretion Examples

| Example | Status | Rationale |
|---------|--------|-----------|
| Cardiovascular risk prediction (weight, smoking, BP, BNP) | Enforcement discretion | One clinically appropriate output |
| Same function using variant genomic data without established relevance | Device | Fails criteria 1 and 2 |
| Same function predicting risk in next 24 hours | Device | Fails criterion 4 (time-critical) |
| Treatment plan for cognitive impairment (HCP reviews/finalizes) | Enforcement discretion | One appropriate plan |
| Same function analyzing PET scan images | Device | Fails criterion 1 |
| Antibiotic recommendation based on symptoms/history | Enforcement discretion | One appropriate recommendation |
| Same function analyzing spectroscopy data | Device | Fails criterion 1 |
| Radiology report summary from radiologist's findings | Enforcement discretion | Does not analyze image itself |
| Same function that also analyzes the image | Device | Fails criterion 1 |
| Differential diagnosis from symptoms/vitals/labs | Enforcement discretion | Single recommendation when alternatives highly improbable |
| Same function establishing definitive diagnosis from images/waveforms | Device | Fails criterion 1 |
| Chronic low back pain care pathway classification | Enforcement discretion | Based on history, symptoms, clinical findings |
| Same function for acute trauma requiring immediate intervention | Device | Fails criterion 4 (time-critical) |

### LLMs and CDS

An LLM-enabled software function may meet criterion 4 if it can sufficiently enable an HCP to independently review the basis for recommendations. No specific LLM evaluation framework has been provided.

### 513(g) for Device Determination

For software where CDS status is uncertain, FDA recommends submitting a 513(g) request for device determination, or using a Q-Submission to discuss with FDA.

## Key Definitions

| Term | Definition |
|------|-----------|
| **Clinical Decision Support (CDS)** | Software intended to support or provide recommendations to an HCP about prevention, diagnosis, or treatment |
| **Non-device CDS** | CDS software meeting all four criteria under section 520(o)(1)(E), excluded from device definition |
| **Device CDS / SaMD** | CDS software failing one or more criteria, regulated as a medical device |
| **Medical information** | Information used in or relating to clinical care, supported by well-understood and accepted sources |
| **Signal acquisition system** | System measuring a parameter from/attached to/external to the body for a medical purpose |
| **Pattern** | Multiple, sequential, or repeated measurements from a signal acquisition system |
| **Automation bias** | Propensity of humans to over-rely on automated suggestions |
| **Enforcement discretion** | FDA policy to not enforce device requirements for software meeting specified conditions |

## Submission Requirements

Software that fails any of the four criteria is a device and must comply with applicable premarket submission requirements. The relevant submission pathway depends on the device classification (typically 510(k) for Class II, De Novo if no predicate exists).

For software where CDS status is uncertain:
- 513(g) request for device determination
- Q-Submission to discuss classification with FDA

## Cross-References

- **Premarket Software Guidance**: "Content of Premarket Submissions for Device Software Functions" -- documentation requirements for device software
- **Multiple Function Device Products**: "Multiple Function Device Products: Policy and Considerations" -- for products with mixed device and non-device functions
- **Policy for Device Software Functions**: "Policy for Device Software Functions and Mobile Medical Applications"
- **Q-Submission Program**: For discussing classification questions with FDA
- **513(g) Guidance**: For formal device classification requests
- **21st Century Cures Act**: Section 520(o) of the FD&C Act -- statutory basis for CDS exemption
