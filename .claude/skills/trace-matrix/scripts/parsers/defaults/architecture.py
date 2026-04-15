"""Default Architecture parser.

Assumes a System Architecture Description (SAD) with a pipe table that has
a `Module` column and an identifier column (`#` or similar). The module ID
regex is derived from the configured `id_prefix` so a project whose modules
are named `SR-01` / `SR-02` or `CM1 / CM2` works by config alone.

The SAD is expected to describe modules in prose. Module ↔ DI trace edges
are only extracted if the table has a `Traces to DI` column — which most
SADs don't carry in v1. When absent, the layer reports `edges_known=False`
so the console can render the "module ↔ DI mapping not yet captured"
banner.

If your SAD diverges (different column names, nested structure, module
IDs embedded in prose), run `/trace-matrix init` to generate a project
adapter.
"""
from __future__ import annotations

import re
from pathlib import Path

from adapter_api import ParserResult
from parsers.markdown_table import parse_file


def _summarize(text: str, max_chars: int = 90) -> str:
    text = text.strip()
    if len(text) <= max_chars:
        return text
    cut = text[:max_chars].rsplit(" ", 1)[0]
    return cut + "…"


def _strip_md(s: str) -> str:
    return s.replace("**", "").replace("*", "").strip()


def _split_ids(s: str) -> list[str]:
    return [tok.strip() for tok in re.split(r"[,;]", s) if tok.strip()]


def parse(path: Path, layer_cfg: dict) -> ParserResult:
    id_prefix = layer_cfg.get("id_prefix", "M")
    cols = layer_cfg.get("columns", {})
    id_col = cols.get("id", "#")
    name_col = cols.get("name", "Module")
    traces_col = cols.get("traces_up", "Traces to DI")

    # Build an ID regex from the configured prefix.
    # Accepts both "M1" (bare digits) and "SR-01" (dash + word-char tail).
    module_id_re = re.compile(
        rf"^({re.escape(id_prefix)}[-_]?\w+)\b"
    )

    if not path or not path.exists():
        return ParserResult(warnings=[f"source missing: {path}"])

    edges_known = False
    nodes: list[dict] = []
    warnings: list[str] = []

    for table in parse_file(path):
        if name_col not in table.headers or id_col not in table.headers:
            continue
        for row in table.rows:
            ident = _strip_md(row.get(id_col, ""))
            if not module_id_re.match(ident):
                continue
            module_name = _strip_md(row.get(name_col, ""))
            summary = _strip_md(row.get("Summary", ""))
            traces: list[str] = []
            if traces_col in table.headers:
                traces = _split_ids(row.get(traces_col, ""))
                if traces:
                    edges_known = True

            nodes.append(
                {
                    "id": ident,
                    "summary": _summarize(module_name + " — " + summary if summary else module_name),
                    "full_text": summary,
                    "module_name": module_name,
                    "category": _strip_md(row.get("Type", "")) or None,
                    "criticality": _strip_md(row.get("Criticality tags", "")) or None,
                    "iec_class": _strip_md(row.get("IEC 62304 Class", "")) or None,
                    "group": None,
                    "group_label": None,
                    "traces_forward_ids": traces,
                }
            )
        if nodes:
            break  # first module table wins

    return ParserResult(
        nodes=nodes,
        warnings=warnings,
        extras={"edges_known": edges_known},
    )
