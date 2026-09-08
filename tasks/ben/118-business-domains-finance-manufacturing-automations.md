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
| Tab layout | **Three peer tabs** | Matches existing nav pattern (one tab per discovered sidecar); no sub-tab machinery to build |

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

### Close-out
- [x] READMEs: `docs/project/README.md` (+ `finance/`, `manufacturing/`, `management-review/` rows) and `docs/project/corpus/README.md` (+ `finance/`, `manufacturing/` rows), each with a changelog row
- [x] Reference audit (subagent, `/reference-audit init` + `fan-out`) over the five new READMEs → reports under `docs/_analysis/pca-device/*-readme-references-audit/`: 57 sound / 4 unverified / 4 broken. All 8 fixed: `approval.yml` wording ×2, roadmap-question wording ×2, MQ-10 consumer, hw rev C attribution, FQ-05 consumer, and the two ISO 13485 `[VERIFY]` tags repointed to the QMS SOP `GL-SOP-QM-002` Management Review (§6.1 cadence, §6.2 inputs) — the standards README deliberately excludes ISO 13485 as QMS-level, so the SOP is the citable source
- [ ] Commit → PR → merge per git-workflow rule; update this doc + index

## Open Questions

- None. The ISO 13485 question resolved: cite `GL-SOP-QM-002` (QMS SOP) rather than a clause; 21 CFR 820 verified sound in both tiers by the reference audit. Remaining `[VERIFY]` tags are the expectation thresholds inside the catalogs (stand-ins, `validated: false`) — those are for the CFO / VP Quality personas to ratify, by design.

## Resume

**Activation:** `bash .claude/hooks/task-activate.sh add <SESSION_UUID> 118`

**Reference audit:** launched as a subagent over the five new READMEs (finance, manufacturing, corpus/finance, corpus/manufacturing, management-review) per `/reference-audit` `init` + `fan-out`; findings land under `docs/_analysis/`. Apply or defer its fixes before commit.

**In-flight artifacts (uncommitted, 2026-09-08):** `.claude/skills/commercial/{SKILL.md,README.md,scripts/commercial.py}`, `.claude/skills/project-console/{VERSION,SKILL.md,README.md,console/app.py,console/commercial/{loader,router}.py,console/web/templates/{_base,commercial_index,commercial_view,commercial_data}.html,tests/test_commercial_domains.py}`, `docs/project/commercial/.console/commercial-index.json` (re-rendered, schema 1.5). Console restarted on :8765 with the new code.

**First action on resume:** if uncommitted — read the reference-audit report(s) under `docs/_analysis/`, apply fixes, then commit ONLY this task's paths (see the concurrency note: never `tasks/ben/119-*`, `tasks/ben/SECOPS.md`) on a branch → PR → merge. Then `/sync-skills push` for `commercial` (v15) and `project-console` (1.65.0) — deferred, registry-facing.

## Economics

_By-hand person-hour estimate per the effort-estimation rubric (`usage-metrics` skill). All phases estimated (Phases 2-3 were subagent-built; their by-hand baseline is what a finance/QE analyst + developer would have taken). `agentic_hours` = supervised human attention so far (planning discussion + review), refreshed at checkpoint._

```json
{
  "economics": {
    "method_version": 1,
    "method_ref": ".claude/skills/usage-metrics/references/effort-estimation-rubric.md",
    "agentic_hours": {
      "min": 2,
      "max": 4
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
      }
    ]
  }
}
```

## Changelog

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
