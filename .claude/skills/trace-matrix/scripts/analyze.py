"""trace-matrix analyze — the rational check used by `/trace-matrix init`.

For each layer of a DHF:
  1. Load the adapter (project override if present, else skill default).
  2. Run it against the configured source(s).
  3. Produce a RationalCheck verdict.

Emits a JSON report so the `/trace-matrix init` action (driven by
SKILL.md instructions) can decide which layers need an LLM-generated
adapter.

This script does not call any LLM itself. It produces the verdict; the
Claude-driven init flow reads the verdict and, for each failing layer,
reads the source doc and writes a bespoke adapter to
`tools/project-console/trace-matrix/adapters/<layer>.py`.
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from adapter_api import ParserResult, load_adapter, rational_check  # noqa: E402
from build import _load_yaml, _sources  # noqa: E402
from graph import LAYER_ORDER as LAYER_KEYS  # noqa: E402 — single source of truth for layer enumeration


def analyze_layer(
    layer_key: str, layer_cfg: dict, repo_root: Path
) -> dict:
    parse_fn, adapter_label = load_adapter(layer_key, repo_root, SKILL_DIR)
    sources = _sources(layer_cfg)
    id_prefix = (layer_cfg or {}).get("id_prefix")

    results: list[dict] = []
    all_nodes: list[dict] = []
    all_warnings: list[str] = []
    any_source_present = False

    if not sources:
        try:
            res = parse_fn(None, layer_cfg or {})
        except TypeError:
            res = ParserResult()
        all_nodes.extend(res.nodes)
        all_warnings.extend(res.warnings)
        results.append({"source": None, "node_count": len(res.nodes)})
    else:
        for src in sources:
            p = repo_root / src
            exists = p.exists()
            if exists:
                any_source_present = True
                # "source_placeholder" detection: any file whose body
                # contains the medtech-docs awaiting-content marker is
                # treated as source_empty for rational-check purposes.
                try:
                    body = p.read_text(encoding="utf-8", errors="ignore")
                    if "<!-- Status: awaiting-content -->" in body:
                        any_source_present = False
                except OSError:
                    any_source_present = False
            if not exists:
                results.append({"source": str(src), "exists": False, "node_count": 0})
                continue
            res = parse_fn(p, layer_cfg or {})
            all_nodes.extend(res.nodes)
            all_warnings.extend(res.warnings)
            results.append(
                {"source": str(src), "exists": True, "node_count": len(res.nodes)}
            )

    check = rational_check(
        ParserResult(nodes=all_nodes),
        id_prefix,
        source_present=any_source_present,
        layer_key=layer_key,
    )
    return {
        "layer": layer_key,
        "adapter": adapter_label,
        "sources": results,
        "warnings": all_warnings,
        "check": asdict(check),
    }


def analyze_dhf(dhf_cfg: dict, repo_root: Path) -> dict:
    layers_cfg = dhf_cfg.get("layers", {}) or {}
    risk_cfg = dhf_cfg.get("risk")

    layer_verdicts: list[dict] = []
    for key in LAYER_KEYS:
        if key == "risk":
            cfg = risk_cfg or {}
        else:
            cfg = layers_cfg.get(key, {}) or {}
        layer_verdicts.append(analyze_layer(key, cfg, repo_root))

    fail_count = sum(1 for v in layer_verdicts if not v["check"]["ok"])
    return {
        "dhf": dhf_cfg.get("name"),
        "layers": layer_verdicts,
        "fail_count": fail_count,
        "needs_adapters": [v["layer"] for v in layer_verdicts if not v["check"]["ok"]],
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Rational-check each layer against its current adapter.")
    ap.add_argument("--repo", type=Path, default=Path.cwd())
    ap.add_argument("--dhf", type=str, default=None, help="Restrict to one DHF")
    ap.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    args = ap.parse_args()

    repo = args.repo.resolve()
    cfg_path = repo / "trace-matrix.yml"
    if not cfg_path.exists():
        print(f"error: {cfg_path} not found.", file=sys.stderr)
        return 2

    cfg = _load_yaml(cfg_path)
    dhfs_cfg = cfg.get("dhfs") or []
    if args.dhf:
        dhfs_cfg = [d for d in dhfs_cfg if d.get("name") == args.dhf]

    report = {"dhfs": [analyze_dhf(d, repo) for d in dhfs_cfg]}

    if args.json:
        print(json.dumps(report, indent=2))
        return 0

    # Human summary
    for d in report["dhfs"]:
        print(f"\n{d['dhf']}")
        for v in d["layers"]:
            ok = "✓" if v["check"]["ok"] else "✗"
            label = v["adapter"].split(":", 1)[0]
            print(
                f"  {ok} {v['layer']:14} [{label:7}] {v['check']['node_count']:4} nodes — {v['check']['reason']}"
            )
        if d["needs_adapters"]:
            print(f"  needs generated adapters: {', '.join(d['needs_adapters'])}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
