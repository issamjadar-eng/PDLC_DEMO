"""Publish helper — orchestrates the markdown→Confluence publish
pipeline for `change-control publish` (Option A: agent-orchestrated).

The publish flow is split across multiple agent turns + multiple
helper invocations because the agent has to call MCP tools between
each pure-Python phase:

    1. agent: getConfluencePage(adf) for divergence detection
       (only if frontmatter has page_id; new pages skip this)
    2. helper `precheck`: read frontmatter, run markdown_transform,
       capture zones from current ADF, compute divergence + diff,
       emit a JSON precheck packet
    3. agent: present O/M/A prompt (or auto-select on first publish);
       on Merge, write <doc>.confluence-side.md and exit
    4. helper `body`: produce the transformed body + a list of any
       captured zones — the body is what we POST to MCP
    5. agent: createConfluencePage / updateConfluencePage with
       contentFormat=markdown, body from step 4
    6. agent: getConfluencePage(adf) on the just-pushed page
    7. helper `splice`: splice captured zones back into the new ADF
       and emit a final ADF body
    8. agent: updateConfluencePage with contentFormat=adf, body from
       step 7 (this is the second push that re-establishes zones)
    9. helper `commit`: update frontmatter (state=published,
       last_published_version, last_published_at), write the new
       snapshot, prune old snapshots, print summary

Subcommands:

  precheck  Read frontmatter + source body, transform body, capture
            zones from current ADF (passed on stdin if existing page),
            compute divergence (need snapshot dir + last_published).
            Emit a JSON precheck packet to stdout for the agent to
            consume.
  body      Print just the transformed-and-stripped markdown body
            (the bytes the agent should send to MCP).
  splice    Read final ADF (post-push) on stdin, splice captured
            zones back, emit ADF on stdout.
  commit    Update frontmatter + write snapshot + prune old snapshots.

Inputs are line-delimited / file-based to keep the protocol
simple in agent-orchestrated mode.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

SKILL_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL_ROOT))

from lib.divergence import compute_diff  # noqa: E402
from lib.frontmatter import (  # noqa: E402
    read as read_frontmatter,
    update as update_frontmatter,
)
from lib.markdown_transform import (  # noqa: E402
    PageRef,
    TransformOptions,
    transform_markdown,
)
from lib.normalizer import normalize_for_diff  # noqa: E402
from lib.snapshot import read_snapshot, write_snapshot  # noqa: E402
from lib.zones import extract_zones, splice_zones_back  # noqa: E402


# ---- Argument parsing ----


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="publish_helper",
        description="Orchestrate the change-control publish pipeline.",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    # precheck
    pc = sub.add_parser(
        "precheck",
        help="Transform body + capture zones + compute divergence; emit JSON.",
    )
    pc.add_argument("--source", required=True, help="Path to the local markdown source.")
    pc.add_argument(
        "--current-adf",
        default="",
        help="Path to a JSON file with the current page's ADF body. "
             "Empty when first-publishing a new page.",
    )
    pc.add_argument(
        "--page-index",
        default="",
        help="Optional path to a JSON file mapping repo-relative .md "
             "paths -> {page_id, space_key, base_url} for cross-link rewriting.",
    )
    pc.add_argument(
        "--cache-root",
        default="docs/.change-control",
        help="Snapshot cache root (default: docs/.change-control).",
    )
    pc.add_argument(
        "--miss-policy",
        choices=("lenient", "strict", "placeholder"),
        default="lenient",
    )
    pc.add_argument(
        "--strip-internal",
        action="store_true",
        help="Publish the FILED BODY ONLY — strip 🔒 INTERNAL <details> containers, "
             "HTML-comment metadata blocks, and 🔒-marked table columns (the same "
             "content transmitted to the regulator). Default keeps 🔒 blocks as "
             "collapsed Confluence expands.",
    )

    # body
    bd = sub.add_parser(
        "body",
        help="Print the transformed markdown body (what to POST to MCP).",
    )
    bd.add_argument("--source", required=True)
    bd.add_argument("--page-index", default="")
    bd.add_argument(
        "--miss-policy", choices=("lenient", "strict", "placeholder"), default="lenient"
    )
    bd.add_argument("--strip-internal", action="store_true",
                    help="Filed-body only: strip 🔒 INTERNAL containers + metadata comments.")

    # html-body — Confluence storage HTML output (kept for diagnostic
    # use even though the Atlassian MCP write API does NOT accept
    # contentFormat=html — see adf-body for the production publish path).
    hb = sub.add_parser(
        "html-body",
        help="Print Confluence storage HTML body (diagnostic; MCP write does not accept html — use adf-body for publish).",
    )
    hb.add_argument("--source", required=True)
    hb.add_argument("--page-index", default="")
    hb.add_argument(
        "--miss-policy", choices=("lenient", "strict", "placeholder"), default="lenient"
    )
    hb.add_argument("--strip-internal", action="store_true",
                    help="Filed-body only: strip 🔒 INTERNAL containers + metadata comments.")

    # adf-body — Atlassian Document Format JSON for contentFormat=adf publish.
    # Recovers panel chrome (panelType), underlines (mark.type=underline),
    # smartcards (inlineCard nodes), and native macros (toc/children/
    # page-signatures via extension nodes). This is the production publish
    # path because MCP write only accepts contentFormat ∈ {markdown, adf}.
    ab = sub.add_parser(
        "adf-body",
        help="Print Confluence ADF body JSON (for contentFormat=adf publish).",
    )
    ab.add_argument("--source", required=True)
    ab.add_argument("--page-index", default="")
    ab.add_argument(
        "--miss-policy", choices=("lenient", "strict", "placeholder"), default="lenient"
    )
    ab.add_argument("--strip-internal", action="store_true",
                    help="Filed-body only: strip 🔒 INTERNAL containers + metadata comments.")
    ab.add_argument(
        "--emit-images-sidecar",
        default="",
        help="If set, write a JSON sidecar to this path listing every "
             "ADF media-node placeholder emitted from local image refs. "
             "Each entry: {placeholder, source_relpath, alt}. The "
             "agent procedure uses this to upload binaries + patch the "
             "ADF before the second updateConfluencePage call.",
    )

    # patch-adf — replace PLACEHOLDER:images/<file> media ids with real
    # attachment ids after upload. Reads ADF on stdin, takes a JSON map
    # `{placeholder: real_id}` from --map, emits patched ADF on stdout.
    pa = sub.add_parser(
        "patch-adf",
        help="Read ADF on stdin, replace PLACEHOLDER:* media ids with "
             "real attachment ids from --map, emit patched ADF on stdout.",
    )
    pa.add_argument(
        "--map",
        required=True,
        help="JSON file: {placeholder_string: real_attachment_id}.",
    )

    # upload-images — given an ADF placeholder list (sidecar) and a
    # target page id, upload each binary via web-control cookie bridge
    # and emit the {placeholder: media_id} map on stdout.
    ui = sub.add_parser(
        "upload-images",
        help="Upload images from a sidecar to a target Confluence page; "
             "emit {placeholder: media_id} map on stdout.",
    )
    ui.add_argument("--sidecar", required=True,
                    help="Path to images sidecar JSON (from adf-body --emit-images-sidecar).")
    ui.add_argument("--source-dir", required=True,
                    help="Directory containing images/<file> binaries to upload.")
    ui.add_argument("--page-id", required=True,
                    help="Target Confluence page id to attach binaries to.")
    ui.add_argument("--base-url", default="",
                    help="Confluence base URL for the cookie bridge. "
                         "Defaults to project.yml `change_control.base_url`.")

    # splice
    sp = sub.add_parser(
        "splice",
        help="Read final ADF on stdin, splice captured zones back, emit ADF on stdout.",
    )
    sp.add_argument(
        "--zones",
        required=True,
        help="Path to a JSON file with the captured zones (from precheck output).",
    )

    # commit
    cm = sub.add_parser(
        "commit",
        help="Update frontmatter + write snapshot.",
    )
    cm.add_argument("--source", required=True)
    cm.add_argument("--page-id", required=True)
    cm.add_argument("--version", type=int, required=True)
    cm.add_argument(
        "--cache-root", default="docs/.change-control",
    )
    cm.add_argument("--published-at", default="")
    cm.add_argument(
        "--state",
        default="published",
        help="State to write into frontmatter (default: published).",
    )

    # write-confluence-side (used by the Merge branch of the agent prompt)
    wc = sub.add_parser(
        "write-confluence-side",
        help="Write the current page's normalized markdown next to the source "
             "as <doc>.confluence-side.md for manual reconciliation.",
    )
    wc.add_argument("--source", required=True)
    wc.add_argument("--current-adf", required=True)

    return p


# ---- Helpers ----


def _today_utc() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_page_index(path: str) -> dict[str, PageRef]:
    if not path:
        return {}
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        return {}
    out: dict[str, PageRef] = {}
    for k, v in raw.items():
        if not isinstance(v, dict):
            continue
        out[k] = PageRef(
            page_id=str(v.get("page_id") or ""),
            space_key=str(v.get("space_key") or ""),
            title=str(v.get("title") or ""),
            base_url=str(v.get("base_url") or ""),
        )
    return out


def _adf_from_mcp_response(raw: Any) -> Any:
    """Accept the raw `getConfluencePage` response and return the ADF doc dict.

    Handles three shapes:
      - Live MCP: `{body: {type: "doc", ...}}` (body IS the ADF doc).
      - Wrapped: `{body: {atlas_doc_format: {value: "<json string>"}}}`.
      - Bare ADF doc passed in directly (`{type: "doc", ...}`).
    """
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
    if isinstance(raw, str) and raw.strip().startswith("{"):
        return json.loads(raw)
    return {"type": "doc", "content": []}


# ---- Subcommand handlers ----


def cmd_precheck(args: argparse.Namespace) -> int:
    source_path = Path(args.source)
    fm = read_frontmatter(source_path)
    confluence = fm.data.get("confluence") or {}
    page_id = str(confluence.get("page_id") or "")
    last_published = int(confluence.get("last_published_version") or 0)

    page_index = _load_page_index(args.page_index)
    transformed, report = transform_markdown(
        fm.body,
        source_doc_path=str(source_path),
        page_index=page_index,
        options=TransformOptions(
            miss_policy=args.miss_policy,
            strip_internal=getattr(args, "strip_internal", False),
        ),
    )

    # Capture zones from the current ADF (only meaningful for existing pages)
    captured_zones: list[dict] = []
    diverged = False
    current_version = 0
    diff = ""
    snapshot = ""
    if args.current_adf:
        adf = _adf_from_mcp_response(json.loads(Path(args.current_adf).read_text(encoding="utf-8")))
        zones = extract_zones(adf)
        captured_zones = [z.to_dict() for z in zones.values()]
        # The agent passes the full MCP response dict — pull `version.number` if present.
        try:
            raw = json.loads(Path(args.current_adf).read_text(encoding="utf-8"))
            current_version = int(((raw.get("version") or {}).get("number")) or 0)
        except (ValueError, TypeError):
            current_version = 0
        if current_version > last_published > 0:
            diverged = True
            their_md = normalize_for_diff(adf)
            snapshot = read_snapshot(page_id, last_published, cache_root=args.cache_root) or ""
            diff = compute_diff(
                snapshot,
                their_md,
                from_label=f"snapshot@v{last_published}",
                to_label=f"confluence@v{current_version}",
            )

    out = {
        "page_id": page_id,
        "last_published_version": last_published,
        "is_first_publish": page_id == "" or last_published == 0,
        "transformed_body_chars": len(transformed),
        "transform_report": {
            "rewrote": report.rewrote,
            "missed": report.missed,
            "fence_swaps": report.fence_swaps,
            "frontmatter_stripped": report.frontmatter_stripped,
            "internal_blocks_stripped": report.internal_blocks_stripped,
            "internal_zones_stripped": report.internal_zones_stripped,
        },
        "zones_captured": captured_zones,
        "diverged": diverged,
        "current_version": current_version,
        "their_diff": diff,
        "snapshot_present": bool(snapshot),
    }
    sys.stdout.write(json.dumps(out, indent=2) + "\n")
    return 0


def cmd_body(args: argparse.Namespace) -> int:
    source_path = Path(args.source)
    fm = read_frontmatter(source_path)
    page_index = _load_page_index(args.page_index)
    transformed, _ = transform_markdown(
        fm.body,
        source_doc_path=str(source_path),
        page_index=page_index,
        options=TransformOptions(
            miss_policy=args.miss_policy,
            strip_internal=getattr(args, "strip_internal", False),
        ),
    )
    sys.stdout.write(transformed)
    return 0


def _md_to_storage_html(md: str) -> str:
    """Convert our adopt-shape markdown to Confluence storage HTML.

    Handles:
      - `> **[success]**` blockquotes → <div data-type="panel-success">
      - `<u>...</u>` inline → preserved (HTML inline allowed in storage)
      - `[label](URL)<!-- smartcard -->` → <a href="URL" data-card-appearance="inline">label</a>
      - `<!-- confluence-side: <key> -->` → native macro placeholder div the
        ADF post-splice (Probe J) replaces with the real extension node.
        For first-publish, drop the bookkeeping comment but emit a TOC macro
        directly when key=="toc" so the rendered page has a working ToC.
      - Headings (#, ##, ###) → <h1>…<h3>
      - Paragraphs, bullet/ordered lists, tables, hr → standard HTML
      - Inline: **bold**, *italic*, `code`, [link](url) → standard HTML

    Best-effort plain-md transform — designed for our adopt output, not a
    general markdown parser. Inputs outside the adopt shape may render
    raw HTML-escaped where the shape doesn't match.
    """
    import re as _re
    import html as _html

    lines = md.splitlines()
    out: list[str] = []
    i = 0

    INLINE_LINK_SC = _re.compile(r"\[([^\]]+)\]\(([^)]+)\)<!-- smartcard -->")
    INLINE_AUTO_SC = _re.compile(r"<([^>]+)><!-- smartcard -->")
    INLINE_LINK = _re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
    INLINE_BOLD_IT = _re.compile(r"\*\*\*([^*]+)\*\*\*")
    INLINE_BOLD = _re.compile(r"\*\*([^*]+)\*\*")
    INLINE_IT = _re.compile(r"(?<!\*)\*([^*\n]+)\*(?!\*)")
    INLINE_CODE = _re.compile(r"`([^`]+)`")
    INLINE_U = _re.compile(r"<u>([^<]+)</u>")

    def _inline(text: str) -> str:
        # Pull out underlines, smartcards and other anchored shapes BEFORE
        # html-escaping so the surrounding `<` / `>` don't get mangled.
        # Strategy: tokenize protected runs, escape the rest, re-stitch.
        tokens: list[tuple[str, str]] = []  # (kind, content)
        cursor = 0

        def consume(pattern, kind_fn):
            nonlocal cursor
            for m in pattern.finditer(text, cursor):
                if m.start() < cursor:
                    continue
                if m.start() > cursor:
                    tokens.append(("text", text[cursor:m.start()]))
                tokens.append(kind_fn(m))
                cursor = m.end()

        # Pass 1 — anchored shapes that contain markup we don't want escaped.
        # Order matters: smartcard link must be matched before plain link.
        # Build a single combined pass using one regex with alternation.
        combined = _re.compile(
            r"(\[[^\]]+\]\([^)]+\)<!-- smartcard -->)"
            r"|(<[^>]+><!-- smartcard -->)"
            r"|(<u>[^<]+</u>)"
            r"|(\[[^\]]+\]\([^)]+\))"
            r"|(`[^`]+`)"
        )
        cursor = 0
        for m in combined.finditer(text):
            if m.start() > cursor:
                tokens.append(("text", text[cursor:m.start()]))
            seg = m.group(0)
            if "<!-- smartcard -->" in seg and seg.startswith("["):
                mm = INLINE_LINK_SC.match(seg)
                tokens.append((
                    "html",
                    f'<a href="{_html.escape(mm.group(2), quote=True)}" data-card-appearance="inline">{_html.escape(mm.group(1))}</a>'
                ))
            elif "<!-- smartcard -->" in seg:
                mm = INLINE_AUTO_SC.match(seg)
                u = mm.group(1)
                tokens.append((
                    "html",
                    f'<a href="{_html.escape(u, quote=True)}" data-card-appearance="inline">{_html.escape(u)}</a>'
                ))
            elif seg.startswith("<u>"):
                mm = INLINE_U.match(seg)
                tokens.append(("html", f"<u>{_html.escape(mm.group(1))}</u>"))
            elif seg.startswith("["):
                mm = INLINE_LINK.match(seg)
                tokens.append((
                    "html",
                    f'<a href="{_html.escape(mm.group(2), quote=True)}">{_html.escape(mm.group(1))}</a>'
                ))
            elif seg.startswith("`"):
                mm = INLINE_CODE.match(seg)
                tokens.append(("html", f"<code>{_html.escape(mm.group(1))}</code>"))
            cursor = m.end()
        if cursor < len(text):
            tokens.append(("text", text[cursor:]))

        # Pass 2 — escape text tokens, then apply bold/italic on escaped text.
        result_parts: list[str] = []
        for kind, content in tokens:
            if kind == "html":
                result_parts.append(content)
            else:
                esc = _html.escape(content, quote=False)
                esc = INLINE_BOLD_IT.sub(r"<strong><em>\1</em></strong>", esc)
                esc = INLINE_BOLD.sub(r"<strong>\1</strong>", esc)
                esc = INLINE_IT.sub(r"<em>\1</em>", esc)
                result_parts.append(esc)
        return "".join(result_parts)

    def _flush_block_paragraph(buf: list[str]) -> None:
        if not buf:
            return
        joined = " ".join(buf).strip()
        if joined:
            out.append(f"<p>{_inline(joined)}</p>")
        buf.clear()

    para_buf: list[str] = []

    def _table_block(start: int) -> tuple[str, int]:
        # Parses a GFM table starting at `start` (header line). Returns
        # (html, next_index_after_table).
        rows: list[list[str]] = []
        j = start
        while j < len(lines) and lines[j].strip().startswith("|"):
            row = lines[j].strip()
            cells = [c.strip() for c in row.strip("|").split("|")]
            rows.append(cells)
            j += 1
        if len(rows) < 2:
            return ("", start)  # not a real table
        # Row 1 is the header, row 2 is the separator (--- | ---), rest are body.
        sep_row = rows[1]
        if not all(_re.match(r"^:?-+:?$", c) for c in sep_row if c):
            return ("", start)
        head = rows[0]
        body = rows[2:]
        n = max(len(head), max((len(r) for r in body), default=0))
        head = head + [""] * (n - len(head))
        body = [r + [""] * (n - len(r)) for r in body]
        html_rows = ['<table data-layout="default"><tbody>']
        html_rows.append("<tr>" + "".join(f"<th><p>{_inline(c)}</p></th>" for c in head) + "</tr>")
        for r in body:
            html_rows.append("<tr>" + "".join(f"<td><p>{_inline(c)}</p></td>" for c in r) + "</tr>")
        html_rows.append("</tbody></table>")
        return ("".join(html_rows), j)

    def _list_block(start: int, ordered: bool) -> tuple[str, int]:
        tag = "ol" if ordered else "ul"
        items: list[str] = []
        j = start
        item_re = _re.compile(r"^\s*(?:\d+\.|[-*])\s+(.*)$")
        while j < len(lines):
            ln = lines[j]
            if not ln.strip():
                # blank line might be in-list separator; peek ahead
                if j + 1 < len(lines) and item_re.match(lines[j+1]):
                    j += 1
                    continue
                break
            m = item_re.match(ln)
            if not m:
                break
            items.append(f"<li><p>{_inline(m.group(1))}</p></li>")
            j += 1
        return (f"<{tag}>" + "".join(items) + f"</{tag}>", j)

    def _blockquote_block(start: int) -> tuple[str, int]:
        # Collect contiguous `> ...` lines (and `>` blank lines).
        body_lines: list[str] = []
        j = start
        while j < len(lines):
            ln = lines[j]
            if ln.startswith("> "):
                body_lines.append(ln[2:])
            elif ln.strip() == ">":
                body_lines.append("")
            else:
                break
            j += 1
        # Detect panel marker: first non-empty line is `**[success]**` etc.
        panel_type: str | None = None
        first = next((b for b in body_lines if b.strip()), "")
        m = _re.match(r"\*\*\[(success|info|note|warning|error)\]\*\*\s*(.*)$", first)
        body_md = "\n".join(body_lines).strip()
        if m:
            panel_type = m.group(1)
            tail = m.group(2)
            # Drop the `**[type]**` prefix from the body (and the line if empty after)
            new_lines = []
            removed = False
            for b in body_lines:
                if not removed and b.strip().startswith(f"**[{panel_type}]**"):
                    rest = b.strip()[len(f"**[{panel_type}]**"):].strip()
                    if rest:
                        new_lines.append(rest)
                    removed = True
                else:
                    new_lines.append(b)
            body_md = "\n".join(new_lines).strip()
        # Recursively render the inner body as md → html
        inner_html = _md_to_storage_html(body_md) if body_md else ""
        if panel_type:
            return (f'<div data-type="panel-{panel_type}">{inner_html}</div>', j)
        return (f"<blockquote>{inner_html}</blockquote>", j)

    while i < len(lines):
        ln = lines[i]
        stripped = ln.strip()

        # Attachments-macro OPEN sentinel — skip to CLOSE and emit a single
        # storage-format `attachments` macro with the captured params.
        m_att_open = _re.match(
            r"<!--\s*confluence-side:\s*attachments\b([^>]*?)-->",
            stripped,
        )
        if m_att_open:
            _flush_block_paragraph(para_buf)
            attrs_text = m_att_open.group(1)
            position_m = _re.search(r"position=(\S+?)(?:\s|$)", attrs_text)
            position = position_m.group(1).strip() if position_m else None
            labels_m = _re.search(r"labels=([^\s>]+)", attrs_text)
            labels = labels_m.group(1).strip() if labels_m else None
            # Walk forward until we find the matching CLOSE sentinel.
            j = i + 1
            while j < len(lines):
                close_m = _re.match(
                    r"<!--\s*/confluence-side:\s*attachments\b([^>]*?)-->",
                    lines[j].strip(),
                )
                if close_m:
                    close_attrs = close_m.group(1)
                    close_pos = _re.search(r"position=(\S+?)(?:\s|$)", close_attrs)
                    if (
                        position is None
                        or close_pos is None
                        or close_pos.group(1).strip() == position
                    ):
                        break
                j += 1
            macro_xml = '<ac:structured-macro ac:name="attachments" ac:schema-version="1">'
            if labels:
                macro_xml += (
                    '<ac:parameter ac:name="labels">'
                    + labels
                    + "</ac:parameter>"
                )
            macro_xml += "</ac:structured-macro>"
            out.append(macro_xml)
            i = j + 1 if j < len(lines) else j
            continue

        # Confluence-side zone sentinels — emit native macro extensions where
        # we can (TOC most importantly), drop the rest as bookkeeping. Real
        # macro injection still comes via post-publish ADF splice (Probe J)
        # for plugins like Document Control; this fast path keeps the page
        # functional on first-publish without the splice round-trip.
        m_zone = _re.match(r"<!--\s*confluence-side:\s*([\w-]+)\s*-->", stripped)
        if m_zone:
            _flush_block_paragraph(para_buf)
            key = m_zone.group(1)
            if key == "toc":
                # Confluence storage TOC macro
                out.append(
                    '<ac:structured-macro ac:name="toc" ac:schema-version="1">'
                    '<ac:parameter ac:name="minLevel">1</ac:parameter>'
                    '<ac:parameter ac:name="maxLevel">6</ac:parameter>'
                    '<ac:parameter ac:name="outline">true</ac:parameter>'
                    '<ac:parameter ac:name="style">none</ac:parameter>'
                    '<ac:parameter ac:name="type">list</ac:parameter>'
                    "</ac:structured-macro>"
                )
            elif key == "children":
                out.append(
                    '<ac:structured-macro ac:name="children" ac:schema-version="2"/>'
                )
            elif key == "page-signatures":
                # Third-party plugin macro — handled via post-splice; emit a
                # tagged placeholder so the splice can find/replace it.
                out.append(
                    '<p data-cc-placeholder="page-signatures">'
                    '<em>[Document Control signatures — re-injected on splice]</em></p>'
                )
            # else: drop unknown zone keys silently
            i += 1
            continue

        # Smartcard-only marker line (rare — strip)
        if stripped == "<!-- smartcard -->":
            i += 1
            continue

        # Heading
        m_h = _re.match(r"^(#{1,6})\s+(.*)$", stripped)
        if m_h:
            _flush_block_paragraph(para_buf)
            level = len(m_h.group(1))
            out.append(f"<h{level}>{_inline(m_h.group(2))}</h{level}>")
            i += 1
            continue

        # Horizontal rule
        if stripped in ("---", "***", "___"):
            _flush_block_paragraph(para_buf)
            out.append("<hr/>")
            i += 1
            continue

        # Blockquote (incl. our success-panel pattern)
        if ln.startswith(">"):
            _flush_block_paragraph(para_buf)
            html, ni = _blockquote_block(i)
            out.append(html)
            i = ni
            continue

        # Tables (line starts with `|` and next line is separator)
        if stripped.startswith("|") and i + 1 < len(lines) and _re.match(r"^\|[\s|:-]+\|$", lines[i+1].strip()):
            _flush_block_paragraph(para_buf)
            html, ni = _table_block(i)
            if html:
                out.append(html)
                i = ni
                continue

        # Lists
        if _re.match(r"^\s*\d+\.\s+", ln):
            _flush_block_paragraph(para_buf)
            html, ni = _list_block(i, ordered=True)
            out.append(html)
            i = ni
            continue
        if _re.match(r"^\s*[-*]\s+", ln):
            _flush_block_paragraph(para_buf)
            html, ni = _list_block(i, ordered=False)
            out.append(html)
            i = ni
            continue

        # Blank line
        if not stripped:
            _flush_block_paragraph(para_buf)
            i += 1
            continue

        # Default: paragraph accumulation
        para_buf.append(stripped)
        i += 1

    _flush_block_paragraph(para_buf)
    return "".join(out)


def _md_to_adf(md: str, images_collector: list[dict] | None = None) -> dict:
    """Convert our adopt-shape markdown to ADF JSON.

    Targeted converter — handles every shape produced by the normalizer:
    panels (`> **[success]**`), underlines (`<u>`), smartcards
    (`[label](URL)<!-- smartcard -->`), zone sentinels
    (`<!-- confluence-side: <key> -->` → ADF `extension` node), headings,
    paragraphs, lists, tables, hr, basic inline marks (bold/italic/code/link).

    Returns a doc node ready to JSON-serialize: `{"type": "doc",
    "version": 1, "content": [...]}`.
    """
    import re as _re

    # Match order matters: image markdown `![alt](url)` must precede the
    # plain-link pattern, otherwise the leading `!` would become text and
    # the rest would be parsed as a regular link. Same with smartcard
    # variants — anchored shapes first, generic last.
    INLINE_TOKENS = _re.compile(
        r"(!\[[^\]]*\]\([^)]+\)(?:<!-- media[^>]*-->)?)"
        r"|(\[[^\]]+\]\([^)]+\)<!-- media[^>]*-->)"
        r"|(\[[^\]]+\]\([^)]+\)<!-- smartcard -->)"
        r"|(<[^>]+><!-- smartcard -->)"
        r"|(<u>[^<]+</u>)"
        r"|(\[[^\]]+\]\([^)]+\))"
        r"|(`[^`]+`)"
        r"|(\*\*\*[^*]+\*\*\*)"
        r"|(\*\*[^*]+\*\*)"
        r"|(?<!\*)(\*[^*\n]+\*)(?!\*)"
    )

    def _text(content: str, marks: list[dict] | None = None) -> dict:
        node = {"type": "text", "text": content}
        if marks:
            node["marks"] = marks
        return node

    def _emit_media_node(alt: str, ref: str) -> dict:
        """Build an ADF `media` node placeholder for a local image
        reference. The `id` carries `PLACEHOLDER:<relpath>` so the action
        layer can swap it for a real attachment id after upload. We only
        treat refs that look like our adopt-shape (`images/<file>`) as
        local media — external/HTTP refs stay as plain links since we
        can't upload them as attachments without first downloading.

        Markdown link destinations are URL-encoded on the adopt side
        (see `lib.markdown_transform.md_link_dest`); decode here before
        anything tries to map the ref to a local file path.
        """
        # Decode the URL slot so spaces / parens / non-ASCII filenames
        # round-trip back to the on-disk relpath.
        try:
            from lib.markdown_transform import md_link_dest_decode  # noqa: WPS433
            ref = md_link_dest_decode(ref)
        except Exception:  # noqa: BLE001 — keep raw ref if decode fails
            pass
        is_local = ref.startswith("images/") or ref.startswith("./images/")
        node_id = f"PLACEHOLDER:{ref}" if is_local else ref
        node: dict = {
            "type": "media",
            "attrs": {
                "type": "file" if is_local else "external",
                "id": node_id,
                "collection": "",
            },
        }
        if not is_local:
            # External image — Confluence's ADF renderer accepts a `url`
            # field on type=external media nodes. Local refs only need
            # the placeholder id.
            node["attrs"]["url"] = ref
        if alt:
            node["attrs"]["alt"] = alt
        if images_collector is not None and is_local:
            images_collector.append({
                "placeholder": node_id,
                "source_relpath": ref,
                "alt": alt,
            })
        return node

    def _inline_nodes(text: str) -> list[dict]:
        """Split text into ADF inline nodes (text + inlineCard).

        Inline images are still emitted at the inline scope (rare —
        usually images are block-level in our adopt output, handled by
        the paragraph-image detector below). For inline occurrences we
        wrap the media node in a `mediaInline` parent if it lands
        mid-paragraph, otherwise the block-level path picks it up
        before we get here.
        """
        out: list[dict] = []
        cursor = 0
        for m in INLINE_TOKENS.finditer(text):
            if m.start() > cursor:
                pre = text[cursor:m.start()]
                if pre:
                    out.append(_text(pre))
            seg = m.group(0)
            if seg.startswith("!["):
                # Inline image — emit a `mediaInline` wrapping the media
                # node. ADF allows `mediaInline` mid-paragraph; the more
                # common shape is block-level `mediaSingle`, handled in
                # the paragraph detector before _inline_nodes is called.
                mm = _re.match(
                    r"!\[([^\]]*)\]\(([^)]+)\)(?:<!-- media[^>]*-->)?",
                    seg,
                )
                alt, ref = mm.group(1), mm.group(2)
                media = _emit_media_node(alt, ref)
                out.append({"type": "mediaInline", "attrs": media["attrs"]})
                cursor = m.end()
                continue
            if "<!-- media" in seg and seg.startswith("["):
                # File-card link `[filename](images/filename)<!-- media [inline ]id=UUID collection=... -->`
                # → ADF mediaInline with type=file. The `inline` flag in the
                # marker indicates the source was a `mediaInline` node (was
                # emitted in inline context). Emit mediaInline with placeholder id.
                mm = _re.match(
                    r"\[([^\]]+)\]\(([^)]+)\)<!-- media([^>]*)-->",
                    seg,
                )
                label, ref = mm.group(1), mm.group(2)
                media = _emit_media_node(label, ref)
                # File-cards always emit as mediaInline regardless of marker
                # flags — that's the inline-safe ADF shape Confluence
                # renders as the file-card chrome (filename pill +
                # download button).
                out.append({"type": "mediaInline", "attrs": media["attrs"]})
                cursor = m.end()
                continue
            if "<!-- smartcard -->" in seg and seg.startswith("["):
                mm = _re.match(r"\[([^\]]+)\]\(([^)]+)\)<!-- smartcard -->", seg)
                out.append({"type": "inlineCard", "attrs": {"url": mm.group(2)}})
            elif "<!-- smartcard -->" in seg:
                mm = _re.match(r"<([^>]+)><!-- smartcard -->", seg)
                out.append({"type": "inlineCard", "attrs": {"url": mm.group(1)}})
            elif seg.startswith("<u>"):
                mm = _re.match(r"<u>([^<]+)</u>", seg)
                out.append(_text(mm.group(1), [{"type": "underline"}]))
            elif seg.startswith("["):
                mm = _re.match(r"\[([^\]]+)\]\(([^)]+)\)", seg)
                label, dest = mm.group(1), mm.group(2)
                # NEW (v0.11.0): plain markdown link (no round-trip marker)
                # whose destination starts with `images/` is treated as a
                # Confluence-attachment binding. This lets users drop a file
                # in `<page>/images/` + write `[label](images/X.pdf)` and
                # publish-roundtrip works without manual marker bookkeeping.
                # We URL-decode first so encoded refs match.
                try:
                    from lib.markdown_transform import md_link_dest_decode  # noqa: WPS433
                    decoded = md_link_dest_decode(dest)
                except Exception:  # noqa: BLE001
                    decoded = dest
                if decoded.startswith("images/") or decoded.startswith("./images/"):
                    media = _emit_media_node(label, dest)
                    out.append({"type": "mediaInline", "attrs": media["attrs"]})
                else:
                    out.append(_text(label, [{"type": "link", "attrs": {"href": dest}}]))
            elif seg.startswith("`"):
                mm = _re.match(r"`([^`]+)`", seg)
                out.append(_text(mm.group(1), [{"type": "code"}]))
            elif seg.startswith("***"):
                mm = _re.match(r"\*\*\*([^*]+)\*\*\*", seg)
                out.append(_text(mm.group(1), [{"type": "strong"}, {"type": "em"}]))
            elif seg.startswith("**"):
                mm = _re.match(r"\*\*([^*]+)\*\*", seg)
                out.append(_text(mm.group(1), [{"type": "strong"}]))
            else:
                mm = _re.match(r"\*([^*\n]+)\*", seg)
                out.append(_text(mm.group(1), [{"type": "em"}]))
            cursor = m.end()
        if cursor < len(text):
            tail = text[cursor:]
            if tail:
                out.append(_text(tail))
        return out

    def _para(text: str) -> dict:
        return {"type": "paragraph", "content": _inline_nodes(text)}

    def _heading(level: int, text: str) -> dict:
        return {"type": "heading", "attrs": {"level": level}, "content": _inline_nodes(text)}

    def _list_item(text: str) -> dict:
        return {"type": "listItem", "content": [_para(text)]}

    def _walk(lines: list[str]) -> list[dict]:
        nodes: list[dict] = []
        i = 0
        while i < len(lines):
            ln = lines[i]
            stripped = ln.strip()

            # AUTO:PAGE-TITLE OPEN sentinel (task 140 / v0.13.0) —
            # strip the entire region. Confluence renders its own title
            # chrome from the API's `title` argument; the AUTO block is a
            # local viewing aid only and contributes nothing to the ADF.
            m_pt_open = _re.match(
                r"<!--\s*AUTO:PAGE-TITLE\b([^>]*?)-->",
                stripped,
            )
            if m_pt_open:
                j = i + 1
                while j < len(lines):
                    if _re.match(
                        r"<!--\s*/AUTO:PAGE-TITLE\b([^>]*?)-->",
                        lines[j].strip(),
                    ):
                        break
                    j += 1
                # Emit nothing — the title goes through the API arg.
                i = j + 1 if j < len(lines) else j
                continue

            # AUTO:TOC OPEN sentinel (task 140 / v0.13.0) — skip the
            # rendered anchor list and emit a single ADF `extension`
            # node with extensionKey="toc" and reconstructed macroParams.
            m_toc_open = _re.match(
                r"<!--\s*AUTO:TOC\b([^>]*?)-->",
                stripped,
            )
            if m_toc_open:
                attrs_text = m_toc_open.group(1)
                position_m = _re.search(
                    r"position=(\S+?)(?:\s|$)", attrs_text
                )
                position = position_m.group(1).strip() if position_m else None
                min_m = _re.search(r"minLevel=(\S+?)(?:\s|$)", attrs_text)
                max_m = _re.search(r"maxLevel=(\S+?)(?:\s|$)", attrs_text)
                min_level = min_m.group(1).strip() if min_m else None
                max_level = max_m.group(1).strip() if max_m else None
                # Walk to matching CLOSE
                j = i + 1
                while j < len(lines):
                    close_m = _re.match(
                        r"<!--\s*/AUTO:TOC\b([^>]*?)-->",
                        lines[j].strip(),
                    )
                    if close_m:
                        close_attrs = close_m.group(1)
                        close_pos = _re.search(
                            r"position=(\S+?)(?:\s|$)", close_attrs
                        )
                        if (
                            position is None
                            or close_pos is None
                            or close_pos.group(1).strip() == position
                        ):
                            break
                    j += 1
                toc_params: dict[str, dict] = {}
                if min_level is not None:
                    toc_params["minLevel"] = {"value": min_level}
                if max_level is not None:
                    toc_params["maxLevel"] = {"value": max_level}
                nodes.append({
                    "type": "extension",
                    "attrs": {
                        "layout": "default",
                        "extensionType": "com.atlassian.confluence.macro.core",
                        "extensionKey": "toc",
                        "parameters": {
                            "macroParams": toc_params,
                            "macroMetadata": {"title": "Table of Contents"},
                        },
                    },
                })
                i = j + 1 if j < len(lines) else j
                continue

            # AUTO:CHILD-INDEX OPEN sentinel — skip the rendered TOC and
            # emit a single ADF `extension` node with key children/pagetree
            # reconstructed from `source=<kind>`. For `source=stub-container`
            # there was no source macro — fully strip, emit nothing.
            m_ci_open = _re.match(
                r"<!--\s*AUTO:CHILD-INDEX\b([^>]*?)-->",
                stripped,
            )
            if m_ci_open:
                attrs_text = m_ci_open.group(1)
                position_m = _re.search(
                    r"position=(\S+?)(?:\s|$)", attrs_text
                )
                position = position_m.group(1).strip() if position_m else None
                source_m = _re.search(r"source=(\S+?)(?:\s|$)", attrs_text)
                source = source_m.group(1).strip() if source_m else "children"
                depth_m = _re.search(r"depth=(\S+?)(?:\s|$)", attrs_text)
                depth_v = depth_m.group(1).strip() if depth_m else None
                # Walk to matching CLOSE
                j = i + 1
                while j < len(lines):
                    close_m = _re.match(
                        r"<!--\s*/AUTO:CHILD-INDEX\b([^>]*?)-->",
                        lines[j].strip(),
                    )
                    if close_m:
                        close_attrs = close_m.group(1)
                        close_pos = _re.search(
                            r"position=(\S+?)(?:\s|$)", close_attrs
                        )
                        if (
                            position is None
                            or close_pos is None
                            or close_pos.group(1).strip() == position
                        ):
                            break
                    j += 1
                if source != "stub-container":
                    macro_params: dict[str, dict] = {}
                    if depth_v:
                        macro_params["depth"] = {"value": depth_v}
                    nodes.append({
                        "type": "extension",
                        "attrs": {
                            "layout": "default",
                            "extensionType": "com.atlassian.confluence.macro.core",
                            "extensionKey": source,
                            "parameters": {
                                "macroParams": macro_params,
                                "macroMetadata": {
                                    "title": (
                                        "Page Tree" if source == "pagetree"
                                        else "Child pages"
                                    )
                                },
                            },
                        },
                    })
                # else: stub-container — emit nothing, fully strip.
                # Also drop any preceding "## Child pages" heading that
                # the synthesizer emitted (look back one or two nodes).
                if source == "stub-container" and nodes:
                    last = nodes[-1]
                    # Heading text "Child pages" with level 2
                    if (
                        isinstance(last, dict)
                        and last.get("type") == "heading"
                        and (last.get("attrs") or {}).get("level") == 2
                    ):
                        content = last.get("content") or []
                        if (
                            len(content) == 1
                            and content[0].get("type") == "text"
                            and content[0].get("text") == "Child pages"
                        ):
                            nodes.pop()
                i = j + 1 if j < len(lines) else j
                continue

            # AUTO:JIRA-LIST OPEN sentinel — skip rendered table and
            # emit a single ADF `extension` node with key=jira and
            # reconstructed jqlQuery.
            m_jl_open = _re.match(
                r"<!--\s*AUTO:JIRA-LIST\b([^>]*?)-->",
                stripped,
            )
            if m_jl_open:
                attrs_text = m_jl_open.group(1)
                position_m = _re.search(
                    r"position=(\S+?)(?:\s|$)", attrs_text
                )
                position = position_m.group(1).strip() if position_m else None
                jql_m = _re.search(r"jql=(\S+?)(?:\s|$)", attrs_text)
                from urllib.parse import unquote
                jql_v = unquote(jql_m.group(1).strip()) if jql_m else None
                # Walk to matching CLOSE
                j = i + 1
                while j < len(lines):
                    close_m = _re.match(
                        r"<!--\s*/AUTO:JIRA-LIST\b([^>]*?)-->",
                        lines[j].strip(),
                    )
                    if close_m:
                        close_attrs = close_m.group(1)
                        close_pos = _re.search(
                            r"position=(\S+?)(?:\s|$)", close_attrs
                        )
                        if (
                            position is None
                            or close_pos is None
                            or close_pos.group(1).strip() == position
                        ):
                            break
                    j += 1
                jira_params: dict[str, dict] = {}
                if jql_v:
                    jira_params["jqlQuery"] = {"value": jql_v}
                nodes.append({
                    "type": "extension",
                    "attrs": {
                        "layout": "default",
                        "extensionType": "com.atlassian.confluence.macro.core",
                        "extensionKey": "jira",
                        "parameters": {
                            "macroParams": jira_params,
                            "macroMetadata": {"title": "Jira issues"},
                        },
                    },
                })
                i = j + 1 if j < len(lines) else j
                continue

            # Attachments-macro OPEN sentinel — skip to matching CLOSE
            # and emit a single ADF `extension` node with the captured
            # macro params (labels, name) reconstructed from the sentinel
            # attribute slot.
            m_att_open = _re.match(
                r"<!--\s*confluence-side:\s*attachments\b([^>]*?)-->",
                stripped,
            )
            if m_att_open:
                attrs_text = m_att_open.group(1)
                position_m = _re.search(r"position=(\S+?)(?:\s|$)", attrs_text)
                position = position_m.group(1).strip() if position_m else None
                labels_m = _re.search(r"labels=([^\s>]+)", attrs_text)
                labels = labels_m.group(1).strip() if labels_m else None
                name_m = _re.search(r"\bname=([^\s>]+)", attrs_text)
                name_filter = name_m.group(1).strip() if name_m else None
                # Walk forward to the matching CLOSE sentinel.
                j = i + 1
                while j < len(lines):
                    close_m = _re.match(
                        r"<!--\s*/confluence-side:\s*attachments\b([^>]*?)-->",
                        lines[j].strip(),
                    )
                    if close_m:
                        close_attrs = close_m.group(1)
                        close_pos = _re.search(
                            r"position=(\S+?)(?:\s|$)", close_attrs
                        )
                        if (
                            position is None
                            or close_pos is None
                            or close_pos.group(1).strip() == position
                        ):
                            break
                    j += 1
                macro_params: dict[str, dict] = {}
                if labels is not None:
                    macro_params["labels"] = {"value": labels}
                if name_filter is not None:
                    macro_params["name"] = {"value": name_filter}
                nodes.append({
                    "type": "extension",
                    "attrs": {
                        "layout": "default",
                        "extensionType": "com.atlassian.confluence.macro.core",
                        "extensionKey": "attachments",
                        "parameters": {
                            "macroParams": macro_params,
                            "macroMetadata": {"title": "Attachments"},
                        },
                    },
                })
                i = j + 1 if j < len(lines) else j
                continue

            # Zone sentinels — emit native ADF extension nodes
            mz = _re.match(r"<!--\s*confluence-side:\s*([\w-]+)\s*-->", stripped)
            if mz:
                key = mz.group(1)
                if key == "toc":
                    nodes.append({
                        "type": "extension",
                        "attrs": {
                            "layout": "default",
                            "extensionType": "com.atlassian.confluence.macro.core",
                            "extensionKey": "toc",
                            "parameters": {
                                "macroParams": {
                                    "minLevel": {"value": "1"},
                                    "maxLevel": {"value": "6"},
                                    "outline": {"value": "true"},
                                    "style": {"value": "none"},
                                    "type": {"value": "list"},
                                },
                                "macroMetadata": {"title": "Table of Contents"},
                            },
                        },
                    })
                elif key == "children":
                    nodes.append({
                        "type": "extension",
                        "attrs": {
                            "layout": "default",
                            "extensionType": "com.atlassian.confluence.macro.core",
                            "extensionKey": "children",
                            "parameters": {"macroParams": {}, "macroMetadata": {"title": "Child pages"}},
                        },
                    })
                elif key == "page-signatures":
                    # Plugin-owned macro; emit a marker paragraph the splice
                    # phase replaces with the third-party extension node.
                    nodes.append(_para("[Document Control signatures — re-injected on splice]"))
                # else: drop unknown keys
                i += 1
                continue

            # Skip stray smartcard markers
            if stripped == "<!-- smartcard -->":
                i += 1; continue

            # Heading
            mh = _re.match(r"^(#{1,6})\s+(.*)$", stripped)
            if mh:
                nodes.append(_heading(len(mh.group(1)), mh.group(2)))
                i += 1; continue

            # Horizontal rule
            if stripped in ("---", "***", "___"):
                nodes.append({"type": "rule"})
                i += 1; continue

            # Blockquote / panel
            if ln.startswith(">"):
                body_lines: list[str] = []
                j = i
                while j < len(lines):
                    l2 = lines[j]
                    if l2.startswith("> "):
                        body_lines.append(l2[2:])
                    elif l2.strip() == ">":
                        body_lines.append("")
                    else:
                        break
                    j += 1
                first_nonempty = next((b for b in body_lines if b.strip()), "")
                m_panel = _re.match(r"^\*\*\[(success|info|note|warning|error)\]\*\*\s*(.*)$", first_nonempty)
                if m_panel:
                    panel_type = m_panel.group(1)
                    new_body: list[str] = []
                    removed = False
                    for b in body_lines:
                        if not removed and b.strip().startswith(f"**[{panel_type}]**"):
                            tail = b.strip()[len(f"**[{panel_type}]**"):].strip()
                            if tail:
                                new_body.append(tail)
                            removed = True
                        else:
                            new_body.append(b)
                    inner = _walk(new_body)
                    nodes.append({"type": "panel", "attrs": {"panelType": panel_type}, "content": inner})
                else:
                    inner = _walk(body_lines)
                    nodes.append({"type": "blockquote", "content": inner})
                i = j; continue

            # Tables
            if stripped.startswith("|") and i + 1 < len(lines) and _re.match(r"^\|[\s|:-]+\|$", lines[i+1].strip()):
                rows: list[list[str]] = []
                j = i
                while j < len(lines) and lines[j].strip().startswith("|"):
                    cells = [c.strip() for c in lines[j].strip().strip("|").split("|")]
                    rows.append(cells)
                    j += 1
                if len(rows) >= 2 and all(_re.match(r"^:?-+:?$", c) for c in rows[1] if c):
                    head = rows[0]
                    body = rows[2:]
                    n = max(len(head), max((len(r) for r in body), default=0))
                    head = head + [""] * (n - len(head))
                    body = [r + [""] * (n - len(r)) for r in body]
                    table_rows = []
                    table_rows.append({"type": "tableRow", "content": [
                        {"type": "tableHeader", "attrs": {}, "content": [_para(c)]} for c in head
                    ]})
                    for r in body:
                        table_rows.append({"type": "tableRow", "content": [
                            {"type": "tableCell", "attrs": {}, "content": [_para(c)]} for c in r
                        ]})
                    nodes.append({"type": "table", "attrs": {"layout": "default"}, "content": table_rows})
                    i = j; continue

            # Lists
            if _re.match(r"^\s*\d+\.\s+", ln):
                items = []
                j = i
                while j < len(lines):
                    m_li = _re.match(r"^\s*\d+\.\s+(.*)$", lines[j])
                    if not m_li:
                        if lines[j].strip() == "":
                            j += 1; continue
                        break
                    items.append(_list_item(m_li.group(1)))
                    j += 1
                nodes.append({"type": "orderedList", "attrs": {"order": 1}, "content": items})
                i = j; continue
            if _re.match(r"^\s*[-*]\s+", ln):
                items = []
                j = i
                while j < len(lines):
                    m_li = _re.match(r"^\s*[-*]\s+(.*)$", lines[j])
                    if not m_li:
                        if lines[j].strip() == "":
                            j += 1; continue
                        break
                    items.append(_list_item(m_li.group(1)))
                    j += 1
                nodes.append({"type": "bulletList", "content": items})
                i = j; continue

            # Blank — skip
            if not stripped:
                i += 1; continue

            # Standalone image line — promote to a `mediaSingle` block.
            # The whole line must be a single image markdown ref
            # (optionally followed by our `<!-- media ... -->` marker
            # comment). Inline images mid-paragraph fall through to the
            # `_inline_nodes` mediaInline branch.
            m_img = _re.match(
                r"^!\[([^\]]*)\]\(([^)]+)\)(?:<!--\s*media[^>]*-->)?\s*$",
                stripped,
            )
            if m_img:
                alt, ref = m_img.group(1), m_img.group(2)
                media = _emit_media_node(alt, ref)
                nodes.append({
                    "type": "mediaSingle",
                    "attrs": {"layout": "center"},
                    "content": [media],
                })
                i += 1
                continue

            # NEW (v0.11.0): standalone file-card line — a paragraph that's
            # just `[label](images/X)` (with or without round-trip marker).
            # Promote to mediaSingle with type=file so Confluence renders
            # the file-card chrome. Image extensions get image-card; other
            # extensions get file-card — decided via lib.mime.
            m_link = _re.match(
                r"^\[([^\]]+)\]\(([^)]+)\)(<!--\s*media[^>]*-->)?\s*$",
                stripped,
            )
            if m_link:
                label, ref = m_link.group(1), m_link.group(2)
                # Decode the URL slot to test against `images/` prefix
                try:
                    from lib.markdown_transform import md_link_dest_decode  # noqa: WPS433
                    decoded = md_link_dest_decode(ref)
                except Exception:  # noqa: BLE001
                    decoded = ref
                if decoded.startswith("images/") or decoded.startswith("./images/"):
                    from lib.mime import is_image_extension  # noqa: WPS433
                    media = _emit_media_node(label, ref)
                    if is_image_extension(decoded):
                        # image extension — wrap as image card
                        nodes.append({
                            "type": "mediaSingle",
                            "attrs": {"layout": "center"},
                            "content": [media],
                        })
                    else:
                        # file extension — mediaSingle with file-card
                        # rendering. ADF supports mediaSingle wrapping a
                        # type=file media node; Confluence renders it as
                        # the standard file-card chrome.
                        nodes.append({
                            "type": "mediaSingle",
                            "attrs": {"layout": "center"},
                            "content": [media],
                        })
                    i += 1
                    continue

            # Default paragraph (greedy single-line). For multi-line paragraph
            # support without complex parsing, accumulate consecutive non-blank
            # non-special lines.
            buf = [stripped]
            j = i + 1
            while j < len(lines):
                ln2 = lines[j]
                s2 = ln2.strip()
                if not s2 or ln2.startswith(">") or ln2.startswith("|") or _re.match(r"^(#{1,6}\s|\s*[-*]\s|\s*\d+\.\s|---$|\*\*\*$|___$|!\[)", s2) or _re.match(r"<!--\s*confluence-side:", s2):
                    break
                buf.append(s2)
                j += 1
            nodes.append(_para(" ".join(buf)))
            i = j

        return nodes

    return {"type": "doc", "version": 1, "content": _walk(md.splitlines())}


def cmd_adf_body(args: argparse.Namespace) -> int:
    source_path = Path(args.source)
    fm = read_frontmatter(source_path)
    page_index = _load_page_index(args.page_index)
    transformed, _ = transform_markdown(
        fm.body,
        source_doc_path=str(source_path),
        page_index=page_index,
        options=TransformOptions(
            miss_policy=args.miss_policy,
            strip_internal=getattr(args, "strip_internal", False),
        ),
    )
    images_collector: list[dict] = []
    adf = _md_to_adf(transformed, images_collector=images_collector)
    sidecar_path = getattr(args, "emit_images_sidecar", "") or ""
    if sidecar_path:
        Path(sidecar_path).write_text(
            json.dumps(images_collector, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        print(
            f"images sidecar: {len(images_collector)} placeholder(s) "
            f"written to {sidecar_path}",
            file=sys.stderr,
        )
    sys.stdout.write(json.dumps(adf, ensure_ascii=False))
    return 0


def _patch_adf_placeholders(adf: Any, id_map: dict[str, str]) -> Any:
    """Walk an ADF tree and replace any media node whose `id` matches a
    PLACEHOLDER:* string in `id_map` with the real attachment id.

    Pure transformation — does not modify the input. Returns a new tree.
    Unmapped placeholders are left alone (the caller surfaces them).
    """
    if isinstance(adf, dict):
        out: dict = {}
        for k, v in adf.items():
            if k == "attrs" and isinstance(v, dict) and "id" in v:
                attrs = dict(v)
                placeholder = attrs.get("id")
                if isinstance(placeholder, str) and placeholder in id_map:
                    attrs["id"] = id_map[placeholder]
                    attrs["type"] = "file"  # uploaded → file collection
                out[k] = attrs
            else:
                out[k] = _patch_adf_placeholders(v, id_map)
        return out
    if isinstance(adf, list):
        return [_patch_adf_placeholders(x, id_map) for x in adf]
    return adf


def cmd_patch_adf(args: argparse.Namespace) -> int:
    raw = sys.stdin.read()
    if not raw.strip():
        print("publish_helper patch-adf: no ADF on stdin", file=sys.stderr)
        return 64
    adf = json.loads(raw)
    id_map = json.loads(Path(args.map).read_text(encoding="utf-8"))
    if not isinstance(id_map, dict):
        print("publish_helper patch-adf: --map must be a JSON object", file=sys.stderr)
        return 65
    patched = _patch_adf_placeholders(adf, id_map)
    sys.stdout.write(json.dumps(patched, ensure_ascii=False))
    return 0


def cmd_upload_images(args: argparse.Namespace) -> int:
    """Upload every binary listed in `--sidecar` to `--page-id`, emit
    the {placeholder: media_id} map on stdout. Failures degrade
    gracefully — skipped entries simply don't appear in the map, and
    the patch step leaves their placeholders intact.
    """
    sidecar = json.loads(Path(args.sidecar).read_text(encoding="utf-8"))
    if not isinstance(sidecar, list):
        print("upload-images: sidecar must be a JSON list", file=sys.stderr)
        return 65
    try:
        from lib.attachments import (  # type: ignore
            extract_confluence_cookies,
            upload_attachment,
        )
    except ImportError as exc:
        print(f"upload-images: attachments lib missing: {exc}", file=sys.stderr)
        return 70
    try:
        cookies = extract_confluence_cookies(args.base_url)
    except Exception as exc:  # noqa: BLE001
        print(f"upload-images: cookie bridge failed: {exc}", file=sys.stderr)
        return 71

    source_dir = Path(args.source_dir)
    id_map: dict[str, str] = {}
    errors: list[str] = []
    for entry in sidecar:
        if not isinstance(entry, dict):
            continue
        placeholder = entry.get("placeholder") or ""
        relpath = entry.get("source_relpath") or ""
        if not placeholder or not relpath:
            continue
        # source-dir + relpath; relpath looks like 'images/<file>'
        source = source_dir / relpath
        if not source.is_file():
            errors.append(f"{relpath}: not found at {source}")
            continue
        try:
            rec = upload_attachment(
                args.base_url, args.page_id, source, cookies,
                comment="image roundtrip",
            )
            real_id = (
                rec.get("extensions", {}).get("fileId")
                or rec.get("id")
                or ""
            )
            if real_id:
                id_map[placeholder] = str(real_id)
            else:
                errors.append(f"{relpath}: upload returned no id")
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{relpath}: {exc}")
    if errors:
        for err in errors[:20]:
            print(f"upload-images warn: {err}", file=sys.stderr)
    sys.stdout.write(json.dumps(id_map, indent=2))
    return 0


def cmd_html_body(args: argparse.Namespace) -> int:
    source_path = Path(args.source)
    fm = read_frontmatter(source_path)
    page_index = _load_page_index(args.page_index)
    transformed, _ = transform_markdown(
        fm.body,
        source_doc_path=str(source_path),
        page_index=page_index,
        options=TransformOptions(
            miss_policy=args.miss_policy,
            strip_internal=getattr(args, "strip_internal", False),
        ),
    )
    sys.stdout.write(_md_to_storage_html(transformed))
    return 0


def cmd_splice(args: argparse.Namespace) -> int:
    raw = sys.stdin.read()
    if not raw.strip():
        print("publish_helper splice: no ADF on stdin", file=sys.stderr)
        return 64
    adf = _adf_from_mcp_response(json.loads(raw))
    zones_raw = json.loads(Path(args.zones).read_text(encoding="utf-8"))
    if not isinstance(zones_raw, list):
        print("publish_helper splice: --zones JSON must be a list of zone dicts", file=sys.stderr)
        return 65
    # Reconstruct the {name: Zone} map the splice expects
    from lib.zones import Zone

    zones = {
        str(z.get("name") or ""): Zone(
            name=str(z.get("name") or ""),
            title=str(z.get("title") or ""),
            content=z.get("content") or [],
        )
        for z in zones_raw
        if isinstance(z, dict)
    }
    out_adf = splice_zones_back(adf, zones)
    sys.stdout.write(json.dumps(out_adf, indent=2) + "\n")
    return 0


def cmd_commit(args: argparse.Namespace) -> int:
    source_path = Path(args.source)
    fm = read_frontmatter(source_path)
    body = fm.body
    update_frontmatter(
        source_path,
        state=args.state,
        confluence={
            "page_id": str(args.page_id),
            "last_published_version": int(args.version),
            "last_published_at": args.published_at or _today_utc(),
        },
    )
    snap_path = write_snapshot(
        page_id=str(args.page_id),
        version=int(args.version),
        markdown=body,
        cache_root=args.cache_root,
    )
    print(
        f"published: page_id={args.page_id} version={args.version} "
        f"snapshot={snap_path}"
    )
    return 0


def cmd_write_confluence_side(args: argparse.Namespace) -> int:
    source_path = Path(args.source)
    side_path = source_path.with_suffix(source_path.suffix + ".confluence-side.md")
    raw = json.loads(Path(args.current_adf).read_text(encoding="utf-8"))
    adf = _adf_from_mcp_response(raw)
    md = normalize_for_diff(adf)
    side_path.write_text(md, encoding="utf-8")
    print(f"wrote: {side_path}")
    return 0


# ---- Entry ----


def _apply_config_defaults(args: argparse.Namespace) -> None:
    """Fill --base-url from project.yml `change_control.base_url` when blank.

    Only `upload-images` uses --base-url; for other subcommands this is a
    no-op (the attribute may not exist).
    """
    try:
        from lib.config import read_change_control_config  # noqa: WPS433
    except ImportError:
        return
    try:
        cfg = read_change_control_config()
    except Exception:  # noqa: BLE001
        return
    if hasattr(args, "base_url") and not getattr(args, "base_url", "") and cfg.base_url:
        args.base_url = cfg.base_url


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    _apply_config_defaults(args)
    if args.cmd == "upload-images" and not getattr(args, "base_url", ""):
        parser.error(
            "upload-images: --base-url required (and not set in project.yml "
            "change_control.base_url)."
        )
    if args.cmd == "precheck":
        return cmd_precheck(args)
    if args.cmd == "adf-body":
        return cmd_adf_body(args)
    if args.cmd == "html-body":
        return cmd_html_body(args)
    if args.cmd == "body":
        return cmd_body(args)
    if args.cmd == "splice":
        return cmd_splice(args)
    if args.cmd == "commit":
        return cmd_commit(args)
    if args.cmd == "write-confluence-side":
        return cmd_write_confluence_side(args)
    if args.cmd == "patch-adf":
        return cmd_patch_adf(args)
    if args.cmd == "upload-images":
        return cmd_upload_images(args)
    parser.error(f"unknown command: {args.cmd}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
