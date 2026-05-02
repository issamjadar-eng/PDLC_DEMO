"""Freeze helper — verify reviewer-tool approval and lock the doc.

`freeze` is agent-orchestrated (Option A). The agent:
  1. Reads `change-control.yml` to learn the configured plugin type.
  2. Calls `mcp__atlassian__getAccessibleAtlassianResources` for cloudId.
  3. Calls `mcp__atlassian__getConfluencePage(adf)` for the page.
  4. Pipes the response into `freeze_helper.py verify` which loads the
     plugin, runs `detect_approval`, and either:
       - on approved=True: updates frontmatter to `state: frozen` with
         `confluence.approval` evidence snapshot, prints the named
         success line ("DocumentControlPlugin detected approval ..."),
         and returns 0.
       - on approved=False: prints the plugin's named reason and
         returns non-zero — fail loud, no fallback.

Subcommands:
  verify    Read plugin config + page response + run plugin.detect_approval.
            Update frontmatter on success.
  unfreeze  Reopen a frozen doc back to `published`. Pure local frontmatter
            mutation (no MCP, no Jira).

The `verify` flow consumes the MCP response on stdin (so the agent
doesn't have to pass page IDs back into the helper — the helper reads
the live ADF directly).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

SKILL_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL_ROOT))

from lib.frontmatter import (  # noqa: E402
    read as read_frontmatter,
    update as update_frontmatter,
)
from lib.review_plugin import (  # noqa: E402
    ApprovalState,
    PluginError,
    PluginNotFound,
    PluginNotImplemented,
    load_plugin,
)


# ---- Argument parsing ----


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="freeze_helper",
        description="Verify reviewer-tool approval and lock the doc.",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    v = sub.add_parser(
        "verify",
        help="Run plugin.detect_approval against the page on stdin (ADF response).",
    )
    v.add_argument("--source", required=True, help="Path to the local markdown source.")
    v.add_argument(
        "--plugin",
        required=True,
        help="Plugin type: document_control | comala | softcomply.",
    )
    v.add_argument(
        "--lifecycle-from",
        default="review-formal",
        help="Required current state in frontmatter (default: review-formal).",
    )
    v.add_argument(
        "--lifecycle-to",
        default="frozen",
        help="State to transition to on success (default: frozen).",
    )

    u = sub.add_parser(
        "unfreeze",
        help="Reopen a frozen doc back to published. Pure local frontmatter mutation.",
    )
    u.add_argument("--source", required=True)
    u.add_argument(
        "--required-state",
        default="frozen",
        help="State the doc must currently be in (default: frozen).",
    )
    u.add_argument(
        "--target-state",
        default="published",
        help="State to transition to (default: published).",
    )

    return p


# ---- MCP-response helpers ----


def _mcp_response_from_stdin() -> dict:
    raw = sys.stdin.read()
    if not raw.strip():
        print("freeze_helper: no MCP response on stdin", file=sys.stderr)
        sys.exit(64)
    try:
        return json.loads(raw)
    except ValueError as exc:
        print(f"freeze_helper: stdin is not valid JSON: {exc}", file=sys.stderr)
        sys.exit(65)


# ---- A "page" object the plugin's detect_approval expects ----


class _PageView:
    """Quack-typed `ConfluencePage`-like object — what plugins read."""

    def __init__(self, raw: dict) -> None:
        self.raw = raw
        body = raw.get("body")
        if isinstance(body, dict) and body.get("type") == "doc":
            self.body = body
            self.body_format = "adf"
        elif isinstance(body, dict):
            for key in ("atlas_doc_format", "storage", "view"):
                slot = body.get(key)
                if isinstance(slot, dict) and "value" in slot:
                    self.body = slot["value"]
                    self.body_format = key
                    break
            else:
                self.body = ""
                self.body_format = "adf"
        else:
            self.body = body or ""
            self.body_format = "adf"
        version_section = raw.get("version") or {}
        try:
            self.version = int(version_section.get("number") or 0)
        except (TypeError, ValueError):
            self.version = 0
        self.title = str(raw.get("title", ""))
        self.page_id = str(raw.get("id") or raw.get("pageId") or "")


class _MCPShim:
    """A tiny stand-in for ConfluenceMCP — plugins call `get_page(page_id, content_format=...)`."""

    def __init__(self, raw: dict) -> None:
        self._page = _PageView(raw)

    def get_page(self, page_id: str, content_format: str = "adf") -> _PageView:
        return self._page


# ---- Subcommand handlers ----


def cmd_verify(args: argparse.Namespace) -> int:
    source_path = Path(args.source)
    fm = read_frontmatter(source_path)
    current_state = fm.data.get("state")
    if current_state != args.lifecycle_from:
        print(
            f"freeze_helper: refusing — doc state is {current_state!r}, "
            f"expected {args.lifecycle_from!r}",
            file=sys.stderr,
        )
        return 66

    confluence = fm.data.get("confluence") or {}
    page_id = str(confluence.get("page_id") or "")
    if not page_id:
        print(
            "freeze_helper: refusing — frontmatter has no confluence.page_id",
            file=sys.stderr,
        )
        return 66

    raw = _mcp_response_from_stdin()
    mcp = _MCPShim(raw)

    try:
        plugin = load_plugin(args.plugin)
    except PluginNotFound as exc:
        print(f"freeze_helper: {exc}", file=sys.stderr)
        return 67

    try:
        state: ApprovalState = plugin.detect_approval(page_id, mcp)
    except PluginNotImplemented as exc:
        print(
            f"freeze_helper: {plugin.name}.detect_approval is a stub "
            f"({exc}); pick `document_control` in change-control.yml or "
            f"contribute the impl upstream.",
            file=sys.stderr,
        )
        return 67
    except PluginError as exc:
        print(f"freeze_helper: plugin error: {exc}", file=sys.stderr)
        return 67

    if not state.approved:
        print(state.reason or f"{plugin.name}: no approval found.", file=sys.stderr)
        return 1

    # Approved — write evidence snapshot + transition state
    update_frontmatter(
        source_path,
        state=args.lifecycle_to,
        confluence={
            "frozen_at_version": state.page_version,
            "approval": state.to_frontmatter(),
        },
    )
    signers_str = ", ".join(s.display_name or s.account_id for s in state.signers) or "-"
    print(
        f"{state.plugin_name} detected approval signatures "
        f"[{signers_str}] on page {page_id} v{state.page_version}. "
        f"Transitioning state to {args.lifecycle_to!r}."
    )
    return 0


def cmd_unfreeze(args: argparse.Namespace) -> int:
    source_path = Path(args.source)
    fm = read_frontmatter(source_path)
    current_state = fm.data.get("state")
    if current_state != args.required_state:
        print(
            f"unfreeze: refusing — doc state is {current_state!r}, "
            f"expected {args.required_state!r}",
            file=sys.stderr,
        )
        return 66

    from datetime import datetime, timezone
    unfrozen_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    update_frontmatter(
        source_path,
        state=args.target_state,
        confluence={
            "frozen_at_version": None,
            "unfrozen_at": unfrozen_at,
        },
    )
    print(
        f"unfreeze: WARNING — reopening this doc invalidates the prior "
        f"approval. Inform the review tool (Document Control / Comala / "
        f"SoftComply) via the Confluence UI to mark the page Superseded."
    )
    print(f"unfreeze: state {args.required_state!r} -> {args.target_state!r}")
    return 0


# ---- Entry ----


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.cmd == "verify":
        return cmd_verify(args)
    if args.cmd == "unfreeze":
        return cmd_unfreeze(args)
    parser.error(f"unknown command: {args.cmd}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
