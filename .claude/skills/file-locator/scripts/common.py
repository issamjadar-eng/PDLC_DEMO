"""Shared utilities for the file-locator skill.

Config loading, glob walking, gate enforcement, content hashing, and summary
extraction. The indexer and the MCP server both import from this module.

Project-agnostic. Reads everything from `project.yml file_locator:`.
"""
from __future__ import annotations

import fnmatch
import hashlib
import os
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

import yaml


# ─── Config ─────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class LocatorConfig:
    project_root: Path
    index_path: Path
    embedding_model: str
    embedding_dimension: int
    embedding_weight: float
    bm25_weight: float
    band_high: float
    band_partial: float
    sub_summary_lines_threshold: int
    sub_summary_h2_threshold: int
    decision_block_pattern: re.Pattern[str]
    includes: tuple[str, ...]
    excludes: tuple[str, ...]


def load_config(project_root: Path | None = None) -> LocatorConfig:
    """Load locator config from `<project_root>/project.yml`. Raises if the
    `file_locator:` block is missing — `setup` action installs it."""
    root = project_root or _detect_project_root()
    pyl = root / "project.yml"
    if not pyl.exists():
        raise FileNotFoundError(f"project.yml not found at {pyl}")
    with pyl.open() as f:
        data = yaml.safe_load(f) or {}
    fl = data.get("file_locator")
    if not fl:
        raise KeyError(
            "project.yml is missing the `file_locator:` block. "
            "Run `/file-locator setup` to install it."
        )
    return LocatorConfig(
        project_root=root,
        index_path=root / fl["index_path"],
        embedding_model=fl["embedding"]["model"],
        embedding_dimension=int(fl["embedding"]["dimension"]),
        embedding_weight=float(fl["ranking"]["embedding_weight"]),
        bm25_weight=float(fl["ranking"]["bm25_weight"]),
        band_high=float(fl["ranking"]["banding"]["high_confidence"]),
        band_partial=float(fl["ranking"]["banding"]["partial_match"]),
        sub_summary_lines_threshold=int(fl["granularity"]["sub_summary_when_lines_gt"]),
        sub_summary_h2_threshold=int(fl["granularity"]["sub_summary_when_h2_gt"]),
        decision_block_pattern=re.compile(fl["granularity"]["decision_block_pattern"], re.MULTILINE),
        includes=tuple(fl["corpus_includes"]),
        excludes=tuple(fl["corpus_excludes"]),
    )


def _detect_project_root() -> Path:
    env = os.environ.get("CLAUDE_PROJECT_DIR")
    if env:
        return Path(env)
    # fallback: walk up from cwd until we find project.yml
    cur = Path.cwd().resolve()
    for p in (cur, *cur.parents):
        if (p / "project.yml").exists():
            return p
    raise RuntimeError("Cannot locate project root: no project.yml in cwd or parents.")


# ─── Gate enforcement ──────────────────────────────────────────────────────

class GateOutcome:
    INCLUDED = "included"
    EXCLUDED_BY_DENYLIST = "gate2_excludes"
    GITIGNORED = "gate3_gitignored"
    SKIP_SENTINEL = "gate4_skip_sentinel"
    NOT_IN_INCLUDES = "not_in_includes"


@dataclass
class WalkResult:
    included: list[Path] = field(default_factory=list)
    by_outcome: dict[str, list[Path]] = field(default_factory=lambda: {
        GateOutcome.EXCLUDED_BY_DENYLIST: [],
        GateOutcome.GITIGNORED: [],
        GateOutcome.SKIP_SENTINEL: [],
        GateOutcome.NOT_IN_INCLUDES: [],
    })


def walk_corpus(cfg: LocatorConfig, audit: bool = False) -> WalkResult:
    """Walk the project tree applying all 4 inclusion gates.

    Returns a WalkResult. In audit mode, also collects non-included files
    bucketed by which gate rejected them. In non-audit mode (default), only
    the `included` list is populated — faster.
    """
    result = WalkResult()
    gitignored = _gitignored_paths(cfg.project_root)

    # In non-audit mode, only walk files matched by at least one include glob.
    # In audit mode, walk everything (so we can report what's NOT included).
    candidates = (
        _walk_everything(cfg.project_root) if audit
        else _walk_matching_includes(cfg.project_root, cfg.includes)
    )

    for abs_path in candidates:
        rel = abs_path.relative_to(cfg.project_root)
        rel_str = str(rel)

        if _matches_any(rel_str, cfg.excludes):
            if audit:
                result.by_outcome[GateOutcome.EXCLUDED_BY_DENYLIST].append(rel)
            continue
        if rel in gitignored:
            if audit:
                result.by_outcome[GateOutcome.GITIGNORED].append(rel)
            continue
        if not _matches_any(rel_str, cfg.includes):
            if audit:
                result.by_outcome[GateOutcome.NOT_IN_INCLUDES].append(rel)
            continue
        if _has_skip_sentinel(abs_path):
            if audit:
                result.by_outcome[GateOutcome.SKIP_SENTINEL].append(rel)
            continue
        result.included.append(rel)

    return result


def _walk_matching_includes(root: Path, includes: tuple[str, ...]) -> Iterable[Path]:
    """Yield files under root that match at least one include glob.
    Skips noisy directories early to avoid full-tree walks."""
    pruned_dirs = {".git", "node_modules", "__pycache__", ".worktrees", "_scratch", ".staging"}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in pruned_dirs]
        for fn in filenames:
            p = Path(dirpath) / fn
            rel_str = str(p.relative_to(root))
            if _matches_any(rel_str, includes):
                yield p


def _walk_everything(root: Path) -> Iterable[Path]:
    """Audit-mode walk — everything except .git and friends."""
    pruned_dirs = {".git", "node_modules", "__pycache__", ".worktrees"}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in pruned_dirs]
        for fn in filenames:
            yield Path(dirpath) / fn


def _matches_any(rel_path: str, patterns: tuple[str, ...]) -> bool:
    # fnmatch handles * and ? but not **. Translate ** to a recursive match
    # by stripping ** segments before comparison.
    for pat in patterns:
        if _glob_match(rel_path, pat):
            return True
    return False


def _glob_match(path: str, pattern: str) -> bool:
    """Match a repo-relative path against a gitignore-style glob.

    Supports `**` (any number of path segments incl. zero), `*` (within
    one segment), `?` (single char), and `{a,b,c}` brace expansion. Uses
    a single-pass tokenizer rather than cascading replace — earlier
    cascading-replace version mangled `*` inside the `**`-replacement.
    """
    parts: list[str] = []
    i = 0
    n = len(pattern)
    while i < n:
        c = pattern[i]
        if c == "*":
            if i + 1 < n and pattern[i + 1] == "*":
                # `**/`: zero-or-more path segments; `**` at end: match anything
                if i + 2 < n and pattern[i + 2] == "/":
                    parts.append("(?:[^/]+/)*")
                    i += 3
                else:
                    parts.append(".*")
                    i += 2
            else:
                parts.append("[^/]*")
                i += 1
        elif c == "?":
            parts.append("[^/]")
            i += 1
        elif c == "{":
            close = pattern.find("}", i)
            if close > 0:
                options = pattern[i + 1 : close].split(",")
                parts.append("(?:" + "|".join(re.escape(o.strip()) for o in options) + ")")
                i = close + 1
            else:
                parts.append(re.escape(c))
                i += 1
        else:
            parts.append(re.escape(c))
            i += 1
    return re.fullmatch("".join(parts), path) is not None


def _gitignored_paths(root: Path) -> set[Path]:
    """Return paths that git reports as ignored. Empty set if not a git repo."""
    try:
        result = subprocess.run(
            ["git", "ls-files", "--others", "--ignored", "--exclude-standard"],
            cwd=root, capture_output=True, text=True, check=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return set()
    return {Path(line) for line in result.stdout.splitlines() if line}


def _has_skip_sentinel(path: Path) -> bool:
    """Check for `locator_skip: true` in frontmatter OR
    `<!-- file-locator: skip -->` in first ~30 lines."""
    try:
        with path.open("r", encoding="utf-8", errors="replace") as f:
            head = "".join(next(f, "") for _ in range(30))
    except OSError:
        return False
    if "<!-- file-locator: skip -->" in head:
        return True
    if head.startswith("---"):
        fm_end = head.find("\n---", 3)
        if fm_end > 0:
            fm = head[3:fm_end]
            if re.search(r"^locator_skip:\s*true\s*$", fm, re.MULTILINE):
                return True
    return False


# ─── Content hashing & summary extraction ──────────────────────────────────

def content_hash(path: Path) -> str:
    """SHA-256 of file content with line endings normalized to LF."""
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk.replace(b"\r\n", b"\n"))
    return h.hexdigest()


@dataclass
class ExtractedSummary:
    text: str
    method: str  # 'frontmatter' | 'auto'


@dataclass
class SubSummary:
    heading_anchor: str
    heading_text: str
    text: str


SUMMARY_MAX_CHARS = 400


def extract_summary(path: Path, cfg: LocatorConfig) -> tuple[ExtractedSummary, list[SubSummary]]:
    """Extract file-level summary and (when granularity rule triggers) sub-summaries."""
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ExtractedSummary(text=path.name, method="auto"), []

    frontmatter, body = _split_frontmatter(content)
    file_summary = _file_level_summary(frontmatter, body, path.name)
    sub_summaries: list[SubSummary] = []

    if _needs_sub_summaries(body, cfg):
        sub_summaries = _extract_sub_summaries(body, cfg)

    return file_summary, sub_summaries


def _split_frontmatter(content: str) -> tuple[dict, str]:
    if not content.startswith("---"):
        return {}, content
    end = content.find("\n---", 3)
    if end < 0:
        return {}, content
    fm_raw = content[3:end].strip()
    body = content[end + 4:].lstrip("\n")
    try:
        fm = yaml.safe_load(fm_raw) or {}
        if not isinstance(fm, dict):
            fm = {}
    except yaml.YAMLError:
        fm = {}
    return fm, body


def _file_level_summary(fm: dict, body: str, filename: str) -> ExtractedSummary:
    # Tier 1: frontmatter `locator_summary:` override
    override = fm.get("locator_summary")
    if isinstance(override, str) and override.strip():
        return ExtractedSummary(text=_truncate(override.strip()), method="frontmatter")

    # Tier 2: auto-extract — frontmatter `summary:` if present, else title + H1 + first para
    summary_field = fm.get("summary")
    title = fm.get("title")

    parts: list[str] = []
    if isinstance(title, str) and title.strip():
        parts.append(title.strip())
    if isinstance(summary_field, str) and summary_field.strip():
        parts.append(summary_field.strip())
    else:
        h1, first_para = _first_h1_and_paragraph(body)
        if h1 and (not parts or h1 != parts[0]):
            parts.append(h1)
        if first_para:
            parts.append(first_para)

    text = " — ".join(parts) if parts else filename
    return ExtractedSummary(text=_truncate(text), method="auto")


def _first_h1_and_paragraph(body: str) -> tuple[str, str]:
    h1 = ""
    first_para = ""
    lines = body.splitlines()
    i = 0
    # Find first H1
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("# ") and not line.startswith("## "):
            h1 = line.lstrip("#").strip()
            i += 1
            break
        i += 1
    # Find first non-empty, non-heading paragraph after H1 (or after frontmatter if no H1)
    if not h1:
        i = 0
    para_lines: list[str] = []
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            if para_lines:
                break
            i += 1
            continue
        if line.startswith("#") or line.startswith(">") or line.startswith("```"):
            if para_lines:
                break
            i += 1
            continue
        para_lines.append(line)
        i += 1
    first_para = " ".join(para_lines)
    return h1, first_para


def _needs_sub_summaries(body: str, cfg: LocatorConfig) -> bool:
    line_count = body.count("\n")
    if line_count > cfg.sub_summary_lines_threshold:
        return True
    h2_count = sum(1 for ln in body.splitlines() if ln.startswith("## "))
    if h2_count > cfg.sub_summary_h2_threshold:
        return True
    if cfg.decision_block_pattern.search(body):
        return True
    return False


def _extract_sub_summaries(body: str, cfg: LocatorConfig) -> list[SubSummary]:
    """Generate sub-summaries per H2 and per DECISION block.

    DECISION blocks (matched via cfg.decision_block_pattern) take precedence —
    their heading goes into the sub-summary anchor with priority over plain H2.
    Duplicate anchors get GitHub-style suffix numbering (-2, -3, ...).
    """
    sub_summaries: list[SubSummary] = []
    anchor_counts: dict[str, int] = {}
    lines = body.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        is_decision = cfg.decision_block_pattern.match(line) is not None
        is_h2 = stripped.startswith("## ") and not stripped.startswith("### ")
        is_h3_decision = stripped.startswith("### ") and is_decision

        if is_h2 or is_h3_decision:
            heading_text = stripped.lstrip("#").strip()
            base_anchor = _heading_to_anchor(heading_text)
            count = anchor_counts.get(base_anchor, 0)
            anchor = base_anchor if count == 0 else f"{base_anchor}-{count + 1}"
            anchor_counts[base_anchor] = count + 1
            section_text = _capture_section_text(lines, i + 1, max_chars=SUMMARY_MAX_CHARS)
            sub_summaries.append(SubSummary(
                heading_anchor=anchor,
                heading_text=heading_text,
                text=_truncate(f"{heading_text} — {section_text}" if section_text else heading_text),
            ))
        i += 1
    return sub_summaries


def _capture_section_text(lines: list[str], start: int, max_chars: int) -> str:
    """Capture first paragraph after a heading, up to max_chars."""
    buf: list[str] = []
    total = 0
    for j in range(start, len(lines)):
        line = lines[j].strip()
        if line.startswith("#"):
            break
        if not line:
            if buf:
                break
            continue
        if line.startswith("```"):
            continue
        buf.append(line)
        total += len(line)
        if total >= max_chars:
            break
    return " ".join(buf)


def _heading_to_anchor(text: str) -> str:
    """GitHub-style slug: lowercase, alphanumerics + hyphens, collapse spaces."""
    s = text.lower()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[-\s]+", "-", s).strip("-")
    return s


def _truncate(text: str, max_chars: int = SUMMARY_MAX_CHARS) -> str:
    text = " ".join(text.split())  # collapse whitespace
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 1].rstrip() + "…"
