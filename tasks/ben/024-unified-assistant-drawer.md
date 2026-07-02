# 024 — Unified Assistant Drawer (reusable sidecar across console sections)

**ID**: 024
**Created**: 2026-04-21
**Status**: Complete
**Created By**: Ben Xavier
**Owner**: Ben Xavier
**Priority**: Medium

---

## Goals

Extract the bespoke Systems Engineering Assistant drawer from `trace_matrix_view.html` into a reusable **Assistant drawer** partial that any console page can mount with page-supplied parameters: default agent, allowed-agents list, grounding source URL, and a scope key for thread persistence. Mount it on the Documents explorer first; retire the trace-matrix custom drawer in the same change so there is a single implementation. Dashboards sidecar migration is deferred to a follow-up.

- One chat drawer used across Documents, Trace Matrix (and later Dashboards)
- Page picks the default agent + allowed agents + grounding URL
- Grounding content is pulled from a page-supplied URL at request time, capped server-side
- Thread history stays client-side (localStorage), keyed by page-supplied scope

## Todos

- [x] Add `GET /agents/api/list` returning non-system solo agents as JSON
- [x] Add `POST /assistant/chat/stream` (SSE) — unified streaming endpoint
- [x] Add `_assistant_drawer.html` Jinja partial with `data-*` parameters
- [x] Add `assistant.js` — generic drawer JS (thread select, history, streaming, markdown render)
- [x] Add assistant drawer CSS block to `console.css` (renamed from `tm-assistant-*` → `pc-assistant-*`)
- [x] Include the partial on Documents explorer and wire default agent + doc grounding URL
- [x] Swap Trace Matrix view to use the generic drawer (default agent: `systems-engineering`)
- [x] Relaunch console via `./run.sh`

## Changelog

- 2026-04-21: Task created. Plan: extract the drawer into a shared partial, unify endpoint, mount on Documents, replace on Trace Matrix, restart.
- 2026-04-21: v1 landed. New `console/assistant/router.py` with `GET /assistant/api/agents` + `POST /assistant/chat/stream` (solo agents only; grounding capped at 80 KB). New `_assistant_drawer.html` partial + `assistant.js` + scoped `pc-assistant-*` CSS in `console.css`. Documents explorer mounts it with a floating FAB; grounding comes from `window.pcAssistantGetGrounding()` which fetches the selected file at send time. Trace Matrix view swapped to the generic drawer with grounding via `url:/trace-matrix/{dhf}/grounding` (new endpoint serves compact context). Old `tm-assistant-*` CSS + JS stripped from `trace_matrix_view.html` (~560 lines removed). Console relaunched on :8765 — smoke: agent list returns 10 agents, Documents page includes drawer + FAB markup, Trace Matrix view renders with 13 `pc-assistant` occurrences and 0 legacy message-element IDs. Dashboards sidecar migration deferred (no consumer yet in this project).
- 2026-06-08: Closed Complete via task-doc audit — v1 landed + smoke-tested; shared assistant drawer mounted system-wide; dashboards-sidecar explicitly deferred. Moved to Completed in 000-index.md.

<!-- STRATEGY CONTENT: architecture, console -->
## Strategy

**Decision:** One generic Assistant drawer instead of per-section bespoke sidecars. The drawer is fully parameterized by `data-*` attributes on its root `<aside>`: `scope` (localStorage thread key), `endpoint` (unified `/assistant/chat/stream`), `default-agent`, `agents` (allowlist), `grounding-url` (page-owned), and `grounding-label` (what to call the grounded item). The page owns selection state and grounding URL; the drawer owns chat UX, thread persistence, and streaming.

**Why:** Before this, the SE Assistant was hard-coded to the trace-matrix sidecar format, and the dashboards sidecar (CHAT_ENABLED + chat_context()) was a near-duplicate. Adding a third bespoke drawer for Documents would have triplicated ~550 lines of JS/CSS. Extracting now keeps the blast radius small (one consumer, one follow-up migration) and forces the contract to be minimal.

**How to apply:** Any new section that wants a chat drawer includes the `_assistant_drawer.html` partial and hands it the five `data-*` attributes. Grounding is fetched from the page-supplied URL; the unified endpoint caps it at 80 KB server-side. Do **not** add section-specific hooks into the drawer partial — if a section needs specialized grounding, it exposes a new GET endpoint and points the drawer at it.

