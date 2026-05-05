# 044 — Submission Tracker Console Integration Recovery

**ID**: 044
**Created**: 2026-05-05
**Status**: In Progress
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

**2026-05-05**
- Created task 044 to address broken tracker console integration
- Investigated project-console v1.9.0 changes (no impact to tracker)
- Discovered root cause: markdown structure incompatibility
- Filing HTML exists but is empty (rows: 0) due to parser failure
- Solution: restructure submission-tracker.md to Phase-based format

**Session ID**: 67f320cb-23ed-4818-8355-07e973d7a3b7

---

## Recovery Command

To activate this task in a new session:
```bash
bash .claude/hooks/task-activate.sh add 67f320cb-23ed-4818-8355-07e973d7a3b7 044
```
