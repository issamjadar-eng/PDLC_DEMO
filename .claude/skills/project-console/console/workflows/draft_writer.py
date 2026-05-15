"""Draft writer for the B6 Create Draft workflow.

Materializes draft files inside a tracker-draft worktree. The draft-author
agent never writes files directly — it returns an outline JSON (mode 1) or
markdown body (mode 2), and this driver:

  1. write_outline_stub(wt, row_id, outline, agent_name, actor)
       Creates `_drafting/<row-id>-<slug>.md` with frontmatter spliced from
       the outline. Body is the no-template banner placeholder if the
       outline reports `qms_template.found: false`, else empty.

  2. mark_outline_approved(wt, row_id)
       Sets `agent.outline_approved_at` ISO timestamp in frontmatter.

  3. write_synthesis(wt, row_id, body_md)
       Replaces the placeholder body with the agent's full markdown body.
       Sets `agent.synthesis_completed_at` and recomputes the
       `references.{inline_citations, verify_markers,
       qms_references_section_present}` counters.

  4. save_to_target(wt, row_id, target_path)
       git-mv's `_drafting/<row-id>-*.md` → `<target_path>` and updates
       submission-tracker.md (Path column + Status). Returns the result
       structure for the router endpoint.

Idempotency:
  - All mutators are safe to retry.
  - If `_drafting/<row-id>-*.md` already exists when write_outline_stub
    runs, the existing file is updated in place (frontmatter merged with
    the new outline; body retained if non-empty).
"""

from __future__ import annotations

import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

DRAFTING_DIR = "_drafting"
TRACKER_MD_REL = "docs/project/submissions/submission-tracker.md"


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _today() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _slugify(text: str) -> str:
    """Make a kebab-case slug suitable for `_drafting/<row-id>-<slug>.md`."""
    s = re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")
    return s or "draft"


def _run(args: list[str], cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(args, cwd=str(cwd), capture_output=True, text=True, timeout=60)


# ── Frontmatter helpers ──────────────────────────────────────────────────

def _yaml_dump(obj: dict) -> str:
    try:
        import yaml  # type: ignore
        return yaml.safe_dump(obj, sort_keys=False, allow_unicode=True)
    except ImportError:
        # Tiny fallback — just enough for our shapes
        return json.dumps(obj, indent=2)


def _yaml_load(text: str) -> dict:
    try:
        import yaml  # type: ignore
        return yaml.safe_load(text) or {}
    except Exception:
        return {}


def _split_frontmatter(text: str) -> tuple[dict, str]:
    """Return (frontmatter_dict, body) for a markdown file. If no frontmatter,
    returns ({}, full text)."""
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end < 0:
        # Malformed; treat as no frontmatter
        return {}, text
    fm = _yaml_load(text[4:end])
    body = text[end + 5:]
    return fm, body


def _join_frontmatter(fm: dict, body: str) -> str:
    return "---\n" + _yaml_dump(fm) + "---\n" + body


# ── Stage 1: outline → frontmatter stub ─────────────────────────────────

_NO_TEMPLATE_BANNER = (
    "> [VERIFY: No QMS template located] Synthesized without a project QMS "
    "template skeleton. Section structure is best-effort — please cross-check "
    "against the governing SOP before review.\n\n"
)


def _existing_staging_file(wt: Path, row_id: str) -> Path | None:
    staging = wt / DRAFTING_DIR
    if not staging.is_dir():
        return None
    matches = sorted(staging.glob(f"{row_id}-*.md"))
    return matches[0] if matches else None


def _build_frontmatter(
    row_id: str,
    outline: dict,
    agent_name: str,
    actor: str,
    branch: str,
    session_task_rel: str,
) -> dict:
    """Build the canonical frontmatter dict from the outline JSON."""
    target = (outline.get("target") or {}) if isinstance(outline, dict) else {}
    qms = (outline.get("qms_template") or {}) if isinstance(outline, dict) else {}
    target_path = target.get("path") or ""
    derived = target.get("derived_filename") or (
        Path(target_path).name if target_path else f"{row_id}-draft.md"
    )
    return {
        "state": "draft",
        "title": outline.get("title") or outline.get("description", "")[:80] or row_id,
        "source": {
            "origin": "local-draft",
            "created_by": "tracker-draft-workflow",
            "tracker_row_id": row_id,
            "draft_session": session_task_rel,
            "draft_branch": branch,
            "drafted_by": actor,
            "drafted_at": _now_iso(),
        },
        "target": {
            "path": target_path,
            "exists": bool(target.get("exists")),
            "derived_filename": derived,
        },
        "confluence": {
            "page_id": None,
            "space": None,
            "parent_page_id": None,
            "version": None,
        },
        "agent": {
            "name": agent_name,
            "outline_approved_at": None,
            "synthesis_completed_at": None,
        },
        "references": {
            "strip_on_publish": True,
            "inline_citations": 0,
            "verify_markers": 0,
            "qms_references_section_present": False,
        },
        "qms_template": {
            "found": bool(qms.get("found")),
            "path": qms.get("path"),
            "governing_sop": qms.get("governing_sop"),
            "search_paths_consulted": qms.get("search_paths_consulted") or [],
        },
    }


def write_outline_stub(
    wt: Path,
    row_id: str,
    outline: dict,
    agent_name: str,
    actor: str,
    branch: str,
    session_task_rel: str,
) -> dict:
    """Materialize `_drafting/<row-id>-<slug>.md` with frontmatter spliced
    from the outline. Body starts as the no-template banner if applicable,
    else empty. Idempotent — re-running merges new outline values into the
    existing frontmatter and preserves any non-empty body."""
    target = (outline.get("target") or {}) if isinstance(outline, dict) else {}
    target_path = target.get("path") or ""
    base_slug = _slugify(Path(target_path).stem if target_path else row_id)
    fname = f"{row_id}-{base_slug}.md"

    staging = wt / DRAFTING_DIR
    staging.mkdir(exist_ok=True)
    existing = _existing_staging_file(wt, row_id)

    qms_found = bool((outline.get("qms_template") or {}).get("found"))
    initial_body = "" if qms_found else _NO_TEMPLATE_BANNER

    if existing is None:
        fm = _build_frontmatter(row_id, outline, agent_name, actor, branch, session_task_rel)
        text = _join_frontmatter(fm, initial_body)
        out_path = staging / fname
        out_path.write_text(text, encoding="utf-8")
        return {
            "staging_file": str(out_path.relative_to(wt)),
            "created": True,
            "merged": False,
        }
    # Merge into existing — preserve body if non-trivial, refresh frontmatter target/qms blocks.
    text = existing.read_text(encoding="utf-8")
    fm, body = _split_frontmatter(text)
    new_fm = _build_frontmatter(row_id, outline, agent_name, actor, branch, session_task_rel)
    # Preserve fields the existing file already filled in (e.g., agent timestamps)
    for k in ("agent",):
        if k in fm and isinstance(fm[k], dict) and isinstance(new_fm.get(k), dict):
            for subk, subv in fm[k].items():
                if subv:
                    new_fm[k][subk] = subv
    # Preserve body if user added content
    body_to_write = body if body.strip() else initial_body
    existing.write_text(_join_frontmatter(new_fm, body_to_write), encoding="utf-8")
    return {
        "staging_file": str(existing.relative_to(wt)),
        "created": False,
        "merged": True,
    }


def mark_outline_approved(wt: Path, row_id: str) -> dict:
    f = _existing_staging_file(wt, row_id)
    if f is None:
        raise LookupError(f"no staging file found for row {row_id}")
    text = f.read_text(encoding="utf-8")
    fm, body = _split_frontmatter(text)
    fm.setdefault("agent", {})
    fm["agent"]["outline_approved_at"] = _now_iso()
    f.write_text(_join_frontmatter(fm, body), encoding="utf-8")
    return {"staging_file": str(f.relative_to(wt)), "outline_approved_at": fm["agent"]["outline_approved_at"]}


# ── Stage 2: synthesis → body ────────────────────────────────────────────

_INLINE_CITE_RE = re.compile(r"\[\d+\]")
_VERIFY_RE = re.compile(r"\[VERIFY:[^\]]*\]")
_REFERENCES_HEADING_RE = re.compile(r"^##\s+(References|QMS References)\s*$", re.MULTILINE | re.IGNORECASE)


def _count_markers(body: str) -> dict:
    return {
        "inline_citations": len(_INLINE_CITE_RE.findall(body)),
        "verify_markers": len(_VERIFY_RE.findall(body)),
        "qms_references_section_present": bool(_REFERENCES_HEADING_RE.search(body)),
    }


def write_synthesis(wt: Path, row_id: str, body_md: str) -> dict:
    """Replace the staging file's body with `body_md`. Updates
    `agent.synthesis_completed_at` and the `references.*` counters."""
    f = _existing_staging_file(wt, row_id)
    if f is None:
        raise LookupError(f"no staging file found for row {row_id}")
    text = f.read_text(encoding="utf-8")
    fm, _old_body = _split_frontmatter(text)
    fm.setdefault("agent", {})
    fm["agent"]["synthesis_completed_at"] = _now_iso()
    counts = _count_markers(body_md)
    fm.setdefault("references", {})
    fm["references"].update(counts)
    new_body = body_md if body_md.endswith("\n") else body_md + "\n"
    f.write_text(_join_frontmatter(fm, new_body), encoding="utf-8")
    return {
        "staging_file": str(f.relative_to(wt)),
        "synthesis_completed_at": fm["agent"]["synthesis_completed_at"],
        "counts": counts,
    }


# ── Stage 3: save → relocate + tracker md update ────────────────────────

_DELIVERABLE_ROW_RE = re.compile(r"^\|\s*(?P<id>[A-Z][A-Z0-9-]+)\s*\|")


def _resolve_target_path(wt: Path, row_id: str, override: str | None) -> str:
    """Return a worktree-relative target path. Prefer caller override, else
    read from the staging file's frontmatter `target.path`."""
    if override:
        return override
    f = _existing_staging_file(wt, row_id)
    if f is None:
        raise LookupError(f"no staging file for row {row_id}")
    fm, _ = _split_frontmatter(f.read_text(encoding="utf-8"))
    target = (fm.get("target") or {}).get("path") or ""
    if not target:
        raise ValueError(f"frontmatter target.path is empty for row {row_id}")
    return target


def _update_tracker_md_for_save(wt: Path, row_id: str, target_path_rel: str) -> bool:
    """Replace the row's Path cell — currently the disabled Create Draft
    button — with a markdown link to the new target path, and bump status
    to Drafted. Returns True if both updates landed; False if row not found.
    """
    md_path = wt / TRACKER_MD_REL
    if not md_path.is_file():
        return False
    md = md_path.read_text(encoding="utf-8")
    lines = md.splitlines(keepends=False)
    changed = False
    target_filename = Path(target_path_rel).name
    # Tracker md uses paths relative to docs/project/submissions/. Compute
    # a relative link from the tracker md back to the target.
    try:
        from os.path import relpath
        link_target = relpath(
            (wt / target_path_rel).resolve(),
            (wt / TRACKER_MD_REL).parent.resolve(),
        )
    except Exception:
        link_target = target_path_rel
    new_path_cell = f"[`{target_filename}`]({link_target})"

    for i, line in enumerate(lines):
        m = _DELIVERABLE_ROW_RE.match(line)
        if not m or m.group("id") != row_id:
            continue
        positions = [j for j, c in enumerate(line) if c == "|"]
        if len(positions) < 9:
            continue
        # Status cell = positions[6]+1..positions[7]; Path cell = positions[7]+1..positions[8]
        status_start = positions[6] + 1
        status_end = positions[7]
        path_start = positions[7] + 1
        path_end = positions[8]
        # Update status to Drafted (preserve bold) + path
        new_status_cell = " **Drafted** "
        new_path_cell_padded = f" {new_path_cell} "
        new_line = (
            line[:status_start] + new_status_cell
            + "|" + new_path_cell_padded + line[path_end:]
        )
        lines[i] = new_line
        changed = True
        break
    if changed:
        suffix = "\n" if md.endswith("\n") else ""
        md_path.write_text("\n".join(lines) + suffix, encoding="utf-8")
    return changed


def save_to_target(
    wt: Path,
    row_id: str,
    target_override: str | None = None,
) -> dict:
    """git-mv the staging file to the resolved target path inside the
    worktree, update submission-tracker.md (Path cell + Status), and
    re-render the HTML. The caller (router) handles ff-merge separately
    via `draft_session.commit_and_merge`."""
    f = _existing_staging_file(wt, row_id)
    if f is None:
        raise LookupError(f"no staging file for row {row_id}")
    target_path_rel = _resolve_target_path(wt, row_id, target_override)
    src = f
    dst = wt / target_path_rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    moved = False
    if str(src) != str(dst):
        # Prefer git mv for clean history; fall back to plain rename if git complains
        r = _run(["git", "mv", str(src.relative_to(wt)), str(dst.relative_to(wt))], cwd=wt)
        if r.returncode != 0:
            # Files may not have been added to the index yet — fall back
            src.rename(dst)
        moved = True

    # Refresh frontmatter: clear `target.exists` is False -> True after this save (now it exists)
    # and update `target.path` if it didn't include the resolved path.
    text = dst.read_text(encoding="utf-8")
    fm, body = _split_frontmatter(text)
    fm.setdefault("target", {})
    fm["target"]["path"] = target_path_rel
    fm["target"]["exists"] = True
    fm["target"]["derived_filename"] = Path(target_path_rel).name
    dst.write_text(_join_frontmatter(fm, body), encoding="utf-8")

    md_updated = _update_tracker_md_for_save(wt, row_id, target_path_rel)
    rendered = regenerate_tracker_html(wt)
    return {
        "row_id": row_id,
        "moved": moved,
        "target_path": target_path_rel,
        "tracker_md_updated": md_updated,
        "tracker_html_rendered": rendered,
    }


def regenerate_tracker_html(wt: Path) -> bool:
    """Re-render tracker HTML inside the worktree. Best-effort."""
    # The render.py inside the worktree's checkout (post-worktree-add) is
    # the same as the project's; resolve it relative to the worktree root.
    script = wt / ".claude/skills/tracker/scripts/render.py"
    if not script.is_file():
        return False
    try:
        r = _run(["python3", str(script), "--project-dir", str(wt)], cwd=wt)
        return r.returncode == 0
    except Exception:
        return False


# ── Outline-sentinel scanning ────────────────────────────────────────────

_OUTLINE_SENTINEL_RE = re.compile(
    r"<!--\s*B6 OUTLINE START:\s*(?P<row>[A-Z][A-Z0-9-]+)\s+v(?P<version>\d+)\s*-->"
    r"(?P<body>.*?)"
    r"<!--\s*/B6 OUTLINE END\s*-->",
    re.DOTALL,
)


def find_latest_outline_block(transcript: str, row_id: str) -> dict | None:
    """Reverse-scan a transcript for the most-recent outline-sentinel block
    matching `row_id`. Returns {version, body} or None."""
    matches = list(_OUTLINE_SENTINEL_RE.finditer(transcript))
    matches = [m for m in matches if m.group("row") == row_id]
    if not matches:
        return None
    last = matches[-1]
    return {
        "version": int(last.group("version")),
        "body": last.group("body").strip(),
    }
