---
name: lessons
description: "Capture, stage, and promote lessons learned from task work — harvest tagged insights into a team ledger, track applications and overrides as evidence, promote mature lessons to their permanent home (skill, CLAUDE.md, agent, rule, glossary, README, standard)"
version: 5
updated: 2026-09-08
---

# Lessons Harvester & Curator

Scan task documents for tagged lessons, stage them in a team-shared ledger, track real-world applications and overrides as evidence, and promote mature lessons to their permanent home. Usage: `/lessons <action> [arguments]`

This skill is the **capture + curation + promotion** end of the lessons pipeline. It is distinct from `/best-practices`, which is the **audit** end — `/best-practices` verifies the project conforms to rules already codified in skills' Best Practices tables. A lesson becomes a `/best-practices` check when `/lessons promote` moves it into a skill's Best Practices table.

## Paths

| Item | Path |
|------|------|
| Ledger (team-shared) | `tasks/lessons-ledger.md` |
| Template | `${CLAUDE_SKILL_DIR}/templates/lessons-ledger.md` |
| Shared scanner | `${CLAUDE_SKILL_DIR}/../shared/task-content-scanner.md` |
| Task gate state | `.state/active-tasks-{session_id}.txt` |

## Dependencies

| File | Required by | Purpose |
|------|-------------|---------|
| `tasks/` directory | All actions | Source tasks to scan |
| `project.yml` | `scan`, `assemble` | Resolves `task_folder` for each team member (used in lesson IDs) |
| `.claude/skills/shared/task-content-scanner.md` | `scan`, `assemble` | Shared scanning algorithm |
| `.state/active-tasks-{session_id}.txt` | `record` | Task gate state file identifies the active task to attach records to |

If any are missing, the skill reports what's needed and how to create it (typically via `/medtech-docs init` or `/task setup`).

## Tag Conventions

### Lessons tag (in source tasks)

```markdown
## Lessons Learned — <topic>

<!-- LESSONS LEARNED: category1, category2 -->

### Principle: Stay High-Level, Ruthlessly

Body explaining the principle, why it matters, and how to apply it...

### Principle: Architecture Name vs. Marketed Name

...
```

- Tag must appear on a **line by itself**, not inside a code block or inline code
- The `## ` heading immediately above the tag is the **block title**
- Each `### ` subsection inside the block becomes **its own lesson**
- Scanner strips common heading prefixes (`Principle:`, `Rule:`, `Pattern:`, `Process:`) to produce the friendly name
- Categories after `LESSONS LEARNED:` are free-form, used for organizing the ledger Staged section
- Block ends at the next `## ` heading or end of file

### Promotion marker (written by `promote` into source tasks)

```markdown
<!-- LESSONS LEARNED: architecture, documentation, regulatory, process -->
<!-- LESSONS REVIEWED: promoted to glossary on 2026-04-20 -->
```

When the scanner sees a `LESSONS REVIEWED: promoted` marker immediately after a `LESSONS LEARNED` tag, it **excludes** the block from future assembly. The block content stays (history preserved); it just stops flowing into the Staged section.

Variants:
- `<!-- LESSONS REVIEWED: promoted to <destination> on YYYY-MM-DD -->` — block moved to final home
- `<!-- LESSONS REVIEWED: superseded by task <ref> on YYYY-MM-DD -->` — replaced by newer task
- `<!-- LESSONS REVIEWED: discarded on YYYY-MM-DD — <reason> -->` — rejected after data showed it wrong

### Records section (in task docs where events happened)

```markdown
## Lesson Records

<!-- LESSON RECORDS -->

### [L-example-01] applied — 2026-04-13
Moved cloud-provider-specific service names from the system SAD §3.2 to the
Management Services child SAD. Caught during review of the deployment section.

### [L-example-01] exception — 2026-04-15
Kept "DICOM" at system level. Rationale: DICOM is a protocol, not a vendor product
— genericizing it would actually harm precision. This suggests L-example-01 may need
an explicit exception clause for standards/protocols vs. vendor products.
```

**Format rules:**
- Section heading must be `## Lesson Records`
- Sentinel comment `<!-- LESSON RECORDS -->` marks it for the scanner (optional but recommended)
- Each record is a `### [LESSON-ID] <outcome> — YYYY-MM-DD` heading
- Body is free-form prose describing the context — this is the **evidence** promote will show you
- Block ends at next `### ` or `## `
- Records are immutable history: once written, they stay even after the lesson is promoted or discarded

## Lesson ID Format

```
L-<task_folder>-<NNN>-<seq>
```

| Component | Source | Example |
|-----------|--------|---------|
| `L-` | Literal prefix | `L-` |
| `<task_folder>` | From `project.yml` (e.g., `ben`, `maryna`, `romanolesh`) | `ben` |
| `<NNN>` | Task number (zero-padded) | `033` |
| `<seq>` | 1-based position of the `### ` heading inside the `<!-- LESSONS LEARNED -->` block | `01` |

Full example: `L-ben-033-01` = first lesson in Ben's task 033.

**ID stability**: `seq` is positional, so reordering `### ` subsections inside a tagged block shifts seq values. Convention: **do not reorder once records exist**; append new lessons at the end of the block. `validate` flags drift.

**Task reference format**: `<task_folder>/<NNN>` (e.g., `ben/033`, `maryna/041`). Used in ledger Record tables and anywhere a task is referenced across team members.

## Ledger Structure

```markdown
# Lessons Ledger

<!-- Generated by /lessons assemble — do not edit record tables directly -->
<!-- Last assembled: YYYY-MM-DD by <user> -->

## Staged

Active lessons under reinforcement. **This section is loaded every session via CLAUDE.md.**

### [L-ben-033-01] Stay High-Level, Ruthlessly
**Status**: staged
**Origin**: ben/033
**Categories**: architecture
**Staged**: 2026-04-07

**Principle**: The system SAD should stay high-level; vendor/implementation detail belongs in child SADs.

**Why**: Every editing pass, vendor names (AWS, Okta, Orthanc) crept back in and had to be stripped. High-level documents need constant vigilance against detail creep.

**How to apply**: When editing a system-level SAD, flag any vendor-specific name, product, or framework before inclusion. Standards and protocols (DICOM, HL7) are exempt — they're not vendor choices.

**Records** (5 applied, 1 exception, 1 challenged, 0 false-positive):
| Date | Task | Outcome | Who | Note |
|------|------|---------|-----|------|
| 2026-04-13 | ben/041 | applied | ben | Moved AWS detail to child SAD |
| 2026-04-15 | ben/041 | exception | ben | DICOM is a protocol, not a vendor |
| ... | ... | ... | ... | ... |

---

## Promoted

Audit trail of lessons that have reached their permanent home. **Not loaded at session start** — this section exists for traceability.

### [L-ben-033-03] Architecture Name vs. Marketed Name
**Status**: promoted → glossary (2026-04-18)
**Origin**: ben/033
**Promoted by**: ben
**Final home**: `glossary.md` — entry "Architecture Name"

---

## Archived / Superseded

Lessons discarded after data showed they were wrong, or superseded by a newer task. Historical only.

### [L-ben-028-02] Prefer Long-Form Prompts
**Status**: discarded (2026-04-20)
**Origin**: ben/028
**Reason**: 4 challenged records over 2 weeks showed the opposite was true for this project
```

## Outcome Types

| Outcome | Meaning | Signal |
|---------|---------|--------|
| **`applied`** | Situation matched, lesson was followed, it worked | Lesson is sound |
| **`exception`** | Situation matched, lesson is right in general but this was a legitimate edge case | Lesson may need an explicit exception clause before promotion |
| **`challenged`** | User tried the opposite to see if the lesson is correct | Multiple challenged records → lesson may be wrong, consider refinement or discard |
| **`false-positive`** | Claude flagged the lesson as applicable but it didn't actually apply | Lesson's "how to apply" text is too broad — tighten the trigger, not the rule |

## Promotion Destinations

| Destination | Syntax | What it writes | Where |
|---|---|---|---|
| **Skill Best Practices** | `promote <id> skill <name>` | Appends a row to that skill's `## Best Practices` table | `.claude/skills/<name>/SKILL.md` |
| **CLAUDE.md** | `promote <id> claude-md [--section "<section>"]` | Appends a bullet; defaults to "Ongoing task discipline" section | `CLAUDE.md` |
| **Agent prompt** | `promote <id> agent <name>` | Appends guidance to an agent prompt file | `.claude/skills/<skill>/agents/<name>.md` |
| **Rule file** | `promote <id> rule <name>` | Creates `.claude/rules/<name>.md` (like `readme-before-write.md`) | `.claude/rules/<name>.md` |
| **Glossary** | `promote <id> glossary` | Adds a term definition | `glossary.md` |
| **Standard note** | `promote <id> standard <id>` | Adds to a project-specific standards applicability note | `docs/external/standards/applicability/<id>.md` |
| **Folder README** | `promote <id> readme <path> [--section "<section>"]` | Appends under `## For Claude` if present, else creates `## Lessons` | `<path>/README.md` |

All destinations: after writing, the skill writes `<!-- LESSONS REVIEWED: promoted to <destination> on YYYY-MM-DD -->` as a marker in the source task under the `<!-- LESSONS LEARNED -->` tag, and moves the ledger entry from `## Staged` to `## Promoted`.

## Actions

Parse the user's argument string `$ARGUMENTS` to determine which action to perform.

### `init`

Initialize `tasks/lessons-ledger.md` from the template. Safe to re-run — skips if the file already exists and is not a placeholder.

1. Check if `tasks/lessons-ledger.md` exists. If yes and it does NOT contain `<!-- Status: awaiting-content -->`, stop and report: "Ledger already initialized. Run `/lessons assemble` to populate."
2. Read the template from `${CLAUDE_SKILL_DIR}/templates/lessons-ledger.md`.
3. Replace template variables: `{{TIMESTAMP}}` with today's date, `{{USER}}` with the git user name.
4. Before writing, read `tasks/README.md` (per README Before Write rule — `tasks/` is project-managed).
5. Write to `tasks/lessons-ledger.md`.
6. Report the file path and suggest next step: `/lessons scan` or `/lessons assemble`.

### `scan [task_folder]`

> Deterministic pre-check: `python3 .claude/skills/strategy/scripts/scan_tags.py --json tasks/` (owned by the strategy skill; shared grammar) lists every `<!-- LESSONS LEARNED` / `<!-- STRATEGY CONTENT` tag the harvesters would silently skip. Run it before `assemble` so a malformed tag is a finding, not a lost lesson.

Find all `<!-- LESSONS LEARNED -->` tagged blocks across task documents. Optionally filter by a single team member's task folder.

1. Read `${CLAUDE_SKILL_DIR}/../shared/task-content-scanner.md` for the scanning algorithm.
2. Glob for `tasks/*/[0-9][0-9][0-9]-*.md` files. If `[task_folder]` is provided, restrict to `tasks/<task_folder>/[0-9][0-9][0-9]-*.md`.
3. For each file, search for lines matching `<!-- LESSONS LEARNED` that appear on a line by themselves (not inside code blocks).
4. For each tagged block found:
   a. Extract the task ID from the filename (3-digit prefix).
   b. Resolve `<task_folder>` from the parent directory name.
   c. Extract the task title from line 1 (`# NNN — Title`).
   d. Extract categories from the tag (comma-separated values after `LESSONS LEARNED: `).
   e. Check the line immediately after the tag for a `<!-- LESSONS REVIEWED: ... -->` marker. If present, record the marker status (`promoted`, `superseded`, `discarded`) — the block will be excluded from assembly but is still reported in scan output.
   f. Find all `### ` headings within the block (tag line → next `## ` or EOF).
   g. For each `### ` subsection, generate a lesson ID using the 1-based position, extract the friendly name by stripping common prefixes (`Principle:`, `Rule:`, `Pattern:`, `Process:`).
   h. Extract the most recent date from the task's `## Changelog` section.
5. Report a summary table:

```
Lessons found

| Lesson ID     | Name                                | Origin     | Categories            | Status   | Last Modified |
|---------------|-------------------------------------|------------|-----------------------|----------|---------------|
| L-ben-033-01  | Stay High-Level, Ruthlessly         | ben/033    | architecture          | active   | 2026-04-12    |
| L-ben-033-02  | Start with Boundaries               | ben/033    | architecture          | active   | 2026-04-12    |
| L-ben-033-03  | Architecture vs. Marketed Name      | ben/033    | documentation         | promoted | 2026-04-12    |
...

19 lessons across 2 tasks (18 active, 1 promoted)
```

**Status values in scan output:**
- `active` — no review marker, will be assembled into Staged
- `promoted` — excluded from assembly (already in Promoted section of ledger)
- `superseded` — excluded
- `discarded` — excluded

### `assemble`

Compile tagged lessons and records into `tasks/lessons-ledger.md`.

**Two-pass algorithm:**

**Pass 1 — lessons**:
1. Run `scan` internally to find all tagged blocks and extract lesson metadata.
2. Skip blocks with any `LESSONS REVIEWED` marker (they're already in Promoted or Archived sections).
3. For each active lesson, extract the full body text of the `### ` subsection (prose, tables, code blocks) as the lesson content. Parse conventional fields if present (`**Principle**:`, `**Why**:`, `**How to apply**:`) — fall back to the full body if the fields aren't used.

**Pass 2 — records**:
4. Glob for `tasks/*/[0-9][0-9][0-9]-*.md` files.
5. For each file, find `## Lesson Records` sections (or `<!-- LESSON RECORDS -->` sentinel).
6. Within each section, find all `### [LESSON-ID] <outcome> — YYYY-MM-DD` headings.
7. For each record: extract lesson ID, outcome, date, and body prose. Task reference is `<task_folder>/<NNN>` derived from the file path. Owner is from the task header.
8. Group records by lesson ID.

**Merge and write**:
9. For each lesson: combine lesson metadata (from Pass 1) with grouped records (from Pass 2).
10. Build the ledger document from the template:
    - Header with generation metadata (`<!-- Last assembled: YYYY-MM-DD by <user> -->`)
    - `## Staged` section with active lessons, each rendered as structured entries with Record tables
    - `## Promoted` section preserved from the previous ledger (append-only — read existing, carry forward)
    - `## Archived / Superseded` section preserved from the previous ledger
11. Before writing, read `tasks/README.md` (README Before Write rule).
12. Write `tasks/lessons-ledger.md`.
13. Report:
    - Count of lessons assembled into Staged
    - Count of records rolled up by outcome
    - Any orphan records (records referencing a lesson ID that doesn't exist)
    - Any drift (records for promoted lessons — means someone was still applying a formalized rule)
    - Any warnings from `validate` that would apply to the just-assembled ledger

### `record <lesson-id> <outcome> [reason]`

Log an application or override event in the currently active task.

1. Verify `<lesson-id>` matches the format `L-<task_folder>-<NNN>-<seq>`.
2. Verify `<outcome>` is one of: `applied`, `exception`, `challenged`, `false-positive`.
3. Get the current session ID: `printenv CLAUDE_SESSION_ID`.
4. Read `.state/active-tasks-{session_id}.txt` to find the active task ID.
5. If no active task, error: "No active task — /lessons record must be called while a task is active. Run `/task find` first."
6. If more than one active task, prompt the user to pick which task this record belongs to.
7. Resolve the active task file: glob `tasks/<task_folder>/<NNN>-*.md` (the task gate state file contains the NNN; task_folder is inferred from the person who activated it, or the user is prompted).
8. Read the task file.
9. If no `## Lesson Records` section exists, create one at the end (before `## Changelog`):
   ```markdown
   ## Lesson Records

   <!-- LESSON RECORDS -->
   ```
10. Append a new record block:
    ```markdown
    ### [<lesson-id>] <outcome> — YYYY-MM-DD
    <reason or placeholder "— (no reason given)">
    ```
11. Append a one-liner to the task's `## Changelog`:
    ```
    - YYYY-MM-DD: Recorded <lesson-id> <outcome> — see Lesson Records
    ```
12. Confirm the write and print the lesson's friendly name (dereferenced from the source task) as context.

**Failure modes to handle:**
- Lesson ID doesn't exist in any task: warn but proceed (may be from a task not yet scanned); validate will flag later.
- Active task file has been promoted/discarded itself: still record, but warn.

### `diff`

Show what's changed since the last assembly.

1. Read `tasks/lessons-ledger.md` and extract the `<!-- Last assembled: YYYY-MM-DD -->` metadata.
2. Run `scan` to find current tagged blocks.
3. Report four categories:
   - **New lessons**: Tagged blocks that aren't in the current ledger's Staged section.
   - **Modified lessons**: Lessons whose source task has a changelog date after the assembly date.
   - **New records**: Records in task docs with a date after the assembly date.
   - **Marker changes**: Tags that gained a `LESSONS REVIEWED` marker since assembly.
4. If nothing has changed: `"No changes since last assembly (YYYY-MM-DD)."`

### `validate`

Check the ledger and task docs for consistency and signal quality.

| Check | How | Severity |
|-------|-----|----------|
| **Ledger exists** | `tasks/lessons-ledger.md` exists and isn't a placeholder | Required |
| **Orphan records** | Each record in a task doc references a lesson ID that exists in some source task | Required |
| **ID format** | Every lesson ID matches `L-<task_folder>-<NNN>-<seq>` | Required |
| **Task folder valid** | The `<task_folder>` component of every ID exists in `project.yml` team roster | Required |
| **Noisy lessons** | Flag any staged lesson with >3 `false-positive` OR >2 `challenged` in the last 30 days | Recommended |
| **Untested staged** | Flag any lesson staged >30 days with zero records | Recommended |
| **Stale activity** | Flag any lesson with records but none in the last 60 days — candidate for promotion or archiving | Recommended |
| **Drift** | Flag any record that references a lesson now in `## Promoted` or `## Archived` | Recommended |
| **Ordering drift** | Flag any tagged block where `### ` subsection order has changed since the last assembly (compare to ledger's recorded seq→name mapping) | Recommended |
| **Ledger freshness** | Warn if `<!-- Last assembled -->` is >7 days old and records exist in task docs | Recommended |

Report results grouped by severity. Exit with a summary like:

```
Validation: tasks/lessons-ledger.md (last assembled 2026-04-20)

  [PASS] Ledger exists and is populated
  [PASS] All lesson IDs well-formed
  [WARN] 2 noisy lessons:
    - L-ben-028-02 "Prefer Long-Form Prompts" — 4 challenged in 14 days
    - L-ben-033-08 "Open Questions are Deliverables" — 3 false-positive in 21 days
  [WARN] 1 untested staged lesson:
    - L-ben-017-01 "Formal Doc Pipeline" staged 2026-04-02, zero records

Summary: 2/3 passed | 0 failed | 2 warnings
```

### `list [status]`

Show ledger contents filtered by status.

- `list` — all staged lessons (most common use)
- `list staged` — same as above
- `list promoted` — only the Promoted section
- `list archived` — only the Archived / Superseded section
- `list all` — every lesson across all three sections

For each entry, show: ID, name, origin, categories, record summary (e.g., `5 applied, 1 exception`), last activity date.

### `show <lesson-id>`

Display one lesson's full entry including the full Record table with prose bodies. Reads the source task for the authoritative content (not the ledger) to avoid stale data.

### `promote <lesson-id> <destination> [args]`

Move a lesson to its permanent home. **Interactive** — shows evidence, asks for confirmation, offers edit-before-promote.

1. Verify `<lesson-id>` exists and is currently `staged`.
2. Read the source task to get the full lesson content (not the ledger — source is authoritative).
3. Re-scan all task docs for records of this lesson ID (live, not cached from ledger).
4. Display the evidence:

```
Promoting L-ben-033-01 "Stay High-Level, Ruthlessly" to <destination>

Source: ben/033 — Module Architecture & Classification
Staged: 2026-04-07 (15 days ago)

Records found (7 across 4 tasks):

  [applied]     2026-04-13 ben/041  (ben)
    Moved AWS-specific service names from §3.2 to child SAD...

  [applied]     2026-04-14 ben/041  (ben)
    Caught Okta leak in auth section during review...

  [exception]   2026-04-15 ben/041  (ben)
    Kept "DICOM" at system level. Rationale: DICOM is a protocol, not a
    vendor product — genericizing it would actually harm precision...

  [applied]     2026-04-18 maryna/043  (maryna)
    (no note)

  [challenged]  2026-04-19 maryna/043  (maryna)
    Tried the opposite approach (keeping tech stack table at system level)
    to see if L-ben-033-01 was too strict. Outcome: it worked fine...

  [applied]     2026-04-20 ben/044  (ben)
    (no note)

  [applied]     2026-04-22 ben/045  (ben)
    (no note)

Summary: 5 applied, 1 exception, 1 challenged, 0 false-positive

Analysis:
  - The exception suggests adding a "standards/protocols exception" clause.
  - The challenged record suggests the rule may be slightly over-constrained
    when applied to tech stack tables.

Options:
  (1) Promote as-is — treat exception/challenge as edge cases
  (2) Edit before promoting — refine the text in light of the evidence
  (3) Defer — keep staged, gather more data
  (4) Discard — data doesn't support the lesson
```

5. On user's choice:
   - **(1) Promote as-is**: Write the lesson content to the destination per the Promotion Destinations table. Move the ledger entry from Staged to Promoted (with `**Final home**` field). Write `<!-- LESSONS REVIEWED: promoted to <destination> on YYYY-MM-DD -->` marker in the source task.
   - **(2) Edit**: Open the lesson in a scratch buffer for user editing. After save, write the edited version to the destination and proceed as (1). Also update the source task with the edited content (so future assemblies reflect the refinement).
   - **(3) Defer**: Do nothing. Report "Deferred — lesson remains in Staged."
   - **(4) Discard**: Write `<!-- LESSONS REVIEWED: discarded on YYYY-MM-DD — <reason> -->` marker in source task. Move ledger entry to Archived section with the discard reason.
6. Before any write, read the destination's parent folder README (README Before Write rule).
7. Report what was done, where, and any remaining records in task docs (they stay as history).

**Multi-subsection warning**: If the source task's `<!-- LESSONS LEARNED -->` tag covers multiple `### ` subsections and only one is being promoted, promote writes a **per-lesson marker** that names only the promoted lesson:

```markdown
<!-- LESSONS LEARNED: architecture, documentation, regulatory, process -->
<!-- LESSONS REVIEWED: L-ben-033-03 promoted to glossary on 2026-04-20 -->
```

The scanner respects per-lesson markers: it excludes only the specifically-named lesson from assembly, leaving the rest of the block active.

## Loading Integration

The `## Staged` section of `tasks/lessons-ledger.md` is loaded at session start via a reference in `CLAUDE.md`'s mandatory session-load block. Only the Staged section is loaded — the `## Promoted` and `## Archived / Superseded` sections are audit trail and must not be loaded (context waste, and they'd double-count with their final homes).

**CLAUDE.md instruction (added by the skill during setup):**

> Read `tasks/lessons-ledger.md`, **only the `## Staged` section** (stop at `## Promoted`). These are lessons under active reinforcement — surface them when their situation matches the work at hand and prompt the user with the four options: apply / exception / challenged / false-positive. Log the outcome with `/lessons record`.

## Close-Out Reflection (via `/task update Complete`)

The `/task` skill's `update` action prompts for reflection before marking a task Complete. The prompt offers:

1. Add a `## Lessons Learned` section with a tagged block (harvested by `/lessons assemble`)
2. Add/review `## Lesson Records` (if Claude or the user noticed lesson events that weren't recorded in the moment)
3. Skip — no lessons from this task
4. Defer — mark Complete now, add lessons later

This is the primary intake for implicit lessons. See `.claude/skills/task/SKILL.md` for the exact prompt mechanics.

## Subagent Delegation

| Scenario | Agent Type | Why |
|---|---|---|
| Scan across many tasks while working | Explore | Read-only, runs in background |
| Assemble (long-running harvest) | general-purpose | Needs Write; keeps harvest out of main context |
| Validate (audit pass) | Explore | Read-only |

Actions that must NOT be delegated:
- `record` — must run in the main session because it uses the session's task gate state
- `promote` — interactive evidence review and user prompts
- `show` — lightweight, no delegation needed

## Notes

- If `$ARGUMENTS` is empty or just "help", show this usage guide.
- The ledger is a **generated artifact** for the lesson and record data — do not edit Record tables directly. Edits should flow back to source task docs, then `/lessons assemble` regenerates. You MAY manually edit the ledger's lesson body text before promotion (option (2) in `promote`), but the canonical version is the source task.
- The scanning algorithm is defined in `${CLAUDE_SKILL_DIR}/../shared/task-content-scanner.md`, shared with `/strategy`.
- When writing to the ledger or any promotion destination, follow the README Before Write convention.
- v1 relies on **best-effort detection** — Claude self-checks loaded staged lessons against current situations. No automatic changelog mining; users can always manually `/lessons record` when they spot a violation Claude missed.
- v1.5 candidate: per-user auto-memory write-through of confirmed lessons as `feedback` entries.
- v2 candidate: automatic mining of task changelogs for violation phrases (`"reverted"`, `"originally proposed"`, `"user corrected"`, etc.).

## Best Practices
See [README.md](README.md) — consumed by `/best-practices` audit.

## Changelog
See [README.md](README.md) for version history.

