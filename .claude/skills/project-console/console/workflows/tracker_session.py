"""Tracker workflow session — backing task doc + git worktree per (actor, kind).

Mirrors `b3_session.py` for the two new tracker workflows from task ben/154:

  * kind="status" — interactive status updates (B4). Worktree at
    `.worktrees/workflow-tracker-status-<YYYY-MM-DD>/` on branch
    `workflow/tracker-status-<YYYY-MM-DD>`. Backing task at
    `tasks/<actor>/NNN-tracker-status-update-<YYYY-MM-DD>.md`.

  * kind="advisor" — Ask the Advisor (B5). Worktree at
    `.worktrees/workflow-tracker-advisor-<YYYY-MM-DD>/` on branch
    `workflow/tracker-advisor-<YYYY-MM-DD>`. Backing task at
    `tasks/<actor>/NNN-tracker-advisor-<YYYY-MM-DD>.md`.

Per task ben/154 D5: single workflow per (actor, kind) at a time.
Per task ben/154 D4: date-based worktree naming, with date-rollover
handling lifted from b3_session.py (`_existing_worktree_dir` walks any
date suffix for the given kind before generating today's name).
"""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

# Files inside the worktree that the workflow may mutate. The status workflow
# writes submission-tracker.md + regenerates submission-tracker.html and
# updates submission-tracker.human.json sidecar overlays. Keep this list
# narrow so the dirty-check is precise.
TRACKER_MD_REL = "docs/project/submissions/submission-tracker.md"
TRACKER_HTML_REL = "docs/project/submissions/submission-tracker.html"
TRACKER_HUMAN_SIDECAR_REL = "docs/project/submissions/submission-tracker.human.json"

VALID_KINDS = ("status", "advisor")


@dataclass(frozen=True)
class Session:
    kind: str               # "status" | "advisor"
    actor_folder: str
    task_id: str
    task_path: str          # repo-relative, canonical (main-branch)
    worktree_path: str      # absolute
    branch: str
    has_diff: bool
    diff_summary: list[str] # `STATUS path` lines from `git status --porcelain`


def today() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _run(args: list[str], cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(args, cwd=str(cwd), capture_output=True, text=True, timeout=30)


def _validate_kind(kind: str) -> None:
    if kind not in VALID_KINDS:
        raise ValueError(f"invalid tracker workflow kind {kind!r}; expected one of {VALID_KINDS}")


# ── Worktree management ──────────────────────────────────────────────────

def _existing_worktree_dir(repo_root: Path, kind: str) -> Path | None:
    """Discover an existing per-kind worktree dir under `.worktrees/`,
    regardless of date suffix. Returns the most recently modified match,
    or None if no worktree for this kind exists. Lifted from b3_session
    to handle the date-rollover bug the same way."""
    base = repo_root / ".worktrees"
    if not base.is_dir():
        return None
    candidates = sorted(
        (p for p in base.glob(f"workflow-tracker-{kind}-*") if p.is_dir() and (p / ".git").exists()),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return candidates[0] if candidates else None


def _existing_worktree_branch(wt: Path) -> str | None:
    r = _run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=wt)
    if r.returncode != 0:
        return None
    return (r.stdout or "").strip() or None


def worktree_branch(repo_root: Path, kind: str) -> str:
    """Return the branch for the per-kind worktree. Reuses an existing
    session's branch if present (date-rollover safe); otherwise mints a
    fresh today-named branch."""
    _validate_kind(kind)
    wt = _existing_worktree_dir(repo_root, kind)
    if wt is not None:
        existing = _existing_worktree_branch(wt)
        if existing:
            return existing
    return f"workflow/tracker-{kind}-{today()}"


def worktree_path(repo_root: Path, kind: str) -> Path:
    """Return the path to the per-kind worktree. Prefers an existing
    worktree (any date suffix); falls back to today's freshly-named path."""
    _validate_kind(kind)
    existing = _existing_worktree_dir(repo_root, kind)
    if existing is not None:
        return existing
    return repo_root / ".worktrees" / f"workflow-tracker-{kind}-{today()}"


def ensure_worktree(repo_root: Path, kind: str) -> Path:
    """Open (or reuse) the per-kind worktree. Idempotent.

    After creation/reuse, syncs the submission-tracker.md + sidecar from
    main's WORKING TREE (not just HEAD) into the worktree. This handles
    the case where main has uncommitted tracker edits — without this sync
    the worktree would only see the last committed version and the user's
    in-flight changes would be invisible to the workflow."""
    _validate_kind(kind)
    wt = worktree_path(repo_root, kind)
    branch = worktree_branch(repo_root, kind)
    if not (wt.is_dir() and (wt / ".git").exists()):
        wt.parent.mkdir(parents=True, exist_ok=True)
        r = _run(["git", "worktree", "add", "-B", branch, str(wt)], cwd=repo_root)
        if r.returncode != 0:
            raise RuntimeError(f"git worktree add failed: {r.stderr.strip()}")
    # Sync uncommitted submission-tracker files from main into the worktree.
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
    return wt


def worktree_diff_summary(wt: Path) -> list[str]:
    r = _run(["git", "status", "--porcelain"], cwd=wt)
    if r.returncode != 0:
        return []
    return [ln for ln in r.stdout.splitlines() if ln.strip()]


def worktree_tracker_md_dirty(wt: Path) -> bool:
    """True iff submission-tracker.md has uncommitted changes inside the
    worktree. Used as a pre-check by the Save & Commit path."""
    r = _run(["git", "status", "--porcelain", "--", TRACKER_MD_REL], cwd=wt)
    return bool((r.stdout or "").strip())


def worktree_discard_all(wt: Path) -> dict:
    """Discard ALL pending changes in the worktree. Worktree, branch, and
    backing task are LEFT IN PLACE so the user can resume. Use
    `cancel_workflow()` to fully tear down."""
    co = _run(["git", "checkout", "HEAD", "--", "."], cwd=wt)
    cl = _run(["git", "clean", "-fd"], cwd=wt)
    if co.returncode != 0 and cl.returncode != 0:
        return {
            "status": "error",
            "checkout_err": co.stderr.strip(),
            "clean_err": cl.stderr.strip(),
        }
    return {"status": "discarded_all", "checkout_rc": co.returncode, "clean_rc": cl.returncode}


def cancel_workflow(repo_root: Path, actor_folder: str, kind: str) -> dict:
    """Tear down the entire workflow session for `(actor, kind)`: discard
    pending diff, remove the worktree, delete the branch, mark the backing
    task Abandoned. Idempotent — returns noop if no session exists."""
    _validate_kind(kind)
    wt = worktree_path(repo_root, kind)
    branch = worktree_branch(repo_root, kind)
    if not (wt.is_dir() and (wt / ".git").exists()):
        return {"status": "noop", "reason": "no open worktree"}
    _run(["git", "checkout", "HEAD", "--", "."], cwd=wt)
    _run(["git", "clean", "-fd"], cwd=wt)
    teardown = _teardown(repo_root, wt, branch)
    task_id = find_compatible_active_task(repo_root, actor_folder, kind) or ""
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


def _kind_title_label(kind: str) -> str:
    return {"status": "Tracker status update", "advisor": "Tracker advisor consultation"}[kind]


def _kind_slug(kind: str) -> str:
    return {"status": "tracker-status-update", "advisor": "tracker-advisor"}[kind]


def find_compatible_active_task(repo_root: Path, actor_folder: str, kind: str) -> str | None:
    """Scan `tasks/<actor>/000-index.md` Active section for a session task
    matching this (kind). Returns the 3-digit task ID or None.

    Strict prefix match against the `_kind_title_label` so unrelated tasks
    that mention "tracker" don't bind by accident."""
    _validate_kind(kind)
    idx = repo_root / "tasks" / actor_folder / "000-index.md"
    if not idx.is_file():
        return None
    text = idx.read_text(encoding="utf-8", errors="ignore")
    m = _INDEX_ACTIVE_SECTION_RE.search(text)
    if not m:
        return None
    body = m.group("body")
    label = _kind_title_label(kind)
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
    repo_root: Path, actor_folder: str, actor_name: str, kind: str
) -> tuple[str, Path]:
    """Create a new task doc backing this tracker workflow session and add
    an index row. Returns (task_id, task_file_path)."""
    _validate_kind(kind)
    task_id = next_task_id(repo_root, actor_folder)
    slug = f"{_kind_slug(kind)}-{today()}"
    fname = f"{task_id}-{slug}.md"
    path = repo_root / "tasks" / actor_folder / fname
    label = _kind_title_label(kind)
    title = f"Console {label} ({today()})"
    summary = (
        f"Auto-created session task backing a live tracker workflow "
        f"({kind}) via the project-console. Worktree: "
        f"`.worktrees/workflow-tracker-{kind}-{today()}/` on branch "
        f"`workflow/tracker-{kind}-{today()}`. "
        + (
            "Status changes accumulate in the worktree; Save & Commit "
            "writes submission-tracker.md, regenerates the HTML, "
            "fast-forwards main, and closes the task."
            if kind == "status"
            else "Conversation transcript accumulates in the changelog; "
            "Save & Close persists the Q&A into the task doc and closes "
            "the workflow."
        )
    )
    body = _render_task_body(task_id, title, actor_name, kind, summary)
    path.write_text(body, encoding="utf-8")
    _insert_index_row(
        repo_root / "tasks" / actor_folder / "000-index.md",
        task_id, title, fname, summary,
    )
    return task_id, path


def _render_task_body(
    task_id: str, title: str, actor_name: str, kind: str, summary: str
) -> str:
    actions_section = (
        "## Goals\n\n"
        f"{summary}\n\n"
        "## Todos\n\n"
        + (
            "- [ ] Click status badges in the dashboard, accumulate pending changes.\n"
            "- [ ] Save & Commit when ready (button in the console).\n"
            "- [ ] Or Cancel to discard pending changes.\n"
            if kind == "status"
            else "- [ ] Pick advisor; ask questions; iterate.\n"
            "- [ ] Save & Close when done — transcript persists into this task doc.\n"
            "- [ ] Or Cancel to discard the conversation.\n"
        )
    )
    return f"""# {task_id} — {title}

**ID**: {task_id}
**Created**: {today()}
**Status**: In Progress
**Created By**: project-console (workflows/tracker-{kind})
**Owner**: {actor_name}
**Priority**: Medium

---

## PERMANENT RULES (do not remove)

1. Every status change / advisor turn is logged to this doc's Changelog and to the worktree's git history.
2. On Save & Commit (status) or Save & Close (advisor) the console marks this task `Complete` and fast-forwards the worktree branch into main.
3. On Cancel the console flips this task to `Abandoned` and removes the worktree.
4. Do not edit the worktree files directly — use the console UI so the audit trail stays intact.

{actions_section}
## Changelog

- {today()} — Auto-created by project-console on first action in the tracker-{kind} workflow.
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
    """Flip task doc Status and move its index row from Active → Completed.
    Used for both Complete (Save) and Abandoned (Cancel)."""
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


# ── Session resolution ──────────────────────────────────────────────────

def resolve_or_create(
    repo_root: Path, actor_folder: str, actor_name: str, kind: str
) -> tuple[str, Path, Path]:
    """Return (task_id, task_path, worktree_path). Reuses a compatible
    active task if one exists; otherwise creates a new one. Idempotent on
    the worktree."""
    _validate_kind(kind)
    existing = find_compatible_active_task(repo_root, actor_folder, kind)
    if existing:
        folder = repo_root / "tasks" / actor_folder
        cands = list(folder.glob(f"{existing}-*.md"))
        task_path = cands[0] if cands else folder / f"{existing}-unknown.md"
        task_id = existing
    else:
        task_id, task_path = create_session_task(repo_root, actor_folder, actor_name, kind)
    wt = ensure_worktree(repo_root, kind)
    return task_id, task_path, wt


def snapshot(repo_root: Path, actor_folder: str, kind: str) -> Session | None:
    """Return the current session state for (actor, kind) if one exists,
    else None. Does not create anything."""
    _validate_kind(kind)
    wt = worktree_path(repo_root, kind)
    if not (wt.is_dir() and (wt / ".git").exists()):
        return None
    diff = worktree_diff_summary(wt)
    existing = find_compatible_active_task(repo_root, actor_folder, kind)
    if not existing:
        return None
    folder = repo_root / "tasks" / actor_folder
    cands = list(folder.glob(f"{existing}-*.md"))
    task_path = cands[0] if cands else folder / f"{existing}-unknown.md"
    return Session(
        kind=kind,
        actor_folder=actor_folder,
        task_id=existing,
        task_path=str(task_path.relative_to(repo_root)),
        worktree_path=str(wt),
        branch=worktree_branch(repo_root, kind),
        has_diff=bool(diff),
        diff_summary=diff,
    )


# ── Commit & merge ───────────────────────────────────────────────────────

def commit_and_merge(
    repo_root: Path, actor_folder: str, actor_name: str, kind: str, message: str
) -> dict:
    """Stage + commit anything in the worktree, fast-forward main, push to
    origin, tear down worktree, mark task Complete. Mirrors the b3 flow.
    No-PR per the project's push-direct policy."""
    _validate_kind(kind)
    wt = worktree_path(repo_root, kind)
    if not wt.is_dir():
        raise RuntimeError(f"no worktree to commit at {wt}")
    branch = worktree_branch(repo_root, kind)

    # 1. Stage + commit anything uncommitted in the worktree.
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

    # 2. If branch isn't ahead of main, nothing to merge.
    ahead = _run(
        ["git", "rev-list", "--count", f"main..{branch}"], cwd=repo_root
    ).stdout.strip()
    if ahead == "0":
        cleanup = _teardown(repo_root, wt, branch)
        task_id = find_compatible_active_task(repo_root, actor_folder, kind) or ""
        if task_id:
            mark_task_complete(repo_root, actor_folder, task_id)
        return {"committed": False, "reason": "branch has no commits ahead of main", **cleanup}

    commit_sha = _run(["git", "rev-parse", branch], cwd=repo_root).stdout.strip()

    # 3. Fast-forward merge into main; auto-stash conflicting unstaged paths.
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
                 f"auto-stash for tracker workflow merge {branch}", "--"] + paths,
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

    # 4. Push (best-effort).
    pushed = False
    r = _run(["git", "push", "origin", "main"], cwd=repo_root)
    if r.returncode == 0:
        pushed = True

    # 5. Teardown + close task.
    cleanup = _teardown(repo_root, wt, branch)
    task_id = find_compatible_active_task(repo_root, actor_folder, kind) or ""
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
