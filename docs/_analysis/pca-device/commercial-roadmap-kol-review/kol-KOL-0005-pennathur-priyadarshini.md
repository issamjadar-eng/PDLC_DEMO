---
title: "KOL Opinion — Dr. Priyadarshini Pennathur (Human Factors / Usability)"
kol_id: KOL-0005
parent_analysis: commercial-roadmap-kol-review
agent: pennathur-priyadarshini
role: kol-panel
specialty: "Human factors engineering, medical device usability, patient-safety engineering"
created: 2026-06-04
---
> _Demo sample data — not for clinical use. Simulated KOL persona opinion for the PDLC_DEMO; not real collected feedback._

## My overall take

I read this roadmap the way I read any device plan: not as a list of features, but as a series of **work systems** — a person, a task, a tool, an environment, and an organization, all interacting. On that lens the PP3500 program is on solid ground where it stays inside the work system it was validated for (supervised acute care, trained nurse, clinician available for alarm response — exactly what the cleared User Needs and Intended Use specify), and it gets progressively more fragile the further it drifts from that system without re-validating the *whole* system, not just the box.

My single biggest concern is **F7 (ambulatory / home PCA)**. This is not a feature increment. It is a wholesale substitution of the operator — from a trained, credentialed, monitored nurse to a post-operative patient and a family caregiver, in a home with no clinical backstop, delivering an opioid. The cleared device explicitly says it is *"not intended for unsupervised home or ambulatory use"* and *"requires that trained clinical staff be available for monitoring and alarm response."* F7 deletes both of those preconditions. Everything I say below flows from that.

## What I like

- The roadmap **names R3** (home-PCA use-safety) and routes it to Human Factors + Clinical. Naming the hardest human-factors leap explicitly, rather than burying it, is exactly the posture I want to see.
- **CAPA-2023-001** (the decimal-point 1.0-vs-10 mg confusion, UN-007) is already in the User Needs as a use-error control. That tells me the program understands use error is a design problem, not a training problem. Good instinct to carry forward.
- The sequencing **defers F7 to Y3→Y4**, behind the connected base. The leap is at least scheduled late, which buys runway for the use-research it will require.
- **F4 (smart alarms)** correctly anchors to the alarm-fatigue KOL cluster. Alarm-fatigue *is* a human-factors problem, not just a signal-processing one.

## What worries me most (human-factors lens)

**Use specification is the gap, not features.** IEC 62366-1 begins with the **use specification** — intended users, use environments, and user-interface characteristics. F7 changes all three at once. You cannot inherit the PP3500's formative/summative validation for a new user profile (patient/family vs nurse), a new environment (home, no monitoring), and new tasks (priming, alarm response, troubleshooting by a layperson at 3 a.m.). F7 requires a **new use specification and a fresh summative usability validation with representative lay users under simulated home-use conditions** — not a delta.

**Automation bias is the hidden hazard in F8.** Dose-personalization decision support changes the clinician from a *decision-maker* into a *decision-checker* — and people under-scrutinize automation they trust. If the algorithm proposes a dose and the path of least resistance is "accept," you have engineered complacency. F8 needs **use transparency** (why this dose), a designed-in **friction point** for confirmation, and summative testing of whether clinicians actually catch a wrong recommendation.

## Feature-by-feature (my wheelhouse)

- **F7 — Ambulatory home PCA (my hardest flag).** New use specification mandatory. Worst-case use scenarios to test: caregiver-administered "PCA by proxy" (a known fatal failure mode in the literature — the patient is *supposed* to be the only one pressing the button), lockout/limit misunderstanding, missed occlusion or end-of-therapy alarm with no nurse present, and reservoir/priming errors. The home environment is the co-designer of every error here. Summative validation with patients *and* family caregivers, not nurses.
- **F8 — Dose personalization.** Automation bias / over-trust. Demand use transparency and a confirmation friction point; validate error-catching, not just task success.
- **F4 — Alarm UI.** Don't just filter alarms — validate that filtering doesn't suppress an *actionable* alarm and that the remaining alarms are still distinguishable and responded-to (UN-010). Test the alarm *work system*, including handoffs.
- **F1–F3, F5 (Cloud Suite, pharmacy-facing).** Lower human-factors risk — trained, supervised users in their existing workflow. Still: every new screen is a new use-error surface; carry them through use-related risk analysis.

## My one piece of advice

**Treat F7 as a new device for usability purposes, and start the home-use formative research now — not at design transfer.** Write the F7 use specification first; let it tell you what hardware, alarms, and labeling the home version actually needs. The work system designs the device, not the other way around.

## Findings I corroborate

- **F-11** — F7 home/ambulatory PCA requires a new IEC 62366-1 use specification + fresh summative usability validation with lay users; cannot inherit the supervised-use validation.
- **F-13** — F8 dose-personalization introduces automation-bias / over-trust risk; needs use transparency and a designed confirmation friction point.
- **F-12** — F4 smart-alarm filtering must be validated to not suppress actionable alarms (UN-010 distinguishability + response).
- **F-4** — the home use-error chain (PCA-by-proxy) is real and unaddressed.

**My verdict:** _Conditional support_ — the Cloud Suite is sound, but F7 home PCA is a wholesale operator/environment change demanding a new use specification and fresh lay-user summative validation.
