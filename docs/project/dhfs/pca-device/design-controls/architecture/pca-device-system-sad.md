# PCA Device — System Software Architecture Description (SAD)

**DHF**: pca-device
**Product**: PP3500 — PainEase PCA Advanced
**Filing**: K210345 (510(k) + PCCP)
**Predicate**: PP3000 (K190567)
**Status**: Draft — first-stab scaffold derived from architecture + regulatory strategy
**Source strategy**: `docs/project/strategies/architecture-strategy.md`, `docs/project/strategies/regulatory-strategy.md`

_Demo artifact — illustrative, not a real submission SAD._

## 1. Purpose & Scope

This SAD describes the **on-device** software architecture of the PP3500 patient-controlled analgesia (PCA) pump. It covers software embedded in the pump itself — both SiMD pump firmware and the on-device SaMD clinician interface — plus the electromechanical hardware boundary. It does **not** cover the Connectivity Adapter or the Cloud Suite; those are separate DHFs and are referenced only at the trust boundary.

Scope rationale is locked by the regulatory strategy's **Filing Scope: PCA Device Alone** decision: the PP3500 510(k) covers only the PCA device. Adapter and Cloud artifacts are pulled into the filing via the composition manifest (cybersecurity only), not by extending this SAD.

## 2. System Context

```
          ┌───────────────────────┐
          │  Hospital IT          │  (external — not in scope)
          │  EHR / Pharmacy / IdP │
          └──────────┬────────────┘
                     │ HL7v2.5 / FHIR R4
          ┌──────────┴────────────┐
          │ Connectivity Adapter  │  (separate DHF — MDDS)
          │    (on-prem)          │
          └──────────┬────────────┘
                     │ TLS 1.3 mutual auth
          ┌──────────┴────────────┐
          │  PP3500 PCA Device    │  ◀── THIS SAD
          │  (SaMD + SiMD + HW)   │
          └──────────┬────────────┘
                     │ drug delivery
                 [ patient ]
```

Trust boundary: the PCA device treats the Adapter as untrusted over the wire. All inbound payloads (drug library updates, firmware updates, time sync) are authenticated and integrity-checked locally before application.

## 3. Composition

The PP3500 is a **combination** of three composition classes per `project.yml`:

| Class | Realization | Regulatory weight |
|---|---|---|
| **SaMD** | On-device clinician/patient UI running on the embedded Linux partition | IEC 62304 Class B/C per module |
| **SiMD** | Pump firmware (RTOS) controlling motor, sensors, alarms, drug library enforcement | IEC 62304 Class C |
| **Hardware** | Custom medical electrical: pump mechanism, occlusion/air-in-line sensors, display, patient bolus button, battery, enclosure | IEC 60601-1, 60601-1-2, 60601-2-24 |

## 4. Module Inventory

The PP3500 on-device software is decomposed into **seven modules**. Every module listed here is in scope for the 510(k) per the regulatory strategy's Critical-Requirement Carve-out (all seven carry CtS, CtF, or CtC-tagged requirements).

| # | Module | IEC 62304 Class | Type | Criticality tags | Summary |
|---|---|---|---|---|---|
| M1 | **Therapy Control** | C | SiMD | CtS, CtF, CtP | Pump motor control, flow rate regulation, bolus delivery, lockout enforcement |
| M2 | **Safety Monitor** | C | SiMD | CtS, CtC | Occlusion detection, air-in-line, dose ceiling, alarm prioritization (IEC 60601-1-8) |
| M3 | **Drug Library Enforcement** | C | SiMD | CtS, CtF | Local cache of cleared drug library; enforces dose/concentration limits at therapy start |
| M4 | **Clinician UI** | B | SaMD (on-device) | CtF, CtC | Touchscreen workflow for programming therapy, viewing status, silencing alarms |
| M5 | **Patient Interface** | B | SiMD | CtF | Bolus request button, lockout feedback, patient-facing status LEDs |
| M6 | **Cybersecurity & Comms** | B | SiMD | CtC, CtS | TLS stack, certificate store, firmware update verifier, audit log, Section 524B SBOM surface |
| M7 | **Device Platform** | C | SiMD | CtC | Boot, RTOS, watchdog, self-test, power management, time source, crypto primitives |

Electromechanical hardware (pump mechanism, sensors, display, enclosure) lives in the hardware design file and is not modeled as a software module here. Service tooling and labeling are out of SAD scope.

## 5. Module Responsibilities & Interfaces

### M1 — Therapy Control
- **Inputs**: programmed therapy from M4, drug library entry from M3, patient bolus from M5
- **Outputs**: motor commands (to HW), delivery log (to M6 for upload), alarm triggers (to M2)
- **Key invariants**: no delivery without an authorized drug library entry; no delivery during active CtS alarm
- **Primary standards**: IEC 62304 Class C, IEC 60601-2-24

### M2 — Safety Monitor
- **Inputs**: sensor telemetry from HW (pressure, air sensor, load cell), therapy state from M1
- **Outputs**: alarm state to M4/M5, interlock to M1
- **Key invariants**: alarm latency ≤ spec per IEC 60601-1-8; no silent degradation
- **Risk file linkage**: owns the top-level hazard chains for occlusion, air embolism, overinfusion

### M3 — Drug Library Enforcement
- **Inputs**: signed drug library payload via M6 (from Cloud Suite Drug Library Manager SaMD), therapy program from M4
- **Outputs**: dose/concentration bounds to M1, reject reason to M4
- **Key invariants**: only libraries with valid signature + version roll-forward are accepted; active therapy uses cached library until quiescent swap
- **PCCP linkage**: drug library updates are the primary PCCP change envelope

### M4 — Clinician UI (SaMD)
- **Inputs**: clinician input via touchscreen, status from M1/M2/M3
- **Outputs**: therapy program to M1, alarm acknowledgment to M2
- **Usability file linkage**: primary operating function per IEC 62366-1
- **Classification note**: SaMD portion of the combination product

### M5 — Patient Interface
- **Inputs**: patient bolus button, status queries
- **Outputs**: bolus request to M1, patient-facing indicators
- **Usability linkage**: secondary operator — patient use task analysis

### M6 — Cybersecurity & Comms
- **Inputs**: Ethernet/Wi-Fi link to Connectivity Adapter, USB service port
- **Outputs**: authenticated inbound payloads (drug library, firmware, time), outbound telemetry + audit log
- **Standards**: FDA Cybersecurity Guidance 2023, Section 524B, AAMI TIR57, IEC 81001-5-1
- **Trust boundary**: only module that talks to the Adapter

### M7 — Device Platform
- **Responsibility**: RTOS, boot chain, watchdog, self-test, time, power, crypto primitives used by M3/M6
- **Standards**: IEC 62304 Class C (SOUP management applies to RTOS + crypto libs)

## 6. Data & Trust Boundaries

- **Patient data** (therapy logs, bolus history): generated on-device, forwarded via M6 to Adapter. De-identified on egress per the data-flow spec.
- **Drug library**: authored in Cloud Suite Drug Library Manager SaMD, signed, distributed via Adapter, verified and cached by M3.
- **Firmware updates**: signed upstream, verified by M6, applied via M7 quiescent boot.
- **PHI boundary**: PHI does not leave the hospital — it crosses device → Adapter (on-prem) and stops there. Cloud egress is de-identified.

## 7. Standards & Guidance Mapping

| Standard / Guidance | Modules | Role |
|---|---|---|
| IEC 62304 | M1–M7 | Software lifecycle, safety classification |
| ISO 14971 | M1, M2, M3 | Risk management (hazard chains owned by Safety Monitor) |
| IEC 62366-1 | M4, M5 | Usability engineering |
| IEC 60601-1 / -1-2 / -1-8 / -2-24 | HW + M2 | Essential performance, alarms, PCA-specific |
| FDA Cybersecurity 2023 + Section 524B | M6, M7 | SBOM, threat model, update mechanism |
| FDA sw-functions guidance | M3, M4 | Device software function identification |
| FDA 510(k) SE guidance | all | Substantial equivalence to PP3000 predicate |
| PCCP (AI/ML + General) | M3, M6 | Drug library update envelope; future predictive-alarm SaMD slot |

## 8. Open Items

- Whether a predictive-alarm SaMD is a new PCA module (M8) or lives in Cloud Suite and feeds M2 via M6 — deferred to post-baseline PCCP planning.
- Module/DHF boundary for the on-device SaMD portion (M4) — currently modeled as a module of the PCA DHF rather than a separate DHF; revisit if FDA pre-sub feedback disagrees.

## 9. Changelog

| Date | Author | Summary |
|---|---|---|
| 2026-04-14 | Claude (first-stab) | Initial scaffold derived from architecture + regulatory strategy docs. Seven-module decomposition for PP3500 on-device software. Task 013. |
