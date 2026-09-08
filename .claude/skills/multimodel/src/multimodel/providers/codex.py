"""OpenAI, via the `codex` CLI on ChatGPT OAuth.

Signing into Codex with a ChatGPT account draws on the plan's included usage
credits; signing in with an API key bills separately at standard API rates. Same
models, different meter — and OAuth means no key on disk. Use
`OpenAIHttpProvider` only when metered billing is specifically wanted.

Two implementation notes:

- `--output-last-message FILE` writes only the agent's final message, so there
  is no stream to mis-parse.
- OpenAI's structured output rejects any schema that does not set
  ``additionalProperties: false`` and list *every* property in ``required``.
  That strictness is applied here rather than in the shared schema, so a looser
  schema that other providers accept is not broken to satisfy this one.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any

from .. import jsonx
from ..base import Provider, resolve_binary, run_cli, tail
from ..types import Response


def strict_schema(schema: dict[str, Any]) -> dict[str, Any]:
    """Rewrite a JSON Schema into the strict form OpenAI requires."""
    if not isinstance(schema, dict):
        return schema

    result = dict(schema)
    if result.get("type") == "object":
        properties = result.get("properties", {})
        result["properties"] = {k: strict_schema(v) for k, v in properties.items()}
        result["additionalProperties"] = False
        result["required"] = list(properties)
    elif result.get("type") == "array" and isinstance(result.get("items"), dict):
        result["items"] = strict_schema(result["items"])
    return result


class CodexProvider(Provider):
    def __init__(self, name: str, cfg: dict[str, Any]) -> None:
        super().__init__(name, cfg)
        self.command = cfg.get("command", "codex")
        self.model = cfg.get("model")
        self.reasoning_effort = cfg.get("reasoning_effort")
        self.sandbox = cfg.get("sandbox", "read-only")

    def available(self) -> tuple[bool, str]:
        resolved = resolve_binary(self.command)
        if not resolved:
            return False, (
                f"Codex CLI {self.command!r} not found. Install: npm i -g @openai/codex"
            )

        # Ask the tool, not the filesystem — installed is not authenticated.
        status = run_cli([resolved, "login", "status"], timeout=30)
        combined = f"{status.stdout}{status.stderr}".strip()
        if not status.ok or "not logged in" in combined.lower():
            return False, (
                "Codex CLI installed but NOT logged in. Run `codex login` and choose "
                "'Sign in with ChatGPT' (the API key option bills separately)."
            )
        first_line = combined.splitlines()[0][:60] if combined else "logged in"
        return True, f"Codex CLI at {resolved} ({first_line})"

    def ask(self, prompt: str, schema: dict[str, Any] | None = None, tag: str = "") -> Response:
        ok, reason = self.available()
        if not ok:
            return Response.failure(self.name, reason, tag)
        if self.workspace == "project" and self.sandbox != "read-only":
            # The read-only sandbox IS the guarantee that project access cannot
            # turn into a write. Refuse rather than run with a looser one.
            return Response.failure(
                self.name,
                f"refusing project workspace with sandbox={self.sandbox!r}; "
                "only 'read-only' is allowed when the agent can see the project",
                tag,
            )

        binary = resolve_binary(self.command) or self.command

        with tempfile.TemporaryDirectory(prefix="mm-codex-") as tmp, self.workdir() as work:
            tmp_path = Path(tmp)
            output_file = tmp_path / "last-message.txt"

            args = [
                binary, "exec",
                "--sandbox", self.sandbox,
                # The agent's working root — isolated by default (see base.py).
                # An empty temp dir is not a git repo, and Codex refuses to run
                # outside one unless told the caller knows.
                "--cd", str(work),
                "--skip-git-repo-check",
                # Fail loud on an unrecognised config key rather than silently
                # ignoring it and quietly downgrading the model.
                "--strict-config",
                "--output-last-message", str(output_file),
                "--color", "never",
            ]
            if schema:
                schema_file = tmp_path / "schema.json"
                schema_file.write_text(json.dumps(strict_schema(schema)), encoding="utf-8")
                args += ["--output-schema", str(schema_file)]
            if self.model:
                args += ["--model", self.model]
            if self.reasoning_effort:
                args += ["-c", f"model_reasoning_effort={self.reasoning_effort}"]
            args.append(prompt)

            result = run_cli(args, self.timeout, cwd=str(work))
            if not result.ok:
                return Response.failure(self.name, f"Codex CLI {result.error}", tag, result.stdout)

            if not output_file.exists():
                return Response.failure(
                    self.name,
                    "Codex wrote no final message; treating as no answer",
                    tag, tail(result.stdout),
                )
            raw = output_file.read_text(encoding="utf-8").strip()

        if not raw:
            return Response.failure(self.name, "Codex returned an empty message", tag)

        if not schema:
            return Response.success(self.name, text=raw, tag=tag, raw=raw)

        required = jsonx.first_required_key(schema)
        data = jsonx.best_object(raw, required_key=required)
        if data is None:
            return Response.failure(
                self.name,
                f"no object with required key {required!r} in Codex output: {raw[:200]}",
                tag, raw,
            )
        return Response.success(self.name, text=raw, data=data, tag=tag, raw=raw)
