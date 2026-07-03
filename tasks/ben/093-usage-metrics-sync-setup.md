# 093 — Usage-Metrics Skill: Registry Merge + Full Setup

**ID**: 093
**Created**: 2026-06-23
**Status**: Complete
**Created By**: Ben Xavier
**Owner**: Ben Xavier
**Priority**: Medium

---

## PERMANENT RULES (do not remove)

This task document is the **session-recovery point** for this work. If the current session drops, is compacted, or ends, the next session must be able to load **this file alone** and continue where we left off. That is only possible if the doc is kept current in-flight.

1. **Update at every meaningful checkpoint (HARD RULE).** After each meaningful unit of work, update this task doc: tick the relevant Todo, add a dated Changelog line naming the concrete artifact (commit SHA, file path, decision, blocker), update progress counts.
2. **Phase-end batching is OK; drift-batching is not.**
3. **A commit is not a substitute.** Git records code; this doc records the narrative.
4. **Resume-ready before any session boundary.**
5. **Capture strategy + lessons as they happen** using `<!-- STRATEGY CONTENT -->` / `<!-- LESSONS LEARNED -->` blocks.

## Goals

Land the new **`usage-metrics`** skill (cross-team Claude Code token-usage + cost telemetry; git-as-aggregator, no shared server, no LLM in the data path) into PDLC_DEMO, and wire the **full team telemetry loop**.

The skill is the user's own work, authored from the **arthrex-pccp** project, sitting on hitachi branch `sync/arthrex-pccp-usage-metrics-console-2026-06-23` (commit `e23c6d1`) with **open PR #231** — not yet on `origin/main`. Per user decision (2026-06-23): **merge PR #231 to registry main first**, then pull into this project; **full setup scope** (hooks + auto-publish + GitHub Action + project-console Metrics view).

The commit bundles two things:
1. **New skill** `skills/usage-metrics/**` (SKILL.md, README, 4 scripts, 2 hooks, 3 templates incl. the GitHub Actions workflow).
2. **Modifies the existing `project-console` skill** — adds a **Metrics view** (`console/metrics/` router+loader, `metrics_view.html`, `metrics.js`, app.py wiring, version bump) that consumes the skill's `usage.json`.
3. Minor touches: `shared/scripts/resolve_user.py`, `task/rules/scratch-and-tmp.md`.

## Todos

- [x] Read `usage-metrics` SKILL.md; evaluate scope + setup footprint
- [x] Confirm registry state (open PR #231; branch pushed; not on origin/main)
- [x] Get user decision: merge-to-main-then-pull + full setup
- [x] Merge hitachi PR #231 → origin/main (squash, delete branch) — merge commit `94653c7`
- [x] Fast-forward local hitachi checkout to main; clean up sync branch — HEAD `94653c7`, sync branch deleted
- [x] `/sync-skills pull` — pulled 23 files (usage-metrics 11 new + project-console metrics 5 new/5 mod + shared/resolve_user.py + task/scratch-and-tmp.md); all byte-identical to hitachi main `94653c7`
- [x] Update `project.yml`: added `usage-metrics` to `security.approved_skills` (project-console already listed)
- [x] Run `/usage-metrics setup` (full loop) — 2 hooks symlinked+registered (SessionStart refresh / SessionEnd publish), `usage_metrics:` block appended, `**/_usage-metrics/**` corpus-excluded, pricing.json seeded, `.github/workflows/usage-metrics-aggregate.yml` installed, tools/ symlinks created
- [x] **Fixed slug bug in `collect.py`** — primary slug did `/`→`-` only, missing the `_` in `PDLC_DEMO` (real transcript dir is `-Users-...-PDLC-DEMO`). Changed to replicate CC's encoding (all non-alphanumeric → `-`) + kept legacy `/`-only as secondary. **Affects any underscore/dot-named project → push upstream.**
- [x] Smoke test: `collect` wrote 6 sessions for ben (611 msgs; 151k in / 639k out / 187.6M cache-read); `aggregate` wrote `index.html` + `usage.json` + `2026-06.md`. Pipeline functional.
- [x] Run `/project-console sync` (1.25.0→1.28.0; "No changes" — app imports live from skill pkg, tool tree holds only config/launch) + restarted via `start.sh`. Metrics view live on **:8765** — `/`, `/metrics`, `/metrics/data` all 200; renders Member 1 (6 sessions, 611 msgs, $139.50 opus-4-8). The `:8081` listener is an unrelated local MLX server, not a console.
- [x] Record sync-log entry
- [ ] Checkpoint
- [ ] Push (NEEDS USER OK — nothing committed yet): (a) project changes (PDLC_DEMO PR), (b) `collect.py` slug fix upstream to hitachi

<!-- LESSONS LEARNED: tooling, skill-portability -->
**Lesson — transcript-dir slug must convert ALL non-alphanumerics, not just `/`.** `usage-metrics/collect.py` located `~/.claude/projects/<slug>` by `str(project_root).replace("/", "-")`. Claude Code's actual encoding replaces every non-alphanumeric char (`/`, `_`, `.`) with `-`, so `…/PDLC_DEMO` → `-Users-…-PDLC-DEMO` (the `_`→`-`). The `/`-only slug missed it, and the `cwd`-match fallback was too weak (checks only the first parseable row of the first jsonl per dir). **Why it matters:** any project whose folder name contains `_` or `.` silently collects nothing — a portability landmine in a registry skill. **How to apply:** when reconstructing a tool's path-derived identifier, replicate the tool's *exact* slug rule (here: all non-alphanumeric → `-`), don't approximate with a single separator. Fix lives in `.claude/skills/usage-metrics/scripts/collect.py:transcript_dir`; push upstream so all consuming projects get it.
<!-- /LESSONS LEARNED -->

## Resume

### In-flight artifacts (uncommitted — user controls commits)
- **Pulled (23 files, byte-identical to hitachi `94653c7`):** `.claude/skills/usage-metrics/**` (new), `.claude/skills/project-console/{SKILL.md,README.md,VERSION,console/app.py,console/metrics/**,console/web/static/metrics.js,console/web/templates/{metrics_view.html,_base.html}}`, `.claude/skills/shared/scripts/resolve_user.py`, `.claude/skills/task/rules/scratch-and-tmp.md`.
- **Setup-generated:** `.claude/hooks/usage-metrics-{refresh,publish}.sh` (symlinks) + `.claude/settings.json` (2 hook registrations); `project.yml` (`usage_metrics:` block + `approved_skills` += usage-metrics + corpus exclude); `tools/usage-metrics/{pricing.json,*.py symlinks}`; `.github/workflows/usage-metrics-aggregate.yml`; `tasks/ben/_usage-metrics/2026-06/*.json` (6 session records); `tools/usage-metrics/{index.html,usage.json,2026-06.md}`.
- **Local edit (push-upstream candidate):** `.claude/skills/usage-metrics/scripts/collect.py` slug fix — now DIVERGES from hitachi main (was byte-identical at pull, then fixed).
- **Registry:** hitachi PR #231 merged → main `94653c7`; local hitachi checkout on main, sync branch deleted.
- Console running on :8765 (bg).

### First action on resume
- Decide pushes: project PR for PDLC_DEMO, and a `/sync-skills push` of the `collect.py` slug fix to hitachi (affects all underscore/dot-named projects). Nothing is committed yet.

## Resume

### In-flight artifacts
- _none yet_

### First action on resume
- Merge hitachi PR #231, then pull.

## Changelog
- 2026-07-03: Status changed to Complete. Economics lives in the v12 sidecar (`tools/usage-metrics/economics.json` → `ben/093`, agentic 6 h).
- 2026-07-03 (checkpoint recovery — no transcript): Reconciled doc vs git. The "In-flight (uncommitted)" state and "First action: decide pushes" below are **superseded — everything shipped**: usage-metrics skill + tooling + console view + hooks + CI merged via PR #67 (`de118ef`); the per-session fast-forward/gitignore fix via PR #72 (`386211e`); the sync-log v5 push record via PR #73 (`1b915eb`); telemetry data committed in `518ceb1`. The `collect.py` slug fix and project changes both landed, and usage-metrics has since advanced to **v12** upstream (pulled 2026-07-03). **Do not re-push.** This task pre-dates 096–100 and its deliverable is live; Status left `In Progress` pending user confirmation to close.
- 2026-06-23: Task created. Evaluation done; user chose merge-to-main + full setup. Starting PR #231 merge.
- 2026-06-30: **Fixed the recurring fast-forward/merge abort caused by per-session usage data** (surfaced repeatedly, incl. during ben/095's merge). Root cause: `collect.py` writes `tasks/<tf>/_usage-metrics/YYYY-MM/<id>.json` into the working tree (untracked on a feature branch); `publish.py` then commits the same file to the shared branch via an isolated worktree → file becomes **tracked on the branch but untracked locally** → next `git pull --ff-only`/`gh pr merge` that updates the branch aborts with "untracked working tree files would be overwritten." NOT a CI-vs-local conflict — CI (`aggregate.py`) only writes `tools/usage-metrics/`, never the per-session JSONs. Fix (usage-metrics v4→v5): `setup` now **git-ignores** `tasks/*/_usage-metrics/` + `**/_usage-metrics/`, and `publish.py` **force-adds** (`git add -f`) so it still reaches the branch. Ignored files are silently superseded on pull → abort impossible; already-tracked files stay tracked; worktree-publish still never touches the working tree. Also updated the auto-loaded `scratch-and-tmp.md` rule row (was "Committed & tracked" → "git-ignored locally, force-published"). **Propagation:** publish.py rides `/sync-skills pull`; the `.gitignore` line is installed by `setup`, so sister projects must **re-run `/usage-metrics setup`** after pulling. Ran setup on this project (added the gitignore). Deliberately reverted the status-line wiring setup also does (team-shared settings.json — out of scope for a bugfix). Files: `usage-metrics/scripts/{publish,setup}.py`, `usage-metrics/{SKILL.md,README.md}`, `task/rules/scratch-and-tmp.md`, project `.gitignore`.

