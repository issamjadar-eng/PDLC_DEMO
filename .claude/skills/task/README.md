# Task Skill — Design & Architecture

This document describes the design decisions behind the task management skill and its enforcement hook. It is not loaded by Claude during normal skill operation — it exists for human understanding.

For skill usage and instructions, see `SKILL.md`.

## Overview

The task skill manages project tasks with per-person folders, indexes, and lifecycle tracking. It is paired with a **PreToolUse hook** that enforces task discipline: no file modifications (Edit/Write/NotebookEdit) are allowed without an active task associated with the current session.

## Dependency Model

Skills declare their dependencies and fail with actionable errors when they're missing. No hidden coupling between skills.

```
project.yml          ← Project infrastructure (not owned by any skill)
  │                     Created by: /medtech-docs init, or manually
  │
  ├─ task skill      ← Reads team roster for validation
  ├─ secops checks   ← Reads email domains, allowlists, team roster
  ├─ best-practices  ← Reads for project validation
  └─ setup.sh        ← Reads for access audit

tasks/ directory     ← Project infrastructure
  │                     Created by: /medtech-docs init, or mkdir
  └─ task skill      ← All actions read/write here

jq                   ← System dependency
  │                     Installed by: brew install jq
  └─ hook scripts    ← JSON parsing for settings.json and hook I/O
```

**Principle:** Each skill checks for its dependencies at runtime and reports:
1. What's missing
2. What it's needed for
3. How to create it (recommends `/medtech-docs init` or provides manual steps)

This means the task skill works standalone in any project — you just need `tasks/`, `project.yml`, and `jq`. You don't need medtech-docs installed, but it's the easiest way to create the infrastructure.

## Components

```
.claude/skills/task/
  SKILL.md                          # Skill instructions (loaded by Claude)
  README.md                         # This file (design docs, not loaded)
  hooks/
    check-active-task.sh            # PreToolUse hook script (source)
    task-activate.sh                # State management script (source)
    register-hook.sh                # Shared hook registration helper (source)
  tests/
    test-task-gate.sh               # Automated test suite (51 tests)
.claude/hooks/
  check-active-task.sh -> ../skills/task/hooks/check-active-task.sh  (symlink)
  task-activate.sh                  # Installed by /task setup (manages state files)
  register-hook.sh                  # Shared hook registration helper
.state/                      # Gitignored — per-session state files
  active-tasks-{session_id}.txt     # One per session, one task ID per line
.claude/settings.json               # Hook wiring (PreToolUse matcher)
```

The hook source lives inside the skill package so it ships as a unit. The symlink at `.claude/hooks/` allows `settings.json` to reference it at a stable path. The activation script is copied (not symlinked) to `.claude/hooks/` by `/task setup`. State files live in `.state/` (gitignored).

## Installation

### Existing project (cloned repo)

If the repo already has the hook committed (symlink + settings.json), cloning is sufficient — everything works out of the box.

### New project

Two paths:

1. **`/medtech-docs init`** — scaffolds the full project, installs skills from the registry, then **runs each skill's `setup` action** if it has one. The task skill's `setup` action wires the hook automatically. This is a generic pattern — any skill can have a `setup` action.

2. **`/task setup`** — standalone setup, run manually after installing the task skill:
   - Creates `.claude/hooks/` and `.state/` directories
   - Creates symlink `.claude/hooks/check-active-task.sh` → `../skills/task/hooks/check-active-task.sh`
   - Installs `task-activate.sh` into `.claude/hooks/`
   - Merges `PreToolUse` hook config into `.claude/settings.json`
   - Verifies `jq` is available

Both are idempotent — safe to re-run.

### Skill Setup Convention

Any skill can define a `### \`setup\`` action in its SKILL.md. During `/medtech-docs init`, each installed skill is checked for a `setup` action and invoked if present. This allows skills to self-wire hooks, config, and dependencies without `medtech-docs` knowing the details.

### Shared Hook Registration

Skills that need hooks use `.claude/hooks/register-hook.sh` — a shared helper that safely manages `settings.json`:

```bash
.claude/hooks/register-hook.sh <event> <matcher> <type> <command>
```

The helper:
- Creates `settings.json` if missing
- Appends to the event's hook array (never overwrites other skills' hooks)
- Checks for duplicates (idempotent — safe to re-run)
- Handles empty matchers (e.g., SessionStart)

Multiple skills can register hooks for the same event without conflict — each gets its own entry in the array.

## Task Gate — How It Works

### The Rule

**Before modifying any file, there must be an active task.** This is enforced mechanically by a `PreToolUse` hook, not by LLM judgment.

### Flow

```
Claude attempts Edit/Write/NotebookEdit
  → PreToolUse hook fires
  → check-active-task.sh reads stdin JSON (file_path, session_id)
  → Checks target path against exempt list
  → If exempt (tasks/*, .claude/*) → ALLOW
  → Checks project-local state file:
      .state/active-tasks-{session_id}.txt
  → If state file exists and non-empty → ALLOW
  → Otherwise → DENY with session ID + exact recovery command
```

### State File

**Location**: `.state/active-tasks-{session_id}.txt` (project-local, gitignored)

One task ID per line. Example:
```
024
023
```

**Why project-local?**
- **Inside the sandbox** — no permission prompts when Claude writes state files
- **Gitignored** (`.state/` is in `.gitignore`) — cannot be committed
- **Per-session** (session ID in filename) — concurrent terminals don't conflict
- **Deterministic path** — `$CLAUDE_PROJECT_DIR/.state/` — no directory traversal needed

**Why not `~/.claude/projects/` (v1)?** The v1 design stored state outside the project sandbox. This caused sandbox permission prompts on every write, unreliable path discovery (Claude Code's internal directory layout is opaque), and session ID resolution failures. See task 027 for the full root cause analysis.

**Session ID**: The hook reads `session_id` from the PreToolUse stdin JSON. The task skill instructs Claude to obtain the session ID by running `printenv CLAUDE_SESSION_ID` (no `$` prefix — avoids expansion prompts) and then use the literal UUID in all subsequent `task-activate.sh` calls. The hook denial message also includes the session ID as a fallback for recovery.

**Why `printenv` instead of `${CLAUDE_SESSION_ID}` template substitution (v1–v6)?** Template variables like `${CLAUDE_SESSION_ID}` are resolved by Claude Code when the skill is loaded in the main session. But subagents read SKILL.md via the Read tool and see the raw `${CLAUDE_SESSION_ID}` text — they then pass it as a shell variable in Bash tool calls, triggering the "Contains expansion" security prompt. `printenv CLAUDE_SESSION_ID` has no `$` prefix, so it never triggers expansion detection regardless of who reads the instruction.

### Activation Script

**`.claude/hooks/task-activate.sh`** manages state files with four commands:

```bash
bash .claude/hooks/task-activate.sh add <session_id> <task_id>
bash .claude/hooks/task-activate.sh remove <session_id> <task_id>
bash .claude/hooks/task-activate.sh list <session_id>
bash .claude/hooks/task-activate.sh clear <session_id>
```

The script lives in `.claude/hooks/` (tracked in git) but writes state files to `.state/` (gitignored). It resolves the state directory as its sibling: `../state/` relative to its own location.

### Lifecycle

```
/task create NNN   →  task-activate.sh add {session_id} NNN (gate opens)
/task find → NNN   →  task-activate.sh add {session_id} NNN
Edit/Write         →  hook checks state file → ALLOW
/task update NNN complete  →  task-activate.sh remove {session_id} NNN
  (if file now empty → gate closes)
next Edit/Write    →  DENY → message includes session ID + exact command

Session crashes    →  orphan file stays in .state/, new session has new ID → harmless
```

### Multi-Session Safety

Each terminal/session gets its own state file (keyed by session ID):
```
.state/active-tasks-abc123.txt  → "024"
.state/active-tasks-def456.txt  → "018"
```

Terminal 1 completing task 024 has zero effect on Terminal 2's state.

### Exempt Paths

| Pattern | Reason |
|---------|--------|
| `*/tasks/*` | Task management: creating task docs, updating indexes, writing SECOPS.md |
| `*/.claude/*` | All project infrastructure: hooks, state files, skills, settings. The gate protects project content, not tooling. |

### What's Gated vs Not

| Tool | Gated? | Why |
|------|--------|-----|
| Edit | Yes | Primary file modification |
| Write | Yes | New file creation |
| NotebookEdit | Yes | Jupyter modifications |
| Bash | No | Can't distinguish read vs write; CLAUDE.md requires Edit/Write for file changes |
| Read/Glob/Grep | No | Read-only operations |

### Auto-Recovery on Deny

When the hook denies a tool call, the deny reason includes:
1. The **session ID** for this session
2. The **exact command** to activate a task: `bash .claude/hooks/task-activate.sh add {session_id} <TASK_ID>`
3. A hint to use `/task create` if no task exists

Claude can recover in one bash command after the first denied edit. No directory traversal, no permission prompts, no guessing.

## Testing

### Running the Test Suite

```bash
bash .claude/skills/task/tests/test-task-gate.sh
```

The test suite is self-contained — it creates its own session state files in `.state/`, runs all scenarios, and cleans up after itself.

**Requirements:** `jq`, the hook at `.claude/hooks/check-active-task.sh`, the activation script at `.claude/hooks/task-activate.sh`

### Test File

| File | Purpose |
|------|---------|
| `tests/test-task-gate.sh` | Automated test suite — 51 tests across 11 sections |

### Test Sections

| # | Section | Tests | Coverage |
|---|---------|-------|----------|
| 1 | Activation — Basic Ops | 10 | add, remove, list, clear, idempotent duplicate, file verification |
| 2 | Activation — Edge Cases | 4 | missing args, unknown action, help, nonexistent session |
| 3 | Activation — File Location | 2 | state in `.state/`, not leaked to `.claude/hooks/` |
| 4 | Hook — Core Gate | 2 | allow with task, deny without |
| 5 | Hook — Exempt Paths | 7 | tasks/\*, .claude/hooks/\*, .state/\*, .claude/skills/\*, .claude/settings.json |
| 6 | Hook — Non-Exempt | 6 | CLAUDE.md, .gitignore, project.yml, docs/, setup.sh, glossary.md |
| 7 | Hook — Multi-Task | 3 | two tasks, remove one, remove all |
| 8 | Hook — Denial Message | 3 | session ID present, activation command present, /task create hint |
| 9 | Hook — Edge Cases | 4 | empty target, empty file, deleted file, empty session ID |
| 10 | End-to-End | 6 | full lifecycle: deny → activate → allow → complete → deny (single + multi) |
| 11 | Session Isolation | 4 | two sessions independent, one completes without affecting other |

### Last Run

51/51 passed (2026-04-05)

## Design History

This enforcement mechanism was designed in task 024 (Security Posture Automation) and overhauled in task 027 (Task Gate Overhaul). Key decisions:

- **Why `PreToolUse` not `SessionStart`?** — SessionStart fires before the user says what they want. PreToolUse fires only when files are about to change.
- **Why `PreToolUse` not `UserPromptSubmit`?** — UserPromptSubmit fires on every prompt (even questions) and can't block, only advise.
- **Why per-session files not a single shared file?** — A new session must start with a closed gate. A shared file could have stale task IDs from a crashed session, silently pre-authorizing the new session. Per-session files ensure every session starts clean.
- **Why project-local (`.state/`) not `~/.claude/projects/` (v1)?** — The v1 location was outside the project sandbox, requiring permission prompts on every write. Path discovery was unreliable (Claude Code's internal directory layout is opaque). Session ID resolution failed (`${CLAUDE_SESSION_ID}` didn't resolve, `dirname $TRANSCRIPT` was inconsistent). See task 027 for the full root cause analysis.
- **Why `.claude/*` exempt instead of just `.claude/hooks/*`?** — The gate protects project content, not tooling. State files, skills, and settings all need to be writable without an active task. Broadening the exemption eliminates the possibility of the gate blocking its own recovery mechanism.
- **Why an activation script instead of inline bash?** — v1 had Claude hand-craft bash commands to find directories and write state files. This was fragile (different path resolution strategies, env var failures). A single script with a deterministic path is reliable and testable.
- **Why `printenv` for session ID?** — v1–v6 used `${CLAUDE_SESSION_ID}` template substitution, which resolves correctly for the main session but fails for subagents (they read SKILL.md via Read tool and see raw shell variable syntax, triggering expansion prompts). `printenv CLAUDE_SESSION_ID` works universally — no `$` prefix means no expansion detection. The hook denial message still includes the session ID (from stdin JSON) as a recovery fallback.
- **Why not gate Bash?** — Can't distinguish `ls` from `echo > file`. CLAUDE.md already mandates Edit/Write for file changes. Accepted gap.

See `tasks/ben/024-security-posture-automation.md` and `tasks/ben/027-task-gate-overhaul.md` for the full design discussions.

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
1. Authoring is voluntary — if a session produces a load-bearing decision (forward-looking scope / architecture / regulatory / risk call) or a non-obvious lesson, offer a Strategy or Lessons block to the user for approval and embed it in the task doc. Do not silently commit strategic content.
2. No per-session nag — the UserPromptSubmit + Stop capture hooks were retired in task skill v23 (see task ben/100). Teams review captured content at monthly cadence via `/strategy assemble` and `/lessons assemble`; the `/best-practices` audit flags when assembly is > 30 days stale.
3. This is a judgment call — a bug fix or routine reorg is not strategy. A conversation about *why* we chose one approach over another is. When in doubt, draft it and let the user decide.

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
