"""pytest configuration for the docflow test suite.

Evidence tiers: `mocked` / `live` markers, `--live` opt-in, and an autouse socket
guard that blocks any network access from a test not marked `live` — the docflow
suite is hermetic (endpoint: none).
"""
from __future__ import annotations

import socket

import pytest


class NetworkAccessBlocked(RuntimeError):
    pass


def pytest_addoption(parser):
    try:
        parser.addoption("--live", action="store_true", default=False,
                         help="run tests marked `live` (need a configured connection)")
    except ValueError:  # another skill's conftest in the same session already added it
        pass


def pytest_configure(config):
    config.addinivalue_line("markers", "mocked: hermetic test against a fake transport with canned payloads")
    config.addinivalue_line("markers", "live: runs against a real endpoint; requires configured connection, opt-in via --live")


@pytest.fixture(autouse=True)
def _socket_guard(request, monkeypatch):
    if request.node.get_closest_marker("live"):
        if not request.config.getoption("--live", default=False):
            pytest.skip("live endpoint tests are opt-in (--live) and need a configured connection")
        yield
        return

    def _blocked(*_a, **_k):
        raise NetworkAccessBlocked(
            "network access from a non-`live` test — unit/mocked tiers must be hermetic")

    monkeypatch.setattr(socket.socket, "connect", _blocked)
    monkeypatch.setattr(socket.socket, "connect_ex", _blocked)
    monkeypatch.setattr(socket, "create_connection", _blocked)
    yield
