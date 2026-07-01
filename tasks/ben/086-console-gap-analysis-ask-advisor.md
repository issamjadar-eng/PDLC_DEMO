# 086 — Console Gap-Analysis: Ask-an-Advisor with Context Injection

**ID**: 086
**Created**: 2026-06-11
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

Add an "ask an advisor" capability to the project-console **Gap Analysis** view, mirroring how the Documents tab offers the unified Assistant drawer (ben/024) — but with the **selected gap analysis injected as grounding context** so the advisor answers against the specific analysis the user is viewing.

- Reuse the shared assistant drawer / advisor-ask pattern already shipped for the Documents tab (shared partial + `assistant.js` + `/assistant/chat/stream`).
- When a gap analysis is selected in the Gap Analysis tab, the ask-advisor flow injects that analysis's content (and its sidecar metadata) into the advisor's context.
- Keep the change inside the `project-console` skill scaffold (skill-owned code) + project `sync` so the console picks it up; respect the skill's ownership classes.

## Todos

- [x] Ground: read `project-console` SKILL.md + gap-analysis view code + Documents-tab assistant integration
- [x] Ground: read `gap-analysis` SKILL.md (render action / JSON sidecars consumed by console)
- [x] Design: context-injection mechanism for selected gap analysis into assistant drawer
- [x] Implement in skill-owned scaffold code
- [x] Restart console (`start.sh`) + browser-verify in Chrome (no `sync` needed — `console/` package is imported via PYTHONPATH, effective on restart)
- [x] Update skill VERSION/changelog
- [x] Drive-by bug fix: edit-mode banner visible on all drawer pages (inline `display:flex` defeating `hidden`)
- [x] Push to project repo (PR #54 → merged `6cda697`)
- [x] Push to skill registry (hitachi PR #216 → squash-merged `9e6a305`; local checkout fast-forwarded; sync branch deleted)

## Design (decided 2026-06-11)

<!-- STRATEGY CONTENT: architecture, console assistant-drawer reuse -->
- **Key discovery:** `console/gap_analysis/router.py` already shipped a `/gap-analysis/{id}/grounding` endpoint (since console 1.23.0) whose docstring says it exists for the assistant drawer — it was never wired to a template. The whole feature is front-end wiring, zero new backend surface.
- **Mount point:** the gap-analysis **detail** view (`gap_analysis_view.html`) — "the selected gap analysis" = the one open. The index page keeps no drawer (no selection state there; Documents-tab analog is the disabled-until-selected FAB, but cards navigate immediately).
- **Grounding injection:** drawer `grounding_source: "url:/gap-analysis/<id>/grounding"` (same pattern as trace-matrix view) — compact text rendition (meta + grounding + advisors + assertions + findings + recommendations) fetched at send time, injected as `GAP ANALYSIS CONTEXT` Tier-1 focus.
- **Default agent = the analysis's primary advisor** (`_default_advisor` in `_decorate_detail`: first `role: primary`, fallback first agent). Sidecar agent names match the console roster (verified: `cybersecurity`, `risk-management`, `regulatory-affairs`); `assistant.js` gracefully falls back if a name doesn't resolve. Agent picker left unrestricted (`allowed_agents: []`).
- **Thread scope** `ga:<id>` — per-analysis localStorage threads.

<!-- LESSONS LEARNED: frontend, hidden-attribute semantics -->
**Inline `display` silently defeats the HTML `hidden` attribute.** The drawer partial's edit-mode banner (`#pc-edit-mode-bar`) had `hidden` in markup AND `display:flex` in its inline `style=` — author inline styles outrank the UA stylesheet's `[hidden]{display:none}`, so the banner rendered on every page hosting the drawer (Documents, Trace Matrix, Tracker, and the new Gap Analysis mount) since the inline style landed (~May upstream pull). Nobody noticed because the bar sits inside the off-canvas drawer. **Why it matters:** any element that pairs `hidden` with an inline `display` is a latent always-visible bug; a11y snapshots surface it (the element appeared in the snapshot tree — that was the tell). **How to apply:** never put `display:` in inline styles of elements toggled via `hidden`; use a `#el:not([hidden]) { display:flex }` rule (or toggle a class). When browser-verifying, treat unexpected elements in the a11y snapshot as real rendering, not snapshot noise.

## Changelog

- 2026-06-11: Task created.
- 2026-06-11: Implemented — `console/gap_analysis/router.py` (`_default_advisor` decoration) + `console/web/templates/gap_analysis_view.html` (drawer + launcher mount, trace-matrix pattern). Skill VERSION 1.25.0 → 1.26.0; SKILL.md frontmatter realigned (was stale at 1.17.0); README changelog entry added.
- 2026-06-11: Browser-verified end-to-end on `/gap-analysis/hipaa-readiness-profile` — launcher renders, drawer opens titled "Gap Analysis Advisor / hipaa-readiness-profile", agent picker defaulted to Cybersecurity Assistant (the analysis's primary advisor), `/grounding` endpoint returns 35 KB compact rendition (HTTP 200), zero console errors. Live SSE smoke test: asked "which assertions are refuted" → advisor answered A10 (F-6) + A11 (F-8), exactly matching the sidecar — grounding injection confirmed working.
- 2026-06-11: Drive-by bug found + fixed during verification: `_assistant_drawer.html` edit-mode banner visible on ALL drawer pages (inline `display:flex` overrides `hidden`; pre-existing since a May upstream pull). Fix: moved `display:flex` to a `#pc-edit-mode-bar:not([hidden])` rule. Re-verified: `display:none` when hidden; B3's `bar.hidden=false` reveal path unaffected. Folded into the 1.26.0 changelog entry.
- 2026-06-12: **Shipped both repos; task Complete.** Project: branch `ben/086-gap-analysis-ask-advisor` → PR #54 → merged `6cda697` (commit `785ae50`, 8 files). Registry: `/sync-skills push --merge` of the 6 project-console files → hitachi PR #216 → squash-merged `9e6a305`; local hitachi checkout fast-forwarded, sync branch deleted both sides; sync-log entry appended. Preflight `check --analyzed` showed all 6 files LOCAL_AHEAD (clean push on top of the ben/085 drift-0 baseline). Nothing in flight.

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
        "todo": "Console gap-analysis ask-an-advisor",
        "personas": [
          "rd-lead"
        ],
        "manual_hours": {
          "min": 10,
          "max": 24
        },
        "confidence": "low",
        "basis": "gap-analysis ask-advisor drawer + grounding"
      }
    ]
  }
}
```
