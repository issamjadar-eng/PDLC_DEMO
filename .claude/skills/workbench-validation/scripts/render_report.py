#!/usr/bin/env python3
"""Workbench validation report + console sidecar renderer.

Joins the validation manifest (user needs + test-case catalog) with the most
recent run results (results_dir/latest.json, or --run <file>) and derives:

  1. The single validation report markdown (needs x tests x results ->
     per-need verdict + fitness-for-use conclusion + known anomalies).
  2. The console sidecar JSON consumed by the project console's
     Settings -> Workbench Validation sub-section.

Per-need verdicts:
  PASS            all mapped test cases passed
  FAIL            any mapped test case failed or errored
  PARTIAL         some mapped test cases were skipped (rest passed)
  NO-EVIDENCE     coverage declared `tests` but no case maps to the need
  PROCESS-CONTROL need is assured by named process controls, not scripts
  EXPLORATORY     need is assured by documented exploratory/human review

Usage:
  python3 render_report.py --root <repo_root> [--manifest <path>] [--run <results-json>]
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("PyYAML is required (python3 -m pip install pyyaml, or run via `uv run --with pyyaml`).")

DEFAULT_MANIFEST = "docs/project/workbench-validation/validation.yml"

LLM_LIMITATION = (
    "LLM-driven skill behavior (content generation, judgment, advisory output) is "
    "**not repeatably testable** and is deliberately excluded from scripted pass/fail "
    "claims in this report. Those needs are assured through process controls — "
    "mandatory human review before content enters the controlled record, deterministic "
    "gates (hooks, lints, renderers) wrapped around the non-deterministic core, "
    "grounding rules, and the git/PR audit trail — and are labeled PROCESS-CONTROL or "
    "EXPLORATORY, never PASS. A change of the underlying model is a first-class "
    "revalidation trigger because it changes tool behavior with zero repository diff."
)

DEFAULT_REVALIDATION_TRIGGERS = [
    "Skill/agent/hook file change (skill-tree git SHA moves) — re-run affected cases",
    "Underlying model or agent-platform version change — re-run full suite + exploratory review of Tier-1 LLM paths",
    "project.yml security/config change — re-run posture and gate cases",
    "Intended-use change (new action, new output destination) — revisit the need register",
    "Periodic: per internal-audit cycle",
]


def need_verdict(need, case_index):
    coverage = need.get("coverage", "tests")
    if coverage == "process-control":
        return "PROCESS-CONTROL"
    if coverage == "exploratory":
        return "EXPLORATORY"
    mapped = [case_index[cid] for cid in need.get("_tests", []) if cid in case_index]
    if not mapped:
        return "NO-EVIDENCE"
    statuses = {c["status"] for c in mapped}
    if statuses & {"FAIL", "ERROR"}:
        return "FAIL"
    if "SKIPPED" in statuses:
        return "PARTIAL"
    return "PASS"


def overall_verdict(needs):
    verdicts = {n["_verdict"] for n in needs}
    if "FAIL" in verdicts:
        return "FAIL"
    if verdicts & {"PARTIAL", "NO-EVIDENCE"}:
        return "PARTIAL"
    return "PASS"


def md_escape(text):
    return str(text).replace("|", "\\|").replace("\n", " ").strip()


def manifest_case_meta(manifest, root):
    """Reviewer-facing metadata per test case, derived from the manifest:
    plain-language description/approach, the judgment rule, and the `source`
    path a TC id can hyperlink to — the first existing repo path found in the
    case's cmd (the actual test artifact), falling back to the manifest itself
    (the case definition) e.g. for inline one-liners."""
    meta = {}
    manifest_rel = manifest.get("_self_rel", "docs/project/workbench-validation/validation.yml")
    for case in manifest.get("test_cases", []):
        cmd = case.get("cmd", [])
        candidates = []
        for i, tok in enumerate(cmd):
            if "/" not in tok or tok.startswith("-"):
                continue
            if i > 0 and cmd[i - 1] in ("--project", "--root", "--manifest", "--directory"):
                continue
            if (root / tok).exists():
                candidates.append(tok)
        source = next((tok for tok in candidates
                       if "/tests" in tok or tok.endswith((".sh", ".py"))),
                      candidates[0] if candidates else None)
        judged = []
        if case.get("pass_pattern"):
            judged.append(f"output must contain \"{case['pass_pattern']}\"")
        if case.get("fail_pattern"):
            judged.append(f"output must not contain \"{case['fail_pattern']}\"")
        judged.append("exit code 0")
        meta[case.get("id")] = {
            "description": case.get("description"),
            "approach": case.get("approach"),
            "source": source or manifest_rel,
            "judged_by": " and ".join(judged),
        }
    return meta


def _report_rel_link(log_rel, manifest):
    """Repo-relative log path -> link relative to the report's own directory."""
    import os
    if not log_rel:
        return ""
    report_dir = str(Path(manifest.get("report", {}).get(
        "output", "tools/workbench-validation/validation-report.md")).parent)
    return os.path.relpath(log_rel, report_dir)


def build_report(manifest, run, needs, case_index, verdict, root, case_meta=None):
    case_meta = case_meta or {}
    env = run.get("environment", {})
    title = manifest.get("report", {}).get("title", "Workbench Validation Report")
    counts = run.get("summary", {})
    lines = []
    add = lines.append

    add(f"# {title}")
    add("")
    banner = manifest.get("banner")
    if banner:
        add(banner)
        add("")
    add(f"**Run**: `{run.get('run_id')}` · started {run.get('started')} · "
        f"{run.get('duration_s', '?')}s · overall verdict: **{verdict}**")
    if run.get("partial"):
        add("")
        add("> ⚠️ This was a **partial run** (`--only`); the report does not reflect the full manifest.")
    add("")
    add("_Generated by the `workbench-validation` skill — do not hand-edit; "
        "re-run the validation to refresh._")
    add("")

    add("## 1. Validation setup record — configuration under test, who, when")
    add("")
    op = env.get("operator") or {}
    op_line = " ".join(filter(None, [
        op.get("git_user"),
        f"<{op['git_email']}>" if op.get("git_email") else None,
        f"({op['os_user']}@{op.get('hostname', '?')})" if op.get("os_user") else None,
    ])) or "_not recorded_"
    add("| Item | Value |")
    add("|---|---|")
    add(f"| Object under validation | AI workbench: `.claude/` skills, agents, hooks, scripts, rules |")
    add(f"| Configuration under test | repo commit `{env.get('git_sha_short', '?')}` "
        f"(`{env.get('git_branch', '?')}`)"
        f"{' — **working tree dirty**' if env.get('git_dirty') else ''}; "
        f"{len(env.get('skills', {}))} skills, {len(env.get('hooks_installed', []))} hooks "
        f"(per-skill versions in the run JSON) |")
    add(f"| Run by | {op_line} |")
    add(f"| Invoked via | {run.get('invoked_via', 'cli')} |")
    add(f"| When | started {run.get('started')} · finished {run.get('finished')} "
        f"({run.get('duration_s', '?')}s) |")
    add(f"| Host / OS | {op.get('os') or env.get('platform', '?')} · Python {env.get('python', '?')} |")
    add(f"| Model identifier | {env.get('model_id') or '_not captured at run time — record at review_'} |")
    add(f"| Results evidence | `{manifest.get('results_dir')}/{run.get('run_id')}.json` |")
    pm = run.get("pinned_manifest") or {}
    add(f"| Pinned test-case definitions | "
        + (f"`{pm['path']}` (sha256 `{pm['sha256'][:12]}…`)" if pm.get("path") else "_not pinned_")
        + " |")
    add(f"| Pinned test artifacts | `{manifest.get('results_dir')}/{run.get('run_id')}/pinned/` — "
        f"per-case copies of the exact test source exercised, with sha256 manifest in the run JSON |")
    add("")

    add("## 2. User needs & intended use")
    add("")
    plan = manifest.get("plan")
    if plan:
        add(f"Intended-use statements, risk assessment, and the assurance model are "
            f"defined in the validation plan: `{plan}`. Each need is stated from a "
            f"role's perspective — the outcome that role requires, independent of how "
            f"the workbench implements it. The table joins each need to its assurance "
            f"evidence from this run.")
        add("")
    add("| ID | Role | Need | Tier | Coverage | Verdict | Evidence |")
    add("|---|---|---|---|---|---|---|")
    for need in needs:
        evidence = ", ".join(f"`{tc}`" for tc in need.get("_tests", [])) or (
            "; ".join(need.get("process_controls", [])) or "—")
        add(f"| {need['id']} | {need.get('role', '—')} "
            f"| {md_escape(need.get('need', ''))} | {need.get('tier', '?')} "
            f"| {need.get('coverage', 'tests')} "
            f"| **{need['_verdict']}** | {md_escape(evidence)} |")
    add("")

    add("## 3. Test cases, results & evidence")
    add("")
    add(f"Summary: **{counts.get('PASS', 0)} PASS / {counts.get('FAIL', 0)} FAIL / "
        f"{counts.get('SKIPPED', 0)} SKIPPED / {counts.get('ERROR', 0)} ERROR** "
        f"across {len(run.get('cases', []))} cases.")
    add("")
    add("Each case's **evidence of record** is its full execution log — command, "
        "working directory, environment changes, timestamps, exit code, judgment "
        "rule, and the complete captured output — written per run under "
        f"`{manifest.get('results_dir')}/{run.get('run_id')}/`.")
    add("")
    add("| ID | Test case | UUT (version exercised) | Needs | Status | Duration | Evidence log | Detail |")
    add("|---|---|---|---|---|---|---|---|")
    for case in run.get("cases", []):
        detail = case.get("reason") or ""
        log = f"[`{case['id']}.log`]({_report_rel_link(case.get('log'), manifest)})" \
            if case.get("log") else "—"
        versions = case.get("uut_versions") or {}
        uut = ", ".join(f"`{u}@{versions[u]}`" if u in versions else f"`{u}`"
                        for u in case.get("uut", [])) or "—"
        add(f"| {case['id']} | {md_escape(case['title'])} | {uut} | "
            f"{', '.join(case.get('wun', [])) or '—'} | **{case['status']}** "
            f"| {case.get('duration_s', '?')}s | {log} | {md_escape(detail) or '—'} |")
    add("")

    add("### What each test case checks (for reviewers)")
    add("")
    add("Written for a reviewer who is not a toolchain specialist: what the case "
        "checks, how the check works, and where the actual test lives.")
    add("")
    for case in run.get("cases", []):
        meta = case_meta.get(case["id"], {})
        source = case.get("source") or meta.get("source")
        links = [f"[source]({_report_rel_link(source, manifest)})"]
        if case.get("pinned"):
            links.append(f"[pinned copy]({_report_rel_link(case['pinned'], manifest)})")
        add(f"**{case['id']} — {case['title']}** ({', '.join(links)})")
        add("")
        if meta.get("description"):
            add(meta["description"])
        if meta.get("approach"):
            add("")
            add(f"_How it's tested:_ {meta['approach']}")
        if meta.get("judged_by"):
            add("")
            add(f"_Pass rule:_ {meta['judged_by']}.")
        add("")

    add("## 4. Known anomalies & limitations")
    add("")
    anomalies = []
    for case in run.get("cases", []):
        if case["status"] in ("FAIL", "ERROR"):
            anomalies.append(f"**{case['id']} {case['status']}** — {case['title']}: "
                             f"{case.get('reason') or 'see run JSON output_tail'}")
        elif case["status"] == "SKIPPED":
            anomalies.append(f"**{case['id']} SKIPPED** — {case['title']}: {case.get('reason')}")
    for item in manifest.get("known_anomalies", []):
        anomalies.append(item)
    if anomalies:
        for item in anomalies:
            add(f"- {item}")
    else:
        add("- None observed in this run.")
    add("")
    add(f"**LLM non-determinism.** {LLM_LIMITATION}")
    add("")

    add("## 5. Conclusion")
    add("")
    if verdict == "PASS":
        add("All user needs with executable evidence passed their mapped test cases; "
            "process-control and exploratory needs are assured as described in the plan. "
            "This run **would support a fitness-for-intended-use determination** for the "
            "workbench configuration baselined in §1, within the intended uses and "
            "limitations stated in the validation plan.")
    elif verdict == "PARTIAL":
        add("Executable evidence is incomplete (skipped cases or needs without mapped "
            "evidence). This run **would support only a qualified fitness-for-use "
            "determination**; close the gaps listed in §4 before relying on the "
            "uncovered needs.")
    else:
        add("One or more test cases failed. This run **does not support a "
            "fitness-for-use determination** for the affected needs; resolve the "
            "anomalies in §4 and re-run.")
    note = manifest.get("conclusion_note")
    if note:
        add("")
        add(note)
    add("")

    add("## 6. Revalidation triggers")
    add("")
    for trigger in manifest.get("revalidation_triggers", DEFAULT_REVALIDATION_TRIGGERS):
        add(f"- {trigger}")
    add("")
    return "\n".join(lines) + "\n"


def build_sidecar(manifest, run, needs, verdict, case_meta=None):
    case_meta = case_meta or {}
    env = run.get("environment", {})
    need_counts = {}
    for need in needs:
        key = need["_verdict"].lower().replace("-", "_")
        need_counts[key] = need_counts.get(key, 0) + 1
    return {
        "schema_version": "1.0",
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "title": manifest.get("report", {}).get("title", "Workbench Validation"),
        "banner": manifest.get("banner"),
        "plan_path": manifest.get("plan"),
        "report_path": manifest.get("report", {}).get("output"),
        "manifest_path": run.get("manifest"),
        "run": {
            "run_id": run.get("run_id"),
            "started": run.get("started"),
            "finished": run.get("finished"),
            "duration_s": run.get("duration_s"),
            "partial": run.get("partial", False),
            "invoked_via": run.get("invoked_via", "cli"),
            "operator": env.get("operator") or {},
            "pinned_manifest": run.get("pinned_manifest"),
        },
        "baseline": {
            "git_sha_short": env.get("git_sha_short"),
            "git_branch": env.get("git_branch"),
            "git_dirty": env.get("git_dirty"),
            "skills_total": len(env.get("skills", {})),
            "hooks_total": len(env.get("hooks_installed", [])),
            "model_id": env.get("model_id"),
        },
        "summary": {
            "verdict": verdict,
            "needs": {"total": len(needs), **need_counts},
            "tests": {"total": len(run.get("cases", [])), **run.get("summary", {})},
        },
        "needs": [
            {
                "id": n["id"], "role": n.get("role"), "tier": n.get("tier"),
                "class": n.get("class"), "need": n.get("need"),
                "coverage": n.get("coverage", "tests"),
                "implemented_by": n.get("implemented_by"),
                "verdict": n["_verdict"], "tests": n.get("_tests", []),
                "process_controls": n.get("process_controls", []),
            }
            for n in needs
        ],
        "tests": [
            {
                "id": c["id"], "title": c["title"], "wun": c.get("wun", []),
                "uut": c.get("uut", []), "uut_versions": c.get("uut_versions", {}),
                "status": c["status"], "duration_s": c.get("duration_s"),
                "reason": c.get("reason"), "log": c.get("log"),
                "cmd": c.get("cmd"),
                "description": case_meta.get(c["id"], {}).get("description"),
                "approach": case_meta.get(c["id"], {}).get("approach"),
                "judged_by": case_meta.get(c["id"], {}).get("judged_by"),
                "source": c.get("source") or case_meta.get(c["id"], {}).get("source"),
                "pinned": c.get("pinned"),
            }
            for c in run.get("cases", [])
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--manifest", default=DEFAULT_MANIFEST)
    parser.add_argument("--run", default=None, help="results JSON (default: results_dir/latest.json)")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    manifest_path = root / args.manifest
    if not manifest_path.is_file():
        sys.exit(f"Manifest not found: {manifest_path}")
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    manifest["_self_rel"] = str(manifest_path.relative_to(root))
    case_meta = manifest_case_meta(manifest, root)

    results_dir = root / manifest.get("results_dir", "tools/workbench-validation/results")
    run_path = Path(args.run) if args.run else results_dir / "latest.json"
    if not run_path.is_absolute():
        run_path = root / run_path
    if not run_path.is_file():
        sys.exit(f"No run results found at {run_path} — run run_validation.py first.")
    run = json.loads(run_path.read_text(encoding="utf-8"))

    case_index = {c["id"]: c for c in run.get("cases", [])}
    # Map need -> test cases from the test_cases[].wun edges (single source of truth).
    needs = [dict(n) for n in manifest.get("user_needs", [])]
    for need in needs:
        need["_tests"] = [c["id"] for c in manifest.get("test_cases", [])
                          if need["id"] in c.get("wun", [])]
        need["_verdict"] = need_verdict(need, case_index)
    verdict = overall_verdict(needs)

    report_rel = manifest.get("report", {}).get(
        "output", "tools/workbench-validation/validation-report.md")
    report_path = root / report_rel
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        build_report(manifest, run, needs, case_index, verdict, root, case_meta),
        encoding="utf-8")

    sidecar_rel = manifest.get(
        "sidecar", "tools/workbench-validation/workbench-validation-index.json")
    sidecar_path = root / sidecar_rel
    sidecar_path.parent.mkdir(parents=True, exist_ok=True)
    sidecar_path.write_text(
        json.dumps(build_sidecar(manifest, run, needs, verdict, case_meta),
                   indent=2) + "\n", encoding="utf-8")

    print(f"Report:  {report_rel}")
    print(f"Sidecar: {sidecar_rel}")
    print(f"Overall verdict: {verdict}")


if __name__ == "__main__":
    main()
