"""Adapter behaviour with the vendor CLIs faked out.

Each provider is driven through a stubbed `run_cli` so the parsing and
fail-closed paths are pinned without a binary or a network.
"""

from __future__ import annotations

import json
import urllib.error
from pathlib import Path
from typing import Any

import pytest

import multimodel.providers.antigravity as agy_mod
import multimodel.providers.codex as codex_mod
import multimodel.providers.grok as grok_mod
import multimodel.providers.openai_http as http_mod
from multimodel.base import CliResult
from multimodel.providers.antigravity import AntigravityProvider
from multimodel.providers.codex import CodexProvider, strict_schema
from multimodel.providers.grok import GrokProvider
from multimodel.providers.openai_http import OpenAIHttpProvider

SCHEMA = {"type": "object", "properties": {"verdict": {"type": "string"}}, "required": ["verdict"]}


def _fake_cli(module, stdout: str = "", ok: bool = True, error: str | None = None, capture: dict | None = None):
    def run(args, timeout, cwd=None):
        if capture is not None:
            capture["args"] = args
            capture["timeout"] = timeout
        return CliResult(ok, stdout=stdout, error=error)
    module.run_cli = run  # patched per-test via monkeypatch in callers


# --- grok --------------------------------------------------------------------


def test_grok_unavailable_when_binary_missing(no_binaries):
    res = GrokProvider("grok", {}).ask("q")
    assert res.ok is False and "not found" in res.error


def test_grok_parses_streamed_envelope(monkeypatch):
    monkeypatch.setattr(grok_mod, "resolve_binary", lambda *_: "/bin/grok")
    envelope = json.dumps({"text": '{"verdict": "thinking"}{"verdict": "no", "why": "x"}'})
    captured: dict[str, Any] = {}
    monkeypatch.setattr(grok_mod, "run_cli", lambda a, t, cwd=None: (captured.update(args=a), CliResult(True, envelope))[1])
    res = GrokProvider("grok", {"model": "grok-4", "workspace": "isolated"}).ask("q", schema=SCHEMA)
    assert res.ok and res.data == {"verdict": "no", "why": "x"}
    assert "--json-schema" in captured["args"] and "--model" in captured["args"]
    assert "--tools" in captured["args"]


def test_grok_prose_reply_to_schema_fails_closed(monkeypatch):
    monkeypatch.setattr(grok_mod, "resolve_binary", lambda *_: "/bin/grok")
    monkeypatch.setattr(grok_mod, "run_cli", lambda a, t, cwd=None: CliResult(True, "Sure, happy to help."))
    res = GrokProvider("grok", {"workspace": "isolated"}).ask("q", schema=SCHEMA)
    assert res.ok is False and "verdict" in res.error


def test_grok_empty_and_failed_cli(monkeypatch):
    monkeypatch.setattr(grok_mod, "resolve_binary", lambda *_: "/bin/grok")
    monkeypatch.setattr(grok_mod, "run_cli", lambda a, t, cwd=None: CliResult(True, "   "))
    assert GrokProvider("grok", {}).ask("q").ok is False
    monkeypatch.setattr(grok_mod, "run_cli", lambda a, t, cwd=None: CliResult(False, error="exited 1: boom"))
    res = GrokProvider("grok", {}).ask("q")
    assert res.ok is False and "boom" in res.error


# --- codex -------------------------------------------------------------------


def test_strict_schema_rewrites_for_openai():
    loose = {"type": "object", "properties": {"a": {"type": "string"}, "b": {"type": "array", "items": {"type": "object", "properties": {"c": {}}}}}, "required": ["a"]}
    strict = strict_schema(loose)
    assert strict["additionalProperties"] is False
    assert strict["required"] == ["a", "b"]
    assert strict["properties"]["b"]["items"]["additionalProperties"] is False
    assert loose["required"] == ["a"], "input must not be mutated"


def test_codex_not_logged_in_is_unavailable(monkeypatch):
    monkeypatch.setattr(codex_mod, "resolve_binary", lambda *_: "/bin/codex")
    monkeypatch.setattr(codex_mod, "run_cli", lambda a, timeout=None, cwd=None: CliResult(True, "Not logged in"))
    ok, why = CodexProvider("codex", {}).available()
    assert ok is False and "codex login" in why


def test_codex_skips_git_repo_check_for_isolated_dir(monkeypatch):
    monkeypatch.setattr(codex_mod, "resolve_binary", lambda *_: "/bin/codex")
    calls: list[list[str]] = []

    def run(args, timeout, cwd=None):
        calls.append(args)
        if args[1:3] == ["login", "status"]:
            return CliResult(True, "Logged in using ChatGPT")
        out = args[args.index("--output-last-message") + 1]
        Path(out).write_text("hi", encoding="utf-8")
        return CliResult(True, "")

    monkeypatch.setattr(codex_mod, "run_cli", run)
    assert CodexProvider("codex", {}).ask("q").ok
    assert "--skip-git-repo-check" in calls[-1]


def test_codex_reads_last_message_file(monkeypatch):
    monkeypatch.setattr(codex_mod, "resolve_binary", lambda *_: "/bin/codex")
    calls: list[list[str]] = []

    def run(args, timeout, cwd=None):
        calls.append(args)
        if args[1:3] == ["login", "status"]:
            return CliResult(True, "Logged in using ChatGPT")
        out = args[args.index("--output-last-message") + 1]
        with open(out, "w", encoding="utf-8") as fh:
            fh.write('{"verdict": "yes"}')
        return CliResult(True, "banner noise")

    monkeypatch.setattr(codex_mod, "run_cli", run)
    res = CodexProvider("codex", {"model": "gpt-5", "reasoning_effort": "high"}).ask("q", schema=SCHEMA)
    assert res.ok and res.data == {"verdict": "yes"}
    exec_args = calls[-1]
    assert "--output-schema" in exec_args and "--strict-config" in exec_args
    assert exec_args[exec_args.index("--model") + 1] == "gpt-5"
    assert "model_reasoning_effort=high" in exec_args


def test_codex_missing_output_file_is_no_answer(monkeypatch):
    monkeypatch.setattr(codex_mod, "resolve_binary", lambda *_: "/bin/codex")

    def run(args, timeout, cwd=None):
        return CliResult(True, "Logged in" if "login" in args else "ran but wrote nothing")

    monkeypatch.setattr(codex_mod, "run_cli", run)
    res = CodexProvider("codex", {}).ask("q")
    assert res.ok is False and "no final message" in res.error


# --- antigravity -------------------------------------------------------------


MODELS_LISTING = "gemini-x-pro\tGemini X Pro\ngemini-x-flash\tGemini X Flash\n"


def _agy_ready(monkeypatch, ask_stdout: str, ask_ok: bool = True):
    """Stub the CLI: `models` says signed in; anything else returns `ask_stdout`."""
    monkeypatch.setattr(agy_mod, "resolve_binary", lambda *_: "/bin/agy")
    seen: dict[str, Any] = {}

    def run(args, timeout=None, cwd=None):
        if args[1:] == ["models"]:
            return CliResult(True, MODELS_LISTING, "Fetching available models...")
        seen["args"] = args
        seen["cwd"] = cwd
        return CliResult(ask_ok, ask_stdout)

    monkeypatch.setattr(agy_mod, "run_cli", run)
    return seen


def test_antigravity_not_signed_in_is_unavailable(monkeypatch):
    monkeypatch.setattr(agy_mod, "resolve_binary", lambda *_: "/bin/agy")
    monkeypatch.setattr(agy_mod, "run_cli", lambda a, timeout=None, cwd=None: CliResult(
        False, "Error: Please sign in to view available models.", error="exited 1"))
    ok, why = AntigravityProvider("agy", {"workspace": "isolated"}).available()
    assert ok is False and "NOT authenticated" in why


def test_antigravity_signed_in_reports_models(monkeypatch):
    _agy_ready(monkeypatch, "")
    ok, why = AntigravityProvider("agy", {"workspace": "isolated"}).available()
    assert ok is True and "2 models" in why


def test_antigravity_uses_structured_output(monkeypatch):
    envelope = json.dumps({"status": "SUCCESS", "response": "text", "structured_output": {"verdict": "ok"}, "usage": {"total_tokens": 12}})
    seen = _agy_ready(monkeypatch, envelope)
    res = AntigravityProvider("agy", {"workspace": "isolated", "timeout_seconds": 77}).ask("q", schema=SCHEMA)
    assert res.ok and res.data == {"verdict": "ok"} and res.usage["total_tokens"] == 12
    assert seen["args"][seen["args"].index("--print-timeout") + 1] == "77s"
    assert "--json-schema" in seen["args"]


def test_antigravity_non_success_status_fails(monkeypatch):
    _agy_ready(monkeypatch, json.dumps({"status": "ERROR"}))
    assert AntigravityProvider("agy", {"workspace": "isolated"}).ask("q").ok is False


def test_antigravity_missing_required_key_fails_closed(monkeypatch):
    _agy_ready(monkeypatch, json.dumps({"status": "SUCCESS", "response": "t", "structured_output": {"other": 1}}))
    res = AntigravityProvider("agy", {"workspace": "isolated"}).ask("q", schema=SCHEMA)
    assert res.ok is False and "verdict" in res.error


def test_antigravity_unparseable_envelope(monkeypatch):
    _agy_ready(monkeypatch, "not json")
    assert AntigravityProvider("agy", {"workspace": "isolated"}).ask("q").ok is False


# --- openai http -------------------------------------------------------------


def test_openai_http_unavailable_without_key(monkeypatch):
    monkeypatch.delenv("MM_TEST_KEY", raising=False)
    ok, why = OpenAIHttpProvider("openai", {"api_key_env": "MM_TEST_KEY"}).available()
    assert ok is False and "MM_TEST_KEY" in why


def test_openai_http_parses_choice_and_redacts_key(monkeypatch):
    monkeypatch.setenv("MM_TEST_KEY", "sk-secret-123")
    provider = OpenAIHttpProvider("openai", {"api_key_env": "MM_TEST_KEY"})
    sent: dict[str, Any] = {}

    def post(payload):
        sent.update(payload)
        return {"choices": [{"message": {"content": '{"verdict": "fine"}'}}], "usage": {"total_tokens": 5}}

    monkeypatch.setattr(provider, "_post", post)
    res = provider.ask("q", schema=SCHEMA)
    assert res.ok and res.data == {"verdict": "fine"}
    assert sent["response_format"]["json_schema"]["schema"]["additionalProperties"] is False

    def boom(payload):
        raise RuntimeError("bad token sk-secret-123 rejected")  # long enough to be redacted

    monkeypatch.setattr(provider, "_post", boom)
    res = provider.ask("q")
    assert res.ok is False and "sk-secret-123" not in res.error and "[REDACTED]" in res.error


def test_openai_http_short_key_is_not_scrubbed_into_words(monkeypatch):
    monkeypatch.setenv("MM_TEST_KEY", "k")
    provider = OpenAIHttpProvider("openai", {"api_key_env": "MM_TEST_KEY"})

    def boom(payload):
        raise RuntimeError("network down")

    monkeypatch.setattr(provider, "_post", boom)
    assert "network down" in provider.ask("q").error


def test_openai_http_http_error_is_a_failed_response(monkeypatch):
    monkeypatch.setenv("MM_TEST_KEY", "k-test-secret-value")
    provider = OpenAIHttpProvider("openai", {"api_key_env": "MM_TEST_KEY"})

    def post(payload):
        raise urllib.error.HTTPError(provider.api_url, 429, "rate limited", {}, None)

    monkeypatch.setattr(provider, "_post", post)
    res = provider.ask("q")
    assert res.ok is False and "429" in res.error


def test_openai_http_never_opens_a_socket_in_tests(monkeypatch):
    """The conftest socket guard must trip if the real urlopen is reached."""
    monkeypatch.setenv("MM_TEST_KEY", "k-test-secret-value")
    res = OpenAIHttpProvider("openai", {"api_key_env": "MM_TEST_KEY", "timeout_seconds": 1}).ask("q")
    assert res.ok is False and "network access attempted" in res.error
