---
version: v0.1
status: draft
summary: PP3500 PCCP scope distilled for FDA discussion — change categories (drug library, firmware, predictive-alarm SaMD), modification protocols, and post-market monitoring.
---

# PCCP Summary — PainEase PCA Advanced (PP3500)

_Demo sample data — not for clinical use._

> **🔒 INTERNAL.** Document control v0.1. Internal source mapping: regulatory-strategy.md § 1 (Critical-Requirement Carve-out; PCCP envelope = Ct*-tagged change types within pre-specified bounds). Strategic posture notes internal-only.

## 1. Purpose 📤

Distilled PCCP scope and structure for Q-Sub discussion. The PCCP defines the post-clearance change envelope so routine, pre-specified updates ship without a new 510(k).

## 2. Device & PCCP Scope 📤

The PCCP covers the PCA device (PP3500) and its dose-enforcement accessory. The Connectivity Adapter (MDDS) is outside the PCCP. The envelope is defined **structurally** as change types that touch criticality-tagged (Ct*) requirements but stay within pre-specified bounds — not as a free-form list.

## 3. Description of Modifications (candidate categories) 📤

| # | Category | Example |
|---|----------|---------|
| C1 | Drug-library updates | New formulary entries / revised dose limits validated against the acceptance protocol |
| C2 | Firmware updates against a fixed risk profile | Defect fixes and performance updates with no new hazard family |
| C3 | Predictive-alarm SaMD additions | Alarm models meeting the change-protocol acceptance criteria |

`[VERIFY] keep category counts in sync with regulatory-strategy.md as the PCCP detail is authored.`

## 4. Modification Protocol Structure 📤

Each category carries a modification protocol: data management, validation method, pre-specified acceptance criteria, and implementation/rollback procedure.

## 5. Performance Criteria & Acceptance Posture 📤

Numeric acceptance values are `[locked at design transfer / pending FDA input]` — Q2.2 asks FDA what the drug-library update acceptance bar should be, so committing values here would be circular.

## 6. Software Changes Routing 📤

Each post-clearance change routes to exactly one of: PCCP-bounded execution, Letter-to-File, or a new 510(k), per 21 CFR 807.81(a)(3) and the FDA software-changes guidance. Changes executed within the cleared PCCP envelope are lawful without a new submission under the **21 CFR 807.81(b) predetermined-change-control-plan carve-out** (statutory basis: FD&C Act § 515C / FDORA 2022) — the regulatory hook that makes PCCP-authorized modifications permissible without a per-change 510(k).

## 7. Post-Market Monitoring Plan 📤

Category-specific performance monitoring, rollback triggers on drug-library or firmware regressions, and a periodic risk-management review cadence per ISO 14971 § 9.

## 8. Precedent Landscape 📖

_Reference — cleared infusion-pump PCCPs as precedent. `[VERIFY] K-numbers before citing.`_
