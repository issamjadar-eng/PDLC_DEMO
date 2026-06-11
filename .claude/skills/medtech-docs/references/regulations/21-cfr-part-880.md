# 21 CFR Part 880 — General Hospital and Personal Use Devices

**Citation**: 21 CFR Part 880 (Title 21, Chapter I, Subchapter H)
**Authority**: 21 U.S.C. 351, 360, 360c, 360e, 360j, 360l, 371
**Promulgating Agency**: FDA / CDRH
**Status**: Active (current at retrieval date — see Source provenance)
**Source**: eCFR API — `https://www.ecfr.gov/api/versioner/v1/full/<date>/title-21.xml?chapter=I&subchapter=H&part=880`

## Scope

Part 880 classifies general hospital and personal use medical devices. It is the regulatory home of **§ 880.6310 — Medical Device Data System (MDDS)**. Since the **April 19, 2021 conforming final rule (86 FR 20278; this section amended at 86 FR 20283)**, § 880.6310 covers **hardware devices only**: software that solely transfers, stores, converts per a preset specification, or displays medical-device data is **not a device at all** under the Cures Act § 3060 carve-out (FD&C Act § 520(o)(1)(D)) and therefore has no classification regulation. § 880.6310 was originally **reclassified from Class III to Class I (510(k)-exempt)** in 2011 (76 FR 8637); the operative FDA guidance is the **September 2022 MDDS guidance update** (`../fda-guidance/mdds-distilled.md`), which establishes the Non-Device-MDDS (software) vs Device-MDDS (hardware) framework.

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
| § 880.6310 | Medical device data system (MDDS) — **hardware only since 86 FR 20283 (2021)** | I | **Exempt** (subject to § 880.9) |
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

#### Verbatim — § 880.6310(a) Identification (current text, as amended by 86 FR 20283, Apr 19, 2021)

> A medical device data system (MDDS) is a **hardware device** that is intended to provide one or more of the following uses, without controlling or altering the functions or parameters of any connected medical devices:
>
> **(1)** The electronic transfer of medical device data;
>
> **(2)** The electronic storage of medical device data;
>
> **(3)** The electronic conversion of medical device data from one format to another format in accordance with a preset specification; or
>
> **(4)** The electronic display of medical device data.
>
> An MDDS may include electronic or electrical hardware such as a physical communications medium (including wireless hardware), modems, and interfaces. An MDDS is not intended to be used in connection with active patient monitoring.

(Emphasis added on "hardware device". Lead-in sentence, paragraph (b), and amendment citation confirmed verbatim against the live eCFR API 2026-06-11; subparagraph wording transcribed via machine-assisted retrieval — [VERIFY subparagraph punctuation against eCFR before quoting in a submission].)

**Amendment history (load-bearing).** The original 2011 text defined MDDS as "a hardware **or software** product" with a software subparagraph (a)(1) ("Software that uses an off-the-shelf computer hardware to perform..."). The **April 19, 2021 conforming final rule (86 FR 20278; § 880.6310 amended at 86 FR 20283)** removed software from the identification to conform to **Cures Act § 3060** (FD&C Act § 520(o)(1)(D)), under which software performing solely these MDDS functions is **not a device**. Any document quoting the "hardware or software product" text is citing the pre-2021 regulation.

#### Verbatim — § 880.6310(b) Classification

> Class I (general controls). The device is exempt from the premarket notification procedures in subpart E of part 807 of this chapter, subject to the limitations in § 880.9.

#### Practical notes (post-Cures framing — aligned with `../fda-guidance/mdds-distilled.md`)

- **Two distinct outcomes for "MDDS-type" functions** (per the 2022 MDDS guidance):
  - **Software** performing solely transfer/store/convert-per-preset-spec/display → **Non-Device-MDDS** — statutorily **not a device** (§ 520(o)(1)(D)). No classification regulation applies, including this one. There is nothing to "exempt" — it is outside FDA device jurisdiction.
  - **Hardware** performing those functions → **Device-MDDS** under § 880.6310 — still a device (the Cures carve-out is software-only): Class I, 510(k)-exempt subject to § 880.9, and additionally under FDA **enforcement discretion** (FDA does not intend to enforce registration/listing, premarket review, postmarket reporting, or QSR).
- **Do not classify software under § 880.6310.** A common stale framing ("our DICOM-ingestion software is Class I exempt MDDS under 880.6310") is wrong post-2021: software that ingests and stores DICOM images, converts device-data formats per a preset specification, or displays device data without analysis is **not a device**, not a Class-I-exempt device. The § 880.9 analysis is moot for such software; it matters only for hardware Device-MDDS.
- **Qualification is processing-bound first.** Whether software OR hardware, a function qualifies as MDDS-type only if it does *solely* transfer/store/convert/display with no analysis, interpretation, or calculation beyond format conversion. If it processes, it is a device function regardless of the software/hardware split. See the 2022 guidance § IV-A (`../fda-guidance/mdds-distilled.md`).
- **The "active patient monitoring" exclusion is load-bearing.** A product intended for active patient monitoring is **not** an MDDS (hardware case) and not Non-Device-MDDS (software case) — it falls under the relevant monitoring-device classification (e.g., § 880.2400 bed-patient monitor; § 870.2300 cardiac monitor). The active-monitoring exclusion is the most common boundary question for MDDS qualification.
- **§ 880.9 applies to hardware Device-MDDS.** Class I exempt status under § 880.6310 is **subject to the limitations in § 880.9**. Hardware MDDS that crosses a § 880.9 trigger (different intended use, different fundamental technology, IVD-specific category) loses its exempt status and must submit a 510(k).
- **Guidance lineage.** Feb 2015 MDDS guidance (FR notice 2015-02573) established the original enforcement-discretion posture; updated Sept 27, 2019; the **Sept 28, 2022 update is operative** — it aligns the guidance with 86 FR 20278 and the Non-Device-MDDS / Device-MDDS framework. See `../fda-guidance/mdds-distilled.md`.

### § 880.6315 — Remote medication management system

(Adjacent classification; not MDDS. Class II, 510(k)-required. Manages medication-administration data flow with active patient-management implications, distinguishing it from the passive MDDS scope.)

## Practical Cross-References

| Question | Look here |
|----------|-----------|
| Is this *software* an MDDS-type function? | Four-verb qualification test (transfer/store/convert-per-preset-spec/display, no processing) per the 2022 guidance § IV-A — if yes, it is **Non-Device-MDDS, not a device**; § 880.6310 does not apply. See `../fda-guidance/mdds-distilled.md` |
| Is this *hardware* an MDDS? | § 880.6310(a) four-verb test + active-monitoring exclusion → Device-MDDS, Class I exempt subject to § 880.9, plus enforcement discretion |
| Can I claim MDDS-exempt status without a 510(k)? | Hardware only: § 880.6310(b) + § 880.9 non-applicability analysis. Software: nothing to claim — not a device (§ 520(o)(1)(D)) |
| Does MDDS interact with Multiple Function Device framework? | Yes — a Non-Device-MDDS software function inside a multi-function product is an "other function" assessed under the MFD framework; see `../fda-guidance/mfd-distilled.md` |
| What if my hardware device crosses § 880.9? | Submit a 510(k). The 510(k) compares against a predicate device. |

## Source Provenance

- **eCFR API endpoint**: `https://www.ecfr.gov/api/versioner/v1/full/<date>/title-21.xml?chapter=I&subchapter=H&part=880` (note: the human-viewer URLs at `ecfr.gov/current/...` redirect automated fetchers to `unblock.federalregister.gov`; use the API endpoint)
- **Retrieval date**: 2026-06-11 (§ 880.6310 re-pulled from live eCFR API after an audit found the prior version quoted the pre-2021 text)
- **Section source citation (from eCFR)**: 76 FR 8649, Feb. 15, 2011, as amended at **86 FR 20283, Apr. 19, 2021**
- **Companion FDA guidance**: `../fda-guidance/mdds-distilled.md` (2015 guidance, updated 2019 and Sept 28, 2022 — the 2022 update is operative)
- **Reclassification anchor**: 76 FR 8637 (Feb 15, 2011) — Class III → Class I exempt; **Cures conforming amendment**: 86 FR 20278 (Apr 19, 2021) — software removed from the identification
- **Authoring**: distilled from eCFR-returned content via a `citations` audit that surfaced this section as a `registry-gap`; § 880.6310 corrected to the post-2021 text on 2026-06-11.

[VERIFY all clause numbers and verbatim text against the live eCFR snapshot before relying on this distillation in a regulated submission. § 880.9 quoted text retains its 2026-05-29 retrieval basis.]
