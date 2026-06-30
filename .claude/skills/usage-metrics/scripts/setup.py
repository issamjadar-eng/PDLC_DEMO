#!/usr/bin/env python3
"""usage-metrics · setup — wire this skill into the current project. Idempotent.

Does the necessary work so the skill is operational in any project:
  1. Symlink the SessionStart refresh hook into .claude/hooks/ (skill is source).
  2. Register the hook in .claude/settings.json via the shared register-hook.sh.
  2b. Symlink .claude/statusline.sh -> skill-owned statusline.sh + register the
     `statusLine` block in settings.json (idempotent; leaves a project fork alone).
  3. Append the `usage_metrics:` config block to project.yml (if absent).
  4. Add `**/_usage-metrics/**` to file_locator.corpus_excludes (if absent).
  4b. Gitignore the per-session usage data so a generated-but-unpulled file never
     blocks a fast-forward of the shared branch (publish force-adds to commit it).
  5. Seed tools/usage-metrics/pricing.json from the bundled rate card (if absent).
  6. Create the gitignored .state/ dir.
  7. Report what was wired vs already present.

Run: python3 .claude/skills/usage-metrics/scripts/setup.py [--project-root PATH]
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

SKILL_REL = ".claude/skills/usage-metrics"
# (hook file, hook event) — each is symlinked into .claude/hooks/ and registered.
HOOKS = [
    ("usage-metrics-refresh.sh", "SessionStart"),   # local dashboard refresh (no git)
    ("usage-metrics-publish.sh", "SessionEnd"),      # publish own data to the shared branch
]


def find_project_root(start: Path) -> Path:
    for cand in (start.resolve(), *start.resolve().parents):
        if (cand / "project.yml").is_file():
            return cand
    raise SystemExit("setup: could not locate project root (no project.yml found)")


def main() -> int:
    ap = argparse.ArgumentParser(description="Wire usage-metrics into this project.")
    ap.add_argument("--project-root", type=Path, default=None)
    args = ap.parse_args()

    root = find_project_root(args.project_root or Path.cwd())
    skill = root / SKILL_REL
    report: list[str] = []

    # --- preflight ---
    reg = root / ".claude" / "hooks" / "register-hook.sh"
    if not reg.is_file():
        raise SystemExit("setup: .claude/hooks/register-hook.sh missing — run `/task setup` first.")
    if not skill.is_dir():
        raise SystemExit(f"setup: skill not found at {SKILL_REL} (is it installed?).")

    # --- 1. dirs ---
    (root / ".claude" / "hooks").mkdir(parents=True, exist_ok=True)
    (root / ".state").mkdir(exist_ok=True)
    exec_dir = root / "tools" / "usage-metrics"
    exec_dir.mkdir(parents=True, exist_ok=True)

    # --- 1a. execution-surface symlinks: tools/usage-metrics/*.py -> skill scripts ---
    # The skill holds the SOURCE; tools/usage-metrics/ is where they execute, so any
    # runtime artifacts (__pycache__, a venv, pip deps) land here, never in the skill.
    for name in ("collect.py", "aggregate.py", "publish.py", "setup.py"):
        link = exec_dir / name
        tgt = Path("..") / ".." / SKILL_REL / "scripts" / name
        desired = os.fspath(tgt)
        if link.is_symlink() and os.readlink(link) == desired:
            report.append(f"tools symlink {name}: already present")
        else:
            if link.exists() or link.is_symlink():
                link.unlink()
            link.symlink_to(tgt)
            report.append(f"tools symlink {name}: created")

    # --- 1b/2. symlink + register each hook (skill is the source of truth) ---
    for hook_name, event in HOOKS:
        link = root / ".claude" / "hooks" / hook_name
        target = Path("..") / "skills" / "usage-metrics" / "hooks" / hook_name
        desired = os.fspath(target)
        if link.is_symlink() and os.readlink(link) == desired:
            report.append(f"hook symlink {hook_name}: already present")
        else:
            if link.exists() or link.is_symlink():
                link.unlink()
            link.symlink_to(target)
            report.append(f"hook symlink {hook_name}: created")
        os.chmod(skill / "hooks" / hook_name, 0o755)
        cmd = '"$CLAUDE_PROJECT_DIR"/.claude/hooks/' + hook_name
        res = subprocess.run(
            [str(reg), event, "", "command", cmd],
            cwd=str(root), env={**os.environ, "CLAUDE_PROJECT_DIR": str(root)},
            capture_output=True, text=True,
        )
        report.append(f"{event} hook ({hook_name}): " + (res.stdout.strip() or res.stderr.strip() or "registered"))

    # --- 2b. status line: symlink the skill-owned script + register statusLine ---
    # The skill holds the SOURCE (statusline.sh); .claude/statusline.sh is a symlink,
    # so a `/sync-skills pull` that updates the skill auto-updates the installed line.
    sl_link = root / ".claude" / "statusline.sh"
    sl_target = Path("skills") / "usage-metrics" / "statusline.sh"
    sl_desired = os.fspath(sl_target)
    if sl_link.is_symlink() and os.readlink(sl_link) == sl_desired:
        report.append("statusline symlink: already present")
    elif sl_link.is_file() and not sl_link.is_symlink():
        report.append("statusline symlink: SKIP (project fork — regular file left alone)")
    else:
        if sl_link.exists() or sl_link.is_symlink():
            sl_link.unlink()
        sl_link.symlink_to(sl_target)
        report.append("statusline symlink: created")
    os.chmod(skill / "statusline.sh", 0o755)

    # Register the statusLine block in settings.json (idempotent; leave a fork alone).
    settings = root / ".claude" / "settings.json"
    sl_cmd = '"$CLAUDE_PROJECT_DIR"/.claude/statusline.sh'
    sj = json.loads(settings.read_text(encoding="utf-8")) if settings.is_file() else {}
    existing = sj.get("statusLine")
    if isinstance(existing, dict) and existing.get("command") == sl_cmd:
        report.append("statusLine config: already present")
    elif existing:
        report.append("statusLine config: SKIP (a different statusLine is configured — left alone)")
    else:
        sj["statusLine"] = {"type": "command", "command": sl_cmd}
        settings.parent.mkdir(parents=True, exist_ok=True)
        settings.write_text(json.dumps(sj, indent=2) + "\n", encoding="utf-8")
        report.append("statusLine config: registered in settings.json")

    # --- 3. project.yml usage_metrics block ---
    pyml = root / "project.yml"
    text = pyml.read_text(encoding="utf-8")
    if "\nusage_metrics:" in text or text.startswith("usage_metrics:"):
        report.append("project.yml usage_metrics: already present")
    else:
        block = (skill / "templates" / "usage_metrics.config.yml").read_text(encoding="utf-8")
        if not text.endswith("\n"):
            text += "\n"
        text += "\n" + block
        pyml.write_text(text, encoding="utf-8")
        report.append("project.yml usage_metrics: appended")

    # --- 4. file_locator exclude ---
    text = pyml.read_text(encoding="utf-8")
    if "**/_usage-metrics/**" in text:
        report.append("file_locator exclude: already present")
    elif "corpus_excludes:" in text:
        lines = text.splitlines(keepends=True)
        out, inserted = [], False
        for ln in lines:
            out.append(ln)
            if not inserted and "**/_work/**" in ln:
                indent = ln[: len(ln) - len(ln.lstrip())]
                out.append(f'{indent}- "**/_usage-metrics/**"   # per-person committed usage data (machine-generated, non-canonical)\n')
                inserted = True
        if not inserted:  # no _work line — add right after corpus_excludes:
            out = []
            for ln in lines:
                out.append(ln)
                if not inserted and ln.strip().startswith("corpus_excludes:"):
                    indent = ln[: len(ln) - len(ln.lstrip())] + "  "
                    out.append(f'{indent}- "**/_usage-metrics/**"\n')
                    inserted = True
        pyml.write_text("".join(out), encoding="utf-8")
        report.append("file_locator exclude: added **/_usage-metrics/**")
    else:
        report.append("file_locator exclude: SKIP (no corpus_excludes: block — add **/_usage-metrics/** manually)")

    # --- 4b. gitignore the per-session usage data ---
    # The per-session JSONs are machine-generated locally and published to the
    # shared branch by the SessionEnd hook (publish.py, via an isolated worktree
    # with `git add -f`). If they sat in the working tree as plain UNTRACKED files,
    # a later `git pull`/merge that brings the now-tracked file down from the branch
    # would abort: "untracked working tree files would be overwritten". Ignoring
    # them makes git treat the local copy as expendable — silently superseded by the
    # tracked version — so the fast-forward never blocks. Already-tracked files stay
    # tracked (gitignore never untracks); only fresh local copies are ignored.
    gi = root / ".gitignore"
    gi_text = gi.read_text(encoding="utf-8") if gi.is_file() else ""
    if "_usage-metrics/" in gi_text:
        report.append("gitignore usage-metrics: already present")
    else:
        block = (
            "\n# Usage-metrics per-session telemetry — machine-generated locally and\n"
            "# published to the shared branch by the usage-metrics SessionEnd hook\n"
            "# (publish.py force-adds). Ignored locally so a generated-but-not-yet-\n"
            "# pulled file never blocks a fast-forward/merge of the shared branch.\n"
            "tasks/*/_usage-metrics/\n"
            "**/_usage-metrics/\n"
        )
        if gi_text and not gi_text.endswith("\n"):
            gi_text += "\n"
        gi.write_text(gi_text + block, encoding="utf-8")
        report.append("gitignore usage-metrics: added tasks/*/_usage-metrics/ + **/_usage-metrics/")

    # --- 5. seed pricing.json ---
    proj_pricing = root / "tools" / "usage-metrics" / "pricing.json"
    if proj_pricing.is_file():
        report.append("pricing.json: already present (project copy)")
    else:
        seed = (skill / "templates" / "pricing.json").read_text(encoding="utf-8")
        proj_pricing.write_text(seed, encoding="utf-8")
        report.append("pricing.json: seeded into tools/usage-metrics/ (edit to update rates)")

    # --- 6. install the daily-aggregate GitHub Actions workflow ---
    # CI aggregates committed per-user data daily (it cannot collect — runners
    # have no local transcripts). Idempotent: install if absent / update if drifted.
    wf_src = (skill / "templates" / "usage-metrics-aggregate.yml").read_text(encoding="utf-8")
    wf_dir = root / ".github" / "workflows"
    wf_dir.mkdir(parents=True, exist_ok=True)
    wf_dst = wf_dir / "usage-metrics-aggregate.yml"
    if wf_dst.is_file() and wf_dst.read_text(encoding="utf-8") == wf_src:
        report.append("GitHub workflow: already present (daily aggregate)")
    else:
        verb = "updated" if wf_dst.is_file() else "installed"
        wf_dst.write_text(wf_src, encoding="utf-8")
        report.append(f"GitHub workflow: {verb} .github/workflows/usage-metrics-aggregate.yml (daily aggregate)")

    # --- 7. report ---
    print("usage-metrics setup — project:", root)
    for r in report:
        print("  •", r)
    print("\nNext: a new session auto-refreshes the dashboard when >7 days stale, or run now:")
    print("  python3 .claude/skills/usage-metrics/scripts/collect.py")
    print("  python3 .claude/skills/usage-metrics/scripts/aggregate.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
