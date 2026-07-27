# corpus — skill design notes

Versioned evidence-corpus grounding engine: immutable dated snapshots of acquired data
(external APIs/web + internal exports/generators) with hash-chained provenance,
first-class assumption records, freshness enforcement, and refresh delta reports.

## Why this exists

Analyses that cite "the data" without pinning *which* data are unreproducible and
un-auditable. This skill gives any project a data tier where:

1. a citation `dataset@snapshot` is stable forever (immutability),
2. every value walks back to its raw source (provenance hash chain),
3. missing data becomes a **stated assumption** (A-NNN) instead of a silent invention,
4. staleness is a check failure, not a surprise (max_age_days + expiring waivers).

It deliberately owns **only** the data tier. Analysis skills (metric computation, claim
lint, reports) and visualization tiers (e.g. a project console) consume snapshots and
cite them — the separation is what keeps each layer honest.

## Design decisions

- **Single-script engine** (`scripts/corpus.py`, stdlib + PyYAML): all behavior
  deterministic and testable; the LLM orchestrates, the script computes and validates.
- **Staging-then-rename acquisition**: a failed acquire leaves zero residue. Same-day
  re-acquire suffixes (`.2`) rather than overwriting — immutability over tidiness.
- **`latest` is a plain text pointer file** (not a symlink): git-friendly, diff-friendly.
- **Acquisition is pluggable via `dataset.yml`**: built-in `openfda` (paginated) and
  `openfda-flatten` normalizer for the common public-FDA case; `command` type as the
  generic seam (generators for fabricated internal data, custom fetchers); `file` for
  export drops.
- **Schema is mandatory**: a dataset without a declared schema fails validation. The
  schema is what makes downstream computation trustworthy.
- **Usage rights are provenance**: every source records `usage_rights`; licensed data
  must not be redistributed and consumers can check the field mechanically.
- **Project-agnostic**: no project names, no dataset roster in the skill. The corpus
  root defaults to `docs/project/corpus/` but is `--root`-overridable; which datasets
  exist is entirely project configuration.

## Lineage

Extends the project pattern of document provenance (source-pinned PDF → source-md →
distilled, as used by medtech reference registries) to **structured data**. Sibling
conventions: skill-emitted JSON sidecars consumed by a project console; expiring
waivers mirror managed-TBD discipline in regulated docs.

## Dependencies

- Python 3.9+, PyYAML.
- Network access to `api.fda.gov` for openFDA acquisitions (offline projects can use
  `command`/`file` acquisition only).

## Best Practices

<!-- Consumed by /best-practices audit -->

| Check | How to Verify | Severity | Scope |
|-------|--------------|----------|-------|
| Skill has SKILL.md | File exists at skill root | Required | shared |
| Frontmatter complete | name, description, version, updated all present | Required | shared |
| README.md exists | Design doc at skill root | Required | shared |
| Changelog current | Latest entry matches version number | Required | shared |
| Corpus check green | `python3 scripts/corpus.py check` exits 0 in consuming project | Recommended | local |
| No hand-edited snapshots | `validate` reports no hash mismatches | Required | local |
| Waivers not expired | `check` reports no stale dataset without an active waiver | Recommended | local |

## Changelog

- 4 (2026-07-27): Generator provenance pinning — when an acquisition or normalize
  `command:` references a dataset-local script (`gen.py` pattern), the snapshot's
  provenance.yml `transforms[]` entry gains an additive `script_sha256` field pinning
  the exact script bytes that produced the snapshot. Old snapshots untouched;
  `validate` does not fail on its absence.
- 3 (2026-07-27): Battle-test hardening. Engine: extended asserts (`max_rows`, per-column
  `enums`, dataset-local `command:` check seam with normalize-style substitutions — how a
  dataset proves its generator/narrative knobs); `acquire --dry-run` (full pipeline in
  staging, results printed, nothing lands — no snapshot slot consumed); `validate` success
  output names each `dataset@snapshot`; optional `data_through:` dataset field recorded
  into provenance.yml as `as_of`; `assume --source` repeatable flag fills
  `sources_consulted` at scaffold time; `check` warns (never fails) on active A-records
  with TODO fields or empty `sources_consulted`; `init` stub gains
  `acquisition.system_of_record`. Docs: curated-file pattern (`file`-type +
  curated.csv), corpus-global A-NNN/W-NNN numbering, command execution contract
  (cwd = dataset dir, absolute substituted paths), file-type internal banner placement
  (README + description, never a CSV row), refresh-over-acquire for knob changes,
  shared-model coherence risk + recommendation.
- 2 (2026-07-22): openfda-count normalizer accepts date-field count buckets (openFDA
  returns `time` instead of `term` when counting on a date field) — enables historical
  count datasets (e.g. events per received-date). Note: openFDA rejects a `limit` param
  on date-field counts (403) — omit `count_limit` for those.
- 1 (2026-07-22): Initial version — engine with init / acquire / refresh / validate /
  diff / check / list / assume / waive; openfda (paginated rows + count-aggregation
  mode) + command + file acquisition types; openfda-flatten (dot-paths incl. list
  indices) + openfda-count + command normalizers; mandatory schema validation;
  hash-chained provenance.yml; A-NNN assumption records; W-NNN expiring waivers;
  freshness banding; refresh delta reports; absolute-path substitution for
  subprocess-based acquisition/normalization.
