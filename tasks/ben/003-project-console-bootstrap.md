# 003 — Project Console Bootstrap

**ID**: 003
**Created**: 2026-04-12
**Status**: Complete
**Created By**: Ben Xavier
**Owner**: Ben Xavier
**Priority**: Medium

---

## Goals

_Establish `tools/project-console/` as the local web UI for project dashboards and Claude-backed chat personas, authenticated via Claude Pro/Max OAuth (no API keys, no per-call cost)._

- Document the definitive architecture and rules for the console in `tools/project-console/ARCHITECTURE.md`
- Identify the Python modules required for the initial implementation (FastAPI app, dashboard registry, chat/persona loader, Agent SDK wrapper, auth check)
- Keep the console strictly read-only with respect to `docs/`, `project.yml`, and `src/`
- Ensure the design works identically on macOS and WSL with one command

## Status snapshot (2026-04-13)

The original v1 todos are largely done — the scaffold, OAuth-only auth, chat router, panel streaming, document browser, and a populated set of domain agents (core-team + KOL groups) are all in place. The remaining gap vs. ARCHITECTURE.md is the **dashboards** and **workflows** sections, plus an end-to-end OAuth smoke test recorded as evidence.

### Done

- [x] Agree on tool name (`project-console`) and location (`tools/`)
- [x] Agree on stack (Python + FastAPI + uv, Jinja2, vanilla JS, Agent SDK with Pro/Max OAuth)
- [x] Write `tools/project-console/ARCHITECTURE.md` as the definitive ruleset (404 lines, four-section IA, OAuth rule, file-drop extensibility)
- [x] Scaffold `pyproject.toml`, `run.sh`, `uv.lock`, and the `console/` package skeleton
- [x] Implement `console/auth.py` preflight — refuses to start if `ANTHROPIC_API_KEY` is set
- [x] Implement `console/config.py` (repo root, paths, agent dir resolution)
- [x] Implement `console/chat/sdk_client.py` — claude-agent-sdk wrapper using OAuth session
- [x] Implement `console/chat/sources.py` — live per-turn source resolver from glob patterns
- [x] Implement `console/chat/domain_agents.py` — frontmatter loader with groups, solo/panel kinds, system agents
- [x] Implement `console/chat/panels.py` — multi-agent panel streaming (round-robin moderator default)
- [x] Implement `console/chat/router.py` — landing page, agents index, agent detail, SSE stream endpoint
- [x] Implement `console/documents/` — tree, renderer, summary, router (project tree browser)
- [x] Templates: `_base.html`, `index.html`, `agents_index.html`, `chat.html`, `documents_browse.html`, `documents_view.html`
- [x] Static assets: `console.css`, `chat.js`, `documents.js`, `markdown.js`, vendored fonts/img
- [x] Populate `domain_agents/core-team/` (10 roles + design-review and core-team panels)
- [x] Populate `domain_agents/kol/` (8 KOL personas + PP3500 KOL panel)

### In progress / remaining

**New top-level sections (architecture says four, only two exist):**
- [ ] **Dashboards section** — implement `console/dashboards/` registry + first dashboard as smoke test
- [ ] **Workflows section** — implement `console/workflows/` parameterized job runner with SSE progress
- [ ] **Dashboard-scoped chat sidecar** — embedded chat tied to a single dashboard's data
- [ ] Wire the new dashboards/workflows routers into `app.py` once they exist

**Agents section corrections (from 2026-04-13 review):**
- [x] **LLM-driven panel moderator** — `panels.py` now branches on `panel.moderator`. New `llm` mode runs a silent moderator (`_llm_pick_next`) that selects the next speaker each turn from the panel roster, with a hard cap of `MAX_LLM_TURNS = 6`. Panels carry a running transcript across speakers so each member sees what was already said. Example panel: `domain_agents/kol/kol-panel-pp3500-llm.md`.
- [x] **Source resolution token budget** — `sources.py` already enforced a 200KB cap; refactored to `resolve_with_meta()` returning a `ResolvedSources` dataclass with `included`, `skipped`, `truncated`, and human-readable `warnings`. `router.py` and `panels.py` now emit `{"type": "warning"}` SSE events that the chat UI renders as a yellow banner. Old `resolve()` kept as a thin wrapper.
- [x] **Native message history** — `router._format_prompt` reformatted from `User:/Assistant:` plain text to a structured `<conversation><turn role="...">...</turn></conversation>` envelope with the latest user message broken out. The agents in this project don't use tools, so the SDK's stateful client (`ClaudeSDKClient`) is overkill for now; documented as the future path if any agent ever needs tool use.
- [x] **Investigate `is_system` agents** — not dead code. `router.py:66,117` filters `_`-prefixed agents from the index and from being chatted with directly, so they can still be loaded and referenced internally (e.g., a future `_moderator.md` system prompt). Convention preserved.
- [x] **Chat history persistence (browser-local)** — `chat.js` rewritten with a per-agent thread store at `project-console:threads:v1:<agent>` containing `{threads, order, activeId}`. New sidebar lists all threads with title + relative time, supports New / Rename / Delete and click-to-switch. Auto-titles from the first user message. Migration: old `project-console:chat:<agent>` keys are converted to a single thread on first load and removed.

**Validation & docs:**
- [ ] **Verify Agent SDK Pro/Max OAuth path end-to-end** with a hello-world chat against a real domain agent and capture the result here as evidence
- [ ] Update `README.md` to reflect the four-section IA (currently 26 lines, likely behind ARCHITECTURE.md)

## Changelog

- 2026-04-12: Task created. Architecture decisions captured in conversation: Python + FastAPI + uv, Pro/Max OAuth only (no API key fallback), live source pulls per turn, dashboards and personas auto-discovered, no build step, no CDN.
- 2026-04-13: Refreshed status — the original v1 todos (architecture doc, scaffold, chat/documents routers, OAuth preflight, populated agent corpus) are complete. Remaining work is the dashboards + workflows sections, dashboard-scoped chat sidecar, an end-to-end OAuth smoke test, and a README refresh.
- 2026-04-13: Reviewed the agents section. Added five corrections (LLM moderator, source token budget, native message history, `is_system` cleanup, browser-local chat history persistence with thread list per agent/panel).
- 2026-04-13: **Task closed out.** V1 scope (architecture doc, FastAPI+uv scaffold, OAuth-only auth, chat router with SSE streaming, multi-agent panels with round-robin + LLM moderator, documents browser, populated core-team + KOL agent corpus, source token budget with warnings, native structured message history, browser-local chat thread persistence) shipped. Remaining work (dashboards section, workflows section, dashboard-scoped chat sidecar, wiring new routers into `app.py`, end-to-end OAuth smoke test, README refresh to four-section IA) migrated to task 008.
- 2026-04-13: Implemented all five agents-section corrections. New files: `domain_agents/kol/kol-panel-pp3500-llm.md`. Modified: `chat/sources.py`, `chat/panels.py`, `chat/sdk_client.py`, `chat/router.py`, `web/templates/chat.html`, `web/static/chat.js`, `web/static/console.css`. Imports verified clean via `uv run python -c`.
