---
id: recs-risk-management
parent_analysis: competitive-threat-assessment
type: recommendation
authored_by: agent:risk-management
created: 2026-08-06
---

# Risk Assessment — Competitive-Threat Risk Register (PP3500 / PainEase PCA Advanced)

> _Demo sample data — not for clinical use. GlobalLogic device figures are fabricated by construction and are graded `INTERNAL-DEMO` throughout._

**Scope note.** This is a **business/program risk register** for competitive threats. It is **not** an ISO 14971 hazard analysis, and its scales are **not** the device's harm-severity scales. What is borrowed from ISO 14971 is the *method*: explicit scales, stated reasoning behind every rating, controls separated into preventive and contingent, residual exposure evaluated after control, and the refusal to accept a "mitigation" that nobody owns and nobody can verify. The section *Coupling to the ISO 14971 risk file* identifies where a competitive threat reaches into the device's safety file — that boundary is where this advisor's authority actually sits.

---

## What good looks like

A competitive-threat register that survives a board review or a diligence data room does six things. `OPINION` — risk-practice judgment, not a cited rule.

1. **It publishes its scales before its ratings.** A register with likelihood and impact columns and no defined bands is unauditable — nobody can tell whether "High" means 30% or 90%.
2. **It states reasoning, not just a number.** The rating is a conclusion; the evidence and inference chain are the artifact. A reviewer must be able to reject the rating without rejecting the risk.
3. **It separates preventive from contingent control.** Preventive moves likelihood; contingent moves impact. Registers that blur them over-credit themselves, because a plan to *respond* gets counted as a plan to *prevent*.
4. **Every risk carries a leading indicator and a trigger threshold.** Without the trigger, the register is a document; with it, it is a control.
5. **It names the risks that are not mitigable.** A register where everything has a tidy mitigation is a reassurance exercise.
6. **It evaluates residual exposure explicitly, and the acceptance is a named human's decision.** **This advisor does not accept residual exposure on the program's behalf.** Every "acceptable?" verdict below is a recommendation to the named owner.

---

## Scales

**These are business-exposure scales and must not be mapped to or compared against the ISO 14971 probability/severity scales** that will live in the (currently non-existent) `risk_management_plan` for `pca-device`. Conflating a commercial impact band with a harm-severity band is exactly the defect doctype governance exists to prevent.

**Likelihood** — probability the threat materialises *within its stated horizon*.

| Band | Meaning | Test |
|---|---|---|
| **L5** Near-certain (>80%) | The mechanism is already operating and observable today | Can I point at it happening now? |
| **L4** Likely (50–80%) | Mechanism established; only timing uncertain | Has it happened to a comparable program? |
| **L3** Possible (20–50%) | Plausible mechanism, no confirming instance yet | Is there a live precedent in an adjacent segment? |
| **L2** Unlikely (5–20%) | Requires a specific enabling event | What would have to be true first? |
| **L1** Remote (<5%) | Requires several independent enabling events | — |

**Impact** — consequence to the program if it materialises, unmitigated.

| Band | Meaning |
|---|---|
| **I5** Program-ending | Invalidates the anchor thesis, blocks lawful sale, or removes the addressable market |
| **I4** Major | Forces re-plan of one or more flagship years, or forfeits a segment or channel |
| **I3** Moderate | Costs a release cycle, a named claim, or a filing round; recoverable inside the plan |
| **I2** Minor | Absorbed by existing contingency |
| **I1** Negligible | Noise |

**Exposure** = L × I. **Critical** ≥16 · **High** 10–15 · **Moderate** 5–9 · **Low** ≤4.

**Control-effectiveness discount.** A mitigation may only be credited with moving a band if it has (a) a named owner, (b) a dated artifact, and (c) an acceptance criterion someone else can check. Mitigations failing any of the three are recorded but credited **zero** band movement. This is the single most important rule here — it is what stops a mitigation column from manufacturing false assurance.

---

## Assessment of the existing R1–R5

`commercial-strategy.md` L142–154 defines D-COMM-1.9 as a five-row table with exactly two columns: **Risk** and **Owning discipline(s)**. No likelihood, no impact, no horizon, no indicator, no trigger, and **no mitigation of any kind** — for any of the five. `ARITHMETIC`.

D-COMM-1.9's own "Why" (L152) is candid that the purpose was to give a KOL review something concrete to probe. Judged against that purpose it succeeds. Judged as a risk register it is a **risk *identification* list**, and the gap between identification and control is the whole of ISO 14971 §7 in the safety analogue.

| # | Risk as written | Specified to a verifiable standard? | The specific defect |
|---|---|---|---|
| **R1** | Predictive-monitoring SaMD clinical-evidence sufficiency | **Closest to adequate** — falsifiable, and correctly anticipates the transferability objection | No control. And it is now **understated**: there are **zero** PubMed hits for infusion-pump ML occlusion or infiltration prediction (`SUBSTANTIATED`, §A.9). There is no general-infusion evidence base to *borrow from*, so the risk is not "borrowed claim" but "no claim exists at all" |
| **R2** | Alarm-fatigue claims over-promising | No | Attributes the benefit to the wrong mechanism — EMR **integration** cut hard-limit alerts −50.3%, soft-limit −30.4%, DERS compliance to 96.1%, all p<0.001 (§B.3). The demonstrated lever is integration, not intelligence. See the worked example |
| **R3** | Ambulatory home-PCA use-safety | No | Correctly identified as the highest-consequence HF leap, then left with a discipline label. The named hazard the literature supplies — **proxy activation defeating PCA's intrinsic consciousness interlock** (Ocay 2018) — is not stated, so nothing downstream can trace to it |
| **R4** | Regulatory sequencing slip | No | No quantification, despite real data: median AI-enabled 510(k) **142 days**, P90 **266 days**, **34.6% exceed six months** (§C.7). A serially-gated five-year plan compounds that tail; the register does not say so |
| **R5** | Reimbursement reliance on cost-avoidance | No | Single posture applied across inpatient-DRG and home/DME settings |

**Verdict.** All five are endogenous execution risks. None carries a control. R1 and R3 reach into the ISO 14971 file, and both are un-actionable there because **every risk-management role for `pca-device` resolves to `null`** — `risk_management_plan`, `software_risk_assessment`, `hazard_analysis`, `hazard_traceability_matrix`, `fmea`, `risk_management_report`, `benefit_risk_analysis`. `SUBSTANTIATED`, read this pass.

---

## The competitive-threat risk register

| ID | Threat (one falsifiable sentence) | L | I | Exposure | Horizon | Owner |
|---|---|---|---|---|---|---|
| **R6** | The predictive wedge is pre-empted by a *deterministic* closed-loop interlock the incumbent already ships and has already cleared | L4 | I4 | **16 Critical** | now | Commercial + Clinical |
| **R7** | IV PCA is evicted from ERAS-covered elective pathways, shrinking the primary Y1–Y3 segment | L5 | I3 | **15 High** | 1–2 yr | Commercial + Clinical |
| **R8** | Absence from the target IDN's GPO agreement makes the device non-evaluable regardless of specification | L4 | I4 | **16 Critical** | now | Commercial |
| **R9** | The competitor-quality window closes before we hold any artifact capable of making a quality claim | L4 | I4 | **16 Critical** | 1–2 yr | Quality + Regulatory |
| **R10** | Incumbents defend on consumables margin, a lever a pump-plus-software entrant does not hold | L4 | I3 | **12 High** | 1–2 yr | Commercial |
| **R11** | A standalone PCA pump is not evaluated against platform incumbents at all — it is out of the comparison | L4 | I5 | **20 Critical** | now | Commercial + Systems Eng |
| **R12** | We resource AI while the demonstrated differentiator is EHR↔pump auto-programming, which we have not filed for | L4 | I4 | **16 Critical** | now | Systems Eng + Regulatory |
| **R13** | Time pressure to remediate a field issue produces an unfiled software change — the exact ICU Medical finding | L3 | I5 | **15 High** | 3–5 yr | Quality + Regulatory |
| **R14** | The PCCP is scoped for detection-accuracy changes, foreclosing the later pivot to advance prediction | L4 | I4 | **16 Critical** | now | Regulatory + Risk |
| **R15** | A PCA-first filing has no same-code predicate newer than 2017, weakening the SE anchor | L3 | I4 | **12 High** | 1–2 yr | Regulatory |
| **R16** | Cybersecurity — a moving guidance target plus a contractual purchase gate — blocks the sale outright | L4 | I4 | **16 Critical** | now | Cybersecurity + Regulatory |

**Disposition of the commercial advisor's proposals:** R6 **kept, re-founded** (the mechanism was wrong); R7 **kept, recalibrated**; R8 **kept as written**; R9 **kept and merged** with the empty-DHF exposure; R10 **kept as written**; R11–R16 **added**.

### R6 — Incumbent pre-emption of the predictive wedge

**Threat.** BD's already-cleared, already-shipping deterministic capnography-triggered PCA Pause satisfies the OIRD safety requirement well enough that a *predictive* claim never becomes a purchase-decision variable.

**Why the commercial framing was wrong, and why the risk survives anyway.** `recs-commercial.md` R6 assumed incumbents could ship predictive alarming to an installed fleet cheaply. The AI evidence contradicts the premise: **zero** of 1,524 devices on FDA's AI-Enabled Medical Device List is an infusion pump, checked three ways; all ten PHC infusion-safety-software clearances are rules-based; **zero** clinical outcome studies exist for ML-based pump prediction (§A.1, §A.5, §A.9 — `SUBSTANTIATED`). No incumbent is one release from predictive.

The real pre-emption is already deployed and needs no AI. BD's EtCO₂ module *"pauses a PCA infusion if the patient's respiratory status falls below hospital-defined limits"* (`SUBSTANTIATED (vendor source)`), and the auto-pause — not the alarm — is the behaviour with published field evidence: McCarter 2008, 9 of 634 PCA patients with respiratory depression requiring intervention, *"in all cases the capnography alarm was the impetus… the pulse oximetry monitor had not alarmed,"* with the pump having automatically paused.

**L4** — the mechanism is deployed today; residual uncertainty is only whether buyers treat "deterministic pause at a threshold" as sufficient. `INFERRED` — fails if a buyer cohort demonstrably prefers lead-time warning, for which no evidence was found either way.
**I4** — D-COMM-1.1 makes predictive monitoring the five-year throughline; losing it forfeits the differentiation spine.

**Leading indicator.** Count of RFP/VAC question sets specifying *lead-time* (minutes of advance warning) versus *threshold* (pause at a set EtCO₂/RR/SpO₂), reviewed quarterly.
**Trigger.** Two consecutive quarters in which ≥80% of received specifications ask only for threshold behaviour → demote predictive from throughline to funded option.

**Preventive.** Re-found D-COMM-1.1's baseline on "capnography-triggered pause exists; our delta is X minutes of lead time at stated sensitivity/specificity" — a testable delta, not an absence claim. *Owner:* Commercial Lead. *Artifact:* D-COMM-1.1 source block. *Acceptance:* no sentence in the assembled strategy asserts incumbents are reactive-alarm-only.
**Contingent.** Specify a *deterministic* threshold-pause capability in the baseline requirement set so the device is competitive on the interlock axis with no predictive claim at all. *Owner:* Systems Engineering. *Acceptance:* a requirement exists for monitor-driven therapy suspension with a stated latency budget, traced to the OIRD hazard.

**Residual.** L3×I3 = **9 Moderate**, contingent on the deterministic interlock being funded. **Recommend acceptable only with that condition** — without it residual stays at 16, because the predictive claim then carries the entire competitive case alone.

### R7 — Category contraction from ERAS / opioid stewardship

**L5.** Measured, not forecast: PCA use 63%→0.5% in colectomy, 61.6%→1.4% in spine, 68.4%→0% in ventral hernia, 88%→10% in donor nephrectomy, 50.6%→32.1% in gynae-onc, and 27%→13% over 2009–2018 in 86,308 Premier lobectomies (all `SUBSTANTIATED`). PCA at 5.51% CAGR against 7.3–8.2% for infusion overall.
**I3, a downgrade from the commercial framing.** A segmentation event, not a market exit: no source argues IV PCA is obsolete, ERAS-labelled NHS protocols still specify routine PCA in 2022, and the guideline-to-ward-practice lag is *"years wide."* A threat model reading only guidelines times this too early.

**Leading indicator.** ERAS-protocol adoption at named target accounts, as a share of the target list; secondarily, PCA line-items in those accounts' order sets.
**Trigger.** >50% of the top-20 target list has published an ERAS pathway covering its highest-volume elective service line → re-weight Y1–Y3 targeting.

**Preventive.** None — the force is exogenous.
**Contingent.** Subdivide D-COMM-1.2 segment 1 into ERAS-exposed and ERAS-resistant populations and weight Y1–Y3 to the second. *Owner:* Commercial Lead with Clinical Affairs. *Acceptance:* the segment table names both sub-populations with separate volume assumptions, and segment 3 is re-tested for a start earlier than Y3.

**Residual.** L5×I2 = **10 High** post-retarget, and it does not go lower. **Recommend accept-and-monitor.** Note the trade: ERAS-resistant populations are smaller, more fragmented and cost more per placement — price it before adopting.

### R8 — Channel-access failure (GPO evaluability gate)

**L4 / I4.** `SUBSTANTIATED` — GPO contract status is a gate, not a discount; TCO dominates unit price; displacement happens at fleet-replacement events. I4 rather than I5 because non-GPO channels (ambulatory/home, alternate-site) remain reachable.

**Leading indicator.** Count of top-N IDNs where the device sits on an active agreement, reviewed at each stage gate.
**Trigger.** Zero GPO awards by end of Year 1 → the Year-2 flagship funding decision reopens.

**Preventive.** Add a GPO contract-award milestone to D-COMM-1.3 as a **commercial gate** alongside the regulatory vehicle; add contract coverage to D-COMM-1.7's stage-gate criteria. *Owner:* Commercial Lead + Program Manager. *Acceptance:* the table carries a "Commercial gate" column with a Y1 GPO milestone; a target-account list exists with GPO coverage, fleet age and contract expiry.
**Contingent.** Pre-qualify a non-GPO channel that can absorb Y1–Y2 volume.

**Residual.** L3×I4 = **12 High**. **Recommend NOT acceptable without the Y1 milestone** — the cheapest high-exposure mitigation in the register, and currently absent.

### R9 — The quality window closes before we hold an artifact that can occupy it

**L4.** The window is real and dated. ICU Medical holds FDA Warning Letter CMS 702535 (2025-04-04). BD is under an amended consent decree with $15k/day/$15M-per-year exposure, an open FDA review of May-2024 Infusion QMS observations, remediation *"substantially complete over the next calendar year"* per its FY2025 10-K, and four Class I events since return-to-market. Windows of this shape close on a 24–36 month scale (`INFERRED` from BD's own stated horizon).
**I4.** The only wedge in this cluster not resting on `INTERNAL-DEMO` figures.

**The compounding fact.** The wedge cannot be claimed. `pca-device` resolves risk, hazard, FMEA, RMR, benefit-risk, cybersecurity-plan and PSUR roles to `null`; verification protocols and reports resolve to folders with `file_count: 0`; `postmarket-strategy.md` is a nine-line stub reading *"awaiting content."* And "we have never had a recall" from a firm with 1,547 units in the field is a denominator artifact, not a quality claim.

**Leading indicator.** Two paired counts on one dashboard: competitor remediation milestones closing, against our own null-resolving DHF roles closing.
**Trigger.** ICU Medical's CMS 702535 close-out published, **or** BD's Infusion QMS 483 review closed, **while** ≥3 of our risk-management roles remain `null` → the quality-led narrative is withdrawn from commercial use.

**Preventive.** A written statement of which DHF artifacts must exist before a quality-posture claim is externally defensible, with dates. *Owner:* Quality Engineering + Regulatory Affairs. *Acceptance:* `risk_management_plan`, `hazard_analysis` and `hazard_traceability_matrix` resolve to real files; commercial makes no quality claim before they do.
**Contingent.** Substitute a purchasable risk-transfer offer — fleet-migration support, recall-contingency swap terms, guaranteed set supply.

**Residual.** L4×I3 = **12 High** even after mitigation, because the closing date is set by the competitors' regulators. **Recommend accept-and-monitor with the trigger armed.**

### R10 — Consumables lock-out

**L4 / I3.** `SUBSTANTIATED` for the structure: ICU Medical FY2024 Infusion Consumables $1.11B vs Infusion Systems $684.2M — 1.6×. `INFERRED` for the pricing-response mechanism (standard razor-blade defence; fails only if the incumbent's consumables margin is already at floor).

**Leading indicator.** Set-price-per-therapy quoted by incumbents in accounts where we are shortlisted.
**Trigger.** Two bids lost on fleet-level TCO while winning on device specification → the business model, not the plan, is what needs changing.

**Preventive.** None available. **Contingent.** Compete on a fleet-level TCO model pricing software licences (10–15% of replacement value annually), service, and EMR-integration cost. *Acceptance:* a TCO model exists and is used in every bid; no bid is submitted on unit price alone.

**Residual.** L4×I3 = **12 High**, unchanged. See *Risks I judge not mitigable*.

### R11 — Platform-bundle displacement

**L4 / I5 — the highest single exposure in this register.** `SUBSTANTIATED` for the mechanism: BD ships PCA, LVP, syringe and EtCO₂ modules on one chassis with the capnography module able to pause the PCA infusion. `SUBSTANTIATED` for the structural corroboration: **31 MEA-primary 510(k)s in the entire history of the code, most recent 2017-08-29**, while modern PCA capability clears under **FRN as a module** on a platform submission. I5 because this does not cost a claim or a year — **it removes the evaluation**.

The PP3500 SAD confirms the exposure from our side: §1 scopes the filing to the on-device software alone, with Adapter and Cloud pulled in *"via the composition manifest (cybersecurity only)."* A defensible filing decision and a weak *platform* posture — the two should not be confused.

**Leading indicator.** Share of target accounts already standardised on a modular chassis versus mixed-fleet.
**Trigger.** >60% of the top-20 target list is single-platform standardised → the hospital-inpatient motion is re-scoped to module-supply or partnership, and ambulatory is accelerated.

**Preventive.** None available to a standalone device. **Contingent.** Two routes, and the program must pick one deliberately: (a) target segments where no platform incumbent has standardised — ambulatory, home, alternate-site, the tier where Moog, Eitan, Zyno and Summit are actively clearing; or (b) build the platform story explicitly, with the Connectivity Adapter and Cloud Suite presented as one system rather than adjacent filings. *Acceptance:* a written decision exists selecting (a) or (b), with the consequence recorded.

**Residual.** L4×I4 = **16 Critical** under (a); L3×I4 = **12 High** under (b). **Recommend NOT acceptable undecided** — leaving this unchosen produces the "not in the comparison" outcome by default.

### R12 — Interoperability table-stakes deficit

**L4 / I4.** `SUBSTANTIATED` throughout §B: ~87.9% of US hospitals have smart pumps but only **13.4%** have EHR→pump auto-programming and 85.1% still document manually (ASHP 2021); interoperability reduced errors 15.4–54.8% for directly impactable errors; EMR integration lifted DERS compliance to **96.1%** and cut hard-limit alerts 50.3%; keystrokes fell 15→2 because integration *removes the option* of bypassing the drug library. PCA-specific: **6.5% of MAUDE IV-PCA events were operator error, 81% of those misprogramming, roughly half associated with harm** (Schein 2009) — the harm auto-programming directly removes. All five majors hold PHC clearances; we hold none.

**Leading indicator.** PHC-class clearances held versus the five majors; EHR integration certifications achieved.
**Trigger.** Entering any competitive bid without a demonstrable auto-programming path → escalate to the Year-N funding decision.

**Preventive.** Move auto-programming from backlog to a baseline requirement with a filing vehicle. *Owner:* Systems Engineering + Regulatory Affairs. *Acceptance:* requirements exist for bi-directional auto-programming and auto-documentation, and the standards matrix cites the **2022** editions of ANSI/AAMI/UL 2800-1 and sub-parts and **ANSI/AAMI 2700-1:2019, not ASTM F2761**.
**Contingent.** Position auto-programming as the Year-1 clinical-safety story so the alarm-reduction claim rests on the mechanism with published evidence.

**Residual.** L2×I4 = **8 Moderate** if the requirement lands in baseline; **16 Critical** if deferred. **Recommend NOT acceptable as currently planned.**

### R13 — Change-control failure of the ICU Medical shape

**L3 / I5.** `SUBSTANTIATED` for the precedent: FDA holds the Medfusion 4000 and CADD Solis VIP adulterated under §501(f)(1)(B) and misbranded under §502(o) because changes that could significantly affect safety or effectiveness shipped without the 510(k) required by 21 CFR 807.81(a)(3)(i); the aggravating fact is that **the unfiled software was the remedy for a Class I recall**, ICU's *own procedure* said a 510(k) was required, and FDA rejected the label-disclosure workaround as *"not sufficient."* L3 because the failure requires a field event first; I5 because the consequence is adulteration/misbranding — it blocks lawful sale.

`INFERRED`, and this is the generalisable lesson: **a Class I recall remedy is, by construction, a change to a risk control measure.** The pressure to remediate fast opposes the obligation to file first, and that opposition is structural for every connected-pump manufacturer.

**Leading indicator.** Count of field-corrective software changes shipped, and for each, whether a filing-decision record exists with a date preceding the release.
**Trigger.** Any field-corrective release reaching a customer without a documented filing decision → immediate hold and CAPA.

**Preventive.** A change-control gate whose filing trigger is *"does this change a risk control measure, or the performance of one?"* — evaluated before release. *Acceptance:* the procedure names risk-control modification as a filing trigger, cites 21 CFR 807.81(a)(3)(i), and records that a label disclosure is not an accepted mitigation. Note §524B's modification trap: **a Special or Abbreviated 510(k) does not exempt the submission.**
**Contingent.** A pre-authorised emergency-mitigation playbook reaching for labeling, IFU and field-safety-notice controls — the ones that do *not* require a filing — while the submission is prepared.

**Residual.** L1×I5 = **5 Moderate** with the gate; **15 High** without. **Recommend NOT acceptable until the gate exists** — and note it cannot exist today, because the risk-management plan it must hook into resolves `null`.

### R14 — PCCP mis-scoping forecloses the predictive roadmap

**L4 / I4.** `SUBSTANTIATED`, verbatim from the operative guidance (2025-08-18): modifications *"must maintain the device within the device's intended use"* — a **statutory** limit citing FD&C Act §§515C(a)(2) and 515C(b)(2). And Appendix B Modification Scenario 2 is the program's own case in hypothetical form: a monitoring device whose retrained model *"can now also predict physiologic instability in advance of its onset"* — *"The methods used for analysis, performance, and statistics were not specified in the PCCP for predicting a future state… a new marketing submission would be required."* L4 because the default engineering instinct is to file detection first and add prediction later; that is exactly the sequence FDA's example forecloses.

Two compounding constraints: the separate **general-device** PCCP guidance is still **draft, "Not for implementation"**; and the SAD designates the drug library as *"the primary PCCP change envelope"* with the predictive-alarm SaMD an explicit open item — so the scope decision is live and unmade.

**Leading indicator.** Whether the PCCP's Modification Protocol contains a pre-specified analysis-performance-and-statistics method for a *future-state prediction* endpoint, not only for detection accuracy.
**Trigger.** PCCP draft reaching pre-sub without that pre-specification → the predictive roadmap is re-planned as a separate submission with its own timeline and budget.

**Preventive.** Specify the predictive methodology — endpoint definition, lead-time claim, sensitivity/specificity acceptance, statistical analysis plan — **in the baseline PCCP**, and use the Q-Submission Program on the narrow indications-for-use carve-out FDA leaves open. *Acceptance:* the Modification Protocol addresses a future-state prediction endpoint, or the program has recorded a written decision to file prediction separately.

**Residual.** L2×I3 = **6 Moderate** with pre-specification; **16 Critical** without. **Recommend NOT acceptable undecided.**

### R15 — Predicate desert / SE anchor decay

**L3 / I4.** `SUBSTANTIATED`: MEA's most recent clearance is **K162165, 2017-08-29**; FDA's own warning letter states the CADD Solis VIP runs on **K111275, dated 2013-02-01**. L3 rather than L4 because the drought is a coding-practice shift as much as an innovation gap — modern PCA capability clears under FRN as a platform module — and filing under FRN sidesteps most of the exposure.

Two facts that cut the other way and should travel with this risk: De Novo is 2.6% of AI-device authorisations but a real route for novel functions with no predicate; and the category-relevant FDA-recognised standard is **AAMI TIR101:2021** — **IEC 60601-2-24 is NOT FDA-recognised**, and with ANSI/AAMI ID26 withdrawn there is **no FDA-recognised particular safety standard for infusion pumps**. The PP3500 SAD §3 and §7 both list IEC 60601-2-24. That is a correctable defect in a controlled design output, and the kind an FDA reviewer finds immediately.

**Trigger.** Pre-sub feedback questioning the predicate → De Novo assessed before the submission is built.
**Preventive.** Resolve the primary product code (MEA vs FRN) and predicate strategy in a Q-Sub before the evidence package is scoped. *Acceptance:* a written decision exists with FDA feedback attached; the standards matrix removes IEC 60601-2-24 as a *recognised* consensus standard and cites TIR101:2021.

**Residual.** L2×I3 = **6 Moderate**. **Recommend acceptable with the Q-Sub condition.**

### R16 — Cybersecurity as a purchase gate and a moving target

**L4 / I4.** `SUBSTANTIATED` on both limbs. **The target moves:** the governing FDA guidance was reissued 2025-06-27 and again **2026-02-03** (retitled "Quality *Management* System"), superseding twice in eight months. FDA anchors SBOM to the **October 2021 NTIA** baseline while CISA's **2026 Minimum Elements** (2026-07-29) explicitly *"updates and replaces"* it. **The gate is contractual:** HSCC MC2 v2 (November 2025) is co-chaired by Mayo Clinic and by **Premier — a national GPO** — and functions as *"in effect, a pre-negotiated contract"*: SBOM required (#44), KEV notification in 3 business days (#33), patches in 30 days (#31), no OS within 2 years of End of Support at delivery (#40). HHS HICP 2023 sub-practice 9.L.B uses **an infusion pump as its worked example**.

The PP3500 SAD names §524B and an SBOM surface — but `cybersecurity_plan` resolves `null` and `vulnerability_management` resolves to a non-existent folder.

**Leading indicator.** The guidance edition cited in the live submission plan versus the current FDA edition, re-checked at every gate; and the count of MC2 v2 clauses the product can contractually meet today.
**Trigger.** Any FDA cybersecurity guidance reissue, **or** MC2 v3 publication → submission plan re-checked within 30 days.

**Preventive.** Date-stamp §524B conformance as a per-gate obligation rather than a plan-time one; build the SBOM to the **2026 CISA superset**, which satisfies both baselines and is the low-regret position (`INFERRED` — FDA has issued no statement on the gap).
**Contingent.** Publish an MDS2 and an architecture diagram as a standing Vendor Assessment Package so a security review does not become a bid-cycle delay.

**Residual.** L2×I3 = **6 Moderate** with the per-gate re-check; **16 Critical** without. **Recommend NOT acceptable until the re-check cadence is written down.**

---

## Risk interactions and compound exposures

`INFERRED` throughout — the couplings are reasoned from the evidence chains above, not observed.

**C-1 — The differentiation collapse: R6 × R11 × R12.** If the predictive wedge is pre-empted by an already-cleared deterministic interlock (R6), *and* the buyer evaluates platforms rather than pumps (R11), *and* the capability that actually reduces error is auto-programming we have not filed for (R12), then the device arrives with no differentiator the buyer recognises. These are not three independent bets — they are **one bet, made three times**, that specification-level differentiation decides PCA placements. The evidence says it does not. **This is the register's dominant compound exposure.**

**C-2 — The empty-file compound: R9 × R13 × R16.** The quality wedge, the change-control gate and the cybersecurity plan all require the same missing substrate: a risk management plan, a hazard analysis and a hazard traceability matrix that currently resolve `null`. **One absence disables three mitigations.** Conversely, closing it is the highest-leverage single action here, because it is the shared prerequisite.

**C-3 — The timing squeeze: R4 × R9 × R14.** The quality window closes on the competitors' remediation clock (~24–36 months). Serial regulatory gating runs on FDA's clock, where 34.6% of AI-enabled 510(k)s exceed six months and P90 is 8.7 months. If the PCCP is mis-scoped, the predictive claim needs a *second* full submission. Three independent clocks, one owned by our competitors' regulators — the arithmetic does not close, and nobody currently owns noticing that.

**C-4 — The claim-substantiation cascade: R6 × the `INTERNAL-DEMO` asymmetry.** If the R6 baseline correction lands — restating the delta against BD's *existing* capnography-triggered pause — the claim gets **harder** to substantiate, not easier. Correcting the premise raises the evidence bar; that is the right outcome and it should be budgeted, not discovered.

**C-5 — R7 × R11 in the ambulatory hedge.** The recommended hedges for R7 (retarget to ERAS-resistant populations) and R11 (accelerate ambulatory) both route into ambulatory/home — which is ICU Medical's CADD home segment, where the incumbent holds an open FDA warning letter *and* three simultaneous Class I recalls on the CADD-Solis family including the PCA configurations. Both an opening and a crowded, actively-failing segment. **The hedge for two risks concentrates exposure in one place** — that concentration should be a conscious decision.

---

## Coupling to the ISO 14971 risk file

**Test 1 — Does the ICU Medical precedent imply a change-control risk control we need? Yes, and it is a risk-management control, not merely a regulatory one.** A recall remedy is a modification to a risk control measure. ISO 14971 requires risk control measures be verified for implementation *and* effectiveness, and any change re-evaluated for new or increased risks. The control needed is a single question inside change control — *"does this change a risk control measure, or the performance of one?"* — wired so a "yes" triggers both a filing decision **and** a risk-file re-evaluation, before release. FDA has already foreclosed the shortcut. This control cannot be written today: `risk_management_plan` and `hazard_traceability_matrix` both resolve `null`, so there is nothing for the gate to look up.

**Test 2 — Does the detection→prediction PCCP constraint change how predictive risk controls must be specified from the start? Yes — decisively.** If a predictive alarm is claimed as a risk control for the OIRD hazard, then its **lead time and its sensitivity/specificity are the risk control's performance specification**, not marketing parameters. First, the control must be specified in the hazard analysis with a stated performance envelope from the baseline, because a later retrain that *adds* predictive capability is a claim change requiring a new submission. Second, any retrain that moves lead time or sensitivity is simultaneously a **change to a risk control** — requiring re-verification and residual-risk re-evaluation under ISO 14971 — and a PCCP-scope question. The PCCP Modification Protocol and the hazard traceability matrix must therefore be authored **against each other**, not sequentially. Writing the PCCP first and back-filling the hazard analysis is the failure mode.

**Test 3 — Does adding cloud/AI to an opioid delivery device change the hazard set? Yes, and the SAD shows the gap.** The SAD states M2 Safety Monitor *"owns the top-level hazard chains for occlusion, air embolism, overinfusion"* — all pump-mechanical. Not among them:

- **Proxy activation.** PCA's intrinsic interlock is the patient's own consciousness; proxy dosing negates it. SEA 33 recorded 6,069 PCA errors in USP MEDMARX, 460 harmful or fatal. In the SAD, the bolus button lives in **M5 Patient Interface, IEC 62304 Class B**. `INFERRED` — the Class B assignment may be justified in a document I cannot read, because none exists; on the SAD alone, the module owning the surface of the most-cited PCA hazard is classified below the modules owning the mechanical ones.
- **Stale automated programming requests.** Not hypothetical: BD took a **Class I recall on 2025-02-18** for a software defect sending **outdated APRs to the pump** — the connectivity layer, not the pump. Any auto-programming capability inherits this hazard, and it crosses the DHF boundary.
- **Drug-library push failure.** A wrong, stale or maliciously-modified library is a dose-limit hazard originating three DHFs away from the pump.
- **Automation complacency.** A predictive alarm that displaces intermittent nursing assessment creates a new failure path when the model is wrong — and continuous monitoring *raises* measured event rates (41% bradypnea vs 1–2%). A hospital installing this will see its numbers get worse before they get better; the risk file should say so.
- **Model drift, connectivity loss and degraded-mode behaviour** — none in the SAD's hazard-chain sentence.

**The load-bearing conclusion.** None of these can currently be shown to be in the risk file, because `hazard_analysis`, `fmea`, `hazard_traceability_matrix`, `risk_management_report` and `benefit_risk_analysis` all resolve `null`. **I am not claiming these hazards are absent from the file — I am reporting that the file does not exist to check**, which is the more serious statement.

---

## Risks I judge not mitigable

`OPINION` throughout — judgments about what is within the program's control.

| Risk | Why not mitigable | Recommended posture |
|---|---|---|
| **R7** — ERAS category contraction | Driven by clinical guideline direction and hospital pathway design. No device attribute answers *"the pump and the IV line are physical impediments to mobilisation"* | **Accept and navigate.** Re-segment; do not attempt to reverse. Monitor the guideline-to-ward lag |
| **R10** — Consumables lock-out | Structural to the business model. Building a consumables business is a different company, not a mitigation | **Accept**, and compete on fleet-level TCO |
| **R11** — Platform-bundle displacement | Not mitigable *as a standalone PCA device*. The only real responses change what the product is | **Decide, do not mitigate.** The unacceptable posture is leaving it unchosen |
| **The `INTERNAL-DEMO` asymmetry** | Structural to this project. No amount of care in the strategy fixes the input layer | **Accept and quarantine.** No comparative claim leaves the building without measurement conditions, a named comparator with vintage, and a resolvable source |
| **Competitor remediation timing (inside R9)** | The closing date is set by FDA's dealings with BD and ICU Medical | **Accept and monitor** with the trigger armed |

---

## Worked example (before / after)

**The risk:** R2 — alarm-fatigue claims over-promising. Chosen because its current shape is the register's typical shape, and because the evidence identifies the *wrong mechanism* rather than merely a missing number.

### Before — as it exists in D-COMM-1.9 (L147)

| # | Risk | Owning discipline(s) |
|---|---|---|
| **R2** | Alarm-fatigue claims (F4) over-promising vs real-world non-actionable-alert reduction | Clinical + Risk |

**Why it fails, in four ways.**

1. **It is not falsifiable.** "Over-promising" has no threshold. No observation could confirm or refute it, so it can never be closed and never escalated.
2. **No likelihood, no impact, no horizon.** Two disciplines are named as owners of an obligation with no defined content — which in practice means neither acts.
3. **No indicator, no trigger, no control.** Nothing changes at any point on any evidence.
4. **It attributes the benefit to the wrong mechanism.** F4's promise is attached to predictive intelligence. The measured lever is **integration**: EMR integration cut hard-limit alerts −50.3%, soft-limit −30.4%, SSRC −38.1% (all p<0.001) and lifted DERS compliance to 96.1%; interoperability cut keystrokes 15→2 and *forces* DERS use by removing the bypass; ISMP's own diagnosis of the DERS ceiling is that smart pumps operate *"in isolation of other electronic systems"* — a prescription for integration, not intelligence. Meanwhile ECRI has named AI a top-10 hazard in five of seven editions and **#1 in both 2025 and 2026**, and has never once listed an AI capability as a remedy. All `SUBSTANTIATED`.

### After — the same risk, specified

> **R2 — Alarm-reduction claim attributed to the wrong mechanism**
>
> **Threat.** The F4 alarm-reduction claim is attributed to predictive intelligence, when the published effect is produced by EHR↔pump integration — so the claim is unsubstantiable as framed and the program under-resources the capability that would actually deliver it.
>
> **Likelihood L4** (50–80%). The claim already exists and the mechanism attribution is already wrong; only external challenge timing is uncertain. `INFERRED`.
> **Impact I3.** Costs a named competitive claim and a release cycle of re-scoping; not segment-forfeiting. `OPINION`.
> **Exposure 12 (High). Horizon: now.**
>
> **Leading indicator.** For each alarm-reduction claim in customer-facing material: does it cite a mechanism with a published effect size, or an internal projection? Reviewed at every claim-release gate.
> **Trigger.** Any external party (VAC, KOL, diligence reviewer, FDA reviewer) asking "compared with what baseline, and by what mechanism" → the entire F4 claim set is withdrawn pending re-derivation.
>
> **Preventive (reduces likelihood).** Re-attribute the alarm-reduction claim to auto-programming and cite the published integration effect sizes, with the vendor-affiliation COI disclosed as the source studies disclose it. *Owner:* Clinical Affairs + Commercial Lead. *Artifact:* D-COMM-1.1 source block and the F4 claim set. *Acceptance:* every alarm-reduction claim names its mechanism, its comparator baseline, and a resolvable citation; no claim attributes alert reduction to a predictive function absent our own evidence.
>
> **Contingent (reduces impact).** Pre-write the fallback claim — "designed to reduce non-actionable alerts through EHR-integrated auto-programming" — a capability claim tied to a mechanism with published support, requiring no predictive evidence. *Acceptance:* the fallback is drafted and Legal-reviewed *before* the primary claim is used externally.
>
> **Residual exposure.** L2×I2 = **4 Low**, conditional on the F4 requirement set being re-derived. **Recommended acceptable** by the Clinical Affairs lead, conditional on that re-derivation and on the alarm-burden hazard being carried into the hazard analysis when it exists.
>
> **Coupling to the ISO 14971 file.** If alarm reduction is claimed as a *safety benefit*, it becomes an input to benefit-risk (ISO 14971 §8) and the claim's evidence basis becomes risk-file evidence, not marketing evidence. That is a materially higher bar and should be chosen deliberately.

**What changed.** The "after" version is longer, less confident, and far more useful: falsifiable, with a watchable indicator and a defined trigger, owned and checkable mitigations, a stated residual with its condition attached, and a named crossing into the safety file. That is the difference between a risk register and a list of worries.

---

## Step-by-step prescription

**1. Publish the scales before publishing any rating.**
`Owner: Risk Management lead` | `Artifact: a scales block in the register's source task, carried into D-COMM-1.9` | `Acceptance: likelihood and impact bands are defined with tests; the block states explicitly that these are business-exposure scales and are not to be mapped to the ISO 14971 harm-severity scales.`

**2. Re-author D-COMM-1.9 as a two-class register with full fields.**
`Owner: Commercial Lead (edit source task, then re-assemble — never hand-edit)` | `Artifact: D-COMM-1.9 source block` | `Acceptance: R1–R5 retained and relabelled "execution risks"; R6–R16 added as "competitive/exogenous risks"; every row carries L, I, horizon, indicator, trigger, preventive control, contingent control, residual, owner. No row ships with a blank mitigation cell.`

**3. Close the three risk-management roles that gate everything else.**
`Owner: Quality Engineering + Risk Management` | `Artifact: the null-resolving roles in the pca-device discovery block` | `Acceptance: risk_management_plan, hazard_analysis and hazard_traceability_matrix resolve to real files; the hazard analysis names — at minimum — proxy activation, opioid-induced respiratory depression, mis-programming, stale automated programming request, and drug-library push failure alongside the SAD's occlusion / air-embolism / overinfusion chains.`

**4. Write the change-control filing trigger keyed to risk-control modification.**
`Owner: Quality Engineering + Regulatory Affairs` | `Artifact: the change-control procedure; the risk management plan from step 3` | `Acceptance: the procedure names "modifies a risk control measure or its performance" as a filing trigger, cites 21 CFR 807.81(a)(3)(i), records that a label disclosure is not an accepted mitigation, and notes that a Special or Abbreviated 510(k) does not exempt §524B content.`

**5. Decide the PCCP scope against the hazard analysis, not after it.**
`Owner: Regulatory Affairs + Risk Management` | `Artifact: the PCCP section and the predictive-alarm hazard-control specification` | `Acceptance: either the Modification Protocol pre-specifies analysis, performance and statistical methods for a future-state prediction endpoint, or a written decision records that prediction will be filed separately, with schedule and budget. The operative guidance edition cited is the 2025-08-18 issue.`

**6. Move auto-programming into the baseline requirement set.**
`Owner: Systems Engineering + Regulatory Affairs` | `Artifact: software-requirements.md; the submission composition manifest; the standards matrix` | `Acceptance: bi-directional auto-programming and auto-documentation requirements exist with a filing vehicle; the standards matrix cites ANSI/AAMI/UL 2800-1:2022 and sub-parts and ANSI/AAMI 2700-1:2019, and removes IEC 60601-2-24 from the FDA-recognised column.`

**7. Add commercial gates and a fleet-cycle clock to the sequencing plan.**
`Owner: Commercial Lead + Program Manager` | `Artifact: D-COMM-1.3 sequencing table; D-COMM-1.7 stage-gate` | `Acceptance: a "Commercial gate" column carries a Y1 GPO contract-award milestone and a per-year fleet-replacement targeting window; contract coverage is a stage-gate criterion; a target-account list exists with GPO coverage, fleet age and contract expiry.`

**8. Make the platform-vs-standalone decision explicit.**
`Owner: Commercial Lead + Systems Engineering` | `Artifact: a decision block in the architecture or commercial strategy` | `Acceptance: a written decision selects module-supply/partnership, own-platform, or platform-free-segment targeting, with the consequence recorded. Undecided is not an acceptable state for a 20-point exposure.`

**9. Put cybersecurity conformance on a per-gate clock.**
`Owner: Cybersecurity + Regulatory Affairs` | `Artifact: the submission plan; the cybersecurity_plan; the SBOM` | `Acceptance: the plan names the cited guidance edition and issue date and is re-checked at each gate; the SBOM is built to the CISA 2026 superset; an MC2 v2 clause gap list and a current MDS2 exist.`

**10. Stand up the post-market surveillance strategy as the register's sensing layer.**
`Owner: Post-Market Surveillance + Risk Management` | `Artifact: postmarket-strategy.md (currently a nine-line "awaiting content" stub)` | `Acceptance: the strategy names the signals that feed the register's leading indicators and the cadence at which triggers are evaluated. Without it, every "leading indicator" in this register is a sentence nobody reads.`

---

## Evidence base

| Claim | Grade | Source |
|---|---|---|
| D-COMM-1.9 carries two columns with no likelihood, impact, indicator, trigger or mitigation | `ARITHMETIC` | `commercial-strategy.md` L142–154 |
| `pca-device` resolves nine risk/clinical/cyber roles to `null`; verification protocols/reports to `file_count: 0` | `SUBSTANTIATED` — read this pass | `pdlc-demo-dhf-discovery.json` |
| `postmarket-strategy.md` is an unassembled stub | `SUBSTANTIATED` — read this pass | `postmarket-strategy.md` |
| The SAD assigns M2 the hazard chains for occlusion, air embolism, overinfusion; proxy activation and OIRD are not named | `SUBSTANTIATED` — read this pass | `pca-device-system-sad.md` §5 |
| SAD lists IEC 60601-2-24, which is **not** FDA-recognised; ID26 withdrawn; TIR101:2021 is the recognised document | `SUBSTANTIATED` | SAD §3, §7; `research-ai-connectivity-regulatory.md` §B.8 |
| Zero AI-enabled infusion pumps among 1,524 FDA-listed AI devices, verified three ways; ten PHC clearances all rules-based; zero pump-ML outcome studies | `SUBSTANTIATED` | §A.1, §A.5, §A.9 |
| BD Alaris EtCO₂ module pauses the PCA infusion below hospital-defined limits | `SUBSTANTIATED (vendor source)` | `research-competitor-regulatory-record.md` claim 26 |
| McCarter 2008: capnography alarmed and the pump auto-paused in 9/9; pulse oximetry alarmed in none | `SUBSTANTIATED` | `research-pca-clinical-landscape.md` §B.3 |
| Proxy activation negates PCA's intrinsic interlock | `SUBSTANTIATED` | Ocay 2018 |
| Schein 2009: 6.5% of IV PCA events operator error; 81% misprogramming; ~half associated with harm | `SUBSTANTIATED` | §B.6 |
| 87.9% smart-pump adoption vs 13.4% auto-programming; 85.1% still document manually | `SUBSTANTIATED` (2020 ASHP); 2026 rate `UNVERIFIED` | §B.0 |
| EMR integration: hard-limit alerts −50.3%, soft-limit −30.4%, DERS compliance 96.1%; keystrokes 15→2 | `SUBSTANTIATED`, vendor-adjacent COI stated | §B.3, §B.5 |
| ECRI: AI in 5 of 7 hazard lists, #1 in 2025 and 2026, never listed as a remedy | `SUBSTANTIATED` | §B.7 |
| PCCP intended-use limit is statutory (FD&C §§515C(a)(2), 515C(b)(2)); operative guidance 2025-08-18 | `SUBSTANTIATED` (verbatim) | §C.1, §C.3 |
| Appendix B Scenario 2: detection→advance prediction requires a new submission unless pre-specified | `SUBSTANTIATED` (verbatim); application `INFERRED` | §C.4 |
| AI-enabled 510(k): median 142 days, P90 266 days, 34.6% exceed six months; MDUFA total time 139 days FY2024 (goal missed) | `SUBSTANTIATED` | §C.7 |
| ICU Medical CMS 702535: adulterated/misbranded for unfiled changes; the unfiled software was the Class I recall remedy; label disclosure "not sufficient" | `SUBSTANTIATED` (verbatim) | claims 29–32 |
| BD: amended consent decree, open May-2024 Infusion 483 review, remediation "substantially complete over the next calendar year", four Class I events since return-to-market | `SUBSTANTIATED` | claims 12–16, 22–24 |
| BD Class I 2025-02-18: outdated automated programming requests sent to the pump — the connectivity layer | `SUBSTANTIATED` | claim 22 |
| 31 MEA 510(k)s ever; most recent 2017-08-29; modern PCA clears under FRN as a platform module | `SUBSTANTIATED` | claims 2–3, 6 |
| ERAS cohorts: PCA 63%→0.5%, 61.6%→1.4%, 68.4%→0%, 88%→10%, 50.6%→32.1%; Premier lobectomy 27%→13% | `SUBSTANTIATED` individually; pooling `INFERRED` | §A.2 |
| The guideline-vs-ward-practice gap is years wide; a 2022 NHS ERAS protocol specifies routine PCA | `SUBSTANTIATED` / `OPINION` on the timing implication | §A.1, Implications 6 |
| A standalone PCA pump "is not in the comparison" against a modular platform | `INFERRED` | §B.5, Implications 2 |
| GPO status is an evaluability gate; TCO dominates; displacement at fleet-replacement events | `SUBSTANTIATED` | `research-market-data.md` (AHRQ, HPN) |
| ICU Medical FY2024: Infusion Consumables $1.11B vs Systems $684.2M (1.6×) | `SUBSTANTIATED` | `research-market-data.md` |
| Cybersecurity guidance reissued 2025-06-27 and 2026-02-03; CISA 2026 SBOM elements replace the NTIA 2021 baseline FDA cites | `SUBSTANTIATED` | §D.5, §D.6 |
| HSCC MC2 v2 co-chaired by a national GPO; SBOM #44, KEV 3 days #33, patches 30 days #31, OS EoS 2 years #40; HICP's worked example is an infusion pump | `SUBSTANTIATED` (verbatim) | §D.7 |
| Every rating in this register (L, I, residual) | `OPINION` — advisor judgment against the published scales; reasoning stated so each can be rejected individually | — |
| The control-effectiveness discount rule | `OPINION` — risk-practice judgment, no cited rule | — |
| M5 Patient Interface's Class B assignment relative to the proxy-activation hazard surface | `INFERRED` from the SAD alone; a justification may exist in a document that does not exist yet | SAD §4, §5 |

---

## Cross-discipline open questions

| Question | Owning discipline | Why blocked here |
|---|---|---|
| Does BD's PCA Pause + EtCO₂ constitute the accepted state of the art for the OIRD hazard — and if so, does ISO 14971's state-of-the-art expectation oblige an equivalent interlock? | Clinical Affairs + Regulatory Affairs | The pivot for R6. Risk management can frame the state-of-the-art question but cannot settle the accepted clinical baseline. |
| Can an incumbent add monitoring-driven or predictive behaviour to an installed fleet under an existing change-control envelope without a new 510(k)? | Regulatory Affairs | Sets R6's duration. |
| Should the predictive alarm be filed as a PP3500 module or as standalone Cloud SaMD feeding M2 — and which hazard file owns the resulting risk control? | Systems Engineering + Regulatory Affairs | The SAD defers this. It determines which DHF's hazard analysis owns the predictive risk control and therefore which PCCP scopes it. |
| Is a hazard analysis that omits proxy activation and OIRD defensible for a PCA pump, given the sentinel-event and closed-claims record? | Clinical Affairs + Human Factors | The hazard analysis does not exist; when it does, this is the first review question an auditor will ask. |
| Does the M5 Patient Interface IEC 62304 Class B assignment survive a proxy-activation hazard analysis? | Systems Engineering + Risk Management | Software safety classification follows from the hazard analysis, which is `null`. |
| What field-performance denominator exists, and does complaint/CAPA data support any externally citable reliability claim? | Post-Market Surveillance | R9's contingent control depends on it, and the post-market strategy is an empty stub. |
| Which MC2 v2 clauses can the product contractually meet today, and which require design change rather than documentation? | Cybersecurity + Legal | R16's residual depends entirely on which of the two it is. |
| Is a benefit-risk analysis that counts alarm reduction as a benefit obliged to hold that claim to risk-file evidence standards rather than marketing standards? | Quality Engineering + Regulatory Affairs | Raised by the worked example. My reading is yes; the QMS form governing benefit-risk should settle it. |

**Governance gap declared.** `pca-device` carries `dhf_organization: "internal"`, so no `.taxonomy.yml` `governing_qms` block attaches to these doctypes. Recommendations above are made against ISO 14971 and the cited FDA guidance; before any is authored into a controlled document, resolve governance through the QMS manifest.

---

## Counterpoints & considerations

**I may be over-weighting the deterministic interlock in R6.** BD's PCA Pause is a *threshold* control — it acts once the patient has already crossed a physiological limit. A lead-time warning that acts before the crossing is genuinely a different control, and if it can be substantiated, the R6 downgrade of the predictive wedge is wrong. My position is that the *justification* is unsubstantiable today regardless of whether the bet is right — but those are two separable questions and the team should separate them rather than inheriting my conflation.

**The register may be too pessimistic on horizon.** Six of eleven risks are marked "now." That is defensible from the evidence but produces a register with no breathing room, which teams discount wholesale. If the program disagrees with any single horizon, the argument to have is about that indicator and that trigger — not about the register's tone.

**Three risks share one mitigation, and that is a fragility as well as a leverage point.** R9, R13 and R16 all route through step 3. If step 3 slips, three high-exposure risks stay uncontrolled simultaneously and the register will look — wrongly — as though nothing was done. The step-3 date should be tracked as a program dependency, not a documentation task.

**The evidence base is one hop from primary in places I have not re-derived.** The strongest R6 fact — BD's PCA Pause — rests on vendor marketing material, and BD's "only platform" claim was not independently checked. If BD's actual labeling is narrower than its marketing, R6's likelihood drops. That closing action sits with Regulatory Affairs, and it is cheap.

---

## Changelog

| Date | Author | Summary |
|------|--------|---------|
| 2026-08-06 | AI assistant(s) — `risk-management` advisor | Initial competitive-threat risk register. Published business-exposure scales distinct from the ISO 14971 harm scales; assessed D-COMM-1.9's R1–R5 as uncontrolled; tested and re-founded the commercial advisor's R6–R10 and added R11–R16; documented five compound exposures; identified the change-control, PCCP-scoping and connected-hazard couplings into the ISO 14971 file; named five risks judged not mitigable. Contributed findings F-15…F-18. |
