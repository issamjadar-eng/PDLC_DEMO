# Tier 1 Regulatory Distillation — FDA Clinical Decision Support Guidance

**Guidance**: Clinical Decision Support Software
**Date**: January 6, 2026 (Final; re-issued January 29, 2026)
**Statutory basis**: 21st Century Cures Act (December 2016); FD&C Act §520(o)(1)(E)
**Topic coverage**: regulatory-submission
**Distillation date**: 2026-04-21
**Source references**:
- `.claude/skills/medtech-docs/references/fda-guidance/cds-distilled.md`

> **Note**: FDA guidance is nonbinding, but the four CDS criteria are derived from binding statutory text (21st Century Cures Act).

---

<a id="OBL-CDS-001"></a>

```yaml
id: OBL-CDS-001
title: "CDS Criterion 1 Analysis"
source: FDA CDS Guidance (2026) §IV Criterion 1
section: "Criterion 1 — Does NOT Acquire, Process, or Analyze Certain Data Types"
scope_flags: [common-baseline, 510k]
topic: regulatory-submission
artifact_type: analysis
dhf_owner: system
min_iec62304_class: A
applies_to: [Device Classification Determination, 510(k) Submission — Device Description, CDS Exemption Analysis]
verbatim: "The software function must not acquire, process, or analyze: medical images, signals from an IVD, or patterns or signals from a signal acquisition system. Any software that directly analyzes X-rays, CT scans, MRI, ultrasound, or similar data is a device regardless of whether it meets criteria 2-4."
extracted_requirements:
  - Any software function that acquires, processes, or analyzes medical images FAILS criterion 1 and is a device (SaMD) — cannot claim CDS non-device status
  - HipLink Pre-Op FAILS criterion 1: it processes CT/MRI images for anatomy segmentation and implant sizing → is a SaMD device
  - HipLink Intra-Op FAILS criterion 1: it acquires and processes C-arm fluoroscopy images for surgical guidance → is a SaMD device
  - Software analyzing HCP-reported findings (not images themselves) may qualify as non-device CDS if other criteria are met
  - Management Services PostOp Reports must be analyzed: if it analyzes imaging data → is a device; if it only displays clinical summaries from HCP-reported findings → may be non-device
```

**Context**: This criterion confirms HipLink Pre-Op and Intra-Op ARE devices — they process medical images. This is not ambiguous. The CDS analysis must be documented to explain WHY these modules are devices (criterion 1 failure), and WHY Management Services PostOp reporting is NOT a device (must demonstrate it does not process medical images or signal patterns — it only displays clinical summaries from structured data reported by clinicians). Document this analysis in the device classification section of the 510(k).

---

<a id="OBL-CDS-002"></a>

```yaml
id: OBL-CDS-002
title: "CDS Criteria 3–4 Analysis"
source: FDA CDS Guidance (2026) §IV Criteria 3 and 4
section: "Criterion 3 — Supports HCP Recommendations; Criterion 4 — Enables Independent Review"
scope_flags: [common-baseline, 510k]
topic: regulatory-submission
artifact_type: analysis
dhf_owner: system
min_iec62304_class: A
applies_to: [Device Classification Determination, 510(k) Submission — Indications for Use, Labeling]
verbatim: "Criterion 3: Does not provide a specific preventive, diagnostic, or treatment output or directive; is not intended to replace the HCP's judgment. Criterion 4: The software enables an HCP to independently review the basis for recommendations so the HCP does not rely primarily on such recommendations. Higher automation increases risk of automation bias; time-critical nature moves from criterion 3 to criterion 4."
extracted_requirements:
  - For Management Services PostOp Reports: evaluate against all four CDS criteria to confirm non-device status
  - Criterion 4 requires the HCP to be able to independently verify any recommendation — software must provide sufficient supporting information
  - Time-critical outputs (e.g., intraoperative alerts for life-threatening conditions) fail criterion 4 — HCP cannot adequately review basis in real-time
  - High automation level risks automation bias — criterion 4 consideration
  - Enforcement discretion applies when only ONE clinically appropriate recommendation exists (cannot fail criterion 3 in that case)
```

**Context**: For Management Services PostOp Reports, if the reports ever include any clinical recommendations (beyond administrative summaries), criteria 3 and 4 must be satisfied to maintain non-device status. Currently scoped as administrative-only (no clinical claims), so the CDS analysis is primarily confirming criterion 1 is satisfied (no medical image processing). But any future PostOp feature that generates clinical recommendations would trigger a full CDS re-analysis.

---

<a id="OBL-CDS-003"></a>

```yaml
id: OBL-CDS-003
title: "CDS Device Determination"
source: FDA CDS Guidance (2026) §V Device Determination Process
section: "513(g) Request and Q-Sub for CDS Classification Questions"
scope_flags: [common-baseline, 510k]
topic: regulatory-submission
artifact_type: process-record
dhf_owner: system
min_iec62304_class: A
applies_to: [Q-Sub Package, Device Classification Documentation]
verbatim: "For software where CDS status is uncertain, FDA recommends submitting a 513(g) request for device determination, or using a Q-Submission to discuss with FDA."
extracted_requirements:
  - For any software function where CDS non-device status is uncertain: use a Q-Sub (pre-submission meeting) to get FDA feedback before filing the 510(k)
  - Document the CDS analysis (four-criterion evaluation) for each software function in the 510(k) submission
  - Management Services PostOp Reports: if there is any uncertainty about non-device status, raise it as a Q-Sub question before submission
  - The CDS classification determination is a required part of the 510(k) device description section
```

**Context**: The Management Services PostOp Reports classification (device vs. non-device) is an open Q-Sub question for HipLink. If FDA disagrees with the non-device positioning, it would require a separate regulatory pathway for PostOp Reports. Raising this as a specific Q-Sub question before filing the 510(k) is the least-burdensome approach — get FDA alignment on the classification early rather than receiving an NSE determination.
