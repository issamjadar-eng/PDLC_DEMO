# 080 — Commercial Roadmap (5-Year) + KOL Gap-Analysis

**ID**: 080
**Created**: 2026-06-03
**Status**: Complete
**Created By**: Ben Xavier
**Owner**: Ben Xavier
**Priority**: High

---

## PERMANENT RULES (do not remove)

This task document is the **session-recovery point** for this work. If the session drops, is compacted, or ends, the next session must be able to load **this file alone** and continue.

1. **Update at every meaningful checkpoint (HARD RULE).** Tick the Todo, add a dated Changelog line naming the concrete artifact, update progress counts.
2. **Phase-end batching is OK; drift-batching is not.**
3. **A commit is not a substitute.** Git records code; this doc records the narrative.
4. **Resume-ready before any session boundary.**
5. **Capture strategy + lessons as they happen** with the required HTML-comment markers.

## Goals

Two linked deliverables, run end-to-end without prompting the user:

- **G1 — 5-Year Commercial Roadmap.** Evaluate the project's own inputs (regulatory + architecture strategy, market/competitive research, KOL roster, component portfolio, Critical-Requirement filing carve-out) and author a 5-year commercial strategy with a phased, feature-level roadmap for the PainEase PP3500 program. Lands in the durable `docs/project/strategies/commercial-strategy.md` via the `/strategy` skill contract (tagged content here → assembled output).
- **G2 — KOL Gap-Analysis of the roadmap.** Run `/gap-analysis` (topic `clinical`, component `pca-device`) where the KOL voice + adjacent disciplines evaluate the roadmap and give their opinion. Each advisor's full response is captured as a separate `recs-<advisor>.md` document; the aggregate `<id>.md` is the final report. Rendered to JSON sidecars so it **shows up in the project console** Gap Analysis tab; verified live in Chrome.

## Todos

- [x] Read skills end-to-end (strategy v19, gap-analysis v5, project-console v1.17.0) + template/routing/contract
- [x] Ground in inputs (regulatory + architecture strategy, market + competitive research, KOL roster, project.yml dhfs)
- [x] Author 5-year commercial roadmap as `<!-- STRATEGY CONTENT: commercial, ... -->` blocks (below)
- [x] Assemble `docs/project/strategies/commercial-strategy.md`
- [x] `/gap-analysis init clinical --component pca-device` → folder + aggregate + README
- [x] `fan-out` — clinical-affairs (KOL) + regulatory-affairs + program-manager + human-factors; each writes `recs-<advisor>.md`
- [x] Aggregate findings + convergence + open-questions into the aggregate report
- [x] `/gap-analysis render` → JSON sidecars
- [x] `/project-console` running; verify Gap Analysis tab renders the new analysis in Chrome
- [x] Final task-doc checkpoint

## Grounding (read 2026-06-03)

- `docs/project/strategies/regulatory-strategy.md` — Critical-Requirement Carve-out (CtS/CtF/CtC/CtP); PCA-device-alone filing scope; component classification (PCA Class II 510(k)+PCCP; Connectivity Adapter MDDS; Drug Library Manager + Alerts Engine + Clinical Interface = Class II SaMD; fleet/analytics/inventory/compliance = non-device).
- `docs/project/strategies/architecture-strategy.md` — ecosystem (PCA device + Connectivity Adapter + Cloud Suite + hospital IT); modular DHFs compose into filings via composition manifest.
- `docs/project/input-analysis/market-research/strategic-market-ai-infusion.md` — AI predictive monitoring top opportunity; home-infusion $54.8B by 2030 (12.8% CAGR); FDA PCCP final Aug 2025; sequencing pre-sub M12 / ambulatory M24 / AI launch M30.
- `docs/project/input-analysis/competitive-landscape/competitive-product-assessment.md` — PP3500 flagship (K210345, Nov 2021); competitive gap = **no predictive monitoring**; AI personalization KOL sentiment +0.55, 35% alert reduction, $180–240M revenue, 68% IRR / 42 mo / $24M; combined $350M+/yr by Y5, portfolio IRR 58%, NPV $425M.
- `docs/project/input-analysis/kol-feedback/` — 8 KOLs. Anchor: KOL-0006 James Paul (PCA/opioid safety). Alarm fatigue: Giuliano (KOL-0001), Shah (KOL-0008), Kirkendall (KOL-0002). DERS/dose limits: Kuitunen (KOL-0004). Human factors: Pennathur (KOL-0005). Infusion standards: Gorski (KOL-0007).

---

## Commercial Strategy

<!-- STRATEGY CONTENT: commercial, market-positioning, launch-sequencing, feature-roadmap, pricing-reimbursement, channel-geography, business-case, competitive-positioning, risks-dependencies -->

### 5-Year Commercial Vision & Positioning

**Decision**: Position the PainEase PP3500 program as the **safety-and-intelligence leader in patient-controlled analgesia**, evolving over five years from a best-in-class standalone PCA pump (cleared K210345) into a **connected, AI-assisted acute-pain platform** spanning hospital and home settings. The strategic throughline is: *close the one decisive competitive gap — the complete absence of predictive monitoring — while monetizing the modular Cloud Suite and an ambulatory form factor.*

**Why**: The competitive assessment is unambiguous that PP3500 already wins on the hardware fundamentals (150+ hr battery = 50% over typical; ±0.5% volumetric accuracy vs ±2.3% for Alaris/Spectrum IQ; 94% patient satisfaction; 80%+ wrong-med error reduction with barcode scanning) but that the **single largest competitive gap across the whole portfolio is the absence of predictive monitoring** — market leaders (BD Alaris, Baxter Spectrum IQ) are reactive-alarm only, while AI-enabled entrants demonstrate 15–30 min early warnings. The AI-enabled device market grows $15.1B → $98.3B (2023→2028, ~45% CAGR); AI-driven personalization is the highest-priority opportunity in our own KOL research (sentiment **+0.55** vs +0.16 baseline). Defending the PCA franchise means owning intelligence, not just hardware.

**How to apply**: Every roadmap release is justified against one of three positioning pillars — (1) **Safety leadership** (opioid-specific guardrails, predictive deterioration/occlusion warnings), (2) **Connected operations** (fleet, drug-library cadence, telemetry — the Cloud Suite monetization engine), (3) **Care-setting expansion** (ambulatory/home PCA). Marketing claims trace to cleared evidence; anything predictive ships only after its SaMD clears or rides the PCCP envelope.

### Market Segmentation & Customer Targeting

**Decision**: Prioritize three buyer segments in sequence: **(1) Acute-care hospitals** (anesthesia / acute pain services, the installed-base defenders — primary through Years 1–3); **(2) Health-system pharmacy & biomed** (the Cloud Suite buyer — drug-library governance, fleet management, surveillance — Years 2–4); **(3) Home-infusion & ambulatory-surgery providers** (the care-setting-expansion buyer — Years 3–5, riding the $28.4B→$54.8B home-infusion market at 12.8% CAGR).

**Why**: The KOL roster maps directly onto these segments and tells us where the credibility is. Acute-pain anesthesiologists (KOL-0006 James Paul) and the alarm-fatigue cluster (Giuliano KOL-0001, Shah KOL-0008, Kirkendall KOL-0002) are the hospital pull; pharmacy DERS expertise (Kuitunen KOL-0004) and infusion-nursing standards (Gorski KOL-0007) anchor the pharmacy/biomed buyer; human-factors depth (Pennathur KOL-0005) de-risks the home/ambulatory leap where the user is a patient or family caregiver, not a trained nurse. Selling intelligence (segment 2/3) before the safety story is proven in the installed base would overextend the brand.

**How to apply**: Year-1 commercial motion = installed-base retention + barcode/drug-library attach. Sequence Cloud Suite upsell to existing PP3500 accounts before net-new. Home/ambulatory enters only after the connected story is referenceable.

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

**How to apply**: Treat the Year column as the commit boundary for the business case below; treat the Regulatory vehicle column as the dependency on `regulatory-strategy.md` (Critical-Requirement Carve-out + PCCP envelope). A feature slips a year rather than shipping ahead of its regulatory vehicle.

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

**Why**: The feature set is mined directly from the competitive gap (predictive monitoring, F6), the highest-KOL-sentiment opportunity (AI personalization, F8, +0.55), the modular component portfolio already classified in `regulatory-strategy.md` (F1–F5), and the home-infusion TAM (F7). Each feature names its KOL anchor so the gap-analysis KOL review has a concrete claim to evaluate.

**How to apply**: This table is the canonical feature commitment. The KOL gap-analysis (G2) critiques *this table* — sequencing realism, evidence sufficiency, alarm-fatigue claims, and home-PCA safety. Engineering reads the Component column to map features to DHFs.

### Pricing & Reimbursement

**Decision**: Adopt a **razor + recurring-software** model: the PP3500 (and later PP3500-A) hardware carries a capital price competitive with Alaris/Spectrum IQ, while the Cloud Suite SaMDs (Drug Library Manager, Alerts Engine, Clinical Surveillance, predictive monitoring) are sold as **per-pump / per-bed annual subscriptions**. Reimbursement strategy leans on **cost-avoidance** (adverse-event reduction, alarm-fatigue labor savings) rather than direct procedure reimbursement, because PCA delivery is bundled into the surgical/inpatient DRG.

**Why**: PCA infusion is not separately reimbursed — the buyer's economic case is avoided harm and nursing efficiency, exactly what the evidence base quantifies (60% adverse-event reduction, 35% alert reduction, 80% IV-med-error reduction). A subscription model captures the recurring value of the Cloud Suite and funds the $24M / 42-month predictive-monitoring development out of installed-base revenue rather than a single capital sale.

**How to apply**: Year-1 list price holds the hardware franchise; Cloud Suite attach rate is the Year-2+ growth lever. Health-economics dossiers (cost-avoidance models) are a Year-1 commercial deliverable, not an afterthought — they are the reimbursement argument.

### Channel & Geographic Expansion

**Decision**: **US direct + GPO/IDN contracting first** (Years 1–3), then **EU MDR and Health Canada** (Years 4–5), prioritizing markets where the KOL footprint already extends (Finland/EU via Kuitunen KOL-0004; Canada via Paul KOL-0006). Home/ambulatory (F7) goes to market through **home-infusion specialty pharmacy and ambulatory-surgery-center channels**, distinct from the acute-care hospital sales motion.

**Why**: The cleared device is K210345 (US). EU MDR (12–18 month CE-mark timelines) and Canada are deliberately deferred until the connected + predictive story is referenceable, so international launches lead with the differentiated platform rather than a me-too pump. Channel bifurcation (hospital direct vs home-infusion specialty) reflects genuinely different buyers.

**How to apply**: International filing sequence is a dependency on `regulatory-strategy.md` §3 (Jurisdictional Differences — currently unpopulated; flag as an open item the roadmap depends on). Home channel build-out begins in Year 3 ahead of the F7 GA.

### Business Case & Revenue Model

**Decision**: Underwrite the program to the portfolio economics in the market analysis: **combined revenue potential ~$350M annually by Year 5, portfolio-level IRR ~58%, NPV ~$425M**, with the AI-predictive-monitoring line item alone carrying $180–240M revenue at **68% IRR over 42 months against a $24M investment**. Treat these as the demo program's underwriting targets, not guarantees.

**Why**: These figures are the project's own input-analysis numbers and give the roadmap a quantified spine the KOL review and the business case can interrogate. The recurring-software model (above) is what makes the Year-5 revenue durable rather than one-time capital.

**How to apply**: Each annual wave is a stage-gate — fund Year N+1 features against Year N attach-rate and evidence milestones. The $24M predictive-monitoring spend is gated behind Year-1/Year-2 Cloud Suite traction.

### Competitive Positioning

**Decision**: Position explicitly **against the reactive-alarm incumbents** (BD Alaris, Baxter Spectrum IQ, B. Braun, ICU Medical Plum 360) on the predictive axis, and **against ambulatory insulin-patch form factors** (Insulet Omnipod, Tandem) as the design benchmark for the F7 ambulatory PCA (180g / 7-day battery class targets vs Omnipod's 72-hour benchmark).

**Why**: The incumbents lead on installed base and breadth but share the predictive-monitoring gap; that gap is the wedge. The ambulatory benchmark comes from the adjacent diabetes patch-pump category, which has already proven the lightweight/long-battery wearable form factor patients accept.

**How to apply**: Competitive claims are evidence-gated — the predictive wedge can only be marketed once F6 clears. Until then, lead with the proven hardware + connected-safety story.

### Key Risks & Dependencies

**Decision**: Track five program-level risks the commercial plan is exposed to: **(R1)** predictive-monitoring SaMD clinical-evidence sufficiency (the 15–30 min warning claim must be substantiated for *PCA/opioid* context, not borrowed from general infusion); **(R2)** alarm-fatigue claims (F4) over-promising vs real-world non-actionable-alert reduction; **(R3)** ambulatory home-PCA use-safety (opioid in an unsupervised setting — the highest-consequence human-factors leap); **(R4)** regulatory sequencing slip (each year's flagship is gated on the prior clearance); **(R5)** reimbursement reliance on cost-avoidance rather than direct payment.

**Why**: These are the seams the KOL gap-analysis is expected to probe. Naming them in the roadmap makes the review's job concrete and shows the plan is not credulous about its own input numbers (which are demo figures).

**How to apply**: Each risk names the discipline that owns its resolution — R1/R2 clinical + risk; R3 human factors + clinical; R4 regulatory + program; R5 commercial + health-economics. The G2 gap-analysis routes findings to those same disciplines.

---

## Strategy capture

<!-- Note: the strategy content is captured inline above under "## Commercial Strategy". The /strategy assemble commercial run harvests it into docs/project/strategies/commercial-strategy.md. -->

<!-- LESSONS LEARNED: process -->
**Lesson (2026-06-03): A commercial roadmap is only as credible as the inputs it traces to.** The roadmap deliberately cites the project's own market/competitive/KOL inputs for every number and feature (rather than inventing market sizing), and then *names the seams* (R1–R5) for the KOL review to attack. **Why:** in a regulated demo, a roadmap that asserts revenue/clinical claims without provenance is indistinguishable from fabrication; tracing each claim to `input-analysis/` keeps it honest and gives the gap-analysis a falsifiable target. **How to apply:** when authoring commercial strategy, every market number gets a source path, and every clinical performance claim is flagged as needing substantiation in the *specific* device context (PCA/opioid), not the general category.

---

## Outcome (2026-06-03 — both goals complete)

**G1 — Commercial roadmap.** `docs/project/strategies/commercial-strategy.md` assembled from the tagged content above (was an `awaiting-content` stub): 9 `D-COMM-*` decisions, a 9-feature phased table (F1–F9) mapped to components + regulatory categories + KOL anchors, 5-year sequencing, pricing/reimbursement, channel/geography, business case, and a 5-risk register (R1–R5). 1 `[VERIFY]` (the demo revenue figures) + 2 named dependencies (regulatory §3 empty; ben/011 tagging not started).

**G2 — KOL gap-analysis.** `docs/_analysis/pca-device/commercial-roadmap-kol-review/`:
- Aggregate report `commercial-roadmap-kol-review.md` — 12 assertions (10 refuted, 1 confirmed, 1 partial), 13 findings, 4 convergence calls, 6 recommendations, 10-item cross-discipline open-questions roll-up.
- Four full advisor responses captured as separate docs: `recs-clinical-affairs.md` (KOL voice, primary), `recs-regulatory-affairs.md`, `recs-program-manager.md`, `recs-human-factors.md`.
- `commercial-roadmap-kol-review.gap.json` + refreshed `docs/_analysis/index.json` via `/gap-analysis render`.
- **Headline:** the panel endorses the *sequencing shape* (A10 confirmed) but found 7 gate-blockers. Two 3-agent convergence calls: **F7 home opioid PCA** (clinical+HF+regulatory) and **F6 predictive monitoring** (clinical+regulatory+PM). Foundation cluster: KOLs uncontacted (F-1), PCCP unwritten (F-5), keystone tasks unresourced (F-9).

**Console verification (Chrome).** Console live on :8765. `/gap-analysis` index shows the new card (10 grounding · 4 advisors · 13 findings · CL/RE/PR/HU avatars); `/gap-analysis/commercial-roadmap-kol-review` detail renders the full KPI bar, grounding table, per-advisor findings mapping, all 12 assertions with dispositions, 13 expandable findings, and 6 recommendations. Screenshots: `_scratch/080-gap-analysis-console-index.png`, `_scratch/080-gap-analysis-console-detail.png`.

<!-- STRATEGY CONTENT: commercial, evidence-discipline -->
### Roadmap evidence discipline (post-review)
The KOL review surfaced that several roadmap claims (F4 alarm reduction, F6 15–30-min predictive warning, F7 home-PCA) lean on **borrowed, non-PCA evidence** (general infusion, insulin-patch, a separate 28-expert market panel) presented as if PCA/opioid-validated. **Why:** for a controlled-substance, patient-actuated device whose dominant failure mode is respiratory depression, borrowed effect sizes do not transfer; the gap is both a marketing-claim risk and a filing risk. **How to apply:** every PCA-context clinical claim in the commercial roadmap must either cite a PCA/opioid source or carry an explicit "feasibility signal — non-PCA source" flag until project-specific evidence exists. (Captured for the next `/strategy assemble commercial`.)

<!-- LESSONS LEARNED: process -->
**Lesson (2026-06-03): Multi-advisor fan-out finds the foundation gaps a single reviewer misses.** Three disciplines independently flagged F7 (home opioid PCA) and three independently flagged F6 (predictive monitoring) — the convergence is what marks them as the highest-confidence, hardest-to-rationalize-away findings. A single clinical reviewer would have caught the evidence gap; only the regulatory + PM advisors surfaced that the *PCCP envelope is unwritten* and the *keystone tagging task is unresourced* — i.e., the roadmap's floor isn't poured. **Why:** review quality scales with perspective diversity, not reviewer effort. **How to apply:** for any cross-functional artifact (roadmap, submission, strategy), route the gap-analysis to ≥3 disciplines and treat ≥2-agent convergence as the priority queue. [[feedback_proactive_strategy_lessons]]

## Changelog

| Date | Author | Summary |
|------|--------|---------|
| 2026-06-03 | Ben Xavier | Task created. Read strategy/gap-analysis/project-console skills end-to-end; grounded in regulatory+architecture strategy, market+competitive research, KOL roster, project.yml dhfs. Authored 5-year commercial roadmap (9 strategy subsections, 9-feature table) as tagged content above. |
| 2026-06-03 | Ben Xavier | G1 done: assembled `commercial-strategy.md` (9 D-COMM decisions, F1–F9 table, R1–R5). G2 done: scaffolded `_analysis/pca-device/commercial-roadmap-kol-review/`, fanned out 4 advisors (clinical/reg/PM/HF), captured 4 full `recs-*.md`, merged 13 findings + 12 assertions + convergence into the aggregate, rendered JSON sidecars. Verified live in Chrome (index card + full detail render; screenshots in _scratch). |
| 2026-06-04 | Ben Xavier | **User clarification**: KOL evaluation should run the *individual KOL agents* alongside our discipline advisors — not just a consolidated clinical voice. Added the **8-member KOL persona-agent panel**: spawned one agent per roster KOL (Paul/Giuliano/Shah/Kuitunen/Kirkendall/Pennathur/Gorski/Braithwaite), each grounded in its own profile + speaking first-person. Captured each full opinion as a separate `kol-KOL-NNNN-*.md` (8 docs). Added findings **F-14…F-21** (one headline per KOL, incl. 4 genuinely-new issues: DERS governance, pediatric scope, INS nursing standards, insulin-analogy biomarker), a KOL-Panel verdict table, and KOL `agent:` changelog rows. Re-rendered: **12 agents** (4 advisors + 8 KOLs), **21 findings**, 12 assertions. Verified in Chrome — console "Advisors that ran" now shows all 12 voices with distinct avatars; index card reads 12 ADVISORS · 21 FINDINGS (screenshots `080-gap-analysis-kol-panel-console.png`, `080-gap-analysis-index-12advisors.png`). KOL opinions clearly marked **simulated/demo** (consistent with F-1). Task complete. |
| 2026-06-08 | Ben Xavier | 2026-06-08: Confirmed Complete via task-doc audit — commercial-strategy.md + docs/_analysis/pca-device/commercial-roadmap-kol-review/ shipped (80f6793). Filed under Completed in 000-index.md. |
- 2026-09-08: harvest tags repaired (ben/123) — 1 tags
