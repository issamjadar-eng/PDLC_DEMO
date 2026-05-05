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


# Dashboards that need the b3-style inline render with workflow chrome
# (Pending-N panel + Save/Cancel + assistant drawer) instead of the generic
# iframe path. Slug-keyed for now; can be lifted into project.yml later.
_INTERACTIVE_DASHBOARD_SLUGS = {"submission-tracker"}


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

    if slug in _INTERACTIVE_DASHBOARD_SLUGS:
        return _render_interactive_tracker_dashboard(request, cfg, dash)

    return templates.TemplateResponse(
        request,
        "dashboard_view.html",
        {"config": cfg, "dashboard": dash},
    )


def _render_interactive_tracker_dashboard(request: Request, cfg, dash):
    """Inline-render the submission tracker as an interactive workflow surface
    (b3 strategy-reassembly parity): host page provides chrome (Pending-N
    panel + Save/Cancel + Ask Advisor drawer); embed-mode HTML fragment from
    render.py is dropped into the page; tracker_interactive.{css,js} overlay
    binds clickable badges. Falls back to the generic iframe path on failure."""
    # Import lazily — the workflows router is the owner of the render-module
    # loader and the actor resolver.
    try:
        from console.workflows import router as workflows_router
    except Exception:
        # Should never happen; fall back to iframe if it does.
        return templates.TemplateResponse(
            request, "dashboard_view.html",
            {"config": cfg, "dashboard": dash},
        )

    actor_info = workflows_router._resolve_actor(cfg.repo_root)
    actor_folder = actor_info.get("task_folder") or ""

    try:
        fragment = workflows_router._tracker_embed_fragment_for_actor(
            cfg, actor_folder
        )
    except Exception as e:
        # Fragment build failed — surface the error inline rather than fall
        # back to iframe (which would hide the issue). Caller sees something
        # useful.
        fragment = (
            f'<div class="muted" style="padding:1rem;border:1px solid '
            f'var(--border);border-radius:6px;color:#fca5a5;">'
            f'Inline render failed: {type(e).__name__}: {e}</div>'
        )

    # Allowed advisors for the drawer = project's enabled advisor list,
    # filtered to solo (non-panel/system) personas.
    allowed_agents: list[str] = []
    try:
        import yaml
        with open(cfg.repo_root / "project.yml", "r") as f:
            pyml = yaml.safe_load(f) or {}
        adv = (pyml.get("advisors") or {}).get("enabled") or []
        if isinstance(adv, list):
            allowed_agents = [str(a) for a in adv]
    except Exception:
        pass

    # Session/pending state for the chrome banner — best-effort.
    pending_count = 0
    session_active = False
    session_branch = ""
    session_task_id = ""
    if actor_folder:
        try:
            from console.workflows import tracker_session, tracker_writer
            sess = tracker_session.snapshot(
                cfg.repo_root, actor_folder, "status"
            )
            if sess is not None:
                session_active = True
                session_branch = sess.branch
                session_task_id = sess.task_id
                pending = tracker_writer.parse_pending_changes(
                    cfg.repo_root / sess.task_path
                )
                pending_count = len(pending)
        except Exception:
            pass

    return templates.TemplateResponse(
        request,
        "dashboard_view.html",
        {
            "config": cfg,
            "dashboard": dash,
            "interactive": True,
            "tracker_fragment": fragment,
            "advisor_allowed_agents": allowed_agents,
            "session_active": session_active,
            "session_branch": session_branch,
            "session_task_id": session_task_id,
            "pending_count": pending_count,
        },
    )
