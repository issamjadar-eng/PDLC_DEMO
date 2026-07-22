"""Commercial section routes — the display tier of the business-question stack.

GET  /commercial                 — question catalog (category rail + answer cards)
GET  /commercial/{bq}            — answer view (verdict, charts, provenance, report, history)
GET  /commercial/{bq}/raw        — the shown edition's data.json (debug)
GET  /commercial/{bq}/grounding  — compact text rendition for the assistant drawer
POST /commercial/render          — shell to the commercial skill's `render`

The console is a pure consumer of the `commercial` skill's sidecars
(`schema_version 1.0`). It plots the sidecar's series verbatim and computes
nothing — every figure on screen was emitted by the skill's deterministic
computation and claim-linted before it got here. Evidence-class badges,
freshness bands, assumption chips, and draft watermarks are rendered from
sidecar fields so a chart can never overstate its grounding.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from console.commercial.loader import (
    load_edition,
    load_index,
    load_pinned_table,
    question_row,
    skill_render_script,
)
from console.config import get_config
from console.documents import renderer as doc_renderer

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).parent.parent / "web" / "templates"))

# Answer status → chip. Mirrors the sidecar's status vocabulary.
STATUS_META = {
    "answered": {"label": "Answered", "cls": "is-answered"},
    "draft-only": {"label": "Draft", "cls": "is-draft"},
    "no-answer": {"label": "Not answered", "cls": "is-none"},
    "not-implemented": {"label": "Planned", "cls": "is-planned"},
}

# Evidence class → badge (icon + label, never color alone). Worst-of rolls up.
EVIDENCE_META = {
    "measured": {"glyph": "✓", "label": "Measured", "cls": "ev-measured",
                 "tip": "Read directly from a pinned corpus snapshot"},
    "derived": {"glyph": "ƒ", "label": "Derived", "cls": "ev-derived",
                "tip": "Computed from pinned snapshots (e.g. a projection)"},
    "assumed": {"glyph": "≈", "label": "Assumed", "cls": "ev-assumed",
                "tip": "Rests on a stated A-NNN assumption record"},
    "unavailable": {"glyph": "∅", "label": "No data", "cls": "ev-unavailable",
                    "tip": "Needed data does not exist — gap stated, not papered over"},
}

FRESH_META = {
    "fresh": {"label": "Fresh", "cls": "fr-fresh", "tip": "All pinned snapshots within max_age_days"},
    "aging": {"label": "Aging", "cls": "fr-aging", "tip": "A pinned snapshot is near its max age"},
    "stale": {"label": "Stale", "cls": "fr-stale", "tip": "A pinned snapshot exceeds max_age_days"},
}

EDITION_META = {
    "approved": {"label": "Approved", "cls": "ed-approved"},
    "draft": {"label": "Draft — not approved", "cls": "ed-draft"},
    "superseded": {"label": "Superseded", "cls": "ed-superseded"},
}


def _decorate_row(q: dict) -> dict:
    q["_status"] = STATUS_META.get(q.get("status"), STATUS_META["not-implemented"])
    q["_evidence"] = EVIDENCE_META.get(q.get("evidence_class") or "")
    q["_fresh"] = FRESH_META.get(q.get("freshness") or "")
    return q


def _is_number(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


# Categorical slots 1-3 of the validated reference palette (dark-surface steps) —
# three lines validate all-pairs; computations cap timeseries at <=4 lines.
TS_COLORS = ["#3987e5", "#d95926", "#199e70", "#c98500"]

VERDICT_META = {
    "met": {"label": "Met", "cls": "vx-met", "glyph": "✓"},
    "at-risk": {"label": "At risk", "cls": "vx-risk", "glyph": "!"},
    "not-met": {"label": "Not met", "cls": "vx-notmet", "glyph": "✗"},
    "not-evaluable": {"label": "Not evaluable", "cls": "vx-none", "glyph": "?"},
}

SEV_META = {
    "high": {"label": "High", "cls": "sv-high"},
    "medium": {"label": "Medium", "cls": "sv-med"},
    "low": {"label": "Low", "cls": "sv-low"},
}


def _timeseries_geometry(s: dict):
    """Server-side SVG geometry for a timeseries series (the console renders the
    sidecar's values verbatim — this computes pixels, never data)."""
    lines = s.get("lines") or []
    all_pts = [(p["x"], p["y"]) for ln in lines for p in ln.get("points", [])]
    if not all_pts:
        return None
    xs = sorted({x for x, _ in all_pts})
    xi = {x: i for i, x in enumerate(xs)}
    ymax = max(y for _, y in all_pts) or 1
    W, H, L, R, T, B = 560, 180, 12, 96, 12, 24
    span = max(1, len(xs) - 1)

    def X(x):
        return L + (W - L - R) * (xi[x] / span)

    def Y(y):
        return T + (H - T - B) * (1 - y / ymax)

    glines = []
    for i, ln in enumerate(lines):
        pts = sorted(ln.get("points", []), key=lambda p: p["x"])
        if not pts:
            continue
        glines.append({
            "label": ln.get("label", f"series {i + 1}"),
            "color": TS_COLORS[i % len(TS_COLORS)],
            "path": " ".join(f"{X(p['x']):.1f},{Y(p['y']):.1f}" for p in pts),
            "dots": [{"cx": round(X(p["x"]), 1), "cy": round(Y(p["y"]), 1),
                      "tip": f"{ln.get('label')} · {p['x']}: {p['y']} {s.get('unit', '')}".strip()}
                     for p in pts],
            "end_x": round(X(pts[-1]["x"]), 1), "end_y": round(Y(pts[-1]["y"]), 1),
        })
    # de-collide direct end labels: lines ending at similar values otherwise overlap
    order = sorted(glines, key=lambda g: g["end_y"])
    for i, g in enumerate(order):
        g["label_y"] = g["end_y"]
        if i and g["label_y"] - order[i - 1]["label_y"] < 13:
            g["label_y"] = order[i - 1]["label_y"] + 13
    return {"w": W, "h": H, "lines": glines, "x0": xs[0][:10], "x1": xs[-1][:10],
            "ymax": ymax, "y0_y": round(Y(0), 1), "ymax_y": round(Y(ymax), 1), "left": L,
            "right": W - R}


def _decorate_series(series: list) -> list:
    """Prepare sidecar series for template rendering: bar geometry for numeric
    points, key-value rows otherwise. The console plots values verbatim."""
    out = []
    for s in series:
        d = dict(s)
        d["_evidence"] = EVIDENCE_META.get(s.get("evidence_class") or "unavailable",
                                           EVIDENCE_META["unavailable"])
        prov = s.get("provenance") or {}
        if prov.get("dataset"):
            d["_prov_label"] = f"{prov['dataset']}@{prov.get('snapshot', '?')}"
            d["_prov_link"] = f"/documents#path=docs/project/corpus/{prov['dataset']}/README.md"
        elif prov.get("assumption"):
            d["_prov_label"] = f"assumption {prov['assumption']}"
            d["_prov_link"] = None
        else:
            d["_prov_label"] = prov.get("note", "")
            d["_prov_link"] = None
        if s.get("kind") == "timeseries":
            d["_ts"] = _timeseries_geometry(s)
            d["_rows"] = []
            d["_numeric"] = False
            out.append(d)
            continue
        pts = s.get("points", [])
        numeric = [p for p in pts if _is_number(p.get("value"))]
        d["_numeric"] = bool(numeric) and len(numeric) == len(pts)
        if d["_numeric"]:
            mx = max((abs(p["value"]) for p in numeric), default=0) or 1
            rows = []
            for p in pts:
                extras = {k: v for k, v in p.items() if k not in ("label", "value")}
                tip = f"{p.get('label')}: {p['value']} {s.get('unit', '')}".strip()
                if extras:
                    tip += " · " + ", ".join(f"{k}={v}" for k, v in extras.items())
                rows.append({"label": p.get("label", ""), "value": p["value"],
                             "pct": round(100.0 * abs(p["value"]) / mx, 1), "tip": tip})
            d["_rows"] = rows
        else:
            d["_rows"] = [{"label": p.get("label", ""), "value": p.get("value", ""), "tip": ""}
                          for p in pts]
        out.append(d)
    return out


class RefBook:
    """Formal-document reference layer: every citation marker becomes a numbered
    superscript pointing at a References list — the display face of the machine
    layer (the raw report keeps the lint-checked markers)."""

    MARKER_RE = re.compile(r"\[(src|assume|derived|config|waived):\s*([^\]<]+?)\s*\]")

    def __init__(self, repo_root: Path, bq: str, edition: str | None):
        self.repo_root = repo_root
        self.bq = bq
        self.edition = edition
        self.refs: list[dict] = []
        self.index: dict[tuple, int] = {}

    def _entry(self, kind: str, value: str) -> dict:
        if kind == "src":
            ds, _, snap = value.rpartition("@")
            return {"kind": "Corpus dataset", "label": f"{ds} — snapshot {snap}",
                    "href": f"/documents#path=docs/project/corpus/{ds}/README.md",
                    "detail": f"immutable snapshot pinned by this edition; provenance in snapshots/{snap}/provenance.yml"}
        if kind == "assume":
            hits = list((self.repo_root / "docs" / "project" / "corpus").glob(f"*/*/assumptions/{value}.yml"))
            href = f"/documents#path={hits[0].relative_to(self.repo_root)}" if hits else None
            return {"kind": "Assumption record", "label": value, "href": href,
                    "detail": "stated estimate where data does not exist — method, confidence, and refresh trigger in the record"}
        if kind == "waived":
            hits = list((self.repo_root / "docs" / "project" / "corpus").glob(f"*/*/waivers/{value}.yml"))
            href = f"/documents#path={hits[0].relative_to(self.repo_root)}" if hits else None
            return {"kind": "Freshness waiver", "label": value, "href": href,
                    "detail": "stale-data acknowledgment with owner and expiry"}
        if kind == "derived":
            href = f"/commercial/{self.bq}/raw" + (f"?edition={self.edition}" if self.edition else "")
            return {"kind": "Computed series", "label": value, "href": href,
                    "detail": "deterministic computation output in this edition's data.json"}
        # config
        rel = value if value.startswith("docs/") else f"docs/project/commercial/{value}"
        return {"kind": "Declared configuration", "label": value,
                "href": f"/documents#path={rel}",
                "detail": "plan constant / threshold declared in versioned project configuration"}

    def number(self, kind: str, value: str) -> int:
        key = (kind, value)
        if key not in self.index:
            self.index[key] = len(self.refs) + 1
            self.refs.append({"n": len(self.refs) + 1, **self._entry(kind, value)})
        return self.index[key]

    def sup(self, kind: str, value: str) -> str:
        n = self.number(kind, value)
        return f'<sup class="cm-ref"><a href="#cm-ref-{n}" title="{kind}: {value}">{n}</a></sup>'

    def referencize_html(self, html: str) -> str:
        return self.MARKER_RE.sub(lambda m: self.sup(m.group(1), m.group(2)), html)

    def for_strings(self, evidence: list) -> list[int]:
        out = []
        for e in evidence or []:
            kind, _, value = str(e).partition(":")
            if value:
                out.append(self.number(kind.strip(), value.strip()))
        return out


def _doc_link_rewriter(doc_repo_rel: str):
    """Rewrite relative links in the rendered report so they open in the
    Documents viewer (same approach as the Submission view)."""
    doc_dir = Path(doc_repo_rel).parent

    def _norm(p: str) -> str:
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

    def repl(m: re.Match) -> str:
        href = m.group(1)
        if not href or href.startswith(("http://", "https://", "/", "#", "mailto:")):
            return m.group(0)
        base = href.split("#", 1)[0]
        if not base:
            return m.group(0)
        resolved = _norm(f"{doc_dir.as_posix()}/{base}")
        return f'href="/documents#path={resolved}" target="_blank" rel="noopener"'

    return lambda html: re.sub(r'href="([^"]+)"', repl, html)


@router.get("/commercial", response_class=HTMLResponse)
async def commercial_index(request: Request, render_error: str | None = None):
    cfg = get_config()
    index = load_index(cfg.repo_root)
    has_skill = skill_render_script(cfg.repo_root) is not None
    questions = [(_decorate_row(dict(q))) for q in (index or {}).get("questions", [])]
    categories = (index or {}).get("categories", [])
    by_cat = []
    for c in categories:
        rows = [q for q in questions if q.get("category") == c.get("key")]
        if rows:
            by_cat.append({"key": c["key"], "name": c.get("name", c["key"]), "rows": rows})
    counts = {
        "total": len(questions),
        "answered": sum(1 for q in questions if q["status"] == "answered"),
        "draft": sum(1 for q in questions if q["status"] == "draft-only"),
        "planned": sum(1 for q in questions if q["status"] == "not-implemented"),
    }
    return templates.TemplateResponse(
        request,
        "commercial_index.html",
        {"config": cfg, "index": index, "by_cat": by_cat, "counts": counts,
         "has_skill": has_skill, "render_error": render_error},
    )


@router.get("/commercial/catalog/grounding", response_class=PlainTextResponse)
async def catalog_grounding():
    """Compact rendition of the whole question board for the catalog's assistant
    drawer. Declared before /commercial/{bq}/grounding so it wins the match."""
    cfg = get_config()
    index = load_index(cfg.repo_root) or {}
    lines = ["# Commercial question board — status roll-up",
             "Tiers: corpus (pinned data) -> commercial (deterministic answers, claim-linted, "
             "draft->approved lifecycle) -> console (display). Evidence classes: measured / "
             "derived / assumed / unavailable. 'unvalidated' expectations are stand-ins to challenge.", ""]
    for q in index.get("questions", []):
        lines.append(f"## {q.get('id')} [{q.get('category')}] — {q.get('question')}")
        lines.append(f"status: {q.get('status')} · personas: {', '.join(q.get('personas', []))} · "
                     f"cadence: {q.get('cadence')}")
        if q.get("verdict_headline"):
            lines.append(f"verdict: {q['verdict_headline']}")
        if q.get("assumptions"):
            lines.append(f"rests on assumptions: {', '.join(q['assumptions'])}")
        if q.get("freshness"):
            lines.append(f"freshness: {q['freshness']} · evidence class: {q.get('evidence_class')}")
        lines.append("")
    return PlainTextResponse("\n".join(lines))


@router.get("/commercial/{bq}", response_class=HTMLResponse)
async def commercial_view(request: Request, bq: str, edition: str | None = None):
    cfg = get_config()
    q = question_row(cfg.repo_root, bq)
    if q is None:
        raise HTTPException(404, f"Unknown question '{bq}'. Run `/commercial render` to refresh the sidecar.")
    q = _decorate_row(dict(q))
    show_id = edition or q.get("approved_edition") or q.get("draft_edition")
    ed = load_edition(cfg.repo_root, bq, show_id) if show_id else None
    if ed is None and show_id:
        raise HTTPException(404, f"No edition '{show_id}' for {bq}.")
    ctx = {"config": cfg, "q": q, "ed": ed, "series": [], "verdicts": [],
           "report_html": "", "editions": q.get("editions", []),
           "ed_meta": None, "EDITION_META": EDITION_META,
           "expectations": [], "narrative": None, "newer_draft": None,
           "references": []}
    if ed:
        refbook = RefBook(cfg.repo_root, bq, ed["edition"])
        ctx["ed_meta"] = EDITION_META.get(ed["status"], EDITION_META["draft"])
        series = _decorate_series(ed["data"].get("series", []))
        # formal reference numbers for each series' source line
        for s in series:
            prov = s.get("provenance") or {}
            if prov.get("dataset"):
                s["_ref_n"] = refbook.number("src", f"{prov['dataset']}@{prov.get('snapshot', '?')}")
            elif prov.get("assumption"):
                s["_ref_n"] = refbook.number("assume", prov["assumption"])
            else:
                s["_ref_n"] = None
        ctx["series"] = series
        ctx["verdicts"] = ed["data"].get("verdicts", [])
        # expectations panel (plan vs actual, with met/not-met verdicts)
        exps = []
        for e in ed["data"].get("expectations", []):
            e = dict(e)
            e["_verdict"] = VERDICT_META.get(e.get("verdict"), VERDICT_META["not-evaluable"])
            exps.append(e)
        ctx["expectations"] = exps
        # narrative panel (issues / risks / watch)
        nar = ed["data"].get("narrative")
        if nar and any(nar.get(k) for k in ("issues", "risks", "watch")):
            groups = []
            for key, title in (("issues", "Issues — materialized, needs action"),
                               ("risks", "Risks — potential, mitigation identified"),
                               ("watch", "Watch")):
                items = []
                for it in nar.get(key, []):
                    it = dict(it)
                    it["_sev"] = SEV_META.get(it.get("severity", "medium"), SEV_META["medium"])
                    it["_refs"] = refbook.for_strings(it.get("evidence"))
                    items.append(it)
                if items:
                    # key name "entries" (not "items") — g.items in Jinja resolves dict.items
                    groups.append({"key": key, "title": title, "entries": items})
            ctx["narrative"] = groups
        # a newer draft exists beyond the shown approved edition
        if ed["status"] == "approved" and q.get("draft_edition") \
                and q["draft_edition"] > ed["edition"]:
            ctx["newer_draft"] = q["draft_edition"]
        abs_report = cfg.repo_root / ed["report_path"]
        if abs_report.is_file():
            try:
                rendered = doc_renderer.render(abs_report)
                html = _doc_link_rewriter(ed["report_path"])(rendered.body_html or "")
                # formal-document reference layer: markers -> superscript numbers
                ctx["report_html"] = refbook.referencize_html(html)
            except Exception:
                ctx["report_html"] = ""
        ctx["references"] = refbook.refs
        # assumption chips → open the record in the Documents viewer when possible
        chips = []
        for aid in q.get("assumptions", []):
            hits = list((cfg.repo_root / "docs" / "project" / "corpus").glob(f"*/*/assumptions/{aid}.yml"))
            link = f"/documents#path={hits[0].relative_to(cfg.repo_root)}" if hits else None
            chips.append({"id": aid, "link": link})
        ctx["assumption_chips"] = chips
    return templates.TemplateResponse(request, "commercial_view.html", ctx)


@router.get("/commercial/{bq}/data", response_class=HTMLResponse)
async def commercial_data(request: Request, bq: str, edition: str | None = None):
    """Dedicated tabular view: the pinned snapshots' normalized rows (the data
    behind the charts) plus each series' points — sortable, filterable, searchable.
    The console still computes nothing; it displays pinned rows verbatim."""
    cfg = get_config()
    q = question_row(cfg.repo_root, bq)
    if q is None:
        raise HTTPException(404, f"Unknown question '{bq}'.")
    show_id = edition or q.get("approved_edition") or q.get("draft_edition")
    ed = load_edition(cfg.repo_root, bq, show_id) if show_id else None
    if ed is None:
        raise HTTPException(404, f"No edition for {bq} — nothing to tabulate.")
    tables = []
    for ds, snap in ed.get("pins", {}).items():
        t = load_pinned_table(cfg.repo_root, ds, snap)
        if t:
            t["id"] = f"ds-{len(tables)}"
            t["title"] = f"{ds.split('/')[-1]} @ {snap}"
            t["kind"] = "Pinned corpus snapshot"
            tables.append(t)
    # series points as tables (the table form of every chart)
    for s in ed["data"].get("series", []):
        if s.get("kind") == "timeseries":
            cols, rows = ["series", "date", "value"], []
            for ln in s.get("lines", []):
                rows += [{"series": ln.get("label", ""), "date": p["x"], "value": str(p["y"])}
                         for p in ln.get("points", [])]
        else:
            pts = s.get("points", [])
            if not pts:
                continue
            extra = sorted({k for p in pts for k in p} - {"label", "value"})
            cols = ["label", "value", *extra]
            rows = [{c: str(p.get(c, "")) for c in cols} for p in pts]
        tables.append({"id": f"s-{s.get('id')}", "title": s.get("label", s.get("id")),
                       "kind": f"Series ({s.get('evidence_class')})", "columns": cols,
                       "rows": rows, "dataset": None, "snapshot": None, "file": "data.json"})
    return templates.TemplateResponse(
        request, "commercial_data.html",
        {"config": cfg, "q": q, "ed": ed, "tables": tables},
    )


@router.get("/commercial/{bq}/raw", response_class=JSONResponse)
async def commercial_raw(bq: str, edition: str | None = None):
    cfg = get_config()
    q = question_row(cfg.repo_root, bq)
    if q is None:
        raise HTTPException(404, f"Unknown question '{bq}'.")
    show_id = edition or q.get("approved_edition") or q.get("draft_edition")
    ed = load_edition(cfg.repo_root, bq, show_id) if show_id else None
    if ed is None:
        raise HTTPException(404, f"No edition for {bq}.")
    return JSONResponse(ed["data"])


@router.get("/commercial/{bq}/grounding", response_class=PlainTextResponse)
async def commercial_grounding(bq: str, edition: str | None = None):
    """Compact textual rendition of the shown answer for the Assistant drawer."""
    cfg = get_config()
    q = question_row(cfg.repo_root, bq)
    if q is None:
        raise HTTPException(404, f"Unknown question '{bq}'.")
    show_id = edition or q.get("approved_edition") or q.get("draft_edition")
    ed = load_edition(cfg.repo_root, bq, show_id) if show_id else None
    lines = [
        f"# Business question {bq} — {q.get('question')}",
        f"Category: {q.get('category')} · Personas: {', '.join(q.get('personas', []))} · "
        f"Cadence: {q.get('cadence')} · Status: {q.get('status')}",
    ]
    if ed:
        lines.append(f"Shown edition: {ed['edition']} ({ed['status']}); pins: "
                     + ", ".join(f"{k}@{v}" for k, v in ed.get("pins", {}).items()))
        for v in ed["data"].get("verdicts", []):
            lines.append(f"Verdict [{v.get('evidence_class')}]: {v.get('headline')}")
        for s in ed["data"].get("series", []):
            prov = s.get("provenance") or {}
            src = prov.get("dataset") and f"{prov['dataset']}@{prov.get('snapshot')}" \
                or prov.get("assumption") or prov.get("note", "")
            lines.append(f"## {s.get('label')} [{s.get('evidence_class')}] (source: {src})")
            for p in s.get("points", []):
                lines.append(f"- {p.get('label')}: {p.get('value')} {s.get('unit', '')}")
        report = cfg.repo_root / ed["report_path"]
        if report.is_file():
            lines.append("\n## Full report (marker-cited)\n")
            lines.append(report.read_text(encoding="utf-8"))
    else:
        lines.append("No computed answer yet — the question is in the catalog as roadmap.")
    return PlainTextResponse("\n".join(lines))


@router.post("/commercial/render")
async def commercial_render():
    """Shell to the commercial skill's `render` to refresh the sidecar."""
    cfg = get_config()
    script = skill_render_script(cfg.repo_root)
    if script is None:
        return RedirectResponse(
            url="/commercial?render_error=" + quote(
                "The commercial skill is not installed at .claude/skills/commercial/.", safe=""),
            status_code=303,
        )
    try:
        proc = subprocess.run(
            [sys.executable, str(script), "render"],
            cwd=str(cfg.repo_root), capture_output=True, text=True, timeout=60,
        )
    except subprocess.TimeoutExpired:
        return RedirectResponse(url="/commercial?render_error=" + quote("render timed out", safe=""),
                                status_code=303)
    if proc.returncode != 0:
        return RedirectResponse(
            url="/commercial?render_error=" + quote(((proc.stdout or "") + (proc.stderr or ""))[:2048], safe=""),
            status_code=303,
        )
    return RedirectResponse(url="/commercial", status_code=303)
