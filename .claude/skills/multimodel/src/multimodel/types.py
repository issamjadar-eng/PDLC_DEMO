"""Core types for the multimodel layer.

Deliberately domain-agnostic. The vocabulary is limited to "ask a provider
something and get a structured answer back", which is why this package can be
lifted into any project unchanged.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass(frozen=True)
class Ask:
    """One request to one provider.

    `tag` is an opaque caller label echoed back on the Response. It is how a
    calling layer keeps track of *why* it asked — a review skill puts its lens
    name here, a test harness might put a case id. The multimodel layer never
    interprets it, which is precisely what keeps this package general.
    """

    prompt: str
    provider: str | None = None       # None = let the caller's dispatcher choose
    schema: dict[str, Any] | None = None
    tag: str = ""


@dataclass
class Response:
    """What a provider returned.

    `ok` is the only field callers should branch on for success. It is False
    whenever we did not get a usable answer — process failure, timeout, bad
    status, or a schema was requested and nothing conformant came back.

    **Fails closed by contract.** A Response with `ok=False` must never be
    interpreted as a meaningful negative answer; it means *no answer*. A caller
    that treats absence of a response as agreement has a bug, and that exact bug
    (a parse failure reading as "approved") is why this distinction is explicit.
    """

    provider: str
    ok: bool
    text: str = ""
    data: dict[str, Any] | None = None
    error: str | None = None
    raw: str = ""
    tag: str = ""
    usage: dict[str, Any] | None = None
    at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    @classmethod
    def failure(cls, provider: str, error: str, tag: str = "", raw: str = "") -> Response:
        return cls(provider=provider, ok=False, error=error, tag=tag, raw=raw)

    @classmethod
    def success(
        cls,
        provider: str,
        text: str,
        data: dict[str, Any] | None = None,
        tag: str = "",
        raw: str = "",
        usage: dict[str, Any] | None = None,
    ) -> Response:
        return cls(
            provider=provider, ok=True, text=text, data=data,
            tag=tag, raw=raw, usage=usage,
        )

    def to_dict(self) -> dict[str, Any]:
        """JSON-ready view for CLI consumers. `raw` is omitted — it can be huge."""
        return {
            "provider": self.provider,
            "ok": self.ok,
            "text": self.text,
            "data": self.data,
            "error": self.error,
            "tag": self.tag,
            "usage": self.usage,
            "at": self.at,
        }


@dataclass
class ProbeResult:
    """Outcome of a live liveness check against a provider.

    Distinct from `Provider.available()` on purpose. `available()` inspects local
    state — is the binary there, is a token file present — and is cheap enough to
    call before every run. A probe makes a real call and is the only thing that
    can prove the *service* will actually answer.

    The distinction is not academic: a vendor can stop serving an account tier
    while valid-looking credentials sit on disk. Every local check passes and
    every real call fails. Cached credentials prove nothing about entitlement.
    """

    provider: str
    ok: bool
    detail: str = ""
    elapsed_seconds: float | None = None
    structured: bool | None = None      # did structured output work?
    usage: dict[str, Any] | None = None

    @property
    def status(self) -> str:
        return "ok" if self.ok else "FAIL"


class ProviderNotAvailable(RuntimeError):
    """Raised when a provider is asked to work but cannot (missing CLI, no auth)."""
