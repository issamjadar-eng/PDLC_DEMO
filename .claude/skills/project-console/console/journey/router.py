"""Journey routes.

GET /journey            — the two journey paths, evaluated live
GET /journey/data.json  — the derived phase state (debug / machine consumers)
GET /journey/grounding  — the same state as plain text, for the drawer

Pure consumer. The map — phase predicates, blocking edges, producer commands
and the binding `rendering:` contract — is authored by `medtech-docs` at
`.claude/skills/medtech-docs/registry/journey.yaml`; standup titles and
why-text come from `new-project-bootstrap.md`; milestone names and order from
`docs/project/milestones/regulatory.yml`. This module renders; it decides
nothing.

No refresh endpoint and no mutation endpoint, by design: every probe is a
stat() against repo truth (2s TTL in the loader), and advancing a phase is a
skill action the user runs in their own session.
"""
from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse
from fastapi.templating import Jinja2Templates

from console.config import get_config
from console.journey.loader import discover, load_journey  # noqa: F401
from console.mdlite import md_inline

router = APIRouter()
templates = Jinja2Templates(
    directory=str(Path(__file__).parent.parent / "web" / "templates")
)

__all__ = ["router", "discover"]

# ARTIFACT LANGUAGE, NEVER COMPLETION LANGUAGE (journey.yaml#rendering.language).
# There is deliberately no "complete"/"done" label and no bare ✓ anywhere in
# this table. Every predicate detects an artifact, never its quality — a
# strategy doc can exist, probe green, and be empty of real decisions. In a
# regulated project a checkmark against a DHF role is a claim someone may be
# asked to substantiate in an audit; the glyphs below are deliberately neutral
# shapes rather than ticks.
STATE_META = {
    "present":   {"label": "artifacts present", "cls": "present",  "glyph": "●"},
    "partial":   {"label": "partly present",    "cls": "partial",  "glyph": "◐"},
    "ready":     {"label": "next up",           "cls": "ready",    "glyph": "○"},
    "blocked":   {"label": "blocked",           "cls": "blocked",  "glyph": "◌"},
    "looping":   {"label": "in the loop",       "cls": "looping",  "glyph": "∞"},
    # Evidence-gauge states (the device-program group). A milestone completes
    # when a package is filed and a regulator responds — unobservable here — so
    # it never reads "present".
    "in-motion": {"label": "evidence in motion", "cls": "motion",  "glyph": "◈"},
    "next-up":   {"label": "next up",            "cls": "ready",   "glyph": "○"},
}


def _decorate(d: dict) -> dict:
    """Inline-markdown the prose the guide and the map supply (both carry
    `code`, **bold** and links). Display-only."""
    for g in d.get("groups", []):
        for p in g.get("phases", []):
            p["_why_html"] = md_inline(p.get("why", ""))
            p["_note_html"] = md_inline(p.get("unobservable_note", ""))
            p["_meta"] = STATE_META.get(p.get("state", ""), STATE_META["ready"])
    return d


@router.get("/journey", response_class=HTMLResponse)
async def journey_page(request: Request):
    cfg = get_config()
    return templates.TemplateResponse(
        request, "journey.html",
        {"config": cfg, "j": _decorate(load_journey(cfg.repo_root))},
    )


@router.get("/journey/data.json", response_class=JSONResponse)
async def journey_data():
    return JSONResponse(load_journey(get_config().repo_root))


@router.get("/journey/grounding", response_class=PlainTextResponse)
async def journey_grounding():
    """Journey state as plain text for the assistant drawer's `url:` grounding.

    ARTIFACT LANGUAGE HERE TOO — and it matters more here than on the page.
    An advisor told a phase is "done" will congratulate the user on a strategy
    nobody has written. The state words emitted below are the map's own, and
    the preamble tells the model explicitly not to upgrade them.
    """
    d = load_journey(get_config().repo_root)
    if not d.get("present"):
        return PlainTextResponse(
            d.get("hint") or "No journey map found.")

    L: list[str] = [
        "# Journey state (derived live from the repo)",
        "",
        f"Map: {d.get('map_path','')}",
        "",
        "Every signal below detects an ARTIFACT, never its quality. \"artifacts "
        "present\" means the files the guide asks for are on disk and nothing "
        "more — a document can exist, be listed present here, and still be "
        "wrong or empty of real decisions. Never describe a phase as complete, "
        "done, or finished.",
        "",
    ]
    for g in d.get("groups", []):
        L += [f"## {g['label']}", ""]
        if g.get("blurb"):
            L += [g["blurb"], ""]
        L.append(f"Focus (where attention belongs): {g.get('focus') or '(none)'}")
        L.append("")
        for p in g.get("phases", []):
            meta = STATE_META.get(p.get("state", ""), STATE_META["ready"])
            L.append(f"### {g['label_prefix']} {p['id']} — {p['title']}  [{meta['label']}]")
            if p.get("why"):
                L.append(f"Why: {p['why']}")
            if p.get("producer"):
                L.append(f"Producer command: {p['producer']}")
            if p.get("blocked_by"):
                L.append(f"Gated by: {', '.join(p['blocked_by'])}")
            if p.get("unobservable_note"):
                L.append(f"NOT OBSERVABLE: {p['unobservable_note']}")
            for c in p.get("checks", []):
                mark = "ok" if c.get("ok") else "not yet"
                L.append(f"  - [{mark}] {c.get('label','')} — {c.get('detail','')}")
            for lv in (p.get("levels") or []):
                L.append(f"  - level '{lv.get('label')}': "
                         f"{'reached' if lv.get('ok') else 'not reached'}")
            ev = p.get("evidence") or {}
            if ev:
                L.append(
                    f"  - evidence (NOT a readiness verdict): {ev.get('total',0)} tracker "
                    f"rows, {ev.get('in_scope',0)} in scope, {ev.get('moved',0)} in motion, "
                    f"{ev.get('scoped_out',0)} scoped out, {ev.get('unrecorded',0)} whose "
                    f"status is recorded in the tracker markdown and not read here."
                )
                L.append(
                    f"  - readiness verdict: NOT AVAILABLE — owned by "
                    f"`{ev.get('readiness_owner','/tracker assess')}`, which has "
                    f"{'run' if ev.get('readiness_available') else 'NOT run'}. Do not "
                    f"infer readiness from the row counts above."
                )
            g_ = p.get("gauge")
            if g_:
                L.append(
                    f"  - steady-state health (NOT a completion signal): "
                    f"{g_.get('installed_skills')} skills installed, last registry sync "
                    f"{g_.get('last_sync') or 'unknown'}"
                    + (f" ({g_.get('age_days')} days ago)" if g_.get("age_days") is not None else "")
                )
            L.append("")
    return PlainTextResponse("\n".join(L))
