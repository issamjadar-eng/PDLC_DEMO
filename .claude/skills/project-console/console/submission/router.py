"""Submission section routes.

GET  /submission                  — index (one card per filing: qsub / 510k / pccp)
GET  /submission/{id}             — detail (pretty package view + per-doc tabs)
GET  /submission/{id}/raw         — raw sidecar JSON (debug)
GET  /submission/{id}/grounding   — compact text rendition for the assistant drawer
POST /submission/render           — shell to the submissions skill's renderer

The console is a generic consumer of the `submissions` skill's JSON contract
(`schema_version: 1.0`). It never parses the submission markdown for structure —
only the sidecars under `docs/project/submissions/`. Document *bodies* are
rendered inline via the documents renderer (so the Q-Sub docs display as pretty
markdown in a tabbed viewer); everything else (pieces, questions, sign-off,
counts) comes from the sidecar.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import (
    HTMLResponse,
    JSONResponse,
    PlainTextResponse,
    RedirectResponse,
)
from fastapi.templating import Jinja2Templates

from console.config import get_config
from console.documents import renderer as doc_renderer
from console.submission.loader import (
    load_filing,
    load_index,
    skill_render_script,
)

router = APIRouter()
templates = Jinja2Templates(
    directory=str(Path(__file__).parent.parent / "web" / "templates")
)

# Filing status → display chip.
STATUS_META = {
    "drafting": {"label": "Drafting", "cls": "is-drafting"},
    "scaffold": {"label": "Scaffold", "cls": "is-scaffold"},
    "ready": {"label": "Ready", "cls": "is-ready"},
    "transmitted": {"label": "Transmitted", "cls": "is-transmitted"},
}

# Scope-routing label → (glyph, short label, css class). Mirrors the
# internal-vs-external-scope-labels rule.
SCOPE_META = {
    "external": ("📤", "FDA-bound", "is-external"),
    "internal": ("📝", "Internal", "is-internal"),
    "deferred": ("⏸️", "Deferred", "is-deferred"),
    "reference": ("📖", "Reference", "is-reference"),
    "": ("", "", ""),
}

# Document kind → glyph for the tab rail.
KIND_GLYPH = {
    "cover-letter": "✉️",
    "device-description": "🩺",
    "intended-use": "🎯",
    "fda-questions": "❓",
    "pccp-summary": "🔁",
    "brief": "📄",
    "template": "🧩",
    "predicate": "🔗",
    "manifest": "📦",
    "doc": "📃",
}


def _doc_link_rewriter(doc_repo_rel: str):
    """Rewrite relative markdown links in a rendered doc body so they open in
    the Documents viewer instead of 404-ing against /submission/<id>. Absolute,
    anchor, and root-relative links are left alone."""
    doc_dir = Path(doc_repo_rel).parent

    def _resolve(href: str) -> str | None:
        if not href or href.startswith(("http://", "https://", "/", "#", "mailto:")):
            return None
        base = href.split("#", 1)[0]
        if not base:
            return None
        # Resolve lexically against the doc's repo-relative dir (sidecar paths
        # are already repo-relative — no filesystem / cwd dependence).
        return _posix_norm(f"{doc_dir.as_posix()}/{base}")

    def repl(m: re.Match) -> str:
        href = m.group(1)
        resolved = _resolve(href)
        if resolved is None:
            return m.group(0)
        return f'href="/documents#path={resolved}" target="_blank" rel="noopener"'

    def run(html: str) -> str:
        return re.sub(r'href="([^"]+)"', repl, html)

    return run


def _posix_norm(p: str) -> str:
    parts: list[str] = []
    for seg in p.split("/"):
        if seg in ("", "."):
            continue
        if seg == "..":
            if parts:
                parts.pop()
        else:
            parts.append(seg)
    return "/".join(parts)


def _decorate(detail: dict, repo_root: Path) -> dict:
    meta = detail.get("meta", {})
    detail["_status"] = STATUS_META.get(
        meta.get("status"), {"label": meta.get("status") or "—", "cls": "is-scaffold"}
    )

    for doc in detail.get("documents", []):
        kind = doc.get("kind", "doc")
        doc["_glyph"] = KIND_GLYPH.get(kind, KIND_GLYPH["doc"])
        # Render the doc body inline (pretty markdown), rewriting cross-doc links.
        abs_path = repo_root / doc.get("path", "")
        body_html = ""
        if abs_path.is_file():
            try:
                rendered = doc_renderer.render(abs_path)
                body_html = _doc_link_rewriter(doc.get("path", ""))(rendered.body_html or "")
            except Exception:
                body_html = ""
        doc["_body_html"] = body_html
        for s in doc.get("sections", []):
            glyph, lbl, cls = SCOPE_META.get(s.get("label", ""), SCOPE_META[""])
            s["_glyph"], s["_scope_label"], s["_scope_cls"] = glyph, lbl, cls

    for q in detail.get("questions", []):
        glyph, lbl, cls = SCOPE_META.get(q.get("label", ""), SCOPE_META[""])
        q["_glyph"], q["_scope_cls"] = glyph, cls

    for grp in ("required", "supporting", "strengtheners", "excluded"):
        for p in detail.get("pieces", {}).get(grp, []):
            p["_blocking"] = bool(p.get("blocking"))

    # Group questions by topic for the panel.
    topics: dict[str, list] = {}
    for q in detail.get("questions", []):
        topics.setdefault(q.get("topic") or "Questions", []).append(q)
    detail["_question_topics"] = list(topics.items())

    detail["_default_advisor"] = meta.get("default_advisor") or "regulatory-affairs"
    return detail


@router.get("/submission", response_class=HTMLResponse)
async def submission_index(request: Request, render_error: str | None = None):
    cfg = get_config()
    index = load_index(cfg.repo_root)
    has_skill = skill_render_script(cfg.repo_root) is not None
    filings = (index or {}).get("filings", [])
    for f in filings:
        f["_status"] = STATUS_META.get(
            f.get("status"), {"label": f.get("status") or "—", "cls": "is-scaffold"}
        )
    return templates.TemplateResponse(
        request,
        "submission_index.html",
        {
            "config": cfg,
            "index": index,
            "filings": filings,
            "has_skill": has_skill,
            "render_error": render_error,
        },
    )


@router.get("/submission/{filing_id}", response_class=HTMLResponse)
async def submission_view(request: Request, filing_id: str):
    cfg = get_config()
    detail = load_filing(cfg.repo_root, filing_id)
    if detail is None:
        raise HTTPException(
            404,
            f"No submission sidecar for filing '{filing_id}'. "
            f"Run `/submissions render` to (re)generate sidecars.",
        )
    detail = _decorate(detail, cfg.repo_root)
    return templates.TemplateResponse(
        request,
        "submission_view.html",
        {"config": cfg, "d": detail},
    )


@router.get("/submission/{filing_id}/raw", response_class=JSONResponse)
async def submission_raw(filing_id: str):
    cfg = get_config()
    detail = load_filing(cfg.repo_root, filing_id)
    if detail is None:
        raise HTTPException(404, f"No sidecar for filing '{filing_id}'.")
    return JSONResponse(detail)


@router.get("/submission/{filing_id}/grounding", response_class=PlainTextResponse)
async def submission_grounding(filing_id: str):
    """Compact textual rendition of a filing for the Assistant drawer."""
    cfg = get_config()
    detail = load_filing(cfg.repo_root, filing_id)
    if detail is None:
        raise HTTPException(404, f"No sidecar for filing '{filing_id}'.")
    return PlainTextResponse(_compact_context(detail))


def _compact_context(d: dict) -> str:
    m = d.get("meta", {})
    lines = [
        f"# Submission — {m.get('type')} · {m.get('device')}",
        f"Status: {m.get('status')} · Filing ID: {m.get('filing_id')} · Milestone: {m.get('milestone')}",
        f"DHFs: {m.get('dhfs')}",
        f"Manifest: {m.get('manifest_md')}",
        "",
        "## Package pieces",
    ]
    pieces = d.get("pieces", {})
    for grp in ("required", "supporting", "strengtheners"):
        for p in pieces.get(grp, []):
            tag = " [transmission-blocking]" if p.get("blocking") else ""
            st = f" ({p['status']})" if p.get("status") else ""
            lines.append(f"- [{grp}] {p.get('name')}{st}{tag}: {p.get('purpose','')}")
    if pieces.get("excluded"):
        lines.append("")
        lines.append("## Excluded")
        for p in pieces["excluded"]:
            lines.append(f"- {p.get('name')} — {p.get('reason','')}")
    lines.append("")
    lines.append("## Documents")
    for doc in d.get("documents", []):
        lines.append(f"### {doc.get('title')} ({doc.get('version')}, {doc.get('status')})")
        if doc.get("summary"):
            lines.append(doc["summary"])
        secs = ", ".join(s.get("title", "") for s in doc.get("sections", []))
        if secs:
            lines.append(f"Sections: {secs}")
        lines.append("")
    if d.get("questions"):
        lines.append("## Questions for FDA")
        for q in d["questions"]:
            lines.append(f"- {q.get('id')} ({q.get('topic')}): {q.get('subject')}")
            if q.get("position"):
                lines.append(f"  position: {q['position']}")
    return "\n".join(lines)


@router.post("/submission/render")
async def submission_render():
    """Shell to the submissions skill's renderer to refresh sidecars."""
    cfg = get_config()
    script = skill_render_script(cfg.repo_root)
    if script is None:
        return RedirectResponse(
            url="/submission?render_error="
            + _qs(
                "The submissions skill is not installed at .claude/skills/submissions/. "
                "Run /sync-skills pull or /submissions setup."
            ),
            status_code=303,
        )
    try:
        proc = subprocess.run(
            [sys.executable, str(script), "--root", str(cfg.repo_root)],
            capture_output=True,
            text=True,
            timeout=60,
        )
    except subprocess.TimeoutExpired:
        return RedirectResponse(url="/submission?render_error=" + _qs("render timed out"), status_code=303)
    if proc.returncode != 0:
        return RedirectResponse(
            url="/submission?render_error=" + _qs((proc.stdout or "") + (proc.stderr or "")),
            status_code=303,
        )
    return RedirectResponse(url="/submission", status_code=303)


def _qs(s: str) -> str:
    from urllib.parse import quote

    return quote(s[:2048], safe="")
