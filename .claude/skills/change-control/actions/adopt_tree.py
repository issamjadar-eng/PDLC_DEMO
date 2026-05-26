"""`change-control adopt-tree` — bulk-adopt every descendant of a root
Confluence page using the JSON-directive MCP bridge (Option B).

Usage:

    python actions/adopt_tree.py \
        --root-page-id <root-page-id> \
        --base-url https://<your-site>.atlassian.net \
        --space-key <SPACE> \
        --target-root docs/confluence-staging/<SPACE> \
        --cache-root docs/.change-control \
        [--max-depth N] [--dry-run] [--fixture <path-to-json>]

The action emits MCP-call directives on fd 3 and reads results on fd 4
(the `lib.mcp_bridge.StreamMCPProxy` protocol). The agent shim wires
those streams up before invoking the script. For tests + offline
development, pass `--fixture <path>` to drive the script from a
captured response map (JSON file mapping `tool:argshash` -> result, or
a list of `{tool, args, result}` records).

Algorithm:

  1. Resolve cloudId via `getAccessibleAtlassianResources`.
  2. Walk the tree via `getConfluencePageDescendants(pageId=ROOT)`,
     producing a flat list of pages (the root + every descendant).
  3. For each page, fetch ADF via `getConfluencePage(adf)`, normalize,
     write to `<target-root>/<page-path>/<slug>.md`, write the
     snapshot, and record progress.
  4. Topic+versions pattern: when a parent page has versioned children
     ("X - 1.0.0", "X - 2.0.0", ...), produce
     `<topic>/index.md` for the parent and `<topic>/v1.0.0.md`,
     `<topic>/v2.0.0.md`, ... for each version. Each is a first-class
     adopted file (versions are concurrent workstreams, not history).
  5. On completion, print a summary: total adopted / topics / versions
     / extensions encountered / smartlinks / failed pages.

This action does NOT do attachment download in v0.6 — single-page
`adopt` keeps images as Confluence URLs; `adopt-tree` follows the same
policy. Image ingestion is a separate `--with-images` flag (deferred —
needs the cookie-auth attachment downloader, separate scope).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

SKILL_ROOT = Path(__file__).resolve().parent.parent
ACTIONS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SKILL_ROOT))
sys.path.insert(0, str(ACTIONS_DIR))

from lib.adopt_sync import (  # noqa: E402
    classify_adopt,
    default_read_local_anc_version,
    default_read_local_body,
    render_conflict_prompt,
    write_conflict_files,
)
from lib.confluence_mcp import ConfluenceMCP  # noqa: E402
from lib.frontmatter import update as update_frontmatter  # noqa: E402
from lib.frontmatter import write as write_frontmatter  # noqa: E402
from lib.manifest import (  # noqa: E402
    MANIFEST_FILENAME,
    Manifest,
    ManifestPage,
    read_manifest,
    write_manifest,
)
from lib.mcp_bridge import (  # noqa: E402
    BridgeError,
    FixtureMCPProxy,
    StreamMCPProxy,
    open_default_streams,
)
from lib.normalizer import NormalizationReport, adf_to_markdown  # noqa: E402
from lib.snapshot import read_snapshot, write_snapshot  # noqa: E402

# Reuse adopt_helper's normalizer + frontmatter builder
from adopt_helper import build_frontmatter, normalize  # noqa: E402


# ---- Types ----


@dataclass
class AdoptResult:
    page_id: str
    title: str
    target: Path
    version: int
    extensions: int = 0
    media: int = 0
    smart_links: int = 0
    zones: list[str] = field(default_factory=list)
    error: str = ""


# ---- Path planning ----


# Topic+versions pattern: matches "Topic name - 1.0.0" / "Topic - v1.0.0"
_VERSION_SUFFIX_RE = re.compile(
    r"\s*[-–]\s*v?(?P<version>\d+(?:\.\d+){1,2})\s*$",
    re.IGNORECASE,
)


def _slugify(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"[\s/\\]+", "-", s)
    s = re.sub(r"[^a-z0-9._-]+", "", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s or "page"


@dataclass
class TopicSplit:
    """Result of analyzing a page title for topic+version pattern."""

    is_versioned: bool
    topic: str  # the slug for the topic folder (or page slug if not versioned)
    version: str  # "1.0.0" if versioned, else ""


def split_topic_version(title: str) -> TopicSplit:
    """If `title` matches the topic+version pattern, return the split.
    Otherwise return `(False, slug(title), "")`."""
    m = _VERSION_SUFFIX_RE.search(title)
    if m is None:
        return TopicSplit(is_versioned=False, topic=_slugify(title), version="")
    topic = title[: m.start()].strip()
    version = m.group("version")
    return TopicSplit(is_versioned=True, topic=_slugify(topic), version=version)


def plan_target_paths(
    pages: list[dict], target_root: Path, root_page_id: str
) -> dict[str, Path]:
    """Plan the target path for every page in the tree at once.

    Two-pass: first identify which pages are "topic parents" (their
    children include versioned siblings); then plan paths.

      - Versioned page  -> `<parent's parent dir>/<parent slug>/v<version>.md`
      - Topic-parent    -> `<parent dir>/<page slug>/index.md`
      - Plain page      -> `<parent dir>/<page slug>.md`

    `<parent dir>` is the slugified ancestor-title chain (excluding
    the page itself, stopping at root_page_id).
    """
    by_id: dict[str, dict] = {
        str(p.get("id") or p.get("pageId")): p for p in pages
    }

    def parent_id(p: dict) -> str:
        return str(p.get("parentId") or "")

    def ancestor_chain(p: dict) -> list[dict]:
        chain: list[dict] = []
        current = p
        while True:
            pid = parent_id(current)
            if not pid or pid == root_page_id:
                break
            parent = by_id.get(pid)
            if parent is None:
                break
            chain.insert(0, parent)
            current = parent
        return chain

    # Pass 1 — find topic parents (parents that have at least one versioned child)
    topic_parents: set[str] = set()
    for p in pages:
        split = split_topic_version(str(p.get("title", "")))
        if split.is_versioned:
            ppid = parent_id(p)
            if ppid in by_id:
                topic_parents.add(ppid)

    # Pass 2 — plan paths
    out: dict[str, Path] = {}
    for p in pages:
        pid = str(p.get("id") or p.get("pageId"))
        title = str(p.get("title", "untitled"))
        chain = ancestor_chain(p)
        parent_dir = target_root / Path(*[_slugify(str(a.get("title", ""))) for a in chain])
        split = split_topic_version(title)

        if split.is_versioned and parent_id(p) in topic_parents:
            # Place under the parent's slug folder; that folder is sibling
            # to the parent page's index.md. The parent's directory is
            # `target_root / Path(*ancestors_of_parent)`.
            parent_chain = chain[:-1] if chain else []
            parent_parent_dir = target_root / Path(
                *[_slugify(str(a.get("title", ""))) for a in parent_chain]
            )
            parent_page = by_id[parent_id(p)]
            topic_slug = _slugify(str(parent_page.get("title", "")))
            out[pid] = parent_parent_dir / topic_slug / f"v{split.version}.md"
            continue

        if pid in topic_parents:
            out[pid] = parent_dir / _slugify(title) / "index.md"
            continue

        out[pid] = parent_dir / f"{_slugify(title)}.md"
    return out


# ---- Tree walking ----


def collect_pages(
    mcp: ConfluenceMCP, root_page_id: str, max_depth: int | None
) -> list[dict]:
    """Fetch the root page + all descendants. Returns a flat list of
    page records ordered by depth (root first)."""
    root = mcp._call(
        "getConfluencePage",
        cloudId=mcp.cloud_id,
        pageId=root_page_id,
        contentFormat="adf",
    )
    pages: list[dict] = [root]
    # Always pass an explicit depth — the MCP tool's default truncates
    # at depth=2 with no warning (observed) and silently drops anything
    # deeper. Use the paginator so cursor-paginated trees aren't
    # truncated either. See lib/confluence_mcp.py:get_descendants_paginated.
    effective_depth = max_depth if max_depth is not None else 10
    descendants = mcp.get_descendants_paginated(
        root_page_id, depth=effective_depth
    )
    for d in descendants:
        if not isinstance(d, dict) or not d.get("id"):
            continue
        # Some MCP responses give back a slim record without ADF body;
        # fetch full body in a separate call.
        full = mcp._call(
            "getConfluencePage",
            cloudId=mcp.cloud_id,
            pageId=str(d["id"]),
            contentFormat="adf",
        )
        if isinstance(full, dict):
            pages.append(full)
    return pages


# ---- Adopt one page ----


def adopt_one(
    page: dict,
    *,
    target: Path,
    base_url: str,
    space_key: str,
    parent_page_id: str,
    page_path: str,
    cache_root: str,
    adopted_at: str,
) -> AdoptResult:
    md, report = normalize(page, base_url)
    fm = build_frontmatter(
        page,
        space_key=space_key,
        parent_page_id=parent_page_id,
        page_path=page_path,
        adopted_at=adopted_at,
    )
    write_frontmatter(target, fm, md)
    write_snapshot(
        page_id=str(fm["confluence"]["page_id"]),
        version=int(fm["confluence"]["last_published_version"]),
        markdown=md,
        cache_root=cache_root,
    )
    return AdoptResult(
        page_id=str(fm["confluence"]["page_id"]),
        title=str(fm["title"]),
        target=target,
        version=int(fm["confluence"]["last_published_version"]),
        extensions=len(report.extensions),
        media=len(report.media_refs),
        smart_links=len(report.smart_links),
        zones=list(report.zones),
    )


# ---- CLI ----


def _today_utc() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="change-control adopt-tree",
        description="Bulk-adopt a Confluence page tree via the MCP bridge.",
    )
    p.add_argument("--root-page-id", required=True)
    p.add_argument(
        "--base-url",
        default="",
        help="Defaults to project.yml `change_control.base_url`.",
    )
    p.add_argument(
        "--space-key",
        default="",
        help="Defaults to project.yml `change_control.spaces[]` (when only "
             "one space is configured).",
    )
    p.add_argument(
        "--target-root",
        default="",
        help="Defaults to the configured space's `staging_target_root`.",
    )
    p.add_argument("--cache-root", default="docs/.change-control")
    p.add_argument("--max-depth", type=int, default=None)
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Plan + print the target paths without writing files. "
             "Compatible with --refresh for a categorize-only summary.",
    )
    p.add_argument(
        "--refresh",
        action="store_true",
        help="Incremental sync mode. Requires an existing "
             "<target-root>/<topic>/.manifest.json. Re-discovers the "
             "Confluence subtree, diffs against the manifest, and only "
             "re-adopts pages whose Confluence version has advanced. "
             "Local edits are preserved (only_yours classification); "
             "real conflicts emit side-by-side files + non-zero exit.",
    )
    p.add_argument(
        "--on-conflict",
        choices=("prompt", "overwrite", "abort", "merge"),
        default="prompt",
        help="On a per-page conflict in --refresh mode, what to do. "
             "Same semantics as adopt_helper write --on-conflict.",
    )
    p.add_argument(
        "--manifest-path",
        default="",
        help="Override the manifest path. Defaults to "
             "<target-root>/.manifest.json. Used by --refresh to read the "
             "old manifest and to write the new one on success.",
    )
    p.add_argument(
        "--fixture",
        default="",
        help="Path to a fixture JSON file. Each line is "
             '`{"tool": "...", "args": {...}, "result": ...}`. Used by tests + '
             "offline dev.",
    )
    p.add_argument(
        "--adopted-at",
        default="",
        help="Override the adoption date (default: today UTC).",
    )
    return p


def _load_fixture(path: Path) -> Callable[[str, dict], Any]:
    """Load a fixture file (line-delimited JSON, each line a record).
    Match by `tool` + `args` (exact dict equality)."""
    records: list[dict] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            records.append(json.loads(line))

    def lookup(tool: str, args: dict) -> Any:
        for r in records:
            if r.get("tool") != tool:
                continue
            if r.get("args") == args:
                return r.get("result")
        # Fall back: match by tool only if there's a single record
        # for that tool.
        matches = [r for r in records if r.get("tool") == tool]
        if len(matches) == 1:
            return matches[0].get("result")
        raise BridgeError(
            f"fixture: no record for tool={tool!r} args={args!r}"
        )

    return lookup


# ---- Refresh-mode helpers (task 130) ----


def _ancestor_titles(by_id: dict[str, dict], page: dict, root_page_id: str) -> list[str]:
    """Top-level version of the closure inside run() — for refresh use."""
    chain: list[str] = []
    current = page
    while True:
        pid = current.get("parentId") or ""
        if not pid or pid == root_page_id:
            break
        parent = by_id.get(str(pid))
        if parent is None:
            break
        chain.insert(0, str(parent.get("title", "")))
        current = parent
    return chain


def _build_manifest_from_pages(
    old_manifest: Manifest,
    new_pages: list[dict],
    target_paths: dict[str, Path],
    pulled_at: str,
) -> Manifest:
    """Build a fresh manifest from the discovered new pages, preserving
    cloud_id / space_key / base_url / root from the old manifest."""
    pages: list[ManifestPage] = []
    for record in new_pages:
        pid = str(record.get("id") or record.get("pageId"))
        if not pid:
            continue
        version_section = record.get("version") or {}
        try:
            v = int(
                version_section.get("number")
                if isinstance(version_section, dict)
                else version_section or 1
            )
        except (TypeError, ValueError):
            v = 1
        target = target_paths.get(pid, Path(""))
        pages.append(ManifestPage(
            id=pid,
            title=str(record.get("title") or ""),
            parent_id=str(record.get("parentId") or ""),
            depth=0,  # depth not tracked in the discovered records
            child_count=0,
            is_container=False,
            target_path=str(target) if target.parts else "",
            confluence_version=v,
            imported_at=pulled_at,
        ))
    return Manifest(
        manifest_version=old_manifest.manifest_version,
        tool_version=old_manifest.tool_version,
        cloud_id=old_manifest.cloud_id,
        space_key=old_manifest.space_key,
        base_url=old_manifest.base_url,
        root_page_id=old_manifest.root_page_id,
        pulled_at=pulled_at,
        pages=pages,
    )


# ---- Refresh-mode categorization (task 130) ----


@dataclass
class RefreshCategory:
    """One category bucket for `--refresh` planning."""

    page_id: str
    title: str
    target: Path
    old_version: int = 0
    new_version: int = 0
    reason: str = ""


@dataclass
class RefreshPlan:
    in_sync: list[RefreshCategory] = field(default_factory=list)
    only_yours_pending: list[RefreshCategory] = field(default_factory=list)
    upstream_changed: list[RefreshCategory] = field(default_factory=list)
    added: list[RefreshCategory] = field(default_factory=list)
    removed: list[RefreshCategory] = field(default_factory=list)
    predicted_conflict: list[RefreshCategory] = field(default_factory=list)

    def render_summary(self) -> str:
        lines = [
            "adopt-tree --refresh plan:",
            f"  in_sync:           {len(self.in_sync):>4}",
            f"  only_yours_pending:{len(self.only_yours_pending):>4}  "
            "(local edits, no upstream change — preserved)",
            f"  upstream_changed:  {len(self.upstream_changed):>4}  "
            "(drift detection runs per-page)",
            f"  added:             {len(self.added):>4}  (new pages)",
            f"  removed:           {len(self.removed):>4}  "
            "(upstream removed; consider deleting locally)",
            f"  predicted_conflict:{len(self.predicted_conflict):>4}  "
            "(both sides changed since v_anc)",
        ]
        if self.removed:
            lines.append("")
            lines.append("removed pages (NOT auto-deleted):")
            for r in self.removed[:20]:
                lines.append(f"  - {r.page_id} {r.title}  ({r.target})")
            if len(self.removed) > 20:
                lines.append(f"  ... and {len(self.removed) - 20} more")
        return "\n".join(lines)


def categorize_refresh(
    old_manifest: Manifest,
    new_pages: list[dict],
    target_paths: dict[str, Path],
    *,
    cache_root: str,
    read_local_body=default_read_local_body,
    read_local_anc_version=default_read_local_anc_version,
    read_snapshot_fn=read_snapshot,
) -> RefreshPlan:
    """Pure categorization of a refresh: diff old manifest vs new pages.

    `target_paths` is the planned target_path map for `new_pages` (from
    `plan_target_paths`). For pages also in the old manifest, the
    target_path comes from the old record (preserves any earlier
    promotion / rename) — we use new only for pages not in old.

    For `upstream_changed` candidates, we additionally inspect the
    local file body + snapshot to predict conflicts BEFORE running
    full adoption. That lets the dry-run summary distinguish "12 pages
    will safely re-adopt" from "3 pages will require user attention".
    """
    plan = RefreshPlan()
    old_by_id = {p.id: p for p in old_manifest.pages}
    new_by_id: dict[str, dict] = {
        str(p.get("id") or p.get("pageId")): p for p in new_pages
    }

    # Pages in both sets
    for pid, old_page in old_by_id.items():
        new_record = new_by_id.get(pid)
        target = Path(old_page.target_path) if old_page.target_path else target_paths.get(pid, Path(""))
        if new_record is None:
            plan.removed.append(RefreshCategory(
                page_id=pid,
                title=old_page.title,
                target=target,
                old_version=old_page.confluence_version,
                reason="upstream removed",
            ))
            continue
        v_old = old_page.confluence_version
        version_section = new_record.get("version") or {}
        try:
            v_new = int(version_section.get("number") if isinstance(version_section, dict) else version_section or 1)
        except (TypeError, ValueError):
            v_new = 1
        title = str(new_record.get("title") or old_page.title)

        if v_new > v_old:
            # Confluence advanced. Predict conflict by classifying without
            # actually rendering the new ADF — we don't need their_md to
            # tell whether the LOCAL body diverges from the snapshot at
            # v_old (snapshot vs local comparison is independent of
            # their_md). If snapshot is missing or local matches snapshot,
            # this is `upstream_changed`. If local diverges from snapshot,
            # this is `predicted_conflict`.
            local_body = read_local_body(target)
            snapshot_md = read_snapshot_fn(pid, v_old, cache_root=cache_root)
            entry = RefreshCategory(
                page_id=pid,
                title=title,
                target=target,
                old_version=v_old,
                new_version=v_new,
            )
            if local_body is None or snapshot_md is None or local_body == snapshot_md:
                entry.reason = f"v{v_old} -> v{v_new}, local matches snapshot"
                plan.upstream_changed.append(entry)
            else:
                entry.reason = (
                    f"v{v_old} -> v{v_new}, local diverges from snapshot — "
                    f"will go through conflict prompt"
                )
                plan.predicted_conflict.append(entry)
            continue

        # No upstream version delta.
        local_body = read_local_body(target)
        snapshot_md = read_snapshot_fn(pid, v_old, cache_root=cache_root)
        entry = RefreshCategory(
            page_id=pid,
            title=title,
            target=target,
            old_version=v_old,
            new_version=v_new,
        )
        if local_body is None:
            # Local file was deleted but Confluence and manifest still
            # know about it — treat as upstream_changed so a fresh write
            # restores the file.
            entry.reason = "local file missing; will re-adopt to restore"
            plan.upstream_changed.append(entry)
        elif snapshot_md is None or local_body == snapshot_md:
            entry.reason = f"v{v_old} unchanged; local matches snapshot"
            plan.in_sync.append(entry)
        else:
            entry.reason = (
                f"v{v_old} unchanged; local diverges from snapshot "
                f"(local-only edit preserved)"
            )
            plan.only_yours_pending.append(entry)

    # Pages added upstream
    for pid, new_record in new_by_id.items():
        if pid in old_by_id:
            continue
        title = str(new_record.get("title") or "")
        version_section = new_record.get("version") or {}
        try:
            v_new = int(version_section.get("number") if isinstance(version_section, dict) else version_section or 1)
        except (TypeError, ValueError):
            v_new = 1
        target = target_paths.get(pid, Path(""))
        plan.added.append(RefreshCategory(
            page_id=pid,
            title=title,
            target=target,
            new_version=v_new,
            reason="new upstream page",
        ))

    return plan


# ---- Main ----


def run(args: argparse.Namespace) -> int:
    if args.fixture:
        proxy = FixtureMCPProxy(_load_fixture(Path(args.fixture)))
    else:
        d, r = open_default_streams()
        proxy = StreamMCPProxy(d, r)

    mcp = ConfluenceMCP(proxy, base_url=args.base_url)
    target_root = Path(args.target_root)
    adopted_at = args.adopted_at or _today_utc()

    pages = collect_pages(mcp, args.root_page_id, args.max_depth)
    print(f"adopt-tree: collected {len(pages)} pages from root {args.root_page_id}", file=sys.stderr)

    by_id: dict[str, dict] = {str(p.get("id") or p.get("pageId")): p for p in pages}
    paths = plan_target_paths(pages, target_root, args.root_page_id)

    # ---- Refresh-mode short-circuit (task 130) ----
    if getattr(args, "refresh", False):
        manifest_path = (
            Path(args.manifest_path) if args.manifest_path
            else target_root / MANIFEST_FILENAME
        )
        if not manifest_path.is_file():
            print(
                f"adopt-tree --refresh: required manifest not found at "
                f"{manifest_path}. Run a full adopt-tree first to seed it.",
                file=sys.stderr,
            )
            return 64
        try:
            old_manifest = read_manifest(manifest_path)
        except Exception as exc:  # noqa: BLE001
            print(f"adopt-tree --refresh: cannot read manifest: {exc}", file=sys.stderr)
            return 65
        plan = categorize_refresh(
            old_manifest,
            pages,
            paths,
            cache_root=args.cache_root,
        )
        print()
        print(plan.render_summary())
        print()
        if args.dry_run:
            print("adopt-tree --refresh --dry-run: no I/O performed.")
            return 0

        # Live refresh: process upstream_changed + added with drift detection.
        actions_taken: list[str] = []
        conflicts_remaining: list[RefreshCategory] = []
        for entry in plan.added + plan.upstream_changed + plan.predicted_conflict:
            page_record = by_id.get(entry.page_id)
            if page_record is None:
                continue
            target = entry.target if entry.target.parts else paths.get(entry.page_id, Path(""))
            if not target.parts:
                continue
            md, report = normalize(page_record, args.base_url)
            fm = build_frontmatter(
                page_record,
                space_key=args.space_key,
                parent_page_id=str(page_record.get("parentId") or ""),
                page_path=" / ".join(_ancestor_titles(by_id, page_record, args.root_page_id) + [str(page_record.get("title", ""))]),
                adopted_at=adopted_at,
            )
            page_id_str = str(fm["confluence"]["page_id"])

            decision = classify_adopt(
                target,
                page_id_str,
                md,
                read_snapshot=lambda pid, ver: read_snapshot(
                    pid, ver, cache_root=args.cache_root
                ),
                read_local_body=default_read_local_body,
                read_local_anc_version=default_read_local_anc_version,
            )

            if decision.action == "in_sync":
                actions_taken.append(f"  IN_SYNC    {page_id_str:>12}  {entry.title}")
                continue
            if decision.action == "only_yours":
                new_version = int(fm["confluence"]["last_published_version"])
                update_frontmatter(
                    target,
                    confluence={
                        "adopted_from_version": new_version,
                        "last_published_version": new_version,
                    },
                )
                actions_taken.append(
                    f"  ONLY_YOURS {page_id_str:>12}  {entry.title} "
                    f"(local edits preserved, fm pointer -> v{new_version})"
                )
                continue
            if decision.action == "conflict":
                if args.on_conflict == "overwrite":
                    write_frontmatter(target, fm, md)
                    write_snapshot(
                        page_id=page_id_str,
                        version=int(fm["confluence"]["last_published_version"]),
                        markdown=md,
                        cache_root=args.cache_root,
                    )
                    actions_taken.append(
                        f"  OVERWRITE  {page_id_str:>12}  {entry.title} (conflict, --on-conflict=overwrite)"
                    )
                elif args.on_conflict == "abort":
                    actions_taken.append(
                        f"  ABORT      {page_id_str:>12}  {entry.title} (conflict, --on-conflict=abort, untouched)"
                    )
                    conflicts_remaining.append(entry)
                else:
                    their_path, diff_path = write_conflict_files(target, decision, page_id=page_id_str)
                    prompt = render_conflict_prompt(target, decision, page_id=page_id_str, their_path=their_path, diff_path=diff_path)
                    print(prompt, file=sys.stderr)
                    actions_taken.append(
                        f"  CONFLICT   {page_id_str:>12}  {entry.title} (side-by-side files written)"
                    )
                    conflicts_remaining.append(entry)
                continue
            # `fresh` or `only_theirs` — safe write.
            write_frontmatter(target, fm, md)
            write_snapshot(
                page_id=page_id_str,
                version=int(fm["confluence"]["last_published_version"]),
                markdown=md,
                cache_root=args.cache_root,
            )
            verb = "FRESH     " if decision.action == "fresh" else "ONLY_THRS "
            actions_taken.append(f"  {verb}{page_id_str:>12}  {entry.title} -> {target}")

        # Print log + summary
        for line in actions_taken:
            print(line)
        print()
        print(f"adopt-tree --refresh complete:")
        print(f"  actions: {len(actions_taken)}")
        print(f"  conflicts requiring user attention: {len(conflicts_remaining)}")
        if plan.removed:
            print(f"  removed pages NOT auto-deleted: {len(plan.removed)} "
                  f"(see plan summary above)")

        # Rewrite manifest at the end on success — only if no unresolved conflicts.
        if not conflicts_remaining:
            new_manifest = _build_manifest_from_pages(
                old_manifest, pages, paths, adopted_at
            )
            write_manifest(manifest_path, new_manifest)
            print(f"  manifest rewritten: {manifest_path}")
        else:
            print(
                f"  manifest NOT rewritten — resolve {len(conflicts_remaining)} "
                f"conflict(s) and re-run, or pass --on-conflict overwrite/abort"
            )
        return 1 if conflicts_remaining else 0

    def ancestor_titles(page: dict) -> list[str]:
        chain: list[str] = []
        current = page
        while True:
            pid = current.get("parentId") or ""
            if not pid or pid == args.root_page_id:
                break
            parent = by_id.get(str(pid))
            if parent is None:
                break
            chain.insert(0, str(parent.get("title", "")))
            current = parent
        return chain

    results: list[AdoptResult] = []
    failed: list[tuple[str, str]] = []

    for page in pages:
        title = str(page.get("title", ""))
        page_id = str(page.get("id") or page.get("pageId") or "")
        target = paths[page_id]
        if args.dry_run:
            print(f"  PLAN  {page_id:>12}  {title}  ->  {target}")
            continue
        try:
            res = adopt_one(
                page,
                target=target,
                base_url=args.base_url,
                space_key=args.space_key,
                parent_page_id=str(page.get("parentId") or ""),
                page_path=" / ".join(ancestor_titles(page) + [title]),
                cache_root=args.cache_root,
                adopted_at=adopted_at,
            )
            results.append(res)
            print(f"  ADOPT {res.page_id:>12} v{res.version}  {res.title}  ->  {res.target}")
        except Exception as exc:
            failed.append((page_id, str(exc)))
            print(f"  FAIL  {page_id:>12}  {title}: {exc}", file=sys.stderr)

    # Summary
    if not args.dry_run:
        topics = sum(1 for r in results if r.target.parent.name and r.target.name == "index.md")
        versions = sum(1 for r in results if r.target.name.startswith("v") and r.target.name != "index.md")
        total_zones = sum(len(r.zones) for r in results)
        total_ext = sum(r.extensions for r in results)
        total_media = sum(r.media for r in results)
        total_links = sum(r.smart_links for r in results)
        print()
        print("adopt-tree summary:")
        print(f"  pages adopted:   {len(results)} / {len(pages)}")
        print(f"  versioned files: {versions}")
        print(f"  index files:     {topics}")
        print(f"  zones found:     {total_zones}")
        print(f"  extensions:      {total_ext}")
        print(f"  media refs:      {total_media}")
        print(f"  smart links:     {total_links}")
        if failed:
            print(f"  FAILED:          {len(failed)}")
            for pid, err in failed[:5]:
                print(f"    {pid}: {err}")
    return 1 if failed and not args.dry_run else 0


def _apply_config_defaults(args: argparse.Namespace) -> None:
    """Fill --base-url / --space-key / --target-root from project.yml when
    blank. CLI flags continue to override.
    """
    try:
        from lib.config import read_change_control_config  # noqa: WPS433
    except ImportError:
        return
    try:
        cfg = read_change_control_config()
    except Exception:  # noqa: BLE001
        return
    if not getattr(args, "base_url", "") and cfg.base_url:
        args.base_url = cfg.base_url
    if not getattr(args, "space_key", "") and len(cfg.spaces) == 1:
        args.space_key = cfg.spaces[0].key
    if not getattr(args, "target_root", ""):
        space = (
            cfg.space_by_key(args.space_key)
            if getattr(args, "space_key", "")
            else (cfg.spaces[0] if len(cfg.spaces) == 1 else None)
        )
        if space and space.staging_target_root:
            args.target_root = space.staging_target_root


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    _apply_config_defaults(args)
    missing = [
        name for name in ("base_url", "space_key", "target_root")
        if not getattr(args, name, "")
    ]
    if missing:
        print(
            "adopt_tree: missing required args (and not in project.yml): "
            + ", ".join("--" + m.replace("_", "-") for m in missing),
            file=sys.stderr,
        )
        return 64
    return run(args)


if __name__ == "__main__":
    sys.exit(main())
