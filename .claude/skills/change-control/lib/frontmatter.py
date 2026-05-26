"""HTML-comment YAML frontmatter for controlled docs.

The contract (locked by Probe A — must NOT render in Confluence):

    <!--
    state: published
    title: <Document Title>
    confluence:
      page_id: <numeric-page-id>
      space_key: <SPACE>
      parent_page_id: <numeric-parent-id>
      page_path: <SPACE>/<parent-title>/<page-title>
      adopted_at: YYYY-MM-DD
      adopted_from_version: 1
      last_published_version: 1
    -->

    # Page Title

    body...

The leading `<!-- ... -->` block is stripped before push (Probe A).
This module is the read/write contract.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    import yaml  # type: ignore
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore


_FRONTMATTER_RE = re.compile(
    r"\A\s*<!--\s*\n(?P<yaml>.*?)\n-->\s*\n?",
    re.DOTALL,
)


@dataclass
class Frontmatter:
    data: dict
    body: str
    raw_block: str = ""  # the original `<!-- ... -->` block (for round-trip)


# ---- Pure parse / serialize ----


def parse(text: str) -> Frontmatter:
    """Split a markdown source into (frontmatter dict, body).

    If no leading `<!-- ... -->` block is present, returns an empty
    dict and the full text as body.
    """
    if yaml is None:
        raise RuntimeError("PyYAML is required for frontmatter parsing")
    m = _FRONTMATTER_RE.match(text)
    if not m:
        return Frontmatter(data={}, body=text, raw_block="")
    raw_yaml = m.group("yaml")
    parsed = yaml.safe_load(raw_yaml) if raw_yaml.strip() else {}
    if not isinstance(parsed, dict):
        parsed = {}
    return Frontmatter(
        data=parsed,
        body=text[m.end():],
        raw_block=text[: m.end()],
    )


def serialize(data: dict, body: str) -> str:
    """Render a frontmatter+body markdown source string."""
    if yaml is None:
        raise RuntimeError("PyYAML is required for frontmatter serialization")
    yaml_text = yaml.safe_dump(
        data, sort_keys=False, default_flow_style=False, allow_unicode=True
    ).rstrip() + "\n"
    return f"<!--\n{yaml_text}-->\n\n{body.lstrip()}"


# ---- I/O ----


def read(path: Path | str) -> Frontmatter:
    p = Path(path)
    return parse(p.read_text(encoding="utf-8"))


def write(path: Path | str, data: dict, body: str) -> Path:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(serialize(data, body), encoding="utf-8")
    return p


def update(path: Path | str, **updates: Any) -> Path:
    """Read frontmatter, deep-merge `updates` into the dict, write back.

    `updates` keys with dict values are deep-merged so callers can do
    `update(path, confluence={"last_published_version": 5})` without
    clobbering siblings under `confluence`.
    """
    fm = read(path)
    merged = _deep_merge(fm.data, updates)
    return write(path, merged, fm.body)


def get_state(path: Path | str) -> str | None:
    return read(path).data.get("state")


# ---- Helpers ----


def _deep_merge(base: dict, overlay: dict) -> dict:
    out = dict(base)
    for k, v in overlay.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out
