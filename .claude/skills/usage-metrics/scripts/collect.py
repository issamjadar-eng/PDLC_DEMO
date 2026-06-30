#!/usr/bin/env python3
"""usage-metrics · collect — parse local Claude Code session transcripts into
per-session token-usage records under the current user's task folder.

Pure script, NO LLM in the data path. Owned by the `usage-metrics` skill.

Design (see project.yml `usage_metrics`):
  - git-as-aggregator: each teammate collects LOCALLY into their own task
    folder; git/GitHub is the aggregation transport; a separate aggregate
    script rolls up across folders.
  - Identity = the task folder (the folder IS the person). NO email/PII is
    written into the committed records. session.id is a UUID, not PII.
  - One file PER SESSION → structurally collision-free across concurrent
    sessions and across machines (distinct session.id → distinct filename).
  - Idempotent: each run fully re-derives a session's totals from its
    transcript and overwrites the file (atomic temp+rename). Safe to re-run.

Source mechanism = `transcript`: Claude Code writes one JSONL transcript per
session under ~/.claude/projects/<project-slug>/<session_id>.jsonl. Each
assistant message carries `.message.usage.{input_tokens, output_tokens,
cache_creation_input_tokens, cache_read_input_tokens}` and `.message.model`.
Usage rows are logged ~2x, so we DEDUPE by `.message.id` before summing, and
bucket each message by its own `timestamp` month (a session crossing a month
boundary splits across month dirs).

Output: tasks/{task_folder}/_usage-metrics/YYYY-MM/<session_id>.json

Usage:
  collect.py [--dry-run] [--project-root PATH] [--quiet]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from collections import defaultdict
from pathlib import Path

sys.dont_write_bytecode = True   # keep __pycache__ out of the skill/shared trees


def find_project_root(start: Path) -> Path:
    """Walk up to the dir containing project.yml (the project root)."""
    p = start.resolve()
    for cand in (p, *p.parents):
        if (cand / "project.yml").is_file():
            return cand
    # Fallback: git toplevel
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, cwd=str(start), check=True,
        ).stdout.strip()
        if out:
            return Path(out)
    except Exception:
        pass
    raise SystemExit("collect: could not locate project root (no project.yml found)")


def read_usage_metrics_config(project_yml: Path) -> dict:
    """Minimal targeted reader for the `usage_metrics:` block (no PyYAML dep).

    Returns the few keys the collector needs: method, per_user_dir, layout.
    Mirrors resolve_user.py's no-dependency stance.
    """
    text = project_yml.read_text(encoding="utf-8")
    m = re.search(r"^usage_metrics:\s*$", text, re.MULTILINE)
    cfg = {"method": None, "per_user_dir": None, "layout": None}
    if not m:
        return cfg
    block = text[m.end():]
    # Stop at the next top-level key (column-0, non-comment).
    end = re.search(r"^\S", block, re.MULTILINE)
    if end:
        block = block[: end.start()]

    def grab(key: str):
        mm = re.search(rf"^\s+{re.escape(key)}:\s*([^\n#]+)", block, re.MULTILINE)
        return mm.group(1).strip() if mm else None

    cfg["method"] = grab("method")
    cfg["per_user_dir"] = grab("per_user_dir")
    cfg["layout"] = grab("layout")
    return cfg


def resolve_task_folder(project_root: Path) -> str:
    """Reuse the canonical roster resolver (.claude/skills/shared/scripts/resolve_user.py)."""
    resolver = project_root / ".claude" / "skills" / "shared" / "scripts" / "resolve_user.py"
    if not resolver.is_file():
        raise SystemExit(f"collect: resolver not found at {resolver}")
    out = subprocess.run(
        [sys.executable, str(resolver), "--task-folder"],
        capture_output=True, text=True, cwd=str(project_root), check=True,
    ).stdout.strip()
    if not out:
        raise SystemExit("collect: resolve_user.py returned no task_folder")
    return out


def transcript_dir(project_root: Path) -> Path:
    """Locate ~/.claude/projects/<slug> for this project.

    Primary: Claude Code encodes the project path by replacing every
    non-alphanumeric character (path separators '/', plus '_' and '.') with
    '-'. A '/'-only replacement misses projects whose folder name contains an
    underscore or dot (e.g. `PDLC_DEMO` → `-...-PDLC-DEMO`, not `...-PDLC_DEMO`).
    Fallback: scan ~/.claude/projects/* and match a transcript whose `cwd`
    equals the project root (robust to encoding quirks).
    """
    base = Path.home() / ".claude" / "projects"
    # Replicate Claude Code's slug: non-alphanumeric → '-'.
    slug = "".join(c if c.isalnum() else "-" for c in str(project_root))
    cand = base / slug
    if cand.is_dir():
        return cand
    # Secondary: legacy '/'-only encoding, for older transcript dirs.
    legacy = base / str(project_root).replace("/", "-")
    if legacy.is_dir():
        return legacy
    # Fallback: match by cwd recorded inside transcripts.
    if base.is_dir():
        target = str(project_root)
        for d in sorted(base.iterdir()):
            if not d.is_dir():
                continue
            for jf in d.glob("*.jsonl"):
                try:
                    with jf.open(encoding="utf-8") as fh:
                        for line in fh:
                            try:
                                row = json.loads(line)
                            except json.JSONDecodeError:
                                continue
                            if row.get("cwd") == target:
                                return d
                            break  # only need the first parseable row
                except OSError:
                    continue
                break
    raise SystemExit(
        f"collect: no transcript dir found for {project_root} under {base}"
    )


def _zero() -> dict:
    # cache_write_5m / cache_write_1h split out of cache_creation for accurate
    # cost (1h ephemeral cache is priced higher than 5m). cache_creation is kept
    # as the display total (== 5m + 1h).
    return {"input": 0, "output": 0, "cache_creation": 0, "cache_read": 0,
            "cache_write_5m": 0, "cache_write_1h": 0, "messages": 0}


def _add(bucket: dict, usage: dict) -> None:
    """Accumulate one message's usage into a stats bucket."""
    bucket["input"] += int(usage.get("input_tokens", 0) or 0)
    bucket["output"] += int(usage.get("output_tokens", 0) or 0)
    bucket["cache_read"] += int(usage.get("cache_read_input_tokens", 0) or 0)
    cc_total = int(usage.get("cache_creation_input_tokens", 0) or 0)
    nested = usage.get("cache_creation") or {}
    c5 = int(nested.get("ephemeral_5m_input_tokens", 0) or 0)
    c1 = int(nested.get("ephemeral_1h_input_tokens", 0) or 0)
    if not nested and cc_total:
        c5 = cc_total  # no split available → treat all as 5m
    bucket["cache_creation"] += (c5 + c1) if nested else cc_total
    bucket["cache_write_5m"] += c5
    bucket["cache_write_1h"] += c1
    bucket["messages"] += 1


def parse_session(jsonl_path: Path):
    """Return {month: {"by_model": {model: stats}, "by_day": {YYYY-MM-DD: stats}}}
    for one session transcript, deduped by message.id."""
    seen_msg_ids: set[str] = set()
    months: dict[str, dict] = defaultdict(lambda: {
        "by_model": defaultdict(_zero),
        "by_day": defaultdict(_zero),
    })
    with jsonl_path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            msg = row.get("message") or {}
            usage = msg.get("usage")
            if not usage:
                continue
            model = msg.get("model") or "unknown"
            # Claude Code emits locally-generated messages (interrupts, error
            # notices) under model "<synthetic>" with zero-token usage — not real
            # API usage; skip so they don't inflate message counts.
            if model == "<synthetic>":
                continue
            msg_id = msg.get("id")
            if not msg_id or msg_id in seen_msg_ids:
                continue
            seen_msg_ids.add(msg_id)
            ts = row.get("timestamp") or ""
            month = ts[:7] if len(ts) >= 7 else "unknown"
            day = ts[:10] if len(ts) >= 10 else "unknown"
            _add(months[month]["by_model"][model], usage)
            _add(months[month]["by_day"][day], usage)
    return months


def session_totals(model_map: dict) -> dict:
    totals = _zero()
    for stats in model_map.values():
        for k in totals:
            totals[k] += stats.get(k, 0)
    return totals


def atomic_write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2, sort_keys=True)
            fh.write("\n")
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def main() -> int:
    ap = argparse.ArgumentParser(description="Collect local Claude Code token usage per session.")
    ap.add_argument("--project-root", type=Path, default=None)
    ap.add_argument("--dry-run", action="store_true", help="compute + print, write nothing")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    project_root = find_project_root(args.project_root or Path.cwd())
    cfg = read_usage_metrics_config(project_root / "project.yml")

    method = cfg.get("method")
    if method == "admin_api":
        raise SystemExit(
            "collect: usage_metrics.method=admin_api is a reserved future seam — "
            "planned, not yet implemented. Set method: local to collect."
        )
    if method not in (None, "local"):
        raise SystemExit(f"collect: unsupported usage_metrics.method={method!r} (expected 'local').")

    task_folder = resolve_task_folder(project_root)
    per_user_tmpl = cfg.get("per_user_dir") or "tasks/{task_folder}/_usage-metrics"
    per_user_dir = project_root / per_user_tmpl.format(task_folder=task_folder)

    tdir = transcript_dir(project_root)
    transcripts = sorted(tdir.glob("*.jsonl"))
    if not transcripts:
        if not args.quiet:
            print(f"collect: no transcripts under {tdir}")
        return 0

    written = 0
    grand = {"input": 0, "output": 0, "cache_creation": 0, "cache_read": 0, "messages": 0}
    for jf in transcripts:
        session_id = jf.stem
        months = parse_session(jf)
        for month, mdata in months.items():
            model_map = mdata["by_model"]
            by_day = mdata["by_day"]
            totals = session_totals(model_map)
            if totals["messages"] == 0:
                continue
            for k in grand:
                grand[k] += totals[k]
            payload = {
                "session_id": session_id,
                "task_folder": task_folder,   # folder name, not PII — no email
                "month": month,
                "source": "transcript",
                "by_model": {m: dict(s) for m, s in model_map.items()},
                "by_day": {d: dict(s) for d, s in sorted(by_day.items())},
                "totals": totals,
            }
            out_path = per_user_dir / month / f"{session_id}.json"
            if args.dry_run:
                if not args.quiet:
                    print(f"[dry-run] {out_path.relative_to(project_root)}  "
                          f"in={totals['input']} out={totals['output']} "
                          f"cacheR={totals['cache_read']} cacheC={totals['cache_creation']}")
            else:
                atomic_write_json(out_path, payload)
            written += 1

    if not args.quiet:
        verb = "would write" if args.dry_run else "wrote"
        print(f"collect: {verb} {written} session-month file(s) for '{task_folder}' "
              f"→ {per_user_dir.relative_to(project_root)}")
        print(f"  totals: input={grand['input']:,} output={grand['output']:,} "
              f"cache_read={grand['cache_read']:,} cache_creation={grand['cache_creation']:,} "
              f"messages={grand['messages']:,}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
