"""`/web-control diagnose [--live]` — health-check + diagnostic dump.

Runs structural + lib-import + live checks, prints a structured
diagnostic report. Used as both:

  - On-demand health check (user runs when something feels off)
  - Recommended first step when the user reports issues

Without `--live`: structural + lib + platform only (~1 second).
With `--live`: also exercises a launch → connect → status → stop cycle
on a temporary profile dir + port (~10 seconds).
"""
from __future__ import annotations

import json
import os
import shutil
import socket
import subprocess
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL_ROOT))


def _check(label: str, ok: bool, detail: str = "", recovery: str = "") -> dict:
    return {"label": label, "ok": ok, "detail": detail, "recovery": recovery}


def _print_check(c: dict) -> None:
    mark = "✓" if c["ok"] else "✗"
    print(f"  {mark}  {c['label']}")
    if c["detail"]:
        print(f"        {c['detail']}")
    if not c["ok"] and c["recovery"]:
        print(f"        recovery: {c['recovery']}")


def main() -> int:
    live = "--live" in sys.argv

    print("web-control diagnose")
    print("====================")
    print()

    checks: list[dict] = []

    # Structure
    print("[1] skill structure")
    for f in [
        "SKILL.md", "README.md", "VERSION",
        "actions/setup.py", "actions/launch.py", "actions/status.py",
        "actions/stop.py", "actions/purge_stale.py", "actions/diagnose.py",
        "lib/__init__.py", "lib/errors.py", "lib/platform.py",
        "lib/lifecycle.py", "lib/connect.py", "lib/input.py", "lib/a11y.py",
        "lib/python_runtime.py",
        "scripts/launch-debug-chrome.sh", "scripts/install-chrome-wsl.sh",
        "templates/mcp-attach-block.json",
        "tests/test-lifecycle.sh",
    ]:
        c = _check(f"file exists: {f}", (SKILL_ROOT / f).is_file())
        checks.append(c)
        _print_check(c)

    # Executable bits
    print()
    print("[2] script executable bits")
    for f in ["scripts/launch-debug-chrome.sh", "scripts/install-chrome-wsl.sh", "tests/test-lifecycle.sh"]:
        path = SKILL_ROOT / f
        c = _check(f"executable: {f}", path.is_file() and os.access(path, os.X_OK))
        checks.append(c)
        _print_check(c)

    # Library imports
    print()
    print("[3] lib imports")
    try:
        from lib import (  # noqa
            connect_to_chrome, find_tab, with_page,
            send_key, click_at, type_text, keyboard_shortcut,
            get_a11y_text, is_signed_in,
            WebControlError, ChromeNotInstalled,
            detect_platform, profile_dir, REQUIRED_CHROME_FLAGS,
        )
        c = _check("lib package importable", True)
    except ImportError as exc:
        c = _check("lib package importable", False, str(exc),
                   "ensure web-control's lib/__init__.py exports the expected names")
    checks.append(c)
    _print_check(c)

    # Python runtime deps
    print()
    print("[4] Python runtime deps (websocket-client, pyyaml)")
    try:
        from lib.python_runtime import discover, runtime_health, install_hint
        info = runtime_health()
        c = _check(
            f"runtime: {info['source']}",
            info["deps_ok"],
            f"python={info['python']}",
            install_hint() if not info["deps_ok"] else "",
        )
    except ImportError:
        c = _check("python_runtime module importable", False, "module missing",
                   "expected at lib/python_runtime.py")
    checks.append(c)
    _print_check(c)

    # Platform detection
    print()
    print("[5] platform")
    try:
        from lib.platform import detect_platform, chrome_binary_path, chrome_version, profile_dir as pdir, REQUIRED_CHROME_FLAGS
        plat = detect_platform()
        c = _check("platform detection", True, f"plat={plat}")
        checks.append(c)
        _print_check(c)
        try:
            binary = chrome_binary_path()
            ver = chrome_version(binary)
            c = _check("chrome binary", True, f"{binary} (v{ver})")
        except Exception as exc:  # noqa: BLE001
            c = _check("chrome binary", False, str(exc),
                       "run /web-control setup to install (apt on Linux/WSL, brew on macOS)")
        checks.append(c)
        _print_check(c)
        c = _check(
            "profile dir exists",
            pdir().is_dir(),
            str(pdir()),
            "run /web-control setup to create",
        )
        checks.append(c)
        _print_check(c)
        flags = REQUIRED_CHROME_FLAGS()
        has_origins = any("--remote-allow-origins" in f and "127.0.0.1" in f for f in flags)
        c = _check(
            "REQUIRED_CHROME_FLAGS includes 127.0.0.1 origin",
            has_origins,
            "; ".join(flags),
            "Chrome 145+ origin check needs both localhost AND 127.0.0.1",
        )
        checks.append(c)
        _print_check(c)
    except Exception as exc:  # noqa: BLE001
        c = _check("platform.py functional", False, str(exc))
        checks.append(c)
        _print_check(c)

    # Live checks
    if live:
        print()
        print("[6] LIVE: launch / status / stop on test port + profile")
        test_port = 9333
        test_profile = "/tmp/web-control-diagnose-test-profile"
        try:
            shutil.rmtree(test_profile, ignore_errors=True)
            launcher = SKILL_ROOT / "scripts" / "launch-debug-chrome.sh"
            env = os.environ.copy()
            env["WEB_CONTROL_PORT"] = str(test_port)
            env["WEB_CONTROL_PROFILE_DIR"] = test_profile
            # Launch (background)
            proc = subprocess.Popen(
                [str(launcher)],
                env=env,
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
            # Poll port
            import time
            deadline = time.time() + 25
            up = False
            while time.time() < deadline:
                try:
                    with socket.create_connection(("127.0.0.1", test_port), timeout=1):
                        up = True
                        break
                except OSError:
                    time.sleep(0.5)
            c = _check("live: launch reaches port", up, f"port={test_port}")
            checks.append(c)
            _print_check(c)
            # Stop
            from lib.lifecycle import kill_chrome
            from pathlib import Path as _P
            kill_chrome(_P(test_profile))
            time.sleep(2)
            try:
                with socket.create_connection(("127.0.0.1", test_port), timeout=1):
                    still_up = True
            except OSError:
                still_up = False
            c = _check("live: stop cleanly closes port", not still_up)
            checks.append(c)
            _print_check(c)
        except Exception as exc:  # noqa: BLE001
            c = _check("live: lifecycle test", False, str(exc))
            checks.append(c)
            _print_check(c)
        finally:
            shutil.rmtree(test_profile, ignore_errors=True)

    # Summary
    print()
    print("====================")
    n_ok = sum(1 for c in checks if c["ok"])
    n_fail = sum(1 for c in checks if not c["ok"])
    print(f"Results: {n_ok} pass, {n_fail} fail")
    if n_fail:
        print()
        print("Failed checks:")
        for c in checks:
            if not c["ok"]:
                print(f"  ✗ {c['label']}")
                if c["recovery"]:
                    print(f"    -> {c['recovery']}")
    return 0 if n_fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
