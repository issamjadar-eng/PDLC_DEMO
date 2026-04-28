---
name: task
description: "Task management for regulated projects — create, find, list, update, and show tasks organized by team member with index tracking"
version: 23
updated: 2026-04-23
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
13. Report what was done — including whether step 9 uninstalled any legacy capture hooks.

### `find <description>`
Search for active tasks that relate to a topic or description. This is the entry point for the task-first workflow.

1. Read every `000-index.md` across all team member folders under `tasks/`
2. Collect all **Active** tasks (not Complete)
3. Match against `<description>` using the **Task** name and **Summary** column in the index — do NOT open individual task files. The index is designed to contain enough context for matching.
4. Present results to the user:
   - **If matches found**: List the matching task(s) with ID, name, owner, and summary. Ask: _"Should I work under one of these, or create a new task?"_
   - **If no matches found**: Say so and ask: _"No active task covers this. Want me to create one?"_
5. Wait for user response before proceeding.

### `create <person> <short-name>`
Create a new task for a team member.

1. Look in `tasks/<person>/` to find the highest existing task number
2. Increment by 1 (zero-padded to 3 digits) for the new task ID
3. **Ensure the person's `_scratch/` folder exists** — if `tasks/<person>/_scratch/` does not exist, `mkdir -p tasks/<person>/_scratch/`. This is a personal sandbox folder, gitignored project-wide (`_scratch/` and `**/_scratch/` patterns in `.gitignore`), for ideas, drafts, and exploratory artifacts the person wants to keep around locally during a task. The directory is local-only — it will not appear in git, and nothing inside it will ever be committed. The folder existing as an empty local directory is the signal to the user that this is where their personal scratch goes. See `tasks/README.md` § "Personal `_scratch/` Folder" and CLAUDE.md § "Personal Scratch & System tmp" for the full convention. Note: Claude uses the OS-provided system `/tmp` for transient intermediates — there is no project-tree `tmp/` directory.
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

**If the hook denies an edit**, the denial message includes the session ID and the exact command to run. Follow it.

**Recovery from hook denial:**
1. The denial message says: `TASK GATE: No active task for session <UUID>. Run: bash .claude/hooks/task-activate.sh add <UUID> <TASK_ID>`
2. Run that exact command
3. Retry the edit

## Notes
- Person names in commands are lowercase first names (e.g., `ben`, `sarah`)
- If `$ARGUMENTS` is empty or just "help", show this usage guide
- Always confirm actions with a short summary of what was done

## Best Practices
See [README.md](README.md) — consumed by `/best-practices` audit.

## Changelog
See [README.md](README.md) for version history.

