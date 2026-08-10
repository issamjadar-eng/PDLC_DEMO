"""Shared display-only markdown helpers for console views.

Uses the `markdown` package from the console venv when available; falls back
to an escaped <pre>. Kept tiny and dependency-optional so views degrade rather
than 500. (gap_analysis and the documents renderer predate this module and
carry their own handling — new views import from here.)
"""
from __future__ import annotations

import html as _html
import re as _re


def md_to_html(text: str) -> str:
    if not text:
        return ""
    try:
        import markdown  # type: ignore

        return markdown.markdown(text, extensions=["tables", "sane_lists", "fenced_code"])
    except Exception:
        return f"<pre class='md-raw'>{_html.escape(text)}</pre>"


def md_inline(text: str) -> str:
    """Escape + minimal inline markdown (`code`, **bold**, [label](url) → label).
    For table cells / one-liners where a full <p>-wrapped render is unwanted."""
    s = _html.escape(text)
    s = _re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", s)
    s = _re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = _re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    return s
