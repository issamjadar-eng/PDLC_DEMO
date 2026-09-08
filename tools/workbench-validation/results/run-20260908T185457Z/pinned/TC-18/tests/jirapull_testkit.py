"""Test helpers for the jira-pull suite (uniquely named so several skills'
test dirs can share one pytest process without `conftest` name clashes)."""
from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
LIB_DIR = SKILL_ROOT / "lib"
FIXTURES = Path(__file__).resolve().parent / "fixtures"


class NetworkAccessInNonLiveTest(RuntimeError):
    """Raised when a unit/mocked test tries to open a network connection."""


def _ensure_lib_package() -> None:
    """Register this skill's `lib/` as the `lib` package if nothing else has.
    Mirrors the synthetic-package loader in test_drift_rules.py (the skill
    folder has a hyphen, so `import jira_pull.lib` is impossible)."""
    if "lib" not in sys.modules:
        pkg = types.ModuleType("lib")
        pkg.__path__ = [str(LIB_DIR)]
        sys.modules["lib"] = pkg


def load_lib_module(name: str):
    """Load `lib/<name>.py` as `lib.<name>` (idempotent)."""
    _ensure_lib_package()
    full = f"lib.{name}"
    if full in sys.modules:
        return sys.modules[full]
    spec = importlib.util.spec_from_file_location(full, LIB_DIR / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[full] = mod
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


def load_refresh_module():
    """Load `actions/refresh.py` under a private name (other skills also ship
    an `actions` package, so the module is loaded by path, not by name)."""
    name = "_jirapull_actions_refresh"
    if name in sys.modules:
        return sys.modules[name]
    _ensure_lib_package()
    load_lib_module("config")
    load_lib_module("normalize")
    spec = importlib.util.spec_from_file_location(name, SKILL_ROOT / "actions" / "refresh.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod
