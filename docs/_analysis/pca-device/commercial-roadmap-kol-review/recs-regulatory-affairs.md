---
title: "Regulatory Feasibility Review — 5-Year Commercial Roadmap"
parent_analysis: commercial-roadmap-kol-review
advisor: regulatory-affairs
role: consulting
created: 2026-06-03
---

> _Demo sample data — not for clinical use._ Consulting regulatory review supporting the clinical-affairs-led KOL gap-analysis of the 5-year commercial roadmap.

## What good looks like (regulatory bar for a roadmap)

A roadmap is regulatorily feasible when **every release names a vehicle that actually carries the change it describes**, and that vehicle's eligibility is verifiable against the cleared device's intended use, the PCCP envelope as authorized, and the change-significance test in 21 CFR 807.81(a)(3). Three bright lines govern:

1. **A PCCP cannot expand intended use or indications for use.** It governs *modifications within* a cleared indication that keep the device substantially equivalent to predicate (`docs/external/fda-guidance/pccp-aiml.md`, "Description of Modifications"). A new clinical output or a new use environment is out of envelope by definition.
2. **A change that introduces a new clinical claim, new patient population, or new use environment is Category C (new submission)** — Flowchart A1 / B5 of `docs/external/fda-guidance/sw-changes.md`.
3. **The envelope must exist before you can ride it.** A PCCP authorized in a *future* 510(k) does not retroactively cover Years 1–2 changes; an unwritten PCCP covers nothing.

## Overall regulatory read

**The sequencing logic is sound; the PCCP-reliance is over-stated and three feature categorizations are wrong.** The roadmap correctly front-loads low-risk Cloud Suite monetization and defers capital-/evidence-heavy predictive AI and ambulatory hardware. But it leans on a **PCCP envelope that does not yet exist** — the project's PCCP (`docs/project/dhfs/pca-device/design-controls/pccp/pccp-predetermined-change-control-plan.md`) is a **v0.1 placeholder stub** with unpopulated `{{template}}` fields and no Description of Modifications, Modification Protocol, or Impact Assessment. Until that is authored and *authorized in a 510(k)*, every "B (PCCP)" cell in D-COMM-1.4 is an aspiration, not a vehicle. Separately, F6, F7, and F8 are each under-categorized relative to what FDA guidance requires. The international wave (D-COMM-1.6) is not yet credible because regulatory-strategy §3 Jurisdictional Differences is empty and §4 Filing Sequence is empty — the roadmap depends on sections that don't exist.

## Sequencing & PCCP-envelope assessment (per year)

- **Y1 (Letter-to-File / PCCP within K210345):** Mostly fine for F2/F3 (MDDS / non-device). But **F1 Drug Library Manager is tagged "C (own 510k)" yet placed under a Y1 "Letter-to-File / PCCP" vehicle** — those conflict. A Class II SaMD accessory that mutates the dose-enforcement table needs its *own* clearance timeline, not an LtF. The vehicle label is wrong even though the feature-row category (C) is right.
- **Y2 (Q-Sub M12 → PCCP-authorized SaMD):** The Q-Sub is correctly placed, but a Q-Sub does **not authorize** anything — it is feedback only (`docs/external/fda-guidance/qsub.md`). The PCCP that would make F4/F5 "B" must be *cleared in a 510(k)* first. There is no cleared SaMD here to attach a PCCP to in Y2, so "B (PCCP)" for F4/F5 presumes an authorization the timeline hasn't produced.
- **Y3 (New 510(k) for predictive + PCCP retraining; ambulatory entry M24):** Correct that F6 needs a **new 510(k)**. The error is calling the *retraining* of that not-yet-cleared predictive function a PCCP item in the same breath — the PCCP rides *on* the F6 clearance, so it cannot pre-date it.
- **Y4 (PCCP retraining + new-indication filing for home):** Home indication is correctly flagged as a new filing, but see F7 below — it may be a different product code / De Novo, which breaks the "rides the PP3500 predicate" assumption.
- **Y5 (international):** Not assessable — §3/§4 of regulatory-strategy are unpopulated (`docs/project/strategies/regulatory-strategy.md` lines 114–124).

## Feature reg-category audit (walk F1–F9)

| # | Roadmap category | Correct? | Corrected read |
|---|---|---|---|
| F1 Drug Library Manager | C (own 510k) | **Category OK, vehicle wrong** | C is right; the Y1 "LtF/PCCP" vehicle label conflicts with its own 510(k) path. |
| F2 Connectivity Adapter | A (MDDS) | ✅ Correct | MDDS, non-device per post-2015 reclassification (regulatory-strategy §2). |
| F3 Fleet/Telemetry | A | ✅ Correct | Non-device software; QMS/cyber only. |
| F4 Alerts Engine v1 (smart-alarm filtering) | B (PCCP) | **Partly wrong** | Alarm *filtering* that changes which alarms a clinician sees is a regulated SaMD output. It needs an **initial 510(k) clearance (C)** to *establish* the device a PCCP could then cover. "B" presumes a cleared baseline that doesn't exist yet. |
| F5 Clinical Surveillance | B | **Likely OK once F4 clears** | Analytics/near-miss surveillance may be lower-risk SaMD or even non-device depending on whether it drives clinical action — needs a classification record before "B." |
| F6 Predictive monitoring | C (new 510k) + PCCP retraining | **Under-categorized** | New *clinical output* (deterioration/occlusion early-warning) on an opioid PCA is plausibly a **new intended use** → new 510(k), and the predicate (PP3000, alarm-only) may not support SE — De Novo risk is live. PCCP applies only to retraining *after* F6 clears. |
| F7 Ambulatory + home indication | C (new clearance + home indication) | **Under-categorized / mis-pathed** | Two stacked changes: (a) new hardware variant, (b) new use environment (unsupervised home) + new user (patient/caregiver). Per `sw-changes.md` Flowchart A1, new population/environment → new 510(k); unsupervised home opioid delivery is a strong **De Novo / different product code** candidate, not a routine new-indication 510(k) off the PP3500 predicate. |
| F8 Dose personalization decision-support | C + PCCP | **Category direction OK, PCCP misapplied** | Dose-personalization that recommends/adjusts opioid dosing is a higher-risk SaMD (possibly outside CDS non-device carve-out). Needs its own authorization; PCCP cannot be the vehicle for the *initial* clinical claim. |
| F9 International | EU MDR / Health Canada | **Not assessable** | Depends on unpopulated regulatory-strategy §3/§4. |

## Worked example (before/after on the most mis-categorized feature — F6)

**Before (roadmap):** "F6 Predictive monitoring — Reg. category **C (new 510k) + PCCP retraining**, Y3. Rides Alerts Engine v2 SaMD."

**After (regulatory read):** "F6 is a **new SaMD with a candidate new intended use** (predictive deterioration/occlusion warning for opioid PCA). Pathway is **not pre-determined**: confirm via Q-Sub whether (a) a new 510(k) against a *predictive-monitoring* predicate is viable, or (b) absent a suitable predicate, **De Novo** is required. PP3000 (alarm-only) is unlikely to support SE for a predictive claim. **PCCP applies only to post-clearance retraining** of F6 once authorized — it is not a vehicle for the initial predictive claim. Acceptance: pathway and predicate confirmed in the M12 Q-Sub before Y3 spend commits."

This reframes F6 from "we own the vehicle" to "we must ask FDA which vehicle exists" — the difference between a fundable Year-3 commit and a guess.

## Why this matters for THIS filing

K210345 is a PCA-device-alone clearance with PP3000 as predicate (`docs/project/submissions/510k/composition-manifest.md`). The roadmap quietly assumes the PP3500 510(k) + an unwritten PCCP can absorb predictive AI, dose decision-support, and a home indication. If the team commits the business case (D-COMM-1.7: $24M predictive spend) against PCCP coverage that FDA never authorized, a single "this is a new intended use, file De Novo" response at the M12 Q-Sub resets the Year-3 timeline and the dependent Year-4/5 waves. The carve-out discipline (CtS/CtF/CtC/CtP) is exactly the right tool — but it has **not been applied** to these features yet (open item, regulatory-strategy line 164).

## Prescriptions (numbered, owner + acceptance)

1. **Author the PCCP before any roadmap cell cites "B."** Owner: RA lead. Acceptance: `pccp-predetermined-change-control-plan.md` populated with the three required sections (Description of Modifications, Modification Protocol, Impact Assessment per `pccp-aiml.md`) and an explicit list of which feature changes fall *inside* the envelope.
2. **Re-categorize F1, F4, F6, F7, F8 in D-COMM-1.4** per the audit table; split "needs initial clearance" from "PCCP-covered retraining." Owner: RA + Commercial. Acceptance: no feature shows "B" without a cleared baseline device, and no feature shows PCCP as the vehicle for an initial clinical claim.
3. **Make the M12 Q-Sub carry F6 pathway + F7 product-code questions.** Owner: RA lead. Acceptance: Q-Sub question set explicitly asks (a) F6 predicate vs De Novo, (b) F7 product code + home-environment indication, (c) whether one PCCP can span Alerts Engine + Clinical Interface (two SaMDs).
4. **Gate D-COMM-1.6 on populating regulatory-strategy §3/§4.** Owner: RA. Acceptance: Jurisdictional Differences + Filing Sequence sections authored before Y5 international commit firms.
5. **Run the Ct* tagging pass** on the feature requirements so "PCCP envelope" is defined structurally, not asserted. Owner: RA. Acceptance: trace-matrix Filing Scope column populated for F1–F8.

## Evidence base (paths + FDA guidance)

- `docs/project/strategies/commercial-strategy.md` — D-COMM-1.3, 1.4, 1.6, 1.7 (roadmap under review).
- `docs/project/strategies/regulatory-strategy.md` — Carve-out §1; component classification §2; §3 Jurisdictional / §4 Filing Sequence **empty** (lines 114–124); Pending Decisions (line 252).
- `docs/project/dhfs/pca-device/design-controls/pccp/pccp-predetermined-change-control-plan.md` — **v0.1 placeholder stub**; no envelope authored.
- `docs/project/submissions/510k/composition-manifest.md` — K210345, predicate PP3000 (K190567), PCA-device-alone scope.
- `docs/project/input-analysis/market-research/strategic-market-ai-infusion.md` — PCCP final Aug 2025; 3–6 mo AI/ML 510(k) timelines; recommended cadence (M12/M24/M30).
- FDA PCCP AI/ML guidance — L1a `.claude/skills/medtech-docs/references/fda-guidance/pccp-aiml-distilled.md` + L1b `docs/external/fda-guidance/pccp-aiml.md` (cite-both): PCCP must keep device within intended use/indications and SE to predicate. **Verdict: sound** (predicate match confirmed against both layers).
- FDA sw-changes guidance — L1a `.claude/skills/medtech-docs/references/fda-guidance/sw-changes-distilled.md` + L1b `docs/external/fda-guidance/sw-changes.md` (cite-both): Flowchart A1 new population/environment → new 510(k). **Verdict: sound.**
- Q-Sub guidance — L1b `docs/external/fda-guidance/qsub.md`: Q-Sub is feedback, not authorization. **Verdict: sound.**

[VERIFY] Whether F6/F7 are De Novo vs new-510(k) is a genuine FDA-feedback question, not something the local grounding resolves — flagged for the M12 Q-Sub, not assertable here.

## Cross-discipline open questions (table)

| # | Question | Routes to | Why it's cross-cutting |
|---|---|---|---|
| Q1 | Does the F6 15–30 min predictive warning claim hold for *opioid/PCA* context (vs borrowed general-infusion evidence)? | Clinical (primary) + Risk | Determines whether F6 is a defensible new claim at all (R1). |
| Q2 | Is unsupervised home opioid PCA (F7) a use-safety profile a 510(k) can support, or does residual risk push De Novo? | Human Factors + Clinical + Risk | Drives F7 pathway (new 510k vs De Novo) and product code. |
| Q3 | Does dose-personalization (F8) recommend/adjust dosing such that it exits the CDS non-device carve-out? | Clinical + Risk | Determines F8 classification and whether it's even SaMD-regulated. |
| Q4 | Can one PCCP span two independent SaMDs (Alerts Engine + Clinical Interface)? | Architecture + RA | Affects whether "B" features can share an envelope or each need their own. |
