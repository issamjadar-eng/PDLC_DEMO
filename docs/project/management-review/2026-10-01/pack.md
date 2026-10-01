# Management Review Pack — 2026-10-01

_Assembled by the commercial-skill engine from approved answer editions. Every figure below was emitted by a claim-linted edition of the cited question; this pack computes nothing._

## Commercial

### BQ-01 — Which of our five device lines fund the company and which consume it — revenue, margin, trajectory by line?

_Category: Board & Portfolio · edition `2026-07-27.3` (approved) · report: `docs/project/commercial/reports/BQ-01/2026-07-27.3/report.md`_

**Verdict:** PP3500 and cloud-suite fund the company — 59.8% of trailing-4Q gross margin ($27.0M of the portfolio's $45.2M GM on $88.2M revenue, window 2025-Q3..2026-Q2); all 6 lines gross-margin positive; margins compressing on IP5000, PP3000

**Summary:** PP3500 and cloud-suite together generate $27.0M of the portfolio's $45.2M trailing-4Q gross margin — 59.8% of the total — on $88.2M in revenue over 2025-Q3 through 2026-Q2. [derived: totals-stat] [src: commercial/internal-financials@2026-07-27] All six product lines are gross-margin positive, so no line is an immediate drag at the gross level. [derived: gm-by-line] The primary decision this analysis informs is capital and resource allocation: the company's financial floor rests on two lines, and both compression signals on PP3000 and IP5000 warrant active monitoring before they erode the portfolio's margin base. [derived: gm-trend] The critical caveat is that gross margin is the only level at which these conclusions hold — no per-line operating-expense allocation exists, so any line that looks healthy here could still be a net consumer of cash at the operating level. [derived: opex-by-line]

| Expectation | Expected | Actual | Verdict |
|---|---|---|---|
| E-01.1 Every product line is gross-margin positive over the trailing four quarters | gross margin > 0 per line, trailing 4Q | all lines positive; thinnest is PP3000 at 45.3% | met (unvalidated) |

**Risks:**
- R1 (medium) — IP5000 gross margin is compressing — 45.9% in the trailing window vs 47.4% in the prior four quarters (-1.5 pts)
- R2 (medium) — PP3000 gross margin is compressing — 45.3% in the trailing window vs 46.8% in the prior four quarters (-1.5 pts)

_Pins: `commercial/internal-financials@2026-07-27` (66d, fresh)_

### BQ-02 — How concentrated are we — PCA franchise, top-3 GPOs, single systems — and what does losing one anchor GPO do to the 5-year plan?

_Category: Board & Portfolio · edition `2026-07-27.3` (approved) · report: `docs/project/commercial/reports/BQ-02/2026-07-27.3/report.md`_

**Verdict:** Meridian Health Alliance carries 38.4% of FY2025 direct-book revenue — above the 30% guardrail on the direct-book basis, and basis-sensitive: the direct book covers 50.6% of total FY2025 revenue, and Meridian Health Alliance's floor share of TOTAL revenue is 19.4% (under the guardrail); top-3 accounts 25.5%, PCA franchise 74.5%; losing the anchor GPO dents every plan year by $15.6M (14.9% of the FY2026 plan) under the stated constant-dent scenario

**Summary:** Meridian Health Alliance holds 38.4% of FY2025 direct-book revenue — above the 30% concentration guardrail — making it a formal Issue that warrants board-level attention before the next contract cycle [derived: share-by-gpo] [src: commercial/internal-sales-accounts@2026-07-27] [config: commercial.yml]. The breach is real on the direct-book basis, but the guardrail's wording against "annual revenue" creates a defensible reading: the direct book covers only 50.6% of total FY2025 revenue ($80.5M), and Meridian Health Alliance's floor share of total revenue is 19.4%, which does not breach [derived: basis-sensitivity] [src: commercial/internal-financials@2026-07-27]. That ambiguity is not a relief — it is a gap to close by acquiring account-attributed distributor revenue. The decision this report informs is whether to escalate the concentration breach to the board now and begin contract-renewal and diversification planning, or to first resolve the denominator question; the data supports escalating both in parallel. The single biggest caveat: the anchor-GPO loss scenario understates true exposure because the $15.6M dent is held constant while the plan grows — the real downside scales with plan size, not with FY2025 [derived: plan-loss-scenario] [src: commercial/internal-revenue-plan@2026-07-27].

| Expectation | Expected | Actual | Verdict |
|---|---|---|---|
| E-02.1 No single GPO carries more than 30% of annual revenue | <= 30% of FY revenue per GPO | Meridian Health Alliance at 38.4% of FY2025 direct-book revenue; all other GPOs within the guardrail — BASIS-SENSITIVE: the expectation says annual revenue, but the test denominator is the direct book (50.6% of total FY2025 revenue); Meridian Health Alliance's floor share of total revenue is 19.4%, which does NOT breach the guardrail (distributor-routed revenue unattributed) | not-met (unvalidated) |

**Issues:**
- I1 (high) — Meridian Health Alliance holds 38.4% of FY2025 direct-book revenue — over the 30% concentration guardrail

**Risks:**
- R1 (medium) — Top-3 accounts hold 25.5% of FY2025 direct-book revenue — account-level concentration compounds the GPO concentration (largest: Northgate Health System at 11.0%)
- R2 (medium) — The loss scenario is a floor, not a forecast: the dent is held constant at the FY2025 anchor book ($15.6M) while the plan grows, and it covers the direct book only — the true dent of losing Meridian Health Alliance grows with the plan
- R3 (medium) — The E-02.1 verdict is basis-sensitive: the guardrail is worded against annual revenue but tested on the direct book, which covers 50.6% of total FY2025 revenue — Meridian Health Alliance breaches on the direct book (38.4%) while its floor share of total revenue (19.4%) does not breach

_Pins: `commercial/internal-sales-accounts@2026-07-27` (66d, fresh); `commercial/internal-revenue-plan@2026-07-27` (66d, fresh); `commercial/internal-financials@2026-07-27` (66d, fresh)_

### BQ-03 — What share of revenue is recurring today vs the Y5 plan — and which parts of the $350M target are contracted, modeled, or aspiration?

_Category: Board & Portfolio · edition `2026-07-27.4` (approved) · report: `docs/project/commercial/reports/BQ-03/2026-07-27.4/report.md`_

**Verdict:** Recurring revenue is 10.8% of revenue today (FY2026H1) vs 68.6% planned for FY2030; of the $350.0M target, $128.0M rides on already-cleared products, $12.0M on letter-to-file changes, and $210.0M (60.0%) sits behind FDA decisions not yet received — and within the $240.0M recurring proxy itself, $210.0M (87.5%) is behind those decisions

**Summary:** Recurring revenue stands at 10.8% of revenue in FY2026H1 against a FY2030 plan of 68.6% — the distance between those two numbers is the central commercial risk. [derived: v-main] [src: commercial/internal-financials@2026-07-27] [src: commercial/internal-revenue-plan@2026-07-27] Of the $350.0M FY2030 target, $128.0M rests on already-cleared products, $12.0M on letter-to-file execution, and $210.0M — 60.0% — waits on FDA decisions not yet received. [src: commercial/internal-revenue-plan@2026-07-27] [derived: y5-decomposition] The exposure is sharper inside the recurring line: 87.5% of the $240.0M cloud-suite recurring proxy ($210.0M) sits behind those same pending decisions, versus 60.0% blended across all revenue. [derived: y5-recurring-decomposition] [src: commercial/internal-revenue-plan@2026-07-27] This report informs whether to carry the aspiration bucket at plan value or to require a regulatory-contingency scenario. The single biggest caveat is that the recurring proxy carries $0.0M in letter-to-file coverage — every dollar of recurring revenue above the $30.0M cleared floor requires an FDA decision. [derived: y5-recurring-decomposition] [src: commercial/internal-revenue-plan@2026-07-27]

| Expectation | Expected | Actual | Verdict |
|---|---|---|---|
| E-03.1 Recurring (subscription) revenue share grows every fiscal year toward the Y5 model | recurring share strictly increasing FY2024 -> FY2026 | FY2024: 5.0%; FY2025: 7.9%; FY2026H1: 10.8% — strictly increasing | met (unvalidated) |

**Risks:**
- R1 (high) — 60.0% of the FY2030 target ($210.0M) is aspiration — revenue behind pccp-enabled and new-submission FDA decisions not yet received — and the blended figure understates the recurring-specific bet: within the cloud-suite recurring proxy alone, 87.5% ($210.0M of $240.0M) sits behind those decisions; the regulatory-exposure and slip arithmetic is BQ-05's answer

_Pins: `commercial/internal-financials@2026-07-27` (66d, fresh); `commercial/internal-revenue-plan@2026-07-27` (66d, fresh)_

### BQ-04 — Does the subscription model work at unit level — LTV per connected pump vs cost-to-serve, and is Cloud Suite cannibalizing hardware ASP?

_Category: Board & Portfolio · edition `2026-07-27.3` (approved) · report: `docs/project/commercial/reports/BQ-04/2026-07-27.3/report.md`_

**Verdict:** Unit economics fail the guardrail: LTV per connected pump $2,237 vs $2,720 cost-to-serve over the same 5-year horizon (ratio 0.82 vs the 3.0 floor); 28 of 39 active sites run ARR below cost-to-serve — concentrated in small sites — and the mean hardware discount at subscribed sites is 5.8% vs the 5% tolerance

**Summary:** The Cloud Suite subscription is loss-making at the unit level: LTV per connected pump is $2,237 against a $2,720 cost-to-serve over the same 5-year horizon, a ratio of 0.82 against the 3.0 floor. [derived: unit-econ-stat] [config: commercial.yml] The structural cause is small sites: all 24 sites with 6 or fewer pumps are individually below cost, and 28 of 39 active sites run ARR below annual cost-to-serve. [derived: band-economics] [src: commercial/internal-subscriptions@2026-07-27.2] This informs one immediate decision: stop expanding the small-site segment before fixing the cost-to-serve model; the 4 connected sites with no subscription are a better near-term revenue target. [derived: attach-gap] [src: commercial/internal-fleet@2026-07-27] The biggest caveat is that the 3.0 LTV floor and the 5% hardware-discount tolerance are both unvalidated stand-ins, and the LTV model itself overstates — no churn decrement, no discounting — while 3 churned sites are already on file. [derived: unit-econ-stat] [config: commercial.yml] [src: commercial/internal-subscriptions@2026-07-27.2]

| Expectation | Expected | Actual | Verdict |
|---|---|---|---|
| E-04.1 Lifetime value per connected pump covers cost-to-serve at a healthy multiple | LTV : cost-to-serve >= 3.0 | ratio 0.82 (ARR $447/pump/yr vs cost $544/pump/yr, active sites; ratio computed on raw sums, rounded for display) | not-met (unvalidated) |
| E-04.2 Cloud Suite attach does not erode hardware pricing beyond tolerance | avg hardware discount at subscribed sites <= 5% | mean hardware discount 5.8% across 39 active subscribed sites — +0.8pp vs the 5% stand-in line; KNIFE-EDGE on |miss| ≤ 1pp (miss = 2.1 SE, SE ≈ 0.4pp, n=39) against an unvalidated threshold — verdict fragile to the stand-in choice | not-met (unvalidated) |

**Issues:**
- I1 (high) — Small sites are negative at unit level: 24 sites (<= 6 pumps) run $460/pump/yr below water (24 of them ARR-below-cost individually)
- I2 (medium) — Mean hardware discount at subscribed sites is 5.8%, over the 5% tolerance — the subscription may be being bought with hardware price

**Risks:**
- R1 (high) — Fleet-wide LTV:cost-to-serve is 0.82, under the 3.0 floor — and the LTV side is flattered by the model (no churn decrement, no discounting) while 3 churned sites already exist

_Pins: `commercial/internal-subscriptions@2026-07-27.2` (66d, fresh); `commercial/internal-fleet@2026-07-27` (66d, stale)_

### BQ-05 — How much plan revenue sits behind FDA decisions we haven't received — by regulatory dependency, with slip triggers?

_Category: Board & Portfolio · edition `2026-07-27.3` (approved) · report: `docs/project/commercial/reports/BQ-05/2026-07-27.3/report.md`_

**Verdict:** $366.0M of the $1,000.0M five-year plan sits behind FDA decisions not yet received; exposure crosses the 40% threshold in FY2029, FY2030 (peak 60.0% in FY2030)

**Summary:** $366.0M of the $1,000.0M five-year plan sits behind FDA decisions not yet received, and exposure crosses the 40% risk-appetite threshold in both FY2029 and FY2030, peaking at 60.0% in FY2030 [derived: v-main] [src: commercial/internal-revenue-plan@2026-07-27] [config: commercial.yml]. This matters because regulatory slips in the back half of the plan are not academic: a uniform 12-month slip of all dependent revenue would push $210.0M out of the five-year window entirely [derived: slip-scenarios] [src: commercial/internal-revenue-plan@2026-07-27] [config: commercial.yml]. The decision this informs is whether the current plan narrative can be approved without formal contingencies — the answer, under any reasonable risk standard, is no for FY2029 and FY2030. The single biggest caveat is that the 40% threshold is a stand-in that the plan of record does not itself set [derived: exposure-by-year] [config: commercial.yml]; if the board has a different appetite, the breach line moves, but the concentration pattern does not.

| Expectation | Expected | Actual | Verdict |
|---|---|---|---|
| E-05.1 Regulatory-dependent revenue stays below the exposure threshold in every plan year | <= 40% of plan-year revenue behind not-yet-received FDA decisions | FY2026: 0.0%; FY2027: 8.5%; FY2028: 23.5%; FY2029: 42.9%; FY2030: 60.0% — over threshold in FY2029, FY2030 | not-met (unvalidated) |

**Issues:**
- I1 (high) — FY2029 exposure is 42.9% — $105.0M of $245.0M sits behind pccp-enabled or new-submission decisions, over the 40% threshold
- I2 (high) — FY2030 exposure is 60.0% — $210.0M of $350.0M sits behind pccp-enabled or new-submission decisions, over the 40% threshold

**Risks:**
- R1 (medium) — A uniform 6-month slip of all dependent revenue cuts FY2030 by $52.5M and pushes $105.0M past FY2030 — out of the five-year window entirely
- R2 (high) — A uniform 12-month slip of all dependent revenue cuts FY2030 by $105.0M and pushes $210.0M past FY2030 — out of the five-year window entirely

_Pins: `commercial/internal-revenue-plan@2026-07-27` (66d, fresh); `commercial/openfda-510k-infusion@2026-07-22` (71d, fresh)_

### BQ-06 — Is the concept pipeline converting, and how does our clearance cycle time compare with our own history and with BD/Baxter?

_Category: Board & Portfolio · edition `2026-07-27.2` (approved) · report: `docs/project/commercial/reports/BQ-06/2026-07-27.2/report.md`_

**Verdict:** Competitor 510(k) review runs a median 213 days received→decision across 29 infusion-pump clearances since 2021; fastest frequent filer is Baxter Healthcare Corporation at 74 days median

**Summary:** Across 29 infusion-pump 510(k) clearances since 2021, competitors face a median review interval of 213 days from receipt to decision [derived: cycle-by-applicant] [src: commercial/openfda-510k-infusion@2026-07-22]. Baxter Healthcare Corporation, the dominant frequent filer with 9 clearances in the period, achieves a median of 74 days — nearly three times faster than the field [src: commercial/openfda-510k-infusion@2026-07-22]. This gap matters for launch planning: a team targeting Baxter-level speed needs to understand what drives that difference, while a team planning conservatively should budget closer to the 213-day field median [derived: cycle-by-applicant] [src: commercial/openfda-510k-infusion@2026-07-22]. The single biggest caveat is that our own received→decision history is not yet available as a corpus dataset, so no internal benchmark exists to compare against the competitor baseline [derived: v-main] [src: commercial/openfda-510k-infusion@2026-07-22].

_Pins: `commercial/openfda-510k-infusion@2026-07-22` (71d, fresh)_

### BQ-07 — What is our actual share of the US PCA/smart-pump segment — taking share from BD/Baxter or growing with the market?

_Category: Market & Competitive · edition `2026-07-27.3` (approved) · report: `docs/project/commercial/reports/BQ-07/2026-07-27.3/report.md`_

**Verdict:** US (NA-proxy) PCA/LVP smart-pump share is a RANGE, not a number: ~0.029%–0.047% of installed base and ~0.55%–1.1% of annual segment dollars (A-003 denominator, LOW confidence); our installed base grew ~16.0%/yr vs the assumed market ~7.3%/yr — directionally gaining, from a tiny base (mismatched bases: ours is UNIT growth of our NA in-segment book; A-003's rate is the DOLLAR CAGR of the total US infusion-pump market — directional comparison only)

**Summary:** Our US PCA/LVP smart-pump position as of FY2026H1 is a range: ~0.029%–0.047% of the installed base and ~0.55%–1.1% of annual segment dollars [derived: share-range] [assume: A-003] [src: commercial/internal-sales-accounts@2026-07-27]. The single biggest caveat is that the denominator carries LOW confidence — it comes from a triangulated assumption, not a public census, and if it is off by a large factor the share figures shift proportionally [assume: A-003]. Our installed base grew ~16.0%/yr against a market growing ~7.3%/yr, which is the only directional evidence of share gain at this scale, but the rates are not directly comparable: ours is unit growth of our NA in-segment book while the market figure is a dollar CAGR of the total US infusion-pump market [derived: growth-rate] [assume: A-003]. The decision this informs: treat share as an order-of-magnitude position marker, not a competitive benchmark, until analyst unit data is purchased to retire the A-003 denominator [assume: A-003].

**Risks:**
- R1 (high) — The entire share figure rests on A-003 (LOW confidence, triangulated from public analyst-report summaries) — the denominator could be off by a large factor, and the unit-share and dollar-share bases already tell different stories (stock share vs flow share)
- R2 (medium) — US share is proxied by the NA region and the denominator is held constant across fiscal years (market growth not modeled per-year) — both stated simplifications of the committed plan

_Pins: `commercial/internal-sales-accounts@2026-07-27` (66d, fresh)_

### BQ-08 — What are we winning and losing on — and how many recent losses cite predictive monitoring we don't have?

_Category: Market & Competitive · edition `2026-07-27.3` (approved) · report: `docs/project/commercial/reports/BQ-08/2026-07-27.3/report.md`_

**Verdict:** Trailing-365d win rate is 58.7% of decided opportunities (37 won / 26 lost; 18 no-decision excluded) vs the 50% stand-in target; dollar-weighted we win 61.4% of decided CRM value ($30,389,000 won vs $19,071,000 lost — we win bigger deals than we lose); 8 of 26 losses (30.8%) have the predictive-monitoring gap primary or cited — $4,792,000 in CRM value

**Summary:** We win at a rate above the stand-in target: 58.7% of decided opportunities in the trailing 365 days, and 61.4% of decided CRM value ($30,389,000 won vs $19,071,000 lost) — we close larger deals than we lose [derived: win-rate] [derived: value-win-rate] [src: commercial/internal-winloss@2026-07-27.4]. The predictive-monitoring gap is the most actionable loss driver: it appears as a primary or cited reason in 8 of 26 in-window losses (30.8%), representing $4,792,000 in CRM opportunity value [derived: pm-gap-losses] [src: commercial/internal-winloss@2026-07-27.4]. That concentration is the strongest data-backed input for the Y3 roadmap investment case. The key caveat: the 58.7% win rate rests on excluding 18 no-decision outcomes from the denominator; counting them as losses drops the rate to 45.7%, so the "met" verdict is denominator-sensitive [derived: win-rate] [src: commercial/internal-winloss@2026-07-27.4].

| Expectation | Expected | Actual | Verdict |
|---|---|---|---|
| E-08.1 Competitive win rate holds at or above half of decided opportunities | >= 50% of won+lost | 58.7% of decided (37W/26L, window 2025-07-20 → 2026-07-20); sensitivity: 45.7% if the 18 no-decisions count as losses — the verdict is denominator-sensitive, not just sample-sensitive | met (unvalidated) |

**Risks:**
- R1 (high) — Predictive-monitoring gap touches 30.8% of in-window losses (8 deals, $4,792,000 CRM value; primary reason in 5 of them) — the largest addressable feature-driven loss pool
- R2 (medium) — Loss attribution is the CRM's single primary_reason per opportunity — a recorded citation is not proof the gap decided the deal

_Pins: `commercial/internal-winloss@2026-07-27.4` (66d, stale)_

### BQ-09 — Are we winning displaced accounts where an incumbent has an open recall or integration disruption — and how long does the window stay open?

_Category: Market & Competitive · edition `2026-07-27.3` (approved) · report: `docs/project/commercial/reports/BQ-09/2026-07-27.3/report.md`_

**Verdict:** Method demo (fabricated CRM joined to REAL FDA recall dates): we win 67.3% of decided opportunities where the incumbent had an FRN recall posted within 180 days of close (n=55) vs 14.3% outside the window (n=7); there is no uniform decay across the interior buckets (65.8% → 70.6% → 0.0%); the >12 months / no prior recall tail sits at 50.0% (n=2)

**Summary:** The recall disruption window is a real targeting signal worth operationalizing — but the win rates shown are a method demonstration on fabricated data and must not drive strategy until re-run against an actual CRM export. When an incumbent had an FRN recall posted within 180 days of close, the demo dataset shows a win rate of 67.3% (n=55) versus 14.3% outside that window (n=7) [derived: v-main] [src: commercial/internal-winloss@2026-07-27.4] [src: commercial/openfda-recalls-infusion@2026-07-22] [config: commercial.yml]. The infusion incumbents produce sustained recall activity — Baxter alone posted 27 FRN recalls since 2021 [src: commercial/openfda-recalls-infusion@2026-07-22] [config: entity-aliases.yml] — which means real deal pipelines will surface recall-window opportunities frequently if this targeting logic is operationalized. The analysis informs one decision: whether to build FDA recall monitoring into field sales targeting; the join method is validated and reusable, but the effect size is not. The single biggest caveat is structural: 55 of 62 decided incumbent-held opportunities already fall inside the window [derived: decay-buckets] [src: commercial/openfda-recalls-infusion@2026-07-22], leaving a control group of only 7 [derived: window-split] [src: commercial/internal-winloss@2026-07-27.4], so the binary contrast carries limited weight on its own.

**Risks:**
- R1 (high) — The effect size is NOT market evidence: opportunity records are demo-fabricated and their seeded disruption windows were set independently of the real recall calendar — only the join method generalizes
- R2 (medium) — Large incumbents recall so often that 55 of 62 decided incumbent-held opportunities fall in-window — the out-of-window control group (n=7) is too small to carry weight on its own

_Pins: `commercial/internal-winloss@2026-07-27.4` (66d, stale); `commercial/openfda-recalls-infusion@2026-07-22` (71d, stale)_

### BQ-10 — Where do we sit vs Alaris/Spectrum IQ/Plum 360 on 5-year TCO per pump — the buyer's spreadsheet?

_Category: Market & Competitive · edition `2026-07-27.3` (approved) · report: `docs/project/commercial/reports/BQ-10/2026-07-27.3/report.md`_

**Verdict:** Indicative, assumption-bounded: our 5-yr TCO is $8,900/pump all-in ($5,100 on the capital+service basis) vs a class-wide competitor range of ~$3,000–$15,000 on capital+service ONLY — competitor consumables and software subscription are undisclosed and excluded, so their true all-in TCO sits ABOVE that range; the ranges overlap and no hard we-win claim is supportable

**Summary:** The PP3500's 5-year all-in TCO is $8,900 per pump [derived: v-main] [config: commercial.yml], and $5,100 on the capital-plus-service basis used for competitive comparison [derived: our-tco]. The class-wide competitor range on that same basis is $3,000–$15,000 [assume: A-004], but it excludes consumables and software subscription — both undisclosed — meaning competitor true all-in cost sits strictly above that range; the ranges overlap and no hard cost-leadership claim is supportable [derived: v-main]. The decision this informs is whether to deploy a TCO argument in buyer conversations; the analysis says to hold until finance ratifies the per-pump constants [config: commercial.yml] and the competitor pricing assumption is refreshed [assume: A-004]. The single biggest caveat is structural: the two sides of the comparison are not built the same way, and any buyer-facing presentation that omits that disclosure misleads rather than persuades [assume: A-004] [derived: tco-comparison].

**Risks:**
- R1 (high) — The comparison is not like-for-like by construction: the competitor range excludes consumables (undisclosed) and quantifies software subscription only as 'required, magnitude unknown', while our figure includes both — the spread understates competitor cost
- R2 (medium) — Our own cost constants are demo stand-ins, not finance-validated rates — both sides of the buyer's spreadsheet are currently unvalidated

_Pins: `commercial/external-competitor-features@2026-07-27` (66d, fresh)_

### BQ-11 — Where are pumps sold but underused — accounts whose utilization/telemetry diverges from what they bought?

_Category: Market & Competitive · edition `2026-07-27.3` (approved) · report: `docs/project/commercial/reports/BQ-11/2026-07-27.3/report.md`_

**Verdict:** 6 connected site(s) ran below 60% of expected infusion hours over 2026-05..2026-07 (worst 34.0%); 2 clear the ≥10-connected-device materiality bar (S-NA-22, S-EMEA-02); the account-revenue tie the question asks for is blocked — no site→account key exists in any pinned dataset

**Summary:** Two connected sites — S-NA-22 and S-EMEA-02 — cleared the 10-device materiality bar and ran at 35.3% and 36.6% of expected infusion hours respectively over the trailing three months 2026-05..2026-07, signaling early churn risk at material scale [derived: flagged-sites] [src: commercial/internal-telemetry-utilization@2026-07-27] [src: commercial/internal-fleet@2026-07-27] [config: commercial.yml]. The connected-fleet median for the same window was 89.6% across 46 sites [derived: site-utilization] [src: commercial/internal-telemetry-utilization@2026-07-27], so these sites are not tracking a fleet-wide dip — they are structural outliers. The data supports an immediate customer-success intervention at both material sites to determine whether the shortfall is case-mix, shelfware, or connectivity failure before renewals close. Dollar exposure cannot be sized: no site-to-account key exists in any pinned dataset, so revenue at risk stays a regional estimate rather than an account-level figure [derived: account-revenue-at-risk] [derived: v-main] [src: commercial/internal-telemetry-utilization@2026-07-27] [src: commercial/internal-fleet@2026-07-27] [config: commercial.yml].

| Expectation | Expected | Actual | Verdict |
|---|---|---|---|
| E-11.1 No material account runs its connected fleet below the utilization floor | >= 60% of expected hours at every account with >= 10 connected devices | site-level proxy (account join unavailable): 2 site(s) with >= 10 connected devices below 60%: S-NA-22 35.3%; S-EMEA-02 36.6% | not-met (unvalidated) |

**Issues:**
- I1 (high) — S-NA-22 runs at 35.3% of expected hours across 19 connected devices over 2026-05..2026-07 — sold-but-underused at material scale (early churn warning)
- I2 (high) — S-EMEA-02 runs at 36.6% of expected hours across 16 connected devices over 2026-05..2026-07 — sold-but-underused at material scale (early churn warning)

**Risks:**
- R1 (high) — Account-level revenue-at-risk cannot be computed: no pinned dataset carries a site→account key (sales-accounts is account-level with no site list) — the churn-risk framing stops at regional context
- R2 (medium) — expected_hours is the dataset's per-segment norm, not a contract term — a site with a legitimately different case mix looks underused against it

_Pins: `commercial/internal-telemetry-utilization@2026-07-27` (66d, stale); `commercial/internal-fleet@2026-07-27` (66d, stale); `commercial/internal-sales-accounts@2026-07-27` (66d, fresh)_

### BQ-12 — What did competitors clear in the last 90 days, laid against our Y1–Y5 roadmap — anything landing on a feature we scheduled two years out?

_Category: Roadmap & State of the Art · edition `2026-07-27.2` (approved) · report: `docs/project/commercial/reports/BQ-12/2026-07-27.2/report.md`_

**Verdict:** 1 infusion-pump clearance(s) in the 90-day window ending 2026-01-28; 0 flag roadmap-relevant keywords — review against the roadmap lanes

**Summary:** The 90-day sweep ending 2026-01-28 found 1 FRN infusion-pump clearance and 0 entries flagging roadmap-relevant keywords [derived: v-main] [src: commercial/openfda-510k-infusion@2026-07-22]. No competitive response on any roadmap lane is required by this result. For context, the quarterly FRN series shows the 1-clearance count is consistent with the low-volume pattern seen across most periods since early 2024, with the exception of 4 clearances in the quarter starting 2025-04-01 [src: commercial/openfda-510k-infusion@2026-07-22]. The primary caveat is dataset scope: FRN product code only; adjacent SaMD and monitoring codes are not covered, so this sweep does not address potential entrant activity in those segments [config: commercial.yml].

_Pins: `commercial/openfda-510k-infusion@2026-07-22` (71d, fresh)_

### BQ-13 — How much runway before someone closes the predictive-monitoring gap — is our Y3 timing defensible, and what if an incumbent buys an AI entrant?

_Category: Roadmap & State of the Art · edition `2026-07-27.3` (approved) · report: `docs/project/commercial/reports/BQ-13/2026-07-27.3/report.md`_

**Verdict:** Nobody in the competitive matrix documents predictive monitoring today, but the runway is assumption-thin: a SaMD-only entrant starting at the data anchor (2026-01-28) could clear 2027-07-28 to 2028-01-28 — about 5 months before our F6 2028-H2 launch anchor; an incumbent acquisition inherits the same clock; 0 ai/predictive-flagged clearance(s) in the trailing-12-month watch. The hardware-scenario reassurance is FRAGILE: its fast edge clears the favorable launch anchor by only 27 days and beats an end-of-2028-H2 launch reading by ~5 months — and the H2 anchor refinement is a catalog config choice, not a strategy-doc commitment

**Summary:** No competitor in the documented matrix ships predictive monitoring today — all 5 products checked return `no` [derived: predictive-shipping-check] [src: commercial/external-competitor-features@2026-07-27]. That gap is real but time-limited: a SaMD-only entrant starting at the data anchor could clear as early as 2027-07-28, about 5 months before our F6 launch anchor [derived: runway-margin] [assume: A-005] [src: commercial/openfda-510k-infusion@2026-07-22] [config: commercial.yml]. An incumbent acquiring an AI entrant inherits the same window and the same threat [assume: A-005] [derived: entry-scenarios] [config: commercial.yml]. The hardware-integrated scenario appears to clear after our anchor, but that margin is 27 days at the fast edge — and flips entirely under the end-of-period reading [derived: hardware-edge-margin] [assume: A-005] [config: commercial.yml]. The decision this informs: accelerate F6 or lock the H2 launch anchor in the strategy document, where it currently exists only as a config entry, not a commitment [derived: v-main] [config: commercial.yml]. The biggest caveat: every runway figure starts the entrant clock at the data anchor (2026-01-28), so any program already underway beats all of them [assume: A-005] [src: commercial/openfda-510k-infusion@2026-07-22].

**Risks:**
- R1 (high) — The F6 runway verdict is assumption-bounded: the entire lead-time model is A-005 (medium confidence), and the entrant clock is modeled from the data anchor (2026-01-28) — a program already underway is ahead of every figure here
- R2 (medium) — Acquisition scenario: an incumbent buying an AI entrant applies the 18-24-month SaMD clock to an established hospital channel — the fastest modeled path to closing our gap, and it is an assumption-class scenario, not an observed signal
- R3 (medium) — The hardware-scenario reassurance ('clears after our launch anchor') holds by only 27 days at the fast edge under the favorable anchor reading, and flips under the end-of-period reading (2028-12-31: the fast edge beats our launch by ~5 months); the H2 anchor refinement itself is a catalog config choice — the strategy doc commits only 'Y3 (2028)'

_Pins: `commercial/openfda-510k-infusion@2026-07-22` (71d, fresh); `commercial/external-competitor-features@2026-07-27` (66d, fresh)_

### BQ-14 — Where exactly do we sit on PCA feature parity, line by line — which gaps are on the roadmap vs silently unaddressed?

_Category: Roadmap & State of the Art · edition `2026-07-27.3` (approved) · report: `docs/project/commercial/reports/BQ-14/2026-07-27.3/report.md`_

**Verdict:** 10 attributes compared: 2 ahead, 4 parity, 4 behind — 3 behind-gaps have a roadmap lane (of which 2 adjacency-only: integrated_etco2, pca_pause_or_etco2 — the lane responds but does not mechanically close the gap), 1 SILENTLY UNADDRESSED (weight_kg)

**Summary:** Across 10 attributes compared, the product is ahead on 2, at parity on 4, and behind on 4 [derived: v-main] [src: commercial/external-competitor-features@2026-07-27] [config: commercial.yml]. The 2 leads — battery life at 150 hours and flow accuracy at 0.35 — are clear differentiators against best-in-class and should anchor competitive positioning [src: commercial/external-competitor-features@2026-07-27] [config: commercial.yml]. Among the 4 behind-gaps, 1 is roadmap-committed with a closing lane, 2 are acknowledged via adjacency lanes that do not mechanically close the gap, and 1 — weight at 0.75 kg against a best competitor at 0.45 kg — has no lane at all [derived: v-main] [src: commercial/external-competitor-features@2026-07-27] [config: commercial.yml]. The decision this report requires is a roadmap-council vote on weight: explicitly accept the gap as a trade-off or assign it a lane [src: commercial/external-competitor-features@2026-07-27] [derived: parity-matrix] [config: commercial.yml]. The biggest caveat: 2 of the 10 verdicts carry provisional flags and must be re-confirmed from source before any external-facing use [src: commercial/external-competitor-features@2026-07-27].

**Issues:**
- I1 (high) — weight_kg is behind (0.75 vs Smiths Medical (ICU Medical) CADD Legacy at 0.45) and NO roadmap lane owns the gap — silently unaddressed, nobody has decided about it

**Risks:**
- R1 (high) — BD ships PCA Pause and integrated EtCO2 today while our nearest roadmap answers sit in the F4 (Y2 (2027)) and F6 (Y3 (2028)) slots — and BOTH lane assignments are adjacency, not closure: F4 is smart alarm filtering and F6 is predictive monitoring, neither a hardware PCA-pause response nor a capnography module, so BD's shipped capability may remain unanswered even after F4/F6 land

_Pins: `commercial/external-competitor-features@2026-07-27` (66d, fresh)_

### BQ-15 — Is the state-of-the-art analysis still current (EU MDR), and are our headline spec differentiators still ahead?

_Category: Roadmap & State of the Art · edition `2026-07-27.3` (approved) · report: `docs/project/commercial/reports/BQ-15/2026-07-27.3/report.md`_

**Verdict:** ride to scheduled review (2027-04-12): both differentiators remain ahead of every documented competitor value and no refresh trigger fired. Accuracy margin ~6.6x vs best documented competitor on our LAB-basis spec (~4.6x on our volumetric-basis spec — ahead on either basis; competitor cells are nominal/field specs), battery ~2.1x; 0 FRN clearance(s) observed after the SOTA anchor date (2026-04-12) in a snapshot whose coverage ends 2026-01-28

**Summary:** Both headline differentiators remain ahead of every documented competitor value and the refresh rule shows no trigger — ride to the scheduled review on 2027-04-12 [derived: v-refresh] [config: commercial.yml]. Flow accuracy leads the best documented competitor by ~6.6x on the laboratory-basis spec and ~4.6x on the volumetric-basis spec; battery life leads the best documented competitor by ~2.1x — both margins positive on every basis tested [derived: differentiator-margins] [src: commercial/external-competitor-features@2026-07-27] [config: commercial.yml]. The data informs the decision of whether to refresh the SOTA document now or hold; the deterministic rule supports holding [derived: v-refresh] [config: commercial.yml]. The single biggest caveat is that the 510(k) snapshot's coverage ends 2026-01-28, so a clearance decided after that date is invisible — 0 clearances observed is lag-limited, not confirmed quiet [derived: since-doc-count] [src: commercial/openfda-510k-infusion@2026-07-22].

**Risks:**
- R1 (medium) — The currency signal is lag-limited: the 510(k) snapshot's coverage ends 2026-01-28, months before the snapshot's acquisition — a recent clearance may already exist unseen

_Pins: `commercial/external-competitor-features@2026-07-27` (66d, fresh); `commercial/openfda-510k-infusion@2026-07-22` (71d, fresh)_

### BQ-16 — For each roadmap feature: documented KOL evidence on file? Which ride on a single voice, and does current sentiment still order the waves?

_Category: Roadmap & State of the Art · edition `2026-07-27.3` (approved) · report: `docs/project/commercial/reports/BQ-16/2026-07-27.3/report.md`_

**Verdict:** META-GAP: all 38 evidence rows are a simulated advisory panel — zero real collected KOL evidence exists (no interviews, surveys, or publications). Within the simulated register: F9 rides on a single voice (E-16.1 floor not met), and the F4, F6, F7, F8 wave slots carry concern-majority sentiment — read as NO documented endorsement of those slots, not as opposition: the register's 3-value vocabulary collapses conditional support into `concern` (stated limitation)

**Summary:** Every roadmap commitment in this program rests on zero real collected KOL evidence — all 38 evidence rows in the register are simulated advisory-panel material; real interviews, surveys, and publications each stand at 0 [derived: evidence-type-census] [src: commercial/internal-kol-register@2026-07-27]. That matters because four committed middle-wave slots (F4, F6, F7, F8) show concern-majority sentiment in the simulated panel and carry no documented endorsement, while F9 (international expansion) rides on a single voice — below the 2-voice floor set by E-16.1 [derived: voices-per-feature] [config: commercial.yml] [src: commercial/internal-kol-register@2026-07-27]. The decision this report informs is a go/no-go on the next roadmap commit: the evidence base needs to be rebuilt from real engagement before that gate. The single biggest caveat is that concern-majority does not equal opposition — the register's 3-value vocabulary collapses conditional support into `concern`, and source documents confirm that specific voices on F4 and F7 explicitly endorsed the sequencing while attaching conditions [derived: v-main] [src: commercial/internal-kol-register@2026-07-27].

| Expectation | Expected | Actual | Verdict |
|---|---|---|---|
| E-16.1 Every committed roadmap feature has at least two independent KOL voices on file | >= 2 distinct KOLs per F1-F9 feature | distinct simulated-panel voices per feature — F1: 5; F2: 3; F3: 3; F4: 6; F5: 4; F6: 5; F7: 5; F8: 6; F9: 1; features below the floor: F9 (and zero REAL voices everywhere — see meta-gap) | not-met (unvalidated) |

**Issues:**
- I1 (high) — Zero real collected KOL evidence exists behind any of the 9 committed roadmap features — the entire register (38 rows) is simulated panel material
- I2 (medium) — F9 fails even the simulated-panel two-voice floor (E-16.1) — the weakest-evidenced committed bet(s)

**Risks:**
- R1 (medium) — The committed middle-wave slots (F4, F6, F7, F8) carry concern-majority sentiment — no documented endorsement of those slots exists. Caveat: the 3-value vocabulary flattens conditional support into concern (source docs show conditional-yes voices on F4 and F7), so this is an evidence-absence signal, not measured opposition

_Pins: `commercial/internal-kol-register@2026-07-27` (66d, fresh)_

### BQ-17 — Stacked against clearances, KOL data, and attach actuals — which roadmap bet do we kill, and which do we pull forward a year?

_Category: Roadmap & State of the Art · edition `2026-07-27.3` (approved) · report: `docs/project/commercial/reports/BQ-17/2026-07-27.3/report.md`_

**Verdict:** Decision support, not the decision: pull-forward candidate F4 Alerts Engine v1 (smart alarm filtering) (composite 0.616, tie with F6 broken on earliest wave); kill candidate F9 International expansion (EU MDR / Canada) (composite 0.0, tie with F7 broken on weakest evidence base) — sentiment axis is simulated-panel only, demand axis is Cloud attach 84.8%. CAUTION on the kill read: the single F9 voice argues the slot is too LATE and too THIN — a voice FOR earlier EU investment, arithmetically converted into kill support by the 3-value sentiment vocabulary

**Summary:** Pull F4 Alerts Engine v1 (smart alarm filtering) into Y2 (2027) and flag F9 International expansion (EU MDR / Canada) for the kill discussion — the composite model outputs scores of 0.616 and 0.0 for those two features respectively [derived: composite] [config: commercial.yml]. Both picks are resolved by tiebreakers, not by score margin, so the ranking is decision support for the council, not a mandate [derived: composite] [config: commercial.yml]. F4's pull-forward case rests on maximum competitive pressure and a Cloud Suite attach of 84.8% [derived: attach-rate] [src: commercial/internal-subscriptions@2026-07-27.2] [src: commercial/internal-fleet@2026-07-27], making it the top eligible candidate by composite. The critical caveat sits entirely on the kill side: the only KOL voice on file for F9 (Kuitunen) argues for earlier EU evidence investment — a stance the 3-value sentiment vocabulary converts into kill support, so the kill ranking is contradicted by its own only evidence [src: commercial/internal-kol-register@2026-07-27] [derived: composite].

**Issues:**
- I1 (high) — Direction inversion on the kill candidate: the single F9 voice on file (Kuitunen) argues F9 is too LATE and too THIN — advocating earlier EU evidence investment — but the 3-value sentiment vocabulary encodes it as bare concern, arithmetically supporting the kill ranking; the only evidence on file contradicts the kill reading

**Risks:**
- R1 (high) — The kill ranking rests on a composite whose sentiment third is simulated and whose demand third does not exist for non-cloud features — F9 scores zero pressure, zero measured demand, and its sentiment comes from 1 simulated voice(s)
- R2 (medium) — F9 and F7 tie exactly at composite 0.0 — only evidence thinness separates the kill candidate from the runner(s)-up

_Pins: `commercial/internal-kol-register@2026-07-27` (66d, fresh); `commercial/external-competitor-features@2026-07-27` (66d, fresh); `commercial/openfda-510k-infusion@2026-07-22` (71d, fresh); `commercial/internal-subscriptions@2026-07-27.2` (66d, fresh); `commercial/internal-fleet@2026-07-27` (66d, stale)_

### BQ-18 — Top three complaint categories this quarter, rate-normalized with a stated denominator — any trending above the risk-file commitment?

_Category: Field: Complaints & Safety · edition `2026-07-27.3` (approved) · report: `docs/project/commercial/reports/BQ-18/2026-07-27.3/report.md`_

**Verdict:** CAPA-review trigger: occlusion-alarm at 3.17 per 100 devices vs threshold 3.0; connectivity at 2.26 per 100 devices vs threshold 2.0 (trailing 90d ending 2026-07-17)

**Summary:** Two complaint categories have crossed their post-market thresholds and require CAPA reviews now. Occlusion-alarm reached 3.17 per 100 devices against a threshold of 3.0, and connectivity reached 2.26 per 100 devices against a threshold of 2.0, both in the trailing 90-day window ending 2026-07-17 [derived: v-main] [src: commercial/internal-complaints@2026-07-27.2] [config: commercial.yml]. Total complaint volume also rose from 74 in the prior window to 101 in the current one, a broad signal that warrants monthly category-level tracking [derived: window-trend]. The data directly informs whether to open formal CAPA reviews for both categories. The key caveat: the thresholds are demo stand-ins, not the risk file's documented acceptability criteria, so breach verdicts are directionally useful but not yet regulatory-grade [config: commercial.yml].

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

_Pins: `commercial/internal-complaints@2026-07-27.2` (66d, stale); `commercial/internal-fleet@2026-07-27` (66d, stale)_

### BQ-19 — How does our adverse-event profile compare to competitors — and what denominator did you use, because MAUDE doesn't have one?

_Category: Field: Complaints & Safety · edition `2026-07-27.2` (approved) · report: `docs/project/commercial/reports/BQ-19/2026-07-27.2/report.md`_

**Verdict:** MAUDE event COUNTS are comparable with caveats; RATE comparison is BLOCKED — the installed-base denominator (A-001) is not yet quantified

**Summary:** BD (CareFusion) dominates MAUDE adverse-event reports for infusion pumps with 61,417 events [src: commercial/openfda-maude-infusion-mfr@2026-07-22], while the next four competitors cluster between 5,474 and 9,548 events [src: commercial/openfda-maude-infusion-mfr@2026-07-22] — a count-level gap that looks meaningful but cannot yet be interpreted as a safety-rate advantage. The key decision this analysis informs is competitive safety positioning: whether PP3500 can claim a favorable adverse-event profile versus field peers. That claim is currently blocked because no manufacturer-level event rate can be computed without an installed-base denominator, and that denominator remains unquantified [derived: v-main] [assume: A-001]. Counts alone are insufficient for a rate claim; the single biggest caveat is that [assume: A-001] must be resolved before any rate-based safety comparison is defensible.

_Pins: `commercial/openfda-maude-infusion-mfr@2026-07-22` (71d, stale); `commercial/openfda-maude-infusion-monthly@2026-07-22` (71d, stale)_

### BQ-20 — Any field signal — complaints, near-misses, alarm data — around opioid over-delivery or PCA-by-proxy?

_Category: Field: Complaints & Safety · edition `2026-07-27.3` (approved) · report: `docs/project/commercial/reports/BQ-20/2026-07-27.3/report.md`_

**Verdict:** WATCH TRIGGERED on our internal log (demo-fabricated): 3 over-delivery and 2 PCA-by-proxy-suspected complaint records (2 MDR-filed, 1 under investigation) — E-20.1 zero-tolerance NOT met; the signal→upgrade loop closed for 2 watch-category signals; real class-wide MAUDE context is counts-only (no denominator)

**Summary:** The franchise-killer watch for PP3500 is triggered: 3 over-delivery complaint records and 2 PCA-by-proxy-suspected records are on the internal log, and the zero-tolerance expectation E-20.1 is not met [derived: v-main] [src: commercial/internal-complaints@2026-07-27.2] [config: commercial.yml]. Over-delivery on a PCA pump is a patient-safety event; per the watch definition, any confirmed occurrence escalates to the CMO regardless of count [config: commercial.yml]. The immediate decision is CMO review of all 3 over-delivery records this cycle, deadline tracking for the open MDR item, and a re-evaluation of whether the risk file's over-delivery controls remain adequate [derived: docket-watch] [src: commercial/internal-regulatory-docket@2026-07-27]. A partial counter-signal exists: both watch-category signals that entered the signal register resolved into corrective upgrade items, showing the feedback loop is functioning [derived: watch-signals] [src: commercial/internal-signal-register@2026-07-27.2]. The single biggest caveat is that E-20.1's zero-tolerance threshold has not been ratified in the risk file, so the "not met" verdict reflects the plan's working definition, not a formally locked control limit [VERIFY].

| Expectation | Expected | Actual | Verdict |
|---|---|---|---|
| E-20.1 Zero confirmed over-delivery events in the field | 0 confirmed over-delivery complaints | 3 over-delivery complaint records on the log (2 MDR-filed, 1 under investigation) — zero-tolerance breached per the plan's 'confirmed' definition | not-met (unvalidated) |

**Issues:**
- I1 (high) — 3 over-delivery complaint records on the internal log — the franchise-killer category; newest is C-2026-0433 (2026-06-27, under-investigation, MDR filed: yes); the docket carries open over-delivery MDR item(s) MDR-2026-0005 — a category-level join, no shared key (see BQ-21)
- I2 (high) — 2 PCA-by-proxy-suspected records (unauthorized bolus by family/visitor suspected); 1 still open — a use-environment hazard the pump's lockout design must answer

**Risks:**
- R1 (medium) — The question asks for alarm data, but raw alarm telemetry is not a corpus dataset — only signals sourced from alarm analytics are visible, so an alarm-signature precursor of over-delivery could be missed

_Pins: `commercial/internal-complaints@2026-07-27.2` (66d, stale); `commercial/internal-signal-register@2026-07-27.2` (66d, fresh); `commercial/openfda-maude-pca-monthly@2026-07-27` (66d, stale); `commercial/internal-regulatory-docket@2026-07-27` (66d, stale)_

### BQ-21 — What's open on the field-action docket, how timely are our MDRs, and what's the exposure if FDA walks in tomorrow?

_Category: Field: Complaints & Safety · edition `2026-07-27.3` (approved) · report: `docs/project/commercial/reports/BQ-21/2026-07-27.3/report.md`_

**Verdict:** If FDA walks in tomorrow: 2 open docket item(s) (MDR-2026-0005 due in 2 days at the pin date; FSCA-2026-001 rollout incomplete) and 1 late MDR filing(s) in the trailing 12 months — on-time rate 94.7% (18 of 19); E-21.1 NOT met

**Summary:** The docket shows 2 open items and an MDR on-time rate of 94.7% (18 of 19 filings) in the trailing 12 months, and expectation E-21.1 is not met under any defensible measurement basis. [derived: v-main] [src: commercial/internal-regulatory-docket@2026-07-27] [config: commercial.yml] The immediate decision is straightforward: MDR-2026-0005 was unfiled with 2 days to its regulatory deadline at the pin date, and that clock does not pause. [derived: exposure-list] [src: commercial/internal-regulatory-docket@2026-07-27] The second open item, FSCA-2026-001, had its report filed on time, but the field action itself remains incomplete — NA done, EMEA at roughly 60% of sites, APAC not yet started — and an FDA investigator will ask why. [src: commercial/internal-regulatory-docket@2026-07-27] The biggest caveat is structural: this analysis audits filing timeliness of what was docketed; complaints that never advanced to a reportability decision are invisible here, so the 94.7% rate cannot be read as a ceiling on actual exposure. [derived: docket-rollup]

| Expectation | Expected | Actual | Verdict |
|---|---|---|---|
| E-21.1 Every MDR is filed within its regulatory deadline | 0 late filings, trailing 12 months | 1 late filing(s) in the trailing 12 months (MDR-2025-0018 +9d); lifetime record holds 2 late filing(s) | not-met (unvalidated) |

**Issues:**
- I1 (high) — MDR-2026-0005 (over-delivery) is open and unfiled with 2 days to its regulatory deadline (2026-07-29) at the pin date — the over-delivery event under investigation (see BQ-20)
- I2 (medium) — FSCA-2026-001 (drug-library-correction) remains open: rollout as recorded — "NA complete 2026-06, EMEA in progress (~60% sites), APAC pending" — an FDA investigator will ask why APAC has not started

**Risks:**
- R1 (medium) — 1 MDR(s) filed late inside the trailing window (MDR-2025-0018 +9d) — a repeat-observation pattern an investigator can cite even at a 94.7% on-time rate
- R2 (medium) — This docket audits filing timeliness of what was docketed — the complaint-to-MDR reportability decision trail is not a corpus dataset, so under-docketing would be invisible here

_Pins: `commercial/internal-regulatory-docket@2026-07-27` (66d, stale)_

### BQ-22 — Of last year's field signals, how many landed as design inputs or upgrade-pipeline items — and how many died in a spreadsheet?

_Category: Field: Complaints & Safety · edition `2026-07-27.3` (approved) · report: `docs/project/commercial/reports/BQ-22/2026-07-27.3/report.md`_

**Verdict:** 16 of 40 lifetime signals (40.0%) died in a spreadsheet (no-action or open past the 90-day SLA); trailing 12 months: 6 of 21 (28.6%) died vs 9 landed in design/upgrade — and only 36.8% of adjudicated cohort signals met the SLA, so E-22.1 is NOT met

**Summary:** The post-market feedback loop is failing: 16 of 40 lifetime signals (40.0%) never reached the design or upgrade pipeline — dispositioned with no action or left open past the 90-day review deadline — and only 36.8% of the adjudicated cohort met that SLA, so expectation E-22.1 is not met. [derived: v-main] [src: commercial/internal-signal-register@2026-07-27.2] [config: commercial.yml] The trailing 12 months show a better landing ratio — 9 of 21 signals reached design or upgrade versus 6 that died — but pace has not improved: the loop closes too slowly to be called reliable. [derived: funnel] [src: commercial/internal-signal-register@2026-07-27.2] This analysis informs two immediate decisions: whether to declare a corrective action on stale-open and no-action signals, and whether the signal-review board needs a structured aging dashboard to prevent future breach. [derived: funnel] [src: commercial/internal-signal-register@2026-07-27.2] [config: commercial.yml] The single biggest caveat is that the 90-day SLA has not been verified against the QMS post-market surveillance SOP — the not-met verdict is only as strong as that unvalidated threshold. [config: commercial.yml]

| Expectation | Expected | Actual | Verdict |
|---|---|---|---|
| E-22.1 Every field signal reaches a disposition within the review SLA | 100% dispositioned within 90 days of opening | 36.8% of adjudicated cohort signals dispositioned within 90 days (7 within, 12 breached incl. 2 stale-open; 2 recent-open pending, excluded) | not-met (unvalidated) |

**Issues:**
- I1 (high) — 40.0% of lifetime signals (10 no-action + 6 open past 90 days) never reached the design or upgrade pipeline — the post-market → design-input loop is leaking
- I2 (medium) — Even signals that DO get dispositioned run slow: only 36.8% of the adjudicated cohort met the 90-day SLA (median lifetime time-to-disposition 103.5 days)

**Risks:**
- R1 (medium) — The 90-day SLA is a stand-in, not yet traced to the post-market SOP — the verdict is only as good as its threshold
- R2 (medium) — Landed dispositions are trusted from the register's DI-/REQ-/UPG- refs — no cross-system trace yet verifies those refs exist in the requirements or upgrade systems

_Pins: `commercial/internal-signal-register@2026-07-27.2` (66d, fresh)_

### BQ-23 — Where do we stand on the current field-update campaign — planned vs actual coverage by region and site, and will we hit the close date?

_Category: Field: Upgrades & Service Ops · edition `2026-07-27.3` (approved) · report: `docs/project/commercial/reports/BQ-23/2026-07-27.3/report.md`_

**Verdict:** Campaign C-2026-02 is 62.7% complete; at current run-rate EMEA, NA will miss the 2026-09-30 close

**Summary:** Campaign C-2026-02 is 62.7% complete against a 95% close target, and two of three regions cannot finish by 2026-09-30 at current run-rates [derived: v-main] [src: commercial/internal-upgrade-campaign@2026-07-27] [config: commercial.yml]. NA is stalled: zero completions in the trailing four-week window with 44 devices remaining [derived: projected-finish] [src: commercial/internal-upgrade-campaign@2026-07-27]. EMEA projects to finish 2031-01-25 at its current rate of 0.2/wk, nearly five years past the close date [derived: projected-finish] [config: commercial.yml]. The decision this report forces is whether to escalate NA and EMEA immediately — surge capacity, remote conversion, or formal close-date re-baseline — or accept a miss. The single biggest caveat: both plan expectations are unvalidated stand-ins, not grounded in a capacity-planned schedule, so the 95% target itself has not been formally confirmed as achievable [derived: coverage-by-region] [config: commercial.yml].

| Expectation | Expected | Actual | Verdict |
|---|---|---|---|
| E-23.1 Campaign C-2026-02 reaches 95% coverage by the close date | 95% by 2026-09-30 | 62.7% coverage as of the pin; projected finishes: APAC 2026-09-21, EMEA 2031-01-25, NA no-recent-completions | not-met (unvalidated) |
| E-23.2 Every region sustains a completion run-rate sufficient to finish its wave | run-rate >= required rate in each region | APAC: 4.5/wk, EMEA: 0.2/wk, NA: 0.0/wk | not-met (unvalidated) |

**Issues:**
- I1 (high) — NA has zero completions in the trailing four-week window with 44 devices remaining — the wave is stalled, not slow

**Risks:**
- R1 (medium) — EMEA projects to finish 2031-01-25, past the 2026-09-30 close (59 remaining at 0.2/wk)

_Pins: `commercial/internal-upgrade-campaign@2026-07-27` (66d, stale)_

### BQ-24 — What are our update failure and retry rates — is any hardware rev, firmware baseline, or site profile failing at a rate that says pause and escalate?

_Category: Field: Upgrades & Service Ops · edition `2026-07-27.3` (approved) · report: `docs/project/commercial/reports/BQ-24/2026-07-27.3/report.md`_

**Verdict:** PAUSE TRIGGER: cohort hw B upgrading from 3.1.2 fails on 31.4% of attempted devices (threshold 15.0%) — pause the wave for this cohort and escalate

**Summary:** The upgrade wave must pause for hardware revision B devices running firmware 3.1.2: 31.4% of the 35 attempted devices in that cohort failed — more than double the 15.0% trigger threshold [derived: v-main] [src: commercial/internal-upgrade-campaign@2026-07-27] [config: commercial.yml]. The failure pattern is cohort-specific: every other qualifying cohort sits well below the threshold, pointing to a hardware-revision × firmware interaction rather than a general campaign problem [derived: failure-by-cohort] [src: commercial/internal-upgrade-campaign@2026-07-27]. The decision this data requires is immediate: halt new attempts on the affected cohort, open an engineering investigation, and hold resumption until a corrected package or cohort-specific procedure is in place. The main caveat is that the 15.0% pause threshold is a demo stand-in, not yet derived from the risk file's acceptability criteria, so the trigger level itself remains unvalidated [config: commercial.yml].

| Expectation | Expected | Actual | Verdict |
|---|---|---|---|
| E-24.1 No cohort's per-attempt failure rate exceeds the pause threshold | <= 15% per attempted device (cohort n >= 20) | worst cohort 31.4% (hw B / from 3.1.2) | not-met (unvalidated) |

**Issues:**
- I1 (high) — Cohort hw B / from 3.1.2 fails on 31.4% of attempted devices (11 of 35) — above the pause threshold

**Risks:**
- R1 (medium) — The pause threshold itself is a demo stand-in — not derived from the risk file, so the trigger level is unvalidated

_Pins: `commercial/internal-upgrade-campaign@2026-07-27` (66d, stale)_

### BQ-25 — Are customers struggling with this upgrade — tickets per 100 upgraded pumps, rollbacks — and what does an upgrade cost the customer?

_Category: Field: Upgrades & Service Ops · edition `2026-07-27.3` (approved) · report: `docs/project/commercial/reports/BQ-25/2026-07-27.3/report.md`_

**Verdict:** Tickets per 100 attempted upgrades are highest in NA at 21.7; 4 site(s) rolled back; estimated customer-side cost of the on-site portion so far $7,272–$16,412

**Summary:** The upgrade campaign is generating friction at a rate that warrants action before the remaining scheduled sites attempt the update. NA leads all regions with 21.7 tickets per 100 attempted upgrades [src: commercial/internal-upgrade-campaign@2026-07-27], and 4 sites have already rolled back entirely [derived: rollback-sites] [src: commercial/internal-upgrade-campaign@2026-07-27]. Remote updates produce more tickets per 100 attempts than on-site visits — 22.3 versus 19.4 — which challenges any assumption that remote is the lower-friction path [derived: tickets-by-method] [src: commercial/internal-upgrade-campaign@2026-07-27]. The customer-side cost of the on-site portion alone is $7,272–$16,412 for completed updates [derived: v-main], but that range rests entirely on modeled hours and benchmark labor rates [assume: A-002], so the true customer burden could be materially higher or lower. The key decision this data informs is whether to pause or modify the campaign — particularly for remote-method NA sites — before the pattern compounds across the still-scheduled population.

_Pins: `commercial/internal-upgrade-campaign@2026-07-27` (66d, stale)_

### BQ-26 — Do we have the capacity to execute the remaining waves on schedule — or do we add headcount, contract labor, or slip?

_Category: Field: Upgrades & Service Ops · edition `2026-07-27.3` (approved) · report: `docs/project/commercial/reports/BQ-26/2026-07-27.3/report.md`_

**Verdict:** Capacity gap to hit the 2026-09-30 close — EMEA, NA STALLED (zero completions in the four weeks to 2026-07-27; EMEA needs 6.4/wk; NA needs 4.7/wk); APAC behind (3.5/wk vs 4.5/wk required); remote conversion covers 0 of 97 on-site-remaining devices today

**Summary:** The upgrade campaign faces a material capacity gap across all three regions and cannot meet the 2026-09-30 close at current run rates: EMEA and NA are fully stalled — zero completions in the four weeks to 2026-07-27 — and APAC is running at 3.5/wk against a 4.5/wk requirement [derived: required-rate] [src: commercial/internal-upgrade-campaign@2026-07-27] [config: commercial.yml]. The decision before leadership is whether to surge field-service capacity, slip the close date, or both, and that choice carries customer-commitment consequences in all three regions. Remote conversion does not relieve the backlog today: 0 of 97 on-site-remaining devices are connected [derived: remote-convertible] [src: commercial/internal-fleet@2026-07-27], and enabling it requires adapter retrofits, not scheduling changes. The single biggest caveat is that no FSE roster or utilization dataset exists in the corpus, so the workload floor of 19.7 FSE-days [derived: fse-days-remaining] is a labor-time lower bound and any surge or slip decision is directional until that data is acquired.

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

_Pins: `commercial/internal-upgrade-campaign@2026-07-27` (66d, stale); `commercial/internal-fleet@2026-07-27` (66d, stale)_

### BQ-27 — How far behind current is the fleet — % of pumps more than one firmware version behind, at which accounts, and connected vs not?

_Category: Field: Upgrades & Service Ops · edition `2026-07-27.3` (approved) · report: `docs/project/commercial/reports/BQ-27/2026-07-27.3/report.md`_

**Verdict:** 56.7% of the PP3500 fleet is ≥1 firmware version behind (21.9% two behind); connected devices are current at 42.3% vs 44.2% for unconnected

**Summary:** More than half the PP3500 fleet — 56.7% — is running firmware at least one version behind, and 21.9% are two full versions behind [derived: v-main] [src: commercial/internal-fleet@2026-07-27]. This is a patient-safety exposure: an outdated drug-error-reduction library is not an operations metric to manage in the next planning cycle; it belongs in the risk conversation now [src: commercial/internal-fleet@2026-07-27]. The decision this data informs is whether a proactive update campaign is required and which regions to lead with. The single biggest caveat is that only one fleet snapshot exists, so currency trends over time cannot yet be assessed — that picture builds as the 7-day refresh cadence accumulates more data [derived: currency-history].

_Pins: `commercial/internal-fleet@2026-07-27` (66d, stale)_

### BQ-28 — Where are we against plan on revenue — by line and region, volume vs price vs timing?

_Category: Economics & Plan-vs-Actual · edition `2026-07-27.3` (approved) · report: `docs/project/commercial/reports/BQ-28/2026-07-27.3/report.md`_

**Verdict:** H1 2026 revenue $46.3M vs plan $48.3M (-4.1%, within the ±5% tolerance overall; 4 of 6 lines breach the band individually on the downside); under plan: cloud-suite -16.4%, SP6500 -15.7%, SP6000 -9.1%, PP3500 -6.3%; masked by IP5000 +24.3%, PP3000 +16.1%; 2026-Q2 alone breached at -5.5%

**Summary:** H1 2026 revenue was $46.3M against a plan of $48.3M, a -4.1% miss that sits inside the ±5% composite tolerance — but the composite flatters the picture [derived: v-main] [src: commercial/internal-financials@2026-07-27] [src: commercial/internal-revenue-plan@2026-07-27] [config: commercial.yml]. Four of the six product lines individually breached the tolerance band on the downside, while two outperforming lines offset those shortfalls inside the total [derived: variance-by-line] [src: commercial/internal-financials@2026-07-27] [src: commercial/internal-revenue-plan@2026-07-27]. The deteriorating quarterly trend matters: 2026-Q2 alone breached at -5.5% versus -2.6% in 2026-Q1, meaning the trajectory is wrong even while the H1 composite still passes [derived: variance-by-quarter] [src: commercial/internal-financials@2026-07-27] [src: commercial/internal-revenue-plan@2026-07-27] [config: commercial.yml]. The decision this informs is whether to reforecast or commit to a recovery plan for the four under-plan lines — starting at the next monthly close. The single biggest caveat: the ±5% flagging tolerance is unratified; the plan of record names no reforecast trigger, so every within-tolerance verdict rests on a stand-in threshold [config: commercial.yml].

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

_Pins: `commercial/internal-financials@2026-07-27` (66d, fresh); `commercial/internal-revenue-plan@2026-07-27` (66d, fresh)_

### BQ-29 — Is the Cloud Suite attach-rate stage-gate holding — the gate that releases the $24M predictive-monitoring spend?

_Category: Economics & Plan-vs-Actual · edition `2026-07-27.3` (approved) · report: `docs/project/commercial/reports/BQ-29/2026-07-27.3/report.md`_

**Verdict:** The attach stage-gate HOLDS at the stand-in level: 43.0% of the PP3500 installed base (295 of 686 pumps) vs the 40% gate — but the $24M releases on a gate NUMBER nobody has ratified; the strategy of record says 'traction' and sets no threshold — and the verdict is denominator-definition-sensitive: under a whole-PCA denominator (884 pumps incl. 198 unconnectable PP3000) attach reads 33.4%, BELOW the stand-in gate; the metric definition is as unratified as the gate number

**Summary:** The Cloud Suite attach gate holds on the primary metric: 295 of 686 PP3500 pumps carry an active subscription, a 43.0% rate against the 40% stand-in threshold [derived: attach-stat] [src: commercial/internal-subscriptions@2026-07-27.2] [src: commercial/internal-fleet@2026-07-27]. But the $24M predictive-monitoring spend should not release on this reading: neither the gate number nor the denominator that produces the attach rate is ratified in the commercial strategy of record, which conditions the spend only on "traction" [config: commercial.yml] [derived: v-main]. Under a whole-PCA denominator, attach reads 33.4% against the same 40% gate — below it — so the denominator choice alone determines whether the gate holds or fails [derived: denominator-sensitivity]. The decision this report informs is the $24M release; the action it requires is a board or CFO ratification of both a numeric gate and a metric definition before the spend is triggered [derived: attach-stat] [derived: denominator-sensitivity] [config: commercial.yml].

| Expectation | Expected | Actual | Verdict |
|---|---|---|---|
| E-29.1 Installed-base Cloud Suite attach reaches the stage-gate level before the predictive-monitoring spend releases | >= 40% of PP3500 installed base attached | 43.0% attach vs the 40% stand-in (+3.0 points); no gate number is ratified in the strategy of record; denominator-sensitive — the whole-PCA basis reads 33.4%, below the gate | met (unvalidated) |

**Risks:**
- R1 (high) — The $24M release decision references a gate with no number of record — the 40% is a stand-in, and at 43.0% attach the reading sits 3.0 points from it; any ratified threshold in that neighborhood flips the verdict — and the metric DEFINITION is equally unratified: the whole-PCA denominator reads 33.4%, below the gate, so the denominator choice alone spans the gate

_Pins: `commercial/internal-subscriptions@2026-07-27.2` (66d, fresh); `commercial/internal-fleet@2026-07-27` (66d, stale)_

### BQ-30 — What's our fully-loaded cost per update, remote vs on-site — and the business case for a remote-first campaign at the top non-connected accounts?

_Category: Economics & Plan-vs-Actual · edition `2026-07-27.3` (approved) · report: `docs/project/commercial/reports/BQ-30/2026-07-27.3/report.md`_

**Verdict:** A remote update costs $120 vs an on-site update between $193 (labor-time floor) and $950 (full-day ceiling) — remote is 12.6–62.1% of on-site depending on unmeasured travel; a $380 adapter pays back in 0.5–5.2 update campaigns at the top non-connected accounts

**Summary:** Remote updates cost $120 each against an on-site range of $193–$950 per completion, making remote 12.6–62.1% of on-site cost depending on unmeasured travel — the economics favor remote across nearly every scenario [derived: v-main] [src: commercial/internal-upgrade-campaign@2026-07-27] [config: commercial.yml]. A $380 per-device connectivity adapter pays back in 0.5–5.2 update campaigns, and the top 47 non-connected accounts hold 355 devices with a total adapter outlay of $134,900 against a per-campaign on-site spend of $68,575–$337,250 [derived: adapter-case] [derived: adapter-payback] [src: commercial/internal-fleet@2026-07-27] [config: commercial.yml]. This informs the decision whether to fund adapter deployment at those accounts before the next update campaign. The single biggest caveat is that the on-site cost range spans from $193 to $950 because FSE travel and overhead are not in any dataset [derived: fully-loaded-onsite] [derived: onsite-cost-bounds] — the remote-first decision flips inside that band, and no capex commitment should be made until the bound is collapsed [derived: adapter-payback].

| Expectation | Expected | Actual | Verdict |
|---|---|---|---|
| E-30.1 A remote update costs a fraction of an on-site visit | remote cost per completed update <= 25% of on-site | remote $120 = 62.1% of the on-site labor floor ($193) but 12.6% of the full-day ceiling ($950) — the ≤25% test depends on the unmeasured travel component | at-risk (unvalidated) |

**Risks:**
- R1 (high) — The fully-loaded on-site cost is unresolvable from campaign data — the $193–$950 bound spans 12.6% to 62.1% on the remote-vs-onsite ratio, and the adapter payback spans 0.5 to 5.2 campaigns — the remote-first decision flips inside that band
- R2 (medium) — All three cost rates are demo stand-ins, not finance-validated (FSE day $950, remote session $120, adapter $380) — and the remote figure is a floor: 10 remote and 7 on-site completions needed a retry whose extra sessions the data does not count

_Pins: `commercial/internal-upgrade-campaign@2026-07-27` (66d, stale); `commercial/internal-fleet@2026-07-27` (66d, stale)_

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

