---
id: research-ai-connectivity-regulatory
parent_analysis: competitive-threat-assessment
type: research
authored_by: agent:general-purpose
created: 2026-08-05
---

# Research — AI/ML, Connectivity, and Regulatory Pathway Reality Check

_Demo sample data — not for clinical use._ The **device program** this research supports (PP3500 / PainEase PCA Advanced) is fictional demo content. The **research findings below are real**: every citation resolves to a live public source retrieved on 2026-08-05, and no statistic, guidance title, date, or URL in this document was invented. Where a project claim could not be corroborated, that is stated explicitly rather than papered over.

---

## Method + limits

**Question this document answers.** The PP3500 strategy rests on a catch-up thesis: competitors are said to hold an AI-driven predictive-monitoring lead, connectivity/EHR interoperability is treated as table stakes, and an FDA PCCP is treated as the mechanism that lets the product evolve after clearance. This document tests that thesis against the real state of the art and the real regulatory pathway, using public sources only.

**Sources used, in priority order.**

| Tier | Source | How accessed |
|---|---|---|
| Primary — FDA | AI-Enabled Medical Device List (full HTML table, parsed to CSV) | `curl` + local parse, 2026-08-05 |
| Primary — FDA | Guidance documents (PCCP AI final; PCCP general draft) — page metadata + full PDF | `curl` + PDF text extraction |
| Primary — FDA | MDUFA V FY2025 Performance Report (PDF) | `curl` + PDF text extraction |
| Primary — FDA | openFDA `device/510k` and `device/classification` APIs | REST, JSON |
| Primary — NLM | PubMed E-utilities (`esearch` / `esummary` / `efetch`) | REST |
| Primary — CISA | ICS-Medical advisories; 2026 SBOM Minimum Elements | direct page fetch (delegated researcher) |
| Primary — statute | 21 U.S.C. § 360n-2 (§ 524B); Federal Register 88 FR 19148 | uscode.house.gov, govinfo.gov |
| Secondary | Vendor pages, ECRI/ISMP/AAMI/HSCC/HHS publications, KLAS, survey reports | web search / fetch (delegated researchers) |

**Delegation.** Two researchers ran in parallel on Sections B and D while this agent held Sections A and C. Both reported in full. Notably, the interoperability researcher **independently reproduced the Section A finding** (1,524 devices, zero `infusion`, zero `pump`, zero product code FRN) by a separate retrieval path — the headline result is therefore double-sourced.

**Grading vocabulary.** `SUBSTANTIATED` — a primary or clearly attributable source with a URL and a date supports the claim as stated. `INFERRED` — not directly stated by any source, but derivable from cited primary data; the derivation is shown. `OPINION` — analyst judgment, labelled, with the reason no source settles it. `UNVERIFIED` — searched for and not found; what was searched and what turned up instead is recorded.

**Limits a reader should carry forward.**

1. **`www.fda.gov` blocks the standard fetch agent** (HTTP 404 to `WebFetch`, HTTP 200 to a browser user-agent via `curl`). All FDA content here was retrieved by `curl` with a browser user-agent and parsed locally. This is a retrieval workaround, not a data caveat — the bytes are FDA's.
2. **The web-search budget for this session was exhausted** partway through (200/200 calls, shared with the delegated researchers). A handful of items marked `UNVERIFIED` may be under-searched rather than genuinely unsourced — they are itemised in *What could NOT be verified*. PubMed E-utilities, the openFDA API, and direct `curl` retrieval of fda.gov / cisa.gov / govinfo.gov remained available throughout and carry the load for every load-bearing finding. **Those four scriptable sources produced the highest-value results in this research and are worth going to first next time, ahead of search.**
3. **FDA's AI-Enabled Medical Device List is explicitly non-exhaustive.** FDA states: _"The list is not a comprehensive resource of AI-enabled medical devices. Instead, the list includes AI-enabled medical devices that were identified primarily based on the use of AI-related terms in the summary descriptions of their marketing authorization document and/or the device's classification."_ An absence on this list therefore means _"no AI-related terminology in the public authorization summary,"_ not _"no machine learning anywhere in the product."_ Section A treats that distinction as load-bearing and cross-checks the absence three independent ways.
4. **The openFDA cross-vendor comparison in Section C is a large sample, not a census** — openFDA caps pagination at 7,000 records, so the AI-vs-non-AI median comparison rests on ~6,350 of the 510(k)s decided in 2024–2025, not all of them.

---

## A. AI/ML in cleared infusion pumps

### A.1 The headline finding: there are none

**No FDA-authorized infusion pump of any kind appears on FDA's AI-Enabled Medical Device List.** Not a large-volume pump, not a syringe pump, not a PCA pump, not a pump-resident safety-software suite, not an infiltration monitor.

Source: FDA, [Artificial Intelligence-Enabled Medical Devices](https://www.fda.gov/medical-devices/software-medical-device-samd/artificial-intelligence-enabled-medical-devices), page states **"Content current as of: 06/16/2026"**; retrieved 2026-08-05. The list contained **1,524 device rows**, earliest decision 1995-09-29, latest decision 2026-03-30.

This absence was checked three independent ways, because a single negative search is weak evidence:

| # | Check | Method | Result |
|---|---|---|---|
| 1 | Free-text | Case-insensitive search of all 1,524 rows for `infusion` and for `pump` across every column | **0 matches** |
| 2 | Product code | Enumerated every product code under the infusion-pump regulations 21 CFR 880.5725, 870.1800, 880.5730 via the openFDA classification API (19 codes: FRN, MEA, MEB, LZG, LZH, LZF, OPP, PHC, PMS, MRZ, MRH, MHD, LDR, QJY, QFG, DQI, PKP, LGZ, LHF), then intersected against the AI list's `Primary Product Code` column | **1 match — and it is not a pump** (see A.2) |
| 3 | Vendor | Searched all rows for every major infusion vendor: Becton Dickinson / CareFusion, ICU Medical, Baxter, B. Braun, Fresenius Kabi, Smiths Medical, Ivenix, Hospira, Moog, Zyno, Eitan / Q Core | **0 pump products.** The only "BD" hits are Therapixel's *MammoScreen BD* (a breast-density radiology algorithm, unrelated company) and a 1995 BD Diagnostics cytology screener |

**Grade: SUBSTANTIATED.** All three checks are reproducible against the cited FDA page and the openFDA classification endpoint.

### A.2 The single near-miss, and why it does not count

The one row whose product code sits inside an infusion-pump regulation:

| Decision | Submission | Device | Company | Panel | Product code |
|---|---|---|---|---|---|
| 2019-11-04 | K190013 | WellDoc BlueStar | WellDoc, Inc. | General Hospital | MRZ — *Accessories, Pump, Infusion* |

BlueStar is a diabetes self-management and insulin-dose-guidance mobile application. It is regulated under an infusion-pump *accessory* code but is not an infusion pump, contains no pump, and delivers nothing. Counting it as "an AI-enabled infusion pump" would be a classification artifact, not a fact about the market.

**Grade: SUBSTANTIATED** (the row exists exactly as shown); **the interpretation that it does not constitute an AI-enabled pump is INFERRED** from the device's function as described in its own name and panel assignment.

### A.3 What the panel distribution actually looks like

The list is overwhelmingly imaging. Counts computed from the parsed table (n = 1,524):

| Panel (lead) | Devices | Share |
|---|---:|---:|
| Radiology | 1,164 | 76.4% |
| Cardiovascular | 147 | 9.6% |
| Neurology | 70 | 4.6% |
| Anesthesiology | 26 | 1.7% |
| Gastroenterology-Urology | 25 | 1.6% |
| Hematology | 21 | 1.4% |
| Ophthalmic | 10 | 0.7% |
| Pathology | 9 | 0.6% |
| Clinical Chemistry | 9 | 0.6% |
| General and Plastic Surgery | 8 | 0.5% |
| Orthopedic | 7 | 0.5% |
| Microbiology | 7 | 0.5% |
| General Hospital | 5 | 0.3% |
| Dental | 5 | 0.3% |
| Clinical Toxicology | 5 | 0.3% |
| Obstetrics and Gynecology | 4 | 0.3% |
| Ear Nose & Throat | 1 | 0.1% |
| Immunology | 1 | 0.1% |

Two panels matter for a PCA pump. **General Hospital** — the panel an infusion pump would most plausibly sit under — has **five** AI-enabled devices in the entire history of the list, and all five are surgical-count, sepsis-scoring, or diabetes-app products. **Anesthesiology** has 26, and every one is a sleep-apnea test, a respiratory-sound classifier, a nerve-block ultrasound aid, or a nociception monitor. Neither panel contains a single delivery device.

**Grade: SUBSTANTIATED** (counts derived from the cited FDA table).

### A.4 The cleared infusion-pump landscape, for contrast

To confirm the absence is not an artifact of nobody clearing pumps at all, the openFDA `device/510k` endpoint was queried for the general infusion-pump code **FRN** over 2020-01-01 → 2026-12-31: **31 clearances**, from every major vendor. A representative slice:

| Decision | K-number | Applicant | Device |
|---|---|---|---|
| 2025-07-28 | K251636 | Baxter Healthcare | Spectrum IQ Infusion System with Dose IQ Safety Software |
| 2025-04-25 | K243855 | CareFusion 303 (BD) | BD Alaris Infusion System with Guardrails Suite MX |
| 2025-04-02 | K242114 / K242115 | ICU Medical | Plum Solo / Plum Duo Precision IV Pump |
| 2024-09-05 | K242390 | Baxter Healthcare | Novum IQ Syringe Pump |
| 2024-03-29 | K211122 | Baxter Healthcare | Novum IQ Large Volume Pump |
| 2023-08-24 | K223607 | ICU Medical | Plum Duo Infusion System |
| 2023-07-21 | K211218 | CareFusion 303 (BD) | BD Alaris System with Guardrails Suite MX v12.1.2 |
| 2023-03-10 | K213744 | Eitan Medical | Avoset Infusion Pump System |
| 2022-03-01 | K210073 / K210074 | Fresenius Kabi | Agilia VP / Agilia SP Infusion Systems |
| 2020-11-19 | K192860 | Q Core Medical | Sapphire Infusion Pump |

The market is active. **None of these 31 devices appears on the AI-Enabled Medical Device List.**

**Grade: SUBSTANTIATED** (openFDA `device/510k`, `product_code:FRN`, retrieved 2026-08-05).

### A.5 Pump safety software — the same answer

Product code **PHC — "Infusion Safety Management Software"** is where drug-library / DERS / interoperability software is cleared. It has **ten clearances in its entire history**:

| Decision | K-number | Applicant | Device |
|---|---|---|---|
| 2026-04-02 | K252130 | ICU Medical | LifeShield Infusion Safety Software Suite |
| 2025-06-20 | K243062 | Becton Dickinson | BD Intelliport System |
| 2025-04-02 | K242117 | ICU Medical | LifeShield Infusion Safety Software Suite |
| 2024-03-29 | K230665 | Baxter Healthcare | Dose IQ Safety Software |
| 2023-08-24 | K223606 | ICU Medical | LifeShield Infusion Safety Software Suite |
| 2022-08-30 | K211124 | Baxter Healthcare | Dose IQ Safety Software |
| 2022-03-01 | K210075 | Fresenius Kabi | Vigilant Software Suite / Vigilant Master Med |
| 2019-04-30 | K182092 | Becton, Dickinson | BD Intelliport System |
| 2014-12-18 | K141474 | Becton Dickinson | Intelliport System |
| 2014-07-25 | K141193 | Smiths Medical | Medfusion 4000 Device-Specific Reports Software |

**None is on the AI list.** The competitive software layer that actually exists on cleared pumps is rules-based safety software — drug libraries, hard/soft dose limits, reporting — not learned models.

**Grade: SUBSTANTIATED** (openFDA `product_code:PHC`, retrieved 2026-08-05).

### A.6 Infiltration/extravasation detection — one cleared product, and it is not AI

The project's "15–30 minute early warning for infiltration" ambition has exactly one regulatory precedent to point at. Product code **PMS — "Peripheral Intravenous (PIV) Infiltration Monitor"** has **five clearances, all held by a single company, ivWatch, LLC**:

| Decision | K-number | Device |
|---|---|---|
| 2024-03-15 | K233881 | ivWatch Model 400 |
| 2022-08-24 | K222212 | ivWatch Model 400 |
| 2020-07-02 | K192385 | ivWatch Model 400 + accessories |
| 2016-12-22 | K162478 | ivWatch |
| 2016-02-11 | K153605 | ivWatch Model 400 |

**ivWatch does not appear on the AI-Enabled Medical Device List.** It is an optical (near-infrared) sensing device, not a learned predictive model, and it is a separate monitor rather than a pump function.

**Grade: SUBSTANTIATED** (openFDA `product_code:PMS`; absence checked against the parsed AI list).

### A.7 PCA pumps specifically — a regulatory backwater

Product code **MEA — "Pump, Infusion, PCA"** has 31 clearances across its history. The **most recent is 2017-08-29** (K162165, Summit Medical ambIT), with K170982 (Smiths CADD-Solis, 2017-08-24) just before it. There has been **no new MEA clearance in roughly nine years.**

This cuts two ways and both are worth stating plainly:

- It weakens the "competitors are racing ahead on AI PCA pumps" premise — nobody is clearing new PCA pumps at all, with or without AI.
- It weakens the predicate landscape for a novel PP3500 feature set: the newest same-code predicate is a 2017 device, so a substantial-equivalence argument for AI-driven predictive monitoring has no recent same-code precedent to lean on.

**Grade: SUBSTANTIATED** (openFDA `product_code:MEA`, sorted by decision date descending).

### A.8 What smart pumps actually do today: DERS, not ML

The mature, widely deployed pump-safety technology is the **dose error reduction system (DERS)** — a drug library defining concentration/dose/rate limits, with hard limits that block programming and soft limits that warn and can be overridden. This is deterministic, rules-based, and configured by pharmacy. It is not machine learning and does not predict anything.

Its real-world limitation is well documented and is a **compliance** problem, not an **algorithm** problem: clinicians bypass the library. Giuliano KK et al., *"Intravenous Smart Pump Drug Library Compliance: A Descriptive Study of 44 Hospitals,"* **J Patient Saf** 2018;14(4):e76–e82, [PMID 28574959](https://pubmed.ncbi.nlm.nih.gov/28574959/), analysed 12 months of data across 7 hospital systems and 44 hospitals and found compliance varying significantly both within and between systems, with the number of drug-library profiles and the pump type as correlated factors.

The recent evidence says the lever that moves DERS compliance is **integration, not intelligence** — see Section B.3, where EMR integration lifted DERS compliance to 96.1%.

**Grade: SUBSTANTIATED.**

### A.9 The peer-reviewed literature on ML in infusion pumps is close to empty

PubMed E-utilities queries, run 2026-08-05:

| Query | Hits |
|---|---:|
| `infusion pump machine learning occlusion detection` | **0** |
| `peripheral intravenous infiltration extravasation detection machine learning` | **0** |
| `smart pump alert fatigue non-actionable alerts reduction` | **0** |
| `infusion pump artificial intelligence predictive monitoring adverse event` | 4 (three are continuous-glucose-monitoring papers; the fourth is a neonatal PIV sensor alarm algorithm, [PMID 31815770](https://pubmed.ncbi.nlm.nih.gov/31815770/)) |
| `(infusion pump) AND (machine learning OR artificial intelligence OR deep learning)` | 256 — **dominated by automated insulin delivery / closed-loop diabetes**, a different device class (LZG/QFG) with its own regulatory and clinical literature |

The one genuinely adjacent hit is Mitchell R. et al. (2020), *"Development of an Alarm Algorithm, With Nanotechnology Multimodal Sensor, to Predict Impending Infusion Failure and Improve Safety of Peripheral Intravenous Catheters in Neonates,"* **Adv Neonatal Care**, [PMID 31815770](https://pubmed.ncbi.nlm.nih.gov/31815770/) — a sensor-plus-algorithm research device for neonatal PIV failure, not a cleared pump function.

**Grade: SUBSTANTIATED** (queries and hit counts are reproducible against the PubMed E-utilities API). **Interpretation — that ML-based prediction in infusion delivery is a research topic rather than a deployed product capability — is INFERRED** from the combination of zero clearances (A.1–A.7) and near-zero literature.

### A.10 Where predictive deterioration monitoring *is* cleared — and it is not on a pump

FDA has authorized clinical-deterioration prediction, but as **standalone software**, decoupled from any delivery device:

| Decision | Submission | Device | Company | Panel | Code |
|---|---|---|---|---|---|
| 2024-06-21 | K233253 | eCARTv5 Clinical Deterioration Suite (eCART) | AgileMD, Inc. | Cardiovascular | QNL |
| 2024-04-02 | DEN230036 | Sepsis ImmunoScore | Prenosis, Inc. | General Hospital | SAK |

This is the shape the capability takes in the real market: a SaMD product consuming EHR and monitor data, cleared on its own, integrating alongside the pump rather than inside it.

**Grade: SUBSTANTIATED** (both rows appear verbatim on the cited FDA AI list).

---

## B. Interoperability

### B.0 The number that reframes the whole strategy

**~88% of US hospitals have smart pumps. ~13% have EHR-to-pump auto-programming.**

| Metric (2020) | Value | Trend |
|---|---:|---|
| US hospitals using smart pumps | **87.9%** | 32.2% (2005) → 88.1% (2017) → 87.9% (2020) — **saturated** |
| US hospitals with EHR→pump **auto-programming** | **13.4%** | 5.9% (2013) → 8.9% (2017) → 13.4% (2020) — **slow growth** |
| US hospitals with pump→EHR **auto-documentation** | **14.9%** | |
| US hospitals where nurses still **manually document** infusions | **85.1%** | |

Source: Pedersen CA, Schneider PJ, Ganio MC, Scheckelhoff DJ, ASHP National Survey of Pharmacy Practice in Hospital Settings, **Am J Health Syst Pharm** 2021;78(12):1074–1093, Table 13.

The pump itself is a commodity. **The connection is not.** Roughly six out of seven US hospitals have not crossed the interoperability gap, despite every major vendor selling the capability and the published evidence favouring it.

**Grade: SUBSTANTIATED** for the 2020 figures. **The current (2024–2026) national adoption rate is UNVERIFIED — no newer survey exists.** BD reported ~960 live interoperability sites as of 2025-11-13 against ~6,100 US hospitals (AHA 2024 Annual Survey), which implies higher-than-13.4% coverage for BD alone, but "sites" and "hospitals" are not the same denominator. **Do not state a 2026 adoption percentage as fact.**

### B.1 Interoperability is the capability that actually shipped

Every major infusion vendor has cleared and deployed EHR-to-pump interoperable **auto-programming** — the pharmacy-verified order flows from the EHR to the pump, the nurse scans and confirms rather than keying in rate and dose, and the infusion event flows back to the EHR for documentation ("closed-loop"). The cleared software layer for this is product code **PHC**, enumerated in A.5: BD Intelliport, ICU Medical LifeShield, Baxter Dose IQ, Fresenius Vigilant.

| Vendor | Product | Key clearance | Interoperability posture |
|---|---|---|---|
| **BD (CareFusion 303)** | Alaris System w/ Guardrails Suite MX | K243855 (2025-04-25); K211218 (2023-07-21) | Bi-directional auto-programming + auto-documentation. Epic and Cerner long-standing; **MEDITECH added Nov 2025**. ~960 US sites live, ~12 new sites/month (BD, 2025-11-13) |
| **ICU Medical** | Plum 360 / LifeCare PCA + MedNet | Plum 360 K161469 (2017-03-28); LifeCare PCA K143612 (2016-04-08) | Full IV-EHR interoperability via MedNet; claims first interoperable deployment 2008. Epic + Cerner confirmed in peer-reviewed multi-site studies. First pump to earn UL 2900-1 / 2900-2-1 cybersecurity certification |
| **Baxter** | Spectrum IQ + Dose IQ | K173084 (2018-05-11); K251636 (2025-07-28) | Purpose-built for bi-directional EMR integration; on-screen barcode to drive auto-programming compliance |
| **Fresenius Kabi** | Ivenix; Agilia Connect + Vigilant | Ivenix K183311 (2019-06-07); Agilia K210073/K210074 (2022-03-01) | Acquired Ivenix **2022-05-04** ($240M upfront + milestones). Built-in integration engine |
| **B. Braun** | Infusomat/Perfusor Space + DoseTrac | Infusomat Space K142596 (2015-06-18) | AutoProgramming + AutoDocumentation via DoseTrac. Epic integration announced 2019-08-15; Allscripts Sunrise 2018-10-18 |

Contrast this against Section A: the vendors have shipped connectivity and *not* shipped machine learning. That asymmetry is the single most important structural fact in this research.

**Grade: SUBSTANTIATED** for clearances (openFDA) and for vendor interoperability posture (vendor releases + peer-reviewed deployment papers). **Epic Toolbox / Showroom per-vendor designations are UNVERIFIED** — the Showroom roster requires an Epic UserWeb login and returned 403/404 to anonymous retrieval; the category itself ("Infusion Pump Integration", stage id 35) is confirmed to exist.

**Third-party market view:** KLAS, *"Smart Pumps/EMR Interoperability 2023: How Are Deep Adopters and the Broader Market Progressing?"* (published 2023-05-16) evaluated ICU Medical, B. Braun, Baxter, and BD against Epic and Cerner, and reported **53% of surveyed organizations implementing or planning** interoperability. **Grade: SUBSTANTIATED.**

### B.2 Published safety benefit — systematic review

Borrelli EP, Lucaci JD, Wilson NS, Taneja A, Weiss M, Beer I. *"Evaluating the Impact of Smart Infusion Pump Interoperability on Reducing Medication Administration Errors: A Systematic Literature Review."* **Med Devices (Auckl)** 2025 Apr 15;18:247–260. doi:10.2147/MDER.S522534. [PMID 40256649](https://pubmed.ncbi.nlm.nih.gov/40256649/)

Findings as stated in the abstract:

- Systematic review of PubMed/Medline and Embase (November 2024). **Only three studies met inclusion criteria.**
- Errors directly impactable by interoperability: **15.4% to 54.8% reduction** post-implementation.
- All medication administration errors (cumulative): **21.2% to 90.5% reduction**, "with variability influenced by baseline compliance, study setting, and patient populations."
- The authors' own conclusion flags the evidence gap: _"future research is needed to assess its impact on adverse drug events, clinician workflows, and patient outcomes."_

**Conflict of interest, stated by the authors and material here:** all six authors are employees and/or shareholders of Becton, Dickinson and Company — a pump vendor. The review is the best available synthesis and is also vendor-authored. Both facts should travel together.

The three constituent studies, retrieved individually:

| Study | Setting | Effect | Grade |
|---|---|---|---|
| **Skog et al. 2022**, *J Patient Saf* 18(3):e666–e671, [PMID 35344977](https://pubmed.ncbi.nlm.nih.gov/35344977/) | Community health system; 350 → 367 infusions observed | Total errors 114.6 → 96.5 per 100 infusions (p = 0.02). **High-risk medication errors 12.8 → 6.8 per 100 (p = 0.01).** Continuous medications 12.6 → 6.0 (p = 0.005). **Manual programming accounted for 77.2% of errors vs 22.8% under auto-programming.** Authors' headline: **16% reduction** | SUBSTANTIATED |
| **VanHorn et al. 2024**, *J Pediatr Pharmacol Ther* 29(3):323–330, [PMID 38863851](https://pubmed.ncbi.nlm.nih.gov/38863851/) | Pediatric; 143,997 → 165,343 infusions | **Guardrail alert overrides 23,751 → 5,885 (p < 0.001). High-risk overrides 5,851 → 207 (p < 0.001).** Errors caught pre-administration 197 → 20 | SUBSTANTIATED |
| **Chin et al. 2024** | Australian ICU; 1,727 → 1,505 infusions | Unintended variances/errors **20.8% → 2.0% (the 90.5% figure)** | **SUBSTANTIATED-INDIRECT** — reachable only via Borrelli's review; the primary was not located in PubMed |

**Grade: SUBSTANTIATED** (peer-reviewed, indexed, abstract retrieved via PubMed efetch 2026-08-05), with the COI noted and the Chin provenance flagged.

**The counter-evidence, which the strategy should not omit.** Rothschild JM et al., *"A controlled trial of smart infusion pumps to improve medication safety in critically ill patients,"* **Crit Care Med** 2005, [PMID 15753744](https://pubmed.ncbi.nlm.nih.gov/15753744/) — a randomized time-series in 735 cardiac surgery patients found **serious medication error rates similar in both arms**, with preventable adverse events (11 vs 14) not differing. Smart-pump technology is not self-evidently effective; implementation quality is what determines whether benefit appears. **Grade: SUBSTANTIATED.**

### B.3 Published safety benefit — large single-system study

Afaq H, Colunga S, Hu L, et al. *"Integration of smart infusion pumps with electronic medical records improves safety and staff productivity at a large academic healthcare system."* **Am J Health Syst Pharm** 2026 Jun 27:zxag187. doi:10.1093/ajhp/zxag187. [PMID 42364102](https://pubmed.ncbi.nlm.nih.gov/42364102/)

Retrospective analysis of Baxter Spectrum IQ pump data, January 2021 – August 2024, across six University of Texas Medical Branch hospitals, spanning EMR integration in Q4 2022:

| Metric | Result |
|---|---|
| Hard-limit alert rate | **−50.3%** (p < 0.001) |
| Soft-limit alert rate | **−30.4%** (p < 0.001) |
| Single-step rate change (SSRC) alert rate | **−38.1%** (p < 0.001) |
| Programming steps, auto vs manual | **1.6 vs 3.3 steps** (p < 0.001) |
| Alert resolution time, auto vs manual | **46.3% shorter** (soft limit), **55.0% shorter** (SSRC) |
| **DERS compliance after integration** | **96.1%** |
| Auto-programming compliance | 53.4% overall; 68.3% for high-alert/REMS medications |

Two numbers deserve emphasis. **DERS compliance reached 96.1% after integration** — integration solved the compliance problem that A.8 identifies as DERS's core weakness. And **auto-programming compliance was only 53.4%** — even where the capability is deployed, roughly half of infusions are still programmed manually, which is where the remaining headroom sits.

**Conflict of interest:** co-authors are affiliated with Baxter International and with Boston Strategic Partners (a Baxter-engaged analytics firm). Again vendor-adjacent.

**Grade: SUBSTANTIATED**, with COI noted.

### B.4 Supporting literature on the integration/compliance problem

| Citation | Relevance |
|---|---|
| *"Collaboration to Remove Barriers to Pump Integration With the Electronic Health Record,"* J Healthc Qual, 2024, [PMID 39405522](https://pubmed.ncbi.nlm.nih.gov/39405522/) | Integration is treated as an organizational/barrier problem, not a technology gap |
| *"Enterprise standardization and convergence of large-volume infusion pump drug libraries,"* Am J Health Syst Pharm, 2023, [PMID 37527506](https://pubmed.ncbi.nlm.nih.gov/37527506/) | Drug-library governance across an enterprise is the operational bottleneck |
| *"Data-based program management of system-wide IV smart pump integration,"* Am J Health Syst Pharm, 2024, [PMID 37804239](https://pubmed.ncbi.nlm.nih.gov/37804239/) | Integration programs are managed with pump data, not learned models |
| *"Pharmacy-driven performance improvement initiative to increase compliance with intravenous smart pump drug error reduction systems…,"* Am J Health Syst Pharm, 2024, [PMID 38069664](https://pubmed.ncbi.nlm.nih.gov/38069664/) | The lever pulled to improve safety is a pharmacy process initiative |
| *"Benefits and risks of using smart pumps to reduce medication error rates: a systematic review,"* Drug Saf, 2014, [PMID 25294653](https://pubmed.ncbi.nlm.nih.gov/25294653/) | The foundational smart-pump evidence review |
| *"Investigating multiple sources of data for smart infusion pump and electronic health record interoperability,"* Am J Health Syst Pharm, 2020, [PMID 32462189](https://pubmed.ncbi.nlm.nih.gov/32462189/) | Data-source reconciliation is the practical interoperability challenge |

**Grade: SUBSTANTIATED** (all indexed in PubMed; titles/journals/years retrieved via esummary 2026-08-05).

### B.5 The keystroke study, and why interoperability forces DERS use

Biltoft J, Finneman L, **Am J Health Syst Pharm** 2018;75(14):1064–1068, [PMID 29987060](https://pubmed.ncbi.nlm.nih.gov/29987060/) — 286-bed hospital:

- **Mean keystrokes to program an infusion: 15 → 2 (86% decrease).**
- Interoperability **forces DERS use, so 100% of prepopulated infusions are protected** by the drug library.
- Incidental finding: $370,000 incremental revenue from improved outpatient charge capture.

That middle point is the mechanism behind B.3's 96.1% DERS compliance. Interoperability does not persuade nurses to use the drug library — it removes the option of bypassing it. **Grade: SUBSTANTIATED.**

Alert-burden corroboration across multiple systems: Blake JWC, *"Infusion Pump Interoperability and Resulting Alert Reduction: Multisystem Findings,"* **J Nurs Care Qual** 2026;41(3):283–292, [PMID 41928352](https://pubmed.ncbi.nlm.nih.gov/41928352/) — 22 clinical sites across 5 health systems plus a control, spanning Epic and Cerner. Integration significantly reduced programming alerts, edits, overrides, and potentially averted overdose events. **Notably, titrated medications showed no change** — the benefit concentrates in intermittently dosed medications. *(Author disclosure: advisor/consultant to ICU Medical.)* **Grade: SUBSTANTIATED.**

### B.6 The DERS ceiling — why the incumbent technology has run out of room

The governing field document is **ISMP, *Guidelines for Optimizing Safe Implementation and Use of Smart Infusion Pumps*, 2020 edition** (38 pp.) — [ISMP PDF](https://www.ismp.org/system/files/resources/2020-10/ISMP176C-Smart%20Infusion%20Pumps-100620.pdf). It supersedes the 2009 original and was built from the second National Smart Infusion Pump Summit (May 2018), funded by Baxter, B. Braun, BD, ICU Medical, and Ivenix. **No newer edition exists** (verified as a negative: ECRI's 2024-03-21 mirror is byte-size-identical to the 2020 ismp.org file). ISMP became an ECRI affiliate effective 2020-01-02.

> ⚠️ Borrelli et al. 2025 (B.2) miscites these guidelines as "2018." The correct edition year is **2020**. Do not propagate the error.

**The compliance target, verbatim (§1.6):** _"Monitor smart infusion pump compliance rates (**target goal of 95% or greater**)… **Bypassing DERS remains a key risk point** in the use of this technology."_ The ≥95% target recurs five times, including for auto-programming compliance (§5.4, §5.5).

**What compliance actually is:**

| Source | Compliance | Override / bypass |
|---|---|---|
| ISMP national survey, *Med Safety Alert!* 2018;23(7) | Only **48%** of respondents reported >90% library compliance | **Up to 45% of nurses** program plain IV solutions outside the library >50% of the time; **58% of staff-level practitioners did not know their own compliance rate** |
| Melton et al., *BMC Med Inform Decis Mak* 2019;19:213 | **87%** (264,470 neonatal infusions) | **73.6% of alerts overridden**; 17% of infusions generated the majority of alerts |
| Schnock et al., *BMJ Qual Saf* 2017;26(2):131–140, [PMID 26908900](https://pubmed.ncbi.nlm.nih.gov/26908900/) | — | **60% of 1,164 observed infusions across 10 hospitals had ≥1 error despite smart pumps** |
| Sproul & Newman, *Can J Hosp Pharm* 2023;76(3):185–195 | **30% of Canadian hospitals do not monitor compliance at all** | **68% allocate <1 pharmacist FTE** to library maintenance; 28% allocate zero |

**Real-world DERS compliance sits roughly 74–90% against a 95% target. Grade: INFERRED** — no national *measured* (as opposed to self-reported) rate exists; do not state one as fact.

**ISMP's own statement of the structural limit (p. 4), verbatim:**

> "…most smart pumps are not linked to available **barcode medication administration (BCMA)** systems and are **not assigned to a specific patient**… Thus, **smart infusion pumps cannot prevent wrong patient errors, incorrect DERS library selections (as well as infusion line mix-ups), and they are not designed to overcome frequent alert overrides or poor compliance**… Presently, **most smart infusion pumps cannot record the reason for each override**."

> "**Even when organizations optimize the use of smart infusion pump technology, safety gaps still exist.** Most of these gaps stem from the smart pump **operating in isolation** of other electronic systems."

Corroborated by Ohashi K, Dalleur O, Dykes PC, Bates DW, **Drug Saf** 2014;37(12):1011–1020, [PMID 25294653](https://pubmed.ncbi.nlm.nih.gov/25294653/): *"smart pumps reduce but do not eliminate programming errors… soft limits were still not as effective as hard limits because of high override rates."*

ISMP's diagnosis — *"operating in isolation of other electronic systems"* — prescribes **integration**, not intelligence. **Grade: SUBSTANTIATED** (verbatim quotation from the cited ISMP PDF).

**PCA-specific, and directly relevant to this program:** Schein JR et al., **Drug Saf** 2009;32(7):549–559, [PMID 19530742](https://pubmed.ncbi.nlm.nih.gov/19530742/) — MAUDE analysis of IV PCA events: **6.5% were operator error, and 81% of those were pump misprogramming, roughly half associated with harm.** By contrast, 76.4% of events were device malfunction but only 0.5% caused harm. **For PCA specifically, the harm lives in misprogramming — which is exactly what auto-programming eliminates.** **Grade: SUBSTANTIATED.**

### B.7 ECRI Top 10 Health Technology Hazards, 2020–2026

| Year | Rank | Hazard title | Theme |
|---|---:|---|---|
| 2020 | 6 | "Alarm, alert, and notification overload…" | Alarms |
| 2020 | 9 | "Medication timing errors in EHRs…" | EHR / med delivery |
| 2021 | 2 | "Fatal Medication Errors Can Result When Drug Entry Fields Populate after Only a Few Letters" | EHR / CPOE |
| 2021 | 8 | "Artificial Intelligence Applications for Diagnostic Imaging May Misrepresent Certain Patient Populations" | **AI** |
| **2022** | **3** | **"Damaged Infusion Pumps Can Cause Medication Errors"** | **Infusion pumps** |
| **2022** | **6** | **"Failure to Adhere to Syringe Pump Best Practices Can Lead to Dangerous Medication Delivery Errors"** | **Infusion pumps** |
| 2022 | 7 | "AI-Based Reconstruction Can Distort Images, Threatening Diagnostic Outcomes" | **AI** |
| 2022 | 10 | "Wi-Fi Dropouts and Dead Zones Can Lead to Patient Care Delays, Injuries, and Deaths" | Connectivity |
| 2023 | 6 | "Inflatable Pressure Infusers can deliver fatal air emboli from IV solution bags" | IV delivery |
| 2023 | 9 | "Overuse of Cardiac Telemetry…" | Alarms |
| 2024 | 5 | "Insufficient Governance of AI Used in Medical Technologies Risks Inappropriate Care Decisions" | **AI** |
| **2024** | **8** | **"Infusion Pump Damage Remains a Medication Safety Concern"** | **Infusion pumps** |
| **2025** | **1** | **"Risks with AI-Enabled Health Technologies"** | **AI** |
| 2025 | 6 | "Dangerously Low Default Alarm Limits on Anesthesia Units" | Alarms |
| **2025** | **8** | **"Infection Risks and Tripping Hazards from Poorly Managed Infusion Lines"** | **Infusion** |
| **2025** | **10** | **"Incomplete Investigations of Infusion System Incidents"** | **Infusion pumps** |
| **2026** | **1** | **"Misuse of AI chatbots in healthcare"** | **AI** |
| 2026 | 2 | "Unpreparedness for a 'digital darkness' event…" | EHR availability |
| **2026** | **5** | **"Misconnections of syringes or tubing to patient lines…"** | **IV delivery** |
| **2026** | **6** | **"Underutilizing medication safety technologies in perioperative settings"** — ECRI's body text names "barcode medication administration systems, **smart infusion pumps**, and automated dispensing cabinets" | **Smart pumps** |
| 2026 | 9 | "Health technology implementations that prompt unsafe clinical workflows" | Interoperability (implied) |

Sources: ECRI news posts for [2020](https://home.ecri.org/blogs/ecri-news/misuse-of-surgical-staplers-tops-ecri-institutes-2020-technology-hazards-list), [2022](https://home.ecri.org/blogs/ecri-news/ecri-names-cybersecurity-attacks-the-top-health-technology-hazard-for-2022), [2023](https://home.ecri.org/blogs/ecri-news/gaps-in-recalls-of-home-use-medical-devices-top-ecris-hazards-list-for-2023), [2024](https://home.ecri.org/blogs/ecri-news/challenges-with-home-use-medical-devices-for-patients-and-caregivers-tops-ecris-2024-health-tech-hazards), [2025](https://home.ecri.org/blogs/ecri-news/artificial-intelligence-tops-2025-health-technology-hazards-list), [2026](https://home.ecri.org/blogs/ecri-news/misuse-of-ai-chatbots-tops-annual-list-of-health-technology-hazards).

**Three patterns worth carrying forward:**

1. **Infusion/IV appears in 5 of 7 editions, and the framing has migrated** — from *"the pump is broken"* (2022, 2024) to *"the system around the pump is unmanaged"* (2025 incident investigations; 2026 **under-use of smart pumps**). ECRI 2026 #6 is effectively an *under-adoption* hazard, which is the same shape as the 13% interoperability gap in B.0.
2. **AI appears in 5 of 7 editions and is #1 in both 2025 and 2026 — but always as a hazard, never as a solution.** ECRI has never listed an AI capability as a remedy for anything.
3. **Alarm hazards appear in only 3 of 7 editions and never top-ranked.** The common industry claim that alarm fatigue is perennially near the top of ECRI's list was true in the 2010s and **is not true for 2020–2026**.

**Grade: SUBSTANTIATED** for the entries cited to ECRI news posts. **SUBSTANTIATED-INDIRECT** for the 2026 #9 long-form scoping text (extracted from indexed Executive Brief PDF text; the PDF's subset-encoded fonts defeated full extraction). Long-form titles for 2020–2023 and 2025 were not cross-checked against their Executive Briefs.

### B.8 Standards — and a gap that matters for filing

| Designation | Title | FDA status |
|---|---|---|
| **AAMI TIR101:2021** | *Fluid delivery performance testing for infusion pumps* — covers syringe, container, volumetric pumps, incl. **enteral, PCA, and epidural** modes | **FDA-recognized: 6-482, entered 2022-05-30, extent Complete** |
| ANSI/AAMI ID26:2004 (R2013) | *Particular requirements for the safety of infusion pumps and controllers* | **Withdrawn**; not FDA-recognized |
| IEC 60601-2-24 (Ed. 2, 2012) | Particular requirements for infusion pumps | Active internationally; **NOT FDA-recognized** |

> **Filing-strategy finding.** FDA recognizes 50 entries across IEC 60601-2-1 → 60601-2-68, but **60601-2-24 is absent** — it sits in a gap between recognized -23 and -25. With ID26 withdrawn, **there is currently no FDA-recognized particular safety standard for infusion pumps.** The FDA-recognized infusion-pump document is TIR101:2021, which covers fluid-delivery performance testing, not general safety. A PP3500 standards matrix that lists IEC 60601-2-24 as an FDA-recognized consensus standard would be wrong.

**Interoperability standards — UL 2800 family.** Editions: ANSI/AAMI/UL 2800-1:2019 (*Standard for Safety for Medical Device Interoperability*) → **2800-1:2022** (*"for Safety" dropped from the title*, 2022-06-10) → **Ed. 3, 2026-01-29**. Sub-parts, all 2022: **2800-1-1** (risk concerns), **2800-1-2** (development life cycle), **2800-1-3** (integration life cycle).

**All four 2022 parts are FDA-recognized** (CDRH standards database, last updated 2026-05-25):

| Recognition # | Designation | Entered | Extent |
|---|---|---|---|
| 13-121 | ANSI/AAMI/UL 2800-1:2022 | 2022-12-19 | Complete |
| 13-125 | ANSI/AAMI/UL 2800-1-1:2022 | 2022-12-19 | Complete |
| 13-126 | ANSI/AAMI/UL 2800-1-2:2022 | 2022-12-19 | Complete |
| 13-127 | ANSI/AAMI/UL 2800-1-3:2022 | 2022-12-19 | Complete |

> ⚠️ **Edition 3 (January 2026) is not yet FDA-recognized. Cite the 2022 editions in a submission.** (INFERRED from the verified database state.)

**Two premise corrections worth propagating into the standards matrix:**

- **ASTM F2761 (ICE) has moved.** The ASTM F29 portfolio transferred to AAMI; F2761 was republished as **ANSI/AAMI 2700-1:2019** (FDA-recognized **13-120**, entered 2021-12-20), joined by **ANSI/AAMI 2700-2-1:2022** (ICE Part 2-1, forensic data logging — FDA-recognized **13-130**, entered 2023-10-09). **Cite 2700-1, not F2761.**
- **AAMI TIR69 is not an interoperability standard.** TIR69:2017(R2020) is *"Risk management of radio-frequency wireless coexistence for medical devices and systems"* (FDA-recognized **19-22**, entered 2017-08-21) — relevant to a connected pump, but an EMC/wireless document.
- **IEC 80001 family:** nine FDA-recognized entries (13-38, 13-40, 13-42, 13-44, 13-63, 13-70, 13-82, 13-102, 13-103), all extent Complete. Note FDA still recognizes **80001-1 Edition 1.0 (2010)**, not the 2021 revision.

**FDA interoperability guidance:** *Design Considerations and Pre-market Submission Recommendations for Interoperable Medical Devices* — **Final, September 2017**, docket FDA-2015-D-4852, CDRH ([FDA guidance page](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/design-considerations-and-pre-market-submission-recommendations-interoperable-medical-devices)).

**AAMI Foundation National Coalition for Infusion Therapy Safety:** launched March 2015 with a three-year scope, **wound down in 2018**. Its four focus areas included *reducing non-actionable pump alarms* and *smart-pump drug-library compliance*. Output includes *Managing Smart Pump Alarms: Reducing Alarm Fatigue* (2018) and the 2012 *Safety Innovations* series. The live aami.org anthology URL now 404s; recoverable via [web.archive.org](https://web.archive.org/web/20230806230107/https://www.aami.org/docs/default-source/foundation/infusion/aami-infusion-anthology-10-8-20.pdf). **Grade: SUBSTANTIATED**, with the caveat that this body no longer produces new work.

### B.9 Is interoperability a bigger practical differentiator than AI right now?

**Yes — and on this evidence it is not close.**

The supporting facts, each independently sourced above:

1. **Cleared products.** Interoperability: all five major vendors (A.5, B.1). ML-based prediction: **zero pump products** (A.1).
2. **Peer-reviewed effect sizes.** Interoperability: 15.4–90.5% error reduction across three studies (B.2), 30–50% alert reduction (B.3), 86% keystroke reduction (B.5). ML-based pump prediction: **zero clinical outcome studies** (A.9).
3. **Standards and guidance.** Interoperability: an FDA-recognized standard family (UL 2800 series, 2700-1) and a final FDA guidance (2017) (B.8). AI in pumps: no standard, no pump-specific guidance.
4. **Field guidance.** ISMP's 2020 guidelines devote an entire section (§5, 20 statements) to interoperability with an explicit ≥95% target, and contain **no AI/ML requirements** (B.6).
5. **The neutral referee.** ECRI names AI as the **#1 hazard** two years running and has never named an AI pump capability at all — while flagging **under-use of smart pumps** as a 2026 hazard (B.7).
6. **Addressable headroom.** ~87% smart-pump saturation against ~13% interoperability adoption (B.0), and only **53.4% auto-programming compliance even after integration** (B.3).

**Grade: OPINION (labelled), resting on SUBSTANTIATED components.** No single source states "interoperability beats AI as a differentiator" — this is analyst judgment. Every one of facts (1)–(6) is independently substantiated above.

**The counter-argument, stated fairly.** Regulatory and clinical attention *is* moving toward AI (ECRI #1 twice; FDA's PCCP framework maturing), and the DERS ceiling is real — Schnock found **60% of infusions still carried ≥1 error even with smart pumps** (B.6), so the field genuinely needs something beyond rule-based limits. A vendor with a five-to-seven-year horizon may reasonably invest in ML-based dose-anomaly detection. But that is a **future bet, not a 2026 differentiator**, and treating it as the latter is precisely the error the project's unsourced claims make.

---

## C. FDA pathway reality check

### C.1 The PCCP guidance — exact identity

**Title:** *Marketing Submission Recommendations for a Predetermined Change Control Plan for Artificial Intelligence-Enabled Device Software Functions* — Guidance for Industry and Food and Drug Administration Staff.

**Dates (both matter):** the PDF cover states **"Document issued on August 18, 2025. Document originally issued on December 4, 2024."** The December 2024 date is the original finalization; **August 18, 2025 is the currently operative version**, and a strategy document citing only "December 2024" is citing a superseded issue of the same guidance.

**Docket:** FDA-2022-D-2628. **Issuing offices:** CDRH, CBER, CDER, and the Office of Combination Products.

**URLs:** [guidance landing page](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/marketing-submission-recommendations-predetermined-change-control-plan-artificial-intelligence) · [full PDF](https://www.fda.gov/media/166704/download) (49 pages). Retrieved 2026-08-05.

**Grade: SUBSTANTIATED.**

### C.2 The separate general-device PCCP guidance is still a DRAFT

*Predetermined Change Control Plans for Medical Devices* — **Draft** Guidance for Industry and FDA Staff, **August 2024**, Docket **FDA-2024-D-2338**, page marked "Content current as of: 08/22/2024" and labelled **"Draft — Not for implementation."** [Landing page](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/predetermined-change-control-plans-medical-devices), retrieved 2026-08-05.

**This is a real planning constraint.** A PP3500 PCCP covering *non-AI* device modifications (mechanical, firmware, hardware, labeling) rests on a draft guidance that FDA explicitly says is not for implementation. Only the **AI-enabled software function** PCCP route has final guidance behind it.

**Grade: SUBSTANTIATED.**

### C.3 Can a PCCP expand a device's intended use? **No.**

Verbatim from the guidance (§ IX, pp. 22–23):

> "Modifications included in a PCCP **must maintain the device within the device's intended use**,[91] and as applicable, **must allow the device to remain substantially equivalent to the predicate device**.[92] In general, FDA believes that modifications included in a PCCP **should also maintain the device within the device's indications for use**.[93]"

Footnote 91 cites **sections 515C(a)(2) and 515C(b)(2) of the FD&C Act**; footnote 92 cites **section 515C(b)(2)(B)**. The intended-use limit is therefore **statutory, not merely a guidance preference** — FDA cannot waive it and a Q-Sub cannot negotiate around it.

Three further constraints from the same passage, each of which changes how a PCCP should be scoped:

1. **"Must" vs. "should."** Intended use is a hard statutory boundary (`must`). Indications for use is softer (`should`, `in general`) — FDA says most IFU modifications "would be difficult for FDA to assess prospectively," but leaves a **narrow carve-out**: _"there may be certain modifications to the indications for use (e.g., certain changes in the indications for use to specify use of the device with an additional device or component) that may be appropriate for inclusion in a PCCP."_ FDA "highly encourages" discussing these through the Q-Submission Program.
2. **Substantial equivalence must survive every modification.** For a 510(k)-routed PCCP, each pre-specified change must leave the device substantially equivalent to the predicate. With the newest same-code PCA predicate dating to 2017 (A.7), the SE anchor is a nine-year-old device.
3. **Where in the review the PCCP is considered.** The guidance states FDA "anticipates that the PCCP will primarily be reviewed **after** FDA finds that the intended use of the subject device and the predicate device are the same, to help determine whether the devices have different technological characteristics that do not raise different questions of safety and effectiveness." The PCCP is evaluated downstream of the intended-use determination — it cannot be used to establish or stretch it.

**Grade: SUBSTANTIATED** (verbatim quotation from the cited PDF, with statutory citations reproduced from the guidance's own footnotes).

### C.4 The Appendix B example that lands directly on the PP3500 thesis

Appendix B of the guidance walks through hypothetical AI-DSF scenarios. One is a **patient-monitoring device that detects the onset of physiologic instability** from vital-sign inputs and raises an alarm — structurally the closest analogue in the guidance to the PP3500's predictive-monitoring ambition.

The pre-specified modification in that example is a re-training to **reduce the false-alarm rate while holding sensitivity** within a non-inferiority margin. That change, executed per the Modification Protocol, needs **no new submission**.

Then Modification Scenario 2 (quoted from the guidance):

> "…the manufacturer also noticed that the modified AI model maintained the same sensitivity and **can now also predict physiologic instability in advance of its onset**, which the previous version of the AI model could not do. The manufacturer would like to update the device's indications for use to reflect this additional performance claim… **The methods used for analysis, performance, and statistics were not specified in the PCCP for predicting a future state.** Because this modification that was not included in the PCCP could significantly affect the safety or effectiveness of the device, **a new marketing submission would be required.**"

This is the single most directly applicable passage in the guidance for this program. FDA's own worked example says that **moving from detection to advance prediction is a claim change requiring a new submission unless the predictive methodology was pre-specified in the PCCP from the start.** A PP3500 PCCP that pre-specifies only accuracy improvements to a detection function will **not** cover a later pivot to "15–30 minute early warning."

**Grade: SUBSTANTIATED** (verbatim from the cited PDF). **Application to PP3500 is INFERRED** — the guidance example is explicitly hypothetical and is not about an infusion pump; the structural parallel is the analyst's mapping.

### C.5 "96% of AI/ML devices cleared via 510(k)" — verified, and it is 96.2%

Computed directly from the submission-number prefix of all 1,524 rows on the FDA AI list:

| Pathway | Devices | Share |
|---|---:|---:|
| 510(k) (`K…`) | 1,466 | **96.2%** |
| De Novo (`DEN…`) | 39 | 2.6% |
| PMA (`P…`) | 19 | 1.2% |

**Grade: SUBSTANTIATED.** The project's "96%" is accurate. Worth noting the tail: De Novo is a real and non-trivial route for genuinely novel AI functions with no predicate — and given A.7's nine-year predicate gap for PCA pumps, De Novo deserves more consideration in the pathway analysis than a 2.6% headline share suggests.

### C.6 "FDA has authorized over 1,000 AI-enabled devices" — verified and now conservative

**1,524** devices as of the list current 2026-06-16. The claim is true and understated.

**Grade: SUBSTANTIATED.**

### C.7 "Typical clearance timelines of 3–6 months" — the number survives, the planning assumption does not

This is the claim most worth unpacking carefully, because the headline number is roughly right for the wrong reason.

**FDA's own two clocks.** FDA reports 510(k) performance against two different measures, and they diverge sharply.

Source: FDA, **MDUFA V FY2025 Performance Report**, [PDF](https://www.fda.gov/media/191127/download?attachment), data as of 2025-09-30, retrieved 2026-08-05.

| Measure | What it counts | Goal | Actual |
|---|---|---|---|
| **510(k) Decision** (Table 1, Table 4) | **FDA days** only — the clock stops while the applicant answers an Additional Information request | 90 FDA days at 95% | **99% met** in FY2024 (n = 3,131) — **MET** |
| **510(k) Total Time to Decision** (Table 5) — a *shared outcome* goal | **Calendar days**, submission to decision, including applicant hold time | 128 (FY23) → 124 (FY24) → 112 (FY25) | **127 days FY23 — MET**; **139 days FY24 — MISSED** |

The gap between "99% of 510(k)s decided within 90 FDA days" and "average 139 calendar days to decision" **is applicant hold time.** FDA's review clock is not the sponsor's calendar.

**What that means for the 3–6 month claim.** 139 calendar days is 4.6 months. So the *average* 510(k) does land inside a 3–6 month window — the claim is not fabricated. Three qualifications matter more than the headline:

1. **The trend is the wrong direction.** 127 days (goal met) → 139 days (goal missed, against a *tighter* goal of 124). FY2025's goal drops again to 112 days.
2. **This is submission-to-decision only.** It excludes Q-Sub interaction (FDA's Pre-Submission written-feedback goal ran 4,198 submissions in FY2025 alone), RTA screening cycles, and all sponsor preparation time. A program plan built on "3–6 months to clearance" that starts the clock at submission is missing the front half of the timeline.
3. **AI-enabled devices are slower than the average device.**

**Original computation — AI-enabled 510(k) review times.** Every `K…` submission on the FDA AI list with a decision from 2023 onward (**n = 862**) was joined to openFDA `device/510k` on `date_received` → `decision_date`:

| Statistic | Days | Months |
|---|---:|---:|
| Median | **142** | 4.7 |
| Mean | 154.5 | 5.1 |
| 25th percentile | 95 | 3.1 |
| 75th percentile | 211 | 6.9 |
| 90th percentile | 266 | 8.7 |
| Maximum | 626 | 20.6 |

Distribution against the claimed window:

| Bucket | Devices | Share |
|---|---:|---:|
| ≤ 90 days (< 3 months) | 201 | 23.3% |
| 91–180 days (3–6 months) | 363 | 42.1% |
| 181–270 days (6–9 months) | 251 | 29.1% |
| 271–365 days (9–12 months) | 31 | 3.6% |
| > 365 days (> 12 months) | 16 | 1.9% |

**Roughly one in three AI-enabled 510(k)s (34.6%) took longer than six months** from receipt to decision, and the 90th percentile is 8.7 months.

**AI vs. non-AI comparison.** For 510(k)s decided 2024-01-01 → 2025-12-31 (openFDA, ~6,350-record sample — see Method limit 4): **non-AI median 126 days; AI-list median 146 days.** AI-enabled submissions run about **20 days longer at the median**.

**Grade: the "3–6 months" claim is PARTIALLY SUBSTANTIATED** — the median AI-enabled 510(k) (142 days / 4.7 months) does sit in the band, but it is an *average outcome*, not a *plannable commitment*: a third of comparable devices exceed it, the trend is worsening, and the figure excludes everything before submission. **The underlying review-time data is SUBSTANTIATED** (MDUFA report quoted; openFDA computation reproducible).

### C.8 Section 524B cybersecurity requirements

See **Section D.3** — the statutory premarket content requirements for a "cyber device" are treated there, alongside the vulnerability history that motivates them.

---

## D. Cybersecurity gate

### D.1 Why cybersecurity belongs in a competitive analysis at all

PP3500 is a connected device — connectivity adapter, cloud suite, telemetry, EHR integration. Since **March 29, 2023**, that makes cybersecurity a **statutory premarket admissibility condition** under FD&C Act § 524B, not a design-quality nicety. Since roughly 2022 it has also become a **contractual purchasing condition**, through model contract language co-authored by a national group purchasing organization (D.5).

In a market where no competitor holds an AI clearance (Section A) and every competitor holds interoperability clearances (Section B), cybersecurity is one of the few axes on which connected pumps genuinely differentiate — and it is the axis where a deficiency **blocks a sale outright** rather than losing a feature comparison.

**Grade: OPINION (labelled)** for the framing; the underlying statutory and contractual facts below are SUBSTANTIATED.

### D.2 The vulnerability track record — every major pump vendor has one

Infusion pumps are among the most advisory-burdened device classes in the CISA ICS-Medical corpus.

| Advisory | Date | Vendor / Product | Peak CVSS |
|---|---|---|---:|
| [ICSA-15-125-01A](https://www.cisa.gov/news-events/ics-advisories/icsa-15-125-01a) | 2015-05-05 (Upd. A 2018-08-23) | Hospira **LifeCare PCA** v5.0 and prior | **v2 10.0** (CVE-2015-3459 — unauthenticated root Telnet) |
| [ICSA-15-161-01](https://www.cisa.gov/news-events/ics-advisories/icsa-15-161-01) | Jun 2015 | Hospira **Plum A+ / A+3 / Symbiq** | **v2 10.0** (CVE-2015-3954, -3953) |
| [ICSMA-17-250-02A](https://www.cisa.gov/news-events/ics-medical-advisories/icsma-17-250-02a) | 2017-09-07 (Upd. A 2017-12-12) | Smiths Medical **Medfusion 4000** | **v3 9.8** (CVE-2017-12725) |
| [ICSMA-19-164-01](https://www.cisa.gov/news-events/ics-medical-advisories/icsma-19-164-01) | 2019-06-14 | BD **Alaris Gateway Workstation** | **v3 10.0** (CVE-2019-10959 — unsigned firmware upload) |
| [ICSA-19-211-01](https://www.cisa.gov/news-events/ics-advisories/icsa-19-211-01) | 2019-07-30 (Upd. A 2020-10-05) | Wind River VxWorks/IPnet — **URGENT/11** (CVE-2019-12255…12265) | **v3 9.8** |
| [ICSA-20-168-01](https://www.cisa.gov/news-events/ics-advisories/icsa-20-168-01) | 2020-06-16 | Treck TCP/IP — **Ripple20** | **v3 10.0** |
| [ICSMA-20-170-04](https://www.cisa.gov/news-events/ics-medical-advisories/icsma-20-170-04) | 2020-06-23 (Upd. B 2022-08-11) | Baxter **Sigma Spectrum** + Wireless Battery Module | v3 8.6 (hard-coded Telnet creds) |
| [ICSMA-20-317-01](https://www.cisa.gov/news-events/ics-medical-advisories/icsma-20-317-01) | Nov 2020 (rev. 2021-03-15) | BD **Alaris 8015 PC Unit + Systems Manager** | v3 6.5 (CVE-2020-25165) |
| [ICSMA-21-294-01](https://www.cisa.gov/news-events/ics-medical-advisories/icsma-21-294-01) | 2021-10-21 (Upd. A 2022-10-20) | B. Braun **Infusomat / Perfusor Space** | **v3 9.0** (CVE-2021-33885) |
| [ICSMA-21-355-01](https://www.cisa.gov/news-events/ics-medical-advisories/icsma-21-355-01) | 2021-12-21 | Fresenius Kabi **Agilia Connect** (12 vuln classes) | v3 7.5 |
| [ICSA-22-067-01](https://www.cisa.gov/news-events/ics-advisories/icsa-22-067-01) | 2022-03-08 | PTC Axeda — **Access:7** | **v3 9.8** |
| [ICSMA-22-251-01](https://www.cisa.gov/news-events/ics-medical-advisories/icsma-22-251-01) | 2022-09-29 | Baxter **Sigma / Spectrum IQ** WBM | v3 7.5 |
| [ICSMA-23-047-01](https://www.cisa.gov/news-events/ics-medical-advisories/icsma-23-047-01) | 2023-02-16 | BD **Alaris Infusion Central** (non-US) | v3 7.3 |
| [ICSMA-23-194-01](https://www.cisa.gov/news-events/ics-medical-advisories/icsma-23-194-01) | Jul 2023 (Upd. A 2023-10-26) | BD **Alaris System w/ Guardrails Suite MX** — 8 vulns | v3 8.2 |

**Grade: SUBSTANTIATED** (each row read from the cited CISA advisory page, 2026-08-05).

**The landmark, and the exact wording is the point.** FDA safety communication, **2015-07-31**, *Cybersecurity Vulnerabilities of Hospira Symbiq Infusion System* ([archived](https://web.archive.org/web/20160103184616/http://www.fda.gov/MedicalDevices/Safety/AlertsandNotices/ucm456815.htm)), verbatim:

> "The FDA is alerting users of the Hospira Symbiq Infusion System to cybersecurity vulnerabilities with this infusion pump. **We strongly encourage that health care facilities transition to alternative infusion systems, and discontinue use of these pumps.**"

FDA stated it was aware of **no** patient adverse event and **no** unauthorized access. This is the first time FDA told providers to stop using a marketed device **for a cybersecurity reason alone** — the vulnerability itself, not harm, drove the market action. That precedent is what converts cybersecurity from a compliance chore into a commercial risk. A companion communication for **Hospira LifeCare PCA3/PCA5** was posted **2015-05-13** ([archived](https://web.archive.org/web/20160101000000/http://www.fda.gov/Safety/MedWatch/SafetyInformation/SafetyAlertsforHumanMedicalProducts/ucm446828.htm)). **Grade: SUBSTANTIATED (verbatim).**

**Field exposure, measured.** Palo Alto **Unit 42** (2022-03-02) scanned **200,000+ infusion pumps** on hospital networks: **75% had known security gaps**; **52.11%** were exposed to CVE-2019-12255 and CVE-2019-12264 (both URGENT/11); a further 39.54% carried CVE-2020-25165. [unit42.paloaltonetworks.com](https://unit42.paloaltonetworks.com/infusion-pump-vulnerabilities/). **Grade: SUBSTANTIATED** (vendor research, method described).

**The supply-chain lesson.** Two of the three worst pump exposures — URGENT/11 and Ripple20 — came from a **third-party TCP/IP stack**, not from pump code. That is exactly the exposure an SBOM exists to surface, which is why SBOM moved from best practice to statute (D.4, D.6).

### D.3 BD Alaris — the market-pause case study, stated accurately

| K-number | Decision | Device |
|---|---|---|
| K133532 | **2014-08-21** | Alaris System with Guardrails Suite MX |
| **K211218** | **2023-07-21** | **BD Alaris System with Guardrails Suite MX v12.1.2** |
| K243855 | 2025-04-25 | BD Alaris Infusion System with Guardrails Suite MX |

The sequence: Class I recall (Feb/Mar 2020, 55 reported injuries and 1 death) → multi-year US market pause → **nearly nine years between system clearances** → July 2023 clearance of a remediated system carrying cybersecurity updates, with the Guardrails Suite MX advisory (ICSMA-23-194-01) published the same month.

> **Two corrections that must travel with this story.** (1) BD's market pause was driven **principally by software, hardware, and user-related recalls — not cybersecurity**; cyber was one remediation workstream, not the cause. Anyone telling this as "cybersecurity killed a product line" is overreaching. The defensible claim is narrower and still strong: *a major pump platform can be off the US market for ~3 years, and its re-entry submission had to carry a cybersecurity story.* (2) The **2025 BD Alaris Class I recall is not a cybersecurity event** — it is an infusion-set flow-accuracy performance issue ([FDA alert](https://www.fda.gov/medical-devices/medical-device-recalls-and-early-alerts/update-alert-infusion-set-performance-issue-bd)). Do not cite it as cyber evidence.

**Grade: SUBSTANTIATED** for the clearance dates (openFDA); **the pause narrative is PARTIALLY SUBSTANTIATED** with the causation correction above; **the "2025 recall is cyber" framing is REFUTED.**

### D.4 Section 524B — what a connected pump must now include

**21 U.S.C. § 360n-2**, added by **Pub. L. 117-328, div. FF, tit. III, § 3305(a)**, Dec. 29, 2022.

> **Note on attribution:** § 524B was **not** "added by the PATCH Act" in statutory terms. The source credit reads § 3305(a) of P.L. 117-328. "PATCH Act" is journalistic shorthand appearing nowhere in the statute — **cite § 3305.** **Grade: SUBSTANTIATED.**

**Subsection (b) — required submission content, verbatim:**

> "The sponsor of an application or submission described in subsection (a) shall—
> (1) submit to the Secretary **a plan to monitor, identify, and address, as appropriate, in a reasonable time, postmarket cybersecurity vulnerabilities and exploits, including coordinated vulnerability disclosure** and related procedures;
> (2) **design, develop, and maintain processes and procedures** to provide a reasonable assurance that the device and related systems are cybersecure, and **make available postmarket updates and patches** … (A) on a reasonably justified regular cycle, known unacceptable vulnerabilities; and (B) as soon as possible out of cycle, critical vulnerabilities that could cause uncontrolled risks;
> (3) **provide to the Secretary a software bill of materials**, including commercial, open-source, and off-the-shelf software components; and
> (4) comply with such other requirements as the Secretary may require through regulation…"

Subsection (a) scopes this to **510(k), De Novo, PMA, PDP, and HDE**.

**Subsection (c) — "cyber device" definition, verbatim.** A device that "(1) includes software validated, installed, or authorized by the sponsor as a device or in a device; (2) **has the ability to connect to the internet**; and (3) contains any such technological characteristics … that could be vulnerable to cybersecurity threats." All three prongs are **conjunctive**.

**Does a connected PCA pump qualify? Unambiguously yes** — pump firmware plus drug-library software satisfies (1); wireless EHR integration and cloud telemetry satisfy (2); a networked firmware interface satisfies (3).

> **The bar is far lower than most teams assume.** Guidance § VII.B footnote 61, verbatim: *"For example, a device may need to be serviced via a USB connection. While the connection may be brief, the ability to connect is present and the device is therefore considered to have the ability to connect to the internet."* **An air-gapped pump serviced over USB is a cyber device.**

> **Modification trap (§ VII.D).** § 524B applies to **any** submission under those pathways, **including modifications**. Even for changes "unlikely to impact cybersecurity," a § 524B(b)(1) plan **must** be provided if not previously submitted, and an SBOM is still required. **A Special or Abbreviated 510(k) does not exempt you.** This directly constrains any PCCP-adjacent modification strategy.

**Effective dates — both verified:**

| Date | Event |
|---|---|
| 2022-12-29 | Enactment of P.L. 117-328 |
| **2023-03-29** | § 524B effective (90 days post-enactment, § 3305(d)) |
| **2023-10-01** | End of FDA's refuse-to-accept forbearance |

Federal Register, **88 FR 19148** (2023-03-30, Docket FDA-2023-D-1030), verbatim: *"FDA generally intends not to issue RTA decisions for premarket submissions submitted for cyber devices based solely on information required by section 524B … **before October 1, 2023** … **Beginning October 1, 2023** … **FDA may RTA premarket submissions that do not** [contain it]."* Requirements **do not apply retroactively** to submissions filed before 2023-03-29. [govinfo.gov](https://www.govinfo.gov/content/pkg/FR-2023-03-30/html/2023-06646.htm). **Grade: SUBSTANTIATED (verbatim).**

### D.5 The governing guidance — and the version most citations get wrong

| Version | Exact title | Issued | Status |
|---|---|---|---|
| RTA policy | Cybersecurity in Medical Devices: Refuse to Accept Policy for Cyber Devices… | Mar 2023 | Landing page unresolved |
| Final v1 | Cybersecurity in Medical Devices: **Quality System** Considerations and Content of Premarket Submissions | 2023-09-27 | Superseded |
| Draft | **Select Updates for the Premarket Cybersecurity Guidance: Section 524B of the FD&C Act** | **2024-03-13** ([FR 2024-05295](https://www.federalregister.gov/documents/2024/03/13/2024-05295/select-updates-for-the-premarket-cybersecurity-guidance-section-524b-of-the-federal-food-drug-and)) | Finalized as § VII of the current guidance |
| Final v2 | Cybersecurity in Medical Devices: **Quality System** Considerations… | 2025-06-27 | Superseded |
| **Final v3 — CURRENT** | Cybersecurity in Medical Devices: **Quality *Management* System** Considerations and Content of Premarket Submissions | **2026-02-03** | **In force** |

The current guidance was **independently verified twice** in this research — by direct retrieval of the FDA guidance page (title, "February 2026", Docket **FDA-2021-D-1158**, "Content current as of: 02/03/2026") and by the PDF cover, which states verbatim: *"Document issued on February 3, 2026. This document supersedes 'Cybersecurity in Medical Devices: Quality System Considerations and Content of Premarket Submissions,' issued June 27, 2025."* [FDA landing page](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/cybersecurity-medical-devices-quality-management-system-considerations-and-content-premarket) · [PDF](https://www.fda.gov/media/119933/download).

> **Note the retitle:** "Quality System" → "Quality **Management** System," reflecting QMSR alignment (ISO 13485 subclauses replacing 21 CFR 820 references). **A PP3500 submission citing the June 2025 or September 2023 version is citing superseded guidance — a real audit finding.**

**Grade: SUBSTANTIATED** (two independent retrievals).

### D.6 SBOM — the requirement, and a live divergence

**What FDA asks for** (current guidance § V.A.4, verbatim): machine-readable SBOMs consistent with the minimum elements in the **October 2021** NTIA document *"Framing Software Component Transparency: Establishing a Common Software Bill of Materials (SBOM)."* Beyond the NTIA minimum, FDA wants, per component: **software level of support** (actively maintained / no longer maintained / abandoned) and **end-of-support date**. Plus all known vulnerabilities including those in **CISA's Known Exploited Vulnerabilities (KEV) Catalog**, each with a safety/security risk assessment.

> **Two corrections worth propagating.** (1) **FDA does not mandate SPDX or CycloneDX** — the guidance says industry-accepted formats "are **encouraged**." SPDX/CycloneDX/SWID appear in the *NTIA* document, not as an FDA format mandate. This is a widespread and consequential misconception. (2) FDA cites the **October 2021 "Framing Software Component Transparency"** document — **not** the July 2021 "Minimum Elements" report that most people cite. **Grade: SUBSTANTIATED.**

**NTIA 2021 minimum elements** (verbatim, p.3): data fields = Supplier, Component Name, Version, Other Unique Identifiers, Dependency Relationship, Author of SBOM Data, Timestamp; plus Automation Support and Practices/Processes. [NTIA PDF](https://www.ntia.gov/files/ntia/publications/sbom_minimum_elements_report.pdf)

**The divergence.** CISA's **"2026 Minimum Elements for a Software Bill of Materials (SBOM)," published 2026-07-29** (joint CISA/NSA/FBI + 15 international partners) states verbatim that it *"updates and replaces the minimum elements for an SBOM published by … NTIA in 2021."* New elements include **SBOM Author Signature, Data Format Name/Version, Generation Context, Tool Name/Version, SBOM Version, Component Hash Value, Component Hash Algorithm, Component License.** [CISA page](https://www.cisa.gov/resources-tools/resources/2026-minimum-elements-software-bill-materials-sbom)

**FDA's February 2026 guidance anchors to the 2021 NTIA baseline; CISA replaced that baseline five months later.** An SBOM conformant to FDA's cited baseline currently lacks hashes, licenses, author signatures, tool provenance, and generation context. **Building to the 2026 superset satisfies both and is the low-regret position. Grade: dates SUBSTANTIATED; the "build to the superset" recommendation is INFERRED** — FDA has issued no statement on the gap.

### D.7 Hospital security review as a purchasing gate — real, and contractual

The gate exists. It is **contractual, not regulatory**, and it operates in three tiers.

**Tier 1 — Voluntary disclosure: MDS2.** Designation **NEMA/MITA HN 1-2019** (revising HIMSS/NEMA HN 1-2013). Direct parse of the live NEMA worksheet: **21 capability categories, 225 question IDs**, referencing IEC TR 80001-2-2:2012 and ISO 27002:2013.

> ⚠️ The widely repeated **"23 capabilities / 240 questions"** figure is **contradicted by the actual file** — treat as UNVERIFIED. Separately, a live defect: the canonical NEMA MDS2 URL cited by **both** HHS HICP 2023 (fn 99) **and** HSCC JSP 2.0 (fn 44) now returns **HTTP 307 to a commercial domain**. Two flagship sector documents point at a broken reference. **Grade: SUBSTANTIATED** (direct HTTP probe, 2026-08-05).

**Tier 2 — Voluntary best practice with gate language: HICP / HHS 405(d).** *Health Industry Cybersecurity Practices*, **2023 Edition**, HHS 405(d) Program with HSCC, under Cybersecurity Act of 2015 § 405(d). Practice #9 (Network Connected Medical Devices), sub-practice **9.L.B "Procurement and Security Evaluations"** ([Technical Volume 2](https://405d.hhs.gov/Documents/tech-vol2-508.pdf), p.120), verbatim:

> "HDOs should establish a set of cybersecurity requirements during the acquisition of medical devices. These requirements should be **memorialized in your organization's contracting processes** … **incorporated into prospective procurements through vendor requests for information (RFIs) or requests for proposals (RFPs)**."
>
> "Organizations should set policies and procedures that **require procurements of technology and integrations (including medical devices) to undergo security evaluations**…"
>
> "**The HDO should insist on receiving a MDS2.** … also consider requesting an **SBOM and an Enterprise Architecture Diagram** to create a complete **Vendor Assessment Package**."

And — directly on point — **HICP's worked example is an infusion pump**: *"an assessment of **an infusion pump system** would evaluate both the infusion pump and the server to which it connects for the formulary update."* **Grade: SUBSTANTIATED (verbatim).**

**Tier 3 — Contract terms with hard numbers: HSCC MC2.** *Health Industry Cybersecurity — Model Contract Language for Medtech Cybersecurity*, v1 March 2022, **v2 published November 2025** (53 pp). [MC2 v2 PDF](https://healthsectorcouncil.org/wp-content/uploads/2025/11/MC2v2.pdf)

| Clause | Obligation | Number |
|---|---|---|
| **#44** (new in v2) | Supplier **shall provide an SBOM** — OSS, COTS, proprietary, libraries, frameworks, OSes, comm stacks | — |
| **#33** | Notify Customer of exploited or **CISA KEV**-listed vulnerabilities | **3 business days** |
| **#31** | Apply security patches | **30 days** |
| **#35** | Written breach notice after determination | **5 days** |
| **#40** | Products **must not run any OS within 2 years of End of Support** at delivery; upgrade path **at Supplier's expense** | **2 years** |
| **#45** | Advance notice: EoL / End-of-Guaranteed-Support / EoS / end-of-training | **24 / 24 / 36 / 24 months** |
| **#11, #43** | Services documented **in an MDS2**; supplier warrants MDS2 responses "complete and accurate" | — |
| **#46** | Attestation to a secure-development process aligned to e.g. ANSI 62443-4-1 | — |

**Who wrote it is itself the evidence.** MC2 v2 co-chairs: **Michelle Bentley (Mayo Clinic)** and **Jason Ferri (Premier — a national GPO)**, with contributors from Cleveland Clinic, St. Luke's University Health Network, Health-ISAC, Medtronic, GE Healthcare, Spacelabs, Accuray, and Nevro. The v1 task group convened February 2020 as a cross-sector group of **~50 HDOs, manufacturers, security specialists, and GPOs**, producing what MC2 itself calls *"in effect, a **pre-negotiated contract**"* (~1,500 downloads, 98 feedback comments). **A GPO co-chairing the model medical-device purchase contract is the strongest structural signal in this research.** **Grade: SUBSTANTIATED (verbatim).**

**Supporting frameworks:** HSCC **Joint Security Plan** v1 Jan 2019, **JSP 2.0 March 2024** — explicitly *"not a regulatory document, nor is it a standard"*; § F.5 specifies the buyer-facing deliverable set (**SBOM, architecture/design docs, security summary report, MDS2, IFU, security whitepapers**). **NIST SP 1800-8**, *Securing Wireless Infusion Pumps in Healthcare Delivery Organizations* (NCCoE, **August 2018**, 375 pp) has a dedicated **§ 6.1 Procurement** and warns verbatim: *"**Too often, the Information Security team is not brought in until after contracts have been signed.**"* It cites **Mayo Clinic's 2017 "Vendor Deliverables to Initiate the Clinical Information Security Pre-Purchase Security Assessment"** — a named health system publishing its pre-purchase security gate.

> **HIC-SCRiM caution:** the PDF cover reads *"v2.0 OCTOBER 2023 — Reprint of 2020 Edition."* **The 2023 is a reprint date; the content is the 2020 edition.**

### D.8 Survey evidence — buyers are rejecting devices

**RunSafe Security, "2026 Medical Device Cybersecurity Index"** — n = **551 healthcare professionals involved in device purchasing decisions** (US/UK/Germany), released ~2026-04-29. [Report](https://runsafesecurity.com/report/medical-device-cybersecurity-index-2026/)

- **56% have rejected a device due to cybersecurity concerns — up from 46% in 2025.**
- **84%** include cybersecurity requirements in vendor RFPs (43% with detailed specifications, up from 38%).
- **81%** rate an SBOM "important" or "essential"; **35% will not consider a device without one.**
- ~79% say FDA cybersecurity guidance or EU MDR has meaningfully influenced procurement.
- 40% report security incidents affected trust in specific vendors; **7% stopped purchasing from certain vendors entirely.**

> ⚠️ **Bias caveat, and it matters:** RunSafe sells runtime exploit protection, and the same report claims 82% deployment/piloting of that category. This is **vendor-sponsored research with a commercial interest in the finding**. Use the **46% → 56% year-over-year trend directionally**; do not present the absolute figure as independent.

**Grade: SUBSTANTIATED as a vendor-sponsored survey**, with the bias stated.

### D.9 Cybersecurity items that remain unverified

| Item | Status |
|---|---|
| HIMSS / Ponemon-Censinet / CHIME / KLAS procurement-rejection figures | **UNVERIFIED** — search budget exhausted; only secondary blog coverage reached. No numbers reported here |
| RTA guidance (March 2023) current status | **UNVERIFIED** — the FR notice is durable, but the guidance landing page did not resolve and it is absent from FDA's cybersecurity hub list. Suggestive of supersession; absence from a curated page is weak evidence |
| Sept 27, 2023 guidance | Sourced from the FR index and downstream supersession statements, **not a direct fetch** (FDA's page now redirects to the Feb 2026 version) |
| A post-2019 MDS2 revision | None found across NEMA, MITA, ANSI, AAMI — but several sites were Cloudflare-blocked, so this is **absence of evidence** |
| Any GPO contractually *mandating* MDS2 | **UNVERIFIED** — nothing public found |
| Vizient device-cyber task force details | **UNVERIFIED** — secondary source only, no date reached |
| B. Braun CVSS 9.7 / 7.7 figures circulating in secondary coverage | **UNVERIFIED — conflicts with CISA**, which governs. Use CISA's 9.0 |

One defect noted in CISA's own material: ICSMA-22-251-01 describes itself as a follow-up to "ICSA-**21**-251-01 … published September 8, **2022**" — internally inconsistent.

---

## Claims under test

| # | Claim (as stated in project material) | Source doc | Verdict | Grade | Evidence |
|---|---|---|---|---|---|
| 1 | Competitors have FDA-cleared AI predictive monitoring on infusion pumps | Competitive threat thesis | **Refuted** | SUBSTANTIATED | Zero of 1,524 devices on FDA's AI-Enabled Medical Device List (current 2026-06-16) is an infusion pump, by free-text, product-code, and vendor cross-check (A.1) |
| 2 | "15–30 minute early warnings" for infiltration/occlusion/deterioration exist on a cleared pump | Competitive threat thesis | **Refuted** | SUBSTANTIATED | No such cleared capability. The only cleared PIV infiltration monitor is ivWatch (code PMS, optical, not on the AI list) (A.6); deterioration prediction exists only as standalone SaMD (A.10) |
| 3 | "ML models trained on 500,000+ infusion events with 15–30 minute warning capabilities" | Competitive threat thesis | **Not found** | UNVERIFIED | No FDA clearance (A.1–A.7); PubMed returns 0 hits for pump-ML occlusion or infiltration prediction (A.9); vendor-marketing search not completed before budget exhaustion |
| 4 | "60% adverse event reduction through predictive monitoring at Mass General Brigham, Mayo Clinic" | Competitive threat thesis | **No source of any kind — STRIKE IT** | **UNVERIFIED / appears fabricated** | **Twelve query variants**, including searches restricted to `massgeneralbrigham.org` and `mayoclinic.org` newsrooms, produced nothing — not peer-reviewed, not press release, not vendor marketing. What actually exists: MGB's irAE-detection LLM at >90% sensitivity/specificity (**detection accuracy, not adverse-event reduction** — a categorically different metric); Mayo's FDA-cleared ECG AI at +32% new low-EF diagnoses. Possible mis-transcription vector: MGB's electronic frailty index reports a **60% *higher* risk of death** — a figure of the opposite sign. **Attributing an unsourced outcome figure to two named real health systems is the highest-liability item in the project material.** There is no defensible substitute; delete the sentence |
| 5 | "80% reduction in IV medication errors with AI-driven systems" | Competitive threat thesis | **Source traced — and it is not AI** | **MISATTRIBUTED** | The figure derives from **Pang R et al., *J Pharm Pract Res* 2011;41(3):192–195** — a single-hospital Australian before/after audit of **Alaris Guardrails rule-based DERS**: infusion error rate 18% → 9.4% → 3.6% (18→3.6 is ~80% relative). **There is no AI or ML anywhere in that study.** Located in project-adjacent form only in uncited marketing pages carrying zero citations for any statistic. Counter-evidence omitted: Rothschild et al., *Crit Care Med* 2005, [PMID 15753744](https://pubmed.ncbi.nlm.nih.gov/15753744/) — randomized trial, **no significant difference** in serious medication error rates |
| 6 | "45% reduction in non-actionable alerts" | Competitive threat thesis | **Source traced to a single uncited blog post** | **UNVERIFIED / unsourceable** | The exact phrase returns **one on-topic healthcare hit** — an SEO blog post stating verbatim *"AI-driven alert filtering systems reduce non-actionable alerts by 45%"* with no citation, study, or footnote. **Claims 5 and 6 very likely share this one uncited source.** Real adjacent figures: alarm-management QI literature spans **12%–89%**; VanHorn 2024 shows guardrail overrides 23,751 → 5,885 (p<0.001) from **interoperability** (B.2) |
| 7 | "BioIntelliSense demonstrated 73% clinical deterioration sensitivity" | Competitive threat thesis | **Not found** | UNVERIFIED | BioIntelliSense does not appear anywhere on the FDA AI-Enabled Medical Device List (searched 2026-08-05). The cited sensitivity figure was not located |
| 8 | "Baxter Spectrum IQ … partnership with MedAware" | Competitive threat thesis | **Not found** | UNVERIFIED | MedAware appears nowhere on the FDA AI list. Baxter's cleared Spectrum IQ stack (K251636, K230041) and Dose IQ software (K230665, K211124) carry no AI listing (A.4, A.5). A commercial partnership could exist without a clearance — but it would not be a cleared AI capability |
| 9 | "96% of AI/ML devices cleared via 510(k)" | Regulatory strategy | **Confirmed** | SUBSTANTIATED | 1,466 / 1,524 = **96.2%** 510(k); 2.6% De Novo; 1.2% PMA (C.5) |
| 10 | "Typical clearance timelines of 3–6 months" | Regulatory strategy | **Partially confirmed — unsafe as a plan** | PARTIALLY SUBSTANTIATED | Median AI 510(k) receipt→decision = **142 days (4.7 mo)**, n=862; but 34.6% exceed 6 months, p90 = 8.7 months, and the figure excludes Q-Sub/RTA/prep. FDA's own FY2024 average TTD was **139 days and MISSED its 124-day goal** (C.7) |
| 11 | "FDA has authorized over 1,000 AI-enabled devices" | Regulatory strategy | **Confirmed (conservative)** | SUBSTANTIATED | **1,524** as of the list current 2026-06-16 (C.6) |
| 12 | A PCCP can expand the device's intended use | Regulatory strategy (implicit) | **Refuted** | SUBSTANTIATED | *"Modifications included in a PCCP **must maintain the device within the device's intended use**"* — statutory, per FD&C Act §§ 515C(a)(2), 515C(b)(2) (C.3) |
| 13 | A PCCP lets the device evolve toward predictive early warning post-clearance | Regulatory strategy | **Refuted unless pre-specified** | SUBSTANTIATED | FDA's own Appendix B example: adding advance prediction to a detection device, where predictive methodology was not pre-specified, **requires a new marketing submission** (C.4) |
| 14 | The PCCP guidance is the December 2024 final guidance | Regulatory strategy | **Superseded citation** | SUBSTANTIATED | Operative version is **issued August 18, 2025**; December 4, 2024 was the original issue (C.1) |
| 15 | A PCCP can cover non-AI device modifications under final guidance | Regulatory strategy (implicit) | **Refuted** | SUBSTANTIATED | The general-device PCCP guidance remains **DRAFT** (August 2024, FDA-2024-D-2338), marked "Not for implementation" (C.2) |
| 16 | Interoperability is table stakes rather than a differentiator | Commercial thesis | **Challenged** | OPINION on SUBSTANTIATED components | Auto-programming compliance was only **53.4%** even after integration (B.3) — the capability is cleared everywhere but realised nowhere near fully. That gap is a differentiator, not table stakes |
| 17 | Connected pumps face a hospital cybersecurity purchasing gate | Commercial thesis | **Confirmed — and it is contractual** | SUBSTANTIATED | HHS HICP 2023 § 9.L.B instructs HDOs to memorialize cyber requirements in contracting and RFPs and to "insist on receiving a MDS2" — **using an infusion pump as its worked example**. HSCC **MC2 v2 (Nov 2025)** converts this to contract terms with hard numbers (SBOM, 3-day KEV notice, 30-day patch, 2-year-EoS OS bar), **co-chaired by Mayo Clinic and Premier, a national GPO** (D.7) |
| 18 | A connected infusion pump is a "cyber device" under § 524B | Regulatory strategy | **Confirmed — and the bar is lower than assumed** | SUBSTANTIATED | All three § 524B(c) prongs met unambiguously. Guidance fn 61: even a device serviced briefly **over USB** "has the ability to connect to the internet." § 524B applies to **modification submissions too** — a Special or Abbreviated 510(k) does **not** exempt (D.4) |
| 19 | The operative FDA premarket cybersecurity guidance is the June 2025 version | Regulatory strategy | **Superseded citation** | SUBSTANTIATED | Current version issued **2026-02-03**, retitled "Quality **Management** System Considerations," Docket FDA-2021-D-1158 — verified independently twice (D.5) |
| 20 | FDA mandates SPDX or CycloneDX SBOM format | Common assumption | **Refuted** | SUBSTANTIATED | Guidance says industry-accepted formats "are **encouraged**." Those formats appear in the *NTIA* document, not as an FDA mandate (D.6) |
| 21 | IEC 60601-2-24 is an FDA-recognized consensus standard for infusion pumps | Standards matrix | **Refuted** | SUBSTANTIATED | FDA recognizes 50 entries across 60601-2-1 → -2-68, but **60601-2-24 is absent**. ANSI/AAMI ID26 is **withdrawn**. **There is currently no FDA-recognized particular safety standard for infusion pumps** — the recognized document is AAMI TIR101:2021 (fluid-delivery performance testing) (B.8) |
| 22 | The 2025 BD Alaris Class I recall is cybersecurity evidence | Competitive threat thesis | **Refuted** | SUBSTANTIATED | It is an **infusion-set flow-accuracy performance issue**. Separately, BD's earlier market pause was driven by software/hardware/user recalls, **not** cybersecurity — cyber was one remediation workstream (D.3) |

---

## What could NOT be verified

Grouped by why, because the reason changes what to do next.

**Exhausted search budget — retryable.** The session's 200 web searches were consumed (shared across this agent and two delegated researchers). The following remain open and are probably findable with a fresh budget:

- **Epic Toolbox / Showroom per-vendor designations** — the "Infusion Pump Integration" category is confirmed to exist (stage id 35), but the vendor roster requires an Epic UserWeb login (403/404 anonymous) (B.1).
- **Chin et al. 2024** — the ICU study carrying the 90.5% figure. Reachable only through Borrelli's systematic review; the primary was not located in PubMed (B.2).
- **HIMSS / Ponemon-Censinet / CHIME / KLAS** procurement-rejection survey figures. Only secondary blog coverage was reached; **no numbers are reported in this document** (D.9).
- **A post-2019 MDS2 revision** — none found across NEMA, MITA, ANSI, AAMI, but several sites were Cloudflare-blocked, so this is absence of evidence rather than evidence of absence (D.9).
- **Any GPO contractually mandating MDS2**, and Vizient device-cyber task force details (D.9).
- **RTA guidance (March 2023) current status**, and a direct fetch of the superseded September 2023 guidance (D.9).
- **ECRI 2026 Executive Brief long-form titles** — the PDF's subset-encoded fonts defeated extraction; 2026 #9's scoping text is SUBSTANTIATED-INDIRECT (B.7).

**Current-state data that does not exist at all.** These are not retrieval failures — no source publishes them, and any number presented as such should be challenged:

- **A 2024–2026 national smart-pump interoperability adoption rate.** The latest survey data is ASHP 2020 (13.4%). **Do not state a 2026 figure as fact** (B.0).
- **A national *measured* (as opposed to self-reported) DERS compliance rate.** All published figures are single-site, convenience-sample, or self-report (B.6).
- **Post-2009 FDA aggregate infusion-pump adverse-event counts.** FDA still cites 2005–2009 (~56,000 reports; 87 recalls, 14 Class I). Raw openFDA event counts are distorted by bulk manufacturer reporting and are **not safe to cite as an event rate**.

**Searched and genuinely absent — the absence is itself the finding.** These are not gaps to be closed; re-searching will return the same answer, and that answer is informative:

- No AI-enabled infusion pump on FDA's list (A.1), by three independent checks.
- No peer-reviewed literature on ML occlusion detection or ML infiltration prediction in infusion pumps — PubMed returns literally zero (A.9).
- No new PCA-pump (code MEA) clearance since 2017 (A.7).
- No AI listing for any pump-safety software (code PHC) or for ivWatch (code PMS) (A.5, A.6).

**Claims with no locatable primary source.** Each should be traced back to whoever introduced it into the project material, because a claim that cannot be sourced should not survive into a competitive assessment:

- **"60% adverse event reduction … Mass General Brigham, Mayo Clinic"** (claim 4) — twelve query variants including institution-restricted searches returned nothing. **Delete it.** Naming two real health systems against an unsourced outcome figure is a false-advertising and reputational exposure, not a citation nit.
- **"80% reduction in IV medication errors with AI-driven systems"** (claim 5) — traced, and the trace is the finding: a **2011 rule-based DERS study** relabelled as AI.
- **"45% reduction in non-actionable alerts"** (claim 6) — traced to a **single uncited SEO blog post**, which also appears to be the source of claim 5.
- "500,000+ infusion events" ML training corpus (claim 3); "BioIntelliSense 73% clinical deterioration sensitivity" (claim 7); "Baxter Spectrum IQ / MedAware partnership" (claim 8) — no primary source located for any.

**Defensible replacements, where the strategy needs a number.** For claim 5 → the Borrelli 2025 range (**15.4%–90.5%**), explicitly labelled *rule-based interoperability, not AI*; or Skog 2022's cleaner "16% reduction in administration errors, high-risk medication errors halved (12.8 → 6.8 per 100 infusions, p = 0.01)." For claim 6 → the **12%–89%** alarm-management range, or VanHorn 2024's verified guardrail-override reduction (23,751 → 5,885, p < 0.001). For claim 4 → **no substitute exists**; strike the sentence.

**Structural caveat that cannot be eliminated.** FDA's AI list is keyed on AI-related terminology in public authorization summaries. A vendor that implemented a learned model but described it without AI vocabulary would not appear. This cannot be ruled out from public sources. It is, however, substantially mitigated by the corroborating absences: zero PubMed literature, zero AI-framed vendor clearances across four relevant product codes, and no marketing-visible cleared claim. A capability hidden this thoroughly is also not a competitive threat, because a competitor cannot market a claim FDA has not cleared.

---

## Implications (OPINION — labelled)

Everything in this section is analyst judgment. The facts underneath are cited above; the conclusions drawn from them are not stated by any source.

**1. The catch-up framing is backwards, and that is good news.** The strategy assumes competitors hold an AI lead that PP3500 must close. The evidence says no competitor has cleared *any* AI capability on *any* infusion pump. There is no gap to close. There is an **open field** — and an unclaimed first-mover position, with all the regulatory cost that implies. The strategic question is not "how fast can we catch up?" but "do we want to be the one who pays to go first?" Those call for different plans, different budgets, and different risk postures.

**2. The AI claims are not merely unsourced — two of them are traceably misattributed.** This is stronger than "we could not verify." The "80% reduction in IV medication errors with AI-driven systems" resolves to a **2011 single-hospital study of rule-based Alaris Guardrails DERS** with no AI in it. The "45% reduction in non-actionable alerts" resolves to **one uncited SEO blog post**, which appears to be the same source. And the "60% at Mass General Brigham and Mayo Clinic" resolves to **nothing at all**. The pattern is consistent: real interoperability and DERS outcomes were relabelled as AI outcomes somewhere upstream. **The strategy is crediting AI for benefits that connectivity and drug libraries actually delivered** — and the MGB/Mayo line should be struck outright before this material goes anywhere near a customer, an investor, or a regulator.

**2a. Cite the version that is in force.** Three separate citation defects surfaced, each an audit finding on its own: the PCCP guidance is the **August 2025** issue, not December 2024 (C.1); the premarket cybersecurity guidance is the **February 2026** issue, not June 2025 or September 2023 (D.5); and **IEC 60601-2-24 is not FDA-recognized** while ANSI/AAMI ID26 is withdrawn, so there is currently **no FDA-recognized particular safety standard for infusion pumps** (B.8). A standards matrix or regulatory strategy carrying any of these is wrong today.

**3. The PCCP is a maintenance instrument, not a roadmap instrument.** This is the finding most likely to change a plan. A PCCP cannot expand intended use — that is statute, not preference (C.3). And FDA's own worked example says that adding *advance prediction* to a *detection* device requires a new submission when the predictive methodology was not pre-specified (C.4). If the PP3500 roadmap is "clear a detection feature now, evolve it into 15–30 minute early warning under the PCCP later," that path is closed as described. The workable version is the inverse: **decide the predictive claim before filing**, specify its methodology, statistics, and acceptance criteria in the Modification Protocol from day one, and use the PCCP to improve a claim already made. Retrofitting is a new 510(k).

**4. Two clocks, and the plan is probably reading the wrong one.** FDA clears 99% of 510(k)s within 90 FDA days while the average calendar time to decision is 139 days and rising (C.7). The difference is hold time on Additional Information requests — sponsor-side, and precisely where a first-of-kind AI submission with no same-code predicate since 2017 will spend its time. A "3–6 month" planning assumption is an average outcome for a typical device, not a commitment available to an atypical one. Planning against the **75th–90th percentile (7–9 months)**, plus Q-Sub and RTA time ahead of it, is the defensible posture.

**5. Interoperability is the underrated play, and the adoption numbers make the case.** ~88% of US hospitals have smart pumps; **~13% have EHR-to-pump auto-programming** (B.0). Even inside integrated systems, **47% of infusions are still programmed manually** (B.3). That is enormous addressable headroom with an existing regulatory route, existing predicates, an FDA-recognized standard family, a 2017 final FDA guidance, and published effect sizes — against an AI route with no predicate, no literature, and a first-mover regulatory bill. ECRI made the same point from the opposite direction by naming **under-use of smart pumps** a 2026 hazard (B.7). If the goal is measurable safety improvement per unit of regulatory risk, the ranking is not close.

**5a. For a PCA device specifically, the evidence points at misprogramming.** MAUDE analysis of IV PCA events found **6.5% were operator error, and 81% of those were pump misprogramming — roughly half associated with harm** — while 76.4% were device malfunctions that caused harm only 0.5% of the time (B.6). For PCA, the harm concentrates precisely where auto-programming intervenes. That is a stronger clinical argument for interoperability on this device than any generic safety claim.

**6. The De Novo question deserves a real answer.** 96.2% of AI devices go through 510(k) (C.5), which reads as reassurance. But that statistic describes devices *with predicates* — mostly radiology algorithms in a dense, mature predicate network. A PCA pump with AI predictive monitoring has no same-code predicate newer than 2017 and no AI-enabled pump predicate at all. The 96% figure may be describing a population this device is not a member of. Whether the SE argument survives, or whether De Novo is the honest route, is a question for the Q-Sub — and it should be asked early, because the answer changes the timeline by quarters.

**7. Cybersecurity is the gate the strategy is not treating as a gate.** Three gates now stack on a connected pump, and only the first is widely internalized. **Reputational** — FDA told providers to stop using the Symbiq pump for a cybersecurity reason alone, with no known adverse event (D.2); that is the precedent every hospital security officer knows. **Regulatory** — § 524B has made cybersecurity a premarket admissibility condition since March 2023, it applies to modification submissions as well as originals, and a Special or Abbreviated 510(k) does not exempt (D.4). **Commercial** — HSCC MC2 v2, co-chaired by Mayo Clinic and a national GPO, converts it into contract terms with hard numbers: SBOM delivery, three-business-day KEV notification, 30-day patching, and no operating system within two years of end-of-support at delivery (D.7). Against a market where **75% of 200,000+ pumps on live hospital networks carried known security gaps** (D.2), this is where a connected-pump program most plausibly loses a sale — not on a feature comparison. The § 524B modification trap in particular interacts directly with the PCCP strategy in implication 3 and deserves an explicit answer.

---

## Changelog

| Date | Author | Summary |
|------|--------|---------|
| 2026-08-05 | AI assistant(s) | Initial research pass for the `competitive-threat-assessment` analysis. Sections A and C grounded in primary FDA sources (AI-Enabled Medical Device List parsed in full — 1,524 rows; PCCP final guidance PDF; MDUFA V FY2025 Performance Report) plus original openFDA computations (AI 510(k) review-time distribution, n=862; pathway split; product-code cross-checks). Section B grounded in PubMed E-utilities retrieval, ASHP/ISMP/ECRI/AAMI sources, and FDA standards-recognition data. Section D grounded in CISA advisories, 21 U.S.C. § 360n-2, the Federal Register, and HHS/HSCC procurement documents. Headline Section A finding independently reproduced by a second researcher via a separate retrieval path. Residual gaps enumerated in *What could NOT be verified* rather than filled. |
