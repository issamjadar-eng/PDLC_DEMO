# 030 — Sync-Skills Pull (2026-04-27) + Post-Update Migrations

**ID**: 030
**Created**: 2026-04-27
**Status**: In Progress
**Created By**: Ben Xavier
**Owner**: Ben Xavier
**Priority**: High

---

## Goals

Bulk pull from hitachi `731b09f` and execute all required post-update migrations identified by the Project Impact Analysis (sync-skills v3 Step 5b).

- Pull all `UPSTREAM_NEWER` + `UPSTREAM_ONLY` files (excluding `__pycache__`/`.pyc`)
- Restore `agents/project-secops.md` as a symlink (upstream converted it to symlink)
- Run `/task setup` — task v23 migration (uninstall deprecated capture hooks)
- Run `/secops setup` — secops v3+ git-identity alignment
- Update `project.yml` `security.approved_skills` — add `dhf-manifest`, `web-control`
- Run `/project-console sync` + restart console — scaffold 1.4.1 → skill 1.7.6 (six minor versions)
- Record sync in `.claude/sync-log.md`

## Sync Result

- Hitachi HEAD before: local checkout already at `731b09f` (origin/main)
- Files pulled: **284**
  - 1 LOCAL_ONLY → already merged via symlink restore (`agents/project-secops.md`)
  - 33 UPSTREAM_NEWER (modified existing skills)
  - 250+ UPSTREAM_ONLY (new files / new skills)
- Files skipped (LOCAL_ONLY): `skills/secops/scripts/resolve_user.py`, `skills/task/hooks/{capture-check,capture-signals}.sh` (latter two deprecated by task v23)
- Files filtered: `__pycache__/*.pyc` (build artifacts)

### New skills installed

| Skill | Purpose |
|---|---|
| `dhf-manifest` | 4-tier DHF deliverable catalog — sibling to `/trace-matrix` |
| `web-control` | Chrome lifecycle + DevTools-Protocol Python lib |
| `docx`, `pdf`, `pptx`, `xlsx` | Anthropic-style office-format skills |

### Existing skills updated

| Skill | Highlights |
|---|---|
| `digest` v6→v8 | Non-blocking SessionStart fetch, sync-check notice, `.state/` relocation |
| `docflow` v31 | 24 doc-type-packs, mermaid + table rule packs, 3 new agents |
| `lessons` v2 | Doc-only state-path update |
| `project-console` 1.4.1→1.7.6 | Overview section, Unified Assistant drawer, tiered grounding (Phase 1+2), footnote citations, sticky auto-scroll, configurable grounding roots, browsable skill-library roots |
| `secops` v4→v5 | Resolver consolidation; BP/Changelog moved to README |
| `strategy` v8→v14 | Shared scope for all per-DHF domains, sub-DHF→DHF terminology, `<task_folder>/NNN` task-ref format, domain registry from `project.yml` |
| `task` v23 | Retired UserPromptSubmit + Stop capture hooks; setup migration cleans them up |
| `agents/project-secops.md` | Now a symlink → `skills/secops/agents/project-secops.md` |

## Post-Update Migrations Executed

See Changelog at bottom for per-step status.

<!-- LESSONS LEARNED: sync, registry-hygiene, hooks -->

### Lessons Learned

- **Symlinks in registry require explicit handling.** The pull-file primitive does a literal `cp`, which on a symlinked file copies the symlink target string as content (or follows the symlink, depending on cp behavior). Restoring `agents/project-secops.md` required deleting the copied content file and creating the symlink manually. Worth fixing in `sync.sh pull-file` or filing as a bug under task ben/029. Why: upstream converted the agent into a symlink; sync's check-script also misreports symlinked files as perpetually UPSTREAM_NEWER (Bug B in task ben/029) — that pattern repeats here.
- **`approved_skills` allowlist drifts silently when new skills appear upstream.** Each pull that introduces new skills requires a project.yml diff to reconcile. A `/best-practices` check enforces this; running it after every sync would catch it earlier. How to apply: after any `/sync-skills pull` that adds new skills, immediately edit `project.yml` `security.approved_skills` before the next session-start audit.

## Outcome

All four required migrations executed successfully:

| # | Action | Result |
|---|---|---|
| 1 | `/task setup` v23 migration | Removed `.claude/hooks/capture-{signals,check}.sh` symlinks; jq-scrubbed `.claude/settings.json` (0 capture references remaining); deleted orphan source files `.claude/skills/task/hooks/capture-{signals,check}.sh` |
| 2 | `/secops setup` git-identity alignment | `resolve_user.py --align-git` reports `already_aligned: true` (`ben.xavier@globallogic.com` matches roster); permissions allow list re-merged (71 → 71, idempotent) |
| 3 | `project.yml` allowlist | Added `dhf-manifest` and `web-control` to `security.approved_skills` (alphabetical insertion) |
| 4 | `/project-console sync` + restart | Scaffold rolled 1.4.1 → 1.7.6 (no project-owned drift); console restarted via `tools/project-console/start.sh`; `GET /` and `GET /overview` return 200; Overview tile rendered |

Sync log entry written at `.claude/sync-log.md` (`2026-04-27 — pull` section).

Remaining `UPSTREAM_NEWER` flag on `agents/project-secops.md` is the documented sync-skills check-script symlink quirk (see task ben/029 Bug B) — content is byte-identical via the symlink target. Remaining `LOCAL_ONLY` flags on `skills/task/hooks/capture-*.sh` will clear after the deletion is committed (currently tracked-deleted in git's index).

## Changelog

- 2026-04-27: Task created. Pull executed (284 files), sync log written, all four post-update migrations executed and verified, console restarted and smoke-tested.
