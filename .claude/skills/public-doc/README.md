# Public-Doc — Design & Architecture

Design notes for the `public-doc` skill. Not loaded during normal operation — for human understanding. For usage, see `SKILL.md`.

## Overview

`public-doc` authors external-facing documents (white papers, articles, one-pagers, briefs) with a strict separation between the public layer (what ships) and the internal layer (evidence, rationale, metadata that backs the claims but never ships). It manages a draft state with `public_doc:` metadata, an INTERNAL-block convention for inline supporting content, a leak-safe strip-for-publish step, and advisory brand/style linting read from the project's own config.

## Lineage

Original skill, not adapted from a prior registry skill. The PDF render pipeline in `scripts/render.py` is generalized from a project-specific whitepaper render script (mermaid → pandoc `--wrap=none` → headless Chrome), made source-agnostic with Chrome auto-detection and graceful degradation when external tools are absent.

## Key Design Decisions

### Two INTERNAL forms: collapsible (primary) + single-comment (terse)

The convention supports two forms, both delimited by `INTERNAL:BEGIN`/`INTERNAL:END` sentinels that always live inside HTML comments:

- **Collapsible (primary)** — paired comment sentinels wrap a `<details>` element, so internal metadata/context *folds away* in GitHub/preview and the author sees the public content by default. This is the form for the pre-Section-1 metadata block (purpose, audience, goals, thesis, key points) and any multi-line rationale/evidence. Authoring ergonomics (fold internal context away; the document reads as the public draft) drove making this primary.
- **Single comment (terse)** — both markers inside one HTML comment; fully hidden even unstripped. Best for one-line inline notes. Constraint: no `-->` in the body.

Initial design (v1) used only the single-comment form, chosen for its structural leak-safety (content can never render even unstripped). v2 added the collapsible form on request, accepting a managed tradeoff: a `<details>` body sits in the HTML DOM until stripped, so the **published path must always be `build`** (strip + verify), never the raw `.md`. The leak invariant is enforced uniformly by lint (every INTERNAL marker must sit inside an HTML comment) and by strip/build (abort if any marker survives). `strip`'s single removal rule — `<!-- INTERNAL:BEGIN … ` through the next `INTERNAL:END -->` — covers both forms, and the collapsible form additionally tolerates `-->` in its body because the rule anchors on the END sentinel, not the first `-->`.

### The skill is project-agnostic; company values live in `tools/public-doc/`

Per the registry's HARD RULE, skills carry no company names, taglines, or banned-word lists. All of that is project config under `tools/public-doc/`, read at runtime. `init` scaffolds it from generic seed templates and never overwrites a populated config. This is what lets the same skill serve every project in the registry.

### Lint is advisory; strip is absolute

Brand/style findings are advisory (exit 0, never blocks) — house style is a judgment call and a hard gate would create drafting friction. But `strip`/`build` treat a malformed or surviving INTERNAL block as a hard error: a leak is the one outcome with no acceptable failure mode, so the *removal* path is absolute even while the *lint* path is soft.

## Roadmap / tracked future improvements

- **Promote `leak` findings to a hard gate.** Today `lint` reports leaks advisorily; `build` already aborts on a surviving marker, but `lint` run on its own does not fail CI. Once the convention has shaped a few documents, make `lint --strict` (or a default) return non-zero on any `leak` finding so CI can block a PR that would publish internal content. Deferred per author preference to try advisory-first.
- **`status` lifecycle enforcement.** Optionally refuse `build` unless `status: approved`.
- **HTML deck handoff.** A `--format deck` that hands the stripped markdown to `md-deck` for a Terminal Green deck, closing the loop with the project's presentation toolchain.
- **Multi-profile diffing.** Render the same draft under two `brand_profile`s (e.g., branded vs. neutral) in one command.

### Trigger description & disambiguation

The description is tuned to disambiguate from the deck/presentation skills (`md-deck`, `frontend-slides`, `pptx`): it scopes to **prose** documents and explicitly hands slides/presentations to those skills. The skill-creator cross-skill conflict scan is clean (no verb/object overlap, no hook collisions). Note: the skill-creator automated *trigger eval* (`run_eval` / `audit-triggers`) does not yield usable signal in every environment — its headless `claude -p` trigger detection can read 0.0 across the board (even for verbatim trigger phrases), so it was not used as the optimization signal here. Trust the conflict scan + judgment over that number until the harness detection is fixed.

## Dependencies

| File / tool | Required by | Purpose |
|------|-------------|---------|
| `tools/public-doc/brand.yml`, `lint-rules.yml` | `lint`, `build` | project brand/style values (optional; leak+verify checks run without them) |
| `python3` | all scripts | strip / lint / render are Python, stdlib-only (PyYAML optional; falls back to a mini-parser) |
| `pandoc` | `build --format html\|pdf` | markdown → HTML |
| `npx` + `@mermaid-js/mermaid-cli` | `build` when the doc has mermaid | diagram → SVG |
| Chrome/Chromium | `build --format pdf` | HTML → PDF (auto-detected; `$PUBLIC_DOC_CHROME` / `--chrome` override) |

`build --format md` (strip only) needs nothing beyond Python — useful in CI or bare environments.

## Best Practices

<!-- Consumed by /best-practices audit -->

| Check | How to Verify | Severity | Scope |
|-------|--------------|----------|-------|
| Skill has SKILL.md | `.claude/skills/public-doc/SKILL.md` exists | Required | shared |
| Frontmatter complete | name, description, version, updated all present | Required | shared |
| README.md exists | Design doc at skill root | Required | shared |
| Changelog current | Latest entry matches frontmatter `version` | Required | shared |
| Scripts executable by python3 | `strip_internal.py`, `lint_doc.py`, `render.py` run with `--help` | Required | shared |
| No company values in skill | grep skill tree for company names returns nothing (values live in `tools/public-doc/`) | Required | shared |
| Project config present | `tools/public-doc/brand.yml` exists (run `/public-doc init`) | Recommended | local |
| No internal leak in published artifacts | published PDF/HTML contains no `INTERNAL:` marker | Required | local |

## Changelog

- 3.1 (2026-06-29): **Title-page version line now composes `status` + `version` + `updated`** (e.g. "Draft · v0.4 · 2026-06-29") instead of showing the bare `updated` date, so a draft is always visibly marked as a draft on the rendered PDF. An explicit `--date` still overrides the whole composition. `render.py` only — no template/CSS change.
- 3 (2026-06-25): **PDF rendering rebuilt on the Chrome DevTools Protocol** (`scripts/cdp_print.js`, node built-in WebSocket — no npm install). Fixes a `--headless=new --print-to-pdf` bug that silently truncated output to one page, and replaces Chrome's un-suppressable file-path footer with a **running logo header + copyright footer** (page numbers, no path). New `render.py` flags `--logo` / `--footer` / `--author` / `--date`; logo + copyright default from `tools/public-doc/brand.yml` (`pdf:` block), author from frontmatter `author`, date from `updated` — keeps the skill project-agnostic. Refined print CSS: clean all-serif, left-aligned (no hyphenation), no heading rules, centered title page, TOC anchors preserved as clickable PDF links.

- 2 (2026-06-17): Added the **collapsible INTERNAL form** (`<!-- INTERNAL:BEGIN -->` + `<details>` + `<!-- INTERNAL:END -->`) as the primary form for metadata/context, alongside the single-comment form (both strip-safe via one removal rule). Reworked `lint`'s leak check to a comment-span invariant (every marker must sit inside an HTML comment) — handles both forms with no false positives. `render.py` now emits **title page (title + `brief`) → TOC page → content sections** (`--toc`, title-block kept, `--brief` / `--no-toc` / `--no-title-page` flags; `brief`/`subtitle` read from frontmatter). Updated draft template (collapsible metadata block) and the INTERNAL spec.
- 1 (2026-06-17): Initial version. Draft-state `public_doc:` metadata; single-comment INTERNAL-block convention; `init` / `new` / `lint` / `build` actions; leak-safe `strip_internal.py`; advisory `lint_doc.py` (leak/brand/style/verify) reading project config from `tools/public-doc/`; `render.py` strip → mermaid → pandoc → Chrome pipeline with tool auto-detection. Lint advisory-first; hard leak-gate tracked in Roadmap. Description scoped to prose + explicit deck-skill disambiguation; cross-skill conflict scan clean. (`evals/trigger-eval.json` holds a domain trigger set for when the eval harness is reliable.)
