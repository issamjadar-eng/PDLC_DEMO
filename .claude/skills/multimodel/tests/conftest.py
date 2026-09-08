"""pytest configuration — hermetic unit tests (socket guard on).

Adds the skill's own `src/` to the path so the package imports without an
install step, exactly as the CLI script does.
"""
from __future__ import annotations

import socket
import sys
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


class NetworkAccessBlocked(RuntimeError):
    """Raised when a test tries to open a socket."""


@pytest.fixture(autouse=True)
def _socket_guard(monkeypatch: pytest.MonkeyPatch):
    def _blocked(*_a, **_k):
        raise NetworkAccessBlocked("network access attempted from a hermetic unit test")
    monkeypatch.setattr(socket.socket, "connect", _blocked)
    monkeypatch.setattr(socket.socket, "connect_ex", _blocked)
    monkeypatch.setattr(socket, "create_connection", _blocked)
    yield


@pytest.fixture
def no_binaries(monkeypatch: pytest.MonkeyPatch):
    """Make every vendor CLI look absent, in every module that resolves one."""
    import multimodel.base as base
    import multimodel.providers.antigravity as agy
    import multimodel.providers.codex as codex
    import multimodel.providers.grok as grok

    for module in (base, agy, codex, grok):
        monkeypatch.setattr(module, "resolve_binary", lambda *_a, **_k: None)
