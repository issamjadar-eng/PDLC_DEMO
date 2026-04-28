---
pack_name: architecture
version: 1.0
doc_type: architecture
status: active
required_sections:
  - purpose
  - intended_audience
  - system_overview
  - software_architecture
  - user_workflows
frontmatter_overlay: null
allowed_element_behaviors:
  mermaid:
    - shared-fidelity
    - type-a-flow
    - type-a-flow-nested
    - type-b-logical
    - type-c-component
    - type-c-network
    - type-e-ui-capture
  table:
    - table-md
    - table-composite
disallowed_element_behaviors:
  mermaid:
    - type-d-matrix
  table:
    - table-colored
    - table-positional
    - table-nested
---

# architecture

Doc-type pack for **architecture** documents — Software Architecture Documents
(SAD), Software Design Documents (SDD), and system architecture records. Loaded
by the v30 adopt orchestrator when `classify_doc.py` returns
`doc_type=architecture`.

## Required structural sections

The working MD body MUST contain H1 or H2 headings matching each of:

| Section (loose-match — H1/H2 with these keywords) | Why required |
|--------------------------------------------------|--------------|
| **Purpose / Overview / Introduction** | States the document's scope and intent |
| **Intended Audience** | Regulatory-document boilerplate required for FDA review |
| **System Overview** | Describes components at the highest level (one paragraph + diagram) |
| **Software Architecture** (or equivalent) | Layer / module decomposition |
| **User Workflows** (or "User Flows" / "Workflows") | How users traverse the system |

Phase 7 validation checks for at least one heading matching each row. An
architecture doc missing "System Overview" or "Software Architecture" fails
Required.

Optional sections that appear in most SADs but aren't strictly required:
- Technology / Framework / Platform(s)
- Security
- Review / Document Control
- Deployment

## Allowed element behaviors

**Mermaid**: `type-a-flow`, `type-a-flow-nested`, `type-b-logical`,
`type-c-component`, `type-c-network`, `type-e-ui-capture` are all allowed. The
`shared-fidelity` pack is loaded for every Mermaid emission.

An architecture doc is expected to have Mermaid — it's the defining element type
for this doc category. A `classify_doc=architecture` MD with zero ```mermaid
fences is a red flag; Phase 7 raises a **warning** (not a hard-fail), since
some architecture docs are pure prose.

**Tables**: `table-md` (simple grid) and `table-composite` (colspan / rowspan)
are allowed. Architecture docs typically use tables for component-to-
responsibility mappings, API endpoint lists, technology choices.

## Disallowed element behaviors

**Mermaid**: `type-d-matrix` is disallowed. A risk-severity matrix or RACI grid
has no place in an architecture doc — it belongs in risk or plan docs. If the
classifier sees a 5×5 grid image, emit it as a markdown table (`table-md`),
not as Mermaid.

**Tables**: `table-colored` (risk-matrix palette), `table-positional` (form
layout), `table-nested` (multi-paragraph cells with nested tables) are
disallowed. These shapes belong to risk docs and forms, not architecture.

## Frontmatter overlay

None. Architecture docs use the base frontmatter schema from
`templates/frontmatter-project.md` plus the always-present identity +
provenance + versioning fields. No type-specific aggregate (unlike
requirement docs' `requirements:` array or risk docs' `hazards:` array).

## Round-trip rules

On **refresh** (source PDF has a new version; working MD is re-adopted):

1. **Preserve all ```mermaid fences** from the existing working MD unless the
   source diagram genuinely changed. The diagnostic is: does the extracted
   image hash differ between versions? If unchanged, keep the prior Mermaid.
   If changed, re-classify and re-emit.
2. **Preserve F11-CLASSIFY markers** that a human has resolved from
   `type="review"` to a concrete type. A human edit on a review marker is a
   one-way decision — don't reopen it.
3. **Preserve caption prose** that diverges from the canonical template
   (humans sometimes add domain-specific context to captions). Match by
   descriptor slug.
4. **Refresh alt text** if source changed; keep alt text if source is
   unchanged.

On **export** (working MD → DOCX/PDF for formal release):

1. Mermaid fences render as SVG + fallback image (pandoc filter).
2. F11-CLASSIFY markers are stripped (they're authoring-only metadata, not
   release content).
3. DOC-CLASSIFY marker is stripped.

## Element-loading order (for `interpret_image.md`)

The orchestrator passes this list to each per-image agent:
1. `references/mermaid-rule-packs/shared-fidelity.md` (always)
2. The type-specific pack based on the agent's classification
   (`type-a-flow.md`, `type-b-logical.md`, etc.)

The agent does NOT load this doc-type pack — the orchestrator has already
applied the pack's allow/deny rules when selecting which type packs to include
in the agent's `MERMAID_PACKS` parameter.

## Validation hooks (for `validate_phase7.py`)

Phase 7 gate checks specific to architecture docs:

- At least one H1/H2 heading matching each required-section keyword set
- DOC-CLASSIFY marker present with `doc_type="architecture"` and
  `pack="doc-type-packs/architecture.md"`
- No `type="d"` F11-CLASSIFY markers (disallowed)
- No `<table>` blocks with `style="background-color"` cells (table-colored is
  disallowed)
- Warning (not hard-fail) if zero ```mermaid fences emitted

## Canonical test case

`HipLink IntraOp - Software Architecture Document (SAD) - 1.0.0` — 16 pages,
8 content images (1× type-e cover banner, 1× type-a system overview, 1× type-b
app architecture, 1× type-c AWS backend, 4× type-a user/surgery/provisioning
flows). Expected Phase 7 outcome: pass; 7/8 mermaid fences emitted; 1/8 type-e
skip-with-reason.

## Changelog

- 2026-04-21: Stub created during task ben/089 Phase A scaffolding.
- 2026-04-21 (session 2): Populated. Required sections derived from the IntraOp
  SAD structure; allowed/disallowed element lists set based on observed real
  usage across the 19 existing architecture MDs in the project. The
  `validate_phase7.py` hooks in this pack are consumed by task 089 priority
  step 5 (validate_phase7.py).
