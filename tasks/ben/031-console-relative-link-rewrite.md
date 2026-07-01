# 031 — Console Relative-Link Rewriter + Expose dhf-manifest Data

**ID**: 031
**Created**: 2026-04-27
**Status**: Complete
**Created By**: Ben Xavier
**Owner**: Ben Xavier
**Priority**: Medium

---

## PERMANENT RULES (do not remove)

This task document is the **session-recovery point** for this work. If the current session drops, is compacted, or ends, the next session must be able to load **this file alone** and continue where we left off.

1. Update at every meaningful checkpoint (HARD RULE).
2. Phase-end batching is OK; drift-batching is not.
3. A commit is not a substitute.
4. Resume-ready before any session boundary.
5. Capture strategy + lessons as they happen.

## Goals

Cross-document hyperlinks in the project-console documents explorer don't connect — `qms-index.md` was the trigger but the bug affects every relative `.md`/image link in the rendered tree. Also expose `.claude/skills/dhf-manifest/data` as a virtual root so deep-links into manifest data resolve.

- Fix relative-link resolution in `console/documents/renderer.py` so `<a href>` and `<img src>` in rendered markdown resolve to console deep-links (`/documents/view/...` and `/documents/raw/...`) computed against the source doc's virtual path.
- Add `.claude/skills/dhf-manifest/data` (and `.claude/skills/medtech-docs/references`) to `console.yaml` `grounding.extra_roots` so the multi-segment root machinery in `tree.py` exposes them as browsable virtual roots — matching the arthrex-pccp setup.
- Verify links in `qms-index.md`, the DHF README trees, and a sampled set of cross-folder links resolve.

## Todos

- [x] Confirm all 55 QMS docs exist on disk; problem is purely link rewriting.
- [x] Confirm `tree.py` already supports multi-segment grounding roots (no code change needed there).
- [x] Add `_rewrite_relative_links()` post-processor in `console/documents/renderer.py`.
- [x] Thread virtual_path through `renderer.render()` callers (`documents/router.py:54`, `documents/router.py:171`, `workflows/router.py:111`).
- [x] Update `tools/project-console/console.yaml` to add `extra_roots` for `medtech-docs/references` and `dhf-manifest/data`.
- [x] Restart console and click-test: qms-index links, cross-tree DHF→QMS link, deep paths.
- [x] Push fix upstream to hitachi — PR #83 merged at `8ddfbe1`; arthrex-pccp picks it up on next pull.

## Notes

- Renderer uses `markdown` lib; `_md.convert(...)` returns HTML with raw author-written hrefs.
- Deep-link route already exists: `/documents/view/{virtual_path}` redirects to `/documents#path=...`. For images, `/documents/raw/{virtual_path}` serves inline media.
- arthrex-pccp uses identical renderer/tree code — the link rewriter is missing there too. Can push the fix upstream to hitachi after local verification.

## Changelog

- 2026-04-27: Task created. Diagnosis complete: renderer emits raw relative hrefs that the browser resolves against `/documents`, hence the 404s. Fix is a post-processing pass in `_render_markdown` that rewrites non-absolute hrefs to `/documents/view/<resolved_virtual_path>`.
- 2026-04-27: Fix landed and verified live.
  - `console/documents/renderer.py`: added `_rewrite_relative_links()` post-pass + threaded `virtual_path` through `render()` and `_render_markdown()`. Skips absolute schemes (`http`, `https`, `mailto`, etc.), `//`, root-relative `/`, anchors `#`, and links that escape the virtual root with `../`. Images route to `/documents/raw/<vp>` for inline display; everything else routes to `/documents/view/<vp>`.
  - `console/documents/router.py:54,171`: pass `virtual_path` into `renderer.render()`. `console/workflows/router.py:111`: same, using `d.virtual_path`.
  - `tools/project-console/console.yaml`: added `grounding.extra_roots` with `.claude/skills/medtech-docs/references` and `.claude/skills/dhf-manifest/data`. Tree.py already supported multi-segment roots — no code change there.
  - Verified live (port 8765 restart): `qms-index.md` category-README and document links rewrite to `/documents/view/docs/internal/source-md/...`; cross-tree link from `docs/project/dhfs/connectivity-adapter/cybersecurity/GL-SOP-SW-004-vulnerability-management-plan.md` → `../../../../internal/source-md/qms-index.md` resolves to `/documents/view/docs/internal/source-md/qms-index.md`; `dhf-manifest/data` and `medtech-docs/references` show as virtual roots in `/documents/api/tree`.
  - Same renderer code lives in arthrex-pccp (file diff was empty against PDLC). Fix is portable upstream via `/sync-skills push project-console`.
- 2026-04-27: Pushed upstream and merged. Branch `sync/pdlc-demo-console-link-rewriter-2026-04-27`, PR https://github.com/GlobalLogic-a-Hitachi-Company/hitachi/pull/83, squash-merged at `8ddfbe1db08c141cdfa9cc5b2639fff0c28842e0`. Local hitachi checkout fast-forwarded to `8ddfbe1`. Sync log updated. Task closed; arthrex-pccp will pick up the fix on its next `/sync-skills pull`.

## Economics

_Retrospective estimate (rough; from task summary). See effort-estimation-rubric.md._

```json
{
  "economics": {
    "method_version": 1,
    "retrospective": true,
    "agentic_hours": 4,
    "todos": [
      {
        "todo": "Console relative-link rewriter",
        "personas": [
          "rd-lead"
        ],
        "manual_hours": {
          "min": 6,
          "max": 16
        },
        "confidence": "low",
        "basis": "relative-link rewriter in console renderer"
      }
    ]
  }
}
```
