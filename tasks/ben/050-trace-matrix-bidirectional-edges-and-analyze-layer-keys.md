# 050 — Trace-Matrix Bidirectional Edges + analyze.py Layer-Keys Fix

**ID**: 050
**Created**: 2026-05-12
**Status**: Complete
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

Generic modifications to the `trace-matrix` skill to fix two issues surfaced by task [[task-049]] (SRS authoring), so any medtech-docs project with a populated SW layer gets correct trace semantics — not just PDLC_DEMO.

### Issue 1 — Bidirectional edge philosophy (V&V scope filter is the visible symptom)

The trace engine's edge-building philosophy is inconsistent across layer pairs. The V&V scope filter in `scripts/graph.py:81–107` drops DI-derived VER nodes when SW exists (because they only carry `verifies_di_ids`, not `traces_forward_ids→SW`), turning previously-valid DI→VER edges into `broken_refs` and leaving the V&V layer empty.

Root principle (decided with user, 2026-05-12): **the engine must treat each layer-pair relationship as authorable from either side. Build the edge if either side claims it. Detect asymmetric authoring as a warning. Compute orphans honestly from the canonical edge set.**

Five sub-changes, all in the trace-matrix skill:

1. **Drop the V&V scope filter at `scripts/graph.py:81–107`.** It's the wrong policy; it deletes legitimate trace data before edges are built.
2. **Make edge-building bidirectional for every layer pair.** After parsing, normalize all authored relationships into a single canonical edge set keyed by `(upstream-id, downstream-id)`, regardless of which side wrote the claim.
3. **Add SW→VER edge building.** Currently `scripts/graph.py:124–142` builds DI→VER edges from DI rows' `verification_ids`, but the parallel logic for SW rows is missing — `scripts/graph.py:144–155` only handles SW→DI (upstream-trace) and ignores SW's own `verification_ids`. Mirror the DI logic so SW→VER edges build the same way.
4. **Asymmetric-trace warnings.** If DI-001 lists VER-X in its verification column but VER-X's `traces_forward_ids` claims a different requirement (or nothing), emit a `warnings` entry like `asymmetric_trace: DI-001 → VER-X, but VER-X does not reciprocate`. Both edges still build (each side's authoring is honored); the warning surfaces the inconsistency for human review.
5. **Orphan rules stay as authored** — `scripts/graph.py:179–195` already matches the right semantics; they just need the scope filter gone to behave correctly post-SW.

### Issue 2 — `scripts/analyze.py` silently skips the `software` layer

`scripts/analyze.py:34` defines `LAYER_KEYS = ["user_needs", "design_inputs", "architecture", "vnv", "risk"]` — `software` is missing. Decided fix (Option B): import the canonical layer list from `graph.LAYER_ORDER` instead of maintaining a parallel constant. Eliminates the bug class — future layer additions only need to touch `graph.py:17`.

### Verification scope

Before marking complete:
- All existing tests in `.claude/skills/trace-matrix/tests/` pass.
- New tests covering: bidirectional edge build for each layer-pair; asymmetric-trace warning emission; DI-derived VER survival post-SW; SW→VER edge build; `analyze.py` reporting on the software layer.
- Rebuild PDLC_DEMO trace matrices and verify: pca-device / connectivity-adapter / cloud-suite — DI→SW edges still 34/32/31; SW→VER edges > 0; V&V layer items > 0 (DI-derived VER nodes preserved); broken_refs count drops to 0 (or only flags genuinely-unknown IDs); orphan flags reflect actual coverage gaps.
- **Sister-project validation per [[feedback_sister_project_compat]]**: run the modified skill against `../../projects/arthrex/pccp/` and confirm no regression (build clean, no new broken_refs introduced, no test failures).

## Why this matters

The PDLC_DEMO trace matrix as of [[task-049]] commit `51f8294` shows DI→SW edges working (34/32/31) but DI→VER broken_refs (4/21/22) and empty V&V layers — the regression cost of adding SW under the current skill. Any sister or future medtech-docs project that adds an SRS to a markdown-authored DHF will hit the same wall. This task generalizes the fix so the skill works for any author-direction pattern (DI-side, SW-side, Jira-mirror, or a mix).

## Source files involved (where the work lives)

| File | Change |
|---|---|
| `.claude/skills/trace-matrix/scripts/graph.py` | Drop scope filter (81–107); refactor edge-building loop (115–177) into a bidirectional canonical-edge pass; add SW→VER from SW `verification_ids`; emit asymmetric-trace warnings. |
| `.claude/skills/trace-matrix/scripts/analyze.py` | Replace `LAYER_KEYS` constant (line 34) with `from graph import LAYER_ORDER`; use `LAYER_ORDER` for iteration. |
| `.claude/skills/trace-matrix/tests/` | New test cases per the verification scope above. |
| `.claude/skills/trace-matrix/SKILL.md` | Document the bidirectional edge philosophy; remove any scope-filter references; note the asymmetric-trace warning surface. |
| `.claude/skills/trace-matrix/README.md` | Update `## Changelog` + `## Best Practices`; bump version per [[feedback_skill_version_bestpractices]]. |

## Todos

### Phase 1 — Read + Plan
- [x] Re-read `scripts/graph.py` end-to-end and `scripts/analyze.py` end-to-end (2026-05-12). Audited test suite — only `test_jira_mirror.py` existed at v7 baseline, no graph.py / analyze.py tests. Audited consumers of edge `kind` labels — only `project-console` reads `traces_forward` per-item lists (not the `kind` field), so kind labels can change without breaking the console.

### Phase 2 — Issue 2 fix (smallest)
- [x] Replaced `analyze.LAYER_KEYS` constant with `from graph import LAYER_ORDER as LAYER_KEYS` (2026-05-12). Confirmed `analyze.py --dhf pca-device` now reports the software layer (32 nodes, project adapter).

### Phase 3 — Issue 1 fix (refactor)
- [x] Refactored `scripts/graph.py` `build()` end-to-end (2026-05-12):
      - Replaced the v7 per-layer-key edge-building blocks with a canonical `(upstream_id, downstream_id)` edge collection from three authoring fields (`traces_forward_ids`, `verifies_di_ids`, `verification_ids`)
      - Added SW→VER edge build from SW rows' `verification_ids` (previously ignored by the engine)
      - Replaced the unconditional v7 V&V scope filter with a narrower one that runs only when V&V has its own source files AND keeps V&V items reciprocating ANY requirement (DI or SW), not SW only
      - Added `asymmetric_trace` warning emission on the V&V layer (scoped to DI↔VER and SW↔VER, fires only when V&V has independent source)
      - Preserved historical edge `kind` labels (`un_to_di`, `di_to_sw`, `di_to_vnv`, `sw_to_vnv`) via `_EDGE_KIND_ALIASES`
      - Orphan rules unchanged (`graph.py:179–195` semantics carried forward)

### Phase 4 — Verify
- [x] All 23 tests pass (6 pre-existing jira-mirror + 17 new bidirectional/scope/orphan/broken-ref tests). New test file: `.claude/skills/trace-matrix/tests/test_graph_bidirectional.py`.
- [x] PDLC_DEMO rebuild: DI→SW counts unchanged at 34/32/31; SW→VER edges built at 4/21/21; V&V layer items 3/21/21 (DI-derived VERs preserved — was 0/0/0 pre-fix); broken_refs reduced to 3/0/0 (only legitimate unknown-VER refs in pca-device's SW doc — VER-PP3500-SW-001 / VER-PP3500-SW-003 — which the SW author needs to either add as DI references or remove).
- [x] **Sister project validation passed**: applied the changes locally to `/Users/ben.xavier/Documents/projects/arthrex/pccp/`, ran build + tests. **Zero regression** — edges, V&V counts, broken_refs identical pre/post across all 4 sister DHFs (hiplink-pre-op: 26/13/0; hiplink-intra-op: 225/139/0; hiplink-mgmt-services: 152/87/0; hiplink-suite: 0/0/0). JSON diff was just deterministic re-sorting. Sister skill files reverted after validation per [[feedback_skill_version_bestpractices]]; promotion upstream happens via `/sync-skills push` when the user chooses.

### Phase 5 — Document + Commit
- [x] Updated `SKILL.md` (v7 → v8) with new "Edge model — bidirectional authoring" section explaining the three authoring fields, the scope filter, and the asymmetric-trace warning. Updated frontmatter description.
- [x] Updated `README.md` with v8 Changelog entry (project-agnostic per skill-creator's rules).
- [ ] Commit + push (separate commits for issue 2 and issue 1 — easier to revert either)
- [ ] (Optional) Push upstream via `/sync-skills push` if the user wants the skill registry updated — confirm before doing so

## Resume Command

```bash
bash .claude/hooks/task-activate.sh add <SESSION_UUID> 050
```

## Open Questions

- Whether to push the skill modification upstream via `/sync-skills push` after PDLC_DEMO and Arthrex/PCCP both pass — defer the decision until both validations are clean.
- Whether asymmetric-trace warnings should also be emitted for the UN↔DI and DI↔SW pairs (which currently only support child→parent authoring) — likely deferred to a follow-up if the same authoring pattern is observed for those pairs. For now scope the warning to DI↔VER and SW↔VER, where both sides are commonly authored.

## Changelog

| Date | Author | Summary |
|---|---|---|
| 2026-05-12 | Ben (with Claude) | Task created. Two trace-matrix skill fixes scoped: (1) drop V&V scope filter + bidirectional edges + SW→VER + asymmetric warning, (2) analyze.py LAYER_KEYS → import graph.LAYER_ORDER. Implementation will be driven by `/skill-creator` with sister-project validation per [[feedback_sister_project_compat]]. |
| 2026-05-12 | Ben (with Claude) | Phases 1–5 complete. Trace-matrix skill bumped v7 → v8. New canonical-edge engine with bidirectional authoring; SW→VER edges; refined scope filter (DI+SW universe, runs only when V&V has independent source); asymmetric-trace warnings. 17 new tests pass; sister-project validated with zero regression. Final PDLC_DEMO state: DI→SW 34/32/31, SW→VER 4/21/21, V&V 3/21/21, broken_refs 3/0/0 (legitimate authoring gaps in pca-device SW doc). Phase 5 commit + push next. |
| 2026-05-12 | Ben (with Claude) | **Upstream push complete + project re-synced.** hitachi PR #159 merged at `d3c3429`. Project pulled 27 files (advisors v1.0→v1.2.0, dhf-manifest v7→v9). Ran `/dhf-manifest discovery-index` post-update action — 9 project + 133 per-DHF resolutions, 0 ambiguity issues for resolved roles. Surfaced filename-convention mismatch (canonical-roles.yaml uses Title Case patterns; medtech-docs convention is lowercase-hyphen). Applied project-side `evidence_layout.layers` override in `project.yml` for `user_needs` + `software_requirements`. Three follow-up improvements scoped + deferred to **task 051 (fresh session)**: (a) lowercase-hyphen pattern variants in `canonical-roles.yaml`, (b) bug fix to populate `ambiguity_notes[]` on multi-match no-winner, (c) frontmatter `canonical_role` declaration as author-facing opt-in. LLM-subagent-at-`--resolve-ambiguity` deferred indefinitely (deterministic improvements first). Commit `7454063`. |
| 2026-06-08 | Ben (with Claude) | 2026-06-08: Confirmed Complete via task-doc audit — analyze.py imports LAYER_ORDER; trace-matrix v8; hitachi PR #159. Filed under Completed in 000-index.md. |

