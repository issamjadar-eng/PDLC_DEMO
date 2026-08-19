"""Document Pipeline loader — the project's documentation flow, derived live.

The console AUTHORS NO DATA here. Every number is a projection of artifacts the
owning skills already produce, computed at request time:

    Input analysis   docs/project/input-analysis/**            (medtech-docs)
    Strategies       console.strategy.loader                   (strategy)
    Design controls  project.yml dhfs[].path + role folders    (medtech-docs)
    Trace            docs/project/console/<dhf>/console_trace_matrix.json
                                                               (trace-matrix)
    Obligations      docs/project/dhf-manifest/*-manifest.json (dhf-manifest)
    Gaps             docs/_analysis/index.json                 (gap-analysis)
    Submission       submissions/.console/submission-index.json(submissions)
    Ingestion        docs/internal/source{,-md}/, docs/external (docflow)
    Publish          docs/.change-control/state.json           (change-control)
    Terms            glossary.md                               (project)
    Information flow CLAUDE.md § Information Flow              (project)

Missing artifacts degrade to an empty stage carrying a `hint` — the producer
command — never an exception.

WHY THIS IS NOT NAMED "docs flow". The sister console calls its equivalent tab
Docs Flow. Here that would collide with the `/docflow` skill, which owns a
different and narrower concept (binary ↔ markdown conversion) and is only one
lane of this view.

TWO PLACES WHERE THE OBVIOUS READ IS THE WRONG READ — do not "simplify" either:

1. **Obligation coverage is NOT computed from the manifest's `status`/
   `location` fields.** `dhf-manifest` v7 (SKILL.md:14) removed both from
   per-obligation entries and moved coverage/lifecycle/evidence-binding to
   `/tracker assess` exclusively. The manifest on disk here predates that
   break, so those fields are still present and every entry reads
   `status: GAP` — which looks like a 0%-coverage dataset and is actually a
   retired schema. We report catalogued COUNTS (the catalog's own job) and
   point coverage at the tracker.

2. **`source-md/` is not evidence that `source/` was converted.** This project
   has ~90 markdown files under `source-md/` and one real binary under
   `source/`: the markdown was largely authored, not converted. Presenting a
   conversion RATIO would invent a pipeline that did not run. We report both
   corpora and count genuine conversion provenance (`docflow:` blocks)
   separately.
"""
from __future__ import annotations

import json
import re
import time
from pathlib import Path

# Live-derivation is cheap but not free; a page reload within a few seconds
# should not re-walk the doc tree. Deliberately longer than the Journey tab's
# 2s TTL — this view answers "how does the pipeline look", not "did the command
# I just ran land".
_CACHE: dict = {"at": 0.0, "data": None}
_CACHE_TTL_S = 15.0


def discover(repo_root: Path) -> dict:
    """Nav probe: the pipeline view exists when the docs pillar does.

    Wrapped by the caller, but defensive here too — the nav middleware has no
    guard of its own, so a raise in any probe 500s every route in the console.
    """
    try:
        return {"has_any": (repo_root / "docs" / "README.md").is_file()}
    except Exception:
        return {"has_any": False}


# ---------------------------------------------------------------------------
# small readers
# ---------------------------------------------------------------------------
def _read_json(p: Path):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def _read_yaml(p: Path):
    try:
        import yaml

        return yaml.safe_load(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def _count_md(root: Path) -> int:
    """Markdown files under `root`, excluding READMEs — a README documents the
    folder's convention rather than being content of the kind being counted."""
    try:
        return sum(1 for p in root.rglob("*.md") if p.name.lower() != "readme.md")
    except Exception:
        return 0


def _mtime_iso(p: Path) -> str:
    try:
        return time.strftime("%Y-%m-%d", time.localtime(p.stat().st_mtime))
    except Exception:
        return ""


# ---------------------------------------------------------------------------
# Lane 1 — authoring pipeline
# ---------------------------------------------------------------------------
def _stage_input_analysis(repo_root: Path) -> dict:
    base = repo_root / "docs" / "project" / "input-analysis"
    if not base.is_dir():
        return {"present": False, "total": 0, "parts": [],
                "hint": "/medtech-docs init scaffolds docs/project/input-analysis/"}
    parts = [{"name": d.name, "count": _count_md(d)}
             for d in sorted(base.iterdir()) if d.is_dir()]
    return {
        "present": True,
        "total": sum(p["count"] for p in parts),
        "parts": parts,
        "hint": "",
    }


def _stage_strategies(repo_root: Path) -> dict:
    """Reuses the Strategy landing loader rather than re-parsing the docs.

    One parser, two consumers. A second decision-counter here would have to
    re-learn the two-format rule (v15 blocks vs legacy prose, never summed) and
    would drift from the Strategy tab the first time either changed.
    """
    try:
        from console.strategy.loader import load_rollup

        r = load_rollup(repo_root)
    except Exception:
        return {"present": False, "hint": "/strategy assemble <domain>"}
    return {
        "present": bool(r["total_domains"]),
        "live": r["live"],
        "stubs": r["stubs"],
        "total": r["total_domains"],
        "decisions": r["decisions"],
        "proposals": r["proposals"],
        "mixed_formats": r["mixed_formats"],
        "hint": "" if r["live"] else "/strategy assemble <domain>",
    }


# Canonical design-controls role folders. Read from disk per DHF rather than
# assumed: a DHF that does not carry a role simply reports it absent.
_DC_ROLES = (
    "user-needs", "requirements", "architecture", "vnv",
    "risk-management", "usability", "labeling", "pccp", "plans",
)


def _dhf_roots(repo_root: Path) -> list[dict]:
    """DHF name → path, from `project.yml dhfs[]`.

    NEVER hardcode DHF paths (.claude/rules/audit-wiring-before-adding-fields):
    the manifest owns where a DHF lives, and a folder rename must not silently
    turn this stage into a liar.
    """
    data = _read_yaml(repo_root / "project.yml") or {}
    out = []
    for row in (data.get("dhfs") or []):
        if isinstance(row, dict) and row.get("path"):
            out.append({
                "name": row.get("architecture_name") or row.get("name") or Path(row["path"]).name,
                "slug": Path(str(row["path"]).rstrip("/")).name,
                "path": str(row["path"]),
                "role": row.get("role", ""),
            })
    return out


def _stage_design_controls(repo_root: Path) -> dict:
    dhfs = _dhf_roots(repo_root)
    if not dhfs:
        return {"present": False, "rows": [], "total_docs": 0,
                "hint": "declare dhfs[] in project.yml, then /medtech-docs add-dhf"}
    rows = []
    for d in dhfs:
        dc = repo_root / d["path"] / "design-controls"
        present_roles = [r for r in _DC_ROLES if (dc / r).is_dir()] if dc.is_dir() else []
        rows.append({
            "name": d["name"],
            "slug": d["slug"],
            "path": d["path"],
            "role": d["role"],
            "roles_present": len(present_roles),
            "roles_total": len(_DC_ROLES),
            "roles": present_roles,
            "docs": _count_md(dc) if dc.is_dir() else 0,
        })
    return {
        "present": True,
        "rows": rows,
        "dhf_count": len(rows),
        "total_docs": sum(r["docs"] for r in rows),
        "hint": "",
    }


def _stage_trace(repo_root: Path) -> dict:
    """Per-DHF trace coverage from the trace-matrix skill's console sidecars.

    `orphan` counts are reported per layer because that is the shape the
    producer emits; collapsing them into one percentage would hide which layer
    is actually unlinked.
    """
    base = repo_root / "docs" / "project" / "console"
    files = sorted(base.glob("*/console_trace_matrix.json")) if base.is_dir() else []
    if not files:
        return {"present": False, "rows": [], "hint": "/trace-matrix build"}
    rows = []
    for f in files:
        d = _read_json(f)
        if not isinstance(d, dict):
            continue
        stats = d.get("stats") or {}
        traced_items = orphans = 0
        layers = []
        for layer, s in stats.items():
            if not isinstance(s, dict):
                continue
            n = int(s.get("count") or 0)
            o = int(s.get("orphan") or 0)
            traced_items += n
            orphans += o
            layers.append({"layer": layer, "count": n, "orphan": o})
        rows.append({
            "dhf": f.parent.name,
            # NOT named `items`: Jinja resolves attribute access before item
            # lookup, so `d.items` in a template returns dict.items (the bound
            # method) and renders as "<built-in method items…>". Any key that
            # shadows a dict method is a template landmine.
            "traced_items": traced_items,
            "orphans": orphans,
            "layers": layers,
            "generated": d.get("generated_at", ""),
        })
    rows.sort(key=lambda r: -r["traced_items"])
    return {
        "present": True,
        "rows": rows,
        "dhf_count": len(rows),
        "traced_items": sum(r["traced_items"] for r in rows),
        "orphans": sum(r["orphans"] for r in rows),
        "hint": "",
    }


def _stage_obligations(repo_root: Path) -> dict:
    """Obligation CATALOG counts only — deliberately not coverage.

    See the module docstring, point 1. The manifest's `status`/`location`
    fields were retired in dhf-manifest v7; a manifest still carrying them is
    pre-v7 and its wall-to-wall `GAP` is a schema artifact, not a finding.
    """
    base = repo_root / "docs" / "project" / "dhf-manifest"
    files = sorted(base.glob("*-dhf-manifest.json")) if base.is_dir() else []
    if not files:
        return {"present": False, "hint": "/dhf-manifest build-manifest"}
    f = files[0]
    d = _read_json(f) or {}
    per = d.get("dhf_manifest") or {}
    rows = [{"dhf": k, "obligations": len(v) if isinstance(v, list) else 0}
            for k, v in per.items()]
    rows.sort(key=lambda r: -r["obligations"])

    # v7 marker. Its ABSENCE is the signal that this artifact predates the
    # schema break — reported so the stage's own provenance is visible rather
    # than quietly assumed current.
    legacy_schema = "obligation_set_hash" not in d

    # The v7 home for coverage. Absent → coverage is simply not computed
    # anywhere yet, and the stage says so instead of inventing a number.
    tracker_sidecar = repo_root / "docs" / "project" / "submissions" / "submission-tracker.agent.json"

    return {
        "present": True,
        "source_obligations": d.get("source_obligations") or 0,
        "projected": sum(r["obligations"] for r in rows),
        "rows": rows,
        "generated": d.get("generated", ""),
        "legacy_schema": legacy_schema,
        "coverage_available": tracker_sidecar.is_file(),
        "coverage_owner": "/tracker assess",
        "hint": "/dhf-manifest build-manifest" if legacy_schema else "",
    }


def _stage_gaps(repo_root: Path) -> dict:
    d = _read_json(repo_root / "docs" / "_analysis" / "index.json")
    if not isinstance(d, dict):
        return {"present": False, "hint": "/gap-analysis render"}
    counts = d.get("counts") or {}
    return {
        "present": True,
        "total": counts.get("total", 0),
        "by_status": counts.get("by_status") or {},
        "by_topic": counts.get("by_topic") or {},
        "hint": "",
    }


def _stage_submission(repo_root: Path) -> dict:
    d = _read_json(
        repo_root / "docs" / "project" / "submissions" / ".console" / "submission-index.json"
    )
    if not isinstance(d, dict):
        return {"present": False, "filings": [], "hint": "/submissions render"}
    filings = []
    for f in (d.get("filings") or []):
        c = f.get("counts") or {}
        filings.append({
            "id": f.get("id", ""),
            "type": f.get("type", ""),
            "title": f.get("title", ""),
            "status": f.get("status", ""),
            "required": c.get("required", 0),
            "docs": c.get("docs", 0),
            "questions": c.get("questions", 0),
            "blocking": f.get("blocking", 0),
        })
    return {"present": True, "filings": filings,
            "blocking": sum(f["blocking"] for f in filings), "hint": ""}


# ---------------------------------------------------------------------------
# Lane 2 — ingestion / conversion
# ---------------------------------------------------------------------------
_BINARY_EXT = {".pdf", ".docx", ".doc", ".xlsx", ".xls", ".pptx"}

# A docflow-converted document carries a `docflow:` provenance key inside its
# leading metadata block. Anchored to line-start so a prose mention of the
# skill name in a README never counts as provenance.
_DOCFLOW_PROV = re.compile(r"^\s*docflow:\s*$", re.MULTILINE)


def _lane_ingestion(repo_root: Path) -> dict:
    internal = repo_root / "docs" / "internal"
    src, src_md = internal / "source", internal / "source-md"
    external = repo_root / "docs" / "external"

    binaries = []
    if src.is_dir():
        for p in src.rglob("*"):
            if p.is_file() and p.suffix.lower() in _BINARY_EXT:
                binaries.append(p.relative_to(repo_root).as_posix())

    md_parts = []
    if src_md.is_dir():
        md_parts = [{"name": d.name, "count": _count_md(d)}
                    for d in sorted(src_md.iterdir())
                    if d.is_dir() and _count_md(d)]

    ext_parts = []
    if external.is_dir():
        ext_parts = [{"name": d.name, "count": _count_md(d)}
                     for d in sorted(external.iterdir()) if d.is_dir()]

    # Genuine conversion provenance, counted across the whole docs tree.
    converted = 0
    try:
        for p in (repo_root / "docs").rglob("*.md"):
            try:
                if _DOCFLOW_PROV.search(p.read_text(encoding="utf-8", errors="ignore")):
                    converted += 1
            except OSError:
                continue
    except Exception:
        pass

    md_total = sum(p["count"] for p in md_parts)
    return {
        "present": src_md.is_dir() or external.is_dir(),
        "binaries": len(binaries),
        "binary_files": binaries[:12],
        "source_md": md_total,
        "source_md_parts": md_parts,
        "external": sum(p["count"] for p in ext_parts),
        "external_parts": ext_parts,
        "converted": converted,
        # The honest framing: a large source-md corpus beside a nearly empty
        # source/ tree means the markdown was AUTHORED, not converted. Stated
        # rather than expressed as a ratio that would imply otherwise.
        "authored_not_converted": md_total > 0 and converted == 0,
        "hint": "/docflow convert <file>",
    }


# ---------------------------------------------------------------------------
# Lane 3 — regulated publish (contract-first)
# ---------------------------------------------------------------------------
# The change-control lifecycle, in order (change-control/SKILL.md:61).
PUBLISH_STATES = ("draft", "published", "review-formal", "frozen", "released")

_FM_STATE = re.compile(r"^\s*state:\s*([a-z-]+)\s*$", re.MULTILINE)


def _lane_publish(repo_root: Path) -> dict:
    """Where each controlled document sits in the regulated publish lifecycle.

    Two sources, in precedence order: the skill's own state cache, else a walk
    for `state:` frontmatter. Both are absent in this project today, so this
    lane renders an empty state — which is the correct contract, not a defect.
    Built ahead of the data so it lights up when the mirror lands.
    """
    cache = repo_root / "docs" / ".change-control" / "state.json"
    by_state: dict[str, int] = {}
    source = ""

    cached = _read_json(cache)
    if isinstance(cached, list):
        source = "state-cache"
        for row in cached:
            if isinstance(row, dict):
                s = str(row.get("state", "")).strip()
                if s:
                    by_state[s] = by_state.get(s, 0) + 1
    elif isinstance(cached, dict) and isinstance(cached.get("documents"), list):
        source = "state-cache"
        for row in cached["documents"]:
            if isinstance(row, dict):
                s = str(row.get("state", "")).strip()
                if s:
                    by_state[s] = by_state.get(s, 0) + 1

    if not by_state:
        docs = repo_root / "docs" / "project"
        if docs.is_dir():
            try:
                for p in docs.rglob("*.md"):
                    try:
                        head = p.read_text(encoding="utf-8", errors="ignore")[:4000]
                    except OSError:
                        continue
                    m = _FM_STATE.search(head)
                    if m:
                        by_state[m.group(1)] = by_state.get(m.group(1), 0) + 1
                if by_state:
                    source = "frontmatter"
            except Exception:
                pass

    return {
        "present": bool(by_state),
        "source": source,
        "by_state": by_state,
        "total": sum(by_state.values()),
        "states": list(PUBLISH_STATES),
        "hint": "/change-control adopt <confluence-url>  or  /change-control publish <file>",
    }


# ---------------------------------------------------------------------------
# Lane 4 — terms + information flow
# ---------------------------------------------------------------------------
# `- **TERM** — definition` under `## Terms` in glossary.md.
_TERM = re.compile(r"^-\s+\*\*(?P<term>[^*]+)\*\*\s*(?:—|-|–)\s*(?P<def>.+)$")


def _lane_terms(repo_root: Path) -> dict:
    """Terms projected live from glossary.md — the file stays canonical.

    A copy here would be the exact drift `.claude/rules/claude-md-references.md`
    exists to prevent, and a glossary that disagrees with itself in two places
    is worse than one that lives in a single file.
    """
    p = repo_root / "glossary.md"
    terms = []
    try:
        for raw in p.read_text(encoding="utf-8").splitlines():
            m = _TERM.match(raw.strip())
            if m:
                d = m.group("def").strip()
                terms.append({
                    "term": m.group("term").strip(),
                    "definition": d[:400] + ("…" if len(d) > 400 else ""),
                })
    except OSError:
        return {"present": False, "terms": [], "source": "glossary.md",
                "hint": "author glossary.md at the repo root"}
    return {"present": bool(terms), "terms": terms, "count": len(terms),
            "source": "glossary.md", "hint": ""}


# The three-tier model in CLAUDE.md § Information Flow. Parsed, never copied.
_FLOW_TIERS = ("external", "internal", "project")


def _lane_information_flow(repo_root: Path) -> dict:
    """The External → Project ← Internal model, projected from CLAUDE.md.

    Only the per-tier descriptions are lifted, and only from the section that
    owns them. CLAUDE.md stays the single source; this is a view of it.
    """
    p = repo_root / "CLAUDE.md"
    try:
        text = p.read_text(encoding="utf-8")
    except OSError:
        return {"present": False, "tiers": [], "hint": ""}

    # Terminate on any heading of level 2 OR DEEPER. The previous `^##\s`
    # required whitespace after the second '#', so a `### Sub-heading` — which
    # is `##` followed by `#` — did not match, and the section body ran on
    # through every subsection until the next level-2 heading. In this repo
    # that swallowed `### Project Manifest`, so the "project" tier rendered
    # its own description plus a heading, bold markers and a markdown table.
    m = re.search(r"^##\s+Information Flow\s*$(.*?)(?=^#{2,}\s|\Z)", text,
                  re.MULTILINE | re.DOTALL)
    body = m.group(1) if m else ""
    tiers = []
    for tier in _FLOW_TIERS:
        # Defence in depth: stop at the next tier bullet, at ANY heading, or at
        # end of body — so a future subsection can't leak into the last tier
        # even if the section regex above is loosened again.
        tm = re.search(
            rf"^-\s+\*\*{tier}\*\*\s*(?:—|-|–)\s*(?P<d>.+?)(?=^-\s+\*\*|^#{{1,6}}\s|\Z)",
            body, re.MULTILINE | re.DOTALL | re.IGNORECASE,
        )
        desc = " ".join(tm.group("d").split()) if tm else ""
        tiers.append({
            "tier": tier,
            "description": desc[:420] + ("…" if len(desc) > 420 else ""),
            "docs": _count_md(repo_root / "docs" / tier),
        })
    return {"present": any(t["description"] for t in tiers), "tiers": tiers,
            "source": "CLAUDE.md § Information Flow", "hint": ""}


# ---------------------------------------------------------------------------
# assembly
# ---------------------------------------------------------------------------
def load_pipeline(repo_root: Path) -> dict:
    now = time.monotonic()
    if _CACHE["data"] is not None and now - _CACHE["at"] < _CACHE_TTL_S:
        return _CACHE["data"]

    authoring = [
        {"key": "input-analysis", "label": "Input analysis",
         "owner": "medtech-docs", "data": _stage_input_analysis(repo_root)},
        {"key": "strategies", "label": "Strategies",
         "owner": "strategy", "data": _stage_strategies(repo_root)},
        {"key": "design-controls", "label": "Design controls",
         "owner": "medtech-docs", "data": _stage_design_controls(repo_root)},
        {"key": "trace", "label": "Trace",
         "owner": "trace-matrix", "data": _stage_trace(repo_root)},
        {"key": "obligations", "label": "Obligations",
         "owner": "dhf-manifest", "data": _stage_obligations(repo_root)},
        {"key": "gaps", "label": "Gap analysis",
         "owner": "gap-analysis", "data": _stage_gaps(repo_root)},
        {"key": "submission", "label": "Submission",
         "owner": "submissions", "data": _stage_submission(repo_root)},
    ]

    data = {
        "present": True,
        "authoring": authoring,
        "ingestion": _lane_ingestion(repo_root),
        "publish": _lane_publish(repo_root),
        "terms": _lane_terms(repo_root),
        "flow": _lane_information_flow(repo_root),
        "stages_present": sum(1 for s in authoring if s["data"].get("present")),
        "stages_total": len(authoring),
    }
    _CACHE.update(at=now, data=data)
    return data
