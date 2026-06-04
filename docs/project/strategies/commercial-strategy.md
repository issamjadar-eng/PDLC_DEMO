# Commercial Strategy

<!-- Assembled: 2026-06-03 by /strategy assemble -->
<!-- Domain: commercial -->
<!-- Sources: ben/080 -->

> This document is auto-assembled from `<!-- STRATEGY CONTENT: commercial, ... -->` tags in task documents.
> Do not edit directly — update the source task and run `/strategy assemble commercial`.
> Unresolved items are marked with [VERIFY].

## Scope & Approach

This shared commercial strategy covers the **5-year go-to-market plan for the PainEase PP3500 program** — the cleared PCA pump (K210345) and the modular Cloud Suite / Connectivity Adapter components that surround it. It records the cross-component commercial decisions (positioning, segmentation, launch sequencing, feature roadmap, pricing/reimbursement, channel/geography, business case, competitive positioning, and program risks) that inform the formal Go-to-Market plan, Business Case, and Market-Expansion plan.

The strategy is grounded in the project's own input analysis — market/competitive research, the 8-member KOL roster, and the component classification already fixed in [regulatory-strategy.md](regulatory-strategy.md) and [architecture-strategy.md](architecture-strategy.md). Every market figure traces to `docs/project/input-analysis/`; every feature names its component (per `project.yml dhfs[]`) and its regulatory vehicle. The roadmap is deliberately written with its seams exposed (the R1–R5 risk decision) so it can be stress-tested by clinical/KOL review.

## Plans Informed

| Formal Plan | DHF | How This Strategy Informs It |
|------------|---------|------------------------------|
| Go-to-Market plan | pca-device (lead) + Cloud Suite components | Market entry sequence, launch phasing, channel + segment targeting |
| Business Case | program-wide | Revenue model, pricing/subscription mix, IRR/NPV underwriting targets |
| Market Expansion | pca-device + future variants | New indications (home/ambulatory), geographies (EU MDR / Canada) |

_The DHF column identifies which DHF each formal plan lives under — formal outputs remain per-DHF under `docs/project/dhfs/<dhf>/...` even though the upstream strategy is shared._

## Strategy Decisions

_Each strategic topic is a level-2-equivalent decision below. Per-component nuance is carried inline (PCA device vs Cloud Suite vs ambulatory variant). Decisions are wrapped in `D-COMM-*` sentinels for stable addressing by the project-console and downstream tooling._

<!-- DECISION:start id=D-COMM-1.1 status=active source=ben/080 created=2026-06-03 last-edited=2026-06-03 -->
### 5-Year Commercial Vision & Positioning

**Decision**: Position the PainEase PP3500 program as the **safety-and-intelligence leader in patient-controlled analgesia**, evolving over five years from a best-in-class standalone PCA pump (cleared K210345) into a **connected, AI-assisted acute-pain platform** spanning hospital and home settings. The strategic throughline is: *close the one decisive competitive gap — the complete absence of predictive monitoring — while monetizing the modular Cloud Suite and an ambulatory form factor.*

**Why**: The competitive assessment is unambiguous that PP3500 already wins on the hardware fundamentals (150+ hr battery = 50% over typical; ±0.5% volumetric accuracy vs ±2.3% for Alaris/Spectrum IQ; 94% patient satisfaction; 80%+ wrong-med error reduction with barcode scanning) but that the **single largest competitive gap across the whole portfolio is the absence of predictive monitoring** — market leaders (BD Alaris, Baxter Spectrum IQ) are reactive-alarm only, while AI-enabled entrants demonstrate 15–30 min early warnings. The AI-enabled device market grows $15.1B → $98.3B (2023→2028, ~45% CAGR); AI-driven personalization is the highest-priority opportunity in our own KOL research (sentiment **+0.55** vs +0.16 baseline). Defending the PCA franchise means owning intelligence, not just hardware.

**How to apply**: Every roadmap release is justified against one of three positioning pillars — (1) **Safety leadership** (opioid-specific guardrails, predictive deterioration/occlusion warnings), (2) **Connected operations** (fleet, drug-library cadence, telemetry — the Cloud Suite monetization engine), (3) **Care-setting expansion** (ambulatory/home PCA). Marketing claims trace to cleared evidence; anything predictive ships only after its SaMD clears or rides the PCCP envelope.
<!-- Source: ben/080, "5-Year Commercial Vision & Positioning", last modified 2026-06-03 -->
<!-- DECISION:end id=D-COMM-1.1 -->

<!-- DECISION:start id=D-COMM-1.2 status=active source=ben/080 created=2026-06-03 last-edited=2026-06-03 -->
### Market Segmentation & Customer Targeting

**Decision**: Prioritize three buyer segments in sequence: **(1) Acute-care hospitals** (anesthesia / acute pain services, the installed-base defenders — primary through Years 1–3); **(2) Health-system pharmacy & biomed** (the Cloud Suite buyer — drug-library governance, fleet management, surveillance — Years 2–4); **(3) Home-infusion & ambulatory-surgery providers** (the care-setting-expansion buyer — Years 3–5, riding the $28.4B→$54.8B home-infusion market at 12.8% CAGR).

**Why**: The KOL roster maps directly onto these segments and tells us where the credibility is. Acute-pain anesthesiologists ([KOL-0006 James Paul](../input-analysis/kol-feedback/KOL-0006-paul-james.md)) and the alarm-fatigue cluster (Giuliano KOL-0001, Shah KOL-0008, Kirkendall KOL-0002) are the hospital pull; pharmacy DERS expertise (Kuitunen KOL-0004) and infusion-nursing standards (Gorski KOL-0007) anchor the pharmacy/biomed buyer; human-factors depth (Pennathur KOL-0005) de-risks the home/ambulatory leap where the user is a patient or family caregiver, not a trained nurse. Selling intelligence (segment 2/3) before the safety story is proven in the installed base would overextend the brand.

**How to apply**: Year-1 commercial motion = installed-base retention + barcode/drug-library attach. Sequence Cloud Suite upsell to existing PP3500 accounts before net-new. Home/ambulatory enters only after the connected story is referenceable.
<!-- Source: ben/080, "Market Segmentation & Customer Targeting", last modified 2026-06-03 -->
<!-- DECISION:end id=D-COMM-1.2 -->

<!-- DECISION:start id=D-COMM-1.3 status=active source=ben/080 created=2026-06-03 last-edited=2026-06-03 -->
### 5-Year Launch Sequencing & Phasing

**Decision**: Phase the program into five annual waves, anchored to the FDA cadence the market analysis recommends (pre-submission Month 12, ambulatory market entry Month 24, AI predictive-monitoring full launch Month 30):

| Year | Theme | Regulatory vehicle | Headline releases |
|---|---|---|---|
| **Y1 (2026)** | Defend & connect the base | Letter-to-File / PCCP envelope (within K210345) | Drug Library Manager GA (SaMD); Connectivity Adapter GA (MDDS); Fleet Management + Telemetry dashboards |
| **Y2 (2027)** | Smart alarms & pharmacy governance | **Q-Sub (M12)** → PCCP-authorized SaMD | Alerts Engine v1 (alarm-fatigue reduction SaMD); Clinical Surveillance app; drug-library analytics |
| **Y3 (2028)** | Predictive monitoring | **New 510(k)** (predictive SaMD) + PCCP for retraining; **ambulatory entry (M24)** | Predictive occlusion/infiltration & deterioration warnings (Alerts Engine v2); ambulatory PP3500-A hardware pilot |
| **Y4 (2029)** | Personalized analgesia & home PCA | PCCP retraining + new indication filing (home) | Dose-personalization decision support; ambulatory PP3500-A GA; home-infusion integration |
| **Y5 (2030)** | Platform & autonomy ceiling | PCCP-at-cadence + selective 510(k)s | Closed-loop-assist research track; multi-site analytics; international (EU MDR / Canada) expansion |

**Why**: This sequencing front-loads the cheap, high-certainty wins (Cloud Suite apps that monetize the existing cleared pump) and defers the capital-intensive, regulatorily-heavy predictive-AI and ambulatory-hardware bets until the connected base and the pharmacy relationship are established. It mirrors the market analysis's own recommended cadence and keeps each year's flagship release gated behind the prior year's clearance/evidence.

**How to apply**: Treat the Year column as the commit boundary for the business case below; treat the Regulatory vehicle column as the dependency on [regulatory-strategy.md](regulatory-strategy.md) (Critical-Requirement Carve-out + PCCP envelope). A feature slips a year rather than shipping ahead of its regulatory vehicle.
<!-- Source: ben/080, "5-Year Launch Sequencing & Phasing", last modified 2026-06-03 -->
<!-- DECISION:end id=D-COMM-1.3 -->

<!-- DECISION:start id=D-COMM-1.4 status=active source=ben/080 created=2026-06-03 last-edited=2026-06-03 -->
### Feature Roadmap (release-by-release)

**Decision**: The roadmap commits to the following named features, each mapped to a Cloud Suite / device component (per `project.yml dhfs[]`) and a regulatory category (A = Letter-to-File; B = PCCP-authorized; C = new submission):

| # | Feature | Component | Year | Reg. category | Positioning pillar | KOL anchor |
|---|---|---|---|---|---|---|
| F1 | Drug Library Manager GA — pharmacist-authored DERS, 200+ med library | `drug-library-manager` (SaMD) | Y1 | C (own 510k/accessory) | Safety | Kuitunen, Paul |
| F2 | Connectivity Adapter GA — on-prem HL7 v2.5 / FHIR R4, PHI-in-hospital | `connectivity-adapter` (MDDS) | Y1 | A (MDDS, non-device) | Connected | Gorski |
| F3 | Fleet Management + Telemetry dashboards | `fleet-management`, `analytics-dashboard` (non-device) | Y1 | A | Connected | — |
| F4 | Alerts Engine v1 — smart alarm filtering / alert-fatigue reduction | `alerts-engine` (SaMD) | Y2 | B (PCCP) | Safety | Shah, Giuliano, Kirkendall |
| F5 | Clinical Surveillance — near-miss & alarm analytics | `clinical-interface` (SaMD) | Y2 | B | Safety | Kirkendall |
| F6 | Predictive monitoring — occlusion / infiltration / deterioration early-warning | `alerts-engine` v2 (SaMD) | Y3 | C (new 510k) + PCCP retraining | Safety | Giuliano, Paul |
| F7 | Ambulatory PP3500-A — lightweight wearable PCA hardware | `pca-device` (new variant) | Y3→Y4 | C (new clearance + home indication) | Care-setting | Pennathur, Paul |
| F8 | Dose personalization decision-support | `alerts-engine` / `clinical-interface` (SaMD) | Y4 | C + PCCP | Safety | Paul, Kuitunen |
| F9 | International expansion (EU MDR / Canada) | program-wide | Y5 | EU MDR / Health Canada | Care-setting | Kuitunen (EU), Paul (Canada) |

**Why**: The feature set is mined directly from the competitive gap (predictive monitoring, F6), the highest-KOL-sentiment opportunity (AI personalization, F8, +0.55), the modular component portfolio already classified in [regulatory-strategy.md](regulatory-strategy.md) (F1–F5), and the home-infusion TAM (F7). Each feature names its KOL anchor so the gap-analysis KOL review has a concrete claim to evaluate.

**How to apply**: This table is the canonical feature commitment. The KOL gap-analysis critiques *this table* — sequencing realism, evidence sufficiency, alarm-fatigue claims, and home-PCA safety. Engineering reads the Component column to map features to DHFs.
<!-- Source: ben/080, "Feature Roadmap (release-by-release)", last modified 2026-06-03 -->
<!-- DECISION:end id=D-COMM-1.4 -->

<!-- DECISION:start id=D-COMM-1.5 status=active source=ben/080 created=2026-06-03 last-edited=2026-06-03 -->
### Pricing & Reimbursement

**Decision**: Adopt a **razor + recurring-software** model: the PP3500 (and later PP3500-A) hardware carries a capital price competitive with Alaris/Spectrum IQ, while the Cloud Suite SaMDs (Drug Library Manager, Alerts Engine, Clinical Surveillance, predictive monitoring) are sold as **per-pump / per-bed annual subscriptions**. Reimbursement strategy leans on **cost-avoidance** (adverse-event reduction, alarm-fatigue labor savings) rather than direct procedure reimbursement, because PCA delivery is bundled into the surgical/inpatient DRG.

**Why**: PCA infusion is not separately reimbursed — the buyer's economic case is avoided harm and nursing efficiency, exactly what the evidence base quantifies (60% adverse-event reduction, 35% alert reduction, 80% IV-med-error reduction). A subscription model captures the recurring value of the Cloud Suite and funds the $24M / 42-month predictive-monitoring development out of installed-base revenue rather than a single capital sale.

**How to apply**: Year-1 list price holds the hardware franchise; Cloud Suite attach rate is the Year-2+ growth lever. Health-economics dossiers (cost-avoidance models) are a Year-1 commercial deliverable, not an afterthought — they are the reimbursement argument.
<!-- Source: ben/080, "Pricing & Reimbursement", last modified 2026-06-03 -->
<!-- DECISION:end id=D-COMM-1.5 -->

<!-- DECISION:start id=D-COMM-1.6 status=active source=ben/080 created=2026-06-03 last-edited=2026-06-03 -->
### Channel & Geographic Expansion

**Decision**: **US direct + GPO/IDN contracting first** (Years 1–3), then **EU MDR and Health Canada** (Years 4–5), prioritizing markets where the KOL footprint already extends (Finland/EU via Kuitunen KOL-0004; Canada via Paul KOL-0006). Home/ambulatory (F7) goes to market through **home-infusion specialty pharmacy and ambulatory-surgery-center channels**, distinct from the acute-care hospital sales motion.

**Why**: The cleared device is K210345 (US). EU MDR (12–18 month CE-mark timelines) and Canada are deliberately deferred until the connected + predictive story is referenceable, so international launches lead with the differentiated platform rather than a me-too pump. Channel bifurcation (hospital direct vs home-infusion specialty) reflects genuinely different buyers.

**How to apply**: International filing sequence is a dependency on [regulatory-strategy.md](regulatory-strategy.md) §3 (Jurisdictional Differences — currently unpopulated; flagged as an open item the roadmap depends on). Home channel build-out begins in Year 3 ahead of the F7 GA.
<!-- Source: ben/080, "Channel & Geographic Expansion", last modified 2026-06-03 -->
<!-- DECISION:end id=D-COMM-1.6 -->

<!-- DECISION:start id=D-COMM-1.7 status=active source=ben/080 created=2026-06-03 last-edited=2026-06-03 -->
### Business Case & Revenue Model

**Decision**: Underwrite the program to the portfolio economics in the market analysis: **combined revenue potential ~$350M annually by Year 5, portfolio-level IRR ~58%, NPV ~$425M**, with the AI-predictive-monitoring line item alone carrying $180–240M revenue at **68% IRR over 42 months against a $24M investment**. Treat these as the demo program's underwriting targets, not guarantees.

**Why**: These figures are the project's own input-analysis numbers (`docs/project/input-analysis/`) and give the roadmap a quantified spine the KOL review and the business case can interrogate. The recurring-software model (above) is what makes the Year-5 revenue durable rather than one-time capital.

**How to apply**: Each annual wave is a stage-gate — fund Year N+1 features against Year N attach-rate and evidence milestones. The $24M predictive-monitoring spend is gated behind Year-1/Year-2 Cloud Suite traction. _[VERIFY] Revenue/IRR/NPV figures are demo input-analysis estimates — substantiate against an independent financial model before any real business-case use._
<!-- Source: ben/080, "Business Case & Revenue Model", last modified 2026-06-03 -->
<!-- DECISION:end id=D-COMM-1.7 -->

<!-- DECISION:start id=D-COMM-1.8 status=active source=ben/080 created=2026-06-03 last-edited=2026-06-03 -->
### Competitive Positioning

**Decision**: Position explicitly **against the reactive-alarm incumbents** (BD Alaris, Baxter Spectrum IQ, B. Braun, ICU Medical Plum 360) on the predictive axis, and **against ambulatory insulin-patch form factors** (Insulet Omnipod, Tandem) as the design benchmark for the F7 ambulatory PCA (180g / 7-day battery class targets vs Omnipod's 72-hour benchmark).

**Why**: The incumbents lead on installed base and breadth but share the predictive-monitoring gap; that gap is the wedge. The ambulatory benchmark comes from the adjacent diabetes patch-pump category, which has already proven the lightweight/long-battery wearable form factor patients accept.

**How to apply**: Competitive claims are evidence-gated — the predictive wedge can only be marketed once F6 clears. Until then, lead with the proven hardware + connected-safety story.
<!-- Source: ben/080, "Competitive Positioning", last modified 2026-06-03 -->
<!-- DECISION:end id=D-COMM-1.8 -->

<!-- DECISION:start id=D-COMM-1.9 status=active source=ben/080 created=2026-06-03 last-edited=2026-06-03 -->
### Key Risks & Dependencies

**Decision**: Track five program-level risks the commercial plan is exposed to:

| # | Risk | Owning discipline(s) |
|---|---|---|
| **R1** | Predictive-monitoring SaMD clinical-evidence sufficiency — the 15–30 min warning claim must be substantiated for *PCA/opioid* context, not borrowed from general infusion | Clinical + Risk |
| **R2** | Alarm-fatigue claims (F4) over-promising vs real-world non-actionable-alert reduction | Clinical + Risk |
| **R3** | Ambulatory home-PCA use-safety — opioid in an unsupervised setting is the highest-consequence human-factors leap | Human Factors + Clinical |
| **R4** | Regulatory sequencing slip — each year's flagship is gated on the prior clearance | Regulatory + Program |
| **R5** | Reimbursement reliance on cost-avoidance rather than direct payment | Commercial + Health-Economics |

**Why**: These are the seams the KOL gap-analysis is expected to probe. Naming them in the roadmap makes the review's job concrete and shows the plan is not credulous about its own input numbers (which are demo figures).

**How to apply**: Each risk names the discipline that owns its resolution; the KOL gap-analysis routes findings to those same disciplines.
<!-- Source: ben/080, "Key Risks & Dependencies", last modified 2026-06-03 -->
<!-- DECISION:end id=D-COMM-1.9 -->

## Open Items

_Unresolved [VERIFY] markers and items needing human decision._

- **[VERIFY]** (D-COMM-1.7) Revenue / IRR / NPV figures are demo input-analysis estimates — substantiate against an independent financial model before any real business-case use.
- **Dependency**: International filing sequence (D-COMM-1.6) depends on [regulatory-strategy.md](regulatory-strategy.md) §3 *Jurisdictional Differences*, which is currently unpopulated. The roadmap's Y5 EU MDR / Canada wave cannot be firmed until that section is authored.
- **Dependency**: Feature-to-filing categorization (D-COMM-1.4) depends on the Critical-Requirement Carve-out tagging pass (regulatory §1) being applied to the underlying requirements (task ben/011, not yet started).

## Assembly History

_Append-only log of changes across assemblies. Most recent first._

### 2026-06-03 — assembled by benxavier-gl
- **Initial assembly** from ben/080
- **Added**: 5-Year Commercial Vision & Positioning, Market Segmentation & Customer Targeting, 5-Year Launch Sequencing & Phasing, Feature Roadmap (release-by-release), Pricing & Reimbursement, Channel & Geographic Expansion, Business Case & Revenue Model, Competitive Positioning, Key Risks & Dependencies (all ben/080)
- 9 subsections, 1 [VERIFY] marker

## Source Traceability

| Output Section | Source Task | Source Subsection | Last Modified |
|---------------|-----------|-------------------|---------------|
| Strategy Decisions | 080 | 5-Year Commercial Vision & Positioning | 2026-06-03 |
| Strategy Decisions | 080 | Market Segmentation & Customer Targeting | 2026-06-03 |
| Strategy Decisions | 080 | 5-Year Launch Sequencing & Phasing | 2026-06-03 |
| Strategy Decisions | 080 | Feature Roadmap (release-by-release) | 2026-06-03 |
| Strategy Decisions | 080 | Pricing & Reimbursement | 2026-06-03 |
| Strategy Decisions | 080 | Channel & Geographic Expansion | 2026-06-03 |
| Strategy Decisions | 080 | Business Case & Revenue Model | 2026-06-03 |
| Strategy Decisions | 080 | Competitive Positioning | 2026-06-03 |
| Strategy Decisions | 080 | Key Risks & Dependencies | 2026-06-03 |
