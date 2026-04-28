"""web-control error hierarchy with built-in recovery hints.

Each error subclass carries a recovery message so consumers can surface
actionable guidance to the user without re-implementing the diagnostic.
"""
from __future__ import annotations


class WebControlError(Exception):
    """Base class for all web-control errors. Includes a recovery hint."""

    recovery: str = (
        "Consult .claude/skills/web-control/README.md troubleshooting section."
    )

    def __init__(self, message: str, recovery: str | None = None) -> None:
        super().__init__(message)
        if recovery:
            self.recovery = recovery

    def render(self) -> str:
        """Render the error + recovery in a consistent format."""
        return f"web-control error: {self.args[0]}\n  -> {self.recovery}"


class ChromeNotInstalled(WebControlError):
    recovery = (
        "Run: /web-control setup (installs Chrome if missing). On macOS the "
        "skill uses your existing Chrome or installs via Homebrew. On WSL it "
        "installs google-chrome-stable via Google's official apt repo."
    )


class ProfileNotInitialized(WebControlError):
    recovery = (
        "Run: /web-control setup (creates the dedicated debug profile dir). "
        "On first launch you will be asked to sign in once with your "
        "corporate Google account."
    )


class ChromeNotRunning(WebControlError):
    recovery = (
        "Run: /web-control launch (starts the debug Chrome with the right flags)."
    )


class DebugPortInUse(WebControlError):
    recovery = (
        "Another process is already listening on the debug port. Either run "
        "/web-control stop to clean up, or pick a different port via the "
        "WEB_CONTROL_PORT environment variable."
    )


class SignInRequired(WebControlError):
    recovery = (
        "The dedicated debug Chrome is running but no corporate Google "
        "session is active. Run /web-control launch and complete sign-in in "
        "the visible browser window. The session persists across restarts."
    )


class UnsupportedPlatform(WebControlError):
    recovery = (
        "web-control supports macOS and Linux/WSL. On native Windows, run "
        "Claude Code under WSL — the Windows-side launcher is documented as "
        "a fallback only."
    )


class ChromeVersionTooOld(WebControlError):
    recovery = (
        "web-control requires Chrome 124+ (for --remote-allow-origins). "
        "Run /web-control setup to upgrade, or update via your platform "
        "package manager."
    )
