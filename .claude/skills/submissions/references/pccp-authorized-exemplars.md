# Authorized-PCCP exemplars — what a good filed PCCP looks like in the public record

🔎 **Finding aid.** The FDA guidance ([`pccp-full-document-structure.md`](pccp-full-document-structure.md)) defines the *required structure*; its own Appendix B examples are **hypothetical** and, by FDA's own note, "not the complete detail expected." This file is the **empirical** companion: real, FDA-**authorized** PCCPs in the public 510(k)/De Novo record that show where the accepted *quality* bar actually sits. Use it to calibrate depth and to copy proven patterns. Cite the primary source (the accessdata PDF) for any filed claim — not this finding aid.

**How to open any device's public summary:** `https://accessdata.fda.gov/cdrh_docs/pdfYY/KYYNNNNN.pdf` (YY = the K-number's two-digit year). Live index of AI-enabled devices (flags which carry a PCCP): `https://www.fda.gov/medical-devices/software-medical-device-samd/artificial-intelligence-enabled-medical-devices` — re-pull it for current K-numbers; the population grows fast (PCCP-carrying devices went from ~26 in mid-2025 toward ~110 by late 2025; ~10% of 2025 AI 510(k)s included a PCCP).

## Exemplar catalog

| K-number | Device / type | Why exemplary | Copyable pattern |
|----------|---------------|---------------|------------------|
| **K250369** | Axial3D INSIGHT — cloud-hosted CT bone-segmentation SaMD (orthopedic/trauma/maxillofacial/cardiovascular; product code QIH) | The closest public archetype to a **bone-segmentation planning** device. The PCCP was the **only delta** vs the sponsor's own predicate (K232841) — validates the "lean initial 510(k) + PCCP" strategy. | Named PCCP sections ("Table 5: Potential Modifications List" with `MOD_ML_001..005`, columns Summary \| Trigger for Retrain \| Timeframe/review-cadence 6/12/18 mo). **Verification/Validation split** (below). A **permanently-frozen expert reference standard** held constant across every future version. Two scope-fence sentences (below). |
| **K241561** | MammoScreen BD (Therapixel) — breast-density AI | **Best-in-class documentation** (top-ranked in the scoping review below). | Names the four MP pillars verbatim ("data management, re-training, performance evaluation and update procedures"); a per-modification table with a **quantified acceptance-criteria row** (e.g., quadratic Cohen's κ > 0.85; non-inferior on density bins) **and** a **post-market drift-monitoring row** (a live Reference Distribution of model output → drift alert → escalation to field-safety notice / MDR). The drift row is the single biggest differentiator most PCCPs lack. |
| **K242807** | HeartFocus (Deski) — cardiac ultrasound guidance | **Most operationally detailed protocol.** | A 3-phase plan with quantitative success criteria (κ/PPV bounds), **predefined sample sizes**, a **one-iteration cap** per modification, subgroup analyses, and **prospective novice-user usability testing**. |
| **K242551** | Syngo Dynamics Auto-EF (Siemens) — cardiac EF | The **conservative / guidance-aligned** archetype. | Locked-model release, fixed equivalence thresholds — clean and minimal, but note it carries **no drift sentinels / rollback**, which is why it scores below MammoScreen. Use as the "safe floor," not the ceiling. |
| **K233955** | Clarius OB AI — fetal-biometry ultrasound segmentation | A clean **4-modification benefit-risk** template. | Each modification = **rationale + testing method + impact assessment**; explicit benefit-risk per change (benefits: performance/generalization; risks: overfitting, unintended bias; mitigations: regularization, cross-validation). |
| **K233030** | BoneMRI (MRIguidance) — orthopedic MRI synthetic-CT | Orthopedic-imaging analog on a different modality. | Useful cross-modality comparator for an imaging-input-expansion change track. |

## Reusable filed-PCCP modification-table schema

Best-in-class filings enumerate modifications in a table with a **stable ID per change** and a fixed column set. The FDA-minimum plus the two enhancements the exemplars add:

`ID | Modification summary | Data used (development + test) | Verification method | QUANTIFIED acceptance criterion | Impact / characterization (before→after) | Trigger for retrain + review cadence | Post-market monitoring & response`

- **"Trigger for Retrain" + "Timeframe/review cadence"** columns → from Axial3D Table 5.
- **"Monitoring / detection / response"** row → from MammoScreen (the drift-monitoring differentiator).

## The Verification-vs-Validation split (performance-evaluation backbone)

The strong AI exemplars split performance evaluation into two named halves — a directly copyable structure:

- **Verification** — peer code review + unit testing + **quantitative metrics** (segmentation: Dice, Pixel Accuracy, AUC, Precision, Recall) measured against the **frozen original-submission (locked baseline) model**; must show equivalence-or-improvement.
- **Validation** — multi-reviewer (**≥ 3**) qualitative comparison against the unmodified model on **fixed independent datasets** representative of the intended-use population + a **quantitative test against a permanently-frozen expert reference standard held constant across all versions** + a **Hazard Analysis re-review** for new bias/limitations.

Axial3D's *permanently-frozen expert reference standard as a standing baseline* is a strong, copyable device — it makes cross-version comparability auditable.

## Scope-fence sentences (keep the device inside substantial equivalence)

Two verbatim boilerplate sentences from K250369 that a good PCCP states explicitly — saying what the PCCP does **not** authorize is as important as what it does:

> "All algorithm modifications will be trained, tuned, and locked prior to release."
> "The PCCP does not include provisions for adaptive algorithms that continuously learn in the field."

## Quantified acceptance-criteria patterns (calibration for `[locked at design transfer]`)

A margin number needs a clinical justification, and a **named metric + threshold** scores higher than a vague "equivalence or improvement" (which is *acceptable* — Axial3D used it — but weaker). Real patterns to calibrate against:

- MammoScreen (K241561): quadratic Cohen's **κ > 0.85**; linear-κ / accuracy / density-bins **non-inferior to comparator**.
- HeartFocus (K242807): **κ / PPV bounds** with **predefined sample sizes** and a **one-iteration cap**.
- Natural Cycles (cited in Innolitics best-practices): **Positive Percent Agreement ≥ 96.5%** with a stated **confidence interval**.

## The documentation-completeness bar (triage index)

A 2025 scoping review (*Evaluating Transparency of PCCPs in FDA-Cleared Radiology AI Devices*, Research Square preprint, DOI 10.21203/rs.3.rs-9411603/v1) ranked **all 34** PCCP-cleared radiology AI submissions by a 4-domain documentation score. The four domains — and where filings fail — are the differentiator map:

1. Modification protocol with explicit acceptance criteria + risk mitigation + data-management — **26/34 pass**.
2. Demographics + methodological quality of clinical studies — **30–31/34 pass**.
3. Retrospective real-world **multi-site** evaluation — **20/34**.
4. **Post-market surveillance / drift monitoring** — only **3/34**, with real-time drift in only **1/34**.

**Domains 3 and 4 are where a filing lands in the top tier** — most cheaply by including a post-market drift-monitoring plan (MammoScreen's live-reference-distribution → alert → escalation pattern) and multi-site real-world evaluation. Empirical transparency deficits a strong PCCP overcomes (npj Digital Medicine, n=1016): 93.3% reported no training-data source, 75.5% no test-data source, only 9.4% training-set size, 23.2% test-set size — so affirmatively stating data provenance, dataset size, and subgroup/demographic performance is itself a differentiator.

## Caveats (grounding discipline)

- The 34-device ranking + the archetype write-ups + the domain-pass statistics are from a **2025 preprint** (not yet peer-reviewed) — a useful **triage heuristic, not gospel**.
- Only **K250369** and **K241561** were read primary-source (accessdata PDF) in the research that seeded this file; all other K-number details are from secondary sources. **Verify any K-number detail against the accessdata PDF under the `/reference-audit` gate before quoting it in a filed body.**
- Public 510(k) summaries are deliberately terse — sponsors hold fuller modification protocols, drift thresholds, and rollback criteria **internally**. "What's in the public summary" is a **floor** on real PCCP content, not the whole filing.
- The FDA AI-device list and the authorized-PCCP count change quickly — re-pull the live index rather than citing a fixed number.

## Sibling references
- [`pccp-full-document-structure.md`](pccp-full-document-structure.md) — the required structure + depth contract (the guidance side).
- [`pccp-change-scope-modify-vs-add.md`](pccp-change-scope-modify-vs-add.md) — the modify-vs-add scope discipline.
