"""B1 — Doc Round-Trip Batch: dry-run logic.

Scans working markdown files under DHF design-controls trees and returns
an export plan. No actual /docflow invocation in this prototype —
the plan describes what *would* run, per the Placeholder Convention.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


# Folders whose `.md` files are candidates for round-trip export to DOCX.
# Kept narrow for the dry-run — real B1 would widen based on frontmatter or
# per-DHF rules.
_CANDIDATE_ROOTS = (
    "docs/project/dhfs",
    "docs/project/submissions",
    "docs/project/strategies",
)


@dataclass(frozen=True)
class Candidate:
    virtual_path: str      # repo-relative posix path
    dhf: str               # dhf leaf name or "" (e.g. mfd-a, "submissions")
    size_bytes: int
    proposed_docx: str     # where /docflow export would land the formal doc


def scan(repo_root: Path) -> list[Candidate]:
    """Return candidate `.md` files under the configured roots, skipping
    anything already under a `formal/` subtree (those are generated outputs)
    and anything under README.md (those aren't round-trip targets)."""
    out: list[Candidate] = []
    for root in _CANDIDATE_ROOTS:
        base = repo_root / root
        if not base.is_dir():
            continue
        for p in sorted(base.rglob("*.md")):
            rel = p.relative_to(repo_root).as_posix()
            if "/formal/" in rel or rel.endswith("/formal"):
                continue
            if p.name.lower() == "readme.md":
                continue
            if p.name.startswith("000-") or p.name == "INDEX.md":
                continue
            try:
                size = p.stat().st_size
            except OSError:
                continue
            dhf = _infer_dhf(rel)
            out.append(
                Candidate(
                    virtual_path=rel,
                    dhf=dhf,
                    size_bytes=size,
                    proposed_docx=_proposed_docx(rel),
                )
            )
    return out


def _infer_dhf(rel: str) -> str:
    parts = rel.split("/")
    # docs/project/dhfs/<dhf>/... → <dhf>
    if len(parts) >= 4 and parts[0] == "docs" and parts[1] == "project" and parts[2] == "dhfs":
        return parts[3]
    if len(parts) >= 3 and parts[0] == "docs" and parts[1] == "project":
        return parts[2]  # submissions, strategies
    return ""


def _proposed_docx(rel: str) -> str:
    """Place the DOCX into the nearest `formal/` sibling of the markdown's
    folder. This mirrors the docflow export convention."""
    p = Path(rel)
    stem = p.stem
    return str(p.parent / "formal" / f"{stem}.docx")


@dataclass(frozen=True)
class PlanEntry:
    virtual_path: str
    proposed_docx: str
    command: str             # the /docflow invocation we'd run
    backend_status: str      # "placeholder" for dry-run; "live" once wired


def build_plan(repo_root: Path, selected_paths: list[str]) -> list[PlanEntry]:
    """For each selected markdown path, produce the /docflow command that
    would be run + the target DOCX path. Validates each path exists under
    the allowed candidate roots (prevents arbitrary path submission)."""
    valid = {c.virtual_path for c in scan(repo_root)}
    out: list[PlanEntry] = []
    for rel in selected_paths:
        rel = rel.strip()
        if not rel or rel not in valid:
            continue
        target = _proposed_docx(rel)
        cmd = f"/docflow export {rel} --target {target}"
        out.append(
            PlanEntry(
                virtual_path=rel,
                proposed_docx=target,
                command=cmd,
                backend_status="placeholder",  # dry-run only in prototype
            )
        )
    return out
