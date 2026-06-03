---
name: knowledge-pack-export
description: |
  Collate a curated subset of project documentation, merge it to fit an external LLM-assistant platform's bounded knowledge budget, and emit a shareable, provenance-stamped "knowledge pack" (knowledge files + generated system-instructions + manifest). Primary target is a Google Gemini Gem (≤10 knowledge files); generalized to OpenAI Custom GPTs, NotebookLM, Claude Projects, and a plain zip handoff via a targets registry.

  TRIGGER when the user wants to **build, generate, package, export, assemble, or refresh** a knowledge bundle / assistant for a platform **outside Claude Code / Claude** — natural-language phrasings include:
    - "make a Gemini Gem from our project / docs"
    - "create a custom GPT / NotebookLM / Claude Project from these documents"
    - "package our strategy + architecture docs into a shareable assistant"
    - "export the key project content as a knowledge pack for an external team"
    - "merge all the strategy docs into one file so it fits the 10-file Gem limit"
    - "build the <pack-slug> pack", "refresh the knowledge pack", "what's in our knowledge packs"
    - "check the pack for stale / contradictory content before sharing"
    - any edit/write to a `*.pack.yml` manifest or to `.claude/skills/knowledge-pack-export/`

  Actions: `setup`, `init <pack-slug>`, `validate <pack-slug>`, `build <pack-slug> [--target <key>]`, `freshness <pack-slug>|--repo`, `list`, `publish <pack-slug>` (v2). Project-agnostic — all project-specific selection lives in the pack manifest, never in the skill.
version: 5
updated: 2026-05-30
---

# Knowledge Pack Export

Turn a repo full of project documents into the bounded bundle an external LLM assistant ingests — repeatably, with provenance. Usage: `/knowledge-pack-export <action> [arguments]`.

A **knowledge pack** is platform-neutral: a small set of **knowledge files** + a generated **`system-instructions.md`** + a **`manifest.json`** recording exactly which source files (and which git commit) each bundle was built from. A Gemini Gem, a Custom GPT, a NotebookLM notebook, or a Claude Project are all just *(system prompt) + (attached files)* — this skill produces both halves and stamps the provenance.

> **Naming note:** "knowledge pack," not "agent pack." This project has *agents* of its own (advisor agents, subagents); the artifact this skill exports is a **knowledge base** for an external assistant, not one of those agents. The name avoids that collision.

## Why this exists / the core constraint

External platforms cap the number of knowledge files you can attach (a Gemini Gem allows **10**). A project has hundreds of docs. The binding constraint is the **file count, not file size** — modern platforms accept large files, but retrieval quality degrades when knowledge is bloated. So the job is to **select** which docs belong in a pack and **merge** them into a small number of thematic bundles that fit the target's cap, while keeping the result groundable and auditable.

## Build model — deterministic by default, LLM only where it earns its keep

The build is a **hybrid** (this is the load-bearing design decision):

- **Deterministic concatenation is the default** (`mode: verbatim`). `scripts/build_pack.py` reads the manifest, expands the source globs, concatenates them verbatim with per-source provenance markers, and stamps the git commit. Reproducible, no hallucination, FDA-defensible.
- **The LLM is invoked only for two bounded jobs:**
  1. **Condensing a slot** (`mode: condense`) when a merge group is too large to ingest usefully. The deterministic pass stages the raw concatenation; the LLM rewrites it per the slot's `condense_brief`. The output is recorded as **`mode: derived`** in `manifest.json` so a reviewer never mistakes a summary for source-of-truth.
  2. **Authoring the persona** in `system-instructions.md` from the manifest's `persona` seed.

This keeps the safe, reproducible path as the default and confines non-determinism to slots the operator explicitly marked for curation. The same deterministic-finds / LLM-judges split powers the `freshness` action (below).

## Bundle structure — every bundle is self-describing and segmentable

Because one bundle file may combine several source documents, the engine makes each bundle navigable for both a human reviewer and a reading agent (all generated deterministically):

1. **A visible preamble** at the top of each `NN-*.md`: the bundle title + "bundle N of M", confidentiality, build commit/date, verbatim-vs-derived, and a **table of the documents inside** (title, source path, key `##` sections). A `═══ BUNDLED DOCUMENTS (verbatim below) ═══` line marks where generated navigation ends and source content begins. This is what lets you confirm at a glance that the right content was included.
2. **Visible, greppable segment markers** between documents: each source doc is introduced by a line `**▌DOCUMENT k of N — <title>**` + a `Source:` path (plus the machine-readable `<!-- source: path @ sha -->`). A reading agent segments a bundle into independent documents by splitting on `^\*\*▌DOCUMENT \d+ of \d+`.
3. **An agent guide** appended to `system-instructions.md` (the "How this pack is organized" section + a bundle map). It tells the assistant how to find a bundle, segment within it, and cite the `Source:` path. It lives in the system prompt, so it costs **no** knowledge-file slot.

## Supporting Files

| File | Purpose |
|------|---------|
| `README.md` | Design document — architecture, decisions, dependencies, lineage, intended use. |
| `scripts/build_pack.py` | Deterministic assembly engine. Subcommands: `validate`, `assemble`, `finalize`. Enforces target file-count cap; writes provenance `manifest.json` + `system-instructions.md` skeleton. |
| `scripts/freshness_check.py` | Read-only drift/staleness **candidate-finder** (project.yml-keyed contradiction scan + staleness + variants). High recall + context + advisory hints; the caller adjudicates. |
| `references/targets.yml` | External-platform registry — per-target file caps, formats, system-prompt mechanism, publish method. Add a platform here, not in the script. |
| `templates/example.pack.yml` | Pack-manifest template used by `init`. |

## Where things live

| Artifact | Location | Why |
|----------|----------|-----|
| Pack manifest (authored input) | `tools/knowledge-packs/<slug>/<slug>.pack.yml` | A pack is a self-contained deliverable unit; input + output live together under `tools/`. |
| Built pack (generated output) | `tools/knowledge-packs/<slug>/pack/` | Knowledge bundles + `system-instructions.md` + `manifest.json`, beside the manifest that produced them. |
| Platform caps/formats | `references/targets.yml` (in the skill) | Project-agnostic; shared across projects via the registry. |

## First-run mental model (read this if you've never used the skill)

There are **two different files** people conflate:
1. **The manifest** (`<slug>.pack.yml`, **YAML**) — the *authored input*. `init` generates a proposed one pre-filled from `project.yml`; you edit which docs go in which slots. This is the thing you maintain.
2. **`manifest.json`** — a *generated output* (provenance sidecar): git SHA, per-slot verbatim/derived mode, byte sizes. `build` writes it; you don't edit it.

Flow: `init <slug>` → edit the `.pack.yml` → `validate <slug>` → `build <slug>` → upload the files in `pack/` to your platform.

## Actions

Parse the user's argument string `$ARGUMENTS` to determine which action to perform.

### `setup`

Verify dependencies and the pack home. Idempotent. This skill ships no hooks/agents/rules, so setup is light.

1. Verify `python3` is available and `python3 -c "import yaml"` succeeds. If PyYAML is missing, tell the user to `pip install pyyaml` and stop — the engine needs it.
2. Create `tools/knowledge-packs/` if missing. Add `tools/knowledge-packs/README.md` if absent, explaining that each `<slug>/` subfolder holds a pack's manifest + built `pack/`.
3. Report what was verified / created.

### `init <pack-slug>`

Scaffold a new pack manifest, pre-filled from `project.yml` so the operator edits rather than writes from scratch.

1. Validate `<pack-slug>` matches `^[a-z][a-z0-9-]*[a-z0-9]$`.
2. If `tools/knowledge-packs/<pack-slug>/<pack-slug>.pack.yml` already exists, stop and report (don't clobber).
3. Read `references/targets.yml` for valid target keys. Read `project.yml` for project name + DHF roster (`dhfs[]`) to pre-populate `pack.title`, `pack.persona`, and suggest source globs (e.g. `docs/project/strategies/*.md`, per-DHF architecture paths).
4. Copy `templates/example.pack.yml`, fill in the slug/title, a default `targets: [gemini-gem]`, a confidentiality line (ask the operator if the content is controlled — default "Controlled — approved end users only"), and a first-cut `slots:` list derived from the project's actual folders.
5. Write `tools/knowledge-packs/<pack-slug>/<pack-slug>.pack.yml` and show the operator the slot list + the target's file cap + how many slots they've used. Tell them to review/edit, then run `validate`.

### `validate <pack-slug>`

Dry-run the pack against its target — no writes. Use before every build and whenever source docs change.

1. Resolve the manifest at `tools/knowledge-packs/<pack-slug>/<pack-slug>.pack.yml`.
2. Run: `python3 .claude/skills/knowledge-pack-export/scripts/build_pack.py validate tools/knowledge-packs/<pack-slug>/<pack-slug>.pack.yml [--target <key>]`.
3. Relay the report: slot count vs `max_files`, per-slot source count + size, any glob that matched no files, which slots are `condense`, and any **image-reference count** (`🖼 N img-refs`). Help fix the manifest (merge slots, fix globs) before building if it reports OVERFLOW or missing sources.

**Image caveat:** a text knowledge pack ingests markdown text only — **images do not travel** and relative `images/...` links will not resolve in the assistant. `validate` reports the image-reference count per slot so the operator knows which bundles lose figures (architecture/diagram-heavy docs especially). If figures are essential, render the doc to PDF via `/docflow` and attach that as the knowledge file instead, or describe the figure in the source markdown.

### `build <pack-slug> [--target <key>]`

Produce the full pack: deterministic-assemble → LLM-condense → finalize.

1. **Validate first** (run the `validate` command). If OVERFLOW or missing sources, stop and surface it.
2. **Assemble (deterministic):**
   `python3 .claude/skills/knowledge-pack-export/scripts/build_pack.py assemble tools/knowledge-packs/<pack-slug>/<pack-slug>.pack.yml [--target <key>]`
   Writes every `verbatim` slot to `tools/knowledge-packs/<pack-slug>/pack/`, stages each `condense` slot's raw concatenation under `pack/_staging/`, writes `manifest.json` + a `system-instructions.md` skeleton. Prints the pending-condense slots + their briefs.
3. **Condense (LLM — only for `pending-condense` slots):** for each staged `<file>.raw`, read it + the slot's `condense_brief`, then **write the curated bundle to `pack/<file>`**. Preserve the provenance banner **and the generated preamble** at the top of the raw file (it already carries the derived-summary header). Keep the `▌DOCUMENT k of N` segment markers around each section you retain. Curate to the brief — keep what it says to keep verbatim, summarize the rest, invent nothing. These are recorded `derived` — make the summary clearly a summary.
4. **Author the persona:** open `pack/system-instructions.md`, replace the persona TODO with role/scope/tone grounded in the manifest `persona` seed + the pack's actual contents. Keep it tight (overlong instructions make Gemini ignore the files). Keep the "consult the attached files first" line + confidentiality banner.
5. **Finalize:**
   `python3 .claude/skills/knowledge-pack-export/scripts/build_pack.py finalize tools/knowledge-packs/<pack-slug>/<pack-slug>.pack.yml [--target <key>]`
   Re-checks file count vs cap, confirms every bundle exists, records final sizes, flips condensed slots to `status: done`.
6. **Recommend a freshness pass** (`freshness <pack-slug>`) before sharing — a verbatim pack faithfully reproduces any stale content in its sources. Then **report:** the pack path, file count vs cap, total size, and the upload recipe for the target (from `references/targets.yml`). Remind the operator that **distribution access control is their responsibility** — the confidentiality banner travels with the pack, but platform sharing scope is set by the operator.

### `freshness <pack-slug>` | `freshness --repo`

Find content that may be **stale or contradictory** relative to the project's source-of-truth wiring (`project.yml`), before a pack ships. This is the relevance check: a verbatim pack is only as current as its sources, and `project.yml` is the oracle for structural facts (a module's IEC 62304 class, device/non-device status).

**Division of labor (the contract — D-211.7):** `scripts/freshness_check.py` is a **deterministic, high-recall candidate-finder, NOT an adjudicator.** It is regex-based: it cannot tell whether a line *asserts* a wrong value (real drift) or merely *mentions* it (a definition, a changelog row, prose discussing the drift, another vendor's software). So it **never suppresses** — it returns every candidate with surrounding context and **advisory signal hints**, and **you (Claude / the calling agent) do the semantic final pass.** This mirrors the build's hybrid split: the tool finds cheaply and reproducibly; the LLM judges.

**Configuration (project-agnostic engine, project-supplied patterns):** the contradiction patterns, module aliases, and hint markers live in `project.yml` under `knowledge_pack.freshness` — the engine hard-codes no project facts (audit-wiring rule). Each `contradictions[]` entry is `{id, regex, oracle}`: `regex` matches the stale assertion, `oracle` is the "what's correct now" note. If the block is absent, the contradiction scan prints a notice and skips; staleness + variants still run (they need no project facts). See the `project.yml` block's comments for the schema.

1. Run, scoped to a pack or the whole repo:
   - `python3 .claude/skills/knowledge-pack-export/scripts/freshness_check.py contradiction --pack <pack-slug> --json`
   - or `... --repo --json` for a repo-wide sweep.
   (Add `staleness`/`variants`/`all`; `--context N` for more lines; drop `--json` for human output.)
2. **Adjudicate each candidate.** For every hit, read its `context[]` + `hints[]` and classify:
   - **Real drift** — the line *asserts* a value contradicting `oracle` (e.g. a module-classification table cell saying "Class C" when project.yml says B). Hints like `in_table_row` + `module_named_nearby` raise the odds.
   - **Not drift** — a definition (`likely_definition`), an audit-trail row recording the fix (`likely_changelog`), a predicate's own class (`likely_predicate_cell`), drift-discussion in `_analysis/` (`in_analysis_doc`), or another vendor / the standard's text (`in_external_doc`).
   Hints are **advisory** — weigh them, don't treat them as verdicts.
3. **Report** the adjudicated list: genuine drifts (file:line + the corrected value) vs. dismissed candidates (with why). Recommend fixing drift **at the source doc**, then rebuilding — never patch the pack directly (that creates a third divergent copy).

The check **exits 0 always** — it's a finder, not a gate; severity is the caller's call.

### `list`

Show defined packs and their build state.

1. Glob `tools/knowledge-packs/*/`. For each, read `<slug>.pack.yml` → `slug`, `title`, `targets`.
2. If `<slug>/pack/manifest.json` exists, read `built_commit`, `built_date`, per-slot `status`/`mode` — report bundle count, whether any are `derived`, and whether `built_commit` lags current `HEAD` (pack is stale vs source).
3. Print a one-line-per-pack summary.

### `publish <pack-slug> [--target <key>]` — v2 (not yet implemented)

Create/update the assistant on the target platform directly. For `gemini-gem`, drives Gem creation under the corporate Google identity via the `/web-control` skill (launch/connect, upload knowledge files + paste system instructions). **Until implemented, this action explains the manual upload recipe** (same as `build` step 6) and points the operator at `/web-control`. Never call `chrome-devtools` cold — route through `/web-control`.

## Dependencies

| File / tool | Required by | Purpose |
|-------------|-------------|---------|
| `python3` + PyYAML | all build / freshness actions | Run the engine + finder (parse manifest + targets + project.yml). |
| `project.yml` | `init`, `freshness` | DHF roster + classification (`init`); `knowledge_pack.freshness` contradiction patterns + module aliases (`freshness`). The engine reads project facts from here — it hard-codes none. |
| `git` | `build`, `validate`, `freshness` | Stamp source commit SHA into `manifest.json`; git-age in staleness. |
| `/web-control` skill | `publish` (v2) | Authenticated browser session for Gem creation under corporate Google identity. |
| `/docflow` skill | optional | If a target needs PDF bundles, convert via docflow (raw pandoc is hook-blocked). |

## Notes

- **Generated artifacts are marked as such.** Every bundle carries a provenance banner; `manifest.json` distinguishes `verbatim` from `derived`. A reviewer must be able to tell source-of-truth from summary.
- **The skill is project-agnostic.** Which docs go in a pack, the confidentiality text, and the persona all live in the per-project `tools/knowledge-packs/<slug>/<slug>.pack.yml` — never hard-coded here.
- **Re-running is cheap and idempotent.** `build` overwrites the pack from current `HEAD`; re-run after source docs change. `list` + `freshness` show whether a pack lags its sources.
- If `$ARGUMENTS` is empty or just "help", show this usage guide.

## Best Practices
See [README.md](README.md) — consumed by `/best-practices` audit.

## Changelog
See [README.md](README.md) for version history.
