# User Needs — Connectivity Adapter (CA-1000)

> _Demo sample data — not for clinical use. Illustrative content for the PDLC_DEMO project._

| Field | Value |
|---|---|
| Document ID | DHF-CA1000-UN-001 |
| Revision | A |
| Status | Draft |
| Owner | GlobalLogic Product Development |
| Component | Connectivity Adapter |
| Model | CA-1000 |
| Component ID | DEV-CA1000 |
| Classification | MDDS (post-2015 FDA reclassification — non-device) |
| Filing Posture | Not separately filed; referenced by PP3500 510(k) (K210345) for cybersecurity posture and HFE composition |
| Parent System | PainEase PCA Advanced (PP-3500, K210345) |
| Applicable Standards | IEC 81001-5-1 (cybersecurity), ISO 13485 (QMS), IEC 62304 (software lifecycle — Class B), HL7 v2.5, HL7 FHIR R4, IEC 62443-4-1 (security dev), NIST SP 800-53 (security controls) |

## Intended Use

The Connectivity Adapter (CA-1000) is GlobalLogic's on-premises server software that aggregates a hospital's fleet of PainEase PCA Advanced pumps (PP-3500) and bridges them to hospital information systems and, optionally, to the GlobalLogic Cloud Suite. The Adapter terminates mutual-TLS sessions from the pump fleet, translates between the internal pump event model and HL7v2.5 / FHIR R4 outbound to the hospital EHR and pharmacy systems, and provides a biomed/IT operator console for fleet health, certificate management, and audit log search. The Adapter contains no clinical decision logic, performs no diagnostic interpretation, and runs entirely inside the hospital network boundary to keep PHI on-prem.

## Scope of This Document

This document is the controlled record of validated user needs for the Connectivity Adapter (CA-1000), captured at the platform design controls baseline. It is the upstream input to the Design Inputs document (`../requirements/design-inputs.md`, DHF-CA1000-DI-001) and to the User Needs ↔ Design Inputs trace matrix. Revision A reflects the initial baseline derived from biomed/IT KOL interviews, hospital infrastructure assessments, the PP3500 510(k) submission's cybersecurity composition manifest, and applicable interoperability standards.

---

## User Needs Categories

| Category | Description |
|---|---|
| **Interoperability (INTR)** | Needs arising from EHR / pharmacy / IdP integration and HL7/FHIR conformance |
| **Operations (OPS)** | Needs of biomed / IT staff operating the Adapter in their workflow |
| **Safety (SAFE)** | Needs that protect patient and operator safety even though the Adapter is MDDS-classified |
| **Cybersecurity (CYBR)** | Needs driven by IEC 81001-5-1, FDA cyber pre-market guidance, and hospital threat model |
| **Regulatory (REGU)** | Needs driven by MDDS classification boundary preservation and standards conformance |

## Functional Groups

The user needs in this document are organized into 7 functional groups aligned with the Adapter module inventory in the SAD (`../architecture/connectivity-adapter-system-sad.md`).

| # | Group | Scope |
|---|---|---|
| A1 | Device Ingest | Receives telemetry, delivery logs, and alarms from the PCA fleet over mutual-TLS |
| A2 | EHR / Pharmacy Bridge | Translates internal events to HL7v2.5 / FHIR R4 outbound to hospital IT |
| A3 | Drug Library Distributor | Pass-through distribution of signed drug-library payloads to the pump fleet |
| A4 | Firmware Update Relay | Pass-through distribution of signed firmware bundles to the pump fleet |
| A5 | Operator Console | Web UI for biomed / IT — fleet health, audit log, cert management |
| A6 | Cybersecurity & Identity | TLS termination, certificate management, IdP integration, audit log, SIEM export |
| A7 | Platform & Lifecycle | Storage, backup, observability, packaging, install, upgrade |

## User Needs by Functional Group

### A1 — Device Ingest

_Needs that govern how the Adapter receives data from the PCA fleet — connection security, persistence, and reliability under hospital network conditions._

| Group | UN ID | Category | Stakeholder | User Need | Source | Priority |
|---|---|---|---|---|---|---|
| A1 | UN-001 | INTR | Biomed Engineer, Pump Fleet Admin | The Adapter must accept incoming telemetry from every pump in a hospital's fleet of up to 500 PainEase PCA Advanced devices over a single mutual-TLS endpoint without imposing per-pump per-hospital configuration. | Biomed KOL interview (KOL-0011); PP3500 SAD §6 connectivity assumptions | High |
| A1 | UN-002 | SAFE | Patient (indirect), Anesthesiologist | The Adapter must not lose pump-originated alarm or therapy-event records during transient network outages between the pump and the Adapter, since these records are evidentiary for downstream PMS and CAPA. | ISO 14971 hazard analysis HZ-CA-002 (data loss); CAPA-2023-001 traceability requirement | High |
| A1 | UN-003 | OPS | Biomed Engineer | The Adapter must persist incoming pump events durably enough that a 24-hour Adapter outage produces no permanent loss of pump-originated records once the Adapter returns to service. | Biomed KOL interview (KOL-0011); hospital SLA expectations | High |

### A2 — EHR / Pharmacy Bridge

_Needs that govern outbound translation to hospital IT systems._

| Group | UN ID | Category | Stakeholder | User Need | Source | Priority |
|---|---|---|---|---|---|---|
| A2 | UN-004 | INTR | Hospital IT, Pharmacist | The Adapter must emit therapy-administration events to the hospital EHR via HL7v2.5 ADT/RDE messages conformant to the IHE Pharmacy profile so that PCA therapy is automatically recorded in the patient chart. | IHE Pharmacy profile §3.2; hospital integration KOL-0012 | High |
| A2 | UN-005 | INTR | Pharmacist | The Adapter must support a parallel FHIR R4 MedicationAdministration outbound channel for hospitals migrating off HL7 v2 so a single Adapter deployment serves both legacy and modern EHR estates. | FHIR R4 §MedicationAdministration; CIO advisory board feedback | Medium |
| A2 | UN-006 | OPS | Hospital IT | The Adapter must allow IT to configure outbound endpoints (host, port, certificates, OBR/OBX mapping) per upstream system without restarting the Adapter or interrupting inbound pump connections. | Hospital integration KOL-0012; deployment retrospective | Medium |

### A3 — Drug Library Distributor

_Needs that govern pass-through distribution of signed drug-library payloads, while preserving the MDDS boundary._

| Group | UN ID | Category | Stakeholder | User Need | Source | Priority |
|---|---|---|---|---|---|---|
| A3 | UN-007 | REGU | Regulatory Affairs, Pharmacy & Therapeutics | The Adapter must distribute drug-library payloads to the pump fleet without modifying, re-signing, or transforming their clinical content, so the Adapter remains classified MDDS rather than becoming an accessory-of-device. | Regulatory strategy §Component classification; FDA MDDS guidance 2017 | High |
| A3 | UN-008 | SAFE | Pharmacist, Anesthesiologist | The Adapter must refuse to distribute any drug-library payload whose digital signature does not verify against the GlobalLogic-managed signing trust anchor. | ISO 14971 hazard analysis HZ-CA-003 (wrong library); IEC 81001-5-1 §7.2 | High |
| A3 | UN-009 | OPS | Pharmacist | The Adapter must let a pharmacy administrator schedule a drug-library rollout to a defined cohort of pumps and observe per-pump rollout status (queued / delivered / activated / failed). | Pharmacy KOL-0013; predicate workflow gap | Medium |

### A4 — Firmware Update Relay

_Needs that govern pass-through firmware distribution._

| Group | UN ID | Category | Stakeholder | User Need | Source | Priority |
|---|---|---|---|---|---|---|
| A4 | UN-010 | SAFE | Patient (indirect), Biomed Engineer | The Adapter must refuse to relay any firmware bundle whose digital signature does not verify against the GlobalLogic-managed signing trust anchor, even if the bundle is locally uploaded by an administrator. | IEC 81001-5-1 §7.2; FDA cyber guidance §V signed-updates | High |
| A4 | UN-011 | OPS | Biomed Engineer | The Adapter must allow biomed to stage a firmware rollout to a defined cohort of pumps, with per-pump status visibility and the ability to pause / resume / abort the rollout. | Biomed KOL-0011; hospital change-control SOP | High |

### A5 — Operator Console

_Needs that govern the biomed / IT web UI._

| Group | UN ID | Category | Stakeholder | User Need | Source | Priority |
|---|---|---|---|---|---|---|
| A5 | UN-012 | OPS | Biomed Engineer | Biomed staff must be able to see real-time fleet health (pumps connected, last heartbeat, firmware revision, library revision, certificate expiry) from the Adapter's operator console without leaving the hospital network. | Biomed KOL-0011; post-market complaint trend review | High |
| A5 | UN-013 | OPS | Hospital IT | IT staff must be able to search the Adapter's audit log by pump serial, user identity, timestamp range, and event class, and export the resulting set as CSV for forensic review. | Hospital IT audit-log SOP; HIPAA audit requirements | Medium |
| A5 | UN-014 | OPS | Biomed Engineer | The operator console must surface a clear "needs attention" list (pumps offline > 24 h, certs expiring < 30 days, failed library rollouts, failed firmware rollouts) so biomed has one daily landing place. | Biomed KOL-0011; usability evaluation prototype feedback | Medium |

### A6 — Cybersecurity & Identity

_Needs that establish the security posture composed into the PP3500 510(k) cybersecurity submission._

| Group | UN ID | Category | Stakeholder | User Need | Source | Priority |
|---|---|---|---|---|---|---|
| A6 | UN-015 | CYBR | Hospital CISO | The Adapter must authenticate human users (biomed, pharmacy, IT) via the hospital's enterprise IdP (SAML 2.0 or OIDC), not via Adapter-local accounts, so credential lifecycle stays under hospital control. | Hospital CISO interview KOL-0014; NIST SP 800-63B | High |
| A6 | UN-016 | CYBR | Hospital CISO | The Adapter must export its security audit log in real time to the hospital SIEM via syslog over TLS, formatted to a recognized event schema (CEF or LEEF). | Hospital CISO interview KOL-0014; SOC operational requirement | High |
| A6 | UN-017 | CYBR | Hospital CISO, Patient (indirect) | The Adapter must enforce mutual-TLS authentication on every pump↔Adapter session so a rogue or impersonated pump cannot inject therapy events. | IEC 81001-5-1 §7.4; FDA cyber pre-market guidance §IV | High |
| A6 | UN-018 | CYBR | Hospital CISO | The Adapter must publish an SBOM (SPDX or CycloneDX) for each released version, accessible to the hospital security team without contacting GlobalLogic support. | FDA cyber pre-market guidance §VIII SBOM; hospital VPAT/SBOM procurement requirement | Medium |

### A7 — Platform & Lifecycle

_Needs that govern install, upgrade, observability, and packaging._

| Group | UN ID | Category | Stakeholder | User Need | Source | Priority |
|---|---|---|---|---|---|---|
| A7 | UN-019 | OPS | Hospital IT | The Adapter must be installable as a single signed package on customer-provided RHEL- or Ubuntu-LTS hardware without requiring a GlobalLogic engineer on-site. | Hospital IT KOL-0012; commercial deployment scaling target | High |
| A7 | UN-020 | OPS | Biomed Engineer, Hospital IT | The Adapter must support a non-disruptive upgrade path from version N to N+1 that does not interrupt active pump↔Adapter sessions for more than 60 seconds. | Hospital change-control SOP; SLA negotiation feedback | Medium |
| A7 | UN-021 | OPS | Hospital IT | The Adapter must produce machine-parsable health metrics (Prometheus exposition format) so hospital IT can integrate the Adapter into existing monitoring stacks. | Hospital IT KOL-0012; observability standardization across customers | Low |
