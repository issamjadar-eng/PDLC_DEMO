"""
/jira-pull refresh — pulls Epics / Stories / Hazards / Test Executions per
project.yml dhfs[].jira and writes JSON+MD to docs/project/_jira/<arch>/<ver>/.

Two-phase orchestration so the Atlassian MCP call (which only runs inside
Claude Code's tool loop) stays out of this script:

  Phase 1 — `--plan`
    The script prints a JSON document describing one or more pull targets:
    `{ "targets": [{dhf, arch_slug, version, layer, issuetype, jql, fields,
                   output_json, output_md, pagination, ...}, ...] }`
    Each target's JQL **always ends with `ORDER BY key ASC`** so the Jira
    issue key becomes a deterministic monotonic cursor — required because
    the wrapped Atlassian MCP search caps at 100 issues/page and does NOT
    expose `nextPageToken` in its response envelope. The `pagination` block
    on each target documents the cursor protocol.

    Claude then calls `mcp__atlassian__searchJiraIssuesUsingJql` for each
    target with the supplied `cloudId`, `jql`, and `fields`. If the response
    contains `maxResults` issues (the cap), it issues a follow-up call with
    `key > "<last-key-of-previous-page>"` appended — `lib.normalize.build_jql`
    accepts a `cursor_after_key` parameter for this. Each page is saved as
    a separate raw file (e.g. `/tmp/refresh_<dhf>_<layer>_p1.json`,
    `_p2.json`, ...).

  Phase 2 — `--merge --layer X --input <path1> [--input <path2> ...]`
    The script reads every raw response, concatenates the issue lists,
    runs each issue through `lib.normalize.normalize_issue`, writes the
    layer's `<L>.json` and `<L>.md` atomically, and bumps the version-level
    `_meta.json`. Multiple `--input` flags merge multi-page pulls.

Usage:
  python -m actions.refresh --plan --dhf <leaf> --version <id> [--layer L]
  python -m actions.refresh --plan --all
  python -m actions.refresh --merge --dhf <leaf> --version <id> --layer <L> --input <path> [--input <path>...]

Pull-only — never writes to Jira. Atomic writes — partial pulls don't leave
the mirror in a half-written state.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Allow running both as `python -m actions.refresh` (when CWD is the skill
# root) and `python3 .claude/skills/jira-pull/actions/refresh.py ...` (the
# common invocation pattern from the project root).
_SKILL_ROOT = Path(__file__).resolve().parent.parent
if str(_SKILL_ROOT) not in sys.path:
    sys.path.insert(0, str(_SKILL_ROOT))

from lib import config as cfgmod  # noqa: E402
from lib import normalize as norm  # noqa: E402


# ─── Plan mode ───────────────────────────────────────────────────────────


def _resolve_extractors(dhf: cfgmod.DhfConfig, version_id: str) -> Dict[str, str]:
    """Pull the prefix-extractor regex map for the version's DTM (used for
    markdown rendering — DI-NNNN, PHA-N, etc.). Falls back to the first DTM
    schema for the DHF when no exact-version match exists."""
    schema = cfgmod.find_dtm_schema(dhf, version_id)
    if schema is None and dhf.dtm_schemas:
        schema = dhf.dtm_schemas[0]
    return dict(schema.extractors) if schema else {}


def _layer_paths(
    cfg: cfgmod.ResolvedConfig, dhf: cfgmod.DhfConfig, version_id: str, layer: str
) -> Dict[str, str]:
    base = (
        cfg.project_root
        / cfg.site.mirror_root.lstrip("/")
        / dhf.arch_slug
        / version_id
    )
    stem = norm.LAYER_FILES[layer]
    return {
        "dir": str(base),
        "json": str(base / f"{stem}.json"),
        "md": str(base / f"{stem}.md"),
    }


def build_targets(
    cfg: cfgmod.ResolvedConfig,
    dhf: cfgmod.DhfConfig,
    version: cfgmod.JiraVersion,
    layers: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """Build pull targets for one DHF×version. Returns one dict per layer."""
    if not dhf.jira:
        return []
    layers = layers or list(norm.LAYER_FILES.keys())
    out: List[Dict[str, Any]] = []
    for layer in layers:
        if layer not in norm.LAYER_FILES:
            raise ValueError(f"unknown layer {layer!r}; valid: {list(norm.LAYER_FILES)}")
        story_filter = (
            {"labels": dhf.jira.story_filter.labels, "statuses": dhf.jira.story_filter.statuses}
            if layer == "stories"
            else None
        )
        jql = norm.build_jql(
            dhf.jira.project_key,
            version.fix_version,
            layer,
            story_filter=story_filter,
        )
        paths = _layer_paths(cfg, dhf, version.id, layer)
        out.append(
            {
                "dhf": dhf.leaf,
                "arch_slug": dhf.arch_slug,
                "arch_name": dhf.architecture_name,
                "marketed_name": dhf.marketed_name,
                "version": version.id,
                "fix_version": version.fix_version,
                "fix_version_id": version.fix_version_id,
                "layer": layer,
                "issuetype": norm.LAYER_DEFAULTS[layer]["issuetype"],
                "jql": jql,
                "fields": list(cfg.site.field_set_common),
                "cloud_id": cfg.site.cloud_id,
                "base_url": cfg.site.base_url,
                "output_dir": paths["dir"],
                "output_json": paths["json"],
                "output_md": paths["md"],
                "pagination": {
                    "page_size": 100,
                    "cursor_field": "key",
                    "ordering": "ASC",
                    "protocol": (
                        "JQL ends with `ORDER BY key ASC`. If a page returns "
                        "exactly page_size issues (likely capped), call MCP "
                        "again with the SAME JQL but rebuilt by "
                        "`build_jql(..., cursor_after_key=<last key on previous page>)` "
                        "until a page returns fewer than page_size. Save each "
                        "page's raw response separately and pass all of them to "
                        "`--merge` via repeated `--input` flags."
                    ),
                },
            }
        )
    return out


def cmd_plan(args: argparse.Namespace) -> int:
    cfg = cfgmod.load(Path.cwd())
    targets: List[Dict[str, Any]] = []
    if args.all:
        for dhf in cfg.dhfs:
            if not dhf.jira:
                continue
            for v in dhf.jira.versions:
                targets.extend(build_targets(cfg, dhf, v, args.layer and [args.layer]))
    else:
        if not (args.dhf and args.version):
            print("--plan requires --dhf and --version (or --all)", file=sys.stderr)
            return 2
        dhf = cfgmod.find_dhf(cfg, args.dhf)
        version = cfgmod.find_version(dhf, args.version)
        targets = build_targets(cfg, dhf, version, args.layer and [args.layer])
    json.dump({"targets": targets}, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


# ─── Merge mode ──────────────────────────────────────────────────────────


def _atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(content, encoding="utf-8")
    os.replace(tmp, path)


def _read_raw_response(input_path: Path) -> List[Dict[str, Any]]:
    """Accept either MCP envelope `{issues: [...]}` (single page or merged
    multi-page), the wrapped MCP envelope `{issues: {nodes: [...]}}` emitted
    by the Atlassian MCP wrapper, or a bare list of issues. Tolerate top-level
    paginated structure with `pages: [{issues: [...]}, ...]`."""
    raw = json.loads(input_path.read_text())
    if isinstance(raw, list):
        return raw
    if not isinstance(raw, dict):
        raise ValueError(f"{input_path}: expected JSON object or array; got {type(raw)}")
    issues = raw.get("issues")
    if isinstance(issues, list):
        return issues
    if isinstance(issues, dict) and isinstance(issues.get("nodes"), list):
        return issues["nodes"]
    if isinstance(raw.get("pages"), list):
        out: List[Dict[str, Any]] = []
        for p in raw["pages"]:
            pissues = (p or {}).get("issues") or []
            if isinstance(pissues, dict) and isinstance(pissues.get("nodes"), list):
                out.extend(pissues["nodes"])
            elif isinstance(pissues, list):
                out.extend(pissues)
        return out
    raise ValueError(
        f"{input_path}: no `issues[]`, `issues.nodes[]`, or `pages[].issues[]` found; can't extract"
    )


def merge_pages(pages: List[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    """Concatenate raw issue lists from one or more MCP/REST pages and
    dedupe on Jira `key`, preserving first-seen order.

    Pure — no I/O, no MCP. This is the seam the mocked-tier tests exercise:
    multi-page pulls can overlap on the key cursor boundary (the follow-up
    query is `key > "<last>"`, but a page saved twice or a retried page
    re-delivers the same issues), so the merge must be idempotent on key.
    Issues without a `key` are kept verbatim (never deduped)."""
    seen_keys: set[str] = set()
    deduped: List[Dict[str, Any]] = []
    for page in pages:
        for r in page:
            # Tolerate both raw envelope shape and pre-flattened shape.
            k = r.get("key") or ""
            if k and k in seen_keys:
                continue
            if k:
                seen_keys.add(k)
            deduped.append(r)
    return deduped


def cmd_merge(args: argparse.Namespace) -> int:
    cfg = cfgmod.load(Path.cwd())
    dhf = cfgmod.find_dhf(cfg, args.dhf)
    version = cfgmod.find_version(dhf, args.version)
    layer = args.layer
    if layer not in norm.LAYER_FILES:
        print(f"unknown layer {layer!r}; valid: {list(norm.LAYER_FILES)}", file=sys.stderr)
        return 2

    inputs: List[Path] = [Path(p) for p in (args.input or [])]
    if not inputs:
        print("--merge requires at least one --input", file=sys.stderr)
        return 2
    # Dedupe on Jira key — multi-page pulls can overlap on the cursor boundary.
    deduped = merge_pages([_read_raw_response(p) for p in inputs])
    flat_issues = [norm.normalize_issue(r) for r in deduped]

    target = build_targets(cfg, dhf, version, [layer])[0]
    enriched_fields = [
        f for f in ("description", "assignee", "reporter", "resolution", "duedate")
        if f in cfg.site.field_set_common
    ]
    meta = norm.build_meta(
        cloud_id=cfg.site.cloud_id,
        fix_version=version.fix_version,
        fix_version_id=version.fix_version_id,
        issuetype=norm.LAYER_DEFAULTS[layer]["issuetype"],
        jql=target["jql"],
        issue_count=len(flat_issues),
        field_set=cfg.site.field_set_common,
        enriched_with=enriched_fields,
    )

    payload = {"_meta": meta, "issues": sorted(flat_issues, key=lambda x: x["key"])}
    json_path = Path(target["output_json"])
    md_path = Path(target["output_md"])

    _atomic_write(
        json_path,
        json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
    )

    extractors = _resolve_extractors(dhf, version.id)
    md = norm.render_layer_md(
        layer,
        flat_issues,
        fix_version=version.fix_version,
        fix_version_id=version.fix_version_id,
        pulled_at=meta["pulled_at"],
        base_url=cfg.site.base_url,
        extractors=extractors,
        arch_marketed_name=dhf.marketed_name,
    )
    _atomic_write(md_path, md)

    # Update version-level _meta.json — keep a per-layer pulled_at log.
    version_meta_path = json_path.parent / "_meta.json"
    if version_meta_path.exists():
        try:
            vmeta = json.loads(version_meta_path.read_text())
        except Exception:
            vmeta = {}
    else:
        vmeta = {}
    vmeta.setdefault("layers", {})[layer] = {
        "pulled_at": meta["pulled_at"],
        "issue_count": meta["issue_count"],
        "schema_version": meta["schema_version"],
        "enriched_with": meta["enriched_with"],
    }
    vmeta["fix_version"] = version.fix_version
    vmeta["fix_version_id"] = version.fix_version_id
    vmeta["arch_slug"] = dhf.arch_slug
    _atomic_write(
        version_meta_path,
        json.dumps(vmeta, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
    )

    print(
        f"[refresh] {args.dhf}/{version.id}/{layer}: wrote {len(flat_issues)} issues "
        f"to {json_path.relative_to(cfg.project_root)} and {md_path.relative_to(cfg.project_root)}",
        file=sys.stderr,
    )
    return 0


# ─── CLI ─────────────────────────────────────────────────────────────────


def main(argv: List[str]) -> int:
    parser = argparse.ArgumentParser(prog="jira-pull refresh")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--plan", action="store_true", help="Emit JSON pull-target list for Claude+MCP")
    mode.add_argument("--merge", action="store_true", help="Read a saved MCP response, normalize, write the mirror")

    parser.add_argument("--all", action="store_true", help="Plan: walk every DHF×version")
    parser.add_argument("--dhf", help="DHF leaf (project.yml dhfs[].leaf)")
    parser.add_argument("--version", help="Version id (e.g. v1.0.0)")
    parser.add_argument("--layer", help="One of epics|stories|hazards|tests")
    parser.add_argument("--input", action="append", help="(merge) path to raw MCP response JSON; repeat for multi-page pulls")
    args = parser.parse_args(argv)

    if args.plan:
        return cmd_plan(args)
    if args.merge:
        if not (args.dhf and args.version and args.layer and args.input):
            parser.error("--merge requires --dhf, --version, --layer, and at least one --input")
        return cmd_merge(args)
    return 1  # unreachable


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
