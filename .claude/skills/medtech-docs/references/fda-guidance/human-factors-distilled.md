# FDA Guidance — Content of Human Factors Information in Medical Device Marketing Submissions

**Full Title**: Content of Human Factors Information in Medical Device Marketing Submissions — Guidance for Industry and Food and Drug Administration Staff
**Document Date**: May 29, 2026 (final); draft issued December 9, 2022
**Status**: Final (Level 1; Contains Nonbinding Recommendations)
**Document Number**: GUI01500052 (docket FDA-2015-D-4599)
**Issuing Bodies**: CDRH (contact: Human Factors Engineering Team, HFPMET@fda.hhs.gov)
**Supersedes**: Nothing per its own preface — it finalizes the December 9, 2022 revised Level 1 draft of the same title. It is expressly "intended to be used to complement" the 2016 final guidance **"Applying Human Factors and Usability Engineering to Medical Devices"** (the "Human Factors Guidance"), which **remains in force**: the 2016 guidance governs *how* to perform HFE/UE work (process, methods, validation-test design); this 2026 guidance governs *what HF information goes into a marketing submission* and in what structure.
**Operationalization**: FDA anticipates ≥ 60 days to operationalize. For submissions pending at publication or received before **August 1, 2026**, FDA generally does not expect the newly recommended information — but will review it if submitted.
**Full text**: [`source-md/human-factors.md`](source-md/human-factors.md)

## Scope

A **risk-based framework for deciding how much human factors information to include in a marketing submission** (510(k), De Novo, PMA, HDE — combination products excluded; see the combination-product HF Q&A guidance instead). It does **not** tell you how to do HFE/UE (that's the 2016 Human Factors Guidance + IEC 62366-1), and it does **not** decide when a submission is required (that's the device-modifications guidances / 21 CFR 807.81, 814.39, 814.108). Device-specific guidances and special controls take precedence where they exist.

**Key-question TL;DR**: Walk the Figure 1 flowchart (Decision Points A–D) against your use-related risk analysis (URRA) to land in one of three **HF Submission Categories**: **Category 1** — modification touching none of {UI, users, uses, environments, training, labeling} → conclusion + high-level summary only; **Category 2** — no critical tasks (new device) / no new-or-impacted critical tasks (modified device), OR critical tasks exist but a **rationale in lieu of HF validation data** holds (history of use, low UI complexity, risk controls remain effective with objective evidence) → rationale + descriptive sections; **Category 3** — critical tasks plus complexity/novelty/known-use-error history → full HFE/UE report **with human factors validation testing**. One category per submission; multiple modifications are assessed **collectively**.

## The HF Submission Category Framework (§ IV)

### Decision Points (Figure 1 companion text, § IV.A)

```
[A] Modification to an existing device (own 510(k)/PMA/HDE/De Novo,
    or new device leveraging the same/similar UI of one's own
    legally marketed device)?
      NO  → [C]      YES → [B]
[B] Change to any of: user interface · intended users · intended uses ·
    intended use environment(s) · training · labeling?
      NO  → CATEGORY 1      YES → [C]
[C] Per the URRA — new devices: any critical tasks?
    modified devices: new critical tasks introduced, or existing
    critical tasks impacted?
      NO  → CATEGORY 2      YES → [D]
[D] Considering UI history of use, UI complexity, and adequacy of
    existing risk control measures — should HF validation test data
    be submitted?
      NO (rationale in lieu) → CATEGORY 2      YES → CATEGORY 3
```

Key readings per decision point:

- **A** — "Yes" is also available for a *new* device that reuses the same/similar UI of the submitter's own legally marketed device and leverages its HF information (the leverage pattern, Examples A.1/B.3).
- **B** — labeling and training are called out separately in the flowchart but are *subsets of the user interface* per the IEC 62366-1-aligned definition. Any touch on the six surfaces routes onward to C; only a fully clean "no change" lands Category 1.
- **C** — run the URRA on the **final finished device**, not just the delta — impacts can land upstream/downstream of the change. A critical task is "impacted" when the change influences the user's **perception, cognition, or physical interaction**; step-count changes (fewer *or* more steps) count. Cumulative impact across multiple changes in one submission must be considered.
- **D** — the escape valve and its limits: for modified devices with impacted critical tasks, a **rationale in lieu of new HF validation testing** is acceptable when existing risk control measures remain effective — *with objective evidence*. HF validation data are likely needed for complex UIs (programming/monitoring/maintenance, many-step systems) or device types with known use-error history (e.g., infusion pumps). FDA may demand HF validation data even where historically not required when: (i) significant difference vs. similar marketed devices affecting use (novel technological feature, new indications, new environment, new user groups); (ii) a post-market safety signal attributed to use error; (iii) increased severity of possible harm from use error. Unsure whether a rationale will fly → **Pre-Sub**.

### Required content per category (§ IV.B, Table 1 — keyed to § V report sections)

| § V report section | Cat 1 | Cat 2 | Cat 3 |
|---|---|---|---|
| 1. Conclusion + high-level summary (incl. category determination + rationale) | ✓ | ✓ | ✓ |
| 2. Intended users / uses / environments / training; 3. UI description; 4. Known use problems | | ✓ | ✓ |
| 5. Preliminary HFE/UE analyses + evaluations | | | ✓ |
| 6. URRA; 7. Critical-task identification | | | ✓ |
| 8. HF validation testing of final design | | | ✓ |

## Submission-content expectations (§ V — the 8 report sections)

Internal HF documentation must be **maintained under the QMS regardless of what is submitted** (QMSR / ISO 13485:2016 § 7.3, esp. 7.3.10; records producible to FDA investigators under FD&C § 704(e)). Submitted HF information is **summary-level** — raw validation data is not typically included. Cross-referencing other submission sections (device description, labeling) instead of repeating content is explicitly endorsed.

1. **Conclusion + high-level summary** (all categories) — adequacy conclusion ("the UI has been found to be adequately designed for the intended users, uses, and use environments…"), the claimed HF Submission Category **with rationale**, summary of HFE/UE processes, residual-risk discussion with benefit-risk reasoning (ISO 14971-consistent) for why further risk control is not possible/practicable.
2. **Users / uses / environments / training** (Cat 2–3) — distinct user populations and capability differences; operational context; environment characteristics (glare, vibration, noise, activity level); training description (sample materials may be appended); for modified devices, a comparison to the existing device.
3. **UI description** (Cat 2–3) — graphical representation of the full UI; written description; **copy of labeling**; operational-sequence overview (user action → device response); for modified devices a **UI comparison table** (Table 4: modification ID | image existing | image modified | description of change).
4. **Known use problems** (Cat 2–3) — for prior models and similar devices (incl. predicates); state "none known" if applicable; for devices modified *in response to* field use problems, discuss problems and fixes. (MAUDE/TPLC searches are the sample-language pattern.)
5. **Preliminary analyses + formative evaluations** (Cat 3) — methods, key results, design modifications made in response, findings that shaped the validation protocol.
6. **URRA** (Cat 3) — excerpt of the use-related portion of the risk analysis; a living document; Table 2 minimum columns: Task ID (traceable to the risk file and HF validation) | user task (knowledge + performance tasks) | possible use errors | hazardous situation | potential harm | severity | critical task Y/N | risk control measure(s) | validation method for risk-control effectiveness. For modified devices: a **comparative URRA** (Table 3 — existing-device rows plus comparison columns for task description, the six change surfaces, and risk controls) covering at minimum all tasks in use scenarios relevant to the modifications, with an acceptability discussion and rationale if no new HF validation data is claimed.
7. **Critical tasks** (Cat 3) — identification process incl. the severity scale used (e.g., five-level qualitative per ISO 14971/TIR24971, table + reference); list/describe critical tasks (new/impacted ones for modified devices, with rationale where existing risk controls remain acceptable); use scenarios with their critical and non-critical tasks.
8. **HF validation testing** (Cat 3) — test-type rationale (simulated use / actual use / clinical study); environment, participants (number, type), training fidelity vs. real world, critical tasks + use scenarios tested, success definitions, data-collection methods; results (task performance, use errors, close calls, interview feedback); comprehensive analysis of all use errors/problems with real-world harm potential; UI design modifications made in response; benefit-risk discussion of residual use-related risk; **full test protocol + scripts/forms appended**; residual-risk analysis. For modified devices, validation may be limited to the aspects affected by the modification (per the 2016 guidance).

## Examples (§ VI) — the pattern in one table

| Example | Change | Category | Why |
|---|---|---|---|
| A.1 | CADe algorithm improvement, zero UI/labeling/training change | **1** | Decision Point B clean "No" — algorithm-only change with untouched UI (the software-change archetype) |
| A.2 | Internal component change + IFU note | **2** | Labeling changed, but no perception/cognition/physical-interaction influence → no impacted critical tasks |
| A.3 | Font 12→14 pt + proportionally larger screen, same layout/icons | **2** | UI changed but same info, same layout/format; formative data backs "no negative influence" |
| A.4 | Text menus → icons; physical knob → touchscreen slider | **3** | Critical tasks impacted (understandability + physical interaction) + complex UI + new training |
| A.5 | Reprocessing IFU rewrite after infection signal | **3** | Safety-signal-driven labeling change; known use-error history |
| A.6 | Add AR display to surgical navigation (same info as monitors) | **3** | Existing critical tasks now performed through a novel, more complex interface with no user familiarity — even with identical informational content |
| A.7 / A.8 | Indication expansion to pediatric / type-2-diabetes users, no design change | **3** | New user group impacts existing critical tasks; adequacy of existing risk controls not apparent for the new population; severity may increase |
| B.1 | Reservoir volume change, no dosing change | **2** | Critical tasks examined, none impacted |
| B.2 | Monochrome PDA programmer → color touchscreen tablet | **3** | Impacted dose-calc task, negative transfer, known use-error history |
| B.3 | New PMA reusing own approved delivery system UI unchanged | **1** | Leverage pattern: own prior HF information carries the unchanged UI |
| C.1 | New PMA, conventional delivery-system design | **2** | Critical tasks exist, but no novel features, trained physicians, simulated-use support |
| C.2 | Fingertip spot-check oximeter, no alarms/interpretation | **2** | No critical tasks at all (no serious-harm pathway) |
| C.3 | Injection device with unique UI feature | **3** | Novel UI feature → different risk profile than marketed equivalents |
| C.4 | Blood lancet w/ auto-retract, competitor predicate | **2** | Critical tasks exist but low-complexity, long-marketed UI pattern + equivalent risk controls |
| C.5 | Bone plate/screw system, competitor predicate | **2** | Surgeon users highly trained; routine workflows (planning, size selection, implantation); no novel/complex UI |
| C.6 | Guided ultrasound for expert + **non-expert** users | **3** | Non-expert user group lacks UI familiarity; inadequate imaging could mask life-threatening conditions; special controls demand usability evidence |

Recurring levers across the examples: **(1)** does the change influence perception/cognition/physical interaction; **(2)** user-group expansions impact critical tasks *without any design change*; **(3)** special controls can independently force usability evidence (21 CFR 876.1520, 862.1355, 862.1356, 892.2100 cited); **(4)** professional-user familiarity + established UI patterns is the load-bearing Category 2 rationale for surgical hardware (C.5); **(5)** novel interaction modalities (AR, unique UI features) route to Category 3 even when informational content is unchanged (A.6).

## Appendices

- **Appendix A** (Cat 1): one-section report outline + sample language — conclusion, category rationale, why the six surfaces are unaffected, leveraged prior HFE/UE evaluations (cross-reference by submission/section; no resubmission of previously reviewed materials).
- **Appendix B** (Cat 2): four-section report outline (conclusion/rationale, users-uses-environments-training, UI description, known use problems) + two sample reports (C.4, C.5) showing how brief a Category 2 report can be — heavy use of cross-references to the device description, plus a MAUDE/TPLC known-use-problem search.
- **Appendix C** (Cat 3): full eight-section HFE/UE report outline (the de facto table of contents for an HF validation package).

## Program Relationships

| Companion | Division of labor |
|---|---|
| **Applying Human Factors and Usability Engineering to Medical Devices** (2016, in force) | The *process* guidance — how to do HFE/UE: task analysis, formative work, validation-test design, known-use-problem identification (§ 6.2), residual-risk appendix. This 2026 guidance decides *what subset of the output goes into the submission*. |
| **IEC 62366-1:2015+AMD1:2020 / ISO 14971:2019 + TIR24971** | Definition sources (UI incl. labeling + training; harm/hazard/risk terms; benefit-risk; severity scales). HFE/UE per 62366-1 produces the URRA-feeding artifacts; "human factors validation testing" ≈ summative evaluation, but FDA flags that some "summative" definitions omit essential components of its definition. |
| **Device-modifications guidances** (sw-changes + hardware companion, PMA-supplement guidance) | Decide **whether** a submission is required. This guidance engages only after that answer is yes, and explicitly does not interpret it. |
| **Q-Submission Program** | Pre-Sub is the named route when unsure whether a Category 2 rationale will be accepted (Decision Point C/D judgment calls). |
| **PCCP guidances** | Not cited in this guidance, but the interaction matters: changes implemented under an authorized PCCP never reach a new marketing submission, so the HF Submission Category question never arises for them — the HF evidence lives in the PCCP's Modification Protocol instead. Any out-of-PCCP change that does require a new submission walks Figure 1 like any other modification (Decision Point A = yes, own device). |
| **Special 510(k) Program** | Orthogonal axes: Special vs. Traditional picks the 510(k) *type*; Figure 1 picks the *HF content*. A UI change riding a Special 510(k) still needs its HF Submission Category determination, and a Category 3 outcome (HF validation data) pressures the Special's summary-format constraint — Category 1/2 outcomes (statement or rationale) are naturally summary-reviewable. |
| **Voluntary consensus standards guidance** | Governs declarations of conformity for the standards referenced here. |

## QMSR Note

The guidance is QMSR-native (issued after the February 2, 2026 effective date): design V&V/change-control obligations are cited as 21 CFR 820.10(c) **incorporating ISO 13485:2016 § 7.3 by reference** (89 FR 7496), with record-keeping per § 7.3.10. No 820.30 vocabulary appears.

## Practical Checklist (Submitter Self-Assessment)

1. Maintain the URRA as a living document in the risk file (Table 2 columns; Task IDs traceable to the risk-management file and HF validation evidence) — submitted or not, FDA can inspect it.
2. At change time, walk A→B→C→D **on the finished device, considering all changes in the submission collectively**; record the category determination and per-decision-point reasoning — that reasoning *is* the § V Section 1 content.
3. Category 1: write the statement + leveraged-evaluation cross-references (submission + section numbers). Don't resubmit previously reviewed HF materials.
4. Category 2: write the rationale against the specific "No" (no critical tasks vs. data-not-needed), supported by comparative analyses (labeling comparison, comparative task analysis, physical comparison), formative data, known-use-problem search, and — where critical tasks are impacted but controls unchanged — **objective evidence the controls remain effective**.
5. Category 3: assemble the eight-section HFE/UE report per Appendix C; append the full validation protocol + scripts/forms; include comparative URRA + UI comparison table for modifications.
6. Pressure-test borderline Category 2 rationales in a Pre-Sub before filing.
7. Filing before ~August 1, 2026: legacy expectations generally apply; after: structure HF content to this guidance.
