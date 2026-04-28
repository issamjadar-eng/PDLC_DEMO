"""Derive the DHF-manifest output filename prefix from project.yml.

The skill emits four files per build: `<prefix>-dhf-manifest.{md,json}`,
`<prefix>-dhf-by-section.md`, and `<prefix>-dhf-dashboard.md`. The prefix
is project-supplied so each project's manifests are visually self-
identifying and the registry stays neutral.

Resolution order:
  1. `dhf_manifest.output_prefix` in project.yml (explicit override)
  2. `project.name` slugified (default)
  3. `dhf` literal fallback (no project.yml found — gives `dhf-dhf-manifest.md`,
     awkward but unique enough to surface the missing project.yml as a smell)

Slugification rules: lowercase; whitespace and underscores → hyphens;
strip non-alphanumeric except hyphens; collapse repeated hyphens; trim
leading/trailing hyphens.
"""
from __future__ import annotations

import re
from pathlib import Path


def _slugify(text: str) -> str:
    s = text.strip().lower()
    s = re.sub(r"[\s_]+", "-", s)
    s = re.sub(r"[^a-z0-9-]+", "", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s


def _read_field(yml_text: str, path: tuple[str, ...]) -> str | None:
    """Walk a tuple of nested keys against indented YAML. Pure stdlib —
    we cannot assume PyYAML is installed in every consumer environment.
    Matches `^<indent><key>: <value>` lines under successive `^<key>:` blocks.
    """
    lines = yml_text.splitlines()
    target_indents: list[int] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.lstrip()
        if not stripped or stripped.startswith("#"):
            i += 1
            continue
        indent = len(line) - len(stripped)
        depth = len(target_indents)
        if depth == len(path):
            return None
        expected_key = path[depth]
        m = re.match(rf"^{re.escape(expected_key)}\s*:\s*(.*)$", stripped)
        if m:
            value = m.group(1).strip()
            if depth == len(path) - 1:
                if value and not value.startswith("#"):
                    return value.strip("\"'")
                return None
            if not target_indents or indent > target_indents[-1]:
                target_indents.append(indent)
            i += 1
            continue
        i += 1
    return None


def project_slug(project_root: Path | None = None) -> str:
    """Return the slug used to prefix dhf-manifest output filenames."""
    root = project_root or _find_project_root()
    yml_path = root / "project.yml"
    if not yml_path.exists():
        return "dhf"
    text = yml_path.read_text(encoding="utf-8", errors="replace")

    override = _read_field(text, ("dhf_manifest", "output_prefix"))
    if override:
        slug = _slugify(override)
        if slug:
            return slug

    name = _read_field(text, ("project", "name"))
    if name:
        slug = _slugify(name)
        if slug:
            return slug

    return "dhf"


def project_display_name(project_root: Path | None = None) -> str:
    """Human-readable project name for output titles. Falls back to "DHF"
    when project.yml is missing or has no name."""
    root = project_root or _find_project_root()
    yml_path = root / "project.yml"
    if not yml_path.exists():
        return "DHF"
    text = yml_path.read_text(encoding="utf-8", errors="replace")
    name = _read_field(text, ("project", "name"))
    return name or "DHF"


def manifest_filename(slug: str, suffix: str) -> str:
    """Compose an output filename: `<slug>-dhf-<suffix>`.

    Suffix examples: `manifest.md`, `manifest.json`, `by-section.md`, `dashboard.md`.
    """
    return f"{slug}-dhf-{suffix}"


def _find_project_root() -> Path:
    """Walk up from CWD until a `project.yml` is found; fallback to CWD."""
    cwd = Path.cwd().resolve()
    for candidate in (cwd, *cwd.parents):
        if (candidate / "project.yml").exists():
            return candidate
    return cwd


if __name__ == "__main__":
    slug = project_slug()
    print(f"slug: {slug}")
    for suffix in ("manifest.md", "manifest.json", "by-section.md", "dashboard.md"):
        print(f"  {manifest_filename(slug, suffix)}")
