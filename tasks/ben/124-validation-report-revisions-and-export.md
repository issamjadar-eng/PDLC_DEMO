# 124 — Workbench Validation: Report Revisions and Word/PDF Export

**ID**: 124
**Created**: 2026-09-09
**Status**: Complete
**Created By**: Ben Xavier
**Owner**: Ben Xavier
**Priority**: High

---

## PERMANENT RULES (do not remove)

This task document is the **session-recovery point** for this work. If the current session drops, is compacted, or ends, the next session must be able to load **this file alone** and continue where we left off.

1. **Update at every meaningful checkpoint (HARD RULE).** Tick the Todo, add a dated Changelog line naming the concrete artifact, refresh progress and the matching `## Economics` entry in the same edit.
2. **Phase-end batching is OK; drift-batching is not.**
3. **A commit is not a substitute.**
4. **Resume-ready before any session boundary.**
5. **Capture strategy + lessons as they happen.**
6. **Estimation provenance.** `## Economics` follows `.claude/skills/usage-metrics/references/effort-estimation-rubric.md`.

**Resume command**: `bash .claude/hooks/task-activate.sh add <SESSION_ID> ben/124`

## Goals

User ask (2026-09-09): in the console's Settings → Validation tab, (1) a **drop-down to pull any revision of the validation report** (any recorded run, not only the latest), and (2) an **export to Word / PDF** so users can download the report **with all artifacts and evidence sectioned**.

<!-- STRATEGY CONTENT: testing, tool-validation, evidence-packaging, console -->

### D1 — Every run is a rendered revision; the console selects, never computes

**Decision.** The runner (and a `render --all-runs` backfill) writes, per run, `results/<run-id>/validation-report.md` and `results/<run-id>/sidecar.json`, plus a `results/index.json` roster (run id, dates, verdict, summary, baseline, schema). Historical runs are re-rendered from their **pinned** manifest and run JSON by the current renderer and say so in their header. The console lists the roster in a drop-down and loads the chosen run's sidecar; it computes nothing.

### D2 — The export is a single sectioned package, produced by the owning skill through docflow

**Decision.** `export_package.py --run <id> --format docx|pdf|md` assembles one markdown package — cover + sign-off block, the report body, then appendices: A pinned manifest; B environment and deployment declaration; C protocols (written protocol, execution record, run evidence files); D per-case evidence logs (full transcripts); E pinned test-source inventory with sha256; F QMS coverage inventory — and converts it through docflow's `export_formal.py` (pandoc → LibreOffice), the project's sanctioned md → DOCX/PDF path. The console's Export buttons call the skill script and stream the file; the exported file is written under `tools/workbench-validation/exports/<run-id>/`.

**Why.** A validation record a reviewer can take out of the workbench has to carry its evidence, not links to it; and it has to be reproducible from the run's own pinned data. Routing conversion through docflow keeps one conversion pipeline and one set of document-quality gates.

## Todos

- [x] workbench-validation 8: `render_run()` + `write_runs_index()`; every run gets `results/<run-id>/validation-report.md` + `sidecar.json` (`revision` block) from its pinned manifest; `results/index.json` newest-first; `--all-runs` backfilled 9 historical runs (July runs without a pinned manifest are flagged as rendered from the live manifest); 29 renderer/runner tests green
- [x] `export_package.py` (md | docx | pdf via docflow `export_formal.py`) + 7 tests (docx/pdf executed with real converters); real export of the latest run: md 16k lines, docx 236 KB, pdf 5.4 MB with 45 evidence logs, 3 protocols / 25 run-evidence files, 39 pinned-source tables, coverage table; exports gitignored (regenerable); WUN-31/32 + TC-45/46
- [x] project-console 1.71.0 (another session had moved the version): revision drop-down (`/setup?run=<id>`, roster from `results/index.json` with derivation fallback), Export Word / PDF / Markdown buttons → `GET /setup/workbench/export?run=&format=` streaming the skill's output; Re-run on the latest revision only; 9 new tests (120 total)
- [x] Docs + landing: SKILL v8, README, plan §4a, folder READMEs, console README; commits `3c7445f` (feature) · run of record `run-20260909T060450Z` **PASS 42/47, 0 FAIL, 5 N/A; needs 31/32 + 1 N/A** → PR #204 merged (`2bcdec4`); registry hitachi #305 merged

## Economics

```json
{
  "economics": {
    "method_version": 1,
    "method_ref": ".claude/skills/usage-metrics/references/effort-estimation-rubric.md",
    "agentic_hours": null,
    "todos": [
      {"id": "revisions", "title": "Per-run revision rendering, runs index, all-runs backfill, tests", "hours_low": 4, "hours_high": 7, "persona": "senior-engineer"},
      {"id": "exporter", "title": "Sectioned validation package exporter (md/docx/pdf via docflow) with appendices A–F and tests", "hours_low": 8, "hours_high": 14, "persona": "senior-engineer"},
      {"id": "console", "title": "Console revision drop-down, export route/buttons, roster loader, 9 tests", "hours_low": 5, "hours_high": 9, "persona": "senior-engineer"}
    ]
  }
}
```

## Changelog

- 2026-09-09: Task created; D1/D2 recorded; contracts fixed for parallel build (per-run artifacts, runs index, exporter CLI, console route).
- 2026-09-09: Renderer revisions + index landed on disk and backfilled; manifest 32 needs / 47 cases; skill docs v8. Exporter fork and console fork running.
- 2026-09-09: Landed — PR #204 (`2bcdec4`) with run of record PASS 42/47; registry hitachi #305 merged. Task Complete.

<!-- LESSONS LEARNED: tooling, console -->
- **A running console can serve a new template against stale code.** uvicorn `--reload` watches its cwd only; the console package lives under the skill folder outside that cwd, so loader/router changes never hot-reloaded while Jinja templates did — the user saw no revision toolbar and no Export buttons although the code was merged. Fixed in the launcher (`--reload-dir "$SKILL_CONSOLE"`, project-console 1.71.1 via `scaffold.py sync`). Until a project re-syncs its launcher, "restart the console" is part of shipping any console code change.

## Resume / follow-up

Everything is on `main`. Follow-ups: port project-console 1.64.0 → 1.71.0 Settings → Validation changes (environment panel, binary verdicts, coverage panel, revision drop-down, export route) to the registry fork by hand; Appendix F (QMS coverage) is included only for the latest run because the coverage JSON is a single latest-run file — write it per run under `results/<run-id>/` if historical coverage is wanted; the three protocol execution records still carry "pending: BX" sign-off, and the exported package's sign-off table is blank by design.
- 2026-09-09 (later): User reported the changes not visible in the console — root cause the launcher's reload scope (see lesson); console restarted, launcher fixed in `scaffold.py` and rolled forward (`run.sh` now watches the skill package), project-console 1.71.1; live page verified: revision toolbar with 9 runs, 3 export links, Markdown export streams (765 KB, correct download header).
- 2026-09-09 (later): User: selecting a revision landed on Connectors. Cause: the selector navigated to `#sec-workbench` while the settings hash router prefixes `sec-` itself. Fixed (`#workbench`; router tolerates the prefixed form), project-console 1.71.2; verified live with `?run=run-20260908T200255Z` selected.
- 2026-09-09 (later): User: "FAIL · 32/43 PASS" reads as a contradiction. Label now verdict-first with counts spelled out ("FAIL — 32 passed, 5 failed, 2 not executed, 4 n/a of 43"); the literal "32/43 FAIL" was not used because 32 is the passed count. project-console 1.71.3.
- 2026-09-09 (later): User: export needs a progress popup. Export buttons now open a modal (spinner, run + format, elapsed timer, phase line for the PDF chain), fetch the package, trigger the download, and report filename / size / build time or the backend error; "Download again" link. project-console 1.71.4; template test added (121 tests).
