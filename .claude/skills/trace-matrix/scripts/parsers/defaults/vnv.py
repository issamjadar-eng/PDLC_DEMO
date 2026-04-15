"""Default V&V parser.

In most projects, verification protocols are not captured in a standalone
document at v1 — they live inline in the Design Inputs doc's
`Verification Method` column. The default V&V parser reflects this: it
**does not read any source file of its own**. Instead, the build
orchestrator hands it the DI parser's `extras["vnv_nodes"]` payload.

This adapter is therefore a trivial pass-through. It exists so the layer
has a well-defined home in the adapter system and projects can override it
(e.g. when a real `verification-protocols.md` appears).
"""
from __future__ import annotations

from pathlib import Path

from adapter_api import ParserResult


def parse(path: Path, layer_cfg: dict) -> ParserResult:
    # The build orchestrator calls this even when `source` is null; we
    # honour that by returning an empty result. The orchestrator then
    # merges in `extras["vnv_nodes"]` from the DI parse. A project that
    # wants real V&V parsing generates an adapter override.
    return ParserResult(warnings=["v1 default: V&V nodes derived from DI verification column"])
