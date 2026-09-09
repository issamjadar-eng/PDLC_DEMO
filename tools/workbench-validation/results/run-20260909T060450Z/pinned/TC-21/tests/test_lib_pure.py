"""Unit + live-placeholder tests for web-control's pure library surface.

Unit tier (unmarked, hermetic): URL normalisation, `Cookie:` header
rendering, and keyboard-shortcut parsing driven through a fake CDP page
that records the commands it would have sent. Nothing here touches Chrome.

Live tier (`@pytest.mark.live`, opt-in via `--live`): a debug-Chrome
reachability smoke. Everything else in this skill — tab discovery, CDP
input, accessibility-tree reads, cookie extraction from the persistent
jar — is browser-driven and is covered end-to-end by
`tests/test-lifecycle.sh`, not by pytest.

Run:
    uv run --no-project --with pytest -- pytest .claude/skills/web-control/tests -q
"""
from __future__ import annotations

import socket

import pytest

from webcontrol_testkit import NetworkAccessInNonLiveTest, load_webcontrol_module

cookies = load_webcontrol_module("cookies")
inputmod = load_webcontrol_module("input")
errors = load_webcontrol_module("errors")


# ─── cookies.py ──────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "given, expected",
    [
        ("example.atlassian.net", "https://example.atlassian.net"),
        ("example.atlassian.net/wiki", "https://example.atlassian.net/wiki"),
        ("/example.atlassian.net", "https://example.atlassian.net"),
        ("http://localhost:9222/json", "http://localhost:9222/json"),
        ("  https://example.atlassian.net/  ", "https://example.atlassian.net/"),
    ],
)
def test_normalize_url(given: str, expected: str) -> None:
    assert cookies._normalize_url(given) == expected


def test_normalize_url_rejects_empty() -> None:
    with pytest.raises(errors.WebControlError):
        cookies._normalize_url("   ")


def test_cookies_to_header_preserves_order_and_skips_nameless() -> None:
    jar = [
        {"name": "cloud.session.token", "value": "abc"},
        {"name": "", "value": "ignored"},
        {"name": "atlassian.xsrf.token", "value": "x=y"},
        {"value": "no-name-key"},
    ]
    assert cookies.cookies_to_header(jar) == "cloud.session.token=abc; atlassian.xsrf.token=x=y"


def test_cookies_to_header_empty_jar() -> None:
    assert cookies.cookies_to_header([]) == ""


# ─── input.py (fake CDP page) ────────────────────────────────────────────


class FakePage:
    """Records CDP commands instead of sending them."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, dict]] = []

    def cmd(self, method: str, params: dict | None = None) -> dict:
        self.calls.append((method, dict(params or {})))
        return {}


def test_keyboard_shortcut_letter_with_modifiers() -> None:
    page = FakePage()
    inputmod.keyboard_shortcut(page, "Ctrl+Alt+M")
    assert [m for m, _ in page.calls] == ["Input.dispatchKeyEvent"] * 2
    down, up = (p for _, p in page.calls)
    assert down["type"] == "keyDown" and up["type"] == "keyUp"
    assert down["modifiers"] == inputmod.Modifiers.CTRL | inputmod.Modifiers.ALT
    assert down["key"] == "m" and down["code"] == "KeyM"


def test_keyboard_shortcut_digit_and_cmd_alias() -> None:
    page = FakePage()
    inputmod.keyboard_shortcut(page, "cmd+1")
    down = page.calls[0][1]
    assert down["modifiers"] == inputmod.Modifiers.META
    assert down["code"] == "Digit1"


@pytest.mark.parametrize("combo", ["", "Ctrl+", "Ctrl+Shift"])
def test_keyboard_shortcut_rejects_modifier_only(combo: str) -> None:
    with pytest.raises(ValueError):
        inputmod.keyboard_shortcut(FakePage(), combo)


# ─── Tier plumbing self-test ─────────────────────────────────────────────


def test_socket_guard_blocks_network_in_unit_tier() -> None:
    with pytest.raises(NetworkAccessInNonLiveTest):
        socket.create_connection(("example.invalid", 443), timeout=0.1)


@pytest.mark.live
def test_live_debug_chrome_reachable() -> None:
    """Live tier placeholder: with `--live`, requires a running debug Chrome
    on the default port; skips with a reason otherwise so the report never
    shows a silent PASS for an unexercised endpoint."""
    platform = load_webcontrol_module("platform")
    lifecycle = load_webcontrol_module("lifecycle")
    port = platform.DEFAULT_DEBUG_PORT
    if not lifecycle.is_debug_port_listening(port):
        pytest.skip(f"no live connection configured (no debug Chrome on port {port})")
    connect = load_webcontrol_module("connect")
    chrome = connect.connect_to_chrome(port=port)
    assert isinstance(chrome.list_tabs(), list)
