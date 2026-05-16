"""Rebuild orchestrator — entry point for `/file-locator rebuild`.

Usage:
    python3 rebuild.py [--full]

Default is incremental: only NEW/CHANGED files are re-processed. --full drops
all existing rows and re-embeds everything.
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

# Allow the script to be invoked from anywhere; resolve common.py relative to this file.
sys.path.insert(0, str(Path(__file__).parent))

from common import load_config  # noqa: E402
from indexer_docs import index  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Rebuild the file-locator index.")
    parser.add_argument(
        "--full",
        action="store_true",
        help="From-scratch rebuild (ignore prior state, re-embed everything).",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress per-step progress; print only final stats line.",
    )
    args = parser.parse_args()

    cfg = load_config()
    if not args.quiet:
        print(f"→ index path:      {cfg.index_path.relative_to(cfg.project_root)}")
        print(f"→ embedding model: {cfg.embedding_model} ({cfg.embedding_dimension}-dim)")
        print(f"→ mode:            {'FULL rebuild' if args.full else 'incremental'}")
        print()

    stats = index(cfg, full=args.full)

    size_kb = (
        cfg.index_path.stat().st_size / 1024 if cfg.index_path.exists() else 0
    )
    print(
        f"✓ {stats.new} new, {stats.changed} changed, {stats.unchanged} unchanged, "
        f"{stats.removed} removed — {stats.elapsed_seconds}s — index {size_kb:.0f} KB"
    )

    if (stats.new + stats.changed + stats.removed) > 0 and os.environ.get("CI") != "true":
        print()
        print(
            "ℹ  If this was a maintenance rebuild, commit the refreshed index:\n"
            "   git add tools/file-locator-mcp/index.db && \\\n"
            "   git commit -m 'file-locator: rebuild index'"
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
