# `/digest` Skill — Design & Architecture

> Human-facing design document. Claude reads `SKILL.md` for action definitions and `scripts/*.py` for behavior — this file exists so a human reader can understand why the skill is shaped the way it is.

## Purpose

Two related artifacts from one git-log-driven core:

1. **Ephemeral daily briefing** — pushed into each user's session context at SessionStart, throttled to once per 12 hours per user. Helps team members start the day with an answer to "what happened since I was last here?" without having to read the whole git log.
2. **Persistent project `CHANGELOG.md`** — a curated reverse-chronological record of significant project activity, filed at repo root, written on demand.

## Design rationale

**Why two surfaces, one skill?**
The core work — reading `git log` since a cutoff, filtering by path + subject heuristics, grouping — is identical for both. Splitting them into two skills would duplicate the aggregation code and create two approval surfaces in `project.yml`. One skill with two actions keeps the code DRY and the namespace clean. See `SKILL.md` for the action definitions.

**Why mechanical and not LLM-summarized?**
Initial v1 runs at SessionStart on every session for every user, possibly multiple times per day per user. LLM summarization at that cadence would be wasteful. Path-based filtering and fixed-theme grouping produce a "good enough" digest at zero token cost. If it proves too dull in practice, a `--smart` flag can feed the same raw data into a subagent later without redesigning the skill.

**Why 12h throttle and not 24h?**
12h supports a mid-day check-in for someone who works off hours. The window is cheap to change — just edit the constant in `hooks/session-briefing.sh`.

**Why per-user (email-keyed) state instead of per-session?**
A 12h throttle tied to sessions would reset too often (every new terminal = new briefing). Tying it to email means each teammate sees the briefing once per window regardless of how they open sessions. The state file is `.state/briefing-last-shown-<email-slug>.txt` — per-project, gitignored (relocated from `.claude/state/` in ben/083 to escape Claude Code's `.claude/**` sensitive-file guard).

**Why include the current user's own commits in the briefing?**
Self-recall of yesterday's work is useful, and filtering them out adds surprise ("why did my commits disappear?"). The explicit design call (from task 019) is to show everyone, including you.

**Why `CHANGELOG.md` at repo root?**
Standard convention, well-understood by humans and tools. The reverse-chronological structure (newest first) is also well-understood, and finding the most recent `## YYYY-MM-DD HH:MM` header gives us a trivial since-cursor for incremental runs.

**Why a `medtech-docs`-owned template rather than a digest-owned one?**
`medtech-docs` already owns the full project-scaffold template library (`readme-*.md`, `standard-file.md`, etc.). Adding one more template next to them keeps the scaffold responsibility in one place. The digest skill references it by path but doesn't own it — consistent with `docflow` referencing `medtech-docs` templates during conversion flows.

## Architecture

```
.claude/skills/digest/
├── SKILL.md                     # action contracts, best-practices checks
├── README.md                    # this file
├── VERSION                      # semver
├── hooks/
│   └── session-briefing.sh      # SessionStart; resolves user, checks throttle,
│                                #   calls digest.py, writes state file
└── scripts/
    ├── digest.py                # daily-briefing aggregator (stateless; state
    │                            #   file is owned by the hook)
    └── build_changelog.py       # CHANGELOG.md builder; finds since-cursor
                                 #   from last dated header
.claude/skills/medtech-docs/templates/
└── changelog-project.md         # seed template used by /digest setup

.state/                          # gitignored (project root)
└── briefing-last-shown-<slug>.txt
```

**State** is minimal:
- One per-user throttle file (`briefing-last-shown-<slug>.txt`) — contents are the last-emitted ISO timestamp, also used as `--since` for the next digest
- The `CHANGELOG.md` itself is its own state — the latest `## YYYY-MM-DD HH:MM` header is the since-cursor for the next `/digest log`

**No `digest.yml`** in v1. Significance rules live in `build_changelog.py` as a constant. Keeping them in-code avoids the drift surface a config file would introduce; if per-project overrides become a frequent ask, v2 introduces the config.

## Future directions (not in v1)

- `--smart` flag on `daily` to feed the raw digest through a subagent for an LLM-polished briefing (opt-in, token cost acknowledged)
- `digest.yml` project config for overriding significance rules and "pay attention" paths
- Optional team email summary pushed via a Stop hook on specific days (weekly rollup)
- `/digest status` reporting per-user throttle timestamps (helps debugging why a briefing didn't fire)
- Push to hitachi medtech-docs as v18 for the `changelog-project.md` template (and potentially the digest skill itself as its own registry entry — task 019 follow-up)

## Related

- `tasks/ben/019-digest-skill.md` — the task that designed and built this skill
- `medtech-docs` skill — owns the `changelog-project.md` template file
- `task` skill — the `/task setup` helper installs `register-hook.sh` which `/digest setup` reuses

## Best Practices

<!-- Read by the /best-practices audit -->

| Check | How to Verify | Severity | Scope |
|---|---|---|---|
| Skill installed | `.claude/skills/digest/SKILL.md` exists | Required | shared |
| Approved skill listed | `project.yml` `security.approved_skills` includes `digest` | Required | shared |
| CHANGELOG.md exists | `CHANGELOG.md` at repo root | Recommended | shared |
| CHANGELOG.md has the medtech-docs template header | `CHANGELOG.md` first line is `# <Project Name> — Project Changelog` | Recommended | shared |
| SessionStart hook registered | `.claude/settings.json` `hooks.SessionStart` contains a command referencing `session-briefing.sh` | Required | shared |
| Hook installed as symlink | `.claude/hooks/session-briefing.sh` is a symlink to `../skills/digest/hooks/session-briefing.sh` | Required | shared |
| Medtech-docs template present | `.claude/skills/medtech-docs/templates/changelog-project.md` exists | Required | shared |

## Changelog

- 9 (2026-09-08): **Version pin aligned.** `SKILL.md` frontmatter had been at `version: 9` (updated 2026-04-23) while `VERSION` still carried `1.3.0` from an older semver scheme and this changelog stopped at 8 — an ambiguous unit-under-test pin flagged by the workbench validation's environment record. `VERSION` now reads `9`; no functional change.

- 8 (2026-04-23): **Non-blocking sync-check + slug-fallback dedup** (task ben/096). `hooks/session-briefing.sh` no longer blocks on `timeout 5 git fetch` at SessionStart — fetches are now spawned into a detached subshell (`( git fetch --quiet >/dev/null 2>&1 & ) 2>/dev/null`) so the hook returns in ~0.2s instead of up-to-5s. The current session reads `git rev-list HEAD..@{u}` against whatever refs the previous session's background fetch populated; first-run emits no sync notice (one cycle later is correct). Also removed the duplicate email-slug fallback (lines 40–44) — `resolve_user.py --task-folder` already produces a stable slug via `slugify()`, so the shell-side `tr '@.' '--'` fallback was both redundant and produced subtly different output in edge cases. Net: hook drops from ~5.2s worst-case to ~0.2s; ~14 lines of shell removed.
  **Post-update:** Hook is symlinked — v8 activates on next session. First session after upgrade won't show a sync notice even if the branch is behind; second session will (background fetch populates refs the first time).
- 7 (2026-04-23): **Move BP/Changelog to README.md** (task ben/095). `## Best Practices` and `## Changelog` sections migrated from `SKILL.md` to this README so they don't load into Claude's context every time the skill triggers. `SKILL.md` now has one-line pointers to this file. No behavior change.
- 6 (2026-04-21): **Sync-check on brief builds** (task ben/085). When the SessionStart hook decides a fresh briefing is due (throttle elapsed), it now also runs a best-effort `timeout 5 git fetch --quiet` + `git rev-list --count HEAD..@{u}`. If the local branch is behind, the briefing grows a friendly, business-user-facing "Heads up — your project folder is out of date" notice naming the branch and the number of changes, plus an embedded `<!-- CLAUDE INSTRUCTION — sync-check -->` block that tells Claude to prompt the user via `AskUserQuestion` on the next turn and run `git pull --ff-only` on yes. Silent on: no upstream, fetch timeout/failure, detached HEAD, missing `timeout` binary, already up-to-date. Does NOT fire on throttled/silent sessions (only when a brief is actually being built) and does NOT fire for manual `/digest daily` — it's a hook-layer concern.
  **Post-update:** No setup re-run needed — hook is installed via symlink, new logic activates on the next brief that fires. Users whose `git config user.email` isn't in `project.yml` still get the sync notice; it keys off branch state, not roster identity.
- 5 (2026-04-20): **Relocate runtime state from `.claude/state/` to `.state/`** (task ben/083). Same `.claude/**` sensitive-file-guard escape as task-skill v18. Updated: `hooks/session-briefing.sh` STATE_DIR, `scripts/build_changelog.py` LLM_CACHE_PATH, `SKILL.md` narrative (session-briefing supporting-file row, `daily --since` default, throttle-key example), `README.md` design rationale + file tree.
  **Post-update:** Hook is symlinked — v5 activates on next session. If a project has a warm throttle cache at `.claude/state/briefing-last-shown-<slug>.txt`, `mv` it to `.state/` to preserve the window; otherwise first briefing after the migration will re-fire (harmless). The LLM cache at `.claude/state/digest-llm-cache.json` can be migrated the same way or left to rebuild from scratch on the next `/digest log` with `--llm`.
- 4 (2026-04-20): **Readable CHANGELOG format.** Each entry now leads with a bold plain-English headline + optional body sentence, with the task ref / SHA / author / date relegated to a muted italic trace footer. Two generation modes: **mechanical** (default) extracts the first paragraph of each commit body (stripping trailers like `Co-Authored-By:`) and cleans the subject — zero token cost. **LLM** (`--llm` flag, auto-enabled on `--retrospective`) batches all commits into a single `claude -p --model haiku --output-format json` call for polished rewrites; results cached at `.claude/state/digest-llm-cache.json` keyed by SHA so incremental runs don't re-summarize. Critical: `claude -p` runs with `cwd=/tmp` and `CLAUDE_*` env stripped so project hooks + CLAUDE.md don't pollute the invocation (62k context tokens avoided, hooks don't fire against the sub-invocation). Built under ben/021.
  **Post-update:** Existing CHANGELOG sections continue to render; `/digest log` going forward uses the new format. Re-run `/digest log --retrospective` to regenerate the baseline in readable form (one-time ~$0.10 LLM cost for ~35 commits via haiku). Cache file is gitignored via `.state/` (relocated from `.claude/state/` in ben/083).
- 3 (2026-04-20): **Roster-driven state-file key.** `hooks/session-briefing.sh` now calls `.claude/skills/secops/scripts/resolve_user.py --task-folder` to resolve the current user to their `team.active[].task_folder` entry and keys the throttle state file on that (`briefing-last-shown-<task-folder>.txt`). Falls back to raw email slug if no roster match. Pair with secops v3 which aligns `git config` at setup time — git email follows the roster from then on, so briefings and commits share the same identity source. Built under ben/020.
  **Post-update:** Existing projects should delete stale `briefing-last-shown-<email-slug>.txt` state files after migration. On MedTech Project we renamed `briefing-last-shown-xavier-ben-gmail-com.txt` → `briefing-last-shown-ben.txt` to preserve the active throttle window.
- 2 (2026-04-20): **Rewrite bare `task NNN:` → `task <person>/NNN:`** in both `digest.py` and `build_changelog.py` output. Commit subjects historically use bare task numbers; the project convention (`.claude/skills/lessons/SKILL.md:115`) requires the person prefix in cross-artifact references. The rewrite resolves the person by globbing `tasks/*/NNN-*.md`; unresolvable numbers are left alone. Applies to daily briefings, retrospective CHANGELOG sections, and incremental `/digest log` runs. Caught immediately after v1 shipped when the retrospective CHANGELOG.md used bare refs. Built under ben/019.
  **Post-update:** CHANGELOG.md entries written before this version may contain bare refs. Regenerate the retrospective (or hand-edit) to align existing sections to the new format.
- 1 (2026-04-20): Initial version. Two user-facing actions (`daily`, `log`) plus `setup`. SessionStart hook with 12h throttle per user email. Path-based significance filter. Retrospective-capable on first `/digest log` run; dated `## YYYY-MM-DD HH:MM` headers as the since-cursor on subsequent runs. Medtech-docs template for `CHANGELOG.md` seed is LOCAL ONLY — upstream push to hitachi medtech-docs deferred to a follow-up task. Built under MedTech Project ben/019.
