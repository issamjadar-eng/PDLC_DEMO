# Connectivity Adapter — System Software Architecture Description (SAD)

**DHF**: connectivity-adapter
**Classification**: MDDS (non-device per post-2015 FDA reclassification)
**Filing**: Not separately filed; referenced by PP3500 510(k) for cybersecurity posture only
**Status**: Draft — first-stab scaffold derived from architecture + regulatory strategy
**Source strategy**: `docs/project/strategies/architecture-strategy.md`, `docs/project/strategies/regulatory-strategy.md`

_Demo artifact — illustrative, not a real submission SAD._

## 1. Purpose & Scope

The Connectivity Adapter is GlobalLogic's on-premises server that aggregates a hospital's fleet of PCA devices and bridges them to hospital IT and (optionally) our Cloud Suite. This SAD covers the Adapter's software architecture only. It does not cover the PCA device or any Cloud Suite component; those are separate DHFs.

Per the regulatory strategy's **Component Classification & Filing Posture** decision, the Adapter is classified MDDS and is **not** separately filed. QMS and cybersecurity evidence still apply; the Adapter's cybersecurity assessment is pulled into the PP3500 510(k) via composition manifest because the PCA's cyber posture depends on everything that touches it.

## 2. System Context

```
 ┌──────────────┐    HL7v2.5    ┌──────────────────┐    TLS 1.3     ┌──────────────┐
 │ EHR /        │◀──────────────│ Connectivity     │────────────────▶│ PCA Devices  │
 │ Pharmacy /   │    FHIR R4    │ Adapter          │  mutual auth   │ (fleet)      │
 │ IdP          │──────────────▶│ (on-prem)        │◀───────────────│              │
 └──────────────┘               └────────┬─────────┘                └──────────────┘
                                         │ (optional, out of baseline)
                                         ▼
                                ┌──────────────────┐
                                │ Cloud Suite      │
                                │ (manufacturer)   │
                                └──────────────────┘
```

Deployment: single on-prem footprint (single component — not split into "local server" + "adapter"). Runs inside the hospital network boundary to keep PHI on-prem.

## 3. Composition

| Class | Realization | Regulatory weight |
|---|---|---|
| **MDDS software** | Device data transfer, storage, display — data in motion between PCA fleet and hospital IT | Non-device per FDA; QMS + cybersecurity apply |
| **Non-device software** | Admin / operator console, health dashboards, local audit log viewer | Non-device |

The Adapter contains **no SaMD, no SiMD, and no hardware** of its own (runs on customer-provided or GlobalLogic-supplied COTS server hardware).

## 4. Module Inventory

| # | Module | Classification | Summary |
|---|---|---|---|
| A1 | **Device Ingest** | MDDS | Receives telemetry, delivery logs, and alarms from PCA fleet over mutual-TLS; persists to local store |
| A2 | **EHR/Pharmacy Bridge** | MDDS | Translates between internal event model and HL7v2.5 / FHIR R4 outbound to hospital IT |
| A3 | **Drug Library Distributor** | MDDS (pass-through) | Receives signed drug-library payloads (from Cloud Drug Library Manager or local admin upload), hands them to A1 for device distribution. Does **not** author, edit, or re-sign libraries — pass-through only to preserve MDDS status |
| A4 | **Firmware Update Relay** | MDDS (pass-through) | Pass-through for signed firmware bundles targeting the PCA fleet |
| A5 | **Operator Console** | Non-device | Web UI for biomed / IT — fleet health, audit log search, cert management |
| A6 | **Cybersecurity & Identity** | (security) | TLS termination, certificate management, IdP integration (SAML/OIDC), audit log, SIEM export |
| A7 | **Platform** | (infra) | Storage, scheduler, backup, observability, packaging |

A3 and A4 are explicitly pass-through. The moment the Adapter would **author** or **transform** a drug library or firmware payload in a way that changes its clinical meaning, its classification flips from MDDS to accessory-of-device and the filing posture changes. The architecture enforces that line.

## 5. Trust & Data Boundaries

- **PHI scope**: therapy logs from the PCA fleet may contain patient identifiers if the EHR returns them. PHI lives on the Adapter's local store and flows out only via A2 to the hospital EHR (same trust zone) — not to Cloud Suite.
- **Inbound from PCA fleet**: mutual-TLS; device cert issued during provisioning (see Cybersecurity Plan).
- **Outbound to EHR**: HL7v2.5 (MLLP/TLS) or FHIR R4 (HTTPS) depending on hospital integration.
- **Outbound to Cloud Suite**: optional; de-identified fleet telemetry only. Disabled by default in the cleared baseline.
- **Admin plane**: A5 + A6 use hospital IdP; no direct internet exposure.

## 6. Standards & Guidance Mapping

| Standard / Guidance | Modules | Role |
|---|---|---|
| FDA MDDS guidance / 21 CFR 880.6310 | A1–A4 | MDDS classification rationale |
| FDA MFD guidance | A1–A4 | Medical device data system / medical function definitions |
| FDA Cybersecurity 2023 + Section 524B | A6 | Threat model, SBOM, update mechanism (feeds PP3500 510(k) via composition manifest) |
| AAMI TIR57 | A6 | Security risk management |
| IEC 81001-5-1 | A6, A7 | Secure product lifecycle |
| HIPAA Security Rule | A1, A6, A7 | PHI safeguards on-prem |

## 7. Relation to PP3500 Filing

The PP3500 510(k) composition manifest pulls the following Adapter artifacts:

- Cybersecurity Plan (A6)
- Threat model + SBOM (A6)
- Interoperability description (A2)
- Classification record (this SAD §3 + §4)

It does **not** pull Adapter functional design controls, risk files, or V&V — those are adjacent evidence, not part of the PP3500 device's design history.

## 8. Open Items

- Whether the Adapter → Cloud Suite link is enabled in the cleared baseline or gated behind a post-clearance switch (strategy doc question d/open).
- Whether A3 ever needs to enforce library-version policy locally (e.g., reject outdated libraries) — that would push it from pass-through MDDS toward accessory-of-device territory and requires classification re-review.

## 9. Changelog

| Date | Author | Summary |
|---|---|---|
| 2026-04-14 | AI assistant (first-stab) | Initial scaffold derived from architecture + regulatory strategy docs. Seven-module decomposition; MDDS + non-device classification. Task 013. |
