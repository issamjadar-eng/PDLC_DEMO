---
name: commercial
description: "Business-question analysis engine — turns a project's business-question catalog (commercial.yml) into data-backed, provenance-cited ANSWER EDITIONS computed deterministically from corpus-skill snapshots, with a claim lint, a gated draft→approved→superseded lifecycle, and console JSON sidecars. Every numeric claim in an answer must carry a machine-resolvable marker ([src: dataset@snapshot], [assume: A-NNN], [derived: series-id], [config: path]); approval is BLOCKED until lint + freshness are green; approved editions are hash-pinned and immutable. TRIGGER when the user wants to: answer / compute / refresh a business question ('answer BQ-23', 'what's our campaign coverage', 'run the field analysis'); lint / check / approve a business answer or report edition; render or refresh the commercial console sidecars; see the question catalog or answer statuses; or add/modify business questions, computations, or the catalog in a project's commercial tree (commercial.yml, computations, reports/). Also trigger on edits under docs/project/commercial/reports/ — approved editions are immutable and hand-edits break approval hashes; route changes through answer/approve. Consumes the corpus skill's snapshots (data tier); produces reports + sidecars only — visualization belongs to the project console."
version: 7
updated: 2026-07-22
dependencies:
  skills:
    - name: corpus
      type: required
      reason: answers pin and cite corpus snapshots; lint resolves markers against the corpus tree
---

# Commercial — Business-Question Analysis Engine

The ANSWER tier of the three-tier analytics stack (corpus = data, commercial = answers,
console = display). A project registers its business questions in `commercial.yml`; each
implemented question has a deterministic computation script that reads pinned corpus
snapshots and writes an **answer edition**. This engine owns everything around that
computation: pinning, linting, lifecycle, and the console contract.

Core guarantees downstream consumers rely on:

- **The LLM never computes.** Numbers exist only because a registered computation script
  emitted them from pinned snapshots. Claude orchestrates (run, lint, interpret,
  approve) and writes prose *around* results — never figures into them.
- **Every figure is substantiated.** The claim lint fails any numeric claim in a report
  that lacks a resolvable marker: `[src: dataset@snapshot]` (must match the edition's
  pins), `[assume: A-NNN]` (must be an active corpus assumption), `[derived: id]` (must
  exist in the edition's data.json), `[config: path]` (declared plan constant). Where
  data doesn't exist, the assumption is stated as such — never silently absorbed.
- **Approval is a gate, not a label.** `approve` runs the lint + pin-freshness checks and
  refuses on any error; on success it hash-pins report.md + data.json (`approval.yml`),
  marks the prior approved edition superseded, and `check` screams if an approved file
  ever changes afterward.
- **Editions are history.** draft → approved → superseded; a refresh opens a NEW draft
  and never mutates an approved edition; superseded editions remain reproducible against
  their pinned snapshots forever.

## Supporting Files

| File | Purpose |
|------|---------|
| `scripts/commercial.py` | The engine — answer / lint / approve / render / check / catalog (Python 3.9+, PyYAML) |
| `templates/commercial.yml` | Starter question-catalog config for a new project |
| `templates/computation-example.py` | Example computation script showing the contract |

## The commercial tree (project-side)

```
<root>/                      # default docs/project/commercial/
  commercial.yml             # question catalog: id, question, category, personas, cadence,
                             #   corpus_deps, computation command, params
  computations.py            # project-owned deterministic computation functions
  reports/BQ-NN/<edition>/   # answer editions (edition id = date, .2 suffix on same-day)
    report.md                # the narrative answer — every figure marker-cited
    data.json                # chart series + verdicts, each with evidence_class + provenance
    pins.json                # dataset -> snapshot pins (written by the engine pre-compute)
    edition.yml              # status: draft | approved | superseded (engine-owned)
    approval.yml             # who/when/checks/content-hashes (written by approve)
  .console/commercial-index.json   # sidecar consumed by the project console
```

## Actions

All actions shell to the engine from the project root:

```bash
python3 .claude/skills/commercial/scripts/commercial.py <subcommand> ...
```

### `answer <BQ-NN>`
Pin the question's `corpus_deps` at their current `latest`, run the registered
computation into a NEW draft edition, then lint it. Drafts are re-generable (same-day
re-answer replaces the draft); an approved edition is never touched — re-answering that
day suffixes (`.2`). A computation must write both `report.md` and `data.json` or the
edition is discarded whole. After answering, read the report and surface the verdict and
any lint findings to the user — the computation's verdict headline is the answer.

### `lint <BQ-NN> [--edition E]`
The claim lint, standalone (also runs automatically inside `answer` and `approve`):
marker resolution (src pins, active assumptions, derived ids, config files, active
unexpired waivers), the numeric-claim rule (digits outside exempt tokens require a
marker on the line), estimation-language-needs-an-assumption (warning), pin freshness vs
each dataset's `max_age_days` (stale without `[waived: W-NNN]` = error), and data.json
series hygiene (evidence_class ∈ measured|derived|assumed|unavailable + provenance).

### `approve <BQ-NN> --by <name> [--edition E] [--verify-note <ref>]`
The gate. Lint errors block approval outright. On success: `approval.yml` with approver,
timestamp, check evidence, and content hashes; prior approved edition → superseded.
**Before approving a substantive new answer, run an adversarial verification**: spawn an
independent subagent that re-derives the headline claims from the pinned snapshots alone
(it gets the pins, not the report) and pass its verdict via `--verify-note`. For routine
refreshes with unchanged methodology, the lint gate alone may suffice — say which was
done.

### `render`
Write `.console/commercial-index.json` (`schema_version: 1.0`) — per question: status
(not-implemented | no-answer | draft-only | answered), approved/draft editions, verdict
headline, worst-of evidence class, freshness band, assumptions cited, report/data paths.
The console is a pure consumer of this file.

### `check`
Whole-chain integrity: approved/superseded content hashes intact (mutation detection),
approved editions still lint green, and the corpus chain green (invokes the corpus
skill's `check`). Run before demos and before rendering anything user-facing.

### `audit <BQ-NN> [--edition E]`
(Re)generate the edition's `quality.json` — the machine-checked audit surface: lint
status (errors/warnings), the resolved-reference inventory (every marker with a
resolved/broken verdict and a one-line note), and per-pin freshness detail. Written
automatically by `answer`, `lint`, and `approve`; run `audit` to refresh it standalone.
Agent-recorded `verifications` entries are preserved across rewrites.

### `record-verification <BQ-NN> --type <t> --verdict <v> --by <who> --summary <s> [--detail-ref <path>] [--edition E]`
File an agent-produced verification into `quality.json` — the half of quality the
engine cannot generate deterministically. Types: `adversarial-verify` (independent
pins-only re-derivation), `red-team` (framing attack), `reference-audit`,
`human-review`. **When you (Claude) run a verify/red-team agent over an answer, file
the outcome here** — an unfiled verification is invisible to the audit surface.
Consoles render these with verdict chips next to the machine checks.

### `catalog`
The question roster with per-question answer status at a glance.

## Registering a question (project-side `commercial.yml`)

```yaml
questions:
  - id: BQ-23
    question: "Where do we stand on campaign coverage vs plan?"
    category: field-ops
    personas: [field-service]
    cadence: weekly
    corpus_deps: [commercial/internal-upgrade-campaign]
    computation: "python3 computations.py BQ-23 --corpus-root {corpus_root} --out {out}"
    params: {close_date: "2026-09-30", target_pct: 95}
```

The computation contract: invoked with cwd = the commercial root; `{corpus_root}` and
`{out}` are substituted absolute paths; `{out}/pins.json` already exists (read it —
compute ONLY from those snapshots); write `report.md` + `data.json` into `{out}`.
Questions without a `computation` are `not-implemented` — visible in the catalog and
sidecar as roadmap, never silently missing. Plan constants (targets, close dates) live
in `params` and are cited in reports as `[config: commercial.yml]`.

**Plan expectations (first-class).** A question may declare `expectations:` — the plan
assumptions its actuals are judged against, each with `id` (E-NN.N), `statement`,
`expected`, `basis`, `set_by`, and `validated:` (false = the expectation itself is a
stand-in not yet grounded in a plan of record / risk file — consoles flag it as
challengeable). Computations evaluate every declared expectation and emit
`data.json.expectations[]` with `actual`, `verdict` (met | at-risk | not-met |
not-evaluable), and `evidence[]`; the same table renders into the linted report. An
expectation the computation didn't evaluate surfaces as `not-evaluable` — a finding,
not a silent omission. This answers "the actuals come from data — but are the
assumptions being met, and are they even correct?"

**Choosing the series form — the diagram follows the data's job.** A computation
declares each series' `kind`; consoles render it. Pick by what the data is FOR, not by
habit (the form heuristic from the dataviz method):

| The data's job | `kind` | Shape |
|---|---|---|
| One headline number (a KPI the verdict hangs on) | `stat` | points: `[{label, value, sub?}]` — rendered as hero-number tiles, not a chart |
| Magnitude across categories (which is biggest?) | *(default — omit kind)* | points: `[{label, value, ...extras}]` — thin horizontal bars, direct labels |
| Plan vs actual / two measures per category | `paired-bars` | `pairs: {a_label, b_label}` + points `[{label, a, b}]` — grouped bars + legend (a = actual first) |
| Change over time (trend, history, stalls) | `timeseries` | `lines: [{label, points: [{x: ISO-date, y}]}]` — ≤4 lines, zero-fill gaps so stalls flatline |
| Per-category dates or verdicts (non-numeric) | *(default)* with non-numeric values | key-value list |
| Data that does not exist | any, `evidence_class: unavailable` + provenance `note` | designed-absence card — state the gap, never fake the form |

**Report-table citations ride inline, never in an Evidence column.** Append the row's
markers to the end of its label cell (or beside the specific figure they substantiate) —
`| Baxter Healthcare [src: ds@snap] | 9 | 74 |`. Consoles render markers as compact
superscripts, so an inline citation costs no width; a dedicated Evidence column wastes a
column to say what a footnote says. The claim lint is line-based, so one marker anywhere
on the row satisfies it for that row's figures.

Form rules that always hold (dataviz non-negotiables): one axis — never a dual-axis
chart (two measures of different scale = two series/charts or `paired-bars`); a
history series that has only one snapshot behind it is NOT a trend — publish the
point-in-time form plus an `unavailable` history series naming what would build the
history (e.g. recurring corpus snapshots); identity is never color-alone (consoles
pair every hue with a label). **Every answered question should carry, where the data
allows: a headline `stat`, the categorical/comparison form, and a `timeseries`
history** — a report without a historical view should say why (data gap), not just
omit it.

**Derivation chains (required for derived series).** A series with
`evidence_class: derived` must declare `derivation: {method: "<one-line formula>",
inputs: ["src: ds@snap", "derived: other-series", "config: path", ...]}` — the lint's
`derivation-chain` check fails a derived series without one. Inputs use the marker
vocabulary, so the chain plugs into the reference layer and walks onward through corpus
provenance to raw sources. New lint rules grandfather already-approved (immutable)
editions in `check` — full enforcement applies at the next approval.

**Answer-edition data.json extensions** (all optional, consoles degrade gracefully):
- `narrative: {issues[], risks[], watch[]}` — decision-ready Risks / Mitigations /
  Issues, generated **deterministically from the computed facts** (each item: id,
  severity, statement, mitigation|action, evidence[]). The narrative is mirrored into
  the report body where the claim lint applies to it.
- a series may set `kind: timeseries` with `lines: [{label, points: [{x: ISO-date,
  y: number}]}]` (≤4 lines; zero-fill gaps so stalls render as flatlines, not holes) —
  consoles render trend line charts from it.

## Dependencies

| File | Required by | Purpose |
|------|-------------|---------|
| Python 3.9+ with PyYAML | all actions | engine runtime |
| corpus tree (default `docs/project/corpus/`) | answer/lint/approve/check | pinned data tier |
| `<root>/commercial.yml` | all actions | the project's question catalog |

## Notes

- **Never hand-edit an edition** — drafts are regenerated by `answer`; approved editions
  are hash-pinned. Fix the computation or the catalog, then re-answer.
- Reports over internal (fabricated) datasets must carry the project's demo-data banner —
  the computation script owns stamping it.
- Entity normalization (e.g. manufacturer-name variants in public FDA data) is an
  analysis-tier concern: keep the alias map in a project config file cited via
  `[config: ...]` so normalization choices are versioned and reviewable.
