"""SoftComply plugin — STUB.

SoftComply ships sign-off + traceability add-ons used in some regulated
Confluence deployments. A real implementation would parse SoftComply
approval macros from ADF and translate the result into `ApprovalState`.

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


class SoftComplyPlugin:
    name = "SoftComplyPlugin"

    def detect_approval(self, page_id: str, mcp: Any) -> ApprovalState:
        raise PluginNotImplemented(
            "SoftComplyPlugin.detect_approval: not implemented in v0.6. "
            "Pick `document_control` in change-control.yml or contribute "
            "the SoftComply impl upstream."
        )

    def start_workflow(self, page_id: str, mcp: Any) -> None:
        raise PluginNotImplemented("SoftComplyPlugin.start_workflow: not implemented in v0.6")

    def transition(self, page_id: str, target_state: str, mcp: Any) -> None:
        raise PluginNotImplemented("SoftComplyPlugin.transition: not implemented in v0.6")

    def supersede(self, page_id: str, mcp: Any) -> None:
        raise PluginNotImplemented("SoftComplyPlugin.supersede: not implemented in v0.6")

    def list_approvals(self, page_id: str, mcp: Any) -> list[ApprovalSigner]:
        raise PluginNotImplemented("SoftComplyPlugin.list_approvals: not implemented in v0.6")
