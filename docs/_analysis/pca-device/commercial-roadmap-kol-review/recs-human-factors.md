---
title: "Use-Safety / Human-Factors Review — 5-Year Commercial Roadmap"
parent_analysis: commercial-roadmap-kol-review
advisor: human-factors
role: consulting
created: 2026-06-03
---

> _Demo sample data — not for clinical use. Consulting human-factors review of `docs/project/strategies/commercial-strategy.md`._

## What good looks like (IEC 62366-1 bar for a care-setting expansion)

A roadmap that moves a cleared opioid PCA pump from supervised hospital use to unsupervised home/ambulatory use is, in IEC 62366-1 terms, a **new use specification** — not a variant of the old one. The standard's Clause 5.1 requires that intended **users**, intended **use environment**, and the **user interface** be re-characterized for each use scenario (`.claude/skills/medtech-docs/references/standards/iec-62366-1.md` §5.1.1–5.1.3). When any of those three change materially, the downstream chain re-opens: a fresh **use-related risk analysis** (5.2), a re-derived **UI specification** with critical-task acceptance criteria (5.3), **formative** evaluation rounds during design (5.6), and a **summative** human-factors validation on a production-equivalent device in a representative environment with statistical evidence that critical tasks are performed safely (5.6). For F7 all three Clause-5.1 axes change at once. The cleared 98.7% task-success figure does not transfer — it was earned against the old use specification (trained clinicians, hospital).

## Overall use-safety read

The roadmap **names** the right risk (D-COMM-1.9 R3: "Ambulatory home-PCA use-safety — opioid in an unsupervised setting is the highest-consequence human-factors leap," owned Human Factors + Clinical) and **names** a human-factors KOL anchor for F7 (Pennathur, KOL-0005). That is more self-awareness than most roadmaps carry. But naming a risk is not the same as scoping the work to retire it. The roadmap nowhere commits F7 to a fresh use specification, formative+summative HF validation, or new use-error risk controls — and it sequences F7 as a "hardware pilot → GA" (D-COMM-1.4) as if the human-factors leap were a form-factor change rather than a user-population change. The alarm-fatigue feature (F4) and dose-personalization (F8) each introduce **new** use-error modes the roadmap does not yet acknowledge. Net: the use-safety framing is present but under-scoped; this review converts R3 into concrete IEC 62366-1 obligations and flags two adjacent use-error risks the roadmap misses.

## The home-PCA user-profile shift (why F7 is not the cleared device)

The cleared device's own user-needs document draws the bright line explicitly. Intended use is "controlled intravenous administration of analgesic medications **by trained healthcare professionals** … in **supervised** acute-care environments where qualified clinical staff are available to monitor the patient and respond to alarms," and the indications statement says the device is "**not** intended for unsupervised home or ambulatory use" and "requires … trained clinical staff … available for monitoring and alarm response" (`docs/project/dhfs/pca-device/design-controls/user-needs/user-needs.md` §Intended Use, §Indications for Use). F7 deletes every clause of that sentence:

- **User**: trained nurse → opioid-naïve patient and/or untrained family caregiver. New capabilities to design for: variable literacy/numeracy, fatigue, impairment (the patient is on opioids), no clinical alarm-response training.
- **Environment**: monitored ward → home (variable lighting, ambient noise, no backup responder, pets/children present, network gaps).
- **Use-error consequence**: the cleared device's existing hazards (over-sedation, occlusion) now play out with **no clinician in the loop** — respiratory depression with no one to respond, plus two new hazard classes the hospital never had: **tampering / diversion** (the lockbox/tamper-evidence need UN-020 was scoped for institutional security, not a home where the cardholder may be the misuse actor) and **unauthorized activation** (a family member or child pressing the bolus button — the cleared device assumed "the patient be cognitively capable of self-administration" with staff present).

This is three simultaneous Clause-5.1 changes. Per IEC 62366-1 that mandates a new use specification and the full evaluation chain, not a delta.

## Feature use-safety assessment (F4, F6, F7, F8)

- **F4 — Alerts Engine v1 (alarm-fatigue reduction, SaMD, Y2).** The clinical intent is sound and KOL-anchored (Shah KOL-0008, Giuliano KOL-0001), and the cleared device already carries an alarm-fatigue user need (UN-010, "without contributing to alarm fatigue"). But alarm *suppression/filtering* is itself a use-error generator: a filtered or de-prioritized alarm is a **missed critical alarm** (perception/cognitive error class, §5.2). The roadmap treats F4 purely as a benefit (35–45% alert reduction, market doc) and never states the inverse risk — that the suppression algorithm plus user trust can cause a clinician to miss an actionable occlusion/over-sedation alarm. F4 needs its own use-related risk analysis with the false-negative (over-suppression) path as a critical task.
- **F6 — Predictive monitoring (Y3).** Out of primary HF scope here (clinical-evidence sufficiency is R1, owned Clinical+Risk), but it shares F8's use-transparency problem: a 15–30 min "early warning" that users learn to trust shapes behavior, so its alert/no-alert UI is a critical-task surface. Flagged for cross-discipline routing, not assessed in depth.
- **F7 — Ambulatory PP3500-A (Y3→Y4).** The highest-consequence item; see the section above and the worked example below. The roadmap benchmarks F7 against insulin patch-pumps (180g/7-day, vs Omnipod 72-hr) in `docs/project/input-analysis/market-research/strategic-market-ai-infusion.md` — but an insulin patch and a home opioid PCA have **different use-error consequence profiles**. Borrowing the form-factor benchmark must not imply borrowing the usability validation; opioid respiratory depression is not insulin's risk profile.
- **F8 — Dose personalization decision-support (Y4, SaMD).** This is the roadmap's highest-sentiment opportunity (+0.55) but it is a **use-transparency / automation-bias** problem. If a clinician (or, in a home variant, a patient) cannot see *why* the system recommended a personalized dose, two opposite use errors appear: **over-reliance** (accepting an unsafe recommendation without the cross-check that catches it) and **under-reliance** (ignoring a good recommendation). Per §5.2 these are cognitive-error-class use errors; F8's UI must make the recommendation's basis and bounds visible, and the "clinician accepts a wrong personalized dose" path is a critical task for summative testing.

## Worked example (before / after: a home-PCA use-error chain)

**Use scenario:** A post-surgical patient is discharged home on the ambulatory PP3500-A. Overnight the patient is drowsy from the opioid; a family caregiver, worried the patient "isn't getting enough relief," presses the bolus button repeatedly on the patient's behalf.

**Before (roadmap as written):** The cleared lockout/cumulative-dose limits (UN-003) and tamper-evident lockbox (UN-020) were validated for a hospital where a nurse monitors sedation and responds to alarms. In the home there is no responder. The caregiver's repeated activation is an **unauthorized-activation use error** → cumulative dose approaches the limit while the patient is already sedated → **hazardous situation** (over-sedation, falling respiratory rate) with no clinician present → **harm** (respiratory depression). The roadmap's only control is the inherited hospital design plus a named risk (R3) — no caregiver-specific control, no monitoring fallback.

**After (control added):** Following a fresh F7 use specification, the use-related risk analysis identifies "unauthorized/by-proxy activation" and "unattended over-sedation" as critical tasks. Risk controls per the §5.2→5.3 chain: (a) a **caregiver-authentication / single-authorized-user** interaction so only the patient (or a designated authorized caregiver) can deliver a bolus; (b) on-device **respiratory/sedation monitoring with an escalation path** (audible local alarm + remote caregiver/clinician notification via the Cloud Suite) so "no responder present" is no longer a single point of failure; (c) IFU + onboarding training validated for a lay user. These controls are then proven in **formative** rounds and a **summative HF validation** before GA — exactly the chain the roadmap does not yet commit to.

## Why this matters for THIS program

The program's own predicate history shows use-error is its dominant risk channel, not device failure: CAPA-2023-001 (decimal-point visibility, 1.0 mg misread as 10 mg) drove user needs UN-007 and UN-004 in the cleared file. That CAPA happened with **trained nurses in hospitals**. Moving the same opioid-delivery surface to untrained home users without re-running the IEC 62366-1 chain re-opens the exact failure mode the program already paid to fix once — now without a clinician backstop. F7 also carries a new clearance + new home indication (D-COMM-1.4 category C), and FDA expects a Human Factors Validation (summative) report in the submission (`.claude/skills/medtech-docs/references/standards/iec-62366-1.md` §FDA-Specific Notes). Under-scoping the HF work is therefore both a safety gap and a filing gap.

## Prescriptions (numbered, owner + acceptance)

1. **Author a fresh F7 use specification before F7 leaves the pilot gate.** Owner: Human Factors (with Clinical). Acceptance: a Use Specification per §5.1 documenting the new intended users (patient + family caregiver), home/ambulatory use environment, and UI; explicitly superseding the cleared "trained HCP / supervised" use spec in `user-needs.md`. F7 cannot move from pilot (D-COMM-1.4 Y3) to GA (Y4) until this exists.
2. **Commit F7 to formative + summative HF validation as a gated deliverable, not an implied step.** Owner: Human Factors. Acceptance: ≥2 formative rounds with representative lay users on prototypes, then a summative HF validation on production-equivalent F7 hardware in a simulated home environment, with critical-task success criteria pre-stated and the summative report cited in the F7 510(k). The 98.7% hospital figure is explicitly retired as inapplicable.
3. **Open a new use-related risk analysis for F7 covering the home-specific hazard classes.** Owner: Human Factors + Risk. Acceptance: URRA (§5.2) enumerating unauthorized/by-proxy activation, tampering/diversion, unattended over-sedation, and lay-user programming errors as critical tasks, each with a risk control traced into the UI spec (§5.3).
4. **Add a use-error risk analysis for F4 covering the over-suppression / missed-critical-alarm path.** Owner: Human Factors + Clinical. Acceptance: F4's risk file names alarm over-suppression (false-negative) as a critical task; the 35–45% reduction claim is paired with a stated missed-actionable-alarm acceptance threshold, not presented as benefit-only.
5. **Treat F8 dose-personalization as a use-transparency problem with explicit over/under-reliance critical tasks.** Owner: Human Factors (with Clinical for the trust model). Acceptance: F8's UI spec requires the recommendation's basis and safe bounds be visible; "user accepts an unsafe personalized dose" and "user ignores a safe one" are both summative critical tasks.

## Evidence base (paths)

- `docs/project/strategies/commercial-strategy.md` — D-COMM-1.4 (F4/F6/F7/F8), D-COMM-1.9 R3.
- `docs/project/dhfs/pca-device/design-controls/user-needs/user-needs.md` — cleared intended use / indications bright line; UN-003, UN-004, UN-007, UN-010, UN-020; CAPA-2023-001 lineage.
- `docs/project/input-analysis/market-research/strategic-market-ai-infusion.md` — 180g/7-day ambulatory benchmark; 35–45% alert-reduction figures.
- `docs/project/input-analysis/kol-feedback/KOL-0005-pennathur-priyadarshini.md` (HF), `KOL-0001-giuliano-kathleen.md` (smart-pump usability/alarm fatigue), `KOL-0008-shah-parth.md` (alert fatigue), `KOL-0006-paul-james.md` (PCA opioid safety).
- `.claude/skills/medtech-docs/references/standards/iec-62366-1.md` (L1a) + `docs/external/standards/iec-62366-1.md` (L1b) — Clause 5.1–5.6, FDA HF-validation expectation.

## Cross-discipline open questions (table)

| # | Question | Owning discipline(s) | Why it matters for HF |
|---|---|---|---|
| Q1 | Is F7 a new indication ("home/unsupervised opioid PCA") requiring its own clearance, and does the filing assume a summative HF report? | Regulatory + Clinical | Determines whether the HF validation is a filing deliverable vs internal-only |
| Q2 | What clinical monitoring fallback (remote clinician, respiratory monitoring) is assumed for the home patient with no on-site responder? | Clinical + Risk | The "no responder" gap is the linchpin of the F7 use-error chain; HF controls depend on whether a monitoring backstop exists |
| Q3 | Does the F4 alarm-suppression algorithm have a quantified missed-actionable-alarm (false-negative) bound the clinical team will accept? | Clinical + Risk | Sets the acceptance threshold for F4's use-error critical task |
| Q4 | For F8, who is the decision-maker in the home variant — clinician-only, or patient-facing? | Clinical + Regulatory | A patient-facing personalization UI is a far higher use-transparency bar than a clinician-facing one |
| Q5 | Are tamper-evidence/diversion controls (UN-020, hospital-scoped) sufficient when the authorized cardholder may be the misuse actor at home? | Risk + Regulatory + HF | Reframes a security need as a home-use-error/diversion control |
