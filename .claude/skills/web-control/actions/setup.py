"""`/web-control setup` — install Chrome (if missing), create profile dir,
make scripts executable. Idempotent."""
from __future__ import annotations

import os
import stat
import subprocess
import sys
from pathlib import Path

# Make the lib package importable when run as a script
SKILL_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL_ROOT))

from lib.errors import ChromeNotInstalled, UnsupportedPlatform, WebControlError  # noqa: E402
from lib.platform import (  # noqa: E402
    chrome_binary_path,
    chrome_major_version,
    detect_platform,
    profile_dir,
)


MIN_CHROME_MAJOR = 124  # --remote-allow-origins lands cleanly here


def _ensure_executable(path: Path) -> None:
    st = path.stat()
    path.chmod(st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def main() -> int:
    print("web-control setup")
    print("=================")

    # 1. Platform check
    try:
        plat = detect_platform()
        print(f"  [1/5] Platform:        {plat}")
    except UnsupportedPlatform as exc:
        print(f"  [1/5] Platform: UNSUPPORTED ({exc})")
        print(f"        -> {exc.recovery}")
        return 64

    # 2. Chrome detection / install hint
    print("  [2/5] Chrome:          ", end="")
    try:
        binary = chrome_binary_path()
        major = chrome_major_version(binary)
        print(f"{binary} (v{major})")
        if major and major < MIN_CHROME_MAJOR:
            print(
                f"        WARNING: Chrome {major} is older than the minimum "
                f"recommended {MIN_CHROME_MAJOR}+ (--remote-allow-origins)."
            )
    except ChromeNotInstalled as exc:
        print("NOT FOUND")
        print(f"        -> {exc}")
        if plat == "wsl" or plat == "linux":
            installer = SKILL_ROOT / "scripts" / "install-chrome-wsl.sh"
            print(f"        Install with: bash {installer}")
        elif plat == "macos":
            print("        Install with: brew install --cask google-chrome")
        return 65

    # 3. Profile dir
    pdir = profile_dir()
    pdir.mkdir(parents=True, exist_ok=True)
    print(f"  [3/5] Profile dir:     {pdir}  (exists: {pdir.is_dir()})")

    # 4. Launcher script(s) executable
    launcher = SKILL_ROOT / "scripts" / "launch-debug-chrome.sh"
    installer = SKILL_ROOT / "scripts" / "install-chrome-wsl.sh"
    for s in (launcher, installer):
        if s.exists():
            _ensure_executable(s)
    print(f"  [4/5] Launcher:        {launcher} (executable)")

    # 5. Python deps for consumer skills (websocket-client) — best-effort detect
    print("  [5/5] Python websocket-client: ", end="")
    try:
        import websocket  # type: ignore  # noqa: F401
        print("OK")
    except ImportError:
        print("MISSING")
        print(
            "        Consumer skills using web-control's connect API need "
            "websocket-client. Install with one of:"
        )
        print("          pip install --user websocket-client")
        print("          (or via a venv your skill manages)")
        # Not fatal — `setup` succeeds even without it; it's a consumer concern

    print()
    print("Setup complete. Next steps:")
    print(f"  1. Run: bash {launcher}")
    print("  2. Sign in to your corporate Google account in the visible Chrome window")
    print("  3. Once signed in, run: /web-control status   (verify port + tab health)")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except WebControlError as exc:
        print(exc.render(), file=sys.stderr)
        sys.exit(1)
