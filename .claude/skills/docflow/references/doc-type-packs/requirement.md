---
pack_name: requirement
version: 1.0
doc_type: requirement
status: active
required_sections:
  - requirements_or_stories
frontmatter_overlay: templates/frontmatter-by-doc-type/requirement.yml
allowed_element_behaviors:
  mermaid:
    - shared-fidelity
    - type-a-flow
    - type-e-ui-capture
  table:
    - table-md
    - table-composite
    - table-nested
disallowed_element_behaviors:
  mermaid:
    - type-b-logical
    - type-c-component
    - type-c-network
    - type-d-matrix
  table:
    - table-colored
    - table-positional
---

# requirement

Doc-type pack for **requirement** documents — Software Requirements
Specifications (SRS), Functional Requirements Specifications (FRS),
Non-Functional Requirements Specifications (NFR), User Requirements
Specifications (URS). Loaded by the v30 adopt orchestrator when
`classify_doc.py` returns `doc_type=requirement`.

## Required structural sections

The working MD body MUST contain **one H2 section that hosts the per-
requirement H4 blocks** — typically `## Requirements` or `## Stories` (MedTech Company
convention). Phase 7 validation matches either heading via the loose-match
keyword set `Requirements | Stories | User Stories | Functional Requirements
| Non-Functional Requirements`.

| Section (loose-match H2) | Why required |
|--------------------------|--------------|
| **Requirements** / **Stories** / **User Stories** | Anchor section for the H4 per-requirement blocks |

Optional H2 sections common in SRS docs but NOT required:

- Overview / Scope / Introduction / Purpose
- Definitions / Glossary / Abbreviations
- Epics (summary of parent Jira Epics — *not* per-requirement content)
- References / Related Documents
- Revision History

**The defining structure is the per-requirement H4 blocks**, not an enclosing
section hierarchy. A valid SRS is `## Stories` followed by N `#### <Key> —
<Summary>` blocks. Phase 7 hard-fails if zero H4 requirement blocks are
detected.

## Per-requirement shape (R1 v22)

Each requirement renders as a three-part block under a `####` heading:

1. **H4 heading** — `#### <Key> — <Summary>` (em-dash, single space either
   side). Key verbatim from source; Summary verbatim.
2. **Attributes table** (markdown, 6 columns) —
   `Key | Traces To | Epic | Classification | Target | Status`
3. **Detail table** (inline HTML, 3 columns, `<colgroup>` widths
   10% / 60% / 30%) — `Field | Value | Criticality`. First row is
   `Description`. Subsequent rows are per-AC.
4. **Notes** line — `**Notes**: —` (em-dash when empty).

The full rendering rules live in `agents/converter.md` sections R1a–R1g. The
requirement-specific body structurer agent (`structure_requirement_body.md`)
and the metadata inference script (`scripts/infer_requirement_metadata.py`)
implement these rules. The v30 orchestrator does NOT re-derive the shape;
it dispatches the structurer + inference script and trusts their output.

## Classification inference (mandatory)

Classification is multi-valued and inferred via the 9 canonical tag regex
patterns in `references/classification-taxonomy.md`:

`functional` (always included) + any of `safety | security | privacy |
usability | performance | reliability | interoperability | regulatory` that
match the Description + AC text via their regex patterns.

The taxonomy file is the source of truth — do NOT derive tags from general
knowledge. Emit as comma-separated inline-code with `(inferred)` suffix:

```
`functional`, `safety` (inferred)
```

Human-confirmed values drop the `(inferred)` suffix and must not be
overwritten on re-adopt (override stability — see R1g).

## Per-AC Criticality inference (conservative)

Criticality tags live in the detail table (one per row — Description row +
each AC row). Inference runs per-AC against ONLY that AC's GIVEN/WHEN/THEN
text, per these rules:

| Classification (regex on AC) | CtX (inferred) |
|------------------------------|----------------|
| `safety` match | `` `CtS` `` |
| `regulatory` match | `` `CtC` `` |
| `performance` match | `` `CtP` `` |
| No match | `` `none` `` |
| *(any)* | **`CtF` is NEVER auto-inferred** — requires human IFU assessment |

- Description row CtX = union of AC CtX tags. `(inferred)` propagates if
  ANY AC was inferred.
- Inline rationale (italics) follows each inferred cell on a `<br>`-
  separated line.

Full per-AC inference rules and worked examples: `agents/converter.md` R1b,
R1d (Classification), and `agents/adopter.md` Phase 5e step 4b.

## Allowed element behaviors

**Mermaid**: `type-a-flow` (rare — user-flow diagrams embedded in an AC
occasionally) and `type-e-ui-capture` (screenshots preserved as images with
skip-reason). `shared-fidelity` loaded for every emission. Most SRS docs have
zero Mermaid — they are dense text + tables, not diagrammatic.

**Tables**: `table-md` (simple markdown tables — epic lists, attribute
tables), `table-composite` (colspan/rowspan for merged Jira-list headers),
`table-nested` (multi-paragraph HTML cells with nested `<table>` — the R1e
sub-table pattern for Patient Details / button-state matrix / Depth Key inside
an AC Value cell).

## Disallowed element behaviors

**Mermaid**: `type-b-logical` (containment diagrams), `type-c-component` /
`type-c-network` (topology), `type-d-matrix` (risk / RACI grids) — none of
these shapes belong in an SRS. If the source contains a component or topology
diagram that defines *context* rather than *requirement*, it typically lives in
the architecture doc, not the SRS; flag with `%% REVIEW:
DIAGRAM-MAYBE-OUT-OF-SCOPE %%` rather than emit.

**Tables**: `table-colored` (risk-matrix palette), `table-positional` (form
layout). If an SRS source uses a colored table to visualize requirement
status, drop the coloring and emit as `table-md` — the Classification /
Status columns are already structured.

## Frontmatter overlay — `requirements:` aggregate

Requirement docs carry a document-wide `requirements:` aggregate populated by
`infer_requirement_metadata.py` after all H4 blocks are emitted. Schema in
`templates/frontmatter-by-doc-type/requirement.yml`. Populated fields:

- `count` — total H4 requirement blocks
- `epics` — map of Epic value → occurrence count
- `classification` — map of each of the 9 canonical tags → count (multi-
  valued; a req with 3 tags contributes 3 counts). Includes all 9 keys even
  when zero.
- `criticality` — map of `CtF | CtS | CtC | CtP | none` → count. Multi-
  valued. `CtF` will be 0 at adopt (never auto-inferred).
- `target_releases` — map of target value → count. Keys: `v1`, `v2`,
  `future`, `unassigned` + any project-specific release strings seen in
  source Fix Version fields.
- `traces_to.resolved` / `traces_to.unresolved` — counts by whether the
  Epic Link carried a `DI-\d+` or `UN-\d+` prefix.
- `status` — map of status value → count. Keys: `proposed | accepted |
  implemented | verified | deferred | rejected | superseded`.

## Round-trip rules

On **refresh** (source PDF has a new version; working MD is re-adopted):

1. **Preserve human-edited Classification cells** (detected by absence of
   `(inferred)` suffix). Re-adopt populates only inferred-or-null cells.
2. **Preserve human-edited Criticality cells** same way. If a human has
   removed `(inferred)` and the rationale line, the cell is sticky.
3. **Preserve Status values** — `proposed` becomes `accepted` → `implemented`
   → `verified` over the lifecycle; re-adopt never resets.
4. **Preserve Notes prose** — free-form human content below the detail
   table.
5. **Preserve `%% REVIEW:` markers** — humans resolve them; re-adopt never
   regenerates a resolved marker.
6. **Refresh Description / AC text** when source changed — match by Key. If
   the Description text differs, re-emit with a `%% REVIEW: CONTENT-CHANGED
   — <Key> description / ACs differ from prior adopt %%` marker so the
   human can reassess Classification + Criticality.

On **export** (working MD → DOCX/PDF for formal release):

1. Inline HTML detail tables render as proper tables via pandoc's HTML-in-
   markdown support.
2. DOC-CLASSIFY marker stripped.
3. Review comments (`<!-- %% REVIEW: ... %% -->`) stripped from release
   output — they are authoring metadata, not release content.

## Element-loading order (for `structure_requirement_body.md`)

The orchestrator passes the structurer agent:

1. This doc-type pack — for required-sections + allowed-shapes.
2. `references/classification-taxonomy.md` — load-bearing for the
   Classification cell inference (the 9 regex patterns are definitional).
3. The spliced-hyperlink pdftotext cache + extract_pdf manifest.

The structurer emits the full body (H1 + H2 wrappers + N H4 blocks each with
their two-table shape). The `infer_requirement_metadata.py` script then runs
against the structured body to populate the frontmatter aggregate.

## Validation hooks (for `validate_phase7.py`)

Phase 7 gates specific to requirement docs:

- At least one H2 heading matching the required-section keyword set
- At least one H4 block matching `^#### \S+ — .+` pattern
- **Every H4 block** has BOTH an attributes table (markdown 6-column with
  `Key | Traces To | Epic | Classification | Target | Status` header) AND a
  detail table (inline HTML `<table>` with `<colgroup>` and `Field | Value |
  Criticality` header row)
- **Every attributes-table Classification cell** contains at least one of
  the 9 canonical tags (`functional` minimum)
- **Every Criticality cell** contains one of `` `CtF` ``, `` `CtS` ``,
  `` `CtC` ``, `` `CtP` ``, `` `none` `` (multi-valued allowed)
- **Frontmatter `requirements:` aggregate** is present, has numeric `count`
  matching the H4 block count in the body
- DOC-CLASSIFY marker present with `doc_type="requirement"` and
  `pack="doc-type-packs/requirement.md"`
- **Warn** (not fail) on Traces To values that do not match `^(DI-\d+|UN-
  \d+)$` — these are "unresolved parent, needs human trace" and are legal
  but flagged for review
- **Warn** if any AC Criticality is `CtF (inferred)` — CtF must never be
  auto-inferred per R1b

## Canonical test case

`MedTech Project Planning - Software Requirements Specification (SRS) - 1.0.0` —
Pre-Op SRS, 7 requirements (AFAI-4083, AFAI-3555, AFAI-3554, AFAI-3537,
AFAI-3536, AFAI-3535, AFAI-3518). Fully R1-v22 shaped under v29 adopter.
Ground-truth diff target for v30 re-adopt. Source:
`docs/project/dhfs/mfd-a/design-controls/requirements/formal/MedTech Project
Planning - Software Requirements Specification (SRS) - 1.0.0.pdf`. Expected
v30 Phase 7 outcome: pass; 7/7 H4 blocks with both tables; Classification
regex matches `functional + safety + privacy + usability + performance`
distributed across the 7 requirements.

## Changelog

- 2026-04-21: Stub created during task ben/089 Phase A scaffolding.
- 2026-04-21 (session 4): Populated during task ben/089 requirement doc-type
  extension. Required-section rule is "at least one H2 hosting N H4 blocks";
  allowed/disallowed element lists derived from observed real usage across
  the 3 fully-adopted R1 SRS MDs in the project (Pre-Op SRS 1.0.0, Mgmt
  Services Web SRS, Privacy by Design Requirements). `requirements:`
  aggregate schema ported verbatim from the v29 adopter Phase 5e output.
  Classification + Criticality inference rules pointed into the authoritative
  `references/classification-taxonomy.md` + `agents/converter.md` R1b/R1d
  locations rather than duplicated.
