---
name: sync-skills
description: "Bidirectional sync between this project's `.claude/skills` + `.claude/agents` and the hitachi registry repository. Pulls updates with evaluation, pushes local fixes upstream as PRs (with opt-in auto-merge)."
version: 2
updated: 2026-04-12
---

# Sync Skills

Keeps the project's installed skills and agents aligned with the `hitachi` registry repository. Usage: `/sync-skills <action> [arguments]`

## Supporting Files

| File | Purpose |
|------|---------|
| `scripts/sync.sh` | Mechanical primitives: fetch, diff, copy, branch, commit, push. Never opens PRs — that's the skill's job via `gh`. |

## Configuration

The script reads the hitachi working-copy path from `project.yml`:

```yaml
registries:
  - name: hitachi
    type: github
    repo: GlobalLogic-a-Hitachi-Company/hitachi
    local_path: ../hitachi   # <— used by this skill
```

If `local_path` is missing, the script falls back to `../hitachi` relative to the project root. `sync-skills` itself is excluded from diffs (prevents self-update surprises).

## Actions

Parse `$ARGUMENTS` to determine the action.

### `check`

Read-only — shows what would change in either direction. Safe to run any time. Mutates nothing.

1. Run `.claude/skills/sync-skills/scripts/sync.sh check`
2. Parse the output. It lists one change per line, tab-separated: `STATUS<TAB>PATH`
3. Group results by status:
   - **`UPSTREAM_ONLY`** — exists in hitachi, missing locally → pull candidate
   - **`LOCAL_ONLY`** — exists locally, missing upstream → push candidate
   - **`UPSTREAM_NEWER`** — both exist, content differs → needs human judgment (could be upstream newer, local newer, or concurrent edits)
4. For each `UPSTREAM_NEWER` entry, use `git -C <hitachi> show origin/main:<path>` vs. the local file to show a unified diff summary (≤20 lines per file unless the user asks for more).
5. Present a **summary report** to the user:
   - Counts per status
   - For `UPSTREAM_NEWER`, a one-line impact note per file: is it a bugfix? new section? template change? Flag anything that touches:
     - `medtech-docs/templates/` — may require re-running parts of `/medtech-docs init`
     - Any `### \`setup\`` action in a SKILL.md — setup may need to be re-run
     - `## Best Practices` sections — new checks may raise audit findings
     - `manifest.md` — informational, but note registry version changes
6. Stop. No mutations. Tell the user which follow-up to run (`pull`, `push <files>`, or `sync`).

### `pull`

Apply upstream changes to the local project. Interactive — per-file approval for anything non-trivial.

**Step 1 — Run `check` first** to get the current state.

**Step 2 — Classify each change:**
- **Safe auto-approve** (may be applied without prompting, but still listed in the summary):
  - `UPSTREAM_ONLY` under `skills/` where the new skill isn't already partially present
  - `UPSTREAM_NEWER` where the local file is *identical to a previous hitachi version* (clean upstream advance)
- **Needs confirmation**:
  - `UPSTREAM_NEWER` where the local file has diverged from any known hitachi version (possible conflict)
  - Deletions (upstream removed a file)
  - New skills with a `### \`setup\`` action (setup will need to be run)

**Step 3 — Present the batch to the user.** Show the counts, list the flagged items, and ask: "Approve all / approve only auto-safe / pick per-file / abort?"

**Step 4 — Apply approved changes:**
- For each approved entry, call `sync.sh pull-file <relpath>`
- The script copies the file (or removes it if upstream deleted it)

**Step 5 — Post-apply reconciliation:**
- If new skills were added → suggest updating `project.yml` `security.approved_skills` and ask the user to confirm additions
- If new agents were added → update `security.approved_agents`
- If a newly-synced skill has a `### \`setup\`` action that wasn't present before → offer to invoke `/skill-name setup`
- If deleted skills/agents were in the allowlist → offer to remove them from `project.yml`

**Step 6 — Record the sync** in `.claude/sync-log.md`:
```markdown
## 2026-04-12 — pull

- Hitachi HEAD after sync: `4e54855`
- Pulled: 3 files
  - `skills/task/SKILL.md` (upstream bugfix — hook-registration idempotency)
  - `skills/medtech-docs/templates/readme-project.md` (new changelog section)
  - `agents/project-secops.md` (new attestation check)
- project.yml: no changes
- Follow-ups: none
```

Use the `hitachi-head` subcommand to get the hash.

### `push [--merge] <files...>`

Contribute local improvements back to the registry. **Default is PR-only — the skill opens a PR and stops.** Pass `--merge` to request automatic squash-merge after the PR is created.

Arguments:
- **`--merge`** (optional, opt-in) — after the PR is opened, squash-merge it with `gh pr merge --squash --delete-branch` and pull the merged commit into the local hitachi checkout. Only honor this flag when the user explicitly passes it (or asks for it in a natural-language request like "push and merge"). Never default to merging.
- **`<files...>`** — one or more paths relative to `.claude/` (e.g., `skills/sync-skills/SKILL.md agents/project-secops.md`). If no paths are given, prompt the user to pick from the `LOCAL_ONLY` and `UPSTREAM_NEWER` lists reported by `check`.

**Step 1 — Preflight checks:**
- Run `check`. Refuse to push any file listed as `UPSTREAM_NEWER` unless the user explicitly acknowledges the divergence (because we'd be overwriting upstream changes).
- Verify every requested path exists locally under `.claude/`.
- Verify the hitachi working tree is clean (`sync.sh push-prep` will refuse if it isn't — surface the error cleanly).

**Step 2 — Draft branch name, commit message, and PR body.**
- Branch: `sync/<project-name>-<topic>-<yyyy-mm-dd>` (e.g., `sync/pdlc-demo-sync-skills-2026-04-12`). Keep the topic concise — pull it from the filenames.
- Commit message: first line is a tight summary (≤72 chars). Body explains *why* the change exists and links back to the originating project and task when possible (e.g., "Discovered while building sync-skills in PDLC_DEMO task 008").
- PR body follows the Claude Code PR convention: `## Summary`, `## Test plan` sections. Include the list of files and a note on any behavioral changes.

**Step 3 — Show the draft to the user.** Print the branch name, commit subject, commit body, PR title, and PR body. Ask for approval or edits. Loop until the user approves or aborts.

**Step 4 — Execute** (each step individually confirmable if the user asked for cautious mode):
1. `sync.sh push-prep <branch>` — resets hitachi to fresh `origin/main` and creates the branch
2. For each file: `sync.sh push-stage <relpath>` — copies local → hitachi
3. `sync.sh push-finalize <commit-msg>` — commits and pushes the branch

**Step 5 — Open PR** with `gh pr create --repo GlobalLogic-a-Hitachi-Company/hitachi --base main --head <branch> --title <title> --body <body>`. Capture and return the PR URL.

**Step 5b — (only if `--merge` was passed) — Auto-merge the PR.**
1. Run `gh pr merge <pr-number> --repo GlobalLogic-a-Hitachi-Company/hitachi --squash --delete-branch`.
2. Verify the merge: `gh pr view <pr-number> --json state,mergedAt` should show `MERGED`.
3. Fast-forward the local hitachi checkout so it stays in sync with the merged state:
   - `git -C <hitachi> checkout main`
   - `git -C <hitachi> pull --ff-only`
4. Record the merge commit hash in the sync log entry.
5. If the merge fails (merge conflicts, branch protection, failing checks), stop and report the error to the user — do **not** retry or force. The PR stays open for human attention.

**Step 6 — Record the push** in `.claude/sync-log.md`. Include the merge commit and final hitachi HEAD if `--merge` was used:
```markdown
## 2026-04-12 — push

- Files: `skills/sync-skills/SKILL.md`, `skills/sync-skills/scripts/sync.sh`
- Branch: `sync/pdlc-demo-add-sync-skills-2026-04-12`
- PR: https://github.com/GlobalLogic-a-Hitachi-Company/hitachi/pull/3
- Commit: "Add sync-skills skill for bidirectional registry sync"
- Status: merged (--merge requested)
- Merge commit: `<hash>`
- Hitachi HEAD after sync: `<hash>`
```
If `--merge` was not passed, `Status` is `awaiting review` and the `Merge commit` / `Hitachi HEAD after sync` lines are omitted.

**Auto-merge is opt-in only.** Do not merge unless the user explicitly passed `--merge` or asked for it in plain language. PR-only is the safe default — review and merge are separate human decisions in that mode.

### `sync`

Convenience wrapper: runs `pull` first (apply upstream changes), then shows any remaining `LOCAL_ONLY`/`UPSTREAM_NEWER` entries as push candidates and asks whether to continue into a `push` flow. Equivalent to `check` → `pull` → `push` in one invocation.

## Notes

- `$ARGUMENTS` empty or `help` → show this usage
- The script refuses any path outside `skills/` or `agents/` — it will not touch `.git/`, `project.yml`, or anything else under `.claude/`
- When the skill needs to modify `project.yml`, it does that itself (via `Edit`), not the script
- Paths are always relative to the registry root: `skills/<name>/...` or `agents/<name>`. The script joins them with the hitachi path or `.claude/` path as needed
- If the hitachi working tree is dirty, `pull` is still safe (the script reads from `origin/main`, not the working copy), but `push` will refuse until it's clean
- If there's no `gh` CLI auth, `push` will fail at Step 5 — tell the user to run `gh auth login` and re-run `push` (the commit is already pushed, so they can re-use the branch)

## Best Practices

<!-- Read by /best-practices skill to audit sync hygiene -->

| Check | How to Verify | Severity |
|-------|--------------|----------|
| Sync log exists | `.claude/sync-log.md` exists | Recommended |
| Sync log has a recent entry | Last entry in `.claude/sync-log.md` is within 30 days | Recommended |
| No silent divergence | Running `sync.sh check` returns zero `UPSTREAM_NEWER` entries, OR those entries are documented in the sync log with a rationale (local customization kept intentionally) | Recommended |
| Hitachi path resolves | `sync.sh hitachi-path` exits 0 and points at an existing git repo | Required |
| Script is executable | `.claude/skills/sync-skills/scripts/sync.sh` has the executable bit | Required |
| Allowlist matches installed | Every skill directory under `.claude/skills/` is listed in `project.yml` `security.approved_skills` (and vice versa) | Required |

## Changelog

- 2 (2026-04-12): Added opt-in `--merge` flag to `push`. When passed, the skill calls `gh pr merge --squash --delete-branch` after the PR is created, then `git pull --ff-only` in the local hitachi checkout so it stays in sync. Default remains PR-only — never merge without explicit request.
- 1 (2026-04-12): Initial version. Four actions: `check`, `pull`, `push <files>`, `sync`. Script primitives: `check`, `pull-file`, `push-prep`, `push-stage`, `push-finalize`, `hitachi-path`, `hitachi-head`. Reads `registries[name=hitachi].local_path` from `project.yml` with `../hitachi` fallback. Excludes `sync-skills` from diffs. Push flow always opens a PR.
