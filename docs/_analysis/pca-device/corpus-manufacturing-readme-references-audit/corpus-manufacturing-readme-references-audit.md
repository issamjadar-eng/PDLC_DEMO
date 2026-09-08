---
audit_id: RA-corpus-manufacturing-readme-001
source_doc: docs/project/corpus/manufacturing/README.md
created: 2026-09-08
status: Findings Posted
schema_version: 1
---

# References Audit — Corpus domain — `manufacturing/`

**Source doc:** [`docs/project/corpus/manufacturing/README.md`](../../../../docs/project/corpus/manufacturing/README.md)
**Audit ID:** `RA-corpus-manufacturing-readme-001`
**Created:** `2026-09-08`
**Status:** `Findings Posted`

This audit verifies that every citation in the source document actually resolves to a real source and that the source supports the cited claim. Findings carry a verdict band (`sound | unverified | broken`) and a finding kind (open enum). External-formal references are verified against both the medtech-docs registry distillation (L1a) and the project applicability layer (L1b) per the "cite both" mandate. See the `reference-audit` skill SKILL.md for the engine contract; see the `citations` advisor for the verdict semantics.

## Summary

| Class | sound | unverified | broken | Total |
|-------|------:|-----------:|-------:|------:|
| external-formal | 0 | 0 | 0 | 0 |
| internal-formal | 8 | 1 | 1 | 10 |
| informal-link | 2 | 0 | 0 | 2 |
| **Total** | **10** | **1** | **1** | **12** |

_Verified 2026-09-08 by the `citations` advisor (batch fan-out, task 118). All 12 verdicts are researcher verdicts (10 internal, 2 informal); five dispatches were re-run after hitting the concurrent-subagent cap — no direct verification by the engine._

## References (Pending Verification)

_All 12 entries dispositioned on 2026-09-08 — retained as the extraction inventory; verdicts are in the Findings sections below._

```yaml
references:
  - {id: I1, class: internal-formal, method: regex, target: "docs/project/manufacturing/", anchor: "Intro L5-6", claim: "The Manufacturing business domain that consumes these datasets lives at docs/project/manufacturing/ and is answered by the commercial-skill engine with --domain manufacturing."}
  - {id: I2, class: internal-formal, method: regex, target: "docs/project/corpus/manufacturing/{internal-production-lots,internal-ncr-capa,internal-suppliers,internal-process-validation}/", anchor: "Structure table", claim: "Four datasets exist with the stated content (production lots 2025-01..2026-08; NCR/CAPA register; approved-supplier register × monthly incoming inspection; validation + calibration register), each with its own README."}
  - {id: I3, class: internal-formal, method: regex, target: "<dataset>/dataset.yml `internal: true`, `asserts.enums`, `max_age_days`", anchor: "Intro L7; Conventions L41-44", claim: "Each dataset.yml declares `internal: true`, pins closed vocabularies via `asserts.enums`, and declares `max_age_days`."}
  - {id: I4, class: internal-formal, method: regex, target: "<dataset>/gen.py (seed 42, `gen` + `normalize` subcommands, no clocks, data through 2026-08-31)", anchor: "Intro L7-8; Expected Content; Conventions L34-36", claim: "Each dataset has a seeded (42) deterministic gen.py with `gen` and `normalize` subcommands that carries no clocks and stamps the demo banner into the raw export."}
  - {id: I5, class: internal-formal, method: regex, target: "<dataset>/snapshots/YYYY-MM-DD/ provenance `as_of` = data_through 2026-08-31", anchor: "Conventions L34-36; Expected Content", claim: "Each snapshot's provenance records `as_of: 2026-08-31` (the generator's literal `data_through`) and snapshots are engine-written and immutable."}
  - {id: I6, class: internal-formal, method: regex, target: "<dataset>/assumptions/A-NNN.yml, <dataset>/waivers/W-NNN.yml", anchor: "Expected Content", claim: "Assumption and waiver records live under each dataset's assumptions/ and waivers/ folders and are scaffolded via corpus.py `assume` / `waive`."}
  - {id: I7, class: internal-formal, method: llm, target: "docs/project/manufacturing/manufacturing.yml corpus_deps (MQ-01 & MQ-08 ← production-lots; MQ-03 ← ncr-capa; MQ-05 ← suppliers; MQ-08 ← process-validation; roadmap MQ-02/04/07/09, MQ-06, MQ-10)", anchor: "Structure table Consumed-by notes", claim: "The catalog's corpus_deps match the Structure table: MQ-01 and MQ-08 read internal-production-lots, MQ-03 reads internal-ncr-capa, MQ-05 reads internal-suppliers, MQ-08 reads internal-process-validation, with the stated roadmap consumers."}
  - {id: I8, class: internal-formal, method: regex, target: "project.yml portfolio {IP5000, PP3000, PP3500, SP6000, SP6500}", anchor: "Conventions L37-38", claim: "The five product_line values are exactly the device portfolio listed in project.yml."}
  - {id: I9, class: internal-formal, method: llm, target: "docs/project/corpus/commercial/internal-fleet (hw_rev letters; PP3500 A/B fielded, C = 2026 revision)", anchor: "Conventions L38-40", claim: "hw_rev reuses commercial/internal-fleet's letter scheme, where PP3500 A/B are in the field and C is the 2026 revision in production."}
  - {id: I10, class: internal-formal, method: llm, target: "<dataset>/README.md narrative-knob lists", anchor: "Conventions L41-42", claim: "Each dataset README documents the narrative knobs as an honest list (modeled, not observed)."}
  - {id: L1, class: informal-link, method: regex, target: ".claude/skills/corpus/scripts/corpus.py {init|acquire|refresh|validate|diff|check|list|assume|waive} manufacturing/<dataset>", anchor: "Conventions L31-32", claim: "corpus.py exposes the subcommands init, acquire, refresh, validate, diff, check, list, assume and waive, taking a <domain>/<dataset> argument."}
  - {id: L2, class: informal-link, method: llm, target: "corpus.py check freshness behaviour (fails on stale data without an unexpired waiver)", anchor: "Conventions L43-44", claim: "`check` fails when a dataset is older than its `max_age_days` unless an unexpired waiver exists."}
```

## Findings (broken)

### I7 — Structure table "Consumed by" vs `manufacturing.yml` corpus_deps · `stale-citation`
- **Claim:** README L16 — `internal-production-lots/` consumed by MQ-01, MQ-08; roadmap MQ-02/04/07/09.
- **Evidence:** `docs/project/manufacturing/manufacturing.yml` corpus_deps: MQ-01 L119, MQ-02 L174, MQ-04 L247, MQ-07 L326, MQ-08 L335, MQ-09 L395 **and MQ-10 L403** all include `manufacturing/internal-production-lots`. Rows L17-19 (ncr-capa → MQ-03; suppliers → MQ-05, roadmap MQ-06; process-validation → MQ-08, roadmap MQ-10) match the catalog exactly. The production-lots row omits MQ-10.
- **Suggested fix:** README L16 — change `roadmap MQ-02/04/07/09` to `roadmap MQ-02/04/07/09/10` (or drop `internal-production-lots` from MQ-10's corpus_deps at L403 if the README is the intended truth).

## Findings (unverified)

### I9 — `hw_rev` letters attributed to `commercial/internal-fleet` · `ambiguous-source`
- **Claim:** README L38-40 — `hw_rev` reuses `commercial/internal-fleet`'s letters "(PP3500 A/B in the field, C = the 2026 revision in production; `-` where a line has no tracked hw rev)".
- **Evidence:** `internal-fleet/gen.py` L21-22 emits only `A`/`B` for PP3500 and `-` for PP3000; `internal-fleet/README.md` and `dataset.yml` (L26, no enum) never mention rev C, a 2026 revision, or "in production". The rev-C statement is defined in the **manufacturing** corpus — `internal-production-lots/gen.py` L7-9 and L41-43 (`REV_C_SHARE` ramp 2026-03..2026-08), `dataset.yml` L42 `hw_rev: ["A","B","C","-"]`. The A/B/`-` half of the citation resolves; the C half does not resolve to the cited source.
- **Suggested fix:** reword L38-40 to attribute only the A/B/`-` scheme to `commercial/internal-fleet` and state that "C = the 2026 revision in production" is a manufacturing-corpus extension (defined in `internal-production-lots/gen.py`); or add the rev-C statement to `internal-fleet/README.md` so the citation resolves as written.

## Findings (sound)

- **I1** `docs/project/manufacturing/` exists (README L3-5, `manufacturing.yml` L1-10 `domain.name: Manufacturing`, `id_prefix: MQ`); `commercial.py` L1584-1585 `--domain`, L111-120 resolves `docs/project/manufacturing/manufacturing.yml`; `commercial/SKILL.md` L76/L81/L85.
- **I2** exactly four dataset folders, each with README.md, dataset.yml, gen.py (+ check_knobs.py, latest); dataset.yml descriptions L4-7 match the table's content lists (production-lots 672 rows 2025-01..2026-08; ncr-capa 286 records; suppliers supplier × month; process-validation IQ/OQ/PQ + calibration + PM, type enum L38).
- **I3** all four dataset.yml: `internal: true` (L10/L10/L10/L11), `max_age_days: 30`, `asserts: enums:` pinning product_line / hw_rev / site / status etc.
- **I4** all four gen.py: `BANNER`, `DATA_THROUGH = "2026-08-31"`, `gen` (`--seed default=42`) + `normalize` subparsers, `random.Random(a.seed)`, raw export carries `banner`/`seed`/`as_of`; no datetime/time clock calls in any of the four.
- **I5** all four `snapshots/2026-09-08/provenance.yml` L4 `as_of: '2026-08-31'`; dataset.yml `data_through: 2026-08-31`; `latest` = 2026-09-08; `corpus/SKILL.md` L47, L97-98, L122-124, L193-194 (immutability contract).
- **I6** all four datasets have `assumptions/` + `waivers/` dirs (currently empty → untracked in git; recreated by `corpus.py init` L440-441); `cmd_assume` L841-860 / `cmd_waive` L864-878 write `A-NNN.yml` / `W-NNN.yml`; SKILL.md L52-53, L165-166, L176-177.
- **I8** `project.yml` L9-14 `portfolio_context: [IP5000, PP3000, PP3500, SP6000, SP6500]` — exactly five; production-lots L41 and process-validation L39 enums identical. Note: ncr-capa L44 adds a `shared` sentinel for non-device records (not mentioned at README L37-38; not a mismatch with project.yml); the README's `project.yml` pointer names no key — the actual key is `project.portfolio_context`.
- **I10** all four dataset READMEs carry "**Narrative knobs seeded** (honest list — modeled, not observed; asserted by `check_knobs.py`)".
- **L1** `corpus.py` L887-936 registers exactly the nine subcommands claimed; `corpus/SKILL.md` L68-L180 documents each. Nuance: `check`/`list` take no dataset positional, `diff` needs `<dataset> <snapA> <snapB>`, `refresh`/`validate` treat the dataset as optional — the README's one-size usage line slightly over-generalises.
- **L2** `corpus.py` L653-655 `freshness_band` → `stale` when `age > max_age_days`; L661-669 `active_waiver` requires `status: active` and unexpired `expires`; L691-696 stale + no waiver → error; L728-732 exit 1. SKILL.md L24-26, L152-155. (Age is measured from the snapshot-id date, not `as_of`.)

## Open Resolutions

_Surfaced by the audit but requiring SME adjudication or project decision — not a defect in the citation itself but an action it points at._

- **I7** is a one-token table fix; **I9** is an attribution fix — both README-only, no engine change needed. Owner: task 118.
- **Informational:** (a) README L37-38 "the portfolio in `project.yml`" — consider naming the key (`project.portfolio_context`) so the pointer is greppable; (b) ncr-capa's extra `shared` product_line value could be mentioned in the shared-vocabulary bullet; (c) L31-32 usage line could carry "(dataset arg applies to dataset-scoped subcommands only)".

## Provenance

- Extraction method: regex pass over the source doc + LLM pass over narrative prose with regex-extracted spans masked (D-202.12).
- Verdict bands: three-band — `sound | unverified | broken` (D-202.13).
- External-formal references verified by two-tier L1a + L1b consolidation (D-202.14).
- Finding `kind` enum is open — v1.1 emits the link-checking subset plus `registry-gap`; v2 candidate kinds reserved per the skill's SKILL.md roadmap section.
- Doc-slug qualified with the parent folder (`corpus-manufacturing-readme`) — inference; SKILL.md `init` step 2 is silent on basename collisions across sibling `README.md` sources.
