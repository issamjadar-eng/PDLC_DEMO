# 049 — Build Out Software Requirements (PCA, Cloud Suite, Connectivity Adapter)

**ID**: 049
**Created**: 2026-05-12
**Status**: In Progress
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

Build out the **software requirements (SRS)** layer for the three core DHFs in PDLC_DEMO so the trace matrix shows UN → DI → SW → V&V chains end-to-end instead of stopping at DI:

| DHF | Current state (as of 2026-05-12 session end) | Goal |
|---|---|---|
| **pca-device** | UN=22, DI=34, **software=0 (source_missing)**, arch=7 (edges_known=false), vnv=3, risk=0 (no_items_parsed) | Author SRS source doc; trace UN→DI→SW; aim for 30–50 SW reqs across the 9 functional groups (G1–G9) |
| **connectivity-adapter** | UN=21, DI=21 (just authored 2026-05-12), **software=0 (source_missing)**, arch=0 (no_items_parsed), risk=0 | Author SRS for the 7 module groups (A1–A7); aim for ~30 SW reqs |
| **cloud-suite** | UN=22, DI=22 (just authored 2026-05-12), **software=0 (source_missing)**, arch=0, risk=0 | Author **platform-level** SRS for the 7 functional groups (P1–P7); aim for ~30 SW reqs. Module-specific SRS lives in child DHFs (drug-library-manager, fleet-management, etc.) and is out of scope for this task |

Then rebuild the trace matrix and verify SW counts > 0 with edges from DI to SW.

## Why this matters

The console's Trace Matrix view currently shows broken/empty SW columns for these three DHFs — the chain stops at DI. Without SW reqs, IEC 62304 §5.2 (software requirements analysis) has no evidence artifact; the trace matrix can't demonstrate decomposition from DI to implementable software-level requirements. This is also a recurring console-walkthrough finding ([[task-048]] sister-parity walkthrough surfaces it).

## Source-of-truth file targets (where SRS docs need to land)

| DHF | SRS source path the trace-matrix.yml will point at | Status |
|---|---|---|
| pca-device | `docs/project/dhfs/pca-device/design-controls/requirements/software-requirements.md` | TBD — does **not** exist; trace-matrix.yml `software` layer is `null` |
| connectivity-adapter | `docs/project/dhfs/connectivity-adapter/design-controls/requirements/software-requirements.md` | TBD — does not exist; `software` layer null |
| cloud-suite | `docs/project/dhfs/cloud-suite/design-controls/requirements/software-requirements.md` | TBD — does not exist; `software` layer null |

**Important** — before authoring, check `trace-matrix.yml`'s `software:` block for each DHF; the field may need to be wired (`source:` path + `id_prefix: SW`) for the trace-matrix build to pick the new file up. The skill won't auto-detect.

## Authoring approach

1. **Use the pca-device DI file as the template shape** — same column headers as `docs/project/dhfs/pca-device/design-controls/requirements/design-inputs.md`. Default parser is GFM-table-driven and picks up rows where the ID column matches the configured `id_prefix` (likely `SW`).
2. **Trace from DI down** — each SW row should declare `Traces to DI` (one or more DI IDs). The default parser produces DI→SW edges from this column.
3. **One SW req → one DI** is the easiest pattern; one SW req → multiple DIs is OK; many SW reqs per DI is the normal decomposition direction.
4. **Functional grouping** — mirror the DI doc's groups (G1–G9 for pca-device; A1–A7 for connectivity-adapter; P1–P7 for cloud-suite) so the rendered trace stays legible.
5. **Demo content is OK and expected** — every file gets the `_Demo sample data — not for clinical use._` banner. CLAUDE.md "no fabricating regulatory content" rule is honored by the demo banner. Reference the same KOL IDs, CAPA IDs, and standards already cited in the UN/DI docs for narrative consistency.
6. **IEC 62304 alignment** — each SW req should be classifiable as one of: Functional (FUNC), Performance (PERF), Interface (INTE), Safety (SAFE), Security (SEC), Usability (USAB). Carry a software-safety class (A / B / C) per IEC 62304 §4.3 if it adds rigor without over-engineering the demo.

## Todos

### Phase 1 — Plan + wire trace-matrix.yml (do FIRST)
- [x] Read `trace-matrix.yml` `software:` block for each of pca-device, connectivity-adapter, cloud-suite — confirmed: **no `software:` block existed at all** for the three DHFs (only user_needs, design_inputs, architecture, vnv, risk). Canonical path = `design-controls/requirements/software-requirements.md` in each DHF tree.
- [x] Updated `trace-matrix.yml` to add a `software:` layer block (source + `id_prefix: SW`) under each of `pca-device`, `connectivity-adapter`, `cloud-suite` (2026-05-12). Module DHFs under `cloud-suite/dhfs/*` left unchanged — they're out of scope for this task.
- [x] **Default `software` parser confirmed to be a no-op** (`.claude/skills/trace-matrix/scripts/parsers/defaults/software.py` returns empty `ParserResult()`). The original task strategy block's claim that "no project adapter is required if SW source mirrors DI shape" was **wrong**. Per `rational_check`, an empty-result-on-populated-source → `ok: false` → `/trace-matrix init` will detect this and generate `tools/project-console/trace-matrix/adapters/software.py`. Plan: (1) author the SRS files in DI-shape with `Traces to DI` column, (2) run `/trace-matrix init --layer software --dhf pca-device` (one DHF at a time so the generator sees a populated source on its first run; the generated adapter is shared across DHFs so subsequent DHFs reuse it).

### Phase 2 — Author SRS files
- [x] **pca-device** — `docs/project/dhfs/pca-device/design-controls/requirements/software-requirements.md` — 32 SW rows across G1–G9, every row traces to ≥1 DI. (2026-05-12)
- [x] **connectivity-adapter** — `docs/project/dhfs/connectivity-adapter/design-controls/requirements/software-requirements.md` — 30 SW rows across A1–A7, every row traces to ≥1 DI. (2026-05-12)
- [x] **cloud-suite** — `docs/project/dhfs/cloud-suite/design-controls/requirements/software-requirements.md` — 30 platform-level SW rows across P1–P7, every row traces to ≥1 DI. Module-specific SRS deferred to child DHFs. (2026-05-12)

### Phase 3 — Rebuild + verify
- [x] Wrote project software adapter at `tools/project-console/trace-matrix/adapters/software.py` modeled on `parsers/defaults/design_inputs.py` — same GFM-table tokenizer, `SW ID` column, `Traces to DI` column. (2026-05-12)
- [x] Built all 10 DHFs: `python3 .claude/skills/trace-matrix/scripts/build.py --repo .` — SW counts: **pca-device 32 / connectivity-adapter 30 / cloud-suite 30**. DI→SW edges: **34 / 32 / 31**. (2026-05-12)
- [x] Verified DI→SW chain in each sidecar:
      - `docs/project/console/pca-device/console_trace_matrix.json` → `edges.kind="di_to_sw"` count = 34
      - `docs/project/console/connectivity-adapter/console_trace_matrix.json` → 32
      - `docs/project/console/cloud-suite/console_trace_matrix.json` → 31
- [ ] **Known side-effect, not blocking**: DI→VER broken_refs appeared after SW was added (pca-device: 4, CA: 21, cloud: 22). Root cause is the graph engine's V&V scope filter (`scripts/graph.py:81–107`): when SW exists, V&V is scoped to "tests that verify SW reqs" by requiring `vnv.traces_forward_ids` to point at SW. Default DI-derived VER nodes only carry `verifies_di_ids`, so they're filter-dropped; the resulting V&V layer ends up empty, and the DI→VER edges become broken_refs. This is a pre-existing skill design point, not something this task introduced. See Open Questions below for the follow-up.
- [ ] Inspect rendered output in console (refresh `/trace-matrix` page) — manual smoke test pending

### Phase 4 — Commit + push
- [x] Two commits landed on `origin/main` (2026-05-12, user confirmed two-commit shape + push):
      - `534a280` `ben/048-prereq: theme switch + Manrope fix + connectivity-adapter & cloud-suite UN/DI` — closes the prior-session work that had been sitting uncommitted since 2026-05-12 evening
      - `51f8294` `ben/049: SRS authoring — pca-device + connectivity-adapter + cloud-suite` — the SRS layer + project adapter + sidecar regens

## Resume Command

```bash
bash .claude/hooks/task-activate.sh add <SESSION_UUID> 049
```

## Session History

### 2026-05-12 — Task created (work paused before SRS authoring)

**Completed in the prior session** (not part of this task, but immediate predecessor — see [[task-048]] for the console-walkthrough thread):
- Theme switch to `globallogic-dark` (extends stock `dark`; preserves GL brand). Files: `tools/project-console/themes/globallogic-dark/`, `tools/project-console/console.yaml`
- Removed `510(k) submission package readiness…` description from the Submission Tracker dashboard card. File: `tools/project-console/console.yaml` (`dashboards.overrides.submission-tracker.description: ""`)
- Manrope font 404 fix via `console.overrides.css` redirecting `@font-face` to `/theme/assets/fonts/manrope-latin.woff2`. File: `.claude/skills/project-console/console/web/static/console.overrides.css` (extension-hook seam — not skill code)
- **UN + DI files authored for connectivity-adapter** (21 UN, 21 DI across A1–A7). Files: `docs/project/dhfs/connectivity-adapter/design-controls/{user-needs/user-needs.md,requirements/design-inputs.md}`
- **UN + DI files authored for cloud-suite (platform-level)** (22 UN, 22 DI across P1–P7). Files: `docs/project/dhfs/cloud-suite/design-controls/{user-needs/user-needs.md,requirements/design-inputs.md}`
- Trace matrix rebuilt for both DHFs — UN ↔ DI edges populated (21 ↔ 21 for CA, 22 ↔ 22 for cloud-suite). Sidecars at `docs/project/console/{connectivity-adapter,cloud-suite}/console_trace_matrix.{md,json}`

**In flight / not yet committed at session pause** (`git status -s` snapshot 2026-05-12 evening):
```
 M .claude/skills/project-console/console/web/static/console.overrides.css
 M docs/project/console/cloud-suite/console_trace_matrix.json
 M docs/project/console/cloud-suite/console_trace_matrix.md
 M docs/project/console/connectivity-adapter/console_trace_matrix.json
 M docs/project/console/connectivity-adapter/console_trace_matrix.md
 M tools/project-console/console.yaml
?? docs/project/dhfs/cloud-suite/design-controls/requirements/design-inputs.md
?? docs/project/dhfs/cloud-suite/design-controls/user-needs/user-needs.md
?? docs/project/dhfs/connectivity-adapter/design-controls/requirements/design-inputs.md
?? docs/project/dhfs/connectivity-adapter/design-controls/user-needs/user-needs.md
?? tools/project-console/themes/globallogic-dark/
```
**Decision at session pause**: user said "actually capture as a task, we'll continue tomorrow" — so SRS authoring + the commit/push were both deferred. Tomorrow's session should resume from Phase 1 above.

<!-- STRATEGY CONTENT: development, testing -->
**SRS authoring approach — DI-shape table + generated project adapter.** Update 2026-05-12: the original strategy block here claimed the default `software` parser is the same GFM-table tokenizer used for UN/DI and that no project adapter is required. **That's wrong.** `.claude/skills/trace-matrix/scripts/parsers/defaults/software.py` is a deliberate no-op pass-through (the layer is optional because many DHFs trace DI→V&V directly without a separate SRS). The correct pattern: (1) author SRS source docs in the DI table shape with `SW ID` + `Traces to DI` columns; (2) wire `software:` in `trace-matrix.yml` with the source path and `id_prefix: SW`; (3) run `/trace-matrix init --layer software` — `rational_check` will see 0 nodes on a populated source → `ok: false` → init generates a project adapter at `tools/project-console/trace-matrix/adapters/software.py` modeled on the doc's observed shape. The adapter is shared across all DHFs that use the same SRS shape, so one init pass on pca-device covers all three.
<!-- /STRATEGY -->

<!-- LESSONS LEARNED: skill-internals -->
**Don't trust task-doc strategy blocks about skill internals without re-reading the skill.** The 2026-05-12 task creation strategy block said the default software parser mirrors the DI tokenizer — Read of `parsers/defaults/software.py` showed it's a no-op `return ParserResult()`. This is exactly what [[feedback_read_skill_before_planning]] warns about: prior-conversation memory of skill behavior is not authoritative; the skill code is. Even when the prior session left a strategy block claiming a fact, re-verify by reading the actual file before basing a plan on it.
<!-- /LESSONS -->

<!-- LESSONS LEARNED: tooling -->
**Adding a SW layer can break the V&V layer in DHFs that relied on DI-derived VER nodes.** `scripts/graph.py:81–107` runs a scope filter: when SW is present, V&V is filtered to "tests that verify SW reqs," requiring `vnv.traces_forward_ids` to point at SW. The default DI-derived VER nodes (emitted via `extras["vnv_nodes"]` from the DI parser) carry only `verifies_di_ids`, not `traces_forward_ids→SW`, so they're filter-dropped — and the DI→VER edges that referenced them become `broken_refs`. Implication: before adding a SW layer to a DHF that has VER references in its DI doc, plan for either (a) a skill enhancement to enrich VER nodes with SW-trace info when SW references the same VER ID, or (b) authoring a dedicated V&V protocol doc. The DI→SW chain works correctly either way; the V&V layer is the casualty. Confirmed on pca-device (4 broken refs), connectivity-adapter (21), cloud-suite (22), 2026-05-12.
<!-- /LESSONS -->

<!-- LESSONS LEARNED: tooling -->
**`scripts/analyze.py` does not enumerate the `software` layer.** The script's `LAYER_KEYS` constant (`scripts/analyze.py:34`) is `["user_needs", "design_inputs", "architecture", "vnv", "risk"]` — software is missing. `scripts/build.py` handles software correctly. So `/trace-matrix analyze` and `/trace-matrix init` (which depends on analyze) silently skip the SW layer; you can't use `analyze` to drive SW-adapter generation. Workaround used: read the source doc shape, write the project adapter directly by hand, then run `build` to verify. This is a one-line fix in the skill (add `"software"` to `LAYER_KEYS`) but is out of scope for task 049.
<!-- /LESSONS -->

<!-- LESSONS LEARNED: tooling -->
**`/trace-matrix init` is one-shot, not a re-detector.** SKILL.md step 2 says it writes `trace-matrix.yml` only "if `trace-matrix.yml` does not exist." If the yml already exists pointing at the wrong source paths (e.g., conventional `user-needs.md` when the DHF has `user-needs-register.md`), init won't re-detect — it'll silently keep stale paths. Confirmed today on connectivity-adapter + cloud-suite. Implication: hand-edit `trace-matrix.yml` when a DHF's actual source filenames diverge from the convention, or delete the yml and re-init (heavyweight). [[feedback_read_skill_before_planning]] proved its worth here.
<!-- /LESSONS -->

<!-- LESSONS LEARNED: tooling -->
**Empty `missing_reason: no_items_parsed` doesn't always mean "parser broken."** Both connectivity-adapter and cloud-suite returned this verdict pre-fix; on inspection the source files were placeholder stubs containing only `{{Populate per the parent QMS template — e.g., UN/DI rows with IDs, criteria, traceability}}`. Parser was fine — the source had no items. The trace-matrix.yml path was *also* wrong (pointing at `user-needs.md` when only `user-needs-register.md` existed). Both gaps had to be fixed. Implication: when a layer reports `no_items_parsed`, check (a) does the source path exist? (b) is the file populated, not a stub? Don't assume parser bug.
<!-- /LESSONS -->

## Open Questions

- ~~**SW id_prefix**~~ — resolved: used `SW` (symmetric with `DI-NNN` in DI docs). Same prefix across all three DHFs.
- ~~**Software safety class per IEC 62304 §4.3**~~ — resolved: per-row classification omitted; system-level class declared in the SRS header (Class C for PP3500; Class B for CA-1000 and Cloud Suite platform).
- ~~**Cloud-suite scope**~~ — resolved: platform-level only (30 rows across P1–P7). Module-specific SRS deferred.
- **NEW — V&V scope-filter behavior** (raised by the Phase 3 build): when SW exists, `graph.py`'s V&V scope filter drops DI-derived VER nodes because they only know `verifies_di_ids`, not `traces_forward_ids → SW`. Result: DI→VER edges become broken_refs (pca-device 4, CA 21, cloud 22) and the V&V layer renders empty. Two fix paths:
   1. Patch the SW adapter (or build orchestrator) to enrich DI-derived VER nodes with `traces_forward_ids` populated from SW rows that reference the same VER-* ID. Keeps the V&V layer alive and removes the broken_refs.
   2. Author dedicated V&V protocol docs per DHF and wire `vnv.source:` in `trace-matrix.yml`; the V&V parser would then produce native VER nodes with explicit SW traces.
   Recommended: option 1 as a small skill enhancement (handled in a separate skill-creator task, since CLAUDE.md says skill modifications go through `/skill-creator`). Option 2 is the long-term right answer for real V&V but is a much larger authoring effort.
- **Console smoke test** — still need to manually refresh the `/trace-matrix` page in project-console to confirm rendering. Local file evidence (sidecar JSON) shows the data is correct; UI verification is the last open item.

## Changelog

| Date | Author | Summary |
|---|---|---|
| 2026-05-12 | Ben (with Claude) | Task created at session pause. Captures in-flight state, planned phases, and resume command. SRS authoring begins next session. |
| 2026-05-12 | Ben (with Claude) | **Phases 1–3 complete.** Wired `software:` blocks for the 3 DHFs in `trace-matrix.yml`. Authored 92 SW rows across pca-device (32), connectivity-adapter (30), cloud-suite (30). Wrote project software adapter at `tools/project-console/trace-matrix/adapters/software.py`. Built all 10 DHFs; DI→SW edges = 34 / 32 / 31. Discovered V&V scope-filter side effect (broken DI→VER refs); captured as new open question with two fix paths. Phase 4 (commit + push) pending user OK. |
