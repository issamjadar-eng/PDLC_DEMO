"""Environment-check bridge — surfaces the project's `setup.sh` in the console.

A project following the medtech-docs conventions ships a root-level
`setup.sh` (dev-environment bootstrapper) with a read-only `--check` mode
and a `setup.md` guide. This module is the console's adapter to that
convention, and it deliberately does only two things:

- **run the script's own `--check` mode** on demand (never the full
  install — that mutates the machine and belongs in the user's terminal),
  parse its `[OK]/[WARN]/[ERROR]` output into a structured report, and
  cache it at `.state/setup-check.json`;
- **read state**: the cached report, the `.state/setup-last-run.txt`
  stamp a full run leaves behind (when the project's script writes one),
  and whether `setup.sh` changed after the last check (staleness).

Everything degrades cleanly when the project has no `setup.sh` — the
loader reports `available: false` and the UI hides the section.
"""
from __future__ import annotations

import datetime as _dt
import json
import re
import subprocess
from pathlib import Path

SETUP_SH_REL = "setup.sh"
SETUP_MD_CANDIDATES = ("setup.md", "SETUP.md")
CHECK_CACHE_REL = ".state/setup-check.json"
FULL_RUN_STAMP_REL = ".state/setup-last-run.txt"
CHECK_TIMEOUT_S = 300

_ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")
_STEP_RE = re.compile(r"^──\s*(.+?)\s*──$")
_LEVEL_RE = re.compile(r"^\[(INFO|OK|WARN|ERROR)\]\s*(.*)$")


def _now_iso() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_check_output(text: str) -> dict:
    """Parse `setup.sh --check` output into {sections: [...], counts: {...}}.

    Pure function. Strips ANSI colors; groups `[LEVEL]` lines under the
    `── Step ──` heading they follow; anything before the first step goes
    into a 'General' section. Unrecognized lines are ignored (progress
    noise, blank lines, third-party tool output).

    The script's `── Summary ──` step is its terminal-facing recap — it
    re-lists the same tools the per-step sections already reported. In a
    grouped report that's pure duplication and it double-counts every
    recapped probe, so the section is dropped entirely (its lines don't
    reach `counts` either)."""
    sections: list[dict] = []
    current: dict | None = None
    skipping = False
    counts = {"ok": 0, "warn": 0, "error": 0, "info": 0}
    for raw in text.splitlines():
        line = _ANSI_RE.sub("", raw).strip()
        if not line:
            continue
        m = _STEP_RE.match(line)
        if m:
            skipping = m.group(1).strip().lower() == "summary"
            if skipping:
                current = None
                continue
            current = {"title": m.group(1), "lines": []}
            sections.append(current)
            continue
        if skipping:
            continue
        m = _LEVEL_RE.match(line)
        if not m:
            continue
        level = m.group(1).lower()
        counts[level] = counts.get(level, 0) + 1
        if current is None:
            current = {"title": "General", "lines": []}
            sections.append(current)
        current["lines"].append({"level": level, "text": m.group(2)})
    return {"sections": sections, "counts": counts}


def run_check(repo_root: Path) -> dict:
    """Run `bash setup.sh --check` (the script's own read-only mode), parse,
    cache, and return the report. Raises RuntimeError on missing script;
    a non-zero exit is NOT an error — it's part of the report."""
    script = repo_root / SETUP_SH_REL
    if not script.is_file():
        raise RuntimeError("setup.sh not found at the project root.")
    started = _dt.datetime.now()
    try:
        r = subprocess.run(
            ["bash", str(script), "--check"],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            timeout=CHECK_TIMEOUT_S,
        )
        output = (r.stdout or "") + (r.stderr or "")
        exit_code = r.returncode
    except subprocess.TimeoutExpired as e:
        output = ((e.stdout or b"").decode(errors="replace")
                  if isinstance(e.stdout, bytes) else (e.stdout or ""))
        output += f"\n[ERROR] check timed out after {CHECK_TIMEOUT_S}s"
        exit_code = -1
    report = parse_check_output(output)
    report.update({
        "ran_at": _now_iso(),
        "exit_code": exit_code,
        "duration_s": round((_dt.datetime.now() - started).total_seconds(), 1),
        "setup_sh_mtime": script.stat().st_mtime,
    })
    cache = repo_root / CHECK_CACHE_REL
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def load_environment(repo_root: Path) -> dict:
    """Read-only state for the Environment section. Never runs the script."""
    script = repo_root / SETUP_SH_REL
    if not script.is_file():
        return {"available": False}

    guide = next(
        (c for c in SETUP_MD_CANDIDATES if (repo_root / c).is_file()), ""
    )

    last_check: dict | None = None
    cache = repo_root / CHECK_CACHE_REL
    if cache.is_file():
        try:
            data = json.loads(cache.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                last_check = data
        except Exception:
            last_check = None

    stamp = ""
    stamp_path = repo_root / FULL_RUN_STAMP_REL
    if stamp_path.is_file():
        try:
            stamp = stamp_path.read_text(encoding="utf-8").strip()
        except OSError:
            stamp = ""

    # Stale when setup.sh changed after the cached check ran.
    mtime = script.stat().st_mtime
    stale = bool(last_check) and mtime > float(last_check.get("setup_sh_mtime") or 0)

    return {
        "available": True,
        "script": SETUP_SH_REL,
        "guide": guide,
        "script_modified": _dt.datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M"),
        "last_full_run": stamp,
        "last_check": last_check,
        "stale": stale,
    }
