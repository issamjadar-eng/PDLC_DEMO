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
_CONSOLE_BASE = ("docs", "project", "console")
_CONSOLE_SIDECAR_NAME = "console_trace_matrix.json"


def _resolve_dhf_root(repo_root: Path, entry: dict) -> tuple[str, Path] | None:
    """Return (leaf_name, absolute_dhf_root) for a project.yml dhfs[] entry.

    Tolerates two conventions that have appeared in the wild:
      1. `path: <leaf>`               — leaf-only style (e.g. `path: pca-device`)
      2. `path: docs/project/dhfs/<leaf>` — full-path style
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
    """List DHF entries with their console-trace-matrix sidecar paths.

    The console reads a *console working copy* of the trace matrix that the
    trace-matrix skill writes to a fixed location:

        docs/project/console/<leaf>/console_trace_matrix.json

    This deliberately lives **outside** the DHF documentation tree
    (`docs/project/dhfs/...` for system DHFs, or `docs/project/_confluence/...`
    for item DHFs in projects that mirror Confluence). The DHF tree is
    reserved for *controlled* trace-matrix deliverables authored by humans;
    the console copy is regenerated on every `build` and is for project
    management and tooling, not regulatory submission.

    The `<leaf>` segment matches `project.yml dhfs[].leaf` and
    `trace-matrix.yml dhfs[].name` — the two skills coordinate on the leaf
    string by convention. No new config field; no shared registry.
    """
    out: list[DHFEntry] = []
    for entry in _project_dhfs(repo_root):
        resolved = _resolve_dhf_root(repo_root, entry)
        if resolved is None:
            continue
        leaf, dhf_root = resolved
        sidecar = repo_root.joinpath(*_CONSOLE_BASE, leaf, _CONSOLE_SIDECAR_NAME)
        display_root = sidecar.parent  # docs/project/console/<leaf>
        out.append(
            DHFEntry(
                name=leaf,
                path=str(display_root.relative_to(repo_root)) if display_root.is_relative_to(repo_root) else str(display_root),
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


_SEVERITY_RANK = {"error": 3, "warning": 2, "info": 1}


def _worst_severity(violations: list[dict]) -> str | None:
    """Return the highest-ranking severity in a list of violations,
    or None if the list is empty. Mirrors the ranking used by the
    `jira-pull` skill's `actions/build_trace.py:_worst_severity` so
    badges in the console match the unified-trace.md badges.
    """
    best = None
    best_rank = -1
    for v in violations:
        rank = _SEVERITY_RANK.get(v.get("severity", ""), 0)
        if rank > best_rank:
            best_rank = rank
            best = v.get("severity")
    return best


def load_drift_overlay(repo_root: Path, sidecar: dict) -> dict | None:
    """Look for `drift.json` files alongside any of the sidecar's layer
    sources, group their violations by `item_id`, and return a compact
    overlay suitable for badge + drawer rendering.

    Discovery rule (project-agnostic): for each path in
    `sidecar.layers[].source_files`, check whether `<same-dir>/drift.json`
    exists. Each unique drift.json is loaded once. This works for any
    project whose trace data is colocated with a sibling drift report —
    `jira-pull` is the first concrete consumer but the contract is generic.

    Returns:
      None if no drift.json is found.
      Otherwise: {
        "summary": { violations_total, by_severity, by_category, ... } merged across files,
        "violations_by_item": { item_id: [violations, ...] },
        "worst_by_item":      { item_id: "error"|"warning"|"info" },
        "sources":            [ "<repo-relative drift.json path>", ... ],
      }
    """
    drift_paths: list[Path] = []
    seen: set[Path] = set()
    for layer in sidecar.get("layers", []) or []:
        for src in layer.get("source_files") or []:
            d = (repo_root / src).parent / "drift.json"
            if d.is_file() and d not in seen:
                seen.add(d)
                drift_paths.append(d)

    if not drift_paths:
        return None

    merged_summary: dict = {
        "violations_total": 0,
        "by_severity": {"error": 0, "warning": 0, "info": 0},
        "by_category": {},
        "by_rule": {},
    }
    by_item: dict[str, list[dict]] = {}
    sources_rel: list[str] = []

    for dp in drift_paths:
        try:
            doc = json.loads(dp.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        sources_rel.append(
            str(dp.relative_to(repo_root)) if dp.is_relative_to(repo_root) else str(dp)
        )

        summary = doc.get("summary") or {}
        merged_summary["violations_total"] += int(summary.get("violations_total", 0) or 0)
        for sev, n in (summary.get("by_severity") or {}).items():
            merged_summary["by_severity"][sev] = (
                merged_summary["by_severity"].get(sev, 0) + int(n or 0)
            )
        for cat, n in (summary.get("by_category") or {}).items():
            merged_summary["by_category"][cat] = (
                merged_summary["by_category"].get(cat, 0) + int(n or 0)
            )
        for rule, n in (summary.get("by_rule") or {}).items():
            merged_summary["by_rule"][rule] = (
                merged_summary["by_rule"].get(rule, 0) + int(n or 0)
            )

        for v in doc.get("violations") or []:
            item_id = v.get("item_id")
            if not item_id:
                continue
            by_item.setdefault(item_id, []).append(v)

    worst_by_item = {iid: _worst_severity(vs) for iid, vs in by_item.items()}
    return {
        "summary": merged_summary,
        "violations_by_item": by_item,
        "worst_by_item": worst_by_item,
        "sources": sources_rel,
    }
