#!/usr/bin/env python3
"""md-deck — layout-risk linter for cached creative slides.

Static analysis pass over `assets/<slug>/.creative-cache/*.html`. Surfaces
recurring layout-risk patterns observed in the v0.6 cache audit (ben/167):

  A. edge-bleed         absolute children with `inset: 0` and zero/tiny
                        padding around their text content
  B. half-empty grid    `grid-template-rows` reserving slots the source
                        likely cannot fill (heuristic — flagged when a grid
                        has 3+ rows but the slide has low body density)
  C. risky overlap      `position: absolute` without all four `inset` sides
                        set, when the element appears to carry text
                        (suggests under-constrained geometry that may drift
                        onto adjacent prose)
  D. tiny body text     `font-size` below `0.7rem` or `< 12px` outside
                        explicit micro-label contexts

Output: per-file warnings + a build summary. **Warnings, not errors** —
agents have agency to break rules with intent. The lint exists so a designer
can quickly find candidates for `--re-roll-creative <slug>`.

Usage:
  python3 lint-creative.py <deck-output-dir>      # default human report
  python3 lint-creative.py <deck-output-dir> --json
  python3 lint-creative.py <deck-output-dir> --quiet  (only summary)
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# ----------------------------------------------------------------------
# Heuristics
# ----------------------------------------------------------------------

# A — edge-bleed: absolute fill with no inner gutter
_RE_INSET_FILL = re.compile(r"position:\s*absolute[^>\"]*?inset:\s*0", re.I)
_RE_PADDING_ZERO = re.compile(r"padding:\s*0(?![\.\d])")
_RE_TINY_PADDING = re.compile(r"padding:\s*0?\.[12]\d?rem")

# B — half-empty grid: many reserved rows or columns
_RE_GRID_ROWS_3PLUS = re.compile(r"grid-template-rows:\s*([^;\"]+)")
_RE_GRID_COLS_3PLUS = re.compile(r"grid-template-columns:\s*([^;\"]+)")

# C — risky overlap: absolute without all 4 anchors
_RE_POS_ABS = re.compile(r"position:\s*absolute")
_RE_INSET_FULL = re.compile(r"inset:\s*\S")  # any inset shorthand counts
_RE_FOUR_ANCHORS = re.compile(r"top:[^;]+;.*?(?:right|left|bottom):", re.S)

# D — tiny font for body
_RE_TINY_FONT_REM = re.compile(r"font-size:\s*0\.[1-6]\d?rem")
_RE_TINY_FONT_PX = re.compile(r"font-size:\s*([6-9]|1[01])px(?!\.)")


def _count_grid_tracks(track_value: str) -> int:
    """Count the number of grid tracks in a `grid-template-*` value."""
    cleaned = re.sub(r"repeat\((\d+)[^)]*\)", lambda m: " ".join(["x"] * int(m.group(1))), track_value)
    return len([t for t in cleaned.split() if t and t not in {",", ";"}])


def lint_file(path: Path) -> list[dict]:
    """Return a list of warning dicts for one cache HTML file."""
    text = path.read_text(encoding="utf-8")
    warnings: list[dict] = []

    # Body density (cheap signal for the half-empty heuristic)
    body_chars = len(re.sub(r"<[^>]+>", "", text))

    # A — edge-bleed
    inset_fills = list(_RE_INSET_FILL.finditer(text))
    for m in inset_fills:
        # Look at the surrounding 200 chars for padding
        window_start = max(0, m.start() - 50)
        window_end = min(len(text), m.end() + 200)
        window = text[window_start:window_end]
        if _RE_PADDING_ZERO.search(window) or (
            "padding:" not in window and "<div" in window
        ):
            warnings.append({
                "class": "A",
                "label": "edge-bleed-risk",
                "message": "absolute child fills parent (inset:0) with padding:0 or no padding — text may touch the rim",
                "snippet": text[m.start():m.start()+90].replace("\n", " "),
            })

    # B — half-empty grid (heuristic): grid with ≥3 tracks and low body density
    rows_match = _RE_GRID_ROWS_3PLUS.search(text)
    cols_match = _RE_GRID_COLS_3PLUS.search(text)
    if rows_match and _count_grid_tracks(rows_match.group(1)) >= 3 and body_chars < 900:
        warnings.append({
            "class": "B",
            "label": "half-empty-grid-risk",
            "message": f"grid-template-rows reserves ≥3 rows but body density is {body_chars} chars — slots may be empty",
            "snippet": rows_match.group(0),
        })
    if cols_match and _count_grid_tracks(cols_match.group(1)) >= 4 and body_chars < 900:
        warnings.append({
            "class": "B",
            "label": "half-empty-grid-risk",
            "message": f"grid-template-columns reserves ≥4 columns but body density is {body_chars} chars",
            "snippet": cols_match.group(0),
        })

    # C — under-constrained absolute (no inset shorthand, fewer than 2 directional anchors)
    for m in _RE_POS_ABS.finditer(text):
        window = text[m.start():m.start() + 250]
        if _RE_INSET_FULL.search(window):
            continue  # has inset shorthand
        anchor_count = sum(1 for kw in ("top:", "right:", "bottom:", "left:") if kw in window)
        if anchor_count < 2:
            warnings.append({
                "class": "C",
                "label": "under-constrained-absolute",
                "message": f"position:absolute with only {anchor_count} directional anchor(s) — geometry depends on parent reflow",
                "snippet": text[m.start():m.start()+90].replace("\n", " "),
            })

    # D — tiny body text
    for m in _RE_TINY_FONT_REM.finditer(text):
        warnings.append({
            "class": "D",
            "label": "tiny-font",
            "message": f"font-size {m.group(0).split(':')[1].strip()} is too small for body text — reserve ≤0.7rem for micro-labels",
            "snippet": m.group(0),
        })
    for m in _RE_TINY_FONT_PX.finditer(text):
        warnings.append({
            "class": "D",
            "label": "tiny-font",
            "message": f"font-size {m.group(0).split(':')[1].strip()} is too small for body text",
            "snippet": m.group(0),
        })

    return warnings


# Severity weights (ben/167 v2). Higher = more readability impact.
# Used by the auto-re-roll trigger and to format the critique text fed back
# to the agent on a directed iteration.
CLASS_WEIGHTS = {
    "A": 3,  # edge-bleed — text touches rim, immediate readability hit
    "D": 3,  # tiny-font — same
    "B": 2,  # half-empty grid — looks unfinished but readable
    "C": 1,  # under-constrained absolute — reflow drift, often invisible
}

# Auto-re-roll threshold: ≥ this many points triggers a critique-aware
# re-roll attempt (only when --auto-re-roll-on-lint is passed). Tuned so a
# single low-severity hit doesn't trigger; multiple high-severity hits do.
RE_ROLL_THRESHOLD = 5


def slide_score(warnings: list[dict]) -> int:
    """Weighted severity score for a single slide's lint warnings."""
    return sum(CLASS_WEIGHTS.get(w.get("class", ""), 0) for w in warnings)


def format_critique(warnings: list[dict]) -> str:
    """Render warnings as a designer-readable critique for the agent.

    Used by the directed-iteration prompt block in `creative.build_brief`.
    Groups by class and lists the specific patterns flagged.
    """
    if not warnings:
        return ""
    by_class: dict[str, list[dict]] = {}
    for w in warnings:
        by_class.setdefault(w.get("class", "?"), []).append(w)
    labels = {
        "A": "edge-bleed (text within ~6px of rim, or absolute fill with no inner padding)",
        "B": "half-empty grid (rows/columns reserved but source content can't fill)",
        "C": "under-constrained absolute (position:absolute with < 2 directional anchors)",
        "D": "tiny body font (font-size < 0.7rem on what reads as body text)",
    }
    lines: list[str] = []
    for cls in sorted(by_class):
        n = len(by_class[cls])
        lines.append(f"  · class {cls} {labels.get(cls, '?')} — {n} hit(s)")
        for w in by_class[cls][:3]:
            lines.append(f"      e.g. {w.get('message', '')}")
    score = slide_score(warnings)
    lines.append(f"  weighted score: {score} (threshold {RE_ROLL_THRESHOLD})")
    return "\n".join(lines)


def lint_deck(out_dir: Path) -> dict:
    cache_dir = out_dir / ".creative-cache"
    if not cache_dir.is_dir():
        return {"files": 0, "warnings": [], "by_class": {}, "by_file": {}}

    by_class: dict[str, int] = {}
    by_file: dict[str, list[dict]] = {}
    total_warnings = 0

    files = sorted(cache_dir.glob("*.html"))
    for f in files:
        warnings = lint_file(f)
        if warnings:
            by_file[f.name] = warnings
            total_warnings += len(warnings)
            for w in warnings:
                by_class[w["class"]] = by_class.get(w["class"], 0) + 1

    return {
        "files": len(files),
        "warnings": total_warnings,
        "by_class": by_class,
        "by_file": by_file,
    }


def _print_human(result: dict, *, quiet: bool = False) -> None:
    files = result["files"]
    n = result["warnings"]
    by_class = result["by_class"]
    print(f"md-deck lint — {files} cache files scanned, {n} warning(s)")
    if not by_class:
        print("  (clean)")
        return
    labels = {
        "A": "edge-bleed-risk",
        "B": "half-empty-grid-risk",
        "C": "under-constrained-absolute",
        "D": "tiny-font",
    }
    for cls in sorted(by_class):
        print(f"  · {cls} {labels.get(cls, '?'):30s} {by_class[cls]:4d} hit(s)")
    if quiet:
        return
    print()
    print("Per-section:")
    by_file = result["by_file"]
    for name in sorted(by_file):
        warnings = by_file[name]
        slug = name.split("__")[0]
        slot = name.rsplit("-", 1)[-1].replace(".html", "")
        cls_counts = {}
        for w in warnings:
            cls_counts[w["class"]] = cls_counts.get(w["class"], 0) + 1
        cls_summary = " ".join(f"{c}:{cls_counts[c]}" for c in sorted(cls_counts))
        print(f"  {slug:50s} {slot:12s} {cls_summary}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("out_dir", help="Deck output directory (e.g., assets/<slug>/)")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    parser.add_argument("--quiet", action="store_true", help="Print only the summary, no per-file list")
    args = parser.parse_args()
    result = lint_deck(Path(args.out_dir))
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        _print_human(result, quiet=args.quiet)
    return 0


if __name__ == "__main__":
    sys.exit(main())
