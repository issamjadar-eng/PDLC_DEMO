# FDA Guidance — Electronic Submission Template for Medical Device 510(k) Submissions

🔎 **Finding aid — NOT the authoritative source.** Distilled summary for quick orientation and early analysis. Ground and cite the authoritative full text [`source-md/510k-estar.md`](source-md/510k-estar.md); verify any quote against the byte-correct `source/` PDF before treating it as verbatim. This paraphrases and omits (appendices/worked examples are routinely dropped) — a section's absence here is never evidence the source is silent.

**Full Title**: Electronic Submission Template for Medical Device 510(k) Submissions — Guidance for Industry and Food and Drug Administration Staff
**Document Date**: October 2, 2023 (originally issued September 22, 2022)
**Status**: **Final — partially binding.** Insofar as it provides "standards," "timetable," or "criteria for waivers and exemptions" under FD&C Act § 745A(b)(3), it has binding effect (exempt from the usual 21 CFR 10.115(d) nonbinding-guidance restriction); other provisions are nonbinding recommendations
**PDF Source**: `source/510k-estar.pdf` (full text: [`source-md/510k-estar.md`](source-md/510k-estar.md))
**Document Number**: GUI00019006; Docket FDA-2021-D-0872
**Issuing Bodies**: CDRH, CBER
**Statutory Basis**: FD&C Act § 745A(b), added by FDARA § 207 (2017)
**Parent Guidance**: "Providing Regulatory Submissions for Medical Devices in Electronic Format — Submissions Under Section 745A(b) of the FD&C Act" (the 745A(b) device parent guidance)
**Sibling (Q-Subs)**: [`qsub-estar-draft-distilled.md`](qsub-estar-draft-distilled.md) — see "This Guidance vs the Q-Sub eSTAR Draft" below

## Scope

This guidance operationalizes the **§ 745A(b) electronic-submission mandate for 510(k)s**: it establishes the electronic format (the **eSTAR** template), the **timetable** (required since **October 1, 2023**), and the **waiver/exemption criteria**. It deliberately does *not* specify the eSTAR user interface or detailed content — FDA revises the template itself as policies change, outside the guidance-revision cycle. It also does not change *what* a complete 510(k) must contain (21 CFR 807.87–807.100 still govern content); it changes *how* that content is packaged and transmitted.

**Key-question TL;DR**: Since October 1, 2023, **every 510(k) — Traditional, Special, and Abbreviated originals, plus Supplements and Amendments (including add-to-files and appeals)** — must be prepared as an **eSTAR** (a structured dynamic PDF with guided prompts) and transmitted via the **CDRH Portal** (or ESG for CBER), unless a narrow exemption applies. **No waivers are granted.** A 510(k) not provided as an electronic submission **will not be received**. In exchange, eSTAR submissions are **not anticipated to undergo RTA** — the template structurally enforces completeness ("eSTAR Complete" status) — replaced by a lighter **technical screening** within 15 days.

## The § 745A(b) Mandate — How This Guidance Binds

- FDARA § 207 (2017) added FD&C Act § 745A(b): pre-submissions and submissions under §§ 510(k), 513(f)(2)(A), 515(c)/(d)/(f), 520(g), 520(m), 564 (and PHS Act § 351), plus supplements and appeals, **must be submitted in electronic format specified by FDA**, beginning on dates FDA sets in final guidance.
- Congress explicitly authorized FDA to impose the requirement *via guidance* — so where this document uses *must*/*required* for standards, timetable, or waiver/exemption criteria, those provisions are **legally binding**, an unusual property for an FDA guidance.
- The 745A(b) device parent guidance defines the framework; per-submission-type guidances (this one for 510(k)s; a draft sibling for Q-Subs) supply formats and dates.
- Lineage: eSubmitter pilot ("Quality in 510(k) Review Program," Sept 2018 – May 30, 2021) → **eSTAR pilot** (CDRH Feb 2020; CBER June 2022) → mandatory (Oct 1, 2023). MDUFA IV commitment letter drove the template program.

## Significant Terminology

| Term | Definition |
|---|---|
| **eCopy** | Electronic duplicate of the old paper submission. **NOT** an electronic submission — does not satisfy the mandate (but some exempted amendment types still ride eCopy). |
| **Electronic Submission (eSubmission)** | The package produced by an electronic submission template containing the data of a "complete" submission. |
| **eSTAR** | electronic Submission Template And Resource — a structured **dynamic PDF** (Adobe Acrobat Pro-based) that guides construction of the eSubmission. The **only** template currently available for 510(k)s. |
| **Structured data** | Content captured in template fields, dropdowns, checkboxes. |
| **Unstructured data** | Content submitted as **attachments** to the template (documents, PDFs, images, videos). |

## eSTAR Characteristics (§ V)

- Highly automated: form construction, autofilling, automatic verification; integrated FDA databases (product codes, recognized consensus standards); embedded links to regulations/guidances; free.
- Content and logic **fully mirror the internal "SMART" review memo templates used by CDRH reviewers** — the submission is structured the way the reviewer reads it.
- Supports Supplements and certain Amendments; images and hyperlinks; comments may be added to the flattened PDF during preparation.
- Attachments are prompted **conditionally**: affirmative answers trigger attachment-type questions (e.g., indicating clinical testing prompts for clinical reports + financial certifications). Attachments appear under the applicable bookmark of the eSTAR PDF.

### RTA Interaction — Technical Screening Replaces RTA

- eSTAR submissions are **not anticipated to undergo the refuse-to-accept (RTA) process**: the CDRH Portal automatically verifies the eSTAR is complete before acceptance.
- Instead: **virus scan + technical screening** — verifies (1) responses accurately describe the device (e.g., "no tissue-contacting components" is actually true) and (2) **at least one relevant attachment exists per applicable attachment-type question** (e.g., a Software Description attachment where software applies).
- Timeline: screening anticipated **within 15 days** of receipt; begins only after the **user fee is paid**.
- Failure: FDA emails the submitter identifying the incomplete information; the 510(k) goes **on hold** until a complete **replacement eSTAR** is submitted. No replacement within **180 days** → 510(k) considered **withdrawn** and closed.
- Screening time does **not** consume the review clock; for a passing submission, **the review clock starts on the day FDA received it** (retroactive to receipt date).

## eSTAR Structure (§ V.A, Table 1)

Sections of the current 510(k) eSTAR template, with the content each collects:

| eSTAR Section | Content |
|---|---|
| Submission Type | Initial-processing info (Form FDA 3514 § A content) |
| Cover Letter / Letters of Reference | Cover letter + documents referring to other submissions |
| Applicant Information | Applicant + correspondent (Form FDA 3514 §§ B–C content) |
| Pre-Submission Correspondence & Previous Regulator Interaction | Prior NSE determinations, deleted/withdrawn 510(k)s, Q-Subs, IDE/PMA/HDE/De Novo numbers for the same device |
| Consensus Standards | Voluntary consensus standards used — FDA-recognized **and** non-recognized |
| Device Description | Listing number; technological characteristics (materials, design, energy source, features per § 513(i)(1)(B), 21 CFR 807.100(b)(2)(ii)(A)); principle of operation; conditions of use (surgical technique, anatomical location, **user interface**, device-device and device-patient interaction); accessories; applicable device-specific guidances/special controls/performance standards |
| Proposed Indications for Use (Form FDA 3881) | Disease/condition diagnosed/treated/prevented/cured/mitigated + patient population (21 CFR 814.20(b)(3)(i) definition applied to 510(k)s) |
| Classification | Most-appropriate classification regulation number (21 CFR 807.87(c)) |
| Predicates and Substantial Equivalence | Predicate identification (K/DEN/reclassified PMA number, etc.); predicate-vs-subject comparison + why differences don't impact safety/effectiveness; reference devices if applicable |
| Design/Special Controls, Risks to Health, and Mitigation Measures | **Special 510(k)s only** — changes, risk analysis method(s) + results, risk control measures |
| Labeling | Proposed labeling per 21 CFR 807.87(e) (label, IFU, patient labeling; 21 CFR 809.10 for IVDs) |
| Reprocessing | Reprocessing validation + labeling, if applicable |
| Sterility | Sterility + validation methods, if applicable |
| Shelf Life | Methods establishing performance over the proposed shelf life, if applicable |
| Biocompatibility | Biocompatibility assessment of patient-contacting materials, if applicable |
| Software/Firmware | Applicable software documentation per FDA's premarket software guidance |
| Cybersecurity/Interoperability | Cybersecurity assessment + interoperability considerations, if applicable |
| EMC, Electrical, Mechanical, Wireless and Thermal Safety | Testing **or a summary of why testing is not needed** |
| Performance Testing | Non-IVD: non-clinical and clinical test reports relied on for SE. IVD: analytical performance, comparison studies, reference ranges, clinical study info |
| References | Literature references, if applicable |
| Administrative Documentation | Executive summary (recommended), Truthful and Accuracy Statement (21 CFR 807.87(l)), 510(k) Summary (21 CFR 807.92) or Statement (21 CFR 807.93) |
| Amendment/Additional Information (AI) response | Responses to AI requests — but the *changed content itself* goes into the respective eSTAR section (e.g., updated labeling into Labeling), not the AI section |

## Waivers, Exemptions, and Timing (§ VI)

**Who must use eSTAR**: ALL 510(k) submissions — original **Traditional, Special, and Abbreviated** 510(k)s, and subsequent **Supplements and Amendments** (add-to-files, appeals), and any other subsequent submission to an original — unless exempted. Non-electronic 510(k)s **will not be received**.

**Exemptions** (§ VI.A — these remain on email/eCopy channels):

- **Interactive review responses** — reply by email to the reviewer (formal AI responses still go through eSTAR);
- **Amendments**: appeals/requests for supervisory review; substantive summary requests; change-in-correspondent amendments; amendments after final decision (add-to-files);
- **Withdrawal requests** (email or CDRH Portal recommended).

**Waivers**: **none.** FDA "has not identified any particular circumstances appropriate for a waiver … and does not intend to grant requests for waiver" — the eSTAR PDF is freely downloadable, so all submitters are presumed able to comply.

**Timing** (§ VI.B): the requirement took effect **October 1, 2023** (after a ≥1-year voluntary transition). Transmission: **CDRH Portal** for CDRH-regulated devices; **Electronic Submissions Gateway (ESG)** for CBER. Known technical blockers (listed on the CDRH Portal page) may force mailing to the CDRH Document Control Center — that's a transmission fallback, not an eSTAR waiver.

## This Guidance vs the Q-Sub eSTAR Draft

Both implement § 745A(b)(3) under the same parent guidance, but do not confuse them:

| | **This guidance — 510(k) eSTAR** | [`qsub-estar-draft-distilled.md`](qsub-estar-draft-distilled.md) — Q-Sub eSTAR/PreSTAR |
|---|---|---|
| Submission type | 510(k)s (Traditional/Special/Abbreviated + Supplements/Amendments) | Q-Submissions — currently **Pre-Subs only** |
| Status | **Final**, in force | **Draft** (May 29, 2025) — not for implementation |
| Electronic format required? | **Yes, since Oct 1, 2023** (binding) | No — voluntary until ≥1 year after finalization |
| Template | 510(k) eSTAR | PreSTAR (Pre-Subs + 513(g)) |
| Screening | Technical screening ≤15 days; 180-day replacement window | Same model, proposed |

Practical consequence: a program filing a Pre-Sub today may still choose eCopy or voluntary PreSTAR, but its eventual **510(k) has no choice** — the package must land in the 510(k) eSTAR structure.

## Cross-References

- **510(k) SE guidance** ([`510k-se-distilled.md`](510k-se-distilled.md)) — substantive SE content the eSTAR's Device Description / Predicates sections collect.
- **Special 510(k)** ([`special-510k-distilled.md`](special-510k-distilled.md)) — Specials also ride eSTAR; the "Design/Special Controls, Risks to Health, and Mitigation Measures" section exists for them.
- **Software functions guidance** ([`sw-functions-distilled.md`](sw-functions-distilled.md)) — defines the software documentation the Software/Firmware section attaches (the technical screen checks a Software Description attachment exists when software applies).
- **Cybersecurity premarket** ([`cybersecurity-distilled.md`](cybersecurity-distilled.md)) — content for the Cybersecurity/Interoperability section.
- **Q-Sub program** ([`qsub-distilled.md`](qsub-distilled.md)) — prior Q-Subs are declared in the Pre-Submission Correspondence section.
- **eCopy guidance** — still governs the exempted amendment types.

## Practical Checklist (Submitter)

1. Download the current 510(k) eSTAR from FDA's eSTAR program page (template versions change as policies change — always start from the current version).
2. Author submission content so each piece maps to an eSTAR section/attachment-type question; expect conditional prompts to demand one attachment per applicable question.
3. Pay the user fee promptly — technical screening does not begin until it is paid.
4. Verify the PDF banner reads "eSTAR Complete" before transmitting via the CDRH Portal (or ESG for CBER).
5. If a technical-screening deficiency email arrives: submit a complete **replacement** eSTAR within 180 days, or the submission is auto-withdrawn.
6. During review: interactive-review responses go by email; formal AI responses go back through eSTAR (changed content placed in its proper section).
