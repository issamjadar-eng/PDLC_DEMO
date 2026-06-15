---
version: v0.1
status: draft
summary: 510(k) transmittal cover letter — identifies the device, submitter, predicate, regulation/product code, and the attachments comprising the premarket notification.
---

<!-- AI-CHANGELOG — internal provenance of AI-assisted edits. Metadata only:
     NOT published downstream, NOT part of the controlled record, vendor-neutral.
| Date       | Task   | Summary                                                |
|------------|--------|--------------------------------------------------------|
| {{DATE}} | {{TASK}} | 510(k) cover letter scaffolded from the submissions template. |
-->

# {{FILING_SHORT}} Cover Letter — {{DEVICE}}

_Demo sample data — not for clinical use._

> **🔒 INTERNAL — working status.** Document control v0.1 · status: draft · authored under {{TASK}}. Reading convention: 🔒 INTERNAL containers are stripped before transmission; the filed body (§§ below) is what goes to FDA. Internal source mapping: {{D_REG_REFS}}.

## 1. Submission Identification 📤

Premarket Notification under section 510(k) of the FD&C Act for **{{DEVICE}}**. Submitter / correspondent, establishment registration, and contact details follow. `[VERIFY] confirm submitter, official correspondent, and registration numbers before transmission.`

## 2. Device & Classification 📤

- **Common/usual name:** `[VERIFY]`
- **Classification regulation:** `[VERIFY] 21 CFR §___`
- **Product code:** `[VERIFY]`
- **Device class:** `[VERIFY]`

Condensed device summary (full detail in [`device-description.md`](./device-description.md)); proposed indications quoted from [`indications-for-use.md`](./indications-for-use.md).

## 3. Predicate & Basis for Substantial Equivalence 📤

Primary predicate {{PREDICATE}}; reference device(s) per the predicate analysis. The substantial-equivalence argument is developed in [`substantial-equivalence.md`](./substantial-equivalence.md).

## 4. Submission Package Contents (Attachments) 📤

This list must align 1:1 with [`composition-manifest.md`](./composition-manifest.md) before transmission.

_Authored in this submission folder:_

- Indications for Use (Form FDA 3881)
- 510(k) Summary (or 510(k) Statement)
- Device description
- Substantial-equivalence discussion + predicate comparison
- Performance testing summary
- Truthful & Accuracy Statement (21 CFR 807.87(l))

_Attached from the DHF (controlled-record PDFs, not authored here — per the QMS submission WI):_

- Proposed labeling (IFU, instructions for use, warnings/precautions/contraindications)
- Consensus-standards list / declarations of conformity to FDA-recognized standards

## 5. Statements & Certifications 📝

Truthful-&-accuracy statement filed separately ([`truthful-accuracy-statement.md`](./truthful-accuracy-statement.md)); financial certification/disclosure per current FDA requirements. Original 510(k)s are submitted as an **eSTAR** via the CDRH Customer Collaboration Portal (eSTAR is mandatory for 510(k)s; an eCopy is not an accepted electronic submission). `[VERIFY] confirm which certifications this submission requires and the current eSTAR submission mechanics.`
