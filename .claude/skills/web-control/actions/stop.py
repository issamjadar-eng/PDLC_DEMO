"""`/web-control stop` — terminate the dedicated debug Chrome cleanly.

Only kills processes whose --user-data-dir matches our profile dir, so the
user's main Chrome is never touched.
"""
from __future__ import annotations

import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL_ROOT))

from lib.errors import WebControlError  # noqa: E402
from lib.lifecycle import chrome_pids, kill_chrome  # noqa: E402
from lib.platform import profile_dir  # noqa: E402


def main() -> int:
    pdir = profile_dir()
    pids = chrome_pids()
    if not pids:
        print(f"web-control stop: no debug Chrome processes for profile {pdir}.")
        return 0
    print(f"web-control stop: terminating {len(pids)} process(es) for profile {pdir}")
    print(f"  pids: {pids}")
    n = kill_chrome()
    remaining = chrome_pids()
    if remaining:
        print(f"  WARNING: {len(remaining)} process(es) still running after kill: {remaining}", file=sys.stderr)
        return 1
    print(f"  cleanly terminated {n} process(es).")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except WebControlError as exc:
        print(exc.render(), file=sys.stderr)
        sys.exit(1)
