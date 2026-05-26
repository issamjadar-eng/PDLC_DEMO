"""Project-level change-control config loader.

Reads the optional `change_control:` block from `<project_root>/project.yml`
and exposes typed dataclasses that action helpers consume as default
values when CLI flags aren't supplied. CLI flags continue to override the
config — backward-compatible with v0.11.0 and earlier.

Skill code stays project-agnostic: this module never hard-codes a project
name, space key, or page id. It's a thin reader for whatever the consumer
project chose to put in `project.yml`.

Schema (all fields optional; missing block returns an empty config):

    change_control:
      cloud_id: <atlassian-cloud-uuid>
      base_url: https://<site>.atlassian.net

      spaces:
        - key: <SPACE_KEY>
          name: <human label>
          staging_target_root: <repo-relative path>
          title_prefixes_to_strip:
            - "<prefix string>"
            - ...

      test_target:
        space_key: <SPACE_KEY>
        parent_page_id: "<page id as string>"
        parent_title: <title>
        title_prefix: <string>

      cross_page_source_map:
        "<page_id>":
          - filename: "<filename>"
            source_page_title: "<source page title>"
          - ...

Empty / missing fields fall through to None so callers can detect "not
configured" and fall back to legacy CLI-required behavior.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    import yaml  # type: ignore
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore


@dataclass
class SpaceConfig:
    """One Confluence space's pull config."""
    key: str = ""
    name: str = ""
    staging_target_root: str = ""
    title_prefixes_to_strip: list[str] = field(default_factory=list)


@dataclass
class TestTarget:
    """Where /change-control verify writes test fixtures."""
    space_key: str = ""
    parent_page_id: str = ""
    parent_title: str = ""
    title_prefix: str = ""


@dataclass
class CrossPageSourceEntry:
    """One cross-page attachment that lives on a different page."""
    filename: str = ""
    source_page_title: str = ""


@dataclass
class ChangeControlConfig:
    """Top-level config block from project.yml.

    All fields default to empty so callers can use the result safely
    without checking for None at every access. A truly missing config
    block produces an instance with everything blank.
    """
    cloud_id: str = ""
    base_url: str = ""
    spaces: list[SpaceConfig] = field(default_factory=list)
    test_target: TestTarget | None = None
    # Map of page_id -> list of cross-page attachment hints.
    cross_page_source_map: dict[str, list[CrossPageSourceEntry]] = field(
        default_factory=dict
    )

    @property
    def is_empty(self) -> bool:
        """True if no fields populated. Callers can use this to decide
        whether to require CLI flags."""
        return not (
            self.cloud_id
            or self.base_url
            or self.spaces
            or self.test_target
            or self.cross_page_source_map
        )

    def space_by_key(self, key: str) -> SpaceConfig | None:
        """Lookup a configured space by its key (case-sensitive). Returns
        None if not configured."""
        for s in self.spaces:
            if s.key == key:
                return s
        return None


def _coerce_space(d: dict[str, Any]) -> SpaceConfig:
    if not isinstance(d, dict):
        return SpaceConfig()
    prefixes = d.get("title_prefixes_to_strip") or []
    if not isinstance(prefixes, list):
        prefixes = []
    return SpaceConfig(
        key=str(d.get("key") or ""),
        name=str(d.get("name") or ""),
        staging_target_root=str(d.get("staging_target_root") or ""),
        title_prefixes_to_strip=[str(p) for p in prefixes],
    )


def _coerce_test_target(d: dict[str, Any]) -> TestTarget | None:
    if not isinstance(d, dict) or not d:
        return None
    return TestTarget(
        space_key=str(d.get("space_key") or ""),
        parent_page_id=str(d.get("parent_page_id") or ""),
        parent_title=str(d.get("parent_title") or ""),
        title_prefix=str(d.get("title_prefix") or ""),
    )


def _coerce_source_map(
    d: dict[str, Any],
) -> dict[str, list[CrossPageSourceEntry]]:
    """Accept two on-disk shapes for the cross-page source map:

      "<page_id>": []                                 # empty list -> []
      "<page_id>": [{filename, source_page_title}]    # list of dicts
      "<page_id>": {"attachments": [{filename, ...}]} # nested form
    """
    out: dict[str, list[CrossPageSourceEntry]] = {}
    if not isinstance(d, dict):
        return out
    for key, raw in d.items():
        kid = str(key)
        entries: list[CrossPageSourceEntry] = []
        if raw is None:
            out[kid] = []
            continue
        # Accept dict-with-attachments shape.
        items: Any = raw
        if isinstance(raw, dict):
            items = raw.get("attachments") or []
        if not isinstance(items, list):
            out[kid] = []
            continue
        for item in items:
            if not isinstance(item, dict):
                continue
            entries.append(CrossPageSourceEntry(
                filename=str(item.get("filename") or ""),
                source_page_title=str(item.get("source_page_title") or ""),
            ))
        out[kid] = entries
    return out


def parse_change_control_config(raw: dict[str, Any] | None) -> ChangeControlConfig:
    """Pure: turn a parsed YAML dict (or None) into a ChangeControlConfig.

    Used by tests + by `read_change_control_config` after I/O. Accepts a
    full project.yml dict (looks up `change_control` key) or just the
    inner block.
    """
    if not isinstance(raw, dict):
        return ChangeControlConfig()
    block: Any = raw.get("change_control") if "change_control" in raw else raw
    if not isinstance(block, dict):
        return ChangeControlConfig()
    spaces_raw = block.get("spaces") or []
    if not isinstance(spaces_raw, list):
        spaces_raw = []
    return ChangeControlConfig(
        cloud_id=str(block.get("cloud_id") or ""),
        base_url=str(block.get("base_url") or ""),
        spaces=[_coerce_space(s) for s in spaces_raw if isinstance(s, dict)],
        test_target=_coerce_test_target(block.get("test_target") or {}),
        cross_page_source_map=_coerce_source_map(
            block.get("cross_page_source_map") or {}
        ),
    )


def find_project_root(start: Path | None = None) -> Path:
    """Walk upward from `start` (or CWD) looking for project.yml. Falls
    back to CWD if not found — caller can still try to load and get an
    empty config.
    """
    here = (start or Path.cwd()).resolve()
    for cand in [here, *here.parents]:
        if (cand / "project.yml").is_file():
            return cand
    # Honour CLAUDE_PROJECT_DIR if set (Claude Code sets this).
    env = os.environ.get("CLAUDE_PROJECT_DIR")
    if env:
        p = Path(env)
        if (p / "project.yml").is_file():
            return p
    return here


def read_change_control_config(
    project_root: Path | None = None,
) -> ChangeControlConfig:
    """Load `<project_root>/project.yml` and parse the `change_control`
    block. Missing file or missing block returns an empty config.

    Never raises on parse errors — the action layer must keep working
    when the project hasn't opted into the config block yet.
    """
    if yaml is None:
        return ChangeControlConfig()
    root = project_root or find_project_root()
    path = root / "project.yml"
    if not path.is_file():
        return ChangeControlConfig()
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError):
        return ChangeControlConfig()
    return parse_change_control_config(raw)


__all__ = [
    "ChangeControlConfig",
    "SpaceConfig",
    "TestTarget",
    "CrossPageSourceEntry",
    "parse_change_control_config",
    "read_change_control_config",
    "find_project_root",
]
