import os
import shutil


class AuthError(RuntimeError):
    pass


def preflight() -> None:
    if os.environ.get("ANTHROPIC_API_KEY"):
        raise AuthError(
            "ANTHROPIC_API_KEY is set. project-console supports Claude Pro/Max "
            "OAuth only. Unset it and retry:\n    unset ANTHROPIC_API_KEY"
        )
    if shutil.which("claude") is None:
        raise AuthError(
            "Claude Code CLI ('claude') was not found on PATH. Install Claude "
            "Code and run 'claude login' first."
        )
