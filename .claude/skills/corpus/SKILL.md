---
name: corpus
description: "Versioned evidence-corpus grounding engine — acquire external data (openFDA, web, APIs) and internal exports into immutable, provenance-pinned snapshots that analyses can cite as dataset@snapshot. Owns the corpus tree (default docs/project/corpus/): dated snapshots (raw byte-pinned payloads + schema-validated normalized CSV + provenance.yml with hash-chained lineage), first-class A-NNN assumption records (where data doesn't exist, the assumption is stated, never silently invented), W-NNN freshness waivers with expiry, per-dataset max_age_days freshness enforcement, and refresh delta reports ('what changed since last snapshot'). TRIGGER when the user wants to: acquire / snapshot / pull / pin / version external or internal data for grounding ('snapshot the openFDA 510(k) data', 'pull competitor recalls into the corpus', 'set up a dataset for X'); refresh a corpus or ask what changed since the last refresh; record or review an assumption where data is unavailable; check corpus health, freshness, staleness, or provenance integrity; waive a stale dataset; or diff two snapshots. Also trigger on any edit under a corpus tree (dataset.yml, snapshots/, assumptions/, waivers/) — snapshots are immutable and hand-edits break hash pins; route changes through the actions. Downstream analysis skills (e.g. a commercial-analytics skill) declare corpus datasets as dependencies and cite snapshots — this skill owns the data tier only, no analysis, no visualization."
version: 1
updated: 2026-07-22
---

# Corpus — Versioned Evidence Grounding Engine

One engine for the project's **grounding data tier**: every dataset an analysis wants to
cite lives here as **immutable dated snapshots** with machine-walkable provenance. The
contract downstream consumers rely on:

- **A citation `dataset@snapshot` is stable forever.** Snapshots are never mutated —
  re-acquisition creates a new snapshot; `latest` is just a pointer. Approved reports can
  pin a snapshot and stay reproducible years later.
- **Every normalized value traces to a raw source.** `provenance.yml` chains
  normalized-file hashes → raw-payload hashes → source URL/system + retrieval timestamp +
  usage rights. `validate` re-hashes the chain; a mutated file is an error, loudly.
- **Missing data becomes a stated assumption, never a silent invention.** When a question
  needs data that doesn't exist (competitor sales, customer-side costs), record an
  `A-NNN` assumption (method, confidence, refresh trigger) and cite *it*. Refresh delta
  reports list active assumptions for review; contradicted ones fail `check` until triaged.
- **Staleness is enforced, not hoped.** Each dataset declares `max_age_days`; `check`
  bands snapshots fresh / aging / stale. A stale dataset fails `check` unless a `W-NNN`
  waiver (owner + expiry — waivers expire too) covers it.

Layers: this skill owns **data acquisition + integrity only**. It performs no analysis,
computes no metrics, renders no visualization — downstream skills consume snapshots and
cite them.

## Supporting Files

| File | Purpose |
|------|---------|
| `scripts/corpus.py` | The engine — all actions are subcommands (requires Python 3.9+, PyYAML) |
| `templates/dataset-openfda.yml` | Example dataset.yml for an openFDA-acquired external dataset |
| `templates/dataset-generator.yml` | Example dataset.yml for a script-generated internal dataset |
| `templates/README-corpus-root.md` | README template for a project's corpus root folder |

## The corpus tree

```
<corpus-root>/<domain>/<dataset>/          # e.g. commercial/openfda-510k
  dataset.yml            # config: acquisition, normalize, schema, max_age_days, usage rights
  README.md              # what the dataset is, source, consumers
  snapshots/YYYY-MM-DD/  # immutable; same-day re-acquire gets a .2 suffix
    raw/                 # byte-pinned payloads exactly as acquired
    normalized/          # schema-validated CSV
    provenance.yml       # sources, hash chain, checks — written by the engine only
    delta-report.md      # written by refresh (vs the previous latest)
  assumptions/A-NNN.yml  # stated assumptions (status: active | contradicted | retired)
  waivers/W-NNN.yml      # freshness waivers (owner, expires, status)
  latest                 # pointer file: newest valid snapshot id
```

Default root: `docs/project/corpus/` (override with `--root`). Domain folders group
datasets by consumer (e.g. `commercial/`); a dataset's full name is `<domain>/<name>`.

## Actions

All actions shell to the engine. Run from the project root:

```bash
python3 .claude/skills/corpus/scripts/corpus.py <subcommand> ...
```

### `init <domain>/<dataset>`
Scaffold a new dataset: folders + a `dataset.yml` stub (acquisition/normalize deliberately
fail with TODO until configured) + README. Then edit `dataset.yml`:

- **`acquisition.type`**: `openfda` (endpoint + search + limit/max_records; paginates
  automatically — or add `count:` for openFDA's aggregation API, the right shape for
  high-volume endpoints like MAUDE events where row-level snapshots would be 10k+ rows;
  pair with `normalize.type: openfda-count` for a term,count CSV), `command` (any shell
  command writing files into `{raw_dir}` — the seam for generators and custom fetchers),
  or `file` (copy an export drop).
- **`acquisition.usage_rights`** is mandatory in spirit: `public-domain`, `licensed (no
  redistribution)`, or `internal`. Licensed data must never be republished — downstream
  consumers read this field.
- **`normalize`**: `type: openfda-flatten` with dot-path `fields:` (built-in), or
  `command:` with `{raw_dir}` / `{normalized_dir}` placeholders.
- **`schema`**: `key:` columns (uniqueness enforced) + `columns:` with
  `type: str|int|float|date` and `required:` flags. Mandatory — a dataset without a
  schema fails validation by design.
- **`max_age_days`**: match the source's real cadence (recalls ~30, clearances ~90,
  internal telemetry ~7, market reports ~365).
- **`internal: true`** marks fabricated/company-internal data; for demo projects the
  generator should stamp its outputs with the project's demo-data banner.

### `acquire <domain>/<dataset>`
Build a new snapshot in staging: acquire → normalize → schema-validate → asserts →
write `provenance.yml` → move into `snapshots/` and update `latest`. **Nothing lands on
failure** — a broken acquisition leaves the corpus exactly as it was. Never hand-create
snapshot folders; the hash chain only exists when the engine writes it.

### `refresh [<dataset>]`
`acquire` plus a **delta report** against the previous latest (added/removed/changed rows
by key) written into the new snapshot, ending with the active assumptions to re-review
against the new data. Omit the dataset to refresh everything. The delta report is the
"what changed in our world" briefing — surface it to the user, don't just file it.

### `validate [<dataset>] [--snapshot ID]`
Integrity for one snapshot (default: latest, all datasets): re-hash raw + normalized files
against `provenance.yml` (mutation detection), parent-hash chain resolution, schema +
asserts re-run, referenced assumption records exist, usage rights present.

### `check`
Whole-corpus health, one command: validate every latest snapshot + freshness banding vs
`max_age_days` (stale without an unexpired waiver = failure) + assumption status
(contradicted = failure until triaged). Exit 0 = GREEN. Run before any downstream
analysis publishes, and in CI if the project wires it.

### `diff <dataset> <snapA> <snapB>`
Row-level delta between any two snapshots (markdown to stdout).

### `assume <dataset> --title ... [--why --method --value --confidence --needed-for --refresh-trigger]`
Scaffold the next `A-NNN` record. Fill every TODO before citing it — an assumption
record is a first-class citable object, held to the same standard as data: state what was
needed, why it's unavailable, the estimation method, the value/range, confidence, and
what event should trigger re-estimation. When a refresh contradicts an assumption, set
`status: contradicted` (check fails until it's revised or retired).

### `waive <dataset> --reason ... --owner ... --expires YYYY-MM-DD`
Scaffold a `W-NNN` freshness waiver. Waivers are visible, owned, and **expire** — a
waiver is a scheduled debt, not a permanent exemption.

### `list`
All datasets: snapshot count, latest, freshness band, assumption count, internal flag.

## Dependencies

| File | Required by | Purpose |
|------|-------------|---------|
| Python 3.9+ with PyYAML | all actions | engine runtime |
| corpus root folder (default `docs/project/corpus/`) | all actions | the data tree; scaffold its README from `templates/README-corpus-root.md` on first use |
| network access to `api.fda.gov` | `acquisition.type: openfda` | openFDA acquisition |

## Notes

- **Immutability is the contract.** If a snapshot is wrong, acquire a new one — never edit
  in place. `validate` treats a hash mismatch as possible tampering and says so.
- **Demo projects**: internal datasets are typically fabricated by a `command`-type
  generator script living next to `dataset.yml`; the generator must stamp the demo-data
  banner into its outputs. External openFDA data is real — do not mix fabricated rows
  into an external dataset.
- **Respect usage rights.** `public-domain` (openFDA) may be committed and shared;
  `licensed` payloads should be summarized/derived rather than redistributed — when in
  doubt, keep raw out of git for that dataset and record the hash only.
- Git versions the corpus, but the snapshot/provenance layer — not git history — is the
  product surface downstream consumers navigate.
