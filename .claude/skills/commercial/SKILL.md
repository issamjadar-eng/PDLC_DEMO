---
name: commercial
description: "Business-question analysis engine — turns a project's business-question catalog (commercial.yml) into data-backed, provenance-cited ANSWER EDITIONS computed deterministically from corpus-skill snapshots, with a claim lint, a gated draft→approved→superseded lifecycle, and console JSON sidecars. Every numeric claim in an answer must carry a machine-resolvable marker ([src: dataset@snapshot], [assume: A-NNN], [derived: series-id], [config: path]); approval is BLOCKED until lint + freshness are green; approved editions are hash-pinned and immutable. TRIGGER when the user wants to: answer / compute / refresh a business question ('answer BQ-23', 'what's our campaign coverage', 'run the field analysis'); lint / check / approve a business answer or report edition; render or refresh the commercial console sidecars; see the question catalog or answer statuses; audit the quality of the analysis code or file/record a code review ('code-audit the computations', 'review the BQ modules', 'is the analysis code reviewed'); or add/modify business questions, computations, or the catalog in a project's commercial tree (commercial.yml, computations, reports/). Also trigger on edits under docs/project/commercial/reports/ — approved editions are immutable and hand-edits break approval hashes; route changes through answer/approve. Consumes the corpus skill's snapshots (data tier); produces reports + sidecars only — visualization belongs to the project console."
version: 12
updated: 2026-07-27
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
    edition.yml              # status: draft | approved | superseded (engine-owned);
                             #   pins plan hash + code_artifacts (the code bytes that computed it)
    approval.yml             # who/when/checks/content-hashes (written by approve)
  code-quality/records.yml   # engine-managed code-quality store (checks + AI reviews per artifact sha)
  .console/commercial-index.json   # sidecar consumed by the project console
```

## Actions

All actions shell to the engine from the project root:

```bash
python3 .claude/skills/commercial/scripts/commercial.py <subcommand> ...
```

### `answer <BQ-NN>`
Pin the question's `corpus_deps` at their current `latest`, run the registered
computation into a NEW draft edition, then lint it. A computation must write both
`report.md` and `data.json` or the edition is discarded whole. After answering, read the
report and surface the verdict and any lint findings to the user — the computation's
verdict headline is the answer.

**Same-day edition semantics.** Re-answering on the same day REPLACES an unapproved
draft in place — same edition id, regenerated content. The `.2` suffix mints only when
the same-day edition is already approved (approved editions are never touched). Filed
`verifications` records survive the replacement: the engine rescues them from the
replaced draft's quality.json and re-files each with `carried_from_replaced_draft: true`
— but the carried verdict was rendered against the OLD bytes (compare its
`report_sha256` stamp), so a substantive re-answer still warrants a fresh verification.

### `lint <BQ-NN> [--edition E]`
The claim lint, standalone (also runs automatically inside `answer` and `approve`):
marker resolution (src pins, active assumptions, derived ids, config files, active
unexpired waivers), the numeric-claim rule (digits outside exempt tokens require a
marker on the line), estimation-language-needs-an-assumption (warning), pin freshness vs
each dataset's `max_age_days` (stale without `[waived: W-NNN]` = error), and data.json
series hygiene (evidence_class ∈ measured|derived|assumed|unavailable + provenance).

Mechanics report authors must know (each one caused real friction when learned the
hard way):

- **The numeric-claim rule is LINE-based.** A figure and its marker must share a
  physical line — a marker on the next line, or on the sentence's earlier line after a
  hard wrap, does not cover it. One marker anywhere on a line covers every figure on
  that line (this is what makes inline table-row citations work). Wrap prose so the
  digits and their marker stay together.
- **Built-in exempt tokens** (digit-bearing identifiers, not claims): `BQ-NN`, `A-NNN`,
  `W-NNN`, `C-YYYY-NN`, ISO dates / edition ids (`YYYY-MM-DD(.N)`), `PPNNNN`, `PE-N`,
  `S-XX-N`, `KNNNNNN`, expectation ids `E-N(.N)`, `FYNNNN`, `YYYY-Q[1-4]`,
  `YYYY-H[12]`, and `510(k)`.
- **Projects extend the lint via a `lint:` block in commercial.yml** — relax-only, it
  can never add findings:
  ```yaml
  lint:
    exempt_patterns: ["RPT-\\d+"]          # extra identifier regexes for the numeric rule
    estimation_exempt_terms: [modeled]     # plan-defined vocabulary, not hedging
  ```
- **The estimation-language word list** (case-insensitive, warning-level):
  `estimate(d)`, `likely`, `approximately`, `roughly`, `assume(d)`, `modeled`. A line
  using one without an `[assume: A-NNN]` warns. When a word is a committed **defined
  term** in the analysis plan (e.g. a `modeled` bucket label in a
  contracted/modeled/aspiration decomposition), exempt it via
  `estimation_exempt_terms` rather than contorting the prose — and define it in the
  plan so the exemption is auditable.
- **`[assume: A-NNN]` resolution is corpus-WIDE, not pin-scoped.** The lint finds the
  record anywhere under the corpus tree, which is convenient for shared assumptions
  (e.g. a market-size record living in a neutral dataset) — but it also means a typo'd
  or lookalike id can resolve against the wrong dataset's record. Convention: the
  plan's Assumptions section names each assumption's home dataset, so a reviewer can
  check the citation is the intended record.
- **Snapshot-id date = data as-of date.** For urgency/recency computations (days
  remaining, staleness, trailing windows), anchor on the pinned snapshot's id date (or
  the snapshot's corpus `as_of` provenance field when present) — never on the
  machine's "today", which makes an answer non-reproducible and silently shifts
  verdicts every time it is re-run.
- **Join-heavy series pin multiple datasets.** Series hygiene accepts
  `provenance: {datasets: [{dataset, snapshot}, ...]}` as an alternative to the single
  `{dataset, snapshot}` form — use it when a series is computed from a join across two
  pins instead of attributing the join to one side.

### `approve <BQ-NN> --by <name> [--edition E] [--verify-note <ref>]`
The gate. Lint errors block approval outright. On success: `approval.yml` with approver,
timestamp, check evidence, and content hashes; prior approved edition → superseded.
**Before approving a substantive new answer, run an adversarial verification**: spawn an
independent subagent that re-derives the headline claims from the pinned snapshots alone
(it gets the pins, not the report) and pass its verdict via `--verify-note`. For routine
refreshes with unchanged methodology, the lint gate alone may suffice — say which was
done. `approve` also prints the edition's code-quality status (see "Code quality"
below) — informational only, never a blocker.

### `render`
Write `.console/commercial-index.json` (`schema_version: 1.3`) — per question: status
(not-implemented | no-answer | draft-only | answered), approved/draft editions, verdict
headline, worst-of evidence class, freshness band, assumptions cited, report/data paths.
The console is a pure consumer of this file. The card's verdict/badges come from the
**newest edition regardless of status** — a fresh draft supersedes an older approved
answer on the card, because showing an out-of-date verdict as "the answer" is worse
than showing an unapproved one (the status chip discloses draftness).

Schema 1.1 adds two reader-aid fields per question row, both sourced from the catalog
(see "Terms & explainers" below) and purely additive — 1.0 consumers degrade gracefully
by ignoring them:

- `"explainers": {…}` — the question's `explainers:` map, verbatim.
- `"terms": [{"term", "definition"}, …]` — the question's `terms:` reference list
  resolved against the catalog's top-level `terms:` dictionary. An unresolved key is a
  render warning to stderr and is skipped — the engine never fabricates a definition.

Schema 1.2 adds a per-question `"code": {…}` block — the code-quality soft-gate badge
surface (see "Code quality" below). Purely additive; older consumers ignore it.

Schema 1.3 adds, per code artifact, `"review_history": […]` — reviews filed against
earlier, now-superseded shas of the same path, so the original (pre-fix) findings stay
visible after the code moves to a new hash. Each entry: `{sha256_12, date, verdict,
by, summary, findings[], detail_ref, superseded: true}`, newest first, capped at 5.
Purely additive; ≤1.2 consumers ignore it. The same block flows into quality.json.

### `check`
Whole-chain integrity: approved/superseded content hashes intact (mutation detection),
approved editions still lint green, and the corpus chain green (invokes the corpus
skill's `check`). Run before demos and before rendering anything user-facing.

### `plan-init <BQ-NN>`
Scaffold the question's **analysis plan** — `plans/BQ-NN.md`, the user-owned prose
contract: Goal (the decision served), Approach (committed definitions — windows,
anchors, denominators), Data (have vs need, gaps stated), Assumptions & expectations,
and Assertions & limits (what the answer does NOT claim). Templated from the catalog
entry with category-specific approach hints, then **never overwritten** — users edit
freely. `answer` pins the plan's hash into the edition; the `plan-currency` lint check
calls out a missing plan, an unpinned edition, or a plan that **changed after the
edition was computed** (drift). Whether the computed answer actually HONORS the plan's
intent is an agent judgment: run an intent-check agent (give it the plan + the
edition; strict — a committed definition not followed is a DEVIATION even if the
numbers are right) and file the verdict via `record-verification --type intent-check`
(HONORED | HONORED-WITH-NOTES | DEVIATION).

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
`human-review`, `intent-check`. **When you (Claude) run a verify/red-team agent over an
answer, file the outcome here** — an unfiled verification is invisible to the audit
surface. Consoles render these with verdict chips next to the machine checks.

`--verdict` is free text, but use the established vocabulary so verdicts aggregate
across editions: `CONFIRMED` | `CONFIRMED-WITH-CAVEAT` | `REFUTED` (adversarial
re-derivation); `ACTIONED` (a prior finding has been addressed by a re-answer);
`HONORED` | `HONORED-WITH-NOTES` | `DEVIATION` (intent-check vs the plan). Each filed
entry is stamped with the short sha256 of the edition's report.md **at filing time** —
the verdict is tied to the byte-state it judged, so a later regeneration is detectable
by comparing the stamp against the current report.

### `code-audit <BQ-NN | --path P | --all>`
Run the DETERMINISTIC code-quality checks over the target's code artifacts and upsert
the store (`code-quality/records.yml`), keyed by each file's current sha256:

- **static lint** — `pyflakes` when importable, else a `py_compile` syntax check; the
  tool used is recorded.
- **poison-pattern scan** — regex rules with line numbers: clocks
  (`datetime.now` / `date.today` / `time.time` — answers must anchor on pinned data,
  never "today"), unseeded randomness (`random.Random()` with no seed, bare
  `random.random/choice/randint/...` calls — a file that seeds the global RNG is not
  flagged, so seeded generators pass), network imports
  (`requests` / `urllib` / `http.client` / `socket` — computations read pins only), and
  `open(` on absolute paths (heuristic, warning only).
- **determinism replay** (computation modules only; `n/a` for generators, which run at
  acquisition time) — the BQ's computation runs twice against the latest edition's
  pins into two temp dirs; `report.md` + `data.json` are byte-compared. A diff is a
  fail — there should be no timestamp fields to exclude.

Targets: a BQ id audits that question's artifacts (module + `computations.py` + dep
generators); `--path` audits one artifact; `--all` sweeps every implemented question.
Inline computations (no per-BQ module) attribute their determinism verdict to
`computations.py`, aggregated across the BQs it owns.

### `record-code-review <path> --verdict V --by B --summary S [--finding "sev|summary|disposition" ...] [--detail-ref R]`
File an **AI review as the review record** against the artifact's CURRENT sha
(creating the store entry if the deterministic checks haven't run yet — noted as
pending). Reviews target the failure classes the deterministic checks cannot see:
**plan conformance** (does the code compute what the analysis plan committed to),
**denominator/basis choices**, **string-literal facts** (including computed-sentence
logic — qualifiers like "worst region" must be computed, not narrated),
**median/rounding traps**, **status-set assumptions** (which status values count as
completed/failed), and **determinism** reasoning the replay can't reach. Findings are
structured (`severity|summary|disposition`); park the full dossier behind
`--detail-ref`.

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

**Terms & explainers — plain-language reader aids (catalog-authored, sidecar-rendered).**
Reports are written for analysts; consoles are read by regulators, executives, and
other non-analyst readers. The catalog carries the decoding layer:

```yaml
terms:                      # top-level dictionary — define each term ONCE
  "510(k)": "The standard FDA premarket route for most moderate-risk devices …"
  MAUDE: "FDA's public database of medical-device adverse-event reports …"

questions:
  - id: BQ-23
    # …
    terms: [MAUDE, "510(k)", {one-off-term: "Inline definition for a term used only here."}]
    explainers:
      question:             # reserved key — whole-answer "About this analysis"
        what: "What this analysis is, in plain words."
        why: "The decision a reader should connect it to."
      coverage-stat:        # a series id from the computation's data.json
        label: "Campaign coverage"        # optional display label
        what: "What this number is."
        why: "Why it matters."
        how_to_read: "Higher is better; compare against the 95% target."  # optional
      verdict:              # reserved key — decodes the verdict concept (gate, trigger)
        what: "…"
        why: "…"
```

- Per-question `terms:` is a **reference list** of keys into the top-level dictionary
  (define once, reference everywhere); an inline `{term: definition}` map entry is
  accepted for one-off terms. Definitions are 1–3 sentences, plain language, written
  for a reader who knows neither analytics nor FDA data-plumbing jargon.
- `explainers:` is keyed by **target id** — a series id from the question's data.json
  (a mis-keyed explainer renders nowhere: read the latest edition's data.json to get
  the ids right), or the reserved keys `question`, `verdict`, `expectations`. Each
  value: `{label?, what, why, how_to_read?}`.
- **Authoring rule — explainer and term text is TIMELESS.** It defines the metric or
  term and its significance; it must NEVER contain pin-dependent facts — no row
  counts, no date ranges, no current values. Those live in the marker-cited report,
  which is regenerated per edition; the explainer survives every re-answer unchanged.
  Style: short sentences, no acronym left undefined, and the "why" states the decision
  the reader should connect the number to.

**Recommended layout at scale — per-BQ modules.** A single `computations.py` works for
a handful of questions but becomes a merge bottleneck when many computations are
authored in parallel (e.g. by concurrent agents). The proven layout: keep shared
helpers + a dispatch table in `computations.py`, and give each question its own module
at `bq_modules/bq_nn.py` exposing `run(corpus_root, out, pins)`. The dispatcher falls
back to `importlib.import_module("bq_modules.bq_nn").run` when the BQ isn't in its
table — `bq_modules/` works as a namespace package, no `__init__.py` required. One
file per question means parallel authors never touch the same file.

**Reuse the shared helpers before re-implementing.** Statistical primitives (median,
percentile, rate calculations) belong in `computations.py` and get imported by every
module — two independently hand-rolled `sorted(vals)[n//2]` "medians" (wrong for even
n) is the canonical failure this prevents. If a helper doesn't exist yet, add it to
the shared file, don't inline it.

**No string-literal facts (a verified failure class).** A computation module may only
interpolate values it READ from a pin, a `params` entry, or a derivation it computed —
never a fact typed into the source as a string literal. A hardcoded record id, count,
or docket number is invisible to the lint (the surrounding line carries a marker) but
rots silently the moment the snapshot refreshes. This includes **sentence logic**:
qualifiers like "most favorable basis", "decays", or "worst region" are claims — they
must be computed from the data (compare the bases, test the bucket shape), not
narrated. And a cross-dataset id (e.g. a docket number matched against a complaints
record) requires that dataset in `corpus_deps` so the id is pinned, not assumed.

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

## Code quality — the soft-gate audit layer for project analysis code

The numbers are only as good as the code that computed them. This layer audits the
PROJECT-SIDE analysis code — per-BQ modules (`bq_modules/bq_nn.py`), the shared
`computations.py`, and corpus dataset generators (`gen.py`) — with **AI review as the
review record**. The engines themselves (this skill's and the corpus skill's scripts)
are out of scope: they are reviewed at registry level, not per project.

**Code pinning.** `answer` records `code_artifacts:` into `edition.yml` — `{path,
sha256}` for the question's module (when present), `computations.py` (always — shared
helpers and inline computations), and each corpus dep's generator (as
`corpus:<domain>/<dataset>/gen.py`). An edition therefore names the exact code bytes
that produced it, the same way it pins its data snapshots.

**The store** (`code-quality/records.yml`, engine-managed): per artifact path, a list
of entries keyed by sha256 — deterministic check results (`static_lint`,
`poison_scan`, `determinism`) written by `code-audit`, plus `reviews[]` filed by
`record-code-review` (`{verdict, by, date, summary, findings[], detail_ref}`). Newest
entry per sha wins; reviews stay attached to the exact bytes they judged.

**The badge surface.** `answer` / `lint` / `audit` write a `code:` block into
quality.json, and `render` mirrors it into the sidecar (schema 1.3): per pinned
artifact `{path, sha256_12, role: module|shared|generator, static_lint, poison_scan,
determinism, review: {verdict, by, date, current, findings, detail_ref} | null,
review_history: […]}` — `current` is true only when the review was filed against the
edition-pinned sha; `review_history` (schema 1.3, additive) carries the newest review
of each OTHER sha of the same path (newest first, cap 5, each flagged
`superseded: true`) so pre-fix findings remain on the audit surface. The
question-level `status` ladder (worst wins):

1. `checks-failed` — a pinned artifact has a failing deterministic check
2. `review-outdated` — the pinned sha lacks a review but an older sha of the same file
   has one (the code changed since it was last reviewed)
3. `unreviewed` — some pinned artifact has never been reviewed
4. `reviewed-current` — every pinned artifact has a review for its exact pinned bytes

**SOFT GATE — never blocks.** `approve` prints the code status but approves
regardless; `check` prints a one-line status count, never failing on it. The badges
create review pressure without making code review a deploy gate. Degradation is
graceful everywhere: no store file → `unreviewed` (no errors); editions predating
code pinning → status computed from current file hashes, with a note saying so.

**Review workflow (Claude-orchestrated).** After substantive computation changes, run
an independent review agent over the changed module(s) — give it the analysis plan +
the module + the shared helpers — and file the verdict via `record-code-review`. An
unfiled review is invisible to the audit surface, exactly like unfiled verifications.

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
