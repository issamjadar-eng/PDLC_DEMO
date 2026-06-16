# IHE Profiles — Integrating the Healthcare Enterprise

🔎 **Finding aid — NOT the authoritative source.** Paraphrased distillation of an external standard/framework; no faithful full-text copy exists in this repository (copyrighted). The original document named in the header above is the sole authority — if a clause-level question isn't answered here, state that the original must be consulted; do not infer clause content. `[VERIFY]` marks are unconfirmed against the source.

**Framework**: IHE Technical Frameworks (Radiology, IT Infrastructure, Patient Care Coordination)
**Source**: IHE International
**Referenced In**: Healthcare interoperability best practice; complements DICOM by defining workflow-level integration patterns

## Overview

IHE doesn't create new standards — it defines **profiles** that specify how existing standards (DICOM, HL7) are used together to solve specific clinical integration problems. Where DICOM defines the protocol for exchanging images, IHE profiles define the **workflow** for how systems coordinate to accomplish clinical tasks.

## Relevant IHE Domains

### Radiology (RAD)

The primary domain for imaging-based platforms.

| Profile | Name | Description |
|---------|------|-------------|
| **SWF** | Scheduled Workflow | Coordinates ordering, scheduling, image acquisition, and storage |
| **PIR** | Patient Information Reconciliation | Reconciles patient demographics across systems |
| **CPI** | Consistent Presentation of Images | Standardizes how images are displayed |
| **KIN** | Key Image Note | Marks significant images within a study |
| **SINR** | Simple Image and Numeric Report | Structured reporting of imaging results |

### IT Infrastructure (ITI)

Cross-domain profiles for general healthcare IT integration.

| Profile | Name | Description |
|---------|------|-------------|
| **ATNA** | Audit Trail and Node Authentication | Security audit logging and mutual TLS authentication |
| **CT** | Consistent Time | Time synchronization across systems |
| **XDS.b** | Cross-Enterprise Document Sharing | Document sharing infrastructure |
| **MHD** | Mobile access to Health Documents | RESTful document sharing (FHIR-based) |
| **PDQ / PDQm** | Patient Demographics Query | Query patient demographics from master patient index |
| **PIX / PIXm** | Patient Identifier Cross-Referencing | Resolve patient identifiers across systems |

### Patient Care Coordination (PCC)

| Profile | Name | Description |
|---------|------|-------------|
| **XDS-MS** | Cross-Enterprise Document Sharing for Medical Summaries | Share surgical summaries and clinical documents |

## IHE Conformance Statement (IHE Integration Statement)

Similar to a DICOM Conformance Statement, IHE expects an **IHE Integration Statement** that declares:
- Which IHE profiles the system supports
- Which actors the system implements for each profile
- Which options are supported
- Integration testing results (Connectathon participation if applicable)
