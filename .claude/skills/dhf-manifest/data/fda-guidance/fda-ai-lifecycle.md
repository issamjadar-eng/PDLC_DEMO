# Tier 1 Regulatory Distillation — FDA AI-Enabled Device Software Functions: Lifecycle Management

**Guidance**: Artificial Intelligence-Enabled Device Software Functions: Lifecycle Management and Marketing Submission Recommendations
**Date**: January 7, 2025 (Draft)
**Topic coverage**: regulatory-submission, validation, software-lifecycle
**Distillation date**: 2026-04-21
**Source references**:
- `.claude/skills/medtech-docs/references/fda-guidance/ai-dsf-lifecycle-distilled.md`

> **Note**: FDA guidance is nonbinding.

---

<a id="OBL-AI-LIFE-001"></a>

```yaml
id: OBL-AI-LIFE-001
title: "AI Device Description"
source: FDA AI Lifecycle Guidance (2025) §V Device Description
section: "AI Device Description — Required Content"
scope_flags: [ai, 510k]
topic: regulatory-submission
artifact_type: submission-content
dhf_owner: system
min_iec62304_class: A
applies_to: [510(k) Submission — Device Description, Software Description]
verbatim: "Statement that AI is used. Inputs, outputs, intended users, use environment, workflow integration. Automation level and configurable elements. Hardware platform description."
extracted_requirements:
  - 510(k) device description must explicitly state that the device includes AI
  - Describe AI inputs (imaging data type, format, resolution requirements), outputs (segmentation, measurements, guidance recommendations), intended users, and use environment
  - State the automation level: fully automated, human-in-the-loop, human-on-the-loop, or human-supervised
  - Describe hardware platform on which AI runs (server for Pre-Op, tablet for Intra-Op)
  - Describe workflow integration: where in the clinical workflow the AI output is presented to the clinician
```

**Context**: The "automation level" disclosure is critical for HipLink. Pre-Op AI (anatomy segmentation, implant sizing) is human-in-the-loop — the surgeon reviews and confirms AI results before they are used. Intra-Op guidance is more time-critical — the automation level for Intra-Op real-time guidance must be clearly stated (e.g., AI provides suggestions that the surgeon validates; surgeon maintains authority over all surgical decisions). Automation bias risk increases with higher automation levels.

---

<a id="OBL-AI-LIFE-002"></a>

```yaml
id: OBL-AI-LIFE-002
title: "AI Device Labeling"
source: FDA AI Lifecycle Guidance (2025) §VI Labeling
section: "AI Labeling Requirements"
scope_flags: [ai, 510k]
topic: labeling-ifu
artifact_type: labeling
dhf_owner: system
min_iec62304_class: A
applies_to: [Instructions for Use, User Documentation, 510(k) Submission — Labeling]
verbatim: "Labeling must include: AI inclusion statement, model I/O, automation level, architecture description, development data description, performance data with confidence intervals, subgroup performance, performance monitoring tools, known limitations, installation/integration instructions."
extracted_requirements:
  - IFU must state that AI is included and describe its role in the device
  - IFU must disclose model inputs and outputs in plain language understandable to the intended user (surgeon)
  - IFU must state the automation level and explicitly note that the surgeon maintains clinical authority
  - Disclose development data characteristics: training data size, source population demographics, geographic distribution, imaging equipment used
  - Include performance data with 95% confidence intervals for all primary performance metrics
  - Include subgroup performance breakdown: sex, age, race/ethnicity, disease severity, BMI (as applicable)
  - Document known limitations: imaging conditions where performance may degrade, patient populations not well-represented in training data
  - Performance monitoring tools disclosure: how users can track device performance in their clinical setting
```

**Context**: The AI labeling requirements are substantially more extensive than traditional software labeling. For HipLink, the IFU for Pre-Op must disclose: that CT/MRI segmentation is AI-generated, the performance metrics with CIs from the validation study, the demographic breakdown of the training and test datasets, and which patient types are at the boundary of the validated use (e.g., patients with severe dysplasia not well-represented in training data). This disclosure enables informed clinical decision-making.

---

<a id="OBL-AI-LIFE-003"></a>

```yaml
id: OBL-AI-LIFE-003
title: "AI Data Management Plan"
source: FDA AI Lifecycle Guidance (2025) §VIII Data Management
section: "Data Management — Development and Testing Data"
scope_flags: [ai, 510k]
topic: validation
artifact_type: submission-content
dhf_owner: both
min_iec62304_class: A
applies_to: [510(k) Submission — Performance Testing, Data Management Plan]
verbatim: "Data collection protocols, cleaning/processing, reference standard, annotation. Data storage/version control. Development/test data independence. Representativeness analysis (demographics, sites, equipment). Subgroup analysis. OUS data justification (if applicable). Synthetic data justification (if applicable)."
extracted_requirements:
  - Document data collection protocols for training and testing datasets: inclusion/exclusion criteria, demographics, imaging equipment, sites
  - Demonstrate representativeness: development and test data must represent the intended use population (demographics, clinical settings, imaging equipment types)
  - Perform subgroup analysis: assess AI performance separately for key subpopulations (sex, age, race/ethnicity, BMI, disease severity)
  - If using out-of-US (OUS) data for training/testing: justify applicability to US intended use population
  - If using synthetic data: justify the methodology and demonstrate that synthetic data appropriately represents real clinical data
  - Test data must be independent of development data — provide evidence of sequestration
```

**Context**: For HipLink, training data likely includes CT/MRI scans from Arthrex's clinical network. The submission must demonstrate that this data is representative of US patients who will use HipLink (demographics, imaging equipment, clinical settings). If training data is primarily European or Asian datasets, the OUS justification must address whether those populations are representative of US hip morphology. This often drives a US-specific validation study even when broader datasets are used for training.

---

<a id="OBL-AI-LIFE-004"></a>

```yaml
id: OBL-AI-LIFE-004
title: "AI Performance Validation"
source: FDA AI Lifecycle Guidance (2025) §X Performance Validation
section: "AI Performance Validation — Statistical Requirements"
scope_flags: [ai, 510k]
topic: validation
artifact_type: submission-content
dhf_owner: both
min_iec62304_class: A
applies_to: [510(k) Submission — Performance Testing, Clinical/Non-Clinical Study Protocol]
verbatim: "Pre-specified study protocols and statistical analysis plans. Sample size justification with adequate power. Primary/secondary endpoints with pre-specified acceptance criteria. Statistical hypotheses (null and alternative) with multiplicity corrections. Subgroup analyses (statistically powered when subgroup claims are made). Repeatability/reproducibility evaluation. Human-device team performance (when human is in the loop). 95% two-sided confidence intervals standard for primary endpoints."
extracted_requirements:
  - Pre-specify all study protocols and statistical analysis plans BEFORE conducting performance validation — post-hoc modifications require FDA concurrence
  - Provide sample size justification with statistical power analysis for primary endpoints
  - Define primary/secondary endpoints with pre-specified acceptance criteria (pass/fail thresholds)
  - State null and alternative hypotheses; apply multiplicity corrections for multiple endpoints
  - Conduct statistically powered subgroup analyses for key demographic subgroups when making subgroup performance claims
  - Evaluate repeatability (same reader, same image, different times) and reproducibility (different readers, different sites)
  - For human-in-the-loop AI (HipLink): evaluate human-device team performance — how does the surgeon perform WITH the AI vs. without?
  - Report all primary endpoints with 95% two-sided confidence intervals
```

**Context**: The human-device team performance evaluation is specifically important for HipLink's AI-assisted surgical guidance. FDA expects evidence not just that the AI algorithm performs well in isolation, but that the combined human-AI team (surgeon using HipLink guidance) performs better or at least equivalently to the baseline (without AI assistance). This may require a human factors study or a reader study comparing surgical planning/guidance accuracy with vs. without AI.

---

<a id="OBL-AI-LIFE-005"></a>

```yaml
id: OBL-AI-LIFE-005
title: "AI Performance Monitoring"
source: FDA AI Lifecycle Guidance (2025) §XI Device Performance Monitoring
section: "Post-Market AI Performance Monitoring"
scope_flags: [ai, 510k, pccp]
topic: post-market
artifact_type: plan
dhf_owner: system
min_iec62304_class: A
applies_to: [Post-Market Surveillance Plan, Device Performance Monitoring Plan]
verbatim: "Data collection methods for postmarket monitoring. Drift detection (data drift, concept drift). Input monitoring. User behavior monitoring. Update deployment plan. Communication procedures for performance changes."
extracted_requirements:
  - Define a post-market AI performance monitoring plan as part of the submission
  - Specify data drift detection: monitoring whether real-world input data distribution shifts from training distribution (imaging equipment changes, patient population changes)
  - Specify concept drift detection: monitoring whether the AI's performance on its intended task degrades over time
  - Define monitoring metrics, monitoring frequency, and thresholds that trigger investigation/corrective action
  - Define how performance changes are communicated to users (update release notes, labeling updates)
  - For PCCP devices: the performance monitoring plan must integrate with the PCCP device monitoring plan
```

**Context**: Post-market AI performance monitoring is a continuous obligation, not a one-time validation. For HipLink, real-world input data drift could occur as imaging technology evolves (new C-arm models, higher resolution DICOM formats) or as the clinical practice evolves (new surgical techniques, different patient populations). The monitoring plan must define specific triggers: e.g., if performance metrics on a rolling real-world sample drop below 90% of the accepted threshold, a root cause analysis and PCCP modification review are triggered.

---

<a id="OBL-AI-LIFE-006"></a>

```yaml
id: OBL-AI-LIFE-006
title: "AI-Specific Cybersecurity"
source: FDA AI Lifecycle Guidance (2025) §XII Cybersecurity (AI-Specific)
section: "AI-Specific Cybersecurity Threats"
scope_flags: [ai, cybersecurity, 510k]
topic: cybersecurity
artifact_type: submission-content
dhf_owner: both
min_iec62304_class: A
applies_to: [Threat Model, Security Risk Assessment, 510(k) Submission — Cybersecurity]
verbatim: "AI-specific threat model: data poisoning, model inversion, evasion attacks, data leakage, overfitting exploitation, bias manipulation, performance drift. Fuzz testing, penetration testing. Access controls, encryption, de-identification."
extracted_requirements:
  - Threat model must include AI-specific attacks in addition to standard cybersecurity threats
  - Data poisoning: adversary corrupts training/re-training data to degrade model performance or introduce bias
  - Model inversion: adversary attempts to reconstruct patient data from AI model outputs
  - Evasion attacks: adversary manipulates inputs (e.g., imaging data) to cause AI to produce incorrect outputs
  - Bias manipulation: adversary systematically degrades AI performance for specific patient subpopulations
  - Performance drift exploitation: adversary exploits known model weaknesses during periods of degraded performance
  - AI model access controls: who can trigger re-training, update deployment, and model configuration changes
```

**Context**: AI-specific security threats are an extension of the standard cybersecurity threat model required by the FDA Cybersecurity guidance. For HipLink, data poisoning is a relevant risk if re-training data is sourced from multiple hospital sites — a compromised hospital could contribute corrupted training data. Evasion attacks on Intra-Op's real-time guidance are particularly dangerous — adversary-manipulated C-arm images could cause AI to produce incorrect surgical guidance. These AI-specific threats must appear in HipLink's threat model.
