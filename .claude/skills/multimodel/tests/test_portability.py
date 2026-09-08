"""The package must stay liftable into any project: standard library only,
no domain vocabulary in identifiers, no reach outside its own directory.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

PACKAGE = Path(__file__).resolve().parents[1] / "src" / "multimodel"

# Identifiers that would mean a host project's domain had leaked in.
DOMAIN_WORDS = ("thesis", "portfolio", "ticker", "trade", "invest", "patient", "device", "dhf")

# The one third-party import, and the one place it may appear (lazily).
ALLOWED_THIRD_PARTY = {"yaml": "config.py"}


def sources() -> list[Path]:
    return sorted(PACKAGE.rglob("*.py"))


def _imports(tree: ast.AST):
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                yield alias.name.split(".")[0], node
        elif isinstance(node, ast.ImportFrom):
            if node.level == 0 and node.module:
                yield node.module.split(".")[0], node


def test_package_exists():
    assert sources(), "multimodel package is missing"


def test_only_stdlib_and_relative_imports():
    stdlib = set(sys.stdlib_module_names)
    offenders = []
    for path in sources():
        for name, _node in _imports(ast.parse(path.read_text(encoding="utf-8"))):
            if name in stdlib or name == "multimodel":
                continue
            if ALLOWED_THIRD_PARTY.get(name) == path.name:
                continue
            offenders.append(f"{path.name}: imports {name}")
    assert not offenders, "non-stdlib import in the portable layer: " + "; ".join(offenders)


def test_no_domain_vocabulary_in_identifiers():
    offenders = []
    for path in sources():
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            name = None
            if isinstance(node, ast.Name):
                name = node.id
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                name = node.name
            elif isinstance(node, ast.arg):
                name = node.arg
            if not name:
                continue
            for word in DOMAIN_WORDS:
                if word in name.lower():
                    offenders.append(f"{path.name}: identifier {name!r} contains {word!r}")
    assert not offenders, "domain vocabulary leaked: " + "; ".join(offenders)


def test_no_pipe_to_shell_in_skill_docs():
    """The install story points at vendor pages, never a pipe-to-shell one-liner."""
    import re
    skill = PACKAGE.parents[1]
    pattern = re.compile(r"curl\s+[^|\n]*\|\s*(sh|bash|zsh)\b")
    hits = [p.name for p in skill.rglob("*.md") if pattern.search(p.read_text(encoding="utf-8"))]
    assert not hits, f"pipe-to-shell instruction in: {hits}"
