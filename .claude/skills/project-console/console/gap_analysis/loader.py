"""Gap Analysis sidecar loader.

The console never parses analysis prose. It only reads the JSON sidecars the
`gap-analysis` skill's `render` action writes under `docs/_analysis/`:

    docs/_analysis/index.json                          — roll-up of all analyses
    docs/_analysis/<component>/<id>/<id>.gap.json      — per-analysis detail (folder-per-analysis)

Loose-coupling rule (same contract as the trace-matrix sidecar): if the
sidecars don't exist, the section degrades to an empty state with a hint to
run `/gap-analysis render`. The console knows nothing about how the JSON was
produced — only the `schema_version: "1.0"` shape.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ANALYSIS_DIR = ("docs", "_analysis")
INDEX_NAME = "index.json"


def _analysis_root(repo_root: Path) -> Path:
    return repo_root.joinpath(*ANALYSIS_DIR)


def discover(repo_root: Path) -> dict:
    """Cheap nav-visibility probe (stat only). Nav shows the tab when the
    roll-up index OR at least one per-analysis sidecar exists."""
    root = _analysis_root(repo_root)
    index = root / INDEX_NAME
    has_index = index.is_file()
    has_any = has_index or any(root.glob("*/*/*.gap.json"))
    return {"has_index": has_index, "has_any": has_any}


def load_index(repo_root: Path) -> dict | None:
    """Return the roll-up index, or a synthesized one from per-analysis
    sidecars if the index file is missing (resilient to a partial render)."""
    root = _analysis_root(repo_root)
    index = root / INDEX_NAME
    if index.is_file():
        try:
            return json.loads(index.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            pass
    # Fallback: rebuild a lightweight index from whatever sidecars exist.
    analyses = []
    for sidecar in sorted(root.glob("*/*/*.gap.json")):
        d = _read_json(sidecar)
        if not d:
            continue
        m = d.get("meta", {})
        analyses.append(
            {
                "id": m.get("id"),
                "title": m.get("title"),
                "status": m.get("status"),
                "topic": m.get("topic"),
                "component": m.get("component"),
                "last_updated": m.get("last_updated"),
                "source_md": m.get("source_md"),
                "sidecar": str(sidecar.relative_to(repo_root).as_posix()),
                "agents": [a["name"] for a in d.get("agents", []) if a.get("ran")],
                "stats": d.get("stats", {}),
            }
        )
    if not analyses:
        return None
    return {"schema_version": "1.0", "analyses": analyses, "counts": _counts(analyses)}


def load_analysis(repo_root: Path, analysis_id: str) -> dict | None:
    """Load one per-analysis sidecar by id (searches all component folders)."""
    root = _analysis_root(repo_root)
    for sidecar in root.glob("*/*/*.gap.json"):
        d = _read_json(sidecar)
        if d and d.get("meta", {}).get("id") == analysis_id:
            return d
    return None


def skill_render_script(repo_root: Path) -> Path | None:
    """Path to the gap-analysis skill's renderer, if installed."""
    p = repo_root / ".claude" / "skills" / "gap-analysis" / "scripts" / "render_sidecars.py"
    return p if p.is_file() else None


def _read_json(p: Path) -> dict | None:
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


# ---------------------------------------------------------------------------
# narrative companion (display-only)
# ---------------------------------------------------------------------------
# The JSON sidecar carries the *structured* projection (findings, assertions,
# the one-line "what they contributed"). For the detail view we ALSO want two
# pieces of prose the renderer leaves in the markdown: the analysis Goal, and
# each agent's FULL writeup. Those live as sibling files in the folder-per-
# analysis layout the gap-analysis skill authors:
#
#     <id>/<id>.md            ← aggregate (carries the "## Goal" section)
#     <id>/recs-<advisor>.md  ← one discipline-advisor full response
#     <id>/kol-*-<name>.md    ← one KOL-persona full response
#
# This is a loose-coupled, convention-based discovery (same spirit as the
# trace-matrix drift.json sibling lookup): if the docs aren't there, the
# detail view simply omits the goal banner / agent-response viewer. We match
# each sibling doc to an agent the sidecar already lists, by name suffix, so
# no extra contract field is required from the producer.

_GOAL_HEADING = re.compile(r"^##\s+.*goal", re.IGNORECASE)
_GOAL_ITEM = re.compile(r"^\s*-\s*\*\*(.+?):\*\*\s*(.+)$")


def _strip_frontmatter(text: str) -> str:
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            return text[end + 4:].lstrip("\n")
    return text


def _frontmatter_field(text: str, key: str) -> str:
    if not text.startswith("---"):
        return ""
    end = text.find("\n---", 3)
    fm = text[3:end] if end != -1 else ""
    m = re.search(rf"^{re.escape(key)}:\s*(.+)$", fm, re.MULTILINE)
    return m.group(1).strip().strip('"').strip("'") if m else ""


def _goal_items(agg_text: str) -> list[dict]:
    """Pull the `- **Label:** value` rows out of the analysis Goal section.
    Generic across analyses (the gap-analysis template authors the Goal section
    with motivating-question / decision / stakeholders bullets in this shape)."""
    body, capturing = [], False
    for line in agg_text.splitlines():
        if line.startswith("## "):
            if capturing:
                break
            capturing = bool(_GOAL_HEADING.match(line))
            continue
        if capturing:
            body.append(line)
    items = []
    for line in body:
        m = _GOAL_ITEM.match(line)
        if m:
            items.append({"label": m.group(1).strip(), "value_md": m.group(2).strip()})
    return items


def load_narratives(repo_root: Path, detail: dict) -> dict:
    """Return display-only companion prose for the detail view:
        {"goal_items": [{"label","value_md"}, ...],
         "agents": {<agent-name>: {"kind","title","specialty","body_md","file"}}}
    Reads sibling markdown next to the aggregate named in `meta.source_md`.
    Missing/unreadable docs degrade silently to empty."""
    out: dict = {"goal_items": [], "agents": {}}
    src = (detail.get("meta") or {}).get("source_md")
    if not src:
        return out
    agg = repo_root / src
    folder = agg.parent
    try:
        out["goal_items"] = _goal_items(agg.read_text(encoding="utf-8"))
    except OSError:
        pass

    docs: list[tuple[Path, str]] = []
    for pattern in ("recs-*.md", "kol-*.md"):
        for p in sorted(folder.glob(pattern)):
            try:
                docs.append((p, p.read_text(encoding="utf-8")))
            except OSError:
                continue

    for agent in detail.get("agents", []):
        name = agent.get("name") or ""
        if not name:
            continue
        for p, text in docs:
            stem = p.stem
            if stem == f"recs-{name}" or stem.endswith(f"-{name}"):
                out["agents"][name] = {
                    "kind": "advisor" if p.name.startswith("recs-") else "kol",
                    "title": _frontmatter_field(text, "title"),
                    "specialty": _frontmatter_field(text, "specialty"),
                    "body_md": _strip_frontmatter(text),
                    "file": p.relative_to(repo_root).as_posix(),
                }
                break
    return out


def _counts(analyses: list[dict]) -> dict:
    def by(key):
        out: dict[str, int] = {}
        for a in analyses:
            k = a.get(key) or "—"
            out[k] = out.get(k, 0) + 1
        return out

    return {
        "total": len(analyses),
        "by_status": by("status"),
        "by_topic": by("topic"),
        "by_component": by("component"),
    }
