---
doc_id: "DHF-PP3500-DI-001"
doc_type: "QSD"
references:
  - doc_id: "GL-TMP-DC-002"
    title: "Parent QMS template"
    resolved: true
    match: null
    note: "21 CFR 820.30(c); ISO 13485 §7.3.3 — mapped under task ben/123"
---
<!-- AI-CHANGELOG — internal provenance of AI-assisted edits. Metadata only:
     NOT published downstream (Confluence/Doc-Control), NOT part of the controlled
     record, stripped on DOCX/PDF export. Vendor-neutral by convention.
| Date       | Task    | Summary |
|------------|---------|---------|
| 2026-09-08 | ben/123 | Provenance block added retroactively; document originally AI-assisted (frontmatter conversion_method) |
-->

# Design Inputs — PainEase PCA Advanced (DEV-PP3500)

> _Demo sample data — not for clinical use. Illustrative content for the PDLC_DEMO project._

| Field | Value |
|---|---|
| Document ID | DHF-PP3500-DI-001 |
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

## 1. Project Identification

_[TBD — section required by GL-TMP-DC-002; content to be authored.]_

## 2. Intended Use and Indications for Use

The PainEase PCA Advanced (Model PP-3500) is a portable, battery-powered patient-controlled analgesia (PCA) infusion pump intended for the controlled intravenous administration of analgesic medications by trained healthcare professionals. The device delivers programmed continuous (basal) infusions and patient-activated bolus doses within prescriber-defined limits to support the management of acute and chronic pain. It is intended for use in supervised acute-care environments where qualified clinical staff are available to monitor the patient and respond to alarms.

## 3. User Needs (Summary)

_[TBD — section required by GL-TMP-DC-002; content to be authored.]_

## 4. Design Inputs (Requirements)

### G1 — Therapy Delivery

_Quantitative flow-rate, bolus, lockout, and cumulative-limit requirements that implement PCA therapy._

| Group | DI ID | Category | Criticality | Requirement Statement | Acceptance Criteria | Traces to UN | Verification Method |
|---|---|---|---|---|---|---|---|
| G1 | DI-001 | PERF | **CTS** | The device shall deliver programmed continuous flow rates from 0.01 to 25 mL/hr with an accuracy of ±5% (or ±0.5 mL/hr, whichever is greater) across the full operating range. | Gravimetric bench test per IEC 60601-2-24 §201.12.1.101 at 5 set points (0.1, 1, 5, 15, 25 mL/hr); n≥3 units, 3 replicates each; all measurements within ±5%. | UN-001, UN-002 | Bench test (VER-PP3500-BT-005) |
| G1 | DI-002 | PERF | **CTS** | The device shall deliver patient-activated bolus doses from 0.01 to 20 mL with a delivered-volume accuracy of ±5% across the dose range. | Gravimetric bench test per IEC 60601-2-24 §201.12; n≥30 bolus deliveries at 3 dose levels; all within ±5%. | UN-001 | Bench test |
| G1 | DI-003 | FUNC | **CTF** | The device shall support a programmable lockout interval from 1 to 99 minutes between consecutive PCA bolus requests. | Software test: program lockout at 1, 15, and 99 min; verify no bolus delivered before interval expires. | UN-003 | Software test (VER-PP3500-SW-002) |
| G1 | DI-004 | SAFE | **CTS** | The device shall enforce programmable 1-hour and 4-hour cumulative dose limits and shall block any bolus that would exceed the limit. | Software test: attempt over-limit bolus via PCA button, clinician menu, and barcode-loaded order; all blocked with alert. | UN-003, UN-004 | Software test (VER-PP3500-SW-002) |

### G2 — Drug Library & Medication Safety

_Drug-library hard-limit enforcement, barcode scanning, and library content management._

| Group | DI ID | Category | Criticality | Requirement Statement | Acceptance Criteria | Traces to UN | Verification Method |
|---|---|---|---|---|---|---|---|
| G2 | DI-005 | SAFE | **CTS** | The device shall enforce drug-library hard maximum limits such that no programming path — manual entry, barcode-loaded order, or clinician override — can program a value exceeding the active library's hard cap. | Software test per VER-PP3500-SW-006: traverse all programming entry paths against a 200-medication test library; zero hard-limit breaches. | UN-004, UN-009 | Software test (VER-PP3500-SW-006) |
| G2 | DI-015 | FUNC | **CTF** | The device shall maintain an on-board drug library of at least 200 medications with editable hard and soft limits, and shall display the active library version on the home screen and at therapy start. | Load reference library; verify count ≥200, version banner visible, version recorded in audit log. | UN-009 | Software test |
| G2 | DI-016 | FUNC | **CTF** | The device shall include an integrated 1D/2D barcode scanner capable of reading medication container barcodes (NDC, GS1) and matching them against the active drug library before therapy start. | Bench test with reference barcode set (50 medications, 5 print qualities); ≥98% first-read success; mismatch produces blocking alert. | UN-008 | Bench test |

### G3 — Alarms & Annunciation

_Occlusion, air-in-line, over-infusion detection and audible alarm annunciation per IEC 60601-1-8._

| Group | DI ID | Category | Criticality | Requirement Statement | Acceptance Criteria | Traces to UN | Verification Method |
|---|---|---|---|---|---|---|---|
| G3 | DI-007 | SAFE | **CTS** | The device shall detect downstream occlusions in the range 3 to 15 psi and annunciate a high-priority occlusion alarm within the response time required by IEC 60601-2-24. | Bench test per IEC 60601-2-24 §201.12.4.4.103 at 3 flow rates (1, 5, 25 mL/hr); alarm time within standard limits for n=10 trials. | UN-006 | Bench test |
| G3 | DI-008 | SAFE | **CTS** | The device shall detect single air-in-line bubbles ≥50 µL and cumulative air ≥1 mL over a 15-minute window and shall annunciate a high-priority air-in-line alarm. | Bench test with calibrated air injector at 0.05, 0.1, and 0.5 mL boluses; 100% detection across n=20 trials per condition. | UN-006 | Bench test |
| G3 | DI-009 | SAFE | **CTS** | The device shall annunciate a high-priority over-infusion alarm and halt delivery if the measured delivered volume deviates from the programmed volume by more than 10% over any rolling 1-hour window. | Software-in-the-loop test injecting motor-position faults; alarm within 60 s and motor halt verified for all n=10 fault scenarios. | UN-001, UN-006 | Software test |
| G3 | DI-019 | INTE | **CTF** | The device shall provide audible alarms compliant with IEC 60601-1-8 for high-, medium-, and low-priority alarm categories, with sound pressure level adjustable from 45 to 80 dB(A) at 1 m. | Acoustic measurement in anechoic chamber; verify SPL range and alarm melody compliance for all alarm categories. | UN-010 | Bench test |

### G4 — Hazard Controls & Essential Performance

_Free-flow protection, IEC 60601 electrical safety, EMC, and biocompatibility — the essential-performance baseline._

| Group | DI ID | Category | Criticality | Requirement Statement | Acceptance Criteria | Traces to UN | Verification Method |
|---|---|---|---|---|---|---|---|
| G4 | DI-006 | SAFE | **CTS** | The device shall prevent free-flow delivery of medication when the administration set is removed from the pumping mechanism, via an integral anti-siphon mechanism on the dedicated administration set. | Bench test per IEC 60601-2-24 §201.12.1.103: open the door under +/-1 m head pressure with set installed; measure free-flow ≤0.1 mL over 60 s for n=10 sets. | UN-005 | Bench test |
| G4 | DI-010 | SAFE | **CTS** | The device shall meet the general electrical-safety and essential-performance requirements of IEC 60601-1 (3rd edition + A1) and the particular standard IEC 60601-2-24. | Third-party safety testing report demonstrating compliance with all applicable clauses; no deviations. | UN-005, UN-018 | Electrical safety test |
| G4 | DI-011 | SAFE | **CTS** | All patient-contacting materials of the dedicated administration set, lockbox exterior, and user-interface surfaces shall be biocompatible per ISO 10993-1 for the intended contact category (limited contact, intact skin / indirect blood contact via fluid path). | Biocompatibility evaluation per ISO 10993-1 hazard table; cytotoxicity, sensitization, and irritation tests passed per ISO 10993-5/-10. | UN-015 | Biocompat test |
| G4 | DI-012 | INTE | **CTS** | The device shall meet the EMC immunity and emissions requirements of IEC 60601-1-2 (4th edition) for professional healthcare facility environments. | Third-party EMC test report; all immunity tests pass with essential performance maintained; emissions within Class B limits. | UN-018 | EMC test |

### G5 — User Interface & Usability

_Touchscreen UI, decimal-point legibility (CAPA-2023-001), and summative usability validation._

| Group | DI ID | Category | Criticality | Requirement Statement | Acceptance Criteria | Traces to UN | Verification Method |
|---|---|---|---|---|---|---|---|
| G5 | DI-013 | USAB | **CTS** | The device's numeric entry interface shall display all dose values with an unambiguous decimal point that remains legible at viewing distances up to 1 m and viewing angles up to ±45°, and shall require explicit confirmation of decimal placement on entry. | Summative usability test per IEC 62366-1 with n≥15 representative nurses; zero decimal-point misread errors across all critical tasks. Display contrast ratio ≥4.5:1 verified by inspection. | UN-007, UN-014 | Usability test (summative) |
| G5 | DI-014 | FUNC | **CTF** | The device shall provide a 3.5-inch color LCD touchscreen user interface supporting programming of all therapy parameters and review of active therapy. | Functional verification of all UI screens against UI specification; touch response <200 ms; n=3 units. | UN-014 | Bench test / inspection |
| G5 | DI-020 | USAB | **CTF** | The device shall allow a trained nurse to complete the standard PCA programming task (load library, scan medication, enter parameters, confirm, start therapy) in ≤5 minutes with zero use errors classified as harmful. | Summative usability test per IEC 62366-1 with n≥15 representative nurses; ≥90% task success; no harmful use errors. | UN-014 | Usability test (summative) |
| G5 | DI-021 | USAB | **CTF** | The device shall present therapy parameters, alarm states, and remaining battery life on a home screen readable from 1 m in ambient light up to 1000 lux. | Inspection and formative usability evaluation under controlled lighting; all key fields legible by n≥10 evaluators. | UN-014, UN-007 | Usability test (formative) |

### G6 — Power, Portability & Physical

_Battery endurance, charging, cleaning compatibility, lockbox tamper-evidence, and physical form factor._

| Group | DI ID | Category | Criticality | Requirement Statement | Acceptance Criteria | Traces to UN | Verification Method |
|---|---|---|---|---|---|---|---|
| G6 | DI-017 | FUNC | **CTF** | The device shall operate continuously on a single fully-charged internal lithium-ion battery for ≥150 hours under nominal therapy conditions (5 mL/hr continuous, 10 boluses/24 hr, default backlight). | Battery endurance bench test on n=5 production-equivalent units; mean runtime ≥150 hr, minimum ≥140 hr. | UN-011 | Bench test |
| G6 | DI-018 | FUNC | **CTF** | The device shall recharge from 0% to 100% state-of-charge in ≤4 hours from the supplied charger. | Bench test on n=5 units; all units reach 100% within 4 hr at 23 °C. | UN-011 | Bench test |
| G6 | DI-030 | FUNC | **CTF** | The device housing, touchscreen, and lockbox shall withstand cleaning and disinfection with hospital-approved quaternary ammonium and isopropyl alcohol wipes for the device service life without functional or cosmetic degradation. | Compatibility test: 1000 wipe cycles per agent on n=3 units; visual inspection and functional check pass. | UN-016 | Bench test |
| G6 | DI-032 | SAFE | **CTF** | The drug-cassette lockbox shall require a physical key or PIN-released latch and shall be tamper-evident, providing visible indication of any unauthorized opening. | Mechanical inspection and 50-cycle tamper-attempt test on n=5 lockboxes; all unauthorized entries leave visible evidence. | UN-020 | Bench test / inspection |
| G6 | DI-033 | FUNC | **CTF** | The device shall weigh ≤0.85 kg with a full medication cassette and shall provide both an IV-pole clamp and a belt-clip mounting interface. | Mass measurement on n=10 production-equivalent units; mechanical fit-check on standard IV pole and belt clip. | UN-022, UN-011 | Bench test / inspection |

### G7 — Connectivity & Interoperability

_Wireless networking and HL7 v2.5 / FHIR R4 EHR integration._

| Group | DI ID | Category | Criticality | Requirement Statement | Acceptance Criteria | Traces to UN | Verification Method |
|---|---|---|---|---|---|---|---|
| G7 | DI-022 | INTE | **S** | The device shall support 802.11 a/b/g/n/ac Wi-Fi (2.4 / 5 GHz) and Bluetooth 5.0 connectivity for integration with hospital networks. | Interoperability test against reference Wi-Fi infrastructure (WPA2-Enterprise); successful association and data exchange across 100 trials. | UN-012 | Bench test |
| G7 | DI-023 | INTE | **S** | The device shall publish therapy start, stop, parameter-change, bolus, and alarm events to a configurable EHR endpoint via HL7 v2.5 messaging, with optional HL7 FHIR R4 message profile. | Interface protocol test against reference HL7 listener; zero message validation errors over 1000-event run. | UN-012, UN-021 | Bench test (interface) |

### G8 — Cybersecurity & Data Integrity

_Authentication, TLS, signed firmware, and tamper-evident audit logging._

| Group | DI ID | Category | Criticality | Requirement Statement | Acceptance Criteria | Traces to UN | Verification Method |
|---|---|---|---|---|---|---|---|
| G8 | DI-024 | SAFE | **CTS** | The device shall implement cybersecurity controls — including authenticated firmware update, signed software, role-based access control, encrypted network communications (TLS 1.2+), and tamper-evident audit logging — to protect against unauthorized access and modification. | Cybersecurity test per IEC 81001-5-1 and FDA premarket cybersecurity guidance; penetration test with zero exploitable critical findings. | UN-013 | Cybersecurity test |
| G8 | DI-034 | INTE | **CTF** | The device shall provide a tamper-evident audit log capable of storing at least 10,000 events (therapy, alarm, programming, security) with timestamp, user ID, and event type, and shall expose the log via the service interface and EHR gateway. | Software test: generate 10,000 events, verify retention, integrity hash, and export; n=3 units. | UN-013, UN-012 | Software test |

### G9 — Regulatory, Labeling & Lifecycle Compliance

_SBOM, IEC 62304 Class C lifecycle, IEC 62366-1 usability process, UDI/GUDID, and serviceability._

| Group | DI ID | Category | Criticality | Requirement Statement | Acceptance Criteria | Traces to UN | Verification Method |
|---|---|---|---|---|---|---|---|
| G9 | DI-025 | INTE | **CTC** | The device manufacturer shall maintain a Software Bill of Materials (SBOM) covering all third-party and open-source software components, in CycloneDX or SPDX format, updated for each released firmware version. | Inspection of SBOM artifact; coverage cross-checked against build manifest; vulnerability monitoring procedure in place. | UN-013, UN-019 | Inspection |
| G9 | DI-026 | FUNC | **CTC** | Device software shall be developed under an IEC 62304 lifecycle process at Software Safety Class C, with documented requirements, architecture, unit/integration/system testing, and traceability. | Audit of software development files against IEC 62304 clauses 5 through 9; no major nonconformities. | UN-019 | Inspection / analysis |
| G9 | DI-027 | USAB | **CTC** | The device development shall apply a usability engineering process compliant with IEC 62366-1, including a use specification, user-interface specification, formative evaluations, and a summative validation. | Inspection of usability engineering file; all required deliverables present and approved. | UN-014, UN-019 | Inspection |
| G9 | DI-028 | INTE | **CTC** | The device, primary packaging, and shipping packaging shall bear a Unique Device Identifier (UDI) carrier and human-readable text per 21 CFR 830 and shall be submitted to GUDID. | Inspection of label artwork and GUDID submission record; UDI scannable on n=10 units. | UN-018 | Inspection |
| G9 | DI-029 | INTE | **CTC** | The Instructions for Use (IFU), labeling, and warning content shall comply with 21 CFR 801 and EU MDR Annex I labeling requirements, including the required opioid warning content. | Regulatory labeling review checklist; no open findings. | UN-018 | Inspection |
| G9 | DI-031 | FUNC | **S** | The device shall provide a serviceability menu (PIN-protected) exposing diagnostic logs, calibration routines, sensor readouts, and field-replaceable unit identifiers for biomedical engineering. | Functional verification of all service menu items; access gated by service PIN. | UN-017 | Software test |

## 5. Standards and Regulations Claimed

_[TBD — section required by GL-TMP-DC-002; content to be authored.]_

## 6. Dependencies and Assumptions

_[TBD — section required by GL-TMP-DC-002; content to be authored.]_

## 7. Open Items

_[TBD — section required by GL-TMP-DC-002; content to be authored.]_

## 8. Approvals

_[TBD — section required by GL-TMP-DC-002; content to be authored.]_

## 9. Revision History

| Rev | Date | Author | Description |
|---|---|---|---|
| B | 2026-04-12 | Ben Xavier | Reorganized into 9 functional groups (G1–G9). No change to DI content; added Group column, per-group H3 sections, and by-group traceability breakdown. |
| A | 2026-04-12 | Ben Xavier | Initial draft — Phase 4 of PDLC_DEMO. Authored from sample corpus (18 UN-/DI- files) with broad adaptation for realism. |

## Appendix — Sections retained from the previous structure

### Indications for Use

The PainEase PCA Advanced is indicated for the patient-controlled intravenous (IV) administration of opioid and non-opioid analgesics — including morphine, hydromorphone, fentanyl, and compatible local anesthetic agents — for the management of moderate to severe acute postoperative pain, acute pain associated with trauma or medical procedures, and chronic pain (including cancer-related pain) in adult and adolescent patients (≥12 years of age and ≥40 kg). The device is intended for use in hospitals, ambulatory surgical centers, and other supervised acute-care facilities under the direction of a qualified prescriber. Pediatric use below 12 years of age requires additional clinical judgment and is outside the scope of the cleared indication. The device is **not** indicated for intrathecal, epidural, or arterial administration; it is **not** intended for unsupervised home or ambulatory use; and it is **not** MRI-safe. PCA therapy with this device requires that the patient be cognitively capable of self-administration and that trained clinical staff be available for monitoring and alarm response. Standard opioid warnings — including risks of respiratory depression, sedation, and abuse — apply to all use of this device.

### Scope of This Document

This document captures the design inputs (system requirements) for the PainEase PCA Advanced (DEV-PP3500), derived from the validated user needs in `../user-needs/user-needs.md` (DHF-PP3500-UN-001). Each requirement carries a category, criticality classification, acceptance criteria, upstream user-need traces, and a planned verification method. Revision A is the Phase 4 baseline supporting design verification planning.

---

### Classification

**Category** — what kind of requirement:

| Category | Description |
|---|---|
| **Functional (FUNC)** | What the device does |
| **Performance (PERF)** | How well it does it — measurable |
| **Safety (SAFE)** | Hazard mitigations and protective features |
| **Usability (USAB)** | Human-factors requirements |
| **Interface (INTE)** | External interfaces (HW, SW, network, user) |

**Criticality** — how critical the requirement is:

| Class | Symbol | Definition |
|---|---|---|
| Critical to Safety | **CTS** | Failure can directly cause patient or operator harm |
| Critical to Function | **CTF** | Failure prevents the device from performing its intended use (no direct safety harm) |
| Critical to Compliance | **CTC** | Driven by regulation, standard, or label claim |
| Supporting | **S** | Enabling or nice-to-have; non-critical |

Every design input has exactly one Category and exactly one Criticality.

### Functional Groups

The design inputs in this document are organized into 9 functional groups aligned with the device architecture, matching the structure of `../user-needs/user-needs.md`.

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

### Traceability Summary

#### By Category and Criticality

| Category | CTS | CTF | CTC | S | Total |
|---|---|---|---|---|---|
| FUNC | 0 | 8 | 1 | 1 | 10 |
| PERF | 2 | 0 | 0 | 0 | 2 |
| SAFE | 9 | 1 | 0 | 0 | 10 |
| USAB | 1 | 2 | 1 | 0 | 4 |
| INTE | 1 | 2 | 3 | 2 | 8 |
| **Total** | **13** | **13** | **5** | **3** | **34** |

#### By Functional Group

| Group | DIs | CTS | CTF | CTC | S | UN Coverage |
|---|---|---|---|---|---|---|
| G1 Therapy Delivery | 4 | 3 | 1 | 0 | 0 | UN-001, UN-002, UN-003, UN-004 |
| G2 Drug Library & Medication Safety | 3 | 1 | 2 | 0 | 0 | UN-004, UN-008, UN-009 |
| G3 Alarms & Annunciation | 4 | 3 | 1 | 0 | 0 | UN-001, UN-006, UN-010 |
| G4 Hazard Controls & Essential Performance | 4 | 4 | 0 | 0 | 0 | UN-005, UN-015, UN-018 |
| G5 User Interface & Usability | 4 | 1 | 3 | 0 | 0 | UN-007, UN-014 |
| G6 Power, Portability & Physical | 5 | 0 | 5 | 0 | 0 | UN-011, UN-016, UN-020, UN-022 |
| G7 Connectivity & Interoperability | 2 | 0 | 0 | 0 | 2 | UN-012, UN-021 |
| G8 Cybersecurity & Data Integrity | 2 | 1 | 1 | 0 | 0 | UN-012, UN-013 |
| G9 Regulatory, Labeling & Lifecycle Compliance | 6 | 0 | 0 | 5 | 1 | UN-013, UN-014, UN-017, UN-018, UN-019 |
| **Total** | **34** | **13** | **13** | **5** | **3** | **22 of 22 UNs covered** |

The by-group "UN Coverage" column lists every UN traced by any DI in that group (which may include UNs whose primary group is elsewhere — e.g., DI-009 in G3 traces to UN-001 from G1).

Every user need UN-001 through UN-022 is covered by at least one design input above. The full UN ↔ DI bidirectional trace matrix lives in `../trace-matrix/un-to-di-trace-matrix.md`.
