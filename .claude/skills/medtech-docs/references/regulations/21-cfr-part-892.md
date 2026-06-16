# 21 CFR Part 892 — Radiology Devices

🔎 **Finding aid — NOT the authoritative source.** Distilled summary with selected commentary. Ground and cite the faithful verbatim full text [`source-md/21-cfr-part-892.md`](source-md/21-cfr-part-892.md) (a no-LLM transcription of the eCFR XML), not this file. Regulations change — verify currency against the live eCFR before relying on it in a submission. `[VERIFY]` marks are unconfirmed.

**Citation**: 21 CFR Part 892 (Title 21, Chapter I, Subchapter H)
**Authority**: 21 U.S.C. 351, 360, 360c, 360e, 360j, 360l, 371
**Promulgating Agency**: FDA / CDRH
**Status**: Active (current at retrieval date — see Source provenance)
**Source**: eCFR API — `https://www.ecfr.gov/api/versioner/v1/full/<date>/title-21.xml?chapter=I&subchapter=H&part=892`

## Scope

Part 892 classifies radiology devices — diagnostic imaging hardware (X-ray, MRI, CT, ultrasound, nuclear medicine), image-management and image-processing software, and radiology-therapy equipment. It is the regulatory home of **§ 892.2050 — Medical image management and processing system (Class II; product codes LLZ and QIH — see practical notes)**, the dominant classification for imaging-planning and PACS-style software used in surgical planning, treatment planning, and image-analysis workflows. Recently-added sections § 892.2060–§ 892.2080 cover **radiological CAD / CADe / CAD-triage** software — the regulatory landing zone for many AI-enabled imaging SaMDs.

Part 892 contains Subparts A–G:

| Subpart | Title |
|---------|-------|
| A | General Provisions |
| B | Diagnostic Devices |
| C–E | [Reserved] |
| F | Therapeutic Devices |
| G | Miscellaneous Devices |

This distillation focuses on **Subpart A § 892.9** (exemption-limitation framework) and **Subpart B § 892.2010–§ 892.2080** (the image-system regulatory chain).

## Section Index — Sections Relevant to Imaging SaMD / PACS / AI

| Section | Title | Class | 510(k)? | Notes |
|---------|-------|-------|---------|-------|
| § 892.1 | Scope | n/a | n/a | |
| § 892.9 | Limitations of exemptions from section 510(k) | n/a | n/a | Same framework pattern as § 880.9 |
| § 892.1715 | Full-field digital mammography system | II | Required | |
| § 892.1750 | Computed tomography x-ray system | II | Required | |
| § 892.2010 | Medical image storage device | I | **Exempt** | Subject to § 892.9 |
| § 892.2020 | Medical image communications device | I | **Exempt** | Subject to § 892.9 |
| § 892.2030 | Medical image digitizer | II | **Exempt** | Subject to § 892.9; special controls DICOM/JPEG (verified vs eCFR 2026-06-11) |
| § 892.2040 | Medical image hardcopy device | II | **Exempt** | Subject to § 892.9; special controls DICOM/JPEG/SMPTE (verified vs eCFR 2026-06-11) |
| § 892.2050 | **Medical image management and processing system** | II | **Required** | **Product codes LLZ + QIH — PACS/planning/processing** |
| § 892.2060 | Radiological CAD software for lesions suspicious of cancer | II | Required | CADx |
| § 892.2070 | Medical image analyzer | II | Required | CADe |
| § 892.2080 | Radiological computer-aided triage and notification software | II | Required | CAD-triage |

## Subpart A — General Provisions

### § 892.9 — Limitations of exemptions from section 510(k)

> The exemption from the requirement of premarket notification (section 510(k) of the act) for a generic type of class I or II device is only to the extent that the device has existing or reasonably foreseeable characteristics of commercially distributed devices within that generic type or, in the case of in vitro diagnostic devices, only to the extent that misdiagnosis as a result of using the device would not be associated with high morbidity or mortality. Accordingly, manufacturers of any commercially distributed class I or II device for which FDA has granted an exemption from the requirement of premarket notification must still submit a premarket notification to FDA before introducing or delivering for introduction into interstate commerce for commercial distribution the device when:
>
> **(a)** The device is intended for a use different from the intended use of a legally marketed device in that generic type of device; e.g., the device is intended for a different medical purpose, or the device is intended for lay use where the former intended use was by health care professionals only;
>
> **(b)** The modified device operates using a different fundamental scientific technology than a legally marketed device in that generic type of device; e.g., a surgical instrument cuts tissue with a laser beam rather than with a sharpened metal blade, or an in vitro diagnostic device detects or identifies infectious agents by using deoxyribonucleic acid (DNA) probe or nucleic acid hybridization technology rather than culture or immunoassay technology; or
>
> **(c)** The device is an in vitro device that is intended: [the same nine IVD categories as § 880.9(c)(1)–(9) — neoplastic-disease diagnosis/monitoring/screening, genetic disorders, surrogate-marker analytes, cardiovascular-risk assessment, diabetes management, microorganism identification, non-IgG antibody detection, noninvasive testing per § 812.3(k), near-patient testing. Verified present (c)(1)–(c)(9) against live eCFR 2026-06-11; see `21-cfr-part-880.md` § 880.9 for the full verbatim list — the § X.9 boilerplate is identical across parts.]

**Why this matters.** Same framework as § 880.9. § 892.9 governs whether 510(k)-exempt imaging devices (§ 892.2010 image storage, § 892.2020 image communications) lose their exempt status. AI-enabled image storage that does anything beyond passive storage — e.g., automatic image preprocessing, indexing-by-clinical-feature, or worklist prioritization — likely crosses § 892.9(b) ("different fundamental scientific technology") and triggers a 510(k). The audit-relevant pattern: project docs claiming § 892.2010 exemption for AI-enabled image storage need an explicit § 892.9 non-applicability analysis.

## Subpart B — Diagnostic Devices (Image-System Chain)

### § 892.2010 — Medical image storage device

> A medical image storage device is a hardware device that provides electronic storage and retrieval functions for medical images. Examples include electronic hardware devices employing magnetic and optical discs, magnetic tapes, and digital memory.
>
> **Classification.** Class I (general controls). The device is exempt from the premarket notification procedures in subpart E of part 807 of this chapter subject to § 892.9.

Practical: passive image storage only. Adding processing, indexing, or workflow features may cross § 892.9 and trigger 510(k).

### § 892.2020 — Medical image communications device

> A medical image communications device provides electronic transfer of medical image data between medical devices. It may include a physical communications medium, modems, and interfaces. It may provide simple image review software functionality for medical image processing and manipulation, such as grayscale window and level, zoom and pan, user delineated geometric measurements, compression, or user added image annotations. The device does not perform advanced image processing or complex quantitative functions. This does not include electronic transfer of medical image software functions.
>
> **Classification.** Class I (general controls). The device is exempt from the premarket notification procedures in subpart E of part 807 of this chapter subject to § 892.9.

Practical: passive image transfer. PACS communications layers that also perform processing fall into § 892.2050 territory.

### § 892.2030 — Medical image digitizer

> A medical image digitizer is a device intended to convert an analog medical image into a digital format. Examples include systems employing video frame grabbers, and scanners which use lasers or charge-coupled devices.
>
> **Classification.** Class II (special controls; voluntary standards — DICOM Std., JPEG Std.). **The device is exempt from the premarket notification procedures in subpart E of part 807 of this chapter subject to the limitations in § 892.9.** (Exemption sentence verified against live eCFR 2026-06-11 — a prior version of this file quoted bare "Class II," contradicting the index table.)

### § 892.2040 — Medical image hardcopy device

> A medical image hardcopy device is a device that produces a visible printed record of a medical image and associated identification information. Examples include multiformat cameras and laser printers.
>
> **Classification.** Class II (special controls; voluntary standards — DICOM Std., JPEG Std., SMPTE Test Pattern). **The device is exempt from the premarket notification procedures in subpart E of part 807 of this chapter subject to the limitations in § 892.9.** (Verified against live eCFR 2026-06-11; eCFR source cite: 63 FR 23387, Apr. 29, 1998, as amended at 84 FR 71819, Dec. 30, 2019 — the 2019 amendment is the Class-II-exemption sweep.)

### § 892.2050 — Medical image management and processing system (QIH)

#### Verbatim — § 892.2050(a) Identification

> A medical image management and processing system is a device that provides one or more capabilities relating to the review and digital processing of medical images for the purposes of interpretation by a trained practitioner of disease detection, diagnosis, or patient management. The software components may provide advanced or complex image processing functions for image manipulation, enhancement, or quantification that are intended for use in the interpretation and analysis of medical images. Advanced image manipulation functions may include image segmentation, multimodality image registration, or 3D visualization. Complex quantitative functions may include semi-automated measurements or time-series measurements.

#### Verbatim — § 892.2050(b) Classification

> Class II (special controls; voluntary standards — Digital Imaging and Communications in Medicine (DICOM) Std., Joint Photographic Experts Group (JPEG) Std., Society of Motion Picture and Television Engineers (SMPTE) Test Pattern).

#### Practical notes

- **Two product codes live under § 892.2050 — do not conflate them.** **LLZ** ("System, Image Processing, Radiological") is the long-standing code — classic PACS, image-management, and most legacy imaging-planning/segmentation software cleared under LLZ. **QIH** ("Automated Radiological Image Processing Software") is the newer code typically assigned to automated/AI-driven image-processing software. A predicate-landscape search scoped to QIH alone will miss the (much larger) LLZ clearance history, and vice versa — search § 892.2050 by regulation number, or both codes. `[VERIFY current code assignments against the FDA Product Classification database for the specific device profile]`
- **NOT exempt.** Unlike § 892.2010 (storage) and § 892.2020 (communications), § 892.2050 requires a 510(k).
- **Scope is broad.** Image manipulation, segmentation, multimodality registration, 3D visualization, semi-automated measurements, time-series quantification — all fall in scope. The breadth is why QIH is the default landing zone for orthopedic / cardiac / oncology imaging planning software.
- **AI-specific overlay.** AI-enabled QIH devices follow the AI-DSF lifecycle guidance and the AI/ML PCCP guidance for change management. The classification (QIH § 892.2050) does not change because the device is AI-enabled; AI specifics live in companion guidance.
- **Boundary with § 892.2060 / § 892.2070 / § 892.2080.** Cancer-CAD (§ 892.2060), CADe analyzers (§ 892.2070), and CAD-triage (§ 892.2080) are distinct classifications for autonomous-output AI. If the device's AI delivers a triage call or a CADx finding directly, it likely belongs in those classifications, not § 892.2050.

### § 892.2060 — Radiological computer-assisted diagnostic software for lesions suspicious of cancer (CADx)

Class II. The CADx classification for AI delivering a probability-of-malignancy or similar diagnostic output.

### § 892.2070 — Medical image analyzer (CADe)

Class II. The CADe classification for AI detecting candidate lesions for the clinician's review.

### § 892.2080 — Radiological computer-aided triage and notification software (CAD-triage)

Class II. The CAD-triage classification for AI prioritizing imaging worklists based on likely-positive findings.

## Adjacent Classification Outside Part 892 — Surgical Navigation

**21 CFR 882.4560 — Stereotaxic instrument (Part 882, Neurological Devices; Class II).** Image-guided surgical *navigation* systems — including orthopedic navigation platforms from major manufacturers — have historically been cleared under § 882.4560 (stereotaxic instrument), not under § 892.2050, even though they consume radiological images. The boundary intuition: § 892.2050 covers image *management/processing for interpretation and planning*; § 882.4560 covers systems that *spatially guide instruments relative to anatomy* intra-operatively. A predicate landscape for intra-operative guidance software should sweep **both** § 892.2050 (LLZ/QIH) and § 882.4560 clearances. `[VERIFY the applicable product codes under 882.4560 for the specific navigation profile against the FDA Product Classification database]`

## Practical Cross-References

| Question | Look here |
|----------|-----------|
| What classification covers our imaging-planning / surgical-planning / PACS software? | § 892.2050 (Class II, 510(k) required; product codes LLZ + QIH) — the default for planning/processing |
| What about intra-operative navigation / instrument guidance? | 21 CFR 882.4560 (stereotaxic instrument) — see the adjacent-classification section; sweep both in predicate searches |
| Is our AI-enabled image storage really § 892.2010 exempt? | § 892.2010 + § 892.9(b) "different fundamental scientific technology" analysis |
| Where does autonomous AI diagnostic output land? | § 892.2060 (CADx), § 892.2070 (CADe), or § 892.2080 (CAD-triage) — not § 892.2050 |
| What's the special-controls reference for QIH? | DICOM Std., JPEG Std., SMPTE Test Pattern (per § 892.2050(b)) |
| Companion guidance for QIH SaMD? | `../fda-guidance/sw-functions-distilled.md`, `../fda-guidance/ai-dsf-lifecycle-distilled.md`, and `../fda-guidance/pccp-aiml-distilled.md` for AI |

## Source Provenance

- **eCFR API endpoint**: `https://www.ecfr.gov/api/versioner/v1/full/<date>/title-21.xml?chapter=I&subchapter=H&part=892` (the human-viewer `ecfr.gov/current/...` URLs redirect automated fetchers; use the API)
- **Retrieval date**: 2026-05-29; **§§ 892.2030, 892.2040, 892.9(c) re-verified against live eCFR 2026-06-11** (exemption sentences + special controls + (c) IVD list confirmed); product-code notes corrected same date (LLZ/QIH conflation)
- (No `source/` XML archive exists yet for this category — the live eCFR API is the escalation path.)
- **Companion FDA guidance**: `../fda-guidance/sw-functions-distilled.md`, `../fda-guidance/ai-dsf-lifecycle-distilled.md`
- **Authoring**: distilled from eCFR-returned content via a `citations` audit that surfaced this section as a `registry-gap`.

[VERIFY all clause numbers and verbatim text against the live eCFR snapshot before relying on this distillation in a regulated submission.]
