"""Provider abstraction and shared CLI plumbing.

Every provider implements `ask()`. Adding a new backend should be one small
module plus a registry entry, never a change to callers.

The CLI helper here encodes three lessons paid for in real debugging time:

1. **Close stdin.** `capture_output=True` leaves stdin inherited, and an agentic
   CLI can read a piped stdin as extra instructions.
2. **Truncate errors from the TAIL.** These tools print a banner and echo the
   prompt first, so head-truncated diagnostics show only boilerplate and hide
   the actual failure at the end.
3. **Resolve binaries outside PATH.** Installers append to shell profiles that a
   running session has not re-read. A "not found" here silently drops a provider,
   which quietly weakens any quorum built on top.

And one lesson about *where* a vendor CLI runs:

4. **These CLIs are agents, not endpoints.** Given a working directory, they
   read from it to ground their answer. That is the point of a `project`
   workspace (the default): the agent may READ the project to gather context,
   and every adapter pins its CLI to read-only — a tool allowlist, a read-only
   sandbox, or a plan mode — so it can never write or execute. `isolated` runs
   the CLI in an empty temporary directory instead, for prompts that carry all
   their own context. The `verify` action proves both properties live.
"""

from __future__ import annotations

import shutil
import subprocess
import tempfile
import time
from abc import ABC, abstractmethod
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from .types import ProbeResult, Response

#: Where a vendor CLI may run. See `Provider.workspace`.
WORKSPACES = ("project", "isolated")
DEFAULT_WORKSPACE = "project"

# A liveness probe deliberately exercises the *same* path real work uses:
# a prompt plus a schema, parsed out of whatever envelope the CLI produces.
# Checking only that a process starts would miss auth, entitlement, and
# structured-output failures — which are the ones that actually bite.
PROBE_PROMPT = 'Respond with JSON only, exactly: {"ok": true}'
PROBE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {"ok": {"type": "boolean"}},
    "required": ["ok"],
}

# Where user-local installers commonly place binaries.
EXTRA_BIN_DIRS = (
    Path.home() / ".local" / "bin",
    Path.home() / "bin",
    Path.home() / ".grok" / "bin",
)


def resolve_binary(command: str, extra_dirs: tuple[Path, ...] = EXTRA_BIN_DIRS) -> str | None:
    """Find an executable, falling back to common user-local install dirs."""
    found = shutil.which(command)
    if found:
        return found
    for directory in extra_dirs:
        candidate = directory / command
        if candidate.exists():
            return str(candidate)
    return None


def tail(text: str, limit: int = 800) -> str:
    """Keep the END of a diagnostic, where the real error lives."""
    cleaned = text.strip()
    return cleaned if len(cleaned) <= limit else f"…{cleaned[-limit:]}"


class CliResult:
    """Outcome of running a CLI, normalised."""

    def __init__(self, ok: bool, stdout: str = "", stderr: str = "", error: str | None = None):
        self.ok = ok
        self.stdout = stdout
        self.stderr = stderr
        self.error = error


def run_cli(args: list[str], timeout: int, cwd: str | None = None) -> CliResult:
    """Run a CLI safely for agent use. Never raises; failures come back as data."""
    try:
        completed = subprocess.run(
            args,
            capture_output=True,
            text=True,
            # See lesson 1 in the module docstring.
            stdin=subprocess.DEVNULL,
            timeout=timeout,
            check=False,
            cwd=cwd,
        )
    except subprocess.TimeoutExpired:
        return CliResult(False, error=f"timed out after {timeout}s")
    except OSError as exc:
        return CliResult(False, error=f"failed to launch: {exc}")

    if completed.returncode != 0:
        combined = f"{completed.stdout}\n{completed.stderr}"
        return CliResult(
            False, completed.stdout, completed.stderr,
            error=f"exited {completed.returncode}: {tail(combined)}",
        )

    return CliResult(True, completed.stdout, completed.stderr)


class Provider(ABC):
    """One model backend."""

    def __init__(self, name: str, cfg: dict[str, Any]) -> None:
        self.name = name
        self.cfg = dict(cfg)

    @property
    def role(self) -> str:
        """Caller-defined grouping label. The multimodel layer does not interpret it."""
        return str(self.cfg.get("role", ""))

    @property
    def timeout(self) -> int:
        return int(self.cfg.get("timeout_seconds", 300))

    @property
    def workspace(self) -> str:
        """`project` (default) — the CLI runs at the project root with READ-ONLY
        tools and may gather context from the repository. `isolated` — it runs
        in an empty temp dir and sees only the prompt."""
        value = str(self.cfg.get("workspace", DEFAULT_WORKSPACE)).lower()
        return value if value in WORKSPACES else DEFAULT_WORKSPACE

    @contextmanager
    def workdir(self) -> Iterator[Path]:
        """The directory the vendor CLI is launched in. See `workspace`."""
        if self.workspace == "project":
            from .config import project_root  # local import: config has no deps on base
            yield project_root()
            return
        with tempfile.TemporaryDirectory(prefix="mm-work-") as tmp:
            yield Path(tmp)

    @abstractmethod
    def available(self) -> tuple[bool, str]:
        """Whether this provider can run right now, and why not if it cannot.

        Should test something meaningful rather than mere file presence where
        possible. A cached credential proves nothing about whether the service
        will still answer.
        """

    @abstractmethod
    def ask(self, prompt: str, schema: dict[str, Any] | None = None, tag: str = "") -> Response:
        """Send a prompt. With a schema, `Response.data` holds the parsed object.

        Must never raise for an expected failure — return `Response.failure`
        instead, so one bad provider cannot abort a whole fan-out.
        """

    def probe(self, timeout: int | None = None) -> ProbeResult:
        """Make a minimal REAL call to prove the service answers.

        `available()` can only inspect local state. This is the check that
        catches an expired session, a revoked entitlement, or a provider that
        silently stopped serving your account tier — none of which change
        anything on disk.

        Costs one small call per provider. Worth it before a long run; skip it
        (`--quick` in the CLI) when you only want a config sanity check.
        """
        ready, reason = self.available()
        if not ready:
            return ProbeResult(self.name, ok=False, detail=reason)

        original = self.cfg.get("timeout_seconds")
        if timeout is not None:
            self.cfg["timeout_seconds"] = timeout
        # A probe is a trivial prompt; it never needs — and must never get — the
        # project directory, whatever the provider's configured workspace is.
        original_workspace = self.cfg.get("workspace")
        self.cfg["workspace"] = "isolated"

        started = time.monotonic()
        try:
            response = self.ask(PROBE_PROMPT, schema=PROBE_SCHEMA, tag="probe")
        except Exception as exc:  # noqa: BLE001 - a probe must never explode
            return ProbeResult(
                self.name, ok=False, detail=f"unexpected error: {exc!r}",
                elapsed_seconds=round(time.monotonic() - started, 2),
            )
        finally:
            if timeout is not None:
                if original is None:
                    self.cfg.pop("timeout_seconds", None)
                else:
                    self.cfg["timeout_seconds"] = original
            if original_workspace is None:
                self.cfg.pop("workspace", None)
            else:
                self.cfg["workspace"] = original_workspace

        elapsed = round(time.monotonic() - started, 2)

        if not response.ok:
            return ProbeResult(
                self.name, ok=False, detail=response.error or "no response",
                elapsed_seconds=elapsed,
            )

        structured = isinstance(response.data, dict) and "ok" in response.data
        detail = "answered and returned structured output" if structured else (
            "answered, but structured output did NOT conform — schema-dependent "
            "callers will fail"
        )
        # A reply without conforming structure is a partial failure, not a pass:
        # every caller in this design depends on schema-shaped answers.
        return ProbeResult(
            self.name, ok=structured, detail=detail,
            elapsed_seconds=elapsed, structured=structured, usage=response.usage,
        )

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"<{type(self).__name__} name={self.name!r}>"
