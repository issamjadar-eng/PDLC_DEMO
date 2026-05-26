# Tier 1 Regulatory Distillation — FDA AI/ML PCCP Guidance

**Guidance**: Marketing Submission Recommendations for a PCCP for AI/ML-Enabled Device Software Functions
**Date**: August 18, 2025 (Final)
**Statutory basis**: FD&C Act §515C (added by FDORA, December 29, 2022)
**Topic coverage**: regulatory-submission, configuration-change, validation
**Distillation date**: 2026-04-21
**Source references**:
- `.claude/skills/medtech-docs/references/fda-guidance/pccp-aiml-distilled.md`

> **Note**: FDA guidance is nonbinding. Obligations represent FDA's stated expectations for premarket submissions.

---

<a id="OBL-AIML-PCCP-001"></a>

```yaml
id: OBL-AIML-PCCP-001
title: "AI Modification Description"
source: FDA AI/ML PCCP Guidance (2025) §VI Description of Modifications
section: "Description of Modifications — AI-Specific Content"
scope_flags: [pccp, 510k, ai]
topic: regulatory-submission
artifact_type: submission-content
dhf_owner: system
min_iec62304_class: A
canonical_role: submission-authored
criticality: must-have
applies_to:
  - role: submission-authored
    file_pattern: "*pccp-document*.md"
verbatim: "Statement whether modifications are implemented automatically, manually, or combination. Statement whether modifications are global (uniform across all devices) or local (site/patient-specific). For local adaptations: description of what local factors warrant the change. Expected frequency of updates. Modifications must maintain the device within its intended use and indications for use."
extracted_requirements:
  - For each AI-DSF modification: state whether implementation is automatic, manual, or combined
  - State whether the modification is global (same for all deployed devices) or local (site/patient-specific adaptation)
  - For local adaptations: document which local factors (patient demographics, local image acquisition conditions, site workflow) trigger the modification
  - State expected frequency of updates (e.g., quarterly re-training, continuous learning with annual release)
  - All modifications must keep the device within its authorized intended use and indications for use
```

**Context**: MedTech Project's AI modifications are primarily manual (human-in-the-loop: MedTech Company reviews V&V results before releasing an updated model) and global (same updated model deployed to all tablets). Local adaptation (site-specific model tuning) is a potential future capability but would require explicit PCCP coverage if intended. The modification frequency drives the monitoring plan cadence — quarterly re-training cycles require quarterly performance monitoring.

---

<a id="OBL-AIML-PCCP-002"></a>

```yaml
id: OBL-AIML-PCCP-002
title: "AI Data Management Protocol"
source: FDA AI/ML PCCP Guidance (2025) §VII Data Management Practices
section: "Modification Protocol — Data Management"
scope_flags: [pccp, 510k, ai]
topic: regulatory-submission
artifact_type: submission-content
dhf_owner: system
min_iec62304_class: A
canonical_role: submission-authored
criticality: must-have
applies_to:
  - role: submission-authored
    file_pattern: "*pccp-document*.md"
  - role: plans
    file_pattern: "*data-management-plan*.md"
verbatim: "Collection protocols (inclusion/exclusion criteria, intended data distribution across covariates including sex, age, race, disease conditions, acquisition conditions, prospective vs. retrospective, enrichment/stratified sampling, number and geographic distribution of sites). Data quality assurance (consistency, completeness, authenticity, missing data handling, traceability). Test data sequestration (strategies to shield test data from development)."
extracted_requirements:
  - Define data collection protocols for PCCP re-training: inclusion/exclusion criteria, covariate distribution requirements (sex, age, race, disease conditions, imaging acquisition conditions)
  - Specify number and geographic distribution of sites contributing to re-training datasets
  - Define data quality assurance procedures: consistency checks, completeness, authenticity verification, handling of missing/equivocal data
  - Define reference standard determination method and clinician grading protocol
  - Define test data sequestration procedures — training data and test data must be strictly separated; test data never seen during development
  - Document measures to prevent unwanted bias from repeated use of test data sets
```

**Context**: For MedTech Project's AI modifications, the data management practices define the rules for how future re-training datasets are collected and managed. The test data set used to evaluate each modification must be independent of training/tuning data and collected from multiple sites. This ensures that performance claims on the modified AI are not inflated by data leakage. MedTech Company must define these practices at submission time — not re-specify them each time a modification is made.

---

<a id="OBL-AIML-PCCP-003"></a>

```yaml
id: OBL-AIML-PCCP-003
title: "AI Performance Evaluation Protocol"
source: FDA AI/ML PCCP Guidance (2025) §VII Performance Evaluation
section: "Modification Protocol — Performance Evaluation"
scope_flags: [pccp, 510k, ai]
topic: regulatory-submission
artifact_type: submission-content
dhf_owner: system
min_iec62304_class: A
canonical_role: submission-authored
criticality: must-have
applies_to:
  - role: submission-authored
    file_pattern: "*pccp-document*.md"
  - role: vnv-plan
    file_pattern: "*vnv-protocol-template*.md"
verbatim: "Assessment metrics (specific metrics, how they demonstrate safe use, comprehensive performance assessment, challenging cases). Statistical analysis plans (equivalent/improved performance vs. previous versions, high-risk subpopulations, sensitivity/specificity trade-offs, sample size determination). Performance targets (acceptance criteria, comparison to authorized version criteria, clinical justification). Failure handling: unresolvable failures must be recorded and specific modifications must NOT be implemented."
extracted_requirements:
  - Pre-specify performance metrics for each modification: sensitivity, specificity, AUC, measurement accuracy, etc.
  - Include statistical analysis plans: null/alternative hypotheses, sample size justification, primary analysis population, subgroup analysis requirements
  - Define acceptance criteria comparing modified AI-DSF to both the original authorized version AND the immediately preceding version
  - Perform performance evaluation across high-risk subpopulations (sex, age, race, disease severity, imaging acquisition variations)
  - If acceptance criteria are not met (unresolvable failure), the modification MUST NOT be implemented — document this requirement explicitly
  - Root cause analysis allowed for resolvable failures (not due to PCCP-specific aspects)
```

**Context**: Pre-specified acceptance criteria are the most important element of the Modification Protocol — they are what FDA pre-authorized when they cleared the PCCP. MedTech Company cannot modify acceptance criteria after seeing V&V results without FDA concurrence. For MFD A's segmentation algorithm, acceptance criteria might include: ≥90% Dice similarity coefficient on test set, non-inferiority to the cleared version at p<0.05, and consistent performance across male/female patients and BMI quartiles.

---

<a id="OBL-AIML-PCCP-004"></a>

```yaml
id: OBL-AIML-PCCP-004
title: "AI Update Procedures"
source: FDA AI/ML PCCP Guidance (2025) §VII Update Procedures
section: "Modification Protocol — Update Procedures"
scope_flags: [pccp, 510k, ai]
topic: regulatory-submission
artifact_type: submission-content
dhf_owner: system
min_iec62304_class: A
canonical_role: submission-authored
criticality: must-have
applies_to:
  - role: submission-authored
    file_pattern: "*pccp-document*.md"
  - role: postmarket
    file_pattern: "*post-market-surveillance-plan*.md"
  - role: plans
    file_pattern: "*labeling-update-process*.md"
verbatim: "Software V&V (whether plan differs from original, integrated environment testing, impact on other device functions). When and how updates deploy (decision criteria, expected timeline, frequency, mechanism, verification of critical safety features post-update). Communication and transparency (PCCP description in public summary/labeling, update communication to users, version information, option to review labeling before update). Device monitoring plan (adverse event tracking, real-world performance monitoring, subpopulation performance changes, rollback criteria)."
extracted_requirements:
  - Define software V&V procedures for each update: integration testing, regression testing, impact on non-modified device functions
  - Define update deployment mechanism: OTA update process, deployment timeline after V&V approval, staged rollout vs. simultaneous global deployment
  - Define post-update verification of critical safety features before the device is used in surgery
  - Define the real-world device monitoring plan: metrics collected, monitoring frequency, performance drift detection thresholds, subpopulation monitoring
  - Define rollback criteria and rollback procedure if post-deployment performance degrades
  - Communication plan: how users are informed of modifications, version information availability, labeling update process
```

**Context**: The update procedure defines how MedTech Project AI modifications flow from V&V approval to the surgical OR. For Intra-Op, post-update verification of critical safety features before clinical use is critical — a broken update should not reach the surgical field. The monitoring plan must track real-world performance post-deployment (not just pre-deployment V&V), including subpopulation drift (model performing worse for a specific patient type after re-training). Rollback criteria must be pre-defined.

---

<a id="OBL-AIML-PCCP-005"></a>

```yaml
id: OBL-AIML-PCCP-005
title: "AI Change Impact Assessment"
source: FDA AI/ML PCCP Guidance (2025) §VIII Impact Assessment
section: "Impact Assessment — AI-Specific Content"
scope_flags: [pccp, 510k, ai]
topic: regulatory-submission
artifact_type: submission-content
dhf_owner: system
min_iec62304_class: A
canonical_role: submission-authored
criticality: must-have
applies_to:
  - role: submission-authored
    file_pattern: "*pccp-document*.md"
  - role: risk-management
    file_pattern: "*risk-management-file*.md"
verbatim: "Discussion of benefits and risks of each modification, including risks of harm and unintended bias. How V&V activities in the Modification Protocol ensure continued safety and effectiveness. How implementation of one modification impacts another. Cumulative impact of implementing all modifications."
extracted_requirements:
  - For each AI-DSF modification: assess risks of harm AND risks of unintended bias (demographic bias, site-specific bias, data drift bias)
  - Discuss how the Modification Protocol V&V activities specifically address each identified risk
  - Assess modification interaction effects: does implementing Pre-Op algorithm update affect Intra-Op guidance performance?
  - Assess cumulative impact when all PCCP modifications are implemented simultaneously
  - Cross-reference bias risk management with the data management practices (how training data distribution controls bias risks)
```

**Context**: AI bias is an explicit FDA concern for AI-DSF PCCPs. The Impact Assessment must address not just clinical performance risks but also the risk that a re-trained algorithm performs systematically worse for certain patient subpopulations (e.g., female patients with atypical hip anatomy, patients with prior hip hardware). This must be linked back to the data management practices (how the training dataset is constructed to mitigate these biases) and the performance evaluation plan (how subgroup performance is assessed for each modification).

---

<a id="OBL-AIML-PCCP-006"></a>

```yaml
id: OBL-AIML-PCCP-006
title: "AI Change Quality System"
source: FDA AI/ML PCCP Guidance (2025) §IX Quality System
section: "Quality System Requirements"
scope_flags: [pccp, 510k, ai]
topic: configuration-change
artifact_type: process-record
dhf_owner: system
min_iec62304_class: A
canonical_role: plans
criticality: must-have
applies_to:
  - role: plans
    file_pattern: "*design-change-records*.md"
  - role: plans
    file_pattern: "*pccp-implementation-records*.md"
  - role: plans
    file_pattern: "*capa-records*.md"
verbatim: "QMS compliance with 21 CFR Part 820 / ISO 13485:2016. Design control procedures for PCCP modifications (21 CFR 820.30). Change management processes for PCCP implementation. Document and record retention (minimum 2 years from commercial release). CAPA procedures applicable to PCCP deviations."
extracted_requirements:
  - Each PCCP modification implementation is a design change under ISO 13485 §7.3.9 — must be reviewed, V&V'd per the Modification Protocol, and approved before release
  - Maintain QMS records for each PCCP modification: V&V results, comparison to acceptance criteria, approval authorization, deployment record
  - Document and record retention: minimum 2 years from commercial release for each modification record
  - PCCP deviations (failure to follow the Modification Protocol) must be handled via CAPA
  - QSR transition to ISO 13485 effective February 2, 2026 — QMS must be compliant before first post-market PCCP modification
```

**Context**: Every PCCP modification implementation generates a set of required QMS records: V&V data, performance results vs. acceptance criteria, approval record, update deployment record, post-deployment monitoring results. These are not optional documentation — they are the evidence base that justifies NOT filing a new 510(k). MedTech Company's QMS must have a defined PCCP implementation workflow that produces these records consistently for every modification.
