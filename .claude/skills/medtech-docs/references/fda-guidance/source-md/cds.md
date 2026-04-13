# Clinical Decision Support Software — Final Guidance

## Metadata

| Field | Value |
|-------|-------|
| **Full Title** | Clinical Decision Support Software |
| **Document Type** | Final Guidance |
| **Document Date** | January 6, 2026 (re-issued January 29, 2026) |
| **Town Hall Date** | March 11, 2026 |
| **Docket Number** | FDA-2017-D-6569 |
| **Center** | CDRH (Center for Devices and Radiological Health) |
| **Contact** | DigitalHealth@fda.hhs.gov |
| **Presenters** | Danielle Faruq (Digital Health Specialist, Division of Digital Health Policy); Aneesh Deoras (Acting Division Director, Division of Digital Health Technology Assessment) |
| **Moderator** | CAPT Kim Piermatteo, Division of Industry and Consumer Education |

---

*This document is a transcript of the CDRH Town Hall held on March 11, 2026, discussing the updated final guidance on Clinical Decision Support Software issued January 6, 2026 and re-issued January 29, 2026.*

---

## Introduction

CAPT Kim Piermatteo: Hello and welcome to this CDRH town hall. This is CAPT Kim Piermatteo of the United States Public Health Service, and I serve as the Education Program Administrator in the Division of Industry and Consumer Education within FDA's Center for Devices and Radiological Health. I'll be the moderator for today's event.

Today we will be discussing the update to the final guidance titled, Clinical Decision Support Software, issued on January 6, 2026 and re-issued on January 29, 2026. This guidance clarifies the FDA's thinking on the types of clinical decision support, or CDS, software functions that are excluded from the definition of a device by the criteria in section 520(o)(1)(E) of the Food, Drug and Cosmetic Act.

I'd now like to introduce our presenters from CDRH's Digital Health Center of Excellence, Danielle Faruq, Digital Health Specialist in the Division of Digital Health Policy, and Aneesh Deoras, Acting Division Director in the Division of Digital Health Technology Assessment.

We'll begin with a presentation from Danielle and Aneesh and then discuss some frequently asked questions regarding this final guidance.

Before I turn it over to Danielle to get us started, I'd like to remind everyone, the intended audience for this event is industry. National media and press members are encouraged to submit their questions through the FDA Newsroom at www.fda.gov/news-events/fda-newsroom.

Thank you all again for joining us. I'll now turn it over to Danielle.

## Learning Objectives

Danielle Faruq: Thank you Kim and thanks everyone for joining us today to learn more about the Clinical Decision Support Software final guidance.

This guidance document is available online on FDA's website as well as on regulations.gov under docket number FDA-2017-D-6569.

Our learning objectives today include:

1. Briefly describing the 21st Century Cures Act and the history of the Clinical Decision Support Software final guidance
2. Explaining FDA's current thinking on clinical decision support, or CDS, including clarification on our interpretation of the criteria in section 520(o)(1)(E) of the Food, Drug and Cosmetic Act, or FD&C Act, for non-device CDS software functions
3. Describing FDA's Enforcement Discretion Policy for software functions that provide one clinically appropriate output and otherwise meet all other criteria in section 520(o)(1)(E) and giving examples of such functions
4. Giving examples of non-device CDS software functions and CDS software functions that meet the device definition

## Learning Objective 1: 21st Century Cures Act and CDS History

Danielle Faruq: As a reminder, in December 2016, the 21st Century Cures Act amended the definition of device in the FD&C Act to exclude certain software functions from the device definition. These software functions are described in section 520(o) of the FD&C Act and include five different categories of software functions, including clinical decision support.

The Clinical Decision Support Software guidance itself has gone through several iterations since the 21st Century Cures Act amended the device definition to exclude certain clinical decision support software functions from the device definition. Most recently, in January 2026, FDA issued a final guidance with updates, which are the topic of today's program.

## Learning Objective 2: FDA's Current Thinking on CDS Criteria

### The Four Criteria for Non-Device CDS

The four criteria that must be met for a software function to be considered non-device CDS software describe the types of CDS that are not regulated as devices. It is important to note that these statutory criteria have not changed as part of updates to the guidance.

### Criterion 1: No Analysis of Medical Images, IVD Signals, or Patterns

Non-device CDS software functions do not acquire, process, or analyze medical images or signals from an in vitro diagnostic device, or IVD, or patterns or signals from a signal acquisition system. In the final guidance update, FDA clarified the interpretation of the terms "signal acquisition system" and "pattern."

- **Signal acquisition system**: A system that measures a parameter from within, attached to, or external to the body for a medical purpose, for example, through continuous, near-continuous, or otherwise streaming measurement.
- **Pattern**: Multiple, sequential, or repeated, measurements of a signal or from a signal acquisition system. The updated final guidance clarified that, by contrast, discrete, episodic, or intermittent point-in-time physiological measurements, for example, routine vital signs obtained at discrete clinical encounters, generally do not, by themselves, constitute a pattern.

FDA considers software functions that assess or interpret the clinical implications or relevance of a signal, pattern, or medical image to be software functions that do not meet criterion one. For example, a software function that's processing or analyzing an ECG waveform or QRS complex, which can be a continuous, near-continuous, or otherwise streaming measurement, and measuring repeated complexes or detecting heart rate arrhythmias, are the kinds of signal processing and analyzing that do not meet criterion one.

### Criterion 2: Displays, Analyzes, or Prints Medical Information

Non-device CDS functions are intended to display, analyze, or print medical information about a patient or other medical information. In other words, if medical information is used as an input, then the software function is not a device so long as it meets the other three criteria.

Such medical information includes:

- **Patient-specific information**: demographic information, symptoms, certain test results, or patient discharge summaries
- **Other medical information**: clinical practice guidelines, peer-reviewed clinical studies, textbooks, approved drug or medical device labeling, and government agency recommendations

In the final guidance, FDA clarified how it interprets the term "medical information." Medical information is the type of information used in, or that relates to, the clinical care of the patient, including patient-specific information. It may generally be communicated between healthcare providers, or HCPs, in a clinical conversation or between HCPs and patients in the context of a clinical decision. However, whether particular information is commonly discussed in a clinical conversation is not, by itself, determinative of whether it is "medical information about a patient" under criterion two, provided the information's relevance to patient care is supported by well-understood and accepted sources and can be appropriately understood in context.

### Criterion 3: Supports or Provides Recommendations to an HCP

Software functions must be intended for the purpose of supporting or providing recommendations to an HCP about prevention, diagnosis, or treatment of a disease or condition.

FDA interprets criterion three to refer to software that is intended for an HCP and that provides condition, disease, or patient-specific information and options to an HCP to enhance, inform, and/or influence a health care decision, but does not provide a specific preventive, diagnostic, or treatment output or directive and is not intended to replace the HCP's judgement.

Software functions that provide the following outputs would meet criterion three, as long as they were not intended to replace or direct the HCP's judgment:

- A list of preventive, diagnostic, or treatment options to the HCP
- A prioritized list of preventive, diagnostic, or treatment options to the HCP
- A list of follow-up or next-step options for the HCP to consider

While the interpretation that software that is not intended to support time-critical decision-making has been removed from criterion three, it is still a consideration when deciding whether a software function meets criterion four.

As part of the updates in this final guidance, FDA communicates an enforcement discretion policy for software functions that fail criterion three because they provide a specific preventive, diagnostic, or treatment output or directive, but for which only one clinically appropriate recommendation exists and the software otherwise meets all criteria under section 520(o)(1)(E). FDA intends to exercise enforcement discretion meaning that FDA does not intend to enforce requirements under the FD&C Act for such functions.

### Criterion 4: Enables HCP Independent Review

Software functions must be intended for the purpose of enabling an HCP to independently review the basis for the recommendations that such software presents so that the HCP does not rely primarily on any of such recommendations to make a clinical diagnosis or treatment decision regarding an individual patient.

#### Recommendations for Satisfying Criterion 4

Sponsors may use alternative approaches as long as the approach enables an HCP to independently review the basis for the recommendations so that they don't rely primarily on such recommendations.

These recommendations have not fundamentally changed as part of the updates, though the guidance now communicates additional recommendations:

- The software or associated labeling should provide adequate background information about underlying sources in plain language
- Information that enables an HCP to independently review the basis of provided recommendations from the software should be presented in a manner that promotes usability and avoids information overload, including prioritizing the most decision-relevant information and making additional detail available as appropriate

FDA also clarified that, in determining whether a software function meets criterion four, FDA considers both the level of automation and time-critical nature of the HCP's decision making when determining whether a software function allows an HCP to independently review the basis for the recommendations presented by the software so that they do not rely primarily on such recommendations.

The time-critical nature of the HCP's decision making is now only a consideration for criterion four (removed from criterion three).

The updated final guidance also clarifies that **automation bias** is the propensity of humans to over-rely on a suggestion from an automated system. In the context of CDS, automation bias can result in errors of commission (following incorrect advice) or omission (failing to act because of not being prompted to do so).

In situations that require urgent action, automation bias increases because there is not sufficient time for the user to adequately consider other information. This understanding of automation bias informs FDA's interpretation that non-device CDS software functions allow an HCP to independently review the basis for the recommendations presented by the software so that they do not rely primarily on such recommendations.

## Learning Objective 3: Enforcement Discretion Policy

As a reminder, FDA interprets criterion three to refer to software that provides condition-, disease-, and/or patient-specific recommendations to an HCP to enhance, inform and/or influence a health care decision but is not intended to replace or direct the HCP's judgment. In cases where a software function provides a specific preventive, diagnostic or treatment output or directive, the software function fails criterion three because it is not intended for the purpose of supporting or providing recommendations under section 520(o)(1)(E)(ii).

If only one recommendation is clinically appropriate and the software function otherwise meets all criteria under section 520(o)(1)(E), FDA intends to exercise enforcement discretion, meaning that FDA does not intend to enforce requirements under the FD&C Act, for such functions.

### Enforcement Discretion Examples

#### Example 1: Cardiovascular Risk Prediction

A software function that predicts risk of future cardiovascular events for an HCP to consider based on a patient's weight, current and historical smoking status, blood pressure, and brain natriuretic peptide (BNP) IVD test results. Assuming that this software function meets all criteria except for criterion three, and has one clinically appropriate output, it is a software function for which FDA intends to exercise enforcement discretion.

**However:**

- A software function with the same functionality, but also utilizes variant genomic data as an input that does not have an established relevance to the diagnostic recommendation, would not fall under this example because it fails criterion one and two. Such a software function is a device software function that would remain the focus of FDA's oversight.
- A software function with the same functionality, but predicts risk of a cardiovascular event in the next 24 hours, would not fall under this example because it fails criterion four. Such a software function is also a device software function that would remain the focus of FDA's oversight.

#### Example 2: Cognitive Impairment Treatment Plan

A software function that creates a recommended treatment plan, including possible medications, for patients diagnosed with cognitive impairment for an HCP to consider based on the patient's diagnosis related to cognitive impairment as well as potential comorbidities, age, sex, and patient preferences, and that should be reviewed, revised, and finalized by an HCP. Assuming this software function meets all criteria except for criterion three and has one clinically appropriate output, it is a software function for which FDA intends to exercise enforcement discretion.

**However:** A software function with the same functionality, but also analyzes positron emission tomography (PET) scan images, would not fall under this example because it fails criterion one. Such a software function is a device software function that would remain the focus of FDA's oversight.

#### Example 3: Antibiotic Recommendation

A software function that recommends a specific FDA-approved antibiotic agent for an HCP to consider based on the patient's symptoms, recent hospitalizations, and previous antibiotic exposure. Assuming this software function meets all criteria except for criterion three and has one clinically appropriate output, it is a software function for which FDA intends to exercise enforcement discretion.

**However:** A software function with the same functionality, but also analyzes spectroscopy data to diagnose bacterial infections, would not fall under this example because it fails criterion one. Such a software function is a device software function that would remain the focus of FDA's oversight.

#### Example 4: Radiology Report Summary

A software function that analyzes a radiologist's clinical findings of an image to generate a proposed summary of the clinical findings for a patient's radiology or pathology report, including a specific diagnostic recommendation based on clinical guidelines that should be reviewed, revised, and finalized by an HCP. This software function meets all criteria except for criterion three and has one clinically appropriate output. Therefore, it is a software function for which FDA intends to exercise enforcement discretion.

**However:**

- A software function with the same functionality, but also analyzes the image to generate the clinical findings and/or make measurements, would not fall under this example because it fails criterion one. Such a software function is a device software function that would remain the focus of FDA's oversight.
- A software function with the same functionality, but utilizes information that cannot be verified and validated to be from well-understood and accepted sources to generate a specific diagnostic recommendation, would not fall under this example because it fails criterion two. Such a software function is a device software function that would remain the focus of FDA's oversight.

#### Example 5: Differential Diagnosis

A software function that provides an HCP with a differential diagnosis based on a patient's symptoms, vital signs, and laboratory values, and that, depending on the clinical context, may present either multiple diagnostic considerations or a single clinically appropriate diagnostic recommendation when alternative diagnoses are highly improbable. The output is intended to support clinical reasoning and to be reviewed, revised, and finalized by the HCP. This software function meets all criteria except for criterion three and has one clinically appropriate output. Therefore, it is a software function for which FDA intends to exercise enforcement discretion.

**However:** A software function that establishes a definitive diagnosis based on an analysis of medical images, waveform data, or other signal-level inputs would not fall under this example because it fails criterion one and because it directs an HCP's judgement instead of recommending a differential diagnosis. Such a software function is a device software function that would remain the focus of FDA's oversight.

#### Example 6: Chronic Low Back Pain Care Pathway

A software function that classifies patients with chronic low back pain into a single recommended appropriate clinical care pathway, for example, conservative management or referral to a surgical spine specialist, based on patient history, symptom duration, and documented clinical findings, where the recommendation is intended to be reviewed and acted upon by an HCP. This software function meets all criteria except for criterion three and has one clinically appropriate output. Therefore, it is a software function for which FDA intends to exercise enforcement discretion.

**However:** A software function that provides care pathway recommendations for patients with acute back pain due to trauma or other emergent conditions, where immediate clinical intervention may be required, would not fall under this example because it fails criterion four. Such a software function is a device software function that would remain the focus of FDA's oversight.

## Learning Objective 4: Examples of Non-Device and Device CDS

### Non-Device CDS Example

Example number 12 in section V.A. of the guidance: A software function that identifies to an HCP that a patient, consistent with the current version of FDA-approved drug labeling, is within specific indicated population for an FDA-approved chemotherapeutic agent based on analysis of patient specific medical information, such as patient diagnosis and pathologist confirmed biopsy results. This example meets criterion one, two and three and is non-device CDS, provided that it also meets criterion four.

### Device Software Function Examples

The following examples are functions that meet the definition of a device and do not meet all four criteria. If an example does not include a statement reflecting that the software function fails a specific criterion, then for the purposes of the example, it can be assumed that the criterion is satisfied. Where criterion three is referenced, if only one option is clinically appropriate and the software function otherwise meets all criteria under section 520(o)(1)(E), then FDA intends to exercise enforcement discretion.

**Example 4: Wearable Signal Analysis for Heart Attack or Narcolepsy** — A software function that analyzes multiple signals (e.g., perspiration rate, heart rate, eye movement, breathing rate) from wearable products to monitor whether a person is having a heart attack or narcolepsy episode. This is a device function. It does not meet criterion one (analyzes signals), criterion two (not intended to display, analyze, or print medical information), or criterion three or four (provides a specific diagnostic output and supports time-critical decision making).

**Example 5: Near-Infrared Camera for Brain Hematoma** — A software function that analyzes near-infrared camera images of a patient intended for use in determining or diagnosing a brain hematoma. This is a device function. It does not meet criterion one (analyzes a signal) or criterion two (not intended to display, analyze, or print medical information).

**Example 9: C-Section Timing** — A software function that analyzes signals from a trans-abdominal electromyography device, a fetal heart rate monitor, and an intrauterine pressure catheter to determine timing of a C-section intervention for an "at term" pregnant woman. This is a device function. It does not meet criterion one (analyzes a medical signal), criterion two (not intended to display, analyze, or print medical information), or criterion three or four (provides a specific, time-critical treatment output or directive).

**Example 11: Life-Threatening Condition Detection** — A software function that analyzes patient-specific medical information to detect a life-threatening condition, such as stroke or sepsis, and generate an alarm or an alert to notify an HCP. This is a device function. It does not meet criterion three or four (intended to provide a specific diagnostic output or directive, including an alarm which supports time-critical decision-making).

**Example 22: Myocardial Ischemia Detection** — A software function that analyzes patient-specific measurements (e.g., ST-segment elevation or depression as reported on an ECG report and cardiac enzyme laboratory results from the electronic health record) to identify patients potentially experiencing myocardial ischemia or infarction. This is a device function. It does not meet criterion three or four (provides a specific diagnostic output or directive and supports time-critical decision-making).

**Example 23: Heart Failure Hospitalization Prediction** — A software function intended for HCP management of heart failure patients that analyzes patient-specific medical information (e.g., daily heart rate, SpO2, blood pressure, or other output from wearable product) to predict heart failure hospitalization. This is a device function. It does not meet criterion three or four (provides a specific diagnostic output or directive and supports time-critical decision making).

**Example 24: Patient Deterioration Detection** — A software function that analyzes hourly pulse oximetry and heart rate measurements (e.g., from a patient's electronic health record) to identify signs of patient deterioration and alert an HCP. This is a device function. It does not meet criterion one (analyzes a pattern), criterion two (not intended to display, analyze, or print medical information), or criterion three or four (provides a specific diagnostic output or directive and supports time-critical decision making).

**Example 25: Hypoglycemia Detection from CGM** — A software function that analyzes glucose measurement outputs from a continuous glucose monitor every 30 minutes to detect periods of potential hypoglycemia and notify the patient's HCP. This is a device function. It does not meet criterion one (analyzes a pattern), criterion two (not intended to display, analyze, or print medical information), or criterion three or four (provides a specific diagnostic output or directive and supports time-critical decision making).

**Example 26: Stroke Drug Therapy Recommendation** — A software function that analyzes a radiologist's score/report of regional contrast discrepancies measured from a head CT of a suspected stroke patient to identify whether the HCP should initiate a specific drug therapy based on a scoring algorithm. This is a device function. It does not meet criterion three or four (provides a specific treatment output or directive and supports time-critical decision making).

**Example 27: Stroke Triage** — A software function that analyzes the radiologist's reported imaging findings and other patient-specific medical information taken by an HCP upon admission as input to a stroke triage algorithm that indicates whether to transfer the patient to a major stroke center for an intervention. This is a device function. It does not meet criterion three or four (provides a specific, time-critical diagnostic or treatment output or directive).

**Example 28: Insulin Dose Calculator** — A software function that helps a diabetic patient manage their blood sugars by calculating bolus insulin dose based on carbohydrate intake, pre-meal blood glucose, and anticipated physical activity reported to adjust carbohydrate ratio and basal insulin. This is a device function. It does not meet criterion three (not intended for an HCP) or criterion four (supports time-critical decision-making).

**Example 29: Digoxin Toxicity Assessment** — A software function that analyzes a patient's symptoms, prior diagnosis, and serum digoxin level from the medical record to assess a patient's likelihood for digoxin toxicity and indicates that treatment with digoxin immune antigen binding fragments (digibind) for those at high risk. This is a device function. It does not meet criterion three or four (provides a specific diagnostic or treatment output or directive and supports time-critical decision-making).

For questions about how to use the guidance or the non-device CDS criteria, please reach out to DigitalHealth@fda.hhs.gov. You may also consider submitting a 513(g) for device determination or Q-Submission to talk with FDA about how to apply the criteria.

## Summary

Topics covered in this town hall:

- Briefly explained the 21st Century Cures Act and history of the Clinical Decision Support guidance
- Explained FDA's current thinking on clinical decision support or CDS, including clarification on interpretation of the statutory criteria
- Described FDA's Enforcement Discretion Policy for software functions that provide one clinically appropriate output and examples
- Reviewed examples of non-device CDS software functions and CDS software functions that meet the device definition

## Frequently Asked Questions

### Q: Would a voice analysis software function for mental health recommendations be non-device CDS?

Would a software function that analyzes voice characteristics in a short recording to make recommendations to the healthcare provider, or HCP, about the prevention, diagnosis, or treatment of mental health diseases or conditions, based on recommendations that were validated in a peer-reviewed published clinical study, meet all four criteria and therefore be non-device CDS?

**A:** Similar to the product in example 14 in section V.C. of the guidance, this software function would likely fail criterion one because it analyzes a signal or pattern and would likely fail criterion two because it is not intended to display, analyze, or print medical information. Therefore, it likely would not meet all four criteria to be non-device CDS.

### Q: How does criterion four relate to large language models?

**A:** Criterion four states that a non-device CDS software function is intended for the purpose of enabling an HCP to independently review the basis for the recommendations that such software presents so that it is not the intent that the HCP rely primarily on any of such recommendations to make a clinical diagnosis or treatment decision regarding an individual patient. A large language model- or, LLM-enabled software function may meet this criterion if it can sufficiently enable an HCP to independently review the basis for the recommendations. The guidance includes software and labeling recommendations for sponsors to consider to enable independent review.

### Q: How would software embedded in a diagnostic ultrasound be considered?

How would a software function embedded in a diagnostic ultrasound medical device that is administered by a patient under medical oversight, be considered by the FDA under the policies in this guidance?

**A:** If this software function is intended to support or provide recommendations to a patient, it would fail criterion three and would not be non-device CDS.

### Q: Would an alarm or alert generating software function be non-device CDS?

**A:** Section 520(o)(1) of the FD&C Act does not explicitly carve out software functions intended to generate alarms or alerts or prioritize patient-related information from the device definition. However, alerts that inform the user of recommendations that meet all the criteria in section 520(o)(1)(E) may be considered non-device CDS. In evaluating whether an alert may be non-device CDS, FDA recommends referring to the interpretation of criterion four, and specifically whether the time-critical nature of the recommendation provides sufficient time for the HCP to consider the basis of the recommendation.

### Q: Does the acute care context make predictive CDS more likely a device?

In acute care, does the context itself make predictive or screening CDS more likely to be considered a device, even if the software provides transparent risk information and does not recommend a specific intervention? If so, what factors drive that determination?

**A:** The acute care context alone does not necessarily mean that a software function meets the definition of a device. If the software function meets all four criteria, it is non-device CDS. For this scenario, FDA recommends referring to the interpretation of criterion four, and specifically the time-critical nature of the HCP's decision making when determining whether a software function allows an HCP to independently review the basis for the recommendation presented by the software so that they do not rely primarily on such recommendations.

### Q: Is a single risk score a non-device under criterion three, or subject to enforcement discretion?

**A:** A CDS software function that provides a single risk score as an output, and meets all other criteria, is a software function for which FDA intends to exercise enforcement discretion where providing a single risk score is clinically appropriate.

### Q: Would risk scores for hospitalized patients be more likely a device?

Would software that provides risk scores for hospitalized patients, including intensive care unit patients, be more likely considered a device, even if the score does not address a life-threatening condition, and it is not intended to drive time-critical decisions?

**A:** The indicated population alone does not entirely dictate whether a software function meets the definition of device. In the context of CDS, if a software function meets all four criteria, it is non-device CDS. If a software function has one clinically appropriate output, meaning it fails criterion three, but otherwise meets the other criteria, it is a software function for which FDA intends to exercise enforcement discretion.

### Q: Why does the cardiovascular event in 24 hours example not fall under enforcement discretion?

Can FDA clarify why the example on page 11 of the updated guidance, for "a software function predicting risk of a cardiovascular event in the next 24 hours", does not fall under the enforcement discretion policy for certain software functions that have one clinically appropriate output but otherwise meet other criteria?

**A:** While this software function has one clinically appropriate output, it fails criterion four because of the time-critical nature of the HCP's decision-making for this intended use, in that there is not sufficient time for the HCP to consider the basis of the recommendation. However, not all software functions that provide a recommendation for harm that may occur within 24 hours necessarily fail criterion four.

### Q: What usability evidence is appropriate for criterion four?

Page 15 notes that usability testing may be needed to evaluate whether implementation meets criterion four. If a product is ultimately considered non-device CDS, could FDA suggest the types of usability evidence that are appropriate to document and whether any public frameworks or standards are recommended for demonstrating adequate independent review by HCPs?

**A:** First, this recommendation wasn't changed in either of the recent updates. Second, FDA does not have specific recommendations on what usability testing may demonstrate that an implementation meets criterion four. However, FDA may request information on usability testing if there is a question about whether a software function fails criterion four and therefore could be a device software function.

## Closing Remarks

Aneesh Deoras: Thank you all for the questions and for joining our discussion on the clinical decision support software guidance. Again, please reach out if you have any questions and we look forward to seeing you for the next town hall.

CAPT Kim Piermatteo: A recording of today's event, a copy of the slides and a transcript will be posted as soon as possible to the event page, as well as to CDRH Learn under the section titled "Specialty Technical Topics," and the sub-section "Digital Health."

If you have additional questions regarding today's town hall, feel free to reach out to DICE at DICE@fda.hhs.gov.

For upcoming CDRH Events, monitor the CDRH Events webpage at www.fda.gov/CDRHevents.
