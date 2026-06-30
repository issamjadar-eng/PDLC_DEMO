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

from console.config import get_config
from console.metrics.loader import load_usage

router = APIRouter()
templates = Jinja2Templates(
    directory=str(Path(__file__).parent.parent / "web" / "templates")
)


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
            # Embedded so the page renders offline with no extra round-trip.
            "usage_json": json.dumps(usage or {}),
        },
    )


@router.get("/metrics/data", response_class=JSONResponse)
async def metrics_data(request: Request):
    cfg = get_config()
    usage = load_usage(cfg.repo_root)
    if usage is None:
        raise HTTPException(status_code=404, detail="usage-metrics not available")
    return usage
