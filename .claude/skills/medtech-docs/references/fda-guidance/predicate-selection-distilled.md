# Best Practices for Selecting a Predicate Device (DRAFT)

**Full Title**: Best Practices for Selecting a Predicate Device to Support a Premarket Notification [510(k)] Submission — Draft Guidance for Industry and Food and Drug Administration Staff
**Document Date**: Issued September 7, 2023
**Status**: **DRAFT — distributed for comment purposes only; "Not for Implementation."** When finalized it will represent FDA's current thinking; until then it signals reviewer expectations but creates no obligations beyond existing statute/regulation. Check whether a final version has issued before relying on section numbering.
**PDF Source**: `source/predicate-selection.pdf` (FDA guidance database document number GUI00020006)
**Issuing Bodies**: CDRH, CBER
**Docket**: Not stated in the document text (assigned via the Federal Register notice of availability; 90-day comment window from FR publication)
**Full text**: [`source-md/predicate-selection.md`](source-md/predicate-selection.md)

## Scope

This draft guidance recommends **four best practices for choosing which predicate device to anchor a 510(k) on**, once the candidate pool of "valid predicate devices" has been established. It explicitly does **not** change the substantial-equivalence (SE) standard, the 513(i) statutory criteria, or any 510(k) content requirement — it is a *selection-hygiene and transparency* layer on top of the 510(k) Program Guidance ([`510k-se-distilled.md`](510k-se-distilled.md)), with which it is meant to be used. It is the outcome of FDA's 2018–2019 "510(k) modernization" push: FDA abandoned its initial proposal to discourage predicates **older than 10 years** (docket FDA-2018-N-4751 comments showed age is the wrong proxy — old implants can carry valuable long-term safety history, while for **software devices a more recently cleared predicate may carry modern cybersecurity, interoperability, and architecture features**) and instead pivoted to predicate **characteristics**: methods quality, real-world safety record, signal status, and recall history.

**Key terminology**: a **"valid predicate device"** = a legally marketed device the submitter believes has the **same intended use** as the subject device, where any different technological characteristics **do not raise different questions of safety and effectiveness**. The four best practices narrow the *list of valid predicates* down to *the* predicate used to support the submission (Figure 1's funnel). FDA — not the submitter — ultimately determines whether a valid predicate exists. **Reference devices are not predicates** (they support scientific methodology / reference values beyond Decision 4 of the 510(k) flowchart) — the four factors formally apply to predicate selection, not reference-device citation.

**Key-question TL;DR**: From your list of valid predicates, prefer the one that (A) was **cleared using well-established methods** (recognized consensus standards, FDA guidance methods, qualified MDDTs, accepted public-domain/literature methods, or methods FDA accepted in your own prior submission); (B) **continues to meet or exceed expected safety and performance** in real-world use (search MAUDE, MDR, MedSun); (C) has **no unmitigated use-related or design-related safety issues** (search emerging signals and safety communications); and (D) has **no design-related recall** (search the Medical Device Recalls Database). Then **say so in the 510(k) Summary**: include a narrative of how the best practices drove the selection; if no best-practice-consistent valid predicate exists, state that, and use the Performance Data section to show how the subject device mitigates the predicate's known issues. Failing a factor does **not** disqualify a predicate — it triggers a mitigation-and-disclosure obligation (Example 2: a recalled predicate was still usable as the *only* valid predicate, with testing addressing the recall's safety concerns).

## Section-by-Section Distillation

### I–II. Introduction & Background

- Four best practices; no change to SE evaluation, statutory criteria, or valid-scientific-evidence requirements. Goal: predictability, consistency, transparency of 510(k) review.
- §II.A restates the 510(k)/SE framework: same intended use first; then same technological characteristics, or different characteristics that raise no different questions of safety/effectiveness with the new device as safe and effective as the predicate (FD&C § 513(i); 21 CFR 807.92(a)(3)–(6)). Statutory exclusion: no SE to a predicate removed from the market at FDA's initiative or adjudicated misbranded/adulterated (§ 513(i)(2)).
- §II.B is the modernization history (Safety Action Plan 2018 → Nov 2018 announcement → Jan 2019 ten-year-predicate proposal → docket feedback → pivot from **predicate age** to **predicate characteristics**). The software-vs-implant asymmetry is FDA's own worked rationale and is useful argumentation: *recent* predicates are affirmatively preferable for software devices.

### III–IV. Scope & How to Use

- Use during 510(k) preparation, in conjunction with the 510(k) Program Guidance; does not supplant device-specific guidances.
- Workflow: build the valid-predicate list (same intended use + no different S&E questions) from the 510(k) Premarket Notification Database starting with administrative search (trade names, manufacturers, K-numbers, product codes / classification regulation), then review each candidate's **510(k) Summary and Indications for Use**, then apply the four § V factors to narrow to the predicate.
- **Document the application of the best practices in the submission itself** (e.g., the SE Discussion section): how the factors were used, and — where a best-practice-consistent valid predicate is unavailable — how the known concerns of the chosen predicate are **mitigated by the subject device** (design features, performance testing).
- Multiple predicates remain permissible per the 510(k) Program Guidance (combining features, multiple intended uses, multiple indications under one intended use); special controls still must be met where established.

### V. The Four Best-Practice Factors

| # | Factor (verbatim heading) | Test | Where to search |
|---|---|---|---|
| **A** | *Predicate devices cleared using well-established methods* | Predicate's clearance testing used: currently FDA-recognized voluntary consensus standards, FDA guidance methods, qualified MDDTs, widely accepted public-domain/literature methods, or methods found acceptable in the submitter's own previous premarket submission. Prefer consensus-developed / peer-reviewed methods. Also ask whether those methods are **still current** (standards get revised; superseded-guidance methods score poorly — Example 1 Predicate 3). | Predicate's public 510(k) Summary (nonclinical tests discussion); Recognized Consensus Standards Database; MDDT list. FDA concedes method info may not be public for older clearances. |
| **B** | *Predicate devices meet or exceed expected safety and performance* | Predicate continues to perform safely and as intended in its use environment; weigh reported adverse events, malfunctions, deaths — newly recognized event types, increased severity/frequency of known events, new product-product interactions. | **MAUDE**, **MDR**, and **MedSun** databases — search each for unexpected injury/death/malfunction reports per candidate. High-frequency failure patterns suggesting fundamental design issues → pick a different valid predicate if one exists. |
| **C** | *Predicate devices without unmitigated use-related or design-related safety issues* | No unmitigated use- or design-related safety issue, including **emerging signals** (per the Emerging Signals guidance: new causal association, FDA-evaluated, potential to affect patient management or benefit-risk) and **safety communications**. Signals may attach to one product, a product type, or cross-manufacturer materials issues (duodenoscope-reprocessing example). | FDA Medical Device Safety page; CBER Safety & Availability (Biologics) page. |
| **D** | *Predicate devices without an associated design-related recall* | No **design-related** recall (vs. manufacturing- or labeling-defect recalls). Design-related recall ⇒ possible fundamental design flaw / inadequate design controls (21 CFR 820.30); root cause may be unknown or uncorrectable. A clearance that was SE-sufficient at the time can still be a poor predicate afterward. | Medical Device Recalls Database (recalls classified since November 2002). Classify the recall cause: e.g., a catheter-tip-fracture recall is design-related when due to material inadequacy for user needs, not a manufacturing deviation. |

All four factors are "whenever possible" recommendations — the remedy for an unavoidable factor failure is **mitigation + disclosure**, not abandonment of the 510(k).

### VI. Transparency — the 510(k) Summary Narrative

- Reaffirms 21 CFR 807.92 content duties and FDA's stated intent (per the 510(k) Program Guidance) to **verify accuracy/completeness of 510(k) Summaries**; FDA may require Summary revisions to reflect its decision-making. FDA encourages the 510(k) Summary over the 510(k) Statement option for transparency.
- **New recommendation**: include in the draft 510(k) Summary a **narrative explaining the predicate selection**, discussing how the four § V best practices were used (lands in the Comparison of Technological Characteristics section per 510(k) Program Guidance Appendix C).
- If **no** valid predicate consistent with the best practices is available: state that in the 510(k) Summary, and use the **Performance Data section** to describe testing that addresses the predicate's known safety/effectiveness concerns.

### VII. Examples (3)

1. **Coronary guidewire, 4 valid predicates** — a 4-column factor table (A–D per candidate) drives selection of the only candidate passing all four (current-FDA-guidance methods, expected AE frequency, no signals, no design recall); rejected candidates failed on internal/non-accepted methods + high MDR fracture frequency + safety communication (Predicate 1), design-related recall (Predicate 2), and superseded-guidance methods (Predicate 3). Narrative goes in the draft 510(k) Summary.
2. **Bone sonometer, 1 valid predicate with a design-related recall** — the recalled predicate is still used (only valid predicate); submission states no best-practice-consistent alternative existed, describes performance testing addressing the recall's safety concerns, and discloses the recall + selection narrative in the 510(k) Summary.
3. **Intervertebral fusion device, 2 valid predicates both passing all factors** — tie broken by **duration of safe use** (15 years vs 3 years on market): longer market history = well-established safety profile. Notable: age operates here as a *positive* tiebreaker for an implant — consistent with the §II.B rationale that age cuts the other way for software.

## Program Relationships

| Companion | Division of labor |
|---|---|
| **510(k) Program Guidance (SE)** ([`510k-se-distilled.md`](510k-se-distilled.md)) | Defines the SE decision (flowchart Decisions 1–5), valid-predicate concept, multiple-predicate and reference-device rules, and 510(k) Summary Appendices B–C. This draft adds the *selection* layer among valid predicates and the Summary selection narrative. |
| **Q-Submission Program** ([`qsub-distilled.md`](qsub-distilled.md)) | Pre-Sub is the venue to validate a proposed predicate (and reference-device structure) with FDA before filing — especially where a factor is failed-and-mitigated or the factor evidence is ambiguous. |
| **Emerging Signals guidance** | Supplies the definition of "emerging signal" used by factor C. |
| **Deciding When to Submit a 510(k) for a Change (device + software)** ([`sw-changes-distilled.md`](sw-changes-distilled.md)) | Cited for the premise of factor B: post-clearance device/manufacturing changes can produce effects not captured in premarket review. |
| **Appropriate Use of Voluntary Consensus Standards** | Underpins factor A's "well-established methods" sourcing, with the Recognized Consensus Standards Database and the MDDT program. |
| **QMSR transition** | The draft's § V.D design-controls discussion cites 21 CFR 820.30 with a footnote anticipating the QMSR rule (then proposed, 87 FR 10119). The final rule has since issued (effective February 2, 2026, incorporating ISO 13485:2016); FDA stated it will update this guidance's Part 820 references when finalizing. Read 820.30 design-control references as ISO 13485:2016 § 7.3. |

## Practical Checklist (Submitter Workflow)

1. Build the candidate list from the 510(k) database (trade names, manufacturers, K-numbers, product code / classification regulation); pull each candidate's 510(k) Summary + Indications for Use.
2. Keep only **valid predicates**: same intended use; technological differences raise no different questions of safety and effectiveness; not FDA-removed / adjudicated misbranded or adulterated.
3. Score each valid predicate on the four factors: **A** methods quality (510(k) Summary nonclinical-tests discussion vs recognized standards / current guidance / MDDT / accepted literature — and still-current?); **B** MAUDE + MDR + MedSun search; **C** emerging signals + safety communications search; **D** Medical Device Recalls Database search (design-related recalls specifically).
4. Select the predicate passing the most factors; for ties consider duration of safe market history (especially non-software devices) — for software devices, modern cybersecurity/interoperability/architecture favors recency.
5. If the chosen predicate fails a factor (or no candidate passes): plan subject-device mitigations (design features, performance testing) for each known concern; state in the 510(k) Summary that a best-practice-consistent valid predicate was unavailable, and cover the mitigations in the Performance Data section.
6. Write the **predicate-selection narrative** into the draft 510(k) Summary (and a factor table à la Examples 1/3 in the SE Discussion of the submission).
7. Record the database searches (dates, terms, results) in the design history / regulatory file — the factor table is only as defensible as its evidence trail.
8. Draft caveat: confirm whether this guidance has been finalized (and whether factor wording / Summary expectations changed) before locking submission language.
