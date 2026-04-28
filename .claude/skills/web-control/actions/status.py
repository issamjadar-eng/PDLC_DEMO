"""`/web-control status` — health-check the debug Chrome."""
from __future__ import annotations

import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL_ROOT))

from lib.errors import ChromeNotInstalled, WebControlError  # noqa: E402
from lib.lifecycle import (  # noqa: E402
    chrome_pids,
    is_chrome_running,
    is_debug_port_listening,
)
from lib.platform import (  # noqa: E402
    DEFAULT_DEBUG_PORT,
    chrome_binary_path,
    chrome_version,
    detect_platform,
    profile_dir,
)


def main() -> int:
    print("web-control status")
    print("==================")

    # Platform
    try:
        plat = detect_platform()
        print(f"  platform:           {plat}")
    except WebControlError as exc:
        print(f"  platform:           ERROR ({exc})")
        return 1

    # Chrome binary
    try:
        binary = chrome_binary_path()
        ver = chrome_version(binary)
        print(f"  chrome binary:      {binary}")
        print(f"  chrome version:     {ver}")
    except ChromeNotInstalled as exc:
        print(f"  chrome binary:      NOT FOUND")
        print(f"                       -> {exc.recovery}")
        return 1

    # Profile dir
    pdir = profile_dir()
    print(f"  profile dir:        {pdir} (exists={pdir.is_dir()})")

    # PIDs
    pids = chrome_pids()
    print(f"  matching processes: {len(pids)} (pids={pids if pids else '-'})")

    # Debug port
    listening = is_debug_port_listening(port=DEFAULT_DEBUG_PORT)
    print(f"  debug port {DEFAULT_DEBUG_PORT}:    {'LISTENING' if listening else 'not listening'}")

    # Tab count if reachable
    if listening:
        try:
            from lib.connect import connect_to_chrome  # noqa: WPS433
            chrome = connect_to_chrome()
            tabs = chrome.list_tabs()
            page_tabs = [t for t in tabs if t.type == "page"]
            print(f"  open page tabs:     {len(page_tabs)}")
            for t in page_tabs[:5]:
                print(f"    - {t.title[:60]} ({t.url[:80]})")
        except Exception as exc:
            print(f"  tab listing:        FAILED ({exc})")

    # Sign-in heuristic — if any drive.google.com/drive/ tab is present, likely signed in
    if listening:
        try:
            from lib.connect import connect_to_chrome  # noqa: WPS433
            chrome = connect_to_chrome()
            signed_in_tab = chrome.find_tab(
                lambda t: t.type == "page" and (
                    "/drive/home" in t.url or "/document/d/" in t.url or "drive.google.com/drive" in t.url
                )
            )
            print(f"  sign-in:            {'authenticated' if signed_in_tab else 'no authenticated drive tab visible'}")
        except Exception:
            pass

    print()
    if not is_chrome_running() and not listening:
        print("  Summary: Chrome is NOT running. Start it with: /web-control launch")
    elif listening:
        print("  Summary: Chrome is running and the debug port is reachable. Ready for use.")
    else:
        print("  Summary: Chrome processes detected but debug port is not listening. Check port conflict.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except WebControlError as exc:
        print(exc.render(), file=sys.stderr)
        sys.exit(1)
