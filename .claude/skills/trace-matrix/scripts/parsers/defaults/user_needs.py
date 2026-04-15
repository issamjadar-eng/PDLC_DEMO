"""Default User Needs parser.

Assumes a medtech-docs-convention `user-needs.md` with H3 group headings
(`### G1 — …`) and pipe tables containing at minimum a `UN ID` column and
a `User Need` column. Additional columns (`Category`, `Stakeholder`, `Source`,
`Priority`) are extracted when present.

If your source doc diverges from this shape, run `/trace-matrix init` to
generate a project-side adapter at
`tools/project-console/trace-matrix/adapters/user_needs.py`.
"""
from __future__ import annotations

import re
from pathlib import Path

from adapter_api import ParserResult
from parsers.markdown_table import parse_file


_GROUP_RE = re.compile(r"^(G\d+)\b")


def _summarize(text: str, max_chars: int = 90) -> str:
    text = text.strip()
    if len(text) <= max_chars:
        return text
    cut = text[:max_chars].rsplit(" ", 1)[0]
    return cut + "…"


def parse(path: Path, layer_cfg: dict) -> ParserResult:
    id_prefix = layer_cfg.get("id_prefix", "UN")
    id_col = layer_cfg.get("columns", {}).get("id", f"{id_prefix} ID")
    text_col = layer_cfg.get("columns", {}).get("text", "User Need")

    if not path or not path.exists():
        return ParserResult(warnings=[f"source missing: {path}"])

    nodes: list[dict] = []
    warnings: list[str] = []

    for table in parse_file(path):
        if id_col not in table.headers:
            continue
        group_label = table.section or ""
        group_match = _GROUP_RE.match(group_label)
        group = group_match.group(1) if group_match else None

        for row in table.rows:
            uid = row.get(id_col, "").strip()
            if not uid.startswith(id_prefix + "-"):
                continue
            full_text = row.get(text_col, "").strip()
            nodes.append(
                {
                    "id": uid,
                    "summary": _summarize(full_text),
                    "full_text": full_text,
                    "category": row.get("Category", "").strip() or None,
                    "criticality": None,
                    "group": group,
                    "group_label": group_label or None,
                    "stakeholder": row.get("Stakeholder", "").strip() or None,
                    "priority": row.get("Priority", "").strip() or None,
                    "source_ref": row.get("Source", "").strip() or None,
                    "traces_forward_ids": [],
                }
            )

    return ParserResult(nodes=nodes, warnings=warnings)
