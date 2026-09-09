"""pytest configuration — hermetic unit tests (socket guard on)."""
from __future__ import annotations

import socket

import pytest


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
