# secops — Design & Architecture

This document is not loaded by Claude during normal skill operation — it exists for human understanding.

For skill usage and instructions, see `SKILL.md`.

## Best Practices

<!-- Read by /best-practices skill to audit project setup -->

| Check | How to Verify | Severity |
|-------|--------------|----------|
| SecOps skill installed | `.claude/skills/secops/SKILL.md` exists | Required |
| project-secops agent present | `.claude/agents/project-secops.md` exists | Required |
| SessionStart security hook registered | `settings.json` `hooks.SessionStart` contains an entry pointing to `security-assert.sh` | Required |
| Permissions allow list present | `settings.json` has `permissions.allow` with ≥ 20 entries | Recommended |
| `project.yml` has security block | `project.yml` contains a top-level `security:` key | Required |
| SECOPS.md up to date | Every active team member has `tasks/{person}/SECOPS.md` with a timestamp younger than 7 days | Recommended |

## Changelog

- 5 (2026-04-23): **YAML-parser consolidation via `resolve_user.py`** (task ben/096). `hooks/security-assert.sh` no longer hand-rolls user-identity resolution — the ~50-line email-fallback loop + `yaml_task_folder_for` call for the current user are replaced by a single `python3 resolve_user.py` JSON call that returns `task_folder`, `name`, `email`, `github` at once. The `FULL_NAME` resolution block near the bottom (formerly 20 lines of back-scanning YAML) is now a one-line fallback since the JSON already carries the name. The `gh api /user` → `yaml_task_folder_for` path is kept as a legacy fallback (for clones that predate the resolver helper). `yaml_list`, `yaml_team_github`, and `yaml_task_folder_for` remain for the multi-user checks (4, 12, 13, 14, 15, 16) that iterate over the roster — the resolver only answers for the current user. Net: ~65 lines of bash YAML-parsing removed; correctness now defers to the tested Python resolver.
  **Post-update:** Hook is symlinked — v5 activates on next session. Behavior unchanged for resolvable users (both paths produce the same `TASK_FOLDER`). Users whose git email doesn't match the roster but whose `gh api /user` login does will still resolve via the legacy fallback path.
- 4 (2026-04-23): **Move BP/Changelog to README.md** (task ben/095). `## Best Practices` and `## Changelog` sections migrated from `SKILL.md` to this README so they don't load into Claude's context every time the skill triggers. `SKILL.md` now has one-line pointers to this file. No behavior change.
- 3 (2026-04-20): **Roster-driven git identity alignment.** Added `scripts/resolve_user.py` — parses `project.yml` `team.active[]`, matches the current git identity via four heuristics (email / single-member / name-fuzzy / `$USER`-matches-task_folder), and on `--align-git` writes repo-local `git config user.email` + `user.name` to the roster values. Added step 6 to `setup` to run the resolver with `--align-git`. Makes `project.yml` the source of truth for git identity on this clone, regardless of the user's global git config. Shared with the `digest` skill — its SessionStart hook uses the same helper to key its throttle state file on `task_folder` instead of raw email slug. Built under ben/020. LOCAL divergence; upstream push deferred.
  **Post-update:** Re-run `/secops setup` to align repo-local git config for this clone. The change is idempotent and only touches `--local` config (no impact on other projects).
- 2 (2026-04-16): **Cross-platform regex fix in `security-assert.sh`.** 25+ uses of `\s` in `grep` and `sed` patterns silently no-op on macOS — BSD regex engines don't interpret `\s` as a whitespace class, so every yaml-parsing helper (`yaml_val`, `yaml_list`, `yaml_team_github`, `yaml_task_folder_for`) returned empty strings, and the hook early-exited at line 176 (`[[ -z "$TASK_FOLDER" ]] && exit 0`). Net effect: **secops was a dead letter on macOS** — no team validation, no active-task gating, no SECOPS.md freshness check. Only Linux/WSL developers actually had security posture enforced. Fix: mass replacement of `\s` with the POSIX class `[[:space:]]` (works identically on both BSD and GNU regex). No behavior change on Linux. Discovered during task 067 cross-platform audit.
  **Post-update:** no user action needed. Hook is installed via symlink — v2 takes effect on next `SessionStart`.
- 1 (2026-04-12): Initial version. Packages `security-assert.sh`, `project-secops` agent, and canonical permissions allow list. `setup` action symlinks hooks, copies agent into `.claude/agents/`, registers SessionStart hook via `register-hook.sh`, and unions permissions into `settings.json`. Auto-discovered by `/medtech-docs init` Step 5. Created under task 049.
