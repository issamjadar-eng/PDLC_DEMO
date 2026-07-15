"""Project risk adapter.

Generated per `/trace-matrix init` step 4 (adapter authoring for a layer the
default parser cannot serve) under task ben/102 on 2026-07-14, after Read of
the risk source doc:

  - docs/project/dhfs/pca-device/risk-management/GL-TMP-RM-003-hazard-analysis.md

The doc instantiates QMS FORM GL-TMP-RM-003 (Hazard Analysis Worksheet),
whose table shape differs from the shipped default risk parser in three ways:

  - the ID column is `HAZ ID` (default expects `Hazard ID`) and the ID
    prefix is `HAZ` per the FORM's exemplar row (default `HZ`)
  - the hazard-description column is `Hazard (ISO 14971 Annex C class)`
  - the FORM carries a `Design Input(s)` column of comma-separated DI IDs —
    the default parser never populates `traces_forward_ids`, so risk items
    would parse but build zero edges to design inputs

This adapter parses the FORM columns and authors `traces_forward_ids` from
the `Design Input(s)` cell. Risk is a parallel overlay in graph.py — each
claim builds a `design_inputs_to_risk` edge (DI upstream, HAZ downstream),
which is what the console's Trace Matrix section renders as risk↔DI mapping.

Severity/probability/region cells are carried into `full_text` so the
console's expandable row shows the scoring without a second fetch. The
`Verification(s)` column is deliberately NOT parsed into edges: its VER
identifiers name planned protocols that are not all nodes in the DI-derived
V&V layer, and claiming them would pollute the gap report with broken refs.

Shared across any DHF whose risk source instantiates GL-TMP-RM-003.
"""
from __future__ import annotations

import re
from pathlib import Path

from adapter_api import ParserResult
from parsers.markdown_table import parse_file


_DI_RE = re.compile(r"\bDI-\d+\b")


def _summarize(text: str, max_chars: int = 90) -> str:
    text = text.strip()
    if len(text) <= max_chars:
        return text
    cut = text[:max_chars].rsplit(" ", 1)[0]
    return cut + "…"


def parse(path: Path, layer_cfg: dict) -> ParserResult:
    id_prefix = layer_cfg.get("id_prefix", "HAZ")
    cols = layer_cfg.get("columns", {})
    id_col = cols.get("id", "HAZ ID")
    hazard_col = cols.get("hazard", "Hazard (ISO 14971 Annex C class)")
    situation_col = cols.get("situation", "Hazardous Situation")
    harm_col = cols.get("harm", "Harm")
    traces_col = cols.get("traces_up", "Design Input(s)")
    controls_col = cols.get("controls", "Controls (design / protective / info)")
    residual_col = cols.get("residual", "Residual Risk")
    s_pre_col = cols.get("s_pre", "S (pre)")
    p_pre_col = cols.get("p_pre", "P (pre)")
    risk_pre_col = cols.get("risk_pre", "Risk (pre)")

    if not path or not path.exists():
        return ParserResult(warnings=[f"source missing: {path}"])

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
            hazard = row.get(hazard_col, "").strip()
            situation = row.get(situation_col, "").strip()
            harm = row.get(harm_col, "").strip()
            controls = row.get(controls_col, "").strip()
            residual = row.get(residual_col, "").strip()
            pre = " / ".join(
                p
                for p in (
                    row.get(s_pre_col, "").strip(),
                    row.get(p_pre_col, "").strip(),
                    row.get(risk_pre_col, "").strip(),
                )
                if p
            )
            di_ids = _DI_RE.findall(row.get(traces_col, ""))

            full_parts = [p for p in (situation, f"Harm: {harm}" if harm else "") if p]
            if pre:
                full_parts.append(f"Pre-control S/P/Risk: {pre}")
            if controls:
                full_parts.append(f"Controls: {controls}")
            if residual:
                full_parts.append(f"Residual risk: {residual}")

            nodes.append(
                {
                    "id": hid,
                    "summary": _summarize(hazard),
                    "full_text": " — ".join(full_parts) if full_parts else hazard,
                    "criticality": residual or None,
                    "category": None,
                    "group": None,
                    "group_label": None,
                    "traces_forward_ids": list(di_ids),
                }
            )

    warnings = [] if nodes else ["no hazards matched the configured prefix"]
    return ParserResult(nodes=nodes, warnings=warnings)
