# Docflow Skill — Design & Architecture

This document captures the **why** behind docflow's design decisions so future work doesn't re-analyze settled choices. It is not loaded by Claude during normal skill operation — it exists for human understanding.

For skill usage and instructions, see `SKILL.md`. For per-version change history, see the `## Changelog` section of `SKILL.md`.

## Overview

Docflow moves documents between three states:

1. **QMS source** — read-only reference docs in `docs/internal/source/` (SOPs, forms, WIs, standards). Converted one-way to markdown in `docs/internal/source-md/` for search, grep, and cross-reference resolution.
2. **DHF formal** — binary deliverables (PDF, DOCX, XLSX) in `docs/project/dhfs/<dhf>/**/formal/`. These are what FDA sees. Owned by the project team.
3. **DHF working** — markdown copies of formal docs, authored and iterated in git, round-tripped back to formal on release.

The skill has three operational modes corresponding to these transitions:

| Mode | Direction | Command | Maturity |
|------|-----------|---------|----------|
| QMS ingest | source → source-md | `/docflow convert`, `/docflow batch` | Mature (127 docs converted) |
| DHF adopt | formal → working MD | `/docflow adopt` | Phase 1 — shakedown complete |
| DHF export | working MD → formal | `/docflow export` | Phase 2 — design-captured, unbuilt |

## Role in the Ecosystem

```
docs/internal/source/                            ← read-only QMS inputs
docs/internal/source-md/                         ← converted markdown (reference)
      │
      │ (cross-refs + template/SOP/WI resolution)
      ▼
docs/project/dhfs/<dhf>/<area>/
  ├── <Title>.md                                 ← working MD (draft lifecycle)
  ├── formal/<Title>.<ext>                       ← current formal (one per title)
  └── images/                                    ← sibling extracted images

docs/project/submissions/<filing>/
  └── composition-manifest.md                    ← includes by title
```

Docflow does not own the filesystem layout (medtech-docs does). It respects the paths and adds metadata + conversion mechanics.

## Key Design Decisions

Each decision below has a **why** and a short **what we rejected** so the reasoning survives the decision.

### D1. `adopt` is a distinct action from `convert`

**Decision**: DHF formal → working MD uses a new `/docflow adopt` action with its own agent (`adopter.md`) and its own frontmatter schema (`frontmatter-project.md`), not an overload of `/docflow convert`.

**Why**:
- `convert` produces one-way reference copies of read-only QMS docs. Frontmatter captures provenance and cross-refs, nothing about authoring.
- `adopt` produces the authoring source of truth that will round-trip back to formal. Frontmatter must capture template instantiation, process governance (SOP/WI), filing composition, version lineage, and round-trip pointers.
- Treating adoption as `convert` with a different output folder would force `frontmatter-source.md` to carry authoring metadata it wasn't designed for, or require a retrofit once Phase 2 export arrives.

**Rejected**: overloading `/docflow convert <dhf-path>`. Simpler syntactically, but the frontmatter schema divergence makes it painful later.

---

### D2. Filenames carry no version suffix

**Decision**: Working MD filenames are `<Title>.md`. Current formal filenames are `formal/<Title>.<ext>`. No `-v30`, `-v1`, `-Draft`, or any other suffix. Exactly one current formal per title.

**Why**:
- Source documents carry their own version lineage — Arthrex's Confluence pages have page-revision numbers (e.g. `v.30` in SDP Appendix E), QMS-controlled templates have their own doc-control versions. Adding a synthetic docflow counter is a parallel invention that drifts from the real one.
- Git already tracks filesystem history. Encoding versions in filenames is a workaround for not trusting git.
- Filename stability lets composition manifests, READMEs, and cross-references point at `<Title>.pdf` forever. No rename churn on every version bump.
- An auditor can run `git log --follow -- formal/<Title>.pdf` to see the full history; `git show <sha>:formal/<Title>.pdf` retrieves the exact bytes of any prior signed version.

**Rejected twice during iteration**:
- First rejected: synthetic linear counter `-v1.pdf` / `-v2.md` / `-v3.pdf` across format transitions. Rejected because it didn't reflect Confluence page versions.
- Second rejected: `<Title> - v30.pdf` / `<Title> - v30 - Draft.md` with version in filename. Rejected because it encoded what git already encodes, adding rename churn.

### D3. Document version is extracted from content, not filename

**Decision**: Phase 0 of the adopter runs extraction hierarchies for title and `doc_version` against the document's content (cover page, PDF metadata, body H1 / revision history, semantic search). Filename is last-resort fallback.

**Why**:
- This project does not enforce a filename policy. Dropped files have varied naming (`AFAI-`-prefixed timestamps, QMS-style IDs, bare titles, manual renames). Relying on filename patterns would introduce project-specific stripping rules that rot.
- The document's *content* carries the canonical title (cover page, "what a reader sees") and the canonical version (revision history, "what the QMS tracks"). These are authoritative in a way filenames are not.
- Content extraction worked correctly on the first shakedown (SDP). Falling back on filename is only needed for malformed/scanned docs with failed OCR — those need human review anyway.

**Rejected**: `project.yml docflow.title_strip_prefixes: ["AFAI-"]` config. Would have worked, but since content extraction is reliable, this is config without a use case. Dropped in favor of "use filename verbatim + flag for manual review" when all content sources fail.

### D4. `doc_version` extraction errors out on failure — no silent defaults

**Decision**: If the adopter cannot extract a `doc_version` from any of the priority sources (revision history, footer, cover, metadata, body scan), it writes `VERSION_NOT_FOUND.txt` in staging and fails the adopt with a user-actionable message. No silent default to `v1`.

**Why**: Regulated documents must never ship with a silently-wrong version. A v.30 doc that gets stored as `v1` in frontmatter is a traceability error — the kind of thing FDA auditors find. Failing loud and asking the user to add `--doc-version vNN` is the correct posture.

**Rejected**: default to `v1` + flag in notes. Simpler but fails the "never lie about regulatory metadata" rule.

### D5. `authored_per` covers both SOPs and WIs

**Decision**: The `authored_per` inference pass scans for both `SOP-\d+` and `WI-\d+` patterns. Each entry records `doc_type: "SOP"` or `"WI"`.

**Why**: Arthrex's QMS uses Work Instructions as the primary process-governance artifact for software development — `WI-000101591 (HAA SDLC)` governs Software Development Plans across the entire lifecycle. Many DHF docs cite WIs with zero SOP references. A SOP-only scanner would leave these docs looking ungoverned. First shakedown surfaced this: the SDP cites 7 WIs and zero SOPs, and the original SOP-only pass reported `authored_per: []` which was actively misleading.

**Rejected**: SOP-only scanning (the initial v15 design). Silent failure mode — governed docs look orphaned.

### D6. Override-merge is 3-way with CONFLICT markers, not auto-replace

**Decision**: When a new formal version drops for an already-adopted doc, `/docflow adopt --override` performs a 3-way section-aware merge (base = prior formal, draft = current working MD, new = new formal). Sections changed by one side auto-apply; sections changed by both emit HTML-comment CONFLICT markers for manual resolution. Metadata carries forward (template_of, authored_per, filings, owner). Inference re-runs on the merged body.

**Why**:
- An author who has been editing a draft for days expects their edits to survive a formal version bump. Silent replacement is unacceptable.
- Auto-merging body edits across versions is where silent loss of intent happens. Emitting CONFLICT markers forces the author to consciously choose.
- Section-aware merging (H2/H3 boundaries) beats line-aware — markdown prose edits span multiple lines naturally, and line-level conflicts produce noise.
- The old formal is preserved in git history. The old working is preserved in git history. No author-time loss is possible.

**Rejected**:
- **Auto-replace**: regenerate working MD from new formal, losing draft edits. Simpler to build, unacceptable for the use case.
- **`obsolete-v30.md` sidecar file**: keep the old working as a `<Title>.obsolete-v30.md` for manual diff. Rejected because git already provides this (`git show HEAD~1:<Title>.md`) without filesystem clutter.

**Status**: design-captured in `adopter.md` but not yet implemented. Today's adopter returns a manual-instruction failure on OVERRIDE-MERGE detection. Full implementation lands when a real upgrade scenario needs to be exercised.

### D7. Staging sits inside the DHF area, not `/tmp`

**Decision**: The adopter's staging directory is a `.staging/` subfolder of the DHF area, sibling to `formal/`. `.gitignore` covers `docs/project/dhfs/**/.staging/`. VS Code `files.exclude` hides it from the explorer.

**Why**:
- Path-resolution validation in Phase 7 is honest: staging has the same folder structure as the final commit, so `images/foo.png` references resolve the same way in staging as after commit. Running validation in `/tmp` would require different path logic.
- Failed runs leave their staging intact for human debugging. `/tmp` staging evaporates on reboot, so post-mortem becomes impossible.
- `.gitignore` + VS Code exclusion make the folder invisible during normal work — the ergonomic cost is near-zero.

**Rejected**: `/tmp/docflow-adopt-<uuid>/`. Cleaner during runs but breaks validation fidelity and post-mortem debugging.

### D8. Frontmatter preserves verbose null blocks

**Decision**: When inference yields no match, the adopter emits the full null-block structure (e.g. `template_of: { doc_id: null, title: null, template_version: null, inferred: true, confidence: null, match_basis: null }`) rather than compacting to `template_of: null`.

**Why**:
- The tracker dashboard reads these fields to generate "template gap" / "process governance not asserted" warnings. A compact `null` loses the structural signal.
- Explicit null fields are self-documenting — a human opening the frontmatter sees which fields COULD be populated, not just which ARE.
- The YAML bloat is cosmetic; machines don't care.

**Rejected**: compact `<field>: null` form for unmatched inferences. Minor DX win, material dashboard loss.

### D9. Missing template / process bindings surface via tracker, not adopter warnings

**Decision**: The adopter captures null `template_of`, empty `authored_per`, and unresolved `references[]` entries in frontmatter without promoting them to adopter-level warnings. The `/tracker` skill reads these fields and renders them as dashboard issues for user review.

**Why**:
- Many valid software DHF docs will hit `template_of: null` because Arthrex software artifacts are Confluence page templates, not paper-form instances. Warning on every adopt would be noise.
- The tracker dashboard is the right surface for "things that need user review" — it aggregates across DHFs, persists state, and integrates with the filing timeline.
- Separation of concerns: adopter captures truth, tracker renders issues.

**Rejected**: suppress the null fields (loses signal) or aggressively warn at adopt time (noisy and premature).

## Dependencies

| File | Required by | Purpose |
|------|-------------|---------|
| `docs/internal/source/` | `convert`, `batch` | QMS source documents (PDF, DOCX, XLSX) |
| `docs/internal/source-md/` | `convert`, `batch`, `sync-known-refs` | Markdown reference copies of QMS docs |
| `docs/internal/source-md/Forms/` | `adopt` (template inference) | Form templates for `template_of` matching |
| `docs/internal/source-md/SOPs/` | `adopt` (process inference) | SOPs for `authored_per` matching |
| `docs/internal/source-md/Work Instructions/` | `adopt` (process inference) | WIs for `authored_per` matching |
| `docs/internal/source/INDEX.md` | `convert`, `adopt` | Cross-reference resolution |
| `docs/internal/qms-reference-graph.md` | `convert`, `adopt`, `sync-known-refs` | Known-but-absent references |
| `docs/project/dhfs/<dhf>/**/formal/` | `adopt` | Input formal docs |
| `docs/project/submissions/*/composition-manifest.md` | `adopt` (filing inference) | Inverse filing index source |
| `pandoc` | All conversions | Markdown ↔ DOCX |
| `pdftotext`, `pdfimages`, `pdfinfo` | PDF conversions | Content + image extraction |
| `soffice` (LibreOffice) | DOCX pagination, DOC conversion | Rendered-page detection |
| Python: `Pillow`, `openpyxl`, `pyyaml` | F1 (PDF image orientation), XLSX, frontmatter | Image + data manipulation |

## Lineage

Originally adapted from a generic document-conversion skill in early task 023 (127-doc QMS conversion). Phase-1 workflows (`convert`, `refresh`, `batch`) were proven across the full QMS corpus. Phase-2 workflows (`export`, `import`, `reconcile`) were stubbed but never built.

Task 075 added the adoption workflow (`adopt`) as a distinct third mode, iterating through v15 (synthetic counter filenames) → v16 (content-driven version extraction, no filename suffixes, override-merge design). The override-merge implementation is deferred until a real upgrade scenario exercises it.

## What Docflow Explicitly Does Not Do

- **Does not enforce filename policies.** Filenames match document titles after adopt; the project has no naming convention beyond that.
- **Does not version branches / alternate authors.** Single linear lineage per doc, tracked in git. Concurrent authoring is a git-branch concern, not a docflow concern.
- **Does not auto-merge body content across formal version bumps.** CONFLICT markers force the author to review.
- **Does not ship its own viewer.** READMEs and working MDs render in any markdown renderer; formal docs use their native format.
- **Does not own the DHF folder structure.** That's `medtech-docs`. Docflow respects whatever layout is there.
