# 21 CFR Part 814 — Premarket Approval of Medical Devices

**Citation**: 21 CFR Part 814 (Title 21, Chapter I, Subchapter H)
**Authority**: 21 U.S.C. 351, 352, 353, 360, 360c–360j, 360e, 371, 372, 374, 379, 379e, 381 `[VERIFY authority list against the live eCFR header]`
**Promulgating Agency**: FDA / CDRH
**Status**: Active (current at retrieval date — see Source provenance)
**Source**: eCFR API — `https://www.ecfr.gov/api/versioner/v1/full/<date>/title-21.xml?chapter=I&subchapter=H&part=814`

## Scope

Part 814 establishes the requirements for **Premarket Approval (PMA)** — the most stringent device marketing pathway, required for Class III devices that are *not* eligible for 510(k) (no predicate, or insufficient to establish substantial equivalence). Unlike a 510(k) (which demonstrates **substantial equivalence** to a predicate under Part 807), a PMA must independently demonstrate, with **valid scientific evidence**, a **reasonable assurance of safety and effectiveness** for the device's intended use. Part 814 also houses the **Humanitarian Device Exemption (HDE)** program (Subpart H).

This distillation focuses on **§ 814.20 (PMA content and format)** — the section the submission skill's PMA template profile maps onto — and indexes the other load-bearing sections (PMA supplements, FDA action incl. the SSED, postapproval requirements, HDE). Consult the eCFR source for verbatim text of sections summarized here.

Part 814 subparts (those most cited):

| Subpart | Title | Key sections |
|---------|-------|--------------|
| A | General Provisions | § 814.1 scope · § 814.3 definitions · § 814.9 confidentiality |
| B | Premarket Approval Application (PMA) | **§ 814.20 content & format** · § 814.39 PMA supplements · § 814.42 filing · § 814.44 FDA action (SSED) · § 814.45 denial |
| E | Postapproval Requirements | § 814.80 general · § 814.82 conditions of approval · § 814.84 reports |
| H | Humanitarian Use Devices (HDE) | § 814.100+ — the HDE alternative for rare-disease devices `[VERIFY exact section span]` |

> `[VERIFY]` the full subpart letter map (incl. any reserved subparts C/D/F/G) against the live eCFR before relying on it in a submission.

## Subpart B — Premarket Approval Application (Detail)

### § 814.20 — Application (content and format)

**This is the section the PMA template profile (`submissions` skill) maps onto.** Verified against the eCFR API 2026-06-15.

**§ 814.20(a) — Signature.** The applicant (or an authorized representative) signs the PMA; if the applicant has no U.S. residence/place of business, a U.S.-based representative must countersign.

**§ 814.20(b) — Required content**, in the order specified:

| § | Component | Maps to PMA template stub |
|---|-----------|----------------------------|
| (b)(1) | Applicant's name and address | cover-letter |
| (b)(2) | Table of contents (volume/page); separate nonclinical-studies and clinical-investigations sections; identification of trade-secret/confidential information | (package assembly) |
| (b)(3) | **Summary** — see (i)–(vi) below | `ssed-summary.md` |
| (b)(3)(i) | Indications for use — disease/condition + patient population | ssed-summary / labeling |
| (b)(3)(ii) | Device description — function, scientific concepts, physical/performance characteristics, manufacturing where relevant | device-description |
| (b)(3)(iii) | Alternative practices/procedures for the same condition | ssed-summary |
| (b)(3)(iv) | Marketing history — foreign/U.S.; any country where withdrawn for safety/effectiveness | ssed-summary |
| (b)(3)(v) | Summary of nonclinical & clinical studies — objectives, design, data collection/analysis, results | ssed-summary |
| (b)(3)(vi) | Conclusions — valid scientific evidence + reasonable safety/effectiveness assurance; **benefit-risk** discussion | ssed-summary |
| (b)(4) | Complete **device description** — pictures, functional components, properties, principles of operation, manufacturing & QC methods | device-description |
| (b)(5) | References to applicable **performance standards** (mandatory + voluntary); compliance or justified deviations | (DHF-attached / standards) |
| (b)(6) | **Technical sections** — nonclinical lab studies (b)(6)(i) + clinical investigations (b)(6)(ii) in sufficient detail for FDA approval determination | `nonclinical-studies.md` · `clinical-studies.md` |
| (b)(7) | For a single-investigation PMA: justification of sufficiency and reproducibility | clinical-studies |
| (b)(8) | **Bibliography** of published safety/effectiveness reports + analysis of other relevant data; copies on FDA request | (package) |
| (b)(9) | Device **samples** (or examination location if impractical to submit) | (logistics) |
| (b)(10) | Copies of all **proposed labeling** | `labeling.md` |
| (b)(11) | **Environmental assessment** per § 25.20(n) or exclusion justification | (package) |
| (b)(12) | **Financial certification/disclosure** statement per Part 54 | cover-letter / statements |
| (b)(13) | **Pediatric information** if readily available — affected subpopulations + patient numbers | ssed-summary |

> The PMA template stubs cover the **major** components (b)(3), (b)(4), (b)(6), (b)(10) + manufacturing. The **minor** components — (b)(5) performance standards, (b)(8) bibliography, (b)(11) environmental assessment, (b)(12) financial certification, (b)(13) pediatric info — are not separate stubs; add them when the PMA profile is built out for real use.

**§ 814.20(c)** — pertinent FDA file info may be incorporated by reference; master files require authorization.
**§ 814.20(d)** — omitted required information must be identified and justified in a separate PMA section.
**§ 814.20(e)** — applicant must periodically **update** a pending PMA with new safety/effectiveness information (≈3 months after filing, after an approvable letter, and on FDA request).

### § 814.39 — PMA supplements

A change to an approved PMA device that affects safety or effectiveness requires a **PMA supplement** (the PMA analogue of a new 510(k) for a significant change). Lighter change-reporting mechanisms exist (30-day notice / special PMA supplement / annual report) depending on change type. `[VERIFY change-type tiers against the live section]`

### § 814.44 — FDA action on a PMA — and the SSED

FDA dispositions: approval order, approvable letter, not-approvable letter, or denial (§ 814.45). On approval, FDA publishes a **Summary of Safety and Effectiveness Data (SSED)** — the public benefit-risk summary (the PMA analogue of the § 807.92 510(k) summary). The template profile's `ssed-summary.md` corresponds to this artifact (built from the § 814.20(b)(3) summary content). `[VERIFY the SSED-publication subsection letter]`

## Subpart E — Postapproval Requirements (summary)

- **§ 814.80** — device must be manufactured, packaged, stored, labeled, distributed, and advertised in conformance with the approved PMA.
- **§ 814.82** — FDA may impose **conditions of approval** (e.g., postapproval studies, labeling restrictions, periodic reporting).
- **§ 814.84** — periodic (annual) reports + unanticipated-adverse-effect reporting.

## Subpart H — Humanitarian Device Exemption (summary)

The **HDE** (§ 814.100+) is an alternative for devices intended to benefit patients with a disease/condition affecting a small population (a Humanitarian Use Device). An HDE is similar in form to a PMA but is **exempt from the effectiveness** requirement — it must show safety + probable benefit and that no comparable device is available. `[VERIFY the population threshold and the exact section span]`

## Practical Cross-References

| Question | Look here |
|----------|-----------|
| What goes in a PMA, and in what order? | § 814.20(b)(1)–(13) — the table above |
| What's the PMA analogue of the 510(k) summary? | The **SSED** (§ 814.44) — public benefit-risk summary on approval |
| How do I change an approved PMA device? | § 814.39 — PMA supplement (vs 30-day notice / annual report by change type) |
| 510(k) vs PMA — which pathway? | Part 807 (510(k), substantial equivalence) vs this Part (PMA, independent reasonable-assurance). Pathway selection lives in `docs/project/strategies/regulatory-strategy.md`. |
| Rare-disease / small-population device? | Subpart H — HDE (safety + probable benefit; effectiveness-exempt) |

## Source Provenance

- **eCFR API endpoint**: `https://www.ecfr.gov/api/versioner/v1/full/<date>/title-21.xml?chapter=I&subchapter=H&part=814`
- **Retrieval date**: 2026-06-15 (§ 814.20(a)–(e) incl. (b)(1)–(13) and (b)(3)(i)–(vi) verified against the eCFR API; § 814.39 / 814.44 / Subparts E & H summarized — flagged `[VERIFY]` where not directly retrieved this pass)
- **Authoring context**: distilled to close the registry gap surfaced by the `submissions` skill PMA-profile verification (ben/088) — the PMA templates previously cited `814.20(b)(...)` with no project distillation to ground against.

[VERIFY all clause numbers and verbatim text against the live eCFR snapshot before relying on this distillation in a regulated submission. The PMA profile in the `submissions` skill is a placeholder; do not treat these summaries as a substitute for the regulation when building out a real PMA.]
