# User Needs — PainEase PCA Advanced (DEV-PP3500)

> _Demo sample data — not for clinical use. Illustrative content for the PDLC_DEMO project._

| Field | Value |
|---|---|
| Document ID | DHF-PP3500-UN-001 |
| Revision | B |
| Status | Draft |
| Owner | GlobalLogic Product Development |
| Device | PainEase PCA Advanced |
| Model | PP-3500 |
| Device ID | DEV-PP3500 |
| FDA Product Code | LZH (Infusion Pump, Patient-Controlled Analgesia) |
| Device Class | Class II |
| 510(k) Number | K210345 (cleared 2021-11-01) |
| Predicate | K190567 (PainEase PCA, DEV-PP3000) |
| Applicable Standards | IEC 60601-1, IEC 60601-1-2 (EMC), IEC 60601-2-24 (infusion pumps), IEC 62304 (software), ISO 14971 (risk), IEC 62366-1 (usability), IEC 81001-5-1 (cybersecurity), ISO 10993-1 (biocompat) |

## Intended Use

The PainEase PCA Advanced (Model PP-3500) is a portable, battery-powered patient-controlled analgesia (PCA) infusion pump intended for the controlled intravenous administration of analgesic medications by trained healthcare professionals. The device delivers programmed continuous (basal) infusions and patient-activated bolus doses within prescriber-defined limits to support the management of acute and chronic pain. It is intended for use in supervised acute-care environments where qualified clinical staff are available to monitor the patient and respond to alarms.

## Indications for Use

The PainEase PCA Advanced is indicated for the patient-controlled intravenous (IV) administration of opioid and non-opioid analgesics — including morphine, hydromorphone, fentanyl, and compatible local anesthetic agents — for the management of moderate to severe acute postoperative pain, acute pain associated with trauma or medical procedures, and chronic pain (including cancer-related pain) in adult and adolescent patients (≥12 years of age and ≥40 kg). The device is intended for use in hospitals, ambulatory surgical centers, and other supervised acute-care facilities under the direction of a qualified prescriber. Pediatric use below 12 years of age requires additional clinical judgment and is outside the scope of the cleared indication. The device is **not** indicated for intrathecal, epidural, or arterial administration; it is **not** intended for unsupervised home or ambulatory use; and it is **not** MRI-safe. PCA therapy with this device requires that the patient be cognitively capable of self-administration and that trained clinical staff be available for monitoring and alarm response. Standard opioid warnings — including risks of respiratory depression, sedation, and abuse — apply to all use of this device.

## Scope of This Document

This document is the controlled record of validated user needs for the PainEase PCA Advanced (DEV-PP3500) program, captured at design controls Phase 4. It is the upstream input to the Design Inputs document (DHF-PP3500-DI-001) and to the User Needs ↔ Design Inputs trace matrix. Revision A reflects the initial baseline derived from KOL interviews, predicate post-market data (including CAPA-2023-001), market research, and applicable standards.

---

## User Needs Categories

| Category | Description |
|---|---|
| **Clinical (CLIN)** | Needs arising from clinical therapy and patient outcomes |
| **User / Workflow (USER)** | Needs of HCPs operating the device in their workflow |
| **Safety (SAFE)** | Patient and operator safety needs independent of clinical efficacy |
| **Regulatory (REGU)** | Needs driven by applicable regulation and standards |
| **Market (MARK)** | Needs driven by commercial / market differentiation |

## Functional Groups

The user needs in this document are organized into 9 functional groups aligned with the device architecture. Each group corresponds to a cohesive feature area of the PainEase PCA Advanced.

| # | Group | Scope |
|---|---|---|
| G1 | Therapy Delivery | Continuous rate, PCA bolus, lockout, cumulative dose limits, flow-rate accuracy |
| G2 | Drug Library & Medication Safety | Drug library, hard/soft limits, barcode scanning, medication verification |
| G3 | Alarms & Annunciation | Occlusion, air-in-line, over-infusion, end-of-therapy, priority, audible/visual |
| G4 | Hazard Controls & Essential Performance | Free-flow, electrical safety, EMC, biocompat, IEC 60601 essential performance |
| G5 | User Interface & Usability | Touchscreen, decimal-point legibility, home screen, programming task flow |
| G6 | Power, Portability & Physical | Battery, charging, weight, mounting, cleaning, lockbox, tamper-evidence |
| G7 | Connectivity & Interoperability | Wi-Fi, Bluetooth, HL7 v2.5, FHIR R4, EHR integration |
| G8 | Cybersecurity & Data Integrity | Authentication, TLS, signed firmware, SBOM, audit log |
| G9 | Regulatory, Labeling & Lifecycle Compliance | UDI/GUDID, IFU/labeling, IEC 62304 Class C, IEC 62366-1, serviceability |

## User Needs by Functional Group

### G1 — Therapy Delivery

_Core analgesic delivery needs: patient-titrated bolus, continuous basal infusion, and clinician-enforced dose limits._

| Group | UN ID | Category | Stakeholder | User Need | Source | Priority |
|---|---|---|---|---|---|---|
| G1 | UN-001 | CLIN | Patient, Nurse, Anesthesiologist | The device must deliver on-demand analgesic bolus doses within prescribed limits to provide effective, patient-titrated pain control across postoperative, acute, and chronic pain scenarios. | KOL-0006 (Paul); acute pain service workflow analysis | High |
| G1 | UN-002 | CLIN | Anesthesiologist, Nurse | The device must support a programmable continuous (basal) infusion rate alongside PCA bolus delivery so clinicians can tailor therapy to opioid-tolerant and chronic-pain patients. | KOL-0006 (Paul); predicate IFU; clinical literature | High |
| G1 | UN-003 | CLIN | Anesthesiologist, Pharmacist | The device must enforce clinician-programmed lockout intervals and 1-hour / 4-hour cumulative dose limits to prevent over-sedation between bolus requests. | KOL-0006 (Paul); ISMP PCA safety guidelines | High |

### G2 — Drug Library & Medication Safety

_Drug-library enforcement, barcode-driven medication verification, and library version control._

| Group | UN ID | Category | Stakeholder | User Need | Source | Priority |
|---|---|---|---|---|---|---|
| G2 | UN-004 | SAFE | Patient, Nurse, Pharmacist | The device must prevent any programming pathway from delivering a dose that exceeds the institution's drug-library hard limits, regardless of operator role or override attempt. | ISO 14971 hazard analysis; CAPA-2023-001 root-cause review | High |
| G2 | UN-008 | USER | Nurse, Pharmacist | Clinicians must be able to verify the medication, concentration, and patient identity at the bedside via integrated barcode scanning to reduce wrong-drug and wrong-patient errors. | KOL-0006 (Paul); ISMP medication safety best practices | High |
| G2 | UN-009 | USER | Nurse | Clinicians must be able to load a current institution-approved drug library onto the pump and confirm the active library version before initiating therapy. | Pharmacy & Therapeutics committee feedback; predicate workflow gap | High |

### G3 — Alarms & Annunciation

_Detection and clinician notification of occlusion, air-in-line, over-infusion, and other priority alarm conditions._

| Group | UN ID | Category | Stakeholder | User Need | Source | Priority |
|---|---|---|---|---|---|---|
| G3 | UN-006 | SAFE | Patient, Nurse | The device must detect downstream occlusions and air-in-line conditions and alert the clinician before patient harm can occur. | IEC 60601-2-24 §201.12; KOL-0006 (Paul) | High |
| G3 | UN-010 | SAFE | Patient, Nurse | Alarms must be reliably audible and distinguishable in a typical acute-care ward environment without contributing to alarm fatigue. | KOL-0008 (Shah); IEC 60601-1-8 | High |

### G4 — Hazard Controls & Essential Performance

_Free-flow protection, electrical safety, EMC, and biocompatibility — the IEC 60601 essential-performance baseline._

| Group | UN ID | Category | Stakeholder | User Need | Source | Priority |
|---|---|---|---|---|---|---|
| G4 | UN-005 | SAFE | Patient, Nurse | The device must prevent gravity-driven free flow of medication if the administration set is removed or improperly loaded. | IEC 60601-2-24; predicate field history | High |
| G4 | UN-015 | SAFE | Patient | All patient-contacting materials (administration set, lockbox surfaces, button surfaces) must be biocompatible for the intended duration and route of contact. | ISO 10993-1; risk file | High |

### G5 — User Interface & Usability

_Touchscreen, decimal-point legibility (CAPA-2023-001), and minimization of programming use errors._

| Group | UN ID | Category | Stakeholder | User Need | Source | Priority |
|---|---|---|---|---|---|---|
| G5 | UN-007 | USER | Nurse, Pharmacist | Clinicians must be able to enter and confirm decimal-point dose values without ambiguity, so that a 1.0 mg dose cannot be misread or mis-entered as 10 mg. | CAPA-2023-001 (decimal-point visibility, 2023-01-10); Field Safety Notice 2023-01-20 | High |
| G5 | UN-014 | USER | Nurse, Anesthesiologist | The user interface must be operable by a trained nurse with minimal training time and must minimize use errors during programming, bolus delivery, and alarm response. | IEC 62366-1 process; usability validation lessons (predicate) | High |

### G6 — Power, Portability & Physical

_Battery endurance, cleaning compatibility, mounting, and physical security of the lockbox._

| Group | UN ID | Category | Stakeholder | User Need | Source | Priority |
|---|---|---|---|---|---|---|
| G6 | UN-011 | USER | Nurse, Biomed Engineer | The pump must operate continuously on battery for at least one full nursing shift cycle to support intra-hospital patient transport and bedside ambulation without interruption. | Nursing workflow study; predicate complaint data | High |
| G6 | UN-016 | USER | Biomed Engineer | The device must support routine cleaning and disinfection per the institution's infection-control protocols without degrading housings, displays, or seals. | Biomed feedback; CDC environmental cleaning guidelines | Medium |
| G6 | UN-020 | MARK | Pharmacist, Nurse | The lockbox / drug cassette must be tamper-evident and physically secure against unauthorized access to controlled substances. | DEA controlled-substance handling expectations; hospital security policy | Medium |
| G6 | UN-022 | USER | Nurse, Patient | The device must be light enough and ergonomically suitable to attach to an IV pole, bedrail, or patient belt clip without impeding mobility. | Nursing workflow study; predicate weight (0.6 kg) baseline | Medium |

### G7 — Connectivity & Interoperability

_Wireless networking and EHR integration via HL7 v2.5 and FHIR R4._

| Group | UN ID | Category | Stakeholder | User Need | Source | Priority |
|---|---|---|---|---|---|---|
| G7 | UN-012 | MARK | Hospital IT, Nurse | The device must integrate with the hospital wireless network and EHR/EMR systems so that programmed therapy and event logs flow into the patient record without manual transcription. | Sales win/loss analysis; KOL-0006 (Paul) | Medium |
| G7 | UN-021 | MARK | Hospital IT, Anesthesiologist | The device should optionally publish therapy events via HL7 FHIR to support smart-pump interoperability initiatives and analytics dashboards. | KOL-0006 (Paul); AAMI infusion-interoperability roadmap | Low |

### G8 — Cybersecurity & Data Integrity

_Protection of patient data and therapy integrity throughout the operational life of the device._

| Group | UN ID | Category | Stakeholder | User Need | Source | Priority |
|---|---|---|---|---|---|---|
| G8 | UN-013 | SAFE | Hospital IT, Biomed Engineer, Regulatory Affairs | The device must protect patient data and therapy integrity against unauthorized network access, malware, and tampering throughout its operational life. | IEC 81001-5-1; FDA premarket cybersecurity guidance (2023) | High |

### G9 — Regulatory, Labeling & Lifecycle Compliance

_UDI/labeling, software lifecycle process, and serviceability needs driven by regulation and lifecycle support._

| Group | UN ID | Category | Stakeholder | User Need | Source | Priority |
|---|---|---|---|---|---|---|
| G9 | UN-017 | USER | Biomed Engineer | The device must provide diagnostic logs, calibration access, and field-replaceable parts to support routine preventive maintenance on a 6-month interval. | Biomed feedback; service economics | Medium |
| G9 | UN-018 | REGU | Regulatory Affairs, Patient | The device, packaging, and IFU must carry UDI, symbols, and labeling content that satisfy 21 CFR 801, 21 CFR 830, and EU MDR 2017/745 requirements. | 21 CFR 801, 21 CFR 830; EU MDR Annex I | High |
| G9 | UN-019 | REGU | Regulatory Affairs | Device software must be developed, documented, and verified under a software lifecycle process commensurate with its safety classification. | IEC 62304; FDA premarket software guidance (2023) | High |

## Traceability

Every user need traces forward to one or more design inputs in `../requirements/design-inputs.md`. The full bidirectional UN ↔ DI trace matrix lives in `../trace-matrix/un-to-di-trace-matrix.md`.

## Revision History

| Rev | Date | Author | Description |
|---|---|---|---|
| B | 2026-04-12 | Ben Xavier | Reorganized into 9 functional groups (G1–G9). No change to UN content; added Group column and per-group H3 sections. |
| A | 2026-04-12 | Ben Xavier | Initial draft — Phase 4 of PDLC_DEMO. Authored from sample corpus (18 UN-/DI- files) with broad adaptation for realism. |
