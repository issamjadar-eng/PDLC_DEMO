"""Task-doc sentinel block for the formal-review (Confluence) tier.

Parallel to `lib.internal_review` but with Confluence-specific fields
(page id, page URL, baseline version, inline marker refs) and distinct
sentinel markers so both tiers can coexist on the same task doc.

Block format:

    <!-- change-control:formal-review begin doc=<repo-path> -->
    ## Formal Review — `<repo-path>`

    | Field | Value |
    |---|---|
    | Confluence page | https://example.atlassian.net/wiki/spaces/.../pages/<id> |
    | Page id | <id> |
    | Baseline version | 5 |
    | Plugin | document_control |
    | First pushed | 2026-04-28T11:30:00Z |
    | Last sync | 2026-04-28T14:15:00Z |
    | Open | 3 inline · 1 footer · 0 macros |
    | Already addressed | 0 |

    ### Open

    - [ ] **#i-mref-abc123** Reviewer · "anchor text"
          > Comment body.

    ### Already Addressed (will reply on next `review-formal-update`)

    (none yet)

    ### Recently Synced

    (none yet)

    ### Confluence-side macros (informational; not drift)

    (none)
    <!-- change-control:formal-review end -->

`#i-` prefix = inline comment (the rest is the inlineMarkerRef);
`#f-` prefix = footer comment (the rest is the comment id);
`#m-` prefix = Confluence-side macro (informational).

This module is a self-contained parser/renderer. Helpers live in
`actions/review_formal_helper.py`. Action procedures (the agent
side) live in `actions/review-formal-{start,status,update,abort}.md`.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone


SENTINEL_BEGIN_RE = re.compile(
    r"<!--\s*change-control:formal-review\s+begin\s+doc=(?P<doc>[^\s>]+)\s*-->"
)
SENTINEL_END = "<!-- change-control:formal-review end -->"


@dataclass
class FormalReviewItem:
    """One open / addressed / synced item in the formal-review block.

    Item kinds:
      - `inline`   — inline comment, keyed by `inlineMarkerRef`
      - `footer`   — footer comment, keyed by comment id
      - `macro`    — Confluence-side extension macro (informational)
    """

    kind: str  # 'inline' | 'footer' | 'macro'
    id: str    # mref / commentId / extensionKey
    author: str = ""
    anchor: str = ""  # inlineOriginalSelection / footer-comment-link
    text: str = ""    # body content
    status: str = "open"  # 'open' | 'addressed' | 'deferred' | 'wont-fix'
    resolution_note: str = ""

    @property
    def kind_short(self) -> str:
        return {"inline": "i", "footer": "f", "macro": "m"}.get(self.kind, "?")


@dataclass
class FormalReviewSection:
    doc_path: str
    page_id: str = ""
    page_url: str = ""
    baseline_version: int = 0
    plugin_name: str = ""
    first_pushed: str = ""
    last_sync: str = ""
    open_items: list[FormalReviewItem] = field(default_factory=list)
    already_addressed: list[FormalReviewItem] = field(default_factory=list)
    recently_synced: list[FormalReviewItem] = field(default_factory=list)
    macros: list[FormalReviewItem] = field(default_factory=list)

    @classmethod
    def new(
        cls,
        doc_path: str,
        page_id: str,
        page_url: str,
        baseline_version: int,
        plugin_name: str = "",
    ) -> "FormalReviewSection":
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        return cls(
            doc_path=doc_path,
            page_id=page_id,
            page_url=page_url,
            baseline_version=int(baseline_version),
            plugin_name=plugin_name,
            first_pushed=now,
            last_sync=now,
        )


# ----------------------------------------------------------------------------
# Render
# ----------------------------------------------------------------------------


def _item_line(item: FormalReviewItem) -> str:
    short = item.kind_short
    label = f"**#{short}-{item.id}**"
    parts = [p for p in (item.author, item.anchor) if p]
    head = " · ".join(parts)
    if item.status == "open":
        line = f"- [ ] {label}"
        if head:
            line += f" {head}"
        if item.text:
            line += f"\n      > {item.text}"
        return line
    line = f"- [x] {label}"
    if head:
        line += f" {head}"
    if item.resolution_note:
        line += f" — {item.status}: {item.resolution_note}"
    elif item.status != "open":
        line += f" — {item.status}"
    return line


def _macro_line(item: FormalReviewItem) -> str:
    short = item.kind_short
    label = f"**#{short}-{item.id}**"
    head = " · ".join(p for p in (item.author, item.anchor) if p)
    line = f"- {label}"
    if head:
        line += f" {head}"
    if item.text:
        line += f" — {item.text}"
    return line


def _section(title: str, items: list[FormalReviewItem], empty_text: str, line_fn=_item_line) -> str:
    body = "\n".join(line_fn(it) for it in items) if items else f"({empty_text})"
    return f"### {title}\n\n{body}\n"


def render_section(section: FormalReviewSection) -> str:
    open_inline = sum(1 for it in section.open_items if it.kind == "inline")
    open_footer = sum(1 for it in section.open_items if it.kind == "footer")
    macro_count = len(section.macros)
    fields = [
        ("Confluence page", section.page_url or "-"),
        ("Page id", section.page_id or "-"),
        ("Baseline version", str(section.baseline_version) if section.baseline_version else "-"),
        ("Plugin", section.plugin_name or "-"),
        ("First pushed", section.first_pushed or "-"),
        ("Last sync", section.last_sync or "-"),
        ("Open", f"{open_inline} inline · {open_footer} footer · {macro_count} macros"),
        ("Already addressed", str(len(section.already_addressed))),
    ]
    table = "| Field | Value |\n|---|---|\n" + "\n".join(
        f"| {k} | {v} |" for k, v in fields
    )
    parts = [
        f"<!-- change-control:formal-review begin doc={section.doc_path} -->",
        f"## Formal Review — `{section.doc_path}`",
        "",
        table,
        "",
        _section("Open", section.open_items, "none yet"),
        _section(
            "Already Addressed (will reply on next `review-formal-update`)",
            section.already_addressed,
            "none yet",
        ),
        _section("Recently Synced", section.recently_synced, "none yet"),
        _section(
            "Confluence-side macros (informational; not drift)",
            section.macros,
            "none",
            line_fn=_macro_line,
        ),
        SENTINEL_END,
    ]
    return "\n".join(parts).rstrip() + "\n"


# ----------------------------------------------------------------------------
# Parse
# ----------------------------------------------------------------------------


_TABLE_ROW_RE = re.compile(r"^\|\s*([^|]+?)\s*\|\s*(.+?)\s*\|$")
_OPEN_RE = re.compile(r"^- \[ \] \*\*#(?P<short>[ifm])-(?P<id>[^*]+?)\*\*(?:\s+(?P<rest>.*))?$")
_DONE_RE = re.compile(r"^- \[x\] \*\*#(?P<short>[ifm])-(?P<id>[^*]+?)\*\*(?:\s+(?P<rest>.*))?$")
_MACRO_RE = re.compile(r"^- \*\*#m-(?P<id>[^*]+?)\*\*(?:\s+(?P<rest>.*))?$")


_KIND_FROM_SHORT = {"i": "inline", "f": "footer", "m": "macro"}


def _parse_item(line: str, next_line: str | None, status: str) -> FormalReviewItem | None:
    m = _OPEN_RE.match(line) if status == "open" else _DONE_RE.match(line)
    if m is None:
        return None
    short = m.group("short")
    kind = _KIND_FROM_SHORT.get(short, short)
    item = FormalReviewItem(kind=kind, id=m.group("id").strip(), status=status)
    rest = (m.group("rest") or "").strip()
    if status != "open" and rest and " — " in rest:
        head, _, tail = rest.partition(" — ")
        if ":" in tail:
            new_status, _, note = tail.partition(":")
            item.status = new_status.strip()
            item.resolution_note = note.strip()
        else:
            item.status = tail.strip()
        rest = head
    bits = [b.strip() for b in rest.split("·")]
    bits = [b for b in bits if b]
    if bits:
        item.author = bits[0]
    if len(bits) > 1:
        item.anchor = " · ".join(bits[1:])
    if next_line and next_line.lstrip().startswith("> "):
        item.text = next_line.lstrip()[2:].rstrip()
    return item


def _parse_macro(line: str) -> FormalReviewItem | None:
    m = _MACRO_RE.match(line)
    if m is None:
        return None
    item = FormalReviewItem(kind="macro", id=m.group("id").strip(), status="open")
    rest = (m.group("rest") or "").strip()
    if " — " in rest:
        head, _, body = rest.partition(" — ")
        item.text = body.strip()
        rest = head
    bits = [b.strip() for b in rest.split("·") if b.strip()]
    if bits:
        item.author = bits[0]
    if len(bits) > 1:
        item.anchor = " · ".join(bits[1:])
    return item


def parse_section(block_text: str) -> FormalReviewSection:
    """Parse a rendered block back into a FormalReviewSection.

    Tolerant — unknown rows are skipped. Caller should treat the
    result as "what the user has on disk now," not as a strict schema.
    """
    section = FormalReviewSection(doc_path="")
    m = SENTINEL_BEGIN_RE.search(block_text)
    if m:
        section.doc_path = m.group("doc")

    lines = block_text.splitlines()
    cur_section = ""
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if stripped.startswith("### "):
            heading = stripped[4:].strip()
            if heading.startswith("Open"):
                cur_section = "open"
            elif heading.startswith("Already Addressed"):
                cur_section = "addressed"
            elif heading.startswith("Recently Synced"):
                cur_section = "synced"
            elif heading.startswith("Confluence-side macros"):
                cur_section = "macros"
            else:
                cur_section = ""
            i += 1
            continue
        # Table rows
        tr = _TABLE_ROW_RE.match(stripped)
        if tr:
            key, value = tr.group(1).strip(), tr.group(2).strip()
            if key == "Page id" and value not in ("-", ""):
                section.page_id = value
            elif key == "Confluence page" and value not in ("-", ""):
                section.page_url = value
            elif key == "Baseline version" and value not in ("-", ""):
                try:
                    section.baseline_version = int(value)
                except ValueError:
                    pass
            elif key == "Plugin" and value not in ("-", ""):
                section.plugin_name = value
            elif key == "First pushed" and value not in ("-", ""):
                section.first_pushed = value
            elif key == "Last sync" and value not in ("-", ""):
                section.last_sync = value
            i += 1
            continue
        # Items
        next_line = lines[i + 1] if i + 1 < len(lines) else None
        if cur_section == "macros":
            mi = _parse_macro(stripped)
            if mi is not None:
                section.macros.append(mi)
        elif cur_section == "open":
            it = _parse_item(stripped, next_line, "open")
            if it is not None:
                section.open_items.append(it)
                if next_line and next_line.lstrip().startswith("> "):
                    i += 1
        elif cur_section in ("addressed", "synced"):
            it = _parse_item(stripped, next_line, "addressed")
            if it is not None:
                if cur_section == "addressed":
                    section.already_addressed.append(it)
                else:
                    section.recently_synced.append(it)
        i += 1
    return section


# ----------------------------------------------------------------------------
# Upsert / find / remove
# ----------------------------------------------------------------------------


def find_block(task_doc_text: str, doc_path: str) -> tuple[int, int] | None:
    lines = task_doc_text.splitlines()
    begin = -1
    for idx, line in enumerate(lines):
        m = SENTINEL_BEGIN_RE.search(line)
        if m and m.group("doc") == doc_path:
            begin = idx
            break
    if begin == -1:
        return None
    end = -1
    for idx in range(begin + 1, len(lines)):
        if SENTINEL_END in lines[idx]:
            end = idx
            break
    if end == -1:
        return None
    return begin, end


def upsert_block(task_doc_text: str, section: FormalReviewSection) -> str:
    rendered = render_section(section).rstrip("\n")
    rng = find_block(task_doc_text, section.doc_path)
    lines = task_doc_text.splitlines()
    if rng is None:
        if task_doc_text and not task_doc_text.endswith("\n"):
            task_doc_text += "\n"
        return task_doc_text + "\n" + rendered + "\n"
    b, e = rng
    new_lines = lines[:b] + rendered.splitlines() + lines[e + 1:]
    return "\n".join(new_lines) + ("\n" if task_doc_text.endswith("\n") else "")


def remove_block(task_doc_text: str, doc_path: str) -> str:
    rng = find_block(task_doc_text, doc_path)
    if rng is None:
        return task_doc_text
    lines = task_doc_text.splitlines()
    b, e = rng
    new_lines = lines[:b] + lines[e + 1:]
    out = "\n".join(new_lines)
    return out + ("\n" if task_doc_text.endswith("\n") else "")
