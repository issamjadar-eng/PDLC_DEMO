# Design Inputs — Connectivity Adapter (CA-1000)

> _Demo sample data — not for clinical use. Illustrative content for the PDLC_DEMO project._

| Field | Value |
|---|---|
| Document ID | DHF-CA1000-DI-001 |
| Revision | A |
| Status | Draft |
| Owner | GlobalLogic Product Development |
| Component | Connectivity Adapter |
| Model | CA-1000 |
| Component ID | DEV-CA1000 |
| Classification | MDDS (post-2015 FDA reclassification — non-device) |
| Filing Posture | Not separately filed; referenced by PP3500 510(k) (K210345) for cybersecurity posture |
| Parent System | PainEase PCA Advanced (PP-3500, K210345) |
| Applicable Standards | IEC 81001-5-1, IEC 62304 Class B, HL7 v2.5, HL7 FHIR R4, IEC 62443-4-1, ISO 13485 |

## Scope of This Document

This document captures the design inputs (system requirements) for the Connectivity Adapter (CA-1000), derived from the validated user needs in `../user-needs/user-needs.md` (DHF-CA1000-UN-001). Each requirement carries a category, criticality classification, acceptance criteria, upstream user-need traces, and a planned verification method. Revision A is the baseline supporting design verification planning.

---

## Classification

**Category** — what kind of requirement:

| Category | Description |
|---|---|
| **Functional (FUNC)** | What the Adapter does |
| **Performance (PERF)** | How well it does it — measurable |
| **Safety (SAFE)** | Hazard mitigations and protective features |
| **Interface (INTE)** | External interfaces (HL7/FHIR, IdP, SIEM, pump) |
| **Security (SEC)** | Cybersecurity controls |

**Criticality** — how critical the requirement is:

| Class | Symbol | Definition |
|---|---|---|
| Critical to Safety | **CTS** | Failure can directly or indirectly contribute to patient or operator harm |
| Critical to Function | **CTF** | Failure prevents the Adapter from performing its intended use |
| Critical to Compliance | **CTC** | Driven by regulation, standard, or filing-posture preservation (MDDS boundary) |
| Supporting | **S** | Enabling or non-critical |

## Functional Groups

| # | Group | Scope |
|---|---|---|
| A1 | Device Ingest | Mutual-TLS pump endpoint; persistence; reliability |
| A2 | EHR / Pharmacy Bridge | HL7v2.5 + FHIR R4 outbound |
| A3 | Drug Library Distributor | Pass-through signed distribution |
| A4 | Firmware Update Relay | Pass-through signed distribution |
| A5 | Operator Console | Biomed / IT web UI |
| A6 | Cybersecurity & Identity | TLS, IdP, audit, SBOM |
| A7 | Platform & Lifecycle | Install, upgrade, observability |

## Design Inputs by Functional Group

### A1 — Device Ingest

| Group | DI ID | Category | Criticality | Requirement Statement | Acceptance Criteria | Traces to UN | Verification Method |
|---|---|---|---|---|---|---|---|
| A1 | DI-001 | PERF | **CTF** | The Adapter shall accept concurrent mutual-TLS sessions from at least 500 distinct pumps on a single ingest endpoint with steady-state per-pump telemetry intervals of ≤ 5 s. | Load test: 500 simulated pumps, 5-second heartbeats, 1-hour soak; ≤ 0.1% sessions dropped; p99 ingest latency ≤ 250 ms. | UN-001 | Bench load test (VER-CA-LT-001) |
| A1 | DI-002 | SAFE | **CTS** | The Adapter shall durably persist every pump-originated alarm and therapy event to local non-volatile storage before acknowledging the event to the originating pump. | Fault-injection test: kill Adapter process after pump send and before ACK reply; verify no event is acknowledged that is not on disk. | UN-002 | Fault-injection test (VER-CA-FI-001) |
| A1 | DI-003 | FUNC | **CTF** | The Adapter shall replay queued pump-originated events to downstream consumers (EHR / FHIR / SIEM) once consumer connectivity is restored, in original chronological order, after consumer outages of up to 24 hours. | Soak test: disable EHR consumer for 24 h with active pump telemetry; restore consumer; verify all events delivered in order; no duplicates. | UN-002, UN-003 | Integration test (VER-CA-IT-002) |

### A2 — EHR / Pharmacy Bridge

| Group | DI ID | Category | Criticality | Requirement Statement | Acceptance Criteria | Traces to UN | Verification Method |
|---|---|---|---|---|---|---|---|
| A2 | DI-004 | INTE | **CTF** | The Adapter shall emit HL7v2.5 ADT^A08 and RDE^O11 messages for therapy administration events, conformant to the IHE Pharmacy profile transaction PHARM-1 / PHARM-2. | IHE Gazelle conformance test suite: PHARM-1 and PHARM-2 pass with 0 errors. | UN-004 | Conformance test (VER-CA-CT-001) |
| A2 | DI-005 | INTE | **CTF** | The Adapter shall emit FHIR R4 MedicationAdministration resources via REST POST to a configurable endpoint, validating against the US Core 6.0 profile. | Validate sample output against US Core 6.0 MedicationAdministration profile via fhir-validator; 0 errors. | UN-005 | Conformance test (VER-CA-CT-002) |
| A2 | DI-006 | FUNC | **CTC** | The Adapter shall expose a configuration API to add, modify, and remove downstream HL7 and FHIR endpoints (including TLS certs and field mappings) without restarting the Adapter process. | Bench: add a new HL7 endpoint while pump traffic flows; observe events delivered to new endpoint within 30 s; pump sessions uninterrupted. | UN-006 | Integration test (VER-CA-IT-003) |

### A3 — Drug Library Distributor

| Group | DI ID | Category | Criticality | Requirement Statement | Acceptance Criteria | Traces to UN | Verification Method |
|---|---|---|---|---|---|---|---|
| A3 | DI-007 | SEC | **CTS** | The Adapter shall verify the digital signature of every drug-library payload (RSA-3072 or higher, chain to GlobalLogic signing root) before queuing the payload for pump distribution, and shall refuse any payload that fails verification. | Negative test: submit (a) valid payload, (b) payload with corrupted signature, (c) payload signed by a non-trust-anchor key; verify only (a) is queued; refusals are logged. | UN-008 | Security test (VER-CA-ST-001) |
| A3 | DI-008 | SAFE | **CTC** | The Adapter shall not modify the byte content, structure, or metadata of any drug-library payload between receipt and pump distribution, so the payload's signature remains valid end-to-end. | Bench: take a signed payload byte-fingerprint at ingress; capture the payload byte-fingerprint at egress to a pump; verify SHA-256 hashes match. | UN-007 | Bench test (VER-CA-BT-001) |
| A3 | DI-009 | FUNC | **CTF** | The Adapter shall support scheduled rollout of a drug-library payload to a configurable cohort of pumps (by serial set, by ward, or by all-fleet) with per-pump status (queued / delivered / activated / failed). | Bench: schedule rollout to a cohort of 20 simulated pumps; verify per-pump status transitions are reported in the operator console and via the rollout API. | UN-009 | Integration test (VER-CA-IT-004) |

### A4 — Firmware Update Relay

| Group | DI ID | Category | Criticality | Requirement Statement | Acceptance Criteria | Traces to UN | Verification Method |
|---|---|---|---|---|---|---|---|
| A4 | DI-010 | SEC | **CTS** | The Adapter shall verify the digital signature of every firmware bundle before queuing it for pump distribution and shall refuse any bundle that fails verification, regardless of whether the bundle was received from Cloud Suite or locally uploaded. | Negative test: try to upload (a) valid signed bundle, (b) unsigned bundle, (c) bundle signed by a non-trust-anchor key; verify only (a) is queued; refusals are logged with operator identity. | UN-010 | Security test (VER-CA-ST-002) |
| A4 | DI-011 | FUNC | **CTF** | The Adapter shall support staged firmware rollout with operator-controlled pause / resume / abort, per-pump status, and configurable concurrency (default ≤ 5 concurrent pump upgrades). | Bench: schedule rollout to 20 simulated pumps; pause at 5/20; resume; abort at 12/20; verify state transitions and that no pump exceeds the concurrency limit. | UN-011 | Integration test (VER-CA-IT-005) |

### A5 — Operator Console

| Group | DI ID | Category | Criticality | Requirement Statement | Acceptance Criteria | Traces to UN | Verification Method |
|---|---|---|---|---|---|---|---|
| A5 | DI-012 | FUNC | **CTF** | The operator console shall render fleet health (pumps connected, last heartbeat, firmware revision, library revision, certificate expiry) with end-to-end refresh latency ≤ 30 s under steady-state load of 500 connected pumps. | Bench: 500 simulated pumps reporting on 5-s intervals; measure UI refresh latency from pump-state change to console reflection; p95 ≤ 30 s. | UN-012 | System test (VER-CA-SY-001) |
| A5 | DI-013 | FUNC | **CTC** | The audit-log search interface shall support filtering by pump serial, user identity, ISO-8601 timestamp range, and event class, returning results in ≤ 5 s for queries spanning ≤ 30 days against a 1M-event log. | Bench: seed a 1M-event audit log; execute representative queries; measure response time; p95 ≤ 5 s. | UN-013 | Performance test (VER-CA-PT-001) |
| A5 | DI-014 | USAB | **S** | The console shall present a "Needs Attention" landing page summarizing offline pumps (> 24 h), certificates expiring within 30 days, and failed library / firmware rollouts within the past 7 days, refreshed at least every 5 minutes. | Usability prototype validation: ≥ 4 of 5 biomed participants complete the task "show me what needs attention today" in ≤ 60 s without prompting. | UN-014 | Usability test (VER-CA-UT-001) |

### A6 — Cybersecurity & Identity

| Group | DI ID | Category | Criticality | Requirement Statement | Acceptance Criteria | Traces to UN | Verification Method |
|---|---|---|---|---|---|---|---|
| A6 | DI-015 | SEC | **CTS** | The Adapter shall authenticate human users exclusively via SAML 2.0 or OIDC against a hospital-configured IdP; the Adapter shall maintain no locally provisioned interactive user accounts. | Penetration test: attempt password / token-based authentication directly against the Adapter (bypassing IdP); verify rejection. Inspect codebase for any local-account code paths; verify none reachable in shipped build. | UN-015 | Security test (VER-CA-ST-003) |
| A6 | DI-016 | INTE | **CTC** | The Adapter shall stream its security audit log in real time to a configurable syslog-TLS endpoint, formatted in CEF (Common Event Format) with end-to-end emission latency ≤ 5 s from event occurrence to syslog receipt. | Bench: configure syslog endpoint; trigger 1000 representative events; verify CEF-conformant lines received within p95 ≤ 5 s; 0 dropped. | UN-016 | Integration test (VER-CA-IT-006) |
| A6 | DI-017 | SEC | **CTS** | The pump↔Adapter ingest endpoint shall enforce mutual TLS 1.3 with X.509 client-certificate validation; sessions with invalid, expired, or untrusted client certificates shall be rejected at TLS handshake and the rejection logged. | Negative test: attempt connection with (a) no client cert, (b) expired client cert, (c) self-signed client cert; verify TLS handshake failure; verify audit log entries. | UN-017 | Security test (VER-CA-ST-004) |
| A6 | DI-018 | SEC | **CTC** | Each released Adapter version shall include a CycloneDX or SPDX SBOM accessible to authenticated hospital security users via the operator console and via an unauthenticated download URL on the GlobalLogic public site for that version. | Inspect release artifacts: SBOM file present, valid SPDX-2.3 or CycloneDX-1.4 schema; ≥ one runtime dependency listed; SBOM URL returns 200 from public site. | UN-018 | Document review (VER-CA-DR-001) |

### A7 — Platform & Lifecycle

| Group | DI ID | Category | Criticality | Requirement Statement | Acceptance Criteria | Traces to UN | Verification Method |
|---|---|---|---|---|---|---|---|
| A7 | DI-019 | FUNC | **CTF** | The Adapter shall install on RHEL 9, Ubuntu 22.04 LTS, and Ubuntu 24.04 LTS from a single signed package, with installation completing in ≤ 30 minutes on a baseline host (8 vCPU, 32 GiB RAM, 500 GB SSD) and requiring no manual library / dependency steps. | Install rehearsal on each target OS; measure end-to-end time; verify Adapter passes self-test post-install. | UN-019 | System test (VER-CA-SY-002) |
| A7 | DI-020 | PERF | **CTF** | The Adapter shall support in-place upgrade from version N to N+1 with no pump↔Adapter session disconnect exceeding 60 s in p99, and zero loss of in-flight pump-originated events. | Soak: 500 simulated pumps active; trigger upgrade; measure max session-disconnect duration; verify event count pre/post matches expected. | UN-020 | System test (VER-CA-SY-003) |
| A7 | DI-021 | INTE | **S** | The Adapter shall expose a `/metrics` endpoint in Prometheus exposition format (text or OpenMetrics), with at minimum: connected-pump count, ingest event rate, queue depth per downstream, audit-log emission rate, certificate-expiry countdown. | Bench: scrape `/metrics`; validate format with promtool; verify required metrics present. | UN-021 | Integration test (VER-CA-IT-007) |
