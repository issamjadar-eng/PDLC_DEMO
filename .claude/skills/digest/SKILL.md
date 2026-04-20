---
name: digest
description: "Project activity digest — automatic morning briefing at SessionStart (12h throttled per user) and on-demand append to the project CHANGELOG.md. TRIGGER when the user says: 'update the project changelog', 'build the changelog', 'add to CHANGELOG.md', 'what changed today', 'morning briefing', 'daily digest', 'project changelog', 'summarize recent commits', 'recap the project activity', 'what did people do since yesterday'."
version: 2
updated: 2026-04-20
---

# Digest

Project-wide activity summarization. Two related surfaces:

1. **Daily briefing** — short markdown digest emitted at SessionStart, throttled to once per 12h per user. Covers commits since last-shown grouped by author, plus a "Pay attention" section scoped to structural diffs, skill updates, and project-level changes. Mechanical aggregation — no LLM cost.
2. **Project `CHANGELOG.md`** — user-invoked append to a persistent file at repo root. First run scans full git history, applies a significance heuristic, and writes a retrospective section; subsequent runs use the last dated header as a since-cursor.

Usage: `/digest <action> [arguments]`

## Dependencies

| File / Tool | Required by | Purpose | How to create |
|---|---|---|---|
| `git` | All actions | Source of truth for commits and file changes | Pre-installed |
| `jq` | `daily` hook | JSON parsing (SessionStart hook reads `session_id` from stdin) | `brew install jq` |
| `project.yml` | `setup`, `daily` | Team roster for email-to-user resolution | `/medtech-docs init` or manual |
| `.claude/hooks/register-hook.sh` | `setup` | Idempotent hook registration helper | Installed by `/task setup` |
| `python3` | `daily`, `log` | Aggregation + CHANGELOG builder scripts | Pre-installed on macOS 12.3+ and mainstream Linux |

`/digest setup` should run **after** `/task setup` has installed `register-hook.sh`. Alphabetical skill directory order satisfies this dependency (`digest` < `task` is FALSE; run `/task setup` manually first if not already done).

## Supporting Files

| File | Purpose |
|---|---|
| `scripts/digest.py` | Daily-briefing aggregator. Reads commits since a cutoff timestamp, groups by author, filters "Pay attention" paths, emits markdown to stdout. Invoked by the SessionStart hook and the `daily` action. |
| `scripts/build_changelog.py` | `CHANGELOG.md` builder. Finds last `## YYYY-MM-DD HH:MM` header as since-cursor (or scans full history on first run), filters commits to significant, groups by theme, emits a proposed new section. Invoked by the `log` action. |
| `hooks/session-briefing.sh` | SessionStart hook. Resolves `git config user.email`; checks per-user throttle file at `.claude/state/briefing-last-shown-<slug>.txt`; runs `digest.py --since <last-shown>` and emits markdown to stdout (rendered as SessionStart system context) if ≥12h since last, else silent. |
| `README.md` | Design documentation — rationale, architecture, future directions. Not loaded by Claude. |

CHANGELOG seed template (owned by the `medtech-docs` skill per project convention):
`.claude/skills/medtech-docs/templates/changelog-project.md`

## Actions

Parse the user's argument string to determine which action to perform:

### `setup`

Install the SessionStart hook, seed `CHANGELOG.md` from the medtech-docs template if missing, and add `digest` to `project.yml` `security.approved_skills`. Idempotent.

1. **Preflight** — verify `jq`, `python3`, `git` are on PATH; verify `.claude/hooks/register-hook.sh` exists (run `/task setup` first if missing); verify `project.yml` exists.
2. **Symlink the hook**: `.claude/hooks/session-briefing.sh` → `../skills/digest/hooks/session-briefing.sh` (skip if already correct; refresh if stale).
3. **Register the SessionStart hook**:
   ```bash
   .claude/hooks/register-hook.sh SessionStart "" command \
     '"$CLAUDE_PROJECT_DIR"/.claude/hooks/session-briefing.sh'
   ```
4. **Seed `CHANGELOG.md`** — if the file is absent at repo root, copy it from `.claude/skills/medtech-docs/templates/changelog-project.md`, substituting `{{PROJECT_NAME}}` with `project.name` from `project.yml` and `{{DATE}}` with today's date.
5. **Append `digest`** to `project.yml` `security.approved_skills` if not already listed (alphabetical insertion).
6. Report what was done.

### `daily [--since <ISO-datetime>] [--dry-run]`

Emit the daily briefing to stdout. Normally invoked by the SessionStart hook; can also be invoked manually for preview or testing.

Arguments:
- `--since` — override the cutoff timestamp (default: contents of `.claude/state/briefing-last-shown-<email-slug>.txt`, or 24h ago if no state file)
- `--dry-run` — compute the digest but do NOT update the throttle state file

Steps:
1. Resolve user identity: `git config user.email` → slugify → state file path.
2. If `--since` not provided: read the state file for the last-shown timestamp. If missing, default to 24h ago.
3. Run `scripts/digest.py --since <ts>`. The script:
   - Lists commits with `git log --since=<ts> --pretty='<SHA>|<author_email>|<author_name>|<ISO date>|<subject>'`
   - Groups by author (including the current user's own commits — per explicit design decision, self-recall is valuable)
   - Runs `git log --since=<ts> --name-only` to build per-commit file lists
   - Filters files against the "Pay attention" path rules:
     - **Structural**: `CLAUDE.md`, `project.yml`, `.claude/rules/**`
     - **Skill updates**: any `.claude/skills/*/SKILL.md` (detect version frontmatter change via `git show <sha>:<path>` comparison), any newly-added `.claude/skills/*/` directory, new lines in `.claude/sync-log.md`
     - **Project-level**: new entries under `docs/project/strategies/**`, `docs/project/submissions/**`, new DHF folders under `docs/project/dhfs/*/`, new `docs/external/standards/*.md`
   - Emits a markdown block: header with window, "Commits" section grouped by author, "Pay attention" section listing matched files with their commit context. Cap at ~60 lines — truncate overflow with a `(+N more)` note.
4. Unless `--dry-run`, update the throttle state file with the current timestamp.
5. The SessionStart hook additionally prepends a short separator line to the output so it renders distinctly in the session log.

### `log [--since <ISO-datetime>] [--title <short-title>] [--dry-run]`

Build and append a new section to `CHANGELOG.md` at repo root.

Arguments:
- `--since` — override the cutoff. Default: the last `## YYYY-MM-DD HH:MM` dated header in `CHANGELOG.md`. If none, scan full history (retrospective).
- `--title` — optional short title appended to the section header (e.g., "Project retrospective", "Post-sync hygiene pass"). Default: generated from the most significant theme found.
- `--dry-run` — compute the new section and print it; do NOT write to `CHANGELOG.md`.

Steps:
1. Read `CHANGELOG.md`. If absent, tell the user to run `/digest setup` first and stop.
2. Find the most recent `## YYYY-MM-DD HH:MM` header. Use its timestamp as `--since`. If no header exists, this is the retrospective first run — `since` is unset (full history).
3. Run `scripts/build_changelog.py --since <ts> [--retrospective]`. The script:
   - Queries `git log [--since=<ts>] --pretty=...`
   - Applies the **significance filter**:
     - Commit subject matches regex `task\s+\d+` (case-insensitive) → ALWAYS significant
     - Commit touches any path in the trigger set → significant
     - Commit subject starts with `chore:`, `fmt:`, `lint:`, `typo:`, `docs(readme):` → NEVER significant (unless it also hits a trigger path)
     - All other commits → NOT significant (conservative default)
     - Trigger paths: `CLAUDE.md`, `project.yml`, `docs/project/strategies/**`, `docs/project/submissions/**/composition-manifest.md`, any `.claude/skills/*/SKILL.md` (version bumped), any new `docs/project/dhfs/*/` folder, any `docs/external/standards/*.md`, any new `.claude/skills/*/` directory, new section under `CHANGELOG.md` itself (excluded — no self-reference loop)
   - Groups by theme in this fixed order: **Skills** (version bumps, new skills, removed skills), **Tasks Completed** (commits whose subject matches `task NNN:` and references an index.md Completed move), **Project Structure** (CLAUDE.md, project.yml, new DHFs, new composition manifests), **Documentation** (strategies, standards, submissions), **Other** (catch-all for matched commits that don't fit a theme)
   - Emits a markdown section with a dated header, the `--title` (or generated), and bulleted entries under each theme — each bullet cites 1–3 commit SHAs in parentheses.
4. Print the proposed section to the user **before** writing. Ask for approval: "Write this section? (y/edit/n)". If edit, offer to receive the edited text. If n, abort.
5. On approval: insert the new section immediately after the file's top preamble and before the most recent existing section (reverse-chronological convention — newest first). Write via the Edit tool.
6. Report the number of significant commits captured and the range.

### `help`

Show this usage guide.

## User identity and throttling

Digest uses `git config user.email` as the primary identity key. The daily throttle file is `.claude/state/briefing-last-shown-<slug>.txt` where `<slug>` is the email with `@` and `.` replaced by `-` (e.g., `ben-xavier-globallogic-com`). One file per user, independent of `session_id` — this matches the 12h-per-user intent and survives session restarts.

If `git config user.email` is empty or matches no `team.active[]` entry in `project.yml`, the hook still runs using the raw email slug (unknown users get briefings too). It does NOT error — an unconfigured or guest identity is a normal case for fresh clones.

## Significance filter — editable

The significance rules live in `scripts/build_changelog.py` as a constant at the top of the file, not in `project.yml`. Projects that want a different filter should fork the script — this intentionally avoids a config-drift surface in v1. If it becomes a frequent request, v2 can introduce `digest.yml` with overrideable patterns.

## Notes

- The daily briefing's "Pay attention" section is path-based and therefore heuristic. A structural change made via a commit whose files don't match the trigger list won't surface. That's a deliberate bias toward noise-free briefings.
- Both actions are read-mostly. `daily` writes only to the throttle state file. `log` writes only to `CHANGELOG.md`, and only with user approval.
- The hook emits to stdout; Claude Code renders SessionStart hook stdout as system context visible to the user at the top of the session.
- Commits authored by the current user ARE included in the daily briefing (per explicit design decision — self-recall of yesterday's work is valuable). The CHANGELOG builder treats all authors equally.
- The CHANGELOG is reverse-chronological (newest first). `/digest log` inserts new sections at the top.
- **Task reference rewrite.** Both `digest.py` and `build_changelog.py` rewrite bare `task NNN` refs in commit subjects into `task <person>/NNN` form per the project convention (`.claude/skills/lessons/SKILL.md:115`). The person is resolved by globbing `tasks/*/NNN-*.md`. Commits referencing numbers that don't resolve to a task file are left alone (avoids silently dropping dangling refs). Historical commit subjects are not rewritten in git — only the rendered output of these scripts.

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

- 2 (2026-04-20): **Rewrite bare `task NNN:` → `task <person>/NNN:`** in both `digest.py` and `build_changelog.py` output. Commit subjects historically use bare task numbers; the project convention (`.claude/skills/lessons/SKILL.md:115`) requires the person prefix in cross-artifact references. The rewrite resolves the person by globbing `tasks/*/NNN-*.md`; unresolvable numbers are left alone. Applies to daily briefings, retrospective CHANGELOG sections, and incremental `/digest log` runs. Caught immediately after v1 shipped when the retrospective CHANGELOG.md used bare refs. Built under ben/019.
  **Post-update:** CHANGELOG.md entries written before this version may contain bare refs. Regenerate the retrospective (or hand-edit) to align existing sections to the new format.
- 1 (2026-04-20): Initial version. Two user-facing actions (`daily`, `log`) plus `setup`. SessionStart hook with 12h throttle per user email. Path-based significance filter. Retrospective-capable on first `/digest log` run; dated `## YYYY-MM-DD HH:MM` headers as the since-cursor on subsequent runs. Medtech-docs template for `CHANGELOG.md` seed is LOCAL ONLY — upstream push to hitachi medtech-docs deferred to a follow-up task. Built under PDLC_DEMO ben/019.
