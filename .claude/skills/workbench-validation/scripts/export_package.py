#!/usr/bin/env python3
"""Workbench validation package exporter.

Assembles ONE sectioned document for a recorded validation run — the report
body plus every artifact and piece of evidence the run rests on — and emits it
as Markdown, or converts it to DOCX / PDF through docflow's `export_formal.py`
(the project's sanctioned md → formal pipeline: pandoc → LibreOffice).

Package layout:
  Cover + Sign-off · Report body (re-rendered from the run's PINNED manifest)
  Appendix A  Pinned validation manifest (YAML)
  Appendix B  Environment record + deployment declaration
  Appendix C  Protocols — written protocol, execution record, run evidence files
  Appendix D  Evidence logs — full per-case transcripts
  Appendix E  Pinned test sources (sha256 inventory)
  Appendix F  QMS template coverage inventory

Usage:
  python3 export_package.py --root <repo> --run <run-id|latest> --format md|docx|pdf
                            [--out <path>] [--manifest <path>]

Prints the absolute output path on the last stdout line.
Exit codes: 0 ok · 2 precondition (run not found, converter missing, conversion failed).
"""

import argparse
import importlib.util
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("PyYAML is required (python3 -m pip install pyyaml, or run via `uv run --with pyyaml`).")

DEFAULT_MANIFEST = "docs/project/workbench-validation/validation.yml"
DEFAULT_RESULTS = "tools/workbench-validation/results"
DEFAULT_PROTOCOLS = "tools/workbench-validation/protocols"
DEFAULT_EXPORTS = "tools/workbench-validation/exports"
DOCFLOW_EXPORT = ".claude/skills/docflow/scripts/export_formal.py"
HERE = Path(__file__).resolve().parent


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _load_renderer():
    spec = importlib.util.spec_from_file_location("wb_render_report", HERE / "render_report.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def utc_now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def fence(text, lang=""):
    """Fence arbitrary text safely — pick a fence longer than any run of
    backticks inside so embedded code blocks never break the package."""
    text = text if text is not None else ""
    longest = 0
    run = 0
    for ch in text:
        if ch == "`":
            run += 1
            longest = max(longest, run)
        else:
            run = 0
    ticks = "`" * max(3, longest + 1)
    body = text.rstrip("\n")
    return f"{ticks}{lang}\n{body}\n{ticks}"


def read_text(path):
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return f"(unreadable: {exc})"


def md_escape(text):
    return str(text if text is not None else "").replace("|", "\\|").replace("\n", " ").strip()


def resolve_run(results_dir, run_arg):
    """Run JSON path + run id for `latest` or an explicit id."""
    if run_arg in (None, "", "latest"):
        latest = results_dir / "latest.json"
        if not latest.is_file():
            return None, None
        try:
            rid = json.loads(latest.read_text(encoding="utf-8")).get("run_id")
        except (OSError, json.JSONDecodeError):
            return None, None
        explicit = results_dir / f"{rid}.json"
        return (explicit if explicit.is_file() else latest), rid
    path = results_dir / f"{run_arg}.json"
    if not path.is_file():
        return None, None
    return path, run_arg


def load_manifest(root, run, run_dir, override):
    """The run's PINNED manifest, else --manifest, else the live manifest."""
    pinned = (run.get("pinned_manifest") or {}).get("path")
    candidates = []
    if pinned:
        candidates.append(("pinned", root / pinned))
    candidates.append(("pinned", run_dir / "validation.yml"))
    if override:
        candidates.append(("override", root / override))
    candidates.append(("live", root / run.get("manifest", DEFAULT_MANIFEST)))
    candidates.append(("live", root / DEFAULT_MANIFEST))
    for kind, path in candidates:
        if path.is_file():
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            data["_self_rel"] = str(path.relative_to(root)) if path.is_relative_to(root) else str(path)
            return data, kind, path
    return None, None, None


# ---------------------------------------------------------------------------
# package sections
# ---------------------------------------------------------------------------

def build_needs(render, manifest, run):
    case_index = {c["id"]: c for c in run.get("cases", [])}
    needs = [dict(n) for n in manifest.get("user_needs", [])]
    for need in needs:
        need["_tests"] = [c["id"] for c in manifest.get("test_cases", [])
                          if need["id"] in c.get("wun", [])]
        need["_verdict"] = render.need_verdict(need, case_index)
        need["_reason"] = render.need_reason(need, case_index)
        need["_strongest"] = render.strongest_evidence(need, case_index)
    return needs, case_index, render.overall_verdict(needs)


def cover(manifest, run, verdict, manifest_kind, historical, generated):
    env = run.get("environment") or {}
    op = env.get("operator") or {}
    title = (manifest.get("report") or {}).get("title", "Workbench Validation Report")
    out = []
    add = out.append
    add(f"# {title} — Validation Package")
    add("")
    banner = manifest.get("banner")
    if banner:
        add(banner)
        add("")
    add(f"**Run** `{run.get('run_id')}` · **Verdict: {verdict}**")
    add("")
    add("| Item | Value |")
    add("|---|---|")
    add(f"| Started / finished | {run.get('started', '?')} → {run.get('finished', '?')} ({run.get('duration_s', '?')}s) |")
    add(f"| Configuration baseline | commit `{env.get('git_sha_short') or env.get('git_sha', '?')}` on `{env.get('git_branch', '?')}`"
        f"{' — **working tree dirty**' if env.get('git_dirty') else ' — clean tree'} |")
    add(f"| Model identifier | {env.get('model_id') or '_not captured_'} |")
    add(f"| Harness version | {env.get('harness_version') or '_not captured_'} |")
    op_line = " ".join(filter(None, [op.get("git_user"), f"<{op['git_email']}>" if op.get("git_email") else None,
                                     f"({op['os_user']}@{op.get('hostname', '?')})" if op.get("os_user") else None])) or "_not recorded_"
    add(f"| Operator | {op_line} |")
    add(f"| Invoked via | {run.get('invoked_via', 'cli')}{' · **partial run**' if run.get('partial') else ''} |")
    add(f"| Run schema | {run.get('schema_version', '?')} · manifest used for this package: {manifest_kind} (`{manifest.get('_self_rel', '?')}`) |")
    add(f"| Package generated | {generated} |")
    add("")
    if historical:
        add("> Historical run re-rendered by the current renderer from its pinned run data.")
        add("")
    for w in run.get("warnings") or []:
        add(f"> ⚠️ {w}")
    if run.get("warnings"):
        add("")
    add("## Sign-off")
    add("")
    add("| Role | Name | Date | Signature |")
    add("|---|---|---|---|")
    add("| Validation lead |  |  |  |")
    add("| Quality |  |  |  |")
    add("| Operator |  |  |  |")
    add("")
    add("## Contents")
    add("")
    add("1. Validation report (re-rendered from this run's pinned manifest and run data)")
    add("2. Appendix A — Pinned validation manifest")
    add("3. Appendix B — Environment record and deployment declaration")
    add("4. Appendix C — Protocols: written protocol, execution record, run evidence")
    add("5. Appendix D — Evidence logs (full per-case transcripts)")
    add("6. Appendix E — Pinned test sources (sha256 inventory)")
    add("7. Appendix F — QMS template coverage inventory")
    add("")
    return out


def appendix_a(manifest_path):
    return ["## Appendix A — Pinned validation manifest", "",
            f"Source: `{manifest_path}`", "", fence(read_text(manifest_path), "yaml"), ""]


def appendix_b(render, run):
    out = ["## Appendix B — Environment record and deployment declaration", ""]
    env = run.get("environment") or {}
    if env:
        # Re-use the report's grouped rendering; strip its <details> wrapper so
        # the section is always expanded in a printed package.
        lines = render.environment_details(env, run)
        lines = [ln for ln in lines if not ln.startswith("<details") and not ln.startswith("</details")]
        lines = [ln.replace("<summary>", "**").replace("</summary>", "**") for ln in lines]
        out.extend(lines)
        out.append("")
    else:
        out += ["_No environment record in this run (pre-1.1 schema)._", ""]
    dep = run.get("deployment") or {}
    out += ["### Deployment declaration", ""]
    if dep:
        out += ["| Dependency | Declared |", "|---|---|"]
        for group, vals in sorted(dep.items()):
            if isinstance(vals, dict):
                for k, v in sorted(vals.items()):
                    out.append(f"| `{group}.{k}` | {v} |")
            else:
                out.append(f"| `{group}` | {vals} |")
    else:
        out.append("_No deployment declaration recorded for this run (pre-2.0 schema)._")
    out.append("")
    return out


def appendix_c(root, run, protocols_dir):
    out = ["## Appendix C — Protocols: written protocol, execution record, run evidence", ""]
    cases = [c for c in run.get("cases", []) if c.get("method") in ("protocol", "inspection")]
    if not cases:
        out += ["_No protocol or inspection cases in this run._", ""]
        return out
    for c in cases:
        out.append(f"### {c['id']} — {c.get('title', '')}")
        out.append("")
        out.append(f"Method: {c.get('method')} · Status: **{c.get('status')}**"
                   + (f" · {md_escape(c.get('reason'))}" if c.get("reason") else ""))
        out.append("")
        proto_rel = c.get("protocol")
        if proto_rel and (root / proto_rel).is_file():
            text = read_text(root / proto_rel)
            version_line = next((ln for ln in text.splitlines() if "version" in ln.lower()), None)
            out.append(f"#### Written protocol — `{proto_rel}`")
            if version_line:
                out.append("")
                out.append(f"_Protocol file version line (current file, not pinned): {md_escape(version_line)}_")
            out.append("")
            out.append(fence(text, "markdown"))
            out.append("")
        else:
            out += [f"_Written protocol not on disk_ (`{proto_rel or '—'}`).", ""]
        rec = c.get("execution_record") or {}
        rec_path = rec.get("path") or f"{protocols_dir}/{c['id']}.result.yml"
        out.append(f"#### Execution record — `{rec_path}`")
        out.append("")
        if (root / rec_path).is_file():
            out.append(fence(read_text(root / rec_path), "yaml"))
        else:
            out.append(f"_No execution record — {c.get('status')}"
                       + (f" ({md_escape(c.get('reason'))})" if c.get("reason") else "") + "._")
        out.append("")
        ev_dir = root / protocols_dir / c["id"]
        ev_files = sorted(ev_dir.rglob("*.md")) if ev_dir.is_dir() else []
        # any evidence files the record names that live elsewhere
        extra = []
        for e in rec.get("evidence") or []:
            p = root / str(e)
            if p.is_file() and p.suffix == ".md" and p not in ev_files and not p.is_relative_to(ev_dir if ev_dir.exists() else root / "___"):
                extra.append(p)
        out.append(f"#### Run evidence files ({len(ev_files) + len(extra)})")
        out.append("")
        if not ev_files and not extra:
            out.append("_None recorded._")
            out.append("")
        for f in ev_files + extra:
            rel = f.relative_to(root)
            out.append(f"##### `{rel}`")
            out.append("")
            out.append(fence(read_text(f), "markdown"))
            out.append("")
    return out


def appendix_d(root, run):
    out = ["## Appendix D — Evidence logs (full per-case transcripts)", ""]
    cases = run.get("cases", [])
    with_logs = 0
    for c in cases:
        out.append(f"### {c['id']} — {c.get('title', '')}")
        out.append("")
        log_rel = c.get("log")
        if log_rel and (root / log_rel).is_file():
            with_logs += 1
            out.append(f"Status: **{c.get('status')}** · log `{log_rel}`")
            out.append("")
            out.append(fence(read_text(root / log_rel), "text"))
        else:
            out.append(f"no log — {c.get('status')}"
                       + (f" ({md_escape(c.get('reason'))})" if c.get("reason") else ""))
        out.append("")
    out.insert(2, f"{with_logs} of {len(cases)} cases carry an evidence log; the rest were never executed by design "
                  f"(NOT-APPLICABLE / NOT-EXECUTED / SKIPPED) or predate per-case logging.")
    out.insert(3, "")
    return out


def appendix_e(run):
    out = ["## Appendix E — Pinned test sources (sha256 inventory)", ""]
    any_rows = False
    for c in run.get("cases", []):
        files = c.get("pinned_files") or []
        if not files and not c.get("pinned"):
            continue
        any_rows = True
        out.append(f"### {c['id']} — {c.get('title', '')}")
        out.append("")
        out.append(f"Pinned copy: `{c.get('pinned') or '—'}` · source: `{c.get('source') or '—'}`")
        out.append("")
        if files:
            out += ["| Pinned file | sha256 |", "|---|---|"]
            for f in files:
                out.append(f"| `{f.get('path')}` | `{f.get('sha256')}` |")
        else:
            out.append("_No file inventory recorded._")
        out.append("")
    if not any_rows:
        out += ["_This run pinned no test sources (pre-pinning schema)._", ""]
    return out


def appendix_f(render, root, manifest, run, is_latest):
    out = ["## Appendix F — QMS template coverage inventory", ""]
    rel = manifest.get("qms_coverage", "tools/workbench-validation/qms-coverage.json")
    path = root / rel
    if not path.is_file() or not is_latest:
        out += [f"_Not produced for this run_ (inventory at `{rel}` "
                + ("belongs to the latest run only" if path.is_file() else "does not exist") + ").", ""]
        return out
    cov, _ = render.load_qms_coverage(manifest, root)
    out.extend(render.qms_coverage_section(cov, rel))
    out.append("")
    out.append("Raw summary:")
    out.append("")
    out.append(fence(json.dumps((cov or {}).get("summary", {}), indent=2), "json"))
    out.append("")
    return out


def build_package(root, run, run_id, manifest, manifest_kind, manifest_path, results_dir, protocols_dir, is_latest):
    render = _load_renderer()
    case_meta = render.manifest_case_meta(manifest, root)
    needs, case_index, verdict = build_needs(render, manifest, run)
    historical = str(run.get("schema_version", "1.0")) < "2.0" or any(n.get("coverage") for n in needs)
    generated = utc_now()
    body = render.build_report(manifest, run, needs, case_index, verdict, root, case_meta)
    # The report starts with its own H1; demote its headings one level so the
    # package has a single H1 (the cover) and the report sits under it.
    body_lines = []
    for ln in body.splitlines():
        if ln.startswith("#"):
            body_lines.append("#" + ln)
        else:
            body_lines.append(ln)
    parts = []
    parts += cover(manifest, run, verdict, manifest_kind, historical, generated)
    parts += ["## 1. Validation report", ""]
    parts += body_lines
    parts += [""]
    parts += appendix_a(manifest_path)
    parts += appendix_b(render, run)
    parts += appendix_c(root, run, protocols_dir)
    parts += appendix_d(root, run)
    parts += appendix_e(run)
    parts += appendix_f(render, root, manifest, run, is_latest)
    parts += ["---", "",
              f"_Package generated {generated} by the workbench-validation skill (`export_package.py`) from run `{run_id}`. "
              "Every appendix is a verbatim copy of the run's recorded artifacts; nothing here is re-executed or re-judged._", ""]
    return "\n".join(parts) + "\n", verdict


# ---------------------------------------------------------------------------
# conversion via docflow
# ---------------------------------------------------------------------------

def convert(root, md_path, fmt, out_path, title, header_text):
    script = root / DOCFLOW_EXPORT
    if not script.is_file():
        return 2, f"docflow exporter not installed at {DOCFLOW_EXPORT}"
    if shutil.which("pandoc") is None:
        return 2, "converter missing: pandoc (required for docx/pdf)"
    if fmt == "pdf" and shutil.which("soffice") is None:
        return 2, "converter missing: soffice (LibreOffice, required for pdf)"
    cmd = [sys.executable, str(script), str(md_path), "--format", fmt, "--out", str(out_path),
           "--title", title, "--header-text", header_text]
    proc = subprocess.run(cmd, cwd=str(root), capture_output=True, text=True)
    if proc.returncode == 2:
        return 2, "converter missing (reported by docflow):\n" + (proc.stderr or proc.stdout)
    if proc.returncode != 0 or not out_path.is_file():
        return 2, f"docflow export failed (exit {proc.returncode}):\n" + (proc.stderr or proc.stdout)
    return 0, ""


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=".")
    ap.add_argument("--run", default="latest", help="run id, or `latest`")
    ap.add_argument("--format", choices=["md", "docx", "pdf"], default="md")
    ap.add_argument("--out", default=None, help="output path (default: tools/workbench-validation/exports/<run-id>/validation-package.<ext>)")
    ap.add_argument("--manifest", default=None, help="manifest to use when the run has no pinned copy")
    ap.add_argument("--results-dir", default=None)
    ap.add_argument("--protocols-dir", default=None)
    args = ap.parse_args(argv)

    root = Path(args.root).resolve()
    live_manifest = None
    if (root / DEFAULT_MANIFEST).is_file():
        try:
            live_manifest = yaml.safe_load((root / DEFAULT_MANIFEST).read_text(encoding="utf-8")) or {}
        except Exception:
            live_manifest = None
    results_rel = args.results_dir or (live_manifest or {}).get("results_dir", DEFAULT_RESULTS)
    protocols_rel = args.protocols_dir or (live_manifest or {}).get("protocol_results_dir", DEFAULT_PROTOCOLS)
    results_dir = root / results_rel

    run_path, run_id = resolve_run(results_dir, args.run)
    if run_path is None:
        print(f"run not found: {args.run} (looked in {results_dir})", file=sys.stderr)
        return 2
    run = json.loads(run_path.read_text(encoding="utf-8"))
    run_dir = results_dir / run_id
    manifest, kind, manifest_path = load_manifest(root, run, run_dir, args.manifest)
    if manifest is None:
        print("no manifest found (pinned, --manifest, or live)", file=sys.stderr)
        return 2
    latest_id = None
    if (results_dir / "latest.json").is_file():
        try:
            latest_id = json.loads((results_dir / "latest.json").read_text(encoding="utf-8")).get("run_id")
        except (OSError, json.JSONDecodeError):
            latest_id = None
    is_latest = (latest_id == run_id)

    package_md, verdict = build_package(root, run, run_id, manifest, kind, manifest_path,
                                        results_dir, protocols_rel, is_latest)

    out_dir = root / DEFAULT_EXPORTS / run_id
    out_dir.mkdir(parents=True, exist_ok=True)
    md_path = out_dir / "validation-package.md"
    if args.format == "md" and args.out:
        md_path = Path(args.out).resolve()
        md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(package_md, encoding="utf-8")
    if args.format == "md":
        print(f"package: {md_path}")
        print(str(md_path))
        return 0

    out_path = Path(args.out).resolve() if args.out else out_dir / f"validation-package.{args.format}"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    title = (manifest.get("report") or {}).get("title", "Workbench Validation Report") + " — Validation Package"
    code, err = convert(root, md_path, args.format, out_path, title, f"{run_id} · {verdict}")
    if code != 0:
        print(err, file=sys.stderr)
        return 2
    print(f"markdown: {md_path}")
    print(str(out_path))
    return 0


if __name__ == "__main__":
    sys.exit(main())
