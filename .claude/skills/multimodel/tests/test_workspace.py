"""Where a vendor CLI runs. Isolated by default; the project directory only on
explicit opt-in; probes always isolated.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import multimodel.providers.antigravity as agy_mod
import multimodel.providers.codex as codex_mod
import multimodel.providers.grok as grok_mod
from multimodel.base import CliResult, Provider
from multimodel.providers.antigravity import AntigravityProvider
from multimodel.providers.codex import CodexProvider
from multimodel.providers.grok import GrokProvider
from multimodel.types import Response


def test_workspace_defaults_to_project_and_rejects_junk():
    class P(Provider):
        def available(self): return True, ""
        def ask(self, prompt, schema=None, tag=""): return Response.success(self.name, "x")
    assert P("p", {}).workspace == "project"
    assert P("p", {"workspace": "isolated"}).workspace == "isolated"
    assert P("p", {"workspace": "anywhere"}).workspace == "project"


def test_workdir_isolated_is_empty_temp_dir_and_project_is_root(tmp_path, monkeypatch):
    class P(Provider):
        def available(self): return True, ""
        def ask(self, prompt, schema=None, tag=""): return Response.success(self.name, "x")
    (tmp_path / "project.yml").write_text("project:\n  name: x\n", encoding="utf-8")
    sub = tmp_path / "docs" / "deep"
    sub.mkdir(parents=True)
    monkeypatch.chdir(sub)
    with P("p", {"workspace": "isolated"}).workdir() as work:
        assert work.is_dir() and work != tmp_path and not any(work.iterdir())
    assert not work.exists(), "temp workspace is removed afterwards"
    with P("p", {}).workdir() as work:
        assert work == tmp_path, "project workspace is the project ROOT, not the cwd"


def _capture(module, stdout: str, ok_login: bool = False):
    seen: dict[str, Any] = {}

    def run(args, timeout, cwd=None):
        if "login" in args or args[1:] == ["models"]:
            return CliResult(True, "Logged in using ChatGPT\nmodel-a\tA")
        seen["args"] = args
        seen["cwd"] = cwd
        if "--output-last-message" in args:
            Path(args[args.index("--output-last-message") + 1]).write_text(stdout, encoding="utf-8")
        return CliResult(True, stdout)

    module.run_cli = run
    return seen


def test_grok_isolated_runs_in_empty_temp_cwd(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(grok_mod, "resolve_binary", lambda *_: "/bin/grok")
    seen: dict[str, Any] = {}
    monkeypatch.setattr(grok_mod, "run_cli", lambda a, t, cwd=None: (seen.update(args=a, cwd=cwd), CliResult(True, "hi"))[1])
    GrokProvider("grok", {"workspace": "isolated"}).ask("q")
    assert seen["cwd"] != str(tmp_path) and Path(seen["cwd"]).name.startswith("mm-work-")
    assert seen["args"][seen["args"].index("--cwd") + 1] == seen["cwd"]


def test_grok_project_default_is_read_only_allowlist_at_root(monkeypatch, tmp_path):
    """The guard is an allowlist of read tools; web search off unless asked."""
    (tmp_path / "project.yml").write_text("project:\n  name: x\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(grok_mod, "resolve_binary", lambda *_: "/bin/grok")
    seen: dict[str, Any] = {}
    monkeypatch.setattr(grok_mod, "run_cli", lambda a, t, cwd=None: (seen.update(args=a, cwd=cwd), CliResult(True, "hi"))[1])
    GrokProvider("grok", {"max_turns": 3}).ask("q")
    args = seen["args"]
    assert seen["cwd"] == str(tmp_path)
    assert "--output-format" in args
    assert args[args.index("--tools") + 1] == "read_file,list_dir,grep"
    assert "--disable-web-search" in args
    assert "--disallowed-tools" not in args and "--permission-mode" not in args
    assert args[args.index("--max-turns") + 1] == "3"
    for forbidden in ("run_terminal_command", "search_replace", "write", "spawn_subagent"):
        assert forbidden not in args[args.index("--tools") + 1]


def test_grok_project_mode_puts_schema_in_prompt_and_parses_text(monkeypatch, tmp_path):
    """REGRESSION: `--json-schema` constrains the FIRST turn, so a narrating
    model never reaches its read tool. In a project workspace the schema is
    requested in the prompt and the answer parsed from the text stream."""
    (tmp_path / "project.yml").write_text("project:\n  name: x\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(grok_mod, "resolve_binary", lambda *_: "/bin/grok")
    seen: dict[str, Any] = {}
    envelope = json.dumps({"text": "I'll read the file first.{\"verdict\": \"final\"}",
                           "stopReason": "end_turn", "num_turns": 2, "structuredOutput": None})
    monkeypatch.setattr(grok_mod, "run_cli", lambda a, t, cwd=None: (seen.update(args=a), CliResult(True, envelope))[1])
    schema = {"required": ["verdict"], "properties": {"verdict": {"type": "string"}}}
    res = GrokProvider("grok", {}).ask("q", schema=schema)
    assert res.ok and res.data == {"verdict": "final"}
    assert "--json-schema" not in seen["args"]
    assert "JSON Schema" in seen["args"][seen["args"].index("-p") + 1]
    assert res.usage == {"num_turns": 2}


def test_grok_isolated_mode_uses_cli_schema_and_cli_forced(monkeypatch):
    monkeypatch.setattr(grok_mod, "resolve_binary", lambda *_: "/bin/grok")
    seen: dict[str, Any] = {}
    envelope = json.dumps({"text": "", "stopReason": "end_turn", "structuredOutput": {"verdict": "v"}})
    monkeypatch.setattr(grok_mod, "run_cli", lambda a, t, cwd=None: (seen.update(args=a), CliResult(True, envelope))[1])
    schema = {"required": ["verdict"], "properties": {"verdict": {}}}
    assert GrokProvider("grok", {"workspace": "isolated"}).ask("q", schema=schema).data == {"verdict": "v"}
    assert "--json-schema" in seen["args"]
    assert GrokProvider("grok", {"schema_mode": "cli"}).ask("q", schema=schema).data == {"verdict": "v"}
    assert "--json-schema" in seen["args"]
    GrokProvider("grok", {"workspace": "isolated", "schema_mode": "prompt"}).ask("q", schema=schema)
    assert "--json-schema" not in seen["args"]


def test_grok_prompt_mode_fails_closed_without_a_conforming_object(monkeypatch, tmp_path):
    (tmp_path / "project.yml").write_text("project:\n  name: x\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(grok_mod, "resolve_binary", lambda *_: "/bin/grok")
    envelope = json.dumps({"text": "I'll read the file first.", "stopReason": "end_turn", "num_turns": 1})
    monkeypatch.setattr(grok_mod, "run_cli", lambda a, t, cwd=None: CliResult(True, envelope))
    res = GrokProvider("grok", {}).ask("q", schema={"required": ["verdict"], "properties": {"verdict": {}}})
    assert res.ok is False and "verdict" in res.error


def test_grok_web_search_and_read_tools_are_configurable(monkeypatch):
    monkeypatch.setattr(grok_mod, "resolve_binary", lambda *_: "/bin/grok")
    seen: dict[str, Any] = {}
    monkeypatch.setattr(grok_mod, "run_cli", lambda a, t, cwd=None: (seen.update(args=a), CliResult(True, "hi"))[1])
    GrokProvider("grok", {"web_search": True, "read_tools": "read_file"}).ask("q")
    assert "--disable-web-search" not in seen["args"]
    assert seen["args"][seen["args"].index("--tools") + 1] == "read_file"


def test_grok_prefers_structured_output_and_reports_turns(monkeypatch):
    monkeypatch.setattr(grok_mod, "resolve_binary", lambda *_: "/bin/grok")
    envelope = json.dumps({
        "text": '{"verdict": "placeholder"}{"verdict": "from-text"}',
        "structuredOutput": {"verdict": "from-envelope"},
        "usage": {"total_tokens": 42}, "num_turns": 7, "total_cost_usd": 0.07,
    })
    monkeypatch.setattr(grok_mod, "run_cli", lambda a, t, cwd=None: CliResult(True, envelope))
    res = GrokProvider("grok", {"workspace": "isolated"}).ask("q", schema={"required": ["verdict"], "properties": {"verdict": {}}})
    assert res.ok and res.data == {"verdict": "from-envelope"}
    assert res.usage == {"total_tokens": 42, "num_turns": 7, "total_cost_usd": 0.07}


def test_grok_cancelled_run_with_placeholder_objects_is_no_answer(monkeypatch):
    """REGRESSION from the first live run: a run that ended `cancelled` left five
    well-formed interim objects in `text` and null structuredOutput. Scraping
    the text accepted a placeholder as the verdict."""
    monkeypatch.setattr(grok_mod, "resolve_binary", lambda *_: "/bin/grok")
    envelope = json.dumps({
        "text": '{"verdict": "class_c", "crux": "placeholder"}{"verdict": "class_c", "crux": "placeholder"}',
        "stopReason": "cancelled", "structuredOutput": None,
        "structuredOutputError": "model did not produce structured output",
        "usage": {"total_tokens": 5}, "num_turns": 1,
    })
    monkeypatch.setattr(grok_mod, "run_cli", lambda a, t, cwd=None: CliResult(True, envelope))
    res = GrokProvider("grok", {"workspace": "isolated"}).ask("q", schema={"required": ["verdict"], "properties": {"verdict": {}}})
    assert res.ok is False
    assert "cancelled" in res.error and "did not produce" in res.error


def test_grok_null_structured_output_on_clean_stop_is_no_answer(monkeypatch):
    monkeypatch.setattr(grok_mod, "resolve_binary", lambda *_: "/bin/grok")
    envelope = json.dumps({"text": '{"verdict": "x"}', "stopReason": "end_turn", "structuredOutput": None})
    monkeypatch.setattr(grok_mod, "run_cli", lambda a, t, cwd=None: CliResult(True, envelope))
    res = GrokProvider("grok", {"workspace": "isolated"}).ask("q", schema={"required": ["verdict"], "properties": {"verdict": {}}})
    assert res.ok is False and "no structured output" in res.error


def test_grok_old_cli_without_structured_field_falls_back_to_text(monkeypatch):
    monkeypatch.setattr(grok_mod, "resolve_binary", lambda *_: "/bin/grok")
    envelope = json.dumps({"text": '{"verdict": "interim"}{"verdict": "final", "crux": "real"}'})
    monkeypatch.setattr(grok_mod, "run_cli", lambda a, t, cwd=None: CliResult(True, envelope))
    res = GrokProvider("grok", {}).ask("q", schema={"required": ["verdict"], "properties": {"verdict": {}}})
    assert res.ok and res.data["verdict"] == "final"


def test_grok_unstructured_cancelled_run_is_no_answer(monkeypatch):
    monkeypatch.setattr(grok_mod, "resolve_binary", lambda *_: "/bin/grok")
    monkeypatch.setattr(grok_mod, "run_cli", lambda a, t, cwd=None: CliResult(True, json.dumps({"text": "partial", "stopReason": "cancelled"})))
    assert GrokProvider("grok", {}).ask("q").ok is False


def test_grok_unstructured_uses_envelope_text(monkeypatch):
    monkeypatch.setattr(grok_mod, "resolve_binary", lambda *_: "/bin/grok")
    monkeypatch.setattr(grok_mod, "run_cli", lambda a, t, cwd=None: CliResult(True, json.dumps({"text": "plain answer", "num_turns": 1})))
    res = GrokProvider("grok", {}).ask("q")
    assert res.ok and res.text == "plain answer" and res.usage == {"num_turns": 1}


def test_codex_passes_cd_and_cwd(monkeypatch, tmp_path):
    (tmp_path / "project.yml").write_text("project:\n  name: x\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(codex_mod, "resolve_binary", lambda *_: "/bin/codex")
    seen = _capture(codex_mod, '{"ok": true}')
    CodexProvider("codex", {"workspace": "isolated"}).ask("q")
    assert seen["cwd"] != str(tmp_path)
    assert seen["args"][seen["args"].index("--cd") + 1] == seen["cwd"]
    seen = _capture(codex_mod, "x")
    CodexProvider("codex", {}).ask("q")
    assert seen["cwd"] == str(tmp_path)
    assert seen["args"][seen["args"].index("--sandbox") + 1] == "read-only"


def test_codex_refuses_project_workspace_with_loose_sandbox(monkeypatch):
    monkeypatch.setattr(codex_mod, "resolve_binary", lambda *_: "/bin/codex")
    monkeypatch.setattr(codex_mod, "run_cli", lambda a, timeout=None, cwd=None: CliResult(True, "Logged in using ChatGPT"))
    res = CodexProvider("codex", {"sandbox": "workspace-write"}).ask("q")
    assert res.ok is False and "read-only" in res.error
    assert CodexProvider("codex", {"sandbox": "workspace-write", "workspace": "isolated"}).workspace == "isolated"


def _agy_settings(tmp_path, allow, deny=None):
    path = tmp_path / "settings.json"
    path.write_text(json.dumps({"permissions": {"allow": allow, "deny": deny or []}}), encoding="utf-8")
    return path


def _agy_projects(tmp_path, root, bound=True, project_id="p-1"):
    d = tmp_path / "projects"; d.mkdir(exist_ok=True)
    if bound:
        (d / f"{project_id}.json").write_text(json.dumps({
            "id": project_id, "name": "x",
            "projectResources": {"resources": [{"folderUri": root.resolve().as_uri()}]}}), encoding="utf-8")
    return d


def test_antigravity_isolated_uses_temp_cwd(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(agy_mod, "resolve_binary", lambda *_: "/bin/agy")
    seen = _capture(agy_mod, json.dumps({"status": "SUCCESS", "response": "ok"}))
    res = AntigravityProvider("agy", {"workspace": "isolated"}).ask("q")
    assert res.ok and seen["cwd"] != str(tmp_path)
    assert "--project" not in seen["args"] and "--mode" not in seen["args"]
    assert "--dangerously-skip-permissions" not in seen["args"]


def test_antigravity_refuses_project_workspace_without_bound_project(monkeypatch, tmp_path):
    root = tmp_path / "repo"; root.mkdir(); (root / "project.yml").write_text("project:\n  name: x\n")
    monkeypatch.chdir(root)
    monkeypatch.setattr(agy_mod, "resolve_binary", lambda *_: "/bin/agy")
    monkeypatch.setattr(agy_mod, "SETTINGS", _agy_settings(tmp_path, ["command(which)"]))
    monkeypatch.setattr(agy_mod, "PROJECTS_DIR", _agy_projects(tmp_path, root, bound=False))
    seen = _capture(agy_mod, json.dumps({"status": "SUCCESS", "response": "ok"}))
    res = AntigravityProvider("agy", {}).ask("q")
    assert res.ok is False and "no Antigravity project is bound" in res.error and "setup" in res.error
    assert "args" not in seen, "must refuse before launching the CLI"
    ok, why = AntigravityProvider("agy", {}).available()
    assert ok and "NOT usable" in why


def test_antigravity_project_workspace_attaches_bound_project(monkeypatch, tmp_path):
    root = tmp_path / "repo"; root.mkdir(); (root / "project.yml").write_text("project:\n  name: x\n")
    monkeypatch.chdir(root)
    monkeypatch.setattr(agy_mod, "resolve_binary", lambda *_: "/bin/agy")
    monkeypatch.setattr(agy_mod, "SETTINGS", _agy_settings(tmp_path, ["command(which)"]))
    monkeypatch.setattr(agy_mod, "PROJECTS_DIR", _agy_projects(tmp_path, root, project_id="team-proj"))
    seen = _capture(agy_mod, json.dumps({"status": "SUCCESS", "response": "ok"}))
    res = AntigravityProvider("agy", {}).ask("q")
    assert res.ok and seen["cwd"] == str(root)
    assert seen["args"][seen["args"].index("--project") + 1] == "team-proj"
    assert "--mode" not in seen["args"] and "--dangerously-skip-permissions" not in seen["args"]
    assert "--sandbox" not in seen["args"]


def test_antigravity_project_id_override_wins(monkeypatch, tmp_path):
    root = tmp_path / "repo"; root.mkdir(); (root / "project.yml").write_text("project:\n  name: x\n")
    monkeypatch.chdir(root)
    monkeypatch.setattr(agy_mod, "resolve_binary", lambda *_: "/bin/agy")
    monkeypatch.setattr(agy_mod, "SETTINGS", _agy_settings(tmp_path, []))
    monkeypatch.setattr(agy_mod, "PROJECTS_DIR", _agy_projects(tmp_path, root, bound=False))
    seen = _capture(agy_mod, json.dumps({"status": "SUCCESS", "response": "ok"}))
    assert AntigravityProvider("agy", {"project_id": "mine"}).ask("q").ok
    assert seen["args"][seen["args"].index("--project") + 1] == "mine"


def test_antigravity_refuses_when_settings_grant_writes_over_project(monkeypatch, tmp_path):
    root = tmp_path / "repo"; root.mkdir(); (root / "project.yml").write_text("project:\n  name: x\n")
    monkeypatch.chdir(root)
    monkeypatch.setattr(agy_mod, "resolve_binary", lambda *_: "/bin/agy")
    monkeypatch.setattr(agy_mod, "SETTINGS", _agy_settings(tmp_path, ["write_file(*)"]))
    monkeypatch.setattr(agy_mod, "PROJECTS_DIR", _agy_projects(tmp_path, root))
    _capture(agy_mod, json.dumps({"status": "SUCCESS", "response": "ok"}))
    res = AntigravityProvider("agy", {}).ask("q")
    assert res.ok is False and "WRITES" in res.error


def test_antigravity_write_rules_clear_semantics(tmp_path):
    root = tmp_path / "repo"; root.mkdir()
    ok, _ = agy_mod.write_rules_clear(_agy_settings(tmp_path, ["read_file(*)", "command(git)"]), root)
    assert ok
    ok, why = agy_mod.write_rules_clear(_agy_settings(tmp_path, [f"write_file({tmp_path})"]), root)
    assert not ok and "WRITES" in why, "a parent-directory write grant covers the root"
    ok, _ = agy_mod.write_rules_clear(_agy_settings(tmp_path, ["write_file(/elsewhere)"]), root)
    assert ok
    ok, why = agy_mod.write_rules_clear(_agy_settings(tmp_path, [], deny=["read_file(*)"]), root)
    assert not ok and "denies" in why
    ok, _ = agy_mod.write_rules_clear(tmp_path / "missing.json", root)
    assert ok, "no settings file means defaults"


def test_antigravity_ensure_workspace_project_creates_once_and_reuses(tmp_path):
    root = tmp_path / "My Repo"; root.mkdir()
    d = tmp_path / "projects"
    pid, path, created = agy_mod.ensure_workspace_project(root, d)
    assert created and pid == "multimodel-my-repo" and path.name == "multimodel-my-repo.json"
    data = json.loads(path.read_text())
    assert data["projectResources"]["resources"][0]["folderUri"] == root.resolve().as_uri()
    pid2, path2, created2 = agy_mod.ensure_workspace_project(root, d)
    assert not created2 and path2 == path and pid2 == pid
    # an existing project bound by someone else (e.g. the CLI's own uuid file) is reused, not duplicated
    other = tmp_path / "projects2"; other.mkdir()
    (other / "abc-uuid.json").write_text(json.dumps({"id": "abc-uuid", "name": "Theirs",
        "projectResources": {"resources": [{"folderUri": root.resolve().as_uri()}]}}))
    pid3, path3, created3 = agy_mod.ensure_workspace_project(root, other)
    assert not created3 and pid3 == "abc-uuid"
    # same id bound to a different folder is never clobbered
    clash = tmp_path / "projects3"; clash.mkdir()
    (clash / "multimodel-my-repo.json").write_text(json.dumps({"id": "multimodel-my-repo",
        "projectResources": {"resources": [{"folderUri": (tmp_path / "elsewhere").as_uri()}]}}))
    import pytest
    with pytest.raises(FileExistsError):
        agy_mod.ensure_workspace_project(root, clash)


def test_antigravity_denial_is_named_when_run_ends_without_output(monkeypatch, tmp_path):
    monkeypatch.setattr(agy_mod, "resolve_binary", lambda *_: "/bin/agy")
    stderr = 'jetski: no output produced — a tool required the "write_file" permission that headless mode cannot prompt for, so it was auto-denied.'

    def run(args, timeout=None, cwd=None):
        if args[1:] == ["models"]:
            return CliResult(True, "m\tM")
        return CliResult(True, json.dumps({"status": "SUCCESS", "response": ""}), stderr)

    monkeypatch.setattr(agy_mod, "run_cli", run)
    res = AntigravityProvider("agy", {"workspace": "isolated"}).ask("q", schema={"required": ["x"], "properties": {"x": {}}})
    assert res.ok is False and "write_file" in res.error and "auto-denied" in res.error
    res = AntigravityProvider("agy", {"workspace": "isolated"}).ask("q")
    assert res.ok is False and "write_file" in res.error


def test_probe_is_always_isolated_and_restores_config_default(tmp_path, monkeypatch):
    seen: list[str] = []

    class P(Provider):
        def available(self): return True, ""
        def ask(self, prompt, schema=None, tag=""):
            seen.append(self.workspace)
            return Response.success(self.name, "{}", data={"ok": True})

    p = P("p", {})
    assert p.probe().ok
    assert seen == ["isolated"]
    assert "workspace" not in p.cfg


def test_probe_is_always_isolated_and_restores_config():
    seen: list[str] = []

    class P(Provider):
        def available(self): return True, ""
        def ask(self, prompt, schema=None, tag=""):
            seen.append(self.workspace)
            return Response.success(self.name, "{}", data={"ok": True})

    p = P("p", {"workspace": "project"})
    assert p.probe().ok
    assert seen == ["isolated"]
    assert p.cfg["workspace"] == "project"
    q = P("q", {})
    q.probe()
    assert "workspace" not in q.cfg



