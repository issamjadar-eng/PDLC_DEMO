"""
/jira-pull build-trace — emit unified-trace.md walking UN→DI→SW→V&V→Risk
with `Unknown — <category>` placeholders for unresolved trace edges, and
inline drift badges when a sibling drift.json is present.

Usage:
  python -m actions.build_trace --dhf <leaf> --version <id>
  python -m actions.build_trace --all
  python -m actions.build_trace --all --dry-run

Reads:
  - <mirror_root>/<arch>/<ver>/{epics,stories,hazards,tests}.json
  - dhfs[].evidence.design_traceability_matrix[] (DTM xlsx + schema map)
  - dhfs[].evidence.hazard_traceability_matrix (optional HTM)
  - <mirror_root>/<arch>/<ver>/drift.json (optional — inline badges per row)

Writes (per DHF×version):
  - <mirror_root>/<arch>/<ver>/unified-trace.md
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
import types
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# ─── Synthetic-package loader (mirrors actions/audit.py) ─────────────────────


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


# ─── Severity ordering for drift badges ──────────────────────────────────────

_SEV_RANK = {"error": 3, "warning": 2, "info": 1}
_SEV_BADGE = {"error": "✗", "warning": "⚠", "info": "ℹ"}


def _worst_severity(severities: List[str]) -> Optional[str]:
    if not severities:
        return None
    return max(severities, key=lambda s: _SEV_RANK.get(s, 0))


def _badge(sev: Optional[str]) -> str:
    if not sev:
        return "✓"
    return _SEV_BADGE.get(sev, "?")


def _normalize_id(raw: str) -> str:
    return re.sub(r"[\s-]+", "", raw.strip())


def _digit_value(canonical: Optional[str]) -> Optional[str]:
    if not canonical:
        return None
    m = re.search(r"(\d+)$", canonical)
    if not m:
        return None
    return m.group(1).lstrip("0") or "0"


def _is_blank(text: Optional[str], tbd: str) -> bool:
    if text is None:
        return True
    s = str(text).strip()
    return s == "" or s == tbd


def _browse_url(base_url: str, key: str) -> str:
    base = base_url.rstrip("/")
    return f"{base}/browse/{key}"


def _link(label: str, url: str) -> str:
    return f"[{label}]({url})"


def _load_drift(mirror_dir: Path) -> Dict[str, List[dict]]:
    """Load drift.json (when present) and group violations by `item_id`."""
    drift_path = mirror_dir / "drift.json"
    if not drift_path.exists():
        return {}
    payload = json.loads(drift_path.read_text())
    by_item: Dict[str, List[dict]] = defaultdict(list)
    for v in payload.get("violations") or []:
        by_item[v["item_id"]].append(v)
    return by_item


def _row_badge(drift_by_item: Dict[str, List[dict]], *keys: str) -> str:
    """Pick the worst severity across all drift entries keyed by any of `keys`,
    return the corresponding badge."""
    sevs: List[str] = []
    for k in keys:
        if not k:
            continue
        for v in drift_by_item.get(k, []):
            sevs.append(v["severity"])
    return _badge(_worst_severity(sevs))


# ─── Trace builder ───────────────────────────────────────────────────────────


def _build_one(cfg, drift_rules, jira_client, dtm_reader, htm_reader, dhf, version_id):
    """Walk one (DHF, version) pair → markdown string + (mirror_dir, payload_meta)."""
    config_mod = sys.modules["lib.config"]
    schema = config_mod.find_dtm_schema(dhf, version_id)
    if schema is None:
        raise KeyError(f"DHF {dhf.leaf!r} has no DTM schema for version {version_id!r}")

    htm_schema = config_mod.find_htm_schema(dhf, version_id)

    j = jira_client.load_state(cfg, dhf, version_id)
    idx = jira_client.build_index(j)
    dtm_state = dtm_reader.read(schema, cfg.project_root)
    htm_state = None
    if htm_schema is not None:
        try:
            htm_state = htm_reader.read(htm_schema, cfg.project_root)
        except (FileNotFoundError, KeyError):
            htm_state = None

    mirror_dir = jira_client.mirror_dir(cfg, dhf, version_id)
    drift_by_item = _load_drift(mirror_dir)

    base_url = cfg.site.base_url or ""
    di_pattern = re.compile(schema.extractors.get("design_input_id") or r"\b(DI-\d+)\b")
    haz_pattern_str = schema.extractors.get("hazard_id")
    haz_pattern = re.compile(haz_pattern_str) if haz_pattern_str else None
    tbd = schema.tbd_value

    # ── Build DI universe: DTM rows by digit, Jira DI Epics by digit ─────────
    dtm_rows_by_digit: Dict[str, List] = defaultdict(list)
    for canonical_di, rows in dtm_state.by_design_input.items():
        digit = _digit_value(canonical_di)
        if digit is not None:
            dtm_rows_by_digit[digit].extend(rows)

    jira_di_by_digit: Dict[str, dict] = {}
    for ep in j.epics:
        m = di_pattern.search(ep.get("summary") or "")
        if not m:
            continue
        canonical = _normalize_id(m.group(1) if m.lastindex else m.group(0))
        digit = _digit_value(canonical)
        if digit is not None and digit not in jira_di_by_digit:
            jira_di_by_digit[digit] = ep

    all_digits = sorted(set(dtm_rows_by_digit.keys()) | set(jira_di_by_digit.keys()),
                        key=lambda d: int(d) if d.isdigit() else 0)

    # ── Hazard lookup: PHA canonical → Jira hazard issue ─────────────────────
    jira_hazard_by_canonical: Dict[str, dict] = {}
    if haz_pattern is not None:
        for hz in j.hazards:
            m = haz_pattern.search(hz.get("summary") or "")
            if not m:
                continue
            canon = _normalize_id(m.group(1) if m.lastindex else m.group(0))
            jira_hazard_by_canonical.setdefault(canon, hz)

    # ── Render markdown ──────────────────────────────────────────────────────
    lines: List[str] = []
    lines.append(f"# Unified Trace — {dhf.architecture_name} / {version_id}")
    lines.append("")
    lines.append(f"- **DHF leaf**: `{dhf.leaf}`")
    lines.append(f"- **Marketed name**: {dhf.marketed_name}")
    lines.append(f"- **Fix version**: {j.fix_version or '_(unknown)_'}")
    lines.append(f"- **DTM source**: `{Path(dtm_state.source_path).name}`")
    if htm_state is not None:
        lines.append(f"- **HTM source**: `{Path(htm_state.source_path).name}`")
    else:
        lines.append("- **HTM source**: _(none declared in project.yml — hazard rows fall back to DTM `hazard_refs`)_")
    drift_total = sum(len(v) for v in drift_by_item.values())
    if drift_total:
        sev_counts: Dict[str, int] = {"error": 0, "warning": 0, "info": 0}
        for vs in drift_by_item.values():
            for v in vs:
                sev_counts[v["severity"]] = sev_counts.get(v["severity"], 0) + 1
        lines.append(f"- **Drift overlay**: {drift_total} violations "
                     f"(error={sev_counts['error']}, warning={sev_counts['warning']}, info={sev_counts['info']}) "
                     f"— see `drift.md` for details.")
    else:
        lines.append("- **Drift overlay**: _(no drift.json present — run `/jira-pull audit` to generate)_")
    lines.append("")
    lines.append("Legend: `✓` clean • `ℹ` info-level drift • `⚠` warning-level drift • `✗` error-level drift")
    lines.append("")

    # ── Per-DI section ───────────────────────────────────────────────────────
    lines.append(f"## Design Inputs ({len(all_digits)})")
    lines.append("")

    untraced_un_count = 0
    for digit in all_digits:
        ep = jira_di_by_digit.get(digit)
        rows = dtm_rows_by_digit.get(digit, [])

        # DI heading
        if ep:
            jira_canonical = next(
                (_normalize_id(m.group(1) if m.lastindex else m.group(0))
                 for m in [di_pattern.search(ep.get("summary") or "")] if m), f"DI?{digit}")
            ep_badge = _row_badge(drift_by_item, ep["key"])
            di_label = f"{jira_canonical} — {ep['key']}"
            di_link = _link(di_label, _browse_url(base_url, ep["key"]))
            lines.append(f"### {ep_badge} {di_link}")
            summary_text = (ep.get("summary") or "").strip()
            if summary_text:
                lines.append(f"- **Jira summary**: {summary_text}")
        else:
            row0 = rows[0] if rows else None
            dtm_canonical = (row0.cells.get("design_input") if row0 else None) or f"digit {digit}"
            lines.append(f"### ⚠ Unknown — DI (DTM cites `{dtm_canonical}` but no Jira Epic)")

        # User Need(s) from DTM
        un_seen = []
        if rows:
            un_label = "user_need" if "user_need" in dtm_state.schema.columns else None
            for row in rows:
                un_text = row.cells.get(un_label) if un_label else None
                if not _is_blank(un_text, tbd):
                    un_seen.append(un_text.strip())
        if un_seen:
            uns = ", ".join(sorted(set(un_seen)))
            lines.append(f"- **User Need (DTM)**: {uns}")
        else:
            untraced_un_count += 1
            lines.append("- **User Need (DTM)**: _Unknown — UN external_ "
                         "(External Protocol UN source not yet identified)")

        # SW children (Stories whose parent.key == ep.key)
        if ep:
            children = idx.stories_by_parent.get(ep["key"], [])
            if children:
                lines.append(f"- **Software (Jira Stories, {len(children)})**:")
                for st in children:
                    st_badge = _row_badge(drift_by_item, st["key"])
                    st_label = f"{st['key']}"
                    st_link = _link(st_label, _browse_url(base_url, st["key"]))
                    summary_short = (st.get("summary") or "")[:100]
                    lines.append(f"    - {st_badge} {st_link} — {summary_short}")
            else:
                lines.append("- **Software (Jira Stories)**: _Unknown — SW (no child Story)_")
        else:
            lines.append("- **Software (Jira Stories)**: _Unknown — SW (no Jira DI Epic)_")

        # V&V (Test Executions linked via inverse '1 Relates' to each child Story)
        vv_count = 0
        vv_lines: List[str] = []
        if ep:
            for st in idx.stories_by_parent.get(ep["key"], []):
                tests = idx.tests_for_story_key(st["key"])
                for tx in tests:
                    tx_badge = _row_badge(drift_by_item, tx["key"])
                    tx_link = _link(tx["key"], _browse_url(base_url, tx["key"]))
                    summary_short = (tx.get("summary") or "")[:100]
                    vv_lines.append(f"    - {tx_badge} {tx_link} (verifies {st['key']}) — {summary_short}")
                    vv_count += 1
        if vv_lines:
            lines.append(f"- **V&V (Test Executions, {vv_count})**:")
            lines.extend(vv_lines)
        else:
            # Distinguish "DTM verification populated but no Jira test" from "all unknown"
            v_text_present = False
            if rows and "verification" in dtm_state.schema.columns:
                v_text_present = any(not _is_blank(r.cells.get("verification"), tbd) for r in rows)
            if v_text_present:
                lines.append("- **V&V (Test Executions)**: _Unknown — V&V (DTM cites verification but no Jira Test)_")
            else:
                lines.append("- **V&V (Test Executions)**: _Unknown — V&V_")

        # Risk (PHA refs from DTM hazard_refs column → Jira Hazards)
        risk_lines: List[str] = []
        if rows and haz_pattern is not None and "hazard_refs" in dtm_state.schema.columns:
            seen_pha: set = set()
            for row in rows:
                cell = row.cells.get("hazard_refs") or ""
                for m in haz_pattern.finditer(cell):
                    raw = m.group(1) if m.lastindex else m.group(0)
                    canon = _normalize_id(raw)
                    if canon in seen_pha:
                        continue
                    seen_pha.add(canon)
                    hz = jira_hazard_by_canonical.get(canon)
                    if hz:
                        hz_badge = _row_badge(drift_by_item, hz["key"], canon)
                        hz_link = _link(f"{canon} — {hz['key']}", _browse_url(base_url, hz["key"]))
                        risk_lines.append(f"    - {hz_badge} {hz_link}")
                    else:
                        risk_lines.append(f"    - ⚠ {canon} — _Unknown — Hazard (DTM cites PHA but no Jira Hazard)_")
        # HTM-driven supplement
        if htm_state is not None and ep:
            jira_canonical_for_di = next(
                (_normalize_id(m.group(1) if m.lastindex else m.group(0))
                 for m in [di_pattern.search(ep.get("summary") or "")] if m), None)
            if jira_canonical_for_di:
                htm_rows = htm_state.by_design_input.get(jira_canonical_for_di, [])
                for hr in htm_rows:
                    pha = (hr.extracted.get("hazard_id") if hr.extracted else None)
                    if not pha:
                        continue
                    hz = jira_hazard_by_canonical.get(pha)
                    if hz:
                        hz_badge = _row_badge(drift_by_item, hz["key"], pha)
                        hz_link = _link(f"{pha} — {hz['key']}", _browse_url(base_url, hz["key"]))
                        line = f"    - {hz_badge} {hz_link} _(via HTM row {hr.row_index})_"
                    else:
                        line = f"    - ⚠ {pha} _(HTM row {hr.row_index}; no Jira Hazard)_"
                    if line not in risk_lines:
                        risk_lines.append(line)
        if risk_lines:
            lines.append(f"- **Risk (Hazards, {len(risk_lines)})**:")
            lines.extend(risk_lines)
        else:
            lines.append("- **Risk (Hazards)**: _Unknown — Hazard (no DTM hazard_refs / HTM linkage)_")

        # Per-DI drift detail (if any)
        di_drift = []
        if ep:
            di_drift.extend(drift_by_item.get(ep["key"], []))
        if rows:
            for row in rows:
                row_key = f"row{row.row_index}"
                for v in drift_by_item.values() if False else []:
                    pass
        # Just surface the DI Epic drift lines (other rules have their own item_ids)
        if di_drift:
            lines.append("- **Drift on this DI**:")
            for v in di_drift:
                badge = _badge(v["severity"])
                lines.append(f"    - {badge} `{v['rule']}` — {v['message']}")
        lines.append("")

    # ── Orphan sections: items only in Jira (non-DI Epics, untraced tests) ────
    non_di_epics = [ep for ep in j.epics
                    if ep["key"] not in {e["key"] for e in jira_di_by_digit.values() if e}]
    if non_di_epics:
        lines.append(f"## Other Jira Epics (not Design Inputs) — {len(non_di_epics)}")
        lines.append("")
        for ep in non_di_epics[:50]:  # cap noise; full list lives in epics.md
            badge = _row_badge(drift_by_item, ep["key"])
            link = _link(ep["key"], _browse_url(base_url, ep["key"]))
            lines.append(f"- {badge} {link} — {(ep.get('summary') or '')[:120]}")
        if len(non_di_epics) > 50:
            lines.append(f"- _...and {len(non_di_epics) - 50} more (see `epics.md`)._")
        lines.append("")

    # Drift Summary appendix
    if drift_by_item:
        rule_counts: Dict[str, int] = defaultdict(int)
        for vs in drift_by_item.values():
            for v in vs:
                rule_counts[v["rule"]] += 1
        lines.append("## Drift Summary")
        lines.append("")
        for rule_id in sorted(rule_counts.keys()):
            lines.append(f"- `{rule_id}`: {rule_counts[rule_id]} violation(s)")
        lines.append("")
        lines.append(f"_See `drift.md` for full violation list and resolution hints._")
        lines.append("")

    lines.append(f"## Stats")
    lines.append("")
    lines.append(f"- Jira: {len(j.epics)} Epics, {len(j.stories)} Stories, "
                 f"{len(j.hazards)} Hazards, {len(j.test_executions)} Test Executions")
    lines.append(f"- DTM: {len(dtm_state.rows)} rows; "
                 f"{len(dtm_state.by_design_input)} distinct DIs; "
                 f"{len(dtm_state.by_user_need)} distinct UNs; "
                 f"{len(dtm_state.by_hazard)} distinct Hazards via `hazard_refs`")
    if htm_state is not None:
        lines.append(f"- HTM: {len(htm_state.rows)} rows")
    if untraced_un_count:
        lines.append(f"- Untraced UN cells: {untraced_un_count} (External Protocol source not yet identified)")
    lines.append("")

    md = "\n".join(lines)

    meta = {
        "dhf": dhf.leaf,
        "architecture_name": dhf.architecture_name,
        "version": version_id,
        "fix_version": j.fix_version,
        "stats": {
            "jira_epics": len(j.epics),
            "jira_stories": len(j.stories),
            "jira_hazards": len(j.hazards),
            "jira_tests": len(j.test_executions),
            "dtm_rows": len(dtm_state.rows),
            "drift_total": drift_total,
        },
    }
    return md, mirror_dir, meta


# ─── CLI ─────────────────────────────────────────────────────────────────────


def _iter_targets(cfg, dhf_leaf: Optional[str], version_id: Optional[str]) -> List[Tuple[Any, str]]:
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
    parser = argparse.ArgumentParser(prog="jira-pull build-trace")
    parser.add_argument("--dhf", help="DHF leaf (project.yml dhfs[].leaf). Omit with --all.")
    parser.add_argument("--version", help="Version id (e.g. v1.0.0). Omit with --all.")
    parser.add_argument("--all", action="store_true",
                        help="Build trace for every (DHF, version) pair with both Jira mirror and DTM schema.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print markdown to stdout without writing.")
    args = parser.parse_args(argv)

    if not args.all and not (args.dhf and args.version):
        parser.error("Provide --all OR both --dhf and --version")

    config_mod, drift_rules, jira_client, dtm_reader, htm_reader = _load_lib()
    cfg = config_mod.load()

    targets = _iter_targets(cfg, None if args.all else args.dhf,
                            None if args.all else args.version)
    if not targets:
        print("[jira-pull build-trace] no DHF×version targets matched", file=sys.stderr)
        return 2

    for dhf, ver in targets:
        try:
            md, mirror_dir, meta = _build_one(cfg, drift_rules, jira_client,
                                              dtm_reader, htm_reader, dhf, ver)
        except FileNotFoundError as e:
            print(f"[jira-pull build-trace] skip {dhf.leaf}/{ver}: {e}", file=sys.stderr)
            continue
        if args.dry_run:
            print(md)
            print(f"# {dhf.leaf}/{ver}: {meta['stats']} (dry-run, not written)", file=sys.stderr)
        else:
            mirror_dir.mkdir(parents=True, exist_ok=True)
            out_path = mirror_dir / "unified-trace.md"
            out_path.write_text(md)
            rel = out_path.relative_to(cfg.project_root) if str(out_path).startswith(str(cfg.project_root)) else out_path
            print(f"[jira-pull build-trace] {dhf.leaf}/{ver} → {rel} "
                  f"({meta['stats']['jira_epics']}E / {meta['stats']['dtm_rows']} DTM rows / "
                  f"{meta['stats']['drift_total']} drift)", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
