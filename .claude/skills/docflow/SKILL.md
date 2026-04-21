---
name: docflow
description: "Document conversion and round-trip management between markdown and formal formats (DOCX, DOC, PDF, XLSX). Use this skill whenever a user asks to convert, adopt, import, export, refresh, round-trip, or 'test docflow on' any .docx / .doc / .pdf / .xlsx / .pptx file — whether under docs/internal/source/ (QMS SOPs, forms, policies, work instructions), under docs/project/dhfs/**/formal/ (DHF working drafts), or elsewhere in the repo. Also use when a user asks to extract images, resolve cross-references, or handle external review comments against any of those formats. Owns the conversion pipeline — image extraction, frontmatter, cross-ref resolution, quality gates, round-trip metadata — so direct pandoc / unzip / soffice / pdftotext calls are blocked by a PreToolUse Bash hook installed by the skill's `setup` action; `/docflow <action>` is the supported entry point."
version: 27
updated: 2026-04-20
---

# Docflow

Move documents between markdown and formal formats with full image fidelity, metadata tracking, and cross-reference resolution. Usage: `/docflow <action> [arguments]`

## Supporting Files

This skill includes supporting files in `${CLAUDE_SKILL_DIR}/`:

| File | Used By | Purpose |
|------|---------|---------|
| `agents/converter.md` | `convert`, `batch` | Agent prompt: source → source-md conversion |
| `agents/refresher.md` | `refresh` | Agent prompt: updated source → merge into existing markdown |
| `agents/adopter.md` | `adopt` | Agent prompt: DHF formal → working MD with project frontmatter, template/SOP inference, suffix versioning |
| `agents/reviewer.md` | `review` | Agent prompt: validate an adopted working MD against its source; detect Mermaid faithfulness violations, frontmatter gaps, ref/image issues; report or fix |
| `references/classification-taxonomy.md` | `adopt` (Phase 5e), `review` (Phase 4 requirements audit) | Canonical industry-informed classification tags for requirement docs — 9 tags anchored in ISO 25010, ISO 14971, IEC 62366, IEC 81001-5-1, 21 CFR Part 11, MDR GSPR, HIPAA/GDPR. NOT project-editable. |
| `agents/importer.md` | `import` | Agent prompt: formal DOCX/PDF → project markdown (Phase 2) |
| `agents/exporter.md` | `export` | Agent prompt: project markdown → formal DOCX/PDF (Phase 2) |
| `templates/frontmatter-source.md` | `convert`, `refresh` | YAML frontmatter template for source-md files |
| `templates/frontmatter-project.md` | `adopt`, `import`, `export` | YAML frontmatter template for project-doc working MD (adopt schema — active; export/import remain Phase 2) |
| `scripts/extract_images.sh` | `convert`, `refresh`, `adopt`, `import` | Image extraction helper |
| `hooks/block-direct-conversion.sh` | `setup` | PreToolUse Bash hook — blocks direct pandoc/unzip/soffice/pdftotext/pdfimages/pdftoppm/qpdf/pdftk calls against `.docx\|.doc\|.xlsx\|.xls\|.pptx\|.ppt\|.pdf` unless `.state/docflow-active` is set (state folder is at project root, relocated from `.claude/state/` in ben/083). Installed by `setup` as a symlink into `.claude/hooks/`. |

## Actions

Parse the user's argument string `$ARGUMENTS` to determine which action to perform.

### Natural-language routing

Before literal action-keyword parsing, detect natural phrasings in `$ARGUMENTS` and rewrite to the canonical form. Applies only when `$ARGUMENTS` does not start with a known action keyword (`help`, `guide`, `convert`, `refresh`, `batch`, `adopt`, `export`, `import`, `reconcile`, `validate`, `sync-known-refs`, `status`).

| User phrasing (regex, case-insensitive) | Rewrite to |
|---|---|
| `\badopt\b\|pull.*(into\|as) working\|convert.*formal.*(to\|into) (working )?(md\|markdown)\|make.*working (copy\|md).*of` | `adopt ` + rest |
| `dry.?run.*adopt\|plan.*adopt\|preview.*adopt` | `adopt --plan ` + rest |
| `re.?adopt\|refresh (the )?working` | `adopt --refresh ` + rest |
| `\breview\b.*(adopted\|working md\|mermaid)\|verify.*(adopted\|working md)\|audit.*(adopted\|working md)\|check.*(mermaid\|fidelity)` | `review ` + rest |
| `review.*--?fix\|fix.*review.*issues\|apply.*review.*correction` | `review --fix ` + rest |

Unmatched natural-language input with no action keyword → show the full help overview.

### `setup`

Wire up the PreToolUse Bash tripwire hook that blocks direct document-conversion tool calls. Idempotent — safe to re-run. Also accepted as `init` for discoverability.

This action follows the skill-creator convention (symlink into `.claude/hooks/`, register via shared `register-hook.sh`) so that `/medtech-docs init` Step 5 auto-discovers and runs it.

1. Verify `jq` is available (required by the hook). If missing, warn: `"Install jq via brew install jq (or apt install jq)"` and stop.
2. Verify `.claude/hooks/register-hook.sh` exists. If missing: warn `"Run /task setup first — it installs the hook registration helper"` and stop. (Same dependency pattern as `/secops setup`.)
3. Create `.claude/hooks/` and `.state/` (at project root) directories if they do not already exist. (`.state/` relocated from `.claude/state/` in ben/083 to escape Claude Code's `.claude/**` sensitive-file guard.)
4. Create symlink `.claude/hooks/block-direct-conversion.sh` → `../skills/docflow/hooks/block-direct-conversion.sh` (skip if already a symlink pointing to the same target). Ensure the source hook file is executable.
5. Register the hook via the shared helper:
   ```bash
   .claude/hooks/register-hook.sh PreToolUse "Bash" command \
     '"$CLAUDE_PROJECT_DIR"/.claude/hooks/block-direct-conversion.sh'
   ```
   `register-hook.sh` is idempotent — safe to re-run; it detects duplicates by exact command match.
6. Report what was done: symlink path, hook-registration result (added vs already-present), and the one-line bypass instruction (`touch .state/docflow-active` / `rm .state/docflow-active`).
7. **Do NOT add `.state/docflow-active` to `.gitignore`** — `.state/` should already be gitignored at a directory level (see `/task setup`). Confirm by reading `.gitignore` and warn if `.state/` (or parent) is not present.

**Bypass mechanics.** The hook honors `.state/docflow-active` as an on/off marker. `/docflow` actions that legitimately need to invoke pandoc/unzip/soffice/pdftotext (currently `convert`, `refresh`, `batch`, `adopt` and their spawned agents) should:

```bash
touch .state/docflow-active
# ... run pandoc / unzip / etc. ...
rm -f .state/docflow-active
```

Use a `trap` so the marker is removed even on failure:
```bash
trap 'rm -f "$PROJECT_DIR/.state/docflow-active"' EXIT
touch "$PROJECT_DIR/.state/docflow-active"
```

The marker is a file, not a lock — concurrent `/docflow` runs are rare in practice, and the simple file-flag covers the single-user CLI case this skill is designed for.

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
  "I need to make a DHF formal doc editable in markdown"   → /docflow adopt <target>
  "I need to adopt a whole DHF's formal content"           → /docflow adopt <dhf>
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
  adopt <target> [flags]    DHF formal doc → round-trippable working MD
                            (suffix versioning + template/SOP inference +
                            filing composition). Target: file | <dhf> | <dhf> --area <a>
  review <target> [--fix]   Validate an adopted working MD against its
                            source document. Detects Mermaid faithfulness
                            violations (containment, layout, edge-routing,
                            invented labels), frontmatter gaps, ref/image
                            issues. Report-only by default; --fix applies
                            non-ambiguous corrections and flags the rest
                            with `%% REVIEW:` comments.
  export <file> [flags]     Markdown → formal DOCX or PDF (Phase 2)
  import <file> [flags]     Formal DOCX/PDF → markdown (Phase 2)
  reconcile <file>          Resolve external review comments (Phase 2)
  validate <doc-id|file>    Quality checks against conversion standards
  sync-known-refs           Harvest unresolved refs from converted files → INDEX.md
  status                    Progress dashboard
  help [action]             This help, or detailed help for an action
  guide                     Interactive workflow selector

FLAGS:
  --format docx|pdf         Output format for export (default: docx)
  --redline                 Export with tracked changes vs. previous version
  --comments                Import with comment extraction
  --clean                   Export clean version (strip review annotations)
  --toolchain               With validate: check CLI tool availability
  --index                   With validate: check INDEX.md + qms-reference-graph.md cover all source/ docs
  --readmes                 With validate: check READMEs under docs/internal/ reference current project-layer artifact paths

REQUIREMENTS:
  CLI tools:    pandoc, pdftotext, pdfimages (poppler), libreoffice, unzip
  Python deps:  openpyxl, pyyaml, Pillow
  Install CLI:  brew install pandoc poppler libreoffice   (macOS)
                apt install pandoc poppler-utils libreoffice unzip   (Debian/WSL)
  Install Py:   pip3 install --break-system-packages --user openpyxl pyyaml Pillow
                (or equivalent under uv / pipx on PEP-668 systems)
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

#### `help adopt`
```
/docflow adopt <target> [flags]

WHAT: Adopt a formal DHF document (or a whole DHF's formal content) into
      round-trippable working markdown — the working MD becomes the authoring
      source of truth that will round-trip back to formal on release.
WHEN: You've migrated formal content into a DHF and want to start authoring
      against a workable markdown copy instead of editing binaries.

WHEN NOT TO USE:
  - To convert read-only QMS reference docs → use /docflow convert
  - To refresh a working MD because the formal changed out-of-band →
    use /docflow adopt --refresh <file>
  - To produce a formal DOCX/PDF from working MD → use /docflow export
    (Phase 2, not yet built)

HOW IT WORKS:
  1. Resolves target (single file, DHF name, or <dhf> --area <sub-area>)
  2. Preflight: DHF in project.yml; no unsuffixed+suffixed collisions;
     Forms + SOPs index available for inference
  3. For each formal file:
     a. Detect source_version from filename suffix (default v1)
     b. git mv formal to <stem>-v{source_version}.{ext} if unsuffixed
     c. Run converter pipeline into staging
     d. Auto-infer template_of + authored_per (confidence-scored)
     e. Auto-populate dhf/dhf_role/dhf_area/source_formal/target_formal/
        version_lineage/filings
     f. Validate against frontmatter-project.md schema
     g. Move working MD to <stem>-v{working_version}.md alongside formal/
     h. Re-render parent-README sentinel blocks
  4. Report summary + list of low-confidence inferences for manual review

NATURAL-LANGUAGE PHRASINGS (skill entry routes these to adopt):
  "adopt this formal doc"                    "pull this into working MD"
  "convert the DHF formal docs to working"   "make a working copy of ..."

TARGET FORMS:
  /docflow adopt <file>                 Single formal doc
  /docflow adopt <dhf>                  All formal/ content in a DHF
  /docflow adopt <dhf> --area <area>    Scope to one sub-area

FLAGS:
  --plan              Dry run — inventory + planned actions, no writes
  --refresh <file>    Re-adopt a file whose formal changed out-of-band.
                      Previous working MD gets status: obsolete; new
                      working MD created at the next version.
  --force             Skip "working MD already exists" warning
  --no-rename         Skip formal rename (advanced — breaks version lineage
                      consistency, for manual recovery only)

PRODUCES:
  <dhf-area>/<stem>-v{N+1}.md                  (working MD)
  <dhf-area>/formal/<stem>-v{N}.{ext}          (renamed formal, via git mv)
  <dhf-area>/images/                           (extracted images, if any)

EXAMPLES:
  /docflow adopt hiplink-mgmt-services --plan
  /docflow adopt hiplink-pre-op --area design-controls/user-needs
  /docflow adopt docs/project/dhfs/hiplink-pre-op/design-controls/user-needs/formal/AFAI-HipLink\ Planning-170426-111505.pdf
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
/docflow validate --index

WHAT: Check a converted file against quality criteria, or verify CLI tools,
      or verify INDEX.md covers every source/ doc.

QUALITY CHECKS:
  Required:  Frontmatter complete, heading structure, content present,
             images accounted for, image manifest, conversion notes
  Warning:   Tables intact, form fields marked, cross-refs tagged, no OCR artifacts

ALSO CHECKS:
  - Orphaned staging directories (incomplete conversions)
  - Unresolved cross-references

TOOLCHAIN CHECK (--toolchain):
  Verifies: pandoc, pdftotext, pdfimages, libreoffice, unzip

INDEX CHECK (--index):
  Verifies: every doc-id in docs/internal/source/ appears in INDEX.md;
            every INDEX.md entry either has a matching source file OR is
            listed under "Known References — Not Yet in Source";
            every Known Reference has a Title column populated (warn if
            the title is unknown — converter should have captured it).
  Runs automatically as a preflight before convert and batch — use this
  form to inspect the gap directly.
```

#### `help sync-known-refs`
```
/docflow sync-known-refs [--dry-run]

WHAT: Harvest unresolved cross-references from converted source-md files
      and merge them into INDEX.md's "Known References — Not Yet in Source"
      table, with titles captured from the citing docs' frontmatter.
WHEN: After a batch conversion run, to promote newly-discovered unresolved
      refs into the project-level INDEX so future converters treat them as
      known-absent instead of flagging them as new unresolved.

HOW IT WORKS:
  1. Walks every .md file under docs/internal/source-md/ (except READMEs)
  2. Parses YAML frontmatter `references:` block; extracts each item's
     doc_id, title, resolved, match, note
  3. Filters to items where resolved == false AND doc_id ∉ source/ AND
     doc_id ∉ INDEX.md functional tables
  4. Groups by doc_id, keeps the first-seen title and the set of citing
     filenames
  5. Diffs against INDEX.md's Known References table
  6. For each new doc-id: generates a row with Missing Doc ID, Title,
     Expected Folder, Cited By
  7. --dry-run: prints proposed additions without writing
  8. Default: appends new rows to INDEX.md's Known References table
     (preserving alphabetical order by doc-id)

WHEN NOT TO USE:
  - To add refs that aren't cited by any converted doc yet (manual INDEX
    edit; sync only promotes observed unresolved refs)
  - To remove rows (manual edit — a doc arriving in source/ triggers a
    Gap C info message from validate --index, not auto-removal)
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
  8. Adopt a DHF formal doc into round-trippable working MD

Enter a number (1-8):
```

Based on response:
- **1** → Recommend `/docflow convert <doc-id>` or `/docflow batch <category>`. Ask if they know the doc-id.
- **2** → Recommend `/docflow export <file>`. Note: Phase 2, not yet implemented.
- **3** → Recommend `/docflow import <file>`. Note: Phase 2, not yet implemented.
- **4** → Recommend `/docflow import <file> --comments` then `/docflow reconcile <file>`. Note: Phase 2.
- **5** → Recommend `/docflow refresh <doc-id>`.
- **6** → Recommend `/docflow validate <doc-id|file>`.
- **7** → Recommend `/docflow status`.
- **8** → Recommend `/docflow adopt <target>`. Ask if they want to adopt a single file, a whole DHF, or a scoped area; recommend `--plan` first to dry-run.

### `convert <doc-id>`

Convert a single source document to markdown.

0. **Preflight — INDEX freshness** (see `validate --index` for the full algorithm): enumerate doc-ids from `docs/internal/source/**/*.{pdf,docx,doc,xlsx}` and from `docs/internal/source/INDEX.md`. If any source doc-id is missing from INDEX.md's functional tables AND not listed under the `## Known References — Not Yet in Source` section, **warn** the user with the unindexed list and ask whether to proceed or abort so they can refresh INDEX.md first. Do not block — this is a warning, not an error. Cross-reference resolution quality degrades with each unindexed doc, so the user needs to know.

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

0. **Preflight — INDEX freshness**: run the same check as `convert` step 0. Because `batch` reads category membership from INDEX.md, an unindexed doc will be **silently excluded** from the batch — this is a stronger failure mode than in `convert`, so surface the gap more prominently:
   - If unindexed docs exist in the relevant category's source folders, report the count and filenames, then ask whether to (a) refresh INDEX.md first, (b) proceed with the partial batch, or (c) abort.
   - Also run the duplicate-file check on Work Instructions — if any `(1)`/`(2)` suffixed duplicates exist for the same doc-id (see `source/Work Instructions/README.md`), report and ask whether to proceed (the converter will convert each duplicate as a separate file, producing wasteful duplicate source-md).

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

### `adopt <target> [flags]`

Adopt DHF formal document(s) into round-trippable working markdown. Unlike `convert` (one-way reference conversion of QMS source docs), adopted MD becomes the **authoring source of truth** — the file the team edits. `/docflow export` (Phase 2) round-trips it back to formal.

**Flags recognized**: `--plan`, `--refresh <file>`, `--force`, `--no-rename`, `--area <path>`

0. **Preflight**:
   - Target must either resolve to a single file under `docs/project/dhfs/<dhf>/**/formal/`, OR be a DHF leaf name matching `project.yml` `dhfs[]`.
   - Verify `docs/internal/source-md/Forms/` and `docs/internal/source-md/SOPs/` exist (required for template + SOP inference). If missing or empty, warn but do not block — inference will return null candidates.
   - **Collision check**: for each formal file, if both `<stem>.ext` AND `<stem>-v{N}.ext` exist in the same folder → error, instruct user to manually resolve before re-running. Auto-resolution here silently loses content; we require explicit intent.
   - If `--plan`, compute the action list and report without writing.

1. **Resolve target**:
   - **Single file** (absolute or relative path to a formal file) → one adoption job. Infer the DHF by walking up the path until a `project.yml` `dhfs[].path` match is found. Infer DHF_AREA from path segments between the DHF root and `formal/`.
   - **DHF name** (e.g. `hiplink-mgmt-services`) → enumerate every file under `docs/project/dhfs/<dhf>/**/formal/` matching `{pdf,docx,doc,xlsx,pptx}`. Exclude patterns: `c-arm-simulator-main/**` (source code), `HLCAS-TC-*` + `*.dcm` + pure-evidence screenshots (runtime evidence, not documentation).
   - **DHF + `--area <path>`** → scope to `docs/project/dhfs/<dhf>/<area>/formal/`.

2. **Per-file adoption** (for each resolved file):

   **2a. Spawn adopter agent** — the agent does all extraction, rename, conversion, and validation:
   - Spawn an Agent with `agents/adopter.md`, parameterized with: SOURCE_PATH (as-dropped), FORMAT, DHF, DHF_ROLE, DHF_AREA, DHF_AREA_DIR, STAGING_DIR, DOC_VERSION_OVERRIDE (if user passed `--doc-version`), FORMS_INDEX_PATH, SOPS_INDEX_PATH, WIS_INDEX_PATH, MANIFEST_PATHS, PROJECT_REFS_PATH.
   - The agent's Phase 0 extracts title + doc_version from the source document's content, detects adoption state (FRESH / IDEMPOTENT / OVERRIDE-MERGE / DOWNGRADE / TITLE-DRIFT), and derives output paths from the extracted title.
   - Up to 5 concurrent agents when processing a DHF-wide target. Serialize if `--plan` is set (no concurrency needed for dry run).

   **2b. Flag handling** (passed through to the agent):
   - `--force` → agent proceeds past IDEMPOTENT detection and re-adopts (overwrites working MD).
   - `--doc-version v<N>` → DOC_VERSION_OVERRIDE is set; agent skips version-extraction hierarchy and uses the flag value.
   - `--override` → agent enters override-merge mode when OVERRIDE-MERGE is detected (3-way merge; currently design-captured only — returns manual-instruction failure).
   - `--confirm-rename` → agent proceeds past TITLE-DRIFT detection and renames the working MD + formal to match the new extracted title.
   - `--plan` → skill runs agent in dry-run mode; agent extracts title+version, detects state, but does NOT rename, convert, or write. Reports what would happen.

   **2c. Validate + commit** (inside the agent):
   - The agent's Phase 7 self-validation runs. If Required checks fail, the agent leaves staging intact with `VALIDATION_FAILED.txt` and returns failure.
   - The agent's Phase 8 performs the transactional commit (git mv formal → title-based name, move images, move working MD, re-render parent README sentinels).

   **2d. Skill-side result handling**:
   - On agent success, working MD has landed at `<DHF_AREA_DIR>/<TITLE>.md` and formal at `formal/<TITLE>.<ext>`. Parent README sentinels re-rendered.
   - On agent failure: staging retained with diagnostic file. Collect into batch summary.

3. **Quality gate enforcement** (DHF-wide targets):
   - Track consecutive Required failures. If ≥ 3, stop and report — likely systemic issue (bad preflight, corrupted template index, etc.).
   - After 10+ files, if failure rate ≥ 30%, stop.
   - Warnings accumulate for the summary.

4. **Report**:

   ```
   Adopt: <target>

     Files adopted:       N
     Files skipped:       K (already adopted, or collision)
     Files failed:        F

     Low-confidence template_of:  [file — top-hint candidate(s)]
     Low-confidence authored_per: [file — SOP candidates]
     Missing template_of:         [file — no candidates]

     Formal renames (git mv):     [old → <Title>.<ext>, ...]
     Working MDs written:         [<Title>.md, ...]
     Parent READMEs re-rendered:  [path, ...]

     Override-merge detected:     [file — old→new doc_version] (Phase 2 — not yet implemented)
     Version extraction failed:   [file — VERSION_NOT_FOUND.txt in staging]
   ```

   Exit non-zero if any file failed, matching `batch` semantics.

5. **Post-run suggestions** (always):
   - If any low-confidence inference surfaced: "Review the adopted files and resolve `template_of`/`authored_per` manually where flagged."
   - If any file was renamed (dropped-in file with non-title name): "Inspect the git mv diff and commit the rename together with the adopted MD."
   - If version extraction failed on any file: "Re-run with `--doc-version vNN <file>` to provide the version explicitly, or annotate the source with a revision marker."
   - If `filings: []` for adopted files: "These docs are not referenced in any composition manifest — run `/docflow validate --orphans` to enumerate."

### `review <target> [flags]`

Validate an adopted working MD against its source document. Complements `adopt` — where `adopt` produces the MD, `review` verifies it stayed faithful. Useful after any adopt run, after a spec update that might surface new regressions in existing adopted docs, or before committing a working MD for the first time.

**Flags**:
- `--fix` — apply non-ambiguous corrections directly to the MD; flag ambiguous cases with `%% REVIEW:` comments. Default is report-only.
- `--mermaid-only` — scope to Mermaid blocks (skip frontmatter, refs, content fidelity audits)
- `--scope <full|mermaid-only>` — same as `--mermaid-only` but explicit

**Target forms**:
- `/docflow review <file>` — single working MD
- `/docflow review <dhf>` — every adopted working MD in a DHF (walks `docs/project/dhfs/<dhf>/**/*.md` that carry `dhf:` frontmatter)
- `/docflow review <dhf> --area <path>` — scope to a sub-area

0. **Preflight**:
   - Resolve target to one or more working MDs.
   - Verify each target is an adopted doc (has frontmatter with `dhf:` and `source_formal:`). Skip anything that isn't.
   - Verify `source_formal` path resolves to an existing formal file.

1. **Spawn reviewer agent** per file (`agents/reviewer.md`), parameterized with:
   - WORKING_MD_PATH
   - FORMAL_PATH (resolved from frontmatter `source_formal`)
   - DHF_AREA_DIR (parent folder of the MD)
   - MODE (`report` default, `fix` if `--fix` flag)
   - SCOPE (`full` default, `mermaid-only` if flag present)
   - CONVERTER_SPEC_PATH (`.claude/skills/docflow/agents/converter.md`)

2. **The agent performs** (see `agents/reviewer.md`): inventory → source pairing → per-Mermaid audit (opens each image, classifies per F11a, enumerates source structure, diffs against emitted Mermaid, records discrepancies per category) → non-Mermaid audits (frontmatter, refs, content fidelity, image integrity) → correct-or-flag → report.

3. **Report back** per file:

   ```
   Review: <Title>.md

     Mermaid blocks reviewed: N
       ✓ Figure 1 (K/K edges verified)
       ⚠ Figure 3 — 2 discrepancies:
           - [FIX] Events moved inside VPC subgraph
           - [FIX] Removed invented label "API layer (outside VPC)"

     Non-Mermaid audits (if --scope full):
       ✓ Frontmatter complete
       ⚠ Cross-refs: 1 unresolved without note (flagged)

     Corrections applied: K (--fix mode)
     Flagged for human review: F (%% REVIEW: comments in MD)

     Overall: PASS | <N issues requiring attention>
   ```

4. **DHF-wide runs**: collect per-file reports; produce an aggregate summary.

5. **When `--fix` applied changes**: recommend the user `git diff <file>` to inspect corrections before committing. Reviewer changes are auto-staged for review but not auto-committed.

**Ambiguity handling** — the reviewer emits `%% REVIEW: <category> — <description>` comments inline in the MD for cases where auto-correction is too risky:
- Classification ambiguity (is it a flow or a logical diagram?)
- Illegible source labels
- Containment boundary that's visually at the pixel edge
- Multiple-target decision branches where target is uncertain
- Structural rewrites that go beyond single-line edits

These are grep-friendly (`grep "%% REVIEW:"`) and dissolve when a human resolves them. A separate Best Practices check flags working MDs with outstanding `%% REVIEW:` comments.

**When to run `review`**:
- After every `/docflow adopt` — the "verify" step of the two-pass workflow
- When the F11 spec or frontmatter schema updates — re-review existing adoptions for new regressions
- Before `/tracker` aggregation — ensures the dashboard reflects verified state
- On a cadence (e.g., `/docflow review hiplink-mgmt-services` weekly) for drift detection

### `adopt` → `review` two-pass workflow

The recommended workflow is:

```
/docflow adopt <file>           # Best-effort conversion
/docflow review <file>          # Report discrepancies (report-only default)
/docflow review <file> --fix    # Apply non-ambiguous corrections
git diff                        # Inspect corrections
# Resolve any %% REVIEW: comments manually
```

Rationale: separation of concerns. Adopter focuses on extraction + inference + initial Mermaid. Reviewer focuses on validation against source. Simpler prompts for each agent; catches bug classes not yet enumerated in F11.

If argument is `--toolchain`, check CLI tool and Python dep availability:
- CLI: `which pandoc`, `which pdftotext`, `which pdfimages`, `which libreoffice`, `which unzip`
- Python: `python3 -c "import openpyxl"`, `python3 -c "import yaml"`, `python3 -c "import PIL"`
- Pillow (PIL) is required for F1 orientation correction on PDF-extracted images — conversions will hit upside-down diagrams without it
- openpyxl + pyyaml are required for XLSX reads
Report which are available and which are missing with install instructions (see REQUIREMENTS block in help).

If argument is `--index`, verify the source-catalog (`source/INDEX.md`) and the QMS reference graph (`docs/internal/qms-reference-graph.md`) together cover every doc-id in `source/`. **Algorithm**:

1. **Collect functional-catalog doc-ids**: parse `docs/internal/source/INDEX.md` (everything before the `## Known References — Not Yet in Source` pointer section). Match all `FORM-\d+ | SOP-\d+ | POL-\d+ | WI-\d+ | QSD-\d+` tokens in functional tables. These are the "present in source/" claims.
2. **Collect Known-References doc-ids**: parse `docs/internal/qms-reference-graph.md` (or legacy `source/INDEX.md` if the split hasn't happened yet) — find the `## Known References — Not Yet in Source` section and match doc-ids using a **column-aware** pattern (doc-ids ONLY in the first column of each table row: `^\|\s*(FORM-\d+|…)\s*\|` per line). **Do not grep the whole section** — the Title and Cited-By columns contain prose that may reference other doc-ids; those are NOT known-absences.
3. **Collect Known-Reference titles + domain + scope**: for each first-column match, also capture columns 2 (Title), 3 (Domain), 4 (HipLink Scope). A Known Reference row with a blank/placeholder title (`_(unknown…)_` or empty) warns — the converter should have captured a title in its frontmatter `references:` block. A row with `review` scope warns too — manual classification needed.
4. **Collect source doc-ids**: enumerate `docs/internal/source/**/*.{pdf,docx,doc,xlsx}`, strip leading doc-id from each filename.
5. **Diff**:
   - `source - INDEX_functional - Known_Refs` → **Gap A (ERROR)**: files in source/ that INDEX.md does not mention anywhere. INDEX is stale — user must add entries to the appropriate functional category.
   - `INDEX_functional - source - Known_Refs` → **Gap B (ERROR)**: functional-category entries that point to a file that no longer exists in source/ and is not explicitly tracked as a known reference. Either the file was removed (INDEX needs cleanup) or it should be moved to Known References.
   - `Known_Refs ∩ source` → **Gap C (INFO)**: a doc listed as "not yet in source/" has been exported — user should remove the row from Known References and add it to a functional table.
   - Known-Reference rows with blank titles → **Warning**: run `/docflow sync-known-refs` to auto-populate from converter output, or edit manually.
6. **Duplicate-file check**: for each `doc-id`, if multiple files match the doc-id prefix in source/, report as **Warning** (see `source/Work Instructions/README.md` duplicate-file mapping). These duplicate files are re-downloads, not separate documents.

If argument is `--readmes`, verify READMEs reference current project-layer artifacts. **Algorithm**:

1. **Project-layer artifacts** — the set of authoritative file paths READMEs must reference correctly:
   - `docs/internal/source/INDEX.md` (source functional catalog)
   - `docs/internal/qms-reference-graph.md` (QMS reference graph)
   - Any file matching `docs/internal/*.md` that is not a README (future: `deliverable-registry.md`, `obligations-index.md`, etc.)
   - `docs/internal/source/*/README.md` (subfolder READMEs)

2. **Walk all READMEs** under `docs/internal/` (recursively) and `docs/project/` (future, for DHF READMEs consuming grounding-layer files).

3. **Extract link targets** — for each README, parse markdown `[text](path)` links and bare-path prose mentions (e.g., `` `docs/internal/qms-reference-graph.md` ``). Resolve relative paths.

4. **Diff**:
   - **Dead link**: a README references a path that no longer exists → **ERROR**
   - **Stale reference**: a README mentions INDEX.md's old behavior (e.g., "Known References table") when that content has moved → **Warning** (detect by searching for known-moved headings inside READMEs that shouldn't own them)
   - **Missing pointer**: a README in a folder that sits alongside a project-layer artifact doesn't mention it → **Recommended** (e.g., `docs/internal/source/` README should mention `../qms-reference-graph.md`)

5. **Report**: list dead links, stale references, missing pointers with file:line citations. Suggest fixes.

### `convert`, `batch`, `sync-known-refs` — README-currency obligation

**When a docflow action causes a structural change that moves, splits, or renames a project-layer artifact, the action is NOT complete until READMEs that reference the old location have been swept for updates.**

Structural changes that trigger a README sweep:
- Splitting one project-layer file into multiple (e.g., v13 split of Known References out of INDEX.md)
- Moving a project-layer artifact between folders (e.g., promoting a file from `source/` to `docs/internal/`)
- Renaming a project-layer file
- Adding a new project-layer artifact that should be linked from its folder's README (e.g., when `deliverable-registry.md` lands, `docs/internal/README.md` must link to it)

Workflow for a structural change:
1. Complete the structural change (create/move/split files)
2. Run `/docflow validate --readmes` to enumerate affected READMEs
3. Update each affected README to reference the new location / mention the new artifact
4. Re-run `/docflow validate --readmes` to confirm clean
5. Only then consider the structural change committed

This is a hard expectation, not a suggestion — stale READMEs silently route future Claude work to wrong files, which is exactly the kind of drift the project was set up to prevent.

Report:
```
Index check:
  INDEX.md entries:        N
  source/ unique doc-ids:  M
  Known References:        K

  Gap A — in source/, missing from INDEX:        [list, or "none"]
  Gap B — in INDEX, missing from source/:        [list, or "none"]
  Gap C — Known Reference now in source/:        [list, or "none"]
  Duplicate files in source/:                    [list, or "none"]

  Overall: PASS / FAIL — N unindexed doc(s) / K duplicate pair(s)
```

Exit non-zero on Gap A or Gap B to signal failure to calling scripts. The `convert` and `batch` actions run this algorithm as a preflight (warning-only).

### `sync-known-refs`

Harvest unresolved cross-references from converted source-md files and merge new entries into INDEX.md's `## Known References — Not Yet in Source` table, with titles extracted from the citing docs' frontmatter `references:` blocks.

**Algorithm**:

1. **Walk converted files**: enumerate every `.md` file under `docs/internal/source-md/` except `README.md`.
2. **Parse frontmatter**: extract each file's YAML frontmatter block; locate the `references:` list.
3. **Extract ref items**: each item has `doc_id`, optional `title`, `resolved`, `match`, `note`. Accept items where `resolved: false` or `resolved:` is absent.
4. **Filter to genuinely-new refs**:
   - Skip items whose `doc_id` matches any source/ file (means the ref is resolvable — probably a converter bug to fix).
   - Skip items whose `doc_id` is already in INDEX.md functional tables.
   - Skip items whose `doc_id` is already listed in Known References.
   - Skip items with `doc_id: null` (external standards like ISO/IEC).
5. **Aggregate by doc-id**: for each new doc-id, collect the first non-null title and the set of citing filenames (strip `.md` to get human-readable doc names).
6. **Infer Expected Folder** from the doc-id prefix:
   - `FORM-` → `Forms/`
   - `SOP-` → `SOPs/`
   - `POL-` → `Policies/`
   - `WI-` → `Work Instructions/`
   - `QSD-` → `Standards/`
7. **Generate rows**: `| {doc-id} | {title or "_(cited without title)_"} | {folder} | {citing docs joined with ", "} |`
8. **Merge into INDEX.md**: insert new rows into the Known References table, keeping the table sorted alphabetically by doc-id. Preserve the table's existing rows and column headers.
9. **Report**: print count of new rows added, list of doc-ids added, and any refs that were skipped (with reason).

**Flags**:
- `--dry-run`: print proposed additions, don't write.

**Integration**: run this after every `/docflow batch` completes. The preflight in `convert`/`batch` will warn if this table is out of sync relative to converted docs.

### Known References table schema (v12 — Domain + Scope)

The Known References table has six columns:

| Column | Source | Purpose |
|--------|--------|---------|
| Missing Doc ID | doc-id cited by a converted source-md, not in source/ or INDEX functional tables | Primary key |
| Title | Converter-written frontmatter `references: - title:` | Human-readable identification |
| Domain | Classified from Title by keyword heuristics | Shared with `/advisors` + `/dhf-builder` — tells us which persona/topic owns this doc |
| HipLink Scope | Derived from Domain + project `device_type` | Tells the team whether to request this doc from QMS |
| Expected Folder | Inferred from doc-id prefix | Where the PDF lands if exported |
| Cited By | Aggregated from frontmatter across all converted files | Traceability |

**Domain values** (also used by `/advisors` persona source scoping):

| Domain | Description | Persona / topic |
|--------|-------------|-----------------|
| `software-lifecycle` | SDLC, coding, version control, SW V&V | software-lifecycle |
| `cybersecurity` | Threat modeling, product security, SPDF | cybersecurity |
| `risk-management` | ISO 14971, dFMEA, PHA, hazard analysis | risk-management |
| `design-controls` | D&D plan, phase gates, design reviews, DHF | design-controls |
| `regulatory` | 510(k), submissions, indications, labeling compliance | regulatory |
| `clinical` | CER, clinical evaluation | clinical |
| `post-market` | PMS, PSUR, complaints, CAPA, event risk | post-market |
| `human-factors` | Usability engineering, HFUE | human-factors |
| `labeling-udi` | Labeling, UDI, GUDID | regulatory (sub-topic) |
| `quality-system` | Doc control, training, audit, deviation, change control, management review | quality-engineering |
| `supplier` | Supplier evaluation, SCR | quality-engineering (sub-topic) |
| `it-data` | IT, data protection, information security | cybersecurity (sub-topic) |
| `product-realization` | DMR, MDF, product initiation | design-controls (sub-topic) |
| `manufacturing` | Cleanroom, packaging, sterilization, calibration, environmental monitoring | manufacturing — **out-of-scope for SaMD** |
| `manufacturing-inspection` | Inspection, test status, measurement equipment | manufacturing — **out-of-scope for SaMD** |
| `unknown` | No title captured — needs manual | review |

**HipLink Scope values**:
- `needed` — Domain ∈ {software-lifecycle, cybersecurity, risk-management, design-controls, regulatory, clinical, post-market, human-factors, labeling-udi}
- `indirect` — Domain ∈ {quality-system, supplier, it-data, product-realization}
- `not-needed` — Domain ∈ {manufacturing, manufacturing-inspection} — **don't request from QMS unless program scope expands to hardware**
- `review` — needs manual classification (unknown domain or ambiguous)

**Project scope configuration**: the mapping from Domain → Scope is **device-type-specific**. A SaMD project treats manufacturing as out-of-scope; a hardware-device project would treat manufacturing as needed. `/docflow sync-known-refs` reads `project.yml` `project.device_type` (e.g., `SaMD`, `hardware`, `combination`) to pick the right mapping. Default is `SaMD`.

**`sync-known-refs` auto-classification rules** (applied in order, first match wins):

```
software-lifecycle:       /software|sdlc|haa|coding|git|programming/
cybersecurity:            /security|cyber|threat model|spdf/
human-factors:            /human factors|usability|hfue|hf.?ue/
labeling-udi:             /\blabel|\budi\b|gudid|direct mark/
clinical:                 /clinical/
post-market:              /post.?market|pms|psur|surveillance|complaint|capa|post.?production|event handling|event risk|service risk/
regulatory:               /510|regulatory|submission|memo.?to.?file|market access|clearance|indication expansion|essential requirement|general safety.*performance|gspr|product release/
manufacturing:            /cleanroom|gownroom|clean.?procedure|packaging|steriliz|calibration|environmental monitoring|work environment|hygiene|classifying environment|design to manufacturing|process failure mode|pfmea/
manufacturing-inspection: /inspection|in.?process|final document review|test status|measurement equipment|gauges/
design-controls:          /design (control|release|review|phase|history|output|input|traceability|plan|planning|verification|validation)|technical review|dhf|eDHF|d&d/
risk-management:          /risk management|fmea|hazard analysis|master harms|harms list|residual risk|benefit.?risk|iso 14971/
supplier:                 /supplier|scr|approved suppliers|sub.?supplier/
quality-system:           /deviation|change control|change order|document control|training|audit|biocompatib|validation master|computer system assurance|management of change|emoc|management review|nonconformance|statistical techniques|validation sampling|quality data|quality plan|external document|qms gap|act number|number system/
it-data:                  /it |information security|data governance|data protection|enterprise systems|acceptable use|it change/
product-realization:      /device history|device master|dmr|mdf|product realization|product initi/
unknown:                  /^$|^_\(unknown/   (no other match)
```

User-override is stable: once a row has a non-default Domain or Scope value, `sync-known-refs` does not overwrite it on subsequent runs. Only new rows get auto-classification; existing classifications are preserved.

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

### Source-MD Folder Structure

The `source-md/` directory mirrors `source/` folder structure exactly. Converted files go into the subfolder matching their document type:

```
source/                              source-md/
├── Forms/                           ├── Forms/
│   └── FORM-000137230 - D&D.docx   │   └── FORM-000137230 - D&D.md
├── SOPs/                            ├── SOPs/
│   └── SOP-000326588 - User...pdf   │   └── SOP-000326588 - User...md
├── Policies/                        ├── Policies/
├── Work Instructions/               ├── Work Instructions/
├── Standards/                       ├── Standards/
└── INDEX.md                         ├── images/     (shared across subfolders)
                                     └── .staging/   (gitignored)
```

| DOC_TYPE | Source Folder | Output Subfolder |
|----------|--------------|-----------------|
| FORM | `source/Forms/` | `source-md/Forms/` |
| SOP | `source/SOPs/` | `source-md/SOPs/` |
| POL | `source/Policies/` | `source-md/Policies/` |
| WI | `source/Work Instructions/` | `source-md/Work Instructions/` |
| QSD | `source/Standards/` | `source-md/Standards/` |

The `convert` action resolves the correct subfolder from the doc-id prefix and passes it as `OUTPUT_DIR` to the converter agent.

### Adopted Working-MD Placement (`/docflow adopt`)

Working MD produced by `/docflow adopt` sits **alongside** the formal file it was adopted from, inside the DHF folder tree (not in `docs/internal/source-md/`).

```
docs/project/dhfs/<dhf>/<dhf-area>/
├── <Title>.md                           # working MD (adopted; draft lifecycle)
├── formal/
│   └── <Title>.<ext>                    # current formal (title-based filename, no version suffix)
├── images/
│   └── <title-kebab>_<descriptor>.png
└── README.md                            # its ## Structure sentinel is re-rendered
```

**Filename convention**:
- Filenames carry NO version suffix and NO `- Draft` marker. Working = `<Title>.md`. Current formal = `formal/<Title>.<ext>`.
- **Exactly one current formal per title**. Prior versions live in git history (`git log --follow -- formal/<Title>.<ext>`). The filesystem reflects current state only.
- Title is extracted from the document's CONTENT (cover page → PDF metadata → body H1 → cleaned filename), not from the source filename pattern. See `templates/frontmatter-project.md` "Title extraction hierarchy".
- Lifecycle signal: folder location (`formal/` vs working area) + frontmatter `lifecycle: draft` field. No filename marker needed.

**Version lives in metadata, not filenames**:
- `doc_version` in frontmatter (e.g. `"v30"`) — extracted from the source document's revision history / cover page / metadata at adopt time.
- `version_lineage[]` — audit trail of format transitions. Never truncated.
- Git history — byte-level record of prior formals.

**Image path prefix**: `images/` (sibling folder, not `../images/`).

**Content exclusions**: adopt skips non-document files — source code trees (`c-arm-simulator-main/**`), DICOM runtime evidence, pure-evidence screenshots.

### When a New Formal Drops (override-merge)

When someone drops a newer version of a formal already under adoption (e.g. a v31 export of a doc currently adopted at v30), `/docflow adopt --override` performs a **3-way merge** between:

- the prior formal (still on disk before override, re-converted to MD as "base")
- the current working MD with author edits ("draft")
- the new formal dropped by the user ("new")

The merge is **section-aware** (H2/H3 boundaries). Sections changed by only one side are auto-applied. Sections changed by both sides emit CONFLICT markers for the author to resolve manually.

Filenames don't change across a version override — `<Title>.<ext>` is stable. Old formal content is preserved in git history (`git show HEAD~1:formal/<Title>.<ext>`).

**Implementation status**: the merge workflow is **design-captured but not yet implemented** in `agents/adopter.md`. Today, an override-merge detection returns a manual-instruction failure. Full implementation lands when a real upgrade scenario needs to be exercised.

### Source-MD Filename Convention

Source-md filenames **must match** the source filename exactly, with only the extension changed:
- Source: `Forms/FORM-000137230 - Design and Development Plan.docx`
- Source-md: `Forms/FORM-000137230 - Design and Development Plan.md`

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

| Check | How to Verify | Severity | Scope |
|-------|--------------|----------|-------|
| Docflow skill installed | `.claude/skills/docflow/SKILL.md` exists | Required | shared |
| Source-md directory exists | `docs/internal/source-md/` exists | Required | shared |
| Images directory exists | `docs/internal/source-md/images/` exists | Required | shared |
| Staging gitignored | `.gitignore` contains `source-md/.staging/` | Required | shared |
| Toolchain available | `pandoc`, `pdftotext`, `pdfimages` are on PATH | Required | shared |
| No orphaned staging | `docs/internal/source-md/.staging/` is empty | Recommended | shared |
| INDEX.md exists | `docs/internal/source/INDEX.md` exists (needed for cross-ref resolution) | Required | shared |
| INDEX.md covers source/ inventory | Every doc-id in `docs/internal/source/**/*.{pdf,docx,doc,xlsx}` appears in INDEX.md (functional table OR `Known References — Not Yet in Source` section). Run `/docflow validate --index`. | Required | shared |
| No duplicate source files | No two files under `docs/internal/source/` share the same doc-id prefix. Run `/docflow validate --index` (also reports duplicates). | Recommended | shared |
| Source subfolders have README | `source/{Forms,SOPs,Policies,Work Instructions,Standards}/README.md` each exist | Required | shared |
| Known References have titles | Every row in `qms-reference-graph.md`'s Known References table populates the Title column. Run `/docflow sync-known-refs` to auto-populate from converted file frontmatter. | Recommended | shared |
| Known References have Domain + Scope | Every row in `qms-reference-graph.md` populates Domain and HipLink Scope (no `review` / no blank). Run `/docflow sync-known-refs`; manually override rows that the auto-classifier can't disambiguate. | Recommended | shared |
| READMEs reference current project-layer paths | Every README under `docs/internal/` references project-layer artifacts (INDEX.md, qms-reference-graph.md, future deliverable-registry.md / obligations-index.md / template-schemas/) at their current path. No dead links, no stale references to moved content. Run `/docflow validate --readmes`. | Required | shared |
| Structural changes sweep READMEs in the same commit | When a docflow action splits, moves, or renames a project-layer artifact, every README that references the old location must be updated in the same commit as the change. Verified indirectly via the dead-link check above — if `validate --readmes` passes after a structural change, the sweep was done. | Required | shared |
| Adopted files use title-based filenames (no version suffix) | Every file under `docs/project/dhfs/<dhf>/**/formal/` AND every adopted `.md` in its sibling folder matches `<Title>.<ext>` pattern. No `-v\d+` suffix in filenames — versioning lives in frontmatter + git history. | Required | shared |
| Adopted working MDs have resolvable source_formal + target_formal | Every `.md` under `docs/project/dhfs/<dhf>/` with `dhf:` in frontmatter has `source_formal` resolving to an existing file and `target_formal` parent folder existing. | Required | shared |
| Adopted working MDs have doc_version populated | Every adopted working MD has a non-null `doc_version` matching `^v\d+$` (normalized form). Null values indicate Phase 0 extraction failure that was silently accepted. | Required | shared |
| Adopted working MDs have template_of populated or flagged | Every adopted working MD has either a non-null `template_of.doc_id` with `confidence`, OR a `notes:` entry explicitly marking the inference as incomplete. No silent nulls. | Recommended | shared |
| Exactly one current formal per title | For each `<Title>.md` in a DHF area, exactly one `formal/<Title>.<ext>` exists (not zero, not multiple). Multiple indicates version-suffix leftovers from old convention; zero indicates an orphan working MD. | Required | shared |
| Adopted working MDs have been reviewed | Every adopted working MD has been through `/docflow review` at least once (or carries `%% REVIEW:` comments that have been resolved). For docs with Mermaid blocks, review is the two-pass complement to adopt; skipping it means discrepancies between Mermaid and source may ship unchecked. | Recommended | shared |
| No outstanding `%% REVIEW:` comments | Adopted working MDs do not contain unresolved `%% REVIEW: <category>` comments. These are placeholders the reviewer emitted for human resolution; unresolved ones indicate the working MD is not yet ready for review-gate sign-off. Grep: `grep -rn '%% REVIEW:' docs/project/dhfs/`. | Recommended | shared |
| PreToolUse Bash tripwire installed | `.claude/hooks/block-direct-conversion.sh` exists as a symlink to `.claude/skills/docflow/hooks/block-direct-conversion.sh` AND `.claude/settings.json` registers it under `hooks.PreToolUse[].matcher == "Bash"`. Without this hook, direct pandoc/unzip/soffice calls against office documents silently bypass `/docflow`. Run `/docflow setup` to install. | Required | shared |
| Tripwire hook is symlink, not copy | `.claude/hooks/block-direct-conversion.sh` is a symlink (not a copy). Same rationale as other skill-owned hooks — `/sync-skills pull` updates the source, and copies drift. Run `/docflow setup` to fix if drifted. | Required | shared |

## Notes

- If `$ARGUMENTS` is empty or just "help", show the full help overview
- The `convert` and `refresh` actions spawn agents from `${CLAUDE_SKILL_DIR}/agents/`
- Phase 2 actions (export, import, reconcile) are defined but not yet implemented
- LibreOffice is required only for `.doc` files (16 of 127). All other formats work without it
- The staging area is never committed to git

## Changelog

- 27 (2026-04-20): **Relocate bypass marker + setup state dir from `.claude/state/docflow-active` to `.state/docflow-active`** (task ben/083). Claude Code's built-in sensitive-file guard prompts on every Bash-initiated touch/rm against `.claude/**` regardless of `settings.json` allow rules. Moving the marker OUT of `.claude/` is the only durable escape. Updated: `hooks/block-direct-conversion.sh` BYPASS_MARKER path + help-text override instructions; `SKILL.md` setup action step 3 (create `.state/` instead of `.claude/state/`) + step 7 gitignore check + bypass mechanics section; all 4 agent prompts (`converter.md`, `adopter.md`, `refresher.md`, `reviewer.md`) Phase 0.0 `touch`/`rm` commands now target `$CLAUDE_PROJECT_DIR/.state/docflow-active`. Historical changelog entries (v24 bypass-marker intro, v23 tripwire intro) preserved.
  **Post-update:** The hook is installed via symlink — v27 activates on next tool call after pulling. No setup re-run required. If a project has an in-flight `/docflow` run with the old marker at `.claude/state/docflow-active`, migrate it via `mv .claude/state/docflow-active .state/docflow-active` (or just `rm .claude/state/docflow-active` — the SessionEnd cleanup will remove it anyway). The `session-cleanup.sh` belt-and-suspenders cleanup already targets `.state/docflow-active` as of task-skill v18.
- 26 (2026-04-20): **Hook regex tightening — shell-aware tokenization via python3 shlex, eliminating prose-in-quoted-arg false positives.** The v23 tripwire matched conversion verbs + office-doc extensions anywhere in the command string, so `gh pr create --body "prose mentioning pandoc ... .docx"`, `git commit -m "docflow changes for foo.docx"`, and `grep pandoc file.docx` all tripped the hook on their first invocation. v24's Bash-level sed splitter was worse — it split on `|` even inside quoted strings, breaking `VERBS='pandoc|soffice|…'` string literals into separate "statements" and then firing on each verb as if it were a command. v26 rewrites `hooks/block-direct-conversion.sh` to call out to `python3 -c` with `shlex` for proper shell tokenization: operators like `;|&&|\|\|` only split chunks when they appear OUTSIDE quoted strings. Verbs and file extensions that appear INSIDE a quoted argument to some OTHER command (gh pr bodies, commit messages, grep patterns, echo literals) are no longer matched because they never become the first token of their own chunk. Test suite expanded to 18 cases covering 7 intended denies + 11 previously-tripping allows; all pass. Known-and-documented bypass surfaces (`bash -c "pandoc foo.docx"`, `find ... -exec pandoc {}`) remain ALLOW — matching user intent that the hook catches casual drift, not a determined bypass.
  **Post-update:** if a project already has `.claude/hooks/block-direct-conversion.sh` symlinked from v23/v24, nothing to do — the symlink points at the skill source and picks up v26 on next tool call. If a project had disabled the hook because of false-positives (by removing the registration or emptying the script), run `/docflow setup` to re-register, and the v26 logic is immediately active.
- 25 (2026-04-20): **T1 composite-table faithfulness rule + mandatory LibreOffice probe + reviewer T1-CHECK and PAGE-PROBE audits.** Surfaced by the HipLink RMP adopt review: the 8×8 composite risk matrix (legend in top-left corner via `gridSpan=3` + matrix body) was split into two separate MD tables AND the legend cells were backfilled with invented ISO-14971-flavored prose ("Risk is acceptable as-is; no further risk control action required") that appears nowhere in the source DOCX. Separately, the agent skipped pagination markers entirely, claiming LibreOffice was unavailable — without running `command -v soffice`, which would have returned `/usr/bin/soffice` (the project's `setup.sh` installs LibreOffice on Linux / WSL / macOS by default). Two root-cause fixes: (1) **`converter.md` Phase 3 — new rule T1** requires probing `gridSpan` + `vMerge` before emitting any non-trivial source table, preserving composites as a single HTML table with `colspan`/`rowspan` mirroring the source, and FORBIDS inventing cell text — every `<td>` text must be a verbatim substring of a source `<w:t>` value. Rationale quotes the RMP incident specifically. (2) **`converter.md` Phase 4.9** rewrites the LibreOffice toolchain detection as MANDATORY: the agent MUST run the `command -v` probe explicitly and report one of three exact labels (`pagination: F15 (rendered)` / `pagination: F14 (author-intended)` / `pagination: skipped (<reason with probe verbatim>)`) in Phase 7 notes — a bare "skipped" with no rationale is a Phase 7 failure. (3) **`reviewer.md` Phase 4** gains two audits: `T1-CHECK` (walks every emitted `<table>` against the source `<w:tbl>`, flags `T1-INVENTED-TEXT` with high-confidence autofix + `T1-COMPOSITE-SPLIT` as `%% REVIEW:`-flagged) and `PAGE-PROBE` (if MD has no page markers, probes LibreOffice in the reviewer's shell and flags `PAGE-PROBE-SKIPPED` as Required when LibreOffice is installed + source DOCX has ≥3 rendered pages). Applied to the HipLink RMP adopted MD: replaced the two separate tables with a single composite `<table>` using `colspan=3` (Acceptable/Conditional/Unacceptable legend spanning cols 1–3 of rows 1–3) + `rowspan=5` (vertical "Probability of Occurrence of Harm" axis label), stripped the invented tier-description prose, cited POL-000100241 / SOP-000100242 for operational definitions in surrounding caption instead. Inserted 4 page markers (pages 1/4/5/6 → next) via F15 (soffice --headless --convert-to pdf + pdftotext `\f` split, 7 rendered pages); pages 2→3 and 3→4 fall inside Section 5 device-description tables and are documented with an HTML-comment skip note per Phase 4.9 "don't fragment tables" rule.
  **Post-update:** (a) existing adopted working MDs are NOT auto-audited — run `/docflow review <file>` (or `/docflow review <dhf>`) to surface T1 violations in previously-adopted docs. Every doc adopted pre-v25 that contained a colored/composite table or a DOCX ≥ 3 rendered pages is a candidate. (b) Adopter behavior change on next `/docflow adopt` run: agent will probe LibreOffice explicitly and emit composite tables as single `<table>` with `colspan`/`rowspan` — no code migration needed, just re-adopt where the MD is known-wrong. (c) `SPEC-ROLL-FORWARD` path (adopter Phase 0.4) handles the v24 → v25 bump as a "rewrite tables + pagination only" pass when `doc_version` is unchanged.
- 24 (2026-04-20): **Bypass marker protocol wired into all four agents.** Follow-up to v23's tripwire — without this, `/docflow`'s own agents would self-block on their first pandoc/pdftotext/unzip/libreoffice call. v24 adds a mandatory **Phase 0.0 — Bypass marker protocol** section at the top of each agent prompt: `touch "$CLAUDE_PROJECT_DIR/.state/docflow-active"` before any gated conversion call (first action of the run for converter/refresher/adopter; before Phase 1 source-loading for reviewer, skipped entirely in lite-mode), `rm -f` the marker as the final action — success OR failure. `agents/adopter.md` additionally documents the IDEMPOTENT short-circuit path (no touch needed if no conversion runs) and the batch-run optimization (leave marker in place across multiple adopts in one `/docflow adopt <dhf>` sweep; remove once when batch completes). `agents/reviewer.md` notes lite-mode skips the protocol entirely (no Bash-gated reads). `scripts/extract_images.sh` is unaffected — the hook only gates Bash calls Claude issues directly, not subprocess calls inside scripts. Belt-and-suspenders: `.claude/skills/task/hooks/session-cleanup.sh` now unconditionally `rm -f`'s `.state/docflow-active` on SessionEnd so crashed agents don't leave the marker behind across sessions.
  **Post-update:** If you pulled v23 and ran `/docflow setup`, pull v24 and take no further action — the marker protocol activates on the next `/docflow convert|refresh|adopt|review` run, and the session-cleanup hook is already installed via symlink. If you have v22-or-earlier adopted working MDs already, no re-adopt is needed; the marker protocol is a runtime safety wrap, not a content change.
- 23 (2026-04-20): **Entry enforcement — PreToolUse Bash tripwire + broadened description + `setup` action.** Surfaced via live bypass: asked to convert the HipLink Risk Management Plan DOCX, Claude went straight to raw `pandoc` + `unzip` + XML introspection instead of routing through `/docflow adopt`, silently losing the colored risk matrix semantics the skill would have preserved. Root cause was two-fold: (a) the `description:` frontmatter read as a reference blurb, not a trigger — phrasings like "convert this docx to md" / "test docflow on this file" / "adopt the risk management plan" didn't match; (b) even when the harness missed, there was nothing stopping direct pandoc/unzip calls. v23 adds: (1) **Broadened `description:`** — action verbs (convert, adopt, import, export, refresh, round-trip, "test docflow on"), explicit file extensions (.docx/.doc/.pdf/.xlsx/.pptx), explicit locations (docs/internal/source/, docs/project/dhfs/**/formal/), and an explicit statement that `/docflow` owns the pipeline. Makes the skill fire on natural conversion phrasing. (2) **New `hooks/block-direct-conversion.sh`** PreToolUse Bash hook — reads hook JSON, detects command-start invocation of `pandoc|libreoffice|soffice|pdftotext|pdfimages|pdftoppm|unzip|qpdf|pdftk` against a `.(docx?|xlsx?|pptx?|pdf)` target, denies with exit 2 + a message pointing to the correct `/docflow` action. Honors `.state/docflow-active` marker for legitimate bypass; allows inert calls (`--help`, `--version`, `--list-*`). (3) **New `setup` action** (also accepted as `init` for discoverability) — follows the skill-creator symlink convention: `.claude/hooks/block-direct-conversion.sh` → `../skills/docflow/hooks/block-direct-conversion.sh`; registers `PreToolUse "Bash"` via the shared `register-hook.sh`; auto-discovered by `/medtech-docs init` Step 5 alongside `/task setup` and `/secops setup`. (4) **Two new Best Practices checks** — tripwire installed (Required) + tripwire is a symlink, not copy (Required). Tested: 10 hook scenarios (deny pandoc-on-docx, deny unzip-on-docx, deny pdftotext-on-pdf, deny libreoffice-convert-docx; allow pandoc-on-md, allow pandoc --version, allow soffice --version, allow non-Bash tools, allow unrelated `ls *.docx`, honor bypass marker) — all pass.
  **Post-update:** Run `/docflow setup` to install the hook. Before this runs, direct pandoc/unzip/etc. calls against DOCX/PDF/XLSX continue to succeed silently, bypassing `/docflow`'s pipeline. After install, use `/docflow <action>` — or, for rare sanctioned bypass, `touch .state/docflow-active && ... && rm .state/docflow-active`. Existing `/docflow` action implementations that shell out to pandoc/unzip (convert, refresh, batch, adopt) need to wrap their calls in the touch/rm marker (or set it once at agent entry and clear on exit); tracked as follow-up on task 079.
- 22 (2026-04-21): **R1 detail table moves from markdown to inline HTML for explicit column widths + native nested tables.** v21.1 fixed clause-level readability inside detail-table cells, but two structural problems remained: (a) markdown-table column widths are content-driven and ungovernable — a multi-paragraph Criticality cell with rationale italic + CtX tags balloons the third column to ~50% of width, squeezing Value (the primary content) into a narrow ribbon; (b) markdown does not allow a nested `<table>` inside a `|...|` cell, so sub-tables (AFAI-3518 AC1 Patient/Correction Details, AFAI-3537 AC8 button-state matrix, AFAI-3536 AC2 Global Control panel) had to render as `·`-separated bullet rows that lose the column shape. v22 converts the **detail table only** (attributes table stays markdown — its 6 columns are short and uniform) to inline HTML `<table>` with: (i) `<colgroup>` setting `Field` 10% / `Value` 60% / `Criticality` 30% — Value gets the most width as the primary content; (ii) full multi-line markdown allowed inside each `<td>` (GFM blank-line-after-`<td>` enables markdown processing); (iii) **nested HTML `<table>` inside Value cells** for sub-table content — Patient Details, button-state matrices, Global Control panels render as actual tables with header rows and column borders, not collapsed bullet runs. Adopter Phase 5e step 7 emits the HTML shape; reviewer Phase 4 audits that the detail-table is `<table>`-form (markdown form → flag as v21.x leftover, auto-fix is a one-time conversion). Spec updates: converter R1a/R1b/R1e (rewritten for HTML emit + nested-table examples); adopter Phase 5e step 7; reviewer Phase 4 R1 detail-table check. SRS re-rendered: 7/7 detail tables now HTML; 3 cells with multi-column source data (AFAI-3518 AC1, AFAI-3537 AC8, AFAI-3536 AC2) now carry true nested `<table>` blocks instead of bullet rows.
  **Post-update:** existing v21.x adopted MDs render in the old narrow-Value layout; re-adopt under v22 swaps to HTML detail tables with proper widths. SPEC-ROLL-FORWARD path (adopter Phase 0.4) now covers the v21.x → v22 jump as a "rewrite tables only" pass — body content unchanged.
- 21.1 (2026-04-20): **R1e v21.1 — user-story keyword bolding + per-bullet newlines + sub-table rendering inside AND clauses.** First v21 SRS render (commit 70c5a7b) was structurally correct but visually unreadable: GIVEN / WHEN / THEN / AND ran together as plain prose; multi-bullet color-keys (Blue 0–1mm • Light Blue 1–2mm • ...) collapsed to a single line; sub-tables inside AND clauses (button-state matrix in AFAI-3537 AC8, color-key in AFAI-4083 AC1) were inline-flattened into illegible runs. v21.1 fixes the **emit shape** (no semantic change): (a) **bold keywords** — wrap `AS A`, `GIVEN THAT`, `GIVEN`, `I WANT`, `SO THAT`, `WHEN`, `THEN`, `AND`, `BUT`, `IF`, `ELSE` in `**...**` so they read as section markers within the cell; (b) **newline per clause** — every keyword opens its own `<br>`-separated line; (c) **bullets get their own lines** — `<br>• <text><br>• <text>` instead of inline `• a • b • c`; (d) **sub-table block inside AND** — for multi-column nested data (button-state matrix etc.), render as bullet block with bolded primary identifier + `·`-separated columns, one row per bullet, all on their own lines. R1e converter spec rewritten with worked example; adopter Phase 5e step 7 references R1e for emit-time formatting. SRS re-rendered under v21.1 for AC1 of AFAI-4083 and AC8 of AFAI-3537 (the worst v21.0 readability cases) — body lines grow modestly but visual readability improves dramatically.
  **Post-update:** existing v21.0 adopted MDs are still v21-shape-correct. The next adopt run for any req doc emits the v21.1 line layout. Existing v21.0 docs can be brought current via `docflow review --fix` (the new `R1-CELL-ILLEGIBLE-RUN` flag: bullets `• a • b • c` inline without `<br>` separators is auto-fixed by inserting `<br>` before each `•` past the first), OR by hand on a per-doc basis.
- 21 (2026-04-20): **R1 v3 shape — column reorder (Value before Criticality), `none` backticked, plus first round of performance optimizations (A/C/F).** Fresh-context resume after the v20 SRS re-adopt surfaced three issues in one round of user feedback. Fixes: (a) **Detail-table column reorder** — `Field | Criticality | Value` → `Field | Value | Criticality`. Value (the user-story / GIVEN-WHEN-THEN) is the primary content readers want to scan; Criticality is an annotation on the right edge. Reads more naturally left-to-right; keeps the visually heavy inline-code CtX cluster from competing with the actual requirement text. Affects converter R1a, adopter Phase 5e step 7 emit, reviewer Phase 4 audit. (b) **`none` backticking** — under v20 `none (inferred)` was plain text while `` `CtS` (inferred) `` and other CtX tags were inline-code. Visual mismatch — `none` drew the eye as unstructured prose. v21 wraps as `` `none` (inferred) `` so it sits in the same grey channel as CtX tags. (c) **Reviewer spec-drift catchup** — reviewer Phase 4 still referenced the v19 7-column attributes table; updated to v21 (6-col attributes + 3-col detail with v21 column order). New `R1-SHAPE-WRONG` flag covers the v20 column-order leftover; new `none-UNBACKTICKED` flag covers the v20 plain-text `none` leftover; both are auto-fix high confidence. (d) **Performance optimizations A + C + F** — the v20 SRS re-adopt agent ran 787s / 90 tool calls / 225k tokens for a 7-story doc and self-reported "IDEMPOTENT — no content changes required." Scaling to ~186 docs in Phase 1g of task 075 was untenable. v21 ships three orthogonal wins: **A — IDEMPOTENT short-circuit** (adopter Phase 0.4): new `docflow_version` field in `frontmatter-project.md`. If existing MD has `doc_version` AND `docflow_version` matching the current run, adopter skips Phases 1–6 entirely and exits with one-line "unchanged" report. New SPEC-ROLL-FORWARD path covers the case where doc_version is unchanged but docflow_version bumped — runs trimmed Phase 5e only (rewrite per-requirement tables under new shape; no body re-extract). **C — Single source-extract pass** (adopter Phase 2 addendum): extract source ONCE into `{{STAGING_DIR}}/source.txt`, every downstream phase reads cache. Prior versions re-shelled `pdftotext` per-requirement during Phase 5e. **F — Review lite-mode** (`SCOPE=frontmatter-only`): reviewer Phase 0 short-circuits to frontmatter + cross-ref + requirements-doc audits only; skips per-Mermaid block audit, image audit, source-pairing — body didn't change in IDEMPOTENT runs, so per-block audits contribute zero value. Expected payoff: re-runs ~80% faster (A+F stacked), fresh adopts ~30% faster (C). Phase 1g (~186 docs) bulk adoption was the trigger; iteration loops on individual specs benefit too.
  **Post-update:** Existing v20 adopted MDs are NOT short-circuit-eligible until they carry a `docflow_version` field. Either (a) re-adopt under v21 (gets A/C/F + new shape together), or (b) hand-add `docflow_version: "v20"` to frontmatter and accept that the next v21+ adopt will SPEC-ROLL-FORWARD (rewrite tables under v21 rules, preserve human-edited values without body re-extract). Reviewer in lite-mode can confirm `docflow_version` presence + spec match without touching the body.
- 20 (2026-04-20): **R1 v2 shape refinement — Criticality moves to detail-table per-AC rows; softer labels; inline rationale for inferred values.** SRS v19 review surfaced that different ACs within the same requirement can have different CtX tags (a heat-map display AC may be CtF+CtS while its legend-display AC is CtF only). Collapsing to a single req-level Criticality loses that fidelity. v20 restructures: (a) **attributes table drops Criticality** (7 → 6 cols: `Key | Traces To | Epic | Classification | Target | Status`); (b) **detail table adds Criticality column** (2 → 3 cols: `Field | Criticality | Value`) — each AC carries its own CtX assessment per use-flow; Description row holds the req-level summary as union of AC CtX tags; (c) **label simplification** — `null` replaces `*(none — manual trace)*` for unresolved Traces To; `none (inferred)` replaces empty/blank for CtX couldn't-determine; `(inferred)` (lowercase plain parens, no italics) replaces `*(inferred)*`; (d) **inline rationale for inferred cells** — Criticality tags get a `<br>_rationale in italics._` line explaining the reasoning; auditable; human removes rationale on confirmation; (e) per-AC inference scans AC-specific GIVEN/WHEN/THEN text; `CtF` still never auto-inferred; (f) frontmatter `requirements.criticality:` counts req-level (Description row) only to avoid double-counting; (g) reviewer Phase 4 gains per-AC Criticality audit + missing-rationale check on inferred cells. Per-AC granularity enables finer trace to risk file / V&V and more realistic dashboards.
  **Post-update:** adopted SRS needs re-adopt under v20 to gain per-AC Criticality column. Human-confirmed tags (no `(inferred)` suffix) stabilize as always.
- 19 (2026-04-20): **R1 Criticality as Critical-to-X (CtX) tags + link-preservation rule.** SRS reformat exposed two gaps: (a) the prior R1 Criticality column used a single-axis 4-level scale (`critical/high/medium/low`) that didn't express *why* a requirement was critical; (b) the flattening pass dropped inline markdown links `[text](url)` from source content — faithfulness violation. v19 addresses both: (1) **Criticality = CtX multi-valued tags** anchored in project `glossary.md` "Criticality Tags": `CtF` (Critical to Function), `CtS` (Critical to Safety), `CtC` (Critical to Compliance), `CtP` (Critical to Performance). Each tag asserts which dimension of the device's intended use / indication for use the requirement is required to fulfill. Multi-valued; a req can be `CtF, CtS` (safety-critical core function). Empty CtX = nice-to-have (acceptable but flagged for periodic review). Attributes table expands to 7 columns (`Key | Traces To | Epic | Classification | Criticality | Target | Status`); (2) **Conservative CtX inference at adopt** — `safety` class → `CtS` suggestion; `regulatory` → `CtC`; `performance` → `CtP`. `CtF` is NEVER auto-inferred (functional classification doesn't automatically mean critical to intended use); humans assess against IFU; (3) **Link preservation** explicit rule in R1e — inline markdown links `[text](url)` survive flattening verbatim, never dropped silently. Jira/Confluence URLs on keys, DI cross-refs, external references all preserved. If a link can't be preserved in place due to structural mismatch, flag `%% REVIEW: link-preservation` rather than drop; (4) glossary.md updated with "Criticality Tags" section defining CtF/CtS/CtC/CtP + relationship to Classification + IFU framing; (5) frontmatter `requirements.criticality:` distribution (CtF/CtS/CtC/CtP/none counts); (6) reviewer Phase 4 audits for empty Criticality, Classification-Criticality mismatches (safety w/o CtS, regulatory w/o CtC, performance w/o CtP), and link-preservation via grep. CtX is a canonical set (not project-editable) — like Classification, cross-project dashboards depend on comparable queries.
  **Post-update:** re-adopt any previously-adopted requirement docs to pick up link preservation; review-fix to add CtX tags. Existing human-edited Classification values stabilize as always (no overwrite). The SRS in task 075 was reformatted before v19 landed — it needs a re-adopt to regain lost links + populate Criticality.
- 18 (2026-04-20): **R1 requirements-table convention + industry-informed classification taxonomy.** SRS adoption surfaced that requirement docs have uniform structure per-requirement (unlike free-form SADs or SOPs) and benefit from a distinct markup convention with structured metadata fields for dashboard queries. v18 adds: (a) **R1 two-table per-requirement shape** in `converter.md` Phase 3 — heading + 6-column attributes table (`Key | Traces To | Epic | Classification | Target | Status`) + Field/Value detail table (Description + per-AC rows). Notes as free-form prose below. Nested inner tables flatten inline with `•` bullets / `·` separators; (b) **Epic Link is the source of Category** — no synthetic keyword inference. Traces To extracted from `DI-\d+` / `UN-\d+` prefix, Epic value verbatim from source. Faithfulness-over-synthesis (same principle as F11b for Mermaid); (c) **Canonical industry-informed classification taxonomy** at `references/classification-taxonomy.md` — 9 multi-valued tags anchored in ISO/IEC 25010, ISO 14971, IEC 62366, IEC 81001-5-1, 21 CFR Part 11, MDR GSPR, HIPAA/GDPR. NOT project-editable for cross-project submission-dashboard comparability. Classification inferred from Description + AC regex patterns (definitional match → `confidence: high`); `functional` is baseline; tags multi-valued; `*(inferred)*` suffix until human override; (d) `adopter.md` Phase 5e — requirements-metadata inference; runs only when `doc_type: requirement`; populates all six attributes-table fields; respects user-override stability; (e) `frontmatter-project.md` gains `requirements:` aggregate block — count, epics map, classification distribution, target_releases, traces_to resolved/unresolved, status distribution. Feeds dashboard queries without per-requirement parsing; (f) `reviewer.md` Phase 4 gains requirements-doc audit — checks R1 shape, canonical classification tags, populated Epic, resolvable Traces To, under-classification flags; (g) first live R1 reformat on HipLink Planning SRS: 634 → 309 lines (51% compaction), 7 requirements restructured with verbatim content preservation, 4 nested color-key / button-state tables flattened inline, `%% REVIEW:` comments preserved at equivalent positions, frontmatter aggregate populated. `requirement_categories` in `project.yml` deferred — add only when Jira Epic-name drift surfaces as dashboard problem.
  **Post-update:** existing adopted SRS / FRS / NFRS / URS working MDs should be re-reformatted via targeted edit (content-preserving, not full re-adopt). Classification defaults to `functional`-only on reformat; human review fills in additional tags per source content. Canonical 9-tag list is registry-level — propose additions via `/sync-skills push` if a project surfaces a gap.
- 17 (2026-04-20): **Two-pass workflow — new `review` action + F11 extensions for layout / containment / edge-routing / label fidelity (Mermaid faithfulness rules).** SAD shakedown (round 2 of task 075 Phase 1c) surfaced that Mermaid supplement generation has failure modes the F11 spec couldn't enumerate prospectively: invented region labels on unlabeled source groupings (e.g. "API layer (outside VPC)"), containment errors (Events cluster placed outside VPC when source shows it inside), wrong layout direction (UI Layer rendered at bottom when source has it at top), and mis-routed edges (self-loops where source shows forward flow). Four iterations of "add another F11 rule + re-adopt" kept finding new error classes — diminishing returns. v17 shifts from rule enumeration to **two-pass workflow**: (a) new `/docflow review <target>` action runs after adopt; spawns `agents/reviewer.md` to validate the working MD against the source image + document, detect discrepancies across Mermaid faithfulness / frontmatter / refs / content / image integrity categories; `--fix` applies non-ambiguous corrections and flags ambiguous cases with `%% REVIEW:` comments; (b) F11 rules extended one more round — F11d containment fidelity (enumerate source regions before declaring subgraphs; nested depth matches source), F11h layout fidelity (direction from source flow; invisible `~~~` hints for edge-sparse diagrams; caption documents arrangement), F11i edge-routing fidelity (enumerate-before-emit protocol for flow diagrams: list every `(source, label, target)` triple against source image before writing Mermaid edges; Phase 7 walks them back); (c) region-label fidelity covered by F11b extension — unlabeled source regions emit `subgraph X[" "]`, never invented descriptive labels; (d) two new Best Practices checks — "Adopted working MDs have been reviewed" (Recommended) + "No outstanding `%% REVIEW:` comments" (Recommended); (e) natural-language routing for review phrasings ("verify this adopted doc", "check mermaid fidelity", "audit working md"). Rationale: image→Mermaid transcription has an irreducible error floor with image-only input (Mermaid < UML expressivity, raster ambiguity, dagre layout limits). Rather than chase every new error class with a new F11 sub-rule, the reviewer agent uses open-ended intelligence against the source as ground truth — catches classes we haven't named.
  **Post-update:** re-running `/docflow review --fix` on already-adopted working MDs applies the new F11 rules retroactively. Adopter prompt unchanged from v16; reviewer is the delta. For submission-critical diagrams, treat the source image as canonical and the Mermaid as a best-effort supplement even after review.
- 16 (2026-04-20): **Filename convention flip: drop version suffixes, adopt title-based filenames; add override-merge design.** Task 075 shakedown surfaced that the v15 convention (`-v1`/`-v2` synthetic counter in filenames) was a parallel invention — the source docs already carry their own version in Confluence page revision numbers (e.g. "v.30" in SDP Appendix E). v16 drops synthetic counters entirely: (a) working MD is `<Title>.md` and formal is `formal/<Title>.<ext>` — NO version suffix, NO `- Draft` marker, versions live in metadata + git history; (b) Title is extracted from document CONTENT at adopt time (cover page → PDF metadata → body H1 → cleaned filename, priority order); (c) `doc_version` is extracted from the document's revision history / cover / metadata (Appendix-E-style markers prioritized) and stored in frontmatter as normalized `v<N>` (no dot, e.g. `v30`); (d) Phase 0 added to adopter for title+version extraction — runs BEFORE any content conversion, fails the whole adopt if version can't be extracted (no silent defaults in regulated docs); (e) frontmatter schema updated — `doc_version` + `release_version` replace `source_version`/`working_version` integer counter; `version_lineage[]` entries keyed by `doc_version` string + `lifecycle` instead of integer `v`; `lifecycle: draft` field added; (f) override-merge design captured for when a newer formal version drops — 3-way section-aware merge between prior formal (base), current working (draft), new formal (new) with HTML-comment CONFLICT markers; implementation stubbed, triggers manual-instruction failure today; (g) Best Practices updated — v15 "files carry version suffix" check inverts to "no version suffix in filenames"; new checks for `doc_version` populated, exactly-one-formal-per-title; (h) WI inference in `authored_per` (carried from v15 fix) remains — Arthrex uses WIs as primary process-governance artifacts alongside SOPs.
  **Post-update:** any v15-era adoptions (with `-v1`/`-v2` suffixes) are legacy — they need cleanup before treating them as canonical. Task 075 includes a rollback of its one shakedown adoption before re-running under v16 convention.
- 15 (2026-04-20): **New `adopt` action for DHF formal doc → round-trippable working MD (Phase 1b of task 075).** Task 071 migrated ~215 formal DHF docs from `hiplink-suite/` into 3 item DHFs, but the content was still in binary formats — unsearchable, undiffable, unciteable. `/docflow convert` (v14) was designed for read-only QMS reference docs and didn't carry the authoring metadata DHF docs need (template instantiation, SOP process binding, filing composition, round-trip target). v15 adds a distinct action: (a) `/docflow adopt <target>` — accepts single file, whole DHF, or `<dhf> --area <path>`; renames formal to `<stem>-v{N}.{ext}` via `git mv` (linear counter, global across format transitions — formal v14 → working v15 → formal v16 → working v17); outputs working MD to `<stem>-v{N+1}.md` alongside `formal/`; (b) new `agents/adopter.md` baselined on `converter.md` with adopt-specific phases — 5a template inference (title-exact / explicit-ref / heading-structure ≥70% / title-fuzzy — confidence-scored with `template_hints` for uncertain cases), 5b SOP inference (body-scan `SOP-\d+` classified by context), 5c filing composition (inverse index from `composition-manifest.md` → `filings[]`), 5d `version_lineage` seeding; (c) `templates/frontmatter-project.md` promoted from Phase-2 stub to active adopt schema — carries identity + lifecycle + suffix versioning + `source_formal`/`target_formal` round-trip pointers + `template_of`/`template_hints`/`authored_per`/`authored_per_hints` with confidence tiers + `filings` + full `version_lineage` audit trail; (d) flags: `--plan` (dry run), `--refresh` (re-adopt with old-working marked `status: obsolete`, never destroyed), `--force`, `--no-rename`; (e) natural-language routing — phrases like "adopt this doc" / "pull into working MD" / "convert formal to markdown" route to adopt without the keyword; (f) collision detection (both unsuffixed + suffixed present → error, manual resolution required — never auto-resolve); (g) parent-README sentinel blocks re-rendered on every adopt so DHF-area READMEs stay current; (h) three new Best Practices checks — "Adopted formal files carry version suffix" (Required), "Adopted working MDs have resolvable source_formal + target_formal" (Required), "Adopted working MDs have template_of populated or flagged" (Recommended).
  **Post-update:** `/docflow adopt` is ready for sample-run validation. First-time adopters should run `/docflow adopt <dhf> --plan` to inventory before committing writes. Export (MD → formal) remains Phase 2 — a follow-up task (spawned from task 075) will build `export` + `import` + `reconcile` to complete the round-trip. Until then, adopted working MDs are authoring-ready but round-trip depends on manual pandoc passes or the forthcoming Phase 2 work.
- 14 (2026-04-16): **README-currency as a first-class concern + `validate --readmes` action.** v13 split `source/INDEX.md` into two files but the eight READMEs that referenced INDEX weren't updated in the same pass — required a follow-up sweep after the user flagged it. That's the exact drift mode the project was set up to prevent (stale READMEs silently route Claude to wrong files). v14 promotes README-currency from an implicit norm to an enforced convention: (a) new `/docflow validate --readmes` sub-action walks READMEs under `docs/internal/`, diffs link targets against actual files, flags dead links + stale references + missing pointers; (b) every structural change action (splits, moves, renames, new project-layer artifacts) has a documented obligation to sweep affected READMEs before considering the change complete; (c) two new Best Practices checks (Required): "READMEs reference current project-layer paths" and "Structural changes sweep READMEs in the same commit"; (d) one new Recommended check: "Known References have Domain + Scope". The rule generalizes beyond INDEX.md — when `deliverable-registry.md`, `obligations-index.md`, or `template-schemas/` land (per task 069), the same sweep expectation applies.
  **Post-update:** run `/docflow validate --readmes` in any adopting project — fix dead links and missing pointers it surfaces. Expect to see the same pattern each time a grounding-layer artifact is introduced.
- 13 (2026-04-16): **Split Known References into its own file — `docs/internal/qms-reference-graph.md`.** The Known References table is project-wide grounding data that spans source/ + source-md/ + future deliverable-registry + obligations/, not a source-folder catalog. Keeping it inside `source/INDEX.md` muddied the file's purpose (source catalog vs. reference graph) and made `source/INDEX.md` grow unbounded as P2-P7 conversions accumulate more unresolved refs. v13 moves the Known References section, its Domain+Scope taxonomy docs, and the format note to `docs/internal/qms-reference-graph.md`. `source/INDEX.md` keeps the functional catalog (123 rows in source/) + Source Folder Summary, and ends with a pointer to the new file. `/docflow validate --index` algorithm updated to read both files; `sync-known-refs` writes to the new file. The split positions `docs/internal/` as the project grounding layer — peers will be `deliverable-registry.md` (task 069 Phase 2), `obligations/{topic}.md` (task 069 Phase 3), `template-schemas/FORM-*.yml` (task 069 Phase 2).
  **Post-update:** the paths `docs/internal/source/INDEX.md` and `docs/internal/qms-reference-graph.md` replace the single-file convention. Any existing automation that parses Known References from `source/INDEX.md` needs the new path. The converter agent's `INDEX_PATH` parameter can stay pointing at `source/INDEX.md` for cross-ref resolution of functional-catalog entries; add a new `REF_GRAPH_PATH` parameter for Known References resolution if your converter invocation needs strict separation. In practice, reading both files with the column-aware algorithm works identically.
- 12 (2026-04-16): **Known References gains Domain + HipLink Scope columns; device-type-aware scoping.** During P2 Risk Management batch, the two RM policies (POL-000100241 + POL-000355608) cited ~40 new unresolved docs spanning manufacturing, cleanroom, inspection, calibration, and supplier procedures — all irrelevant to a SaMD program. Without classification, every unresolved ref looked equally important. v12 adds: (a) Domain column — classifies each Known Reference by persona/topic using keyword heuristics (shared taxonomy with `/advisors` + future `/dhf-builder`); (b) HipLink Scope column — derives `needed` / `indirect` / `not-needed` / `review` from Domain + project device_type; (c) published Domain taxonomy (16 domains) mapped to persona ownership; (d) documented classification ruleset (16 regex patterns applied in priority order); (e) user-override stability — once set manually, a row's Domain/Scope isn't overwritten by auto-classification. Applied to pccp retroactively — 87 Known References classified: 42 needed, 20 indirect, 23 not-needed (all manufacturing/inspection — we can skip requesting these from QMS), 2 review (no title captured).
  **Post-update:** run `/docflow sync-known-refs` — existing rows keep their Domain/Scope if populated, new rows get auto-classified. Set `project.device_type` in project.yml to one of `SaMD` / `hardware` / `combination` to tune the Domain → Scope mapping. Default is SaMD.
- 11 (2026-04-16): **Known References table gains Title column + new `sync-known-refs` action.** v10 added a preflight that surfaced unindexed docs, but the Known References table only captured `Missing Doc ID | Expected Folder | Notes` — three columns of opaque doc-ids. Users couldn't tell at a glance what `WI-000107821` or `SOP-000261193` is without grepping every converted source-md. The converter agent has been writing structured `references:` YAML in each converted file's frontmatter since v4, with `doc_id`, `title`, `resolved`, `match`, `note` per citation — but nothing was harvesting those titles into INDEX. v11 closes that gap: (a) Known References table is now 4 columns — `Missing Doc ID | Title | Expected Folder | Cited By` — titles carry the descriptive name captured from citing docs; (b) new `/docflow sync-known-refs [--dry-run]` action walks `source-md/**/*.md` frontmatter, extracts unresolved refs, diffs against INDEX, and merges new rows with auto-inferred Expected Folder (from doc-id prefix) and aggregated Cited By list; (c) `validate --index` extended — parser is now **column-aware** (reads only column 1 for Known Reference doc-ids, ignoring doc-ids that appear in Cited-By prose) and warns on rows with blank titles; (d) new Best Practices check: "Known References have titles". Applied to pccp retroactively — 41 of 43 existing Known Reference rows now carry titles extracted from converter-written frontmatter (2 remaining titleless because those docs were only cited in revision history / without inline title by the citing doc).
  **Post-update:** run `/docflow sync-known-refs` in any adopting project — if the Known References table has blank titles, the sync will populate them from converted-file frontmatter. If no titles surface even after sync, the converter either wasn't capturing titles (v3 or earlier — re-run `/docflow convert` on the citing docs) or the source doc genuinely cited the ref without a title.
- 10 (2026-04-16): **INDEX-freshness preflight for `convert` and `batch`; new `validate --index` action.** Previously the converter would silently degrade when INDEX.md fell out of sync with `source/` — cross-reference resolution would fail (unresolved refs in converted MD), and `batch` would silently exclude unindexed docs because it reads category membership from INDEX. v10 adds: (a) new preflight step 0 at the top of `convert` and `batch` that runs the INDEX-freshness check as a warning — calls out unindexed source files before spawning any converter agent, so the user can refresh INDEX first; (b) new `validate --index` sub-action with a full diff algorithm — Gap A (in source/ missing from INDEX = ERROR), Gap B (INDEX functional entry with no source file and not a Known Reference = ERROR), Gap C (Known Reference has arrived in source/ = INFO), duplicate-file warning on same-doc-id multiple copies; (c) Known-References awareness — the INDEX.md `## Known References — Not Yet in Source` section is parsed as a whitelist of doc-ids intentionally cited but not yet exported from QMS, so they don't trigger Gap B; (d) three new Best Practices checks: INDEX covers source/ inventory, no duplicate source files, source subfolders have README. Rationale: SOP-000355609 conversion surfaced 16 unresolved cross-refs, 14 of which turned out to be WIs not yet in source/ and the other 2 were docs (QSD-000108614, WI-000108236) that existed in source/ but were missing from INDEX. Without a preflight, the next batch would hit the same failure mode. Also introduces duplicate-file check because `source/Work Instructions/` has 5 `(1)`/`(2)` re-download pairs that would convert twice without warning.
  **Post-update:** run `/docflow validate --index` in any adopting project — if it reports Gap A (unindexed source docs), refresh `docs/internal/source/INDEX.md` to add them. If it reports duplicate files under source/, remove the duplicates before running any batch.
- 9 (2026-04-16): **F15 — DOCX pagination via LibreOffice-rendered PDF (preferred over F14 `w:br` fallback).** LibreOffice is already a documented toolchain dep (installed via `brew install --cask libreoffice` on mac, `apt install libreoffice-writer libreoffice-calc libreoffice-impress` on Linux/WSL — see setup.sh). When available, docflow now renders DOCX → PDF via `soffice --headless --convert-to pdf`, then paginates the rendered PDF via pdftotext form feeds. This gives **authoritative rendered pagination** (what the reader sees when printing) rather than author-intended section boundaries. FORM-000137230 example: `w:br` parsing counted 4 pages (3 explicit breaks); LibreOffice-rendered PDF counted 20 pages (the form's tables + checkbox blocks span multiple rendered pages per section). The 20-page number is what matters for regulatory traceability. F14 `w:br` parsing remains as fallback when LibreOffice is not on PATH — frontmatter `notes:` flags which method was used.
  **Post-update:** no user action needed if LibreOffice is already installed. If `soffice` is not on PATH, install via `apt install libreoffice-writer libreoffice-calc libreoffice-impress` (Linux/WSL) or `brew install --cask libreoffice` (mac), then re-run DOCX conversions to get rendered pagination instead of author-intended.
- 8 (2026-04-16): **F14 — DOCX page markers from author-intended `w:br type="page"` breaks.** Previous v5 rule skipped DOCX pagination ("Word's page concept is viewport-dependent"), but DOCX authors often commit explicit `<w:br w:type="page"/>` breaks in `word/document.xml` — these are deterministic author-intent boundaries even without a rendered PDF. Converter now parses document.xml, extracts each explicit page break's following paragraph text as an anchor, locates it in the markdown, and inserts `*— End of Page N of M —*` before it. Total pages = explicit-break-count + 1. DOCX files with 0 explicit breaks skip markers with a frontmatter note. FORM-000137230 patched: 3 explicit breaks (before "Parts in Scope", "Packaging Engineering", "Orthopedic Research Department") → 4 logical pages, 4 markers inserted. Rendering-based pagination (LibreOffice PDF export) remains a stronger but optional path when the tool is available.
  **Post-update:** no user action needed. Existing DOCX conversions can be spot-checked for explicit page breaks with `unzip -p FILE.docx word/document.xml | grep -c 'w:type="page"'` — if non-zero and no page markers in the MD, re-run or patch manually.
- 7 (2026-04-16): **F13 — Mermaid supplement emits at EVERY image occurrence, not just the canonical one.** Bilingual/multi-language documents typically show the same image (with original-language labels) in each language section — a German reader shouldn't have to jump to the English section to see the rendered diagram. Previous "emit once, cross-reference" design (v5) was wrong. Converter.md Phase 4.7 updated: emit Mermaid at every occurrence; keep labels in source image's original language (usually English) since the Mermaid is a structural supplement to the image; note this in the target-language caption explicitly. Phase 7 validation rule: "emit at every occurrence including translated sections — never skip duplicates." SOP-000355609 patched: DE section now has full Mermaid for Abbildung 1 and Abbildung 2 (same English labels as EN figures, German caption explaining labels are English per source). SOP now has 4 rendered Mermaid diagrams (2 EN + 2 DE), not 2.
  **Post-update:** no user action needed. Existing bilingual conversions should be re-rendered or the missing Mermaid blocks added at translated occurrences.
- 6 (2026-04-16): **F12 — Mermaid label-quoting rule (silent render failure otherwise).** Unquoted special characters (`/`, `(`, `)`, `:`, `,`, `&`, `#`, `?`) in Mermaid node/link labels cause silent render failure in GitHub, VS Code Mermaid extension, and many other renderers — while OTHER Mermaid blocks in the same file still render, making the failure hard to spot. Discovered in SOP-000355609 Figure 2 which contains `Item / Feature`, `DI Source`, `Identify Item/Feature`, `Hazard / Hazardous Situation / Harm` — the `/` characters broke the parser. Phase 4.7 now requires quoting every label that contains anything beyond letters/digits/hyphens/spaces/`<br>`. Phase 7 adds a Mermaid-label-scan check as a warning. Figure 2 of SOP-000355609 patched to quote all labels — now renders correctly alongside Figure 1.
  **Post-update:** no user action needed. Applies to conversions run after this update. Existing converted files with Mermaid blocks should be spot-checked — if any diagrams mysteriously fail to render while others render, the label-quoting rule is the first thing to check.
- 5 (2026-04-16): **Drop Image Manifest section, caption below Mermaid, page boundary markers for PDFs.** Review-driven simplifications: (a) `## Image Manifest` body section removed as redundant — every image is already referenced in-body with alt text + caption, and `image_count` + `has_images` live in frontmatter. Machine-readable image inventory is now an OPTIONAL `images:` frontmatter array for export / refresh pipelines. (b) Phase 4.7 Mermaid layout reordered: image → Mermaid → caption+authoritative-source line. Reader sees the diagram before the disclaimer. Caption includes `(source p.X)`. (c) New Phase 4.9: **page boundary markers for PDF sources** — `*— End of Page N of M —*` inserted at natural section/paragraph boundaries (detected from pdftotext form feeds, total count from pdfinfo). Skipped for XLSX (sheets are the unit), DOCX/DOC (no reliable page boundaries), and PDFs ≤ 2 pages. EN→DE / multi-language boundary annotated explicitly. Phase 7 updated: dropped manifest checks, added page-marker checks (presence for multi-page PDFs, consistent total M, language-boundary annotation). SOP-000355609 sample patched end-to-end: manifest section removed, both figure captions moved below Mermaid, 7 page markers added (pages 1/2/3/4/5/7/14/15 transitions).
  **Post-update:** no user action required in-project — converter.md is read per-conversion. Any conversions run after this update get the new layout automatically. Existing converted files can be migrated with a one-time pass if desired (remove manifest sections, reorder Mermaid captions, add page markers) but it's not required for downstream correctness.
- 4 (2026-04-16): **converter.md rewrite — bake in F1-F11 (image pipeline) + X1-X8 (XLSX) + transactional commit + end-of-conversion checks.** Changes: (a) Phase 3 extended with XLSX-specific rules: column-spanning merged headers → annotated leaf headers (X4), color-banding semantics preserved in frontmatter (X5), source typos preserved verbatim with `<!-- sic -->` (X6), blank-template row count reproduced (X7), dataValidation prompts preserved as Input Guidance (X3). (b) Phase 4 rewritten end-to-end: 4.1 Inventory/Dedup (F2 — group by object ID or hash; unzip supplement for XLSX VML/drawings X2), 4.2 Classify decorative vs content, 4.3 Orientation correction MANDATORY for PDF via PIL (F1), 4.4 Descriptor from caption first / heading / content — never from brief (F6, F7), 4.5 Subfolder-aware relative path `../images/` required (F10 — breaks the rendered view otherwise), 4.6 Self-contained alt text 30-100 words for complex diagrams (F8), 4.7 Mermaid supplement for flow diagrams with image as canonical authoritative source (F11), 4.8 Manifest one-row-per-unique-image not per-reference. (c) Phase 6 frontmatter guidance: blank-form templates are `faithful` not `partial` (X1). (d) Phase 7 Self-Validate expanded with end-of-conversion checks: every image ref resolves from markdown's final location (F10), every extracted image referenced at least once, manifest row-count equals unique extracted count (F2), duplicate refs permitted, orientation-checked for PDF (F1), Mermaid supplement adjacent to flow diagrams (F11 warning). (e) Phase 8 Commit rewritten as transactional sequence (F5, F9): mkdir targets → move images first → verify each image arrived → verify every markdown ref resolves from OUTPUT_DIR → only then move markdown → only then delete staging. `VALIDATION_FAILED.txt` / `COMMIT_FAILED.txt` marker files on abort. SKILL.md toolchain REQUIREMENTS block extended to include Pillow + openpyxl + pyyaml with PEP-668 install hint (F3, F4, X8); `validate --toolchain` checks Python deps too. Validated against SOP-000355609 (4th exemplar, first with real content images): image paths now resolve via `../images/`, Mermaid supplements present alongside both flow diagrams.
  **Post-update:** no user action needed in existing projects — converter.md is read per-conversion. Any conversions run after this update get F1-F11 + X1-X8 + transactional commit automatically. Existing converted files that predate this update (FORM-000137230, SOP-000326588, FORM-000355646) should be spot-checked if they have content images or live in DOC_TYPE subfolders with relative `images/` refs.
- 3 (2026-04-16): **Fix `find` option order in `extract_images.sh`.** Line 67 had `find "$DIR" -name "*.docx" -maxdepth 1` — BSD find errors on `-maxdepth` after a primary (it must precede all primaries). On macOS, the call failed with an error and returned empty, so the WF-1 image-extraction branch skipped image discovery silently. Reordered to `find "$DIR" -maxdepth 1 -name "*.docx"` which is accepted by both BSD and GNU find. No other sites audited had the same pattern. Discovered during task 067 cross-platform audit.
  **Post-update:** No user action. Script is run on demand; next invocation picks up the fix.
- 2 (2026-04-13): Added `Scope` column to the Best Practices table for `/best-practices` v8+ compatibility. Every docflow check is classified as `shared` — docflow operates on `docs/internal/source/` and `docs/internal/source-md/`, both at project root and shared across all DHFs. Also updated the README example path from `docs/project/design-controls/architecture/sad.md` to `docs/project/dhfs/<dhf>/design-controls/architecture/sad.md` to reflect the unified DHF shape (the actual docflow functionality is unchanged — the path in the example is illustrative, not enforced). See `tasks/ben/007-sub-dhf-migration.md` P5.7. **LOCAL divergence from upstream pending a future `/sync-skills push`**; upstream (hitachi) still ships v1 without the Scope column.
- 1 (2026-04-03): Initial version — convert, refresh, batch, validate, status, help, guide actions. Phase 1 (WF-4 source conversion) fully specified. Phase 2 (WF-1/2/3 import/export) stubbed.
