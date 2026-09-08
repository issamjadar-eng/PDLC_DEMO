---
audit_id: RA-corpus-finance-readme-001
source_doc: docs/project/corpus/finance/README.md
created: 2026-09-08
status: Findings Posted
schema_version: 1
---

# References Audit — Corpus domain — `finance/`

**Source doc:** [`docs/project/corpus/finance/README.md`](../../../../docs/project/corpus/finance/README.md)
**Audit ID:** `RA-corpus-finance-readme-001`
**Created:** `2026-09-08`
**Status:** `Findings Posted`

This audit verifies that every citation in the source document actually resolves to a real source and that the source supports the cited claim. Findings carry a verdict band (`sound | unverified | broken`) and a finding kind (open enum). External-formal references are verified against both the medtech-docs registry distillation (L1a) and the project applicability layer (L1b) per the "cite both" mandate. See the `reference-audit` skill SKILL.md for the engine contract; see the `citations` advisor for the verdict semantics.

## Summary

| Class | sound | unverified | broken | Total |
|-------|------:|-----------:|-------:|------:|
| external-formal | 0 | 0 | 0 | 0 |
| internal-formal | 9 | 0 | 0 | 9 |
| informal-link | 2 | 0 | 0 | 2 |
| **Total** | **11** | **0** | **0** | **11** |

_Verified 2026-09-08 by the `citations` advisor (batch fan-out, task 118). All 11 verdicts are researcher verdicts (9 internal, 2 informal); six dispatches were relaunched after hitting the concurrent-subagent cap — no direct verification by the engine._

## References (Pending Verification)

_All 11 entries dispositioned on 2026-09-08 — retained as the extraction inventory; verdicts are in the Findings sections below._

```yaml
references:
  - {id: I1, class: internal-formal, method: regex, target: "docs/project/finance/", anchor: "Intro L5-6", claim: "The Finance business domain that consumes these datasets lives at docs/project/finance/ and is the second domain of the commercial-skill answer engine."}
  - {id: I2, class: internal-formal, method: regex, target: "docs/project/corpus/finance/{internal-standard-costs,internal-warranty-claims,internal-gl-budget,internal-ar-inventory}/", anchor: "Structure table", claim: "Four datasets exist with the stated grains (quarter × line × revenue type; per claim; month × function × cost center; month × region × channel × line), each with its own README."}
  - {id: I3, class: internal-formal, method: regex, target: "<dataset>/gen.py (seed 42, as-of 2026-08-31, banner-stamped JSON raw export, CSV normalize)", anchor: "Intro L7; Expected Content", claim: "Each dataset has a seeded deterministic gen.py (seed 42, no clocks, as-of 2026-08-31) that emits a banner-stamped JSON raw export and a CSV normalize."}
  - {id: I4, class: internal-formal, method: regex, target: "<dataset>/check_knobs.py on the corpus `asserts.command` seam", anchor: "Intro L9-11; Expected Content", claim: "Each dataset has a check_knobs.py wired into dataset.yml `asserts.command`, and the corpus engine executes `asserts.command` at acquire/validate so a narrative knob cannot drift silently."}
  - {id: I5, class: internal-formal, method: regex, target: "<dataset>/dataset.yml, snapshots/YYYY-MM-DD/, latest", anchor: "Expected Content", claim: "Each dataset has a hand-edited dataset.yml (acquisition / normalize / schema / asserts), engine-written immutable dated snapshots, and a `latest` pointer file."}
  - {id: I6, class: internal-formal, method: regex, target: "docs/project/corpus/commercial/{internal-financials,internal-fleet,internal-complaints}", anchor: "Intro L11-12", claim: "Finance questions also cite the commercial financials, fleet and complaints datasets under the shared corpus root."}
  - {id: I7, class: internal-formal, method: llm, target: "docs/project/finance/finance.yml corpus_deps (FQ-01/FQ-03/FQ-08/FQ-06; roadmap FQ-02/04/10/07)", anchor: "Structure table Consumers column", claim: "FQ-01 consumes internal-standard-costs, FQ-03 internal-warranty-claims, FQ-08 internal-gl-budget, FQ-06 internal-ar-inventory; roadmap consumers are FQ-02, FQ-04, FQ-10 and FQ-07 respectively."}
  - {id: I8, class: internal-formal, method: llm, target: "docs/project/corpus/commercial/internal-financials (FY2025 ~$80.5M revenue model) + internal-standard-costs/check_knobs.py", anchor: "Conventions — Coherence", claim: "Product lines, revenue types, unit prices and the FY2025 ~$80.5M revenue model are reused from commercial/internal-financials; copied blocks are marked \"keep in sync\"; the standard-costs knob check reads the financials snapshot directly and fails on divergence."}
  - {id: I9, class: internal-formal, method: llm, target: "<dataset>/README.md narrative-knob lists", anchor: "Intro L8-9", claim: "Each dataset README lists the generator's narrative knobs."}
  - {id: L1, class: informal-link, method: regex, target: ".claude/skills/corpus/scripts/corpus.py acquire finance/<dataset> [--dry-run]", anchor: "Conventions L33-35", claim: "corpus.py exists, has an `acquire` subcommand that takes a `<domain>/<dataset>` argument, and supports `--dry-run`."}
  - {id: L2, class: informal-link, method: llm, target: "demo banner stamped into raw export, never a CSV row", anchor: "Conventions L40-41", claim: "Every generator stamps the demo banner into its raw export and the banner never appears as a CSV row in the normalized output."}
```

## Findings (broken)

_None._

## Findings (unverified)

_None._

## Findings (sound)

- **I1** `docs/project/finance/` exists; its README L3-4 and `finance.yml` L1-2 both state "second domain of the one-engine/N-roots model"; `commercial/SKILL.md` L70-71 describes sibling-root domains.
- **I2** exactly four dataset folders, each with README.md, dataset.yml, gen.py, check_knobs.py, latest; grains confirmed in each README/dataset.yml (standard-costs "quarter × product line × revenue type" L5-6; warranty "per-claim" L5; gl-budget "period × 15 cost centers across six functions" L5-7; ar-inventory "period × region × channel × product line" L6).
- **I3** all four gen.py: `--seed default=42`, `random.Random(a.seed)`, literal `as_of 2026-08-31`, `json.dump({"banner": BANNER, …})` raw export, `csv.DictWriter` normalize; wall-clock grep = 0 hits in each.
- **I4** all four dataset.yml carry `asserts: … command: python3 check_knobs.py {normalized_dir}/records.csv`; `corpus.py` L373-374 `run_asserts` "re-run on every acquire AND every validate", L416-423 executes `asserts.command` and records non-zero exit as an error; wired into `_acquire` (L515, raises L533-534) and `_validate_snapshot` (L626, exit 1 at L646).
- **I5** every dataset.yml has `acquisition:` / `normalize:` / `schema:` / `asserts:`; each has `snapshots/2026-09-08/{raw/export.json, normalized/records.csv, provenance.yml}` and a `latest` file reading `2026-09-08`; `corpus/SKILL.md` L14-15, L47, L122-125 confirm immutability + engine-written pointer.
- **I6** the three commercial datasets resolve; `finance.yml` cites internal-financials (FQ-01/02/05/09), internal-fleet (FQ-03/04/07), internal-complaints (FQ-03).
- **I7** `finance.yml` corpus_deps + `computation:` presence match the table exactly: FQ-01→standard-costs (roadmap FQ-02), FQ-03→warranty-claims (FQ-04), FQ-06→ar-inventory (FQ-07), FQ-08→gl-budget (FQ-10); only four `computation:` lines exist (L117, L194, L297, L387). Informational: FQ-05 (L277/L282) is an additional roadmap consumer of gl-budget not listed at README L20 — the table does not claim exclusivity.
- **I8** `internal-financials/README.md` L14 "FY2025 totals ~$80.5M"; `internal-ar-inventory/gen.py` L8-9/L31 "copy — keep in sync" (L32-47 byte-identical to financials gen.py L22-37); `internal-standard-costs/gen.py` L42-44 identical `ASP_HW`/`ASP` constants; `internal-standard-costs/check_knobs.py` L15/L26-27 reads the financials `latest` snapshot and L51-53 exits 1 on divergence.
- **I9** all four dataset READMEs carry a "**Narrative knobs seeded** (honest list — modeled, not observed)" section, each corroborated by its check_knobs.py.
- **L1** `corpus.py` L893-898 `acquire` subparser with positional `dataset` and `--dry-run`; `corpus/SKILL.md` L121 `### acquire <domain>/<dataset> [--dry-run]`, L133-134.
- **L2** all four gen.py put the banner as a top-level JSON key and the CSV path writes only `["rows"]`; BANNER referenced nowhere else. (Verdict rests on generator code; the committed `records.csv` artifacts were not grepped — a cheap follow-up if wanted.)

## Open Resolutions

_Surfaced by the audit but requiring SME adjudication or project decision — not a defect in the citation itself but an action it points at._

- **Informational, no status impact:** (a) README L20 Consumers cell for `internal-gl-budget/` omits roadmap FQ-05 — consider `FQ-08 (roadmap FQ-05, FQ-10)`; (b) generator banners use an ASCII hyphen (`_Demo sample data - not for clinical use._`) where READMEs and reports use the em dash — harmless, but a grep for the canonical banner will miss the raw exports; (c) the literal "keep in sync" marker appears in `internal-ar-inventory/gen.py` and `internal-standard-costs/README.md` L42-43, while `internal-standard-costs/gen.py` L42 says "identical constants" — README L37-38 ("copied blocks are marked \"keep in sync\"") is true of the README/ar-inventory copies but not literally of that one generator comment.

## Provenance

- Extraction method: regex pass over the source doc + LLM pass over narrative prose with regex-extracted spans masked (D-202.12).
- Verdict bands: three-band — `sound | unverified | broken` (D-202.13).
- External-formal references verified by two-tier L1a + L1b consolidation (D-202.14).
- Finding `kind` enum is open — v1.1 emits the link-checking subset plus `registry-gap`; v2 candidate kinds reserved per the skill's SKILL.md roadmap section.
- Doc-slug qualified with the parent folder (`corpus-finance-readme`) — inference; SKILL.md `init` step 2 is silent on basename collisions across sibling `README.md` sources.
