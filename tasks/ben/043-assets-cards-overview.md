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

`/overview` route now displays a card grid combining:
1. **Project overview items** — PDF and PPTX files at repo root, rendered as cards with titles
2. **Asset items** — discovered via `assets/*/index.html` scan + `<title>` tag extraction

All items are selectable cards. Clicking a card loads its content in a shared iframe viewer below the cards. Viewer includes:
- Header bar with title, "Open in tab ↗" link, and close button
- 80vh iframe displaying the content
- Card selection updates the iframe URL and highlights active card

Static serving of assets via FastAPI `StaticFiles` mount at `/assets` (with `html=True` for index.html auto-serve). Discovery is company-agnostic: activates whenever overview files exist.

Workflows card on landing page wired to `/workflows` route with descriptive text ("Automation and process templates").

## Changelog

2026-05-05 — Task created; starting exploration phase
2026-05-05 — Exploration + plan complete; starting implementation
2026-05-05 — All 4 files edited; console restarted; 3 asset cards rendering + iframe viewer working; static serving verified (initial placement on landing page)
2026-05-05 — Corrected placement: moved asset cards from landing page to /overview route; extracted discovery to overview/router.py; removed unused code from chat/router.py; wired Workflows card to /workflows (commit 2211647)
2026-05-05 — Restructured /overview to show project overview as cards (PDF + PPTX) + asset decks as selectable cards with unified iframe viewer below; users select any card to view inline; verified PDF and asset HTML decks working (commit a39609b)
