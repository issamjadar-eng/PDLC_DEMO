---
name: task
description: "Task management for regulated projects — `create`, `find`, `update`, `checkpoint`, `summary`, `setup` tasks organized by team member with index tracking. The `summary` action derives `tasks/task-summary.json` (counts, categorized open work, recent-activity digest, economics rollup) for the project console's Tasks tab — use it when the user says 'refresh the task summary', 'update the tasks tab', or the console shows a stale/missing task summary. The `checkpoint` action refreshes the active task doc to **resume-ready** state — use it when wrapping up for the day, before `/clear`, before `/quit`, ending the session, signing off, handing off to a fresh session, taking a break, pausing work, or any time you want to make sure the task doc captures everything needed to pick up later. Triggers on phrases like 'wrap up', 'sign off', 'handoff', 'before I clear', 'before I restart', 'save context for next session', 'make sure the task doc is updated'."
version: 35
updated: 2026-07-27
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
| `hooks/task-activate.sh` | Activation script source — symlinked into `.claude/hooks/` by `setup` action (writes per-session state files into `.state/` at project root; also appends an activation ledger under `_usage-metrics/` for per-task token attribution). |
| `hooks/session-env.sh` | SessionStart hook — reads `session_id` from hook JSON and exports `CLAUDE_SESSION_ID` via `CLAUDE_ENV_FILE`, making the ID available to all Bash tool calls. Required by `check-active-task.sh`. Symlinked from `.claude/hooks/` by `setup`. |
| `hooks/session-cleanup.sh` | SessionEnd hook — removes `.state/active-tasks-{session_id}.txt` when a session ends, AND writes `.state/uncheckpointed-<person>-<NNN>-<date>.txt` markers for any active task whose `last-checkpoint-*.txt` marker is older than 15 minutes (or missing). Symlinked from `.claude/hooks/` by `setup`. |
| `hooks/checkpoint-recover.sh` | SessionStart hook — scans `.state/` for any `uncheckpointed-*.txt` markers from previous sessions; if found, injects a SessionStart `additionalContext` block prompting Claude to offer retroactive `/checkpoint` recovery from `git log` + diff. Symlinked from `.claude/hooks/` by `setup`. Pairs with `session-cleanup.sh` and the `checkpoint` action. |
| `hooks/register-hook.sh` | Shared hook registration helper — installed to `.claude/hooks/` by `setup` action if not already present |
| `commands/checkpoint.md` | Slash command alias — thin wrapper that invokes the `checkpoint` action by name. Symlinked from `.claude/commands/` by `setup` so the user can type `/checkpoint` directly. Source of truth lives inside the skill so `/sync-skills pull` propagates updates. |
| `scripts/task_summary.py` | `summary` action — derives `tasks/task-summary.json` (counts, categorized open work, recent-activity window, economics rollup) for the project console's Tasks tab. Stdlib-only; categories overridable per-project via `tasks/task-summary-config.json` |
| `tests/test-task-gate.sh` | Automated test suite — 18 scenarios for the task gate hook |
| `rules/scratch-and-tmp.md` | The personal-sandbox convention (`_work/` committed, `_scratch/` gitignored, OS `/tmp` transient) — canonical source for the auto-loaded rule. The `setup` action symlinks `.claude/rules/scratch-and-tmp.md` to this file (same install pattern as hooks and agents). |
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
7. Create symlink `.claude/hooks/session-cleanup.sh` → `../skills/task/hooks/session-cleanup.sh` (skip if already exists). This hook fires on SessionEnd and (a) purges the task-gate state file for the ending session, (b) writes an `uncheckpointed-<person>-<NNN>-<date>.txt` marker into `.state/` for any active task whose `last-checkpoint-*.txt` marker is older than 15 minutes (or missing). The marker is the SessionStart hook's signal to offer retroactive `/checkpoint` recovery in the next session.
8. Create symlink `.claude/hooks/checkpoint-recover.sh` → `../skills/task/hooks/checkpoint-recover.sh` (skip if already exists). This hook fires on SessionStart and scans `.state/` for any `uncheckpointed-*` markers left by previous sessions; if any exist, it injects an `additionalContext` block into Claude's startup context so the new session proactively offers to recover the lost state from `git log` + diff.
9. Create symlink `.claude/hooks/task-activate.sh` → `../skills/task/hooks/task-activate.sh` (skip if it already points there). This is the same source-of-truth-in-skill pattern as the other hooks (steps 5–8): the symlink — not a copy — is what makes a `/sync-skills pull` that updates the task skill auto-update the installed hook, with no stale copy to audit. **Migration (copy → symlink):** older installs (skill ≤ v30) copied this hook as a regular file; if `.claude/hooks/task-activate.sh` exists and is **not** a symlink, replace it (`rm -f` then create the symlink) so the pulled skill version takes effect. If the project has forked it into a customized regular file, leave the fork alone and report it.
10. **Migration — uninstall deprecated capture hooks (v13 → v23)**. The Strategy/Lessons capture-nag hooks (v12–v22) have been retired; they fired on every user prompt and every response turn with a 25% hit rate and high flow cost (see task ben/100). If a project was previously set up, clean up the now-orphaned artifacts:
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
14. Register the checkpoint-recover hook (no matcher — fires for all SessionStart events; chains after session-env in registration order, which is fine since they're independent):
    ```bash
    .claude/hooks/register-hook.sh SessionStart "" command \
      '"$CLAUDE_PROJECT_DIR"/.claude/hooks/checkpoint-recover.sh'
    ```
    The helper safely appends to `settings.json` without overwriting other skills' hooks. It checks for duplicates (idempotent).
15. **Install the personal-sandbox convention.** The `_scratch/` and `_work/` sandboxes the `create` action provisions only hold up if the project also gitignores `_scratch/` (`_work/` is deliberately **not** ignored — it is meant to be committed) and the convention is discoverable. The task skill owns this convention because the sandboxes exist only because tasks exist. Install all three pieces idempotently:
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

      - `scratch-and-tmp.md` — personal sandboxes: `tasks/{person}/_work/` (committed, reviewable; never a canonical/grounding source) and `tasks/{person}/_scratch/` (gitignored, local-only); OS `/tmp` for transient intermediates.
      ```
      If CLAUDE.md already has an auto-loaded-rules section but no `scratch-and-tmp.md` line, add just that line; if the existing line predates the `_work/` sandbox (mentions only `_scratch/`), update it to the text above.
16. **Backfill missing index files.** For each `tasks/<person>/` folder that contains task files (`NNN-*.md`) but either has no `000-index.md` or has one missing rows for some task files:
    - Parse each task file for: `**ID**: NNN`, the title from the `# NNN — Title` H1 line, `**Status**: <status>`, `**Priority**: <priority>`.
    - Categorize by status: rows with `Status == Complete` go in the Completed table (ID | Task | Summary); all others go in Active (ID | Task | Status | Priority | Summary). Use the task title as the Summary placeholder.
    - Write `000-index.md` using the template in "## Index file format" below, with the parsed rows populating the tables. Preserve any existing Changelog entries; append `- YYYY-MM-DD: Index backfilled from existing task files (skill v26 install).`
    - Skip folders whose index already has rows for every task file (idempotent). The check: every `NNN-*.md` filename has a matching `| NNN |` row in either table.
17. **Install the slash command alias.** The task skill ships a `checkpoint` slash command at `commands/checkpoint.md` — a thin wrapper that invokes the `checkpoint` action by name. Create `.claude/commands/` if missing, then symlink `.claude/commands/checkpoint.md` → `../skills/task/commands/checkpoint.md` (skip if it already points there; repoint if the target moved; leave a project fork alone). This is the same install pattern the skill uses for its hooks and rules: source-of-truth lives inside the skill so `/sync-skills pull` updates it automatically; the symlink — not a copy — is what eliminates drift. Note: Claude Code does not currently sync `.claude/commands/` via the `sync-skills` registry; the slash command is installed per-project from the skill's `commands/` directory.
18. Report what was done — including whether step 10 uninstalled any legacy capture hooks, which of the three step-15 convention pieces were installed vs already present, whether the slash command symlink was created or already present, and how many person folders had indexes backfilled.

## Index file format

Each team member has an index file at `tasks/<person>/000-index.md` — a per-person table of contents that the `find` action scans **without opening individual task files**. The `create`, `update`, and `setup` actions are responsible for keeping it current; if any of them stops maintaining it, `find` silently degrades.

**Template** (used by `create` when a person folder is new, and by `setup` backfill):

```markdown
# Task Index — <Full Name>

## Active

| ID | Task | Status | Priority | Summary |
|----|------|--------|----------|---------|
| — | — | — | — | No active tasks |

## Completed

| ID | Task | Summary |
|----|------|---------|
| — | — | No completed tasks |

## Changelog

- YYYY-MM-DD: Folder created.
```

**Columns:**
- **ID** — zero-padded `NNN`, matches the task filename prefix.
- **Task** — task title (the part after `NNN — ` in the file's H1 line).
- **Status** (Active table only) — one of: Not Started, In Progress, Blocked.
- **Priority** (Active table only) — Low, Medium, High, Critical.
- **Summary** — one sentence describing the task's goals/scope. Substantive enough for `find` to match a user description against it without opening the task file. At create time, set to the task title as a placeholder; refine as Goals solidify.

**Placeholder rows** (`| — | — | … | No active tasks |`) preserve the markdown table when a section is empty. Keep them; replace when the first real row is added.

When moving a row from Active → Completed, drop the Status and Priority cells. The Completed table is intentionally narrower because completed tasks don't need triage data.

### `summary [--window N]`

Generate the project activity summary the console **Tasks tab** renders — current activities, what's open (categorized), and a short recent-window digest, WITHOUT dumping the full task list. Data lives in the repo (`tasks/task-summary.json`), regenerated on request; the console is a pure consumer.

1. Run: `python3 .claude/skills/task/scripts/task_summary.py --root <repo_root>` — derives counts (all statuses), open tasks with the index's curated one-liners + keyword categories, the last-N-days window (touched/created/closed + shipped-highlight changelog lines; both bullet `- YYYY-MM-DD: …` and table `| date | msg |` changelog forms are parsed), and the Economics rollup (modeled by-hand hours vs. self-reported agentic hours — evidence classes labeled, never conflated; in-doc `## Economics` blocks only).
2. **Compose the narrative.** Read the derived data, then write a 2–4 sentence window-in-review (what actually moved, the honest headline) and re-run with `--narrative "<text>"`; add the one thing to watch via `--watch "<text>"` when there is one. The script never writes prose — the narrative is Claude's editorial read, stamped into the JSON; without the flags the previous prose is preserved.
3. The console shows the `generated` stamp's age (fresh ≤ 7 d, aging ≤ 21 d, stale beyond) — regenerate when it goes stale, after a milestone, or when the board visibly changed.
4. The JSON is a regenerated projection — never hand-edit; task docs + indexes stay the source of truth.
5. **Category tuning is project data, not skill code.** The keyword→category map (with icons) defaults to a generic set inside the script; a project overrides it by writing `tasks/task-summary-config.json` (`{"categories": [{"name", "icon", "keywords": [...]}]}`). Never edit the script's defaults with project-specific vocabulary — the skill is registry-shared.

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

1. Look in `tasks/<person>/` to find the highest existing task number. Increment by 1 (zero-padded to 3 digits) for the new task ID. If the folder doesn't exist yet, start at `001` and `mkdir -p` the folder.
2. **Ensure the person's sandbox folders exist** — if `tasks/<person>/_scratch/` or `tasks/<person>/_work/` does not exist, `mkdir -p` each. They are the two personal sandboxes, distinguished by one axis — does it go into git?
   - `_scratch/` — gitignored project-wide (`_scratch/` and `**/_scratch/` patterns in `.gitignore`); ideas, drafts, and exploratory artifacts kept locally during a task. Local-only — nothing inside it is ever committed. The empty local directory is the signal that this is where personal scratch goes.
   - `_work/` — the personal **committed** sandbox: task-support artifacts the person wants in git and reviewable by teammates (data workbooks, generated reports, supporting outputs) that are neither a task doc nor a controlled `docs/` deliverable. Git won't show the directory until the first file lands (empty dirs are untracked), but provisioning it tells the person where committed companions go instead of loose in the task-folder root. `_work/` content is never a grounding/citation source and must be excluded from semantic-search corpora (`**/_work/**`).

   See `.claude/rules/scratch-and-tmp.md` for the full three-sandbox convention — the auto-loaded rule file installed by the `setup` action. Note: Claude uses the OS-provided system `/tmp` for transient intermediates — there is no project-tree `tmp/` directory.
3. Create the task file `tasks/<person>/NNN-<short-name>.md` using the template below. Populate the header fields as follows:
   - **Title** (`# NNN — Task Title`): generate from `<short-name>` with title-case (e.g., `project-bootstrap` → `Project Bootstrap`). The user may override.
   - `**ID**`: the new NNN.
   - `**Created**`: today's ISO date.
   - `**Status**`: `Not Started`.
   - `**Created By**` and `**Owner**`: the `<person>` arg expanded to full name. Check existing tasks in the folder for the naming convention; fall back to `project.yml` `team.active[].name` where `task_folder == <person>`.
   - `**Priority**`: `Medium` unless the user specified one.
   - Initialize the inner **Changelog** with `- YYYY-MM-DD: Task created`.
4. The task file uses this structure:

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
   - **when you tick a Todo off (or add/restructure Todos), fill/refresh the matching `## Economics` entry in the same edit** — the by-hand person-hours that unit would have taken, ranged + persona-tagged, per the rubric (if `## Economics` is present / usage-metrics is installed). **Checking the box is the estimate trigger** — don't defer it to a later checkpoint.
2. **Phase-end batching is OK; drift-batching is not.** Planned phases (e.g., "finish Phase 2, then log the whole phase at once") are a legitimate checkpoint — writing once per phase is fine if the phase is bounded and the write happens **at the phase boundary, before the next phase starts**. What's not OK: accumulating updates in your head across arbitrary work, waiting for "end of the session," "after the push," or the user to ask. By then a crash or context-trim has lost the state. Rule of thumb: if you can't name the specific upcoming checkpoint where you'll write the update, write it now.
3. **A commit is not a substitute.** Git history records code; this doc records the project narrative — what was done, why, what's left, what surprised us.
4. **Resume-ready before any session boundary.** Before recommending a fresh session, marking Complete, or ending work, the doc must already contain: (a) what was completed this session with concrete artifacts, (b) status of any in-flight work and temp artifacts, (c) priority-ordered next steps with file paths, (d) open questions blocking progress, (e) the exact `/task` activation command to resume.
5. **Capture strategy + lessons as they happen.** If the session produces option comparisons, scope/boundary decisions, architectural pivots, non-obvious insights, or corrected assumptions, write them into the appropriate section **in-flight** — not just in chat. Harvesting skills can only surface what was written.
6. **Estimation provenance (if `## Economics` is present).** This doc's `## Economics` block is the by-hand person-hour estimate, built per the effort-estimation rubric at `.claude/skills/usage-metrics/references/effort-estimation-rubric.md` (owned by the `usage-metrics` skill). To **add or refresh** an estimate on resume — even without loading the task skill — read that rubric first for the anchors, personas, and JSON schema; the block also carries a `method_ref` naming it. Skip silently if `usage-metrics` isn't installed. Point to the rubric, never copy it into this doc.

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
```

4b. **Scaffold the `## Economics` section (if the `usage-metrics` skill is installed).** If `.claude/skills/usage-metrics/` exists, insert an `## Economics` section immediately **before** `## Changelog` in the new task doc — so economics tracking is present **from creation**, not conditional on a later checkpoint ever running. Use this **empty stub**: it carries the method pointer but no estimate yet (an empty `todos` list is safely ignored by the aggregator), and gets **filled at checkpoint** per the `checkpoint` action's step 3b, against the effort-estimation rubric:

    ````markdown
    ## Economics

    _By-hand person-hour estimate, **filled at checkpoint** per the effort-estimation rubric (`usage-metrics` skill). Empty until the first completed todo is estimated; an empty `todos` list is ignored by the aggregator._

    ```json
    {
      "economics": {
        "method_version": 1,
        "method_ref": ".claude/skills/usage-metrics/references/effort-estimation-rubric.md",
        "agentic_hours": null,
        "todos": []
      }
    }
    ```
    ````

    Skip this step **silently** if `usage-metrics` isn't installed — the base task doc simply has no `## Economics` section (matching PERMANENT RULE 6's "if present" gating). Do **not** copy the rubric's content into the doc; the `method_ref` pointer is the whole link.

5. **Update `tasks/<person>/000-index.md`** — see "## Index file format" above. If the index file doesn't exist, create it from the empty template (substituting `<Full Name>` from `project.yml`). Then append a new row to the Active table:
   ```
   | NNN | <Task Title> | Not Started | <Priority> | <Task Title — refine as scope solidifies> |
   ```
   If the Active table still has only the placeholder row (`| — | — | — | — | No active tasks |`), remove the placeholder before appending. Add an index changelog line: `- YYYY-MM-DD: Task NNN created.`
6. **Activate the new task** for the current session — see "## Task Gate State File" below for the activation command and session-ID handling.
7. Show the user the created task file path, the task ID, and the Summary placeholder in the index (so they can refine it once the scope is clearer).

### `update <person> <NNN> <status>`
Change a task's status. Also rewires the corresponding row in `tasks/<person>/000-index.md` — the index and the task file must agree.

`<status>` is one of: `Not Started`, `In Progress`, `Blocked`, `Complete`.

1. Find the task file via glob `tasks/<person>/NNN-*.md`. If 0 matches, fail; if >1, list them and fail.
1b. **Completion economics gate (if `<status>` is `Complete` and the `usage-metrics` skill is installed).** Before flipping the status, ensure the task's `## Economics` block is **filled** — completion is the definitive estimate point (you know the final by-hand scope *and* the agentic hours). If the block is missing or still an unfilled stub (`todos: []` and/or `agentic_hours: null`), fill it now per `.claude/skills/usage-metrics/references/effort-estimation-rubric.md`: one `todos[]` entry per completed unit (by-hand person-hours, ranged + persona-tagged) and a real `agentic_hours`. Do **not** close a task with an empty stub — that is the exact gap that leaves work uncounted in the value rollup. Skip silently if usage-metrics isn't installed.
2. Update the `**Status**: ...` line in the task file's header to `<status>`. Add an entry to the task file's inner Changelog: `- YYYY-MM-DD: Status changed to <status>.`
3. **Update `tasks/<person>/000-index.md`** — find the row whose ID column matches `NNN` (in either Active or Completed table):
   - If new `<status>` is anything other than `Complete`:
     - If the row is in **Active**: rewrite the Status cell to `<status>`. Leave other columns alone.
     - If the row is in **Completed**: move it back to Active. Re-read `**Priority**` from the task file to populate the Priority cell. The Summary cell carries over.
   - If new `<status>` is `Complete`:
     - If the row is in **Active**: remove it from Active, append it to Completed using only the ID | Task | Summary columns (drop Status + Priority).
     - If already in **Completed**: no-op.
   - In either case, add an index changelog line: `- YYYY-MM-DD: Task NNN status → <status>.`
   - If a table empties out, restore its placeholder row (`| — | — | … | No active tasks |` / `| — | — | No completed tasks |`).
4. If new `<status>` is `Complete`, deactivate the task in the session state file — see "## Task Gate State File" below.
5. Confirm the change to the user: task file path, new status, and which index table the row now lives in.

### `checkpoint [<person> <NNN>]`
Refresh the active task doc to **resume-ready** state before a session boundary. The doc is the session-recovery point for the work — a fresh Claude session given only the file must be able to re-enter without asking "what were we doing?" This action enforces that.

Use this when wrapping up for the day, before `/clear`, before `/quit`, ending the session, signing off, handing off to a fresh session, taking a break, or any time the user signals an upcoming boundary.

**Note on `/checkpoint`:** in projects that install this skill, the `/checkpoint` slash command deliberately shadows Claude Code's built-in `/checkpoint` alias for `/rewind` — this skill's auditable, written task-doc refresh is the intended meaning here. The built-in conversation/file snapshot is still reachable via `/rewind`, `/undo`, or `Esc + Esc`. See README.md for rationale.

Args are optional. With no args, use the currently-active task. Pass `<person> <NNN>` to checkpoint a specific task explicitly.

1. **Identify the target task doc.** If args were omitted: run `printenv CLAUDE_SESSION_ID` (use the **literal UUID** in subsequent calls — see the warning in "## Task Gate State File" below), then read `.state/active-tasks-{session_id}.txt`. Use the first task ID listed; if multiple are active, prefer the most recently activated. Find the file via `tasks/*/NNN-*.md`. If no task is active and no args were given, fail with: `"No active task to checkpoint. Pass <person> <NNN> or activate a task first."`
2. **Audit the doc** against the PERMANENT RULE 4 success criteria — a fresh session must be able to recover: (a) what was completed this session with concrete artifacts (commit SHAs, PR URLs, file paths), (b) status of any in-flight work and outstanding temp artifacts, (c) priority-ordered next steps with file paths, (d) open questions blocking progress, (e) the exact `/task` activation command to resume.
3. **Refresh the Todos section.** Tick off items completed this session. Rewrite the remaining list in priority order with concrete file paths. Promote completed Todos into the Goals checklist if they were structural milestones (not just one-off chores).
3b. **Reconcile the `## Economics` estimates** (if the `usage-metrics` skill is installed). If the team is following PERMANENT RULE 1, most `todos[]` entries were **already filled as each Todo was checked off** — here you just **reconcile**: confirm every completed todo has an entry, and set/refresh the whole-task `agentic_hours`. If the section is missing (older doc) or still an empty stub, fill it now: for each todo **completed this session**, a `## Economics` entry — the **by-hand person-hours** the same work would have taken, **ranged + persona-tagged**, per `.claude/skills/usage-metrics/references/effort-estimation-rubric.md` — and replace `agentic_hours: null` with your estimate. Ensure the block's `method_ref` names that rubric path so the estimate is self-describing on a bare resume. Do it inline now (you hold the context); no approval gate. Skip silently if usage-metrics isn't installed. This is what makes the agentic-value comparison possible — the agentic side (tokens/wall-clock) is measured automatically; this is the only by-hand half.
4. **Refresh the Open Questions section.** Resolve any questions answered this session — strike them through or move to a "Resolved this session" subsection. Trim the list. Open Questions should never accumulate stale entries across multiple sessions; if the same question survived two checkpoints, surface that explicitly.
5. **Refresh the Resume → In-flight artifacts subsection.** List every file you (Claude) generated or modified this session that's expected to be reviewed/edited externally (browsers, IDEs). Note the current state of relevant external systems: git HEADs of any repos touched, merged PR URLs, deployed URLs, outstanding temp files. **Explicitly state whether anything has been committed by Claude** (it usually has not — the user controls commits).
6. **Refresh the Resume → First action on resume subsection.** List the priority-ordered first steps for the next session. Include anti-patterns to avoid: work that already shipped this session (so it isn't redone), commits not to make unless explicitly asked, sub-sessions or branches already cleaned up.
7. **Refresh the Changelog.** Add a dated entry naming what shipped this session: commit SHAs, merged PR URLs, files changed, decisions captured, lessons saved to memory.
8. **Verify the index entry** in `tasks/<person>/000-index.md` — the Status column must match the task file's `**Status**:` header. The Summary cell should reflect current scope, not the original-creation summary; update if it has drifted. If the index file is missing or doesn't have a row for this task, create/append it.
9. **Do not commit anything to git.** The user controls commits explicitly; do not assume that checkpointing implies a commit. If the project has uncommitted changes, state that clearly in the In-flight artifacts subsection so the next session knows.
10. **Write checkpoint markers.** Two state files coordinate with the SessionEnd / SessionStart hooks:
    - Write `.state/last-checkpoint-<person>-<NNN>.txt` (just `touch` it — content doesn't matter; the mtime is the signal). The SessionEnd hook (`hooks/session-cleanup.sh`) compares this mtime against a 30-minute staleness threshold to decide whether to write an `uncheckpointed-*` marker.
    - Delete any matching `.state/uncheckpointed-<person>-<NNN>-*.txt` markers — this checkpoint just made them obsolete. If the current session was triggered by a recovery markers from a previous session, this is where they get cleared.
11. **Output the resume marker.** Once all refreshes are complete, output the EXACT text on its own line as the final response:

    ```
    ✅ Resume-ready — safe to /clear or /quit.
    ```

    Nothing else after that line. This is the user's signal that the doc is fully prepped and they can safely end the session.

## Task Gate State File

A `PreToolUse` hook enforces that file modifications (Edit/Write/NotebookEdit) require an active task. The task skill manages the per-session state file that unlocks this gate.

**State file path:** `.state/active-tasks-{session_id}.txt` (project root, gitignored; relocated from `.claude/state/` in ben/083 to escape `.claude/**` sensitive-file guard)

One task ID per line. Per-session files ensure each terminal/session has independent gate state.

**Session ID**: To get the current session ID, run `printenv CLAUDE_SESSION_ID` via the Bash tool. A SessionStart hook sets this env var automatically at the beginning of every session. Use the **literal UUID string** in all subsequent `task-activate.sh` calls. **CRITICAL**: NEVER use `$CLAUDE_SESSION_ID`, `${CLAUDE_SESSION_ID}`, or any shell variable syntax in Bash tool calls — this triggers a "Contains expansion" security prompt requiring manual user approval. Always use the literal UUID output from `printenv`.

**When to update the state file:**

| After this action | Do this |
|-------------------|---------|
| `create` (step 6) | Activate the new task ID |
| `find` → high-confidence match selected | Activate the matched task ID |
| `update` setting status to `Complete` (step 4) | Deactivate the completed task ID |

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

