# 21 CFR Part 892 — Radiology Devices

**Citation**: 21 CFR Part 892 (Title 21, Chapter I, Subchapter H)
**Authority**: 21 U.S.C. 351, 360, 360c, 360e, 360j, 360l, 371
**Promulgating Agency**: FDA / CDRH
**Status**: Active (current at retrieval date — see Source provenance)
**Source**: eCFR API — `https://www.ecfr.gov/api/versioner/v1/full/<date>/title-21.xml?chapter=I&subchapter=H&part=892`

## Scope

Part 892 classifies radiology devices — diagnostic imaging hardware (X-ray, MRI, CT, ultrasound, nuclear medicine), image-management and image-processing software, and radiology-therapy equipment. It is the regulatory home of **§ 892.2050 — Medical image management and processing system (QIH product code, Class II)**, the dominant classification for imaging-planning and PACS-style software used in surgical planning, treatment planning, and image-analysis workflows. Recently-added sections § 892.2060–§ 892.2080 cover **radiological CAD / CADe / CAD-triage** software — the regulatory landing zone for many AI-enabled imaging SaMDs.

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
| § 892.2030 | Medical image digitizer | II | Exempt | LLZ product code |
| § 892.2040 | Medical image hardcopy device | II | Exempt | LMD product code |
| § 892.2050 | **Medical image management and processing system** | II | **Required** | **QIH product code — PACS/planning/processing** |
| § 892.2060 | Radiological CAD software for lesions suspicious of cancer | II | Required | CADx |
| § 892.2070 | Medical image analyzer | II | Required | CADe |
| § 892.2080 | Radiological computer-aided triage and notification software | II | Required | CAD-triage |

## Subpart A — General Provisions

### § 892.9 — Limitations of exemptions from section 510(k)

> The exemption from the requirement of premarket notification (510(k)) for a generic type of device is only to the extent that the device has existing or reasonably foreseeable characteristics of commercially distributed devices within that generic type or, in the case of in vitro diagnostic devices, only to the extent that misdiagnosis as a result of using the device would not be associated with high morbidity or mortality. Accordingly, manufacturers of any commercially distributed device for which FDA has granted an exemption from the requirement of premarket notification must still submit a premarket notification to FDA before introducing or delivering for introduction into interstate commerce for commercial distribution the device when:
>
> **(a)** The device is intended for a use different from the intended use of a legally marketed device in that generic type of device; e.g., the device is intended for a different medical purpose, or the device is intended for lay use where the former intended use was by health care professionals only;
>
> **(b)** The modified device operates using a different fundamental scientific technology than a legally marketed device in that generic type of device; e.g., a surgical instrument cuts tissue with a laser beam rather than with a sharpened metal blade, or an in vitro diagnostic device detects or identifies infectious agents by using deoxyribonucleic or ribonucleic acid hybridization or amplification rather than culture or immunoassay techniques.

**Why this matters.** Same framework as § 880.9. § 892.9 governs whether 510(k)-exempt imaging devices (§ 892.2010 image storage, § 892.2020 image communications) lose their exempt status. AI-enabled image storage that does anything beyond passive storage — e.g., automatic image preprocessing, indexing-by-clinical-feature, or worklist prioritization — likely crosses § 892.9(b) ("different fundamental scientific technology") and triggers a 510(k). The audit-relevant pattern: project docs claiming § 892.2010 exemption for AI-enabled image storage need an explicit § 892.9 non-applicability analysis.

## Subpart B — Diagnostic Devices (Image-System Chain)

### § 892.2010 — Medical image storage device

> A medical image storage device is a device that provides electronic storage and retrieval functions for medical images. Examples include devices employing magnetic and optical discs, magnetic tape, and digital memory.
>
> **Classification.** Class I (exempt from premarket notification subject to the limitations in § 892.9).

Practical: passive image storage only. Adding processing, indexing, or workflow features may cross § 892.9 and trigger 510(k).

### § 892.2020 — Medical image communications device

> A medical image communications device provides electronic transfer of medical image data between medical devices. It may include a physical communications medium, modems, interfaces, and a communications protocol.
>
> **Classification.** Class I (exempt from premarket notification subject to the limitations in § 892.9).

Practical: passive image transfer. PACS communications layers that also perform processing fall into § 892.2050 territory.

### § 892.2030 — Medical image digitizer

> A medical image digitizer is a device intended to convert an analog medical image into a digital format. Examples include systems employing video frame grabbers, and scanners which use lasers or charge-coupled devices.
>
> **Classification.** Class II.

### § 892.2040 — Medical image hardcopy device

> A medical image hardcopy device is a device that produces a visible printed record of a medical image and associated identification information. Examples include multiformat cameras and laser printers.
>
> **Classification.** Class II.

### § 892.2050 — Medical image management and processing system (QIH)

#### Verbatim — § 892.2050(a) Identification

> A medical image management and processing system is a device that provides one or more capabilities relating to the review and digital processing of medical images for the purposes of interpretation by a trained practitioner of disease detection, diagnosis, or patient management. The software components may provide advanced or complex image processing functions for image manipulation, enhancement, or quantification that are intended for use in the interpretation and analysis of medical images. Advanced image manipulation functions may include image segmentation, multimodality image registration, or 3D visualization. Complex quantitative functions may include semi-automated measurements or time-series measurements.

#### Verbatim — § 892.2050(b) Classification

> Class II (special controls; voluntary standards — Digital Imaging and Communications in Medicine (DICOM) Std., Joint Photographic Experts Group (JPEG) Std., Society of Motion Picture and Television Engineers (SMPTE) Test Pattern).

#### Practical notes

- **Product code: QIH.** Almost all imaging-planning, PACS, and segmentation/measurement SaMDs cleared as 510(k) Class II clear under product code QIH against § 892.2050.
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

## Practical Cross-References

| Question | Look here |
|----------|-----------|
| What classification covers our imaging-planning / surgical-planning / PACS software? | § 892.2050 (QIH, Class II, 510(k) required) — the default |
| Is our AI-enabled image storage really § 892.2010 exempt? | § 892.2010 + § 892.9(b) "different fundamental scientific technology" analysis |
| Where does autonomous AI diagnostic output land? | § 892.2060 (CADx), § 892.2070 (CADe), or § 892.2080 (CAD-triage) — not § 892.2050 |
| What's the special-controls reference for QIH? | DICOM Std., JPEG Std., SMPTE Test Pattern (per § 892.2050(b)) |
| Companion guidance for QIH SaMD? | `../fda-guidance/sw-functions-distilled.md`, `../fda-guidance/ai-dsf-lifecycle-distilled.md`, and `../fda-guidance/pccp-aiml-distilled.md` for AI |

## Source Provenance

- **eCFR API endpoint**: `https://www.ecfr.gov/api/versioner/v1/full/<date>/title-21.xml?chapter=I&subchapter=H&part=892`
- **Retrieval date**: 2026-05-29
- **eCFR raw XML**: archived under `source/21-cfr-part-892.xml` (when present)
- **Companion FDA guidance**: `../fda-guidance/sw-functions-distilled.md`, `../fda-guidance/ai-dsf-lifecycle-distilled.md`
- **Authoring**: distilled from eCFR-returned content via a `citations` audit that surfaced this section as a `registry-gap`.

[VERIFY all clause numbers and verbatim text against the live eCFR snapshot before relying on this distillation in a regulated submission.]
