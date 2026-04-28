"""`/web-control launch` — start the dedicated debug Chrome via the launcher
script. Idempotent: returns success if already running."""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL_ROOT))

from lib.errors import WebControlError  # noqa: E402
from lib.lifecycle import is_debug_port_listening  # noqa: E402
from lib.platform import DEFAULT_DEBUG_PORT, profile_dir  # noqa: E402


def main() -> int:
    launcher = SKILL_ROOT / "scripts" / "launch-debug-chrome.sh"
    if not launcher.exists():
        print(f"ERROR: launcher missing at {launcher}", file=sys.stderr)
        print("  -> Run: /web-control setup", file=sys.stderr)
        return 65

    print(f"web-control launch (port {DEFAULT_DEBUG_PORT}, profile {profile_dir()})")
    if is_debug_port_listening(port=DEFAULT_DEBUG_PORT):
        print("  Debug port already responding — skipping launch (idempotent).")
        return 0

    try:
        result = subprocess.run([str(launcher)], check=False)
    except FileNotFoundError as exc:
        print(f"ERROR: cannot execute launcher: {exc}", file=sys.stderr)
        return 65

    if result.returncode != 0:
        print(
            "ERROR: launcher exited non-zero. See output above.",
            file=sys.stderr,
        )
        print(
            "  -> Diagnostic: bash {} (run directly to see full output)".format(launcher),
            file=sys.stderr,
        )
    return result.returncode


if __name__ == "__main__":
    try:
        sys.exit(main())
    except WebControlError as exc:
        print(exc.render(), file=sys.stderr)
        sys.exit(1)
