"""Formal-review tier helper — task-doc sentinel-block I/O for
`review-formal-{start, status, update, abort}`.

Subcommands:

  start    Write a new formal-review block to the active task doc with
           page id, page URL, baseline version, plugin name. State
           transitions `published → review-formal` in the source frontmatter.

  status   Read a Confluence page response on stdin (with optional
           inline + footer comment lists also passed as files), parse
           into FormalReviewItems, refresh the existing task-doc block
           preserving any `[x] addressed` items the user has hand-edited.

  update   On a successful publish: move "Already Addressed" items into
           "Recently Synced", clear macros listing.

  abort    Remove the formal-review block from the task doc; transition
           state back to `published`.

This helper is project-agnostic. The agent procedure
(`review-formal-*.md`) calls the relevant MCP tools and feeds responses
in via files / stdin.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

SKILL_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL_ROOT))

from lib.formal_review import (  # noqa: E402
    FormalReviewItem,
    FormalReviewSection,
    SENTINEL_END,
    find_block,
    parse_section,
    remove_block,
    render_section,
    upsert_block,
)
from lib.frontmatter import (  # noqa: E402
    read as read_frontmatter,
    update as update_frontmatter,
)
from lib.normalizer import NormalizationReport, normalize_for_diff  # noqa: E402


# ---- ADF response unwrapping ----


def _adf_from_response(raw: Any) -> Any:
    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except (ValueError, TypeError):
            return {"type": "doc", "content": []}
    if isinstance(raw, dict):
        body = raw.get("body")
        if isinstance(body, dict):
            if body.get("type") == "doc":
                return body
            for key in ("atlas_doc_format", "storage", "view"):
                slot = body.get(key)
                if isinstance(slot, dict) and "value" in slot:
                    val = slot["value"]
                    if isinstance(val, str) and val.strip().startswith("{"):
                        return json.loads(val)
                    if isinstance(val, dict):
                        return val
        if raw.get("type") == "doc":
            return raw
    return {"type": "doc", "content": []}


def _version_from_response(raw: dict) -> int:
    v = raw.get("version") or {}
    if isinstance(v, dict):
        try:
            return int(v.get("number") or 0)
        except (TypeError, ValueError):
            return 0
    return 0


# ---- Argument parsing ----


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="review_formal_helper",
        description="Maintain the formal-review sentinel block in the active task doc.",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--source", required=True, help="Source markdown doc path.")
    common.add_argument("--task-doc", required=True, help="Active task doc path.")

    s = sub.add_parser("start", parents=[common], help="Initialize the formal-review block.")
    s.add_argument("--page-url", required=True)
    s.add_argument("--baseline-version", type=int, required=True)
    s.add_argument("--plugin", default="document_control")

    st = sub.add_parser("status", parents=[common],
                        help="Refresh the block from Confluence comments + body diff.")
    st.add_argument("--current-adf", required=True,
                    help="Path to JSON file with the current page response.")
    st.add_argument("--inline-comments", default="",
                    help="Path to JSON file: list of inline comment dicts (or empty for none).")
    st.add_argument("--footer-comments", default="",
                    help="Path to JSON file: list of footer comment dicts (or empty for none).")
    st.add_argument("--cache-root", default="docs/.change-control")

    u = sub.add_parser("update", parents=[common],
                       help="Move Already Addressed → Recently Synced; clear macros listing.")

    a = sub.add_parser("abort", parents=[common],
                       help="Remove the block + transition state back to published.")
    a.add_argument("--target-state", default="published")

    return p


# ---- Comment-record normalizers ----


def _items_from_inline(records: list[dict]) -> list[FormalReviewItem]:
    out: list[FormalReviewItem] = []
    for r in records:
        if not isinstance(r, dict):
            continue
        marker_ref = ""
        anchor = ""
        props = r.get("inlineCommentProperties") or r.get("properties") or {}
        if isinstance(props, dict):
            marker_ref = (
                props.get("inlineMarkerRef")
                or props.get("markerRef")
                or ""
            )
            anchor = (
                props.get("inlineOriginalSelection")
                or props.get("originalSelection")
                or ""
            )
        if not marker_ref:
            marker_ref = str(r.get("id") or "")
        body = r.get("body", "")
        if isinstance(body, dict):
            for key in ("storage", "view", "atlas_doc_format", "raw"):
                slot = body.get(key)
                if isinstance(slot, dict) and "value" in slot:
                    body = slot["value"]
                    break
                if isinstance(slot, str):
                    body = slot
                    break
            else:
                body = ""
        author = r.get("author") or r.get("createdBy") or {}
        author_name = ""
        if isinstance(author, dict):
            author_name = author.get("displayName") or author.get("accountId") or ""
        elif isinstance(author, str):
            author_name = author
        out.append(FormalReviewItem(
            kind="inline",
            id=str(marker_ref),
            author=str(author_name),
            anchor=str(anchor),
            text=str(body).replace("\n", " ").strip()[:200],
            status="open",
        ))
    return out


def _items_from_footer(records: list[dict]) -> list[FormalReviewItem]:
    out: list[FormalReviewItem] = []
    for r in records:
        if not isinstance(r, dict):
            continue
        cid = str(r.get("id") or r.get("commentId") or "")
        body = r.get("body", "")
        if isinstance(body, dict):
            for key in ("storage", "view", "atlas_doc_format", "raw"):
                slot = body.get(key)
                if isinstance(slot, dict) and "value" in slot:
                    body = slot["value"]
                    break
                if isinstance(slot, str):
                    body = slot
                    break
            else:
                body = ""
        author = r.get("author") or r.get("createdBy") or {}
        author_name = ""
        if isinstance(author, dict):
            author_name = author.get("displayName") or author.get("accountId") or ""
        out.append(FormalReviewItem(
            kind="footer", id=cid, author=str(author_name),
            text=str(body).replace("\n", " ").strip()[:200], status="open",
        ))
    return out


def _items_from_macros(report: NormalizationReport) -> list[FormalReviewItem]:
    out: list[FormalReviewItem] = []
    for ext in report.extensions:
        if not isinstance(ext, dict):
            continue
        key = str(ext.get("key") or "")
        if not key:
            continue
        out.append(FormalReviewItem(
            kind="macro", id=key, author="", anchor="",
            text=f"Confluence-side macro ({key})", status="open",
        ))
    return out


# ---- Subcommand handlers ----


def _load_records(path: str) -> list[dict]:
    if not path:
        return []
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(raw, dict):
        return list(raw.get("results") or [])
    if isinstance(raw, list):
        return list(raw)
    return []


def cmd_start(args: argparse.Namespace) -> int:
    source_path = Path(args.source)
    fm = read_frontmatter(source_path)
    state = fm.data.get("state")
    if state != "published":
        print(f"review-formal-start: refusing — source state is {state!r}, expected 'published'",
              file=sys.stderr)
        return 66
    page_id = str((fm.data.get("confluence") or {}).get("page_id") or "")
    if not page_id:
        print("review-formal-start: refusing — no confluence.page_id in frontmatter",
              file=sys.stderr)
        return 66

    task_doc = Path(args.task_doc)
    task_text = task_doc.read_text(encoding="utf-8") if task_doc.exists() else ""
    section = FormalReviewSection.new(
        doc_path=str(source_path),
        page_id=page_id,
        page_url=args.page_url,
        baseline_version=args.baseline_version,
        plugin_name=args.plugin,
    )
    task_doc.write_text(upsert_block(task_text, section), encoding="utf-8")
    update_frontmatter(source_path, state="review-formal", confluence={
        "review_baseline_version": args.baseline_version,
    })
    print(f"review-formal-start: doc={source_path} page={page_id} v{args.baseline_version} -> task {task_doc}")
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    source_path = Path(args.source)
    task_doc = Path(args.task_doc)
    fm = read_frontmatter(source_path)
    if fm.data.get("state") != "review-formal":
        print(
            f"review-formal-status: refusing — state is {fm.data.get('state')!r}, "
            f"expected 'review-formal'",
            file=sys.stderr,
        )
        return 66

    raw = json.loads(Path(args.current_adf).read_text(encoding="utf-8"))
    adf = _adf_from_response(raw)
    current_version = _version_from_response(raw if isinstance(raw, dict) else {})

    inline_records = _load_records(args.inline_comments)
    footer_records = _load_records(args.footer_comments)

    # Existing block — preserve user-edited Already-Addressed across refresh
    task_text = task_doc.read_text(encoding="utf-8") if task_doc.exists() else ""
    rng = find_block(task_text, str(source_path))
    if rng is None:
        print("review-formal-status: no existing block; run review-formal-start first.",
              file=sys.stderr)
        return 66
    block_text = "\n".join(task_text.splitlines()[rng[0]:rng[1] + 1])
    prior = parse_section(block_text)

    # Build refreshed open items + macros
    inline_items = _items_from_inline(inline_records)
    footer_items = _items_from_footer(footer_records)
    open_items = inline_items + footer_items

    # Honor user edits: any open id that the user moved to addressed
    # stays in addressed, not back in open.
    addressed_ids = {(it.kind, it.id) for it in prior.already_addressed}
    open_items = [
        it for it in open_items if (it.kind, it.id) not in addressed_ids
    ]

    norm_report = NormalizationReport()
    _ = normalize_for_diff(adf)  # walk + populate report side-effect
    # normalize_for_diff returns markdown; but we need report data. Use the
    # underlying adf_to_markdown with explicit report:
    from lib.normalizer import adf_to_markdown
    adf_to_markdown(adf, attachment_url=None, report=norm_report)
    macros = _items_from_macros(norm_report)

    refreshed = FormalReviewSection(
        doc_path=str(source_path),
        page_id=prior.page_id,
        page_url=prior.page_url,
        baseline_version=prior.baseline_version or current_version,
        plugin_name=prior.plugin_name,
        first_pushed=prior.first_pushed,
        last_sync=__import__("datetime").datetime.now(__import__("datetime").timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        open_items=open_items,
        already_addressed=prior.already_addressed,
        recently_synced=prior.recently_synced,
        macros=macros,
    )
    task_doc.write_text(upsert_block(task_text, refreshed), encoding="utf-8")
    print(
        f"review-formal-status: open={len(open_items)} "
        f"({sum(1 for it in open_items if it.kind == 'inline')} inline · "
        f"{sum(1 for it in open_items if it.kind == 'footer')} footer) · "
        f"macros={len(macros)} · already_addressed={len(prior.already_addressed)}"
    )
    return 0


def cmd_update(args: argparse.Namespace) -> int:
    """Post-publish bookkeeping. Move Already Addressed -> Recently Synced;
    clear macros listing. Caller is responsible for the actual publish push +
    comment-reply MCP calls."""
    source_path = Path(args.source)
    task_doc = Path(args.task_doc)
    task_text = task_doc.read_text(encoding="utf-8") if task_doc.exists() else ""
    rng = find_block(task_text, str(source_path))
    if rng is None:
        print("review-formal-update: no existing block; nothing to update.", file=sys.stderr)
        return 66
    block_text = "\n".join(task_text.splitlines()[rng[0]:rng[1] + 1])
    section = parse_section(block_text)

    moved = list(section.already_addressed)
    section.already_addressed = []
    section.recently_synced = moved + section.recently_synced
    section.macros = []
    from datetime import datetime, timezone
    section.last_sync = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    task_doc.write_text(upsert_block(task_text, section), encoding="utf-8")
    print(f"review-formal-update: moved {len(moved)} addressed -> recently synced")
    return 0


def cmd_abort(args: argparse.Namespace) -> int:
    source_path = Path(args.source)
    task_doc = Path(args.task_doc)
    if task_doc.exists():
        task_doc.write_text(remove_block(task_doc.read_text(encoding="utf-8"), str(source_path)),
                            encoding="utf-8")
    update_frontmatter(source_path, state=args.target_state)
    print(f"review-formal-abort: state -> {args.target_state}; block removed from {task_doc}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.cmd == "start":
        return cmd_start(args)
    if args.cmd == "status":
        return cmd_status(args)
    if args.cmd == "update":
        return cmd_update(args)
    if args.cmd == "abort":
        return cmd_abort(args)
    parser.error(f"unknown command: {args.cmd}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
