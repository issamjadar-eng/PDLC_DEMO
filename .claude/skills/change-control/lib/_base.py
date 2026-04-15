"""
Connector base class, Authenticator interface, deployment-flavor enum.

STATUS: STUB. Interfaces only — no working implementations.

These are the extensibility seams that let the skill grow without
rewrites:

  - Connector subclasses (ConfluenceConnector, JiraConnector,
    WindchillConnector) inherit common httpx setup, retry/backoff,
    and auth injection.
  - Authenticator implementations (TokenAuthenticator for v1,
    OAuth2Authenticator planned for v2) plug into any Connector.
  - DeploymentFlavor (Cloud for v1, DataCenter planned for v2) lets
    connectors branch on endpoint paths and auth specifics.

When implementation begins, this file becomes the foundation —
build it first, before any concrete connectors.
"""
from __future__ import annotations

from enum import Enum
from typing import Protocol


class DeploymentFlavor(str, Enum):
    """Atlassian deployment target. Project picks one in change-control.yml."""

    CLOUD = "cloud"            # v1 — implemented (when actions ship)
    DATA_CENTER = "data_center"  # v2 planned — stubbed only


class Authenticator(Protocol):
    """Inject auth into an outgoing httpx request. STUB."""

    def inject(self, request) -> None:  # noqa: ANN001
        """Mutate the httpx Request to add auth headers."""
        ...


class TokenAuthenticator:
    """API token + email basic auth. STUB.

    v1 default. Reads (user, token) from OS keychain via `keyring`,
    falls back to environment variables (CONFLUENCE_USER /
    CONFLUENCE_TOKEN, JIRA_USER / JIRA_TOKEN) for projects without
    keychain support.
    """

    def __init__(self, service: str) -> None:
        self.service = service

    def inject(self, request) -> None:  # noqa: ANN001
        raise NotImplementedError(
            "TokenAuthenticator is a stub. See README.md 'Connectivity "
            "Architecture' for the design and tasks/ben/017-change-control-skill.md "
            "for implementation roadmap."
        )


class OAuth2Authenticator:
    """OAuth 2.0 (3LO) authenticator. STUB — v2 planned."""

    def inject(self, request) -> None:  # noqa: ANN001
        raise NotImplementedError("OAuth2Authenticator is a v2 capability.")


class Connector:
    """
    Base class for all external-system connectors.

    STUB. Subclasses (ConfluenceConnector, JiraConnector, ComalaConnector,
    WindchillConnector) will inherit:

      - shared httpx.AsyncClient setup
      - common retry/backoff policy
      - auth injection via the Authenticator
      - structured logging hooks for the audit trail
    """

    def __init__(
        self,
        base_url: str,
        flavor: DeploymentFlavor,
        auth: Authenticator,
    ) -> None:
        self.base_url = base_url
        self.flavor = flavor
        self.auth = auth

    async def request(self, method: str, path: str, **kwargs):  # noqa: ANN003
        raise NotImplementedError("Connector.request is a stub.")
