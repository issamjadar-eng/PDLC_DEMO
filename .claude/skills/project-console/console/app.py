from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from jinja2 import Template

from console import themes
from console.auth import preflight
from console.chat.router import router as chat_router
from console.config import get_config
from console.dashboards.router import router as dashboards_router
from console.documents.router import router as documents_router
from console.trace_matrix.router import router as trace_matrix_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    preflight()
    yield


app = FastAPI(title="Project Console", lifespan=lifespan)


def _render_theme_footer(theme) -> str:
    footer_path = theme.pack_dir / "footer.html.j2"
    if not footer_path.is_file():
        return ""
    try:
        return Template(footer_path.read_text()).render(theme=theme)
    except Exception:
        return ""


@app.middleware("http")
async def theme_context(request: Request, call_next):
    """Resolve the active theme on every request and stash it on request.state
    so templates can read branding, CSS variables, and the rendered footer."""
    cfg = get_config()
    theme = themes.resolve(cfg)
    request.state.theme = theme
    request.state.theme_css = theme.css_variables()
    request.state.theme_footer = _render_theme_footer(theme)
    request.state.config = cfg
    return await call_next(request)


app.include_router(chat_router)
app.include_router(documents_router)
app.include_router(dashboards_router)
app.include_router(trace_matrix_router)

_static_dir = Path(__file__).parent / "web" / "static"
app.mount("/static", StaticFiles(directory=_static_dir), name="static")


@app.get("/theme/assets/{filename:path}")
async def theme_asset(filename: str):
    """Serve an asset from the active theme pack (logo, favicon, font, etc.)."""
    cfg = get_config()
    theme = themes.resolve(cfg)
    pack_dir = theme.pack_dir.resolve()
    abs_path = (pack_dir / filename).resolve()
    try:
        abs_path.relative_to(pack_dir)
    except ValueError:
        return Response(status_code=404)
    if not abs_path.is_file():
        return Response(status_code=404)
    return FileResponse(abs_path)
