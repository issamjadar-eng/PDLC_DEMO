---
title: "KOL Opinion — Dr. Susan Braithwaite (Insulin Infusion / Ambulatory-Pump Analogy)"
kol_id: KOL-0003
parent_analysis: commercial-roadmap-kol-review
agent: braithwaite-susan
role: kol-panel
specialty: "IV insulin infusion protocols, ICU glucose management, ambulatory-pump perspective"
created: 2026-06-04
---
> _Demo sample data — not for clinical use. Simulated KOL persona opinion for the PDLC_DEMO; not real collected feedback._

## My overall take

Let me be honest up front: PCA is not my specialty. I have spent twenty-five years on intravenous insulin protocols and ICU glucose management — algorithms, ambulatory patch pumps, the slow grind toward closed-loop. I was asked here precisely *because* your roadmap leans on my world: it borrows the insulin-patch-pump form factor (D-COMM-1.8, Omnipod/Tandem as the F7 design benchmark) and the AI-personalization analogy (F8) and applies them to an opioid product. So my value is not to bless your PCA decisions — it is to tell you where the analogy I know intimately *holds*, and where I think it is quietly dangerous. I am broadly supportive of the form-factor benchmarking and deeply cautious about the personalization and home-safety borrowings.

## Where the insulin/ambulatory analogy holds

The **hardware form-factor benchmark is sound and I endorse it.** Insulet and Tandem have done you an enormous favor: they proved that patients will wear a lightweight, tubeless-or-low-profile, multi-day-battery device on the body for days at a time, and that the supply chain, adhesives, occlusion sensing, and reservoir mechanics for an ambulatory wearable are solved engineering problems. Targeting a 180 g / 7-day class against Omnipod's 72-hour benchmark (D-COMM-1.8) is a reasonable, evidence-grounded design goal. The *mechanical and human-wearability* analogy transfers cleanly.

The **connected-fleet and analytics analogy holds too.** Diabetes went through exactly the cloud-telemetry, remote-data, drug-library-governance evolution your Cloud Suite describes. F1–F3 (Y1) mirror the CGM/pump-data ecosystem maturation, and that path is well-trodden. No objection there.

## Where it dangerously does NOT (opioid vs insulin failure modes)

Here is where my expertise becomes a warning rather than an endorsement.

**Failure-mode timescale and reversibility are not comparable.** When an insulin pump over-delivers, the patient becomes hypoglycemic over *tens of minutes to hours*; there are physiologic warning signs, the patient is usually conscious enough to act, and the antidote (oral or IV glucose) is fast, cheap, and ubiquitous. Opioid over-delivery produces **respiratory depression that can become irreversible in minutes**, often *without* the patient noticing — they simply stop breathing. The therapeutic margin is narrower and the failure is faster, quieter, and far less forgiving. Borrowing the patch-pump form factor is fine; borrowing its *risk tolerance* would be a serious error. An occlusion-sensing or delivery-fault spec that is "good enough for insulin" is **not** automatically good enough for opioid.

**Closed-loop took us years — and we had a fast, cheap antidote.** Automated insulin delivery required a decade-plus of evidence, hybrid (not full) autonomy, and conservative guardrails, *even though* hypoglycemia is more forgiving than respiratory arrest. Your Y5 "closed-loop-assist research track" (D-COMM-1.3) should inherit that humility and then add margin, not subtract it. Do not let the diabetes precedent make closed-loop opioid delivery *sound* mature. It is the opposite.

**Personalization is the analogy I worry about most.** In insulin, personalization (F8's cousin) means adjusting toward a measurable, continuously-sensed target (glucose) with a real-time feedback signal. **Opioid analgesia has no equivalent continuous, objective biomarker** — pain is subjective and respiratory drive is the safety variable, not the efficacy variable. A dose-personalization engine that optimizes for reported analgesia without an objective respiratory-safety closed loop is optimizing the wrong axis. This is precisely your R1/R3 risk, and I think it is under-weighted.

## Feature-by-feature (F7, F8, personalization)

- **F7 (Ambulatory PP3500-A, D-COMM-1.4 / 1.8):** Support the *form factor*; flag the *setting*. Insulin patch pumps live in an unsupervised home because insulin failure is slow. Opioid in an unsupervised home (R3) is a categorically higher-consequence leap. The hardware benchmark transfers; the use-environment safety case does **not** — it must be built fresh with mandatory respiratory monitoring (e.g., capnography/SpO₂) as a gating assumption, not an accessory.
- **F8 (Dose personalization, D-COMM-1.4):** Highest-sentiment opportunity in your roster, and the place the insulin analogy is most seductive and most wrong. Require an objective respiratory-safety feedback variable in the loop before personalizing dose. Without it, the +0.55 sentiment is enthusiasm for a capability whose safety substrate doesn't yet exist.
- **Personalization generally:** Demand the biomarker. If you can't name the continuous safety signal, you can't borrow my closed-loop story.

## My one piece of advice

**Borrow the form factor, never the failure-mode tolerance.** Write into the roadmap an explicit, one-line "non-analogy clause" beside D-COMM-1.8 and F8: *"Insulin-pump precedent informs hardware and connectivity only; opioid respiratory-depression risk requires an independent, more conservative safety case with a continuous respiratory-safety signal."* That single sentence will stop a future engineer from importing an insulin-grade spec into an opioid device.

## Findings I corroborate

- **F-2** — predictive evidence must be PCA/opioid-specific, not borrowed; the analogy-borrowing failure in another guise.
- **F-4** — home/ambulatory opioid use-safety is the highest-consequence leap; the insulin-patch benchmark imports a far more forgiving failure mode.
- **F-13** — F8 personalization lacks an objective opioid safety biomarker (respiratory drive), so it optimizes the wrong axis.
- **F-10** — the closed-loop / autonomy timeline (Y5) is over-optimistic given how long hybrid insulin autonomy took with a more forgiving failure mode.

**My verdict:** _Support hardware/connectivity borrowings; oppose risk-tolerance borrowing_ — opioid's fast, irreversible respiratory failure forbids importing insulin-grade tolerance into F7/F8.

_(Note: PCA is outside my core specialty; I defer to the PCA-specialist KOLs on alarm-fatigue and DERS specifics and speak only to the ambulatory-infusion analogy.)_
