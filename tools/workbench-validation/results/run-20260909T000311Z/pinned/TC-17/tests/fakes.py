"""Fake transports for the `mocked` tier — canned Jira/Confluence responses.

The code under test reaches Atlassian through `urllib.request.urlopen`
(REST + cookie bridge) and through the lazily imported
`lib.attachments.extract_confluence_cookies`. These helpers replace both
seams with deterministic fakes; no socket is ever opened (the conftest
socket guard would raise if one were).

Usage:

    def test_x(monkeypatch):
        install_fake_cookie_bridge(monkeypatch, cookie="fake=cookie")
        install_fake_urlopen(monkeypatch, [FakeResponse.from_fixture("jira_search_two_issues.json")])
        ...
"""
from __future__ import annotations

import io
import json
import sys
import types
import urllib.error
import urllib.request
from pathlib import Path
from typing import Callable, Iterable

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "atlassian"


def load_fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


class FakeResponse(io.BytesIO):
    """Minimal stand-in for the object `urlopen` returns (context manager +
    `.read()` + `.status`)."""

    def __init__(self, payload: bytes, status: int = 200, url: str = ""):
        super().__init__(payload)
        self.status = status
        self.url = url

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, *exc) -> None:
        self.close()

    @classmethod
    def from_fixture(cls, name: str, status: int = 200) -> "FakeResponse":
        return cls(json.dumps(load_fixture(name)).encode("utf-8"), status=status)


def http_error(status: int, reason: str, url: str = "https://example.atlassian.net") -> urllib.error.HTTPError:
    return urllib.error.HTTPError(url, status, reason, hdrs=None, fp=io.BytesIO(b""))  # type: ignore[arg-type]


def install_fake_urlopen(
    monkeypatch,
    responses: Iterable[FakeResponse | Exception],
    *,
    seen: list | None = None,
) -> list:
    """Replace `urllib.request.urlopen` with a queue of canned responses.
    Each call pops the next item; an `Exception` item is raised instead of
    returned. Every `Request` (or URL string) passed in is appended to
    `seen` so tests can assert on the URL / headers that were used."""
    queue = list(responses)
    seen = seen if seen is not None else []

    def _fake_urlopen(req, *args, **kwargs):
        seen.append(req)
        if not queue:
            raise AssertionError("fake urlopen: no more canned responses")
        item = queue.pop(0)
        if isinstance(item, Exception):
            raise item
        return item

    monkeypatch.setattr(urllib.request, "urlopen", _fake_urlopen)
    return seen


def fake_attachments_module(
    *,
    cookie: str | Callable[[str], str] | Exception = "fake=cookie",
    list_attachments: Callable | None = None,
) -> types.ModuleType:
    """Build a fake `lib.attachments` module. `cookie` may be a header
    string, a callable, or an Exception instance to raise (cookie-bridge
    failure)."""
    mod = types.ModuleType("lib.attachments")

    def _extract(url: str) -> str:
        if isinstance(cookie, Exception):
            raise cookie
        if callable(cookie):
            return cookie(url)
        return cookie

    mod.extract_confluence_cookies = _extract  # type: ignore[attr-defined]
    if list_attachments is not None:
        mod.list_attachments = list_attachments  # type: ignore[attr-defined]
    return mod


def install_fake_cookie_bridge(monkeypatch, **kwargs) -> types.ModuleType:
    """Install a fake `lib.attachments` into `sys.modules` for the duration
    of the test (restored by monkeypatch). This is the seam the code under
    test resolves via `from lib.attachments import ...`, so patching here is
    order-independent regardless of which module object other tests
    imported first."""
    mod = fake_attachments_module(**kwargs)
    monkeypatch.setitem(sys.modules, "lib.attachments", mod)
    return mod
