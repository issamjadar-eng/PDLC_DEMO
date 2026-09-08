"""Council construction and fan-out semantics."""

from __future__ import annotations

from typing import Any

from multimodel import Ask, Council, register
from multimodel.base import Provider
from multimodel.types import Response


class EchoProvider(Provider):
    def available(self) -> tuple[bool, str]:
        return True, "echo"

    def ask(self, prompt: str, schema: dict[str, Any] | None = None, tag: str = "") -> Response:
        if self.cfg.get("boom"):
            raise RuntimeError("boom")
        return Response.success(self.name, text=f"{self.name}:{prompt}", data={"ok": True}, tag=tag)


register("echo", EchoProvider)


def _config(**providers: dict[str, Any]) -> dict[str, Any]:
    return {"providers": providers}


def test_from_config_uses_entry_name_as_type_and_skips_disabled():
    council = Council.from_config(_config(
        a={"type": "echo", "enabled": True},
        b={"type": "echo", "enabled": False},
    ))
    assert council.names == ["a"]
    assert "disabled" in council.skipped["b"]


def test_unknown_type_is_reported_not_silently_dropped():
    council = Council.from_config(_config(mystery={"enabled": True, "type": "nope"}))
    assert council.names == []
    assert "no adapter" in council.skipped["mystery"]


def test_role_filter_and_only_filter():
    cfg = _config(
        a={"type": "echo", "enabled": True, "role": "challenger"},
        b={"type": "echo", "enabled": True, "role": "worker"},
        c={"type": "echo", "enabled": True, "role": "challenger"},
    )
    assert Council.from_config(cfg, role="challenger").names == ["a", "c"]
    assert Council.from_config(cfg, only=["b"]).names == ["b"]
    assert Council.from_config(cfg, only=["zzz"]).names == []


def test_null_entry_is_tolerated():
    council = Council.from_config({"providers": {"a": None}}, include_disabled=True)
    assert "no adapter" in council.skipped["a"]


def test_ask_all_preserves_order_and_tags():
    council = Council.from_config(_config(
        x={"type": "echo", "enabled": True}, y={"type": "echo", "enabled": True}))
    responses = council.ask_all("q", tag="lens")
    assert [r.provider for r in responses] == ["x", "y"]
    assert all(r.ok and r.tag == "lens" for r in responses)


def test_run_never_raises_and_reports_missing_provider():
    council = Council.from_config(_config(
        x={"type": "echo", "enabled": True}, bad={"type": "echo", "enabled": True, "boom": True}))
    responses = council.run([
        Ask(prompt="q", provider="x"),
        Ask(prompt="q", provider="bad"),
        Ask(prompt="q", provider="ghost"),
        Ask(prompt="q", provider=None),
    ])
    assert [r.ok for r in responses] == [True, False, False, False]
    assert "boom" in responses[1].error
    assert "not in this council" in responses[2].error
    assert "no provider" in responses[3].error


def test_distribute_is_round_robin_and_deterministic():
    council = Council.from_config(_config(
        a={"type": "echo", "enabled": True}, b={"type": "echo", "enabled": True}))
    assert council.distribute(["t1", "t2", "t3"]) == [("a", "t1"), ("b", "t2"), ("a", "t3")]
    assert Council([]).distribute(["t1"]) == []


def test_response_to_dict_omits_raw():
    r = Response.success("p", text="t", data={"k": 1}, raw="huge", usage={"total_tokens": 3})
    d = r.to_dict()
    assert "raw" not in d
    assert d["provider"] == "p" and d["ok"] is True and d["data"] == {"k": 1}
