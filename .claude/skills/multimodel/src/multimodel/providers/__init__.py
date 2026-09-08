"""Provider implementations.

One module per backend. Each is independent — deleting one, or adding another,
should not touch anything else.
"""

from .antigravity import AntigravityProvider
from .codex import CodexProvider
from .grok import GrokProvider
from .openai_http import OpenAIHttpProvider

__all__ = [
    "AntigravityProvider",
    "CodexProvider",
    "GrokProvider",
    "OpenAIHttpProvider",
]
