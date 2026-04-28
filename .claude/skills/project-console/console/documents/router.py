import dataclasses
import json
from pathlib import Path
from typing import AsyncIterator
from urllib.parse import quote

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import (
    FileResponse,
    HTMLResponse,
    JSONResponse,
    RedirectResponse,
    StreamingResponse,
)
from fastapi.templating import Jinja2Templates

from console.config import get_config
from console.documents import renderer, summary, tree

router = APIRouter()
templates = Jinja2Templates(
    directory=str(Path(__file__).parent.parent / "web" / "templates")
)

SUMMARIZABLE_KINDS = {"markdown", "html", "text"}


@router.get("/documents", response_class=HTMLResponse)
async def documents_explorer(request: Request):
    cfg = get_config()
    return templates.TemplateResponse(
        request,
        "documents_explorer.html",
        {"config": cfg},
    )


# ---------------- JSON APIs for the explorer UI ----------------


@router.get("/documents/api/tree")
async def api_tree():
    cfg = get_config()
    return JSONResponse({"nodes": tree.list_tree(cfg.repo_root, max_depth=3)})


@router.get("/documents/api/children")
async def api_children(path: str = Query(...)):
    cfg = get_config()
    return JSONResponse({"children": tree.list_children(cfg.repo_root, path)})


def _file_payload(virtual_path: str, abs_path: Path) -> dict:
    rendered = renderer.render(abs_path)
    # URL-encode path segments but keep the slashes as separators so
    # filenames with spaces or special characters still resolve.
    encoded = quote(virtual_path, safe="/")
    return {
        "path": virtual_path,
        "filename": abs_path.name,
        "kind": rendered.kind,
        "extension": rendered.extension,
        "size": rendered.size,
        "frontmatter": _jsonable(rendered.frontmatter),
        "body_html": rendered.body_html,
        "body_text": rendered.body_text,
        "summarizable": rendered.kind in SUMMARIZABLE_KINDS,
        "raw_url": f"/documents/raw/{encoded}",
        "download_url": f"/documents/download/{encoded}",
    }


@router.get("/documents/api/folder")
async def api_folder(path: str = Query(...)):
    cfg = get_config()
    abs_path = tree.resolve_virtual_path(cfg.repo_root, path.strip("/"))
    if abs_path is None or not abs_path.is_dir():
        raise HTTPException(404, "Folder not found")
    readme = tree.find_folder_readme(abs_path)
    if readme is None:
        return JSONResponse({"path": path, "readme": None})
    rel = readme.relative_to(cfg.repo_root)
    # Re-derive virtual path (same prefix rules as resolve_virtual_path).
    readme_virtual = f"{path.rstrip('/')}/{readme.name}"
    return JSONResponse({"path": path, "readme": _file_payload(readme_virtual, readme)})


@router.get("/documents/api/file")
async def api_file(path: str = Query(...)):
    cfg = get_config()
    abs_path = tree.resolve_virtual_path(cfg.repo_root, path.strip("/"))
    if abs_path is None or not abs_path.is_file():
        raise HTTPException(404, "File not found")
    return JSONResponse(_file_payload(path, abs_path))


def _jsonable(value):
    if dataclasses.is_dataclass(value):
        return dataclasses.asdict(value)
    if isinstance(value, dict):
        return {k: _jsonable(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_jsonable(v) for v in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


# ---------------- Deep-link compatibility ----------------


@router.get("/documents/view/{virtual_path:path}", response_class=HTMLResponse)
async def documents_view(virtual_path: str):
    # Legacy deep-link target — redirect into the explorer with a path fragment
    # so existing <a href="/documents/view/..."> links (from agent source lists)
    # still work.
    return RedirectResponse(f"/documents#path={virtual_path.strip('/')}")


_PDF_MEDIA_TYPE = "application/pdf"


def _inline_media_type(abs_path: Path) -> str | None:
    ext = abs_path.suffix.lower()
    return {
        ".pdf": _PDF_MEDIA_TYPE,
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".gif": "image/gif",
        ".svg": "image/svg+xml",
        ".webp": "image/webp",
        ".html": "text/html",
        ".htm": "text/html",
    }.get(ext)


@router.get("/documents/raw/{virtual_path:path}")
async def documents_raw(virtual_path: str):
    """Serve a file inline (for in-browser viewing). No Content-Disposition
    attachment header — the browser displays PDFs, images, and HTML inline
    instead of forcing a download."""
    cfg = get_config()
    abs_path = tree.resolve_virtual_path(cfg.repo_root, virtual_path.strip("/"))
    if abs_path is None or not abs_path.is_file():
        raise HTTPException(404, "File not found")
    media_type = _inline_media_type(abs_path)
    return FileResponse(
        abs_path,
        media_type=media_type,
        headers={"Content-Disposition": f'inline; filename="{abs_path.name}"'},
    )


@router.get("/documents/download/{virtual_path:path}")
async def documents_download(virtual_path: str):
    """Force-download a file (Content-Disposition: attachment)."""
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
