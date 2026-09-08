"""Test helpers for the web-control suite (uniquely named so several skills'
test dirs can share one pytest process without `conftest` name clashes).

The skill's `lib/` is loaded under a private alias (`_webcontrol_lib`)
because other skills also ship a top-level `lib` package; relative imports
inside the package still resolve because the alias is registered as a real
package in `sys.modules`."""
from __future__ import annotations

import importlib
import importlib.util
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
LIB_ALIAS = "_webcontrol_lib"


class NetworkAccessInNonLiveTest(RuntimeError):
    """Raised when a unit/mocked test tries to open a network connection."""


def load_webcontrol_lib():
    """Import this skill's `lib` package as `_webcontrol_lib` (idempotent)."""
    if LIB_ALIAS in sys.modules:
        return sys.modules[LIB_ALIAS]
    pkg_init = SKILL_ROOT / "lib" / "__init__.py"
    spec = importlib.util.spec_from_file_location(
        LIB_ALIAS, pkg_init, submodule_search_locations=[str(pkg_init.parent)]
    )
    pkg = importlib.util.module_from_spec(spec)
    sys.modules[LIB_ALIAS] = pkg
    spec.loader.exec_module(pkg)  # type: ignore[union-attr]
    return pkg


def load_webcontrol_module(name: str):
    load_webcontrol_lib()
    return importlib.import_module(f"{LIB_ALIAS}.{name}")
