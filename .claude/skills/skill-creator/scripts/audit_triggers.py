#!/usr/bin/env python3
"""
audit-triggers — full implementation of the trigger / cross-skill audit action.

Usage:
  python -m scripts.audit_triggers <skill-name> [--no-eval] [--quiet]

What it does (3 checks):
  1. Trigger eval — runs 20 should-trigger / should-not-trigger paraphrases
     against the target skill's frontmatter description via run_eval.py
     (which subprocess'es `claude -p` per query).
  2. Cross-skill conflict scan — pure-Python checks against every other
     skill in .claude/skills/:
       - trigger-verb overlap with object disambiguation
       - PreToolUse hook matcher collisions
       - project-name leakage (against project.yml)
       - actions/ vs § Actions documentation drift
  3. Pass/fail summary + remediation.

Output:
  - stdout report (markdown)
  - JSON log to .state/skill-creator-audit-<skill>-<YYYY-MM-DD>.json
  - clears the skill from .state/skill-creator-armed-{session_id}.json
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

# Make `from scripts.utils import ...` work whether run as -m or directly.
_SKILL_DIR = Path(__file__).resolve().parent.parent
if str(_SKILL_DIR) not in sys.path:
    sys.path.insert(0, str(_SKILL_DIR))
from scripts.utils import parse_skill_md  # noqa: E402


# ---------- helpers ----------

def find_project_root(start: Path) -> Path:
    for parent in [start, *start.parents]:
        if (parent / ".claude").is_dir():
            return parent
    return start


def load_project_tokens(project_yml: Path) -> set[str]:
    """Extract project-specific tokens from project.yml that should never
    appear in skill files. Prefer real YAML if PyYAML is available; fall
    back to a tolerant line scanner so the audit is not blocked when the
    user's environment lacks PyYAML.

    Sources scanned:
      - project.name                         (e.g., "MedTech Project")
      - dhfs[].leaf                          (e.g., "<device>-suite")
      - dhfs[].path basename                 (e.g., "<device>-module")
      - team.active[].name                   (e.g., "Jane Doe")
      - team.active[].github                 (e.g., "jane-doe")
    """
    tokens: set[str] = set()
    text = project_yml.read_text(errors="replace")

    # Splitting is per-source: project.name has unique sub-tokens worth
    # catching alone (e.g. company + product name); DHF leaves like
    # "<device>-suite" do — splitting catches the unique stem ("<device>")
    # while the GENERIC blacklist filters generic compound parts ("suite",
    # "services") that match generic English usage. Same for team names —
    # last names alone match too broadly, so we use the full string only
    # for team. Rule: split project.name and DHF leaves; full-only for team.
    def _add_full(value: str) -> None:
        v = value.strip().strip("'\"").lower()
        if v:
            tokens.add(v)

    def _add_split(value: str) -> None:
        v = value.strip().strip("'\"").lower()
        if not v:
            return
        tokens.add(v)
        for sub in re.split(r"[\s\-_/]+", v):
            if len(sub) > 3:
                tokens.add(sub)

    try:
        import yaml  # type: ignore
        data = yaml.safe_load(text) or {}
        _add_split(((data.get("project") or {}).get("name")) or "")
        for dhf in (data.get("dhfs") or []):
            # DHF leaves like "<device>-pre-op" — split so we catch the
            # unique stem (e.g. "<device>") even when used in a different
            # form (e.g. "DeviceName IntraOp"). Generic sub-tokens (pre,
            # op, suite, services, intra) are filtered by GENERIC below.
            _add_split(dhf.get("leaf") or "")
            p = dhf.get("path") or ""
            if p:
                _add_split(p.rsplit("/", 1)[-1])
        for member in ((data.get("team") or {}).get("active") or []):
            # Team names: full only — first names alone (Bob, Sam, Ben)
            # match too broadly in normal text.
            _add_full(member.get("name") or "")
            _add_full(member.get("github") or "")
    except ImportError:
        # Tolerant fallback: line-based scan. Treat all values as full
        # tokens (no split) since we can't tell which key they belong to.
        for line in text.splitlines():
            m = re.match(r"\s*(name|leaf|github):\s*(.+?)\s*$", line)
            if m:
                _add_full(m.group(2))

    # Filter out generic placeholder tokens that should never be flagged.
    # These are words that may appear inside compound names but are too
    # common in normal English/technical writing to be useful signals.
    GENERIC = {
        # YAML field names + common skill scaffolding
        "name", "project", "skill", "test", "demo", "example", "main",
        "user", "team", "active", "inactive", "leaf", "path", "github",
        # generic technical words frequent in compound DHF names
        "suite", "service", "services", "core", "common", "internal",
        "external", "control", "review", "config", "data", "admin",
        "default", "module", "system", "platform", "tool", "tools",
        "client", "server", "model", "models", "manager", "management",
        "device", "site", "page", "doc", "docs",
        # common sub-tokens that appear in DHF/path names but are too
        # broad to be project-specific (medical/regulated-device jargon)
        "pre", "post", "intra", "extra", "mgmt", "ops", "infra",
        "frontend", "backend", "ui", "api", "rest", "auth",
    }
    return tokens - GENERIC


def list_skills(skills_dir: Path) -> list[Path]:
    return sorted(p for p in skills_dir.iterdir()
                  if p.is_dir() and (p / "SKILL.md").exists())


# ---------- check 1: trigger eval ----------

DEFAULT_QUERY_TEMPLATES = [
    # ---- should-trigger (10) ----
    # Explicit
    ("modify the {name} skill to handle {topic}", True),
    ("create a new skill for {topic}", True),
    ("optimize the {name} skill description", True),
    # Maintenance / extension
    ("add a new action to the {name} skill", True),
    ("extend the {name} skill so it can also do {topic}", True),
    ("fix a bug in the {name} skill — {topic} isn't working", True),
    ("the {name} skill should also support {topic}", True),
    # Path-based
    ("I'm editing .claude/skills/{name}/SKILL.md to update its description", True),
    # Audit / evaluation
    ("audit the trigger words for {name} — they might conflict with another skill", True),
    ("does the {name} skill description actually fire on natural-language phrasings?", True),
    # ---- should-not-trigger (10) ----
    ("fix the bug in src/api/handler.py", False),
    ("update the README.md in the project root", False),
    ("write a unit test for the payment module", False),
    ("run the linter and fix all errors", False),
    ("refactor the React component in app/components/Foo.tsx", False),
    ("improve the documentation in docs/onboarding.md", False),
    ("modify the user model schema in db/migrations/", False),
    ("set up CI for the new repo", False),
    ("debug why the test suite is slow", False),
    ("add error handling to the payment processor", False),
]


def build_eval_set(skill_name: str, topic_hint: str = "<feature>") -> list[dict]:
    out = []
    for tmpl, should in DEFAULT_QUERY_TEMPLATES:
        out.append({
            "query": tmpl.format(name=skill_name, topic=topic_hint),
            "should_trigger": should,
        })
    return out


def run_trigger_eval(skill_path: Path, eval_set: list[dict],
                     project_root: Path, model: str = "claude-haiku-4-5-20251001",
                     timeout: int = 60) -> dict[str, Any]:
    """Invoke run_eval.py as a subprocess for the trigger eval.

    Returns parsed JSON result dict, or a stub with `skipped=True` on failure.
    """
    eval_path = project_root / ".state" / f"audit-eval-{skill_path.name}.json"
    eval_path.parent.mkdir(parents=True, exist_ok=True)
    eval_path.write_text(json.dumps(eval_set, indent=2))

    out_path = project_root / ".state" / f"audit-eval-result-{skill_path.name}.json"

    cmd = [
        sys.executable, "-m", "scripts.run_eval",
        "--skill", str(skill_path),
        "--eval-set", str(eval_path),
        "--output", str(out_path),
        "--model", model,
        "--timeout", str(timeout),
    ]
    try:
        proc = subprocess.run(
            cmd, cwd=_SKILL_DIR.parent.parent.parent,  # project root
            capture_output=True, text=True, timeout=timeout * len(eval_set) + 60,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError) as exc:
        return {"skipped": True, "reason": f"run_eval invocation failed: {exc}"}

    if proc.returncode != 0 or not out_path.exists():
        return {
            "skipped": True,
            "reason": f"run_eval exit={proc.returncode}; stderr: {proc.stderr[-500:]}",
        }
    try:
        return json.loads(out_path.read_text())
    except json.JSONDecodeError as exc:
        return {"skipped": True, "reason": f"could not parse result: {exc}"}


# ---------- check 2a: trigger-verb overlap ----------

# Verbs that appear in many descriptions but are object-anchored. We only
# flag a conflict when verb AND a likely-shared object both overlap.
TRACKED_VERBS = {
    "adopt", "import", "sync", "publish", "push", "pull", "fetch",
    "release", "snapshot", "mirror", "copy", "ingest", "acquire",
    "freeze", "create", "modify", "edit",
}


def extract_description(skill_path: Path) -> str:
    try:
        _, desc, _ = parse_skill_md(skill_path)
        return desc or ""
    except Exception:
        return ""


def verb_overlap_audit(target: str, target_desc: str,
                       all_skills: list[Path]) -> list[dict]:
    """Find verb+object overlap with other skills."""
    target_words = set(re.findall(r"\b[a-z]+\b", target_desc.lower()))
    target_verbs = target_words & TRACKED_VERBS

    findings = []
    for other in all_skills:
        if other.name == target:
            continue
        other_desc = extract_description(other).lower()
        other_words = set(re.findall(r"\b[a-z]+\b", other_desc))
        shared_verbs = target_verbs & other_words & TRACKED_VERBS
        if not shared_verbs:
            continue

        # Collect candidate object words (nouns) — heuristic: words near the
        # shared verbs in either description.
        for verb in shared_verbs:
            t_ctx = _verb_context(target_desc.lower(), verb)
            o_ctx = _verb_context(other_desc, verb)
            shared_objects = (t_ctx & o_ctx) - TRACKED_VERBS - _STOPWORDS
            if shared_objects:
                findings.append({
                    "verb": verb,
                    "other_skill": other.name,
                    "shared_objects": sorted(shared_objects)[:5],
                    "severity": "review",
                })
    return findings


_STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "of", "in", "on", "at", "to", "for",
    "with", "by", "from", "as", "is", "be", "are", "was", "were", "this", "that",
    "these", "those", "it", "its", "any", "all", "each", "via", "use", "used",
    "uses", "user", "user's", "users", "skill", "skills", "action", "actions",
    "do", "does", "doing", "done", "want", "wants", "when", "where", "while",
    "if", "then", "than", "should", "would", "could", "must", "may", "can",
    "also", "only", "into", "onto", "out", "off", "up", "down", "over", "under",
    "before", "after", "during", "between", "within", "without", "your", "their",
    "our", "his", "her", "my", "we", "you", "they", "i", "me", "us", "them",
}


def _verb_context(text: str, verb: str, window: int = 6) -> set[str]:
    """Return set of words within `window` tokens of any occurrence of `verb`."""
    tokens = re.findall(r"\b[a-z]+\b", text)
    out = set()
    for i, tok in enumerate(tokens):
        if tok == verb:
            for j in range(max(0, i - window), min(len(tokens), i + window + 1)):
                if j != i and len(tokens[j]) > 2:
                    out.add(tokens[j])
    return out


# ---------- check 2b: PreToolUse hook matcher collisions ----------

HOOK_MATCHER_RE = re.compile(
    r'register-hook\.sh\s+PreToolUse\s+["\']?([^"\'\s]+)["\']?', re.IGNORECASE)


def hook_collision_audit(target: str, all_skills: list[Path]) -> list[dict]:
    matchers_by_skill: dict[str, list[str]] = {}
    for s in all_skills:
        text = (s / "SKILL.md").read_text(errors="replace")
        for m in HOOK_MATCHER_RE.finditer(text):
            matchers_by_skill.setdefault(s.name, []).append(m.group(1))

    target_matchers = set(matchers_by_skill.get(target, []))
    if not target_matchers:
        return []

    findings = []
    for other, ms in matchers_by_skill.items():
        if other == target:
            continue
        shared = target_matchers & set(ms)
        for shared_m in shared:
            findings.append({
                "matcher": shared_m,
                "other_skill": other,
                "severity": "stacking — verify hooks chain correctly under both denials",
            })
    return findings


# ---------- check 2c: project-name leakage ----------

def name_leakage_audit(skill_path: Path, project_root: Path) -> list[str]:
    """Scan all skill files for project-specific names from project.yml.

    Tokens come from project.name, dhfs[].leaf, dhfs[].path basename,
    team.active[].name, team.active[].github. Each line that contains any
    token (case-insensitive, word-bounded) is reported.
    """
    project_yml = project_root / "project.yml"
    if not project_yml.exists():
        return []
    tokens = load_project_tokens(project_yml)
    if not tokens:
        return []
    pattern = re.compile(r"\b(" + "|".join(re.escape(t) for t in tokens) + r")\b",
                         re.IGNORECASE)

    leaks = []
    for f in skill_path.rglob("*"):
        if f.is_dir() or f.suffix in {".pyc", ".so"} or "__pycache__" in f.parts:
            continue
        try:
            text = f.read_text(errors="replace")
        except (OSError, UnicodeDecodeError):
            continue
        for ln, line in enumerate(text.splitlines(), 1):
            if pattern.search(line):
                leaks.append(f"{f.relative_to(skill_path)}:{ln}: {line.strip()[:120]}")
                if len(leaks) >= 15:
                    return leaks
    return leaks


# ---------- check 2d: actions/ vs § Actions documentation drift ----------

def actions_drift_audit(skill_path: Path) -> dict[str, list[str]]:
    """Compare files under actions/ with action headings in SKILL.md."""
    actions_dir = skill_path / "actions"
    fs_actions: set[str] = set()
    if actions_dir.is_dir():
        for f in actions_dir.iterdir():
            if f.is_file() and f.suffix in {".md", ".py", ".sh"}:
                stem = f.stem.replace("_", "-")
                if stem in {"__init__", "helper"} or stem.endswith("-helper"):
                    continue
                fs_actions.add(stem)

    skill_md = (skill_path / "SKILL.md").read_text(errors="replace")
    documented: set[str] = set()
    # Match "### `<name>" or "### `<name> <args>"
    for m in re.finditer(r"^### `([a-z][\w-]*)", skill_md, re.MULTILINE):
        documented.add(m.group(1))

    # Normalize underscores/hyphens
    documented_norm = {d.replace("_", "-") for d in documented}

    only_in_fs = sorted(fs_actions - documented_norm)
    only_in_md = sorted(documented_norm - fs_actions)
    return {"undocumented_files": only_in_fs, "documented_but_missing_file": only_in_md}


# ---------- main ----------

def disarm_skill(project_root: Path, skill_name: str) -> None:
    session_id = os.environ.get("CLAUDE_SESSION_ID", "")
    if not session_id:
        return
    state_path = project_root / ".state" / f"skill-creator-armed-{session_id}.json"
    if not state_path.exists():
        return
    try:
        data = json.loads(state_path.read_text())
        skills = [s for s in data.get("skills", []) if s != skill_name]
        state_path.write_text(json.dumps({"skills": skills}, indent=2))
    except (json.JSONDecodeError, OSError):
        pass


def render_report(skill_name: str, eval_result: dict, verb_findings: list[dict],
                  hook_findings: list[dict], leakage: list[str],
                  drift: dict[str, list[str]]) -> str:
    lines: list[str] = []
    P = lines.append
    P(f"# Trigger audit — `{skill_name}`")
    P(f"_run at {_dt.datetime.now().isoformat(timespec='seconds')}_")
    P("")

    # 1. Trigger eval
    P("## 1. Trigger eval (20 queries)")
    if eval_result.get("skipped"):
        P(f"_skipped: {eval_result.get('reason', 'unknown')}_")
    else:
        results = eval_result.get("results", [])
        passes = sum(1 for r in results if r.get("triggered") == r.get("should_trigger"))
        total = len(results)
        P(f"**{passes}/{total} pass.**")
        fails = [r for r in results if r.get("triggered") != r.get("should_trigger")]
        if fails:
            P("")
            P("Failures:")
            for r in fails:
                expected = "should-trigger" if r.get("should_trigger") else "should-not-trigger"
                got = "triggered" if r.get("triggered") else "did not trigger"
                P(f"- `{r.get('query', '')[:100]}` — expected {expected}, **{got}**")
    P("")

    # 2a. Verb overlap
    P("## 2a. Trigger-verb overlap with other skills")
    if not verb_findings:
        P("_no overlapping verb+object pairs found._")
    else:
        for f in verb_findings:
            P(f"- verb `{f['verb']}` shared with `{f['other_skill']}` "
              f"(common context: {', '.join(f['shared_objects'])}) — {f['severity']}")
    P("")

    # 2b. Hook collisions
    P("## 2b. PreToolUse hook matcher collisions")
    if not hook_findings:
        P("_no collisions._")
    else:
        for f in hook_findings:
            P(f"- matcher `{f['matcher']}` also registered by `{f['other_skill']}` — {f['severity']}")
    P("")

    # 2c. Name leakage
    P("## 2c. Project-name leakage")
    if not leakage:
        P("_clean — no project-name leakage in skill files._")
    else:
        P("**Leaks detected — skills must stay project-agnostic:**")
        for l in leakage:
            P(f"- {l}")
    P("")

    # 2d. Drift
    P("## 2d. `actions/` vs § Actions documentation drift")
    undoc = drift.get("undocumented_files", [])
    missing = drift.get("documented_but_missing_file", [])
    if not undoc and not missing:
        P("_clean — every file documented; every documented action has a file._")
    else:
        if undoc:
            P("**Files exist under `actions/` but NOT documented in SKILL.md § Actions:**")
            for a in undoc:
                P(f"- `{a}`")
        if missing:
            P("**Documented in SKILL.md § Actions but no file under `actions/`:**")
            for a in missing:
                P(f"- `{a}`")
    P("")

    # Summary
    P("## Summary")
    issues = []
    if eval_result.get("skipped"):
        issues.append("eval skipped (run manually)")
    elif eval_result.get("results"):
        fails = [r for r in eval_result["results"] if r.get("triggered") != r.get("should_trigger")]
        if fails:
            issues.append(f"{len(fails)} eval queries fail")
    if verb_findings:
        issues.append(f"{len(verb_findings)} verb-overlap findings")
    if hook_findings:
        issues.append(f"{len(hook_findings)} hook collisions")
    if leakage:
        issues.append("project-name leakage")
    if drift.get("undocumented_files") or drift.get("documented_but_missing_file"):
        issues.append("actions/ ↔ SKILL.md drift")
    if not issues:
        P("**PASS — no issues.**")
    else:
        P(f"**REVIEW — {len(issues)} item(s):** {'; '.join(issues)}.")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit a skill's trigger surface")
    parser.add_argument("skill_name", help="Skill name (folder under .claude/skills/)")
    parser.add_argument("--no-eval", action="store_true",
                        help="Skip the LLM trigger eval (run only static checks)")
    parser.add_argument("--quiet", action="store_true", help="Reduce verbosity")
    args = parser.parse_args(argv)

    project_root = find_project_root(Path.cwd())
    skills_dir = project_root / ".claude" / "skills"
    target = skills_dir / args.skill_name
    if not target.is_dir() or not (target / "SKILL.md").exists():
        print(f"error: skill not found: {target}", file=sys.stderr)
        return 2

    all_skills = list_skills(skills_dir)

    # Static checks first
    target_desc = extract_description(target)
    verb_findings = verb_overlap_audit(args.skill_name, target_desc, all_skills)
    hook_findings = hook_collision_audit(args.skill_name, all_skills)
    leakage = name_leakage_audit(target, project_root)
    drift = actions_drift_audit(target)

    # Trigger eval (subprocess; can be skipped)
    if args.no_eval:
        eval_result = {"skipped": True, "reason": "--no-eval flag"}
    else:
        eval_set = build_eval_set(args.skill_name)
        eval_result = run_trigger_eval(target, eval_set, project_root)

    report = render_report(args.skill_name, eval_result, verb_findings,
                           hook_findings, leakage, drift)
    print(report)

    # Persist log
    log_dir = project_root / ".state"
    log_dir.mkdir(parents=True, exist_ok=True)
    today = _dt.date.today().isoformat()
    log_path = log_dir / f"skill-creator-audit-{args.skill_name}-{today}.json"
    log_path.write_text(json.dumps({
        "skill": args.skill_name,
        "run_at": _dt.datetime.now().isoformat(timespec="seconds"),
        "eval_result": eval_result,
        "verb_findings": verb_findings,
        "hook_findings": hook_findings,
        "leakage": leakage,
        "drift": drift,
    }, indent=2))
    if not args.quiet:
        print(f"\n_full log: {log_path.relative_to(project_root)}_", file=sys.stderr)

    # Disarm this skill in the watch hook's per-session state
    disarm_skill(project_root, args.skill_name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
