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
  SKILL.md                            # Skill instructions (loaded by Claude)
  README.md                           # This file (design docs, not loaded)
  hooks/
    check-active-task.sh              # PreToolUse — task gate (source)
    task-activate.sh                  # State management script (source)
    session-env.sh                    # SessionStart — exports CLAUDE_SESSION_ID
    session-cleanup.sh                # SessionEnd — purges gate file, writes uncheckpointed markers
    checkpoint-recover.sh             # SessionStart — surfaces uncheckpointed markers as additionalContext
    register-hook.sh                  # Shared hook registration helper (source)
  commands/
    checkpoint.md                     # Slash command alias for `/task checkpoint`
  rules/
    scratch-and-tmp.md                # Auto-loaded rule (source)
  tests/
    test-task-gate.sh                 # Automated test suite (51 tests)
.claude/hooks/
  check-active-task.sh -> ../skills/task/hooks/check-active-task.sh    (symlink)
  session-env.sh -> ../skills/task/hooks/session-env.sh                (symlink)
  session-cleanup.sh -> ../skills/task/hooks/session-cleanup.sh        (symlink)
  checkpoint-recover.sh -> ../skills/task/hooks/checkpoint-recover.sh  (symlink)
  task-activate.sh                    # Installed by /task setup (copied, not symlinked)
  register-hook.sh                    # Shared hook registration helper (copied)
.claude/commands/
  checkpoint.md -> ../skills/task/commands/checkpoint.md               (symlink)
.claude/rules/
  scratch-and-tmp.md -> ../skills/task/rules/scratch-and-tmp.md        (symlink)
.state/                                # Gitignored — runtime state
  active-tasks-{session_id}.txt        # Gate state — one task ID per line
  last-checkpoint-{person}-{NNN}.txt   # Touched by checkpoint action — staleness signal
  uncheckpointed-{person}-{NNN}-{date}.txt  # Written by SessionEnd; consumed by SessionStart
.claude/settings.json                 # Hook wiring (PreToolUse/SessionStart/SessionEnd matchers)
```

The skill follows a single install pattern across hooks, agents, rules, and slash commands: **source of truth lives inside the skill; symlinks under `.claude/` connect it to Claude Code's discovery paths.** A `/sync-skills pull` that updates the skill auto-updates everything downstream — no separate copy step, no stale duplicates to audit. `task-activate.sh` and `register-hook.sh` are the two exceptions (copied, not symlinked) because they're written to by other tooling.

### Why a slash command at all?

The primary trigger for `checkpoint` is the skill's frontmatter description, which fires on natural-language phrases like "wrap up", "sign off", "before /clear", "make sure the task doc is updated". The slash command is a **muscle-memory alias** for users who'd rather type `/checkpoint` than express the intent in prose. Both routes invoke the same action body in SKILL.md.

### Why `/checkpoint` deliberately shadows the built-in

Claude Code ships `/checkpoint` as an alias for `/rewind` — an opaque, ephemeral snapshot of conversation+files for undo. This skill reclaims the name for a different concept: a deliberate, written refresh of the task doc to **resume-ready** state, committed to git, auditable.

The override is intentional because:
- **Audit visibility is the value prop.** In regulated workloads, "checkpoint" means a signed-off milestone, not an undo point. Auto-snapshots are useless to a reviewer; a task doc is not.
- **Forcing function.** Reinforces that the source of truth lives in committed artifacts, not Claude's hidden state.
- **The built-in is still reachable** via `/rewind`, `/undo`, or `Esc + Esc` — only one of three aliases is shadowed, and auto-snapshotting itself is untouched.

Trade-off: one-time surprise for users who learned `/checkpoint` elsewhere. Mitigated by this note and the skill's own description.

### Checkpoint-recovery hook pair

`session-cleanup.sh` (SessionEnd) and `checkpoint-recover.sh` (SessionStart) coordinate via marker files in `.state/`:

1. **During work**: each `/checkpoint` invocation `touch`es `.state/last-checkpoint-<person>-<NNN>.txt` — the mtime is the recency signal.
2. **On SessionEnd**: for each active task, if the `last-checkpoint-*` marker is missing or older than 30 minutes, write `.state/uncheckpointed-<person>-<NNN>-<date>.txt` with the session ID and task path. (Then purge the gate file as before.)
3. **On the next SessionStart**: scan for `uncheckpointed-*` markers. If any exist, emit a SessionStart `additionalContext` block telling Claude to offer retroactive `/checkpoint` recovery from `git log` + `git diff` since the task doc's last mtime. The conversation transcript is lost, but the commit/edit history isn't — usually enough.
4. **On `/checkpoint` completion**: delete any matching `uncheckpointed-*` markers so they don't resurface.

This addresses the failure mode where a user hits `/clear` or `/quit` without saying anything that would trigger description-based recovery. Hooks can't auto-invoke Claude actions, but they can persist enough breadcrumbs for the next session to recover.

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

## Version History

| Version | Date | Change |
|---------|------|--------|
| v34 | 2026-07-20 | **New `summary` action — the console Tasks tab's data producer.** `scripts/task_summary.py` (stdlib-only) derives `tasks/task-summary.json`: status counts, categorized open tasks (with the index's curated Summary one-liners), a last-N-days activity window (touched/created/closed + shipped-highlight changelog lines), a `category_icons` map, and an Economics rollup (modeled by-hand vs. self-reported agentic hours, evidence classes labeled). Parses both bullet (`- YYYY-MM-DD: …`) and table (`\| date \| msg \|`) changelog forms. The narrative/watch prose is **Claude-composed** and stamped via `--narrative`/`--watch` — the script never writes prose and preserves previous prose when the flags are omitted. Category keywords/icons default to a generic set; projects override via `tasks/task-summary-config.json` (JSON so the script stays venv-free) — never by editing the script (registry-shared). The JSON is a regenerated projection; task docs + indexes remain the source of truth. Consumed by project-console's Tasks tab (a pure reader). Ported from a sister project's fork; adapted for project-agnostic categories and this registry's changelog conventions. |
| v33 | 2026-06-30 | **Economics gets *filled* on the events that actually happen, not just at a manual checkpoint.** v32 made the `## Economics` section always *exist*; this closes the parallel gap that it only ever got *filled* at `/checkpoint` step 3b — so a task could be created, worked, and Completed with an empty stub. Three triggers now drive the fill: (1) **Todo check-off** — PERMANENT RULE 1 now says ticking a Todo off (or adding/restructuring Todos) fills the matching `## Economics` entry *in the same edit* ("checking the box is the estimate trigger"); (2) **Completion gate** — `update … Complete` step 1b refuses to close a task with an unfilled stub, filling it first (completion is the definitive estimate point); (3) **Session end** — the SessionEnd staleness threshold dropped 30 → **15 min** so a stale/unfilled task is flagged sooner for next-session recovery. `checkpoint` 3b reworded from "fill" to "**reconcile**" (most entries should already exist from todo check-offs). Per user (ben/098): the deliberately-removed per-turn nag hook (ben/100) was **not** re-introduced — all three triggers are action-gated or the existing SessionEnd hook, none per-turn. |
| v32 | 2026-06-30 | **`## Economics` is now scaffolded at task creation (was only ever added at checkpoint).** New `create` step 4b: when the `usage-metrics` skill is installed, a new task doc is born with an `## Economics` section — an empty stub carrying `method_version` + `method_ref` + `agentic_hours: null` + `todos: []` (the empty list is safely ignored by the aggregator until filled). Closes a real gap: economics was only added by `checkpoint` step 3b, so a task that never hit a `/checkpoint` — even a **Completed** one — silently carried no economics section at all (observed on sister-project docs). Checkpoint 3b reworded from "add" to "fill" the (now pre-existing) stub. Gated on usage-metrics being installed, same as PERMANENT RULE 6; skipped silently otherwise, and the rubric is never copied in (pointer only). No change to the base template when usage-metrics is absent. |
| v31 | 2026-06-30 | **`task-activate.sh` is now installed as a symlink, not a copy.** `setup` step 9 changed from copying the hook to symlinking it (`.claude/hooks/task-activate.sh` → `../skills/task/hooks/task-activate.sh`) — matching steps 5–8 for the other four task hooks. The copy was the odd one out: because it was a regular file, a `/sync-skills pull` that advanced the skill (e.g. v30's activation-ledger `log_activation`, which feeds usage-metrics per-task token attribution) left the *installed* hook stale until the next `/task setup` re-copied it. Symlinking eliminates that stale-hook window entirely — the pulled skill version is effective immediately. Step 9 gains a copy→symlink migration (replace a non-symlink `task-activate.sh`; leave a forked regular file alone). `register-hook.sh` (step 4) is deliberately left a copy — it is pre-symlink bootstrap infra other skills depend on before any symlink exists. **Post-update:** re-run `/task setup` after pulling this version to replace the copied hook with the symlink. |
| v30 | 2026-06-30 | **Task doc is now self-sufficient for resuming the effort estimate.** The embedded PERMANENT RULES block gained rule 6: it names the effort-estimation rubric (`.claude/skills/usage-metrics/references/effort-estimation-rubric.md`) as the source for the `## Economics` block, so a session resuming from the task doc **alone** — without loading the task skill — knows where to read the anchors/schema to add or refresh an estimate (gracefully skipped if `usage-metrics` isn't installed). Checkpoint step 3b now also stamps the block's `method_ref` with that path so the estimate is self-describing. Closes a resume-correctness gap: previously the "read the rubric" instruction lived only in the checkpoint action, invisible to a bare doc-only resume. Pointer only — the rubric is never copied into task docs. |
| v29 | 2026-06-10 | **`_work/` sandbox wired into the skill (completes the convention added to `rules/scratch-and-tmp.md`).** The rule had gained a third sandbox — `tasks/{person}/_work/`, the personal **committed** sandbox for task-support artifacts (data workbooks, generated reports) that are neither task docs nor controlled deliverables — but the skill itself didn't know about it. This version: (a) `create` step 2 now provisions `_work/` alongside `_scratch/`; (b) `setup` step 15 retitled to "personal-sandbox convention" and notes `_work/` is deliberately not gitignored; (c) the CLAUDE.md auto-loaded-rules pointer line now describes both sandboxes and instructs updating a stale `_scratch/`-only line; (d) the rule gains a **never-a-grounding-source** guardrail — agents must not cite `_work/` content as canonical, and semantic-search corpora must exclude `**/_work/**` (the file-locator skill's default `corpus_excludes` and walker pruning were updated in tandem). Frontmatter version also reconciled (had lagged at 27 while README was at v28). Re-running `/task setup` refreshes the CLAUDE.md pointer line; no new hooks. |
| v28 | 2026-05-17 | **Document why `/checkpoint` shadows Claude Code's built-in alias.** v27 added the slash command but didn't explain that it deliberately overrides Claude Code's built-in `/checkpoint` alias for `/rewind`. README gains a "Why `/checkpoint` deliberately shadows the built-in" subsection under "Why a slash command at all?" — covers the rationale (audit visibility is the value prop in regulated workloads, "checkpoint" means a signed-off milestone, the built-in stays reachable via `/rewind`/`/undo`/`Esc+Esc`) and the trade-off (one-time surprise for users who learned `/checkpoint` elsewhere). SKILL.md gains a one-paragraph note inside the `checkpoint` action spec so Claude sees it at trigger time (README isn't loaded into context). Pure documentation — no behavioral change, no setup re-run required. |
| v27 | 2026-05-17 | **`checkpoint` action + slash command + recovery hook pair.** New `checkpoint` action refreshes the active task doc to **resume-ready** state per the doc's own PERMANENT RULE 4 — what was completed this session with concrete artifacts, in-flight state, next-step priorities, open questions, activation command. Frontmatter description expanded with natural-language triggers ("wrap up", "sign off", "before /clear", "make sure the task doc is updated", etc.) so the skill fires on conversational session-end signals; action ends by emitting `✅ Resume-ready — safe to /clear or /quit.` as the user's signal that the doc is fully prepped. The skill now ships a slash command (`commands/checkpoint.md`) as a muscle-memory alias, installed via symlink by `setup` — same source-of-truth-in-skill pattern as hooks/rules. To handle the "user just hit /clear without warning" case, added a **hook pair**: `session-cleanup.sh` (SessionEnd) writes `.state/uncheckpointed-<person>-<NNN>-<date>.txt` markers for any active task whose `last-checkpoint-*` marker is stale (>30min) or missing; new `checkpoint-recover.sh` (SessionStart) scans for those markers and injects `additionalContext` so the next session proactively offers retroactive checkpoint from `git log` + diff. The checkpoint action `touch`es the staleness marker on completion and deletes the matching uncheckpointed marker. Also dropped `list` and `show` from the frontmatter description (frontmatter-promised-but-missing since v26; no point listing actions that aren't implemented). |
| v26 | 2026-05-17 | **Index maintenance moved into SKILL.md.** The `find` action has always read `tasks/<person>/000-index.md` to match user descriptions, but the `create` and `update` action specs lived in README.md (not loaded into Claude's context) so indexes silently drifted: rows for new tasks were never written, completed rows were never moved, and folders without an index just had `find` degrade to a no-op. This version (a) adds an explicit "## Index file format" section to SKILL.md defining the file shape, (b) extends `create` with explicit index-write steps (5–7), (c) adds a `update <person> <NNN> <status>` action that rewires the row on status change and moves it between Active/Completed tables, (d) adds a `setup` step that backfills missing indexes by parsing existing task files. Also closes a markdown rendering bug: the task-file template's opening ```` ```markdown ```` fence was never closed, so everything from the template through "## Task Gate State File" rendered as one giant code block on GitHub. |
| v25 | 2026-05-15 | **`setup` installs the scratch/tmp convention.** New step 13 idempotently installs three pieces: the auto-loaded rule `.claude/rules/scratch-and-tmp.md` (a **symlink** to the skill-owned source `rules/scratch-and-tmp.md` — same install pattern as hooks/agents, so `/sync-skills pull` auto-updates it), the `_scratch/` + `**/_scratch/` `.gitignore` patterns, and a CLAUDE.md "Auto-loaded rules" pointer section. The `create` action already provisions `tasks/{person}/_scratch/`; this closes the gap where that folder existed but was neither gitignored nor documented. The task skill owns this convention because the `_scratch/` sandbox exists only because tasks exist. Projects customize by forking the symlink into a regular file. |
| v24 | 2026-04-27 | **Default-to-action two-branch rubric.** `find` action no longer asks before activating: high-confidence match → reuse + announce in one line; anything else → create + announce in one line. The one-line announcement is the user's escape hatch. Hook denial recovery uses the same rubric and adds a "trust the denial-message UUID over `printenv`" rule for compaction/restart cases. Project-wide effect: removes the most common 2–3 message stall that was blocking team members on every fresh topic. Ported from spec-gaming task v27. (See task ben/119.) |
| v23 | 2026-04-23 | Capture redesign — retired flow-killing hooks, strategy-doc-centric conflict flow. (Task ben/100.) |
| earlier | — | See git log for prior version history. |

**Post-update (v27):** Re-run `/task setup` once. Steps 8 (symlink `checkpoint-recover.sh`), 14 (register the SessionStart hook), and 17 (symlink the slash command) are new; existing projects need them installed. Idempotent — safe to re-run.

**Post-update (v26):** Re-run `/task setup` once. The new step 14 backfills missing `000-index.md` files for every person folder that contains task files but lacks rows for them. It is idempotent — folders whose indexes already cover every task file are skipped.

**Post-update (v25):** Re-run `/task setup` once. Step 13 installs the scratch/tmp convention (rule file + gitignore patterns + CLAUDE.md pointer); it is idempotent, so re-running is safe. Behavioral changes alone (e.g. v24's rubric) need no re-run.

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

### Action specs

Action specs live in [SKILL.md](SKILL.md) (`create`, `find`, `update`, `setup`) — that's the file Claude loads when the skill triggers. The frontmatter also advertises `list` and `show` actions, but those are not yet implemented in SKILL.md; track as a follow-up.
