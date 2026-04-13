---
name: docflow
description: "Document conversion and round-trip management — convert between markdown and formal formats (DOCX, PDF, XLSX) with image fidelity, metadata tracking, and cross-reference resolution"
version: 1
updated: 2026-04-03
---

# Docflow

Move documents between markdown and formal formats with full image fidelity, metadata tracking, and cross-reference resolution. Usage: `/docflow <action> [arguments]`

## Supporting Files

This skill includes supporting files in `${CLAUDE_SKILL_DIR}/`:

| File | Used By | Purpose |
|------|---------|---------|
| `agents/converter.md` | `convert`, `batch` | Agent prompt: source → source-md conversion |
| `agents/refresher.md` | `refresh` | Agent prompt: updated source → merge into existing markdown |
| `agents/importer.md` | `import` | Agent prompt: formal DOCX/PDF → project markdown (Phase 2) |
| `agents/exporter.md` | `export` | Agent prompt: project markdown → formal DOCX/PDF (Phase 2) |
| `templates/frontmatter-source.md` | `convert`, `refresh` | YAML frontmatter template for source-md files |
| `templates/frontmatter-project.md` | `import`, `export` | YAML frontmatter template for project docs (Phase 2) |
| `scripts/extract_images.sh` | `convert`, `refresh`, `import` | Image extraction helper |

## Actions

Parse the user's argument string `$ARGUMENTS` to determine which action to perform.

### `help [action]`

Display help information about docflow.

- `help` (no argument): Show the full help overview below
- `help <action>`: Show detailed help for a specific action

**Full help overview** (display when user runs `/docflow help` or `/docflow` with no arguments):

```
DOCFLOW — Document conversion and round-trip management

  Move documents between markdown and formal formats (DOCX, PDF) with
  full image fidelity, metadata tracking, and cross-reference resolution.

WHEN TO USE DOCFLOW:
  "I need to convert a QMS source document to markdown"    → /docflow convert <doc-id>
  "QMS updated an SOP, I need to refresh the markdown"     → /docflow refresh <doc-id>
  "I need to convert a batch of source documents"          → /docflow batch <category>
  "I wrote markdown and need a Word doc"                   → /docflow export <file>
  "I have a Word doc and need to edit it in markdown"      → /docflow import <file>
  "Someone reviewed my Word doc and sent it back"          → /docflow import <file> --comments
  "I need to work through the reviewer's comments"         → /docflow reconcile <file>
  "I need to check if a conversion is good"                → /docflow validate <doc-id>
  "How far along are we on conversions?"                   → /docflow status

ACTIONS:
  convert <doc-id>          Source doc → markdown (QMS reference docs)
  refresh <doc-id>          Update markdown from new source version
  batch <category>          Bulk convert by priority category (P1-P7)
  export <file> [flags]     Markdown → formal DOCX or PDF (Phase 2)
  import <file> [flags]     Formal DOCX/PDF → markdown (Phase 2)
  reconcile <file>          Resolve external review comments (Phase 2)
  validate <doc-id|file>    Quality checks against conversion standards
  status                    Progress dashboard
  help [action]             This help, or detailed help for an action
  guide                     Interactive workflow selector

FLAGS:
  --format docx|pdf         Output format for export (default: docx)
  --redline                 Export with tracked changes vs. previous version
  --comments                Import with comment extraction
  --clean                   Export clean version (strip review annotations)
  --toolchain               With validate: check CLI tool availability

REQUIREMENTS:
  pandoc, pdftotext, pdfimages (poppler), libreoffice, unzip
  Run /docflow validate --toolchain to check availability.

KNOWN LIMITATIONS:
  - No visual formatting preservation (colors, fonts, cell shading)
  - Scanned PDFs need OCR fallback (Claude Read tool)
  - XLSX embedded charts require LibreOffice render or screenshot
  - VBA/macros lost in DOC → DOCX conversion
  - Complex nested tables flattened to sequential tables
  - Large documents (>100 pages) may need manual splitting
  - Round-trip MD→DOCX→MD won't produce identical markdown
  - One person owns the markdown at a time (use git for version control)

Type /docflow help <action> for detailed usage and examples.
```

**Per-action help** — when user runs `/docflow help <action>`, display the relevant block:

#### `help convert`
```
/docflow convert <doc-id>

WHAT: Convert an internal QMS source document (SOP, Form, Policy, WI) to markdown.
WHEN: You need a readable markdown version of a QMS document for reference.
WORKFLOW: WF-4 (Template conformance)

WHEN NOT TO USE:
  - To import a project DOCX you're editing → use /docflow import
  - To update an already-converted doc from a new source → use /docflow refresh

HOW IT WORKS:
  1. Resolves doc-id to source file in docs/internal/source/
  2. Detects format (PDF, DOCX, DOC, XLSX)
  3. Writes to staging area (source-md/.staging/{doc-id}/)
  4. Extracts content, images, builds frontmatter
  5. Resolves cross-references against INDEX.md
  6. Validates output (all Required quality checks)
  7. On success: moves to source-md/, deletes staging
  8. On failure: leaves staging for inspection

PRODUCES:
  docs/internal/source-md/{original-filename}.md
  docs/internal/source-md/images/{doc-id}_{descriptor}.{ext}

EXAMPLES:
  /docflow convert FORM-000137230
  /docflow convert SOP-000355609
  /docflow convert WI-000101591
```

#### `help refresh`
```
/docflow refresh <doc-id>

WHAT: Update a source-md file from a revised source document, preserving manual edits.
WHEN: QMS has issued a new version of an SOP/Form/Policy/WI.
WORKFLOW: WF-4 (Template conformance — revision cycle)

WHEN NOT TO USE:
  - For first-time conversion → use /docflow convert
  - If you want to discard all manual edits → delete the source-md and use /docflow convert

HOW IT WORKS:
  1. Finds existing source-md file and new source document
  2. Converts new source through standard pipeline (in staging)
  3. Diffs new conversion against existing source-md
  4. Merges: new/changed content incorporated, manual refinements preserved
  5. Flags conflicts where manual edits and source changes overlap
  6. Validates, then commits or fails (same staging flow as convert)

PRODUCES:
  Updated source-md file with conversion_history in frontmatter.
  Report: sections changed, images added/removed, conflicts flagged.
```

#### `help batch`
```
/docflow batch <category>

WHAT: Convert multiple source documents in a priority category.
WHEN: You're ready to convert a batch of related documents.

CATEGORIES (by priority):
  P1  Design Controls — Plans/Reviews (~17 docs)
  P2  Risk Management (~14 docs)
  P3  Software Development (~8 docs)
  P4  Regulatory Submissions (~12 docs)
  P5  V&V (~16 docs)
  P6  Cybersecurity (~6 docs)
  P7  Remaining (~54 docs)

QUALITY GATE:
  ≥3 consecutive Required failures → batch stops (systemic issue)
  ≥30% failure rate after 10+ docs → batch stops
  Warnings → continue, report at end
  Single failure → skip, continue, report at end

PRODUCES:
  Batch summary report with per-document pass/fail/warning status.
```

#### `help validate`
```
/docflow validate <doc-id|file>
/docflow validate --toolchain

WHAT: Check a converted file against quality criteria, or verify CLI tools.

QUALITY CHECKS:
  Required:  Frontmatter complete, heading structure, content present,
             images accounted for, image manifest, conversion notes
  Warning:   Tables intact, form fields marked, cross-refs tagged, no OCR artifacts

ALSO CHECKS:
  - Orphaned staging directories (incomplete conversions)
  - Unresolved cross-references

TOOLCHAIN CHECK (--toolchain):
  Verifies: pandoc, pdftotext, pdfimages, libreoffice, unzip
```

#### `help export`
```
/docflow export <file> [--format docx|pdf] [--redline] [--clean]

WHAT: Export a markdown document to formal DOCX or PDF.
WHEN: You've written or edited markdown and need a formal deliverable.
WORKFLOW: WF-1 (new doc), WF-2 (revision), WF-3 (post-reconciliation)
STATUS: Phase 2 — not yet implemented.
```

#### `help import`
```
/docflow import <file> [--comments]

WHAT: Import a formal DOCX/PDF into project markdown.
WHEN: You have an existing formal document you want to edit in markdown.
WORKFLOW: WF-2 (existing doc revision), WF-3 (external review)
STATUS: Phase 2 — not yet implemented.

WITH --comments:
  Extracts Word comments as markdown annotations for /docflow reconcile.
```

#### `help reconcile`
```
/docflow reconcile <file>

WHAT: Interactively resolve external review comments embedded in markdown.
WHEN: After /docflow import --comments, to work through reviewer feedback.
WORKFLOW: WF-3 (external review round-trip)
STATUS: Phase 2 — not yet implemented.
```

#### `help status`
```
/docflow status

WHAT: Show overall conversion progress and batch history.

DISPLAYS:
  - Total converted vs remaining (N / 127)
  - Per-category progress (P1-P7)
  - Incomplete conversions in staging
  - Unresolved cross-references count
  - Last batch results
```

### `guide`

Interactive workflow selector for users who aren't sure which action to use.

Present this menu and wait for user response:

```
What are you trying to do?

  1. Convert an internal QMS document (SOP, Form, Policy, WI) to markdown
  2. Create a formal Word/PDF from a markdown document I wrote
  3. Bring a Word/PDF document into markdown for editing
  4. Incorporate feedback from someone who reviewed a Word document
  5. Update a markdown file because the source document was revised
  6. Check the quality of a converted document
  7. See overall conversion progress

Enter a number (1-7):
```

Based on response:
- **1** → Recommend `/docflow convert <doc-id>` or `/docflow batch <category>`. Ask if they know the doc-id.
- **2** → Recommend `/docflow export <file>`. Note: Phase 2, not yet implemented.
- **3** → Recommend `/docflow import <file>`. Note: Phase 2, not yet implemented.
- **4** → Recommend `/docflow import <file> --comments` then `/docflow reconcile <file>`. Note: Phase 2.
- **5** → Recommend `/docflow refresh <doc-id>`.
- **6** → Recommend `/docflow validate <doc-id|file>`.
- **7** → Recommend `/docflow status`.

### `convert <doc-id>`

Convert a single source document to markdown.

1. **Resolve the source file**: Search `docs/internal/source/` recursively for a file whose name starts with `<doc-id>`. If multiple matches, ask the user to disambiguate. If no match, report error.

2. **Detect format**: Check file extension (`.pdf`, `.docx`, `.doc`, `.xlsx`).

3. **Check for existing conversion**: Look for a matching file in `docs/internal/source-md/`. If found, warn: _"A source-md file already exists for this doc-id. Use `/docflow refresh` to update it, or confirm you want to overwrite."_

4. **Read the agent prompt**: Read `${CLAUDE_SKILL_DIR}/agents/converter.md`.

5. **Parameterize and spawn agent**: Inject these parameters into the agent prompt:
   - `SOURCE_PATH`: Full path to source file
   - `DOC_ID`: The document ID (e.g., `FORM-000137230`)
   - `DOC_TYPE`: FORM, SOP, POL, WI, or QSD
   - `FORMAT`: pdf, docx, doc, or xlsx
   - `TITLE`: Document title (from filename, after the doc-id and separator)
   - `OUTPUT_DIR`: `docs/internal/source-md/`
   - `STAGING_DIR`: `docs/internal/source-md/.staging/{DOC_ID}/`
   - `IMAGE_DIR`: `docs/internal/source-md/images/`
   - `INDEX_PATH`: `docs/internal/source/INDEX.md` (for cross-reference resolution)

   Spawn an Agent with the parameterized prompt.

6. **Report result**: Show the agent's summary — file written (or failure), image count, cross-references resolved/unresolved, any conversion notes.

### `refresh <doc-id>`

Refresh an existing source-md file from an updated source document.

1. **Find existing source-md**: Search `docs/internal/source-md/` for a file matching `<doc-id>`. If not found, suggest `/docflow convert` instead.

2. **Find new source**: Search `docs/internal/source/` for the source file.

3. **Read the agent prompt**: Read `${CLAUDE_SKILL_DIR}/agents/refresher.md`.

4. **Parameterize and spawn agent**: Same parameters as `convert`, plus:
   - `EXISTING_MD_PATH`: Path to the current source-md file
   
   Spawn an Agent with the parameterized prompt.

5. **Report result**: Sections changed, images added/removed, conflicts flagged.

### `batch <category>`

Convert multiple documents in a priority category.

1. **Resolve category**: Map `<category>` to a document list using `docs/internal/source/INDEX.md`:
   - `P1` or `design-controls` → Design Controls — Plans, Reviews, & Phase Gates + Design Controls — Traceability
   - `P2` or `risk` → Risk Management
   - `P3` or `software` → Software Development
   - `P4` or `regulatory` → Regulatory Submissions
   - `P5` or `vnv` → Verification & Validation
   - `P6` or `cybersecurity` → Cybersecurity / Product Security
   - `P7` or `remaining` → All remaining categories

2. **Filter already-converted**: Check which doc-ids already have source-md files. Report: _"N of M already converted, converting remaining K."_

3. **Run conversions**: Spawn parallel converter agents (up to 5 concurrent). Each uses the same staging flow as individual `convert`.

4. **Quality gate enforcement**:
   - Track consecutive Required failures. If ≥3, stop the batch.
   - After 10+ docs, if failure rate ≥30%, stop the batch.
   - Warnings: continue, accumulate for report.

5. **Produce batch report**: Show per-document results (pass/fail/warning), total counts, any quality gate triggers.

### `validate <doc-id|file>`

Check a converted file against quality criteria.

If argument is `--toolchain`, check CLI tool availability instead:
- `pandoc` — run `which pandoc`
- `pdftotext` — run `which pdftotext`
- `pdfimages` — run `which pdfimages`
- `libreoffice` — run `which libreoffice`
- `unzip` — run `which unzip`
Report which are available and which are missing with install instructions.

Otherwise, validate a converted document:

1. **Find the file**: If `<doc-id>`, search `docs/internal/source-md/` for matching file. If `<file>`, use the path directly.

2. **Run quality checks**:

| Check | Pass Criteria | Severity |
|-------|--------------|----------|
| Frontmatter complete | All required fields populated (doc_id, doc_type, title, format, conversion_date, conversion_method, conversion_fidelity) | **Required** |
| Heading structure | At least one H1 and one H2 | **Required** |
| Source content present | Word count > 50 (excluding frontmatter) | **Required** |
| Images accounted for | Every image in `images/` matching this doc-id is referenced in markdown; if `image_count > 0`, all listed images exist as files | **Required** |
| Image manifest present | If `image_count > 0`, `## Image Manifest` section exists with table | **Required** |
| Tables intact | Markdown contains at least one table if `has_tables: true` | **Warning** |
| Form fields marked | If `has_form_fields: true`, at least one `[____]`, `- [ ]`, or `[SIGNATURE` present | **Warning** |
| Cross-references tagged | References to other docs use `[DOC-ID — Title]` or `[Title]` format | **Warning** |
| No OCR artifacts | No sequences of 3+ consecutive non-ASCII garbled characters | **Warning** |
| Conversion notes present | If `conversion_fidelity` is `partial`, `notes:` field is non-empty | **Required** |

3. **Check for orphaned staging**: Report any directories in `source-md/.staging/`.

4. **Report results**: List each check with pass/fail/warning, overall status.

### `status`

Show overall conversion progress.

1. **Count source documents**: Read `docs/internal/source/INDEX.md`, count unique doc-ids.

2. **Count converted**: Count `.md` files in `docs/internal/source-md/` (excluding README.md).

3. **Check staging**: Count directories in `source-md/.staging/`.

4. **Categorize progress**: Map converted doc-ids to priority categories (P1-P7).

5. **Display dashboard**:
```
Docflow Status

  Overall: N / 127 converted (X%)

  By category:
    P1 Design Controls:    N1 / T1
    P2 Risk Management:    N2 / T2
    P3 Software Dev:       N3 / T3
    P4 Regulatory:         N4 / T4
    P5 V&V:                N5 / T5
    P6 Cybersecurity:      N6 / T6
    P7 Remaining:          N7 / T7

  In staging (incomplete): S
  Toolchain: pandoc ✓  pdftotext ✓  pdfimages ✓  libreoffice ✗  unzip ✓
```

### `export`, `import`, `reconcile`

**Phase 2 — not yet implemented.**

If invoked, display:
```
/docflow {action} is planned for Phase 2.

Phase 2 covers:
  - WF-1: Export markdown → formal DOCX/PDF
  - WF-2: Import formal → markdown for editing, re-export with redlines
  - WF-3: Import with comments, reconcile, re-export clean

Current Phase 1 actions available:
  convert, refresh, batch, validate, status, help, guide
```

## Conventions

### Source-MD Filename Convention

Source-md filenames **must match** the source filename exactly, with only the extension changed:
- Source: `FORM-000137230 - Design and Development Plan.docx`
- Source-md: `FORM-000137230 - Design and Development Plan.md`

### Image Naming Convention

All extracted images live in `docs/internal/source-md/images/`:
```
{doc-id}_{descriptor}.{ext}
```
- `{doc-id}`: Lowercase (e.g., `form-000137230`)
- `{descriptor}`: Short kebab-case label, unique within the document
- `{ext}`: PNG preferred. Convert EMF/WMF to PNG.

### Frontmatter

Every source-md file begins with YAML frontmatter. See `${CLAUDE_SKILL_DIR}/templates/frontmatter-source.md` for the template.

### Cross-Reference Format

- Doc-id present: `[DOC-ID — Title]`
- Title only: `[Title]` with `<!-- ref: matched to DOC-ID by title -->` if resolved
- Unresolved: leave as prose with `<!-- ref: unresolved -->`

### Atomic Writes

All conversions use a staging area (`source-md/.staging/{doc-id}/`). Output moves to final location only after validation passes. Failed conversions leave staging intact for debugging.

## Best Practices

<!-- Read by /best-practices skill to audit project setup -->

| Check | How to Verify | Severity |
|-------|--------------|----------|
| Docflow skill installed | `.claude/skills/docflow/SKILL.md` exists | Required |
| Source-md directory exists | `docs/internal/source-md/` exists | Required |
| Images directory exists | `docs/internal/source-md/images/` exists | Required |
| Staging gitignored | `.gitignore` contains `source-md/.staging/` | Required |
| Toolchain available | `pandoc`, `pdftotext`, `pdfimages` are on PATH | Required |
| No orphaned staging | `docs/internal/source-md/.staging/` is empty | Recommended |
| INDEX.md exists | `docs/internal/source/INDEX.md` exists (needed for cross-ref resolution) | Required |

## Notes

- If `$ARGUMENTS` is empty or just "help", show the full help overview
- The `convert` and `refresh` actions spawn agents from `${CLAUDE_SKILL_DIR}/agents/`
- Phase 2 actions (export, import, reconcile) are defined but not yet implemented
- LibreOffice is required only for `.doc` files (16 of 127). All other formats work without it
- The staging area is never committed to git

## Changelog

- 1 (2026-04-03): Initial version — convert, refresh, batch, validate, status, help, guide actions. Phase 1 (WF-4 source conversion) fully specified. Phase 2 (WF-1/2/3 import/export) stubbed.
