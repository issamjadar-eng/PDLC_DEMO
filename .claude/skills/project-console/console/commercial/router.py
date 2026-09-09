"""Commercial section routes — the display tier of the business-question stack.

One router serves EVERY business domain (Commercial, Finance, Manufacturing, ...):
the `{domain}` path segment selects the domain root `docs/project/<domain>/`.
`/commercial...` is kept as a permanent redirect to `/domains/commercial...`.

GET  /domains/{domain}                 — question catalog (category rail + answer cards)
GET  /domains/{domain}/{bq}            — answer view (verdict, charts, provenance, report, history)
GET  /domains/{domain}/{bq}/raw        — the shown edition's data.json (debug)
GET  /domains/{domain}/{bq}/grounding  — compact text rendition for the assistant drawer
POST /domains/{domain}/render          — shell to the engine's `render --domain <domain>`

The console is a pure consumer of the `commercial` skill's sidecars
(`schema_version 1.0`). It plots the sidecar's series verbatim and computes
nothing — every figure on screen was emitted by the skill's deterministic
computation and claim-linted before it got here. Evidence-class badges,
freshness bands, assumption chips, and draft watermarks are rendered from
sidecar fields so a chart can never overstate its grounding.
"""
from __future__ import annotations

import html as _html
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote

import markdown as _md_lib
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, PlainTextResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from console.commercial.loader import (
    _read_yaml,
    domain_meta,
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

DEFAULT_DOMAIN = "commercial"


def _domain_ctx(cfg, domain: str) -> dict:
    """Template context shared by every domain page: identity block + URL/path
    bases. Unknown domain (no sidecar, not the historical default) → 404 so a
    typo'd slug never renders an empty Commercial-looking page."""
    dm = domain_meta(cfg.repo_root, domain)
    if load_index(cfg.repo_root, domain) is None and domain != DEFAULT_DOMAIN:
        raise HTTPException(404, f"Unknown business domain '{domain}'. A domain is any "
                                 f"docs/project/<slug>/.console/<slug>-index.json — render one first.")
    return {"domain": domain, "dm": dm, "base": dm["href"], "droot": dm["root_rel"]}


@router.api_route("/commercial", methods=["GET", "POST"], include_in_schema=False)
@router.api_route("/commercial/{rest:path}", methods=["GET", "POST"], include_in_schema=False)
async def commercial_legacy(request: Request, rest: str = ""):
    """The pre-domain URL scheme. 307 keeps method + body so bookmarked GETs and
    in-flight form POSTs both land on /domains/commercial/..."""
    url = f"/domains/{DEFAULT_DOMAIN}" + (f"/{rest}" if rest else "")
    if request.url.query:
        url += "?" + request.url.query
    return RedirectResponse(url, status_code=307)

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


# ── "How it was built" ───────────────────────────────────────────────────────
# A reader-facing walkthrough of the reasoning behind an answer, DERIVED ENTIRELY
# from material that already exists and is already checked: the user-authored
# analysis plan, the computation's own recorded derivations, the corpus assumption
# records, the pins, and the expectation verdicts. It authors nothing and stores
# nothing, so it cannot drift from the answer it explains.
#
# Deliberately NOT called "chain of thought": in this architecture no model reasons
# its way to a figure — a deterministic script computes every number. The tab
# explains the ANALYSIS, not an assistant.

PLAN_SECTIONS = {
    "goal": "goal",
    "approach": "approach",
    "data": "data",
    "assertions": "assertions",
}


def _plan_sections(plan_md: str) -> dict:
    """Split the analysis plan into its `## ` sections, keyed by the first word of
    the heading (goal / approach / data / assertions …). Headings carry an em-dash
    subtitle in practice ("Goal — the decision this answer serves")."""
    out, cur, buf = {}, None, []
    for line in (plan_md or "").splitlines():
        if line.startswith("## "):
            if cur:
                out[cur] = "\n".join(buf).strip()
            head = line[3:].strip().lower()
            key = re.split(r"[\s—-]", head)[0]
            cur, buf = PLAN_SECTIONS.get(key), []
        elif cur:
            buf.append(line)
    if cur:
        out[cur] = "\n".join(buf).strip()
    return {k: v for k, v in out.items() if v}


def _pin_freshness(repo_root: Path, ds: str, snap: str) -> dict:
    """Age and band computed NOW — deliberately not read from the edition's
    quality.json, which froze the age at lint time. A snapshot that has since gone
    stale would otherwise read "fresh" here while the header, which recomputes,
    says "Stale": the two surfaces must not contradict each other. Banding mirrors
    the engine (stale past max_age_days, aging past three quarters of it)."""
    import datetime as _dt
    max_age, rec = 90, _read_yaml(repo_root / "docs" / "project" / "corpus" / ds / "dataset.yml")
    if isinstance(rec, dict):
        try:
            max_age = int(rec.get("max_age_days", 90))
        except (TypeError, ValueError):
            max_age = 90
    try:
        age = (_dt.date.today() - _dt.date.fromisoformat(str(snap).split(".")[0])).days
    except ValueError:
        return {"age": None, "max_age": max_age, "band": ""}
    band = "stale" if age > max_age else ("aging" if age > max_age * 0.75 else "fresh")
    return {"age": age, "max_age": max_age, "band": band}


def _how_ctx(repo_root: Path, q: dict, ed: dict, ctx: dict, domain: str) -> dict:
    """Walkthrough + the challenge list. Every row points at something a reader can
    actually change on the next revision."""
    from console.commercial.loader import _root as _domain_root
    bq = q["id"]
    plan_file = _domain_root(repo_root, domain) / "plans" / f"{bq}.md"
    secs = _plan_sections(plan_file.read_text(encoding="utf-8")) if plan_file.is_file() else {}
    how = {"plan_path": f"docs/project/{domain}/plans/{bq}.md",
           "has_plan": plan_file.is_file(),
           "goal_html": _md_to_html(secs["goal"]) if secs.get("goal") else "",
           "approach_html": _md_to_html(secs["approach"]) if secs.get("approach") else "",
           "limits_html": _md_to_html(secs["assertions"]) if secs.get("assertions") else ""}

    # how each figure was produced — recorded by the computation itself
    how["derivations"] = [
        {"label": sr.get("label") or sr.get("id"), "id": sr.get("id"),
         "method": (sr.get("derivation") or {}).get("method", ""),
         "inputs": (sr.get("derivation") or {}).get("inputs", []),
         "evidence": sr.get("_evidence", {})}
        for sr in ctx.get("series", [])
        if (sr.get("derivation") or {}).get("method")]

    # what the data could not answer — stated by the computation, never papered over
    how["gaps"] = [
        {"label": sr.get("label") or sr.get("id"),
         "note": (sr.get("provenance") or {}).get("note", "")}
        for sr in ctx.get("series", []) if sr.get("evidence_class") == "unavailable"]

    # the pins, aged as of now (see _pin_freshness)
    how["pins"] = [
        {"dataset": ds, "snapshot": snap,
         "link": f"/documents#path=docs/project/corpus/{ds}/README.md",
         **_pin_freshness(repo_root, ds, snap)}
        for ds, snap in (ed.get("pins") or {}).items()]

    # full assumption records — method, confidence, and what would retire them
    assumptions = []
    for chip in ctx.get("assumption_chips", []):
        hits = list((repo_root / "docs" / "project" / "corpus").glob(f"*/*/assumptions/{chip['id']}.yml"))
        rec = _read_yaml(hits[0]) if hits else None
        assumptions.append({"id": chip["id"], "link": chip.get("link"), "rec": rec or {}})
    how["assumptions"] = assumptions

    # ── the payload: everything a reader can push back on ────────────────────
    ch = []
    for e in ctx.get("expectations", []):
        if not e.get("validated"):
            ch.append({"kind": "Threshold", "cls": "vx-risk",
                       "what": f"{e.get('id')} — {e.get('statement')} (expected {e.get('expected')}) "
                               f"is a stand-in: {e.get('basis')}",
                       "action": "Ratify the threshold in the plan of record, mark the expectation "
                                 "validated in the catalog, then re-answer."})
    for a in assumptions:
        r = a["rec"]
        ch.append({"kind": "Assumption", "cls": "ev-assumed", "link": a.get("link"),
                   "what": f"{a['id']} — {r.get('title', 'stated assumption')}"
                           + (f" ({r.get('value_or_range')})" if r.get("value_or_range") else "")
                           + f". {r.get('estimation_method', '')} Confidence: {r.get('confidence', '?')}.",
                   "action": r.get("refresh_trigger")
                             or "Acquire the underlying data and replace the assumption."})
    for g in how["gaps"]:
        note = g["note"][:1].upper() + g["note"][1:] if g["note"] else ""
        ch.append({"kind": "Missing data", "cls": "ev-unavailable",
                   "what": f"{g['label']} could not be computed. {note}",
                   "action": "Acquire the named data as a corpus dataset; the cut appears on the next answer."})
    for pin in how["pins"]:
        if pin["band"] in ("aging", "stale"):
            ch.append({"kind": "Freshness", "cls": "fr-" + pin["band"],
                       "what": f"{pin['dataset']}@{pin['snapshot']} is {pin['band']}"
                               + (f" ({pin['age']}d against a {pin['max_age']}d limit)" if pin.get("age") is not None else "")
                               + " — the answer describes the world as of that snapshot.",
                       "action": "Refresh the dataset and re-answer, or file a freshness waiver with an owner and expiry."})
    if ctx.get("plan_status") and ctx["plan_status"]["cls"] != "vx-met":
        ch.append({"kind": "Plan", "cls": "vx-risk",
                   "what": f"The analysis plan is {ctx['plan_status']['label'].lower()}.",
                   "action": "Re-answer so the edition pins the current plan."})
    how["challenges"] = ch
    return how


def _split_verdict(text: str):
    """A verdict headline is assembled by the computations as `"; ".join(parts)` — one
    long string of clauses. Typeset it as a LEAD + supporting points so the most
    important sentence on the page can be read at a glance. Characters are never
    altered, only line-broken, so the page and the exported document carry the
    identical claim. Semicolons inside (parens) or [brackets] are not split points;
    fewer than three clauses stays a single paragraph (a list of two reads worse)."""
    depth, parts, buf = 0, [], []
    for ch in text or "":
        if ch in "([":
            depth += 1
        elif ch in ")]":
            depth = max(0, depth - 1)
        if ch == ";" and depth == 0:
            parts.append("".join(buf).strip()); buf = []
        else:
            buf.append(ch)
    parts.append("".join(buf).strip())
    parts = [p for p in parts if p]
    if len(parts) < 3:
        return (text or "").strip(), []
    return parts[0], parts[1:]


# Header status is EXCEPTION-ONLY: the expected states (measured/derived evidence,
# fresh pins) say nothing a reader can act on, and rendering them permanently turns
# real signals into wallpaper. Only these values surface in the title block; the full
# picture always lives on the Quality & audit tab.
NOTEWORTHY_EVIDENCE = {"assumed", "unavailable"}
NOTEWORTHY_FRESHNESS = {"aging", "stale"}


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

# --- Computation-code quality layer (sidecar schema 1.2 `code` per question row).
# SOFT GATE: badges only — nothing here blocks approval or rendering. Rows
# without the field (schema ≤1.1) degrade to an honest empty state.

CODE_STATUS_META = {
    "reviewed-current": {"label": "Reviewed — current", "glyph": "✓", "cls": "vx-met"},
    "review-outdated": {"label": "Review outdated", "glyph": "⟳", "cls": "vx-risk"},
    "unreviewed": {"label": "Unreviewed", "glyph": "○", "cls": "vx-none"},
    "checks-failed": {"label": "Checks failed", "glyph": "✗", "cls": "vx-notmet"},
}

# pass = ok tone, fail = danger, n/a = muted — icon + label, never color alone
CODE_CHECK_META = {
    "pass": {"glyph": "✓", "cls": "vx-met"},
    "fail": {"glyph": "✗", "cls": "vx-notmet"},
    "n/a": {"glyph": "—", "cls": "vx-none"},
}

CODE_ROLE_META = {
    "computation": {"glyph": "ƒ", "label": "Computation — produces this answer's figures"},
    "shared": {"glyph": "⧉", "label": "Shared module — used by several computations"},
    "generator": {"glyph": "⚙", "label": "Generator — emits report/sidecar structure"},
}

CODE_CHECKS = (("static_lint", "lint"), ("poison_scan", "poison scan"),
               ("determinism", "determinism"))

# Review verdict → chip class (code reviews + superseded history entries).
REVIEW_VERDICT_CLS = {
    "APPROVED": "vx-met",
    "APPROVED-WITH-FINDINGS": "vx-risk",
    "CHANGES-REQUIRED": "vx-notmet",
}


def _inline_md_ref(ref) -> str | None:
    """A detail_ref the console may render INLINE: a repo-relative markdown
    path (never a URL, never absolute). Anything else → None (external link
    affordance only)."""
    if isinstance(ref, str) and ref and ref.endswith(".md") \
            and not ref.startswith(("http://", "https://", "/")) \
            and ".." not in Path(ref).parts:
        return ref
    return None


def _decorate_code(q: dict) -> dict | None:
    """Normalize a question row's schema-1.2/1.3 `code` block for the Quality
    tab's Computation code panel. Absent/malformed → None (the panel renders its
    empty state); rows without `review_history` (schema ≤1.2) degrade to no
    history chrome. The console renders the audit verbatim — it never re-runs a
    check or re-derives a status."""
    raw = q.get("code")
    if not isinstance(raw, dict):
        return None
    arts = []
    for a in raw.get("artifacts") or []:
        if not isinstance(a, dict):
            continue
        d = dict(a)
        d["_role"] = CODE_ROLE_META.get(a.get("role") or "", CODE_ROLE_META["computation"])

        def _status(key):
            # engine emits either a bare string or a structured {status, ...} object
            v = a.get(key, "n/a")
            if isinstance(v, dict):
                v = v.get("status", "n/a")
            return v if v in CODE_CHECK_META else "n/a"

        d["_checks"] = [{"name": name, "value": _status(key),
                         **CODE_CHECK_META[_status(key)]}
                        for key, name in CODE_CHECKS]
        review = a.get("review") if isinstance(a.get("review"), dict) else None
        d["review"] = review
        # soft-gate badge per artifact: deterministic fail > review outdated > unreviewed
        if any(_status(k) == "fail" for k, _ in CODE_CHECKS):
            d["_badge"] = CODE_STATUS_META["checks-failed"]
        elif review is None:
            d["_badge"] = CODE_STATUS_META["unreviewed"]
        elif not review.get("current", False):
            d["_badge"] = CODE_STATUS_META["review-outdated"]
        else:
            d["_badge"] = None  # reviewed + current — the verdict chip carries it
        if review:
            d["_review_cls"] = "vx-met" if review.get("current") else "vx-risk"
            ref = review.get("detail_ref")
            if isinstance(ref, str) and ref and not ref.startswith(("http://", "https://", "/")):
                d["_detail_link"] = f"/documents#path={ref}"
            d["_detail_md"] = _inline_md_ref(ref)
            findings = []
            for f in review.get("findings") or []:
                if isinstance(f, dict):
                    f = dict(f)
                    f["_sev"] = SEV_META.get(f.get("severity", "medium"), SEV_META["medium"])
                    findings.append(f)
            d["_findings"] = findings
        # schema 1.3: reviews filed against superseded shas of the same file —
        # the original (pre-fix) findings stay inspectable in place. Absent
        # (schema ≤1.2) or malformed → no history chrome, zero errors.
        history = []
        for h in a.get("review_history") or []:
            if not isinstance(h, dict) or not h.get("verdict"):
                continue
            h = dict(h)
            h["_cls"] = REVIEW_VERDICT_CLS.get(str(h.get("verdict", "")).upper(), "vx-none")
            hf = []
            for f in h.get("findings") or []:
                if isinstance(f, dict):
                    f = dict(f)
                    f["_sev"] = SEV_META.get(f.get("severity", "medium"), SEV_META["medium"])
                    hf.append(f)
            h["_findings"] = hf
            ref = h.get("detail_ref")
            if isinstance(ref, str) and ref and not ref.startswith(("http://", "https://", "/")):
                h["_detail_link"] = f"/documents#path={ref}"
            h["_detail_md"] = _inline_md_ref(ref)
            history.append(h)
        d["_history"] = history
        arts.append(d)
    return {
        "status": raw.get("status"),
        "_status": CODE_STATUS_META.get(raw.get("status") or "", CODE_STATUS_META["unreviewed"]),
        "artifacts": arts,
    }

# --- Verification-plan checklist (sidecar schema 1.4 `verification_plan` per
# question row). The plan DECLARES the gates; done-marks are COMPUTED by the
# engine from the edition's actual records — the console renders them verbatim
# and never re-derives a mark. Marks: ✓ done / ○ not done / • informational
# (custom or not-computable). Rows without the field (schema ≤1.3) → None.

VP_MARK_META = {
    True: {"glyph": "✓", "cls": "vx-met", "label": "Done — computed from this edition's records"},
    False: {"glyph": "○", "cls": "vx-risk", "label": "Not done yet — computed from this edition's records"},
    None: {"glyph": "•", "cls": "vx-none", "label": "Informational — completion not machine-computed"},
}


def _decorate_vplan(q: dict) -> dict | None:
    """Normalize a question row's schema-1.4 `verification_plan` list for the
    Plan tab checklist + the Quality-tab header chip. Absent/malformed → None
    (no chip, no checklist — schema ≤1.3 degrades cleanly)."""
    raw = q.get("verification_plan")
    if not isinstance(raw, list):
        return None
    gates, met, total = [], 0, 0
    for g in raw:
        if not isinstance(g, dict) or not g.get("gate"):
            continue
        d = dict(g)
        done = d.get("done") if isinstance(d.get("done"), bool) else None
        d["_mark"] = VP_MARK_META[done]
        if done is not None:
            total += 1
            met += 1 if done else 0
        gates.append(d)
    if not gates:
        return None
    return {"gates": gates, "met": met, "total": total,
            "_cls": "vx-met" if total and met == total else "vx-risk"}


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
    # A null y is a GAP ("no observation this period" — e.g. no lots at a station
    # that month), never a zero: it keeps its x slot on the axis but draws nothing.
    all_pts = [(p["x"], p.get("y")) for ln in lines for p in ln.get("points", [])]
    if not all_pts:
        return None
    xs = sorted({x for x, _ in all_pts})
    xi = {x: i for i, x in enumerate(xs)}
    ymax = max((y for _, y in all_pts if y is not None), default=0) or 1
    # no right-side series end-labels (the bottom legend carries series identity)
    # — the full right margin belongs to the data
    W, H, L, R, T, B = 560, 180, 12, 14, 12, 24
    span = max(1, len(xs) - 1)

    def X(x):
        return L + (W - L - R) * (xi[x] / span)

    def Y(y):
        return T + (H - T - B) * (1 - y / ymax)

    glines = []
    for i, ln in enumerate(lines):
        pts = sorted((p for p in ln.get("points", []) if p.get("y") is not None),
                     key=lambda p: p["x"])
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
        })
    _place_point_labels(glines, spacing=(W - L - R) / span, w=W, h=H, left=L,
                        right=R, bottom=B, ymax_y=round(Y(ymax), 1), ymax=ymax)
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


def _text_w(s, size: float) -> float:
    """Rough SVG text width estimate at viewbox scale (avg glyph ≈ 0.62em)."""
    return len(str(s)) * size * 0.62 + 3


VLABEL_FS = 8.5  # value-label font size at viewbox scale — subordinate to 10px axis ticks


def _place_point_labels(glines: list, spacing: float, w: int, h: int, left: int,
                        right: int, bottom: int, ymax_y: float, ymax) -> None:
    """Direct value labels on timeseries points (dataviz: direct labels beat
    hover-only), placed by ONE global collision pass across all lines.

    Candidate selection — conservative as line count grows:
      ≤2 lines, ≥60px point spacing → every point;
      ≤2 lines, denser            → endpoints + min/max per line;
      ≥3 lines                    → last point per line + global min/max only.
    Priority when two candidates want the same space: line-endpoint value (3)
    > min/max extremum (2) > interior value (1); one label per point (dedupe
    by keeping the highest priority). Placement tries above the point, flips
    below when a neighboring point crowds the space above, clamps inside the
    viewbox, and DROPS the label rather than overlap — the hover tooltip
    always carries the number. The three axis tick labels are pre-seeded as
    occupied boxes so value labels never sit on them."""
    dense_ok = len(glines) <= 2 and spacing >= 60
    sel: dict[tuple[int, int], int] = {}

    def bump(key, pr):
        sel[key] = max(sel.get(key, 0), pr)

    if len(glines) >= 3:
        flat = [(gi, pi, p["v"]) for gi, g in enumerate(glines)
                for pi, p in enumerate(g["_pts"])]
        for gi, g in enumerate(glines):
            bump((gi, len(g["_pts"]) - 1), 3)
        if flat:
            gmax = max(flat, key=lambda t: t[2])
            gmin = min(flat, key=lambda t: t[2])
            bump((gmax[0], gmax[1]), 2)
            bump((gmin[0], gmin[1]), 2)
    else:
        for gi, g in enumerate(glines):
            pp = g["_pts"]
            vals = [p["v"] for p in pp]
            if dense_ok:
                for pi in range(len(pp)):
                    bump((gi, pi), 1)
            bump((gi, vals.index(max(vals))), 2)
            bump((gi, vals.index(min(vals))), 2)
            bump((gi, 0), 3)
            bump((gi, len(pp) - 1), 3)

    # occupied boxes, seeded with the three axis tick labels (10px font)
    boxes = [
        (left, h - 16.0, left + _text_w("0000-00-00", 10), float(h)),      # x0 tick
        (w - right - _text_w("0000-00-00", 10), h - 16.0, float(w - right), float(h)),  # x1 tick
        (float(left), ymax_y - 13.0, left + _text_w(ymax, 10), ymax_y),    # ymax tick
    ]

    def collides(b):
        return any(b[0] < o[2] + 2 and b[2] > o[0] - 2 and
                   b[1] < o[3] + 2 and b[3] > o[1] - 2 for o in boxes)

    for g in glines:
        g["labels"] = []
    # highest priority places first; ties resolve left-to-right
    order = sorted(sel.items(),
                   key=lambda kv: (-kv[1], glines[kv[0][0]]["_pts"][kv[0][1]]["cx"]))
    for (gi, pi), _pr in order:
        pp = glines[gi]["_pts"]
        p = pp[pi]
        text = _fmt_point(p["v"])
        tw = _text_w(text, VLABEL_FS)
        # clamp horizontally inside the viewbox — never clip at an edge
        x = max(tw / 2 + 2, min(p["cx"], w - tw / 2 - 2))
        # a neighboring point noticeably higher on screen means the line slopes
        # through the space above this point — prefer below
        crowded_above = any(0 <= k < len(pp) and pp[k]["cy"] < p["cy"] - 12
                            for k in (pi - 1, pi + 1))
        above, below = p["cy"] - 7, p["cy"] + 15
        placed = None
        for cy in ((below, above) if crowded_above else (above, below)):
            y = min(max(cy, 9.0), h - bottom + 8.0)  # clamp inside viewbox / off ticks
            b = (x - tw / 2, y - VLABEL_FS, x + tw / 2, y + 2)
            if not collides(b):
                placed = (x, y, b)
                break
        if placed is None:
            continue  # drop rather than overlap — hover carries the number
        boxes.append(placed[2])
        glines[gi]["labels"].append({"x": round(placed[0], 1),
                                     "y": round(placed[1], 1), "v": text})


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
            # a null measure is a gap (no plan row / no observation), never a zero
            mx = max((max(abs(p.get("a") or 0), abs(p.get("b") or 0)) for p in pts), default=0) or 1
            d["_paired"] = {
                "a_label": pairs.get("a_label", "actual"),
                "b_label": pairs.get("b_label", "plan"),
                "rows": [{"label": p.get("label", ""),
                          "a": p.get("a", 0), "b": p.get("b", 0),
                          "a_pct": round(100.0 * abs(p.get("a") or 0) / mx, 1),
                          "b_pct": round(100.0 * abs(p.get("b") or 0) / mx, 1),
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

    def __init__(self, repo_root: Path, bq: str, edition: str | None, domain: str = "commercial"):
        self.repo_root = repo_root
        self.domain = domain
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
            href = f"/domains/{self.domain}/{self.bq}/raw" + (f"?edition={self.edition}" if self.edition else "")
            return {"kind": "Computed series", "label": value, "href": href,
                    "detail": "deterministic computation output in this edition's data.json"}
        # config
        rel = value if value.startswith("docs/") else f"docs/project/{self.domain}/{value}"
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


@router.get("/domains/{domain}", response_class=HTMLResponse)
async def commercial_index(domain: str, request: Request, render_error: str | None = None):
    cfg = get_config()
    index = load_index(cfg.repo_root, domain)
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
         "has_skill": has_skill, "render_error": render_error, **_domain_ctx(cfg, domain)},
    )


@router.get("/domains/{domain}/catalog/grounding", response_class=PlainTextResponse)
async def catalog_grounding(domain: str, ):
    """Compact rendition of the whole question board for the catalog's assistant
    drawer. Declared before /commercial/{bq}/grounding so it wins the match."""
    cfg = get_config()
    index = load_index(cfg.repo_root, domain) or {}
    dm = domain_meta(cfg.repo_root, domain)
    lines = [f"# {dm['name']} question board — status roll-up",
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


@router.get("/domains/{domain}/review-detail", response_class=HTMLResponse)
async def commercial_review_detail(domain: str, path: str = ""):
    """Render a repo-relative markdown dossier (review / verification
    detail_ref) to an HTML fragment for in-place expansion on the Quality tab.
    Lazy-loaded by the template's dossier folds; cached client-side.

    SECURITY — strict resolution: the path must be repo-relative, resolve
    strictly INSIDE the repo root, and name an existing `.md` file. Absolute
    paths, `..` traversal, and non-markdown files are rejected (403/404).
    Declared before /commercial/{bq} so the literal segment wins the match."""
    cfg = get_config()
    rel = (path or "").strip()
    if not rel or rel.startswith(("/", "\\")) or "\\" in rel or ":" in rel.split("/", 1)[0]:
        raise HTTPException(403, "path must be repo-relative")
    if ".." in Path(rel).parts:
        raise HTTPException(403, "path traversal rejected")
    if not rel.endswith(".md"):
        raise HTTPException(403, "only markdown dossiers render inline")
    repo = cfg.repo_root.resolve()
    target = (repo / rel).resolve()
    try:
        target.relative_to(repo)
    except ValueError:
        raise HTTPException(403, "path escapes the repo root")
    if not target.is_file():
        raise HTTPException(404, f"no such dossier: {rel}")
    try:
        html = doc_renderer.render(target).body_html or ""
    except Exception:
        raise HTTPException(500, "dossier failed to render")
    return HTMLResponse(html)


# ---------------------------------------------------------------- narrative layer
# The narrative is prose AROUND the computed results — an executive summary plus a
# "What this tells us" per report section — stored by the ENGINE as
# reports/<BQ>/<edition>/narrative.md, hash-pinned to the report/data bytes it
# explains and held to the same claim lint as the report. The console synthesizes
# it (grounded on report.md + data.json only), hands it to the engine to stamp and
# lint, and renders it; it never edits figures.

_NARR_FM_RE = re.compile(r"\A---\n(.*?)\n---\n", re.S)
_NARR_H2_RE = re.compile(r"^## (.+?)\s*$", re.M)
_HTML_H2_RE = re.compile(r"<h2[^>]*>(.*?)</h2>", re.S)
_TAG_RE = re.compile(r"<[^>]+>")

def _parse_narrative(text: str):
    fm, body = {}, text
    m = _NARR_FM_RE.match(text)
    if m:
        fm = _read_yaml_text(m.group(1)) or {}
        body = text[m.end():]
    heads = list(_NARR_H2_RE.finditer(body))
    sections = {}
    for i, h in enumerate(heads):
        end = heads[i + 1].start() if i + 1 < len(heads) else len(body)
        sections[h.group(1).strip()] = body[h.end():end].strip()
    return fm, sections


def _read_yaml_text(text: str):
    try:
        import yaml
        return yaml.safe_load(text)
    except Exception:
        return None


def _md_to_html(text: str) -> str:
    return _md_lib.markdown(text, extensions=["tables", "sane_lists"])


# Section placement for charts — MIRRORS the engine's `place_series` (commercial.py)
# so the Full Report tab and the exported document put every figure in the same
# section: explicit `section:` → first DATA section citing `[derived: <id>]` → token
# overlap with a data heading → unplaced (rendered as an Overview block up front).
_NON_DATA_HEADS = ("method & provenance", "assumptions & expectations", "narrative")
_STOP = {"by", "vs", "and", "the", "of", "per", "a", "in", "to", "on", "for", "with", "an", "or"}


def _place_series(report_md: str, series: list):
    heads = list(_NARR_H2_RE.finditer(report_md))
    secs = []
    for i, h in enumerate(heads):
        end = heads[i + 1].start() if i + 1 < len(heads) else len(report_md)
        secs.append((h.group(1).strip(), report_md[h.end():end]))
    placed = {h: [] for h, _ in secs}
    extra = []
    lower = {h.lower(): h for h, _ in secs}
    for sr in series:
        sid = sr.get("id", "")
        target = None
        exp = (sr.get("section") or "").strip().lower()
        if exp and exp in lower:
            target = lower[exp]
        if target is None:
            for h, body in secs:
                if h.lower().startswith(_NON_DATA_HEADS):
                    continue
                if f"[derived: {sid}]" in body:
                    target = h
                    break
        if target is None:
            toks = set(re.findall(r"[a-z0-9]+", (sid + " " + str(sr.get("label", ""))).lower())) - _STOP
            best = (0, None)
            for h, _ in secs:
                if h.lower().startswith(_NON_DATA_HEADS):
                    continue
                ov = len(toks & (set(re.findall(r"[a-z0-9]+", h.lower())) - _STOP))
                if ov > best[0]:
                    best = (ov, h)
            if best[1] and (best[0] >= 2 or (best[0] == 1 and len(toks) <= 3)):
                target = best[1]
        (extra if target is None else placed[target]).append(sr)
    return placed, extra


def _chart_html(s: dict) -> str:
    """Render one decorated series through the shared chart macro (no explainer
    button in document context — the Visualization tab carries those)."""
    return templates.env.get_template("_cm_chart.html").module.chart(s, "", True)


def _narrative_ctx(cfg, repo_root: Path, ed: dict, refbook, report_html: str, domain: str,
                   series: list | None = None) -> dict:
    """Read narrative.md (if any) -> executive-summary HTML, staleness, and the Full
    Report HTML: the report with each section's charts placed after its table(s)
    and a "What this tells us" fold appended; headline charts no section cites go
    into an Overview block ahead of the first section."""
    from console.commercial.loader import _root as _domain_root
    edir = _domain_root(repo_root, domain) / "reports" / ed["bq"] / ed["edition"]
    np = edir / "narrative.md"
    out = {"narrative_status": "missing", "exec_summary_html": "", "narr_meta": {},
           "report_html_narrated": report_html, "narr_sections_used": 0, "overview_html": ""}
    fm, sections, stale = {}, {}, False
    if np.is_file():
        fm, sections = _parse_narrative(np.read_text(encoding="utf-8"))
    import hashlib

    def _sha(p):
        return hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None
    if np.is_file():
        stale = fm.get("report_sha256") != _sha(edir / "report.md") or fm.get("data_sha256") != _sha(edir / "data.json")
        out["narrative_status"] = "stale" if stale else "present"
        out["narr_meta"] = {"generated_at": fm.get("generated_at"), "author": fm.get("author")}
    by_key = {k.lower(): v for k, v in sections.items()}
    es = by_key.pop("executive summary", None)
    if es:
        out["exec_summary_html"] = refbook.referencize_html(_md_to_html(es))
    # charts by section (same rule as the engine's export)
    report_md = (edir / "report.md").read_text(encoding="utf-8") if (edir / "report.md").is_file() else ""
    placed, extra = _place_series(report_md, series or [])
    placed_l = {k.lower(): v for k, v in placed.items()}
    if extra:
        out["overview_html"] = '<div class="cm-fr-charts">' + "".join(_chart_html(s) for s in extra) + "</div>"
    # per section: heading + body (tables) + its charts + the narrative fold
    parts = _HTML_H2_RE.split(report_html)  # [pre, h1text, body1, h2text, body2, ...]
    if len(parts) > 1:
        rebuilt = [parts[0]]
        for i in range(1, len(parts), 2):
            head_html, body = parts[i], parts[i + 1] if i + 1 < len(parts) else ""
            key = _html.unescape(_TAG_RE.sub("", head_html)).strip().lower()
            rebuilt.append(f"<h2>{head_html}</h2>{body}")
            figs = placed_l.get(key) or []
            if figs:
                rebuilt.append('<div class="cm-fr-charts">' + "".join(_chart_html(s) for s in figs) + "</div>")
            n = by_key.get(key)
            if n:
                out["narr_sections_used"] += 1
                rebuilt.append(
                    '<details class="cm-narr" open><summary><span class="cm-narr-k">What this tells us</span>'
                    + ('<span class="cm-narr-stale" title="written against an earlier version of the figures">stale</span>' if stale else '')
                    + '</summary><div class="cm-narr-body md-body">'
                    + refbook.referencize_html(_md_to_html(n)) + '</div></details>')
        out["report_html_narrated"] = "".join(rebuilt)
    return out


@router.post("/domains/{domain}/{bq}/narrative")
async def commercial_narrative(domain: str, request: Request, bq: str):
    """Regenerate the edition's narrative on demand (every `answer` already writes
    one automatically). Delegates to the engine's `narrative-generate`; the file is
    kept even if the lint-guided retry still has errors — the UI shows them."""
    cfg = get_config()
    form = await request.form()
    edition = str(form.get("edition") or "").strip()
    q = question_row(cfg.repo_root, bq, domain)
    ed = load_edition(cfg.repo_root, bq, edition, domain) if (q and edition) else None
    if ed is None:
        raise HTTPException(404, f"No edition '{edition}' for {bq}.")
    script = skill_render_script(cfg.repo_root)
    back = f"/domains/{domain}/{bq}?edition={quote(edition, safe='')}"
    if script is None:
        return RedirectResponse(back + "&narr_error=" + quote("commercial skill not installed", safe=""), status_code=303)
    # One implementation: the engine's `narrative-generate` (claude CLI synthesis →
    # stamp → lint with a lint-guided retry). The console just invokes it — the same
    # path `answer` takes automatically for every new or refreshed edition.
    import anyio
    rc, out = await anyio.to_thread.run_sync(
        lambda: _run([sys.executable, str(script), "--domain", domain, "narrative-generate", bq,
                      "--edition", edition, "--force"], cfg.repo_root, 900))
    errors = [ln.strip()[len("ERROR"):].strip() for ln in out.splitlines() if ln.strip().startswith("ERROR")]
    if rc != 0 and not errors:
        return RedirectResponse(back + "&narr_error=" + quote(out[-800:], safe=""), status_code=303)
    _run([sys.executable, str(script), "--domain", domain, "render"], cfg.repo_root)
    if errors:
        return RedirectResponse(back + "&narr_error=" + quote("narrative saved but the claim lint still reports: " + " | ".join(errors)[:1200], safe=""), status_code=303)
    return RedirectResponse(back + "&narr_ok=1", status_code=303)


_EXPORT_MEDIA = {"md": "text/markdown", "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                 "pdf": "application/pdf"}


@router.get("/domains/{domain}/{bq}/export")
async def commercial_export(domain: str, bq: str, edition: str | None = None, format: str = "docx"):
    """Assemble and download the formal document via the engine's `export`."""
    cfg = get_config()
    if format not in _EXPORT_MEDIA:
        raise HTTPException(400, "format must be md, docx or pdf")
    q = question_row(cfg.repo_root, bq, domain)
    if q is None:
        raise HTTPException(404, f"Unknown question '{bq}'.")
    show_id = edition or q.get("latest_edition") or q.get("approved_edition")
    ed = load_edition(cfg.repo_root, bq, show_id, domain) if show_id else None
    if ed is None:
        raise HTTPException(404, f"No edition for {bq}.")
    script = skill_render_script(cfg.repo_root)
    if script is None:
        raise HTTPException(503, "commercial skill not installed")
    rc, out = _run([sys.executable, str(script), "--domain", domain, "export", bq, "--edition", ed["edition"],
                    "--format", format, "--print-path"], cfg.repo_root, timeout=300)
    if rc != 0:
        raise HTTPException(502, f"export failed: {out[-800:]}")
    path = Path(out.strip().splitlines()[-1])
    if not path.is_absolute():
        path = cfg.repo_root / path
    if not path.is_file():
        raise HTTPException(502, "export produced no file")
    return FileResponse(str(path), media_type=_EXPORT_MEDIA[format], filename=path.name)


@router.get("/domains/{domain}/{bq}", response_class=HTMLResponse)
async def commercial_view(domain: str, request: Request, bq: str, edition: str | None = None):
    cfg = get_config()
    q = question_row(cfg.repo_root, bq, domain)
    if q is None:
        raise HTTPException(404, f"Unknown question '{bq}'. Run the engine's `render --domain {domain}` to refresh the sidecar.")
    q = _decorate_row(dict(q))
    # default: the NEWEST edition (draft included, clearly watermarked) — reviewers see
    # the latest work; the approved record is one click away in the editions rail
    show_id = edition or q.get("latest_edition") or q.get("approved_edition") or q.get("draft_edition")
    ed = load_edition(cfg.repo_root, bq, show_id, domain) if show_id else None
    if ed is None and show_id:
        raise HTTPException(404, f"No edition '{show_id}' for {bq}.")
    ctx = {"config": cfg, "q": q, "ed": ed, "series": [], "verdicts": [], **_domain_ctx(cfg, domain),
           "report_html": "", "editions": q.get("editions", []),
           "ed_meta": None, "EDITION_META": EDITION_META,
           "expectations": [], "narrative": None, "newer_draft": None,
           "narrative_status": "missing", "exec_summary_html": "", "narr_meta": {},
           "tab_attention": {}, "head_status": [], "how": None,
           "narr_error": request.query_params.get("narr_error"), "narr_ok": request.query_params.get("narr_ok"),
           "references": [], "quality": None, "code": _decorate_code(q),
           "vplan": _decorate_vplan(q),
           "tables": [], "unstructured": [],
           "explainers": _explainers_for(q, []), "terms": _terms_for(q),
           "kind_glossary": KIND_GLOSSARY,
           "explain_json": {}, "team": team_names(cfg.repo_root),
           "approved_qp": request.query_params.get("approved"),
           "pr_url": request.query_params.get("pr"),
           "approve_error": request.query_params.get("approve_error"),
           "push_error": request.query_params.get("push_error")}
    if ed:
        refbook = RefBook(cfg.repo_root, bq, ed["edition"], domain)
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
        ctx["verdicts"] = [dict(v) for v in ed["data"].get("verdicts", [])]
        for v in ctx["verdicts"]:
            v["_lead"], v["_points"] = _split_verdict(v.get("headline", ""))
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
                    v["_detail_md"] = _inline_md_ref(v.get("detail_ref"))
        ctx["quality"] = quality
        # Data tab: structured tables + unstructured artifact inventory
        ctx["tables"] = _build_tables(cfg.repo_root, ed)
        ctx["unstructured"] = _build_unstructured(cfg.repo_root, ed)
        # Plan tab: user-owned analysis contract, rendered; status from quality.json
        PLAN_META = {"in-sync": {"label": "In sync — edition computed under this plan", "cls": "vx-met"},
                     "drifted": {"label": "Plan changed since this edition — review intent, re-answer", "cls": "vx-risk"},
                     "unpinned": {"label": "Edition predates plan pinning — re-answer to pin", "cls": "vx-risk"},
                     "missing": {"label": "No plan yet — scaffold with plan-init", "cls": "vx-notmet"}}
        plan_file = cfg.repo_root / "docs" / "project" / domain / "plans" / f"{bq}.md"
        ctx["plan_html"] = ""
        ctx["plan_status"] = None
        ctx["plan_path"] = f"docs/project/{domain}/plans/{bq}.md"
        if plan_file.is_file():
            try:
                ctx["plan_html"] = doc_renderer.render(plan_file).body_html or ""
            except Exception:
                ctx["plan_html"] = ""
        pstatus = (quality or {}).get("plan") or {}
        ctx["plan_status"] = PLAN_META.get(pstatus.get("status"),
                                           PLAN_META["missing"] if not plan_file.is_file() else None)
        # ── Title-block status + tab dots, both exception-only ────────────────
        # The edition's draft/approved state is NOT repeated here: the editions rail
        # names it and the chart area is watermarked. Evidence class and pin freshness
        # appear only at their noteworthy values, so a marker in the header always
        # means "read this", never "everything is normal".
        head = []
        if (q.get("evidence_class") or "") in NOTEWORTHY_EVIDENCE and q.get("_evidence"):
            head.append({"cls": q["_evidence"]["cls"], "label": q["_evidence"]["label"],
                         "tip": q["_evidence"]["tip"]})
        if (q.get("freshness") or "") in NOTEWORTHY_FRESHNESS and q.get("_fresh"):
            head.append({"cls": q["_fresh"]["cls"], "label": q["_fresh"]["label"],
                         "tip": q["_fresh"]["tip"]})
        ctx["head_status"] = head
        # A tab dot marks a tab whose contents need attention — no counts, no chips:
        # the detail is one click away, and a clean tab row is the common case.
        lint_bad = bool(quality and (quality.get("lint", {}).get("errors")
                                     or quality.get("lint", {}).get("status") not in (None, "pass")))
        code_bad = bool(ctx.get("code") and ctx["code"]["_status"]["cls"] == "vx-notmet")
        plan_bad = bool(ctx["plan_status"] and ctx["plan_status"]["cls"] != "vx-met")
        ctx["tab_attention"] = {
            "quality": lint_bad or code_bad,
            "quality_why": "The claim lint or the code audit reports a failure"
                           if (lint_bad or code_bad) else "",
            "plan": plan_bad,
            "plan_why": (ctx["plan_status"]["label"] if plan_bad else ""),
        }
        abs_report = cfg.repo_root / ed["report_path"]
        if abs_report.is_file():
            try:
                rendered = doc_renderer.render(abs_report)
                html = _doc_link_rewriter(ed["report_path"])(rendered.body_html or "")
                # formal-document reference layer: markers -> superscript numbers
                ctx["report_html"] = refbook.referencize_html(html)
            except Exception:
                ctx["report_html"] = ""
        ctx.update(_narrative_ctx(cfg, cfg.repo_root, ed, refbook, ctx["report_html"], domain, ctx["series"]))
        ctx["report_html"] = ctx.pop("report_html_narrated")
        ctx["references"] = refbook.refs
        # assumption chips → open the record in the Documents viewer when possible
        chips = []
        for aid in q.get("assumptions", []):
            hits = list((cfg.repo_root / "docs" / "project" / "corpus").glob(f"*/*/assumptions/{aid}.yml"))
            link = f"/documents#path={hits[0].relative_to(cfg.repo_root)}" if hits else None
            chips.append({"id": aid, "link": link})
        ctx["assumption_chips"] = chips
        ctx["how"] = _how_ctx(cfg.repo_root, q, ed, ctx, domain)
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


@router.get("/domains/{domain}/{bq}/data", response_class=HTMLResponse)
async def commercial_data(domain: str, request: Request, bq: str, edition: str | None = None):
    """Dedicated tabular view (deep-linkable twin of the answer's Data tab)."""
    cfg = get_config()
    q = question_row(cfg.repo_root, bq, domain)
    if q is None:
        raise HTTPException(404, f"Unknown question '{bq}'.")
    show_id = edition or q.get("latest_edition") or q.get("approved_edition")
    ed = load_edition(cfg.repo_root, bq, show_id, domain) if show_id else None
    if ed is None:
        raise HTTPException(404, f"No edition for {bq} — nothing to tabulate.")
    return templates.TemplateResponse(
        request, "commercial_data.html",
        {"config": cfg, "q": q, "ed": ed, "tables": _build_tables(cfg.repo_root, ed),
         **_domain_ctx(cfg, domain)},
    )


def _run(cmd: list, cwd: Path, timeout: int = 120):
    try:
        p = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, timeout=timeout)
        return p.returncode, (p.stdout or "") + (p.stderr or "")
    except subprocess.TimeoutExpired:
        return 1, f"timed out: {' '.join(str(c) for c in cmd)}"


def _push_approval(repo_root: Path, bq: str, edition: str, approver: str, domain: str = "commercial"):
    """The project's push sequence for the approved edition: branch -> stage only
    the answer + sidecar paths -> commit -> PR -> auto-merge -> back to main.
    Returns (pr_url or None, error or None). Approval itself already happened —
    a push failure leaves it approved locally and reports honestly."""
    branch = f"console/approve-{bq}-{edition}".replace(" ", "")
    paths = [f"docs/project/{domain}/reports/{bq}", f"docs/project/{domain}/.console"]
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


@router.post("/domains/{domain}/{bq}/approve")
async def commercial_approve(domain: str, request: Request, bq: str):
    """UI approval: run the gated approve (lint + freshness enforced by the skill),
    refresh the sidecar, then push to the repo per the project's git workflow."""
    cfg = get_config()
    form = await request.form()
    edition = str(form.get("edition") or "")
    approver = str(form.get("approver") or "").strip()
    note = str(form.get("verify_note") or "").strip() or "approved via console UI (no independent verification recorded)"
    if not approver:
        return RedirectResponse(f"/domains/{domain}/{bq}?approve_error=" + quote("pick an approver", safe=""), status_code=303)
    script = skill_render_script(cfg.repo_root)
    if script is None:
        return RedirectResponse(f"/domains/{domain}/{bq}?approve_error=" + quote("commercial skill not installed", safe=""), status_code=303)
    rc, out = _run([sys.executable, str(script), "--domain", domain, "approve", bq, "--edition", edition,
                    "--by", approver, "--verify-note", note], cfg.repo_root)
    if rc != 0:
        return RedirectResponse(
            f"/domains/{domain}/{bq}?edition={edition}&approve_error=" + quote(out[-1200:], safe=""), status_code=303)
    _run([sys.executable, str(script), "--domain", domain, "render"], cfg.repo_root)
    pr_url, err = _push_approval(cfg.repo_root, bq, edition, approver, domain)
    q = f"/domains/{domain}/{bq}?approved={quote(edition, safe='')}"
    if pr_url:
        q += "&pr=" + quote(pr_url, safe="")
    if err:
        q += "&push_error=" + quote(err, safe="")
    return RedirectResponse(q, status_code=303)


@router.get("/domains/{domain}/{bq}/raw", response_class=JSONResponse)
async def commercial_raw(domain: str, bq: str, edition: str | None = None):
    cfg = get_config()
    q = question_row(cfg.repo_root, bq, domain)
    if q is None:
        raise HTTPException(404, f"Unknown question '{bq}'.")
    show_id = edition or q.get("approved_edition") or q.get("draft_edition")
    ed = load_edition(cfg.repo_root, bq, show_id, domain) if show_id else None
    if ed is None:
        raise HTTPException(404, f"No edition for {bq}.")
    return JSONResponse(ed["data"])


@router.get("/domains/{domain}/{bq}/grounding", response_class=PlainTextResponse)
async def commercial_grounding(domain: str, bq: str, edition: str | None = None):
    """Compact textual rendition of the shown answer for the Assistant drawer."""
    cfg = get_config()
    q = question_row(cfg.repo_root, bq, domain)
    if q is None:
        raise HTTPException(404, f"Unknown question '{bq}'.")
    show_id = edition or q.get("approved_edition") or q.get("draft_edition")
    ed = load_edition(cfg.repo_root, bq, show_id, domain) if show_id else None
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


@router.post("/domains/{domain}/render")
async def commercial_render(domain: str, ):
    """Shell to the commercial skill's `render` to refresh the sidecar."""
    cfg = get_config()
    script = skill_render_script(cfg.repo_root)
    if script is None:
        return RedirectResponse(
            url=f"/domains/{domain}?render_error=" + quote(
                "The commercial skill is not installed at .claude/skills/commercial/.", safe=""),
            status_code=303,
        )
    try:
        proc = subprocess.run(
            [sys.executable, str(script), "--domain", domain, "render"],
            cwd=str(cfg.repo_root), capture_output=True, text=True, timeout=60,
        )
    except subprocess.TimeoutExpired:
        return RedirectResponse(url=f"/domains/{domain}?render_error=" + quote("render timed out", safe=""),
                                status_code=303)
    if proc.returncode != 0:
        return RedirectResponse(
            url=f"/domains/{domain}?render_error=" + quote(((proc.stdout or "") + (proc.stderr or ""))[:2048], safe=""),
            status_code=303,
        )
    return RedirectResponse(url=f"/domains/{domain}", status_code=303)
