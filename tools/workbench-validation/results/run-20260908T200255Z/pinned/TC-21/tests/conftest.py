"""pytest configuration for the web-control test suite — three evidence tiers.

Tiers (names are shared across the workbench's skills so a validation
report can say which kind of evidence each case produced):

  unit    (unmarked)             pure logic — URL/cookie/shortcut parsing
                                 against fake page objects
  mocked  @pytest.mark.mocked    real code paths against a fake CDP/HTTP
                                 transport with canned payloads — hermetic
  live    @pytest.mark.live      needs a running debug Chrome / real
                                 endpoint; opt-in via `--live`

A socket guard (autouse) makes any network attempt from a test that is NOT
marked `live` fail loudly. `live` tests are skipped unless `--live` is
passed. The shell suite `tests/test-lifecycle.sh` remains the end-to-end
lifecycle check (its `--no-live` flag is the same idea for bash).

The skill's `lib/` is loaded under a private alias (`_webcontrol_lib`)
because other skills also ship a top-level `lib` package; relative imports
inside the package still resolve because the alias is registered as a real
package in `sys.modules`.
"""
from __future__ import annotations

import socket
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from webcontrol_testkit import NetworkAccessInNonLiveTest  # noqa: E402

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
            "marked `live`. Unit/mocked tests must be hermetic — use fake page/transport "
            "objects or mark the test @pytest.mark.live."
        )

    monkeypatch.setattr(socket.socket, "connect", _blocked)
    monkeypatch.setattr(socket, "create_connection", _blocked)
    yield
