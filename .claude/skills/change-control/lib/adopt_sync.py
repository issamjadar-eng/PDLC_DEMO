"""Adopt-direction drift detection (three-way classify).

Mirrors `lib/divergence.py` for the inbound (Confluence → repo) path.

Given:
  - `their_md`     — markdown rendered from the current Confluence page
                     (already normalized via `normalize_for_diff`)
  - the local file at `target_path` (may be absent)
  - the cached snapshot at the local file's `adopted_from_version`
    (the common ancestor — `v_anc`)

Classify the situation as one of:

  - `fresh`        — local file does not yet exist; safe write.
  - `in_sync`      — snapshot == local body == their_md. No-op.
  - `only_theirs`  — local body == snapshot, but Confluence has
                     changed.  Safe overwrite (refresh snapshot).
  - `only_yours`   — local body diverges from snapshot, but
                     Confluence has not changed since `v_anc`.
                     Preserve local edits; bump `adopted_from_version`
                     pointer only.
  - `conflict`     — both sides changed since `v_anc`. Caller decides
                     what to do (overwrite / merge / abort).

The comparison is intentionally between *body* strings only — we never
diff frontmatter (which is local-only metadata and would always differ).

Pure logic in `classify_adopt`; no filesystem access. Callers inject:
  - `read_snapshot(page_id, version)` — see `lib.snapshot.read_snapshot`
  - `read_local_body(target_path)` — return body markdown (no
                                     frontmatter) or None when absent
  - `read_local_anc_version(target_path)` — return the local file's
                                            `confluence.adopted_from_version`
                                            or None when absent

This module also owns the side-by-side conflict-file emission used by
`adopt_helper.py:cmd_write` on conflict (writes
`<doc>.confluence-side.md` + `<doc>.local-diff.md`).
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Literal, Optional

from .divergence import compute_diff, strip_auto_regions


AdoptAction = Literal["fresh", "in_sync", "only_theirs", "only_yours", "conflict"]


@dataclass
class AdoptSyncDecision:
    """Outcome of `classify_adopt`.

    - `action`        — see `AdoptAction` above
    - `reason`        — short human-readable explanation
    - `snapshot_md`   — body at common-ancestor version (None when no
                        snapshot cache entry — e.g., very first adopt
                        of a tree pulled by an older skill version)
    - `their_md`      — current Confluence body markdown (always set)
    - `local_md`      — local file body or None when file is absent
    - `local_anc_version` — the value of `confluence.adopted_from_version`
                        on the local file (None when file absent)
    """

    action: AdoptAction
    reason: str
    snapshot_md: Optional[str]
    their_md: str
    local_md: Optional[str]
    local_anc_version: Optional[int]


SnapshotReader = Callable[[str, int], Optional[str]]
LocalBodyReader = Callable[[Path], Optional[str]]
LocalAncReader = Callable[[Path], Optional[int]]


def classify_adopt(
    target_path: Path,
    page_id: str,
    their_md: str,
    *,
    read_snapshot: SnapshotReader,
    read_local_body: LocalBodyReader,
    read_local_anc_version: LocalAncReader,
) -> AdoptSyncDecision:
    """Three-way classify.

    Decision tree:
      1. local file absent             -> `fresh`
      2. local body == their_md        -> `in_sync` (regardless of snapshot)
      3. snapshot missing              -> `only_theirs` (treat as fresh
                                          overwrite, can't prove a local
                                          edit happened)
      4. local body == snapshot, snapshot != their_md   -> `only_theirs`
      5. local body != snapshot, snapshot == their_md   -> `only_yours`
      6. local body != snapshot, snapshot != their_md   -> `conflict`
    """
    local_md = read_local_body(target_path)
    local_anc_version = read_local_anc_version(target_path)

    if local_md is None:
        return AdoptSyncDecision(
            action="fresh",
            reason="target file does not exist",
            snapshot_md=None,
            their_md=their_md,
            local_md=None,
            local_anc_version=None,
        )

    # Sentinel-aware compare (task 131): auto-rendered regions
    # (CHILD-INDEX, JIRA-LIST, attachments tables) are regenerated
    # deterministically from external state. They MUST NOT count as
    # drift. Strip them on both sides before comparing.
    local_diff_md = strip_auto_regions(local_md)
    their_diff_md = strip_auto_regions(their_md)

    if local_diff_md == their_diff_md:
        return AdoptSyncDecision(
            action="in_sync",
            reason="local body equals current Confluence body (auto regions ignored)",
            snapshot_md=None,
            their_md=their_md,
            local_md=local_md,
            local_anc_version=local_anc_version,
        )

    snapshot_md: Optional[str] = None
    if local_anc_version is not None:
        snapshot_md = read_snapshot(page_id, local_anc_version)

    if snapshot_md is None:
        # No common-ancestor body to compare against — treat as
        # "only theirs". This loses the chance to detect a local edit,
        # but the alternative is to refuse the write, which would block
        # any re-adopt of pages adopted before snapshots existed.
        return AdoptSyncDecision(
            action="only_theirs",
            reason=(
                f"no snapshot at v{local_anc_version} for page {page_id}; "
                f"treating as overwriteable"
            ),
            snapshot_md=None,
            their_md=their_md,
            local_md=local_md,
            local_anc_version=local_anc_version,
        )

    snapshot_diff_md = strip_auto_regions(snapshot_md)
    local_changed = local_diff_md != snapshot_diff_md
    their_changed = snapshot_diff_md != their_diff_md

    if not local_changed and their_changed:
        return AdoptSyncDecision(
            action="only_theirs",
            reason="local body matches snapshot; Confluence has changed",
            snapshot_md=snapshot_md,
            their_md=their_md,
            local_md=local_md,
            local_anc_version=local_anc_version,
        )

    if local_changed and not their_changed:
        return AdoptSyncDecision(
            action="only_yours",
            reason=(
                "local body diverges from snapshot; "
                "Confluence unchanged since common ancestor"
            ),
            snapshot_md=snapshot_md,
            their_md=their_md,
            local_md=local_md,
            local_anc_version=local_anc_version,
        )

    # Both sides changed.
    return AdoptSyncDecision(
        action="conflict",
        reason="both local body and Confluence body changed since common ancestor",
        snapshot_md=snapshot_md,
        their_md=their_md,
        local_md=local_md,
        local_anc_version=local_anc_version,
    )


# ---- I/O helpers (default implementations) ----


def default_read_local_body(target_path: Path) -> Optional[str]:
    """Read the markdown body (without frontmatter) at `target_path`,
    or return None when the file does not exist."""
    if not target_path.is_file():
        return None
    # Lazy import — keeps the module importable in unit tests that
    # provide their own readers.
    from .frontmatter import read as read_frontmatter
    fm = read_frontmatter(target_path)
    return fm.body


def default_read_local_anc_version(target_path: Path) -> Optional[int]:
    """Read `confluence.adopted_from_version` from the local file's
    frontmatter. Returns None when the file is absent or the field is
    missing."""
    if not target_path.is_file():
        return None
    from .frontmatter import read as read_frontmatter
    fm = read_frontmatter(target_path)
    confluence = fm.data.get("confluence") if isinstance(fm.data, dict) else None
    if not isinstance(confluence, dict):
        return None
    val = confluence.get("adopted_from_version")
    try:
        return int(val) if val is not None else None
    except (TypeError, ValueError):
        return None


# ---- Conflict-file emission ----


CONFLICT_SUFFIX_THEIRS = ".confluence-side.md"
CONFLICT_SUFFIX_LOCAL_DIFF = ".local-diff.md"


def conflict_paths(target_path: Path) -> tuple[Path, Path]:
    """Return `(<doc>.confluence-side.md, <doc>.local-diff.md)` paths
    sibling to `target_path`."""
    base = target_path
    # If target ends in `.md`, swap the extension; otherwise append.
    if base.suffix == ".md":
        stem_path = base.with_suffix("")
        their_path = stem_path.with_name(stem_path.name + CONFLICT_SUFFIX_THEIRS)
        diff_path = stem_path.with_name(stem_path.name + CONFLICT_SUFFIX_LOCAL_DIFF)
    else:
        their_path = base.with_name(base.name + CONFLICT_SUFFIX_THEIRS)
        diff_path = base.with_name(base.name + CONFLICT_SUFFIX_LOCAL_DIFF)
    return their_path, diff_path


def write_conflict_files(
    target_path: Path,
    decision: AdoptSyncDecision,
    *,
    page_id: str,
) -> tuple[Path, Path]:
    """Emit `<doc>.confluence-side.md` (their_md verbatim) and
    `<doc>.local-diff.md` (unified diff snapshot vs local). Returns
    the two paths written. Caller is responsible for the prompt."""
    their_path, diff_path = conflict_paths(target_path)
    their_path.parent.mkdir(parents=True, exist_ok=True)
    their_path.write_text(decision.their_md, encoding="utf-8")
    snapshot = decision.snapshot_md or ""
    local = decision.local_md or ""
    anc_label = (
        f"snapshot@v{decision.local_anc_version}"
        if decision.local_anc_version is not None
        else "snapshot"
    )
    diff = compute_diff(
        snapshot,
        local,
        from_label=anc_label,
        to_label="local-current",
    )
    if not diff:
        diff = "(no diff — local body matches snapshot)\n"
    header = (
        f"# local-vs-snapshot diff for page {page_id}\n"
        f"# {decision.reason}\n\n"
    )
    diff_path.write_text(header + diff, encoding="utf-8")
    return their_path, diff_path


# ---- Structured prompt rendering ----


def render_conflict_prompt(
    target_path: Path,
    decision: AdoptSyncDecision,
    *,
    page_id: str,
    their_path: Path,
    diff_path: Path,
) -> str:
    """Render the structured stderr prompt the agent reads on conflict.

    Single multi-line block, machine-parseable header line first
    (`CHANGE_CONTROL_ADOPT_CONFLICT page_id=<id> target=<path>`) so
    downstream automation can grep without regexing prose.
    """
    lines = [
        f"CHANGE_CONTROL_ADOPT_CONFLICT page_id={page_id} target={target_path}",
        f"  reason: {decision.reason}",
        f"  their (Confluence) body: {their_path}",
        f"  local-vs-snapshot diff:  {diff_path}",
        "  options:",
        "    overwrite — accept Confluence body, lose local edits",
        "                (re-run with --on-conflict overwrite or --force)",
        "    merge     — leave both side-by-side files; user reconciles by hand",
        "                (default; this is what just happened)",
        "    abort     — leave the local file untouched",
        "                (re-run with --on-conflict abort)",
    ]
    return "\n".join(lines)
