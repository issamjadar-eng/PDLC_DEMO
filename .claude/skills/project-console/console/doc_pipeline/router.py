"""Document Pipeline routes.

GET /doc-pipeline            — the page
GET /doc-pipeline/data.json  — the derived data (debug / machine consumers)
GET /doc-pipeline/grounding  — the same state as plain text, for the drawer

Pure consumer, read-only. There is deliberately **no** refresh endpoint and no
mutation endpoint: every figure is derived live from repo state (15s TTL in the
loader), and producing an artifact is a skill action the user runs in their own
session — the console is a router, the skill is the actor. A "refresh" button
here would imply the console owns data it only reads.
"""
from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse
from fastapi.templating import Jinja2Templates

from console.config import get_config
from console.doc_pipeline.loader import discover, load_pipeline  # noqa: F401

router = APIRouter()
templates = Jinja2Templates(
    directory=str(Path(__file__).parent.parent / "web" / "templates")
)

__all__ = ["router", "discover"]


@router.get("/doc-pipeline", response_class=HTMLResponse)
async def doc_pipeline_page(request: Request):
    cfg = get_config()
    return templates.TemplateResponse(
        request,
        "doc_pipeline.html",
        {"config": cfg, "p": load_pipeline(cfg.repo_root)},
    )


@router.get("/doc-pipeline/data.json", response_class=JSONResponse)
async def doc_pipeline_data():
    return JSONResponse(load_pipeline(get_config().repo_root))


@router.get("/doc-pipeline/grounding", response_class=PlainTextResponse)
async def doc_pipeline_grounding():
    """Pipeline state as plain text for the assistant drawer's `url:` grounding.

    Same derived data as `data.json`, written for a reader rather than a
    parser — the drawer inlines this verbatim into the agent's system prompt,
    and JSON braces would spend that budget on syntax.

    Reuses `load_pipeline` (shared 15s TTL) rather than re-deriving, so an
    advisor answering seconds after a page load is describing the same repo
    state the human is looking at.

    THE CAVEATS TRAVEL WITH THE NUMBERS. An advisor told "437 obligations" with
    no further context will reason about coverage that nobody computed, and one
    told "72 QMS markdown files" will assume a conversion pipeline ran. Both
    qualifiers below are load-bearing, not padding.
    """
    d = load_pipeline(get_config().repo_root)
    L: list[str] = [
        "# Document pipeline state (derived live from the repo)",
        "",
        "Every figure is a count of artifacts present. Presence is not quality: "
        "a document can exist, be counted here, and still be wrong or empty.",
        "",
        "## Authoring",
    ]
    for s in d["authoring"]:
        x = s["data"]
        if not x.get("present"):
            L.append(f"- {s['label']} ({s['owner']}): no artifact yet — produce with `{x.get('hint','')}`")
            continue
        if s["key"] == "input-analysis":
            L.append(f"- Input analysis: {x['total']} docs across "
                     + ", ".join(f"{p['name']} ({p['count']})" for p in x["parts"]))
        elif s["key"] == "strategies":
            L.append(f"- Strategies: {x['live']}/{x['total']} domains live, "
                     f"{x['decisions']} decisions, {x['proposals']} proposed changes")
            if x.get("mixed_formats"):
                L.append("    · counts come from two decision formats (structured blocks "
                         "and legacy prose); prose decisions carry no lifecycle status")
        elif s["key"] == "design-controls":
            L.append(f"- Design controls: {x['dhf_count']} DHFs, {x['total_docs']} docs")
            for r in x["rows"]:
                L.append(f"    · {r['slug']}: {r['roles_present']}/{r['roles_total']} "
                         f"role folders, {r['docs']} docs")
        elif s["key"] == "trace":
            L.append(f"- Trace: {x['traced_items']} traced items across {x['dhf_count']} DHFs, "
                     f"{x['orphans']} orphans")
        elif s["key"] == "obligations":
            L.append(f"- Obligations: {x['projected']} projected from "
                     f"{x['source_obligations']} source obligations "
                     f"(manifest generated {x['generated'] or 'unknown'})")
            L.append(f"    · COVERAGE IS NOT AVAILABLE. It is owned by "
                     f"`{x['coverage_owner']}`, which has "
                     f"{'run' if x['coverage_available'] else 'NOT run'}. Do not infer "
                     f"coverage from the obligation count.")
            if x.get("legacy_schema"):
                L.append("    · this manifest predates the v7 schema; its per-obligation "
                         "status/location fields were retired and are deliberately not read")
        elif s["key"] == "gaps":
            L.append(f"- Gap analysis: {x['total']} analyses "
                     + ", ".join(f"{k}={v}" for k, v in x["by_status"].items()))
        elif s["key"] == "submission":
            L.append(f"- Submission: {len(x['filings'])} filings, {x['blocking']} blocking items")
            for f in x["filings"]:
                L.append(f"    · {f['id']} ({f['type']}): status {f['status']}, "
                         f"{f['required']} required pieces")

    i = d["ingestion"]
    L += ["", "## Ingestion",
          f"- {i['binaries']} binary source files, {i['source_md']} QMS markdown files, "
          f"{i['external']} distilled external references"]
    if i["authored_not_converted"]:
        L.append("- NO document carries `docflow:` conversion provenance. The markdown was "
                 "AUTHORED directly, not converted from binaries — there is no conversion "
                 "ratio, and the QMS markdown must not be described as 'converted'.")
    else:
        L.append(f"- {i['converted']} documents carry `docflow:` conversion provenance")

    p = d["publish"]
    L += ["", "## Regulated publish"]
    if p["present"]:
        L.append(f"- {p['total']} controlled documents, read from {p['source']}: "
                 + ", ".join(f"{k}={v}" for k, v in p["by_state"].items()))
    else:
        L.append("- Nothing is under change control yet: no state cache and no `state:` "
                 "frontmatter anywhere in the tree. The lifecycle "
                 f"({' → '.join(p['states'])}) is defined but unused in this repo.")

    f = d["flow"]
    if f["present"]:
        L += ["", f"## Information flow (projected from {f['source']})"]
        for t in f["tiers"]:
            L.append(f"- {t['tier']}: {t['docs']} docs — {t['description']}")

    t = d["terms"]
    if t["present"]:
        L += ["", f"## Project terms ({t['count']}, from {t['source']})"]
        for x in t["terms"]:
            L.append(f"- {x['term']}: {x['definition']}")

    return PlainTextResponse("\n".join(L))
