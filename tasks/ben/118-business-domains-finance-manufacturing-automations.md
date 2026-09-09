# 118 — Business Domains: Finance, Manufacturing & Workflow Automations

**ID**: 118
**Created**: 2026-09-08
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
   - **when you tick a Todo off (or add/restructure Todos), fill/refresh the matching `## Economics` entry in the same edit** — the by-hand person-hours that unit would have taken, ranged + persona-tagged, per the rubric (if `## Economics` is present / usage-metrics is installed). **Checking the box is the estimate trigger** — don't defer it to a later checkpoint.
2. **Phase-end batching is OK; drift-batching is not.** Planned phases (e.g., "finish Phase 2, then log the whole phase at once") are a legitimate checkpoint — writing once per phase is fine if the phase is bounded and the write happens **at the phase boundary, before the next phase starts**. What's not OK: accumulating updates in your head across arbitrary work, waiting for "end of the session," "after the push," or the user to ask. By then a crash or context-trim has lost the state. Rule of thumb: if you can't name the specific upcoming checkpoint where you'll write the update, write it now.
3. **A commit is not a substitute.** Git history records code; this doc records the project narrative — what was done, why, what's left, what surprised us.
4. **Resume-ready before any session boundary.** Before recommending a fresh session, marking Complete, or ending work, the doc must already contain: (a) what was completed this session with concrete artifacts, (b) status of any in-flight work and temp artifacts, (c) priority-ordered next steps with file paths, (d) open questions blocking progress, (e) the exact `/task` activation command to resume.
5. **Capture strategy + lessons as they happen.** If the session produces option comparisons, scope/boundary decisions, architectural pivots, non-obvious insights, or corrected assumptions, write them into the appropriate section **in-flight** — not just in chat. Harvesting skills can only surface what was written.
6. **Estimation provenance (if `## Economics` is present).** This doc's `## Economics` block is the by-hand person-hour estimate, built per the effort-estimation rubric at `.claude/skills/usage-metrics/references/effort-estimation-rubric.md` (owned by the `usage-metrics` skill). To **add or refresh** an estimate on resume — even without loading the task skill — read that rubric first for the anchors, personas, and JSON schema; the block also carries a `method_ref` naming it. Skip silently if `usage-metrics` isn't installed. Point to the rubric, never copy it into this doc.

Success test for this doc: a fresh Claude session, given only this file, can re-enter the work without asking the user "what were we doing?"

## Goals

Extend the three-tier analytics stack (corpus = data, commercial = answers, console = display) from one business domain (Commercial) to three (Commercial, Finance, Manufacturing), and add healthcare / life-sciences workflow automations that cut across them.

- **G1 — Domain generalization.** One business-question engine, N domain roots. The `commercial` skill engine already takes `--root`; the console loader hard-codes `docs/project/commercial` + one sidecar. Generalize both so a domain is discovered, not wired. Commercial stays byte-for-byte unchanged as the first domain (its 30 approved/draft editions must not be disturbed).
- **G2 — Finance domain.** `docs/project/finance/` catalog (~10 questions), analysis plans, new demo corpus generators under `corpus/finance/`, 3–4 questions implemented end to end with claim-linted draft editions and a rendered sidecar.
- **G3 — Manufacturing domain.** Same shape under `docs/project/manufacturing/` + `corpus/manufacturing/`, framed by what 21 CFR 820 / ISO 13485 inspections look at (yield, NCR/CAPA, supplier quality, process validation, lot genealogy).
- **G4 — Workflow automations.** (a) Scheduled evidence refresh GitHub Action (openFDA re-snapshot → re-answer dependents → delta on the morning card). (b) Management Review Pack workflow assembling latest approved editions across all three domains. (c) MDR-timeliness watch and month-end close pack as console workflow-catalog entries.

### Decisions taken at kickoff (2026-09-08)

The user approved the plan with "go ahead and do it" and left three decisions to the AI assistant; defaults chosen:

| Decision | Choice | Why |
|---|---|---|
| Extend catalog vs. domains | **Domains** | Separate approver trees, keeps Commercial catalog at 30, corpus tree already groups by domain folder |
| Move BQ-28..30 (Economics) to Finance? | **Stay in Commercial** | Approved editions are hash-pinned; moving breaks approval history for no functional gain |
| Tab layout | ~~Three peer tabs~~ → **one "Business" dropdown** (user request, same day) | Three slots pushed the priority-ordered nav's rightmost entries into the hamburger on ordinary widths; a dropdown costs one slot and scales to more domains. A single domain still renders as a plain link |

<!-- STRATEGY CONTENT: architecture, business-analytics domains -->
**Domain generalization of the business-question stack.** The commercial engine (`commercial.py`, `DEFAULT_ROOT = docs/project/commercial`, `--root` override) and the console loader (`console/commercial/loader.py`, `COMMERCIAL_DIR` constant) were built for one domain. The chosen shape: a domain is any `docs/project/<domain>/` folder containing a `commercial.yml`-shaped catalog and a `.console/<domain>-index.json` sidecar; the console discovers domains and renders one nav tab each. The corpus tree is unchanged (it already namespaces `corpus/<domain>/<dataset>`). The engine's markers, lint, approval gate and edition lifecycle are domain-agnostic and reused verbatim — no second engine. Economics questions (BQ-28..30) remain in Commercial to preserve approved-edition hashes.
<!-- /STRATEGY CONTENT -->

<!-- STRATEGY CONTENT: commercial, finance & manufacturing reporting -->
**Standard HLS device-company reporting to build.** Finance: gross margin and std-vs-actual cost variance by line/region; cost of poor quality (scrap, rework, warranty, complaint handling, field-action spend); warranty/service reserve adequacy vs field failure rates; working capital (inventory days, AR aging by GPO, consumable pull-through); subscription ARR/NRR/churn; budget vs actual by function; cost of regulatory delay. Manufacturing: first-pass yield / scrap / rework; NCR rate + aging; CAPA open/aging/effectiveness; supplier incoming reject rate, scorecards, single-source exposure, audit currency; capacity vs demand plan; lot release lead time + DHR completeness; process-validation and calibration status; component obsolescence by hw rev; recall scoping via lot genealogy. All internal datasets are generated demo data with the demo banner.
<!-- /STRATEGY CONTENT -->

<!-- LESSONS LEARNED: process -->
**Two sessions in one checkout silently share uncommitted edits.** A sibling session committing "its" skill files swept up this session's in-flight version bump, producing a release number on `main` that does not contain the change its changelog describes. Detect it with `git diff --stat` on files you edited before you commit (no diff = someone else committed your edit). Prevent it by running concurrent sessions in separate `git worktree`s, and by always staging an explicit path list, never `git add -A`.
<!-- /LESSONS LEARNED -->

<!-- LESSONS LEARNED: tooling -->
**Generalizing a hard-wired console section costs less than a new module.** The commercial console module had exactly four coupling points to its domain (loader root constant, sidecar filename, route prefix, template URL literals). Parameterizing those with a shared `_domain_ctx` and a discovery scan made the same 1,200-line router serve N domains with no duplication; the redirect from the old prefix kept every existing test passing unchanged. Check the coupling points before assuming a second copy is needed.
<!-- /LESSONS LEARNED -->

<!-- STRATEGY CONTENT: architecture, narrative layer for computed reports -->
**Prose around numbers, never numbers from prose.** Computed reports stay terse and cited; the reader-facing layer (executive summary, "what this tells us" per section) is a separate `narrative.md` per edition, hash-pinned to the report/data it explains and held to the identical claim lint — every sentence with a digit must carry a marker that resolves against the edition's pins, so the LLM can interpret but cannot introduce or recompute a figure. Because the narrative sits outside the approval hash, it can be added or regenerated on approved editions without breaking immutability; a re-answer makes it visibly stale. The export assembles both layers into one document with numbered references, which is what a CFO or VP Quality actually circulates.
<!-- /STRATEGY CONTENT -->

<!-- LESSONS LEARNED: tooling -->
**Feed the linter back to the writer.** The first narrative synthesis passed the claim lint on the first try because the system prompt encoded the lint's exact rules (marker on the same line as any digit; headings must match; no estimation words without `[assume:]`), and the route retries once with the lint findings verbatim. Writing the generator against the checker's contract, rather than hoping and filtering, is what made an LLM-written layer acceptable inside a hash-pinned evidence chain.
<!-- /LESSONS LEARNED -->

<!-- STRATEGY CONTENT: regulatory, management review inputs -->
**Management Review Pack boundary.** The pack assembles quantitative inputs (approved answer editions across Commercial / Finance / Manufacturing: verdicts, expectation verdicts, issues, risks, pin freshness) and stops there. It does not claim to *be* the management review, does not cite ISO 13485 clause numbers (the standard is deliberately undistilled as QMS-level; the citable source is the QMS SOP `GL-SOP-QM-002`, §6.2 inputs), and never includes unapproved drafts in a pack of record (draft preview is flagged and internal). Approval remains a human act in the domain tabs; CI only refreshes evidence and drafts.
<!-- /STRATEGY CONTENT -->

<!-- STRATEGY CONTENT: operations, workflow automation -->
**HLS workflow automations chosen.** (1) Scheduled evidence refresh — weekly GitHub Action re-snapshots openFDA datasets, re-answers dependent questions into drafts, surfaces the delta. (2) Management Review Pack — ISO 13485 management-review inputs (complaints, CAPA, supplier performance, audits, post-market data) assembled from latest approved editions across domains into a dated pack. [Resolved at close-out: cite `GL-SOP-QM-002` Management Review §6.1/§6.2 — the QMS SOP — not an ISO clause; ISO 13485 is deliberately undistilled in `docs/external/`.] (3) MDR-timeliness watch (30-day clock). (4) Month-end close pack (auto-answer finance questions on the 1st). Only two Actions exist today (file-locator rebuild, usage-metrics aggregate), so (1) sets the pattern for data-driven Actions.
<!-- /STRATEGY CONTENT -->

## Todos

### Phase 1 — Domain generalization (skill work: `commercial` + `project-console`)
- [x] Read `commercial.py` root/corpus handling + `render` sidecar naming; read console `commercial/` loader, router, templates, `app.py` nav probe
- [x] Engine: `--domain <slug>` shorthand; catalog `commercial.yml` else `<domain>.yml`; sidecar `.console/<domain>-index.json`; `domain` identity block (schema 1.5); lint-exempt id token widened to `[A-Z]{1,2}Q-NN` (commercial skill v15)
- [x] Console: `loader.list_domains()` discovery; routes at `/domains/{domain}/…`; `/commercial…` 307-redirects; nav loops `request.state.domain_nav` with `ic-finance` / `ic-manufacturing` sprites (project-console 1.63.0)
- [x] Regression: 19/19 commercial console tests pass (12 existing + 7 new in `tests/test_commercial_domains.py`); live probe of `/domains/commercial`, `/commercial` → 307, `/domains/nope` → 404. `commercial.py check` reports pre-existing pin staleness (July pins vs Sept today) — not a regression. One unrelated pre-existing failure in `test_setup_cli_catalog.py` (Jama blank-URL entry from ben/116) confirmed failing at HEAD too.
- [x] Bump skill versions + changelogs (commercial README v15, project-console README 1.63.0); `/sync-skills push` deferred to close-out

### Phase 2 — Finance domain
- [x] Corpus generators under `corpus/finance/` (snapshot `2026-09-08` each, `check_knobs.py` assert seams): `internal-standard-costs` 160 rows (cross-dataset knob check vs `commercial/internal-financials`), `internal-warranty-claims` 607, `internal-gl-budget` 120, `internal-ar-inventory` 1,200 (adds `product_line` grain)
- [x] `docs/project/finance/finance.yml` (10 FQ, 4 categories, `domain:` block) + README + `plans/FQ-01..10` + `code-quality/` (12 artifacts, checks pass, unreviewed)
- [x] `computations.py` (domain-local helpers) + `bq_modules/fq_01,03,06,08.py`
- [x] FQ-01 (H1 2026 GM 51.5%, below 55% floor; PP3000/IP5000 hw std-cost variance ~+11%), FQ-03 (YTD warranty +23.1%; PP3000 $801/unit), FQ-06 (DSO 55.2 d vs 50; Northgate over-90 32.5%; $3.36M cash trapped), FQ-08 (opex +1.5% YTD; RA/QA +16.7%, S&M −9.8%, R&D +6.6%) — FQ-01/06/08 lint 0/0; FQ-03 lint 2 errors on stale `commercial/internal-fleet` + `internal-complaints` pins (43 d > 7 d) → resolved in main session by `corpus refresh` of those two datasets + re-answer (see changelog). 9 expectation thresholds are `[VERIFY]` stand-ins

### Phase 3 — Manufacturing domain
- [x] Corpus generators under `corpus/manufacturing/` (snapshot `2026-09-08` each, `check_knobs.py` assert seams): `internal-production-lots` 672 rows, `internal-ncr-capa` 286 rows (+`supplier_id` col beyond brief), `internal-suppliers` 240 rows, `internal-process-validation` 155 rows
- [x] `docs/project/manufacturing/manufacturing.yml` (10 MQ, 5 categories, 15 terms, `domain:` block) + README + `plans/MQ-01..10` + `code-quality/` (9 artifacts, checks pass, unreviewed)
- [x] MQ-01 (FPY 96.6%, PP3500 rev C at test 92.5%), MQ-03 (32 open CAPAs, 21 past due, effectiveness 60% vs 90%), MQ-05 (SUP-003 single-source pump-motor 7.9% rejects, audit 289 d overdue), MQ-08 (10 overdue validation/calibration items, Westfield cluster) — all 0 lint errors / 0 warnings; sidecar schema 1.5, 4 draft-only + 6 not-implemented. 7 expectation thresholds are `[VERIFY]` stand-ins (`validated: false`)

### Phase 4 — Workflow automations
- [x] `.github/workflows/business-evidence-refresh.yml` (installed from the new commercial-skill template) — weekly Mon 05:00 UTC: `corpus refresh` every `*/openfda-*` → engine `dependents <ds>` → `answer` per discovered domain (drafts only); monthly 1st 05:30 UTC: `dependents '*'` re-answer in every domain → `render` → `pack` (approved only); `workflow_dispatch` with mode input; commits corpus + reports + sidecars + pack. **Untested in CI** (fires on schedule / manual dispatch after merge).
- [x] Console workflow-catalog entries D3 Business Evidence Refresh (live), D4 Management Review Pack (live, detail view + Generate form → POST `/workflows/management-review-pack/generate`), D5 MDR Timeliness Watch (partial: BQ-21 + monthly Action), D6 Month-End Close Pack (partial: monthly Action's Finance leg)
- [x] Management Review Pack assembler = engine action `commercial.py pack --domains … [--as-of] [--include-drafts]` → `docs/project/management-review/<date>/pack.{md,json}` (+ folder README). Plus engine `dependents <dataset|prefix|*>`. First pack assembled for 2026-09-08 over Commercial (30 answered); to be re-assembled at close-out with Finance + Manufacturing.

### Phase 5 — Narrative layer + export (user request 2026-09-08: "executive summary + a narrative per section explaining what the data tells us, as expansions; export to Word/PDF; build and test")
- [x] Contract: per-edition `narrative.md` (AI-assisted prose *around* the computed results — never new figures; every figure marker-cited and claim-linted like the report; front matter pins the report/data hashes it was written against so it goes stale visibly) — engine `narrative-lint`, sidecar/edition status `narrative: present|stale|missing`
- [x] Engine `export <BQ> [--edition] --format md|docx|pdf` — assembles title/banner/metadata → executive summary → each report section followed by its "What this tells us" → expectations → issues/risks → references; docx via pandoc, pdf via LibreOffice headless (clear error if tools absent)
- [x] Console: "Generate narrative" (server-side Claude synthesis grounded on report.md + data.json, then engine lint; stored as `narrative.md`), executive-summary panel + per-section "What this tells us" expansions in the Report tab, Export buttons (docx/pdf) streaming the file
- [x] Tests: `tests/test_commercial_narrative.py` (6 tests, exercises the real engine's export end to end); full console suite green. Live: FQ-06 narrative generated in ~2 min, lint 0/0 first pass; BQ-01 (APPROVED, 2026-07-27.3) narrative generated, lint 0/0, `check` raised no hash mutation; md/docx/pdf downloads 200 (pdf 176 KB via LibreOffice); Word file carries the exec summary + 7 "What this tells us" blocks + references; Chrome screenshot of the panel + folds

### Phase 6 — Automatic narratives + backfill (user request 2026-09-08: "it should be done when a report is created or updated; retroactively generate them for all reports; spin up agents")
- [x] Engine `narrative_generate` via `claude -p` (6 s round-trip verified; MQ-05 in 56 s, 0 errors / 1 warning); `narrative-generate [--force] [--retries]`; `answer` calls it after a clean lint, `--no-narrative` opts out, failure never fails the answer (commercial v17)
- [x] Console button delegates to the engine (1.67.1); console-side SDK synthesis removed
- [x] Backfill: 4 subagents over the 35 remaining editions — every `narrative-generate` exited 0 on the FIRST pass (no automatic retry triggered anywhere, no hand-fixes); 7 warnings total, all "estimation language without [assume:]" on otherwise fully cited lines (left as-is; warnings are non-blocking by design). One agent returned early after backgrounding its batch and was resumed to completion
- [x] Rendered all three sidecars (schema 1.6): 38 / 38 implemented questions `narrative: present`; `check` reports no hash mutation on the 30 approved editions; `pack` now carries each question's executive summary (30 summaries in the 2026-09-08 pack); console suite green; spot-checked BQ-02, BQ-19, MQ-03 pages render their folds

### Phase 7 — Visualization vs Full Report (user request 2026-09-08: "break Report into Visualization (quick view of the analyzed data) and Full Report (for Word/PDF; tabular data with the graphs in the right sections)")
- [x] Section↔chart placement rule: a series belongs to the report section whose body cites `[derived: <series-id>]` (existing contract), else token-overlap fallback, else an "Additional charts" tail; optional explicit `section:` on a series (additive)
- [x] Console: `Visualization` tab (verdict, executive summary, charts, expectation verdicts) + `Full Report` tab (document order: each section's table + its charts + "What this tells us", narrative issues/risks, references, export buttons); chart panel factored into a Jinja macro so the router can place it per section
- [x] Engine `export`: render each series to SVG (pure-python; bars / paired-bars / timeseries / stat) into `exports/<stem>-charts/`, referenced from the right section of the markdown; docx via pandoc embeds SVG (PNG via rsvg-convert when available)
- [x] Tests (2 new placement cases; full console suite green) + live check: FQ-06 Full Report renders 9 inline charts across 6 sections + Overview; export docx carries 9 media files; PDF 249 KB with charts

### Phase 8 — Answer-view hierarchy pass (user 2026-09-08: "seems very busy and complicated, take a fresh design look")
- [x] Diagnosis: one `.cm-chip` component served status + actions + navigation + help, so 8 same-weight pills competed and the right half of the page was empty
- [x] Header: ⓘ icon-only on the identifier line; status as an **exception-only** meta line (draft state dropped — the editions rail already names it; Derived/Fresh dropped — only `assumed`/`unavailable`/`aging`/`stale` surface); actions right-aligned with Word+PDF+Markdown behind one `⬇ Export` menu; "Data view" removed as a duplicate of the Data tab (all four narrowings requested by the user during the pass)
- [x] Tabs carry no status badges (lint / code / verification / plan) — one attention dot when a tab's contents need a look; counts stay on the panels
- [x] Verdict typeset as lead + dashed supporting points via `_split_verdict` (bracket-aware, ≥3 clauses, characters unaltered)
- [x] 8 new tests + vplan tab test rewritten; 106/106 green; live-verified on MQ-01 (clean state) and BQ-25 (assumed + stale + assumption)
- [x] Two defects caught in verification: shared `.cm-verdict-k` gutter wrapped the executive-summary label; `.cm-meta-item` declaring `--c` beat the tone classes on source order and greyed every status dot

### Close-out
- [x] READMEs: `docs/project/README.md` (+ `finance/`, `manufacturing/`, `management-review/` rows) and `docs/project/corpus/README.md` (+ `finance/`, `manufacturing/` rows), each with a changelog row
- [x] Reference audit (subagent, `/reference-audit init` + `fan-out`) over the five new READMEs → reports under `docs/_analysis/pca-device/*-readme-references-audit/`: 57 sound / 4 unverified / 4 broken. All 8 fixed: `approval.yml` wording ×2, roadmap-question wording ×2, MQ-10 consumer, hw rev C attribution, FQ-05 consumer, and the two ISO 13485 `[VERIFY]` tags repointed to the QMS SOP `GL-SOP-QM-002` Management Review (§6.1 cadence, §6.2 inputs) — the standards README deliberately excludes ISO 13485 as QMS-level, so the SOP is the citable source
- [x] Commit `b3f6d71` → PR #184 → merged to `main` as `2173a0d` (197 files); branch deleted; this doc + index updated
- [x] User follow-up (2026-09-08): collapse the three domain tabs into ONE "Business" nav dropdown to save nav width — `_base.html` (`.nav-dd` button + `ic-business` sprite + menu), topnav.js (menu re-parented to header, fixed-positioned under the button, closes on resize/scroll/outside/Escape, one priority item), `console.css` `.nav-dd*`, domains test updated; project-console 1.66.0
- [x] `/sync-skills push` done 2026-09-08 (user go-ahead): hitachi PR #303 (commercial v14→v18) + PR #304 (project-console 1.61.0→1.67.3), PR-only per the sync-skills contract; 2 upstream-only theme footers pulled; sync-log recorded. Say "merge them" to squash-merge + prune
- [x] First real CI run of `business-evidence-refresh` (weekly): SUCCESS — 5 openFDA snapshots refreshed (2026-09-09), 9 dependent BQs re-answered as drafts, committed `59d787c`; 2 drafts (BQ-09, BQ-20) lint-failed on stale INTERNAL pins (winloss, docket at 30 d) → refreshed those datasets locally, re-answered (lint 0/0 + narratives), and widened the Action's weekly leg to refresh every corpus dataset so internal pins never age out between runs. Narratives for the other 7 CI drafts generated locally (CI has no CLI). All drafts now `narrative: present`

## Open Questions

- None. The ISO 13485 question resolved: cite `GL-SOP-QM-002` (QMS SOP) rather than a clause; 21 CFR 820 verified sound in both tiers by the reference audit. Remaining `[VERIFY]` tags are the expectation thresholds inside the catalogs (stand-ins, `validated: false`) — those are for the CFO / VP Quality personas to ratify, by design.

## Resume

**Activation:** `bash .claude/hooks/task-activate.sh add <SESSION_UUID> 118`

**Reference audit:** launched as a subagent over the five new READMEs (finance, manufacturing, corpus/finance, corpus/manufacturing, management-review) per `/reference-audit` `init` + `fan-out`; findings land under `docs/_analysis/`. Apply or defer its fixes before commit.

**Landed on `main` (2026-09-08):** PR #189 → `d97dddd` (auto-narrative + backfill), PR #188 → `5bc8023` (narrative layer + export), PR #185 → `8fa73a7` (Business nav dropdown), PR #184 → `2173a0d` (commit `b3f6d71`). Nothing from this task is uncommitted except this post-merge bookkeeping edit to the task doc + index. `tasks/ben/SECOPS.md` carries an unrelated local change from before this task.

**Was in-flight before the merge (now committed):** `.claude/skills/commercial/{SKILL.md,README.md,scripts/commercial.py}`, `.claude/skills/project-console/{VERSION,SKILL.md,README.md,console/app.py,console/commercial/{loader,router}.py,console/web/templates/{_base,commercial_index,commercial_view,commercial_data}.html,tests/test_commercial_domains.py}`, `docs/project/commercial/.console/commercial-index.json` (re-rendered, schema 1.5). Console restarted on :8765 with the new code.

**First action on resume:** run `/sync-skills push` for `commercial` (v15) and `project-console` (1.65.0) once the user confirms (registry-facing). Then check the first `business-evidence-refresh` Action run (schedule or `workflow_dispatch`) in GitHub Actions and triage any lint warnings it reports. Optional next: approve a first Finance/Manufacturing edition in the console so the Management Review Pack carries all three domains.

## Economics

_By-hand person-hour estimate per the effort-estimation rubric (`usage-metrics` skill). All phases estimated (Phases 2-3 were subagent-built; their by-hand baseline is what a finance/QE analyst + developer would have taken). `agentic_hours` = supervised human attention so far (planning discussion + review), refreshed at checkpoint._

```json
{
  "economics": {
    "method_version": 1,
    "method_ref": ".claude/skills/usage-metrics/references/effort-estimation-rubric.md",
    "agentic_hours": {
      "min": 3,
      "max": 6
    },
    "todos": [
      {
        "todo": "Phase 1 — generalize commercial engine + console to N business domains (engine --domain/catalog/sidecar/domain block; loader discovery; router /domains/{domain} + legacy redirect; nav; 7 new tests)",
        "personas": [
          "rd-lead"
        ],
        "manual_hours": {
          "min": 40,
          "max": 90
        },
        "confidence": "med",
        "basis": "software anchor 325-750 LOC/dev-month on ~350 net LOC incl. tests; internal tooling not IEC 62304, so the low end of the anchor is defensible"
      },
      {
        "todo": "Phase 1 — skill docs: commercial SKILL.md Domains section + README v15; project-console SKILL/README 1.63.0",
        "personas": [
          "rd-lead"
        ],
        "manual_hours": {
          "min": 4,
          "max": 10
        },
        "confidence": "med",
        "basis": "document authoring 3-7 hr/page on ~1.5 pages of contract text"
      },
      {
        "todo": "Phase 4 — engine dependents + pack (Management Review Pack assembler), GitHub Action template + install, console Workflows D3-D6 + pack detail view + generate route, management-review README",
        "personas": [
          "rd-lead",
          "quality-engineering"
        ],
        "manual_hours": {
          "min": 45,
          "max": 110
        },
        "confidence": "med",
        "basis": "software anchor on ~500 net LOC (engine 170, Action 130, console 120, template 90) at the low end; plus judgment-tier 4-12 h QE design of what a review input pack must and must not contain (no published norm)"
      },
      {
        "todo": "Phase 2 — Finance domain: 4 seeded corpus generators with knob asserts + READMEs, 10-question catalog with terms/explainers, 10 analysis plans, domain computations + 4 modules, 4 linted draft editions, code-quality store (built by subagent; reviewed + FQ-03 re-pinned in main session)",
        "personas": [
          "rd-lead",
          "commercial",
          "quality-engineering"
        ],
        "manual_hours": {
          "min": 60,
          "max": 140
        },
        "confidence": "med",
        "basis": "software anchor on ~1,400 net LOC (4 generators ~500, 4 modules ~700, computations 150) at the low end for internal tooling + document authoring 3-7 hr/page on ~12 pages of plans/READMEs/catalog prose; judgment-tier adder for a finance analyst defining the metrics (GM, std-cost variance, DSO, budget variance) and the demo narrative knobs"
      },
      {
        "todo": "Phase 3 — Manufacturing domain: same shape (4 generators + knob asserts, 10-question catalog, 10 plans, computations + 4 modules, 4 linted drafts, code-quality store)",
        "personas": [
          "rd-lead",
          "quality-engineering"
        ],
        "manual_hours": {
          "min": 60,
          "max": 140
        },
        "confidence": "med",
        "basis": "same sizing as Finance (~1,400 net LOC + ~12 pages); judgment-tier adder for a QE defining FPY / NCR-CAPA aging / supplier scorecard / validation-posture metrics"
      },
      {
        "todo": "Close-out — corpus refresh of two stale datasets + re-answer, pack re-assembly, two console null-point fixes with regressions, project + corpus README rows, concurrency incident triage, task doc + economics",
        "personas": [
          "rd-lead"
        ],
        "manual_hours": {
          "min": 4,
          "max": 10
        },
        "confidence": "med",
        "basis": "defect fixing ~4-6 hr/defect x2 at the low end (small, well-localized) + ~1 page of README rows"
      },
      {
        "todo": "Nav: collapse domain tabs into one Business dropdown (template/JS/CSS/test; console 1.66.0)",
        "personas": [
          "rd-lead"
        ],
        "manual_hours": {
          "min": 6,
          "max": 14
        },
        "confidence": "med",
        "basis": "software anchor on ~120 net LOC incl. fixed-position menu re-parenting + a11y; low end for UI tooling"
      },
      {
        "todo": "Phase 5 — narrative layer + export: engine narrative-lint/stamp/export + shared lint refactor (~330 LOC), console generate/display/export routes + template + CSS (~260 LOC), 6-test suite, SKILL/README docs, live verification incl. LLM synthesis prompt engineering",
        "personas": [
          "rd-lead",
          "quality-engineering"
        ],
        "manual_hours": {
          "min": 40,
          "max": 95
        },
        "confidence": "med",
        "basis": "software anchor 325-750 LOC/dev-month on ~650 net LOC at the low end (internal tooling) + document authoring 3-7 hr/page on ~2 pages of contract text; judgment-tier 4-10 h QE for defining the provenance/lint contract that lets LLM prose sit inside a hash-pinned evidence chain (no published norm)"
      },
      {
        "todo": "Phase 6 — automatic narrative on answer (engine narrative-generate via claude CLI, console delegation), pack exec summaries, CI notes, and backfill of 35 editions' executive summaries + per-section insights via 4 subagents",
        "personas": [
          "rd-lead",
          "commercial",
          "quality-engineering"
        ],
        "manual_hours": {
          "min": 60,
          "max": 130
        },
        "confidence": "med",
        "basis": "software anchor on ~180 net LOC at the low end (4-8 h) + document authoring 3-7 hr/page for the by-hand equivalent of 35 narratives (exec summary + ~6 sections each ≈ 0.4-0.5 page of analyst prose per report, ~15 pages total → 45-105 h, an analyst reading each report and writing the interpretation) + ~2-4 h QE review sampling; judgment-tier on the prose page count"
      }
    ]
  }
}
```

## Changelog

- 2026-09-08: **Phase 8 (answer-view hierarchy) built + tested.** project-console 1.69.0. Design rule adopted for this surface: **status is exception-only** — a marker renders only at a value a reader can act on, so the header and tab row are silent in the normal case and a badge always means something. Corollary applied to tabs: navigation carries no status; the dot says "look here", the panel says what. Lesson: a utility class appended at the end of a stylesheet must not declare a custom property that tone classes set earlier at equal specificity — source order silently flattens them (every status dot rendered grey until caught in the browser, not by the tests).
- 2026-09-08: **Phase 7 landed** — PR #198 → `8ad8b84`. Registry PRs #303/#304 each advanced by one commit (commercial v19, project-console 1.68.0); still PR-only, awaiting the user's merge decision. PDF fix along the way: LibreOffice draws embedded SVG blank, so charts are rasterized to PNG (2x) via a single headless LibreOffice call before pandoc; md keeps SVG.
- 2026-09-08: **Phase 7 built + tested: Visualization / Full Report split + charts in the exported document.** Engine v19 (`render_series_svg`, `place_series`, Overview block), console 1.68.0 (`_cm_chart.html` macro, `_place_series` mirror, two tabs). Decision: chart placement keys off the report's own `[derived:]` citations in DATA sections (non-data sections excluded — they cite everything), so screen and document agree without a new schema field; an optional `section:` override exists. Also: CI first run triaged (see Phase 4 todo), 2 internal datasets refreshed, 9 CI drafts given narratives.
- 2026-09-08: **Registry push + project close-out.** PDLC_DEMO PR #196 (`ff97804`: commercial v18 doc rows left by ben/121, task doc). Registry: hitachi PRs #303 + #304 opened (36 files, all LOCAL_AHEAD by blob-history probe; 0 divergence). Pulled 2 footer templates. Dispatched the evidence-refresh Action (weekly mode) for its first CI run.
- 2026-09-08: **Phase 6 landed** — PR #189 merged to `main` as `d97dddd`. Built in an isolated `git worktree` from origin/main because a concurrent session (task ben/121, workbench validation) had ~70 dirty files in this checkout, five of them overlapping mine (commercial + project-console README/SKILL/VERSION); my edits were re-applied as text replacements against origin/main so none of the other session's hunks were swept up. This checkout is deliberately NOT pulled forward (the other session's dirty tree blocks a safe fast-forward); its next pull will reconcile — my uncommitted copies are byte-identical to what merged. Lesson (repeat): concurrent sessions belong in separate worktrees.
- 2026-09-08: **Phase 6 complete.** 35 narratives backfilled by 4 parallel subagents in ~19 min wall-clock (1–3 min each, sequential within an agent); 0 lint errors first pass across all 35 — the system prompt encodes the lint rules, so the writer rarely trips the checker. Also: `pack` includes exec summaries; Action comments document that CI runners without an authenticated CLI leave `narrative: missing` (visible, not silent). Skill versions: commercial v17, project-console 1.67.1.
- 2026-09-08: **Phase 6 in flight.** Decision: narrative synthesis lives in the ENGINE (`claude -p`), not the console — so `answer` (CLI, console, CI where authenticated) produces the narrative as part of the report, and the console button is only a regenerate. Backfill launched as 4 parallel subagents.
- 2026-09-08: **Phase 5 landed** — PR #188 merged to `main` as `5bc8023`; branch deleted. Incident: while stashing generated usage-metrics files before a pull I dropped an unrelated pre-existing auto-stash (`pre-pull auto-stash 6196925`); recovered it via `git fsck` dangling commits and re-stored it (it held only stale generated dashboard files). Lesson: check `git stash list` before `stash drop`.
- 2026-09-08: **Phase 5 built + tested: narrative layer + Word/PDF export.** commercial skill v16 (`narrative-lint`, `narrative-stamp`, `export`; `_lint_markdown_text` factored out of `lint_edition` so report and narrative share one lint; sidecar schema 1.6 `narrative` status; `exports/` gitignored), project-console 1.67.0 (exec-summary panel, per-section folds, Generate/Regenerate, ⬇ Word / ⬇ PDF). Design decisions: (a) the narrative is a separate hash-pinned file, never edits to report.md — approved editions stay byte-identical and `check` stays green; (b) same claim lint for prose as for figures — the LLM may cite, never compute; (c) staleness is visible, not silent — re-answer flips the narrative to `stale` until regenerated; (d) synthesis is one call + one lint-guided retry, file kept either way with errors surfaced. Concurrency again: main moved to console 1.66.1 (ben/120) under this checkout; my bump placed as 1.67.0 above it.
- 2026-09-08: **Nav dropdown landed** — PR #185 merged to `main` as `8fa73a7` (project-console 1.66.0). User briefly floated a "Reports" topline with a summary landing page, then withdrew it ("business is fine") — no landing page built; noted as a possible future refinement.
- 2026-09-08: **Nav dropdown (user follow-up).** Replaced the three peer domain tabs with one "Business" dropdown (project-console 1.66.0). Mechanic worth remembering: the nav clips overflow, so an in-nav menu must be re-parented outside it and positioned `fixed` — same reason the hamburger lives outside the nav.
- 2026-09-08: **Landed.** Commit `b3f6d71` → PR #184 → merged to `main` as `2173a0d`; branch `ben/118-business-domains` deleted. Staged an explicit path list (excluded the sibling session's `tasks/ben/SECOPS.md`). Remaining: registry push (`/sync-skills push`) — deferred.
- 2026-09-08: Reference audit complete + all 8 findings fixed (see close-out todos). Decision: management-review obligations cite the QMS SOP, never an ISO 13485 clause — consistent with `docs/external/standards/README.md`'s deliberate exclusion of QMS-level standards.
- 2026-09-08: Main-session follow-through on Finance: `corpus refresh commercial/internal-fleet` (884 rows) + `internal-complaints` (435 rows) → new `2026-09-08` snapshots, zero-row deltas (deterministic generators); `answer FQ-03` re-pinned → lint 0/0; `render` finance. Second console gap fix from FQ-03: a null measure in a `paired-bars` point (no plan row for a category) raised in `abs()` → coerced to a gap; regression added. All `/domains/finance/FQ-*` 200; full console suite 90/90. Management Review Pack re-assembled for 2026-09-08 over commercial,finance,manufacturing: 30 answered (all commercial), 20 not in pack (finance + manufacturing have drafts only — approval is the human step that moves them in).
- 2026-09-08: **Phase 2 (Finance) complete via subagent** — see ticked todos. `check` fails only on pre-existing stale commercial pins (ten datasets, 43–48 d).
- 2026-09-08: **Concurrency incident.** A second Claude session (task ben/119) worked in this same checkout on `main` and merged PR #182 (`2662b4e`), which committed the project-console `VERSION`/`SKILL.md` files while they carried my uncommitted 1.63.0 bump — it re-bumped them to 1.64.0 for its own change, so "1.64.0" on `main` currently lacks the domain code. Resolution: my changelog entry renumbered to **1.65.0** and placed above 1.64.0; `VERSION`/`SKILL.md` set to 1.65.0; commercial README pairing note updated. Side benefit: that PR also fixed the pre-existing `test_setup_cli_catalog` Jama failure. At commit time stage only this task's paths (never `tasks/ben/119-*` or `SECOPS.md`).
- 2026-09-08: Console fix surfaced by MQ-01: a null `y` in a trend line (month with no rev B lots at test) 500ed `_timeseries_geometry`; now treated as a gap (x slot kept, nothing drawn) — regression in `test_commercial_domains.py`. All four `/domains/manufacturing/MQ-*` views 200.
- 2026-09-08: **Phase 3 (Manufacturing) complete via subagent** — see ticked todos; `check` fails only on pre-existing stale commercial pins (43–48 d). No adversarial-verify / red-team / code-review records filed (not in scope).
- 2026-09-08: **Phase 4 built (uncommitted)** while the domain subagents run: engine `dependents` + `pack` actions, Action template + install, console Workflows D3–D6 with the Management Review Pack detail view, `docs/project/management-review/README.md`. Decision: the pack is an *assembly* (copies verdicts/expectations from linted editions, cites edition + report path, computes nothing, names no standards clauses — no ISO 13485 distillation exists under `docs/external/standards/`, so clause citations stay `[VERIFY]`). Decision: CI never approves; it only refreshes snapshots and drafts.
- 2026-09-08: **Phases 2 + 3 launched as two parallel subagents** (Finance: 4 corpus generators under `corpus/finance/`, `docs/project/finance/` catalog FQ-01..10 with FQ-01/03/06/08 implemented; Manufacturing: 4 generators under `corpus/manufacturing/`, `docs/project/manufacturing/` catalog MQ-01..10 with MQ-01/03/05/08 implemented). Main session proceeds with Phase 4 (workflow automations) in non-overlapping files (`.github/workflows/`, console `workflows/catalog.py`).
- 2026-09-08: **Phase 1 complete (uncommitted).** Engine + console generalized to N business domains; Commercial byte-compatible. Test: 19/19 commercial suites. Decision: URL scheme `/domains/<slug>` with permanent 307 from `/commercial…` (chosen over a catch-all `/<slug>` that would shadow later-registered routers, and over dual-decorator registration that would keep two URL schemes alive).
- 2026-09-08: Task created. Plan discussed with the user (three-domain generalization + finance + manufacturing + HLS workflow automations); user approved with defaults (domains, Economics stays in Commercial, three peer tabs).
