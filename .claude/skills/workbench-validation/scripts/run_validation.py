#!/usr/bin/env python3
"""Workbench validation runner.

Executes the project's workbench validation manifest (validation.yml): a
declarative catalog of test cases (existing skill test suites, lints, audits)
mapped to workbench user needs (WUN-xx). Records a timestamped results JSON
plus a `latest.json` copy under the manifest's results_dir, including the
configuration baseline (git SHA, dirty flag, per-skill versions) required for
tool-validation evidence.

Evidence: every case's FULL captured execution output (stdout+stderr merged,
ANSI-stripped) is written to `results/<run-id>/<TC-ID>.log` with an execution
header (command, cwd, env modifications, timestamps, exit code, status). The
run JSON carries the repo-relative `log` path per case; `output_tail` remains
only a convenience excerpt — the log file is the evidence of record.

Statuses:
  PASS    - exit 0 (and pass_pattern matched, if declared)
  FAIL    - nonzero exit, or fail_pattern matched, or pass_pattern absent
  SKIPPED - a binary listed in `requires` is not installed
  NOT-APPLICABLE - an `endpoint: live` case whose `connection:` the manifest
            declares as `none` for this deployment (never executed; reported
            explicitly so a deliberately absent connection does not read as a
            gap)
  ERROR   - timeout or launcher exception

Evidence tiers (D7): every case declares `endpoint: none | mocked | live` —
whether it touched no external system, a fake transport with canned payloads,
or a real endpoint. The tier is carried into the run JSON, the evidence-log
header, the report, and the console sidecar so a reader can tell mock-verified
from live-verified evidence.

Environment record (D8): the run JSON's `environment` block is the canonical
setup record — configuration under test (git SHA, dirty-file list, per-skill
versions incl. frontmatter/VERSION mismatches, hooks, agents, rules), runtime
(Python, OS, harness version, model id), tooling (every required binary's
resolved path + version), connections (declared tiers, MCP servers configured,
reachability probes), and isolation (env vars stripped/set).

Exit code: 0 if no FAIL/ERROR cases, 1 otherwise (CI-gate friendly).

Usage:
  python3 run_validation.py --root <repo_root> [--manifest <path>]
                            [--only TC-01,TC-02] [--render]
                            [--model-id <identifier>] [--invoked-via cli|console]
"""

import argparse
import getpass
import hashlib
import json
import os
import platform as platform_mod
import re
import shutil
import socket
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("PyYAML is required (python3 -m pip install pyyaml, or run via `uv run --with pyyaml`).")

ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")
DEFAULT_MANIFEST = "docs/project/workbench-validation/validation.yml"
OUTPUT_TAIL = 1500


def utc_now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def run_cmd(cmd, cwd, timeout, env):
    t0 = time.monotonic()
    try:
        proc = subprocess.run(
            cmd, cwd=str(cwd), timeout=timeout, env=env,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
        )
        return proc.returncode, proc.stdout or "", time.monotonic() - t0, None
    except subprocess.TimeoutExpired as exc:
        out = exc.stdout.decode() if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        return None, out, time.monotonic() - t0, f"timeout after {timeout}s"
    except Exception as exc:  # launcher failure (missing file, perms, ...)
        return None, "", time.monotonic() - t0, str(exc)


def git_baseline(root):
    def g(*args):
        try:
            return subprocess.run(
                ["git", *args], cwd=str(root), capture_output=True, text=True, timeout=30
            ).stdout.strip()
        except Exception:
            return ""
    porcelain = g("status", "--porcelain")
    dirty_files = [ln.strip() for ln in porcelain.splitlines() if ln.strip()]
    return {
        "git_sha": g("rev-parse", "HEAD"),
        "git_sha_short": g("rev-parse", "--short", "HEAD"),
        "git_branch": g("rev-parse", "--abbrev-ref", "HEAD"),
        "git_dirty": bool(dirty_files),
        "git_dirty_files": dirty_files[:200],
        "git_dirty_count": len(dirty_files),
    }


def frontmatter_block(text):
    """The YAML frontmatter between the opening and closing `---` fences
    (empty string when the file has none)."""
    if not text.startswith("---"):
        return ""
    end = text.find("\n---", 3)
    return text[3:end] if end != -1 else text[3:20000]


def skill_versions(root):
    """Per-skill version map parsed from SKILL.md frontmatter (+ VERSION file)."""
    versions = {}
    skills_dir = root / ".claude" / "skills"
    if not skills_dir.is_dir():
        return versions
    for skill_dir in sorted(skills_dir.iterdir()):
        skill_md = skill_dir / "SKILL.md"
        if not skill_dir.is_dir() or not skill_md.is_file():
            continue
        entry = {}
        try:
            # Parse the YAML frontmatter block itself (between the `---`
            # fences) — a fixed head window silently drops the version of any
            # skill whose description is long, which then records an empty
            # UUT pin for that skill.
            head = frontmatter_block(skill_md.read_text(encoding="utf-8", errors="replace"))
            m = re.search(r"^version:\s*(\S+)", head, re.MULTILINE)
            if m:
                entry["version"] = m.group(1).strip("'\"")
            m = re.search(r"^updated:\s*(\S+)", head, re.MULTILINE)
            if m:
                entry["updated"] = m.group(1).strip("'\"")
        except OSError:
            pass
        vfile = skill_dir / "VERSION"
        if vfile.is_file():
            try:
                entry["version_file"] = vfile.read_text().strip()
            except OSError:
                pass
        # D5 — an ambiguous UUT pin (frontmatter says one thing, VERSION file
        # another) is recorded, never silently resolved.
        if entry.get("version") and entry.get("version_file") \
                and entry["version"] != entry["version_file"]:
            entry["version_mismatch"] = True
        versions[skill_dir.name] = entry
    return versions


def _first_line(text):
    return (text or "").strip().splitlines()[0].strip() if (text or "").strip() else None


def probe_binary(name):
    """Resolved path + `--version` first line for a required binary, or a
    `missing` marker. Never raises; bounded by a short timeout."""
    path = shutil.which(name)
    if path is None:
        return {"path": None, "version": None, "missing": True}
    version = None
    for flag in ("--version", "-version", "version"):
        try:
            proc = subprocess.run([path, flag], capture_output=True, text=True, timeout=10)
            out = _first_line(proc.stdout) or _first_line(proc.stderr)
            if out:
                version = out[:200]
                break
        except Exception:
            continue
    return {"path": path, "version": version, "missing": False}


def probe_python_packages(root):
    """Versions of the test-harness packages `uv run --with pytest --with pyyaml`
    actually resolves — the versions the pytest-based cases executed under."""
    if shutil.which("uv") is None:
        return {"note": "uv not installed — pytest-based cases would be SKIPPED"}
    code = ("import json,sys;o={};\n"
            "import pytest;o['pytest']=pytest.__version__\n"
            "import yaml;o['pyyaml']=getattr(yaml,'__version__',None)\n"
            "print(json.dumps(o))")
    try:
        proc = subprocess.run(
            ["uv", "run", "--no-project", "--with", "pytest", "--with", "pyyaml", "--",
             "python", "-c", code],
            cwd=str(root), capture_output=True, text=True, timeout=120)
        line = [ln for ln in proc.stdout.splitlines() if ln.startswith("{")]
        return json.loads(line[-1]) if line else {"note": "could not resolve"}
    except Exception as exc:
        return {"note": f"probe failed: {exc}"}


def harness_version():
    """Version of the agent harness driving the workbench, when a CLI exposes
    one; null (and reported as 'not captured') otherwise."""
    for candidate in ("claude",):
        path = shutil.which(candidate)
        if path is None:
            continue
        try:
            proc = subprocess.run([path, "--version"], capture_output=True, text=True, timeout=10)
            out = _first_line(proc.stdout) or _first_line(proc.stderr)
            if out:
                return out[:200]
        except Exception:
            continue
    return None


def _read_project_yml(root):
    try:
        return yaml.safe_load((root / "project.yml").read_text(encoding="utf-8")) or {}
    except Exception:
        return {}


def _mcp_servers_configured(root, project_yml):
    """MCP servers the project approves (project.yml) and configures (settings)."""
    approved = ((project_yml.get("security") or {}).get("approved_mcps")) or []
    approved = [a.get("name") if isinstance(a, dict) else str(a) for a in approved]
    configured = []
    for name in (".mcp.json", ".claude/settings.json", ".claude/settings.local.json"):
        fp = root / name
        if not fp.is_file():
            continue
        try:
            data = json.loads(fp.read_text(encoding="utf-8"))
        except Exception:
            continue
        for key in (data.get("mcpServers") or {}):
            configured.append(f"{key} ({name})")
    return {"approved": approved, "configured": configured}


def probe_connections(root, manifest, project_yml):
    """D7/D8 — what this deployment declares for each external connection,
    and a bounded reachability probe for anything declared present. A
    declared `none` is never probed (it is not a gap, it is a statement)."""
    declared = manifest.get("connections") or {}
    endpoints = {}
    cc = project_yml.get("change_control") or {}
    jira_url = (cc.get("jira") or {}).get("base_url")
    for space in cc.get("spaces") or []:
        if isinstance(space, dict) and space.get("base_url"):
            endpoints.setdefault("confluence", space["base_url"])
    if jira_url:
        endpoints["jira"] = jira_url
    out = {}
    for name, state in sorted(declared.items()):
        entry = {"declared": state, "base_url": endpoints.get(name), "reachability": None}
        if state in (None, "none", "None", False):
            entry["reachability"] = "not probed — declared none"
        elif not endpoints.get(name):
            entry["reachability"] = "not probed — no base_url in project.yml"
        else:
            try:
                import urllib.request
                req = urllib.request.Request(endpoints[name], method="HEAD")
                with urllib.request.urlopen(req, timeout=5) as resp:
                    entry["reachability"] = f"reachable (HTTP {resp.status})"
            except Exception as exc:
                entry["reachability"] = f"unreachable ({type(exc).__name__})"
        out[name] = entry
    return out


def operator_info(root):
    """Who ran the validation, from where — part of the setup record."""
    def g(*args):
        try:
            return subprocess.run(
                ["git", *args], cwd=str(root), capture_output=True, text=True, timeout=15
            ).stdout.strip() or None
        except Exception:
            return None
    try:
        os_user = getpass.getuser()
    except Exception:
        os_user = None
    try:
        hostname = socket.gethostname()
    except Exception:
        hostname = None
    return {
        "git_user": g("config", "user.name"),
        "git_email": g("config", "user.email"),
        "os_user": os_user,
        "hostname": hostname,
        "os": platform_mod.platform(),
    }


def _schema_at_least(version, floor):
    def parts(v):
        try:
            return tuple(int(x) for x in str(v).split("."))
        except ValueError:
            return (0,)
    return parts(version) >= parts(floor)


def lint_needs(needs):
    """User-story contract for needs: `role`, `need` (outcome phrased to follow
    'I need the workbench to…') and `so_that` (purpose) are all required;
    the renderer composes the sentence. Returns (problems, warnings)."""
    problems, warns = [], []
    for n in needs:
        nid = n.get("id", "WUN-??")
        for field in ("role", "need", "so_that"):
            if not str(n.get(field) or "").strip():
                problems.append(f"{nid}: missing `{field}`")
        text = str(n.get("need") or "").strip()
        low = text.lower()
        if low.startswith(("as a ", "as an ", "i need ")):
            warns.append(f"{nid}: `need` already starts with story wording — write only the outcome "
                         "(the renderer prefixes 'As a <role>, I need the workbench to')")
        if low.startswith(("the workbench ", "the system ")):
            warns.append(f"{nid}: `need` starts with a subject — phrase it as the outcome verb phrase")
        so = str(n.get("so_that") or "").strip().lower()
        if so.startswith("so that "):
            warns.append(f"{nid}: `so_that` already starts with 'so that' — the renderer adds it")
    return problems, warns


def _names(dirpath, suffixes):
    if not dirpath.is_dir():
        return []
    return sorted(p.name for p in dirpath.iterdir() if p.suffix in suffixes and p.is_file())


def environment_baseline(root, manifest=None, cases=None, model_id=None):
    """The canonical setup record (D8). Flat keys kept for older consumers
    (`git_sha_short`, `git_dirty`, `operator`, `skills`, `hooks_installed`,
    `model_id`, `python`, `platform`); the grouped keys carry the full
    record: tooling, python_packages, connections, isolation."""
    manifest = manifest or {}
    cases = cases or []
    base = git_baseline(root)
    skills = skill_versions(root)
    model = model_id or os.environ.get("CLAUDE_MODEL") or None
    required = {"git", "python3"}
    for case in cases:
        required.update(case.get("requires", []))
        for tok in case.get("cmd", [])[:1]:
            if "/" not in tok:
                required.add(tok)
    env_unset, env_set = set(), set()
    for case in cases:
        env_unset.update(case.get("env_unset", []))
        env_set.update((case.get("env") or {}).keys())
    project_yml = _read_project_yml(root)
    base.update({
        "python": sys.version.split()[0],
        "python_executable": sys.executable,
        "platform": sys.platform,
        "architecture": platform_mod.machine(),
        "operator": operator_info(root),
        "harness_version": harness_version(),
        "model_id": model,
        "model_captured": bool(model),
        "hooks_installed": _names(root / ".claude" / "hooks", (".sh", ".py")),
        "agents_installed": _names(root / ".claude" / "agents", (".md",)),
        "rules_loaded": _names(root / ".claude" / "rules", (".md",)),
        "skills": skills,
        "skill_version_mismatches": sorted(
            name for name, e in skills.items() if e.get("version_mismatch")),
        "tooling": {name: probe_binary(name) for name in sorted(required)},
        "python_packages": probe_python_packages(root),
        "connections": {
            "declared": manifest.get("connections") or {},
            "mcp_servers": _mcp_servers_configured(root, project_yml),
            "endpoints": probe_connections(root, manifest, project_yml),
        },
        "isolation": {
            "env_unset": sorted(env_unset),
            "env_set_keys": sorted(env_set),
            "cwd": str(root),
            "socket_guard": "owned by each suite's conftest (unit/mocked tiers block sockets; live tier allows) — not enforced by the runner",
        },
    })
    return base


def execute_case(case, root, connections=None):
    case_id = case.get("id", "TC-??")
    result = {
        "id": case_id,
        "title": case.get("title", case_id),
        "wun": case.get("wun", []),
        "uut": case.get("uut", []),
        "uut_versions": {},
        "endpoint": case.get("endpoint") or "unspecified",
        "connection": case.get("connection"),
        "cmd": " ".join(case.get("cmd", [])),
        "status": "ERROR",
        "exit_code": None,
        "duration_s": 0.0,
        "reason": None,
        "output_tail": "",
        "log": None,
        "_output_full": "",
        "_started": utc_now(),
    }
    if result["endpoint"] not in ("none", "mocked", "live", "unspecified"):
        result.update(status="ERROR",
                      reason=f"unknown endpoint tier {result['endpoint']!r} (expected none|mocked|live)")
        return result
    if result["endpoint"] == "live":
        conn = case.get("connection")
        declared = (connections or {}).get(conn) if conn else None
        if conn and declared in (None, "none", "None", False):
            result.update(
                status="NOT-APPLICABLE",
                reason=f"no live {conn} connection in this deployment "
                       f"(manifest connections.{conn}: {declared if declared is not None else 'undeclared'})")
            return result
    for binary in case.get("requires", []):
        if shutil.which(binary) is None:
            result.update(status="SKIPPED", reason=f"required binary not installed: {binary}")
            return result
    env = dict(os.environ)
    for var in case.get("env_unset", []):
        env.pop(var, None)
    env.update({k: str(v) for k, v in (case.get("env") or {}).items()})

    code, output, duration, err = run_cmd(
        case.get("cmd", []), root / case.get("cwd", "."), case.get("timeout", 600), env
    )
    clean = ANSI_RE.sub("", output)
    result.update(
        exit_code=code,
        duration_s=round(duration, 2),
        output_tail=clean[-OUTPUT_TAIL:],
        _output_full=clean,
    )
    if err is not None:
        result.update(status="ERROR", reason=err)
        return result

    pass_pat, fail_pat = case.get("pass_pattern"), case.get("fail_pattern")
    if fail_pat and re.search(fail_pat, clean):
        result.update(status="FAIL", reason=f"fail_pattern matched: {fail_pat}")
    elif pass_pat:
        if re.search(pass_pat, clean) and code == 0:
            result["status"] = "PASS"
        else:
            result.update(status="FAIL", reason=f"pass_pattern not matched: {pass_pat}"
                          if code == 0 else f"exit code {code}")
    else:
        result["status"] = "PASS" if code == 0 else "FAIL"
        if code != 0:
            result["reason"] = f"exit code {code}"
    return result


def detect_source(case, root):
    """The test artifact a case actually executes. Prefers test-looking paths
    (a `/tests` dir or a script) among the cmd tokens; skips arguments to
    environment flags like `--project`, which point at a runtime env, not the
    test under execution."""
    cmd = case.get("cmd", [])
    candidates = []
    for i, tok in enumerate(cmd):
        if "/" not in tok or tok.startswith("-"):
            continue
        if i > 0 and cmd[i - 1] in ("--project", "--root", "--manifest", "--directory"):
            continue
        if (root / tok).exists():
            candidates.append(tok)
    for tok in candidates:
        if "/tests" in tok or tok.endswith((".sh", ".py")):
            return tok
    return candidates[0] if candidates else None


def sha256_file(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pin_test_artifacts(run_dir, case_id, source, root):
    """Copy the test artifact(s) the case executed into the run's evidence
    folder (results/<run-id>/pinned/<TC-ID>/) so this exact version stays
    reviewable after the skill under test evolves. Returns the repo-relative
    pinned path plus a sha256 manifest of every pinned file."""
    if not source:
        return None, []
    src = root / source
    dest_root = run_dir / "pinned" / case_id
    try:
        if src.is_dir():
            shutil.copytree(src, dest_root / src.name, dirs_exist_ok=True,
                            ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store"))
        else:
            dest_root.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest_root / src.name)
    except OSError as exc:
        print(f"  !! could not pin test artifacts for {case_id}: {exc}", file=sys.stderr)
        return None, []
    files = [{"path": str(f.relative_to(root)), "sha256": sha256_file(f)}
             for f in sorted(dest_root.rglob("*")) if f.is_file()]
    return str(dest_root.relative_to(root)), files


def write_evidence_log(run_dir, run_id, case, result, operator=None, invoked_via="cli", tooling=None):
    """Persist the case's full execution transcript as the evidence of record:
    an execution-statement header (what ran, where, with which env changes,
    when, how it exited, how it was judged) followed by the complete captured
    output. One file per case under results/<run-id>/."""
    log_path = run_dir / f"{result['id']}.log"
    judged_by = []
    if case.get("pass_pattern"):
        judged_by.append(f"pass_pattern={case['pass_pattern']!r}")
    if case.get("fail_pattern"):
        judged_by.append(f"fail_pattern={case['fail_pattern']!r}")
    judged_by.append("exit code")
    uut_line = ", ".join(
        f"{u}@{result['uut_versions'][u]}" if u in result.get("uut_versions", {}) else u
        for u in result.get("uut", [])
    ) or "—"
    operator = operator or {}
    tooling = tooling or {}
    tooling_line = "; ".join(
        f"{b}={((tooling.get(b) or {}).get('version') or (tooling.get(b) or {}).get('path') or 'missing')}"
        for b in case.get("requires", []) if b in tooling)
    op_line = " ".join(filter(None, [
        operator.get("git_user"),
        f"<{operator['git_email']}>" if operator.get("git_email") else None,
        f"({operator['os_user']}@{operator.get('hostname', '?')})" if operator.get("os_user") else None,
    ])) or "—"
    header = [
        "==== workbench-validation evidence log ====",
        f"run_id:      {run_id}",
        f"run by:      {op_line} · invoked via {invoked_via}",
        f"case:        {result['id']} — {result['title']}",
        f"purpose:     {case.get('description', '—')}",
        f"approach:    {case.get('approach', '—')}",
        f"UUT:         {uut_line}",
        f"user needs:  {', '.join(result.get('wun', [])) or '—'}",
        f"endpoint:    {result.get('endpoint', 'unspecified')}"
        + (f" (connection: {result['connection']})" if result.get("connection") else ""),
        f"test source: {result.get('source') or '—'}"
        + (f" (pinned copy: {result['pinned']})" if result.get("pinned") else ""),
        f"command:     {result['cmd']}",
        f"cwd:         {case.get('cwd', '.')}",
        f"env_unset:   {', '.join(case.get('env_unset', [])) or '—'}",
        f"env_set:     {', '.join(sorted((case.get('env') or {}).keys())) or '—'}",
        f"requires:    {', '.join(case.get('requires', [])) or '—'}",
        f"tooling:     {tooling_line or '—'}",
        f"timeout_s:   {case.get('timeout', 600)}",
        f"started:     {result.get('_started', '?')} (UTC)",
        f"exit_code:   {result['exit_code']}",
        f"duration_s:  {result['duration_s']}",
        f"judged by:   {'; '.join(judged_by)}",
        f"status:      {result['status']}"
        + (f" ({result['reason']})" if result.get("reason") else ""),
        "==== captured output — stdout+stderr merged, ANSI escapes stripped ====",
        "",
    ]
    body = result.get("_output_full", "") or "(no output captured)"
    try:
        log_path.write_text("\n".join(header) + body + "\n", encoding="utf-8")
        return log_path
    except OSError as exc:
        print(f"  !! could not write evidence log for {result['id']}: {exc}", file=sys.stderr)
        return None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="repo root")
    parser.add_argument("--manifest", default=None, help="path to validation.yml (relative to root)")
    parser.add_argument("--only", default=None, help="comma-separated TC ids to run")
    parser.add_argument("--render", action="store_true",
                        help="also render the report + console sidecar after the run")
    parser.add_argument("--invoked-via", default="cli", dest="invoked_via",
                        help="how the run was initiated (cli | console) — recorded in the setup record")
    parser.add_argument("--model-id", default=None, dest="model_id",
                        help="identifier of the model operating the workbench for this run "
                             "(falls back to $CLAUDE_MODEL; recorded as 'not captured' when absent)")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    manifest_path = root / (args.manifest or DEFAULT_MANIFEST)
    if not manifest_path.is_file():
        sys.exit(f"Manifest not found: {manifest_path}")
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))

    # Need-format contract (manifest schema >= 1.2): every need is a user story
    # composed from role / need / so_that. Missing fields are an error on 1.2+
    # manifests and a warning on older ones; double wording is a warning.
    need_problems, need_warnings = lint_needs(manifest.get("user_needs", []))
    schema = str(manifest.get("schema_version", "1.0"))
    if need_problems and _schema_at_least(schema, "1.2"):
        sys.exit("Manifest user_needs do not meet the need-format contract:\n  - "
                 + "\n  - ".join(need_problems))

    cases = manifest.get("test_cases", [])
    if args.only:
        wanted = {tc.strip() for tc in args.only.split(",")}
        cases = [c for c in cases if c.get("id") in wanted]

    started = utc_now()
    t0 = time.monotonic()
    run_id = datetime.now(timezone.utc).strftime("run-%Y%m%dT%H%M%SZ")
    results_dir = root / manifest.get("results_dir", "tools/workbench-validation/results")
    run_dir = results_dir / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    # Baseline captured up front so each case's UUT(s) can be pinned to the
    # exact version they were exercised at (UUT = unit under test — the
    # workbench component(s) the case actually runs against).
    env_base = environment_baseline(root, manifest, cases, model_id=args.model_id)
    connections = manifest.get("connections") or {}
    warnings = []
    if env_base.get("git_dirty") and not args.only:
        warnings.append(
            f"working tree dirty ({env_base.get('git_dirty_count', '?')} files) — this run "
            "cannot serve as a run of record; commit first and re-run")
    if not env_base.get("model_captured"):
        warnings.append("model identifier not captured — pass --model-id (or set $CLAUDE_MODEL); "
                        "a model change is a revalidation trigger and cannot be detected otherwise")
    if env_base.get("skill_version_mismatches"):
        warnings.append("skill version pin ambiguous (frontmatter != VERSION): "
                        + ", ".join(env_base["skill_version_mismatches"]))
    for w in need_problems if not _schema_at_least(schema, "1.2") else []:
        warnings.append("need-format: " + w)
    for w in need_warnings:
        warnings.append("need-format: " + w)
    missing_tier = [c.get("id") for c in cases if not c.get("endpoint")]
    if missing_tier:
        warnings.append("cases without an `endpoint:` tier (none|mocked|live): " + ", ".join(missing_tier))
    for w in warnings:
        print(f"!! WARNING: {w}", file=sys.stderr, flush=True)

    def uut_version(name):
        entry = env_base["skills"].get(name) or {}
        return entry.get("version") or entry.get("version_file")

    # Pin the manifest itself — the exact test-case definitions this run used.
    pinned_manifest = None
    try:
        shutil.copy2(manifest_path, run_dir / manifest_path.name)
        pinned_manifest = {
            "path": str((run_dir / manifest_path.name).relative_to(root)),
            "sha256": sha256_file(manifest_path),
        }
    except OSError as exc:
        print(f"  !! could not pin manifest: {exc}", file=sys.stderr)

    results = []
    for case in cases:
        print(f"[{case.get('id')}] {case.get('title', '')} ...", flush=True)
        res = execute_case(case, root, connections)
        res["uut_versions"] = {u: v for u in res["uut"]
                               if (v := uut_version(u)) is not None}
        res["source"] = detect_source(case, root)
        res["pinned"], res["pinned_files"] = pin_test_artifacts(
            run_dir, res["id"], res["source"], root)
        log_path = write_evidence_log(run_dir, run_id, case, res,
                                      operator=env_base.get("operator"),
                                      invoked_via=args.invoked_via,
                                      tooling=env_base.get("tooling"))
        res["log"] = str(log_path.relative_to(root)) if log_path else None
        res.pop("_output_full", None)
        res.pop("_started", None)
        print(f"  -> {res['status']}"
              + (f" ({res['reason']})" if res.get("reason") else "")
              + f"  [{res['duration_s']}s]", flush=True)
        results.append(res)

    counts = {}
    for res in results:
        counts[res["status"]] = counts.get(res["status"], 0) + 1
    run = {
        "schema_version": "1.1",
        "run_id": run_id,
        "started": started,
        "finished": utc_now(),
        "duration_s": round(time.monotonic() - t0, 1),
        "manifest": str(manifest_path.relative_to(root)),
        "pinned_manifest": pinned_manifest,
        "invoked_via": args.invoked_via,
        "partial": bool(args.only),
        "warnings": warnings,
        "connections": connections,
        "environment": env_base,
        "summary": counts,
        "cases": results,
    }

    run_file = results_dir / f"{run['run_id']}.json"
    run_file.write_text(json.dumps(run, indent=2) + "\n", encoding="utf-8")
    (results_dir / "latest.json").write_text(json.dumps(run, indent=2) + "\n", encoding="utf-8")

    total = len(results)
    print(f"\n{run['run_id']}: {counts.get('PASS', 0)}/{total} PASS, "
          f"{counts.get('FAIL', 0)} FAIL, {counts.get('SKIPPED', 0)} SKIPPED, "
          f"{counts.get('NOT-APPLICABLE', 0)} NOT-APPLICABLE, "
          f"{counts.get('ERROR', 0)} ERROR -> {run_file}")

    if args.render:
        render = Path(__file__).parent / "render_report.py"
        subprocess.run([sys.executable, str(render), "--root", str(root),
                        "--manifest", str(manifest_path.relative_to(root))], check=True)

    sys.exit(1 if counts.get("FAIL", 0) or counts.get("ERROR", 0) else 0)


if __name__ == "__main__":
    main()
