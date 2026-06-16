# 21 CFR Part 807 — Establishment Registration and Device Listing

🔎 **Finding aid — NOT the authoritative source.** Distilled summary with selected commentary. Ground and cite the faithful verbatim full text [`source-md/21-cfr-part-807.md`](source-md/21-cfr-part-807.md) (a no-LLM transcription of the eCFR XML), not this file. Regulations change — verify currency against the live eCFR before relying on it in a submission. `[VERIFY]` marks are unconfirmed.

**Citation**: 21 CFR Part 807 (Title 21, Chapter I, Subchapter H)
**Authority**: 21 U.S.C. 321, 331, 351, 352, 360, 360c, 360e, 360i, 360j, 360k, 374, 393
**Promulgating Agency**: FDA / CDRH
**Status**: Active (current at retrieval date — see Source provenance)
**Source**: eCFR API — `https://www.ecfr.gov/api/versioner/v1/full/<date>/title-21.xml?chapter=I&subchapter=H&part=807`

## Scope

Part 807 establishes the requirements for **device establishment registration**, **device listing**, and — most consequentially for premarket strategy — **when a 510(k) premarket notification is required (§ 807.81)**. (Note on exemptions: § 807.85 exempts only **custom devices** and **distributors/repackagers** under conditions; *class-based* 510(k) exemption flows from FD&C Act § 510(l)/(m) and the device's classification regulation, not from Part 807. § 807.65 covers establishment-registration exemptions.) The Part 807 framework is the regulatory anchor for the entire 510(k) substantial-equivalence pathway and for the "significant change" analysis that drives sw-changes guidance and PCCP scope decisions.

Part 807 contains Subparts A–E:

| Subpart | Title |
|---------|-------|
| A | General Provisions |
| B | Procedures for Device Establishments |
| C | Procedures for Foreign Device Establishments |
| D | Exemptions |
| E | Premarket Notification Procedures |

This distillation focuses on **Subpart E (§§ 807.81–807.100)** and **Subpart D (§ 807.65)** — the sections cited most often in medtech regulatory strategy. Subparts A–C (registration and listing administration) are summarized; consult the eCFR source for verbatim text.

## Section Index — Sections Relevant to Premarket Strategy

| Section | Title | Notes |
|---------|-------|-------|
| § 807.3 | Definitions | Definitions of "establishment," "device," "manufacturer," "specifications developer," etc. |
| § 807.20 | Who must register and submit a device list? | Threshold for triggering registration / listing obligations |
| § 807.65 | Exemptions for device establishments | Exemptions from registration/listing — NOT the same as 510(k) exemptions in § 807.85 |
| § 807.81 | When a premarket notification submission is required | **Load-bearing for all 510(k) work**; § 807.81(a)(3) is the "significant change" trigger |
| § 807.85 | Exemption from premarket notification | Custom devices (§ 520(b)) + distributors/repackagers — **NOT** the class-based exemption mechanism (that's FD&C § 510(l)/(m) + the classification regulation) |
| § 807.87 | Information required in a premarket notification submission | The 510(k) content list — feeds eSTAR templates |
| § 807.92 | Content and format of a 510(k) summary | The public-facing summary that becomes part of the cleared device record |
| § 807.97 | Misbranding by reference to premarket notification | "FDA approved" prohibition — clearance ≠ approval |
| § 807.100 | FDA action on a premarket notification | Five actions: SE order, NSE order, additional-info request, withhold pending Part 54 certification/disclosure, advise 510(k) not required |

## Subpart E — Premarket Notification Procedures (Detail)

### § 807.81 — When a premarket notification submission is required

**This is the section every 510(k)/sw-changes/PCCP question routes through.**

#### Verbatim — § 807.81(a)

> Except as provided in paragraph (b) of this section, each person who is required to register his establishment pursuant to § 807.20 must submit a premarket notification submission to the Food and Drug Administration at least 90 days before he proposes to begin the introduction or delivery for introduction into interstate commerce for commercial distribution of a device intended for human use which meets any of the following criteria:
>
> **(1)** The device is being introduced into commercial distribution for the first time; that is, the device is not of the same type as, or is not substantially equivalent to, (i) a device in commercial distribution before May 28, 1976, or (ii) a device introduced for commercial distribution after May 28, 1976, that has subsequently been reclassified into class I or II.
>
> **(2)** The device is being introduced into commercial distribution for the first time by a person required to register, whether or not the device meets the criteria in paragraph (a)(1) of this section.
>
> **(3)** The device is one that the person currently has in commercial distribution or is reintroducing into commercial distribution, but that is about to be **significantly changed or modified in design, components, method of manufacture, or intended use**. The following constitute significant changes or modifications that require a premarket notification:
>
> > **(i)** A change or modification in the device that could significantly affect the safety or effectiveness of the device, e.g., a significant change or modification in design, material, chemical composition, energy source, or manufacturing process.
> >
> > **(ii)** A major change or modification in the intended use of the device.

(§ 807.81(a)(1)–(a)(3) above verified verbatim against the in-repo eCFR source-md, Title-21 issue 2026-06-11. The earlier pre-2024 three-romanette (a)(1) text was corrected to the current two-romanette wording.)

**§ 807.81(b) — the PCCP carve-out (confirmed against live eCFR 2026-06-11).** Paragraph (b) lists when a new submission is *not* required, and now includes changes implemented under a **cleared predetermined change control plan consistent with the submission** (alongside the pending-PMA and reclassification-petition cases). This is the regulatory hook that makes PCCP-authorized changes lawful without a per-change 510(k) — the statutory basis is FD&C § 515C (FDORA 2022). `[VERIFY exact (b) wording before quoting in a submission]`

**Why this matters.** Almost every sw-changes / PCCP / Letter-to-File decision is framed against § 807.81(a)(3) — specifically (a)(3)(i) "could significantly affect safety or effectiveness" and (a)(3)(ii) "major change in intended use." The FDA software-changes guidance (`../fda-guidance/sw-changes-distilled.md`) interprets these criteria for software modifications; the General PCCP and AI/ML PCCP guidances (`../fda-guidance/pccp-general-distilled.md`, `../fda-guidance/pccp-aiml-distilled.md`) describe how pre-authorized modification protocols satisfy the § 807.81(a)(3) gate without per-change submission.

The three-way decision tree — PCCP / Letter-to-File / new 510(k) — explicitly hangs off § 807.81(a)(3). When a project doc cites "21 CFR 807.81(a)(3)" in a sw-changes context, the cite is to this subsection.

### § 807.85 — Exemption from premarket notification

(Re-pulled from live eCFR 2026-06-11 — the prior version of this section quoted text that was **not** § 807.85; corrected. Source cite per eCFR: 42 FR 42526, Aug. 23, 1977, as amended at 81 FR 70340, Oct. 12, 2016.)

> **(a)** A **custom device** is exempt from premarket notification requirements of this subpart if the device is within the meaning of section 520(b) of the Federal Food, Drug, and Cosmetic Act.
> > **(1)** It is intended for use by a patient named in the order of the physician or dentist (or other specially qualified person); or
> > **(2)** It is intended solely for use by a physician or dentist (or other specially qualified person) and is not generally available to, or generally used by, other physicians or dentists (or other specially qualified persons).
>
> **(b)** A **distributor** who places a device into commercial distribution for the first time under his own name **and a repackager** who places his own name on a device and does not change any other labeling or otherwise affect the device shall be exempted from the premarket notification requirements of this subpart if:
> > **(1)** The device was in commercial distribution before May 28, 1976; or
> > **(2)** A premarket notification submission was filed by another person.

`[VERIFY (b) chapeau wording against eCFR — transcribed via machine-assisted retrieval; the (a) criteria, (b)(1)/(2) conditions, and the custom-device/distributor scope are confirmed]`

**Practical:** § 807.85 covers only two narrow cases — **custom devices** (FD&C § 520(b)) and **private-label distributors/repackagers** of already-marketed devices (the case the device-changes guidance cites). It is **not** the mechanism that makes a device class 510(k)-exempt. Class-based exemption flows from **FD&C Act § 510(l) (Class I) / § 510(m) (listed Class II)** as implemented in the device's own classification regulation ("exempt from the premarket notification procedures in subpart E of part 807, subject to the limitations in § 8XX.9"). The "§ 9" limitation framework (§ 880.9, § 892.9, § 882.9, …) then determines whether an exempt device exceeds its exemption envelope and triggers a 510(k).

### § 807.87 — Information required in a premarket notification submission

The required content elements, **by subsection letter** (verified against the eCFR API 2026-06-15; for verbatim text, cite the `source-md/` transcription per the finding-aid note above):

| § | Element |
|---|---|
| (a) | Device name — trade/proprietary name, classification name, common or usual name |
| (b) | Establishment registration number of the submitter |
| (c) | Class into which the device is classified under § 513 + the classification panel |
| (d) | Action taken to comply with any applicable performance standard under § 514 |
| (e) | **Proposed labels, labeling, and advertisements** sufficient to describe the device, its intended use, and directions for use |
| (f) | Statement of **substantial equivalence** — comparison showing similarities/differences to a legally marketed (predicate) device |
| (g) | Supporting data for any significant change/modification or new indication |
| (h) | A **510(k) summary** (§ 807.92) **or** a **510(k) statement** (§ 807.93) |
| (i) | **Financial certification or disclosure** statement per Part 54 |
| (j) | Statements of compliance for clinical data (domestic and foreign investigations) |
| (k) | **Class III summary and certification** — types of safety/effectiveness problems + certification that a reasonable search of known information was conducted (preamendment Class III devices) |
| (l) | **Truthful-and-accuracy statement** — submitter's best-of-knowledge attestation that all data/information are truthful and accurate and that no material fact has been omitted |
| (m) | Any additional information FDA requests |

This list is the 510(k) eSTAR's content backbone — each eSTAR module maps to a § 807.87 element.

> **Citation discipline (load-bearing).** The two adjacent certifications are easily confused: **§ 807.87(k) is the *Class III summary & certification*; § 807.87(l) is the *truthful-and-accuracy statement*.** Cite **(l)** for the T&A statement. (A miscite of (k)↔(l) is exactly the slip this lettered table exists to prevent.)

### § 807.92 — Content and format of a 510(k) summary

The public-facing summary that becomes part of the cleared device's record on accessdata.fda.gov. Required content includes intended use, comparison to predicate, performance data summary, non-clinical and clinical study summaries, and conclusion of substantial equivalence. **This is the document the predicate device's K-number resolves to** — every accessdata lookup of a K-number returns the § 807.92 summary.

### § 807.97 — Misbranding by reference to premarket notification

> Any representation that creates an impression of official approval of a device because of complying with the premarket notification regulations is misleading and constitutes misbranding.

**Practical:** 510(k) clearance is NOT FDA approval. Marketing copy, labeling, and even internal documents that say "FDA-approved" for a 510(k)-cleared device are misbranding. The audit-relevant pattern: project docs that conflate "cleared" and "approved" trigger this section.

### § 807.100 — FDA action on a premarket notification

§ 807.100(a) defines **five** FDA actions after review (re-verified against live eCFR 2026-06-11): (1) order declaring the device **substantially equivalent (SE)** to a legally marketed predicate; (2) order declaring it **not substantially equivalent (NSE)**; (3) **request additional information**; (4) **withhold the decision** until a certification or disclosure statement is submitted under Part 54 (clinical-investigator financial disclosure); (5) **advise the applicant that premarket notification is not required**. Until an SE order issues, the applicant may not market the device. § 807.100(b) sets out the substantial-equivalence criteria (same intended use; same technological characteristics, or different characteristics with data demonstrating equivalent safety/effectiveness). (Note: "withdrawal" is a *submitter* action, not a § 807.100 disposition — a prior version of this file misstated this. MDUFA review-clock mechanics are program practice, not § 807.100 text.)

## Subpart D — Exemptions

### § 807.65 — Exemptions for device establishments

Lists categories of establishments exempt from the registration and listing requirements of Subpart B — e.g., manufacturers of components/parts, manufacturers of devices for export only, licensed practitioners who manufacture devices solely for their own patients. **Distinct from § 807.85** (which is about exemption from premarket notification, not from establishment registration).

## Practical Cross-References

| Question | Look here |
|----------|-----------|
| Is a software change significant enough to require a new 510(k)? | § 807.81(a)(3)(i) interpreted by `../fda-guidance/sw-changes-distilled.md` |
| Can I pre-authorize this change category via PCCP? | § 807.81(a)(3) + `../fda-guidance/pccp-general-distilled.md` / `../fda-guidance/pccp-aiml-distilled.md` |
| Is my device 510(k)-exempt? | Look up the device's classification regulation (Part 8XX); check the `§ X.5XXX` section for "exempt from premarket notification ... subject to the limitations of § X.9" |
| What goes in the 510(k) submission? | § 807.87 — 12 content elements |
| What does FDA do with a 510(k)? | § 807.100 — SE / NSE / additional-info request / withhold pending Part 54 / advise-not-required |

## Source Provenance

- **eCFR API endpoint**: `https://www.ecfr.gov/api/versioner/v1/full/<date>/title-21.xml?chapter=I&subchapter=H&part=807` (the human-viewer `ecfr.gov/current/...` URLs redirect automated fetchers; use the API)
- **Retrieval date**: 2026-05-29; **§§ 807.85, 807.100, 807.81(b) re-pulled 2026-06-11** after an audit found the § 807.85 quote was not the CFR text and § 807.100 listed the wrong dispositions
- **§ 807.85 source cite (from eCFR)**: 42 FR 42526, Aug. 23, 1977, as amended at 81 FR 70340, Oct. 12, 2016
- **Authoring agent**: distilled from eCFR-returned content via a `citations` audit that surfaced this section as a `registry-gap`; corrected 2026-06-11. (No `source/` XML archive exists yet for this category — the live eCFR API is the escalation path.)

[VERIFY all clause numbers and verbatim text against the live eCFR snapshot before relying on this distillation in a regulated submission.]
