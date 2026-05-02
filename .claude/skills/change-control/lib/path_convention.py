"""Drive path convention for the internal-review tier.

Derives the canonical Google Drive folder + filename for an md file:

    AI_PDLC/<project.name>/<task_folder>/<doc-name>

where:
    project.name  — read from project.yml
    task_folder   — read from project.yml team.active[*] matched against
                    `git config user.name` (Q9, locked 2026-04-27)
    doc-name      — repo path with separators replaced by underscores,
                    .md extension dropped (Q2, locked 2026-04-27)
"""
from __future__ import annotations

import re
import subprocess
from functools import lru_cache
from pathlib import Path
from typing import Iterable

import yaml


PROJECT_YML_RELATIVE = "project.yml"
AI_PDLC_PREFIX = "AI_PDLC"


def project_root() -> Path:
    """Return the consuming project's root by walking up from cwd looking
    for project.yml."""
    cur = Path.cwd().resolve()
    for parent in [cur] + list(cur.parents):
        if (parent / PROJECT_YML_RELATIVE).is_file():
            return parent
    raise RuntimeError(
        "could not locate project.yml — run change-control from inside the "
        "project tree"
    )


@lru_cache(maxsize=1)
def _project_yml() -> dict:
    with (project_root() / PROJECT_YML_RELATIVE).open() as f:
        return yaml.safe_load(f)


def project_name() -> str:
    name = _project_yml().get("project", {}).get("name")
    if not name:
        raise RuntimeError("project.yml: project.name is missing")
    return name


def team_active() -> list[dict]:
    return _project_yml().get("team", {}).get("active", []) or []


def git_user_name() -> str | None:
    """Return `git config user.name` or None if unset."""
    try:
        out = subprocess.check_output(
            ["git", "config", "--get", "user.name"],
            stderr=subprocess.DEVNULL,
            cwd=project_root(),
        )
        return out.decode().strip() or None
    except subprocess.CalledProcessError:
        return None


def resolve_current_user_task_folder() -> str:
    """Resolve the current user's task_folder slug.

    Strategy (Q9, locked):
      1. Read git config user.name
      2. Match against team.active[*].name
      3. Return the matching row's task_folder
      4. If no match or no git name, raise — the action prompts the user
         to pick from the roster (handled at action layer, not here).
    """
    name = git_user_name()
    if not name:
        raise RuntimeError(
            "git config user.name is not set. Set it with: "
            "git config --global user.name \"Your Full Name\""
        )
    for member in team_active():
        if member.get("name") == name:
            tf = member.get("task_folder")
            if not tf:
                raise RuntimeError(
                    f"team.active row for {name!r} has no task_folder"
                )
            return tf
    roster = ", ".join(m.get("name", "?") for m in team_active())
    raise RuntimeError(
        f"git user.name {name!r} does not match any team.active member. "
        f"Active members: {roster}"
    )


def doc_name_from_repo_path(rel_path: str | Path) -> str:
    """Convert a repo-relative md path to a Drive-safe doc name.

    Examples:
      docs/project/dhfs/<dhf-name>/design-controls/architecture/foo.md
        → docs_project_dhfs_<dhf-name>_design-controls_architecture_foo
      tasks/<user>/119-some-task.md
        → tasks_<user>_119-some-task
      <doc-slug>-system-sad.md
        → <doc-slug>-system-sad

    Rules:
      - Path separators (/) → underscore (_)
      - .md extension stripped (also .docx — kept verbatim until Drive convert)
      - No other transformations; spaces preserved (rare in repo paths)
    """
    p = str(rel_path).strip().lstrip("./")
    p = re.sub(r"\\", "/", p)  # normalize Windows separators if any
    # Strip trailing extensions we know about
    for ext in (".md", ".markdown"):
        if p.lower().endswith(ext):
            p = p[: -len(ext)]
            break
    return p.replace("/", "_")


def drive_path_for(rel_path: str | Path, task_folder: str | None = None) -> list[str]:
    """Return the AI_PDLC folder path components + final doc name.

    Returns a list like ['AI_PDLC', '<project name>', '<task_folder>', 'docs_..._foo']
    where the last element is the doc name and the rest are folder names
    (in order). Project name and task_folder are read from project.yml.
    """
    tf = task_folder or resolve_current_user_task_folder()
    return [
        AI_PDLC_PREFIX,
        project_name(),
        tf,
        doc_name_from_repo_path(rel_path),
    ]


def drive_folder_components(task_folder: str | None = None) -> list[str]:
    """Return just the folder hierarchy (AI_PDLC/project/task_folder/),
    excluding the final doc name."""
    tf = task_folder or resolve_current_user_task_folder()
    return [AI_PDLC_PREFIX, project_name(), tf]


def archived_doc_name(original_name: str, freeze_date: str) -> str:
    """Apply the [ARCHIVED YYYY-MM-DD] prefix per Q7 (locked 2026-04-27).

    Args:
      original_name: the current Drive doc name
      freeze_date: 'YYYY-MM-DD' format
    """
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", freeze_date):
        raise ValueError(f"freeze_date must be YYYY-MM-DD, got {freeze_date!r}")
    return f"[ARCHIVED {freeze_date}] {original_name}"
