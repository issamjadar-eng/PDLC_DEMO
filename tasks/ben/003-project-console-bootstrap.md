# 003 — Project Console Bootstrap

**ID**: 003
**Created**: 2026-04-12
**Status**: In Progress
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

## Todos

- [x] Agree on tool name (`project-console`) and location (`tools/`)
- [x] Agree on stack (Python + FastAPI + uv, Jinja2, vanilla JS, Agent SDK with Pro/Max OAuth)
- [ ] Write `tools/project-console/ARCHITECTURE.md` as the definitive ruleset
- [ ] Enumerate the modules needed for v1 (auth, config, app factory, dashboards registry, chat router, persona loader, sources resolver, SDK client)
- [ ] Decide which dashboard and which persona to build first as the smoke test
- [ ] Scaffold `pyproject.toml`, `run.sh`, and the `console/` package skeleton
- [ ] Verify Agent SDK Pro/Max OAuth path end-to-end with a hello-world chat call

## Changelog

- 2026-04-12: Task created. Architecture decisions captured in conversation: Python + FastAPI + uv, Pro/Max OAuth only (no API key fallback), live source pulls per turn, dashboards and personas auto-discovered, no build step, no CDN.
