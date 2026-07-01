# 044 — Submission Tracker Console Integration Recovery

**ID**: 044
**Created**: 2026-05-05
**Closed**: 2026-05-11
**Status**: Complete (closed via reset-to-upstream; follow-up tracked as ben/047)
**Created By**: Ben Xavier
**Owner**: Ben Xavier
**Priority**: High

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

Address the broken submission package tracker data population in the project-console console following major architectural changes in v1.7.6 → v1.9.0 (asset cards, unified viewer, consolidated button bar).

- Understand root cause of tracker data not populating in the console dashboard
- Identify what changed in project-console that broke tracker integration
- Repair or rebuild the tracker data pipeline
- Verify submission-tracker dashboard renders correctly in the console
- Document changes to sync-log

## Todos

- [ ] Investigate project-console v1.9.0 changes and their impact on tracker dashboard discovery
- [ ] Examine how dashboards are discovered and rendered in current console version
- [ ] Check if tracker skill needs updates for the new console architecture
- [ ] Rebuild/regenerate tracker data if needed
- [ ] Test tracker dashboard rendering in console
- [ ] Update sync-log with findings and resolution

## Background

**Recent skill changes:**
- project-console: v1.7.6 → v1.9.0 (assets cards, unified viewer, consolidated buttons)
- tracker skill exists but data isn't populating in console
- submission-tracker.html exists at `docs/project/submissions/submission-tracker.html`
- console.yaml references submission-tracker dashboard with pattern matching

**Observed issue:**
- Submission package tracker shows no data when accessed via console
- HTML file exists and has 445 lines of content
- Dashboard should match patterns: `docs/**/*-tracker.html`

## Investigation Findings

### Phase 1: File & Discovery System Check

**File Status**: ✅ `docs/project/submissions/submission-tracker.html` exists (445 lines)
- Contains complete HTML dashboard with CSS, controls, summary cards, progress bars, and data tables
- Data shows: 74 Base 510(k) items, 17 PCCP items, 7 Mgmt Services items, 20 Engineering items
- Generated: 2026-04-14 (stale, needs rebuild via `/tracker render`)

**Discovery System**: ✅ Works correctly
- Pattern `docs/**/*-tracker.html` in `console.yaml` correctly matches the tracker file
- Discovery.py extracts title from HTML `<title>` tag and description from meta tags
- Dashboard slug correctly generated as `submission-tracker` (from filename stem)

**Console Router Integration**: ✅ Code present
- dashboards/router.py correctly routes to special interactive handler for `submission-tracker` slug
- Calls `_tracker_embed_fragment_for_actor()` to render submission tracker content
- Renders via `dashboard_view.html` template with interactive=True flag

**Tracker Render Module**: ✅ Located and callable
- `.claude/skills/tracker/scripts/render.py` exists (1292 lines)
- Contains required `render_embed_fragment()` function at line 1274
- Function wraps `render()` with `embed=True` parameter

### Phase 2: Root Cause Hypothesis

The tracker HTML file and discovery system are both fine. The issue is likely:
1. **Tracker HTML is stale** (last generated 2026-04-14, task creation date 2026-05-05 = 21 days old)
2. **Tracker render may fail** on missing submission-tracker.md or malformed markdown structure
3. **Console asset card redesign** (v1.9.0) may have altered dashboard routing or template rendering

### Phase 3: Root Cause Identified ❌

**THE PROBLEM**: Structural markdown format incompatibility

- `submission-tracker.md` uses **Part-based structure** (Part 1, Part 2, Part 3...)
- Tracker render.py expects **Phase-based structure** (`## Phase: Filing`, `## Phase: Release 1`, etc.)
- The render script searches for `## Phase:` regex match and finds ZERO matches in the current markdown
- Result: render script outputs "rows: 0" and generates empty dashboard HTML
- HTML file exists but is orphaned/stale (generated 2026-04-14, no data)

**EVIDENCE**:
- `/tracker render` produces zero rows: `rows: 0 · eng: 0 · details: 0; phases: {}`
- render.py line 205: `phase_h2 = re.compile(r'^## Phase:\s*(.+?)\s*$')`
- submission-tracker.md line 76+: `## Part 1 — Base 510(k) Requirements` (no "Phase:" in heading)

### Phase 4: Solution Path

The markdown structure must be rebuilt to match the Phase-based schema. Options:

1. **Use `/tracker generate`** (if available) — regenerate tracker from composition manifest + DHF evidence
2. **Reformat manually** — convert Part 1/2/3 sections to Phase: Filing / Release 1 / Release 2 structure
3. **Check if tracker schema changed** — render.py may have been updated but markdown wasn't migrated

**Next step**: Check if tracker skill has a `generate` or `build` action that can rebuild the markdown from source

---

## Summary & Findings

### Root Cause: Markdown Structure Incompatibility

The submission package tracker data **is not showing in the console** because the tracker.html file is empty (rows: 0) due to a structural incompatibility between:

- **`submission-tracker.md`** — uses **Part/Subsection** headers: `## Part 1 — Base 510(k)` → `### 1.1 Admin`
- **`render.py`** — expects **Phase-based** headers: `## Phase: Filing` → `### Subsection`

The render script cannot parse the markdown and generates empty HTML. The console dashboard discovery works fine; the rendering just produces no data.

### Architectural Context

- **project-console v1.9.0 redesign** (asset cards, unified viewer) doesn't affect tracker — the issue predates this redesign
- **tracker HTML file** (23KB) exists but is orphaned with stale generation date (2026-04-14)
- **tracker markdown file** exists (28KB, valid content) but wrong structure
- **tracker render script** is strict about `## Phase:` pattern matching

### Resolution Required

The `submission-tracker.md` must be restructured from Part-based to Phase-based organization. This is a significant structural change affecting all 118 rows across 4 sections.

Two paths forward:
1. **Automated conversion** — write a script to reorganize markdown by Phase (Filing, Release 1, Release 2, R2 PCCP)
2. **Manual rebuild** — use `/tracker build` or regenerate from composition manifest

Neither requires changing project-console — the console works fine once the markdown is fixed.

## Changelog

**2026-05-11 (CLOSED — reset to upstream baseline)**
- During a routine `/sync-skills pull`, upstream landed B6 Create Draft workflow (hitachi PR #143) touching `tracker/scripts/render.py`. The v16/v17 local fork (init-taxonomy + classify-folders + assess-phases + reconcile-taxonomy actions, plus the phase-mapper / folder-classifier agents and taxonomy.py) had diverged enough that maintaining a local fork was no longer the right shape.
- User decision: drop the local WIP, take upstream `origin/main` as canonical for the tracker skill, regenerate the project's submission tracker from upstream v11's generator against the existing milestone catalog.
- Actions taken:
  - Archived all v16/v17 skill WIP (15 files: actions, agents, schemas, scripts) to `tasks/ben/044/archive/wip-dropped-2026-05-11/skill/`
  - Archived all v16/v17 project artifacts (candidate md+html, aggregates/gaps/help/phase-map/row-source sidecars, tracker-user-rows.yml, pca-device .taxonomy.yml, legacy backup+preinit canonicals) to `tasks/ben/044/archive/wip-dropped-2026-05-11/project-artifacts/`
  - Pulled clean `tracker/{SKILL.md,README.md,scripts/generate.py,scripts/render.py}` from `origin/main`, plus new B6 pieces (`agents/draft-author.md`, `scripts/build-draft-context.py`, `tests/test_create_draft_wiring.py`) and the project-console draft workflow (`workflows/draft_*.py`, `web/templates/workflow_tracker_draft.html`, `tests/test_draft_workflow_e2e.py`) and the `tracker_interactive.js` / `assistant.js` / `router.py` updates
  - Synced project-console scaffold to skill 1.17.0
  - Regenerated `submission-tracker.md` (5.8KB / 52 table rows) and `submission-tracker.html` (24.7KB / 44 item rows / 6 Create Draft buttons) via upstream v11 generator
- Outcome: console boots clean on `http://127.0.0.1:8765`, tracker dashboard renders 44 rows with live B6 buttons. Demo depth regression (44 rows vs the 118-row legacy) is captured in task **ben/047** for follow-up via project-data and small upstream-pushable improvements.
- Follow-up: `tasks/ben/047-tracker-upstream-baseline-improvements.md`.

**2026-05-05 (P1 build complete — taxonomy-driven evidence discovery)**
- Shipped tracker skill v12: two new actions (`init-taxonomy`, `reconcile-taxonomy`), schema v0.3 (additive over Arthrex v0.2), top-level `project.yml.taxonomies[]` registry, generator integration with hardcoded fallback preserved.
- New artifacts:
  - `.claude/skills/tracker/schemas/taxonomy.schema.yml`
  - `.claude/skills/tracker/scripts/taxonomy.py` (resolver + scanner + reconcile lib)
  - `.claude/skills/tracker/scripts/init_taxonomy.py`
  - `.claude/skills/tracker/scripts/reconcile_taxonomy.py`
  - `.claude/skills/tracker/actions/init-taxonomy.md`
  - `.claude/skills/tracker/actions/reconcile-taxonomy.md`
  - `.claude/skills/tracker/.gitignore` (`__pycache__/`)
- Modified:
  - `.claude/skills/tracker/SKILL.md` — added `init-taxonomy`/`reconcile-taxonomy` action sections and the registration model
  - `.claude/skills/tracker/README.md` — v12 changelog
  - `.claude/skills/tracker/scripts/generate.py` — `discover_system_dhf_evidence()` tries resolver first, falls back to hardcoded `DEFAULT_SYSTEM_DHF_ROLE_MAP`
  - `project.yml` — new `taxonomies:` block (auto-added by init); Caveat: PyYAML round-trip stripped comments throughout — file is functional but lost inline rationale.
- Generated:
  - `docs/project/dhfs/pca-device/.taxonomy.yml` — 65 mapped, 2 pending (design-review-log, pccp-predetermined-change-control-plan), 0 broken refs
- Smoke tests:
  - `init-taxonomy --dhf pca-device`: ✅ 65 mapped, 3 pending (1 leaked: README.md — fixed inline by adding root-level `README.md`/`readme.md` to DEFAULT_EXCLUDES)
  - `reconcile-taxonomy --dhf pca-device`: ✅ mapped=65, on_disk=67, +pending=0, broken=0
  - `/tracker generate --dry-run` with taxonomy: 260 rows (65 × 4 milestones)
  - `/tracker generate --dry-run` without taxonomy (file moved aside): 44 rows (11 × 4 milestones — confirms hardcoded fallback intact)
  - Sister project: Arthrex's `hiplink-suite` has no taxonomy → resolver returns None → hardcoded walk runs → unchanged behavior. Their 3-DHF shared `_confluence/.taxonomy.yml` continues via legacy `dhfs[].taxonomy_path` precedence rule.

### Console preview card (added 2026-05-05)

- `render.py` extended with `--candidate` / `--input` / `--output` flags so the candidate `.md` can render to a sibling `.html` without overwriting canonical
- `tools/project-console/console.yaml` extended:
  - new pattern: `docs/**/*-tracker-candidate.html`
  - new override: `submission-tracker-candidate` titled "Submission Tracker — Generator Candidate (preview)" with explicit "do NOT treat as DHF evidence" warning
- Project-console restarted via `start.sh` to pick up the new pattern
- Verified: both dashboards discovered (`submission-tracker`, `submission-tracker-candidate`); candidate route returns 200

### Folder aggregation classifier (Tier 1) — built 2026-05-05

User feedback that drove this: "Benefit-Risk Analysis documents are actually row per document, there is a single aggregated version" — the per-file granularity introduced by P1 was polluting the tracker with what is conceptually one collective deliverable. Built type-agnostic structural classifier (no per-content-type rules):

- **Schema v0.4** — added `aggregate: folder|none`, `primary_member`, `members`, `confidence`, `rationale` per mapping. Folder mappings use trailing-slash key. Defaults reproduce v0.3 behavior; v0.2 (Arthrex) and v0.3 (PDLC) files load unchanged.
- **`classify_folder()` in taxonomy.py** — Tier 1 heuristics: numbered-series (`PREFIX-NNNN.md`), aggregator-name signals (`report`/`summary`/`overview`/`rollup`/`evaluation-report`/`synthesis`/`consolidated`), single-role uniformity. Decision tree: ≥3 numbered + single role → aggregate (high conf, primary = aggregator if present else first member); aggregator + ≥2 siblings + single role → aggregate (medium conf); mixed roles → independent (high conf); else uncertain (low conf, fallback per-file).
- **`build_mappings_from_scan` rewrite** — folder-aware. Groups files by folder, runs classifier, emits aggregate mapping or per-file mappings.
- **`_discover_via_taxonomy` in generate.py** — honors `aggregate: folder` (one row pointing at primary_member, members in `extra_paths` + new `aggregate_members`/`aggregate_count` fields for renderer); skips per-file mappings appearing in any aggregate's members list.
- **No type-specific code** — "benefit-risk" never appears anywhere in the heuristic. Same logic catches CEP-NNNN, LSS-NNNN, FMA-NNNN with no per-type bloat (key user requirement).

**Validated on `pca-device`:**
- 65 file mappings → 32 mappings (8 folder aggregates)
- 260 generator rows → 128 (51% reduction)
- BRA folder: collapsed to one row, primary = `GL-TMP-UC-005-clinical-evaluation-report.md`, members = `[BRA-1001..1005 + GL-TMP-UC-005-…]`
- Folders aggregated: `clinical/benefit-risk/`, `clinical/evaluation-plans/`, `clinical/literature-search/`, `vnv/<...>`, `trace-matrix/<...>`, `risk-management/<...>`, 2 postmarket folders

**Both follow-ups landed 2026-05-05:**

**(1) Renderer aggregate UI**
- `submission-tracker.aggregates.json` sidecar emitted by generate.py (`emit_aggregates_sidecar`)
- `render.py` extended: `load_aggregates_sidecar`, `aggregate_badge_html` (N members pill with rationale tooltip), `aggregate_members_html` (clickable member-list block in row expansion). New CSS for `.row-icon.aggregate-badge` and `.aggregate-members`.
- Required fix in generate.py: aggregate fields (`aggregate`, `aggregate_members`, `aggregate_count`, `aggregate_rationale`) were not propagating from `_discover_via_taxonomy` output through to the milestone loop's row dict — now passed through.
- Verified: 36 member-list blocks rendered in candidate.html; e.g. `clinical/benefit-risk/` row carries `5 members` badge and expands to show all 6 BRA + report files.

**(2) Tier 2 LLM classifier**
- `agents/folder-classifier.md` — Tier 2 rubric (aggregate / independent / primary-with-supplements). Type-agnostic — explicitly forbids hardcoding on content type names.
- `scripts/build_classify_context.py` — bundle builder; one YAML per uncertain folder + manifest.json.
- `scripts/merge_classify_results.py` — applies per-folder JSON verdicts to taxonomy (aggregate verdicts drop per-file mappings + add folder mapping with `tier2_classifier: true`; independent verdicts append to `classifier_notes:`).
- `actions/classify-folders.md` — full Step 1-5 orchestration playbook (mirrors enrich-help fan-out).
- Smoke-tested on pca-device: builder found 6 real uncertain folders (cybersecurity, postmarket, postmarket/complaints, postmarket/capa, design-controls/user-needs, design-controls/requirements) — each is a legitimate Tier 2 candidate, each gets a real LLM call when `/tracker classify-folders` is invoked.

**No artifacts left on the deferred list for the aggregation work** — P2 is done. Next phases (P3 = `/tracker assess` AI Status sidecar, P4 = project-console filtered view with user_status overlay) remain ahead.

<!-- LESSONS LEARNED: tracker-skill, classifier-design -->
**Lesson**: Aggregation rules must be **structural, not semantic**. The first instinct on "Benefit-Risk Analyses should aggregate" is to add a special-case rule for benefit-risk; the right move is to detect the pattern that benefit-risk happens to exhibit (N numbered files matching `PREFIX-NNNN`, plus optional aggregator-named summary doc, all single-role) and code THAT. Rule lives in the skill once; future content types (CEP, LSS, FMA, STR — all observed in pca-device today; future BIA, FMECA, etc.) inherit aggregation for free with no per-type code change. Anti-pattern: if the heuristic ever needs to grep for a content-type name, the design is wrong.
**Why**: User explicitly named this constraint: "I don't want to have to be explicit and bloat the skills per type, we need language that allows the skills/agent to make that assessment." Captured as a design rule for future classifier work.
<!-- END LESSONS LEARNED -->

### Path-doubling bug in emitter (FIXED 2026-05-05)

- **Symptom**: links in candidate dashboard's Path column resolved to `/documents#path=docs/project/submissions/docs/project/dhfs/...` (doubled prefix → 404 in Documents tab).
- **Root cause**: `emit_phase_tables` in `generate.py` wrote project-root-relative paths into the markdown link target (`[BRA-1001.md](docs/project/dhfs/pca-device/...)`). The render.py URL rewriter does `(src_dir / url).resolve()` against the markdown file's directory (`docs/project/submissions/`), producing the doubled prefix. Hand-authored canonical tracker dodged the bug by using plain backticks instead of links.
- **Fix**: added `_md_link_relative()` helper + `_MD_SRC_DIR` constant in generate.py. Emitter now writes markdown-relative link targets (`../dhfs/pca-device/...`) so render.py's path-resolve produces the clean `docs/project/dhfs/pca-device/...` virtual path.
- **Verified**: `href="/documents#path=docs/project/dhfs/pca-device/clinical/benefit-risk/BRA-1001.md"` (clean); zero `submissions/docs/project` occurrences in the rendered HTML.

### Phase-map assessment — TODOs to revisit (parked 2026-05-05)

Built the `assess-phases` action (skill v17): bundle builder + regulatory-affairs subagent fan-out + merger producing 3 sidecars (phase-map.json, help.json, gaps.json). Ran 14 parallel agent dispatches against PDLC_DEMO `pca-device` (45 mappings × 4 milestones). The infrastructure works end-to-end. The **agent output quality was poor** — agents defaulted to `posture: draft-readiness` for almost every artifact at QSub (e.g., trace matrices, full V&V protocols, RM Report, pFMEA), which is wrong: a Q-Sub is a focused FDA interaction with a small purposeful package, not "510(k) but earlier." Hand-curated the phase-map after the agent run so each file is anchored to ONE primary milestone (no cross-phase duplication, per user direction). Final shape: QSub=4 / 510(k)+PCCP=28 / LMR1=0 / LMR2=0 / Other=13.

**TODO — revisit the agent assessment method.** Open questions:

1. **Is a rubric the right approach, or are we over-engineering?** The agent rubric tried to encode posture vocabulary + decision rules + per-role artifact tables. The agents still produced "draft of essentially everything" output. Worth asking whether:
   - (a) The rubric needs much sharper FDA Q-Sub Program guidance grounding (specifically what's IN a Q-Sub package per FDA Q-Sub Program guidance — Cover Letter, focused questions, meeting agenda, targeted supporting materials only as needed for the questions; NOT trace matrix / full V&V / pFMEA / etc.)
   - (b) The project should declare its Q-Sub questions explicitly (`regulatory.yml.milestones[qsub-release].qsub_questions: [...]`) so the agent uses those as the inclusion litmus test instead of guessing
   - (c) Approach should be inverted — instead of asking the agent "for each file, what's its posture per milestone?" ask "for milestone X, given these candidate files and the milestone's purpose, which subset belongs?" — the milestone-anchored question may produce better discrimination
   - (d) Drop the agent-rubric approach entirely for milestone assignment; let users hand-curate (the current state) and have agents do help-text enrichment only (their stronger suit)
2. **No-cross-phase-duplication design.** User direction: each file appears in EXACTLY ONE milestone. Future milestones inherit via explicit user promote/copy action — NOT auto-duplication. Need a `/tracker promote-to-phase <row-id> <milestone>` action and a user-override sidecar (`*.user.json`) that records promotions.
3. **User-override layer not built.** Designed in this session (the triplet pattern: `phase-map.json` = AI baseline, `phase-map.user.json` = user overlay, merged consumed file). Build when re-revisiting agent assessment so overrides survive re-runs.
4. **Out-of-Scope section in renderer.** The 13 `scope: other` files are excluded from milestone rows but no separate band shows them. Need a render-side "Out of Scope / Other" section.
5. **Per-milestone Gaps band.** The 28 entries in `gaps.json` (Q-Sub Cover Letter, Pre-Sub Questions, Software Test Plan triplet, Hazard Trace Matrix, etc.) aren't surfaced in the dashboard. Need a render-side per-milestone Gaps band.
6. **regulatory-affairs subagent has no Write tool.** Each of the 14 dispatches returned the JSON in its message body instead of writing to disk; parent had to capture-and-write each. Either (a) use a different subagent type that has Write, or (b) accept the parent capture-and-write pattern as the contract and document it in the action playbook.
7. **Friendly-title acronym list misses `pca` and `sad`.** "pca-device-system-sad.md" humanizes to "Pca Device System Sad" instead of "PCA Device System SAD". Add to KNOWN_ACRONYMS.
8. **DHF Manifest catalog is 510(k)-shaped, not Q-Sub-shaped (audit finding 2026-05-05).** Reviewed `docs/project/dhf-manifest/pdlc-demo-dhf-manifest.json` for Q-Sub guidance: only 1 obligation (`OBL-CDS-003: CDS Device Determination`, FDA CDS Guidance 2026 §V) explicitly tags `applies_to: Q-Sub Package`. The other 19 `regulatory-submission` / `submission-content` obligations are all substantive 510(k) filing content (Substantial Equivalence Argument, Predicate Selection, Performance Data, 510(k) Summary Content, §524B, SBOM, MFD Core Policy, Software Documentation Level, etc.). FDA Q-Sub Program-required formal items (Cover Letter, Pre-Submission Questions, Meeting Agenda, focused supporting materials) are NOT indexed in this catalog — they live in FDA Q-Sub Program guidance which the catalog hasn't ingested. **Implication for the agent assessment revisit**: if we want catalog-driven phase assignment, the dhf-manifest catalog needs Q-Sub Program guidance ingested as new obligation entries (OBL-QSUB-COVER-LETTER, OBL-QSUB-PRESUB-QUESTIONS, OBL-QSUB-MEETING-AGENDA, OBL-QSUB-DEVICE-DESCRIPTION, OBL-QSUB-PREDICATE-IDENT, etc.) with `applies_to: [Q-Sub Package, ...]`. Without that, the agent has no catalog grounding for Q-Sub package shape and falls back to "draft of 510(k) content" — which is what produced the over-broad QSub assignments in the first agent run.
9. **Submissions folder taxonomy missing.** The catalog's OBL-510K-001..004 (SE Argument, Predicate Selection, Performance Data, 510(k) Summary) point to submission-narrative content that lives in `docs/project/submissions/510k/` (e.g., `predicate-comparison.md`, `se-discussion.md` from the original 118-row tracker). That folder is NOT registered in `project.yml.taxonomies[]`, so the generator never sees those files. Run `/tracker init-taxonomy --path docs/project/submissions/510k` to scaffold a taxonomy for the submissions folder so submission-narrative deliverables show up in the tracker as 510(k)+PCCP-anchored rows. (Same pattern likely needed for `docs/project/submissions/qsub/` and `docs/project/submissions/pccp/`.)

### Known follow-ups discovered during P1

1. ~~**Row-ID collision under taxonomy-driven discovery (BLOCKER).**~~ **FIXED in P1.5.** Added a per-(milestone, dhf, role, subkind) seen-counter in `generate_rows()`: first occurrence keeps the bare ID (preserves folder-walk-emitter compat where exactly one row per tuple existed); subsequent occurrences append `-2`, `-3`, etc. Taxonomy `primary: true` files claim the bare ID via init_taxonomy's sorted-paths build → yaml insertion order → dict iteration order. Verified: 65 unique IDs across 65 QSub rows, BRA-1001 (primary) → `Q-PC23`, BRA-1002 → `Q-PC23-2`, BRA-1003 → `Q-PC23-3`; backward-compat hardcoded path still produces 44 rows with original IDs.
2. **REF column still empty** — generator doesn't read dhf-manifest catalog to populate REF. This is `/tracker assess` territory (P3).
3. **`pending:` triage workflow missing** — no `classify` action yet to promote `pending` → `mappings`. User has to hand-edit. Add in P2.
4. **`project.yml` comment loss on PyYAML round-trip** — flagged in changelog. Mitigation: future schema additions to `project.yml` should be hand-authored when comments matter. Long-term: ruamel.yaml round-trip support would preserve comments.

**Session ID** (current): f42700a1-25d6-4f56-b0aa-3b281709bbcb

---

### Earlier session entries

**2026-05-05 (initial — investigation + redesign)**
- Created task 044 to address broken tracker console integration
- Investigated project-console v1.9.0 changes (no impact to tracker)
- Discovered root cause: markdown structure incompatibility
- Filing HTML exists but is empty (rows: 0) due to parser failure
- Solution: restructure submission-tracker.md to Phase-based format
- Backed up original: `submission-tracker.md.backup-2026-05-05` (28K, 118 hand-curated rows)
- Created `docs/project/milestones/regulatory.yml` v1 (5 content-posture milestones; **superseded — see below**)
- Moved current tracker aside: `submission-tracker.md.preinit-2026-05-05` (so `/tracker init` would scaffold fresh)
- Discovered second root cause: `regulatory.yml` lacks `bindings:` per milestone — generator produced empty candidate
- **Strategy clarification from user**: 4-milestone regulatory strategy in order — QSub (validate approach with FDA), 510(k)+PCCP (filing event for market authorization), LMR1 (first commercial release; this is what ships, not the as-filed version), LMR2 (further commercial enhancements + PCCP envelope expansion)
- Rewrote `regulatory.yml` v2 with the 4-milestone framing, matching generator's hardcoded prefix map (`qsub-release` → Q, `pccp-release` → "", `lmr1-release` → L1, `lmr2-release` → L2). Each milestone has bindings to `pca-device` DHF as starting scope.
- Discovered third root cause: project.yml `dhfs[].path` fields were stale — `pca-device` should be `docs/project/dhfs/pca-device` (full project-root-relative path); generator + assess.py both resolve `path` literally with no prefix logic. Updated all 10 DHFs in project.yml.
- **Generator now produces 44 rows** (11 canonical roles × 4 milestones) → `submission-tracker.candidate.md`
- 44 rows ≠ 118 originally hand-curated; gap explained below.

### Generator output gap vs. original tracker

| Source | Original (118 rows) | Generator candidate (44 rows) |
|---|---|---|
| pca-device evidence walk (all 4 milestones) | included | ✅ 44 rows |
| Engineering Prerequisites | ~20 rows | ❌ — needs `docs/project/milestones/engineering.yml` |
| (submission)-scope rows (cover letter, narrative, predicate analysis, PCCP narrative) | ~30 rows | ❌ — needs richer composition-manifest entries |
| Other DHFs (connectivity-adapter, cloud-suite + 7 children) | not in original | ❌ — bindings only target `pca-device` |
| Per-row REF citations | hand-curated | ❌ — empty `—` (generator doesn't populate REF) |

### Open issues with current candidate

1. **Only QSub rows have paths.** Bindings for the other 3 milestones use `version: v1.0/v1.1/v1.2`; system-DHF evidence walk only matches `version: current`. Either change all bindings to `version: current` or extend the version-matching logic.
2. **Scope shows `pca-device`** instead of `Suite`. Add `architecture_name: Suite` to the pca-device DHF entry.
3. **No legends, Cross-Milestone Summary, Reviewer Sign-off, or Changelog** sections in the candidate — the generator only emits row tables.

### Files state at end of session

- `docs/project/submissions/submission-tracker.md.backup-2026-05-05` — pristine original (DO NOT DELETE)
- `docs/project/submissions/submission-tracker.md.preinit-2026-05-05` — same content, identical to backup; can delete once we're confident
- `docs/project/submissions/submission-tracker.candidate.md` — generator's current output (44 rows)
- `docs/project/submissions/submission-tracker.html` — STALE (last from 2026-04-14 with rows: 0)
- `docs/project/submissions/submission-tracker.md` — DOES NOT EXIST (we moved it to .preinit)
- `docs/project/submissions/submission-tracker.row-source.json` — generator sidecar (provenance)

### Next priority-ordered steps

1. Decide whether to fix the version pinning (change milestone bindings to `version: current`) so all 4 milestones' rows have paths
2. Add `architecture_name: Suite` to pca-device in project.yml so scope renders cleanly
3. Run `/tracker render` against the candidate (or promote candidate → canonical with `--write-canonical`) to see the dashboard
4. Decide on scope expansion: add `engineering.yml` for Engineering Prereqs, expand bindings to other DHFs, or accept the 4-milestone × pca-device shape as the tracker baseline
5. Restore submission-tracker.md to a name that lives in the canonical location

**Session IDs**: 67f320cb-23ed-4818-8355-07e973d7a3b7 (initial), f42700a1-25d6-4f56-b0aa-3b281709bbcb (current)

<!-- STRATEGY CONTENT: regulatory, milestone-strategy -->
**Decision**: PP3500 regulatory milestone framing is QSub → 510(k)+PCCP → LMR1 → LMR2 (in order).
- **QSub**: pre-submission to validate FDA approach + key questions
- **510(k)+PCCP**: filing event securing market authorization (K210345). NOT the version that ships to customers.
- **LMR1**: first commercial release — full feature set + UX, built in parallel with the FDA review window. This is what ships.
- **LMR2**: second commercial release — further PCCP envelope expansion + commercial enhancements
**Why**: The 510(k) review window is a build window — the team builds the final commercial product (LMR1) during it; only LMR1 (or later) reaches market.
**Captured in**: `docs/project/milestones/regulatory.yml` (4 milestones, bindings to pca-device DHF).
<!-- END STRATEGY CONTENT -->

<!-- LESSONS LEARNED: tracker-skill, configuration -->
**Lesson**: `project.yml` `dhfs[].path` is project-root-relative, not a leaf-only or bare-name. The generator + `/tracker assess` both do literal path resolution (`project_root / dhf.path`); there is no `docs/project/dhfs/` prefix logic anywhere. The comment in project.yml that read "folder name under docs/project/dhfs/ (or nested path)" was misleading and led to silent zero-row generator output. Updated comment + 10 path entries.
**Why this matters**: Future projects scaffolded from a template will inherit whatever `path` convention they're given; getting it wrong produces empty tracker output with no clear error.
<!-- END LESSONS LEARNED -->

<!-- LESSONS LEARNED: tracker-skill, milestone-catalog -->
**Lesson**: `regulatory.yml` milestone IDs are matched against a hardcoded prefix map in `generate.py` (`ms_prefix_map`): `qsub-release` → Q, `pccp-release` → no-prefix (baseline), `lmr1-release` → L1, `lmr2-release` → L2. Using milestone IDs that aren't in this map produces rows with empty milestone prefix (so e.g. all rows collide at `PC1`, `PC2`...). Projects that need a different filing strategy (e.g., De Novo, PMA, IDE-then-PMA) need to either (a) reuse these IDs as conceptual placeholders, or (b) extend the prefix map in generate.py.
<!-- END LESSONS LEARNED -->

<!-- STRATEGY CONTENT: development, architecture; tracker-skill, project-console -->
## Three-Layer Taxonomy Architecture (decision 2026-05-05)

**Decision**: Refactor the tracker's discovery model from hardcoded folder paths to a three-layer taxonomy architecture. Brittleness driver: the current `DEFAULT_SYSTEM_DHF_ROLE_MAP` (11 hardcoded folders × DHF) silently skips evidence not in the canonical layout (e.g., `design-controls/labeling/`, `design-controls/pccp/`, `design-controls/usability/` are invisible to generate.py today) and collapses multi-file folders to the alphabetically-first `.md`.

### Layer model

| Layer | Owner | Artifact | Purpose |
|---|---|---|---|
| **1. Source taxonomy** | `/tracker` | `<root>/.taxonomy.yml` (per root — DHFs + predicate-analysis + submissions + strategies + external/internal references) | Lossless map of files-on-disk → canonical roles. Every file is captured. |
| **2. Row inventory + AI Status** | `/tracker` | `submission-tracker.md` (row tables) + `submission-tracker.agent.json` (AI Status sidecar) | Rows projected from milestones × taxonomies × dhf-manifest catalog. AI Status is machine-derived (file existence, lifecycle frontmatter, content coverage). |
| **3. Filtered view + User Status** | `/project-console` | `docs/project/console/taxonomy-view.yml` | User-curated overlay keyed by row_id. Carries `visible:`, `milestone_override:`, `user_status:`, `notes:`. Round-trip safe — joined to layer 1/2 by row_id, never mutates them. |

### Key architectural moves

1. **Taxonomy is horizontal, not DHF-specific.** Same machinery serves DHFs, predicate analysis, submission folders, strategy docs, external/internal references. `root_kind:` field selects the role vocabulary plugin.
2. **Conflict surfacing via `unmapped:` block.** Files known to exist but not classified live in the taxonomy's `unmapped:` list with `first_seen` dates. `/tracker reconcile-taxonomy` re-scans and updates this block. Generation never silently drops files.
3. **AI Status / User Status split.** AI Status (machine assessment) and User Status (human dropdown) live as separate fields and are displayed side-by-side. Disagreement between them is a feature — surfaces review/CAPA situations.
4. **Vocabulary grounding for DHFs is `dhf-manifest`.** Canonical-role names in DHF taxonomies must reference roles declared in the catalog. Other root kinds (predicate-analysis, submission, external-reference) declare their own vocabulary.
5. **Status vocabulary is shared between AI and User**: `Not Started | In Progress | Drafted | In Review | Approved | Inherited | N/A`, plus User-only `Needs Revision` / `Blocked`. Shared vocab makes AI vs User disagreement visually meaningful.

### Skill placement

Taxonomy actions (`init-taxonomy`, `reconcile-taxonomy`, `classify`, `validate`) live inside `/tracker`. Tracker is both builder and first consumer. Project-console is the filtered-view consumer; reads tracker's emitted artifacts but does not own taxonomy authoring.

### Taxonomy registration in project.yml (decision 2026-05-05)

Top-level `taxonomies:` block is the canonical registry. Inverts the current Arthrex pattern (per-DHF `taxonomy_path:`) so a single taxonomy can declare it applies to one root, many roots, or non-DHF folders.

```yaml
# project.yml
taxonomies:
  - id: <slug>
    file: <path-to-taxonomy.yml>
    applies_to_dhfs: [<dhf-leaf>, ...]    # 0..N DHF leafs
    applies_to_paths: [<folder-path>, ...] # 0..N non-DHF roots
```

**Resolution precedence** (deterministic, for each root the tracker walks):
1. `taxonomies[]` registry match
2. Legacy `dhfs[].taxonomy_path:` (Arthrex backward-compat; loader synthesizes a `taxonomies[]` entry in memory)
3. Co-located `<root>/.taxonomy.yml`
4. Hardcoded `DEFAULT_SYSTEM_DHF_ROLE_MAP` fallback (system DHFs only)

**Migration**: Arthrex's existing 3-DHF `taxonomy_path:` fields keep working unchanged. Optional cleaner form:
```yaml
taxonomies:
  - id: confluence-product-overview
    file: docs/project/_confluence/.taxonomy.yml
    applies_to_dhfs: [hiplink-pre-op, hiplink-intra-op, hiplink-mgmt-services]
```
Both forms supported indefinitely; Arthrex migrates if/when they want a single source of truth for taxonomy registration.

**Why this shape**:
- 1:1 and 1:N use the same field structure (`applies_to_dhfs: [a]` vs `[a,b,c]`)
- Non-DHF roots (predicate-analysis, submission folders, external references) are first-class via `applies_to_paths:`
- `/tracker list-taxonomies` enumerates one block; no crawling needed
- `/tracker reconcile-taxonomy <id>` resolves all covered roots from one registry lookup; the shared-taxonomy-across-N-DHFs case becomes one reconcile, not N

### Action surface

```
/tracker init-taxonomy <path>           # build .taxonomy.yml at any root
/tracker init-taxonomy --all-dhfs       # iterate project.yml dhfs[]
/tracker init-taxonomy --root-kind=submission docs/project/submissions/510k
/tracker reconcile-taxonomy <path>      # diff disk vs taxonomy
/tracker reconcile-taxonomy --all       # walk every .taxonomy.yml
/tracker classify <path> <file> <role>  # promote unmapped → mappings
/tracker list-taxonomies                # discover + summary
/tracker validate-taxonomy <path>       # CI schema check
/tracker assess                         # emit AI Status sidecar (existing action, extended)
```

### Data flow

```
.taxonomy.yml (per root) ─┐
                          ├──▶ /tracker generate ──▶ submission-tracker.md (rows)
regulatory.yml ───────────┤                            │
dhf-manifest ─────────────┘                            ├──▶ /tracker assess ──▶ submission-tracker.agent.json (AI Status)
                                                       │
                                                       ▼
                                          docs/project/console/taxonomy-view.yml
                                          (project-console-owned: visible, milestone_override, user_status)
                                                       │
                                                       ▼
                                          project-console dashboard
                                          (joins rows + AI Status + User overlay)
```

### Why we picked this over alternatives

- **Frontmatter-driven roles** (every doc declares `canonical_role:` in YAML frontmatter): elegant but scatters source of truth across hundreds of files; refactor cost is real. Single-file taxonomy localizes the contract.
- **Pure `project.yml` override** (`tracker.system_dhf_layout`): inherits the rigid-layout problem; just lets each project pick a different rigid layout. Doesn't surface drift.
- **Separate `/taxonomy` skill**: cleaner architecturally but multi-hour scaffold cost (VERSION, README, registry, hooks, sister-project compat). User chose to keep it inside `/tracker` — we extract later if other consumers emerge.

### Build phases (proposed)

| Phase | Scope | Validation gate |
|---|---|---|
| **P1** | `/tracker init-taxonomy` + `/tracker reconcile-taxonomy`; build `.taxonomy.yml` for `pca-device`; update `/tracker generate` to consume it | pca-device candidate reflects all evidence including labeling/pccp/usability folders the hardcoded walk misses today |
| **P2** | Extend taxonomy to other roots (predicate-analysis, submission folders); validate `root_kind` plugin model | Predicate-analysis rows appear in (submission)-scope of tracker |
| **P3** | `/tracker assess` AI Status sidecar with shared vocabulary | submission-tracker.agent.json populated |
| **P4** | Project-console reads taxonomy-view.yml; renders AI Status + User Status side-by-side; UI for hide/show, milestone override, user-status dropdown | End-to-end demo: AI says one thing, user overrides via dropdown, dashboard shows both |
<!-- END STRATEGY CONTENT -->

<!-- LESSONS LEARNED: tracker-skill, evidence-discovery -->
**Lesson**: Hardcoded path walks (e.g., `DEFAULT_SYSTEM_DHF_ROLE_MAP` in tracker's `generate.py`) silently drop evidence not in the canonical layout AND collapse multi-file folders to one alphabetically-sorted winner. The brittleness is invisible — the generator just produces fewer rows. Taxonomy + reconcile + `pending:` block are the antidote: discovery is explicit, ambiguities surface as conflicts the user resolves, and re-scans can detect drift over time.
**Why**: Discovered while investigating why the original 118-row tracker collapsed to a 44-row generator candidate. The other 74 rows aren't lost data — they're evidence the hardcoded walk can't see.
<!-- END LESSONS LEARNED -->

<!-- LESSONS LEARNED: tracker-skill, sister-project-compat -->
**Lesson**: Arthrex (sister project at `../../projects/arthrex/pccp/`) is significantly ahead on this exact problem space and ALREADY has a working v0.2 taxonomy (`docs/project/_confluence/.taxonomy.yml`, 155 lines, shared across 3 external-mode item DHFs) plus a fully-developed `tracker.status_vocabulary` block in project.yml that implements the AI-vs-User-Status dual model we just designed. Three things would have broken if PDLC_DEMO's redesign had proceeded blind:
  1. **`unmapped:` naming collision** — Arthrex uses it as a per-mapping field meaning "intentionally not evidence" (categories: informational/navigation/assets/metadata). Our proposed top-level "files-not-yet-classified" block would have silently corrupted their taxonomy. Renamed our concept to `pending:`.
  2. **Status vocabulary** — Arthrex has 7-state vocabulary locked in (not-started/drafting/drafted/in-review/needs-revision/approved/not-applicable) with documented intent that "AI=Approved, Status=Needs Revision surfaces a real disagreement." Use their vocab verbatim, don't invent.
  3. **Multi-DHF shared taxonomy** — Arthrex's 3 item DHFs share ONE taxonomy via `taxonomy_path` override (Confluence template they all share). Co-located-only `<root>/.taxonomy.yml` would have forced 3 duplicates. Default is co-located; `taxonomy_path:` override continues to work for shared cases.
**Why this matters**: Validates the "check sister project before redesigning skills" rule from feedback memory. The convergence is striking — both projects independently arrived at the same architectural problem; Arthrex got there first and shipped a partial implementation. PDLC_DEMO can adopt their schema and vocabulary instead of re-deriving them.
<!-- END LESSONS LEARNED -->

**Session ID**: 67f320cb-23ed-4818-8355-07e973d7a3b7

---

## ⏸ Resume Point — 2026-05-05 end of session

### Where we are right now (read this first)

The submission tracker is **functioning end-to-end with hand-curated data**. The candidate dashboard at `http://127.0.0.1:8765/dashboards/submission-tracker-candidate` shows a clean **37-row tracker** organized by milestone with rich help text on the QSub package.

**Current state on disk:**
- `docs/project/dhfs/pca-device/.taxonomy.yml` — 32 mappings (24 file + 8 aggregates) including 5 aggregation_candidates flagged for Tier 2 review
- `docs/project/submissions/tracker-user-rows.yml` — 5 user-injected QSub formal-package rows (Q1–Q5: Cover Letter, Pre-Sub Questions, Meeting Agenda, Device Description, Predicate Identification)
- `docs/project/submissions/submission-tracker.phase-map.json` — hand-curated assignment, each file in EXACTLY ONE primary milestone (`_hand_curated: true`)
- `docs/project/submissions/submission-tracker.help.json` — 9 row-id-keyed help blocks for QSub (Q1-Q5 + Q-PC1, Q-PC2, Q-PC23, Q-PC26 — re-keyed from the agent file-path entries) + 45 legacy file-path-keyed entries from the agent run (don't render but preserved for the agent-method revisit)
- `docs/project/submissions/submission-tracker.gaps.json` — 28 catalog/Q-Sub gaps from the agent run (not rendered yet)
- `docs/project/submissions/submission-tracker.candidate.md` — 4.6KB regenerated candidate
- `docs/project/submissions/submission-tracker-candidate.html` — rendered, served at /dashboards/submission-tracker-candidate
- `/tmp/phase-map-bundles/` — 14 agent result JSONs preserved for the agent-method revisit (manifest.json + 14 *.result.json + 14 *.yaml bundles)

**Tracker shape today:**

| Section | Rows | Notes |
|---|---|---|
| QSub | 9 | 5 user-injected formal package items (Q1-Q5) + 4 catalog-anchored supporting materials (System SAD, Design Inputs, Cybersecurity Plan, CEP) |
| 510(k)+PCCP | 28 | Full filing content: risk management (5 distinct ISO 14971 artifacts), V&V (3 protocols), trace matrices (3 distinct), cybersecurity (VMP/Threat Model/SBOM), labeling, plans, requirements, user needs, etc. |
| LMR1 / LMR2 | 0 each | Empty by design — user will promote items forward via the (future) user-override layer when authoring commercial-release deltas |
| Out of Scope | 13 (excluded from rendering) | PMCF studies, complaint records, CAPA, internal strategy/testing-strategy, tool validation, risk-strategy. Currently NOT rendered anywhere — needs an Out-of-Scope band. |

### Concrete priority-ordered next steps

The work below is ordered by impact and rough estimated effort. Pick from the top.

1. **Render Out-of-Scope section** *(small render-side fix, ~30 min)*
   - 13 `scope: other` files in phase-map.json don't appear anywhere in the dashboard today.
   - Add a render-side band below the milestone phases listing scope=other rows with their `scope_rationale`.
   - Hooks: `render.py` reads `phase_map_sidecar` for scope=other entries; emit a section after the last phase.

2. **Render per-milestone Gaps band** *(small render-side fix, ~30 min)*
   - 28 entries in `gaps.json` (Q-Sub formal items, Software Test Plan triplet, Hazard Trace Matrix, Cybersecurity Mgmt Plan, etc.) don't surface in the dashboard.
   - Note: the 5 Q-Sub formal items are now in user-rows (Q1-Q5) so those duplicates can be removed from gaps.json before rendering.
   - Add a per-milestone "Gaps" band; render after each milestone's row tables.

3. **User-override layer** *(medium, ~1.5h)* — the round-trip safety net the user explicitly asked for. Triplet pattern:
   - `submission-tracker.phase-map.user.json` — user overrides; never touched by merger
   - merger reads BOTH AI baseline + user overlay; outputs merged file with `_provenance` per field
   - bundle builder includes existing user overrides in agent context so agents don't contradict
   - Build a `/tracker promote-to-phase <row-id> <milestone>` action that records a user promotion in the .user.json file

4. **Submissions folder taxonomy** *(small, ~15 min)* — quick win
   - `docs/project/submissions/510k/`, `qsub/`, `pccp/` aren't registered in `project.yml.taxonomies[]`
   - Run: `python3 .claude/skills/tracker/scripts/init_taxonomy.py --project-dir <root> --path docs/project/submissions/510k`
   - Surfaces existing predicate-comparison.md, se-discussion.md (from the original 118-row tracker) as 510(k)+PCCP rows

5. **DHF Manifest catalog — add Q-Sub Program guidance entries** *(medium, ~1h)* — addresses the catalog-shape gap
   - Catalog has only 1 Q-Sub-explicit obligation today (`OBL-CDS-003`). Need ~6 more: OBL-QSUB-COVER-LETTER, OBL-QSUB-PRESUB-QUESTIONS, OBL-QSUB-MEETING-AGENDA, OBL-QSUB-DEVICE-DESCRIPTION, OBL-QSUB-PREDICATE-IDENT, OBL-QSUB-PROGRAM-PROCEDURES.
   - Once catalog has them, the agent has grounding for Q-Sub assignment instead of guessing.
   - Owned by `/dhf-manifest` skill, not tracker.

6. **Revisit the agent assessment method** *(large, multi-session)* — TODO #8 in this doc. Open question: rubric vs question-driven inversion vs hand-curate-only. See "Phase-map assessment — TODOs to revisit" section above (9 explicit follow-ups).

7. **Friendly-title acronym list polish** *(trivial, 5 min)* — add `pca`, `sad` to `KNOWN_ACRONYMS` in `taxonomy.py` so "Pca Device System Sad" → "PCA Device System SAD". Re-init pca-device after.

8. **Datetime serialization warning** *(trivial, 5 min)* — `emit_row_source_sidecar` warns "Object of type datetime is not JSON serializable" when reading user-rows.yml's `_meta` block. Convert `_meta.created_at` / `last_updated_at` to strings (ISO format) when reading. Cosmetic — affects user-row badges only.

### Open questions blocking progress

- **None blocking.** All TODOs are independent forward-progress work; nothing requires user clarification before proceeding.
- The biggest design open question (TODO #6 — agent method) needs user input on direction (rubric tightening vs question-driven inversion vs drop agent for milestone assignment) but not until you're ready to invest in the revisit.

### Skill-side state (everything in `.claude/skills/tracker/`)

Tracker skill at v17 with:
- Schema v0.4 taxonomy (`schemas/taxonomy.schema.yml`)
- Resolver + scanner + Tier 1 classifier + title extraction (`scripts/taxonomy.py`)
- Init / reconcile CLIs (`scripts/init_taxonomy.py`, `scripts/reconcile_taxonomy.py`)
- Tier 2 LLM classifier infrastructure (bundle builder + agent rubric + merger + action playbook)
- Phase-map assessment infrastructure (`scripts/build_phase_map_context.py`, `scripts/merge_phase_map_results.py`, `agents/phase-mapper.md`, `actions/assess-phases.md`)
- Renderer aggregate UI (count badges, member-list expansion)
- Renderer `--candidate` / `--input` / `--output` flags
- Generator phase-map sidecar consumption
- All portability seams: `tracker.filename_prefix_strip_patterns`, `tracker.classification_heuristics`, `tracker.title_acronyms` per-project overrides

### Hard-coded files to revisit / hand-edit on next session

| File | Why | Pattern |
|---|---|---|
| `docs/project/submissions/submission-tracker.phase-map.json` | Hand-curated; contains `_hand_curated: true` flag | If you want to move items between milestones, edit this directly (set posture=n/a on current milestone, set posture+version_label on new milestone) |
| `docs/project/submissions/tracker-user-rows.yml` | Q1-Q5 user-injected QSub items | Edit directly to add more user rows or modify Q1-Q5 wording |
| `docs/project/submissions/submission-tracker.help.json` | Q1-Q5 + Q-PC1/Q-PC2/Q-PC23/Q-PC26 hand-authored / re-keyed | Edit row-id keys directly to refine help content; re-render to see changes |

### Recovery Command

To activate this task in a new session:
```bash
bash .claude/hooks/task-activate.sh add 67f320cb-23ed-4818-8355-07e973d7a3b7 044
```

To regenerate + render the dashboard after any edit:
```bash
uv run --project tools/project-console python .claude/skills/tracker/scripts/generate.py --project-dir /Users/ben.xavier/Documents/demos/pdlc_demo --md --candidate
uv run --project tools/project-console python .claude/skills/tracker/scripts/render.py --project-dir /Users/ben.xavier/Documents/demos/pdlc_demo --candidate
# Then hard-refresh http://127.0.0.1:8765/dashboards/submission-tracker-candidate
```

To restart the project-console (if needed):
```bash
bash tools/project-console/start.sh
```

## Economics

_Retrospective estimate (rough; from task summary). See effort-estimation-rubric.md._

```json
{
  "economics": {
    "method_version": 1,
    "retrospective": true,
    "agentic_hours": 5,
    "todos": [
      {
        "todo": "Tracker console integration recovery",
        "personas": [
          "rd-lead"
        ],
        "manual_hours": {
          "min": 10,
          "max": 24
        },
        "confidence": "low",
        "basis": "reset-to-upstream tracker recovery + re-sync"
      }
    ]
  }
}
```
