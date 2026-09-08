#!/usr/bin/env python3
"""Command line for the multimodel layer — the contract other skills call.

    python3 .claude/skills/multimodel/scripts/multimodel.py doctor            # config + live probes
    python3 .claude/skills/multimodel/scripts/multimodel.py doctor --quick    # config only, NO calls
    python3 .claude/skills/multimodel/scripts/multimodel.py doctor --json     # machine-readable
    python3 .claude/skills/multimodel/scripts/multimodel.py providers         # who is configured / ready
    python3 .claude/skills/multimodel/scripts/multimodel.py verify            # prove project access is read-only (live)
    python3 .claude/skills/multimodel/scripts/multimodel.py ask "question"    # every enabled provider
    python3 .claude/skills/multimodel/scripts/multimodel.py ask --provider grok --schema s.json --prompt-file p.md --json

Config comes from the host project's `project.yml` (`multimodel:` block) by
default, or from a `.toml` passed with --config. Self-contained: this script
adds the skill's own `src/` to the path, so nothing needs installing.

Exit codes: 0 all good · 1 something is wrong (or any provider did not answer) · 2 bad usage.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from multimodel import (  # noqa: E402
    ConfigError,
    Council,
    external_send_allowed,
    load_config,
    project_root,
    verify_all,
)


def _load(args: argparse.Namespace) -> dict[str, Any] | None:
    try:
        return load_config(args.config)
    except ConfigError as exc:
        print(f"[FAIL] {exc}", file=sys.stderr)
        return None


def _read_schema(spec: str | None) -> dict[str, Any] | None:
    """`--schema` accepts a path to a JSON file or inline JSON."""
    if not spec:
        return None
    path = Path(spec)
    text = path.read_text(encoding="utf-8") if path.is_file() else spec
    schema = json.loads(text)
    if not isinstance(schema, dict):
        raise ValueError("schema must be a JSON object")
    return schema


def _read_prompt(args: argparse.Namespace) -> str:
    if args.prompt_file:
        if args.prompt_file == "-":
            return sys.stdin.read()
        return Path(args.prompt_file).read_text(encoding="utf-8")
    if args.prompt:
        return args.prompt
    raise ValueError("give a PROMPT argument, --prompt-file PATH, or --prompt-file - for stdin")


# -- doctor ------------------------------------------------------------------


def cmd_doctor(args: argparse.Namespace) -> int:
    config = _load(args)
    if config is None:
        return 1

    council = Council.from_config(config, role=args.role, include_disabled=args.all)
    report: dict[str, Any] = {
        "config": str(args.config or "project.yml"),
        "providers": {},
        "skipped": council.skipped,
        "policy": {},
    }
    problems: list[str] = []

    allowed, why = external_send_allowed(config)
    report["policy"] = {"external_send_allowed": allowed, "reason": why}

    if not council.providers:
        message = (
            "no providers found"
            + (f" with role={args.role!r}" if args.role else "")
            + ". Enable one with `enabled: true`, or pass --all."
        )
        if args.json:
            print(json.dumps({**report, "problems": [message], "ok": False}, indent=2))
        else:
            print(f"[FAIL] {message}")
        return 1

    if not args.json:
        print("multimodel doctor")
        print("=" * 66)
        print(f"config    : {report['config']}")
        print(f"providers : {', '.join(council.names)}")
        print(f"policy    : {why}")
        if council.skipped:
            print("skipped   : " + "; ".join(f"{k} ({v})" for k, v in council.skipped.items()))
        print()
        print("Configuration")

    availability = council.availability()
    for name, (ok, reason) in availability.items():
        provider = council.get(name)
        workspace = provider.workspace if provider else "?"
        report["providers"][name] = {"available": ok, "reason": reason, "workspace": workspace}
        if not ok:
            problems.append(f"{name}: {reason}")
        if not args.json:
            print(f"  [{'ok' if ok else 'FAIL'}]   {name:<14} [{workspace}] {reason}")

    if args.quick:
        if not args.json:
            print("\n(--quick: skipped live probes. Local checks cannot detect an")
            print(" expired session or a revoked entitlement — only a real call can.)")
    elif not allowed:
        problems.append(f"live probes skipped: {why}")
        if not args.json:
            print(f"\n(live probes skipped: {why})")
    else:
        if not args.json:
            print()
            print("Live probes (one small call each)")
        for result in council.probe_all(timeout=args.timeout):
            entry = report["providers"].setdefault(result.provider, {})
            entry.update({
                "probe_ok": result.ok,
                "probe_detail": result.detail,
                "elapsed_seconds": result.elapsed_seconds,
                "structured_output": result.structured,
                "usage": result.usage,
            })
            if not result.ok:
                problems.append(f"{result.provider}: probe failed - {result.detail}")
            if not args.json:
                elapsed = f"{result.elapsed_seconds:.1f}s" if result.elapsed_seconds else "-"
                print(f"  [{result.status:<4}] {result.provider:<14} {elapsed:>6}  {result.detail}")
                if result.usage and result.usage.get("total_tokens"):
                    turns = result.usage.get("num_turns")
                    extra = f", turns: {turns}" if turns is not None else ""
                    print(f"{'':>24}tokens: {result.usage['total_tokens']:,}{extra}")

    report["problems"] = problems
    report["ok"] = not problems

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print()
        print("=" * 66)
        if problems:
            print(f"{len(problems)} issue(s):")
            for problem in problems:
                print(f"  - {problem}")
        elif args.quick:
            # Never claim more than was actually checked. No call was made, so
            # "configured" is the strongest honest word available here.
            print("Configuration looks correct. NOT verified against the services —")
            print("re-run without --quick to confirm they actually answer.")
        else:
            print("All providers answered and returned structured output.")

    return 1 if problems else 0


# -- providers -----------------------------------------------------------------


def cmd_providers(args: argparse.Namespace) -> int:
    config = _load(args)
    if config is None:
        return 1
    council = Council.from_config(config, role=args.role, include_disabled=True)
    rows = []
    for provider in council.providers:
        enabled = bool(provider.cfg.get("enabled", False))
        ok, reason = provider.available() if enabled else (False, "disabled")
        rows.append({
            "name": provider.name,
            "type": provider.cfg.get("type", provider.name),
            "role": provider.role,
            "workspace": provider.workspace,
            "enabled": enabled,
            "available": ok,
            "reason": reason,
            "description": provider.cfg.get("description", ""),
        })
    if args.json:
        print(json.dumps({"providers": rows, "skipped": council.skipped}, indent=2))
        return 0
    for row in rows:
        state = "ready" if row["available"] else ("off" if not row["enabled"] else "FAIL")
        print(f"  [{state:<5}] {row['name']:<14} role={row['role'] or '-':<11} ws={row['workspace']:<9} {row['reason']}")
    for name, why in council.skipped.items():
        print(f"  [skip ] {name:<14} {why}")
    return 0


# -- verify ------------------------------------------------------------------


def cmd_verify(args: argparse.Namespace) -> int:
    """Prove, live, that each provider can read the project and cannot write it."""
    config = _load(args)
    if config is None:
        return 1
    allowed, why = external_send_allowed(config)
    if not allowed:
        print(f"[FAIL] cannot verify without sending: {why}", file=sys.stderr)
        return 1

    council = Council.from_config(config, role=args.role, only=args.provider or None)
    explicit = bool(args.provider)
    candidates = []
    skipped: dict[str, str] = {}
    for provider in council.providers:
        if args.timeout:
            provider.cfg["timeout_seconds"] = args.timeout
        if provider.workspace == "isolated" and not explicit:
            # Nothing to verify: an isolated provider never sees the project.
            # Naming it with --provider forces the check anyway.
            skipped[provider.name] = "isolated by config — no project access to verify"
            continue
        provider.cfg["workspace"] = "project"
        candidates.append(provider)
    ready = [p for p in candidates if p.available()[0]]
    skipped.update({p.name: p.available()[1] for p in candidates if p not in ready})

    root = project_root()
    results = verify_all(ready, root, attempts=args.attempts)
    report = {
        "root": str(root),
        "results": [r.to_dict() for r in results],
        "unavailable": skipped,
        "ok": bool(results) and all(r.ok for r in results),
    }
    if args.json:
        print(json.dumps(report, indent=2))
        return 0 if report["ok"] else 1

    print("multimodel verify — read-only project access")
    print("=" * 66)
    print(f"root      : {root}")
    print(f"providers : {', '.join(p.name for p in ready) or '(none available)'}")
    print()
    for r in results:
        elapsed = f"{r.elapsed_seconds:.1f}s"
        tries = f" (attempt {r.attempts})" if r.attempts > 1 else ""
        print(f"  [{r.status:<8}] {r.provider:<14} {elapsed:>6}  read={'ok' if r.read_ok else 'FAIL'}"
              f"  write={'blocked' if r.write_blocked else 'LANDED'}  {r.detail}{tries}")
        if r.usage and r.usage.get("num_turns") is not None:
            print(f"{'':>26}turns: {r.usage['num_turns']}")
    for name, why in skipped.items():
        print(f"  [--      ] {name:<14}       not verified: {why}")
    print()
    print("=" * 66)
    if not results:
        print("Nothing verified — no provider is configured for project access and available.")
    elif report["ok"]:
        print("Every verified provider read the marker and could not write. Project access is read-only.")
    else:
        print("At least one provider FAILED — see rows above. Do not use a CRITICAL provider in project mode.")
    return 0 if report["ok"] else 1


# -- ask ---------------------------------------------------------------------


def cmd_ask(args: argparse.Namespace) -> int:
    config = _load(args)
    if config is None:
        return 1

    allowed, why = external_send_allowed(config)
    if not allowed:
        print(f"[FAIL] refusing to send: {why}", file=sys.stderr)
        return 1

    try:
        prompt = _read_prompt(args)
        schema = _read_schema(args.schema)
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print(f"[FAIL] {exc}", file=sys.stderr)
        return 2

    council = Council.from_config(config, role=args.role, only=args.provider or None)
    if not council.providers:
        wanted = f" {args.provider}" if args.provider else ""
        print(f"[FAIL] no enabled providers{wanted}", file=sys.stderr)
        for name, reason in council.skipped.items():
            print(f"       {name}: {reason}", file=sys.stderr)
        return 1
    for provider in council.providers:
        if args.timeout:
            provider.cfg["timeout_seconds"] = args.timeout
        if args.workspace:
            provider.cfg["workspace"] = args.workspace

    responses = council.ask_all(prompt, schema=schema, tag=args.tag)
    failed = sum(1 for r in responses if not r.ok)

    if args.json:
        print(json.dumps({
            "answered": len(responses) - failed,
            "asked": len(responses),
            "responses": [r.to_dict() for r in responses],
        }, indent=2))
        return 1 if failed else 0

    for response in responses:
        print(f"\n{'=' * 66}\n{response.provider}\n{'=' * 66}")
        if response.ok:
            if schema and response.data is not None:
                print(json.dumps(response.data, indent=2))
            else:
                print(response.text.strip())
        else:
            # Never let a failure read as an answer.
            print(f"[NO ANSWER] {response.error}")
    print(f"\n{len(responses) - failed}/{len(responses)} answered.")
    return 1 if failed else 0


# -- parser ------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="multimodel",
        description="Query several independent LLM providers and check they work.",
    )
    parser.add_argument(
        "--config", default=None,
        help="project.yml (multimodel: block) or a .toml file; default: nearest project.yml",
    )
    parser.add_argument("--role", default=None, help="only providers with this role label")

    sub = parser.add_subparsers(dest="command", required=True)

    doctor = sub.add_parser("doctor", help="check configuration and provider liveness")
    doctor.add_argument("--quick", action="store_true",
                        help="skip live probes (config checks only, no calls made)")
    doctor.add_argument("--json", action="store_true", help="machine-readable output")
    doctor.add_argument("--all", action="store_true", help="include disabled providers")
    doctor.add_argument("--timeout", type=int, default=90, help="probe timeout, seconds")
    doctor.set_defaults(func=cmd_doctor)

    providers = sub.add_parser("providers", help="list configured providers and readiness")
    providers.add_argument("--json", action="store_true", help="machine-readable output")
    providers.set_defaults(func=cmd_providers)

    verify = sub.add_parser("verify", help="live check: each provider reads a marker and cannot write")
    verify.add_argument("--provider", action="append", help="restrict to this provider (repeatable)")
    verify.add_argument("--timeout", type=int, default=None, help="override timeout_seconds")
    verify.add_argument("--attempts", type=int, default=2,
                        help="retries for a read miss (a landed write is never retried)")
    verify.add_argument("--json", action="store_true", help="machine-readable output")
    verify.set_defaults(func=cmd_verify)

    ask = sub.add_parser("ask", help="ask enabled providers a question")
    ask.add_argument("prompt", nargs="?", help="the question (or use --prompt-file)")
    ask.add_argument("--prompt-file", help="read the prompt from a file, or '-' for stdin")
    ask.add_argument("--provider", action="append",
                     help="restrict to this provider (repeatable); default: every enabled one")
    ask.add_argument("--schema", help="JSON Schema file or inline JSON for structured output")
    ask.add_argument("--tag", default="", help="opaque label echoed back on each response")
    ask.add_argument("--timeout", type=int, default=None, help="override timeout_seconds")
    ask.add_argument("--workspace", choices=["project", "isolated"], default=None,
                     help="where the vendor CLI runs: the project root with read-only tools "
                          "(default) or an empty temp dir that sees only the prompt")
    ask.add_argument("--json", action="store_true", help="machine-readable output")
    ask.set_defaults(func=cmd_ask)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    sys.exit(main())
