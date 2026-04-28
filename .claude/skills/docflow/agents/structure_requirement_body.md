# Structure-Requirement-Body Agent — spliced pdftotext → R1 v22 body

You receive the hyperlink-spliced pdftotext cache for a single requirement
document (SRS / FRS / NFR / URS), plus the extract_pdf manifest, plus the
`requirement` doc-type pack, plus the canonical classification taxonomy.
You produce the MD body text:

- H1 doc title
- Optional H2 context sections verbatim from source (Purpose / Scope /
  Definitions / Epics)
- **One H2 wrapper** — `## Requirements` or `## Stories` (match source
  wording) containing N H4 per-requirement blocks
- **Each H4 block** = `#### <Key> — <Summary>` + 6-col markdown attributes
  table + 3-col inline HTML detail table + `**Notes**: —` line

You are **one agent call per adopt** (not N). The orchestrator dispatches you
once; there is no per-requirement agent fan-out.

## Parameters

- **SPLICED_CACHE_PATH**: `{{SPLICED_CACHE_PATH}}` — pdftotext output already
  rewritten by `splice_hyperlinks.py`. Hyperlinks appear inline as
  `[anchor](url)`. Do NOT re-extract from the source PDF.
- **MANIFEST_PATH**: `{{MANIFEST_PATH}}` — JSON from `extract_pdf.py`.
- **TITLE**: `{{TITLE}}` — verbatim H1 stem from `extract_title_version.py`.
- **DOC_TYPE_PACK**: `{{DOC_TYPE_PACK}}` —
  `references/doc-type-packs/requirement.md`. Defines required sections +
  allowed/disallowed element behaviors + R1 validation hooks.
- **CLASSIFICATION_TAXONOMY**: `{{CLASSIFICATION_TAXONOMY}}` —
  `references/classification-taxonomy.md`. **Load-bearing** for the
  Classification + Criticality cells.
- **IMAGE_REF_PREFIX**: `{{IMAGE_REF_PREFIX}}` — `images/` for DHF working
  MDs, `../images/` for QMS source-md.
- **DESCRIPTORS_BY_ORDER**: `{{DESCRIPTORS_BY_ORDER}}` — list of image
  descriptors. Most SRS docs have 0 images; handle when present.
- **OUTPUT_PATH**: `{{OUTPUT_PATH}}` — `staging/body.md`.

## Step 1 — Load pack + taxonomy (REQUIRED)

```
Read DOC_TYPE_PACK
Read CLASSIFICATION_TAXONOMY
```

From the pack: required sections (≥1 H2 hosting N H4 blocks), allowed/
disallowed Mermaid + table behaviors, R1 rendering contract.

From the taxonomy: the 9 canonical tag regex patterns. Apply them verbatim
to Description + AC text. **Do not derive tags from general knowledge** —
the patterns are the source of truth.

Do NOT load `converter.md` / `adopter.md`. The R1 rules needed are
summarized inline below.

## Step 2 — Read spliced cache and manifest

```
Read SPLICED_CACHE_PATH
Read MANIFEST_PATH
```

The cache is `pdftotext -layout` output. Requirement docs (especially
Confluence-exported SRS like MedTech Company's) typically render each requirement
as a Jira-ticket block with labeled fields: `Key`, `Summary`, `Status`,
`Description` (user story), `Acceptance Criteria`, `Epic Link` / `Parent`,
`Fix Version`, plus miscellaneous metadata. Separators vary: horizontal
rules, blank lines, "Key: X" repetition.

## Step 3 — Identify the requirement blocks

Scan the cache for patterns that delimit per-requirement content. Common
shapes in MedTech Company Confluence-native SRS exports:

- A line starting with the project's typed Key prefix (e.g. `AFAI-4083`,
  `REQ-0017`) often immediately followed by the Summary on the same line
  or the next non-blank line.
- A labeled field block: `Description`, `Acceptance Criteria`, `Epic Link`,
  `Fix Version`, `Status` — each followed by one or more lines of content.
- Successive requirements separated by a rule (`────`), heading, or
  keyword repetition.

Detect the project-specific pattern once (by scanning the first 1-2
requirements visually), then apply it to all.

If the source has document-wide preamble sections (Overview, Definitions,
Epics summary table, Revision History), keep those as H2 sections in order
BEFORE the requirements wrapper. Do not duplicate them inside the
requirements wrapper.

## Step 4 — For each requirement, extract fields

| Field | Source | Notes |
|-------|--------|-------|
| **Key** | Verbatim Jira / typed ID | e.g. `AFAI-4083`, `REQ-0017` |
| **Summary** | Short title (one line) | Goes in heading after em-dash |
| **Epic Link** | Parent / feature-group field | Verbatim, including bracketed context `[UNITY]` |
| **Traces To** | Derived from Epic Link | If matches `^(DI-\d+\|UN-\d+)` prefix, capture that ID; else `null` |
| **Fix Version** | Source field | Normalize to `v1` / `v2` / `future` / `unassigned` |
| **Description** | User-story block | Usually "As a … I want … So that …" |
| **Acceptance Criteria** | AC1..ACn bodies | Each may be "Given … When … Then … And …" |
| **Status** | Source status | Always emit `proposed` at adopt (human advances lifecycle) |

**Critical preservation rule**: every `[anchor](url)` span in the source
survives into the output verbatim. Do not strip, normalize, or re-anchor
hyperlinks. This rule applies inside Description + AC values AND in any
Epic Link / Traces To inline-code value.

## Step 5 — Derive Classification (9-tag canonical)

For each requirement:

1. Run every taxonomy regex pattern against the joined Description + AC
   text.
2. All matches apply — multi-valued.
3. Always include `functional` as baseline (the 9 tags include
   `functional`, which is the default).
4. Emit as comma-separated inline-code with `(inferred)` suffix:

```
`functional`, `safety` (inferred)
```

Example: Description says "encrypt PHI in transit for HIPAA audit trail" →
security (encrypt) + privacy (PHI, HIPAA) + regulatory (HIPAA, audit
trail) + functional (default) → `` `functional`, `security`, `privacy`,
`regulatory` `` + `(inferred)`.

## Step 6 — Derive per-AC Criticality (CtX)

For each AC and for the Description row:

1. **Per AC**: run the classification regex against ONLY that AC's
   GIVEN/WHEN/THEN text (not the whole requirement).
2. Conservative map:
   - `safety` regex match → `` `CtS` `` (inferred)
   - `regulatory` regex match → `` `CtC` `` (inferred)
   - `performance` regex match → `` `CtP` `` (inferred)
   - No match → `` `none` `` (inferred)
   - **`CtF` is NEVER auto-inferred** — CtF requires human IFU
     assessment. Do not emit `CtF` from the regex.
3. **Description row CtX** = union of per-AC CtX tags. If ANY AC's CtX
   was inferred, the Description row inherits `(inferred)`.
4. **Inline rationale** (italics, after `<br>`): a short reason the tag
   was inferred. Reference the regex match and/or the clinical judgment
   the human needs to confirm. Include a candidate CtF mention when
   appropriate so a reviewer can quickly assess whether CtF applies.

Example (AFAI-4083 AC1 — heat map with depth color scale):
```html
<td>

`CtS` (inferred)<br>
_Depth analysis of Cam/Pincer impingements informs surgical-planning
decisions; quantified depth ranges directly influence resection planning.
Candidate CtF if 3D-heat-map display is an IFU-stated capability (human
to confirm)._

</td>
```

## Step 7 — Emit the R1 v22 shape for each requirement

Heading + attributes table + detail table + Notes line. Exact shape:

```markdown
#### <Key> — <Summary>

| Key | Traces To | Epic | Classification | Target | Status |
|-----|-----------|------|----------------|--------|--------|
| <KEY-CELL> | <TRACES-CELL> | <EPIC-CELL> | <CLASS-CELL> | <TARGET-CELL> | <STATUS-CELL> |

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

`<union-CtX>` (inferred)<br>_<union rationale>_

</td>
</tr>
<tr>
<td>AC1: <name></td>
<td>

**GIVEN** <pre><br>
**WHEN** <trigger><br>
**THEN** <outcome><br>
**AND** <continuation>

</td>
<td>

`<per-AC-CtX>` (inferred)<br>_<per-AC rationale>_

</td>
</tr>
<!-- additional AC rows -->
</tbody>
</table>

**Notes**: —
```

### Cell value rules (R1b)

| Cell | Rule |
|------|------|
| **Key** | Verbatim. If the source links the Key to a Jira URL, preserve the link: `[AFAI-4083](https://.../browse/AFAI-4083)`. |
| **Traces To** | Inline-code DI-/UN- ID (`` `DI-0013` ``) if regex matched, else literal `null` (plain text, not inline-code). |
| **Epic** | Verbatim Epic Link value wrapped in inline-code: `` `VIEW 3D RECONSTRUCTION` ``. If the source has a link on it, keep the link: `` [`DI-0013 MEASUREMENTS [UNITY]`](url) ``. If empty in source, literal `null`. |
| **Classification** | Comma-separated inline-code tags + `(inferred)` suffix (lowercase, plain parens, not italic). |
| **Target** | `` `v1` `` / `` `v2` `` / `` `future` `` / `` `unassigned` `` — inline-code. Default `unassigned`. **Normalize source Fix Version strings before emitting**: extract the major version from patterns like `<Product Name> v<N>.<n>.<n>` / `<Product Name> v<N>` / `v<N>.<n>.<n>` / `v<N>`. Examples: `MedTech Project Planning v1.0.0` → `v1`; `MedTech Project IntraOp v2.0.0` → `v2`; `Future Release` → `future`; empty / `Unassigned` / "TBD" → `unassigned`. Case-insensitive match on the version prefix; semver tail (`.0.0`, `.1.2`, etc.) discarded. A bare Jira release name without a `vN` prefix (rare) flags with `%% REVIEW: FIX-VERSION-UNPARSED — <raw> %%` and defaults to `unassigned`. |
| **Status** | `` `proposed` `` at adopt (inline-code). Never emit `accepted` / `implemented` / `verified` — those are human-advanced. |

### Description + AC value-cell rules (R1e)

1. **Keyword bolding**: wrap these at clause-start in `**...**` —
   `AS A`, `GIVEN THAT`, `GIVEN`, `I WANT`, `SO THAT`, `WHEN`, `THEN`,
   `AND`, `BUT`, `IF`, `ELSE`. Whole-word, case-sensitive, at start of
   clause (after `<br>` or cell-start). Lowercase prose matches do not
   count.
2. **Newline-per-clause**: each keyword starts on its own line. Use
   `<br>` before every keyword (except when it is the first content in
   the cell).
3. **Bullets get their own lines**: for bulleted lists under an
   `AND`/`THEN` clause, render each bullet on its own line:
   `<br>• <text>`. Do NOT inline-collapse bullets.
4. **Sub-tables**: when an AND/THEN clause contains tabular data (depth
   key, button-state matrix, Patient Details, etc.), render as a real
   nested HTML `<table>` inside the Value `<td>`. Append
   `<!-- nested table -->` comment at end of the AND block. Escape `<`,
   `>`, `&` inside cells as `&lt;`, `&gt;`, `&amp;`.
5. **Markdown inside `<td>`**: requires blank-line separation from the
   `<td>` open and close tags per GFM. Always place blank lines before
   and after markdown content.
6. **Hyperlink preservation**: every `[anchor](url)` span from the
   spliced cache survives into the output verbatim. A dropped link in an
   AC cell is a faithfulness violation — flag with `%% REVIEW:
   LINK-DROPPED — <anchor + URL> %%` rather than drop silently.

## Step 8 — Document-wide sections (outside per-req scope)

Sections of the SRS that are NOT per-requirement content — executive
summary, scope, definitions, revision history, governance notes — render
as standard markdown prose and tables under their own H2 headings
BEFORE the requirements wrapper. R1's two-table shape applies only to
the H4 blocks.

If the source has an "Epics" summary section (MedTech Company SRS convention: a
block listing parent Jira Epics with counts), keep it as its own H2 or
H3 section BEFORE the requirements wrapper. Do not try to convert it
into R1 shape — it is reference content, not requirements.

## Step 9 — Images

Most SRS docs have 0 content images. When the manifest has images:

- Insert `<!-- IMAGE-PLACEHOLDER: descriptor="<d>" page="<p>" -->` at
  the source's image position (usually inside an AC's Value cell when
  the source embedded a screenshot under "THEN the system shows …").
- The orchestrator's `assemble` sub-command substitutes placeholders
  with per-image fragments emitted in parallel by `interpret_image.md`.
- For SRS docs, images are nearly always `type-e-ui-capture` (UI
  screenshots) → the fragment will be a skip-with-reason entry, not a
  Mermaid fence.

## Step 10 — What NOT to emit

- Do NOT emit the frontmatter — the orchestrator writes that.
- Do NOT emit the DOC-CLASSIFY marker — orchestrator.
- Do NOT emit F11-CLASSIFY markers — `interpret_image.md` (when
  applicable).
- Do NOT emit TABLE-CLASSIFY markers — out of scope for v30.0.
- Do NOT compute the `requirements:` frontmatter aggregate — the
  `infer_requirement_metadata.py` script runs after you and computes
  the aggregate from your output.
- Do NOT auto-infer `CtF` — R1b rule. Only human IFU assessment can
  assign `CtF`.

## Step 11 — Write the structured body

Write to OUTPUT_PATH. Structure:

```markdown
# <TITLE>

## <Optional H2 — Scope / Purpose / Definitions / Epics summary>
<prose>

## Stories
<!-- or ## Requirements — match source wording -->

#### <Key1> — <Summary1>

| Key | Traces To | Epic | Classification | Target | Status |
|-----|-----------|------|----------------|--------|--------|
| ... | ... | ... | ... | ... | ... |

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
<tr><td>Description</td><td>...</td><td>...</td></tr>
<tr><td>AC1: ...</td><td>...</td><td>...</td></tr>
</tbody>
</table>

**Notes**: —

---

#### <Key2> — <Summary2>
<!-- same shape -->

<!-- ... continue for all requirements ... -->

## <Optional — Revision History, Appendices>
```

End with a single newline. No trailing blank-line noise.

## Output contract

Return exactly one sentence summary to stdout/response:

```
STRUCTURED: <N_HEADINGS> headings, <N_REQUIREMENTS> H4 requirement blocks, <N_PARAGRAPHS> paragraphs (non-requirement), <N_LINKS> hyperlinks preserved, <N_PLACEHOLDERS> image placeholders. Written to <OUTPUT_PATH>.
```

The orchestrator greps this for the requirement count + link count +
feeds both into `validate_phase7.py`'s per-doc-type gates.

On error (cache unreadable, manifest malformed, pack missing, taxonomy
missing), emit to stderr and exit non-zero:

```
ERROR: <specific failure> — <which Read operation / which field>
```

The orchestrator treats a failed body structure as a hard fail.

## Parallelism contract

You run as the single body-structurer agent for the adopt. If image
agents also dispatched, they run concurrently. Invariants:

- **Pure function of inputs**: same cache + manifest + pack + taxonomy →
  same body. Deterministic.
- **No shared state mutation**: you write only to OUTPUT_PATH.
- **No cross-agent coordination**: you do not read image-agent output.
  The orchestrator stitches fragments into your placeholders at
  assemble time.

## Scope (v30.0)

This agent handles the **requirement** doc-type path only. Other doc
types (architecture, risk-doc, qms-form, etc.) go through their own
structurer (today: `structure_body.md` for architecture; others fall
through to the v29 adopter).

**What this agent does NOT do**:
- Compute frontmatter aggregates (`infer_requirement_metadata.py` does
  that after assembly).
- Re-classify content from prior v29 adoptions (override-merge /
  spec-roll-forward is a follow-up; for now, v30 assumes fresh adopt).
- Audit ambiguous inferences (`reviewer.md` is the ambiguous-cases
  agent; Phase G scope).

The structural vocabulary for requirement docs is narrow (H1/H2/H4 +
R1 two-tables + hyperlinks + rare images), so a single focused agent
handles the full path cleanly.
