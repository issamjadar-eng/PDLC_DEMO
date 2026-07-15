"""Setup section routes — the project-settings surface.

GET    /setup                          — settings shell (connectors, skills,
                                          agents, plugins, rules & hooks,
                                          team & security)
GET    /setup/data                     — full aggregate data model as JSON
POST   /setup/connectors/{name}        — add/update a server in .mcp.json
                                          (+ ensures the allowlist entry — the
                                          two files move in lockstep)
POST   /setup/connectors/{name}/approval — {"approved": bool} allowlist toggle
DELETE /setup/connectors/{name}        — remove the server from .mcp.json

Writes go exclusively through console.setup.writer (backups + audit log).
The console edits config only — Claude Code owns the MCP server lifecycle,
so every mutation response reminds the caller a session restart is needed.
"""
from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from console.config import get_config
from console.setup import writer
from console.setup.catalog import CATALOG
from console.setup.loader import load_connectors, load_setup

router = APIRouter()
templates = Jinja2Templates(
    directory=str(Path(__file__).parent.parent / "web" / "templates")
)

RESTART_NOTE = (
    "Saved. Connector config is read at Claude Code session start — restart "
    "the session (or /mcp → Reconnect) for the change to take effect."
)


@router.get("/setup", response_class=HTMLResponse)
async def setup_index(request: Request):
    cfg = get_config()
    setup = load_setup(cfg.repo_root)
    return templates.TemplateResponse(
        request,
        "setup_view.html",
        {
            "config": cfg,
            "setup": setup,
            "data": setup["connectors"],  # connector model (incl. write-path JS)
            "catalog": CATALOG,
        },
    )


@router.get("/setup/data", response_class=JSONResponse)
async def setup_data(request: Request):
    cfg = get_config()
    return load_setup(cfg.repo_root)


@router.post("/setup/connectors/{name}", response_class=JSONResponse)
async def setup_upsert(name: str, request: Request):
    cfg = get_config()
    body = await request.json()
    spec = body.get("spec") if isinstance(body, dict) else None
    if not isinstance(spec, dict):
        raise HTTPException(status_code=400, detail="Body must be {'spec': {...}}.")
    try:
        writer.upsert_server(cfg.repo_root, cfg.tool_root, name, spec)
        # Keep the security allowlist in lockstep: an installed connector the
        # posture check would flag as unapproved is a config bug, not a feature.
        writer.set_approved(cfg.repo_root, cfg.tool_root, name, approved=True)
    except writer.SetupWriteError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"ok": True, "note": RESTART_NOTE}


@router.post("/setup/connectors/{name}/approval", response_class=JSONResponse)
async def setup_approval(name: str, request: Request):
    cfg = get_config()
    body = await request.json()
    approved = bool(body.get("approved")) if isinstance(body, dict) else None
    if not isinstance(body, dict) or "approved" not in body:
        raise HTTPException(status_code=400, detail="Body must be {'approved': bool}.")
    try:
        changed = writer.set_approved(cfg.repo_root, cfg.tool_root, name, approved)
    except writer.SetupWriteError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"ok": True, "changed": changed}


@router.delete("/setup/connectors/{name}", response_class=JSONResponse)
async def setup_remove(name: str, request: Request):
    cfg = get_config()
    try:
        writer.remove_server(cfg.repo_root, cfg.tool_root, name)
    except writer.SetupWriteError as e:
        raise HTTPException(status_code=400, detail=str(e))
    # Deliberately leave the allowlist row: removal ≠ un-approval, and the
    # loader will surface the "approved but not installed" state visibly.
    return {"ok": True, "note": RESTART_NOTE}
