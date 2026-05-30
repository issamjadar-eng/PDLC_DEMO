# Knowledge Pack Export — Design & Architecture

This document describes the design behind the `knowledge-pack-export` skill. It is not loaded by Claude during normal operation — it exists for human understanding and as the skill's index layer. For usage, see `SKILL.md`.

## Overview & intended use

`knowledge-pack-export` packages a curated subset of a project's documentation into the bounded bundle an external LLM-assistant platform ingests — primarily a **Google Gemini Gem** (≤10 knowledge files), generalized to OpenAI Custom GPTs, NotebookLM, Claude Projects, and a plain zip handoff. The output (a "knowledge pack") is *(generated system instructions) + (≤N knowledge files) + (provenance manifest)*.

**Intended use:** teams **outside Claude Code / Claude** need self-serve access to a program's knowledge (strategy, architecture, classification rationale, predicate analysis, submission posture) without someone hand-curating a document bundle each time. The operator authors a manifest once and rebuilds on demand — this is *tool generation*, a repeatable packaging pipeline, not a one-off export. In a regulated program the packs carry full content and are **access-controlled at distribution** (who the Gem is shared with), not by redacting content.

**Why "knowledge pack," not "agent pack":** the skill was first drafted as `agent-pack-export`, but "agent" is overloaded in this project — there are advisor agents and subagents, and "export the agents" reads as exporting *those*. The artifact is a **knowledge base** for an external assistant, so `knowledge-pack-export` is the accurate, unambiguous name (renamed from `agent-pack-export` in v2).

## Lineage

Original skill, not adapted from a prior version. Mirrors conventions from sibling content-pipeline skills (`md-deck`/`frontend-slides` write generated output beside provenance metadata; `strategy` assembles per-domain content from many sources) and the `project.yml`-as-source-of-truth pattern shared across the registry. Unlike `md-deck` (which writes to `assets/<slug>/`), a knowledge pack keeps its authored manifest and generated output **together** under `tools/knowledge-packs/<slug>/`, because a pack is a self-contained deliverable unit rather than a rendered view of one source file.

## Key Design Decisions

### Hybrid build engine — deterministic default, LLM only on marked slots

The binding correctness concern is regulated content: an external pack must be provenance-clean and reproducible. So the default merge is **deterministic concatenation** (`mode: verbatim`) — verbatim source text with per-source `<!-- source: path @ sha -->` markers and a git-commit stamp. The LLM is invoked only where pure concatenation can't solve the problem: a merge group with too many docs to ingest usefully (`mode: condense`). Condensed output is recorded as `mode: derived` in `manifest.json`, so a reviewer can always tell a summary from source-of-truth. This confines non-determinism to slots the operator explicitly opted into.

### File count, not file size, is the constraint

The Gemini Gem cap is **10 knowledge files**; per-file size is generous (~100 MB). Bundles never hit a byte ceiling at our doc sizes — the real limits are file count and retrieval quality (bloated knowledge degrades grounding). The engine enforces `max_files` per target and merges into thematic bundles; `condense` exists to protect retrieval quality, not to dodge a size cap.

### Manifest-driven selection, not heuristic

Which documents an external team receives is, in a regulated project, an auditable authored decision. The per-pack `<slug>.pack.yml` manifest is that decision: explicit source globs → bundle slots → verbatim/condense mode. No auto-selection heuristic. Manifests live under `tools/knowledge-packs/<slug>/`, keeping project-specific selection out of the project-agnostic skill.

### Confidentiality travels with the artifact; access control is the operator's

Packs carry full content (no in-pipeline redaction) and are intended for approved end users, access-controlled at distribution. The skill cannot enforce who a Gem is shared with — that's a platform setting the operator owns. What the skill *can* do is make the control intent travel with the artifact: a confidentiality banner in `system-instructions.md`, in each bundle's header, and in `manifest.json`.

### Self-describing, segmentable bundles (v3)

A bundle that silently concatenates five documents is correct but unusable: neither a human reviewer nor a reading agent can tell what's inside or where one document ends. v3 makes every bundle navigable, all generated deterministically (no LLM, verbatim builds stay reproducible): a **visible preamble** (title, bundle N of M, a table of the contained documents + their key `##` sections, and a `BUNDLED DOCUMENTS` divider), **visible greppable segment markers** (`▌DOCUMENT k of N — <title>` + `Source:` path) between documents, and an **agent guide** folded into `system-instructions.md` (costs no knowledge-file slot). The dual payoff: the operator can confirm the right content was included by reading the preamble, and the assistant can segment a bundle into independent documents and cite each by its source path.

### Targets registry decouples platform specifics

`references/targets.yml` holds per-platform caps/formats/publish methods. Adding OpenAI GPTs or NotebookLM is a data edit, not a code change. The build engine reads the cap from here and enforces it.

### Freshness is a candidate-finder; the caller adjudicates (D-211.7)

A verbatim pack is only as current as its sources — if a source doc's prose has rotted relative to `project.yml` (e.g. asserts "IEC 62304 Class C" for a module project.yml records as Class B), the pack faithfully reproduces the staleness, and a contradictory answer in the Gem is the result. The `freshness` action addresses this, but the **design decision is about who decides**:

- `scripts/freshness_check.py` is **deterministic and high-recall**, keyed off `project.yml` (the oracle for structural facts). It is regex — it *cannot* tell an assertion ("the module is Class C") from a mention ("we fixed the Class C drift"). Therefore it **never suppresses**: every candidate is returned with surrounding context and **advisory signal hints** (`likely_definition`, `likely_changelog`, `likely_predicate_cell`, `in_analysis_doc`, `in_external_doc`, `in_table_row`, `module_named_nearby`).
- The **caller (Claude, or an agent in a workflow) does the semantic final pass** — reading each hit's context to classify real-drift vs. mention. The tool is *grep-with-grounding*; the caller is the *judge*.

This is the same split as the build engine (deterministic finds cheaply + reproducibly; LLM judges). An earlier draft had the tool *drop* "benign" hits — that was wrong: a dropped hit is a finding the smart layer never sees. High recall + rich context + a judging caller is the correct contract for a check that gates regulated content. The finder **exits 0 always** — severity is the caller's call, not a hard gate.

## Possible future improvements

Design backlog — none implemented yet, listed roughly by value.

- **Image support (figures travel with the pack).** A text knowledge pack ingests markdown only, so `images/...` references are lost (the `validate` action reports the count as a caveat). Source docs under `_confluence/<leaf>/.../images/` carry real architecture diagrams, hazard figures, etc. Options, increasing in effort:
  1. **PDF render per slot** — a `render: pdf` flag on a slot routes its sources through `/docflow` (md→PDF with embedded images) and attaches the PDF as the knowledge file. Best fidelity for diagram-heavy slots (e.g. architecture); costs the same one file-slot. Caveat: PDF is less cleanly segmentable than the markdown convention.
  2. **Image sidecar + link rewrite** — copy referenced images into the pack output and rewrite links to relative paths, for targets that accept a folder/zip (not a Gem, which takes flat files).
  3. **Alt-text inlining** — for figures with descriptive alt-text, surface that inline so the assistant can reason about the diagram even without the bitmap.
- **`publish` action (v2).** Drive Gem/GPT creation via `/web-control` (upload knowledge files + paste system-instructions under the corporate identity) instead of manual upload. Spec'd in SKILL.md; not built.
- **Per-doctype canonical-source resolution.** "Which copy is canonical" is per-doctype (architecture → `_confluence`; risk/trace → dhfs more populated but `_confluence` carries the full set incl. Hazard Analysis + image folders). Today the manifest encodes each choice by hand; a helper that resolves the canonical path from `project.yml`/taxonomy given (DHF, doctype) would remove the manual step and prevent drift-mirror mistakes.
- **Auto-`init` from project structure.** `init` could propose a fuller default slot set by walking `project.yml dhfs[]` + the submission composition manifests, so a new project trims a near-complete manifest rather than building one up.
- **Drift gate on build.** Optionally run `freshness` automatically at the end of `build` and print the candidate count, so an operator at least sees the drift signal before shipping (still advisory — never a hard gate).
- **Per-slot retrieval-budget warning.** Beyond the file-count cap, warn when one bundle is large enough to dominate retrieval (e.g. a 200 KB+ strategy bundle), suggesting a split.

## Dependencies

| File | Required by | Purpose |
|------|-------------|---------|
| `scripts/build_pack.py` | `validate`, `build` | Deterministic assembly + provenance + cap enforcement. |
| `scripts/freshness_check.py` | `freshness` | Read-only project.yml-keyed contradiction / staleness / variant candidate-finder. |
| `references/targets.yml` | all build actions | Per-target file caps, formats, publish methods. |
| `templates/example.pack.yml` | `init` | Manifest scaffold. |
| `project.yml` (project root) | `init`, `freshness` | DHF roster + classification (manifest pre-fill + the contradiction oracle). |
| `git` (project root) | `build`, `validate`, `freshness` | Source-commit provenance stamp; git-age in staleness. |
| PyYAML | all build / freshness actions | YAML parsing in the engine + finder. |
| `/web-control` skill | `publish` (v2) | Authenticated browser session for Gem creation. |

## Best Practices

<!-- Consumed by /best-practices audit -->

| Check | How to Verify | Severity | Scope |
|-------|--------------|----------|-------|
| Skill has SKILL.md | `.claude/skills/knowledge-pack-export/SKILL.md` exists | Required | shared |
| Frontmatter complete | name, description, version, updated all present | Required | shared |
| README.md exists | Design doc at skill root | Required | shared |
| Changelog current | Latest entry matches SKILL.md `version` | Required | shared |
| Build engine present | `scripts/build_pack.py` exists | Required | shared |
| Freshness finder present | `scripts/freshness_check.py` exists | Required | shared |
| Targets registry present | `references/targets.yml` parses and has ≥1 target with `max_files` | Required | shared |
| Manifest template present | `templates/example.pack.yml` exists | Required | shared |
| Built packs carry provenance | every `tools/knowledge-packs/*/pack/manifest.json` records `built_commit` + per-slot `mode` | Recommended | shared |
| Project-agnostic | no project/company/device names in any skill file | Required | shared |

## Changelog

- 4 (2026-05-30): `validate` now reports per-slot **image-reference counts** + a pack-level warning — images do not travel into a text knowledge pack and relative `images/...` links break, so the operator sees which diagram-heavy bundles lose figures (and can render those to PDF via `/docflow` instead).
- 3 (2026-05-30): Bundles are now self-describing and segmentable. Each `NN-*.md` opens with a deterministic **visible preamble** (title, bundle N of M, confidentiality, build stamp, and a table of the documents inside with their key `##` sections + a `BUNDLED DOCUMENTS` divider). Constituent documents are separated by visible greppable **segment markers** (`▌DOCUMENT k of N — <title>` + `Source:` path) alongside the machine `<!-- source -->` comment, so a reading agent can split a bundle into independent documents. `system-instructions.md` gains an **agent guide** ("How this pack is organized" + bundle map) that costs no knowledge-file slot. Purpose: let an operator verify the right content was included and let reading agents navigate/segment/cite precisely.
- 2 (2026-05-29): Renamed `agent-pack-export` → `knowledge-pack-export` ("agent" collided with the project's advisor agents / subagents). Relocated pack home from `agent-packs/` + `assets/<slug>/agent-pack/` to a unified `tools/knowledge-packs/<slug>/` (manifest + `pack/` output together). Added the `freshness` action + `scripts/freshness_check.py` — a project.yml-keyed, high-recall drift/staleness candidate-finder whose caller adjudicates (D-211.7): never suppresses, returns context + advisory hints, exits 0 (finder not gate). Documented the first-run mental model (authored `.pack.yml` input vs generated `manifest.json` output).
- 1 (2026-05-29): Initial version (as `agent-pack-export`) — collate project docs into an external LLM-assistant knowledge pack (Gemini Gem first; OpenAI GPT / NotebookLM / Claude Project / zip via a targets registry). Hybrid build engine (deterministic concatenation default; LLM condense only on `mode: condense` slots, flagged `derived`). Actions: setup, init, validate, build, list, publish (v2 stub). Provenance via git-commit stamp + per-source markers + verbatim/derived flag.
