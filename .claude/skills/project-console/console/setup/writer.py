"""Setup section write path — the ONLY place the console mutates connector config.

Two files own connector truth and both are edited here, always in lockstep:

- `.mcp.json`   — JSON round-trip (2-space indent, trailing newline)
- `project.yml` — **surgical line edits only** inside the `approved_mcps:` block.
  A yaml.dump round-trip would destroy the file's comments, so we insert/remove
  single list-item lines and then re-parse the whole file to validate; on any
  validation failure the original bytes are restored.

Every write takes a timestamped backup under `tools/project-console/.data/
setup-backups/` and appends a row to `.data/setup-audit.log` — the console is
editing security-relevant config, so changes must be reconstructable.

Env var VALUES are deliberately not writable here (v1): secrets do not
round-trip through the browser.
"""
from __future__ import annotations

import datetime as _dt
import json
import re
import shutil
from pathlib import Path

import yaml

from console.setup.loader import mcp_json_path, project_yml_path

# Connector names: conservative slug — what .mcp.json keys look like in practice.
NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,63}$")


class SetupWriteError(Exception):
    """User-facing write failure (surfaced as HTTP 400/409/500 detail)."""


def _data_dir(tool_root: Path) -> Path:
    d = tool_root / ".data"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _backup(tool_root: Path, target: Path) -> Path | None:
    if not target.is_file():
        return None
    stamp = _dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    bdir = _data_dir(tool_root) / "setup-backups"
    bdir.mkdir(parents=True, exist_ok=True)
    dest = bdir / f"{target.name}.{stamp}.bak"
    n = 1
    while dest.exists():  # same-second writes must not clobber earlier backups
        n += 1
        dest = bdir / f"{target.name}.{stamp}-{n}.bak"
    dest.write_bytes(target.read_bytes())
    return dest


def _audit(tool_root: Path, action: str, name: str, detail: str = "") -> None:
    line = (
        f"{_dt.datetime.now().isoformat(timespec='seconds')} | {action} | {name}"
        + (f" | {detail}" if detail else "")
        + "\n"
    )
    with (_data_dir(tool_root) / "setup-audit.log").open("a", encoding="utf-8") as fh:
        fh.write(line)


def validate_name(name: str) -> str:
    name = (name or "").strip()
    if not NAME_RE.match(name):
        raise SetupWriteError(
            "Invalid connector name — use letters, digits, dot, dash, underscore "
            "(max 64 chars)."
        )
    return name


def validate_spec(spec: dict) -> dict:
    """Normalize + validate a server spec before it reaches .mcp.json."""
    if not isinstance(spec, dict):
        raise SetupWriteError("Server spec must be an object.")
    transport = str(spec.get("type") or "").strip()
    out: dict = {}
    if spec.get("url"):
        transport = transport or "http"
        if transport not in ("http", "sse"):
            raise SetupWriteError("URL-based servers must have type http or sse.")
        url = str(spec["url"]).strip()
        if not url.startswith(("http://", "https://")):
            raise SetupWriteError("Server url must start with http:// or https://.")
        out = {"type": transport, "url": url}
    else:
        transport = transport or "stdio"
        if transport != "stdio":
            raise SetupWriteError(f"type {transport!r} requires a url.")
        command = str(spec.get("command") or "").strip()
        if not command:
            raise SetupWriteError("stdio servers require a command.")
        args = spec.get("args") or []
        if not isinstance(args, list):
            raise SetupWriteError("args must be a list of strings.")
        out = {
            "type": "stdio",
            "command": command,
            "args": [str(a) for a in args],
            "env": {},
        }
    # Env values never arrive from the browser; preserve is handled by caller.
    return out


# ── .mcp.json ────────────────────────────────────────────────────────────────

def _read_mcp(repo_root: Path) -> dict:
    p = mcp_json_path(repo_root)
    if not p.is_file():
        return {"mcpServers": {}}
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        raise SetupWriteError(f".mcp.json could not be parsed ({e}) — fix it manually first.")
    if not isinstance(data, dict):
        raise SetupWriteError(".mcp.json root is not an object — fix it manually first.")
    data.setdefault("mcpServers", {})
    return data


def _write_mcp(repo_root: Path, data: dict) -> None:
    mcp_json_path(repo_root).write_text(
        json.dumps(data, indent=2) + "\n", encoding="utf-8"
    )


def upsert_server(repo_root: Path, tool_root: Path, name: str, spec: dict) -> None:
    """Add or update `mcpServers[name]`, preserving any existing env block
    (env is not editable from the console — an update must not clobber it)."""
    name = validate_name(name)
    spec = validate_spec(spec)
    data = _read_mcp(repo_root)
    existing = data["mcpServers"].get(name)
    # Carry secrets-adjacent blocks across updates for BOTH transports: the
    # browser never sends env/headers, so an update must not drop them
    # (URL specs carry no env key at all — the old `"env" in spec` guard
    # silently lost a remote server's env/headers on every update).
    if isinstance(existing, dict):
        for key in ("env", "headers"):
            if isinstance(existing.get(key), dict) and not spec.get(key):
                spec[key] = existing[key]
    _backup(tool_root, mcp_json_path(repo_root))
    data["mcpServers"][name] = spec
    _write_mcp(repo_root, data)
    _audit(tool_root, "upsert", name, f"type={spec.get('type')}")


def remove_server(repo_root: Path, tool_root: Path, name: str) -> None:
    name = validate_name(name)
    data = _read_mcp(repo_root)
    if name not in data["mcpServers"]:
        raise SetupWriteError(f"Connector {name!r} is not defined in .mcp.json.")
    _backup(tool_root, mcp_json_path(repo_root))
    del data["mcpServers"][name]
    _write_mcp(repo_root, data)
    _audit(tool_root, "remove", name)


# ── project.yml security.approved_* (surgical, comment-preserving) ───────────

def _approved_block(lines: list[str], key: str = "approved_mcps") -> tuple[int, str]:
    """Locate the `<key>:` list-key line. Returns (index, key_indent)."""
    for i, line in enumerate(lines):
        m = re.match(rf"^(\s*){re.escape(key)}:\s*(\[\s*\])?\s*$", line)
        if m:
            return i, m.group(1)
    raise SetupWriteError(
        f"project.yml has no {key}: key under security: — add it manually first."
    )


def _validate_yaml(path: Path, original: str, expect_name: str, present: bool,
                   key: str = "approved_mcps") -> None:
    """Re-parse the edited file; on failure restore original bytes and raise."""
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        approved = [str(x) for x in ((data.get("security") or {}).get(key) or [])]
        ok = (expect_name in approved) if present else (expect_name not in approved)
        if not ok:
            raise ValueError("post-edit allowlist state mismatch")
    except Exception as e:
        path.write_text(original, encoding="utf-8")
        raise SetupWriteError(f"project.yml edit failed validation ({e}); file restored.")


def set_approved(repo_root: Path, tool_root: Path, name: str, approved: bool,
                 key: str = "approved_mcps") -> bool:
    """Insert/remove `- <name>` inside a security.<key> allowlist block.
    Returns True if the file changed (idempotent no-op returns False)."""
    name = validate_name(name)
    p = project_yml_path(repo_root)
    if not p.is_file():
        raise SetupWriteError("project.yml not found.")
    original = p.read_text(encoding="utf-8")
    lines = original.splitlines(keepends=True)
    key_idx, key_indent = _approved_block(lines, key)

    # Collect the existing item lines directly under the key. Items may sit at
    # the key's indent or deeper (both are valid YAML); match the first item's
    # indent, defaulting to the key's own.
    item_re = re.compile(r"^(\s*)-\s+(\S.*?)\s*$")
    item_indent = key_indent
    block: list[tuple[int, str]] = []  # (line index, item value)
    j = key_idx + 1
    while j < len(lines):
        m = item_re.match(lines[j])
        if m and len(m.group(1)) >= len(key_indent):
            if not block:
                item_indent = m.group(1)
            block.append((j, m.group(2)))
            j += 1
            continue
        if lines[j].strip() == "" or lines[j].lstrip().startswith("#"):
            # Blank/comment lines end the block only if no item follows —
            # simplest safe rule: stop at the first non-item line.
            break
        break

    names = [v for _, v in block]
    if approved and name in names:
        return False
    if not approved and name not in names:
        return False

    _backup(tool_root, p)
    if approved:
        # `<key>: []` inline-empty form → expand to a block list.
        if re.match(rf"^\s*{re.escape(key)}:\s*\[\s*\]\s*$", lines[key_idx]):
            lines[key_idx] = f"{key_indent}{key}:\n"
        insert_at = block[-1][0] + 1 if block else key_idx + 1
        lines.insert(insert_at, f"{item_indent}- {name}\n")
    else:
        for idx, value in block:
            if value == name:
                del lines[idx]
                break
    p.write_text("".join(lines), encoding="utf-8")
    _validate_yaml(p, original, name, present=approved, key=key)
    _audit(tool_root, "approve" if approved else "unapprove", name, f"list={key}")
    return True


# ── project.yml team roster (surgical, comment-preserving) ───────────────────
#
# Same doctrine as the allowlist edits: never yaml.dump the file. Members are
# multi-line list items, so the unit of edit is an item BLOCK (the `- name:`
# line plus its deeper-indented field lines). Add appends to team.active;
# deactivate moves the block to team.inactive with `removed:` + `reason:` —
# the roster convention the project manifest documents. The console edits
# project.yml only: actual repo access lives in GitHub and is audited against
# this roster by the project's posture check, not granted/revoked here.

_GITHUB_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})$")
_FOLDER_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,63}$")
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _validate_scalar(label: str, value: str, max_len: int) -> str:
    """A value we will emit as a plain YAML scalar on one line."""
    value = " ".join((value or "").split())
    if not value:
        raise SetupWriteError(f"{label} is required.")
    if len(value) > max_len:
        raise SetupWriteError(f"{label} is too long (max {max_len} chars).")
    if ":" in value or "#" in value or value[0] in "-&*?|>!%@`\"'{[":
        raise SetupWriteError(
            f"{label} must not contain ':' or '#' or start with YAML punctuation."
        )
    return value


def _find_team_list(lines: list[str], list_key: str):
    """Locate `team.<list_key>` in project.yml lines.

    Returns (key_idx, key_indent, inline_empty, item_indent, items) where
    items is a list of (start, end) line ranges — one per `- ` member block
    (end exclusive). item_indent is None when the list has no items yet.
    """
    team_idx = next(
        (i for i, l in enumerate(lines) if re.match(r"^team:\s*$", l)), None
    )
    if team_idx is None:
        raise SetupWriteError("project.yml has no top-level team: block — add it manually first.")
    key_idx = key_indent = None
    inline_empty = False
    for j in range(team_idx + 1, len(lines)):
        if re.match(r"^\S", lines[j]):  # next top-level key ends the team block
            break
        m = re.match(rf"^(\s+){re.escape(list_key)}:\s*(\[\s*\])?\s*$", lines[j])
        if m:
            key_idx, key_indent, inline_empty = j, m.group(1), bool(m.group(2))
            break
    if key_idx is None:
        raise SetupWriteError(
            f"project.yml team: block has no {list_key}: key — add it manually first."
        )
    items: list[tuple[int, int]] = []
    item_indent = None
    i = key_idx + 1
    while not inline_empty and i < len(lines):
        m = re.match(r"^(\s*)-\s", lines[i])
        if m and len(m.group(1)) >= len(key_indent) and (
            item_indent is None or m.group(1) == item_indent
        ):
            item_indent = m.group(1)
            start = i
            i += 1
            while i < len(lines):
                nxt = lines[i]
                indent = len(nxt) - len(nxt.lstrip())
                if nxt.strip() and indent > len(item_indent) and not re.match(
                    rf"^{re.escape(item_indent)}-\s", nxt
                ):
                    i += 1
                    continue
                break
            items.append((start, i))
            continue
        break
    return key_idx, key_indent, inline_empty, item_indent, items


def _item_field(lines: list[str], start: int, end: int, field: str) -> str:
    for line in lines[start:end]:
        m = re.match(rf"^\s*(?:-\s+)?{re.escape(field)}:\s*(.*?)\s*$", line)
        if m:
            v = m.group(1)
            if len(v) >= 2 and v[0] == v[-1] and v[0] in "'\"":
                v = v[1:-1]
            return v
    return ""


def _member_block(fields: list[tuple[str, str]], item_indent: str) -> list[str]:
    field_indent = item_indent + "  "
    first_key, first_val = fields[0]
    out = [f"{item_indent}- {first_key}: {first_val}\n"]
    out += [f"{field_indent}{k}: {v}\n" for k, v in fields[1:]]
    return out


def _validate_team_yaml(path: Path, original: str, github: str, active: bool) -> None:
    """Re-parse the edited file; on failure restore original bytes and raise."""
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        team = data.get("team") or {}
        in_active = any(
            isinstance(m, dict) and m.get("github") == github
            for m in team.get("active") or []
        )
        in_inactive = any(
            isinstance(m, dict) and m.get("github") == github
            for m in team.get("inactive") or []
        )
        ok = (in_active and not in_inactive) if active else (in_inactive and not in_active)
        if not ok:
            raise ValueError("post-edit roster state mismatch")
    except Exception as e:
        path.write_text(original, encoding="utf-8")
        raise SetupWriteError(f"project.yml edit failed validation ({e}); file restored.")


def add_team_member(repo_root: Path, tool_root: Path, member: dict) -> str:
    """Append a member to team.active (name, github, task_folder, role, email
    + today's `added:` date). Email domain is checked against
    security.approved_email_domains when that list is declared."""
    name = _validate_scalar("Name", str(member.get("name") or ""), 80)
    role = _validate_scalar("Role", str(member.get("role") or ""), 120)
    github = str(member.get("github") or "").strip()
    if not _GITHUB_RE.match(github):
        raise SetupWriteError("GitHub username is invalid (letters, digits, dashes; max 39 chars).")
    folder = str(member.get("task_folder") or "").strip().lower()
    if not _FOLDER_RE.match(folder):
        raise SetupWriteError("Task folder must be a lowercase slug (letters, digits, - or _).")
    email = str(member.get("email") or "").strip().lower()
    if not _EMAIL_RE.match(email):
        raise SetupWriteError("Email address is invalid.")

    p = project_yml_path(repo_root)
    if not p.is_file():
        raise SetupWriteError("project.yml not found.")
    original = p.read_text(encoding="utf-8")
    project = yaml.safe_load(original) or {}
    domains = [
        str(d).lstrip("@").lower()
        for d in (project.get("security") or {}).get("approved_email_domains") or []
    ]
    domain = email.rsplit("@", 1)[-1]
    if domains and domain not in domains:
        raise SetupWriteError(
            f"Email domain @{domain} is not in security.approved_email_domains "
            f"({', '.join('@' + d for d in domains)})."
        )
    team = project.get("team") or {}
    for m in team.get("active") or []:
        if not isinstance(m, dict):
            continue
        if str(m.get("github") or "") == github:
            raise SetupWriteError(f"{github!r} is already on the active roster.")
        if str(m.get("task_folder") or "") == folder:
            raise SetupWriteError(
                f"Task folder {folder!r} is already used by {m.get('name')!r}."
            )
    if any(
        isinstance(m, dict) and str(m.get("github") or "") == github
        for m in team.get("inactive") or []
    ):
        raise SetupWriteError(
            f"{github!r} is in team.inactive — re-activating a former member is a "
            "manual project.yml edit (move the row back and clear removed/reason), "
            "so their history stays on one entry."
        )

    lines = original.splitlines(keepends=True)
    key_idx, key_indent, inline_empty, item_indent, items = _find_team_list(lines, "active")
    item_indent = item_indent if item_indent is not None else key_indent
    block = _member_block(
        [("name", name), ("github", github), ("task_folder", folder),
         ("role", role), ("email", email),
         ("added", _dt.date.today().isoformat())],
        item_indent,
    )
    _backup(tool_root, p)
    if inline_empty:
        lines[key_idx] = f"{key_indent}active:\n"
    insert_at = items[-1][1] if items else key_idx + 1
    lines[insert_at:insert_at] = block
    p.write_text("".join(lines), encoding="utf-8")
    _validate_team_yaml(p, original, github, active=True)
    _audit(tool_root, "team-add", github, f"folder={folder}")
    return (
        f"Added {name} to team.active. project.yml is the roster of record — "
        "grant actual repo access in GitHub, then run the project's posture "
        "check to confirm the two match. Create their tasks/" + folder + "/ folder on first task."
    )


def deactivate_team_member(repo_root: Path, tool_root: Path, github: str,
                           reason: str) -> str:
    """Move a member's block from team.active to team.inactive, appending
    `removed:` (today) + `reason:` per the roster convention."""
    github = (github or "").strip()
    if not _GITHUB_RE.match(github):
        raise SetupWriteError("GitHub username is invalid.")
    reason = _validate_scalar("Reason", reason, 200)

    p = project_yml_path(repo_root)
    if not p.is_file():
        raise SetupWriteError("project.yml not found.")
    original = p.read_text(encoding="utf-8")
    lines = original.splitlines(keepends=True)

    a_key, a_indent, a_empty, _a_item, a_items = _find_team_list(lines, "active")
    match = next(
        ((s, e) for s, e in a_items if _item_field(lines, s, e, "github") == github),
        None,
    )
    if a_empty or match is None:
        raise SetupWriteError(f"{github!r} is not on the active roster.")
    start, end = match
    fields = [
        (k, _item_field(lines, start, end, k))
        for k in ("name", "github", "task_folder", "role", "email", "added")
    ]
    fields = [(k, v) for k, v in fields if v]
    fields += [("removed", _dt.date.today().isoformat()), ("reason", reason)]

    _backup(tool_root, p)
    del lines[start:end]
    if len(a_items) == 1:  # roster now empty → keep the key parseable
        lines[a_key] = f"{a_indent}active: []\n"

    i_key, i_indent, i_empty, i_item, i_items = _find_team_list(lines, "inactive")
    i_item = i_item if i_item is not None else i_indent
    block = _member_block(fields, i_item)
    if i_empty:
        lines[i_key] = f"{i_indent}inactive:\n"
    insert_at = i_items[-1][1] if i_items else i_key + 1
    lines[insert_at:insert_at] = block
    p.write_text("".join(lines), encoding="utf-8")
    _validate_team_yaml(p, original, github, active=False)
    _audit(tool_root, "team-deactivate", github, f"reason={reason}")
    name = dict(fields).get("name") or github
    return (
        f"Moved {name} to team.inactive. This edits the roster of record only — "
        "revoke their GitHub repo access separately, then run the project's "
        "posture check to confirm."
    )


# ── registry skill install / update (copy from the registry's local clone) ───

def _backup_dir(tool_root: Path, target: Path) -> Path:
    stamp = _dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    bdir = _data_dir(tool_root) / "setup-backups" / f"{target.name}.{stamp}"
    shutil.copytree(target, bdir, symlinks=True)
    return bdir


def install_skill(repo_root: Path, tool_root: Path, registry: dict,
                  name: str) -> str:
    """Install or update a skill from a registry — the local clone when one
    exists (fast path), otherwise a tarball downloaded straight from GitHub
    via `gh` (read access is enough; customer projects often have no clone
    and no write access to the registry).

    Scope is deliberately narrow — this is the console's convenience path,
    not a replacement for the registry sync tooling:

    - **New skill**: plain copy (there is no local state to clobber — the
      same thing the sync tooling does for registry-only files) + allowlist.
    - **Update**: allowed only when the registry version is strictly newer
      than the installed one (server-side downgrade guard); the entire local
      skill directory is backed up under `.data/setup-backups/` first, then
      replaced wholesale. Locally-diverged skills at equal-or-newer versions
      never get an update path here — that reconciliation belongs to the
      sync tooling.

    Returns a human-readable note for the UI.
    """
    import tempfile

    from console.setup.loader import _skill_version, _version_key  # local import: avoid cycle at module load

    name = validate_name(name)
    src = None
    source_note = ""
    registry_local = str(registry.get("local_path") or "")
    if registry_local:
        cand = (repo_root / registry_local).resolve() / "skills" / name
        if (cand / "SKILL.md").is_file():
            src = cand
            source_note = f"from={registry_local}"
    tmp = None
    if src is None:
        repo = str(registry.get("repo") or "")
        if not repo:
            raise SetupWriteError(
                f"Skill {name!r}: registry has neither a usable local clone nor a "
                "`repo` to download from."
            )
        from console.setup.registry_remote import RegistryRemoteError, download_skill_dir
        tmp = tempfile.TemporaryDirectory()
        try:
            src = download_skill_dir(
                repo, str(registry.get("branch") or "main"), name, Path(tmp.name)
            )
        except RegistryRemoteError as e:
            tmp.cleanup()
            raise SetupWriteError(str(e))
        source_note = f"from=github:{repo}"
    dst = repo_root / ".claude" / "skills" / name
    updating = dst.is_dir()
    try:
        if updating:
            reg_v, loc_v = _skill_version(src), _skill_version(dst)
            if _version_key(reg_v) <= _version_key(loc_v):
                raise SetupWriteError(
                    f"Registry has {name} v{reg_v or '?'} but v{loc_v or '?'} is installed — "
                    "not an upgrade. Use the registry sync tooling to reconcile."
                )
            backup = _backup_dir(tool_root, dst)
            shutil.rmtree(dst)
        else:
            backup = None
        shutil.copytree(src, dst, symlinks=True)
    finally:
        if tmp is not None:
            tmp.cleanup()
    changed = set_approved(repo_root, tool_root, name, approved=True, key="approved_skills")
    _audit(
        tool_root,
        "skill-update" if updating else "skill-install",
        name,
        source_note + (f" backup={backup.name}" if backup else "")
        + (" allowlisted" if changed else ""),
    )
    action = "Updated" if updating else "Installed"
    source_human = "the registry's local clone" if "github:" not in source_note else "GitHub"
    return (
        f"{action} {name} from {source_human}"
        + (" (previous copy backed up under .data/setup-backups/)" if backup else "")
        + ". Restart the Claude Code session to pick it up; if the skill has a "
        "setup action, run /"
        + name + " setup. Run the registry sync tooling's status check to confirm lockstep."
    )
