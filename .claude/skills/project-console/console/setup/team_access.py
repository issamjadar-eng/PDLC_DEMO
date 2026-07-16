"""Team repo-access audit — the roster's GitHub reality, in Team & Security.

Cross-references the GitHub repo's actual collaborators (via `gh api`,
read access to the collaborator list requires push/admin on the repo)
against the roster of record (`project.yml team.*`), with the
permission-aware teaching-project semantics:

- rostered active member            → ok (their role is shown)
- unrostered, read/triage           → observer (info — expected; the roster
                                      tracks contributors, not viewers)
- unrostered, write/maintain/admin  → warning (roster them or reduce to read)
- inactive member with ANY access   → error (offboarding not carried out)
- active member with NO access      → warning (missing access)

Network runs ONLY on demand (the section's Run-audit button), and the
result is cached at `.state/team-access-audit.json` with a timestamp;
page loads read the cache. The console only REPORTS — access changes
happen in GitHub (e.g. `gh api -X PUT repos/<repo>/collaborators/<user>
-f permission=pull`).
"""
from __future__ import annotations

import datetime as _dt
import json
import subprocess
from pathlib import Path

CACHE_REL = ".state/team-access-audit.json"
GH_TIMEOUT_S = 60

_WRITE_ROLES = ("write", "maintain", "admin")


class TeamAccessError(Exception):
    """User-facing failure (surfaced as HTTP 400 detail)."""


def _now_iso() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def classify(collaborators: list[dict], active: list[str],
             inactive: list[str]) -> dict:
    """Pure classification of collaborator (login, role) pairs against the
    roster. Returns {rows: [...], counts: {...}} — rows sorted worst-first."""
    severity_rank = {"error": 0, "warning": 1, "info": 2, "ok": 3}
    rows: list[dict] = []
    seen: set[str] = set()
    for c in collaborators:
        login = str(c.get("login") or "")
        role = str(c.get("role") or "")
        if not login:
            continue
        seen.add(login)
        if login in inactive:
            status, note = "error", (
                "Marked inactive in the roster but still has repo access — "
                "revoke it in GitHub."
            )
        elif login in active:
            status, note = "ok", "Rostered active member."
        elif role in _WRITE_ROLES:
            status, note = "warning", (
                "Not in the roster but can modify the repo — add them to "
                "team.active or reduce their access to read."
            )
        else:
            status, note = "info", (
                "Read-only observer — expected for a teaching project; the "
                "roster tracks contributors, not viewers."
            )
        rows.append({"login": login, "role": role, "status": status,
                     "note": note, "rostered": login in active})
    for member in active:
        if member and member not in seen:
            rows.append({
                "login": member, "role": "none", "status": "warning",
                "note": "In team.active but has NO repo access — grant it in "
                        "GitHub or check the github username in project.yml.",
                "rostered": True,
            })
    rows.sort(key=lambda r: (severity_rank.get(r["status"], 9), r["login"].lower()))
    counts = {k: sum(1 for r in rows if r["status"] == k)
              for k in ("ok", "info", "warning", "error")}
    return {"rows": rows, "counts": counts}


def run_audit(repo_root: Path) -> dict:
    """Fetch collaborators from GitHub, classify against the roster, cache."""
    import yaml

    try:
        project = yaml.safe_load((repo_root / "project.yml").read_text(encoding="utf-8")) or {}
    except Exception as e:
        raise TeamAccessError(f"project.yml could not be read ({e}).")
    repo = str((project.get("project") or {}).get("repo") or "")
    if not repo:
        raise TeamAccessError("project.yml has no project.repo — add it to enable the audit.")
    team = project.get("team") or {}
    active = [str(m.get("github") or "") for m in team.get("active") or [] if isinstance(m, dict)]
    inactive = [str(m.get("github") or "") for m in team.get("inactive") or [] if isinstance(m, dict)]

    try:
        r = subprocess.run(
            ["gh", "api", "--paginate", f"repos/{repo}/collaborators",
             "--jq", '.[] | {login: .login, role: .role_name}'],
            capture_output=True, text=True, timeout=GH_TIMEOUT_S,
        )
    except FileNotFoundError:
        raise TeamAccessError(
            "GitHub CLI (gh) is not installed — install it and run `gh auth login`."
        )
    except subprocess.TimeoutExpired:
        raise TeamAccessError("GitHub API call timed out.")
    if r.returncode != 0:
        detail = (r.stderr or r.stdout or "").strip()[:300]
        raise TeamAccessError(
            f"Could not list collaborators for {repo}: {detail or 'unknown error'} "
            "(viewing collaborators needs push access to the repo)."
        )
    collaborators = []
    for line in r.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            collaborators.append(json.loads(line))
        except json.JSONDecodeError:
            continue

    report = classify(collaborators, active, inactive)
    report.update({"repo": repo, "checked_at": _now_iso()})
    cache = repo_root / CACHE_REL
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def load_audit(repo_root: Path) -> dict | None:
    """Cached audit, or None. Never runs the network."""
    p = repo_root / CACHE_REL
    if not p.is_file():
        return None
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or not isinstance(data.get("rows"), list):
            return None
    except Exception:
        return None
    # Flag when the roster changed after the audit ran — findings may be stale.
    try:
        yml_mtime = (repo_root / "project.yml").stat().st_mtime
        checked = _dt.datetime.strptime(
            str(data.get("checked_at") or ""), "%Y-%m-%dT%H:%M:%SZ"
        ).replace(tzinfo=_dt.timezone.utc).timestamp()
        data["stale"] = yml_mtime > checked
    except Exception:
        data["stale"] = False
    return data
