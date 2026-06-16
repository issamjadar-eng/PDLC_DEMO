---
name: docflow
description: "Document conversion and round-trip management between markdown and formal formats (DOCX, DOC, PDF, XLSX). Use this skill whenever a user asks to convert, adopt, import, export, refresh, round-trip, or 'test docflow on' any .docx / .doc / .pdf / .xlsx / .pptx file — whether under docs/internal/source/ (QMS SOPs, forms, policies, work instructions), under docs/project/dhfs/**/formal/ (DHF working drafts), or elsewhere in the repo. Also use when a user asks to extract images, resolve cross-references, or handle external review comments against any of those formats. Owns the conversion pipeline — image extraction, frontmatter, cross-ref resolution, quality gates, round-trip metadata — so direct pandoc / unzip / soffice / pdftotext calls are blocked by a PreToolUse Bash hook installed by the skill's `setup` action; `/docflow <action>` is the supported entry point."
version: 35
updated: 2026-04-23
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
| `agents/fidelity_adjudicator.md` | `convert`, `adopt`, `refresh` (Phase 7) | Agent prompt: adjudicate `prose_fidelity` flags fabrication-vs-reformatting against the source; returns CLEAR/BLOCK. Spawned only when the deterministic finder `warn`s. The gate that catches LLM-regenerated prose (the `source-md` fabrication failure mode). |
| `scripts/verify_conversion_fidelity.py` | `convert`, `adopt`, `refresh` (Phase 7), CLI/CI | Deterministic prose-fidelity finder: shingle-diffs converted markdown against the source (`pdftotext`) and flags prose runs absent from it. Triage (pass/warn) — feeds the adjudicator; never auto-fails on word-count. Importable `assess()`; CLI supports `--dir`/`--json`. |
| `scripts/validate_phase7.py` | `convert`, `adopt` (Phase 7) | Scripted Phase-7 gate (structure/markers/images/links). `--source <pdf>` adds the `prose_fidelity` check (warn + `requires_adjudication` + spans). |
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
  /docflow adopt <file>                 Single formal doc (default: into DHF area, restructured to formal/)
  /docflow adopt <dhf>                  All formal/ content in a DHF
  /docflow adopt <dhf> --area <area>    Scope to one sub-area
  /docflow adopt <binary> --into <md>   Explicit-location: any source binary → working MD at <md>,
                                        binary stays put (no formal/ restructure)

FLAGS:
  --plan                   Dry run — inventory + planned actions, no writes
  --refresh <file>         Re-adopt a file whose formal changed out-of-band.
                           Previous working MD gets status: obsolete; new
                           working MD created at the next version.
  --force                  Skip "working MD already exists" warning
  --no-rename              Skip formal rename (advanced — breaks version lineage
                           consistency, for manual recovery only)
  --into <md-path>         Explicit output location for the working MD. Lifts the
                           dhfs/**/formal/ source requirement (binary may live
                           anywhere) and leaves the binary IN PLACE — no rename,
                           no formal/ restructure. source_formal points at the
                           binary's actual location. One file → one location.
  --binary-authoritative   Mark the binary as the controlled record and the MD as
                           a derived faithful view (authoritative: formal). The MD
                           is refreshed FROM the binary; export never overwrites it.
                           Use for externally/team-authored controlled documents.
                           Required when --into targets a managed _confluence page.

  SPLICE: when --into points at an existing managed _confluence page (its leading
  <!-- --> block has a confluence: key), adopt SPLICES instead of colliding —
  preserves the comment-block frontmatter (confluence: binding + state:), the
  page-title / doc-governance / attachments sentinels, and intro blockquotes;
  folds a docflow: provenance sub-block (source, authoritative, conversion
  date/direction) into the comment block; replaces ONLY the body inside an
  AUTO:DOCFLOW-BODY sentinel; refreshes the controlled-record blockquote.

PRODUCES (default mode):
  <dhf-area>/<stem>-v{N+1}.md                  (working MD)
  <dhf-area>/formal/<stem>-v{N}.{ext}          (renamed formal, via git mv)
  <dhf-area>/images/                           (extracted images, if any)

PRODUCES (explicit-location mode, --into a NEW path):
  <md-path>                                    (working MD, verbatim location)
  <md-dir>/images/                             (extracted images, if any)
  (source binary unchanged, in place; source_formal points at it)

PRODUCES (SPLICE — --into an existing _confluence page):
  <page>.md                                    (body replaced in-place; preamble + sentinels preserved)
  <page-dir>/images/                           (extracted figures, alongside the attachment)
  (comment block gains a docflow: sub-block; AUTO:DOCFLOW-BODY wraps the body)

EXAMPLES:
  /docflow adopt mfd-c --plan
  /docflow adopt mfd-a --area design-controls/user-needs
  /docflow adopt docs/project/dhfs/mfd-a/design-controls/user-needs/formal/AFAI-MedTech Project\ Planning-170426-111505.pdf
  /docflow adopt "docs/project/_confluence/<dhf>/<root>/<slug>/images/FORM-NNN.docx" \
    --into "docs/project/_confluence/<dhf>/<root>/<slug>/derived/FORM-NNN.md" \
    --binary-authoritative
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

**Flags recognized**: `--plan`, `--refresh <file>`, `--force`, `--no-rename`, `--area <path>`, `--into <md-path>`, `--binary-authoritative`

0. **Preflight**:
   - **Auto-locate sub-mode** (no `--into`, and the positional target is a **single binary** that is NOT under `docs/project/dhfs/<dhf>/**/formal/` and is NOT a DHF leaf name): docflow **infers** the output location by convention-detection instead of erroring. Run `python3 .claude/skills/docflow/scripts/locate_md_target.py "<binary>" --root .` and branch on the JSON `confidence` band (the helper reads the project's OWN conventions — existing link → `source→source-md` tier rule → nearest `.taxonomy.yml` → sibling-folder pattern → README; it never guesses from the filename):
     - `covered` → an md view already exists/links this binary (`target_md`). Report it and STOP — nothing to adopt.
     - `high` → set `INTO_PATH = target_md`, `AUTHORITY = formal` (binary is the controlled record), and proceed exactly as **explicit-location mode** below (incl. SPLICE if `target_md` is an existing managed `_confluence` page). Echo the inferred target + rationale to the user.
     - `prompt` → the location/action is ambiguous (e.g. a folder already holds an md that may BE the view — see `alternatives[].action: link-existing`, or a `_confluence` node has multiple possible attachments). Present `target_md`, the `rationale`, and any `alternatives` (link-existing vs generate-new), and STOP for the user to confirm or pass `--into` explicitly. **Do NOT auto-generate** — silently creating a duplicate view is exactly the failure this guards against.
     - `none` → no convention signal. Report and ask the user for an explicit `--into <md-path>`.
     This sub-mode is what the file-locator `audit` detector hands off to (it finds binaries with no indexed md and calls `/docflow adopt <binary>` with no `--into`).
   - **Default mode** (no `--into`): target must either resolve to a single file under `docs/project/dhfs/<dhf>/**/formal/`, OR be a DHF leaf name matching `project.yml` `dhfs[]`.
   - **Explicit-location mode** (`--into <md-path>` given): the positional target is a single **source binary at any path** (the `dhfs/**/formal/` requirement is lifted — the binary may live anywhere the team manages it, e.g. a `_confluence` node's `images/<file>.docx`). `--into` is the explicit output path for the working MD; the binary stays where it is. `--binary-authoritative` marks the binary as the controlled record (MD is a derived view). DHF-name and `--area` forms are not valid with `--into` (it adopts exactly one file to one location).
   - Verify `docs/internal/source-md/Forms/` and `docs/internal/source-md/SOPs/` exist (required for template + SOP inference). If missing or empty, warn but do not block — inference will return null candidates.
   - **Collision check**: default mode — for each formal file, if both `<stem>.ext` AND `<stem>-v{N}.ext` exist in the same folder → error. Explicit-location mode — if the `--into` path already exists, branch: (a) the existing file is a **managed `_confluence` page** (its leading `<!-- … -->` block contains a `confluence:` key) → **SPLICE mode** (preserve the comment block + all sentinels + intro blockquotes; fold a `docflow:` sub-block into the comment block; replace only the body, wrapped in an `AUTO:DOCFLOW-BODY` sentinel; refresh the provenance blockquote — see `agents/adopter.md` "`_confluence`-page splice"). Splice requires `--binary-authoritative`. (b) any other existing file → error unless `--force`. Auto-resolution silently loses content; we require explicit intent.
   - If `--plan`, compute the action list and report without writing.

1. **Resolve target**:
   - **Single file, default mode** (absolute or relative path to a formal file) → one adoption job. Infer the DHF by walking up the path until a `project.yml` `dhfs[].path` match is found. Infer DHF_AREA from path segments between the DHF root and `formal/`. DHF_AREA_DIR = parent of `formal/`.
   - **Single file, explicit-location mode** (`--into <md-path>`) → one adoption job. SOURCE_PATH = the positional binary (any location). OUTPUT goes to `--into <md-path>` verbatim; OUTPUT_DIR = `dirname(<md-path>)`; the binary is **not** moved or renamed. Best-effort DHF/DHF_AREA inference: if `<md-path>` falls under a `project.yml dhfs[].path`, populate `dhf`/`dhf_role`/`dhf_area` from it; otherwise leave them null (the explicit path is authoritative, not the DHF layout). AUTHORITY = `formal` if `--binary-authoritative` else `working`.
   - **DHF name** (e.g. `mfd-c`) → enumerate every file under `docs/project/dhfs/<dhf>/**/formal/` matching `{pdf,docx,doc,xlsx,pptx}`. Exclude patterns: `c-arm-simulator-main/**` (source code), `HLCAS-TC-*` + `*.dcm` + pure-evidence screenshots (runtime evidence, not documentation).
   - **DHF + `--area <path>`** → scope to `docs/project/dhfs/<dhf>/<area>/formal/`.

2. **Per-file adoption** (for each resolved file):

   **2a. Spawn adopter agent** — the agent does all extraction, rename, conversion, and validation:
   - Spawn an Agent with `agents/adopter.md`, parameterized with: SOURCE_PATH (as-dropped), FORMAT, DHF, DHF_ROLE, DHF_AREA, DHF_AREA_DIR, STAGING_DIR, DOC_VERSION_OVERRIDE (if user passed `--doc-version`), FORMS_INDEX_PATH, SOPS_INDEX_PATH, WIS_INDEX_PATH, MANIFEST_PATHS, PROJECT_REFS_PATH, **INTO_PATH** (the `--into` value, or null), **AUTHORITY** (`formal` if `--binary-authoritative` else `working`).
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
   - On agent success (default mode), working MD has landed at `<DHF_AREA_DIR>/<TITLE>.md` and formal at `formal/<TITLE>.<ext>`. Parent README sentinels re-rendered.
   - On agent success (explicit-location mode), working MD has landed at the `--into` path verbatim; the source binary was **not** moved (`source_formal` points at its in-place location); `authoritative` reflects `--binary-authoritative`. No `formal/` restructure.
   - On agent success (SPLICE mode — `--into` an existing managed `_confluence` page), the page's comment-block frontmatter (incl. `confluence:` binding), all sentinels (page-title, `doc-governance`, `confluence-side: attachments`), and intro blockquotes were preserved; a `docflow:` provenance sub-block was folded into the comment block; the body was replaced inside an `AUTO:DOCFLOW-BODY` sentinel. Surface any `body_deltas` the agent reported for RA review.
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
- On a cadence (e.g., `/docflow review mfd-c` weekly) for drift detection

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
3. **Collect Known-Reference titles + domain + scope**: for each first-column match, also capture columns 2 (Title), 3 (Domain), 4 (MedTech Project Scope). A Known Reference row with a blank/placeholder title (`_(unknown…)_` or empty) warns — the converter should have captured a title in its frontmatter `references:` block. A row with `review` scope warns too — manual classification needed.
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
| MedTech Project Scope | Derived from Domain + project `device_type` | Tells the team whether to request this doc from QMS |
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

**MedTech Project Scope values**:
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
See [README.md](README.md) — consumed by `/best-practices` audit.

## Notes

- If `$ARGUMENTS` is empty or just "help", show the full help overview
- The `convert` and `refresh` actions spawn agents from `${CLAUDE_SKILL_DIR}/agents/`
- Phase 2 actions (export, import, reconcile) are defined but not yet implemented
- LibreOffice is required only for `.doc` files (16 of 127). All other formats work without it
- The staging area is never committed to git

## Changelog

- **v35** — Clarified the SPLICE faithful-to-source-structure rule. "Faithful" means render the document's **real sections as `## N. Title` headings, preserving the source's numbering** — whether the source used Word heading styles OR numbered section-divider paragraphs (promoting a real numbered section to a heading is a faithful transposition, not an invention, and keeps pages navigable + consistent). v34 was too literal (it kept numbered section paragraphs as list items, producing un-navigable bodies that disagreed with sibling pages). Still forbidden: fabricating/dropping/re-ordering/re-titling sections or inventing heading levels with no real section. Body content (tables/lists/figures) stays as-is. Wanting different structure is a source-document edit, then refresh. (ben/229)
- **v34** — SPLICE-mode **non-canonical + publish-gate + faithfulness policy** (for `authoritative: formal` pages). The attached binary is the canonical record; the page markdown is an internal, non-canonical derived view for agent/reviewer findability — so SPLICE now (a) inserts a required top **`AUTO:DOCFLOW-NOTICE`** banner ("🚫 NON-CANONICAL — DO NOT EDIT THIS MARKDOWN; edit the source document and re-run docflow"), (b) sets **`confluence.publish_body: false`** by default (the markdown body is NOT pushed to Confluence unless the team opts in; the attachment + node `index.md` is the publication), and (c) enforces **faithful-to-source structure** (HARD RULE — mirror the source's real heading styles / numbered paragraphs as-is; do NOT invent a heading outline the controlled record lacks; structural changes are source-document edits, then refresh). `docflow.conversion.faithful_to_source_structure: true` records this. (ben/229)
- **v33** — `adopt` **`_confluence`-page SPLICE mode** (extends explicit-location mode). When `--into` targets an existing managed `_confluence` page (leading `<!-- -->` block has a `confluence:` key), docflow no longer treats it as a collision — it **splices**: preserves the comment-block frontmatter (incl. the `confluence:` binding + change-control `state:`), the `AUTO:PAGE-TITLE` / `doc-governance` / `confluence-side: attachments` sentinels, and hand-authored intro blockquotes; folds a `docflow:` provenance sub-block into the comment block (authoritative side, `source_formal`, source format, conversion direction + date + method + fidelity + docflow_version, refresh_cmd); replaces **only** the body inside a new docflow-owned `AUTO:DOCFLOW-BODY` sentinel (which `refresh` regenerates); and refreshes the controlled-record provenance blockquote. Governance IDs are NOT duplicated into `docflow:` (they render from `.taxonomy.yml` via the `doc-governance` sentinel). Requires `--binary-authoritative`. Notable body-content deltas vs. a prior page draft are reported as `body_deltas` for RA review, not silently dropped. Grounded in `change-control/lib/frontmatter.py` (the comment block is `yaml.safe_load`-parsed → `docflow:` coexists with `confluence:`, round-trips, and is stripped before Confluence push). (ben/229)
- **v32** — `adopt` explicit-location mode. New flags `--into <md-path>` (output the working MD at an explicit path; lifts the `dhfs/**/formal/` source requirement so the binary may live anywhere; leaves the binary IN PLACE — no rename, no `formal/` restructure; `source_formal` points at its actual location) and `--binary-authoritative` (binary is the controlled record, MD is a derived faithful view refreshed FROM the binary, never exported back over it — new `authoritative: formal|working` frontmatter field). Default mode behavior is unchanged (`INTO_PATH` null → `OUTPUT_DIR == DHF_AREA_DIR`). Motivation: adopting team/externally-authored controlled binaries that already live where the team manages them (e.g. a `_confluence` node's `images/<file>.docx`) into a git-reviewable working MD without forcing the waterfall layout. (ben/229)

See [README.md](README.md) for earlier version history.

