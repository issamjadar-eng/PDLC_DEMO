---
name: task
description: "Task management for regulated projects — create, find, list, update, and show tasks organized by team member with index tracking"
version: 14
updated: 2026-04-13
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
| `hooks/task-activate.sh` | Activation script source — installed to `.claude/state/` by `setup` action. Manages per-session state files. |
| `hooks/session-env.sh` | SessionStart hook — reads `session_id` from hook JSON and exports `CLAUDE_SESSION_ID` via `CLAUDE_ENV_FILE`, making the ID available to all Bash tool calls. Required by `check-active-task.sh`. Symlinked from `.claude/hooks/` by `setup`. |
| `hooks/session-cleanup.sh` | SessionEnd hook — removes `.claude/state/active-tasks-{session_id}.txt` when a session ends, so completed sessions don't leave orphan state files. Symlinked from `.claude/hooks/` by `setup`. |
| `hooks/register-hook.sh` | Shared hook registration helper — installed to `.claude/hooks/` by `setup` action if not already present |
| `tests/test-task-gate.sh` | Automated test suite — 18 scenarios for the task gate hook |
| `README.md` | Design documentation (not loaded by Claude — for human reference) |

## Actions

Parse the user's argument string `$ARGUMENTS` to determine which action to perform:

### `setup`
Wire up the task gate hook and activation script for this project. Self-contained — no dependency on other skills. Idempotent — safe to re-run.

1. Verify `jq` is available (required by hooks). If missing, warn: "Install jq via `brew install jq`" and stop.
2. Create `.claude/hooks/` directory if it doesn't exist
3. Create `.claude/state/` directory if it doesn't exist
4. If `.claude/hooks/register-hook.sh` does not exist, install it from `${CLAUDE_SKILL_DIR}/hooks/register-hook.sh` and make it executable. This is shared infrastructure — any skill can use it to register hooks safely.
5. Create symlink `.claude/hooks/check-active-task.sh` → `../skills/task/hooks/check-active-task.sh` (skip if already exists)
6. Create symlink `.claude/hooks/session-env.sh` → `../skills/task/hooks/session-env.sh` (skip if already exists). This hook makes `CLAUDE_SESSION_ID` available to all Bash tool calls — the task gate relies on it.
7. Create symlink `.claude/hooks/session-cleanup.sh` → `../skills/task/hooks/session-cleanup.sh` (skip if already exists). This hook purges the task-gate state file and the capture-armed/exit-pending markers on SessionEnd.
8. Create symlink `.claude/hooks/capture-signals.sh` → `../skills/task/hooks/capture-signals.sh` (skip if already exists). This hook detects strategic-intent entry/exit signals in user prompts and arms the Strategy/Lessons capture check (v12+).
9. Create symlink `.claude/hooks/capture-check.sh` → `../skills/task/hooks/capture-check.sh` (skip if already exists). This hook is the hard backstop that blocks `Stop` events when an armed task still lacks capture (v12+).
10. Install `task-activate.sh` into `.claude/hooks/` — copy from `${CLAUDE_SKILL_DIR}/hooks/task-activate.sh` and make executable. (Skip if already exists and content matches.)
11. Register the task gate hook using the shared helper:
    ```bash
    .claude/hooks/register-hook.sh PreToolUse "Edit|Write|NotebookEdit" command \
      '"$CLAUDE_PROJECT_DIR"/.claude/hooks/check-active-task.sh'
    ```
12. Register the session-env hook (no matcher — fires for all SessionStart events):
    ```bash
    .claude/hooks/register-hook.sh SessionStart "" command \
      '"$CLAUDE_PROJECT_DIR"/.claude/hooks/session-env.sh'
    ```
13. Register the session-cleanup hook:
    ```bash
    .claude/hooks/register-hook.sh SessionEnd "" command \
      '"$CLAUDE_PROJECT_DIR"/.claude/hooks/session-cleanup.sh'
    ```
14. Register the capture-signals hook (UserPromptSubmit — arms strategic intent and injects soft nudges):
    ```bash
    .claude/hooks/register-hook.sh UserPromptSubmit "" command \
      '"$CLAUDE_PROJECT_DIR"/.claude/hooks/capture-signals.sh'
    ```
15. Register the capture-check hook (Stop — hard backstop for uncaptured armed tasks):
    ```bash
    .claude/hooks/register-hook.sh Stop "" command \
      '"$CLAUDE_PROJECT_DIR"/.claude/hooks/capture-check.sh'
    ```
    The helper safely appends to `settings.json` without overwriting other skills' hooks. It checks for duplicates (idempotent).
16. Report what was done

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
3. Create the task file `tasks/<person>/NNN-<short-name>.md` using this structure:

```markdown
# NNN — Task Title

**ID**: NNN
**Created**: YYYY-MM-DD
**Status**: Not Started | In Progress | Blocked | Complete
**Created By**: Name
**Owner**: Name
**Priority**: Low | Medium | High | Critical

---

## Goals

_What this task aims to accomplish and why it matters to the project._

- Goal 1
- Goal 2

## Todos

_Actionable work items. Check off as completed._

- [ ] Todo item 1
- [ ] Todo item 2

## Changelog

_Reverse-chronological record of meaningful progress, decisions, and blockers._

- YYYY-MM-DD: Task created
```

Optional sections — add when the task needs them:
- **References**: Links to guidance docs, related tasks, external sources (`| Ref | Description | Location |`)
- **Analysis**: Findings, reasoning, design decisions, conclusions
- **Outcome**: Final result or decision when task is complete

**Strategy and Lessons Learned are not "optional when convenient" — they are soft-required whenever the task generates that kind of content.** Harvesting skills (`/strategy`, `/lessons`) can only surface what was written, so missing capture = permanently lost context.

- **Strategy**: Add a Strategy section whenever the task involves any of: choosing between alternatives, defining or redrawing scope/boundaries, regulatory pathway decisions, predicate selection, architecture trade-offs, module boundary calls, or risk posture decisions. Use the format: `<!-- STRATEGY CONTENT: domain, topic1, topic2 -->` where domain is one of: regulatory, commercial, architecture, development, testing, risk, postmarket. Harvested by `/strategy` skill.
- **Lessons Learned**: Add a Lessons Learned section whenever the task surfaces a non-obvious insight, a corrected assumption, a reusable pattern, or a "why" that won't be derivable from the final code/doc alone. Use the format: `<!-- LESSONS LEARNED: category1, category2 -->`. Harvested by `/lessons` skill.

**Capture discipline for Claude:**
1. Watch for the triggers above during the session, not just at the end.
2. Before marking a task Complete (or ending a session that touched a task), check whether those triggers fired. If yes, draft a Strategy or Lessons block and offer it to the user for approval — do not silently commit strategic content.
3. If the session genuinely had no qualifying content, add a changelog line: `- YYYY-MM-DD: No strategy/lessons content this session` so the absence is intentional, not forgotten.
4. This is still a judgment call — a bug fix or routine reorg is not strategy. A conversation about *why* we chose one approach over another is. When in doubt, draft it and let the user decide.

When creating, populate:
   - Set **ID** to the new NNN
   - Set **Created** to today's date
   - Set **Status** to "Not Started"
   - Set **Created By** and **Owner** to `<person>` (use their full name — check existing tasks in their folder for the convention)
   - Set **Priority** to "Medium" (unless the user specifies otherwise)
   - Initialize the **Changelog** with `- YYYY-MM-DD: Task created`
4. Add the task to the Active table in `tasks/<person>/000-index.md` — include a **Summary** column with a one-line description of the task's goals/scope (not just the task name). This summary must be descriptive enough for `/task find` to match by topic without opening the task file.
5. If `tasks/<person>/` doesn't exist yet, create the folder and a new `000-index.md` with empty Active and Completed tables
6. Show the user the created file path and task ID

### `list [person]`
List tasks, with optional filtering.

- `list` — Show all active tasks across all team members
- `list <person>` — Show all tasks (active and completed) for that person
- `list all` — Show all tasks across all team members (active and completed)

Read each person's `000-index.md` and display the results.

### `update <person> <NNN> <status>`
Update a task's status.

1. Read the task file `tasks/<person>/NNN-*.md` (glob to find it by number)
2. Update the **Status** field in the header to the new status
3. If status is "Complete":
   - Move the entry from Active to Completed in `tasks/<person>/000-index.md`
   - Remove the Status column (completed tasks don't need it)
4. If status changes from "Complete" back to something else, move it back to Active
5. Add a changelog entry: `- YYYY-MM-DD: Status changed to <status>`
6. Confirm the change to the user

### `show <person> <NNN>`
Display a task's contents. Read and show the file `tasks/<person>/NNN-*.md`.

## Task Gate State File

A `PreToolUse` hook enforces that file modifications (Edit/Write/NotebookEdit) require an active task. The task skill manages the per-session state file that unlocks this gate.

**State file path:** `.claude/state/active-tasks-{session_id}.txt` (project-local, gitignored)

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

<!-- Read by /best-practices skill to audit project setup -->

| Check | How to Verify | Severity | Scope |
|-------|--------------|----------|-------|
| Task folder exists | `tasks/` directory exists | Required | shared |
| Task README exists | `tasks/README.md` exists | Required | shared |
| At least one person subfolder | At least one subfolder under `tasks/` containing `000-index.md` | Required | shared |
| Task structure defined in skill | `create` action in task skill contains the task document structure | Required | shared |
| CLAUDE.md enforces task-first | `CLAUDE.md` contains "Task-First Workflow" section | Required | shared |
| Task skill installed | `.claude/skills/task/SKILL.md` exists | Required | shared |
| Index is current | Every task file's Status matches its position (Active vs Completed) in its `000-index.md` | Recommended | shared |
| Index has summaries | Every row in `000-index.md` has a non-empty Summary column | Required | shared |
| No orphan tasks | Every task file in a person's folder has a corresponding row in their `000-index.md` | Recommended | shared |

## Changelog

- 14 (2026-04-13): Added `Scope` column to the Best Practices table so `/best-practices` v8+ (which introduced Scope-column parsing under the unified sub-DHF shape) can classify every task-skill check as `shared`, `per-dhf`, `per-submission`, or `cross-cutting`. Every task-skill check is classified as `shared` — task management is project-level (the `tasks/` folder lives at project root, not inside any sub-DHF). See `tasks/ben/007-sub-dhf-migration.md` P5.7 for the Scope column spec. **This is a LOCAL divergence from upstream pending a future `/sync-skills push`**; upstream (hitachi) still ships v13 without the Scope column. When the Scope-column feature is contributed back to hitachi, all skills' check tables will get the column in one coordinated update.
  **Post-update:** No user action needed. The Scope column is additive — `/best-practices` v8 defaults to `shared` when the column is absent, so v13 behavior is preserved as a fallback.
- 13 (2026-04-13): Extended `setup` action to symlink and register the two capture-backstop hooks introduced in v12: `capture-signals.sh` (UserPromptSubmit — detects strategic-intent entry/exit signals, arms and soft-nudges) and `capture-check.sh` (Stop — hard backstop blocking `Stop` events when armed tasks lack capture). Previously downstream users pulling v12 got the hook files but had no automated path to register them, leaving the capture backstop silently inactive. Now `/task setup` wires everything up in one idempotent command. First skill to adopt the new post-update annotation convention added in sync-skills v3 — the block below is what `/sync-skills pull` will surface to downstream users.
  **Post-update:** Run `/task setup` to symlink and register the new UserPromptSubmit and Stop hooks. Without this, the capture backstop is installed but inactive — your task sessions won't arm on strategic intent signals and won't be blocked from ending with uncaptured Strategy/Lessons content. The setup action is idempotent, so running it on a project that already has the earlier hooks registered is safe.
- 12 (2026-04-13): Reframed Strategy and Lessons Learned sections from "optional" to soft-required with explicit trigger lists and capture discipline for Claude. Root cause: the prior "add when the task needs them" framing caused Claude to skip capture even when sessions were clearly architectural/strategic, leaving `/strategy` and `/lessons` skills nothing to harvest. New template spells out triggers (choosing between alternatives, scope calls, trade-offs, non-obvious insights), requires end-of-session review, and requires an explicit "no content this session" changelog note when nothing qualifies. Added `capture-signals.sh` (UserPromptSubmit) and `capture-check.sh` (Stop) hooks implementing the armed-state-machine backstop. Paired with feedback memory `feedback_capture_strategy_lessons.md`.
  **Post-update:** Run `/task setup` to symlink and register the new UserPromptSubmit and Stop hooks. (Retroactively annotated in v13 — v12 shipped before the post-update annotation convention existed, so users who pulled v12 between its release and v13 had no signal that registration was required.)
- 11 (2026-04-12): Task skill now owns `session-env.sh` and `session-cleanup.sh` (moved from `.claude/hooks/` into `hooks/` in the skill). `setup` action extended to symlink both into `.claude/hooks/` and register SessionStart (session-env) + SessionEnd (session-cleanup) hooks via `register-hook.sh`. Rationale: session-env exports the ID the task gate depends on, and session-cleanup removes the task-gate state file — both are task-skill concerns, not security. This means `/medtech-docs init` Step 5 auto-wires them when it discovers `/task setup`. See task 049.
- 10 (2026-04-08): Robust session ID. SessionStart hook (`session-env.sh`) reads `session_id` from hook JSON and exports as `CLAUDE_SESSION_ID` via `CLAUDE_ENV_FILE`. Hook JSON session_id is consistent across parent and subagent sessions. `check-active-task.sh` prefers env var, falls back to hook JSON for subagents where env var isn't inherited. `uuidgen` fallback if JSON has no session_id.
- 9 (2026-04-08): Added optional Strategy and Lessons Learned sections to task document template. Strategy sections use `<!-- STRATEGY CONTENT: domain, topics -->` tags harvested by `/strategy` skill. Lessons sections use `<!-- LESSONS LEARNED: categories -->` tags for future `/lessons` skill. See task 035.
- 8 (2026-04-08): Fix session ID discovery. `CLAUDE_SESSION_ID` was not an env var — `printenv` returned nothing. Added SessionStart hook (`session-env.sh`) that writes `CLAUDE_SESSION_ID` to `CLAUDE_ENV_FILE`, making it a real env var for all Bash tool calls. Multi-session safe (each session gets its own env).
- 7 (2026-04-08): Fix subagent expansion prompts. Replace `${CLAUDE_SESSION_ID}` template variable with `printenv CLAUDE_SESSION_ID` instruction. Template variables are resolved for the main session but appear as raw shell syntax to subagents reading the file via Read tool.
- 6 (2026-04-07): Auto-purge stale state files. `check-active-task.sh` now deletes state files older than 7 days on every invocation. Added `purge` subcommand to `task-activate.sh` for manual cleanup. See task 037.
- 5 (2026-04-05): Moved task gate state from `~/.claude/projects/` to `.claude/state/` (project-local, gitignored). Added `task-activate.sh` script for state management. Hook denial message now includes session ID for one-command recovery. Replaced complex bash snippets with single `task-activate.sh` calls. Expanded exempt paths to `.claude/*`. See task 027.
- 4 (2026-04-05): Added task gate enforcement. PreToolUse hook denies file modifications without an active task. Per-session state file at `~/.claude/projects/`. Task skill manages state file on create/find/complete. Added hooks/ directory and README.md to skill package.
- 3 (2026-03-30): Migrated from .claude/commands/ to .claude/skills/ directory structure. Updated best-practices check path.
- 2 (2026-03-30): Embedded task document structure inline; removed external template dependency. Added version frontmatter and changelog.
- 1 (2026-03-23): Initial version — task management with find, create, list, update, show actions.
