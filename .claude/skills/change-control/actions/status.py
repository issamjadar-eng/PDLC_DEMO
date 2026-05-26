"""`change-control status` — read-only view of all controlled docs.

Scans a path tree for markdown files with HTML-comment YAML
frontmatter that includes a `state` field (any state — draft,
published, review-formal, frozen, released). Prints a table with
state / page_id / last_published_version / title / path.

Pure-local: no MCP, no network. Fast enough to run on every DHF
tree. (Optional `--check-divergence` flag would add a network probe —
deferred until an action consumer needs it; v0.6 keeps status
no-network.)

Usage:

    python actions/status.py [<path>] [--json] [--state <S>]

Defaults:
  - <path>: `docs`
  - Output: human-readable table; `--json` switches to JSON for tooling
  - `--state <S>`: filter to that lifecycle state only

Always exits 0 unless the path doesn't exist or args are malformed.
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Iterable

SKILL_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL_ROOT))

from lib.frontmatter import read as read_frontmatter  # noqa: E402


VALID_STATES = ("draft", "published", "review-formal", "review-internal", "frozen", "released")


@dataclass
class DocStatus:
    path: str
    state: str = ""
    title: str = ""
    page_id: str = ""
    space_key: str = ""
    last_published_version: int = 0
    frozen_at_version: int = 0
    approval_plugin: str = ""
    approval_signers: list[str] = field(default_factory=list)


def scan_tree(root: Path) -> Iterable[DocStatus]:
    """Walk `root`, parse every `*.md` with HTML-comment frontmatter
    that has a `state` field, and yield a `DocStatus` per match."""
    for path in sorted(root.rglob("*.md")):
        if path.name.endswith(".confluence-side.md"):
            continue
        try:
            fm = read_frontmatter(path)
        except Exception:
            continue
        data = fm.data
        state = data.get("state")
        if not state:
            continue
        confluence = data.get("confluence") or {}
        approval = confluence.get("approval") or {}
        signers: list[str] = []
        for s in approval.get("signers") or []:
            if isinstance(s, dict):
                signers.append(s.get("display_name") or s.get("account_id") or "")
        yield DocStatus(
            path=str(path),
            state=str(state),
            title=str(data.get("title") or ""),
            page_id=str(confluence.get("page_id") or ""),
            space_key=str(confluence.get("space_key") or ""),
            last_published_version=int(confluence.get("last_published_version") or 0),
            frozen_at_version=int(confluence.get("frozen_at_version") or 0),
            approval_plugin=str(approval.get("plugin") or ""),
            approval_signers=signers,
        )


def render_table(rows: list[DocStatus]) -> str:
    if not rows:
        return "(no controlled docs found)"
    headers = ["state", "page_id", "v", "title", "path"]
    data: list[list[str]] = [headers]
    for r in rows:
        title = r.title[:50]
        path = r.path
        if len(path) > 60:
            path = "..." + path[-57:]
        data.append([
            r.state,
            r.page_id or "-",
            str(r.last_published_version) if r.last_published_version else "-",
            title or "-",
            path,
        ])
    widths = [max(len(row[i]) for row in data) for i in range(len(headers))]
    lines = []
    for i, row in enumerate(data):
        lines.append("  ".join(cell.ljust(widths[j]) for j, cell in enumerate(row)))
        if i == 0:
            lines.append("  ".join("-" * w for w in widths))
    return "\n".join(lines)


def render_summary(rows: list[DocStatus]) -> str:
    counts: dict[str, int] = {}
    for r in rows:
        counts[r.state] = counts.get(r.state, 0) + 1
    parts = [f"{counts.get(s, 0)} {s}" for s in VALID_STATES if counts.get(s, 0) > 0]
    other = [k for k in counts if k not in VALID_STATES]
    for k in other:
        parts.append(f"{counts[k]} {k}")
    if not parts:
        return "0 docs"
    return ", ".join(parts) + f" ({sum(counts.values())} total)"


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="change-control status",
        description="Read-only view of all controlled docs and their lifecycle states.",
    )
    p.add_argument("path", nargs="?", default="docs",
                   help="Root path to scan (default: docs).")
    p.add_argument("--json", action="store_true",
                   help="Emit JSON instead of a human-readable table.")
    p.add_argument("--state", default="",
                   help="Filter to docs in this lifecycle state only.")
    return p


def run(args: argparse.Namespace) -> int:
    root = Path(args.path)
    if not root.exists():
        print(f"status: path not found: {root}", file=sys.stderr)
        return 64
    rows = list(scan_tree(root))
    if args.state:
        rows = [r for r in rows if r.state == args.state]
    if args.json:
        print(json.dumps([asdict(r) for r in rows], indent=2, sort_keys=True))
    else:
        print(render_table(rows))
        print()
        print(f"summary: {render_summary(rows)}")
    return 0


def main(argv: list[str] | None = None) -> int:
    return run(_build_parser().parse_args(argv))


if __name__ == "__main__":
    sys.exit(main())
