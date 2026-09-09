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
import subprocess
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


def _fallback_fm(block: str) -> dict:
    """Line-oriented frontmatter parser for blocks strict YAML rejects.

    Agent descriptions are prose and routinely contain unquoted `: ` (e.g.
    "the economic buyer: weighs …"), which is a yaml.safe_load parse error.
    This fallback treats the block as `key: value` lines at indent 0, where a
    value continues across subsequent indented lines and supports `>` / `|`
    block scalars. Values are kept as plain strings.
    """
    fields: dict = {}
    key = None
    buf: list[str] = []
    key_re = re.compile(r"^([A-Za-z_][\w-]*):\s?(.*)$")

    def flush():
        nonlocal key, buf
        if key is not None:
            val = " ".join(s.strip() for s in buf if s.strip())
            if val.startswith((">", "|")):
                val = val[1:].lstrip("-+ ").strip()
            if len(val) >= 2 and val[0] == val[-1] and val[0] in "'\"":
                val = val[1:-1]
            fields[key] = val
        key, buf = None, []

    for line in block.splitlines():
        m = key_re.match(line)
        if m and not line[:1].isspace():
            flush()
            key = m.group(1)
            buf = [m.group(2)]
        elif key is not None:
            buf.append(line)
    flush()
    return fields


def _body_summary(path: Path) -> str:
    """First prose paragraph of a markdown file (after any frontmatter /
    leading headings) — the summary of record for frontmatter-less agent
    prompt files, which conventionally open with `# Title` + a role line."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return ""
    text = _FRONTMATTER_RE.sub("", text, count=1)
    para: list[str] = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith(("#", "<!--", "|", "-", "*", "```", ">")):
            if para:
                break  # end of the first prose paragraph (hard-wrapped lines joined)
            continue
        para.append(line)
    return " ".join(para)


def _frontmatter(path: Path) -> dict:
    """Best-effort YAML frontmatter of a markdown file; {} on any failure.

    Strict YAML first; if that fails (prose descriptions with unquoted
    colons are common in agent files), fall back to a tolerant line parser
    so the description/tools/model still surface.
    """
    try:
        m = _FRONTMATTER_RE.match(path.read_text(encoding="utf-8"))
        if not m:
            return {}
    except OSError:
        return {}
    block = m.group(1)
    try:
        data = yaml.safe_load(block)
        if isinstance(data, dict):
            return data
    except yaml.YAMLError:
        pass
    return _fallback_fm(block)


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
            desc = str(fm.get("description") or "") or _body_summary(f)
            rows.append({
                "name": name,
                "installed": True,
                "approved": is_approved,
                "owner": _symlink_owner(f) or "project",
                "description": _first_sentence(desc),
                "full_description": _clip(desc, 900),
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
            desc = str(fm.get("description") or "") or _body_summary(f)
            rows.append({
                "name": name,
                "installed": True,
                "approved": is_approved,
                "owner": f.parent.parent.name,
                "description": _first_sentence(desc),
                "full_description": _clip(desc, 900),
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
                        # The registered command points at a script (usually a
                        # .claude/hooks/ symlink into the owning skill). The
                        # script's own header comment is its description — the
                        # convention skill-creator's hook template stamps.
                        script = _hook_script_path(repo_root, cmd)
                        desc = _script_summary(script) if script else ""
                        owner = (_symlink_owner(script) or "project") if script else "project"
                        hooks.append({
                            "event": str(event),
                            "matcher": matcher,
                            "command": cmd.rsplit("/", 1)[-1].strip('"'),
                            "command_full": cmd.replace('"$CLAUDE_PROJECT_DIR"/', ""),
                            "description": _first_sentence(desc),
                            "full_description": _clip(desc, 600),
                            "owner": owner,
                        })
        except (json.JSONDecodeError, OSError):
            pass
    return {"rules": rules, "hooks": hooks}


def _hook_script_path(repo_root: Path, command: str) -> Path | None:
    """Best-effort script path from a registered hook command string
    (e.g. '"$CLAUDE_PROJECT_DIR"/.claude/hooks/x.sh --flag')."""
    m = re.search(r"\.claude/hooks/[\w./-]+", command or "")
    if not m:
        return None
    p = repo_root / m.group(0)
    return p if p.is_file() else None


def _script_summary(path: Path) -> str:
    """Description from a script's leading header — the `#` comment block
    after the shebang (shell) or the module docstring (python). A
    `name.sh — description` first line yields just the description."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return ""
    lines = text.splitlines()
    if lines and lines[0].startswith("#!"):
        lines = lines[1:]
    # python module docstring
    body = "\n".join(lines).lstrip()
    for quote in ('"""', "'''"):
        if body.startswith(quote):
            end = body.find(quote, 3)
            para = body[3:end if end > 0 else None].strip()
            return " ".join(para.split("\n\n", 1)[0].split())
    # shell/other: leading comment block, first paragraph
    para: list[str] = []
    for line in lines:
        s = line.strip()
        if not s.startswith("#"):
            break
        s = s.lstrip("#").strip()
        if not s or set(s) <= {"─", "-", "="}:  # blank or divider comment
            if para:
                break
            continue
        para.append(s)
    summary = " ".join(para)
    # 'name.sh — description' convention → keep the description side
    m = re.match(r"^\S+\.(?:sh|py|bash)\s+[—-]+\s+(.*)$", summary)
    return m.group(1) if m else summary


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
            "task_folder": str(m.get("task_folder") or ""),
            "email": str(m.get("email") or ""),
            "added": str(m.get("added") or ""),
        }
        for m in (team.get("active") or [])
        if isinstance(m, dict)
    ]
    inactive = [
        {
            "name": str(m.get("name") or ""),
            "role": str(m.get("role") or ""),
            "github": str(m.get("github") or ""),
            "removed": str(m.get("removed") or ""),
            "reason": str(m.get("reason") or ""),
        }
        for m in (team.get("inactive") or [])
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
        "inactive": inactive,
        "inactive_count": len(inactive),
        "repo": str((project.get("project") or {}).get("repo") or ""),
        "registries": registries,
        "email_domains": [str(x) for x in security.get("approved_email_domains") or []],
        "allowlist_counts": {
            key.replace("approved_", ""): len(security.get(key) or [])
            for key in ("approved_skills", "approved_mcps",
                        "approved_plugins", "approved_agents")
        },
    }


# ---------------------------------------------------------------------------
# Command-line tooling (read-only probes — the console never installs or
# authenticates anything; it detects state and shows the fix commands)
# ---------------------------------------------------------------------------

def _probe(cmd: list[str], timeout: int = 5) -> tuple[int, str]:
    """Run a read-only diagnostic command. Never raises."""
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.returncode, (r.stdout + r.stderr).strip()
    except FileNotFoundError:
        return 127, ""
    except Exception as e:  # timeout, permission, …
        return 1, str(e)


def parse_gh_auth(output: str) -> dict:
    """Extract login state from `gh auth status` output (any gh 2.x format).
    Pure function — unit-testable without a gh install."""
    m = re.search(r"Logged in to (\S+?)(?: account| as) (\S+)", output or "")
    if m:
        return {"logged_in": True, "host": m.group(1), "account": m.group(2)}
    return {"logged_in": False, "host": "", "account": ""}


def load_cli_tooling(repo_root: Path) -> dict:
    """Detect the git/gh command-line tooling this project's workflow needs.
    Read-only: presence, version, auth state, repo remote — plus the
    copy-paste fix command when something is missing. Installation and
    `gh auth login` (interactive OAuth) happen in the user's terminal."""
    tools: list[dict] = []

    git_path = shutil.which("git")
    version = detail = ""
    if git_path:
        _, out = _probe(["git", "--version"])
        version = out.removeprefix("git version").strip()
        rc, remote = _probe(["git", "-C", str(repo_root), "remote", "get-url", "origin"])
        detail = f"origin: {remote}" if rc == 0 and remote else "no origin remote configured"
    tools.append({
        "name": "git",
        "title": "git",
        "installed": bool(git_path),
        "version": version,
        "detail": detail,
        "status": "ok" if git_path else "warning",
        "fix": "" if git_path else "xcode-select --install   (or: brew install git)",
    })

    gh_path = shutil.which("gh")
    version = detail = fix = ""
    status = "warning"
    if gh_path:
        _, vout = _probe(["gh", "--version"])
        m = re.search(r"gh version (\S+)", vout)
        version = m.group(1) if m else ""
        _, aout = _probe(["gh", "auth", "status"])
        auth = parse_gh_auth(aout)
        if auth["logged_in"]:
            status = "ok"
            detail = f"authenticated as {auth['account']} ({auth['host']})"
        else:
            detail = "installed but not authenticated"
            fix = "gh auth login"
    else:
        detail = "not installed — the project's push workflow (PR create/merge) needs it"
        fix = "brew install gh && gh auth login"
    tools.append({
        "name": "gh",
        "title": "GitHub CLI (gh)",
        "installed": bool(gh_path),
        "version": version,
        "detail": detail,
        "status": status,
        "fix": fix,
    })

    return {"tools": tools, "counts": _counts(tools)}


def _counts(rows: list[dict]) -> dict:
    return {
        "total": len(rows),
        "ok": sum(1 for r in rows if r["status"] == "ok"),
        "warning": sum(1 for r in rows if r["status"] == "warning"),
        "info": sum(1 for r in rows if r["status"] == "info"),
    }


# ---------------------------------------------------------------------------
# GitHub workflows (repo automation)
# ---------------------------------------------------------------------------

def _workflow_triggers(data: dict) -> list[str]:
    """Human-readable trigger list from a workflow's `on:` block.

    YAML 1.1 parses the bare key `on` as boolean True — read both spellings.
    """
    on = data.get("on", data.get(True))
    out: list[str] = []
    if isinstance(on, str):
        return [on]
    if isinstance(on, list):
        return [str(x) for x in on]
    if not isinstance(on, dict):
        return []
    for event, cfg in on.items():
        event = "manual (workflow_dispatch)" if event == "workflow_dispatch" else str(event)
        if isinstance(cfg, dict):
            bits = []
            for k in ("branches", "paths", "types"):
                v = cfg.get(k)
                if isinstance(v, list) and v:
                    bits.append(f"{k}: {', '.join(str(x) for x in v)}")
            if event == "schedule":
                pass
            out.append(f"{event} ({'; '.join(bits)})" if bits else event)
        elif isinstance(cfg, list) and event == "schedule":
            crons = [c.get("cron") for c in cfg if isinstance(c, dict) and c.get("cron")]
            out.append(f"schedule (cron: {'; '.join(crons)})" if crons else "schedule")
        else:
            out.append(event)
    return out


def _skill_text_index(repo_root: Path) -> dict[str, str]:
    """skill-name → concatenated small-text-file content, for ownership grep."""
    index: dict[str, str] = {}
    skills_dir = repo_root / ".claude" / "skills"
    if not skills_dir.is_dir():
        return index
    for d in skills_dir.iterdir():
        if not d.is_dir():
            continue
        chunks: list[str] = []
        for f in d.rglob("*"):
            if f.suffix not in (".md", ".py", ".sh", ".yml", ".yaml"):
                continue
            try:
                if f.stat().st_size > 200_000:
                    continue
                chunks.append(f.read_text(encoding="utf-8", errors="ignore"))
            except OSError:
                continue
        index[d.name] = "\n".join(chunks)
    return index


def load_workflows(repo_root: Path) -> dict:
    """Inventory of .github/workflows/*.yml: what each is, what triggers it,
    and which installed skill owns it (a skill that scaffolds or documents the
    workflow file mentions its filename; otherwise it's project-authored)."""
    wf_dir = repo_root / ".github" / "workflows"
    rows: list[dict] = []
    if not wf_dir.is_dir():
        return {"rows": rows}
    skill_texts = _skill_text_index(repo_root)
    for f in sorted(list(wf_dir.glob("*.yml")) + list(wf_dir.glob("*.yaml"))):
        try:
            text = f.read_text(encoding="utf-8")
        except OSError:
            continue
        try:
            data = yaml.safe_load(text) or {}
        except yaml.YAMLError:
            data = {}
        if not isinstance(data, dict):
            data = {}
        # Leading comment block = the workflow's own description of record.
        comment: list[str] = []
        for line in text.splitlines():
            if line.startswith("#"):
                comment.append(line.lstrip("# ").strip())
            elif line.strip():
                break
        jobs = data.get("jobs")
        job_names = list(jobs.keys()) if isinstance(jobs, dict) else []
        owner = next(
            (s for s, blob in skill_texts.items() if f.name in blob), "project"
        )
        rows.append({
            "name": str(data.get("name") or f.stem),
            "file": f".github/workflows/{f.name}",
            "triggers": _workflow_triggers(data),
            "jobs": job_names,
            "description": _clip(" ".join(c for c in comment if c), 400),
            "owner": owner,
        })
    return {"rows": rows}


# ---------------------------------------------------------------------------
# Registries
# ---------------------------------------------------------------------------

def _version_key(v: str) -> tuple:
    """Loose version ordering: numeric runs compared as ints ('1.32.0', '11')."""
    nums = re.findall(r"\d+", str(v or ""))
    return tuple(int(n) for n in nums) if nums else (0,)


def _skill_version(skill_dir: Path) -> str:
    vfile = skill_dir / "VERSION"
    if vfile.is_file():
        try:
            v = vfile.read_text(encoding="utf-8").strip()
            if v:
                return v
        except OSError:
            pass
    return str(_frontmatter(skill_dir / "SKILL.md").get("version") or "")


def _registry_status(reg_v: str, loc_v: str | None) -> str:
    if loc_v is None:
        return "not-installed"
    if _version_key(reg_v) > _version_key(loc_v):
        return "update"
    if _version_key(reg_v) < _version_key(loc_v):
        return "local-ahead"
    return "current"


def load_registries(repo_root: Path, project: dict) -> dict:
    """Configured registries (project.yml registries[]) + per-registry skill
    availability vs the local install.

    Catalog source order for a `github`-type registry:

    1. the cached **GitHub catalog** (`.state/registry-catalog-<name>.json`,
       written by the Refresh-from-GitHub action) — works with read-only
       repo access and no local clone;
    2. the **local clone** (`local_path`, the sync tooling's checkout) when
       no GitHub catalog has been fetched yet;
    3. neither → `reachable: false` with a Refresh hint.

    Statuses are recomputed per request against the CURRENT local install,
    so an install/update reflects immediately even with an older cache:

    - `not-installed` → available to Add
    - `update`        → registry version is newer than the installed one
    - `local-ahead`   → installed version is newer (push candidate; no button,
                        an update here would be a downgrade)
    - `current`       → versions match

    Reads only; installs go through the writer.
    """
    installed: dict[str, str] = {}
    skills_dir = repo_root / ".claude" / "skills"
    if skills_dir.is_dir():
        for d in skills_dir.iterdir():
            if d.is_dir() and (d / "SKILL.md").is_file():
                installed[d.name] = _skill_version(d)

    def _local_desc(name: str) -> tuple[str, str]:
        fm = _frontmatter(skills_dir / name / "SKILL.md")
        desc = str(fm.get("description") or "")
        return _first_sentence(desc), _clip(desc, 900)

    registries = []
    actionable = 0
    for reg in project.get("registries") or []:
        if not isinstance(reg, dict):
            continue
        entry: dict = {
            "name": str(reg.get("name") or ""),
            "type": str(reg.get("type") or ""),
            "repo": str(reg.get("repo") or ""),
            "description": str(reg.get("description") or ""),
            "local_path": str(reg.get("local_path") or ""),
            "reachable": None,
            "source": "",
            "fetched_at": "",
            "skills": [],
        }
        cached = None
        if entry["type"] == "builtin":
            entry["reachable"] = True
            entry["skills"] = [
                {"name": str(s), "status": "builtin", "description": "",
                 "registry_version": "", "local_version": ""}
                for s in reg.get("skills") or []
            ]
            registries.append(entry)
            continue

        if entry["repo"]:
            from console.setup.registry_remote import load_cached_catalog
            cached = load_cached_catalog(repo_root, entry["name"])

        if cached:
            entry["reachable"] = True
            entry["source"] = "github"
            entry["fetched_at"] = str(cached.get("fetched_at") or "")
            for name in sorted(cached.get("skills") or {}):
                info = cached["skills"][name] or {}
                reg_v = str(info.get("version") or "")
                loc_v = installed.get(name)
                status = _registry_status(reg_v, loc_v)
                if status in ("not-installed", "update"):
                    actionable += 1
                desc, full = str(info.get("description") or ""), str(info.get("full_description") or "")
                if not desc and loc_v is not None:
                    desc, full = _local_desc(name)
                entry["skills"].append({
                    "name": name,
                    "description": desc,
                    "full_description": full,
                    "registry_version": reg_v,
                    "local_version": loc_v or "",
                    "status": status,
                })
        elif entry["local_path"]:
            root = (repo_root / entry["local_path"]).resolve()
            catalog = root / "skills"
            entry["reachable"] = catalog.is_dir()
            entry["source"] = "clone" if entry["reachable"] else ""
            if entry["reachable"]:
                for d in sorted(catalog.iterdir()):
                    if not d.is_dir() or not (d / "SKILL.md").is_file():
                        continue
                    fm = _frontmatter(d / "SKILL.md")
                    reg_v = _skill_version(d)
                    loc_v = installed.get(d.name)
                    status = _registry_status(reg_v, loc_v)
                    if status in ("not-installed", "update"):
                        actionable += 1
                    entry["skills"].append({
                        "name": d.name,
                        "description": _first_sentence(fm.get("description") or ""),
                        "full_description": _clip(fm.get("description"), 900),
                        "registry_version": reg_v,
                        "local_version": loc_v or "",
                        "status": status,
                    })
        else:
            entry["reachable"] = False
        registries.append(entry)

    return {"registries": registries, "actionable": actionable}


# ---------------------------------------------------------------------------
# Aggregate
# ---------------------------------------------------------------------------

def load_setup(repo_root: Path, run_id: str | None = None) -> dict:
    """Everything the settings shell renders, in one defensive call.
    `run_id` selects which workbench-validation run revision the Validation
    section shows (default: latest)."""
    project, warnings = _load_project_yml(repo_root)
    connectors = load_connectors(repo_root)
    return {
        "project": load_project_settings(project),
        "connectors": connectors,
        "skills": load_skills(repo_root, project),
        "agents": load_agents(repo_root, project),
        "plugins": load_plugins(repo_root, project),
        "rules_hooks": load_rules_hooks(repo_root),
        "workflows": load_workflows(repo_root),
        "team": load_team_security(project),
        "team_access": _load_team_access(repo_root),
        "registries": load_registries(repo_root, project),
        "cli": load_cli_tooling(repo_root),
        "appearance": _load_appearance(),
        "environment": _load_environment(repo_root),
        "workbench": load_workbench_validation(repo_root, run_id=run_id),
        "warnings": warnings,
    }


WORKBENCH_SIDECAR_REL = "tools/workbench-validation/workbench-validation-index.json"
WORKBENCH_RUNNER_REL = ".claude/skills/workbench-validation/scripts/run_validation.py"
WORKBENCH_EXPORTER_REL = ".claude/skills/workbench-validation/scripts/export_package.py"
WORKBENCH_RESULTS_REL = "tools/workbench-validation/results"
WORKBENCH_INDEX_REL = "tools/workbench-validation/results/index.json"
WORKBENCH_EXPORT_FORMATS = {
    "docx": ("application/vnd.openxmlformats-officedocument.wordprocessingml.document", "docx"),
    "pdf": ("application/pdf", "pdf"),
    "md": ("text/markdown", "md"),
}


def _run_verdict_from_summary(summary: dict) -> str:
    bad = ("FAIL", "ERROR", "NOT-EXECUTED")
    return "FAIL" if any(summary.get(k) for k in bad) else "PASS"


def load_workbench_runs(repo_root: Path) -> list:
    """Roster of recorded validation runs, newest first. Reads the skill's
    `results/index.json` when present; otherwise derives the roster from the
    per-run `results/run-*.json` files so older skill versions still list."""
    results = repo_root / WORKBENCH_RESULTS_REL
    index = repo_root / WORKBENCH_INDEX_REL
    rows: list = []
    if index.is_file():
        try:
            data = json.loads(index.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                data = data.get("runs") or []
            rows = [r for r in data if isinstance(r, dict) and r.get("run_id")]
        except (OSError, json.JSONDecodeError):
            rows = []
    if not rows and results.is_dir():
        for f in results.glob("run-*.json"):
            try:
                d = json.loads(f.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            env = d.get("environment") or {}
            summary = d.get("summary") or {}
            rid = d.get("run_id") or f.stem
            rows.append({
                "run_id": rid,
                "started": d.get("started"),
                "finished": d.get("finished"),
                "verdict": _run_verdict_from_summary(summary),
                "summary": summary,
                "partial": bool(d.get("partial")),
                "invoked_via": d.get("invoked_via", "cli"),
                "schema_version": d.get("schema_version"),
                "git_sha_short": env.get("git_sha_short"),
                "git_dirty": env.get("git_dirty"),
                "model_id": env.get("model_id"),
                "sidecar": f"{WORKBENCH_RESULTS_REL}/{rid}/sidecar.json",
                "report": f"{WORKBENCH_RESULTS_REL}/{rid}/validation-report.md",
                "derived": True,
            })
    for r in rows:
        summ = r.get("summary") or {}
        r["total_cases"] = sum(v for v in summ.values() if isinstance(v, int))
        r["pass_cases"] = summ.get("PASS", 0)
        st = str(r.get("started") or "")
        r["started_label"] = (st[:10] + " " + st[11:16] + " UTC") if len(st) >= 16 else (st or "—")
        # Verdict-first outcome label with the counts spelled out, so the verdict
        # word never sits next to a pass count ("FAIL · 32/43 PASS" read as a
        # contradiction). e.g. "FAIL — 32 passed, 5 failed, 2 not executed, 4 n/a of 43".
        words = (("PASS", "passed"), ("FAIL", "failed"), ("ERROR", "errored"), ("SKIPPED", "skipped"),
                 ("NOT-EXECUTED", "not executed"), ("NOT-APPLICABLE", "n/a"))
        parts = [f"{summ[k]} {w}" for k, w in words if isinstance(summ.get(k), int) and summ.get(k)]
        r["outcome_label"] = f"{r.get('verdict') or '?'} — " + (", ".join(parts) if parts else "no cases") + f" of {r['total_cases']}"
    rows.sort(key=lambda r: (str(r.get("started") or ""), r.get("run_id") or ""), reverse=True)
    return rows


def load_workbench_validation(repo_root: Path, run_id: str | None = None) -> dict:
    """Setup → Workbench Validation: tool-validation posture of the .claude
    toolchain itself. Pure consumer of the workbench-validation skill's sidecar
    (needs × tests × report verdicts); the console computes nothing. Degrades to
    available=False when neither the skill nor a sidecar is present, and to an
    empty-state (available=True, data=None) when the skill is installed but no
    validation has been run yet."""
    sidecar = repo_root / WORKBENCH_SIDECAR_REL
    skill_installed = (repo_root / WORKBENCH_RUNNER_REL).is_file()
    runs = load_workbench_runs(repo_root)
    latest_id = runs[0]["run_id"] if runs else None
    selected = None
    if run_id:
        selected = next((r for r in runs if r["run_id"] == run_id), None)
    if selected is None:
        selected = runs[0] if runs else None
    is_latest = bool(selected) and selected["run_id"] == latest_id
    out = {
        "available": skill_installed or sidecar.is_file() or bool(runs),
        "skill_installed": skill_installed,
        "exporter_installed": (repo_root / WORKBENCH_EXPORTER_REL).is_file(),
        "sidecar": WORKBENCH_SIDECAR_REL,
        "data": None,
        "stale": None,
        "head_sha": None,
        # Run-revision selection: the roster of recorded runs (newest first),
        # which one this view shows, and whether it is the latest. A non-latest
        # revision reads its own per-run sidecar; a missing per-run sidecar is
        # reported, never silently substituted (only the latest may fall back
        # to the main sidecar, which is by construction the latest run's).
        "runs": runs,
        "selected_run": selected,
        "selected_run_id": selected["run_id"] if selected else None,
        "is_latest": is_latest,
        "unknown_run": bool(run_id) and selected is not None and selected["run_id"] != run_id,
        "revision_notice": None,
        "export_formats": list(WORKBENCH_EXPORT_FORMATS),
        # Named differences between the recorded environment and the repo as
        # it is now (D8): "stale" is no longer a single SHA comparison but a
        # list a reviewer can read — commit moved, which skills changed
        # version, hooks added/removed. Empty list + stale=False means the
        # recorded environment still describes this checkout.
        "differences": [],
        "dirty_at_run": None,
        "model_captured": None,
    }
    source = None
    if selected:
        per_run = repo_root / str(selected.get("sidecar") or f"{WORKBENCH_RESULTS_REL}/{selected['run_id']}/sidecar.json")
        if per_run.is_file():
            source = per_run
        elif is_latest and sidecar.is_file():
            source = sidecar
        else:
            out["revision_notice"] = (
                f"Revision {selected['run_id']} has no rendered sidecar yet — run "
                "`/workbench-validation render --all-runs` to render every recorded run.")
    elif sidecar.is_file():
        source = sidecar
    if source is None:
        return out
    try:
        out["data"] = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        out["data"] = None
        return out
    out["data_source"] = str(source.relative_to(repo_root)) if source.is_relative_to(repo_root) else str(source)
    baseline = out["data"].get("baseline") or {}
    env = out["data"].get("environment") or {}
    out["dirty_at_run"] = bool(baseline.get("git_dirty"))
    out["model_captured"] = bool(baseline.get("model_id"))
    diffs = []
    # Freshness: the recorded config baseline vs the repo HEAD right now.
    try:
        head = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"], cwd=str(repo_root),
            capture_output=True, text=True, timeout=10,
        ).stdout.strip()
        out["head_sha"] = head or None
        recorded = baseline.get("git_sha_short") or ""
        if head and recorded and not head.startswith(recorded) and head != recorded:
            diffs.append(f"commit moved: recorded {recorded}, HEAD {head}")
    except Exception:
        pass
    # Per-skill versions recorded vs installed now (frontmatter block parse).
    recorded_skills = env.get("skills") or {}
    if recorded_skills:
        now = _installed_skill_versions(repo_root)
        for name in sorted(set(recorded_skills) | set(now)):
            then_v = (recorded_skills.get(name) or {}).get("version")
            now_v = now.get(name)
            if name not in now:
                diffs.append(f"skill removed since run: {name}")
            elif name not in recorded_skills:
                diffs.append(f"skill added since run: {name}")
            elif then_v and now_v and then_v != now_v:
                diffs.append(f"{name}: {then_v} → {now_v}")
    recorded_hooks = set(env.get("hooks_installed") or [])
    hooks_dir = repo_root / ".claude" / "hooks"
    if recorded_hooks and hooks_dir.is_dir():
        now_hooks = {p.name for p in hooks_dir.iterdir() if p.suffix in (".sh", ".py")}
        for h in sorted(now_hooks - recorded_hooks):
            diffs.append(f"hook added since run: {h}")
        for h in sorted(recorded_hooks - now_hooks):
            diffs.append(f"hook removed since run: {h}")
    out["differences"] = diffs
    out["stale"] = bool(diffs)
    return out


def _installed_skill_versions(repo_root: Path) -> dict:
    """{skill: frontmatter version} for every installed skill, parsing the
    whole frontmatter block (a fixed head window misses long descriptions)."""
    import re as _re
    versions: dict = {}
    skills_dir = repo_root / ".claude" / "skills"
    if not skills_dir.is_dir():
        return versions
    for d in sorted(skills_dir.iterdir()):
        md = d / "SKILL.md"
        if not d.is_dir() or not md.is_file():
            continue
        try:
            text = md.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        versions[d.name] = None  # installed, version unknown (e.g. external office skills)
        if not text.startswith("---"):
            continue
        end = text.find("\n---", 3)
        block = text[3:end] if end != -1 else text[3:20000]
        m = _re.search(r"^version:\s*(\S+)", block, _re.MULTILINE)
        if m:
            versions[d.name] = m.group(1).strip("'\"")
    return versions


def _load_appearance() -> dict:
    """Installed theme packs + a swatch for each, for the Appearance section.

    Read-only: selection lives in the viewer's browser (a cookie the theme
    middleware reads), never in project config, so nothing here writes.

    The swatch pulls the tokens a viewer actually judges a theme by — page
    ground, panel fill, body text, brand and accent — plus the category ramp
    when the pack ships one. Colours come from the RESOLVED tokens, so a pack
    that inherits most of its palette still previews correctly.
    """
    from console.config import get_config
    from console import themes

    cfg = get_config()
    packs = []
    for p in themes.list_packs(cfg):
        t = p["tokens"]
        packs.append({
            "name": p["name"],
            "label": p["label"],
            "source": p["source"],
            "is_default": p["is_default"],
            "tagline": t.get("tagline", ""),
            "swatch": {
                "body_bg": t.get("body_bg", "#ffffff"),
                "surface": t.get("surface", t.get("body_bg", "#ffffff")),
                "text": t.get("text", "#1f2937"),
                "muted": t.get("text_muted", "#6b7280"),
                "primary": t.get("primary", "#2563eb"),
                "accent": t.get("accent", t.get("primary", "#2563eb")),
                "border": t.get("border", "#e5e7eb"),
            },
            "categories": [c.strip() for c in (t.get("category_colors") or "").split(",") if c.strip()],
        })
    packs.sort(key=lambda p: (p["source"] != "project", p["name"]))
    return {"packs": packs, "default": cfg.theme_name, "cookie": "pc_theme"}


def _load_environment(repo_root: Path) -> dict:
    from console.setup.envcheck import load_environment
    return load_environment(repo_root)


def _load_team_access(repo_root: Path) -> dict | None:
    from console.setup.team_access import load_audit
    return load_audit(repo_root)


def load_project_settings(project: dict) -> dict:
    """Setup → Project data: the `project:` block's fields (scalars editable)
    plus an inventory of every top-level project.yml section, each annotated
    from the skill-shipped description catalog (project_meta.py) so all
    consuming projects render the same explanations."""
    from console.setup.project_meta import PROJECT_FIELDS, SECTIONS, UNKNOWN_FIELD_NOTE

    fields = []
    for key, value in (project.get("project") or {}).items():
        scalar = isinstance(value, (str, int, float, bool))
        if scalar:
            display = str(value)
        elif isinstance(value, list) and all(isinstance(x, (str, int, float, bool)) for x in value):
            display = ", ".join(str(x) for x in value)
        elif isinstance(value, dict):
            display = ", ".join(f"{k}: {v}" for k, v in value.items())
        else:
            display = _clip(str(value), 160)
        fields.append({
            "key": str(key),
            "value": display,
            "editable": scalar,
            "known": key in PROJECT_FIELDS,
            "description": PROJECT_FIELDS.get(key, UNKNOWN_FIELD_NOTE),
        })

    sections = []
    for key, value in project.items():
        if key == "project":
            continue
        meta = SECTIONS.get(key) or {}
        if isinstance(value, list):
            size = f"{len(value)} item{'s' if len(value) != 1 else ''}"
        elif isinstance(value, dict):
            size = f"{len(value)} key{'s' if len(value) != 1 else ''}"
        else:
            size = "scalar"
        preview, truncated = _yaml_preview(value)
        sections.append({
            "key": str(key),
            "size": size,
            "known": key in SECTIONS,
            "description": meta.get("description", UNKNOWN_FIELD_NOTE),
            "managed": meta.get("managed", ""),
            "preview": preview,
            "preview_truncated": truncated,
        })
    return {"fields": fields, "sections": sections}


def _yaml_preview(value, max_lines: int = 40) -> tuple[str, int]:
    """Compact YAML rendering of a config block for the row expansion.
    Returns (text, hidden_line_count) — capped so huge blocks (dhfs,
    strategy_domains) don't blow the page up."""
    try:
        text = yaml.safe_dump(value, sort_keys=False, allow_unicode=True,
                              default_flow_style=False, width=100).rstrip()
    except yaml.YAMLError:
        text = str(value)
    lines = text.splitlines()
    if len(lines) <= max_lines:
        return text, 0
    return "\n".join(lines[:max_lines]), len(lines) - max_lines
