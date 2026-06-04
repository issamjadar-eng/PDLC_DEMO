---
title: "KOL Opinion — Lisa Gorski (Infusion Nursing Standards)"
kol_id: KOL-0007
parent_analysis: commercial-roadmap-kol-review
agent: gorski-lisa
role: kol-panel
specialty: "Infusion therapy standards of practice, nursing workflow, infusion-complication prevention"
created: 2026-06-04
---
> _Demo sample data — not for clinical use. Simulated KOL persona opinion for the PDLC_DEMO; not real collected feedback._

## My overall take

I've spent thirty-eight years at the bedside and on the INS Standards Committee, and the lens I bring is simple: a pump is only as safe as the workflow it lives inside. This roadmap is technically literate and commercially coherent, but it is written by people who think about *devices* and *filings*, not about the nurse who hangs the bag at 2 a.m. or the patient's daughter who reconnects a line in a living room. The hardware story is strong. The workflow and standards story is thin — and in infusion therapy, that's where patients actually get hurt. I'd call this a conditional yes: the sequencing instinct (defend the base, connect, then expand) is right, but F2, F3, and especially F7 need a nursing-standards spine before they're real.

## What I like

- **Sequencing discipline (D-COMM-1.3).** Deferring home/ambulatory PCA to Years 3–5, *after* the connected story is referenceable, is the correct instinct. Opioid PCA in an unsupervised setting is not where you cut your teeth.
- **Cost-avoidance framing tied to nursing efficiency (D-COMM-1.5).** You correctly name nursing labor and alarm fatigue as the economic case. That's honest — PCA is bundled into the DRG, so avoided harm and nurse time *are* the argument.
- **You named me on F2 and on the pharmacy/biomed segment (D-COMM-1.2).** Good — the Connectivity Adapter and drug-library governance genuinely are where infusion-nursing standards bite hardest.

## What worries me most (nursing-workflow / standards lens)

The roadmap treats connectivity as a *data* problem (HL7/FHIR, MDDS) and nearly forgets it is a *workflow* problem. INS Standards of Practice are explicit that automated programming must reduce, not relocate, the nurse's verification burden. My single biggest worry: **F7 home PCA has no defined user.** The roadmap says "patient or family caregiver" almost in passing. Who performs the infusion-line care, the independent double-check for a high-alert opioid, the site assessment for infiltration? INS standards assume a *competency-verified* clinician for those tasks. You cannot delete the nurse and keep the safety claim.

## Feature-by-feature (my wheelhouse)

**F2 — Connectivity Adapter / EHR-pharmacy workflow.** Auto-programming from the EHR is the right direction *if and only if* it preserves independent verification at the point of care. Today the nurse scans patient, drug, and pump and reconciles against the order. If F2 pre-populates the pump from the order, you've moved the verification upstream into pharmacy and the EHR — that can be safer, but it can also create automation complacency at the bedside. **Requirement:** F2 must specify where the nurse's independent double-check of a high-alert medication happens, and the human factors must confirm the nurse can still catch a wrong-channel or wrong-line error. This is a standards conformance claim, not a feature bullet.

**F3 — Fleet/telemetry as it affects nursing.** Useful for biomed and pharmacy. My concern is that fleet dashboards and drug-library cadence changes (F1) push *new libraries* to pumps the nurse is actively using. INS standards require that library updates not surprise a clinician mid-infusion. Specify the change-management workflow: when a library version changes, what does the nurse see, and is an in-progress infusion ever silently re-bounded?

**F7 — Ambulatory/home PCA.** This is the one that keeps me up. Home infusion is a real, standards-governed discipline — INS publishes home-infusion competencies, and the responsible party is typically a home-infusion nurse, not the family. The roadmap conflates "ambulatory wearable" (still nurse-managed) with "home self-administration" (a different risk universe). For a high-alert opioid you need: defined caregiver competency, a tamper/diversion control, a site-assessment cadence, and a clear escalation path. R3 names the human-factors leap but stops short of naming the *standards* the home program must satisfy. Tie F7 to INS home-infusion standards explicitly, or it will not survive review.

## My one piece of advice

For every connected and home feature, write the **nurse/caregiver workflow and its INS-standards conformance** as an input *before* the regulatory category. Name the user, name the verification step, name the competency. A roadmap that monetizes connectivity while silently relocating the nurse's safety checks is a roadmap that ships an unsafe workflow with a clean 510(k).

## Findings I corroborate

- **F-4** — home-PCA user/caregiver is undefined; F7 lacks a named competency-verified operator and INS home-infusion standards anchor.
- **F-11** — roadmap conflates "ambulatory/wearable, nurse-managed" with "home self-administration"; distinct risk and standards regimes; F7 needs its own validation.
- **F-3** — F2 auto-programming does not specify where the nurse's independent high-alert double-check occurs (automation-complacency risk).
- **F-8 / F-9** — drug-library / fleet updates (F1/F3) lack a mid-infusion change-management workflow; risk of silent re-bounding of an in-progress infusion.

**My verdict:** _Conditional yes_ — sequencing is right, but F2/F3/F7 each need a named nurse-or-caregiver workflow and INS-standards conformance before they're safe to claim.
