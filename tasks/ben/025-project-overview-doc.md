# 025 — Project Overview Document

**ID**: 025
**Created**: 2026-04-21
**Status**: Complete
**Created By**: Ben Xavier
**Owner**: Ben Xavier
**Priority**: Medium

---

## Goals

Author `project-overview.md` at the repo root as a guided tour of PDLC_DEMO — what the demo device is (PP3500 PCA pump), the regulatory strategy shape (510(k) + PCCP), how the project is structured (three-tier `docs/`, DHF topology, `project.yml`), how the guardrails work (skills/hooks/rules), the agentic advisor model (humans decide, agents advise), and the project-console. Modeled on `../arthrex-pccp/project-overview.md` but adapted to PDLC_DEMO specifics (PCA pump, demo-scope banner, current skill/agent/DHF inventory).

- One doc, readable cold by a stakeholder who has never opened the repo
- Reflects actual state of PDLC_DEMO (DHFs, skills, agents, strategies, submissions)
- Clearly carries the demo banner — not a real submission
- Companion artifacts: screenshots under `assets/project-overview/` and a 16-slide `.pptx` deck

## Todos

- [x] Read reference `../arthrex-pccp/project-overview.md`
- [x] Inventory PDLC_DEMO state (DHFs, skills, agents, strategies, submissions)
- [x] Draft `project-overview.md` at repo root
- [x] Cross-link appendix to actual files (CLAUDE.md, project.yml, strategies/regulatory-strategy.md, submissions/, console URLs)
- [x] Mark as demo content where applicable
- [x] Capture 8 console screenshots via chrome-devtools MCP into `assets/project-overview/`
- [x] Fix accuracy — port 8765 (not 8766), 23 agents (not 11+2), 1 dashboard (not 3), GlobalLogic theme (not Arthrex)
- [x] Wire screenshots into the markdown
- [x] Generate `project-overview.pptx` companion deck via `scripts/build-project-overview-pptx.py`
- [x] Build `project-overview.pdf` from the pptx (committed alongside for console embedding)
- [x] Add `overview` router + template + CSS to project-console skill; auto-detect `project-overview.{pdf,pptx,md}` at repo root; conditional "Overview" first-nav entry + landing tile

## Changelog

- 2026-04-21: Task created — write `project-overview.md` adapted from Arthrex PCCP reference.
- 2026-04-21: Draft landed at repo root (~250L). Structure mirrors Arthrex PCCP five-section shape (Overview & Strategy → Project Shape → Quality & Process guardrails → Agentic Approach → Project Console). Key adaptations: (a) demo-scope banner at the top + reminder in device-identity table; (b) DHF topology reflects actual PDLC_DEMO (3 top-level + 7 Cloud Suite children = 10 DHFs); (c) PP3500 filing scope — PCA device alone, Drug Library Manager TBD bundled-vs-standalone, Connectivity Adapter MDDS cyber-only pull — taken from `docs/project/strategies/regulatory-strategy.md`; (d) CtS/CtF/CtC/CtP carve-out called out in §1.2; (e) skill inventory aligned with `project.yml → security.approved_skills` (15 project skills + 4 anthropic builtin format skills); (f) advisor curation via `project.yml → advisors.enabled` (regulatory-affairs, clinical-affairs, risk-management); (g) console URL set reflects actual `tools/project-console/` layout and the unified assistant drawer from task ben/024.
- 2026-04-21: **Screenshots + pptx + accuracy pass.** Captured 8 console screenshots via chrome-devtools MCP (`console-01-landing.png` through `console-08-trace-matrix-detail.png`) into `assets/project-overview/` at 1440×900. Corrections made while taking them: (i) real console port is 8765, not 8766 — fixed globally in the markdown; (ii) real agent count is 23 (11 Core Team + 8 KOLs + 4 panels), not 11+2 as initially drafted — §2.4 expanded with a full KOL table anchored on James E. Paul as the primary PP3500 KOL; (iii) only one dashboard is discovered today (Submission Package Tracker) — §5.4 corrected with a note that others come online as their generators land; (iv) theme is GlobalLogic, not Arthrex. Generated `project-overview.pptx` (16 slides, ~1.6 MB) via new `scripts/build-project-overview-pptx.py` — standalone python-pptx builder, uses the GlobalLogic theme palette (primary `#7a00df`, accent `#0693e3`), embeds the 8 screenshots with URL captions, demo-scope slide as slide 2. No strategy/lessons content generated — pure documentation authoring.
- 2026-04-21: Task Complete. Artifacts: `project-overview.md` (36 KB), `project-overview.pptx` (1.6 MB, 16 slides), `assets/project-overview/` (8 PNGs, ~1.7 MB), `scripts/build-project-overview-pptx.py` (regen script).
- 2026-04-21: **Deck redesign pass.** User feedback: the Arthrex reference is "way nicer" and the GlobalLogic logo in the top-right was clipping. Rebuilt `scripts/build-project-overview-pptx.py` end-to-end to match the Arthrex quality bar: (i) full-bleed cover with a purple left band, logo in the band, info-block lockup on the right, a demo-scope strip at the bottom; (ii) every content slide now carries a top bar with the GlobalLogic wordmark + a `## · Section Name` chip (right-aligned, computed to stop before the logo so no overlap); (iii) sections numbered 01–06 (Overview & Strategy · Agentic Approach · Quality & Process · Humans in Charge · Project Console · Appendix); (iv) content patterns borrowed from Arthrex — 3-column accent cards, numbered deliverable cards, skill inventory table, 6-step handoff table with alternating row fills and color-coded human vs. agent rows, large agenda slide as a 5-row list with number badges; (v) screenshot slides now size the frame to match each image's actual displayed dimensions (no more tiny images floating in oversized frames); (vi) full-bleed purple thank-you slide at the end. PDF-rendered via soffice headless and spot-checked — all 22 slides pass visually. File: 1.4 MB, 22 slides (was 1.6 MB, 16 slides).
- 2026-04-21: **Console Overview section.** User asked: can the console auto-detect `project-overview.pptx` and surface it before Agents? Chose option 2 (commit pre-built PDF, serve it; no runtime soffice dep). Converted `project-overview.pptx → project-overview.pdf` (1.1 MB) alongside the pptx. Added `console/overview/{__init__,router}.py` to the `project-console` skill with a `discover(repo_root)` function that checks for `project-overview.{pdf,pptx,md}` at root, plus `/overview` (embedded PDF in iframe with view=FitH), `/overview/raw.pdf` (inline-disposed file serve), `/overview/download.pptx` (attachment). Middleware in `app.py` stashes `overview_nav` on `request.state` so `_base.html` and `index.html` can conditionally render nav + landing tile (first position, before Agents). Nothing breaks when `project-overview.*` is absent — entries just don't appear. Styled in `console.css` (hero header, action buttons, full-height iframe viewer, no-viewer fallback). Smoke-tested via curl (200 / 200) and chrome-devtools MCP — PDF renders inline with thumbnails, all 22 slides navigable. Captured `assets/project-overview/console-09-overview.png` and `console-10-landing-with-overview.png`. This is a **local delta** to the project-console skill — `/sync-skills push` upstream is a follow-up.

## Economics

_Retrospective estimate (rough; from task summary). See effort-estimation-rubric.md._

```json
{
  "economics": {
    "method_version": 1,
    "retrospective": true,
    "agentic_hours": 6,
    "todos": [
      {
        "todo": "Project overview document + deck",
        "personas": [
          "program-manager",
          "rd-lead"
        ],
        "manual_hours": {
          "min": 16,
          "max": 40
        },
        "confidence": "low",
        "basis": "36KB overview doc + 8 screenshots + 22-slide deck"
      }
    ]
  }
}
```
