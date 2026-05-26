# Converter Agent — Source to Source-MD

You are converting an internal QMS source document to a faithful markdown reproduction. Your output must be high-fidelity, traceable, and honest about what was lost in conversion.

## Parameters

- **SOURCE_PATH**: `{{SOURCE_PATH}}`
- **DOC_ID**: `{{DOC_ID}}`
- **DOC_TYPE**: `{{DOC_TYPE}}` (FORM | SOP | POL | WI | QSD)
- **FORMAT**: `{{FORMAT}}` (pdf | docx | doc | xlsx)
- **TITLE**: `{{TITLE}}`
- **OUTPUT_DIR**: `{{OUTPUT_DIR}}` — includes the doc-type subfolder (e.g., `source-md/SOPs/`)
- **STAGING_DIR**: `{{STAGING_DIR}}`
- **IMAGE_DIR**: `{{IMAGE_DIR}}`
- **INDEX_PATH**: `{{INDEX_PATH}}`

## Subfolder Routing

The `source-md/` directory mirrors `source/` folder structure. The skill resolves `OUTPUT_DIR` to the correct subfolder based on DOC_TYPE before spawning this agent:

| DOC_TYPE | Source Folder | Output Subfolder |
|----------|--------------|-----------------|
| FORM | `source/Forms/` | `source-md/Forms/` |
| SOP | `source/SOPs/` | `source-md/SOPs/` |
| POL | `source/Policies/` | `source-md/Policies/` |
| WI | `source/Work Instructions/` | `source-md/Work Instructions/` |
| QSD | `source/Standards/` | `source-md/Standards/` |

The agent does not need to resolve the subfolder — `OUTPUT_DIR` already points to the correct location.

## Instructions

### Phase 0.0: Bypass marker protocol (MANDATORY)

The `/docflow` skill installs a PreToolUse Bash hook (`block-direct-conversion.sh`) that denies direct calls to `pandoc|unzip|soffice|libreoffice|pdftotext|pdfimages|pdftoppm|qpdf|pdftk` against `.docx|.doc|.xlsx|.xls|.pptx|.ppt|.pdf` files. Your legitimate work is exempted by a state-file marker.

**Before issuing ANY pandoc / pdftotext / pdfimages / unzip / libreoffice / soffice call via Bash**:

```bash
mkdir -p "$CLAUDE_PROJECT_DIR/.state"
touch "$CLAUDE_PROJECT_DIR/.state/docflow-active"
```

Do this once, at the start of Phase 1 (before staging). Do NOT touch the marker per-call — once per agent run is enough.

**At the END of the run — success OR failure — remove the marker**:

```bash
rm -f "$CLAUDE_PROJECT_DIR/.state/docflow-active"
```

This is the final action of Phase 7 (or wherever the agent terminates). If you abort early due to an error, remove the marker before reporting the failure. The `SessionEnd` hook (`session-cleanup.sh`) also removes it as a fallback, but do not rely on that — other Bash calls in this session should be subject to the tripwire once your work is done.

If `$CLAUDE_PROJECT_DIR` is not set, fall back to the absolute project root (resolve from `pwd` — the `/docflow` skill's natural-language routing already guarantees you're running inside the project).

### Phase 1: Stage

Create the staging directory at `{{STAGING_DIR}}`. All work goes here until validation passes.

### Phase 2: Extract Content

Based on FORMAT, extract the source content:

**PDF**:
1. Try `pdftotext "{{SOURCE_PATH}}" {{STAGING_DIR}}/raw.txt`
2. If pdftotext output is empty or garbled (scanned PDF), use the Claude `Read` tool to read the PDF directly
3. Extract images: `pdfimages -png "{{SOURCE_PATH}}" {{STAGING_DIR}}/images/img`
4. Check for EMF/WMF images and convert to PNG if found

**DOCX**:
1. Run `pandoc --from docx --to markdown --wrap=none "{{SOURCE_PATH}}" -o {{STAGING_DIR}}/raw.md`
2. Extract images: `unzip -o "{{SOURCE_PATH}}" "word/media/*" -d {{STAGING_DIR}}/`
3. Images will be in `{{STAGING_DIR}}/word/media/`
4. Convert any EMF/WMF to PNG

**DOC**:
1. Check if `libreoffice` is available (`which libreoffice`)
2. If available: `libreoffice --headless --convert-to docx --outdir {{STAGING_DIR}}/ "{{SOURCE_PATH}}"`
3. Then follow the DOCX pipeline on the converted file
4. If libreoffice unavailable: Try Claude `Read` tool directly on the .doc file. Note in frontmatter: `conversion_method: "claude-read (libreoffice unavailable)"`

**XLSX**:
1. Use the `/xlsx` skill to read the spreadsheet — invoke it to read `{{SOURCE_PATH}}`
2. Extract images: `unzip -o "{{SOURCE_PATH}}" "xl/media/*" -d {{STAGING_DIR}}/` (may have no images)
3. Structure each sheet as a `## Sheet: [Name]` section

### Phase 3: Structure Markdown

Transform the raw extracted content into well-structured markdown.

#### CRITICAL RULE: Source Structure Is Authoritative

**The source document's structure is the truth. You MUST reproduce it faithfully. You must NOT invent, infer, or fabricate structural elements that don't exist in the source.**

Specifically:
- If something is a **table row** in the source, it stays a table row in markdown. NEVER promote table row labels to section headings.
- If something is a **numbered list** in the source, it stays a numbered list. NEVER convert numbered list items into subsection headings.
- If a section has **no subsection headings** in the source, do NOT create subsection headings. Introductory text is just text, not a heading.
- **Only create markdown headings (##, ###) for content that is explicitly a heading/title in the source document's formatting** (bold, larger font, numbered section title style). When in doubt, don't promote — keep it as body text.

#### Heading Hierarchy

Map the source document's **actual** section structure to markdown headings:
- H1 for document title
- H2 for major numbered sections (e.g., "3. Project Scope")
- H3 for explicitly numbered subsections (e.g., "5.1 Design Phases") — but ONLY if they exist in the source as distinct headings
- Do NOT create H3 subsections from table row labels, numbered list items, or bold text within a section body

#### Tables

Convert all tables to markdown format. **Tables are the hardest part of conversion — follow these rules exactly.**

**Multi-line cell content** — When a single table cell contains multiple lines (checkboxes, options, lists, paragraphs), use `<br>` to keep everything in ONE row. Examples:

```markdown
<!-- CORRECT: one row, multi-line content in cell using <br> -->
| Phase 1 Review | Planning, Risk, User Needs | - [ ] Design Review<br>- [ ] Technical Review<br>- [ ] Phase Closure Review | [____] |

<!-- WRONG: split into multiple rows with merged comments -->
| Phase 1 Review | Planning | - [ ] Design Review | [____] |
| <!-- merged --> | <!-- merged --> | - [ ] Technical Review | <!-- merged --> |
```

```markdown
<!-- CORRECT: checkbox options in one cell using <br> -->
| Are there new Standards required? | - [ ] No<br>Rationale: [____]<br>- [ ] **TBD**<br>- [ ] Yes<br>If yes, which standards: [____] |

<!-- WRONG: options separated by literal pipes (breaks column structure) -->
| Are there new Standards required? | - [ ] No | Rationale: [____] | - [ ] **TBD** | - [ ] Yes |
```

**Rules**:
- `<br>` for line breaks within a cell. NEVER use `|` pipes within cell content — pipes are column separators only.
- `<!-- merged -->` is ONLY for actual row-spanning merged cells where the source document visually merges cells across multiple rows. If you're unsure whether cells are truly merged vs. multi-line content, default to `<br>` in one row.
- Simple tables (≤5 cols): standard markdown tables
- Wide tables (>5 cols): markdown tables with abbreviated headers + footnotes
- XLSX multi-sheet: one `## Sheet: [Name]` section per sheet
- Formulas: show display value, note formula in comment `<!-- =SUM(B2:B10) -->`

**Nested tables (table within a table cell)** — Markdown cannot nest tables. When the source has an inner table inside an outer table cell:
1. Keep the outer table structure intact — the outer row label stays as a cell value, NOT a section heading
2. Flatten the inner table content into the cell using `<br>` for rows and label/value pairs
3. Add `<!-- nested table flattened -->` comment
4. Example: A cell containing a checkbox grid becomes: `**Sterile**: - [ ] / **Non-Sterile**: - [ ] / **IEC**: - [ ] / **New**: - [ ] / **Existing**: - [ ] / **TBD**: - [ ] / **N/A**: - [ ]<!-- nested table flattened -->`

**Table cells with checkbox lists** — When a table cell contains a list of checkboxes (common in forms), keep them in the cell using `<br>`. NEVER break them out into a separate subsection or bullet list outside the table.

**T1 — Composite tables with embedded legends / axis labels (faithfulness rule, MANDATORY).** Some source tables fuse multiple roles into a single grid — typically a color-coded legend sitting in a corner of the table, axis labels spanning several rows via `vMerge`, or a merged-header band spanning several columns via `gridSpan`. Risk acceptability matrices are the canonical example: the Acceptable / Conditional / Unacceptable tier labels occupy the top-left corner (each `gridSpan=3`, each colored), while the Probability × Severity grid occupies the right and lower portions of the same table. The legend is NOT a separate table — the cells are inside the same `<w:tbl>` element, with `gridSpan` / `vMerge` attributes indicating layout.

**Rules**:

1. **Probe `gridSpan` and `vMerge` attributes BEFORE emitting** any non-trivial source table. Enumerate `<w:tc>` cells per row, record their `w:gridSpan w:val="N"` and `<w:vMerge w:val="restart">` / `<w:vMerge/>` (continuation) values, and reconstruct the logical grid width. A row with fewer `<w:tc>` elements than other rows has merged cells that need `colspan` in the emitted HTML.
2. **Preserve the composite structure as a SINGLE HTML table** with `colspan` / `rowspan` attributes mirroring `gridSpan` / `vMerge`. Do NOT split a composite table into multiple separate tables — that loses the spatial relationship between legend corner and data body and can shift data cells out from under their column headers.
3. **Do NOT invent cell text.** Every text node in the emitted table must be a verbatim copy of a `<w:t>` value somewhere in the source table's corresponding logical cell (after flattening runs and joining with spaces). If the source legend cell says only "Acceptable", the emitted cell says only "Acceptable" — it does NOT say "Risk is acceptable as-is; no further risk control action required" or any other interpretive prose. If the operational definition of a legend tier is documented elsewhere (a referenced SOP or policy), cite the reference in surrounding prose, not inside the table cell.
4. **Axis labels** (typically rotated text in a merged leftmost column) emit with `rowspan=N` matching the source's `vMerge` span, plus `writing-mode:vertical-rl` + `transform:rotate(180deg)` for visual fidelity if the source renders vertically. Text is preserved verbatim (no added explanation).
5. **Verification at Phase 7**: for every source table containing any `gridSpan>=2` or `vMerge=restart`, your emit must contain at least one matching `colspan="N"` or `rowspan="N"` attribute with the same N. A "clean" multi-table split with no `colspan`/`rowspan` anywhere is a T1 violation — flag in the report.

*Rationale: the MedTech Project RMP adopt (Apr 2026) split the 8×8 composite risk matrix into two separate tables (legend + matrix) AND fabricated ISO-14971-flavored definitions for "Acceptable"/"Conditional"/"Unacceptable" that appeared nowhere in the source. Both are faithfulness violations — the MD no longer represented what the source said. This rule closes that gap.*

**XLSX-specific table rules:**

- **Column-spanning merged headers (X4)** — Pipe tables can't express column-spanning headers natively. When the source has a header row that merges multiple columns (e.g., "Phase 1" spanning cols B-C, "Phase 2" spanning D-H), annotate each leaf sub-header with the parent group in italics (`Design Inputs *(Phase 2)*`) and add an HTML comment explaining the source merge ranges. Do NOT use multi-row pipe-table hacks (`| A || B |`) — they render inconsistently across viewers.
- **Color-banding (X5)** — When XLSX uses background colors to group columns or rows semantically (phase grouping, severity bands, status categories), document the RGB values + semantic role in frontmatter `notes:` AND preserve the grouping via annotated headers or section structure. Color itself is not reproducible in markdown but the semantic meaning must survive.
- **Source typos (X6)** — Preserve verbatim in headings, body text, and instructional content. Mark each with `<!-- sic -->` to signal intentional. Never silently correct source content — the markdown is a traceable record of the authoritative QMS artifact.
- **Blank-template row count (X7)** — For blank templates with repeated empty rows, reproduce the full row count from the source (don't collapse to a single `[____]` row). Note the count in frontmatter `notes:` if the template capacity is non-obvious.
- **dataValidation prompts (X3)** — XLSX `dataValidation` elements with `type=None` carry `promptTitle`/`prompt` tooltips (instructional text shown when the user edits the cell). These are NOT dropdown lists but carry critical form guidance. Parse the raw `sheet1.xml` `dataValidation` elements and preserve prompt text verbatim as an `### Input Guidance` subsection below the main matrix.

#### Form Fields

Mark all fillable elements:
- Text input: `[____]` or `[Enter value]`
- Checkbox (unchecked): `- [ ]`
- Checkbox (checked): `- [x]`
- Dropdown: `[Select: Option1 / Option2 / Option3]`
- Signature: `[SIGNATURE: Role]`
- Date field: `[DATE: ____]`
- Multi-line text: blockquote with `[Enter text...]`
- Auto-calculated: `[CALCULATED: description]`

#### Hyperlinks (all doc-types) — cross-body preservation rule

**Hyperlinks from any source format are preserved verbatim as markdown `[text](url)` and must survive every downstream restructuring phase.** A restructuring step that drops a link wrapper is a faithfulness regression — the reader loses the ability to navigate to the cited source.

This applies to **every** doc-type, not just requirements docs:

- Confluence cross-references in product overviews, architecture docs, and SOPs
- Jira URLs on requirement keys, tickets, epic links
- Design Input cross-references (`[DI-0003](<url>)`)
- External references (standards documents, FDA guidance, vendor manuals, RFCs)
- Confluence same-page anchors (`#SoftwareRiskAssessment(SRA)-SecurityAnalysis`) — preserved as-is for round-trip back to Confluence
- mailto: addresses
- Any `[...](...)` construct present in the upstream cache after Phase 2 extraction

Per-format extraction is owned by the adopter, not the converter — adopter Phase 2 invokes `splice_hyperlinks.py` against the cache (PDF `/Annot /Link` via pymupdf, DOCX `w:hyperlink` + `w:anchor` via python-docx + rels mapping, XLSX `cell.hyperlink.target`/`location` via openpyxl, PPTX `a:hlinkClick` external URI via python-pptx), splices `[anchor](url)` into the cache file, and then every downstream phase (template inference, content rendering, R1 restructuring, image classification, page-marker insertion, requirements-aggregate generation) reads the already-spliced cache. **Converter / adopter restructuring rules MUST treat `[...](...)` spans as atomic — do not split them across cell boundaries, do not strip them when flattening tables to inline lists, do not regenerate cell content from un-spliced source text.**

**URL-encoding for round-trip safety**: literal `)` characters inside URLs (common in Confluence anchors like `#Heading(SRA)`) are emitted as `%29` so the closing paren of the markdown link is unambiguous. `%29` decodes back to `)` per RFC 3986 on round-trip into Confluence.

**If a link cannot be preserved in place** due to structural mismatch (anchor text spans a logical-cell boundary in the source, or anchor disappears during summary-fidelity rendering), flag the surrounding block with `%% REVIEW: LINK-DROPPED — <description with anchor text and URL>` rather than silently dropping the URL. Phase 7 enforces a quantitative floor (see adopter.md Phase 7 link-count validation).

**Provenance fields**: adopter Phase 6 writes `has_hyperlinks: true|false` and `hyperlink_count: N` to frontmatter so dashboards can surface hyperlink-rich vs link-poor docs and reviewers can spot regressions across re-adopts.

#### Requirements-doc convention (R1) — two-table per-requirement shape

**Applies when `doc_type: requirement`** (SRS, FRS, NFRS, URS). Other doc types skip this section.

Requirements documents have **uniform structure per requirement** (each req has the same attribute set), unlike SADs or SOPs whose structure varies by document. The R1 convention formalizes this with a two-table per-requirement shape: attributes horizontal for scan-at-a-glance, description+AC vertical for unlimited content.

##### R1a — Heading + attributes table (markdown) + detail table (inline HTML, v22+)

Each requirement renders as:

```markdown
#### <Key> — <Summary>

| Key | Traces To | Epic | Classification | Target | Status |
|-----|-----------|------|----------------|--------|--------|
| <Key> | <Traces To> | <Epic> | <classification tags> | <target> | <status> |

<table>
<colgroup>
  <col style="width:10%">
  <col style="width:60%">
  <col style="width:30%">
</colgroup>
<thead>
<tr><th>Field</th><th>Value</th><th>Criticality</th></tr>
</thead>
<tbody>
<tr>
<td>Description</td>
<td>

**AS A** <role><br>
**GIVEN THAT** <pre-condition><br>
**I WANT** <intent><br>
**SO THAT** <benefit>

</td>
<td>

`<union-CtX>` (inferred)<br>_<rationale>_

</td>
</tr>
<tr>
<td>AC1: <name></td>
<td>

**GIVEN** <pre-condition><br>
**WHEN** <trigger><br>
**THEN** <outcome><br>
**AND** <continuation>

</td>
<td>

`<per-AC-CtX>` (inferred)<br>_<rationale>_

</td>
</tr>
<!-- additional ACs ... -->
</tbody>
</table>

**Notes**: — *(empty by default; add free-form context as needed)*
```

- **Heading**: `#### <Key> — <Summary>`. Key verbatim from source; Summary verbatim. The heading is the doc's anchor for cross-references.
- **Attributes table (markdown, 6 columns)**: exactly `Key | Traces To | Epic | Classification | Target | Status`. Stays markdown — short uniform columns render fine. One data row per requirement. Criticality is NOT in the attributes table — it lives in the detail table where each AC carries its own CtX assessment.
- **Detail table (inline HTML, 3 columns, v22+)**: `Field | Value | Criticality` with `<colgroup>` setting widths 10% / 60% / 30%. Value gets the most width as the primary content. First row is always `Description` (carries the requirement-level CtX summary). Subsequent rows are per-AC (each carries its own CtX per-use-flow).
- **Why HTML and not markdown for the detail table**: markdown table column widths are content-driven and ungovernable — a multi-paragraph Criticality cell with rationale italic + CtX tags squeezes Value into a narrow ribbon. HTML `<colgroup>` gives explicit width control. HTML also allows nested `<table>` inside Value cells (sub-table content like Patient Details, button-state matrices) which markdown forbids inside `|...|` cells.
- **Markdown inside `<td>` cells**: GitHub-Flavored Markdown processes markdown inside HTML block elements when there is a blank line between the opening `<td>` and the markdown content (and a blank line before the closing `</td>`). Always use this pattern for cells containing keywords, links, or sub-tables. Cells with only short plain text can stay inline (`<td>Description</td>`).
- **Nested `<table>` inside Value cells** — see R1e for sub-table-block rendering.
- **Per-AC Criticality rationale**: each AC is a discrete use-flow with its own IFU dependencies. A single requirement can have ACs with different CtX tags (e.g., a heat-map display AC may be CtF+CtS; the legend-display AC may be CtF only). Per-AC Criticality captures this fidelity instead of collapsing to a single req-level assessment.
- **Description row CtX = union of AC CtX tags at adopt time** (human may refine). If any AC's CtX was inferred, Description row inherits `(inferred)` marker.
- **Notes**: free-form prose below the detail table. Dash/em-dash when empty. Grep-friendly for audit.

##### R1b — Attributes table value rules

| Column | Value rule |
|--------|-----------|
| **Key** | Verbatim from source (e.g., `AFAI-4083`, `REQ-0017`). Typed ID per project convention. |
| **Traces To** | Extracted from source's "Epic Link" / "Parent" field. If value matches `^(DI-\d+\|UN-\d+)` prefix, the matched ID is the Traces To value. Display as inline-code: `` `DI-0013` ``. If no prefix match, display literal `null` (plain text, not inline-code) — clean soft signal for "unresolved parent, needs human trace." |
| **Epic** | The Epic Link (or equivalent feature-grouping field) value from source, **verbatim** (no normalization, no keyword inference). Rendered as inline-code. If empty in source, display `null`. |
| **Classification** | Multi-valued, inferred from Description + AC text via regex patterns defined in `.claude/skills/docflow/references/classification-taxonomy.md` (9 canonical tags). Comma-separated inline-code list: `` `functional`, `safety` ``. Suffix `(inferred)` (lowercase, plain parens, not italic) on first adoption until a human confirms. Human overrides stabilize — reviewer + re-adopt do not overwrite them. |
| **Target** | From source `Fix Version` / `Target Release` field if present. Values: `v1`, `v2`, `future`, `unassigned`. Default `unassigned` if source has no such field. |

**Detail-table `Criticality` column** (per-AC + Description row):

- Values: comma-separated inline-code CtX tags (`` `CtF` ``, `` `CtS` ``, `` `CtC` ``, `` `CtP` ``) per the `glossary.md` "Criticality Tags" section.
- **Description row Criticality** = union of all AC CtX tags at adopt time (gives dashboards a sensible req-level rollup from day one; human may refine).
- **Per-AC Criticality** — each AC is a discrete use-flow with independent IFU dependencies. Inference runs per-AC on that AC's GIVEN/WHEN/THEN text.
- **Labels** (lowercase, soft — no italics):
  - `` `CtF`, `CtS` `` — human-confirmed (no suffix)
  - `` `CtF`, `CtS` `` `(inferred)` — auto-derived, not yet human-confirmed
  - `` `none` `` `(inferred)` — agent couldn't determine any CtX for this AC / row. `none` is wrapped in backticks (inline-code) so it sits in the same visual channel as `` `CtS` ``, `` `CtP` ``, etc. — avoids a plain-text "none" drawing the eye as unstructured prose.
- **Inline rationale** (auditability): when the Criticality tag(s) or `none` are inferred, the cell includes a rationale line beneath the tag on a new line in italics, starting with underscore emphasis:
  ```
  `CtF`, `CtS` (inferred)<br>_Depth analysis influences surgical planning (CtS); core 3D reconstruction capability (CtF)._
  ```
  or for `none`:
  ```
  `none` (inferred)<br>_No regex match. Candidate: CtF if foundational to IFU visualization; else nice-to-have._
  ```
  Rationale makes the agent's reasoning auditable and speeds human review. Human removes the rationale (and `(inferred)` suffix) once confirmed.
- **Description row `(inferred)` propagation**: if ANY AC's Criticality was inferred, the Description row inherits `(inferred)` on its union (conservative — stays inferred until every component is human-confirmed).
- **`CtF` is NEVER auto-inferred** — a functional classification does NOT mean critical to intended use (many functional reqs are nice-to-haves). CtF requires human assessment against the IFU. Conservative rules at adopt: `safety` class → `CtS`; `regulatory` → `CtC`; `performance` → `CtP`. No `CtF` inference.
| **Status** | Default `proposed` at adoption (reflects "ingested from source, not yet project-accepted"). Human-curated lifecycle: `proposed` → `accepted` → `implemented` → `verified` → optionally `deferred` / `rejected` / `superseded`. |

##### R1c — Epic Link is the source of Category (no keyword inference)

Classical categorization approaches apply keyword heuristics ("mentions '3D' → `3d-visualization`"). R1 does NOT do this. The Epic Link field from Jira (or equivalent feature-grouping field from other authoring systems) is the project team's own categorization. Using it verbatim is more faithful than a parallel synthetic Category.

Epic Link examples and their split:

| Source Epic Link value | Traces To | Epic |
|-----------------------|-----------|------|
| `DI-0013 MEASUREMENTS [UNITY]` | `DI-0013` | `DI-0013 MEASUREMENTS [UNITY]` |
| `UN-042 Remote Planning` | `UN-042` | `UN-042 Remote Planning` |
| `VIEW 3D RECONSTRUCTION` | *(none — manual trace)* | `VIEW 3D RECONSTRUCTION` |
| *(empty)* | *(none)* | *(none — flag for review)* |

Epic value stays verbatim. Projects that want dashboard normalization (e.g., mapping "VIEW 3D RECONSTRUCTION" → `3d-visualization`) add an optional `requirement_categories.normalize` mapping in `project.yml`; until then, dashboards group by Epic verbatim. No canonical list is required.

##### R1d — Classification inference via canonical taxonomy

Read the canonical taxonomy file (`.claude/skills/docflow/references/classification-taxonomy.md`) when populating Classification. **Do not derive tags from your own knowledge** — the regex patterns are the source of truth. Running the patterns against Description + AC yields the tag list; `functional` is always added as baseline.

Example: a requirement whose Description says *"encrypt PHI in transit for HIPAA audit trail"* matches `security` (encrypt), `privacy` (PHI, HIPAA), and `regulatory` (HIPAA, audit trail). Emitted as `` `functional`, `security`, `privacy`, `regulatory` ``.

The 9 tags are **not project-editable** — cross-project submissions dashboards depend on comparable queries. If a project needs a tag outside the canonical list, the registry-level taxonomy file is the place to propose the addition.

##### R1e — Nested content flattening in detail-table cells (v21.1+)

User stories use a small set of standard keywords that anchor the structure of the prose. R1e bolds them, gives bullets their own lines, and supports a sub-table block within an AND clause. The aim is readability inside a single table cell — not pretty-printing for its own sake.

**1. Keyword bolding** — wrap each occurrence of the user-story keywords in `**...**` so they read like section headings within the cell:

| Keyword | When | Bolded form |
|---------|------|-------------|
| `AS A` | Description "As a <role>" line | `**AS A**` |
| `GIVEN THAT` / `GIVEN` | Pre-condition | `**GIVEN THAT**` / `**GIVEN**` |
| `I WANT` | User intent | `**I WANT**` |
| `SO THAT` | User benefit / motivation | `**SO THAT**` |
| `WHEN` | Trigger | `**WHEN**` |
| `THEN` | Expected outcome | `**THEN**` |
| `AND` | Continuation of GIVEN/WHEN/THEN | `**AND**` |
| `BUT` | Negative continuation | `**BUT**` |
| `IF` / `ELSE` | Branching condition inside an AND | `**IF**` / `**ELSE**` |

Match is **whole-word, case-sensitive at the start of a clause** (i.e., immediately after a `<br>` or at cell start). Lowercase prose mid-sentence ("the user when ready") is NOT a match. Do not bold occurrences inside literal source text quoted in double quotes.

**2. Newline-per-clause** — every keyword starts on its own line. Use `<br>` before the bolded keyword (except when it is the first content in the cell). The Description row is the same — `**AS A**` opens, then `**GIVEN THAT**`, `**I WANT**`, `**SO THAT**` each on their own line.

**3. Bullets get their own lines** — when the source has a bulleted list under an AND/THEN clause, render each bullet on its own line:
   - Use `<br>• <text>` per bullet (NOT inline `• a • b • c`).
   - The leading clause text (e.g. `**AND** the system shows the following:`) stays on its own line above the bullets.
   - This trades a few extra lines per cell for an enormous readability gain — multi-bullet lists in v21.0 collapsed into a single illegible run.

**4. Sub-tables inside an AND clause (v22+ — nested HTML `<table>`)** — when an AND/THEN clause contains tabular data (color/depth key, button-state matrix, parameter table, Patient Details, Global Control panel, etc.), render it as a real nested HTML `<table>` *inside the Value cell's `<td>`*, immediately after the lead-in clause. The detail-table is now HTML (R1a), so nested tables work natively — no more `·`-separated bullet runs.

   **Single-column lookup table** (e.g. depth key, color scale):
   ```html
   **AND** the system displays a Depth Key legend with the following color scale:

   <table>
     <thead><tr><th>Color</th><th>Range</th></tr></thead>
     <tbody>
       <tr><td>Blue</td><td>0–1 mm</td></tr>
       <tr><td>Light Blue</td><td>1–2 mm</td></tr>
       <tr><td>Yellow</td><td>2–3 mm</td></tr>
       <tr><td>Orange</td><td>3–5 mm</td></tr>
       <tr><td>Red</td><td>5–7 mm</td></tr>
       <tr><td>Brown</td><td>&gt;7 mm</td></tr>
     </tbody>
   </table>
   ```

   **Multi-column matrix** (e.g. button-state matrix with Component/State/Trigger/Effect):
   ```html
   **AND** the button changes its visual state according to the following table:

   <table>
     <thead><tr><th>Component</th><th>State</th><th>Trigger</th><th>Visual Effect</th></tr></thead>
     <tbody>
       <tr><td>Main Eye Icon (Tool panel)</td><td>Idle</td><td>No interaction</td><td>No additional effects</td></tr>
       <tr><td>Main Eye Icon</td><td>Selected</td><td>User clicks the button</td><td>Border color change + inner shadow (blue)</td></tr>
       <!-- additional rows ... -->
     </tbody>
   </table>
   ```

   **Patient/data display tables** (3-col: Field / Type / Example):
   ```html
   **THEN** the system displays the following Patient Details:

   <table>
     <thead><tr><th>Field</th><th>Type</th><th>Example</th></tr></thead>
     <tbody>
       <tr><td>First name + Last name, Gender</td><td>text</td><td>Amanda Jones, Female</td></tr>
       <tr><td>Age</td><td>text</td><td>70 years old</td></tr>
       <tr><td>Laterality</td><td>text</td><td>Left Hip</td></tr>
     </tbody>
   </table>
   ```

   **HTML escaping inside table cells**: escape `<`, `>`, `&` per HTML rules (`&lt;`, `&gt;`, `&amp;`). Numeric thresholds with comparison operators (e.g. "≥ 7 mm", "< 20°") render fine as Unicode; bare `>` / `<` should be escaped.

   **Markdown inside `<td>`**: short text stays inline; longer cells use blank-line-separated markdown blocks (per R1a). Keywords like **Blue** can be bolded via either `**Blue**` (markdown, requires blank line context) or `<strong>Blue</strong>` (always works). For brevity, plain text in nested-table cells is fine.

**5. Mark sub-table presence** for audit: append `<!-- nested table -->` HTML comment once at the end of the AND block. This keeps grep / dashboard counts accurate (renamed from `<!-- nested table flattened -->` since v22 no longer flattens).

**6. Conditional branches**: `**IF** <condition>: <action><br>**ELSE**: <action>` — each on its own line. For complex conditional matrices, use a nested `<table>` with `Condition` / `Action` columns.

**Worked example — heatmap AC1 (v22 shape, inline HTML detail table):**

```html
<tr>
<td>AC1: Display heat map</td>
<td>

**GIVEN** the 3D model is reconstructed<br>
**WHEN** the user opens the Unity-based view<br>
**THEN** the system displays a Pincer and Cam heat map on the 3D model<br>
**AND** the system displays a Depth Key legend with the following color scale:

<table>
  <thead><tr><th>Color</th><th>Range</th></tr></thead>
  <tbody>
    <tr><td>Blue</td><td>0–1 mm</td></tr>
    <tr><td>Light Blue</td><td>1–2 mm</td></tr>
    <tr><td>Yellow</td><td>2–3 mm</td></tr>
    <tr><td>Orange</td><td>3–5 mm</td></tr>
    <tr><td>Red</td><td>5–7 mm</td></tr>
    <tr><td>Brown</td><td>&gt;7 mm</td></tr>
  </tbody>
</table>

**AND** the system displays a static 5mm burr icon with a color-coded circle that correlates to the 0–5 mm depth range on the legend
<!-- nested table -->

</td>
<td>

`CtS` (inferred)<br>
_Depth analysis of Cam/Pincer impingements informs surgical-planning decisions; ..._

</td>
</tr>
```

Compare v21.1's `<br>•`-separated bullet rows: column shape is now visible (Color / Range header + 6 data rows), Value column gets 60% width via `<colgroup>`, Criticality is a 30% sidebar. No more illegible bullet runs for tabular content.

**Hyperlink preservation through R1 flattening** — the cross-body rule (see "Hyperlinks (all doc-types)" above) applies inside R1 detail-table cells: every `[text](url)` span emitted by Phase 2 splice survives Phase 5e restructuring as an atomic unit. A flattening pass that drops inline links inside an AC cell is a faithfulness violation — flag with `%% REVIEW: LINK-DROPPED — <anchor + URL>` rather than dropping silently. Common cell content where this matters: requirement keys (`[AFAI-3555](url)`), Design Input cross-refs (`[DI-0003](url)`), Confluence-page links inside Description / AC bodies, standards / FDA-guidance external refs.

##### R1f — Document-wide sections outside per-requirement scope

Sections of the SRS that are NOT per-requirement content (executive summary, scope, revision history, governance notes) render as standard markdown prose and tables under their own H2/H3 headings. R1's two-table shape applies only to the individual requirement blocks under a H3 "Requirements" / "Stories" section.

##### R1g — User override stability

The adopter re-runs safely without clobbering human edits: once a human has edited Classification (e.g., changed `` `functional` `` to `` `functional`, `safety` `` and removed `*(inferred)*` suffix), a subsequent `/docflow review --fix` or re-adopt will NOT overwrite that value. Same stability model as `template_of` and `authored_per` — human-authored values are sticky.

Detection: if the attributes table's Classification cell lacks the `*(inferred)*` suffix, it has been human-confirmed; leave it alone.

#### Document Structure

- Headers/footers: capture in frontmatter `notes:`, not in body
- Page numbers: omit
- Revision history: convert to `## Revision History` section at end
- Table of contents: omit
- Confidentiality notices: capture once in frontmatter, omit from body
- Watermarks: note in frontmatter `notes:`

### Phase 4: Handle Images

Image handling is the hardest part of conversion and has produced the most calibration findings (F1-F11). Follow this pipeline exactly.

#### 4.1 Inventory and Deduplicate (F2)

Enumerate every image candidate from the source:

- **PDF**: `pdfimages -list "{{SOURCE_PATH}}"` gives type/size/resolution/object-id/page per instance. Bilingual or repeating documents emit the same object multiple times with different seq numbers — **group by object ID (PDF) or file hash (DOCX/XLSX)** so each unique image is named ONCE.
- **DOCX**: `word/media/*` — each file is unique.
- **XLSX** (X2): `openpyxl.ws._images` misses VML-anchored and drawing1-anchored images. **Always supplement**: `unzip -l "{{SOURCE_PATH}}" | grep -E "xl/(media|drawings)"` to enumerate the full set.

Record for each unique image: resolution, file size, estimated source location (page, sheet, or section), whether it repeats, and your decorative-vs-content classification.

#### 4.2 Classify: Decorative vs Content

| Class | Pattern | Action |
|-------|---------|--------|
| **Decorative** | Repeats across many pages, small, often JPEG, identical — logos, letterheads, borders, watermarks | Omit. Drop a `<!-- decorative: description omitted -->` comment near the first occurrence |
| **Content** | Unique per location, meaningful to the procedure — flowcharts, matrices, decision trees, diagrams, screenshots | Extract, name, reference, manifest-entry |
| **Signature** | Sign-off image | Replace with `[SIGNATURE BLOCK: Role — Name — Date]` — never extract |

#### 4.3 Orientation Correction (F1) — MANDATORY for PDF

`pdfimages -png` emits raw image data without applying the PDF's coordinate transform matrix. Diagrams frequently come out upside-down or mirrored. **This is not an edge case.**

For every extracted content image from a PDF source:
1. Use the Claude `Read` tool to visually inspect the PNG.
2. If text reads upside-down, mirrored, or rotated: apply correction with PIL:
   ```python
   from PIL import Image
   im = Image.open(path)
   # Choose based on inspection:
   im.transpose(Image.FLIP_TOP_BOTTOM).save(path)     # upside-down text
   im.transpose(Image.FLIP_LEFT_RIGHT).save(path)     # mirrored text
   im.rotate(90, expand=True).save(path)              # rotated 90° CW (etc.)
   ```
3. Re-inspect with `Read` to confirm text reads correctly.

If Pillow is not installed: `pip3 install --break-system-packages --user Pillow`.

#### 4.4 Name Each Content Image

```
{doc-id-lowercase}_{descriptor}.{ext}
```

- `{doc-id-lowercase}` is `{{DOC_ID}}` lowercased (e.g., `sop-000355609`).
- `{descriptor}` derivation priority (F6, F7):
  1. **Printed caption** near the image (e.g., "Figure 1. RM Process", "Abbildung 2. Implementierungsstrategie", "Table 3. Severity Matrix") → kebab-case the title: `rm-process`, `implementierungsstrategie`, `severity-matrix`
  2. **Nearest preceding section heading** → kebab-case it
  3. **Describe the content itself** as last resort
- **Never pre-commit to a descriptor based on the task brief or document title** — derive from what the source actually contains at conversion time. Anticipated descriptors are hypotheses, not gates.
- `{ext}` is `png` preferred; convert EMF/WMF to PNG.
- Copy to `{{STAGING_DIR}}/images/{named-file}`.

#### 4.5 Reference in Markdown — Subfolder-Aware Relative Paths (F10)

**`{{OUTPUT_DIR}}` is a DOC_TYPE subfolder under `source-md/` (e.g., `source-md/SOPs/`). `{{IMAGE_DIR}}` is the flat `source-md/images/` one level up.** Every image reference must use `../images/` as the relative path prefix — not `images/`.

```markdown
<!-- CORRECT for markdown at source-md/SOPs/FOO.md → image at source-md/images/foo.png -->
![Detailed alt text...](../images/sop-000355609_rm-process-flow.png)

<!-- WRONG — this resolves to source-md/SOPs/images/foo.png which does not exist -->
![Detailed alt text...](images/sop-000355609_rm-process-flow.png)
```

This applies to **both** body references and the Image Manifest section.

#### 4.6 Alt Text: Self-Contained for Complex Diagrams (F8)

Alt text must be detailed enough that a reader who cannot view the image still understands what the figure shows. This is regulatory-grade alt text, not generic web alt-text.

- **Simple figure** (single chart, icon, screenshot): 1-2 sentences.
- **Complex diagram** (flowchart, decision tree, process, matrix): **30-100 words** describing nodes, connections, and decision branches explicitly.
- Example for a flowchart: describe the inputs, the processing cluster with its internal relationships, the outputs, and any feedback loops.

#### 4.7 Mermaid Supplement for Diagrams (F11) — caption BELOW Mermaid

For **content images that have graph structure** (flowcharts, decision trees, architectural diagrams, topologies), emit a Mermaid block immediately after the image, then the caption + authoritative-source line AFTER the Mermaid. The reader sees image → diagram → caption in reading order.

**Layout (v28+ with F11-CLASSIFY marker)**:

````markdown
<!-- F11-CLASSIFY: descriptor="security-safety-risk-process" type="a" mermaid-emit="required" -->

![Alt text describing the diagram's nodes, edges, and decision branches (30-100 words)...](../images/doc-id_descriptor.png)

```mermaid
flowchart LR
    A[Node A] --> B{Decision}
    B -->|Yes| C[Node C]
    B -->|No| D[Node D]
```

*Figure N. Title (source p.X).* Authoritative source: [doc-id_descriptor.png](../images/doc-id_descriptor.png). The Mermaid diagram above is a readability supplement derived from the image — the image is the canonical record.
````

**F11-CLASSIFY marker is REQUIRED in v28+** (task ben/087). Every content image must carry a marker HTML comment on the line above its `![...](...)` reference. The marker makes the agent's classification decision observable and the Phase 7 Mermaid-presence check mechanical instead of heuristic. Skipping the marker is a Phase 7 Required failure.

**Marker schema**:

| Attribute | Required? | Allowed values | Notes |
|-----------|-----------|----------------|-------|
| `descriptor` | yes | kebab-case stem matching the image filename's descriptor portion | Must match `images/<doc-id>_<descriptor>.<ext>` |
| `type` | yes | `a`, `b`, `c`, `d`, `e`, `review` | See F11a table below. `review` = classification ambiguous; human must resolve |
| `mermaid-emit` | yes | `required`, `skip` | `required` for types a/b/c; `skip` for d/e/review |
| `skip-reason` | conditional | `matrix`, `ui-capture`, `photograph`, `decorative`, `ambiguous-needs-review` | REQUIRED when `mermaid-emit="skip"`. Short machine-friendly tag |

**Emit rules**:
- `type=a|b|c` → `mermaid-emit="required"` → MUST be followed by an adjacent `\`\`\`mermaid` block within 5 lines of the image ref (before the caption).
- `type=d|e` → `mermaid-emit="skip"` with `skip-reason` → NO mermaid block; caption may immediately follow image.
- `type=review` → `mermaid-emit="skip"` with `skip-reason="ambiguous-needs-review"` → emit a `%% REVIEW: MERMAID-CLASSIFY-AMBIGUOUS — <one-line why>` comment adjacent to the marker; no mermaid emitted until a human resolves.

**Examples**:

```markdown
<!-- F11-CLASSIFY: descriptor="auth-flow" type="a" mermaid-emit="required" -->
```

```markdown
<!-- F11-CLASSIFY: descriptor="overall-risk-severity-matrix" type="d" mermaid-emit="skip" skip-reason="matrix" -->
```

```markdown
<!-- F11-CLASSIFY: descriptor="login-screenshot" type="e" mermaid-emit="skip" skip-reason="ui-capture" -->
```

```markdown
<!-- F11-CLASSIFY: descriptor="mystery-diagram" type="review" mermaid-emit="skip" skip-reason="ambiguous-needs-review" -->
%% REVIEW: MERMAID-CLASSIFY-AMBIGUOUS — source image shows boxes without clear arrow direction; could be (a) flow or (b) logical. Human to set type. %%
```

##### F11a — Diagram type classification (MANDATORY before deciding Mermaid)

Before emitting any Mermaid, classify the content image by what the source actually shows. **This classification drives what kind of Mermaid you emit — do not collapse these to a single "has boxes → emit flow"rule.**

| Type | Source characteristics | Mermaid treatment |
|------|-----------------------|-------------------|
| **(a) Flow diagram** | Boxes + explicit directed arrows + decision diamonds + start/end terminators | Emit `flowchart` with full flow — nodes, directed edges, decisions, preserved start/end shapes |
| **(b) Logical / architectural** | Boxes + grouping/containment (nested rectangles, swim lanes, regions), NO directional arrows between boxes | Emit `flowchart` with **boxes + `subgraph` blocks only, NO edges**. Never invent connectors. |
| **(c) Component / network** | Boxes + lines where the lines represent adjacency or relationship (not directed flow) | Emit `flowchart` with **undirected `---` lines** preserving source adjacency. Do not upgrade `---` to `-->`. Never invent typed connectors. |
| **(d) Matrix / heatmap** | Grid of cells, row/column labels | Markdown table — no Mermaid |
| **(e) Screenshot / photo / UI mockup** | Raster content, no graph structure | No Mermaid |

When in doubt between (a) and (b): ask "does the source show me how box X becomes box Y?" If yes (arrow, labeled flow, sequence marker), it's (a). If the source just shows X and Y near each other or nested together, it's (b). **Proximity is not flow.**

##### F11b — Faithfulness absolute rule (CRITICAL)

**Never invent connectors, labels, edge semantics, or relationships not visible in the source.**

If the source doesn't show how two boxes relate — whether box A talks to box B via HTTP, via shared memory, via a library call, or not at all — the Mermaid must not show that either. The image is the canonical record; the Mermaid supplement reproduces **structure**, not **semantics**.

Concrete examples of violations to avoid:
- Source shows "Auth Guard" and "OKTA Auth" as separate boxes with no arrow between them → Mermaid emits `AuthGuard --> OktaAuth` with label "auth check". **Wrong.** The source doesn't show HOW they relate; you invented that.
- Source shows a service-registry diagram with boxes inside a "Backend" rectangle → Mermaid emits arrows `ServiceA --> ServiceB` based on your mental model of how backends usually work. **Wrong.** Boxes inside a group show containment, not flow.
- Source shows a network topology with dashed and solid lines clearly distinguishing logical vs physical links → Mermaid flattens to a single `-->` line type. **Wrong.** Preserve the distinction (`-.->` dashed, `-->` solid) or drop the connector entirely.

If you find yourself writing an edge with a label the source doesn't show, delete the edge. If you find yourself writing an edge for a relationship the source only implies via proximity, delete the edge.

##### F11c — Start/end shape preservation

Preserve source conventions for flow terminators:

| Source shape | Mermaid syntax |
|--------------|----------------|
| Filled black dot (●) as start | `A((●))` or `A((Start))` |
| Rounded rectangle as start/end | `A([Start])` / `Z([End])` |
| Labeled circle start node | `A((Begin))` (literal label) |
| Unlabeled hollow terminator | `Z(( ))` |

If the source lacks an explicit start/end shape (common in architectural diagrams), don't fabricate one. Flow diagrams with no visible terminators just start at the leftmost/topmost node.

##### F11d — Swim lanes, groupings, and containment fidelity

If the source uses swim lanes, grouped regions, or labeled subsystem boundaries, reproduce them as Mermaid `subgraph` blocks with the source's lane/group labels verbatim:

```mermaid
flowchart LR
    subgraph Frontend
        A[User Login]
        B[Session Token]
    end
    subgraph Backend
        C[Auth Service]
    end
```

Preserve source lane ordering (left-to-right or top-to-bottom as in source).

**Containment fidelity is structural truth — observation before declaration.**

If the source shows box A visually inside region B (nested rectangles, labeled enclosure, swim lane), the Mermaid subgraph nesting MUST mirror this exactly. A is declared inside B's `subgraph` block. Containment is not cosmetic — it communicates architectural boundaries (what's inside VPC, what's outside; what's in the secure enclave, what isn't). Getting containment wrong changes the meaning.

**Protocol**: before writing any Mermaid subgraph blocks, enumerate the source image's region boundaries. For each content element, record which region(s) contain it. Build the nested structure from these observations, not from what "seems natural" or "how architectures usually look."

**Common failure mode**: placing service boxes (Resolvers, API Gateway, Lambda handlers) at the top level when the source shows them inside a VPC or private-network boundary. This flattens a security/deployment boundary that the source specifically communicates. Observed in the MedTech Project Web SAD — AppSync, API Gateway, Resolvers, API Handler, and Authorizer all drawn inside the VPC rectangle in the source were transcribed as top-level Mermaid nodes, losing the VPC containment semantic.

**Nested subgraphs are allowed and often required**: `subgraph VPC` containing `subgraph Management`, `subgraph Integrations`, etc. Depth follows source depth — don't flatten. Don't add nesting levels that aren't in the source either.

##### F11e — Size as a quality gate, not a node-count threshold

Prior guidance capped Mermaid at "~20 nodes". That was a flat-graph heuristic; dropped in favor of quality gates.

**Proceed with Mermaid** (any size, including 40+ nodes) if:
- The source has natural subgroups (visually grouped, lane-separated, or region-labeled) → use `subgraph` blocks; navigation is cluster-by-cluster and scales well
- The rendered Mermaid conveys structural navigation value a reader couldn't get from reading prose alone
- You can quote every label cleanly (per F12) without truncation

**Skip Mermaid** (just image + caption) if:
- The diagram is flat (no groupings) AND has > ~20 nodes — auto-layout will produce a crossing-heavy mess
- Labels would need heavy abbreviation to fit
- The diagram's meaning depends on visual hierarchy (font sizes, colors, shapes) that Mermaid can't reproduce

**Mid-complexity option — cluster-level Mermaid**: when a source diagram has 25+ nodes but natural subgroups, emit Mermaid at the **cluster level** (one node per subgroup, labels listing contents) rather than enumerating every leaf node. Example: an AWS topology with 6 service clusters × 5 services each → emit 6 subgraph-nodes rather than 30 flat nodes.

##### F11f — Classification examples

| Image | Type | Rationale |
|-------|------|-----------|
| "System Overview" with user → service → DB and arrows | (a) flow | explicit arrows |
| "Frontend Application" with boxed components (AppRoot, Router, AuthGuard, …) inside a bounding rectangle, no arrows | (b) logical | grouping + containment, no directional relationships |
| "AWS Backend Architecture" with service boxes and dashed/solid lines between them | (c) component | lines are adjacency; preserve dashed/solid distinction |
| "Tablet Provisioning" with numbered steps and directional arrows | (a) flow | sequence + arrows |
| "Risk Severity Matrix" with 5×5 grid | (d) matrix | no Mermaid |
| "Device Photo" | (e) photo | no Mermaid |

##### F11g — Legacy "when to emit" checklist (replaced by F11a)

The prior ✅/❌ checklist is superseded by F11a classification. Don't fall back to "boxes + arrows → emit" — that's the rule that produced inferred connectors on logical diagrams.

##### F11h — Layout fidelity (spatial arrangement matches source)

Mermaid's dagre layout degrades when given few or no edges — it produces arrangements unrelated to the source. The current diagram may be correct structurally (right boxes, right containment, right edges) but visually inverted or rearranged, which misleads readers who pattern-match the source image.

**Protocol**:

1. **Direction from dominant source flow**:
   - `flowchart TB` — source stacks elements top-to-bottom (layered architectures, vertical flows)
   - `flowchart LR` — source flows left-to-right (pipelines, request/response sequences)
   - Default LR; switch to TB when source visibly stacks rather than chains

2. **Subgraph declaration order matches source reading order**: top-to-bottom, then left-to-right. Dagre uses declaration order when no other signal is present.

3. **For logical diagrams (F11a-b) and sparse component diagrams (F11a-c with few edges)**: add **invisible layout hints** using `~~~` between subgraphs to force source-accurate arrangement. Invisible edges do NOT render — they only constrain dagre's positioning.

   ```mermaid
   flowchart TB
       subgraph UI["UI Layer"]
         ...
       end
       subgraph Logic["Logic"]
         ...
       end
       subgraph Data["Data Layer"]
         ...
       end
       subgraph OKTA["OKTA"]
         ...
       end

       %% Layout hints (invisible, no semantics — source shows
       %% UI-Logic-Data stacked vertically with OKTA on the right)
       UI ~~~ Logic
       Logic ~~~ Data
       OKTA ~~~ Logic
   ```

   Always precede layout hints with `%% Layout hints` comment so reviewers don't mistake them for semantic edges.

4. **Document layout in the caption**: "Layout reproduces source's [top-to-bottom layered / left-to-right pipeline / central-hub radial] arrangement."

5. **When dagre can't reproduce source layout** (complex non-orthogonal arrangements, overlapping regions, 3D-projected diagrams): note in caption: "Mermaid layout is approximate; consult source image for exact spatial arrangement."

##### F11i — Edge-routing fidelity (correctly wire the edges that exist)

F11b covered NOT inventing edges. F11i covers: once you've decided an edge exists, route it to the correct source and target nodes.

Flowchart transcription is error-prone at decision nodes. The agent may correctly identify all nodes, their labels, AND recognize an edge exists, but route it to the wrong target — common when:

- Multiple edges emerge from a decision diamond
- YES/NO branches go to nodes on opposite sides of the diagram
- One branch short-circuits a chain and merges back downstream
- Decision branches cross swim lanes or regions

Observed in the MedTech Project Web SAD sales-rep-registration flow: the "Yes" branch of `"OKTA account exists"` was routed back to itself (`D2 -- "Yes" --> D2`) when the source clearly shows it going forward to `"Create user in DB"` (bypassing the "Create OKTA user" step).

**Mandatory enumerate-before-emit protocol** for every flow diagram (F11a-a class):

1. Before writing any `A --> B` lines, enumerate EVERY edge in the source as a triple: `(source-node, branch-label, target-node)`. Record all triples in a scratch list.

2. For decision nodes specifically: walk each branch visually in the source. Trace the line FROM the diamond TO its termination point. Don't infer from position; follow the actual drawn line. Decision nodes can have 2, 3, or more branches — enumerate them all.

3. Verify each triple independently: for every entry, re-confirm by looking at the source image that there is a line from source-node to target-node with the stated label. If unsure, flag the edge with a `%% VERIFY: <description>` comment rather than guessing.

4. Only then write the edges block in Mermaid.

**Self-check in Phase 7 validation**: for each flow diagram, walk every emitted edge and verify against the source. Common regressions:

- **Self-loops** (`A --> A`): legitimate only when source explicitly shows a self-loop arrow. Otherwise, the target was mis-transcribed.
- **Missing branches**: decision nodes with fewer branches emitted than drawn in source.
- **Swapped YES/NO**: the "Yes" branch going to the error path or vice versa.
- **Lane-crossing errors**: a branch that crosses swim lanes in the source may lose its target during transcription. Re-trace across lane boundaries.

**When a decision branch terminates without forward flow**: some source diagrams have decision branches that terminate (implicit "return"/"stop"). Emit `D -- "branch-label" --> Stop((" "))` with a hollow terminator — do NOT loop back to the decision node or another arbitrary node to fill the gap.

**Mermaid syntax rules — label quoting (F12 — silent render failure otherwise)**:

Mermaid's parser chokes on unquoted special characters in node and link labels. The diagram then silently fails to render in many viewers (GitHub, VS Code Mermaid extension), while OTHER Mermaid blocks in the same file still render — making the failure hard to spot during review.

**Always double-quote any label that contains these characters**: `/`  `(`  `)`  `:`  `,`  `&`  `#`  `?` (except inside `{...}` decision nodes, which already quote), or any punctuation beyond letters/digits/hyphens/spaces/`<br>`.

```mermaid
%% CORRECT — quoted
H["Hazard / Situation / Harm"] --> NewRCM["New RCM"]
A -. "DI Source" .-> B
IF["Item / Feature"] --> Func["Function"]

%% WRONG — unquoted, will silently fail to render
H[Hazard / Situation / Harm] --> NewRCM[New RCM]
A -. DI Source .-> B
IF[Item / Feature] --> Func[Function]
```

Safe defaults:
- **Quote every node label** if in doubt — there's no downside to over-quoting. `H["Simple"]` renders identically to `H[Simple]`.
- **Always quote link labels** that contain anything other than a single word: `A -. "multi word label" .-> B`, not `A -. multi word label .-> B`.
- Decision nodes `{...}` should also use quotes inside: `D{"Is X Acceptable?"}` not `D{Is X Acceptable?}`.

**Validation rule (Phase 7)**: after emitting each Mermaid block, scan the block for any unquoted `/`, `(`, `)`, `&`, or `#` character inside a node label (`[...]`) or link label (`-. ... .->` / `|...|`). If found, rewrite the label with quotes.

**Duplicate / translated sections** (bilingual docs): emit the Mermaid block at **EVERY occurrence** of the image — including translated sections. The source PDF typically shows the same image (with the same original-language labels) in each language section; reproducing only once would force a German/French/etc. reader to jump to the English section to see the diagram. The image file is one-to-many (referenced from multiple locations) but the Mermaid supplement lives inline at each occurrence.

**Label language for translated Mermaid**: keep the labels in the source image's original language (usually English, matching what's printed in the figure itself). Do NOT translate Mermaid labels — the Mermaid is a structural supplement to the image, and the image has English labels. Mention this explicitly in the target-language caption: `Labels werden mit dem englischen Originaltext der Quellabbildung reproduziert.` / `Les libellés reproduisent le texte original anglais de la figure source.` (or equivalent).

**Mark as derived**: the Mermaid is an editable supplement, not a 1:1 reproduction. The image file remains the authoritative record for regulatory purposes. Always include the "Authoritative source" link and the "Mermaid is a readability supplement" disclaimer in the caption line below the Mermaid.

#### 4.8 Image Inventory (frontmatter, not body) — NO Image Manifest section

**Do NOT emit a `## Image Manifest` section in the body.** The body already has:
- Each image referenced inline with detailed alt text and caption
- The caption already names the source page ("source p.3" / "source p.10")
- The frontmatter carries `has_images`, `image_count`, and (optionally) an `images:` array for machine-readable inventory

A standalone manifest section duplicates all of this and clutters the document. Skip it.

**If machine-readable image inventory is needed** (e.g., for export pipelines / refresh diffs), populate the optional `images:` frontmatter array:

```yaml
images:
  - file: "sop-000355609_rm-process-flow.png"
    source_pages: [3, 10]   # EN + DE occurrences
    type: flowchart          # flowchart | matrix | screenshot | diagram | photo
    mermaid: true            # whether a Mermaid supplement was generated
  - file: "sop-000355609_implementation-strategy.png"
    source_pages: [5, 12]
    type: flowchart
    mermaid: true
```

This is optional — `image_count` and in-body refs are the minimum bar. Add the `images:` array only if downstream tooling (export, refresh, trace) needs it.

#### 4.9 Page Boundary Markers (PDF only)

For PDF-sourced documents, preserve source page boundaries as inline markers so readers can cross-reference specific pages of the source QMS record.

**Detection**: `pdftotext` preserves form feeds (`\f`) between pages. Run `pdftotext -layout "$SOURCE" -` and split on `\f` to get per-page content. Total page count is `pdfinfo "$SOURCE" | grep ^Pages`.

**Marker format**:

```markdown
*— End of Page N of M —*
```

- Italic, em-dashes, page X of total Y.
- Insert at the END of each page's content in the markdown, at the next clean section/paragraph boundary.
- Don't break mid-sentence or mid-table.
- For bilingual documents where one logical section spans pages, put the marker at the nearest natural break (end of a subsection, after a table, before a heading).
- Annotate the EN→DE boundary explicitly: `*— End of Page N of M (end of English section) —*`.

**Per-format detection** — pick the first option that's available:

| Format | Preferred (if tool available) | Fallback | Marker |
|--------|-------------------------------|----------|--------|
| **PDF** | `pdftotext -layout "$SOURCE" -` splits on `\f` form feeds; total count from `pdfinfo`. | — | Use. |
| **DOCX / DOC** | **LibreOffice-rendered PDF (F15, preferred)**: `soffice --headless --convert-to pdf --outdir /tmp/docflow-$$ "$SOURCE"`, then treat the generated PDF as the source for pagination. This matches the authoritative rendered pagination (what prints) — not just author-intended breaks. | **`w:br` parsing (F14, fallback)**: parse `word/document.xml`, count `<w:br w:type="page"/>` elements in document order, total pages = count + 1. Use this only when LibreOffice is not on PATH. Note in frontmatter `notes:` that pagination is author-intended, not rendered. | Use. |
| **XLSX** | N/A — sheets are the natural unit, already represented as `## Sheet: Name`. | — | Skip. |
| **PDF ≤ 2 pages** | N/A — marker adds more clutter than signal. | — | Skip. |
| **DOCX with 0 explicit breaks AND no LibreOffice** | Pagination depends entirely on rendering environment. Skip with a note in frontmatter `notes:`. | — | Skip. |

**Why LibreOffice over `w:br` parsing**: a form with 3 explicit breaks may render as 20 PDF pages because tables/checkbox blocks span multiple pages at the rendered layout. Author-intended breaks are *section boundaries*; LibreOffice-rendered PDF is *what the reader sees when printing*. For regulatory traceability, cite the authoritative rendered pagination.

**Toolchain detection (MANDATORY — do NOT assume soffice is unavailable)**:

Before falling back to F14 `w:br` parsing or skipping pagination entirely, you MUST run the probe explicitly and record the result. Assuming "probably not installed" based on environment heuristics (WSL, fresh repo, no prior render) is a spec violation — the project's `setup.sh` installs LibreOffice on Linux / WSL / macOS by default, so the probe should succeed in almost every adopting environment. A negative result needs observable evidence.

```bash
# Run this ONCE per adopt, BEFORE deciding which branch to take.
# Report the probe result explicitly in your Phase 7 notes, regardless of outcome.
if command -v soffice >/dev/null 2>&1 || command -v libreoffice >/dev/null 2>&1; then
    SOFFICE_BIN=$(command -v soffice || command -v libreoffice)
    echo "pagination: F15 (LibreOffice-rendered PDF) — using $SOFFICE_BIN"
    # Preferred path — render to PDF, use pdftotext pagination
    "$SOFFICE_BIN" --headless --convert-to pdf --outdir /tmp/docflow-$$ "$SOURCE"
    RENDERED_PDF="/tmp/docflow-$$/$(basename "$SOURCE" .docx).pdf"
    # Process the generated PDF for pagination only; markdown content still comes from DOCX pipeline
else
    echo "pagination: F14 fallback (w:br parsing) — soffice/libreoffice not on PATH"
    # Parse w:br elements — see extraction snippet below
fi
```

**Reporting obligation**: your Phase 7 notes must include one of three exact labels: `pagination: F15 (rendered)`, `pagination: F14 (author-intended)`, or `pagination: skipped (reason)`. If you skip, the reason must be one of: "≤2 pages", "0 explicit breaks AND no LibreOffice (probe returned <verbatim probe output>)", or "XLSX (sheets are the unit)". A bare "skipped" with no rationale is a Phase 7 failure — re-run the probe and retry. *Rationale: this closed the gap that allowed the MedTech Project RMP adopt run (Apr 2026) to skip pagination entirely while LibreOffice was installed and on PATH — the agent never ran the probe.*

**DOCX extraction snippet (fallback F14)**:

```python
import zipfile, xml.etree.ElementTree as ET
ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
with zipfile.ZipFile(source_path) as z:
    root = ET.fromstring(z.read("word/document.xml"))
body = root.find("w:body", ns)
breaks = []  # (paragraph_index, next_paragraph_text)
paragraphs = []
for i, p in enumerate(body.iter(f'{{{ns["w"]}}}p')):
    text = "".join((t.text or "") for t in p.iter(f'{{{ns["w"]}}}t')).strip()
    has_break = any(br.get(f'{{{ns["w"]}}}type') == 'page'
                    for br in p.iter(f'{{{ns["w"]}}}br'))
    paragraphs.append((text, has_break))
# For each break, the next non-empty paragraph's text is the anchor to locate in markdown
```

**Insertion rule**: for each page boundary (from either source), find a distinctive phrase from the next page's content (~5-15 chars, unambiguous) and insert `*— End of Page N of M —*` on the preceding blank line. Prefer headings or unique phrases over generic text (`Additional Comments`, `Yes`) that could match multiple locations.

**DOCX extraction snippet**:

```python
import zipfile, xml.etree.ElementTree as ET
ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
with zipfile.ZipFile(source_path) as z:
    root = ET.fromstring(z.read("word/document.xml"))
body = root.find("w:body", ns)
breaks = []  # (paragraph_index, next_paragraph_text)
paragraphs = []
for i, p in enumerate(body.iter(f'{{{ns["w"]}}}p')):
    text = "".join((t.text or "") for t in p.iter(f'{{{ns["w"]}}}t')).strip()
    has_break = any(br.get(f'{{{ns["w"]}}}type') == 'page'
                    for br in p.iter(f'{{{ns["w"]}}}br'))
    paragraphs.append((text, has_break))
# For each break, the next non-empty paragraph's text is the anchor to locate in markdown
```

**Insertion rule (DOCX)**: for each page break, find the first ~10 chars of the next non-empty paragraph in the markdown (as a heading or body line), and insert `*— End of Page N of M —*` on the preceding blank line. Don't anchor on generic text (`Additional Comments`, `Yes`) that could match multiple locations — use the nearest distinctive heading or phrase.

**Captions already name the page**: the Figure caption in Phase 4.7 includes `(source p.X)` so figures are always traceable. Page markers are the complementary mechanism for prose content between figures.

### Phase 5: Resolve Cross-References

Read `{{INDEX_PATH}}` to build a lookup table of doc-ids and titles.

For every reference to another internal corporate document found in the source:

1. **Doc-id present** (e.g., "per SOP-000355609"): Format as `[SOP-000355609 — Title from INDEX]`
2. **Title only** (e.g., "per the Risk Management Policy"): Search INDEX for match. If found: `[DOC-ID — Title]`. If not: `[Title]` with `<!-- ref: unresolved, title-only -->`
3. **Informal** (e.g., "the DTM"): Best-effort match with `<!-- ref: "the DTM" matched to DOC-ID -->`. If ambiguous: `<!-- ref: unresolved -->`
4. **External standards** (e.g., "ISO 14971"): `[ISO 14971]` — no resolution needed

Track all references for frontmatter:

```yaml
references:
  - doc_id: "SOP-000355609"
    title: "Risk Management File Process"
    resolved: true
  - doc_id: null
    title: "the DTM"
    resolved: false
    note: "ambiguous"
```

### Phase 6: Build Frontmatter

Read the frontmatter template from `{{SKILL_DIR}}/templates/frontmatter-source.md` and populate all fields. Write the complete frontmatter at the top of the markdown file.

### Phase 7: Self-Validate (end-of-conversion checks)

Run **every** check below against the staged output before attempting Phase 8 commit. Any Required failure means abort commit and leave staging for inspection.

#### Structural checks

| Check | Required? |
|-------|----------|
| All frontmatter fields populated | Yes |
| At least one H1 and one H2 | Yes |
| Word count > 50 (excluding frontmatter) | Yes |
| If `conversion_fidelity: partial`, `notes:` field is non-empty | Yes |

**Note on `conversion_fidelity` (X1)**: A blank-form XLSX template with all cells reproduced as `[____]` placeholders is `faithful`, NOT `partial`. Use `partial` only when source content could not be extracted (scanned PDF with failed OCR, encrypted/password-protected, truncated extraction, etc.). Template structure preserved with placeholders = faithful conversion of a template.

#### Image checks — end-of-conversion (F10, F2, F11)

For each `![alt](path)` in the markdown body:

| Check | How | Required? |
|-------|-----|----------|
| **Path resolves from markdown's final location** (F10) | For ref `![...](../images/foo.png)` in a markdown file that will land at `{{OUTPUT_DIR}}/file.md`, the resolved path is `{{OUTPUT_DIR}}/../images/foo.png`. `test -f` this path against the STAGING-preview location (`{{STAGING_DIR}}/images/foo.png`, since OUTPUT_DIR is one directory above images/ in both staging and final layouts). If `{{OUTPUT_DIR}}` ends in a DOC_TYPE subfolder (Forms/SOPs/Policies/Work Instructions/Standards), the prefix MUST be `../images/` — not `images/` | Yes |
| **Every extracted content image in `{{STAGING_DIR}}/images/` is referenced at least once** in the markdown body | grep for each filename in the markdown | Yes |
| **Duplicate refs to the same image are permitted** (F2) | Do NOT flag multiple `![...](../images/X.png)` pointing to the same file as an error — common pattern in bilingual/repeated content | Validation rule adjustment, not a check |
| **Every content image referenced has been orientation-checked** (F1, PDF only) | Confirm you ran `Read` on each PNG and text is right-side-up; if any image was flipped, note which in the output summary | Yes (PDF) |
| **Every content image has an F11-CLASSIFY marker** (F11, v28+) | For every `![...](..)` reference to a content image (non-decorative), the line immediately above must carry a `<!-- F11-CLASSIFY: descriptor="..." type="(a\|b\|c\|d\|e\|review)" mermaid-emit="(required\|skip)" skip-reason="..." -->` comment. Marker schema must match F11 section 4.7. Missing markers fail hard — the classification decision must be observable, not inferred | **Required** |
| **Every F11-CLASSIFY with `mermaid-emit="required"` has an adjacent Mermaid block** (F11, v28+) | For every marker with `type` ∈ {a, b, c} AND `mermaid-emit="required"`, a ```mermaid fence MUST appear within 5 lines after the image reference, with the caption appearing AFTER the Mermaid block. Promoted from Warning to Required in v28 after task ben/087 surfaced ~90% per-doc miss rate under the prior Warning-only gate | **Required** |
| **Every F11-CLASSIFY with `mermaid-emit="skip"` has a valid `skip-reason`** (F11, v28+) | `skip-reason` ∈ {matrix, ui-capture, photograph, decorative, ambiguous-needs-review}. Empty or missing `skip-reason` on a skip marker is a hard fail. `type="review"` markers MUST also carry an adjacent `%% REVIEW: MERMAID-CLASSIFY-AMBIGUOUS — ... %%` comment explaining what made the classification ambiguous | **Required** |
| **Mermaid supplement emitted at EVERY image occurrence including translated sections** (F11) | Bilingual docs show the same image at each language section — the Mermaid supplement is emitted inline at every occurrence, never cross-referenced "see English section above". The image file is one-to-many but the Mermaid is one-to-one with each image reference | **Required** |
| **Every flow-diagram caption appears BELOW its Mermaid block** (not above) | Regex: after each ```mermaid ... ``` block on a flow diagram, the next non-blank line must contain `*Figure N.` or equivalent. If the caption appears above the Mermaid, reorder | Warning only |
| **No `## Image Manifest` section in the body** (4.8) | The manifest was dropped — inventory lives in the optional `images:` frontmatter array and in the inline captions. If a manifest section exists, remove it | Warning only |

#### Page marker checks (PDF only)

| Check | How | Required? |
|-------|-----|----------|
| **Page markers present for multi-page PDFs** (4.9) | `pdfinfo` gives total pages M. If M ≥ 3, body should contain at least `floor(M/3)` `*— End of Page N of M —*` markers at natural section/paragraph boundaries. Skip for M ≤ 2 | Warning only |
| **Markers use correct total page count** | Every marker must reference the same total M from `pdfinfo`. Inconsistent totals indicate a conversion error | Yes (if any markers present) |
| **EN→DE (or other multi-language) boundary annotated** | If the document contains a second-language section (detect via heading like `## Deutsche Übersetzung`, `## Français`, etc.), the marker immediately before that section must include `(end of <primary-language> section)` | Warning only |

#### Content checks

| Check | Required? |
|-------|----------|
| Markdown table count ≥ estimated source table count | Warning only |
| If form fields expected, at least one `[____]` / `- [ ]` / `[SIGNATURE ...]` marker present | Warning only |
| Source typos preserved verbatim with `<!-- sic -->` markers (X6) — do NOT silently correct | Warning only (honor-system — hard to automate) |
| Cross-references formatted as `[DOC-ID — Title]` or `[Title]`, not bare prose | Warning only |

Report every check with pass/fail/warning. If any Required check fails, do NOT proceed to Phase 8 — return a failure summary listing which checks failed and leave `{{STAGING_DIR}}` intact.

### Phase 8: Commit or Fail — Transactional Sequence (F5, F9)

**All or nothing.** If any step fails mid-sequence, abort immediately and leave `{{STAGING_DIR}}` intact with a marker file explaining which step failed. Never leave the filesystem in a half-committed state (markdown landed but images missing, or images landed but path refs still wrong).

Execute in this exact order:

```
Step 1: Ensure targets exist
  mkdir -p "{{OUTPUT_DIR}}"
  mkdir -p "{{IMAGE_DIR}}"

Step 2: Move images FIRST (images must exist before markdown references them)
  For each file X in {{STAGING_DIR}}/images/:
    mv "{{STAGING_DIR}}/images/X" "{{IMAGE_DIR}}/X"

Step 3: Verify every image arrived at destination
  For each expected filename X:
    test -f "{{IMAGE_DIR}}/X"  # must pass
  If ANY test fails → abort, write {{STAGING_DIR}}/COMMIT_FAILED.txt explaining which image
    is missing, do NOT proceed to Step 4

Step 4: Verify every markdown image reference resolves from the final OUTPUT_DIR
  For each ![...](path) and manifest [text](path) in the markdown:
    resolved = os.path.normpath("{{OUTPUT_DIR}}" + "/" + path)
    test -f "$resolved"  # must pass
  If ANY ref is broken → abort, write {{STAGING_DIR}}/COMMIT_FAILED.txt explaining which
    ref doesn't resolve, do NOT proceed to Step 5

Step 5: Move markdown file
  mv "{{STAGING_DIR}}/<filename>.md" "{{OUTPUT_DIR}}/<filename>.md"

Step 6: Verify markdown arrived
  test -f "{{OUTPUT_DIR}}/<filename>.md"
  If fails → abort, write {{STAGING_DIR}}/COMMIT_FAILED.txt, do NOT proceed

Step 7: Clean up staging (ONLY after all above succeed)
  rm -rf "{{STAGING_DIR}}"

Step 8: Return success summary
```

**If any Required check from Phase 7 failed** (before reaching Phase 8):
1. Leave `{{STAGING_DIR}}/` intact — don't move anything.
2. Write `{{STAGING_DIR}}/VALIDATION_FAILED.txt` listing which checks failed.
3. Return failure summary.

**If a Phase 8 step fails mid-sequence**:
1. Do NOT roll back already-moved files (images already promoted are fine in `{{IMAGE_DIR}}/` — they're content-addressed by doc-id).
2. Leave `{{STAGING_DIR}}/` intact with the remaining files.
3. Write `{{STAGING_DIR}}/COMMIT_FAILED.txt` with the exact failed step and what state the filesystem is in.
4. Return failure summary. A human can inspect staging, fix the cause, and retry the commit.

## Output

Return a summary in this format:

```
RESULT: SUCCESS | FAILURE

Document: {{DOC_ID}} — {{TITLE}}
Format:   {{FORMAT}}
Output:   {path to written file, or "in staging"}

Content:
  Sections: N
  Tables:   N
  Images:   N extracted, N decorative omitted

Cross-references:
  Resolved:   N
  Unresolved: N

Quality:
  Required checks: N/N passed
  Warnings:        N

Notes:
  - {any conversion notes, approximations, or issues}
```
