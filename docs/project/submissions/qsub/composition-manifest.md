# Composition Manifest — Q-Sub (Pre-Submission)

> **🔒 INTERNAL — NOT TRANSMITTED.** Sponsor-side package-assembly artifact (tracker source of truth, milestone projection, readiness gates). Never sent to FDA; the FDA-facing package listing is the cover letter Attachments section (§ 6), which must align 1:1 with this manifest before transmission.

_Demo sample data — not for clinical use._

_Snapshot of which pieces of which DHF(s) are included in the PP3500 Q-Sub. Source of truth for `/tracker build`, `/submissions render`, and the submission package itself. Strategic framing is canonical in [`regulatory-strategy.md`](../../strategies/regulatory-strategy.md) — this manifest references it, it does not restate it._

## Filing Identification

| Field | Value |
|-------|-------|
| Filing type | Q-Sub (Pre-Submission) |
| Filing ID | TBD (assigned by FDA on receipt) |
| Submission folder | `docs/project/submissions/qsub/` |
| Milestone | qsub-release (posture: readiness-check) |
| Regulatory pathway | Pre-submission meeting request to validate PCCP scope, predicate, and accessory-bundling before the formal 510(k) |
| Target filing date | TBD |
| DHFs spanned | `pca-device` (lead) + `cloud-suite/drug-library-manager` (accessory SaMD) + `connectivity-adapter` (identified, not filed) |

## Included Pieces

The Q-Sub is strategic — it includes enough of the design-control record to frame the questions we are asking FDA, but not the full design-control package. The goal is to validate scope, classification, predicate, and PCCP envelope before investing in full V&V.

### Required (per FDA Q-Sub guidance + milestone bindings)

**Formal FDA submission deliverables**

| Piece | Path | Purpose in Q-Sub | Tracker Row |
|-------|------|------------------|-------------|
| Q-Sub cover letter | [`cover-letter.md`](./cover-letter.md) | Formal request for pre-submission meeting; identifies device, submitter, target date, and the primary questions | Q4 |
| Device description | [`device-description.md`](./device-description.md) | FDA-facing description of the PCA device + adjacent components, intended use, clinical context | Q5 |
| Proposed indications for use | [`intended-use.md`](./intended-use.md) | Draft IFU statement (patient population, care setting, user qualifications) | Q6 |
| PCCP summary | [`pccp-summary.md`](./pccp-summary.md) | Distilled PCCP scope for FDA discussion: change categories, modification protocols, monitoring | Q8 |
| Questions for FDA | [`fda-questions.md`](./fda-questions.md) | Consolidated primary question set — 6 questions across 3 topics | Q9 |

**Supporting technical architecture**

| Piece | Path | Purpose in Q-Sub | Tracker Row |
|-------|------|------------------|-------------|
| System SAD | [`pca-device system SAD`](../../dhfs/pca-device/design-controls/architecture/) | Establishes the PCA device architecture and the SaMD / SiMD / hardware boundary | Q1 |
| Predicate analysis | [`predicate-analysis`](../../input-analysis/predicate-analysis/README.md) | PP3000 (K190567) substantial-equivalence framing | Q7 |

**Required-Pre-Meeting strengthener briefs** (package should NOT transmit until these are at status ≥ `draft-v0.1`)

| Piece | Path | Purpose in Q-Sub | Status |
|-------|------|------------------|--------|
| Connectivity-Adapter MDDS rationale brief | [`mdds-rationale.md`](./mdds-rationale.md) | Anchors Q1.2 (Connectivity Adapter Non-Device-MDDS — not separately filed) | **draft-v0.0 — transmission-blocking** |
| Drug-Library-Manager accessory brief | [`accessory-samd-brief.md`](./accessory-samd-brief.md) | Anchors Q1.1 (bundle-vs-standalone for the Class II SaMD accessory) | **draft-v0.0 — strongly-desired, not transmission-blocking** |

### Supporting (advisory bindings — component-level detail)

| Piece | Path | Purpose in Q-Sub | Tracker Row |
|-------|------|------------------|-------------|
| Drug Library Manager DHF | [`cloud-suite/drug-library-manager`](../../dhfs/cloud-suite/drug-library-manager/) | Accessory-SaMD detail framing the bundling question | Q10 |
| Connectivity Adapter DHF | [`connectivity-adapter`](../../dhfs/connectivity-adapter/) | MDDS classification + cybersecurity story for the adjacent component | Q11 |

## Excluded Pieces

Intentionally out of scope for this Q-Sub. Listed so reviewers know what was not sent and why. (Bound to **510(k) + PCCP Release**, not Q-Sub.)

| Piece | Why excluded |
|-------|--------------|
| Full V&V protocols and results | Q-Sub precedes V&V execution; bound to 510(k) Release |
| Risk management file | Drafting in progress; ships with 510(k) Release |
| Clinical evaluation | Q-Sub asks whether clinical evidence is needed at all |
| Cybersecurity assessment (system-level) | Per-component evidence exists; system-level assessment ships with 510(k) Release |
| Labeling / DFU | Not polished for Q-Sub external review |

## Cross-References

This manifest spans 3 DHFs (1 lead device + 1 accessory SaMD + 1 identified MDDS). Per [`regulatory-strategy.md`](../../strategies/regulatory-strategy.md) § 1 (Filing Scope: PCA Device Alone), the PP3500 510(k) covers the PCA device; the adapter and Drug Library Manager are named adjacent components pulled in by composition, not by expanding the PP3500 DHF boundary.

## Reviewer Sign-off

_Roles only — per QMS. Author/contributor tracking lives in the Changelog below._

| Role | Name | Date | Signature |
|------|------|------|-----------|
| R&D Lead | _TBD_ | — | _pending_ |
| Regulatory Affairs | _TBD_ | — | _pending_ |
| Quality Assurance | _TBD_ | — | _pending_ |

## Changelog

| Date | Author | Summary |
|------|--------|---------|
| 2026-06-15 | BX / AI Assistant | Initial Q-Sub composition manifest (task ben/087) — demo seed for the project-console Submission section. Scope per regulatory-strategy.md §§ 1–2 (PCA device alone; adapter MDDS; Drug Library Manager accessory SaMD). |
