---
audit_id: RA-management-review-readme-001
source_doc: docs/project/management-review/README.md
created: 2026-09-08
status: Findings Posted
schema_version: 1
---

# References Audit — Management review — assembled input packs

**Source doc:** [`docs/project/management-review/README.md`](../../../../docs/project/management-review/README.md)
**Audit ID:** `RA-management-review-readme-001`
**Created:** `2026-09-08`
**Status:** `Findings Posted`

This audit verifies that every citation in the source document actually resolves to a real source and that the source supports the cited claim. Findings carry a verdict band (`sound | unverified | broken`) and a finding kind (open enum). External-formal references are verified against both the medtech-docs registry distillation (L1a) and the project applicability layer (L1b) per the "cite both" mandate. See the `reference-audit` skill SKILL.md for the engine contract; see the `citations` advisor for the verdict semantics.

## Summary

| Class | sound | unverified | broken | Total |
|-------|------:|-----------:|-------:|------:|
| external-formal | 0 | 1 | 0 | 1 |
| internal-formal | 3 | 0 | 0 | 3 |
| informal-link | 4 | 0 | 0 | 4 |
| **Total** | **7** | **1** | **0** | **8** |

_Verified 2026-09-08 by the `citations` advisor (batch fan-out, task 118). Method note: 6 of 8 verdicts are researcher verdicts; L1 and L2 were verified directly by the engine after their researcher dispatches hit the concurrent-subagent cap._

## References (Pending Verification)

_All 8 entries dispositioned on 2026-09-08 — retained as the extraction inventory; verdicts are in the Findings sections below._

```yaml
references:
  - {id: E1, class: external-formal, method: regex, target: "ISO 13485 (management review; [VERIFY] tag pointing at a future distillation under docs/external/standards/)", anchor: "Intro paragraph 2 L13-17", claim: "No ISO 13485 management-review distillation exists today in either the registry (L1a) or the project applicability layer (L1b docs/external/standards/), so the [VERIFY] tag is the correct posture until one is distilled; the QMS — not this folder — governs which clauses require the review and its minutes/outputs."}
  - {id: I1, class: internal-formal, method: regex, target: "docs/project/management-review/YYYY-MM-DD/{pack.md, pack.json}", anchor: "Structure table", claim: "Each dated pack folder holds a reviewer-facing pack.md and a machine-summary pack.json (per domain: answered ids + editions, unanswered ids, issue/risk counts, expectation verdict tallies); at least one dated pack exists on disk in that shape."}
  - {id: I2, class: internal-formal, method: llm, target: "docs/project/{commercial,finance,manufacturing}/ approved editions", anchor: "Intro L5-9", claim: "The pack assembles, per business domain (Commercial, Finance, Manufacturing), the latest approved answer edition of each question — verdict, expectation verdicts, materialized issues, open risks, pinned snapshots + freshness — plus the roster of questions with no approved answer."}
  - {id: I3, class: internal-formal, method: llm, target: "pack.md report references by repo-relative path (no copied report bodies)", anchor: "Conventions L40", claim: "Packs reference reports by repo-relative path and never copy report bodies."}
  - {id: L1, class: informal-link, method: regex, target: ".claude/skills/commercial/scripts/commercial.py pack --domains commercial,finance,manufacturing [--as-of YYYY-MM-DD] [--include-drafts]", anchor: "Intro L5-6; Expected Content L29-30", claim: "commercial.py has a `pack` action that accepts `--domains` (comma-separated), `--as-of` (freshness anchor) and `--include-drafts` (flags drafts inline), assembling approved editions only by default."}
  - {id: L2, class: informal-link, method: llm, target: "project console Workflows → Management Review Pack", anchor: "Expected Content L30-31", claim: "The project console's Workflows catalog exposes a Management Review Pack workflow that invokes the pack action."}
  - {id: L3, class: informal-link, method: regex, target: ".github/workflows/business-evidence-refresh.yml (monthly; approved editions only)", anchor: "Expected Content L31-32; Changelog", claim: "A monthly GitHub Action named business-evidence-refresh exists and runs the pack action with approved editions only (no --include-drafts)."}
  - {id: L4, class: informal-link, method: regex, target: ".claude/skills/commercial/SKILL.md version 15 (pack action)", anchor: "Changelog L46", claim: "The commercial skill is at version 15 and its SKILL.md documents the `pack` action."}
```

## Findings (broken)

_None._

## Findings (unverified)

### E1 — ISO 13485 management review (`[VERIFY]` tag) · `registry-gap` — **the `[VERIFY]` tag is appropriate**
- **Claim:** no ISO 13485 management-review distillation exists today in L1a or L1b; the tag asks for one "once one exists under `docs/external/standards/`".
- **Evidence (L1a):** `.claude/skills/medtech-docs/references/standards/` holds 12 files, none ISO 13485; its README L38: "QMS-level standards (ISO 13485, 21 CFR Part 820) — not distilled here; those are organizational compliance, not per-device." `references/regulations/21-cfr-part-820.md` L48/L52: "this registry carries no ISO 13485 source text … ISO 13485:2016 (incorporated by reference — no distillation in this registry yet)". `grep -i 13485` across the registry = 22 incidental cross-mentions, no distillation; "management review" in the Part 820 distilled + source-md = 0 hits.
- **Evidence (L1b):** `docs/external/standards/` — same 12-file roster, no ISO 13485. Its README L52-54 lists ISO 13485 under **"Evaluated — not required"**: "QMS-level standard — owned at the organization/QMS level, not the project DHF". `docs/external/regulations/qmsr-part-820.md` L46 carries the same posture: "[VERIFY] ISO 13485:2016 internal clause numbers … no ISO 13485 source text exists in this repository."
- **Verdict:** the negative premise is true in both tiers and ISO 13485 is paywalled (not web-fetched) — the reference is genuinely unverifiable locally, so the `[VERIFY]` posture is correct.
- **Suggested fix (project decision, not made here):** the tag's expectation of a *future* distillation under `docs/external/standards/` conflicts with that folder's own README (L54), which deliberately excludes ISO 13485 as QMS-level. Either (a) distill ISO 13485:2016 § 5.6 into the registry (`references/standards/iso-13485.md`, clause numbers `[VERIFY]` since no source text can be bundled) plus a project applicability note, and reconcile the README exclusion row; or (b) repoint the tag to the QMS as the governing source (e.g. the management-review SOP under `docs/internal/`) and drop the "once one exists under `docs/external/standards/`" expectation.

## Findings (sound)

- **I1** `management-review/` holds exactly README.md + `2026-09-08/pack.md` + `2026-09-08/pack.json`; pack.json top-level `as_of`, `domains[]` (commercial | finance | manufacturing), `include_drafts`; per domain `answered[]` `{id, edition, draft}`, `unanswered[]`, `issues`, `risks`, `expectations {met, not-met, at-risk, not-evaluable}` — all four README-described elements present.
- **I2** all three domain folders exist; pack.md L5/L473/L490 per-domain sections; L9 "edition `2026-07-27.3` (approved) · report: `docs/project/commercial/reports/BQ-01/…`", Verdict / Expectation table / Issues / Risks / Pins lines, "### Not in this pack" rosters (L475-479, L492-496: FQ-01..FQ-10 — finance and manufacturing have draft editions only, no approved ones). `commercial.py` L1462-1464 picks `status == 'approved'`; L1470-1474 `cmd_pack` docstring matches the README sentence.
- **I3** 30/30 answered questions in pack.md point at a repo-relative `docs/project/commercial/reports/<id>/<edition>/report.md`; report sections (economics table, narrative, method) do not appear in the pack. `commercial.py` L1515 `relative_to(parent.parent.parent)`; L1514 reads `data.json` — `report.md` is never read or copied.
- **L1** `commercial.py` L1656 `add_parser("pack", …)`, L1657 `--domains` (comma-separated), L1659 `--as-of` ("also the freshness anchor"), L1660 `--include-drafts`; L1458-1467 approved-only default with flagged draft fallback; L1516-1518 inline ` **DRAFT**` tag.
- **L2** `.claude/skills/project-console/console/workflows/catalog.py` L265-281 `Workflow(slug="management-review-pack", title="Management Review Pack", backend_status="live", …)`; `router.py` L152/L164 posts `/workflows/management-review-pack/generate` → `commercial.py pack --domains …`. (Catalog source lives under the skill's `console/` tree, not `tools/project-console/` — the runtime shell.)
- **L3** `.github/workflows/business-evidence-refresh.yml` L25 name; L27-30 crons (weekly Mon + `30 5 1 * *` monthly); L127-131 "Monthly — assemble the Management Review Pack (approved editions only)" → `pack --domains … --out docs/project/management-review`; `--include-drafts` = 0 matches. The weekly cron is gated out of the pack step, so "monthly" is accurate.
- **L4** `commercial/SKILL.md` L4 `version: 15`, L5 `updated: 2026-09-08`; L337-344 `### pack --domains a,b,c [--out DIR] [--as-of …] [--include-drafts]` section. (SKILL.md has no changelog, so "v15 documents pack" is verified; "v15 introduced pack" is not asserted and was not checked.)

## Open Resolutions

_Surfaced by the audit but requiring SME adjudication or project decision — not a defect in the citation itself but an action it points at._

- **E1 — ISO 13485 posture decision** (owner: quality-engineering / regulatory-affairs). `docs/external/standards/README.md` L54 excludes ISO 13485 as QMS-level, while three project docs (`management-review/README.md` L16-17, `qmsr-part-820.md` L46, `manufacturing/README.md` L51-53) now carry `[VERIFY]` tags waiting for a distillation there. Decide once: distill (and amend the exclusion row) or repoint the tags to the QMS SOP. Until then the tags are correct and should stay.
- **Uncited standards fact (v2 `unsourced-claim-candidate`, not emitted in v1.1):** README L13-14 lists the management-review input set ("complaints, CAPA, supplier performance, post-market and financial data") — an ISO 13485 § 5.6.2 / QMSR-derived list with no citation. Resolves with E1.

## Provenance

- Extraction method: regex pass over the source doc + LLM pass over narrative prose with regex-extracted spans masked (D-202.12).
- Verdict bands: three-band — `sound | unverified | broken` (D-202.13).
- External-formal references verified by two-tier L1a + L1b consolidation (D-202.14).
- Finding `kind` enum is open — v1.1 emits the link-checking subset plus `registry-gap`; v2 candidate kinds reserved per the skill's SKILL.md roadmap section.
- Doc-slug qualified with the parent folder (`management-review-readme`) — inference; SKILL.md `init` step 2 is silent on basename collisions across sibling `README.md` sources.
