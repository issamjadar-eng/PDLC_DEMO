"""pytest configuration for the knowledge-pack-export test suite.

Tiers, named as in the workbench-validation manifest (`endpoint:`):
  unit (no marker) — pure logic, socket guard ON;  mocked — fake transport, guard ON;
  live — real endpoint, opt-in via `--live`, guard OFF. Nothing in this suite is live
  today; the guard makes hermeticity a hard property rather than a hope.
"""
from __future__ import annotations

import socket

import pytest

_TIER_RULE = ("network access attempted from a non-`live` test — unit and mocked tiers "
              "must be hermetic")


def pytest_addoption(parser: pytest.Parser) -> None:
    try:
        parser.addoption("--live", action="store_true", default=False,
                         help="run tests marked `live` against real endpoints")
    except ValueError:  # another skill's conftest already registered it (combined run)
        pass


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "mocked: hermetic test against a fake transport; no sockets")
    config.addinivalue_line("markers", "live: runs against a real endpoint; opt-in via `--live`")


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    if config.getoption("--live", default=False):
        return
    skip_live = pytest.mark.skip(
        reason="live endpoint tests are opt-in (--live) and need a configured connection")
    for item in items:
        if item.get_closest_marker("live"):
            item.add_marker(skip_live)


class NetworkAccessBlocked(RuntimeError):
    """Raised when a non-live test tries to open a socket."""


@pytest.fixture(autouse=True)
def _socket_guard(request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch):
    if request.node.get_closest_marker("live"):
        yield
        return

    def _blocked(*_a, **_k):
        raise NetworkAccessBlocked(_TIER_RULE)

    monkeypatch.setattr(socket.socket, "connect", _blocked)
    monkeypatch.setattr(socket.socket, "connect_ex", _blocked)
    monkeypatch.setattr(socket, "create_connection", _blocked)
    yield
