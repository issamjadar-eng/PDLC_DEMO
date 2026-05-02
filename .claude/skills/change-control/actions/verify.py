"""verify — repeatable smoke tests for /change-control.

This helper writes structured JSON reports to
`tasks/<person>/_scratch/verify-<kind>-<date>.json` so the user can
inspect after each run. The reports are personal scratch (gitignored)
and never tracked.

Sub-actions:

  orphan-file              — synthesize a test PDF + plain-link markdown,
                             push to test_target, assert attachment renders,
                             re-adopt, assert marker restored.
  cross-page-resolution    — adopt a known UNKNOWN_MEDIA_ID page, assert
                             the resolver replaces the placeholder.
  drift-detection          — synthesize a hand-edit on an adopted page,
                             run `adopt --on-conflict prompt`, assert the
                             structured stderr fires.
  all                      — run all of the above.

The agent procedure in `actions/verify.md` orchestrates the live MCP /
cookie-bridge calls; this Python helper handles report writing and the
deterministic / offline pieces (config audit, scratch path resolution,
report shape).
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL_ROOT))

from lib.config import (  # noqa: E402
    ChangeControlConfig,
    TestTarget,
    find_project_root,
    read_change_control_config,
)


@dataclass
class VerifyStep:
    name: str
    ok: bool
    details: str = ""


@dataclass
class VerifyReport:
    kind: str
    date: str
    config: dict
    steps: list[VerifyStep] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return all(s.ok for s in self.steps) and bool(self.steps)

    def to_json(self) -> dict:
        return {
            "kind": self.kind,
            "date": self.date,
            "config": self.config,
            "steps": [
                {"name": s.name, "ok": s.ok, "details": s.details}
                for s in self.steps
            ],
            "ok": self.ok,
        }


# ---- Helpers ----


def _today_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _scratch_dir(project_root: Path, person: str) -> Path:
    """Return tasks/<person>/_scratch — create if missing. Personal scratch
    is gitignored project-wide, so files written here never end up in git.
    """
    d = project_root / "tasks" / person / "_scratch"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _detect_person(project_root: Path) -> str:
    """Best-effort person detection: read project.yml team.active[0]
    task_folder. Tests / non-team users get "default".
    """
    try:
        import yaml  # type: ignore
        raw = yaml.safe_load((project_root / "project.yml").read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return "default"
    team = (raw or {}).get("team") or {}
    active = team.get("active") or []
    if active and isinstance(active[0], dict):
        return str(active[0].get("task_folder") or "default")
    return "default"


def _config_summary(cfg: ChangeControlConfig) -> dict:
    """Subset of the config that's safe + useful to embed in the report.
    Excludes sensitive fields and large nested data."""
    return {
        "cloud_id": cfg.cloud_id,
        "base_url": cfg.base_url,
        "test_target": (
            {
                "space_key": cfg.test_target.space_key,
                "parent_page_id": cfg.test_target.parent_page_id,
                "parent_title": cfg.test_target.parent_title,
                "title_prefix": cfg.test_target.title_prefix,
            }
            if cfg.test_target
            else None
        ),
    }


def _validate_test_target(cfg: ChangeControlConfig) -> tuple[bool, str]:
    """Pre-flight: test_target must be configured + non-empty for live
    sub-actions."""
    if cfg.test_target is None:
        return False, "no project.yml change_control.test_target configured"
    tt = cfg.test_target
    missing = [
        n for n in ("space_key", "parent_page_id", "parent_title")
        if not getattr(tt, n)
    ]
    if missing:
        return False, f"test_target missing: {', '.join(missing)}"
    return True, ""


def write_report(
    report: VerifyReport,
    *,
    project_root: Path | None = None,
    person: str | None = None,
) -> Path:
    """Write the report to tasks/<person>/_scratch/verify-<kind>-<date>.json
    and return the path.
    """
    root = project_root or find_project_root()
    p = person or _detect_person(root)
    d = _scratch_dir(root, p)
    out = d / f"verify-{report.kind}-{report.date}.json"
    out.write_text(
        json.dumps(report.to_json(), indent=2) + "\n",
        encoding="utf-8",
    )
    return out


# ---- Sub-actions (deterministic; live work is orchestrated by the
# actions/verify.md agent procedure which calls into this for report
# writing and config-audit steps). ----


def cmd_audit(args: argparse.Namespace) -> int:
    """Print a config-only audit. No live MCP / cookie-bridge calls.
    Used by the agent procedure as the first step of every verify run.
    """
    cfg = read_change_control_config()
    report = VerifyReport(
        kind="audit",
        date=_today_utc(),
        config=_config_summary(cfg),
    )
    report.steps.append(VerifyStep(
        name="config-loaded",
        ok=not cfg.is_empty,
        details=(
            "project.yml change_control block present" if not cfg.is_empty
            else "project.yml change_control block missing or empty"
        ),
    ))
    ok, msg = _validate_test_target(cfg)
    report.steps.append(VerifyStep(
        name="test-target-configured",
        ok=ok,
        details=msg or (
            f"test_target = {cfg.test_target.parent_title} "
            f"(page {cfg.test_target.parent_page_id} in space "
            f"{cfg.test_target.space_key})"
            if cfg.test_target else ""
        ),
    ))
    report.steps.append(VerifyStep(
        name="cross-page-source-map-present",
        ok=bool(cfg.cross_page_source_map),
        details=(
            f"{len(cfg.cross_page_source_map)} entries"
            if cfg.cross_page_source_map
            else "no cross_page_source_map entries (resolver will fall back to live CQL)"
        ),
    ))
    out = write_report(report)
    print(json.dumps(report.to_json(), indent=2))
    print(f"\nreport written: {out}", file=sys.stderr)
    return 0 if report.ok else 1


def cmd_orphan_file(args: argparse.Namespace) -> int:
    """Stub for the orphan-file roundtrip verify. The full live workflow
    is orchestrated by the agent in `actions/verify.md` — this entry
    point exists so the agent can write a structured report at the end.

    Reads steps from stdin as JSON list of {name, ok, details} dicts and
    persists as a verify-orphan-file-<date>.json report.
    """
    cfg = read_change_control_config()
    raw = sys.stdin.read().strip()
    try:
        steps_raw = json.loads(raw) if raw else []
    except ValueError as exc:
        print(f"verify orphan-file: stdin is not valid JSON: {exc}", file=sys.stderr)
        return 64
    if not isinstance(steps_raw, list):
        print("verify orphan-file: stdin must be a JSON list of step dicts.",
              file=sys.stderr)
        return 65
    report = VerifyReport(
        kind="orphan-file",
        date=_today_utc(),
        config=_config_summary(cfg),
        steps=[
            VerifyStep(
                name=str(s.get("name") or ""),
                ok=bool(s.get("ok")),
                details=str(s.get("details") or ""),
            )
            for s in steps_raw if isinstance(s, dict)
        ],
    )
    out = write_report(report)
    print(json.dumps(report.to_json(), indent=2))
    print(f"\nreport written: {out}", file=sys.stderr)
    return 0 if report.ok else 1


def cmd_cross_page_resolution(args: argparse.Namespace) -> int:
    """Stub for cross-page-resolution verify. Agent feeds steps via stdin."""
    cfg = read_change_control_config()
    raw = sys.stdin.read().strip()
    try:
        steps_raw = json.loads(raw) if raw else []
    except ValueError as exc:
        print(f"verify cross-page-resolution: stdin is not valid JSON: {exc}", file=sys.stderr)
        return 64
    if not isinstance(steps_raw, list):
        print("stdin must be JSON list", file=sys.stderr)
        return 65
    report = VerifyReport(
        kind="cross-page-resolution",
        date=_today_utc(),
        config=_config_summary(cfg),
        steps=[
            VerifyStep(
                name=str(s.get("name") or ""),
                ok=bool(s.get("ok")),
                details=str(s.get("details") or ""),
            )
            for s in steps_raw if isinstance(s, dict)
        ],
    )
    out = write_report(report)
    print(json.dumps(report.to_json(), indent=2))
    print(f"\nreport written: {out}", file=sys.stderr)
    return 0 if report.ok else 1


def cmd_drift_detection(args: argparse.Namespace) -> int:
    """Stub for drift-detection verify. Agent feeds steps via stdin."""
    cfg = read_change_control_config()
    raw = sys.stdin.read().strip()
    try:
        steps_raw = json.loads(raw) if raw else []
    except ValueError as exc:
        print(f"verify drift-detection: stdin is not valid JSON: {exc}", file=sys.stderr)
        return 64
    if not isinstance(steps_raw, list):
        print("stdin must be JSON list", file=sys.stderr)
        return 65
    report = VerifyReport(
        kind="drift-detection",
        date=_today_utc(),
        config=_config_summary(cfg),
        steps=[
            VerifyStep(
                name=str(s.get("name") or ""),
                ok=bool(s.get("ok")),
                details=str(s.get("details") or ""),
            )
            for s in steps_raw if isinstance(s, dict)
        ],
    )
    out = write_report(report)
    print(json.dumps(report.to_json(), indent=2))
    print(f"\nreport written: {out}", file=sys.stderr)
    return 0 if report.ok else 1


# ---- CLI ----


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="change-control verify",
        description="Repeatable smoke tests for /change-control.",
    )
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser(
        "audit",
        help="Config-only audit — no live calls. Validates project.yml "
             "change_control block + test_target presence.",
    )
    sub.add_parser(
        "orphan-file",
        help="Persist orphan-file roundtrip report. Reads steps JSON list "
             "from stdin, writes report to tasks/<person>/_scratch/.",
    )
    sub.add_parser(
        "cross-page-resolution",
        help="Persist cross-page-resolution report from stdin steps.",
    )
    sub.add_parser(
        "drift-detection",
        help="Persist drift-detection report from stdin steps.",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    handlers = {
        "audit": cmd_audit,
        "orphan-file": cmd_orphan_file,
        "cross-page-resolution": cmd_cross_page_resolution,
        "drift-detection": cmd_drift_detection,
    }
    h = handlers.get(args.cmd)
    if h is None:
        parser.error(f"unknown command: {args.cmd}")
        return 1
    return h(args)


if __name__ == "__main__":
    sys.exit(main())
