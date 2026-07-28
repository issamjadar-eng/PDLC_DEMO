# 110 — Workbench Validation

**ID**: 110
**Created**: 2026-07-27
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
   - **when you tick a Todo off (or add/restructure Todos), fill/refresh the matching `## Economics` entry in the same edit** — the by-hand person-hours that unit would have taken, ranged + persona-tagged, per the rubric (if `## Economics` is present / usage-metrics is installed). **Checking the box is the estimate trigger** — don't defer it to a later checkpoint.
2. **Phase-end batching is OK; drift-batching is not.** Planned phases (e.g., "finish Phase 2, then log the whole phase at once") are a legitimate checkpoint — writing once per phase is fine if the phase is bounded and the write happens **at the phase boundary, before the next phase starts**. What's not OK: accumulating updates in your head across arbitrary work, waiting for "end of the session," "after the push," or the user to ask. By then a crash or context-trim has lost the state. Rule of thumb: if you can't name the specific upcoming checkpoint where you'll write the update, write it now.
3. **A commit is not a substitute.** Git history records code; this doc records the project narrative — what was done, why, what's left, what surprised us.
4. **Resume-ready before any session boundary.** Before recommending a fresh session, marking Complete, or ending work, the doc must already contain: (a) what was completed this session with concrete artifacts, (b) status of any in-flight work and temp artifacts, (c) priority-ordered next steps with file paths, (d) open questions blocking progress, (e) the exact `/task` activation command to resume.
5. **Capture strategy + lessons as they happen.** If the session produces option comparisons, scope/boundary decisions, architectural pivots, non-obvious insights, or corrected assumptions, write them into the appropriate section **in-flight** — not just in chat. Harvesting skills can only surface what was written.
6. **Estimation provenance (if `## Economics` is present).** This doc's `## Economics` block is the by-hand person-hour estimate, built per the effort-estimation rubric at `.claude/skills/usage-metrics/references/effort-estimation-rubric.md` (owned by the `usage-metrics` skill). To **add or refresh** an estimate on resume — even without loading the task skill — read that rubric first for the anchors, personas, and JSON schema; the block also carries a `method_ref` naming it. Skip silently if `usage-metrics` isn't installed. Point to the rubric, never copy it into this doc.

Success test for this doc: a fresh Claude session, given only this file, can re-enter the work without asking the user "what were we doing?"

## Goals

_MedTech-style validation of the project's AI workbench — the `.claude/` toolchain (skills, agents, hooks, scripts, rules) used to author and manage design-control artifacts. In MedTech, tools used to design and document control artifacts require validation (ISO 13485 QMS-software validation, CSA-style risk-based assurance). Today the workbench has scattered validation-ish assets (per-skill tests, best-practices audit, secops checks, hooks) but no unified structure._

- Design a right-sized, risk-based validation framework for the workbench, grounded in project sources (`docs/external/`, `docs/internal/source-md/`) — CSA-style, honest about LLM non-determinism.
- Produce **three visible components**: (1) workbench user needs / intended-use requirements, (2) an executable test/assurance run that maps to those needs, (3) a single generated **validation report** that rolls needs × tests × results into a fitness-for-use statement.
- Surface all three in the project console under **Settings → Workbench Validation**, re-runnable periodically.
- Demo posture: everything carries the demo banner — illustrative of the method, not a real regulatory claim.

## Todos

_Actionable work items. Check off as completed._

- [x] Phase 0 — Research: agent fan-out (asset inventory, console contract, regulatory grounding) and synthesize the approach into this doc
- [x] Phase 1 — Author workbench user needs + validation plan artifact (WUN register, risk tiers, assurance mapping)
- [x] Phase 2 — Build the test/assurance runner that executes existing deterministic checks + records results as JSON
- [x] Phase 3 — Build the validation report generator (needs × tests × results → report markdown + console sidecar JSON)
- [x] Phase 4 — Console: add Settings → Workbench Validation sub-section rendering the three components
- [x] Phase 5 — Run end-to-end, verify in console (screenshot-verified), update this doc
- [x] Push to main + registry skill sync

## Open Questions

- ~~Where should the validation artifacts live long-term?~~ Resolved: `docs/project/workbench-validation/` (validates toolchain, not device — outside DHF trees).
- ~~Reusable skill or project-local tooling?~~ Resolved: registry-shareable skill `workbench-validation` (project data stays in the project manifest).
- Follow-up candidates (upstream fixes surfaced by the validation run, each a possible new task): (1) tracker test fixture drift (`test_script_emits_bundle_for_existing_row` — row 'DHF' not in inventory); (2) change-control `test_c_jira_renderer_graceful_degrades_on_auth_failure`; (3) secops CFG-PROJECT-YML docstring false-positives; (4) task-gate suite exits 0 on failures; (5) push `workbench-validation` skill + console changes to the hitachi registry after local merge.

## Resume

### In-flight artifacts (all UNCOMMITTED — nothing committed or pushed this session)
- New skill: `.claude/skills/workbench-validation/` (SKILL.md v1, README, VERSION, scripts/run_validation.py, scripts/render_report.py, templates/×2).
- Project artifacts: `docs/project/workbench-validation/` (README, validation-plan.md, validation.yml, results/×3 runs + latest.json, validation-report.md, .console/workbench-validation-index.json). `docs/project/README.md` row+changelog.
- Console (project-console skill tree, v1.57.0→1.58.0): `console/setup/loader.py` (`load_workbench_validation` + `workbench` key), `console/setup/router.py` (`POST /setup/workbench/render`), `console/web/templates/setup_view.html` (nav link + `sec-workbench` panel + `suWbRender()` JS), VERSION, SKILL.md (frontmatter + Setup table row), README changelog.
- `project.yml`: `workbench-validation` added to `security.approved_skills`.
- Console restarted on :8765 and verified: `/setup/data` carries `workbench` key; `/setup#workbench` renders tiles + WUN register + tests table (screenshot-verified); `POST /setup/workbench/render` re-runs and returns verdict. Latest run: 13/16 PASS, 3 triaged FAILs, overall FAIL (honest).

### First action on resume
- If the user approves push: full git-workflow sequence (branch → PR → auto-merge → delete). Everything is built and verified; nothing to redo.
- Activation: `bash .claude/hooks/task-activate.sh add <SESSION_UUID> 110`

## Phase 0 — Research Findings

### Console integration contract (agent report, verified against SKILL.md + code)

- **All console behavior lives in the skill tree** — `.claude/skills/project-console/console/` is imported via PYTHONPATH by `tools/project-console/run.sh` (SKILL.md L186). Never edit `tools/project-console/` for UI; it's project-owned config/launcher only (SKILL.md L138–146).
- **Settings sub-section pattern** (no registry; conventional): in `console/web/templates/setup_view.html` add (a) sidebar nav link `<a href="#workbench" data-sec="workbench">` near L218–222 (conditionally shown like Environment), (b) panel `<section class="su-sec" id="sec-workbench" data-title="Workbench Validation">` (pattern-match Environment section L950–1028: status tiles, list, empty state, action button). Generic hash-router JS (L1037–1054) picks it up automatically.
- **Data**: add `load_workbench_validation(repo_root)` in `console/setup/loader.py` (defensive, degrade-to-empty per loader docstring L20–25), keyed into `load_setup()` return (L1041–1055).
- **Sidecar convention**: producer skill writes `docs/project/<domain>/.console/<name>-index.json` (`schema_version: "1.0"`); console is a pure consumer, computes nothing. Report markdown referenced by repo-relative path, rendered via existing documents renderer.
- **Optional render endpoint**: `POST /setup/workbench/render` in `console/setup/router.py` shelling to producer skill's render script (mirror gap_analysis `skill_render_script`, loader.py L84–87).
- **Ship discipline**: bump `.claude/skills/project-console/VERSION` (currently 1.57.0) + SKILL.md frontmatter, add row to Setup table (SKILL.md L334–357). Restart via `/project-console start` (`--reload` does NOT watch the skill package); verify at `http://127.0.0.1:8765/setup#workbench` + key in `GET /setup/data`.

### Existing validation-asset inventory (agent report)

**What exists:** 14 of 37 skills have `tests/` (project-console 13 py incl. e2e, change-control 12 py + 1 sh, sync-skills 6 sh, advisors 3 py, writing-well 2 py + evals, trace-matrix 2 py, plus jira-pull / md-deck / medtech-docs / tracker / task / dhf-manifest / web-control / explain). ~20 deterministic checker/lint scripts (docflow fidelity, regulatory-authoring lint, commercial dossier lint, submissions 4 linters, secops `audit_artifacts.py` static scanner with `--json` + exit-1-on-Critical/High, dhf-manifest validate/coverage, tracker validate, skill-creator quick_validate + trigger-eval harness). 2 hard-blocking hooks (task gate, docflow conversion block) + ~12 advisory hooks incl. secops 16-check SessionStart assert (JSON output, cached to SECOPS.md). 12 auto-loaded rules (prose, unenforced). `project.yml` security allowlists. best-practices audit = markdown report from registry manifest + 31 per-skill README Best Practices tables (JSON only as internal transport, not persisted).

**Gaps (the validation framework's raison d'être):**
1. No CI/gate runs any of it — all manual/local; the 2 GH workflows only rebuild file-locator index + usage aggregate.
2. No unified test runner (only writing-well has `run_tests.sh`); no pytest.ini/conftest anywhere.
3. ~23 skills with no tests, incl. the auditors themselves (best-practices, secops).
4. Load-bearing checkers with no regression tests pinning them.
5. VERSION tracking inconsistent (5 skills have VERSION files; mixed semver/integer).
6. Hooks mostly untested (only task gate + web-control lifecycle).
7. Rules unenforced/untested.
8. `change-control/hooks/pre_tool_use_frozen.py` is a live STUB (exits 0 — designed control currently inert).
9. No `project.yml` validation/quality block declaring what must pass — no single source of truth for a validation report to cite.
10. best-practices produces no persisted machine-readable artifact (not trendable as validation evidence).

### Regulatory grounding (agent report)

- **Strongest in-project anchor: GL-WI-SW-004 §8 "Tool Validation (IEC 62304 §6.1)"** — `docs/internal/source-md/software-cybersecurity/software-vv-wi.md` L136–145, L162: tools impacting a result validated for intended use via (1) documented intended use, (2) risk assessment ("what could the tool get wrong and how would that affect a release decision?"), (3) risk-scaled evidence, (4) configuration baseline; revalidate on tool upgrade / use-case change. Backed by GL-SOP-QM-001 L53/L131 (Part 11 "validated systems" hook) + GL-SOP-QM-006.
- **Not distilled in-project (stay [VERIFY]-flagged):** ISO 13485 §4.1.6 text (deliberately org-level, per `docs/external/standards/README.md` L54), FDA CSA guidance, 21 CFR Part 11 source text, GAMP 5. Also: GL-WI-SW-004's own "IEC 62304 §6.1" citation deserves a reference-audit (likely wrong clause).
- **Model:** 3 risk tiers — T1 High (output enters DHF/submission or gates record integrity: authoring skills, regulatory lint, docflow, task-gate + conversion-block hooks), T2 Medium (advisory detection + config control: audits, sync-skills, secops), T3 Low (display/telemetry: console views, digest, usage-metrics). Assurance depth scales per tier (scripted tests → seeded-error spot checks → verified-by-use).
- **LLM non-determinism handled honestly:** deterministic parts (hooks, scripts, lints, renderers) get scripted repeatable tests; LLM-driven parts get process controls (mandatory human review, deterministic gates wrapped around them, grounding rules, git/PR audit trail) — never fake expected-output test cases for prose generation. Config baseline = skill-tree git SHA + model ID; model change is a first-class revalidation trigger.
- **14 candidate workbench user needs (WUN-01…WUN-14)** covering authoring, audit, hooks/gates, renderers, console, sync/registry, security posture, cross-cutting traceability.
- **Demo posture:** banner + "illustrative of method only" disclaimer; conclusions phrased "would support a fitness-for-use determination"; package lives outside controlled DHF trees.

### Synthesized approach (DECIDED)

<!-- STRATEGY CONTENT: architecture, workbench tool-validation framework design -->
**Architecture decision — three components, one producer skill, console as pure consumer:**

1. **New project skill `workbench-validation`** (`.claude/skills/workbench-validation/`) — the producer. Owns: the validation model (SKILL.md), `scripts/run_validation.py` (executes the manifest), `scripts/render_report.py` (results → validation-report.md + console sidecar JSON). Created via skill-creator conventions; added to `project.yml security.approved_skills`.
2. **Project-owned validation artifacts at `docs/project/workbench-validation/`** (durable docs home, outside controlled DHF trees — validates the workbench, not the device):
   - `validation-plan.md` — intended-use classes, risk tiers, WUN register (WUN-01…14), assurance mapping, revalidation triggers. Component 1 (user needs).
   - `validation.yml` — declarative manifest mapping WUN → executable test cases (existing skill tests/lints/audits + coverage class for process-control-only needs). Project data stays project-local (sentinel guardrail: never bake project data into registry skill files).
   - `results/<timestamp>-run.json` — raw run evidence. Component 2 (tests).
   - `validation-report.md` — generated single report: needs × tests × results → per-WUN verdict + fitness-for-use statement + known anomalies (incl. honest LLM non-determinism section). Component 3.
   - `.console/workbench-validation-index.json` — console sidecar (`schema_version: "1.0"`).
3. **Console**: `load_workbench_validation()` in `console/setup/loader.py` + nav link/panel `#workbench` in `setup_view.html` (pattern: Environment section) + `POST /setup/workbench/render` shelling to the skill's runner. VERSION bump 1.57.0 → 1.58.0.

**Manifest v1 test inventory (executable evidence, mapped to WUNs):** task gate bash suite (WUN-07), docflow conversion-block check (WUN-08), medtech-docs sentinel renderer pytest (WUN-09), regulatory-authoring/writing-well lint self-tests (WUN-04), advisors/trace-matrix/tracker/md-deck/jira-pull/change-control/project-console pytest suites, sync-skills bash suites (WUN-11), dhf-manifest discovery test (WUN-06), secops `audit_artifacts.py --json` (WUN-12), skill-creator `quick_validate.py` sweep over all SKILL.mds (WUN-13 config baseline). WUNs with no executable evidence (WUN-02/03/05/14 → process controls / exploratory) are reported as such — coverage class `process-control`, never a fake PASS.
<!-- /STRATEGY CONTENT -->

<!-- STRATEGY CONTENT: architecture, validation data model refinements (user feedback round) -->
**Refinements decided with user (2026-07-27/28):**
1. **Role-based user needs.** Every WUN carries `role:` and is written in the role's plain language — the outcome required, never the implementation. Mechanism moved to `implemented_by:` (traceability info only, may change without the need changing). This matches classic user-needs discipline: the user doesn't know how it's implemented.
2. **Evidence of record = full execution logs.** Beyond results JSON, the runner persists per-case transcripts at `results/<run-id>/<TC-ID>.log`: execution header (command, cwd, env changes, timestamps, exit code, judgment rule, status) + complete ANSI-stripped output. Report and console link each log.
3. **Data-first / customer-QMS portability (user's framing).** Canonical layer is machine-readable (validation.yml, run JSON, evidence logs, sidecar); the markdown report is ONE projection. A customer QMS needing its own report format gets a new transform over the same data — validation is general-purpose, formatting is downstream.
4. **Placement.** Console nav label is just "Validation" (docs keep the full "Workbench Validation" name). Generated outputs live in `tools/workbench-validation/` (tool-output convention, like `tools/usage-metrics/`); authored plan + manifest stay in `docs/project/workbench-validation/`. `tools/workbench-validation` added to console.yaml `grounding.extra_roots` so logs/report resolve in the Documents viewer.
<!-- /STRATEGY CONTENT -->

<!-- STRATEGY CONTENT: testing, validation reviewer-readability + reproducibility (user feedback round 2) -->
**Round-2 refinements decided with user (2026-07-28):**
1. **UUT (unit under test)** — `test_cases[].uut:` names the component(s) a case actually runs against (multiple allowed; `all-skills` sentinel); the runner pins each named skill to the version exercised (`uut_versions` from the run-start baseline) — stamped into results, evidence-log headers, report, sidecar, console column.
2. **Reviewer-friendly test cases** — titles/description/approach rewritten in plain language for non-specialists; console test rows click-to-expand (description, approach, pass rule, command, links); report gains "What each test case checks (for reviewers)".
3. **TC hyperlinks** — TC ids link to the actual test source (derived from cmd; env-flag args like `--project` excluded — that mistake initially pinned the console's whole `.venv`); `.claude/skills` added to console.yaml `grounding.extra_roots` so sources resolve in Documents.
4. **Validation setup record** — every run records configuration under test + operator (git user/email, OS user, hostname, OS) + invocation source (`--invoked-via cli|console`; console endpoint passes `console`) + timestamps. Report §1 is now the setup record; console shows a setup-record line.
5. **Test-artifact pinning** — the run folder receives byte copies of `validation.yml` and each case's test source (`pinned/<TC-ID>/`, `__pycache__` excluded), sha256-manifested in the run JSON — so the exact tests executed stay reviewable across validation runs as skills evolve.
<!-- /STRATEGY CONTENT -->

<!-- LESSONS LEARNED: process -->
- The workbench already had ~14 test suites + ~20 deterministic checkers but zero unified entry point, zero persisted machine-readable results, and zero CI wiring — validation-shaped assets accumulate naturally per-skill, but the "single validation report" view only exists if something owns the aggregation. Design the aggregator early.
- Live stub found: `change-control/hooks/pre_tool_use_frozen.py` exits 0 (designed control, currently inert) — a validation run must surface designed-but-inert controls as findings, not count them as controls.
<!-- /LESSONS LEARNED -->

## Economics

_By-hand person-hour estimate, **filled at checkpoint** per the effort-estimation rubric (`usage-metrics` skill). Empty until the first completed todo is estimated; an empty `todos` list is ignored by the aggregator._

```json
{
  "economics": {
    "method_version": 1,
    "method_ref": ".claude/skills/usage-metrics/references/effort-estimation-rubric.md",
    "agentic_hours": {"min": 0.5, "max": 1.5},
    "todos": [
      {
        "todo": "Phase 0 — research fan-out (asset inventory, console contract, regulatory grounding) + synthesized approach",
        "personas": ["quality-engineering", "rd-lead", "regulatory-affairs"],
        "manual_hours": {"min": 12, "max": 24},
        "confidence": "med",
        "basis": "audit/gap-assessment anchor (~1-2 focused auditor-days for 37-skill toolchain inventory) + requirements/arch decomposition share for the validation model + QMS-source review (GL-WI-SW-004, Part 11 hooks); scope fuzzy pre-build"
      },
      {
        "todo": "Phase 1 — validation plan + 15-WUN register + folder README",
        "personas": ["quality-engineering", "regulatory-affairs"],
        "manual_hours": {"min": 8, "max": 16},
        "confidence": "med",
        "basis": "document authoring anchor 3-7 hr/page (regulated high end) on ~3 pages of dense plan content incl. intended-use classes, tiering, and need statements grounded in QMS WI"
      },
      {
        "todo": "Phase 2 — validation runner (manifest schema + executor + baseline capture) incl. suite triage",
        "personas": ["rd-lead", "vnv-lead"],
        "manual_hours": {"min": 10, "max": 20},
        "confidence": "med",
        "basis": "software anchor ~20-25 LOC/day low end for ~250 LOC stdlib runner would overstate; sized as small-module + test-integration debugging across 16 heterogeneous suites (env sensitivity, exit-code masking, dep resolution)"
      },
      {
        "todo": "Phase 3 — report/sidecar renderer + manifest authoring (16 TCs) + 3 triage cycles",
        "personas": ["rd-lead", "quality-engineering"],
        "manual_hours": {"min": 8, "max": 16},
        "confidence": "med",
        "basis": "software anchor for ~300 LOC renderer + test-engineering share for the TC catalog mapping and failure triage/dispositioning"
      },
      {
        "todo": "Phase 4-5 — console Settings sub-section (loader + panel + endpoint + JS) + version discipline + end-to-end verify",
        "personas": ["rd-lead"],
        "manual_hours": {"min": 6, "max": 12},
        "confidence": "med",
        "basis": "software anchor: ~200 LOC across loader/router/template in an existing FastAPI/Jinja codebase incl. contract reading, restart/verify cycle, and docs (SKILL table row + changelog)"
      },
      {
        "todo": "Feedback round — role-based WUN rewrite, per-case evidence logs, tools/ output relocation, nav label",
        "personas": ["rd-lead", "quality-engineering"],
        "manual_hours": {"min": 5, "max": 10},
        "confidence": "med",
        "basis": "requirements-rewrite of 15 needs (role voice) + ~120 LOC evidence-log + path-relocation sweep across 10 files + re-verify cycle; document-authoring anchor for the register rewrite, software anchor for the rest"
      },
      {
        "todo": "Feedback round 2 — UUT + version pinning, reviewer-friendly cases (16 descriptions/approaches), TC source links, setup record, test-artifact pinning, UI fixes",
        "personas": ["rd-lead", "vnv-lead", "quality-engineering"],
        "manual_hours": {"min": 10, "max": 20},
        "confidence": "med",
        "basis": "test-engineering anchor for authoring 16 non-specialist case descriptions + ~250 LOC across runner/renderer/console (pinning w/ sha256 manifest, operator capture, expandable UI) + debug of source-detection over-pin + 3 verify cycles"
      }
    ]
  }
}
```

## Changelog

- 2026-07-27: Task created. Research fan-out launched (3 agents: .claude validation-asset inventory, project-console settings contract, MedTech tool-validation grounding).
- 2026-07-28: SHIPPED + SYNCED. PDLC_DEMO PR #168 merged (`29097d7`) — skill + project artifacts + console 1.58.0 (137 files). Registry sync: pulled writing-well v3→v5 + NEW public-doc skill (19 files, allowlisted); pushed workbench-validation v3 + project-console 1.58.0 as hitachi PR #290, squash-merged `933ffad`; drift 0 both directions. Sync-log + pulled files landed via PDLC_DEMO PR #169 (`cdd8a8b`). Post-merge stash-pop conflicts on 5 machine-generated files (usage-metrics telemetry/dashboard, console manifest) resolved to HEAD (generated state, hooks republish). 3 pre-existing stashes from earlier sessions left untouched. Task Complete.
- 2026-07-28: Feedback round 2 shipped (workbench-validation v3, console within 1.58.0): (a) UUT field per test case with version pinning (`task@35`, `project-console@1.58.0`…) across results/logs/report/sidecar/console; (b) reviewer-friendly test cases — plain titles + description/approach, console click-to-expand rows, report "What each test case checks" section; (c) TC ids hyperlink to test source (detect_source heuristic; fixed --project env-arg bug that pinned 1458 files incl. console .venv → 43 scoped files); (d) validation setup record per run (operator git/OS user + hostname + OS, invoked-via cli/console, timestamps) in report §1 + console setup-record line + log headers; (e) test-artifact pinning — manifest + per-case sources copied into `results/<run-id>/pinned/` with sha256 manifest; (f) Status/Time column-merge fix (widths + column-gap). Full re-runs verified; screenshots confirmed; log + source links resolve via Documents API. Still uncommitted.
- 2026-07-28: UI polish: WUN-register Need column now word-wraps (was ellipsis-truncated) — `setup_view.html` need cell `white-space:normal` + `overflow-wrap` + 18px right padding, rows top-aligned; screenshot-verified after restart.
- 2026-07-28: User-feedback round shipped: (a) role-based WUN register (`role:` + plain-language needs + `implemented_by:` traceability) across manifest/plan/report/sidecar/console; (b) per-case evidence logs (`tools/workbench-validation/results/<run-id>/<TC-ID>.log`, full transcripts + execution headers) linked from report + console tests table; (c) outputs relocated `docs/.../{results,.console,report}` → `tools/workbench-validation/` (authored plan+manifest stay in docs), console.yaml `grounding.extra_roots` += tools/workbench-validation; (d) console nav label → "Validation". workbench-validation skill v1→v2; console loader/template/SKILL/README amended within 1.58.0. Re-run verified: 13/16 PASS, 16 evidence logs, log resolution via Documents API 200, screenshot-verified. Still uncommitted.
- 2026-07-27: Phases 4–5 complete. Console Settings → Workbench Validation sub-section shipped in the project-console skill tree (1.57.0→1.58.0): `load_workbench_validation()` in `console/setup/loader.py` (defensive sidecar consumer + HEAD-vs-baseline staleness), nav link + `sec-workbench` panel in `setup_view.html` (status tiles, WUN register with verdict badges, test-results table, report/plan links via Documents tab, demo banner, Run-validation button), `POST /setup/workbench/render` in `router.py` (shells the skill runner; exit 1 = valid FAIL verdict, not HTTP error). SKILL.md Setup-table row + README 1.58.0 changelog + VERSION. `project.yml` approved_skills += workbench-validation. Console restarted + verified: `/setup/data` workbench key, page render screenshot, POST endpoint live re-run (13/16 PASS). All three components visible. NOT committed/pushed — awaiting user.
- 2026-07-27: Phases 1–3 complete. New skill `.claude/skills/workbench-validation/` (SKILL.md v1, README, VERSION, scripts/run_validation.py + render_report.py, templates/). Project artifacts: `docs/project/workbench-validation/` (README, validation-plan.md with 15-WUN register, validation.yml with 16 test cases, results/, generated validation-report.md + .console sidecar). `docs/project/README.md` structure row + changelog added. End-to-end runs: **13/16 PASS, 3 honest FAILs** all triaged in `known_anomalies` — TC-08 tracker `test_script_emits_bundle_for_existing_row` (row 'DHF' not in inventory — fixture drift), TC-10 change-control `test_c_jira_renderer_graceful_degrades_on_auth_failure`, TC-15 secops CFG-PROJECT-YML High false-positives (docstring mentions). Manifest fixes during bring-up: TC-09 needed `--with openpyxl` + deselect of `test_exec` (helper-name pytest collision); TC-16 exempts external office skills; TC-01 needs `env_unset: CLAUDE_SESSION_ID` + `pass_pattern` (suite exits 0 even with 29 failures — upstream fix candidate).
- 2026-07-27: Phase 0 complete — all 3 agent reports synthesized into this doc (§ Phase 0 — Research Findings + § Synthesized approach). Decisions: new `workbench-validation` producer skill; project artifacts at `docs/project/workbench-validation/` (plan+WUN register, validation.yml manifest, results/, generated report, .console sidecar); console Settings sub-section `#workbench` in project-console skill tree (loader + setup_view.html + render endpoint).
