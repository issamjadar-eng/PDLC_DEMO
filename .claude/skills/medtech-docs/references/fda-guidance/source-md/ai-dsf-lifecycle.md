# Artificial Intelligence-Enabled Device Software Functions: Lifecycle Management and Marketing Submission Recommendations

**Full Title**: Artificial Intelligence-Enabled Device Software Functions: Lifecycle Management and Marketing Submission Recommendations — Draft Guidance for Industry and Food and Drug Administration Staff
**Document Date**: January 7, 2025
**Status**: DRAFT — Not for Implementation
**PDF Source**: https://www.fda.gov/media/184856/download
**Document Number**: GUI00007028
**Issuing Bodies**: CDRH, CBER, CDER, Office of Combination Products

---

## Table of Contents

- I. Introduction
- II. Scope
- III. TPLC Approach: General Principles
- IV. How to Use this Guidance: Overview of AI-Enabled Device Marketing Submission Content Recommendations
  - A. Quality System Documentation
- V. Device Description
- VI. User Interface and Labeling
  - A. User Interface
  - B. Labeling
- VII. Risk Assessment
- VIII. Data Management
- IX. Model Description and Development
- X. Validation
  - A. Performance Validation
- XI. Device Performance Monitoring
- XII. Cybersecurity
- XIII. Public Submission Summary
- Appendix A: Table of Recommended Documentation
- Appendix B: Transparency Design Considerations
- Appendix C: Performance Validation Considerations
- Appendix D: Usability Evaluation Considerations
- Appendix E: Example Model Card
- Appendix F: Example 510(k) Summary with Model Card

---

## I. Introduction

FDA has long promoted a total product life cycle (TPLC) approach to the oversight of medical devices, including artificial intelligence (AI)-enabled devices, and has committed to developing guidances and resources for such an approach. Some recent efforts include developing guiding principles for good machine learning practice (GMLP) and transparency for machine learning-enabled devices to help promote safe, effective, and high-quality machine learning models; and a public workshop on fostering a patient-centered approach to AI-enabled devices, including discussions of device transparency for users. This guidance intends to continue these efforts, by providing lifecycle management and marketing submission recommendations consistent with a TPLC approach for AI-enabled devices.

This guidance provides recommendations on the contents of marketing submissions for devices that include AI-enabled device software functions including documentation and information that will support FDA's review. To support the development of appropriate documentation for FDA's assessment of devices, this guidance also provides recommendations for the design and development of AI-enabled devices that manufacturers may consider using throughout the TPLC. The recommendations reflect a comprehensive approach to lifecycle management of AI-enabled devices throughout the TPLC. Furthermore, the guidance includes FDA's current thinking on strategies to address transparency and bias throughout the TPLC of AI-enabled devices, including by collecting evidence to evaluate whether a device benefits all relevant demographic groups (e.g., race, ethnicity, sex, and age) similarly, to help ensure these devices remain safe and effective for their intended use.

The emergence of consensus standards related to software has helped to improve the consistency and quality of software development and documentation, particularly with respect to activities such as risk assessment and management. When possible, FDA harmonized the terminology and recommendations in this guidance with software-related consensus standards. The Agency encourages the consideration of such FDA-recognized consensus standards when developing AI-enabled devices and preparing premarket documentation. For the current edition of the FDA-recognized consensus standards referenced in this document, see the FDA Recognized Consensus Standards Database. If submitting a Declaration of Conformity to a recognized standard, we recommend including the appropriate supporting documentation.

In general, FDA's guidance documents do not establish legally enforceable responsibilities. Instead, guidances describe the Agency's current thinking on a topic and should be viewed only as recommendations, unless specific regulatory or statutory requirements are cited. The use of the word *should* in Agency guidances means that something is suggested or recommended, but not required.

## II. Scope

For purposes of this guidance, FDA refers to a software function that meets the definition of a device as a "device software function." A "device software function" is a software function that meets the device definition in section 201(h) of the Federal Food, Drug, and Cosmetic Act (FD&C Act). As discussed in other FDA guidance, the term "function" is a distinct purpose of the product, which could be the intended use or a subset of the intended use of the product.

AI-enabled devices are devices that include one or more AI-enabled device software functions (AI-DSFs). An AI-DSF is a device software function that implements one or more "AI models" (referred to as "models" in this guidance) to achieve its intended purpose. A model is a mathematical construct that generates an inference or prediction based on new input data. In this guidance, when "AI-enabled device" is used, it refers to the whole device, whereas when "AI-DSF" is used, it refers only to the function that uses AI. In this guidance, when "model" is used, it refers only to the mathematical construct.

To continue to support the development of AI enabled devices, this guidance provides recommendations on the documentation and information that should be included in marketing submissions to support FDA's review of devices that include AI-DSFs. For purposes of this guidance, the term "marketing submission" refers to premarket notification (510(k)) submission, De Novo classification request, Premarket Approval (PMA) application, Humanitarian Device Exemption (HDE), or Biologics License Application (BLA). Some of the proposed recommendations in this guidance also may apply to Investigational Device Exemption (IDE) submissions. For AI-enabled devices subject to 510(k) requirements, an AI-enabled device can be found substantially equivalent to a non-AI-enabled device with the same intended use provided, among other things, the AI-enabled device does not introduce different questions of safety and effectiveness compared to the non-AI-enabled device and meets other requirements for a determination of substantial equivalence in accordance with section 513(i) of the FD&C Act.

Generally, the recommendations in this guidance also apply to the device constituent part of a combination product when the device constituent part includes an AI-DSF. In developing an AI-DSF, sponsors should consider the impact of the AI-DSF in the context of the combination product as a whole. For a combination product that includes an AI-DSF, we highly encourage early engagement with the FDA lead review division for the combination product.

The recommendations proposed within this guidance are based on FDA's experience with reviewing a variety of AI-enabled devices, as well as current regulatory science research.

While the proposed recommendations are intended to be broadly applicable to AI-enabled devices, many of these recommendations may be specifically relevant to devices that incorporate the subset of AI known as machine learning, particularly deep learning and neural networks. Additional considerations may apply for other forms of AI.

This guidance is not intended to provide a complete description of what may be necessary to include in a marketing submission for an AI-enabled device. In particular, this guidance references sections of the FDA guidance titled "Content of Premarket Submissions for Device Software Functions" (hereafter referred to as "Premarket Software Guidance"), which includes significant additional considerations for AI-enabled devices, but does not include references to every section of that guidance. Additionally, this guidance does not address all of the data and information to be submitted in support of a specific indication for an AI-enabled device. FDA recommends that sponsors also refer to other guidances, as applicable to a particular device, for recommendations on other aspects of a marketing submission. Examples of relevant guidances for specific technologies include the FDA guidances titled "Technical Performance Assessment of Quantitative Imaging in Radiological Device Premarket Submissions" and "Technical Considerations for Medical Devices with Physiologic Closed-Loop Control Technology." FDA further encourages sponsors to consider other available resources including consensus standards and publicly available information when preparing their marketing submissions. As with all devices, FDA intends to take a risk-based approach to determining specific testing and applicable recommendations to support marketing submissions for AI-enabled devices.

Early engagement with FDA can help guide product development and submission preparation. In particular, early engagement could be helpful when new and emerging technology is used in the development or design of the device, or when novel methods are used during the validation of the device. FDA encourages sponsors to consider discussing these plans with FDA via the Q-Submission Program.

## III. TPLC Approach: General Principles

This guidance acknowledges the importance of a TPLC approach to the management of AI-enabled devices. In addition to recommendations regarding the documentation and information that should be included in marketing submissions, which reflect a comprehensive approach to the management of risk throughout the TPLC, the resources provided in this guidance are also intended to assist with the device development and lifecycle management of AI-enabled devices, which should help support the safety and effectiveness of these devices. This guidance provides both specific recommendations on the information and documentation to support a marketing submission for an AI-enabled device, as well as recommendations for the design, development, deployment, and maintenance of AI-enabled devices, including the performance management.

This guidance also includes FDA's current thinking on strategies to address transparency and bias throughout the TPLC of AI-enabled devices. These interconnected considerations are important throughout the TPLC and should be incorporated from the earliest stage of device design through decommission to help design transparency and the control of bias into the device and ensure its safety and effectiveness. Transparency involves ensuring that important information is both accessible and functionally comprehensible and is connected both to the sharing of information, and to the usability of a device. AI bias is a potential tendency to produce incorrect results in a systematic, but sometimes unforeseeable way, which can impact safety and effectiveness of the device within all or a subset of the intended use population (e.g., different healthcare settings, different input devices, sex, age, etc.). A comprehensive approach to transparency and bias is particularly important for AI-enabled devices, which can be hard for users to understand due to the opacity of many models and model reliance on data correlations that may not map directly to biologically plausible mechanisms of action. Recommendations for a design approach to transparency are provided in Appendix B (Transparency Design Considerations). With regards to the control of bias for AI-enabled devices this can include addressing representativeness in data collection for development, testing, and monitoring throughout the product lifecycle, as well as evaluating performance across subgroups of intended use.

Finally, this guidance includes recommendations that address the performance of AI-enabled devices throughout the TPLC, including in the postmarket setting. For example, AI-enabled devices can be sensitive to differences in input data (also referred to as data drift), such as input data used during development as compared to input data in actual deployments. Further, in addition to data drift, which occurs when systems that produce inputs for AI-enabled devices change over times in ways that may impact the performance of the device but may not be evident to users, AI-enabled devices can also be susceptible to changes in performance due to other factors. Sponsors are also encouraged to consider the use of a predetermined change control plan (PCCP), as discussed in FDA guidance titled "Marketing Submission Recommendations for a Predetermined Change Control Plan for Artificial Intelligence-Enabled Device Software Functions," which describes an approach for manufacturers to prospectively specify and seek premarket authorization for intended modifications to an AI-DSF (e.g., to improve device performance) without needing to submit additional marketing submissions or obtain further FDA authorization before implementing such modification consistent with the PCCP.

## IV. How to Use this Guidance: Overview of AI-Enabled Device Marketing Submission Content Recommendations

This guidance provides recommendations on the documentation and information that should be included in marketing submissions to support FDA's review of devices that include AI-DSFs.

There are some differences between the way FDA and the AI community consider the AI-enabled device TPLC and certain terminology. Therefore, this guidance clarifies these differences to facilitate better understanding of the recommendations in this guidance. For example, the AI community often uses the term "validation" to refer to data curation or model tuning that can be combined with the model training phase to optimize the model selection. However, validation is defined in 21 CFR 820.3(z) as "...confirmation by examination and provision of objective evidence that the particular requirements for a specific intended use can be consistently fulfilled." This guidance uses the definition in 820.3(z), specifically when addressing the evaluation of performance of the model for its intended use. For clarity, using the term "validation" to refer to the training and tuning process should be avoided in the context of medical device marketing submissions. Also, the term "development" is used throughout this guidance to refer to training, tuning, and tuning evaluation (often referred to as "internal testing" in the AI community). In this guidance, "test data" is used to refer to data that may be used for verification and validation activities, also known as the testing process, and is not used to describe part of the development process. The "FDA Digital Health and Artificial Intelligence Glossary – Educational Resource" provides a compilation of commonly used terms in the artificial intelligence and machine learning space and their definitions.

Sections V through XIII of this guidance describe the marketing submission content recommendations for AI-enabled devices. Specifically, in each section, under "*Why should it be included in a submission for an AI-enabled device*," an explanation is provided for why certain information should be included in a marketing submission. An explanation of what documentation and information should be included in a marketing submission can be found under "*What sponsors should include in a submission*." Finally, recommendations regarding where sponsors should include the information within each section of a marketing submission can be found under "*Where sponsors should provide it in a submission*." Information regarding lifecycle considerations as well as examples of marketing submission materials are provided in the appendices of this guidance.

The recommendations related to marketing submissions are organized according to how they should appear in the submission (See Appendix A (Table of Recommended Documentation)), which does not always align directly with the order of activities in the TPLC. While all referenced submission sections are provided to FDA during premarket review, they include information about what has already been done to develop and validate the device, as well as what a sponsor plans to do in the future to ensure a device's ongoing safety and effectiveness. Some sections of the guidance also describe information relevant to multiple steps in the TPLC. One example of how the sections in this guidance may align with the TPLC is included below:

- **Development** — Risk Assessment, Data Management, and Model Description and Development
- **Validation** — Data Management and Validation
- **Description of the Final Device** — Device Description, Model Description and Development, User Interface and Labeling, Public Submission Summary
- **Postmarket Management** — Device Performance Monitoring and Cybersecurity

This guidance generally describes information that would be generated and documented during software development, verification, and validation. However, the information necessary to support market authorization will vary based on the specifics of each AI-enabled device, and during premarket review FDA may request additional information that is needed to evaluate the submission.

### A. Quality System Documentation

When considering the recommendations in Sections V through XIII of this guidance, it may be helpful to consider if the documentation and information that should be included in a marketing submission, under "*What sponsors should include in a submission*," could exist in the Quality System documentation. One source of documentation that may be used as part of demonstrating substantial equivalence or reasonable assurance of safety and effectiveness in the marketing submission for certain AI-enabled devices is documentation related to the ongoing requirements of the Quality System (QS) Regulation. This guidance explains how some documentation that may be relevant for QS regulation compliance for medical devices generally can also be provided premarket to demonstrate how a sponsor or manufacturer is addressing risks associated with AI-enabled devices specifically.

For example, the QS Regulation requires that manufacturers establish design controls for certain finished devices (see 21 CFR 820.30). Specifically, as part of design controls, a manufacturer must "establish and maintain procedures for validating the device design," which "shall ensure that devices conform to defined user needs and intended uses and shall include testing of production units under actual or simulated use conditions" (21 CFR 820.30(g)). In addition, under 21 CFR 820.30(i) a manufacturer must establish and maintain procedures to identify, document, validate or where appropriate verify, review, and approve of design changes before their implementation ("design changes") for all devices, including those with automated software. Similarly, as part of the control of nonconforming product, manufacturers must establish and maintain procedures to "control product that does not conform to specified requirements," including, under some circumstances, user requirements, and to implement corrective and preventative action, including "complaints" and "other sources of quality data" to identify "existing and potential causes of nonconforming product." (21 CFR 820.90(a) and 820.100(a)(1)). Further, manufacturers have ongoing responsibility to manage and maintain device quality, including by reviewing the "suitability and effectiveness of the quality system at defined intervals and with sufficient frequency according to established procedures" to ensure the quality objectives are being met.

## V. Device Description

*Why should it be included in a submission for an AI-enabled device:* The following section describes information that sponsors should provide in the device description section of their marketing submission to help FDA understand the general characteristics of the AI-enabled device. The following recommendations supplement device-specific recommendations and recommendations provided in the Premarket Software Guidance, where applicable.

The device description supports FDA's understanding of the intended use, expected operational sequence of the device (e.g., clinical workflow), use environment, features of the model, and design of the AI-enabled device. This information is needed for FDA to evaluate the safety and effectiveness of the device. The device description provides important context about what the device does, including how it works, how a user may interact with it, and under what circumstances a device is likely to be used as intended.

*What sponsors should include in a submission:* In general, sponsors should include the following types of information as part of a device description for an AI-enabled device:

- A statement that AI is used in the device.
- A description of the device inputs and device outputs, including whether the inputs are entered manually or automatically, and a list of compatible input devices and acquisition protocols, as applicable.
- An explanation of how AI is used to achieve the device's intended use. For devices with multiple functions, this explanation may include how AI-DSFs interact with each other as well as how they interact with non-AI-DSFs.
- A description of the intended users, their characteristics, and the level and type of training they are expected to have and/or receive. Users include those who will interpret the output. When relevant, list the qualifications or clinical role of the users intended to interpret the output. Users also include all people who interact with the device including during installation, use, and maintenance.
- A description of the intended use environment(s) (e.g., clinical setting, home setting).
- A description of the intended workflow for the use of the device (e.g., intended decision-making role), including:
  - A description of the degree of automation of the device provides in comparison to the workflow for the current standard of care;
  - A description of the clinical circumstances that may lead to use; and
  - An explanation of how the outputs will be used in the clinical workflow.
- A description of installation and maintenance procedures.
- A description of any calibration and/or configuration procedures that must be regularly performed by users in order to maintain performance, including when calibration must be performed and how users can identify if calibration is needed again or is incorrect, as applicable.

Additionally, sponsors should include the following types of information as part of a device description for an AI-enabled device that has elements that can be configured by a user:

- A description of all configurable elements of the AI-enabled device, for example:
  - Visualizations that the user can turn on/off (e.g., overlays, quality indicators, or heatmaps);
  - Software inputs;
  - Model parameters when they are configured during use; and/or
  - Alert thresholds.
- A description of how these elements and their settings can be configured, including:
  - A description of the users who make configuration decisions (e.g., clinical user, administrative user, patient) including any necessary qualifications and training needed to make these decisions, as applicable;
  - An explanation of how users know which selections have been made;
  - A description of the level at which the configuration is defined, for example at the patient-, clinical site- or hospital network-level; and
  - A description of customizable pre-defined operating points, their outputs and performance ranges, as applicable. It is also important to specify how the operating points or operating point range(s) were selected based on the indications for use of the device.
- A description of the potential impact of the configurable elements on user decision making.

Finally, if a device contains multiple connected applications with separate interfaces, the device description should address all applications in the device. Sponsors may also wish to consider enhancing the device description with the use of graphics, diagrams, illustrations, screen captured images, or video demonstrations, including screen captured video.

*Where sponsors should provide it in a submission:* The AI-enabled device description information should be included in the "**Device Description**" section of the marketing submission.

## VI. User Interface and Labeling

The user interface includes all points of interaction between the user and the device, including all elements of the device with which the user interacts (e.g., those parts of the device that users see, hear, touch). It also includes all sources of information transmitted by the device (including packaging and labeling), training, and all physical controls and display elements (including alarms and the logic of operation of each device component and of the user interface system as a whole), as applicable. A user interface might be used throughout many phases of installation and use, such as while the user sets up the device (e.g., unpacking, set up, calibration), uses the device, or performs maintenance on the device (e.g., cleaning, replacing a battery, repairing parts). One way to help support the safety and effectiveness of the device for users is to design the user interface such that important information is provided throughout the course of use, to ensure that the device conforms to defined user needs. An approach that integrates important information throughout the user interface may help ensure that device users have access to information at the right time and in the right location to support safe and effective use, consistent with the intended use of the device. For software or mobile applications, manufacturers may leverage the user interface elements, such as information on the screen or alerts sent to other products, in addition to device labeling, to communicate risks about the device so that the necessary information is provided at the right time.

It is important to provide a holistic understanding of the user interface in a marketing submission to support the agency's understanding of how the device works. If a sponsor references the user interface design in their risk analysis or another section of the submission to control risks, inclusion of the user interface may also support explanations of those risk controls. However, the actual analysis of the efficacy of risk control should be located separately from the description of the user interface. Further information on this topic is described in Section VII (Risk Assessment) and Appendix D (Usability Evaluation Considerations).

With regard to labeling specifically, a device user interface includes, but is not limited to, labeling. Further, within the user interface, labeling is subject to specific regulations. For example, depending on whether the device is for prescription-use or not, manufacturers are required to provide labeling containing adequate directions for use that would ensure that a layman or, for prescription devices, a practitioner licensed by law to administer the device, "can use a device safely and for the purposes for which it is intended." One way to satisfy these requirements for AI-enabled devices could be to provide, in the labeling, clear information about the model, its performance characteristics, and how the model is integrated into the device. For example, users may need to know specific information about the model, such as the nature of the data on which the model was trained. These technical characteristics can be critical to the safe and effective use of the device because they can support a user's understanding of how the device should be expected to perform, and what factors may impact performance.

The following sections further detail recommended information on the user interface (Section VI.A), and the labeling (Section VI.B), that should be provided in a marketing submission to support FDA's understanding of what is communicated to users and the elements of the device with which the users interact.

Appendix B (Transparency Design Considerations) of this guidance outlines a recommended approach to transparency, including examples of types of information, modes of communication, and communication styles that may be helpful to consider when designing the user interface (including labeling) of an AI-enabled medical device. It may also be helpful to integrate a model card in the device labeling to clearly communicate information about an AI-enabled device (see Appendix E (Example Model Card)).

Note that inclusion of a unique device identifier (UDI) in the labeling is required for devices, including AI-enabled devices, that are subject to UDI requirements. A new UDI is required when there is a new version and/or model, and for new device packages.

### A. User Interface

*Why should it be included in a submission for an AI-enabled device:* It is important for FDA to understand the device's user interface, in order to understand how the device is used. The user interface can convey important information about what the device is intended to do, and how users are intended to interact with it. Seeing the user interface can help FDA understand how the device will be operated and how it will fit into the clinical workflow, which can support the review of a device and help the agency determine whether it is safe and effective.

A representation of the user interface can also serve to support the sponsor's risk assessment and other documentation when the user interface is referenced as an element of those sections. For example, the user interface can communicate important information to users that supports safe and effective use of the device, and the user interface design may play a crucial role in controlling or eliminating risks associated with not knowing or misunderstanding information that is critical to the safe and effective use of the device. While not required, if a sponsor chooses to use elements of the user interface as part of risk control in the risk assessment, the inclusion of the user interface can help further facilitate review. Further information on this topic is described in Section VII (Risk Assessment) and Appendix D (Usability Evaluation Considerations).

While the user interface does include the printed labeling (e.g., packaging and user manuals) and all elements of the user interface should be designed to collectively support the user's understanding of how to use the device, sponsors should submit labeling separately as described in Section VI.B (Labeling). This section describes how sponsors should provide FDA with an understanding of the remaining elements of the user interface.

*What sponsors should include in a submission:* Sponsors should provide information about and descriptions of the user interface that makes clear the device workflow, including the information that is provided to users, when the information is provided, and how it is presented. Possible methods to provide this type of information about the user interface include:

- A graphical representation (e.g., photographs, illustrations, wireframes, line drawings) of the device and its user interface. This may include a depiction of the overall device and all components of the user interface with which the user will interact (e.g., display and function screens, alarm speakers, controls).
- A written description of the device user interface.
- An overview of the operational sequence of the device and the user's expected interactions with the user interface. This may include the sequence of user actions performed to use the device and resulting device responses, when appropriate.
- Examples of the output format, including example reports representing a range of expected outcomes.
- A demonstration of the device, for example by providing a recorded video.

*Where sponsors can provide it in a submission:* The user interface information should be included in the "**Software Description**" in the Software Documentation section of the marketing submission.

### B. Labeling

*Why should it be included in a submission for an AI-enabled device:* A marketing submission must include labeling information in sufficient detail to help FDA determine that the proposed labeling satisfies applicable requirements for the type of marketing submission. Device labeling must satisfy all applicable FDA labeling requirements, including, but not limited to, 21 CFR Part 801, as discussed above. This section of the guidance includes labeling considerations for AI-enabled devices to support compliance with these requirements.

*What sponsors should include in a submission:* The labeling for an AI-enabled device should address the following types of information in a format and at a reading level that is appropriate for the intended user (e.g., considering characteristics such as age, education or literacy level, sensory or physical impairments, or occupational specialty) to help ensure users can quickly access important information. Tables and graphics may be used to communicate this information.

**Inclusion of AI:**
- Statement that AI is used in the device.
- Explanation of how AI is used to achieve the device's intended use.
  - For devices with multiple functions, this explanation may include how AI-DSFs interact with each other as well as how they interact with non-AI DSFs.

**Model Input:**
- Description of the model inputs (e.g., signals or patterns acquired from other compatible devices, images from an acquisition system (e.g., MRI), or patient-derived samples, which can be input manually or automatically). Related aspects to consider include:
  - For systems incorporating inputs from an electronic interface, information on the necessary system configuration to ensure the inputs are consistent with the design and validation of the AI-enabled device.
  - For systems that require input from other medical devices (e.g., an x-ray device), a list of the specific compatible devices or device specification, along with the acceptable acquisition protocols, as applicable.
  - For systems in which the loss of model inputs may prevent the AI-enabled device from generating an output, an explanation of the potential impact of the lost inputs on the performance of the AI-enabled device.
- Instructions on any steps the user is expected to take to prepare input data for processing by the device, including any expected characteristics (e.g., functional capabilities, experience and knowledge levels, and level of training) of those performing these steps. This information should be consistent with the intended use that was studied in the device validation.

**Model Output:**
- Explanation of what the model output means and how it is intended to be used.

**Automation:**
- Explanation of the intended degree of automation the device exhibits.

**Model Architecture:**
- High level description of the methods and architecture used to develop the model(s) implemented in the device.

**Model Development Data:**
- Description of the development data, including:
  - The source(s) of data;
  - Study sites;
  - Sample size;
  - Demographic distributions; and
  - Criteria/expertise used for determining clinical reference standard (ground truth).

**Performance Data:**
- Description of the performance validation data, including:
  - The source(s) of data;
  - Study sites;
  - Sample size;
  - Other important study design and data structure information (e.g., randomization schemes, repeated measurements, clinical reference standard);
  - Primary endpoints of the validation study, including pre-specified performance criteria; and
  - Criteria/expertise used for determining clinical reference standard data.

**Device Performance Metrics:**
- Description of the device performance metrics.
  - An example of performance metrics may include metrics such as the area under the receiver operating characteristic curve (AUROC), sensitivity and specificity, true/false positive and true/false negative counts (e.g., in a confusion matrix), positive/negative predictive values (PPV/NPV), and positive/negative diagnostic likelihood ratios (PLR/NLR). All performance estimates should be provided with confidence intervals.
- Explanation of the device performance across important subgroups. Generally, subgroup analysis by patient characteristics (e.g., sex, age, race, ethnicity, disease severity), geographic sites, and data collection equipment are appropriate.
- Description of the corresponding performance for different operating points, including subgroup analysis for each operating point, as applicable.

**Performance Monitoring:**
- Description of any methods or tools to monitor and manage device performance, including instructions for the use of such tools, as applicable when ongoing performance monitoring and management by the user is considered necessary for the safe and effective use of the device.

**Limitations:**
- Description of all known limitations of the AI-enabled device, AI-DSF(s), or model(s).
  - Some limitations of a model may not reach the degree of severity that would warrant a contraindication, warning, or precaution, but they may still be important to include in labeling. For example, the training dataset may have only included a few patients with a rare presentation of a disease or condition; users may benefit from knowing the limitations of the data when that rare presentation is suggested by the model as a diagnosis.

**Installation and Use:**
- Information about the installation and implementation instructions, including:
  - Instructions on integrating the AI-enabled device into the site's data systems and clinical workflow; and
  - Instructions for ensuring that any input data are compatible and appropriate for the device.
    - Terms may need to be explicitly defined. For example, a healthcare system and a manufacturer may both have data labeled as "sex," but one may be using sex at birth while the other may be using self-reported sex.

**Customization:**
- Description of and instructions on any customizable features, including:
  - When users or healthcare systems can configure the operating points for the device;
  - When it is appropriate to select different configurations; and
  - When operating points are configurable, how end users can discern the operating point the device is currently operating at.

**Metrics and Visualizations:**
- Explanation of any additional metrics or visualizations used to add context to the model output.

**Patient and Caregiver Information:**
For AI-enabled devices intended for use by patients or caregivers, manufacturers should provide labeling material that is designed for patients and caregivers describing the instructions for use, the device's indication, intended use, risks, and limitations. Patients and caregivers are considered users if they will operate the device, interpret the outcome, or make decisions based on the outcome, even if they are not the only user or the primary operator of the device. This material should be at an appropriate reading level for the intended audience. If patient and caregiver-specific material is not provided, sponsors should provide an explanation of how patients and caregivers will understand how to use the device, including how to make decisions about whether to use the device and how to use the output of the device.

*Where sponsors should provide it in a submission:* Information regarding the AI-enabled device labeling should be included in the "**Labeling**" section of the marketing submission.

> **ADDITIONAL RESOURCES:**
> - Appendix B (Transparency Design Considerations) outlines a potential approach to understanding a device's indications for use and a model card, which may aid in the development of the user interface.
> - While model cards are not required for presenting information about the labeling or user interface, they may be a helpful tool to organize information. In general, model cards can be adapted to the specific needs and context of each AI-enabled device.
>   - Appendix E (Example Model Card) includes an example of a basic model card format intended for users and healthcare providers that conveys information including a summary of the model's intended use and intended users, and evidence supporting safety and effectiveness.
>   - Appendix F (Example 510(k) Submission Summary with Model Card) includes an example of a completed basic model card.
> - FDA's guidance titled "Device Labeling Guidance #G91-1 (Blue Book Memo)" includes suggestions regarding what information should be included within device labeling.

## VII. Risk Assessment

*Why should it be included in a submission for an AI-enabled device:* A comprehensive risk assessment helps ensure the device is safe and effective. When included in a marketing submission, a comprehensive risk assessment helps FDA understand whether appropriate risks have been identified and how they are controlled. In Section VI.C of the Premarket Software Guidance, FDA recommends that marketing submissions that include device software functions include a risk management file composed of a risk management plan, a risk assessment, and a risk management report. Consistent with this, marketing submissions of AI-enabled devices should include a risk management file that takes into account the recommendations of Premarket Software Guidance and the recommendations of this guidance, in addition to any other applicable guidance.

Sponsors should also refer to the FDA-recognized version of ANSI/AAMI/ISO 14971 *Medical devices - Applications of risk management to medical devices* for additional information on the development and application of a risk management file, which is also applicable to AI-enabled devices. FDA also recognizes that AI-enabled devices can be associated with new or different risks than device software functions generally. Therefore, FDA also recommends that sponsors incorporate the considerations outlined in the FDA-recognized voluntary consensus standard of AAMI CR34971 *Guidance on the Application of ISO 14971 to Artificial Intelligence and Machine Learning*, which is specific to AI-enabled devices.

**Risks Across the TPLC:** When conducting a risk analysis, manufacturers are expected to identify possible hazards associated with the design in both normal and fault conditions. The risks associated with the hazards, including those resulting from user error, should then be calculated in both normal and fault conditions. If any risk is judged unacceptable, it should be reduced to acceptable levels by the appropriate means. This risk assessment should take into account all users, as described in Section VI (User Interface and Labeling) of this guidance, across the TPLC. FDA recommends that manufacturers follow this approach for AI-enabled devices across their TPLC.

**Risks Related to Information in AI-Enabled Devices:** One aspect of risk management that can be particularly important for AI-enabled devices is the management of risks that are related to understanding information that is necessary to use or interpret the device, including risks related to lack of information or unclear information. Misunderstood, misused, or unavailable information can impact the safe and effective use of a device. For example, for devices that utilize complex algorithms, including AI-enabled devices, the performance in different disease subtypes may not be apparent to users, or the logic underlying the output information may not be easily understandable, which can negatively affect user understanding and use of the device. Lack of, or unclear information can also make it difficult for different users to know whether a device is not performing as expected, or how to correctly follow instructions. FDA recommends that consideration of risks related to understanding information should be one part of a comprehensive approach to risk management for an AI-enabled device.

*What sponsors should include in a submission:* Sponsors should provide a "Risk Management File" that includes a risk management plan, a risk assessment. In addition to other considerations, the risk assessment should consider user tasks and knowledge tasks that occur throughout the full continuum of use of the device, including, for example, the process of installing the device, maintaining performance over time, and any risks associated with user interpretation of the results of a device, as appropriate.

In addition to the considerations provided in FDA-recognized voluntary consensus standards and applicable guidances, FDA recommends that sponsors consider the risks related to understanding information during the risk assessment. As with all identified risks, sponsors should provide an explanation of any risk controls, including elements of the user interface, such as labeling, that address the identified risks. Information that may be helpful to discuss such risks and their controls, as applicable, is provided in Appendix D (Usability Evaluation Considerations).

*Where sponsors should provide it in a submission:* Much of the information on risk assessment for an AI-enabled device should be included in the "**Risk Management File**" in the Software Documentation section of the marketing submission, as recommended by the Premarket Software Guidance.

## VIII. Data Management

*Why should it be included in a submission for an AI-enabled device:* For an AI-enabled device, the model is part of the mechanism of action. Therefore, a clear explanation of the data management, including data management practices (i.e., how data has been or will be collected, processed, annotated, stored, controlled, and used) and characterization of data used in the development and validation of the AI-enabled device is critical for FDA to understand how the device was developed and validated. This understanding helps to enable FDA's evaluation of an AI-enabled device's safety and effectiveness.

The performance and behavior of AI systems rely heavily on the quality, diversity, and quantity of data used to train and tune them. The accuracy and usefulness of a validation of an AI-enabled device also depends on the quality, diversity, and quantity of data used to test it. Thus, FDA reviewers evaluate data management in order to understand whether an AI-enabled device is safe and effective. This includes the alignment of the collection and management of training and test data with the intended use and resulting device requirements.

Data management is also an important means of identifying and mitigating bias. The characterization of sources of bias is necessary to assess the potential for AI bias in the AI-enabled device. AI bias is a potential tendency to produce incorrect results in a systematic, but sometimes unforeseeable, way due to limitations in the training data or erroneous assumptions in the machine learning process. AI bias has been well-documented. For example, during training, models can be over-trained to recognize features of images that are unique to specific scanners, patient subpopulations, or clinical sites but have little to do with generalizable patient anatomy, physiology, or condition, which can lead to AI bias in the resulting model. In another example, underrepresentation of certain populations in datasets could lead to overfitting (i.e., data fitting too closely to the potential biases of the training data) based on demographic characteristics, which can impact the AI-enabled device performance in the underrepresented population.

Using unbiased, representative training data for models promotes generalizability to the intended use population and avoids perpetuating biases or idiosyncrasies from the data itself.

The inclusion of representative data in validation datasets may be important, because underrepresentation may impact the ability to identify any performance problems, including understanding performance in underrepresented populations. Although bias may be difficult to eliminate completely, FDA recommends that manufacturers, as a starting point, ensure that the validation data sufficiently represents the intended use (target) population of a medical device.

To objectively assess the device performance, it is also important for FDA reviewers to understand whether the test data are independent (e.g., sampled from completely different clinical sites) from the training data and are sequestered from the model developers and the model development stage. Appropriate separation of the development and test datasets can help with evaluating the true performance of an AI-enabled device. Data leakage between the validation and development datasets can create uncertainty regarding the true performance of the AI-enabled device.

*What sponsors should include in a submission:* In a submission, a sponsor should provide the following types of information for both the training and testing data, in the appropriate marketing submission sections. It may be helpful to organize data management information by the sections described below. Generally, information on data collection, development and test data independence, reference standards, and representativeness should be provided. Sponsors should also explain any differences in the data management approach and the characteristics of the data between the development and validation phases. The submission should include an explanation for the differences and justification for them.

**Data Collection:**
- A description of how data were collected (e.g., clinical study protocols with inclusion/exclusion criteria), including:
  - The names of clinical sites or institutions involved (sites should be uniquely identified and consistently referred to throughout the submission)
  - The time period during which the data were acquired
  - If data were used from a pre-existing database, the appropriateness of the use of this database
  - If real-world data (RWD) are used, the source and collection of this evidence. FDA encourages sponsors to leverage the Q-Submission Program for obtaining FDA feedback on proposed uses of RWD.
- A description of the limitations of the dataset
- A description of the quality assurance processes related to the data
- A description of the size of each data set
- A description of the mechanisms used to improve diversity in enrollment within the scope of the study
- A description of the use of synthetic data (if applicable), accompanied by a comprehensive explanation of how the data were generated and why they are fit-for-purpose

**Data Cleaning/Processing:**
To provide optimum training results, it may be important to clean data used for development, such as by removing incorrect, duplicate, or incomplete data. These processing steps should be described, including data quality factors used, data inclusion/exclusion criteria, treatment of missing data, and whether the steps are internal or external to the AI-DSF.

Testing data, on the other hand, should only be processed in a manner that is representative of the RWD the model will encounter in its intended use. Any such data processing, data quality factors used, data inclusion/exclusion criteria, and treatment of missing data should be justified as aligned with pre-processing implemented in the final AI-DSF.

**Reference Standard:**
For the purposes of this guidance, a reference standard is the best available representative truth that can be used to define the true condition for each patient/case/record. It is possible that a reference standard may be used in device training, device validation, or both. A reference standard is validated by evidence from current practice within the medical and regulatory communities for establishing a patient's true status with respect to a clinical task. The reference standard should reflect the clinical task. Clinical tasks may consist of, for example, classification of a disease or condition, segmentation of contours on medical images, detection by bounding boxes, or localization by markings. The following types of information should be provided regarding the selected reference standard:

- A description of how the reference standard was established
- A description of the uncertainty inherent in the selected reference standard
- A description of the strategy for addressing cases where results obtained using a reference standard may be equivocal or missing
- If the reference standard is based on evaluations from clinicians, provide:
  - The grading protocol used
  - What data are provided to these clinicians
  - How the clinicians' evaluations are collected/adjudicated for determining the clinical reference standard, including: blinding protocol; and number of participating clinicians and their qualifications
  - An assessment of the intra- and/or inter-clinician variability for each task, as applicable, as well as an assessment on whether the observed variability is within commonly accepted standards for a particular measurement task

**Data Annotation:**
- When data annotation is used, the following types of information should be provided regarding the data annotation approach:
  - A description of the expertise of those performing the data annotation
  - A description of the specific training, instructions or guidelines provided to data annotators to guide their annotation decisions, including whether annotators are blinded to each other
  - A description of the methods for evaluating quality/consistency of data annotations and adjudicating disagreements (consensus evaluation, sampling). FDA recommends the use of independent assessments by each annotator, without knowledge of the other annotators' decisions, to ensure objective high-quality data annotations
  - A detailed plan for addressing incorrect data annotation

**Data Storage:**
A description of the data storage of both training and test data. The description should address dataset version control and should ensure the security of the data by addressing the items described in Section XII (Cybersecurity) of this guidance.

**Management and Independence of Data:**
- A description of the development data, including how the development data were split into training, tuning, tuning evaluation, and any additional subsets, and specification of which model development activities were performed using each dataset
- A description of the controls in place to ensure the data used for testing is sequestered from the development process
- A justification of why the data used for validation provides a robust external validation. For example, a description of the sites from which test data originates from, because, in general, test data should come from sites different from those used to develop the AI-DSF

**Representativeness:**
- An explanation of how the data is representative of the intended use population and indications for use, including:
  - A description of the relevant population characteristics, when available, including:
    - Disease conditions (e.g., positive/negative cases, disease severity, disease subtype, comorbidities, distribution of the disease spectrum)
    - Patient population demographics (e.g., sex, age, race, ethnicity, height, weight)
    - Data acquisition equipment and conditions (e.g., locations at which data are collected, data acquisition devices/methods, imaging and reconstruction protocols), including any factors that may impact signals analyzed during data acquisition
    - Test data collection sites (e.g., clinical sites, institutions). Generally, while a single data collection site may be a useful starting point during initial data assessment phases, reliance on a single site is generally not appropriate for understanding whether the data are representative of the intended use population and indications for use. The use of multiple data collection sites, such as sites in diverse clinical practice settings may assure a more representative sample of the intended use population. For example, the use of at least three geographically diverse US clinical sites (or health care systems) may be appropriate to clinically validate an AI-enabled device
  - A characterization of the distribution of data along important covariates, including those corresponding to the population characteristics described above
  - If any of the relevant population characteristics above were not available for the data, an explanation of why, and a justification of the use of the data without this information
  - A subgroup analysis or analyses stratified by the identified covariates
  - If OUS data are used during validation, an explanation regarding how the data compares to the U.S. population and U.S. medical practice in terms of general medical practice, disease presentation, prevalence, and progression as well as the demographic characteristics of patients. Due to the data-driven nature of typical models and the obscurity of their algorithms, their generalized performance on the U.S. target population may not be adequately captured in the clinical study if a significant portion of the validation data are OUS data. AI-enabled devices may also be more sensitive than traditional medical devices to the idiosyncratic patterns in the training or test data. For these reasons, they may require higher proportion of U.S. data in the clinical validation. FDA encourages sponsors to leverage the Q-Submission process for obtaining FDA feedback on proposed uses of OUS data

*Where sponsors should provide it in a submission:* The data management information for data used in the development of the model should be included in the "**Software Description**" in the Software Documentation section of the marketing submission, as described in the Premarket Software Guidance.

The data management information for data used in the performance validation (i.e., clinical validation) documentation should be included in the "**Performance Testing**" section of the marketing submission. When the characteristics of data used for model training and validation differ, sponsors should highlight and justify the differences along with the performance validation data management section in the performance testing documentation element.

## IX. Model Description and Development

*Why should it be included in a submission for an AI-enabled device:* Information about the model (and device) design, including its biases and limitations, supports FDA's ability to assess the safety and effectiveness of an AI-enabled device and determine the device's performance testing specifications.

Section VI.B of the Premarket Software Guidance describes information that should be included as part of a software description in a marketing submission, including the model description. Whereas the device description is broader and provides information about the whole device, how users interact with it, and how it fits into the clinical workflow, the model description, as part of the software description, specifically provides detailed information about the technical characteristics of the model(s) themselves and the algorithms and methods that were used in their development. This information helps FDA understand the basis for the functionality of an AI-enabled device. Understanding the methods used to develop the model also helps FDA identify potential limitations, sources of AI bias, and considerations for appropriate device labeling.

*What sponsors should include in a submission:* In a submission, sponsors should include the information described below for each model in the AI-enabled device.

In situations where multiple models are employed as part of the AI-enabled device, it can be particularly helpful to include a diagram of how model outputs combine to create the device outputs. The description of the algorithms and models should be sufficiently detailed to enable a competent AI practitioner to produce an equivalent model. The use of diagrams in addition to textual descriptions is encouraged to enhance clarity.

**Model Description:**
- An explanation of each model used as part of the AI-enabled device, including but not limited to:
  - Model inputs and outputs;
  - A description of model architecture;
  - A description of features;
  - A description of the feature selection process and any loss function(s) used for model design and optimization, as appropriate; and
  - Model parameters.
- In situations where the AI-enabled device has customizable features involving the model, such as being customizable to operate at multiple pre-defined operating points or with a variable number of inputs, a description of the technical elements of the model that allow for and control customization.
- A description of any quality control criteria or algorithms, including AI-based and third-party ones, for the input data, including how the quality assessment metrics align with the intended use of the device (intended patient population and use environment).
- A description of any methods applied to the input and/or output data, including:
  - Pre-processing of input data (e.g., normalization);
  - Post-processing of output data; and
  - Data augmentation or synthesis.

**Model Development:**
- A description of how the model was trained, including but not limited to:
  - Optimization methods;
  - Training paradigms (e.g., supervised, unsupervised or semi-supervised learning, federated learning, active learning);
  - Regularization techniques employed;
  - Training hyperparameters (e.g., the loss function learning rate) as applicable; and
  - Summary training performance such as the loss function convergence curves for the different data subsets (such as training, tuning, tuning evaluation).
- If tuning evaluation was conducted, a description of the metrics and results obtained.
- An explanation of any pre-trained models that were used, as applicable.
  - If a pre-trained model was used, specify the dataset that was used for pre-training and how the pre-trained model was obtained.
- A description of the use of ensemble methods (e.g., bagging or boosting), as applicable.
- An explanation of how any thresholds (e.g., operating points) were determined.
- An explanation of any calibration of the model output.

*Where sponsors should provide it in a submission:* Information on model development, including the model description, and the method for model development, should be included as part of the "**Software Description**" in the Software Documentation section of the marketing submission, as described in the Premarket Software Guidance.

## X. Validation

For an AI-enabled device, validation includes ensuring that the device, as utilized by users, will perform its intended use safely and effectively, as well as establishing that the relevant performance specifications of the device can be consistently met. For AI-enabled devices, manufacturers should demonstrate users' ability to interact with and understand the device as intended in addition to ensuring the device itself meets relevant performance specifications. To this end, it can be helpful to consider both performance validation (including human factors validation) and an evaluation of usability. Note that, for the purposes of this guidance (in the context of risk controls in the absence of human factors validation), usability describes whether the device can be used safely and effectively by the intended users, including whether users consistently and correctly receive, understand, interpret, and apply information related to the AI-enabled device.

Together, performance validation and human factors validation (or an evaluation of usability as appropriate) help provide FDA with information about how the device may be used and perform under real world circumstances. Performance validation may employ a variety of testing and monitoring methods to evaluate the statistical performance of the model under testing conditions, and human factors validation testing involves understanding how various users are likely to use a device in context. In other words, performance validation is meant to provide confirmation that device specifications conform to user needs and intended uses, and that performance requirements implemented can be consistently fulfilled, while human factors validation and an evaluation of usability are meant to specifically address whether all intended users can achieve specific goals while using the device and whether users will be able to consistently interact with the device safely and effectively.

**Software Version History:** Section VI.I of the Premarket Software Guidance describes information that should be included as part of a software description in a marketing submission, including information regarding the software version history. For AI-enabled devices, the software version history includes consideration of the model version and any differences between the tested version of the model and the released version, along with an assessment of the potential effect of the differences on the safety and effectiveness of the device. It is important for FDA to understand what version of the model was tested in order to ensure that all validation activities will be objective, and the model has not been adjusted opportunistically in light of the test data (i.e., post-hoc adjustment) without the Agency's concurrence.

New unique device identifiers (UDIs) are required for devices that are required to bear a UDI on its label when there is a new version and/or model, and for new device packages.

### A. Performance Validation

*Why should it be included in a submission for an AI-enabled device:* The performance validation for an AI-enabled device provides objective evidence that the device performs predictably and reliably in the target population according to its intended use. The following recommendations are intended to supplement device-specific recommendations and recommendations provided in other FDA guidances where applicable, including "Design Considerations for Pivotal Clinical Investigations for Medical Devices," "Statistical Guidance on Reporting Results from Studies Evaluating Diagnostic Tests," and "Electronic Source Data in Clinical Investigations."

As part of FDA's evaluation of safety and effectiveness of the device, it is important for FDA to understand how the device performs overall in the intended use population, as well as in subgroups of interest. Acceptable performance in certain subgroups may mask lower performance in other subgroups when the evaluation is performed only for the total population. Poor performance in specific subgroups could make the device unsafe for use in those groups, which may impact the potential scope of the intended use population. Section VIII (Data Management) outlines why stratification and analyses of subgroups of interest is important to FDA's evaluation of safety and effectiveness. An analysis of subgroup performance that supports safe and effective use across the expected intended use population also helps to ensure that devices can be used for all intended patients.

While differential performance across subgroups is not unique to AI-enabled devices, the reliance of models on relationships learned from large amounts of data, and the relative opacity of models to users make AI-enabled devices particularly susceptible to unexpected differences in performance. Even when the data used to develop the model is representative during training, models can be over-trained to recognize features of data that are unique to specific characteristics of the study dataset but may be spurious to the identification or treatment of the disease or condition. Spurious learnings could impact performance differentially across characteristics of interest such as disease subtype or patient demographics, especially when data from study participants from different groups tend to be collected at different sites.

Information on the uncertainty of device outputs is also important because it helps reviewers understand how to interpret device outputs. When not specified for a device type in statute, regulation, or guidance, repeatability and/or reproducibility studies can still help FDA understand and quantify the uncertainty associated with device outputs when provided.

Appendix C (Performance Validation Considerations) of this guidance includes additional recommendations for some common approaches to performance validation. In addition, FDA encourages sponsors to leverage the Q-Submission Program for obtaining FDA feedback on proposed approaches to AI-enabled device development and validation. In particular, early engagement could be helpful to discuss the use of RWD, the use of new and emerging study methods, or the validation of new technologies.

**Assessing the Performance of the Human-Device Team:** It is important for sponsors to consider the interactions between users and the device when identifying the appropriate methods for performance testing. In the document, "Good Machine Learning Practice: Guiding Principles," Principle Seven discusses placing focus on "the performance of the Human-AI Team." This principle explains that it is important to understand the performance of the "Human-AI team, rather than just the performance of the model in isolation" when a model has a "human in the loop." The intended use and clinical workflow of AI-enabled devices span a continuum of decision-making roles from more autonomous systems to supportive (aid) tools that assist specific users, but rely on the human to interpret the AI outputs and ultimately make clinical decisions.

As the device moves along this spectrum, the nature of the clinical study or other studies (e.g., human factors validation testing) that would be appropriate to support performance evaluation of an AI-based medical device will vary according to the intended use of the model. For some devices, more emphasis may be placed on the model's standalone performance (i.e., Did the actual output match the expected output?). For others, a focus may be assessing the performance of the human-AI team, beyond just the performance of the model in isolation (i.e., Did the intended user working with the new device perform the same or better than the operator alone or with another device?). Sponsors should consider that, in certain scenarios, both standalone and human-device team performance evaluations may support the overall performance evaluation of the AI-enabled device.

*What sponsors should include in a submission:* The validation testing should provide objective information to characterize the model performance with respect to the intended use. A validation assesses the model's performance on independent datasets. Assessing the robustness of the model to anticipate reasonably foreseeable changes in input data and conditions of use should also be included, as appropriate, based on risk associated with these changes.

Validation methods differ depending on the intended use of a device. For example:

- Devices estimating defined measurements otherwise performed by accepted reference methods may need a precision study to adequately assess their repeatability and reproducibility.
- Devices monitoring time-series patient data and needing periodic re-calibrations may need a stability study and a change tracking study to assess their dynamic responses.
- Devices similar to survey instruments measuring less well-defined patient parameters may need additional evidence of construct validity (i.e., the extent to which a test measures what it is proposed to measure).
- Prognostic clinical decision support devices may need longitudinal data with survival analysis, calibration analysis, and/or discrimination analysis (e.g., risk stratification analysis), among other methods.

Depending on the specific AI-enabled device, this evidence could come from non-clinical bench or analytical studies, pre-clinical animal studies, clinical performance studies, clinical outcome studies, or some combination thereof.

**Study Protocols:** To support performance validation, sponsors should include information regarding all study protocols including statistical analysis plans. The statistical analysis plans should include study design and analysis details. Important aspects for these documents to cover include:

- Study design details, including:
  - A study design description (e.g., prospective, comparative study design with a sufficient statistical power to demonstrate the key clinical performance metric)
  - For a prospective study, procedures and methods that will be followed, a description of the operators involved in these procedures and methods, and any tools or equipment to be used
  - For a retrospective study, plans on how to handle, prepare, process, and select archived data or material
  - A description of the data recording mechanisms that will be used to record the version or state of the AI-enabled device used during the study for a given patient. To ensure accuracy, automated collection of these data implemented in an electronic case report form (eCRF) or electronic data capture (EDC) system may be appropriate.
  - A description of the procedures and methods for blinding of the device outputs from the clinical reference standard determination process, masking of the clinical reference standard from the users/interpreters of the device outputs, and masking of the test data from the model developers and clinical team (to avoid opportunistic tweaking or bias in the study design), as applicable
  - A description of the controls in place to address any risks posed to the patient or user by the AI-enabled device during the study
  - If the protocol is altered during the execution of the clinical study, the applicant should explain the changes, and identify which changes are deemed minor and major, providing adequate justification for any repeated tests or tests with deviations from the pre-specified plans. The study protocol should be followed and all types of protocol deviations, including those deemed minor, should be minimized.
  - A full accounting of all enrolled subjects (with an accountability table)
  - A description of baseline distributions of the study population and other important factors in the dataset such as data acquisition equipment, device configurations, and disease status or conditions, and a justification of their representativeness
- Statistical analysis plans, including:
  - A description of the primary endpoint(s) or outcome(s), which should be reflective of the primary objective of the study
  - Pre-specified study success/failure criteria with respect to each of multiple primary endpoints (e.g., performance goals) that are clinically justified (e.g., supported by literature or prior investigations)
  - An explanation of the statistical hypotheses, such as null hypothesis, and the alternative (working) hypothesis
  - A sample size justification that ensures adequate study power
  - An explanation of the statistical analysis of the primary endpoint(s), including information to justify the sample size calculation
  - An explanation of the pre-specified, appropriate statistical approaches for handling multiplicity issues and controlling for overall Type I error rates
  - A description of the appropriate statistical methodology
  - A subgroup analysis plan. The appropriate subgroups are informed by the intended use of the device, but should generally include patient sex, age, race, ethnicity, disease variables, clinical data site, data acquisition equipment (e.g., camera brand), and, if applicable, conditions for use (including skill level of the user when relevant), device configurations, and other relevant confounding factors that may impact the device performance. When a specific performance claim is made with respect to a subgroup, the subgroup analysis should be statistically significant, including the inclusion of appropriately powered subgroups. However, when specific subgroup performance claims are not made, subgroup performance does not need to be statistically powered for each subgroup, but effort should be made to include reasonable numbers of patients for each subgroup so that any reported results have meaning and context.

**Study Results:** To support performance validation, sponsors should include information regarding the study results. Important aspects for these documents to cover include:

- An explanation of the pre-specified results for each test, including subgroup analyses
- An explanation of the results with adequate subgroup analyses for relevant subgroups as described above
  - If demographic information is not available for the study data, an explanation of the reasons it is not available, why performance evaluation can be supported without demographic subgroup analysis, and how risks associated with the lack of demographic subgroup analyses have been controlled
- When feasible, and appropriate, an evaluation of the device repeatability and reproducibility

*Where sponsors should provide it in a submission:* Information on the non-clinical or clinical testing of the device should be included in the appropriate sections of the marketing submission. For example, clinical study findings should go in the clinical section of the marketing submission. Information on the software verification and software validation of the model should be included in the "**Software testing as part of Verification and Validation**" in the Software Documentation section of the marketing submission, as described in the Premarket Software Guidance.

## XI. Device Performance Monitoring

*Why should it be included in a submission for an AI-enabled device:* The performance of AI-enabled devices deployed in a real-world environment (i.e., marketed AI-enabled devices following approval or clearance) may change or degrade over time, presenting a risk to patients. In general, as part of a quality system for a medical device, including an AI-enabled device, manufacturers should have a postmarket performance monitoring plan to help identify and respond to changes in performance in a postmarket setting. The inclusion of a performance monitoring plan in the marketing submission may help to reduce uncertainty and support FDA's evaluation of risk controls.

As part of their ongoing management of AI-enabled devices manufacturers should proactively monitor, identify, and address device performance changes, as well as changes to device inputs and the context in which the device is used that could lead to changes in device performance. In addition, sponsors must develop and implement plans for comprehensive risk analysis programs and documentation consistent with the Quality System Regulation (21 CFR Part 820) to manage risks related to undesirable changes in device performance for AI-enabled devices.

FDA generally does not assess quality system regulation compliance as part of its review of marketing submissions under section 510(k) of the FD&C Act. However, in some cases, it may be appropriate for FDA to review details from the sponsor's quality system in the marketing submission to ensure adequate ongoing performance. Such a review may help support a determination of substantial equivalence.

Ongoing performance monitoring is important for AI-enabled devices because, as described above, models are highly dependent on the characteristics of data used to train them, and as such, their performance can be particularly sensitive to changes in data inputs. Changes in device performance may originate from many factors, such as changes in patient populations over time, disease patterns, or data drift from other changes. When performance changes do occur, users may be less likely to identify them in AI-enabled devices if, for example, the devices are part of a highly automated process with limited ongoing human interaction, or if the output is prognostic such that different healthcare professionals may be involved in the use of the device and in confirmatory follow-up interactions with the patient. Because the performance of AI-enabled devices can change as aspects of the environments in which they are approved or cleared for use may change over time, it may not be possible to completely control risks with development and testing activities performed premarket (prior to device authorization and deployment).

*What sponsors should include in a submission:* Sponsors of AI-enabled devices that elect to employ proactive performance monitoring as a means of risk control and to provide reasonable assurance of the device's safety and effectiveness, should include information regarding their performance monitoring plans as part of the premarket submission. Sponsors are encouraged to obtain FDA feedback on the plan through the Q-Submission Program. For a 510(k) submission, FDA generally does not require such plans for devices, absent certain circumstances, for which a performance monitoring plan is not a special control for the particular device type (i.e., the applicable classification regulation). For a De Novo classification request, such a plan may be necessary to control risks posed by the particular device type and so FDA may establish such a special control for the device type going forward. For a PMA, a performance monitoring plan may be a condition of approval. However, sponsors may opt to include information regarding the performance monitoring plan in any submission for an AI-enabled device.

Performance monitoring plans should identify and respond to, in a timely fashion, performance changes or conditions that may lead to performance change or degradation. A robust performance monitoring plan includes proactive efforts to capture device performance after deployment. Components of such a plan may include:

- A description of the data collection and analysis methods for:
  - Identifying, characterizing, and assessing changes in model performance, including assessing the results from performance monitoring on safety and effectiveness
  - Monitoring potential causes of undesirable changes in performance, such as:
    - Changes in patient demographics or disease prevalence;
    - Shifts in input data;
    - Changes to input data due to corruption in the data pipeline (input data integrity), such as missing values, duplicate records, data type mismatches; and
    - Changes in users' behavior or in user demographics.
- A description of robust software lifecycle processes that include mechanisms for monitoring in the deployment environment
- A plan for deploying updates, mitigations, and corrective actions that address changing performance in a timely manner
- FDA notes that some actions taken to address performance changes may not require a marketing submission or authorization (21 CFR 807.81(a)(3) and 21 CFR 814.39(a)) prior to being taken. Please refer to FDA guidances titled, "Deciding When to Submit a 510(k) for a Change to an Existing Device," and "Deciding When to Submit a 510(k) for a Software Change to an Existing Device" to help assess whether a particular change may require a premarket submission to FDA. Sponsors may also wish to consider the use of a PCCP, as appropriate.
  - This plan does not replace applicable statutory or regulatory requirements, including the requirements to report to FDA information about certain adverse events, and corrections and removals, under 21 CFR Parts 803 and 806.
- A description of the procedures for communicating the results of performance monitoring and any mitigations to device users.

*Where sponsors should provide it in a submission:* When appropriate, a device performance monitoring plan should be included in the "**Risk Management File**" in the Software Documentation section of the marketing submission.

## XII. Cybersecurity

*Why should it be included in a submission for an AI-enabled device:* As with any digital or software component integrated into a medical device, AI can present cybersecurity risks. FDA's general recommendations for designing and maintaining cybersecurity as well as relevant marketing submission documentation are provided in the guidance document titled "Cybersecurity in Medical Devices: Quality System Considerations and Content of Premarket Submissions" (hereafter referred to as the "2023 Premarket Cybersecurity Guidance"). The 2023 Premarket Cybersecurity Guidance identifies security objectives that may be relevant for medical devices, including AI-enabled devices: authenticity, which includes integrity; authorization; availability; confidentiality; and secure and timely updatability and patchability.

For AI-enabled devices that meet the definition of a "cyber device" under section 524B(c) of the FD&C Act, the recommendations in this section of the guidance are intended to help manufacturers meet their obligations under section 524B of the FD&C Act. Examples of AI risks which can be impacted by cybersecurity threats include, but are not limited to:

- **Data Poisoning:** Cyber threats could lead to data poisoning by deliberately injecting inauthentic or maliciously modified data, risking outcomes in areas like medical diagnosis.
- **Model inversion/stealing:** Cyber threats could intentionally use forged or altered data to infer details from or replicate models. These pose risks to continued model performance as well as intellectual property and privacy breaches.
- **Model Evasion:** Cyber attackers could intentionally craft or modify input samples to deceive models, leading them to incorrect classifications. These pose risks to the reliability and integrity of model predictions, potentially undermining trust in AI-enabled devices and exposing them to malicious exploitation.
- **Data leakage:** Cyber threats could exploit vulnerabilities to access sensitive training or inference data in models.
- **Overfitting:** Cyber threats could deliberately "overfit" a model, exposing the AI components to adversarial attacks as these components struggle to adapt effectively to modified patient data.
- **Model Bias:** Cyber threats could lead to manipulation of training data to introduce or accentuate biases. They could exploit known biases using adversarial examples, embed backdoors during training to later trigger biased behaviors, or leverage pre-trained models with inherent biases, amplifying them with skewed fine-tuning data.
- **Performance Drift:** Cyber threats could lead to model performance drift by changing the underlying data distribution, which degrades model performance. Cyber threats could slightly shift the input data over time or exploit vulnerabilities in dynamic environments, causing the model to make inaccurate predictions or become more susceptible to adversarial attacks.

*What sponsors should include in a submission:* Consistent with the submission documentation recommended in the 2023 Premarket Cybersecurity Guidance regarding the cybersecurity controls and security risk management relevant to the AI components or features, sponsors should include the following types of information:

- Any additional elements in the cybersecurity risk management report, threat modeling, cybersecurity risk assessment, labeling, and other deliverables, where there are unique considerations related to AI cybersecurity.
- An explanation regarding how the cybersecurity testing is appropriate to address the risks associated with the model, including, at minimum the following tests:
  - Malformed input (fuzz) testing; and
  - Penetration testing.
- A Security Use Case View(s) that covers the AI-enabled considerations for the device.
- A description of controls implemented to address data vulnerability and preventing data leakage, including:
  - Access controls;
  - Any data encryption; and
  - Anonymization or de-identification of sensitive data.

Sponsors should refer to the control recommendations in Appendix 1 of the 2023 Premarket Cybersecurity Guidance for how they may wish to address the specific risks above. Example approaches to controlling cybersecurity risks related to AI-enabled devices include:

- For data poisoning attacks, consider:
  - Validating, authenticating, and cleansing data
  - Employing anomaly detection and data integrity checks (e.g., cryptographic hashes)
  - Applying adversarial training, which is a method used to improve the robustness and security of models
- For cyber threats using forged data to introduce overfitting, model bias, etc., consider:
  - Adopting differential privacy, which is a technique to protect the privacy of individual data points in a dataset
  - Engaging in secure multi-party computation (MPC), which is a technique that can allow multiple parties to collaboratively train a model without revealing their local datasets to each other
  - Employing data authentication and integrity protections
  - Introducing watermarking, which involves embedding hidden watermarks into AI models to prove ownership
  - Applying continuous model performance monitoring
- For model evasion, consider adversarial training to enhance model robustness and implement strict input verification checks to ensure data conforms to expected patterns

*Where sponsors should provide it in a submission:* The cybersecurity information should be included in the "**Cybersecurity/Interoperability**" section of the marketing submission, as described in the 2023 Premarket Cybersecurity Guidance.

## XIII. Public Submission Summary

*Why should it be included in a submission for an AI-enabled device:* Transparency is a key component of premarket authorization and is important to patient care. This is especially important for AI-enabled devices, which are heavily data driven and incorporate algorithms exhibiting a degree of opacity. In public workshops and comments, including the October 14, 2021 virtual public workshop on the transparency of AI-enabled devices titled "Transparency of Artificial Intelligence/Machine Learning-enabled Medical Devices," patients noted concerns with the use of AI in their care. The public has consistently called for additional information about how FDA makes authorization decisions about AI-enabled devices, as well as more information about the design and validation of these devices. The public submission summary should include specific information describing the characteristics of these devices to support transparency, which can contribute to public health by increasing understanding of AI-enabled devices and developing public trust.

Public submission summaries are required and available on the FDA website for most marketing authorization decisions. These summaries describe the device and the information supporting regulatory decision-making. Where a public summary is required, details about the AI-enabled device must be included in sufficient detail in the public-facing documents to support transparency to users of FDA's determination of substantial equivalence or reasonable assurance of safety and effectiveness for the device. To ensure public access to important information on authorized AI-enabled devices, this section describes the types of information sponsors should include in the public submission summary as well as a possible format for such information.

While not required, the use of a model card may be one way to communicate information about AI-enabled devices because they are a means to consistently summarize the key aspects of AI-enabled devices and can be used to concisely describe their characteristics, performance, and limitations. Appendix E (Example Model Card) provides recommendations for the contents and formatting of a model card. Research has demonstrated that the use of a model card can increase user trust and understanding. The use of a model card as part of a public submission summary specifically is one way to support clear and consistent communication about an AI-enabled device to the interested parties in the public as well as to users, such as patients, clinicians, regulators, and researchers. The use of the model card can address the challenges associated with determining the best approach to communicate important information about the AI-enabled device.

*What sponsors should include in a submission:* Sponsors must comply with the submission regulations for their particular submission. In addition, sponsors should consider FDA recommendations for the relevant marketing submission type. Sponsors should also provide the following types of information excluding any patient identifiers, trade secrets, and confidential commercial information:

- A statement that AI is used in the device;
- An explanation of how AI is used as part of the device's intended use. For devices with multiple functions, this explanation may include how AI-DSFs interact with each other as well as how they interact with non-AI-DSFs;
- A description of the class of model (e.g., convolutional neural network, recurrent neural network, support vector machine, transformers) and limitations of the model within the device description;
- A description of the development and validation datasets (size, source of data), including information about the demographic characteristics in the training and validation data, along with information about the demographic characteristics in the population(s) of intended use. The description should also compare the training dataset to the validation dataset and model data inputs expected in the intended use. The comparison should describe how independence of test data from training data was ensured;
- A description of the statistical confidence level of predictions, including any other descriptions or metrics that describe statistical confidence and uncertainty, as applicable; and
- A description of how the model will be updated and maintained over time, if applicable.

Sponsors should consider using a model card to organize information. Appendix E (Example Model Card) includes recommendations on the elements that may be included within a model card. While the example model card includes recommended elements and format for a model card, sponsors may include additional information and/or follow a different format. In the absence of the model card structure, sponsors should still consider including the information a model card contains.

*Where sponsors should provide it in a submission:* The public submission summary should be included in the "**Administrative Documentation**" section of the marketing submission.

## Appendix A: Table of Recommended Documentation

| Guidance Section and Recommended Information | Recommended Section in Sponsor's Marketing Submission |
|---|---|
| Section V Device Description | Device Description |
| Section VI.A User Interface | Software Description |
| Section VI.B Labeling | Labeling |
| Section VII Risk Assessment | Risk Management File of Software Documentation |
| Section VIII Data Management | Data for development: Software Description of Software Documentation; Data for testing: Performance Testing |
| Section IX Model Description and Development | Software Description |
| Section X.A Performance Validation | Clinical and non-clinical testing: Performance Testing; Software verification and software validation: Software testing as part of verification and validation of Software Documentation |
| Section XI Device Performance Monitoring | Risk Management File of Software Documentation |
| Section XII Cybersecurity | Cybersecurity |
| Section XIII Public Submission Summary | Administration Information |

## Appendix B: Transparency Design Considerations

This appendix contains recommendations for developing a transparent device centered around users. These recommendations are intended to help sponsors develop safe and effective medical devices and high-quality marketing submissions. While sponsors may identify alternate approaches that support FDA's evaluation of safety and effectiveness, they should integrate transparency considerations starting at the design phase of the TPLC to ensure the availability of information to support the marketing submission.

In this guidance, transparency refers to clearly communicating the contextually relevant performance and design information of a device to the appropriate stakeholders in a manner that they can understand and act on. Transparency involves ensuring that important information is both accessible and functionally comprehensible and is connected both to the sharing of information, and to the usability of a device. As such, a user-centered approach to transparency design helps support the safe and effective use of AI-enabled devices.

Key topics addressed in this appendix include:

- **Transparency by Design Across the TPLC** — Sponsors should take a holistic approach to identifying relevant contextual factors for device use and how those factors impact device performance when determining what information should be communicated. Sponsors should consider transparency throughout the full continuum of implementation through use, maintenance, and decommission.
- **The Right Information at the Right Time** — Consider what information the users might need, when they might need it to facilitate decision-making, and the potential risks if the users do not have the appropriate information at the right time, at all, or if it is misunderstood.
- **Understanding User Characteristics and Needs** — The ability of a user to operate an AI-enabled device depends on their personal characteristics and the device use environment.
- **Communication Style and Format** — It is also important to consider the format used for communication. Factors may include: the reading level of the user, the location of information, and design elements such as hierarchy, visualizations, and dynamic labeling.
- **Explainability Information and Visualizations** — It is also important to consider when additional information may detract from understanding, rather than add to it. Explainability tools or visualizations can be valuable in increasing model transparency and a user's confidence in a model's output, but if not well designed and validated for the target user group, they could also significantly mislead users.

## Appendix C: Performance Validation Considerations

This appendix contains recommendations for some aspects of clinical performance validation in AI-enabled devices, which are intended to help sponsors develop safe and effective medical devices. Key topics include:

- **Pre-specification of Study Protocols and Statistical Analysis Plan** — Post-hoc analysis may bias the performance assessment. Therefore, study protocols and statistical analysis plans should be pre-specified.
- **Study Reports** — All performance and usability assessments should be objective, and the model should not be tweaked opportunistically in light of the test data results (i.e., no post-hoc adjustment).
- **Masking Protocol** — For diagnostic devices, a masking protocol in the clinical study ensures that the user of the test is "blinded/masked" to the clinical reference standard result while the provider of the clinical reference standard result is "blinded/masked" to the test result.
- **Model Precision: Repeatability and Reproducibility** — A precision study gauges the variability of a device output when making repeated measurements on the same patient.
- **Study Endpoints and Acceptance Criteria** — Primary endpoints are usually assessed using pre-specified acceptance criteria within a statistical hypothesis testing framework.
- **Validation of AI-based Pre-processing Steps** — Some models may include a quality control algorithm that discards "low" quality cases from further processing. However, such low-quality cases may actually be truly hard/difficult ones — an example of missing not at random (MNAR).

## Appendix D: Usability Evaluation Considerations

This appendix provides recommendations to help sponsors understand when usability testing may help support the control of risks. As described in this guidance Section X Validation, sponsors should conduct human factors evaluations as part of design controls for every medical device requiring a premarket submission. Human factors engineering processes typically begin with preliminary analysis and evaluation of all tasks which, if performed incorrectly or not performed at all, could cause serious harm. This appendix is focused on the evaluation of usability to support risk controls when a human factors validation testing report is not required, where usability addresses whether all intended users can achieve specific goals while using the device and whether users will be able to consistently interact with the device safely and effectively.

For AI-enabled devices, it may be specifically important for sponsors to identify and evaluate risk controls related to user tasks regarding the interpretation and use of information and interactions with novel user interfaces. The application of this information is a particular challenge for users of AI-enabled devices because models developed through AI techniques vary in explainability and interpretability.

## Appendix E: Example Model Card

A model card is a popular format for communicating information about a device that may align with the kind of information that FDA may require, for example in the publicly available 510(k) summaries and labeling. The model card format and content discussed below is intended to serve as an example of possible formatting a sponsor could use to communicate information about the model and the AI-enabled device in the public submission summary and other locations where this information may be shared by the sponsor.

The example model card below has been designed based on user-centered research to present data in an order and format that is useful and easy to understand for non-technical audiences and is provided to sponsors to facilitate the inclusion of a model card.

**Example Model Card Structure:**

- **Device Information:** Name of the Device, Version of the Device, Date when the Device was created (or last updated), Model Architecture
- **Regulatory Status** (for model cards used outside of the public submission summary): Authorization status, File number
- **Description:** Intended users, Intended use, Indications for use, Instructions for Use, Clinical benefits, Clinical workflow phase, Inputs and outputs of the model, Degree of automation compared to the current standard of care
- **Performance and Limitations:** Accuracy metrics with 95% two-sided confidence intervals, Known biases or failure modes, Precision (reproducibility), Known gaps in data characterization, Limitations in model development or performance evaluation, Known circumstances where device input will not align with development/validation data, Evidence (clinical trial number, DOI, etc.) with data characterization details, Methods used to establish the model meets intended use and user requirements
- **Risk Management:** Potential risks, Description of information that could impact risks and patient outcomes across the product lifecycle, Interactions, Deployment, and Updates details
- **Development:** Data Characterization including sources, types, relevant details

## Appendix F: Example 510(k) Summary with Model Card

This appendix serves as an example of the types of information sponsors should generally provide in a 510(k) summary, including an example of a completed Basic Model Card. The example presents a hypothetical AI-enabled device — the "Disease X Screening Model" — a stand-alone software that uses a convolutional neural network to analyze 12-lead resting ECGs from 4 compatible ECG devices to screen for Disease X in patients above the age of 22.

The example includes:

- **Indications For Use** statement
- **Device Description** with model details
- **Summary of Technological Characteristics** comparison table (Subject Device vs. Predicate Device)
- **Model Training Description** with demographic breakdowns (race, sex, age), training data split ratios, and tuning evaluation results
- **Summary of Non-Clinical Performance Data** covering human factors, cybersecurity, and software V&V
- **Summary of Clinical Validation** including:
  - Study design (retrospective, 25,000 patients, 5 sites)
  - Inclusion/exclusion criteria
  - Demographic distributions by race, age, hospital site, and ECG acquisition device
  - Primary endpoints (sensitivity >= 75%, PPV >= 50%)
  - Study results with confusion matrix (Sensitivity: 84%, Specificity: 83%, PPV: 55.3%, NPV: 95.4%)
  - Subgroup analyses by race, age, hospital site, and ECG acquisition device
  - Plain language interpretation for benefit-risk consideration
- **Completed Basic Model Card** with all sections populated for the Disease X Screening Model
