---
title: "KOL Opinion — Dr. Evan Kirkendall (Smart-Pump Safety / CDS / Pediatrics)"
kol_id: KOL-0002
parent_analysis: commercial-roadmap-kol-review
agent: kirkendall-evan
role: kol-panel
specialty: "Smart-pump safety, pediatric medication errors, real-time safety-event detection, CDS"
created: 2026-06-04
---
> _Demo sample data — not for clinical use. Simulated KOL persona opinion for the PDLC_DEMO; not real collected feedback._

## My overall take

I'll be direct: this is a thoughtful roadmap, and I'm glad someone is finally treating PCA intelligence as a product category rather than a feature checkbox. The strategic instinct — that the decisive gap in this market is the absence of predictive monitoring, and that reactive-alarm incumbents are vulnerable there — is correct. I've spent fifteen years cataloging smart-pump errors and living inside alarm-fatigue data, and I can tell you the wedge you've identified (F4/F5/F6) is real.

But my enthusiasm is conditional. The roadmap repeatedly states *effect sizes* — "35% alert reduction," "15–30 min early warnings," "60% adverse-event reduction" — as if they were properties of the device rather than claims that must survive a sensitivity/specificity analysis in a specific population at a specific care intensity. In my world, an alarm-reduction number with no false-negative denominator is not evidence; it's marketing. The plan's own R1/R2 risks name this honestly, which is why I'm a *qualified yes* rather than a skeptic.

## What I like

- **F5 (Clinical Surveillance / near-miss analytics) sequenced in Y2, ahead of predictive F6.** This is exactly right. You cannot build credible predictive monitoring without first instrumenting the near-miss and non-actionable-alert substrate. F5 is the labeled-data engine for F6 — treat it as infrastructure, not a standalone app.
- **The razor + subscription model funding $24M of predictive development out of installed-base revenue.** It means F6 doesn't have to ship prematurely to pay for itself.
- **R1's insistence that the warning claim be substantiated for *opioid/PCA* context, not borrowed from general infusion.** Opioid-induced respiratory depression has a different physiologic signature and time-course than occlusion or infiltration. Borrowing a general-infusion warning curve would be a clinical error.

## What worries me most

**Pediatrics is invisible.** The roadmap names eight KOLs, three care-setting expansions, and nine features — and not one word about weight-based dosing, neonatal/PICU concentration limits, or the fact that pediatric PCA (and PCA-by-proxy) is a distinct, higher-consequence use case. I am a pediatric hospitalist; if you list me as a KOL anchor on F4/F5/F8 you are implicitly claiming pediatric credibility you have not designed for. **Decide explicitly: is peds in scope or out?** "Out for now" is a defensible answer. Silent ambiguity is not — it will surface as a labeling and post-market problem.

My second worry is **alert-burden specificity in vulnerable populations.** A "35% reduction in non-actionable alerts" averaged across an adult med-surg floor can still *increase* clinically meaningful false-negatives in a neonate, where physiologic variability is enormous and the cost of a missed deterioration is catastrophic. Population-stratified specificity, not a single headline number, is what I'll judge F4 and F6 on.

## Feature-by-feature (my wheelhouse)

- **F4 — Alerts Engine v1 (alarm filtering).** My domain. Demand a confusion matrix, not a reduction percentage. The metric that matters is *non-actionable alerts suppressed per true-positive missed*. Commit to a hard floor on sensitivity for respiratory-depression-class alerts — those must never be filtered.
- **F5 — Clinical Surveillance / near-miss analytics.** Mine, and the most under-valued item on the list. Its real value is generating the labeled near-miss corpus that makes F6 trainable and auditable. Fund it as a data platform; fund the surveillance-event taxonomy explicitly — pediatric AE terminology is not free.
- **F6 — Predictive monitoring.** Strong wedge, but the 15–30 min number is a population claim. Report lead-time *and* false-alarm rate together; a 20-minute warning that fires ten times a shift is alarm fatigue wearing a lab coat.
- **F8 — Dose-personalization decision support.** This is where pediatrics becomes unavoidable. Dose personalization without weight-banded guardrails is the single highest-risk CDS item here. I'd gate F8 on an explicit pediatric in/out decision made back at F4.

## My one piece of advice

Make one decision now, in writing: **is the pediatric population in or out of this roadmap's scope?** Every alarm, surveillance, and CDS claim downstream inherits that answer. Pick one and design to it.

## Findings I corroborate

- **F-2** — effect-size claims (alert/AE reduction, 15–30 min warning) are stated as device properties without sensitivity/specificity denominators.
- **F-3** — alarm-fatigue claim (F4) risks over-promising vs real-world non-actionable-alert reduction; needs a confusion-matrix commitment.
- **F-12** — a single headline number can hide an increased false-negative rate in vulnerable subgroups.
- **F-13** — F8 dose-personalization lacks weight-banded guardrails and a population-scope gate.

**My verdict:** _Qualified yes_ — the predictive/alarm wedge is real, but I need population-stratified sensitivity/specificity and an explicit pediatric in/out decision.
