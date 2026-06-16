# FDA Guidance (DRAFT): Electronic Submission Template for Medical Device Q-Submissions

🔎 **Finding aid — NOT the authoritative source.** Distilled summary for quick orientation and early analysis. Ground and cite the authoritative full text [`source-md/qsub-estar-draft.md`](source-md/qsub-estar-draft.md); verify any quote against the byte-correct `source/` PDF before treating it as verbatim. This paraphrases and omits (appendices/worked examples are routinely dropped) — a section's absence here is never evidence the source is silent.

**Full Title**: Electronic Submission Template for Medical Device Q-Submissions: Draft Guidance for Industry and Food and Drug Administration Staff
**Document Date**: May 29, 2025 (Draft — Not for Implementation)
**Status**: **DRAFT** (Contains Nonbinding Recommendations; when final, will contain **both binding and nonbinding provisions** per § 745A(b)(3))
**Comment Deadline**: July 28, 2025 (60 days from Federal Register notice)
**Source PDF**: `source/qsub-estar-draft.pdf` (raw text in `source-md/qsub-estar-draft.md`)
**CDRH Document Number**: GUI00007041
**FR Notice (Availability)**: FR Doc 2025-09615 — `source/qsub-fr-2025-09615.pdf` — 90 FR 22742+ (Vol. 90, No. 102, Thursday May 29, 2025); Docket **FDA-2025-D-1082**
**Issuing Bodies**: CDRH + CBER
**Statutory Basis**: FD&C Act § 745A(b) (electronic submission mandate, added by FDARA § 207, 2017); 21 CFR 10.115(d) (binding-guidance exception when carrying out § 745A(b)(3))
**Companion Final Guidance**: `qsub-distilled.md` (Q-Submission Program, May 29, 2025) — defines the Q-Sub types and Pre-Sub content; THIS guidance defines the *electronic format* for those submissions
**Companion Parent Guidance**: 745A(b) device parent guidance ("Providing Regulatory Submissions for Medical Devices in Electronic Format — Submissions Under Section 745A(b)")

## Scope

This **draft** guidance establishes the technical standards for preparing and submitting **electronic submissions of Q-Subs** under FDA's mandate in FD&C Act § 745A(b)(3). When finalized, it specifies:

- The **standards** for electronic Q-Sub submissions (eSTAR template format).
- The **timetable** for implementation (one-year transition period from final-guidance issuance before electronic submissions become required).
- The **criteria for waivers and exemptions** from electronic-submission requirements.

**Currently in scope**: **Pre-Submissions (Pre-Subs)** only — the only Q-Sub type for which eSTAR is currently available. Other Q-Sub types (SIRs, Study Risk Determinations, Informational Meetings, PMA Day 100 Meetings) will be added in future versions of this guidance.

**Why this guidance is unusual**: Per § 745A(b)(3), portions of this guidance that establish "standards," "timetables," or "criteria for waivers and exemptions" will carry **binding effect** when final (not just current FDA thinking). This is one of the few FDA guidances that becomes partially binding. Other provisions remain nonbinding.

## Key Terminology

| Term | Definition |
|------|-----------|
| **eCopy** | Electronic duplicate of a paper submission per 84 FR 68334 / eCopy guidance. **NOT** an electronic submission per § 745A(b)(3). |
| **Electronic Submission (eSubmission)** | The submission package produced by an electronic submission template that contains the data of a "complete" submission. The target state under § 745A(b)(3). |
| **eSTAR (electronic Submission Template And Resource)** | An electronic submission template built within a structured dynamic PDF that guides a user through eSubmission construction. The **only** electronic submission template currently available for Q-Subs. |
| **PreSTAR** | The current eSTAR variant covering Pre-Subs and 513(g) requests; will expand to other submission types in future versions. |
| **Electronic submission template** | A guided submission-preparation tool walking industry through relevant content/components — improves consistency, quality, and review-process efficiency. |
| **Structured data** | Data captured in fields, dropdowns, checkboxes within the template. |
| **Unstructured data** | Data submitted as attachments to the template. |

## Current eSTAR Template Structure (Pre-Subs)

The current Pre-Sub eSTAR template includes the following high-level sections (per § V Table 1):

| Section | Content |
|---|---|
| **Submission Type** | Identification of key initial-processing information (Form FDA 3514 Section A content) |
| **Cover Letter / Letters of Reference** | Cover letter + references to other submissions |
| **Applicant Information** | Applicant + correspondent info (Form FDA 3514 Sections B/C content) |
| **Pre-Submission Correspondence & Previous Regulator Interaction** | Prior NSE determinations, deleted/withdrawn 510(k)s, prior Q-Subs, IDE/PMA/HDE/De Novo, 513(g)s, EUAs |
| **Consensus Standards** | Voluntary consensus standards used (FDA-recognized or not) |
| **Submission Characteristics** | Overall purpose + intended-submission type + Q-Sub question topic categories. **Meeting info if applicable**: type, length, ≥ 3 preferred dates/times, draft agenda with time per item, planned attendees + positions, non-US-citizen identification, requested FDA staff |
| **Product Description** | Listing number; tech characteristics (materials, design, energy source, features); principle of operation; conditions of use (surgical technique, anatomic location, UI, device-device interaction, device-patient interaction); accessory marketing; RFD number if any |
| **Device Uses / Proposed Indications for Use** | Disease/condition + patient population the device will diagnose/treat/prevent/cure/mitigate |
| **Classification** | Proposed classification regulation number (21 CFR 807.87(c)) |
| **Labeling** | Proposed labeling — device label, IFU, patient labeling per Patient Labeling guidance |
| **References** | Literature references |
| **Pre-Submission Questions** (Pre-Subs only) | Questions tied to review topics named in Submission Characteristics; supporting docs |

When finalized, **this Table 1 will REPLACE Appendix 1 (Pre-Sub Acceptance Checklist)** of `qsub-distilled.md` — the structural compatibility is intentional. The eSTAR template embeds the acceptance checklist.

## Technical Screening (Replaces RTA for eSTAR)

eSTAR submissions are **not anticipated to undergo RTA** because the template structurally enforces completeness. Instead, FDA conducts:

- **Virus scanning** + **technical screening** — verifies the eSTAR responses accurately describe the device and that every applicable attachment-type question has at least one attachment.
- Performed within **15 calendar days** of FDA receiving the Pre-Sub eSTAR.
- If the Pre-Sub eSTAR fails technical screening: FDA notifies submitter via email naming the incomplete information; Pre-Sub goes **on hold** until updated.
- Updated eSTAR submitted within **180 days** of deficiency notification → logged as an Amendment; otherwise FDA considers the Pre-Sub withdrawn and closed in the system.
- Once technical screening passes, review-clock continues for substantive review.

This replaces the Day-15 RTA process described in `qsub-distilled.md` for eSTAR submissions specifically.

## Exemptions From Electronic Submission Requirements

Per § VI.A, the following Pre-Subs/information will be **exempt** from electronic submission requirements when this guidance is finalized:

- **Interactive review responses** — when reviewer used phone/email interactive review, submitter replies via email (not eSTAR).
- **Amendments of these types** (remain subject to eCopy requirements):
  - Appeals / requests for supervisory review.
  - Change in correspondent / change of legal entity.
  - Amendments after decision.
  - Meeting minutes.
  - Meeting-minutes disagreements.
  - Presentation slides.
  - Withdrawal requests.

Other responses to FDA additional-information requests **must** be submitted as eSTAR Amendments via the "Amendment/Additional Information (AI) Response" template category.

## Waivers — None Granted

> "FDA has not identified any particular circumstances appropriate for a waiver of the Pre-Sub electronic submission requirements and does not intend to grant requests for waiver."

Rationale: eSTAR PDF is freely downloadable from FDA's website; all submitters should have the ability to provide a Pre-Sub eSTAR.

## Timing — When Electronic Submissions Will Be Required

- **Current state** (May 2025, pre-finalization): eSTAR for Pre-Subs is **voluntary**; eCopy remains permitted.
- **Transition period**: a minimum **one-year transition** from final-guidance issuance.
- **Required state**: after the transition period, **all Pre-Subs** (Originals, Supplements, Amendments) **must** be submitted as eSTAR eSubmissions, unless covered by an exemption (§ VI.A).

Pre-Subs not provided as electronic submissions after the implementation date **will not be received**.

## Submission Mechanics

| Center | Portal | Support Email |
|---|---|---|
| **CDRH** | FDA CDRH Portal (or mail to CDRH Document Control Center for known technical-blocker cases) | `OPEQSubmissionSupport@fda.hhs.gov` |
| **CBER** | Electronic Submissions Gateway (per CBER eSubmission guidance) | `ESUBPREP@fda.hhs.gov` |

## Cross-References

- **Q-Sub Program**: `qsub-distilled.md` — defines Pre-Sub content, the 5 Q-Sub types, MDUFA timelines. THIS draft guidance defines the *electronic format* for those submissions.
- **eCopy Program**: FDA "eCopy Program for Medical Device Submissions" guidance (84 FR 68334) — current submission format; will be superseded for Pre-Subs after this guidance finalizes.
- **745A(b) device parent guidance**: "Providing Regulatory Submissions for Medical Devices in Electronic Format — Submissions Under Section 745A(b) of the FD&C Act" — overall electronic-submission framework.
- **MDUFA IV Commitment Letter**: https://www.fda.gov/media/102699/download — established eSTAR development commitment.
- **MDUFA V Commitment Letter**: https://www.fda.gov/media/158308/download — affirmed continued eSTAR development.
- **eSTAR Voluntary Program**: https://www.fda.gov/medical-devices/how-study-and-market-your-device/voluntary-estar-program
- **CDRH Portal**: https://www.fda.gov/medical-devices/industry-medical-devices/send-and-track-medical-device-premarket-submissions-online-cdrh-portal

## Historical Context

- **2017**: FDARA § 207 added § 745A(b) to FD&C Act, mandating electronic format for premarket submissions; MDUFA IV Commitment Letter promised eSTAR development by FY 2020.
- **Feb 27, 2020**: eSTAR Pilot Program launched (85 FR 11371).
- **2022**: MDUFA V Commitment Letter reaffirmed eSTAR expansion commitment.
- **May 29, 2025**: This draft guidance issued + Federal Register notice of availability (FR Doc 2025-09615).
- **Jul 28, 2025**: Public comment deadline.
- **Expected finalization**: per § 745A(b)(3)(B), not later than 1 year after close of public comment period.
- **Earliest required state**: 1 year after final guidance issuance.

## Source Provenance

- **Source PDF**: `source/qsub-estar-draft.pdf` (CDRH document number GUI00007041)
- **Source-MD**: `source-md/qsub-estar-draft.md` (raw `pdftotext -layout` extraction)
- **Companion FR notice**: `source/qsub-fr-2025-09615.pdf` (FR Doc 2025-09615 announcing availability)
- **Comments docket**: FDA-2025-D-1082 (via regulations.gov)
- **Authoring**: distilled directly from the draft guidance PDF text after `pdftotext` extraction (run under docflow bypass-marker convention).

[VERIFY content remains current — this guidance is a draft and may change materially between publication and finalization. Re-distill when FDA issues the final version.]
