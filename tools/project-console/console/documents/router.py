import json
from pathlib import Path
from typing import AsyncIterator

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates

from console.config import get_config
from console.documents import renderer, summary, tree

router = APIRouter()
templates = Jinja2Templates(
    directory=str(Path(__file__).parent.parent / "web" / "templates")
)

SUMMARIZABLE_KINDS = {"markdown", "html", "text"}


@router.get("/documents", response_class=HTMLResponse)
async def documents_root(request: Request):
    cfg = get_config()
    entries = tree.list_dir(cfg.repo_root, "")
    return templates.TemplateResponse(
        request,
        "documents_browse.html",
        {
            "config": cfg,
            "entries": entries,
            "breadcrumbs": [("Documents", "")],
            "current": "",
        },
    )


@router.get("/documents/browse/{virtual_path:path}", response_class=HTMLResponse)
async def documents_browse(request: Request, virtual_path: str):
    cfg = get_config()
    virtual_path = virtual_path.strip("/")
    if not virtual_path:
        return RedirectResponse("/documents")
    abs_path = tree.resolve_virtual_path(cfg.repo_root, virtual_path)
    if abs_path is None:
        raise HTTPException(404, "Not found")
    if abs_path.is_file():
        return RedirectResponse(f"/documents/view/{virtual_path}")
    entries = tree.list_dir(cfg.repo_root, virtual_path)
    crumbs = tree.breadcrumbs(virtual_path)
    return templates.TemplateResponse(
        request,
        "documents_browse.html",
        {
            "config": cfg,
            "entries": entries,
            "breadcrumbs": crumbs,
            "current": virtual_path,
        },
    )


@router.get("/documents/view/{virtual_path:path}", response_class=HTMLResponse)
async def documents_view(request: Request, virtual_path: str):
    cfg = get_config()
    virtual_path = virtual_path.strip("/")
    abs_path = tree.resolve_virtual_path(cfg.repo_root, virtual_path)
    if abs_path is None or not abs_path.is_file():
        raise HTTPException(404, "File not found")
    rendered = renderer.render(abs_path)
    crumbs = tree.breadcrumbs(virtual_path)
    return templates.TemplateResponse(
        request,
        "documents_view.html",
        {
            "config": cfg,
            "rendered": rendered,
            "virtual_path": virtual_path,
            "filename": abs_path.name,
            "breadcrumbs": crumbs,
            "summarizable": rendered.kind in SUMMARIZABLE_KINDS,
        },
    )


@router.get("/documents/raw/{virtual_path:path}")
async def documents_raw(virtual_path: str):
    cfg = get_config()
    abs_path = tree.resolve_virtual_path(cfg.repo_root, virtual_path.strip("/"))
    if abs_path is None or not abs_path.is_file():
        raise HTTPException(404, "File not found")
    return FileResponse(abs_path, filename=abs_path.name)


@router.post("/documents/summary/{virtual_path:path}")
async def documents_summary(virtual_path: str):
    cfg = get_config()
    abs_path = tree.resolve_virtual_path(cfg.repo_root, virtual_path.strip("/"))
    if abs_path is None or not abs_path.is_file():
        raise HTTPException(404, "File not found")
    rendered = renderer.render(abs_path)
    if rendered.kind not in SUMMARIZABLE_KINDS:
        raise HTTPException(400, f"Cannot summarize {rendered.kind} file")

    async def event_stream() -> AsyncIterator[str]:
        try:
            async for token in summary.summarize(abs_path):
                yield f"data: {json.dumps({'type': 'token', 'text': token})}\n\n"
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
