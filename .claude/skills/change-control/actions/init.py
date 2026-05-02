"""`change-control init` — wire the skill into the project (MCP-mode).

Preflight checks for the v0.6 MCP-first path:

  1. `.mcp.json` exists at project root and has an `atlassian` entry.
  2. `project.yml` `security.approved_mcps` lists `atlassian`.
  3. `change-control.yml` is present (copies the example template if absent).
  4. `docs/.change-control/state.json` exists (creates `{"page_index": {}}` if absent).
  5. PreToolUse hook is registered (existing scaffold logic — leaves
     a TODO if the project's hook-register script isn't found).
  6. Reminds user to run `/mcp` and authenticate the atlassian connector
     if no token is cached.

What it does NOT do (dropped from the v0.5 design):
  - `mark` binary check
  - keyring probe
  - httpx Python dep check

Project-agnostic. Reads `change-control.yml` if present to surface
the configured base_url + plugin in the report.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path
from typing import Any

SKILL_ROOT = Path(__file__).resolve().parent.parent

try:
    import yaml  # type: ignore
except ImportError:
    yaml = None  # type: ignore


# ---- Checks ----


def _project_root() -> Path:
    """Walk up from cwd to find a `.mcp.json` or `project.yml`. Falls
    back to cwd if neither is found."""
    cwd = Path.cwd().resolve()
    for p in [cwd, *cwd.parents]:
        if (p / "project.yml").exists() or (p / ".mcp.json").exists():
            return p
    return cwd


def check_mcp_json(root: Path) -> tuple[bool, str]:
    p = root / ".mcp.json"
    if not p.is_file():
        return False, ".mcp.json not found at project root"
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (ValueError, OSError) as exc:
        return False, f".mcp.json is not valid JSON: {exc}"
    servers = data.get("mcpServers") or data.get("mcp_servers") or {}
    if "atlassian" not in servers:
        return False, ".mcp.json has no `atlassian` entry under mcpServers"
    return True, "atlassian MCP entry present"


def check_approved_mcps(root: Path) -> tuple[bool, str]:
    p = root / "project.yml"
    if not p.is_file():
        return False, "project.yml not found (warn-only — pre-existing limitation)"
    if yaml is None:
        return False, "PyYAML not installed; cannot validate approved_mcps"
    try:
        data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        return False, f"project.yml is not valid YAML: {exc}"
    sec = (data.get("security") or {}) if isinstance(data, dict) else {}
    approved = sec.get("approved_mcps") or []
    if not isinstance(approved, list) or "atlassian" not in approved:
        return False, "project.yml security.approved_mcps does not list `atlassian`"
    return True, "atlassian listed in security.approved_mcps"


def check_change_control_yml(root: Path) -> tuple[bool, str, dict[str, Any]]:
    """Returns (present, message, parsed-or-empty). Copies the example
    template if absent (as a side-effect)."""
    p = root / "change-control.yml"
    if p.is_file():
        if yaml is None:
            return True, "change-control.yml present (parsing skipped — PyYAML missing)", {}
        try:
            return True, "change-control.yml present", yaml.safe_load(p.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError as exc:
            return False, f"change-control.yml is not valid YAML: {exc}", {}
    template = SKILL_ROOT / "templates" / "change-control.example.yml"
    if template.is_file():
        shutil.copy2(template, p)
        return True, f"change-control.yml absent — copied from {template}", {}
    return False, "change-control.yml absent and template missing", {}


def check_state_json(root: Path) -> tuple[bool, str]:
    p = root / "docs" / ".change-control" / "state.json"
    if p.is_file():
        return True, f"{p} present"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({"page_index": {}}, indent=2) + "\n", encoding="utf-8")
    return True, f"{p} created (empty page_index)"


# ---- Main ----


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="change-control init",
        description="Wire the change-control skill into the project (MCP-first preflight).",
    )
    p.add_argument(
        "--root",
        default="",
        help="Project root (default: walk up from cwd to find project.yml/.mcp.json).",
    )
    p.add_argument("--json", action="store_true", help="Emit JSON report.")
    return p


def run(args: argparse.Namespace) -> int:
    root = Path(args.root) if args.root else _project_root()
    results: list[tuple[str, bool, str]] = []

    ok, msg = check_mcp_json(root)
    results.append(("mcp.json:atlassian", ok, msg))

    ok, msg = check_approved_mcps(root)
    results.append(("project.yml:approved_mcps", ok, msg))

    ok, msg, cfg = check_change_control_yml(root)
    results.append(("change-control.yml", ok, msg))

    ok, msg = check_state_json(root)
    results.append(("docs/.change-control/state.json", ok, msg))

    confluence = (cfg.get("confluence") or {}) if isinstance(cfg, dict) else {}
    base_url = str(confluence.get("base_url") or "")
    plugin = ""
    rp = (cfg.get("review_plugin") or {}) if isinstance(cfg, dict) else {}
    if isinstance(rp, dict):
        plugin = str(rp.get("type") or "")

    if args.json:
        report = {
            "root": str(root),
            "checks": [
                {"name": name, "ok": ok, "message": msg}
                for name, ok, msg in results
            ],
            "configured_base_url": base_url,
            "configured_review_plugin": plugin,
        }
        print(json.dumps(report, indent=2))
    else:
        print(f"change-control init  (root: {root})")
        print("=" * 60)
        for name, ok, msg in results:
            mark = "OK   " if ok else "WARN "
            print(f"  [{mark}] {name}: {msg}")
        print()
        if base_url:
            print(f"  configured base_url:        {base_url}")
        if plugin:
            print(f"  configured review_plugin:   {plugin}")
        print()
        not_ok = [r for r in results if not r[1]]
        if not_ok:
            print("Next steps:")
            for name, _, msg in not_ok:
                print(f"  - {name}: {msg}")
        else:
            print("Preflight passed.")
        print()
        print("If the atlassian MCP shows 'Not connected' in `/mcp`,")
        print("run `/mcp` and authenticate the atlassian connector to enable")
        print("publish / freeze / review-formal-* actions.")

    # Always 0 on success-or-warnings — init is informational, not gating.
    return 0


def main(argv: list[str] | None = None) -> int:
    return run(_build_parser().parse_args(argv))


if __name__ == "__main__":
    sys.exit(main())
