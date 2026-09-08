# 120 — Workbench Validation: User-Story Need Format

**ID**: 120
**Created**: 2026-09-08
**Status**: In Progress
**Created By**: Ben Xavier
**Owner**: Ben Xavier
**Priority**: Medium

---

## PERMANENT RULES (do not remove)

This task document is the **session-recovery point** for this work. If the current session drops, is compacted, or ends, the next session must be able to load **this file alone** and continue where we left off.

1. **Update at every meaningful checkpoint (HARD RULE).** After each unit of work, tick the Todo, add a dated Changelog line naming the concrete artifact, refresh progress and the matching `## Economics` entry in the same edit.
2. **Phase-end batching is OK; drift-batching is not.**
3. **A commit is not a substitute.**
4. **Resume-ready before any session boundary.**
5. **Capture strategy + lessons as they happen.**
6. **Estimation provenance.** `## Economics` follows `.claude/skills/usage-metrics/references/effort-estimation-rubric.md`.

**Resume command**: `bash .claude/hooks/task-activate.sh add <SESSION_ID> ben/120`

## Goals

Follow-on to ben/119. Rewrite the workbench user-need register (WUN-01…16) into an explicit user-story form and make the form a checked contract of the `workbench-validation` skill:

> As a `<role>`, I need the workbench to `<outcome the role can observe>`, so that `<purpose>`.

Decided with the user 2026-09-08: connector is "so that"; the statement is **composed from structured fields** (`role`, `need`, `so_that`) by the renderer, never hand-written as one sentence, so the runner can check that every need carries a purpose.

<!-- LESSONS LEARNED: process, concurrency -->
- **Two sessions in one clone.** A version bump written by regex on a shared skill overwrote a sibling task's uncommitted bump in the working tree (1.66.0 → 1.64.1) for a few minutes. When another session is active in the same clone, read the current value immediately before writing it, never from memory of an earlier read, and diff against HEAD before committing shared skill files.

<!-- STRATEGY CONTENT: testing, tool-validation, user-needs, coverage-honesty -->

### D2 — Coverage is decided by a dry run, not by the existence of a script

**Decision.** A need is declared `coverage: tests` only after its candidate executable has been run in this project and its exit-code contract confirmed. Scripts that judge **project data state** (snapshot freshness, package contents) rather than tool behaviour are not scripted cases: their result flips with the data, so they go in as process-control and their current result is recorded as a project-content anomaly with an owner.

**Why.** Of the four `tests` candidates the scrub proposed, two failed the dry run for reasons unrelated to the tool: the knowledge-pack template does not validate here (no pack exists), and the commercial check correctly reports 43-day-old snapshots. Declaring them `tests` would have produced a FAIL that says nothing about the workbench, or a NO-EVIDENCE that drags the verdict to PARTIAL.

<!-- STRATEGY CONTENT: testing, tool-validation, user-needs, authoring-format -->

### D1 — Needs are user stories composed from structured fields

**Decision.** Each need in `validation.yml` carries `role`, `need` (the outcome, phrased to follow "I need the workbench to…", free of mechanism) and `so_that` (the purpose). The renderer composes "As a {role}, I need the workbench to {need}, so that {so_that}." into the report, sidecar (`statement`) and console. The runner refuses a schema ≥ 1.2 manifest where a need lacks any of the three, and warns when a `need` already starts with "As a" / "I need" (double wording).

**Why.** The previous register was role-perspective but implicit: only one of sixteen needs said "I need", and none carried a purpose. The purpose clause is what a reviewer uses to judge whether the mapped evidence really assures the need, and what the risk tier should follow from. Composing from fields keeps the register machine-checkable and lets a customer QMS with a different sentence shape get it from a transform (the skill's data-first rule) instead of a rewrite.

**What it commits us to.** "The workbench", never "the system" (in this repo "the system" reads as the device). The outcome stays observable by the role; mechanism remains only in `implemented_by`. The plan's §4 register table is regenerated from the manifest, not hand-kept.

## Todos

- [x] Manifest: 16 needs rewritten as `need` + `so_that`; schema 1.2
- [x] Runner: `lint_needs()` — missing role/need/so_that is an error on schema ≥ 1.2 (warning below); duplicated story wording is a warning
- [x] Renderer: `need_statement()` composes the story (role lower-cased mid-sentence unless acronym); report §2 single Need column; sidecar `statement`/`so_that`; sidecar schema 1.2
- [x] Skill templates (manifest + plan), SKILL.md, README changelog + Best Practices row; workbench-validation 4 → 5
- [x] Project plan §4 regenerated from the manifest (7 columns incl. WUN-16); README changelog rows
- [x] Console needs row shows the composed statement; project-console 1.66.1 (1.65/1.66 landed from ben/118 meanwhile — my first bump to 1.64.1 briefly overwrote 1.66.0 in the working tree; corrected before commit)
- [x] Register scrub: fork surveyed 35 skills + hooks against the 16 needs; 8 coordinated chains had zero coverage (external publishing, data→answer→console, filing-package gates, capture→harvest, session-start truth, cost attribution, grounding, the validation tooling itself). Integrated as 13 new needs (WUN-17…29) — coverage decided per dry-run, not per proposal:
  - `tests`: WUN-17 public-doc strip (TC-22, positive + malformed-block negative, verified exit 3); WUN-20 submissions transmit gate (TC-25, declared project-instance positive on `qsub`; `510k` exits 2 = precondition, not run); WUN-26 validation tooling (TC-26 → new 21-case suite); WUN-27/28 from the WUN-06 split (TC-07/09/18 → 27, TC-08 → 28)
  - `process-control` (honest): WUN-18 knowledge packs (no pack in this project; the template pack fails validate here), WUN-19 commercial gate (`commercial.py check` exits 1 on **stale 43-day pins** — a real content finding recorded as an anomaly for the commercial owner, not a tool defect), WUN-21 harvest, WUN-22 session start, WUN-23 cost attribution, WUN-24 docflow fidelity, WUN-25 grounding (TC-04 also mapped), WUN-29 frozen documents (inert hook named)
  - Rewrites: WUN-06 narrowed to dhf-manifest coverage; WUN-15 loses the freeze half; WUN-10 T3 → T2
- [x] workbench-validation `tests/test_runner_renderer.py` — 21 cases (the tool had been an untested checker itself)
- [ ] Run of record on a clean tree (manifest changed → re-pin) → PASS
- [ ] Commit → PR → merge; registry sync branch (hitachi #301) updated

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

- 2026-09-08: Task created after discussing the need format with the user; D1 recorded (user-story form, "so that", structured fields composed by the renderer).
- 2026-09-08: Format change implemented end to end (manifest 1.2, runner lint, renderer composition, templates, plan §4 regenerated, console row). User added a scrub ask: review needs per skill and as coordinated skills for missing needs — research fork launched; integration pending its report.
- 2026-09-08: Scrub integrated — 29 needs / 24 cases; plan §4 regenerated; two anomalies (checkers gap amended; commercial stale pins recorded). D2 recorded (coverage decided by dry run). Next: debug run, commit, run of record, PR, registry branch update.
