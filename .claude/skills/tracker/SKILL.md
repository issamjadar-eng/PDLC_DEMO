---
name: tracker
description: "Submission package tracker — build tracker markdown from architecture, regulatory, and composition-manifest context, render HTML dashboard, update status, assess readiness."
version: 6
updated: 2026-04-23
---

# Submission Package Tracker

Build and manage the submission package tracker. Usage: `/tracker <action> [arguments]`

## Source Files

| File | Purpose |
|------|---------|
| `docs/project/submissions/submission-tracker.md` | Source of truth — all deliverables, status, scope, effort, phase, engineering prerequisites |
| `docs/project/submissions/submission-tracker.html` | Generated dashboard — never hand-edit |
| `${CLAUDE_SKILL_DIR}/scripts/render.py` | Python script that generates HTML from markdown |

## Context Required for Building the Tracker

The tracker is not built in isolation — it is derived from composition manifests, architecture, regulatory guidance, and strategy documents. Before adding or modifying deliverables, read the **Context & Sources** section at the top of `submission-tracker.md`. It lists every source document and explains what each one informs.

**Key sources** (in reading order):
1. **Composition manifest** (`docs/project/submissions/<filing>/composition-manifest.md`) — the authoritative list of which DHF pieces are included in this filing. A filing can span multiple DHFs (the manifest records the cross-references). Read this **first** to know which DHFs the tracker must span.
2. **Project manifest** (`project.yml` — `dhfs[]`) — list of DHFs in the project. Each entry's `path` points to a folder under `docs/project/dhfs/` containing per-DHF content.
3. **System SADs** — one per DHF at `docs/project/dhfs/<dhf>/design-controls/architecture/<device-slug>-system-sad.md` (where `<device-slug>` matches the `project.device_family` value from `project.yml`, or the DHF's own slug for multi-component projects) — module architecture, SaMD boundaries, classifications → drives Scope and per-module splits.
4. **Regulatory Strategy** — shared, one file at `docs/project/strategies/regulatory-strategy.md` — filing sequence, PCCP scope, predicate lineage, document reuse, jurisdictional roadmap → drives Phase assignments. Per-component differences are expressed as callout subsections inside this one doc, not as separate per-DHF files. (As of strategy skill v10: all strategy briefs are shared; formal per-DHF outputs — 510(k) submission, PCCP protocol, LMR — still live under `dhfs/<dhf>/design-controls/`, `postmarket/`, etc.)
5. **Submission tracker task** (e.g., `tasks/<person>/NNN-submission-package-tracker.md`) — strategy decisions, filing strategy, parent/child DHF → drives Phase and Part structure.
6. **FDA guidance documents** (`docs/external/fda-guidance/`) — shared; deliverable requirements per guidance → drives what items exist in each Part.

**Composition manifest is the source of truth** (task 007 P4.2): when a filing's composition manifest is updated, the tracker's deliverable list must reflect the new included pieces. `/tracker build` reads the composition manifest at plan time (when producing its output) so reviewers see the full filing impact before any commit.

## Tracker Structure

The tracker markdown has 4 Parts, each serving a different purpose:

| Part | What it tracks | How items get added |
|------|---------------|---------------------|
| **Part 1: Base 510(k)** | Standard 510(k) deliverables required for any submission | Derived from FDA 510(k) SE guidance, sw-functions guidance, ISO 14971, IEC 62304, IEC 62366-1, cybersecurity guidance |
| **Part 2: PCCP Additive** | Additional deliverables because we include a PCCP | Derived from PCCP AI/ML guidance and PCCP General guidance |
| **Part 3: Management Services** | Non-submission regulatory items for MDDS/non-device module | Derived from MDDS regulation (21 CFR 880.6310), MFD guidance, Section 524B |
| **Part 4: Engineering Prerequisites** | Engineering capabilities that gate regulatory deliverables | Derived from analyzing what technical work each deliverable depends on |

### Column Definitions

**Parts 1-3 (regulatory deliverables):**

| Column | Purpose | How to assign |
|--------|---------|---------------|
| **#** | Unique ID. Prefix indicates category (A=Admin, SW=Software, R=Risk, etc.). Suffix indicates module (a=Intra-Op, b=Pre-Op, c=Mgmt Services). | Follow existing prefix convention. Next available number within category. |
| **Deliverable** | Name of the document or artifact. Include module name for per-module items (e.g., "SRS — Intra-Op"). | Match FDA guidance terminology where possible. |
| **Scope** | Device (one for whole product), Per-Module (one per module), Both (device-level referencing per-module detail). | Read System SAD to understand module boundaries. Device-level = covers all modules. Per-Module = specific to one module's internal design. |
| **Effort** | Low / Med / High / V.High. Relative to this project. Per-instance for Per-Module items. | See Effort Scale in the markdown for definitions. |
| **Phase** | When the deliverable must reach target quality. Filing / Filing (proto) / Release 1 / Release 2 / Release 3. | Intra-Op items = Filing. Pre-Op items = Filing (proto) per the Pre-Op filing strategy. See Phase Scale for full rules. |
| **FDA Reference** | Regulation or guidance section that requires this deliverable. | Cite the specific guidance and section (e.g., "PCCP AI/ML Sec VII.B"). |
| **Project Location** | Where the deliverable lives in the project docs/ structure. | Follow the folder conventions in `docs/project/README.md`. |
| **Status** | Not Started / Partial / In Progress / Done. | Not Started = no work product. Partial = legacy or started. In Progress = actively being worked. Done = substantially complete. |
| **Evidence** | What exists today — file references, legacy doc descriptions, notes. | Be specific: "IntraOp PHA v2 (DOCX, 2026-04-08)" not just "exists". |

**Part 4 (engineering prerequisites):**

| Column | Purpose | How to assign |
|--------|---------|---------------|
| **#** | ENG prefix + number + optional module suffix. | ENG1a, ENG1b, ENG2, etc. |
| **Prerequisite** | Name of the engineering capability. Include module for per-module items. | Describe the capability, not the task (e.g., "AI Model Development" not "Train the model"). |
| **Gates** | Comma-separated list of deliverable IDs from Parts 1-3 that cannot be completed until this prerequisite is ready. | Review each gated deliverable — does it truly need this engineering work to exist? |

### Per-Module Naming Convention

Items split by module use letter suffixes:
- **a** = Intra-Op (lead module)
- **b** = Pre-Op
- **c** = Management Services (when applicable)

Exception: SW3 (SRS Intra-Op) and SW4 (SRS Pre-Op) use separate IDs for historical reasons. Both conventions are valid.

### Adding New Deliverables

1. Read the Context & Sources section to understand what informed existing items
2. Identify which Part the deliverable belongs in (regulatory basis determines Part 1 vs 2 vs 3)
3. Assign an ID following the prefix convention for the category
4. For Per-Module items, create separate rows with a/b suffixes
5. Assign Scope, Effort, Phase based on the column definitions above
6. Check if any Part 4 engineering prerequisite gates this deliverable — add to Gates if so
7. If a new engineering capability is needed, add it to Part 4 with its gated deliverables
8. Run `/tracker render` to regenerate the HTML

## Actions

Parse the user's argument string `$ARGUMENTS` to determine which action to perform.

### `init`

First-time setup of the submission tracker for a project. Idempotent — safe to re-run.

**Steps**:
1. **Check prerequisites**:
   - `project.yml` has a non-empty `dhfs[]` list — required, tracker cannot run without it
   - For each entry in `dhfs[]` that maps to this filing (per the composition manifest, if one exists, or all entries if no manifest exists yet), verify:
     - System SAD exists at `docs/project/dhfs/<dhf>/design-controls/architecture/<device-slug>-system-sad.md` (where `<device-slug>` is the `project.device_family` value from `project.yml` for single-component projects, or the DHF's own slug for multi-component projects) — warn if missing, needed for Scope assignments
     - (shared) regulatory strategy exists at `docs/project/strategies/regulatory-strategy.md` — warn if missing. Checked once per project, not per DHF.
   - FDA guidance documents exist in `docs/external/fda-guidance/` — shared, warn if missing
   - Composition manifest exists at `docs/project/submissions/<filing>/composition-manifest.md` — INFO if missing (tracker can run without it for single-DHF projects; required for multi-DHF filings)
2. **Create tracker markdown** (if `docs/project/submissions/submission-tracker.md` does not exist):
   - Scaffold the file with the standard structure: intro, Context & Sources, Two-Level Deliverable Model, Status Legend, Parts 1-4 headers with empty tables, Summary, Effort Scale, Phase Scale, Changelog
   - Populate the Context & Sources section with paths to the architecture and guidance documents found in step 1
   - Tell the user: "Tracker scaffold created. Run `/tracker build` to populate deliverables from regulatory guidance."
3. **Add CLAUDE.md rule** (if not already present):
   - Check `CLAUDE.md` for a "Tracker Skill Before Edit" section under `### For Claude`
   - If missing, add it:
     ```
     #### Tracker Skill Before Edit (MANDATORY)

     **Before editing `docs/project/submissions/submission-tracker.md`**, load the `/tracker` skill (`.claude/skills/tracker/SKILL.md`). It defines column conventions, valid values, naming rules, and the Context & Sources that inform the tracker. After editing, run `/tracker render` to regenerate the HTML dashboard. Do not edit `submission-tracker.html` directly — it is generated output.
     ```
   - Place it after "README Before Write" and before "Task-First Workflow" if those sections exist, otherwise append to the For Claude section
4. **Verify render script**: Confirm `${CLAUDE_SKILL_DIR}/scripts/render.py` exists and is executable
5. **Report** what was created, what was skipped (already exists), and what's missing (prerequisites)

### `build [topic]`

Add or extend deliverables in the tracker markdown. This is the authoring action — it guides creating new items based on regulatory and architectural context.

**Examples**:
- `/tracker build` — review the tracker for completeness against the referenced guidance documents
- `/tracker build cybersecurity` — review cybersecurity deliverables (C1-C8) against the cybersecurity guidance for completeness
- `/tracker build engineering` — review Part 4 engineering prerequisites for missing gates or new capabilities

**Steps**:
1. Read the Context & Sources section of `submission-tracker.md`
2. Read the relevant source documents (System SAD, regulatory guidance, strategy)
3. Compare existing deliverables against what the sources require
4. Propose additions, removals, or reclassifications to the user
5. After user approval, edit the markdown following the column definitions and naming conventions
6. Run `/tracker render` to regenerate the HTML

This action does NOT auto-modify the tracker — it proposes changes and waits for user approval.

### `render`

Regenerate the HTML dashboard from the markdown source.

1. Run: `python3 ${CLAUDE_SKILL_DIR}/scripts/render.py`
2. The script reads `docs/project/submissions/submission-tracker.md`
3. Outputs to `docs/project/submissions/submission-tracker.html`
4. Report: item count, status breakdown, any parse warnings

The render script preserves existing help content from the previous HTML when items haven't changed. New items get auto-generated help content.

### `update <id> <field> <value>`

Update a deliverable's field in the markdown source.

**Fields**: `status`, `effort`, `phase`, `evidence`

**Examples**:
- `/tracker update SW3 status Partial`
- `/tracker update ENG2a status "In Progress"`
- `/tracker update R2a evidence "IntraOp PHA v2 (DOCX, updated 2026-04-08)"`

**Steps**:
1. Read `submission-tracker.md`
2. Find the row matching `<id>` (exact match on first column)
3. Update the specified field value
4. Write the file
5. Report what changed
6. Suggest: "Run `/tracker render` to update the HTML dashboard"

### `status [filter]`

Show summary counts without opening the HTML.

- `/tracker status` — full summary (by part, by status, by phase, by effort)
- `/tracker status filing` — show only Filing-phase items with status breakdown
- `/tracker status engineering` — show only Part 4 engineering prerequisites

**Steps**:
1. Read `submission-tracker.md`
2. Parse all deliverable rows
3. Display summary tables in terminal

**Output format**:
```
Submission Tracker Status
─────────────────────────
Parts:     89 Base │ 48 PCCP │ 7 Mgmt Svc │ 20 Engineering │ 164 Total
Status:    1 Done │ 16 Partial │ 147 Not Started
Phase:     119 Filing │ 38 Filing (proto) │ 4 Release 1 │ 2 Release 2
Effort:    XX Low │ XX Med │ XX High │ XX V.High
```

### `assess`

Auto-detect status mismatches by checking whether expected files exist.

**Steps**:
1. Read `submission-tracker.md`
2. For each deliverable with a `Project Location` that maps to a file path:
   - Glob for files matching the expected location
   - If files exist but status is "Not Started" → flag as potential mismatch
   - If no files exist but status is "Partial" or "Done" → flag as potential mismatch
3. Report findings with suggested status updates

This is advisory — it suggests changes, doesn't auto-apply them.

### `help`

Show this usage guide.

## Markdown Table Structure

The render script expects markdown tables in this format:

**Parts 1-3 (regulatory deliverables)**:
```
| # | Deliverable | Scope | Effort | Phase | FDA Reference | Project Location | Status | Evidence |
```

**Part 4 (engineering prerequisites)**:
```
| # | Prerequisite | Scope | Effort | Phase | Status | Gates |
```

**Valid values**:
- **Scope**: Device, Per-Module, Both
- **Effort**: Low, Med, High, V.High
- **Phase**: Filing, Filing (proto), Release 1, Release 2, Release 3
- **Status**: Not Started, Partial, In Progress, Done

## HTML Dashboard Features

The generated HTML includes:
- **5 summary cards**: Base, PCCP, Mgmt Services, Engineering, Total
- **4-way filtering**: Status × Scope × Phase × Part (AND logic)
- **Progress bars**: Per-part with done/partial segments
- **Collapsible categories**: Click headers to expand/collapse
- **Help rows**: Click any deliverable row for contextual help (regulatory text, examples, current state)
- **Engineering Gates**: Part 4 shows which deliverable IDs each prerequisite gates
- **Color-coded badges**: Status (green/yellow/gray), Scope (blue/cyan/purple), Effort (green→red), Phase (solid blue/dashed blue/green/orange)
- **Self-contained**: No external CSS or JS dependencies

## Best Practices
See [README.md](README.md) — consumed by `/best-practices` audit.

## Changelog
See [README.md](README.md) for version history.

