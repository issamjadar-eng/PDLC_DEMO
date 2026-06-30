#!/usr/bin/env python3
"""usage-metrics · publish — push THIS user's _usage-metrics/ data to the shared
branch WITHOUT touching the working tree or current branch (temporary git
worktree based on origin/<branch>).

Why a worktree: the per-user raw data must reach the branch the daily-aggregate
GitHub workflow reads (it triggers on push to tasks/*/_usage-metrics/**). Doing
it via a worktree means a teammate mid-work on a feature branch never gets a
surprise commit/push of their WIP — only their own _usage-metrics/ folder is
published, in isolation. Concurrency-safe: on a non-fast-forward push it
re-syncs to the latest remote tip and retries once.

Best-effort: ANY failure is logged and swallowed (exit 0) — it must never
disrupt the user's repo or session. Pushing the data (no [skip ci]) triggers the
aggregate workflow → fresh team dashboard.

Run: publish.py [--dry-run] [--quiet] [--project-root PATH]
"""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True


def run(args, cwd, check=False):
    return subprocess.run(args, cwd=str(cwd), capture_output=True, text=True, check=check)


def find_project_root(start: Path) -> Path:
    for c in (start.resolve(), *start.resolve().parents):
        if (c / "project.yml").is_file():
            return c
    raise SystemExit("publish: no project.yml found")


def read_publish_cfg(pyml: Path) -> dict:
    cfg = {"enabled": False, "branch": "main"}
    text = pyml.read_text(encoding="utf-8")
    m = re.search(r"^usage_metrics:\s*$", text, re.MULTILINE)
    if not m:
        return cfg
    block = text[m.end():]
    end = re.search(r"^\S", block, re.MULTILINE)
    if end:
        block = block[: end.start()]
    pm = re.search(r"^\s+publish:\s*$", block, re.MULTILINE)
    if not pm:
        return cfg
    pblock = block[pm.end():]
    en = re.search(r"enabled:\s*(true|false)", pblock)
    br = re.search(r"branch:\s*([^\n#]+)", pblock)
    if en:
        cfg["enabled"] = en.group(1) == "true"
    if br:
        cfg["branch"] = br.group(1).strip()
    return cfg


def resolve_tf(root: Path) -> str:
    r = run([sys.executable, str(root / ".claude/skills/shared/scripts/resolve_user.py"),
             "--task-folder"], root)
    return r.stdout.strip()


def main() -> int:
    ap = argparse.ArgumentParser(description="Publish this user's _usage-metrics data to the shared branch.")
    ap.add_argument("--project-root", type=Path, default=None)
    ap.add_argument("--dry-run", action="store_true", help="do everything except the push")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    root = find_project_root(args.project_root or Path.cwd())
    cfg = read_publish_cfg(root / "project.yml")
    if not cfg["enabled"] and not args.dry_run:
        if not args.quiet:
            print("publish: disabled (set usage_metrics.publish.enabled: true to enable)")
        return 0

    tf = resolve_tf(root)
    if not tf:
        if not args.quiet:
            print("publish: could not resolve task_folder — skipping")
        return 0

    rel = f"tasks/{tf}/_usage-metrics"
    if not (root / rel).is_dir():
        if not args.quiet:
            print(f"publish: no data at {rel} — nothing to publish")
        return 0

    branch = cfg["branch"]
    run(["git", "fetch", "origin", branch], root)
    base = f"origin/{branch}"
    if run(["git", "rev-parse", "--verify", base], root).returncode != 0:
        base = branch  # no remote tracking yet — base on local branch

    wt = Path(tempfile.mkdtemp(prefix="um-publish-"))
    tmp_branch = "_um-publish-tmp"
    try:
        if run(["git", "worktree", "add", "--quiet", "-B", tmp_branch, str(wt), base], root).returncode != 0:
            if not args.quiet:
                print("publish: could not create worktree — skipping")
            return 0
        for attempt in (1, 2):
            dst = wt / rel
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(root / rel, dst)
            # Force-add: the per-session data is git-ignored in working trees (so a
            # generated-but-not-yet-pulled file never blocks a fast-forward/merge of
            # the shared branch). It must still be committed HERE to reach the branch
            # the aggregate workflow reads — hence -f.
            run(["git", "add", "-f", "--", rel], wt)
            if run(["git", "diff", "--cached", "--quiet", "--", rel], wt).returncode == 0:
                if not args.quiet:
                    print("publish: no changes to publish")
                return 0
            run(["git", "-c", "user.name=usage-metrics",
                 "-c", "user.email=usage-metrics@local",
                 "commit", "-m", f"usage-metrics: publish {tf} data"], wt)
            if args.dry_run:
                if not args.quiet:
                    print(f"[dry-run] would push {rel} → {branch} (worktree isolated; working tree untouched)")
                return 0
            if run(["git", "push", "origin", f"HEAD:{branch}"], wt).returncode == 0:
                if not args.quiet:
                    print(f"publish: pushed {rel} → {branch}")
                return 0
            # non-fast-forward → re-sync to the latest tip and retry once
            run(["git", "fetch", "origin", branch], root)
            run(["git", "reset", "--hard", f"origin/{branch}"], wt)
        if not args.quiet:
            print("publish: push did not succeed (will retry next session)")
        return 0
    finally:
        run(["git", "worktree", "remove", "--force", str(wt)], root)
        run(["git", "branch", "-D", tmp_branch], root)
        shutil.rmtree(wt, ignore_errors=True)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception as e:  # never disrupt the session
        print(f"publish: error (ignored): {e}", file=sys.stderr)
        raise SystemExit(0)
