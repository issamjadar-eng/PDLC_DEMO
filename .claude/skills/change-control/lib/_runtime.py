"""Runtime guard for change-control action scripts.

Each action script imports `ensure_runtime()` first. If the current
interpreter is missing required deps (websocket-client, pyyaml), this
re-launches the script under the discovered web-control runtime.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

# Make web-control's lib importable
_PROJECT_ROOT = Path(__file__).resolve().parents[4]
_WEB_CONTROL_DIR = _PROJECT_ROOT / ".claude" / "skills" / "web-control"


def _have_deps() -> tuple[bool, list[str]]:
    missing: list[str] = []
    for mod in ("websocket", "yaml"):
        try:
            __import__(mod)
        except ImportError:
            missing.append(mod)
    return (not missing, missing)


def ensure_runtime() -> None:
    """If the current Python is missing deps, re-launch this script under
    the right Python via web-control's discovery. If discovery also can't
    find a Python with the deps, print a clear error + install hint."""
    if os.environ.get("_WEB_CONTROL_RUNTIME_VERIFIED") == "1":
        return  # Avoid loop on re-launch
    have, missing = _have_deps()
    if have:
        os.environ["_WEB_CONTROL_RUNTIME_VERIFIED"] = "1"
        return

    # Try to discover a better runtime via web-control. Load python_runtime
    # explicitly by path — sys.path-based import would collide with
    # change-control's own lib package (already in sys.modules as 'lib').
    pr_path = _WEB_CONTROL_DIR / "lib" / "python_runtime.py"
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("_wc_python_runtime", pr_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"could not load spec from {pr_path}")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        discover = mod.discover
        install_hint = mod.install_hint
    except (ImportError, FileNotFoundError, AttributeError) as exc:
        print(
            f"ERROR: change-control action needs Python deps {missing} but "
            f"web-control's runtime discovery is not loadable: {exc}",
            file=sys.stderr,
        )
        print(
            "Recovery: pip install --user websocket-client pyyaml",
            file=sys.stderr,
        )
        sys.exit(2)

    py, source = discover()
    if source == "fallback":
        print(
            f"ERROR: change-control action needs Python deps {missing}. "
            f"Tried interpreter {py!r} but it is missing them.",
            file=sys.stderr,
        )
        print(install_hint(), file=sys.stderr)
        sys.exit(2)

    # Re-launch this script under the discovered runtime
    new_env = os.environ.copy()
    new_env["_WEB_CONTROL_RUNTIME_VERIFIED"] = "1"
    new_env["_WEB_CONTROL_RUNTIME_SOURCE"] = source
    os.execve(py, [py, sys.argv[0], *sys.argv[1:]], new_env)
