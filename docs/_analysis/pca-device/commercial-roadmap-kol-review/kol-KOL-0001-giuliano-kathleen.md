---
title: "KOL Opinion — Dr. Kathleen Giuliano (Smart-Pump Usability / Alarm Fatigue)"
kol_id: KOL-0001
parent_analysis: commercial-roadmap-kol-review
agent: giuliano-kathleen
role: kol-panel
specialty: "IV smart pump usability, alarm/alert fatigue, medication administration safety"
created: 2026-06-04
---
> _Demo sample data — not for clinical use. Simulated KOL persona opinion for the PDLC_DEMO; not real collected feedback._

## My overall take

I've spent two decades watching nurses drown in smart-pump alarms — 65 million of them across 107 hospitals in the work I know best, averaging better than one alarm a minute on a third of infusions. So I read this roadmap with one question: does it make the bedside *quieter and safer*, or just quieter? Those are not the same thing, and conflating them is the single most dangerous mistake in my field. The hardware story here is genuinely strong, the sequencing is disciplined, and you've named the right risk (R2). But the Alerts Engine claim as written (F4) is exactly the trap I study, and I won't sign off on it until you bound it correctly.

## What I like

The launch sequencing (D-COMM-1.3) is honest. You defer the capital-heavy, evidence-heavy predictive and ambulatory bets behind the cheap, cleared Cloud Suite wins, and you gate each year on the prior clearance. That's the right temperament. I also appreciate that the roadmap exposes its seams on purpose — naming R1–R5 instead of hiding them tells me this was written to be stress-tested, not to be sold. And segmenting me into the "alarm-fatigue cluster" with Shah and Kirkendall (D-COMM-1.2) is correct; that *is* where the hospital pull lives.

## What worries me most (alarm-fatigue lens)

F4 says "smart alarm filtering / alert-fatigue reduction" and the market source cites "45% reduction in non-actionable alerts." Here is my hard objection: **a percentage reduction in alarm *count* is not a safety claim — it's a noise claim.** The number that determines whether F4 helps or kills is the one nobody has put on the page: **the suppressed-true-alarm rate.** If you filter 45% of alarms and even a fraction of a percent of the suppressed ones were real occlusions, infiltrations, or apnea events in an opioid patient, you have built a device that makes nurses *more* trusting of a *less* trustworthy alarm — the worst possible combination. Alarm fatigue isn't cured by silence; it's cured by *raising the signal-to-noise ratio without dropping signal.* F4 must ship with a pre-specified bound on missed/delayed true alarms (sensitivity floor, with confidence interval), measured on a labeled real-alarm dataset — not just an aggregate "45% fewer alerts" headline. Until that bound exists, F4's positioning pillar is "Safety" in name only.

R2 already gestures at this ("over-promising vs real-world non-actionable-alert reduction") — but R2 is framed as a *marketing* risk. It's a *patient-safety* risk. Re-own it under Clinical + Risk *and* Human Factors, with the sensitivity floor as an acceptance criterion, not a claim to walk back later.

## Feature-by-feature (my wheelhouse)

- **F4 (Alerts Engine v1)** — Conditional. Add the suppressed-true-alarm bound and a human-factors validation that nurses can still distinguish actionable from filtered. This is opioid-context PCA; borrow nothing from general infusion (same caution R1 rightly applies to F6).
- **F5 (Clinical Surveillance)** — Like it. Near-miss/alarm analytics is how you *measure* whether F4 actually helped post-deployment. Make F5 the closed loop that validates F4's bound in the field, not just a dashboard.
- **F7 (Ambulatory home PCA)** — This is the highest-consequence human-factors leap in the whole plan, and R3 is right to flag it. Opioid PCA with a patient or family caregiver as the user — not a trained nurse — changes everything about alarm design: the alarm has to be *understood and acted on by a layperson*, often at night, possibly impaired. Don't port the hospital alarm logic. F7 needs its own summative usability study with representative home users, and Pennathur is the right anchor.
- **F6 (Predictive monitoring)** — Promising but downstream of F4's discipline. If you can't bound suppressed true alarms on v1, you can't be trusted to bound them on a predictive v2.

## My one piece of advice

Put a single number on the roadmap and defend it: the maximum acceptable rate of suppressed or delayed true alarms for F4, with its measurement method. Every "fewer alarms" program that skipped that number became a recall waiting to happen. Make it your acceptance gate, not your apology.

## Findings I corroborate

- **F-2** — F6's borrowed-number transferability problem applies to F4's alarm figures too.
- **F-3** — F4 alarm-reduction claim lacks a suppressed-true-alarm / sensitivity bound (my primary objection).
- **F-12** — alarm over-suppression is a missed-critical-alarm use error; R2 is mis-framed as marketing, it is patient-safety.
- **F-11** — F7 home PCA needs a layperson-specific summative usability study; hospital alarm logic must not be ported.

**My verdict:** _Conditional support_ — strong roadmap, but I will not endorse F4 until it carries a pre-specified suppressed-true-alarm bound, not a count reduction.
