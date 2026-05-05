"""Overview router — serves `project-overview.pdf` (preferred) or `.pptx` at
repo root as an embedded full-page PDF, with download links to both. Nav is
added conditionally by the base template when discovery finds either file.
"""

from __future__ import annotations

import re
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

from console.config import get_config

router = APIRouter()
templates = Jinja2Templates(
    directory=str(Path(__file__).parent.parent / "web" / "templates")
)


def _extract_asset_title(html_path: Path) -> str | None:
    try:
        text = html_path.read_text(encoding="utf-8", errors="ignore")
        m = re.search(r"<title[^>]*>([^<]+)</title>", text, re.IGNORECASE)
        return m.group(1).strip() if m else None
    except Exception:
        return None


def _discover_assets(repo_root: str) -> list[dict]:
    assets_dir = Path(repo_root) / "assets"
    items = []
    if assets_dir.is_dir():
        for sub in sorted(assets_dir.iterdir()):
            if sub.is_dir() and (sub / "index.html").exists():
                raw_title = _extract_asset_title(sub / "index.html")
                title = raw_title or sub.name.replace("-", " ").title()
                items.append({"name": sub.name, "title": title, "url": f"/assets/{sub.name}/"})
    return items


def discover(repo_root: Path) -> dict:
    """Return which overview assets exist at repo root.

    Keys: `pdf`, `pptx`, `md` — each is a repo-relative string path or None.
    `has_viewer` is True when something embeddable (today: the PDF) is present.
    """
    pdf = repo_root / "project-overview.pdf"
    pptx = repo_root / "project-overview.pptx"
    md = repo_root / "project-overview.md"
    return {
        "pdf": "project-overview.pdf" if pdf.is_file() else None,
        "pptx": "project-overview.pptx" if pptx.is_file() else None,
        "md": "project-overview.md" if md.is_file() else None,
        "has_viewer": pdf.is_file(),
        "has_any": pdf.is_file() or pptx.is_file() or md.is_file(),
    }


@router.get("/overview", response_class=HTMLResponse)
async def overview_page(request: Request):
    cfg = get_config()
    found = discover(cfg.repo_root)
    if not found["has_any"]:
        raise HTTPException(404, "No project-overview.{pdf,pptx,md} at repo root")
    return templates.TemplateResponse(
        request,
        "overview.html",
        {"config": cfg, "found": found, "asset_items": _discover_assets(cfg.repo_root)},
    )


@router.get("/overview/raw.pdf")
async def overview_raw_pdf():
    cfg = get_config()
    pdf = cfg.repo_root / "project-overview.pdf"
    if not pdf.is_file():
        raise HTTPException(404, "project-overview.pdf not found")
    # inline so the browser embeds in <iframe>
    return FileResponse(
        pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": 'inline; filename="project-overview.pdf"'},
    )


@router.get("/overview/download.pptx")
async def overview_download_pptx():
    cfg = get_config()
    pptx = cfg.repo_root / "project-overview.pptx"
    if not pptx.is_file():
        raise HTTPException(404, "project-overview.pptx not found")
    return FileResponse(
        pptx,
        media_type=(
            "application/vnd.openxmlformats-officedocument.presentationml.presentation"
        ),
        filename="project-overview.pptx",
    )
