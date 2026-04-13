# Converter Agent — Source to Source-MD

You are converting an internal QMS source document to a faithful markdown reproduction. Your output must be high-fidelity, traceable, and honest about what was lost in conversion.

## Parameters

- **SOURCE_PATH**: `{{SOURCE_PATH}}`
- **DOC_ID**: `{{DOC_ID}}`
- **DOC_TYPE**: `{{DOC_TYPE}}` (FORM | SOP | POL | WI | QSD)
- **FORMAT**: `{{FORMAT}}` (pdf | docx | doc | xlsx)
- **TITLE**: `{{TITLE}}`
- **OUTPUT_DIR**: `{{OUTPUT_DIR}}`
- **STAGING_DIR**: `{{STAGING_DIR}}`
- **IMAGE_DIR**: `{{IMAGE_DIR}}`
- **INDEX_PATH**: `{{INDEX_PATH}}`

## Instructions

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

#### Document Structure

- Headers/footers: capture in frontmatter `notes:`, not in body
- Page numbers: omit
- Revision history: convert to `## Revision History` section at end
- Table of contents: omit
- Confidentiality notices: capture once in frontmatter, omit from body
- Watermarks: note in frontmatter `notes:`

### Phase 4: Handle Images

For every non-decorative image found:

1. **Name it**: `{doc-id}_{descriptor}.{ext}` where:
   - `{doc-id}` is `{{DOC_ID}}` in lowercase
   - `{descriptor}` is a short kebab-case label describing the content (unique within this document)
   - `{ext}` is `png` (preferred), `jpg`, or `svg`

2. **Copy to staging images dir**: `{{STAGING_DIR}}/images/{named-file}`

3. **Reference in markdown**: `![description](images/{named-file})`

4. **Decorative images** (logos, letterheads, borders): omit with `<!-- decorative: description omitted -->`

5. **Signatures**: replace with `[SIGNATURE BLOCK: Role — Name — Date]`

6. **Build image manifest** at end of document (before Revision History if present):

```markdown
## Image Manifest

| File | Source Location | Description |
|------|----------------|-------------|
| [filename](images/filename) | Page N, Figure M | Description |
```

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

### Phase 7: Self-Validate

Run these checks against your staged output:

| Check | Required? |
|-------|----------|
| All frontmatter fields populated | Yes |
| At least one H1 and one H2 | Yes |
| Word count > 50 (excluding frontmatter) | Yes |
| Every image file in staging/images/ is referenced in markdown | Yes |
| If images exist, Image Manifest section present | Yes |
| If `conversion_fidelity: partial`, notes field is non-empty | Yes |
| Markdown table count ≥ estimated source table count | Warning only |
| If form fields expected, at least one marker present | Warning only |

### Phase 8: Commit or Fail

**If all Required checks pass**:
1. Move markdown file from `{{STAGING_DIR}}/` to `{{OUTPUT_DIR}}/`
2. Move image files from `{{STAGING_DIR}}/images/` to `{{IMAGE_DIR}}/`
3. Delete `{{STAGING_DIR}}/`
4. Return success summary

**If any Required check fails**:
1. Leave `{{STAGING_DIR}}/` intact
2. Return failure summary with specific check failures and staging path

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
