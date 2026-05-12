# 047 — Tracker Upstream-Baseline Improvements

**ID**: 047
**Created**: 2026-05-11
**Status**: Not Started
**Created By**: Ben Xavier
**Owner**: Ben Xavier
**Priority**: Medium

---

## PERMANENT RULES (do not remove)

This task document is the **session-recovery point** for this work. If the current session drops, is compacted, or ends, the next session must be able to load **this file alone** and continue where we left off. That is only possible if the doc is kept current in-flight.

1. **Update at every meaningful checkpoint (HARD RULE).** After each meaningful unit of work — a converted/adopted doc, a committed change, a launched batch, a completed phase, a decision, a discovered blocker, a design pivot — update this task doc:
   - tick the relevant Todo checkbox
   - add a dated Changelog line naming the concrete artifact (commit SHA, file path, decision, blocker)
   - update any progress counts/tables in Goals
2. **Phase-end batching is OK; drift-batching is not.** Planned phases (e.g., "finish Phase 2, then log the whole phase at once") are a legitimate checkpoint — writing once per phase is fine if the phase is bounded and the write happens **at the phase boundary, before the next phase starts**. What's not OK: accumulating updates in your head across arbitrary work, waiting for "end of the session," "after the push," or the user to ask. By then a crash or context-trim has lost the state. Rule of thumb: if you can't name the specific upcoming checkpoint where you'll write the update, write it now.
3. **A commit is not a substitute.** Git history records code; this doc records the project narrative — what was done, why, what's left, what surprised us.
4. **Resume-ready before any session boundary.** Before recommending a fresh session, marking Complete, or ending work, the doc must already contain: (a) what was completed this session with concrete artifacts, (b) status of any in-flight work and temp artifacts, (c) priority-ordered next steps with file paths, (d) open questions blocking progress, (e) the exact `/task` activation command to resume.
5. **Capture strategy + lessons as they happen.** If the session produces option comparisons, scope/boundary decisions, architectural pivots, non-obvious insights, or corrected assumptions, write them into the appropriate section **in-flight** — not just in chat. Harvesting skills can only surface what was written.

Success test for this doc: a fresh Claude session, given only this file, can re-enter the work without asking the user "what were we doing?"

## Goals

Now that the tracker skill and submission tracker artifacts are reset to the upstream baseline (hitachi `origin/main` v11 — see `tasks/ben/044/archive/wip-dropped-2026-05-11/` for the dropped v16/v17 WIP), drive a series of focused improvements on top of this clean foundation. The goal is to get the dashboard from the current 44-row baseline back to something with the depth of the legacy 118-row tracker (`tasks/ben/044/archive/wip-dropped-2026-05-11/project-artifacts/submission-tracker.md.backup-2026-05-05`) — but built on the **milestone-driven generator model** that upstream supports, not the legacy hand-curated FDA-TOC structure.

- Make the live dashboard at `/dashboards/submission-tracker` materially useful for demoing the PP3500 program (not just a 44-row stub)
- Stay on the upstream tracker skill — improvements land as project-data changes (project.yml, milestones catalog, composition manifests, DHF evidence) or as upstream-pushable skill changes, not as a local fork
- Preserve B6 Create Draft button surface — every improvement should keep or grow the set of rows that can drive a draft workflow

## Starting State (2026-05-11)

**Skill side** — upstream `origin/main` `tracker` v11 + `project-console` 1.17.0 + `md-deck` build.py 3.9 fix + new B6 Create Draft pieces (`tracker/agents/draft-author.md`, `tracker/scripts/build-draft-context.py`, `project-console/workflows/draft_*.py`, etc.). Clean — no local edits to skill files.

**Project side** — submission tracker regenerated via upstream v11 generator:
- `docs/project/submissions/submission-tracker.md` — 52-table-row, 5.8KB markdown (`## Phase: <milestone>` × DHF structure)
- `docs/project/submissions/submission-tracker.html` — 24.7KB rendered dashboard, **44 item rows + 6 Create Draft buttons**
- `docs/project/milestones/regulatory.yml` — 4 milestones (qsub-release, pccp-release, lmr1-release, lmr2-release) bound to pca-device DHF
- `docs/project/submissions/510k/composition-manifest.md` — single composition manifest present
- Console at http://127.0.0.1:8765 — boots clean, serves dashboard with rows visible

**Archived / not deleted** — `tasks/ben/044/archive/wip-dropped-2026-05-11/`:
- All v16/v17 skill WIP (assess-phases, classify-folders, init-taxonomy, reconcile-taxonomy actions; folder-classifier + phase-mapper agents; taxonomy.schema.yml; 7 scripts including taxonomy.py)
- Generator output sidecars (aggregates.json, gaps.json, help.json, phase-map.json, row-source.json) and `tracker-user-rows.yml`
- Legacy canonical (`submission-tracker.md.backup-2026-05-05` = 28.8KB / 118 rows / Part 1–4 FDA-TOC structure) and `.preinit` twin
- `pca-device.taxonomy.yml` (the DHF-scoped taxonomy file written by `init-taxonomy`)
- HTML for the candidate dashboard

## Full 7-Stage Recovery Plan (drafted 2026-05-11)

User asked for plan-mode review before any writes. Each stage below shows: what gets authored / executed, the source of truth (legacy backup row inventory), the target file(s), and the expected dashboard delta after the stage lands. Stages 1-4 are pure project-data authoring (no skill calls). Stage 5 is a generator data fix. Stages 6-7 are skill action invocations that produce sidecars.

**Legacy backup inventory:** 79 rows + 11 sections at `tasks/ben/044/archive/wip-dropped-2026-05-11/project-artifacts/submission-tracker.md.backup-2026-05-05`. ID prefixes: CY (21), ENG (20), SW (19), RM (8), HF (8), MS (7), PC (6), AI (6), PS (5), LB (3), CL (3), PR (2), DD (2), ST (1), plus single-letter A (3 admin rows — A1/A2/A3).

### Stage 1 — Structural chrome (hand-author into current `submission-tracker.md`)

**Lift:** small. Copy-port verbatim from backup. No skill changes. Generator regen will overwrite the row tables but will not overwrite intro/legend sections that the renderer doesn't own — those persist if appended after the generator's emitted sections.

**Content to insert (all from backup lines 1-75 + 297-307):**
- Title + header banner (replaces "Generator Candidate" title with canonical "Submission Package Tracker")
- `## Context & Sources` (6 subsections naming the 6 inputs: composition manifests, project manifest, system SADs, regulatory strategy, submission tracker task, FDA guidance)
- `## Two-Level Deliverable Model` (explains row-id convention: prefix=category, suffix=module variant)
- `## Status Legend` (Not Started / Partial / In Progress / Done table)
- `## Effort Scale` (Low / Med / High / V.High definitions)
- `## Phase Scale` (Filing / Filing (proto) / Release 1 / Release 2 / Release 3 — these are LEGACY phase names; need to reconcile with new milestone names QSub/510k+PCCP/LMR1/LMR2)
- `## Cross-Milestone Summary` (skeleton — populated as rows land)
- `## Reviewer Sign-off` (skeleton — R&D Lead / Regulatory / QA roles)
- `## Changelog` (preserve dated session entries from backup)

**Phase-scale reconciliation decision needed:** legacy `Filing` ≡ new `510k+PCCP`. Legacy `Release 1` ≡ new `LMR1`. Legacy `Release 2` ≡ new `LMR2`. Legacy `Release 3` is beyond our current 4-milestone scope. Plan: replace legacy phase values with the new milestone short-labels inline.

**Dashboard delta:** chrome only (no rows change). Visible improvement: legends visible, context section visible, page no longer says "Generator Candidate" in title.

### Stage 2 — Author `docs/project/milestones/engineering.yml`

**Lift:** medium. New file, schema mirrors sister's `engineering.yml` (see schema reference in this doc above).

**Content:** all 20 ENG rows from backup (ENG1-ENG20). Each becomes a binding with: `id`, `capability` (the Prerequisite text), `scope: Device` (legacy says "Device" — needs reconciliation: in new model, scope is the architecture name → likely `Suite` for pca-device or per-module if some ENG rows are module-specific), `effort`, `unblocks: [<gate IDs>]` (these are the downstream row IDs the legacy lists in the Gates column), `status: Not Started`, optional `notes`.

**Phase distribution:** ENG1-18 are legacy "Filing" → bind to `pccp-release` milestone. ENG19-20 are legacy "Release 2" → bind to `lmr2-release`. Decision: emit as one `engineering-pccp-release` milestone with `prerequisites: [pccp-release, lmr2-release]` (multiple regulatory milestones the eng work supports), or split into two engineering milestones. Sister chose one. Recommend: one milestone with two `prerequisites:`.

**Downstream concern:** the `unblocks:` IDs reference downstream rows (RM2a, SW3a, CY2a, etc.). Those rows don't exist yet — they'd be authored in Stages 3-5. The `unblocks` field is informational (renders in tracker's Gates column); if a referenced ID doesn't exist as a row, the rendering doesn't break — the Gates column just shows the literal ID string and the reader infers the dependency. Safe to author ahead.

**Dashboard delta:** +20 ENG rows, new Engineering Prerequisites section appears between Phase sections and Deliverable Details.

### Stage 3 — Author `docs/project/submissions/qsub/composition-manifest.md` + `tracker-user-rows.yml`

**Lift:** medium. Folder `qsub/` exists at `docs/project/submissions/qsub/` but no manifest. Sister's qsub manifest is the schema template.

**Content sources:**
- Backup `## Part 1.1 Administrative & Cover` rows: A1 (Cover Letter), A2 (510(k) Summary), A3 (Indications for Use Form FDA 3881) — these are legacy 510(k) admin items but are also Q-Sub items in pre-submission form.
- Sister's qsub model has 12 Q rows (Q1-Q12); we may not need all 12. Minimum viable: 4-5 narrative pieces (cover letter, device description, indications, predicate analysis, PCCP summary) corresponding to Q4-Q8 in sister's numbering — these are the 5 rows that carry the live Create Draft buttons in sister.
- Plus 1-3 "supporting" pieces pointing at our existing System SAD, regulatory strategy, etc.

**Two artifacts to author:**
1. `qsub/composition-manifest.md` — narrative manifest with Required/Supporting tables, each piece referencing a Tracker Row ID
2. `tracker-user-rows.yml` — the user-injected row registry. Each Q-row entry has: `id: Q4`, `name`, `scope: (submission)`, `phase: QSub`, `status: Not Started`, `reason`, `path: '<button class="tracker-action-btn" disabled>Create Draft</button>'` — that path-cell button is what render.py wires into the live B6 button.

**Path target for the disabled-button rows:** legacy backup says A1 → `docs/project/submissions/510k/cover-letter.md` etc. Those files don't exist yet. The B6 Create Draft workflow is the authoring mechanism — clicking Create Draft creates `_drafting/Q4-cover-letter-<timestamp>.md` in a worktree-backed session that ff-merges back.

**Dashboard delta:** +5-12 Q rows, several with live Create Draft buttons. QSub phase finally has substantive content.

### Stage 4 — Author `docs/project/submissions/pccp/composition-manifest.md`

**Lift:** medium. Folder `pccp/` exists; no manifest.

**Content sources:** backup `## Part 2.1 PCCP Core` (PC1-PC6), `## Part 2.4 PCCP Support Documentation` (PS1-PS5), `## Part 2.5 AI/ML-Specific Documentation` (AI1-AI6) — 17 rows total.

**Pattern:** same as Stage 3 — manifest tables with Tracker Row IDs, plus user-rows entries for any narrative pieces that need Create Draft buttons. The PC/PS/AI rows are MOSTLY pointing at DHF evidence files under `docs/project/dhfs/pca-device/design-controls/pccp/` (per legacy) — so these are more "manifest entries that bind to existing evidence" than "Create Draft narrative pieces."

**Decision:** which PC/PS/AI rows are (a) data-driven (manifest binds to DHF evidence) vs (b) narrative-authored (needs Create Draft). Recommend: PC1 (PCCP Cover Section) + PC4 (PCCP Performance Criteria narrative) + maybe AI1 (AI/ML Model Description narrative) → user-rows with Create Draft. Rest → manifest entries pointing at DHF evidence paths.

**Dashboard delta:** +17 PCCP-area rows, 510k+PCCP phase substantially populated.

### Stage 5 — Expand `regulatory.yml` milestone bindings + add Suite architecture_name + version pinning

**Lift:** medium-low. Project-data fix on the existing `regulatory.yml`.

**Three sub-fixes (already in this task's existing Phase 1 todos):**
1. Add `architecture_name: Suite` to pca-device entry in `project.yml` → scope column renders `Suite` instead of `pca-device`
2. Change milestone version bindings from `v1.0/v1.1/v1.2` per-version to either `version: current` (uniformly) or extend the matching logic → all 4 milestones' rows get resolved file paths (currently only QSub does)
3. Add additional doc bindings to walk Cybersecurity, HF, RM, SW, CL files where they exist in `docs/project/dhfs/pca-device/design-controls/{cybersecurity,usability,risk-management,software,clinical}/` → emits CY/HF/RM/SW/CL rows from DHF evidence walks

**Dashboard delta:** every existing row gets a working path; new technical-deliverable rows appear; scope reads "Suite" everywhere instead of "pca-device".

**Downstream concern (largest in this stage):** the legacy backup has hand-curated FDA REF citations per row (e.g. `21 CFR 807.87`, `FDA PCCP General §IV.A`, `IEC 62304 §5.5`). The generator currently emits REF column as `—` (empty). To preserve these, either:
- Author REF strings into each binding entry in `regulatory.yml` (skill change needed — REF emission from milestone bindings)
- Author REF strings as front-matter `ref:` on each DHF evidence file → generator reads file frontmatter
- Author REF strings into per-row entries in the `tracker-user-rows.yml` (works today; manual upkeep)
- Defer REF emission as an upstream-pushable improvement

Recommend defer for now (Stage 5 just gets paths working). Mark REF emission as Phase 3 work in this task.

### Stage 6 — Run `/tracker enrich-help` + `/tracker enrich-details`

**Lift:** medium (LLM-driven).

`/tracker enrich-help` builds `submission-tracker.help.json` — populates the `(?)` panel with "What is X / Why it matters / Main topics" content per row. Sister's sample row Q1 panel:
```
<h4>What is Q1?
<h4>Why it matters in this project
<h4>Main topics
```

`/tracker enrich-details` builds `submission-tracker.details.json` — populates the `(i)` panel with structured Phase/Scope/Path/Primary REF/All applicable REFs/Notes blocks per row. Sister has 1 `details.json` driving the (i) info-row content.

Both actions invoke subagents via the existing infrastructure; estimated cost ~50-150K tokens combined for the row inventory after Stages 2-5 land.

**Dashboard delta:** every row's expand-panel becomes rich. Two icon-buttons next to each row id come alive.

### Stage 7 — Run `/tracker assess`

**Lift:** medium (LLM-driven).

Produces `submission-tracker.agent.json` → populates the AI Status column with per-row regulatory-affairs verdict. Sister has this and it's why their AI Status column renders content.

**Dashboard delta:** AI Status column populates.

## Downstream Dependency Inventory (file paths the rows would reference)

Drafted from a scan of the legacy backup's `Project Location` column. ✗ = does not currently exist; ✓ = exists.

| Path category | Sample paths | Count | Existing? |
|---|---|---|---|
| `docs/project/submissions/510k/` narrative | `cover-letter.md`, `510k-summary.md`, `indications-for-use.md`, `truthful-accuracy.md` | ~4 | ✗ — all TBD via Create Draft |
| `docs/project/submissions/qsub/` narrative | (if we author Q-rows) | ~4-5 | ✗ — TBD via Create Draft |
| `docs/project/submissions/pccp/` narrative | `pccp-cover.md`, etc. | ~2-3 | ✗ |
| `docs/project/dhfs/pca-device/design-controls/pccp/` | `cover.md`, `modifications.md`, `protocol.md`, `performance-criteria.md`, `monitoring-plan.md`, `governance.md` | ~6 | mix — check |
| `docs/project/dhfs/pca-device/design-controls/cybersecurity/` | various | ~21 | mix — check |
| `docs/project/dhfs/pca-device/design-controls/risk-management/` | various | ~8 | likely partial |
| `docs/project/dhfs/pca-device/design-controls/software/` (or `/architecture/`) | various | ~19 | likely partial |
| `docs/project/dhfs/pca-device/design-controls/usability/` | various | ~8 | likely partial |

Conclusion: **most narrative-row file paths do not exist yet**, but that's not a hard block — rows render correctly with Status = Not Started + empty Evidence column. The B6 Create Draft workflow is the intended authoring path that will populate these files over time.

The **real** downstream concern is **ENG-row gates referencing technical-deliverable rows that don't exist as rows yet** (RM2a, SW3a, CY2a, etc.). Those need actual rows in the tracker for the gate references to be meaningful. Stage 5's expanded milestone bindings + the technical-deliverable rows from DHF evidence walks are what populate them.

## Concrete Sister-Side Patterns to Mirror (added 2026-05-11 via ben/048 #12)

A side-by-side `/dashboards/submission-tracker` comparison with the arthrex/pccp sister project confirmed the skill renders identically on both sides (same 11-column template, same code path). All visible differences trace to project-side inputs missing from our project. The sister has 123 rows / 19 structural sections / 5 live Create Draft buttons / populated AI Status column / rich (?)(i) info-panels; ours has 44 rows / 4 sections / 0 Create Draft buttons / empty AI Status / empty info-panels. Concrete inputs to mirror, in roughly priority order:

| Sister has | We're missing | Effect when added | Pipeline |
|---|---|---|---|
| `docs/project/milestones/engineering.yml` | ✗ | 10 `ENG1-ENG10` rows + Engineering Prerequisites section | Generator reads it natively |
| `docs/project/milestones/regulatory.md` + `README.md` | ✗ | Narrative context next to the catalog | Authored content |
| `docs/project/submissions/qsub/composition-manifest.md` | ✗ (folder exists, manifest doesn't) | ~12 `Q1-Q12` rows incl. cover letter / device description / indications / predicate analysis / PCCP summary | Generator reads it |
| `docs/project/submissions/pccp/composition-manifest.md` | ✗ (folder exists, manifest doesn't) | Richer 510k+PCCP phase rows | Generator reads it |
| `docs/project/submissions/tracker-user-rows.yml` | ✗ | Hand-authored rows incl. ones with `<button class="tracker-action-btn" disabled>Create Draft</button>` placeholders in the Path cell that `render.py` rewrites into live B6 buttons | `/tracker add-row` action (Model D) |
| `docs/project/submissions/submission-tracker.help.json` | ✗ | "What is X / Why it matters / Main topics" content in `(?)` info-rows | `/tracker enrich-help` action |
| `docs/project/submissions/submission-tracker.details.json` | ✗ | Structured Phase/Scope/Path/Primary REF/All applicable REFs/Notes blocks in `(i)` info-rows | `/tracker enrich-details` action |
| `docs/project/submissions/submission-tracker.agent.json` | ✗ | Populated AI Status column | `/tracker assess` action |
| Hand-authored structural sections (Status/Scope/Phase/Effort/REF Priority Legends; Cross-Milestone Summary; Notable Findings; Reviewer Sign-off; Changelog) | ✗ | Surrounding chrome the renderer expects | Author-managed, append directly to `submission-tracker.md` (sister keeps these stable across generator runs by hand-edit; long-term: candidate-for-upstream emitter additions) |
| Validation report (`submission-tracker.validation-report.md`) | ✗ | Audit trail for generator vs canonical drift | `python3 generate.py --validate` (read-only) |

The ben/047 todos already capture most of these; this table makes the sister's exact pattern explicit so we can mirror filenames + schemas rather than reinvent.

## Known Gaps vs. Legacy 118-Row Demo Depth

Documented in task ben/044 (`### Generator output gap vs. original tracker`) and confirmed against the current generator dry-run:

| Gap | Current state | What it needs |
|---|---|---|
| Only QSub milestone rows have resolved paths | 11 rows have paths, 33 are blank | Either change all milestone bindings to `version: current` OR extend `version: v1.0/v1.1/v1.2` matching logic in `generate.py`. Hitting the version-matching logic is more correct long-term but pushes into upstream. |
| Scope renders as `pca-device` instead of `Suite` | All 44 rows show scope `pca-device` | Add `architecture_name: Suite` to the pca-device DHF entry in `project.yml`. Project-data fix; no skill change. |
| Engineering Prerequisites section missing entirely | 0 rows | Author `docs/project/milestones/engineering.yml` (the upstream skill reads this — see `tracker/SKILL.md` "Plan layer"). Project-data fix. |
| (submission)-scope rows missing — no cover letter, narrative, predicate analysis, PCCP narrative | 0 rows of `scope: (submission)` | Expand `docs/project/submissions/510k/composition-manifest.md` (and any other phase composition manifests) with submission-narrative entries. Project-data fix. |
| Other DHFs (connectivity-adapter, cloud-suite + 7 children) not represented | 0 non-pca-device rows | Either extend milestone bindings to target additional DHFs OR accept pca-device-as-headline framing. Project-data fix; design decision. |
| Per-row REF citations are empty `—` | Generator doesn't populate REF | Upstream improvement to generator — either author REF in source markdown convention or wire REF resolution into the milestone catalog. Skill change candidate. |
| No legends, Cross-Milestone Summary, Reviewer Sign-off, Changelog | Generator emits only row tables | Upstream improvement to generator. Skill change candidate. |

## Todos

Phase 1 — Cheap project-data wins (no skill changes; can ship to demo today)
- [ ] Add `architecture_name: Suite` to pca-device entry in `project.yml`; regenerate tracker; confirm scope column reads `Suite`
- [ ] Decide milestone-binding strategy (uniform `version: current` vs. per-version) and update `regulatory.yml`; regenerate; confirm all 44 rows have paths
- [ ] Author `docs/project/milestones/engineering.yml` with the Engineering Prerequisites the legacy tracker had (~20 rows); regenerate; confirm Engineering Prereqs section appears
- [ ] Expand `docs/project/submissions/510k/composition-manifest.md` with cover-letter / narrative / predicate-analysis / PCCP narrative entries to drive (submission)-scope rows
- [ ] (Optional) Add a QSub composition manifest at `docs/project/submissions/qsub/composition-manifest.md` if QSub bindings need their own snapshot

Phase 2 — B6 Create Draft surface validation
- [ ] Identify which rows the upstream renderer marks Create Draft–eligible and exercise the workflow end-to-end on at least one (`/workflows/tracker-draft/<row_id>` → propose → synthesize → save)
- [ ] Confirm the worktree lifecycle (`draft_session.py` / `draft_writer.py`) works inside this repo's git layout
- [ ] If the per-row eligibility rule is too narrow, broaden via project-data or open an upstream issue

Phase 3 — Upstream-pushable skill improvements (post-Phase-1 baseline)
- [ ] REF-column population: design a project-data convention (REF declared in milestone catalog? in composition manifest? in DHF frontmatter?) and prototype generator support; push upstream if generic enough
- [ ] Structural sections (legends, Cross-Milestone Summary, Reviewer Sign-off, Changelog) — append-only emitter additions in generate.py; push upstream
- [ ] (Stretch) Revisit the v16/v17 taxonomy work in the archive — anything still worth resurrecting on the new baseline?

## Background / Why This Task Exists

Task ben/044 attempted a tracker recovery via a three-layer taxonomy refactor that grew into substantial skill modifications (v16, v17 — `init-taxonomy`, `classify-folders`, `assess-phases`, `reconcile-taxonomy`, plus a TIER-2 agent fan-out pattern). The work diverged from the upstream skill registry and produced a candidate dashboard with only 44 rows vs. the 118-row legacy canonical — substantially less demo depth.

On 2026-05-11, during a routine `/sync-skills pull`, upstream landed the B6 Create Draft workflow (hitachi PR #143) which touched `tracker/scripts/render.py` and added significant new project-console + tracker pieces. Merging upstream's B6 against the local v17 fork was tractable for `render.py` (one helper + one CSS block + one call-site wire-up) but the broader divergence meant the local fork would only grow and never push back upstream cleanly.

User decision: reset to upstream baseline, archive the local WIP for reference, drive improvements from project-data and small upstream-pushable changes instead of carrying a local skill fork.

## Resume Command

```bash
bash .claude/hooks/task-activate.sh add <UUID-from-printenv-or-denial> 047
```

## Changelog

- 2026-05-11: Task created. Captures the reset-to-upstream decision and the priority-ordered improvement backlog. Predecessor task 044 (Tracker Console Redesign Recovery) closed out; v16/v17 skill WIP + sidecars + legacy canonical archived to `tasks/ben/044/archive/wip-dropped-2026-05-11/`.
- 2026-05-11: Enriched with concrete sister-side patterns to mirror (table added above the Known Gaps section). Side-by-side `/dashboards/submission-tracker` comparison with arthrex/pccp confirmed the skill renders identically on both projects — every visible delta (44 rows vs 123, 4 sections vs 19, 0 Create Draft buttons vs 5, empty vs populated AI Status / (?)(i) panels) is project-data input volume, not skill bespoke-ness. The sister already has the milestone catalog files, composition manifests, user-rows registry, and three enrichment sidecars (help/details/agent) populated; we have only the regulatory.yml and a single composition manifest. Surfaced via ben/048 #12.
- 2026-05-11: **Drafted full 7-stage recovery plan** (see new § "Full 7-Stage Recovery Plan" above). Each stage names target files, content sources from the legacy 79-row backup, schema references from the sister, expected dashboard delta, and known downstream-dependency concerns. Pending user review of the plan-as-a-whole before any project-data writes begin.
- 2026-05-12: **Stage 1 (structural chrome) — first attempt, then wiped + reconstructed.** First attempt: hand-authored `submission-tracker.md` with Context & Sources / legends / Two-Level Model / Scale tables / Cross-Milestone / Reviewer Sign-off / Changelog (44 rows preserved). Worked. Then ran `/tracker generate --md --write-canonical` (Stage 2 follow-on) which is the v11-documented destructive path — wiped all chrome. User redirected to "use skills that own the generation" and `/tracker init` semantics. Reconstructed cleanly: applied phase-naming fix (regulatory.yml: `510(k)+PCCP Release` → `510k+PCCP Release` to match sister), added `tracker.display.phase_label_overrides` to project.yml so ENG rows render `510k+PCCP` / `LMR2` instead of milestone IDs (workaround for generate.py:248 bug), ran `/tracker generate --candidate` to produce a correctly-labeled row-table artifact, composed canonical from init scaffold spec + candidate row tables. Final state: 64 rows / 4 phases / scales-grid / 7-status legend / all chrome restored. Dashboard 112KB.
- 2026-05-12: **Stage 2 (engineering.yml) done.** Authored `docs/project/milestones/engineering.yml` with all 20 ENG rows from the archived legacy backup, split into two engineering milestones: `engineering-pccp-release` (ENG1–ENG18; prereq `pccp-release`) and `engineering-lmr2-release` (ENG19–ENG20; prereq `lmr2-release`). Phase column distribution matches the legacy intent: ENG1–18 → 510k+PCCP, ENG19–20 → LMR2 (AI/ML envelope). Cross-Milestone Summary updated to show 64 total rows.
- 2026-05-12: **Status column aligned to evidence-on-disk via overlay.** Rule: a row whose `path:` resolves to a real document (markdown link, not `—`) is at minimum status `Drafting` — "evidence exists, therefore work has begun." Applied via overlay script: scanned all 132 catalog-derived rows; for any row where `path` starts with `[` (real-file link) AND status is `Not Started` (or absent → defaults to Not Started), bumped status to `Drafting`. Left alone: rows already past `Not Started` (Drafting / Drafted / etc.), rows with `path: "—"` (no real evidence), and `N/A` rows (the out-of-scope decision wins over evidence existence — e.g., `Q-CA25` has a real `user-needs-register.md` linked but stays N/A because user-needs is out of scope for MDDS). **45 rows bumped Not Started → Drafting.** Final dashboard status distribution: 70 Not Started / 52 Drafting / 32 N/A. Implementation note: initial regex-substitution attempt accidentally stripped the trailing `:` from 45 row-ID lines (the `:` was outside the captured group); fixed with a follow-up `re.sub` that re-added the colon. YAML now parses clean.

- 2026-05-12: **Deliverable names harmonized for CA / CS rows.** Pattern: `<Scope> <RoleLabel>` short-prefix form, replacing both the generator's folder-name fallbacks (e.g., `user-needs` → "Adapter User Needs") and the earlier longer-form names ("Connectivity Adapter SAD" → "Adapter SAD"). Also dropped the `— LMR1/LMR2 Refresh` suffix on architecture + cybersecurity rows since the Phase column already carries that info. 88 CA/CS rows × 4 phases renamed via overlay; pca-device names left as-is (already descriptive). Unique name set: 22 distinct ("Adapter SAD" / "Cloud SAD" / "Adapter User Needs" / "Cloud User Needs" / etc., 11 roles × 2 DHFs).

- 2026-05-12: **Path column fully repaired via overlay `path:` overrides.** User reported clicks "lead nowhere." Root cause: (a) `render.py::rewrite_url()` (lines 120-139) treats `[label](docs/project/dhfs/...)` as relative to the canonical markdown's directory (`docs/project/submissions/`), so every rewrite double-prefixes to `/documents#path=docs/project/submissions/docs/project/...` — broken in the Documents tab. (b) `discover_system_dhf_evidence()` (generate.py:659) picks alphabetical-first non-README `.md`, so `GL-TMP-DC-002-design-input-specification.md` shadows the real `design-inputs.md` (alphabetical order); every Path was linking to a template scaffold instead of authored content. **Overlay-only fix shipped** (no skill code change): authored `/tmp/inventory_evidence.py` to classify every (DHF × role) folder's `.md` files as `real` / `sop` / `template`, then `/tmp/build_path_overlay.py` to regenerate `submission-tracker.overlay.yml`'s `rows:` section with a `path:` override per catalog-derived row. URL format `[<filename>](/documents#path=<project-relative-path>)` — the leading `/` trips render.py's `url.startswith('/')` short-circuit at line 132 so the bad double-prefix path is skipped entirely. **Result: 68/132 rows link to real evidence (17 evidence pairs × 4 phases); 64/132 render `—`** for roles whose only content is GL-TMP scaffolding. Zero `GL-TMP-*` links remain in the rendered HTML. Existing curated overlay fields (`name`/`status`/`effort`/`ref`/`owner`/`notes`) preserved end-to-end through the rewrite.

<!-- LESSONS LEARNED: skill-render -->
`render.py::rewrite_url()` resolves relative links against `src_dir` (the canonical markdown's directory) rather than the project root, so any `[label](docs/project/...)` written into a tracker md outside `docs/project/submissions/` gets double-prefixed in the dashboard. Workaround: in the overlay, write paths pre-rewritten as `[label](/documents#path=<project-relative>)` — the leading `/` short-circuits the rewriter via `url.startswith('/')` at line 132. Permanent fix is a render.py change to detect project-root-relative paths (e.g., any path starting with `docs/` resolves from `project_dir`, not `src_dir`). Push to upstream when 047 Phase-3 batch ships.
<!-- /LESSONS LEARNED -->

<!-- LESSONS LEARNED: skill-generator -->
`generate.py::discover_system_dhf_evidence()` picks the alphabetically-first non-README `.md` as the canonical row Path. `GL-TMP-*` template scaffolds win against real authored content (`design-inputs.md`, `user-needs-register.md`, etc.) by alphabetical order. Workaround: per-row `path:` override in the overlay. Permanent fix: rank files by classifier (real > SOP > template) before picking the canonical. Same upstream batch as the rewrite_url fix.
<!-- /LESSONS LEARNED -->

- 2026-05-12: **Multi-DHF expansion — connectivity-adapter (MDDS) + cloud-suite (non-medical dep) added to tracker.** Previously the tracker only walked `pca-device`; the architecture has two more DHFs that didn't appear at all. Three coordinated changes: (a) `project.yml` — added `architecture_name: Adapter` to connectivity-adapter, `architecture_name: Cloud` to cloud-suite (drives Scope column display), added `mdds: true` classification flag + `class: I` on connectivity-adapter, and added explicit `tracker.row_id_schema.dhf_prefix_map: {pca-device: PC, connectivity-adapter: CA, cloud-suite: CS}` so row IDs stay readable (otherwise fallback first-2-letters would give "CO"/"CL"). (b) `regulatory.yml` — added a second + third binding per milestone (`dhf: connectivity-adapter` `required: true`, `dhf: cloud-suite` `required: false`) — 8 new bindings total (2 DHFs × 4 milestones). (c) `submission-tracker.overlay.yml` — added 88 new row entries (11 roles × 4 phases × 2 DHFs): 56 applicable (effort + ref + friendly name) and 32 marked `status: N/A` for the trimmed roles. **Trim mechanism — overlay-only**, since the upstream generator walks the full system-DHF role map (`SYSTEM_DHF_ROLE_MAP`) for every DHF with no per-DHF allowlist; physically removing folders would be lossy. Trimmed roles for both connectivity-adapter and cloud-suite: `user-needs`, `tool-validation`, `clinical`, `postmarket`. Rationale: MDDS (21 CFR 880.6310) has no clinical UI / no Class-C tooling / no clinical claims / postmarket folds into parent PSUR; cloud-suite is non-medical, so the same set is N/A (its inclusion in the tracker documents the dependency contract — architecture / SBOM / storage / OTA — not clinical evidence). Hand-merged candidate row tables into canonical via `/tmp/merge_tracker.py` preserving chrome + (submission) subsections. Dashboard: **174 rows total** (154 deliverable + 20 ENG), 296 KB; status breakdown 115 Not Started + 7 Drafting + 32 N/A; phase counts QSub 38 / 510k+PCCP 44 / LMR1 33 / LMR2 39.

<!-- STRATEGY CONTENT: architecture, regulatory, multi-dhf-scope -->
Multi-DHF scope decisions locked in:
- **pca-device (Class II SaMD/SiMD, K210345 anchor)** — full 11 canonical roles per phase.
- **connectivity-adapter (MDDS, 21 CFR 880.6310, Class I exempt from 510(k))** — 7 applicable roles (architecture, plans, requirements, vnv, trace-matrix, risk-management, cybersecurity). MDDS is exempt from premarket review but **still under 21 CFR 820.30 design controls**, so the design-controls evidence still ships; cyber per FDA cyber guidance is required.
- **cloud-suite (non-medical)** — 7 applicable roles, identical to MDDS. Cloud-suite itself isn't a medical device but PCA + adapter depend on it for architecture context, SBOM, storage encryption, and OTA / device-management — those dependencies must be documented in the submission, hence the rows. The trim rationale matches: no clinical/UN/tools/postmarket.

**Mechanism gap surfaced**: the upstream tracker generator has no per-DHF role allowlist — `SYSTEM_DHF_ROLE_MAP` is global. Trimming via overlay-N/A is the current project-data-only workaround. Long-term upstream improvement candidate: `dhfs[].tracker_roles: [list]` in project.yml, generator filters role map per DHF. Adds value for any sister project with MDDS / non-medical / accessory DHFs alongside the main system DHF.
<!-- /STRATEGY CONTENT -->

- 2026-05-12: **Effort column fully populated via overlay.** Filled the remaining 27 deliverable rows in `submission-tracker.overlay.yml` (3 QSub gaps — Q-PC26/Q-PC28/Q-PC16; 6 510k+PCCP — PC26/PC2/PC28/PC16/PC23/PC24; 9 LMR1 — all roles except PC1/PC9; 9 LMR2 — all roles except PC1/PC9). ENG rows continue to source effort from `engineering.yml` bindings (V.High → Low scale). Calibration heuristic: QSub readiness rows lean Med–V.High (first-draft cost); 510k+PCCP rows match QSub for new-content roles (architecture/requirements/vnv/risk/clinical); LMR1 rows lean Low–Med (refresh-only); LMR2 mirrors LMR1 except `L2-PC27` V.High and `L2-PC23` High (AI/ML envelope adds material effort). Each new entry also carries an authoritative `ref` citation (FDA sw-functions, IEC 62366-1, IEC 62304, ISO 14971, GMLP). Overlay row count: 44/44 deliverables now have effort; YAML parses clean; no changes to generator output (overlay applies at render time only — no `generate.py --write-canonical` invoked).

<!-- STRATEGY CONTENT: development, effort-calibration -->
Effort calibration heuristic locked in for the PCA tracker: (a) QSub-phase rows that produce a first draft of a regulated artifact (architecture, requirements, V&V, clinical) are High–V.High; (b) plans/trace-matrix/tool-validation/postmarket lean Med because they're checklist-y or template-driven; (c) LMR1 refresh-cycle rows step down one tier from their QSub/PCCP counterparts (architecture High not V.High, plans Low not Med, etc.); (d) LMR2 mirrors LMR1 with a deliberate bump on V&V and clinical to absorb the AI/ML envelope cost. This is the de-facto calibration scale — replicate it in sister projects rather than re-deriving per row.
<!-- /STRATEGY CONTENT -->

- 2026-05-12: **Stage 5c (unified overlay sidecar) done — upstream-shipped, supersedes 5b.** User feedback on 5b: "we just extended the friendly name, why didn't we use the same overlay file to store the deliverable description?" — plus the sharper insight that **per-row title flexibility** ("System SAD — Draft" vs "System SAD — Final") is the right primitive, with per-(DHF, role) just an optional default. Also asked about `path` field (overrideable too — lets you flip a row in/out of the B6 Create Draft workflow per-row). Rebuilt: dropped `submission-tracker.deliverable-names.yml` in favor of a unified `submission-tracker.overlay.yml` with two sections — `defaults.by_dhf_role.<dhf>.<role>` (generator-time name default, replaces 5b's deliverable-names) + `rows.<id>` (renderer-time per-row overrides for `name`/`status`/`effort`/`ref`/`path` plus metadata `owner`/`target_date`/`blockers`/`notes`). Closes the `effort` + `path` override gaps that the legacy `human.json` overlay didn't support. Pushed as hitachi PR #154; squash-merged at `735fc17` (atomic supersede of #153 since #153 had no downstream adopters; merged 30 min prior). Patch shape: ~85 LOC delta in generate.py + ~50 LOC in render.py. `render.py::load_human_overlay()` falls back to legacy `human.json` for back-compat. Tested locally end-to-end: defaults render (11 friendly names × 4 phases); per-row name override demoed on Q-PC9 ("Risk Management Report (Q-Sub readiness draft)") and L1-PC1 / L2-PC1 ("System SAD — LMR1 Release" / "System SAD — LMR2 Release"); status override flipped 7 rows to Drafting; effort badges populated (vhigh/high/med/low/unset); no-sidecar fallback test passed (clean defaults); legacy human.json test passed.
- 2026-05-12: **Stage 5b (deliverable-names sidecar) done — upstream-shipped.** Authored `docs/project/submissions/submission-tracker.deliverable-names.yml` (v0.1 schema, per-DHF × canonical-role mapping with `"*"` wildcard) listing the 11 friendly names for pca-device DHF. Patched `tracker/scripts/generate.py` (+60 lines, -0 lines, 3 hunks): added `DELIVERABLE_NAMES_REL` constant, `load_deliverable_name_overrides()` + `lookup_friendly_name()` helpers (precedence: specific DHF > "*" wildcard > fallback), wired the lookup into `generate_rows()` at the system+external evidence-walk emission site. Tested locally (PDLC_DEMO renders friendly names) AND with sidecar absent (graceful fallback to folder.name; zero rows lost). Pushed upstream as hitachi PR #153; squash-merged at `faae97e`; local hitachi fast-forwarded. Sister picks up the sidecar contract on her next `/sync-skills pull`; her behavior unchanged until she authors her own sidecar. Sync log updated. Decision rationale captured in PR body: sidecar location wins over project.yml block due to locality (next to other tracker sidecars) + scoping (tracker-domain data, not general project config) + pattern consistency.
- 2026-05-12: **Stage 5 (project.yml + regulatory.yml fixes) done.** Three changes: (a) added `architecture_name: Suite` to the pca-device DHF entry in project.yml so generator-emitted rows render scope `Suite` instead of `pca-device`; this also flipped the per-phase subsection heading from `### pca-device` to `### Suite (system DHF, IEC 62304 Class C)`. (b) Changed all 4 milestone bindings in regulatory.yml from `version: v1.0`/`v1.1`/`v1.2` → `version: current` so every milestone walks the same on-disk evidence (was: only QSub resolved paths; LMR1/LMR2/510k+PCCP rows showed `_(no path)_`). Now **all 66 deliverable rows have resolved paths**, not just 11. (c) Confirmed the existing `doc_pattern: '**/*'` binding already walks the full DHF role tree (11 canonical roles per phase — architecture, plans, user-needs, requirements, vnv, trace-matrix, tool-validation, risk-management, clinical, postmarket, cybersecurity), broader than the legacy `CY/HF/RM/SW` split; no additional bindings needed at this time. Used a small Python merge script (12 lines) to splice the candidate's `### Suite` blocks into the canonical's `### pca-device` slots while preserving chrome + the (submission) subsections from Stages 3-4. Dashboard now 154 KB / 86 item-rows / 22 Create Draft buttons / all scope values resolved.
- 2026-05-12: **Stage 4 (PCCP narrative rows) done.** Authored 17 PCCP-area rows directly into canonical (same hand-author pattern as Stage 3 — sister's production approach): under `## Phase: 510k+PCCP / ### (submission)` added **PCCP1–PCCP6** (PCCP Core: Cover, Description of Modifications, Modification Protocol, Impact Assessment, Trace Table, Public Summary) + **PS1–PS5** (PCCP Support: Drug Library Update Protocol, Drug Library V&V, Drug Library Acceptance, Firmware Update Protocol, Firmware V&V); under `## Phase: LMR2 / ### (submission)` added **AI1–AI6** (AI-DSF Description of Modifications, AI Re-Training Practices, AI Data Management, AI Performance Evaluation, AI Update Procedures, AI Drift Monitoring Plan). **Renamed legacy `PC` prefix → `PCCP`** to avoid collision with generator-emitted `PC<n>` IDs from pca-device evidence walks. All 17 rows are Create Draft–eligible (Not Started status + disabled-button placeholder in Path cell). Cross-Milestone Summary updated. Render verified: 86 total rows (66 deliverable + 20 ENG), 22 live Create Draft buttons. Dashboard 146 KB.
- 2026-05-12: **Stage 3 (QSub narrative rows + Create Draft buttons) done.** Authored 5 new `(submission)`-scope rows directly into the canonical's QSub Phase section under a new `### (submission)` subsection: **Q4** Q-Sub cover letter, **Q5** Device description (Q-Sub formal), **Q6** Proposed indications for use, **Q7** Predicate device analysis (Q-Sub summary), **Q8** PCCP summary for FDA feedback. Each row's Path cell carries the literal `<button class="tracker-action-btn" disabled>Create Draft</button>` placeholder that `render.py::wire_create_draft_button()` rewrites into a live B6 button (row-id + data-action + click handler). Verified in rendered HTML: 5 buttons with `data-row-id="Q[4-8]" data-action="create-draft"` — matches sister-project count exactly. Tracker now: 69 rows / QSub phase=16 / dashboard 120KB. **Decision: skip `/tracker add-row` + `tracker-user-rows.yml` path** despite the SKILL.md preference. Reason: the action's step 6 (`generate.py --write-canonical`) wipes hand-managed chrome — the same v11-documented gap that bit Stage 2. Sister's tracker.md and tracker-user-rows.yml disagree about Q4-Q8 (their registry has older "Pre-Op SAD / Intra-Op SAD" bootstrap entries; their live canonical has the cover-letter / device-description / etc. entries), so sister's actual production pattern for narrative rows is hand-authoring into the canonical, NOT the registry. We're following her live pattern, not her bootstrap pattern.
- 2026-05-12: **Upstream-pushable parser/generator improvements surfaced during Stages 1+2 (logged here for Phase-3 batch PR):**
  - `render.py::parse_markdown()` doesn't reset `in_scale = None` when entering Phase / Eng / Details modes (lines 312, 320, 326). If `## Effort Scale` or `## Phase Scale` sits BEFORE `## Phase: <name>` sections, subsequent row tables are consumed as scale entries → 0 rows. Workaround: place Scale tables AFTER row sections (sister's pattern). Permanent fix: reset `in_scale = None` in the phase_h2 / eng_h2 / details_h2 handlers.
  - `generate.py::discover_engineering_rows()` line 248 passes `target_milestone_id` as both `ms_id` AND `ms_short` to `_phase_for_milestone()`, so ENG rows render the milestone id (`pccp-release`) instead of the short label (`510k+PCCP`) when no override is configured. Workaround: project.yml `tracker.display.phase_label_overrides`. Permanent fix: look up the matching milestone's `short_label` (or stripped `name`) from the catalog so ENG rows match deliverable rows' code path.
  - `generate.py --write-canonical` overwrites the entire canonical including hand-authored chrome (Context & Sources, Legends, Cross-Milestone Summary, Reviewer Sign-off, Changelog, Deliverable Details inline blocks, Scale tables). The v11 changelog already documents this cutover-readiness gap. Permanent fix: parse the existing canonical, preserve chrome sections, replace only the generator-owned row tables (per-Phase + Engineering Prerequisites). Workaround until then: never use `--write-canonical`; always `--candidate` + hand-merge.
