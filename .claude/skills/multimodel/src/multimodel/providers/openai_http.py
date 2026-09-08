"""OpenAI over the HTTP API with a key — the METERED path.

Present for completeness and for environments with no interactive login (CI,
containers). Prefer `CodexProvider`, which reaches the same models through a
ChatGPT subscription instead of per-token billing.

Reads its key from the environment only. This package never loads a .env file or
touches credential storage — that is the host project's business. Standard
library `urllib` keeps the layer dependency-free.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any

from .. import jsonx
from ..base import Provider
from ..types import Response
from .codex import strict_schema

API_URL = "https://api.openai.com/v1/chat/completions"


class OpenAIHttpProvider(Provider):
    def __init__(self, name: str, cfg: dict[str, Any]) -> None:
        super().__init__(name, cfg)
        self.api_key_env = cfg.get("api_key_env", "OPENAI_API_KEY")
        self.model = cfg.get("model", "gpt-5")
        self.api_url = cfg.get("api_url", API_URL)

    def _key(self) -> str | None:
        return os.environ.get(self.api_key_env)

    def available(self) -> tuple[bool, str]:
        if not self._key():
            return False, (
                f"{self.api_key_env} is not set in the environment. "
                "Prefer the codex provider (ChatGPT OAuth) over metered API billing."
            )
        return True, f"{self.api_key_env} present"

    def _post(self, payload: dict[str, Any]) -> dict[str, Any]:
        request = urllib.request.Request(
            self.api_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self._key()}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=self.timeout) as reply:  # noqa: S310
            return json.loads(reply.read().decode("utf-8"))

    def ask(self, prompt: str, schema: dict[str, Any] | None = None, tag: str = "") -> Response:
        ok, reason = self.available()
        if not ok:
            return Response.failure(self.name, reason, tag)

        payload: dict[str, Any] = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
        }
        if schema:
            payload["response_format"] = {
                "type": "json_schema",
                "json_schema": {
                    "name": "response",
                    "schema": strict_schema(schema),
                    "strict": False,
                },
            }

        try:
            body = self._post(payload)
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", "replace")[:300] if exc.fp else ""
            return Response.failure(
                self.name, self._scrub(f"HTTP {exc.code}: {detail or exc.reason}"), tag
            )
        except Exception as exc:  # noqa: BLE001 - surfaced as a failed Response
            return Response.failure(self.name, self._scrub(f"request failed: {exc}"), tag)

        try:
            text = body["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError):
            return Response.failure(
                self.name, f"unexpected response shape: {json.dumps(body)[:200]}", tag
            )

        usage = body.get("usage")
        if not schema:
            return Response.success(self.name, text=text, tag=tag, raw=text, usage=usage)

        required = jsonx.first_required_key(schema)
        data = jsonx.best_object(text, required_key=required)
        if data is None:
            return Response.failure(
                self.name, f"no object with required key {required!r}: {text[:200]}", tag, text
            )
        return Response.success(
            self.name, text=text, data=data, tag=tag, raw=text, usage=usage
        )

    def _scrub(self, message: str) -> str:
        """Never let a key reach a log or a caller's error string."""
        key = self._key()
        # Only a real-length secret is worth redacting; replacing a trivially
        # short string would mangle unrelated words in the diagnostic.
        return message.replace(key, "[REDACTED]") if key and len(key) >= 8 else message
