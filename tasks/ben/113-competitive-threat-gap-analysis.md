# 113 — Competitive Threat Gap Analysis

**ID**: 113
**Created**: 2026-08-05
**Status**: In Progress
**Created By**: Ben Xavier
**Owner**: Ben Xavier
**Priority**: High

---

## PERMANENT RULES (do not remove)

This task document is the **session-recovery point** for this work. If the current session drops, is compacted, or ends, the next session must be able to load **this file alone** and continue where we left off. That is only possible if the doc is kept current in-flight.

1. **Update at every meaningful checkpoint (HARD RULE).** After each meaningful unit of work — a converted/adopted doc, a committed change, a launched batch, a completed phase, a decision, a discovered blocker, a design pivot — update this task doc:
   - tick the relevant Todo checkbox
   - add a dated Changelog line naming the concrete artifact (commit SHA, file path, decision, blocker)
   - update any progress counts/tables in Goals
   - **when you tick a Todo off (or add/restructure Todos), fill/refresh the matching `## Economics` entry in the same edit** — the by-hand person-hours that unit would have taken, ranged + persona-tagged, per the rubric. **Checking the box is the estimate trigger.**
2. **Phase-end batching is OK; drift-batching is not.** Planned phases are a legitimate checkpoint — write at the phase boundary, before the next phase starts.
3. **A commit is not a substitute.** Git history records code; this doc records the project narrative.
4. **Resume-ready before any session boundary.** Before recommending a fresh session, marking Complete, or ending work, the doc must contain: (a) what was completed with concrete artifacts, (b) status of in-flight work, (c) priority-ordered next steps with file paths, (d) open questions, (e) the exact `/task` activation command to resume.
5. **Capture strategy + lessons as they happen** — write them in-flight, not just in chat.
6. **Estimation provenance.** The `## Economics` block is built per `.claude/skills/usage-metrics/references/effort-estimation-rubric.md`.

Success test for this doc: a fresh Claude session, given only this file, can re-enter the work without asking the user "what were we doing?"

## Goals

Produce a **substantive, evidence-graded gap analysis of competitor threats** against the GlobalLogic infusion portfolio (anchor: PP3500 / PainEase PCA Advanced), rendered in the project console with visualizations.

- **G1** — Assess real competitor threats (BD, Baxter, ICU Medical, B. Braun, Fresenius Kabi, Smiths/ICU CADD, Insulet, Medtronic) against our claimed positioning, grounded in **public, verifiable** sources (FDA 510(k) database, recall/MAUDE records, published market data, KLAS, company filings).
- **G2** — **Evidence-grade every claim.** Each assertion carries an explicit grade: `SUBSTANTIATED` (public verifiable source), `INTERNAL-DEMO` (repo-only, unverifiable outside), `INFERRED` (reasoned from substantiated facts), `OPINION` (advisor judgment, no source). Any unsubstantiated claim states *why* it is unsubstantiated.
- **G3** — Audit the project's **own competitive inputs** (`competitive-product-assessment.md`, `state-of-the-art-analysis.md`, `strategic-market-ai-infusion.md`) for internal contradictions, arithmetic errors, apples-to-oranges benchmarks, and unsourced numbers that would not survive external scrutiny.
- **G4** — Identify **Risks and Mitigations** for each material threat, with owner discipline, trigger/leading indicator, and DHF/regulatory linkage.
- **G5** — Render in the **project console** Gap Analysis view, well formatted, with **inline-SVG visualizations** (threat heatmap, evidence-grade distribution, clearance timeline, market-share/segment charts, risk matrix).

## Todos

- [x] Ground in the repo's competitive/market inputs + strategies
- [x] Read `gap-analysis` SKILL.md; confirm console render path supports inline SVG
- [x] Scaffold the analysis folder + evidence-grade contract README
- [x] Validate the chart palette against this console's real surfaces (`dataviz`)
- [x] Deterministic arithmetic audit of the project's own market claims
- [ ] Fan out research agents (public-source substantiation) — 3 of 4 returned; PCA-clinical still in flight
- [ ] Fan out discipline advisors — `commercial` landed (`recs-commercial.md`, F-1…F-6); `regulatory-affairs` (F-7…F-11), `cybersecurity` (F-12…F-14), `risk-management` (F-15…F-18) running; `clinical-affairs` gated on the clinical research
- [ ] Author the aggregate: assertions, findings (evidence-graded), risks + mitigations, visualizations
- [ ] `/gap-analysis render` + `--check`; verify in the console
- [ ] Push to `main`

## Strategy

<!-- STRATEGY CONTENT: commercial, competitive-positioning, evidence-grading -->
**Decision — separate "our fictional portfolio" from "the real competitive field."** The GlobalLogic devices (PP3500, SP6500, IP5000) and all their performance numbers are demo fabrications; the competitors named in the input analyses (BD Alaris, Baxter Spectrum IQ / Novum IQ, ICU Medical Plum 360, B. Braun Infusomat Space, Fresenius Agilia, Smiths/ICU CADD, Insulet Omnipod, Medtronic MiniMed) are **real companies with public regulatory and market records**. The analysis therefore grades evidence on a four-band scale rather than treating the whole document as uniformly demo-grade: competitor-side facts can and must be substantiated against FDA/public sources; our-side claims are `INTERNAL-DEMO` by construction and must be labelled as such so no reader mistakes a fabricated ±0.5% accuracy figure for verified evidence.

**Why it matters:** the user explicitly asked for "well researched, substantiated data and when just opinions or unsubstantiated, then say so, with reasoning." A single blanket demo banner does not satisfy that — per-claim grading does.
<!-- /STRATEGY CONTENT -->

## Economics

_By-hand person-hour estimate, filled at checkpoint per the effort-estimation rubric (`usage-metrics` skill)._

```json
{
  "economics": {
    "method_version": 1,
    "method_ref": ".claude/skills/usage-metrics/references/effort-estimation-rubric.md",
    "agentic_hours": null,
    "todos": []
  }
}
```

## Changelog

- 2026-08-05: **Research agents 1–2 of 4 returned.** `research-market-data.md` (43 KB, 19 sub-claims tested): traced the repeated **$19.5B / 8.2%** to a single SkyQuest *global-2025* sentence pasted into three mutually exclusive slots (global-2031, US-2025, China); 5 growth claims arithmetically self-inconsistent; the two input docs state the same 2023 global market **10.8× apart** ($3.5B vs $37.72B); **PCA pumps grow 5.51% vs 7.3–8.2% for infusion overall**, and **ERAS Society 2025 colorectal guidelines direct away from routine IV PCA** — a structural headwind no input doc names. `research-competitor-regulatory-record.md` (76 graded claims: 66 SUBSTANTIATED / 2 INFERRED / 8 UNVERIFIED + 7 OPINION) **corrected two of my briefing premises**: Alaris return-to-market is **K211218, 2023-07-21** (not Feb 2024), and there is **no ICU Medical sale of Smiths Medical** (the 2025 divestiture was IV Solutions to Otsuka). New load-bearing facts: PCA product code **MEA has had zero clearances since K162165 (2017-08-29)**; FDA warning letter **CMS 702535 (2025-04-04)** holds ICU Medical's **CADD Solis VIP adulterated and misbranded** on a **2013 clearance (K111275)**, followed by three simultaneous Class I recalls on the CADD-Solis PCA variants (2025-04-10).
- 2026-08-05: **Research agent 3 of 4 returned** — `research-ai-connectivity-regulatory.md` (849 lines, 22 graded claims: 14 SUBSTANTIATED / 5 UNVERIFIED / 1 MISATTRIBUTED / 1 PARTIAL / 1 OPINION). Headline: **zero AI-enabled infusion pumps** among the 1,524 rows of FDA's AI-Enabled Medical Device List, verified three independent ways (free-text, all 19 product codes under 21 CFR 880.5725/870.1800/880.5730, and vendor sweep) — so the strategy's premise that competitors have predictive monitoring we lack is refuted in the opposite direction: **nobody has cleared one**. The real differentiator is interoperability (~88% smart-pump adoption vs **~13% EHR auto-programming**; 47% of infusions still manually programmed inside integrated systems). Three source-provenance defects found: "80% error reduction with AI" traces to a **2011 rule-based DERS study containing no AI**; "45% alert reduction" traces to a **single uncited blog post**; "60% adverse-event reduction at Mass General Brigham / Mayo Clinic" has **no source across 12 query variants** while naming two real institutions. Pathway corrections: operative PCCP guidance is **2025-08-18** (not Dec 2024); the general-device PCCP guidance is still **DRAFT**; the statutory intended-use limit (FD&C §515C) plus FDA's Appendix B worked example close the "clear detection now, evolve to prediction under the PCCP later" route. Real timelines: **median 142 days** receipt→decision across 862 AI 510(k)s since 2023, **34.6% exceeding six months** — plan 7–9 months, not the claimed 3–6. Standards defect: **IEC 60601-2-24 is not FDA-recognized** and ANSI/AAMI ID26 is withdrawn — there is currently no FDA-recognized particular safety standard for infusion pumps.
- 2026-08-05: **`commercial` advisor landed** → `recs-commercial.md` (F-1…F-6). Independently verified its arithmetic: **9,567,700 ÷ 1,547 = 6,184.68 → "$6,185"**, establishing that "9,567,700 annual IV pumps" is a **dollar figure mislabelled as a unit count** and that $6,185 is our own internal revenue-per-device, not a market ASP. Also: the "150+ hr vs typical 100-hour" battery claim **contradicts its own document's competitor table** (4–7 hr → 21×–37×, not 1.5×) and carries no test conditions while the competitor figures carry flow rates; accuracy is stated as ±0.5% / ±0.35% ("laboratory") / ±0.1% across three docs; the "reactive-alarm only" premise is contradicted by our own input analysis (Alaris PCA Module ships **PCA Pause + EtCO2**); the real defensible price is the buried Q4-2024 actual of **$4,250–$4,600/unit**; and the quality-posture wedge — the only one resting on substantiated competitor facts — is precisely where the `pca-device` DHF resolves most roles to `null`.
- 2026-08-05: Charts 1–4 built and visually verified on **both** console surfaces (screenshot pass): CAGR claim audit, evidence-grade distribution, segment-growth comparison, competitor regulatory-posture timeline.
- 2026-08-05: Task created. Grounded in `competitive-product-assessment.md`, `state-of-the-art-analysis.md`, `strategic-market-ai-infusion.md`, and the `gap-analysis` SKILL.md. Confirmed the console gap-analysis renderer (`console/gap_analysis/router.py:_md_to_html`, Python-Markdown with `tables` + `sane_lists`) passes raw inline `<svg>` through to `f._html | safe` — so SVG visualizations embedded in finding bodies will render in the console without any console-skill change.
