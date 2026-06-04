---
id: commercial-roadmap-kol-review
title: "KOL Review — 5-Year Commercial Roadmap (PP3500)"
status: draft
component: pca-device
topic: clinical
created: 2026-06-03
last_updated: 2026-06-04
authored_by:
  - human:Ben Xavier
  - agent:clinical-affairs
  - agent:regulatory-affairs
  - agent:program-manager
  - agent:human-factors
  - agent:paul-james
  - agent:giuliano-kathleen
  - agent:kuitunen-sini
  - agent:shah-parth
  - agent:pennathur-priyadarshini
  - agent:kirkendall-evan
  - agent:gorski-lisa
  - agent:braithwaite-susan
grounded_against:
  - roadmap: docs/project/strategies/commercial-strategy.md  # subject under review
  - strategy: docs/project/strategies/regulatory-strategy.md  # carve-out, classifications, empty §3/§4
  - kol: docs/project/input-analysis/kol-feedback/  # 8 KOL profiles (all "not yet contacted")
  - market: docs/project/input-analysis/competitive-landscape/competitive-product-assessment.md  # $24M/42mo, +0.55, $350M/Y5
  - market: docs/project/input-analysis/market-research/strategic-market-ai-infusion.md  # 15-30min, alert-reduction, Omnipod benchmark
  - artifact: docs/project/dhfs/pca-device/design-controls/user-needs/user-needs.md  # cleared bright line; CAPA-2023-001
  - artifact: docs/project/dhfs/pca-device/design-controls/pccp/pccp-predetermined-change-control-plan.md  # v0.1 stub
  - standard: docs/external/standards/iec-62366-1.md  # use-spec / summative HF validation
  - guidance: docs/external/fda-guidance/pccp-aiml.md  # PCCP cannot expand intended use
  - guidance: docs/external/fda-guidance/sw-changes.md  # Flowchart A1 new population/environment
recommended_agents:
  - clinical-affairs
  - regulatory-affairs
  - program-manager
  - human-factors
superseded_by: null
---

# KOL Review — 5-Year Commercial Roadmap (PP3500)

> _Demo sample data — not for clinical use._

## Goal of this analysis

The user asked the KOLs to evaluate the project's new 5-year commercial roadmap (`docs/project/strategies/commercial-strategy.md`) and give their opinion — run through the **individual KOL agents** *and* our discipline advisors. This gap-analysis is that evaluation, run as **two agent layers**:

1. **Discipline advisors (our agents)** — **clinical-affairs** (primary, consolidated clinical voice), **regulatory-affairs** (pathway/PCCP feasibility), **program-manager** (executability/dependencies), **human-factors** (use-safety of the home-PCA leap). These authored findings **F-1…F-13**.
2. **KOL persona agents (our KOLs)** — one agent per named KOL on the roster, each grounded in its own profile and speaking in the first person: **Paul** (PCA/opioid safety), **Giuliano** + **Shah** (alarm/alert fatigue), **Kuitunen** (DERS/dose limits), **Kirkendall** (smart-pump safety/CDS/pediatrics), **Pennathur** (human factors), **Gorski** (infusion-nursing standards), **Braithwaite** (insulin/ambulatory-pump analogy). Each KOL's full opinion is captured as a separate `kol-KOL-NNNN-<name>.md` document, and each contributes one headline finding **F-14…F-21**.

> **Demo integrity note.** The KOL agents are **simulated persona opinions** generated for this demo — *not* real collected feedback. This is consistent with finding **F-1**: the project's 8 KOL profiles are marked "not yet contacted," so in a real program these simulated opinions would be replaced by actual KOL interviews.

- **Motivating question:** Is the 5-year roadmap clinically, regulatorily, and operationally credible — or does it over-claim on borrowed evidence, an unwritten PCCP, and unresourced dependencies?
- **Decision the analysis informs:** Whether the roadmap can be committed as-is, or must be re-cut (re-categorized features, gated GAs, evidence plans) before Year-1 commit.
- **Stakeholders:** Commercial lead, Regulatory Affairs, Program Management, Clinical Affairs, Human Factors, Risk.

## Expected methodology

Each advisor critiques the roadmap against the bar appropriate to its discipline and cites project artifacts + standards:

- **clinical** — context-matched clinical evidence (PCA/opioid, not borrowed general-infusion); ISO 14155 / clinical-evaluation framing; KOL-attribution discipline.
- **regulatory** — FDA change-significance test (21 CFR 807.81(a)(3)); PCCP AI/ML guidance (a PCCP cannot expand intended use); sw-changes Flowchart A1 (new population/environment → new submission); Q-Sub = feedback, not authorization.
- **program** — executability bar: every release names a vehicle that exists or is funded; upstream evidence resourced; stage-gates with owners/acceptance; mapped critical path.
- **human-factors** — IEC 62366-1 Clause 5.1–5.6: a material change to user / environment / UI re-opens use specification → URRA → formative → summative validation.

Findings anchor to that declared bar; "the roadmap is missing X" is only valid against the stated expectation.

## Source being analyzed

### Primary source
- `docs/project/strategies/commercial-strategy.md` — the 5-year commercial roadmap (decisions D-COMM-1.1 … D-COMM-1.9; the F1–F9 feature table; the R1–R5 risk register).

### Reference standards / external
- `docs/external/standards/iec-62366-1.md` §5.1–5.6 (use specification, summative HF validation).
- `docs/external/fda-guidance/pccp-aiml.md` (PCCP scope); `docs/external/fda-guidance/sw-changes.md` (change-significance); `docs/external/fda-guidance/qsub.md` (Q-Sub = feedback).

### Related context
- `docs/project/strategies/regulatory-strategy.md` (Ct* carve-out; component classifications; empty §3/§4).
- `docs/project/input-analysis/kol-feedback/` (8 KOL profiles); market/competitive research; `user-needs.md` (cleared bright line + CAPA-2023-001); PCCP v0.1 stub.

## Assertions

| # | Assertion | Clause / decision | Evidence (path) | Status |
|---|---|---|---|---|
| A1 | Every feature in D-COMM-1.4 with a named KOL anchor has a recorded KOL opinion on that feature. | D-COMM-1.4 | `kol-feedback/*` ("Not yet contacted") | **refuted** |
| A2 | The F6 15–30 min predictive-warning + 60% adverse-event-reduction claim is substantiated in a PCA/opioid (OIRD) population. | D-COMM-1.4 F6 | `strategic-market-ai-infusion.md` L28–29, L60 | **refuted** |
| A3 | Every roadmap feature tagged "B (PCCP)" has a written, authorized PCCP envelope covering it. | FDA PCCP AI/ML | `pccp-...-plan.md` (v0.1 stub) | **refuted** |
| A4 | F6/F7/F8 regulatory categories correctly reflect FDA change-significance (no new intended use / environment misclassified). | sw-changes Flowchart A1 | `sw-changes.md`; D-COMM-1.4 | **refuted** |
| A5 | F7 home-PCA commits to a fresh IEC 62366-1 use specification + summative HF validation before GA. | IEC 62366-1 §5.1–5.6 | `user-needs.md`; D-COMM-1.4 F7 | **refuted** |
| A6 | F4's alarm-reduction claim is paired with a bounded maximum missed-true-alarm rate. | D-COMM-1.4 F4 / R2 | `commercial-strategy.md` D-COMM-1.4 | **refuted** |
| A7 | The roadmap's upstream dependencies (ben/011 tagging, ben/049 SRS) are scheduled + resourced, not merely acknowledged. | D-COMM Open Items | `tasks/ben/000-index.md` | **refuted** |
| A8 | The Y5 international wave (D-COMM-1.6) is supported by populated regulatory-strategy §3/§4. | D-COMM-1.6 | `regulatory-strategy.md` §3/§4 (empty) | **refuted** |
| A9 | The $24M / 42-month predictive build timeline is consistent with the F6 Year-3 launch slot. | D-COMM-1.4 F6 / D-COMM-1.7 | `competitive-product-assessment.md` | **refuted** |
| A10 | The roadmap's sequencing logic (front-load Cloud Suite monetization, defer capital-intensive bets) is sound. | D-COMM-1.3 | all four advisor reviews | **confirmed** |
| A11 | F1/F2/F3 (Y1 Cloud Suite) are correctly classified and the lowest-risk wave. | D-COMM-1.4 / reg-strategy §2 | `regulatory-strategy.md` §2 | **partial** |
| A12 | F8 dose-personalization adequately addresses use-transparency / automation-bias. | IEC 62366-1 §5.2 | D-COMM-1.4 F8 | **refuted** |

## Assertion positions

_Per-advisor stance on each assertion (Positive = advisor judges the claim holds / the roadmap satisfies it; Negative = a real gap; Neutral = partial / depends / out of lane). Rendered as the click-to-expand detail behind each assertion in the project-console. Stances distilled from the discipline-advisor and KOL-panel responses in this folder._

### A1
- negative — clinical-affairs: KOLs never contacted; a specialty mapping is not an endorsement
- negative — paul-james: I have not been contacted — don't present my match as my view
- negative — regulatory-affairs: a CER reviewer won't accept uncollected KOL opinion as input

### A2
- negative — clinical-affairs: 15–30 min / 60% figures are general-infusion, not an OIRD cohort
- negative — paul-james: 73% sensitivity = ~1-in-4 missed; for respiratory depression that is the whole question
- negative — shah-parth: precision / false-negative rate never reported alongside the warning window
- negative — braithwaite-susan: borrowing an effect size across unlike failure modes

### A3
- negative — regulatory-affairs: the project PCCP is a v0.1 stub; a PCCP also can't carry a new clinical claim
- negative — program-manager: the Ct* tagging keystone (ben/011) that defines the envelope is Not Started
- negative — kuitunen-sini: library-update envelope is named but not instantiated

### A4
- negative — regulatory-affairs: F6/F7/F8 introduce new intended use / environment → De Novo risk, not routine 510(k)
- negative — paul-james: home opioid PCA is a new use, not a tweak of the cleared device
- neutral — program-manager: categories may hold, but the pathway is unconfirmed until the Q-Sub

### A5
- negative — human-factors: no fresh use-spec or summative HF validation is committed for F7
- negative — pennathur-priyadarshini: F7 changes user, environment, and tasks at once — can't inherit validation
- negative — gorski-lisa: F7 has no named competency-verified operator or INS home-infusion anchor

### A6
- negative — giuliano-kathleen: a count reduction is not a safety claim; there is no suppressed-true-alarm floor
- negative — shah-parth: the alert metric is one-sided — sensitivity / false-negative not paired
- negative — human-factors: the over-suppression / missed-critical-alarm use error is unaddressed

### A7
- negative — program-manager: ben/011 Not Started + ben/049 paused — acknowledged is not the same as managed
- negative — regulatory-affairs: the PCCP envelope can't be instantiated until the tagging pass runs

### A8
- negative — regulatory-affairs: regulatory-strategy §3 (jurisdictional) and §4 (filing sequence) are both empty
- negative — kuitunen-sini: EU MDR library-governance evidence must start in Y1–Y2, not Y5
- neutral — program-manager: Y5 is appropriately soft, but it can't be firmed on empty sections

### A9
- negative — program-manager: a 42-month build started ~Y2 lands ~Y5, past the F6 Year-3 slot — an internal inconsistency
- neutral — clinical-affairs: a slower evidence build is actually safer; re-slot rather than rush

### A10
- positive — clinical-affairs: owning predictive intelligence rather than another me-too pump is the right wedge
- positive — regulatory-affairs: front-loading low-risk Cloud Suite and deferring capital-intensive bets is correct
- positive — program-manager: the shape is right; the risk is in resourcing, not the sequence
- positive — giuliano-kathleen: disciplined — each year gated on the prior clearance
- positive — gorski-lisa: defend the base, connect, then expand is the correct instinct

### A11
- neutral — regulatory-affairs: F2/F3 are correctly classed; F1's Y1 "LtF/PCCP" vehicle label conflicts with its own 510(k)
- negative — program-manager: F1 is over-stuffed into Y1 — own 510(k), filing path still TBD
- neutral — kuitunen-sini: F1 is the right class but under-specified as a governed DERS

### A12
- negative — human-factors: automation bias is unaddressed; F8 needs use-transparency + a confirmation friction point
- negative — pennathur-priyadarshini: the clinician becomes a decision-checker and under-scrutinizes trusted automation
- negative — braithwaite-susan: there is no objective opioid safety biomarker for the loop to optimize against

## KOL Panel — individual opinions

The 8-member KOL roster was run as **individual persona agents**, each speaking for itself. Full opinions are captured as separate documents (linked below); each KOL's headline concern is also carried as a finding (F-14…F-21). _Simulated persona opinions — demo only; see the integrity note above._

| KOL | Specialty | Verdict | Headline concern | Finding | Full opinion |
|---|---|---|---|---|---|
| **Dr. James Paul** (KOL-0006) | PCA / opioid safety (the anchor) | Endorse w/ reservations | Gate every intelligence feature on PCA/opioid-specific evidence + a clinician-accepted missed-true-event bound | F-14 | [kol-KOL-0006-paul-james.md](kol-KOL-0006-paul-james.md) |
| **Dr. Kathleen Giuliano** (KOL-0001) | Smart-pump usability / alarm fatigue | Conditional | F4 must carry a pre-specified suppressed-true-alarm sensitivity floor, not a count reduction | F-15 | [kol-KOL-0001-giuliano-kathleen.md](kol-KOL-0001-giuliano-kathleen.md) |
| **Dr. Parth Shah** (KOL-0008) | Alert fatigue / alert optimization | Conditional | Adopt a two-sided alert metric (sensitivity + false-negative, paired) as a hard gate | F-16 | [kol-KOL-0008-shah-parth.md](kol-KOL-0008-shah-parth.md) |
| **Sini Kuitunen, PharmD** (KOL-0004) | DERS / dose-limit safety | Conditional | F1 must be a *governed* hard/soft-limit DERS with a validation gate; F8 subordinate to F1 hard limits | F-17 | [kol-KOL-0004-kuitunen-sini.md](kol-KOL-0004-kuitunen-sini.md) |
| **Dr. Evan Kirkendall** (KOL-0002) | Smart-pump safety / CDS / pediatrics | Qualified yes | Pediatric scope is undefined — decide in/out; effect sizes need population-stratified sensitivity/specificity | F-18 | [kol-KOL-0002-kirkendall-evan.md](kol-KOL-0002-kirkendall-evan.md) |
| **Dr. Priyadarshini Pennathur** (KOL-0005) | Human factors / usability | Conditional | F7 needs a *new* IEC 62366-1 use specification + lay-user summative validation; F8 needs use-transparency | F-19 | [kol-KOL-0005-pennathur-priyadarshini.md](kol-KOL-0005-pennathur-priyadarshini.md) |
| **Lisa Gorski** (KOL-0007) | Infusion-nursing standards | Conditional yes | Connected/home features lack a named nurse/caregiver workflow + INS-standards conformance | F-20 | [kol-KOL-0007-gorski-lisa.md](kol-KOL-0007-gorski-lisa.md) |
| **Dr. Susan Braithwaite** (KOL-0003) | Insulin / ambulatory-pump analogy | Mixed | Borrow insulin-pump form factor only — never its risk tolerance; F8 needs an objective respiratory-safety biomarker | F-21 | [kol-KOL-0003-braithwaite-susan.md](kol-KOL-0003-braithwaite-susan.md) |

**Panel read:** No KOL opposed the roadmap outright; every one endorsed the *strategic shape* and gated their support on **evidence discipline** — substantiate claims in PCA/opioid context, bound the false-negative side of every alarm/prediction claim, and re-derive the home-setting safety case rather than borrowing it. The panel independently piled onto the same seams the discipline advisors found (see Convergence), and added four genuinely new ones: **DERS governance** (Kuitunen, F-17), **pediatric scope** (Kirkendall, F-18), **INS nursing-workflow standards** (Gorski, F-20), and the **insulin-analogy risk-tolerance trap** (Braithwaite, F-21).

## Findings

**Coverage scope:** Findings **F-1…F-13** are from the discipline advisors; **F-14…F-21** are the KOL panel's headline concerns (one per KOL). All critique the roadmap document (`commercial-strategy.md`) and its traceability to the project's own inputs. Out-of-scope: the underlying clinical truth of the market figures (they are demo estimates already flagged `[VERIFY]` in D-COMM-1.7); the build of the features themselves.

### Summary table

| # | Status | Short label | Artifact(s) affected | Category | Severity | Effort | Blocks roadmap commit? | Multi-agent | Depends on |
|---|---|---|---|---|---|---|---|---|---|
| F-1 | open | KOL "anchors" are uncontacted records, not opinions | commercial-strategy D-COMM-1.4; kol-feedback/* | Methodology | high | med | YES | clinical | — |
| F-2 | open | F6 predictive warning borrowed from general infusion, not PCA/OIRD | D-COMM-1.4 F6, D-COMM-1.1 | Substantiation | high | high | YES | **3-agent** (clin+reg+PM) | A2 |
| F-3 | open | F4 alarm claim cites general-infusion numbers, no suppressed-true bound | D-COMM-1.4 F4, R2 | Substantiation | med | med | no | clin + HF | F-12 |
| F-4 | open | F7 home opioid PCA — benefit-risk not re-derived for setting | D-COMM-1.4 F7, R3 | Coverage | high | high | YES | **3-agent** (clin+HF+reg) | F-11, F-6 |
| F-5 | open | PCCP envelope cited but unwritten + can't carry new claims | D-COMM-1.3/1.4; pccp stub | Substantiation | high | med | YES | reg + PM | — |
| F-6 | open | F6/F7/F8 under-categorized — new intended use / environment (De Novo risk) | D-COMM-1.4 | Drift | high | med | YES | reg (+ clin/HF on F7) | — |
| F-7 | open | International wave depends on empty reg-strategy §3/§4 | D-COMM-1.6; regulatory-strategy §3/§4 | Coverage | med | low | no | reg + PM | — |
| F-8 | open | Year-1 over-stuffed: 3 concurrent GAs incl. un-pathed own-510(k) SaMD | D-COMM-1.3/1.4; regulatory-strategy §2 | Coverage | high | med | YES | PM | F-5 |
| F-9 | open | Keystone deps not resourced (ben/011 Not Started, ben/049 paused) | D-COMM Open Items; tasks index; reg-strategy §1 | Substantiation | high | high | YES | PM (+ reg) | — |
| F-10 | open | Serialized clearance-gating + $24M/42mo collides with Y3 slot | D-COMM-1.3, R4, D-COMM-1.7 | Methodology | med | med | no | PM | F-9 |
| F-11 | open | F7 needs fresh use-spec + summative HF validation | D-COMM-1.4/1.9; user-needs.md | Coverage | high | high | YES | HF (+ clin) | F-4 |
| F-12 | open | F4 alarm-suppression introduces missed-critical-alarm use error | D-COMM-1.4 F4 | Methodology | high | med | no | HF + clin | F-3 |
| F-13 | open | F8 dose-personalization is an unaddressed use-transparency risk | D-COMM-1.4 F8 | Substantiation | med | med | no | HF | — |
| F-14 | open | Gate every intelligence feature on PCA/opioid evidence + a missed-true-event bound | D-COMM-1.4 F4/F6/F8 | Methodology | high | high | YES | KOL Paul (+clin) | F-2, F-3 |
| F-15 | open | F4 needs a pre-specified suppressed-true-alarm sensitivity floor, not a count cut | D-COMM-1.4 F4 | Substantiation | high | med | no | KOL Giuliano (+clin/HF) | F-3, F-12 |
| F-16 | open | Adopt a two-sided alert metric (sensitivity + false-neg paired) as a hard gate | D-COMM-1.4 F4/F6/F8 | Methodology | high | med | YES | KOL Shah (+clin) | F-3 |
| F-17 | open | F1 must be a governed hard/soft-limit DERS w/ validation gate; F8 ≤ F1 hard limits | D-COMM-1.4 F1/F8 | Coverage | high | med | YES | KOL Kuitunen | — |
| F-18 | open | Pediatric population scope undefined — decide in/out; stratify effect sizes | D-COMM-1.2/1.4 | Coverage | high | low | no | KOL Kirkendall | — |
| F-19 | open | F7 needs new IEC 62366-1 use-spec + lay-user summative; F8 needs use-transparency | D-COMM-1.4 F7/F8 | Coverage | high | high | YES | KOL Pennathur (+HF) | F-11, F-13 |
| F-20 | open | Connected/home features lack named nurse/caregiver workflow + INS-standards conformance | D-COMM-1.4 F2/F3/F7 | Coverage | high | med | no | KOL Gorski | — |
| F-21 | open | Insulin-pump precedent transfers form-factor only, not risk tolerance; F8 needs respiratory biomarker | D-COMM-1.4 F7/F8, D-COMM-1.8 | Substantiation | high | med | YES | KOL Braithwaite | F-4 |

**Resolution progress:** 0 / 21 resolved. 21 open. 0 deferred. 0 superseded. _(F-1…F-13 discipline advisors; F-14…F-21 KOL panel.)_

**Headline reads:**
- **Gate-blockers (11):** F-1, F-2, F-4, F-5, F-6, F-8, F-9 (advisors) + F-14, F-16, F-17, F-19, F-21 (KOL panel) should be resolved before the roadmap is committed for Year-1 execution or shown externally.
- **Strongest consensus — now reinforced by the KOL panel:** **F7 home opioid PCA** (advisors clinical+HF+regulatory; KOLs Paul, Pennathur, Gorski, Braithwaite) and **F6 predictive monitoring / one-sided alarm claims** (advisors clinical+regulatory+PM; KOLs Paul, Giuliano, Shah, Kirkendall). When 7 independent voices land on the same two features, those are the calls to act on first.
- **New issues the KOL panel surfaced (not in F-1…F-13):** DERS governance / hard-soft-limit discipline (F-17, Kuitunen), pediatric scope decision (F-18, Kirkendall), INS nursing-workflow standards (F-20, Gorski), and the insulin-analogy risk-tolerance trap + missing respiratory biomarker (F-21, Braithwaite).
- **Foundation gaps:** the roadmap rests on **uncontacted KOLs** (F-1 — and note the KOL opinions here are *simulated* for the demo), an **unwritten PCCP** (F-5), and **unresourced keystone tasks** (F-9).
- **What every voice endorses:** the *sequencing shape* (A10 confirmed) — front-loading Cloud Suite monetization and deferring capital-intensive AI/hardware is the right strategy. No KOL opposed it; all 8 gated support on **evidence discipline**, not on strategy.

### F-1: KOL "anchors" are uncontacted bibliographic records, not recorded opinions
- **Status:** open
- **Category:** Methodology
- **Severity:** high
- **Effort:** med
- **Author:** agent:clinical-affairs
- **What:** D-COMM-1.4 attaches a named KOL to each feature ("KOL anchor" column) and D-COMM-1.1 cites "+0.55 / +0.16" sentiment as KOL validation. But all eight named KOL profiles are bibliographic records with engagement status "None - Not yet contacted" and "No notes recorded." The sentiment numbers come from a separate 28-expert market-research panel, not from Paul, Giuliano, Kuitunen, et al. The roadmap presents a specialty-to-feature mapping as if it were validated KOL endorsement.
- **Evidence:** `kol-feedback/KOL-0006-paul-james.md` (+7 siblings): "Not yet contacted / No notes recorded"; `competitive-product-assessment.md` L33 ("+0.55"/"+0.16" trace to the market panel).
- **Worked example (before / after):** Before — "F6 … KOL anchor: Giuliano, Paul" implying endorsement. After — "F6 … KOL anchor (specialty match, opinion not yet collected): Giuliano, Paul — interview pending; no recorded position as of 2026-06-03." **[illustrative]**
- **Impact:** Clinical: roadmap rests on unvalidated voice. Filing: a CER reviewer would not accept uncollected KOL opinion as clinical input. Commercial: any "KOL-validated" claim is unsupportable.
- **Resolution proposal:** Run actual KOL interviews; add dated per-feature notes in `kol-feedback/`; relink the D-COMM-1.4 anchor column to those notes.
- **Owner / next step:** Clinical Affairs — schedule interviews before the roadmap is used externally (pre-Y1 commit).

### F-2: F6 15–30-min predictive warning borrowed from general infusion, not PCA/opioid OIRD
- **Status:** open
- **Category:** Substantiation
- **Severity:** high
- **Effort:** high
- **Author:** agent:clinical-affairs
- **What:** The flagship F6 claim (15–30 min early warning; 60% adverse-event reduction) is sourced from general-infusion data and a non-PCA deterioration model (73% sensitivity), and from Mass General/Mayo general-monitoring deployments — none opioid-PCA OIRD. A 73% deterioration sensitivity implies ~1 in 4 true events missed; for respiratory depression that residual is the entire clinical question, and it is unaddressed.
- **Evidence:** `strategic-market-ai-infusion.md` L28–29 (window; BiointelliSense 73%), L60 (60% AE reduction, general monitoring); `commercial-strategy.md` D-COMM-1.1 + R1 (R1 names the gap; the F6 row still over-claims).
- **Worked example (before / after):** Before — "AI-enabled entrants demonstrate 15–30 min early warnings." After — "15–30-min figures derive from general-infusion/non-PCA deterioration data; OIRD sensitivity, missed-true rate, and lead-time in a PCA cohort are not yet established — treat as feasibility signal pending a PCA/opioid evidence package." **[illustrative]**
- **Impact:** Clinical: core safety claim unsubstantiated for the actual hazard. Filing: F6's new-510(k) clinical evidence would not support an OIRD claim on borrowed data. Commercial: predictive wedge (D-COMM-1.8) un-marketable until cleared on PCA evidence.
- **Resolution proposal:** Commission a PCA/opioid clinical-evaluation + literature-search plan targeting OIRD endpoints; gate F6's Year-3 commit on it; re-label borrowed numbers as feasibility signal.
- **Owner / next step:** Clinical Affairs (+ Risk for residual-risk threshold) — initiate evidence plan before the Year-2 stage gate.

### F-3: F4 alarm-fatigue claim cites general-infusion alert numbers without bounding suppressed true alarms
- **Status:** open
- **Category:** Substantiation
- **Severity:** med
- **Effort:** med
- **Author:** agent:clinical-affairs
- **What:** F4 promises alarm-fatigue reduction citing "45% reduction in non-actionable alerts / 80% reduction in alert deviation" — general smart-pump figures. The claim is one-sided: it quantifies alarm reduction but does not bound the suppressed-true-alarm (missed real event) rate. In a PCA context, over-suppression of an early OIRD signal is categorically more dangerous than suppressing a nuisance occlusion alarm.
- **Evidence:** `strategic-market-ai-infusion.md` L16 (45%/80%, general infusion); `commercial-strategy.md` D-COMM-1.4 F4 + R2 (R2 names the risk; F4 still presents the bare number).
- **Worked example (before / after):** Before — "Alerts Engine v1 — smart alarm filtering / alert-fatigue reduction (45% non-actionable reduction)." After — "Alerts Engine v1 — alarm filtering with a bounded maximum suppressed-true-alarm rate [target TBD]; general-infusion 45% is feasibility signal, re-validated for PCA alarm classes under IEC 60601-1-8." **[illustrative]**
- **Impact:** Clinical: clinicians distrust unbounded "fewer alarms." Filing: alarm-system change touches IEC 60601-1-8 essential performance. Commercial: an over-promised number invites field complaints.
- **Resolution proposal:** Add a suppressed-true-alarm acceptance bound to F4; decompose "alert reduction" into actionable vs missed-true; validate against PCA alarm classes.
- **Owner / next step:** Clinical + Risk — define metric before F4 Year-2 design inputs lock.

### F-4: F7 home opioid PCA benchmarked to insulin patch; setting-specific benefit-risk not re-derived
- **Status:** open
- **Category:** Coverage
- **Severity:** high
- **Effort:** high
- **Author:** agent:clinical-affairs
- **What:** F7 moves patient-actuated opioid PCA into the unsupervised home, benchmarked on form factor against insulin patch pumps (Omnipod 72-hr). The benchmark imports a form factor from a category whose failure mode (glycemic excursion, slow onset) is far more forgiving than OIRD (minutes to apnea), and the user shifts from trained nurse to patient/family caregiver. The roadmap does not re-derive the benefit-risk or use-related risk analysis for the home setting; R3 names the risk but F7 still commits to Year 3→4 GA.
- **Evidence:** `strategic-market-ai-infusion.md` L18 (180g/7-day vs Omnipod); `commercial-strategy.md` D-COMM-1.4 F7, D-COMM-1.8, R3.
- **Worked example (before / after):** Before — "Ambulatory PP3500-A — lightweight wearable PCA hardware (vs Omnipod 72-hr)." After — "Ambulatory PP3500-A — home opioid PCA, gated on a setting-specific use-related risk analysis and benefit-risk re-derivation for the patient/caregiver user; insulin-patch benchmark is a form-factor reference only, not a safety-evidence basis." **[illustrative]**
- **Impact:** Clinical: highest-consequence leap; unsupervised opioid delivery. Filing: new home indication requires its own HF validation + benefit-risk. Commercial: a home opioid misadventure is an existential program risk.
- **Resolution proposal:** Require a home-setting HF + benefit-risk study as a hard gate before F7 GA; don't let the diabetes-patch benchmark stand in for safety evidence.
- **Owner / next step:** Human Factors + Clinical — scope the home-setting study before the Year-3 ambulatory-entry milestone.

### F-5: PCCP envelope is cited as a vehicle but is unwritten and cannot legally carry the changes claimed
- **Status:** open
- **Category:** Substantiation
- **Severity:** high
- **Effort:** med
- **Author:** agent:regulatory-affairs
- **What:** D-COMM-1.4 tags F4/F5 (and the retraining halves of F6/F8) as "B (PCCP)," but (a) the project PCCP is a **v0.1 placeholder stub** with unpopulated `{{template}}` fields — no envelope exists; and (b) per `pccp-aiml.md`, a PCCP only covers modifications *within* the cleared intended use that keep the device SE to predicate, so it can never carry an *initial* clinical claim. A PCCP also needs a cleared baseline device to attach to — F4's smart-alarm SaMD has none yet.
- **Evidence:** `pca-device/design-controls/pccp/pccp-predetermined-change-control-plan.md` (stub); `docs/external/fda-guidance/pccp-aiml.md` (Description of Modifications — intra-intended-use, SE).
- **Worked example (before / after):** Before — "F4 Alerts Engine v1 — Reg. category **B (PCCP)**, Y2." After — "F4 needs an **initial 510(k) (C)** to establish the smart-alarm SaMD; only subsequent retraining within its cleared indication is PCCP-eligible. 'B' presumes a cleared baseline that does not exist in Y2."
- **Impact:** Regulatory: relies on an authorization (and a document) that doesn't exist. Filing: PCCP must be authored and *cleared in a 510(k)* before any "B" cell is real. Commercial: $24M predictive spend (D-COMM-1.7) gated behind a vehicle the team doesn't yet hold.
- **Resolution proposal:** Author the PCCP (three required sections per `pccp-aiml.md`); re-label every "B" cell to split initial-clearance from PCCP-covered retraining; run the Ct* tagging pass so the envelope is defined structurally.
- **Owner / next step:** RA lead — populate the PCCP stub and re-cut D-COMM-1.4's vehicle column.

### F-6: F6/F7/F8 are under-categorized — new intended use / population / environment beyond a routine new-indication 510(k)
- **Status:** open
- **Category:** Drift
- **Severity:** high
- **Effort:** med
- **Author:** agent:regulatory-affairs
- **What:** F6 (predictive deterioration/occlusion warning) is a new *clinical output* on an opioid PCA — plausibly a new intended use the PP3000 alarm-only predicate cannot support (De Novo risk). F7 stacks a new hardware variant with a new use environment + new user — per `sw-changes.md` Flowchart A1 that is new-510(k) territory and a strong **De Novo / different product code** candidate. F8 (dose-personalization decision-support) recommends opioid dosing and may exit the CDS non-device carve-out. The roadmap treats all three as predictable 510(k)+PCCP off the existing predicate.
- **Evidence:** `docs/external/fda-guidance/sw-changes.md` Flowchart A1; `submissions/510k/composition-manifest.md` (predicate PP3000 K190567, alarm-only); D-COMM-1.4 F6–F8.
- **Worked example (before / after):** Before — "F7 — C (new clearance + home indication), rides PP3500." After — "F7 = new variant + new unsupervised-home environment + new user → confirm product code and **De Novo vs 510(k)** at Q-Sub; PP3500 predicate may not carry the home opioid indication."
- **Impact:** Regulatory: pathway is unconfirmed, not 'C-as-drawn.' Filing: De Novo for F6/F7 changes timelines + evidence burden materially. Commercial: Years 3–5 cascade off these — a De Novo finding resets dependent launches.
- **Resolution proposal:** Re-categorize F6/F7/F8 with explicit "pathway TBD pending Q-Sub"; route De Novo-vs-510(k) + product-code questions into the M12 Q-Sub; pull predicate analysis to test SE for a predictive claim.
- **Owner / next step:** RA lead — add F6/F7/F8 pathway questions to the Q-Sub; flag De Novo contingency in D-COMM-1.4.

### F-7: International wave (D-COMM-1.6) commits to EU MDR / Canada while the strategy sections it depends on are empty
- **Status:** open
- **Category:** Coverage
- **Severity:** med
- **Effort:** low
- **Author:** agent:regulatory-affairs
- **What:** D-COMM-1.6 sequences EU MDR + Health Canada in Years 4–5 and even names KOL anchors, but `regulatory-strategy.md` §3 *Jurisdictional Differences* and §4 *Filing Sequence* are both "No strategy content assembled yet," and the Jurisdictional roadmap is an open Pending Regulatory Decision. The roadmap commits to a wave whose enabling analysis does not exist.
- **Evidence:** `commercial-strategy.md` D-COMM-1.6 + Open Items; `regulatory-strategy.md` §3, §4, Pending Decisions.
- **Worked example (before / after):** Before — "Y5 — international (EU MDR / Canada) expansion." After — "Y5 international **gated** on authoring regulatory-strategy §3 (Jurisdictional Differences) + §4 (Filing Sequence); EU MDR class + conformity route for an AI-enabled opioid PCA confirmed before commit."
- **Impact:** Regulatory: dependency on unwritten sections. Filing: EU MDR route/class undetermined. Commercial: Year-5 revenue line rests on an unscoped market entry.
- **Resolution proposal:** Treat D-COMM-1.6 Y5 as provisional until §3/§4 are populated; author a minimal Jurisdictional Differences brief (US vs EU MDR vs Canada classification + conformity route) as the Y4 dependency.
- **Owner / next step:** RA — populate regulatory-strategy §3/§4; mark D-COMM-1.6 Y5 provisional pending that.

### F-8: Year-1 over-stuffed — three concurrent GAs including an un-pathed own-510(k) SaMD
- **Status:** open
- **Category:** Coverage
- **Severity:** high
- **Effort:** med
- **Author:** agent:program-manager
- **What:** D-COMM-1.3 commits Y1 to three simultaneous GA launches (Drug Library Manager, Connectivity Adapter, Fleet/Telemetry). F1 Drug Library Manager is reg-category C — its **own 510(k)** — yet `regulatory-strategy.md` §2 still lists its filing path (accessory bundle vs standalone) as **TBD**. A feature whose regulatory vehicle is undecided cannot be safely committed as a Y1 GA alongside two other launches.
- **Evidence:** `commercial-strategy.md` D-COMM-1.4 F1 (C, Y1); `regulatory-strategy.md` §2 ("bundled … or standalone — TBD").
- **Worked example (before / after):** Before — "F1 Drug Library Manager GA — Y1." After — "F1 — Y1 commercial-readiness target; regulatory GA gated on filing-path decision + ben/011 + ben/049 + FDA clearance; may land Y2."
- **Impact:** Schedule: F1 GA likely slips to Y2 once filing path + clearance are sequenced. Filing: undecided accessory-vs-standalone path blocks submission planning. Commercial: Y1 attach-rate story leans on F1; a slip softens the Y2 growth lever.
- **Resolution proposal:** Resolve F1's filing path now; re-label Y1 GA dates as commercial-readiness vs the binding clearance gate; allow F1 to slip to Y2 without cascading.
- **Owner / next step:** Regulatory + Program — resolve accessory-bundle vs standalone 510(k) and re-date F1.

### F-9: Keystone upstream dependencies acknowledged but not resourced
- **Status:** open
- **Category:** Substantiation
- **Severity:** high
- **Effort:** high
- **Author:** agent:program-manager
- **What:** The feature-to-filing categorization (D-COMM-1.4) and the PCCP envelope depend on the Ct* criticality tagging pass (ben/011), which is **Not Started**, and on the SRS layer (ben/049), which is **paused** mid-build. The Open Items name §3 and ben/011 but are **silent on ben/049**. SaMD GAs (F1 Y1; F4/F5 Y2) cannot reach clearance without SW requirements and traced V&V. These are acknowledged risks, not managed (scheduled + staffed) ones.
- **Evidence:** `commercial-strategy.md` Open Items; `tasks/ben/000-index.md` (ben/011 Not Started; ben/049 paused); `regulatory-strategy.md` §1 (PCCP envelope = Ct*-tagged change types).
- **Worked example (before / after):** Before — Open Item "depends on ben/011, not yet started." After — dependency-register row "ben/011: owner Regulatory+Program; start date X; acceptance = trace-matrix Filing Scope column populated; blocks Y1 F1 + all Y2 PCCP releases" plus a parallel ben/049 row.
- **Impact:** Schedule: keystone tagging un-started → 510(k)+PCCP scope + V&V split unstarted; Y1/Y2 dates unanchored. Filing: PCCP envelope (the change-velocity thesis) can't be instantiated until ben/011 runs. Commercial: the recurring-software revenue model (D-COMM-1.7) rides on PCCP-authorized releases that depend on this keystone.
- **Resolution proposal:** Promote ben/011 + ben/049 into the roadmap's dependency register with owners, start dates, acceptance; sequence both before Y1 commit; verify staffing against the 30+ in-flight tasks.
- **Owner / next step:** Program — build the dependency register; Regulatory (ben/011) + Engineering (ben/049) own execution.

### F-10: Serialized clearance-gating ignores FDA review variance and collides with the predictive build timeline
- **Status:** open
- **Category:** Methodology
- **Severity:** med
- **Effort:** med
- **Author:** agent:program-manager
- **What:** D-COMM-1.3 and R4 commit to "each year's flagship gated on the prior year's clearance" — a fully serialized chain against FDA review, whose timing varies; one long Q-Sub or 510(k) cascades through every downstream year. Compounding this, the $24M / 42-month predictive build, if started at Y2 per the gating logic, completes ~Y5 — **past** its Y3 launch slot in D-COMM-1.4. The plan does not reconcile the 42-month duration with the Y3 commitment.
- **Evidence:** `commercial-strategy.md` D-COMM-1.3, R4, D-COMM-1.7; `competitive-product-assessment.md` ($24M / 42 months); D-COMM-1.4 F6 (Y3).
- **Worked example (before / after):** Before — "F6 Predictive monitoring — Y3" with the build gated behind Y1/Y2 traction. After — predictive build kicks off no later than early Y2 to clear by Y3, OR F6 re-slots to Y4/Y5 with the 68% IRR re-underwritten; parallel pre-work (Q-Sub, evidence generation) overlaps prior-year clearance windows.
- **Impact:** Schedule: serialized gating makes end-to-end timeline a sum of worst-case FDA windows; the 42-month/Y3 collision is an internal inconsistency. Filing: no parallelism → no slack for review variance. Commercial: headline 68% IRR underwrites to a Y3 launch the build duration may not support.
- **Resolution proposal:** De-serialize via explicit parallel pre-work overlapping clearance windows; reconcile the 42-month build against the Y3 slot (start-early or re-slot); treat each gate as a real decision point with acceptance criteria.
- **Owner / next step:** Program + Regulatory — model the predictive build backward from Y3 and add parallel-track scheduling (mitigates R4).

### F-11: F7 home-PCA crosses the cleared bright line — needs a fresh use specification and full IEC 62366-1 formative+summative validation
- **Status:** open
- **Category:** Coverage
- **Severity:** high
- **Effort:** high
- **Author:** agent:human-factors
- **What:** The roadmap moves opioid PCA from supervised hospital use to unsupervised home/ambulatory use (F7) and names the risk (R3) but never commits F7 to a new use specification, formative+summative HF validation, or new use-error risk controls. F7 changes all three IEC 62366-1 Clause-5.1 axes at once (user, environment, use-error consequence), so the cleared 98.7% task-success evidence does not transfer. The cleared user-needs file explicitly states the device is "not intended for unsupervised home or ambulatory use."
- **Evidence:** `commercial-strategy.md` D-COMM-1.4 F7, R3; `user-needs.md` (Intended Use / Indications — explicit home exclusion; UN-003/UN-020; CAPA-2023-001); `iec-62366-1.md` §5.1–5.6.
- **Worked example (before / after):** Before — a family caregiver presses the bolus button by proxy on an already-sedated home patient; inherited hospital lockout limits assume a monitoring nurse, none present → over-sedation → respiratory depression with no responder. After — a fresh F7 use spec + URRA make "unauthorized/by-proxy activation" and "unattended over-sedation" critical tasks; controls (single-authorized-user activation, on-device respiratory monitoring + remote escalation, lay-user-validated IFU) proven in formative rounds + a summative HF validation before GA.
- **Impact:** Safety: highest-consequence use-error path in the roadmap. Filing: a new home indication (category C) requires a summative HF report; under-scoping is a 510(k) gap. Commercial: F7 GA can't responsibly cross the pilot→GA gate without this.
- **Resolution proposal:** Gate F7 pilot→GA on (1) a fresh use specification superseding the cleared HCP/supervised spec, (2) ≥2 formative rounds + a summative HF validation on production-equivalent hardware in a simulated home environment, (3) a new URRA covering home-specific hazard classes.
- **Owner / next step:** Human Factors (with Clinical + Risk) — author the F7 use specification before any F7 GA commitment; route the home-indication/filing question to Regulatory.

### F-12: F4 alarm-fatigue reduction can create a new missed-critical-alarm use error (over-suppression)
- **Status:** open
- **Category:** Methodology
- **Severity:** high
- **Effort:** med
- **Author:** agent:human-factors
- **What:** The roadmap frames F4 and its 35–45% alert-reduction claim purely as a benefit and never states the inverse use-error: an over-suppressing or mis-prioritizing filter, plus user trust in it, can cause a clinician to miss an actionable alarm (occlusion, over-sedation). This is a perception/cognitive use-error class under IEC 62366-1 §5.2 and must be analyzed as a critical task, not assumed away.
- **Evidence:** `commercial-strategy.md` D-COMM-1.4 F4, R2; `strategic-market-ai-infusion.md` (35–45%); `user-needs.md` UN-010; `iec-62366-1.md` §5.2.
- **Worked example (before / after):** Before — F4 de-prioritizes a "low-value" alarm class to cut noise; a real occlusion alarm is filtered/delayed; the nurse, conditioned to trust the quieter system, does not respond → over-sedation goes unnoticed. After — F4's URRA names alarm over-suppression (false-negative) as a critical task; the reduction claim is paired with a stated maximum missed-actionable-alarm rate Clinical accepts; the suppression UI is tested for whether users notice what was suppressed.
- **Impact:** Safety: a safety feature that, mis-tuned, suppresses the alarm it was meant to surface. Filing: F4 is PCCP-governed (category B); a UI/alarm change triggers URRA re-evaluation. Commercial: an over-promised reduction claim (R2) ignoring the false-negative path invites complaints.
- **Resolution proposal:** Require F4's risk file to model the over-suppression path with a quantified missed-actionable-alarm acceptance bound; pair every reduction claim with that bound; make "user misses a suppressed actionable alarm" a summative critical task.
- **Owner / next step:** Human Factors + Clinical — add the false-negative critical task to F4's use-related risk analysis; route the acceptable threshold to Clinical/Risk (R2).

### F-13: F8 dose personalization is an unaddressed use-transparency / over-reliance risk
- **Status:** open
- **Category:** Substantiation
- **Severity:** med
- **Effort:** med
- **Author:** agent:human-factors
- **What:** F8 (dose-personalization decision-support) is the roadmap's highest-sentiment opportunity (+0.55) but is treated as a benefit with no use-transparency analysis. If the user cannot see why a personalized dose was recommended or its safe bounds, two opposite cognitive-class use errors appear: over-reliance (accepting an unsafe recommendation without the cross-check that catches it) and under-reliance (ignoring a good one). For an opioid dose this is consequential.
- **Evidence:** `commercial-strategy.md` D-COMM-1.4 F8, D-COMM-1.1 (+0.55); `iec-62366-1.md` §5.2 (cognitive use errors), §5.3 (UI spec acceptance criteria).
- **Worked example (before / after):** Before — F8 surfaces a personalized opioid dose with no visible rationale; a fatigued clinician accepts it because the system is trusted; the recommendation is wrong for this patient and automation-bias removes the human cross-check → over-dose. After — F8's UI spec requires the recommendation's basis + safe bounds be visible and bounded; "user accepts an unsafe personalized dose" and "user ignores a safe one" are both summative critical tasks with pre-stated success criteria.
- **Impact:** Safety: automation bias on an opioid dose is a credible over-/under-dose path. Filing: F8 is category C+PCCP; a decision-support UI is a critical-task surface FDA will expect tested. Commercial: a personalization feature users can't trust (or over-trust) undercuts the +0.55 thesis.
- **Resolution proposal:** Require F8's UI specification to expose recommendation basis + safe bounds; add over-reliance + under-reliance as summative critical tasks; resolve clinician-only vs patient-facing scope before locking the UI bar.
- **Owner / next step:** Human Factors (with Clinical for the trust model) — add the two transparency critical tasks to the F8 UI spec; route the decision-maker-scope question to Clinical/Regulatory.

### F-14: [KOL — Dr. James Paul] Gate every intelligence feature on PCA/opioid-specific evidence + a missed-true-event bound
- **Status:** open
- **Category:** Methodology
- **Severity:** high
- **Effort:** high
- **Author:** agent:paul-james
- **What:** The opioid-safety anchor's headline position: the roadmap markets the upside of every intelligence feature (F4 alarms, F6 prediction, F8 personalization) while footnoting the downside. For a controlled substance whose signature catastrophe is opioid-induced respiratory depression (OIRD), the *missed-true-event rate* is not a footnote — it is the entire clinical question. No intelligence feature should ship without PCA/opioid-specific evidence and a clinician-accepted maximum missed-true-event bound.
- **Evidence:** `kol-KOL-0006-paul-james.md`; `commercial-strategy.md` D-COMM-1.4 (F4/F6/F8), D-COMM-1.1; R1/R2 name the gap but the feature rows still over-claim.
- **Worked example (before / after):** Before — "Predictive monitoring … 15–30 min early warnings" / "Alerts Engine … 45% fewer alerts." After — each ships only with a stated maximum missed-true (OIRD-class) event rate, clinician-accepted, measured in a PCA/opioid cohort. "Owning the alarm is worthless if it's the alarm you suppressed."
- **Impact:** Clinical: a quiet, fast, irreversible harm channel is left unbounded. Filing: an OIRD claim on borrowed data won't clear. Commercial: the predictive wedge can't be marketed until cleared on PCA evidence.
- **Resolution proposal:** Make the missed-true-event bound a first-class acceptance criterion on F4 and F6; gate F6/F7/F8 on PCA/opioid-specific evidence before commit.
- **Owner / next step:** Clinical Affairs + Risk — set the bounds before the Year-2 stage gate. _(Reinforces F-2, F-3.)_

### F-15: [KOL — Dr. Kathleen Giuliano] F4 needs a pre-specified suppressed-true-alarm sensitivity floor, not a count reduction
- **Status:** open
- **Category:** Substantiation
- **Severity:** high
- **Effort:** med
- **Author:** agent:giuliano-kathleen
- **What:** A percentage reduction in alarm *count* is a noise claim, not a safety claim. The determining number — absent from the roadmap — is the suppressed/delayed true-alarm rate. A filter that quiets 45% of alarms while dropping even a fraction of true occlusion/apnea signals makes nurses *more* trusting of a *less* trustworthy alarm: the worst combination. R2 mis-frames this as a marketing risk; it is patient-safety.
- **Evidence:** `kol-KOL-0001-giuliano-kathleen.md`; `commercial-strategy.md` D-COMM-1.4 F4, R2; `strategic-market-ai-infusion.md` (45% figure, general infusion).
- **Worked example (before / after):** Before — "Alerts Engine v1 — alarm-fatigue reduction (45% fewer non-actionable alerts)." After — F4 ships with a pre-specified sensitivity floor (max suppressed/delayed true-alarm rate, with CI) measured on a labeled real-alarm dataset, re-owned under Clinical+Risk+HF as an acceptance criterion.
- **Impact:** Safety: a mis-tuned filter suppresses the alarm it exists to surface. Filing: alarm change touches IEC 60601-1-8. Commercial: a "fewer alarms" program without that number is a recall waiting to happen.
- **Resolution proposal:** Put one defensible number on the roadmap — the maximum acceptable suppressed/delayed true-alarm rate for F4 — with its measurement method, as the gate not the apology.
- **Owner / next step:** Clinical + Risk + Human Factors — define before F4 design inputs lock. _(Reinforces F-3, F-12.)_

### F-16: [KOL — Dr. Parth Shah] Adopt a two-sided alert metric (sensitivity + false-negative, paired) as a hard gate
- **Status:** open
- **Category:** Methodology
- **Severity:** high
- **Effort:** med
- **Author:** agent:shah-parth
- **What:** Every alert-reduction figure in the roadmap is one-sided and borrowed from general infusion (the market doc rates PCA relevance "Medium"). PCA's alarm population — patient-demand events, lockout hits, opioid sedation — has a far higher false-negative consequence than maintenance-fluid occlusion. No reduction claim should ship — internally, to FDA, or in marketing — unless reported as a *pair*: non-actionable-alert reduction *alongside* true-alert sensitivity and measured false-negative rate, on PCA traffic.
- **Evidence:** `kol-KOL-0008-shah-parth.md`; `strategic-market-ai-infusion.md` (45%/80%/35%, PCA relevance "Medium"); `commercial-strategy.md` D-COMM-1.4 F4/F6/F8.
- **Worked example (before / after):** Before — "45% reduction in non-actionable alerts." After — "45% non-actionable-alert reduction *at X% true-alert sensitivity, false-negative rate Y%*, validated on PCA traffic" — the pairing is a deliverable, not an afterthought.
- **Impact:** Safety: a one-sided filter is a "sedation-detection bypass with a friendly dashboard." Filing: borrowed numbers won't substantiate a PCA claim. Commercial: the metric contract protects the claim from field reversal.
- **Resolution proposal:** Write the two-sided metric into the roadmap now as a hard gate for F4, F6, and F8; treat the borrowed percentages as hypotheses to re-derive on PCA data.
- **Owner / next step:** Clinical + Data Science — adopt the paired metric before any alert-reduction commitment. _(Reinforces F-3; pairs with F-15.)_

### F-17: [KOL — Sini Kuitunen] F1 must be a governed hard/soft-limit DERS with a validation gate; F8 must never exceed F1 hard limits
- **Status:** open
- **Category:** Coverage
- **Severity:** high
- **Effort:** med
- **Author:** agent:kuitunen-sini
- **What:** The roadmap treats the drug library as a feature to ship (F1, "200+ meds") rather than a safety-critical dataset to govern. It never names the hard-limit (pump refuses) vs soft-limit (warns, overridable) distinction that *is* the opioid-PCA safety case, states no pre-deployment library-validation gate, and never constrains F8 personalization to stay within F1's hard limits — so a personalization engine could silently recommend above the limit the library exists to enforce.
- **Evidence:** `kol-KOL-0004-kuitunen-sini.md`; `commercial-strategy.md` D-COMM-1.4 F1/F8; `regulatory-strategy.md` §2 (Drug Library Manager = Class II SaMD, "directly mutates the safety table").
- **Worked example (before / after):** Before — "Drug Library Manager GA — pharmacist-authored DERS, 200+ med library." After — "governed DERS: documented hard/soft-limit data model + pharmacist sign-off + a pre-deployment validation gate (stated threshold) + version control; F8 architecturally cannot recommend outside F1 hard limits."
- **Impact:** Safety: the hard upper limit on cumulative dose/lockout/concentration is the whole opioid case. Filing: EU MDR Notified Bodies scrutinize library-validation harder than FDA — start EU evidence in Y1–Y2, not Y5. Commercial: F1 becomes the most defensible safety claim instead of a checklist.
- **Resolution proposal:** Rewrite F1 as a governed validated hard/soft-limit DERS with a sign-off gate; make F8 provably subordinate to F1 hard limits; log overrides and feed them back into library tuning.
- **Owner / next step:** Pharmacy/Clinical + Regulatory — author the F1 governance + validation gate before GA. _(New issue — not in F-1…F-13.)_

### F-18: [KOL — Dr. Evan Kirkendall] Pediatric population scope is undefined; effect sizes need population-stratified sensitivity/specificity
- **Status:** open
- **Category:** Coverage
- **Severity:** high
- **Effort:** low
- **Author:** agent:kirkendall-evan
- **What:** The roadmap names 8 KOLs, 3 care-setting expansions, and 9 features, with not one word on pediatric/neonatal weight-based dosing, concentration limits, or PCA-by-proxy. Listing a pediatric hospitalist as a KOL anchor implies pediatric credibility the design hasn't established. A single averaged "35% alert reduction" can *increase* clinically meaningful false-negatives in a neonate. Scope must be decided explicitly — "out for now" is fine; silent ambiguity is not.
- **Evidence:** `kol-KOL-0002-kirkendall-evan.md`; `commercial-strategy.md` D-COMM-1.2 (segments), D-COMM-1.4 (F4/F5/F8 anchor Kirkendall).
- **Worked example (before / after):** Before — roadmap silent on pediatrics; Kirkendall listed as F4/F5 anchor. After — an explicit "pediatric population: in / out of scope for v1" line; if in, every alarm/CDS claim carries population-stratified sensitivity/specificity and weight-banded guardrails.
- **Impact:** Safety: pediatric PCA is higher-consequence and error-amplifying. Filing: silent scope becomes a labeling + post-market problem. Commercial: claiming pediatric anchors without pediatric design is a credibility risk.
- **Resolution proposal:** Make a written pediatric in/out decision now; stratify all effect-size claims by population; gate F8 dose personalization on that decision.
- **Owner / next step:** Clinical + Regulatory — record the scope decision before F4/F8 design inputs. _(New issue — not in F-1…F-13.)_

### F-19: [KOL — Dr. Priyadarshini Pennathur] F7 needs a new IEC 62366-1 use specification + lay-user summative; F8 needs use-transparency
- **Status:** open
- **Category:** Coverage
- **Severity:** high
- **Effort:** high
- **Author:** agent:pennathur-priyadarshini
- **What:** The human-factors KOL's work-system read: F7 is not a feature increment but a wholesale substitution of the operator (trained nurse → patient/family caregiver), environment (ward → home, no backstop), and tasks — all three IEC 62366-1 use-specification axes at once. The cleared validation cannot be inherited. F8 separately engineers automation bias: a clinician shifts from decision-maker to decision-checker and under-scrutinizes trusted automation.
- **Evidence:** `kol-KOL-0005-pennathur-priyadarshini.md`; `user-needs.md` (cleared "trained HCP / supervised"; CAPA-2023-001); `commercial-strategy.md` D-COMM-1.4 F7/F8, R3; `iec-62366-1.md` §5.1–5.6.
- **Worked example (before / after):** Before — F7 sequenced as "hardware pilot → GA." After — write the F7 use specification *first* (it tells you what hardware/alarms/labeling the home version needs); test worst-case scenarios (PCA-by-proxy, missed alarm with no nurse, priming errors); summative validation with patients + family caregivers. F8 gets use-transparency + a confirmation friction point, validated for error-catching not just task success.
- **Impact:** Safety: the home work system co-designs every error. Filing: a new home indication requires a summative HF report; F8 decision-support is a critical-task surface. Commercial: F7 cannot responsibly cross pilot→GA without this.
- **Resolution proposal:** Treat F7 as a new device for usability; start home-use formative research now, not at design transfer; build F8 transparency in.
- **Owner / next step:** Human Factors + Clinical — author the F7 use spec before any GA commit. _(Reinforces F-11, F-13 from the HF-KOL vantage.)_

### F-20: [KOL — Lisa Gorski] Connected/home features lack a named nurse/caregiver workflow + INS-standards conformance
- **Status:** open
- **Category:** Coverage
- **Severity:** high
- **Effort:** med
- **Author:** agent:gorski-lisa
- **What:** The infusion-nursing-standards KOL: the roadmap treats connectivity as a data problem and forgets it is a workflow problem. INS Standards require automated programming to *reduce, not relocate*, the nurse's verification burden. F2 auto-programming doesn't say where the nurse's independent high-alert double-check happens; F1/F3 library updates have no mid-infusion change-management (risk of silently re-bounding an in-progress infusion); and F7 "home PCA" has no defined competency-verified operator and conflates nurse-managed ambulatory care with lay self-administration.
- **Evidence:** `kol-KOL-0007-gorski-lisa.md`; `commercial-strategy.md` D-COMM-1.4 F2/F3/F7, D-COMM-1.2; INS Infusion Therapy Standards of Practice (home-infusion competencies).
- **Worked example (before / after):** Before — "Connectivity Adapter GA — HL7/FHIR" and "home/ambulatory PCA." After — F2 specifies where the bedside independent double-check of a high-alert opioid occurs; F1/F3 specify what a nurse sees when a library version changes mid-infusion; F7 names the responsible competency-verified operator (typically a home-infusion nurse) and conforms to INS home-infusion standards.
- **Impact:** Safety: relocating verification silently creates automation complacency. Filing: a clean 510(k) over an unsafe workflow still injures patients. Commercial: nursing/pharmacy buyers (segment 2) will reject features that ignore their standards.
- **Resolution proposal:** For every connected/home feature, write the nurse/caregiver workflow + INS-standards conformance as an input *before* the regulatory category; name the user, the verification step, the competency.
- **Owner / next step:** Clinical/Nursing + Human Factors — add workflow-conformance inputs to F2/F3/F7. _(New issue — not in F-1…F-13.)_

### F-21: [KOL — Dr. Susan Braithwaite] Insulin-pump precedent transfers form-factor only, not risk tolerance; F8 needs a respiratory-safety biomarker
- **Status:** open
- **Category:** Substantiation
- **Severity:** high
- **Effort:** med
- **Author:** agent:braithwaite-susan
- **What:** The ambulatory-infusion KOL's warning about the roadmap's own analogy: borrowing the insulin patch-pump *form factor* (D-COMM-1.8) and connectivity is sound, but importing its *risk tolerance* is dangerous. Insulin over-delivery is slow, signposted, and has a fast cheap antidote; opioid over-delivery is minutes-to-apnea, silent, and far less forgiving. And insulin personalization works because it optimizes toward a continuously-sensed biomarker (glucose) — opioid analgesia has no equivalent objective continuous safety signal, so F8 as framed optimizes reported analgesia (efficacy) while the safety variable (respiratory drive) is unmonitored.
- **Evidence:** `kol-KOL-0003-braithwaite-susan.md`; `commercial-strategy.md` D-COMM-1.4 F7/F8, D-COMM-1.8 (Omnipod/Tandem benchmark), D-COMM-1.3 (Y5 closed-loop research).
- **Worked example (before / after):** Before — F7 benchmarked to Omnipod 72-hr; F8 "dose personalization (+0.55 sentiment)." After — a one-line non-analogy clause beside D-COMM-1.8/F8: "insulin precedent informs hardware + connectivity only; opioid respiratory-depression risk requires an independent, more conservative safety case with a continuous respiratory-safety signal (e.g., capnography/SpO₂)"; F8 requires that biomarker in the loop before personalizing dose.
- **Impact:** Safety: an insulin-grade occlusion/fault spec is not opioid-safe; personalization without a safety biomarker optimizes the wrong axis. Filing: the Y5 closed-loop-assist track must inherit insulin's decade of humility *and add margin*. Commercial: the +0.55 personalization opportunity rests on a safety substrate that doesn't yet exist.
- **Resolution proposal:** Add the non-analogy clause; make a continuous respiratory-safety signal a gating assumption for F7 home use and F8 personalization, not an accessory.
- **Owner / next step:** Clinical + Systems Engineering — define the required safety biomarker before F7/F8 commit. _(Reinforces F-4; sharpens F-13.)_

## Convergence (findings reached independently by ≥2 advisors)

The highest-confidence calls — where multiple voices (discipline advisors *and* KOL persona agents) converged on the same root cause from different evidence bases. The KOL panel turned two 3-agent calls into 6–7-voice calls:

- **C1 — F7 home opioid PCA is the roadmap's biggest unmanaged leap (7 voices).** Advisors: clinical (F-4) + human-factors (F-11) + regulatory (F-6, De Novo). KOLs: Paul (delete the responder, insulin-patch benchmark ≠ safety evidence), Pennathur (F-19, three use-spec axes change at once), Gorski (F-20, no defined competency-verified operator), Braithwaite (F-21, opioid failure mode ≠ insulin). When the opioid-safety, human-factors, nursing-standards, and ambulatory-infusion KOLs *and* three disciplines all land here, F7 cannot cross pilot→GA as written.
- **C2 — F6 predictive monitoring / one-sided alarm claims are committed on a foundation that isn't there (7 voices).** Advisors: clinical (F-2) + regulatory (F-5/F-6) + program (F-10). KOLs: Paul (F-14, missed-true bound), Giuliano (F-15, sensitivity floor), Shah (F-16, two-sided metric), Kirkendall (F-18, population-stratified). Every alarm/alert KOL independently demanded the *false-negative half* of the claim that the roadmap omits. The flagship intelligence features are the least de-risked.
- **C3 — New issues only the KOL panel surfaced.** Four findings the discipline advisors missed: DERS hard/soft-limit governance + validation gate (F-17, Kuitunen), pediatric scope decision (F-18, Kirkendall), INS nursing-workflow standards (F-20, Gorski), and the insulin-analogy risk-tolerance trap + missing respiratory biomarker (F-21, Braithwaite). This is the value of running the actual KOL personas, not just a consolidated clinical voice.
- **C4 — The roadmap's floor isn't poured yet (foundation cluster: uncontacted KOLs F-1, unwritten PCCP F-5, unresourced keystone tasks F-9).** And note the meta-point: the KOL opinions in this very analysis are *simulated* (per F-1) — in a real program they'd be replaced by the actual interviews F-1 calls for.

## Recommendations

1. **Re-cut D-COMM-1.4's regulatory-category + KOL-anchor columns** before any Year-1 commit: split initial-clearance from PCCP-retraining; mark F6/F7/F8 pathways "TBD pending Q-Sub"; relabel KOL anchors as "specialty match — opinion pending."
2. **Author the PCCP** (`pccp-predetermined-change-control-plan.md`) with its three required sections, then run the **Ct* tagging pass (ben/011)** so the PCCP envelope is defined structurally — these are the keystone that makes every "B" feature real.
3. **Gate F7 and F6 on evidence + validation plans** (PCA/opioid clinical-evidence plan for F6; fresh use-specification + summative HF validation + home-specific URRA for F7) — do not let them cross their pilot/launch gates without those deliverables.
4. **Build a dependency register** promoting ben/011 + ben/049 to owned, scheduled, resourced items; re-label Y1 GA dates as commercial-readiness vs binding clearance gates; de-serialize the gate model with parallel pre-work.
5. **Carry the open regulatory questions into the M12 Q-Sub** (F6 predicate-vs-De-Novo; F7 product-code + home indication; one-PCCP-spanning-two-SaMDs); populate regulatory-strategy §3/§4 before firming the Y5 international wave.
6. **Add the missing safety half** to F4 (bounded missed-true-alarm rate) and F8 (use-transparency critical tasks).

## Cross-discipline open questions

Rolled up across all four advisor files; owning discipline preserved.

| # | Question | Owning discipline | Raised by |
|---|---|---|---|
| 1 | What OIRD detection sensitivity / false-negative rate is the acceptance threshold for F6? | Risk Management | clinical, regulatory |
| 2 | Does F6 become on-device module M8 or feed M2 via M6, and what PCCP envelope covers retraining? | Architecture + Regulatory | clinical |
| 3 | Is unsupervised home opioid PCA (F7) a use-safety profile a 510(k) can support, or does residual risk push De Novo? | Regulatory + Human Factors + Clinical + Risk | regulatory, HF, clinical |
| 4 | What clinical monitoring fallback (remote clinician, respiratory monitoring) is assumed for the home patient with no on-site responder? | Clinical + Risk | human-factors |
| 5 | Does the F4 alarm-suppression algorithm have a quantified missed-actionable-alarm bound Clinical will accept? | Clinical + Risk | clinical, human-factors |
| 6 | Does dose-personalization (F8) recommend/adjust dosing such that it exits the CDS non-device carve-out, and is it clinician- or patient-facing? | Clinical + Regulatory | regulatory, human-factors |
| 7 | Can one PCCP span two independent SaMDs (Alerts Engine + Clinical Interface)? | Architecture + Regulatory | regulatory |
| 8 | Is ben/011 + ben/049 staffing available, or does it contend with the 30+ in-flight tasks? | Program + Engineering | program |
| 9 | Can the cost-avoidance reimbursement case (R5) be substantiated with PCA-specific adverse-event-reduction data? | Health-Economics | clinical |
| 10 | Are tamper-evidence/diversion controls (UN-020, hospital-scoped) sufficient when the authorized cardholder may be the home misuse actor? | Risk + Regulatory + Human Factors | human-factors |

## Self-review checklist

- [x] **Findings anchored to declared methodology** — each F-N cites the discipline bar it tests against.
- [x] **Every artifact-path claim grepped** — KOL "not yet contacted", PCCP v0.1 stub, regulatory-strategy §3/§4 empty, ben/011 Not Started all verified at write time.
- [x] **Standard / guidance citations checked** — IEC 62366-1 §5.1–5.6; PCCP AI/ML (intra-intended-use); sw-changes Flowchart A1; Q-Sub = feedback.
- [x] **"Missing X" claims cross-checked** against the actual source (roadmap, regulatory-strategy, user-needs, PCCP stub).
- [x] **Internal consistency** — summary table, per-finding blocks, and convergence section agree on multi-agent flags.
- [x] **Worked example present under every F-N.**
- [x] **Cross-discipline open questions present** (rolled up across all four advisors).
- [x] **Author attribution** — every F-N carries `**Author:** agent:<name>` so the console maps findings to advisors.

## Open Questions

- Several findings (F-2, F-4, F-6, F-11) hinge on FDA feedback (predicate-vs-De-Novo for F6/F7; whether home opioid PCA is 510(k)-supportable). Those are genuinely Q-Sub questions — the local grounding can frame them but not resolve them.
- The market figures (revenue/IRR/NPV) are demo input-analysis estimates already flagged `[VERIFY]` in D-COMM-1.7; this analysis critiques the roadmap's *use* of them, not their underlying truth.

## References

- **Internal artifacts:** `commercial-strategy.md` (D-COMM-1.1…1.9); `regulatory-strategy.md` (§1 carve-out, §2 classifications, §3/§4 empty); `user-needs.md` (cleared bright line; UN-003/004/007/010/020; CAPA-2023-001); `pccp-predetermined-change-control-plan.md` (v0.1 stub); `pca-device-system-sad.md` (§4/§5/§8); `submissions/510k/composition-manifest.md` (K210345, predicate PP3000 K190567).
- **KOL roster:** `kol-feedback/KOL-0001…0008` (8 profiles, all "not yet contacted").
- **Market/competitive:** `competitive-product-assessment.md`; `strategic-market-ai-infusion.md`.
- **Standards / guidance:** IEC 62366-1 §5.1–5.6 (L1a `.claude/skills/medtech-docs/references/standards/iec-62366-1.md` + L1b `docs/external/standards/iec-62366-1.md`); FDA PCCP AI/ML, sw-changes (Flowchart A1), Q-Sub (`docs/external/fda-guidance/`).

## Changelog

| Date | Author | Summary |
|------|--------|---------|
| 2026-06-03 | human:Ben Xavier (task ben/080) | Scaffolded analysis; conducted 4-advisor fan-out; merged 13 findings + convergence + open-questions roll-up into this aggregate. |
| 2026-06-03 | agent:clinical-affairs | Clinical/KOL review: uncontacted KOLs (F-1) and PCA-borrowed evidence for F4/F6/F7; 4 findings, 3 blocking. |
| 2026-06-03 | agent:regulatory-affairs | Regulatory review: PCCP envelope unwritten + overclaimed (F-5); F6/F7/F8 under-categorized, De Novo risk (F-6); international wave depends on empty strategy sections (F-7). |
| 2026-06-03 | agent:program-manager | Executability review: Year-1 over-stuffing (F-8), unresourced keystone deps (F-9), serialized-gate + 42-month/Y3 timeline collision (F-10). |
| 2026-06-03 | agent:human-factors | Use-safety review: F7 home-PCA use-spec + summative HF validation gap (F-11), F4 alarm-suppression missed-critical-alarm use error (F-12), F8 dose-transparency risk (F-13). |
| 2026-06-04 | agent:paul-james | KOL (PCA/opioid): Endorse with reservations — gate every intelligence feature on PCA/opioid evidence + a clinician-accepted missed-true-event bound (F-14). |
| 2026-06-04 | agent:giuliano-kathleen | KOL (alarm fatigue): Conditional — F4 must carry a pre-specified suppressed-true-alarm sensitivity floor, not a count reduction (F-15). |
| 2026-06-04 | agent:shah-parth | KOL (alert optimization): Conditional — adopt a two-sided alert metric (sensitivity + false-negative, paired) as a hard gate for F4/F6/F8 (F-16). |
| 2026-06-04 | agent:kuitunen-sini | KOL (DERS): Conditional — F1 must be a governed hard/soft-limit DERS with a validation gate; F8 must never exceed F1 hard limits (F-17). |
| 2026-06-04 | agent:kirkendall-evan | KOL (pediatrics/CDS): Qualified yes — decide pediatric scope in/out; effect sizes need population-stratified sensitivity/specificity (F-18). |
| 2026-06-04 | agent:pennathur-priyadarshini | KOL (human factors): Conditional — F7 needs a new IEC 62366-1 use spec + lay-user summative; F8 needs use-transparency (F-19). |
| 2026-06-04 | agent:gorski-lisa | KOL (infusion nursing): Conditional yes — connected/home features need a named nurse/caregiver workflow + INS-standards conformance (F-20). |
| 2026-06-04 | agent:braithwaite-susan | KOL (insulin analogy): Mixed — borrow insulin-pump form factor only, not risk tolerance; F8 needs an objective respiratory-safety biomarker (F-21). |
| 2026-06-04 | human:Ben Xavier (task ben/080) | Added the 8-member KOL persona-agent panel alongside the discipline advisors per user clarification; captured each full opinion as a `kol-*.md` doc; added findings F-14…F-21; re-rendered sidecars. |
