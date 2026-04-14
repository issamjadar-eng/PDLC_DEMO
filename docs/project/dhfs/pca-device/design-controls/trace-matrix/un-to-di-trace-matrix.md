# User Needs ↔ Design Inputs Trace Matrix — PainEase PCA Advanced (DEV-PP3500)

> _Demo sample data — not for clinical use. Illustrative content for the PDLC_DEMO project._

| Field | Value |
|---|---|
| Document ID | DHF-PP3500-TM-001 |
| Revision | A |
| Status | Draft |
| Device | PainEase PCA Advanced (DEV-PP3500) |
| 510(k) | K210345 |
| Owner | GlobalLogic Product Development |
| Upstream Docs | `../user-needs/user-needs.md` (DHF-PP3500-UN-001), `../requirements/design-inputs.md` (DHF-PP3500-DI-001) |

## Purpose

This document is the bidirectional trace matrix linking every User Need (UN) to the Design Inputs (DIs) that implement or verify it, and vice versa. It is organized by the same 9 functional groups used in the upstream documents.

## Forward Trace — UN → DI (by functional group)

### G1 — Therapy Delivery

| UN ID | User Need (summary) | Traced DIs |
|---|---|---|
| UN-001 | On-demand patient-titrated bolus delivery within prescribed limits | DI-001, DI-002, DI-009 |
| UN-002 | Programmable continuous (basal) infusion alongside PCA bolus | DI-001 |
| UN-003 | Clinician-enforced lockout intervals and 1 hr / 4 hr cumulative limits | DI-003, DI-004 |

### G2 — Drug Library & Medication Safety

| UN ID | User Need (summary) | Traced DIs |
|---|---|---|
| UN-004 | Hard-limit enforcement across all programming pathways | DI-004, DI-005 |
| UN-008 | Bedside barcode verification of medication and patient | DI-016 |
| UN-009 | Load and confirm institution-approved drug library version | DI-005, DI-015 |

### G3 — Alarms & Annunciation

| UN ID | User Need (summary) | Traced DIs |
|---|---|---|
| UN-006 | Detect occlusion and air-in-line and alert clinician | DI-007, DI-008, DI-009 |
| UN-010 | Audible, distinguishable alarms without alarm fatigue | DI-019 |

### G4 — Hazard Controls & Essential Performance

| UN ID | User Need (summary) | Traced DIs |
|---|---|---|
| UN-005 | Prevent gravity-driven free flow when set is removed | DI-006, DI-010 |
| UN-015 | Biocompatible patient-contacting materials | DI-011 |

### G5 — User Interface & Usability

| UN ID | User Need (summary) | Traced DIs |
|---|---|---|
| UN-007 | Unambiguous decimal-point dose entry and display | DI-013, DI-021 |
| UN-014 | Trained-nurse operability with minimized programming use errors | DI-013, DI-014, DI-020, DI-021, DI-027 |

### G6 — Power, Portability & Physical

| UN ID | User Need (summary) | Traced DIs |
|---|---|---|
| UN-011 | Battery operation across a full nursing shift cycle | DI-017, DI-018, DI-033 |
| UN-016 | Cleaning and disinfection compatibility with hospital protocols | DI-030 |
| UN-020 | Tamper-evident, physically secure controlled-substance lockbox | DI-032 |
| UN-022 | Light, ergonomic, IV-pole / belt-clip mountable | DI-033 |

### G7 — Connectivity & Interoperability

| UN ID | User Need (summary) | Traced DIs |
|---|---|---|
| UN-012 | Wireless EHR/EMR integration without manual transcription | DI-022, DI-023, DI-034 |
| UN-021 | Optional HL7 FHIR publication for smart-pump interoperability | DI-023 |

### G8 — Cybersecurity & Data Integrity

| UN ID | User Need (summary) | Traced DIs |
|---|---|---|
| UN-013 | Protect patient data and therapy integrity through life | DI-024, DI-025, DI-034 |

### G9 — Regulatory, Labeling & Lifecycle Compliance

| UN ID | User Need (summary) | Traced DIs |
|---|---|---|
| UN-017 | Diagnostic logs and field-replaceable parts for PM | DI-031 |
| UN-018 | UDI, symbols, and labeling per 21 CFR 801/830 and EU MDR | DI-010, DI-012, DI-028, DI-029 |
| UN-019 | Software lifecycle commensurate with safety class | DI-025, DI-026, DI-027 |

## Reverse Trace — DI → UN (by functional group)

### G1 — Therapy Delivery

| DI ID | Category | Criticality | Requirement (summary) | Traces to UN |
|---|---|---|---|---|
| DI-001 | PERF | CTS | Continuous flow rate 0.01–25 mL/hr at ±5% accuracy | UN-001, UN-002 |
| DI-002 | PERF | CTS | PCA bolus 0.01–20 mL at ±5% delivered-volume accuracy | UN-001 |
| DI-003 | FUNC | CTF | Programmable lockout interval 1–99 minutes | UN-003 |
| DI-004 | SAFE | CTS | Enforce 1 hr / 4 hr cumulative dose limits | UN-003, UN-004 |

### G2 — Drug Library & Medication Safety

| DI ID | Category | Criticality | Requirement (summary) | Traces to UN |
|---|---|---|---|---|
| DI-005 | SAFE | CTS | Drug-library hard-limit enforcement across all paths | UN-004, UN-009 |
| DI-015 | FUNC | CTF | On-board ≥200 medication library with version display | UN-009 |
| DI-016 | FUNC | CTF | Integrated 1D/2D barcode scanner with library matching | UN-008 |

### G3 — Alarms & Annunciation

| DI ID | Category | Criticality | Requirement (summary) | Traces to UN |
|---|---|---|---|---|
| DI-007 | SAFE | CTS | Downstream occlusion detection 3–15 psi with alarm | UN-006 |
| DI-008 | SAFE | CTS | Air-in-line detection ≥50 µL with high-priority alarm | UN-006 |
| DI-009 | SAFE | CTS | Over-infusion detection and motor halt on >10% deviation | UN-001, UN-006 |
| DI-019 | INTE | CTF | IEC 60601-1-8 audible alarms 45–80 dB(A) | UN-010 |

### G4 — Hazard Controls & Essential Performance

| DI ID | Category | Criticality | Requirement (summary) | Traces to UN |
|---|---|---|---|---|
| DI-006 | SAFE | CTS | Anti-siphon free-flow protection on administration set | UN-005 |
| DI-010 | SAFE | CTS | IEC 60601-1 and 60601-2-24 electrical safety compliance | UN-005, UN-018 |
| DI-011 | SAFE | CTS | ISO 10993-1 biocompatibility for patient-contact surfaces | UN-015 |
| DI-012 | INTE | CTS | IEC 60601-1-2 EMC immunity and emissions compliance | UN-018 |

### G5 — User Interface & Usability

| DI ID | Category | Criticality | Requirement (summary) | Traces to UN |
|---|---|---|---|---|
| DI-013 | USAB | CTS | Unambiguous decimal-point dose entry with confirmation | UN-007, UN-014 |
| DI-014 | FUNC | CTF | 3.5-inch color LCD touchscreen UI for therapy programming | UN-014 |
| DI-020 | USAB | CTF | Standard PCA programming task ≤5 min, no harmful errors | UN-014 |
| DI-021 | USAB | CTF | Home screen legible from 1 m up to 1000 lux ambient | UN-014, UN-007 |

### G6 — Power, Portability & Physical

| DI ID | Category | Criticality | Requirement (summary) | Traces to UN |
|---|---|---|---|---|
| DI-017 | FUNC | CTF | ≥150 hr battery endurance under nominal therapy | UN-011 |
| DI-018 | FUNC | CTF | Recharge 0–100% in ≤4 hr | UN-011 |
| DI-030 | FUNC | CTF | Cleaning compatibility with QAC and IPA wipes | UN-016 |
| DI-032 | SAFE | CTF | Key/PIN lockbox with tamper-evident indication | UN-020 |
| DI-033 | FUNC | CTF | ≤0.85 kg with IV-pole and belt-clip mounting | UN-022, UN-011 |

### G7 — Connectivity & Interoperability

| DI ID | Category | Criticality | Requirement (summary) | Traces to UN |
|---|---|---|---|---|
| DI-022 | INTE | S | 802.11 a/b/g/n/ac Wi-Fi and Bluetooth 5.0 | UN-012 |
| DI-023 | INTE | S | HL7 v2.5 events with optional FHIR R4 profile | UN-012, UN-021 |

### G8 — Cybersecurity & Data Integrity

| DI ID | Category | Criticality | Requirement (summary) | Traces to UN |
|---|---|---|---|---|
| DI-024 | SAFE | CTS | Cybersecurity controls — auth, signed FW, RBAC, TLS, audit | UN-013 |
| DI-034 | INTE | CTF | Tamper-evident audit log ≥10,000 events with export | UN-013, UN-012 |

### G9 — Regulatory, Labeling & Lifecycle Compliance

| DI ID | Category | Criticality | Requirement (summary) | Traces to UN |
|---|---|---|---|---|
| DI-025 | INTE | CTC | SBOM (CycloneDX/SPDX) maintained per firmware release | UN-013, UN-019 |
| DI-026 | FUNC | CTC | IEC 62304 Class C software lifecycle process | UN-019 |
| DI-027 | USAB | CTC | IEC 62366-1 usability engineering process | UN-014, UN-019 |
| DI-028 | INTE | CTC | UDI carrier per 21 CFR 830 and GUDID submission | UN-018 |
| DI-029 | INTE | CTC | IFU and labeling per 21 CFR 801 and EU MDR Annex I | UN-018 |
| DI-031 | FUNC | S | PIN-protected serviceability menu with diagnostics | UN-017 |

## Coverage Summary

- Total User Needs: 22
- Total Design Inputs: 34
- Total UN ↔ DI trace links: 46
- UN→DI coverage: 22 / 22 (100%) — zero orphan user needs
- DI→UN coverage: 34 / 34 (100%) — zero orphan design inputs
- Average DIs per UN: 2.09
- Average UNs per DI: 1.35

## Revision History

| Rev | Date | Author | Description |
|---|---|---|---|
| A | 2026-04-12 | Ben Xavier | Initial version — bidirectional trace matrix aligned with user-needs.md Rev B and design-inputs.md Rev B. |
