"""Trace Matrix sidecar loader.

The console never computes traces. It only reads `trace-matrix.json` files
that the `trace-matrix` skill has written into each DHF's
`design-controls/trace-matrix/` folder. This loader walks `project.yml`'s
`dhfs[]` and returns whatever sidecars currently exist.

Loose coupling rule: if no sidecars exist, the section degrades gracefully
to an empty state with a hint to run the build. If the trace-matrix skill is
not installed, the section still works for any pre-existing sidecars.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass
class DHFEntry:
    name: str          # leaf name, e.g. "pca-device"
    path: str          # full path under docs/project/dhfs/, e.g. "cloud-suite/dhfs/drug-library-manager"
    sidecar_path: Path
    has_sidecar: bool


def _project_dhfs(repo_root: Path) -> list[dict]:
    pyml = repo_root / "project.yml"
    if not pyml.exists():
        return []
    raw = yaml.safe_load(pyml.read_text(encoding="utf-8")) or {}
    return raw.get("dhfs") or []


_DHF_BASE = ("docs", "project", "dhfs")


def _resolve_dhf_root(repo_root: Path, entry: dict) -> tuple[str, Path] | None:
    """Return (leaf_name, absolute_dhf_root) for a project.yml dhfs[] entry.

    Tolerates two conventions that have appeared in the wild:
      1. `path: <leaf>`               — PDLC_DEMO style (e.g. `path: pca-device`)
      2. `path: docs/project/dhfs/<leaf>` — Arthrex PCCP style (full path)
    An explicit `leaf:` field wins if present.

    Returns None if the entry is unusable.
    """
    raw_path = (entry.get("path") or "").strip().rstrip("/")
    leaf = (entry.get("leaf") or "").strip() or (raw_path.split("/")[-1] if raw_path else "")
    if not leaf:
        return None

    if not raw_path:
        dhf_root = repo_root.joinpath(*_DHF_BASE, leaf)
    else:
        parts = raw_path.split("/")
        # If the path already starts with docs/project/dhfs/, use as-is; else prepend.
        if tuple(parts[: len(_DHF_BASE)]) == _DHF_BASE:
            dhf_root = repo_root.joinpath(*parts)
        else:
            dhf_root = repo_root.joinpath(*_DHF_BASE, *parts)
    return leaf, dhf_root


def list_dhfs(repo_root: Path) -> list[DHFEntry]:
    out: list[DHFEntry] = []
    for entry in _project_dhfs(repo_root):
        resolved = _resolve_dhf_root(repo_root, entry)
        if resolved is None:
            continue
        leaf, dhf_root = resolved
        sidecar = dhf_root / "design-controls" / "trace-matrix" / "trace-matrix.json"
        out.append(
            DHFEntry(
                name=leaf,
                path=str(dhf_root.relative_to(repo_root)) if dhf_root.is_relative_to(repo_root) else str(dhf_root),
                sidecar_path=sidecar,
                has_sidecar=sidecar.is_file(),
            )
        )
    return out


def load_sidecar(repo_root: Path, dhf_name: str) -> dict | None:
    for entry in list_dhfs(repo_root):
        if entry.name == dhf_name and entry.has_sidecar:
            try:
                return json.loads(entry.sidecar_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                return None
    return None


def skill_build_script(repo_root: Path) -> Path | None:
    """Return the path to the trace-matrix skill's build.py if installed."""
    p = repo_root / ".claude" / "skills" / "trace-matrix" / "scripts" / "build.py"
    return p if p.is_file() else None
