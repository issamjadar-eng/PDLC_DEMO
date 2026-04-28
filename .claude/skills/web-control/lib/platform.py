"""Platform detection + Chrome path resolution + canonical flag list.

The skill supports macOS and Linux/WSL. On Linux it expects google-chrome to
be installed via apt (Google's official repo). On macOS it expects Google
Chrome.app at the standard /Applications/ path or any Chromium-family browser
the user has installed.
"""
from __future__ import annotations

import os
import platform as _platform
import shutil
from pathlib import Path

from .errors import ChromeNotInstalled, UnsupportedPlatform


# ---- Constants ----

DEFAULT_DEBUG_PORT = int(os.environ.get("WEB_CONTROL_PORT", "9222"))


def _profile_dir_default() -> Path:
    """The dedicated debug profile dir. Same path on all platforms (Chrome
    accepts --user-data-dir paths uniformly)."""
    return Path.home() / ".config" / "google-chrome-debug"


def profile_dir() -> Path:
    override = os.environ.get("WEB_CONTROL_PROFILE_DIR")
    return Path(override).expanduser() if override else _profile_dir_default()


# Required Chrome flags (validated in task 116).
# Window-size + position keep the window small + visible so re-auth stays
# user-responsive (see task 116 P2.9 / task 117 strategy notes).
def REQUIRED_CHROME_FLAGS(port: int | None = None, profile: Path | None = None) -> list[str]:
    p = port if port is not None else DEFAULT_DEBUG_PORT
    pdir = profile if profile is not None else profile_dir()
    return [
        f"--remote-debugging-port={p}",
        # Both origins required: Chrome 145+ treats localhost and 127.0.0.1
        # as distinct origins for the WebSocket origin check.
        f"--remote-allow-origins=http://localhost:{p},http://127.0.0.1:{p}",
        f"--user-data-dir={pdir}",
        "--window-size=800,700",
        "--window-position=100,100",
    ]


# ---- Platform detection ----

def detect_platform() -> str:
    """Return one of: 'macos', 'wsl', 'linux'. Native Windows is not
    supported as a primary platform — raise UnsupportedPlatform."""
    sysname = _platform.system().lower()
    if sysname == "darwin":
        return "macos"
    if sysname == "linux":
        # WSL detection — kernel release contains 'microsoft' in WSL2
        try:
            release = Path("/proc/version").read_text().lower()
            if "microsoft" in release or "wsl" in release:
                return "wsl"
        except OSError:
            pass
        return "linux"
    if sysname == "windows":
        raise UnsupportedPlatform(
            f"native Windows detected ({sysname}); web-control runs under "
            f"WSL on Windows."
        )
    raise UnsupportedPlatform(f"unrecognized platform: {sysname}")


def chrome_binary_path() -> str:
    """Return absolute path to the Chrome binary. Raises ChromeNotInstalled
    if not found. Probes platform-typical locations."""
    plat = detect_platform()
    candidates: list[str] = []
    if plat == "macos":
        candidates = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
            "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
        ]
    else:
        # Linux / WSL — apt-installed locations
        candidates = [
            "/usr/bin/google-chrome",
            "/usr/bin/google-chrome-stable",
            "/usr/bin/chromium-browser",
            "/usr/bin/chromium",
            "/snap/bin/chromium",
        ]
        # Also consult PATH
        for name in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser"):
            found = shutil.which(name)
            if found:
                candidates.append(found)

    for c in candidates:
        if Path(c).exists() and os.access(c, os.X_OK):
            return c

    raise ChromeNotInstalled(
        f"no Chrome-family browser found on {plat}. Searched: {candidates}"
    )


def chrome_version(binary: str | None = None) -> str:
    """Return Chrome version string, e.g., '145.0.7632.159'."""
    import subprocess
    b = binary or chrome_binary_path()
    try:
        out = subprocess.check_output([b, "--version"], stderr=subprocess.STDOUT, timeout=5).decode().strip()
    except Exception as exc:
        raise ChromeNotInstalled(f"could not run {b} --version: {exc}")
    # "Google Chrome 145.0.7632.159" / "Chromium 134.0.6998.165"
    parts = out.split()
    for tok in parts:
        if tok and tok[0].isdigit():
            return tok
    return out


def chrome_major_version(binary: str | None = None) -> int:
    v = chrome_version(binary)
    try:
        return int(v.split(".")[0])
    except ValueError:
        return 0
