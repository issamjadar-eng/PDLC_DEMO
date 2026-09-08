"""Grok, via the xAI `grok` CLI on account OAuth.

No API key required: the CLI holds its own per-machine OAuth, so usage draws on
the account's plan rather than metered API billing.

READ-ONLY BY CONSTRUCTION. The CLI is an agent whose built-in tools include a
terminal and file editing. The adapter passes `--tools` with an allowlist of
read tools only (`read_file,list_dir,grep` by default) and disables web search,
so the model can gather context from the project but has no tool that writes
or executes — verified live by the skill's `verify` action rather than assumed.
Note that the CLI executes tools only inside a directory it trusts (one the
user has opened it in); in an untrusted temporary directory it answers from
the prompt alone.

STRUCTURED OUTPUT HAS TWO MODES, AND THE CHOICE IS LOAD-BEARING. With the
CLI's own `--json-schema`, the model's *first* turn is constrained to the
schema — and when that turn is a narration ("I'll read the file first…") it is
forced into the JSON shape and the run ends at one turn, tools never called
(measured: 0 of 2 reads with the flag, 3 of 3 without, same prompt). So:

- `schema_mode: cli`    — pass `--json-schema`; the CLI validates and returns
                          `structuredOutput`. Right for prompt-only asks.
- `schema_mode: prompt` — ask for the schema in the prompt and parse the last
                          substantive object out of the text stream with
                          `jsonx.best_object`. Right when the model must use
                          tools first (a `project` workspace).
- `schema_mode: auto`   — (default) `prompt` in a `project` workspace, `cli`
                          in an `isolated` one.

Output contract: a JSON envelope (`--output-format json`). Current versions
carry ``usage`` and ``num_turns``, plus an already-parsed ``structuredOutput``
object when `--json-schema` was passed; the adapter trusts that object and its
companion ``stopReason`` / ``structuredOutputError`` exclusively in `cli` mode.
"""

from __future__ import annotations

import json
from typing import Any

from .. import jsonx
from ..base import Provider, resolve_binary, run_cli
from ..types import Response

#: Read-only built-in tools, as the CLI names them. The allowlist is the guard.
DEFAULT_READ_TOOLS = "read_file,list_dir,grep"

#: stopReason values that mean the model finished on its own terms.
_CLEAN_STOPS = frozenset({"end_turn", "stop", "completed", "end"})

SCHEMA_MODES = ("auto", "cli", "prompt")

SCHEMA_INSTRUCTION = (
    "\n\nWhen you have finished, reply with ONE JSON object and nothing after it. "
    "It must match this JSON Schema exactly:\n{schema}\n"
)


class GrokProvider(Provider):
    def __init__(self, name: str, cfg: dict[str, Any]) -> None:
        super().__init__(name, cfg)
        self.command = cfg.get("command", "grok")
        self.model = cfg.get("model")
        self.max_turns = cfg.get("max_turns")
        self.read_tools = cfg.get("read_tools", DEFAULT_READ_TOOLS)
        self.web_search = bool(cfg.get("web_search", False))
        mode = str(cfg.get("schema_mode", "auto")).lower()
        self.schema_mode = mode if mode in SCHEMA_MODES else "auto"

    def uses_cli_schema(self) -> bool:
        """Whether a schema goes to the CLI (`--json-schema`) or into the prompt."""
        if self.schema_mode == "auto":
            return self.workspace == "isolated"
        return self.schema_mode == "cli"

    def available(self) -> tuple[bool, str]:
        resolved = resolve_binary(self.command)
        if not resolved:
            return False, f"Grok CLI {self.command!r} not found on PATH"
        return True, f"Grok CLI at {resolved}"

    def ask(self, prompt: str, schema: dict[str, Any] | None = None, tag: str = "") -> Response:
        ok, reason = self.available()
        if not ok:
            return Response.failure(self.name, reason, tag)

        cli_schema = bool(schema) and self.uses_cli_schema()
        if schema and not cli_schema:
            prompt = prompt + SCHEMA_INSTRUCTION.format(schema=json.dumps(schema))

        with self.workdir() as work:
            args = [resolve_binary(self.command) or self.command, "-p", prompt,
                    "--cwd", str(work), "--output-format", "json",
                    # Allowlist, not denylist: anything not named here does not
                    # exist for the model — no terminal, no editor, no subagents.
                    "--tools", self.read_tools]
            if not self.web_search:
                args.append("--disable-web-search")
            if cli_schema:
                args += ["--json-schema", json.dumps(schema)]
            if self.model:
                args += ["--model", self.model]
            if self.max_turns:
                args += ["--max-turns", str(self.max_turns)]

            result = run_cli(args, self.timeout, cwd=str(work))

        if not result.ok:
            return Response.failure(self.name, f"Grok CLI {result.error}", tag, result.stdout)

        raw = result.stdout
        if not raw.strip():
            return Response.failure(self.name, "Grok CLI returned empty output", tag)

        envelope = _envelope(raw)
        usage = _usage(envelope)
        text = raw.strip()
        if envelope and isinstance(envelope.get("text"), str) and not schema:
            text = envelope["text"].strip()

        # The envelope says how the run ended. Anything but a clean end of turn
        # (a cancelled run, a budget exhausted mid-thought) is NO ANSWER, even
        # when the text stream holds well-formed interim objects — a first live
        # run produced five "placeholder" objects and no conclusion exactly so.
        if envelope:
            stop = envelope.get("stopReason")
            if stop is not None and stop not in _CLEAN_STOPS:
                return Response.failure(
                    self.name,
                    f"Grok run ended with stopReason={stop!r}"
                    + (f": {envelope['structuredOutputError']}"
                       if envelope.get("structuredOutputError") else ""),
                    tag, raw,
                )

        if not schema:
            return Response.success(self.name, text=text, tag=tag, raw=raw, usage=usage)

        required = jsonx.first_required_key(schema)
        if cli_schema and envelope and "structuredOutput" in envelope:
            # This CLI version validates the schema itself. Trust its verdict
            # exclusively: a null here means the model did not produce
            # conforming output, and scraping the text stream instead would
            # re-open the fail-open path this adapter exists to close.
            data = envelope.get("structuredOutput")
            if not isinstance(data, dict) or (required and required not in data):
                return Response.failure(
                    self.name,
                    "Grok produced no structured output"
                    + (f": {envelope['structuredOutputError']}"
                       if envelope.get("structuredOutputError") else ""),
                    tag, raw,
                )
            return Response.success(self.name, text=text, data=data, tag=tag, raw=raw, usage=usage)

        # Prompt-mode schema (or an old CLI): the answer is the last substantive
        # object in the text stream — after the narration and any interim pings.
        source = envelope["text"] if envelope and isinstance(envelope.get("text"), str) else raw
        data = jsonx.best_object(source, required_key=required)
        if data is None:
            return Response.failure(
                self.name,
                f"no object with required key {required!r} in Grok output: {raw[:200]}",
                tag, raw,
            )
        return Response.success(self.name, text=text, data=data, tag=tag, raw=raw, usage=usage)


def _envelope(raw: str) -> dict[str, Any] | None:
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return None
    return parsed if isinstance(parsed, dict) else None


def _usage(envelope: dict[str, Any] | None) -> dict[str, Any] | None:
    """Token usage plus the agent-turn count — the number that reveals roaming."""
    if not envelope:
        return None
    usage = envelope.get("usage")
    usage = dict(usage) if isinstance(usage, dict) else {}
    if "num_turns" in envelope:
        usage["num_turns"] = envelope["num_turns"]
    if "total_cost_usd" in envelope:
        usage["total_cost_usd"] = envelope["total_cost_usd"]
    return usage or None
