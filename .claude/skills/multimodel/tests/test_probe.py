"""Probe semantics: `available()` inspects local state; `probe()` makes a real call.

Stub providers only — nothing here touches a network or a binary.
"""

from __future__ import annotations

from typing import Any

from multimodel.base import Provider
from multimodel.council import Council
from multimodel.types import Response


class StubProvider(Provider):
    def __init__(self, name: str, cfg: dict[str, Any] | None = None) -> None:
        super().__init__(name, cfg or {})
        self.calls = 0

    def available(self) -> tuple[bool, str]:
        if self.cfg.get("unavailable"):
            return False, "stub says unavailable"
        return True, "stub available"

    def ask(self, prompt: str, schema: dict[str, Any] | None = None, tag: str = "") -> Response:
        self.calls += 1
        mode = self.cfg.get("mode", "good")
        if mode == "error":
            return Response.failure(self.name, "stub failure", tag)
        if mode == "unstructured":
            return Response.success(self.name, text="sure thing", tag=tag)
        if mode == "raises":
            raise RuntimeError("stub exploded")
        return Response.success(self.name, text="{}", data={"ok": True}, tag=tag)


def test_probe_passes_when_provider_answers_with_structure():
    result = StubProvider("s").probe()
    assert result.ok
    assert result.structured is True
    assert result.elapsed_seconds is not None


def test_probe_does_not_call_when_unavailable():
    provider = StubProvider("s", {"unavailable": True})
    result = provider.probe()
    assert not result.ok
    assert provider.calls == 0
    assert "unavailable" in result.detail


def test_probe_fails_when_the_call_fails():
    result = StubProvider("s", {"mode": "error"}).probe()
    assert not result.ok
    assert "stub failure" in result.detail


def test_probe_fails_when_output_is_unstructured():
    result = StubProvider("s", {"mode": "unstructured"}).probe()
    assert not result.ok
    assert result.structured is False
    assert "structured output" in result.detail.lower()


def test_probe_never_raises():
    result = StubProvider("s", {"mode": "raises"}).probe()
    assert not result.ok
    assert "exploded" in result.detail


def test_probe_restores_the_original_timeout():
    provider = StubProvider("s", {"timeout_seconds": 300})
    provider.probe(timeout=5)
    assert provider.cfg["timeout_seconds"] == 300


def test_probe_leaves_no_timeout_key_when_there_was_none():
    provider = StubProvider("s")
    provider.probe(timeout=5)
    assert "timeout_seconds" not in provider.cfg


def test_council_probes_every_provider():
    council = Council([StubProvider("a"), StubProvider("b", {"mode": "error"})])
    results = {r.provider: r for r in council.probe_all(timeout=5)}
    assert results["a"].ok
    assert not results["b"].ok


def test_council_probe_on_empty_council_is_empty():
    assert Council([]).probe_all() == []


def test_availability_is_cheaper_than_probe():
    provider = StubProvider("s")
    provider.available()
    assert provider.calls == 0
