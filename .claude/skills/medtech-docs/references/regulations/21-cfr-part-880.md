# 21 CFR Part 880 — General Hospital and Personal Use Devices

**Citation**: 21 CFR Part 880 (Title 21, Chapter I, Subchapter H)
**Authority**: 21 U.S.C. 351, 360, 360c, 360e, 360j, 360l, 371
**Promulgating Agency**: FDA / CDRH
**Status**: Active (current at retrieval date — see Source provenance)
**Source**: eCFR API — `https://www.ecfr.gov/api/versioner/v1/full/<date>/title-21.xml?chapter=I&subchapter=H&part=880`

## Scope

Part 880 classifies general hospital and personal use medical devices. It is the regulatory home of **§ 880.6310 — Medical Device Data System (MDDS)**, the foundational regulation for software that transfers, stores, converts, or displays medical-device data without controlling or altering connected devices. § 880.6310 was **reclassified from Class III to Class I (510(k)-exempt)** in 2011, and the 2015 FDA MDDS guidance (`../fda-guidance/mdds-distilled.md`) clarified the agency's enforcement posture for MDDS, image-storage, and image-communications devices.

Part 880 contains Subparts A–G:

| Subpart | Title |
|---------|-------|
| A | General Provisions |
| B | [Reserved] |
| C | General Hospital and Personal Use Monitoring Devices |
| D–E | [Reserved] |
| F | General Hospital and Personal Use Therapeutic Devices |
| G | General Hospital and Personal Use Miscellaneous Devices |

This distillation focuses on **Subpart A § 880.9** (the exemption-limitation framework) and **Subpart G § 880.6310** (MDDS).

## Section Index — Sections Relevant to SaMD / Data-Movement Devices

| Section | Title | Class | 510(k)? |
|---------|-------|-------|---------|
| § 880.1 | Scope | n/a | n/a |
| § 880.9 | Limitations of exemptions from section 510(k) | n/a | n/a — limitation framework |
| § 880.6300 | Implantable radiofrequency transponder system | III | Required |
| § 880.6310 | Medical device data system (MDDS) | I | **Exempt** (subject to § 880.9) |
| § 880.6315 | Remote medication management system | II | Required |

## Subpart A — General Provisions

### § 880.9 — Limitations of exemptions from section 510(k)

> The exemption from the requirement of premarket notification (510(k)) for a generic type of device is only to the extent that the device has existing or reasonably foreseeable characteristics of commercially distributed devices within that generic type or, in the case of in vitro diagnostic devices, only to the extent that misdiagnosis as a result of using the device would not be associated with high morbidity or mortality. Accordingly, manufacturers of any commercially distributed device for which FDA has granted an exemption from the requirement of premarket notification must still submit a premarket notification to FDA before introducing or delivering for introduction into interstate commerce for commercial distribution the device when:
>
> **(a)** The device is intended for a use different from the intended use of a legally marketed device in that generic type of device; e.g., the device is intended for a different medical purpose, or the device is intended for lay use where the former intended use was by health care professionals only;
>
> **(b)** The modified device operates using a different fundamental scientific technology than a legally marketed device in that generic type of device; e.g., a surgical instrument cuts tissue with a laser beam rather than with a sharpened metal blade, or an in vitro diagnostic device detects or identifies infectious agents by using deoxyribonucleic or ribonucleic acid hybridization or amplification rather than culture or immunoassay techniques; or
>
> **(c)** The device is an in vitro device that is intended:
> > (1) For use in the diagnosis, monitoring, or screening of neoplastic diseases with the exception of immunohistochemical devices;
> > (2) For use in screening or diagnosis of familial or acquired genetic disorders, including inborn errors of metabolism;
> > (3) For measuring an analyte that serves as a surrogate marker for screening, diagnosis, or monitoring life-threatening diseases such as acquired immune deficiency syndrome (AIDS), chronic or active hepatitis, tuberculosis, or myocardial infarction or to monitor therapy;
> > (4) For assessing the risk of cardiovascular diseases;
> > (5) For use in diabetes management;
> > (6) For identifying or inferring the identity of a microorganism directly from clinical material;
> > (7) For detection of antibodies to microorganisms other than immunoglobulin G (IgG) or IgG assays when the results are not qualitative, or are used to determine immunity, or when the assay is intended for use in matrices other than serum or plasma;
> > (8) For noninvasive testing as defined in § 812.3(k) of this chapter; and
> > (9) Near patient testing (point of care).

**Why this matters.** § 880.9 is the **exemption-limitation framework** that governs whether a 510(k)-exempt device (including MDDS under § 880.6310) loses its exempt status. A device claimed as MDDS-exempt that crosses any § 880.9 trigger — different intended use, different fundamental technology, or one of the IVD-specific categories — must submit a 510(k) before commercial distribution. **A project documenting an MDDS-exempt classification must explicitly establish non-applicability of § 880.9.**

The same pattern appears in other 800-series parts: § 892.9 for radiology, § 882.9 for neurological, § 870.9 for cardiovascular, etc. — every "§ 9" section instantiates this framework.

## Subpart G — Miscellaneous Devices

### § 880.6310 — Medical device data system (MDDS)

#### Verbatim — § 880.6310(a) Identification

> A medical device data system (MDDS) is a hardware or software product that transfers, stores, converts according to preset specifications, or displays medical device data, without controlling or altering the function or parameters of any connected medical device. An MDDS may include:
>
> **(1)** Software that uses an off-the-shelf computer hardware to perform one or more of the following functions, without controlling or altering the functions or parameters of any connected medical device:
> > (i) The electronic transfer of medical device data;
> > (ii) The electronic storage of medical device data;
> > (iii) The electronic conversion of medical device data from one format to another format in accordance with a preset specification;
> > (iv) The electronic display of medical device data.
>
> **(2)** Electronic or electrical hardware such as a physical communications medium (including wireless hardware), modems, interfaces, and a communications protocol that performs one or more of the four functions identified in paragraph (a)(1) of this section.
>
> An MDDS does not include devices intended to be used in connection with active patient monitoring.

#### Verbatim — § 880.6310(b) Classification

> Class I (general controls). The device is exempt from the premarket notification procedures in subpart E of part 807 of this chapter subject to the limitations in § 880.9.

#### Practical notes

- **Reclassification history.** § 880.6310 was finalized at **76 FR 8637 (Feb 15, 2011)** reclassifying MDDS from Class III to Class I (510(k)-exempt). The 2011 final rule established the four-verb scope: **transfer / store / convert / display**. Any device intended for any of these four uses (and only those uses) without controlling or altering connected medical devices qualifies as MDDS.
- **The "active patient monitoring" exclusion is load-bearing.** A device that transfers, stores, converts, or displays medical device data BUT is intended for active patient monitoring is **not** an MDDS — it falls under the relevant monitoring-device classification (e.g., § 880.2400 bed-patient monitor; § 870.2300 cardiac monitor). The active-monitoring exclusion is the most common boundary question for MDDS classification.
- **§ 880.9 still applies.** Class I exempt status under § 880.6310 is **subject to the limitations in § 880.9**. A device that meets § 880.6310's identification but crosses a § 880.9 trigger (different intended use, different fundamental technology, IVD-specific category) loses its exempt status and must submit a 510(k).
- **Enforcement discretion overlay.** FDA's Feb 2015 MDDS guidance (Federal Register notice 2015-02573) announced that the agency does not intend to enforce compliance with the regulatory requirements for MDDS for "low-risk" data-movement products. The guidance does not change the classification (still Class I exempt); it adds an enforcement-discretion layer for the manufacturer's compliance posture. See `../fda-guidance/mdds-distilled.md`.
- **What's IN scope as MDDS.** Software that ingests DICOM images and stores them; software that converts proprietary device-data formats to HL7 FHIR; software that displays multi-device data on a dashboard without alarming or alerting; the hardware modems/interfaces that carry the data.
- **What's OUT of scope (not MDDS).** Software that alerts on physiological thresholds (active monitoring → not MDDS); software that controls device parameters (not MDDS — likely PACS or device-specific classification); software that interprets device data to deliver a clinical recommendation (CDS or higher-risk SaMD, not MDDS).

### § 880.6315 — Remote medication management system

(Adjacent classification; not MDDS. Class II, 510(k)-required. Manages medication-administration data flow with active patient-management implications, distinguishing it from the passive MDDS scope.)

## Practical Cross-References

| Question | Look here |
|----------|-----------|
| Is this software an MDDS or something more? | § 880.6310(a) four-verb test (transfer/store/convert/display) + active-monitoring exclusion + § 880.9 limitations |
| Can I claim MDDS-exempt status without a 510(k)? | § 880.6310(b) + § 880.9 non-applicability analysis + Feb 2015 enforcement-discretion overlay (`../fda-guidance/mdds-distilled.md`) |
| Does MDDS interact with Multiple Function Device framework? | Yes — MDDS-functioning sub-modules in a larger device-function product fall under MFD scope; see `../fda-guidance/mfd-distilled.md` |
| What if my device crosses § 880.9? | Submit a 510(k). The 510(k) compares against a predicate device. |

## Source Provenance

- **eCFR API endpoint**: `https://www.ecfr.gov/api/versioner/v1/full/<date>/title-21.xml?chapter=I&subchapter=H&part=880`
- **Retrieval date**: 2026-05-29
- **eCFR raw XML**: archived under `source/21-cfr-part-880.xml` (when present)
- **Companion FDA guidance**: `../fda-guidance/mdds-distilled.md` (Feb 2015 enforcement-discretion guidance)
- **Reclassification anchor**: 76 FR 8637 (Feb 15, 2011) — Class III → Class I exempt
- **Authoring**: distilled from eCFR-returned content via a `citations` audit that surfaced this section as a `registry-gap`.

[VERIFY all clause numbers and verbatim text against the live eCFR snapshot before relying on this distillation in a regulated submission.]
