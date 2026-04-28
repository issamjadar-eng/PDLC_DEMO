"""Chrome lifecycle helpers — pid lookup, port-listening detection, kill."""
from __future__ import annotations

import os
import re
import signal
import socket
import subprocess
import time
from pathlib import Path

from .platform import DEFAULT_DEBUG_PORT, profile_dir


def chrome_pids(profile: Path | None = None) -> list[int]:
    """Return PIDs of Chrome processes that match our dedicated user-data-dir.

    Matches via ps + cmdline grep. Avoids killing the user's main Chrome.
    """
    pdir = str(profile or profile_dir())
    pids: list[int] = []
    try:
        out = subprocess.check_output(["ps", "-eo", "pid=,args="], stderr=subprocess.DEVNULL).decode()
    except Exception:
        return []
    for line in out.splitlines():
        line = line.strip()
        if not line:
            continue
        # Match the chrome binary running with our user-data-dir
        if pdir in line and ("chrome" in line.lower() or "chromium" in line.lower()):
            mo = re.match(r"\s*(\d+)\s", line)
            if mo:
                pid = int(mo.group(1))
                # Don't include the current process or its parents to avoid
                # accidental self-kills if invoked weirdly
                if pid != os.getpid() and pid != os.getppid():
                    pids.append(pid)
    return pids


def is_chrome_running(profile: Path | None = None) -> bool:
    return len(chrome_pids(profile)) > 0


def is_debug_port_listening(port: int = DEFAULT_DEBUG_PORT, host: str = "127.0.0.1", timeout: float = 1.0) -> bool:
    """Try a TCP connect — quicker than scraping ss/netstat output."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def kill_chrome(profile: Path | None = None, timeout: float = 5.0) -> int:
    """Send SIGTERM to Chrome processes matching our user-data-dir. Returns
    the number of processes signaled. Idempotent."""
    pids = chrome_pids(profile)
    if not pids:
        return 0
    for pid in pids:
        try:
            os.kill(pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
    # Wait for processes to exit
    deadline = time.time() + timeout
    while time.time() < deadline:
        if not chrome_pids(profile):
            return len(pids)
        time.sleep(0.2)
    # Force-kill any survivors
    for pid in chrome_pids(profile):
        try:
            os.kill(pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    return len(pids)
