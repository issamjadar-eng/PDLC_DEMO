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
    _read_yaml,
    load_edition,
    load_index,
    load_pinned_table,
    question_row,
    skill_render_script,
    team_names,
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

# Reserved explainer targets (schema 1.1) → default labels when the sidecar
# author omits one. Series targets default to the series' own label.
EXPLAINER_DEFAULT_LABELS = {
    "question": "About this analysis",
    "verdict": "The verdict",
    "expectations": "Assumptions & expectations",
}

# Kind glossary — console-owned chrome for the Data tab's artifact inventory.
# Static plain-language copy explaining what each artifact KIND is; generic and
# project-agnostic (the per-file summaries come from authored metadata instead).
KIND_GLOSSARY = {
    "raw": {
        "label": "Raw acquisition payload",
        "what": "The exact bytes fetched from the source system when the snapshot was taken, kept unmodified.",
        "why": "It is the ground truth everything else derives from — if a number is ever questioned, this file settles what the source actually said at acquisition time.",
        "how_to_read": "You rarely read it directly; its checksum in provenance.yml proves the normalized data came from these exact bytes.",
    },
    "normalized": {
        "label": "Normalized data",
        "what": "The raw payload reshaped into a clean, consistent table (CSV) with declared columns.",
        "why": "Analyses run against this tidy form, not the raw payload, so every answer uses the same well-defined fields.",
        "how_to_read": "Column meanings are declared in dataset.yml; the rows appear under Structured above.",
    },
    "provenance": {
        "label": "Provenance record",
        "what": "A hash-chain audit trail for the snapshot: where each file came from, when, and the checksum of every step from raw bytes to normalized table.",
        "why": "It makes the data tamper-evident — any change to any file breaks the recorded checksums, so you can trust the numbers were not quietly edited.",
        "how_to_read": "Each source lists its origin and retrieval time; each transform links its output hash back to its input hash.",
    },
    "dataset-config": {
        "label": "Dataset configuration",
        "what": "The dataset's declared contract: what it contains, where it is acquired from, how it is normalized, its column schema, and how old it may get before it counts as stale.",
        "why": "It is the single place that defines what this data IS — analyses and freshness checks both read it.",
        "how_to_read": "The description says what the data covers; max_age_days sets the freshness bar; the schema block names each column.",
    },
    "readme": {
        "label": "Dataset README",
        "what": "The human-facing overview of the dataset — what it covers, which questions consume it, and known limitations.",
        "why": "It carries the caveats that numbers alone cannot: what the data does NOT capture and how it should (and should not) be used.",
        "how_to_read": "Read the limitation notes before leaning on any conclusion drawn from this dataset.",
    },
    "assumption": {
        "label": "Assumption record",
        "what": "A stated estimate used where real data does not exist — with the estimation method, the value or range used, a confidence level, and a trigger for revisiting it.",
        "why": "It keeps guesses honest: every assumed figure in an answer traces to one of these records instead of hiding inside the analysis.",
        "how_to_read": "Check the confidence level and the refresh trigger — a low-confidence assumption is an invitation to challenge the number.",
    },
    "waiver": {
        "label": "Freshness waiver",
        "what": "A time-boxed, owner-signed acknowledgment that a dataset is older than its freshness limit but is knowingly being used anyway.",
        "why": "Stale data can silently mislead — a waiver makes the staleness a visible, expiring decision rather than an accident.",
        "how_to_read": "Note the reason and the expiry date; an expired waiver means the data must be re-acquired before reuse.",
    },
    "delta": {
        "label": "Delta report",
        "what": "A machine-generated diff between this snapshot and the previous one: how many rows were added, removed, or changed.",
        "why": "It shows at a glance whether a refresh actually moved the data — and flags unexpected churn worth investigating.",
        "how_to_read": "The rows line reads added / removed / changed; the sections below list the affected record ids.",
    },
}


def _explainers_for(q: dict, series: list) -> dict:
    """Normalize the sidecar's schema-1.1 `explainers` map (absent on 1.0 rows
    → {}). Keys are series ids or the reserved question/verdict/expectations."""
    raw = q.get("explainers")
    if not isinstance(raw, dict):
        return {}
    labels_by_series = {s.get("id"): s.get("label") for s in series}
    out = {}
    for key, ex in raw.items():
        if not isinstance(ex, dict) or not ex.get("what"):
            continue
        default = EXPLAINER_DEFAULT_LABELS.get(key) or labels_by_series.get(key) or key
        out[key] = {"label": ex.get("label") or default,
                    "what": ex.get("what", ""),
                    "why": ex.get("why", ""),
                    "how_to_read": ex.get("how_to_read", "")}
    return out


def _terms_for(q: dict) -> list:
    """Sidecar `terms` list (schema 1.1) — absent/malformed → []."""
    out = []
    for t in q.get("terms") or []:
        if isinstance(t, dict) and t.get("term") and t.get("definition"):
            out.append({"term": str(t["term"]), "definition": str(t["definition"])})
    return out


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
            "_pts": [{"cx": round(X(p["x"]), 1), "cy": round(Y(p["y"]), 1), "v": p["y"]}
                     for p in pts],
            "end_x": round(X(pts[-1]["x"]), 1), "end_y": round(Y(pts[-1]["y"]), 1),
        })
    # de-collide direct end labels: lines ending at similar values otherwise overlap
    order = sorted(glines, key=lambda g: g["end_y"])
    for i, g in enumerate(order):
        g["label_y"] = g["end_y"]
        if i and g["label_y"] - order[i - 1]["label_y"] < 13:
            g["label_y"] = order[i - 1]["label_y"] + 13
    _place_point_labels(glines, spacing=(W - L - R) / span, h=H, bottom=B)
    for g in glines:
        g.pop("_pts", None)
    return {"w": W, "h": H, "lines": glines, "x0": xs[0][:10], "x1": xs[-1][:10],
            "ymax": ymax, "y0_y": round(Y(0), 1), "ymax_y": round(Y(ymax), 1), "left": L,
            "right": W - R}


def _fmt_point(v) -> str:
    if isinstance(v, float) and v.is_integer():
        return f"{int(v):,}"
    if isinstance(v, int):
        return f"{v:,}"
    return str(v)


def _place_point_labels(glines: list, spacing: float, h: int, bottom: int) -> None:
    """Direct value labels on timeseries points (dataviz: direct labels beat
    hover-only). Density heuristic: ≤2 lines AND comfortable horizontal room
    (≥60px between points at viewbox scale) → label every point; otherwise
    label only the decision-relevant points (endpoints + min/max per line) and
    leave the rest to the hover tooltips. Labels sit above the point, flip
    below when the line crowds the space above, and are skipped rather than
    overlapped."""
    dense_ok = len(glines) <= 2 and spacing >= 60
    placed: list[tuple[float, float]] = []
    for g in glines:
        pp = g["_pts"]
        if dense_ok:
            idxs = list(range(len(pp)))
        else:
            vals = [p["v"] for p in pp]
            idxs = sorted({0, len(pp) - 1, vals.index(min(vals)), vals.index(max(vals))})
        labels = []
        for j in idxs:
            p = pp[j]
            above, below = p["cy"] - 8, p["cy"] + 16
            # a neighboring point noticeably higher on screen means the line
            # slopes through the space above this point — label below instead
            crowded_above = any(
                0 <= k < len(pp) and pp[k]["cy"] < p["cy"] - 12
                for k in (j - 1, j + 1))
            cand = [below, above] if crowded_above else [above, below]
            ly = next((c for c in cand
                       if not any(abs(px - p["cx"]) < 34 and abs(py - c) < 11
                                  for px, py in placed)), None)
            if ly is None:
                continue  # skip rather than overlap
            ly = min(max(ly, 9.0), float(h - bottom + 12))
            placed.append((p["cx"], ly))
            labels.append({"x": p["cx"], "y": round(ly, 1), "v": _fmt_point(p["v"])})
        g["labels"] = labels


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
        if s.get("kind") == "stat":
            # headline numbers — a stat tile row, not a chart
            d["_stat"] = [{"label": p.get("label", ""), "value": p.get("value", ""),
                           "sub": p.get("sub", "")} for p in s.get("points", [])]
            d["_rows"] = []
            d["_numeric"] = False
            out.append(d)
            continue
        if s.get("kind") == "paired-bars":
            # two measures per category (plan vs actual) — grouped thin bars, legend required
            pairs = s.get("pairs", {})
            pts = s.get("points", [])
            mx = max((max(abs(p.get("a", 0)), abs(p.get("b", 0))) for p in pts), default=0) or 1
            d["_paired"] = {
                "a_label": pairs.get("a_label", "actual"),
                "b_label": pairs.get("b_label", "plan"),
                "rows": [{"label": p.get("label", ""),
                          "a": p.get("a", 0), "b": p.get("b", 0),
                          "a_pct": round(100.0 * abs(p.get("a", 0)) / mx, 1),
                          "b_pct": round(100.0 * abs(p.get("b", 0)) / mx, 1),
                          "tip": f"{p.get('label')}: {pairs.get('a_label', 'a')} {p.get('a')} · "
                                 f"{pairs.get('b_label', 'b')} {p.get('b')} {s.get('unit', '')}".strip()}
                         for p in pts],
            }
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
    # default: the NEWEST edition (draft included, clearly watermarked) — reviewers see
    # the latest work; the approved record is one click away in the editions rail
    show_id = edition or q.get("latest_edition") or q.get("approved_edition") or q.get("draft_edition")
    ed = load_edition(cfg.repo_root, bq, show_id) if show_id else None
    if ed is None and show_id:
        raise HTTPException(404, f"No edition '{show_id}' for {bq}.")
    ctx = {"config": cfg, "q": q, "ed": ed, "series": [], "verdicts": [],
           "report_html": "", "editions": q.get("editions", []),
           "ed_meta": None, "EDITION_META": EDITION_META,
           "expectations": [], "narrative": None, "newer_draft": None,
           "references": [], "quality": None, "tables": [], "unstructured": [],
           "explainers": _explainers_for(q, []), "terms": _terms_for(q),
           "kind_glossary": KIND_GLOSSARY,
           "explain_json": {}, "team": team_names(cfg.repo_root),
           "approved_qp": request.query_params.get("approved"),
           "pr_url": request.query_params.get("pr"),
           "approve_error": request.query_params.get("approve_error"),
           "push_error": request.query_params.get("push_error")}
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
        # plain-language explainer layer (sidecar schema 1.1; absent on 1.0 → {})
        ctx["explainers"] = _explainers_for(q, series)
        for s in series:
            s["_explainer"] = ctx["explainers"].get(s.get("id"))
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
        # quality & audit tab — machine-generated lint/reference/freshness audit
        # plus agent-recorded verification/red-team verdicts
        VER_META = {"CONFIRMED": "vx-met", "PASS": "vx-met", "HONORED": "vx-met",
                    "CONFIRMED-WITH-CAVEAT": "vx-risk", "HONORED-WITH-NOTES": "vx-risk",
                    "REFUTED": "vx-notmet", "DEVIATION": "vx-notmet"}
        quality = ed.get("quality")
        if quality:
            quality = dict(quality)
            CHECK_META = {"pass": {"cls": "vx-met", "label": "✓ pass"},
                          "warn": {"cls": "vx-risk", "label": "! warnings"},
                          "fail": {"cls": "vx-notmet", "label": "✗ fail"}}
            for chk in quality.get("lint", {}).get("checks", []):
                chk["_meta"] = CHECK_META.get(chk.get("status"), CHECK_META["pass"])
            for f in quality.get("freshness", []):
                f["_band"] = FRESH_META.get(f.get("band"), FRESH_META["fresh"])
            for v in quality.get("verifications", []):
                v["_cls"] = VER_META.get(str(v.get("verdict", "")).upper(), "vx-none")
                if v.get("detail_ref"):
                    v["_detail_link"] = f"/documents#path={v['detail_ref']}"
        ctx["quality"] = quality
        # Data tab: structured tables + unstructured artifact inventory
        ctx["tables"] = _build_tables(cfg.repo_root, ed)
        ctx["unstructured"] = _build_unstructured(cfg.repo_root, ed)
        # Plan tab: user-owned analysis contract, rendered; status from quality.json
        PLAN_META = {"in-sync": {"label": "In sync — edition computed under this plan", "cls": "vx-met"},
                     "drifted": {"label": "Plan changed since this edition — review intent, re-answer", "cls": "vx-risk"},
                     "unpinned": {"label": "Edition predates plan pinning — re-answer to pin", "cls": "vx-risk"},
                     "missing": {"label": "No plan yet — scaffold with plan-init", "cls": "vx-notmet"}}
        plan_file = cfg.repo_root / "docs" / "project" / "commercial" / "plans" / f"{bq}.md"
        ctx["plan_html"] = ""
        ctx["plan_status"] = None
        ctx["plan_path"] = f"docs/project/commercial/plans/{bq}.md"
        if plan_file.is_file():
            try:
                ctx["plan_html"] = doc_renderer.render(plan_file).body_html or ""
            except Exception:
                ctx["plan_html"] = ""
        pstatus = (quality or {}).get("plan") or {}
        ctx["plan_status"] = PLAN_META.get(pstatus.get("status"),
                                           PLAN_META["missing"] if not plan_file.is_file() else None)
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
    # one shared modal payload: authored explainers + the console-owned kind
    # glossary (Data tab), namespaced so keys can never collide
    ctx["explain_json"] = {**ctx["explainers"],
                           **{f"kind:{k}": v for k, v in KIND_GLOSSARY.items()}}
    return templates.TemplateResponse(request, "commercial_view.html", ctx)


def _build_tables(repo_root: Path, ed: dict) -> list:
    """Structured tables behind an answer: pinned snapshot rows + each series'
    table form. Shared by the standalone data view and the answer Data tab."""
    tables = []
    for ds, snap in ed.get("pins", {}).items():
        t = load_pinned_table(repo_root, ds, snap)
        if t:
            t["id"] = f"ds-{len(tables)}"
            t["title"] = f"{ds.split('/')[-1]} @ {snap}"
            t["kind"] = "Pinned corpus snapshot"
            tables.append(t)
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
    return tables


def _truncate(text: str, n: int = 140) -> str:
    text = " ".join(str(text).split())
    return text if len(text) <= n else text[: n - 1].rstrip() + "…"


def _first_sentence(text: str) -> str:
    text = " ".join(str(text).split())
    m = re.search(r"[.!?](?:\s|$)", text)
    return text[: m.end()].strip() if m else _truncate(text)


def _readme_first_para(p: Path) -> str:
    """First non-banner paragraph of a README — skips headings, italic demo
    banners, blockquotes, HTML comments, and list bullets."""
    try:
        lines = p.read_text(encoding="utf-8").splitlines()
    except OSError:
        return ""
    para: list[str] = []
    for ln in lines:
        st = ln.strip()
        if not st:
            if para:
                break
            continue
        if not para and st.startswith(("#", "_", ">", "-", "*", "<!--", "|")):
            continue
        para.append(st)
    return _truncate(" ".join(para)) if para else ""


def _raw_source_summary(prov: dict | None, fname: str) -> str:
    """Summary for a raw payload file from the snapshot's authored provenance
    sources[] — never invented; empty string when provenance is silent."""
    from urllib.parse import urlparse

    for src in (prov or {}).get("sources", []) or []:
        files = {Path(f.get("path", "")).name for f in src.get("files", []) or []}
        if files and fname not in files:
            continue
        origin = src.get("system") or ""
        if not origin and src.get("url"):
            origin = urlparse(str(src["url"])).netloc
        bits = ["Byte-pinned acquisition payload"]
        head = " · ".join(x for x in (str(src.get("type", "")).strip(), origin) if x)
        if head:
            bits.append(head)
        if src.get("retrieved_at"):
            bits.append(f"retrieved {str(src['retrieved_at'])[:10]}")
        out = " — ".join(bits[:2]) + (f", {bits[2]}" if len(bits) > 2 else "")
        if src.get("notes"):
            out += f" · {_truncate(src['notes'], 80)}"
        return out
    return ""


def _provenance_summary(prov: dict | None) -> str:
    if not prov:
        return ""
    checks = prov.get("checks") or {}
    if "schema_valid" not in checks and "asserts_passed" not in checks:
        status = "not recorded"
    elif checks.get("schema_valid", True) and checks.get("asserts_passed", True):
        status = "passed"
    else:
        status = "failed"
    n_src = len(prov.get("sources") or [])
    n_tr = len(prov.get("transforms") or [])
    return f"Hash-chain provenance: {n_src} source(s), {n_tr} transform(s), schema checks {status}"


def _assumption_summary(rec: dict | None) -> str:
    if not rec:
        return ""
    bits = [str(rec.get("title") or "assumption record")]
    meta = " · ".join(x for x in (
        f"status {rec['status']}" if rec.get("status") else "",
        f"confidence {rec['confidence']}" if rec.get("confidence") else "") if x)
    if meta:
        bits.append(meta)
    out = " — ".join(bits)
    if rec.get("value_or_range"):
        out += f": {_truncate(rec['value_or_range'], 110)}"
    return out


def _waiver_summary(rec: dict | None) -> str:
    if not rec:
        return ""
    out = _truncate(rec.get("reason") or "freshness waiver", 110)
    meta = " · ".join(x for x in (
        f"expires {rec['expires']}" if rec.get("expires") else "",
        f"status {rec['status']}" if rec.get("status") else "") if x)
    return f"{out} — {meta}" if meta else out


def _delta_summary(p: Path) -> str:
    try:
        for ln in p.read_text(encoding="utf-8").splitlines():
            st = ln.strip()
            if st.startswith("- rows:"):
                return "Snapshot delta vs prior: " + st[2:].strip()
    except OSError:
        pass
    return ""


def _build_unstructured(repo_root: Path, ed: dict) -> list:
    """Unstructured artifacts behind an answer: per pinned dataset — raw payloads,
    provenance.yml, dataset config/README, delta report, assumption + waiver
    records. Each carries a one-line human summary derived ONLY from authored
    metadata (provenance sources, dataset description, record fields — the
    console invents nothing) plus a kind key into the static KIND_GLOSSARY."""
    groups = []
    for ds, snap in ed.get("pins", {}).items():
        base = repo_root / "docs" / "project" / "corpus" / ds
        sdir = base / "snapshots" / snap
        prov = _read_yaml(sdir / "provenance.yml")
        artifacts = []  # key name "artifacts" — g.items in Jinja resolves dict.items

        def add(p: Path, label: str, kind: str, summary: str = ""):
            if p.exists():
                rel = p.relative_to(repo_root)
                artifacts.append({"label": label, "name": p.name, "kind": kind,
                              "summary": summary,
                              "size_kb": round(p.stat().st_size / 1024, 1),
                              "href": f"/documents#path={rel}"})

        for raw in sorted((sdir / "raw").glob("*")) if (sdir / "raw").is_dir() else []:
            add(raw, "raw payload (as acquired)", "raw",
                _raw_source_summary(prov, raw.name))
        add(sdir / "provenance.yml", "provenance hash chain", "provenance",
            _provenance_summary(prov))
        add(sdir / "delta-report.md", "delta vs prior snapshot", "delta",
            _delta_summary(sdir / "delta-report.md"))
        dcfg = _read_yaml(base / "dataset.yml")
        add(base / "dataset.yml", "dataset config (schema, acquisition, cadence)",
            "dataset-config",
            _first_sentence((dcfg or {}).get("description") or ""))
        add(base / "README.md", "dataset README", "readme",
            _readme_first_para(base / "README.md"))
        for a in sorted((base / "assumptions").glob("A-*.yml")) if (base / "assumptions").is_dir() else []:
            add(a, "assumption record", "assumption", _assumption_summary(_read_yaml(a)))
        for w in sorted((base / "waivers").glob("W-*.yml")) if (base / "waivers").is_dir() else []:
            add(w, "freshness waiver", "waiver", _waiver_summary(_read_yaml(w)))
        groups.append({"dataset": ds, "snapshot": snap, "artifacts": artifacts})
    return groups


@router.get("/commercial/{bq}/data", response_class=HTMLResponse)
async def commercial_data(request: Request, bq: str, edition: str | None = None):
    """Dedicated tabular view (deep-linkable twin of the answer's Data tab)."""
    cfg = get_config()
    q = question_row(cfg.repo_root, bq)
    if q is None:
        raise HTTPException(404, f"Unknown question '{bq}'.")
    show_id = edition or q.get("latest_edition") or q.get("approved_edition")
    ed = load_edition(cfg.repo_root, bq, show_id) if show_id else None
    if ed is None:
        raise HTTPException(404, f"No edition for {bq} — nothing to tabulate.")
    return templates.TemplateResponse(
        request, "commercial_data.html",
        {"config": cfg, "q": q, "ed": ed, "tables": _build_tables(cfg.repo_root, ed)},
    )


def _run(cmd: list, cwd: Path, timeout: int = 120):
    try:
        p = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, timeout=timeout)
        return p.returncode, (p.stdout or "") + (p.stderr or "")
    except subprocess.TimeoutExpired:
        return 1, f"timed out: {' '.join(str(c) for c in cmd)}"


def _push_approval(repo_root: Path, bq: str, edition: str, approver: str):
    """The project's push sequence for the approved edition: branch -> stage only
    the answer + sidecar paths -> commit -> PR -> auto-merge -> back to main.
    Returns (pr_url or None, error or None). Approval itself already happened —
    a push failure leaves it approved locally and reports honestly."""
    branch = f"console/approve-{bq}-{edition}".replace(" ", "")
    paths = [f"docs/project/commercial/reports/{bq}", "docs/project/commercial/.console"]
    title = f"approve {bq}@{edition} via console ({approver})"
    body = (f"Answer edition {bq}@{edition} approved by {approver} via the project-console "
            f"approve action (gate: claim lint + pin freshness; content hash-pinned in "
            f"approval.yml).\n\n🤖 Generated with [Claude Code](https://claude.com/claude-code)")
    steps = [
        (["git", "checkout", "-B", branch], "create branch"),
        (["git", "add", *paths], "stage"),
        (["git", "commit", "-m", title + "\n\n" + body.split("\n\n")[0]], "commit"),
        (["git", "push", "-u", "origin", branch, "--force-with-lease"], "push"),
    ]
    for cmd, label in steps:
        rc, out = _run(cmd, repo_root)
        if rc != 0:
            _run(["git", "checkout", "main"], repo_root)
            return None, f"{label} failed: {out[-800:]}"
    rc, out = _run(["gh", "pr", "create", "--title", title, "--body", body], repo_root)
    pr_url = next((ln.strip() for ln in out.splitlines() if ln.strip().startswith("http")), None)
    if rc != 0 and not pr_url:
        _run(["git", "checkout", "main"], repo_root)
        return None, f"PR create failed: {out[-800:]}"
    rc, out = _run(["gh", "pr", "merge", branch, "--merge", "--delete-branch"], repo_root, timeout=180)
    _run(["git", "checkout", "main"], repo_root)
    _run(["git", "pull", "--ff-only"], repo_root)
    _run(["git", "branch", "-D", branch], repo_root)
    if rc != 0:
        return pr_url, f"PR created but merge failed: {out[-800:]}"
    return pr_url, None


@router.post("/commercial/{bq}/approve")
async def commercial_approve(request: Request, bq: str):
    """UI approval: run the gated approve (lint + freshness enforced by the skill),
    refresh the sidecar, then push to the repo per the project's git workflow."""
    cfg = get_config()
    form = await request.form()
    edition = str(form.get("edition") or "")
    approver = str(form.get("approver") or "").strip()
    note = str(form.get("verify_note") or "").strip() or "approved via console UI (no independent verification recorded)"
    if not approver:
        return RedirectResponse(f"/commercial/{bq}?approve_error=" + quote("pick an approver", safe=""), status_code=303)
    script = skill_render_script(cfg.repo_root)
    if script is None:
        return RedirectResponse(f"/commercial/{bq}?approve_error=" + quote("commercial skill not installed", safe=""), status_code=303)
    rc, out = _run([sys.executable, str(script), "approve", bq, "--edition", edition,
                    "--by", approver, "--verify-note", note], cfg.repo_root)
    if rc != 0:
        return RedirectResponse(
            f"/commercial/{bq}?edition={edition}&approve_error=" + quote(out[-1200:], safe=""), status_code=303)
    _run([sys.executable, str(script), "render"], cfg.repo_root)
    pr_url, err = _push_approval(cfg.repo_root, bq, edition, approver)
    q = f"/commercial/{bq}?approved={quote(edition, safe='')}"
    if pr_url:
        q += "&pr=" + quote(pr_url, safe="")
    if err:
        q += "&push_error=" + quote(err, safe="")
    return RedirectResponse(q, status_code=303)


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
