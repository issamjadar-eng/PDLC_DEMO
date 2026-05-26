---
name: skill-creator
description: |
  Create, modify, audit, and measure skills. Owns the trigger surface (frontmatter `description` + § Actions) of every skill in `.claude/skills/<name>/`.

  TRIGGER when the user wants to **create, modify, edit, extend, fix, refactor, audit, evaluate, optimize, package, or test any skill** — including:
    - Explicit skill work: "create a skill for X", "make a new skill", "modify the X skill", "optimize the X skill description", "run evals on the X skill", "package the X skill"
    - Maintenance / extension framed as feature work: "add an action to X skill", "extend X to also handle Y", "fix a bug in the Y skill", "the Z skill should also do W", "add Confluence support to change-control", "add internal review tier to <skill>"
    - Path-based — ANY edit/write to files under `.claude/skills/<name>/`, especially `SKILL.md` (frontmatter or § Actions), `actions/`, `hooks/`, or `scripts/`. **If the deliverable lands in `.claude/skills/`, the work IS skill modification regardless of how the user frames it.** Past tasks built/modified skills end-to-end without firing this skill because they were framed as feature tiers — that gap is what these triggers fix.
    - Audit / quality: "are the trigger words for X conflicting with Y?", "audit the triggers on the X skill", "does the X skill description handle natural language?", "is the X skill being undertriggered?", "check skill X against other skills"
    - Skill conventions: "how should I structure a skill", "what goes in SKILL.md vs README", "skill conventions"

  Actions: `setup`, `audit-triggers <skill>`, `improve-description <skill>`, `package <skill>`, plus the iterative create/eval/improve flow described below.

  A PreToolUse hook (installed by `setup`) emits a one-line reminder when a SKILL.md frontmatter or § Actions section is edited — armed once per skill per session, auto-cleared when `audit-triggers` runs or the session ends, body-only edits skipped.
version: 7
updated: 2026-05-15
---

# Skill Creator

A skill for creating new skills and iteratively improving them — adapted from Anthropic's skill-creator with project-specific conventions for self-contained, versioned, symlink-based skills.

At a high level, the process of creating a skill goes like this:

- Decide what you want the skill to do and roughly how it should do it
- Write a draft of the skill
- Create a few test prompts and run claude-with-access-to-the-skill on them
- Help the user evaluate the results both qualitatively and quantitatively
  - While the runs happen in the background, draft some quantitative evals if there aren't any (if there are some, you can either use as is or modify if you feel something needs to change about them). Then explain them to the user (or if they already existed, explain the ones that already exist)
  - Use the `eval-viewer/generate_review.py` script to show the user the results for them to look at, and also let them look at the quantitative metrics
- Rewrite the skill based on feedback from the user's evaluation of the results (and also if there are any glaring flaws that become apparent from the quantitative benchmarks)
- Repeat until you're satisfied
- Expand the test set and try again at larger scale

Your job when using this skill is to figure out where the user is in this process and then jump in and help them progress through these stages. So for instance, maybe they're like "I want to make a skill for X". You can help narrow them down, write a draft, write the test cases, figure out how they want to evaluate, run all the prompts, and repeat.

On the other hand, maybe they already have a draft of the skill. In this case you can go straight to the eval/iterate part of the loop.

Of course, you should always be flexible and if the user is like "I don't need to run a bunch of evaluations, just vibe with me", you can do that instead.

Then after the skill is done (but again, the order is flexible), you can also run the skill description improver, which we have a whole separate script for, to optimize the triggering of the skill.

## Supporting Files

| File | Purpose |
|------|---------|
| `templates/skill-md.md` | SKILL.md skeleton with all required sections and frontmatter |
| `templates/readme-skill.md` | README.md template for new skills (design doc) |
| `templates/hook-template.sh` | Shell hook boilerplate for new hook scripts |
| `agents/grader.md` | Subagent: evaluates assertions against outputs |
| `agents/comparator.md` | Subagent: blind A/B comparison between two outputs |
| `agents/analyzer.md` | Subagent: analyzes why one version beat another |
| `references/schemas.md` | JSON schemas for evals, grading, benchmark, comparison, analysis |
| `scripts/` | Python automation: eval runner, benchmark aggregation, description optimization, **trigger audit** |
| `scripts/audit_triggers.py` | `audit-triggers` action — runs trigger eval + cross-skill conflict scan, produces report |
| `hooks/skill-md-watch.py` | PreToolUse hook — fires once per skill per session when SKILL.md frontmatter / § Actions is edited; reminds to run `audit-triggers` |
| `hooks/skill-md-watch-cleanup.sh` | SessionEnd hook — clears per-session armed state |
| `eval-viewer/` | HTML review interface and feedback collection |
| `assets/eval_review.html` | Interactive trigger eval query editor |

## Actions

### `setup`

Install the SKILL.md watch hooks (PreToolUse + SessionEnd) into `.claude/settings.json`. Idempotent — safe to re-run.

Steps:
1. Verify `jq` and `.claude/hooks/register-hook.sh` are present (the latter is installed by `/task setup`).
2. Create `.state/` at project root if missing (gitignored runtime state).
3. Symlink `.claude/hooks/skill-creator-watch.py` → `../skills/skill-creator/hooks/skill-md-watch.py` (skip if exists).
4. Symlink `.claude/hooks/skill-creator-cleanup.sh` → `../skills/skill-creator/hooks/skill-md-watch-cleanup.sh` (skip if exists).
5. Register PreToolUse hook on `Edit|Write|NotebookEdit` matcher pointing at `skill-creator-watch.py`.
6. Register SessionEnd hook (no matcher) pointing at `skill-creator-cleanup.sh`.
7. Report what was wired vs already present.

### `audit-triggers <skill-name>`

Audit a skill's trigger surface. Produces a report covering:

1. **Trigger eval** — runs 20 evaluation queries against the skill's current frontmatter description via `claude -p` (uses existing `scripts/run_eval.py` infrastructure):
   - 10 should-trigger paraphrases covering: explicit skill work ("modify the X skill"), maintenance/feature framings ("add an action to X", "extend X to handle Y", "fix bug in X"), path-based ("I'm editing `.claude/skills/X/SKILL.md`"), natural language ("we want to do <X's domain> on <object>").
   - 10 should-not-trigger near-misses — feature work outside skill scope, similar-vocabulary tasks for other skills, generic "improve X" where X isn't a skill.
2. **Cross-skill conflict scan** — pure-Python checks against every other skill in the project:
   - **Trigger-verb overlap with object-disambiguation** — flags only conflicts where verb AND likely object overlap.
   - **PreToolUse hook matcher collisions** — scans every SKILL.md for hook registration patterns; reports stacking/conflict.
   - **Project-name leakage** — regex against `project.yml` `project.name` and DHF leaf names; skills must stay project-agnostic.
   - **`actions/` vs § Actions documentation drift** — flags any file under `actions/` not documented in SKILL.md, and vice versa.
3. **Pass/fail summary** + concrete remediation suggestions.

Output: stdout report + JSON log to `.state/skill-creator-audit-<skill>-<YYYY-MM-DD>.json`. Clears the skill from the per-session armed state (so the watch hook can re-fire if the skill is edited again).

This action is **automatically recommended** by the SKILL.md watch hook whenever a skill's frontmatter or Actions section is edited.

### Iterative create / improve flow

(Existing — see "Communicating with the user" + scripts/run_loop.py for the eval+improve loop.)

## Communicating with the user

The skill creator is liable to be used by people across a wide range of familiarity with coding jargon. Pay attention to context cues to understand how to phrase your communication. In the default case:

- "evaluation" and "benchmark" are borderline, but OK
- for "JSON" and "assertion" you want to see serious cues from the user that they know what those things are before using them without explaining them

It's OK to briefly explain terms if you're in doubt, and feel free to clarify terms with a short definition if you're unsure if the user will get it.

---

## Project Skill Conventions

Every skill created in this project MUST follow these conventions. Read the templates in `${CLAUDE_SKILL_DIR}/templates/` and use them as starting points.

### Required Skill Structure

```
skill-name/
├── SKILL.md          # Required — skill instructions with YAML frontmatter
├── README.md         # Required — design document (not loaded during operation)
├── hooks/            # Optional — shell hooks (source of truth; .claude/hooks/ symlinks here)
├── agents/           # Optional — subagent prompt files (.claude/agents/ symlinks here)
├── rules/            # Optional — auto-loaded rule files (.claude/rules/ symlinks here)
├── templates/        # Optional — output templates, scaffolding templates
├── references/       # Optional — docs loaded into context as needed
├── scripts/          # Optional — executable code for deterministic/repetitive tasks
└── assets/           # Optional — files used in output (HTML templates, icons, fonts)
```

### Required YAML Frontmatter

Every SKILL.md MUST have these fields:

```yaml
---
name: skill-name
description: "When to trigger, what it does. Be pushy — combat undertriggering."
version: 1
updated: YYYY-MM-DD
---
```

- **name**: Skill identifier (kebab-case)
- **description**: Primary triggering mechanism. Include both what the skill does AND specific contexts for when to use it. Make descriptions "pushy" to combat undertriggering
- **version**: Integer, incremented on each meaningful change
- **updated**: ISO date of last version bump

### Required SKILL.md Sections

Every SKILL.md must include these sections (use the template as a starting point):

| Section | Purpose | Required |
|---------|---------|----------|
| `## Supporting Files` | Table listing all bundled files and their purpose | Yes |
| `## Actions` | Action definitions with step-by-step instructions | Yes (if skill has actions) |

**Optional but recommended SKILL.md sections:**

| Section | Purpose | When to include |
|---------|---------|-----------------|
| `## Subagent Delegation` | Table: scenario → agent type → prompt file | When skill uses agents |
| `## Dependencies` | Table: file → required by → purpose | When skill reads/writes outside itself |
| `## Notes` | Operational caveats, fallback behavior | When non-obvious |

### Required README.md Sections

These sections belong in **README.md** (not SKILL.md). SKILL.md is loaded into Claude's context every time the skill triggers — Changelog history and health-check tables don't help Claude execute the skill. README.md is never auto-loaded, so keeping this metadata there costs nothing at runtime.

| Section | Purpose | Required |
|---------|---------|----------|
| `## Best Practices` | Table of health checks consumed by `/best-practices` audit | Yes |
| `## Changelog` | Reverse-chronological version history | Yes |

### Best Practices Table Format

Goes in **README.md**:

```markdown
## Best Practices

<!-- Consumed by /best-practices audit -->

| Check | How to Verify | Severity | Scope |
|-------|--------------|----------|-------|
| Skill has SKILL.md | File exists at skill root | Required | shared |
| Frontmatter complete | name, description, version, updated all present | Required | shared |
| README.md exists | Design doc at skill root | Required | shared |
| Changelog current | Latest entry matches version number | Required | shared |
```

Severity: `Required` or `Recommended`. Scope: `shared` (project-wide) or `local` (skill-specific).

### Changelog Format

Goes in **README.md**:

```markdown
## Changelog

- 3 (2026-04-16): Description of what changed in version 3 of the skill
- 2 (2026-04-15): Description of what changed in version 2 of the skill
- 1 (2026-04-14): Initial version — what the skill does, adapted from what
```

**Skill-scoped only.** Each entry describes what changed in the skill itself — new actions, schema changes, behavior changes, bug fixes. The skill changelog is not a journal of project work that used the skill. Specifically:

- ❌ No project-specific names (companies, devices, codenames).
- ❌ No project task references (e.g. `ben/118`, `ros/045`).
- ❌ No project-level outcomes ("backfilled 52 references in regulatory-strategy.md").
- ✅ Yes skill capability changes ("added `--dry-run` flag to `push` action").
- ✅ Yes skill schema/contract changes ("`version:` field is now required in frontmatter").
- ✅ Yes skill bug fixes ("fixed BSD-vs-GNU `find -maxdepth` ordering").

If a skill change was driven by a project's needs, describe the skill change neutrally. Project context lives in commit history and the task doc, not in the skill's changelog.

### Project-Agnostic Authoring (HARD RULE)

Skills under `.claude/skills/` and bundled agents under `.claude/skills/*/agents/` must be **project-agnostic** — usable by any medtech project from the registry. They contain no project-specific names: no company names, no device codenames, no project task IDs, no team members, no Jira project keys.

Allowed placeholders in examples: `MedTech Project`, `MedTech Company`, `<device>`, `PROJECT-1234`. These signal "fill in your own value here."

Project-specific values belong in:
- `project.yml` (read at runtime by the skill)
- `docs/` (the project's authored documents)
- `tasks/` (the project's task docs)
- `CLAUDE.md` (the project's own rules)

**Never** in `.claude/skills/**` or `.claude/agents/**`. If a skill needs a per-project value, it reads it from `project.yml` — it does not hard-code anything. A skill that hard-codes one project's names becomes a fork; the registry's project-agnostic abstraction is what lets it serve every project.

### Self-Contained Skills & Symlink Pattern

Skills are self-contained — all hooks, agents, rules, templates, and scripts live inside the skill directory. Claude Code only discovers hooks from `.claude/hooks/`, subagents from `.claude/agents/`, and auto-loaded rules from `.claude/rules/`, so a skill that ships any of these must populate those directories with **symlinks** back to the skill-owned source. Never copy.

**Why symlinks:** When a skill is updated (via `/sync-skills pull`), the installed hooks, agents, and rules update automatically. No separate copy step, no drift, no stale duplicates to audit.

**Setup action pattern** — every skill that ships hooks, agents, or rules must have a `setup` action that:

1. Creates `.claude/hooks/`, `.claude/agents/`, `.claude/rules/`, and `.state/` (at project root) directories as needed.
2. For each hook script in the skill's `hooks/`, creates a symlink:
   `.claude/hooks/my-hook.sh` → `../skills/my-skill/hooks/my-hook.sh`
3. For each agent file in the skill's `agents/`, creates a symlink:
   `.claude/agents/my-agent.md` → `../skills/my-skill/agents/my-agent.md`
4. For each rule file in the skill's `rules/`, creates a symlink:
   `.claude/rules/my-rule.md` → `../skills/my-skill/rules/my-rule.md`
   Rules under `.claude/rules/` are auto-loaded into every session. Symlinking (not copying) is what lets a `/sync-skills pull` that updates the skill auto-update the rule. A project customizes a rule by forking the symlink into a regular file — `/sync-skills` leaves forks alone, exactly as it does for agents. Because the canonical source lives under `skills/<name>/rules/` (a normal file), `/sync-skills` diffs that real file and never sees the `.claude/rules/` symlink — so there is no symlink-vs-content false positive for rules.
5. For each hook, registers it via the shared helper:
   ```bash
   .claude/hooks/register-hook.sh <Event> "<matcher>" command \
     '"$CLAUDE_PROJECT_DIR"/.claude/hooks/my-hook.sh'
   ```
6. Reports what was done.

The setup action must be **idempotent** — safe to re-run. Skip symlinks that already exist and point at the right target; replace (don't silently keep) symlinks whose target has moved. The register helper already checks for duplicates.

**Agent ownership rule:** the skill's `agents/` directory is the source of truth. A project that wants to customize an advisor forks the agent file (converts the symlink into a regular file); `/sync-skills` and `/advisors sync` detect the divergence and leave forks alone.

**Registry-level `agents/` directory** (hitachi root `agents/`): only for cross-skill registry agents that don't belong to any one skill (e.g., `project-secops.md` is owned by the `secops` skill and lives under `skills/secops/agents/`, not at the registry root). Do not push per-skill agent files to the registry root.

### Multi-Hook Coexistence (HARD RULE)

Multiple skills can — and routinely do — register hooks against the **same event** (e.g., `task` and `change-control` both hook PreToolUse on `Edit|Write|NotebookEdit`; `task`, `secops`, and `digest` all hook SessionStart). Claude Code chains them in registration order. The shared `.claude/hooks/register-hook.sh` helper handles JSON-merging into `settings.json` without clobbering existing entries. **This is the design, not a coordination problem to solve.**

To make your skill's hooks coexist safely with other skills' hooks, follow these five rules:

1. **Symlink names must be skill-prefixed.** Use `.claude/hooks/<skill>-<purpose>.{sh,py}` (e.g., `task-active-check.sh`, `skill-creator-watch.py`, `change-control-frozen.py`). Never use a generic name like `pre-tool-use.sh` — two skills doing that collide on the symlink.
2. **State files must be skill-prefixed and session-scoped.** If your hook persists per-session state, name the file `.state/<skill>-<purpose>-{session_id}.{json,txt}` (e.g., `.state/active-tasks-{session_id}.txt`, `.state/skill-creator-armed-{session_id}.json`). Never read or write another skill's state file — a hook that touches another skill's state is no longer self-contained.
3. **Never assume execution order.** Other skills' hooks may run before or after yours. Your hook must be correct in isolation, with no dependency on what ran first.
4. **Default to exit 0.** Informational nudges go to stderr (visible to user, not blocking). Use the structured PreToolUse JSON contract (`{"decision": "block", "reason": "..."}`) only when you genuinely need to deny the operation.
5. **Provide a SessionEnd cleanup hook** if you create per-session state — and make it purge ONLY your own state files (matching `<skill>-` prefix). Don't loop over `.state/*-{session_id}.*` and clean everything; that would corrupt other skills' state.

**Reference implementation pairs** (good to learn from):
- `task` skill: `hooks/check-active-task.sh` (PreToolUse) + `hooks/session-cleanup.sh` (SessionEnd) + state file `.state/active-tasks-{session_id}.txt`
- `skill-creator` skill: `hooks/skill-md-watch.py` (PreToolUse) + `hooks/skill-md-watch-cleanup.sh` (SessionEnd) + state file `.state/skill-creator-armed-{session_id}.json`

Both pairs hook the same events (PreToolUse Edit/Write/NotebookEdit + SessionEnd), use skill-prefixed symlink names + state files, and have no awareness of each other. That's the canonical shape.

**Note on WSL2:** Symlinks created in WSL2 may not be visible in VS Code's file explorer. This is expected. The hooks and agents still resolve from the CLI, and source files can be edited via the skill directory directly.

### README.md as Design Document

Per the README Navigation Rule, every skill gets a README.md that:

- Explains design decisions and architecture
- Documents lineage (what it was adapted from, if applicable)
- Lists dependencies
- Contains `## Best Practices` table (consumed by `/best-practices` audit)
- Contains `## Changelog` section (version history)
- Is NOT loaded by Claude during normal skill operation
- Exists for human understanding and as the skill's index layer

The Best Practices table and Changelog live here — not in SKILL.md — because SKILL.md is loaded into context on every skill trigger. These are metadata for auditors and maintainers, not instructions Claude needs to execute the skill.

Use the template at `${CLAUDE_SKILL_DIR}/templates/readme-skill.md`.

### Progressive Disclosure

Skills use a three-level loading system:
1. **Metadata** (name + description) — always in context (~100 words)
2. **SKILL.md body** — in context whenever skill triggers (<500 lines ideal)
3. **Bundled resources** — as needed (unlimited, scripts can execute without loading)

Key patterns:
- Keep SKILL.md under 500 lines; use reference files for overflow
- Reference files clearly from SKILL.md with guidance on when to read them
- For large reference files (>300 lines), include a table of contents

---

## Creating a Skill

### Capture Intent

Start by understanding the user's intent. The current conversation might already contain a workflow the user wants to capture (e.g., they say "turn this into a skill"). If so, extract answers from the conversation history first — the tools used, the sequence of steps, corrections the user made, input/output formats observed. The user may need to fill the gaps, and should confirm before proceeding.

1. What should this skill enable Claude to do?
2. When should this skill trigger? (what user phrases/contexts)
3. What's the expected output format?
4. Should we set up test cases to verify the skill works? Skills with objectively verifiable outputs (file transforms, data extraction, code generation, fixed workflow steps) benefit from test cases. Skills with subjective outputs (writing style, art) often don't need them. Suggest the appropriate default based on the skill type, but let the user decide.

### Interview and Research

Proactively ask questions about edge cases, input/output formats, example files, success criteria, and dependencies. Wait to write test prompts until you've got this part ironed out.

Check available MCPs — if useful for research (searching docs, finding similar skills, looking up best practices), research in parallel via subagents if available, otherwise inline. Come prepared with context to reduce burden on the user.

### Write the SKILL.md

Based on the user interview, read the template at `${CLAUDE_SKILL_DIR}/templates/skill-md.md` and fill in all sections. Ensure:

- YAML frontmatter has all 4 required fields (name, description, version, updated)
- Supporting Files table lists every bundled file
- Best Practices table has at least the standard checks
- Changelog has the initial version entry
- README.md is created alongside SKILL.md using the readme template

### Skill Writing Guide

#### Principle of Lack of Surprise

Skills must not contain malware, exploit code, or any content that could compromise system security. A skill's contents should not surprise the user in their intent if described.

#### Writing Patterns

Prefer using the imperative form in instructions.

**Defining output formats:**
```markdown
## Report structure
ALWAYS use this exact template:
# [Title]
## Executive summary
## Key findings
## Recommendations
```

**Examples pattern:**
```markdown
## Commit message format
**Example 1:**
Input: Added user authentication with JWT tokens
Output: feat(auth): implement JWT-based authentication
```

#### Writing Style

Try to explain to the model why things are important in lieu of heavy-handed musty MUSTs. Use theory of mind and try to make the skill general and not super-narrow to specific examples. Start by writing a draft and then look at it with fresh eyes and improve it.

### Test Cases

After writing the skill draft, come up with 2-3 realistic test prompts — the kind of thing a real user would actually say. Share them with the user. Then run them.

Save test cases to `evals/evals.json`. Don't write assertions yet — just the prompts. You'll draft assertions in the next step while the runs are in progress. See `references/schemas.md` for the full schema.

---

## Running and Evaluating Test Cases

This section is one continuous sequence — don't stop partway through.

Put results in `<skill-name>-workspace/` as a sibling to the skill directory. Within the workspace, organize results by iteration (`iteration-1/`, `iteration-2/`, etc.) and within that, each test case gets a directory (`eval-0/`, `eval-1/`, etc.).

### Step 1: Spawn all runs (with-skill AND baseline) in the same turn

For each test case, spawn two subagents in the same turn — one with the skill, one without. Launch everything at once so it all finishes around the same time.

**With-skill run:**
```
Execute this task:
- Skill path: <path-to-skill>
- Task: <eval prompt>
- Input files: <eval files if any, or "none">
- Save outputs to: <workspace>/iteration-<N>/eval-<ID>/with_skill/outputs/
- Outputs to save: <what the user cares about>
```

**Baseline run** (same prompt, but the baseline depends on context):
- **Creating a new skill**: no skill at all. Same prompt, no skill path, save to `without_skill/outputs/`.
- **Improving an existing skill**: the old version. Before editing, snapshot the skill, then point the baseline subagent at the snapshot. Save to `old_skill/outputs/`.

Write an `eval_metadata.json` for each test case. Give each eval a descriptive name.

### Step 2: While runs are in progress, draft assertions

Don't just wait for the runs to finish — use this time productively. Draft quantitative assertions for each test case and explain them to the user.

Good assertions are objectively verifiable and have descriptive names — they should read clearly in the benchmark viewer. Subjective skills are better evaluated qualitatively — don't force assertions onto things that need human judgment.

### Step 3: As runs complete, capture timing data

When each subagent task completes, you receive a notification containing `total_tokens` and `duration_ms`. Save this data immediately to `timing.json` in the run directory. This is the only opportunity to capture this data.

### Step 4: Grade, aggregate, and launch the viewer

Once all runs are done:

1. **Grade each run** — spawn a grader subagent that reads `agents/grader.md`. Save results to `grading.json`. The grading.json expectations array must use the fields `text`, `passed`, and `evidence` — the viewer depends on these exact field names.

2. **Aggregate into benchmark** — run from the skill-creator directory:
   ```bash
   python -m scripts.aggregate_benchmark <workspace>/iteration-N --skill-name <name>
   ```

3. **Do an analyst pass** — read the benchmark data and surface patterns. See `agents/analyzer.md` for what to look for.

4. **Launch the viewer**:
   ```bash
   nohup python <skill-creator-path>/eval-viewer/generate_review.py \
     <workspace>/iteration-N \
     --skill-name "my-skill" \
     --benchmark <workspace>/iteration-N/benchmark.json \
     > /dev/null 2>&1 &
   VIEWER_PID=$!
   ```
   For iteration 2+, also pass `--previous-workspace <workspace>/iteration-<N-1>`.

   **Headless environments:** Use `--static <output_path>` to write a standalone HTML file instead of starting a server.

5. **Tell the user** the results are ready for review.

### Step 5: Read the feedback

When the user tells you they're done, read `feedback.json`. Empty feedback means the user thought it was fine. Focus improvements on test cases where the user had specific complaints.

---

## Improving the Skill

### How to think about improvements

1. **Generalize from the feedback.** We're trying to create skills that work across many prompts. Rather than put in fiddly overfitty changes, try branching out and using different metaphors or patterns.

2. **Keep the prompt lean.** Remove things that aren't pulling their weight. Read the transcripts — if the skill is making the model waste time on unproductive work, remove those instructions.

3. **Explain the why.** Try hard to explain the **why** behind everything. If you find yourself writing ALWAYS or NEVER in all caps, reframe and explain the reasoning instead.

4. **Look for repeated work across test cases.** If all test cases resulted in the subagent writing a similar helper script, bundle that script in `scripts/` and tell the skill to use it.

### The iteration loop

After improving the skill:

1. Apply improvements (bump `version` and update `Changelog`)
2. Rerun all test cases into a new `iteration-<N+1>/` directory
3. Launch the reviewer with `--previous-workspace`
4. Wait for user review
5. Read new feedback, improve again, repeat

Keep going until the user is happy, feedback is empty, or you're not making meaningful progress.

---

## Advanced: Blind comparison

For situations where you want a more rigorous comparison between two versions of a skill, there's a blind comparison system. Read `agents/comparator.md` and `agents/analyzer.md` for the details. The basic idea is: give two outputs to an independent agent without telling it which is which, and let it judge quality. Then analyze why the winner won.

This is optional, requires subagents, and most users won't need it.

---

## Description Optimization

The description field in SKILL.md frontmatter is the primary mechanism that determines whether Claude invokes a skill. After creating or improving a skill, offer to optimize the description for better triggering accuracy.

### Step 1: Generate trigger eval queries

Create 20 eval queries — a mix of should-trigger and should-not-trigger. Save as JSON.

The queries must be realistic and something a user would actually type. Include file paths, personal context, column names, URLs. A little backstory. Mix of lengths. Focus on edge cases.

For **should-trigger** queries (8-10): different phrasings of the same intent, some formal, some casual. Include cases where the user doesn't explicitly name the skill but clearly needs it.

For **should-not-trigger** queries (8-10): near-misses — queries that share keywords but need something different. Don't make them obviously irrelevant.

### Step 2: Review with user

Present the eval set using the HTML template:

1. Read `assets/eval_review.html`
2. Replace placeholders: `__EVAL_DATA_PLACEHOLDER__`, `__SKILL_NAME_PLACEHOLDER__`, `__SKILL_DESCRIPTION_PLACEHOLDER__`
3. Write to a temp file and open it
4. User edits/exports → `eval_set.json`

### Step 3: Run the optimization loop

```bash
python -m scripts.run_loop \
  --eval-set <path-to-trigger-eval.json> \
  --skill-path <path-to-skill> \
  --model <model-id-powering-this-session> \
  --max-iterations 5 \
  --verbose
```

### Step 4: Apply the result

Take `best_description` from the JSON output and update the skill's SKILL.md frontmatter. Show the user before/after and report the scores.

---

## Subagent Delegation

| Scenario | Agent Type | Prompt |
|----------|-----------|--------|
| Grade assertions against outputs | general-purpose | `agents/grader.md` |
| Blind A/B comparison | general-purpose | `agents/comparator.md` |
| Analyze why winner won / benchmark patterns | general-purpose | `agents/analyzer.md` |

## Notes

- Assembled documents and generated artifacts should be clearly marked as such
- When improving an existing skill, always bump the `version` and add a `Changelog` entry
- The README Navigation Rule applies: every folder created by a skill must have a README.md

