# 097 — Value & ROI Table — Column Info Hover

**ID**: 097
**Created**: 2026-06-30
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
2. **Phase-end batching is OK; drift-batching is not.** Planned phases are a legitimate checkpoint — write once per phase at the phase boundary, before the next phase starts. What's not OK: accumulating updates in your head, waiting for "end of the session," "after the push," or the user to ask.
3. **A commit is not a substitute.** Git history records code; this doc records the project narrative — what was done, why, what's left, what surprised us.
4. **Resume-ready before any session boundary.** Before recommending a fresh session, marking Complete, or ending work, the doc must contain: (a) what was completed this session with concrete artifacts, (b) status of any in-flight work and temp artifacts, (c) priority-ordered next steps with file paths, (d) open questions blocking progress, (e) the exact `/task` activation command to resume.
5. **Capture strategy + lessons as they happen.** Option comparisons, scope/boundary decisions, architectural pivots, non-obvious insights, or corrected assumptions go into the appropriate section **in-flight** — not just in chat.
6. **Estimation provenance (if `## Economics` is present).** This doc's `## Economics` block is the by-hand person-hour estimate, built per the effort-estimation rubric at `.claude/skills/usage-metrics/references/effort-estimation-rubric.md` (owned by the `usage-metrics` skill). To add or refresh an estimate on resume — even without loading the task skill — read that rubric first for the anchors, personas, and JSON schema; the block also carries a `method_ref` naming it. Skip silently if `usage-metrics` isn't installed. Point to the rubric, never copy it into this doc.

Success test for this doc: a fresh Claude session, given only this file, can re-enter the work without asking the user "what were we doing?"

## Goals

_What this task aims to accomplish and why it matters to the project._

- Add an **info (?) hover tooltip** that explains each column in the project console's **Metrics ▸ Value & ROI** by-task table, so a reader understands what Agentic (hrs), By-hand (hrs), Hours saved, and Agentic $ actually mean without reading the methodology section.
- **Be honest about the units in the tooltip copy** — surface the same nuance the `agentic_hours` discussion raised: Agentic (hrs) is *human supervised time*, not machine compute, and not additive across parallel/overlapping work; By-hand is *specialist person-hours* (a labor sum); Hours saved is the difference. The hover is a chance to state the unit distinction plainly at the point of use.
- Keep it lightweight and self-consistent with the existing `vv-` styling; reuse the live-methodology source where practical so column copy doesn't drift from the rubric.

## Todos

_Actionable work items. Check off as completed._

- [x] Mechanism decided: per-column header `i` icon (`.vv-info`, `tabindex=0`, `aria-label`) with a CSS `.vv-tip` bubble shown on hover **and** keyboard focus. Edge columns (`vv-info-l`/`vv-info-r`) align the tip to the edge so it doesn't overflow the `.vv-scroll` container.
- [x] Column copy written — honest on units: Agentic (hrs) = human supervised time (not compute, not additive across overlap); By-hand (hrs) = specialist person-hours (labor sum, range); Hours saved = the difference; Agentic $ = measured token/compute cost.
- [x] Implemented in `metrics_view.html` (the `<th>` cells + scoped `vv-` CSS live in the template, not `value.js`). Info-icon click `stopPropagation` in `value.js` so it doesn't trigger the column sort.
- [x] Accessibility: focusable trigger (`tabindex=0`), `aria-label` carries the copy, `.vv-tip` is `aria-hidden`; shows on hover + focus, no layout shift.
- [x] **Top pagination** — added `.vv-pager-top` prev/next/page-info in `.vv-controls` next to the Rows selector (bottom pager kept). Refactored `value.js` pager from ID-based (`$("vv-prev")`) to **class-based** (`querySelectorAll('.vv-prev')` …) so both pagers render + disable + update in sync.
- [x] Verified live on `:8765` (restart + cache-bust): 7 info icons, top pager present, class-based wiring served, `value.js` syntax OK. _Visual hover/pager-sync confirmation pending user refresh._
- [ ] Version bump + changelog (project-console); push.

## Strategy

<!-- STRATEGY CONTENT: development, console-ux, value-roi-tab -->
Tooltip copy is a natural place to resolve the `agentic_hours` unit ambiguity for the end user (see the ben/096 close-out discussion): state at point-of-use that Agentic (hrs) = human supervised time (not compute, not additive across overlap), By-hand = specialist person-hours, Hours saved = the difference. This complements — does not replace — the bottom-of-page methodology section.
<!-- /STRATEGY CONTENT -->

## Open Questions

- Should the column copy be **sourced** (e.g., from a small definitions block the router passes in, or derived from the rubric) so it can't drift from the methodology — or is inline copy fine for v1? Lean: inline for v1, note the drift risk.
- Do the `<th>` cells live in the template (`metrics_view.html`) or are they built in `value.js`? Determines where the markup goes. (Both are candidates — the sortable headers with `data-k` were seen in the template; confirm before editing.)

## Resume

**Status:** Task just created. Scope = add per-column info hovers to the Value & ROI by-task table, with honest unit copy.
**First action on resume:** confirm whether the by-task `<th>` cells are authored in `metrics_view.html` or rendered by `value.js`, then implement the header `?` hover there.
**In-flight artifacts:** none yet. Nothing committed.

## Economics

_By-hand person-hour estimate, **filled at checkpoint** per the effort-estimation rubric (`usage-metrics` skill). Empty until the first completed todo is estimated; an empty `todos` list is ignored by the aggregator._

```json
{
  "economics": {
    "method_version": 1,
    "method_ref": ".claude/skills/usage-metrics/references/effort-estimation-rubric.md",
    "agentic_hours": {"min": 2, "max": 4},
    "todos": [
      {
        "todo": "column info hovers on 7 by-task headers (accessible, edge-aligned tooltips) + top pager + class-based pager refactor + filter repurpose (project-console 1.30.x → 1.30.8)",
        "personas": ["rd-lead"],
        "manual_hours": {"min": 3, "max": 7},
        "confidence": "med",
        "basis": "frontend: accessible tooltip system across 7 headers (hover+keyboard focus, edge-aligned to avoid clip) + top pager + ID→class pager-wiring refactor + stopPropagation + by-task filter repurpose — LOC-norm low-mid, a11y + top/bottom-sync judgment"
      },
      {
        "todo": "economics scaffold at create (task v32) + task v31 alignment (task-activate copy→symlink)",
        "personas": ["rd-lead"],
        "manual_hours": {"min": 1, "max": 3},
        "confidence": "med",
        "basis": "skill authoring: new create step-4b stub scaffold + checkpoint reword + v31 symlink migration + 2 version bumps — judgment-tier, small LOC"
      }
    ]
  }
}
```

## Changelog

- 2026-07-03: Status changed to Complete. Economics stub filled at the completion gate (rd-lead, 2–4 agentic h).
- 2026-07-03 (checkpoint recovery — no transcript): Reconciled doc vs git. The column-hover work described below as *"uncommitted / Next: push"* **shipped and is merged to `main`**: PR #87 (`1da0ad3` — economics scaffold at `create` + **column info hovers & top pager** + task v31 align) delivered the task goal, and PR #93 (`f3c433a` — by-task filter → "has agentic cost", project-console 1.30.8) followed. **Do not re-push.** All described work appears delivered — Status left `In Progress` pending user confirmation to close.
- 2026-07-01: **By-task filter repurposed (value-table follow-on).** The "measured only" checkbox filtered `r.retro` (retrospective *hours* estimates) — confusing, hid ~94/95 rows, unrelated to cost. Repurposed to **"has agentic cost"** = rows with token cost > 0 (measured or allocated), per user. `value.js` `keep()` + template label/tooltip; project-console 1.30.8.
- 2026-06-30: **Fixed the missing-economics-section gap + aligned task skill v30→v31→v32.** Diagnosis (grounded in the sister project): the `create` action never scaffolded `## Economics` — it was only added at `checkpoint` step 3b — so a task could be created *and completed* with no economics (sister-project ben/267 is Complete with none). Also: we were on task **v30** while the registry + sister were on **v31** (the `task-activate.sh` copy→symlink fix). Fix: (1) pulled task **v31** (SKILL + README) and converted our local `.claude/hooks/task-activate.sh` copy → symlink (v31 post-update); (2) authored **v32** — new `create` step 4b scaffolds an `## Economics` empty stub (`method_version`/`method_ref`/`agentic_hours: null`/`todos: []`) when usage-metrics is installed, so every task doc carries the section from birth (filled at checkpoint); checkpoint 3b reworded "add"→"fill". Backfilled this doc (097) with the stub. Validated: stub parses, empty `todos` ignored by the aggregator, fences balanced. This doc's structure (Strategy/Resume) vs 267's (Context/Why) = optional-section author discretion; base template is identical. **Uncommitted.**
- 2026-06-30: **Built column info hovers + top pagination (uncommitted).** `metrics_view.html`: added an `i` info icon to all 7 by-task `<th>` headers with an accessible `.vv-tip` tooltip (hover + keyboard focus; edge-aligned via `vv-info-l`/`vv-info-r` so tips don't clip the `.vv-scroll` container); copy states the honest unit distinction (agentic = supervised human time, not compute/not additive; by-hand = specialist person-hours; saved = difference). Added a compact top pager (`.vv-pager-top`) inside `.vv-controls` next to the Rows selector, keeping the bottom pager. `value.js`: refactored the pager wiring from ID-based to **class-based** (`.vv-prev`/`.vv-next`/`.vv-pageinfo`) so top + bottom stay in sync, and added `stopPropagation` on `.vv-info` clicks so the icon doesn't sort the column. Verified live: 7 icons, top pager, class wiring served, `value.js` syntax OK. Next: version bump + push.
- 2026-06-30: Task created — add column-explanation info hovers to the console Value & ROI by-task table; tooltip copy to state the honest unit distinction (agentic = supervised human time, by-hand = specialist person-hours) surfaced in the ben/096 close-out.
