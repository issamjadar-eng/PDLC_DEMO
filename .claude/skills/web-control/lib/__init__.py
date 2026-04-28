"""web-control — Chrome browser automation as shared infrastructure.

Consumer skills import from this package to get a CDP-connected Chrome session
under the user's corporate Google identity, without managing Chrome lifecycle
themselves.

Public API surface:
    from web_control.lib import (
        connect_to_chrome,    # connect.py
        find_tab,
        with_page,
        send_key,             # input.py
        click_at,
        type_text,
        keyboard_shortcut,
        get_a11y_text,        # a11y.py
        is_signed_in,
        WebControlError,      # errors.py
        ChromeNotInstalled,
        ProfileNotInitialized,
        ChromeNotRunning,
        DebugPortInUse,
        SignInRequired,
    )
"""
from .errors import (
    WebControlError,
    ChromeNotInstalled,
    ProfileNotInitialized,
    ChromeNotRunning,
    DebugPortInUse,
    SignInRequired,
    UnsupportedPlatform,
)
from .platform import (
    detect_platform,
    chrome_binary_path,
    profile_dir,
    DEFAULT_DEBUG_PORT,
    REQUIRED_CHROME_FLAGS,
)
from .lifecycle import (
    is_chrome_running,
    is_debug_port_listening,
    chrome_pids,
    kill_chrome,
)
from .connect import (
    connect_to_chrome,
    find_tab,
    with_page,
    list_tabs,
    new_tab,
)
from .input import (
    send_key,
    click_at,
    type_text,
    keyboard_shortcut,
    Modifiers,
)
from .a11y import (
    get_a11y_text,
    is_signed_in,
)

__all__ = [
    "WebControlError",
    "ChromeNotInstalled",
    "ProfileNotInitialized",
    "ChromeNotRunning",
    "DebugPortInUse",
    "SignInRequired",
    "UnsupportedPlatform",
    "detect_platform",
    "chrome_binary_path",
    "profile_dir",
    "DEFAULT_DEBUG_PORT",
    "REQUIRED_CHROME_FLAGS",
    "is_chrome_running",
    "is_debug_port_listening",
    "chrome_pids",
    "kill_chrome",
    "connect_to_chrome",
    "find_tab",
    "with_page",
    "list_tabs",
    "new_tab",
    "send_key",
    "click_at",
    "type_text",
    "keyboard_shortcut",
    "Modifiers",
    "get_a11y_text",
    "is_signed_in",
]
