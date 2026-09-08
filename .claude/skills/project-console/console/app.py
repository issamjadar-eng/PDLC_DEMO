from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from jinja2 import Template

from console import themes
from console.assistant.router import invalidate_index as rebuild_assistant_index
from console.assistant.router import router as assistant_router
from console.auth import preflight
from console.chat.router import router as chat_router
from console.commercial.loader import discover as discover_commercial
from console.commercial.router import router as commercial_router
from console.config import get_config
from console.dashboards.router import router as dashboards_router
from console.documents.router import router as documents_router
from console.doc_pipeline.loader import discover as discover_doc_pipeline
from console.doc_pipeline.router import router as doc_pipeline_router
from console.gap_analysis.loader import discover as discover_gap_analysis
from console.gap_analysis.router import router as gap_analysis_router
from console.journey.loader import discover as discover_journey
from console.journey.router import router as journey_router
from console.metrics.loader import discover as discover_metrics
from console.metrics.router import router as metrics_router
from console.overview.router import discover as discover_overview
from console.overview.router import router as overview_router
from console.setup.router import router as setup_router
from console.tasks_view.loader import discover as discover_tasks
from console.tasks_view.router import router as tasks_router
from console.strategy.router import discover as discover_strategy
from console.strategy.router import router as strategy_router
from console.submission.loader import discover as discover_submission
from console.submission.router import router as submission_router
from console.trace_matrix.router import router as trace_matrix_router
from console.workflows.router import router as workflows_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    preflight()
    # Warm the assistant drawer's README index at startup (Tier 3 grounding).
    # The build is synchronous and cheap (~10 ms). Warnings for any folder
    # missing a README are exposed via /assistant/api/index/status.
    try:
        idx = rebuild_assistant_index()
        if idx.missing_readme_folders:
            print(
                f"[assistant] index built: {idx.readme_count} READMEs, "
                f"{idx.total_bytes // 1024} KB; "
                f"{len(idx.missing_readme_folders)} folder(s) missing README.md:"
            )
            for m in idx.missing_readme_folders:
                print(f"  - {m}")
        else:
            print(
                f"[assistant] index built: {idx.readme_count} READMEs, "
                f"{idx.total_bytes // 1024} KB; no coverage gaps"
            )
    except Exception as e:
        print(f"[assistant] index build failed at startup: {e}")
    yield


app = FastAPI(title="Project Console", lifespan=lifespan)

# Cache-buster for the static stylesheet. The console uses hash-based SPA
# navigation, so console.css is only fetched on a full page load; without a
# version query a browser keeps serving the cached copy after a CSS edit.
# Stat the file per request (cheap) so edits take effect on the next load.
# Per-browser theme selection. Deliberately NOT a project.yml / console.yaml
# setting: it is one viewer's preference, so it must not be committed. Read in
# the theme middleware and by /theme/assets; always validated against the
# installed packs before it reaches a path.
THEME_COOKIE = "pc_theme"

_static_css_path = Path(__file__).parent / "web" / "static" / "console.css"


def _static_version() -> str:
    """Cache-busting token = newest mtime across served CSS + JS assets, so any
    static edit (console.css, assistant.js, …) forces a reload. Previously this
    tracked only console.css, so JS-only edits went unnoticed until a hard
    refresh."""
    try:
        mtimes = [
            p.stat().st_mtime
            for p in (*_static_dir.glob("*.css"), *_static_dir.glob("*.js"))
        ]
        return str(int(max(mtimes))) if mtimes else "0"
    except (OSError, ValueError):
        return "0"


def _render_theme_footer(theme, default_theme=None) -> str:
    """Render a footer for the active pack, falling back to the project default.

    Same chain, and the same reasoning, as `/theme/assets`: a pack is a
    palette, but the footer carries project IDENTITY — copyright, legal links.
    Those must not change because a viewer picked different colours. The
    bundled packs therefore ship no footer at all, so any project pack's
    footer shows through under every palette.

    Each template renders with ITS OWN pack's theme, so a fallback footer gets
    the project's tagline rather than a half-and-half of two packs.

    Context is `theme` plus `year`. `year` exists because the templates needed
    it and had no way to reach it: the bundled light pack shipped
    `{{ "now"|e }}` — a quoted string through the escape filter, so it rendered
    the literal word "now". Jinja has no `now` global, and the except-branch
    below swallows template errors into an empty footer, so an undefined
    variable would have silently deleted the footer entirely; a string literal
    was the only thing that visibly "worked".

    A project with no footer in any pack renders none, and `_base.html` omits
    the element entirely rather than leaving an empty bar.
    """
    for candidate in (theme, default_theme):
        if candidate is None:
            continue
        footer_path = candidate.pack_dir / "footer.html.j2"
        if not footer_path.is_file():
            continue
        try:
            return Template(footer_path.read_text()).render(
                theme=candidate, year=datetime.now().year)
        except Exception:
            return ""
    return ""


def _nav_probe(fn, repo_root) -> bool:
    """Run a section's `discover()` and reduce it to a nav-visibility boolean.

    Swallows everything. This runs inside the request middleware, so an
    unhandled exception in one section's probe would take down every route in
    the console — including the ones that have nothing to do with that section.
    Failing closed (hide the nav entry) keeps the blast radius at one tab.
    """
    try:
        return bool(fn(repo_root)["has_any"])
    except Exception:
        return False


@app.middleware("http")
async def theme_context(request: Request, call_next):
    """Resolve the active theme on every request and stash it on request.state
    so templates can read branding, CSS variables, and the rendered footer."""
    cfg = get_config()
    # Per-browser theme selection. Stored in a cookie rather than console.yaml
    # so one person's preference never lands in the repo, and rather than
    # localStorage so the SERVER sees it: the active pack decides which logo,
    # favicon, font and footer `/theme/assets/*` serves, not just the CSS
    # variables. A client-only mechanism would leave those on the project
    # default and render a pack half-applied.
    #
    # The value is untrusted (it reaches a filesystem path), so it goes
    # through `safe_theme_name`; anything unrecognised falls back to the
    # project default.
    selected = themes.safe_theme_name(cfg, request.cookies.get(THEME_COOKIE))
    theme = themes.resolve(cfg, selected)
    request.state.theme = theme
    request.state.theme_is_default = selected is None
    request.state.theme_css = theme.css_variables()
    # Second argument is the project default pack — the footer falls back to
    # it so a personal palette choice never changes the project's copyright.
    request.state.theme_footer = _render_theme_footer(
        theme, themes.resolve(cfg) if selected else None)
    request.state.config = cfg
    request.state.static_v = _static_version()
    # Nav visibility — one cheap filesystem probe per section, per request.
    # EVERY probe goes through `_nav_probe`: this middleware runs on the way to
    # every route, so an exception raised by any single probe would 500 the
    # whole console rather than just hide one nav entry. A section whose probe
    # fails is treated as "not discoverable" and the rest of the app stays up.
    request.state.overview_nav = _nav_probe(discover_overview, cfg.repo_root)
    # Strategy — shows when docs/project/strategies/*-strategy.md exist.
    request.state.strategy_nav = _nav_probe(discover_strategy, cfg.repo_root)
    # Submission — shows when submission sidecars / manifests exist.
    request.state.submission_nav = _nav_probe(discover_submission, cfg.repo_root)
    # Gap Analysis — shows when sidecars exist under docs/_analysis/.
    request.state.gap_analysis_nav = _nav_probe(discover_gap_analysis, cfg.repo_root)
    # Business domains (Commercial, Finance, Manufacturing, ...) — one nav entry
    # per discovered docs/project/<slug>/.console/<slug>-index.json. Same
    # fail-closed contract as `_nav_probe`: a broken probe hides the tabs, not the app.
    try:
        request.state.domain_nav = list(discover_commercial(cfg.repo_root).get("domains") or [])
    except Exception:
        request.state.domain_nav = []
    # Metrics — shows when the usage-metrics skill has published
    # tools/usage-metrics/usage.json.
    request.state.metrics_nav = _nav_probe(discover_metrics, cfg.repo_root)
    # Tasks — shows when the task skill has published tasks/task-summary.json.
    request.state.tasks_nav = _nav_probe(discover_tasks, cfg.repo_root)
    # Document Pipeline — shows when the docs pillar exists (docs/README.md).
    request.state.doc_pipeline_nav = _nav_probe(discover_doc_pipeline, cfg.repo_root)
    # Journey — INVERTED DISCOVERY: lights whenever the MAP exists, not when a
    # producer artifact does. A journey tab that hides while the project is
    # immature hides exactly when it is most useful.
    request.state.journey_nav = _nav_probe(discover_journey, cfg.repo_root)
    return await call_next(request)


app.include_router(chat_router)
app.include_router(documents_router)
app.include_router(dashboards_router)
app.include_router(overview_router)
app.include_router(strategy_router)
app.include_router(submission_router)
app.include_router(commercial_router)
app.include_router(trace_matrix_router)
app.include_router(gap_analysis_router)
app.include_router(assistant_router)
app.include_router(workflows_router)
app.include_router(metrics_router)
app.include_router(setup_router)
app.include_router(tasks_router)
app.include_router(doc_pipeline_router)
app.include_router(journey_router)

_static_dir = Path(__file__).parent / "web" / "static"
app.mount("/static", StaticFiles(directory=_static_dir), name="static")

# Serve project asset decks (assets/*/index.html) at /assets if the dir exists.
_assets_root = Path(get_config().repo_root) / "assets"
if _assets_root.is_dir():
    app.mount("/assets", StaticFiles(directory=str(_assets_root), html=True), name="project-assets")


@app.get("/theme/assets/{filename:path}")
async def theme_asset(filename: str, request: Request):
    """Serve an asset from the active theme pack (logo, favicon, font, etc.).

    Honors the per-browser selection for the same reason the middleware does —
    otherwise a selected pack would get its colours but the default pack's
    logo and web font.
    """
    cfg = get_config()
    selected = themes.safe_theme_name(cfg, request.cookies.get(THEME_COOKIE))

    # Asset lookup falls back to the project default pack. Packs are palettes
    # first: the bundled `light` / `dark` packs carry no logo, favicon or web
    # font at all, so without this a viewer selecting one would lose the
    # project's branding AND its font — the font silently, since a failed
    # @font-face just falls back to the system UI stack with no error. Colours
    # are per-pack; identity assets belong to the project.
    candidates = []
    if selected:
        candidates.append(themes.resolve(cfg, selected).pack_dir)
    candidates.append(themes.resolve(cfg).pack_dir)

    for pack_dir in candidates:
        pack_dir = pack_dir.resolve()
        abs_path = (pack_dir / filename).resolve()
        try:
            abs_path.relative_to(pack_dir)
        except ValueError:
            return Response(status_code=404)   # traversal — refuse outright
        if abs_path.is_file():
            return FileResponse(abs_path)
    return Response(status_code=404)
