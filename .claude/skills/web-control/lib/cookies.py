"""Cookie extraction via CDP `Network.getCookies`.

Consumer-skill API:

    from lib.cookies import extract_cookies, cookies_to_header

    cookies = extract_cookies("https://example.atlassian.net/")
    header = cookies_to_header(cookies)
    # header -> "name1=val1; name2=val2; ..."

The cookies belong to Chrome's persistent jar — they are returned for the
given URL regardless of which tab is currently open. We attach to any
existing page tab to issue the CDP call; if Chrome has no page tabs we
create a blank `about:blank` tab and clean it up after.

The cookie jar is shared across the dedicated debug profile, so any sign-in
the user completes in that browser window is reusable by any consumer
skill that knows the target URL. Pair this with a "Remember me" sign-in so
the session cookie persists across browser restarts.
"""
from __future__ import annotations

from typing import Any

from .connect import Tab, connect_to_chrome
from .errors import WebControlError
from .platform import DEFAULT_DEBUG_PORT


def _normalize_url(url_or_domain: str) -> str:
    """Accept `example.atlassian.net`, `example.atlassian.net/wiki`, or a
    fully-qualified URL; return a fully-qualified URL with scheme."""
    s = url_or_domain.strip()
    if not s:
        raise WebControlError("empty URL/domain", recovery="Pass a domain or URL.")
    if "://" in s:
        return s
    return "https://" + s.lstrip("/")


def extract_cookies(
    url_or_domain: str,
    port: int = DEFAULT_DEBUG_PORT,
) -> list[dict[str, Any]]:
    """Return cookies in Chrome's debug jar that match the given URL.

    Uses CDP `Network.getCookies` with the `urls` filter — Chrome returns
    only cookies whose domain + path + secure flags would be sent on a
    request to that URL.

    Raises `ChromeNotRunning` if the debug port is unreachable.
    """
    target_url = _normalize_url(url_or_domain)
    chrome = connect_to_chrome(port=port)

    tabs = chrome.list_tabs()
    page_tabs = [t for t in tabs if t.type == "page"]
    created_tab: Tab | None = None
    if page_tabs:
        tab = page_tabs[0]
    else:
        created_tab = chrome.new_tab("about:blank")
        tab = created_tab

    try:
        with chrome.with_page(tab) as page:
            page.cmd("Network.enable")
            result = page.cmd("Network.getCookies", {"urls": [target_url]})
            return list(result.get("cookies", []))
    finally:
        if created_tab is not None:
            try:
                import urllib.request

                urllib.request.urlopen(
                    f"http://127.0.0.1:{port}/json/close/{created_tab.id}", timeout=2
                ).read()
            except Exception:
                pass


def cookies_to_header(cookies: list[dict[str, Any]]) -> str:
    """Render a CDP cookie list as a `Cookie:` header value.

    Format: `name1=value1; name2=value2`. Order follows input order.
    Skips entries with empty `name`.
    """
    parts: list[str] = []
    for c in cookies:
        name = c.get("name", "")
        if not name:
            continue
        value = c.get("value", "")
        parts.append(f"{name}={value}")
    return "; ".join(parts)


def cookies_for_domain(
    domain: str,
    port: int = DEFAULT_DEBUG_PORT,
) -> list[dict[str, Any]]:
    """Convenience wrapper — accept a bare domain; return cookies for `https://<domain>/`."""
    return extract_cookies(domain, port=port)
