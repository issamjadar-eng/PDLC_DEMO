"""Document Control plugin — full implementation (v0.6 reference plugin).

Document Control is an Atlassian Marketplace add-on that records Part 11
e-signatures on Confluence pages via a `page-signatures` extension macro.
This plugin reads the page's ADF, locates the macro, and parses the
signers + signed-at timestamps to produce an `ApprovalState`.

The action layer is agnostic of the macro name — only this plugin
recognizes `page-signatures`. New tooling (Comala, SoftComply, …) =
new plugin module, NOT a fork of `freeze.py`.

Macro shapes seen in the wild (from the AFAI/AI_PDLC_INT_TEST sandbox
and real DHF pages like Product Overview `5132713985`):

    {
        "type": "extension",
        "attrs": {
            "extensionKey": "page-signatures",
            "extensionType": "...",
            "parameters": {
                "macroParams": {
                    "signatures": {
                        "value": "<json or escaped string>"
                    }
                }
            }
        }
    }

The exact `signatures` payload varies across Document Control versions.
We accept several shapes:
  - JSON-encoded list of `{accountId, displayName, role, signedAt}`
  - JSON-encoded dict `{signatures: [...]}`
  - flat list embedded directly in `attrs.parameters`
  - a `localInfo`/`bodyInfo` block carrying signer metadata

Whatever we extract, we return as a project-agnostic
`ApprovalState(approved=True, signers=[...], evidence_kind="page-signatures")`.
On absent / empty / un-parseable macros we return
`approved=False` with a populated `reason` string.

This plugin is read-only in v0.6: `start_workflow`, `transition`,
`supersede` raise `PluginNotImplemented`. v0.7 may add write-side
support if Document Control exposes a stable REST surface.
"""
from __future__ import annotations

import json
from typing import Any

from .base import (
    ApprovalSigner,
    ApprovalState,
    PluginNotImplemented,
    ReviewPlugin,
)


EXTENSION_KEY = "page-signatures"


class DocumentControlPlugin:
    """Reference implementation. See module docstring for shape coverage."""

    name = "DocumentControlPlugin"

    # ---- Approval detection (read-side) ----

    def detect_approval(self, page_id: str, mcp: Any) -> ApprovalState:
        """Fetch the page as ADF, locate the page-signatures macro,
        parse signers, and return an `ApprovalState`."""
        page = mcp.get_page(page_id, content_format="adf")
        adf_body = page.body
        if not adf_body:
            return ApprovalState(
                approved=False,
                plugin_name=self.name,
                page_id=page_id,
                page_version=page.version,
                evidence_kind=EXTENSION_KEY,
                reason=(
                    f"DocumentControlPlugin: page {page_id} has empty body; "
                    f"no `{EXTENSION_KEY}` macro present."
                ),
            )
        try:
            adf = json.loads(adf_body) if isinstance(adf_body, str) else adf_body
        except (ValueError, TypeError) as exc:
            return ApprovalState(
                approved=False,
                plugin_name=self.name,
                page_id=page_id,
                page_version=page.version,
                evidence_kind=EXTENSION_KEY,
                reason=(
                    f"DocumentControlPlugin: page {page_id} ADF body is not "
                    f"valid JSON ({exc}); cannot detect approval."
                ),
            )

        nodes = find_signature_macros(adf)
        if not nodes:
            return ApprovalState(
                approved=False,
                plugin_name=self.name,
                page_id=page_id,
                page_version=page.version,
                evidence_kind=EXTENSION_KEY,
                reason=(
                    f"DocumentControlPlugin: no `{EXTENSION_KEY}` macro present "
                    f"on page {page_id}; cannot transition to frozen."
                ),
            )

        signers: list[ApprovalSigner] = []
        for node in nodes:
            signers.extend(parse_signers_from_node(node))

        if not signers:
            return ApprovalState(
                approved=False,
                plugin_name=self.name,
                page_id=page_id,
                page_version=page.version,
                evidence_kind=EXTENSION_KEY,
                reason=(
                    f"DocumentControlPlugin: `{EXTENSION_KEY}` macro present on "
                    f"page {page_id} but contains no parsed signers."
                ),
                raw=nodes,
            )

        return ApprovalState(
            approved=True,
            plugin_name=self.name,
            page_id=page_id,
            page_version=page.version,
            evidence_kind=EXTENSION_KEY,
            signers=signers,
            raw=nodes,
        )

    # ---- Write-side stubs ----

    def start_workflow(self, page_id: str, mcp: Any) -> None:
        raise PluginNotImplemented(
            "DocumentControlPlugin.start_workflow: v0.6 uses manual UI handoff "
            "for workflow start; this method is reserved for v0.7+."
        )

    def transition(self, page_id: str, target_state: str, mcp: Any) -> None:
        raise PluginNotImplemented(
            "DocumentControlPlugin.transition: v0.6 uses manual UI handoff "
            "for workflow transitions."
        )

    def supersede(self, page_id: str, mcp: Any) -> None:
        raise PluginNotImplemented(
            "DocumentControlPlugin.supersede: v0.6 uses manual UI handoff "
            "for supersede."
        )

    def list_approvals(self, page_id: str, mcp: Any) -> list[ApprovalSigner]:
        return self.detect_approval(page_id, mcp).signers


# ---- Pure helpers (testable without MCP) ----


def find_signature_macros(adf: Any) -> list[dict]:
    """Return every `extension`/`bodiedExtension` node whose
    `attrs.extensionKey == "page-signatures"`."""
    out: list[dict] = []
    _collect_macros(adf, out)
    return out


def _collect_macros(node: Any, out: list[dict]) -> None:
    if isinstance(node, dict):
        if node.get("type") in ("extension", "bodiedExtension", "inlineExtension"):
            attrs = node.get("attrs") or {}
            if attrs.get("extensionKey") == EXTENSION_KEY:
                out.append(node)
        for v in node.values():
            _collect_macros(v, out)
    elif isinstance(node, list):
        for v in node:
            _collect_macros(v, out)


def parse_signers_from_node(node: dict) -> list[ApprovalSigner]:
    """Extract signers from a single `page-signatures` macro node.

    Several shapes are supported because Document Control's macro body
    differs across versions and configurations. We try them in priority
    order and stop at the first that yields signers.
    """
    attrs = node.get("attrs") or {}
    parameters = attrs.get("parameters") or {}
    macro_params = parameters.get("macroParams") or {}

    # Shape A: macroParams.signatures.value is a JSON-encoded list/dict
    sig_param = macro_params.get("signatures") or {}
    sig_value = (
        sig_param.get("value") if isinstance(sig_param, dict) else sig_param
    )
    if isinstance(sig_value, str) and sig_value.strip():
        parsed = _safe_load_json(sig_value)
        signers = _signers_from_parsed(parsed)
        if signers:
            return signers

    # Shape B: parameters.signatures is the parsed list directly
    if "signatures" in parameters:
        signers = _signers_from_parsed(parameters["signatures"])
        if signers:
            return signers

    # Shape C: localInfo / bodyInfo carries a list under .signatures or .signers
    for key in ("localInfo", "bodyInfo"):
        info = attrs.get(key) or {}
        if isinstance(info, dict):
            for k in ("signatures", "signers", "approvals"):
                if k in info:
                    signers = _signers_from_parsed(info[k])
                    if signers:
                        return signers

    # Shape D: bodied extension — walk content for signature paragraphs
    content = node.get("content")
    if isinstance(content, list):
        signers = _signers_from_body_text(content)
        if signers:
            return signers

    return []


def _safe_load_json(s: str) -> Any:
    try:
        return json.loads(s)
    except (ValueError, TypeError):
        return None


def _signers_from_parsed(parsed: Any) -> list[ApprovalSigner]:
    """Accept a list of dicts, a `{signatures: [...]}` wrapper, or
    a `{signers: [...]}` wrapper. Returns `[]` for unrecognized shapes."""
    if parsed is None:
        return []
    if isinstance(parsed, dict):
        for k in ("signatures", "signers", "approvals"):
            if k in parsed and isinstance(parsed[k], list):
                return _signers_from_list(parsed[k])
        # Single signer dict
        single = _signer_from_dict(parsed)
        return [single] if single else []
    if isinstance(parsed, list):
        return _signers_from_list(parsed)
    return []


def _signers_from_list(items: list) -> list[ApprovalSigner]:
    out: list[ApprovalSigner] = []
    for it in items:
        if isinstance(it, dict):
            s = _signer_from_dict(it)
            if s:
                out.append(s)
    return out


def _signer_from_dict(d: dict) -> ApprovalSigner | None:
    account_id = (
        d.get("accountId") or d.get("userKey") or d.get("user") or d.get("id") or ""
    )
    display = (
        d.get("displayName") or d.get("name") or d.get("fullName") or d.get("user") or ""
    )
    role = d.get("role") or d.get("approvalRole") or ""
    signed_at = (
        d.get("signedAt")
        or d.get("date")
        or d.get("timestamp")
        or d.get("approvedAt")
        or ""
    )
    if not (account_id or display):
        return None
    return ApprovalSigner(
        account_id=str(account_id),
        display_name=str(display),
        role=str(role),
        signed_at=str(signed_at),
        raw=d,
    )


def _signers_from_body_text(content: list) -> list[ApprovalSigner]:
    """Last-resort: walk a bodied extension's content for paragraph
    text matching `Signed by <Name> <date>` or similar. Yields a
    single signer per such paragraph."""
    out: list[ApprovalSigner] = []
    for node in content:
        if not isinstance(node, dict):
            continue
        if node.get("type") == "paragraph":
            text = "".join(
                c.get("text", "")
                for c in node.get("content") or []
                if isinstance(c, dict) and c.get("type") == "text"
            )
            stripped = text.strip()
            if not stripped:
                continue
            # We don't try to be clever — capture the line as displayName.
            out.append(
                ApprovalSigner(
                    account_id="",
                    display_name=stripped,
                    role="",
                    signed_at="",
                    raw={"paragraph": stripped},
                )
            )
    return out
