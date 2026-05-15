---
name: best-practices
description: "Audit project setup against best practices from a shared registry and local skills — checks CLAUDE.md, folder structure, standards, tasks, DHF layout with parallel subagent fan-out"
version: 15
updated: 2026-04-27
---

# Best Practices Audit

Audit this project's setup against best practices. Usage: `/best-practices [action]`

## Actions

Parse the user's argument string `$ARGUMENTS` to determine which action to perform. Default action (no arguments) is `audit`.

### `audit`
Run a full audit of the project against all best practices.

**Step 1 — Fetch registry practices**

Determine the registry repo from `project.yml`. Read the file and find the first `registries:` entry with `type: github` — use its `repo:` and `path:` fields. If `project.yml` doesn't exist or has no github registry, fall back to `GlobalLogic-a-Hitachi-Company/hitachi` / `skills/manifest.md`.

Fetch the best practices manifest from the registry. Try methods in order:

1. **Local clone (preferred)**: If the registry entry has a `local_path:` field, resolve it relative to the project root and read `{local_path}/{REGISTRY_PATH}` directly. This is the fastest path and works offline.
2. **gh CLI (fallback)**: `gh api repos/{REGISTRY_REPO}/contents/{REGISTRY_PATH} --jq '.content' | base64 -d`
   - Works for both public and private repos when the user is authenticated with `gh`
3. **Raw URL (last resort)**: `https://raw.githubusercontent.com/{REGISTRY_REPO}/main/{REGISTRY_PATH}`
   - Only works for public repos
4. **If all fail**: Warn the user and continue with local-only checks.

Parse the manifest for practice definitions (see Registry Format below).

**Step 2 — Scan local skills**

Read all `.claude/skills/*/README.md` files in the project. For each file that contains a `## Best Practices` section, parse the table of checks. (Best Practices tables live in README.md — not SKILL.md — because SKILL.md is loaded into context on every skill trigger while README.md is never auto-loaded.)

**Step 3 — Run checks**

**Tool selection rules (mandatory):** To avoid triggering user approval prompts, use dedicated tools for all checks:
- **File existence**: Use Glob (not `test -f` or `ls`)
- **Content search**: Use Grep (not `grep` or `rg` via Bash)
- **File reading**: Use Read (not `cat` or `head` via Bash)
- **Bash only for**: `gh api` (registry fetch), `bash .claude/hooks/*` (hook scripts), or `python3 -c '...'` (complex logic). These are pre-approved in `settings.json`. Never use bare `for`, `test`, `[`, or `if` as the first command in a Bash call — wrap in `bash -c '...'` or `python3 -c '...'` if shell logic is needed.

**Scope column parsing (v8, added for unified DHF shape):**

Every check table in every SKILL.md may include a `Scope` column. Values:
- `shared` — run once at project root (legacy behavior)
- `per-dhf` — run once per entry in `project.yml` `dhfs[]`, with the DHF root (`docs/project/dhfs/<path>`) as the implicit working directory. Path references in "How to Verify" without a leading `/` are resolved relative to this root.
- `per-submission` — run once per `docs/project/submissions/<filing>/` folder, with the filing folder as the implicit working directory.
- `cross-cutting` — run once at project root, but reads across multiple DHFs (enumerates `project.dhfs[]` and correlates).

If the `Scope` column is absent from a check table row, default to **`shared`**. This preserves backward compatibility with skills that haven't added the column yet (per task 007 ambiguity #1 sign-off).

When parsing each README.md \`## Best Practices\` table, detect whether the header row contains a `Scope` column:
- If yes: read the Scope value from each data row.
- If no: treat every check as `shared`.

**DHF enumeration (for `per-dhf` and `cross-cutting` checks):**

Read `project.yml` once at the start of the audit and extract the `dhfs[]` list. Each entry has `path`, `regulatory`, `filing`, and optional `parent` fields. If `project.yml` is missing or `dhfs:` is missing, treat the list as empty — `per-dhf` checks will iterate zero items and emit an INFO line explaining why. Cross-cutting checks can still run and will report the missing manifest.

**Subagent dispatch for per-dhf and per-submission checks (v9 implementation of task 007 P5.5a):**

In a multi-dhf project, `per-dhf` and `per-submission` checks **fan out to LLM subagent workers via the Agent tool** — one subagent per DHF for per-dhf, one per composition manifest for per-submission. Each subagent runs its assigned checks and returns a structured JSON findings list that the dispatcher merges into the final report.

**Why subagents and not subprocess/in-process**: `/best-practices` is a dispatcher that discovers checks from other skills' `## Best Practices` sections. Each owning skill writes its own "How to Verify" column, and that column can be a scripted test (bash one-liner, `test -f`, grep) or a reasoning-based criterion ("every user need traces to at least one measurable acceptance criterion"). The dispatcher has no control over the mix. Subprocess fan-out would only handle scripted checks; LLM subagents handle both kinds uniformly — running shell commands for scripted checks and reasoning through judgment for the others.

**Pool separation**: per-DHF subagents and per-submission subagents are **disjoint pools**. A composition manifest typically belongs to a single submission but its artifacts span multiple DHFs; scoping per-submission work to one subagent per manifest keeps cross-DHF reference checks in one context without duplicating work across multiple per-DHF subagents.

**N=1 short-circuit optimization**: When `project.dhfs[]` has exactly one entry, the dispatcher runs `per-dhf` checks in its own context rather than spawning a subagent. This is a pure performance optimization — semantically identical to spawning one subagent — and saves token cost for simple projects.

**Per-check execution logic:**

**Step A — Read project.yml once** and extract `dhfs[]`. Compute `N = len(dhfs[])`.

**Step B — Partition checks by Scope** after parsing every SKILL.md `## Best Practices` table:
- `SHARED_CHECKS` — run in the dispatcher's own context
- `PER_DHF_CHECKS` — dispatched to per-DHF subagent pool (or run in-process if N≤1)
- `PER_SUBMISSION_CHECKS` — dispatched to per-submission subagent pool
- `CROSS_CUTTING_CHECKS` — run in the dispatcher's own context (they enumerate `dhfs[]` themselves)

**Step C — Run shared and cross-cutting checks in the parent context.**
1. For each check in `SHARED_CHECKS + CROSS_CUTTING_CHECKS`: verify the condition via Glob/Read/Grep, classify PASS/FAIL/WARN/INFO, record result with no label.
2. Handle the two special checks ("Skills are self-contained" and "Skills are versioned") as described after the dispatch section.

**Step D — Fan out per-dhf checks.**

**D.1 — If `N == 0`:** Skip all `per-dhf` checks with an INFO line per check: `[INFO] <check> — skipped, no DHFs defined`. Continue to Step E.

**D.2 — If `N == 1`:** Short-circuit optimization. Run every `per-dhf` check in the dispatcher's own context against the single `dhfs[0]` root. Record each result with label `dhf=<last-segment-of-path>`. Continue to Step E.

**D.3 — If `N > 1`:** Fan out to subagents. **Spawn one Agent tool call per DHF in a single message** (parallelism is achieved by the Agent tool when multiple Agent calls are issued in one message). For each entry `E` in `dhfs[]`, skip if `--dhf=<name>` was passed and `E`'s leaf name doesn't match. For each remaining entry, invoke:

```
Agent(
  description="Audit DHF <leaf-name>",
  subagent_type="general-purpose",
  prompt=<per-dhf subagent prompt template below, with substitutions>
)
```

**Subagent prompt template (per-dhf):**

```
You are a best-practices audit worker for DHF `<LEAF_NAME>` at path `docs/project/dhfs/<FULL_PATH>`.

Your job: run the following checks against this DHF and return a structured JSON findings list. You are a read-only worker — do not modify any files.

Checks to run:
1. <CHECK_ID_1> (from <OWNING_SKILL_1>): <CHECK_NAME_1>
   Severity: <Required|Recommended>
   How to verify: <VERBATIM "How to Verify" COLUMN FROM THE OWNING SKILL'S SKILL.md>
2. <CHECK_ID_2> (from <OWNING_SKILL_2>): ...
...

Working directory resolution: paths in "How to Verify" without a leading `/` are relative to `docs/project/dhfs/<FULL_PATH>/`. Paths starting with `docs/`, `.claude/`, `tasks/`, or any absolute path are project-root-relative.

For each check:
- If the "How to verify" is a shell command or file-existence test, run it via Bash (read-only commands only: `test -f`, `test -d`, `ls`, `grep`, `cat`, `python3 -c`) or via Glob/Read/Grep. Interpret exit code or match as PASS/FAIL.
- If the "How to verify" is a natural-language criterion (e.g., "every user need traces to a measurable acceptance criterion"), read the relevant files and reason through it. Err toward FAIL when uncertain — audit results must be conservative.
- Severity governs the failure classification: Required → FAIL on failure, Recommended → WARN on failure.
- Do NOT modify any files. You may only read.
- Do NOT invoke any tool outside Read, Glob, Grep, and Bash (read-only commands).

Return a single JSON block, nothing else, with this exact schema:

```json
{
  "sub_dhf": "<LEAF_NAME>",
  "sub_dhf_path": "<FULL_PATH>",
  "findings": [
    {
      "check_id": "<unique identifier>",
      "skill": "<owning skill name>",
      "check_name": "<human-readable check name>",
      "status": "PASS" | "FAIL" | "WARN" | "INFO",
      "severity": "Required" | "Recommended",
      "message": "<short explanation; empty string if PASS>"
    }
  ]
}
```

If you cannot complete the audit (filesystem error, malformed check definition, check requires write access), return:

```json
{
  "sub_dhf": "<LEAF_NAME>",
  "sub_dhf_path": "<FULL_PATH>",
  "findings": [],
  "dispatch_error": "<short explanation of what went wrong>"
}
```

Do not emit any text outside the JSON block.
```

**Step E — Fan out per-submission checks.** Iterate `docs/project/submissions/*/` via Glob. Skip entries without a composition manifest if any `per-submission` check requires one (check-specific judgment). Spawn one Agent tool call per composition manifest in a single message, with the parallel template:

**Subagent prompt template (per-submission):**

```
You are a best-practices audit worker for submission `<FILING_NAME>` with composition manifest at `docs/project/submissions/<FILING_NAME>/composition-manifest.md`.

Your job: run the following per-submission checks against this filing and return a structured JSON findings list. You are a read-only worker — do not modify any files.

Checks to run:
1. <CHECK_ID_1> (from <OWNING_SKILL_1>): <CHECK_NAME_1>
   Severity: <Required|Recommended>
   How to verify: <VERBATIM "How to Verify" FROM THE OWNING SKILL'S SKILL.md>
2. ...

Working directory resolution: paths in "How to Verify" without a leading `/` are relative to `docs/project/submissions/<FILING_NAME>/`. Paths starting with `docs/`, `.claude/`, `tasks/`, or any absolute path are project-root-relative. When a check references `dhfs/<dhf>/...` that path is under `docs/project/dhfs/<dhf>/` — the composition manifest's "Included pieces" section lists which DHFs this filing spans, so cross-DHF reads are expected.

For each check:
- Same PASS/FAIL/WARN/INFO rules as the per-dhf template above.
- Composition-manifest-parsing checks should parse the manifest markdown for the five required sections (Filing Identification, Included Pieces, Excluded Pieces, Cross-references, Reviewer Sign-off) and verify each "Included piece" resolves to an existing file.

Return a single JSON block, nothing else, with this exact schema:

```json
{
  "submission": "<FILING_NAME>",
  "submission_path": "docs/project/submissions/<FILING_NAME>",
  "findings": [
    { "check_id": "...", "skill": "...", "check_name": "...", "status": "...", "severity": "...", "message": "..." }
  ]
}
```

On dispatch error, return the same shape with an empty `findings` array and a `dispatch_error` field.
```

**Step F — Collect subagent results and handle errors.**
1. For each Agent call from Steps D.3 and E, parse the returned JSON block. Use `python3 -c` to extract the JSON payload from the agent's text response if needed.
2. If a subagent returned `dispatch_error`: emit a synthetic `[FAIL] dispatch error — <subagent_id>` finding with the error message. Continue merging other subagents' results — one bad subagent does not kill the audit.
3. If a subagent returned malformed JSON (parse failure): emit `[FAIL] malformed JSON from subagent — <subagent_id>` and continue.
4. If a subagent timed out or never completed: emit `[FAIL] subagent did not return — <subagent_id>` and continue.
5. Merge all per-DHF findings into `RESULTS["per-dhf"][leaf_name]` and all per-submission findings into `RESULTS["per-submission"][filing_name]`.

**Step G — Handle the two special shared checks** (deferred from Step C because they scan all skills' SKILL.md files rather than project data):
- **"Skills are self-contained"**: Read each `.claude/skills/*/SKILL.md` file and scan for patterns that reference external files as dependencies — e.g., "using the template at `<path>`", "read from `<path>`", or file path references that the skill requires to exist in order to function. A skill may *reference* project files it reads/writes as part of its operation (e.g., a task skill reading `tasks/`), but must not depend on an external file to provide its own templates, structures, or definitions. All scaffolding content the skill generates must be defined inline in `SKILL.md` or in supporting files within the skill's own directory (referenced via `${CLAUDE_SKILL_DIR}`).
- **"Skills are versioned"**: Read each `.claude/skills/*/SKILL.md` file and verify it has YAML frontmatter with a `version:` field. Then read the corresponding `.claude/skills/*/README.md` and verify it has a `## Changelog` section. **Exempt externally-sourced skills** — if a skill's SKILL.md has no YAML frontmatter at all (no `---` delimiter in the first 5 lines), it is an external/utility skill and should be reported as INFO (not FAIL): `[INFO] <skill> — external skill, versioning not required`.

**Step H — Classify and aggregate**. For each recorded result: PASS / FAIL / WARN / INFO.
- FAIL for "Required" severity checks that don't pass
- WARN for "Recommended" severity checks that don't pass
- PASS for checks that pass
- INFO for checks that are intentionally skipped (per-dhf in a project with empty `dhfs[]`, `mixed` regulatory DHFs skipping certain checks, external skills exempt from versioning, etc.)

**Cost envelope**: A medium-sized project (≈10 DHFs and a handful of filings). A single audit run spawns ~10–15 subagents (one per DHF + one per composition manifest). Each subagent reads a bounded slice of the tree and executes a known list of checks. Rough envelope: each subagent ~5–15k input tokens, ~1–3k output tokens; per-audit ~100–200k total tokens. This is a deliberate action, not a hot path — operators run it before commits or PR, not on every save. Knobs to control cost: `--dhf=<name>` narrows the per-dhf pool; per-submission pool is naturally bounded by manifest count.

**Backward compatibility**: In single-dhf mode (N=1) or zero-dhf mode (N=0), no subagents are spawned. The serial path is byte-identical to v8 behavior. This preserves deterministic audit output for simple projects.

**Step 4 — Report**

Display results in a grouped format. Grouping depends on whether the project has more than one DHF:

**Single DHF (or no dhfs[]):** flat layout grouped by source (legacy format).

```
Project Audit: <project name from project.yml or CLAUDE.md>

## Registry Practices (from GlobalLogic-a-Hitachi-Company/hitachi)
  [PASS] CLAUDE.md exists with project overview
  [PASS] Glossary exists
  [FAIL] No .gitignore found                          (Required)

## Task Management (from .claude/skills/task/SKILL.md)
  [PASS] Task folder exists
  [PASS] Task README exists
  [WARN] Index has 1 orphan task                       (Recommended)

Summary: 8/10 passed | 1 failed | 1 warning
```

**Multi DHF (>1 entries in `dhfs[]`):** grouped by Scope.

```
Project Audit: <project name> (multi-dhf, <N> DHFs)

## Shared Checks
  [PASS] CLAUDE.md exists with project overview
  [PASS] Team roster has active members
  ...

## Per-DHF Checks
  ### pca-device
    [PASS] DHF README exists
    [PASS] Design controls scaffold present
    ...
  ### connectivity-adapter
    [PASS] DHF README exists
    [WARN] Clinical folder empty                      (Recommended)
    ...

## Per-Submission Checks
  ### submissions/510k-pp3500/
    [PASS] Composition manifest exists
    ...

## Cross-Cutting Checks
  [PASS] project.dhfs[] matches dhfs/ folder tree
  [PASS] DHF leaf names are unique
  ...

Summary: 22 passed | 1 failed | 4 warnings | 1 info
```

After the report, suggest specific fixes for any FAIL or WARN items.

### `check <practice-name>`
Run a single named check and report its result. Useful for verifying a fix.

### `fix [--dry-run]`

Auto-remediate **mechanical drift** found by the `audit` action, subject to a strict safety model. Creates a task document to capture what was changed, activates it, applies Tier A fixes, flags Tier B and Tier C for human review, and leaves everything **uncommitted** so you can review the diff before committing.

**Safety model — three tiers:**

| Tier | What qualifies | Action |
|------|----------------|--------|
| **A — Auto-apply** | Content inside `<!-- AUTO:STRUCTURE ... -->` sentinel blocks in README files. The renderer owns this content by construction (see `.claude/rules/sentinel-blocks.md`). | Invoke `.claude/skills/medtech-docs/scripts/render-sentinels.py <file>` once per affected README. No additional prompting. |
| **B — Flag only (never auto-write)** | CLAUDE.md Project Structure tree, CLAUDE.md DHF table, CLAUDE.md team references. These regions carry human intent (annotations, custom schemas, narrative context) that mechanical rewriting would clobber. | Task doc captures a **proposed fix** (specific additions/removals with exact text) as a human checklist. User applies manually after review. |
| **C — Flag only** | Narrative drift — information-flow diagrams, convention prose, relationship sections, anything outside the structural-table slot. | Task doc lists the finding. Human-owned content — `fix` never touches it. |

**Default behavior** is to apply Tier A and capture Tier B/C in the task doc. Pass `--dry-run` to preview without writing anything — nothing is applied, no task doc created, no files modified.

**Flow:**

**Step 1 — Run the audit.** Reuse the `audit` action to collect all findings. Filter to drift-detection findings from best-practices v11+ and medtech-docs v18+:
- `README Structure table matches folders`
- `CLAUDE.md Project Structure tree matches filesystem`
- `CLAUDE.md DHF table matches project.yml`
- `CLAUDE.md team references match project.yml`
- `medtech-docs templates match init folder tree`

If no drift-detection findings are FAIL/WARN, exit with "no drift to fix" and stop — do not create a task doc.

**Step 2 — Classify each finding by tier.**
- If the finding's target file is under `docs/**/README.md` AND the README contains `<!-- AUTO:STRUCTURE ... -->` at or near the drifted region → **Tier A**.
- If the finding's target file is `CLAUDE.md` in project root → **Tier B**.
- If the finding is for `medtech-docs templates match init folder tree` → **Tier B** (skill-author fix, not project-content fix).
- Otherwise → **Tier C** (narrative / other).

**Step 3 — Determine task owner.**
1. Read `git config user.email`.
2. Match against `project.yml` `team.active[].email` — use that member's `task_folder`.
3. If no match, prompt the user for which person's folder to use. Do not silently default.

**Step 4 — `--dry-run` branch (no writes):**
Print a preview to stdout, grouped by tier. For Tier A findings list the files that would be rendered. For Tier B findings print the proposed change as a diff-like block. Exit 0. Do not create or modify any files.

**Step 5 — Default branch (apply Tier A, flag B/C):**

5a. **Determine next task ID** for the chosen person (scan `tasks/<person>/` for highest NNN, increment, zero-pad).

5b. **Write task doc** at `tasks/<person>/NNN-fix-readme-drift-YYYY-MM-DD.md`:
```markdown
# NNN — Fix README/CLAUDE.md Drift (auto-detected)

**ID**: NNN
**Created**: YYYY-MM-DD
**Status**: In Progress
**Created By**: best-practices fix (auto)
**Owner**: <resolved person name>
**Priority**: Medium

---

## Goals

Auto-remediate mechanical README drift detected by `/best-practices audit`. Tier A fixes are applied automatically inside `<!-- AUTO:STRUCTURE -->` sentinels. Tier B and Tier C findings require human review and are captured below as a manual checklist.

## Tier A — Auto-applied (sentinel blocks)

<!-- Populated by fix action with one row per auto-applied render -->
| File | Finding | Renderer result |
|------|---------|-----------------|
| ... | ... | updated / no-change |

## Tier B — Proposed fixes (requires human apply)

<!-- CLAUDE.md: never auto-written. Proposed changes below. Apply manually. -->

### Proposal N: <short summary>
**File**: `CLAUDE.md`
**Finding**: <check name>
**Current content (excerpt)**:
    ... verbatim lines from current file ...
**Proposed content**:
    ... verbatim proposed replacement ...
**Rationale**: <why this change>
**To apply**: <specific hand-edit instructions>

- [ ] Review proposal N
- [ ] Apply (manually, after review)

## Tier C — Flagged (narrative drift, not auto-fixable)

- [ ] <file>: <narrative finding> — human review required

## Todos

- [x] Tier A auto-applied
- [ ] Review Tier B proposals above
- [ ] Apply Tier B manually where accepted
- [ ] Review Tier C findings
- [ ] Commit the fix (after diff review)

## Changelog

- YYYY-MM-DD: Task auto-created by /best-practices fix. <N> Tier A auto-applied, <M> Tier B proposed, <K> Tier C flagged.
```

5c. **Append the task to `tasks/<person>/000-index.md`** Active table.

5d. **Activate the task** via `bash .claude/hooks/task-activate.sh add $(printenv CLAUDE_SESSION_ID) NNN` so subsequent file writes pass the task gate.

5e. **Apply Tier A fixes.** For each Tier A finding, deduplicate by target file, then invoke:
```
python3 .claude/skills/medtech-docs/scripts/render-sentinels.py <target-file>
```
Record the result (updated / no-change / error) in the task doc's Tier A table.

5f. **Populate Tier B proposals in the task doc.** For each Tier B finding, compute the specific proposed change:
- **CLAUDE.md DHF table**: compare `project.yml` `dhfs[]` leaves to the table's first column. For each leaf in `dhfs[]` but not in the table → propose a row addition (schema: Architecture Name = `<leaf>` or TODO, Marketed Name = TODO, Classification = derived from `classification` object, IEC 62304 = `Class <c>`). For each table row with no matching `dhfs[]` leaf → flag as possibly stale (do NOT propose removal; list as "review needed").
- **CLAUDE.md Project Structure tree**: compare top-level tree entries (e.g., `├── docs/`) to actual top-level directories. For new dirs → propose adding an entry at the right place in the tree. For removed dirs → flag as possibly stale (do not propose removal).
- **CLAUDE.md team references**: list CLAUDE.md name-drops that are not in `project.yml` `team.active[]` (may be stale or may be intentional historical reference — flag only).

For each proposal, write: current content excerpt, proposed content, rationale, and exact hand-edit instructions. Never generate `Edit` or `Write` tool calls that touch CLAUDE.md.

5g. **Populate Tier C findings** as a simple checklist of what to review.

5h. **Write final changelog row** on the task doc summarizing counts.

**Step 6 — Report.** Print:
- Task doc path
- Counts: N Tier A applied, M Tier B proposals, K Tier C flagged
- Git status summary (`git status --short`)
- Explicit note: "Changes are **uncommitted**. Review `git diff` and the task doc, then commit when ready. CLAUDE.md was **not modified** — Tier B proposals are in the task doc for your review."

**Constraints (hard rules):**

1. **`fix` never writes to `CLAUDE.md`**, ever. Not even wrapping sections in sentinels. That is an explicit future action (`fix --wrap-claude-md` if we add it later, which would still require per-region confirmation).
2. **`fix` never writes outside `<!-- AUTO:STRUCTURE -->` sentinels** in any file. If the renderer would need to create a sentinel to fix something, report it as Tier B instead — never inject sentinels into existing files.
3. **`fix` never commits.** Git commits are a human action.
4. **`fix` never deletes files.**
5. **`fix` never removes content** — only additions and in-sentinel regenerations. Stale rows are flagged, not removed.
6. **If audit cannot run** (registry unreachable, project.yml malformed, etc.), `fix` aborts with a clear error and creates no task doc.

### `sync`
Fetch the latest skills from the registry and compare against locally installed skills.

1. Fetch the manifest using the same method as `audit` Step 1 (read registry `local_path` first, then gh CLI, then raw URL fallback). When reading from `local_path`, also run `git -C {local_path} pull --ff-only` first to ensure the local clone is current.
2. For each skill listed in the manifest's **Published Skills** table:
   a. Check if a corresponding directory exists in `.claude/skills/` with a `SKILL.md`
   b. If installed, read the local `SKILL.md`'s `version:` frontmatter and compare to the registry version
3. Report for each skill:
   - **Up to date**: local version matches registry version
   - **Update available**: registry version is higher than local version — show the registry changelog entries since the local version
   - **Not installed**: skill exists in registry but not locally
   - **Local only**: skill exists locally but not in registry (custom project skill)

## Registry Format

The shared registry at `GlobalLogic-a-Hitachi-Company/hitachi` uses this structure:

```
hitachi/
├── skills/
│   ├── manifest.md              # Master index of all published skills and project-level practices
│   ├── task/
│   │   └── SKILL.md             # Task management skill
│   ├── best-practices/
│   │   └── SKILL.md             # This skill
│   ├── medtech-docs/
│   │   ├── SKILL.md             # MedTech documentation skill
│   │   └── templates/           # Supporting template files
│   └── ...
```

### manifest.md format

The manifest has three sections:

**Terminology** — definitions of "skill", "command", and "registry"

**Project Practices** — best practices that apply to any project, not tied to a specific skill:

```markdown
## Project Practices

| Check | How to Verify | Severity |
|-------|--------------|----------|
| CLAUDE.md exists | `CLAUDE.md` exists in project root | Required |
| ...
```

**Published Skills** — index of available skills with versions:

```markdown
## Published Skills

| Skill | Directory | Version | Description |
|-------|-----------|---------|-------------|
| Task Management | task/ | 3 | Task-driven workflow with per-person folders |
| Best Practices | best-practices/ | 3 | Project audit against shared best practices |
```

### Skill file format

Every skill is a directory containing `SKILL.md` with:

1. **YAML frontmatter** with `name:`, `description:`, `version:` (integer) and `updated:` (date)
2. **Title and usage** — `# Skill Name` followed by description
3. **Actions** — what the skill does when invoked

And a `README.md` with:

4. **Best Practices** (optional) — checks the `/best-practices` audit should run for this skill (table format; scanned by audit Step 2)
5. **Changelog** — reverse-chronological list of changes per version

Skills may include supporting files (templates, scripts, examples) alongside `SKILL.md` in the same directory.

## Notes
- The registry repo defaults to `GlobalLogic-a-Hitachi-Company/hitachi` but is read from `project.yml` `registries:` section (first `type: github` entry)
- Fetching prefers `gh api` (works with private repos) over raw URL (public only)
- If the registry is unreachable, the audit still runs using local skill best practices only
- The audit is read-only — it never modifies project files, only reports findings

