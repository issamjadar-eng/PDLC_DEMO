"""pytest configuration for the jira-pull test suite — three evidence tiers.

Tiers (names are shared across the workbench's skills so a validation
report can say which kind of evidence each case produced):

  unit    (unmarked)             pure logic over in-memory fixtures
  mocked  @pytest.mark.mocked    real client code paths against canned
                                 Jira/Confluence payloads — hermetic
  live    @pytest.mark.live      runs against a real endpoint; opt-in via
                                 `--live` and needs a configured connection

A socket guard (autouse) makes any network attempt from a test that is NOT
marked `live` fail loudly, so a unit/mocked test can never silently reach
an enterprise endpoint. `live` tests are skipped unless `--live` is passed.

The MCP search call itself (`mcp__atlassian__searchJiraIssuesUsingJql`)
runs inside the agent's tool loop and is not callable from pytest — the
mocked tier covers the deterministic halves on either side of it
(JQL/cursor composition, page merge + dedupe, normalization, provenance).
"""
from __future__ import annotations

import socket
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from jirapull_testkit import FIXTURES, NetworkAccessInNonLiveTest  # noqa: E402

# ─── Tier plumbing ───────────────────────────────────────────────────────

LIVE_SKIP_REASON = "live endpoint tests are opt-in (--live) and need a configured connection"


def pytest_addoption(parser: pytest.Parser) -> None:
    try:
        parser.addoption(
            "--live",
            action="store_true",
            default=False,
            help="run tests marked `live` against real endpoints (default: skip)",
        )
    except ValueError:
        # A sibling skill's conftest already registered `--live` in this
        # pytest process (same semantics); sharing the option is intended.
        pass


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line(
        "markers",
        "mocked: hermetic test against a fake Jira/Confluence transport with canned payloads",
    )
    config.addinivalue_line(
        "markers",
        "live: runs against a real endpoint; requires configured connection, opt-in via `--live`",
    )


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    if config.getoption("--live"):
        return
    skip_live = pytest.mark.skip(reason=LIVE_SKIP_REASON)
    for item in items:
        if item.get_closest_marker("live"):
            item.add_marker(skip_live)


@pytest.fixture(autouse=True)
def _socket_guard(request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch):
    """Block real sockets unless the test is marked `live`."""
    if request.node.get_closest_marker("live"):
        yield
        return

    def _blocked(*_a, **_k):
        raise NetworkAccessInNonLiveTest(
            f"{request.node.nodeid}: network access attempted from a test that is not "
            "marked `live`. Unit/mocked tests must be hermetic — use canned fixtures "
            "under tests/fixtures/ or mark the test @pytest.mark.live."
        )

    monkeypatch.setattr(socket.socket, "connect", _blocked)
    monkeypatch.setattr(socket, "create_connection", _blocked)
    yield


@pytest.fixture
def atlassian_fixtures() -> Path:
    return FIXTURES / "atlassian"
