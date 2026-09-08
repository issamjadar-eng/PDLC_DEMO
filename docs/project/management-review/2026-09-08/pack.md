# Management Review Pack — 2026-09-08

_Assembled by the commercial-skill engine from approved answer editions. Every figure below was emitted by a claim-linted edition of the cited question; this pack computes nothing._

## Commercial

### BQ-01 — Which of our five device lines fund the company and which consume it — revenue, margin, trajectory by line?

_Category: Board & Portfolio · edition `2026-07-27.3` (approved) · report: `docs/project/commercial/reports/BQ-01/2026-07-27.3/report.md`_

**Verdict:** PP3500 and cloud-suite fund the company — 59.8% of trailing-4Q gross margin ($27.0M of the portfolio's $45.2M GM on $88.2M revenue, window 2025-Q3..2026-Q2); all 6 lines gross-margin positive; margins compressing on IP5000, PP3000

| Expectation | Expected | Actual | Verdict |
|---|---|---|---|
| E-01.1 Every product line is gross-margin positive over the trailing four quarters | gross margin > 0 per line, trailing 4Q | all lines positive; thinnest is PP3000 at 45.3% | met (unvalidated) |

**Risks:**
- R1 (medium) — IP5000 gross margin is compressing — 45.9% in the trailing window vs 47.4% in the prior four quarters (-1.5 pts)
- R2 (medium) — PP3000 gross margin is compressing — 45.3% in the trailing window vs 46.8% in the prior four quarters (-1.5 pts)

_Pins: `commercial/internal-financials@2026-07-27` (43d, fresh)_

### BQ-02 — How concentrated are we — PCA franchise, top-3 GPOs, single systems — and what does losing one anchor GPO do to the 5-year plan?

_Category: Board & Portfolio · edition `2026-07-27.3` (approved) · report: `docs/project/commercial/reports/BQ-02/2026-07-27.3/report.md`_

**Verdict:** Meridian Health Alliance carries 38.4% of FY2025 direct-book revenue — above the 30% guardrail on the direct-book basis, and basis-sensitive: the direct book covers 50.6% of total FY2025 revenue, and Meridian Health Alliance's floor share of TOTAL revenue is 19.4% (under the guardrail); top-3 accounts 25.5%, PCA franchise 74.5%; losing the anchor GPO dents every plan year by $15.6M (14.9% of the FY2026 plan) under the stated constant-dent scenario

| Expectation | Expected | Actual | Verdict |
|---|---|---|---|
| E-02.1 No single GPO carries more than 30% of annual revenue | <= 30% of FY revenue per GPO | Meridian Health Alliance at 38.4% of FY2025 direct-book revenue; all other GPOs within the guardrail — BASIS-SENSITIVE: the expectation says annual revenue, but the test denominator is the direct book (50.6% of total FY2025 revenue); Meridian Health Alliance's floor share of total revenue is 19.4%, which does NOT breach the guardrail (distributor-routed revenue unattributed) | not-met (unvalidated) |

**Issues:**
- I1 (high) — Meridian Health Alliance holds 38.4% of FY2025 direct-book revenue — over the 30% concentration guardrail

**Risks:**
- R1 (medium) — Top-3 accounts hold 25.5% of FY2025 direct-book revenue — account-level concentration compounds the GPO concentration (largest: Northgate Health System at 11.0%)
- R2 (medium) — The loss scenario is a floor, not a forecast: the dent is held constant at the FY2025 anchor book ($15.6M) while the plan grows, and it covers the direct book only — the true dent of losing Meridian Health Alliance grows with the plan
- R3 (medium) — The E-02.1 verdict is basis-sensitive: the guardrail is worded against annual revenue but tested on the direct book, which covers 50.6% of total FY2025 revenue — Meridian Health Alliance breaches on the direct book (38.4%) while its floor share of total revenue (19.4%) does not breach

_Pins: `commercial/internal-sales-accounts@2026-07-27` (43d, fresh); `commercial/internal-revenue-plan@2026-07-27` (43d, fresh); `commercial/internal-financials@2026-07-27` (43d, fresh)_

### BQ-03 — What share of revenue is recurring today vs the Y5 plan — and which parts of the $350M target are contracted, modeled, or aspiration?

_Category: Board & Portfolio · edition `2026-07-27.4` (approved) · report: `docs/project/commercial/reports/BQ-03/2026-07-27.4/report.md`_

**Verdict:** Recurring revenue is 10.8% of revenue today (FY2026H1) vs 68.6% planned for FY2030; of the $350.0M target, $128.0M rides on already-cleared products, $12.0M on letter-to-file changes, and $210.0M (60.0%) sits behind FDA decisions not yet received — and within the $240.0M recurring proxy itself, $210.0M (87.5%) is behind those decisions

| Expectation | Expected | Actual | Verdict |
|---|---|---|---|
| E-03.1 Recurring (subscription) revenue share grows every fiscal year toward the Y5 model | recurring share strictly increasing FY2024 -> FY2026 | FY2024: 5.0%; FY2025: 7.9%; FY2026H1: 10.8% — strictly increasing | met (unvalidated) |

**Risks:**
- R1 (high) — 60.0% of the FY2030 target ($210.0M) is aspiration — revenue behind pccp-enabled and new-submission FDA decisions not yet received — and the blended figure understates the recurring-specific bet: within the cloud-suite recurring proxy alone, 87.5% ($210.0M of $240.0M) sits behind those decisions; the regulatory-exposure and slip arithmetic is BQ-05's answer

_Pins: `commercial/internal-financials@2026-07-27` (43d, fresh); `commercial/internal-revenue-plan@2026-07-27` (43d, fresh)_

### BQ-04 — Does the subscription model work at unit level — LTV per connected pump vs cost-to-serve, and is Cloud Suite cannibalizing hardware ASP?

_Category: Board & Portfolio · edition `2026-07-27.3` (approved) · report: `docs/project/commercial/reports/BQ-04/2026-07-27.3/report.md`_

**Verdict:** Unit economics fail the guardrail: LTV per connected pump $2,237 vs $2,720 cost-to-serve over the same 5-year horizon (ratio 0.82 vs the 3.0 floor); 28 of 39 active sites run ARR below cost-to-serve — concentrated in small sites — and the mean hardware discount at subscribed sites is 5.8% vs the 5% tolerance

| Expectation | Expected | Actual | Verdict |
|---|---|---|---|
| E-04.1 Lifetime value per connected pump covers cost-to-serve at a healthy multiple | LTV : cost-to-serve >= 3.0 | ratio 0.82 (ARR $447/pump/yr vs cost $544/pump/yr, active sites; ratio computed on raw sums, rounded for display) | not-met (unvalidated) |
| E-04.2 Cloud Suite attach does not erode hardware pricing beyond tolerance | avg hardware discount at subscribed sites <= 5% | mean hardware discount 5.8% across 39 active subscribed sites — +0.8pp vs the 5% stand-in line; KNIFE-EDGE on |miss| ≤ 1pp (miss = 2.1 SE, SE ≈ 0.4pp, n=39) against an unvalidated threshold — verdict fragile to the stand-in choice | not-met (unvalidated) |

**Issues:**
- I1 (high) — Small sites are negative at unit level: 24 sites (<= 6 pumps) run $460/pump/yr below water (24 of them ARR-below-cost individually)
- I2 (medium) — Mean hardware discount at subscribed sites is 5.8%, over the 5% tolerance — the subscription may be being bought with hardware price

**Risks:**
- R1 (high) — Fleet-wide LTV:cost-to-serve is 0.82, under the 3.0 floor — and the LTV side is flattered by the model (no churn decrement, no discounting) while 3 churned sites already exist

_Pins: `commercial/internal-subscriptions@2026-07-27.2` (43d, fresh); `commercial/internal-fleet@2026-07-27` (43d, stale)_

### BQ-05 — How much plan revenue sits behind FDA decisions we haven't received — by regulatory dependency, with slip triggers?

_Category: Board & Portfolio · edition `2026-07-27.3` (approved) · report: `docs/project/commercial/reports/BQ-05/2026-07-27.3/report.md`_

**Verdict:** $366.0M of the $1,000.0M five-year plan sits behind FDA decisions not yet received; exposure crosses the 40% threshold in FY2029, FY2030 (peak 60.0% in FY2030)

| Expectation | Expected | Actual | Verdict |
|---|---|---|---|
| E-05.1 Regulatory-dependent revenue stays below the exposure threshold in every plan year | <= 40% of plan-year revenue behind not-yet-received FDA decisions | FY2026: 0.0%; FY2027: 8.5%; FY2028: 23.5%; FY2029: 42.9%; FY2030: 60.0% — over threshold in FY2029, FY2030 | not-met (unvalidated) |

**Issues:**
- I1 (high) — FY2029 exposure is 42.9% — $105.0M of $245.0M sits behind pccp-enabled or new-submission decisions, over the 40% threshold
- I2 (high) — FY2030 exposure is 60.0% — $210.0M of $350.0M sits behind pccp-enabled or new-submission decisions, over the 40% threshold

**Risks:**
- R1 (medium) — A uniform 6-month slip of all dependent revenue cuts FY2030 by $52.5M and pushes $105.0M past FY2030 — out of the five-year window entirely
- R2 (high) — A uniform 12-month slip of all dependent revenue cuts FY2030 by $105.0M and pushes $210.0M past FY2030 — out of the five-year window entirely

_Pins: `commercial/internal-revenue-plan@2026-07-27` (43d, fresh); `commercial/openfda-510k-infusion@2026-07-22` (48d, fresh)_

### BQ-06 — Is the concept pipeline converting, and how does our clearance cycle time compare with our own history and with BD/Baxter?

_Category: Board & Portfolio · edition `2026-07-27.2` (approved) · report: `docs/project/commercial/reports/BQ-06/2026-07-27.2/report.md`_

**Verdict:** Competitor 510(k) review runs a median 213 days received→decision across 29 infusion-pump clearances since 2021; fastest frequent filer is Baxter Healthcare Corporation at 74 days median

_Pins: `commercial/openfda-510k-infusion@2026-07-22` (48d, fresh)_

### BQ-07 — What is our actual share of the US PCA/smart-pump segment — taking share from BD/Baxter or growing with the market?

_Category: Market & Competitive · edition `2026-07-27.3` (approved) · report: `docs/project/commercial/reports/BQ-07/2026-07-27.3/report.md`_

**Verdict:** US (NA-proxy) PCA/LVP smart-pump share is a RANGE, not a number: ~0.029%–0.047% of installed base and ~0.55%–1.1% of annual segment dollars (A-003 denominator, LOW confidence); our installed base grew ~16.0%/yr vs the assumed market ~7.3%/yr — directionally gaining, from a tiny base (mismatched bases: ours is UNIT growth of our NA in-segment book; A-003's rate is the DOLLAR CAGR of the total US infusion-pump market — directional comparison only)

**Risks:**
- R1 (high) — The entire share figure rests on A-003 (LOW confidence, triangulated from public analyst-report summaries) — the denominator could be off by a large factor, and the unit-share and dollar-share bases already tell different stories (stock share vs flow share)
- R2 (medium) — US share is proxied by the NA region and the denominator is held constant across fiscal years (market growth not modeled per-year) — both stated simplifications of the committed plan

_Pins: `commercial/internal-sales-accounts@2026-07-27` (43d, fresh)_

### BQ-08 — What are we winning and losing on — and how many recent losses cite predictive monitoring we don't have?

_Category: Market & Competitive · edition `2026-07-27.3` (approved) · report: `docs/project/commercial/reports/BQ-08/2026-07-27.3/report.md`_

**Verdict:** Trailing-365d win rate is 58.7% of decided opportunities (37 won / 26 lost; 18 no-decision excluded) vs the 50% stand-in target; dollar-weighted we win 61.4% of decided CRM value ($30,389,000 won vs $19,071,000 lost — we win bigger deals than we lose); 8 of 26 losses (30.8%) have the predictive-monitoring gap primary or cited — $4,792,000 in CRM value

| Expectation | Expected | Actual | Verdict |
|---|---|---|---|
| E-08.1 Competitive win rate holds at or above half of decided opportunities | >= 50% of won+lost | 58.7% of decided (37W/26L, window 2025-07-20 → 2026-07-20); sensitivity: 45.7% if the 18 no-decisions count as losses — the verdict is denominator-sensitive, not just sample-sensitive | met (unvalidated) |

**Risks:**
- R1 (high) — Predictive-monitoring gap touches 30.8% of in-window losses (8 deals, $4,792,000 CRM value; primary reason in 5 of them) — the largest addressable feature-driven loss pool
- R2 (medium) — Loss attribution is the CRM's single primary_reason per opportunity — a recorded citation is not proof the gap decided the deal

_Pins: `commercial/internal-winloss@2026-07-27.4` (43d, stale)_

### BQ-09 — Are we winning displaced accounts where an incumbent has an open recall or integration disruption — and how long does the window stay open?

_Category: Market & Competitive · edition `2026-07-27.3` (approved) · report: `docs/project/commercial/reports/BQ-09/2026-07-27.3/report.md`_

**Verdict:** Method demo (fabricated CRM joined to REAL FDA recall dates): we win 67.3% of decided opportunities where the incumbent had an FRN recall posted within 180 days of close (n=55) vs 14.3% outside the window (n=7); there is no uniform decay across the interior buckets (65.8% → 70.6% → 0.0%); the >12 months / no prior recall tail sits at 50.0% (n=2)

**Risks:**
- R1 (high) — The effect size is NOT market evidence: opportunity records are demo-fabricated and their seeded disruption windows were set independently of the real recall calendar — only the join method generalizes
- R2 (medium) — Large incumbents recall so often that 55 of 62 decided incumbent-held opportunities fall in-window — the out-of-window control group (n=7) is too small to carry weight on its own

_Pins: `commercial/internal-winloss@2026-07-27.4` (43d, stale); `commercial/openfda-recalls-infusion@2026-07-22` (48d, stale)_

### BQ-10 — Where do we sit vs Alaris/Spectrum IQ/Plum 360 on 5-year TCO per pump — the buyer's spreadsheet?

_Category: Market & Competitive · edition `2026-07-27.3` (approved) · report: `docs/project/commercial/reports/BQ-10/2026-07-27.3/report.md`_

**Verdict:** Indicative, assumption-bounded: our 5-yr TCO is $8,900/pump all-in ($5,100 on the capital+service basis) vs a class-wide competitor range of ~$3,000–$15,000 on capital+service ONLY — competitor consumables and software subscription are undisclosed and excluded, so their true all-in TCO sits ABOVE that range; the ranges overlap and no hard we-win claim is supportable

**Risks:**
- R1 (high) — The comparison is not like-for-like by construction: the competitor range excludes consumables (undisclosed) and quantifies software subscription only as 'required, magnitude unknown', while our figure includes both — the spread understates competitor cost
- R2 (medium) — Our own cost constants are demo stand-ins, not finance-validated rates — both sides of the buyer's spreadsheet are currently unvalidated

_Pins: `commercial/external-competitor-features@2026-07-27` (43d, fresh)_

### BQ-11 — Where are pumps sold but underused — accounts whose utilization/telemetry diverges from what they bought?

_Category: Market & Competitive · edition `2026-07-27.3` (approved) · report: `docs/project/commercial/reports/BQ-11/2026-07-27.3/report.md`_

**Verdict:** 6 connected site(s) ran below 60% of expected infusion hours over 2026-05..2026-07 (worst 34.0%); 2 clear the ≥10-connected-device materiality bar (S-NA-22, S-EMEA-02); the account-revenue tie the question asks for is blocked — no site→account key exists in any pinned dataset

| Expectation | Expected | Actual | Verdict |
|---|---|---|---|
| E-11.1 No material account runs its connected fleet below the utilization floor | >= 60% of expected hours at every account with >= 10 connected devices | site-level proxy (account join unavailable): 2 site(s) with >= 10 connected devices below 60%: S-NA-22 35.3%; S-EMEA-02 36.6% | not-met (unvalidated) |

**Issues:**
- I1 (high) — S-NA-22 runs at 35.3% of expected hours across 19 connected devices over 2026-05..2026-07 — sold-but-underused at material scale (early churn warning)
- I2 (high) — S-EMEA-02 runs at 36.6% of expected hours across 16 connected devices over 2026-05..2026-07 — sold-but-underused at material scale (early churn warning)

**Risks:**
- R1 (high) — Account-level revenue-at-risk cannot be computed: no pinned dataset carries a site→account key (sales-accounts is account-level with no site list) — the churn-risk framing stops at regional context
- R2 (medium) — expected_hours is the dataset's per-segment norm, not a contract term — a site with a legitimately different case mix looks underused against it

_Pins: `commercial/internal-telemetry-utilization@2026-07-27` (43d, stale); `commercial/internal-fleet@2026-07-27` (43d, stale); `commercial/internal-sales-accounts@2026-07-27` (43d, fresh)_

### BQ-12 — What did competitors clear in the last 90 days, laid against our Y1–Y5 roadmap — anything landing on a feature we scheduled two years out?

_Category: Roadmap & State of the Art · edition `2026-07-27.2` (approved) · report: `docs/project/commercial/reports/BQ-12/2026-07-27.2/report.md`_

**Verdict:** 1 infusion-pump clearance(s) in the 90-day window ending 2026-01-28; 0 flag roadmap-relevant keywords — review against the roadmap lanes

_Pins: `commercial/openfda-510k-infusion@2026-07-22` (48d, fresh)_

### BQ-13 — How much runway before someone closes the predictive-monitoring gap — is our Y3 timing defensible, and what if an incumbent buys an AI entrant?

_Category: Roadmap & State of the Art · edition `2026-07-27.3` (approved) · report: `docs/project/commercial/reports/BQ-13/2026-07-27.3/report.md`_

**Verdict:** Nobody in the competitive matrix documents predictive monitoring today, but the runway is assumption-thin: a SaMD-only entrant starting at the data anchor (2026-01-28) could clear 2027-07-28 to 2028-01-28 — about 5 months before our F6 2028-H2 launch anchor; an incumbent acquisition inherits the same clock; 0 ai/predictive-flagged clearance(s) in the trailing-12-month watch. The hardware-scenario reassurance is FRAGILE: its fast edge clears the favorable launch anchor by only 27 days and beats an end-of-2028-H2 launch reading by ~5 months — and the H2 anchor refinement is a catalog config choice, not a strategy-doc commitment

**Risks:**
- R1 (high) — The F6 runway verdict is assumption-bounded: the entire lead-time model is A-005 (medium confidence), and the entrant clock is modeled from the data anchor (2026-01-28) — a program already underway is ahead of every figure here
- R2 (medium) — Acquisition scenario: an incumbent buying an AI entrant applies the 18-24-month SaMD clock to an established hospital channel — the fastest modeled path to closing our gap, and it is an assumption-class scenario, not an observed signal
- R3 (medium) — The hardware-scenario reassurance ('clears after our launch anchor') holds by only 27 days at the fast edge under the favorable anchor reading, and flips under the end-of-period reading (2028-12-31: the fast edge beats our launch by ~5 months); the H2 anchor refinement itself is a catalog config choice — the strategy doc commits only 'Y3 (2028)'

_Pins: `commercial/openfda-510k-infusion@2026-07-22` (48d, fresh); `commercial/external-competitor-features@2026-07-27` (43d, fresh)_

### BQ-14 — Where exactly do we sit on PCA feature parity, line by line — which gaps are on the roadmap vs silently unaddressed?

_Category: Roadmap & State of the Art · edition `2026-07-27.3` (approved) · report: `docs/project/commercial/reports/BQ-14/2026-07-27.3/report.md`_

**Verdict:** 10 attributes compared: 2 ahead, 4 parity, 4 behind — 3 behind-gaps have a roadmap lane (of which 2 adjacency-only: integrated_etco2, pca_pause_or_etco2 — the lane responds but does not mechanically close the gap), 1 SILENTLY UNADDRESSED (weight_kg)

**Issues:**
- I1 (high) — weight_kg is behind (0.75 vs Smiths Medical (ICU Medical) CADD Legacy at 0.45) and NO roadmap lane owns the gap — silently unaddressed, nobody has decided about it

**Risks:**
- R1 (high) — BD ships PCA Pause and integrated EtCO2 today while our nearest roadmap answers sit in the F4 (Y2 (2027)) and F6 (Y3 (2028)) slots — and BOTH lane assignments are adjacency, not closure: F4 is smart alarm filtering and F6 is predictive monitoring, neither a hardware PCA-pause response nor a capnography module, so BD's shipped capability may remain unanswered even after F4/F6 land

_Pins: `commercial/external-competitor-features@2026-07-27` (43d, fresh)_

### BQ-15 — Is the state-of-the-art analysis still current (EU MDR), and are our headline spec differentiators still ahead?

_Category: Roadmap & State of the Art · edition `2026-07-27.3` (approved) · report: `docs/project/commercial/reports/BQ-15/2026-07-27.3/report.md`_

**Verdict:** ride to scheduled review (2027-04-12): both differentiators remain ahead of every documented competitor value and no refresh trigger fired. Accuracy margin ~6.6x vs best documented competitor on our LAB-basis spec (~4.6x on our volumetric-basis spec — ahead on either basis; competitor cells are nominal/field specs), battery ~2.1x; 0 FRN clearance(s) observed after the SOTA anchor date (2026-04-12) in a snapshot whose coverage ends 2026-01-28

**Risks:**
- R1 (medium) — The currency signal is lag-limited: the 510(k) snapshot's coverage ends 2026-01-28, months before the snapshot's acquisition — a recent clearance may already exist unseen

_Pins: `commercial/external-competitor-features@2026-07-27` (43d, fresh); `commercial/openfda-510k-infusion@2026-07-22` (48d, fresh)_

### BQ-16 — For each roadmap feature: documented KOL evidence on file? Which ride on a single voice, and does current sentiment still order the waves?

_Category: Roadmap & State of the Art · edition `2026-07-27.3` (approved) · report: `docs/project/commercial/reports/BQ-16/2026-07-27.3/report.md`_

**Verdict:** META-GAP: all 38 evidence rows are a simulated advisory panel — zero real collected KOL evidence exists (no interviews, surveys, or publications). Within the simulated register: F9 rides on a single voice (E-16.1 floor not met), and the F4, F6, F7, F8 wave slots carry concern-majority sentiment — read as NO documented endorsement of those slots, not as opposition: the register's 3-value vocabulary collapses conditional support into `concern` (stated limitation)

| Expectation | Expected | Actual | Verdict |
|---|---|---|---|
| E-16.1 Every committed roadmap feature has at least two independent KOL voices on file | >= 2 distinct KOLs per F1-F9 feature | distinct simulated-panel voices per feature — F1: 5; F2: 3; F3: 3; F4: 6; F5: 4; F6: 5; F7: 5; F8: 6; F9: 1; features below the floor: F9 (and zero REAL voices everywhere — see meta-gap) | not-met (unvalidated) |

**Issues:**
- I1 (high) — Zero real collected KOL evidence exists behind any of the 9 committed roadmap features — the entire register (38 rows) is simulated panel material
- I2 (medium) — F9 fails even the simulated-panel two-voice floor (E-16.1) — the weakest-evidenced committed bet(s)

**Risks:**
- R1 (medium) — The committed middle-wave slots (F4, F6, F7, F8) carry concern-majority sentiment — no documented endorsement of those slots exists. Caveat: the 3-value vocabulary flattens conditional support into concern (source docs show conditional-yes voices on F4 and F7), so this is an evidence-absence signal, not measured opposition

_Pins: `commercial/internal-kol-register@2026-07-27` (43d, fresh)_

### BQ-17 — Stacked against clearances, KOL data, and attach actuals — which roadmap bet do we kill, and which do we pull forward a year?

_Category: Roadmap & State of the Art · edition `2026-07-27.3` (approved) · report: `docs/project/commercial/reports/BQ-17/2026-07-27.3/report.md`_

**Verdict:** Decision support, not the decision: pull-forward candidate F4 Alerts Engine v1 (smart alarm filtering) (composite 0.616, tie with F6 broken on earliest wave); kill candidate F9 International expansion (EU MDR / Canada) (composite 0.0, tie with F7 broken on weakest evidence base) — sentiment axis is simulated-panel only, demand axis is Cloud attach 84.8%. CAUTION on the kill read: the single F9 voice argues the slot is too LATE and too THIN — a voice FOR earlier EU investment, arithmetically converted into kill support by the 3-value sentiment vocabulary

**Issues:**
- I1 (high) — Direction inversion on the kill candidate: the single F9 voice on file (Kuitunen) argues F9 is too LATE and too THIN — advocating earlier EU evidence investment — but the 3-value sentiment vocabulary encodes it as bare concern, arithmetically supporting the kill ranking; the only evidence on file contradicts the kill reading

**Risks:**
- R1 (high) — The kill ranking rests on a composite whose sentiment third is simulated and whose demand third does not exist for non-cloud features — F9 scores zero pressure, zero measured demand, and its sentiment comes from 1 simulated voice(s)
- R2 (medium) — F9 and F7 tie exactly at composite 0.0 — only evidence thinness separates the kill candidate from the runner(s)-up

_Pins: `commercial/internal-kol-register@2026-07-27` (43d, fresh); `commercial/external-competitor-features@2026-07-27` (43d, fresh); `commercial/openfda-510k-infusion@2026-07-22` (48d, fresh); `commercial/internal-subscriptions@2026-07-27.2` (43d, fresh); `commercial/internal-fleet@2026-07-27` (43d, stale)_

### BQ-18 — Top three complaint categories this quarter, rate-normalized with a stated denominator — any trending above the risk-file commitment?

_Category: Field: Complaints & Safety · edition `2026-07-27.3` (approved) · report: `docs/project/commercial/reports/BQ-18/2026-07-27.3/report.md`_

**Verdict:** CAPA-review trigger: occlusion-alarm at 3.17 per 100 devices vs threshold 3.0; connectivity at 2.26 per 100 devices vs threshold 2.0 (trailing 90d ending 2026-07-17)

| Expectation | Expected | Actual | Verdict |
|---|---|---|---|
| E-18.1 Complaint rates stay within the per-category thresholds | <= 2.0 per 100 devices per 90d (occlusion-alarm <= 3.0) | occlusion-alarm 3.17 vs 3.0; connectivity 2.26 vs 2.0 | not-met (unvalidated) |
| E-18.2 Complaint volume is not trending upward window-over-window | current 90d window <= 130% of prior window | current 101 vs prior 74 | not-met (unvalidated) |

**Issues:**
- I1 (high) — occlusion-alarm at 3.17 per 100 devices exceeds its threshold of 3.0 in the trailing 90d window
- I2 (high) — connectivity at 2.26 per 100 devices exceeds its threshold of 2.0 in the trailing 90d window

**Risks:**
- R1 (medium) — Total complaint volume is rising window-over-window (101 vs 74)
- R2 (medium) — The category thresholds are demo stand-ins, not the risk file's documented acceptability criteria — a breach verdict is only as good as its threshold

_Pins: `commercial/internal-complaints@2026-07-27.2` (43d, stale); `commercial/internal-fleet@2026-07-27` (43d, stale)_

### BQ-19 — How does our adverse-event profile compare to competitors — and what denominator did you use, because MAUDE doesn't have one?

_Category: Field: Complaints & Safety · edition `2026-07-27.2` (approved) · report: `docs/project/commercial/reports/BQ-19/2026-07-27.2/report.md`_

**Verdict:** MAUDE event COUNTS are comparable with caveats; RATE comparison is BLOCKED — the installed-base denominator (A-001) is not yet quantified

_Pins: `commercial/openfda-maude-infusion-mfr@2026-07-22` (48d, stale); `commercial/openfda-maude-infusion-monthly@2026-07-22` (48d, stale)_

### BQ-20 — Any field signal — complaints, near-misses, alarm data — around opioid over-delivery or PCA-by-proxy?

_Category: Field: Complaints & Safety · edition `2026-07-27.3` (approved) · report: `docs/project/commercial/reports/BQ-20/2026-07-27.3/report.md`_

**Verdict:** WATCH TRIGGERED on our internal log (demo-fabricated): 3 over-delivery and 2 PCA-by-proxy-suspected complaint records (2 MDR-filed, 1 under investigation) — E-20.1 zero-tolerance NOT met; the signal→upgrade loop closed for 2 watch-category signals; real class-wide MAUDE context is counts-only (no denominator)

| Expectation | Expected | Actual | Verdict |
|---|---|---|---|
| E-20.1 Zero confirmed over-delivery events in the field | 0 confirmed over-delivery complaints | 3 over-delivery complaint records on the log (2 MDR-filed, 1 under investigation) — zero-tolerance breached per the plan's 'confirmed' definition | not-met (unvalidated) |

**Issues:**
- I1 (high) — 3 over-delivery complaint records on the internal log — the franchise-killer category; newest is C-2026-0433 (2026-06-27, under-investigation, MDR filed: yes); the docket carries open over-delivery MDR item(s) MDR-2026-0005 — a category-level join, no shared key (see BQ-21)
- I2 (high) — 2 PCA-by-proxy-suspected records (unauthorized bolus by family/visitor suspected); 1 still open — a use-environment hazard the pump's lockout design must answer

**Risks:**
- R1 (medium) — The question asks for alarm data, but raw alarm telemetry is not a corpus dataset — only signals sourced from alarm analytics are visible, so an alarm-signature precursor of over-delivery could be missed

_Pins: `commercial/internal-complaints@2026-07-27.2` (43d, stale); `commercial/internal-signal-register@2026-07-27.2` (43d, fresh); `commercial/openfda-maude-pca-monthly@2026-07-27` (43d, stale); `commercial/internal-regulatory-docket@2026-07-27` (43d, stale)_

### BQ-21 — What's open on the field-action docket, how timely are our MDRs, and what's the exposure if FDA walks in tomorrow?

_Category: Field: Complaints & Safety · edition `2026-07-27.3` (approved) · report: `docs/project/commercial/reports/BQ-21/2026-07-27.3/report.md`_

**Verdict:** If FDA walks in tomorrow: 2 open docket item(s) (MDR-2026-0005 due in 2 days at the pin date; FSCA-2026-001 rollout incomplete) and 1 late MDR filing(s) in the trailing 12 months — on-time rate 94.7% (18 of 19); E-21.1 NOT met

| Expectation | Expected | Actual | Verdict |
|---|---|---|---|
| E-21.1 Every MDR is filed within its regulatory deadline | 0 late filings, trailing 12 months | 1 late filing(s) in the trailing 12 months (MDR-2025-0018 +9d); lifetime record holds 2 late filing(s) | not-met (unvalidated) |

**Issues:**
- I1 (high) — MDR-2026-0005 (over-delivery) is open and unfiled with 2 days to its regulatory deadline (2026-07-29) at the pin date — the over-delivery event under investigation (see BQ-20)
- I2 (medium) — FSCA-2026-001 (drug-library-correction) remains open: rollout as recorded — "NA complete 2026-06, EMEA in progress (~60% sites), APAC pending" — an FDA investigator will ask why APAC has not started

**Risks:**
- R1 (medium) — 1 MDR(s) filed late inside the trailing window (MDR-2025-0018 +9d) — a repeat-observation pattern an investigator can cite even at a 94.7% on-time rate
- R2 (medium) — This docket audits filing timeliness of what was docketed — the complaint-to-MDR reportability decision trail is not a corpus dataset, so under-docketing would be invisible here

_Pins: `commercial/internal-regulatory-docket@2026-07-27` (43d, stale)_

### BQ-22 — Of last year's field signals, how many landed as design inputs or upgrade-pipeline items — and how many died in a spreadsheet?

_Category: Field: Complaints & Safety · edition `2026-07-27.3` (approved) · report: `docs/project/commercial/reports/BQ-22/2026-07-27.3/report.md`_

**Verdict:** 16 of 40 lifetime signals (40.0%) died in a spreadsheet (no-action or open past the 90-day SLA); trailing 12 months: 6 of 21 (28.6%) died vs 9 landed in design/upgrade — and only 36.8% of adjudicated cohort signals met the SLA, so E-22.1 is NOT met

| Expectation | Expected | Actual | Verdict |
|---|---|---|---|
| E-22.1 Every field signal reaches a disposition within the review SLA | 100% dispositioned within 90 days of opening | 36.8% of adjudicated cohort signals dispositioned within 90 days (7 within, 12 breached incl. 2 stale-open; 2 recent-open pending, excluded) | not-met (unvalidated) |

**Issues:**
- I1 (high) — 40.0% of lifetime signals (10 no-action + 6 open past 90 days) never reached the design or upgrade pipeline — the post-market → design-input loop is leaking
- I2 (medium) — Even signals that DO get dispositioned run slow: only 36.8% of the adjudicated cohort met the 90-day SLA (median lifetime time-to-disposition 103.5 days)

**Risks:**
- R1 (medium) — The 90-day SLA is a stand-in, not yet traced to the post-market SOP — the verdict is only as good as its threshold
- R2 (medium) — Landed dispositions are trusted from the register's DI-/REQ-/UPG- refs — no cross-system trace yet verifies those refs exist in the requirements or upgrade systems

_Pins: `commercial/internal-signal-register@2026-07-27.2` (43d, fresh)_

### BQ-23 — Where do we stand on the current field-update campaign — planned vs actual coverage by region and site, and will we hit the close date?

_Category: Field: Upgrades & Service Ops · edition `2026-07-27.3` (approved) · report: `docs/project/commercial/reports/BQ-23/2026-07-27.3/report.md`_

**Verdict:** Campaign C-2026-02 is 62.7% complete; at current run-rate EMEA, NA will miss the 2026-09-30 close

| Expectation | Expected | Actual | Verdict |
|---|---|---|---|
| E-23.1 Campaign C-2026-02 reaches 95% coverage by the close date | 95% by 2026-09-30 | 62.7% coverage as of the pin; projected finishes: APAC 2026-09-21, EMEA 2031-01-25, NA no-recent-completions | not-met (unvalidated) |
| E-23.2 Every region sustains a completion run-rate sufficient to finish its wave | run-rate >= required rate in each region | APAC: 4.5/wk, EMEA: 0.2/wk, NA: 0.0/wk | not-met (unvalidated) |

**Issues:**
- I1 (high) — NA has zero completions in the trailing four-week window with 44 devices remaining — the wave is stalled, not slow

**Risks:**
- R1 (medium) — EMEA projects to finish 2031-01-25, past the 2026-09-30 close (59 remaining at 0.2/wk)

_Pins: `commercial/internal-upgrade-campaign@2026-07-27` (43d, stale)_

### BQ-24 — What are our update failure and retry rates — is any hardware rev, firmware baseline, or site profile failing at a rate that says pause and escalate?

_Category: Field: Upgrades & Service Ops · edition `2026-07-27.3` (approved) · report: `docs/project/commercial/reports/BQ-24/2026-07-27.3/report.md`_

**Verdict:** PAUSE TRIGGER: cohort hw B upgrading from 3.1.2 fails on 31.4% of attempted devices (threshold 15.0%) — pause the wave for this cohort and escalate

| Expectation | Expected | Actual | Verdict |
|---|---|---|---|
| E-24.1 No cohort's per-attempt failure rate exceeds the pause threshold | <= 15% per attempted device (cohort n >= 20) | worst cohort 31.4% (hw B / from 3.1.2) | not-met (unvalidated) |

**Issues:**
- I1 (high) — Cohort hw B / from 3.1.2 fails on 31.4% of attempted devices (11 of 35) — above the pause threshold

**Risks:**
- R1 (medium) — The pause threshold itself is a demo stand-in — not derived from the risk file, so the trigger level is unvalidated

_Pins: `commercial/internal-upgrade-campaign@2026-07-27` (43d, stale)_

### BQ-25 — Are customers struggling with this upgrade — tickets per 100 upgraded pumps, rollbacks — and what does an upgrade cost the customer?

_Category: Field: Upgrades & Service Ops · edition `2026-07-27.3` (approved) · report: `docs/project/commercial/reports/BQ-25/2026-07-27.3/report.md`_

**Verdict:** Tickets per 100 attempted upgrades are highest in NA at 21.7; 4 site(s) rolled back; estimated customer-side cost of the on-site portion so far $7,272–$16,412

_Pins: `commercial/internal-upgrade-campaign@2026-07-27` (43d, stale)_

### BQ-26 — Do we have the capacity to execute the remaining waves on schedule — or do we add headcount, contract labor, or slip?

_Category: Field: Upgrades & Service Ops · edition `2026-07-27.3` (approved) · report: `docs/project/commercial/reports/BQ-26/2026-07-27.3/report.md`_

**Verdict:** Capacity gap to hit the 2026-09-30 close — EMEA, NA STALLED (zero completions in the four weeks to 2026-07-27; EMEA needs 6.4/wk; NA needs 4.7/wk); APAC behind (3.5/wk vs 4.5/wk required); remote conversion covers 0 of 97 on-site-remaining devices today

| Expectation | Expected | Actual | Verdict |
|---|---|---|---|
| E-26.1 Existing field-service capacity absorbs the remaining waves without surge or slip | current run-rate >= required rate through 2026-09-30 in every region | EMEA: stalled (6.4/wk required); NA: stalled (4.7/wk required); APAC: 3.5/wk vs 4.5 required | not-met (unvalidated) |

**Issues:**
- I1 (high) — EMEA wave is stalled under the uniform criterion — zero completions in the four weeks to 2026-07-27 (last completion 2026-06-22, 59 devices remaining, 6.4/wk now required)
- I2 (high) — NA wave is stalled under the uniform criterion — zero completions in the four weeks to 2026-07-27 (last completion 2026-05-11, 44 devices remaining, 4.7/wk now required)

**Risks:**
- R1 (medium) — APAC misses the 2026-09-30 close at current rate (3.5/wk vs 4.5/wk required)
- R2 (high) — The remote-conversion recovery lever is sized at 0 of 97 on-site-remaining devices — the fleet connectivity join shows the on-site backlog is unconnected, so conversion first requires connectivity (adapters), it is not a scheduling change
- R3 (medium) — The hire/contract/slip decision is being made on run-rate projections plus a labor-time-only workload floor (19.7 FSE-days) — FSE roster, utilization, travel, and visits-per-day are not yet a corpus dataset

_Pins: `commercial/internal-upgrade-campaign@2026-07-27` (43d, stale); `commercial/internal-fleet@2026-07-27` (43d, stale)_

### BQ-27 — How far behind current is the fleet — % of pumps more than one firmware version behind, at which accounts, and connected vs not?

_Category: Field: Upgrades & Service Ops · edition `2026-07-27.3` (approved) · report: `docs/project/commercial/reports/BQ-27/2026-07-27.3/report.md`_

**Verdict:** 56.7% of the PP3500 fleet is ≥1 firmware version behind (21.9% two behind); connected devices are current at 42.3% vs 44.2% for unconnected

_Pins: `commercial/internal-fleet@2026-07-27` (43d, stale)_

### BQ-28 — Where are we against plan on revenue — by line and region, volume vs price vs timing?

_Category: Economics & Plan-vs-Actual · edition `2026-07-27.3` (approved) · report: `docs/project/commercial/reports/BQ-28/2026-07-27.3/report.md`_

**Verdict:** H1 2026 revenue $46.3M vs plan $48.3M (-4.1%, within the ±5% tolerance overall; 4 of 6 lines breach the band individually on the downside); under plan: cloud-suite -16.4%, SP6500 -15.7%, SP6000 -9.1%, PP3500 -6.3%; masked by IP5000 +24.3%, PP3000 +16.1%; 2026-Q2 alone breached at -5.5%

| Expectation | Expected | Actual | Verdict |
|---|---|---|---|
| E-28.1 Year-to-date revenue tracks the 2026 plan within tolerance | within +/- 5% of plan, YTD | -4.1% YTD (H1 2026) — within tolerance overall; 4 of 6 lines breach the ±5% band individually on the downside | met (unvalidated) |

**Issues:**
- I1 (high) — cloud-suite is -16.4% under plan for H1 2026 ($5.0M actual vs $6.0M plan) — beyond the ±5% flagging tolerance
- I2 (high) — SP6500 is -15.7% under plan for H1 2026 ($3.5M actual vs $4.1M plan) — beyond the ±5% flagging tolerance
- I3 (medium) — SP6000 is -9.1% under plan for H1 2026 ($5.0M actual vs $5.5M plan) — beyond the ±5% flagging tolerance
- I4 (medium) — PP3500 is -6.3% under plan for H1 2026 ($22.4M actual vs $23.9M plan) — beyond the ±5% flagging tolerance

**Risks:**
- R1 (medium) — Quarter-over-quarter timing is deteriorating: 2026-Q1 -2.6% → 2026-Q2 -5.5% — the latest quarter breaches the ±5% band on its own
- R2 (medium) — The ±5% tolerance is a stand-in — the plan of record names no reforecast trigger, so the within/outside verdict is only as good as an unratified threshold

_Pins: `commercial/internal-financials@2026-07-27` (43d, fresh); `commercial/internal-revenue-plan@2026-07-27` (43d, fresh)_

### BQ-29 — Is the Cloud Suite attach-rate stage-gate holding — the gate that releases the $24M predictive-monitoring spend?

_Category: Economics & Plan-vs-Actual · edition `2026-07-27.3` (approved) · report: `docs/project/commercial/reports/BQ-29/2026-07-27.3/report.md`_

**Verdict:** The attach stage-gate HOLDS at the stand-in level: 43.0% of the PP3500 installed base (295 of 686 pumps) vs the 40% gate — but the $24M releases on a gate NUMBER nobody has ratified; the strategy of record says 'traction' and sets no threshold — and the verdict is denominator-definition-sensitive: under a whole-PCA denominator (884 pumps incl. 198 unconnectable PP3000) attach reads 33.4%, BELOW the stand-in gate; the metric definition is as unratified as the gate number

| Expectation | Expected | Actual | Verdict |
|---|---|---|---|
| E-29.1 Installed-base Cloud Suite attach reaches the stage-gate level before the predictive-monitoring spend releases | >= 40% of PP3500 installed base attached | 43.0% attach vs the 40% stand-in (+3.0 points); no gate number is ratified in the strategy of record; denominator-sensitive — the whole-PCA basis reads 33.4%, below the gate | met (unvalidated) |

**Risks:**
- R1 (high) — The $24M release decision references a gate with no number of record — the 40% is a stand-in, and at 43.0% attach the reading sits 3.0 points from it; any ratified threshold in that neighborhood flips the verdict — and the metric DEFINITION is equally unratified: the whole-PCA denominator reads 33.4%, below the gate, so the denominator choice alone spans the gate

_Pins: `commercial/internal-subscriptions@2026-07-27.2` (43d, fresh); `commercial/internal-fleet@2026-07-27` (43d, stale)_

### BQ-30 — What's our fully-loaded cost per update, remote vs on-site — and the business case for a remote-first campaign at the top non-connected accounts?

_Category: Economics & Plan-vs-Actual · edition `2026-07-27.3` (approved) · report: `docs/project/commercial/reports/BQ-30/2026-07-27.3/report.md`_

**Verdict:** A remote update costs $120 vs an on-site update between $193 (labor-time floor) and $950 (full-day ceiling) — remote is 12.6–62.1% of on-site depending on unmeasured travel; a $380 adapter pays back in 0.5–5.2 update campaigns at the top non-connected accounts

| Expectation | Expected | Actual | Verdict |
|---|---|---|---|
| E-30.1 A remote update costs a fraction of an on-site visit | remote cost per completed update <= 25% of on-site | remote $120 = 62.1% of the on-site labor floor ($193) but 12.6% of the full-day ceiling ($950) — the ≤25% test depends on the unmeasured travel component | at-risk (unvalidated) |

**Risks:**
- R1 (high) — The fully-loaded on-site cost is unresolvable from campaign data — the $193–$950 bound spans 12.6% to 62.1% on the remote-vs-onsite ratio, and the adapter payback spans 0.5 to 5.2 campaigns — the remote-first decision flips inside that band
- R2 (medium) — All three cost rates are demo stand-ins, not finance-validated (FSE day $950, remote session $120, adapter $380) — and the remote figure is a floor: 10 remote and 7 on-site completions needed a retry whose extra sessions the data does not count

_Pins: `commercial/internal-upgrade-campaign@2026-07-27` (43d, stale); `commercial/internal-fleet@2026-07-27` (43d, stale)_

## Finance

### Not in this pack

| Question | Why | |
|---|---|---|
| FQ-01 | no approved edition | Gross margin by product line and region vs prior year, with standard-vs-actual cost variance by line — which lines are eroding? |
| FQ-02 | not implemented | Price / volume / mix bridge — how much of the revenue and margin change vs prior year is price, how much is volume, how much is mix? |
| FQ-03 | no approved edition | Cost of poor quality — warranty spend, warranty cost per installed unit by line and hardware revision, share linked to complaints; trend? |
| FQ-04 | not implemented | Warranty and service reserve adequacy vs the observed field failure rate — is the reserve keeping up with what the field is costing? |
| FQ-05 | not implemented | Cost of regulatory delay — per month, per product line, what does a slipped clearance cost in deferred revenue and carried spend? |
| FQ-06 | no approved edition | DSO and over-90 AR by GPO and region, inventory days by product line — where is cash trapped? |
| FQ-07 | not implemented | Consumable pull-through vs installed base — are consumable shipments per installed device holding, by line and region? |
| FQ-08 | no approved edition | Budget vs actual year to date by function with headcount variance — which functions breach the tolerance and why? |
| FQ-09 | not implemented | Subscription economics — ARR, net revenue retention, and churn for the cloud suite; is recurring revenue compounding or leaking? |
| FQ-10 | not implemented | R&D spend vs milestone — what has each program consumed against its plan, and what is eligible for capitalization? |

## Manufacturing

### Not in this pack

| Question | Why | |
|---|---|---|
| MQ-01 | no approved edition | First-pass yield, scrap and rework by product line, hw rev, station and site — where is yield eroding, and since when? |
| MQ-02 | not implemented | Capacity vs the demand plan — can each line and site build the planned units, and where is the constraint? |
| MQ-03 | no approved edition | NCR rate and aging, CAPA open count, past-due share and effectiveness-verification backlog — by source and severity. |
| MQ-04 | not implemented | Lot release lead time and DHR completeness — where are lots queuing before release, and is it getting worse? |
| MQ-05 | no approved edition | Supplier quality — incoming reject rate and on-time by supplier and component family, scorecard distribution, single-source exposure, audit currency. |
| MQ-06 | not implemented | Component obsolescence risk by hardware revision — which parts on which revs are single-sourced, end-of-life, or on conditional suppliers? |
| MQ-07 | not implemented | Recall scoping via lot genealogy — if a component lot or process window is implicated, which finished lots and fleet devices are affected? |
| MQ-08 | no approved edition | Process-validation and calibration posture — overdue and due items by site and product line, and the blockers for PP3500 rev C release. |
| MQ-09 | not implemented | Cost of scrap and rework by line and station — what is yield loss costing, and where does a yield point buy the most? |
| MQ-10 | not implemented | Design-transfer readiness per line — are validations, DHR templates, work instructions and training complete for each revision in production? |

