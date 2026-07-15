"""Setup section loaders — the project-settings surface.

Connectors (the original section) merge three sources into one per-connector
status model:

- `.mcp.json` `mcpServers`          → definitions (type, command/args or url, env KEYS)
- `project.yml security.approved_mcps` → allowlist membership
- `console/setup/catalog.py`        → which connectors the console can configure

The sibling section loaders (`load_skills`, `load_agents`, `load_plugins`,
`load_rules_hooks`, `load_team_security`) apply the same installed-vs-approved
pattern to the rest of the project's tool surface, each read-only:

- `.claude/skills/*/`   × `security.approved_skills`
- `.claude/agents/*.md` × `security.approved_agents`
- (none — allowlist only) × `security.approved_plugins`
- `.claude/rules/*.md` + `.claude/settings.json` hooks (inventory, no allowlist)
- `project.yml team.*` + `security` + `registries[]` (posture summary)

`load_setup` aggregates everything for the settings shell template.

Every loader is defensive: a missing or malformed file degrades to an empty
contribution plus a surfaced warning — it never raises into the route. Env
var VALUES are never returned to callers; only the key name and whether a
non-empty value is present ("set"). Secrets stay out of the browser.
"""
from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

import yaml

MCP_JSON_REL = ".mcp.json"
PROJECT_YML_REL = "project.yml"

MASK = "•••"


def mcp_json_path(repo_root: Path) -> Path:
    return repo_root / MCP_JSON_REL


def project_yml_path(repo_root: Path) -> Path:
    return repo_root / PROJECT_YML_REL


def load_mcp_servers(repo_root: Path) -> tuple[dict, list[str]]:
    """Return ({name: spec}, warnings). Missing file → empty dict, no warning."""
    p = mcp_json_path(repo_root)
    if not p.is_file():
        return {}, []
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        return {}, [f"{MCP_JSON_REL} could not be parsed: {e}"]
    servers = data.get("mcpServers")
    if not isinstance(servers, dict):
        return {}, [f"{MCP_JSON_REL} has no mcpServers object"]
    return servers, []


def load_approved_mcps(repo_root: Path) -> tuple[list[str], list[str]]:
    """Return (approved names, warnings) from project.yml security.approved_mcps."""
    p = project_yml_path(repo_root)
    if not p.is_file():
        return [], [f"{PROJECT_YML_REL} not found"]
    try:
        data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    except (yaml.YAMLError, OSError) as e:
        return [], [f"{PROJECT_YML_REL} could not be parsed: {e}"]
    approved = (data.get("security") or {}).get("approved_mcps")
    if approved is None:
        return [], [f"{PROJECT_YML_REL} has no security.approved_mcps list"]
    return [str(x) for x in approved], []


def _probe_command(repo_root: Path, command: str) -> dict:
    """Cheap existence probe for a stdio server's launch command.

    Repo-relative paths (./…) are stat'ed; bare commands resolved via PATH.
    Result is advisory — the console never launches the command.
    """
    if command.startswith("./") or command.startswith("../"):
        target = (repo_root / command).resolve()
        ok = target.is_file()
        return {
            "kind": "path",
            "ok": ok,
            "detail": command if ok else f"{command} not found in project",
        }
    resolved = shutil.which(command)
    return {
        "kind": "which",
        "ok": resolved is not None,
        "detail": resolved or f"{command} not on PATH",
    }


def _env_summary(spec: dict) -> list[dict]:
    """Env KEYS with set/empty state — values are never surfaced."""
    env = spec.get("env") or {}
    if not isinstance(env, dict):
        return []
    return [
        {"key": str(k), "set": bool(str(v or "").strip())}
        for k, v in env.items()
    ]


def _masked_spec(spec: dict) -> dict:
    """Copy of the server spec safe to render: env values replaced by a mask."""
    out = dict(spec)
    env = spec.get("env")
    if isinstance(env, dict):
        out["env"] = {
            str(k): (MASK if str(v or "").strip() else "")
            for k, v in env.items()
        }
    return out


def load_connectors(repo_root: Path) -> dict:
    """The merged Setup data model.

    Returns {connectors: [...], warnings: [...], sources: {...}} where each
    connector row carries: name, configured, approved, status, spec (masked),
    env (keys + set flags), probe, transport.
    """
    servers, w1 = load_mcp_servers(repo_root)
    approved, w2 = load_approved_mcps(repo_root)
    warnings = w1 + w2

    rows: list[dict] = []
    for name in sorted(set(servers) | set(approved)):
        spec = servers.get(name)
        configured = spec is not None
        is_approved = name in approved
        row: dict = {
            "name": name,
            "configured": configured,
            "approved": is_approved,
        }
        if configured:
            transport = str(spec.get("type") or ("http" if spec.get("url") else "stdio"))
            row["transport"] = transport
            row["spec"] = _masked_spec(spec)
            row["env"] = _env_summary(spec)
            command = spec.get("command")
            if transport == "stdio" and command:
                row["probe"] = _probe_command(repo_root, str(command))
        if configured and is_approved:
            row["status"] = "ok"
            row["status_note"] = ""
        elif configured:
            row["status"] = "warning"
            row["status_note"] = (
                "Defined in .mcp.json but not in project.yml "
                "security.approved_mcps — the security posture check will flag it."
            )
        else:
            row["status"] = "info"
            row["status_note"] = (
                "Approved in project.yml but not defined in .mcp.json — "
                "approved but not installed."
            )
        rows.append(row)

    return {
        "connectors": rows,
        "warnings": warnings,
        "sources": {
            "mcp_json": MCP_JSON_REL,
            "mcp_json_exists": mcp_json_path(repo_root).is_file(),
            "project_yml": PROJECT_YML_REL,
        },
    }


# ---------------------------------------------------------------------------
# Shared helpers for the non-connector sections
# ---------------------------------------------------------------------------

_FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def _load_project_yml(repo_root: Path) -> tuple[dict, list[str]]:
    p = project_yml_path(repo_root)
    if not p.is_file():
        return {}, [f"{PROJECT_YML_REL} not found"]
    try:
        return yaml.safe_load(p.read_text(encoding="utf-8")) or {}, []
    except (yaml.YAMLError, OSError) as e:
        return {}, [f"{PROJECT_YML_REL} could not be parsed: {e}"]


def _approved_list(project: dict, key: str) -> list[str]:
    val = (project.get("security") or {}).get(key)
    if not isinstance(val, list):
        return []
    return [str(x) for x in val]


def _frontmatter(path: Path) -> dict:
    """Best-effort YAML frontmatter of a markdown file; {} on any failure."""
    try:
        m = _FRONTMATTER_RE.match(path.read_text(encoding="utf-8"))
        if not m:
            return {}
        data = yaml.safe_load(m.group(1))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _clip(text, max_chars: int = 900) -> str:
    text = " ".join(str(text or "").split())
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rsplit(" ", 1)[0] + "…"


_SKILL_SURFACE_DIRS = ("actions", "agents", "hooks", "rules", "scripts", "templates", "references")


def _skill_surface(skill_dir: Path) -> list[str]:
    """Which conventional component dirs a skill ships (cheap capability hint)."""
    return [d for d in _SKILL_SURFACE_DIRS if (skill_dir / d).is_dir()]


def _first_sentence(text: str, max_chars: int = 180) -> str:
    text = " ".join(str(text or "").split())
    for stop in (". ", " — ", " - "):
        idx = text.find(stop)
        if 0 < idx < max_chars:
            return text[: idx + (1 if stop == ". " else 0)]
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rsplit(" ", 1)[0] + "…"


def _symlink_owner(path: Path) -> str | None:
    """For a symlink into a skill tree, return the owning skill name."""
    try:
        if not path.is_symlink():
            return None
        target = path.readlink().as_posix()
    except OSError:
        return None
    m = re.search(r"skills/([^/]+)/", target)
    return m.group(1) if m else None


def _status_row(installed: bool, approved: bool, flag_noun: str) -> tuple[str, str]:
    """The shared installed-vs-approved status triad."""
    if installed and approved:
        return "ok", ""
    if installed:
        return "warning", (
            f"Installed but not in project.yml security.{flag_noun} — "
            "the security posture check will flag it."
        )
    return "info", (
        f"Approved in project.yml security.{flag_noun} but not installed."
    )


# ---------------------------------------------------------------------------
# Skills
# ---------------------------------------------------------------------------

def load_skills(repo_root: Path, project: dict) -> dict:
    """Installed skills (.claude/skills/*/SKILL.md) × approved_skills."""
    skills_dir = repo_root / ".claude" / "skills"
    approved = _approved_list(project, "approved_skills")
    builtin: set[str] = set()
    for reg in project.get("registries") or []:
        if isinstance(reg, dict) and reg.get("type") == "builtin":
            builtin.update(str(s) for s in reg.get("skills") or [])

    installed: dict[str, dict] = {}
    if skills_dir.is_dir():
        for d in sorted(skills_dir.iterdir()):
            if not d.is_dir() or not (d / "SKILL.md").is_file():
                continue
            fm = _frontmatter(d / "SKILL.md")
            version = ""
            vfile = d / "VERSION"
            if vfile.is_file():
                try:
                    version = vfile.read_text(encoding="utf-8").strip()
                except OSError:
                    version = ""
            installed[d.name] = {
                "version": version or str(fm.get("version") or ""),
                "description": _first_sentence(fm.get("description") or ""),
                "full_description": _clip(fm.get("description"), 900),
                "updated": str(fm.get("updated") or ""),
                "path": f".claude/skills/{d.name}/",
                "files": _skill_surface(d),
            }

    rows = []
    for name in sorted(set(installed) | set(approved)):
        meta = installed.get(name)
        is_installed = meta is not None
        is_approved = name in approved
        status, note = _status_row(is_installed, is_approved, "approved_skills")
        if not is_installed and name in builtin:
            status, note = "ok", ""
        rows.append({
            "name": name,
            "installed": is_installed,
            "approved": is_approved,
            "builtin": name in builtin,
            "version": (meta or {}).get("version", ""),
            "description": (meta or {}).get("description", ""),
            "full_description": (meta or {}).get("full_description", ""),
            "updated": (meta or {}).get("updated", ""),
            "path": (meta or {}).get("path", ""),
            "files": (meta or {}).get("files", []),
            "status": status,
            "status_note": note,
        })
    return {"rows": rows, "counts": _counts(rows)}


# ---------------------------------------------------------------------------
# Agents
# ---------------------------------------------------------------------------

def load_agents(repo_root: Path, project: dict) -> dict:
    """Agents × approved_agents, from BOTH install surfaces:

    - `.claude/agents/*.md` — top-level registered agents (source: installed)
    - `.claude/skills/*/agents/*.md` — skill-bundled agents a skill spawns via
      prompt file without registering top-level (source: bundled); skipped
      when a top-level agent of the same name exists (it's usually the
      symlink target).

    approved_agents entries may be bare names (`project-secops`) or
    skill-relative paths (`red-team/agents/ceo-skeptic`) — matched on the
    final path segment.
    """
    agents_dir = repo_root / ".claude" / "agents"
    approved_raw = _approved_list(project, "approved_agents")
    approved = {entry.rsplit("/", 1)[-1] for entry in approved_raw}

    rows = []
    seen: set[str] = set()
    if agents_dir.is_dir():
        for f in sorted(agents_dir.glob("*.md")):
            name = f.stem
            seen.add(name)
            fm = _frontmatter(f)
            is_approved = name in approved
            status, note = _status_row(True, is_approved, "approved_agents")
            tools = fm.get("tools")
            if isinstance(tools, list):
                tools = ", ".join(str(t) for t in tools)
            target = ""
            try:
                if f.is_symlink():
                    target = f.readlink().as_posix().lstrip("./")
            except OSError:
                target = ""
            rows.append({
                "name": name,
                "installed": True,
                "approved": is_approved,
                "owner": _symlink_owner(f) or "project",
                "description": _first_sentence(fm.get("description") or ""),
                "full_description": _clip(fm.get("description"), 900),
                "path": f".claude/agents/{f.name}",
                "target": target,
                "tools": str(tools or ""),
                "model": str(fm.get("model") or ""),
                "source": "installed",
                "status": status,
                "status_note": note,
            })

    skills_dir = repo_root / ".claude" / "skills"
    approved_skills = set(_approved_list(project, "approved_skills"))
    if skills_dir.is_dir():
        for f in sorted(skills_dir.glob("*/agents/*.md")):
            name = f.stem
            if name in seen:
                continue
            seen.add(name)
            fm = _frontmatter(f)
            owner_skill = f.parent.parent.name
            is_approved = name in approved
            # Bundled agents inherit approval from their approved owning
            # skill: they are the skill's internal workers, spawned by it and
            # audited with it. Explicit listing (e.g. for agents other skills
            # borrow) still works and is shown as such.
            if is_approved:
                status, note = "ok", ""
            elif owner_skill in approved_skills:
                status, note = "ok", "approved via the owning skill (security.approved_skills)"
            else:
                status, note = _status_row(True, False, "approved_agents")
            tools = fm.get("tools")
            if isinstance(tools, list):
                tools = ", ".join(str(t) for t in tools)
            rows.append({
                "name": name,
                "installed": True,
                "approved": is_approved,
                "owner": f.parent.parent.name,
                "description": _first_sentence(fm.get("description") or ""),
                "full_description": _clip(fm.get("description"), 900),
                "path": f.relative_to(repo_root).as_posix(),
                "target": "",
                "tools": str(tools or ""),
                "model": str(fm.get("model") or ""),
                "source": "bundled",
                "approved_via": "" if is_approved else (
                    "skill" if status == "ok" else ""),
                "status": status,
                "status_note": note,
            })
        rows.sort(key=lambda r: r["name"])

    for name in sorted(approved - seen):
        status, note = _status_row(False, True, "approved_agents")
        rows.append({
            "name": name, "installed": False, "approved": True,
            "owner": "", "description": "", "full_description": "",
            "path": "", "target": "", "tools": "", "model": "",
            "source": "", "status": status, "status_note": note,
        })
    return {"rows": rows, "counts": _counts(rows)}


# ---------------------------------------------------------------------------
# Plugins
# ---------------------------------------------------------------------------

def load_plugins(repo_root: Path, project: dict) -> dict:
    """Plugin allowlist — installs live outside the repo, so this section is
    allowlist-only (an empty list is itself posture information)."""
    rows = [
        {"name": name, "installed": None, "approved": True,
         "status": "ok", "status_note": ""}
        for name in sorted(_approved_list(project, "approved_plugins"))
    ]
    return {"rows": rows, "counts": _counts(rows)}


# ---------------------------------------------------------------------------
# Rules & hooks
# ---------------------------------------------------------------------------

def load_rules_hooks(repo_root: Path) -> dict:
    """Inventory of auto-loaded rules and registered hooks (no allowlist)."""
    rules = []
    rules_dir = repo_root / ".claude" / "rules"
    if rules_dir.is_dir():
        for f in sorted(rules_dir.glob("*.md")):
            title, summary, target = "", "", ""
            try:
                if f.is_symlink():
                    target = f.readlink().as_posix().lstrip("./")
                for line in f.read_text(encoding="utf-8").splitlines():
                    line = line.strip()
                    if not title and line.startswith("# "):
                        title = line[2:].strip()
                    elif title and line and not line.startswith(("#", "<!--", "|", "-", "```")):
                        summary = _clip(line, 320)
                        break
            except OSError:
                pass
            rules.append({
                "name": f.stem,
                "owner": _symlink_owner(f) or "project",
                "path": f".claude/rules/{f.name}",
                "target": target,
                "title": title,
                "summary": summary,
            })

    hooks = []
    settings = repo_root / ".claude" / "settings.json"
    if settings.is_file():
        try:
            cfg = json.loads(settings.read_text(encoding="utf-8"))
            for event, entries in (cfg.get("hooks") or {}).items():
                if not isinstance(entries, list):
                    continue
                for entry in entries:
                    matcher = str(entry.get("matcher") or "")
                    for h in entry.get("hooks") or []:
                        cmd = str(h.get("command") or "")
                        hooks.append({
                            "event": str(event),
                            "matcher": matcher,
                            "command": cmd.rsplit("/", 1)[-1].strip('"'),
                            "command_full": cmd.replace('"$CLAUDE_PROJECT_DIR"/', ""),
                        })
        except (json.JSONDecodeError, OSError):
            pass
    return {"rules": rules, "hooks": hooks}


# ---------------------------------------------------------------------------
# Team & security posture
# ---------------------------------------------------------------------------

def load_team_security(project: dict) -> dict:
    team = project.get("team") or {}
    members = [
        {
            "name": str(m.get("name") or ""),
            "role": str(m.get("role") or ""),
            "github": str(m.get("github") or ""),
        }
        for m in (team.get("active") or [])
        if isinstance(m, dict)
    ]
    registries = [
        {
            "name": str(r.get("name") or ""),
            "type": str(r.get("type") or ""),
            "repo": str(r.get("repo") or ""),
            "skills": len(r.get("skills") or []),
        }
        for r in (project.get("registries") or [])
        if isinstance(r, dict)
    ]
    security = project.get("security") or {}
    return {
        "members": members,
        "inactive_count": len(team.get("inactive") or []),
        "registries": registries,
        "email_domains": [str(x) for x in security.get("approved_email_domains") or []],
        "allowlist_counts": {
            key.replace("approved_", ""): len(security.get(key) or [])
            for key in ("approved_skills", "approved_mcps",
                        "approved_plugins", "approved_agents")
        },
    }


def _counts(rows: list[dict]) -> dict:
    return {
        "total": len(rows),
        "ok": sum(1 for r in rows if r["status"] == "ok"),
        "warning": sum(1 for r in rows if r["status"] == "warning"),
        "info": sum(1 for r in rows if r["status"] == "info"),
    }


# ---------------------------------------------------------------------------
# Aggregate
# ---------------------------------------------------------------------------

def load_setup(repo_root: Path) -> dict:
    """Everything the settings shell renders, in one defensive call."""
    project, warnings = _load_project_yml(repo_root)
    connectors = load_connectors(repo_root)
    return {
        "connectors": connectors,
        "skills": load_skills(repo_root, project),
        "agents": load_agents(repo_root, project),
        "plugins": load_plugins(repo_root, project),
        "rules_hooks": load_rules_hooks(repo_root),
        "team": load_team_security(project),
        "warnings": warnings,
    }
