---
name: sync-skills
description: "Bidirectional sync between this project's `.claude/skills` + `.claude/agents` and the hitachi registry repository. Pulls updates with evaluation, pushes local fixes upstream as PRs (with opt-in auto-merge). `pull` performs a three-way merge analysis on every UPSTREAM_NEWER file via git blob-history probing — bucketing each into UPSTREAM_ADVANCE / LOCAL_AHEAD / BOTH_DIVERGED before any auto-apply, so locally-newer files are surfaced as push candidates instead of being clobbered. `status` action gives an at-a-glance \"are all four places in lockstep?\" health check before switching machines. `prune` action removes merged `sync/*` push branches that accumulate in the registry checkout. `deps` action resolves a skill's dependency closure (sibling skills + agents) from `dependencies:` frontmatter so a single-skill pull also brings what it needs — and `pull` now surfaces that closure before applying."
version: 8.4
updated: 2026-05-30
---

# Sync Skills

Keeps the project's installed skills and agents aligned with the `hitachi` registry repository. Usage: `/sync-skills <action> [arguments]`

## Supporting Files

| File | Purpose |
|------|---------|
| `scripts/sync.sh` | Mechanical primitives: fetch, diff, copy, branch, commit, push, status, three-way analyze, deps closure. Never opens PRs — that's the skill's job via `gh`. |
| `scripts/resolve_deps.py` | Dependency-closure resolver — reads each skill's `dependencies:` frontmatter block and computes the transitive skill closure + agent union; flags closure members absent in the consumer. Dependency-free (hand-parses the bounded YAML shape). Backs the `deps` subcommand and the `pull` co-dependency step. |
| `tests/test_status.sh` | Self-contained smoke tests for the `status` action. Builds a fake project + registry world, exercises 4 cases (all-synced, dirty, ahead, drift). |
| `tests/test_three_way_pull.sh` | Self-contained smoke tests for `analyze` + `check --analyzed`. Four cases (UPSTREAM_ADVANCE, LOCAL_AHEAD, BOTH_DIVERGED, mixed batch with UPSTREAM_ONLY). |
| `tests/test_deps.sh` | Self-contained smoke tests for the `deps` action / `resolve_deps.py`. Builds a fake registry with `dependencies:` blocks + a consumer missing some members; asserts transitive closure, optional-not-traversed, agent union, missing-flagging, JSON shape, exit codes, unresolved detection (21 assertions). |
| `tests/test_prune.sh` | Self-contained smoke tests for the `prune` action — builds a hitachi world with merged + unmerged `sync/*` branches; 15 assertions over dry-run classification, `--apply` deletion (local + remote), idempotence, and the empty case. |
| `tests/test_windows_symlink_guard.sh` | Regression tests for the Windows-clone symlink corruption vector (v8.3). 4 cases: clean Windows-style symlink reports no false drift; corrupted-target push-stage refused with exit 8 (oversized + multi-line variants); real Linux symlink still stages cleanly. |

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

1. Run `.claude/skills/sync-skills/scripts/sync.sh check --analyzed` (the `--analyzed` flag enriches every UPSTREAM_NEWER row with a three-way merge recommendation; pass-through rows are unchanged).
2. Parse the output. It lists one change per line, tab-separated:
   - For `UPSTREAM_ONLY` and `LOCAL_ONLY` rows: `STATUS<TAB>PATH`
   - For `UPSTREAM_NEWER` rows: `STATUS<TAB>PATH<TAB>RECOMMENDATION<TAB>SUMMARY`
3. Group results by status (and, for `UPSTREAM_NEWER`, by recommendation):
   - **`UPSTREAM_ONLY`** — exists in hitachi, missing locally → pull candidate
   - **`LOCAL_ONLY`** — exists locally, missing upstream → push candidate
   - **`UPSTREAM_NEWER` + `UPSTREAM_ADVANCE`** — local matches an OLD hitachi blob; upstream advanced cleanly → safe auto-pull
   - **`UPSTREAM_NEWER` + `LOCAL_AHEAD`** — local blob is unknown to hitachi history AND was recently edited (≤7 days) → KEEP LOCAL, push candidate (do NOT auto-pull)
   - **`UPSTREAM_NEWER` + `BOTH_DIVERGED`** — both sides advanced from a common ancestor → manual diff review required
   - **`UPSTREAM_NEWER` + `UNDETERMINED`** — blob-history probe couldn't decide → treat as BOTH_DIVERGED for safety
4. For each `UPSTREAM_NEWER` entry that landed in BOTH_DIVERGED or UNDETERMINED, use `git -C <hitachi> show origin/main:<path>` vs. the local file to show a unified diff summary (≤20 lines per file unless the user asks for more).
5. Present a **summary report** to the user:
   - Counts per status
   - For `UPSTREAM_NEWER`, a one-line impact note per file: is it a bugfix? new section? template change? Flag anything that touches:
     - `medtech-docs/templates/` — may require re-running parts of `/medtech-docs init`
     - Any `### \`setup\`` action in a SKILL.md — setup may need to be re-run
     - `## Best Practices` sections — new checks may raise audit findings
     - `manifest.md` — informational, but note registry version changes
6. Stop. No mutations. Tell the user which follow-up to run (`pull`, `push <files>`, or `sync`).

### `status`

At-a-glance health check across all four sync surfaces. Use before switching machines, before a long uninterruptible push, or any time the user asks "are we synced?" Read-only — only `git fetch --quiet` runs, and only to refresh remote refs.

Reports five labeled blocks:

1. **Project repo working tree** — clean / DIRTY (with file list)
2. **Project local HEAD ⇄ origin** — SYNCED / AHEAD / BEHIND / DIVERGED / NO UPSTREAM
3. **Registry repo working tree** — clean / DIRTY (or MISSING if the hitachi clone isn't present)
4. **Registry local HEAD ⇄ origin** — SYNCED / AHEAD / BEHIND / DIVERGED
5. **Skill drift** — count of files in `LOCAL_ONLY` / `UPSTREAM_ONLY` / `UPSTREAM_NEWER` (reuses the `check` primitive). Also notes a stale-`sync/*`-branch count when any exist — hygiene only, does **not** affect the SYNCED verdict (see the `prune` action).

Final line is `Overall: SYNCED — safe to switch machines` or `Overall: NOT SYNCED — see <which block> above`.

1. Run `.claude/skills/sync-skills/scripts/sync.sh status`
2. The script prints all five blocks and exits 0 if everything is SYNCED, 1 otherwise.
3. Pass the output to the user verbatim. Do not paraphrase — the format is the contract.
4. If overall is NOT SYNCED, follow up with one concrete next step per failing block:
   - DIRTY working tree → suggest `git -C <repo> status` then commit/stash
   - AHEAD → suggest `git -C <repo> push`
   - BEHIND → suggest `git -C <repo> pull --ff-only`
   - DIVERGED → suggest manual rebase/merge (do not auto-resolve)
   - DRIFT → suggest `/sync-skills check` for per-file detail, then `pull` or `push`
   - MISSING → suggest cloning hitachi alongside the project repo

### `pull`

Apply upstream changes to the local project. Interactive — per-file approval for anything non-trivial.

**Step 1 — Run `check --analyzed` first** (NOT plain `check` — the three-way analysis is mandatory, not optional). This bucketizes every UPSTREAM_NEWER file via git blob-history probing.

**Step 2 — Classify each change into one of three buckets:**

- **Auto-pull bucket** (may be applied without per-file prompting, but still listed in the summary):
  - `UPSTREAM_ONLY` under `skills/` where the new skill isn't already partially present (new file, no conflict possible)
  - `UPSTREAM_NEWER` + `UPSTREAM_ADVANCE` recommendation — the local file's blob is in hitachi's history at an older commit; upstream has cleanly advanced. Safe to fast-forward.

- **Skip bucket — NEVER auto-pull**:
  - `UPSTREAM_NEWER` + `LOCAL_AHEAD` recommendation — the local file's blob is unknown to hitachi history AND the project's commit touching this file is recent (≤7 days). The local copy is the newer one; pulling would clobber un-pushed work. **Surface these as push candidates instead.**

- **Confirm bucket — per-file Y/N gate, with diff**:
  - `UPSTREAM_NEWER` + `BOTH_DIVERGED` recommendation — both sides have advanced from the common ancestor. Show the unified diff (≤30 lines) and ask the user to approve, skip, or abort per file.
  - `UPSTREAM_NEWER` + `UNDETERMINED` recommendation — analyze probe couldn't decide; treat as BOTH_DIVERGED for safety.
  - Deletions (upstream removed a file)
  - New skills with a `### \`setup\`` action (setup will need to be run)

**Step 3 — Present the bucketed batch to the user.** Show the three buckets explicitly with counts and per-file lines (recommendation + 1-line summary). The default action is **"approve auto-pull bucket only"** — the safest default. Other options: "approve auto-pull + walk confirm bucket", "approve everything (acknowledged risk)", "abort". The skip bucket (LOCAL_AHEAD) is NEVER auto-pulled regardless of choice — it's surfaced for the next push.

**Step 3b — Resolve dependency closure for any newly-pulled skill (MANDATORY when a `UPSTREAM_ONLY` skill is in the approved batch).** A skill's dependencies — sibling skills it consumes, the `shared/` utilities, and (the silent-failure case) **agents**, which live on a separate sync surface (`.claude/agents/` vs `.claude/skills/`) — are not carried automatically just because you pulled the skill's directory. For each skill being newly added, run:

```bash
.claude/skills/sync-skills/scripts/sync.sh deps <skill-name>
```

This reads the skill's `dependencies:` frontmatter (the contract documented by `skill-creator`) and prints the transitive **required** skill closure + the **agent** union, flagging every member `[MISSING locally]`. Then:
- **Required skills flagged `[MISSING locally]`** → add them to the pull batch (they bucket as `UPSTREAM_ONLY` themselves) and re-resolve until the closure is satisfied. A required dep you don't pull means the skill is installed broken.
- **Agents flagged `[MISSING locally]`** → these are NOT pulled by file-copy. Note them and, in Step 5, run the owning skill's agent-install action (`/advisors init`, `/reference-audit setup`, `/secops setup`) so the agents land as symlinks/copies in `.claude/agents/`.
- **Optional skills** → list them for the user; do not auto-add.
- **`! UNRESOLVED`** lines mean a declared required dep names a skill absent from the registry — surface it as a registry-integrity bug, don't silently drop it.

If the resolver reports "Required skills: none" and "Agents: none," say so and continue — the skill is self-contained.

**Critical safety property:** `UPSTREAM_NEWER` + `LOCAL_AHEAD` and `UPSTREAM_NEWER` + `BOTH_DIVERGED` files are NEVER auto-applied. The pre-v8 behavior of bulk-approving every UPSTREAM_NEWER file overwrote 1131 lines of un-pushed local work in one incident — the bucketing in v8 exists to make that failure mode unreachable.

**Step 4 — Apply approved changes:**
- For each approved entry, call `sync.sh pull-file <relpath>`
- The script copies the file (or removes it if upstream deleted it)

**Step 5 — Post-apply reconciliation:**
- If new skills were added → suggest updating `project.yml` `security.approved_skills` and ask the user to confirm additions
- **If Step 3b flagged any agents `[MISSING locally]`** → run the owning skill's agent-install action so they land in `.claude/agents/`: `/advisors init` (advisor personas), `/reference-audit setup` (citations agents), `/secops setup` (project-secops). Agents are a separate sync surface — a file-copy pull never installs them. Then add the new agents to `project.yml` `security.approved_agents`.
- If new agents were added → update `security.approved_agents`
- If a newly-synced skill has a `### \`setup\`` action that wasn't present before → offer to invoke `/skill-name setup`
- If deleted skills/agents were in the allowlist → offer to remove them from `project.yml`

**Step 5b — MANDATORY: Analyze pulled changes for project-update impact.** For every pulled file, Claude must read the updated content (in particular the `## Changelog` section of each SKILL.md and any `**Post-update:**` annotations) and determine whether the local project needs to be updated to align with the new skill. This is not optional — it runs on every successful pull, even for a single file. Analyze:

  1. **Changelog entries** — for each new version entry, extract the stated behavior/contract change and any `**Post-update:**` block. The post-update annotation (sync-skills v3+ / task v13+ convention) is the authoritative source for "what downstream must do after pulling this version."
  2. **Setup action changes** — if a skill's `### \`setup\`` action gained new steps (new hooks to register, new symlinks, new allowlist entries), the user must re-run `/skill-name setup`. Offer to run it.
  3. **Template changes** — if a pulled file lives under `templates/` or is referenced by a skill's init/scaffold action, check whether existing project files derived from that template need to be regenerated or patched. Flag specific files by path.
  4. **Best Practices table changes** — if a pulled SKILL.md's `## Best Practices` table gained new `Required` or `Recommended` checks, run (or offer to run) `/best-practices` to surface any new FAILs, and explicitly list which checks are new.
  5. **Frontmatter / schema changes** — new `version:` fields, renamed YAML fields, new required keys in `project.yml`, or registry-config shape changes all require a local update. Apply the update or tell the user exactly what to change.
  6. **Terminology renames** — if the upstream changed a user-facing term (e.g., `sub-DHF` → `DHF`, renamed action names, renamed template files), grep the project for the old term and report every hit that may need updating.
  7. **Hook changes** — if `hooks/` files were added or changed in a skill that installs session hooks, re-running `/skill setup` is usually required even when the changelog doesn't say so explicitly. Flag it.

Present findings as a **Project Impact Report** with this shape:

```
Pulled N file(s). Analyzing project impact...

[skills/<name>/SKILL.md — v<old> → v<new>]
  Changelog summary: <one-line per version jump>
  Post-update required: <yes/no + verbatim post-update text if present>
  Project impact: <none | list concrete local changes needed>
  Action: <no action | run `/foo setup` | edit <path> | run `/best-practices` | ...>

[<next file>]
  ...

Summary: <N files pulled, M require action, K actions auto-offered>
```

If any action is offered, wait for user approval before executing. If the analysis concludes "no action needed," say so explicitly — silence is not acceptable. This analysis is part of what `pull` *means* in this project; skipping it defeats the purpose of syncing.

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
- Branch: `sync/<project-name>-<topic>-<yyyy-mm-dd>` (e.g., `sync/acme-demo-sync-skills-2026-04-12`). Keep the topic concise — pull it from the filenames.
- Commit message: first line is a tight summary (≤72 chars). Body explains *why* the change exists and links back to the originating project and task when possible (e.g., "Discovered while building sync-skills in <project> task 008").
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
3. Fast-forward the local hitachi checkout so it stays in sync with the merged state, then delete the now-merged local branch:
   - `git -C <hitachi> checkout main`
   - `git -C <hitachi> pull --ff-only`
   - `git -C <hitachi> branch -D <branch>` — `--squash --delete-branch` above removed the *remote* sync branch; this removes the leftover *local* one. Without this step every `--merge` push leaves a stale `sync/*` branch in the hitachi checkout (they accumulate — see the `prune` action).
4. Record the merge commit hash in the sync log entry.
5. If the merge fails (merge conflicts, branch protection, failing checks), stop and report the error to the user — do **not** retry or force. The PR stays open for human attention.

**Step 6 — Record the push** in `.claude/sync-log.md`. Include the merge commit and final hitachi HEAD if `--merge` was used:
```markdown
## 2026-04-12 — push

- Files: `skills/sync-skills/SKILL.md`, `skills/sync-skills/scripts/sync.sh`
- Branch: `sync/acme-demo-add-sync-skills-2026-04-12`
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

### `prune`

Delete merged `sync/*` push branches that have accumulated in the hitachi checkout. Every `push` runs `push-prep`, which creates a `sync/<topic>-<date>` branch. The `--merge` path deletes that branch automatically (Step 5b, since v8.2); but **PR-only pushes** — where the PR is merged later, outside the skill — leave both the local and the remote branch behind. Over many pushes these accumulate (one cleanup cleared 111 of them). `prune` clears the residue safely.

1. Run `.claude/skills/sync-skills/scripts/sync.sh prune` — **dry-run, deletes nothing.**
2. The script checks out `main`, fetches + prunes `origin`, then classifies every `sync/*` branch (local ∪ remote) against `main` via `git cherry`, emitting tab-separated lines:
   - `MERGED<TAB><branch><TAB><locality>` — the branch's content is in `main`; safe to delete.
   - `UNMERGED<TAB><branch><TAB><locality> — N commit(s) not in main (kept)` — genuinely unmerged or superseded work; **never auto-deleted.**
   It closes with a `prune: <M> merged, <U> unmerged/superseded` summary.
3. Present the result to the user: how many MERGED branches will be deleted, and — by name — any UNMERGED branches being kept (a UNMERGED branch may be a harmless superseded iteration or genuinely abandoned work; that judgment is the user's, not the skill's).
4. On user approval, run `.claude/skills/sync-skills/scripts/sync.sh prune --apply` — deletes every MERGED branch on **both** sides (`git branch -D` locally, `git push origin --delete` remotely). Idempotent — safe to re-run.
5. Report what was removed. **Do not** write a `.claude/sync-log.md` entry — `prune` is branch hygiene, not a pull/push sync action.

`prune` only ever touches the `sync/*` namespace — never `main`, never feature branches, never `agents/` or `skills/`. It refuses to run if the hitachi working tree is dirty. The conservative default (dry-run; UNMERGED kept; explicit `--apply` to delete) means a stray branch is never lost without the user seeing it first.

### `deps <skill> [<skill> ...]`

Resolve and show a skill's **dependency closure** — what else must be installed for it to work — without pulling anything. The closure has two surfaces that a naive single-skill pull misses:

1. **Sibling skills** the skill consumes (and *their* required deps, transitively), including the `shared/` utilities.
2. **Agents**, which live on a separate sync surface (`.claude/agents/`). Pulling a skill's directory never installs its agents — they must be wired by the owning skill's install action.

Use this before pulling an unfamiliar skill ("what does `gap-analysis` drag in?"), as part of `pull` Step 3b, or any time you want to know whether the project is missing a co-dependency.

1. Run `.claude/skills/sync-skills/scripts/sync.sh deps <skill> [...]`. The script reads each skill's `dependencies:` frontmatter from the **registry** (what a pull would bring) and, by default, flags every closure member not present in this project as `[MISSING locally]`. Read-only.
2. The report has four parts: **Required skills** (transitive — must co-install), **Agents** (the union across the required closure — must co-install via the owning skill's install action), **Optional skills** (listed, never auto-pulled), and a `! UNRESOLVED` line if a required dep names a skill absent from the registry.
3. Pass `--json` for machine-readable output (consumed by tooling); `--no-missing` to skip the local-presence annotation (pure closure).
4. Present the result and, if anything is `[MISSING locally]`, recommend the concrete follow-up: `pull` the missing required skills, and run `/advisors init` / `/reference-audit setup` / `/secops setup` for missing agents.

The `dependencies:` frontmatter contract (shape, `required`/`optional` semantics, the owner-lists-its-agents convention) is documented by the `skill-creator` skill — that's the authoring side; `deps` is the resolving side.

## Notes

- `$ARGUMENTS` empty or `help` → show this usage
- The script refuses any path outside `skills/` or `agents/` — it will not touch `.git/`, `project.yml`, or anything else under `.claude/`
- When the skill needs to modify `project.yml`, it does that itself (via `Edit`), not the script
- Paths are always relative to the registry root: `skills/<name>/...` or `agents/<name>`. The script joins them with the hitachi path or `.claude/` path as needed
- If the hitachi working tree is dirty, `pull` is still safe (the script reads from `origin/main`, not the working copy), but `push` will refuse until it's clean
- If there's no `gh` CLI auth, `push` will fail at Step 5 — tell the user to run `gh auth login` and re-run `push` (the commit is already pushed, so they can re-use the branch)

## Best Practices
See [README.md](README.md) — consumed by `/best-practices` audit.

## Changelog
See [README.md](README.md) for version history.

