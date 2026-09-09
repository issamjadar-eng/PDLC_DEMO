---
version: v0.1
status: draft
summary: Formal request for an FDA pre-submission meeting on the PP3500 PCA Advanced — device scope, accessory bundling, predicate, and PCCP envelope.
---

<!-- AI-CHANGELOG — internal provenance of AI-assisted edits. Metadata only:
     NOT published downstream, NOT part of the controlled record, vendor-neutral.
| Date       | Task    | Summary                                              |
|------------|---------|------------------------------------------------------|
| 2026-06-15 | ben/087 | Cover letter drafted as a demo Q-Sub seed.           |
| 2026-09-08 | ben/123 | § 5 meeting-request placeholder resolved into a definitive commitment; the open logistics item moved into the 🔒 INTERNAL container as a managed TBD (owner: RA lead). AI assistant. |
-->

# Q-Sub Cover Letter — PainEase PCA Advanced (PP3500)

_Demo sample data — not for clinical use._

> **🔒 INTERNAL — working status.** Document control v0.1 · status: draft · authored under ben/087. Reading convention: 🔒 INTERNAL containers are stripped before transmission; the filed body (§§ 1–6) is what goes to FDA. Internal source mapping: regulatory-strategy.md §§ 1 (Filing Scope), 2 (Module Classification). `[VERIFY]` submitter, FDA division, and tracking-number fields before transmission. TBD (owner: Regulatory affairs lead) — confirm meeting format and attendees for § 5 before transmission.

## 1. Introduction 📤

The PainEase PCA Advanced (PP3500) is a Class II patient-controlled analgesia (PCA) infusion pump, a software-plus-hardware medical device combining SiMD pump firmware, custom medical-electrical hardware, and SaMD accessory components. We are requesting a Pre-Submission meeting to validate the device scope, accessory-bundling approach, predicate selection, and Predetermined Change Control Plan (PCCP) envelope before the formal 510(k) (K210345) filing.

## 2. Device Description & Proposed IFU 📤

PP3500 delivers clinician-programmed and patient-demand analgesic infusion governed by an on-device drug library. A condensed three-component summary follows; full detail is in [`device-description.md`](./device-description.md), and the device-level IFU is quoted from [`intended-use.md`](./intended-use.md).

| Component | Role | Classification posture |
|-----------|------|------------------------|
| PCA Device (PP3500) | Pump firmware + ME hardware | Class II medical device — the 510(k) subject |
| Drug Library Manager | Cloud SaMD that authors the enforced dose-limit table | Class II SaMD accessory (bundle vs standalone — Q1.1) |
| Connectivity Adapter | On-prem data conduit | Non-Device MDDS — identified, not separately filed (Q1.2) |

## 3. Predicate Strategy 📤

Primary predicate: **PainEase PCA (PP3000), K190567** — the prior-generation device from the same manufacturer. PP3500 preserves the intended use and core infusion technology; the substantial-equivalence discussion concerns the added connectivity and the SaMD accessory.

## 4. PCCP Scope 📤

We propose a single PCCP covering the post-clearance change envelope: drug-library updates, firmware updates against a fixed risk profile, and a predictive-alarm SaMD pathway — each bounded by the criticality-tagged change envelope described in [`pccp-summary.md`](./pccp-summary.md).

## 5. Pre-Submission Meeting Request 📤

We request a teleconference within FDA's standard Pre-Submission timeframe. On receipt of FDA's scheduling response, the sponsor will provide the proposed attendees and an agenda mapped to the six questions in [`fda-questions.md`](./fda-questions.md).

## 6. Submission Package Contents (Attachments) 📤

This list must align 1:1 with [`composition-manifest.md`](./composition-manifest.md) before transmission.

- Device description ([`device-description.md`](./device-description.md))
- Proposed indications for use ([`intended-use.md`](./intended-use.md))
- PCCP summary ([`pccp-summary.md`](./pccp-summary.md))
- Questions for FDA ([`fda-questions.md`](./fda-questions.md))
- System SAD (supporting technical architecture — provided on request)
