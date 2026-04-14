# 008 — Project Console: Dashboards, Workflows & Validation

**ID**: 008
**Created**: 2026-04-13
**Status**: In Progress
**Created By**: Ben Xavier
**Owner**: Ben Xavier
**Priority**: Medium

---

## Goals

_Complete the four-section IA of `tools/project-console/` by building out the two missing sections (dashboards, workflows), wiring the dashboard-scoped chat sidecar, validating the Claude Pro/Max OAuth path end-to-end, and refreshing the README. Task 003 delivered the chat + documents sections; this task closes the remaining gap vs. `ARCHITECTURE.md`._

- Implement `console/dashboards/` registry + first dashboard as smoke test
- Implement `console/workflows/` parameterized job runner with SSE progress
- Build the dashboard-scoped chat sidecar (embedded chat tied to a single dashboard's data)
- Wire the new dashboards/workflows routers into `app.py`
- Capture an end-to-end OAuth smoke test against a real domain agent as evidence
- Refresh `tools/project-console/README.md` to reflect the four-section IA

## Context (migrated from task 003)

Task 003 stood up `tools/project-console/` with:
- FastAPI scaffold, OAuth-only auth (refuses to start if `ANTHROPIC_API_KEY` is set)
- Chat router, SSE streaming, domain-agent loader, multi-agent panels (round-robin + LLM moderator)
- Documents browser (tree, renderer, summary)
- Populated `domain_agents/core-team/` (10 roles + design-review + core-team panels) and `domain_agents/kol/` (8 KOL personas + PP3500 KOL panels)
- Source resolution with 200KB token budget and `ResolvedSources` warning surface
- Native structured message history (`<conversation><turn>...`) — `ClaudeSDKClient` deferred until agents need tool use
- Browser-local chat thread persistence (`chat.js` thread store with sidebar, New/Rename/Delete, auto-title)

`ARCHITECTURE.md` defines four top-level sections: **Chat**, **Documents**, **Dashboards**, **Workflows**. Only the first two exist. This task builds the remaining two and validates the whole surface.

## Todos

- [ ] **Dashboards section** — implement `console/dashboards/` registry + first dashboard as smoke test
- [ ] **Workflows section** — implement `console/workflows/` parameterized job runner with SSE progress
- [ ] **Dashboard-scoped chat sidecar** — embedded chat tied to a single dashboard's data
- [ ] Wire the new dashboards/workflows routers into `app.py` once they exist
- [ ] **Verify Agent SDK Pro/Max OAuth path end-to-end** with a hello-world chat against a real domain agent and capture the result here as evidence
- [ ] Update `tools/project-console/README.md` to reflect the four-section IA (currently 26 lines, likely behind ARCHITECTURE.md)

## Changelog

- 2026-04-13: Task created. Scope and todos migrated from task 003 after its v1 (chat + documents) scope shipped. Task 003 closed out.
