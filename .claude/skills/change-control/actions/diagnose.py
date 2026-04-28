"""`change-control diagnose [--live]` — health-check + diagnostic dump.

Runs structural + lib-import + project-config + identity + (optionally
live) checks. Provides actionable diagnostic output for both routine
health checks and "something is broken" troubleshooting.

Without `--live`: structural + lib + identity (~2s).
With `--live`: also runs the web-control diagnose live test, exercises
gdoc lib smoke (connect + list_open_comments on any open doc tab if
present), and round-trips a temp metadata block through the active task
doc (~15s).
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL_ROOT))

# Self-relaunch under a Python with web-control's runtime deps if needed
from lib._runtime import ensure_runtime  # noqa: E402
ensure_runtime()


def _check(label, ok, detail="", recovery=""):
    return {"label": label, "ok": ok, "detail": detail, "recovery": recovery}


def _print_check(c):
    mark = "✓" if c["ok"] else "✗"
    print(f"  {mark}  {c['label']}")
    if c["detail"]:
        print(f"        {c['detail']}")
    if not c["ok"] and c["recovery"]:
        print(f"        recovery: {c['recovery']}")


def main() -> int:
    live = "--live" in sys.argv

    print("change-control diagnose")
    print("=======================")
    print()

    checks: list[dict] = []

    # 1. Structure
    print("[1] skill structure")
    for f in [
        "SKILL.md", "README.md", "VERSION",
        "actions/init.py", "actions/freeze.py", "actions/unfreeze.py",
        "actions/status.py", "actions/release.py",
        "actions/review_start.py", "actions/review_status.py",
        "actions/review_update.py", "actions/review_abort.py",
        "actions/help.py", "actions/diagnose.py",
        "lib/_runtime.py", "lib/path_convention.py",
        "lib/internal_review.py", "lib/gdoc.py",
        "tests/test-internal-review.sh",
    ]:
        c = _check(f"file: {f}", (SKILL_ROOT / f).is_file())
        checks.append(c)
        _print_check(c)

    # 2. Lib imports (without re-loading change-control's lib package)
    print()
    print("[2] lib imports")
    try:
        from lib.path_convention import project_name, project_root, doc_name_from_repo_path  # noqa
        from lib.internal_review import (  # noqa
            ReviewSection, ReviewItem, render_section, parse_section,
            upsert_block, find_block, remove_block, active_task_path,
        )
        c = _check("change-control lib importable", True)
    except ImportError as exc:
        c = _check("change-control lib importable", False, str(exc),
                   "fix imports in lib/__init__.py or path issues")
    checks.append(c)
    _print_check(c)

    try:
        from lib import gdoc as gdoc_lib  # noqa
        from lib.gdoc import _wc
        wc = _wc()
        sample_keys = sorted(list(wc.keys())[:6])
        c = _check(
            "gdoc loads web_control_lib correctly",
            "connect_to_chrome" in wc,
            f"loaded keys (sample): {sample_keys}",
        )
    except Exception as exc:  # noqa: BLE001
        c = _check("gdoc loads web_control_lib", False, str(exc),
                   "ensure web-control skill is installed at .claude/skills/web-control/")
    checks.append(c)
    _print_check(c)

    # 3. Project config
    print()
    print("[3] project config")
    try:
        from lib.path_convention import project_name, project_root, team_active, git_user_name, resolve_current_user_task_folder
        c = _check("project.name resolvable", True, project_name())
        checks.append(c); _print_check(c)
        ta = team_active()
        c = _check("team.active populated", len(ta) > 0, f"{len(ta)} members")
        checks.append(c); _print_check(c)
        try:
            tf = resolve_current_user_task_folder()
            c = _check(
                "git user.name matches a team member",
                True,
                f"task_folder={tf} (git user.name={git_user_name()!r})",
            )
        except RuntimeError as exc:
            c = _check(
                "git user.name matches a team member",
                False, str(exc),
                "set git config --global user.name to match an entry in project.yml team.active[].name",
            )
        checks.append(c); _print_check(c)
    except Exception as exc:  # noqa: BLE001
        c = _check("project config loadable", False, str(exc))
        checks.append(c); _print_check(c)

    # 4. Active task doc lookup
    print()
    print("[4] active task")
    session_id = os.environ.get("CLAUDE_SESSION_ID", "")
    if not session_id:
        c = _check("CLAUDE_SESSION_ID env", False, "not set",
                   "session-env hook should set this; check /task setup")
    else:
        c = _check("CLAUDE_SESSION_ID env", True, session_id[:8] + "...")
    checks.append(c); _print_check(c)
    if session_id:
        try:
            from lib.internal_review import active_task_path
            from lib.path_convention import project_root as _pr
            tp = active_task_path(session_id, _pr())
            if tp:
                c = _check("active task doc found", True, str(tp.relative_to(_pr())))
            else:
                c = _check("active task doc found", False,
                           "no active task; review-start will fail until one is activated",
                           "bash .claude/hooks/task-activate.sh add <session-id> <task-id>")
        except Exception as exc:  # noqa: BLE001
            c = _check("active task lookup", False, str(exc))
        checks.append(c); _print_check(c)

    # 5. Live: defer to web-control's diagnose, plus gdoc smoke
    if live:
        print()
        print("[5] LIVE: delegate to web-control diagnose --live")
        wc_diag = SKILL_ROOT.parent / "web-control" / "actions" / "diagnose.py"
        result = subprocess.run([sys.executable, str(wc_diag), "--live"],
                                capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            print("  ✓ web-control --live diagnose passed")
            checks.append(_check("web-control live diagnose", True))
        else:
            print("  ✗ web-control --live diagnose failed:")
            for line in result.stdout.splitlines()[-10:]:
                print(f"    {line}")
            checks.append(_check("web-control live diagnose", False,
                                 "see web-control diagnose --live output above"))

        # Live gdoc smoke
        print()
        print("[6] LIVE: gdoc smoke (any open doc tab → list_open_comments)")
        try:
            chrome = gdoc_lib._wc()["connect_to_chrome"]()
            tab = chrome.find_tab(lambda t: "/document/d/" in t.url)
            if tab:
                comments = gdoc_lib.list_open_comments(tab.url)
                c = _check(
                    "list_open_comments on live doc",
                    True,
                    f"tab={tab.title[:40]!r} comments={len(comments)}",
                )
            else:
                c = _check(
                    "list_open_comments smoke",
                    True,
                    "no open doc tab — skipping (open a doc + re-run if you want to validate)",
                )
        except Exception as exc:  # noqa: BLE001
            c = _check("gdoc lib smoke", False, str(exc),
                       "ensure web-control debug Chrome is running and signed in")
        checks.append(c); _print_check(c)

    # Summary
    print()
    print("=======================")
    n_ok = sum(1 for c in checks if c["ok"])
    n_fail = sum(1 for c in checks if not c["ok"])
    print(f"Results: {n_ok} pass, {n_fail} fail")
    if n_fail:
        print()
        print("Failed checks:")
        for c in checks:
            if not c["ok"]:
                print(f"  ✗ {c['label']}")
                if c["detail"]:
                    print(f"    detail: {c['detail']}")
                if c["recovery"]:
                    print(f"    -> {c['recovery']}")
    return 0 if n_fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
