# Drug Library Manager — System Software Architecture Description (SAD)

**DHF**: cloud-suite/dhfs/drug-library-manager
**Classification**: Class II SaMD (accessory to PCA device; directly affects dose enforcement)
**Filing**: Own 510(k) OR bundled into PP3500 filing as accessory — TBD in submission planning
**Status**: Draft — first-stab scaffold derived from architecture + regulatory strategy
**Source strategy**: `docs/project/strategies/architecture-strategy.md`, `docs/project/strategies/regulatory-strategy.md`

_Demo artifact — illustrative, not a real submission SAD._

## 1. Purpose & Scope

The Drug Library Manager (DLM) is a cloud SaMD used by hospital pharmacists to author, review, approve, and publish the drug library that the PP3500 PCA device enforces at therapy start. Because DLM directly mutates the safety table the pump enforces, it is classified as a Class II SaMD — an accessory to the PCA device with its own design controls, risk file, and regulatory weight. Any other classification would be regulatory malpractice per the regulatory strategy.

This SAD covers DLM's software architecture only. It does not cover any other Cloud Suite component (Fleet Management, Telemetry, Analytics, Surveillance, Update Distribution, Reg Data Pipelines, Customer Portals — those are non-device software under separate DHFs).

## 2. System Context

```
 ┌────────────────┐     ┌──────────────────┐     sign + publish     ┌──────────────────┐
 │ Pharmacist     │────▶│ Drug Library     │───────────────────────▶│ Connectivity     │
 │ Reviewer       │◀───▶│ Manager (SaMD)   │   signed payload        │ Adapter          │
 │ Approver       │     │   (cloud)        │                         │ (on-prem)        │
 └────────────────┘     └────────┬─────────┘                         └────────┬─────────┘
                                 │                                            │ mutual TLS
                                 ▼                                            ▼
                         ┌──────────────┐                             ┌──────────────┐
                         │ Audit store  │                             │ PCA Device   │
                         │ (append-only)│                             │ (M3 cache)   │
                         └──────────────┘                             └──────────────┘
```

DLM is the **authoring origin** of the safety-critical drug library. The Adapter is a pass-through distribution path (MDDS). The PCA device's Drug Library Enforcement module (M3 in the pca-device SAD) is the terminal enforcer.

## 3. Composition

| Class | Realization | Regulatory weight |
|---|---|---|
| **SaMD** | Cloud-hosted web application with authoring workflow, review/approval, signing, and publication APIs | IEC 62304 Class B overall (some modules Class C) |
| **Non-device cloud infrastructure** | Storage, IAM, observability, CI/CD — shared with the broader Cloud Suite | Non-device |

No SiMD, no hardware.

## 4. Module Inventory

| # | Module | IEC 62304 Class | Criticality tags | Summary |
|---|---|---|---|---|
| D1 | **Library Authoring** | B | CtF | Pharmacist-facing editor — drug entries, concentration ranges, dose limits, hard/soft limits |
| D2 | **Review & Approval Workflow** | B | CtS, CtC | Multi-role workflow: author → reviewer → approver; electronic signature (21 CFR Part 11) |
| D3 | **Validation Engine** | C | CtS, CtF | Static checks against clinical rules, unit consistency, dose-limit sanity; blocks publication on failure |
| D4 | **Signing Service** | C | CtS, CtC | Builds canonical payload, signs with DLM signing key; key material in HSM-backed KMS |
| D5 | **Publication API** | B | CtF | Exposes signed payloads to the Connectivity Adapter's Drug Library Distributor (A3) |
| D6 | **Audit Log** | B | CtC | Append-only record of every edit, review, approval, and publication event (21 CFR Part 11) |
| D7 | **Cybersecurity & Identity** | B | CtC, CtS | IdP integration, RBAC (author/reviewer/approver/admin separation), SBOM, 524B surface |

## 5. Key Invariants

- No library payload is published without **two distinct humans** (author ≠ approver).
- No library payload is published if D3 validation fails.
- Every published payload is signed by D4 and the signature is verifiable by the PCA device (M3) independently of the Adapter.
- Audit log (D6) is append-only and cryptographically chained; tamper-evident.
- Role separation is enforced in D7 — no single user holds author + reviewer + approver + signing authority.

## 6. Data & Trust Boundaries

- **No PHI**: DLM operates on library definitions, not patient data. If PHI ever enters this system, classification and filing scope change.
- **Signing keys**: held in KMS/HSM; only D4 has sign authority; key rotation policy documented in Cybersecurity Plan.
- **Publish boundary**: D5 is the only egress to the Adapter. Everything else is inbound.

## 7. Standards & Guidance Mapping

| Standard / Guidance | Modules | Role |
|---|---|---|
| IEC 62304 | D1–D7 | Software lifecycle, safety classification |
| ISO 14971 | D3 | Risk management (clinical-rule failure modes) |
| IEC 62366-1 | D1, D2 | Usability — pharmacist workflow is the primary operating function |
| 21 CFR Part 11 | D2, D6 | Electronic signatures + audit trail |
| FDA Cybersecurity 2023 + Section 524B | D4, D7 | SBOM, threat model, key management |
| FDA sw-functions guidance | all | SaMD function identification and classification rationale |
| FDA 510(k) SE guidance | all | SE pathway (predicate TBD in submission planning) |

## 8. Relation to PP3500 Filing

Per the regulatory strategy's Component Classification decision, DLM may either:

1. **Be bundled into the PP3500 510(k)** as an accessory (drawing on the composition manifest), or
2. **Be filed as its own standalone 510(k)** — likely later, after PP3500 clears.

Either way, the PP3500 510(k) composition manifest at minimum pulls:

- DLM classification record + architecture summary (this SAD §3, §4)
- DLM cybersecurity plan + threat model
- The **signing trust chain** that the PCA device (M3) relies on

If bundled, the full design controls / V&V / risk file also enter the PP3500 composition.

## 9. Open Items

- Filing posture — bundle vs standalone — TBD in submission planning. Triggers a different composition manifest shape.
- Predicate selection for DLM (if standalone) — not yet analyzed.
- Whether the future AI/ML predictive-dose-optimization SaMD becomes a module of DLM or a separate SaMD — deferred to PCCP envelope planning.

## 10. Changelog

| Date | Author | Summary |
|---|---|---|
| 2026-04-14 | Claude (first-stab) | Initial scaffold derived from architecture + regulatory strategy docs. Seven-module decomposition; Class II SaMD accessory classification. Task 013. |
