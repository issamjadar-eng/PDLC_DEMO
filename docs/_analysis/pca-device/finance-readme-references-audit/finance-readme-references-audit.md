---
audit_id: RA-finance-readme-001
source_doc: docs/project/finance/README.md
created: 2026-09-08
status: Findings Posted
schema_version: 1
---

# References Audit — Finance — business-question answers

**Source doc:** [`docs/project/finance/README.md`](../../../../docs/project/finance/README.md)
**Audit ID:** `RA-finance-readme-001`
**Created:** `2026-09-08`
**Status:** `Findings Posted`

This audit verifies that every citation in the source document actually resolves to a real source and that the source supports the cited claim. Findings carry a verdict band (`sound | unverified | broken`) and a finding kind (open enum). External-formal references are verified against both the medtech-docs registry distillation (L1a) and the project applicability layer (L1b) per the "cite both" mandate. See the `reference-audit` skill SKILL.md for the engine contract; see the `citations` advisor for the verdict semantics.

## Summary

| Class | sound | unverified | broken | Total |
|-------|------:|-----------:|-------:|------:|
| external-formal | 0 | 0 | 0 | 0 |
| internal-formal | 12 | 1 | 1 | 14 |
| informal-link | 4 | 0 | 0 | 4 |
| **Total** | **16** | **1** | **1** | **18** |

_Verified 2026-09-08 by the `citations` advisor (batch fan-out, task 118). All 18 verdicts are researcher verdicts (14 internal, 4 informal); three dispatches were re-run after hitting the concurrent-subagent cap — no direct verification by the engine._

## References (Pending Verification)

_All 18 entries dispositioned on 2026-09-08 — retained as the extraction inventory; verdicts are in the Findings sections below._

```yaml
references:
  - {id: I1, class: internal-formal, method: regex, target: "docs/project/finance/finance.yml", anchor: "Intro L6; Structure row 1", claim: "The finance question catalog lives in finance.yml and holds 10 questions FQ-01..FQ-10 with a `domain:` identity block, lint extensions, terms dictionary and categories; implemented questions carry corpus deps + computation + params + expectations."}
  - {id: I2, class: internal-formal, method: regex, target: "docs/project/finance/computations.py", anchor: "Structure row 2", claim: "computations.py is the domain-local shared helper layer (pin loading, expectations, narrative/report rendering, dispatch) with no question-specific code."}
  - {id: I3, class: internal-formal, method: regex, target: "docs/project/finance/bq_modules/fq_nn.py (fq_01, fq_03, fq_06, fq_08)", anchor: "Structure row 3; Changelog", claim: "One deterministic computation module exists per implemented question (FQ-01, FQ-03, FQ-06, FQ-08), each exposing `run(corpus_root, out, pins)`."}
  - {id: I4, class: internal-formal, method: regex, target: "docs/project/finance/plans/FQ-NN.md + plans/README.md", anchor: "Structure row 4", claim: "User-owned analysis plans exist for all 10 questions and the plans folder has its own README describing the committed-definition + verification-gate checklist convention."}
  - {id: I5, class: internal-formal, method: regex, target: "docs/project/finance/reports/FQ-NN/<edition>/ {report.md, data.json, pins.json, edition.yml, quality.json, approval.yml}", anchor: "Structure row 5", claim: "Each answer edition folder carries report.md, data.json, pins.json, edition.yml, quality.json and approval.yml."}
  - {id: I6, class: internal-formal, method: regex, target: "docs/project/finance/code-quality/ (records.yml + README.md)", anchor: "Structure row 6", claim: "The code-quality store holds records.yml with deterministic check results + AI code reviews per artifact sha (soft gate) and has its own README."}
  - {id: I7, class: internal-formal, method: regex, target: "docs/project/finance/.console/finance-index.json", anchor: "Structure row 7", claim: "The console sidecar exists at .console/finance-index.json with schema 1.5 and a `domain` block."}
  - {id: I8, class: internal-formal, method: regex, target: "docs/project/corpus/finance/* and docs/project/corpus/commercial/*", anchor: "Intro L7-8", claim: "Computation modules read pinned corpus snapshots under corpus/finance/* and, cross-domain, corpus/commercial/*."}
  - {id: I9, class: internal-formal, method: regex, target: "docs/project/corpus/commercial/{internal-financials,internal-fleet,internal-complaints}", anchor: "Conventions — Cross-domain pins", claim: "Finance questions cite the commercial/internal-financials, internal-fleet and internal-complaints datasets alongside finance/* datasets; each dataset declares its own max_age_days."}
  - {id: I10, class: internal-formal, method: llm, target: "docs/project/corpus/finance/internal-ar-inventory/README.md", anchor: "Conventions — Ratios aggregate", claim: "The internal-ar-inventory README declares the convention that ratios aggregate by implied daily flow (DSO = Σ AR ÷ Σ (AR ÷ DSO); inventory days likewise), never by averaging ratios."}
  - {id: I11, class: internal-formal, method: llm, target: "docs/project/finance/finance.yml (params / expectations)", anchor: "Conventions — Plan constants", claim: "Plan constants live in `params`, are cited as `[config: finance.yml]`, and stand-in constants carry `validated: false` with a `[VERIFY]` basis."}
  - {id: I12, class: internal-formal, method: llm, target: "docs/project/finance/finance.yml + .console/finance-index.json (not-implemented status)", anchor: "Conventions — Unimplemented questions", claim: "Unimplemented questions remain visible in the catalog and sidecar with status `not-implemented`."}
  - {id: I13, class: internal-formal, method: llm, target: "docs/project/finance/reports/*/*/report.md (demo banner)", anchor: "Scope paragraph L14-15", claim: "Every current answer edition carries the `_Demo sample data — not for clinical use._` banner."}
  - {id: I14, class: internal-formal, method: llm, target: "docs/project/commercial/", anchor: "Intro L4-5", claim: "Finance uses the same three-tier stack as the existing commercial domain (corpus → answers → console)."}
  - {id: L1, class: informal-link, method: llm, target: ".claude/skills/commercial/SKILL.md § Domains", anchor: "Intro L3-4", claim: "The commercial skill's SKILL.md has a \"Domains\" section describing the one-engine-N-roots model, of which Finance is the second domain."}
  - {id: L2, class: informal-link, method: regex, target: ".claude/skills/commercial/scripts/commercial.py --domain finance {answer|lint|approve|render|check|catalog|plan-init|code-audit}", anchor: "Conventions L31-33", claim: "commercial.py exists, accepts a `--domain` flag, and exposes the subcommands answer, lint, approve, render, check, catalog, plan-init and code-audit."}
  - {id: L3, class: informal-link, method: llm, target: "commercial.py approve --by <name> --verify-note; check tamper detection", anchor: "Conventions — Lifecycle / Never hand-edit", claim: "`approve` takes `--by <name>` and `--verify-note`; `check` treats post-approval mutation of a hash-pinned edition as tampering; lifecycle is draft → approved → superseded."}
  - {id: L4, class: informal-link, method: llm, target: "[src: dataset@snapshot] / [assume: A-NNN] / [derived: id] / [config: finance.yml] marker grammar", anchor: "Intro L9-11", claim: "Every figure in report.md / data.json carries one of the four machine-resolvable markers, as defined by the commercial skill's claim-lint grammar."}
```

## Findings (broken)

### I5 — `reports/FQ-NN/<edition>/` file list · `stale-citation`
- **Claim:** each answer edition folder carries report.md, data.json, pins.json, edition.yml, quality.json **and approval.yml** (Structure row 5).
- **Evidence:** `docs/project/finance/reports/` holds four editions (FQ-01/03/06/08 @ 2026-09-08), each with report.md, data.json, pins.json, edition.yml, quality.json — `approval.yml` is absent in all four; every `edition.yml` L3 reads `status: draft`. `.claude/skills/commercial/SKILL.md` L63: `approval.yml  # who/when/checks/content-hashes (written by approve)` — the file exists only once an edition is approved.
- **Suggested fix:** reword README L25 to make the file conditional — `report.md, data.json, pins.json, edition.yml, quality.json; approval.yml once approved`.

## Findings (unverified)

### I12 — `not-implemented` in catalog **and** sidecar · `ambiguous-source`
- **Claim:** unimplemented questions stay visible in the catalog and sidecar as `not-implemented` (Conventions L49-50).
- **Evidence:** sidecar half verified — `.console/finance-index.json` carries all 10 questions and FQ-02/04/05/07/09/10 each have `"status": "not-implemented"` (L249, L534, L573, L818, L1042, L1077). Catalog half is not literal — `finance.yml` has no `status:` key anywhere; the six roadmap entries exist (L173, L263, L277, L367, L439, L452) and are distinguished only by a missing `computation:` key (L3 comment: `Questions without \`computation\` render as not-implemented`).
- **Suggested fix:** tighten README L49-50 to `stay listed in the catalog (no \`computation\`) and carried in the sidecar with \`status: not-implemented\``; or accept as-is if "as not-implemented" is read as the rendered status rather than a catalog field.

## Findings (sound)

- **I1** `finance.yml` — `domain:` block L5-10, `lint:` L17, `terms:` L36, `categories:` L103, exactly 10 `id: FQ-` entries (L111-L452); FQ-01/03/06/08 carry corpus_deps + computation + params + expectations.
- **I2** `computations.py` — L11-13 docstring "domain-local SHARED HELPER LAYER only … keep question-specific code out"; name-based `module_dispatch` L173; no per-question logic found.
- **I3** `bq_modules/` — exactly fq_01/03/06/08.py, each `def run(corpus_root, out, pins):` (L37/L31/L26/L35).
- **I4** `plans/` — FQ-01..FQ-10.md + README.md; README L15-32 describes committed definitions + verification-plan checklist + hash pinning into `edition.yml`.
- **I6** `code-quality/records.yml` — 13 sha256-keyed entries with static_lint / poison_scan / determinism + `reviews: []`; README L3 "soft gate", L14 filed via `record-code-review`.
- **I7** `.console/finance-index.json` — L2 `"schema_version": "1.5"`, L4-11 `domain` block (`key: finance`, `id_prefix: FQ`).
- **I8** corpus roots — `fq_01.py` L15-16 reads `commercial/internal-financials` and `finance/internal-standard-costs`; FQ-01 pins.json pins both.
- **I9** cross-domain pins — `finance.yml` corpus_deps L116/L193/L282/L372/L444 cite the three commercial datasets; every cited dataset.yml declares `max_age_days` (90/7/7; finance 30/30/30/90).
- **I10** `internal-ar-inventory/README.md` L15-17 — "DSO over any slice = Σ AR ÷ Σ (AR ÷ dso_days); inventory days = Σ inventory ÷ Σ (inventory ÷ inventory_days)" (README says "ratios do not sum"; citing prose paraphrases as "never by averaging ratios" — equivalent).
- **I11** `finance.yml` L123 `params:`; all 9 `validated: false` expectations carry a `[VERIFY]` basis (e.g. L128-130); FQ-01 report L9/L55 cite `[config: finance.yml]`.
- **I13** demo banner — 4/4 report.md L3 `_Demo sample data — not for clinical use._`.
- **I14** `docs/project/commercial/README.md` L3-4 states the same corpus → answers → console stack; `corpus/README.md` L14/L16 list both domain roots.
- **L1** `commercial/SKILL.md` L68 `## Domains — one engine, N roots`; L70-77 `--domain <slug>` / `<domain>.yml (e.g. finance.yml)`. Note: SKILL.md does not rank Finance as "second" — that ordinal is the README's own framing.
- **L2** `commercial.py` L1584 `--domain`; add_parser answer L1589, lint L1593, approve L1598, render L1605, check L1608, code-audit L1627, plan-init L1644, catalog L1648 — all 8 present.
- **L3** `commercial.py` L1598-1601 `--by` (required) + `--verify-note`; L1142-1155 `cmd_check` hash-mismatch → "MUTATED after approval?"; lifecycle draft → approved → superseded (L6, L932, L1009, L1022).
- **L4** `commercial.py` L48 `MARKER_RE` = `[(src|assume|derived|config|waived): …]`; L740-745 numeric-coverage lint; all four quality.json lint `pass`. (Grammar also has a fifth `waived` marker the README does not list — not a defect, the README lists the four that appear in figures.)

## Open Resolutions

_Surfaced by the audit but requiring SME adjudication or project decision — not a defect in the citation itself but an action it points at._

- **I5 / I12 are wording fixes**, not structural defects — the engine behaves as the README intends; the README over-specifies (approval.yml on drafts) or under-specifies (how the catalog expresses "not-implemented"). Apply the two rewordings when the README is next touched (task 118 owner).

## Provenance

- Extraction method: regex pass over the source doc + LLM pass over narrative prose with regex-extracted spans masked (D-202.12).
- Verdict bands: three-band — `sound | unverified | broken` (D-202.13).
- External-formal references verified by two-tier L1a + L1b consolidation (D-202.14).
- Finding `kind` enum is open — v1.1 emits the link-checking subset plus `registry-gap`; v2 candidate kinds reserved per the skill's SKILL.md roadmap section.
- Doc-slug qualified with the parent folder (`finance-readme`) — inference; SKILL.md `init` step 2 is silent on basename collisions across sibling `README.md` sources.
