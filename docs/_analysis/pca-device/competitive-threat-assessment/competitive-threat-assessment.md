---
id: competitive-threat-assessment
title: "Competitive Threat Assessment — PP3500 / Infusion Portfolio"
status: draft
component: pca-device
topic: competitive
created: 2026-08-05
last_updated: 2026-08-06
authored_by:
  - human:Ben Xavier
  - agent:commercial
  - agent:regulatory-affairs
  - agent:clinical-affairs
  - agent:risk-management
  - agent:cybersecurity
grounded_against:
  - research: docs/_analysis/pca-device/competitive-threat-assessment/research-market-data.md  # independent market sizing; 20 project claims put under test
  - research: docs/_analysis/pca-device/competitive-threat-assessment/research-competitor-regulatory-record.md  # 76 graded claims from FDA/SEC primary records
  - research: docs/_analysis/pca-device/competitive-threat-assessment/research-ai-connectivity-regulatory.md  # FDA AI list, interoperability adoption, PCCP + 524B pathway reality
  - research: docs/_analysis/pca-device/competitive-threat-assessment/research-pca-clinical-landscape.md  # ERAS displacement, OIRD monitoring expectations, clinical claims under test
  - strategy: docs/project/strategies/commercial-strategy.md  # subject under review — D-COMM-1.1 thesis, 1.8 positioning, 1.9 risk register
  - strategy: docs/project/strategies/regulatory-strategy.md  # pathway + PCCP envelope
  - market: docs/project/input-analysis/competitive-landscape/competitive-product-assessment.md  # subject under review
  - market: docs/project/input-analysis/competitive-landscape/state-of-the-art-analysis.md  # subject under review
  - market: docs/project/input-analysis/market-research/strategic-market-ai-infusion.md  # subject under review
  - kol: docs/project/input-analysis/kol-feedback/  # 8 profiles, all "Not yet contacted"
recommended_agents:
  - commercial
  - regulatory-affairs
  - clinical-affairs
  - risk-management
  - cybersecurity
superseded_by: null
---

# Competitive Threat Assessment — PP3500 / Infusion Portfolio

> _Demo sample data — not for clinical use._
>
> **Read the grade tokens.** The GlobalLogic devices are demo fabrications; the competitors are real companies with real public records. Every claim below carries an explicit evidence grade so the two can never be confused. See [README.md](README.md) for the full contract.

## Goal of this analysis

The user asked for a gap analysis of **competitor threats against our products**, with well-researched substantiated data — and with anything that is merely opinion or unsubstantiated labelled as such, with reasoning. This analysis is that assessment, run as **two agent layers**: four **research agents** built a public-source evidence base first (FDA clearance/recall/enforcement records, independent market sizing, the AI/interoperability/pathway reality, and the PCA clinical-utilization literature), and five **discipline advisors** then reasoned *against that evidence base* rather than from memory.

- **Motivating question:** Where is the portfolio actually exposed to competitors — and how much of our own competitive case would survive contact with a customer's value-analysis committee, an FDA reviewer, or a diligence reader?
- **Decision the analysis informs:** Whether the 5-year commercial and regulatory plan can proceed on its current competitive premises, or must be re-founded before the next commit gate.
- **Stakeholders:** Commercial lead, Regulatory Affairs, Clinical Affairs, Risk Management, Quality Engineering, Program Management.

## Expected methodology

_Declaring the standard up front, so that "missing X" findings are anchored rather than unanchored opinion._

A competitive threat assessment for a regulated device program is expected to draw on the **union** of five techniques. This analysis was built to cover all five; where coverage is partial, it is stated.

| Technique | What it surfaces | Anchor | Covered here by |
|---|---|---|---|
| **Structured competitor intelligence** | Who competes, on what, with what regulatory standing | Porter five-forces; FDA public records | `research-competitor-regulatory-record.md` (76 graded claims from openFDA / SEC / FDA enforcement) |
| **Independent market sizing + claim audit** | Whether the program's own market premises hold | CAGR arithmetic; multi-vendor triangulation | `research-market-data.md` (20 verdict entries) |
| **Technology / state-of-the-art scan** | Whether the claimed capability gap is real | FDA AI-Enabled Device List; peer-reviewed literature | `research-ai-connectivity-regulatory.md` |
| **Demand-side / clinical-practice analysis** | Whether the *use case* is stable | Clinical guidelines (ERAS), utilization literature, harm literature | `research-pca-clinical-landscape.md` |
| **Risk analysis with controls** | What could invalidate the plan, and what we would do | ISO 14971 discipline applied to business risk | `recs-risk-management.md` |

**What is deliberately out of scope.** This is *business and program* risk, not ISO 14971 patient-harm risk. No hazard analysis is produced here. Where a competitive threat **couples** to the ISO 14971 file, that coupling is called out explicitly rather than resolved here.

### The evidence-grade model

The analysis mixes two kinds of subject matter and grades them differently. This is the methodological core of the whole document.

| Grade | Meaning | Can it support an external claim? |
|---|---|---|
| `SUBSTANTIATED` | Citable public/primary source; URL + date recorded | **Yes** |
| `ARITHMETIC` | Verifiable by computation from figures in the project's own documents | **Yes** — reproducible without any external source |
| `INTERNAL-DEMO` | Stated only in this repo; fabricated demo content | **No — never.** Externally unverifiable by construction |
| `INFERRED` | Reasoned from substantiated facts; reasoning chain stated so a reader can reject it | **Qualified** — only with the chain shown |
| `OPINION` | Advisor judgment, no source; why no source exists is stated | **No** — labelled as judgment |
| `UNVERIFIED` | Claimed somewhere, not confirmable; what would close it is recorded | **No** — pending closure |

**Why per-claim grading rather than one demo banner.** A single "demo sample data" banner at the top of a file tells a reader that *the device* is fictional. It does not tell them that a *market figure* was pasted from a real vendor report into a slot it does not describe, or that a *clinical claim* is real-world-sourced but methodologically malformed. Those are different defects with different fixes, and only per-claim grading separates them.

## Source being analyzed

### Primary sources (subject under review)

- `docs/project/strategies/commercial-strategy.md` — decisions D-COMM-1.1 through D-COMM-1.9
- `docs/project/input-analysis/competitive-landscape/competitive-product-assessment.md`
- `docs/project/input-analysis/competitive-landscape/state-of-the-art-analysis.md`
- `docs/project/input-analysis/market-research/strategic-market-ai-infusion.md`
- `docs/project/strategies/regulatory-strategy.md`

### Evidence base built for this analysis

- [`research-market-data.md`](research-market-data.md) — independent market picture; 20 verdict entries on the project's own claims
- [`research-competitor-regulatory-record.md`](research-competitor-regulatory-record.md) — 76 graded claims (66 `SUBSTANTIATED`) from FDA and SEC primary records
- [`research-ai-connectivity-regulatory.md`](research-ai-connectivity-regulatory.md) — FDA AI-Enabled Device List parse, interoperability adoption, PCCP and §524B pathway analysis
- [`research-pca-clinical-landscape.md`](research-pca-clinical-landscape.md) — ERAS displacement evidence, OIRD monitoring expectations, project clinical claims under test

### Advisor prescriptions

- [`recs-commercial.md`](recs-commercial.md) · [`recs-regulatory-affairs.md`](recs-regulatory-affairs.md) · [`recs-clinical-affairs.md`](recs-clinical-affairs.md) · [`recs-risk-management.md`](recs-risk-management.md) · [`recs-cybersecurity.md`](recs-cybersecurity.md)

## Assertions

_Falsifiable claims about the project artifacts, stated so the analysis can confirm or refute them with evidence rather than assert conclusions._

| # | Assertion | Clause / decision | Evidence (path) | Status |
|---|---|---|---|---|
| A1 | The strategy's premise that market leaders are "reactive-alarm only" is supported by the project's own competitive inputs. | D-COMM-1.1 | `state-of-the-art-analysis.md` L39, L52 — Alaris PCA Module ships PCA Pause + EtCO₂ | refuted |
| A2 | Competitors have cleared AI/predictive monitoring capability that PP3500 lacks. | D-COMM-1.1 | `research-ai-connectivity-regulatory.md` §A.1 — 0 of 1,524 FDA-listed AI devices is an infusion pump | refuted |
| A3 | Every market-growth figure in the input analyses is internally consistent with its own start and end values. | D-COMM-1.1, 1.7 | `research-market-data.md` rows 1–11; independently recomputed | refuted |
| A4 | The three input-analysis documents agree with each other on the markets they both size. | — | `research-market-data.md` rows 5c, 10 — 2023 global market stated 10.8× apart | refuted |
| A5 | The battery-life comparison compares like device categories under stated test conditions. | D-COMM-1.1 | `research-pca-clinical-landscape.md` §C.1 | refuted |
| A6 | The volumetric-accuracy claim is stated consistently across the project's documents. | D-COMM-1.1 | `competitive-product-assessment.md` L14; `state-of-the-art-analysis.md` L24, L62; `strategic-market-ai-infusion.md` L57 | refuted |
| A7 | The AI performance claims ("80% error reduction", "45% alert reduction", "60% adverse-event reduction") trace to identifiable supporting sources. | D-COMM-1.1, 1.5 | `research-ai-connectivity-regulatory.md` — traced to a non-AI 2011 study, an uncited blog post, and nothing | refuted |
| A8 | The risk register includes at least one competitor-originated or demand-side risk. | D-COMM-1.9 | `commercial-strategy.md` L142–L156 — R1–R5 all endogenous | refuted |
| A9 | The ambulatory extension is benchmarked against the incumbent it would meet in procurement. | D-COMM-1.8 | `recs-commercial.md` §5 — benchmarked against Insulet Omnipod, not ICU Medical CADD | refuted |
| A10 | The roadmap's PCCP-authorized features remain inside the statutory intended-use limit and FDA's pre-specification requirement. | D-COMM-1.4 | `research-ai-connectivity-regulatory.md` §C.3–C.4 — FD&C §515C; Appendix B Modification Scenario 2 | refuted |
| A11 | The roadmap's annual regulatory cadence is consistent with observed 510(k) decision times. | D-COMM-1.3 | `research-ai-connectivity-regulatory.md` §C — median 142 days; 34.6% exceed six months | refuted |
| A12 | The PCA segment grows at or above the infusion-pump category rate, as the input analyses imply. | D-COMM-1.1 | `research-market-data.md` § *Sub-segments* — PCA 5.51% vs category 6.5–8.5% | refuted |
| A13 | The project cites an FDA-recognized particular safety standard for infusion pumps. | regulatory strategy | `research-ai-connectivity-regulatory.md` §B.8 — IEC 60601-2-24 not FDA-recognized; ANSI/AAMI ID26 withdrawn | refuted |
| A14 | The KOL sentiment figures anchoring the positioning rest on recorded KOL opinions. | D-COMM-1.1, 1.2 | `docs/project/input-analysis/kol-feedback/` — all 8 profiles "Not yet contacted" | refuted |
| A15 | The quality-posture wedge is supported by DHF evidence the project currently holds. | D-COMM-1.1 | `pdlc-demo-dhf-discovery.json` — risk, hazard, FMEA, clinical-eval, cyber roles resolve to `null` | refuted |
| A16 | The KLAS award claim for ICU Medical Plum 360 is accurate. | competitive inputs | `research-market-data.md` row 9 — verified against ICU Medical and KLAS | confirmed |
| A17 | The smart-pump software market figure ($1.21B → $1.82B @ 7.04%) is accurate. | competitive inputs | `research-market-data.md` row 4 — matches Mordor exactly; mislabelled "smart pump market" in one doc | partial |
| A18 | The refurbished Baxter Sigma Spectrum price band is accurate as a refurbished price. | competitive inputs | `research-market-data.md` row 8a — live listings at $997–$1,097 | confirmed |
| A19 | The device record carries the FDA product code for a PCA pump. | device record | `DEV-PP3500_regulatory_info.md` L22 says **LZH**; openFDA returns LZH = "Pump, Infusion, **Enteral**"; MEA is the PCA code | refuted |
| A20 | The cybersecurity artifacts the submission manifests cite as evidence exist as content. | qsub + 510(k) manifests | Threat model and SBOM resolve `exists: true` to unfilled `{{placeholder}}` templates across all ten DHFs | refuted |
| A21 | The project's clinical evaluation file addresses the hazards the PCA literature names. | `clinical/**` | Zero of 17 files mention proxy, respiratory depression, capnography, EtCO₂, naloxone or sedation — conductor-verified grep | refuted |
| A22 | The project's cybersecurity reference stack cites the guidance edition currently in force. | L1a + L1b refs | Both carry September 27, 2023; the operative edition is February 3, 2026 — two supersessions later | refuted |

**Reading the table.** Nineteen refuted, two confirmed, one partial. That ratio is itself the headline finding: the competitive case is not marginally overstated — it is built on premises that do not survive checking. Note what the two confirmed rows have in common: both are **facts about competitors**, taken from published sources. Every refuted row is either a claim about **us**, a **market figure** sourced without provenance, or an **artifact the project's own indexes report as present when it is not**.

## Assertion positions

### A1
- negative — commercial: the project's own input analysis records Alaris PCA Pause + EtCO₂ two documents away from the strategy that denies it
- negative — clinical-affairs: BD markets the closed loop as the feature; the auto-pause behaviour is what has field evidence

### A2
- negative — regulatory-affairs: absence verified three independent ways across the full 1,524-row list
- neutral — commercial: the absence cuts both ways — it refutes "we are behind" but also means the category is unproven

### A8
- negative — commercial: all five risks are execution risks about things GlobalLogic controls
- negative — risk-management: a register with no exogenous risk is a project plan, not a risk register

### A12
- negative — commercial: PCA underperforms its own category by ~2 points
- neutral — clinical-affairs: narrowing, not collapse — and the guideline-to-ward-practice lag means the threat times later than the guidelines suggest

### A15
- negative — commercial: the wedge with the strongest evidence is the area where our own DHF is emptiest
- negative — cybersecurity: `cybersecurity_plan` resolves to `null` while the roadmap adds a large connected surface

## Findings

**Coverage scope.** F-1…F-22 assess the project's **competitive premises and claims** as recorded in the commercial strategy and the three input-analysis documents, against the four-file public-source evidence base. Not in scope: the DHF's design-control content, the ISO 14971 risk file itself, and the V&V evidence — those have their own analyses. Items outside scope appear in Recommendations, not Findings.

### Summary table

| # | Status | Short label | Artifact(s) affected | Category | Severity | Effort | Blocks commit gate? | Multi-agent | Depends on |
|---|---|---|---|---|---|---|---|---|---|
| F-1 | open | Positioning thesis rests on a premise our own input analysis contradicts | commercial-strategy D-COMM-1.1 | Substantiation | high | med | YES | **3-agent** (COMM + CLIN + REG) | BD labeling retrieval |
| F-2 | open | Risk register contains no competitor-threat category — R1–R5 all endogenous | commercial-strategy D-COMM-1.9 | Coverage | high | low | YES | 2-agent (COMM + RISK) | — |
| F-3 | open | Comparative claims are scope-unlabelled and contradict the documents' own data | all three input analyses | Methodology | high | med | YES | 2-agent (COMM + CLIN) | source-PDF retrieval |
| F-4 | open | Ambulatory extension benchmarks a device it will never meet on an RFP | commercial-strategy D-COMM-1.8 | Methodology | med | low | no | 2-agent (COMM + REG) | MEA predicate sweep |
| F-5 | open | Launch sequencing and reimbursement posture ignore how placements are bought | commercial-strategy D-COMM-1.3, 1.5, 1.7 | Coverage | high | high | no | no | CY2027 HH PPS rule text |
| F-6 | open | PCA structural narrowing unmodelled in segmentation and geography | commercial-strategy D-COMM-1.2, 1.6 | Coverage | med | med | no | 2-agent (COMM + CLIN) | — |
| F-7 | open | PCCP envelope over-claimed — F4/F5 categorised B cannot ride a PCCP | commercial-strategy D-COMM-1.3, 1.4 | Drift | high | med | YES | 2-agent (REG + RISK) | PCCP scope decision |
| F-8 | open | No predicate for a predictive PCA function, and De Novo never evaluated | regulatory-strategy §9; qsub questions | Coverage | high | med | no | 2-agent (REG + RISK) | Q-Sub cycle |
| F-9 | open | Standards matrix anchors on a non-recognized standard and omits every recognized one | SAD §3/§5/§7; design-inputs; SRS | Substantiation | high | **low** | no | 2-agent (REG + RISK) | — |
| F-10 | open | No filing-trigger rule for recall remedies — the ICU Medical failure mode is unguarded | change-control SOP; PCCP protocol | Methodology | high | high | no | 2-agent (REG + RISK) | F-15 (risk file) |
| F-11 | open | Product code on file is LZH ("Pump, Infusion, Enteral") for a PCA pump | DEV-PP3500_regulatory_info.md; qsub Q1.3 | Substantiation | high | **low** | no | no | — |
| F-12 | open | Cybersecurity submission evidence is unfilled templates across all ten DHFs, while three manifests assert it exists | 10 DHF cybersecurity trees; both manifests | Coverage | high | high | YES | 2-agent (CYBER + RISK) | — |
| F-13 | open | Both tiers of the cybersecurity reference stack are two supersessions stale | L1a + L1b guidance refs; iec-81001-5-1.md | Substantiation | high | **low** | no | 2-agent (CYBER + REG) | — |
| F-14 | open | Year-1 connected roadmap expands the attack surface across an unresolved trust boundary | architecture-strategy open items; Adapter SAD | Methodology | high | med | no | 2-agent (CYBER + RISK) | F-12 |
| F-15 | open | D-COMM-1.9 is a risk list, not a risk register — no controls on any of R1–R5 | commercial-strategy D-COMM-1.9 | Methodology | high | med | YES | 2-agent (RISK + COMM) | — |
| F-16 | open | The ICU Medical unfiled-remedy precedent implies a change-control gate the program cannot currently build | change control; the null risk file | Coverage | high | high | no | 2-agent (RISK + REG) | risk-file authoring |
| F-17 | open | PCCP detection→prediction constraint forecloses the D-COMM-1.1 wedge unless pre-specified at baseline | PCCP section; predictive hazard control | Probe-preempt | high | med | YES | 2-agent (RISK + REG) | F-7 |
| F-18 | open | Cloud/AI on an opioid delivery device expands the hazard set well beyond what the SAD names | SAD §5; the null hazard analysis | Coverage | high | high | no | 2-agent (RISK + CYBER) | risk-file authoring |
| F-19 | open | Clinical evaluation file is script-generated shape with none of the device's named hazards | dhfs/pca-device/clinical/** | Substantiation | high | high | no | no | — |
| F-20 | open | PP3500 has no replacement interlock — intended use delegates it to staff vigilance the literature says fails | user-needs.md; D-COMM-1.1 | Coverage | high | high | no | 2-agent (CLIN + RISK) | F-1 |
| F-21 | open | Two clinical claims must be struck outright; four more cannot be used comparatively as written | all three input analyses; D-COMM-1.5 | Substantiation | high | med | YES | 2-agent (CLIN + COMM) | — |
| F-22 | open | KOL roster is uncontacted and mis-specialised for the populations that retain IV PCA | kol-feedback/**; D-COMM-1.1, 1.2 | Methodology | high | med | no | no | recurrence of a prior open finding |

**Resolution progress**: 0 / 22 resolved. 22 open.

### Headline reads

- **Seven findings block the next commit gate** — F-1, F-2, F-3, F-7, F-12, F-15, F-17. Every one is a defect in what the plan *asserts* or *fails to control*, not in how it executes.
- **The strongest multi-agent consensus is F-1**, reached independently by commercial, clinical and regulatory from three different evidence bases: the "competitors are reactive-alarm only, and have predictive monitoring we lack" premise is wrong in *both* directions at once. **14 of 22 findings carry multi-agent consensus.**
- **Four findings are high-severity / low-effort — do these first**: F-9 (standards matrix), F-11 (product code), F-13 (stale reference stack), and F-2 (add the exogenous risk class). Each is an authoring pass, not a program.
- **The most teachable finding is F-3**, because the same defect recurs across four independent variables (price, battery, accuracy, borrowed clinical outcomes) — a *process* defect, not four mistakes.
- **The dominant compound exposure is not any single finding.** The risk advisor's C-1 names it: F-1 (predictive wedge pre-empted) × the platform threat × the interoperability deficit are **one bet made three times** — that specification-level differentiation decides PCA placements. The evidence says it does not.
- **One absence disables three mitigations.** F-12, F-16 and F-18 all require the same missing substrate — a risk management plan, hazard analysis and hazard traceability matrix that resolve `null`. Closing it is the single highest-leverage action in the set.

### Two corrections absorbed into this analysis

Advisors corrected each other, and the record should show it rather than quietly adopting the later view.

1. **The clinical files exist.** `recs-commercial.md` §8 reported `clinical_evaluation_plan`, `clinical_evaluation_report` and `benefit_risk_analysis` as resolving to `null`. That is true of the **discovery index** and false of the **filesystem** — 15 records plus 2 templates live under `docs/project/dhfs/pca-device/clinical/`, which the index's `design-controls/`-rooted patterns miss. **Verified by the conductor.** The finding changes from "missing" to "**present but unusable**," which F-19 argues is the worse state: an empty folder is a known gap; a populated folder of script-generated records reads as coverage.
2. **The ERAS 2025 colorectal quotation is withdrawn.** `research-market-data.md` quoted ERAS Society 2025 colorectal guidance as saying evidence "does not strongly support opioid PCA." `research-pca-clinical-landscape.md` §A.1 attempted the same primary text, got **HTTP 403**, and found a guideline summariser stating the document carries **no PCA-specific recommendation** — grading the snippet `UNVERIFIED` and instructing it must not be quoted. **Neither file read the primary text.** This analysis therefore does not rely on it. F-6 rests instead on the ERAS **arthroplasty** consensus (Wainwright 2020, quoted verbatim from a retrieved PDF), the measured Premier utilization series, and the sub-category CAGR gap — all `SUBSTANTIATED` independently.

### At a glance

<svg viewBox="0 0 760 250" width="100%" style="max-width:760px;font-family:inherit" role="img" aria-label="Stacked bars showing, for each family of the project's own claims, how many stand as stated, how many are defective, and how many are unverifiable.">
  <g fill="currentColor" font-size="11.5">
    <text x="0" y="14" font-weight="700">The project's own claims, put under external test</text>
    <text x="0" y="30" opacity=".72">Counts are the research agents' own verdict tallies. Bars are proportional within each family.</text>
  </g>
  <g font-size="11" fill="currentColor">
    <rect x="0" y="44" width="11" height="11" rx="2.5" fill="#199e70"/><text x="17" y="54">Stands as stated</text>
    <rect x="150" y="44" width="11" height="11" rx="2.5" fill="#d95926"/><text x="167" y="54">Wrong, contradicted or refuted</text>
    <rect x="360" y="44" width="11" height="11" rx="2.5" fill="#86b6ef"/><text x="377" y="54">Unverifiable</text>
  </g>
  <g font-size="11.5" fill="currentColor">
    <text x="242" y="90" text-anchor="end">Market sizing &amp; growth</text>
    <text x="242" y="103" text-anchor="end" font-size="10" opacity=".62">20 verdict entries</text>
    <rect x="250" y="79" width="145" height="17" rx="4" fill="#199e70"/>
    <rect x="397" y="79" width="267" height="17" rx="4" fill="#d95926"/>
    <rect x="666" y="79" width="74" height="17" rx="4" fill="#86b6ef"/>
    <text x="322" y="92" text-anchor="middle" fill="#ffffff" font-size="10.5" font-weight="700">6</text>
    <text x="530" y="92" text-anchor="middle" fill="#ffffff" font-size="10.5" font-weight="700">11</text>
    <text x="703" y="92" text-anchor="middle" fill="#0b0b0b" font-size="10.5" font-weight="700">3</text>
    <text x="242" y="130" text-anchor="end">AI, interoperability &amp; pathway</text>
    <text x="242" y="143" text-anchor="end" font-size="10" opacity=".62">14 with stated verdicts</text>
    <rect x="250" y="119" width="138" height="17" rx="4" fill="#199e70"/>
    <rect x="390" y="119" width="350" height="17" rx="4" fill="#d95926"/>
    <text x="319" y="132" text-anchor="middle" fill="#ffffff" font-size="10.5" font-weight="700">4</text>
    <text x="565" y="132" text-anchor="middle" fill="#ffffff" font-size="10.5" font-weight="700">10</text>
    <text x="242" y="170" text-anchor="end">Clinical performance</text>
    <text x="242" y="183" text-anchor="end" font-size="10" opacity=".62">6 claims tested</text>
    <rect x="250" y="159" width="490" height="17" rx="4" fill="#d95926"/>
    <text x="495" y="172" text-anchor="middle" fill="#ffffff" font-size="10.5" font-weight="700">6 — none survives as written</text>
  </g>
  <g fill="currentColor" font-size="10.5" opacity=".62">
    <text x="0" y="206">Across all three families: 10 of 40 assessed claims stand as written. Clinical defects are mostly methodological</text>
    <text x="0" y="220">(wrong comparator, missing denominator, uncontrolled single-arm) rather than false — the devices are demo fabrications,</text>
    <text x="0" y="234">so the finding is about how the claims are CONSTRUCTED, not whether the fictional numbers are true.</text>
  </g>
</svg>

<svg viewBox="0 0 760 330" width="100%" style="max-width:760px;font-family:inherit" role="img" aria-label="Timeline of FDA clearances, Class I recalls and enforcement actions across the four incumbent infusion pump makers, 2020 to 2026.">
  <g fill="currentColor" font-size="11.5">
    <text x="0" y="14" font-weight="700">Incumbent regulatory posture, 2020–2026 — the quality window, and its clock</text>
    <text x="0" y="30" opacity=".72">Every incumbent has taken a Class I recall in the last three years. Three of four in the last eighteen months.</text>
  </g>
  <g font-size="11" fill="currentColor">
    <circle cx="6" cy="46" r="5.5" fill="#199e70"/><text x="17" y="50">510(k) clearance</text>
    <rect x="128" y="40.5" width="11" height="11" rx="2.5" fill="#d95926"/><text x="145" y="50">Class I recall</text>
    <path d="M244 40 l6 11 h-12 z" fill="#3987e5"/><text x="257" y="50">Enforcement action</text>
  </g>
  <g stroke="currentColor" opacity=".18">
    <line x1="150" y1="72" x2="150" y2="272"/><line x1="240" y1="72" x2="240" y2="272"/>
    <line x1="330" y1="72" x2="330" y2="272"/><line x1="420" y1="72" x2="420" y2="272"/>
    <line x1="510" y1="72" x2="510" y2="272"/><line x1="600" y1="72" x2="600" y2="272"/>
    <line x1="690" y1="72" x2="690" y2="272"/>
  </g>
  <g fill="currentColor" font-size="10.5" opacity=".6" text-anchor="middle">
    <text x="150" y="288">2020</text><text x="240" y="288">2021</text><text x="330" y="288">2022</text>
    <text x="420" y="288">2023</text><text x="510" y="288">2024</text><text x="600" y="288">2025</text><text x="690" y="288">2026</text>
  </g>
  <g font-size="11.5" fill="currentColor">
    <text x="142" y="96" text-anchor="end" font-weight="600">BD — Alaris</text>
    <line x1="150" y1="92" x2="735" y2="92" stroke="currentColor" opacity=".12"/>
    <text x="142" y="146" text-anchor="end" font-weight="600">ICU Medical — CADD</text>
    <line x1="150" y1="142" x2="735" y2="142" stroke="currentColor" opacity=".12"/>
    <text x="142" y="196" text-anchor="end" font-weight="600">Baxter</text>
    <line x1="150" y1="192" x2="735" y2="192" stroke="currentColor" opacity=".12"/>
    <text x="142" y="246" text-anchor="end" font-weight="600">B. Braun</text>
    <line x1="150" y1="242" x2="735" y2="242" stroke="currentColor" opacity=".12"/>
  </g>
  <g>
    <rect x="157" y="86.5" width="11" height="11" rx="2.5" fill="#d95926"/>
    <path d="M311 86 l6 11 h-12 z" fill="#3987e5"/>
    <circle cx="466" cy="92" r="5.5" fill="#199e70"/>
    <path d="M541 86 l6 11 h-12 z" fill="#3987e5"/>
    <rect x="580" y="86.5" width="11" height="11" rx="2.5" fill="#d95926"/>
    <circle cx="608" cy="92" r="5.5" fill="#199e70"/>
    <rect x="624" y="86.5" width="11" height="11" rx="2.5" fill="#d95926"/>
    <rect x="639" y="86.5" width="11" height="11" rx="2.5" fill="#d95926"/>
    <rect x="654" y="86.5" width="11" height="11" rx="2.5" fill="#d95926"/>
  </g>
  <g fill="currentColor" font-size="9.5" opacity=".72">
    <text x="150" y="112">Class I: all US pumps (Feb 2020) · consent decree live throughout</text>
    <text x="466" y="78" text-anchor="middle">K211218 return</text>
    <text x="735" y="112" text-anchor="end">4 Class I events since return · 483 review still open</text>
  </g>
  <g>
    <circle cx="332" cy="142" r="5.5" fill="#199e70"/>
    <rect x="480" y="136.5" width="11" height="11" rx="2.5" fill="#d95926"/>
    <path d="M594 136 l6 11 h-12 z" fill="#3987e5"/>
    <rect x="601" y="136.5" width="11" height="11" rx="2.5" fill="#d95926"/>
    <rect x="613" y="136.5" width="11" height="11" rx="2.5" fill="#d95926"/>
    <rect x="625" y="136.5" width="11" height="11" rx="2.5" fill="#d95926"/>
  </g>
  <g fill="currentColor" font-size="9.5" opacity=".72">
    <text x="332" y="128" text-anchor="middle">Smiths acquired</text>
    <text x="735" y="162" text-anchor="end">Warning letter: CADD Solis VIP "adulterated and misbranded" + 3 Class I on one day (Apr 2025)</text>
  </g>
  <g>
    <circle cx="358" cy="192" r="5.5" fill="#199e70"/>
    <rect x="475" y="186.5" width="11" height="11" rx="2.5" fill="#d95926"/>
    <circle cx="510" cy="192" r="5.5" fill="#199e70"/>
    <circle cx="555" cy="192" r="5.5" fill="#199e70"/>
    <circle cx="583" cy="192" r="5.5" fill="#199e70"/>
  </g>
  <g fill="currentColor" font-size="9.5" opacity=".72">
    <text x="735" y="212" text-anchor="end">8 clearances 2022–2025 — files routinely; 1 Class I (Aug 2023)</text>
  </g>
  <g><rect x="490" y="236.5" width="11" height="11" rx="2.5" fill="#d95926"/></g>
  <g fill="currentColor" font-size="9.5" opacity=".72">
    <text x="735" y="262" text-anchor="end">1 Class I with a patient death (Nov 2023) · zero clearances 2020–2026</text>
  </g>
  <g fill="currentColor" font-size="10.5" opacity=".62">
    <text x="0" y="312">Marker positions are approximate to the month. Every event is sourced in research-competitor-regulatory-record.md.</text>
  </g>
</svg>

---

### F-1: Positioning thesis rests on a premise our own input analysis contradicts

- **Author:** agent:commercial
- **Status:** open
- **Category:** Substantiation
- **Severity:** high
- **Effort:** med
- **Grade:** `ARITHMETIC` for the internal contradiction (verifiable by reading two project files); `SUBSTANTIATED` for the FDA-list absence; `UNVERIFIED` for BD's current labelled capability
- **What:** D-COMM-1.1 stakes the entire 5-year positioning on "the single largest competitive gap is the absence of predictive monitoring — market leaders are reactive-alarm only." **Both halves fail, in opposite directions.** (a) The incumbents are *not* reactive-alarm only: the project's own `state-of-the-art-analysis.md` L39/L52 records that BD's Alaris PCA Module ships **PCA Pause with EtCO₂ integration**, which auto-suspends the PCA infusion when capnography crosses a hospital-set threshold — monitoring-driven intervention on the exact PCA hazard. (b) Nor do competitors have the predictive capability we claim to lack: **zero of the 1,524 devices on FDA's AI-Enabled Medical Device List is an infusion pump of any kind**, verified three independent ways. Separately, all seven figures justifying the thesis are `INTERNAL-DEMO` (battery, accuracy, satisfaction, error reduction, KOL sentiment) or graded CONTRADICTED (the AI-market CAGR). Note the asymmetry: D-COMM-1.7 carries a `[VERIFY]` on the financial figures that stay internal, while D-COMM-1.1's customer-facing claims carry none.

**Worked example (before / after).**

*Before* — `commercial-strategy.md` L36:
> "…the **single largest competitive gap across the whole portfolio is the absence of predictive monitoring** — market leaders (BD Alaris, Baxter Spectrum IQ) are reactive-alarm only, while AI-enabled entrants demonstrate 15–30 min early warnings."

*After* — a version that survives checking:
> "**The competitive baseline, stated precisely.** No infusion pump of any manufacturer currently holds FDA authorization for an AI/ML-enabled predictive function — the FDA AI-Enabled Medical Device List (1,524 devices, current 2026-06-16) contains none `SUBSTANTIATED`. The relevant incumbent capability is not prediction but **monitored interlock**: BD's Alaris PCA Module integrates EtCO₂ and pauses the PCA infusion on a hospital-defined respiratory threshold `SUBSTANTIATED` (BD product documentation).
>
> **Our position is therefore a category-creation bet, not a catch-up.** The differentiation claim available to us is *earlier* warning than a threshold interlock provides — which requires (a) clinical evidence that advance prediction improves on threshold-triggered pause in the PCA/opioid context, and (b) a predictive methodology pre-specified in the PCCP from the outset (see F-7). Until both exist, we lead with the monitored-interlock parity story, not a predictive-superiority story."

- **Evidence:** `commercial-strategy.md` L36 vs `state-of-the-art-analysis.md` L39, L52. FDA-list absence: `research-ai-connectivity-regulatory.md` §A.1. AI-market CAGR: `research-market-data.md` row 3c. `[VERIFY]` asymmetry: `commercial-strategy.md` L124 vs L36.
- **Impact:**
  - _Commercial:_ the wedge is measured against a baseline that does not exist, so the differentiation margin is unknown and probably far narrower than stated; every downstream artifact built on D-COMM-1.1 inherits the defect.
  - _Regulatory:_ a "first predictive monitoring in PCA" marketing claim would have to survive comparison against a competitor's already-cleared monitoring-integrated PCA feature.
  - _Filing:_ no direct impact on K210345 — but the F6 substantial-equivalence argument must not assume an empty predictive field.
- **Resolution proposal:** In the source task feeding `/strategy assemble commercial`, replace D-COMM-1.1's premise with the corrected baseline above; apply the D-COMM-1.7 `[VERIFY]` treatment to every `INTERNAL-DEMO` figure in the "Why"; demote predictive monitoring from "the strategic throughline" to one funded option among the three positioning pillars. **Re-assemble — do not hand-edit `commercial-strategy.md`** (L8), or the fix is silently overwritten.
- **Depends on:** a Regulatory Affairs retrieval of BD Alaris PCA Module labeling, to convert the `UNVERIFIED` half.
- **Owner / next step:** Commercial Lead, with Regulatory Affairs.

### F-2: Risk register contains no competitor-threat category — R1–R5 are all endogenous

- **Author:** agent:commercial
- **Status:** open
- **Category:** Coverage
- **Severity:** high
- **Effort:** low
- **Grade:** `SUBSTANTIATED` for the missing threats' underlying facts; `INFERRED` for the pre-emption mechanism
- **What:** All five risks in D-COMM-1.9 are execution risks about things GlobalLogic controls — our evidence (R1), our claims (R2), our design (R3), our schedule (R4), our business model (R5). Not one names a competitor, a competitor action, a demand-side force, or a channel gate. This is a well-built *program* risk register with no *competitive* risk register anywhere in the document. D-COMM-1.9's own "Why" (L152) is honest that it was built to be probed by a clinical review — and it succeeds at that. The problem is coverage, not quality. R1 deserves specific credit for anticipating the borrowed-claim objection.

**Worked example (before / after).**

*Before* — D-COMM-1.9 R1 as written:
> "| **R1** | Predictive-monitoring SaMD clinical-evidence sufficiency — the 15–30 min warning claim must be substantiated for *PCA/opioid* context, not borrowed from general infusion | Clinical + Risk |"

Three columns: risk, description, owner. No likelihood, no impact, no leading indicator, no trigger, no control. It names a concern; it does not manage one.

*After* — the same risk specified so it can be tracked, plus the missing exogenous class:

| # | Class | Threat | L | I | Leading indicator | Trigger | Preventive control | Owner |
|---|---|---|---|---|---|---|---|---|
| R1 | Execution | Predictive-SaMD evidence insufficient in the PCA/opioid context | — | — | Q-Sub feedback on evidence plan | FDA requests clinical data at pre-sub | Pre-specify predictive methodology in the PCCP from v1 | Clinical + Risk |
| **R6** | **Exogenous** | An incumbent adds predictive alarming to its installed fleet under its own change-control envelope, at zero incremental capital cost to the customer | — | — | Competitor 510(k) filings under FRN/PHC; release notes on fleet software | Any incumbent clears or ships a predictive alarm function | Compress F6 timeline; secure a lead-account evidence partnership | Commercial + Reg |
| **R7** | **Exogenous** | ERAS/opioid-stewardship contraction removes IV PCA from the elective surgical pathways we target first | — | — | ERAS penetration in target accounts; IV-PCA order volume per account | Target-account ERAS penetration passes a set threshold | Re-weight Y1–Y3 targeting to ERAS-resistant populations | Commercial + Clinical |
| **R8** | **Exogenous** | Absent GPO contract coverage, the device is not evaluable regardless of specification | — | — | GPO contract coverage across the target-account list | Y1 close without a contract award | Make GPO award a Y1 commit gate | Commercial |
| **R9** | **Exogenous** | The incumbent quality window closes before we hold the contracts to convert it | — | — | Competitor recall cadence; consent-decree/warning-letter closure | Remediation closure announced | Build the fleet-migration + risk-absorption offer now | Commercial + Quality |
| **R10** | **Exogenous** | Consumables lock-out — the incumbent defends by discounting matched disposable sets, a lever we do not have | — | — | Competitor set pricing in contested bids | Set discounting appears in a lost bid | Price at fleet-TCO level, not unit level | Commercial |

_(Likelihood and impact ratings are left for the risk-management advisor to populate against a published scale — a rating without a scale is unauditable.)_

- **Evidence:** `commercial-strategy.md` L142–L156. Supporting facts: `research-market-data.md` §§ *How a new entrant actually wins placements*, *Competitive structure*, *The PCA utilization question*; ICU Medical FY2024 consumables-vs-systems split (1.6×).
- **Impact:**
  - _Commercial:_ the plan has no early-warning instrumentation for the events most likely to invalidate it, and no trigger thresholds — so a competitor response is discovered at the point of lost placement rather than in advance.
  - _Regulatory:_ R6's severity depends on incumbent change-control latitude, an open regulatory question.
  - _Filing:_ none direct.
- **Resolution proposal:** Add R6–R10 to the D-COMM-1.9 source block with owning discipline, leading indicator and trigger threshold each; relabel R1–R5 as **execution** risks so the two classes are visibly distinct. Re-assemble.
- **Owner / next step:** Commercial Lead, with Risk Management for register format.

### F-3: Comparative claims are scope-unlabelled and contradict the documents' own data

- **Author:** agent:commercial
- **Status:** open
- **Category:** Methodology
- **Severity:** high
- **Effort:** med
- **Grade:** `ARITHMETIC` for all three contradictions (reproducible from the project's own files); `INFERRED` for the units-error conclusion
- **What:** Four independent instances of one defect — a comparative claim with no measurement condition, no named comparator, or a scope mismatch between its two sides. This recurs across four unrelated variables, which makes it a **process defect rather than four mistakes**.

  **(a) Price — a units error.** `state-of-the-art-analysis.md` L64 states "9,567,700 annual IV pumps"; L65 states "1,547 devices"; L68 states "$6,185 per device average revenue." **9,567,700 ÷ 1,547 = 6,184.68 → $6,185.** So "9,567,700 annual IV pumps" is a **dollar figure mislabelled as a unit count**, and $6,185 is our own derived internal revenue-per-device — not a market ASP. It is then tabled at L71 beside two *secondary-market refurbished* prices, implying a ~6× premium we do not command. The honest number is in the same document at L70: Q4 2024, $127,500–$138,000 across 30+ units = **$4,250–$4,600/unit**, which sits at the top of the published $1,800–$4,500 PCA band — a perfectly defensible premium story that the document buried.

  **(b) Battery — a category error with a smoking gun.** "150+ hr vs typical 100-hour offerings" names no comparator. The same document's own table shows BD Alaris 6 hr @ 25 mL/hr, Baxter Sigma Spectrum 4 hr @ 125 mL/hr, ICU Medical Plum 360 7 hr @ 25 mL/hr — so against its own named competitors the claim is **21×–37×**, not 1.5×. Those are **mains-powered LVP backup runtimes**; ours is an **operating** spec, quoted with no flow rate at all. And the smoking gun: the **BD Alaris PCA Module — the one true like-for-like PCA comparator — appears in that same table as its own row with no battery figure**. The document compares against three non-PCA pumps while leaving the real comparator blank, one row below.

  **(c) Accuracy — three different numbers.** ±0.5% (`competitive-product-assessment.md` L14), ±0.35% "in laboratory applications" (`state-of-the-art-analysis.md` L24/L62), ±0.1% (`strategic-market-ai-infusion.md` L57); "market standard" as both ±2.3% and ±2.5%; no test conditions anywhere; and an unqualified "outperforming **all** major competitors."

  **(d) Borrowed and absolute claims.** "Zero wrong-medication errors since implementation" (L46) — a single-KOL testimonial presented as an absolute safety claim with **no denominator**, in a domain where the pre-intervention harm base rate is ~0.65 per 100,000 medications, so a genuine zero is achievable purely by having too small a denominator. And "60% adverse event reduction at Mass General Brigham, Mayo Clinic" (`strategic-market-ai-infusion.md` L60) — attributed to two named real institutions, with **no source found across 12 query variants** — which D-COMM-1.5 (L100) then uses as the reimbursement argument.

- **Evidence:** `state-of-the-art-analysis.md` L25, L47–L49, L64, L65, L68–L71; `competitive-product-assessment.md` L14, L46; `strategic-market-ai-infusion.md` L57, L60; consumed at `commercial-strategy.md` L36, L100. Corroboration: `research-pca-clinical-landscape.md` §C, §C.1; `research-market-data.md` rows 8a–8e.
- **Impact:**
  - _Commercial:_ none of these survive a value-analysis committee or a diligence reviewer; the price line implies a premium we do not command while burying the real one; D-COMM-1.5's health-economics dossier is scheduled to be built on an unsourced third-party figure.
  - _Regulatory:_ the absolute-zero safety claim and any claim beyond cleared labeling are promotional-claim exposure.
  - _Filing:_ claim consistency across the DHF and marketing material is an audit surface.
- **The same defect in the market numbers.** The conductor independently recomputed every growth claim in the three input analyses from the start and end values each document prints. Five of eight are internally inconsistent with their own figures:

<svg viewBox="0 0 760 330" width="100%" style="max-width:760px;font-family:inherit" role="img" aria-label="Bar chart of the gap between each stated CAGR and the CAGR implied by the same document's own start and end figures.">
  <g fill="currentColor" font-size="11.5">
    <text x="0" y="14" font-weight="700">Stated CAGR vs. CAGR implied by the document's own figures</text>
    <text x="0" y="30" opacity=".72">Gap in percentage points. Recomputed by the conductor from the start/end values printed in each source document.</text>
  </g>
  <g stroke="currentColor" opacity=".18" stroke-width="1">
    <line x1="330" y1="48" x2="330" y2="286"/><line x1="432.5" y1="48" x2="432.5" y2="286"/>
    <line x1="535" y1="48" x2="535" y2="286"/><line x1="637.5" y1="48" x2="637.5" y2="286"/>
    <line x1="740" y1="48" x2="740" y2="286"/>
  </g>
  <g fill="currentColor" font-size="10.5" opacity=".6" text-anchor="middle">
    <text x="330" y="302">0</text><text x="432.5" y="302">4</text><text x="535" y="302">8</text>
    <text x="637.5" y="302">12</text><text x="740" y="302">16 pp</text>
  </g>
  <g font-size="11.5" fill="currentColor">
    <text x="322" y="69" text-anchor="end">Global infusion pump market</text>
    <rect x="330" y="59" width="402.3" height="14" rx="4" fill="#3987e5"/>
    <text x="726" y="69" text-anchor="end" fill="#ffffff" font-weight="700" font-size="10">15.7 pp — stated 8.2% vs implied 24.0%</text>
    <text x="322" y="98" text-anchor="end">AI-enabled device market · assessment doc</text>
    <rect x="330" y="88" width="269.1" height="14" rx="4" fill="#3987e5"/>
    <text x="592" y="98" text-anchor="end" fill="#ffffff" font-weight="700" font-size="10">10.5 pp — stated 35% vs implied 45.5%</text>
    <text x="322" y="127" text-anchor="end">Neonatal market · market-research doc</text>
    <rect x="330" y="117" width="92.3" height="14" rx="4" fill="#3987e5"/>
    <text x="430" y="127" fill="currentColor" font-size="10.5" opacity=".85">3.6 pp — stated 5.6% vs implied 9.2%</text>
    <text x="322" y="156" text-anchor="end">Home infusion market</text>
    <rect x="330" y="146" width="74.3" height="14" rx="4" fill="#3987e5"/>
    <text x="412" y="156" fill="currentColor" font-size="10.5" opacity=".85">2.9 pp — stated 12.8% vs implied 9.9%</text>
    <text x="322" y="185" text-anchor="end">Neonatal market · assessment doc</text>
    <rect x="330" y="175" width="38.4" height="14" rx="4" fill="#3987e5"/>
    <text x="376" y="185" fill="currentColor" font-size="10.5" opacity=".85">1.5 pp — stated 5.6% vs implied 7.1%</text>
    <text x="322" y="214" text-anchor="end" opacity=".7">AI-enabled device market · market-research doc</text>
    <rect x="330" y="204" width="12.8" height="14" rx="4" fill="#86b6ef"/>
    <text x="350" y="214" fill="currentColor" font-size="10.5" opacity=".7">0.5 pp — consistent</text>
    <text x="322" y="243" text-anchor="end" opacity=".7">EU market</text>
    <rect x="330" y="233" width="3" height="14" rx="1.5" fill="#86b6ef"/>
    <text x="341" y="243" fill="currentColor" font-size="10.5" opacity=".7">0.1 pp — consistent</text>
    <text x="322" y="272" text-anchor="end" opacity=".7">Smart pump market</text>
    <rect x="330" y="262" width="3" height="14" rx="1.5" fill="#86b6ef"/>
    <text x="341" y="272" fill="currentColor" font-size="10.5" opacity=".7">0.0 pp — consistent</text>
  </g>
  <g fill="currentColor" font-size="10.5" opacity=".6">
    <text x="0" y="322">Tolerance for "consistent" is 0.6 pp (rounding). Separately, the same $19.5B / 8.2% pair appears in three mutually exclusive slots.</text>
  </g>
</svg>

- **And the same defect in the AI performance claims.** Three of them were traced to their origin, and none of the origins supports the claim:

<svg viewBox="0 0 760 230" width="100%" style="max-width:760px;font-family:inherit" role="img" aria-label="Three AI performance claims traced back to their actual sources, each of which fails to support the claim.">
  <g fill="currentColor" font-size="11.5">
    <text x="0" y="14" font-weight="700">Where the three AI performance claims actually come from</text>
    <text x="0" y="30" opacity=".72">Each was traced to its origin. None of the three origins supports the claim made.</text>
  </g>
  <g font-size="11.5" fill="currentColor">
    <text x="0" y="56" font-size="10.5" opacity=".6" font-weight="700">CLAIM AS WRITTEN</text>
    <text x="330" y="56" font-size="10.5" opacity=".6" font-weight="700">TRACED TO</text>
    <text x="645" y="56" font-size="10.5" opacity=".6" font-weight="700">VERDICT</text>
    <line x1="0" y1="62" x2="740" y2="62" stroke="currentColor" opacity=".18"/>
    <text x="0" y="84">"80% reduction in IV medication</text>
    <text x="0" y="98">errors with AI-driven systems"</text>
    <rect x="300" y="79" width="14" height="14" rx="3" fill="#d95926"/>
    <text x="330" y="84">A 2011 study of a rule-based dose-error</text>
    <text x="330" y="98" font-weight="700">reduction system — containing no AI</text>
    <text x="645" y="91" font-size="10.5" opacity=".85">misattributed</text>
    <line x1="0" y1="118" x2="740" y2="118" stroke="currentColor" opacity=".1"/>
    <text x="0" y="140">"45% reduction in</text>
    <text x="0" y="154">non-actionable alerts"</text>
    <rect x="300" y="135" width="14" height="14" rx="3" fill="#d95926"/>
    <text x="330" y="140">A single blog post,</text>
    <text x="330" y="154" font-weight="700">itself uncited</text>
    <text x="645" y="147" font-size="10.5" opacity=".85">unsourceable</text>
    <line x1="0" y1="174" x2="740" y2="174" stroke="currentColor" opacity=".1"/>
    <text x="0" y="196">"60% adverse-event reduction at</text>
    <text x="0" y="210">Mass General Brigham, Mayo Clinic"</text>
    <rect x="300" y="191" width="14" height="14" rx="3" fill="#d95926"/>
    <text x="330" y="196">No source of any kind, across</text>
    <text x="330" y="210" font-weight="700">12 query variants</text>
    <text x="645" y="203" font-size="10.5" opacity=".85">no source</text>
  </g>
</svg>

  The third names two real institutions, and D-COMM-1.5 uses it as the reimbursement argument. The research agent's recommendation was one word: *"Delete it."*

- **Resolution proposal:** Banner all three input-analysis files as not-for-external-use pending substantiation; retrieve the source PDF to resolve the 9,567,700 units error; relabel $6,185 as internal revenue-per-device and remove it from any competitor price table; rebuild L71 with scope labels, dates and sources, showing the Q4 2024 actual; add measurement conditions and named comparators to every battery and accuracy claim, or strike the comparison; **populate the Alaris PCA Module battery row or drop the battery comparison entirely**; re-derive every growth figure from a single sourced pair; strike the 60% figure rather than soften it.
- **Owner / next step:** Commercial Lead, with Marketing and Legal on the absolute and borrowed claims.

### F-4: Ambulatory extension benchmarks a device it will never meet on an RFP

- **Author:** agent:commercial
- **Status:** open
- **Category:** Methodology
- **Severity:** med
- **Effort:** low
- **Grade:** `SUBSTANTIATED` (openFDA + SEC filing); `INFERRED` for the wear-cycle-vs-battery unit mismatch
- **What:** D-COMM-1.8 (L131) benchmarks the F7 ambulatory PCA exclusively against **Insulet Omnipod and Tandem** — insulin patch pumps — and names neither ICU Medical, CADD, nor ambulatory PCA anywhere. ICU Medical acquired Smiths Medical in January 2022 for $2.35B, taking the **CADD** ambulatory-PCA franchise; an openFDA query confirms CADD-Legacy PCA Ambulatory Infusion System (K982839) under **product code MEA** — the same code an ambulatory PP3500-A would file under. Omnipod is an insulin pump in a different product code, sold to a different buyer through a different channel under a different payment mechanism; it will never appear in the same procurement. Compounding it, "7-day battery vs Omnipod's 72-hour benchmark" compares a battery specification to a **wear-cycle constraint** (set by insulin stability and cannula-site rotation, not power budget) — the same unit-mismatch defect as F-3.

**Worked example (before / after).**

*Before* — D-COMM-1.8 L131:
> "…and **against ambulatory insulin-patch form factors** (Insulet Omnipod, Tandem) as the design benchmark for the F7 ambulatory PCA (180g / 7-day battery class targets vs Omnipod's 72-hour benchmark)."

*After*:
> "**Procurement competitor (F7): ICU Medical's CADD ambulatory-PCA franchise**, acquired with Smiths Medical in January 2022 `SUBSTANTIATED` (SEC filing). CADD files under product code **MEA**, the same code an ambulatory PP3500-A would file under `SUBSTANTIATED` (openFDA). The project's own competitor table already records the right benchmark — CADD Legacy at **450g, 2–3 day battery** — against which a 180g target is a **60% weight reduction against the actual incumbent**, a materially stronger claim than the Omnipod comparison and one that will be in the room.
>
> **Industrial-design references (not procurement competitors): Insulet Omnipod, Tandem t:slim X2.** These inform form factor and patient-acceptance design only. Their wear intervals are set by infusion-set and site labeling rather than battery capacity, so no battery-runtime comparison is drawn against them."

- **Evidence:** `commercial-strategy.md` L131; `competitive-product-assessment.md` L63; `research-market-data.md` § *Ambulatory / CADD franchise position*; openFDA 510(k) API, retrieved 2026-08-05.
- **Impact:**
  - _Commercial:_ F7's competitive analysis, positioning and pricing are calibrated against a non-competitor, so the actual threat in the segment is unassessed — and the segment belongs to the same incumbent that holds the KLAS-winning hospital pump and the leading PCA franchise.
  - _Regulatory:_ an F7 filing would proceed against CADD-class MEA predicates, so positioning and predicate strategy currently point at different device families.
  - _Filing:_ relevant to a future F7 submission, not to K210345.
- **Resolution proposal:** Rewrite D-COMM-1.8's ambulatory paragraph per the "after" text; identify ICU Medical's **current** ambulatory-PCA line via a full openFDA sweep on product code MEA plus ICU product literature (the advisor's 8-record query did not exhaust the franchise, and `icumed.com` returned HTTP 404 — so CADD-Solis's absence from that result set is **not** established absence).
- **Owner / next step:** Commercial Lead, with Regulatory Affairs confirming the MEA predicate landscape.

### F-5: Launch sequencing and reimbursement posture ignore how placements are actually bought

- **Author:** agent:commercial
- **Status:** open
- **Category:** Coverage
- **Severity:** high
- **Effort:** high
- **Grade:** `SUBSTANTIATED` for the placement mechanics and the live CMS rulemaking; `UNVERIFIED` for the home-infusion payment-pathway specifics
- **What:** Every commit boundary in D-COMM-1.3's five-year table is a **regulatory vehicle**. There is no GPO contract-award milestone, no fleet-replacement targeting window, no capital-cycle gate, no TCO-model gate — and D-COMM-1.7 funds the next year on attach-rate and evidence, not contract coverage. GPO contracting appears in D-COMM-1.6 (L109) as a *channel mechanism*, never as the **evaluability gate** the evidence says it is: a device not on the IDN's GPO agreement is frequently not evaluable at all, TCO dominates unit price (software licences 10–15% of replacement value annually; EMR networking more than doubles cost), and displacement happens at fleet-replacement events on ~3-year capital horizons. A plan clocked only to FDA will land flagship releases in years when target accounts are not buying. Separately, D-COMM-1.5 applies **one reimbursement posture** (cost-avoidance, DRG-bundled) across all five years and all three segments — including the Y3–Y5 home/ambulatory segment, a materially different payment environment in which a **CY2027 HH PPS rulemaking published 2026-07-06** is actively addressing DME benefit expansion for infusion pumps. No owner tracks it.

**Worked example (before / after).** D-COMM-1.3's Year-1 row:

*Before:*

| Year | Theme | Regulatory vehicle | Headline releases |
|---|---|---|---|
| **Y1 (2026)** | Defend & connect the base | Letter-to-File / PCCP envelope (within K210345) | Drug Library Manager GA; Connectivity Adapter GA; Fleet Management + Telemetry |

*After:*

| Year | Theme | Regulatory vehicle | **Commercial gate** | Headline releases |
|---|---|---|---|---|
| **Y1 (2026)** | Defend & connect the base | Letter-to-File / PCCP envelope (within K210345) | **GPO contract award secured in ≥N target IDNs; fleet-age + contract-expiry map published for the top-N account list; fleet-level TCO model built and validated against one real bid** | Drug Library Manager GA; Connectivity Adapter GA; Fleet Management + Telemetry |

Same regulatory discipline, with the gate that actually determines whether anything can be sold sitting beside it.

- **Evidence:** `commercial-strategy.md` L58–L64, L68, L98–L102, L109, L124; `research-market-data.md` § *How a new entrant actually wins placements*; Federal Register API (CMS), CY2027 HH PPS rate update published 2026-07-06, retrieved 2026-08-05.
- **Impact:**
  - _Commercial:_ the plan can execute perfectly against FDA and still miss every buying window; without GPO coverage the device may not be evaluable regardless of clearance; the ambulatory business case is underwritten on an inpatient reimbursement assumption.
  - _Regulatory:_ none direct — the regulatory sequencing itself is sound.
  - _Filing:_ none.
- **Resolution proposal:** Add a "Commercial gate" column to D-COMM-1.3 as above; build the target-account list with GPO coverage, fleet age and contract expiry; add contract coverage to D-COMM-1.7's stage-gate criteria; split D-COMM-1.5's posture by care setting after reading the CY2027 HH PPS rule text and the external-infusion-pump DME coverage criteria; assign a named owner to track CMS rulemaking affecting infusion-pump benefit scope.
- **Owner / next step:** Commercial Lead with Program Manager and Health Economics.

### F-6: PCA structural narrowing unmodelled in segmentation and geography

- **Author:** agent:commercial
- **Status:** open
- **Category:** Coverage
- **Severity:** med
- **Effort:** med
- **Grade:** `INFERRED` — guideline direction, ERAS cohort magnitudes and the sub-category CAGR gap converge; the 2025 expert consensus and ongoing PCA-optimisation literature bound the claim short of collapse
- **What:** PCA pumps grow at **5.51%** inside a **6.5–8.5%** category — narrowing, not collapse. Commercially this is a **segmentation event**: IV PCA is being removed from the ERAS-reached elective surgical pathways (colorectal, joint replacement, gynae-onc, thoracic) and retained where multimodal and regional techniques cannot cover — opioid-tolerant patients, trauma, oncology and palliative pain, sickle-cell crisis, burns, and non-ERAS settings. D-COMM-1.2 (L45) makes "acute-care hospitals (anesthesia / acute pain services)" the **primary segment through Years 1–3** — precisely the ERAS-exposed buyer — while the populations that inherit residual demand appear only as segment 3, deferred to Years 3–5. Two aggravating factors: (i) the 5.51% figure comes from a model whose published restraints list recalls, medication errors, cybersecurity and supply chain but omit **ERAS, multimodal analgesia and regional anaesthesia entirely** — so it is the *optimistic* case, not the base case; (ii) APAC is the fastest-growing PCA region at 7.29% and is absent from D-COMM-1.6, which selects EU and Canada on KOL footprint, while the actual case against APAC (145%/125% tariffs, NMPA complexity) sits unused in the project's own input analysis.

<svg viewBox="0 0 760 260" width="100%" style="max-width:760px;font-family:inherit" role="img" aria-label="Range bars comparing published CAGR estimates across infusion market segments. PCA pumps are the slowest.">
  <g fill="currentColor" font-size="11.5">
    <text x="0" y="14" font-weight="700">Published growth rates — where PCA sits inside its own category</text>
    <text x="0" y="30" opacity=".72">Bars span the range across published vendor estimates; a dot marks a single-source point estimate.</text>
  </g>
  <g stroke="currentColor" opacity=".18">
    <line x1="300" y1="48" x2="300" y2="196"/><line x1="386" y1="48" x2="386" y2="196"/>
    <line x1="472" y1="48" x2="472" y2="196"/><line x1="558" y1="48" x2="558" y2="196"/>
    <line x1="644" y1="48" x2="644" y2="196"/><line x1="730" y1="48" x2="730" y2="196"/>
  </g>
  <g fill="currentColor" font-size="10.5" opacity=".6" text-anchor="middle">
    <text x="300" y="212">4%</text><text x="386" y="212">5%</text><text x="472" y="212">6%</text>
    <text x="558" y="212">7%</text><text x="644" y="212">8%</text><text x="730" y="212">9%</text>
  </g>
  <g font-size="11.5" fill="currentColor">
    <text x="292" y="68" text-anchor="end">Infusion pumps, global</text>
    <rect x="515" y="57" width="215" height="13" rx="4" fill="#3987e5"/>
    <text x="510" y="68" text-anchor="end" font-size="10.5" opacity=".8">6.5–8.5%</text>
    <text x="292" y="94" text-anchor="end">Infusion pumps, US</text>
    <circle cx="583.8" cy="89" r="6" fill="#3987e5"/>
    <text x="597" y="93" font-size="10.5" opacity=".8">7.3%</text>
    <text x="292" y="120" text-anchor="end">Infusion pump software</text>
    <circle cx="561.4" cy="115" r="6" fill="#3987e5"/>
    <text x="575" y="119" font-size="10.5" opacity=".8">7.04%</text>
    <text x="292" y="146" text-anchor="end">Home infusion therapy</text>
    <rect x="515" y="135" width="206" height="13" rx="4" fill="#3987e5"/>
    <text x="510" y="146" text-anchor="end" font-size="10.5" opacity=".8">6.5–8.4%</text>
    <text x="292" y="172" text-anchor="end" font-weight="700">PCA pumps</text>
    <circle cx="429.9" cy="167" r="7" fill="#d95926"/>
    <text x="444" y="171" font-size="10.5" font-weight="700" fill="#d95926">5.51% — slowest segment named in the analysis</text>
  </g>
  <g fill="currentColor" font-size="10.5" opacity=".62">
    <text x="0" y="234">PCA grows ~1.8 points slower than the category it sits inside. Competing PCA estimates run far higher (6.1–19.3%) but are</text>
    <text x="0" y="248">less methodologically explicit; the 5.51% figure is from the one report that publishes its restraint weights — and omits ERAS.</text>
  </g>
</svg>

  **The honest bound, and a withdrawn citation.** The clinical evidence base explicitly cautions that the **guideline-to-ward-practice gap is years wide** — a 2022 NHS enhanced-recovery protocol still specifies routine PCA for colorectal surgery, and a 2025 cohort of 1,461 IV-PCA patients had no routine respiratory monitoring at all. A threat model reading only the guidelines will **time this threat too early**. This finding is about re-weighting, not retreat. **Note also that the ERAS 2025 colorectal quotation one research file used is withdrawn** (see *Two corrections absorbed* above) — the finding rests instead on the ERAS **arthroplasty** consensus (Wainwright 2020, *"strongly recommended that the use of such pumps is limited in the routine arthroplasty surgical population,"* quoted verbatim from a retrieved PDF), the measured Premier series (open-lobectomy PCA **27% → 13%**, P < .0001, 86,308 cases), seven before/after ERAS cohorts clustering 50–88% pre → 0–32% post, and the CAGR gap above.

- **Evidence:** `research-market-data.md` § *A vendor blind spot worth knowing about*, § *Sub-segments*; `research-pca-clinical-landscape.md` §A.1, §A.2, §A.4, § *Implications* item 6; `commercial-strategy.md` L45, L109; tariff/NMPA rationale at `state-of-the-art-analysis.md` L34, L72.
- **Impact:**
  - _Commercial:_ the plan's primary segment for its first three years is the one under structural pressure, and the growth-inheriting segment is deferred to the back half; the business case is underwritten to a CAGR whose own model omits the largest force acting on it.
  - _Clinical:_ the retained-indication list (opioid-tolerant, trauma, oncology, sickle-cell, burns) implies different use environments and different user profiles than the elective-surgical assumption.
  - _Regulatory:_ F7's home indication becomes more strategically load-bearing if hospital PCA narrows faster than modelled.
- **Resolution proposal:** Subdivide D-COMM-1.2 segment 1 into ERAS-exposed and ERAS-resistant populations, weighting Y1–Y3 targeting to the latter; reassess whether segment 3 can start before Y3; record an explicit written rationale in D-COMM-1.6 for excluding the fastest-growing PCA region; re-underwrite D-COMM-1.7 with a downside case below 5.51%. **Price the execution cost first** — the ERAS-resistant segments are smaller and more fragmented, so this trades exposure for a harder commercial motion.
- **Owner / next step:** Commercial Lead, with Clinical Affairs to confirm ERAS penetration in the target account base.

### F-7: PCCP envelope over-claimed — F4/F5 categorised B cannot ride a PCCP

- **Author:** agent:regulatory-affairs
- **Status:** open
- **Category:** Drift
- **Severity:** high
- **Effort:** med
- **Grade:** `INFERRED` — application of `SUBSTANTIATED` statutory text to the roadmap table
- **What:** D-COMM-1.4 assigns category **B (PCCP-authorized)** to F4 (Alerts Engine v1) and F5 (Clinical Surveillance). Both are net-new SaMD functions in DHFs other than `pca-device`; neither exists in K210345. A PCCP authorises pre-specified modifications to a *cleared* function within the cleared intended use (FD&C §515C(a)(2)/(b)(2), PCCP guidance §IX) — **there is nothing to modify.** Separately, F6's PCCP-for-retraining is sequenced *after* F4's, but Appendix B Modification Scenario 2 requires the predictive methodology to be pre-specified from the start, so the dependency is inverted. And the annual cadence assumes 3–6 month clearances against a **142-day median with 34.6% exceeding six months and a P90 of 266 days**.

**Worked example (before / after).** *Before:* `| F4 | Alerts Engine v1 — smart alarm filtering | alerts-engine (SaMD) | Y2 | **B (PCCP)** |`. *After:* `| F4 | … | Y2→Y3 | **C — own 510(k), with the PCCP filed alongside it** |`. Three independent reasons, any one sufficient: (1) nothing to modify — K210345 cleared reactive alarms, not alarm filtering; (2) wrong DHF — `alerts-engine` sits under `cloud-suite`, and a PCCP on device A cannot authorise a function in DHF B; (3) the direction of change is adverse — alarm *filtering* reduces annunciation on a safety alarm, which FDA's Appendix B treats as PCCP-eligible only inside an already-cleared alarm function with a pre-specified non-inferiority margin. **What it costs:** a Y2 GA becomes Y2-late/Y3. **What it buys:** it structurally eliminates the ICU Medical failure mode, and it creates the right moment to file the PCCP that pre-specifies F6's predictive methodology — two years before F6 is funded.

- **Evidence:** `commercial-strategy.md` D-COMM-1.4 rows F4/F5/F6, D-COMM-1.3 Y2–Y4; `research-ai-connectivity-regulatory.md` §C.3, §C.4, §C.7; `regulatory-strategy.md` §2 ("introduced via PCCP **or** future filings" — where the ambiguity lives).
- **Impact:** _Regulatory:_ a submission-free plan for two device functions that require submissions. _Commercial:_ F4 and F5 GA dates are not achievable as written, and the slip cascades to F6 and F8 under D-COMM-1.3's own slip rule. _Filing:_ risk of an unfiled-change finding of exactly the ICU Medical shape.
- **Resolution proposal:** Re-categorise F4 → C and F5 → A-or-C after a classification determination; file F4's PCCP alongside F4's submission and pre-specify the F6 predictive methodology in it; re-plan D-COMM-1.3 on P90 review times plus a Q-Sub cycle and one RTA contingency.
- **Owner / next step:** RA Lead with Commercial Lead — amend D-COMM-1.4 at source and author the regulatory-strategy §1 PCCP-scope decision.

### F-8: No predicate for a predictive PCA function, and De Novo has never been evaluated

- **Author:** agent:regulatory-affairs
- **Status:** open
- **Category:** Coverage
- **Severity:** high
- **Effort:** med
- **Grade:** `SUBSTANTIATED` (predicate landscape) + `OPINION` (pathway recommendation)
- **What:** The newest same-code (MEA) PCA clearance is **K162165, 2017-08-29** — nine years. Zero AI-enabled infusion pumps exist across 1,524 rows of FDA's AI list. The one directly analogous cleared capability, Sepsis ImmunoScore, reached market via **De Novo (DEN230036)**. The project's Q-Sub asks six questions and **none concerns the predictive function's pathway**; Q3.1 addresses only PP3000 substantial equivalence "with added connectivity." Regulatory-strategy §9 still lists "Predicate lineage beyond PP3000" as pending. The advisor's read: forcing a novel predictive function through 510(k) against a 2017-era predicate landscape risks an **NSE** — which costs the whole submission, not merely time.
- **Evidence:** `research-competitor-regulatory-record.md` claims 2–3, 6; `research-ai-connectivity-regulatory.md` §A.1, §A.10, §C.5; `docs/project/submissions/qsub/fda-questions.md` (all six read); `regulatory-strategy.md` §9.
- **Impact:** _Regulatory:_ NSE risk on the roadmap's most expensive filing. _Commercial:_ the $24M / 42-month predictive-monitoring line item is underwritten against an unexamined pathway. _Filing:_ De Novo would create the classification and special controls competitors must then meet — a strategic asset the plan does not price.
- **Resolution proposal:** Add a Q-Sub question electing between 510(k)-with-predicate and De Novo for the predictive function, with a stated preliminary position and the DEN230036 precedent cited; author regulatory-strategy §9's predicate-lineage decision before F6 is funded.
- **Owner / next step:** RA Lead — draft the question and a §8 Q-Sub-strategy section.

### F-9: Standards matrix anchors on a non-recognized standard and omits every recognized one

- **Author:** agent:regulatory-affairs
- **Status:** open
- **Category:** Substantiation
- **Severity:** high
- **Effort:** low
- **Grade:** `SUBSTANTIATED`
- **What:** **IEC 60601-2-24 is not FDA-recognized** (absent between recognized -23 and -25) and ANSI/AAMI ID26 is withdrawn — so **there is no FDA-recognized particular safety standard for infusion pumps.** The project caught this once and never propagated it: `docs/external/standards/iec-60601-2-24.md` line 7 states it plainly and its "do not claim recognized conformity" check is still `[ ]` pending, while the standard remains listed as a peer of IEC 60601-1 in the SAD (§3, §5, §7) and in the design-inputs / user-needs / SRS headers. The FDA-recognized document for this class — **AAMI TIR101:2021 (recognition 6-482, entered 2022-05-30, extent Complete)**, which explicitly covers **PCA mode** — has **no applicability doc**. Neither do the recognized interoperability standards (UL 2800-1:2022 family 13-121/125/126/127; ANSI/AAMI 2700-1:2019 13-120 — the successor to ASTM F2761), nor the *Infusion Pumps — Total Product Life Cycle* guidance and its **safety assurance case**. The SAD also cites the 2023 cybersecurity guidance, two supersessions stale.
- **Evidence:** `research-ai-connectivity-regulatory.md` §B.8, §D.5; `docs/external/standards/iec-60601-2-24.md` lines 7, 54; `pca-device-system-sad.md` §3, §5, §7; folder listings of `docs/external/standards/` (12 files) and `docs/external/fda-guidance/` (12 files).
- **Impact:** _Regulatory:_ a submission claiming conformity to a non-recognized standard is a correctable but avoidable finding; a missing safety assurance case for this device class is **not** correctable late. _Commercial:_ Fresenius already markets "first cleared following TIR101" — this is competitive parity, not only compliance. _Filing:_ interoperability evidence has no standard to attach to.
- **Resolution proposal:** Create TIR101, TPLC-guidance, UL 2800-1:2022 and 2700-1:2019 applicability docs; demote 60601-2-24 to a labelled test-method basis everywhere it appears; refresh the cybersecurity citation; schedule the safety assurance case as a tracked 510(k) deliverable.
- **Owner / next step:** RA Lead with Systems Engineering — one authoring pass. **High severity, low effort — do this first.**

### F-10: No filing-trigger rule for recall remedies — the ICU Medical failure mode is unguarded

- **Author:** agent:regulatory-affairs
- **Status:** open
- **Category:** Methodology
- **Severity:** high
- **Effort:** high
- **Grade:** `SUBSTANTIATED` (precedent) + `INFERRED` (applicability to PP3500)
- **What:** FDA holds ICU Medical's Medfusion 4000 and CADD Solis VIP **adulterated (§501(f)(1)(B)) and misbranded (§502(o))** for shipping changes that could significantly affect safety or effectiveness without the 510(k) required by **21 CFR 807.81(a)(3)(i)** — where the change **was the remedy for a Class I recall**, where **ICU's own procedure said a 510(k) was required**, and where FDA expressly rejected the label-disclosure workaround as *"not sufficient."* PP3500 is marketed with an active post-market record (complaint rate 7.5/1,000/yr, one serious injury, one Field Safety Notice), so **this precedent applies now, not at next filing**. §524B compounds it: modifications, including via Special or Abbreviated 510(k), still require the postmarket-cyber plan and an SBOM.
- **Evidence:** `research-competitor-regulatory-record.md` claims 29–32; `research-ai-connectivity-regulatory.md` §D.4 (guidance §VII.D); `DEV-PP3500_regulatory_info.md` Post-Market Surveillance section.
- **Impact:** _Regulatory:_ the highest-probability enforcement exposure on this program, and it is a **process** exposure, not a product one. _Commercial:_ the credible pitch against BD and ICU is "the safety architecture without the compliance history" — a single unfiled corrective push forfeits it. _Filing:_ a strong argument for scoping the PCCP wide on anticipated change families at the original filing rather than stretching it later.
- **Resolution proposal:** Amend change control so the filing trigger is *"does this change a risk-control measure?"*; require a filing determination before any field release of a corrective software change; require compensating field mitigation (use restriction / customer notification) when the change falls outside the PCCP; state explicitly that label disclosure is not a permitted mitigation.
- **Owner / next step:** Quality Engineering with RA Lead. **Depends on F-15/F-16** — the gate cannot be written until there is a risk file for it to look up.

### F-11: Product code on file is LZH ("Pump, Infusion, Enteral") for a PCA pump

- **Author:** agent:regulatory-affairs
- **Status:** open
- **Category:** Substantiation
- **Severity:** high
- **Effort:** low
- **Grade:** `SUBSTANTIATED` (code definitions, live openFDA query, independently re-run by the conductor) / `INTERNAL-DEMO` (the project record's assignment)
- **What:** `DEV-PP3500_regulatory_info.md` line 22 states **"FDA Product Code: LZH (Infusion Pump, Patient-Controlled Analgesia)."** An openFDA `device/classification` query returns **LZH = "Pump, Infusion, Enteral"** (21 CFR 880.5725, Class II); the PCA code is **MEA = "Pump, Infusion, Pca"** (same regulation, Class II); the general code is **FRN = "Pump, Infusion."** The code assignment and its own parenthetical label disagree with FDA's database. Q-Sub Q1.3 asks FDA to "confirm the predicate's product code" **without naming one**, so the Q-Sub cannot surface the error.
- **Evidence:** `DEV-PP3500_regulatory_info.md` line 22; openFDA `device/classification.json` for LZH / MEA / FRN, queried 2026-08-06 by the advisor and independently re-run by the conductor.
- **Impact:** _Regulatory:_ a mis-coded submission risks routing to the wrong review branch and an RTA cycle — which restarts a calendar the roadmap has no slack for. _Filing:_ it also forces the deliberate MEA-vs-FRN-vs-PHC election the program has never made — the same decision that governs the Drug Library Manager's code.
- **Resolution proposal:** Correct the device record with the openFDA definition quoted; make the code election an explicit regulatory-strategy decision (MEA for PCA identity vs FRN for platform identity vs PHC for the safety-software layer); rewrite Q1.3 to name the proposed code and ask FDA to confirm it.
- **Owner / next step:** RA Lead — device-record correction plus a Q1.3 rewrite before Q-Sub transmission. **High severity, low effort.**

### F-12: Cybersecurity submission evidence is unfilled templates across all ten DHFs, while three manifests assert it exists

- **Author:** agent:cybersecurity
- **Status:** open
- **Category:** Coverage
- **Severity:** high
- **Effort:** high
- **Grade:** `SUBSTANTIATED` — every file and index entry cited was read; the conductor independently confirmed the stub sizes and placeholder count
- **What:** `cybersecurity_plan` resolves `null` for **all ten** DHFs. The threat model and SBOM resolve `exists: true` at ~1.8 KB each but are **unfilled QMS templates** (`{{DHF_NAME}}`, `{{Summary per the parent QMS template}}`, `{{}}`), rev 0.1 DRAFT, "not released," replicated identically across all ten. The vulnerability-management plan is the same stub and exists in only three of ten. Meanwhile `qsub/composition-manifest.md` L67 states *"Per-component evidence exists"* as the reason for excluding the system-level cybersecurity assessment, and `510k/composition-manifest.md` pulls Cybersecurity Plan + Threat Model + SBOM from three DHFs that have none. §524B makes the vulnerability-monitoring plan and the SBOM **statutory** premarket content, with FDA able to refuse-to-accept since 2023-10-01.

  **The generalisable lesson, and it reaches past cybersecurity: role resolution is not content.** Any dashboard, tracker or readiness report keyed on `exists: true` currently reports this program as having a threat model and an SBOM for ten components. It has neither, for any.

- **Evidence:** `pdlc-demo-dhf-discovery.json` (all ten `dhf_roles` blocks); `pca-device/cybersecurity/GL-TMP-SW-002-threat-model.md` (1,810 bytes, 5 `{{` placeholders — conductor-verified), `GL-WI-SW-002-sbom.md`, `GL-SOP-SW-004-vulnerability-management-plan.md`; `qsub/composition-manifest.md` L67 (conductor-verified); `510k/composition-manifest.md` L50, L61–62, L77; `research-ai-connectivity-regulatory.md` §D.4.
- **Impact:** _Security:_ no threat model means no basis for the security requirements that do exist, no attack-surface baseline, and no way to arbitrate the TLS 1.2-vs-1.3 drift between the SRS and both SADs. _Regulatory:_ direct RTA exposure — the two artifacts §524B makes statutory are both templates. _Commercial:_ HSCC MC2 v2 #44 makes SBOM delivery a contract term and HICP 9.L.B tells health systems to demand an SBOM plus MDS2 before purchase.
- **Resolution proposal:** Two-speed. **Immediately**, annotate every manifest row with the artifact's true revision status and correct the Q-Sub L67 assertion — a one-pass edit that removes a false claim from a submission-composition document. **Then** author one system-level threat model spanning device + Adapter + Cloud + hospital-IT boundary (methodology justified, exploitability not probability), generate a real machine-readable SBOM built to the CISA 2026 superset, and write one platform-level Cybersecurity Management Plan whose numeric commitments match MC2 v2 (#31 30-day patch, #33 3-business-day KEV notice, #35 5-day breach notice).
- **Owner / next step:** Cybersecurity Lead (author) with Regulatory Affairs (manifest correction, immediately).

### F-13: Both tiers of the cybersecurity reference stack are two supersessions stale, and one states a mandate FDA does not impose

- **Author:** agent:cybersecurity
- **Status:** open
- **Category:** Substantiation
- **Severity:** high
- **Effort:** low
- **Grade:** `SUBSTANTIATED` — both tiers read; the current-edition fact independently double-verified
- **What:** The registry distillation (L1a) and the project applicability file (L1b) both carry `**Document Date**: September 27, 2023` and the superseded title *"Quality **System** Considerations."* The operative guidance is the **February 3, 2026** issue, retitled *"Quality **Management** System Considerations"* (docket FDA-2021-D-1158), superseding the **June 27, 2025** issue, which superseded September 2023 — **two supersessions in eight months.** Separately, `docs/external/standards/iec-81001-5-1.md` L156 asserts SBOM *"Machine-readable format required (SPDX or CycloneDX)"*; FDA says industry-accepted formats *"are encouraged"*, and those formats come from the NTIA document, not an FDA mandate. That same file's clause numbers carry an unclosed `[VERIFY]` and every row of its verification-checks table is an unpopulated stub. **Citation verdicts:** guidance edition **broken**; SPDX/CycloneDX mandate **broken**; 81001-5-1 clause numbers **unverified** (paywalled, absent at every local rung — closable only with the purchased standard).
- **Evidence:** the L1a distilled reference and L1b `docs/external/fda-guidance/cybersecurity.md`; `docs/external/standards/iec-81001-5-1.md` L156, L179–193; `research-ai-connectivity-regulatory.md` §D.5, §D.6; `research-competitor-regulatory-record.md` claim 75.
- **Impact:** _Security:_ the SBOM will be built to the wrong contract — the 2021 NTIA baseline lacks the component hashes, licences, author signature, tool provenance and generation context that CISA's 2026 replacement specifies. _Regulatory:_ a submission citing a superseded edition is an audit finding on its own — and it is the **reference layer** that is stale, so anything authored from it inherits the defect. _Commercial:_ an SBOM failing a buyer's format expectation stalls the Vendor Assessment Package.
- **Resolution proposal:** Refresh both tiers to the February 2026 edition **before authoring any cybersecurity artifact**; strike the SPDX/CycloneDX "required" language; either close the 81001-5-1 clause `[VERIFY]` against a purchased copy or drop clause numbers and cite deliverables only; add a standing re-check of the governing edition at every submission gate.
- **Owner / next step:** Regulatory Affairs (refresh) with Cybersecurity Lead (SBOM baseline decision). **High severity, low effort.**

### F-14: The Year-1 connected roadmap expands the attack surface across a trust boundary the architecture strategy still records as unresolved

- **Author:** agent:cybersecurity
- **Status:** open
- **Category:** Methodology
- **Severity:** high
- **Effort:** med
- **Grade:** `SUBSTANTIATED` for each component fact; `INFERRED` for the incompatibility
- **What:** `architecture-strategy.md` § *Open Items* still carries *"Trust and network boundaries — where PHI lives across device↔adapter↔hospital-IT↔cloud"* and *"Whether the Connectivity Adapter talks to Our Cloud Suite directly… or not at all in the cleared baseline"* as **unresolved**. The Adapter SAD nonetheless asserts an answer — cloud egress *"optional, out of baseline… de-identified fleet telemetry only. Disabled by default"* — and points its provisioning trust anchor at a *"(see Cybersecurity Plan)"* that resolves `null`. D-COMM-1.4 then ships F2 (Adapter GA) and F3 (fleet management + telemetry dashboards) in **Year 1**, and F4/F5 cloud SaMD in Y2 — none of which function with egress disabled. `INFERRED`: a cloud dashboard cannot render telemetry over a disabled path. Two competitors have had **Class I recalls originating in exactly this layer** — BD's Alaris Systems Manager / Care Coordination Engine Infusion Adapter (2025-02-18, outdated automated programming requests reaching the pump) and ICU Medical's CADD-Solis wireless module (Z-1662-2025, still expanding 2026-05-27). Layered on top, F6/F8 put cloud-hosted model inference on infusion telemetry — which defeats the "de-identified egress" claim (per-patient prediction must be re-associated with a named patient) and introduces model-artifact integrity, service-availability and data-poisoning threats for which the SRS has no analogue: the firmware signature requirement covers firmware bundles only.

  **A discipline note the advisor insisted on.** The ICU Medical wireless recall is a **reliability failure, not a cyber exploit** — no CVE, no advisory, no adversary. Its legitimate use is narrow: evidence that the integration layer is where connected pumps now fail in ways that stop therapy.

- **Evidence:** `architecture-strategy.md` § *Open Items*; `connectivity-adapter-system-sad.md` §2, §5, §7, §8; `commercial-strategy.md` D-COMM-1.4 rows F2–F6, F8; `pca-device-system-sad.md` §6; `software-requirements.md` §G8; `research-competitor-regulatory-record.md` claims 22, 35.
- **Impact:** _Security:_ the largest new attack surface in the program is being built across a boundary with no threat model, no resolved data classification, and no integrity requirement for cloud→device payloads. _Regulatory:_ if F3 ships in Y1 with egress enabled, the cleared baseline described in the 510(k) is wrong — and the Adapter SAD already warns that behaviour beyond pass-through flips its MDDS classification. _Commercial:_ a hospital security review of the Year-1 connected offering will probe exactly where two competitors failed.
- **Resolution proposal:** Resolve the open item as a decision, not an assumption, and model the Adapter→Cloud link in **both** states. Replace the unqualified word "de-identified" with field-level data classification plus a written re-identification-risk assessment. Enumerate every inbound cloud→Adapter payload type and give each a signature-verification requirement. Gate enablement on threat-model coverage + security requirements + verification protocols. **If F3 ships in Y1, record cloud-enabled as the cleared baseline and file it that way.**
- **Owner / next step:** Systems Engineering (boundary decision) with Cybersecurity Lead and Regulatory Affairs.

### F-15: D-COMM-1.9 is a risk list, not a risk register — no controls on any of R1–R5

- **Author:** agent:risk-management
- **Status:** open
- **Category:** Methodology
- **Severity:** high
- **Effort:** med
- **Grade:** `ARITHMETIC` — verifiable by reading `commercial-strategy.md` L142–154
- **What:** The commercial plan's only risk register carries two columns (Risk, Owning discipline). **No likelihood, impact, time horizon, leading indicator, trigger threshold, or mitigation exists for any of the five rows.** Five risks are named and none is controlled. R2 additionally attributes its alarm-reduction premise to predictive intelligence when the published effect is produced by EHR↔pump **integration** (−50.3% hard-limit alerts, 96.1% DERS compliance), so the risk as written misses the actual defect. This finding is the methodological sibling of F-2: F-2 says the register is missing an entire *class* of risk; F-15 says the risks it does carry are uncontrolled.
- **Evidence:** `commercial-strategy.md` L142–154; `research-ai-connectivity-regulatory.md` §B.3, §B.5, §B.6.
- **Impact:** _Risk:_ no exposure is quantified, so nothing can be escalated, accepted, or closed on evidence. _Commercial:_ a diligence reviewer reads an uncontrolled register as an unmanaged program. _Regulatory:_ none directly — this register is not a regulated artifact, and it must not be confused with the ISO 14971 file.
- **Resolution proposal:** Re-author D-COMM-1.9 as a two-class register — execution risks (R1–R5) and competitive/exogenous risks (R6–R16) — with **published likelihood and impact scales** and, for every row, a leading indicator, a trigger threshold, separated preventive and contingent controls, a residual rating, and a named owner. Credit no mitigation that lacks an owner, an artifact and an acceptance criterion. The full specified register is in [`recs-risk-management.md`](recs-risk-management.md).
- **Owner / next step:** Commercial Lead with Risk Management — edit the source task and re-assemble.

### F-16: The ICU Medical unfiled-remedy precedent implies a change-control gate the program cannot currently build

- **Author:** agent:risk-management
- **Status:** open
- **Category:** Coverage
- **Severity:** high
- **Effort:** high
- **Grade:** `SUBSTANTIATED` — FDA Warning Letter CMS 702535; DHF nulls read from the discovery index
- **What:** A recall remedy is **by construction** a modification to a risk control measure. ISO 14971 requires risk control measures be verified for implementation *and* effectiveness, and any change re-evaluated for new or increased risks. So the control needed is a change-control gate whose filing trigger is *"does this change a risk control, or its performance?"*, wired to **both** a filing decision and an ISO 14971 re-evaluation. **The PP3500 cannot build that gate today**: `risk_management_plan`, `hazard_analysis`, `hazard_traceability_matrix`, `fmea`, `risk_management_report` and `benefit_risk_analysis` all resolve `null`, so there is nothing for the gate to look up. This is F-10 seen from the risk side: F-10 names the missing rule; F-16 names why the rule cannot yet be written.
- **Evidence:** `research-competitor-regulatory-record.md` claims 29–32; `pdlc-demo-dhf-discovery.json` `dhf_roles.pca-device`.
- **Impact:** _Risk:_ the single highest-consequence process failure in the competitor record has no corresponding control in our file. _Commercial:_ the quality-posture wedge cannot be claimed while our own file is emptiest exactly where the competitor failed. _Regulatory:_ adulteration/misbranding exposure, with FDA having foreclosed the label-disclosure shortcut.
- **Resolution proposal:** Sequence it — (1) author the risk management plan and hazard analysis; (2) write the change-control filing trigger against them, citing 21 CFR 807.81(a)(3)(i) and noting that a Special or Abbreviated 510(k) does not exempt §524B content; (3) pre-authorise an emergency-mitigation playbook using labeling/IFU/field-safety-notice controls that do not require a filing.
- **Owner / next step:** Quality Engineering with Regulatory Affairs and Risk Management.

### F-17: The PCCP detection→prediction constraint forecloses the D-COMM-1.1 wedge unless the predictive method is specified from the baseline

- **Author:** agent:risk-management
- **Status:** open
- **Category:** Probe-preempt
- **Severity:** high
- **Effort:** med
- **Grade:** `SUBSTANTIATED` for the guidance text (verbatim); `INFERRED` for the application to PP3500
- **What:** FDA's own worked example states that when a retrained model *"can now also predict physiologic instability in advance of its onset,"* and the methods for analysis, performance and statistics for predicting a future state were not pre-specified in the PCCP, **a new marketing submission is required.** The intended-use limit is statutory (FD&C §§515C(a)(2), 515C(b)(2)) and cannot be negotiated. **Consequence for the risk file:** if a predictive alarm is claimed as a risk control for the OIRD hazard, its **lead time and its sensitivity/specificity are the risk control's performance specification**, not marketing parameters. So the control must be specified in the hazard analysis with a stated performance envelope from the baseline; and any retrain that moves lead time or sensitivity is *simultaneously* a change to a risk control (requiring ISO 14971 re-verification) and a PCCP-scope question. **The PCCP Modification Protocol and the hazard traceability matrix must be authored against each other, not sequentially.** Writing the PCCP first and back-filling the hazard analysis is the failure mode. The SAD already defers exactly this question, so the decision is live and unmade.
- **Evidence:** `research-ai-connectivity-regulatory.md` §C.2, §C.3, §C.4; `pca-device-system-sad.md` §5 M3 and §8.
- **Impact:** _Risk:_ a risk control whose performance envelope is unspecified at baseline cannot be verified or re-evaluated when it changes. _Commercial:_ the five-year positioning throughline is stranded behind an unbudgeted second submission. _Regulatory:_ a PCCP scoped only to detection accuracy will not carry the predictive claim, and no Q-Sub can widen it.
- **Resolution proposal:** Before the PCCP section is drafted, pre-specify the predictive endpoint definition, lead-time claim, sensitivity/specificity acceptance and statistical analysis plan in the Modification Protocol — or record a written decision to file prediction separately, with schedule and budget. Cite the 2025-08-18 issue, not the superseded December 2024 date.
- **Owner / next step:** Regulatory Affairs with Risk Management.

### F-18: Cloud/AI on an opioid delivery device expands the hazard set well beyond what the SAD names

- **Author:** agent:risk-management
- **Status:** open
- **Category:** Coverage
- **Severity:** high
- **Effort:** high
- **Grade:** `SUBSTANTIATED` for the SAD text and the BD recall; `SUBSTANTIATED` for the proxy-activation and OIRD literature; `INFERRED` for the software-classification observation
- **What:** The SAD assigns M2 Safety Monitor *"the top-level hazard chains for occlusion, air embolism, overinfusion"* — all pump-mechanical. The hazards the connected/AI architecture introduces or amplifies are not named: **proxy activation** (defeats PCA's intrinsic consciousness interlock; 6,069 PCA errors and 460 harmful/fatal in USP MEDMARX per Joint Commission SEA 33); **opioid-induced respiratory depression** (97% of closed claims judged preventable with better monitoring, 77% ending in severe brain damage or death); **stale automated programming requests** — not hypothetical, this is BD's own Class I recall of 2025-02-18, in the connectivity layer rather than the pump; **drug-library push failure** from a SaMD three DHFs away; **model drift and automation complacency** — where a predictive alarm displacing intermittent nursing assessment creates a new failure path, and continuous monitoring *raises* measured event rates (41% bradypnea vs 1–2% under intermittent assessment), so a hospital installing this will see its numbers get worse before they get better. Separately, the bolus button — the surface of the most-cited PCA hazard — sits in M5 at IEC 62304 **Class B**, below the modules owning the mechanical hazards.

  **The load-bearing statement, phrased precisely.** None of this can be checked against the risk file because `hazard_analysis`, `fmea`, `hazard_traceability_matrix` and `benefit_risk_analysis` all resolve `null`. **The advisor is not claiming these hazards are absent from the file — it is reporting that the file does not exist to check**, which is the more serious statement.

- **Evidence:** `pca-device-system-sad.md` §4, §5; `research-pca-clinical-landscape.md` §B.1, §B.2, §B.3; `research-ai-connectivity-regulatory.md` §B.6; `research-competitor-regulatory-record.md` claim 22; `pdlc-demo-dhf-discovery.json`.
- **Impact:** _Risk:_ the connected-architecture hazard set is unmodelled, and it crosses DHF boundaries the composition manifest currently spans for cybersecurity only. _Commercial:_ the safety-architecture story that value-analysis committees and the liability record actually ask about cannot be told. _Regulatory:_ FDA's Infusion Pumps TPLC guidance expects a safety assurance case connecting design elements to safety mitigations; that case cannot be built from a null hazard analysis.
- **Resolution proposal:** Author the hazard analysis with the connected/AI hazards enumerated alongside the mechanical chains; re-test the M5 software safety classification against the proxy-activation hazard once modelled; extend the submission composition manifest so cross-DHF hazards have a named owning file rather than falling between `pca-device`, `connectivity-adapter` and `cloud-suite`.
- **Owner / next step:** Risk Management with Systems Engineering and Human Factors.

### F-19: Clinical evaluation file is script-generated shape with none of the device's named hazards

- **Author:** agent:clinical-affairs
- **Status:** open
- **Category:** Substantiation
- **Severity:** high
- **Effort:** high
- **Grade:** `SUBSTANTIATED` — every artifact read; the null grep result stated with its pattern, and independently re-run by the conductor
- **What:** `docs/project/dhfs/pca-device/clinical/` contains 5 CEPs, 5 BRAs, 5 literature-search records and a CER template — files whose own footers read *"Generated by … data generation script."* A case-insensitive grep of the whole tree for `proxy|respirator|capnograph|EtCO|end-tidal|naloxone|sedation` returns **zero matching files** (conductor-verified). The two hazards that define PCA harm in the published literature — **PCA-by-proxy** and **opioid-induced respiratory depression** — appear nowhere in the device's clinical evaluation. LSS-1001's PICO population is *chronic pain requiring long-term opioid therapy*, not the cleared acute-postoperative indication, and its Boolean omits every hazard term — so the search **would not retrieve** the Closed Claims analysis, McCarter, Overdyk, Ocay, or SEA 33. BRA-1001 asserts *"Level 1 evidence from RCTs"* with no study cited, carries `Device ID: DEV-1001` against frontmatter `device_ids: [DEV-PP3500]`, has empty `related_user_needs` / `related_design_inputs`, and lists *"Wireless connectivity enables remote monitoring and early intervention"* as a clinical benefit of a device with no monitoring capability.

  **This finding corrects `recs-commercial.md` §8**, which reported these roles as absent. They resolve `null` in the discovery index because its patterns look under `design-controls/`; the files exist under `clinical/`. **A populated folder of unusable records reads as coverage and is worse than an empty one** — the same lesson F-12 draws for cybersecurity.

- **Evidence:** `docs/project/dhfs/pca-device/clinical/` (full tree); CEP-1001; BRA-1001 L38, L65; LSS-1001 L32, L47; `research-pca-clinical-landscape.md` §B.1–B.2; `pdlc-demo-dhf-discovery.json`.
- **Impact:** _Clinical:_ no clinical evaluation of the hazards that actually cause harm on this device class. _Regulatory:_ an MDR/MEDDEV reviewer or ISO 13485 auditor opening these finds an evidence-grade `high` assertion with no evidence and a device-ID mismatch. _Commercial:_ the quality-posture wedge cannot be claimed from this file.
- **Resolution proposal:** Rebuild CEP + LSS around the cleared indication and the named hazards (re-execute the search with proxy / OIRD / capnography / programming-error terms; produce a PRISMA record); rebuild the BRA with SEA 33, Lee 2015 and Ocay 2018 as cited hazard basis; reconcile device IDs; populate the trace fields; strike or support the "Level 1 evidence" and "remote monitoring" assertions. Separately, **fix the discovery-index patterns so `clinical/` resolves** — the index defect is its own finding.
- **Owner / next step:** Clinical Affairs — rebuild CEP-1001 and LSS-1001 first as the pattern for the rest; raise the index-pattern fix with the `dhf-manifest` owner.

### F-20: PP3500 has no replacement interlock — intended use delegates it to staff vigilance the literature says fails

- **Author:** agent:clinical-affairs
- **Status:** open
- **Category:** Coverage
- **Severity:** high
- **Effort:** high
- **Grade:** `SUBSTANTIATED` for the artifacts and the competitor capability; `INFERRED` for the interlock argument
- **What:** PCA's intrinsic safety interlock is **the patient's own consciousness**, and the most-cited PCA hazard — proxy activation — defeats it (Ocay 2018: proxy dosing *"negates a key safety measure of PCA use which is that a sleeping or sedated patient will not press the PCA button"*). `user-needs.md` L22/L26 states the device is *"intended for use in supervised acute-care environments where qualified clinical staff are available to monitor the patient and respond to alarms,"* and its nine functional groups contain **no physiological-monitoring group and no closed-loop response**. That delegates the replacement interlock to intermittent nursing assessment — the control Overdyk 2007 showed detects bradypnea at **1–2% where continuous monitoring detects 41%**, and the control McCarter 2008 showed alarmed in **zero of nine** events that capnography caught. Meanwhile BD's Alaris EtCO₂ Module *"pauses a PCA infusion if the patient's respiratory status falls below hospital-defined limits."*

  **Bounding the finding honestly:** this is a **value-analysis and liability exposure, not a clearance exposure.** The regulatory floor is CMS's 2012 intermittent q2–2.5 h suggestion, Joint Commission SEA 49 is retired (Feb 2019), no AAMI standard was located, and nothing requires integrated monitoring for lawful sale. Clinical Affairs' answer to the question posed by the commercial advisor is therefore two-part and pulls both ways: **yes**, PCA Pause + EtCO₂ is monitoring-driven intervention for the OIRD hazard; **no**, capnography during PCA is not standard of care. Both halves must appear in any rewrite of D-COMM-1.1.

- **Evidence:** `user-needs.md` L22, L26, L48–L58; `research-pca-clinical-landscape.md` §B.1, §B.3, §B.4, §B.5; `state-of-the-art-analysis.md` L39/L52; `commercial-strategy.md` L34/L36.
- **Impact:** _Clinical:_ the device's safety case rests on a control with documented poor sensitivity, and the residual risk is analysed nowhere. _Commercial:_ our differentiation is measured against a monitored incumbent baseline, not against nothing — which narrows the F-1 wedge further. _Regulatory:_ adding an interlock may or may not sit inside K210345 — unresolved.
- **Resolution proposal:** Author a Clinical Affairs position on the replacement interlock stating (a) whether PP3500 provides, integrates to, or documents reliance on institutional monitoring; (b) the benefit-risk consequence of each; (c) explicitly that continuous monitoring is a society expectation not a requirement, so the team is not misled in either direction. Route the filing consequence to Regulatory.
- **Owner / next step:** Clinical Affairs → Systems Engineering + Risk Management → Regulatory Affairs.

### F-21: Two clinical claims must be struck outright; four more cannot be used comparatively as written

- **Author:** agent:clinical-affairs
- **Status:** open
- **Category:** Substantiation
- **Severity:** high
- **Effort:** med
- **Grade:** `UNVERIFIED` / `INTERNAL-DEMO` for the claims; `SUBSTANTIATED` for the published benchmarks they fail against
- **What:** **Strike now:** (1) *"60% adverse event reduction … at Mass General Brigham, Mayo Clinic"* — twelve query variants including institution-restricted searches found nothing; it attaches an unsourced outcome to two real health systems for a capability we do not have, and D-COMM-1.5 consumes it as the reimbursement argument. (2) *"Zero wrong-medication errors since implementation"* — no denominator, no period, no surveillance method; voluntary reporting is the least sensitive ascertainment available; barcode scanning suppresses its own numerator; single-KOL attribution **to a KOL never contacted — and that KOL's own profile records a 0.25% PCA error rate, i.e. non-zero.** **Restate before any comparative use:** the VAS 8.1→1.9 figure (a within-patient change presented alongside superiority language; Cochrane's between-arm figure is ~0.9 points on 0–10 — a ~7× category mismatch); the 94% satisfaction figure (a modality property — Cochrane 81% vs 61% — that any compliant PCA pump inherits, with no comparative information in a single-arm design); the 98.7% task-success rate (wrong metric shape — HF validation asks which use errors had harm potential, not what fraction passed; an aggregate conceals which 1.3% failed and whether those were critical tasks); the 80% barcode figure (published BCMA effects cluster at **41–55%** — Poon 2010 *NEJM* 41.4%, Thompson 2018 43.5% / 55.4% harm reduction).
- **Evidence:** `competitive-product-assessment.md` L14, L24, L25, L29, L30, L46, L81; `KOL-0006-paul-james.md` L41, L46; `research-ai-connectivity-regulatory.md`; `research-pca-clinical-landscape.md` §C; McNicol 2015; Poon 2010; Thompson 2018.
- **Impact:** _Clinical:_ the claim set addresses neither the regulator nor the buyer. _Commercial:_ the 60% figure is a live dependency in D-COMM-1.5's health-economics deliverable. _Regulatory/Legal:_ named-institution attribution of an unsourced outcome, and an absolute-zero safety claim, are the two highest-exposure sentences in the input analyses.
- **Resolution proposal:** Delete the two; restate the four with design, n, sites, period, instrument, and an explicit within-patient vs between-arm label; replace the 98.7% aggregate with a critical-task / use-error framing; cite Poon and Thompson for barcode. Apply fixes to the source task, not the assembled strategy.
- **Owner / next step:** Clinical Affairs (restatement) with Commercial + Legal (deletion sign-off) — **before any external use.**

### F-22: KOL roster is uncontacted and mis-specialised for the populations that retain IV PCA

- **Author:** agent:clinical-affairs
- **Status:** open
- **Category:** Methodology
- **Severity:** high
- **Effort:** med
- **Grade:** `SUBSTANTIATED` for the engagement status and the sentiment misattribution (conductor-verified, 8 of 8); `INFERRED` for the specialty-coverage gap
- **What:** All eight KOL profiles read `Current Status: None - Not yet contacted`, `Last Interaction: None`, `Internal Notes: No notes recorded.` The **"+0.55 vs +0.16"** sentiment figures cited in D-COMM-1.1 as KOL validation **do not come from these people** — they come from a **28-expert (18 verified) market-research panel** on **general infusion**, for **AI-driven personalization**. That is a double substitution: wrong panel, wrong therapy context. This was raised as **F-1 in the `commercial-roadmap-kol-review` cluster and remains `Status: open`** — a recurrence across two analyses, which is itself the finding. Second, unnamed anywhere: the roster covers smart-pump usability, paediatric medication safety, human factors, infusion nursing, alert fatigue and one PCA/acute-pain expert — and contains **no sickle-cell physician, no burn clinician, no obstetric anaesthetist, and no palliative-care physician.** If IV PCA's retained demand sits in those populations (F-6), the roster is specialised for the segment the plan is being advised to de-emphasise and silent on the one it would move toward.
- **Evidence:** `kol-feedback/KOL-0001…0008` (8/8, conductor-verified); `kol-feedback/README.md` roster; `competitive-product-assessment.md` L18, L33; `commercial-strategy.md` L36; `commercial-roadmap-kol-review.md` L221–L233; `research-pca-clinical-landscape.md` §A.4.
- **Impact:** _Clinical:_ every user need, design input and roadmap feature anchored on "KOL validation" rests on a specialty match, not a recorded opinion — and a CER reviewer will not accept uncollected opinion as clinical input. _Commercial:_ no "KOL-validated" claim is currently supportable. _Strategic:_ the roster cannot inform the segment-1 re-targeting decision because it has no voice from the retained-indication populations.
- **Resolution proposal:** Re-label "+0.55 / +0.16" at every occurrence as market-panel sentiment on general infusion; mark each profile as opinion-collected (dated note) or opinion-not-collected; run the interviews before the roadmap is used externally; extend the roster with at least one candidate each in sickle-cell/haematology, burns, obstetric anaesthesia and palliative care. Close or date-stamp the non-closure of the prior analysis's F-1.
- **Owner / next step:** Clinical Affairs — interviews scheduled before the Y1 commit; roster extension in the same pass.

## Recommendations

1. **Quarantine the comparative claim set before any external use.** Banner all three input-analysis files as not cleared for external use pending substantiation; disposition each claim in F-3 individually with a named owner and date. _(Owner: Commercial Lead + Marketing + Regulatory Affairs)_
2. **Re-found D-COMM-1.1 on the corrected competitive baseline** — no cleared AI-enabled pump anywhere, and an incumbent monitored-interlock capability that does exist. Edit the source task and re-assemble; never hand-edit the assembled strategy. _(Owner: Commercial Lead)_
3. **Add the exogenous risk class (R6–R10) to D-COMM-1.9** with owning discipline, leading indicator and trigger threshold each, and relabel R1–R5 as execution risks. _(Owner: Commercial Lead + Risk Management)_
4. **Strike, do not soften, the "60% adverse-event reduction at Mass General Brigham, Mayo Clinic" claim** — it names two real institutions and has no source across 12 query variants — and re-found D-COMM-1.5's cost-avoidance argument on evidence we hold. _(Owner: Commercial Lead + Health Economics)_
5. **Re-benchmark the F7 ambulatory extension to ICU Medical's current CADD line** under product code MEA, retaining Omnipod and Tandem explicitly as industrial-design references only. _(Owner: Commercial Lead + Regulatory Affairs)_
6. **Add a Commercial-gate column to D-COMM-1.3** carrying a Y1 GPO contract-award milestone and a per-year fleet-replacement targeting window, and add contract coverage to D-COMM-1.7's stage-gates. _(Owner: Commercial Lead + Program Manager)_
7. **Convert the quality-posture wedge from a claim into an evidenced asset** — it is the only wedge resting on substantiated competitor facts, and it is precisely where the `pca-device` DHF is emptiest. Decide what must exist before the claim is externally defensible. _(Owner: Quality Engineering + Regulatory Affairs)_
8. **Commission a targeted retrieval of Bykov 2021** (Premier database, 6M+ surgical inpatients) plus a search for NIS/Premier analyses of IV-PCA *route* utilisation 2015–2024. This single artifact would move the central PCA-narrowing thesis from `INFERRED` to `SUBSTANTIATED`. _(Owner: Clinical Affairs)_
9. **Correct the standards matrix.** IEC 60601-2-24 is not FDA-recognized and ANSI/AAMI ID26 is withdrawn — there is currently no FDA-recognized particular safety standard for infusion pumps. Cite **AAMI TIR101:2021** (recognition 6-482) instead, add the interoperability standards (UL 2800-1:2022 family; ANSI/AAMI 2700-1:2019), and schedule the **safety assurance case** the Infusion Pumps TPLC guidance expects. _(Owner: Regulatory Affairs)_
10. **Correct the product code.** The device record assigns **LZH**, which FDA defines as "Pump, Infusion, Enteral." Fix it, make the MEA-vs-FRN-vs-PHC election an explicit strategy decision, and rewrite Q-Sub Q1.3 to name the proposed code rather than asking open-ended. _(Owner: Regulatory Affairs)_
11. **Correct the false evidence assertion in the Q-Sub composition manifest — this week.** It states "Per-component evidence exists" as the reason for excluding the system-level cybersecurity assessment. The per-component evidence is unfilled templates. A false claim in a submission-composition document is different in kind from an empty folder: it is a statement a reviewer can hold the program to. _(Owner: Regulatory Affairs + Cybersecurity)_
12. **Refresh the cybersecurity reference stack before authoring anything from it.** Both the registry distillation and the project applicability file are pinned to the September 2023 guidance; the operative edition is February 3, 2026. Anything authored from the stale tier inherits the defect. _(Owner: Regulatory Affairs)_
13. **Close the three risk-management roles that gate everything else.** `risk_management_plan`, `hazard_analysis` and `hazard_traceability_matrix` resolve `null` — and F-12, F-16 and F-18 all depend on them. **One absence disables three mitigations**; closing it is the highest-leverage single action in this analysis. _(Owner: Quality Engineering + Risk Management)_
14. **Fix the discovery-index role patterns.** They resolve `clinical/` artifacts to `null` because they look under `design-controls/`, which caused one advisor to report present-but-unusable files as absent. Separately, they report `exists: true` for template stubs. **Role resolution is not content** — any dashboard keyed on it currently overstates readiness. _(Owner: whoever owns `dhf-manifest`)_

## Cross-discipline handoffs

_Items this analysis needs from other disciplines to close. Aggregated across advisors._

| # | Question | Owning discipline | Why blocked here |
|---|---|---|---|
| 1 | Does BD's Alaris PCA Module labeling confirm the PCA Pause + EtCO₂ capability, and is capnography monitoring during PCA now standard of care? | Clinical Affairs | Determines whether our differentiation is measured against "nothing" or an established monitored baseline. Governs how D-COMM-1.1 must be rewritten. |
| 2 | Can BD, Baxter or ICU Medical add predictive alarming to an installed fleet under an existing change-control envelope without a new 510(k)? | Regulatory Affairs | Sets the duration of the entire D-COMM-1.1 wedge and the severity of risk R6. If yes, the moat is a release cycle. |
| 3 | Would an ambulatory PP3500-A file under product code MEA against CADD-class predicates, and does that constrain the indications F7 can claim? | Regulatory Affairs | Determines whether F-4's re-benchmark is merely commercially right or also regulatorily binding. |
| 4 | Is the 15–30 minute predictive-warning claim transferable from general infusion to opioid-induced respiratory depression in PCA? | Clinical Affairs | This is R1. Commercial cannot price or position a claim whose clinical transferability is unestablished. |
| 5 | Which specific DHF artifacts must exist before a quality-posture claim is externally defensible, and what is the timeline to close the `null` roles? | Quality Engineering | The wedge with the strongest evidence is the area with the emptiest file. |
| 6 | What field-performance denominator (units × months in service) exists, and does complaint/CAPA data support any externally citable reliability claim? | Post-Market Surveillance | Without a denominator, "no recalls" is a low-exposure artifact, not a quality claim. |
| 7 | Do FTC substantiation standards, Lanham Act exposure and FDA promotional-claim limits apply to the F-3 claims — and which must be struck versus re-scoped? | Legal + Regulatory Affairs | Frameworks were named without verifying any provision (`UNVERIFIED`). The methodology finding stands independently; the disposition decision does not belong to this analysis. |

## Self-review checklist

- [x] **Aggregate counts re-verified** against the underlying research files, not just their summaries.
- [x] **Every arithmetic claim independently recomputed** by the conductor (CAGRs, 9,567,700 ÷ 1,547, 127,500 ÷ 30, 150 ÷ 7, 150 ÷ 4).
- [x] **Every "our own document contradicts itself" claim re-read at the cited line** in the source file.
- [x] **KOL contact status re-grepped** — all 8 profiles confirmed "Not yet contacted."
- [x] **Charts visually verified** by screenshot on both console surfaces (light `#ffffff`, dark `#1e293b`), not merely written.
- [x] **Chart palette validated** with the `dataviz` validator against those exact surfaces; red/green severity encoding rejected on a measured deuteranopia failure (ΔE 4.1).
- [x] **Two briefing premises corrected** where a research agent refuted them (Alaris return-to-market date; the non-existent ICU Medical/Smiths divestiture) rather than carried forward.
- [x] **Cross-discipline handoffs section present.**
- [ ] **Standards-designation drift check** — pending Regulatory Affairs confirmation of what should replace IEC 60601-2-24 in the standards matrix.

## Open Questions

- Is the "9,567,700 annual IV pumps" figure a revenue amount, as the arithmetic implies? Closing evidence: the source PDF behind `state-of-the-art-analysis.md`.
- Does a national IV-PCA *route* utilization time-series exist for 2015–2024? Closing evidence: Bykov 2021 full text (Premier, 6M+ surgical inpatients) plus an NIS/Premier route analysis. This is the highest-value single retrieval in the whole assessment.
- What is ICU Medical's **current** ambulatory-PCA product line, and does CADD-Solis remain actively marketed? Closing evidence: a full openFDA sweep on product code MEA plus ICU Medical product literature.
- Does a hospital already running continuous ward monitoring from a patient-monitoring vendor treat pump-integrated capnography as duplicative? This is the pivotal commercial question for the monitored-interlock strategy, and no source addressing it was found.
- Should the `gap-analysis` skill's `data/topic-advisor-map.yml` gain a `competitive` topic? This analysis ran with a freeform topic because the map carries no competitive/commercial entry, and its natural advisor set (commercial primary; regulatory-affairs, clinical-affairs, risk-management, cybersecurity consulting) is stable enough to encode.

## References

- **Standards / guidance:** FDA, *Predetermined Change Control Plans for Medical Devices* (final, 2025-08-18); FD&C Act §515C; §524B (Consolidated Appropriations Act 2023 §3305); FDA premarket cybersecurity guidance (reissued 2025-06, 2026-02); IEC 81001-5-1; IEC 62366-1. **Note:** IEC 60601-2-24 is *not* FDA-recognized and ANSI/AAMI ID26 is withdrawn.
- **FDA records:** AI-Enabled Medical Device List (1,524 rows, current 2026-06-16); product codes MEA, FRN, PHC; K211218, K243855 (BD); K111275, K982839 (CADD lineage); K162165 (most recent MEA); warning letter CMS 702535 (ICU Medical, 2025-04-04).
- **Literature:** ERAS Society colorectal guidelines (2025, 2018); McNicol 2015 Cochrane (PCA satisfaction, VAS); Poon 2010 *NEJM* and Thompson 2018 (barcode medication administration); Lee 2015 (OIRD closed claims); ASHP National Survey 2021 (interoperability adoption).
- **Internal artifacts:** `commercial-strategy.md` D-COMM-1.1…1.9; `regulatory-strategy.md`; the three input-analysis documents; `pdlc-demo-dhf-discovery.json`; the 8 KOL profiles.
- **Full citation trails** live in the four `research-*.md` files, each of which records its own grade counts and its own "what could not be verified" table.

## Changelog

| Date | Author | Summary |
|------|--------|---------|
| 2026-08-05 | human:Ben Xavier (task ben/113) | Analysis scaffolded; evidence-grade contract defined; four research agents commissioned to build the public-source evidence base before any advisor reasoned. |
| 2026-08-05 | agent:commercial | Commercial assessment → `recs-commercial.md`. Contributed F-1…F-6. Found the 9,567,700 ÷ 1,547 = $6,185 units error, the battery-claim self-contradiction, the three-way accuracy inconsistency, the endogenous-only risk register, and the Omnipod-vs-CADD benchmarking category error. |
| 2026-08-06 | agent:regulatory-affairs | Regulatory assessment → `recs-regulatory-affairs.md`. Contributed F-7…F-11. Established that the commercial roadmap commits against regulatory decisions the regulatory strategy has not made; that F4/F5 are mis-categorised as PCCP-authorized against the statutory §515C limit; that the F6 PCCP dependency is inverted per Appendix B Scenario 2; that De Novo has never been evaluated despite a nine-year predicate drought; that the standards matrix anchors on a non-recognized standard while omitting every recognized one; and that the device record carries **LZH ("Pump, Infusion, Enteral")** for a PCA pump. |
| 2026-08-06 | agent:cybersecurity | Cybersecurity assessment → `recs-cybersecurity.md`. Contributed F-12…F-14. Established that `cybersecurity_plan` resolves `null` across all ten DHFs and that threat-model and SBOM roles resolve `exists: true` to unfilled QMS templates — **role resolution is not content**. Identified the false "per-component evidence exists" assertion in the Q-Sub manifest, the two-supersession staleness of both reference tiers, the broken SPDX/CycloneDX "required" claim, and the collision between the Year-1 connected roadmap and an unresolved Adapter→Cloud trust boundary. Declined to treat the ICU Medical wireless-module recall as cybersecurity evidence. |
| 2026-08-06 | agent:risk-management | Competitive-threat risk register → `recs-risk-management.md`. Contributed F-15…F-18. Published business-exposure scales explicitly distinct from the ISO 14971 harm scales; assessed R1–R5 as uncontrolled; **re-founded the commercial advisor's R6** (its premise that incumbents could ship predictive alarming cheaply is refuted — the real pre-emption is BD's already-cleared *deterministic* interlock); added R11–R16; documented five compound exposures; identified three couplings into the ISO 14971 file; named five risks judged not mitigable. |
| 2026-08-06 | agent:clinical-affairs | Clinical assessment → `recs-clinical-affairs.md`. Contributed F-19…F-22. **Corrected `recs-commercial.md`** on the clinical-file nulls (present under `clinical/`, missed by the index patterns) and **flagged the ERAS-2025 conflict between two research files**, recommending the unconfirmed guideline quotation be withdrawn — both absorbed above. Established that the clinical tree contains zero references to PCA-by-proxy or OIRD, that the literature-search PICO does not match the cleared indication, and that `user-needs.md` delegates the replacement safety interlock to staff vigilance. |
| 2026-08-06 | human:Ben Xavier (task ben/113) | Conductor pass: independently re-verified the load-bearing arithmetic (all CAGRs; 9,567,700 ÷ 1,547; 127,500 ÷ 30; 150 ÷ 7 and ÷ 4), the KOL contact status (8/8), the clinical-tree hazard-term absence, the cybersecurity stub sizes and placeholder counts, the Q-Sub manifest assertion, and the LZH/MEA/FRN product-code definitions via openFDA. Absorbed both inter-advisor corrections. Added the five visualizations. |
