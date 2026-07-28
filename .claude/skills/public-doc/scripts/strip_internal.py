#!/usr/bin/env python3
"""
strip_internal.py — produce public-safe markdown from a public-doc draft.

A draft carries two kinds of non-public content:
  1. A `public_doc:` metadata frontmatter block (goals, audience, campaign, ...).
  2. INTERNAL blocks — single HTML comments delimited by INTERNAL:BEGIN/END that
     hold supporting evidence and positioning rationale.

Both must be removed before the document is published. This script removes them
and then VERIFIES that no internal marker survived — internal content leaking
into a public artifact is the failure mode the whole skill exists to prevent.

Usage:
    python3 strip_internal.py INPUT.md [-o OUTPUT.md] [--keep-title] [--quiet]

If -o is omitted the cleaned markdown is written to stdout.

Exit codes:
    0  clean output produced
    2  a leak was detected after stripping (should never happen; safety net)
    3  malformed input (e.g., an unterminated INTERNAL block)
    1  usage / IO error
"""
from __future__ import annotations
import argparse
import re
import sys
from pathlib import Path

# An INTERNAL block is a single HTML comment whose body starts with INTERNAL:BEGIN
# and ends with INTERNAL:END. DOTALL so it spans lines; non-greedy so adjacent
# blocks don't merge.
INTERNAL_BLOCK = re.compile(
    r"<!--\s*INTERNAL:BEGIN\b.*?INTERNAL:END\s*-->",
    re.DOTALL,
)

# Any residual marker that means a strip was incomplete or a block was malformed.
LEAK_MARKERS = [
    re.compile(r"INTERNAL:BEGIN\b"),
    re.compile(r"INTERNAL:END\b"),
]

# A YAML frontmatter block that contains a `public_doc:` mapping at the top of file.
FRONTMATTER = re.compile(r"\A---\n(?P<body>.*?)\n---\n?", re.DOTALL)


def strip_frontmatter(md: str, keep_title: bool) -> tuple[str, str | None]:
    """Remove a leading `public_doc:` frontmatter block.

    Returns (markdown_without_frontmatter, title_or_None). The title is pulled
    so the renderer can pass it to pandoc even though the metadata is dropped.
    Frontmatter that is NOT a public_doc block is left untouched (the doc may use
    frontmatter for another purpose).
    """
    m = FRONTMATTER.match(md)
    if not m or "public_doc:" not in m.group("body"):
        return md, None

    title = None
    tm = re.search(r"^\s*title:\s*(.+?)\s*$", m.group("body"), re.MULTILINE)
    if tm:
        title = tm.group(1).strip().strip("'\"")

    rest = md[m.end():]
    if keep_title and title:
        rest = f"# {title}\n\n{rest.lstrip()}"
    return rest, title


def strip_internal_blocks(md: str) -> str:
    return INTERNAL_BLOCK.sub("", md)


def collapse_blank_runs(md: str) -> str:
    """Stripping a block often leaves 3+ blank lines; collapse to at most 2."""
    md = re.sub(r"\n{3,}", "\n\n", md)
    return md.strip() + "\n"


def detect_leaks(md: str) -> list[str]:
    leaks = []
    for pat in LEAK_MARKERS:
        for mo in pat.finditer(md):
            line = md.count("\n", 0, mo.start()) + 1
            leaks.append(f"line {line}: residual marker {mo.group(0)!r}")
    return leaks


def check_unterminated(original: str) -> list[str]:
    """A BEGIN with no matching END is a malformed block — catch it before strip
    silently keeps the content."""
    begins = len(re.findall(r"INTERNAL:BEGIN\b", original))
    ends = len(re.findall(r"INTERNAL:END\b", original))
    problems = []
    if begins != ends:
        problems.append(
            f"unbalanced INTERNAL markers: {begins} BEGIN vs {ends} END "
            "(every block must be a single comment: '<!-- INTERNAL:BEGIN ... INTERNAL:END -->')"
        )
    return problems


def strip(md: str, keep_title: bool = False) -> tuple[str, str | None]:
    problems = check_unterminated(md)
    if problems:
        raise ValueError("; ".join(problems))
    md, title = strip_frontmatter(md, keep_title)
    md = strip_internal_blocks(md)
    md = collapse_blank_runs(md)
    leaks = detect_leaks(md)
    if leaks:
        raise RuntimeError("LEAK after strip:\n  " + "\n  ".join(leaks))
    return md, title


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input", type=Path)
    ap.add_argument("-o", "--output", type=Path)
    ap.add_argument("--keep-title", action="store_true",
                    help="emit the metadata title as an H1 at the top of the output")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    if not args.input.exists():
        print(f"error: input not found: {args.input}", file=sys.stderr)
        return 1

    md = args.input.read_text()
    try:
        cleaned, title = strip(md, keep_title=args.keep_title)
    except ValueError as e:           # malformed input
        print(f"error: {e}", file=sys.stderr)
        return 3
    except RuntimeError as e:         # leak safety net
        print(f"error: {e}", file=sys.stderr)
        return 2

    if args.output:
        args.output.write_text(cleaned)
        if not args.quiet:
            n_blocks = len(INTERNAL_BLOCK.findall(md))
            print(f"[strip] {args.input} -> {args.output} "
                  f"({n_blocks} INTERNAL block(s) removed, "
                  f"title={title!r})", file=sys.stderr)
    else:
        sys.stdout.write(cleaned)
    return 0


if __name__ == "__main__":
    sys.exit(main())
