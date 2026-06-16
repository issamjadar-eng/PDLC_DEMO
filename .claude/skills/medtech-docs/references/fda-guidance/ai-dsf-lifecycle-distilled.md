# FDA Guidance: AI-Enabled Device Software Functions -- Lifecycle Management

🔎 **Finding aid — NOT the authoritative source.** Distilled summary for quick orientation and early analysis. Ground and cite the authoritative full text [`source-md/ai-dsf-lifecycle.md`](source-md/ai-dsf-lifecycle.md); verify any quote against the byte-correct `source/` PDF before treating it as verbatim. This paraphrases and omits (appendices/worked examples are routinely dropped) — a section's absence here is never evidence the source is silent.

**Full Title**: Artificial Intelligence-Enabled Device Software Functions: Lifecycle Management and Marketing Submission Recommendations
**Document Date**: January 7, 2025
**Status**: Draft -- Not for Implementation
**PDF Source**: https://www.fda.gov/media/184856/download
**Issuing Body**: CDRH, CBER, CDER, Office of Combination Products
**Document Number**: GUI00007028

## Scope

This is a **comprehensive lifecycle management and marketing submission content** guidance for **all AI-enabled devices** -- not limited to the PCCP mechanism. It provides:

- Recommendations on marketing submission content for devices that include AI-enabled device software functions (AI-DSFs)
- Recommendations for design, development, deployment, and maintenance throughout the Total Product Life Cycle (TPLC)
- Strategies for transparency and bias across the TPLC
- Recommendations for postmarket performance monitoring

This guidance applies to **AI-enabled devices only** -- devices that include one or more AI-DSFs. It does NOT apply to non-AI device software functions. For non-AI software, refer to the "Content of Premarket Submissions for Device Software Functions" guidance.

### Applicable Marketing Submission Types

510(k), De Novo, PMA, HDE, BLA, and IDE submissions (in part).

### Combination Products

Applies to the device constituent part of device-led combination products when that part includes an AI-DSF. Early FDA engagement strongly encouraged.

### Relationship to AI/ML PCCP Guidance

| Aspect | This Guidance (Lifecycle/Broad) | PCCP AI/ML Guidance |
|--------|-------------------------------|---------------------|
| **Focus** | Full lifecycle and submission content for ALL AI-enabled devices | Specifically the PCCP mechanism for iterative AI-DSF modifications |
| **PCCP detail** | References PCCP guidance; encourages use | Defines PCCP components and requirements in detail |
| **Applicability** | All AI-enabled devices (not just those using PCCPs) | Only AI-DSFs using the PCCP mechanism |

These documents are **complementary**: this guidance tells you what to include in a marketing submission for any AI-enabled device; the PCCP guidance tells you how to structure a PCCP within that submission.

## Key Requirements

### Marketing Submission Content Sections

#### 1. Device Description (Section V)
- Statement that AI is used
- Inputs, outputs, intended users, use environment, workflow integration
- Automation level and configurable elements
- Hardware platform description

#### 2. User Interface and Labeling (Section VI)
- Graphical representations, operational sequence, example outputs, demo video
- Labeling must include: AI inclusion statement, model I/O, automation level, architecture description, development data description, performance data with confidence intervals, subgroup performance, performance monitoring tools, known limitations, installation/integration instructions, customization instructions, patient/caregiver materials

**Performance Metrics for Labeling:**
- AUROC, sensitivity, specificity
- True/false positive and negative counts (confusion matrix)
- PPV/NPV, PLR/NLR
- All estimates with confidence intervals (typically 95% two-sided)
- Subgroup performance analysis
- Operating point performance (when applicable)

#### 3. Risk Assessment (Section VII)
- Risk management file (plan + assessment + report)
- AI-specific risks: bias, opacity, data drift
- Information-related risks
- Usability risk controls

#### 4. Data Management (Section VIII)
- Data collection protocols, cleaning/processing, reference standard, annotation
- Data storage/version control
- Development/test data independence
- Representativeness analysis (demographics, sites, equipment)
- Subgroup analysis
- OUS data justification (if applicable)
- Synthetic data justification (if applicable)

#### 5. Model Description and Development (Section IX)
- Architecture, features, feature selection, loss functions, parameters
- Quality control criteria, pre/post-processing, data augmentation
- Training methods, optimization, learning paradigm, regularization, hyperparameters
- Convergence curves, tuning evaluation
- Pre-trained model provenance, ensemble methods
- Thresholds, calibration

#### 6. Performance Validation (Section X)
- Pre-specified study protocols and statistical analysis plans
- Sample size justification with adequate power
- Primary/secondary endpoints with pre-specified acceptance criteria
- Statistical hypotheses (null and alternative) with multiplicity corrections
- Subgroup analyses (statistically powered when subgroup claims are made)
- Repeatability/reproducibility evaluation
- Human-device team performance (when human is in the loop)
- Masking/blinding protocols
- Precision studies using SD and %CV
- 95% two-sided confidence intervals standard for primary endpoints
- Within-patient correlations accounted for when applicable
- Quality control algorithm bias analysis (worst-case sensitivity analysis)

#### 7. Software Version History
- All differences between tested and released model versions
- Impact assessment of differences on safety and effectiveness
- Post-hoc model adjustments after seeing test data require FDA concurrence

#### 8. Device Performance Monitoring (Section XI)
- Data collection methods for postmarket monitoring
- Drift detection (data drift, concept drift)
- Input monitoring
- User behavior monitoring
- Update deployment plan
- Communication procedures for performance changes

#### 9. Cybersecurity (Section XII)
- AI-specific threat model: data poisoning, model inversion, evasion attacks, data leakage, overfitting exploitation, bias manipulation, performance drift
- Fuzz testing, penetration testing
- Access controls, encryption, de-identification

#### 10. Public Submission Summary / Model Card (Section XIII)
- Statement that AI is used
- Explanation of how AI achieves the intended use
- Model class description and limitations
- Development and validation dataset descriptions (size, source, demographics)
- Statistical confidence level of predictions
- Description of how the model will be updated/maintained over time
- Model card recommended (see Appendix E in guidance for format)

**Model Card Contents:**
- Device info, regulatory status, description
- Performance and limitations
- Risk management summary
- Deployment/update information
- Development data characterization

## Key Definitions

| Term | Definition |
|------|-----------|
| **Device Software Function (DSF)** | A software function that meets the device definition in section 201(h) of the FD&C Act. (The guidance's DSF definition does not itself use the SaMD/SiMD split.) |
| **AI-Enabled Device** | A device that includes one or more AI-enabled device software functions (AI-DSFs). |
| **AI-DSF** | A device software function that implements one or more AI models. |
| **Model** | A mathematical construct that generates an inference or prediction based on new input data. |
| **Validation** | Per 21 CFR 820.3(z): confirmation by examination and provision of objective evidence that particular requirements for a specific intended use can be consistently fulfilled. NOT the AI community's usage for tuning. |
| **Development** | Training, tuning, and tuning evaluation (often called "internal testing" in AI community). |
| **Test Data** | Data used for verification and validation activities. NOT part of the development process. |
| **AI Bias** | A potential tendency to produce incorrect results systematically, which can impact safety and effectiveness within all or a subset of the intended use population. |
| **Data Drift** | Changes in input data used during development compared to input data in actual deployments. |
| **Reference Standard** | The best available representative truth for each patient/case/record. |
| **Synthetic Data** | Artificially created data representing the structure, properties, and relationships of actual patient data. *(Distiller-supplied gloss — this guidance references synthetic data in passing but carries no formal definition.)* |

**Terminology Warning:** FDA explicitly warns against using "validation" in the AI community sense (tuning/model selection) in marketing submissions. Use "development" for training/tuning and "validation" only for the 21 CFR 820.3(z) meaning.

## Submission Requirements

### Where to Include Content in the Submission

| Guidance Section | Submission Location |
|-----------------|---------------------|
| Device Description | Device Description section |
| User Interface | Software Description in Software Documentation |
| Labeling | Labeling section |
| Risk Assessment | Risk Management File in Software Documentation |
| Data Management (development data) | Software Description in Software Documentation |
| Data Management (testing data) | Performance Testing |
| Model Description | Software Description in Software Documentation |
| Performance Validation (clinical/non-clinical) | Performance Testing |
| Performance Validation (software V&V) | Software Documentation |
| Performance Monitoring | Risk Management File in Software Documentation |
| Cybersecurity | Cybersecurity/Interoperability section |
| Public Summary | Administrative Documentation |

### Postmarket Reporting

- Manufacturers must report deaths, serious injuries, and malfunctions per 21 CFR Parts 803 and 806
- Performance monitoring plan results and mitigations should be communicated to device users

### Design Controls

- 21 CFR 820.30 requires procedures to identify, document, validate or verify, review, and approve design changes before implementation
- Nonconforming product procedures (21 CFR 820.90) and CAPA (21 CFR 820.100) apply
- QSR→QMSR transition: ISO 13485:2016 incorporated by reference effective February 2, 2026 *(external regulatory context, not stated in this guidance)*

## Cross-References

- **PCCP AI/ML Guidance**: Marketing Submission Recommendations for a PCCP for AI-DSFs
- **Premarket Software Guidance**: Content of Premarket Submissions for Device Software Functions
- **Device Modifications Guidances**: Deciding When to Submit a 510(k) for a Change/Software Change to an Existing Device
- **Cybersecurity Guidance**: Cybersecurity in Medical Devices (2023)
- **Human Factors**: Applying Human Factors and Usability Engineering to Medical Devices
- **Q-Submission Program**: Requests for Feedback and Meetings
- **Interoperability**: Design Considerations and Premarket Submission Recommendations for Interoperable Medical Devices
- **Real-World Evidence**: Use of Real-World Evidence to Support Regulatory Decision-Making
- **Diagnostic Statistics**: Statistical Guidance on Reporting Results from Studies Evaluating Diagnostic Tests
- **Demographics in Studies**: Collection of Race and Ethnicity Data in Clinical Trials; Age-, Race-, and Ethnicity-Specific Data; Sex-Specific Data
- **Standards**: ANSI/AAMI/ISO 14971 (Risk Management), AAMI CR34971 (ISO 14971 for AI/ML). *(The guidance names only these two; ANSI/AAMI HE75 (Human Factors) and ISO 13485 (QMS) are distiller-added related standards.)*
