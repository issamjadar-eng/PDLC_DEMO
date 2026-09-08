"""Adapter registry.

Maps a config `type` (or section name) to a Provider class. Adding a backend is
one entry here plus one module — never a change to callers.
"""

from __future__ import annotations

from typing import Any

from .base import Provider
from .providers import (
    AntigravityProvider,
    CodexProvider,
    GrokProvider,
    OpenAIHttpProvider,
)

REGISTRY: dict[str, type[Provider]] = {
    "grok": GrokProvider,
    "codex": CodexProvider,
    "antigravity": AntigravityProvider,
    "openai_http": OpenAIHttpProvider,
    # Aliases so a config section can be named naturally.
    "gemini": AntigravityProvider,
    "openai": OpenAIHttpProvider,
    "xai": GrokProvider,
}


def register(type_name: str, cls: type[Provider]) -> None:
    """Add a provider type at runtime, for host projects with custom backends."""
    REGISTRY[type_name] = cls


def build_provider(name: str, cfg: dict[str, Any]) -> Provider | None:
    """Instantiate one provider from config. Returns None if the type is unknown.

    Falls back to the section name as the type, so a `grok:` entry needs no
    redundant `type: grok`.
    """
    type_name = cfg.get("type", name)
    cls = REGISTRY.get(type_name)
    return cls(name, cfg) if cls else None
