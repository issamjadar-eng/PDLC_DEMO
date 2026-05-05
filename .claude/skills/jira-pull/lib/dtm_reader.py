"""
Read a DTM xlsx using the schema map declared in project.yml
`dhfs[].evidence.design_traceability_matrix[].columns` and produce a
normalized DtmState consumed by the drift-rule registry.

Project-agnostic: knows nothing about specific column headers, prefix
conventions, or DTM provenance. Everything comes through `DtmSchema`
(from `lib.config`).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Pattern

from openpyxl import load_workbook
from openpyxl.utils import column_index_from_string

from .config import DtmSchema


@dataclass(frozen=True)
class DtmRow:
    """One normalized DTM data row.

    Raw cell values keyed by canonical column name (from schema.columns).
    Extracted IDs (DI/UN/Hazard prefixes) populated when an extractor matches.
    """
    row_index: int                         # 1-based xlsx row number for traceability
    cells: Dict[str, Optional[str]]        # canonical_name -> raw cell text (None if blank)
    extracted: Dict[str, Optional[str]]    # extractor_name -> first match (None if no match)
    is_blank: bool                         # all cells empty / sentinel-only


@dataclass(frozen=True)
class DtmState:
    schema: DtmSchema
    rows: List[DtmRow]
    sheet_name: str
    source_path: str

    # Convenience indices
    by_design_input: Dict[str, List[DtmRow]] = field(default_factory=dict)
    by_user_need: Dict[str, List[DtmRow]] = field(default_factory=dict)
    by_hazard: Dict[str, List[DtmRow]] = field(default_factory=dict)


_BLANK_SENTINELS = ("", "TBD", "N/A", "NA")


def _is_blank(value: Optional[str], schema: DtmSchema) -> bool:
    if value is None:
        return True
    s = str(value).strip()
    if s == "":
        return True
    if s == schema.tbd_value:
        return True
    return False


def _cell_text(value) -> Optional[str]:
    if value is None:
        return None
    s = str(value).strip()
    return s if s else None


def _compile_extractors(schema: DtmSchema) -> Dict[str, Pattern[str]]:
    return {name: re.compile(pat) for name, pat in (schema.extractors or {}).items()}


def _normalize_id(raw: str) -> str:
    """Collapse internal whitespace + hyphens so 'PHA 5', 'PHA-5', 'PHA 5'
    all canonicalize to a single form. Letter prefix stays as-is; digit
    suffix preserved. We pick 'PHA5' (no separator) as canonical."""
    return re.sub(r"[\s-]+", "", raw.strip())


def _extract_first(text: Optional[str], pattern: Pattern[str]) -> Optional[str]:
    if text is None:
        return None
    m = pattern.search(text)
    if not m:
        return None
    raw = m.group(1) if m.lastindex else m.group(0)
    return _normalize_id(raw)


def _extract_all_hazards(text: Optional[str], pattern: Pattern[str]) -> List[str]:
    """Hazard refs may be comma-separated (e.g. 'PHA 11, PHA 5, PHA 30').
    Returns canonical-normalized IDs (stripped of internal whitespace/hyphens)."""
    if text is None:
        return []
    return [
        _normalize_id(m.group(1) if m.lastindex else m.group(0))
        for m in pattern.finditer(text)
    ]


def read(schema: DtmSchema, project_root: Path) -> DtmState:
    """Read the DTM xlsx into a DtmState. Path is resolved relative to project_root."""
    xlsx_path = (project_root / schema.xlsx_path).resolve()
    wb = load_workbook(xlsx_path, data_only=True, read_only=True)
    if schema.sheet not in wb.sheetnames:
        raise KeyError(
            f"DTM sheet {schema.sheet!r} not in {xlsx_path.name}; sheets: {wb.sheetnames}"
        )
    ws = wb[schema.sheet]

    column_indices = {name: column_index_from_string(letter)
                      for name, letter in schema.columns.items()}

    extractor_patterns = _compile_extractors(schema)

    rows: List[DtmRow] = []
    by_di: Dict[str, List[DtmRow]] = {}
    by_un: Dict[str, List[DtmRow]] = {}
    by_haz: Dict[str, List[DtmRow]] = {}

    # read_only=True iterates lazily; iter_rows lets us seek to data start.
    for excel_row_num, raw_row in enumerate(
        ws.iter_rows(min_row=schema.data_start_row, values_only=True),
        start=schema.data_start_row,
    ):
        cells: Dict[str, Optional[str]] = {}
        for col_name, col_idx in column_indices.items():
            value = raw_row[col_idx - 1] if col_idx - 1 < len(raw_row) else None
            cells[col_name] = _cell_text(value)

        # Treat row as blank if EVERY canonical column is blank-or-sentinel.
        is_blank = all(_is_blank(cells[name], schema) for name in column_indices)
        if is_blank:
            # Skip trailing blank rows but don't break — some DTMs have padded rows.
            continue

        extracted: Dict[str, Optional[str]] = {}
        for name, pat in extractor_patterns.items():
            # Decide which column the extractor reads from based on extractor name
            # convention: design_input_id <- columns.design_input, etc.
            source_col = name.replace("_id", "")
            source_text = cells.get(source_col)
            extracted[name] = _extract_first(source_text, pat)

        row = DtmRow(
            row_index=excel_row_num,
            cells=cells,
            extracted=extracted,
            is_blank=False,
        )
        rows.append(row)

        # Index for fast rule-evaluation lookups
        if di_id := extracted.get("design_input_id"):
            by_di.setdefault(di_id, []).append(row)
        if un_id := extracted.get("user_need_id"):
            by_un.setdefault(un_id, []).append(row)
        # Hazard column may carry multiple PHA refs — re-extract all
        if "hazard_id" in extractor_patterns:
            for h in _extract_all_hazards(cells.get("hazard_refs"),
                                          extractor_patterns["hazard_id"]):
                by_haz.setdefault(h.strip(), []).append(row)

    wb.close()

    return DtmState(
        schema=schema,
        rows=rows,
        sheet_name=schema.sheet,
        source_path=str(xlsx_path),
        by_design_input=by_di,
        by_user_need=by_un,
        by_hazard=by_haz,
    )
