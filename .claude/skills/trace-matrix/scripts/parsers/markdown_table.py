"""Tiny GitHub-flavored markdown table parser.

Walks a markdown file line-by-line and yields each table as a list of dict
rows (header → value). Captures the H3 (`###`) heading the table sits under,
which we use as a "group" label (e.g. `G1 — Therapy Delivery`).

Zero dependencies. Good enough for the design-controls source docs in this
project, which use simple pipe tables without colspans, line wraps, or
embedded pipes.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator


@dataclass
class TableBlock:
    headers: list[str]
    rows: list[dict[str, str]]
    section: str | None = None  # nearest preceding H3 heading text
    line_no: int = 0


_PIPE_ROW = re.compile(r"^\s*\|(.+)\|\s*$")
_DIVIDER = re.compile(r"^\s*\|?\s*:?[-]{3,}:?\s*(\|\s*:?[-]{3,}:?\s*)+\|?\s*$")
_H3 = re.compile(r"^###\s+(.+?)\s*$")


def _split_row(line: str) -> list[str]:
    m = _PIPE_ROW.match(line)
    if not m:
        return []
    inner = m.group(1)
    return [c.strip() for c in inner.split("|")]


def iter_tables(text: str) -> Iterator[TableBlock]:
    lines = text.splitlines()
    section: str | None = None
    i = 0
    while i < len(lines):
        line = lines[i]
        h3 = _H3.match(line)
        if h3:
            section = h3.group(1)
            i += 1
            continue

        # Look for a header row followed by a divider row.
        if _PIPE_ROW.match(line) and i + 1 < len(lines) and _DIVIDER.match(lines[i + 1]):
            headers = _split_row(line)
            rows: list[dict[str, str]] = []
            j = i + 2
            while j < len(lines) and _PIPE_ROW.match(lines[j]) and not _DIVIDER.match(lines[j]):
                cells = _split_row(lines[j])
                if len(cells) == len(headers):
                    rows.append({h: c for h, c in zip(headers, cells)})
                j += 1
            yield TableBlock(headers=headers, rows=rows, section=section, line_no=i + 1)
            i = j
            continue
        i += 1


def parse_file(path: Path) -> list[TableBlock]:
    return list(iter_tables(path.read_text(encoding="utf-8")))
