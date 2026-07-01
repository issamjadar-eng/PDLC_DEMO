# 088 — Submissions Skill: Filing-Type Profiles + Manifest Ownership + Architecture Markup

**ID**: 088
**Created**: 2026-06-15
**Status**: Complete
**Created By**: Ben Xavier
**Owner**: Ben Xavier
**Priority**: High

---

## PERMANENT RULES (do not remove)

This task document is the **session-recovery point** for this work. If the current session drops, is compacted, or ends, the next session must be able to load **this file alone** and continue where we left off. That is only possible if the doc is kept current in-flight.

1. **Update at every meaningful checkpoint (HARD RULE).** After each meaningful unit of work — a converted/adopted doc, a committed change, a launched batch, a completed phase, a decision, a discovered blocker, a design pivot — update this task doc: tick the relevant Todo, add a dated Changelog line naming the concrete artifact, update any progress counts in Goals.
2. **Phase-end batching is OK; drift-batching is not.** Write at the phase boundary, before the next phase starts.
3. **A commit is not a substitute.** Git records code; this doc records the narrative.
4. **Resume-ready before any session boundary.**
5. **Capture strategy + lessons as they happen.**

## Goals

Make the `submissions` skill able to generate **good-quality Q-Subs, 510(k)s, and PMA (placeholder)** — not just the Q-Sub-shaped set it ships today. Scope this round is **capability only** (no PP3500 content authored).

- **Filing-type template profiles.** Today `templates/` is a single flat, Q-Sub-shaped set and `scaffold` instantiates *all* of it regardless of filing type (SKILL.md L80–83). Reorganize into per-filing-type profiles so `scaffold 510k` lays down the 510(k) document set (SE discussion, predicate comparison, IFU/FDA-3881, 510(k) summary, truthful-&-accuracy) and `scaffold pma` lays down PMA placeholder stubs.
- **Register PMA** as a recognized filing type (skill description, `render_sidecars.py` `FILING_META`, scaffold profile).
- **Composition-manifest ownership.** Affirm `submissions` owns the manifest (schema + template + authoring); `/tracker` stays a read-only consumer. Declare the manifest's load-bearing section/column contract once in the skill so filing-type variants can vary *content* (pieces/rows) without breaking the section/column skeleton tracker's `generate.py` parser + 2 best-practices checks key on.
- **README architecture + cross-skill dependency markup.** Document the submissions↔tracker (and dhf-manifest / project-console) boundaries and producer/consumer seams in the README; mark up dependencies/relationships in both skills' SKILL.md.

## Decisions (this task)

<!-- STRATEGY CONTENT: architecture, regulatory — submission package tooling boundaries -->

- **Scope = capability only** (user, 2026-06-15). Build the skill's *ability* to generate good 510(k)/PMA filings; do **not** author the PP3500 510(k)/PMA content this round.
- **Do NOT merge tracker into submissions** (user Q, 2026-06-15). They sit at different layers: `submissions` = FDA-facing **content authoring + packaging** for one filing; `/tracker` = **program-wide readiness scoreboard** across all DHFs + engineering prerequisites + multiple milestones (QSub→510k+PCCP→LMR1→LMR2), with obligation-coverage analysis against the dhf-manifest catalog and lifecycle-state plugins (Confluence/Comala, SharePoint, Jira, Windchill…). Submissions would consume **none** of that. Mental model: **dhf-manifest = syllabus · tracker = scorecard · submissions = one of the things being scored (and the only one it also authors).**
- **Composition-manifest = the single seam.** `submissions` authors it; `/tracker` reads it as **one of ~7 inputs**. Healthy producer/consumer boundary, not a merge line. Ownership: submissions owns schema + template + authoring; tracker is a consumer keyed to a stable section/column contract.
- **How the manifest is built today:** scaffolded from `composition-manifest.template.md` then hand-authored — **NOT** auto-generated from `regulatory.yml` milestones (tracker SKILL.md L31 "projection of milestone bindings" is conceptual framing, not mechanical).
- **Two parsers exist:** `submissions/scripts/render_sidecars.py::parse_manifest()` (L220) + `tracker/scripts/generate.py` R9.3 manifest walker (L482–612). **Lean: keep them independent but governed by one *declared* schema** (less invasive; matches the loose-coupled sidecar pattern both skills already use). Collapsing into one shared parser is a deferred follow-up, not this round.

## Todos

- [x] Read `submissions/SKILL.md`, `tracker/SKILL.md`, submissions README end-to-end; trace manifest producer/consumer
- [x] Confirm state: qsub fully authored; 510k manifest-only (no content docs); pccp empty; PMA absent
- [x] Activate task (088) + route build through `/skill-creator` conventions
- [x] Reorganize `templates/` into per-filing-type profiles (`_shared/` + `qsub/` + `510k/` + `pma/`) — via `git mv` (history preserved)
- [x] Author 510(k) template set (cover letter, indications-for-use/FDA-3881, 510(k) summary, substantial-equivalence + predicate comparison table, device description, performance-testing summary, truthful-&-accuracy) — 7 files
- [x] Author PMA **placeholder** template set (cover letter, SSED, device description, nonclinical/clinical, manufacturing, labeling) — 7 stubs, each `🚧 PLACEHOLDER`
- [x] Register PMA in `render_sidecars.py` `FILING_META` + new `DOC_META`/`DOC_ORDER` stems + docstring; verified parser unaffected
- [x] SKILL.md: PMA in description; profile-aware `scaffold` rewrite; `## Filing-type profiles` registry; `## Composition-manifest contract` (section/column schema); `### Skill relationships` producer/consumer table; v1→v2 + VERSION=2
- [x] README: `## Architecture & boundaries` (profiles + submissions↔tracker ownership + why-not-merge); Best Practices extended; v2 changelog row
- [x] tracker/SKILL.md: ownership attribution on Context input #3 (submissions owns manifest; tracker read-only consumer); v13→v14 + README changelog
- [x] Ran `render` + `render --check` — clean (exit 0); sidecars byte-identical (no regression); qsub still 7 docs; index shows 510k + qsub
- [x] Verification: spawned `regulatory-affairs` (vs FDA) + `quality-engineering` (vs QMS source-md) agents; consolidated punch-list (see Verification section)
- [x] Applied F1–F5 + scaffold notes (S1/S2); labeling/standards handled as **DHF-attached exhibits** (user decision). Re-verified: `render --check` exit 0, no stray `807.87(k)`, `(l)` in all 3 spots. Folded into v2 changelog (v2 unshipped — no v3 mint).
- [ ] **Deferred follow-ups (B1–B4, NOT this skill — separate authoring):** B1 add `docs/external/...`/`references/regulations/21-cfr-part-814.md` distillation before PMA build-out; B2 author `GL-FORM-RA-001` + taxonomy-map the manifest; B3 author `GL-WI-RA-003` (PMA WI); B4 pin §807.87 subsection letters in `references/regulations/21-cfr-part-807.md`.
- [x] Pushed — PR #59 merged to `main` (`b24111e`); branch deleted.
- [x] B1–B4 spun out to **ben/089** (separate references + QMS authoring scope).
- [ ] (Optional) `/skill-creator audit-triggers submissions` — recommended after frontmatter/Actions edit; deferred (runs 20 `claude -p` evals)

## Verification (two agents, 2026-06-15)

<!-- LESSONS LEARNED: verification, regulatory — registry-template correctness vs scaffold-time mapping -->

Read-only verification of the new 510(k)/PMA templates by `regulatory-affairs` (vs FDA) + `quality-engineering` (vs `docs/internal/source-md/` QMS). Verdicts: 510(k) **sound, ship after fixes**; PMA **fine as intentional placeholder**.

**Template-level fixes (registry-correct, project-agnostic — apply here):**
- **F1 [verified] Citation error** — Truthful-&-Accuracy cited `807.87(k)`; correct is **`807.87(l)`** ((k) is the Class III cert). Verified vs live eCFR + our own `510k-estar-distilled.md` (already correct). 3 occurrences: `510k/truthful-accuracy-statement.md` ×2, `510k/cover-letter.md` ×1.
- **F2 Shared composition-manifest hardcodes Q-Sub pieces** (`intended-use`, `pccp-summary`, `fda-questions`, strengthener briefs) → breaks the 1:1 cover-letter↔manifest alignment the 510(k) cover letter mandates. Fix: genericize the `_shared` manifest's Included-Pieces rows so they're profile-neutral (scaffold injects per-profile rows — SKILL.md scaffold step 4 already says this; the literal rows mislead).
- **F3 Proposed labeling listed-but-absent** — cover-letter §4 + manifest reference it; no `510k/labeling.md`. QE: labeling is **DHF-derived** per GL-WI-RA-001 §5.3. Resolution options: document-as-DHF-attached (annotate) vs add template.
- **F4 Consensus Standards / Declarations of Conformity** — own eSTAR section; absent from 510(k) set (partial in `performance-testing.md`). Add a short DoC section vs DHF-attach.
- **F5 [nice] eCopy/eSTAR wording stale** — eSTAR mandatory since 2023-10-01; eCopy is not an electronic submission. Reword `510k/cover-letter.md` §5.

**Scaffold-time / SKILL.md-doc (not template edits):**
- **S1** Sign-off roster: registry default `R&D / RA / QA` is fine generic; **this QMS** wants GL-WI-RA-001 §5.4 chain (RA Specialist → RA Lead → Quality → **VP-RA**) — populate at scaffold time. Document in SKILL.md/README that scaffold maps sign-off to the project QMS chain.
- **S2** `status: placeholder` is not in the GL-SOP-QM-001 §6.2 status enum; only matters if a submission doc becomes a controlled record (it's a derived view; controlled record = DHF artifact per WI §5.3). Document the transition, don't change templates.

**QMS / reference backlog (out of this skill — separate authoring):**
- **B1** No `references/regulations/21-cfr-part-814.md` distillation exists → PMA subsection citations are **unverified**; add before any PMA build-out.
- **B2** QMS has **no `GL-FORM-RA-*`** for submission package assembly → recommend authoring GL-FORM-RA-001 + map composition-manifest doctype to it via `.taxonomy.yml`.
- **B3** PMA has **no governing QMS doc** (GL-WI-RA-001 §2 defers to future GL-WI-RA-003).
- **B4** `references/regulations/21-cfr-part-807.md` lists §807.87 elements as **unlettered bullets** — pin the subsection letters (this ambiguity let the (k)/(l) slip).

**Confirmed-correct (no action):** roles-only sign-off (conformant w/ GL-SOP-QM-006 §6 separation-of-duties — do NOT add Author row); 510(k) Summary-vs-Statement choice present; Class III cert + exec summary correctly out-of-scope; PMA major 814.20(b) components all covered.

## Open Questions

- Collapse the two manifest parsers into one shared implementation? (Lean: no — keep independent under one declared schema this round; revisit as follow-up.)
- PMA depth — pure placeholder stubs only this round (confirmed: capability-only, placeholder per user).

## Changelog

- 2026-06-15: Task created. Grounding complete (both SKILL.mds + README read; manifest producer/consumer traced; filing state confirmed). Scope = capability-only; tracker-merge rejected with rationale; manifest-ownership stance + two-parser lean captured.
- 2026-06-15: **Capability build complete (local).** submissions v1→v2. (1) `templates/` reorganized into profiles `_shared/` + `qsub/` + `510k/` + `pma/` (`git mv` preserved history for the 7 moved files). (2) Authored 510(k) profile (7 docs incl. substantial-equivalence with inline predicate-comparison table, IFU/FDA-3881, 510(k) summary, performance-testing, truthful-&-accuracy) + PMA placeholder profile (7 `🚧 PLACEHOLDER` stubs). (3) `render_sidecars.py`: added `pma` to `FILING_META`, +10 `DOC_META` stems, expanded `DOC_ORDER`, docstring. (4) SKILL.md: profile-aware `scaffold` (resolves filing→profile, stops on unknown type instead of falling back to Q-Sub), `## Filing-type profiles` registry, `## Composition-manifest contract` (declares the sections/columns `/tracker` parses), `### Skill relationships` producer/consumer table, PMA in description. (5) README: `## Architecture & boundaries` (profiles + submissions-owns-manifest / tracker-consumes + why-not-merge), Best Practices + v2 changelog. (6) tracker SKILL.md v13→v14: manifest ownership attribution on Context input #3 + README changelog. **Verification:** `render` + `render --check` clean (exit 0), sidecars byte-identical (idempotent, no regression), qsub intact at 7 docs. No commit (awaiting user push request).
- 2026-06-15: **Pushed + closed.** PR #59 merged to `main` (`b24111e`); branch deleted; submissions v2 + tracker v14 shipped. B1–B4 follow-ups spun to ben/089. Status → Complete.
- 2026-06-15: **Two-agent verification + fixes.** `regulatory-affairs` (vs FDA: 21 CFR 807 Subpart E, RTA/eSTAR backbone, SE guidance, 814.20(b)) + `quality-engineering` (vs `docs/internal/source-md/` QMS). Both: 510(k) sound / PMA fine-as-placeholder. Applied F1 (citation `807.87(k)`→`(l)`, verified vs live eCFR + our `510k-estar-distilled.md`, 3 spots), F2 (genericized `_shared` manifest Included-Pieces — was Q-Sub-shaped, broke cover-letter↔manifest 1:1), F3/F4 (proposed-labeling + consensus-standards/DoC documented as **DHF-attached exhibits** per user decision + GL-WI-RA-001 §5.3 — annotated cover-letter §4 + manifest "Attached from DHF" table + SKILL.md profiles note), F5 (eSTAR-mandatory wording), S1/S2 (scaffold-time QMS-mapping notes in SKILL.md: sign-off chain + controlled-record transition stay project-specific). Re-verified clean. Fixes folded into v2 changelog. **Deferred B1–B4** (Part 814 distillation, GL-FORM-RA-001, GL-WI-RA-003, pin 807.87 letters) — separate docs/QMS authoring, out of this skill's scope. No commit.

## Economics

_Retrospective estimate (rough; from task summary). See effort-estimation-rubric.md._

```json
{
  "economics": {
    "method_version": 1,
    "retrospective": true,
    "agentic_hours": 9,
    "todos": [
      {
        "todo": "Submissions filing-type profiles",
        "personas": [
          "rd-lead",
          "regulatory-affairs"
        ],
        "manual_hours": {
          "min": 24,
          "max": 60
        },
        "confidence": "low",
        "basis": "submissions v2 filing-type profiles + doc sets"
      }
    ]
  }
}
```
