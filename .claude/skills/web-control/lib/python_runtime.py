"""Discover a Python interpreter that has the deps web-control needs.

Used by change-control's action scripts when they're invoked as
subprocess. The deps web-control's lib needs at runtime:

  - websocket-client    (CDP WebSocket channel; apt: python3-websocket)
  - pyyaml              (project.yml read; apt: python3-yaml)

Discovery order (first that has all deps wins):
  1. WEB_CONTROL_PYTHON env var (explicit override)
  2. python3 from PATH (system; on Ubuntu/Debian, both deps come from
     apt; on macOS, from `pip install --user`)
  3. /tmp/dhf-probe-venv/bin/python3 (legacy dev-venv path; only used
     when system Python is missing deps and the developer happened to
     have this from earlier work)

If nothing found, returns the system python3 with a clear warning so the
caller can surface a recovery hint pointing at apt / pip --user.

Note: setup.sh now installs the deps system-wide via apt (Linux/WSL)
or pip --user (macOS). The dev-venv fallback exists for environments
where setup.sh hasn't run (CI containers, test rigs).
"""
from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path


REQUIRED_DEPS = ("websocket", "yaml")  # import names


def _has_deps(py: str) -> bool:
    """Return True iff the given python interpreter has all REQUIRED_DEPS importable."""
    if not py or not Path(py).is_file() and not shutil.which(py):
        return False
    code = f"import {','.join(REQUIRED_DEPS)}; print('ok')"
    try:
        result = subprocess.run(
            [py, "-c", code],
            capture_output=True, text=True, timeout=5,
        )
        return result.returncode == 0 and "ok" in result.stdout
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def discover() -> tuple[str, str]:
    """Return (python_path, source_label) for the best-fit interpreter.

    source_label is one of:
      'env'      — WEB_CONTROL_PYTHON
      'system'   — python3 on PATH (the happy path; setup.sh installs
                   deps via apt on Linux/WSL or pip --user on macOS)
      'apt'      — /usr/bin/python3 explicit (handles devs whose PATH
                   has Homebrew/linuxbrew python ahead of /usr/bin —
                   apt-installed python3-websocket / python3-yaml are
                   only visible to Ubuntu's /usr/bin/python3)
      'devvenv'  — /tmp/dhf-probe-venv (legacy dev surface; fallback)
      'fallback' — last-resort system python with missing deps
    """
    # 1. Env override
    env_py = os.environ.get("WEB_CONTROL_PYTHON")
    if env_py and _has_deps(env_py):
        return env_py, "env"

    # 2. System python3 — primary path. setup.sh installs deps here:
    #    Linux/WSL: sudo apt install python3-websocket python3-yaml
    #    macOS:     pip install --user websocket-client pyyaml
    sys_py = shutil.which("python3") or "python3"
    if _has_deps(sys_py):
        return sys_py, "system"

    # 3. Explicit /usr/bin/python3 — covers the case where a developer
    # has Homebrew/linuxbrew python first on PATH (no apt visibility)
    # but Ubuntu's apt-installed deps are present at /usr/bin/python3.
    apt_py = "/usr/bin/python3"
    if Path(apt_py).is_file() and apt_py != sys_py and _has_deps(apt_py):
        return apt_py, "apt"

    # 4. Legacy dev-venv fallback (handy in test rigs / CI containers
    # where setup.sh hasn't run)
    devvenv = "/tmp/dhf-probe-venv/bin/python3"
    if _has_deps(devvenv):
        return devvenv, "devvenv"

    # Fallback — return system python anyway so the caller gets a clear
    # error with the install hint instead of a silent crash
    return sys_py, "fallback"


def runtime_health() -> dict:
    """Return a structured health snapshot for diagnostics."""
    py, source = discover()
    info: dict = {
        "python": py,
        "source": source,
        "deps_ok": source != "fallback",
        "missing": [],
    }
    if source == "fallback":
        for dep in REQUIRED_DEPS:
            try:
                subprocess.run(
                    [py, "-c", f"import {dep}"],
                    capture_output=True, timeout=3, check=True,
                )
            except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
                info["missing"].append(dep)
    return info


def install_hint() -> str:
    """Return a one-liner the user can run to fix a missing-deps situation."""
    return (
        "Install web-control runtime deps with one of:\n"
        "  pip install --user websocket-client pyyaml\n"
        "  or: pip install --break-system-packages websocket-client pyyaml\n"
        "  or: python3 -m venv .state/web-control-venv && \\\n"
        "      .state/web-control-venv/bin/pip install websocket-client pyyaml"
    )
