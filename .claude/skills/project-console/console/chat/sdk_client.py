import json
import os
import tempfile
from pathlib import Path
from typing import AsyncIterator

from claude_agent_sdk import (
    AgentDefinition,
    AssistantMessage,
    ClaudeAgentOptions,
    StreamEvent,
    TextBlock,
    create_sdk_mcp_server,
    query,
    tool,
)
from claude_agent_sdk.types import SystemPromptFile

from console.chat.domain_agents import _parse_frontmatter
from console.chat.index_builder import is_groundable
from console.config import get_config


def _resolve_model(model: str | None) -> str:
    """Thin wrapper around `Config.resolve_model`; kept for call-site stability."""
    return get_config().resolve_model(model)


# ---------------- custom MCP tool: read_files ----------------
#
# The assistant drawer's Tier 3 grounding is the README tree; Tier 2 is the
# agent's `core:` list. For anything else, the agent calls `read_files` to
# fetch specific `.md` content on demand. The tool validates every path
# against `config.grounding_roots` (docs/project, docs/external,
# docs/internal/source-md by default, extended via `grounding.extra_roots`
# in console.yaml to expose skill-embedded references). Paths must not
# contain excluded segments below the root (source/source-md/formal/
# images/.staging) — this is what keeps the raw `source-md/` pre-conversion
# tree inside the skill references hidden while `docs/internal/source-md/`
# (an explicit root) remains visible.
# Folder paths expand to direct-child .md files (README first if present).
# Max 200 KB per file inlined to prevent a single huge doc from blowing up
# the turn; agent should request specific paths, not dump trees.

_MAX_SINGLE_FILE_BYTES = 200_000


def _expand_one_path(repo_root: Path, rel: str) -> tuple[list[Path], str | None]:
    """Resolve one user-supplied path. Returns (paths, error)."""
    if not rel or rel.startswith("/") or ".." in Path(rel).parts:
        return [], f"rejected: absolute or parent-relative path: {rel!r}"
    allowed_roots = get_config().grounding_roots
    if not any(rel == root or rel.startswith(root + "/") for root in allowed_roots):
        return [], (
            f"rejected: path must start with one of "
            f"{allowed_roots}; got {rel!r}"
        )
    p = (repo_root / rel).resolve()
    try:
        p.relative_to(repo_root.resolve())
    except ValueError:
        return [], f"rejected: path escapes repo root: {rel!r}"
    if not p.exists():
        return [], f"not found: {rel!r}"
    if not is_groundable(p, repo_root):
        return [], (
            f"rejected: path is in an excluded folder "
            f"(source/source-md/formal/images/.staging below grounding root): {rel!r}"
        )
    if p.is_file():
        if p.suffix != ".md":
            return [], f"rejected: only .md files may be read: {rel!r}"
        return [p], None
    if p.is_dir():
        out: list[Path] = []
        readme = p / "README.md"
        if readme.exists():
            out.append(readme)
        for child in sorted(p.iterdir()):
            if (
                child.is_file()
                and child.suffix == ".md"
                and child.name != "README.md"
                and is_groundable(child, repo_root)
            ):
                out.append(child)
        return out, None
    return [], f"rejected: not a file or directory: {rel!r}"


@tool(
    "read_files",
    "Read one or more markdown files from the project docs tree. "
    "Each path can be a specific .md file (docs/project/.../doc.md) or a "
    "folder (docs/project/.../architecture/) which expands to its direct-child "
    ".md files plus the folder's own README.md. Use this after scanning the "
    "README index in the system prompt to fetch specific content that would "
    "help answer the question. Prefer over-fetching when in doubt.",
    {"paths": list[str]},
)
async def _read_files_tool(args: dict) -> dict:
    paths = args.get("paths") or []
    cfg = get_config()
    repo_root = cfg.repo_root
    parts: list[str] = []
    errors: list[str] = []
    seen: set[Path] = set()
    for rel in paths:
        expanded, err = _expand_one_path(repo_root, rel)
        if err:
            errors.append(err)
            continue
        for p in expanded:
            if p in seen:
                continue
            seen.add(p)
            try:
                text = p.read_text(encoding="utf-8", errors="replace")
            except OSError as e:
                errors.append(f"read failed for {p.relative_to(repo_root)}: {e}")
                continue
            if len(text) > _MAX_SINGLE_FILE_BYTES:
                text = text[:_MAX_SINGLE_FILE_BYTES] + (
                    f"\n\n[... truncated — file was "
                    f"{len(text)} bytes, cap {_MAX_SINGLE_FILE_BYTES} ...]"
                )
            parts.append(
                f"===== FILE: {p.relative_to(repo_root).as_posix()} =====\n\n{text}"
            )
    if errors:
        parts.append("===== ERRORS =====\n" + "\n".join(errors))
    content = "\n\n".join(parts) if parts else "(no files matched)"
    return {"content": [{"type": "text", "text": content}]}


_GROUNDING_MCP_SERVER = create_sdk_mcp_server(
    name="console-grounding",
    version="1.0.0",
    tools=[_read_files_tool],
)


# ---------------- external MCP servers + subagents ----------------
#
# Two extra capability seams, both governed by the agent definition / project
# config rather than hardcoded here so the skill stays project-agnostic:
#   * external MCP servers (e.g. the semantic file-locator) — exposed to every
#     chat agent, resolved by name from the project's `.mcp.json`.
#   * project subagents (e.g. red-team-researcher) — opt-in per agent via the
#     agent definition's `subagents:` list, loaded from `.claude/agents/`.


def _external_mcp_servers(repo_root: Path, names: list[str]) -> dict:
    """Build SDK `mcp_servers` entries for the named stdio servers declared in
    the project's `.mcp.json`. Repo-root-relative commands/args are made
    absolute so the server launches regardless of the console's cwd. Servers
    not present (or not stdio) are silently skipped — the feature degrades to
    "not available" rather than erroring.
    """
    out: dict = {}
    mcp_path = repo_root / ".mcp.json"
    if not mcp_path.exists():
        return out
    try:
        data = json.loads(mcp_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return out
    servers = data.get("mcpServers") or {}

    def _abs(token: str) -> str:
        if isinstance(token, str) and (token.startswith("./") or token.startswith("../")):
            return str((repo_root / token).resolve())
        return token

    for name in names:
        cfg = servers.get(name)
        if not isinstance(cfg, dict) or cfg.get("type", "stdio") != "stdio":
            continue
        command = cfg.get("command")
        if not command:
            continue
        out[name] = {
            "type": "stdio",
            "command": _abs(command),
            "args": [_abs(a) for a in (cfg.get("args") or [])],
            "env": dict(cfg.get("env") or {}),
        }
    return out


def _load_subagent(repo_root: Path, name: str) -> tuple[str, AgentDefinition] | None:
    """Load a project subagent (`.claude/agents/<name>.md`) into an SDK
    AgentDefinition so a console agent can invoke it via the Task tool.
    Returns None if the file is absent or unparseable.
    """
    path = repo_root / ".claude" / "agents" / f"{name}.md"
    if not path.exists():
        return None
    try:
        meta, body = _parse_frontmatter(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    tools_raw = meta.get("tools")
    if isinstance(tools_raw, str):
        tools = [t.strip() for t in tools_raw.split(",") if t.strip()]
    elif isinstance(tools_raw, list):
        tools = [str(t).strip() for t in tools_raw if str(t).strip()]
    else:
        tools = None
    return name, AgentDefinition(
        description=meta.get("description", name),
        prompt=body.strip(),
        tools=tools,
        model=meta.get("model"),
    )


async def stream_response(
    *,
    system_prompt: str,
    user_message: str,
    model: str | None = None,
    enable_read_files: bool = True,
    enable_file_locator: bool = True,
    subagents: list[str] | None = None,
    max_turns: int = 15,
) -> AsyncIterator[str]:
    """Yield text deltas as they arrive from the Agent SDK.

    Writes system_prompt to a temp file and passes SystemPromptFile to the
    SDK so the CLI receives --system-prompt-file instead of an inline arg.
    This avoids [Errno 7] Argument list too long on large prompts (>~100KB).

    When `enable_read_files` is True, registers the in-process `read_files`
    MCP tool so the agent can fetch specific .md content on demand from
    the docs tree. Tool calls count toward `max_turns`.

    Uses ``include_partial_messages=True`` so the SDK emits ``StreamEvent``
    objects wrapping raw Anthropic API stream events. We extract text from
    ``content_block_delta`` events (for streaming text chunks). The final
    ``AssistantMessage`` is ignored to avoid duplicating text that already
    arrived via deltas.
    """
    tmp_path: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False, encoding="utf-8"
        ) as tmp:
            tmp.write(system_prompt)
            tmp_path = tmp.name

        cfg = get_config()
        repo_root = cfg.repo_root
        mcp_servers: dict = {}
        allowed_tools: list[str] = []
        if enable_read_files:
            mcp_servers["console-grounding"] = _GROUNDING_MCP_SERVER
            allowed_tools.append("mcp__console-grounding__read_files")
        if enable_file_locator:
            for sname, scfg in _external_mcp_servers(repo_root, cfg.chat_mcp_servers).items():
                mcp_servers[sname] = scfg
                allowed_tools.append(f"mcp__{sname}")  # allow all tools from this server

        agents_opt: dict[str, AgentDefinition] = {}
        for sa in (subagents or []):
            loaded = _load_subagent(repo_root, sa)
            if loaded:
                agents_opt[loaded[0]] = loaded[1]
        if agents_opt:
            allowed_tools.append("Task")  # lets the agent invoke its declared subagent(s)

        options = ClaudeAgentOptions(
            system_prompt=SystemPromptFile(type="file", path=tmp_path),
            model=_resolve_model(model),
            include_partial_messages=True,
            mcp_servers=mcp_servers,
            allowed_tools=allowed_tools,
            agents=agents_opt or None,
            cwd=str(repo_root),
            max_turns=max_turns,
        )
        got_any_delta = False
        async for msg in query(prompt=user_message, options=options):
            if isinstance(msg, StreamEvent):
                evt = msg.event or {}
                etype = evt.get("type")
                if etype == "content_block_delta":
                    delta = evt.get("delta") or {}
                    if delta.get("type") == "text_delta":
                        text = delta.get("text") or ""
                        if text:
                            got_any_delta = True
                            yield text
            elif isinstance(msg, AssistantMessage) and not got_any_delta:
                # Fallback: no deltas arrived (older CLI, or partial messages
                # disabled upstream) — yield the full block text as one chunk.
                for block in msg.content:
                    if isinstance(block, TextBlock) and block.text:
                        yield block.text
    finally:
        if tmp_path:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass


async def collect_response(
    *,
    system_prompt: str,
    user_message: str,
    model: str | None = None,
    enable_read_files: bool = True,
    enable_file_locator: bool = True,
    subagents: list[str] | None = None,
    max_turns: int = 15,
) -> str:
    parts: list[str] = []
    async for token in stream_response(
        system_prompt=system_prompt,
        user_message=user_message,
        model=model,
        enable_read_files=enable_read_files,
        enable_file_locator=enable_file_locator,
        subagents=subagents,
        max_turns=max_turns,
    ):
        parts.append(token)
    return "".join(parts)
