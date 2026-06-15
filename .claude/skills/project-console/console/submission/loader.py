"""Submission sidecar loader.

The console never parses submission prose. It reads only the JSON sidecars the
`submissions` skill's `render` action writes under `docs/project/submissions/`:

    docs/project/submissions/.console/submission-index.json   — roll-up of filings
    docs/project/submissions/<filing>/<filing>.submission.json — per-filing detail

Loose-coupling rule (same contract as the gap-analysis / trace-matrix sidecars):
if the sidecars don't exist, the section degrades to an empty state with a hint to
run `/submissions render`. The console knows nothing about how the JSON was
produced — only the `schema_version: "1.0"` shape (see the submissions SKILL.md).

Document *bodies* are not in the sidecar — the router renders each doc's markdown
inline via the documents renderer, using the repo-relative `path` the sidecar
carries. This keeps the sidecar small and the rendering consistent with the rest
of the console.
"""
from __future__ import annotations

import json
from pathlib import Path

SUBMISSIONS_DIR = ("docs", "project", "submissions")
CONSOLE_DIR = ".console"
INDEX_NAME = "submission-index.json"


def _root(repo_root: Path) -> Path:
    return repo_root.joinpath(*SUBMISSIONS_DIR)


def discover(repo_root: Path) -> dict:
    """Cheap nav-visibility probe (stat only). Nav shows the Submission tab when
    the roll-up index OR any per-filing sidecar OR any composition-manifest
    exists."""
    root = _root(repo_root)
    index = root / CONSOLE_DIR / INDEX_NAME
    has_index = index.is_file()
    has_any = (
        has_index
        or any(root.glob("*/*.submission.json"))
        or any(root.glob("*/composition-manifest.md"))
    )
    return {"has_index": has_index, "has_any": has_any}


def _read_json(p: Path) -> dict | None:
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def load_index(repo_root: Path) -> dict | None:
    """Return the roll-up index, or synthesize one from per-filing sidecars if
    the index file is missing (resilient to a partial render)."""
    root = _root(repo_root)
    index = root / CONSOLE_DIR / INDEX_NAME
    d = _read_json(index)
    if d:
        return d
    filings = []
    for sidecar in sorted(root.glob("*/*.submission.json")):
        f = _read_json(sidecar)
        if not f:
            continue
        m = f.get("meta", {})
        filings.append(
            {
                "id": m.get("id"),
                "type": m.get("type"),
                "title": m.get("title"),
                "status": m.get("status"),
                "folder": m.get("folder"),
                "manifest": m.get("manifest_md"),
                "counts": f.get("counts", {}),
                "blocking": f.get("blocking", 0),
                "default_advisor": m.get("default_advisor", "regulatory-affairs"),
            }
        )
    if not filings:
        return None
    return {"schema_version": "1.0", "filings": filings}


def load_filing(repo_root: Path, filing_id: str) -> dict | None:
    """Load one per-filing sidecar by id."""
    root = _root(repo_root)
    p = root / filing_id / f"{filing_id}.submission.json"
    return _read_json(p)


def skill_render_script(repo_root: Path) -> Path | None:
    """Path to the submissions skill's renderer, if installed."""
    p = repo_root / ".claude" / "skills" / "submissions" / "scripts" / "render_sidecars.py"
    return p if p.is_file() else None
