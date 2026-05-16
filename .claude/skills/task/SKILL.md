---
name: task
description: "Task management for regulated projects — create, find, list, update, and show tasks organized by team member with index tracking"
version: 25
updated: 2026-05-15
---

# Task Management

Manage project tasks. Usage: `/task <action> [arguments]`

## Dependencies

This skill requires the following project infrastructure. If missing, the skill will report which files are needed and how to create them.

| File | Required by | Purpose | How to create |
|------|-------------|---------|---------------|
| `tasks/` directory | All actions | Task storage | `/medtech-docs init` or `mkdir -p tasks/` |
| `project.yml` | `setup`, team validation | Team roster, security config | `/medtech-docs init` or create manually (see template below) |
| `jq` | `setup` (hook scripts) | JSON parsing for hook registration | `brew install jq` |

**Minimal `project.yml`** (if not using `/medtech-docs init`):
```yaml
project:
  name: My Project
  repo: owner/repo
team:
  active:
    - name: Your Name
      github: your-github-username
      task_folder: yourname
      role: Your Role
      email: you@company.com
      added: 2026-01-01
  inactive: []
```

When any action encounters a missing dependency, it should report:
- What file is missing
- What it's needed for
- Suggest: "Run `/medtech-docs init` to create project infrastructure, or create the file manually."

## Supporting Files

| File | Purpose |
|------|---------|
| `hooks/check-active-task.sh` | PreToolUse hook — denies Edit/Write/NotebookEdit when no active task is set. Symlinked from `.claude/hooks/`. |
| `hooks/task-activate.sh` | Activation script source — installed to `.claude/hooks/` by `setup` action (writes per-session state files into `.state/` at project root). |
| `hooks/session-env.sh` | SessionStart hook — reads `session_id` from hook JSON and exports `CLAUDE_SESSION_ID` via `CLAUDE_ENV_FILE`, making the ID available to all Bash tool calls. Required by `check-active-task.sh`. Symlinked from `.claude/hooks/` by `setup`. |
| `hooks/session-cleanup.sh` | SessionEnd hook — removes `.state/active-tasks-{session_id}.txt` when a session ends, so completed sessions don't leave orphan state files. Symlinked from `.claude/hooks/` by `setup`. |
| `hooks/register-hook.sh` | Shared hook registration helper — installed to `.claude/hooks/` by `setup` action if not already present |
| `tests/test-task-gate.sh` | Automated test suite — 18 scenarios for the task gate hook |
| `rules/scratch-and-tmp.md` | The scratch/tmp convention — canonical source for the auto-loaded rule. The `setup` action symlinks `.claude/rules/scratch-and-tmp.md` to this file (same install pattern as hooks and agents). |
| `README.md` | Design documentation (not loaded by Claude — for human reference) |

## Actions

Parse the user's argument string `$ARGUMENTS` to determine which action to perform:

### `setup`
Wire up the task gate hook and activation script for this project. Self-contained — no dependency on other skills. Idempotent — safe to re-run.

1. Verify `jq` is available (required by hooks). If missing, warn: "Install jq via `brew install jq`" and stop.
2. Create `.claude/hooks/` directory if it doesn't exist
3. Create `.state/` directory at project root if it doesn't exist (runtime state, gitignored; relocated from `.claude/state/` in task ben/083 to escape Claude Code's `.claude/**` sensitive-file guard)
4. If `.claude/hooks/register-hook.sh` does not exist, install it from `${CLAUDE_SKILL_DIR}/hooks/register-hook.sh` and make it executable. This is shared infrastructure — any skill can use it to register hooks safely.
5. Create symlink `.claude/hooks/check-active-task.sh` → `../skills/task/hooks/check-active-task.sh` (skip if already exists)
6. Create symlink `.claude/hooks/session-env.sh` → `../skills/task/hooks/session-env.sh` (skip if already exists). This hook makes `CLAUDE_SESSION_ID` available to all Bash tool calls — the task gate relies on it.
7. Create symlink `.claude/hooks/session-cleanup.sh` → `../skills/task/hooks/session-cleanup.sh` (skip if already exists). This hook purges the task-gate state file on SessionEnd.
8. Install `task-activate.sh` into `.claude/hooks/` — copy from `${CLAUDE_SKILL_DIR}/hooks/task-activate.sh` and make executable. (Skip if already exists and content matches.)
9. **Migration — uninstall deprecated capture hooks (v13 → v23)**. The Strategy/Lessons capture-nag hooks (v12–v22) have been retired; they fired on every user prompt and every response turn with a 25% hit rate and high flow cost (see task ben/100). If a project was previously set up, clean up the now-orphaned artifacts:
    - Remove dangling symlinks: `rm -f .claude/hooks/capture-signals.sh .claude/hooks/capture-check.sh`
    - Remove `UserPromptSubmit` entries whose command path ends with `capture-signals.sh`, and `Stop` entries whose command path ends with `capture-check.sh`. If either event array becomes empty after filtering, drop the array entirely. Do this with a single idempotent jq pass over `settings.json`:
      ```bash
      jq '
        .hooks.UserPromptSubmit = (
          (.hooks.UserPromptSubmit // []) 
          | map(.hooks |= map(select(.command | test("capture-signals\\.sh$") | not)))
          | map(select(.hooks | length > 0))
        )
        | .hooks.Stop = (
          (.hooks.Stop // [])
          | map(.hooks |= map(select(.command | test("capture-check\\.sh$") | not)))
          | map(select(.hooks | length > 0))
        )
        | if (.hooks.UserPromptSubmit | length) == 0 then del(.hooks.UserPromptSubmit) else . end
        | if (.hooks.Stop | length) == 0 then del(.hooks.Stop) else . end
      ' .claude/settings.json > .claude/settings.json.tmp && mv .claude/settings.json.tmp .claude/settings.json
      ```
10. Register the task gate hook using the shared helper:
    ```bash
    .claude/hooks/register-hook.sh PreToolUse "Edit|Write|NotebookEdit" command \
      '"$CLAUDE_PROJECT_DIR"/.claude/hooks/check-active-task.sh'
    ```
11. Register the session-env hook (no matcher — fires for all SessionStart events):
    ```bash
    .claude/hooks/register-hook.sh SessionStart "" command \
      '"$CLAUDE_PROJECT_DIR"/.claude/hooks/session-env.sh'
    ```
12. Register the session-cleanup hook:
    ```bash
    .claude/hooks/register-hook.sh SessionEnd "" command \
      '"$CLAUDE_PROJECT_DIR"/.claude/hooks/session-cleanup.sh'
    ```
    The helper safely appends to `settings.json` without overwriting other skills' hooks. It checks for duplicates (idempotent).
13. **Install the scratch/tmp convention.** The `_scratch/` sandbox the `create` action provisions only holds up if the project also gitignores it and the convention is discoverable. The task skill owns this convention because `_scratch/` exists only because tasks exist. Install all three pieces idempotently:
    - **Rule file** — create `.claude/rules/` if missing, then symlink `.claude/rules/scratch-and-tmp.md` → `../skills/task/rules/scratch-and-tmp.md` (skip if it already points there; repoint if the target moved; if the project has forked the rule into a regular file, leave the fork alone). Files under `.claude/rules/` are auto-loaded into every session by Claude Code; the symlink — not a copy — is what makes a `/sync-skills pull` that updates the task skill auto-update the rule, with no drift and no stale copy to audit. This is the same install pattern the skill uses for its hooks.
    - **Gitignore** — ensure `.gitignore` contains both the `_scratch/` and `**/_scratch/` patterns. If `.gitignore` exists and has neither, append this commented block; if `.gitignore` does not exist, create it with this block:
      ```
      # Personal scratch — per-person sandbox under tasks/{person}/_scratch/.
      # User-managed, never committed. See .claude/rules/scratch-and-tmp.md.
      _scratch/
      **/_scratch/
      ```
    - **CLAUDE.md pointer** — if a `CLAUDE.md` exists at the project root and does not already reference `.claude/rules/`, append this section so readers know the rule is auto-loaded and must not be restated inline:
      ```
      ## Auto-loaded rules

      Files under `.claude/rules/` are auto-loaded into every session — see those files, not this one, for the canonical text:

      - `scratch-and-tmp.md` — `tasks/{person}/_scratch/` is the only sanctioned scratch location; OS `/tmp` for transient intermediates.
      ```
      If CLAUDE.md already has an auto-loaded-rules section but no `scratch-and-tmp.md` line, add just that line.
14. Report what was done — including whether step 9 uninstalled any legacy capture hooks, and which of the three step-13 convention pieces were installed vs already present.

### `find <description>`
Search for active tasks that relate to a topic or description. This is the entry point for the task-first workflow.

1. Read every `000-index.md` across all team member folders under `tasks/`
2. Collect all **Active** tasks (not Complete)
3. Match against `<description>` using the **Task** name and **Summary** column in the index — do NOT open individual task files. The index is designed to contain enough context for matching.
4. **Default to creating a new task. Reuse only on a high-confidence existing match.** Score candidates against `<description>` and the current session context (what the user has been discussing; what was last active this session). Then branch by exactly **two** outcomes — never three:

   - **High confidence — one clear winner exists.** Announce and activate in one line: _"Activating task NNN (Task Gate Overhaul) — say so if you meant something else."_ Then proceed. Confidence is high when **any** of these holds:
     - Exactly one active task has a name or Summary that substantively matches the description (not just a stopword overlap).
     - The session has already been anchored on one specific task (recent messages, prior activation this session, or a task file the user just pointed at).
     - Only one plausible match exists across the whole active set for the topic at hand.
   - **Anything else → create a new task.** This includes: no matches, weak matches, multiple plausible matches, "kinda fits two things." Don't stop to ask "use existing or create new?" — just create + announce in one line: _"Creating task NNN — short-name for this. Say so if an existing task should own it."_ Then run `/task create <person> <short-name>` and activate. The one-line announcement is the escape hatch; the user can redirect in one reply.

5. For both branches: update the per-session state file (see "Task Gate State File" below) before returning control. No mid-flow confirmation prompt in either branch.

**Why this two-branch rubric.** The gate exists to anchor work to *some* task, not to force a deliberation about *which* task. When an existing task is a clear home, reuse it; when it isn't, the cheapest path is to create rather than to interrogate the user across 2–3 messages. The one-line announcement in both branches gives the user a single-reply escape hatch ("no, use 029" / "fold into 082 instead"). Treating ambiguity as a reason to create rather than a reason to ask removes the most common stall in the prior rubric. Cost of an occasional misfit task: one user reply to redirect or one merge later. Cost of asking on every fresh topic: a recurring 2–3 message stall.

### `create <person> <short-name>`
Create a new task for a team member.

1. Look in `tasks/<person>/` to find the highest existing task number
2. Increment by 1 (zero-padded to 3 digits) for the new task ID
3. **Ensure the person's `_scratch/` folder exists** — if `tasks/<person>/_scratch/` does not exist, `mkdir -p tasks/<person>/_scratch/`. This is a personal sandbox folder, gitignored project-wide (`_scratch/` and `**/_scratch/` patterns in `.gitignore`), for ideas, drafts, and exploratory artifacts the person wants to keep around locally during a task. The directory is local-only — it will not appear in git, and nothing inside it will ever be committed. The folder existing as an empty local directory is the signal to the user that this is where their personal scratch goes. See `.claude/rules/scratch-and-tmp.md` for the full convention — the auto-loaded rule file installed by the `setup` action. Note: Claude uses the OS-provided system `/tmp` for transient intermediates — there is no project-tree `tmp/` directory.
4. Create the task file `tasks/<person>/NNN-<short-name>.md` using this structure:

```markdown
# NNN — Task Title

**ID**: NNN
**Created**: YYYY-MM-DD
**Status**: Not Started | In Progress | Blocked | Complete
**Created By**: Name
**Owner**: Name
**Priority**: Low | Medium | High | Critical

---

## PERMANENT RULES (do not remove)

This task document is the **session-recovery point** for this work. If the current session drops, is compacted, or ends, the next session must be able to load **this file alone** and continue where we left off. That is only possible if the doc is kept current in-flight.

1. **Update at every meaningful checkpoint (HARD RULE).** After each meaningful unit of work — a converted/adopted doc, a committed change, a launched batch, a completed phase, a decision, a discovered blocker, a design pivot — update this task doc:
   - tick the relevant Todo checkbox
   - add a dated Changelog line naming the concrete artifact (commit SHA, file path, decision, blocker)
   - update any progress counts/tables in Goals
2. **Phase-end batching is OK; drift-batching is not.** Planned phases (e.g., "finish Phase 2, then log the whole phase at once") are a legitimate checkpoint — writing once per phase is fine if the phase is bounded and the write happens **at the phase boundary, before the next phase starts**. What's not OK: accumulating updates in your head across arbitrary work, waiting for "end of the session," "after the push," or the user to ask. By then a crash or context-trim has lost the state. Rule of thumb: if you can't name the specific upcoming checkpoint where you'll write the update, write it now.
3. **A commit is not a substitute.** Git history records code; this doc records the project narrative — what was done, why, what's left, what surprised us.
4. **Resume-ready before any session boundary.** Before recommending a fresh session, marking Complete, or ending work, the doc must already contain: (a) what was completed this session with concrete artifacts, (b) status of any in-flight work and temp artifacts, (c) priority-ordered next steps with file paths, (d) open questions blocking progress, (e) the exact `/task` activation command to resume.
5. **Capture strategy + lessons as they happen.** If the session produces option comparisons, scope/boundary decisions, architectural pivots, non-obvious insights, or corrected assumptions, write them into the appropriate section **in-flight** — not just in chat. Harvesting skills can only surface what was written.

Success test for this doc: a fresh Claude session, given only this file, can re-enter the work without asking the user "what were we doing?"

## Goals

_What this task aims to accomplish and why it matters to the project._

- Goal 1
- Goal 2

## Todos

_Actionable work items. Check off as completed._

- [ ] Todo item 1
- [ ] Todo item 2

## Changelog
See [README.md](README.md) for version history.

## Task Gate State File

A `PreToolUse` hook enforces that file modifications (Edit/Write/NotebookEdit) require an active task. The task skill manages the per-session state file that unlocks this gate.

**State file path:** `.state/active-tasks-{session_id}.txt` (project root, gitignored; relocated from `.claude/state/` in ben/083 to escape `.claude/**` sensitive-file guard)

One task ID per line. Per-session files ensure each terminal/session has independent gate state.

**Session ID**: To get the current session ID, run `printenv CLAUDE_SESSION_ID` via the Bash tool. A SessionStart hook sets this env var automatically at the beginning of every session. Use the **literal UUID string** in all subsequent `task-activate.sh` calls. **CRITICAL**: NEVER use `$CLAUDE_SESSION_ID`, `${CLAUDE_SESSION_ID}`, or any shell variable syntax in Bash tool calls — this triggers a "Contains expansion" security prompt requiring manual user approval. Always use the literal UUID output from `printenv`.

**When to update the state file:**

| After this action | Do this |
|-------------------|---------|
| `create` (after step 6) | Activate the new task ID |
| `find` → user selects a task to work under | Activate the selected task ID |
| `update` to "Complete" (after step 3) | Deactivate the completed task ID |

**Implementation** — use the activation script:
```bash
# First, get the session ID (do this once per session)
printenv CLAUDE_SESSION_ID
# Returns e.g.: a1b2c3d4-e5f6-7890-abcd-ef1234567890

# Activate a task — use the literal UUID from printenv
bash .claude/hooks/task-activate.sh add a1b2c3d4-e5f6-7890-abcd-ef1234567890 027

# Deactivate a task
bash .claude/hooks/task-activate.sh remove a1b2c3d4-e5f6-7890-abcd-ef1234567890 027

# Check what's active
bash .claude/hooks/task-activate.sh list a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

**If the hook denies an edit**, the denial message includes the session ID and the exact command template. Don't parrot the denial message back to the user — **decide which task to activate** using the same confidence rubric as the `find` action, then run the command.

**Recovery from hook denial:**

**Important — session ID source.** Always use the `<UUID>` printed in the denial message itself (the hook reports the actually-active session). `printenv CLAUDE_SESSION_ID` can return a stale value across compactions or session restarts. If the printenv UUID and the denial-message UUID disagree, **trust the denial message** and re-activate against that ID.

1. Note the session `<UUID>` from the denial message.
2. **Pick a task to activate** using the same two-branch rubric as `find` (default: create new; reuse only on high confidence):
   - **High confidence — reuse and activate.** If the current session is clearly anchored on one task (recent messages about it, the user referenced a specific task file, there's exactly one active task whose name/Summary matches what's being edited), announce it in one line and activate. Example: _"This edit to `.claude/skills/task/SKILL.md` is part of task 119 (Default-to-Action Rubric) — activating and retrying. Say so if you meant a different task."_
   - **Anything else — create + activate, don't ask.** No clear match, weak match, or two/three plausible matches: create a new task with a concrete name and announce in one line. Example: _"Creating task 120 — hook-debug-harness for this and activating. Say so if an existing task should own it."_ Then `/task create <person> <short-name>`, activate, and retry. Don't open-ended-ask "use existing or create new?" — the one-line announcement is the escape hatch.
3. Run the activation command with the literal UUID from the denial message:
   ```bash
   bash .claude/hooks/task-activate.sh add <UUID-from-denial> <TASK_ID>
   ```
4. Retry the edit.

## Notes
- Person names in commands are lowercase first names (e.g., `ben`, `sarah`)
- If `$ARGUMENTS` is empty or just "help", show this usage guide
- Always confirm actions with a short summary of what was done

## Best Practices
See [README.md](README.md) — consumed by `/best-practices` audit.

## Changelog
See [README.md](README.md) for version history.

