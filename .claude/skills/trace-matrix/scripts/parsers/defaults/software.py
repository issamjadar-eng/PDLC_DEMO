"""Default Software Requirements parser.

The software layer is optional — many DHFs (especially device-level
"system" DHFs) don't have a separate software-requirements artifact and
trace directly from Design Inputs to V&V. The default parser is a no-op
pass-through so the layer renders empty without complaint.

Item DHFs whose software requirements live in a Jira mirror (Stories
under `_jira/<arch>/<version>/stories.md`) should set
`adapter: jira-mirror` on the layer in `trace-matrix.yml` to invoke the
shared adapter at `parsers/jira_mirror.py`. Other shapes call for a
project-side adapter at `tools/project-console/trace-matrix/adapters/software.py`.
"""
from __future__ import annotations

from pathlib import Path

from adapter_api import ParserResult


def parse(path: Path, layer_cfg: dict) -> ParserResult:
    return ParserResult()
