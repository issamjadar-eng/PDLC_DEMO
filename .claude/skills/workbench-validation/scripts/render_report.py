#!/usr/bin/env python3
"""Workbench validation report + console sidecar renderer.

Joins the validation manifest (user needs + test-case catalog) with the most
recent run results (results_dir/latest.json, or --run <file>) and derives:

  1. The single validation report markdown (needs x tests x results ->
     per-need verdict + fitness-for-use conclusion + known anomalies).
  2. The console sidecar JSON consumed by the project console's
     Settings -> Workbench Validation sub-section.

Per-need verdicts (schema 2.0 — GxP-style, pass or fail only):
  PASS            every applicable mapped case passed
  FAIL            any applicable mapped case failed, errored, was skipped or
                  was not executed — or the need has no applicable case at
                  all ("no evidence"); the reason is stated beside the verdict
  NOT-APPLICABLE  every mapped case depends on something this deployment
                  declares absent (nothing to execute here, by declaration)

The evidence METHOD (scripted / protocol / inspection) and SCOPE (capability
fixtures shipped with the skill vs this deployment's content) are attributes of
the test case, never verdicts. NOT-APPLICABLE never lowers a verdict: a
declared absence is a fact about the instance, not a gap. Non-determinism of
the assistant is handled by protocols with acceptance criteria under a pinned
model, and stated as a limitation — it does not create a third verdict.

Revisions: every run is rendered as its own revision — `results/<run-id>/
validation-report.md` + `results/<run-id>/sidecar.json` — from that run's
PINNED manifest (`results/<run-id>/validation.yml`), and `results/index.json`
lists every run (newest first) for the console's revision drop-down. The
top-level report/sidecar always reflect the latest run. `--all-runs` backfills
every recorded run; a historical run's header says it was re-rendered by the
current renderer from its pinned data.

Usage:
  python3 render_report.py --root <repo_root> [--manifest <path>] [--run <results-json>]
                           [--all-runs] [--no-per-run]
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
    "Where a need's outcome is the assistant's judgment (content generation, "
    "citation verification, grounding), the behavior is not deterministic. This report "
    "does not create a third verdict for it: such needs are tested by **protocol** — a "
    "fixed challenge set with known expected outcomes, explicit acceptance criteria and "
    "repeat runs under a pinned model — and pass or fail like any other. Deterministic "
    "gates (hooks, lints, renderers) around the non-deterministic core are tested as "
    "scripted capability cases. A change of the underlying model is a first-class "
    "revalidation trigger because it changes tool behavior with zero repository diff; "
    "a protocol result is valid only for the model id recorded in its execution record."
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
        return "FAIL"
    applicable = [c for c in mapped if c["status"] != "NOT-APPLICABLE"]
    if not applicable:
        return "NOT-APPLICABLE"
    if all(c["status"] == "PASS" for c in applicable):
        return "PASS"
    return "FAIL"


def need_reason(need, case_index):
    """Why the verdict is what it is — one line a reviewer can act on."""
    mapped = [case_index[cid] for cid in need.get("_tests", []) if cid in case_index]
    if not mapped:
        return "no evidence — no test case maps to this need"
    applicable = [c for c in mapped if c["status"] != "NOT-APPLICABLE"]
    if not applicable:
        return "not applicable in this deployment: " + "; ".join(
            f"{c['id']} — {c.get('reason')}" for c in mapped)
    bad = [c for c in applicable if c["status"] != "PASS"]
    if not bad:
        na = [c for c in mapped if c["status"] == "NOT-APPLICABLE"]
        note = f"; {len(na)} case(s) not applicable here" if na else ""
        return f"all {len(applicable)} applicable case(s) passed{note}"
    return "; ".join(f"{c['id']} {c['status']}" + (f" ({c.get('reason')})" if c.get("reason") else "")
                     for c in bad)


TIER_RANK = {"live": 3, "mocked": 2, "none": 1, "unspecified": 0}
TIER_WORD = {"live": "live-verified", "mocked": "mock-verified",
             "none": "verified without external endpoints", "unspecified": "tier unspecified"}


def strongest_evidence(need, case_index):
    """Plain-language statement of the best evidence tier behind a need's
    verdict, and what was not exercised — the D7 honesty line."""
    mapped = [case_index[cid] for cid in need.get("_tests", []) if cid in case_index]
    if not mapped:
        return "no mapped test case"
    passed = [c for c in mapped if c["status"] == "PASS"]
    na = [c for c in mapped if c["status"] == "NOT-APPLICABLE"]
    best = max((c.get("endpoint", "unspecified") for c in passed),
               key=lambda t: TIER_RANK.get(t, 0), default=None)
    parts = []
    if best:
        scopes = sorted({c.get("scope", "?") for c in passed})
        methods = sorted({c.get("method", "?") for c in passed})
        parts.append(f"{TIER_WORD.get(best, best)} ({'/'.join(scopes)} scope, {'/'.join(methods)})")
    else:
        parts.append("no passing evidence")
    if na:
        conns = sorted({c.get("connection") or "endpoint" for c in na})
        parts.append(f"live {', '.join(conns)} not applicable in this deployment")
    elif best and best != "live" and any(c.get("endpoint") == "live" for c in mapped):
        parts.append("live case did not pass")
    return "; ".join(parts)


def need_statement(need):
    """The user story a need renders as, composed from its structured fields:
    'As a <role>, I need the workbench to <need>, so that <so_that>.'"""
    role = str(need.get("role") or "").strip() or "user"
    # Mid-sentence role: lower-case a capitalised first word unless it is an
    # acronym ("DHF author" stays, "Reviewer / approver" -> "reviewer / approver").
    if len(role) > 1 and role[0].isupper() and role[1].islower():
        role = role[0].lower() + role[1:]
    outcome = str(need.get("need") or "").strip().rstrip(".")
    purpose = str(need.get("so_that") or "").strip().rstrip(".")
    article = "an" if role[:1].lower() in "aeiou" else "a"
    sentence = f"As {article} {role}, I need the workbench to {outcome}"
    if purpose:
        sentence += f", so that {purpose}"
    return sentence + "."


def overall_verdict(needs):
    verdicts = {n["_verdict"] for n in needs}
    return "FAIL" if "FAIL" in verdicts else "PASS"


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


def environment_details(env, run):
    """§1 expandable full environment record (D8) — every field of the
    canonical `environment` block, grouped, rendered inside a collapsed
    <details> so the verdict stays readable and the record stays complete."""
    out = []
    add = out.append
    add("<details>")
    add("<summary><strong>Full environment record</strong> — what this run executed against "
        "(expand for the complete setup record)</summary>")
    add("")
    add("**Configuration under test**")
    add("")
    add("| Field | Value |")
    add("|---|---|")
    add(f"| Commit | `{env.get('git_sha', '?')}` on `{env.get('git_branch', '?')}` |")
    dirty = env.get("git_dirty_files") or []
    if env.get("git_dirty"):
        shown = ", ".join(f"`{md_escape(f)}`" for f in dirty[:25])
        more = f" … +{env.get('git_dirty_count', len(dirty)) - 25} more" if len(dirty) > 25 else ""
        add(f"| Working tree | **dirty** — {env.get('git_dirty_count', len(dirty))} file(s): {shown}{more} |")
    else:
        add("| Working tree | clean |")
    skills = env.get("skills") or {}
    mism = env.get("skill_version_mismatches") or []
    add(f"| Skills installed | {len(skills)}"
        + (f" — **version pin ambiguous** (frontmatter ≠ VERSION): {', '.join(f'`{m}`' for m in mism)}" if mism else "")
        + " |")
    add(f"| Hooks installed | {', '.join(f'`{h}`' for h in env.get('hooks_installed', [])) or '—'} |")
    add(f"| Agents installed | {len(env.get('agents_installed') or [])} |")
    add(f"| Rules loaded | {', '.join(f'`{r}`' for r in env.get('rules_loaded', [])) or '—'} |")
    add("")
    if skills:
        add("<details><summary>Per-skill versions exercised</summary>")
        add("")
        add("| Skill | Frontmatter version | VERSION file | Updated |")
        add("|---|---|---|---|")
        for name, e in sorted(skills.items()):
            flag = " ⚠️" if e.get("version_mismatch") else ""
            add(f"| `{name}` | {e.get('version') or '—'}{flag} | {e.get('version_file') or '—'} | {e.get('updated') or '—'} |")
        add("")
        add("</details>")
        add("")
    add("**Runtime**")
    add("")
    add("| Field | Value |")
    add("|---|---|")
    add(f"| Python | {env.get('python', '?')} (`{env.get('python_executable', '?')}`) |")
    op = env.get("operator") or {}
    add(f"| OS / architecture | {op.get('os') or env.get('platform', '?')} · {env.get('architecture', '?')} |")
    add(f"| Host / OS user | {op.get('hostname') or '?'} / {op.get('os_user') or '?'} |")
    add(f"| Harness version | {env.get('harness_version') or '_not captured_'} |")
    add(f"| Model identifier | {env.get('model_id') or '_not captured — pass --model-id_'} |")
    add("")
    add("**Tooling** — binaries the cases required, as resolved on this host")
    add("")
    add("| Binary | Resolved path | Version |")
    add("|---|---|---|")
    for name, t in sorted((env.get("tooling") or {}).items()):
        if t.get("missing"):
            add(f"| `{name}` | **missing** | — |")
        else:
            add(f"| `{name}` | `{t.get('path')}` | {md_escape(t.get('version') or '—')} |")
    pk = env.get("python_packages") or {}
    if pk:
        add("")
        add("Test-harness packages resolved by `uv`: "
            + ", ".join(f"`{k}` {v}" for k, v in pk.items()) + ".")
    add("")
    add("**Connections** — declared tiers, MCP servers, reachability")
    add("")
    conns = env.get("connections") or {}
    declared = conns.get("declared") or {}
    add("| Connection | Declared for this deployment | Base URL | Reachability at run start |")
    add("|---|---|---|---|")
    endpoints = conns.get("endpoints") or {}
    for name in sorted(set(declared) | set(endpoints)):
        e = endpoints.get(name) or {}
        add(f"| `{name}` | {declared.get(name, e.get('declared', '—'))} | "
            f"{('`' + e['base_url'] + '`') if e.get('base_url') else '—'} | {e.get('reachability') or '—'} |")
    if not (declared or endpoints):
        add("| — | no connections declared in the manifest | — | — |")
    mcp = conns.get("mcp_servers") or {}
    add("")
    add(f"MCP servers approved in `project.yml`: {', '.join(f'`{a}`' for a in mcp.get('approved', [])) or 'none'}; "
        f"configured: {', '.join(f'`{c}`' for c in mcp.get('configured', [])) or 'none'}.")
    add("")
    add("**Isolation**")
    add("")
    iso = env.get("isolation") or {}
    add(f"- Env vars stripped for cases: {', '.join(f'`{v}`' for v in iso.get('env_unset', [])) or 'none'}")
    add(f"- Env vars set for cases: {', '.join(f'`{v}`' for v in iso.get('env_set_keys', [])) or 'none'}")
    add(f"- Socket guard: {iso.get('socket_guard', '—')}")
    add(f"- Working directory: `{iso.get('cwd', '?')}`")
    add("")
    add("</details>")
    return out


def load_qms_coverage(manifest, root):
    """The QMS template coverage inventory written by a deployment case
    (default: tools/workbench-validation/qms-coverage.json). None when absent —
    the report then states that no inventory was produced in this run."""
    rel = manifest.get("qms_coverage", "tools/workbench-validation/qms-coverage.json")
    path = root / rel
    if not path.is_file():
        return None, rel
    try:
        return json.loads(path.read_text(encoding="utf-8")), rel
    except (OSError, json.JSONDecodeError) as exc:
        return {"_error": f"unreadable: {exc}"}, rel


def qms_coverage_section(cov, rel):
    """§3b — which imported QMS templates/forms have validation evidence, which
    are imported but unused, and which project doctypes have no template
    imported at all. A project acquires QMS content over time; this table is
    what tells a reviewer whether the validation kept up."""
    out = []
    add = out.append
    add("### QMS template coverage — what the imported QMS governs, and what has evidence")
    add("")
    if cov is None:
        add(f"_No QMS coverage inventory was produced in this run (expected at `{rel}`). "
            "Add a deployment case that runs the inventory script, or declare "
            "`deployment.content.qms_forms: false` if this instance has no QMS templates._")
        add("")
        return out
    if cov.get("_error"):
        add(f"_QMS coverage inventory at `{rel}` could not be read: {cov['_error']}_")
        add("")
        return out
    sm = cov.get("summary") or {}
    add(f"Registry: `{cov.get('registry', '?')}` · generated {cov.get('generated', '?')}. "
        f"**{sm.get('templates_total', 0)} templates/forms imported** — "
        f"{sm.get('templates_instantiated', 0)} instantiated by project documents, "
        f"{sm.get('templates_tested', 0)} exercised by the conformance check, "
        f"{sm.get('templates_unused', 0)} imported but not yet used (no project evidence); "
        f"{sm.get('procedures_total', 0)} procedures (SOP/WI) referenced; "
        f"**{sm.get('documents_governed', 0)} of {sm.get('documents_total', 0)} project documents governed by a template, "
        f"{sm.get('documents_without_template', 0)} with no template imported for their doctype.**")
    add("")
    templates = cov.get("templates") or []
    if templates:
        add("| Template / form | Type | Project documents | Conformance evidence | Pass / Fail | Status |")
        add("|---|---|---|---|---|---|")
        order = {"covered-failing": 0, "covered": 1, "unused": 2}
        for t in sorted(templates, key=lambda t: (order.get(t.get("status"), 9), t.get("id", ""))):
            tested = "tested" if t.get("tested") else "**not tested**"
            status = {"covered": "covered", "covered-failing": "**covered — failing**",
                      "unused": "_imported, unused — no project evidence_"}.get(t.get("status"), t.get("status", "?"))
            add(f"| `{t.get('id', '?')}` {md_escape(t.get('title') or '')} | {t.get('doc_type', '?')} "
                f"| {t.get('instances', 0)} | {tested} | {t.get('pass', 0)} / {t.get('fail', 0)} | {status} |")
        add("")
    procs = cov.get("procedures") or []
    if procs:
        add("Procedures referenced by project documents (govern process, not structure — no template test applies): "
            + ", ".join(f"`{p.get('id', '?')}` ({p.get('referenced_by', 0)})" for p in procs) + ".")
        add("")
    gaps = cov.get("documents_without_template") or []
    if gaps:
        by = {}
        for g in gaps:
            by.setdefault((g.get("doctype_hint") or "?", g.get("reason") or "?"), []).append(g.get("doc"))
        add("**QMS gaps — project doctypes with no imported template** (a finding for QMS import, not for the documents):")
        add("")
        add("| Doctype (folder) | Reason | Documents |")
        add("|---|---|---|")
        for (hint, reason), docs in sorted(by.items()):
            shown = ", ".join(f"`{Path(d).name}`" for d in docs[:6]) + (f" … +{len(docs) - 6}" if len(docs) > 6 else "")
            add(f"| `{hint}` | {reason} | {len(docs)}: {shown} |")
        add("")
    return out


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
    for w in run.get("warnings", []) or []:
        add(f"> ⚠️ {w}")
    if run.get("warnings"):
        add("")
    lines.extend(environment_details(env, run))
    add("")

    add("## 2. User needs & intended use")
    add("")
    plan = manifest.get("plan")
    if plan:
        add(f"Intended-use statements, risk assessment, and the assurance model are "
            f"defined in the validation plan: `{plan}`. Each need is a user story — "
            f"*As a role, I need the workbench to achieve an outcome, so that a purpose "
            f"is served* — composed from the manifest's `role` / `need` / `so_that` "
            f"fields; the outcome is what the role can observe, never how the workbench "
            f"implements it. The table joins each need to its assurance evidence from "
            f"this run.")
        add("")
    add("| ID | Need (user story) | Tier | Verdict | Why | Strongest evidence | Test cases |")
    add("|---|---|---|---|---|---|---|")
    for need in needs:
        cases = []
        for tc in need.get("_tests", []):
            c = case_index.get(tc) or {}
            cases.append(f"`{tc}` ({c.get('scope', '?')}/{c.get('method', '?')})")
        add(f"| {need['id']} "
            f"| {md_escape(need_statement(need))} | {need.get('tier', '?')} "
            f"| **{need['_verdict']}** | {md_escape(need.get('_reason', ''))} "
            f"| {md_escape(need.get('_strongest', ''))} | {md_escape(', '.join(cases) or '—')} |")
    add("")

    add("## 3. Test cases, results & evidence")
    add("")
    add(f"Summary: **{counts.get('PASS', 0)} PASS / {counts.get('FAIL', 0)} FAIL / "
        f"{counts.get('SKIPPED', 0)} SKIPPED / {counts.get('NOT-EXECUTED', 0)} NOT-EXECUTED / "
        f"{counts.get('NOT-APPLICABLE', 0)} NOT-APPLICABLE / {counts.get('ERROR', 0)} ERROR** "
        f"across {len(run.get('cases', []))} cases.")
    add("")
    add("**Scope.** *Capability* cases ship with a skill and run against the skill's own "
        "fixtures — they are portable and prove what the tool can do anywhere. *Deployment* "
        "cases run this deployed workbench against this instance's own content (its QMS "
        "documents, taxonomy, submission packages, corpus, connections) — they are the part a "
        "deployment authors for itself from the skill's guidance. A deployment case whose "
        "dependency this instance declares absent is **NOT-APPLICABLE** with its justification.")
    add("")
    add("**Method.** *scripted* — executed by the runner, judged by exit code/pattern; "
        "*protocol* / *inspection* — executed by an operator against a written protocol with "
        "acceptance criteria, judged from its execution record; a protocol with no record yet is "
        "**NOT-EXECUTED**, which fails its need (untested is not passed).")
    add("")
    dep = run.get("deployment") or {}
    if dep:
        add("**Deployment declaration** — what this instance has (drives NOT-APPLICABLE):")
        add("")
        add("| Dependency | Declared |")
        add("|---|---|")
        for group, vals in sorted(dep.items()):
            if isinstance(vals, dict):
                for k, v in sorted(vals.items()):
                    add(f"| `{group}.{k}` | {v} |")
            else:
                add(f"| `{group}` | {vals} |")
        add("")
    tiers = {}
    for c in run.get("cases", []):
        tiers[c.get("endpoint", "unspecified")] = tiers.get(c.get("endpoint", "unspecified"), 0) + 1
    add("**Evidence tiers.** Every case declares what it touched: `none` — no external "
        "system (pure logic, hooks, renderers); `mocked` — the real client code paths "
        "against a fake Jira/Confluence transport with canned payloads (hermetic, runs "
        "here); `live` — a real enterprise endpoint, executed only when this deployment "
        "declares the connection. A `live` case for a connection declared `none` is "
        "reported **NOT-APPLICABLE** — a statement about this deployment, not a gap — "
        "and never lowers a verdict. Where an integration runs through an MCP server the "
        "agent makes the call, not a script; those paths are covered by recorded live "
        "probes under `exploratory` coverage, never a scripted PASS. This run: "
        + ", ".join(f"{n} `{t}`" for t, n in sorted(tiers.items())) + ".")
    add("")
    add("Each case's **evidence of record** is its full execution log — command, "
        "working directory, environment changes, timestamps, exit code, judgment "
        "rule, and the complete captured output — written per run under "
        f"`{manifest.get('results_dir')}/{run.get('run_id')}/`.")
    add("")
    for scope_name, scope_label in (("capability", "Capability tests — portable, skill-shipped fixtures"),
                                    ("deployment", "Deployment tests — this instance's content"),
                                    ("unspecified", "Cases without a declared scope")):
        group = [c for c in run.get("cases", []) if c.get("scope", "unspecified") == scope_name]
        if not group:
            continue
        add(f"#### {scope_label}")
        add("")
        add("| ID | Test case | UUT (version exercised) | Needs | Method | Endpoint | Status | Duration | Evidence | Detail |")
        add("|---|---|---|---|---|---|---|---|---|---|")
        for case in group:
            detail = case.get("reason") or ""
            if case.get("execution_record"):
                log = f"[record]({_report_rel_link(case['execution_record']['path'], manifest)})"
            elif case.get("log"):
                log = f"[`{case['id']}.log`]({_report_rel_link(case.get('log'), manifest)})"
            else:
                log = "—"
            versions = case.get("uut_versions") or {}
            uut = ", ".join(f"`{u}@{versions[u]}`" if u in versions else f"`{u}`"
                            for u in case.get("uut", [])) or "—"
            ep = case.get("endpoint", "unspecified")
            ep = f"{ep} ({case['connection']})" if case.get("connection") else ep
            add(f"| {case['id']} | {md_escape(case['title'])} | {uut} | "
                f"{', '.join(case.get('wun', [])) or '—'} | {case.get('method', '?')} | `{ep}` | **{case['status']}** "
                f"| {case.get('duration_s', '?')}s | {log} | {md_escape(detail) or '—'} |")
        add("")

    cov, cov_rel = load_qms_coverage(manifest, root)
    lines.extend(qms_coverage_section(cov, cov_rel))

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

    add("## 4. Findings, open items & known anomalies")
    add("")
    failing_needs = [n for n in needs if n["_verdict"] == "FAIL"]
    if failing_needs:
        add("**Needs failing in this run** (each is a finding to close — build the missing "
            "check, execute the protocol, or fix the tool — never a label to apply):")
        add("")
        for n in failing_needs:
            add(f"- **{n['id']} FAIL** — {md_escape(n.get('_reason', ''))}")
        add("")
    anomalies = []
    for case in run.get("cases", []):
        if case["status"] in ("FAIL", "ERROR"):
            anomalies.append(f"**{case['id']} {case['status']}** — {case['title']}: "
                             f"{case.get('reason') or 'see run JSON output_tail'}")
        elif case["status"] == "SKIPPED":
            anomalies.append(f"**{case['id']} SKIPPED** — {case['title']}: {case.get('reason')}")
        elif case["status"] == "NOT-EXECUTED":
            anomalies.append(f"**{case['id']} NOT-EXECUTED** — {case['title']}: {case.get('reason')} "
                             f"(protocol: `{case.get('protocol')}`)")
    na = [c for c in run.get("cases", []) if c["status"] == "NOT-APPLICABLE"]
    if na:
        anomalies.append("**Not applicable in this deployment** (declared, not gaps): "
                         + "; ".join(f"{c['id']} — {c.get('reason')}" for c in na))
    for item in manifest.get("known_anomalies", []):
        anomalies.append(item)
    if anomalies:
        for item in anomalies:
            add(f"- {item}")
    else:
        add("- None observed in this run.")
    add("")
    add("### Limitations")
    add("")
    add(f"**Assistant non-determinism.** {LLM_LIMITATION}")
    add("")

    add("## 5. Conclusion")
    add("")
    if verdict == "PASS":
        add("Every applicable user need passed its mapped test cases (needs whose dependencies "
            "this deployment declares absent are recorded NOT-APPLICABLE with justification). "
            "This run **would support a fitness-for-intended-use determination** for the "
            "workbench configuration baselined in §1, within the intended uses and "
            "limitations stated in the validation plan.")
    else:
        add("One or more user needs FAIL — a mapped case failed, was not executed, or no "
            "case exists for the need. This run **does not support a fitness-for-use "
            "determination** for the affected needs; close each finding in §4 (build the "
            "check, execute the protocol, or fix the tool) and re-run.")
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


def build_sidecar(manifest, run, needs, verdict, case_meta=None, qms_coverage=None):
    case_meta = case_meta or {}
    env = run.get("environment", {})
    need_counts = {}
    for need in needs:
        key = need["_verdict"].lower().replace("-", "_")
        need_counts[key] = need_counts.get(key, 0) + 1
    tiers, scopes = {}, {}
    for c in run.get("cases", []):
        tiers[c.get("endpoint", "unspecified")] = tiers.get(c.get("endpoint", "unspecified"), 0) + 1
        scopes[c.get("scope", "unspecified")] = scopes.get(c.get("scope", "unspecified"), 0) + 1
    return {
        "schema_version": "2.0",
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
            "git_dirty_count": env.get("git_dirty_count", 0),
            "skills_total": len(env.get("skills", {})),
            "hooks_total": len(env.get("hooks_installed", [])),
            "model_id": env.get("model_id"),
            "model_captured": bool(env.get("model_id")),
            "harness_version": env.get("harness_version"),
            "skill_version_mismatches": env.get("skill_version_mismatches", []),
        },
        "environment": env,
        "warnings": run.get("warnings", []),
        "connections": run.get("connections") or env.get("connections", {}).get("declared", {}),
        "deployment": run.get("deployment") or {},
        "qms_coverage": qms_coverage,
        "summary": {
            "verdict": verdict,
            "needs": {"total": len(needs), **need_counts},
            "tests": {"total": len(run.get("cases", [])), **run.get("summary", {})},
            "tiers": tiers,
            "scopes": scopes,
        },
        "needs": [
            {
                "id": n["id"], "role": n.get("role"), "tier": n.get("tier"),
                "class": n.get("class"), "need": n.get("need"),
                "so_that": n.get("so_that"), "statement": need_statement(n),
                "implemented_by": n.get("implemented_by"),
                "verdict": n["_verdict"], "reason": n.get("_reason"), "tests": n.get("_tests", []),
                "strongest_evidence": n.get("_strongest"),
                "process_controls": n.get("process_controls", []),
            }
            for n in needs
        ],
        "tests": [
            {
                "id": c["id"], "title": c["title"], "wun": c.get("wun", []),
                "uut": c.get("uut", []), "uut_versions": c.get("uut_versions", {}),
                "status": c["status"], "duration_s": c.get("duration_s"),
                "endpoint": c.get("endpoint", "unspecified"),
                "connection": c.get("connection"),
                "scope": c.get("scope", "unspecified"), "method": c.get("method", "unspecified"),
                "requires_deployment": c.get("requires_deployment", []),
                "protocol": c.get("protocol"), "execution_record": c.get("execution_record"),
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


RENDERER_VERSION = "8"


def evaluate(manifest, run, root):
    """Needs × cases → verdicts for one run. Returns (needs, case_index, verdict, case_meta)."""
    case_meta = manifest_case_meta(manifest, root)
    case_index = {c["id"]: c for c in run.get("cases", [])}
    # Map need -> test cases from the test_cases[].wun edges (single source of truth).
    needs = [dict(n) for n in manifest.get("user_needs", [])]
    for need in needs:
        need["_tests"] = [c["id"] for c in manifest.get("test_cases", [])
                          if need["id"] in c.get("wun", [])]
        need["_verdict"] = need_verdict(need, case_index)
        need["_reason"] = need_reason(need, case_index)
        need["_strongest"] = strongest_evidence(need, case_index)
    return needs, case_index, overall_verdict(needs), case_meta


def load_manifest(path, root):
    manifest = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    manifest["_self_rel"] = str(path.relative_to(root)) if path.is_absolute() and root in path.parents else str(path)
    return manifest


def manifest_for_run(run, live_manifest_path, results_dir, root):
    """The manifest a run was executed against: its pinned copy when present,
    else the live manifest (flagged so the report says so)."""
    pinned = results_dir / run.get("run_id", "") / live_manifest_path.name
    if pinned.is_file():
        m = load_manifest(pinned, root)
        m["_pinned"] = True
        # generated outputs still resolve against the live layout keys
        live = load_manifest(live_manifest_path, root)
        for key in ("results_dir", "sidecar", "report", "qms_coverage", "protocol_results_dir"):
            if key in live and key not in m:
                m[key] = live[key]
        return m
    m = load_manifest(live_manifest_path, root)
    m["_pinned"] = False
    return m


def render_run(manifest, run, root, out_dir, historical_note=None, qms_coverage=None):
    """Write this run's own revision: report + sidecar under out_dir."""
    needs, case_index, verdict, case_meta = evaluate(manifest, run, root)
    out_dir.mkdir(parents=True, exist_ok=True)
    report = build_report(manifest, run, needs, case_index, verdict, root, case_meta)
    if historical_note:
        lines = report.split("\n")
        # after the title line
        lines.insert(2, f"> {historical_note}")
        lines.insert(3, "")
        report = "\n".join(lines)
    (out_dir / "validation-report.md").write_text(report, encoding="utf-8")
    side = build_sidecar(manifest, run, needs, verdict, case_meta, qms_coverage=qms_coverage)
    side["revision"] = {
        "run_id": run.get("run_id"),
        "rendered_with": f"render_report {RENDERER_VERSION}",
        "rendered_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "manifest": "pinned" if manifest.get("_pinned") else "live",
        "historical_note": historical_note,
    }
    (out_dir / "sidecar.json").write_text(json.dumps(side, indent=2) + "\n", encoding="utf-8")
    return verdict, side


def run_verdict_from_summary(summary):
    return "FAIL" if any(k in summary for k in ("FAIL", "ERROR", "NOT-EXECUTED")) else "PASS"


def write_runs_index(results_dir, root):
    """results/index.json — every recorded run, newest first, for the
    console's revision drop-down. Verdict comes from the run's rendered
    sidecar when present, else from its summary."""
    rows = []
    for f in sorted(results_dir.glob("run-*.json"), reverse=True):
        try:
            run = json.loads(f.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        rid = run.get("run_id") or f.stem
        env = run.get("environment") or {}
        side_path = results_dir / rid / "sidecar.json"
        verdict = None
        if side_path.is_file():
            try:
                verdict = (json.loads(side_path.read_text(encoding="utf-8")).get("summary") or {}).get("verdict")
            except (OSError, json.JSONDecodeError):
                verdict = None
        rows.append({
            "run_id": rid,
            "started": run.get("started"), "finished": run.get("finished"),
            "verdict": verdict or run_verdict_from_summary(run.get("summary") or {}),
            "summary": run.get("summary") or {},
            "cases_total": len(run.get("cases", [])),
            "partial": run.get("partial", False), "invoked_via": run.get("invoked_via", "cli"),
            "schema_version": run.get("schema_version"),
            "git_sha_short": env.get("git_sha_short"), "git_dirty": env.get("git_dirty"),
            "model_id": env.get("model_id"),
            "sidecar": str((results_dir / rid / "sidecar.json").relative_to(root)) if side_path.is_file() else None,
            "report": str((results_dir / rid / "validation-report.md").relative_to(root))
                      if (results_dir / rid / "validation-report.md").is_file() else None,
            "pinned_manifest": (run.get("pinned_manifest") or {}).get("path"),
        })
    (results_dir / "index.json").write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--manifest", default=DEFAULT_MANIFEST)
    parser.add_argument("--run", default=None, help="results JSON (default: results_dir/latest.json)")
    parser.add_argument("--all-runs", action="store_true",
                        help="also (re-)render every recorded run as its own revision")
    parser.add_argument("--no-per-run", action="store_true",
                        help="skip writing the per-run revision + index (top-level outputs only)")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    manifest_path = root / args.manifest
    if not manifest_path.is_file():
        sys.exit(f"Manifest not found: {manifest_path}")
    manifest = load_manifest(manifest_path, root)
    results_dir = root / manifest.get("results_dir", "tools/workbench-validation/results")
    run_path = Path(args.run) if args.run else results_dir / "latest.json"
    if not run_path.is_absolute():
        run_path = root / run_path
    if not run_path.is_file():
        sys.exit(f"No run results found at {run_path} — run run_validation.py first.")
    run = json.loads(run_path.read_text(encoding="utf-8"))

    # --- top-level outputs (always the run given / latest, against the live manifest) ---
    needs, case_index, verdict, case_meta = evaluate(manifest, run, root)
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
    cov, _ = load_qms_coverage(manifest, root)
    cov = None if (cov or {}).get("_error") else cov
    sidecar_path.write_text(
        json.dumps(build_sidecar(manifest, run, needs, verdict, case_meta, qms_coverage=cov),
                   indent=2) + "\n", encoding="utf-8")

    # --- per-run revisions + index ---
    if not args.no_per_run:
        latest_id = None
        latest_path = results_dir / "latest.json"
        if latest_path.is_file():
            try:
                latest_id = json.loads(latest_path.read_text(encoding="utf-8")).get("run_id")
            except (OSError, json.JSONDecodeError):
                latest_id = None
        targets = [run]
        if args.all_runs:
            targets = []
            for f in sorted(results_dir.glob("run-*.json")):
                try:
                    targets.append(json.loads(f.read_text(encoding="utf-8")))
                except (OSError, json.JSONDecodeError):
                    continue
        rendered = 0
        for r in targets:
            rid = r.get("run_id")
            if not rid:
                continue
            m = manifest_for_run(r, manifest_path, results_dir, root)
            is_latest = (rid == latest_id)
            note = None
            if not is_latest or str(r.get("schema_version", "1.0")) != str(run.get("schema_version", "1.0")):
                note = (f"Historical revision: run `{rid}` re-rendered by render_report {RENDERER_VERSION} "
                        f"on {datetime.now(timezone.utc).strftime('%Y-%m-%d')} from its "
                        f"{'pinned' if m.get('_pinned') else 'live (no pinned copy)'} manifest and recorded run data.")
            render_run(m, r, root, results_dir / rid, historical_note=note,
                       qms_coverage=cov if is_latest else None)
            rendered += 1
        rows = write_runs_index(results_dir, root)
        print(f"Revisions: {rendered} rendered · index {len(rows)} runs → "
              f"{(results_dir / 'index.json').relative_to(root)}")

    print(f"Report:  {report_rel}")
    print(f"Sidecar: {sidecar_rel}")
    print(f"Overall verdict: {verdict}")


if __name__ == "__main__":
    main()
