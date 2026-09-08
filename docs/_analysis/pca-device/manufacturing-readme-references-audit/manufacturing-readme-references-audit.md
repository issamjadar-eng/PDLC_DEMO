---
audit_id: RA-manufacturing-readme-001
source_doc: docs/project/manufacturing/README.md
created: 2026-09-08
status: Findings Posted
schema_version: 1
---

# References Audit — Manufacturing — business-question answers

**Source doc:** [`docs/project/manufacturing/README.md`](../../../../docs/project/manufacturing/README.md)
**Audit ID:** `RA-manufacturing-readme-001`
**Created:** `2026-09-08`
**Status:** `Findings Posted`

This audit verifies that every citation in the source document actually resolves to a real source and that the source supports the cited claim. Findings carry a verdict band (`sound | unverified | broken`) and a finding kind (open enum). External-formal references are verified against both the medtech-docs registry distillation (L1a) and the project applicability layer (L1b) per the "cite both" mandate. See the `reference-audit` skill SKILL.md for the engine contract; see the `citations` advisor for the verdict semantics.

## Summary

| Class | sound | unverified | broken | Total |
|-------|------:|-----------:|-------:|------:|
| external-formal | 1 | 1 | 0 | 2 |
| internal-formal | 8 | 0 | 2 | 10 |
| informal-link | 4 | 0 | 0 | 4 |
| **Total** | **13** | **1** | **2** | **16** |

_Verified 2026-09-08 by the `citations` advisor (batch fan-out, task 118). All 16 verdicts are researcher verdicts (2 external, 10 internal, 4 informal); ten dispatches were re-run after hitting the concurrent-subagent cap — no direct verification by the engine._

## References (Pending Verification)

_All 16 entries dispositioned on 2026-09-08 — retained as the extraction inventory; verdicts are in the Findings sections below._

```yaml
references:
  - {id: E1, class: external-formal, method: regex, target: "21 CFR Part 820 (QMSR) — applicability analysis under docs/external/regulations/", anchor: "Conventions — Standards / regulation references L51-52", claim: "A QMSR (21 CFR Part 820) applicability analysis exists under docs/external/regulations/ and is the only distilled regulation source this domain relies on; the registry (L1a) also distills Part 820."}
  - {id: E2, class: external-formal, method: regex, target: "ISO 13485 (clause numbers)", anchor: "Conventions — Standards / regulation references L52-53", claim: "ISO 13485 clause numbers are NOT distilled in this project (neither L1a registry nor L1b docs/external/standards/), so every ISO 13485 clause mention in this domain is tagged [VERIFY]."}
  - {id: I1, class: internal-formal, method: regex, target: "docs/project/manufacturing/manufacturing.yml", anchor: "Intro L7; Structure row 1", claim: "manufacturing.yml is the 10-question catalog with a `domain:` identity block, `lint:` exemptions, `terms:`, `categories:`, and questions MQ-01..MQ-10 carrying personas, cadence, corpus deps, params, expectations and explainers."}
  - {id: I2, class: internal-formal, method: regex, target: "docs/project/manufacturing/computations.py (incl. snapshot_as_of)", anchor: "Structure row 2; Conventions — No clocks", claim: "computations.py is a domain-local copy of the shared helper layer (pin loading, as-of anchoring, expectations, narrative, dispatch) and exposes `snapshot_as_of` used to anchor aging math on the pinned snapshot's provenance `as_of`."}
  - {id: I3, class: internal-formal, method: regex, target: "docs/project/manufacturing/bq_modules/mq_nn.py (mq_01, mq_03, mq_05, mq_08)", anchor: "Structure row 3; Changelog", claim: "One deterministic computation module exists per implemented question (MQ-01, MQ-03, MQ-05, MQ-08), each exposing `run(corpus_root, out, pins)`."}
  - {id: I4, class: internal-formal, method: regex, target: "docs/project/manufacturing/plans/MQ-NN.md + plans/README.md", anchor: "Structure row 4", claim: "User-owned analysis plans exist for all ten questions and the plans folder has its own README."}
  - {id: I5, class: internal-formal, method: regex, target: "docs/project/manufacturing/reports/MQ-NN/<edition>/ {report.md, data.json, pins.json, edition.yml, quality.json, approval.yml}", anchor: "Structure row 5", claim: "Each answer edition folder carries report.md, data.json, pins.json, edition.yml (pinning plan + code artifacts), quality.json and approval.yml."}
  - {id: I6, class: internal-formal, method: regex, target: "docs/project/manufacturing/code-quality/ (records.yml + README.md)", anchor: "Structure row 6", claim: "The code-quality store holds records.yml and has its own README."}
  - {id: I7, class: internal-formal, method: regex, target: "docs/project/manufacturing/.console/manufacturing-index.json", anchor: "Structure row 7", claim: "The console sidecar exists with schema 1.5 and a `domain` block."}
  - {id: I8, class: internal-formal, method: regex, target: "docs/project/corpus/manufacturing/internal-*", anchor: "Intro L5; Demo banner L17-19", claim: "Every dataset this domain reads lives under corpus/manufacturing/internal-* and is demo-fabricated; the computations stamp the demo banner into each report."}
  - {id: I9, class: internal-formal, method: llm, target: "docs/project/manufacturing/manufacturing.yml (params / expectations validated: false)", anchor: "Conventions — Thresholds L47-50", claim: "Thresholds (yield floor, reject ceiling, effectiveness floor, due-soon window) are `params`, cited as `[config: manufacturing.yml]`, declared as `expectations` with `validated: false`, with every such basis carrying `[VERIFY]`."}
  - {id: I10, class: internal-formal, method: llm, target: "docs/project/manufacturing/manufacturing.yml + .console/manufacturing-index.json (not-implemented)", anchor: "Conventions — Unimplemented questions", claim: "Unimplemented questions remain visible in catalog and sidecar as `not-implemented`."}
  - {id: L1, class: informal-link, method: regex, target: ".claude/skills/commercial/scripts/commercial.py --domain manufacturing {answer|lint|approve|render|check|catalog|plan-init|code-audit|audit}", anchor: "Conventions L35-37", claim: "commercial.py accepts `--domain manufacturing` and exposes the subcommands answer, lint, approve, render, check, catalog, plan-init, code-audit and audit."}
  - {id: L2, class: informal-link, method: llm, target: "project console tab /domains/manufacturing", anchor: "Intro L6", claim: "The project console serves a Manufacturing tab at the route /domains/manufacturing (per the commercial skill's Domains model and the console's domain router)."}
  - {id: L3, class: informal-link, method: llm, target: "commercial.py approve --by <name> --verify-note; check tamper detection", anchor: "Conventions — Lifecycle / Never hand-edit", claim: "`approve` takes `--by <name>` and `--verify-note`; `check` treats post-approval mutation of a hash-pinned edition as tampering."}
  - {id: L4, class: informal-link, method: llm, target: "[src: dataset@snapshot] / [assume: A-NNN] / [derived: id] / [config: manufacturing.yml] marker grammar", anchor: "Intro L9-11", claim: "Every figure in report.md / data.json carries one of the four machine-resolvable markers, as defined by the commercial skill's claim-lint grammar."}
```

## Findings (broken)

### I5 — `reports/MQ-NN/<edition>/` file list · `stale-citation`
- **Claim:** each edition folder carries report.md, data.json, pins.json, edition.yml, quality.json **and approval.yml** (Structure row 5, L29).
- **Evidence:** four edition folders (MQ-01/03/05/08 @ 2026-09-08), all `status: draft` (edition.yml L3); each has the first five files — `approval.yml` is missing in all four. The pinning half is supported: `edition.yml` L7-9 `plan:` path + sha256, L10-16 `code_artifacts:` with sha256 per module/helper/generator. README L44 itself describes approval as a later gated step, so approval.yml is not a per-edition invariant.
- **Suggested fix:** reword L29 — `report.md, data.json, pins.json, edition.yml (pins plan + code artifacts), quality.json, plus approval.yml once approved`.

### I10 — `not-implemented` in catalog **and** sidecar · `stale-citation`
- **Claim:** unimplemented questions stay visible in the catalog and sidecar as `not-implemented` (L54-55).
- **Evidence:** sidecar half true — `.console/manufacturing-index.json` `"status": "not-implemented"` for MQ-02/04/06/07/09/10 (L212, L410, L610, L635, L840, L865); implemented four carry `draft-only`. Catalog half not literally true — `manufacturing.yml` has no `status` / `implementation` key on any question; the unimplemented state is expressed only by an absent `computation:` plus a `# roadmap: … not implemented.` comment (L175-176, L248, L319, L327, L396, L404). The six-question set matches between the two files.
- **Suggested fix:** either add `status: not-implemented` to the six catalog entries, or reword L54-55 to `stay visible in the catalog (no \`computation:\` block, roadmap comment) and are rendered in the sidecar as \`not-implemented\``. (Same situation as finance README L49-50, which the finance audit scored `unverified` — harmonise both READMEs with one wording.)

## Findings (unverified)

### E2 — ISO 13485 clause numbers · `registry-gap` — **the `[VERIFY]` posture is appropriate**
- **Claim:** ISO 13485 clause numbers are not distilled in this project and are tagged `[VERIFY]` wherever named (L52-53).
- **Evidence (L1a):** `.claude/skills/medtech-docs/references/standards/README.md` L38 "QMS-level standards (ISO 13485, 21 CFR Part 820) — not distilled here"; glob `**/*13485*` across `references/standards/` and `references/industry-frameworks/` → no files (only passing cross-refs in iec-62304.md L18, iec-82304-1.md L31). `references/regulations/21-cfr-part-820.md` L48 "this registry carries no ISO 13485 source text", L52 "ISO 13485:2016 (incorporated by reference — no distillation in this registry yet)"; its L33-41 QSR→ISO 13485 crosswalk rows are each `[VERIFY]`-tagged.
- **Evidence (L1b):** `docs/external/standards/README.md` L54 lists ISO 13485 as "Evaluated — not required … owned at the organization/QMS level"; glob `docs/external/**/*13485*` → no files; `docs/external/regulations/qmsr-part-820.md` L46 "[VERIFY] ISO 13485:2016 internal clause numbers … no ISO 13485 source text exists in this repository."
- **Domain sweep:** L51-53 of the README is the sole "13485" hit across README, manufacturing.yml, plans/, reports/, bq_modules/, code-quality/, .console/ — no ISO 13485 clause number is actually cited anywhere in the domain, so there is no un-tagged mention. The negative claim is true and the reference is genuinely unverifiable locally (paywalled; not web-fetched).
- **Suggested fix:** extend the registry with `.claude/skills/medtech-docs/references/standards/iso-13485.md` (clause map for 4.2, 7.3, 7.5.6, 8.2.2, 8.5.2/8.5.3 as invoked by § 820.10) plus an L1b applicability doc `docs/external/standards/iso-13485.md`, reconciling the L54 exclusion row — a project decision shared with the management-review audit (E1). Until then the `[VERIFY]` sentence should stand.

## Findings (sound)

- **E1** 21 CFR Part 820 (QMSR) — L1a-full `references/regulations/source-md/21-cfr-part-820.md` (faithful eCFR text, 89 FR 7523; § 820.1 Scope), L1a-aid `references/regulations/21-cfr-part-820.md`, L1b `docs/external/regulations/qmsr-part-820.md` ("Project Applicability … § 1 Applicability determination … § 3 Module mapping … § 4 Open items"). Both tiers present; "only distilled source" holds as a domain-reliance statement (the repo also distills Parts 807/814/880/892 and 45 CFR 164, none applicable here).
- **I1** `manufacturing.yml` — `domain:` L5-10, `lint: exempt_patterns:` L16-27, `terms:` L35-103 (16), `categories:` L105-110 (5), exactly ten `MQ-` ids (L114-L398); `personas`/`cadence`/`corpus_deps` on all 10; `computation`/`params`/`expectations`/`explainers` on the four implemented. Optional tightening: "implemented questions add params, expectations, explainers".
- **I2** `computations.py` L7-13 docstring (no clocks; shared helper layer, domain-local copy); `snapshot_as_of` L45-55 reads `provenance.yml as_of`, falls back to snapshot-id date; no `datetime.now`/`date.today`/`time.time`; no question-specific code. ("Copy" = shared subset copied and extended — commercial's copy lacks `snapshot_as_of`; README does not claim identity.)
- **I3** `bq_modules/` — exactly mq_01/03/05/08.py, each `def run(corpus_root, out, pins):` (L55/L22/L22/L20); no random/clock calls.
- **I4** `plans/` — README.md + MQ-01..MQ-10.md; README L3-6 user-owned + hash-pinned into `edition.yml`, L22 `## Verification plan`; MQ-01 edition.yml L7-9 pins `plans/MQ-01.md` sha256.
- **I6** `code-quality/records.yml` sha256-keyed entries (static_lint / poison_scan / determinism / `reviews: []`) for mq_01/03/05/08, computations.py, gen.py; README L3 "soft gate", L20-22.
- **I7** `.console/manufacturing-index.json` L2 `"schema_version": "1.5"`, L4-11 `domain` block (`key: manufacturing`, `id_prefix: MQ`).
- **I8** four `internal-*` datasets, all `internal: true` / "demo-fabricated"; implemented questions' corpus_deps are all `manufacturing/internal-*` (L119, L184, L256, L335); `computations.py` L24 BANNER consumed by all four modules; 4/4 report.md carry the banner at L3. **Forward note:** roadmap MQ-02/07/09 depend on `commercial/internal-revenue-plan`, `commercial/openfda-recalls-infusion` (not demo-fabricated), `commercial/internal-fleet`, `finance/internal-standard-costs` — L17-19 goes stale the moment one of them is implemented.
- **I9** params L121 `fpy_floor_pct: 95`, L186 `effectiveness_verified_floor_pct: 90`, L258 `reject_ceiling_pct: 3`, L337 `due_soon_days: 30`; all seven expectations `validated: false` with `[VERIFY]` bases (L126-128, L191-199, L263-271, L342-350); `[config: manufacturing.yml]` in all four reports via `CONFIG_MARKER` L25-26. (`due_soon_days` has no dedicated E-row — cited as a plan constant in the MQ-08 report.)
- **L1** `commercial.py` L1584-1585 `--domain` (resolved L1664-1665 to `docs/project/<domain>`); add_parser answer L1589, lint L1593, approve L1598, render L1605, check L1608, audit L1611, code-audit L1627, plan-init L1644, catalog L1648 — all nine present (four unlisted extras: record-verification, record-code-review, dependents, pack).
- **L2** `.claude/skills/project-console/console/commercial/router.py` L704 `@router.get("/domains/{domain}")`; `loader.py` L5-7 domains discovered from `docs/project/<slug>/.console/<slug>-index.json`, L80 `href: /domains/{domain}`, L33 `KNOWN_ICONS` includes `manufacturing`; `commercial/SKILL.md` L83-84; `tests/test_commercial_domains.py` L138-145/L161-162.
- **L3** `commercial.py` L1601 `--by` (required), L1602 `--verify-note` (consumed L1017); `cmd_check` L1149-1155 hash mismatch → "MUTATED after approval?" for approved/superseded editions. ("tamper" is the README's paraphrase; SKILL.md L205 says "mutation detection".)
- **L4** `commercial.py` L48 `MARKER_RE` covers src/assume/derived/config (+ `waived`); L724-729 `config:` resolved as a repo-relative file path, so `[config: manufacturing.yml]` is the correct form; L745 numeric-coverage lint; all four quality.json `lint.status: pass`, `marker-resolution` pass, config `resolved: true`. (No current manufacturing report uses `[assume:]` — grammar accepts it.)

## Open Resolutions

_Surfaced by the audit but requiring SME adjudication or project decision — not a defect in the citation itself but an action it points at._

- **E2 — ISO 13485 posture decision** (owner: quality-engineering / regulatory-affairs; shared with `management-review-readme-references-audit` E1): `docs/external/standards/README.md` L54 deliberately excludes ISO 13485 as QMS-level while this README and two others carry `[VERIFY]` tags waiting for a distillation. Decide once — distill (and amend the exclusion row) or repoint the tags to the QMS SOP as governing source.
- **Verdict-band inconsistency to note:** I10 here (`broken`) and finance I12 (`unverified`) describe the same catalog-vs-sidecar wording issue; the researchers scored it differently. Treat both as the same wording fix.
- **I8 forward note** — when MQ-02/07/09 are implemented, L17-19 ("every dataset this domain reads … demo-fabricated `corpus/manufacturing/internal-*`") must be revised because `commercial/openfda-recalls-infusion` is real external data.

## Provenance

- Extraction method: regex pass over the source doc + LLM pass over narrative prose with regex-extracted spans masked (D-202.12).
- Verdict bands: three-band — `sound | unverified | broken` (D-202.13).
- External-formal references verified by two-tier L1a + L1b consolidation (D-202.14).
- Finding `kind` enum is open — v1.1 emits the link-checking subset plus `registry-gap`; v2 candidate kinds reserved per the skill's SKILL.md roadmap section.
- Doc-slug qualified with the parent folder (`manufacturing-readme`) — inference; SKILL.md `init` step 2 is silent on basename collisions across sibling `README.md` sources.
