"""
Read/write the `state:` block on controlled docs.

STATUS: STUB. Trivial but foundational — implement first when work begins.

The frontmatter contract (see README.md "The Frontmatter Contract"):

    ---
    title: ...
    state: draft | frozen | released
    doc_class: design-input
    frozen_at: 2026-04-14
    frozen_commit: a3f9c21
    confluence_page_id: 458291
    confluence_version_at_publish: 1
    jira_ecr: PP3500-1234
    windchill_eco: null
    ---
"""
from __future__ import annotations

from pathlib import Path
from typing import Any


def read(path: Path) -> dict[str, Any]:
    """Read the YAML frontmatter block from a markdown file. STUB."""
    raise NotImplementedError("frontmatter.read is a stub.")


def write(path: Path, data: dict[str, Any]) -> None:
    """Replace the YAML frontmatter block, preserving body. STUB."""
    raise NotImplementedError("frontmatter.write is a stub.")


def get_state(path: Path) -> str | None:
    """Return the `state` field, or None if not a controlled doc. STUB."""
    raise NotImplementedError("frontmatter.get_state is a stub.")
