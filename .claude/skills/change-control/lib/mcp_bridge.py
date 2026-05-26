"""Runtime MCP bridge — JSON-directive protocol used by bulk actions.

Python actions can't invoke `mcp__atlassian__*` tools directly (those
are agent-side calls). For bulk operations like `adopt-tree` we use a
JSON-directive protocol over a pair of file-descriptors:

  - directives_fd (write side): the action emits one JSON object per
    line:
        {"id": "<uuid>", "tool": "getConfluencePage", "args": {...}}
  - results_fd (read side): the agent (or a fixture-driven stub)
    writes back one JSON object per line:
        {"id": "<uuid>", "ok": true, "result": {...}}
        {"id": "<uuid>", "ok": false, "error": "..."}

The bridge writes a directive, then blocks reading lines until it sees
a result with the matching id. Single-threaded usage is assumed.

Two transport flavors:

  * `StreamMCPProxy(directives, results)` — actions construct this
    against open file objects (typically fd 3 + fd 4 set up by the
    agent shim, or any pair of streams).
  * `FixtureMCPProxy(fixture)` — for tests; maps tool name (or
    a callable on `(tool, args)`) to canned responses.

Both implement the `MCPCallable` protocol from `lib.confluence_mcp` so
`ConfluenceMCP(proxy)` works unchanged.
"""
from __future__ import annotations

import json
import os
import uuid
from typing import Any, Callable, Optional, TextIO


class BridgeError(Exception):
    """Raised when the MCP-bridge protocol fails (mismatched IDs,
    malformed response, EOF before result, etc.)."""


# ---- Stream-based bridge (production use) ----


class StreamMCPProxy:
    """Wraps a pair of streams as an MCPCallable."""

    def __init__(self, directives: TextIO, results: TextIO) -> None:
        self._directives = directives
        self._results = results

    def __call__(self, tool: str, **kwargs: Any) -> Any:
        msg_id = uuid.uuid4().hex
        directive = {"id": msg_id, "tool": tool, "args": kwargs}
        self._directives.write(json.dumps(directive) + "\n")
        self._directives.flush()
        return self._await(msg_id)

    def _await(self, msg_id: str) -> Any:
        while True:
            line = self._results.readline()
            if line == "":
                raise BridgeError(
                    f"mcp-bridge: stream closed while awaiting result for {msg_id}"
                )
            line = line.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
            except ValueError as exc:
                raise BridgeError(
                    f"mcp-bridge: malformed result line: {line!r} ({exc})"
                )
            if payload.get("id") != msg_id:
                # Skip unrelated payloads (defensive — protocol is in-order
                # but this guards against stale lines on retry).
                continue
            if not payload.get("ok", False):
                raise BridgeError(
                    f"mcp-bridge: tool {payload.get('tool', '?')!r} returned "
                    f"error: {payload.get('error', 'unknown')}"
                )
            return payload.get("result")


def open_default_streams() -> tuple[TextIO, TextIO]:
    """Default transport: directives on fd 3, results on fd 4. The agent
    shim opens these before invoking the action."""
    try:
        directives = os.fdopen(3, "w", buffering=1)
        results = os.fdopen(4, "r", buffering=1)
    except OSError as exc:
        raise BridgeError(
            f"mcp-bridge: fd 3/4 not available ({exc}). The action must be "
            f"invoked via the agent shim that opens the directive + result "
            f"streams; see actions/adopt_tree.md for the protocol."
        )
    return directives, results


# ---- Fixture-based proxy (tests + dry-runs) ----


class FixtureMCPProxy:
    """Test transport. Construct with a dict mapping tool name -> response,
    or a callable `(tool, args) -> response`."""

    def __init__(
        self,
        fixture: dict[str, Any] | Callable[[str, dict], Any],
    ) -> None:
        self._fixture = fixture
        self.calls: list[tuple[str, dict]] = []

    def __call__(self, tool: str, **kwargs: Any) -> Any:
        self.calls.append((tool, dict(kwargs)))
        if callable(self._fixture):
            return self._fixture(tool, kwargs)
        if isinstance(self._fixture, dict) and tool in self._fixture:
            return self._fixture[tool]
        raise BridgeError(f"FixtureMCPProxy: no fixture for tool {tool!r}")


def make_proxy(transport: Optional[str] = None, **kwargs: Any):
    """Pick a transport by name."""
    if transport in (None, "stream"):
        d, r = open_default_streams()
        return StreamMCPProxy(d, r)
    if transport == "fixture":
        if "fixture" not in kwargs:
            raise BridgeError("make_proxy(transport='fixture') needs `fixture=`")
        return FixtureMCPProxy(kwargs["fixture"])
    raise BridgeError(f"unknown transport: {transport!r}")
