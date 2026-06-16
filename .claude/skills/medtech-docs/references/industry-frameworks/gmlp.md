# Good Machine Learning Practice (GMLP) — Guiding Principles

🔎 **Finding aid — NOT the authoritative source.** Paraphrased distillation of an external standard/framework; no faithful full-text copy exists in this repository (copyrighted). The original document named in the header above is the sole authority — if a clause-level question isn't answered here, state that the original must be consulted; do not infer clause content. `[VERIFY]` marks are unconfirmed against the source.

**Framework**: Good Machine Learning Practice for Medical Device Development: Guiding Principles (October 2021)
**Source**: FDA, Health Canada, MHRA (joint publication)
**Referenced In**: PCCP AI/ML guidance

## Overview

The GMLP Guiding Principles are 10 consensus principles jointly published by FDA, Health Canada, and the UK's MHRA. They represent the regulators' expectations for responsible development of AI/ML-enabled medical devices. While not legally binding, they are referenced in FDA's PCCP AI/ML guidance and signal what FDA considers good practice.

## The 10 Guiding Principles

### Principle 1 — Multi-Disciplinary Expertise Is Leveraged Throughout the Total Product Life Cycle

- Involve diverse expertise: clinical, data science, engineering, regulatory, human factors, cybersecurity
- Expertise should span the entire lifecycle, not just development

### Principle 2 — Good Software Engineering and Security Practices Are Implemented

- Follow established software engineering practices (IEC 62304)
- Apply security best practices (IEC 81001-5-1, NIST CSF)
- Maintain data integrity, reproducibility, and auditability of the ML pipeline
- Version control for data, models, and code

### Principle 3 — Clinical Study Participants and Data Sets Are Representative of the Intended Patient Population

- Training, validation, and test data must reflect the intended patient population
- Consider demographic diversity: age, sex, race, ethnicity, comorbidities
- Address potential bias and data imbalance

### Principle 4 — Training Data Sets Are Independent of Test Sets

- Maintain strict separation between training, validation, and test datasets
- Avoid data leakage
- Document data splitting methodology

### Principle 5 — Selected Reference Datasets Are Based Upon Best Available Methods

- Use gold-standard or best-available reference data for ground truth
- Document the method for establishing reference labels/annotations
- Quantify inter-rater variability when using human-annotated data

### Principle 6 — Model Design Is Tailored to the Available Data and Reflects the Intended Use of the Device

- Model complexity should match the available data — avoid overfitting
- Model architecture should align with the clinical task
- Justify the choice of model architecture

### Principle 7 — Focus Is Placed on the Performance of the Human-AI Team

- Evaluate performance of the human-AI system, not just the algorithm in isolation
- Consider how clinicians interact with AI outputs (trust, over-reliance, dismissal)
- Design the UI to support appropriate human oversight

### Principle 8 — Testing Demonstrates Device Performance During Clinically Relevant Conditions

- Test under conditions that reflect real clinical use
- Include edge cases, challenging cases, and failure modes
- Performance metrics should be clinically meaningful (not just technical metrics)

### Principle 9 — Users Are Provided Clear, Essential Information

- Provide users with information about the device's AI/ML capabilities and limitations
- Include: intended use, performance characteristics, known limitations, training data description
- Enable users to make informed decisions about AI outputs

### Principle 10 — Deployed Models Are Monitored for Performance and Re-Training Risks Are Managed

- Monitor real-world performance for drift or degradation
- Establish triggers for model re-evaluation
- Manage risks from re-training (data shifts, performance changes)

## Mapping to PCCP AI/ML Guidance

| GMLP Principle | PCCP AI/ML Guidance Section | Connection |
|---------------|---------------------------|------------|
| 1 (Multi-disciplinary) | General — team competency | PCCP modifications require diverse expertise for evaluation |
| 2 (Software engineering) | Section on software documentation | IEC 62304 applies to ML components |
| 3 (Representative data) | Modification Protocol — data requirements | Data representativeness is a pre-condition for model updates |
| 4 (Independent test sets) | Modification Protocol — evaluation methodology | Independent evaluation data required for change validation |
| 5 (Reference datasets) | Performance criteria — ground truth | Reference standards must be defined for each modification type |
| 6 (Model design) | Description of modifications | Model architecture changes must be justified |
| 7 (Human-AI team) | Impact assessment — usability | Changes must not degrade human-AI team performance |
| 8 (Clinically relevant testing) | Performance criteria — acceptance thresholds | Testing must use clinically relevant conditions |
| 9 (User information) | Labeling requirements | Labeling must be updated for material AI changes |
| 10 (Monitoring) | Update procedures — post-deployment | Ongoing monitoring required; feeds back into PCCP change triggers |
