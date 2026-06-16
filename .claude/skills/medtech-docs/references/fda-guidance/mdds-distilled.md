# FDA Guidance: Medical Device Data Systems, Medical Image Storage Devices, and Medical Image Communications Devices

🔎 **Finding aid — NOT the authoritative source.** Distilled summary for quick orientation and early analysis. Ground and cite the authoritative full text [`source-md/mdds.md`](source-md/mdds.md); verify any quote against the byte-correct `source/` PDF before treating it as verbatim. This paraphrases and omits (appendices/worked examples are routinely dropped) — a section's absence here is never evidence the source is silent.

**Full Title**: Medical Device Data Systems, Medical Image Storage Devices, and Medical Image Communications Devices: Guidance for Industry and Food and Drug Administration Staff
**Document Date**: **September 28, 2022** (minor update); **originally issued February 9, 2015**; previously revised September 27, 2019
**Status**: Final (Contains Nonbinding Recommendations)
**Docket Number**: FDA-2014-D-0798
**CDRH Document Number**: 1400021
**Issuing Bodies**: CDRH + CBER
**Statutory Basis**: 21st Century Cures Act § 3060 (Dec 13, 2016) amending FD&C Act § 520(o)(1)(D); FD&C Act § 201(h) device definition
**Companion Regulation**: 21 CFR 880.6310 (MDDS — Class I exempt, reclassified 2011) — see `../../regulations/21-cfr-part-880.md`. Plus 21 CFR 892.2010 (Medical Image Storage Device, Class I exempt) and 21 CFR 892.2020 (Medical Image Communications Device, Class I exempt) — see `../../regulations/21-cfr-part-892.md`.
**Companion Guidance**: `mfd-distilled.md` (Multiple Function Device); `sw-functions-distilled.md` (Policy for Device Software Functions); `cds-distilled.md` (Clinical Decision Support); the "Changes to Existing Medical Software Policies Resulting from Section 3060" guidance (2019)
**Related Final Rules**: 76 FR 8637 (Feb 15, 2011 — MDDS reclassified Class III → Class I); 86 FR 20278 (Apr 19, 2021 — classification regs conformed to Cures Act § 3060)
**Source PDF**: `source/mdds.pdf`; raw text in `source-md/mdds.md`

## Scope

This guidance establishes FDA's regulatory posture for software and hardware products that **transfer, store, convert formats, or display medical device data**. The 2022 update reflects a **fundamental statutory shift** introduced by 21st Century Cures Act § 3060 (Dec 13, 2016): software functions that solely perform the four MDDS actions are **no longer devices** under FD&C Act § 201(h). This is not enforcement discretion — it is a statutory carve-out.

The guidance partitions the space into **two categories**:

1. **Non-Device-MDDS** — *software* functions solely intended to transfer, store, convert formats, or display medical device data and results. Per Cures Act § 3060 / FD&C Act § 520(o)(1)(D), these are **not devices** and not subject to FDA device regulation at all.

2. **Device-MDDS** — *hardware* functions intended to transfer, store, convert formats, or display medical device data. These **remain devices** under § 201(h) (the Cures Act carve-out is software-only), but FDA exercises **enforcement discretion** — does not intend to enforce registration/listing, premarket review, postmarket reporting, or QSR. Includes hardware subject to 21 CFR 880.6310 (MDDS), 21 CFR 892.2010 (medical image storage), and 21 CFR 892.2020 (medical image communications).

The 2022 update also covers **Multiple Function Device Products** containing MDDS — Non-Device-MDDS sub-functions remain unregulated; Device-MDDS sub-functions receive enforcement discretion; FDA may still assess the *impact* of either on the device-function-under-review per the Multiple Function Device guidance.

## Key Requirements

### Section III — Definitions

> **Non-Device-MDDS**: Software functions that are solely intended to transfer, store, convert formats, or display medical device data and results.
>
> **Device-MDDS**: Hardware functions that are solely intended to transfer, store, convert formats, or display medical device data and results.

The split between software and hardware is the load-bearing legal distinction post-Cures-Act.

### Section IV-A — Policy for Non-Device-MDDS

A Non-Device-MDDS is a software function solely intended to provide one or more of the following uses, **without controlling or altering the functions or parameters of any connected medical devices**, which may or may not be intended for active patient monitoring:

- **Electronic transfer or exchange** of medical device data (e.g., software that collects ventilator-output CO2 levels and transmits to a central patient data repository).
- **Electronic storage and retrieval** of medical device data (e.g., software that stores historical blood pressure for later provider review).
- **Electronic conversion** of medical device data from one format to another in accordance with a preset specification (e.g., software that converts pulse oximeter digital data into a printable digital format).
- **Electronic display** of medical device data, including secondary or remote displays that solely display data and results (e.g., software that displays a previously stored ECG for a specific patient).

**Hard limits — software functions that are NOT Non-Device-MDDS:**

- Software that **modifies the data** beyond format conversion.
- Software that **controls the functions or parameters** of any connected medical device.
- Software that **analyzes or interprets** clinical laboratory or other device data and results.
- Software that **generates alarms or alerts** based on the data.
- Software that **prioritizes patient information on multi-patient displays** (typical of active patient monitoring).

These software functions ARE device software functions and remain subject to FDA regulation **unless they meet the criteria outlined in section 520(o)(1)(E) of the FD&C Act** (the CDS carve-out) — per the guidance (source § III).

**The "active patient monitoring" framework.** Software functions are device functions intended for active patient monitoring (and thus NOT Non-Device-MDDS) when:

- The **clinical context** requires a timely response (e.g., in-hospital patient monitoring).
- The **clinical condition** (disease or diagnosis) requires a timely response (e.g., a monitor for life-threatening arrhythmias like ventricular fibrillation; a diabetes device for time-sensitive intervention).

The footnote to this section quotes 76 FR 8637 at 8644 defining "active" as "any device that is intended to be relied upon in deciding to take immediate clinical action." The active-monitoring exclusion is the most common boundary question for MDDS classification.

**Active-patient-monitoring examples (NOT MDDS):**

- A nurse-telemetry station functioning as a secondary alarm system receiving and displaying ICU bedside-monitor information for immediate clinical intervention.
- A device that receives/displays information, alarms, or alerts from a home monitor and alerts a caregiver to take immediate clinical action.

**Non-Device-MDDS examples (in scope):**

- An application transmitting a child's temperature to a parent/guardian while the child is in a school's nurse room.
- An application facilitating remote display of blood glucose meter information for the user's own retrospective review (NOT intended for immediate clinical action).
- Any network-component assemblage that includes specialized software expressly for Non-Device-MDDS functionality.
- Custom software written by entities other than the original device manufacturer (hospitals, providers, third-party vendors) that connects directly to a medical device solely to obtain device information.
- Modified portions of IT infrastructure software created/modified for specific Non-Device-MDDS functionality.

### Section IV-B — Policy for Device-MDDS

Hardware functions that transfer, store, convert formats, or display medical device data remain devices under § 201(h). FDA does not intend to enforce regulatory controls (registration, listing, premarket review, postmarket reporting, QSR) for hardware functions limited to assisting:

- (a) MDDS subject to **21 CFR 880.6310**
- (b) Medical image storage devices subject to **21 CFR 892.2010**
- (c) Medical image communications devices subject to **21 CFR 892.2020**

**§ 880.9 / § 892.9 still apply — but enforcement discretion overrides anyway.** The classification regulations exempt these hardware functions from premarket notification subject to the § 880.9 / § 892.9 limitations. When those limitations would otherwise trigger a 510(k) (e.g., a Device-MDDS that is an in vitro device for assessing cardiovascular disease risk under § 880.9(c)(4), or diabetes management under § 880.9(c)(5)), **FDA still does not intend to enforce compliance** with the regulatory controls.

**Specialized medical display hardware is NOT Device-MDDS.** Hardware displays for digital mammography, radiology, pathology, ophthalmology (e.g., § 892.2050) and other specialized medical display hardware **integral to the safe and effective use of a medical device hardware product** (such as integral 3D displays in robotic surgery systems and displays built into ICU bedside monitors) are NOT Device-MDDS — they are not excluded from the device definition by the Cures Act and remain devices subject to their classification.

**General-purpose IT hardware is also NOT a device at all.** General-purpose hardware IT infrastructure (network routers for data transfer, NAS for storage, PDF software for data conversion, computer monitors for data display) is not a device function — neither the software nor the hardware function meets § 201(h). Not regulated as devices.

### Section IV-C — Multiple Function Device Products that contain MDDS

Per FD&C Act § 520(o)(2):

- FDA **does not regulate** Non-Device-MDDS functions contained in a multiple function device product.
- For Device-MDDS functions in a multiple function device product, FDA **does not, at this time, intend to enforce** regulatory requirements.
- FDA **may still assess the impact** of Non-Device-MDDS and Device-MDDS functions on the safety and effectiveness of the device function-under-review per the Multiple Function Device guidance (`mfd-distilled.md`).

This means a multiple function device product containing MDDS sub-functions does not trigger 510(k) on those MDDS sub-functions, but the impact-analysis framework from the MFD guidance still applies to evaluate how the MDDS sub-functions interact with the device-function-under-review.

## Practical Cross-References

| Question | Look here |
|----------|-----------|
| Is this software an MDDS / non-device? | § III definition + § IV-A active-patient-monitoring exclusion + Cures Act § 3060 / § 520(o)(1)(D) |
| Does my product fall under enforcement discretion as Device-MDDS hardware? | § IV-B — must be hardware limited to the four MDDS actions; specialized medical displays are excluded |
| What if my product is a multiple-function device with an MDDS sub-function? | § IV-C + companion `mfd-distilled.md` for impact-assessment framework |
| Is alarm/alert generation MDDS? | No — § IV-A excludes alarms, alerts, and active-monitoring prioritization explicitly |
| Are general-purpose IT components (routers, NAS, monitors) MDDS? | No — they are not devices at all per § IV-B |
| Does data conversion via AI count as MDDS? | **Not addressed by this guidance** — the 2022 MDDS guidance does not mention AI/ML. The test it gives is whether conversion is "in accordance with a preset specification" (§ IV-A); whether a learned/AI transformation satisfies that is an open question for the program, *not* settled here. (Distiller note, not guidance text.) |

## Historical Context

- **Feb 15, 2011** (76 FR 8637): MDDS reclassified from Class III to Class I (510(k)-exempt). Established the four-verb framework (transfer / store / convert / display) and the active-patient-monitoring exclusion.
- **Feb 9, 2015**: Original MDDS enforcement-discretion guidance issued — framed enforcement discretion for low-risk software in this space.
- **Dec 13, 2016**: Cures Act § 3060 enacted; § 520(o)(1)(D) added to FD&C Act, statutorily carving out software functions solely intended to transfer/store/convert formats/display medical device data — these are no longer devices at all.
- **Sept 27, 2019**: Minor guidance update conforming to Cures Act § 3060.
- **Apr 19, 2021** (86 FR 20278): Final rule conforming classification regulations to Cures Act § 3060.
- **Sept 28, 2022**: This guidance updated to align with 86 FR 20278 — establishes the Non-Device-MDDS vs Device-MDDS framework.

For projects citing the "2015 MDDS guidance" in regulatory strategy, **note that the 2022 update fundamentally reframes the legal basis** — what was enforcement discretion in 2015 is, for software functions, a statutory non-device carve-out post-Cures-Act. The 2022 update is the operative guidance for current submissions.

## Source Provenance

- **Source PDF**: `source/mdds.pdf` (the 2022 update — 9 pages)
- **Source-MD**: `source-md/mdds.md` (raw `pdftotext -layout` extraction)
- **Federal Register notice (original 2015)**: [80 FR 7479 / FR document 2015-02573](https://www.govinfo.gov/content/pkg/FR-2015-02-09/pdf/2015-02573.pdf) — archived as `source/fr-2015-02573-mdds-notice.pdf`
- **Conforming final rule (2021)**: 86 FR 20278 (Apr 19, 2021)
- **Reclassification anchor**: 76 FR 8637 (Feb 15, 2011)
- **Public comments docket**: FDA-2014-D-0798
- **Authoring**: distilled directly from the 2022 guidance PDF text after `pdftotext` extraction (run under the docflow bypass marker convention). PDF placed by the human collaborator after WebFetch was unable to retrieve fda.gov directly.
