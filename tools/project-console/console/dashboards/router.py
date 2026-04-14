from dataclasses import dataclass
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from console.config import get_config

router = APIRouter()
templates = Jinja2Templates(
    directory=str(Path(__file__).parent.parent / "web" / "templates")
)


@dataclass(frozen=True)
class Dashboard:
    slug: str
    title: str
    description: str
    source: str  # virtual path under repo_root

    @property
    def embed_url(self) -> str:
        return f"/documents/raw/{self.source}"

    @property
    def source_url(self) -> str:
        return f"/documents#path={self.source}"


DASHBOARDS: dict[str, Dashboard] = {
    "submission-tracker": Dashboard(
        slug="submission-tracker",
        title="Submission Package Tracker",
        description="510(k) submission package readiness across base submission, PCCP, and supporting engineering artifacts.",
        source="docs/project/submissions/submission-tracker.html",
    ),
}


@router.get("/dashboards", response_class=HTMLResponse)
async def dashboards_index(request: Request):
    cfg = get_config()
    return templates.TemplateResponse(
        request,
        "dashboards_index.html",
        {"config": cfg, "dashboards": list(DASHBOARDS.values())},
    )


@router.get("/dashboards/{slug}", response_class=HTMLResponse)
async def dashboard_view(request: Request, slug: str):
    dash = DASHBOARDS.get(slug)
    if dash is None:
        raise HTTPException(404, f"Dashboard '{slug}' not found")
    cfg = get_config()
    abs_path = cfg.repo_root / dash.source
    if not abs_path.is_file():
        raise HTTPException(404, f"Dashboard source missing: {dash.source}")
    return templates.TemplateResponse(
        request,
        "dashboard_view.html",
        {"config": cfg, "dashboard": dash},
    )
