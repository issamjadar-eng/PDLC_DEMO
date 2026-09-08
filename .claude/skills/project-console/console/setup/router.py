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
POST   /setup/registries/{name}/refresh — fetch the registry catalog straight
                                          from GitHub (gh, read access) and
                                          cache it under .state/
POST   /setup/environment/check        — run the project's `setup.sh --check`
                                          (read-only mode) and cache the parsed
                                          report; the full install never runs
                                          from the browser
POST   /setup/workbench/render         — run the workbench-validation skill's
                                          runner (--render): executes the
                                          validation manifest and regenerates
                                          the report + sidecar this page reads
POST   /setup/project/field            — update one scalar field in the
                                          project.yml `project:` block
POST   /setup/team/access-audit        — cross-reference GitHub collaborators
                                          against the project.yml roster
                                          (report-only, cached under .state/)
POST   /setup/team/members             — add a member to project.yml team.active
POST   /setup/team/members/{github}/deactivate — move to team.inactive
                                          ({"reason": str}; roster edit only —
                                          GitHub repo access is not touched)

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


@router.post("/setup/skills/{name}/install", response_class=JSONResponse)
async def setup_install_skill(name: str, request: Request):
    """Install/update a skill from a configured registry's local clone.

    The registry is referenced by NAME and resolved against project.yml —
    the browser never supplies a filesystem path.
    """
    import anyio

    cfg = get_config()
    body = await request.json()
    reg_name = str(body.get("registry") or "") if isinstance(body, dict) else ""
    reg = _find_registry(cfg.repo_root, reg_name)
    try:
        note = await anyio.to_thread.run_sync(
            lambda: writer.install_skill(cfg.repo_root, cfg.tool_root, reg, name)
        )
    except writer.SetupWriteError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"ok": True, "note": note}


@router.post("/setup/registries/{name}/refresh", response_class=JSONResponse)
async def setup_registry_refresh(name: str, request: Request):
    """Fetch a registry's skill catalog straight from GitHub (via gh, read
    access suffices) and cache it — the catalog source that works for
    projects with no local clone and no sync tooling."""
    import anyio

    from console.setup import registry_remote
    cfg = get_config()
    reg = _find_registry(cfg.repo_root, name)
    try:
        catalog = await anyio.to_thread.run_sync(
            lambda: registry_remote.refresh_catalog(cfg.repo_root, reg)
        )
    except registry_remote.RegistryRemoteError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {
        "ok": True,
        "note": f"Fetched {len(catalog['skills'])} skills from {catalog['repo']}.",
        "fetched_at": catalog["fetched_at"],
    }


def _find_registry(repo_root: Path, reg_name: str) -> dict:
    project = _load_project_yml_dict(repo_root)
    reg = next(
        (r for r in project.get("registries") or []
         if isinstance(r, dict) and r.get("name") == reg_name),
        None,
    )
    if not reg:
        raise HTTPException(status_code=400, detail=f"Unknown registry {reg_name!r}.")
    return reg


@router.post("/setup/environment/check", response_class=JSONResponse)
async def setup_environment_check(request: Request):
    """Run the project's `setup.sh --check` (its own read-only mode) and
    return the parsed report. The full install is never run from here —
    it mutates the machine and belongs in the user's terminal."""
    import anyio

    from console.setup import envcheck
    cfg = get_config()
    try:
        report = await anyio.to_thread.run_sync(
            lambda: envcheck.run_check(cfg.repo_root)
        )
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"ok": True, "report": report}


@router.post("/setup/workbench/render", response_class=JSONResponse)
async def setup_workbench_render(request: Request):
    """Run the workbench-validation skill's runner with --render: executes the
    project's validation manifest (existing skill test suites, lints, audits)
    and regenerates the report + sidecar. The console stays a pure consumer —
    all computation happens in the owning skill's script."""
    import subprocess
    import sys

    import anyio

    from console.setup.loader import WORKBENCH_RUNNER_REL
    cfg = get_config()
    runner = cfg.repo_root / WORKBENCH_RUNNER_REL
    if not runner.is_file():
        raise HTTPException(status_code=400,
                            detail="workbench-validation skill is not installed.")

    # Optional body {"model_id": "..."}: the model operating the workbench for
    # this run. The harness does not expose it to scripts, so the operator
    # states it; without it the runner records "not captured" and flags the
    # run as a debugging run rather than a run of record.
    model_id = None
    try:
        body = await request.json()
        if isinstance(body, dict) and body.get("model_id"):
            model_id = str(body["model_id"]).strip()[:120]
    except Exception:  # no / non-JSON body is fine
        model_id = None

    def _run():
        cmd = [sys.executable, str(runner), "--root", str(cfg.repo_root), "--render",
               "--invoked-via", "console"]
        if model_id:
            cmd += ["--model-id", model_id]
        return subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
    try:
        proc = await anyio.to_thread.run_sync(_run)
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="Validation run timed out.")
    # Exit 1 means FAIL/ERROR cases exist — that is a valid, reportable outcome,
    # not an HTTP error; the refreshed sidecar carries the verdict.
    tail = (proc.stdout or "").strip().splitlines()[-3:]
    return {"ok": proc.returncode in (0, 1), "exit_code": proc.returncode,
            "summary": "\n".join(tail)}


@router.post("/setup/project/field", response_class=JSONResponse)
async def setup_project_field(request: Request):
    """Update one scalar project.* field (surgical project.yml edit)."""
    cfg = get_config()
    body = await request.json()
    if not isinstance(body, dict) or "key" not in body or "value" not in body:
        raise HTTPException(status_code=400, detail="Body must be {'key','value'}.")
    try:
        note = writer.set_project_field(
            cfg.repo_root, cfg.tool_root, str(body["key"]), str(body["value"])
        )
    except writer.SetupWriteError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"ok": True, "note": note}


@router.post("/setup/team/access-audit", response_class=JSONResponse)
async def setup_team_access_audit(request: Request):
    """Cross-reference GitHub repo collaborators against the project.yml
    roster (permission-aware) and cache the result. Report-only — access
    changes happen in GitHub."""
    import anyio

    from console.setup import team_access
    cfg = get_config()
    try:
        report = await anyio.to_thread.run_sync(
            lambda: team_access.run_audit(cfg.repo_root)
        )
    except team_access.TeamAccessError as e:
        raise HTTPException(status_code=400, detail=str(e))
    c = report["counts"]
    return {
        "ok": True,
        "note": (f"Audited {len(report['rows'])} accounts on {report['repo']}: "
                 f"{c['ok']} rostered, {c['info']} observers, "
                 f"{c['warning']} warnings, {c['error']} errors."),
    }


@router.post("/setup/team/members", response_class=JSONResponse)
async def setup_team_add(request: Request):
    """Add a member to project.yml team.active (roster of record only)."""
    cfg = get_config()
    body = await request.json()
    if not isinstance(body, dict):
        raise HTTPException(status_code=400, detail="Body must be a member object.")
    try:
        note = writer.add_team_member(cfg.repo_root, cfg.tool_root, body)
    except writer.SetupWriteError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"ok": True, "note": note}


@router.post("/setup/team/members/{github}/deactivate", response_class=JSONResponse)
async def setup_team_deactivate(github: str, request: Request):
    """Move a member from team.active to team.inactive with removed + reason."""
    cfg = get_config()
    body = await request.json()
    reason = str(body.get("reason") or "") if isinstance(body, dict) else ""
    try:
        note = writer.deactivate_team_member(cfg.repo_root, cfg.tool_root, github, reason)
    except writer.SetupWriteError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"ok": True, "note": note}


def _load_project_yml_dict(repo_root: Path) -> dict:
    from console.setup.loader import _load_project_yml
    project, _ = _load_project_yml(repo_root)
    return project


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
