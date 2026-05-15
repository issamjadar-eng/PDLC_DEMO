# Software Requirements — Cloud Suite (Platform)

> _Demo sample data — not for clinical use. Illustrative content for the PDLC_DEMO project._

| Field | Value |
|---|---|
| Document ID | DHF-CLOUD-SRS-001 |
| Revision | A |
| Status | Draft |
| Owner | GlobalLogic Product Development |
| Component | Cloud Suite (Platform) |
| Component ID | DEV-CLOUD |
| Software Safety Class | B (per IEC 62304 §4.3) — platform-level classification; child modules may classify higher |
| Applicable Standards | ISO 13485, IEC 62304, IEC 81001-5-1, ISO 27001, HIPAA Security Rule, GDPR, HITRUST CSF |

## Scope of This Document

This document captures the **platform-level** software requirements (SRS) for the Cloud Suite, derived from the platform-level design inputs in `./design-inputs.md` (DHF-CLOUD-DI-001). These SRS rows describe the shared services every child module inherits (identity, ingestion, storage, observability, reliability, compliance, privacy). Module-specific SRS lives in the corresponding child DHFs under `../dhfs/<module>/` and is out of scope for this document.

The platform is classified IEC 62304 Software Safety Class B at the platform level; child modules may classify higher (Class C) when they participate directly in clinical decision-support paths. Per-row safety classification is omitted in this demo. Revision A is the baseline supporting platform software verification planning and the trace-matrix DI→SW→V&V chain.

---

## Classification

**Category** — what kind of requirement:

| Category | Description |
|---|---|
| **Functional (FUNC)** | What the platform software does |
| **Performance (PERF)** | How well it does it — measurable |
| **Interface (INTE)** | External interfaces (IdP, Connectivity Adapter, SIEM, EHR) |
| **Security (SEC)** | Cybersecurity controls |
| **Privacy (PRIV)** | HIPAA / GDPR controls |
| **Reliability (RELY)** | Availability, durability, recovery |

**Criticality** — same scheme as DI (CTS / CTF / CTC / S).

## Functional Groups

The SW requirements follow the same 7 platform groups as the DI doc.

| # | Group | Scope |
|---|---|---|
| P1 | Identity & Access | Federated IdP, tenant-claim authorization, RBAC, workload identity |
| P2 | Data Ingestion | mTLS ingest, idempotent event store, per-tenant back-pressure |
| P3 | Storage & Tenancy | Residency, BYOK encryption, PITR |
| P4 | Observability & Audit | Hash-chained audit log, customer streaming sinks, telemetry envelope |
| P5 | Reliability & Continuity | SLA collector, failover automation, chaos harness |
| P6 | Compliance & Lifecycle | Change-control integration, SBOM publisher, staged rollout |
| P7 | Privacy & Data-Subject Rights | GDPR DSR API, retention manager, non-prod de-identification gate |

## Software Requirements by Functional Group

### P1 — Identity & Access

| Group | SW ID | Category | Criticality | Requirement Statement | Acceptance Criteria | Traces to DI | Verification Method |
|---|---|---|---|---|---|---|---|
| P1 | SW-001 | SEC | **CTS** | The federated authentication module shall authenticate hospital end users exclusively via SAML 2.0 or OIDC against a hospital-configured IdP and shall provision no platform-local interactive end-user accounts. | Code review: no local-account creation code path reachable in shipped build. Penetration test: attempt local-account use; verify rejection. | DI-001 | Security test (VER-CLOUD-ST-001) |
| P1 | SW-002 | SEC | **CTS** | The tenant-claim authorization middleware shall validate the tenant claim on every authenticated API call against the requested resource's tenant ownership, rejecting any cross-tenant access regardless of role. | Penetration test: with Hospital A credentials, attempt 100+ cross-tenant operations against Hospital B; verify 0 succeed. | DI-002 | Security test (VER-CLOUD-ST-002) |
| P1 | SW-003 | FUNC | **CTC** | The self-service role-management UI + API shall allow hospital admins to assign / revoke per-module roles for users in their tenant, with changes effective in ≤5 minutes and recorded in the audit log. | Bench: as a hospital admin, assign / revoke a module role; measure time to effect; verify audit entries. | DI-003 | Integration test (VER-CLOUD-IT-001) |
| P1 | SW-004 | SEC | **CTS** | The workload-identity issuer shall mint short-lived (≤1 hour TTL) credentials for every internal service-to-service call, with no long-lived service-account secrets present in deployment manifests or secret stores. | Static scan: grep manifests, secret-store inventory, codebase for long-lived credential patterns; verify 0 hits. | DI-004 | Security audit (VER-CLOUD-SA-001) |
| P1 | SW-024 | SEC | **CTF** | The cross-tenant probe harness shall run a continuous-integration security test that attempts 100+ cross-tenant enumeration operations against a synthetic two-tenant environment, failing the build on any successful crossover. | CI run on every commit; verify probe executes and that injected vulnerabilities fail the build. | DI-002 | Security test |
| P1 | SW-025 | SEC | **CTF** | The workload-credential rotation watcher shall scan active workload credentials, alert on any credential within 5 minutes of expiry that has not been rotated, and surface stale credentials on the operations dashboard. | Bench: seed credentials at -1 / 0 / 5 / 60 min expiry; verify alerting behavior. | DI-004 | Software test |

### P2 — Data Ingestion

| Group | SW ID | Category | Criticality | Requirement Statement | Acceptance Criteria | Traces to DI | Verification Method |
|---|---|---|---|---|---|---|---|
| P2 | SW-005 | SEC | **CTS** | The ingestion mTLS endpoint shall validate the Connectivity Adapter's tenant identity via X.509 client-certificate, rejecting events with missing / malformed / untrusted tenant claims and logging the rejection. | Negative test: events with (a) valid cert, (b) revoked cert, (c) cert claiming wrong tenant; verify only (a) succeeds; rejections logged. | DI-005 | Security test (VER-CLOUD-ST-003) |
| P2 | SW-006 | RELY | **CTS** | The idempotent event-store shall accept buffered submissions spanning up to 4 hours of pump activity per hospital, deduplicating by pump-assigned event ID with no unique-event loss and no duplicates persisted. | Soak: simulator buffers 4 h of telemetry for a 500-pump fleet then drains; verify 0 loss + 0 duplicates. | DI-006 | Integration test (VER-CLOUD-IT-002) |
| P2 | SW-007 | PERF | **CTF** | The per-tenant token-bucket back-pressure controller shall isolate ingestion rate per tenant such that a single hospital's 10× burst does not push cross-tenant ingest p95 latency above 1 s sustained. | Burst test: drive one hospital to 10× steady-state; measure other-hospital p95 latency. | DI-007 | Performance test (VER-CLOUD-PT-001) |

### P3 — Storage & Tenancy

| Group | SW ID | Category | Criticality | Requirement Statement | Acceptance Criteria | Traces to DI | Verification Method |
|---|---|---|---|---|---|---|---|
| P3 | SW-008 | PRIV | **CTC** | The EU-residency replication enforcer shall confine storage, processing, backup, and replication of EU-tenant PHI to EU-based infrastructure regions, with cross-region replication into non-EU regions blocked at the storage-layer policy (not just IaC review). | IaC review + penetration test: attempt reading EU-tenant PHI from non-EU regions; verify access-denied at the storage layer. | DI-008 | Security audit (VER-CLOUD-SA-002) |
| P3 | SW-009 | SEC | **CTS** | The encryption layer shall encrypt all persistent PHI and authentication artifacts with AES-256-GCM under hospital-rotatable (BYOK) keys, with per-tenant key rotation completing in ≤24 h and zero operational disruption. | Bench: trigger BYOK rotation on a test tenant; measure completion; verify reads / writes uninterrupted. | DI-009 | Integration test (VER-CLOUD-IT-003) |
| P3 | SW-010 | RELY | **CTF** | The point-in-time restore service shall restore a single tenant's PHI dataset to any timestamp within the prior 35 days in ≤24 h, with restored data isolated from other tenants. | DR rehearsal: PITR for a synthetic tenant at random T within the 35-day window; verify time + isolation. | DI-010 | DR test (VER-CLOUD-DR-001) |
| P3 | SW-026 | FUNC | **CTF** | The tenant-scoped backup/restore CLI + admin UI shall expose backup-status, list available restore points, initiate restore, and report progress, with all actions gated by tenant-scoped RBAC and audit-logged. | Bench: drive every CLI + UI operation as a tenant admin; verify access control + audit entries. | DI-010 | Software test |
| P3 | SW-029 | INTE | **S** | The key-rotation operator dashboard shall surface per-tenant BYOK rotation state (last rotation, next scheduled, key version, KMS region) and expose a per-tenant rotation status API for the customer's own dashboards. | Bench: run 5 rotations across 3 tenants; verify dashboard + API reflect state. | DI-009 | Software test |

### P4 — Observability & Audit

| Group | SW ID | Category | Criticality | Requirement Statement | Acceptance Criteria | Traces to DI | Verification Method |
|---|---|---|---|---|---|---|---|
| P4 | SW-011 | SEC | **CTC** | The audit-log writer shall append every read, write, and admin API action to a tamper-evident hash-chained log retained for ≥7 years, with attempted mutation detected on the next-entry append. | Generate 1M events; verify hash-chain intact; attempt mutation; verify detection. | DI-011 | Security test (VER-CLOUD-ST-004) |
| P4 | SW-012 | INTE | **CTC** | The customer audit-log streaming sink layer shall deliver each tenant's audit log to a customer-configured destination (syslog-TLS, Kafka, S3) with p95 emission latency ≤5 minutes. | Bench: each destination type; trigger 10,000 events; measure customer-side receipt; verify p95 ≤5 min. | DI-012 | Integration test (VER-CLOUD-IT-004) |
| P4 | SW-013 | FUNC | **CTF** | The telemetry envelope schema + release-gate validator shall require every module's release pipeline to emit conformant request-rate, error-rate, p50/p95/p99 latency, and KPI metrics, with non-conformant builds blocked from release. | Inspect each module's pipeline: schema validator present; force a non-conformant build; verify gate blocks release. | DI-013 | Process verification (VER-CLOUD-PV-001) |
| P4 | SW-023 | FUNC | **CTC** | The forensic audit-query API shall allow hospital DPOs to query their tenant's audit log by user identity, ISO-8601 timestamp range, and event class, returning structured results with cryptographic integrity proof. | Bench: query the audit log of a synthetic tenant; verify result correctness and integrity proof. | DI-011, DI-020 | Software test |
| P4 | SW-027 | INTE | **S** | The SIEM integration manager shall expose a per-tenant configuration interface for streaming destinations (sink type, endpoint, credentials, retention) and shall surface delivery-health (success rate, lag, last error) on the operator console. | Bench: configure 3 destinations per tenant; verify config persistence; inject failures; verify health UI reflects. | DI-012 | Software test |
| P4 | SW-028 | FUNC | **CTC** | The telemetry-conformance linter shall run at CI time against each module's instrumentation, failing the build if the module emits a metric that diverges from the envelope schema. | CI run on each module; deliberately diverge instrumentation; verify build failure. | DI-013 | Process verification |

### P5 — Reliability & Continuity

| Group | SW ID | Category | Criticality | Requirement Statement | Acceptance Criteria | Traces to DI | Verification Method |
|---|---|---|---|---|---|---|---|
| P5 | SW-014 | RELY | **CTS** | The blackbox SLA-probe collector shall measure external availability of clinical-workflow read APIs (target ≥99.9%) and write APIs (target ≥99.5%) and publish a monthly SLA report aggregating per-API-class availability. | Operate the collector for 90 days; aggregate the report; verify thresholds met. | DI-014 | Operational measurement (VER-CLOUD-OM-001) |
| P5 | SW-015 | RELY | **CTF** | The regional-failover automation shall execute a documented runbook on primary-region loss, achieving RPO ≤15 min and RTO ≤8 h for the failed region's tenants, with progress visible on an operator dashboard. | DR exercise: simulate primary-region loss; measure RPO (data delta) + RTO (time to customer-visible restoration). | DI-015 | DR test (VER-CLOUD-DR-002) |
| P5 | SW-016 | RELY | **S** | The chaos exercise harness shall execute one chaos exercise per quarter across at least one failure class (region loss, dependency outage, certificate expiry, IdP outage), with hypothesis, outcome, and CAPA recorded. | Chaos exercise log: ≥4 exercises per calendar year; each with hypothesis / outcome / CAPA where applicable. | DI-016 | Process verification (VER-CLOUD-PV-002) |

### P6 — Compliance & Lifecycle

| Group | SW ID | Category | Criticality | Requirement Statement | Acceptance Criteria | Traces to DI | Verification Method |
|---|---|---|---|---|---|---|---|
| P6 | SW-017 | FUNC | **CTC** | The change-control workflow integration shall require every production module release to bundle four artifacts (design change, risk-assessment delta, V&V trace, release approval) and shall record the bundle retrievably per release. | Process audit: sample 30 releases; verify each has all four artifacts attached. | DI-017 | Process audit (VER-CLOUD-PA-001) |
| P6 | SW-018 | FUNC | **CTC** | The SBOM release publisher shall generate a CycloneDX 1.4 or SPDX 2.3 SBOM for every released module version and shall publish it via a documented GlobalLogic public URL pattern without per-customer NDA. | Release artifact review: pick 10 module releases; verify SBOM file, schema validity, fetchable via public URL. | DI-018 | Document review (VER-CLOUD-DR-001) |
| P6 | SW-019 | FUNC | **CTS** | The staged-rollout pipeline shall execute canary (≤5%) → small (≤25%) → broad sequencing with operator pause / rollback at each stage and auto-pause health gates triggered by anomaly detection. | Release rehearsal: inject anomaly during rollout; verify auto-pause + operator-initiated rollback. | DI-019 | Integration test (VER-CLOUD-IT-005) |

### P7 — Privacy & Data-Subject Rights

| Group | SW ID | Category | Criticality | Requirement Statement | Acceptance Criteria | Traces to DI | Verification Method |
|---|---|---|---|---|---|---|---|
| P7 | SW-020 | PRIV | **CTC** | The data-subject-rights (DSR) API shall support GDPR Art. 15 (access), Art. 16 (rectification), and Art. 17 (erasure) operations on a per-data-subject basis, executable by a tenant DPO, with statutory-timeline tracking and audit trail. | Bench: execute access, rectification, erasure for a synthetic data subject in a test tenant; measure end-to-end time; verify audit-trail entries. | DI-020 | Integration test (VER-CLOUD-IT-006) |
| P7 | SW-021 | PRIV | **CTC** | The per-tenant retention manager shall enforce retention policies (default 7 years; customer-extendable; minimum 6 years for HIPAA-covered records), purging end-of-retention data deterministically with cryptographic evidence of purge retained. | Synthetic record at past EOL boundary: trigger purge; verify storage / index / backup all purged; cryptographic evidence retained. | DI-021 | Integration test (VER-CLOUD-IT-007) |
| P7 | SW-022 | PRIV | **CTC** | The non-production de-identification gate shall block any production-derived dataset from crossing into development, staging, or analytic-sandbox environments unless it has been cryptographically de-identified, with the gate enforced at the data-pipeline layer (not policy alone). | Data-pipeline audit: verify gate active; sample non-prod datasets; scan for direct PHI identifiers; verify 0 hits. | DI-022 | Security audit (VER-CLOUD-SA-003) |
| P7 | SW-030 | PRIV | **S** | The retention-policy editor UI shall allow tenant DPOs to set per-record-class retention (within statutory minimums), with all changes audit-logged and effective at the next scheduled retention sweep. | Bench: set / modify retention policies as a DPO; verify audit entries; verify next-sweep behavior. | DI-021 | Software test |

## Traceability Summary

### By Category and Criticality

| Category | CTS | CTF | CTC | S | Total |
|---|---|---|---|---|---|
| FUNC | 1 | 2 | 5 | 0 | 8 |
| PERF | 0 | 1 | 0 | 0 | 1 |
| INTE | 0 | 0 | 1 | 2 | 3 |
| SEC | 5 | 2 | 1 | 0 | 8 |
| PRIV | 0 | 0 | 4 | 1 | 5 |
| RELY | 2 | 2 | 0 | 1 | 5 |
| **Total** | **8** | **7** | **11** | **4** | **30** |

### By Functional Group

| Group | SWs | DI Coverage |
|---|---|---|
| P1 Identity & Access | 6 | DI-001, DI-002, DI-003, DI-004 |
| P2 Data Ingestion | 3 | DI-005, DI-006, DI-007 |
| P3 Storage & Tenancy | 5 | DI-008, DI-009, DI-010 |
| P4 Observability & Audit | 6 | DI-011, DI-012, DI-013, DI-020 |
| P5 Reliability & Continuity | 3 | DI-014, DI-015, DI-016 |
| P6 Compliance & Lifecycle | 3 | DI-017, DI-018, DI-019 |
| P7 Privacy & Data-Subject Rights | 4 | DI-020, DI-021, DI-022 |
| **Total** | **30** |  |

All 22 platform DIs are covered by at least one SW row.

## Revision History

| Rev | Date | Author | Description |
|---|---|---|---|
| A | 2026-05-12 | Ben Xavier | Initial draft — Phase 2 of task 049. 30 platform-level SW rows across 7 platform groups. Demo content; IEC 62304 Class B platform-level classification; per-row safety class omitted; module-specific SRS lives in child DHFs. |
