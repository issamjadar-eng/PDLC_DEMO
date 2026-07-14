# 101 — Registry Sync 2026-07-14 + Statusline Install + Submissions VERSION Fix

**ID**: 101
**Created**: 2026-07-14
**Status**: In Progress
**Created By**: Ben Xavier
**Owner**: Ben Xavier
**Priority**: Medium

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

_Routine registry-alignment + tooling maintenance, three units:_

- Pull the 2026-07-14 hitachi registry updates into PDLC_DEMO (change-control v0.14.0, submissions v6, digest hook fix, tracker render.py) — done before task creation, recorded in `.claude/sync-log.md`.
- Install the usage-metrics team status line in this project (it landed in the skill at v4 but `setup` had last been run pre-v4, so `.claude/statusline.sh` + the `statusLine` settings block were missing).
- Fix the submissions skill version mismatch (VERSION file `5` vs SKILL.md frontmatter `6`) locally and push the one-line fix upstream to hitachi.

## Todos

- [x] `/sync-skills pull` — 18 files from hitachi `761afd3` (12 UPSTREAM_ADVANCE + 6 new), impact analysis + sync-log entry
- [x] Re-run `usage-metrics` setup → `.claude/statusline.sh` symlink + `statusLine` block in `.claude/settings.json`; smoke-tested the script; setup also refreshed `.github/workflows/usage-metrics-aggregate.yml`
- [x] Fix `.claude/skills/submissions/VERSION` `5` → `6` locally
- [x] Push the VERSION fix upstream to hitachi as a sync PR — [hitachi PR #266](https://github.com/GlobalLogic-a-Hitachi-Company/hitachi/pull/266), branch `sync/pdlc-demo-submissions-version-2026-07-14`, awaiting review (PR-only default; not merged)
- [x] Record push in `.claude/sync-log.md`
- [ ] Merge hitachi PR #266 (or wait for review), then `git -C ../hitachi pull --ff-only` — until merged, local VERSION shows LOCAL_AHEAD in sync checks (protected, won't be clobbered)
- [ ] Commit session changes in PDLC_DEMO when user asks (nothing committed yet)

## Changelog

- 2026-07-14: Task created (retroactively covers the sync pull + statusline install done just before the task gate fired on the VERSION edit).
- 2026-07-14: Sync pull recorded in `.claude/sync-log.md` (hitachi HEAD `761afd3`); statusline installed + smoke-tested (`[Fable 5] · $1.23` render OK).
- 2026-07-14: Reviewed the submissions version mismatch — evidence: README changelog v6 row (2026-07-07) + SKILL.md frontmatter `version: 6` (both from PR #264) vs `VERSION` file `5` (last touched PR #262) → correct value is 6. Fixed local `.claude/skills/submissions/VERSION`; pushed upstream as hitachi PR #266 (commit `2381d8a`, awaiting review); push logged in `.claude/sync-log.md`; hitachi checkout returned to `main`.

## Economics

_By-hand person-hour estimate, **filled at checkpoint** per the effort-estimation rubric (`usage-metrics` skill). Empty until the first completed todo is estimated; an empty `todos` list is ignored by the aggregator._

```json
{
  "economics": {
    "method_version": 1,
    "method_ref": ".claude/skills/usage-metrics/references/effort-estimation-rubric.md",
    "agentic_hours": null,
    "todos": [
      {
        "todo": "sync-skills pull (18 files) + three-way analysis + per-skill impact review + sync-log entry",
        "by_hand_hours": [0.75, 1.5],
        "persona": "devops-engineer",
        "retrospective": false
      },
      {
        "todo": "diagnose missing statusline (pre-v4 setup) + idempotent setup re-run + smoke test",
        "by_hand_hours": [0.25, 0.75],
        "persona": "devops-engineer",
        "retrospective": false
      },
      {
        "todo": "review VERSION-vs-frontmatter mismatch via upstream git history, fix locally, branch + commit + upstream PR #266 + sync-log entry",
        "by_hand_hours": [0.25, 0.5],
        "persona": "devops-engineer",
        "retrospective": false
      }
    ]
  }
}
```
