"""Keyboard / mouse / text-input helpers, layered on a Page.

CDP modifier bitfield: Alt=1, Ctrl=2, Meta=4, Shift=8.
Common gotcha: Ctrl+Alt = 3 (NOT 6 — 6 is Meta+Ctrl). See task 116
probe scripts for the bug-find.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .connect import Page


class Modifiers:
    NONE = 0
    ALT = 1
    CTRL = 2
    META = 4
    SHIFT = 8


def send_key(page: "Page", key: str, code: str, vk: int, modifiers: int = 0) -> None:
    """Send a single keyDown + keyUp pair."""
    page.cmd("Input.dispatchKeyEvent", {
        "type": "keyDown",
        "modifiers": modifiers,
        "key": key,
        "code": code,
        "windowsVirtualKeyCode": vk,
    })
    page.cmd("Input.dispatchKeyEvent", {
        "type": "keyUp",
        "modifiers": modifiers,
        "key": key,
        "code": code,
        "windowsVirtualKeyCode": vk,
    })


def click_at(page: "Page", x: float, y: float, button: str = "left") -> None:
    """Single click at (x, y)."""
    page.cmd("Input.dispatchMouseEvent", {
        "type": "mousePressed", "x": x, "y": y, "button": button, "clickCount": 1,
    })
    page.cmd("Input.dispatchMouseEvent", {
        "type": "mouseReleased", "x": x, "y": y, "button": button, "clickCount": 1,
    })


def type_text(page: "Page", text: str) -> None:
    """Insert text at the current focus position. Uses Input.insertText
    which avoids per-key dispatching and works with IME-aware editors
    like Google Docs."""
    page.cmd("Input.insertText", {"text": text})


# Common keyboard shortcuts ----------------------------------------------------

# Single-key helpers
def press_enter(page: "Page") -> None:
    send_key(page, "Enter", "Enter", 13)


def press_escape(page: "Page") -> None:
    send_key(page, "Escape", "Escape", 27)


def press_tab(page: "Page", shift: bool = False) -> None:
    mods = Modifiers.SHIFT if shift else 0
    send_key(page, "Tab", "Tab", 9, modifiers=mods)


def select_all(page: "Page") -> None:
    """Ctrl+A (or Cmd+A on macOS)."""
    send_key(page, "a", "KeyA", 65, modifiers=Modifiers.CTRL)


def keyboard_shortcut(page: "Page", combo: str) -> None:
    """Friendly shortcut interface, e.g. 'Ctrl+Alt+M', 'Ctrl+A'.

    Recognized modifiers: Ctrl, Alt, Shift, Meta (case-insensitive).
    The non-modifier final token is treated as the key.
    """
    parts = [p.strip() for p in combo.split("+") if p.strip()]
    if not parts:
        raise ValueError(f"empty shortcut: {combo!r}")
    mods = 0
    key_token: str | None = None
    mod_map = {"ctrl": Modifiers.CTRL, "alt": Modifiers.ALT, "shift": Modifiers.SHIFT, "meta": Modifiers.META, "cmd": Modifiers.META}
    for p in parts:
        k = p.lower()
        if k in mod_map:
            mods |= mod_map[k]
        else:
            key_token = p
    if key_token is None:
        raise ValueError(f"shortcut {combo!r} has only modifiers, no key")

    # Map the key to (key, code, vk). Letter keys are easy.
    if len(key_token) == 1 and key_token.isalpha():
        letter = key_token.lower()
        send_key(page, letter, f"Key{letter.upper()}", ord(letter.upper()), modifiers=mods)
        return
    if len(key_token) == 1 and key_token.isdigit():
        d = key_token
        send_key(page, d, f"Digit{d}", ord(d), modifiers=mods)
        return

    # Named keys
    named = {
        "Enter": ("Enter", "Enter", 13),
        "Escape": ("Escape", "Escape", 27),
        "Esc": ("Escape", "Escape", 27),
        "Tab": ("Tab", "Tab", 9),
        "Space": (" ", "Space", 32),
        "Backspace": ("Backspace", "Backspace", 8),
        "Delete": ("Delete", "Delete", 46),
        "Home": ("Home", "Home", 36),
        "End": ("End", "End", 35),
    }
    if key_token in named:
        k, c, vk = named[key_token]
        send_key(page, k, c, vk, modifiers=mods)
        return

    raise ValueError(f"unrecognized key in shortcut: {key_token!r}")
