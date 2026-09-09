---
version: v0.1
status: draft
summary: FDA-facing description of the PP3500 PCA infusion pump and its adjacent components — architecture, clinical functions, predicate framing, and documentation level.
---

<!-- AI-CHANGELOG — internal provenance of AI-assisted edits. Metadata only:
     NOT published downstream (Confluence/Doc-Control), NOT part of the controlled
     record, stripped on DOCX/PDF export. Vendor-neutral by convention.
| Date       | Task    | Summary |
|------------|---------|---------|
| 2026-09-08 | ben/123 | Three `[VERIFY]` tags in the filed body resolved against project sources (FDA software-functions cascade at rung 3; separation claims against the three System SADs); open items recorded as managed TBDs in the INTERNAL container. |
-->
# Device Description — PainEase PCA Advanced (PP3500)

_Demo sample data — not for clinical use._

> **🔒 INTERNAL.** Document control v0.1 · companion to the PCA-device System SAD + Proposed IFU. Internal source mapping: regulatory-strategy.md §§ 1–2; predicate per `input-analysis/predicate-analysis/`. Architecture facts defer to the System SAD — reconcile before transmission. TBD (owner: Systems Engineering lead; RA confirms) — the System SAD is a first-stab draft; lock the separation wording in § 4 before transmission. TBD (owner: RA lead + Risk Management) — author the Documentation Level Statement (OBL-SWF-001) once the hazard analysis exists.

## 1. Purpose 📤

Q-Sub-level description of the PP3500 PCA infusion pump and its adjacent connectivity/SaMD components — sufficient to frame device scope, classification, and the substantial-equivalence discussion. Not full V&V detail.

## 2. Device Summary 📤

| Field | Value |
|-------|-------|
| Marketing name | PainEase PCA Advanced (PP3500) |
| Device type | Patient-controlled analgesia (PCA) infusion pump |
| Clinical area | Acute / post-operative pain management |
| Composition | SiMD pump firmware + custom medical-electrical hardware + SaMD accessory (Drug Library Manager) |
| Intended users | Clinicians (programming) and patients (demand dosing) under clinician supervision |
| Predicate | PainEase PCA (PP3000), K190567 |
| Filing pathway | 510(k) with PCCP (K210345) |
| Documentation level | Enhanced — failure of the dose-enforcement functions could present a hazardous situation with a probable risk of death or serious injury prior to risk controls, and per the FDA software-functions guidance the level applies to the device as a whole; the formal Documentation Level Statement is provided with the 510(k) |

## 3. Component Architecture 📤

- **PCA Device (PP3500)** — the pump: dose computation, occlusion/air-in-line safety, the enforced drug-library limit table, and the patient demand button. Class II medical device; the 510(k) subject.
- **Drug Library Manager** — cloud SaMD that authors and distributes the dose-limit table the pump enforces. Class II SaMD accessory (it directly affects dose enforcement).
- **Connectivity Adapter** — on-prem conduit moving programming and event data between the pump and hospital systems. Non-Device MDDS (post-2015 FDA reclassification).

## 4. Clinical Functions per Component 📤

- Pump: continuous + demand-bolus infusion, lockout-interval enforcement, dose/time limits, alarms.
- Drug Library Manager: formulary authoring, dose-limit validation, signed library distribution.
- Connectivity Adapter: store-and-forward of orders and infusion events (no clinical computation).

## 5. Software Architecture & Component Separation 📤

The pump enforces safety limits independently of network availability; the Drug Library Manager cannot command an infusion — it only supplies the limit table the pump authenticates and integrity-checks (signature, version roll-forward) before caching and enforcing. The adapter performs no clinical computation.

## 6. Intended Users 📤

Licensed clinicians program therapy; patients self-administer demand doses within clinician-set limits.

## 7. Predicate Justification 📤

PP3000 (K190567) shares the intended use and core infusion technology. PP3500 adds connectivity and a SaMD accessory; the substantial-equivalence argument addresses whether these raise different questions of safety or effectiveness.

## 8. Software Documentation Level 📤

Enhanced documentation is proposed on the basis of the device's safety role (dose enforcement): failure of any dose-enforcement function could present a hazardous situation with a probable risk of death or serious injury before risk controls, and per the FDA software-functions guidance the documentation level applies to the device as a whole. The formal Documentation Level Statement and its supporting risk assessment will be provided in the 510(k).

## 9. Cross-Reference Grounding Map 📝

_Internal — maps each section to upstream artifacts (System SAD, predicate analysis, regulatory-strategy.md). Stripped at transmission._
