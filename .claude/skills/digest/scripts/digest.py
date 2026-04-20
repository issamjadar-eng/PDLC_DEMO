#!/usr/bin/env python3
"""Daily briefing aggregator for the /digest skill.

Reads commits since a cutoff timestamp and emits a short markdown digest to
stdout. Grouped by author. "Pay attention" section covers structural,
skill, and project-level changes. See ../SKILL.md for the full contract.

Invoked by:
  - scripts/session-briefing.sh (SessionStart hook)
  - /digest daily action (user-invoked preview)

Exit codes:
  0  success (digest written to stdout)
  1  git not available or not in a git repo
  2  invalid arguments
"""
from __future__ import annotations

import argparse
import fnmatch
import os
import re
import subprocess
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Path patterns for the "Pay attention" filter. Groups are rendered in this
# order. Each pattern uses fnmatch semantics against git-reported paths.
PAY_ATTENTION_GROUPS: list[tuple[str, list[str]]] = [
    ("Structural", [
        "CLAUDE.md",
        "project.yml",
        ".claude/rules/*",
        ".claude/rules/**",
    ]),
    ("Skill updates", [
        ".claude/skills/*/SKILL.md",
        ".claude/skills/*/VERSION",
        ".claude/sync-log.md",
    ]),
    ("Project-level", [
        "docs/project/strategies/*",
        "docs/project/strategies/**",
        "docs/project/submissions/**/composition-manifest.md",
        "docs/external/standards/*.md",
    ]),
]


@dataclass
class Commit:
    sha: str
    short_sha: str
    author_email: str
    author_name: str
    date: str  # ISO
    subject: str
    files: list[str] = field(default_factory=list)


def git(*args: str, check: bool = True) -> str:
    try:
        res = subprocess.run(
            ["git", *args],
            capture_output=True,
            text=True,
            check=check,
        )
    except FileNotFoundError:
        print("error: git not found on PATH", file=sys.stderr)
        sys.exit(1)
    return res.stdout


def load_commits(since: str | None) -> list[Commit]:
    """Return commits since `since` (ISO timestamp) or all commits if None."""
    # Use NUL as field separator to survive subjects containing |
    fmt = "%H%x00%h%x00%ae%x00%an%x00%aI%x00%s"
    args = ["log", "--pretty=format:" + fmt, "--date=iso-strict"]
    if since:
        args += [f"--since={since}"]
    raw = git(*args)
    if not raw.strip():
        return []

    commits: list[Commit] = []
    for line in raw.strip().split("\n"):
        parts = line.split("\x00")
        if len(parts) < 6:
            continue
        sha, short_sha, email, name, date, subject = parts[:6]
        commits.append(Commit(sha, short_sha, email, name, date, subject))

    # Populate files for each commit with one diff-tree call per SHA. This is
    # fine at briefing scale (commits since 12h ago).
    for c in commits:
        out = git("diff-tree", "--no-commit-id", "--name-only", "-r", c.sha, check=False)
        c.files = [ln for ln in out.strip().split("\n") if ln]
    return commits


def matches_any(path: str, patterns: list[str]) -> bool:
    for pat in patterns:
        if fnmatch.fnmatch(path, pat):
            return True
    return False


def detect_new_skill_dirs(commits: list[Commit]) -> set[str]:
    """New skill directories detected by the presence of SKILL.md added in a commit.

    Uses git log --diff-filter=A to identify added files. Deduplicates by skill
    directory.
    """
    seen: set[str] = set()
    if not commits:
        return seen
    # Find adds within the commit range.
    oldest_sha = commits[-1].sha
    newest_sha = commits[0].sha
    out = git(
        "log", f"{oldest_sha}^..{newest_sha}",
        "--diff-filter=A", "--name-only", "--pretty=format:",
        check=False,
    )
    for ln in out.splitlines():
        ln = ln.strip()
        m = re.match(r"^(\.claude/skills/[^/]+)/SKILL\.md$", ln)
        if m:
            seen.add(m.group(1))
    return seen


def group_by_author(commits: list[Commit]) -> dict[str, list[Commit]]:
    groups: dict[str, list[Commit]] = defaultdict(list)
    for c in commits:
        key = f"{c.author_name} <{c.author_email}>"
        groups[key].append(c)
    return groups


def classify_pay_attention(commits: list[Commit]) -> dict[str, list[tuple[str, Commit]]]:
    """Return {group_name: [(file, commit), ...]} for files matching each group."""
    result: dict[str, list[tuple[str, Commit]]] = defaultdict(list)
    for c in commits:
        for f in c.files:
            for group_name, patterns in PAY_ATTENTION_GROUPS:
                if matches_any(f, patterns):
                    result[group_name].append((f, c))
                    break
    return result


def format_commit_line(c: Commit) -> str:
    return f"`{c.short_sha}` {c.subject}"


def emit_briefing(
    commits: list[Commit],
    since: str | None,
    new_skills: set[str],
) -> str:
    lines: list[str] = []
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    window = f"since {since}" if since else "(no prior briefing — showing last 24h)"
    lines.append(f"# Daily briefing — {now}")
    lines.append("")
    lines.append(f"_{window}_")
    lines.append("")
    if not commits:
        lines.append("No new commits in this window.")
        lines.append("")
        return "\n".join(lines)

    lines.append(f"**{len(commits)} commit(s)** in this window.")
    lines.append("")

    # Commits grouped by author
    lines.append("## Commits")
    lines.append("")
    authors = group_by_author(commits)
    for author, cs in sorted(authors.items(), key=lambda kv: -len(kv[1])):
        lines.append(f"**{author}** — {len(cs)} commit(s)")
        for c in cs[:8]:
            lines.append(f"  - {format_commit_line(c)}")
        if len(cs) > 8:
            lines.append(f"  - _(+{len(cs) - 8} more)_")
        lines.append("")

    # Pay attention
    pay = classify_pay_attention(commits)
    if pay or new_skills:
        lines.append("## Pay attention")
        lines.append("")
        for group_name, _patterns in PAY_ATTENTION_GROUPS:
            entries = pay.get(group_name, [])
            if not entries:
                continue
            # Deduplicate (file, commit) but keep order stable
            seen_pairs: set[tuple[str, str]] = set()
            deduped: list[tuple[str, Commit]] = []
            for f, c in entries:
                key = (f, c.sha)
                if key in seen_pairs:
                    continue
                seen_pairs.add(key)
                deduped.append((f, c))
            lines.append(f"**{group_name}** ({len(deduped)} change(s))")
            for f, c in deduped[:8]:
                lines.append(f"  - `{f}` (`{c.short_sha}` {c.subject})")
            if len(deduped) > 8:
                lines.append(f"  - _(+{len(deduped) - 8} more)_")
            lines.append("")

        if new_skills:
            lines.append(f"**New skills** ({len(new_skills)})")
            for s in sorted(new_skills):
                lines.append(f"  - `{s}/`")
            lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def default_since() -> str:
    """Fallback cutoff: 24 hours ago."""
    dt = datetime.now(timezone.utc) - timedelta(hours=24)
    return dt.isoformat(timespec="seconds")


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Daily briefing for /digest skill")
    ap.add_argument("--since", help="ISO-8601 cutoff timestamp")
    ap.add_argument("--dry-run", action="store_true",
                    help="compute but do not update state (no-op here — caller owns state)")
    args = ap.parse_args(argv)

    # Check we're in a git repo
    try:
        git("rev-parse", "--git-dir")
    except SystemExit:
        raise
    except Exception:
        print("error: not in a git repo", file=sys.stderr)
        return 1

    since = args.since or default_since()
    commits = load_commits(since)
    new_skills = detect_new_skill_dirs(commits)
    out = emit_briefing(commits, since, new_skills)
    sys.stdout.write(out)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
