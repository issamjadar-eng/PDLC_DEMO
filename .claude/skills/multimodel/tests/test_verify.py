"""The read-only verifier: behavioural, fail-closed, cleans up after itself."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from multimodel.base import Provider
from multimodel.types import Response
from multimodel.verify import MARKER, WRITTEN, provider_dir, verify_all, verify_provider


class Agent(Provider):
    """A fake vendor agent that really touches the filesystem like one would."""

    def available(self):
        return True, "fake"

    def ask(self, prompt: str, schema: dict[str, Any] | None = None, tag: str = "") -> Response:
        root = Path(self.cfg["root"])
        mode = self.cfg.get("mode", "reads-only")
        if mode == "dead":
            return Response.failure(self.name, "unreachable", tag)
        if mode == "raises":
            raise RuntimeError("boom")
        if tag == "verify-read":
            content = (root / provider_dir(self.name) / MARKER).read_text(encoding="utf-8").strip() if mode != "blind" else ""
            return Response.success(self.name, text="", data={"content": content}, tag=tag, usage={"num_turns": 1})
        wrote = False
        if mode == "writes":
            (root / provider_dir(self.name) / WRITTEN).write_text("hello", encoding="utf-8")
            wrote = True
        if mode == "silent-deny":
            # a CLI that ends the run at the denial with no output at all
            return Response.failure(self.name, 'tool call auto-denied (needs the \'write_file\' permission)', tag)
        return Response.success(self.name, text="", data={"wrote": wrote}, tag=tag)


def test_read_only_agent_passes_and_marker_is_cleaned(tmp_path):
    r = verify_provider(Agent("a", {"root": str(tmp_path)}), tmp_path)
    assert r.ok and r.status == "PASS" and r.read_ok and r.write_blocked
    assert not (tmp_path / provider_dir("a") / MARKER).exists()
    assert r.usage == {"num_turns": 1}


def test_writing_agent_is_critical_and_file_is_removed(tmp_path):
    r = verify_provider(Agent("a", {"root": str(tmp_path), "mode": "writes"}), tmp_path)
    assert not r.ok and r.status == "CRITICAL" and r.read_ok and not r.write_blocked
    assert "not read-only" in r.detail
    assert not (tmp_path / provider_dir("a") / WRITTEN).exists(), "the verifier cleans up the landed file"


def test_blind_agent_fails_read(tmp_path):
    r = verify_provider(Agent("a", {"root": str(tmp_path), "mode": "blind"}), tmp_path)
    assert r.status == "FAIL" and not r.read_ok and r.write_blocked


def test_silent_denial_on_write_probe_still_passes(tmp_path):
    """Some CLIs emit nothing after a denied write; the disk is the evidence."""
    r = verify_provider(Agent("a", {"root": str(tmp_path), "mode": "silent-deny"}), tmp_path)
    assert r.status == "PASS" and r.read_ok and r.write_blocked
    assert "write_file" in r.detail


def test_dead_or_crashing_agent_is_a_fail_not_a_crash(tmp_path):
    r = verify_provider(Agent("a", {"root": str(tmp_path), "mode": "dead"}), tmp_path)
    assert r.status == "FAIL" and "unreachable" in r.detail
    r = verify_provider(Agent("a", {"root": str(tmp_path), "mode": "raises"}), tmp_path)
    assert r.status == "FAIL" and "boom" in r.detail


def test_token_is_fresh_per_run(tmp_path, monkeypatch):
    seen: list[str] = []

    class Spy(Agent):
        def ask(self, prompt, schema=None, tag=""):
            seen.append((Path(self.cfg["root"]) / provider_dir(self.name) / MARKER).read_text())
            return super().ask(prompt, schema, tag)

    verify_provider(Spy("a", {"root": str(tmp_path)}), tmp_path)
    verify_provider(Spy("a", {"root": str(tmp_path)}), tmp_path)
    assert seen[0] != seen[1] and all(s.startswith("marker-") for s in seen)


def test_verify_all_runs_every_provider(tmp_path):
    results = verify_all([Agent("a", {"root": str(tmp_path)}), Agent("b", {"root": str(tmp_path), "mode": "writes"})], tmp_path)
    assert [r.status for r in results] == ["PASS", "CRITICAL"]
    assert verify_all([], tmp_path) == []
    assert results[0].to_dict()["status"] == "PASS"


def test_parallel_providers_do_not_share_a_marker(tmp_path):
    """REGRESSION: one shared marker path made parallel verifications read each
    other's token and trip on each other's write attempt."""
    assert provider_dir("a") != provider_dir("b")
    results = verify_all([Agent("a", {"root": str(tmp_path)}), Agent("b", {"root": str(tmp_path)})], tmp_path)
    assert all(r.status == "PASS" for r in results)


def test_read_miss_is_retried_but_landed_write_is_not(tmp_path):
    calls = {"blind": 0, "writes": 0}

    class Flaky(Agent):
        def ask(self, prompt, schema=None, tag=""):
            if tag == "verify-read":
                calls[self.cfg["mode"]] += 1
            if self.cfg["mode"] == "blind" and calls["blind"] == 2 and tag == "verify-read":
                self.cfg["mode"] = "reads-only"
                r = super().ask(prompt, schema, tag)
                self.cfg["mode"] = "blind"
                return r
            return super().ask(prompt, schema, tag)

    r = verify_provider(Flaky("a", {"root": str(tmp_path), "mode": "blind"}), tmp_path, attempts=3)
    assert r.status == "PASS" and r.attempts == 2
    r = verify_provider(Flaky("b", {"root": str(tmp_path), "mode": "writes"}), tmp_path, attempts=3)
    assert r.status == "CRITICAL" and r.attempts == 1, "a landed write is never retried"


def test_scratch_folders_are_removed_after_a_run(tmp_path):
    from multimodel.verify import VERIFY_DIR
    verify_all([Agent("a", {"root": str(tmp_path)}), Agent("b", {"root": str(tmp_path)})], tmp_path)
    assert not (tmp_path / VERIFY_DIR).exists()
