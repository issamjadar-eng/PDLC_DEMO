"""Config loader for project-console.

In skill-install mode, this package lives under
`.claude/skills/project-console/console/`. The running project is identified
by the `CLAUDE_PROJECT_DIR` environment variable set by the launcher script
(`tools/project-console/run.sh`). All project state — `project.yml`,
`docs/`, `tools/project-console/` — is resolved relative to that.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class Config:
    repo_root: Path
    tool_root: Path           # tools/project-console/
    agents_dir: Path          # tools/project-console/agents/
    themes_dir: Path          # tools/project-console/themes/
    skill_root: Path | None   # .claude/skills/project-console/ (for fallback themes)
    project: dict
    console: dict             # parsed console.yaml (merged with defaults)
    data_dir: Path

    @property
    def project_name(self) -> str:
        return self.project.get("name", "Project Console")

    @property
    def device(self) -> str:
        return (
            self.project.get("device_family")
            or self.project.get("device")
            or self.project.get("lead_product", "")
        )

    @property
    def regulatory_pathway(self) -> str:
        return self.project.get("regulatory_pathway", "")

    @property
    def theme_name(self) -> str:
        return self.console.get("theme", "light")

    @property
    def server_host(self) -> str:
        return self.console.get("server", {}).get("host", "127.0.0.1")

    @property
    def server_port(self) -> int:
        return int(self.console.get("server", {}).get("port", 8765))

    @property
    def dashboards_config(self) -> dict:
        return self.console.get("dashboards", {}) or {}


_DEFAULT_CONSOLE_YAML: dict[str, Any] = {
    "theme": "light",
    "dashboards": {
        "patterns": [
            "docs/**/*-tracker.html",
            "docs/**/*-dashboard.html",
            "docs/**/dashboard.html",
            "docs/**/*-tree.html",
        ],
        "overrides": {},
    },
    "server": {"host": "127.0.0.1", "port": 8765, "log_level": "info"},
    "auth": {"callback_url": None},
}


def _resolve_repo_root() -> Path:
    env = os.environ.get("CLAUDE_PROJECT_DIR")
    if env:
        p = Path(env).resolve()
        if p.exists():
            return p
    cwd = Path.cwd().resolve()
    for candidate in (cwd, *cwd.parents):
        if (candidate / "project.yml").exists():
            return candidate
    raise RuntimeError(
        "Cannot resolve project root. Set CLAUDE_PROJECT_DIR or run from inside "
        "a project containing project.yml."
    )


def _resolve_skill_root(repo_root: Path) -> Path | None:
    candidate = repo_root / ".claude" / "skills" / "project-console"
    return candidate if candidate.exists() else None


@lru_cache(maxsize=1)
def get_config() -> Config:
    repo_root = _resolve_repo_root()

    project_yml = repo_root / "project.yml"
    if not project_yml.exists():
        raise RuntimeError(f"project.yml not found at {project_yml}")
    project_data = (yaml.safe_load(project_yml.read_text()) or {}).get("project", {})

    tool_root = repo_root / "tools" / "project-console"
    console_yml = tool_root / "console.yaml"
    if console_yml.exists():
        console_data = yaml.safe_load(console_yml.read_text()) or {}
    else:
        console_data = {}

    merged = {k: (dict(v) if isinstance(v, dict) else v) for k, v in _DEFAULT_CONSOLE_YAML.items()}
    for k, v in console_data.items():
        if isinstance(v, dict) and isinstance(merged.get(k), dict):
            inner = dict(merged[k])
            inner.update(v)
            merged[k] = inner
        else:
            merged[k] = v

    return Config(
        repo_root=repo_root,
        tool_root=tool_root,
        agents_dir=tool_root / "agents",
        themes_dir=tool_root / "themes",
        skill_root=_resolve_skill_root(repo_root),
        project=project_data,
        console=merged,
        data_dir=tool_root / ".data",
    )
