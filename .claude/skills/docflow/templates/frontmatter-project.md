# Frontmatter Template — Project Documents (Adopt Schema)

Used by `/docflow adopt` to produce round-trippable working-MD copies of DHF formal documents. Every file adopted from `docs/project/dhfs/<dhf>/**/formal/` into its sibling working-MD location carries this frontmatter.

Contrast with `frontmatter-source.md`:
- `frontmatter-source.md` → read-only reference copies of QMS docs in `docs/internal/source/`. One-way, provenance-only.
- `frontmatter-project.md` → living working copies of DHF formal docs. Round-trippable, authoring metadata + template/SOP bindings + filing composition.

```yaml
---
# --- Identity ---
title: "{Document title, without doc-id or version suffix}"
doc_type: "{user-need | requirement | architecture | plan | risk | vnv |
            sop-instance | form-instance | report | clinical | postmarket |
            cybersecurity | other}"
dhf: "{hiplink-suite | hiplink-pre-op | hiplink-intra-op | hiplink-mgmt-services}"
dhf_role: "{system | item}"                    # from project.yml dhfs[]
dhf_area: "{design-controls/user-needs | design-controls/requirements |
             design-controls/architecture | design-controls/vnv |
             design-controls/trace-matrix | design-controls/plans |
             design-controls/tool-validation | design-controls/release-closure |
             risk-management | clinical | cybersecurity | postmarket}"

# --- Lifecycle ---
status: "{draft | in-review | approved | obsolete}"
lifecycle: "draft"                  # Working MDs are always `draft`. The formal counterpart in `formal/`
                                    # represents the released `formal` lifecycle; no frontmatter is
                                    # carried on binary formal files.
owner: "{author name or role}"
last_modified: "{YYYY-MM-DD}"
docflow_version: "v21"              # The docflow SKILL.md version that produced this MD. Stamped at adopt
                                    # time from `.claude/skills/docflow/SKILL.md` frontmatter. Used by
                                    # adopter Phase 0.4 to short-circuit idempotent re-runs (same
                                    # doc_version + same docflow_version → skip). On SPEC-ROLL-FORWARD
                                    # (doc_version unchanged but docflow_version bumped), adopter rewrites
                                    # the R1 per-requirement tables under the new spec's rules without
                                    # re-extracting the body.

# --- Versioning (source document's own version; extracted from content, not filename) ---
# Filenames do NOT carry version suffixes. A working MD is `<Title>.md`; its paired
# formal is `formal/<Title>.<ext>`. Exactly one current formal per title; prior
# formal versions live in git history.
#
# The document's version is extracted FROM THE SOURCE DOC at adopt time — from
# revision history, cover page, PDF metadata, or (last resort) an explicit
# --doc-version flag from the user. We never invent a version counter.
doc_version: "v30"                  # String, normalized to `v<N>` form (no dot). E.g. `v30`, not `v.30`.
                                    # Verbatim-source form (e.g. "v.30") preserved in version_lineage.
release_version: "1.0.0"            # Optional product/release version if embedded in title. null if absent.
version_lineage:                    # Monotonically growing audit trail. NEVER truncate.
  - doc_version: "v30"
    doc_version_raw: "v.30"         # Verbatim string from the source doc, before normalization
    lifecycle: "formal"
    format: "pdf"
    path: "formal/<Title>.pdf"
    event: "original"               # original | adopt | override-merge | export | refresh | obsoleted
    date: "{YYYY-MM-DD}"
  - doc_version: "v30"
    doc_version_raw: "v.30"
    lifecycle: "draft"
    format: "md"
    path: "<Title>.md"
    event: "adopt"
    date: "{YYYY-MM-DD}"

# --- Provenance (round-trip pointers) ---
source_formal: "formal/<Title>.pdf"     # Relpath (from this MD's folder) to the current formal.
                                        # Filename is stable across versions; git tracks history.
target_formal: "formal/<Title>.pdf"     # Where /docflow export will write the next formal output.
                                        # Same path as source_formal (export overwrites). Format can
                                        # differ if explicitly set (e.g. adopted PDF, export DOCX).
conversion_date: "{YYYY-MM-DD}"
conversion_method: "{pandoc+manual | pdftotext+manual | libreoffice+pandoc+manual |
                     xlsx+manual | claude-read+manual}"
conversion_fidelity: "{faithful | summary | partial}"
pages: null                              # PDFs only
sheets: null                             # XLSX only
slides: null                             # PPTX only
has_images: false
image_count: 0
has_tables: false
has_form_fields: false
has_hyperlinks: false                    # v29+: any link annotation in source
hyperlink_count: 0                       # v29+: total `[text](url)` spans in working MD

# --- Template binding (QMS form/template this doc instantiates) ---
# Auto-inferred at adopt time by matching title + heading structure against
# docs/internal/source-md/Forms/*.md. Null if the doc is not a form instance
# (e.g. free-form reports, user-drafted architecture docs).
template_of:
  doc_id: null                        # e.g. "FORM-000137230"
  title: null                         # Captured title of the matched template
  template_version: null              # Version of the template this doc was authored against
  inferred: false                     # true if auto-inferred, false if human-authored
  confidence: null                    # high | medium | low | null (not-applicable)
  match_basis: null                   # "title-exact" | "title-fuzzy" | "heading-structure" | "explicit-ref" | null
template_hints:                       # Non-empty when confidence is medium/low OR match was ambiguous
  - doc_id: null
    title: null
    reason: null                      # Why this was a candidate (e.g., "partial title match", "shared heading set")

# --- Process binding (SOPs / Work Instructions governing this doc's creation/review) ---
# Auto-inferred from explicit references in the doc (footer, revision history,
# "per SOP-XXX" / "per WI-XXX" phrasings). List of process artifacts, not a single
# scalar — some docs are governed by multiple.
#
# IMPORTANT: In Arthrex's QMS, Work Instructions (WI-\d+) play a process-governance
# role equivalent to SOPs in other QMS frameworks — many DHF docs cite WIs without
# any SOP reference. The adopter scans BOTH SOP-\d+ AND WI-\d+ patterns.
authored_per:
  - doc_id: null                      # e.g. "SOP-000326588" or "WI-000101591"
    doc_type: null                    # "SOP" | "WI" — inferred from doc_id prefix
    title: null
    inferred: false
    confidence: null                  # high | medium | low
    note: null                        # Which clause / section applies, if known
authored_per_hints:                   # Candidates that didn't clear the confidence bar
  - doc_id: null
    doc_type: null                    # "SOP" | "WI"
    reason: null

# --- Filing composition (which submissions include this doc) ---
# Populated at adopt time from docs/project/submissions/<filing>/composition-manifest.md
# — used by /tracker and composition-manifest validation to query by metadata
# instead of path-grepping. Updated when a manifest references this doc.
filings: []                           # Subset of ["qsub", "510k", "pccp"]

# --- Cross-references (same semantics as source-md) ---
# Other docs this doc cites. Resolved against docs/internal/source-md/ and
# other adopted DHF docs. Unresolved refs carry resolved: false and feed
# /docflow sync-known-refs.
references: []

# --- Requirements-doc aggregate (ONLY when doc_type: requirement) ---
# Populated by adopter Phase 5e. Feeds dashboard queries without parsing
# per-requirement tables. Counts are over requirement instances; classification
# counts multi-valued (a req with 3 tags contributes 3 counts).
# OMIT this entire block for non-requirement doc_types.
requirements:
  count: 0                            # Total requirements in this doc
  epics:                              # Map of Epic Link value → count. Verbatim from source.
    # "DI-0013 MEASUREMENTS [UNITY]": 2
    # "VIEW 3D RECONSTRUCTION": 5
  classification:                     # Map of canonical tag → count. Multi-valued; sums > count.
    functional: 0
    safety: 0
    security: 0
    privacy: 0
    usability: 0
    performance: 0
    reliability: 0
    interoperability: 0
    regulatory: 0
  criticality:                        # Map of CtX tag → count. Multi-valued. See glossary.md "Criticality Tags".
    CtF: 0                            # Critical to Function
    CtS: 0                            # Critical to Safety
    CtC: 0                            # Critical to Compliance
    CtP: 0                            # Critical to Performance
    none: 0                           # Reqs with no CtX assertion (nice-to-haves)
  target_releases:                    # Map of target value → count
    v1: 0
    v2: 0
    future: 0
    unassigned: 0
  traces_to:                          # How many reqs have resolvable (DI-/UN-prefix) parent vs prose-only
    resolved: 0
    unresolved: 0
  status:                             # Lifecycle distribution
    proposed: 0
    accepted: 0
    implemented: 0
    verified: 0
    deferred: 0
    rejected: 0
    superseded: 0

# --- History ---
conversion_history: []                # Appends on every adopt/refresh; version_lineage is the canonical record
notes: null                           # Conversion notes. REQUIRED when conversion_fidelity is 'partial'.
                                      # Also the place to record inference warnings, e.g.
                                      # "template_of could not be auto-inferred — manual review"
---
```

## Field Definitions

### Identity

| Field | Required | Description |
|-------|----------|-------------|
| `title` | Yes | Document title, without doc-id or version suffix. Human-readable. |
| `doc_type` | Yes | Semantic type. Drives rendering template selection at export time. |
| `dhf` | Yes | Which DHF this doc belongs to. Must match a leaf name in `project.yml` `dhfs[]`. Auto-inferred from path. |
| `dhf_role` | Yes | `system` (device-level) or `item` (module-level). Auto-inferred from `project.yml`. |
| `dhf_area` | Yes | Subfolder under the DHF (e.g. `design-controls/user-needs`). Auto-inferred from path. |

### Lifecycle

| Field | Required | Description |
|-------|----------|-------------|
| `status` | Yes | `draft` (in-flight), `in-review` (under review), `approved` (released), `obsolete` (superseded) |
| `lifecycle` | Yes | `draft` for working MDs (always), `formal` reserved for future use (never written on working MD frontmatter). Redundant with folder location but useful for queries. |
| `owner` | Yes | Author or owning role (e.g. `"Ben Xavier"` or `"regulatory-lead"`) |
| `last_modified` | Yes | Date of last meaningful edit, not including automated metadata updates |
| `docflow_version` | Yes (v21+) | The docflow SKILL.md version that produced this MD (e.g. `"v21"`). Stamped at adopt time. Enables idempotency short-circuit on re-runs: if `doc_version` and `docflow_version` both match the current run, the adopter exits without re-extracting or re-inferring. |

### Versioning

| Field | Required | Description |
|-------|----------|-------------|
| `doc_version` | Yes | The source document's own version, normalized to `v<N>` form (no dot). Extracted from doc content at adopt time. |
| `release_version` | No | Product/release version if embedded in title (e.g. `1.0.0` for `HipLink Web - SDP - 1.0.0`). `null` if absent. |
| `version_lineage` | Yes | Full chronological list of format transitions. Never truncated — this is the audit record. |

**Version extraction hierarchy** (adopter runs these in order at adopt time; first match wins):

1. **Revision history tables / blocks** — `"Current document version: v.30"`, `"Version 30 (current)"`, Appendix E style
2. **Document footer / header** — `v.N` in running headers/footers
3. **Cover page / title block** — version markers in prominent cover text
4. **PDF metadata** — `/Subject`, `/Keywords` occasionally carry rev info
5. **Semantic search of full body** — patterns `[Vv]\.?\s*\d+`, `Rev(?:ision)?:?\s*\d+` with context scoring (structured-table matches rank higher than body-prose matches)
6. **Explicit user override** — `--doc-version v30` flag on the adopt command
7. **Error-out** if none of the above succeed → adopter writes `VERSION_NOT_FOUND.txt` in staging, does NOT commit, returns failure. Regulated docs should never ship with a silently defaulted version.

**Normalization**: strip dot between `v` and digits (`v.30` → `v30`), lowercase the `v`, strip any `.0` suffix on major versions (`v30.0` → `v30`). Preserve the raw source string in `version_lineage[].doc_version_raw` for audit.

**Counter semantics**:
- **Adopt** preserves the formal's `doc_version` on the working MD (working inherits the formal's version — they represent the same version in different formats, draft vs formal lifecycle).
- **Override (merge)** (when a new formal drops): adopter detects `doc_version(new) > doc_version(current)`, runs 3-way merge on content, and updates working MD's `doc_version` to the new value. Both formal and working now reflect the new version.
- **Export** (Phase 2): the reviewer/approver specifies the new `doc_version` when releasing; adopt never silently bumps.
- **Refresh** (re-adopt of same version): no version change; body re-extracted from current formal.

### Filename convention

**No version suffix on filenames.** Git history is the version record.

| File | Pattern | Example |
|------|---------|---------|
| Working MD | `<Title>.md` | `HipLink Web - Software Development Plan (SDP) - 1.0.0.md` |
| Current formal | `formal/<Title>.<ext>` | `formal/HipLink Web - Software Development Plan (SDP) - 1.0.0.pdf` |
| Prior formals | (not on disk — in git history only) | `git log --follow -- formal/<Title>.pdf` |

`<Title>` is extracted from the document at adopt time (see **Title extraction** below). Any release version embedded in the title (e.g. `- 1.0.0`) stays as part of the filename — it's part of the product/doc identity, not the doc version.

**Title extraction hierarchy** (first match wins):

1. **Cover page / first-page prominent text** (largest font, top of page) — authoritative for "what a human reader sees as the title"
2. **PDF metadata `/Title`** field — `pdfinfo <file> | awk '/^Title:/'`
3. **Body first H1** — the top-level heading in the extracted markdown
4. **Cleaned filename** — strip documented prefixes (e.g. `AFAI-`) and trailing timestamp patterns (`-YYMMDD-HHMMSS`); last resort because filename is ambiguous when multiple hyphens separate components

If sources 1 and 2 disagree: **cover page wins** (what the reader sees as canonical; metadata often goes stale on re-exports).

**File sanitization**: strip filesystem-unsafe characters from extracted title (`/`, `\`, `:`, `*`, `?`, `<`, `>`, `|`, `"`). Most Arthrex doc titles use parentheses, hyphens, spaces — all legal on all major filesystems.

### Provenance

| Field | Required | Description |
|-------|----------|-------------|
| `source_formal` | Yes | Relpath (from MD's folder) to the current formal file. Stable across versions — filename doesn't change when version bumps. |
| `target_formal` | Yes | Relpath where `/docflow export` will write the next formal output. Normally same as `source_formal` (export overwrites). Can differ if explicit `--format docx` or similar. |
| `conversion_date` | Yes | Date of the most recent adopt or override-merge event |
| `conversion_method` | Yes | Toolchain used (see converter.md for tool selection rules) |
| `conversion_fidelity` | Yes | `faithful`, `summary`, or `partial` — matches source-md semantics |

### Template binding

`template_of` captures **what QMS form/template this doc instantiates** — e.g. a User Needs doc that instantiates `FORM-000137230 (Design and Development Plan)` has `template_of.doc_id: "FORM-000137230"`.

Auto-inference heuristics (applied in priority order at adopt time):
1. **Title-exact**: doc title string equals a `source-md/Forms/FORM-*.md` `title` field → `confidence: high`
2. **Explicit reference**: doc body contains `"per FORM-XXX"` or cites the form in a revision history → `confidence: high`
3. **Heading-structure match**: doc's H1/H2 set overlaps ≥ 70% with a template's heading set → `confidence: medium`, populate `template_hints` with other overlapping templates
4. **Title-fuzzy** (token-set ratio ≥ 0.8): → `confidence: low`, populate `template_hints` with all ≥ 0.6 candidates
5. **No match**: `template_of: null`, `template_hints` lists the top 3 nearest candidates, `notes:` gains `"template_of could not be auto-inferred — manual review"`

### Process binding

`authored_per` captures **which process artifacts (SOPs AND/OR Work Instructions) govern this doc's creation/review**. Unlike `template_of` (structural), this is process metadata — what procedure was followed.

In Arthrex's QMS, many DHF docs cite Work Instructions (`WI-\d+`) as the governing process artifact **without any SOP reference** — e.g. `WI-000101591 HAA SDLC Model` governs Software Development Plans across the HAA-SDLC lifecycle. The adopter MUST scan both `SOP-\d+` AND `WI-\d+` patterns. Absence of SOP refs in a doc body does NOT mean the doc is ungoverned.

Auto-inference:
1. Scan doc body for `SOP-\d+` AND `WI-\d+` pattern matches.
2. For each match: resolve against `source-md/SOPs/` (for SOPs) or `source-md/Work Instructions/` (for WIs) to capture title + presence.
3. Populate `authored_per[]` with matches that have clear contextual binding (e.g. in a "Governing Procedures" / "Standards" / revision-history section, or cited in an Appendix explaining source references) — `confidence: high`.
4. Matches found in passing prose → `authored_per_hints[]` with the citing sentence as `reason`.
5. Each entry carries `doc_type: "SOP"` or `"WI"` inferred from the doc-id prefix, so downstream tooling can filter by process-artifact class without re-parsing the doc-id.

**SOP vs WI equivalence for authored_per**: some QMS frameworks draw SOP and WI as a strict hierarchy (SOP = the how, WI = the step-by-step). Arthrex's HAA SDLC uses WIs as the primary governance artifact for software lifecycle, with SOPs layered on for cross-cutting controls. For `authored_per` purposes both are equivalent process citations and captured uniformly — the `doc_type` field preserves which is which for filter/grouping needs.

### Filing composition

`filings` is derived from `docs/project/submissions/<filing>/composition-manifest.md` at adopt time. When the manifest references this doc's path, append the filing slug to `filings`.

This is the inverse index to the composition manifests — it lets a doc answer "which filings include me?" without scanning every manifest.

**Source of truth**: the composition manifests remain authoritative. `filings` is a convenience field. If they disagree, trust the manifest and re-sync.

### References

Same shape as `frontmatter-source.md` `references:`. Resolves against:
1. `docs/internal/source-md/` (QMS docs)
2. Other adopted DHF docs (working MD across all DHFs)
3. `docs/external/` references

Unresolved refs (resolved: false) feed `/docflow sync-known-refs` as today.

## Notes on usage

- **Auto-populated fields at adopt time**: `dhf`, `dhf_role`, `dhf_area`, `source_formal`, `conversion_date`, `conversion_method`, `conversion_fidelity`, `pages`/`sheets`/`slides`, `has_images`, `image_count`, `has_tables`, `has_form_fields`, `source_version`, `working_version`, `version_lineage` (initial entry), `template_of` + `template_hints` (inferred), `authored_per` + `authored_per_hints` (inferred), `filings` (from manifests).
- **Human-authored fields**: `title` (refined from filename), `doc_type`, `status`, `owner`, `notes` (when inference is incomplete).
- **Maintained-by-tooling fields**: `last_modified` (on every write), `target_formal` (default on adopt, user can override), `version_lineage` (on every adopt/export/refresh), `references` (resolved by converter agent).
