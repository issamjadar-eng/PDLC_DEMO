#!/usr/bin/env python3
"""Migrate strategy docs to the v15 decision-block format.

Walks each H3 in `docs/project/strategies/<domain>-strategy.md`, allocates
a stable decision ID (`D-<DOMAIN>-<SECTION>.<INDEX>`), wraps the H3 + body
in `<!-- DECISION:start ... -->` / `<!-- DECISION:end ... -->` sentinels,
and infers `source=` + `created=` from the existing `<!-- Source: ... -->`
comment that the assembler always emits per subsection.

Idempotent — re-running on an already-migrated doc skips already-wrapped
H3s. Reversible — pass `--reverse` to strip sentinels back out.

Usage:
    migrate_decisions.py [--all] [--domain regulatory] [--reverse]
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

DOMAIN_PREFIXES = {
    "regulatory": "REG",
    "commercial": "COMM",
    "architecture": "ARCH",
    "development": "DEV",
    "testing": "TEST",
    "risk": "RISK",
    "postmarket": "POSTM",
    "operations": "OPS",
}

# Sections that are NOT decision content — skip when allocating IDs.
# These are the structural / reference sections at the top + bottom of every
# assembled strategy doc.
META_H2_HEADINGS = {
    "plans informed",
    "plans this informs",
    "what belongs here",
    "how to contribute",
    "open items",
    "source traceability",
    "history",
    "assembly history",
}

_H2_RE = re.compile(r"^##\s+(.+?)\s*$")
_H3_RE = re.compile(r"^###\s+(.+?)\s*$")
_SECTION_NUM_RE = re.compile(r"^\s*(\d+)\.")
_SOURCE_COMMENT_RE = re.compile(
    r"<!--\s*Source:\s*"
    # Accept either v14+ canonical `<folder>/NNN` (e.g. ben/032) OR
    # legacy `task NNN` form. Resolve to canonical post-match.
    r"(?P<source>(?:task\s+\d+|[\w./-]+)),"
    r'\s*"(?P<heading>[^"]+)",'
    r"\s*last\s+modified\s+(?P<date>\d{4}-\d{2}-\d{2})\s*-->",
    re.IGNORECASE,
)


def _canonicalize_source(repo_root: Path, source_raw: str) -> str:
    """Convert legacy `task 032` / bare `032` to canonical `<folder>/032`
    by globbing `tasks/*/<NNN>-*.md`. Returns the input unchanged if it's
    already in canonical form or if resolution is ambiguous."""
    s = source_raw.strip()
    if "/" in s:
        return s
    m = re.match(r"task\s+(\d{2,4})$", s, re.IGNORECASE)
    num = m.group(1) if m else (s if s.isdigit() else None)
    if num is None:
        return s
    cands = sorted((repo_root / "tasks").glob(f"*/{num}-*.md"))
    if len(cands) == 1:
        return f"{cands[0].parent.name}/{num}"
    return s
_DECISION_START_RE = re.compile(r"^<!--\s+DECISION:start\b")
_DECISION_END_RE = re.compile(r"^<!--\s+DECISION:end\b")
_NUMBERED_H3_RE = re.compile(r"^###\s+(\d+\.\d+)\s+(.*)$")


def domain_prefix(domain: str) -> str:
    return DOMAIN_PREFIXES.get(domain.lower()) or domain.upper()[:4]


def is_meta_h2(heading: str) -> bool:
    h = heading.strip().lower()
    if h in META_H2_HEADINGS:
        return True
    # Also ignore "X. Foo" where Foo lower-case matches a meta heading.
    m = _SECTION_NUM_RE.match(heading)
    if m:
        rest = heading[m.end():].strip().lower()
        if rest in META_H2_HEADINGS:
            return True
    return False


def section_index(heading: str, fallback: int) -> int:
    m = _SECTION_NUM_RE.match(heading)
    if m:
        return int(m.group(1))
    return fallback


def migrate(path: Path, domain: str, repo_root: Path | None = None) -> dict:
    """Migrate a strategy doc in place. Returns a stats dict."""
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    n = len(lines)
    out: list[str] = []
    prefix = domain_prefix(domain)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    current_section: str | None = None
    current_section_idx: int | None = None
    decisions_in_section = 0
    seq_section_idx = 0  # for H2s without a leading number
    inside_decision_block = False
    inside_blockquote = False
    skipped = 0
    wrapped = 0

    i = 0
    while i < n:
        line = lines[i]
        stripped = line.strip()

        # Track whether we're inside a `> **Proposed change**` blockquote
        # (don't try to wrap H3s inside those — they aren't real decisions).
        if stripped.startswith(">"):
            inside_blockquote = True
        elif stripped == "":
            inside_blockquote = False
        else:
            inside_blockquote = inside_blockquote and stripped.startswith(">")

        # Track existing DECISION sentinels — skip wrapped regions.
        if _DECISION_START_RE.match(line):
            inside_decision_block = True
            out.append(line)
            i += 1
            continue
        if _DECISION_END_RE.match(line):
            inside_decision_block = False
            out.append(line)
            i += 1
            continue
        if inside_decision_block:
            out.append(line)
            i += 1
            continue

        # H2 → reset section + decision counter.
        m_h2 = _H2_RE.match(line)
        if m_h2 and not _H3_RE.match(line):
            heading = m_h2.group(1).strip()
            seq_section_idx += 1
            if is_meta_h2(heading):
                current_section = None
                current_section_idx = None
            else:
                current_section = heading
                current_section_idx = section_index(heading, seq_section_idx)
                decisions_in_section = 0
            out.append(line)
            i += 1
            continue

        # H3 → start of a decision block (only if inside a content H2).
        m_h3 = _H3_RE.match(line)
        if m_h3 and current_section_idx is not None and not inside_blockquote:
            decisions_in_section += 1
            heading = m_h3.group(1).strip()
            decision_id = f"D-{prefix}-{current_section_idx}.{decisions_in_section}"
            # Walk forward to find the end of the decision body — next H2/H3
            # or EOF. Capture the source comment if present.
            body_start = i
            body_end = n
            for j in range(i + 1, n):
                if _H2_RE.match(lines[j]) and not _H3_RE.match(lines[j]):
                    body_end = j
                    break
                if _H3_RE.match(lines[j]):
                    body_end = j
                    break
            block_text = "\n".join(lines[body_start:body_end])
            src_match = _SOURCE_COMMENT_RE.search(block_text)
            source_raw = src_match.group("source") if src_match else ""
            source = (
                _canonicalize_source(repo_root, source_raw)
                if source_raw and repo_root else source_raw
            )
            created = src_match.group("date") if src_match else today

            meta_parts = [f"id={decision_id}", "status=active"]
            if source:
                meta_parts.append(f"source={source}")
            meta_parts.append(f"created={created}")
            start_marker = f"<!-- DECISION:start {' '.join(meta_parts)} -->"
            end_marker = f"<!-- DECISION:end id={decision_id} -->"

            # Prepend numeric prefix `<sec>.<idx>` to the H3 heading line so
            # readers see decision boundaries clearly. Skip if already prefixed.
            num_prefix = f"{current_section_idx}.{decisions_in_section}"
            block_lines = list(lines[body_start:body_end])
            if block_lines and block_lines[0].startswith("### "):
                head_text = block_lines[0][4:]
                if not _NUMBERED_H3_RE.match(block_lines[0]):
                    block_lines[0] = f"### {num_prefix} {head_text}"
            out.append(start_marker)
            for ln in block_lines:
                out.append(ln)
            # Trim trailing blank lines from the block before closing.
            while out and out[-1].strip() == "":
                out.pop()
            out.append(end_marker)
            out.append("")  # one blank line after end-marker for readability
            wrapped += 1
            i = body_end
            continue

        out.append(line)
        i += 1

    new_text = "\n".join(out)
    if not new_text.endswith("\n"):
        new_text += "\n"
    if new_text != text:
        path.write_text(new_text, encoding="utf-8")
    return {"path": str(path), "wrapped": wrapped, "skipped": skipped, "domain": domain}


def reverse(path: Path) -> dict:
    """Strip DECISION sentinels back out, and remove the `<sec>.<idx> `
    numeric prefix from H3 headings that were inside decision blocks.
    Idempotent."""
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    out: list[str] = []
    removed = 0
    inside_block = False
    for line in lines:
        if _DECISION_START_RE.match(line):
            inside_block = True
            removed += 1
            continue
        if _DECISION_END_RE.match(line):
            inside_block = False
            removed += 1
            continue
        if inside_block:
            m = _NUMBERED_H3_RE.match(line)
            if m:
                line = f"### {m.group(2)}"
        out.append(line)
    new_text = "\n".join(out)
    if not new_text.endswith("\n"):
        new_text += "\n"
    if new_text != text:
        path.write_text(new_text, encoding="utf-8")
    return {"path": str(path), "removed": removed}


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true", help="migrate every *-strategy.md")
    ap.add_argument("--domain", help="single domain key (e.g. regulatory)")
    ap.add_argument("--reverse", action="store_true", help="strip sentinels (de-migrate)")
    ap.add_argument(
        "--repo-root",
        default=".",
        help="project root containing docs/project/strategies/",
    )
    args = ap.parse_args(argv)
    repo = Path(args.repo_root).resolve()
    strat_dir = repo / "docs" / "project" / "strategies"
    if not strat_dir.is_dir():
        print(f"error: {strat_dir} not found", file=sys.stderr)
        return 1
    targets: list[Path] = []
    if args.all:
        targets = sorted(strat_dir.glob("*-strategy.md"))
    elif args.domain:
        p = strat_dir / f"{args.domain}-strategy.md"
        if not p.is_file():
            print(f"error: {p} not found", file=sys.stderr)
            return 1
        targets = [p]
    else:
        ap.error("specify --all or --domain")
        return 2
    for p in targets:
        domain = p.name.removesuffix("-strategy.md")
        if args.reverse:
            r = reverse(p)
            print(f"  ↺  {r['path']}: removed {r['removed']} sentinel line(s)")
        else:
            r = migrate(p, domain, repo_root=repo)
            print(f"  ✓  {r['path']}: wrapped {r['wrapped']} decision(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
