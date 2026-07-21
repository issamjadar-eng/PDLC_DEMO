"""Tasks section routes.

GET /tasks              — the activity summary page (no full task list)
GET /tasks/summary.json — the raw derived summary (debug / machine consumers)

Pure consumer of the `task` skill's `/task summary` artifact
(tasks/task-summary.json). Category icons come from the artifact's
`category_icons` map (project-tunable via tasks/task-summary-config.json) —
nothing project-specific lives in this module. Discovery-gated nav, same
pattern as Metrics / Gap Analysis.
"""
from __future__ import annotations

import html as _html
import re as _re
from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from console.config import get_config
from console.tasks_view.loader import discover, load_summary  # noqa: F401

router = APIRouter()
templates = Jinja2Templates(
    directory=str(Path(__file__).parent.parent / "web" / "templates")
)

FALLBACK_ICON = "📌"


def _md_inline(text: str) -> str:
    """Escape + minimal inline markdown (`code`, **bold**, [label](url) → label).
    For one-liners where a full <p>-wrapped markdown render is unwanted."""
    s = _html.escape(text or "")
    s = _re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", s)
    s = _re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = _re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    return s


@router.get("/tasks", response_class=HTMLResponse)
async def tasks_page(request: Request):
    cfg = get_config()
    s = load_summary(cfg.repo_root)
    if s:
        icons = s.get("category_icons") or {}
        for t in s.get("open_tasks", []):
            t["_summary_html"] = _md_inline(t.get("summary", ""))
            t["_icon"] = icons.get(t.get("category"), FALLBACK_ICON)
        for h in s.get("recent", {}).get("highlights", []):
            h["_line_html"] = _md_inline(h.get("line", ""))
            h["_icon"] = icons.get(h.get("category"), FALLBACK_ICON)
        s["_cat_icons"] = icons
    return templates.TemplateResponse(
        request, "tasks_view.html", {"config": cfg, "s": s},
    )


@router.get("/tasks/summary.json", response_class=JSONResponse)
async def tasks_summary_json():
    cfg = get_config()
    s = load_summary(cfg.repo_root)
    return JSONResponse(
        s or {"error": "tasks/task-summary.json missing — run /task summary"}
    )
