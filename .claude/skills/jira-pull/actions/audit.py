"""
/jira-pull audit — emit drift.json + drift.md from the rule registry,
comparing the cached Jira snapshot against the live DTM/HTM xlsx parse.

Usage:
  python -m actions.audit --dhf <leaf> --version <id>
  python -m actions.audit --all

Reads:
  - docs/project/_jira/<arch>/<ver>/{epics,stories,hazards,tests}.json
  - dhfs[].evidence.design_traceability_matrix[]
  - jira_pull.exempt_filters, jira_pull.severity_overrides (optional)

Writes (per DHF×version):
  - <mirror_root>/<arch>/<ver>/drift.json
  - <mirror_root>/<arch>/<ver>/drift.md

The audit is read-only against Jira (uses committed mirror, not the MCP).
"""

from __future__ import annotations

import argparse
import datetime as dt
import importlib.util
import json
import sys
import types
from collections import OrderedDict
from pathlib import Path
from typing import Any, Dict, List, Tuple


# ─── Synthetic-package loader ────────────────────────────────────────────────
# The skill folder has a hyphen (`jira-pull`) which Python won't accept as a
# package identifier, so the lib modules can't be imported via normal package
# resolution. We register them under a synthetic `lib` package keyed off this
# file's location.

def _load_lib():
    here = Path(__file__).resolve().parent
    lib_dir = here.parent / "lib"
    if "lib" not in sys.modules:
        pkg = types.ModuleType("lib")
        pkg.__path__ = [str(lib_dir)]
        sys.modules["lib"] = pkg
    for name in ("config", "drift_rules", "jira_client", "dtm_reader", "htm_reader"):
        if f"lib.{name}" in sys.modules:
            continue
        spec = importlib.util.spec_from_file_location(f"lib.{name}", lib_dir / f"{name}.py")
        mod = importlib.util.module_from_spec(spec)
        sys.modules[f"lib.{name}"] = mod
        spec.loader.exec_module(mod)
    return (sys.modules["lib.config"],
            sys.modules["lib.drift_rules"],
            sys.modules["lib.jira_client"],
            sys.modules["lib.dtm_reader"],
            sys.modules["lib.htm_reader"])


# ─── Per-pair audit ──────────────────────────────────────────────────────────


def _audit_one(cfg, drift_rules, jira_client, dtm_reader, htm_reader, dhf, version_id):
    """Run all 21 rules against one (DHF, version) pair. Returns
    (drift_payload_dict, mirror_dir_Path) — caller writes the files."""
    schema = None
    for s in dhf.dtm_schemas:
        if s.version == version_id:
            schema = s
            break
    if schema is None:
        raise KeyError(f"DHF {dhf.leaf!r} has no DTM schema for version {version_id!r}")

    htm_schema = None
    for s in dhf.htm_schemas:
        if s.version == version_id:
            htm_schema = s
            break

    j = jira_client.load_state(cfg, dhf, version_id)
    dtm_state = dtm_reader.read(schema, cfg.project_root)
    htm_state = None
    htm_load_error = None
    if htm_schema is not None:
        try:
            htm_state = htm_reader.read(htm_schema, cfg.project_root)
        except (FileNotFoundError, KeyError) as e:
            htm_load_error = f"{type(e).__name__}: {e}"

    fix_version_target = j.fix_version
    if not fix_version_target and dhf.jira:
        for v in dhf.jira.versions:
            if v.id == version_id:
                fix_version_target = v.fix_version
                break

    rule_cfg = drift_rules.RuleConfig(
        extractors=dict(schema.extractors or {}),
        exempt_filters=cfg.tuning.exempt_filters,
        severity_overrides=cfg.tuning.severity_overrides,
        di_resolution_fallback=cfg.tuning.di_resolution_fallback,
        design_input_label=cfg.tuning.design_input_label,
        fix_version=fix_version_target,
        dtm_xlsx_path=str((cfg.project_root / schema.xlsx_path).resolve()),
    )

    implemented: List[str] = []
    not_implemented: List[str] = []
    by_rule: "OrderedDict[str, list]" = OrderedDict()
    errors: List[Dict[str, str]] = []

    for rule_id, fn in drift_rules.RULES.items():
        try:
            vs = fn(j, dtm_state, htm_state, rule_cfg)
        except NotImplementedError:
            not_implemented.append(rule_id)
            by_rule[rule_id] = []
            continue
        except Exception as e:  # don't let one bad rule kill the audit
            errors.append({"rule": rule_id, "exception": f"{type(e).__name__}: {e}"})
            by_rule[rule_id] = []
            continue
        implemented.append(rule_id)
        # apply severity overrides post-emit
        if rule_cfg.severity_overrides:
            override = rule_cfg.severity_overrides.get(rule_id)
            if override:
                vs = [drift_rules.Violation(
                    rule=v.rule,
                    severity=override,
                    item_id=v.item_id,
                    item_kind=v.item_kind,
                    message=v.message,
                    resolution_hint=v.resolution_hint,
                    references=v.references,
                ) for v in vs]
        by_rule[rule_id] = vs

    flat_violations: List[dict] = []
    by_sev: Dict[str, int] = {"error": 0, "warning": 0, "info": 0}
    by_cat: Dict[str, int] = {"A": 0, "B": 0, "C": 0}
    by_rule_count: "OrderedDict[str, int]" = OrderedDict()

    for rule_id, vs in by_rule.items():
        by_rule_count[rule_id] = len(vs)
        for v in vs:
            by_sev[v.severity] = by_sev.get(v.severity, 0) + 1
            by_cat[rule_id[0]] = by_cat.get(rule_id[0], 0) + 1
            flat_violations.append({
                "rule": v.rule,
                "severity": v.severity,
                "item_id": v.item_id,
                "item_kind": v.item_kind,
                "message": v.message,
                "resolution_hint": v.resolution_hint,
                "references": dict(v.references or {}),
            })

    fix_version = j.fix_version or ""
    payload = {
        "dhf": dhf.leaf,
        "architecture_name": dhf.architecture_name,
        "arch_slug": dhf.arch_slug,
        "version": version_id,
        "fix_version": fix_version,
        "audit_run_at": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "dtm_source": dtm_state.source_path,
        "htm_source": htm_state.source_path if htm_state else None,
        "htm_load_error": htm_load_error,
        "summary": {
            "violations_total": len(flat_violations),
            "by_severity": by_sev,
            "by_category": by_cat,
            "by_rule": dict(by_rule_count),
            "rules_implemented": implemented,
            "rules_not_implemented": not_implemented,
            "rule_errors": errors,
        },
        "violations": flat_violations,
    }
    mirror_dir = jira_client.mirror_dir(cfg, dhf, version_id)
    return payload, mirror_dir


# ─── Markdown rendering ──────────────────────────────────────────────────────


_RULE_TITLES = {
    "A1": "Jira-only DI Epic",
    "A2": "DTM-only DI",
    "A3": "Jira-only Software item",
    "A4": "DTM-only Software item",
    "A5": "Jira-only Hazard",
    "A6": "HTM-only Hazard",
    "A7": "Jira-only Test Execution",
    "A8": "DTM-only Test reference",
    "B1": "DI without UN",
    "B2": "DI without Software",
    "B3": "DI without V&V",
    "B4": "DI without Hazard",
    "B5": "UN without DI",
    "B6": "Software without parent DI",
    "B7": "Hazard without DI",
    "B8": "Hazard without mitigation or V&V",
    "C1": "Status mismatch",
    "C2": "Summary drift",
    "C3": "Version-scope mismatch",
    "C4": "ID format drift",
    "C5": "Stale working xlsx",
}


def render_md(payload: dict) -> str:
    lines: List[str] = []
    lines.append(f"# Drift Audit — {payload['architecture_name']} / {payload['version']}")
    lines.append("")
    lines.append(f"- **DHF leaf**: `{payload['dhf']}`")
    lines.append(f"- **Architecture name**: {payload['architecture_name']}")
    lines.append(f"- **Fix version**: {payload['fix_version'] or '_(none in mirror metadata)_'}")
    lines.append(f"- **Audit run at**: {payload['audit_run_at']}")
    lines.append(f"- **DTM source**: `{payload['dtm_source']}`")
    lines.append("")
    s = payload["summary"]
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- **Violations total**: {s['violations_total']}")
    sv = s["by_severity"]
    lines.append(f"- **By severity**: error={sv.get('error',0)}, warning={sv.get('warning',0)}, info={sv.get('info',0)}")
    bc = s["by_category"]
    lines.append(f"- **By category**: A={bc.get('A',0)}, B={bc.get('B',0)}, C={bc.get('C',0)}")
    lines.append(f"- **Rules implemented**: {len(s['rules_implemented'])} of {len(s['rules_implemented']) + len(s['rules_not_implemented'])} — {', '.join(s['rules_implemented']) or '_(none)_'}")
    if s["rules_not_implemented"]:
        lines.append(f"- **Rules not yet implemented**: {', '.join(s['rules_not_implemented'])}")
    if s.get("rule_errors"):
        lines.append("- **Rule errors** (rules that raised unexpectedly):")
        for err in s["rule_errors"]:
            lines.append(f"  - `{err['rule']}` — {err['exception']}")
    lines.append("")

    if not payload["violations"]:
        lines.append("## Violations")
        lines.append("")
        lines.append("_No drift detected by the implemented rules._")
        lines.append("")
        return "\n".join(lines)

    lines.append("## Violations")
    lines.append("")
    grouped: "OrderedDict[str, List[dict]]" = OrderedDict()
    for v in payload["violations"]:
        grouped.setdefault(v["rule"], []).append(v)
    for rule_id, vs in grouped.items():
        title = _RULE_TITLES.get(rule_id, rule_id)
        sev = vs[0]["severity"]
        lines.append(f"### {rule_id} — {title} (severity: {sev}, count: {len(vs)})")
        lines.append("")
        for v in vs:
            lines.append(f"- **{v['item_id']}** ({v['item_kind']}) — {v['message']}")
            lines.append(f"  - Resolution: {v['resolution_hint']}")
            refs = v.get("references") or {}
            if refs:
                ref_str = ", ".join(f"`{k}`={v_!r}" for k, v_ in refs.items())
                lines.append(f"  - References: {ref_str}")
        lines.append("")
    return "\n".join(lines)


# ─── CLI ─────────────────────────────────────────────────────────────────────


def _write_outputs(mirror_dir: Path, payload: dict) -> Tuple[Path, Path]:
    mirror_dir.mkdir(parents=True, exist_ok=True)
    json_path = mirror_dir / "drift.json"
    md_path = mirror_dir / "drift.md"
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=False) + "\n")
    md_path.write_text(render_md(payload))
    return json_path, md_path


def _iter_targets(cfg, dhf_leaf: str | None, version_id: str | None) -> List[Tuple[Any, str]]:
    targets: List[Tuple[Any, str]] = []
    for d in cfg.dhfs:
        if dhf_leaf and d.leaf != dhf_leaf:
            continue
        for s in d.dtm_schemas:
            if version_id and s.version != version_id:
                continue
            if d.jira and any(v.id == s.version for v in d.jira.versions):
                targets.append((d, s.version))
    return targets


def main(argv: List[str]) -> int:
    parser = argparse.ArgumentParser(prog="jira-pull audit")
    parser.add_argument("--dhf", help="DHF leaf (project.yml dhfs[].leaf). Omit with --all.")
    parser.add_argument("--version", help="Version id (e.g. v1.0.0). Omit with --all.")
    parser.add_argument("--all", action="store_true", help="Run audit across every (DHF, version) pair with both Jira mirror and DTM schema.")
    parser.add_argument("--dry-run", action="store_true", help="Print the JSON payload to stdout without writing files.")
    args = parser.parse_args(argv)

    if not args.all and not (args.dhf and args.version):
        parser.error("Provide --all OR both --dhf and --version")

    config_mod, drift_rules, jira_client, dtm_reader, htm_reader = _load_lib()
    cfg = config_mod.load()

    targets = _iter_targets(cfg, None if args.all else args.dhf,
                            None if args.all else args.version)
    if not targets:
        print("[jira-pull audit] no DHF×version targets matched", file=sys.stderr)
        return 2

    overall_violations = 0
    for dhf, ver in targets:
        try:
            payload, mirror_dir = _audit_one(cfg, drift_rules, jira_client, dtm_reader, htm_reader, dhf, ver)
        except FileNotFoundError as e:
            print(f"[jira-pull audit] skip {dhf.leaf}/{ver}: {e}", file=sys.stderr)
            continue
        n = payload["summary"]["violations_total"]
        overall_violations += n
        if args.dry_run:
            print(json.dumps(payload, indent=2))
            print(f"# {dhf.leaf}/{ver} → {n} violations (dry-run, not written)", file=sys.stderr)
        else:
            json_path, md_path = _write_outputs(mirror_dir, payload)
            print(f"[jira-pull audit] {dhf.leaf}/{ver} → {n} violations → {json_path.relative_to(cfg.project_root)}", file=sys.stderr)

    return 0 if overall_violations == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
