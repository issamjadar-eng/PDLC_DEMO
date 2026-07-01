"""Metrics section routes.

GET /metrics        — team token-usage + cost dashboard (rendered from usage.json)
GET /metrics/data   — raw team JSON (debug / API)

The console is a generic consumer of the `usage-metrics` skill's published
`tools/usage-metrics/usage.json` (anonymized, schema `usage-metrics/team/v1`).
The page embeds that JSON and builds the visualization client-side (metrics.js).
"""
from __future__ import annotations

import json
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

import markdown as _md_lib

from console.config import get_config
from console.metrics.loader import load_usage

router = APIRouter()
templates = Jinja2Templates(
    directory=str(Path(__file__).parent.parent / "web" / "templates")
)

# The estimation methodology shown at the bottom of the Value tab is rendered
# LIVE from the usage-metrics skill's rubric — so updating the rubric (or pulling
# a newer skill via /sync-skills) updates the console with no duplication.
RUBRIC_REL = ".claude/skills/usage-metrics/references/effort-estimation-rubric.md"

_STATIC_DIR = Path(__file__).parent.parent / "web" / "static"


def _asset_version() -> str:
    """Cache-bust token = newest mtime across the metrics/value static assets.

    Restarting the console changes the files but not the URL, so browsers keep
    serving a stale value.js. Appending ?v=<mtime> forces a refetch whenever the
    JS actually changes (and nothing more) — no manual hard-refresh needed.
    """
    latest = 0.0
    for name in ("metrics.js", "value.js"):
        try:
            latest = max(latest, (_STATIC_DIR / name).stat().st_mtime)
        except OSError:
            pass
    return str(int(latest))


def _methodology_html(repo_root: Path) -> str:
    p = repo_root / RUBRIC_REL
    if not p.is_file():
        return ""
    try:
        text = p.read_text(encoding="utf-8")
    except OSError:
        return ""
    return _md_lib.markdown(text, extensions=["tables", "fenced_code", "sane_lists"])


@router.get("/metrics", response_class=HTMLResponse)
async def metrics_index(request: Request):
    cfg = get_config()
    usage = load_usage(cfg.repo_root)
    return templates.TemplateResponse(
        request,
        "metrics_view.html",
        {
            "config": cfg,
            "available": usage is not None,
            # Embedded so the page renders offline with no extra round-trip. The
            # Value/ROI sub-tab applies the $ overlay from console-side labor rates
            # (the contentious assumption stays out of the committed data).
            "usage_json": json.dumps(usage or {}),
            "labor_rates_json": json.dumps(cfg.labor_rates),
            "currency": cfg.value_currency,
            "methodology_html": _methodology_html(cfg.repo_root),
            "asset_v": _asset_version(),
        },
    )


@router.get("/metrics/data", response_class=JSONResponse)
async def metrics_data(request: Request):
    cfg = get_config()
    usage = load_usage(cfg.repo_root)
    if usage is None:
        raise HTTPException(status_code=404, detail="usage-metrics not available")
    return usage
