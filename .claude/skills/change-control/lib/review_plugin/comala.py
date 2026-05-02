"""Comala Document Management plugin — STUB.

Comala is a widely-deployed Confluence add-on for workflow + sign-off.
Its REST surface lives at `/rest/cw/1/...`. A real implementation
would parse Comala's sign-off macros from ADF (or call the Comala
REST API) and translate the response into `ApprovalState`.

Not implemented in v0.6 — ships as a stub so the interface contract
is visible and a future contributor knows where to plug in.
"""
from __future__ import annotations

from typing import Any

from .base import (
    ApprovalSigner,
    ApprovalState,
    PluginNotImplemented,
)


class ComalaPlugin:
    name = "ComalaPlugin"

    def detect_approval(self, page_id: str, mcp: Any) -> ApprovalState:
        raise PluginNotImplemented(
            "ComalaPlugin.detect_approval: not implemented in v0.6. "
            "Pick `document_control` in change-control.yml or contribute "
            "the Comala impl upstream."
        )

    def start_workflow(self, page_id: str, mcp: Any) -> None:
        raise PluginNotImplemented("ComalaPlugin.start_workflow: not implemented in v0.6")

    def transition(self, page_id: str, target_state: str, mcp: Any) -> None:
        raise PluginNotImplemented("ComalaPlugin.transition: not implemented in v0.6")

    def supersede(self, page_id: str, mcp: Any) -> None:
        raise PluginNotImplemented("ComalaPlugin.supersede: not implemented in v0.6")

    def list_approvals(self, page_id: str, mcp: Any) -> list[ApprovalSigner]:
        raise PluginNotImplemented("ComalaPlugin.list_approvals: not implemented in v0.6")
