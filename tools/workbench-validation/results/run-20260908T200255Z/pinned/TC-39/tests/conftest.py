"""pytest configuration for the change-control test suite — evidence tiers.

Every test in this suite belongs to one of three tiers, named the same way
here, in the workbench-validation manifest (`endpoint:`), and in the
validation report:

  unit    (no marker)   pure logic; no endpoint; socket guard ON
  mocked  @mocked       hermetic run of the real client code paths against a
                        fake Jira/Confluence transport with canned payloads
                        (tests/fixtures/atlassian/); socket guard ON
  live    @live         runs against a real endpoint; opt-in via `--live` and
                        needs a configured connection (project.yml
                        change_control.jira.base_url); socket guard OFF

The socket guard makes the hermeticity rule enforceable: a `unit` or `mocked`
test that opens a socket is a defect, not a flake. A `live` test that does is
expected.
"""
from __future__ import annotations

import socket

import pytest

_TIER_RULE = (
    "network access attempted from a non-`live` test — unit and mocked tiers "
    "must be hermetic (mark the test `@pytest.mark.live` only if it is meant "
    "to hit a real endpoint; otherwise mock the transport via tests/fakes.py)"
)


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--live",
        action="store_true",
        default=False,
        help="run tests marked `live` against real endpoints (needs a "
             "configured connection in project.yml change_control.jira)",
    )


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line(
        "markers",
        "mocked: hermetic test against a fake Jira/Confluence transport with "
        "canned payloads (tests/fixtures/atlassian/); no sockets",
    )
    config.addinivalue_line(
        "markers",
        "live: runs against a real endpoint; requires a configured connection, "
        "opt-in via `--live`",
    )
    config.addinivalue_line(
        "markers",
        "freeze_gate: evidence for the frozen-document edit block (WUN-29); "
        "EXPECTED TO FAIL while hooks/pre_tool_use_frozen.py is a stub — run "
        "with `-m freeze_gate` as its own validation case and exclude it from "
        "the main suite with `-m 'not freeze_gate'`",
    )


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    if config.getoption("--live"):
        return
    skip_live = pytest.mark.skip(
        reason="live endpoint tests are opt-in (--live) and need a configured connection"
    )
    for item in items:
        if item.get_closest_marker("live"):
            item.add_marker(skip_live)


class NetworkAccessBlocked(RuntimeError):
    """Raised when a non-live test tries to open a socket."""


@pytest.fixture(autouse=True)
def _socket_guard(request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch):
    """Block socket connections for every test not marked `live`."""
    if request.node.get_closest_marker("live"):
        yield
        return

    def _blocked(*_args, **_kwargs):
        raise NetworkAccessBlocked(_TIER_RULE)

    monkeypatch.setattr(socket.socket, "connect", _blocked)
    monkeypatch.setattr(socket.socket, "connect_ex", _blocked)
    monkeypatch.setattr(socket, "create_connection", _blocked)
    yield
