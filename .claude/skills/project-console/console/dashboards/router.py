from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from console.config import get_config
from console.dashboards.discovery import discover

router = APIRouter()
templates = Jinja2Templates(
    directory=str(Path(__file__).parent.parent / "web" / "templates")
)


def _load_dashboards():
    cfg = get_config()
    return discover(cfg.repo_root, cfg.dashboards_config)


@router.get("/dashboards", response_class=HTMLResponse)
async def dashboards_index(request: Request):
    cfg = get_config()
    dashboards = _load_dashboards()
    return templates.TemplateResponse(
        request,
        "dashboards_index.html",
        {"config": cfg, "dashboards": dashboards},
    )


@router.get("/dashboards/{slug}", response_class=HTMLResponse)
async def dashboard_view(request: Request, slug: str):
    cfg = get_config()
    dashboards = _load_dashboards()
    dash = next((d for d in dashboards if d.slug == slug), None)
    if dash is None:
        raise HTTPException(404, f"Dashboard '{slug}' not found")
    abs_path = cfg.repo_root / dash.source
    if not abs_path.is_file():
        raise HTTPException(404, f"Dashboard source missing: {dash.source}")
    return templates.TemplateResponse(
        request,
        "dashboard_view.html",
        {"config": cfg, "dashboard": dash},
    )
