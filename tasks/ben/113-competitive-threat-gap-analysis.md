# 113 — Competitive Threat Gap Analysis

**ID**: 113
**Created**: 2026-08-05
**Status**: Complete
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
- [x] Fan out research agents (public-source substantiation) — all 4 returned (~250 KB of graded evidence)
- [x] Fan out discipline advisors — all 5 landed (`commercial` F-1…F-6, `regulatory-affairs` F-7…F-11, `cybersecurity` F-12…F-14, `risk-management` F-15…F-18, `clinical-affairs` F-19…F-22)
- [x] Author the aggregate: 22 assertions, 22 evidence-graded findings, an 11-risk competitive register with mitigations, 5 inline-SVG visualizations
- [x] `/gap-analysis render` + `--check` + `--strict-recs` — all clean; verified rendering in the running console
- [x] Push to `main` — PR #176 merged (`4c98764`)

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
    "agentic_hours": 5.5,
    "todos": [
      {
        "todo": "Public-source evidence base: FDA clearance/recall/enforcement record, independent market sizing, AI/interoperability/pathway reality, PCA clinical-utilization literature",
        "by_hand_hours": [80, 120],
        "persona": "regulatory-analyst + market-analyst",
        "note": "4 parallel research streams, ~130 graded claims against primary sources (openFDA, SEC, FDA guidance PDFs, PubMed, society guidelines). By hand this is multi-week desk research across two disciplines."
      },
      {
        "todo": "Five discipline assessments (commercial, regulatory, clinical, risk, cyber) each grounded in that evidence base",
        "by_hand_hours": [60, 100],
        "persona": "senior cross-functional (RA/clinical/commercial/risk/cyber leads)",
        "note": "Each is a substantive prescription with worked before/after examples and an owned acceptance criterion per action."
      },
      {
        "todo": "Aggregate authoring: 22 assertions, 22 findings, risk register, conductor re-verification of load-bearing arithmetic and artifact claims",
        "by_hand_hours": [24, 40],
        "persona": "program lead / analyst"
      },
      {
        "todo": "5 inline-SVG visualizations: palette validated against real console surfaces, screenshot-verified on both, then verified in the running console",
        "by_hand_hours": [8, 14],
        "persona": "data-viz designer"
      }
    ]
  }
}
```

_Estimate basis: ~172–274 by-hand person-hours against ~5.5 agentic hours. The dominant saving is the research layer — four simultaneous primary-source sweeps with per-claim grading is the part a human team does sequentially over weeks. The dominant residual human cost is judgment: deciding which advisor to believe when two disagreed, and re-verifying the load-bearing arithmetic rather than trusting it._

## Lessons Learned

<!-- LESSONS LEARNED: research-methodology, agent-orchestration -->
**Tell research agents "never guess a citation" and they will correct your briefing.** Two premises I handed the regulatory-record agent were wrong — the Alaris return-to-market date (K211218, 2023-07-21, not Feb 2024) and a non-existent ICU Medical sale of Smiths Medical (the 2025 divestiture was IV Solutions to Otsuka). Both would have mis-timed the competitive window. The instruction that produced the correction was explicit: *"Do NOT guess K-numbers, dates, or figures… a fabricated citation is the single worst outcome here."* Absent that, an agent optimising for a complete-looking answer fills the gap.

**Advisors correct each other if you let them read each other's work — and the corrections are the highest-value output.** The clinical advisor caught that the commercial advisor's "clinical files resolve to null" came from the *discovery index*, not the filesystem; the files exist, which makes it "present but unusable" — a worse defect that reads as coverage. It also caught that one research file quoted an ERAS guideline the other research file had tried to retrieve, got a 403 on, and explicitly graded "must not be quoted." **Rule: give each advisor the prior advisors' outputs, and record corrections in the aggregate rather than silently adopting the later view.**

**"Role resolution is not content" generalises past cybersecurity.** Two independent findings (F-12, F-19) reduced to the same defect: an index reporting `exists: true` for template stubs, and role patterns rooted at the wrong folder reporting real files as `null`. Any readiness dashboard keyed on role resolution overstates readiness in the first case and understates it in the second.

**Per-claim evidence grading beats a document-level banner.** A "demo sample data" banner tells a reader the device is fictional. It does not tell them a real vendor figure was pasted into a slot it doesn't describe, or that a clinical claim is real-world-sourced but methodologically malformed. Different defects, different fixes — only per-claim grading separates them.
<!-- /LESSONS LEARNED -->

<!-- LESSONS LEARNED: dataviz, tooling -->
**Validate the chart palette against the consuming surface, not the reference surface.** The `dataviz` skill ships a validated default palette, but "validated" means against *its* surfaces (`#fcfcfb` / `#1a1a19`). This console uses `#ffffff` / `#1e293b`. Re-running the validator against the real surfaces found one categorical set that passes all-pairs on **both**, which meant one palette could serve either theme. More importantly it killed the conventional red/amber/green risk encoding: red↔green measures **ΔE 4.1 under deuteranopia** — the classic failure. Severity is *magnitude*, not state, so a single-hue sequential ramp is both the accessible choice and the formally correct one.

**Check the renderer's contract before authoring markdown it will parse.** `render_sidecars.py` splits assertion table rows on `|` — so an escaped `\|` inside a cell silently shifts every column after it, and one assertion parsed as `open` instead of `refuted`. Caught only because the rendered counts didn't match the authored ones. **Rule: after rendering, diff the sidecar's counts against what you wrote.**
<!-- /LESSONS LEARNED -->

## Resume / handoff

**State: Complete.** Everything is merged to `main` via PR #176 (`4c98764`). Nothing is in flight.

**In-flight artifacts:** none of mine. Note the working tree carries **pre-existing uncommitted changes I did not author and did not touch** — `.claude/skills/project-console/console/{app.py,strategy/router.py,web/templates/_base.html,web/templates/workflow_b3_index.html}`, plus `tasks/ben/SECOPS.md`, `tasks/ben/103-*.md` and the `_usage-metrics/` JSON files. These blocked a local fast-forward of `main`, so **local `main` sits at `198814e` while `origin/main` is at `4c98764`.** My files were restored into the working tree via `git checkout origin/main -- <paths>`. Whoever picks up next should resolve or commit those changes and then fast-forward.

**If this analysis is taken forward,** the four high-severity / low-effort items are the place to start — F-9 (standards matrix), F-11 (product code), F-13 (stale cybersecurity reference stack), F-2 (add the exogenous risk class). Each is an authoring pass. The highest-leverage structural item is closing `risk_management_plan` / `hazard_analysis` / `hazard_traceability_matrix`, because F-12, F-16 and F-18 all depend on that same substrate — one absence disables three mitigations.

**Also still open (uncheckpointed from a prior session):** `ben/103` still has a marker at `.state/uncheckpointed-ben-103-2026-08-04.txt`. It was not addressed in this session.

## Changelog

- 2026-08-06: **Complete.** All five advisors landed; aggregate authored with 22 assertions (19 refuted / 2 confirmed / 1 partial), 22 evidence-graded findings, an 11-risk competitive register with scales + leading indicators + trigger thresholds + separated preventive/contingent controls, and 5 inline-SVG visualizations. Two inter-advisor corrections absorbed and recorded rather than silently adopted. Conductor independently re-verified the load-bearing arithmetic (all CAGRs; 9,567,700 ÷ 1,547; 127,500 ÷ 30; 150 ÷ 7 and ÷ 4), KOL contact status (8/8), the clinical-tree hazard-term absence, cybersecurity stub sizes + placeholder counts, the Q-Sub manifest assertion, and the LZH/MEA/FRN product-code definitions via a live openFDA query. `/gap-analysis render --check` and `--strict-recs` both clean; rendering verified in the running console (22 findings, 5 advisor tabs, charts inline). Shipped via PR #176 (`4c98764`).
- 2026-08-05: **Research agents 1–2 of 4 returned.** `research-market-data.md` (43 KB, 19 sub-claims tested): traced the repeated **$19.5B / 8.2%** to a single SkyQuest *global-2025* sentence pasted into three mutually exclusive slots (global-2031, US-2025, China); 5 growth claims arithmetically self-inconsistent; the two input docs state the same 2023 global market **10.8× apart** ($3.5B vs $37.72B); **PCA pumps grow 5.51% vs 7.3–8.2% for infusion overall**, and **ERAS Society 2025 colorectal guidelines direct away from routine IV PCA** — a structural headwind no input doc names. `research-competitor-regulatory-record.md` (76 graded claims: 66 SUBSTANTIATED / 2 INFERRED / 8 UNVERIFIED + 7 OPINION) **corrected two of my briefing premises**: Alaris return-to-market is **K211218, 2023-07-21** (not Feb 2024), and there is **no ICU Medical sale of Smiths Medical** (the 2025 divestiture was IV Solutions to Otsuka). New load-bearing facts: PCA product code **MEA has had zero clearances since K162165 (2017-08-29)**; FDA warning letter **CMS 702535 (2025-04-04)** holds ICU Medical's **CADD Solis VIP adulterated and misbranded** on a **2013 clearance (K111275)**, followed by three simultaneous Class I recalls on the CADD-Solis PCA variants (2025-04-10).
- 2026-08-05: **Research agent 3 of 4 returned** — `research-ai-connectivity-regulatory.md` (849 lines, 22 graded claims: 14 SUBSTANTIATED / 5 UNVERIFIED / 1 MISATTRIBUTED / 1 PARTIAL / 1 OPINION). Headline: **zero AI-enabled infusion pumps** among the 1,524 rows of FDA's AI-Enabled Medical Device List, verified three independent ways (free-text, all 19 product codes under 21 CFR 880.5725/870.1800/880.5730, and vendor sweep) — so the strategy's premise that competitors have predictive monitoring we lack is refuted in the opposite direction: **nobody has cleared one**. The real differentiator is interoperability (~88% smart-pump adoption vs **~13% EHR auto-programming**; 47% of infusions still manually programmed inside integrated systems). Three source-provenance defects found: "80% error reduction with AI" traces to a **2011 rule-based DERS study containing no AI**; "45% alert reduction" traces to a **single uncited blog post**; "60% adverse-event reduction at Mass General Brigham / Mayo Clinic" has **no source across 12 query variants** while naming two real institutions. Pathway corrections: operative PCCP guidance is **2025-08-18** (not Dec 2024); the general-device PCCP guidance is still **DRAFT**; the statutory intended-use limit (FD&C §515C) plus FDA's Appendix B worked example close the "clear detection now, evolve to prediction under the PCCP later" route. Real timelines: **median 142 days** receipt→decision across 862 AI 510(k)s since 2023, **34.6% exceeding six months** — plan 7–9 months, not the claimed 3–6. Standards defect: **IEC 60601-2-24 is not FDA-recognized** and ANSI/AAMI ID26 is withdrawn — there is currently no FDA-recognized particular safety standard for infusion pumps.
- 2026-08-05: **`commercial` advisor landed** → `recs-commercial.md` (F-1…F-6). Independently verified its arithmetic: **9,567,700 ÷ 1,547 = 6,184.68 → "$6,185"**, establishing that "9,567,700 annual IV pumps" is a **dollar figure mislabelled as a unit count** and that $6,185 is our own internal revenue-per-device, not a market ASP. Also: the "150+ hr vs typical 100-hour" battery claim **contradicts its own document's competitor table** (4–7 hr → 21×–37×, not 1.5×) and carries no test conditions while the competitor figures carry flow rates; accuracy is stated as ±0.5% / ±0.35% ("laboratory") / ±0.1% across three docs; the "reactive-alarm only" premise is contradicted by our own input analysis (Alaris PCA Module ships **PCA Pause + EtCO2**); the real defensible price is the buried Q4-2024 actual of **$4,250–$4,600/unit**; and the quality-posture wedge — the only one resting on substantiated competitor facts — is precisely where the `pca-device` DHF resolves most roles to `null`.
- 2026-08-05: Charts 1–4 built and visually verified on **both** console surfaces (screenshot pass): CAGR claim audit, evidence-grade distribution, segment-growth comparison, competitor regulatory-posture timeline.
- 2026-08-05: Task created. Grounded in `competitive-product-assessment.md`, `state-of-the-art-analysis.md`, `strategic-market-ai-infusion.md`, and the `gap-analysis` SKILL.md. Confirmed the console gap-analysis renderer (`console/gap_analysis/router.py:_md_to_html`, Python-Markdown with `tables` + `sane_lists`) passes raw inline `<svg>` through to `f._html | safe` — so SVG visualizations embedded in finding bodies will render in the console without any console-skill change.
