"""`change-control promote` — move an adopted file from the staging tree
to its canonical DHF location, preserving frontmatter (and optionally
the snapshot cache mapping).

Usage:

    python actions/promote.py <staged-path> <dhf-path> [--no-git]

  - <staged-path>: the file currently under e.g.
    `docs/confluence-staging/AFAI/.../page.md`
  - <dhf-path>: the target under e.g.
    `docs/project/dhfs/<dhf>/.../page.md`

What it does:
  1. Verify the staged file exists and has `confluence.page_id`
     frontmatter (otherwise it's not a managed adopted file — refuse).
  2. Verify the DHF target is under `docs/project/dhfs/`.
  3. Move via `git mv` if the repo is a git repo and `--no-git` was
     not passed; otherwise plain `os.rename`.
  4. Frontmatter is unchanged — the `confluence.page_id` binds the
     file to its Confluence page regardless of repo location.
  5. Print a one-line summary.

This is a pure-local action — no MCP, no network. Project-agnostic.
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL_ROOT))

from lib.frontmatter import read as read_frontmatter  # noqa: E402


DHF_PREFIX = "docs/project/dhfs/"


class PromoteError(Exception):
    pass


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="change-control promote",
        description="Move an adopted file from staging into its canonical DHF location.",
    )
    p.add_argument("staged_path", help="Source file under docs/confluence-staging/.../*.md")
    p.add_argument("dhf_path", help="Target file under docs/project/dhfs/.../*.md")
    p.add_argument(
        "--no-git",
        action="store_true",
        help="Use plain rename instead of `git mv` (skips git history preservation).",
    )
    p.add_argument(
        "--allow-non-dhf-target",
        action="store_true",
        help="Allow targets outside docs/project/dhfs/ (use only for one-offs).",
    )
    return p


def _is_git_repo(at: Path) -> bool:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            cwd=at,
            capture_output=True,
            text=True,
            check=False,
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False


def _git_mv(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        ["git", "mv", str(src), str(dst)],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise PromoteError(
            f"git mv failed (exit {result.returncode}): {result.stderr.strip()}"
        )


def _plain_mv(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(src), str(dst))


def promote(
    staged_path: str | Path,
    dhf_path: str | Path,
    *,
    use_git: bool = True,
    allow_non_dhf_target: bool = False,
) -> Path:
    src = Path(staged_path)
    dst = Path(dhf_path)
    if not src.is_file():
        raise PromoteError(f"staged file not found: {src}")
    if dst.exists():
        raise PromoteError(f"target already exists: {dst}")

    fm = read_frontmatter(src)
    confluence = fm.data.get("confluence") or {}
    if not isinstance(confluence, dict) or not confluence.get("page_id"):
        raise PromoteError(
            f"staged file lacks `confluence.page_id` frontmatter — refusing to "
            f"promote unmanaged file: {src}"
        )

    target_str = str(dst).replace(os.sep, "/")
    if not target_str.startswith(DHF_PREFIX) and not allow_non_dhf_target:
        raise PromoteError(
            f"target {dst} is not under {DHF_PREFIX!r}. Pass "
            f"--allow-non-dhf-target to override (rare; only use for one-offs)."
        )

    repo_root = Path.cwd()
    if use_git and _is_git_repo(repo_root):
        _git_mv(src, dst)
    else:
        _plain_mv(src, dst)
    return dst


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        target = promote(
            args.staged_path,
            args.dhf_path,
            use_git=not args.no_git,
            allow_non_dhf_target=args.allow_non_dhf_target,
        )
    except PromoteError as exc:
        print(f"promote: error: {exc}", file=sys.stderr)
        return 64
    print(f"promoted: {args.staged_path} -> {target}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
