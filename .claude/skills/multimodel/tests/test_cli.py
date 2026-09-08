"""The CLI contract other skills call: exit codes, --json shapes, policy gate."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

import pytest

from multimodel import register
from multimodel.base import Provider
from multimodel.types import Response

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "multimodel.py"


@pytest.fixture(scope="module")
def cli():
    spec = importlib.util.spec_from_file_location("multimodel_cli", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class StubProvider(Provider):
    def available(self) -> tuple[bool, str]:
        return (not self.cfg.get("down"), "stub")

    def ask(self, prompt: str, schema: dict[str, Any] | None = None, tag: str = "") -> Response:
        if self.cfg.get("down"):
            return Response.failure(self.name, "down", tag)
        data = {"ok": True} if schema else None
        return Response.success(self.name, text=f"echo:{prompt.strip()}", data=data, tag=tag)


register("stub", StubProvider)

TOML = """
[policy]
external_send = "{policy}"
[providers.one]
enabled = true
type = "stub"
role = "challenger"
[providers.two]
enabled = true
type = "stub"
role = "worker"
down = {down}
[providers.off]
enabled = false
type = "stub"
"""


def _config(tmp_path, policy="allowed", down="false") -> str:
    path = tmp_path / "models.toml"
    path.write_text(TOML.format(policy=policy, down=down), encoding="utf-8")
    return str(path)


def test_doctor_quick_json(cli, tmp_path, capsys):
    rc = cli.main(["--config", _config(tmp_path), "doctor", "--quick", "--json"])
    out = json.loads(capsys.readouterr().out)
    assert rc == 0 and out["ok"] is True
    assert out["providers"]["one"]["available"] is True
    assert "off" in out["skipped"]
    assert out["policy"]["external_send_allowed"] is True


def test_doctor_live_reports_probe_and_failure(cli, tmp_path, capsys):
    rc = cli.main(["--config", _config(tmp_path, down="true"), "doctor", "--json"])
    out = json.loads(capsys.readouterr().out)
    assert rc == 1
    assert out["providers"]["one"]["probe_ok"] is True
    assert out["providers"]["two"]["available"] is False
    assert any("two" in p for p in out["problems"])


def test_doctor_role_filter_and_no_providers(cli, tmp_path, capsys):
    rc = cli.main(["--config", _config(tmp_path), "--role", "nobody", "doctor", "--quick", "--json"])
    out = json.loads(capsys.readouterr().out)
    assert rc == 1 and out["ok"] is False


def test_ask_json_and_provider_selection(cli, tmp_path, capsys):
    rc = cli.main(["--config", _config(tmp_path), "ask", "--provider", "two", "--json", "hello"])
    out = json.loads(capsys.readouterr().out)
    assert rc == 0 and out["asked"] == 1 and out["responses"][0]["provider"] == "two"
    assert out["responses"][0]["text"] == "echo:hello"


def test_ask_prompt_file_and_schema(cli, tmp_path, capsys):
    prompt = tmp_path / "p.md"
    prompt.write_text("from file\n", encoding="utf-8")
    schema = tmp_path / "s.json"
    schema.write_text('{"type":"object","properties":{"ok":{"type":"boolean"}},"required":["ok"]}')
    rc = cli.main(["--config", _config(tmp_path), "ask", "--prompt-file", str(prompt),
                   "--schema", str(schema), "--json"])
    out = json.loads(capsys.readouterr().out)
    assert rc == 0 and all(r["data"] == {"ok": True} for r in out["responses"])
    assert out["responses"][0]["text"] == "echo:from file"


def test_ask_text_mode_marks_no_answer(cli, tmp_path, capsys):
    rc = cli.main(["--config", _config(tmp_path, down="true"), "ask", "q"])
    out = capsys.readouterr().out
    assert rc == 1 and "[NO ANSWER]" in out and "1/2 answered" in out


def test_ask_refuses_when_policy_forbids(cli, tmp_path, capsys):
    rc = cli.main(["--config", _config(tmp_path, policy="forbidden"), "ask", "q"])
    assert rc == 1 and "refusing to send" in capsys.readouterr().err


def test_ask_without_prompt_is_usage_error(cli, tmp_path, capsys):
    rc = cli.main(["--config", _config(tmp_path), "ask"])
    assert rc == 2


def test_ask_unknown_provider_lists_skipped(cli, tmp_path, capsys):
    rc = cli.main(["--config", _config(tmp_path), "ask", "--provider", "off", "q"])
    err = capsys.readouterr().err
    assert rc == 1 and "off" in err and "disabled" in err


def test_providers_json(cli, tmp_path, capsys):
    rc = cli.main(["--config", _config(tmp_path), "providers", "--json"])
    out = json.loads(capsys.readouterr().out)
    names = {row["name"]: row for row in out["providers"]}
    assert rc == 0 and names["off"]["enabled"] is False and names["one"]["available"] is True


def test_missing_config_is_a_clean_failure(cli, tmp_path, capsys):
    rc = cli.main(["--config", str(tmp_path / "nope.toml"), "doctor", "--quick"])
    assert rc == 1 and "[FAIL]" in capsys.readouterr().err


def test_verify_command_reports_per_provider(cli, tmp_path, capsys, monkeypatch):
    """`verify` forces project workspace, plants the marker at the project root, reports."""
    from multimodel.verify import MARKER, WRITTEN, provider_dir

    (tmp_path / "project.yml").write_text("project:\n  name: x\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    class ReadOnly(StubProvider):
        def ask(self, prompt, schema=None, tag=""):
            assert self.workspace == "project"
            if tag == "verify-read":
                content = (tmp_path / provider_dir(self.name) / MARKER).read_text().strip()
                return Response.success(self.name, "", data={"content": content}, tag=tag)
            if self.name == "two":
                (tmp_path / provider_dir(self.name) / WRITTEN).write_text("x")
            return Response.success(self.name, "", data={"wrote": self.name == "two"}, tag=tag)

    register("stub", ReadOnly)
    try:
        rc = cli.main(["--config", _config(tmp_path), "verify", "--json"])
    finally:
        register("stub", StubProvider)
    out = json.loads(capsys.readouterr().out)
    by = {r["provider"]: r for r in out["results"]}
    assert rc == 1 and out["ok"] is False
    assert by["one"]["status"] == "PASS" and by["two"]["status"] == "CRITICAL"
    assert not (tmp_path / provider_dir("two") / WRITTEN).exists()


def test_verify_refuses_when_policy_forbids(cli, tmp_path, capsys):
    rc = cli.main(["--config", _config(tmp_path, policy="forbidden"), "verify"])
    assert rc == 1 and "cannot verify" in capsys.readouterr().err


def test_ask_workspace_flag_reaches_providers(cli, tmp_path, capsys, monkeypatch):
    seen: dict[str, str] = {}

    class SpyProvider(StubProvider):
        def ask(self, prompt, schema=None, tag=""):
            seen[self.name] = self.workspace
            return super().ask(prompt, schema, tag)

    register("stub", SpyProvider)
    try:
        rc = cli.main(["--config", _config(tmp_path), "ask", "--workspace", "isolated", "--json", "q"])
    finally:
        register("stub", StubProvider)
    assert rc == 0 and seen == {"one": "isolated", "two": "isolated"}


def test_verify_skips_isolated_by_config_unless_named(cli, tmp_path, capsys, monkeypatch):
    from multimodel.verify import MARKER, provider_dir

    (tmp_path / "project.yml").write_text("project:\n  name: x\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    cfg = tmp_path / "iso.toml"
    cfg.write_text(TOML.format(policy="allowed", down="false").replace(
        '[providers.two]\nenabled = true\ntype = "stub"\nrole = "worker"',
        '[providers.two]\nenabled = true\ntype = "stub"\nrole = "worker"\nworkspace = "isolated"'),
        encoding="utf-8")

    class ReadOnly(StubProvider):
        def ask(self, prompt, schema=None, tag=""):
            if tag == "verify-read":
                content = (tmp_path / provider_dir(self.name) / MARKER).read_text().strip()
                return Response.success(self.name, "", data={"content": content}, tag=tag)
            return Response.success(self.name, "", data={"wrote": False}, tag=tag)

    register("stub", ReadOnly)
    try:
        rc = cli.main(["--config", str(cfg), "verify", "--json"])
        out = json.loads(capsys.readouterr().out)
        assert rc == 0 and out["ok"] is True
        assert [r["provider"] for r in out["results"]] == ["one"]
        assert "isolated by config" in out["unavailable"]["two"]
        rc = cli.main(["--config", str(cfg), "verify", "--provider", "two", "--json"])
        out = json.loads(capsys.readouterr().out)
        assert rc == 0 and [r["provider"] for r in out["results"]] == ["two"]
    finally:
        register("stub", StubProvider)
