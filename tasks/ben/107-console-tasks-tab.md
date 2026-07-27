# 107 — Console Tasks Tab (port from spec-gaming sister project)

**ID**: 107
**Created**: 2026-07-20
**Status**: Complete
**Created By**: Ben Xavier
**Owner**: Ben Xavier
**Priority**: Medium

---

## PERMANENT RULES (do not remove)

This task document is the **session-recovery point** for this work. If the current session drops, is compacted, or ends, the next session must be able to load **this file alone** and continue where we left off. That is only possible if the doc is kept current in-flight.

1. **Update at every meaningful checkpoint (HARD RULE).** After each meaningful unit of work — a converted/adopted doc, a committed change, a launched batch, a completed phase, a decision, a discovered blocker, a design pivot — update this task doc: tick the relevant Todo checkbox, add a dated Changelog line naming the concrete artifact (commit SHA, file path, decision, blocker), update any progress counts/tables in Goals. **When you tick a Todo off, fill/refresh the matching `## Economics` entry in the same edit** per the rubric.
2. **Phase-end batching is OK; drift-batching is not.** Write the update at the phase boundary, before the next phase starts — never "at the end of the session."
3. **A commit is not a substitute.** Git history records code; this doc records the project narrative.
4. **Resume-ready before any session boundary.** The doc must contain: (a) what was completed with concrete artifacts, (b) in-flight work status, (c) priority-ordered next steps with file paths, (d) open questions, (e) the exact `/task` activation command.
5. **Capture strategy + lessons as they happen** — in-flight, in this doc, with the HTML-comment markers.
6. **Estimation provenance.** `## Economics` follows `.claude/skills/usage-metrics/references/effort-estimation-rubric.md` (`method_ref` names it). Read the rubric before adding/refreshing estimates.

Success test for this doc: a fresh Claude session, given only this file, can re-enter the work without asking the user "what were we doing?"

## Goals

Port the sister project's (spec-gaming) console **Tasks tab** into this project's registry skills — an *activity summary* view (what's moving, what's open, recent highlights, effort picture), deliberately not a full task list.

Reviewed source (spec-gaming, diverged project-console fork):
- `tasks/task-summary.json` — derived artifact; console is a pure consumer
- `.claude/skills/task/scripts/task_summary.py` (276 L, stdlib-only) + `### summary [--window N]` action — script derives data; **Claude composes the narrative/watch lines** and stamps them via `--narrative`/`--watch` (script never writes prose; preserves previous prose when omitted)
- `console/tasks_view/{loader,router}.py` + `tasks_view.html` — freshness aging (fresh ≤7d / aging ≤21d / stale), rollup stats, narrative panel, Open-now cards, Recently-shipped timeline, economics footnote

Required adaptations (sister fork ≠ our registry conventions):
1. **Project-agnostic categories (HARD RULE).** Their category keywords ("tetris", "unity"…) are hardcoded in the skill — project leakage. Ours: generic defaults in the script + optional project-owned override at `tasks/task-summary-config.json` (JSON, because the script stays stdlib-only — no PyYAML at bare `python3`; project.yml would need a YAML parser). Icons ride in the same config and are emitted into the JSON (`category_icons`) so the console has no hardcoded map either.
2. **Changelog parsing.** Their docs use `| date | msg |` table rows; ours use `- YYYY-MM-DD: …` bullets. Script must parse both.
3. **Doc links.** Their template links `/documents#path=…`; our explorer resolves `/documents/view/<path>` and `tasks` is already a tree root (`documents/tree.py ROOT_NAMES`) — link accordingly.
4. **Template conventions.** Ours: `{% block head %}` inline styles w/ theme vars + `{% block content %}`; theirs uses separate CSS files + different base blocks. Port `md_inline` (their `mdlite.py`) into the tasks_view router (tiny, display-only).
5. **Nav.** Discovery-gated (`request.state.tasks_nav` middleware flag, like Metrics) + `ic-tasks` icon in the `_base.html` sprite.

## Todos

- [x] Phase 1 — task skill v34: `scripts/task_summary.py` (adapted: bullet+table changelogs, generic categories + `tasks/task-summary-config.json` override, `category_icons` in JSON, Abandoned status class) + `### summary` action + Supporting Files row + frontmatter v34 + README v34 changelog
- [x] Phase 2 — project-console 1.41.0: `console/tasks_view/{__init__,loader,router}.py`, `tasks_view.html` (theme-var CSS, `/documents/view/` links, `md_inline` ported into router), app.py nav flag + router, `_base.html` `ic-tasks` icon + gated nav item, SKILL.md "Topline section: Tasks", README changelog
- [x] Phase 3 — seeded `tasks/task-summary-config.json` (5 medtech categories + icons); generated `tasks/task-summary.json` (107 tasks, 10 open, 12 closed/30d, econ rollup over 11 in-doc blocks); composed + stamped narrative and watch (ben/046 filing-entity gap)
- [x] Phase 4 — console restarted; `/tasks` + `/tasks/summary.json` 200, cards/timeline/narrative render, task-doc links redirect 307→200 into the explorer, no regressions on `/`, `/setup`, `/metrics`, `/documents`
- [x] Phase 5 — pushed: PDLC_DEMO PR #155 (`3859857`); `/sync-skills push` → hitachi PR #282 merged (`e9a4a05`), clone ff'd, sync branch cleaned, drift 0 both sides

<!-- LESSONS LEARNED: skills, sync -->
**Lesson — porting from a diverged sister fork is adaptation, not copying (category: skills/registry-sync).** The sister project's console is a fork with different template blocks, nav machinery, and CSS conventions, and its `task_summary.py` had project vocabulary ("tetris", "unity") hardcoded into a registry-shared skill — exactly the project-leakage failure the sentinel-blocks guardrail describes. **Why:** a fork's code embeds its project's conventions invisibly; a byte-copy would have imported both the leakage and a changelog-format mismatch (their task docs use `| date | msg |` tables, ours use `- date: …` bullets — their regex would have silently found zero activity here, an empty-but-plausible Tasks tab). **How to apply:** before porting anything from a sister fork, diff the *conventions* (data formats, template contracts, config homes), route project-specific vocabulary into project-owned data files (here `tasks/task-summary-config.json`), and verify the port against real project data — the "12 closed in last 30d" number was the tell that parsing actually worked.
<!-- /LESSONS LEARNED -->

<!-- LESSONS LEARNED: skills, contracts -->
**Lesson — derived-artifact fields that reach a UI need a normalization contract at the producer AND a clamp at the consumer (category: skills/contracts).** The Tasks tab shipped rendering `open_tasks[].status` raw; task authors decorate status lines freely ("Not Started — captured during ben/045 …"), and one long decoration rendered as a giant nowrap chip overlaying the next column. **Why:** free-text doc fields have no length/shape guarantee, and a `white-space: nowrap` badge is the worst consumer for one; testing only against well-formed rows missed the decorated form that already existed in the tree. **How to apply:** when a script projects doc fields into a JSON artifact, normalize enum-like fields to a canonical closed set at the producer (decoration → a separate clamped note field, contract stated in the script docstring), AND give the rendering element a defensive max-width/ellipsis so a stale or foreign artifact still can't break layout. Fixed in task v35 + project-console 1.53.0.
<!-- /LESSONS LEARNED -->

## Open Questions

- Should the economics footnote also read the usage-metrics v12 `economics.json` sidecar (where ben/100 migrated 94 retrospective blocks)? v1 reads task-doc blocks only — the Metrics ▸ Value tab already owns the full economics story. Deferred.

## Resume

### In-flight artifacts

- **Uncommitted** (nothing committed by Claude): task skill (`scripts/task_summary.py`, SKILL.md v34, README v34 row); project-console (`console/tasks_view/*`, `tasks_view.html`, `app.py`, `_base.html`, SKILL.md, README, VERSION 1.41.0); project data (`tasks/task-summary-config.json`, `tasks/task-summary.json`); this task doc + index row.
- Console **running** on http://127.0.0.1:8765 with the Tasks tab live and verified.
- Pre-existing dirty files from other tasks (102/103/104/106 artifacts) also in git status — keep this task's commit scoped.

### First action on resume

1. If pushing: commit only the files listed above → branch → PR → auto-merge per `.claude/rules/git-workflow.md`; then consider `/sync-skills push` for both skills (task + project-console) to hitachi.
2. Regenerate the summary after any board change: `/task summary` (narrative preserved unless re-composed).
3. Activation: `bash .claude/hooks/task-activate.sh add <SESSION_ID> 107`

## Economics

_By-hand person-hour estimate per the effort-estimation rubric (`usage-metrics` skill)._

```json
{
  "economics": {
    "method_version": 1,
    "method_ref": ".claude/skills/usage-metrics/references/effort-estimation-rubric.md",
    "agentic_hours": {"min": 0.5, "max": 1.0},
    "todos": [
      {
        "todo": "task skill v34 summary action (adapted script + SKILL.md + README)",
        "personas": ["rd-lead"],
        "manual_hours": {"min": 4, "max": 7},
        "confidence": "med",
        "basis": "adapting a reviewed 276-LOC reference implementation (parsing changes, config override, docs) — software anchor low end + judgment; port, not greenfield"
      },
      {
        "todo": "console tasks_view section (loader/router/template/nav) at 1.41.0",
        "personas": ["rd-lead"],
        "manual_hours": {"min": 4, "max": 8},
        "confidence": "med",
        "basis": "port of a reviewed view to different template/theme conventions + docs; software anchor low end + judgment"
      },
      {
        "todo": "status-chip overflow fix: producer normalization contract (task v35) + consumer clamp (console 1.53.0) + regen/verify",
        "personas": ["rd-lead"],
        "manual_hours": {"min": 1.5, "max": 3},
        "confidence": "high",
        "basis": "defect fixing anchor ~4-6h/defect scaled down — small UI defect, two-file fix + contract doc + verification (Capers Jones per-defect, low end)"
      },
      {
        "todo": "project data: category config, summary generation, narrative/watch, verification",
        "personas": ["rd-lead", "program-manager"],
        "manual_hours": {"min": 1.5, "max": 3},
        "confidence": "high",
        "basis": "config authoring + a PM-style month-in-review paragraph + route smoke; judgment"
      }
    ]
  }
}
```

## Changelog

- 2026-07-27 (close): **Task Complete.** Project landing PR #155 (`3859857`); registry landing hitachi PR #282 (`e9a4a05`); sync-log entry written; drift 0. Economics reconciled at completion (`agentic_hours` 0.5–1.0 supervised).
- 2026-07-27 (later): project-console **1.53.1** — styled hover tooltip on the status chip (user follow-up: the clamp can ellipsize on narrow screens). CSS-only bubble via `::after content: attr(data-full)` showing full status + note on hover and keyboard focus; ellipsis moved to inner `.tk-chip-tx` span (chip's `overflow: hidden` would have clipped the pseudo-element); native `title` removed to avoid double tooltip. Verified live: data-full carries ben/046's full text, tabindex present.
- 2026-07-27: **Status-chip overflow bug fixed both-layers** (reported via screenshot: ben/046's decorated status rendered as a giant pill over the timeline). Producer: task v35 — `open_tasks[].status` contractually canonical, decoration → clamped `status_note`. Consumer: project-console 1.53.0 — chip renders leading clause only, full text on hover, `max-width: 11em` + ellipsis; note shown in card meta. Also reconciled project-console SKILL.md frontmatter (lagged at 1.41.0 vs VERSION 1.52.0) → 1.53.0. Regenerated summary (all 10 open statuses assert canonical; narrative preserved); console restarted and verified via HTML chip extraction.
- 2026-07-20: All four build phases delivered in one session. task skill v34 (`scripts/task_summary.py` + `summary` action); project-console 1.41.0 (`console/tasks_view/` + `tasks_view.html` + nav); project data seeded (`tasks/task-summary-config.json`, `tasks/task-summary.json` with composed narrative + ben/046 watch). Verified live: `/tasks` 200 with cards/timeline/narrative, doc links resolve via explorer redirect, sibling routes regression-free. Uncommitted; remaining = push + upstream sync push.
- 2026-07-20: Task created; spec-gaming source reviewed (task_summary.py, tasks_view module, template, mdlite) and the five required adaptations recorded in Goals.
