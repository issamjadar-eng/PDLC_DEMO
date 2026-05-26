"""Review-plugin abstraction for Confluence-side approval tooling.

The skill is shared upstream across customers who use different review
add-ons (Document Control, Comala, SoftComply, etc.). The action layer
never references a specific tool — every approval check routes through
this `ReviewPlugin` interface, and customers pick their implementation
in `change-control.yml` `review_plugin.type`.

Adding a new tool = a new module under `lib/review_plugin/`, NOT a fork
of the action layer. New tooling, new plugin module.

The action layer trusts the plugin's verdict — when `detect_approval`
returns `approved=True`, transition state and capture the evidence
snapshot in frontmatter. No local re-confirmation prompt; that would
defeat the audit trail.
"""
from __future__ import annotations

from .base import (
    ApprovalState,
    ApprovalSigner,
    PluginNotImplemented,
    PluginNotFound,
    PluginError,
    ReviewPlugin,
    load_plugin,
)

__all__ = [
    "ApprovalState",
    "ApprovalSigner",
    "PluginNotImplemented",
    "PluginNotFound",
    "PluginError",
    "ReviewPlugin",
    "load_plugin",
]
