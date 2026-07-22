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
