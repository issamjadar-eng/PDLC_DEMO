"""multimodel — query several independent LLM providers and get structured answers.

A small, portable, dependency-free layer for talking to more than one model
provider at once. Domain-agnostic by design: it knows how to dispatch prompts
and parse structured replies, and nothing about what the replies mean.

    from multimodel import Council, load_config

    council = Council.from_config(load_config(), role="challenger")

    # Same question to everyone
    for r in council.ask_all("Is this argument sound?", schema=MY_SCHEMA):
        print(r.provider, r.ok, r.data)

    # Different question per provider, round-robin over labels
    asks = [
        Ask(prompt=build(tag), provider=name, schema=MY_SCHEMA, tag=tag)
        for name, tag in council.distribute(["security", "performance", "clarity"])
    ]
    responses = council.run(asks)

Design rules worth preserving if you extend it:

- **Fail closed.** `Response.ok is False` means *no answer*, never a negative
  answer. A caller that reads a failed response as agreement has a bug.
- **Never raise for an expected failure.** One unreachable provider must not
  abort a fan-out; it returns an unsuccessful Response instead.
- **No credential handling.** Providers read the environment or rely on a CLI's
  own OAuth. This package never loads .env files or writes tokens.
- **Prefer subscription OAuth over API keys** where a provider offers both.
- **Standard library only.** Nothing to install; the package runs anywhere the
  host project's Python does.
"""

from .base import PROBE_PROMPT, PROBE_SCHEMA, Provider, resolve_binary, run_cli
from .config import ConfigError, external_send_allowed, load_config, project_root
from .council import Council
from .registry import REGISTRY, build_provider, register
from .types import Ask, ProbeResult, ProviderNotAvailable, Response
from .verify import VerifyResult, verify_all, verify_provider

__version__ = "1.0.0"

__all__ = [
    "Ask",
    "ConfigError",
    "Council",
    "PROBE_PROMPT",
    "PROBE_SCHEMA",
    "VerifyResult",
    "ProbeResult",
    "Provider",
    "ProviderNotAvailable",
    "REGISTRY",
    "Response",
    "build_provider",
    "external_send_allowed",
    "load_config",
    "project_root",
    "register",
    "resolve_binary",
    "run_cli",
    "verify_all",
    "verify_provider",
]
