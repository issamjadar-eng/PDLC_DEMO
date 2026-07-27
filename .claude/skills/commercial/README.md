# commercial — skill design notes

Business-question analysis engine: deterministic answer editions computed from
corpus-skill snapshots, claim lint, gated draft→approved→superseded lifecycle, and
console JSON sidecars. The middle tier of corpus (data) → commercial (answers) →
console (display).

## Why this exists

Answering business questions with an LLM invites two failure modes: invented numbers and
silently-stale answers presented as current. This skill makes both structurally hard:

1. **Computation is scripted, not generated.** Registered project-side scripts read
   pinned snapshots; the engine discards any edition where the script fails or doesn't
   produce both report.md and data.json.
2. **Claims are machine-checked.** The lint resolves every marker and rejects any
   numeric claim without one. Estimation language without a cited assumption record is
   flagged. Stale pins block unless a visible, unexpired waiver is cited.
3. **Approval is enforced, hash-pinned, and auditable.** approval.yml records approver,
   checks, and content hashes; `check` detects post-approval mutation.

## Design decisions

- **Engine in the skill, catalog + computations in the project.** The skill is
  project-agnostic (registry rule); which questions exist, their data dependencies, and
  their computation logic are project configuration under the commercial root.
- **Editions are date-keyed with same-day suffixing** (mirrors corpus snapshots).
  Drafts are mutable-by-regeneration; approved editions immutable.
- **Markers are inline and human-readable** (`[src: ds@snap]`) rather than a separate
  citation database — the report stays a plain markdown document whose substantiation is
  visible to a reader and checkable by a script.
- **Worst-of evidence class** rolls up to the sidecar (assumed < derived < measured) so
  a dashboard badge can't overstate an answer's grounding.
- **Adversarial verification is an agent-tier control**, recorded via `--verify-note` in
  approval.yml — the engine gates on deterministic checks; independent re-derivation is
  orchestrated by Claude per SKILL.md (spawn a subagent with pins only, not the report).
- **`check` chains to corpus `check`** so one command asserts the whole grounding chain.

## v1 scope notes

- The lint verifies marker *resolution*, not value *recomputation* — report and
  data.json are emitted by the same deterministic script from the same pins, so
  consistency is by construction; independent value re-derivation is the verify agent's
  job. A future `lint --recompute` could re-run the computation and diff.
- Line-level numeric rule exempts headings and identifier tokens (BQ/A/W ids, ISO dates,
  device serials, K-numbers); table dividers are skipped.

## Dependencies

- `corpus` skill (required): answers pin and cite corpus snapshots; lint resolves
  markers against the corpus tree.
- Python 3.9+, PyYAML.

## Best Practices

<!-- Consumed by /best-practices audit -->

| Check | How to Verify | Severity | Scope |
|-------|--------------|----------|-------|
| Skill has SKILL.md | File exists at skill root | Required | shared |
| Frontmatter complete | name, description, version, updated all present | Required | shared |
| README.md exists | Design doc at skill root | Required | shared |
| Changelog current | Latest entry matches version number | Required | shared |
| Commercial check green | `python3 scripts/commercial.py check` exits 0 in consuming project | Recommended | local |
| No hand-edited approved editions | `check` reports no post-approval hash mismatches | Required | local |
| Sidecar current | `.console/commercial-index.json` regenerated after newest edition | Recommended | local |

## Changelog

- 11 (2026-07-27): Code-quality audit layer for project-side analysis code (soft gate —
  badges, never blocks; AI review is the review record; engines out of scope, reviewed
  at registry level). `answer` pins `code_artifacts:` (path + sha256 of the per-BQ
  module, `computations.py`, and dep generators as `corpus:<ds>/gen.py`) into
  edition.yml. New engine-managed store `code-quality/records.yml`: per-artifact
  entries keyed by sha with deterministic check results + filed reviews (newest entry
  per sha wins). New `code-audit <BQ|--path|--all>` action — static lint (pyflakes,
  py_compile fallback), poison-pattern scan with line numbers (clocks, unseeded
  randomness — seeded generator usage passes, network imports, absolute-path `open`
  warning), determinism replay (double-run byte-compare of report.md+data.json against
  latest-edition pins; `n/a` for generators; inline BQs aggregate onto
  computations.py). New `record-code-review <path>` action files structured AI-review
  verdicts (`--finding "sev|summary|disposition"`) against the file's current sha.
  quality.json + sidecar gain a per-question `code:` block (schema_version 1.2,
  additive): per pinned artifact checks + newest review with `current` sha-match flag;
  question status ladder checks-failed > review-outdated > unreviewed >
  reviewed-current. `approve` prints the code status (never blocks); `check` adds a
  non-fatal status count line. Graceful degradation: missing store → unreviewed;
  pre-pinning editions → status from current file hashes with a note.
- 10 (2026-07-27): Plain-language reader aids for non-analyst console readers. Catalog
  schema: top-level `terms:` dictionary (term -> 1-3 sentence plain-language
  definition, defined once) + per-question `terms:` reference lists (string keys into
  the dictionary; inline `{term: definition}` accepted for one-offs) + per-question
  `explainers:` maps keyed by data.json series id or the reserved keys
  question / verdict / expectations, each `{label?, what, why, how_to_read?}`.
  Engine `render`: sidecar `schema_version` 1.0 -> 1.1; each question row gains
  `explainers` (verbatim) and `terms` (resolved; unresolved key = stderr warning +
  skip, never fabricated) — purely additive, 1.0 consumers ignore the new fields.
  SKILL.md documents the schema and the timeless-authoring rule (explainer/term text
  defines the metric and its significance; never pin-dependent facts). Template gains
  a commented example of both blocks.
- 9 (2026-07-27): Battle-test hardening. Engine: (bug fix) same-day draft replacement
  now carries filed `verifications` records forward from the replaced draft's
  quality.json (each stamped `carried_from_replaced_draft: true`) — previously they
  were silently dropped despite the preservation promise; project-extensible lint via
  a commercial.yml `lint:` block (`exempt_patterns` regexes extend the numeric-claim
  exempt tokens, `estimation_exempt_terms` words are skipped by the
  estimation-language check — relax-only); built-in exempt tokens extended with
  `E-N(.N)`, `FYNNNN`, `YYYY-Q[1-4]`, `YYYY-H[12]`, `510(k)`; `record-verification`
  stamps the short sha256 of report.md into each entry (verdict tied to the byte-state
  it judged); series hygiene accepts multi-dataset provenance
  `{datasets: [{dataset, snapshot}, ...]}` for join-heavy series (validated:
  non-empty, each entry needs dataset + snapshot). SKILL.md: documented the per-BQ
  module layout (`bq_modules/bq_nn.py` with `run(corpus_root, out, pins)`), the
  line-based marker rule + estimation word list + lint config, corpus-wide `[assume:]`
  resolution caveat, snapshot-id-as-as-of convention, the no-string-literal-facts
  rule (incl. computed sentence logic), same-day edition semantics + verification
  carry, the verdict vocabulary + hash stamping, newest-edition sidecar-card
  rationale, and shared-helper reuse.
- 8 (2026-07-22): Analysis plans (Option A — prose contract, machine drift-detection,
  agent intent-verification): `plan-init` scaffolds a user-owned `plans/BQ-NN.md`
  (goal / approach with committed definitions / data have-vs-need / assumptions /
  assertions & limits; category-specific approach hints; never overwritten); `answer`
  pins the plan's hash into the edition; new `plan-currency` lint check calls out
  missing / unpinned / drifted plans (warnings — plans are living docs); quality.json
  gains a `plan` block; `record-verification` gains type `intent-check` for agent
  verdicts on whether the answer honors the plan (HONORED / HONORED-WITH-NOTES /
  DEVIATION — strict: an unfollowed committed definition is a deviation even with
  correct numbers).
- 7 (2026-07-22): Lint itemized into named checks (artifacts / numeric-coverage /
  marker-resolution / estimation-language / pin-freshness / series-hygiene /
  derivation-chain), each with status + findings in quality.json. New
  `derivation-chain` check: derived series must declare {method, inputs[]} — the data
  chain is stated, not implied. quality.json gains `data_availability` (have / via
  stated assumption / missing, derived from the edition's series). `check`
  grandfathers post-approval lint rules for immutable approved editions.
- 6 (2026-07-22): Per-edition `quality.json` audit surface — lint status, resolved-
  reference inventory (every marker with resolved/broken + note), per-pin freshness
  detail; written by answer/lint/approve, refreshable via the new `audit` action.
  New `record-verification` action files agent-produced verdicts (adversarial-verify /
  red-team / reference-audit / human-review) into the same file, preserved across
  machine rewrites. `lint_edition` now returns (errors, warnings, detail).
- 5 (2026-07-22): Report-table citation convention — markers ride inline at the end of
  the row's label cell (consoles render them as compact superscripts), never in a
  dedicated Evidence column (guidance added to SKILL.md; the claim lint is line-based
  so one marker per row still satisfies it).
- 4 (2026-07-22): Edition recency is creation-time, not name — suffix allocation is
  max+1 (never reuses a freed suffix, which made lexicographic order lie about
  newest), `list_editions` sorts by `created_at`, default edition resolution returns
  the newest edition regardless of status, and the sidecar row gains
  `latest_edition` (cards' verdict/badges now reflect the newest edition).
- 3 (2026-07-22): Form-selection guidance in SKILL.md — the diagram follows the data's
  job (stat = headline number; default bars = magnitude; paired-bars = plan vs actual;
  timeseries = change over time; kv = non-numeric; unavailable = stated gap), with the
  every-answer-should-carry-a-history rule (a missing historical view must say why).
  New series kinds in the contract: `stat` (points w/ label/value/sub) and
  `paired-bars` (`pairs` labels + `{label, a, b}` points).
- 2 (2026-07-22): Plan expectations as first-class records — per-question `expectations:`
  in the catalog (statement / expected / basis / set_by / `validated:` flag for
  stand-ins), evaluated every edition into `data.json.expectations[]` with
  met | at-risk | not-met | not-evaluable verdicts. data.json extensions:
  `narrative {issues/risks/watch}` (deterministic Risks/Mitigations/Issues from
  computed facts, mirrored into the linted report) and `kind: timeseries` series
  (`lines[]` of dated points, zero-filled) for trend charts.
- 1 (2026-07-22): Initial version — answer/lint/approve/render/check/catalog; edition
  lifecycle (draft/approved/superseded) with same-day suffixing; claim lint (marker
  resolution, numeric-claim rule, estimation-language rule, pin freshness with waivers,
  data.json evidence-class hygiene); hash-pinned approvals; console sidecar
  (schema_version 1.0); check chains to corpus check.
