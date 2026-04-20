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
import json
import re
import subprocess
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

# Commit trailers to drop when extracting the "human paragraph" of a commit
# body. Matched at the START of a line, case-insensitive.
TRAILER_PREFIXES = (
    "Co-Authored-By:", "Co-authored-by:", "Signed-off-by:", "Reviewed-by:",
    "Fixes:", "Closes:", "Refs:", "See:", "Link:",
)

# Subjects that start with these prefixes lose them when cleaned — they
# read as metadata, not narrative.
CLEANUP_SUBJECT_PREFIXES = (
    "chore:", "fmt:", "lint:", "style:", "typo:", "docs:", "test:",
    "feat:", "fix:", "refactor:", "perf:", "build:", "ci:",
)

# Where the LLM cache lives. Keyed on commit SHA.
LLM_CACHE_PATH = Path(".claude/state/digest-llm-cache.json")


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


def clean_subject(subject: str) -> str:
    """Strip task-ref and metadata prefixes, capitalize first letter.

    `task ben/018: sync-skills pull (53 files) + close 16 Required FAILs`
      → `Sync-skills pull (53 files) + close 16 Required FAILs`
    `chore: bump deps`
      → `Bump deps`
    """
    s = subject.strip()
    # Strip leading "task <person>/NNN:" or "task NNN:"
    s = re.sub(r"^\s*task\s+\S+?\s*:\s*", "", s, flags=re.IGNORECASE)
    # Strip conventional-commit-style prefix
    for pref in CLEANUP_SUBJECT_PREFIXES:
        if s.lower().startswith(pref):
            s = s[len(pref):].strip()
            break
    # Capitalize first letter
    if s:
        s = s[0].upper() + s[1:]
    return s


def extract_body_paragraph(body: str) -> str:
    """Return the first real paragraph of a commit body, stripping trailers.

    A "paragraph" is lines separated from the next by a blank line. Lines
    that look like trailers (Co-Authored-By:, Signed-off-by:, etc.) are
    treated as a trailer block and excluded.
    """
    if not body:
        return ""
    # Normalize line endings, split into paragraphs
    paragraphs: list[list[str]] = []
    current: list[str] = []
    for raw in body.splitlines():
        line = raw.rstrip()
        if not line.strip():
            if current:
                paragraphs.append(current)
                current = []
            continue
        if line.startswith(TRAILER_PREFIXES):
            # Terminate current paragraph; stop reading further
            if current:
                paragraphs.append(current)
            current = []
            break
        current.append(line)
    if current:
        paragraphs.append(current)

    if not paragraphs:
        return ""
    first = " ".join(p.strip() for p in paragraphs[0])
    # Collapse double-spaces
    return re.sub(r"\s+", " ", first).strip()


def extract_readable_mechanical(c: Commit) -> tuple[str, str]:
    """Return (headline, body) extracted mechanically from commit subject + body.

    Headline: cleaned subject (strip task ref, strip conventional-prefix,
    capitalize).
    Body: first paragraph of commit message body, trailers removed.
    """
    headline = clean_subject(c.subject)
    body = extract_body_paragraph(c.body)
    # If the body first sentence repeats the headline, drop it
    if body and headline and body.lower().startswith(headline.lower()):
        tail = body[len(headline):].lstrip(" .—-:")
        body = tail
    return headline, body


def batch_summarize_llm(commits: list[Commit], quiet: bool = False) -> dict[str, dict[str, str]]:
    """Call `claude -p` ONCE with all commits as a JSON input; parse the
    returned JSON array of summaries. Cache results by SHA.

    Returns {sha: {"headline": "...", "body": "..."}}. On any failure (claude
    CLI missing, timeout, parse error), falls back to mechanical extraction
    and caches nothing so a future run can retry.
    """
    cache: dict[str, dict[str, str]] = {}
    if LLM_CACHE_PATH.exists():
        try:
            cache = json.loads(LLM_CACHE_PATH.read_text())
        except (json.JSONDecodeError, OSError):
            cache = {}

    to_summarize = [c for c in commits if c.sha not in cache]
    if not to_summarize:
        if not quiet:
            print(f"[build_changelog] LLM cache hit for all {len(commits)} commits",
                  file=sys.stderr)
        return {sha: cache[sha] for sha in (c.sha for c in commits) if sha in cache}

    if not quiet:
        print(f"[build_changelog] batching {len(to_summarize)} uncached commits "
              f"({len(commits) - len(to_summarize)} cached) via claude -p", file=sys.stderr)

    # Build the batch payload — compact JSON input so the model can chew through all at once
    payload = []
    for c in to_summarize:
        # Trim body aggressively — 1500 chars is plenty for a paragraph
        body = (c.body or "")[:1500]
        payload.append({
            "sha": c.short_sha,
            "subject": c.subject,
            "body": body,
            "files_sample": c.files[:15],
        })
    user_msg = (
        "Rewrite each of the following git commits as a plain-English CHANGELOG "
        "entry for a non-technical reader (project manager, regulatory reviewer, "
        "newcomer). Return a JSON array with one object per input commit, each "
        "containing:\n"
        "  - sha: the commit's short SHA (copy from input)\n"
        "  - headline: ONE plain-English sentence, <=25 words. No unexplained "
        "jargon. Lead with the outcome, not the tool name.\n"
        "  - body: ONE optional follow-up sentence, <=30 words, giving context "
        "(why it matters, what downstream impact it has). Use empty string if "
        "the headline stands alone.\n\n"
        "Respond with ONLY the JSON array. No prose, no markdown fences.\n\n"
        "Input:\n" + json.dumps(payload, indent=2)
    )
    system_prompt = (
        "You are a project changelog writer. Rewrite git commits as plain "
        "English for non-technical readers. Prefer outcome over mechanism. "
        "Never emit 'task ben/NNN:' or SHA references in the headline or body — "
        "those go in a separate trace footer the reader will see below. "
        "Explain unavoidable jargon briefly inline."
    )

    cmd = [
        "claude", "-p",
        "--model", "haiku",
        "--output-format", "json",
        "--no-session-persistence",
        "--disable-slash-commands",
        "--system-prompt", system_prompt,
        user_msg,
    ]
    # Run claude from a neutral cwd (/tmp) so it doesn't pick up THIS
    # project's CLAUDE.md, skills, or hooks. The CLI discovers context by
    # walking up from cwd; pinning to /tmp keeps the invocation pure
    # text-in / JSON-out. Also clear CLAUDE_PROJECT_DIR in case something
    # else set it.
    env = {k: v for k, v in __import__("os").environ.items() if not k.startswith("CLAUDE_")}
    env.setdefault("PATH", __import__("os").environ.get("PATH", ""))
    env.setdefault("HOME", __import__("os").environ.get("HOME", ""))
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, check=False, timeout=180,
            cwd="/tmp", env=env,
        )
    except subprocess.TimeoutExpired:
        if not quiet:
            print("[build_changelog] claude -p timed out; falling back to mechanical",
                  file=sys.stderr)
        return {}
    except FileNotFoundError:
        if not quiet:
            print("[build_changelog] claude CLI not found; falling back to mechanical",
                  file=sys.stderr)
        return {}

    if result.returncode != 0:
        if not quiet:
            print(f"[build_changelog] claude -p failed (rc={result.returncode}): "
                  f"{result.stderr[:300]}", file=sys.stderr)
        return {}

    # The CLI returns a JSON envelope; extract the "result" field
    try:
        envelope = json.loads(result.stdout)
        raw_result = envelope.get("result", "").strip()
    except json.JSONDecodeError:
        if not quiet:
            print("[build_changelog] claude envelope not JSON; falling back",
                  file=sys.stderr)
        return {}

    # Strip ```json ... ``` fences if the model added them
    raw_result = re.sub(r"^```(?:json)?\s*", "", raw_result)
    raw_result = re.sub(r"\s*```\s*$", "", raw_result).strip()

    try:
        arr = json.loads(raw_result)
    except json.JSONDecodeError:
        if not quiet:
            print(f"[build_changelog] summary JSON parse failed: {raw_result[:200]}",
                  file=sys.stderr)
        return {}

    # Resolve short_sha back to full sha for cache keying
    short_to_full = {c.short_sha: c.sha for c in to_summarize}
    for entry in arr:
        sha_key = entry.get("sha", "")
        full = short_to_full.get(sha_key)
        if not full:
            continue
        cache[full] = {
            "headline": str(entry.get("headline", "")).strip(),
            "body": str(entry.get("body", "")).strip(),
        }

    # Persist cache
    try:
        LLM_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
        LLM_CACHE_PATH.write_text(json.dumps(cache, indent=2, sort_keys=True))
    except OSError:
        pass

    return {c.sha: cache[c.sha] for c in commits if c.sha in cache}


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


def extract_task_ref(subject: str) -> str | None:
    """Return the task reference in `<person>/<NNN>` form if the commit
    subject contains one (either already in the person-prefixed form or a
    bare `task NNN` that resolves). None if no ref.
    """
    # Prefer a pre-qualified ref like `ben/018` or `task ben/018:`
    m = re.search(r"\b(\w+)/(\d{3,})\b", subject)
    if m:
        return f"{m.group(1)}/{m.group(2)}"
    # Fall back to bare `task NNN` resolving via the cache
    m = re.search(r"\btask\s+(0*\d+)\b", subject, re.IGNORECASE)
    if m:
        global _TASK_FOLDER_CACHE
        if _TASK_FOLDER_CACHE is None:
            _TASK_FOLDER_CACHE = _build_task_folder_cache()
        padded = m.group(1).zfill(3)
        person = _TASK_FOLDER_CACHE.get(padded)
        if person:
            return f"{person}/{padded}"
    return None


def emit_section(
    commits: list[Commit],
    title: str | None,
    retrospective: bool,
    summaries: dict[str, dict[str, str]] | None = None,
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

    summaries = summaries or {}

    for theme in THEME_ORDER:
        entries = themed.get(theme, [])
        if not entries:
            continue
        lines.append(f"### {theme}")
        lines.append("")
        # Deduplicate by subject for readability.
        seen_subjects: set[str] = set()
        for c in entries:
            if c.subject in seen_subjects:
                continue
            seen_subjects.add(c.subject)

            # Source of headline + body: LLM summary if available, else
            # mechanical extraction from commit body + subject.
            if c.sha in summaries:
                headline = summaries[c.sha].get("headline", "") or clean_subject(c.subject)
                body_line = summaries[c.sha].get("body", "") or ""
            else:
                headline, body_line = extract_readable_mechanical(c)

            # Trace footer — task ref, sha, author, date, all muted.
            trace_parts: list[str] = []
            task_ref = extract_task_ref(c.subject)
            if task_ref:
                trace_parts.append(task_ref)
            trace_parts.append(f"`{c.short_sha}`")
            trace_parts.append(c.author_name)
            trace_parts.append(c.date[:10])
            trace = "_" + " · ".join(trace_parts) + "_"

            lines.append(f"- **{headline}**")
            if body_line:
                lines.append(f"  {body_line}")
            lines.append(f"  {trace}")
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
    ap.add_argument("--llm", action="store_true",
                    help="Use `claude -p` (batched) to rewrite commits as "
                         "plain-English CHANGELOG entries. Auto-enabled for "
                         "--retrospective.")
    ap.add_argument("--no-llm", action="store_true",
                    help="Disable LLM summarization even if --retrospective.")
    ap.add_argument("--quiet", action="store_true",
                    help="Suppress diagnostic stderr (LLM batching progress etc.)")
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

    # Decide whether to use the LLM. Retrospective runs default to --llm
    # for a polished baseline; --no-llm overrides.
    use_llm = args.llm or (retrospective and not args.no_llm)
    summaries: dict[str, dict[str, str]] = {}
    if use_llm and sig:
        summaries = batch_summarize_llm(sig, quiet=args.quiet)

    out = emit_section(sig, args.title, retrospective, summaries)
    sys.stdout.write(out)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
