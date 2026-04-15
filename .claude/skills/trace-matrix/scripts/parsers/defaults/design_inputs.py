"""Default Design Inputs parser.

Assumes a medtech-docs-convention `design-inputs.md` with pipe tables that
carry at minimum a `DI ID` column, a `Requirement Statement` column, a
`Traces to UN` column (comma-separated upstream UN IDs), and a
`Verification Method` column (free text, often containing a `VER-XYZ-nnn`
style identifier in parentheses).

The V&V layer is derived from the `Verification Method` column — any
`VER-*` identifiers found become V&V nodes on the V&V layer, and are
returned under `extras["vnv_nodes"]`. The build orchestrator picks them up
when building the V&V layer for that DHF.

If your source doc diverges from this shape, run `/trace-matrix init` to
generate a project-side adapter.
"""
from __future__ import annotations

import re
from pathlib import Path

from adapter_api import ParserResult
from parsers.markdown_table import parse_file


_GROUP_RE = re.compile(r"^(G\d+)\b")
_DEFAULT_VER_RE = re.compile(r"\b(VER-[A-Z0-9][A-Z0-9-]+)\b")
_CRIT_NORMALIZE = {
    "CTS": "CtS",
    "CTF": "CtF",
    "CTC": "CtC",
    "CTP": "CtP",
    "S": "Supporting",
}


def _summarize(text: str, max_chars: int = 90) -> str:
    text = text.strip()
    if len(text) <= max_chars:
        return text
    cut = text[:max_chars].rsplit(" ", 1)[0]
    return cut + "…"


def _strip_md_emphasis(s: str) -> str:
    return s.replace("**", "").replace("*", "").strip()


def _split_ids(s: str) -> list[str]:
    return [tok.strip() for tok in re.split(r"[,;]", s) if tok.strip()]


def parse(path: Path, layer_cfg: dict) -> ParserResult:
    id_prefix = layer_cfg.get("id_prefix", "DI")
    cols = layer_cfg.get("columns", {})
    id_col = cols.get("id", f"{id_prefix} ID")
    stmt_col = cols.get("statement", "Requirement Statement")
    traces_col = cols.get("traces_up", "Traces to UN")
    verif_col = cols.get("verification", "Verification Method")
    crit_col = cols.get("criticality", "Criticality")
    accept_col = cols.get("acceptance", "Acceptance Criteria")

    ver_pattern = layer_cfg.get("ver_id_pattern")
    ver_re = re.compile(ver_pattern) if ver_pattern else _DEFAULT_VER_RE

    if not path or not path.exists():
        return ParserResult(warnings=[f"source missing: {path}"])

    nodes: list[dict] = []
    vnv_seen: dict[str, dict] = {}
    warnings: list[str] = []

    for table in parse_file(path):
        if id_col not in table.headers:
            continue
        group_label = table.section or ""
        group_match = _GROUP_RE.match(group_label)
        group = group_match.group(1) if group_match else None

        for row in table.rows:
            did = row.get(id_col, "").strip()
            if not did.startswith(id_prefix + "-"):
                continue
            statement = row.get(stmt_col, "").strip()
            traces_un = _split_ids(row.get(traces_col, ""))
            ver_text = row.get(verif_col, "")
            ver_ids = ver_re.findall(ver_text)

            crit_raw = _strip_md_emphasis(row.get(crit_col, ""))
            crit = _CRIT_NORMALIZE.get(crit_raw.upper()) if crit_raw else None

            nodes.append(
                {
                    "id": did,
                    "summary": _summarize(statement),
                    "full_text": statement,
                    "category": row.get("Category", "").strip() or None,
                    "criticality": crit,
                    "group": group,
                    "group_label": group_label or None,
                    "acceptance_criteria": row.get(accept_col, "").strip() or None,
                    "verification_method": ver_text.strip() or None,
                    "traces_forward_ids": list(traces_un),
                    "verification_ids": list(ver_ids),
                    "has_verification_id": bool(ver_ids),
                }
            )

            for vid in ver_ids:
                if vid not in vnv_seen:
                    summary = re.sub(r"\(.*?\)", "", ver_text).strip().rstrip(";.,")
                    vnv_seen[vid] = {
                        "id": vid,
                        "summary": _summarize(summary or vid),
                        "full_text": ver_text.strip(),
                        "category": None,
                        "criticality": None,
                        "group": group,
                        "group_label": group_label or None,
                        "source_ref": f"derived from {did}",
                        "verifies_di_ids": [did],
                        "traces_forward_ids": [],
                    }
                else:
                    vnv_seen[vid]["verifies_di_ids"].append(did)

    return ParserResult(
        nodes=nodes,
        warnings=warnings,
        extras={"vnv_nodes": list(vnv_seen.values())},
    )
