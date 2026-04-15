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


def list_dhfs(repo_root: Path) -> list[DHFEntry]:
    out: list[DHFEntry] = []
    for entry in _project_dhfs(repo_root):
        path = entry.get("path")
        if not path:
            continue
        name = path.rstrip("/").split("/")[-1]
        sidecar = (
            repo_root
            / "docs"
            / "project"
            / "dhfs"
            / path
            / "design-controls"
            / "trace-matrix"
            / "trace-matrix.json"
        )
        out.append(
            DHFEntry(
                name=name,
                path=path,
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
