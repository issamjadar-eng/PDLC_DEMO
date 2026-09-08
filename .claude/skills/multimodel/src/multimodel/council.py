"""The Council — fan a prompt out across independent model providers.

The point of a council is *uncorrelated* error. One model is one set of priors;
asking it to check its own reasoning mostly produces agreement with itself.
Independently-trained models are the cheapest available source of genuine
disagreement.

This layer stays domain-agnostic. It knows how to dispatch work across providers
and hand back structured answers. What the answers *mean* — whether an argument
survives, whether a design holds up, whether a finding is real — belongs to the
caller.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from typing import Any

from .base import Provider
from .registry import build_provider
from .types import Ask, ProbeResult, Response


class Council:
    """A set of providers that can be asked things, together or individually."""

    def __init__(self, providers: list[Provider], skipped: dict[str, str] | None = None) -> None:
        self.providers = providers
        # Config entries that did not become providers, with the reason. Kept so
        # a typo in `type:` or a disabled entry is visible rather than silent.
        self.skipped: dict[str, str] = dict(skipped or {})

    # -- construction --------------------------------------------------------

    @classmethod
    def from_config(
        cls,
        config: dict[str, Any],
        role: str | None = None,
        include_disabled: bool = False,
        only: list[str] | None = None,
    ) -> Council:
        """Build from a parsed config mapping.

        Expects ``{"providers": {name: {...}}}``. Each entry needs a ``type``
        (adapter key) or falls back to using its own name as the type, so an
        entry named ``grok`` needs no redundant ``type: grok``.

        `only` restricts to the named providers (still subject to `enabled`
        unless `include_disabled`).
        """
        providers: list[Provider] = []
        skipped: dict[str, str] = {}
        for name, cfg in (config.get("providers") or {}).items():
            cfg = cfg or {}
            if only is not None and name not in only:
                continue
            if not include_disabled and not cfg.get("enabled", False):
                skipped[name] = "disabled (enabled: false)"
                continue
            if role is not None and cfg.get("role") != role:
                skipped[name] = f"role {cfg.get('role')!r} != {role!r}"
                continue
            provider = build_provider(name, cfg)
            if provider is None:
                skipped[name] = f"no adapter for type {cfg.get('type', name)!r}"
                continue
            providers.append(provider)
        return cls(providers, skipped)

    # -- inspection ----------------------------------------------------------

    @property
    def names(self) -> list[str]:
        return [p.name for p in self.providers]

    def get(self, name: str) -> Provider | None:
        return next((p for p in self.providers if p.name == name), None)

    def availability(self) -> dict[str, tuple[bool, str]]:
        """Per-provider readiness. Cheap enough to call before a run."""
        return {p.name: p.available() for p in self.providers}

    def ready(self) -> list[Provider]:
        return [p for p in self.providers if p.available()[0]]

    def probe_all(self, timeout: int = 90, max_workers: int = 4) -> list[ProbeResult]:
        """Live-check every provider in parallel.

        Costs one small call each. This is the only check that can catch a
        revoked entitlement or an expired session, since neither changes
        anything on disk.
        """
        if not self.providers:
            return []
        workers = max(1, min(max_workers, len(self.providers)))
        with ThreadPoolExecutor(max_workers=workers) as pool:
            return list(pool.map(lambda p: p.probe(timeout=timeout), self.providers))

    # -- dispatch ------------------------------------------------------------

    def distribute(self, tags: list[str]) -> list[tuple[str, str]]:
        """Assign tags to providers round-robin. Returns (provider_name, tag).

        Deterministic on purpose: a stable tag→provider mapping keeps per-tag
        accuracy comparable across runs. The tradeoff is that a provider's
        weakness on its fixed tag becomes a blind spot no one else covers, so
        callers tracking long-run accuracy may want to rotate the offset once
        they have enough history to notice.
        """
        if not self.providers:
            return []
        return [
            (self.providers[i % len(self.providers)].name, tag)
            for i, tag in enumerate(tags)
        ]

    def run(self, asks: list[Ask], max_workers: int = 4) -> list[Response]:
        """Execute asks in parallel, preserving input order.

        Never raises for a provider-level failure. A provider that errors yields
        an `ok=False` Response so one bad backend cannot abort the fan-out — and
        so the caller can see that it *did not answer*, rather than silently
        getting a smaller set of results than it asked for.
        """
        if not asks:
            return []

        def execute(ask: Ask) -> Response:
            if ask.provider is None:
                return Response.failure(
                    "<unassigned>", "Ask has no provider; assign one first", ask.tag
                )
            provider = self.get(ask.provider)
            if provider is None:
                return Response.failure(
                    ask.provider, f"provider {ask.provider!r} is not in this council", ask.tag
                )
            try:
                return provider.ask(ask.prompt, ask.schema, ask.tag)
            except Exception as exc:  # noqa: BLE001 - a bug must not kill the fan-out
                return Response.failure(
                    ask.provider, f"unexpected provider error: {exc!r}", ask.tag
                )

        workers = max(1, min(max_workers, len(asks)))
        with ThreadPoolExecutor(max_workers=workers) as pool:
            return list(pool.map(execute, asks))

    def ask(
        self,
        provider: str,
        prompt: str,
        schema: dict[str, Any] | None = None,
        tag: str = "",
    ) -> Response:
        """Ask exactly one provider."""
        return self.run([Ask(prompt=prompt, provider=provider, schema=schema, tag=tag)])[0]

    def ask_all(
        self,
        prompt: str,
        schema: dict[str, Any] | None = None,
        tag: str = "",
        max_workers: int = 4,
    ) -> list[Response]:
        """Ask every provider the same question — the simple consensus check.

        Note that agreement here is weak evidence: models can share a blind spot.
        Disagreement is usually the more informative outcome.
        """
        asks = [
            Ask(prompt=prompt, provider=p.name, schema=schema, tag=tag)
            for p in self.providers
        ]
        return self.run(asks, max_workers=max_workers)

    def __len__(self) -> int:
        return len(self.providers)

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"<Council providers={self.names}>"
