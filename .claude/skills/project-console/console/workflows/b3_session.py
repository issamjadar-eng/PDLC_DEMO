"""B3 review session — backing task doc + git worktree per domain.

Every live mutation from B3 runs inside a dedicated git worktree under
`.worktrees/workflow-strategy-<domain>-<YYYY-MM-DD>/` on branch
`workflow/strategy-<domain>-<YYYY-MM-DD>`. A companion task doc lives in
the actor's `tasks/<actor-folder>/` — either an existing compatible active
task is reused, or a new one is created. Commit & Merge pushes the branch
changes to main and closes out the task + worktree.
"""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass(frozen=True)
class Session:
    domain: str
    actor_folder: str
    task_id: str
    task_path: str          # repo-relative, canonical (main-branch)
    worktree_path: str      # absolute
    branch: str
    has_diff: bool
    diff_summary: list[str] # list of `STATUS path` strings from `git status --porcelain`


def today() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _run(args: list[str], cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(args, cwd=str(cwd), capture_output=True, text=True, timeout=30)


# ── Worktree management ──────────────────────────────────────────────────

def worktree_branch(domain: str) -> str:
    return f"workflow/strategy-{domain}-{today()}"


def worktree_path(repo_root: Path, domain: str) -> Path:
    return repo_root / ".worktrees" / f"workflow-strategy-{domain}-{today()}"


def ensure_worktree(repo_root: Path, domain: str) -> Path:
    """Open (or reuse) the per-domain worktree. Idempotent.

    After creation/reuse, also syncs main's WORKING-TREE state for the
    `docs/project/strategies/` directory into the worktree. This handles
    the case where main has uncommitted strategy-doc changes (e.g. fresh
    decision-block migration) — without this sync, the worktree would
    only see the last committed version and per-decision lookups (by
    `D-DOMAIN-N.M` id) would fail."""
    wt = worktree_path(repo_root, domain)
    branch = worktree_branch(domain)
    if not (wt.is_dir() and (wt / ".git").exists()):
        wt.parent.mkdir(parents=True, exist_ok=True)
        r = _run(["git", "worktree", "add", "-B", branch, str(wt)], cwd=repo_root)
        if r.returncode != 0:
            raise RuntimeError(f"git worktree add failed: {r.stderr.strip()}")
    # Sync uncommitted strategy-doc changes from main into the worktree.
    import shutil
    src_dir = repo_root / "docs/project/strategies"
    dst_dir = wt / "docs/project/strategies"
    if src_dir.is_dir():
        dst_dir.mkdir(parents=True, exist_ok=True)
        for src in src_dir.glob("*-strategy.md"):
            dst = dst_dir / src.name
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


def worktree_file_diff(wt: Path, rel_path: str) -> str:
    """Return the unified diff for a single file inside the worktree (vs.
    HEAD). Empty string on miss / not modified."""
    r = _run(["git", "diff", "--no-color", "--", rel_path], cwd=wt)
    if r.returncode != 0:
        return ""
    return r.stdout


def worktree_file_versions(wt: Path, rel_path: str) -> tuple[str, str]:
    """Return `(before, after)` — the file's HEAD content and current
    working-tree content inside the worktree. Either may be empty if the
    file is new/deleted."""
    head = _run(["git", "show", f"HEAD:{rel_path}"], cwd=wt)
    before = head.stdout if head.returncode == 0 else ""
    after_path = wt / rel_path
    try:
        after = after_path.read_text(encoding="utf-8") if after_path.exists() else ""
    except OSError:
        after = ""
    return before, after


def friendly_file_diff_html(wt: Path, rel_path: str) -> str:
    """Render a non-technical diff view: line-by-line table with green
    'added' / red 'removed' / grey 'unchanged' rows, line numbers in two
    columns, no `+`/`-` gutters or `@@` headers. Suitable for regulatory
    reviewers who shouldn't see git's raw output."""
    import difflib
    import html as _html
    before, after = worktree_file_versions(wt, rel_path)
    if not before and not after:
        return '<p class="muted">No content to compare.</p>'
    b_lines = before.splitlines()
    a_lines = after.splitlines()
    sm = difflib.SequenceMatcher(None, b_lines, a_lines)
    parts: list[str] = [
        '<table class="friendly-diff">',
        '<thead><tr>'
        '<th class="ln-col" title="Line number in the saved version">Saved</th>'
        '<th class="ln-col" title="Line number in your draft">Draft</th>'
        '<th>Content</th>'
        '</tr></thead><tbody>',
    ]
    bn = an = 0
    added = removed = unchanged = 0
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            for k in range(i1, i2):
                bn += 1
                an += 1
                unchanged += 1
                parts.append(
                    f'<tr class="diff-context">'
                    f'<td class="ln">{bn}</td><td class="ln">{an}</td>'
                    f'<td class="content">{_html.escape(b_lines[k])}</td></tr>'
                )
        elif tag == "delete":
            for k in range(i1, i2):
                bn += 1
                removed += 1
                parts.append(
                    f'<tr class="diff-removed">'
                    f'<td class="ln">{bn}</td><td class="ln"></td>'
                    f'<td class="content"><span class="badge-rm">removed</span> '
                    f'{_html.escape(b_lines[k])}</td></tr>'
                )
        elif tag == "insert":
            for k in range(j1, j2):
                an += 1
                added += 1
                parts.append(
                    f'<tr class="diff-added">'
                    f'<td class="ln"></td><td class="ln">{an}</td>'
                    f'<td class="content"><span class="badge-add">added</span> '
                    f'{_html.escape(a_lines[k])}</td></tr>'
                )
        elif tag == "replace":
            for k in range(i1, i2):
                bn += 1
                removed += 1
                parts.append(
                    f'<tr class="diff-removed">'
                    f'<td class="ln">{bn}</td><td class="ln"></td>'
                    f'<td class="content"><span class="badge-rm">removed</span> '
                    f'{_html.escape(b_lines[k])}</td></tr>'
                )
            for k in range(j1, j2):
                an += 1
                added += 1
                parts.append(
                    f'<tr class="diff-added">'
                    f'<td class="ln"></td><td class="ln">{an}</td>'
                    f'<td class="content"><span class="badge-add">added</span> '
                    f'{_html.escape(a_lines[k])}</td></tr>'
                )
    parts.append("</tbody></table>")
    summary = (
        f'<p class="diff-summary">'
        f'<strong>{added}</strong> line(s) added · '
        f'<strong>{removed}</strong> line(s) removed · '
        f'<strong>{unchanged}</strong> unchanged'
        f'</p>'
    )
    return summary + "".join(parts)


def worktree_discard(wt: Path, rel_path: str) -> dict:
    """Discard a single file's changes in the worktree (`git checkout --
    <path>` for tracked files; `rm` for untracked). Returns a small
    diagnostic dict."""
    # Distinguish untracked vs modified.
    status = _run(["git", "status", "--porcelain", "--", rel_path], cwd=wt)
    line = (status.stdout or "").strip()
    if not line:
        return {"status": "noop", "reason": "no pending change for path"}
    code = line[:2]
    if code.startswith("??"):
        # Untracked — remove it.
        target = wt / rel_path
        try:
            if target.is_file():
                target.unlink()
            return {"status": "removed_untracked", "path": rel_path}
        except OSError as e:
            return {"status": "error", "reason": str(e)}
    # Tracked — checkout HEAD.
    r = _run(["git", "checkout", "HEAD", "--", rel_path], cwd=wt)
    if r.returncode != 0:
        return {"status": "error", "reason": r.stderr.strip()}
    return {"status": "discarded", "path": rel_path}


# ── Task-doc lifecycle ───────────────────────────────────────────────────

_INDEX_ACTIVE_SECTION_RE = re.compile(
    r"^##\s+Active\s*$(?P<body>.*?)(?=^##\s|\Z)",
    re.MULTILINE | re.DOTALL,
)
_INDEX_ROW_RE = re.compile(
    r"^\|\s*(?P<id>\d{3})\s*\|\s*(?P<title>[^|]+?)\s*\|\s*\[\d{3}\]\(\d{3}-[\w-]+\.md\)\s*\|\s*(?P<status>[^|]+?)\s*\|\s*(?P<summary>[^|]+?)\s*\|",
    re.MULTILINE,
)


def find_compatible_active_task(
    repo_root: Path, actor_folder: str, domain: str
) -> str | None:
    """Scan `tasks/<actor>/000-index.md` Active section for a task whose
    title/summary matches the strategy-reassembly topic for this domain.
    Returns the 3-digit task ID or None."""
    idx = repo_root / "tasks" / actor_folder / "000-index.md"
    if not idx.is_file():
        return None
    text = idx.read_text(encoding="utf-8", errors="ignore")
    m = _INDEX_ACTIVE_SECTION_RE.search(text)
    if not m:
        return None
    body = m.group("body")
    # Heuristic match: title OR summary contains "strategy" AND ("reassembly"
    # OR "re-assembly" OR "re-assemble") AND the domain slug. Status != Complete.
    patt = re.compile(
        rf"(?i)\bstrategy\b.*(?:re-?assembl|workflow).*\b{re.escape(domain)}\b"
        rf"|\b{re.escape(domain)}\b.*(?:re-?assembl|workflow).*\bstrategy\b"
    )
    for row in _INDEX_ROW_RE.finditer(body):
        if row.group("status").strip().lower() == "complete":
            continue
        hay = f"{row.group('title')} {row.group('summary')}"
        if patt.search(hay):
            return row.group("id")
    return None


def next_task_id(repo_root: Path, actor_folder: str) -> str:
    folder = repo_root / "tasks" / actor_folder
    if not folder.is_dir():
        folder.mkdir(parents=True, exist_ok=True)
    existing = [int(p.name[:3]) for p in folder.glob("[0-9][0-9][0-9]-*.md")]
    return f"{(max(existing) + 1) if existing else 1:03d}"


def create_session_task(
    repo_root: Path, actor_folder: str, actor_name: str, domain: str
) -> tuple[str, Path]:
    """Create a new task doc for this console strategy-reassembly session
    and add an index row. Returns (task_id, task_file_path)."""
    task_id = next_task_id(repo_root, actor_folder)
    slug = f"console-strategy-reassembly-{domain}-{today()}"
    fname = f"{task_id}-{slug}.md"
    path = repo_root / "tasks" / actor_folder / fname
    title = f"Console strategy re-assembly — {domain} ({today()})"
    summary = (
        f"Auto-created session task backing a live re-assembly of "
        f"{domain}-strategy.md via the project-console /workflows/strategy-reassembly "
        f"page. Worktree: `.worktrees/workflow-strategy-{domain}-{today()}/` "
        f"on branch `workflow/strategy-{domain}-{today()}`. Mutations "
        f"(Accept / Reject / Modify / Re-Assemble) land in the worktree; "
        f"Commit & Merge closes the task and fast-forwards main."
    )
    body = _render_task_body(task_id, title, actor_name, domain, summary)
    path.write_text(body, encoding="utf-8")
    _insert_index_row(
        repo_root / "tasks" / actor_folder / "000-index.md",
        task_id,
        title,
        fname,
        summary,
    )
    return task_id, path


def _render_task_body(
    task_id: str, title: str, actor_name: str, domain: str, summary: str
) -> str:
    return f"""# {task_id} — {title}

**ID**: {task_id}
**Created**: {today()}
**Status**: In Progress
**Created By**: project-console (workflows/strategy-reassembly)
**Owner**: {actor_name}
**Priority**: Medium

---

## PERMANENT RULES (do not remove)

1. Update this doc as actions are taken in the console workflow.
2. Every Accept / Reject / Modify / Re-Assemble in the console is logged both here and in the strategy doc's `## History` section.
3. On Commit & Merge the console marks this task `Complete` and fast-forwards the worktree branch into main.
4. If you abandon the session, delete the worktree at `.worktrees/workflow-strategy-{domain}-{today()}/` and mark this task `Abandoned`.

## Goals

{summary}

## Todos

- [ ] Review pending proposals surfaced by re-assembly.
- [ ] Accept / Reject / Modify each as appropriate.
- [ ] Commit & Merge when done (button in the console).

## Changelog

- {today()} — Auto-created by project-console on first Execute in the strategy-reassembly workflow.
"""


def _insert_index_row(
    index_path: Path, task_id: str, title: str, fname: str, summary: str
) -> None:
    """Insert a new row at the top of the Active section."""
    if not index_path.is_file():
        return
    text = index_path.read_text(encoding="utf-8", errors="ignore")
    m = _INDEX_ACTIVE_SECTION_RE.search(text)
    if not m:
        return
    # Find the first data row in the Active section (the header divider line
    # starts with `|----`; rows come after it). Insert our row immediately
    # after the divider.
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


def mark_task_complete(repo_root: Path, actor_folder: str, task_id: str) -> None:
    """Flip the task doc Status to Complete + move its index row from Active
    to Completed. Best-effort; skips silently if the index row isn't found."""
    task_folder = repo_root / "tasks" / actor_folder
    for p in task_folder.glob(f"{task_id}-*.md"):
        t = p.read_text(encoding="utf-8")
        t = re.sub(
            r"^\*\*Status\*\*:\s*.*$",
            "**Status**: Complete",
            t,
            count=1,
            flags=re.MULTILINE,
        )
        p.write_text(t, encoding="utf-8")
    idx = task_folder / "000-index.md"
    if not idx.is_file():
        return
    text = idx.read_text(encoding="utf-8")
    # Match a row with our task_id in the Active section.
    row_re = re.compile(
        rf"^\|\s*{task_id}\s*\|.*\|\s*In Progress\s*\|.*$\n",
        re.MULTILINE,
    )
    m = row_re.search(text)
    if not m:
        return
    row = m.group(0).replace("In Progress", "Complete")
    text = row_re.sub("", text, count=1)
    # Insert under Completed section divider.
    compl_m = re.search(r"^##\s+Completed\s*$", text, re.MULTILINE)
    if compl_m:
        # Find the divider line under Completed's table header.
        after_header = text[compl_m.end():]
        div_m = re.search(r"^\|-[-|\s]+$\n", after_header, re.MULTILINE)
        if div_m:
            insert_at = compl_m.end() + div_m.end()
            text = text[:insert_at] + row + text[insert_at:]
    idx.write_text(text, encoding="utf-8")


# ── Session resolution ──────────────────────────────────────────────────

def resolve_or_create(
    repo_root: Path, actor_folder: str, actor_name: str, domain: str
) -> tuple[str, Path, Path]:
    """Return (task_id, task_path, worktree_path). Reuses a compatible
    active task if one exists; otherwise creates a new one. Idempotent on
    the worktree (reuses existing)."""
    existing = find_compatible_active_task(repo_root, actor_folder, domain)
    if existing:
        # Locate the file path for the existing task.
        folder = repo_root / "tasks" / actor_folder
        cands = list(folder.glob(f"{existing}-*.md"))
        task_path = cands[0] if cands else folder / f"{existing}-unknown.md"
        task_id = existing
    else:
        task_id, task_path = create_session_task(repo_root, actor_folder, actor_name, domain)
    wt = ensure_worktree(repo_root, domain)
    return task_id, task_path, wt


def snapshot(repo_root: Path, actor_folder: str, domain: str) -> Session | None:
    """Return the current session state for this (actor, domain) if one
    exists, else None. Does not create anything."""
    wt = worktree_path(repo_root, domain)
    if not (wt.is_dir() and (wt / ".git").exists()):
        return None
    diff = worktree_diff_summary(wt)
    existing = find_compatible_active_task(repo_root, actor_folder, domain)
    if not existing:
        return None
    folder = repo_root / "tasks" / actor_folder
    cands = list(folder.glob(f"{existing}-*.md"))
    task_path = cands[0] if cands else folder / f"{existing}-unknown.md"
    return Session(
        domain=domain,
        actor_folder=actor_folder,
        task_id=existing,
        task_path=str(task_path.relative_to(repo_root)),
        worktree_path=str(wt),
        branch=worktree_branch(domain),
        has_diff=bool(diff),
        diff_summary=diff,
    )


# ── Commit & merge ───────────────────────────────────────────────────────

def commit_and_merge(
    repo_root: Path, actor_folder: str, actor_name: str, domain: str, message: str
) -> dict:
    """Inside the worktree: git add -A + commit + checkout main in the
    primary repo and merge the worktree branch fast-forward; push to origin
    if configured; remove the worktree; mark the task Complete. No-PR path
    per the project's push/merge-direct policy."""
    wt = worktree_path(repo_root, domain)
    if not wt.is_dir():
        raise RuntimeError(f"no worktree to commit at {wt}")
    branch = worktree_branch(domain)

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

    # 2. Check branch is ahead of main. If equal, nothing to merge.
    ahead = _run(
        ["git", "rev-list", "--count", f"main..{branch}"], cwd=repo_root
    ).stdout.strip()
    if ahead == "0":
        cleanup = _teardown(repo_root, wt, branch)
        return {"committed": False, "reason": "branch has no commits ahead of main", **cleanup}

    commit_sha = _run(["git", "rev-parse", branch], cwd=repo_root).stdout.strip()

    # 3. Merge fast-forward into main. If main has conflicting unstaged
    # changes on the same paths the branch touches, auto-stash them out of
    # the way (the branch's version is the authoritative post-review state).
    auto_stashed = False
    r = _run(["git", "checkout", "main"], cwd=repo_root)
    if r.returncode != 0:
        raise RuntimeError(f"checkout main failed: {r.stderr.strip()}")

    # Attempt FF. If it fails due to conflicting unstaged paths, stash + retry.
    r = _run(["git", "merge", "--ff-only", branch], cwd=repo_root)
    if r.returncode != 0 and "would be overwritten" in (r.stderr or ""):
        # Stash only the paths the branch touches, then retry.
        paths = _run(
            ["git", "diff", "--name-only", f"main..{branch}"], cwd=repo_root
        ).stdout.split()
        if paths:
            _run(
                ["git", "stash", "push", "-m",
                 f"auto-stash for workflow merge {branch}", "--"] + paths,
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

    # 5. Push (best-effort).
    pushed = False
    r = _run(["git", "push", "origin", "main"], cwd=repo_root)
    if r.returncode == 0:
        pushed = True

    # 6. Cleanup worktree + branch + mark task complete.
    cleanup = _teardown(repo_root, wt, branch)
    mark_task_complete(repo_root, actor_folder, find_compatible_active_task(
        repo_root, actor_folder, domain
    ) or "")
    return {
        "committed": True,
        "committed_new": committed_new,
        "commit_sha": commit_sha,
        "pushed": pushed,
        "branch_merged": branch,
        "auto_stashed_main_changes": auto_stashed,
        **cleanup,
    }


def _teardown(repo_root: Path, wt: Path, branch: str) -> dict:
    """Remove the worktree + delete the branch. Best-effort."""
    _run(["git", "worktree", "remove", "--force", str(wt)], cwd=repo_root)
    _run(["git", "branch", "-D", branch], cwd=repo_root)
    return {"worktree_removed": str(wt), "branch_deleted": branch}
