"""Supported-connector catalog for the Setup section.

Company-agnostic registry of MCP connectors the console knows how to
configure. Each entry carries a ready-to-write `.mcp.json` server spec
template plus the metadata the Setup UI needs to render an "Add connector"
card. Project-specific values (paths, ports, tokens) are entered by the
user at configure time — nothing project-specific lives here.

Two pseudo-entries (`custom-stdio`, `custom-http`) let users add any server
the catalog doesn't know about; they render as free-form forms rather than
prefilled templates.
"""
from __future__ import annotations

# Each entry:
#   key            — connector name as it will appear in .mcp.json mcpServers
#   title          — display name
#   description    — one-liner for the card
#   docs           — reference URL (rendered as a link, never fetched)
#   spec           — .mcp.json server template; None for the custom forms
#   env_required   — env keys the server needs at runtime (shown as a checklist;
#                    values are configured outside the console — never here)
#   editable       — which spec fields the configure form exposes
CATALOG: list[dict] = [
    {
        "key": "chrome-devtools",
        "title": "Chrome DevTools",
        "description": (
            "Browser automation and inspection (navigate, screenshot, console, "
            "network) via the chrome-devtools MCP server."
        ),
        "docs": "https://github.com/ChromeDevTools/chrome-devtools-mcp",
        "spec": {
            "type": "stdio",
            "command": "npx",
            "args": ["-y", "chrome-devtools-mcp@latest"],
            "env": {},
        },
        "env_required": [],
        "editable": ["args"],
    },
    {
        "key": "file-locator",
        "title": "File Locator (semantic search)",
        "description": (
            "Local semantic file search over the project's docs corpus "
            "(fastembed + SQLite FTS5). Ships with the file-locator skill; "
            "requires the skill to be installed and its index built."
        ),
        "docs": "",
        "spec": {
            "type": "stdio",
            "command": "./tools/file-locator-mcp/bootstrap.sh",
            "args": ["./.claude/skills/file-locator/scripts/server.py"],
            "env": {},
        },
        "env_required": [],
        "editable": [],
    },
    {
        "key": "custom-stdio",
        "title": "Custom stdio server",
        "description": (
            "Any MCP server launched as a local process (command + args). "
            "Use for servers not in the catalog."
        ),
        "docs": "https://modelcontextprotocol.io/",
        "spec": None,
        "env_required": [],
        "editable": ["name", "command", "args"],
    },
    {
        "key": "custom-http",
        "title": "Custom HTTP / SSE server",
        "description": (
            "Any remote MCP server reachable over HTTP (streamable HTTP or SSE). "
            "Authentication is handled by the MCP client, not the console."
        ),
        "docs": "https://modelcontextprotocol.io/",
        "spec": None,
        "env_required": [],
        "editable": ["name", "url", "transport"],
    },
]


def get(key: str) -> dict | None:
    for entry in CATALOG:
        if entry["key"] == key:
            return entry
    return None
