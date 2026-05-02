"""Manifest — first-class on-disk artifact describing an adopted
Confluence subtree.

A manifest captures the full state of one adopt-tree run:
  - the cloud + space + base URL the tree came from
  - the root page id of the subtree
  - per-page records (id, title, parent, depth, container/leaf flag,
    pinned Confluence content version, planned target path)

Why a first-class artifact:
  - The planner is a pure function over the manifest. Re-rendering the
    on-disk tree from a manifest is deterministic — no Confluence calls.
  - `pull`, `publish`, `promote`, and divergence checks all need the
    same metadata. A single committed manifest is the source of truth;
    the alternative is reading frontmatter from every file and
    reconstructing the tree, which is fragile.
  - Atomic write means partial pulls don't corrupt the manifest — it's
    the LAST step of adopt-tree, after all per-page work has succeeded.

On-disk location: `<staging-root>/<topic-root>/.manifest.json`. The
manifest is committed (not gitignored) — it IS the structural record.

Schema (manifest_version = 1):

    {
      "manifest_version": 1,
      "tool_version": "<change-control version>",
      "cloud_id": "<uuid>",
      "space_key": "<KEY>",
      "base_url": "https://<site>.atlassian.net",
      "root_page_id": "<id>",
      "pulled_at": "YYYY-MM-DD",
      "pages": [
        {
          "id": "<page id>",
          "title": "<page title>",
          "parent_id": "<parent id, '' for root>",
          "depth": 0,
          "child_count": 12,
          "is_container": true,
          "target_path": "<staging-root>/<...>/index.md",
          "confluence_version": 4,
          "imported_at": "YYYY-MM-DD"
        },
        ...
      ]
    }

Project-agnostic: no project-specific names or hard-coded slugs. The
slug rule + module-prefix-strip + version-sibling collapse logic in
`plan_paths` accepts a `slug_rule` callable so callers can plug their
own policy.
"""
from __future__ import annotations

import json
import os
import re
import tempfile
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Callable, Iterable, Optional


MANIFEST_VERSION = 1
MANIFEST_FILENAME = ".manifest.json"


@dataclass
class ManifestPage:
    id: str
    title: str
    parent_id: str = ""
    depth: int = 0
    child_count: int = 0
    is_container: bool = False
    target_path: str = ""
    confluence_version: int = 1
    imported_at: Optional[str] = None

    @classmethod
    def from_dict(cls, d: dict) -> "ManifestPage":
        return cls(
            id=str(d.get("id", "")),
            title=str(d.get("title", "")),
            parent_id=str(d.get("parent_id", "") or ""),
            depth=int(d.get("depth", 0) or 0),
            child_count=int(d.get("child_count", 0) or 0),
            is_container=bool(d.get("is_container", False)),
            target_path=str(d.get("target_path", "") or ""),
            confluence_version=int(d.get("confluence_version", 1) or 1),
            imported_at=d.get("imported_at"),
        )


@dataclass
class Manifest:
    tool_version: str
    cloud_id: str
    space_key: str
    base_url: str
    root_page_id: str
    pulled_at: str
    pages: list[ManifestPage] = field(default_factory=list)
    manifest_version: int = MANIFEST_VERSION

    def to_dict(self) -> dict:
        # Stable key order for deterministic round-trip
        return {
            "manifest_version": self.manifest_version,
            "tool_version": self.tool_version,
            "cloud_id": self.cloud_id,
            "space_key": self.space_key,
            "base_url": self.base_url,
            "root_page_id": self.root_page_id,
            "pulled_at": self.pulled_at,
            "pages": [asdict(p) for p in self.pages],
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Manifest":
        version = int(d.get("manifest_version", MANIFEST_VERSION))
        if version != MANIFEST_VERSION:
            raise ValueError(
                f"unsupported manifest_version={version} "
                f"(this code understands {MANIFEST_VERSION})"
            )
        return cls(
            manifest_version=version,
            tool_version=str(d.get("tool_version", "")),
            cloud_id=str(d.get("cloud_id", "")),
            space_key=str(d.get("space_key", "")),
            base_url=str(d.get("base_url", "")),
            root_page_id=str(d.get("root_page_id", "")),
            pulled_at=str(d.get("pulled_at", "")),
            pages=[ManifestPage.from_dict(p) for p in d.get("pages", [])],
        )


# ---- I/O ----


def read_manifest(path: Path) -> Manifest:
    """Read a manifest from disk. Raises if the file is missing,
    malformed, or carries an unsupported manifest_version."""
    raw = Path(path).read_text(encoding="utf-8")
    return Manifest.from_dict(json.loads(raw))


def write_manifest(path: Path, manifest: Manifest) -> None:
    """Atomic write — serialise to a sibling tmp file then rename.

    Atomicity matters because adopt-tree writes the manifest as its
    LAST step — if the process is killed mid-write, the next run sees
    either the old manifest (intact) or no manifest (must re-pull),
    never a half-written one.
    """
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(manifest.to_dict(), indent=2, ensure_ascii=False) + "\n"
    fd, tmp_name = tempfile.mkstemp(
        prefix=".manifest.", suffix=".tmp", dir=str(target.parent)
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(payload)
        os.replace(tmp_name, target)
    except Exception:
        # Best-effort cleanup
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise


# ---- Slug rule (default) ----


_VERSION_RE = re.compile(
    r"\s*[-–]\s*v?(\d+(?:\.\d+){1,2})\s*$", re.IGNORECASE
)
_VERSION_DOT_RE = re.compile(
    r"\s+v\.?(\d+(?:\.\d+){1,2})\s*$", re.IGNORECASE
)


def default_slugify(s: str, max_len: int = 40) -> str:
    """Default slug rule: lowercase-kebab, ASCII, 40-char soft cap,
    preserve trailing parenthetical disambiguator (e.g., "...(SDP)" →
    "-sdp" appended after the cap). Pure function — no project-specific
    knowledge."""
    s = s.strip()
    paren_suffix = ""
    m = re.search(r"\s*\(([^)]+)\)\s*$", s)
    if m:
        paren_inner = m.group(1).strip()
        paren_slug = re.sub(r"[^a-zA-Z0-9]+", "-", paren_inner).strip("-").lower()
        if paren_slug:
            paren_suffix = "-" + paren_slug
        s = s[: m.start()].strip()
    s = s.lower()
    s = re.sub(r"[\s/\\:]+", "-", s)
    s = re.sub(r"[^a-z0-9._-]+", "", s)
    s = re.sub(r"-+", "-", s).strip("-.")
    if not s:
        s = "page"
    if len(s) > max_len:
        cut = s[:max_len]
        last_dash = cut.rfind("-")
        if last_dash >= 8:
            cut = cut[:last_dash]
        s = cut.rstrip("-.")
    return s + paren_suffix


def strip_prefixes(title: str, prefixes: Iterable[str]) -> str:
    for p in prefixes:
        if title.startswith(p):
            return title[len(p):]
    return title


def is_same_topic(parent_slug: str, child_topic_slug: str) -> bool:
    """Fuzzy parent-IS-topic match.

    Returns True when the two slugs represent the same topic, allowing
    for one to carry a parenthetical disambiguator suffix the other
    doesn't (e.g., parent `vulnerability-assessments-sec` vs child topic
    `vulnerability-assessments` — the parent has the `(SEC)` parenthetical
    that `default_slugify` rendered as `-sec`).

    Match rules (in order):
      1. Exact equality.
      2. Longer slug equals shorter + '-<one-or-more-tokens>' — i.e.,
         the longer slug is the shorter slug plus a kebab-segment suffix
         (the parenthetical-disambiguator form).
    Anything else returns False.

    Pure function — no project-specific knowledge.
    """
    if not parent_slug or not child_topic_slug:
        return False
    if parent_slug == child_topic_slug:
        return True
    longer, shorter = (
        (parent_slug, child_topic_slug)
        if len(parent_slug) > len(child_topic_slug)
        else (child_topic_slug, parent_slug)
    )
    if longer.startswith(shorter + "-"):
        # Bound the suffix length so we don't accidentally collapse
        # genuinely-different topics like
        # `software-security-sec` vs `cybersecurity-measures-and-metrics-sec`
        # (those don't satisfy the prefix rule at all, but the bound is
        # belt-and-braces against future drift).
        suffix = longer[len(shorter) + 1:]
        # Suffix should be one short kebab token (the parenthetical) —
        # multi-token suffixes likely mean different topics.
        # 1–8 chars, no further dashes is the safe envelope; allow up
        # to one internal dash for two-word abbreviations like `mvp-1`.
        if 1 <= len(suffix) <= 12 and suffix.count("-") <= 1:
            return True
    return False


def split_version(title: str) -> tuple[str, str]:
    """Return (topic_title, version). version="" if not versioned."""
    m = _VERSION_RE.search(title)
    if m:
        return title[: m.start()].strip(), m.group(1)
    m2 = _VERSION_DOT_RE.search(title)
    if m2:
        return title[: m2.start()].strip(), m2.group(1)
    return title, ""


# ---- The pure planner ----


SlugRule = Callable[[str], str]


def plan_paths(
    manifest: Manifest,
    *,
    prefixes: list[str],
    staging_root: str,
    slug_rule: SlugRule = default_slugify,
) -> dict[str, str]:
    """Pure function: compute target paths for every page in the
    manifest.

    Rules (locked in tasks 122/123):
      - Root page → `<staging-root>/<root-slug>/index.md`
      - Non-root container (has children) → `<...>/<slug>/index.md`
      - Non-root leaf → `<...>/<slug>.md`
      - Versioned sibling ("Topic - 1.0.0") under a parent that IS the
        topic → `<parent-folder>/v<version>.md` (no redundant subfolder)
      - Versioned sibling under a parent that is NOT the topic →
        `<parent-folder>/<topic-slug>/v<version>.md`

    `prefixes` is the list of module-title prefixes to strip BEFORE
    slugging (so `"<Module> - Software Architecture Document (SAD)"` →
    `"software-architecture-document-sad"`).

    Returns `{page_id: target_path_string}`. Does NOT mutate the
    manifest — caller merges results back in.
    """
    by_id: dict[str, ManifestPage] = {p.id: p for p in manifest.pages}
    children_of: dict[str, list[str]] = {}
    for p in manifest.pages:
        children_of.setdefault(p.parent_id or "", []).append(p.id)

    def has_children(page_id: str) -> bool:
        return bool(children_of.get(page_id))

    # Sort pages by depth so parents are planned before children — that
    # way each child can derive its parent_dir from the parent's already-
    # planned target_path (which correctly accounts for versioned
    # containers becoming `v<N>/index.md` directories).
    pages_by_depth = sorted(manifest.pages, key=lambda p: p.depth)
    out: dict[str, str] = {}

    for p in pages_by_depth:
        title = p.title
        stripped = strip_prefixes(title, prefixes)
        stem, version = split_version(stripped)

        if p.depth == 0 or not p.parent_id:
            slug = slug_rule(stripped) or "product-overview"
            out[p.id] = f"{staging_root}/{slug}/index.md"
            continue

        # Derive the parent's directory from its planned target_path
        # (already computed because we walk by depth ascending).
        parent_path = out.get(p.parent_id)
        if parent_path:
            # If parent's path is `<...>/index.md`, parent's dir is `<...>`.
            # If parent's path is `<...>.md` (a leaf), the parent has no
            # directory — but a leaf wouldn't have children, so this is a
            # bug-class we want to surface explicitly rather than mask.
            if parent_path.endswith("/index.md"):
                prefix_path = parent_path[: -len("/index.md")]
            elif parent_path.endswith(".md"):
                # Parent was planned as a leaf but turns out to have a
                # child — this can happen if children_of was computed
                # before the child's parent_id was known. Fall back to
                # treating the leaf basename as a directory.
                prefix_path = parent_path[: -len(".md")]
            else:
                prefix_path = parent_path
        else:
            # Parent missing from manifest — fall back to recomputed slug.
            prefix_path = staging_root

        if version:
            topic_slug = slug_rule(stem)
            parent = by_id.get(p.parent_id)
            parent_stem_slug = ""
            if parent is not None:
                parent_stripped = strip_prefixes(parent.title, prefixes)
                parent_stem, _ = split_version(parent_stripped)
                if parent_stem:
                    parent_stem_slug = slug_rule(parent_stem)
            # Versioned page that itself has children (e.g.
            # "SDD - 1.0.0" containing design specs) must be a
            # container — `v<N>/index.md`, not `v<N>.md`. Otherwise
            # it's a leaf — `v<N>.md`.
            leaf_or_idx = "index.md" if has_children(p.id) else None
            if parent_stem_slug and is_same_topic(parent_stem_slug, topic_slug):
                # Parent IS the topic container — drop the redundant subfolder.
                # Fuzzy match handles parenthetical-suffix mismatches like
                # `vulnerability-assessments-sec` parent vs
                # `vulnerability-assessments` topic.
                if leaf_or_idx:
                    out[p.id] = f"{prefix_path}/v{version}/index.md"
                else:
                    out[p.id] = f"{prefix_path}/v{version}.md"
            else:
                if leaf_or_idx:
                    out[p.id] = f"{prefix_path}/{topic_slug}/v{version}/index.md"
                else:
                    out[p.id] = f"{prefix_path}/{topic_slug}/v{version}.md"
            continue

        slug = slug_rule(stripped)
        if has_children(p.id):
            out[p.id] = f"{prefix_path}/{slug}/index.md"
        else:
            out[p.id] = f"{prefix_path}/{slug}.md"
    return out


def annotate_pages_with_planned_paths(
    manifest: Manifest,
    *,
    prefixes: list[str],
    staging_root: str,
    slug_rule: SlugRule = default_slugify,
) -> None:
    """In-place: fill `target_path`, `child_count`, `is_container` on
    every ManifestPage by running the planner."""
    children_of: dict[str, int] = {}
    for p in manifest.pages:
        children_of[p.parent_id or ""] = children_of.get(p.parent_id or "", 0) + 1
    paths = plan_paths(
        manifest,
        prefixes=prefixes,
        staging_root=staging_root,
        slug_rule=slug_rule,
    )
    for p in manifest.pages:
        p.child_count = children_of.get(p.id, 0)
        p.is_container = p.child_count > 0
        if p.id in paths:
            p.target_path = paths[p.id]
