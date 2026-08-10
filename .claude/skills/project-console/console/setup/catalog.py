"""Supported-connector catalog for the Setup section.

Company-agnostic registry of MCP connectors the console knows how to
configure. Each entry carries a ready-to-write `.mcp.json` server spec
template plus the metadata the Setup UI needs to render an "Add connector"
card. Project-specific values (paths, ports, tokens) are entered by the
user at configure time — nothing project-specific lives here.

Two pseudo-entries (`custom-stdio`, `custom-http`) let users add any server
the catalog doesn't know about; they render as free-form forms rather than
prefilled templates.

Curation policy — **vendor-official servers only**. Clicking Configure writes
`.mcp.json` *and* adds the connector to `project.yml security.approved_mcps`,
so a catalog row is effectively a pre-blessed allowlist entry. Third-party or
individual-authored servers are deliberately not catalogued even when they
exist; a team that has vetted one adds it through the custom stdio/HTTP forms,
which keeps that an explicit act rather than a curated recommendation. A tool
with no vendor server is listed with `availability: "none"` rather than
omitted — an absent card is ambiguous, a "no vendor MCP" card is an answer.

Endpoints are never guessed. Where a vendor's MCP is real but its endpoint is
customer-gated (Jama Connect), the entry ships an empty `url` plus a
`url_placeholder` hint and a `note` saying where to obtain the real one.
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
#
# Optional keys:
#   note           — caution/context line rendered under the description; use
#                    for instance-specific endpoints, licensing prerequisites,
#                    or scope caveats the one-liner would overstate
#   url_placeholder— input placeholder when the entry ships no concrete URL
#   availability   — "vendor" (default) or "none". "none" renders an
#                    informational card with no Configure button: the tool was
#                    researched and has no vendor MCP server.
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
        "key": "atlassian",
        "title": "Jira + Confluence (Atlassian)",
        "description": (
            "Atlassian's official remote MCP server — Jira issues, Confluence "
            "pages, and Compass, over OAuth. One connector serves both Jira "
            "and Confluence. Sign-in happens in the MCP client on first "
            "connect (/mcp in a session); no tokens in config."
        ),
        "docs": (
            "https://support.atlassian.com/atlassian-rovo-mcp-server/docs/"
            "getting-started-with-the-atlassian-remote-mcp-server/"
        ),
        # /v1/mcp/authv2 is the OAuth endpoint; the older /v1/sse endpoint is
        # deprecated (unsupported after 2026-06-30) — do not use it here.
        "spec": {
            "type": "http",
            "url": "https://mcp.atlassian.com/v1/mcp/authv2",
        },
        "env_required": [],
        "editable": ["url"],
    },
    {
        "key": "gitlab",
        "title": "GitLab",
        "description": (
            "GitLab's official MCP server — merge requests, issues, pipelines, "
            "and repository search. Served by the GitLab instance itself at "
            "/api/v4/mcp; OAuth dynamic client registration on first connect, "
            "so no personal access token lands in config."
        ),
        "docs": "https://docs.gitlab.com/user/model_context_protocol/mcp_server/",
        "spec": {
            "type": "http",
            "url": "https://gitlab.com/api/v4/mcp",
        },
        "env_required": [],
        "editable": ["url"],
        "note": (
            "Self-managed instance? Replace the host — the endpoint is "
            "https://<your-gitlab-host>/api/v4/mcp."
        ),
    },
    {
        "key": "git",
        "title": "Git (local repository)",
        "description": (
            "The MCP reference Git server — read, search, diff, and stage "
            "against a local checkout. Operates on this repository; no network "
            "service and no credentials involved."
        ),
        "docs": "https://github.com/modelcontextprotocol/servers/tree/main/src/git",
        "spec": {
            "type": "stdio",
            "command": "uvx",
            "args": ["mcp-server-git", "--repository", "."],
            "env": {},
        },
        "env_required": [],
        "editable": ["args"],
        "note": (
            "Needs uv on PATH (uvx ships with it). --repository is relative to "
            "where the MCP client starts, which for this project is the repo root."
        ),
    },
    {
        "key": "jama-connect",
        "title": "Jama Connect",
        "description": (
            "Jama Connect MCP — requirements, traceability, reviews, and "
            "baselines, with Jama's own permissions and lifecycle rules "
            "enforced on every tool call. Licensed add-on, enabled per tenant."
        ),
        "docs": "https://help.jamasoftware.com/ah/en/jama-connect-mcp-.html",
        "spec": {
            "type": "http",
            "url": "",
        },
        "env_required": [],
        "editable": ["url"],
        "url_placeholder": "https://<your-jama-instance>/…  (from Jama admin)",
        "note": (
            "Endpoint is instance-specific and published only to licensed "
            "customers — get it from your Jama administrator or Customer "
            "Success Manager. Left blank deliberately rather than guessed."
        ),
    },
    {
        "key": "microsoft-365",
        "title": "Microsoft 365 (Graph, Enterprise)",
        "description": (
            "Microsoft's official MCP Server for Enterprise — natural-language "
            "queries over Microsoft Graph: users, groups, licences, policies, "
            "sign-in and audit logs. Delegated permissions only."
        ),
        "docs": "https://learn.microsoft.com/en-us/graph/mcp-server/get-started",
        "spec": {
            "type": "http",
            "url": "https://mcp.svc.cloud.microsoft/enterprise",
        },
        "env_required": [],
        "editable": ["url"],
        "note": (
            "Tenant/directory data — not Word, Excel, Outlook or SharePoint "
            "file content. A tenant admin must provision the server first. For "
            "document and mailbox content, point the URL at your tenant's "
            "Agent 365 server instead."
        ),
    },
    {
        "key": "miro",
        "title": "Miro",
        "description": (
            "Miro's official MCP server — read and write boards, frames, "
            "diagrams, tables, and documents. OAuth 2.1 with dynamic client "
            "registration; access is scoped to one Miro team, chosen at sign-in."
        ),
        "docs": "https://developers.miro.com/docs/miro-mcp",
        "spec": {
            "type": "http",
            "url": "https://mcp.miro.com",
        },
        "env_required": [],
        "editable": ["url"],
    },
    {
        "key": "lucid",
        "title": "Lucid (Lucidchart / Lucidspark)",
        "description": (
            "Lucid's official MCP server — search a workspace, summarise and "
            "export documents, generate diagrams, and share links across "
            "Lucidchart and Lucidspark. OAuth; no API key."
        ),
        "docs": (
            "https://help.lucid.co/hc/en-us/articles/42578801807508-"
            "Integrate-Lucid-with-AI-tools-using-the-Lucid-MCP-server"
        ),
        "spec": {
            "type": "http",
            "url": "https://mcp.lucid.app/mcp",
        },
        "env_required": [],
        "editable": ["url"],
        "note": (
            "A Lucid account admin must enable MCP access before anyone can "
            "connect. Not available on FedRAMP accounts."
        ),
    },
    {
        "key": "mastercontrol",
        "title": "MasterControl",
        "description": (
            "Controlled documents, DHF records, approvals, and InfoCards. "
            "MasterControl publishes no MCP server — integration today means "
            "its licensed REST/Web Services APIs."
        ),
        "docs": (
            "https://www.mastercontrol.com/resource-center/documents/"
            "mastercontrol-quality-excellence-systems-integrations/"
        ),
        "spec": None,
        "env_required": [],
        "editable": [],
        "availability": "none",
        "note": (
            "Checked 2026-08-07: no vendor MCP server. A third-party one "
            "exists on GitHub but is not catalogued here — a connector holding "
            "credentials to the controlled-document system of record should "
            "clear security review first, then be added via Custom stdio."
        ),
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
