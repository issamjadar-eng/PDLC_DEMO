# Software Requirements — PainEase PCA Advanced (DEV-PP3500)

> _Demo sample data — not for clinical use. Illustrative content for the PDLC_DEMO project._

| Field | Value |
|---|---|
| Document ID | DHF-PP3500-SRS-001 |
| Revision | A |
| Status | Draft |
| Owner | GlobalLogic Product Development |
| Device | PainEase PCA Advanced |
| Model | PP-3500 |
| Device ID | DEV-PP3500 |
| Software Safety Class | C (per IEC 62304 §4.3) — whole-system classification |
| Applicable Standards | IEC 62304 (software lifecycle), IEC 60601-1, IEC 60601-2-24, IEC 81001-5-1 (cybersecurity), IEC 62366-1 (usability), 21 CFR 820.30 |

## Scope of This Document

This document captures the software requirements (SRS) for the PainEase PCA Advanced (DEV-PP3500), derived from the system design inputs in `./design-inputs.md` (DHF-PP3500-DI-001). Each row decomposes a design input into one or more implementable software-level requirements with acceptance criteria, upstream DI traces, and a planned verification method. The PP3500 firmware is classified IEC 62304 Software Safety Class C at the system level; per-row safety classification is omitted in this demo (default per the task decision 2026-05-12). Revision A is the Phase 4 baseline supporting software verification planning and the trace-matrix DI→SW→V&V chain.

---

## Classification

**Category** — what kind of requirement:

| Category | Description |
|---|---|
| **Functional (FUNC)** | What the software does |
| **Performance (PERF)** | How well it does it — measurable |
| **Interface (INTE)** | Software interfaces (HW driver, network, user, EHR) |
| **Safety (SAFE)** | Hazard-mitigation software |
| **Security (SEC)** | Cybersecurity controls |
| **Usability (USAB)** | Software contribution to use-related risk mitigation |

**Criticality** — same scheme as DI (CTS / CTF / CTC / S). Every SW row has exactly one Category and one Criticality.

## Functional Groups

The SW requirements in this document follow the same 9-group structure as the DI doc so the trace stays legible end-to-end.

| # | Group | Scope |
|---|---|---|
| G1 | Therapy Delivery | Motor-control, bolus, lockout, cumulative-limit firmware |
| G2 | Drug Library & Medication Safety | Library loader, hard-limit enforcement, barcode flow |
| G3 | Alarms & Annunciation | Occlusion / air-in-line / over-infusion detection + alarm engine |
| G4 | Hazard Controls & Essential Performance | Free-flow detection, self-test, IEC 60601 boundary monitoring |
| G5 | User Interface & Usability | Numeric-entry widget, task-flow state machine, home-screen render |
| G6 | Power, Portability & Physical | Battery SoC, charge controller, lockbox monitoring |
| G7 | Connectivity & Interoperability | Wi-Fi/Bluetooth stack, HL7 v2.5, FHIR R4 |
| G8 | Cybersecurity & Data Integrity | Signed-update verifier, RBAC, TLS, audit log |
| G9 | Regulatory, Labeling & Lifecycle Compliance | IEC 62304 lifecycle scaffolding, service interface, UDI accessor |

## Software Requirements by Functional Group

### G1 — Therapy Delivery

_Closed-loop motor-control firmware, bolus delivery, lockout state machine, and cumulative-limit enforcement._

| Group | SW ID | Category | Criticality | Requirement Statement | Acceptance Criteria | Traces to DI | Verification Method |
|---|---|---|---|---|---|---|---|
| G1 | SW-001 | PERF | **CTS** | The pump-motor control firmware shall maintain commanded flow rate within ±5% (or ±0.5 mL/hr, whichever is greater) across 0.01–25 mL/hr by closed-loop position feedback on the syringe-drive encoder. | Software-in-the-loop test with calibrated encoder model; verify rate error within ±5% across 5 setpoints; n=100 control-loop iterations per setpoint. | DI-001 | Software test (VER-PP3500-SW-001) |
| G1 | SW-002 | FUNC | **CTS** | The bolus-delivery routine shall compute and deliver patient-activated bolus doses (0.01–20 mL) within ±5% delivered volume, integrating motor steps against the encoder-measured displacement. | Unit + integration test: simulate 30 bolus deliveries at 3 dose levels; all delivered volumes within ±5% of programmed. | DI-002 | Software test (VER-PP3500-SW-001) |
| G1 | SW-003 | FUNC | **CTF** | The lockout-interval state machine shall block any patient-requested bolus while the current lockout timer (1–99 min) is active, and shall log every blocked request to the audit log. | Software test: program lockout at 1, 15, 99 min; issue PCA-button presses during interval; verify zero bolus deliveries; verify each press is logged. | DI-003 | Software test (VER-PP3500-SW-002) |
| G1 | SW-004 | SAFE | **CTS** | The cumulative-dose tracker shall maintain rolling 1-hour and 4-hour delivered-volume sums per active therapy and shall block any bolus that would cause a sum to exceed its configured cap, regardless of programming path (PCA button, clinician menu, barcode-loaded order). | Software test: drive 50 boluses across all three entry paths against a 1-hr cap; verify zero over-limit deliveries; verify rolling-sum resets after window elapses. | DI-004 | Software test (VER-PP3500-SW-002) |
| G1 | SW-005 | FUNC | **CTF** | The therapy-parameter validator shall reject programming submissions whose rate, bolus, or lockout values fall outside library-defined hard limits, and shall return the violating field plus the active library version to the UI for display. | Unit test: 100 randomized invalid parameter sets against the reference library; verify 100% rejection; verify violation reason is structured (field + limit). | DI-001, DI-002, DI-005 | Software test |

### G2 — Drug Library & Medication Safety

_Drug-library loader, hard-limit enforcement at every programming entry-point, and barcode↔library matching._

| Group | SW ID | Category | Criticality | Requirement Statement | Acceptance Criteria | Traces to DI | Verification Method |
|---|---|---|---|---|---|---|---|
| G2 | SW-006 | SAFE | **CTS** | The hard-limit enforcement layer shall reject any programmed value exceeding the active library's hard cap, at all four programming entry points (manual UI, barcode-loaded order, clinician override, service-menu test mode), with no path bypass. | Code review: identify every parameter-write entry point; verify each calls the central enforcement routine. Software test: 200-medication test library; exercise every entry; zero hard-limit breaches. | DI-005 | Software test (VER-PP3500-SW-006) |
| G2 | SW-007 | FUNC | **CTF** | The drug-library loader shall accept signed library packages (≥200 medications), validate signature against the GlobalLogic root, persist the package to internal NVRAM, and display the active library version (vMAJ.MIN.PATCH) on the home screen and at therapy start. | Software test: load reference 200-medication library; verify count, signature pass, version banner visible at home + start, version recorded in audit log. | DI-015 | Software test |
| G2 | SW-008 | INTE | **CTF** | The barcode-scan handler shall capture 1D/2D barcodes from the integrated scanner, parse NDC and GS1 formats, perform a library lookup, and block therapy start with a non-dismissible alert if no match is found. | Bench + software test: 50-medication barcode set at 5 print qualities; ≥98% first-read success; mismatch produces blocking alert; no programming progresses past start. | DI-016 | Software test (VER-PP3500-SW-006) |

### G3 — Alarms & Annunciation

_Occlusion-pressure, air-in-line, and over-infusion detection algorithms plus the alarm-priority engine._

| Group | SW ID | Category | Criticality | Requirement Statement | Acceptance Criteria | Traces to DI | Verification Method |
|---|---|---|---|---|---|---|---|
| G3 | SW-009 | SAFE | **CTS** | The occlusion-detection routine shall sample downstream-pressure sensor output at ≥10 Hz, identify pressures in the 3–15 psi range as occlusion-class events, and raise a high-priority occlusion alarm within the response time required by IEC 60601-2-24 for the active flow rate. | Software-in-the-loop with sensor-emulator: inject 30 occlusion profiles across 3 flow rates; verify alarm raised within standard limit for all trials. | DI-007 | Software test (VER-PP3500-SW-003) |
| G3 | SW-010 | SAFE | **CTS** | The air-in-line detection algorithm shall identify single bubbles ≥50 µL and accumulated air ≥1 mL over a rolling 15-minute window using the in-line ultrasonic sensor, and shall raise a high-priority air-in-line alarm. | Software test against captured sensor traces with calibrated bubble injections; 100% detection at 0.05/0.1/0.5 mL across n=20 trials per condition. | DI-008 | Software test |
| G3 | SW-011 | SAFE | **CTS** | The over-infusion detector shall compute the difference between commanded delivered volume and encoder-measured delivered volume over a rolling 1-hour window and shall halt the motor and raise a high-priority alarm if the delta exceeds 10%. | Software-in-the-loop: inject motor-step / encoder-position faults; verify motor halt + alarm within 60 s for n=10 fault scenarios. | DI-009 | Software test |
| G3 | SW-012 | INTE | **CTF** | The alarm-priority engine shall route alarm events to the audio driver with IEC 60601-1-8-compliant priority melodies (high / medium / low) and shall mix per-priority SPL between 45 and 80 dB(A) at 1 m per configuration. | Acoustic measurement + software test: trigger each alarm class at min/mid/max SPL; verify melody and SPL bands. | DI-019 | Bench test |

### G4 — Hazard Controls & Essential Performance

_Software contributions to free-flow detection and IEC 60601 essential-performance monitoring._

| Group | SW ID | Category | Criticality | Requirement Statement | Acceptance Criteria | Traces to DI | Verification Method |
|---|---|---|---|---|---|---|---|
| G4 | SW-013 | SAFE | **CTS** | The door-state monitor shall sample the cassette-door sensor at ≥10 Hz, halt the motor within 200 ms of an open-door signal during active therapy, and require explicit operator acknowledgement before resuming delivery. | Bench + software test: open the door during active therapy at 3 flow rates; verify motor-halt time and resume-confirmation requirement; n=20 cycles. | DI-006 | Software test |
| G4 | SW-014 | SAFE | **CTC** | The power-on self-test shall validate motor encoder, pressure sensor, air-in-line sensor, watchdog timer, and battery voltage rails before allowing therapy programming, and shall annunciate a service-required alarm on any failed sub-test. | Software test: inject each sub-test failure; verify self-test reports the failed subsystem and the therapy path is blocked. | DI-010 | Software test |

### G5 — User Interface & Usability

_Numeric-entry widget with explicit decimal confirmation (CAPA-2023-001 mitigation), task-flow state machine, and home-screen renderer._

| Group | SW ID | Category | Criticality | Requirement Statement | Acceptance Criteria | Traces to DI | Verification Method |
|---|---|---|---|---|---|---|---|
| G5 | SW-015 | USAB | **CTS** | The numeric-entry widget shall render every entered value with an unambiguous decimal point (color-contrast ≥4.5:1, position-fixed display field), and shall require explicit operator confirmation of decimal placement before the value is accepted into therapy parameters. | Unit + summative usability test: verify decimal rendering in light/dark themes; n≥15 nurses complete the standard PCA programming task; zero decimal-misread errors. | DI-013 | Usability test (summative) |
| G5 | SW-016 | FUNC | **CTF** | The programming task-flow state machine shall guide the operator through load-library → scan-medication → enter-parameters → confirm → start in a fixed forward order, with explicit step-back, and shall log every transition. | Software test: traverse all 5 transitions and step-back paths; verify task-flow log captures each transition with timestamp + operator identity. | DI-020 | Software test |
| G5 | SW-017 | INTE | **CTF** | The home-screen renderer shall display active therapy parameters, current alarm state (if any), and remaining battery life in fields legible from 1 m at ambient illumination up to 1000 lux. | Inspection + software test: verify field placement and font sizes match the UI spec; render contrast measured with illuminance meter. | DI-021 | Inspection / bench test |
| G5 | SW-018 | INTE | **CTF** | The touchscreen input driver shall process touch events with ≤200 ms end-to-end latency (sensor → UI response) on the 3.5-inch display. | Bench test with high-speed camera: 100 touch events; measure response latency; p95 ≤200 ms. | DI-014 | Bench test |

### G6 — Power, Portability & Physical

_Software-controlled battery management, charge controller, and lockbox-state event capture._

| Group | SW ID | Category | Criticality | Requirement Statement | Acceptance Criteria | Traces to DI | Verification Method |
|---|---|---|---|---|---|---|---|
| G6 | SW-019 | FUNC | **CTF** | The battery state-of-charge estimator shall maintain SoC within ±5% of coulomb-counted truth and shall raise a medium-priority low-battery alarm at 30 minutes of projected runtime remaining. | Bench test: run a battery-discharge curve from 100% to 0%; compare estimator to coulomb-counter; verify alarm trigger point. | DI-017 | Bench test |
| G6 | SW-020 | INTE | **CTF** | The charge-controller firmware shall manage cell-balanced charging from 0% to 100% within 4 hours at 23 °C, and shall protect against over-current, over-temperature, and over-voltage by halting the charge cycle. | Bench test on n=5 production-equivalent boards; measure charge time + fault-trigger response. | DI-018 | Bench test |
| G6 | SW-021 | SAFE | **CTF** | The lockbox-state monitor shall poll the lockbox latch sensor at ≥1 Hz and shall record every open/close transition (timestamp, operator identity if known, latch source: key/PIN) in a tamper-evident sub-log. | Software test: 50 open/close cycles with mixed key/PIN sources; verify sub-log entries and tamper indicator state. | DI-032 | Software test |

### G7 — Connectivity & Interoperability

_Wireless stack integration, HL7 v2.5 message builder, FHIR R4 publisher._

| Group | SW ID | Category | Criticality | Requirement Statement | Acceptance Criteria | Traces to DI | Verification Method |
|---|---|---|---|---|---|---|---|
| G7 | SW-022 | INTE | **S** | The Wi-Fi / Bluetooth stack shall associate with WPA2-Enterprise networks (2.4 / 5 GHz, 802.11 a/b/g/n/ac) and Bluetooth 5.0, and shall automatically reconnect after link loss without operator intervention. | Bench test: 100 disassociation events; verify automatic reconnect within 30 s; verify no operator prompt. | DI-022 | Bench test |
| G7 | SW-023 | INTE | **S** | The HL7 v2.5 message builder shall encode therapy start, stop, parameter-change, bolus, and alarm events as ADT^A08 and RDE^O11 messages conformant to IHE Pharmacy profile transactions and shall deliver them to the configured EHR endpoint. | IHE Gazelle conformance test: PHARM-1 + PHARM-2 transactions pass with 0 errors over 1000-event run. | DI-023 | Conformance test |
| G7 | SW-024 | INTE | **S** | The FHIR R4 publisher shall serialize therapy administration events as MedicationAdministration resources conformant to US Core 6.0 and shall POST them to a configurable FHIR endpoint. | Validate 100 emitted resources with fhir-validator against US Core 6.0; 0 schema or profile errors. | DI-023 | Conformance test |

### G8 — Cybersecurity & Data Integrity

_Signed firmware verification, RBAC engine, TLS client, and tamper-evident audit log._

| Group | SW ID | Category | Criticality | Requirement Statement | Acceptance Criteria | Traces to DI | Verification Method |
|---|---|---|---|---|---|---|---|
| G8 | SW-025 | SEC | **CTS** | The firmware-update verifier shall validate the digital signature of every firmware bundle (RSA-3072 or higher, chain to the GlobalLogic signing root) before unlocking the bootloader, and shall refuse any bundle that fails verification with a logged reason code. | Negative test: present (a) valid bundle, (b) corrupted-signature bundle, (c) bundle signed by non-trust-anchor key; verify only (a) installs; verify the other two log a structured refusal. | DI-024 | Cybersecurity test |
| G8 | SW-026 | SEC | **CTS** | The RBAC engine shall enforce role-based access for clinician, biomed, service, and admin roles at every privileged operation (program therapy, edit library, export audit log, install firmware) with no operation reachable by an unauthenticated session. | Code review + penetration test: enumerate privileged operations; verify each has RBAC enforcement; attempt bypass with unauthenticated and lower-role sessions; verify rejection. | DI-024 | Cybersecurity test |
| G8 | SW-027 | SEC | **CTS** | All outbound network channels (EHR, FHIR, audit-log export, telemetry) shall use TLS 1.2 or higher with server certificate validation against a configured trust store; sessions to untrusted endpoints shall be refused. | Configure each outbound channel; attempt connection with valid, expired, and untrusted server certs; verify only valid succeeds. | DI-024 | Cybersecurity test |
| G8 | SW-028 | SEC | **CTF** | The tamper-evident audit log shall append every therapy, alarm, programming, and security event to a hash-chained on-board log of at least 10,000 entries, with timestamp, user ID, and event type. | Software test: generate 10,000 events; export log; verify hash-chain integrity intact; attempt log mutation; verify detection on next-event append. | DI-034 | Software test |
| G8 | SW-029 | INTE | **CTF** | The audit-log export interface shall expose the audit log over the service interface (PIN-gated) and over the EHR gateway (TLS + RBAC-authenticated) in a structured format (JSON or HL7). | Software test: export via both channels; verify content equivalence; verify gating works. | DI-034 | Software test |

### G9 — Regulatory, Labeling & Lifecycle Compliance

_IEC 62304 lifecycle scaffolding artifacts, service-menu diagnostic, and UDI accessor._

| Group | SW ID | Category | Criticality | Requirement Statement | Acceptance Criteria | Traces to DI | Verification Method |
|---|---|---|---|---|---|---|---|
| G9 | SW-030 | FUNC | **CTC** | The device firmware shall be developed and tested under the IEC 62304 Class C lifecycle, with documented unit-test coverage ≥80% on safety-classified modules (G1, G3, G4, G6, G8), integration-test coverage of every inter-module interface, and a system test suite traceable to every SRS row. | Audit firmware development files against IEC 62304 clauses 5 through 9; review coverage reports; verify trace from every SW-NNN row to ≥1 test artifact. | DI-026 | Inspection / analysis |
| G9 | SW-031 | FUNC | **S** | The service-menu interface shall be PIN-gated and shall expose diagnostic logs, calibration routines, sensor readouts, and field-replaceable unit identifiers for biomedical engineering use. | Software test: verify PIN gate; verify each diagnostic returns expected payload on n=3 service-mode entries. | DI-031 | Software test |
| G9 | SW-032 | INTE | **CTC** | The device-info accessor shall return the UDI (DI + PI components per 21 CFR 830) to the label-render and EHR-gateway interfaces, populated at manufacturing time and read-only at runtime. | Unit test: read UDI on n=10 production-equivalent units; verify format and content match GUDID submission record. | DI-028 | Software test / inspection |

## Traceability Summary

### By Category and Criticality

| Category | CTS | CTF | CTC | S | Total |
|---|---|---|---|---|---|
| FUNC | 0 | 6 | 2 | 1 | 9 |
| PERF | 1 | 0 | 0 | 0 | 1 |
| SAFE | 7 | 1 | 0 | 0 | 8 |
| USAB | 1 | 0 | 0 | 0 | 1 |
| INTE | 0 | 6 | 1 | 3 | 10 |
| SEC | 3 | 0 | 0 | 0 | 3 |
| **Total** | **12** | **13** | **3** | **4** | **32** |

### By Functional Group

| Group | SWs | DI Coverage |
|---|---|---|
| G1 Therapy Delivery | 5 | DI-001, DI-002, DI-003, DI-004, DI-005 |
| G2 Drug Library & Medication Safety | 3 | DI-005, DI-015, DI-016 |
| G3 Alarms & Annunciation | 4 | DI-007, DI-008, DI-009, DI-019 |
| G4 Hazard Controls & Essential Performance | 2 | DI-006, DI-010 |
| G5 User Interface & Usability | 4 | DI-013, DI-014, DI-020, DI-021 |
| G6 Power, Portability & Physical | 3 | DI-017, DI-018, DI-032 |
| G7 Connectivity & Interoperability | 3 | DI-022, DI-023 |
| G8 Cybersecurity & Data Integrity | 5 | DI-024, DI-034 |
| G9 Regulatory, Labeling & Lifecycle Compliance | 3 | DI-026, DI-028, DI-031 |
| **Total** | **32** |  |

DI rows covered by at least one SW: DI-001, DI-002, DI-003, DI-004, DI-005, DI-006, DI-007, DI-008, DI-009, DI-010, DI-013, DI-014, DI-015, DI-016, DI-017, DI-018, DI-019, DI-020, DI-021, DI-022, DI-023, DI-024, DI-026, DI-028, DI-031, DI-032, DI-034. DI rows without direct SW decomposition (handled by hardware, mechanical, or labeling artifacts rather than software): DI-011 (biocompat), DI-012 (EMC), DI-025 (SBOM artifact), DI-027 (usability engineering process), DI-029 (labeling), DI-030 (cleaning compatibility), DI-033 (mass/mount fit-check). These are tracked under their respective non-software work products.

## Revision History

| Rev | Date | Author | Description |
|---|---|---|---|
| A | 2026-05-12 | Ben Xavier | Initial draft — Phase 2 of task 049. 32 SW rows across 9 functional groups mirroring the DI structure. Demo content; IEC 62304 Class C system-level classification; per-row safety class omitted per task decision. |
