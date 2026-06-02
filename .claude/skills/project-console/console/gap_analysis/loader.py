"""Gap Analysis sidecar loader.

The console never parses analysis prose. It only reads the JSON sidecars the
`gap-analysis` skill's `render` action writes under `docs/_analysis/`:

    docs/_analysis/index.json                       — roll-up of all analyses
    docs/_analysis/<component>/<id>.gap.json        — per-analysis detail

Loose-coupling rule (same contract as the trace-matrix sidecar): if the
sidecars don't exist, the section degrades to an empty state with a hint to
run `/gap-analysis render`. The console knows nothing about how the JSON was
produced — only the `schema_version: "1.0"` shape.
"""
from __future__ import annotations

import json
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
    has_any = has_index or any(root.glob("*/*.gap.json"))
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
    for sidecar in sorted(root.glob("*/*.gap.json")):
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
    for sidecar in root.glob("*/*.gap.json"):
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
