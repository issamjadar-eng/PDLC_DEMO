# Full filed PCCP — document structure at filing depth

🔎 **Finding aid.** This encodes the *structure and depth* FDA expects in a **filed** Predetermined Change Control Plan (PCCP) — the one that rides inside a 510(k)/De Novo, not the abbreviated PCCP *summary* used for a Q-Sub. Use it when scaffolding or authoring a full PCCP (`scaffold pccp`, or a hand-authored `pccp-plan.md`). Cite the guidance itself (rung 1/rung 3), not this file.

**Governing guidance** (verify current status + section numbers against the byte-correct source before transmission — see the `/reference-audit` gate):
- **AI/ML PCCP final** — *Marketing Submission Recommendations for a Predetermined Change Control Plan for AI-Enabled Device Software Functions* (Dec 2024, updated Aug 2025). Structure lives in **§ VI / § VII / § VIII** + **Appendix A** (per-sub-component content elements) + **Appendix B** (worked device examples).
- **General PCCP draft** — *Predetermined Change Control Plans for Medical Devices* (Aug 2024). Mirrors the same shape under its own lettering (Description § VII.A, Modification Protocol § VII.B, Traceability § VII.C, Impact Assessment § VII.D). **Draft** — flag draft-reliance for any non-AI change track.

> **Numbering caution.** The four Modification-Protocol sub-components in the AI/ML final are **numbered (1)–(4)** under § VII.B, with the Statistical Analysis Plan at **§ VII(3)(c)** and performance targets at **§ VII(3)(d)**. Some distilled/applicability layers re-letter these A–D — do **not** inherit that lettering into a filed body; verify against the byte-correct source-md.

---

## The three components (+ the required fourth artifact)

A filed PCCP is **not** three narrative paragraphs — it is three components worked **per modification**, plus a traceability table binding them:

| Component | Guidance | Altitude | The filing-depth test |
|-----------|----------|----------|-----------------------|
| **1. Description of Modifications** | AI/ML § VI · General § VII.A | **per modification** | Each modification has its own entry with rationale + post-modification performance specifications + required metadata. |
| **2. Modification Protocol** | AI/ML § VII.B(1)–(4) · General § VII.B | **per modification** | Each modification has a full four-sub-component protocol (not a table row). |
| **2b. Traceability table (Table 1)** | AI/ML § VII.C · General § VII.C | **whole set** | **Required.** A matrix mapping each modification → the specific Data-Management / Re-Training / Performance-Evaluation / Update-Procedure method that governs it. |
| **3. Impact Assessment** | AI/ML § VIII · General § VII.D | **per modification + set-level** | Each modification's benefit-risk (incl. bias) worked, plus set-level interaction + cumulative impact **methodology with pre-specified thresholds**. |

The single most common "reads like a summary, not a filed PCCP" failure is carrying most modifications at **one-row-in-a-table** altitude while working only one or two exemplars. A filed PCCP needs each authorized modification worked to depth **or** the set deliberately narrowed (see the scope-vs-effort note below).

---

## Component 1 — Description of Modifications (per modification)

Each modification entry states, at minimum:
- **Specific change** + **specific rationale** (why this change).
- **Post-modification performance specifications** — the concrete characteristics/performance the device *will have* after the change (§ VI.B). Not deferred entirely to the performance table.
- **Required metadata**: implementation mode (automatic / manual / combination); **global vs. local** (and, if local, the local factors); expected update frequency; labeling sections impacted.
- An explicit statement the modification stays **within intended use / indications** and preserves substantial equivalence.
- An **explicit exclusions** list at set level (what is *not* pre-authorized) — mirror it in the change-routing tree.

## Component 2 — Modification Protocol, four sub-components (per modification)

> **Appendix A is a question-checklist, not a section outline.** The AI/ML final guidance Appendix A decomposes the four sub-components into lettered "questions for consideration" (Data Management a–d, Re-Training a–b, Performance Evaluation a–e, Update Procedures a–d). Author each sub-component by **answering the applicable questions** — with an explicit "not applicable + why" for the rest — not by restating the questions as headings or padding with standards text. FDA states the list is developing, non-exhaustive, and non-mandatory: demonstrate coverage against it; depth scales with each modification's risk.

> **Methods-comparison statement (Appendix A 4.a.1; § VII.B intro) — commonly omitted.** Each Modification Protocol must state how its methods are **similar to or different from** the V&V methods used **elsewhere in the same submission**, and **justify any difference**. A protocol that re-executes the cleared V&V says so; one that uses a subset justifies the subset; one that introduces a **genuinely new method** (e.g., a new reader study for a bounded measurement addition) owes an explicit justification. Author a short per-shape paragraph (re-executed / justified-subset / new-method).

**(1) Data Management Practices** (§ VII.B(1); Appendix A). A data-management *specification*, not a paragraph: data-collection protocol; inclusion/exclusion criteria; **representativeness / covariate plan** (sex, age, race/ethnicity, disease severity, acquisition conditions — characterized per dataset); reference-standard / ground-truth determination protocol (clinician-grading method, qualifications, equivocal-case handling, reference-standard uncertainty); **train / tune / test independence + sequestration procedures** (the procedures, not the adjective); per-dataset descriptive statistics; QA process; multi-reader sub-study for ground-truth-variable tasks. *(State "Not applicable" explicitly for a change that alters no data input or computation — e.g., a pure UI/visualization change; a computation-logic change is NOT N/A.)*
> **Don't stop at collection — the data-governance "back half" is required and commonly omitted** (Appendix A 1.b, "assurance of data quality"). Authors cover collection / representativeness / sequestration well and go silent on: data **storage, retention, and access control** (version-controlled, role-based, retention-scheduled, each dataset version traceable to the retraining record that consumed it); the ongoing data-**QA process** (ingest consistency/completeness/integrity checks; annotation-issue adjudication records); **currency / obsolete-data removal** (superseded acquisitions removed from training pools, removal recorded); **anti-tampering controls on the sequestered test set specifically** (checksummed, access-logged, single-unlock discipline — this is what *keeps* the sequestration real, so tie it to the § VII.B(1) sequestration procedures, not a floating control); and a **human-subject-protections** statement (retrospective de-identified data; IRB / consent determinations; 21 CFR 50/56 + 45 CFR 46 applicability assessed per source). Author these once as a shared "Data governance" block and reference it from each modification's sub-component (1).

**(2) Re-Training / Update Methodology** (§ VII.B(2)). Which processing steps change (preprocessing / architecture / coefficients / hyperparameters — with rationale if architecture changes, which usually routes *out* of the PCCP); **explicit update triggers** (data-volume threshold, drift detection, performance-deviation, fixed cadence, or combination); overfitting + bias-from-retraining mitigations; QMS change-control linkage.

**(3) Performance Evaluation** (§ VII.B(3)) — *the sub-component authors most often under-build.* It must contain a **pre-specified Statistical Analysis Plan** covering the guidance's own questions:

| SAP element | Guidance anchor | Note |
|-------------|-----------------|------|
| Primary / secondary endpoints + hypotheses | § VII(3)(c) | Improvement-vs-non-inferiority stated as a testable hypothesis |
| Comparison basis: vs **original cleared** AND **last-authorized** version | § VII(3)(c)(1) | The dual comparison — catches drift accumulating across successive modifications |
| Non-inferiority / equivalence **margin + its clinical justification** | § VII(3)(d)(2) | A margin *number* without a clinical-justification paragraph is non-conforming |
| Sample-size determination **method** | § VII(3)(c)(5) | Power, α, assumed effect size/SD, resulting n — the *method* is filing-complete even where constants defer |
| **Analysis population** (e.g., intention-to-diagnose vs per-protocol) | § VII(3)(c)(6) | Frequently omitted |
| **Missing-data + outlier handling** | § VII(3)(c)(8) | Frequently omitted |
| Reference-standard-variability treatment | § VII(3)(c)(7) | Imperfect-reference-standard / correlated-error handling |
| Subgroup / high-risk-subpopulation analysis | § VII(3)(c)(2) | Acceptance per subgroup, not only aggregate |
| Sensitivity/specificity trade-off protection | § VII(3)(c)(4) | A gain in one metric must not silently degrade the other |
| Metrics + **challenging/edge cases** to evaluate | § VII(3)(b)(3–5) | Name the metrics and the hard cases |
| Acceptance criteria vs the **authorized version's** criteria | § VII(3)(d)(1) | |
| Additional-testing determination (bench/standalone vs clinical/usability/integrated-hardware) | § VII(3)(e) | The per-category "is bench enough?" decision |
| **Unresolvable-failure statement** (verbatim pattern) | § VII.B(3) | Failure recorded → modification **NOT** implemented; root-cause may permit re-test |

**Key distinction — methodology-complete vs value-locked.** The SAP *methodology* (endpoints, hypotheses, margin *justification*, sample-size *method*, analysis population, missing-data handling, reference-standard protocol) must be **filled now** — none of it requires a locked number. Only the specific numeric constants (margins, n, thresholds) legitimately defer to design transfer (and, where put to FDA, to Q-Sub feedback). "Light on details" is almost always a *methodology* gap, not a *numbers* gap — do not fix it by inventing more numbers.

**Verification / Validation split (from the authorized exemplars).** The strong AI exemplars structure Performance Evaluation as two named halves — a copyable backbone: **Verification** = peer code review + unit testing + quantitative metrics (segmentation: Dice, HD95, AUC, Precision, Recall) vs a **frozen original-submission (locked baseline) model**, showing equivalence-or-improvement; **Validation** = multi-reviewer (≥ 3) qualitative comparison on fixed independent intended-use-population datasets + a quantitative test against a **permanently-frozen expert reference standard held constant across all versions** + a Hazard-Analysis re-review for new bias/limitations. See [`pccp-authorized-exemplars.md`](pccp-authorized-exemplars.md) (K250369 Axial3D; K241561 MammoScreen) for the worked patterns and quantified-criteria calibration.

**(4) Update Procedures** (§ VII.B(4)). Software V&V plan incl. **integrated-environment testing** + impact on other device functions; deployment decision criteria / timeline / mechanism; global vs. local deployment; **cybersecurity** risk management for the update; user communication / transparency / labeling-review-before-update / bias disclosure; labeling + **UDI** update; **real-world performance monitoring plan** with subpopulation tracking; **rollback criteria + a mechanism tested at design transfer** (not deferred to first incident).
> **Baseline labeling disclosure — a standing, not per-modification, commitment** (AI/ML § V.C; § 515C(b)(3)). The device labeling must state, from clearance, that the device **has an authorized PCCP**, **incorporates machine learning**, and that **authorized updates may modify its performance, inputs, or use** — independent of any specific modification. Authors capture the *per-modification* labeling impact and forget this standing baseline disclosure. Commit to it once (Description-of-Modifications metadata or a shared update-procedure provision) and mirror it in the labeling deliverable. Also easily missed: a **user-visible in-product version display** (Appendix A 4.c.4), the **option to review updated labeling before an update takes effect** (a *transmitted* commitment that must survive into the filed plan — see the reconciliation gate below), and a **reasoned N/A** for re-running the model on a user's prior data (Appendix A 4.c.9) where it does not apply.

> **Post-market drift monitoring is the top exemplary-vs-adequate differentiator.** In a review of 34 authorized radiology PCCPs, only ~3 carried any post-market surveillance and only 1 referenced real-time drift updates — so including one is the cheapest way to land in the top documentation tier. The copyable pattern (K241561 MammoScreen): a **live Reference Distribution of model output**, real-world comparison against it, and **drift alerts that escalate to a field-safety notice / MDR**. The Dec-2024 final guidance also shifts the expectation from ad-hoc "real-world monitoring" to a **formal ISO 13485-aligned post-market surveillance plan**. Treat the device-monitoring plan + rollback criteria as a required, worked protocol element — not an afterthought.

## Component 3 — Impact Assessment (per modification + set-level)

The five/six elements (§ VIII):
1. Device with **each** modification implemented individually vs. the unmodified device.
2. **Benefits and risks — including harm and unintended bias — of each individual modification.** Worked benefit-risk determination per modification: benefit named; risks (incl. bias, per subgroup) enumerated; acceptability conclusion in light of benefit (ISO 14971 § 7.4 / § 8).
3. How the Modification Protocol's V&V continues to reasonably ensure safety/effectiveness (per modification).
4. **Interaction between modifications** — a pairwise screen across the set, with material couplings pulled out and analyzed (not one worked pair).
5. **Cumulative impact** — the *method* by which stacked modifications are re-evaluated against **pre-specified aggregate thresholds** (e.g., stacked-retrain count, aggregate drift budget, accumulated subgroup-delta ceiling), and against which baseline. A cumulative-impact *methodology at filing time*, not a promise to look later.
6. Impact on **overall device functionality** incl. non-AI functions, infrastructure, and (for a multi-function device) the "other functions" boundary.
- **Cross-references** into the submission's risk assessment / MP sections must resolve to *populated* content, not placeholders.

The residual-risk **acceptance gate** (ISO 14971 § 7.3 per-hazard, § 7.5 risks-from-controls, § 8 overall/cumulative) should be worked as a **before/after re-scoring** on the project's risk matrix for at least the exemplar modifications — a worked determination, not only a method statement — and the modification's hazard set traced to the device hazard register.

---

## Reconcile the filed PCCP against the transmitted pre-submission (the filed document is the side that moves)

When a filed PCCP/510(k) follows a **transmitted** Q-Submission, the Q-Sub is the **anchor**: it has been sent to FDA and FDA's feedback attaches to it. So in any divergence between the transmitted Q-Sub and the later filed document, **the filed document is the side that must move** — never the reverse. A filed PCCP that quietly under-delivers or contradicts a position the Q-Sub already stated is the sharpest, most expensive defect this skill exists to prevent (it becomes a deficiency letter after transmission, not a cheap edit before it).

**Run this reconciliation before a filed PCCP/510(k) is declared done.** Walk the transmitted Q-Sub set — the PCCP summary, the questions-for-FDA, and every supporting brief — and check three things:

1. **Every transmitted commitment has a home in the filed document.** A commitment made in the Q-Sub (a monitoring dimension, a gate element, a routing sub-pathway, a dual-comparison rule, a per-category table, a cross-item propagation rule, an expedited security-patch pathway) that has **no corresponding content in the plan** is a *weaker-in-filed* under-delivery — a defect, even though each document is internally clean. This is invisible to a single-document lint; only the pairwise walk catches it.
2. **No filed statement contradicts, narrows, or broadens a transmitted position.** A scope boundary that got **narrower** in the filed doc (e.g., an exclusion that dropped a clause) **broadens the device's perimeter** beyond what was presented — a contradiction in the direction that matters. **Stricter-in-filed is fine** (you may add rigor); **weaker-in-filed is a defect** (you dropped a commitment). A transmitted provision silently omitted (e.g., "labeling review before update") is a *reverse regression* — FDA has already seen it; the plan must re-absorb it.
3. **Never assert an FDA agreement or precedent that has not occurred.** A filed posture must match the **transmitted** posture unless FDA actually changed it. Writing "clinical evidence per FDA agreement" for something only *proposed* (bench-first, pending an FDA question) **fabricates a regulatory agreement and inverts the filed posture** — a blocker. Keep the transmitted framing: "evidence tier per FDA's response — bench proposed; clinical if FDA expects." A demonstrative *"assume FDA agrees"* working premise (used to build depth) is **internal only** — it must never surface in a filed claim as "per FDA agreement."

Direction rule in one line: **the transmitted document sets the floor; the filed document may exceed it but may not fall below it, contradict it, or claim an agreement that was only requested.**

## Two distinct tables — do not conflate them

A filed PCCP produces **two** tables, for two audiences:

1. **Internal Traceability table (Table 1, § VII.C — required).** Maps each modification → the specific Data-Management / Re-Training / Performance-Evaluation / Update-Procedure method that governs it. Binds Description to Protocol; lives inside the filed PCCP body.
2. **Public 510(k)/De Novo-summary table (General PCCP § IX).** A *distinct*, public-facing disclosure that lands in the **510(k) summary document** (not inside the PCCP body). Columns: **`Planned Modifications | Test Methods and Validation Activities | Communication to users, as needed`**. The test-methods cell is expected to **name recognized consensus standards + FDA guidances** per modification. FDA's worked row for "add a new wireless card" cites ANSI/AAMI ES60601-1, IEC 60601-1-2/-1-8/-4-2, AIM 7351731, IEEE/ANSI C63.27, AAMI TIR69 + the EMC and RF-Wireless guidances; the comms cell reads "Labeling will be updated in accordance with the authorized PCCP …". A good submission surfaces the PCCP in the **cover letter and table of contents**, and states — at a "level of detail that permits understanding of the specific modifications" — the planned modifications, testing methods, performance requirements, and change-communication means. In the receiving **510(k) Summary** this is a dedicated PCCP section (the `templates/510k/510k-summary.md` profile carries a conditional § 8) — and it must be a **tracked required piece in the composition manifest** so it cannot fall through at assembly time. This is a **cross-filing handoff**: the requirement is authored in the PCCP but *delivered* in the 510(k) Summary, so both the PCCP depth contract and the 510(k) profile must carry it — a fix applied only to the PCCP body leaves the receiving document blind.

*(Caveat: the General PCCP guidance is the Aug-2024 **draft**; the § IX sample table was dropped in the local source-md conversion — verify against the byte-correct source PDF before any verbatim citation.)*

## Strong-vs-weak attributes & weak-PCCP red flags

Distilled from authorized-filing teardowns + former-FDA-reviewer commentary (Innolitics, Medcrypt, FDA Law Blog, RAPS) — pair each with the underlying FDA final-guidance section (cite both). See [`pccp-authorized-exemplars.md`](pccp-authorized-exemplars.md) for the K-number evidence.

**Strong-PCCP attributes:** a *limited* number of *specific* enumerated modifications; **independent/separable** modifications documented in separable units (so FDA can strike one without rejecting the whole plan); every change demonstrably within the cleared intended use / indications; **quantitative acceptance criteria with confidence bounds** and named metrics (not "performance will be maintained"); per-modification-category V&V (not one generic protocol); validation data independent from development data; explicit re-training triggers/guardrails; an affirmative **unresolvable-failure → do-not-implement + rollback** statement; an Impact Assessment covering **safety, effectiveness AND security together** (name cyber/secure-patching + interoperability risk when the device ingests external data); labeling/UDI/version + user-communication update procedures; a **formal post-market surveillance/drift plan**; affirmative transparency of training/test data source + size + subgroup performance; the PCCP filed in the **original** submission and surfaced in the cover letter/TOC; a compliant QMS/design-control posture (FDA may withhold PCCP authorization on QSR non-compliance alone).

**Weak-PCCP red flags (a QA/lint pass can run these):** (1) "updates as needed" / open-ended change lists with no enumerated categories; (2) subjective acceptance criteria lacking quantitative thresholds + CIs; (3) one generic V&V protocol spanning all change types; (4) no rollback / unresolvable-failure statement; (5) security treated as out-of-scope or "handled elsewhere"; (6) any change touching intended use / indications / new patient population / removed contraindication; (7) training/test data provenance, size, subgroup performance not stated; (8) PCCP not referenced in the cover letter/TOC; (9) modifications not separably documented; (10) a PCCP bolted on only after an FDA additional-information request (too late — it must be in the original submission).

## Document-control apparatus (it is a controlled deliverable)

A filed PCCP is a controlled record. It needs, as a **visible authored header** (never inside a 🔒 container — the document-control header is the standard exception to the internal-tier rule):
- unique **document ID**, version, status, effective date;
- **author / reviewer / approver with dates** (populate the sign-off chain from the project's governing submission WI/SOP, if one exists — check the taxonomy `governing_qms`);
- a visible **change-history table** (a metadata-comment changelog does **not** satisfy this);
- a **Terms/abbreviations table** (every filed-body acronym defined once).

**Placeholder discipline.** Prefer the **managed-TBD** form (`TBD — [named controlled protocol], owner, gate`) over an invented "representative" number: a fabricated number that survives into a controlled context reads as a real acceptance criterion. If a demonstrative draft uses representative sample values, mark each unmistakably (inline tag + banner) **and** carry a pre-transmission checklist committing to the swap — but know that until the swap it is a draft of a controlled record, not the record.

## Scope-vs-effort (read before building N full protocols)

More pre-authorized modifications = more Modification-Protocol + Impact-Assessment surface a reviewer can push back on, and the guidance favors "a **few, specific** modifications" (General PCCP Guiding Principle 4). Two implications:
- **Pre-Q-Sub**, working one AI + one non-AI exemplar to depth and carrying the rest at table altitude is a legitimate *Q-Sub-stage* choice — the Q-Sub questions exist precisely to let FDA prune the set *before* full depth is invested. Confirm the intended consumer (Q-Sub support vs filed 510(k)) before building every protocol.
- When building depth, **prioritize the hard shapes** (imaging-equipment expansion with an equivalence SAP; a real-time/latency-coupled function; a computation-logic change where Data Management is *not* N/A) over the easy ones — depth is only proven where review risk concentrates.

## Sibling references
- [`pccp-authorized-exemplars.md`](pccp-authorized-exemplars.md) — the **empirical** companion: real FDA-authorized PCCPs in the public record (K-number catalog, modification-table schema, quantified-criteria patterns, the documentation-completeness bar). This file is the *required structure*; that one is *what accepted filings actually look like*.
- [`pccp-change-scope-modify-vs-add.md`](pccp-change-scope-modify-vs-add.md) — a *new output* dressed as an *improvement of an existing one* is a scope over-claim; a bounded addition needs its own enumerated category + regulator agreement.
- [`pre-sub-package-consistency.md`](pre-sub-package-consistency.md) — cross-document seam consistency once the PCCP joins the package.
