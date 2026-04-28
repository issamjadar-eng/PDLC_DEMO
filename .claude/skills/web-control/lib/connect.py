"""DevTools Protocol connection helpers.

Consumer-skill API:
    from web_control.lib import connect_to_chrome, find_tab, with_page

    chrome = connect_to_chrome()
    tab = chrome.find_tab(lambda t: "drive.google.com" in t["url"])
    with chrome.with_page(tab) as page:
        page.eval("location.href")
        page.click(x, y)
"""
from __future__ import annotations

import contextlib
import json
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Callable, Iterator

from .errors import ChromeNotRunning, DebugPortInUse
from .lifecycle import is_debug_port_listening
from .platform import DEFAULT_DEBUG_PORT


def _http_json(url: str, timeout: float = 5.0, method: str = "GET") -> Any:
    req = urllib.request.Request(url, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.URLError as exc:
        raise ChromeNotRunning(f"could not reach {url}: {exc}")


@dataclass
class Tab:
    id: str
    title: str
    url: str
    type: str
    webSocketDebuggerUrl: str

    @classmethod
    def from_dict(cls, d: dict) -> "Tab":
        return cls(
            id=d.get("id", ""),
            title=d.get("title", ""),
            url=d.get("url", ""),
            type=d.get("type", ""),
            webSocketDebuggerUrl=d.get("webSocketDebuggerUrl", ""),
        )


class Page:
    """Live DevTools Protocol session against a single tab."""

    def __init__(self, ws) -> None:
        self.ws = ws
        self._next_id = 0

    def cmd(self, method: str, params: dict | None = None, timeout: float = 30.0) -> dict:
        self._next_id += 1
        msg_id = self._next_id
        self.ws.send(json.dumps({"id": msg_id, "method": method, "params": params or {}}))
        deadline = time.time() + timeout
        while time.time() < deadline:
            raw = self.ws.recv()
            resp = json.loads(raw)
            if resp.get("id") == msg_id:
                if "error" in resp:
                    raise RuntimeError(f"{method} error: {resp['error']}")
                return resp.get("result", {})
        raise TimeoutError(f"timeout waiting for {method} response")

    def eval(self, expression: str, return_by_value: bool = True) -> Any:
        r = self.cmd("Runtime.evaluate", {"expression": expression, "returnByValue": return_by_value})
        return r.get("result", {}).get("value")

    def navigate(self, url: str) -> None:
        self.cmd("Page.navigate", {"url": url})

    def wait_for_url(self, predicate: Callable[[str], bool], timeout: float = 30.0, poll: float = 0.5) -> str:
        deadline = time.time() + timeout
        last = ""
        while time.time() < deadline:
            url = self.eval("location.href") or ""
            last = url
            if predicate(url):
                return url
            time.sleep(poll)
        raise TimeoutError(f"URL did not satisfy predicate within {timeout}s; last={last!r}")

    def wait_ready(self, timeout: float = 30.0) -> None:
        deadline = time.time() + timeout
        while time.time() < deadline:
            if self.eval("document.readyState") == "complete":
                return
            time.sleep(0.3)
        raise TimeoutError("page did not reach readyState=complete")


class Chrome:
    """Connection handle. Use connect_to_chrome() to obtain one."""

    def __init__(self, host: str = "127.0.0.1", port: int = DEFAULT_DEBUG_PORT) -> None:
        self.host = host
        self.port = port
        self._base = f"http://{host}:{port}"

    @property
    def version(self) -> dict:
        return _http_json(f"{self._base}/json/version")

    def list_tabs(self) -> list[Tab]:
        return [Tab.from_dict(d) for d in _http_json(f"{self._base}/json")]

    def find_tab(self, predicate: Callable[[Tab], bool]) -> Tab | None:
        for t in self.list_tabs():
            if predicate(t):
                return t
        return None

    def new_tab(self, url: str) -> Tab:
        # The PUT /json/new?<url> endpoint creates a tab and returns its descriptor
        d = _http_json(f"{self._base}/json/new?{url}", method="PUT")
        return Tab.from_dict(d)

    @contextlib.contextmanager
    def with_page(self, tab: Tab) -> Iterator[Page]:
        # websocket-client is required for the live channel.
        try:
            import websocket  # type: ignore
        except ImportError as exc:
            raise WebControlError(  # noqa: F821 — re-imported for runtime
                "websocket-client not installed",
                recovery="Run: pip install websocket-client (or use web-control's bundled venv)",
            ) from exc
        ws = websocket.create_connection(tab.webSocketDebuggerUrl, timeout=20)
        try:
            page = Page(ws)
            page.cmd("Page.enable")
            page.cmd("Runtime.enable")
            yield page
        finally:
            try:
                ws.close()
            except Exception:
                pass


def connect_to_chrome(host: str = "127.0.0.1", port: int = DEFAULT_DEBUG_PORT, retries: int = 3) -> Chrome:
    """Establish a connection. Returns a Chrome handle.

    Raises ChromeNotRunning if the debug port doesn't respond.
    """
    last_err: Exception | None = None
    for _ in range(retries):
        if is_debug_port_listening(port=port, host=host):
            try:
                chrome = Chrome(host=host, port=port)
                _ = chrome.version  # verify protocol response
                return chrome
            except Exception as exc:
                last_err = exc
        time.sleep(1.0)
    if last_err:
        raise ChromeNotRunning(f"debug port {host}:{port} not responding: {last_err}")
    raise ChromeNotRunning(f"debug port {host}:{port} not responding")


# Top-level convenience aliases for the documented surface
def list_tabs(host: str = "127.0.0.1", port: int = DEFAULT_DEBUG_PORT) -> list[Tab]:
    return connect_to_chrome(host, port).list_tabs()


def find_tab(predicate: Callable[[Tab], bool], host: str = "127.0.0.1", port: int = DEFAULT_DEBUG_PORT) -> Tab | None:
    return connect_to_chrome(host, port).find_tab(predicate)


def new_tab(url: str, host: str = "127.0.0.1", port: int = DEFAULT_DEBUG_PORT) -> Tab:
    return connect_to_chrome(host, port).new_tab(url)


@contextlib.contextmanager
def with_page(tab: Tab, host: str = "127.0.0.1", port: int = DEFAULT_DEBUG_PORT) -> Iterator[Page]:
    chrome = connect_to_chrome(host, port)
    with chrome.with_page(tab) as page:
        yield page


# Re-export the error class so callers don't have to know the lib structure
from .errors import WebControlError  # noqa: E402
