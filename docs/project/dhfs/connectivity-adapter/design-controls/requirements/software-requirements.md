# Software Requirements — Connectivity Adapter (CA-1000)

> _Demo sample data — not for clinical use. Illustrative content for the PDLC_DEMO project._

| Field | Value |
|---|---|
| Document ID | DHF-CA1000-SRS-001 |
| Revision | A |
| Status | Draft |
| Owner | GlobalLogic Product Development |
| Component | Connectivity Adapter |
| Model | CA-1000 |
| Component ID | DEV-CA1000 |
| Software Safety Class | B (per IEC 62304 §4.3) — whole-system classification |
| Applicable Standards | IEC 62304, IEC 81001-5-1, HL7 v2.5, HL7 FHIR R4, IHE Pharmacy, IEC 62443-4-1, ISO 13485 |

## Scope of This Document

This document captures the software requirements (SRS) for the Connectivity Adapter (CA-1000), derived from the system design inputs in `./design-inputs.md` (DHF-CA1000-DI-001). Each row decomposes a design input into one or more implementable software-level requirements. The CA-1000 is classified IEC 62304 Software Safety Class B at the system level (MDDS posture); per-row safety classification is omitted in this demo. Revision A is the baseline supporting software verification planning and the trace-matrix DI→SW→V&V chain.

---

## Classification

**Category** — what kind of requirement:

| Category | Description |
|---|---|
| **Functional (FUNC)** | What the Adapter software does |
| **Performance (PERF)** | How well it does it — measurable |
| **Interface (INTE)** | External interfaces (HL7/FHIR, IdP, SIEM, pump) |
| **Safety (SAFE)** | Hazard-mitigation software |
| **Security (SEC)** | Cybersecurity controls |
| **Reliability (RELY)** | Availability, durability, recovery |

**Criticality** — same scheme as DI (CTS / CTF / CTC / S).

## Functional Groups

The SW requirements follow the same 7-module-group structure as the DI doc.

| # | Group | Scope |
|---|---|---|
| A1 | Device Ingest | mTLS listener, durable event store, replay engine |
| A2 | EHR / Pharmacy Bridge | HL7v2.5 builder, FHIR publisher, endpoint config API |
| A3 | Drug Library Distributor | Signature verification, byte-fidelity store, rollout scheduler |
| A4 | Firmware Update Relay | Signature verification, staged-rollout state machine |
| A5 | Operator Console | Fleet health view-model, audit-log search, attention-page |
| A6 | Cybersecurity & Identity | IdP integration, CEF audit streamer, mTLS validator, SBOM |
| A7 | Platform & Lifecycle | Installer, upgrade orchestrator, Prometheus metrics |

## Software Requirements by Functional Group

### A1 — Device Ingest

| Group | SW ID | Category | Criticality | Requirement Statement | Acceptance Criteria | Traces to DI | Verification Method |
|---|---|---|---|---|---|---|---|
| A1 | SW-001 | PERF | **CTF** | The mutual-TLS ingest listener shall accept ≥500 concurrent pump sessions on a single endpoint with steady-state 5 s telemetry intervals at p99 ingest latency ≤250 ms. | Load test: 500 simulated pumps, 5 s heartbeats, 1-hour soak; ≤0.1% sessions dropped; p99 ≤250 ms. | DI-001 | Software / load test (VER-CA-LT-001) |
| A1 | SW-002 | SAFE | **CTS** | The durable event-queue writer shall fsync every pump-originated alarm and therapy event to local non-volatile storage **before** transmitting the ACK back to the originating pump. | Fault-injection: kill the writer process between fsync-call and ACK-send; verify no event is ACK'd that is not on disk. | DI-002 | Fault-injection test (VER-CA-FI-001) |
| A1 | SW-003 | FUNC | **CTF** | The replay engine shall hold queued events for downstream consumers up to 24 hours of consumer outage, replay them in original chronological order on consumer-availability restoration, with zero duplicates emitted. | Soak: disable EHR consumer for 24 h with active pump telemetry; restore; verify all events delivered in order; verify dedup. | DI-003 | Integration test (VER-CA-IT-002) |
| A1 | SW-004 | FUNC | **CTF** | The per-pump session state tracker shall maintain a live registry of connected pumps (serial, cert thumbprint, last heartbeat, firmware rev, library rev) updated within 1 s of each ingest event, queryable by the operator console and the alerting subsystem. | Bench: 500 simulated pumps; sample registry state; verify accuracy and update latency. | DI-001 | Software test |
| A1 | SW-023 | RELY | **CTF** | The pump-session keepalive watchdog shall detect pump-side disconnects within 15 s (3× the 5-s heartbeat window), update session state to `offline`, and emit a "pump went offline" event onto the internal bus. | Bench: drop 100 pump sessions at randomized intervals; measure detection latency; verify state transition. | DI-001 | Software test |
| A1 | SW-030 | FUNC | **CTF** | The event de-duplication index shall maintain pump-assigned event IDs for 72 hours and shall suppress any replay event whose ID is already in the index, preserving the original order. | Software test: replay a 10,000-event burst twice; verify only 10,000 unique events delivered downstream. | DI-003 | Software test |

### A2 — EHR / Pharmacy Bridge

| Group | SW ID | Category | Criticality | Requirement Statement | Acceptance Criteria | Traces to DI | Verification Method |
|---|---|---|---|---|---|---|---|
| A2 | SW-005 | INTE | **CTF** | The HL7 v2.5 message builder shall encode therapy administration events as ADT^A08 and RDE^O11 messages conformant to IHE Pharmacy profile transactions PHARM-1 and PHARM-2. | IHE Gazelle conformance test: PHARM-1 and PHARM-2 pass with 0 errors. | DI-004 | Conformance test (VER-CA-CT-001) |
| A2 | SW-006 | INTE | **CTF** | The FHIR R4 publisher shall emit MedicationAdministration resources to a configurable REST endpoint, validating against the US Core 6.0 MedicationAdministration profile. | fhir-validator pass against US Core 6.0; 0 errors on 100 sample resources. | DI-005 | Conformance test (VER-CA-CT-002) |
| A2 | SW-007 | FUNC | **CTC** | The endpoint configuration API shall accept add / modify / remove operations for HL7 and FHIR downstream endpoints (URL, TLS cert, field mappings) and shall apply changes without restarting the Adapter process or interrupting pump sessions. | Bench: add a new HL7 endpoint while 500 pumps stream; verify events flow to new endpoint within 30 s; verify zero session drops. | DI-006 | Integration test (VER-CA-IT-003) |

### A3 — Drug Library Distributor

| Group | SW ID | Category | Criticality | Requirement Statement | Acceptance Criteria | Traces to DI | Verification Method |
|---|---|---|---|---|---|---|---|
| A3 | SW-008 | SEC | **CTS** | The drug-library signature verifier shall validate every library payload (RSA-3072+, chain to the GlobalLogic signing root) before queuing it for pump distribution, refusing any payload that fails. | Negative test: present (a) valid, (b) corrupted-signature, (c) non-trust-anchor; verify only (a) is queued; refusals logged. | DI-007 | Security test (VER-CA-ST-001) |
| A3 | SW-009 | SAFE | **CTC** | The byte-fidelity store shall capture a SHA-256 hash of every library payload at ingress and at egress to each pump, and shall block egress and log a critical event if the hashes diverge. | Software test: 1000 library distributions; verify ingress/egress hashes match for all; inject corruption; verify block + log. | DI-008 | Software test (VER-CA-BT-001) |
| A3 | SW-010 | FUNC | **CTF** | The rollout scheduler shall accept a cohort spec (serial set / ward / all-fleet), schedule library distribution to the cohort's pumps, and expose per-pump status (queued / delivered / activated / failed) via API and operator console. | Bench: schedule rollout to a 20-pump cohort; verify status transitions reported in console + API. | DI-009 | Integration test (VER-CA-IT-004) |
| A3 | SW-024 | FUNC | **CTF** | The drug-library rollback handler shall, on operator command, restore the previous library version to a cohort of pumps and shall block any new rollout for that cohort while a rollback is in progress. | Software test: rollback a 20-pump cohort mid-rollout; verify per-pump previous-version active; verify new rollouts blocked. | DI-009 | Software test |

### A4 — Firmware Update Relay

| Group | SW ID | Category | Criticality | Requirement Statement | Acceptance Criteria | Traces to DI | Verification Method |
|---|---|---|---|---|---|---|---|
| A4 | SW-011 | SEC | **CTS** | The firmware signature verifier shall validate every firmware bundle before queuing it for pump distribution, refusing any unsigned or non-trust-anchor bundle and logging the rejection with operator identity. | Negative test: present valid / unsigned / non-trust-anchor bundles; verify only valid queues; refusals logged. | DI-010 | Security test (VER-CA-ST-002) |
| A4 | SW-012 | FUNC | **CTF** | The staged-rollout state machine shall support operator-controlled pause, resume, and abort across a configurable cohort, with per-pump status and a concurrency cap (default ≤5 concurrent pump upgrades). | Bench: schedule 20-pump rollout; pause at 5; resume; abort at 12; verify state transitions and no pump exceeds concurrency. | DI-011 | Integration test (VER-CA-IT-005) |
| A4 | SW-025 | FUNC | **CTF** | The firmware rollback handler shall revert pumps in a cohort to their pre-rollout firmware revision on operator command, suspending the in-flight rollout and emitting a rollback-complete event per pump. | Software test: rollback a 20-pump cohort mid-rollout; verify each pump back at pre-rollout rev; verify event emission. | DI-011 | Software test |

### A5 — Operator Console

| Group | SW ID | Category | Criticality | Requirement Statement | Acceptance Criteria | Traces to DI | Verification Method |
|---|---|---|---|---|---|---|---|
| A5 | SW-013 | FUNC | **CTF** | The fleet-health view-model shall aggregate pump session state (connected, last heartbeat, firmware rev, library rev, certificate expiry) into a UI feed refreshed end-to-end ≤30 s under 500-pump load. | Bench: 500 simulated pumps on 5-s intervals; measure UI refresh latency; p95 ≤30 s. | DI-012 | System test (VER-CA-SY-001) |
| A5 | SW-014 | FUNC | **CTC** | The audit-log search service shall support filtering by pump serial, user identity, ISO-8601 timestamp range, and event class, returning paginated results in p95 ≤5 s for queries spanning ≤30 days against a 1M-event log. | Bench: seed 1M-event audit log; run representative queries; measure response time. | DI-013 | Performance test (VER-CA-PT-001) |
| A5 | SW-015 | INTE | **S** | The "Needs Attention" landing-page composer shall aggregate offline pumps (>24 h), certs expiring within 30 days, and failed rollouts within the past 7 days, refreshed at least every 5 minutes. | Usability prototype validation: ≥4/5 biomed participants complete the "needs attention today" task in ≤60 s. | DI-014 | Usability test (VER-CA-UT-001) |
| A5 | SW-026 | SEC | **CTF** | The console RBAC enforcement layer shall scope every console operation (view fleet, edit endpoint, run rollback, export audit log) to the operator's IdP-asserted role, with no operation reachable by an unauthenticated session. | Code review + penetration test: enumerate console operations; verify each has RBAC enforcement; attempt bypass; verify rejection. | DI-013, DI-015 | Security test |

### A6 — Cybersecurity & Identity

| Group | SW ID | Category | Criticality | Requirement Statement | Acceptance Criteria | Traces to DI | Verification Method |
|---|---|---|---|---|---|---|---|
| A6 | SW-016 | SEC | **CTS** | The Adapter shall authenticate human users exclusively via SAML 2.0 or OIDC against a hospital-configured IdP, with no local-account code path reachable in shipped builds. | Penetration test: attempt password / token-based local auth; verify rejection. Code review: verify no local-account paths reachable in release builds. | DI-015 | Security test (VER-CA-ST-003) |
| A6 | SW-017 | INTE | **CTC** | The CEF audit-log streamer shall emit every security audit event in Common Event Format to a configured syslog-TLS endpoint with end-to-end latency p95 ≤5 s and zero drops. | Bench: configure syslog-TLS; trigger 1000 events; verify CEF-conformant receipt within p95 ≤5 s; 0 drops. | DI-016 | Integration test (VER-CA-IT-006) |
| A6 | SW-018 | SEC | **CTS** | The pump↔Adapter ingest endpoint shall enforce mutual TLS 1.3 with X.509 client-cert validation, rejecting sessions with invalid / expired / untrusted client certificates at TLS handshake and logging the rejection. | Negative test: attempt connection with no cert, expired cert, self-signed cert; verify TLS handshake failure; verify audit-log entries. | DI-017 | Security test (VER-CA-ST-004) |
| A6 | SW-019 | FUNC | **CTC** | The release pipeline shall generate a CycloneDX 1.4 or SPDX 2.3 SBOM for each Adapter release, publish it via the operator console to authenticated hospital security users, and publish it via an unauthenticated download URL on the GlobalLogic public site for that version. | Inspect release artifacts: SBOM file present, valid schema, ≥1 runtime dependency listed; SBOM URL returns 200 from public site. | DI-018 | Document review (VER-CA-DR-001) |
| A6 | SW-029 | INTE | **CTF** | The certificate-expiry monitor shall scan pump client-cert and downstream-endpoint server-cert expirations daily, raise console alerts for any cert expiring within 30 days, and surface the affected pumps / endpoints on the "Needs Attention" page. | Bench: seed 5 certs with expiries at -7 / 0 / 7 / 30 / 60 days; verify daily scan flags appropriate certs; verify console + landing-page surfacing. | DI-017, DI-014 | Software test |

### A7 — Platform & Lifecycle

| Group | SW ID | Category | Criticality | Requirement Statement | Acceptance Criteria | Traces to DI | Verification Method |
|---|---|---|---|---|---|---|---|
| A7 | SW-020 | FUNC | **CTF** | The installer package shall install the Adapter on RHEL 9, Ubuntu 22.04 LTS, and Ubuntu 24.04 LTS from a single signed package, completing installation in ≤30 minutes on a baseline host (8 vCPU, 32 GiB, 500 GB SSD) with zero manual library / dependency steps. | Install rehearsal on each OS; measure end-to-end time; verify Adapter passes self-test post-install. | DI-019 | System test (VER-CA-SY-002) |
| A7 | SW-021 | PERF | **CTF** | The in-place upgrade orchestrator shall execute version N→N+1 upgrades with no pump↔Adapter session disconnect exceeding 60 s in p99 and zero loss of in-flight pump-originated events. | Soak: 500 active pumps; trigger upgrade; measure max disconnect; verify pre/post event counts match. | DI-020 | System test (VER-CA-SY-003) |
| A7 | SW-022 | INTE | **S** | The `/metrics` endpoint shall expose Prometheus-format metrics with at minimum: connected-pump count, ingest event rate, queue depth per downstream, audit-log emission rate, certificate-expiry countdown. | Bench: scrape `/metrics`; validate with promtool; verify required metrics present. | DI-021 | Integration test (VER-CA-IT-007) |
| A7 | SW-027 | FUNC | **CTF** | The configuration migration tool shall translate the operator's previous-version configuration (endpoints, RBAC, retention policies) into the new-version schema during in-place upgrade, with a manual review-and-approve step before activation. | Software test: 5 representative configs across upgrade paths N→N+1; verify migration output and review-gate enforcement. | DI-020 | Software test |
| A7 | SW-028 | RELY | **CTF** | The Adapter self-test routine shall, at every process start, validate disk-write permissions, certificate-trust-store readability, downstream-endpoint reachability, and IdP configuration, refusing to accept pump traffic on any failure with a structured-log error code. | Software test: inject each failure class; verify process refuses traffic and logs the correct error code. | DI-019 | Software test |

## Traceability Summary

### By Category and Criticality

| Category | CTS | CTF | CTC | S | Total |
|---|---|---|---|---|---|
| FUNC | 0 | 10 | 3 | 0 | 13 |
| PERF | 0 | 2 | 0 | 0 | 2 |
| SAFE | 1 | 0 | 1 | 0 | 2 |
| INTE | 0 | 3 | 1 | 2 | 6 |
| SEC | 4 | 1 | 0 | 0 | 5 |
| RELY | 0 | 2 | 0 | 0 | 2 |
| **Total** | **5** | **18** | **5** | **2** | **30** |

_USAB-class requirements are tracked at A5 via SW-015 (categorized INTE for parser uniformity)._

### By Functional Group

| Group | SWs | DI Coverage |
|---|---|---|
| A1 Device Ingest | 6 | DI-001, DI-002, DI-003 |
| A2 EHR / Pharmacy Bridge | 3 | DI-004, DI-005, DI-006 |
| A3 Drug Library Distributor | 4 | DI-007, DI-008, DI-009 |
| A4 Firmware Update Relay | 3 | DI-010, DI-011 |
| A5 Operator Console | 4 | DI-012, DI-013, DI-014, DI-015 |
| A6 Cybersecurity & Identity | 5 | DI-014, DI-015, DI-016, DI-017, DI-018 |
| A7 Platform & Lifecycle | 5 | DI-019, DI-020, DI-021 |
| **Total** | **30** |  |

All 21 CA-1000 DIs are covered by at least one SW row.

## Revision History

| Rev | Date | Author | Description |
|---|---|---|---|
| A | 2026-05-12 | Ben Xavier | Initial draft — Phase 2 of task 049. 30 SW rows across 7 module groups. Demo content; IEC 62304 Class B system-level classification; per-row safety class omitted per task decision. |
