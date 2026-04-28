"""Accessibility-tree helpers — read body text and check sign-in state.

Google Docs renders body text in a canvas. To read it programmatically the
doc tab must have Screen Reader Mode enabled (Ctrl+Alt+Z), and the reader
queries the CDP a11y tree (Accessibility.getFullAXTree).
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from .input import keyboard_shortcut

if TYPE_CHECKING:
    from .connect import Page


def is_screen_reader_enabled(page: "Page") -> bool:
    """Detect whether Google Docs SR mode is on. Heuristic: the body
    innerText contains the announcement string when SR is on."""
    return bool(page.eval(
        "/Screen reader support enabled/i.test(document.body.innerText)"
    ))


def enable_screen_reader(page: "Page") -> None:
    """Toggle SR mode if not already on. Idempotent."""
    if is_screen_reader_enabled(page):
        return
    keyboard_shortcut(page, "Ctrl+Alt+Z")
    # Give Google Docs a moment to apply the toggle
    import time
    time.sleep(1.5)


def get_a11y_text(page: "Page", role_filter: tuple[str, ...] = ("StaticText",)) -> list[str]:
    """Return text-bearing nodes from the CDP a11y tree, filtered by role.

    Defaults to StaticText. Pass role_filter=() to get all named nodes.
    """
    page.cmd("Accessibility.enable")
    tree = page.cmd("Accessibility.getFullAXTree")
    out: list[str] = []
    for n in tree.get("nodes", []):
        role = (n.get("role") or {}).get("value", "")
        name = (n.get("name") or {}).get("value", "")
        if not name:
            continue
        if role_filter and role not in role_filter:
            continue
        out.append(name)
    return out


def is_signed_in(page: "Page") -> bool:
    """Heuristic: a Drive doc tab navigated under an authenticated session
    lands on /drive/home or /document/d/. An unauthenticated session
    redirects to accounts.google.com or workspace.google.com/products/drive."""
    url = page.eval("location.href") or ""
    if "accounts.google.com" in url:
        return False
    if "workspace.google.com/" in url and "/products/drive" in url:
        return False
    if "/drive/home" in url or "/document/d/" in url or "drive.google.com/drive/" in url:
        return True
    # Unknown — let the caller decide
    return None  # type: ignore[return-value]
