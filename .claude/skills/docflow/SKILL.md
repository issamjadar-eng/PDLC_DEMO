---
name: docflow
description: "Document conversion and round-trip management — convert between markdown and formal formats (DOCX, PDF, XLSX) with image fidelity, metadata tracking, and cross-reference resolution"
version: 14
updated: 2026-04-16
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

### `validate <doc-id|file>`

Check a converted file against quality criteria.

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

## Notes

- If `$ARGUMENTS` is empty or just "help", show the full help overview
- The `convert` and `refresh` actions spawn agents from `${CLAUDE_SKILL_DIR}/agents/`
- Phase 2 actions (export, import, reconcile) are defined but not yet implemented
- LibreOffice is required only for `.doc` files (16 of 127). All other formats work without it
- The staging area is never committed to git

## Changelog

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
