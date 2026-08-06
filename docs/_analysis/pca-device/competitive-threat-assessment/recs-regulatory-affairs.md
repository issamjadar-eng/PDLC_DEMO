---
id: recs-regulatory-affairs
parent_analysis: competitive-threat-assessment
type: recommendation
authored_by: agent:regulatory-affairs
created: 2026-08-06
---

# Regulatory Affairs — Competitive Exposure and Strategy Prescription

> _Demo sample data — not for clinical use._ The PP3500 device program is fictional. The FDA guidance, statute, product-code, standards-recognition and competitor-enforcement facts cited below are real and traceable to the research files in this folder or to a live openFDA query run 2026-08-06.

Advisory only. This is an assistant's read for the RA leads — it commits the program to nothing.

---

## What good looks like

1. **Every roadmap feature names a filing vehicle that can actually carry it.** A PCCP carries *modifications to a cleared function within the cleared intended use*. It does not carry new device functions, new intended uses, or software living in a different DHF.
2. **The predicate question is answered before the feature is funded.** For a function with no same-code, same-intended-use precedent, the sponsor has explicitly evaluated 510(k) vs De Novo and taken the answer to a Q-Sub — rather than discovering at RTA that the SE argument has no anchor.
3. **The standards matrix cites standards FDA actually recognizes.** Non-recognized standards may supply test methods, but they are labelled as performance-data basis, never as declaration-of-conformity anchors.
4. **Change control treats "does this modify a risk control?" as the filing trigger** — including, especially, when the change is a recall remedy.
5. **The schedule is built on the review-time distribution, not its median.**

## What the strategy does instead

`regulatory-strategy.md` has real content in §1 (Critical-Requirement Carve-out), §2 (Component Classification), and §5 (DHF composition). **Sections 3, 4, 6, 7 and 8 all read `_No strategy content assembled yet for this section._`** — jurisdictional differences, filing sequence, document reuse, pre-market strategy, and **Q-Sub questions**. §9 still lists "PCCP scope for post-clearance changes" and "Predicate lineage beyond PP3000" as *pending decisions*.

Meanwhile `commercial-strategy.md` D-COMM-1.3/1.4 commit a five-year, nine-feature roadmap in which **every commit boundary is a regulatory vehicle** — and D-COMM-1.3's own rule is "a feature slips a year rather than shipping ahead of its regulatory vehicle." **The commercial strategy has committed against decisions the regulatory strategy has not made.** That is the structural finding under all five below.

---

## Walk-through of the exposure

### 1. The PCCP envelope vs the roadmap (D-COMM-1.4)

The statutory limit is not negotiable. Per the operative PCCP guidance (**issued 2025-08-18**, originally 2024-12-04; Docket FDA-2022-D-2628), §IX states modifications "**must maintain the device within the device's intended use**… and **must allow the device to remain substantially equivalent to the predicate device**," citing **FD&C §515C(a)(2), (b)(2), (b)(2)(B)** — statute, not preference. `SUBSTANTIATED`

| ID | Feature | Stated category | Assessment |
|---|---|---|---|
| F1 | Drug Library Manager GA | C (own 510(k)/accessory) | **Vehicle right, sequence wrong.** F1 is Y1; the Q-Sub question that governs it is at **M12**. The question lands after the GA. `INFERRED` |
| F2 | Connectivity Adapter (MDDS) | A (non-device) | **Asserted, not established.** The MDDS rationale brief is `draft-v0.0 — transmission-blocking` per the Q-Sub manifest. Non-device status also does not exempt the *pump's* submissions from §524B. `SUBSTANTIATED` |
| F3 | Fleet / telemetry dashboards | A | Plausible non-device. No objection. `OPINION` |
| **F4** | **Alerts Engine v1 — alarm filtering** | **B (PCCP)** | **Mis-categorised. Should be C.** See worked example. `INFERRED` |
| **F5** | **Clinical Surveillance — near-miss analytics** | **B (PCCP)** | **Mis-categorised.** Either non-device retrospective analytics (**A**) or an active clinical-decision SaMD (**C**). It cannot be B — there is no cleared `clinical-interface` function to modify. `INFERRED` |
| F6 | Predictive monitoring | C + PCCP retraining | **Category right, dependency inverted.** See below. `INFERRED` |
| F7 | Ambulatory PP3500-A + home indication | C | Right. But D-COMM-1.3's Y4 row reads "PCCP retraining **+** new indication filing (home)" — the home indication is an **intended-use change**, statutorily outside any PCCP. The row invites the wrong reading. `SUBSTANTIATED` |
| F8 | Dose-personalisation decision support | C + PCCP | Right vehicle; depends entirely on F6's PCCP having pre-specified the methodology. `INFERRED` |

**The F6 trap is the sharpest item in the evidence base.** PCCP guidance **Appendix B, Modification Scenario 2** walks a patient-monitoring device that detects physiologic instability and is retrained to *predict it in advance*: "**The methods used for analysis, performance, and statistics were not specified in the PCCP for predicting a future state**… a **new marketing submission would be required**." `SUBSTANTIATED` (verbatim)

Applied here: a Y2 PCCP written around alarm-filtering accuracy will **not** cover a Y3 pivot to "15–30 minute early warning." The predictive methodology must be pre-specified in the PCCP at the moment it is first filed — which, if F4 is filed in Y2, means Y2. **The roadmap has this backwards.** `INFERRED` — the guidance example is hypothetical and not about an infusion pump; the structural parallel is my mapping.

### 2. The predicate problem

PP3500 itself is cleared (K210345, predicate PP3000/K190567). The exposure is entirely forward — F6 and F7.

- **MEA ("Pump, Infusion, Pca," 21 CFR 880.5725, Class II)**: 31 clearances ever; newest **K162165, 2017-08-29**. Nine years, zero. `SUBSTANTIATED`
- The drought is partly a coding artifact: modern PCA-capable systems clear under **FRN**. `SUBSTANTIATED`
- **Zero AI-enabled infusion pumps exist** — 1,524 rows on FDA's AI list, checked three independent ways. `SUBSTANTIATED`
- Where deterioration prediction *is* authorized, it is standalone SaMD decoupled from delivery: eCART **K233253** (510(k)) and Sepsis ImmunoScore **DEN230036** (**De Novo**). `SUBSTANTIATED`

**Does De Novo deserve real consideration? Yes — and it is currently not considered anywhere.** The Q-Sub has six questions; Q3.1 asks only whether PP3000 is an appropriate predicate "with added connectivity." **No question asks about the pathway for the predictive function at all.**

The argument for De Novo: a predictive-alarm function on a PCA pump has no same-intended-use predicate, and the one directly analogous capability that reached market did so via De Novo. De Novo produces a classification regulation and special controls — which then become the barrier every competitor must clear, and which the sponsor helped write. Per §515C, PCCPs are available on the De Novo route too.

The argument against: De Novo is 2.6% of the AI authorisation population (39 of 1,524) and is slower than 510(k). `SUBSTANTIATED`

My read: forcing a novel predictive function through 510(k) against a 2017-era predicate landscape is the higher-risk path, because the likely failure mode is not a delay — it is an **NSE**, which costs the whole submission. The disciplined move is to put the choice in front of FDA in the Q-Sub rather than pick it internally. `OPINION` — no source settles a pathway election.

### 3. "Competitors have AI" is refuted — what that does

D-COMM-1.1 rests on: "market leaders… are reactive-alarm only, while **AI-enabled entrants demonstrate 15–30 min early warnings**." The evidence refutes the premise. There are no AI-enabled entrants in infusion. The one cleared infiltration-detection product, **ivWatch** (product code PMS), is **optical near-infrared sensing, not a learned model, and a separate monitor rather than a pump function**. PubMed returns **0 hits** on infusion-pump ML occlusion detection. `SUBSTANTIATED`

**The first-mover case.** No competitor holds an AI infusion clearance. A cleared predictive PCA function is genuinely category-defining, and via De Novo it becomes the classification others file against.

**The no-predicate-burden case.** Zero clearances means zero precedent, no special controls, no review-division familiarity, no recognized standard, and near-empty literature. And the neutral referee is hostile: ECRI has named AI the **#1 health-technology hazard in both 2025 and 2026** and has **never listed an AI capability as a remedy for anything**. That shapes both review climate and purchasing climate.

**Where I land.** The refutation does not kill the opportunity; it **reprices it**. It destroys the *urgency* argument — there is no competitor to catch — while leaving the *first-mover* argument intact but expensive. Being first means F6 is the single most costly and least predictable filing on the roadmap, not a shortcut past the incumbents.

One live hazard: D-COMM-1.1's "AI-enabled entrants demonstrate 15–30 min early warnings" is an unsubstantiated comparative claim in a strategy doc that feeds the Go-to-Market plan. The program's own record already states "Cannot Compare Without Data" in its Key Messaging Guardrails. It should be corrected at source before it migrates into promotional material. `INFERRED`

### 4. Interoperability is the real regulatory-competitive axis — and the plan is silent

The asymmetry is the strongest structural fact in the research: **vendors shipped connectivity and did not ship machine learning.** ~88% smart-pump saturation vs **~13.4% EHR→pump auto-programming** (ASHP 2021), with 85.1% of infusions still manually documented. PCA-specifically: MAUDE analysis (Schein 2009) found **6.5% of IV PCA events were operator error, 81% of those misprogramming, roughly half associated with harm** — the harm auto-programming removes. `SUBSTANTIATED`

The regulatory strategy addresses interoperability in exactly one clause. There is no interoperability plan, no product code, and no standard.

- **Product code PHC ("Infusion Safety Management Software")** is where every competitor's drug-library/DERS/interoperability layer clears — 10 clearances ever: ICU LifeShield (K252130, K242117, K223606), BD Intelliport (K243062, K182092, K141474), Baxter Dose IQ (K230665, K211124), Fresenius Vigilant (K210075). The Drug Library Manager is that exact product shape. **PHC appears nowhere in the regulatory strategy or the Q-Sub**, and Q1.3 asks FDA to "confirm the predicate's product code" without naming one. `SUBSTANTIATED`
- **No interoperability standard is in the project.** A grep for `2800|2700-1|F2761` across `docs/` returns zero hits outside the research file. Missing and FDA-recognized: **ANSI/AAMI/UL 2800-1:2022 (13-121)**, **-1-1 (13-125)**, **-1-2 (13-126)**, **-1-3 (13-127)**; and **ANSI/AAMI 2700-1:2019 (13-120)** — the successor to ASTM F2761, which should be cited as 2700-1, not F2761. **UL 2800 Edition 3 (2026-01-29) is not yet recognized — cite the 2022 editions.** `SUBSTANTIATED`
- `docs/external/fda-guidance/` holds 12 files; none is the **2017 Interoperable Medical Devices** final guidance or the **Infusion Pumps — Total Product Life Cycle** guidance (Dec 2014). `SUBSTANTIATED`

### 5. The competitor enforcement record — the most transferable lesson here

**FDA Warning Letter CMS 702535, 2025-04-04, ICU Medical.** FDA holds the Medfusion 4000 and CADD Solis VIP **adulterated (§501(f)(1)(B)) and misbranded (§502(o))** for changes shipped without the 510(k) required by **21 CFR 807.81(a)(3)(i)**. Three aggravators: the unfiled software **was the remedy for a Class I recall**; **ICU's own procedure said a 510(k) was required**; and FDA states that adding a label statement that the software was not FDA-reviewed **"is not sufficient."** `SUBSTANTIATED`

What that prescribes for PP3500 — applying **today**, not at next filing, because PP3500 is marketed with an active post-market record:

1. **The filing trigger is "does this change a risk-control measure?" — not "is this a safety improvement?"** A recall remedy is the *most* likely change to need a filing, because it modifies a risk control by definition. This is the inversion that caught ICU.
2. **The PCCP is the only legitimate fast path, and only for changes pre-specified before the event.** The strongest available argument for scoping the PCCP wide across *anticipated* change families at the original filing — and against trying to stretch it afterwards.
3. **There is no small-change exemption on the cyber axis.** §524B applies to *any* submission including modifications; a §524B(b)(1) plan must be provided if not previously submitted, and an SBOM is still required. **A Special or Abbreviated 510(k) does not exempt you.** `SUBSTANTIATED`
4. **The written procedure must be one you can follow under recall pressure** — FDA used ICU's own SOP as the evidence against it.
5. **Label disclosure is foreclosed.** Do not design a mitigation around it.

### 6. Timeline realism

D-COMM-1.3's annual cadence assumes 3–6 month clearances. The claim is *partially* true and *not plannable*:

| Measure | Value |
|---|---|
| AI-enabled 510(k) median, receipt→decision (n=862, 2023+) | **142 days** (4.7 mo) |
| 75th / 90th percentile | 211 / **266 days** (6.9 / 8.7 mo) |
| Share exceeding six months | **34.6%** |
| AI vs non-AI median delta | **~+20 days** |
| MDUFA V total time to decision, FY2024 | **139 days — goal MISSED** against a tightening goal (124 → 112) |

Three omissions matter more than the median. The figure is **submission-to-decision only** — it excludes Q-Sub turnaround, RTA screening, and all sponsor preparation. Since **2023-10-01** FDA may RTA cyber-device submissions lacking §524B content (88 FR 19148) — an RTA restarts the calendar. And the segment comparator is brutal: **BD's K211218 took 27 months** (2021-04-23 → 2023-07-21); **K243855 took four months**. Same firm, same product family, a 6.75× spread driven by regulatory standing. `SUBSTANTIATED`

`ARITHMETIC`: F6 must clear inside Y3 (2028). At the AI 90th percentile plus one Q-Sub cycle plus one RTA round, a Q1-2028 submission lands in Q1-2029 at the tail. Under D-COMM-1.3's own slip rule, one tail-case review slips **two** features — F6 and F8.

### 7. The standards defect

**There is currently no FDA-recognized particular safety standard for infusion pumps.** FDA recognizes 50 entries across IEC 60601-2-1 → -2-68, but **60601-2-24 is absent** — it sits in the gap between recognized -23 and -25 — and ANSI/AAMI ID26:2004(R2013) is **withdrawn**. `SUBSTANTIATED`

The project caught this once and did not propagate it. `docs/external/standards/iec-60601-2-24.md` line 7 states it plainly, and its verification check "510(k) does not claim FDA-recognized-standard conformity for this standard" is still `[ ]` **pending**. Meanwhile the standard is still listed as a peer of IEC 60601-1 in `pca-device-system-sad.md` (§3, §5, §7), in `design-inputs.md`, `user-needs.md`, and `software-requirements.md` — with no non-recognition note. `SUBSTANTIATED`

**What the matrix should cite:**

1. **AAMI TIR101:2021** — *Fluid delivery performance testing for infusion pumps*, explicitly covering **PCA mode**. **FDA-recognized 6-482, entered 2022-05-30, extent Complete.** No applicability doc for it exists in the project. Fresenius already claims "first cleared following TIR101" as a differentiator — this is a parity item, not just compliance. `SUBSTANTIATED`
2. **FDA *Infusion Pumps — Total Product Life Cycle*, final Dec 2014** — asks for a **safety assurance case** connecting design elements to safety mitigations and warns FDA may conduct pre-clearance inspections. The safety assurance case is the distinctive artifact for this device class and appears in no submission manifest. `SUBSTANTIATED`
3. **IEC 60601-2-24:2012** — retained as a *test-method / performance-data basis only*, edition-pinned, labelled non-recognized, with its three open subclause `[VERIFY]`s resolved against a licensed copy.
4. **Interoperability** — UL 2800-1:2022 family and ANSI/AAMI 2700-1:2019. Not Edition 3. Not F2761.
5. **Cybersecurity guidance version** — the SAD cites "FDA Cybersecurity Guidance 2023." The current guidance is **issued 2026-02-03** (FDA-2021-D-1158), superseding 2025-06-27, which superseded 2023-09-27. **The SAD is two supersessions stale.** `SUBSTANTIATED`

---

## Worked example (before / after) — F4, Alerts Engine v1

**BEFORE** (D-COMM-1.4 as written):

> | F4 | Alerts Engine v1 — smart alarm filtering / alert-fatigue reduction | `alerts-engine` (SaMD) | Y2 | **B (PCCP)** | Safety | … |

**AFTER** (defensible):

> | F4 | Alerts Engine v1 — smart alarm filtering | `alerts-engine` (SaMD) | Y2→Y3 | **C — own 510(k) (or accessory bundle), with the PCCP filed *alongside* it** | Safety | … |

**Why the change.** Three independent reasons, any one sufficient.

1. **Nothing to modify.** A PCCP authorises pre-specified modifications to a *cleared* function. K210345 cleared a PCA pump with reactive alarms. There is no cleared alarm-filtering function. Category B assumes a baseline that does not exist. `INFERRED`
2. **Wrong DHF, wrong device.** `alerts-engine` is a distinct DHF under `cloud-suite`. The PP3500 PCCP is scoped to the `pca-device` DHF per regulatory-strategy §1 ("Filing Scope: PCA Device Alone"). A PCCP on device A cannot authorise a device function in DHF B. Regulatory-strategy §2's phrasing — future AI/ML SaMDs "introduced via PCCP **or** future filings" — is where the ambiguity lives; that "or" should resolve to "future filings, with a PCCP attached." `SUBSTANTIATED` + `INFERRED`
3. **The direction of the change is adverse.** Alarm *filtering* reduces annunciation on a safety alarm. FDA's own Appendix B treats false-alarm reduction as PCCP-eligible only when sensitivity is held inside a pre-specified non-inferiority margin — and only within an already-cleared alarm function. `SUBSTANTIATED`

**What the correction costs.** F4 moves from "no submission" to "Q-Sub cycle + a 510(k)." On the §C.7 distribution that is a Y2 GA becoming a Y2-late/Y3 GA.

**What it buys.** (a) It eliminates the ICU Medical failure mode structurally — F4 cannot become an unfiled software push. (b) It creates the *right* moment to file the PCCP that pre-specifies the **predictive methodology** for F6, defusing Appendix B Scenario 2 before it fires. (c) It gives the Q-Sub a real question to ask, two years before F6 is funded.

---

## Why this project specifically

- **It is a connected opioid pump.** §524B applies with certainty: the SAD's M6 module carries TLS, certificate store, firmware-update verifier, Wi-Fi and a USB service port — satisfying all three conjunctive prongs of §524B(c). The guidance's own footnote 61 puts even a USB-serviced air-gapped device inside scope. `SUBSTANTIATED`
- **The device is already marketed with a post-market record.** The ICU precedent is a present-tense risk. The next field-safety correction is the test.
- **The evidence points the safety case at interoperability, not intelligence.** ISMP's 2020 guidelines diagnose the DERS ceiling as smart pumps "**operating in isolation** of other electronic systems" and set a **≥95% compliance target**; integration achieved **96.1%** in the UTMB study, and keystrokes fall **15 → 2**. For PCA specifically, misprogramming is where the harm lives. A regulatory strategy that funds F6 heavily and leaves interoperability unaddressed is aimed at the wrong hazard. `SUBSTANTIATED` components; `OPINION` on the prioritisation.
- **The product code on file is wrong.** `DEV-PP3500_regulatory_info.md` line 22 states: **"FDA Product Code: LZH (Infusion Pump, Patient-Controlled Analgesia)."** openFDA `device/classification` (queried 2026-08-06) returns **LZH = "Pump, Infusion, Enteral"**, 21 CFR 880.5725, Class II; the PCA code is **MEA = "Pump, Infusion, Pca."** A PCA pump carrying an enteral-pump code is a scoping error that surfaces at RTA — and Q1.3 asks FDA to "confirm the predicate's product code" **without naming one**, so the Q-Sub currently cannot catch it. `SUBSTANTIATED` (code definitions) / `INTERNAL-DEMO` (that the project doc says LZH)

---

## Step-by-step prescription

| # | Action | Owner | Artifact | Acceptance criterion |
|---|---|---|---|---|
| 1 | Correct the PP3500 product code to **MEA** (or establish FRN/PHC deliberately), and name the chosen code in Q1.3 | RA Lead | `DEV-PP3500_regulatory_info.md`; `qsub/fda-questions.md` Q1.3 | Doc states MEA with the openFDA definition quoted; Q1.3 names the proposed code and asks FDA to confirm rather than asking open-ended |
| 2 | Re-categorise **F4 → C** and **F5 → A-or-C**; split D-COMM-1.3's Y4 row so the home indication is not adjacent to "PCCP retraining" | Commercial Lead + RA Lead | `commercial-strategy.md` (via source task) | Every roadmap row's vehicle passes the §515C intended-use test; no B-category row names a function absent from K210345 |
| 3 | Author regulatory-strategy **§8 Q-Sub Questions** and add two: (a) pathway election for the predictive function — 510(k)-with-predicate vs **De Novo**; (b) whether a single PCCP may pre-specify predictive methodology ahead of the predictive function's own submission | RA Lead | `regulatory-strategy.md` §8; `qsub/fda-questions.md` | Both carry a stated preliminary position and cite PCCP guidance §IX + Appendix B Scenario 2 |
| 4 | Write the **PCCP scope decision** that §9 lists as pending — enumerating change families, and stating that the PCCP does not carry new device functions, new DHFs, or intended-use changes | RA Lead | `regulatory-strategy.md` §1/§2 | Decision text quotes the §515C limit; every D-COMM-1.4 B-category row traces to a named pre-specified change family or is re-categorised |
| 5 | Add a **recall-remedy filing-trigger rule** to change control: any change modifying a risk-control measure requires a filing determination *before* field release; a corrective change outside the PCCP holds until the submission is filed, with a compensating field mitigation rather than an unfiled software push. Label disclosure is not permitted | QA + RA | Change-control SOP; PCCP modification protocol | SOP text is executable under a Class I clock; explicitly cites 21 CFR 807.81(a)(3)(i) and the §524B(b) modification obligation |
| 6 | Create the **AAMI TIR101:2021** applicability doc and make it the primary fluid-delivery performance anchor; demote IEC 60601-2-24 to non-recognized test-method basis everywhere | RA + Systems | New `docs/external/standards/aami-tir101.md`; SAD §3/§7; `design-inputs.md`, `user-needs.md`, `software-requirements.md` | TIR101 recognition (**6-482**) recorded; every 60601-2-24 citation carries the non-recognized label; the `[ ]` check at `iec-60601-2-24.md` line 54 closes |
| 7 | Add the **FDA Infusion Pumps TPLC (Dec 2014)** applicability doc and schedule a **safety assurance case** as a named 510(k) deliverable | RA Lead | New guidance doc; `510k/composition-manifest.md` | Safety assurance case appears as a tracked row with an owner |
| 8 | Add the **interoperability standards + guidance** layer (UL 2800-1:2022 family, ANSI/AAMI 2700-1:2019, 2017 Interoperable Medical Devices guidance). Evaluate **PHC** as the Drug Library Manager's product code | RA + Systems | New applicability docs; `regulatory-strategy.md`; Q1.1 | SAD §7 carries an interoperability row; Q1.1 names PHC and cites at least two competitor precedents |
| 9 | Refresh the cybersecurity citation to the **2026-02-03** guidance throughout, and add the §524B-applies-to-modifications rule to the PCCP text | Cyber + RA | SAD §5/§7; `docs/external/fda-guidance/cybersecurity.md` | No document cites the 2023 or June-2025 edition; PCCP text states a Special/Abbreviated 510(k) does not exempt §524B content |
| 10 | Re-plan D-COMM-1.3 against the **90th percentile** (266 days) plus a Q-Sub cycle plus one RTA contingency | Program + RA | `commercial-strategy.md` D-COMM-1.3 | Each C-category feature shows submission date, P50 and P90 decision dates, and the downstream feature it blocks at P90 |

---

## Evidence base

| Claim | Grade | Source |
|---|---|---|
| PCCP modifications must stay within intended use / SE; statutory per FD&C §515C(a)(2), (b)(2), (b)(2)(B) | `SUBSTANTIATED` | `research-ai-connectivity-regulatory.md` §C.3 (guidance §IX verbatim, 2025-08-18 issue) |
| Detection → advance prediction requires a new submission unless methodology pre-specified | `SUBSTANTIATED` | ibid. §C.4 (Appendix B Scenario 2, verbatim) |
| General-device PCCP guidance is still DRAFT (Aug 2024) | `SUBSTANTIATED` | ibid. §C.2 |
| Zero AI-enabled infusion pumps among 1,524 rows, verified three ways | `SUBSTANTIATED` | ibid. §A.1 |
| MEA: 31 clearances ever; newest K162165, 2017-08-29 | `SUBSTANTIATED` | `research-competitor-regulatory-record.md` claims 2–3 |
| Modern PCA function clears under FRN, not MEA | `SUBSTANTIATED` | ibid. claim 6 |
| Deterioration prediction cleared as standalone SaMD: K233253 (510(k)), DEN230036 (De Novo) | `SUBSTANTIATED` | `research-ai-connectivity-regulatory.md` §A.10 |
| 510(k) = 96.2% of AI authorisations; De Novo = 2.6% (39/1,524) | `SUBSTANTIATED` | ibid. §C.5 |
| AI 510(k) median 142 days; 34.6% > 6 months; P90 = 266 days; MDUFA V FY2024 total time 139 days (goal missed) | `SUBSTANTIATED` | ibid. §C.7 |
| BD K211218 = 27-month review; K243855 = 4-month review | `SUBSTANTIATED` | `research-competitor-regulatory-record.md` claims 8, 11 |
| ICU Medical WL CMS 702535: adulterated §501(f)(1)(B) / misbranded §502(o); recall remedy shipped unfiled; label workaround rejected; CADD Solis VIP on K111275 (2013-02-01) | `SUBSTANTIATED` | ibid. claims 29–32 |
| §524B applies to modifications incl. Special/Abbreviated 510(k); plan + SBOM still required | `SUBSTANTIATED` | `research-ai-connectivity-regulatory.md` §D.4 |
| RTA exposure for cyber devices from 2023-10-01 (88 FR 19148) | `SUBSTANTIATED` | ibid. §D.4 (verbatim) |
| Current cyber guidance issued 2026-02-03, supersedes 2025-06-27 | `SUBSTANTIATED` | ibid. §D.5 |
| IEC 60601-2-24 NOT FDA-recognized; ID26 withdrawn; TIR101:2021 recognized 6-482 | `SUBSTANTIATED` | ibid. §B.8; corroborated by `docs/external/standards/iec-60601-2-24.md` line 7 |
| UL 2800-1:2022 family recognized 13-121/125/126/127; ANSI/AAMI 2700-1:2019 = 13-120; Ed. 3 not recognized | `SUBSTANTIATED` | ibid. §B.8 |
| PHC has 10 clearances ever; all four major vendors present | `SUBSTANTIATED` | ibid. §A.5 |
| 87.9% smart-pump adoption vs 13.4% auto-programming (ASHP 2021) | `SUBSTANTIATED` | ibid. §B.0 |
| PCA harm concentrates in misprogramming (Schein 2009) | `SUBSTANTIATED` | ibid. §B.6 |
| ivWatch is optical, not AI; a separate monitor, not a pump function | `SUBSTANTIATED` | ibid. §A.6 |
| ECRI names AI #1 hazard 2025 and 2026; never as a remedy | `SUBSTANTIATED` | ibid. §B.7 |
| **LZH = "Pump, Infusion, Enteral"; MEA = "Pump, Infusion, Pca"** (both 880.5725, Class II) | `SUBSTANTIATED` | openFDA `device/classification`, queried 2026-08-06 |
| PP3500 record assigns LZH and labels it "Patient-Controlled Analgesia" | `INTERNAL-DEMO` | `DEV-PP3500_regulatory_info.md` line 22 |
| Regulatory strategy §§3, 4, 6, 7, 8 empty; §9 lists PCCP scope + predicate lineage as pending | `SUBSTANTIATED` | `regulatory-strategy.md` |
| SAD cites 60601-2-24 as a peer standard and "FDA Cybersecurity Guidance 2023" | `SUBSTANTIATED` | `pca-device-system-sad.md` §3, §5, §7 |
| No interoperability standard or TIR101 doc in `docs/external/standards/`; no TPLC/interoperability guidance in `docs/external/fda-guidance/` | `SUBSTANTIATED` | folder listings + grep, 2026-08-06 |
| MDDS rationale brief is `draft-v0.0 — transmission-blocking` | `SUBSTANTIATED` | `qsub/composition-manifest.md` |
| Q-Sub has no question on predictive-function pathway or De Novo | `SUBSTANTIATED` | `qsub/fda-questions.md` (6 questions, read in full) |
| F4/F5 mis-categorised; F6 PCCP dependency inverted | `INFERRED` | Application of §515C + Appendix B Scenario 2 to D-COMM-1.4 |
| De Novo is the lower-risk pathway for the predictive function | `OPINION` | No source elects a pathway |
| Interoperability outranks AI as the near-term regulatory-competitive axis | `OPINION` | Rests on substantiated components §A.1, §A.5, §B.0–B.9 |

**Citation-verification note.** FDA-guidance and standards claims were verified against the project applicability files and the research files' verbatim quotations: **sound**. The `LZH`/`MEA` classification claims were verified by live openFDA query: **sound**. **IEC 60601-2-24 subclause numbers remain `unverified`** — the standard is paywalled and absent locally; the project's own applicability doc records that the public preview *contradicts* two of the three. Do not treat those numbers as sound.

---

## Cross-discipline open questions

| # | Question | Route to |
|---|---|---|
| 1 | Is a 15–30 minute early-warning claim clinically substantiable in a **PCA/opioid** population, or only borrowed from general infusion? This gates F6's entire SE/De Novo argument | Clinical Affairs |
| 2 | Does alarm *filtering* (F4) reduce annunciation of a safety alarm in a way that changes a residual-risk conclusion? If yes, F4 is a risk-control change, not a feature | Risk Management |
| 3 | Can the three open IEC 60601-2-24 subclause `[VERIFY]`s be closed against a licensed copy before Hazard Analysis Rev 1.0 — and if the numbers change, does the V&V protocol design change with them? | V&V Lead + Quality Engineering |
| 4 | Does the Connectivity Adapter perform any transformation, alerting, or prioritisation that defeats the Non-Device MDDS classification? Who has verified that against the code? | Systems Engineering + R&D |
| 5 | Home/ambulatory PCA (F7) puts an opioid infusion under an untrained operator. What summative usability evidence would support a home-indication filing, and how long does generating it take? | Human Factors |
| 6 | Does the current SBOM build to the **CISA 2026** superset or only to the NTIA 2021 baseline FDA cites? | Cybersecurity |
| 7 | Does the program have bandwidth for two C-category filings in Y3 (F6 + F7) at P90 review times, alongside remediation risk on the marketed device? | Program Manager |

---

## Counterpoints and considerations

1. **The MEA drought cuts both ways.** Nine years with no filings under a code is also what a dying category looks like. A "PCA-first" regulatory identity may be clean and commercially disadvantaged at once; BD and ICU both structure their filings as PCA-as-a-module-on-a-platform. The product-code election should be made on that strategic axis, not only on naming accuracy. `OPINION`
2. **De Novo is not free.** It is slower, evidence-hungrier, and used by 2.6% of AI sponsors for good reason. My recommendation is to *ask FDA*, not to pre-commit — a Q-Sub presenting both options with a stated preference is cheaper than either wrong choice.
3. **I may be over-reading F5.** If Clinical Surveillance is genuinely retrospective analytics with no clinical action driven from it, category A is defensible and my B→C framing is too aggressive. That determination needs the actual function inventory — route it to Systems Engineering before acting on it.

---

## Changelog

| Date | Author | Summary |
|------|--------|---------|
| 2026-08-06 | AI assistant(s) — `regulatory-affairs` advisor | Initial regulatory assessment. Contributed F-7…F-11. Established that the commercial roadmap commits against regulatory decisions the regulatory strategy has not made (§§3/4/6/7/8 empty, §9 pending); that F4/F5 are mis-categorised as PCCP-authorized against the statutory §515C limit; that the F6 PCCP dependency is inverted per Appendix B Scenario 2; that De Novo has never been evaluated despite a nine-year predicate drought; that the standards matrix anchors on a non-recognized standard while omitting every recognized one; and that the device record carries **LZH ("Pump, Infusion, Enteral")** for a PCA pump, verified by live openFDA query. |
