#!/usr/bin/env python3
"""Roster-driven user identity resolver.

Resolves the current session's user by matching `git config user.email`
(and related signals) against `project.yml` `team.active[]`. Used by:

  - /secops setup          (aligns repo-local git config to roster identity)
  - /secops security-assert (defensive re-align at SessionStart)
  - /digest session-briefing.sh  (stable state-file key via task_folder)

Usage:
  resolve_user.py               emit JSON with task_folder, name, email,
                                github, match_reason (or unresolved=true)
  resolve_user.py --task-folder emit JUST the task_folder string on stdout
                                (for shell state-file keys)
  resolve_user.py --align-git   resolve + write repo-local git config if
                                mismatched. emits JSON diagnostic.

Match heuristics (priority order):
  1. git user.email exactly matches team.active[].email
  2. single-member roster → take that member (--align-git will fix drift)
  3. git user.name substring-matches team.active[].name (case-insensitive)
  4. $USER env matches team.active[].task_folder exactly
  5. no match → emit the slug fallback (never aligns git in this branch)
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path


def parse_roster(yml_text: str) -> list[dict[str, str]]:
    """Extract team.active[] entries from project.yml as a list of dicts.

    Minimal parser (no PyYAML dep) — matches the stable shape of
    project.yml used across PDLC_DEMO + Arthrex PCCP. Each active entry
    is a block of `    <key>: <value>` lines under `  - name: ...`.
    """
    # Isolate the active: ... inactive: region.
    m = re.search(
        r"^team:\s*\n"
        r"\s*active:\s*\n"
        r"(?P<body>(?:[ \t]+(?:-[ \t]+)?\w+:.*\n|[ \t]*\n)+?)"
        r"(?=\s*inactive:|^\S)",
        yml_text,
        re.MULTILINE,
    )
    if not m:
        return []

    body = m.group("body")
    entries: list[dict[str, str]] = []
    current: dict[str, str] | None = None

    for raw in body.splitlines():
        line = raw.rstrip()
        if not line.strip():
            continue
        # A new entry starts with "-"
        lead = re.match(r"^\s*-\s+(\w+):\s*(.*)$", line)
        if lead:
            if current:
                entries.append(current)
            current = {}
            key, val = lead.group(1), lead.group(2)
            current[key] = val.strip().strip('"').strip("'")
            continue
        kv = re.match(r"^\s+(\w+):\s*(.*)$", line)
        if kv and current is not None:
            current[kv.group(1)] = kv.group(2).strip().strip('"').strip("'")

    if current:
        entries.append(current)

    return entries


def git_config(key: str, *, scope: str = "") -> str:
    """Read a git config value. scope='' means effective (local over global);
    scope='--local' / '--global' / '--system' per git's semantics."""
    cmd = ["git", "config"]
    if scope:
        cmd.append(scope)
    cmd.extend(["--default", "", key])
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, check=False).stdout
    except FileNotFoundError:
        return ""
    return out.strip()


def set_git_local(key: str, value: str) -> None:
    subprocess.run(
        ["git", "config", "--local", key, value],
        check=True,
        capture_output=True,
        text=True,
    )


def slugify(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[@.]", "-", s)
    s = re.sub(r"[^a-z0-9-]", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s or "unknown-user"


def resolve(
    roster: list[dict[str, str]],
    git_email: str,
    git_name: str,
    os_user: str,
) -> tuple[dict[str, str] | None, str]:
    """Return (matched_entry, reason). None if no match."""
    ge = (git_email or "").strip().lower()
    gn = (git_name or "").strip().lower()
    ou = (os_user or "").strip().lower()

    # 1. Exact email match
    for m in roster:
        if m.get("email", "").strip().lower() == ge and ge:
            return m, "git-email-matches-roster"

    # 2. Single-member roster
    if len(roster) == 1:
        return roster[0], "single-member-roster"

    # 3. Fuzzy git user.name substring
    for m in roster:
        rname = m.get("name", "").strip().lower()
        if rname and (rname in gn or gn in rname) and gn:
            return m, "git-name-fuzzy-match"

    # 4. OS user matches task_folder
    for m in roster:
        tf = m.get("task_folder", "").strip().lower()
        if tf and tf == ou and ou:
            return m, "os-user-matches-task-folder"

    return None, "no-match"


def align_git_if_needed(
    matched: dict[str, str],
    current_local_email: str,
    current_local_name: str,
) -> list[str]:
    """Write repo-local git config to match the roster entry. Returns a list
    of human-readable change descriptions (empty if no change was needed).

    Only sets --local config (never touches --global). Safe: a user's other
    projects are unaffected.
    """
    changes: list[str] = []
    roster_email = matched.get("email", "").strip()
    roster_name = matched.get("name", "").strip()

    if roster_email and current_local_email != roster_email:
        set_git_local("user.email", roster_email)
        changes.append(
            f"user.email: {current_local_email or '(unset)'} → {roster_email}"
        )
    if roster_name and current_local_name != roster_name:
        set_git_local("user.name", roster_name)
        changes.append(
            f"user.name: {current_local_name or '(unset)'} → {roster_name}"
        )
    return changes


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--task-folder", action="store_true",
                    help="emit JUST the task_folder string on stdout "
                         "(slug fallback if unresolved)")
    ap.add_argument("--align-git", action="store_true",
                    help="write repo-local git user.email/user.name to the "
                         "roster values if drift is detected")
    ap.add_argument("--project-yml", default="project.yml",
                    help="path to project.yml (default: ./project.yml)")
    ap.add_argument("--quiet", action="store_true",
                    help="suppress diagnostic stderr from --align-git")
    args = ap.parse_args(argv)

    yml_path = Path(args.project_yml)
    if not yml_path.exists():
        # No project.yml — graceful fallback to raw git email slug.
        result = {
            "unresolved": True,
            "reason": "no-project-yml",
            "task_folder": None,
            "slug": slugify(git_config("user.email")),
        }
        if args.task_folder:
            print(result["slug"])
        else:
            print(json.dumps(result, indent=2))
        return 0

    roster = parse_roster(yml_path.read_text())
    git_email = git_config("user.email")  # effective (local over global)
    git_name = git_config("user.name")
    os_user = os.environ.get("USER", "")

    matched, reason = resolve(roster, git_email, git_name, os_user)

    if matched:
        task_folder = matched.get("task_folder", "").strip()
        result = {
            "unresolved": False,
            "match_reason": reason,
            "task_folder": task_folder,
            "name": matched.get("name", ""),
            "email": matched.get("email", ""),
            "github": matched.get("github", ""),
            "role": matched.get("role", ""),
        }

        if args.align_git:
            local_email = git_config("user.email", scope="--local")
            local_name = git_config("user.name", scope="--local")
            changes = align_git_if_needed(matched, local_email, local_name)
            result["git_alignment"] = {
                "changes": changes,
                "already_aligned": not changes,
            }
            if changes and not args.quiet:
                for c in changes:
                    print(f"[resolve_user] aligned git {c}", file=sys.stderr)

        if args.task_folder:
            print(task_folder or slugify(matched.get("email", "")))
        else:
            print(json.dumps(result, indent=2))
        return 0

    # No match — fall back to email slug
    slug = slugify(git_email) if git_email else "unknown-user"
    result = {
        "unresolved": True,
        "reason": reason,
        "task_folder": None,
        "slug": slug,
        "git_email": git_email,
        "git_name": git_name,
        "roster_size": len(roster),
    }
    if args.align_git and not args.quiet:
        print(
            f"[resolve_user] no roster match for git user.email "
            f"'{git_email}' (reason: {reason}); git config NOT aligned",
            file=sys.stderr,
        )
    if args.task_folder:
        print(slug)
    else:
        print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
