"""Snapshot cache for divergence detection.

Cache layout:

    docs/.change-control/snapshots/<page_id>-<version>.md

The file holds the last markdown body we pushed (or, on `adopt`, the
markdown we normalized from the page's ADF at adoption time). On each
new push we:

  1. read frontmatter to get `page_id` + `last_published_version`
  2. fetch current Confluence version from MCP
  3. if newer, normalize ADF→markdown and diff against the cached
     snapshot at `last_published_version` to surface reviewer changes
  4. on a clean push, write a new snapshot at the new version and
     prune older snapshots for the same page

This module is the I/O layer. Pure logic (path composition, prune
selection) is split out so it can be tested without filesystem state.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional


SNAPSHOT_DIRNAME = "snapshots"
DEFAULT_CACHE_ROOT = "docs/.change-control"

_FILENAME_RE = re.compile(r"^(?P<page_id>[A-Za-z0-9._-]+)-(?P<version>\d+)\.md$")


# ---- Path composition (pure) ----


def snapshot_dir(cache_root: str | Path = DEFAULT_CACHE_ROOT) -> Path:
    return Path(cache_root) / SNAPSHOT_DIRNAME


def snapshot_filename(page_id: str, version: int) -> str:
    if not page_id:
        raise ValueError("snapshot_filename: page_id must not be empty")
    if not isinstance(version, int) or version < 0:
        raise ValueError(f"snapshot_filename: version must be non-negative int, got {version!r}")
    return f"{page_id}-{version}.md"


def snapshot_path(
    page_id: str, version: int, cache_root: str | Path = DEFAULT_CACHE_ROOT
) -> Path:
    return snapshot_dir(cache_root) / snapshot_filename(page_id, version)


# ---- Filename parsing (pure) ----


@dataclass(frozen=True)
class SnapshotFile:
    page_id: str
    version: int
    path: Path


def parse_snapshot_filename(name: str) -> Optional[tuple[str, int]]:
    """Parse `<page_id>-<version>.md` → `(page_id, version)`. Returns
    None for non-matching names."""
    m = _FILENAME_RE.match(name)
    if not m:
        return None
    return m.group("page_id"), int(m.group("version"))


def select_snapshots_for_page(
    files: Iterable[Path], page_id: str
) -> list[SnapshotFile]:
    """Filter + sort snapshot files belonging to `page_id`,
    most-recent-version first."""
    out: list[SnapshotFile] = []
    for p in files:
        parsed = parse_snapshot_filename(p.name)
        if parsed is None:
            continue
        pid, ver = parsed
        if pid == page_id:
            out.append(SnapshotFile(page_id=pid, version=ver, path=p))
    out.sort(key=lambda s: s.version, reverse=True)
    return out


def select_prunable(
    snapshots: list[SnapshotFile], keep_version: int
) -> list[SnapshotFile]:
    """Return the snapshots that should be deleted given that we want
    to keep only the snapshot at `keep_version`. Older OR newer
    versions are both prunable — the contract is "one snapshot per
    page, the latest pushed."
    """
    return [s for s in snapshots if s.version != keep_version]


# ---- I/O ----


def write_snapshot(
    page_id: str,
    version: int,
    markdown: str,
    *,
    cache_root: str | Path = DEFAULT_CACHE_ROOT,
    prune_others: bool = True,
) -> Path:
    """Write `markdown` to `<cache_root>/snapshots/<page_id>-<version>.md`.

    Creates parent directories. If `prune_others`, deletes any other
    snapshot file for the same page in the same dir (older OR newer
    versions). Returns the written path.
    """
    target = snapshot_path(page_id, version, cache_root)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(markdown, encoding="utf-8")
    if prune_others:
        prune_old_snapshots(page_id, keep_version=version, cache_root=cache_root)
    return target


def read_snapshot(
    page_id: str, version: int, cache_root: str | Path = DEFAULT_CACHE_ROOT
) -> Optional[str]:
    """Return the cached markdown for `(page_id, version)` or None
    if absent."""
    p = snapshot_path(page_id, version, cache_root)
    if not p.is_file():
        return None
    return p.read_text(encoding="utf-8")


def list_snapshots(
    page_id: str, cache_root: str | Path = DEFAULT_CACHE_ROOT
) -> list[SnapshotFile]:
    """All cached snapshots for a page, newest version first."""
    d = snapshot_dir(cache_root)
    if not d.is_dir():
        return []
    return select_snapshots_for_page(sorted(d.iterdir()), page_id)


def latest_snapshot(
    page_id: str, cache_root: str | Path = DEFAULT_CACHE_ROOT
) -> Optional[SnapshotFile]:
    items = list_snapshots(page_id, cache_root)
    return items[0] if items else None


def prune_old_snapshots(
    page_id: str,
    keep_version: int,
    cache_root: str | Path = DEFAULT_CACHE_ROOT,
) -> list[Path]:
    """Delete snapshots for `page_id` other than `keep_version`.
    Returns the list of deleted paths."""
    deleted: list[Path] = []
    for s in list_snapshots(page_id, cache_root):
        if s.version == keep_version:
            continue
        try:
            s.path.unlink()
            deleted.append(s.path)
        except FileNotFoundError:
            pass
    return deleted
