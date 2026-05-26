"""Review-plugin interface, dataclasses, error types, plugin loader.

The interface is intentionally narrow:
  - `detect_approval(page_id, mcp)` — returns the page's current
    approval state. This is the only call the v0.6 action layer needs
    (used by `freeze` to verify the configured tool reports approval
    before transitioning state to `frozen`).
  - `start_workflow` / `transition` / `supersede` / `list_approvals` —
    reserved for future use (write-side workflow control). Stub-OK
    for v0.6; concrete implementations may raise
    `PluginNotImplemented`.

Concrete plugins live as siblings of this module:
  - `document_control.py` — full implementation, ships with v0.6
  - `comala.py` — stub
  - `softcomply.py` — stub
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional, Protocol


# ---- Errors ----


class PluginError(Exception):
    """Base for review-plugin errors. Carries a recovery hint."""

    recovery: str = "See change-control README on configuring `review_plugin`."

    def __init__(self, message: str, recovery: str | None = None) -> None:
        super().__init__(message)
        if recovery:
            self.recovery = recovery


class PluginNotFound(PluginError):
    recovery = (
        "Set `review_plugin.type` in change-control.yml to one of: "
        "document_control, comala, softcomply."
    )


class PluginNotImplemented(PluginError):
    recovery = (
        "The selected review_plugin does not yet implement this method. "
        "Either pick a plugin that does (document_control ships in v0.6) "
        "or contribute the implementation upstream."
    )


# ---- Dataclasses ----


@dataclass
class ApprovalSigner:
    """A single signature captured by the plugin."""

    account_id: str = ""
    display_name: str = ""
    role: str = ""
    signed_at: str = ""
    raw: dict = field(repr=False, default_factory=dict)


@dataclass
class ApprovalState:
    """Outcome of `detect_approval`. The action layer trusts this verdict."""

    approved: bool
    plugin_name: str
    page_id: str
    page_version: int = 0
    signers: list[ApprovalSigner] = field(default_factory=list)
    evidence_kind: str = ""  # tool-specific tag, e.g. "page-signatures"
    reason: str = ""  # populated when approved=False
    raw: Any = field(repr=False, default=None)

    def to_frontmatter(self) -> dict:
        """Project-agnostic frontmatter snapshot for audit traceability.

        Stored under `confluence.approval.*` on freeze."""
        return {
            "plugin": self.plugin_name,
            "approved": self.approved,
            "page_version": self.page_version,
            "evidence_kind": self.evidence_kind,
            "signers": [
                {
                    "account_id": s.account_id,
                    "display_name": s.display_name,
                    "role": s.role,
                    "signed_at": s.signed_at,
                }
                for s in self.signers
            ],
        }


# ---- Interface ----


class ReviewPlugin(Protocol):
    """Plugin contract. Implementations live in sibling modules."""

    name: str

    def detect_approval(
        self,
        page_id: str,
        mcp: Any,  # ConfluenceMCP — Any-typed to avoid circular import
    ) -> ApprovalState: ...

    def start_workflow(self, page_id: str, mcp: Any) -> None: ...

    def transition(self, page_id: str, target_state: str, mcp: Any) -> None: ...

    def supersede(self, page_id: str, mcp: Any) -> None: ...

    def list_approvals(self, page_id: str, mcp: Any) -> list[ApprovalSigner]: ...


# ---- Loader ----


def load_plugin(plugin_type: str) -> ReviewPlugin:
    """Resolve a plugin by `change-control.yml` `review_plugin.type`.

    Raises `PluginNotFound` for unknown names. Importing the plugin
    module is deferred until lookup so a missing optional dependency
    in one plugin doesn't block the others.
    """
    key = (plugin_type or "").strip().lower()
    if key in ("", "none"):
        raise PluginNotFound("review_plugin.type is empty in change-control.yml")
    if key == "document_control":
        from .document_control import DocumentControlPlugin

        return DocumentControlPlugin()
    if key == "comala":
        from .comala import ComalaPlugin

        return ComalaPlugin()
    if key == "softcomply":
        from .softcomply import SoftComplyPlugin

        return SoftComplyPlugin()
    raise PluginNotFound(
        f"unknown review_plugin.type: {plugin_type!r}. "
        f"Known types: document_control, comala, softcomply."
    )
