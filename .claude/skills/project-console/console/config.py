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
    def model_default(self) -> str:
        """Console-wide default model. Agents resolve to this when model is absent or 'default'."""
        return (self.console.get("models") or {}).get("default") or DEFAULT_MODEL

    @property
    def summarizer_model(self) -> str:
        """Model used for catalog build-time LLM summarization (Phase 2 / task 099)."""
        return (self.console.get("models") or {}).get("summarizer") or DEFAULT_SUMMARIZER

    def resolve_model(self, model: str | None) -> str:
        """Resolve an agent's frontmatter `model:` field to the effective model ID.

        Hierarchy: explicit model → sentinel `"default"` / absent → console.yaml
        `models.default` → DEFAULT_MODEL.
        """
        if model and model != "default":
            return model
        return self.model_default

    @property
    def grounding_roots(self) -> tuple[str, ...]:
        """Filesystem roots (relative to repo_root) that are exposable to the
        assistant drawer's grounding surface — scanned by the README-index
        walker and accepted by the `read_files` tool.

        Defaults cover the project's own docs tree. Extended by the console.yaml
        `grounding.extra_roots` list to expose skill-embedded reference material
        (e.g. distilled FDA guidance and standards shipped inside the
        `medtech-docs` skill at `.claude/skills/medtech-docs/references/`).
        """
        defaults = ("docs/project", "docs/external", "docs/internal/source-md")
        extras = tuple(
            str(x) for x in ((self.console.get("grounding") or {}).get("extra_roots") or [])
        )
        # Preserve order + dedupe.
        seen: set[str] = set()
        out: list[str] = []
        for r in defaults + extras:
            r = r.rstrip("/")
            if r and r not in seen:
                seen.add(r)
                out.append(r)
        return tuple(out)

    @property
    def labor_rates(self) -> dict[str, float]:
        """Persona → fully-loaded USD/hour, from console.yaml `value.labor_rates`.
        Presentation-layer ONLY — the contentious labor-rate assumption lives here,
        not in the committed person-hours/token data. Persona keys mirror the
        advisor set; `default` covers unlisted personas and `_unattributed`."""
        block = (self.console.get("value") or {}).get("labor_rates") or {}
        return {str(k): float(v) for k, v in block.items() if isinstance(v, (int, float))}

    def labor_rate_for(self, persona: str) -> float:
        """Loaded $/hr for a persona, falling back to `default` (then 0.0)."""
        rates = self.labor_rates
        return rates.get(persona, rates.get("default", 0.0))

    @property
    def value_currency(self) -> str:
        return str((self.console.get("value") or {}).get("currency") or "USD")

    @property
    def chat_mcp_servers(self) -> list[str]:
        """External MCP servers (by name, as declared in the project's
        `.mcp.json`) exposed to every chat agent as tools — e.g. the
        semantic file-locator. Project-configurable via console.yaml
        `chat.mcp_servers`; defaults to the file-locator if present.
        Names absent from `.mcp.json` are silently skipped at launch.
        """
        configured = (self.console.get("chat") or {}).get("mcp_servers")
        if configured is None:
            return ["file-locator"]
        return [str(x) for x in configured]

    def caps_for_model(self, model: str) -> dict[str, int]:
        """Return cap values (`source_cap_kb`, `grounding_cap_kb`) for the given model.

        Resolution order (highest wins):
          1. console.yaml `models.caps.<model>`
          2. console.yaml `models.caps.default`
          3. code defaults `_MODEL_CAP_DEFAULTS[<model>]`
          4. `DEFAULT_CAPS` (Sonnet-tier fallback)
        """
        caps_block = (self.console.get("models") or {}).get("caps") or {}
        user_override = caps_block.get(model) or {}
        user_default = caps_block.get("default") or {}
        code_default = _MODEL_CAP_DEFAULTS.get(model, {})
        merged: dict[str, int] = dict(DEFAULT_CAPS)
        merged.update(code_default)
        merged.update(user_default)
        merged.update(user_override)
        return merged

    @property
    def dashboards_config(self) -> dict:
        return self.console.get("dashboards", {}) or {}


DEFAULT_MODEL = "claude-sonnet-4-6"
DEFAULT_SUMMARIZER = "claude-haiku-4-5"

# Fallback cap defaults (Sonnet-tier) — apply when no per-model or user
# override is present. Expressed in KB for readability in console.yaml.
DEFAULT_CAPS: dict[str, int] = {
    "source_cap_kb": 500,
    "grounding_cap_kb": 80,
}

# Per-model cap defaults baked into the code. console.yaml `models.caps`
# entries override these. Context windows:
#   Sonnet 4.6 ≈ 200K tokens ≈ 800 KB plaintext
#   Opus 4.7   ≈ 1M tokens   ≈ 4 MB plaintext
#   Haiku 4.5  ≈ 200K tokens ≈ 800 KB plaintext
# Caps sized to leave headroom for conversation history + response.
_MODEL_CAP_DEFAULTS: dict[str, dict[str, int]] = {
    "claude-sonnet-4-6": {"source_cap_kb": 500, "grounding_cap_kb": 80},
    "claude-opus-4-7":   {"source_cap_kb": 2000, "grounding_cap_kb": 200},
    "claude-haiku-4-5":  {"source_cap_kb": 300, "grounding_cap_kb": 80},
}

_DEFAULT_CONSOLE_YAML: dict[str, Any] = {
    "theme": "light",
    "models": {
        "default": DEFAULT_MODEL,
        "summarizer": DEFAULT_SUMMARIZER,
    },
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
