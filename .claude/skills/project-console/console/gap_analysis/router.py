"""Gap Analysis section routes.

GET  /gap-analysis                 — index (one capability card per analysis)
GET  /gap-analysis/{id}            — detail (grounding · agents · assertions · findings)
GET  /gap-analysis/{id}/raw        — raw sidecar JSON (debug)
GET  /gap-analysis/{id}/grounding  — compact text rendition for the assistant drawer
POST /gap-analysis/render          — shell to the gap-analysis skill's renderer

The console is a generic consumer of the `gap-analysis` skill's JSON contract
(`schema_version: 1.0`). It never parses the analysis markdown — only the
sidecars under `docs/_analysis/`. The render endpoint shells out to the
skill's `render_sidecars.py` if installed (same shape as the trace-matrix
build endpoints), so a stale/missing sidecar can be refreshed from the UI.
"""
from __future__ import annotations

import html
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
from console.gap_analysis.loader import (
    load_analysis,
    load_index,
    load_narratives,
    skill_render_script,
)

router = APIRouter()
templates = Jinja2Templates(
    directory=str(Path(__file__).parent.parent / "web" / "templates")
)

# Status → display vocabulary (badge class + label). Drives the colored chips.
STATUS_META = {
    "draft": {"label": "Draft", "cls": "is-draft"},
    "review": {"label": "In Review", "cls": "is-review"},
    "accepted": {"label": "Accepted", "cls": "is-accepted"},
    "superseded": {"label": "Superseded", "cls": "is-superseded"},
}

ASSERTION_META = {
    "confirmed": {"label": "Confirmed", "cls": "is-confirmed", "glyph": "✓"},
    "partial": {"label": "Partial", "cls": "is-partial", "glyph": "◐"},
    "refuted": {"label": "Refuted", "cls": "is-refuted", "glyph": "✗"},
    "verify": {"label": "Verify", "cls": "is-verify", "glyph": "?"},
    "open": {"label": "Open", "cls": "is-open", "glyph": "○"},
}

# Per-advisor stance on an assertion (the click-to-expand detail).
STANCE_META = {
    "positive": {"label": "Positive", "cls": "is-positive", "glyph": "▲"},
    "neutral": {"label": "Neutral", "cls": "is-neutral", "glyph": "◆"},
    "negative": {"label": "Negative", "cls": "is-negative", "glyph": "▼"},
}

# Grounding pointer type → short label + glyph for the Grounding panel.
GROUNDING_META = {
    "dhf": ("DHF", "📁"),
    "internal": ("Internal SOP/WI", "🏛"),
    "external": ("Project applicability", "📑"),
    "standard": ("Standard", "📘"),
    "framework": ("Framework", "🧭"),
    "jira_mirror": ("Jira mirror", "🔗"),
    "confluence": ("Confluence", "🔗"),
    "submissions": ("Submissions", "📦"),
}


def _md_to_html(text: str) -> str:
    """Render a markdown chunk to HTML. Uses the `markdown` package if present
    (it is, in the console venv); falls back to an escaped <pre> block."""
    if not text:
        return ""
    try:
        import markdown  # type: ignore

        return markdown.markdown(text, extensions=["tables", "sane_lists"])
    except Exception:
        return f"<pre class='ga-raw'>{html.escape(text)}</pre>"


def _md_inline(text: str) -> str:
    """Render an inline markdown fragment, unwrapping the single <p> the
    markdown package adds, so it sits inside a banner without block spacing."""
    h = _md_to_html(text).strip()
    if h.startswith("<p>") and h.endswith("</p>") and h.count("<p>") == 1:
        h = h[3:-4]
    return h


# Role → badge class. KOL persona agents carry role "contributor"; discipline
# advisors carry primary/consulting. Anything else falls back to consulting.
def _role_cls(role: str) -> str:
    if role == "primary":
        return "is-primary"
    if role == "contributor":
        return "is-contributor"
    return "is-consulting"


def _decorate_detail(detail: dict, repo_root: Path) -> dict:
    """Add display-only fields (rendered HTML, status meta) without mutating
    the contract semantics."""
    meta = detail.get("meta", {})
    detail["_status"] = STATUS_META.get(meta.get("status"), {"label": meta.get("status") or "—", "cls": "is-open"})

    for a in detail.get("assertions", []):
        a["_meta"] = ASSERTION_META.get(a.get("status"), ASSERTION_META["open"])
        a["_clause_html"] = _md_inline(a.get("clause", ""))
        a["_evidence_html"] = _md_inline(a.get("evidence", ""))
        for p in a.get("positions", []):
            p["_meta"] = STANCE_META.get(p.get("stance"), STANCE_META["neutral"])
            nm = p.get("advisor", "")
            p["_initials"] = nm[:2].upper()
        a["_pos_count"] = len(a.get("positions", []))

    for g in detail.get("grounding", []):
        lbl, glyph = GROUNDING_META.get(g.get("type", ""), (g.get("type") or "source", "•"))
        g["_label"] = lbl
        g["_glyph"] = glyph

    for f in detail.get("findings", []):
        f["_html"] = _md_to_html(f.get("body_md", ""))
        author = f.get("author", "")
        f["_author_name"] = author.split(":", 1)[1].strip() if ":" in author else author

    detail["_recommendations_html"] = [_md_to_html(r) for r in detail.get("recommendations", [])]
    detail["_open_questions_html"] = [_md_to_html(q) for q in detail.get("open_questions", [])]

    # --- narrative companion: Goal banner + full per-agent responses ---------
    narr = load_narratives(repo_root, detail)

    goal = []
    for it in narr["goal_items"]:
        label, value = it["label"], it["value_md"]
        low = label.lower()
        if "stakeholder" in low:
            chips = [c.strip(" ._*`") for c in re.split(r"[;,]", value)]
            goal.append({"label": label, "kind": "chips", "chips": [c for c in chips if c]})
        else:
            goal.append({
                "label": label,
                "kind": "question" if "question" in low else "text",
                "value_html": _md_inline(value),
            })
    detail["_goal_items"] = goal

    by_name = narr["agents"]
    groups = {"advisor": [], "kol": []}
    for a in detail.get("agents", []):
        doc = by_name.get(a.get("name"))
        if not doc:
            continue
        groups[doc["kind"]].append({
            "name": a.get("name"),
            "role": a.get("role"),
            "role_cls": _role_cls(a.get("role")),
            "title": doc["title"],
            "specialty": doc["specialty"],
            "file": doc["file"],
            "finding_ids": a.get("contributed_finding_ids", []),
            "html": _md_to_html(doc["body_md"]),
        })
    detail["_agent_docs"] = groups
    detail["_agent_docs_total"] = len(groups["advisor"]) + len(groups["kol"])
    return detail


@router.get("/gap-analysis", response_class=HTMLResponse)
async def gap_analysis_index(request: Request, render_error: str | None = None):
    cfg = get_config()
    index = load_index(cfg.repo_root)
    has_skill = skill_render_script(cfg.repo_root) is not None
    analyses = (index or {}).get("analyses", [])
    for a in analyses:
        a["_status"] = STATUS_META.get(a.get("status"), {"label": a.get("status") or "—", "cls": "is-open"})
    return templates.TemplateResponse(
        request,
        "gap_analysis_index.html",
        {
            "config": cfg,
            "index": index,
            "analyses": analyses,
            "has_skill": has_skill,
            "render_error": render_error,
        },
    )


@router.get("/gap-analysis/{analysis_id}", response_class=HTMLResponse)
async def gap_analysis_view(request: Request, analysis_id: str):
    cfg = get_config()
    detail = load_analysis(cfg.repo_root, analysis_id)
    if detail is None:
        raise HTTPException(
            404,
            f"No gap-analysis sidecar for id '{analysis_id}'. "
            f"Run `/gap-analysis render` to (re)generate sidecars.",
        )
    detail = _decorate_detail(detail, cfg.repo_root)
    return templates.TemplateResponse(
        request,
        "gap_analysis_view.html",
        {"config": cfg, "d": detail},
    )


@router.get("/gap-analysis/{analysis_id}/raw", response_class=JSONResponse)
async def gap_analysis_raw(analysis_id: str):
    cfg = get_config()
    detail = load_analysis(cfg.repo_root, analysis_id)
    if detail is None:
        raise HTTPException(404, f"No sidecar for id '{analysis_id}'.")
    return JSONResponse(detail)


@router.get("/gap-analysis/{analysis_id}/grounding", response_class=PlainTextResponse)
async def gap_analysis_grounding(analysis_id: str):
    """Compact textual rendition of an analysis for the Assistant drawer
    (mounted on the detail view with grounding_source url:/gap-analysis/{id}/grounding)."""
    cfg = get_config()
    detail = load_analysis(cfg.repo_root, analysis_id)
    if detail is None:
        raise HTTPException(404, f"No sidecar for id '{analysis_id}'.")
    return PlainTextResponse(_compact_context(detail))


def _compact_context(d: dict) -> str:
    m = d.get("meta", {})
    lines = [
        f"# Gap Analysis — {m.get('title')}",
        f"Status: {m.get('status')} · Topic: {m.get('topic')} · Component: {m.get('component')}",
        f"Source: {m.get('source_md')}",
        "",
        "## Grounded against",
    ]
    for g in d.get("grounding", []):
        note = f"  ({g['note']})" if g.get("note") else ""
        lines.append(f"- [{g.get('type')}] {g.get('path')}{note}")
    lines.append("")
    lines.append("## Advisors")
    for a in d.get("agents", []):
        fids = ", ".join(a.get("contributed_finding_ids", []))
        lines.append(f"- {a.get('name')} ({a.get('role')}) → {fids or 'no findings'}: {a.get('changelog_summary','')}")
    lines.append("")
    lines.append("## Assertions")
    for a in d.get("assertions", []):
        lines.append(f"- {a.get('id')} [{a.get('status')}] {a.get('assertion')} — {a.get('clause')}")
    lines.append("")
    lines.append("## Findings")
    for f in d.get("findings", []):
        lines.append(f"### {f.get('id')} ({f.get('author')}): {f.get('label')}")
        lines.append(f.get("body_md", ""))
        lines.append("")
    if d.get("recommendations"):
        lines.append("## Recommendations")
        for r in d["recommendations"]:
            lines.append(f"- {r}")
    return "\n".join(lines)


@router.post("/gap-analysis/render")
async def gap_analysis_render():
    """Shell to the gap-analysis skill's renderer to refresh sidecars."""
    cfg = get_config()
    script = skill_render_script(cfg.repo_root)
    if script is None:
        return RedirectResponse(
            url="/gap-analysis?render_error="
            + _qs("The gap-analysis skill is not installed at .claude/skills/gap-analysis/. Run /sync-skills pull."),
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
        return RedirectResponse(url="/gap-analysis?render_error=" + _qs("render timed out"), status_code=303)
    if proc.returncode != 0:
        return RedirectResponse(
            url="/gap-analysis?render_error=" + _qs((proc.stdout or "") + (proc.stderr or "")),
            status_code=303,
        )
    return RedirectResponse(url="/gap-analysis", status_code=303)


def _qs(s: str) -> str:
    from urllib.parse import quote

    return quote(s[:2048], safe="")
