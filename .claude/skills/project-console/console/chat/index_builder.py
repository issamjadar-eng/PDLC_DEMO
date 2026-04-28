"""Project README index — the Tier 3 grounding catalog.

Concatenates every `<root>/**/README.md` (for each configured root) in
tree order into one string that is inlined in the assistant drawer's
system prompt. Agents scan this index to discover what content exists
in the project + any exposed skill reference folders, and then call the
`read_files` tool to fetch specific `.md` files on demand.

Design notes:
  - READMEs are human-authored and version-controlled; no LLM summarization.
  - Grounding roots come from `config.grounding_roots` — the project's
    docs tree by default, extended with any `grounding.extra_roots` entries
    in `console.yaml` (e.g. `.claude/skills/medtech-docs/references` for
    skill-embedded distilled standards + guidance).
  - Exclusion patterns check segments BELOW the grounding root, so
    `source` / `source-md` / `formal` / `images` / `.staging` segments
    inside a skill reference tree are skipped without affecting the
    explicit `docs/internal/source-md` root.
  - Startup scan is <20 ms; no cache complexity. An admin endpoint
    triggers a rebuild on demand.
  - Missing-README warnings expose folder-coverage gaps.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from console.config import get_config

# Path-segment names that — when they appear BELOW a grounding root —
# exclude that file or folder from the grounding surface. The check is
# root-relative, so `docs/internal/source-md/*` (explicit root) is fine.
#   source     — pre-conversion originals (DOCX, PDF) — NOT markdown
#   formal     — post-conversion formal exports (DOCX, PDF) — NOT markdown
#   images     — extracted images referenced from markdown
#   .staging   — work-in-progress conversion scratch
#
# `source-md/` is intentionally NOT excluded: it holds full-text markdown
# conversions of FDA guidance and similar source documents. Agents need
# to reach these for clause-level citations with hyperlinks.
_EXCLUDE_SEGMENTS = frozenset({"source", "formal", "images", ".staging"})

# Segments that should NOT generate a "missing README" coverage warning
# when they lack their own README.md. These folders are bulk-conversion
# trees (one markdown file per source doc, no curated index); they're
# still groundable but don't need per-folder scope framing.
_COVERAGE_SKIP_SEGMENTS = frozenset({"source-md"})


@dataclass(frozen=True)
class IndexResult:
    text: str
    readme_count: int
    total_bytes: int
    missing_readme_folders: list[str]


def _resolve_roots(repo_root: Path) -> list[tuple[str, Path]]:
    """Return the configured grounding roots as (relative, absolute) pairs
    that exist on disk. Order is preserved from config.
    """
    out: list[tuple[str, Path]] = []
    for rel in get_config().grounding_roots:
        p = (repo_root / rel)
        if p.exists() and p.is_dir():
            out.append((rel, p))
    return out


def _is_excluded_under_root(path: Path, root_abs: Path) -> bool:
    """True if `path` contains an excluded segment BELOW `root_abs`.

    Exclusion is root-relative: `.staging` inside the root is skipped,
    but `root_abs` itself or its own ancestor segments are not checked.
    """
    try:
        rel = path.relative_to(root_abs)
    except ValueError:
        # Not under this root — treat as excluded so callers err conservatively.
        return True
    return any(seg in _EXCLUDE_SEGMENTS for seg in rel.parts)


def _path_is_groundable(path: Path, repo_root: Path) -> bool:
    """True if `path` is under any configured grounding root AND not excluded
    by that root's segment rules.
    """
    for _rel, abs_root in _resolve_roots(repo_root):
        try:
            path.relative_to(abs_root)
        except ValueError:
            continue
        return not _is_excluded_under_root(path, abs_root)
    return False


def _list_readmes(repo_root: Path) -> list[Path]:
    out: list[Path] = []
    for _rel, abs_root in _resolve_roots(repo_root):
        for p in sorted(abs_root.rglob("README.md")):
            if _is_excluded_under_root(p, abs_root):
                continue
            out.append(p)
    return out


def _find_missing_readme_folders(repo_root: Path) -> list[str]:
    """Walk each grounding root and report any folder that contains .md
    working content but no README.md. These are index blind spots — the
    agent will see files under them via `read_files` only if it guesses a
    path, never via the index. `_COVERAGE_SKIP_SEGMENTS` folders (e.g.
    bulk-conversion `source-md/` trees) are groundable but exempt from
    coverage warnings since they're not meant to have curated READMEs.
    """
    missing: list[str] = []
    for _rel, abs_root in _resolve_roots(repo_root):
        for dirpath in abs_root.rglob("*"):
            if not dirpath.is_dir():
                continue
            if _is_excluded_under_root(dirpath, abs_root):
                continue
            rel = dirpath.relative_to(abs_root)
            if any(seg in _COVERAGE_SKIP_SEGMENTS for seg in rel.parts):
                continue
            md_files = [p for p in dirpath.iterdir() if p.is_file() and p.suffix == ".md"]
            if not md_files:
                continue
            if not (dirpath / "README.md").exists():
                missing.append(dirpath.relative_to(repo_root).as_posix())
    return sorted(missing)


def build_index(repo_root: Path) -> IndexResult:
    """Construct the README index. Cheap enough to run on every startup."""
    readmes = _list_readmes(repo_root)
    parts: list[str] = []
    total = 0
    for p in readmes:
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        rel = p.relative_to(repo_root).as_posix()
        chunk = f"\n\n===== INDEX ENTRY: {rel} =====\n\n{text}"
        parts.append(chunk)
        total += len(chunk)
    index_text = "".join(parts) if parts else ""
    missing = _find_missing_readme_folders(repo_root)
    return IndexResult(
        text=index_text,
        readme_count=len(readmes),
        total_bytes=total,
        missing_readme_folders=missing,
    )


# ---------------- core resolution ----------------

def _expand_core_entry(repo_root: Path, entry: str) -> list[Path]:
    """Expand one agent `core:` entry into a list of `.md` file paths.

    Semantics:
      - Specific .md file path    → that file (if groundable)
      - Folder path               → the folder's README.md + direct-child .md
                                    (non-README), both filtered for groundability
      - Glob (`**`, `*`, `?`)     → glob match restricted to groundable .md files
    """
    if any(ch in entry for ch in ("*", "?", "[")):
        return [
            m for m in sorted(repo_root.glob(entry))
            if m.is_file() and m.suffix == ".md" and _path_is_groundable(m, repo_root)
        ]
    p = repo_root / entry
    if not p.exists():
        return []
    if p.is_file() and p.suffix == ".md" and _path_is_groundable(p, repo_root):
        return [p]
    if p.is_dir() and _path_is_groundable(p, repo_root):
        files: list[Path] = []
        readme = p / "README.md"
        if readme.exists():
            files.append(readme)
        for child in sorted(p.iterdir()):
            if (
                child.is_file()
                and child.suffix == ".md"
                and child.name != "README.md"
                and _path_is_groundable(child, repo_root)
            ):
                files.append(child)
        return files
    return []


def resolve_core(repo_root: Path, entries: list[str]) -> list[Path]:
    """Resolve an agent's `core:` list to a flat, deduplicated list of paths."""
    seen: set[Path] = set()
    out: list[Path] = []
    for entry in entries:
        for p in _expand_core_entry(repo_root, entry):
            if p not in seen:
                seen.add(p)
                out.append(p)
    return out


def concatenate_files(repo_root: Path, paths: list[Path]) -> str:
    """Concatenate the contents of paths with separator headers."""
    parts: list[str] = []
    for p in paths:
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        rel = p.relative_to(repo_root).as_posix()
        parts.append(f"\n\n===== FILE: {rel} =====\n\n{text}")
    return "".join(parts)


# Public alias — callers may want to check groundability of arbitrary paths
# (e.g. the read_files tool validating a user-supplied path).
def is_groundable(path: Path, repo_root: Path) -> bool:
    return _path_is_groundable(path, repo_root)
