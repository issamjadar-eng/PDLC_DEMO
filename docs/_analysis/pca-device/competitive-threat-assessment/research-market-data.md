---
id: research-market-data
parent_analysis: competitive-threat-assessment
type: research
authored_by: agent:general-purpose
created: 2026-08-05
---

# Public-Source Market Research — Competitive Threat Assessment (PP3500 / PCA Device)

> _The project documents under test are **demo sample data — not for clinical use**. The public sources cited in this file are **real** and were retrieved on 2026-08-05. Where a project claim is graded CONFIRMED, that means the project's number matches a real published vendor estimate — it does **not** mean the project's underlying narrative is sound._

## Method + limits

**What was done.** Read the three project documents under test, computed every stated CAGR independently, then searched public sources for each figure. Sources preferred in this order: company SEC filings / earnings releases (audited or management-reported), award-body press releases (KLAS, ICU Medical), peer-reviewed literature and society guidelines (ERAS Society, PubMed/PMC), then market-research-firm summaries.

**CAGR formula used throughout:** `CAGR = (end / start)^(1 / years) − 1`. Every arithmetic result below is shown with its inputs so it can be re-derived.

**Limits that materially constrain the confidence of this file:**

1. **Market-research-firm figures are vendor estimates, not audited data.** They are marketing artifacts for a paid report. Different firms disagree by multiples, not percentages — the ambulatory infusion pump market was found at **$885.3M (2023)** from one firm and **$14.8B (2023)** from another, a **16.7×** spread for a market with the same name. No single vendor number in this file should be treated as fact. Where firms disagree, the range is given.
2. **Segment definitions are unstated and non-comparable.** "Infusion pump market" sometimes means pump hardware only, sometimes hardware + disposable sets + software. This alone explains several-fold differences and is the most likely root cause of the project's errors.
3. **Paywalls.** Grand View Research and MDPI returned HTTP 403 to direct fetch; their figures below come from search-result summaries and press releases, which is a weaker rung of evidence and is flagged per-row.
4. **Signify Research's infusion-pump competitor-share analysis exists but is gated** behind an infographic request form. It is the most likely home of a real share table and could not be read.
5. **No national time-series on IV PCA utilization was located.** This is the single most important gap in this file — see [The PCA utilization question](#the-pca-utilization-question).

**Grading vocabulary:** `SUBSTANTIATED` (public source, URL cited) · `SUBSTANTIATED (vendor estimate)` (published, but a research-firm projection, not audited) · `INFERRED` (derived by reasoning, reasoning shown) · `OPINION` (labelled, no source available) · `UNVERIFIED` (searched, did not confirm — what was seen is stated).

---

## Claims under test

| # | Project claim | Project source file | What public sources say | Verdict | Grade |
|---|---|---|---|---|---|
| 1 | Global infusion pump market **$3.5B (2023) → $19.5B (2031) at 8.2% CAGR** | `state-of-the-art-analysis.md` L29 | $3.5B→$19.5B over 8 yr implies **23.95%** CAGR, not 8.2%. At 8.2% for 8 yr, $3.5B reaches only **$6.57B**. To reach $19.5B in 2031 at 8.2%, the 2023 base must be **$10.38B**. Real published 2024/2025 global figures cluster at **$15.35–19.9B** ([SkyQuest](https://www.skyquestt.com/report/infusion-pump-market): $18.01B 2024, $19.49B 2025, $36.61B 2033 @ 8.2%; [MarketsandMarkets](https://www.marketsandmarkets.com/Market-Reports/infusion-pumps-accessories-market-90374506.html): $19.86B 2025 → $28.35B 2030 @ 7.4%; [Precedence](https://www.precedenceresearch.com/infusion-pump-market): $17.49B 2025). The $3.5B base is **~5× too low** and matches no published estimate found. | **ARITHMETICALLY WRONG** (and base contradicted) | SUBSTANTIATED (vendor estimate) |
| 2a | **US market $19.5B (2025), 8.2% CAGR** | `state-of-the-art-analysis.md` L31 | [MarketsandMarkets US](https://www.marketsandmarkets.com/Market-Reports/geography/infusion-pumps-accessories-market/us): US infusion pump market **$8,257.4M (2025) → $11,771.2M (2030) at 7.3%**. North America is ~38% of the global market, so a US figure equal to the *global* figure is impossible. The claim overstates the US market by **~2.4×**. | **CONTRADICTED** | SUBSTANTIATED (vendor estimate) |
| 2b | **China market $19.5B at 8.4% CAGR** | `state-of-the-art-analysis.md` L34 | [Databridge APAC](https://www.databridgemarketresearch.com/reports/asia-pacific-infusion-pumps-market): China held **38.5% of the APAC** infusion pump market (2024); China infusion pump market cited at **~$0.92B by 2026**. Firms disagree on scope, but no source places China anywhere near $19.5B. Overstated by roughly an **order of magnitude**. | **CONTRADICTED** | SUBSTANTIATED (vendor estimate) |
| 2c | *Is the repeated $19.5B a copy-paste artifact?* | all three slots | **Yes — almost certainly.** [SkyQuest](https://www.skyquestt.com/report/infusion-pump-market) states verbatim: *"Global Infusion Pump Market size was valued at USD 18.01 Billion in 2024 and is poised to grow from USD **19.49 Billion in 2025** … growing at a **CAGR of 8.2%**."* That single sentence supplies **both** the $19.5B and the 8.2% figures. It is a **global 2025** figure that has been pasted into three different slots — global-2031, US-2025, and (with the CAGR nudged to 8.4%) China. The China row also inherits the number without inheriting the CAGR, which is the signature of manual duplication rather than independent sourcing. | **CONTRADICTED (provenance identified)** | INFERRED — reasoning: exact match on both the value and the CAGR from a single source sentence, replicated across three mutually exclusive scopes |
| 3 | AI-enabled medical device market **$15.1B (2023) → $98.3B (2028)** at **35% CAGR** | `competitive-product-assessment.md` L16, L71 | True implied CAGR = **45.45%**. At 35%, $15.1B reaches **$67.71B** by 2028, not $98.3B. **This document is the wrong one.** | **ARITHMETICALLY WRONG** | INFERRED (arithmetic shown) |
| 3b | Same endpoints at **45% CAGR** | `strategic-market-ai-infusion.md` L24 | At 45%, $15.1B reaches **$96.79B** — within 1.5% of the stated $98.3B. **This document has the internally consistent CAGR.** | **CONFIRMED (internally consistent)** | INFERRED (arithmetic shown) |
| 3c | *Are the underlying AI-market endpoints real?* | both | **No.** Published estimates are far lower: **$10.2B (2023) → $29.8B (2028) at 24.7%**; [Grand View](https://www.grandviewresearch.com/industry-analysis/ai-enabled-medical-devices-market-report) $13.67B (2024); another firm $12.38B (2025) → **$42.43B (2030) at 27.3%** ([GlobeNewswire](https://www.globenewswire.com/news-release/2026/06/30/3319462/28124/en/AI-in-Medical-Devices-Market-Expected-to-Reach-42-43-Billion-by-2030-Driven-by-Increased-AI-Integration)); [BIS Research](https://bisresearch.com/industry-report/artificial-intelligence-machine-learning-medical-device-market.html) $4.01B (2022) → $35.46B (2032) at 24.35%. Published CAGRs cluster at **24–38%**, not 45%. **$98.3B by 2028 exceeds every published 2028 estimate found by roughly 3×.** So the doc that is arithmetically *right* (45%) is sourced from figures that are directionally wrong. | **CONTRADICTED** | SUBSTANTIATED (vendor estimate) |
| 4 | Smart pump market **$1.21B (2025) → $1.82B (2031) at 7.04% CAGR** | `competitive-product-assessment.md` L72; `state-of-the-art-analysis.md` L30 | **Arithmetic is exact**: (1.82/1.21)^(1/6) − 1 = **7.040%**. And the figures match a real report precisely — [Mordor Intelligence, Infusion Pump *Software* Market](https://www.mordorintelligence.com/industry-reports/infusion-pump-software): **$1.21B (2025) → $1.82B (2031), 7.04% CAGR (2026–2031)**. **Caveat:** this is the infusion pump **software** market, not the smart pump market. `state-of-the-art-analysis.md` labels it correctly ("Smart pump software market"); `competitive-product-assessment.md` L72 drops the word "software" and calls it the "Smart pump market" — a ~16× scope error against the ~$19B device market. Corroborating: [SNS Insider](https://www.snsinsider.com/reports/infusion-pump-software-market-2033) puts infusion pump software at $862.12M (2023) → $1,655.17M (2032) at 7.52%. | **CONFIRMED** (figures + arithmetic); **mislabelled** in one doc | SUBSTANTIATED (vendor estimate) |
| 5a | Neonatal infusion pump **$3.2B (2025) → $4.5B (2030) at 5.6% CAGR** | `competitive-product-assessment.md` L74 | Implied CAGR = **7.06%**, not 5.6%. At 5.6%, $3.2B reaches **$4.20B**, not $4.5B. No standalone neonatal-infusion-pump market report at this size was located. | **ARITHMETICALLY WRONG** | INFERRED (arithmetic shown) |
| 5b | Neonatal infusion pump **$2.06B (2025) → $3.2B (2030) at 5.6% CAGR** | `strategic-market-ai-infusion.md` L27 | Implied CAGR = **9.21%**, not 5.6%. At 5.6%, $2.06B reaches **$2.71B**. Also arithmetically wrong — but the **$2.06B base is the more defensible of the two**: [Grand View IV infusion pumps](https://www.grandviewresearch.com/industry-analysis/intravenous-infusion-pump-market) puts the global IV infusion pump market at **$6.72B (2025)** with the **pediatrics/neonatology segment at 27%** → **≈$1.81B**. $2.06B is ~14% above that derivation; $3.2B is ~77% above it. | **ARITHMETICALLY WRONG** (base closer to defensible) | INFERRED — derivation: $6.72B × 27% ≈ $1.81B |
| 5c | The two docs disagree with each other on the same market | both | The same portfolio's own documents state the 2025 neonatal market as both **$3.2B** and **$2.06B** — a 55% disagreement — and the 2030 value as both **$4.5B** and **$3.2B**, where one doc's 2030 figure equals the other doc's 2025 figure. Both then quote the identical 5.6% CAGR, which fits neither pair. | **CONTRADICTED (internally)** | INFERRED (direct comparison of the two files) |
| 6 | Market shares **BD 35%, Baxter 25%, B. Braun 15%** | `competitive-product-assessment.md` L59–L62, L76 | **No published source giving this triple was found.** What was found: [iData Research](https://idataresearch.com/best-selling-large-volume-infusion-pumps-in-the-united-states/) — *"BD holding over **50%** of the large volume pump market in **2019**"*, which contradicts the 35% figure for the segment where BD is strongest. [Signify Research](https://www.signifyresearch.net/insights/infusion-pumps-the-evolution-in-competitor-share/) has a competitor-share analysis but it is **gated**. Company-reported revenue offers a partial sanity check: [BD MMS](https://investors.bd.com/news-events/press-releases/detail/915/bd-reports-fourth-quarter-and-full-year-fiscal-2025-financial-results) **$3.47B (FY2025)** (includes Pyxis dispensing, not pumps alone); [ICU Medical FY2024](https://ir.icumed.com/news-releases/news-release-details/icu-medical-announces-fourth-quarter-2024-results-and-provides) Infusion Consumables **$1.11B**, Infusion Systems **$684.2M**, Vital Care **$437.9M**. The claim carries **no year, no geography, and no segment definition**, so it cannot be tested as written. | **UNVERIFIABLE** | UNVERIFIED — searched iData, Signify, MarketsandMarkets, Coherent, BCC; no source produced the 35/25/15 triple |
| 6b | *Alaris recall disruption* | (context for #6) | **Substantiated and material.** FDA issued a **Class I recall on all US Alaris pumps in Feb 2020**; BD sold under a **consent decree until 2023**; BD [regained 510(k) clearance and relaunched in 2023](https://www.medtechdive.com/news/BDX-BD-Alaris-infusion-pump-FDA/688720/), which added ~50 bps to 2024 top line. **Alaris infusion-set recalls continued into 2025** ([ONS, Sept 2025](https://www.ons.org/publications-research/voice/news-views/09-2025/bd-continues-expand-its-recall-certain-alaris-pump); [FDA](https://www.fda.gov/safety/recalls-market-withdrawals-safety-alerts/bd-provides-update-voluntary-recalls-alaristm-pump-module-model-8100-and-certain-alaristm-pump)). A single static "BD 35%" with no vintage is therefore not just unverifiable but **actively misleading** — BD's share moved materially across 2020–2025. | **CONFIRMED (the disruption)** | SUBSTANTIATED |
| 7 | Home infusion **$28.4B (2023) → $54.84B (2030) at 12.8% CAGR** | `competitive-product-assessment.md` L73; `strategic-market-ai-infusion.md` L18, L26 | Implied CAGR = **9.86%**, not 12.8%. At 12.8% for 7 yr, $28.4B reaches **$65.99B**, not $54.84B. Published 2023 bases are all **higher** than $28.4B: **$35.98B** (SNS Insider), **$31.9B** (GM Insights), **$38.9B** (Market.us). Published forecasts: [Grand View](https://www.grandviewresearch.com/press-release/global-home-infusion-therapy-market) **$61.72B by 2030 at 8.2%**; [SNS Insider](https://www.globenewswire.com/news-release/2024/09/23/2951513/0/en/Home-Infusion-Therapy-Market-Size-Projected-to-Reach-USD-71-82-Billion-by-2032-with-8-36-CAGR-SNS-Insider) $71.82B by 2032 at 8.36%; [Mordor](https://www.mordorintelligence.com/industry-reports/home-infusion-market) $35.60B by 2030 at 6.5%. **Published CAGRs cluster at 6.5–8.4% — the claimed 12.8% is above every one of them.** Additional defect: `competitive-product-assessment.md` L73 labels these same numbers "**Ambulatory** market" while `strategic-market-ai-infusion.md` labels them "**Home infusion** market" — two different markets, one set of numbers. | **ARITHMETICALLY WRONG** (and CAGR contradicted) | SUBSTANTIATED (vendor estimate) |
| 8a | **$895–$995 refurbished Baxter Sigma Spectrum** | `state-of-the-art-analysis.md` L71 | **Right order of magnitude, real secondary market.** Live listings found at **$997.00** (software 6.02) and **$1,097.00** (software 8.0) at [MDMaxx](https://mdmaxx.com/products/baxter-35700ba-sigma-spectrum-infusion-iv-pump-refurbished); multiple other refurb dealers list the same model ([CIA Medical](https://www.ciamedical.com/baxter-sig-001-sigma-spectrum-pump-infusion-refurbished-single-channel-ea), [Gumbo](https://gumbomedical.com/product/baxter-sigma-spectrum-iv-pump/)). The claimed range sits just below current asks. | **CONFIRMED (as a refurb price)** | SUBSTANTIATED |
| 8b | **$1,295 ICU Medical Plum 360** | `state-of-the-art-analysis.md` L71 | Not confirmed. Refurb-market search surfaced Plum 360 **repair services at $450** but no unit listing at $1,295. A $1,295 price for a Plum 360 would in any case be a **refurbished/secondary** price, not new-unit capital pricing. | **UNVERIFIABLE** | UNVERIFIED — searched refurb dealer listings; no matching unit price found |
| 8c | **$6,185 device family average** | `state-of-the-art-analysis.md` L69, L71 | Plausible **as a new-unit ASP**, and that is exactly the problem — see 8e. Published new-unit bands: large-volume pumps **$2,184–$6,865**; syringe pumps **$2,380–$5,982**; PCA pumps **$1,800–$4,500**; overall average **$1,777** ([AutoInfu](https://autoinfu.com/factors-affecting-infusion-pump-price/)). $6,185 sits at the **top of the LVP band**. | **CONFIRMED (as new-unit ASP band)** | SUBSTANTIATED |
| 8d | **$8,000–12,000 per neonatal pump** | `competitive-product-assessment.md` L79 | **Above every published band found.** Neonatal work is done with syringe pumps, whose published new-unit range tops out at **$5,982**. The claim is 1.3–2× above the top of the relevant band. No source supporting $8–12K per neonatal pump was found. | **CONTRADICTED** | UNVERIFIED — searched pump pricing aggregators and dealer listings; nothing above ~$6.9K for any pump class |
| 8e | *Is the doc comparing refurb prices to new-unit prices?* | `state-of-the-art-analysis.md` L71 | **Yes — the three figures sit in a single line of the same table.** "$895–$995 (Refurbished Baxter Sigma Spectrum); $1,295 (ICU Medical Plum 360); **$6,185 device family average**" places two **secondary-market resale** prices beside one **new-unit ASP** with no scope label, implying GlobalLogic's device commands ~6× the competition. It does not: it commands roughly parity-to-premium against **new** competitor units in the $2,184–$6,865 band. The comparison also omits the recurring economics that dominate the real buying decision — **annual software licences at 10–15% of system replacement value**, **service contracts $150–250/pump**, and **cost more than doubling when pumps are networked to the EMR/pharmacy** ([NCBI/AHRQ *Making Healthcare Safer III*](https://www.ncbi.nlm.nih.gov/books/NBK555506/)). | **CONTRADICTED (invalid comparison)** | INFERRED — reasoning: refurb resale and new-unit ASP are different markets; the table applies no scope label |
| 9 | **ICU Medical Plum 360 — KLAS Honor 2025, 8th consecutive year** | `strategic-market-ai-infusion.md` L45; `competitive-product-assessment.md` L61 | **Correct.** [ICU Medical, 2025](https://www.icumed.com/about-us/news/2025/best-in-klas-2025/): Plum 360 recognized as top-performing **Smart Pump EMR-Integrated** by KLAS, *"Best in KLAS eight years in a row,"* and *"the only smart infusion system to win the Smart Pump EMR-Integrated category."* **Nuance the docs omit:** KLAS runs **two** smart-pump categories — [Smart Pumps EHR-Integrated](https://klasresearch.com/best-in-klas-ranking/smart-pumps-ehr-integrated/2025/124-37) and [Smart Pumps Traditional](https://klasresearch.com/best-in-klas-ranking/smart-pumps-traditional/2025/124-38) — and Plum 360 won the integrated one. In 2023 it was the [first ever to win both](https://www.icumed.com/about-us/news/2023/best-in-klas-2023/). A [2026 Traditional ranking](https://klasresearch.com/best-in-klas-ranking/smart-pumps-traditional/2026/124-38) also exists, so the award is live and current. | **CONFIRMED** | SUBSTANTIATED |
| 10 | *Bonus defect found:* infusion pump market **$37.72B (2023) → $92.23B (2032)** | `strategic-market-ai-infusion.md` L61 | Implied CAGR **10.44%** (none stated). More importantly, this **directly contradicts the same portfolio's other document**, which puts the 2023 global infusion pump market at **$3.5B** (`state-of-the-art-analysis.md` L29). Two project documents state the *same market in the same year* **10.8× apart**, and neither matches the ~$15–18B published consensus. | **CONTRADICTED (internally)** | INFERRED (direct comparison of the two files) |
| 11 | *Bonus defect found:* **Canada market $10.3B, 7.3% CAGR** | `state-of-the-art-analysis.md` L33 | Not directly researched, but flagged as implausible on its face: Canada's figure would be **~125% of the entire US market** ($8.26B, MarketsandMarkets) for a country with roughly one-ninth the population and lower per-capita device spend. Also note the **7.3% CAGR is exactly the published US CAGR** — another likely copy-paste. | **UNVERIFIABLE (implausible)** | UNVERIFIED — not searched directly; flagged on internal-consistency grounds |

### Grade and verdict counts

**By verdict — 19 assessed sub-claims.** Rows 1 and 7 carry a compound verdict (arithmetically wrong *and* the underlying figure contradicted); they are counted once, under ARITHMETICALLY WRONG.

| Verdict | Count | Rows |
|---|---|---|
| **ARITHMETICALLY WRONG** | **5** | 1, 3, 5a, 5b, 7 |
| **CONTRADICTED** | **6** | 2a, 2b, 2c, 3c, 5c, 8d, 8e, 10 → counted as 6 distinct claims (2c and 5c/10 are provenance/internal-consistency findings on claims already listed) |
| **CONFIRMED** | **6** | 3b, 4, 6b, 8a, 8c, 9 |
| **UNVERIFIABLE** | **3** | 6, 8b, 11 |

**Bottom line: 11 of 19 sub-claims (58%) are arithmetically wrong or contradicted by public sources; 3 more cannot be verified at all. Only 6 stand — and of those 6, one (row 4) is correct but mislabelled in one of the two documents that carries it.**

**By grade:**

| Grade | Count |
|---|---|
| SUBSTANTIATED | 4 |
| SUBSTANTIATED (vendor estimate) | 7 |
| INFERRED | 7 |
| UNVERIFIED | 4 |
| OPINION | 0 (all opinion is confined to the Implications section) |

---

## Independent market picture

Setting the project's numbers aside entirely, here is what public sources support.

### Global infusion pump market

There is no single number. Firms disagree by roughly 30% on the current size and by 2–3 points on growth:

| Firm | 2024/2025 size | Forecast | CAGR |
|---|---|---|---|
| [SkyQuest](https://www.skyquestt.com/report/infusion-pump-market) | $18.01B (2024) / $19.49B (2025) | $36.61B (2033) | 8.2% (2026–33) |
| [MarketsandMarkets](https://www.marketsandmarkets.com/Market-Reports/infusion-pumps-accessories-market-90374506.html) | $19.86B (2025) | $28.35B (2030) | 7.4% |
| [Precedence](https://www.precedenceresearch.com/infusion-pump-market) | $17.49B (2025) | $36.42B (2035) | — |
| [Straits](https://www.globenewswire.com/news-release/2024/10/08/2960030/0/en/Global-Infusion-Pumps-Market-Size-to-Reach-USD-31-99-Billion-by-2033-Straits-Research.html) | $15.35B (2024) / $16.66B (2025) | $31.99B (2033) | 8.50% |
| [Market.us](https://media.market.us/infusion-pump-market-news-2025/) | — | — | 6.6% (2025–32) |

**Defensible working range: global infusion pump market ≈ $17–20B (2025), growing 6.5–8.5%.** Grade: SUBSTANTIATED (vendor estimate), multi-source.

### Regional split

- **US: $8.26B (2025) → $11.77B (2030) at 7.3%** ([MarketsandMarkets](https://www.marketsandmarkets.com/Market-Reports/geography/infusion-pumps-accessories-market/us)). North America ≈ **38%+** of the global market.
- **China:** largest APAC market at **38.5% of APAC (2024)** ([Databridge](https://www.databridgemarketresearch.com/reports/asia-pacific-infusion-pumps-market)); one estimate places China at **~$0.92B by 2026**. Firms disagree, but the scale is **sub-$2B**, not $19.5B.

### Sub-segments relevant to this portfolio

| Segment | Published estimate | Source |
|---|---|---|
| **PCA pumps** | **$491.57M (2025) → $678.19M (2031), 5.51% CAGR**; NA = 42.08% share; APAC fastest at 7.29% | [Mordor](https://www.mordorintelligence.com/industry-reports/patient-controlled-analgesia-pumps-market) |
| PCA pumps (competing estimates) | $2.41B (2024) → $4.07B (2033) @ 7.4%; $2.90B (2023) → $4.70B (2030) @ 6.10%; $656M (2024) → $3.83B (2034) @ 19.30% | [MRFR](https://www.marketresearchfuture.com/reports/patient-controlled-analgesic-pump-market-30136), [Allied](https://www.alliedmarketresearch.com/patient-controlled-analgesic-pumps-market-A13386), [ZMR](https://www.globenewswire.com/news-release/2026/07/15/3327744/0/en/latest-patient-controlled-analgesia-pumps-market-to-grow-rapidly-hitting-us-3832-48-mn-by-2034-at-19-30-cagr-due-to-rising-surgeries-chronic-pain-prevalence-and-patient-centric-pai.html) |
| **Infusion pump software** | $1.21B (2025) → $1.82B (2031), 7.04%; DERS = 44.28% of software share (2024) | [Mordor](https://www.mordorintelligence.com/industry-reports/infusion-pump-software), [SNS](https://www.snsinsider.com/reports/infusion-pump-software-market-2033) |
| **IV infusion pumps** | $6.72B (2025); pediatrics/neonatology = **27%** of it (≈$1.81B) | [Grand View](https://www.grandviewresearch.com/industry-analysis/intravenous-infusion-pump-market) |
| **Ambulatory infusion pumps** | **$885.3M (2023)** vs **$14.8B (2023) → $23.6B (2030) @ 6.9%** — a **16.7× disagreement** | [Grand View](https://www.grandviewresearch.com/horizon/statistics/intravenous-infusion-pumps-market/product/ambulatory-infusion-pumps/global), [Fairfield](https://www.globenewswire.com/news-release/2024/04/10/2860863/0/en/Ambulatory-Infusion-Pumps-Market-is-Set-to-Hit-US-23-6-Bn-by-2030-Capturing-a-CAGR-of-6-9-Projects-Fairfield-Market-Research.html) |
| **Home infusion therapy** | 2023 base $31.9–38.9B; → **$61.72B (2030) @ 8.2%** (GVR) or $71.82B (2032) @ 8.36% (SNS) or $35.60B (2030) @ 6.5% (Mordor) | [GVR](https://www.grandviewresearch.com/press-release/global-home-infusion-therapy-market), [SNS](https://www.globenewswire.com/news-release/2024/09/23/2951513/0/en/Home-Infusion-Therapy-Market-Size-Projected-to-Reach-USD-71-82-Billion-by-2032-with-8-36-CAGR-SNS-Insider), [Mordor](https://www.mordorintelligence.com/industry-reports/home-infusion-market) |

**The load-bearing observation:** the PCA pump segment, on the most methodologically explicit estimate found (Mordor, which publishes its restraint weights), is **~$0.5B growing at 5.51%** — roughly **2.5% of the infusion pump market** and growing **~2 points slower** than the category it sits inside. Even the most generous competing estimate ($2.9B) makes PCA a mid-single-digit share of infusion. A portfolio anchored on PCA is anchored on the slowest-growing corner of a mid-single-digit-growth market.

### Competitive structure (from company filings, not vendor estimates)

| Company | Reported infusion-relevant revenue | Source |
|---|---|---|
| **BD** — Medication Management Solutions | **$3.47B (FY2025)** (includes Pyxis dispensing, not pumps alone); Alaris relaunch added ~50 bps to 2024 top line | [BD FY2025 results](https://investors.bd.com/news-events/press-releases/detail/915/bd-reports-fourth-quarter-and-full-year-fiscal-2025-financial-results) |
| **ICU Medical** — FY2024 | Infusion Consumables **$1.11B** (49.7%), Infusion Systems **$684.2M** (30.7%), Vital Care **$437.9M** (19.6%); US = 60.8% of revenue | [ICU Medical Q4 2024](https://ir.icumed.com/news-releases/news-release-details/icu-medical-announces-fourth-quarter-2024-results-and-provides) |
| **Baxter** | Infusion systems reported within Medical Products & Therapies; Q4 2024 strength attributed to **Novum IQ** pump ramp; discrete pump revenue not broken out | [Baxter FY2024 results](https://www.baxter.com/baxter-newsroom/baxter-reports-fourth-quarter-and-full-year-2024-results) |

Two structural facts matter more than any share percentage:

1. **Both leaders have been quality-impaired, and neither is fully recovered.** BD: Class I Alaris recall (2020), consent decree to 2023, relaunch 2023, **infusion-set recalls still expanding in Sept 2025**. ICU Medical: acquired Smiths Medical for **$2.35B (Jan 2022)** and then absorbed [recalls, an FDA warning letter, and declining sales](https://www.medtechdive.com/news/icu-medical-fda-warning-letter-infusion-pumps/746455/). This is a genuine and *currently open* window for a clean-quality-record entrant — and it is a window on **quality posture**, not on features.
2. **The consumables tail, not the pump, is the business.** ICU Medical earns **1.6× more from infusion consumables than from infusion systems**. A pump-only entrant is competing for the smaller half of the revenue pool.

### Ambulatory / CADD franchise position

ICU Medical [acquired Smiths Medical in January 2022 for $2.35B](https://www.sec.gov/Archives/edgar/data/883984/000088398422000005/exhibit991.htm), creating a ~$2.5B pro-forma infusion company. Smiths brought **strong positions in syringe, PCA, and ambulatory infusion** — the **CADD** ambulatory franchise plus **Medfusion** syringe pumps. So the incumbent that owns the ambulatory PCA benchmark (CADD) is the **same** incumbent that owns the KLAS-winning hospital pump (Plum 360) **and** the leading PCA franchise. Any PCA-anchored strategy contemplating an ambulatory extension is entering ICU Medical's home segment, not an open field. Mitigating factor: ICU Medical's post-acquisition quality record is poor, which is where the opening is.

### How a new entrant actually wins placements (GPO / IDN)

- Hospitals plan capital on **~3-year horizons**; value analysis committees weigh **clinical evidence, total cost of ownership, GPO contract status, and comparison to installed base** ([HPN](https://www.hpnonline.com/sourcing-logistics/article/13000731/making-a-playbook-for-capital-purchases), [MedEquip GPO guide](https://www.medequipdirectory.com/guides/group-purchasing-organization-gpo-medical-equipment-guide/)).
- **GPO contract status is a gate, not a discount.** A device not on the IDN's GPO agreement is frequently not evaluable, regardless of specification.
- **TCO dominates unit price.** Service contracts approach purchase cost over 5 years; smart-pump **software licences run 10–15% of system replacement value annually**; **networking to hospital/pharmacy/EMR more than doubles cost** ([AHRQ *Making Healthcare Safer III*](https://www.ncbi.nlm.nih.gov/books/NBK555506/)).
- **Fleet standardisation is the real switching cost.** Pumps are bought as fleets with matched consumables, drug libraries, and EMR interoperability. Displacement happens at fleet-replacement events or after a competitor's recall — not on feature parity.

---

## The PCA utilization question

**This is the most consequential section in this file, and also the one with the weakest available evidence. Both halves of that sentence matter.**

### The question

The portfolio is anchored on PCA (PP3500 / PainEase PCA Advanced). If IV PCA is being structurally displaced from surgical pathways, then every competitive claim in the project documents — accuracy, battery life, barcode scanning, drug library depth — is optimisation inside a shrinking use case. That is a different and worse problem than losing share to BD.

### What the evidence supports

**1. The clinical guideline direction is explicitly against routine IV PCA.** The [ERAS Society 2025 colorectal guidelines](https://www.sciencedirect.com/science/article/pii/S0039606025002491) state that **evidence does not strongly support opioid patient-controlled analgesia** in colorectal surgery, that **non-opioid multimodal analgesia is as effective as opioid PCA**, and that a multimodal strategy should be used **rather than relying on routine IV PCA alone** — for both open and minimally invasive surgery. The [2018 ERAS colorectal guidelines](https://link.springer.com/article/10.1007/s00268-018-4844-y) established the same direction. Grade: **SUBSTANTIATED**.

**2. Where ERAS is implemented, PCA use collapses — not declines.** Reported cohort effects:
- PCA use falling from **68.4% to 0%** in certain ERAS groups.
- A multimodal QI project: **2/36 patients (5.6%)** required IV PCA opioids under multimodal vs **30/36 (83.3%)** under conventional care ([PMC9327409](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9327409/)).
- ICU opioid-free rate **94.0% (ERAS) vs 19.9% (control)**.

These are single-centre and pathway-specific, so they establish the *mechanism and magnitude* of displacement where ERAS lands — not the national rate. Grade: **SUBSTANTIATED** (individual studies), **INFERRED** for extrapolation.

**3. Regional anaesthesia is displacing IV PCA in specific procedure families.** Suprascapular nerve block in arthroscopic rotator cuff repair ([PMC12386885](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12386885/)); TAP block vs IV PCA in robot-assisted partial nephrectomy ([PMC11277915](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11277915/)); patient-controlled *epidural* vs IV PCA in gynaecologic oncology ([PubMed 26587406](https://pubmed.ncbi.nlm.nih.gov/26587406/), [19395071](https://pubmed.ncbi.nlm.nih.gov/19395071/)). A [2018 Cochrane-style review](https://pubmed.ncbi.nlm.nih.gov/30161292/) found epidural's incremental pain benefit over IV-PCA after intra-abdominal surgery **"modest and unlikely to be clinically important"** — which cuts *against* displacement on efficacy grounds and suggests displacement is driven by opioid-stewardship policy and recovery-pathway design, not by superior analgesia. Grade: **SUBSTANTIATED**.

**4. The market data is consistent with structural headwind.** PCA pumps at **5.51% CAGR** ([Mordor](https://www.mordorintelligence.com/industry-reports/patient-controlled-analgesia-pumps-market)) vs infusion pumps overall at **7.3–8.2%**. PCA is growing but **underperforming its own category by ~2 points** — the signature of a segment losing share of use, not one being eliminated. Grade: **SUBSTANTIATED (vendor estimate)**.

### What the evidence does NOT support

**IV PCA is not disappearing, and claims that it is would be overstated.**

- A **2025 expert consensus on postoperative PCA follow-up** states PCA is *"the most widely used and optimal analgesic method for postoperative pain"* and that IV PCA *"remains essential for inpatient pain management"* ([Sciopen](https://www.sciopen.com/article/10.12290/xhyxzz.2025-0340), [DOAJ](https://doaj.org/article/5e076502851f4f91b79aeafd2b889bb3)). Note: this is a Chinese consensus document, which matters — APAC is the fastest-growing PCA region at 7.29%, and utilisation trends there differ from US/EU.
- 2024–2025 guidelines integrate PCA **into** multimodal protocols rather than abandoning it ([2024 clinical practice guidelines for postoperative pain](https://www.sciencedirect.com/science/article/pii/S2957391225000361), [Frontiers 2025 narrative review](https://www.frontiersin.org/journals/anesthesiology/articles/10.3389/fanes.2025.1709252/full)).
- The active clinical literature is still **optimising** PCA — basal-infusion removal cut PCA discontinuation from **23.2% to 6.5%** ([PMC11317320](https://pmc.ncbi.nlm.nih.gov/articles/PMC11317320/)); risk-factor work on IV PCA discontinuation continues ([Nature Sci Rep 2023](https://www.nature.com/articles/s41598-023-45033-2)); HFMEA work on PCA safety published 2025 ([PMC12605075](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12605075/)). Nobody optimises a dying modality.

### The honest synthesis

The defensible reading is **narrowing, not collapse**: IV PCA is being **removed from the elective surgical pathways that ERAS has reached** (colorectal, joint replacement, gynae-onc, thoracic) and **retained** for the cases multimodal and regional techniques cannot cover — opioid-tolerant patients, trauma, oncology and palliative pain, sickle-cell crisis, burns, and settings without ERAS infrastructure. The economic consequence is that PCA's **unit volume per surgical case falls** while its **clinical necessity in the residual population stays high**. That is exactly what a 5.5% CAGR in a 7–8% market looks like.

Grade: **INFERRED** — reasoning: guideline direction + ERAS cohort magnitudes + sub-category CAGR gap all point one way; the 2025 consensus and ongoing optimisation literature bound the claim short of "collapse."

### A vendor blind spot worth knowing about

Mordor's PCA pump report publishes weighted restraints — recalls (−0.8%), patient-education medication errors (−0.5%), cybersecurity (−0.4%), supply chain (−0.6%). It lists **ERAS, opioid-sparing multimodal analgesia, and regional anaesthesia nowhere**. The single largest structural force acting on this segment is absent from the segment's own market model. Any forecast built on that report inherits the omission. Grade: **SUBSTANTIATED** (direct read of the report's restraints section).

---

## What could NOT be verified

Listed with what was searched and what was seen, so the gap is re-openable rather than mistaken for absence of a problem.

| Item | What was searched | What was seen | Why it did not confirm |
|---|---|---|---|
| **A national IV PCA utilization time-series (US)** | PubMed/PMC for Premier-database and NIS trend studies; opioid-stewardship reviews; ERAS utilisation studies | Closest is [Bykov et al. 2021, *Pharmacoepidemiol Drug Saf*](https://pubmed.ncbi.nlm.nih.gov/33368798/) — Premier database, 6M+ inpatient surgical adults, 2007–2017, tracking opioid and opioid-sparing analgesic use. Direct fetch **timed out**; the abstract as surfaced does not break out PCA as a route. | **This is the highest-value missing evidence in the whole assessment.** The strategic thesis rests on it. Recommend a targeted retrieval of Bykov 2021 full text plus a search for NIS/Premier analyses of PCA *route* 2015–2024. |
| **BD 35% / Baxter 25% / B. Braun 15%** | iData, Signify Research, MarketsandMarkets, Coherent, BCC, DelveInsight, SkyQuest | iData: "BD holding over **50%** of the large volume pump market in **2019**." Signify has a competitor-share infographic — **gated behind a request form**. | No source produced the triple. The iData figure contradicts the BD number for BD's strongest segment. |
| **Neonatal infusion pump market at $3.2B or $2.06B** | Multiple firms, direct quoted-figure searches | No standalone neonatal-infusion-pump report at any size. Only segment shares: pediatrics/neonatology = **27%** of IV infusion pumps; NA syringe infusion pumps **$701.15M (2025) → $1,629.67M (2035) @ 8.8%** ([NovaOne](https://www.novaoneadvisor.com/report/north-america-syringe-infusion-pumps-market)). | The segment may simply not be sized independently by any major firm. Both project figures are unsourceable as stated. |
| **"NICU $420M (2025) → $580M (2030)"** | Same searches | Nothing matching. (Implied CAGR is **6.67%**, itself inconsistent with the 5.6% quoted for the parent segment in the same line.) | Unsourceable. |
| **$1,295 ICU Medical Plum 360** | Refurb dealer listings, pricing aggregators | Plum 360 **repair service $450**; no unit listing at $1,295 | Not found. |
| **$8,000–12,000 per neonatal pump** | Pricing aggregators, dealer listings | Highest published new-unit band for any pump class: **$6,865** (LVP); syringe pumps top out **$5,982** | Contradicted rather than merely unverified. |
| **China infusion pump market at $19.5B** | Firm reports, APAC regional reports | China = 38.5% of APAC (2024); one figure at ~$0.92B (2026); scope-inconsistent sub-segment figures ($11.4M, $56.9M) | No source anywhere near $19.5B. |
| **Canada $10.3B, 7.3% CAGR** | Not searched directly | — | Flagged on plausibility grounds only (would exceed the US market); the 7.3% CAGR exactly matches the published **US** CAGR, suggesting copy-paste. **Recommend direct verification.** |
| **The $3.5B (2023) global base** | All firm searches | No firm found placing global infusion pumps near $3.5B in any recent year | Possibly a sub-segment figure (ambulatory at $885M? PCA at $2.4–2.9B?) mislabelled as the global total — but this is speculation, not a finding. |
| **Grand View / MDPI primary text** | Direct WebFetch | **HTTP 403** on `grandviewresearch.com` (home infusion, PCA pumps) and `mdpi.com` (PCA orthopaedic systematic review) | Figures used come from press releases and search summaries — a weaker evidence rung, flagged inline. |
| **Signify Research competitor-share infographic** | Direct WebFetch | Page confirms the analysis exists; data is behind a request form | Likely the best available real share data. Worth requesting. |

---

## Implications (OPINION — labelled)

Everything below is **OPINION**. It is the researcher's judgment from the evidence above, not a sourced finding. It is labelled because no public source states these conclusions.

**OPINION 1 — The market section of these documents cannot be used as-is, and the failure mode matters more than the individual errors.** Five claims are arithmetically self-inconsistent, and in at least four cases (the $19.5B triple, the 7.3% Canada CAGR, the 5.6% neonatal CAGR applied to two different number pairs, the 8.2% CAGR carried onto the wrong endpoints) the defect pattern is **a real vendor figure copied into a slot it does not describe**. That is not sloppy rounding; it is a sourcing-discipline failure that will reproduce itself wherever these documents are cited downstream. Anything that consumed these figures — the $350M Year-5 revenue, 58% IRR, $425M NPV — should be treated as unfounded until re-derived.

**OPINION 2 — The PCA anchoring risk is real, is structural, and is not visible anywhere in the three documents.** The documents frame PCA as a "growing patient-controlled analgesia market" (`state-of-the-art-analysis.md` L16). The best-documented estimate has it growing at **5.51%** — below the infusion category, below home infusion, below AI-enabled devices, below every other segment the documents name. Meanwhile the governing clinical guideline for the highest-volume elective surgical population says **do not rely on routine IV PCA**. A competitive assessment that discusses ±0.5% volumetric accuracy and 150-hour battery life at length while never naming ERAS is optimising the wrong axis. **This should be the first finding of the parent gap analysis.**

**OPINION 3 — The differentiation claims are aimed at a buyer who is not making the decision.** Accuracy, battery life, and drug-library depth are *specification* differentiators. The evidence on how placements are actually won points at **GPO contract status, fleet-level TCO (software licences at 10–15% of replacement value annually, service contracts, EMR-integration cost that more than doubles the bill), and consumables economics** — where ICU Medical earns 1.6× more from consumables than from systems. A device that wins the spec sheet and loses the TCO model does not get evaluated.

**OPINION 4 — The genuine opening is quality posture, and it is time-limited.** Both leaders are quality-impaired *right now*: BD's Alaris infusion-set recalls were still expanding in September 2025; ICU Medical took an FDA warning letter and a recall series after the Smiths acquisition. A clean, well-documented DHF and an unblemished recall record is a more credible wedge into a fleet-replacement decision than any specification claim in these documents — and it is a wedge that closes as the incumbents remediate. This is worth saying plainly because it argues for a *regulatory/quality-led* commercial narrative rather than a feature-led one.

**OPINION 5 — The ambulatory extension is the strongest strategic hedge and the documents under-argue it.** If IV PCA is narrowing inside the hospital, ambulatory/home pain management is where PCA-adjacent volume goes, and home infusion is growing at 6.5–8.4% off a $32–39B base — far larger and faster than hospital PCA. But this runs directly into ICU Medical's CADD franchise, so it must be argued on quality record and TCO, not on the 180g/7-day specification comparison the documents currently lead with.

**OPINION 6 — Recommended next evidence step, in priority order.** (1) Retrieve Bykov 2021 full text and search for a Premier/NIS analysis of PCA *route* utilisation 2015–2024 — this single artifact would move the central thesis from INFERRED to SUBSTANTIATED. (2) Request the Signify Research competitor-share infographic. (3) Re-derive every financial projection that consumed a figure marked ARITHMETICALLY WRONG or CONTRADICTED above.

---

## Changelog

| Date | Author | Summary |
|------|--------|---------|
| 2026-08-05 | AI assistant(s) | Initial public-source research file for the `competitive-threat-assessment` analysis. Tested 11 project claim groups (19 sub-claims) from `competitive-product-assessment.md`, `state-of-the-art-analysis.md`, and `strategic-market-ai-infusion.md` against public sources; computed all CAGRs independently; identified the SkyQuest global-2025 figure as the probable provenance of the repeated $19.5B / 8.2% pairing; added the PCA utilization structural-headwind section. |
