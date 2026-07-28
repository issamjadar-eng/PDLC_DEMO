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
  ERROR   - timeout or launcher exception

Exit code: 0 if no FAIL/ERROR cases, 1 otherwise (CI-gate friendly).

Usage:
  python3 run_validation.py --root <repo_root> [--manifest <path>]
                            [--only TC-01,TC-02] [--render]
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
    return {
        "git_sha": g("rev-parse", "HEAD"),
        "git_sha_short": g("rev-parse", "--short", "HEAD"),
        "git_branch": g("rev-parse", "--abbrev-ref", "HEAD"),
        "git_dirty": bool(g("status", "--porcelain")),
    }


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
            head = skill_md.read_text(encoding="utf-8", errors="replace")[:2000]
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
        versions[skill_dir.name] = entry
    return versions


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


def environment_baseline(root):
    base = git_baseline(root)
    base.update({
        "python": sys.version.split()[0],
        "platform": sys.platform,
        "operator": operator_info(root),
        "model_id": os.environ.get("CLAUDE_MODEL") or None,
        "hooks_installed": sorted(
            p.name for p in (root / ".claude" / "hooks").glob("*")
            if p.suffix in (".sh", ".py")
        ) if (root / ".claude" / "hooks").is_dir() else [],
        "skills": skill_versions(root),
    })
    return base


def execute_case(case, root):
    case_id = case.get("id", "TC-??")
    result = {
        "id": case_id,
        "title": case.get("title", case_id),
        "wun": case.get("wun", []),
        "uut": case.get("uut", []),
        "uut_versions": {},
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


def write_evidence_log(run_dir, run_id, case, result, operator=None, invoked_via="cli"):
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
        f"test source: {result.get('source') or '—'}"
        + (f" (pinned copy: {result['pinned']})" if result.get("pinned") else ""),
        f"command:     {result['cmd']}",
        f"cwd:         {case.get('cwd', '.')}",
        f"env_unset:   {', '.join(case.get('env_unset', [])) or '—'}",
        f"env_set:     {', '.join(sorted((case.get('env') or {}).keys())) or '—'}",
        f"requires:    {', '.join(case.get('requires', [])) or '—'}",
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
    args = parser.parse_args()

    root = Path(args.root).resolve()
    manifest_path = root / (args.manifest or DEFAULT_MANIFEST)
    if not manifest_path.is_file():
        sys.exit(f"Manifest not found: {manifest_path}")
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))

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
    env_base = environment_baseline(root)

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
        res = execute_case(case, root)
        res["uut_versions"] = {u: v for u in res["uut"]
                               if (v := uut_version(u)) is not None}
        res["source"] = detect_source(case, root)
        res["pinned"], res["pinned_files"] = pin_test_artifacts(
            run_dir, res["id"], res["source"], root)
        log_path = write_evidence_log(run_dir, run_id, case, res,
                                      operator=env_base.get("operator"),
                                      invoked_via=args.invoked_via)
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
        "schema_version": "1.0",
        "run_id": run_id,
        "started": started,
        "finished": utc_now(),
        "duration_s": round(time.monotonic() - t0, 1),
        "manifest": str(manifest_path.relative_to(root)),
        "pinned_manifest": pinned_manifest,
        "invoked_via": args.invoked_via,
        "partial": bool(args.only),
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
          f"{counts.get('ERROR', 0)} ERROR -> {run_file}")

    if args.render:
        render = Path(__file__).parent / "render_report.py"
        subprocess.run([sys.executable, str(render), "--root", str(root),
                        "--manifest", str(manifest_path.relative_to(root))], check=True)

    sys.exit(1 if counts.get("FAIL", 0) or counts.get("ERROR", 0) else 0)


if __name__ == "__main__":
    main()
