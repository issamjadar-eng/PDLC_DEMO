"""
Confluence base API connector.

STATUS: STUB. v1 will be raw httpx against Atlassian Cloud REST v2,
shelling out to `mark` (kovetskiy/mark) for markdown → Confluence
rendering at publish time.

Endpoint surface (Cloud v2):
  - GET    /wiki/api/v2/pages/{id}            (read page + version)
  - POST   /wiki/api/v2/pages                 (create page)
  - PUT    /wiki/api/v2/pages/{id}            (update page — new version)
  - GET    /wiki/api/v2/pages/{id}/versions
  - GET    /wiki/api/v2/pages/{id}/comments
  - POST   /wiki/api/v2/attachments

Publish flow:
  1. Caller hands us a markdown file path and target space.
  2. Shell out to `mark -u $user -p $token -b $base_url <file>`.
  3. Parse mark's output to extract the page ID and new version number.
  4. Return both to the freeze action for frontmatter capture.

Read flow uses raw httpx with token auth via TokenAuthenticator.

Data Center support is a v2 capability — the connector will branch on
DeploymentFlavor for endpoint paths (`/rest/api` vs `/wiki/api/v2`).
"""
from __future__ import annotations

from pathlib import Path

from ._base import Connector


class ConfluenceConnector(Connector):
    """STUB. See module docstring for the planned design."""

    async def get_page(self, page_id: str) -> dict:
        raise NotImplementedError("ConfluenceConnector.get_page is a stub.")

    async def publish_markdown(
        self,
        path: Path,
        space_key: str,
        parent_page_id: str | None = None,
    ) -> tuple[str, int]:
        """Publish markdown via `mark` shell-out. Returns (page_id, version). STUB."""
        raise NotImplementedError("ConfluenceConnector.publish_markdown is a stub.")

    async def list_comments(self, page_id: str) -> list[dict]:
        raise NotImplementedError("ConfluenceConnector.list_comments is a stub.")

    async def attach_file(self, page_id: str, path: Path) -> dict:
        raise NotImplementedError("ConfluenceConnector.attach_file is a stub.")
