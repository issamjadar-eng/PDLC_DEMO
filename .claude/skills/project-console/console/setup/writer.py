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
    if isinstance(existing, dict) and isinstance(existing.get("env"), dict) and "env" in spec:
        spec["env"] = existing["env"]
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


# ── project.yml security.approved_mcps (surgical, comment-preserving) ────────

def _approved_block(lines: list[str]) -> tuple[int, str]:
    """Locate the `approved_mcps:` key line. Returns (index, key_indent)."""
    for i, line in enumerate(lines):
        m = re.match(r"^(\s*)approved_mcps:\s*(\[\s*\])?\s*$", line)
        if m:
            return i, m.group(1)
    raise SetupWriteError(
        "project.yml has no approved_mcps: key under security: — add it manually first."
    )


def _validate_yaml(path: Path, original: str, expect_name: str, present: bool) -> None:
    """Re-parse the edited file; on failure restore original bytes and raise."""
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        approved = [str(x) for x in ((data.get("security") or {}).get("approved_mcps") or [])]
        ok = (expect_name in approved) if present else (expect_name not in approved)
        if not ok:
            raise ValueError("post-edit allowlist state mismatch")
    except Exception as e:
        path.write_text(original, encoding="utf-8")
        raise SetupWriteError(f"project.yml edit failed validation ({e}); file restored.")


def set_approved(repo_root: Path, tool_root: Path, name: str, approved: bool) -> bool:
    """Insert/remove `- <name>` inside the approved_mcps block. Returns True if
    the file changed (idempotent no-op returns False)."""
    name = validate_name(name)
    p = project_yml_path(repo_root)
    if not p.is_file():
        raise SetupWriteError("project.yml not found.")
    original = p.read_text(encoding="utf-8")
    lines = original.splitlines(keepends=True)
    key_idx, key_indent = _approved_block(lines)

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
        # `approved_mcps: []` inline-empty form → expand to a block list.
        if re.match(r"^\s*approved_mcps:\s*\[\s*\]\s*$", lines[key_idx]):
            lines[key_idx] = f"{key_indent}approved_mcps:\n"
        insert_at = block[-1][0] + 1 if block else key_idx + 1
        lines.insert(insert_at, f"{item_indent}- {name}\n")
    else:
        for idx, value in block:
            if value == name:
                del lines[idx]
                break
    p.write_text("".join(lines), encoding="utf-8")
    _validate_yaml(p, original, name, present=approved)
    _audit(tool_root, "approve" if approved else "unapprove", name)
    return True
