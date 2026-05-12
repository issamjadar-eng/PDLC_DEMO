# Design Inputs — Cloud Suite (Platform)

> _Demo sample data — not for clinical use. Illustrative content for the PDLC_DEMO project._

| Field | Value |
|---|---|
| Document ID | DHF-CLOUD-DI-001 |
| Revision | A |
| Status | Draft |
| Owner | GlobalLogic Product Development |
| Component | Cloud Suite (Platform) |
| Component ID | DEV-CLOUD |
| Classification | Platform DHF — `mixed` regulatory posture |
| Filing Posture | TBD — platform has no own filing; child modules each roll up to their respective filings |
| Parent System | PainEase PCA portfolio + Connectivity Adapter (CA-1000) |
| Applicable Standards | ISO 13485, IEC 62304, IEC 81001-5-1, ISO 27001, HIPAA Security Rule, GDPR, HITRUST CSF |

## Scope of This Document

This document captures the **platform-level** design inputs (system requirements) for the Cloud Suite, derived from the validated user needs in `../user-needs/user-needs.md` (DHF-CLOUD-UN-001). These requirements are inherited by every child module under `../dhfs/<module>/`; module-specific requirements live in the corresponding child DHFs. Each requirement carries a category, criticality classification, acceptance criteria, upstream user-need traces, and a planned verification method.

---

## Classification

**Category** — what kind of requirement:

| Category | Description |
|---|---|
| **Functional (FUNC)** | What the platform does |
| **Performance (PERF)** | How well it does it — measurable |
| **Interface (INTE)** | External interfaces (IdP, Connectivity Adapter, SIEM, EHR) |
| **Security (SEC)** | Cybersecurity controls |
| **Privacy (PRIV)** | HIPAA / GDPR controls |
| **Reliability (RELY)** | Availability, durability, recovery |

**Criticality**:

| Class | Symbol | Definition |
|---|---|---|
| Critical to Safety | **CTS** | Failure can indirectly contribute to patient or operator harm (platform contributes to clinical workflow even though it does not make decisions) |
| Critical to Function | **CTF** | Failure prevents the platform from delivering the service modules rely on |
| Critical to Compliance | **CTC** | Driven by regulation, standard, or customer-contractual posture |
| Supporting | **S** | Enabling or non-critical |

## Functional Groups

| # | Group | Scope |
|---|---|---|
| P1 | Identity & Access | Customer + internal identity, RBAC, workload identity |
| P2 | Data Ingestion | Inbound from Connectivity Adapter, tenant routing, back-pressure |
| P3 | Storage & Tenancy | Isolation, encryption, residency, backup, restore |
| P4 | Observability & Audit | Telemetry, audit log, SIEM export |
| P5 | Reliability & Continuity | SLA, DR, chaos validation |
| P6 | Compliance & Lifecycle | Change control, SBOM, staged rollout |
| P7 | Privacy & Data-Subject Rights | GDPR fulfillment, retention, PHI minimization |

## Design Inputs by Functional Group

### P1 — Identity & Access

| Group | DI ID | Category | Criticality | Requirement Statement | Acceptance Criteria | Traces to UN | Verification Method |
|---|---|---|---|---|---|---|---|
| P1 | DI-001 | SEC | **CTS** | The platform shall authenticate hospital end users exclusively via federation to a hospital-configured IdP (SAML 2.0 or OIDC) and shall provision no platform-local interactive end-user accounts. | Code review: no local-account creation code path is reachable in shipped build. Penetration test: attempt to create or use a local interactive account; verify rejection. | UN-001 | Security test (VER-CLOUD-ST-001) |
| P1 | DI-002 | SEC | **CTS** | Every authenticated API call shall be authorized against a tenant claim asserted by the federated IdP, and shall be rejected unless the requested resource belongs to that tenant. Cross-tenant resource enumeration shall not be possible at any API. | Penetration test: with Hospital A credentials, attempt 100+ tenant-crossing operations against Hospital B resources (read, write, list); verify 0 succeed. | UN-002 | Security test (VER-CLOUD-ST-002) |
| P1 | DI-003 | FUNC | **CTC** | Hospital administrators shall be able to manage per-module role assignments through a self-service admin interface without GlobalLogic-side ticketing, with changes effective in ≤ 5 minutes. | Bench: as a hospital admin, assign / revoke a module role to a user; measure time to effect; verify audit log entry. | UN-003 | Integration test (VER-CLOUD-IT-001) |
| P1 | DI-004 | SEC | **CTS** | Every internal service-to-service call shall use a short-lived workload-identity credential (≤ 1 hour TTL) issued by the platform's workload-identity service; long-lived service-account secrets shall not exist in the platform deployment manifest or secret store. | Static scan: deployment manifests, secret-store inventory, and codebase grepped for long-lived credential patterns; verify 0 hits. | UN-004 | Security audit (VER-CLOUD-SA-001) |

### P2 — Data Ingestion

| Group | DI ID | Category | Criticality | Requirement Statement | Acceptance Criteria | Traces to UN | Verification Method |
|---|---|---|---|---|---|---|---|
| P2 | DI-005 | FUNC | **CTS** | Every ingested event from a hospital's Connectivity Adapter shall carry a hospital tenant identifier validated by mutual-TLS client-certificate identity; events with missing, malformed, or untrusted tenant claims shall be rejected and the rejection logged. | Negative test: submit events with (a) valid tenant cert, (b) revoked cert, (c) cert claiming a different tenant; verify only (a) succeeds; audit log entries for refusals. | UN-005 | Security test (VER-CLOUD-ST-003) |
| P2 | DI-006 | RELY | **CTS** | The platform shall accept buffered event submissions from the Connectivity Adapter spanning up to 4 hours of pump activity per hospital without rejection or loss, and shall deduplicate replayed events idempotently by their pump-assigned event ID. | Soak: Connectivity Adapter simulator buffers 4 h of telemetry for a 500-pump fleet then drains; verify zero unique events lost; verify zero duplicates persisted. | UN-006 | Integration test (VER-CLOUD-IT-002) |
| P2 | DI-007 | PERF | **CTF** | The ingestion path shall enforce per-tenant back-pressure such that no single hospital's event burst can cause cross-tenant ingestion p95 latency to exceed 1 second sustained. | Burst test: drive a single hospital to 10× steady-state rate; measure other-hospital p95 latency; verify ≤ 1 s sustained. | UN-007 | Performance test (VER-CLOUD-PT-001) |

### P3 — Storage & Tenancy

| Group | DI ID | Category | Criticality | Requirement Statement | Acceptance Criteria | Traces to UN | Verification Method |
|---|---|---|---|---|---|---|---|
| P3 | DI-008 | PRIV | **CTC** | For tenants designated as "EU residency", the platform shall store, process, back up, and replicate PHI exclusively within EU-based infrastructure regions (default eu-west-1); cross-region replication into non-EU regions shall be technically blocked, not just policy-controlled. | Infrastructure-as-code review: confirm replication topology for EU tenants does not include non-EU regions. Penetration test: attempt to read EU-tenant PHI from non-EU region buckets; verify access-denied at the storage layer. | UN-008 | Security audit (VER-CLOUD-SA-002) |
| P3 | DI-009 | SEC | **CTS** | All persistent storage of PHI and authentication artifacts shall be encrypted at rest using AES-256-GCM with hospital-rotatable keys (BYOK via KMS), with per-tenant key rotation completing in ≤ 24 h with no operational disruption. | Bench: trigger BYOK rotation on a test tenant; measure completion time; verify reads / writes continue uninterrupted. | UN-009 | Integration test (VER-CLOUD-IT-003) |
| P3 | DI-010 | RELY | **CTF** | The platform shall provide point-in-time restore of a single tenant's PHI dataset to any timestamp within the prior 35 days, completing the restore in ≤ 24 h with the restored data isolated from other tenants. | Disaster recovery rehearsal: perform a PITR for a synthetic tenant at a random T within the 35-day window; measure restore time; verify isolation. | UN-010 | DR test (VER-CLOUD-DR-001) |

### P4 — Observability & Audit

| Group | DI ID | Category | Criticality | Requirement Statement | Acceptance Criteria | Traces to UN | Verification Method |
|---|---|---|---|---|---|---|---|
| P4 | DI-011 | SEC | **CTC** | Every read, write, and administrative API action against a hospital's data shall produce a tamper-evident audit log entry (append-only with hash-chain integrity), retained for at least 7 years, and accessible to that hospital via a forensic-query API. | Generate 1M events; verify hash-chain integrity intact; attempt log mutation; verify detection. | UN-011 | Security test (VER-CLOUD-ST-004) |
| P4 | DI-012 | INTE | **CTC** | Hospitals shall be able to stream their tenant's audit log to a customer-configured destination (syslog-TLS, Kafka, S3 sink) with p95 emission latency ≤ 5 minutes from event occurrence to customer-side receipt. | Bench: configure each destination type; trigger representative events; measure customer-side receipt timestamp; verify p95 ≤ 5 min. | UN-012 | Integration test (VER-CLOUD-IT-004) |
| P4 | DI-013 | FUNC | **CTF** | Each module shall emit a standard telemetry envelope (request rate, error rate, p50/p95/p99 latency, business KPIs) to the shared observability stack; modules that do not emit conformant telemetry shall fail release-readiness gating. | Inspect each module's release pipeline: telemetry-schema conformance check is mandatory; verify a non-conformant build is blocked. | UN-013 | Process verification (VER-CLOUD-PV-001) |

### P5 — Reliability & Continuity

| Group | DI ID | Category | Criticality | Requirement Statement | Acceptance Criteria | Traces to UN | Verification Method |
|---|---|---|---|---|---|---|---|
| P5 | DI-014 | RELY | **CTS** | The platform shall achieve a measured monthly availability of ≥ 99.9% for clinical-workflow read APIs and ≥ 99.5% for write APIs, computed by external blackbox probes. | Quarterly SLA report: aggregate measured availability per API class; verify thresholds met. | UN-014 | Operational measurement (VER-CLOUD-OM-001) |
| P5 | DI-015 | RELY | **CTF** | The platform shall sustain a complete loss of any single cloud region with RPO ≤ 15 min and RTO ≤ 8 h for the failed region's tenants, demonstrated via a documented regional-failover runbook. | DR exercise: simulate primary-region loss; measure RPO (data delta) and RTO (time to customer-visible restoration); verify within targets. | UN-015 | DR test (VER-CLOUD-DR-002) |
| P5 | DI-016 | RELY | **S** | The platform shall execute a chaos exercise covering at least one failure class (region loss, dependency outage, certificate expiry, identity provider outage) on at least a quarterly cadence, with documented outcomes and follow-up actions. | Chaos exercise log: ≥ 4 exercises per calendar year; each with documented hypothesis, outcome, and CAPA where applicable. | UN-016 | Process verification (VER-CLOUD-PV-002) |

### P6 — Compliance & Lifecycle

| Group | DI ID | Category | Criticality | Requirement Statement | Acceptance Criteria | Traces to UN | Verification Method |
|---|---|---|---|---|---|---|---|
| P6 | DI-017 | FUNC | **CTC** | Every change to any module's production deployment shall pass through a shared change-control workflow that records design change, risk-assessment delta, V&V trace, and release approval, retrievable per release. | Process audit: sample 30 releases across modules; verify each has the four required artifacts attached. | UN-017 | Process audit (VER-CLOUD-PA-001) |
| P6 | DI-018 | FUNC | **CTC** | Every released module version shall publish a versioned SBOM (CycloneDX 1.4 or SPDX 2.3) accessible without per-customer NDA from a documented GlobalLogic public URL pattern. | Release artifact review: pick latest 10 module releases; verify SBOM file present, valid schema, fetchable from public URL. | UN-018 | Document review (VER-CLOUD-DR-001) |
| P6 | DI-019 | FUNC | **CTS** | Module releases shall use a staged rollout pipeline (canary cohort ≤ 5% → small cohort ≤ 25% → broad) with operator-controlled pause and rollback at each stage, and with health gates that auto-pause on anomaly detection. | Release rehearsal: trigger a rollout with deliberately injected anomaly; verify auto-pause; verify operator-initiated rollback. | UN-019 | Integration test (VER-CLOUD-IT-005) |

### P7 — Privacy & Data-Subject Rights

| Group | DI ID | Category | Criticality | Requirement Statement | Acceptance Criteria | Traces to UN | Verification Method |
|---|---|---|---|---|---|---|---|
| P7 | DI-020 | PRIV | **CTC** | The platform shall expose a data-subject-rights API supporting GDPR Art. 15 (access), Art. 16 (rectification), and Art. 17 (erasure) operations on a per-data-subject basis, executable by a hospital DPO under their tenant scope, with statutory-timeline tracking and audit trail. | Bench: against a test tenant, execute access, rectification, and erasure for a synthetic data subject; measure end-to-end time; verify audit-trail entries. | UN-020 | Integration test (VER-CLOUD-IT-006) |
| P7 | DI-021 | PRIV | **CTC** | The platform shall enforce per-tenant retention policies for PHI and audit logs (default 7 years; customer-extendable; minimum 6 years for HIPAA-covered records), and shall purge end-of-retention data deterministically with cryptographic evidence of purge. | Synthetic record at past EOL boundary: trigger purge; verify storage / index / backup all purged; verify cryptographic evidence record retained. | UN-021 | Integration test (VER-CLOUD-IT-007) |
| P7 | DI-022 | PRIV | **CTC** | Non-production environments (development, staging, analytic sandbox) shall not contain production PHI; any test data derived from production shall be cryptographically de-identified prior to environment crossover, and the de-identification gate shall be enforced at the data-pipeline layer. | Data-pipeline audit: verify de-identification gate active; sample non-production datasets; scan for direct PHI identifiers; verify 0 hits. | UN-022 | Security audit (VER-CLOUD-SA-003) |
