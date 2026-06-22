# FDA Guidance: Medical Device Accessories — Describing Accessories and Classification Pathways

🔎 **Finding aid — NOT the authoritative source.** Distilled summary for quick orientation and early analysis. Ground and cite the authoritative full text [`source-md/accessories.md`](source-md/accessories.md); verify any quote against the byte-correct `source/accessories.pdf` before treating it as verbatim. This paraphrases and omits (the appendix worked-example detail is condensed) — a section's absence here is never evidence the source is silent.

**Full Title**: Medical Device Accessories – Describing Accessories and Classification Pathways: Guidance for Industry and Food and Drug Administration Staff
**Document Date**: **December 20, 2017** (issued); **originally issued December 30, 2016**. Supersedes "Medical Device Accessories – Describing Accessories and Classification Pathway for New Accessory Types," issued January 30, 2017.
**Status**: Final (Contains Nonbinding Recommendations)
**Docket Number**: FDA-2015-D-0025
**CDRH Document Number**: 1770
**OMB Control No.**: 0910-0823
**Issuing Bodies**: CDRH + CBER
**Statutory Basis**: FD&C Act § 201(h) (the "device" definition expressly includes "accessory"); § 513(f)(6) (Accessory Classification process — New + Existing Accessory Requests); § 513(f)(2) (De Novo classification for new accessory types); § 513(a)(1) (risk-/control-based classification criteria); **FDA Reauthorization Act of 2017 (FDARA, Pub. L. 115-52), Aug 18, 2017**, amending § 513(f) to require classifying an accessory on **its own** risks "notwithstanding the classification of any other device with which such accessory is intended to be used."
**Companion Guidance**: De Novo Classification Process guidance; Pre-Submission / Q-Sub program — see `qsub-distilled.md`; Benefit-Risk determination factors guidance; Policy for Device Software Functions — see `sw-functions-distilled.md`; Multiple Function Device — see `mfd-distilled.md`; Clinical Decision Support — see `cds-distilled.md`
**Source PDF**: `source/accessories.pdf` (17-page file; 14 pages of content + appendix); raw text in `source-md/accessories.md`

## Scope

This guidance describes (a) **what FDA generally considers an "accessory"** to a medical device and (b) **how an accessory gets classified** — applying the FD&C Act's risk- and regulatory-control-based framework to the accessory **based on the accessory's own risks**, not the parent device's class.

The load-bearing legal shift is **FDARA 2017** (Aug 18, 2017): § 513(f) now requires FDA to classify an accessory "based on the risks of the accessory when used as intended and the level of regulatory controls necessary to provide a reasonable assurance of safety and effectiveness of the accessory, **notwithstanding the classification of any other device with which such accessory is intended to be used**." Practical consequence: **an accessory may be classified in a lower class than its parent device** (e.g., an accessory to a Class III parent that poses only low/moderate risk may be regulated as Class I or II), where general controls (or general + special controls) provide reasonable assurance of safety and effectiveness.

The guidance applies **only to articles that meet the device definition under § 201(h)**. It applies the same paradigm to **software accessories, including SaMD** (see § III below). It is the operative guidance for the **Accessory Classification process under § 513(f)(6)** and for using the **De Novo process (§ 513(f)(2))** to classify a *new accessory type*.

## Table of Contents (mirrors the source)

| § | Section |
|---|---------|
| I | Introduction |
| II | Background — jurisdiction over accessories; the two traditional classification ways; FDARA 2017 amendment |
| III | Scope — § 513(f)(6) mechanisms; SaMD treatment |
| IV | Definitions — Accessory, Component, Finished Device, Parent Device |
| V | Accessory Classification **Policy** — the two questions (A: is it an accessory? B: what are its risks/controls?) |
| VI | Accessory Classification **Processes** — A: Accessory Requests (New / Existing); B: De Novo for new accessory types |
| VII | Paperwork Reduction Act of 1995 |
| App. 1 | Recommended content for a Request for Accessory De Novo Classification |

## Key Definitions (Section IV)

> **Accessory**: A finished device that is intended to **support, supplement, and/or augment** the performance of one or more **parent devices**.
>
> **Parent Device**: A finished device whose performance is supported, supplemented, and/or augmented by one or more accessories.
>
> **Component** (21 CFR 820.3(c)): any raw material, substance, piece, part, software, firmware, labeling, or assembly intended to be included as part of the finished, packaged, and labeled device.
>
> **Finished Device** (21 CFR 820.3(l)): any device or accessory to any device suitable for use or capable of functioning, whether or not packaged, labeled, or sterilized.

The **accessory vs. component** distinction is load-bearing: a *component* is built into another device; an *accessory* is itself a finished device used **with** a parent device.

## Section V-A — Is the article an accessory? (the two-prong test)

An article is an accessory when **both** prongs are met:

1. **Intended for use with one or more parent devices.** Intended use is generally determined by the **labeling and promotional materials of the *potential accessory*** (not the parent's). Articles labeled "optional" still count. **Counter-examples** (NOT accessories merely because usable with a device): a mobile phone used as a general platform, or an off-the-shelf computer monitor used to display medical data — *unless specifically intended* for use with the medical device.
2. **Intended to support, supplement, and/or augment** a parent device's performance:
   - **Supports** — enables/facilitates the parent to perform per its intended use. *Source examples*: a tunneling tool that creates a conduit for neurostimulator leads (necessary to enable intended use); an **infusion pump stand** that holds medications/liquids/infusion accessories at the right height and within reach (the pump works without it, but the stand still supports performance).
   - **Supplements** — adds a new function or new way of using the parent **without changing its intended use**. *Source examples*: a pulse oximeter that lets a multi-parameter monitor display SpO₂; a new balloon catheter expanding the treatable population for an approved transcatheter heart valve.
   - **Augments** — enables the parent to perform its intended use **more safely or effectively** (faster, more precise, more usable/convenient). *Source examples*: a guidewire increasing a bone-cutting instrument's precision; software adding color/contrast filters to enhance raw images from an imaging device.

The three categories overlap; many accessories do more than one. If any of support/supplement/augment is met, FDA intends to treat the article as an accessory — **required or optional**.

**Not accessories / not devices**: non-device-specific off-the-shelf replacement parts (batteries, USB cables, computer mouse, etc.) used with a medical device — FDA does not intend to consider these accessories or devices.

## Section V-B — Risk and regulatory controls

FDA determines an accessory's risk and the controls needed for reasonable assurance of safety and effectiveness **the same way it does for non-accessory devices**, but evaluated **in the context of the accessory's intended use *with* the parent device**. Key principle: **not all parent-device risks are imputed to the accessory** — the accessory's risk profile can differ significantly. FDA evaluates (a) the risks from the accessory's *impact on the parent device* and (b) any *unique risks of the accessory independent of the parent*. The controls needed to address those risks set the accessory's class.

## Section II — Two traditional ways accessories were classified

1. **Same classification as the parent device**, via one of:
   - 510(k) premarket notification (accessory found substantially equivalent under the parent's classification regulation);
   - PMA approval (an accessory to an approved Class III device may be approved in a PMA and remain Class III); or
   - **express inclusion** in the parent device's classification regulation or reclassification order.
2. **A unique, separate classification regulation for the accessory** — used when the accessory has a different risk profile (e.g., usable with multiple parents, or has standalone functions) warranting different controls.

FDARA 2017 overlays both: classification must reflect the accessory's **own** risk, so "same as parent" is appropriate only when the accessory actually meets the criteria for the parent's class.

## Section III — Software / SaMD treatment

The risk-/control-based paradigm applies to **all software products that meet the accessory definition, including SaMD** (IMDRF: "software intended to be used for one or more medical purposes that perform these purposes without being part of a hardware medical device").

**Critical boundary — using device data ≠ being an accessory.** A standalone software program that *analyzes radiological images* or *analyzes specific data parameters generated by a device* (e.g., blood-pressure or heart-rate data) is **SaMD but generally NOT an accessory**, because it does not *support, supplement, or augment the performance of the device that generated the data*. Conversely, SaMD used **in combination (e.g., as a module) with other devices** **may be** an accessory if it supports/supplements/augments one or more parent devices. The accessory test is about the support/supplement/augment relationship, not mere data consumption.

## Section VI — Accessory Classification Processes

FDA tracks **Accessory Requests as Q-Submissions** (see `qsub-distilled.md`). A Pre-Submission is recommended to get FDA feedback on a proposed Accessory Request.

### A. Accessory Requests under § 513(f)(6)

| Request type | Statute | When | FDA decision clock | Notes |
|---|---|---|---|---|
| **New Accessory Type** | § 513(f)(6)(C) | Accessory included in a PMA / PMA supplement / 510(k) and **not yet classified distinctly**; type never before classified/cleared/approved | **Concurrent** with the decision on the premarket submission it accompanies | Submit *with* the parent submission; cover letter must flag "New Accessory Request" + proposed class (I or II). If **denied** but the parent submission clears/approves, the accessory is legally marketed **in the parent's class**. |
| **Existing Accessory Type** | § 513(f)(6)(D) | Accessory already granted marketing authorization as part of another device's submission | **Within 85 days** of receipt | Cover letter must flag "Existing Accessory Request" + proposed **and** current class. FDA offers a pre-submission meeting on request. If granted, FDA issues a written order and publishes a final order in the Federal Register (codified in 21 CFR parts 862–892). |

**Class II requests** (either type) must include an **initial draft proposal for special controls** if special controls would be required under § 513(a)(1)(B).

### B. De Novo for new accessory types (§ 513(f)(2))

For a **new accessory type** with **no legally marketed predicate** and not covered by an existing classification regulation/PMA/510(k): the De Novo process gives a pathway to **Class I or II** for low-to-moderate-risk accessories where general controls (or general + special controls) provide reasonable assurance of safety and effectiveness.

- **Decision clock**: written order **within 120 days** of the request.
- **If granted** (§ 513(a)(1)(A) or (B) criteria met): classifies the new accessory (and type) in Class I or II; may be marketed immediately and **serve as a predicate** for future 510(k)s (if applicable); FDA publishes a Federal Register notice.
- **If declined**: the accessory remains in **Class III** under § 513(f)(1) and may not be marketed until a PMA is submitted and approved.

See `predicate-selection-distilled.md` and `510k-se-distilled.md` for the downstream 510(k) pathway a granted De Novo accessory enables.

## Appendix 1 — Recommended content for an accessory De Novo request (condensed)

FDA recommends a streamlined De Novo submission including: clear identification as a *De Novo for a new accessory type*; **device information** (parent device(s) described; compatibility with a specific parent / multiple parents / a class of devices; technical characteristics ensuring compatibility; how the accessory supports/supplements/augments the parent); **parent-product identification** (model number, connector type); **classification summary + recommendation** (rationale for why it doesn't fit any existing parent classification); **risks to health + proposed mitigations**; **proposed controls** (Class II → general + special controls; Class I → general controls only, with rationale); **performance-data summary** (all reasonably known relevant data, favorable or not); and **labeling** with adequate instructions for use with the parent device(s), including compatibility and technical characteristics. A **draft executive summary** is also recommended (administrative info; proposed identification language for the new classification regulation/order; accessory summary; performance-data summary; risk/mitigation info; benefit/risk considerations).

## Practical Cross-References

| Question | Look here |
|----------|-----------|
| Is my article an accessory at all? | § V-A two-prong test (intended-for-use-with + support/supplement/augment) + § IV definitions |
| My accessory is for a Class III parent — must it be Class III? | **No** — § II + FDARA 2017: classify on the accessory's *own* risk; it can be lower class |
| Is my SaMD that consumes device data an accessory? | § III — using device data ≠ accessory; must *support/supplement/augment the generating/parent device* |
| New accessory bundled with a parent submission | § VI-A "New Accessory Type" (§ 513(f)(6)(C)) — decided concurrently with the parent submission |
| Reclassify an already-marketed accessory | § VI-A "Existing Accessory Type" (§ 513(f)(6)(D)) — 85-day clock |
| New accessory type, no predicate | § VI-B De Novo (§ 513(f)(2)) — 120-day clock; Class I/II |
| What goes in an accessory De Novo? | Appendix 1 |
| Are off-the-shelf parts (cables, batteries) accessories? | No — § V-A; non-device-specific OTS parts are neither accessories nor devices |

## Distiller Notes (NOT guidance text)

- The guidance's own **infusion-pump-stand** example (§ V-A, "supports") is directly relevant to infusion-device programs: a stand that holds the pump/medications is an accessory that *supports* the parent pump even though the pump functions without it. Whether a given accessory to a PCA infusion pump is itself a device/accessory, and at what class, is a **project-applicability** question — work it in `docs/external/fda-guidance/` against the project's actual accessory list, not here.
- This guidance is **silent on AI/ML** accessories specifically; for AI-enabled software accessories, pair this with `cds-distilled.md`, `sw-functions-distilled.md`, and the AI/ML lifecycle references.

## Source Provenance

- **Source PDF**: `source/accessories.pdf` (issued Dec 20, 2017; 17-page file)
- **Source-MD**: `source-md/accessories.md` (raw `pdftotext -layout` extraction — the authoritative grounding + citation surface)
- **Docket**: FDA-2015-D-0025 · **CDRH doc #**: 1770 · **OMB Control No.**: 0910-0823
- **Key statute**: FDARA 2017 (Pub. L. 115-52) amendment to FD&C Act § 513(f), effective Aug 18, 2017
