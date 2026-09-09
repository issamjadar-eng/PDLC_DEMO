# 124 — Workbench Validation: Report Revisions and Word/PDF Export

**ID**: 124
**Created**: 2026-09-09
**Status**: In Progress
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
- [ ] `export_package.py` (md | docx | pdf via docflow) + tests; WUN-31/32 + TC-45
- [ ] project-console 1.68.0: run drop-down (`/setup?run=<id>`), Export buttons + `GET /setup/workbench/export`, tests
- [~] Docs: SKILL v8 (`export` action, artifact table), README changelog, plan §4a, folder README rows done; WUN-31/32 + TC-45/46 in the manifest (32 needs / 47 cases); console README + commit/PR/registry pending the forks

## Economics

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

- 2026-09-09: Task created; D1/D2 recorded; contracts fixed for parallel build (per-run artifacts, runs index, exporter CLI, console route).
- 2026-09-09: Renderer revisions + index landed on disk and backfilled; manifest 32 needs / 47 cases; skill docs v8. Exporter fork and console fork running.
