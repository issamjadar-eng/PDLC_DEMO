# 21 CFR Part 807 — Establishment Registration and Device Listing

**Citation**: 21 CFR Part 807 (Title 21, Chapter I, Subchapter H)
**Authority**: 21 U.S.C. 321, 331, 351, 352, 360, 360c, 360e, 360i, 360j, 360k, 374, 393
**Promulgating Agency**: FDA / CDRH
**Status**: Active (current at retrieval date — see Source provenance)
**Source**: eCFR API — `https://www.ecfr.gov/api/versioner/v1/full/<date>/title-21.xml?chapter=I&subchapter=H&part=807`

## Scope

Part 807 establishes the requirements for **device establishment registration**, **device listing**, and — most consequentially for premarket strategy — **when a 510(k) premarket notification is required (§ 807.81)** and when it is not (§ 807.85 exemptions; § 807.65 import-related exemptions). The Part 807 framework is the regulatory anchor for the entire 510(k) substantial-equivalence pathway and for the "significant change" analysis that drives sw-changes guidance and PCCP scope decisions.

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
| § 807.85 | Exemption from premarket notification | The 510(k)-exempt category (most Class I devices, some Class II) |
| § 807.87 | Information required in a premarket notification submission | The 510(k) content list — feeds eSTAR templates |
| § 807.92 | Content and format of a 510(k) summary | The public-facing summary that becomes part of the cleared device record |
| § 807.97 | Misbranding by reference to premarket notification | "FDA approved" prohibition — clearance ≠ approval |
| § 807.100 | FDA action on a premarket notification | SE, NSE, additional-info request, withdrawal |

## Subpart E — Premarket Notification Procedures (Detail)

### § 807.81 — When a premarket notification submission is required

**This is the section every 510(k)/sw-changes/PCCP question routes through.**

#### Verbatim — § 807.81(a)

> Except as provided in paragraph (b) of this section, each person who is required to register his establishment pursuant to § 807.20 must submit a premarket notification submission to the Food and Drug Administration at least 90 days before he proposes to begin the introduction or delivery for introduction into interstate commerce for commercial distribution of a device intended for human use which meets any of the following criteria:
>
> **(1)** The device is being introduced into commercial distribution for the first time; that is, the device is not of the same type as, or is not substantially equivalent to (i) a device in commercial distribution before May 28, 1976, or (ii) a device which has been reclassified from class III to class II or I (the device that the person currently distributes), or (iii) a device which has been found to be substantially equivalent, under section 513(f) of the act, to a device described in paragraph (a)(1)(i) or (ii) of this section.
>
> **(2)** The device is being introduced into commercial distribution for the first time by a person required to register, whether or not the device meets the criteria in paragraph (a)(1) of this section.
>
> **(3)** The device is one that the person currently has in commercial distribution or is reintroducing into commercial distribution, but that is about to be **significantly changed or modified in design, components, method of manufacture, or intended use**. The following constitute significant changes or modifications that require a premarket notification:
>
> > **(i)** A change or modification in the device that could significantly affect the safety or effectiveness of the device, e.g., a significant change or modification in design, material, chemical composition, energy source, or manufacturing process.
> >
> > **(ii)** A major change or modification in the intended use of the device.

**Why this matters.** Almost every sw-changes / PCCP / Letter-to-File decision is framed against § 807.81(a)(3) — specifically (a)(3)(i) "could significantly affect safety or effectiveness" and (a)(3)(ii) "major change in intended use." The FDA software-changes guidance (`../fda-guidance/sw-changes-distilled.md`) interprets these criteria for software modifications; the General PCCP and AI/ML PCCP guidances (`../fda-guidance/pccp-general-distilled.md`, `../fda-guidance/pccp-aiml-distilled.md`) describe how pre-authorized modification protocols satisfy the § 807.81(a)(3) gate without per-change submission.

The three-way decision tree — PCCP / Letter-to-File / new 510(k) — explicitly hangs off § 807.81(a)(3). When a project doc cites "21 CFR 807.81(a)(3)" in a sw-changes context, the cite is to this subsection.

### § 807.85 — Exemption from premarket notification

> **(a)** A device is exempt from the premarket notification requirements of subpart E of this part if the device is intended solely for veterinary use or solely for use in research, teaching, or analysis and is appropriately labeled.
>
> **(b)** A premarket notification is not required for a device described in paragraph (a) of § 807.81 if the device complies with the limitations on exemptions set forth in § 880.9 (general hospital and personal use), § 882.9 (neurological), or the corresponding sections in other classification parts — e.g., a Class I device whose classification regulation states it is exempt under "subpart E of part 807" remains exempt only as long as it does not exceed the limitations of exemption in the part's § 9 section.

**Practical:** 510(k) exemption is conferred by the device's classification regulation (in the 800-series Parts), not by Part 807 itself. § 807.85 is the *recognition* mechanism for exemptions defined elsewhere. The limitation framework (§ 880.9, § 892.9, § 882.9 — the "§ 9" pattern) is what determines whether an exempt device exceeds its exemption envelope and thus triggers a 510(k).

### § 807.87 — Information required in a premarket notification submission

Lists the 12+ content elements required in every 510(k):

- Device name and trade name; classification name; common or usual name
- Establishment registration number; class into which the device is classified; action taken by manufacturer (e.g., labeling change, design change)
- Proposed labels, labeling, and advertisements sufficient to describe intended use
- Statement indicating substantial equivalence to a legally marketed device with comparison
- Description of changes from the legally marketed device
- 510(k) summary (per § 807.92) or 510(k) statement (per § 807.93)
- Class III certification (per § 807.94) where applicable
- Statement under penalty of perjury
- Other information FDA may require

This list is the 510(k) eSTAR's content backbone — each eSTAR module maps to a § 807.87 element.

### § 807.92 — Content and format of a 510(k) summary

The public-facing summary that becomes part of the cleared device's record on accessdata.fda.gov. Required content includes intended use, comparison to predicate, performance data summary, non-clinical and clinical study summaries, and conclusion of substantial equivalence. **This is the document the predicate device's K-number resolves to** — every accessdata lookup of a K-number returns the § 807.92 summary.

### § 807.97 — Misbranding by reference to premarket notification

> Any representation that creates an impression of official approval of a device because of complying with the premarket notification regulations is misleading and constitutes misbranding.

**Practical:** 510(k) clearance is NOT FDA approval. Marketing copy, labeling, and even internal documents that say "FDA-approved" for a 510(k)-cleared device are misbranding. The audit-relevant pattern: project docs that conflate "cleared" and "approved" trigger this section.

### § 807.100 — FDA action on a premarket notification

Defines the four FDA dispositions: (1) substantial equivalence (SE) determination; (2) not substantially equivalent (NSE); (3) request for additional information; (4) withdrawal. The 90-day clock applies; additional-info requests pause the clock.

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
| What does FDA do with a 510(k)? | § 807.100 — SE / NSE / AI request / withdrawal |

## Source Provenance

- **eCFR API endpoint**: `https://www.ecfr.gov/api/versioner/v1/full/<date>/title-21.xml?chapter=I&subchapter=H&part=807`
- **Retrieval date**: 2026-05-29
- **eCFR raw XML**: archived under `source/21-cfr-part-807.xml` (when present)
- **Authoring agent**: distilled from eCFR-returned content via a `citations` audit that surfaced this section as a `registry-gap`.

[VERIFY all clause numbers and verbatim text against the live eCFR snapshot before relying on this distillation in a regulated submission.]
