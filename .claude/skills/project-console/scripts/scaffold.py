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
PROJECT_OWNED = {"agents/", "themes/", "console.yaml", ".env", "pyproject.toml", "run.sh", "start.sh"}


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
  overrides: {{}}
    # submission-tracker:
    #   title: "Submission Package Tracker"
    #   group: "Submissions"
    #   order: 1

server:
  host: 127.0.0.1
  port: {port}
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

RUN_SH_TEMPLATE = r"""#!/usr/bin/env bash
# project-console launcher. The FastAPI app code lives in the skill at
# $CLAUDE_PROJECT_DIR/.claude/skills/project-console/console/; this script
# injects that directory onto sys.path and runs uvicorn.
#
# Port is read from console.yaml `server.port` (falls back to 8765). Use
# `start.sh` for an idempotent launch that stops any existing listener first.
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

# Resolve port from console.yaml (falls back to 8765). Keep this block in sync
# with the matching one in start.sh.
PORT=8765
if [ -f console.yaml ]; then
  discovered=$(awk '
    /^server:/ { s=1; next }
    /^[^[:space:]]/ && s { s=0 }
    s && /port:/ { gsub(/[^0-9]/, "", $2); if ($2 != "") { print $2; exit } }
  ' console.yaml 2>/dev/null || true)
  if [ -n "$discovered" ]; then
    PORT="$discovered"
  fi
fi

HOST=127.0.0.1
if [ -f console.yaml ]; then
  discovered_host=$(awk '
    /^server:/ { s=1; next }
    /^[^[:space:]]/ && s { s=0 }
    s && /host:/ { sub(/^[[:space:]]*host:[[:space:]]*/, ""); sub(/[[:space:]]*#.*$/, ""); gsub(/["'\'']/, ""); print; exit }
  ' console.yaml 2>/dev/null || true)
  if [ -n "$discovered_host" ]; then
    HOST="$discovered_host"
  fi
fi

uv sync

# Strip macOS Finder junk (Icon\r, AppleDouble ._*) that can crash
# jsonschema.iterdir() when they show up inside site-packages. Cheap no-op
# on non-macOS machines or clean venvs.
if [ -d .venv ]; then
  find .venv \( -name $'Icon\r' -o -name '._*' \) -print -delete 2>/dev/null | head -20 >/dev/null || true
fi

export PYTHONPATH="$SKILL_CONSOLE/..:${PYTHONPATH:-}"
echo "project-console: launching on http://$HOST:$PORT ..."
# uvicorn --reload watches cwd (tools/project-console/) recursively. Exclude
# trace-matrix/ because the `Initialize with Claude` flow writes adapters
# there at runtime and we don't want the file write to kill the in-flight
# SSE stream. Also exclude common venv/cache dirs.
exec uv run uvicorn console.app:app --reload \
  --reload-exclude 'trace-matrix/*' \
  --reload-exclude 'trace-matrix/**/*' \
  --reload-exclude '.venv/*' \
  --reload-exclude '.venv/**/*' \
  --reload-exclude '__pycache__/*' \
  --reload-exclude '.data/*' \
  --host "$HOST" --port "$PORT"
"""

START_SH_TEMPLATE = """\
#!/usr/bin/env bash
# project-console start — idempotent launcher. Kills any process already
# listening on the configured port, then execs run.sh. Use this whenever
# skill code has changed (uvicorn --reload does NOT watch the skill
# package) or when an earlier session left a stale console running.
set -euo pipefail
cd "$(dirname "$0")"

# Resolve port: prefer console.yaml's server.port, fall back to 8765.
PORT=8765
if [ -f console.yaml ]; then
  discovered=$(awk '
    /^server:/ { s=1; next }
    /^[^[:space:]]/ && s { s=0 }
    s && /port:/ { gsub(/[^0-9]/, "", $2); if ($2 != "") { print $2; exit } }
  ' console.yaml 2>/dev/null || true)
  if [ -n "$discovered" ]; then
    PORT="$discovered"
  fi
fi

# Kill any existing listener on the port
existing=$(lsof -ti "tcp:$PORT" 2>/dev/null || true)
if [ -n "$existing" ]; then
  pids=$(echo "$existing" | tr '\\n' ' ')
  echo "project-console: stopping existing console on port $PORT (pid(s): $pids)"
  # Best effort: TERM first, wait, then KILL stragglers
  echo "$existing" | xargs kill 2>/dev/null || true
  sleep 1
  still=$(lsof -ti "tcp:$PORT" 2>/dev/null || true)
  if [ -n "$still" ]; then
    echo "project-console: force-killing stragglers on port $PORT"
    echo "$still" | xargs kill -9 2>/dev/null || true
    sleep 1
  fi
fi

echo "project-console: starting on port $PORT..."
exec bash ./run.sh
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


DEFAULT_PORT = 8765


def init_scaffold(project_root: Path, skill_root: Path, force: bool, port: int = DEFAULT_PORT) -> None:
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
    (tool_root / "console.yaml").write_text(CONSOLE_YAML_DEFAULT.format(port=port))
    (tool_root / "pyproject.toml").write_text(PYPROJECT_TEMPLATE)
    (tool_root / "run.sh").write_text(RUN_SH_TEMPLATE)
    (tool_root / "run.sh").chmod(0o755)
    (tool_root / "start.sh").write_text(START_SH_TEMPLATE)
    (tool_root / "start.sh").chmod(0o755)
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
    print(f"Configured port: {port} (edit tools/project-console/console.yaml server.port to change)")
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

    # Files we replace in sync (skill-owned templates)
    skill_owned = [
        ("run.sh", RUN_SH_TEMPLATE, 0o755),
        ("start.sh", START_SH_TEMPLATE, 0o755),
    ]
    updated = []
    for rel, content, mode in skill_owned:
        dst = tool_root / rel
        if not dst.exists() or dst.read_text() != content:
            dst.write_text(content)
            dst.chmod(mode)
            updated.append(rel)

    # Copy over any NEW agent templates that the project doesn't have yet.
    # Existing files are left alone — the project owns its roster after init.
    src_agents = skill_root / "agents" / "templates"
    agents_dst = tool_root / "agents" / "core-team"
    new_agents: list[str] = []
    if src_agents.is_dir() and agents_dst.is_dir():
        for src in src_agents.glob("*.md"):
            dst = agents_dst / src.name
            if not dst.exists():
                shutil.copy2(src, dst)
                new_agents.append(src.name)

    manifest["skill_version"] = current_version
    manifest["last_synced_at"] = dt.datetime.now(dt.timezone.utc).isoformat()
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")

    print(f"Synced: {prev_version} → {current_version}")
    if updated:
        print("Updated files:")
        for u in updated:
            print(f"  - {u}")
    if new_agents:
        print("Added agent templates (new since last sync):")
        for name in new_agents:
            print(f"  - agents/core-team/{name}")
    if not updated and not new_agents:
        print("No changes.")
    print()
    print("If the console is running, restart it to pick up skill code changes.")
    print("(uvicorn --reload watches tools/project-console/, not the skill package.)")


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
    p.add_argument("--port", type=int, default=DEFAULT_PORT,
                   help=f"Port for the console server (default: {DEFAULT_PORT}). "
                        "Claude should ask the user to confirm before running init.")
    p.add_argument("--project-root", default=None)
    p.add_argument("--skill-root", default=None)
    args = p.parse_args()

    project_root = resolve_project_root(args.project_root)
    skill_root = resolve_skill_root(project_root, args.skill_root)

    if not skill_root.exists():
        print(f"Skill not found at {skill_root}", file=sys.stderr)
        return 1

    if args.action == "init":
        init_scaffold(project_root, skill_root, args.force, args.port)
    elif args.action == "sync":
        sync_scaffold(project_root, skill_root)
    elif args.action == "status":
        status_scaffold(project_root, skill_root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
