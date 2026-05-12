# User Needs — Cloud Suite (Platform)

> _Demo sample data — not for clinical use. Illustrative content for the PDLC_DEMO project._

| Field | Value |
|---|---|
| Document ID | DHF-CLOUD-UN-001 |
| Revision | A |
| Status | Draft |
| Owner | GlobalLogic Product Development |
| Component | Cloud Suite (Platform) |
| Component ID | DEV-CLOUD |
| Classification | Platform DHF — `mixed` regulatory posture; per-module child DHFs carry filing weight |
| Filing Posture | TBD — platform has no own filing; child modules each roll up to their respective filings (or stay non-device) |
| Parent System | PainEase PCA portfolio + Connectivity Adapter (CA-1000) |
| Hosting | GlobalLogic-managed multi-tenant cloud (us-east-1, us-west-2 primary regions; eu-west-1 for EU customers) |
| Applicable Standards | ISO 13485 (QMS), IEC 62304 (lifecycle — varies by module: Class A / B), IEC 81001-5-1 (cybersecurity), ISO 27001 (ISMS), HIPAA Security Rule, GDPR Art. 25/32, HITRUST CSF, FDA AI/ML PCCP (where applicable) |
| Child DHFs | drug-library-manager, fleet-management, alerts-engine, analytics-dashboard, inventory-tracker, clinical-interface, compliance-reports |

## Intended Use

The Cloud Suite is GlobalLogic's multi-tenant cloud platform that hosts a portfolio of customer-facing modules supporting hospital pharmacy, biomed, clinical, and compliance workflows around the PainEase PCA Advanced (PP-3500) device family. The platform itself performs no clinical decision making; clinical functionality lives in the individual child-module DHFs. The platform provides shared cross-cutting services (multi-tenant identity, data ingestion from the on-prem Connectivity Adapter, durable storage with hospital-tenant isolation, encryption, audit logging, observability, regional residency, and lifecycle / change-control infrastructure) on which each child module is built.

## Scope of This Document

This document captures the **platform-level** user needs of the Cloud Suite — the cross-cutting needs that every child module relies on. It is the upstream input to the platform Design Inputs document (`../requirements/design-inputs.md`, DHF-CLOUD-DI-001) and to the platform User Needs ↔ Design Inputs trace matrix. Module-specific user needs (e.g., the predictive-alarm specifics of the Alerts Engine, the drug-library authoring specifics of the Drug Library Manager) live in the corresponding child DHFs under `../dhfs/<module>/design-controls/user-needs/`.

Revision A reflects the initial baseline derived from hospital CISO interviews, customer onboarding retrospectives, ISO 27001 controls mapping, and the cross-module regulatory and cybersecurity strategy briefs.

---

## User Needs Categories

| Category | Description |
|---|---|
| **Multi-Tenancy (TENT)** | Hospital-tenant isolation, data residency, per-tenant configuration |
| **Operations (OPS)** | Needs of hospital admins, GlobalLogic operations, and module owners running on the platform |
| **Cybersecurity (CYBR)** | Platform security posture: identity, encryption, audit, vulnerability management |
| **Regulatory (REGU)** | Platform-level standards conformance and QMS infrastructure |
| **Reliability (RELY)** | Availability, durability, disaster recovery |
| **Privacy (PRIV)** | HIPAA / GDPR posture, PHI handling, data-subject rights, regional residency |

## Functional Groups

| # | Group | Scope |
|---|---|---|
| P1 | Identity & Access | Customer (hospital) and GlobalLogic-internal identity; SSO; RBAC; service-account hygiene |
| P2 | Data Ingestion | Inbound from Connectivity Adapter; per-tenant routing; back-pressure |
| P3 | Storage & Tenancy | Hospital-tenant isolation; encryption at rest; regional residency; backup; restore |
| P4 | Observability & Audit | Telemetry; audit log; SIEM export; per-tenant access logs |
| P5 | Reliability & Continuity | Availability SLA; disaster recovery; cross-region failover; chaos validation |
| P6 | Compliance & Lifecycle | QMS infrastructure shared across modules; change control; release management; SBOM publication |
| P7 | Privacy & Data-Subject Rights | HIPAA Right of Access; GDPR Art. 15–17; PHI minimization; retention policy |

## User Needs by Functional Group

### P1 — Identity & Access

| Group | UN ID | Category | Stakeholder | User Need | Source | Priority |
|---|---|---|---|---|---|---|
| P1 | UN-001 | CYBR | Hospital CISO | Hospital staff using any Cloud Suite module must authenticate exclusively via the hospital's enterprise IdP (SAML 2.0 or OIDC); the platform must not provision local hospital user accounts. | Hospital CISO interview KOL-0014; ISO 27001 Annex A.9.2 | High |
| P1 | UN-002 | TENT | Hospital Administrator | A user authorized in Hospital A must under no circumstance be able to read, modify, or even enumerate data belonging to Hospital B, even via direct API calls or token replay. | Onboarding retrospective; ISO 27001 Annex A.9.4; HIPAA §164.312(a) | High |
| P1 | UN-003 | OPS | Hospital Administrator | Hospital administrators must be able to define module-level role assignments (e.g., who can author drug libraries, who can view audit logs) without GlobalLogic involvement. | Customer success retrospective; admin workflow analysis | Medium |
| P1 | UN-004 | CYBR | GlobalLogic Security | Every GlobalLogic-internal service-to-service call must use short-lived (≤ 1 h) workload identity credentials; long-lived service-account secrets must not exist in the platform. | Internal security review; NIST SP 800-204 §4 | High |

### P2 — Data Ingestion

| Group | UN ID | Category | Stakeholder | User Need | Source | Priority |
|---|---|---|---|---|---|---|
| P2 | UN-005 | TENT | Hospital IT, Pharmacist | Therapy events forwarded from a hospital's Connectivity Adapter must arrive in the Cloud Suite labeled with the originating hospital tenant and must be routable only to that tenant's storage and modules. | Connectivity Adapter SAD §6; onboarding retrospective | High |
| P2 | UN-006 | RELY | Hospital IT | A Cloud Suite ingestion outage of up to 4 hours must not cause permanent loss of pump-originated events — events buffered at the Connectivity Adapter must be acceptable to the Cloud Suite upon recovery. | Operational SLA negotiation; CAPA-2023-001 evidentiary requirement | High |
| P2 | UN-007 | OPS | GlobalLogic Operations | The platform must provide per-tenant ingestion back-pressure so a single hospital generating an unexpected event burst cannot degrade ingestion latency for other hospitals. | Multi-tenant SaaS design retrospective; load-test learnings | Medium |

### P3 — Storage & Tenancy

| Group | UN ID | Category | Stakeholder | User Need | Source | Priority |
|---|---|---|---|---|---|---|
| P3 | UN-008 | PRIV | Hospital DPO, EU Customer | EU customers' PHI must remain in EU-based infrastructure (storage, compute, backup, log replicas) end-to-end; no cross-region replication into US regions for EU-tenant data. | GDPR Art. 44–49 (data transfer); EU customer procurement requirement | High |
| P3 | UN-009 | CYBR | Hospital CISO | All persistent storage of PHI and authentication artifacts must be encrypted at rest with hospital-rotatable keys (BYOK or HYOK), and the platform must support per-tenant key rotation without operational disruption. | Hospital CISO procurement requirement; NIST SP 800-57 | High |
| P3 | UN-010 | RELY | Hospital Administrator | A hospital must be able to request restoration of its own tenant data to a point-in-time within the past 35 days, and the platform must complete the restore in ≤ 24 hours. | Operational SLA negotiation; HIPAA contingency plan §164.308(a)(7) | Medium |

### P4 — Observability & Audit

| Group | UN ID | Category | Stakeholder | User Need | Source | Priority |
|---|---|---|---|---|---|---|
| P4 | UN-011 | CYBR | Hospital CISO | Every read, write, and administrative action against a hospital's data must produce a tamper-evident audit log entry retained for ≥ 7 years and accessible to the hospital for forensic review. | HIPAA §164.312(b); hospital CISO procurement requirement | High |
| P4 | UN-012 | CYBR | Hospital CISO | Hospitals must be able to stream their tenant's audit log to their own SIEM in near-real time (p95 latency ≤ 5 min) without GlobalLogic-side filtering or summarization. | Hospital CISO interview KOL-0014; SOC integration requirement | Medium |
| P4 | UN-013 | OPS | GlobalLogic Operations, Module Owner | Each module on the platform must emit structured telemetry (request rate, error rate, latency percentiles, business KPIs) to a shared observability stack so operations can detect and triage cross-module incidents. | Internal SRE practice; on-call retrospective | Medium |

### P5 — Reliability & Continuity

| Group | UN ID | Category | Stakeholder | User Need | Source | Priority |
|---|---|---|---|---|---|---|
| P5 | UN-014 | RELY | Hospital Administrator, Pharmacist | The Cloud Suite must achieve ≥ 99.9% monthly availability for read-paths used by clinical workflows (drug-library distribution, alarm review, dashboard read) and ≥ 99.5% for write-paths. | Operational SLA negotiation; commercial commitments | High |
| P5 | UN-015 | RELY | Hospital Administrator | A complete loss of the primary cloud region must not result in customer data loss beyond a 15-minute RPO and must be recoverable within an 8-hour RTO, with regional failover exercised on a documented cadence. | Operational continuity plan; HIPAA §164.308(a)(7); HITRUST CSF | High |
| P5 | UN-016 | RELY | GlobalLogic Operations | The platform must continuously validate its failover and recovery paths via scheduled chaos exercises (≥ quarterly) so disaster-recovery readiness does not silently regress between real incidents. | Internal SRE chaos engineering practice | Medium |

### P6 — Compliance & Lifecycle

| Group | UN ID | Category | Stakeholder | User Need | Source | Priority |
|---|---|---|---|---|---|---|
| P6 | UN-017 | REGU | Regulatory Affairs, QA | Every module on the platform must inherit a shared change-control workflow (design change, risk assessment, V&V trace, release approval) so design controls (21 CFR 820.30 / ISO 13485 §7.3) hold consistently across the portfolio. | QMS shared-strategy brief; ISO 13485 §7.3.9 | High |
| P6 | UN-018 | REGU | Hospital CISO, Regulatory Affairs | Every released module version must publish a versioned SBOM (CycloneDX or SPDX) accessible to hospital security teams and to FDA submissions without per-customer NDAs. | FDA cyber pre-market guidance §VIII; hospital procurement; cross-module strategy | High |
| P6 | UN-019 | OPS | GlobalLogic Operations | The platform must support staged, per-tenant rollout of module updates (canary → small cohort → broad) with operator-controlled pause / rollback, so a defective release cannot reach the full customer base before detection. | SRE rollout practice; CAPA-2024-007 lesson | High |

### P7 — Privacy & Data-Subject Rights

| Group | UN ID | Category | Stakeholder | User Need | Source | Priority |
|---|---|---|---|---|---|---|
| P7 | UN-020 | PRIV | Hospital DPO, EU Customer | The platform must support fulfillment of GDPR Art. 15 (right of access), Art. 16 (rectification), and Art. 17 (erasure) requests on a per-data-subject basis within statutory timelines (1 month default, extendable to 3). | GDPR Arts. 15–17; EU customer procurement requirement | High |
| P7 | UN-021 | PRIV | Hospital DPO | The platform must enforce per-tenant configurable retention policies for PHI and audit logs (default: 7 years per HIPAA, customer-extendable) and must purge data deterministically at end-of-retention with cryptographic evidence of purge. | HIPAA §164.530(j); GDPR Art. 5(1)(e); customer retention policy variability | Medium |
| P7 | UN-022 | PRIV | Hospital DPO, GlobalLogic Privacy | The platform must minimize PHI in non-production environments — production data must not appear in development, staging, or analytic sandbox environments without explicit data-subject-level controls. | GDPR Art. 25 (data minimization); internal privacy engineering policy | Medium |
