"""Default Risk parser.

Looks for a pipe table with a `Hazard ID` column. If the source file is a
medtech-docs `awaiting-content` strategy placeholder, returns an empty
result with a warning. Risk data will often live in a separate FMEA or
hazard-trace doc — projects whose layout differs should generate an adapter
via `/trace-matrix init`.
"""
from __future__ import annotations

from pathlib import Path

from adapter_api import ParserResult
from parsers.markdown_table import parse_file


def parse(path: Path, layer_cfg: dict) -> ParserResult:
    id_prefix = layer_cfg.get("id_prefix", "HZ")
    cols = layer_cfg.get("columns", {})
    id_col = cols.get("id", "Hazard ID")
    hazard_col = cols.get("hazard", "Hazard")
    situation_col = cols.get("situation", "Hazardous Situation")

    if not path or not path.exists():
        return ParserResult(warnings=["source missing"])

    text = path.read_text(encoding="utf-8")
    if "<!-- Status: awaiting-content -->" in text:
        return ParserResult(warnings=["source is awaiting-content placeholder"])

    nodes: list[dict] = []
    for table in parse_file(path):
        if id_col not in table.headers:
            continue
        for row in table.rows:
            hid = row.get(id_col, "").strip()
            if not hid.startswith(id_prefix + "-"):
                continue
            nodes.append(
                {
                    "id": hid,
                    "summary": row.get(hazard_col, "").strip(),
                    "full_text": row.get(situation_col, "").strip(),
                    "criticality": None,
                    "category": None,
                    "group": None,
                    "group_label": None,
                    "traces_forward_ids": [],
                }
            )

    warnings = [] if nodes else ["no hazards matched the configured prefix"]
    return ParserResult(nodes=nodes, warnings=warnings)
