"""Metrics section loader — reads the usage-metrics team JSON.

The console is a generic consumer of the `usage-metrics` skill: it never parses
transcripts or computes cost itself — it only reads the skill's published
`tools/usage-metrics/usage.json` (anonymized, schema `usage-metrics/team/v1`).
"""
from __future__ import annotations

import json
from pathlib import Path

USAGE_REL = "tools/usage-metrics/usage.json"


def usage_path(repo_root: Path) -> Path:
    return repo_root / USAGE_REL


def discover(repo_root: Path) -> dict:
    """Cheap nav-visibility probe (stat only). The Metrics tab shows only when
    the usage-metrics skill has published a team JSON."""
    return {"has_any": usage_path(repo_root).is_file()}


def load_usage(repo_root: Path) -> dict | None:
    """Return the team usage JSON, or None if missing/unreadable."""
    p = usage_path(repo_root)
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
