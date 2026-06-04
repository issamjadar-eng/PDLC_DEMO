---
title: "KOL Opinion — Dr. Parth Shah (Alert Fatigue / Alert Optimization)"
kol_id: KOL-0008
parent_analysis: commercial-roadmap-kol-review
agent: shah-parth
role: kol-panel
specialty: "Smart-pump alert fatigue, alert optimization, evidence-based alert-burden reduction"
created: 2026-06-04
---
> _Demo sample data — not for clinical use. Simulated KOL persona opinion for the PDLC_DEMO; not real collected feedback._

## My overall take

I've spent ten years studying why clinicians stop trusting smart-pump alarms, and the short version is this: **the failure mode is never "too few alerts." It's too many of the wrong ones, which teaches people to ignore all of them — including the one that would have saved a life.** So when I read a roadmap that puts an "Alerts Engine v1 — alarm-fatigue reduction" (F4) and a "predictive monitoring" engine (F6) at its center, I'm genuinely encouraged. You're aiming at the right wound. But the way the supporting evidence is framed worries me, because almost every number you've borrowed is *one-sided*. A "% reduction" in alerts, with no paired statement of what it cost you in missed true events, is — bluntly — a marketing number, not a safety claim. In my field that asymmetry is the original sin.

## What I like

- **F4 is positioned as a Safety pillar, not an efficiency play.** Good. Alarm-fatigue reduction is a patient-safety intervention. If it were framed as "nurse productivity," I'd be much more skeptical.
- **R2 already names the over-promise risk** ("alarm-fatigue claims over-promising vs real-world non-actionable-alert reduction"). Someone on this team already sees the trap. I want to push that risk from a one-liner into a measurement contract.
- **PCCP vehicle for F4 (category B).** Alert logic *must* be retrainable post-clearance, because alert thresholds drift with every drug-library change and every new care unit. Shipping the alert engine under a PCCP envelope is exactly right.
- **You separated v1 (filtering) from v2 (prediction).** Filtering existing alarms and predicting future events are different evidentiary beasts. Conflating them is a common mistake; you didn't.

## What worries me most (alert-optimization lens)

**The 45% / 80% / 35% numbers are general-infusion figures, and PCA is not general infusion.** Your own market doc rates its PCA relevance as "Medium" and says PCA "is mentioned only by extension." The 45% non-actionable-alert reduction and "80% reduction in alert deviation" come from a smart-pump *infusion* fleet reference — continuous and intermittent IV delivery. PCA's alarm population is dominated by **patient-demand events, lockout-interval hits, and respiratory/sedation concerns from opioids** — a fundamentally different mix with a far higher consequence on the false-negative side. A suppressed occlusion alarm on a maintenance fluid is an inconvenience; a suppressed signal on an over-sedated opioid patient is a code. You cannot transfer the percentage without transferring the *consequence model*, and nobody has.

Second: **every reduction figure in the roadmap is missing its denominator-mate.** "45% reduction in non-actionable alerts" is meaningless to me without "...at X% sensitivity to true actionable events, with a measured false-negative rate of Y." A filter that drops 45% of alerts is trivial to build — drop the right 45% and you're a hero; drop the wrong 45% and you've built a sedation-detection bypass with a friendly dashboard.

## Feature-by-feature (my wheelhouse)

- **F4 — Alerts Engine v1.** Endorse the intent; reject the current evidence framing. Before this ships, I want an **actionability-classified alarm taxonomy for PCA specifically** and a paired metric: non-actionable-alert reduction *reported alongside* true-alert sensitivity and false-negative rate, validated on PCA traffic, not borrowed infusion traffic. The 35%-via-personalization and 45%-filtering numbers should be treated as *hypotheses to be re-derived on PCA data*, not commitments.
- **F6 — Predictive monitoring (occlusion / infiltration / deterioration).** The "15–30 min early warning" is the headline I distrust most. Early-warning systems live or die on **alert burden per true positive** — the 73% deterioration sensitivity in your doc implies a 27% miss rate, and the precision (false-alarm load) isn't stated at all. For an opioid PCA population, deterioration = respiratory depression; the cost of a false negative is maximal. F6 needs a prospective PCA-context PPV/sensitivity study, full stop. This is correctly flagged as R1 — keep it there.
- **F5 — Clinical Surveillance / near-miss analytics.** Lower risk, and actually the right *substrate*: surveillance analytics is where you should be measuring your own alert actionability over time. I'd make F5 the evidence engine that continuously validates F4/F6 in the field.
- **F8 — Dose personalization.** Personalized analgesia is promising but it changes the alarm baseline per patient — your alert thresholds become patient-relative. Don't ship F8 until F4's measurement contract can handle moving baselines.

## My one piece of advice

**Adopt a two-sided alert metric as a hard gate for F4, F6, and F8, and write it into the roadmap now.** No alert-reduction claim ships — internally, to FDA, or in marketing — unless it's stated as a *pair*: actionable-alert sensitivity (and false-negative rate) reported in the same breath as the non-actionable-alert reduction. One-sided "% reduction" claims are how good engineers ship dangerous filters. Make the pairing a deliverable, not an afterthought.

## Findings I corroborate

- **F-2** — the 45%/80%/35% alert figures are general-infusion (PCA-relevance "Medium"); they must be re-derived on PCA traffic before commitment.
- **F-3** — every reduction figure lacks its paired sensitivity/false-negative metric; this is my core objection.
- **F-12** — a one-sided filter is a missed-critical-alarm use error waiting to happen.

**My verdict:** _Support in intent, conditional on evidence_ — won't endorse any alert-reduction claim until it's reported two-sided (sensitivity and false-negatives paired) on PCA data, not borrowed infusion numbers.
