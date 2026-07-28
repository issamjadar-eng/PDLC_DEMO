"""Commercial sidecar loader.

The console never computes a business answer and never parses answer markdown for
structure. It reads only what the `commercial` skill publishes under
`docs/project/commercial/`:

    .console/commercial-index.json         — question roster + per-BQ statuses (schema 1.x)
    reports/BQ-NN/<edition>/data.json      — chart series + verdicts (evidence-classed)
    reports/BQ-NN/<edition>/edition.yml    — lifecycle metadata (draft/approved/superseded, pins)
    reports/BQ-NN/<edition>/approval.yml   — approver, checks, content hashes (approved editions)

Loose-coupling rule (same contract as Submission / Tasks / Gap-Analysis): sidecars
missing → empty state with a hint to run the skill's `render`; the console knows
nothing about how the numbers were produced — that's the point. Report *bodies*
render via the documents renderer using the repo-relative path in the sidecar.
"""
from __future__ import annotations

import json
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover — PyYAML ships with the console deps
    yaml = None

COMMERCIAL_DIR = ("docs", "project", "commercial")
INDEX_REL = (".console", "commercial-index.json")


def _root(repo_root: Path) -> Path:
    return repo_root.joinpath(*COMMERCIAL_DIR)


def discover(repo_root: Path) -> dict:
    """Cheap nav-visibility probe (stat only)."""
    index = _root(repo_root).joinpath(*INDEX_REL)
    return {"has_index": index.is_file(), "has_any": index.is_file()}


def _read_json(p: Path) -> dict | None:
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _read_yaml(p: Path) -> dict | None:
    if yaml is None:
        return None
    try:
        return yaml.safe_load(p.read_text(encoding="utf-8"))
    except (OSError, Exception):
        return None


def load_index(repo_root: Path) -> dict | None:
    return _read_json(_root(repo_root).joinpath(*INDEX_REL))


def question_row(repo_root: Path, bq: str) -> dict | None:
    index = load_index(repo_root) or {}
    for q in index.get("questions", []):
        if q.get("id") == bq:
            return q
    return None


def load_edition(repo_root: Path, bq: str, edition: str) -> dict | None:
    """One edition's full detail: data.json + lifecycle + approval + report path."""
    edir = _root(repo_root) / "reports" / bq / edition
    data = _read_json(edir / "data.json")
    meta = _read_yaml(edir / "edition.yml") or {}
    if data is None and not meta:
        return None
    approval = _read_yaml(edir / "approval.yml")
    quality = _read_json(edir / "quality.json")
    rel = edir.relative_to(repo_root)
    return {
        "quality": quality,
        "plan_pin": meta.get("plan"),
        "bq": bq,
        "edition": edition,
        "status": meta.get("status", "draft"),
        "created_at": meta.get("created_at"),
        "pins": meta.get("pins", {}),
        "data": data or {},
        "approval": approval,
        "report_path": str(rel / "report.md"),
        "data_path": str(rel / "data.json"),
    }


def load_pinned_table(repo_root: Path, dataset: str, snapshot: str) -> dict | None:
    """Rows of a pinned snapshot's normalized CSV — the tabular truth behind an
    answer's charts. Read-only; the console never mutates corpus data."""
    import csv as _csv

    ndir = repo_root / "docs" / "project" / "corpus" / dataset / "snapshots" / snapshot / "normalized"
    if not ndir.is_dir():
        return None
    csvs = sorted(ndir.glob("*.csv"))
    if not csvs:
        return None
    try:
        with open(csvs[0], newline="", encoding="utf-8") as f:
            reader = _csv.DictReader(f)
            columns = reader.fieldnames or []
            rows = [dict(r) for r in reader]
    except OSError:
        return None
    return {"dataset": dataset, "snapshot": snapshot, "file": csvs[0].name,
            "columns": columns, "rows": rows}


def team_names(repo_root: Path) -> list[str]:
    """Active roster names from project.yml — the approver choices for the UI
    approve action (who-may-approve: any rostered member, recorded by name)."""
    if yaml is None:
        return []
    try:
        data = yaml.safe_load((repo_root / "project.yml").read_text(encoding="utf-8"))
        return [m.get("name") for m in (data.get("team", {}).get("active") or []) if m.get("name")]
    except Exception:
        return []


def skill_render_script(repo_root: Path) -> Path | None:
    p = repo_root / ".claude" / "skills" / "commercial" / "scripts" / "commercial.py"
    return p if p.is_file() else None
