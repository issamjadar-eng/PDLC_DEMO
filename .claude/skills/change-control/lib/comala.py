"""
Review-plugin abstraction — Comala Document Management + SoftComply.

STATUS: STUB. v1 will implement ComalaPlugin against the Comala REST API
(`/rest/cw/1/...`). SoftComplyPlugin is reserved as a stub; implementation
is a v2 capability.

The ReviewPlugin interface lets the project pick its plugin in
change-control.yml — the action layer never knows which one is in use.
This is one of the six extensibility seams documented in README.md.
"""
from __future__ import annotations

from typing import Protocol


class ReviewPlugin(Protocol):
    """Shared interface for Confluence review/sign-off plugins. STUB."""

    async def get_state(self, page_id: str) -> str: ...
    async def transition(self, page_id: str, target_state: str) -> None: ...
    async def supersede(self, page_id: str) -> None: ...
    async def list_approvals(self, page_id: str) -> list[dict]: ...


class ComalaPlugin:
    """Comala Document Management. STUB.

    Endpoint surface (planned):
      - GET    /rest/cw/1/content/{pageId}/state
      - POST   /rest/cw/1/content/{pageId}/transition
      - POST   /rest/cw/1/content/{pageId}/supersede
      - GET    /rest/cw/1/content/{pageId}/approvals
    """

    async def get_state(self, page_id: str) -> str:
        raise NotImplementedError("ComalaPlugin is a stub.")

    async def transition(self, page_id: str, target_state: str) -> None:
        raise NotImplementedError("ComalaPlugin is a stub.")

    async def supersede(self, page_id: str) -> None:
        raise NotImplementedError("ComalaPlugin is a stub.")

    async def list_approvals(self, page_id: str) -> list[dict]:
        raise NotImplementedError("ComalaPlugin is a stub.")


class SoftComplyPlugin:
    """SoftComply eQMS. STUB — v2 planned."""

    async def get_state(self, page_id: str) -> str:
        raise NotImplementedError("SoftComplyPlugin is a v2 capability.")

    async def transition(self, page_id: str, target_state: str) -> None:
        raise NotImplementedError("SoftComplyPlugin is a v2 capability.")

    async def supersede(self, page_id: str) -> None:
        raise NotImplementedError("SoftComplyPlugin is a v2 capability.")

    async def list_approvals(self, page_id: str) -> list[dict]:
        raise NotImplementedError("SoftComplyPlugin is a v2 capability.")
