# FDA Guidance — The Special 510(k) Program

**Full Title**: The Special 510(k) Program — Guidance for Industry and Food and Drug Administration Staff
**Document Date**: September 13, 2019 (final); draft issued September 28, 2018
**Status**: Final (Contains Nonbinding Recommendations)
**PDF Source**: https://www.fda.gov/media/116418/download (document number 18008)
**Issuing Bodies**: CDRH, CBER
**Supersedes**: The Special 510(k) content of "The New 510(k) Paradigm — Alternate Approaches to Demonstrating Substantial Equivalence in Premarket Notifications" (March 20, 1998)
**Full text**: [`source-md/special-510k.md`](source-md/special-510k.md)

## Scope

This guidance describes an **optional 510(k) submission type** for certain well-defined modifications where a manufacturer modifies **its own legally marketed device** and design control procedures produce reliable results that can form the basis for substantial equivalence (SE). It does not change *whether* a 510(k) is required — that question belongs to the device-modifications guidances ("Deciding When to Submit a 510(k) for a Change to an Existing Device" and its software companion). Once a new 510(k) is determined to be required, this guidance decides **which kind** of 510(k) can carry it.

**Key-question TL;DR**: A change to an existing device may ride a Special 510(k) when all three hold: (1) the submitter is the manufacturer legally authorized to market the existing device; (2) performance data are unnecessary, or **well-established methods** are available to evaluate the change; and (3) all performance data needed to support SE can be reviewed in a **summary or risk analysis format** (no complete test reports). FDA's goal is review within **30 days** of receipt. If FDA disagrees on any criterion, the submission is **converted to a Traditional 510(k)** — which often triggers RTA, since a Special lacks the complete test reports a Traditional expects.

## Section-by-Section Distillation

### I–II. Introduction & Background

- Established 1998 under the New 510(k) Paradigm; this 2019 final restates and **broadens** the program.
- Leverage point: design controls (21 CFR 820.30, in effect since June 1, 1997). FDA relies on its previous review of the predicate's detailed information plus the manufacturer's risk analysis and verification/validation under design controls, instead of re-reviewing complete data.
- Review goal: **30 days** of receipt by the Document Control Center (vs. the 90-day statutory clock under FD&C § 510(n)(1)).
- **Major policy shift from the 1998 program**: eligibility is *no longer* gated on whether the change affects the **intended use** or alters the **fundamental scientific technology**. FDA "no longer intends to focus on" those factors; instead it focuses on whether the **evaluation methods are well-established** and whether results are **reviewable in summary or risk-analysis format**. Certain indications-for-use and labeling changes may consequently now be made via Special 510(k). (In practice, intended-use-altering changes still usually fail the method/summary tests — e.g., they need clinical data — so they route Traditional anyway, but the exclusion is no longer per-se.)
- Special 510(k)s remain subject to the standard 510(k) content/format requirements (21 CFR 807.87, 807.90, 807.92–.94).

### III. The Special 510(k) Program — Eligibility Framework

Entry condition: the manufacturer has already determined (per 21 CFR 807.81(a)(3) and the device-modifications guidances) that the change likely requires a new 510(k). Then the **Figure 1 flowchart** asks four questions:

```
[A] Change to the manufacturer's OWN legally marketed device?
      NO → Traditional/Abbreviated
[B] Performance data needed to evaluate the change?
      NO → Special 510(k) OK (with rationale that no data are necessary)
[C] Well-established method available to evaluate the change?
      NO → Traditional/Abbreviated
[D] Can ALL data needed for SE be reviewed in summary / risk-analysis format?
      NO → Traditional/Abbreviated
      YES → Special 510(k) (subject to § III.E additional considerations)
```

**A. Own device** — The program relies on FDA's prior review of the submitter's predicate; third parties modifying someone else's device are out (converted to Traditional). If the predicate 510(k) was cleared under a different name, include a statement affirming the submitter is the manufacturer legally authorized to market the predicate.

**B. Performance data needed?** — Decided under the manufacturer's design control procedures (21 CFR 820.30(i)). Some changes need no data (e.g., relabeling to "MR Unsafe" rests on scientific rationale only) — those may be submitted as a Special with a clear no-data-necessary rationale. If FDA disagrees, it continues through C–E before considering conversion.

**C. Well-established methods** — Methods "established for evaluation of the device, device type, or scientific topic area, and validated according to scientific principles." Recognized sources:
- The submitter's own methods/protocols/acceptance criteria from the previously cleared 510(k), applied unchanged;
- Methods in an FDA-recognized voluntary consensus standard or FDA guidance;
- Qualified Medical Device Development Tools (MDDTs);
- Widely available/accepted public-domain or literature methods, or methods FDA previously accepted in the submitter's own 510(k), De Novo, or PMA.

Minor deviations from a well-established method may be acceptable; **significant protocol or acceptance-criteria deviations disqualify**. Uncertain? Use the Q-Submission (Pre-Sub) process. Methods relying on **clinical studies or animal data** are typically NOT well-established for this purpose (methodologies/endpoints vary and can't be summarized). Notably for software: "Traditional 510(k)s often identify the verification and validation approaches that are used for software such that **many subsequent software changes may occur under a Special 510(k)**."

**D. Summary / risk-analysis reviewability** — Results must survive summarization without losing SE-relevant information. **Complete test reports should not be submitted.** Data cannot be summarized when the SE determination depends on FDA's interpretation of underlying data — images, raw graphs, line-item data (e.g., fatigue-to-failure failure-mode image review). Limited representative images (e.g., radiopacity) are acceptable. Acceptable formats include: summary table of design-control activities; redlined SRS/design documentation; risk-management documentation (e.g., DFMEA) plus a V&V summary. The summary should give, per change: V&V activities, why the methods fit the change, acceptance criteria, deviations from prior methods, and results.

**E. Additional considerations (routes OUT even if A–D pass)**:
- Evaluation spans **more than three scientific disciplines**;
- Bundled multiple devices with unrelated changes;
- A recent violative QS inspection with design-control observations relevant to the change (rebuttable with a rationale);
- Anticipated complete-test-report scenarios: indications changes supported by clinical/animal/cadaver data; novel sterilization methods; initial MR Conditional labeling (or significant deviations from the original MR test methods); single-use → reusable needing reprocessing-validation or human-factors data; ISO 10993-18 chemical characterization / ISO 10993-17 toxicological risk assessment for biocompatibility;
- Reprocessed SUDs requiring validation data under FD&C § 510(o); reusable devices on the § 510(q) reprocessing-validation list.

### Conversion to Traditional

If any criterion fails, FDA converts the Special to a Traditional 510(k) (with management concurrence) and explains the reason in terms of the § III factors. Conversion is costly: a Special lacks complete test reports, so the converted submission **frequently fails RTA** as a Traditional. If conversion happens after acceptance for substantive review, the clock continues into the 90-day statutory deadline and MDUFA goals. Practical takeaway: self-assess the four questions honestly before choosing the Special route.

### Appendix A. Content of a Special 510(k)

- Coversheet identifying the submission as **"Special 510(k): Device Modification"**;
- Name of the existing device + its cleared 510(k) number;
- 21 CFR 807.87 content: detailed description of the change(s) (explicitly state what is *unchanged*); tabular modified-vs-cleared comparison; clean **and redlined** copies of updated documents (labeling, risk analysis); and other since-clearance changes that did not themselves require a 510(k);
- A **concise summary of design control activities** (FDA treats this as "appropriate supporting data" under 21 CFR 807.87(g); the risk analysis itself may be attached in lieu of a new table): risk-analysis method + results, the change(s), all associated risks including new ones, and risk control measures;
- Risk-analysis-driven identification of V&V activities with **summary of test methods, acceptance criteria, and results** (descriptive statistics — mean/SD/range — for quantitative results; deviations justified). For non-standardized methods: reference the prior protocol and identify any differences. For recognized-standard methods: declaration of conformity (with ISO/IEC 17050-2 supporting documentation) or, without a DOC, a description of methods/deviations/options/acceptance criteria/results;
- Indications for Use form (FDA 3881);
- A **signed design-control statement** by the designated individual(s): all required V&V was performed and predetermined acceptance criteria were met; and the submitter complies (and is not in violation of) 21 CFR 820.30, records available on request.

### Appendix B. Examples (15)

Pattern across the examples: changes evaluated with the **same protocols/acceptance criteria as the predicate submission**, recognized consensus standards, or FDA-guidance methods, with pass/fail- or statistics-summarizable results → Special OK (B.4 monitor-tube compatibility, B.5 home-use environment via 60601-series, B.6 adding gamma sterilization, B.7 MR coil channel count, B.8 IVD strain reactivity, B.10 implant size change, B.11–B.15 IVD design/labeling/threshold changes). Changes needing **clinical evidence or novel methods** → not Special (B.1 adding lung-nodule CAD feature + quantitative claims, B.2 adding wireless control, B.3 disease-specific indication). Changes where SE depends on FDA's interpretation of underlying data → not Special (B.9 initial MR Conditional labeling) — even when consensus-standard methods exist for every test.

### Appendix C. Design-control summary examples

Two formats from cleared Specials: (C.1) fault-tree-based risk analysis (ISO 14971) plus a 5-column table — Device Change | Risks | V&V Method(s) | Acceptance Criteria | Summary of Results — with "protocol and acceptance criteria same as Kxxxxxx without any deviations" annotations; (C.2) DFMEA-based equivalent covering biocompatibility-by-rationale, sterilization validation (ISO 11137-1/VDmax), dimensional verification, and simulated-use validation.

## Program Relationships

| Companion | Division of labor |
|---|---|
| **Deciding When to Submit a 510(k) for a Change to an Existing Device** + software companion ([`sw-changes-distilled.md`](sw-changes-distilled.md)) | Decide **IF** a new 510(k) is required. The Special program assumes that answer is yes and decides **WHICH KIND**. |
| **Traditional 510(k)** ([`510k-se-distilled.md`](510k-se-distilled.md)) | Default type; complete test data; the conversion target when Special criteria fail. |
| **Abbreviated 510(k)** (The Abbreviated 510(k) Program, 2019 — the other half of the superseded New 510(k) Paradigm) | Relies on guidance/special controls/consensus-standard conformity with summary reports; standard review clock; not restricted to the submitter's own device. |
| **PCCP guidances** ([`pccp-aiml-distilled.md`](pccp-aiml-distilled.md), [`pccp-general-distilled.md`](pccp-general-distilled.md)) | Changes implemented in conformance with an authorized PCCP need **no new 510(k) at all** — the Special question never arises. **Introducing** a PCCP requires a **Traditional or Abbreviated** 510(k) (the AI/ML PCCP final § V.B submission-type list deliberately omits Special). **Modifying an already-authorized PCCP** is different: per the AI/ML PCCP final § V.E, "a special 510(k) submission may be appropriate to modify a PCCP where the modifications to a PCCP comprise changes to the manufacturer's own device and PCCP and where well-established methods are available to evaluate the change to the PCCP." |
| **Q-Submission Program** ([`qsub-distilled.md`](qsub-distilled.md)) | Pre-Sub feedback on whether a method deviation is "significant" or a planned change is Special-eligible. |
| **Refuse to Accept Policy for 510(k)s** | Acceptance review; summary-format failures are intended to be caught (and conversion decided) at the RTA stage. |

## QMSR Note (Posted-Copy Banner)

The FDA-posted copy carries a transition note: 21 CFR part 820 was amended February 2, 2024 (89 FR 7496) and the **Quality Management System Regulation (QMSR)** took effect **February 2, 2026**, incorporating **ISO 13485:2016** by reference. The QMSR no longer uses the terms "Design Controls" / "Design Validation"; their elements now live in **ISO 13485:2016 Clause 7.3** and subclauses. Read this guidance's references to 21 CFR 820.30 design controls (risk analysis, design verification/validation, design change control, the Appendix A signed design-control statement) as mapping to the corresponding ISO 13485:2016 § 7.3 requirements (7.3.6 verification, 7.3.7 validation, 7.3.9 control of design and development changes).

## Practical Checklist (Manufacturer Self-Assessment)

1. Did the modifications guidance(s) say a new 510(k) is needed? (If no → document under QMS; if covered by an authorized PCCP → no submission.)
2. Is this our own legally marketed device (510(k)-cleared, preamendments, reclassified, or granted De Novo)?
3. Are the evaluation methods the same protocols/acceptance criteria FDA already saw — or recognized standards/guidance/MDDT methods — with at most minor deviations?
4. Can every result be reviewed as summaries, tables, descriptive statistics, or a risk analysis — with no images/raw-data interpretation by FDA?
5. ≤ 3 scientific disciplines involved, single device, no relevant open design-control inspection findings, and none of the § III.E complete-test-report scenarios?
6. If all yes → Special 510(k) ("Special 510(k): Device Modification" coversheet, Appendix A content). If any doubt → Pre-Sub, or file Traditional and avoid the conversion/RTA penalty.
