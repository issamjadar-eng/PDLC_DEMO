"""`change-control review-internal-status <doc>` — wire-compatible alias for `review-status`.

Renamed in v0.6 as part of the naming pivot: the original
`review-*` set is now the `review-internal-*` tier (Google Docs
backend). The new `review-formal-*` tier covers Confluence +
review-plugin approval workflows.

This alias delegates to the original action verbatim. The old name
will be removed after one release window.
"""
from __future__ import annotations

import sys
from pathlib import Path

ACTIONS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ACTIONS_DIR))

import review_status as _impl  # noqa: E402


def main() -> int:
    print(
        "DEPRECATION NOTICE: `review-internal-status` is the new name for `review-status`. "
        "Both work in v0.6; the old name will be removed in v0.7.",
        file=sys.stderr,
    )
    return _impl.main()


if __name__ == "__main__":
    sys.exit(main())
