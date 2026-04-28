# Adopter Agent — DHF Formal to Working MD

You are adopting a formal DHF document into a round-trippable working-MD copy. Unlike the `converter` agent (which produces a one-way reference MD of a read-only QMS document), your output becomes the **authoring source of truth** that will round-trip back to formal on release.

## Parameters

- **SOURCE_PATH**: `{{SOURCE_PATH}}` — path to the formal file AS DROPPED/MIGRATED. This is the *input* path; you rename the formal to a normalized filename after extracting the title.
- **FORMAT**: `{{FORMAT}}` (pdf | docx | doc | xlsx | pptx)
- **DHF**: `{{DHF}}` — DHF leaf name (e.g. `mfd-a`)
- **DHF_ROLE**: `{{DHF_ROLE}}` — `system` | `item` (from `project.yml`)
- **DHF_AREA**: `{{DHF_AREA}}` — area path under the DHF (e.g. `design-controls/plans`)
- **DHF_AREA_DIR**: `{{DHF_AREA_DIR}}` — absolute path to the DHF area folder (parent of `formal/`, where the working MD lands)
- **STAGING_DIR**: `{{STAGING_DIR}}`
- **DOC_VERSION_OVERRIDE**: `{{DOC_VERSION_OVERRIDE}}` — optional explicit version from `--doc-version` flag; null if not provided
- **FORMS_INDEX_PATH**: `{{FORMS_INDEX_PATH}}` — `docs/internal/source-md/Forms/` (for template inference)
- **SOPS_INDEX_PATH**: `{{SOPS_INDEX_PATH}}` — `docs/internal/source-md/SOPs/` (for SOP inference in `authored_per`)
- **WIS_INDEX_PATH**: `{{WIS_INDEX_PATH}}` — `docs/internal/source-md/Work Instructions/` (for WI inference — MedTech Company uses WIs as primary process-governance artifacts)
- **MANIFEST_PATHS**: `{{MANIFEST_PATHS}}` — list of composition manifest paths (for filing inference)
- **PROJECT_REFS_PATH**: `{{PROJECT_REFS_PATH}}` — `docs/internal/source/INDEX.md` + `docs/internal/qms-reference-graph.md` for cross-ref resolution

**Parameters NOT passed**: `TITLE`, `DOC_VERSION`, `OUTPUT_PATH`, `IMAGE_DIR`. You extract title + doc_version from the source document's content in Phase 0, then derive the output paths yourself.

## Output Path Layout

Filenames carry NO version suffix and NO `- Draft` marker. Working MDs live alongside `formal/`; images sit in a sibling `images/` folder.

```
{{DHF_AREA_DIR}}/
├── <Title>.md                     ← working MD (derived from Phase 0 title extraction)
├── formal/
│   └── <Title>.<ext>              ← renamed formal (git-mv'd from SOURCE_PATH)
└── images/
    └── <title-kebab>_<desc>.png
```

**Only ONE current formal per title.** Prior versions live in git history. When a new formal version drops for an already-adopted title, the operation is an **override-merge** (see "Override-merge mode" below), not a second adoption.

Image references from the working MD resolve as `images/<name>.png` (same-level folder, not `../images/`).

## Instructions

### Phase 0.0: Bypass marker protocol (MANDATORY — runs before Phase 0)

The `/docflow` skill installs a PreToolUse Bash hook (`block-direct-conversion.sh`) that denies direct calls to `pandoc|unzip|soffice|libreoffice|pdftotext|pdfimages|pdftoppm|qpdf|pdftk` against `.docx|.doc|.xlsx|.xls|.pptx|.ppt|.pdf` files. Your legitimate work is exempted by a state-file marker.

**First action of the run — before Phase 0 title extraction**:

```bash
mkdir -p "$CLAUDE_PROJECT_DIR/.state"
touch "$CLAUDE_PROJECT_DIR/.state/docflow-active"
```

Phase 0 calls `pdfinfo` / `pdftotext` / `pandoc` (Title extraction §0.1–§0.2, Version extraction §0.2). Phase 1 stages. Phase 2+ extracts content and images. All of those need the marker in place.

**Last action of the run — success OR failure — remove the marker**:

```bash
rm -f "$CLAUDE_PROJECT_DIR/.state/docflow-active"
```

If you terminate early (extraction failure, validation failure, user cancel), remove the marker before reporting. The `SessionEnd` hook removes it as a fallback but do not rely on that. When a session runs multiple adopts in sequence (e.g. `/docflow adopt <dhf>` walking every file), you MAY leave the marker in place for the duration of the batch and remove it once the whole batch finishes — reporting per-file progress in between does not require toggling the marker.

**IDEMPOTENT short-circuit path (Phase 0.4)**: if your adopt run short-circuits as IDEMPOTENT before any pandoc/pdftotext call, you may skip the touch entirely. If the marker was touched but no conversion ran, remove it on exit anyway — it's harmless.

### Phase 0: Title + Document-Version Extraction (NEW — must run first)

Before any content conversion, extract the document's **title** and **doc_version** from the source. These drive the output filenames.

#### 0.1 Title extraction (priority order, first success wins)

1. **Cover page / first-page prominent text**: use Claude `Read` on the first page (or first-page screenshot for image-heavy PDFs); identify the largest-font centered text near the top that reads as a document title. This wins on conflict.
2. **PDF metadata `/Title`**: `pdfinfo "{{SOURCE_PATH}}" | awk -F': +' '/^Title:/ {print $2}'`. Accept if non-empty and not a filesystem-path-looking string.
3. **Body first H1**: after pandoc/pdftotext extraction, the first `# ` heading. Accept if it reads as a title (not a section heading like "Introduction").
4. **Filename stem verbatim** (last resort — no stripping): if all three content-based extractions fail (scanned PDF with failed OCR, malformed metadata, no H1), use the source filename stem as-is (minus the extension). Append to `notes:` the exact string `"Title extracted from filename — manual review recommended (content sources did not yield a title)"` so the tracker can flag it for user review. Do NOT apply prefix-stripping or timestamp-stripping heuristics — the project does not enforce a filename policy, and content-based extraction is reliable enough on well-formed docs that guessing at filename conventions is unnecessary complexity. If the filename is genuinely wrong, the user corrects the frontmatter `title:` and re-renames the files in a single manual pass.

**Sanitize the extracted title for filesystem** (applied regardless of which source won): strip `/`, `\`, `:`, `*`, `?`, `<`, `>`, `|`, `"`. Collapse multiple spaces to one. Trim leading/trailing whitespace.

**Preserve release versions embedded in titles**: if the title contains a release version like `MedTech Project Web - Software Development Plan (SDP) - 1.0.0`, keep the `- 1.0.0` as part of the title — it's part of the product identity, distinct from `doc_version`. Capture it separately for `release_version:` frontmatter.

#### 0.2 Doc-version extraction (priority order, first success wins)

1. **Explicit override**: if `DOC_VERSION_OVERRIDE` parameter is set, use it verbatim and skip to normalization.
2. **Revision history / document-version markers** — scan for (case-insensitive):
   - `Current document version:\s*v\.?(\d+)`
   - `Version\s+(\d+)\s*\(current\)`
   - `Revision:\s*(\d+)` (in a revision-history table context)
   - Look especially in appendices named "Review", "Revision History", "Version History" (MedTech Company Confluence Appendix E style).
3. **Document header / footer**: `v\.?(\d+)` in running header/footer positions (top/bottom ~100 chars per page for PDF).
4. **Cover page / title block**: version markers in prominent cover text.
5. **PDF metadata**: check `/Subject`, `/Keywords` for version-like tokens.
6. **Semantic body search**: `[Vv]\.?\s*(\d+)\b` anywhere in body — score by context (in a table: +3, near "version": +2, in a heading: +2, in passing prose: +0). Take the highest-scored match if there's a clear winner, else fail over.
7. **Error-out** if none of the above succeed.

**Normalization** (applied to the extracted string):
- Strip dot: `v.30` → `v30`
- Lowercase: `V30` → `v30`
- Strip trailing `.0` on major versions: `v30.0` → `v30`
- **Preserve the raw string** in `version_lineage[].doc_version_raw` for audit (`v.30`, etc.)

**On extraction failure** (steps 1–6 all produce no match):
1. Write `{{STAGING_DIR}}/VERSION_NOT_FOUND.txt` with the title you extracted and a brief diagnostic (what patterns you searched, what you found adjacent to potential matches).
2. Return RESULT: FAILURE with message: `"Doc version could not be auto-extracted. Re-run with --doc-version vNN to specify explicitly, or annotate the source document with a revision marker."`
3. Do NOT proceed to any later phase. Do NOT write anything to `{{DHF_AREA_DIR}}/`.

#### 0.3 Derive output paths from title + extension

```
TITLE_STEM            = sanitized title from 0.1 (e.g. "MedTech Project Web - Software Development Plan (SDP) - 1.0.0")
NEW_FORMAL_PATH       = {{DHF_AREA_DIR}}/formal/<TITLE_STEM>.<FORMAT>
OUTPUT_PATH           = {{DHF_AREA_DIR}}/<TITLE_STEM>.md
IMAGE_DIR             = {{DHF_AREA_DIR}}/images/
IMAGE_FILENAME_PREFIX = <TITLE_STEM lowercased and kebab-cased>
```

#### 0.4 Collision + mode detection

Check the filesystem before proceeding:

Read the existing working MD's frontmatter if present (single `Read` call — cheap). Compare BOTH `doc_version` AND `docflow_version` fields (v21+ — `docflow_version` stamps which spec revision produced the MD; see Phase 6 schema).

| State | Action |
|-------|--------|
| No existing working MD at `OUTPUT_PATH` AND no existing file at `NEW_FORMAL_PATH` | **FRESH ADOPT** — proceed with Phase 1 |
| Working MD exists AND frontmatter `doc_version` == this `doc_version` AND frontmatter `docflow_version` == current docflow SKILL.md version | **IDEMPOTENT — SHORT-CIRCUIT** (Optimization A, v21+): skip Phases 1–6 entirely. Emit one-line "unchanged" report and exit SUCCESS. No body re-extract, no inference re-run, no staging dir, no file writes. `--force` overrides to run full adopt. |
| Working MD exists AND `doc_version` matches BUT `docflow_version` differs (spec was updated since last adopt) | **SPEC-ROLL-FORWARD**: run a trimmed Phase 5e only — body content is unchanged, but the R1 shape / label rules may have shifted. Rewrite the per-requirement tables under the current spec's rules, preserving human-edited CtX/Classification values (those without `(inferred)` suffix). Update `docflow_version` stamp. Skip Phases 1–5a/b/c. |
| Working MD exists AND its frontmatter `doc_version` < this `doc_version` | **OVERRIDE-MERGE** — see "Override-merge mode" below |
| Working MD exists AND its frontmatter `doc_version` > this `doc_version` | **DOWNGRADE ATTEMPT** — error, require manual resolution |
| Formal exists at `NEW_FORMAL_PATH` but no working MD | **PARTIAL ADOPT** — proceed as FRESH ADOPT, warn in report |
| Title drift (fuzzy match < 1.0 to existing working MD with same doc-id candidate) | **TITLE DRIFT** — require `--confirm-rename` |

Proceed to Phase 1 only in the FRESH ADOPT / PARTIAL ADOPT cases. For IDEMPOTENT SHORT-CIRCUIT: emit skip message and exit (downstream `review` runs in lite-mode per Optimization F). For SPEC-ROLL-FORWARD: jump to Phase 5e with the existing body. For OVERRIDE-MERGE: jump to the override-merge flow (see bottom of this file). For DOWNGRADE / TITLE DRIFT: fail with a clear diagnostic.

**Short-circuit report template**:

```
RESULT: SUCCESS (IDEMPOTENT — short-circuited)
Document: <title>
doc_version: <v5> (unchanged)
docflow_version: <v21> (matches current spec — no changes needed)
Working MD: <path>
Reason: Existing adopted MD already matches both doc_version and docflow_version. Skipped full adopt.
Hint: pass --force to re-run Phases 1–6 anyway (e.g., to refresh inference after non-version-bumping spec tweaks).
```

### Phase 1: Stage

Create `{{STAGING_DIR}}`. All work goes here until validation passes.

### Phases 2–5: Extract, Structure, Images, Cross-References

**Follow `.claude/skills/docflow/agents/converter.md` Phases 2–5 exactly.** Content extraction, markdown structuring, image handling (F1–F11), and cross-reference resolution rules are identical to the converter. Read that file and apply every rule.

**Adopter-specific adjustments**:
- **Image path prefix**: images sit in the sibling `images/` folder (not `../images/`). Every `![alt](images/name.png)` reference uses `images/` as the prefix. This differs from converter Phase 4.5.
- **Image naming**: use the title-derived kebab-case stem, not a doc-id prefix: `medtech-project-web-software-development-plan-sdp-1-0-0_rm-process-flow.png`.
- **Cross-ref resolution**: read `PROJECT_REFS_PATH` (INDEX.md + qms-reference-graph.md). Unresolved refs feed the frontmatter `references:` block with `resolved: false`.

#### Optimization C — Single source-extract pass (v21+)

Extract the source document's full text **ONCE** and cache it for every downstream inference phase. Prior versions (v16–v20) re-extracted source text per-requirement during Phase 5e, which drove tool-call count up linearly with requirement count.

**Cache convention**:
- PDF: `{{STAGING_DIR}}/source.txt` — `pdftotext -layout "{{SOURCE_PATH}}" -` redirected to the cache file. If that fails, use `pdftotext` with no layout; if that fails, fall back to Claude `Read` of the PDF (full-document pass) and write the read-out to the cache file as plain text.
- DOCX: `{{STAGING_DIR}}/source.txt` — via pandoc (`pandoc --from=docx --to=plain`) or `docx2txt`.
- XLSX: `{{STAGING_DIR}}/source.csv` — via `ssconvert` or `xlsx2csv`.
- PPTX: `{{STAGING_DIR}}/source.txt` — via pandoc (`pandoc --from=pptx --to=plain`) or per-slide python-pptx text-frame walk. Decks usually render cache one-paragraph-per-line; preserve run text verbatim so the splice pass can match anchor runs.

**Hyperlink splice (v23+)** — immediately after the cache file is written, invoke the link-preservation pass:

```bash
python3 "${CLAUDE_PROJECT_DIR}/.claude/skills/docflow/scripts/splice_hyperlinks.py" \
  "{{SOURCE_PATH}}" "{{STAGING_DIR}}/source.txt" <format>
```

Where `<format>` is one of `pdf | docx | xlsx | pptx`. The script reads link annotations from the source (PDF `/Annot /Link`, DOCX `w:hyperlink`, XLSX `cell.hyperlink`, PPTX `a:hlinkClick` external URIs) and rewrites the cache so anchor-text spans carry `[anchor](url)` inline. Every link is preserved verbatim — external URIs and internal anchors (e.g. Confluence same-page `#Heading(SRA)`) both round-trip — because the downstream export path may push the markdown back to Confluence where same-page anchors re-bind.

**PPTX scope limitation (v23.0)**: only external URIs (`a:hlinkClick` with address) are captured. Intra-deck slide jumps (`a:hlinkClick action="ppaction://hlinksldjump"`) are NOT extracted — python-pptx's `_Hyperlink` does not expose them, and resolving slide IDs requires raw XML walking. Decks rarely use intra-deck jumps as traceability edges (Confluence/Figma/Jira links dominate), but if a deck relies on them, flag `LINK-PPTX-INTERNAL-JUMP` in Phase 7 and treat as an edge case.

The script emits a one-line summary to stdout. The `kinds=[...]` labels vary per format:
- PDF: `found=N unique=M spliced=K kinds=[URI=N, GOTO=N, NAMED=N]` (unique reflects per-page dedup of redundant annotations)
- DOCX: `found=N spliced=K kinds=[external=N, internal=N, broken=N]`
- XLSX: `found=N spliced=K kinds=[external=N, internal=N]`
- PPTX: `found=N spliced=K kinds=[external=N]`

Record this line in the staging log for Phase 7 validation. See task ben/086 and `splice_hyperlinks.py` docstring for algorithm details (longest-anchor-first with protected-regions; cross-format `(anchor, url) -> requested_count` aggregation for correct multiplicity and tight idempotency; URL-encoding of `)` to `%29` for safe round-trip of URLs containing literal parens).

**All subsequent phases read the cache** rather than re-invoking `pdftotext` / Claude Read on the source:
- Phase 3 (structuring): reads cache.
- Phase 5a (template inference): reads cache for body scan.
- Phase 5b (SOP/WI inference): reads cache.
- Phase 5e (requirements metadata): reads cache for per-requirement attribute + AC extraction.

**When Claude `Read` of the source is still required** (image-heavy PDFs where layout matters, diagrams, scanned docs): pair it with `Read` on the cache too — do NOT re-shell `pdftotext`. The cache is the single source of truth for text; Claude `Read` is the supplement for visual-layout reasoning only.

**Staging cache is ephemeral** — Phase 9 Step 9 (`rm -rf "{{STAGING_DIR}}"`) removes it. Do not persist the cache into the DHF folder.

### Phase 5a: Template Inference

Infer `template_of` — the QMS form/template this document instantiates.

1. **Load candidate templates**: enumerate every `.md` file in `{{FORMS_INDEX_PATH}}`. Parse YAML frontmatter for `title`, `doc_id`. Collect H1 and H2 headings from the body.

2. **Apply priority heuristics** (first match wins):

   | Priority | Heuristic | Confidence |
   |----------|-----------|------------|
   | 1 | **Title-exact**: TITLE (from Phase 0) equals a template's `title` (case-insensitive, whitespace-normalized, generic suffix tokens stop-worded) | `high` |
   | 2 | **Explicit reference**: doc body contains `"per FORM-\d+"`, `"FORM-\d+ template"`, or cites the form in a revision history row | `high` |
   | 3 | **Heading-structure match**: the adopted doc's H1/H2 set overlaps ≥ 70% with a template's heading set (Jaccard similarity on normalized heading strings) | `medium` |
   | 4 | **Title-fuzzy**: token-set ratio ≥ 0.8 between TITLE and a template's `title` AFTER stop-wording generic tokens (`Plan`, `Form`, `Template`, `Form for`, `Procedure`) | `low` |
   | 5 | No match above 0.6 similarity | `null` (no match) |

   **Stop-word rationale**: titles ending in `Plan` / `Form` / `Template` produce noisy fuzzy matches because the suffix dominates similarity. Stop-wording before scoring gives more signal on the distinguishing words.

3. **Populate `template_of`**:
   ```yaml
   template_of:
     doc_id: "FORM-XXX"          # Or null if no match
     title: "<matched template title>"
     template_version: null       # Future — to be filled when templates carry version metadata
     inferred: true
     confidence: "high|medium|low|null"
     match_basis: "title-exact|title-fuzzy|heading-structure|explicit-ref"
   ```

4. **Populate `template_hints`** when `confidence` is `medium`, `low`, or `null`: up to 3 candidates sorted by similarity score, each with a `reason` string (scoring details). If no candidates cross 0.4 similarity, `template_hints: []`.

5. **If `template_of.doc_id` is null**, append to `notes:` a clearly-detectable line: `"template_of could not be auto-inferred — manual review required"`. Future validation check matches on `template.*not.*inferred|manual review`.

### Phase 5b: SOP + WI Inference

Infer `authored_per` — process artifacts (SOPs AND Work Instructions) governing this document's creation/review.

**CRITICAL**: MedTech Company's QMS uses Work Instructions (`WI-\d+`) as the primary process-governance artifact for software development. Many DHF docs cite WIs with zero SOP references. **You MUST scan both `SOP-\d+` AND `WI-\d+` patterns.** Populating only SOPs on a WI-governed doc is a silent-failure bug.

1. **Scan body**: regexes `\bSOP-\d+\b` AND `\bWI-\d+\b`. Record each match + ~200 chars of surrounding context. Dedupe identical doc-ids.

2. **Classify by context**:

   | Context | Classification |
   |---------|----------------|
   | Match under "Governing Procedures" / "Applicable SOPs" / "Applicable Work Instructions" / "Standards" / "References" heading, OR in a Revision History row | `authored_per[]` `confidence: high` |
   | Match in an Appendix binding references to process elements (SDP's Appendix C style) | `authored_per[]` `confidence: high` |
   | Match in a footer-like location (last ~200 chars of a page) | `authored_per[]` `confidence: medium` |
   | Match in passing prose | `authored_per_hints[]` |

3. **Resolve each match**:
   - `SOP-\d+` → `{{SOPS_INDEX_PATH}}`
   - `WI-\d+` → `{{WIS_INDEX_PATH}}`
   - Extract `title` from resolved file's frontmatter; if file absent, leave `title: null` and set `note: "not in source-md — reference only"`.

4. **Populate** with `doc_type: "SOP"` or `"WI"` per entry. Empty lists are valid if nothing found after scanning BOTH patterns.

### Phase 5c: Filing Composition

Populate `filings[]` — inverse index of submissions including this doc.

For each manifest in `{{MANIFEST_PATHS}}`: grep for the working MD path (`<TITLE_STEM>.md`) OR the formal path (`formal/<TITLE_STEM>.<ext>`) OR legacy paths (the original unrenamed SOURCE_PATH filename — manifests may reference pre-migration names). If any form matches, append the filing slug (`qsub`, `510k`, `pccp` — from manifest's parent folder) to `filings[]`.

Empty `filings: []` is honest — the doc may not yet be assigned. A separate `/docflow validate --orphans` check will flag docs in `formal/` not cited by any manifest.

### Phase 5d: Version Lineage Seeding

Build the initial `version_lineage` entries reflecting the two-format state after adopt:

```yaml
version_lineage:
  - doc_version: "{{normalized doc_version}}"
    doc_version_raw: "{{raw extracted string}}"
    lifecycle: "formal"
    format: "{{FORMAT}}"
    path: "formal/{{TITLE_STEM}}.{{FORMAT}}"
    event: "original"
    date: "{{today YYYY-MM-DD}}"
  - doc_version: "{{normalized doc_version}}"
    doc_version_raw: "{{raw extracted string}}"
    lifecycle: "draft"
    format: "md"
    path: "{{TITLE_STEM}}.md"
    event: "adopt"
    date: "{{today YYYY-MM-DD}}"
```

Both entries share the same `doc_version` — they represent the same version in two formats/lifecycles. The formal is the released binary; the draft is the working MD authored from it.

For override-merge (see below), additional entries append reflecting the prior version's obsoletion and the new version's adopt-merge event.

### Phase 5e: Requirements-Doc Metadata Inference (NEW — only when `doc_type: requirement`)

For requirement documents (SRS, FRS, NFRS, URS), populate R1 per-requirement metadata. Skip this phase for other doc types.

**Prerequisite reading**:
- `.claude/skills/docflow/agents/converter.md` sections R1a–R1g (structural convention)
- `.claude/skills/docflow/references/classification-taxonomy.md` (canonical classification tags + regex patterns)

**Inputs**: the structured markdown from Phase 3 should have one `#### <Key> — <Summary>` heading per requirement, each followed by a detail block (attribute rows + AC rows) in whatever shape pandoc/source extraction produced. Phase 5e restructures these into the R1 two-table shape and populates inferred metadata.

**For each requirement**:

1. **Extract source fields**:
   - Key (verbatim from source — the identifier used in the heading)
   - Summary (from source — goes into the heading after the em-dash)
   - Epic Link / Parent / Feature Group (source field name varies — use whichever the source provides)
   - Fix Version / Target Release (source field name varies)
   - Description (user story / requirement text)
   - Acceptance Criteria (per-AC bodies)

2. **Derive Traces To**:
   - If Epic Link matches `^(DI-\d+|UN-\d+)` prefix: extract the matched ID as Traces To; flag the resolvable parent
   - If no prefix match: Traces To = `*(none — manual trace)*` flagged for human review
   - If Epic Link is empty: Traces To = `*(none)*`

3. **Derive Epic**:
   - Value = Epic Link verbatim from source (do NOT normalize, do NOT keyword-infer)
   - If source Epic Link is empty: `*(none — flag for review)*`

4. **Derive Classification** (multi-valued):
   - Scan Description + AC body text with the canonical regex patterns (from `references/classification-taxonomy.md`)
   - All matches apply (multi-valued)
   - Always include `functional` as baseline
   - Emit as comma-separated list with `*(inferred)*` suffix: `` `functional`, `safety` *(inferred)* ``
   - Confidence: `high` (patterns are definitional)

4b. **Derive Criticality (CtX) per-AC + Description row** — Criticality lives in the detail table (not the attributes table per v20), one CtX assessment per row (Description row + each AC row). Per glossary.md "Criticality Tags":
   - **Per-AC inference**: for each AC, run the Classification regex patterns against ONLY that AC's GIVEN/WHEN/THEN text (not the whole requirement's text). Each AC is a discrete use-flow with its own IFU dependencies — a single requirement can have ACs with different CtX tags.
   - **Conservative mapping** per AC:
     - `safety` class (regex match on AC text) → `CtS` (inferred)
     - `regulatory` class → `CtC` (inferred)
     - `performance` class → `CtP` (inferred)
     - **`CtF` is NEVER auto-inferred** — functional classification doesn't mean critical to IFU. Human assesses per-AC against the IFU.
   - **Empty CtX for an AC** (no regex matches, no safety/regulatory/performance signals): emit `` `none` (inferred) `` with an inline rationale explaining why no CtX was derived and what candidate tags a human should consider.
   - **Description row Criticality** = union of all AC CtX tags at adopt time. If ANY AC's CtX was inferred, Description row inherits `(inferred)` on its union. This gives dashboards a req-level rollup from day one; human may refine.
   - **Inline rationale for inferred cells**: include reasoning beneath the tag(s) on a `<br>`-separated line in italics. Example:
     ```
     `CtF`, `CtS` (inferred)<br>_Depth analysis influences surgical planning (CtS); core 3D reconstruction (CtF)._
     ```
     or for `none`:
     ```
     `none` (inferred)<br>_No regex match. Candidate: CtF if foundational to IFU visualization; else nice-to-have._
     ```
     Rationale makes the agent's reasoning auditable. Human removes rationale (and `(inferred)` suffix) once CtX is confirmed.
   - Label convention (lowercase, soft; no italics around `(inferred)`; `none` wrapped in backticks for visual parity with CtX tags):
     - `` `CtF`, `CtS` `` — human-confirmed (no suffix)
     - `` `CtF`, `CtS` `` `(inferred)` — auto-derived
     - `` `none` `` `(inferred)` — agent couldn't determine. Backticked so `none` sits in the same grey inline-code channel as `` `CtS` ``, `` `CtP` ``, etc. (v21 change from v20's plain-text `none`).
   - Confidence: `medium` on inference. Stabilize on human confirmation (removal of `(inferred)` suffix + rationale line).

5. **Derive Target**:
   - If source has `Fix Version` / `Target Release` field: use value
   - Else: `unassigned`
   - Normalize to `v1` / `v2` / `future` / `unassigned` if source uses free-form strings

6. **Set Status**:
   - Default `proposed` at adoption
   - Human-curated lifecycle; adopter never changes after initial set

7. **Emit per R1a v22 shape** (markdown attributes table + **inline HTML detail table** with `<colgroup>` widths 10%/60%/30%; per-AC Criticality; Value column precedes Criticality per v21 column order; **Value cell follows R1e v22 rules**: bold the user-story keywords (`AS A` / `GIVEN THAT` / `GIVEN` / `I WANT` / `SO THAT` / `WHEN` / `THEN` / `AND` / `BUT` / `IF` / `ELSE`), one clause per `<br>`-separated line, multi-bullet lists rendered with `<br>• <item>` per bullet on its own line, **nested sub-tables rendered as inline HTML `<table>` blocks inside the Value `<td>`** (NOT bullet rows with `·` separators — see converter R1e for the worked example). Markdown content inside HTML `<td>` requires blank-line separation from `<td>` tags per GFM. Links preserved verbatim per R1e):
   ```markdown
   #### <Key> — <Summary>

   | Key | Traces To | Epic | Classification | Target | Status |
   |-----|-----------|------|----------------|--------|--------|
   | <Key> | <Traces To or `null`> | `<Epic>` | `<class-tags>` (inferred) | `<target>` | `<status>` |

   | Field | Value | Criticality |
   |-------|-------|-------------|
   | Description | <verbatim description — preserve `[text](url)` links> | `<union-CtX>` (inferred)<br>_<union rationale>_ |
   | AC1: <name> | <AC content with nested flattening per R1e; preserve links> | `<per-AC-CtX>` (inferred)<br>_<per-AC rationale>_ |
   | AC2: <name> | <...> | `<per-AC-CtX>` (inferred)<br>_<rationale>_ OR `` `none` `` (inferred)<br>_<why none + candidate>_ |

   **Notes**: —
   ```
   
   **Label format**:
   - Traces To: inline-code ID (`` `DI-0013` ``) OR literal `null` (plain text) when no prefix match
   - Epic: inline-code verbatim (`` `VIEW 3D RECONSTRUCTION` ``) OR literal `null` when empty in source
   - Classification cell: comma-separated inline-code + `(inferred)` suffix (lowercase, plain parens)
   - Criticality cell: comma-separated inline-code CtX + `(inferred)` suffix + `<br>_rationale in italics._`
   - `` `none` `` `(inferred)` when no CtX could be determined — followed by `<br>_rationale + candidate CtX._` (v21: `none` is backticked for visual parity with CtX tags)

8. **User override stability**: if this is a re-adopt and the existing MD already has R1 shape with human-edited values (detectable by absence of `*(inferred)*` suffix on Classification), preserve the human values. Only populate fields that are null or still `*(inferred)*`.

**Document-wide aggregate** (for Phase 6 frontmatter): after all requirements are emitted, compute:
- `count`: total number of requirements
- `epics`: map of Epic value → count
- `classification`: map of tag → count (count occurrences, not unique reqs; a req with 3 tags contributes 3 counts)
- `criticality`: map of CtX tag → count, plus `none` for reqs with empty Criticality. Multi-valued (a req with `CtF, CtS` contributes to both). Counts occurrences, not unique reqs.
- `target_releases`: map of target value → count
- `traces_to.resolved` / `traces_to.unresolved`: counts by whether DI-/UN- prefix matched
- `status`: map of status value → count

These aggregates go in `frontmatter.requirements:` (see Phase 6 schema).

### Phase 6: Build Frontmatter

Read `.claude/skills/docflow/templates/frontmatter-project.md` — populate **every** field per the schema.

**Auto-populated fields**:
- `title`: from Phase 0.1 (TITLE_STEM with any sanitization reversed for display)
- `docflow_version`: read the `version:` field from `.claude/skills/docflow/SKILL.md` frontmatter and stamp it verbatim (e.g. `"v21"`). This lets Phase 0.4 short-circuit on subsequent runs when the spec hasn't changed (Optimization A). On SPEC-ROLL-FORWARD the existing value is overwritten with the new spec version after the Phase 5e rewrite completes.
- `doc_type`: heuristic from DHF_AREA (`user-needs` → `user-need`, `plans` → `plan`, `requirements` → `requirement`, etc.) plus content inspection
- `dhf`, `dhf_role`, `dhf_area`: from parameters
- `status`: `"draft"`
- `lifecycle`: `"draft"` (working MD is always draft)
- `owner`: `"TBD — author to populate"`
- `last_modified`: today
- `doc_version`: normalized form from Phase 0.2 (e.g. `"v30"`)
- `release_version`: captured in Phase 0.1 if title had an embedded product-release version (e.g. `"1.0.0"`); else null
- `source_formal`: `formal/<TITLE_STEM>.<FORMAT>` (relpath from working MD's folder)
- `target_formal`: same as `source_formal` by default (export overwrites)
- `conversion_date`, `conversion_method`, `conversion_fidelity`, `pages`/`sheets`/`slides`, `has_images`, `image_count`, `has_tables`, `has_form_fields`: per converter Phase 6 rules
- `has_hyperlinks` (v29+): `true` iff the Phase 2 splice summary line reported any spliced links (`spliced > 0`). Stored as boolean.
- `hyperlink_count` (v29+): final count of `[text](url)` spans in the rendered working MD body — `grep -oE '\[[^]]+\]\([^)]+\)' OUTPUT_PATH | wc -l` after Phase 8 commit. This is the post-restructuring count, not the Phase 2 splice count, so it reflects what survived the pipeline (which is what matters for downstream dashboards).
- `template_of` + `template_hints`: from Phase 5a
- `authored_per` + `authored_per_hints`: from Phase 5b
- `filings`: from Phase 5c
- `version_lineage`: from Phase 5d
- `references`: from cross-ref resolution in Phase 5
- `conversion_history`: single entry with today's date and `"Initial adoption from formal at doc_version {{doc_version}}"`
- `notes`: include inference warnings (5a/5b) + conversion-fidelity notes

### Phase 7: Self-Validate

Run converter-Phase-7 checks (structural, image, page-marker, content), **plus** these adopt-specific checks:

| Check | How | Required? |
|-------|-----|-----------|
| `source_formal` resolves | `test -f {{DHF_AREA_DIR}}/<source_formal>` (after Phase 8 rename) | Yes |
| `target_formal` parent folder exists | `test -d $(dirname {{DHF_AREA_DIR}}/<target_formal>)` | Yes |
| `version_lineage` has ≥ 2 entries ending in event `adopt` | Last entry event is `adopt`, `lifecycle: draft`, `format: md` | Yes |
| `doc_version` normalized (no dot, lowercase `v`) | Regex `^v\d+$` | Yes |
| `doc_version` present in filename of neither formal nor working | Filenames should be `<TITLE>.md` / `<TITLE>.<ext>` — **no `-v\d+` suffix** | Yes |
| No `- Draft` suffix in filename | Redundant with folder location; frontmatter `lifecycle: draft` is the marker | Yes |
| Image path prefix is `images/` | Grep all `![...](...)` refs; each must start with `images/` | Yes |
| `template_of` inferred or flagged in notes | Either `template_of.doc_id` set with `confidence`, OR `notes:` matches `template.*not.*inferred\|manual review` | Warning |
| `dhf` + `dhf_area` match output path | Parse OUTPUT_PATH; verify frontmatter matches | Yes |
| No collision with existing working MD | `test ! -f OUTPUT_PATH` before committing (skill pre-checked; re-verify) | Yes |
| **Link-count floor (v29+)** | Compare body link count `B = grep -oE '\[[^]]+\]\([^)]+\)' OUTPUT_PATH \| wc -l` against the Phase 2 splice summary's `spliced=K` value. If `B >= K * 0.9` → pass. If `0.5 * K <= B < 0.9 * K` → **Warning** (some links lost during restructuring; reviewer should investigate which). If `B < 0.5 * K` → **Required failure** (catastrophic link loss; abort with `LINK-COUNT-FAILED.txt` in staging). When `K = 0` (source had no hyperlinks), check passes vacuously. | Yes / Warning / Required (graduated) |
| **`has_hyperlinks` + `hyperlink_count` consistency (v29+)** | If `hyperlink_count > 0` then `has_hyperlinks: true`; if `hyperlink_count == 0` then `has_hyperlinks: false`. Mismatch → Required failure. | Yes |

### Phase 8: Commit — Transactional + Parent README Re-render

Transactional sequence (all-or-nothing; abort leaves staging intact with a marker file):

```
Step 1: mkdir targets
  mkdir -p "{{DHF_AREA_DIR}}/formal"
  mkdir -p "{{DHF_AREA_DIR}}"
  # Only mkdir images/ if we actually have content images to place
  if [ "$(ls {{STAGING_DIR}}/images/ 2>/dev/null)" ]; then
      mkdir -p "{{DHF_AREA_DIR}}/images"
  fi

Step 2: git-mv the formal to its new name (title-based, no version suffix)
  git mv "{{SOURCE_PATH}}" "{{DHF_AREA_DIR}}/formal/{{TITLE_STEM}}.{{FORMAT}}"
  # Skip this step entirely if SOURCE_PATH already equals the target (no rename needed)

Step 3: Move images FIRST (images must exist before markdown references them)
  For each file X in {{STAGING_DIR}}/images/:
    mv "{{STAGING_DIR}}/images/X" "{{DHF_AREA_DIR}}/images/X"

Step 4: Verify every image arrived
  test -f "{{DHF_AREA_DIR}}/images/X" for each expected X
  On fail → abort, write COMMIT_FAILED.txt

Step 5: Verify every markdown image ref resolves from OUTPUT_PATH
  For each ![...](images/X.png) in the markdown:
    test -f "{{DHF_AREA_DIR}}/images/X.png"
  On fail → abort

Step 6: Move working MD
  mv "{{STAGING_DIR}}/<TITLE_STEM>.md" "{{DHF_AREA_DIR}}/{{TITLE_STEM}}.md"

Step 7: Verify working MD arrived
  test -f "{{DHF_AREA_DIR}}/{{TITLE_STEM}}.md"

Step 8: Re-render parent README sentinel blocks (non-blocking)
  parent_dir = "{{DHF_AREA_DIR}}"
  if [ -f "$parent_dir/README.md" ]; then
      python3 .claude/skills/medtech-docs/scripts/render-sentinels.py "$parent_dir/README.md" || true
  fi
  grandparent = $(dirname "$parent_dir")
  if [ -f "$grandparent/README.md" ]; then
      python3 .claude/skills/medtech-docs/scripts/render-sentinels.py "$grandparent/README.md" || true
  fi

Step 9: Clean up staging
  rm -rf "{{STAGING_DIR}}"
```

On any Phase 7 Required failure → leave staging, write `VALIDATION_FAILED.txt`, return FAILURE.
On any Phase 8 step failure → leave staging, write `COMMIT_FAILED.txt` documenting which step failed and filesystem state.

### Phase 9: Auto-chained review (v28+) — F11 Mermaid supplement audit

**Rationale**: single-pass Mermaid emission in Phase 4.7 has an empirical ~90% miss rate per-doc, surfaced in task ben/087 after the retroactive sweep of task 086 Batch 1+2 re-adopts. F11 is a long rule inherited by reference, flagged Warning-only in Phase 7, and self-reported without observability. The reviewer agent — with a narrower scope and a single job — catches gaps the adopter misses. Making the review pass automatic (not opt-in) closes the gap at adopt-time rather than relying on a separate human-initiated review step that frequently never runs.

**After Phase 8 commits successfully**, chain the reviewer automatically:

```
Step 1: Skip if the adopt set --no-review, OR if the final MD has zero content images
  • parse frontmatter: if image_count == 0 AND has_images == false, skip Phase 9
  • if agent invoked with --no-review flag, skip Phase 9 (caller is running review externally)

Step 2: Spawn the reviewer agent, scoped to --mermaid-only --fix
  • Target: {{DHF_AREA_DIR}}/{{TITLE_STEM}}.md
  • Read agents/reviewer.md for the full spec
  • MODE=fix SCOPE=mermaid-only
  • The reviewer enumerates every content image, classifies per F11a, constructs a Mermaid
    supplement for types (a)(b)(c) where one is missing, flags ambiguous classifications
    with `%% REVIEW: MERMAID-CLASSIFY-AMBIGUOUS — ...`. Skips type (d) matrices and
    (e) screenshots.

Step 3: Collect reviewer report
  • Append a one-line summary to the working MD's frontmatter conversion_history:
    { date: ..., event: "auto-review", scope: "mermaid-only", mermaid_added: N, flagged: K }
  • If reviewer flagged issues with %% REVIEW: comments, surface them in the adopt final
    report — these are gaps the human needs to resolve manually.

Step 4: Non-blocking on reviewer failure
  • If the reviewer agent returns an error, log it but do not abort the adopt — the
    working MD is already committed and the adopt is successful. Emit a
    `REVIEW_PHASE_FAILED` entry in the report.
```

**Skip conditions** (Phase 9 no-op):
- Adopter invoked with `--no-review` flag (caller will run review separately)
- Final MD has `image_count: 0` and `has_images: false` (nothing for F11 to audit)
- `SCOPE=frontmatter-only` or any other lite-mode is in force

**Not a replacement for `/docflow review <file>`** — full review (non-mermaid scope) still requires an explicit invocation. Phase 9 specifically closes the Mermaid-emission reliability gap.

## Override-merge mode (STUB — full impl pending real upgrade scenario)

When Phase 0.4 detects OVERRIDE-MERGE (existing working MD with lower `doc_version` than the new formal drop), you perform a **3-way merge** between:

- **base** = the PRIOR formal (still on disk at `{{DHF_AREA_DIR}}/formal/<TITLE_STEM>.<ext>` — has NOT been overridden yet) re-converted to markdown
- **draft** = the current working MD (`{{DHF_AREA_DIR}}/<TITLE_STEM>.md`) — base + author's edits
- **new** = the new formal ({{SOURCE_PATH}}) converted to markdown

**Merge algorithm** (section-aware, H2/H3 as boundaries):

| base | draft | new | Outcome |
|------|-------|-----|---------|
| X | X | X | No change — use X |
| X | X | Y | Only formal changed → use Y (accept) |
| X | Y | X | Only author changed → use Y (preserve) |
| X | Y | Y | Parallel same change → use Y |
| X | Y | Z | **CONFLICT** — emit both with sentinels |
| absent | present | absent | Author-added section → keep |
| absent | absent | present | New-formal-added section → insert |
| present | present | absent | Formal removed; if author edited, CONFLICT; else remove |

**Conflict sentinel format**:

```markdown
<!-- CONFLICT: v<old>→v<new> formal changed this section AND your v<old> draft had edits -->
<!-- === DRAFT (your edits on v<old> base) === -->

<draft version>

<!-- === NEW FORMAL (from v<new>) === -->

<new-formal version>

<!-- === END CONFLICT === -->
```

**Frontmatter on override-merge**:
- Content-derived (`conversion_*`, `pages`, `has_*`): use NEW
- Inference (`template_of`, `authored_per`, `template_hints`, `authored_per_hints`): RE-RUN on merged body (don't carry forward stale confidence)
- Human-authored (`owner`, `status`, `notes`): carry forward; append `"Override-merged v<old>→v<new> on {date}; N conflicts, see in-body CONFLICT markers"` to notes
- `doc_version`: update to new version
- `version_lineage`: append 2 entries (`event: obsoleted` on old draft, `event: override-merge` on new draft); old formal's `original` entry stays

**Commit on override-merge**: the old formal is `git rm`'d from working tree (preserved in git history), new formal is `git add`'d at `<TITLE_STEM>.<ext>`, working MD is overwritten with merged body.

**STATUS OF THIS SECTION**: design-captured. Full implementation pending a real upgrade scenario to exercise. Today's adopter runs treat OVERRIDE-MERGE as **failure with manual-instruction message**: `"OVERRIDE-MERGE detected (v<old> → v<new>). The merge workflow is not yet implemented. Options: (a) git rm the old formal, move aside the old working MD, then re-run adopt for fresh FRESH ADOPT; (b) wait for merge impl in task [TBD]."`

## Output

```
RESULT: SUCCESS | FAILURE

Document: <title>
DHF:      <dhf> / <dhf_area>
Version:  <doc_version>  (raw: <doc_version_raw>)
Release:  <release_version>  (if applicable)

Paths:
  Working MD:    <OUTPUT_PATH>
  Current formal: <NEW_FORMAL_PATH>
  Renamed from:  <SOURCE_PATH>  (if different)

Extraction (Phase 0):
  Title source:       <cover-page | pdf-metadata | body-h1 | filename>
  Version source:     <rev-history | header-footer | cover | metadata | body-scan | user-override>

Content:
  Sections: N
  Tables:   N
  Images:   N extracted, N decorative omitted

Inference:
  template_of:   <doc_id> (confidence: <level>, basis: <basis>)  OR  "not inferred — N hints"  OR  "no candidates"
  authored_per:  [<doc_id>, ...] (N high, M medium; N_sops SOPs, N_wis WIs)
  filings:       [<filing>, ...]  OR  "[] — not yet in any manifest"

Cross-references:
  Resolved:   N
  Unresolved: N

Quality:
  Required checks: N/N passed
  Warnings:        N

README sentinels: <list of re-rendered paths, or "none with sentinel blocks">

Notes:
  - <conversion notes, inference warnings>
```
