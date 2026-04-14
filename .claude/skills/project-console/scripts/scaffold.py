#!/usr/bin/env python3
"""Scaffold tools/project-console/ into a project.

Usage:
    python scaffold.py init [--force]
    python scaffold.py sync
    python scaffold.py status

Run from the project root (where project.yml lives). The skill package is
resolved via CLAUDE_PROJECT_DIR/.claude/skills/project-console/ or via the
--skill-root flag.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import shutil
import sys
from pathlib import Path


SCAFFOLD_DIRS = [
    "agents",
    "themes",
]

# class map for the scaffolded files. Anything under console/ or the static
# scaffold is skill-owned; everything in project-owned dirs is user territory.
PROJECT_OWNED = {"agents/", "themes/", "console.yaml", ".env", "pyproject.toml", "run.sh"}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def resolve_project_root(cli_root: str | None) -> Path:
    if cli_root:
        return Path(cli_root).resolve()
    env = os.environ.get("CLAUDE_PROJECT_DIR")
    if env:
        return Path(env).resolve()
    cwd = Path.cwd().resolve()
    for candidate in (cwd, *cwd.parents):
        if (candidate / "project.yml").exists():
            return candidate
    raise SystemExit("Cannot locate project root (no project.yml found).")


def resolve_skill_root(project_root: Path, cli_skill: str | None) -> Path:
    if cli_skill:
        return Path(cli_skill).resolve()
    return (project_root / ".claude/skills/project-console").resolve()


def read_skill_version(skill_root: Path) -> str:
    vf = skill_root / "VERSION"
    if vf.is_file():
        return vf.read_text().strip()
    return "0.0.0-dev"


# ---------------- init ----------------

CONSOLE_YAML_DEFAULT = """\
# tools/project-console/console.yaml
# Project-local configuration for project-console. Safe to edit.
#
# Theme resolution order:
#   1. tools/project-console/themes/<theme>/
#   2. .claude/skills/project-console/themes/<theme>/  (light, dark)
#   3. fallback: light

theme: light

dashboards:
  patterns:
    - docs/**/*-tracker.html
    - docs/**/*-dashboard.html
    - docs/**/dashboard.html
    - docs/**/*-tree.html
  overrides: {}
    # submission-tracker:
    #   title: "Submission Package Tracker"
    #   group: "Submissions"
    #   order: 1

server:
  host: 127.0.0.1
  port: 8765
  log_level: info

auth:
  callback_url: null
"""

PYPROJECT_TEMPLATE = """\
[project]
name = "project-console"
version = "0.1.0"
description = "Local web UI for this project — dashboards, domain agents, workflows."
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.115",
    "uvicorn[standard]>=0.32",
    "jinja2>=3.1",
    "pyyaml>=6.0",
    "claude-agent-sdk>=0.1.0",
    "pydantic>=2.9",
    "markdown>=3.7",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = []
bypass-selection = true
"""

RUN_SH_TEMPLATE = """\
#!/usr/bin/env bash
# project-console launcher. The FastAPI app code lives in the skill at
# $CLAUDE_PROJECT_DIR/.claude/skills/project-console/console/; this script
# injects that directory onto sys.path and runs uvicorn.
set -euo pipefail
cd "$(dirname "$0")"

# Derive project root (where project.yml lives)
PROJECT_ROOT="$(cd ../.. && pwd)"
export CLAUDE_PROJECT_DIR="$PROJECT_ROOT"

SKILL_CONSOLE="$PROJECT_ROOT/.claude/skills/project-console/console"
if [ ! -d "$SKILL_CONSOLE" ]; then
    echo "Error: project-console skill not installed at $SKILL_CONSOLE" >&2
    echo "Run /sync-skills pull, or copy .claude/skills/project-console/ from the registry." >&2
    exit 1
fi

uv sync
export PYTHONPATH="$SKILL_CONSOLE/..:${PYTHONPATH:-}"
exec uv run uvicorn console.app:app --reload --host 127.0.0.1 --port 8765
"""

README_TEMPLATE = """\
# tools/project-console

Local web UI for this project — scaffolded by the `project-console` skill.
The FastAPI app code lives in the skill package at
`.claude/skills/project-console/console/`; this directory contains only
the project-local runtime state.

## What's here

| File / dir | Purpose | Ownership |
|---|---|---|
| `console.yaml` | Theme, dashboards, server, auth config | project-owned |
| `agents/` | Materialized agent roster | project-owned |
| `themes/<name>/` | Project-local theme packs (from `/project-console theme <url>`) | project-owned |
| `.env` | OAuth secrets, Anthropic key (gitignored) | project-owned |
| `pyproject.toml`, `uv.lock` | Python runtime deps | project-owned |
| `run.sh` | Launcher — imports the skill's `console` package and starts uvicorn | project-owned |
| `.project-console.manifest.json` | Install manifest (skill version, file classes) | committed |

## Run

```sh
./run.sh
# → http://127.0.0.1:8765
```

First launch will run `uv sync`. Subsequent launches reuse the venv.

## Update

When a newer `project-console` skill is pulled via `/sync-skills pull`, run:

```
/project-console sync
```

Sync replaces skill-owned files in-place, respects project-owned files, and
asks about any drift you haven't declared in the Customizations section below.

## Customizations

_Anything you change outside `console.overrides.css`, `project_extensions.py`,
or `_project_overrides/` should be declared here so `/project-console sync`
knows what to preserve. Format: one bullet per change, include file + reason + date._

<!-- No customizations declared. -->
"""

GITIGNORE_TEMPLATE = """\
.env
.venv/
__pycache__/
*.pyc
.data/
uv.lock
"""


def init_scaffold(project_root: Path, skill_root: Path, force: bool) -> None:
    tool_root = project_root / "tools" / "project-console"
    if tool_root.exists() and not force:
        # If a manifest exists, suggest sync instead.
        if (tool_root / ".project-console.manifest.json").exists():
            print(f"tools/project-console/ already initialized. Run `sync` to update.")
            return
        print(f"tools/project-console/ exists but has no manifest. Re-run with --force to overwrite.")
        return

    tool_root.mkdir(parents=True, exist_ok=True)

    # Agents — copy template library
    agents_dst = tool_root / "agents" / "core-team"
    agents_dst.mkdir(parents=True, exist_ok=True)
    src_agents = skill_root / "agents" / "templates"
    if src_agents.is_dir():
        for src in src_agents.glob("*.md"):
            dst = agents_dst / src.name
            if not dst.exists():
                shutil.copy2(src, dst)

    # Themes dir (empty — skill defaults are used until user runs `theme <url>`)
    (tool_root / "themes").mkdir(exist_ok=True)

    # Config files
    (tool_root / "console.yaml").write_text(CONSOLE_YAML_DEFAULT)
    (tool_root / "pyproject.toml").write_text(PYPROJECT_TEMPLATE)
    (tool_root / "run.sh").write_text(RUN_SH_TEMPLATE)
    (tool_root / "run.sh").chmod(0o755)
    (tool_root / "README.md").write_text(README_TEMPLATE)
    (tool_root / ".gitignore").write_text(GITIGNORE_TEMPLATE)
    (tool_root / ".env.example").write_text(
        "# Copy to .env and fill in.\n"
        "ANTHROPIC_API_KEY=\n"
        "OAUTH_CLIENT_ID=\n"
        "OAUTH_CLIENT_SECRET=\n"
    )

    # Manifest (narrow — no hashes, committed)
    manifest = {
        "skill": "project-console",
        "skill_version": read_skill_version(skill_root),
        "installed_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "last_synced_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "file_classes": {
            "console.yaml": "project-owned",
            "pyproject.toml": "project-owned",
            "run.sh": "skill-owned",
            "README.md": "skill-owned",
            "agents/": "project-owned",
            "themes/": "project-owned",
            ".env": "project-owned",
        },
    }
    (tool_root / ".project-console.manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n"
    )

    print(f"Scaffolded {tool_root}")
    print("Next steps:")
    print("  1. cd tools/project-console && uv sync")
    print("  2. cp .env.example .env  # fill in credentials")
    print("  3. ./run.sh")
    print("  4. (optional) /project-console theme https://www.your-company.com")


# ---------------- sync ----------------

def sync_scaffold(project_root: Path, skill_root: Path) -> None:
    tool_root = project_root / "tools" / "project-console"
    manifest_path = tool_root / ".project-console.manifest.json"
    if not manifest_path.exists():
        print("No manifest found. Run `init` first.")
        return

    manifest = json.loads(manifest_path.read_text())
    current_version = read_skill_version(skill_root)
    prev_version = manifest.get("skill_version", "unknown")

    # Files we replace in sync
    skill_owned = [
        ("run.sh", RUN_SH_TEMPLATE, 0o755),
    ]
    updated = []
    for rel, content, mode in skill_owned:
        dst = tool_root / rel
        if not dst.exists() or dst.read_text() != content:
            dst.write_text(content)
            dst.chmod(mode)
            updated.append(rel)

    manifest["skill_version"] = current_version
    manifest["last_synced_at"] = dt.datetime.now(dt.timezone.utc).isoformat()
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")

    print(f"Synced: {prev_version} → {current_version}")
    if updated:
        print("Updated files:")
        for u in updated:
            print(f"  - {u}")
    else:
        print("No skill-owned file changes.")


# ---------------- status ----------------

def status_scaffold(project_root: Path, skill_root: Path) -> None:
    tool_root = project_root / "tools" / "project-console"
    manifest_path = tool_root / ".project-console.manifest.json"
    if not manifest_path.exists():
        print("Not installed (no manifest). Run `init` to scaffold.")
        return

    manifest = json.loads(manifest_path.read_text())
    print(f"Project: {project_root}")
    print(f"Skill:   {skill_root}")
    print(f"Installed version: {manifest.get('skill_version')}")
    print(f"Current version:   {read_skill_version(skill_root)}")
    print(f"Installed at: {manifest.get('installed_at')}")
    print(f"Last synced:  {manifest.get('last_synced_at')}")


# ---------------- main ----------------

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("action", choices=["init", "sync", "status"])
    p.add_argument("--force", action="store_true")
    p.add_argument("--project-root", default=None)
    p.add_argument("--skill-root", default=None)
    args = p.parse_args()

    project_root = resolve_project_root(args.project_root)
    skill_root = resolve_skill_root(project_root, args.skill_root)

    if not skill_root.exists():
        print(f"Skill not found at {skill_root}", file=sys.stderr)
        return 1

    if args.action == "init":
        init_scaffold(project_root, skill_root, args.force)
    elif args.action == "sync":
        sync_scaffold(project_root, skill_root)
    elif args.action == "status":
        status_scaffold(project_root, skill_root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
