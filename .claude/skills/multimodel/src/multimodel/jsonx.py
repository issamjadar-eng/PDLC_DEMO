"""JSON extraction from messy model output.

Agentic CLIs do not return clean documents. Observed in practice:

- A bare object.
- A fenced ```json block.
- An envelope such as ``{"text": "..."}`` whose payload is a *string* of JSON.
- **Several concatenated objects** in one stream, where an agent emitted interim
  status objects while researching and the real answer came last.

That third-and-fourth combination once caused a fail-open bug: a naive
``find('{')`` / ``rfind('}')`` spanned the whole stream, parsed as the envelope,
found none of the expected keys, and silently returned defaults that read as
approval. Everything here exists to make that failure impossible.
"""

from __future__ import annotations

import json
from typing import Any


def iter_json_objects(text: str) -> list[str]:
    """Return every balanced top-level ``{...}`` span in text.

    A brace-counting scan that respects string literals and escapes, so braces
    or quotes inside a value cannot desynchronise it.
    """
    spans: list[str] = []
    depth = 0
    start: int | None = None
    in_string = False
    escaped = False

    for index, char in enumerate(text):
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue

        if char == '"':
            in_string = True
        elif char == "{":
            if depth == 0:
                start = index
            depth += 1
        elif char == "}" and depth > 0:
            depth -= 1
            if depth == 0 and start is not None:
                spans.append(text[start : index + 1])
                start = None

    return spans


def strip_fences(text: str) -> str:
    """Remove a surrounding ``` fence if present."""
    cleaned = text.strip()
    if not cleaned.startswith("```"):
        return cleaned
    lines = cleaned.splitlines()
    if len(lines) > 2:
        lines = lines[1:-1]
    return "\n".join(lines).removeprefix("json").strip()


def collect_objects(
    text: str,
    required_key: str | None = None,
    _depth: int = 0,
) -> list[dict[str, Any]]:
    """Find candidate JSON objects, descending one level into string envelopes.

    Args:
        text: raw provider output.
        required_key: if given, only objects containing this key are returned,
            and envelope strings are searched for nested matches. This is what
            lets a caller say "I want the object that actually answered me",
            rather than accepting the first well-formed thing it sees.
    """
    if _depth > 3:
        return []

    found: list[dict[str, Any]] = []
    for span in iter_json_objects(strip_fences(text)):
        try:
            parsed = json.loads(span)
        except json.JSONDecodeError:
            continue
        if not isinstance(parsed, dict):
            continue

        if required_key is None or required_key in parsed:
            found.append(parsed)
            continue

        # Envelope: descend into string-valued fields that look like payloads.
        for value in parsed.values():
            if isinstance(value, str) and "{" in value:
                found.extend(collect_objects(value, required_key, _depth + 1))

    return found


def best_object(text: str, required_key: str | None = None) -> dict[str, Any] | None:
    """Pick the most likely *final* answer object from messy output.

    Last wins: an agentic model streams interim objects and then its conclusion.
    Where several candidates qualify, prefer the last one carrying substantive
    content over a bare status ping.

    Returns None when nothing qualifies — which callers must treat as "no
    answer", never as an empty-but-valid answer.
    """
    candidates = collect_objects(text, required_key)
    if not candidates:
        return None

    substantive = [
        obj for obj in candidates
        if any(isinstance(v, str) and v.strip() for v in obj.values())
    ]
    return (substantive or candidates)[-1]


def first_required_key(schema: dict[str, Any] | None) -> str | None:
    """The key used to find the answer object among the noise.

    The first entry of `required` wins; otherwise the first declared property.
    Callers should put the most identifying field first in `required`.
    """
    if not schema:
        return None
    required = schema.get("required") or []
    if required:
        return str(required[0])
    properties = schema.get("properties") or {}
    return next(iter(properties), None)
