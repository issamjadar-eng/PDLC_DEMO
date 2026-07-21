"""Tasks tab loader — reads the summary the `task` skill's `summary` action
derives to tasks/task-summary.json. Pure consumer: the console never parses
task docs itself; regenerate with `/task summary`. Age is computed from the
`generated` stamp so staleness is visible in the UI."""
from __future__ import annotations

import datetime
import json
from pathlib import Path

SUMMARY_REL = ("tasks", "task-summary.json")
FRESH_D = 7
AGING_D = 21


def _path(repo_root: Path) -> Path:
    return repo_root.joinpath(*SUMMARY_REL)


def discover(repo_root: Path) -> dict:
    """Cheap nav-visibility probe (stat only) — the Tasks tab shows only when
    the task skill has published a summary."""
    return {"has_any": _path(repo_root).is_file()}


def load_summary(repo_root: Path) -> dict | None:
    p = _path(repo_root)
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    try:
        age = (datetime.date.today()
               - datetime.date.fromisoformat(d.get("generated", ""))).days
    except ValueError:
        age = None
    d["_age_days"] = age
    d["_age_label"] = ("today" if age == 0
                       else f"{age}d ago" if age is not None else "?")
    d["_freshness"] = ("fresh" if age is not None and age <= FRESH_D
                       else "aging" if age is not None and age <= AGING_D
                       else "stale" if age is not None else "unknown")
    return d
