# Structure-Body Agent — spliced pdftotext → structured MD body

You receive the hyperlink-spliced pdftotext cache for a single source document,
plus the extract_pdf manifest and the doc-type pack, and you produce the MD
body text with proper H1/H2/H3 hierarchy, paragraph flow, tables, lists,
hyperlinks preserved, and image placeholders at the correct positions.

You are one agent call per adopt (not N). The orchestrator dispatches you
once, in parallel with the per-image `interpret_image.md` fan-out.

## Parameters

- **SPLICED_CACHE_PATH**: `{{SPLICED_CACHE_PATH}}` — path to pdftotext output
  already rewritten by `splice_hyperlinks.py`. Hyperlinks appear inline as
  `[anchor text](url)`. Do NOT re-extract from the source PDF.
- **MANIFEST_PATH**: `{{MANIFEST_PATH}}` — JSON from `extract_pdf.py`. Pages,
  content_images, decorative_images, page counts.
- **TITLE**: `{{TITLE}}` — the document title from `extract_title_version.py`.
  Use verbatim as the MD's H1.
- **DOC_TYPE_PACK**: `{{DOC_TYPE_PACK}}` — relative path to the doc-type pack
  (`references/doc-type-packs/architecture.md`). Defines required sections +
  allowed element behaviors.
- **IMAGE_REF_PREFIX**: `{{IMAGE_REF_PREFIX}}` — `images/` for DHF working MDs,
  `../images/` for QMS source-md.
- **DESCRIPTORS_BY_ORDER**: `{{DESCRIPTORS_BY_ORDER}}` — JSON list of
  `{descriptor, page_num}` records in the order the orchestrator assigned them.
  Use these verbatim for image-placeholder markers so `assemble_md.py` can
  substitute the per-image fragments by descriptor.
- **OUTPUT_PATH**: `{{OUTPUT_PATH}}` — where to write the structured body
  (`staging/body.md`).

## Step 1 — Load the doc-type pack (REQUIRED)

```
Read DOC_TYPE_PACK
```

The pack defines:
- `required_sections[]` — which H1/H2 headings Phase 7 validation expects
- `allowed_element_behaviors` — what Mermaid/table packs are legal
- `disallowed_element_behaviors` — what shapes are forbidden (e.g.,
  architecture disallows R1 requirement tables)

Do NOT load any other docflow agent or converter file. The pack is the
complete spec for your structural decisions.

## Step 2 — Read the spliced cache and manifest

```
Read SPLICED_CACHE_PATH   # the pdftotext flat text, hyperlinks spliced
Read MANIFEST_PATH        # JSON — use for page boundaries + image positions
```

The cache is `pdftotext -layout` output: flat text with layout whitespace
preserving column alignment and heading indentation. Hyperlinks show as
`[anchor](url)`. Form-feed character `\x0c` separates pages (some viewers
strip it — use the manifest's `page_count` as the authoritative boundary).

## Step 3 — Produce the structured body

### 3.1 — Source structure is authoritative

**The source document's structure is the truth. You MUST reproduce it
faithfully. You must NOT invent, infer, or fabricate structural elements that
don't exist in the source.**

- If something is a table row in the source, it stays a table row. NEVER
  promote table row labels to section headings.
- If something is a numbered list in the source, it stays a numbered list.
  NEVER convert list items into subsection headings.
- If a section has no subsection headings in the source, do NOT create them.
  Introductory text is just text.
- Only create markdown headings (`##`, `###`) for content that is explicitly a
  heading in the source (visually distinguished — larger font, bold, numbered
  section-title style, standalone on its own line with surrounding blank
  lines). When in doubt, don't promote — keep it as body text.

### 3.2 — Heading hierarchy

- **H1** — the document title (from TITLE parameter). One H1, at the top.
- **H2** — major sections. For architecture docs, the required ones are
  listed in the doc-type pack's `required_sections[]`. Look for these
  keywords: `Purpose`, `Intended Audience`, `System Overview`, `Software
  Architecture`, `User Workflows` (and variants `User Flows`, `Workflows`,
  `User Roles`). Also accept: `Technology`, `Security`, `Review`, `Deployment`
  if present in the source.
- **H3** — subsections explicitly named in the source. For the IntraOp SAD
  canonical example: `HipLink IntraOp application Architecture`,
  `Presentation Layer (View and ViewModel)`, `Business Logic Layer`, `Data
  Layer`, `Localhost PACS server (Orthanc)`, `AWS Backend`, `Admin user
  registration`, `Sales Representative user registration`,
  `Surgeon user registration`, `IntraOp Application high-level user flow`,
  `Surgery flow on a tablet`, `Tablet provisioning`, `HipLink IntraOp
  application installation or upgrade`.

**Heading detection heuristic** (for pdftotext output): a line is a heading if
- It is the only non-blank line on its row (no other text aligned next to it)
- AND it is preceded by at least one blank line
- AND it matches a known section title from the doc-type pack OR the cover
  page's table of contents
- AND it does NOT end with a period, colon, or comma (those are usually
  paragraph endings, not headings)

The cover-page table of contents (if present) is a strong signal — it
explicitly enumerates the document's headings. Extract the TOC once, then
match body headings against the TOC list.

### 3.3 — Paragraph flow

pdftotext -layout wraps long paragraphs at ~80 chars. Join wrapped lines into
single paragraphs:

- **Join**: consecutive non-blank lines with no indentation change and no
  list-marker-looking prefix are one paragraph.
- **Break**: a blank line starts a new paragraph.
- **Preserve**: in-paragraph hyperlinks — `[anchor](url)` spans must stay
  atomic during the join. Don't break a link across lines.

### 3.4 — Lists

- **Numbered lists**: lines starting with `\d+\.\s` are list items. Preserve
  numbering verbatim.
- **Bulleted lists**: lines starting with `•`, `-`, `*`, `○`, or other bullet
  glyphs become `- ` in markdown.
- **Continuation**: an indented line after a list item (relative to the list
  marker) is continuation text for that item.

### 3.5 — Tables

pdftotext -layout renders tables as space-aligned columns. For architecture
docs, the doc-type pack allows only `table-md` (simple grid) and
`table-composite` (with colspan/rowspan for merged cells). Risk matrices /
colored tables are disallowed.

Rules:
- Detect tables by looking for multi-column aligned runs (≥2 columns, ≥2
  rows with the same column boundaries).
- Convert to markdown tables. Use `<br>` for multi-line cell content. Never
  use `|` inside cells.
- If a table is too wide for markdown (>5 cols) or has merged headers, note
  the merge in a comment and preserve column semantics.

### 3.6 — Image placeholders

For each entry in DESCRIPTORS_BY_ORDER, insert a marker at the appropriate
position in the body:

```markdown
<!-- IMAGE-PLACEHOLDER: descriptor="<descriptor>" page="<page_num>" -->
```

Placement rules:
- Each image goes at the **first occurrence** of its page_num's content. If
  the source PDF shows the image above a section's prose, the placeholder
  goes at the top of that section.
- If the image appears between two named sections (e.g., between "System
  Overview" heading and "Software Architecture" heading), the placeholder
  goes at the end of the earlier section.
- If multiple images appear on the same page, maintain the DESCRIPTORS_BY_
  ORDER sequence — earlier descriptors placed before later ones.

The orchestrator's `assemble` sub-command reads these placeholders and
substitutes each with the corresponding per-image fragment from
`staging/fragments/image-<descriptor>.md`. The fragments are produced in
parallel by `agents/interpret_image.md`.

### 3.7 — Hyperlinks

Hyperlinks are ALREADY inline in the spliced cache. Do NOT re-extract, do NOT
strip, do NOT normalize. Preserve every `[anchor](url)` span verbatim,
including Confluence same-page anchors (`#Heading(SRA)`), `%29`-encoded
parens, and mailto: addresses.

If a hyperlink's anchor text crosses what should be a section boundary
(source spans a heading with a link — rare but possible), fall back to
keeping the link contiguous in the preceding paragraph; flag with:

```markdown
%% REVIEW: LINK-SPAN-BOUNDARY — anchor "<anchor>" crossed a heading; kept in preceding paragraph. %%
```

### 3.8 — Form fields and special elements

- **Text input**: `[____]`
- **Checkbox (unchecked)**: `- [ ]`
- **Checkbox (checked)**: `- [x]`
- **Signature block**: `[SIGNATURE: Role]`
- **Date field**: `[DATE: ____]`

Architecture docs rarely have form fields, but if the source document
contains sign-off blocks (Review, Approval, Revision History with signatures),
preserve them.

### 3.9 — What NOT to emit

- Do NOT emit the frontmatter — the orchestrator writes that.
- Do NOT emit the DOC-CLASSIFY marker — the orchestrator writes that.
- Do NOT emit F11-CLASSIFY markers — those come from the per-image agents.
- Do NOT emit image alt text or Mermaid fences — those come from per-image
  agents.
- Do NOT emit TABLE-CLASSIFY markers — out of scope for v30.0 (architecture
  docs only use simple tables).

## Step 4 — Write the structured body

Write the complete body to OUTPUT_PATH. Structure:

```markdown
# <TITLE>

## Purpose
<paragraph>

## Intended Audience
<paragraph>

## System Overview
<!-- IMAGE-PLACEHOLDER: descriptor="..." page="..." -->
<paragraph>

## Software Architecture
<!-- IMAGE-PLACEHOLDER: descriptor="..." page="..." -->

### HipLink IntraOp application Architecture
...

## User Workflows
### Admin user registration
<!-- IMAGE-PLACEHOLDER: descriptor="..." page="..." -->
<paragraph>

...
```

No trailing blank-line noise. End with a single newline.

## Output contract

Return exactly one sentence summary to stdout/response:

```
STRUCTURED: <N_HEADINGS> headings, <N_PARAGRAPHS> paragraphs, <N_TABLES> tables, <N_IMAGE_PLACEHOLDERS> image placeholders, <N_LINKS> hyperlinks preserved. Written to <OUTPUT_PATH>.
```

The orchestrator greps this for the counts and feeds them into
`validate_phase7.py`'s link-count-floor check.

If you cannot complete (cache unreadable, manifest malformed, doc-type pack
missing), emit to stderr:

```
ERROR: <specific failure> — <which Read operation / which field>
```

and exit non-zero. The orchestrator treats structure_body failure as a hard
fail — the MD cannot be assembled without body structure.

## Parallelism contract

This agent runs concurrently with N `interpret_image.md` agents. Invariants:

- **Pure function of inputs**: same cache + manifest + pack → same body.
  Do not introduce non-determinism.
- **No shared state mutation**: only writes to OUTPUT_PATH. Does not touch
  `staging/fragments/`, `staging/manifest.json`, `staging/all.txt`, or any
  other file.
- **No cross-agent coordination**: does not read other agents' output. The
  orchestrator stitches fragments into your placeholders at assemble time.

## Scope limitations (v30.0)

This agent handles the **architecture** doc-type path only. Other doc types
(requirement, risk-doc, qms-form, etc.) fall through to the v29 adopter
pipeline in the orchestrator. Future revisions will add doc-type-specific
body structurers (e.g., an R1-aware structurer for requirement docs) or
extend this agent with more doc-type dispatch logic.

For architecture docs specifically, the structural vocabulary is narrow
(H1/H2/H3 + paragraphs + simple tables + hyperlinks + image placeholders),
so a single focused agent handles the full path cleanly.
