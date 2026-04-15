"""
Jira REST v3 connector.

STATUS: STUB. v1 will be raw httpx against Atlassian Cloud REST v3 with
token auth via TokenAuthenticator.

Endpoint surface:
  - POST   /rest/api/3/issue                      (create ECR)
  - GET    /rest/api/3/issue/{key}                (fetch ECR)
  - POST   /rest/api/3/issue/{key}/transitions    (state change)
  - POST   /rest/api/3/issue/{key}/comment        (comment on unfreeze)
  - POST   /rest/api/3/issueLink                  (link to other issues)

Used by:
  - actions/freeze.py — resolve or create the ECR for a doc being frozen
  - actions/unfreeze.py — comment on the ECR when a freeze is broken
  - actions/release.py — transition the ECR when Windchill release lands
"""
from __future__ import annotations

from ._base import Connector


class JiraConnector(Connector):
    """STUB. See module docstring."""

    async def create_issue(self, project_key: str, summary: str, issue_type: str = "Task") -> dict:
        raise NotImplementedError("JiraConnector.create_issue is a stub.")

    async def get_issue(self, key: str) -> dict:
        raise NotImplementedError("JiraConnector.get_issue is a stub.")

    async def transition(self, key: str, transition_id: str) -> None:
        raise NotImplementedError("JiraConnector.transition is a stub.")

    async def comment(self, key: str, body: str) -> dict:
        raise NotImplementedError("JiraConnector.comment is a stub.")
