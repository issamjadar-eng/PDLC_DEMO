"""
Windchill PLM connector.

STATUS: STUB. Phase 3 capability — last to be implemented.

The vault layer is intentionally deferred until Phase 1 (draft) and
Phase 2 (Confluence formal review) are working end-to-end. Once the
Comala "Released" webhook fires, this connector takes the signed PDF
+ metadata, creates a new Windchill ECO referencing the Jira ECR, and
attaches the artifact.

Connection options under consideration (none implemented):

  - Windchill REST Services (WRS) — modern REST API on PTC Windchill
    11.x and later. Cleanest option for Cloud or recent on-prem.
  - Info*Engine SOAP — legacy but widely deployed. Many regulated
    medtech shops are still on this.
  - File-based drop folder + Windchill workflow trigger — lowest-tech
    fallback when neither API is available. Drop signed PDF + metadata
    XML into a shared folder; Windchill polls and creates the ECO.

Auth typically OAuth 2.0 client credentials against PTC's identity
service, or SAML for on-prem. Unlike Atlassian Cloud, Windchill
deployments vary widely — the connector design will likely need a
WindchillTransport interface (REST vs SOAP vs file-drop) similar to
the ReviewPlugin abstraction for Comala/SoftComply.
"""
from __future__ import annotations

from pathlib import Path

from ._base import Connector


class WindchillConnector(Connector):
    """STUB. Phase 3 — see module docstring."""

    async def create_eco(
        self,
        title: str,
        description: str,
        jira_ecr: str,
    ) -> str:
        """Create an ECO and return its number. STUB."""
        raise NotImplementedError("WindchillConnector is a Phase 3 stub.")

    async def attach_pdf(self, eco_number: str, pdf_path: Path) -> None:
        raise NotImplementedError("WindchillConnector is a Phase 3 stub.")

    async def promote_to_released(self, eco_number: str) -> None:
        raise NotImplementedError("WindchillConnector is a Phase 3 stub.")
