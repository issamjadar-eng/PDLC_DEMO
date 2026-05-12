"""B6 Create Draft session — per-row worktree + session task.

Mirrors `tracker_session.py` (B4) but keys on `(actor, row_id)` so multiple
rows can have concurrent draft sessions. One **active** session per row at
a time (per task 175 D4).

Worktree layout:
  - Path:   `.worktrees/workflow-tracker-draft-<row-id>-<YYYY-MM-DD>/`
  - Branch: `workflow/tracker-draft-<row-id>-<YYYY-MM-DD>`
  - Session task: `tasks/<actor>/NNN-tracker-draft-<row-id>-<YYYY-MM-DD>.md`

Per task 175 D8: drafts live at `_drafting/<row-id>-<slug>.md` at project
root inside the worktree for the entire draft session. Save & Commit
git-mv's to `target.path` from frontmatter atomic with the tracker md
update + ff-merge to main.
"""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

KIND = "tracker-draft"
TRACKER_MD_REL = "docs/project/submissions/submission-tracker.md"
TRACKER_HTML_REL = "docs/project/submissions/submission-tracker.html"
TRACKER_HUMAN_SIDECAR_REL = "docs/project/submissions/submission-tracker.human.json"
DRAFTING_DIR = "_drafting"


@dataclass(frozen=True)
class DraftSession:
    row_id: str
    actor_folder: str
    task_id: str
    task_path: str
    worktree_path: str
    branch: str
    staging_file: str | None      # repo-relative path to _drafting/<row-id>-*.md
    has_outline: bool
    has_synthesis: bool
    target_path: str | None       # from frontmatter, if synthesized


def today() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _run(args: list[str], cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(args, cwd=str(cwd), capture_output=True, text=True, timeout=30)


def _validate_row_id(row_id: str) -> None:
    if not re.match(r"^[A-Z][A-Z0-9-]+$", row_id):
        raise ValueError(f"invalid row_id {row_id!r} — expected uppercase alphanumeric+dash")


# ── Worktree management ──────────────────────────────────────────────────

def _existing_worktree_dir(repo_root: Path, row_id: str) -> Path | None:
    """Find an existing per-row draft worktree, regardless of date suffix.
    Returns the most-recently-modified match or None."""
    base = repo_root / ".worktrees"
    if not base.is_dir():
        return None
    pattern = f"workflow-tracker-draft-{row_id}-*"
    candidates = sorted(
        (p for p in base.glob(pattern) if p.is_dir() and (p / ".git").exists()),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return candidates[0] if candidates else None


def _existing_worktree_branch(wt: Path) -> str | None:
    r = _run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=wt)
    if r.returncode != 0:
        return None
    return (r.stdout or "").strip() or None


def worktree_branch(repo_root: Path, row_id: str) -> str:
    _validate_row_id(row_id)
    wt = _existing_worktree_dir(repo_root, row_id)
    if wt is not None:
        existing = _existing_worktree_branch(wt)
        if existing:
            return existing
    return f"workflow/tracker-draft-{row_id}-{today()}"


def worktree_path(repo_root: Path, row_id: str) -> Path:
    _validate_row_id(row_id)
    existing = _existing_worktree_dir(repo_root, row_id)
    if existing is not None:
        return existing
    return repo_root / ".worktrees" / f"workflow-tracker-draft-{row_id}-{today()}"


def ensure_worktree(repo_root: Path, row_id: str) -> Path:
    """Open (or reuse) the per-row draft worktree. Idempotent.

    Syncs the submission-tracker.md + sidecars from main's working tree
    into the worktree so any uncommitted edits on main are visible.
    """
    _validate_row_id(row_id)
    wt = worktree_path(repo_root, row_id)
    branch = worktree_branch(repo_root, row_id)
    if not (wt.is_dir() and (wt / ".git").exists()):
        wt.parent.mkdir(parents=True, exist_ok=True)
        # Try to recreate from existing branch first
        branch_exists = _run(["git", "show-ref", "--verify", "--quiet",
                              f"refs/heads/{branch}"], cwd=repo_root).returncode == 0
        if branch_exists:
            r = _run(["git", "worktree", "add", str(wt), branch], cwd=repo_root)
        else:
            r = _run(["git", "worktree", "add", "-B", branch, str(wt)], cwd=repo_root)
        if r.returncode != 0:
            raise RuntimeError(f"git worktree add failed: {r.stderr.strip()}")

    # Sync uncommitted tracker files from main into the worktree
    import shutil
    for rel in (TRACKER_MD_REL, TRACKER_HTML_REL, TRACKER_HUMAN_SIDECAR_REL):
        src = repo_root / rel
        if not src.is_file():
            continue
        dst = wt / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        try:
            src_text = src.read_text(encoding="utf-8")
            dst_text = dst.read_text(encoding="utf-8") if dst.exists() else ""
            if src_text != dst_text:
                shutil.copy2(src, dst)
        except OSError:
            continue

    # Ensure _drafting/ exists in the worktree
    (wt / DRAFTING_DIR).mkdir(exist_ok=True)
    return wt


def worktree_diff_summary(wt: Path) -> list[str]:
    r = _run(["git", "status", "--porcelain"], cwd=wt)
    if r.returncode != 0:
        return []
    return [ln for ln in r.stdout.splitlines() if ln.strip()]


def find_staging_file(wt: Path, row_id: str) -> Path | None:
    """Return the `_drafting/<row-id>-*.md` file inside the worktree, or None."""
    staging = wt / DRAFTING_DIR
    if not staging.is_dir():
        return None
    matches = sorted(staging.glob(f"{row_id}-*.md"))
    return matches[0] if matches else None


def _read_frontmatter(path: Path) -> dict:
    if not path.is_file():
        return {}
    text = path.read_text(encoding="utf-8", errors="ignore")
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---", 4)
    if end < 0:
        return {}
    fm_text = text[4:end]
    try:
        import yaml  # type: ignore
        return yaml.safe_load(fm_text) or {}
    except Exception:
        return {}


def cancel_workflow(repo_root: Path, actor_folder: str, row_id: str) -> dict:
    """Discard the draft session entirely: discard pending diff, remove the
    worktree, delete the branch, mark the backing task Abandoned.
    Idempotent."""
    _validate_row_id(row_id)
    wt = worktree_path(repo_root, row_id)
    branch = worktree_branch(repo_root, row_id)
    if not (wt.is_dir() and (wt / ".git").exists()):
        return {"status": "noop", "reason": "no open worktree"}
    _run(["git", "checkout", "HEAD", "--", "."], cwd=wt)
    _run(["git", "clean", "-fd"], cwd=wt)
    teardown = _teardown(repo_root, wt, branch)
    task_id = find_compatible_active_task(repo_root, actor_folder, row_id) or ""
    if task_id:
        _mark_task_abandoned(repo_root, actor_folder, task_id)
    return {"status": "cancelled", "task_id": task_id, **teardown}


def _teardown(repo_root: Path, wt: Path, branch: str) -> dict:
    _run(["git", "worktree", "remove", "--force", str(wt)], cwd=repo_root)
    _run(["git", "branch", "-D", branch], cwd=repo_root)
    return {"worktree_removed": str(wt), "branch_deleted": branch}


# ── Task-doc lifecycle ───────────────────────────────────────────────────

_INDEX_ACTIVE_SECTION_RE = re.compile(
    r"^##\s+Active\s*$(?P<body>.*?)(?=^##\s|\Z)",
    re.MULTILINE | re.DOTALL,
)
_INDEX_ROW_RE = re.compile(
    r"^\|\s*(?P<id>\d{3})\s*\|\s*(?P<title>[^|]+?)\s*\|\s*\[\d{3}\]\(\d{3}-[\w-]+\.md\)\s*\|\s*(?P<status>[^|]+?)\s*\|\s*(?P<summary>[^|]+?)\s*\|",
    re.MULTILINE,
)


def _kind_title_label(row_id: str) -> str:
    return f"Tracker draft {row_id}"


def find_compatible_active_task(repo_root: Path, actor_folder: str, row_id: str) -> str | None:
    """Scan the actor's task index for an Active session task matching this row."""
    _validate_row_id(row_id)
    idx = repo_root / "tasks" / actor_folder / "000-index.md"
    if not idx.is_file():
        return None
    text = idx.read_text(encoding="utf-8", errors="ignore")
    m = _INDEX_ACTIVE_SECTION_RE.search(text)
    if not m:
        return None
    body = m.group("body")
    label = _kind_title_label(row_id)
    title_re = re.compile(rf"^Console {re.escape(label)}\b", re.IGNORECASE)
    for row in _INDEX_ROW_RE.finditer(body):
        if row.group("status").strip().lower() == "complete":
            continue
        title = row.group("title").strip()
        if title_re.match(title):
            return row.group("id")
    return None


def next_task_id(repo_root: Path, actor_folder: str) -> str:
    folder = repo_root / "tasks" / actor_folder
    if not folder.is_dir():
        folder.mkdir(parents=True, exist_ok=True)
    existing = [int(p.name[:3]) for p in folder.glob("[0-9][0-9][0-9]-*.md")]
    return f"{(max(existing) + 1) if existing else 1:03d}"


def create_session_task(
    repo_root: Path, actor_folder: str, actor_name: str, row_id: str
) -> tuple[str, Path]:
    _validate_row_id(row_id)
    task_id = next_task_id(repo_root, actor_folder)
    slug = f"tracker-draft-{row_id}-{today()}"
    fname = f"{task_id}-{slug}.md"
    path = repo_root / "tasks" / actor_folder / fname
    label = _kind_title_label(row_id)
    title = f"Console {label} ({today()})"
    summary = (
        f"Auto-created session task backing a live B6 Create Draft workflow "
        f"for tracker row {row_id}. Worktree: "
        f"`.worktrees/workflow-tracker-draft-{row_id}-{today()}/` on branch "
        f"`workflow/tracker-draft-{row_id}-{today()}`. The agent proposes an "
        f"outline → user approves → agent synthesizes → user reviews → "
        f"Save & Commit ff-merges into main."
    )
    body = _render_task_body(task_id, title, actor_name, row_id, summary)
    path.write_text(body, encoding="utf-8")
    _insert_index_row(
        repo_root / "tasks" / actor_folder / "000-index.md",
        task_id, title, fname, summary,
    )
    return task_id, path


def _render_task_body(
    task_id: str, title: str, actor_name: str, row_id: str, summary: str
) -> str:
    return f"""# {task_id} — {title}

**ID**: {task_id}
**Created**: {today()}
**Status**: In Progress
**Created By**: project-console (workflows/tracker-draft)
**Owner**: {actor_name}
**Priority**: Medium

---

## PERMANENT RULES (do not remove)

1. Every stage transition (outline-proposed, outline-approved, draft-synthesized, saved/cancelled) is logged in this doc's Changelog.
2. On Save & Commit the console marks this task `Complete` and fast-forwards the worktree branch into main.
3. On Cancel the console flips this task to `Abandoned` and removes the worktree (the in-progress draft is discarded).
4. Do not edit the worktree files directly — use the console UI so the audit trail stays intact.

## Goals

{summary}

## Outline

_Will be populated when the agent proposes an outline._

## Final Draft Path

_Will be populated when Save & Commit relocates the draft from `_drafting/` to its eventual home._

## Changelog

- {today()} — Auto-created by project-console on first Create Draft click for row {row_id}.
"""


def _insert_index_row(
    index_path: Path, task_id: str, title: str, fname: str, summary: str
) -> None:
    if not index_path.is_file():
        return
    text = index_path.read_text(encoding="utf-8", errors="ignore")
    m = _INDEX_ACTIVE_SECTION_RE.search(text)
    if not m:
        return
    body_start, body_end = m.span("body")
    active = text[body_start:body_end]
    divider_m = re.search(r"^\|-[-|\s]+$\n", active, re.MULTILINE)
    if not divider_m:
        return
    insert_at = body_start + divider_m.end()
    new_row = (
        f"| {task_id} | {title} | [{task_id}]({fname}) | In Progress | "
        f"{summary} | Medium | {today()} |\n"
    )
    text = text[:insert_at] + new_row + text[insert_at:]
    index_path.write_text(text, encoding="utf-8")


def _mark_task_status(
    repo_root: Path, actor_folder: str, task_id: str, new_status: str
) -> None:
    task_folder = repo_root / "tasks" / actor_folder
    for p in task_folder.glob(f"{task_id}-*.md"):
        t = p.read_text(encoding="utf-8")
        t = re.sub(
            r"^\*\*Status\*\*:\s*.*$",
            f"**Status**: {new_status}",
            t, count=1, flags=re.MULTILINE,
        )
        p.write_text(t, encoding="utf-8")
    idx = task_folder / "000-index.md"
    if not idx.is_file():
        return
    text = idx.read_text(encoding="utf-8")
    row_re = re.compile(
        rf"^\|\s*{task_id}\s*\|.*\|\s*In Progress\s*\|.*$\n",
        re.MULTILINE,
    )
    m = row_re.search(text)
    if not m:
        return
    row = m.group(0).replace("In Progress", new_status)
    text = row_re.sub("", text, count=1)
    compl_m = re.search(r"^##\s+Completed\s*$", text, re.MULTILINE)
    if compl_m:
        after_header = text[compl_m.end():]
        div_m = re.search(r"^\|-[-|\s]+$\n", after_header, re.MULTILINE)
        if div_m:
            insert_at = compl_m.end() + div_m.end()
            text = text[:insert_at] + row + text[insert_at:]
    idx.write_text(text, encoding="utf-8")


def mark_task_complete(repo_root: Path, actor_folder: str, task_id: str) -> None:
    _mark_task_status(repo_root, actor_folder, task_id, "Complete")


def _mark_task_abandoned(repo_root: Path, actor_folder: str, task_id: str) -> None:
    _mark_task_status(repo_root, actor_folder, task_id, "Abandoned")


def append_changelog(task_path: Path, entry: str) -> None:
    """Append a row to the task doc's Changelog section. Caller writes the
    full bullet text minus the leading `- ` and date prefix."""
    if not task_path.is_file():
        return
    text = task_path.read_text(encoding="utf-8")
    line = f"- {today()} — {entry}\n"
    if "## Changelog" in text:
        text = text.rstrip() + "\n" + line
    else:
        text = text.rstrip() + "\n\n## Changelog\n\n" + line
    task_path.write_text(text, encoding="utf-8")


# ── Session resolution ──────────────────────────────────────────────────

def resolve_or_create(
    repo_root: Path, actor_folder: str, actor_name: str, row_id: str
) -> tuple[str, Path, Path]:
    """Return (task_id, task_path, worktree_path). Reuses a compatible
    active task if one exists; otherwise creates a new one. Idempotent on
    the worktree."""
    _validate_row_id(row_id)
    existing = find_compatible_active_task(repo_root, actor_folder, row_id)
    if existing:
        folder = repo_root / "tasks" / actor_folder
        cands = list(folder.glob(f"{existing}-*.md"))
        task_path = cands[0] if cands else folder / f"{existing}-unknown.md"
        task_id = existing
    else:
        task_id, task_path = create_session_task(repo_root, actor_folder, actor_name, row_id)
    wt = ensure_worktree(repo_root, row_id)
    return task_id, task_path, wt


def snapshot(repo_root: Path, actor_folder: str, row_id: str) -> DraftSession | None:
    """Return current session state, or None if no session exists."""
    _validate_row_id(row_id)
    wt = worktree_path(repo_root, row_id)
    if not (wt.is_dir() and (wt / ".git").exists()):
        return None
    existing = find_compatible_active_task(repo_root, actor_folder, row_id)
    if not existing:
        return None
    folder = repo_root / "tasks" / actor_folder
    cands = list(folder.glob(f"{existing}-*.md"))
    task_path = cands[0] if cands else folder / f"{existing}-unknown.md"
    staging = find_staging_file(wt, row_id)
    fm = _read_frontmatter(staging) if staging else {}
    agent = fm.get("agent") or {}
    target = fm.get("target") or {}
    return DraftSession(
        row_id=row_id,
        actor_folder=actor_folder,
        task_id=existing,
        task_path=str(task_path.relative_to(repo_root)),
        worktree_path=str(wt),
        branch=worktree_branch(repo_root, row_id),
        staging_file=str(staging.relative_to(wt)) if staging else None,
        has_outline=bool(agent.get("outline_approved_at") or staging is not None),
        has_synthesis=bool(agent.get("synthesis_completed_at")),
        target_path=target.get("path"),
    )


# ── Save & Commit ───────────────────────────────────────────────────────

def commit_and_merge(
    repo_root: Path, actor_folder: str, actor_name: str, row_id: str, message: str
) -> dict:
    """Stage + commit anything in the worktree, fast-forward main, push to
    origin, tear down worktree, mark task Complete. Mirrors the B4 pattern."""
    _validate_row_id(row_id)
    wt = worktree_path(repo_root, row_id)
    if not wt.is_dir():
        raise RuntimeError(f"no worktree to commit at {wt}")
    branch = worktree_branch(repo_root, row_id)

    _run(["git", "add", "-A"], cwd=wt)
    committed_new = False
    status = _run(["git", "status", "--porcelain"], cwd=wt)
    if status.stdout.strip():
        r = _run(
            [
                "git",
                "-c", f"user.name={actor_name}",
                "-c", f"user.email={actor_name.replace(' ', '.').lower()}@console.local",
                "commit", "-m", message,
            ],
            cwd=wt,
        )
        if r.returncode != 0:
            raise RuntimeError(f"git commit failed: {r.stderr.strip()}")
        committed_new = True

    ahead = _run(
        ["git", "rev-list", "--count", f"main..{branch}"], cwd=repo_root
    ).stdout.strip()
    if ahead == "0":
        cleanup = _teardown(repo_root, wt, branch)
        task_id = find_compatible_active_task(repo_root, actor_folder, row_id) or ""
        if task_id:
            mark_task_complete(repo_root, actor_folder, task_id)
        return {"committed": False, "reason": "branch has no commits ahead of main", **cleanup}

    commit_sha = _run(["git", "rev-parse", branch], cwd=repo_root).stdout.strip()

    auto_stashed = False
    r = _run(["git", "checkout", "main"], cwd=repo_root)
    if r.returncode != 0:
        raise RuntimeError(f"checkout main failed: {r.stderr.strip()}")
    r = _run(["git", "merge", "--ff-only", branch], cwd=repo_root)
    if r.returncode != 0 and "would be overwritten" in (r.stderr or ""):
        paths = _run(
            ["git", "diff", "--name-only", f"main..{branch}"], cwd=repo_root
        ).stdout.split()
        if paths:
            _run(
                ["git", "stash", "push", "-m",
                 f"auto-stash for tracker-draft merge {branch}", "--"] + paths,
                cwd=repo_root,
            )
            auto_stashed = True
            r = _run(["git", "merge", "--ff-only", branch], cwd=repo_root)
    if r.returncode != 0:
        raise RuntimeError(
            f"fast-forward merge failed: {r.stderr.strip()}. "
            f"Main has diverged — resolve manually: `cd {repo_root} && "
            f"git merge --no-ff {branch}` or rebase the branch."
        )

    pushed = False
    r = _run(["git", "push", "origin", "main"], cwd=repo_root)
    if r.returncode == 0:
        pushed = True

    cleanup = _teardown(repo_root, wt, branch)
    task_id = find_compatible_active_task(repo_root, actor_folder, row_id) or ""
    if task_id:
        mark_task_complete(repo_root, actor_folder, task_id)
    return {
        "committed": True,
        "committed_new": committed_new,
        "commit_sha": commit_sha,
        "pushed": pushed,
        "branch_merged": branch,
        "auto_stashed_main_changes": auto_stashed,
        **cleanup,
    }
