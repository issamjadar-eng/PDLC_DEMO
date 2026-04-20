#!/usr/bin/env python3
"""Project CHANGELOG.md builder for the /digest skill.

Finds the last `## YYYY-MM-DD HH:MM` header in CHANGELOG.md, queries git log
since that timestamp, filters to significant commits, groups by theme, and
emits a proposed new section to stdout. The /digest log action shows this to
the user for approval before writing.

First run (no prior header in CHANGELOG.md) scans full history — retrospective
mode. Subsequent runs use the last dated header as the since-cursor.

Invoked by:
  - /digest log action

Exit codes:
  0  success (section written to stdout, or no significant commits to write)
  1  not in a git repo, or CHANGELOG.md missing
  2  invalid arguments
"""
from __future__ import annotations

import argparse
import fnmatch
import re
import subprocess
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path


# Significance rule: a commit is significant if (subject matches TASK_REF_RE)
# OR (any file matches TRIGGER_PATHS) OR (a SKILL.md version bumped) OR (a
# new skill/DHF landed). Everything else drops. There is no explicit
# "chore:" denylist — commits with those prefixes simply don't match the
# triggers unless they also touch a trigger path (e.g. `chore: update
# CLAUDE.md`), in which case we deliberately want them in.

TASK_REF_RE = re.compile(r"\btask\s+0*\d+\b", re.IGNORECASE)

# For rewriting bare `task NNN:` refs in commit subjects into `task <person>/NNN:`
# per the project convention (.claude/skills/lessons/SKILL.md:115 —
# "Task reference format: <task_folder>/<NNN>, used anywhere a task is
# referenced across team members"). Built lazily on first use.
BARE_TASK_RE = re.compile(r"\btask\s+(0*\d+)\b", re.IGNORECASE)

TRIGGER_PATHS = [
    "CLAUDE.md",
    "project.yml",
    "docs/project/strategies/*",
    "docs/project/strategies/**",
    "docs/project/submissions/**/composition-manifest.md",
    "docs/external/standards/*.md",
]


@dataclass
class Commit:
    sha: str
    short_sha: str
    author_name: str
    author_email: str
    date: str
    subject: str
    body: str = ""
    files: list[str] = field(default_factory=list)


def git(*args: str, check: bool = True) -> str:
    res = subprocess.run(["git", *args], capture_output=True, text=True, check=check)
    return res.stdout


def load_commits(since: str | None) -> list[Commit]:
    fmt = "%H%x00%h%x00%an%x00%ae%x00%aI%x00%s%x00%b%x1e"
    args = ["log", "--pretty=format:" + fmt, "--date=iso-strict"]
    if since:
        args += [f"--since={since}"]
    raw = git(*args)
    if not raw.strip():
        return []

    commits: list[Commit] = []
    for entry in raw.strip().split("\x1e"):
        entry = entry.strip("\n")
        if not entry:
            continue
        parts = entry.split("\x00")
        if len(parts) < 7:
            continue
        sha, short_sha, name, email, date, subject, body = parts[:7]
        commits.append(Commit(sha, short_sha, name, email, date, subject, body))

    for c in commits:
        out = git("diff-tree", "--no-commit-id", "--name-only", "-r", c.sha, check=False)
        c.files = [ln for ln in out.strip().split("\n") if ln]
    return commits


def matches_any(path: str, patterns: list[str]) -> bool:
    for pat in patterns:
        if fnmatch.fnmatch(path, pat):
            return True
    return False


_TASK_FOLDER_CACHE: dict[str, str] | None = None


def _build_task_folder_cache() -> dict[str, str]:
    """Map `<NNN>` (zero-padded 3-digit) to its owning `<person>` folder.

    Walks `tasks/*/NNN-*.md`. If a number exists under multiple folders (shouldn't
    happen per convention, but tolerate it), pick the first alphabetically.
    """
    cache: dict[str, str] = {}
    from pathlib import Path as _P
    for p in sorted(_P("tasks").glob("*/[0-9][0-9][0-9]-*.md")):
        num = p.name[:3]
        person = p.parent.name
        cache.setdefault(num, person)
    return cache


def _get_task_folder(num_str: str) -> str | None:
    """Look up the person folder for a task number (string, e.g. '018' or '18').

    Zero-pads to 3 digits before lookup. Returns None if no task file with that
    number exists under any `tasks/<person>/`.
    """
    global _TASK_FOLDER_CACHE
    if _TASK_FOLDER_CACHE is None:
        _TASK_FOLDER_CACHE = _build_task_folder_cache()
    padded = num_str.zfill(3)
    return _TASK_FOLDER_CACHE.get(padded)


def rewrite_task_refs(text: str) -> str:
    """Rewrite bare `task NNN` → `task <person>/NNN` per project convention.

    Leaves the text alone if the task number can't be resolved to a folder (so
    we don't silently drop references to deleted or unindexed tasks).
    """
    def _sub(m: re.Match[str]) -> str:
        raw = m.group(0)           # e.g. "task 018"
        num = m.group(1)           # e.g. "018"
        person = _get_task_folder(num)
        if person is None:
            return raw
        # Preserve the caller's word "task" and capitalization; just inject the prefix.
        prefix = raw[: m.start(1) - m.start()]  # "task " (with original whitespace)
        padded = num.zfill(3)
        return f"{prefix}{person}/{padded}"
    return BARE_TASK_RE.sub(_sub, text)


def is_version_bumped_skillmd(commit: Commit) -> list[str]:
    """Return any .claude/skills/*/SKILL.md paths where this commit changed the version field."""
    bumped: list[str] = []
    for f in commit.files:
        if not (f.startswith(".claude/skills/") and f.endswith("/SKILL.md")):
            continue
        before = git("show", f"{commit.sha}^:{f}", check=False)
        after = git("show", f"{commit.sha}:{f}", check=False)
        before_v = _extract_version(before)
        after_v = _extract_version(after)
        if before_v != after_v and after_v is not None:
            bumped.append(f)
    return bumped


def _extract_version(content: str) -> str | None:
    m = re.search(r"^version:\s*(\S+)", content, re.MULTILINE)
    return m.group(1) if m else None


def is_new_dhf(commit: Commit) -> list[str]:
    """Detect newly-added DHF folders — heuristic: a new README.md added under docs/project/dhfs/*/."""
    added = git("show", "--diff-filter=A", "--name-only", "--pretty=format:", commit.sha, check=False)
    new_dhfs: list[str] = []
    for ln in added.splitlines():
        m = re.match(r"^(docs/project/dhfs/[^/]+)/README\.md$", ln)
        if m:
            new_dhfs.append(m.group(1))
    return new_dhfs


def is_new_skill(commit: Commit) -> list[str]:
    added = git("show", "--diff-filter=A", "--name-only", "--pretty=format:", commit.sha, check=False)
    new_skills: list[str] = []
    for ln in added.splitlines():
        m = re.match(r"^(\.claude/skills/[^/]+)/SKILL\.md$", ln)
        if m:
            new_skills.append(m.group(1))
    return new_skills


def is_significant(commit: Commit) -> bool:
    """Apply the significance filter. Returns True if the commit belongs in CHANGELOG.md."""
    if TASK_REF_RE.search(commit.subject):
        return True
    for f in commit.files:
        if matches_any(f, TRIGGER_PATHS):
            return True
    if is_version_bumped_skillmd(commit):
        return True
    if is_new_skill(commit):
        return True
    if is_new_dhf(commit):
        return True
    return False


def theme_for_commit(commit: Commit) -> str:
    """Classify a commit into one theme. Checks themes in priority order."""
    # Skills: version bumps or new/removed skills
    if is_version_bumped_skillmd(commit) or is_new_skill(commit):
        return "Skills"
    # Tasks Completed: commit subject has "task NNN" AND (touches tasks/*/000-index.md OR subject mentions "close"/"complete")
    if TASK_REF_RE.search(commit.subject):
        for f in commit.files:
            if f.startswith("tasks/") and f.endswith("/000-index.md"):
                subj = commit.subject.lower()
                if "close" in subj or "complete" in subj or "closed" in subj:
                    return "Tasks Completed"
        return "Tasks"
    # Project Structure: CLAUDE.md, project.yml, new DHFs, composition manifests
    for f in commit.files:
        if f in ("CLAUDE.md", "project.yml"):
            return "Project Structure"
        if f.startswith("docs/project/dhfs/"):
            return "Project Structure"
        if f.endswith("composition-manifest.md"):
            return "Project Structure"
    if is_new_dhf(commit):
        return "Project Structure"
    # Documentation: strategies, standards, submissions, docs/*
    for f in commit.files:
        if f.startswith("docs/"):
            return "Documentation"
    return "Other"


THEME_ORDER = ["Skills", "Tasks Completed", "Tasks", "Project Structure", "Documentation", "Other"]


def emit_section(
    commits: list[Commit],
    title: str | None,
    retrospective: bool,
) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    # Group by theme
    themed: dict[str, list[Commit]] = defaultdict(list)
    for c in commits:
        themed[theme_for_commit(c)].append(c)

    # Generate default title if none supplied
    if title is None:
        if retrospective:
            title = "Project retrospective"
        else:
            # Most significant theme = largest non-empty in priority order
            for t in THEME_ORDER:
                if themed.get(t):
                    if t == "Skills":
                        title = "Skill updates"
                    elif t == "Tasks Completed":
                        title = "Tasks completed"
                    elif t == "Tasks":
                        title = "Task work"
                    elif t == "Project Structure":
                        title = "Project structure changes"
                    elif t == "Documentation":
                        title = "Documentation updates"
                    else:
                        title = "Activity update"
                    break
            if title is None:
                title = "Activity update"

    lines: list[str] = []
    lines.append(f"## {now} — {title}")
    lines.append("")
    if retrospective:
        lines.append("_Retrospective pass covering project history to date._")
        lines.append("")
    if not commits:
        lines.append("No significant commits in this window.")
        lines.append("")
        return "\n".join(lines)

    lines.append(f"**{len(commits)} significant commit(s)** across {len([t for t in themed if themed[t]])} theme(s).")
    lines.append("")

    for theme in THEME_ORDER:
        entries = themed.get(theme, [])
        if not entries:
            continue
        lines.append(f"### {theme}")
        lines.append("")
        # Deduplicate by subject for readability. Rewrite bare task refs to
        # `<person>/NNN` per project convention (lessons/SKILL.md:115).
        seen_subjects: set[str] = set()
        for c in entries:
            key = c.subject
            if key in seen_subjects:
                continue
            seen_subjects.add(key)
            subject = rewrite_task_refs(c.subject)
            lines.append(f"- {subject} (`{c.short_sha}` — {c.author_name}, {c.date[:10]})")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def find_last_dated_header(changelog_path: Path) -> str | None:
    """Return the ISO timestamp embedded in the topmost `## YYYY-MM-DD HH:MM` header,
    or None if no dated header exists. The header format is:
        ## YYYY-MM-DD HH:MM UTC — <title>
    and git --since accepts `YYYY-MM-DD HH:MM` directly.
    """
    if not changelog_path.exists():
        return None
    content = changelog_path.read_text()
    # Match the first dated header (topmost since CHANGELOG is reverse-chronological)
    m = re.search(r"^##\s+(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2})\s*(?:UTC)?", content, re.MULTILINE)
    if not m:
        return None
    return m.group(1)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Build project CHANGELOG.md section")
    ap.add_argument("--since", help="ISO cutoff timestamp; overrides CHANGELOG.md header")
    ap.add_argument("--title", help="Section title")
    ap.add_argument("--dry-run", action="store_true",
                    help="Emit to stdout; do not modify CHANGELOG.md (caller handles writes)")
    ap.add_argument("--retrospective", action="store_true",
                    help="Mark the section as retrospective (first run)")
    ap.add_argument("--changelog", default="CHANGELOG.md",
                    help="Path to CHANGELOG.md (default: repo root)")
    args = ap.parse_args(argv)

    try:
        git("rev-parse", "--git-dir")
    except subprocess.CalledProcessError:
        print("error: not in a git repo", file=sys.stderr)
        return 1

    changelog_path = Path(args.changelog)
    since = args.since
    retrospective = args.retrospective
    if retrospective:
        # Explicit retrospective — full history scan, ignore any bootstrap header
        since = None
    elif since is None:
        last = find_last_dated_header(changelog_path)
        if last:
            since = last
        else:
            retrospective = True

    commits = load_commits(since)
    # Filter to significant
    sig = [c for c in commits if is_significant(c)]

    out = emit_section(sig, args.title, retrospective)
    sys.stdout.write(out)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
