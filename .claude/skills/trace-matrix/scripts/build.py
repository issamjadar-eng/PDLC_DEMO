"""trace-matrix build CLI.

Usage:
    python build.py [--repo PATH] [--dhf NAME] [--check]

Reads `trace-matrix.yml` at the repo root and emits per-DHF trace-matrix.md
+ trace-matrix.json via the adapter-loader pipeline.

Adapter resolution (see `adapter_api.load_adapter`):
  1. Project override at `tools/project-console/trace-matrix/adapters/<layer>.py`
  2. Skill default at `scripts/parsers/defaults/<layer>.py`

Build is always deterministic — no LLM calls. LLM-powered adapter
generation lives in the `init` action, not here.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Allow running both as a module and as a script.
SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from adapter_api import ParserResult, load_adapter  # noqa: E402
from graph import LAYER_TITLES, Layer, build as build_graph  # noqa: E402
from emit import to_sidecar, write_json, write_markdown  # noqa: E402


def _load_yaml(path: Path) -> dict:
    """Tiny YAML loader sufficient for trace-matrix.yml."""
    try:
        import yaml  # type: ignore

        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except ImportError:
        pass
    return _mini_yaml(path.read_text(encoding="utf-8"))


def _mini_yaml(text: str) -> dict:
    import re

    lines = [ln.rstrip() for ln in text.splitlines() if ln.strip() and not ln.lstrip().startswith("#")]

    def parse_block(idx: int, indent: int):
        result = None
        while idx < len(lines):
            line = lines[idx]
            cur_indent = len(line) - len(line.lstrip())
            if cur_indent < indent:
                return result, idx
            stripped = line.strip()
            if stripped.startswith("- "):
                if result is None:
                    result = []
                item_text = stripped[2:]
                if ":" in item_text and not item_text.endswith(":"):
                    k, v = item_text.split(":", 1)
                    item = {k.strip(): _scalar(v.strip())}
                    idx += 1
                    rest, idx = parse_block(idx, cur_indent + 2)
                    if isinstance(rest, dict):
                        item.update(rest)
                    result.append(item)
                elif item_text.endswith(":"):
                    item = {item_text[:-1].strip(): None}
                    idx += 1
                    rest, idx = parse_block(idx, cur_indent + 2)
                    if rest is not None:
                        item[item_text[:-1].strip()] = rest
                    result.append(item)
                else:
                    result.append(_scalar(item_text))
                    idx += 1
            elif ":" in stripped:
                k, v = stripped.split(":", 1)
                k = k.strip()
                v = v.strip()
                if result is None:
                    result = {}
                if v == "":
                    idx += 1
                    sub, idx = parse_block(idx, cur_indent + 2)
                    result[k] = sub
                else:
                    result[k] = _scalar(v)
                    idx += 1
            else:
                idx += 1
        return result, idx

    def _scalar(s: str):
        if s == "" or s.lower() == "null" or s == "~":
            return None
        if s.lower() == "true":
            return True
        if s.lower() == "false":
            return False
        if re.fullmatch(r"-?\d+", s):
            return int(s)
        if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
            return s[1:-1]
        return s

    parsed, _ = parse_block(0, 0)
    return parsed or {}


def _sources(layer_cfg: dict | None) -> list[str]:
    """Normalize source: to a list. Accepts str, list[str], or None."""
    if not layer_cfg:
        return []
    src = layer_cfg.get("source")
    if src is None:
        return []
    if isinstance(src, str):
        return [src]
    if isinstance(src, list):
        return [s for s in src if s]
    return []


def _run_layer(
    layer_key: str,
    layer_cfg: dict,
    repo_root: Path,
) -> tuple[list[dict], list[str], dict, str, list[str]]:
    """Run the adapter for one layer.

    Returns (nodes, warnings, extras, adapter_label, source_files).
    """
    sources = _sources(layer_cfg)
    adapter_name = (layer_cfg or {}).get("adapter")
    parse_fn, adapter_label = load_adapter(
        layer_key, repo_root, SKILL_DIR, adapter_name=adapter_name
    )

    all_nodes: list[dict] = []
    all_warnings: list[str] = []
    merged_extras: dict = {}
    resolved_sources: list[str] = []

    # The V&V layer is special: its default adapter reads nothing and
    # relies on DI-derived extras. We still call it so project overrides
    # can do something different.
    if not sources:
        try:
            result = parse_fn(None, layer_cfg or {})
        except TypeError:
            # Some adapters may not accept None
            result = ParserResult()
        all_nodes.extend(result.nodes)
        all_warnings.extend(result.warnings)
        if isinstance(result.extras, dict):
            merged_extras.update(result.extras)
        return all_nodes, all_warnings, merged_extras, adapter_label, resolved_sources

    for src in sources:
        p = repo_root / src
        resolved_sources.append(str(src))
        result = parse_fn(p, layer_cfg or {})
        all_nodes.extend(result.nodes)
        all_warnings.extend(result.warnings)
        if isinstance(result.extras, dict):
            for k, v in result.extras.items():
                if isinstance(v, list) and k in merged_extras and isinstance(merged_extras[k], list):
                    merged_extras[k].extend(v)
                else:
                    merged_extras[k] = v

    return all_nodes, all_warnings, merged_extras, adapter_label, resolved_sources


def build_dhf(repo_root: Path, dhf_cfg: dict) -> tuple[str, dict, dict]:
    name = dhf_cfg["name"]
    layers_cfg = dhf_cfg.get("layers", {}) or {}
    risk_cfg = dhf_cfg.get("risk")

    # Layer order matches graph.LAYER_ORDER. The software layer is optional —
    # DHFs that don't declare it get an empty layer rendered with
    # missing_reason=source_missing, which the emit/console layers handle.
    layer_specs = [
        ("user_needs", layers_cfg.get("user_needs", {}) or {}),
        ("design_inputs", layers_cfg.get("design_inputs", {}) or {}),
        ("software", layers_cfg.get("software", {}) or {}),
        ("architecture", layers_cfg.get("architecture", {}) or {}),
        ("vnv", layers_cfg.get("vnv", {}) or {}),
        ("risk", risk_cfg or layers_cfg.get("risk", {}) or {}),
    ]

    adapters_used: dict[str, str] = {}
    source_map: dict[str, list[str]] = {}
    layers: list[Layer] = []
    di_derived_vnv: list[dict] = []

    for key, cfg in layer_specs:
        nodes, warnings, extras, label, srcs = _run_layer(key, cfg, repo_root)
        adapters_used[key] = label
        source_map[key] = srcs

        if key == "design_inputs":
            di_derived_vnv = extras.get("vnv_nodes", []) or []

        if key == "vnv" and not nodes and di_derived_vnv:
            # Default V&V adapter yields nothing; merge in the DI-derived VERs.
            nodes = di_derived_vnv

        missing_reason = None
        if not nodes:
            if key == "vnv":
                missing_reason = "no_vnv_ids_found"
            elif not srcs:
                missing_reason = "source_missing"
            else:
                missing_reason = "no_items_parsed"

        edges_known = True
        if key == "architecture":
            edges_known = bool(extras.get("edges_known", False))

        layers.append(
            Layer(
                key=key,
                title=LAYER_TITLES[key],
                id_prefix=cfg.get("id_prefix", ""),
                items=nodes,
                missing_reason=missing_reason if not nodes else None,
                edges_known=edges_known,
                warnings=warnings,
                source_files=srcs,
            )
        )

    graph = build_graph(layers)
    sidecar = to_sidecar(name, graph)
    return name, sidecar, adapters_used


def main() -> int:
    ap = argparse.ArgumentParser(description="Build the trace matrix for one or all DHFs.")
    ap.add_argument("--repo", type=Path, default=Path.cwd(), help="Project root (defaults to CWD)")
    ap.add_argument("--dhf", type=str, default=None, help="Build only this DHF")
    ap.add_argument("--check", action="store_true", help="Dry run — no files written; exit 1 on gaps")
    args = ap.parse_args()

    repo = args.repo.resolve()
    cfg_path = repo / "trace-matrix.yml"
    if not cfg_path.exists():
        print(f"error: {cfg_path} not found. Run /trace-matrix init first.", file=sys.stderr)
        return 2

    cfg = _load_yaml(cfg_path)
    dhfs_cfg = cfg.get("dhfs") or []
    if args.dhf:
        dhfs_cfg = [d for d in dhfs_cfg if d.get("name") == args.dhf]
        if not dhfs_cfg:
            print(f"error: DHF '{args.dhf}' not in trace-matrix.yml", file=sys.stderr)
            return 2

    any_gap = False
    print(f"trace-matrix build — {len(dhfs_cfg)} DHF(s)")
    print()
    for dhf_cfg in dhfs_cfg:
        name, sidecar, adapters = build_dhf(repo, dhf_cfg)
        out_dir = repo / dhf_cfg.get(
            "output_dir",
            f"docs/project/console/{name}",
        )

        stats = sidecar["stats"]
        gaps = sidecar["gaps"]
        gap_count = sum(len(v) for v in gaps["orphans"].values()) + len(gaps["broken_refs"])
        if gap_count:
            any_gap = True

        print(f"  {name}")
        for layer_key in ["user_needs", "design_inputs", "software", "architecture", "vnv", "risk"]:
            s = stats.get(layer_key, {})
            extra = ""
            if "missing_reason" in s:
                extra = f"  [{s['missing_reason']}]"
            elif layer_key == "architecture" and not s.get("edges_known", True):
                extra = "  [edges unknown]"
            adapter_label = adapters.get(layer_key, "?")
            if adapter_label.startswith("shared:"):
                adapter_tag = adapter_label.split(":", 1)[1].strip() or "shared"
            elif adapter_label.startswith("project:"):
                adapter_tag = "proj"
            else:
                adapter_tag = "deflt"
            print(
                f"    {layer_key:14} count={s.get('count', 0):3}  "
                f"fwd={s.get('with_forward', 0):3}  orphan={s.get('orphan', 0):3}"
                f"  [{adapter_tag}]{extra}"
            )
        if gaps["broken_refs"]:
            print(f"    broken refs: {len(gaps['broken_refs'])}")
        print(f"    → {out_dir}/console_trace_matrix.{{md,json}}")
        print()

        if not args.check:
            write_json(out_dir / "console_trace_matrix.json", sidecar)
            write_markdown(out_dir / "console_trace_matrix.md", sidecar)

    if args.check and any_gap:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
