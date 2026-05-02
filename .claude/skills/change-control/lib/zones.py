"""Confluence Zones — ADF capture + splice.

Authors mark regions of source markdown as Confluence-owned using a
reserved `<details>` block:

    <details>
    <summary>__CONFLUENCE_ZONE__: open-issues-jira-filter</summary>

    _Confluence-managed content — drop a Jira filter, info panel, or
    live data block here. Preserved across re-pushes._

    </details>

When pushed via markdown, that becomes an Expand macro
(ADF type `expand`) whose `attrs.title` carries the
`__CONFLUENCE_ZONE__:` marker. Reviewers replace the placeholder body
with a Jira filter / info panel / live data block. Our re-push must
preserve their additions inside zones while authoritatively replacing
everything outside.

The flow:

    1. Pre-push: extract_zones(current_adf) -> {name: adf_fragment}
    2. update_page(...) with new markdown body (which lays down the
       zone markers but with empty interior)
    3. Re-read the page as ADF
    4. splice_zones_back(new_adf, captured) -> spliced_adf
    5. update_page(...) once more with `contentFormat=adf` to land
       the spliced result

This module owns steps 1 and 4. The action-layer pipeline owns the
two update_page calls.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any


CONFLUENCE_ZONE_PREFIX = "__CONFLUENCE_ZONE__:"


@dataclass
class Zone:
    """A captured Confluence Zone — its name and its inner ADF content."""

    name: str
    title: str
    content: list[dict]

    def to_dict(self) -> dict:
        return {"name": self.name, "title": self.title, "content": self.content}


# ---- Capture ----


def extract_zones(adf: Any) -> dict[str, Zone]:
    """Walk an ADF document and return all Confluence Zones.

    Result is a dict keyed by zone name (the part of `attrs.title` that
    follows `__CONFLUENCE_ZONE__: `). Zone names are deduplicated by
    last-wins — if the same name appears twice on a page, only the
    last occurrence's content is preserved (warn at action layer).

    Accepts either a parsed dict or a JSON string.
    """
    if isinstance(adf, str):
        adf = json.loads(adf)
    if not isinstance(adf, dict):
        return {}
    found: dict[str, Zone] = {}
    _collect_zones(adf, found)
    return found


def _collect_zones(node: Any, out: dict[str, Zone]) -> None:
    if isinstance(node, dict):
        if node.get("type") in ("expand", "nestedExpand"):
            title = (node.get("attrs") or {}).get("title", "")
            if isinstance(title, str) and title.startswith(CONFLUENCE_ZONE_PREFIX):
                name = title[len(CONFLUENCE_ZONE_PREFIX):].strip()
                content = node.get("content") or []
                if isinstance(content, list):
                    out[name] = Zone(name=name, title=title, content=content)
        for v in node.values():
            _collect_zones(v, out)
    elif isinstance(node, list):
        for v in node:
            _collect_zones(v, out)


# ---- Splice ----


def splice_zones_back(adf: Any, zones: dict[str, Zone]) -> dict:
    """Return a new ADF document with Confluence Zones' interiors
    replaced by the captured fragments.

    For each `expand` node whose title is a `__CONFLUENCE_ZONE__:` marker:
      - if the zone name is in `zones`, replace the node's `content`
        with the captured fragment
      - if not, leave the node alone (new zone introduced by the new
        push; reviewer hasn't touched it yet)

    The input is not mutated; a deep-ish copy is constructed for the
    output. Accepts either a parsed dict or a JSON string.
    """
    if isinstance(adf, str):
        adf = json.loads(adf)
    if not isinstance(adf, dict):
        return {}
    return _splice_node(adf, zones)


def _splice_node(node: Any, zones: dict[str, Zone]) -> Any:
    if isinstance(node, dict):
        new: dict = {}
        node_type = node.get("type")
        title = (node.get("attrs") or {}).get("title", "")
        is_zone = (
            node_type in ("expand", "nestedExpand")
            and isinstance(title, str)
            and title.startswith(CONFLUENCE_ZONE_PREFIX)
        )
        for k, v in node.items():
            if is_zone and k == "content":
                name = title[len(CONFLUENCE_ZONE_PREFIX):].strip()
                if name in zones:
                    # Deep-copy the captured content so a later splice
                    # doesn't share state with the captured zone.
                    new[k] = json.loads(json.dumps(zones[name].content))
                else:
                    new[k] = _splice_node(v, zones)
            else:
                new[k] = _splice_node(v, zones)
        return new
    if isinstance(node, list):
        return [_splice_node(v, zones) for v in node]
    return node


# ---- Helpers ----


def zone_names(zones: dict[str, Zone]) -> list[str]:
    """Stable-sorted list of zone names (for logging)."""
    return sorted(zones.keys())


def diff_zone_sets(before: dict[str, Zone], after: dict[str, Zone]) -> dict[str, list[str]]:
    """What changed between two captures? Useful in `review-formal-status`
    output. Returns `{added, removed, kept}`."""
    a, b = set(before.keys()), set(after.keys())
    return {
        "added": sorted(b - a),
        "removed": sorted(a - b),
        "kept": sorted(a & b),
    }
