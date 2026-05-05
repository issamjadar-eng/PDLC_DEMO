# 043 — Expose Asset Items in Project Overview

**ID**: 043
**Created**: 2026-05-05
**Status**: Complete
**Owner**: Ben Xavier
**Priority**: Medium

---

## PERMANENT RULES (do not remove)

This task document is the **session-recovery point** for this work. Keep it updated at every meaningful checkpoint.

## Goals

- Discover asset items with index.html files in the project
- Add card UI to project overview to list these assets
- Allow selection/navigation to each asset item
- Display selected asset content in the overview

## Todos

- [x] Explore project structure and find assets with index.html
- [x] Understand current project-console overview architecture
- [x] Design card layout and selection mechanism
- [x] Edit `console/app.py` — mount `assets/` at `/assets`
- [x] Edit `console/chat/router.py` — asset discovery + landing context
- [x] Edit `console/web/templates/index.html` — cards + inline viewer
- [x] Edit `console/web/static/console.css` — viewer styles
- [x] Restart console and test

## Architecture

Assets (directories with `index.html` files) in `assets/` directory are discovered via scan + title extraction, mounted at `/assets` for static serving, and rendered as card grid on `/overview` route with inline iframe viewer. Asset cards only render when assets exist (conditional in template). Company-agnostic feature.

Additionally: Workflows card on landing page wired to `/workflows` route with descriptive text ("Automation and process templates").

## Changelog

2026-05-05 — Task created; starting exploration phase
2026-05-05 — Exploration + plan complete; starting implementation
2026-05-05 — All 4 files edited; console restarted; 3 asset cards rendering + iframe viewer working; static serving verified (initial placement on landing page)
2026-05-05 — Corrected placement: moved asset cards from landing page to /overview route; extracted discovery to overview/router.py; removed unused code from chat/router.py; wired Workflows card to /workflows (commit 2211647)
