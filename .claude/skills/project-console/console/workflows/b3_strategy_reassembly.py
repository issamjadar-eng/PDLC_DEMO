"""B3 — Strategy Re-Assembly: scanner + parser for docs/project/strategies/*.

Parses each assembled strategy doc to surface:
  • front-matter-ish metadata (domain, assembled date, sources, status)
  • proposed-change callouts (> **Proposed change** blockquotes from task 100's
    conflict flow — resolution options are accept / withdraw / leave)
  • assembly history entries (### YYYY-MM-DD — assembled by ...)

All mutating actions (accept / withdraw / leave / re-assemble) are dry-run
in this prototype per the Placeholder Convention.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

_STRATEGIES_DIR = "docs/project/strategies"

# Matches a blockquote-indented "> **Proposed change**" callout header.
# Example: > **Proposed change** — task 056 ("Module Architecture", Ben, 2026-04-15)
_PROPOSAL_HEADER_RE = re.compile(
    r"^>\s*\*\*Proposed change\*\*\s*(?:—|-)?\s*(.*)$",
    re.IGNORECASE,
)

# Matches the closing resolution hint: > *Resolution: re-run /strategy assemble ...*
_PROPOSAL_RESOLUTION_RE = re.compile(r"^>\s*\*Resolution:", re.IGNORECASE)

# Matches a section heading (level 2). We use this to locate which section a
# proposal sits under.
_H2_RE = re.compile(r"^##\s+(.+?)\s*$")

# Matches an assembly history entry header (level 3 under ## Assembly History).
_HISTORY_ENTRY_RE = re.compile(r"^###\s+(\d{4}-\d{2}-\d{2})\s*(?:—|-)\s*(.+?)\s*$")

# Parse the header tail into structured fields. The convention from the
# assembler is: `<task_folder>/NNN ("Heading", Author, YYYY-MM-DD)` (v14+),
# with legacy `task NNN (...)` also accepted for older strategy docs.
_PROPOSAL_TAIL_RE = re.compile(
    r'(?:task\s+|(?=\w+/\d))(?P<task>[\w./-]+?)\s*\(\s*"(?P<heading>[^"]+)"\s*,\s*(?P<author>[^,]+?)\s*,\s*(?P<date>\d{4}-\d{2}-\d{2})\s*\)',
)


@dataclass(frozen=True)
class StrategyDoc:
    slug: str          # e.g. "regulatory" (from filename minus "-strategy")
    filename: str      # e.g. "regulatory-strategy.md"
    virtual_path: str  # repo-relative posix
    title: str
    domain: str        # from <!-- Domain: X -->
    status: str        # "awaiting-content" | "assembled" | "unknown"
    assembled_date: str  # from <!-- Assembled: DATE by CMD -->
    sources: list[str] = field(default_factory=list)  # task IDs
    proposal_count: int = 0
    history_count: int = 0
    size_bytes: int = 0


@dataclass(frozen=True)
class Proposal:
    # Numeric index inside the doc (0-based, by appearance order) — used as ID
    # for dry-run actions.
    idx: int
    task_id: str           # e.g. "056" or "ben/056"
    heading: str           # the section heading referenced
    author: str
    date: str              # YYYY-MM-DD
    section: str           # level-2 section this proposal sits under
    raw: str               # verbatim block text (including ">" prefixes)
    start_line: int        # 1-based line number in source
    end_line: int


@dataclass(frozen=True)
class HistoryEntry:
    date: str              # YYYY-MM-DD
    label: str             # e.g. "assembled by /strategy assemble regulatory"
    body: str              # following lines until next ### or end


# ── Discovery ────────────────────────────────────────────────────────────

def scan(repo_root: Path) -> list[StrategyDoc]:
    base = repo_root / _STRATEGIES_DIR
    if not base.is_dir():
        return []
    out: list[StrategyDoc] = []
    for p in sorted(base.glob("*-strategy.md")):
        meta = _parse_header(p)
        text = p.read_text(encoding="utf-8", errors="ignore")
        proposals = _parse_proposals(text)
        history = _parse_history(text)
        slug = p.name.removesuffix("-strategy.md")
        out.append(
            StrategyDoc(
                slug=slug,
                filename=p.name,
                virtual_path=p.relative_to(repo_root).as_posix(),
                title=meta.get("title") or slug.replace("-", " ").title() + " Strategy",
                domain=meta.get("domain") or slug,
                status=meta.get("status") or ("assembled" if meta.get("assembled_date") else "unknown"),
                assembled_date=meta.get("assembled_date") or "",
                sources=meta.get("sources") or [],
                proposal_count=len(proposals),
                history_count=len(history),
                size_bytes=p.stat().st_size,
            )
        )
    return out


def get_by_slug(repo_root: Path, slug: str) -> StrategyDoc | None:
    return next((d for d in scan(repo_root) if d.slug == slug), None)


# ── Parsing helpers ──────────────────────────────────────────────────────

def _parse_header(p: Path) -> dict:
    """Read the first ~40 lines to pull out frontmatter-ish HTML comments +
    the H1 title. Stops before the first H2."""
    out: dict = {}
    sources: list[str] = []
    try:
        with p.open("r", encoding="utf-8", errors="ignore") as fh:
            for i, raw in enumerate(fh):
                line = raw.rstrip()
                if i == 0 and line.startswith("# "):
                    out["title"] = line[2:].strip()
                if line.startswith("## "):
                    break
                if m := re.match(r"<!--\s*Status:\s*(.+?)\s*-->", line):
                    out["status"] = m.group(1).strip()
                if m := re.match(r"<!--\s*Domain:\s*(.+?)\s*-->", line):
                    out["domain"] = m.group(1).strip()
                if m := re.match(r"<!--\s*Assembled:\s*([0-9-]+)\s*(?:by\s+(.+?))?\s*-->", line):
                    out["assembled_date"] = m.group(1)
                if m := re.match(r"<!--\s*Sources:\s*(.+?)\s*-->", line):
                    parts = [x.strip() for x in m.group(1).split(",") if x.strip()]
                    # Normalize: "task 056" → "056"
                    for x in parts:
                        xs = x.replace("task", "").strip()
                        if xs:
                            sources.append(xs)
                if i > 40:
                    break
    except OSError:
        pass
    if sources:
        out["sources"] = sources
    return out


def _parse_proposals(text: str) -> list[Proposal]:
    """Find each contiguous blockquote that starts with `> **Proposed change**`.
    Track the enclosing level-2 section heading for context."""
    lines = text.splitlines()
    proposals: list[Proposal] = []
    current_section = "(before first section)"
    i = 0
    n = len(lines)
    idx = 0
    while i < n:
        line = lines[i]
        if (m := _H2_RE.match(line)):
            current_section = m.group(1).strip()
            i += 1
            continue
        if _PROPOSAL_HEADER_RE.match(line):
            # Collect the contiguous blockquote.
            start = i
            header_tail = _PROPOSAL_HEADER_RE.match(line).group(1)
            block_lines = [line]
            j = i + 1
            while j < n and (lines[j].startswith(">") or lines[j].strip() == ""):
                # Stop if we just passed a resolution line followed by a blank
                # AND the next non-blank isn't a ">" — i.e. the blockquote ended.
                block_lines.append(lines[j])
                if lines[j].strip() == "" and (j + 1 >= n or not lines[j + 1].startswith(">")):
                    break
                j += 1
            end = j
            raw = "\n".join(block_lines).rstrip()
            tail_m = _PROPOSAL_TAIL_RE.search(header_tail + " " + raw)
            task_id = tail_m.group("task") if tail_m else ""
            heading = tail_m.group("heading") if tail_m else ""
            author = tail_m.group("author") if tail_m else ""
            date = tail_m.group("date") if tail_m else ""
            proposals.append(
                Proposal(
                    idx=idx,
                    task_id=task_id,
                    heading=heading,
                    author=author,
                    date=date,
                    section=current_section,
                    raw=raw,
                    start_line=start + 1,
                    end_line=end + 1,
                )
            )
            idx += 1
            i = end
            continue
        i += 1
    return proposals


def _parse_history(text: str) -> list[HistoryEntry]:
    """Extract entries under `## Assembly History` — each `### YYYY-MM-DD — label`
    with its following body (until the next ### or next ##)."""
    lines = text.splitlines()
    n = len(lines)
    # Find the Assembly History section.
    start = None
    for i, line in enumerate(lines):
        if re.match(r"^##\s+(?:Assembly\s+)?History\s*$", line, re.IGNORECASE):
            start = i + 1
            break
    if start is None:
        return []
    entries: list[HistoryEntry] = []
    i = start
    while i < n:
        line = lines[i]
        if line.startswith("## ") and not line.startswith("### "):
            break
        m = _HISTORY_ENTRY_RE.match(line)
        if m:
            date, label = m.group(1), m.group(2).strip()
            body_lines: list[str] = []
            j = i + 1
            while j < n and not lines[j].startswith("### ") and not (
                lines[j].startswith("## ") and not lines[j].startswith("### ")
            ):
                body_lines.append(lines[j])
                j += 1
            entries.append(HistoryEntry(date=date, label=label, body="\n".join(body_lines).strip()))
            i = j
            continue
        i += 1
    return entries


# ── Type classification (for UI badges) ──────────────────────────────────

_WITHDRAWN_LINE_RE = re.compile(r"^<!--\s*STRATEGY\s+WITHDRAWN:", re.IGNORECASE)
_PROPOSED_LINE_RE = re.compile(r"^<!--\s*STRATEGY\s+PROPOSED:", re.IGNORECASE)
_REPLACE_HINT_RE = re.compile(r"\b(supersed|replac|deprecat|retire)", re.IGNORECASE)

PROPOSAL_KINDS = {
    "new": {"label": "New decision", "icon": "🆕", "color": "#2e7d32"},
    "modify": {"label": "Modify existing", "icon": "✏️", "color": "#f9a825"},
    "replace": {"label": "Replace existing", "icon": "🔄", "color": "#6a1b9a"},
    "withdraw": {"label": "Withdraw", "icon": "🗑️", "color": "#c62828"},
}


# ── Decision-block parser (v15+ format) ──────────────────────────────────

_DECISION_START_LINE_RE = re.compile(
    r"^<!--\s+DECISION:start\s+(?P<meta>.+?)\s+-->\s*$"
)
_DECISION_END_LINE_RE = re.compile(r"^<!--\s+DECISION:end(?:\s+id=\S+)?\s*-->\s*$")


@dataclass(frozen=True)
class Decision:
    """A first-class strategy decision parsed from a v15 strategy doc.

    `id` is stable for the life of the decision; `status` carries the
    lifecycle state (active / proposed-change / superseded / withdrawn).
    `body` is the raw markdown between the start sentinel and the end
    sentinel, including the H3 heading line. `metadata` holds any
    additional fields parsed from the start sentinel."""
    id: str
    status: str
    source: str
    created: str
    last_edited: str
    supersedes: str
    section_label: str
    heading: str
    body: str
    start_line: int
    end_line: int
    metadata: dict


def _parse_decision_metadata(s: str) -> dict:
    """Parse `id=X status=Y source=Z` into a dict. Tolerates extra spaces."""
    out: dict = {}
    for token in s.split():
        if "=" in token:
            k, v = token.split("=", 1)
            out[k.strip()] = v.strip()
    return out


def parse_decisions(text: str) -> list[Decision]:
    """Walk the strategy doc and emit one Decision per `DECISION:start`/
    `DECISION:end` pair. Returns an empty list if the doc hasn't been
    migrated to the v15 format yet (which is fine — callers fall back to
    the legacy heading-based rendering)."""
    lines = text.splitlines()
    out: list[Decision] = []
    current_section = ""
    n = len(lines)
    i = 0
    while i < n:
        line = lines[i]
        if line.startswith("## ") and not line.startswith("### "):
            current_section = line[3:].strip()
            i += 1
            continue
        m = _DECISION_START_LINE_RE.match(line)
        if not m:
            i += 1
            continue
        meta = _parse_decision_metadata(m.group("meta"))
        start_line = i + 1   # 1-based
        body_lines: list[str] = []
        heading = ""
        i += 1
        # Capture optional blank lines, then the H3 heading.
        while i < n and lines[i].strip() == "":
            body_lines.append(lines[i])
            i += 1
        if i < n and lines[i].startswith("### "):
            heading = lines[i][4:].strip()
            body_lines.append(lines[i])
            i += 1
        # Collect body until end sentinel.
        while i < n and not _DECISION_END_LINE_RE.match(lines[i]):
            body_lines.append(lines[i])
            i += 1
        end_line = i + 1     # 1-based, points at the end sentinel
        if i < n:
            i += 1            # consume the end sentinel
        out.append(
            Decision(
                id=meta.get("id", ""),
                status=meta.get("status", "active"),
                source=meta.get("source", ""),
                created=meta.get("created", ""),
                last_edited=meta.get("last-edited", ""),
                supersedes=meta.get("supersedes", ""),
                section_label=current_section,
                heading=heading,
                body="\n".join(body_lines).rstrip(),
                start_line=start_line,
                end_line=end_line,
                metadata=meta,
            )
        )
    return out


_NUMBER_PREFIX_RE = re.compile(r"^\d+\.\d+\s+")


def _h3_text_no_prefix(line: str) -> str:
    """Return the H3's heading text minus any `<sec>.<idx> ` numeric prefix."""
    if not line.startswith("### "):
        return line
    return _NUMBER_PREFIX_RE.sub("", line[4:].strip())


def existing_section_content(text: str, proposal: Proposal) -> str:
    """Return the markdown body of `proposal.section` from the current
    strategy doc, with the proposal's own callout block + paired
    STRATEGY-PROPOSED marker removed. Empty string if the section doesn't
    exist as an H2/H3 heading in the doc.

    This is what the UI shows as "Currently in this section" alongside
    the proposed change — answers the user's question "what does this
    proposal actually change?"."""
    if not proposal.section:
        return ""
    lines = text.splitlines()
    section_start = None
    section_level = None
    target = proposal.section.strip()
    for i, line in enumerate(lines):
        if line.startswith("## ") and line[3:].strip() == target:
            section_start, section_level = i, 2
            break
        if line.startswith("### ") and (
            line[4:].strip() == target or _h3_text_no_prefix(line) == target
        ):
            section_start, section_level = i, 3
            break
    if section_start is None:
        return ""

    # End-of-section: next heading at same OR higher level.
    section_end = len(lines)
    for j in range(section_start + 1, len(lines)):
        ln = lines[j]
        if ln.startswith("## "):
            section_end = j
            break
        if section_level == 3 and ln.startswith("### "):
            section_end = j
            break

    # Lines to omit: the proposal callout block + adjacent blanks +
    # any STRATEGY PROPOSED marker that pairs with it.
    drop = set(range(proposal.start_line - 1, proposal.end_line))
    cursor = proposal.end_line
    while cursor < len(lines) and lines[cursor].strip() == "":
        drop.add(cursor)
        cursor += 1
    if cursor < len(lines) and re.match(
        r"^<!--\s*STRATEGY\s+PROPOSED:", lines[cursor], re.IGNORECASE
    ):
        drop.add(cursor)

    body: list[str] = []
    for k in range(section_start + 1, section_end):
        if k in drop:
            continue
        body.append(lines[k])
    return "\n".join(body).strip()


def classify_proposal(text: str, proposal: Proposal) -> str:
    """Return one of {'new','modify','replace','withdraw'} based on the
    HTML marker adjacent to the proposal callout in the strategy doc, plus
    a body-text heuristic to distinguish modify-vs-replace."""
    lines = text.splitlines()
    i = proposal.end_line  # `end_line` is 1-based exclusive (next line after callout)
    while i < len(lines) and lines[i].strip() == "":
        i += 1
    if i >= len(lines):
        return "new"
    if _WITHDRAWN_LINE_RE.match(lines[i]):
        return "withdraw"
    if _PROPOSED_LINE_RE.match(lines[i]):
        # Body-text heuristic to distinguish "modify" (additive, both kept)
        # from "replace" (newer supersedes older). The assembler doesn't
        # always emit a paired REVIEWED:superseded marker on the older
        # task's tag, so we lean on language cues in the callout body.
        if _REPLACE_HINT_RE.search(proposal.raw):
            return "replace"
        return "modify"
    return "new"


# ── Action planning (dry-run) ────────────────────────────────────────────

_VALID_ACTIONS = {"accept", "reject", "modify"}


@dataclass(frozen=True)
class ActionPlan:
    domain: str
    action: str              # per-proposal ("accept" | "reject" | "modify") or "re-assemble"
    proposal_idx: int | None
    commands: list[str]      # CLI invocations that would be issued
    file_edits: list[str]    # human-readable description of file changes
    backend_status: str = "placeholder"
    # Audit-trail fields (populated by the router from resolve_user.py +
    # active-task state file). Safe defaults so this dataclass stays usable
    # from unit tests without the console runtime.
    actor: str = ""           # e.g. "Ben Xavier"
    actor_email: str = ""
    active_task_ids: tuple[str, ...] = ()
    history_entry_preview: str = ""   # the line that would be appended to ## History
    can_execute_live: bool = False    # True when actor + active task are both present


def plan_proposal_action(
    doc: StrategyDoc,
    proposal: Proposal,
    action: str,
    new_body: str | None = None,
) -> ActionPlan:
    """Describe what `action` would do to `proposal`. No files touched.

    `new_body` is only meaningful for `action="modify"` — it carries the
    user-edited proposal content that would replace the original before
    acceptance.
    """
    if action not in _VALID_ACTIONS:
        raise ValueError(f"unknown action: {action}")
    commands: list[str] = []
    edits: list[str] = []
    if action == "accept":
        commands.append(f"/strategy assemble {doc.domain}  # (with action=accept on proposal #{proposal.idx})")
        edits.append(
            f"Replace source task {proposal.task_id}'s `<!-- STRATEGY CONTENT -->` marker with "
            f"`<!-- STRATEGY REVIEWED: superseded by task {proposal.task_id} -->` in the *older* task doc."
        )
        edits.append(
            f"Remove `<!-- STRATEGY PROPOSED -->` from task {proposal.task_id}."
        )
        edits.append(
            f"Promote the `> **Proposed change**` callout at {doc.virtual_path}:{proposal.start_line}–{proposal.end_line} "
            f"to authoritative section content (removes the blockquote prefix)."
        )
    elif action == "reject":
        commands.append(f"/strategy assemble {doc.domain}  # (with action=reject on proposal #{proposal.idx})")
        edits.append(
            f"Mark task {proposal.task_id}'s tag `<!-- STRATEGY WITHDRAWN: -->` so future assemblies exclude it."
        )
        edits.append(
            f"Remove the `> **Proposed change**` callout from {doc.virtual_path} (lines {proposal.start_line}–{proposal.end_line})."
        )
    elif action == "modify":
        preview = (new_body or "").strip()
        if not preview:
            edits.append("No replacement body supplied — no changes would be made.")
        else:
            snippet = preview if len(preview) <= 200 else preview[:200] + "…"
            commands.append(
                f"/strategy assemble {doc.domain}  # (with action=modify+accept on proposal #{proposal.idx})"
            )
            edits.append(
                f"Edit task {proposal.task_id}'s source body to match the modified text (see preview below)."
            )
            edits.append(
                f"Replace the `> **Proposed change**` callout at {doc.virtual_path}:{proposal.start_line}–{proposal.end_line} "
                f"with the modified content, then promote to authoritative section content."
            )
            edits.append(f"Modified body preview: {snippet}")
    return ActionPlan(
        domain=doc.domain,
        action=action,
        proposal_idx=proposal.idx,
        commands=commands,
        file_edits=edits,
    )


def plan_reassemble(doc: StrategyDoc) -> ActionPlan:
    cmds = [f"/strategy assemble {doc.domain}"]
    edits = [
        f"Scan all task docs for `<!-- STRATEGY CONTENT: {doc.domain}, ... -->` tags.",
        f"Re-render {doc.virtual_path} (preserving Assembly History).",
        "Prompt for conflict resolution on any blocks that collide with existing content.",
    ]
    return ActionPlan(
        domain=doc.domain,
        action="re-assemble",
        proposal_idx=None,
        commands=cmds,
        file_edits=edits,
    )


# ── Live execution (only Reject is live-capable in this pass) ─────────────

def active_task_ids(repo_root: Path) -> list[str]:
    """Read every `.state/active-tasks-*.txt` file and return a de-duplicated
    list of task IDs currently active across any session."""
    state_dir = repo_root / ".state"
    if not state_dir.is_dir():
        return []
    seen: list[str] = []
    for f in state_dir.glob("active-tasks-*.txt"):
        try:
            for line in f.read_text(encoding="utf-8", errors="ignore").splitlines():
                tid = line.strip()
                if tid and tid not in seen:
                    seen.append(tid)
        except OSError:
            continue
    return seen


def _today() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _hhmm() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).strftime("%H:%M")


def build_history_entry_preview(
    action: str,
    proposal: Proposal,
    actor: str,
    active_task_ids_: list[str],
) -> str:
    """Construct the single history line that would be appended for this
    action. Shown to the user before execution; also the literal string
    written on execute."""
    actor_str = actor or "unknown-actor"
    under = f"under task {active_task_ids_[0]}" if active_task_ids_ else "no-active-task"
    heading = proposal.heading or "(no heading)"
    return (
        f"- {_hhmm()} · **{action.title()}** · \"{heading}\" "
        f"({proposal.task_id or '?'}) · by {actor_str} · {under}"
    )


_PROPOSED_MARKER_RE = re.compile(
    r"<!--\s*STRATEGY\s+PROPOSED:\s*vs\s+(?P<older>[\w./-]+?)\s*"
    r'(?:,\s*section\s+"(?P<section>[^"]+)")?\s*-->',
    re.IGNORECASE,
)


def _find_proposed_marker(text: str, proposal_end_line: int) -> tuple[str, str] | None:
    """Look for the `<!-- STRATEGY PROPOSED: vs <older>, section "X" -->`
    marker on the first non-blank line after the callout. Returns
    (older_task_id, section_name) or None."""
    lines = text.splitlines()
    i = proposal_end_line
    while i < len(lines) and lines[i].strip() == "":
        i += 1
    if i >= len(lines):
        return None
    m = _PROPOSED_MARKER_RE.search(lines[i])
    if not m:
        return None
    return m.group("older"), (m.group("section") or "")


def _rewrite_source_task_marker(
    repo_root: Path,
    older_task_id: str,
    newer_task_id: str,
    domain: str,
    section: str,
) -> dict:
    """Open `tasks/<task_folder>/<NNN>-*.md` and mark the matching
    `<!-- STRATEGY CONTENT -->` tag as `<!-- STRATEGY REVIEWED: superseded
    by <newer> -->`. Returns a diagnostic dict describing what happened.

    Skips the rewrite (status=skipped, reason) when the task file can't be
    located or the tag covers multiple subsections (higher blast-radius
    decision — user should handle manually)."""
    task_path, resolved = _resolve_task_path(repo_root, older_task_id)
    if task_path is None:
        return {"status": "skipped", "reason": resolved}
    text = task_path.read_text(encoding="utf-8")
    lines = text.splitlines()

    # Locate STRATEGY CONTENT tag for this domain. If multiple, disambiguate
    # by picking the one whose following block contains a `### <section>`
    # heading that matches the target section.
    content_re = re.compile(
        rf"<!--\s*STRATEGY\s+CONTENT:\s*{re.escape(domain)}\b[^>]*-->",
        re.IGNORECASE,
    )
    tag_indices = [i for i, ln in enumerate(lines) if content_re.search(ln)]
    if not tag_indices:
        return {"status": "skipped", "reason": f"no STRATEGY CONTENT tag for domain {domain!r}"}

    # Determine each tag's block extent (from tag line to next `## ` or EOF).
    def block_bounds(start: int) -> tuple[int, int]:
        end = len(lines)
        for j in range(start + 1, len(lines)):
            if lines[j].startswith("## ") and not lines[j].startswith("### "):
                end = j
                break
        return start, end

    target_tag = None
    for tag_i in tag_indices:
        s, e = block_bounds(tag_i)
        # Collect level-3 headings in the block.
        sub_headings = [
            lines[k][4:].strip() for k in range(s, e) if lines[k].startswith("### ")
        ]
        if section and any(h == section for h in sub_headings):
            target_tag = tag_i
            if len(sub_headings) > 1:
                return {
                    "status": "skipped",
                    "reason": (
                        f"tag at {task_path.relative_to(repo_root)}:{tag_i+1} covers "
                        f"{len(sub_headings)} subsections — refusing to mark entire tag "
                        f"superseded. Split the tag or handle manually."
                    ),
                    "task_path": str(task_path.relative_to(repo_root)),
                }
            break
    if target_tag is None and len(tag_indices) == 1:
        # Single tag and no section disambiguation — best-effort match it.
        target_tag = tag_indices[0]

    if target_tag is None:
        return {
            "status": "skipped",
            "reason": f"could not disambiguate STRATEGY CONTENT tag for section {section!r}",
        }

    # Insert `<!-- STRATEGY REVIEWED: superseded by <newer> -->` on the line
    # immediately after the tag (replacing any existing STRATEGY PROPOSED /
    # REVIEWED marker on that line so markers don't stack).
    review_marker = f"<!-- STRATEGY REVIEWED: superseded by {newer_task_id} -->"
    insert_at = target_tag + 1
    if insert_at < len(lines) and re.match(
        r"^<!--\s*STRATEGY\s+(REVIEWED|REVIEW|PROPOSED|WITHDRAWN):",
        lines[insert_at],
        re.IGNORECASE,
    ):
        lines[insert_at] = review_marker
    else:
        lines.insert(insert_at, review_marker)

    new_text = "\n".join(lines) + ("\n" if text.endswith("\n") else "")
    tmp = task_path.with_suffix(task_path.suffix + ".tmp")
    tmp.write_text(new_text, encoding="utf-8")
    tmp.replace(task_path)
    return {
        "status": "written",
        "task_path": str(task_path.relative_to(repo_root)),
        "line": target_tag + 2,  # 1-based line where the marker now sits
        "marker": review_marker,
    }


def _dedent_callout_body(raw: str) -> str:
    """Turn a `> **Proposed change** — ... / > ... / > *Resolution:* ...`
    blockquote into its dedented body content:
      - drop the `> **Proposed change**` header line
      - drop the `> *Resolution: ...*` footer line
      - drop leading/trailing blank-quote lines
      - strip the `> ` (or `>`) prefix from remaining lines
    """
    lines = raw.splitlines()
    out: list[str] = []
    for line in lines:
        if _PROPOSAL_HEADER_RE.match(line):
            continue
        if _PROPOSAL_RESOLUTION_RE.match(line):
            continue
        if line.startswith("> "):
            out.append(line[2:])
        elif line.startswith(">"):
            out.append(line[1:])
        else:
            out.append(line)
    # Trim leading/trailing blank lines for a tidy insertion.
    while out and out[0].strip() == "":
        out.pop(0)
    while out and out[-1].strip() == "":
        out.pop()
    return "\n".join(out)


def perform_accept(
    repo_root: Path,
    doc: StrategyDoc,
    proposal: Proposal,
    actor: str,
    active_task_ids_: list[str],
) -> dict:
    """LIVE execution of Accept: promote the proposal callout to normal
    authoritative content (strip `> ` prefix + drop header/footer), remove
    the paired `<!-- STRATEGY PROPOSED -->` marker, then append a dated
    entry to `## History`.

    Strategy-doc-only — does NOT rewrite the source task's
    `<!-- STRATEGY CONTENT -->` tag yet (that's a higher blast-radius
    follow-up; older content remains in place above the promoted block).
    """
    if not actor:
        raise RuntimeError("refusing to execute without resolved actor")
    if not active_task_ids_:
        raise RuntimeError("refusing to execute without an active task in `.state/`")

    abs_path = repo_root / doc.virtual_path
    original = abs_path.read_text(encoding="utf-8")
    lines = original.splitlines()

    proposals = _parse_proposals(original)
    target = next((p for p in proposals if p.idx == proposal.idx), None)
    if target is None:
        raise RuntimeError(f"proposal #{proposal.idx} no longer present in {doc.virtual_path}")

    # Slice out the callout block, produce the dedented promoted content,
    # and swap it in. The promoted content replaces the callout lines
    # exactly — line count usually shrinks by 2–3 (lost header + footer).
    start = target.start_line - 1
    end = target.end_line - 1
    promoted = _dedent_callout_body(target.raw)

    # Assemble the rewrite: keep everything before the callout, insert the
    # promoted body, then pick up AFTER the callout — optionally consuming
    # a trailing `<!-- STRATEGY PROPOSED -->` marker + blanks.
    before = lines[:start]
    cursor = end + 1
    # Consume blank lines + the PROPOSED marker (if present) + one trailing blank.
    while cursor < len(lines) and lines[cursor].strip() == "":
        cursor += 1
    if cursor < len(lines) and re.match(
        r"^<!--\s*STRATEGY\s+PROPOSED:", lines[cursor], re.IGNORECASE
    ):
        cursor += 1
        if cursor < len(lines) and lines[cursor].strip() == "":
            cursor += 1
    after = lines[cursor:]

    kept = before + promoted.splitlines() + [""] + after
    kept_text = "\n".join(kept)
    history_line = build_history_entry_preview("accept", target, actor, active_task_ids_)
    new_text = _append_history_line(kept_text, actor, history_line)

    tmp = abs_path.with_suffix(abs_path.suffix + ".tmp")
    tmp.write_text(new_text, encoding="utf-8")
    tmp.replace(abs_path)

    # Source-task marker rewrite: mark the older task's STRATEGY CONTENT tag
    # as `<!-- STRATEGY REVIEWED: superseded by <newer_task> -->`. Best-effort:
    # skips gracefully when the task file is missing or multi-subsection
    # coverage prevents a clean mark.
    source_rewrite = {"status": "not-attempted", "reason": "no STRATEGY PROPOSED marker found"}
    marker = _find_proposed_marker(original, target.end_line)
    if marker is not None:
        older_task_id, section = marker
        newer_task_id = target.task_id or ""
        if newer_task_id:
            source_rewrite = _rewrite_source_task_marker(
                repo_root, older_task_id, newer_task_id, doc.domain, section
            )

    return {
        "virtual_path": doc.virtual_path,
        "lines_before": len(lines),
        "lines_after": new_text.count("\n") + 1,
        "promoted_body_preview": promoted[:200] + ("…" if len(promoted) > 200 else ""),
        "history_line": history_line,
        "actor": actor,
        "active_task_ids": list(active_task_ids_),
        "source_task_rewrite": source_rewrite,
    }


_STRATEGY_CONTENT_TAG_RE = re.compile(
    r"<!--\s*STRATEGY\s+CONTENT:\s*(?P<domain>[\w-]+)\b[^>]*-->",
    re.IGNORECASE,
)
_REVIEWED_OR_WITHDRAWN_RE = re.compile(
    r"<!--\s*STRATEGY\s+(?:REVIEWED:\s*superseded|WITHDRAWN)",
    re.IGNORECASE,
)


def _scan_tagged_tasks(repo_root: Path, domain: str) -> list[str]:
    """Return `<task_folder>/NNN` IDs for every task file containing an
    active `<!-- STRATEGY CONTENT: <domain> -->` tag whose block is not
    marked superseded / withdrawn on the next line."""
    tasks_dir = repo_root / "tasks"
    if not tasks_dir.is_dir():
        return []
    hits: list[str] = []
    for md in sorted(tasks_dir.glob("*/[0-9][0-9][0-9]-*.md")):
        try:
            lines = md.read_text(encoding="utf-8", errors="ignore").splitlines()
        except OSError:
            continue
        for i, line in enumerate(lines):
            m = _STRATEGY_CONTENT_TAG_RE.search(line)
            if not m:
                continue
            if m.group("domain").lower() != domain.lower():
                continue
            # Skip tags whose very-next line marks them superseded/withdrawn.
            if i + 1 < len(lines) and _REVIEWED_OR_WITHDRAWN_RE.search(lines[i + 1]):
                continue
            tid = f"{md.parent.name}/{md.name[:3]}"
            if tid not in hits:
                hits.append(tid)
            break  # one tag per task is enough to count it
    return hits


def perform_reassemble(
    repo_root: Path,
    doc: StrategyDoc,
    actor: str,
    active_task_ids_: list[str],
) -> dict:
    """LIVE re-assemble (detection pass): scan every task doc for active
    `<!-- STRATEGY CONTENT: <domain> -->` tags, diff against the strategy
    doc's current `<!-- Sources: -->` list, update the Sources + Assembled
    header metadata, and append a dated `## History` entry summarizing the
    delta.

    This is a detection+metadata pass, not a full content merge. For the
    full conflict-aware assembler (interactive accept/withdraw/leave on
    clashing subsections), run `/strategy assemble <domain>` from Claude
    Code — that agent writes `> **Proposed change**` callouts which the
    console then surfaces for per-proposal Accept / Reject / Modify.
    """
    if not actor:
        raise RuntimeError("refusing to execute without resolved actor")
    if not active_task_ids_:
        raise RuntimeError("refusing to execute without an active task in `.state/`")

    abs_path = repo_root / doc.virtual_path
    original = abs_path.read_text(encoding="utf-8")

    scanned = _scan_tagged_tasks(repo_root, doc.domain)
    current = list(doc.sources)  # from the `<!-- Sources: -->` header line
    # Normalize current to `<task_folder>/NNN` shape when possible. Existing
    # sources are stored as bare `NNN` (historical) or `folder/NNN` (v14+).
    current_norm: list[str] = []
    for s in current:
        if "/" in s:
            current_norm.append(s)
        elif s.isdigit():
            # Best-effort: map to ben/ folder if that's the only match.
            cands = list((repo_root / "tasks").glob(f"*/{s}-*.md"))
            current_norm.append(
                f"{cands[0].parent.name}/{s}" if len(cands) == 1 else s
            )
        else:
            current_norm.append(s)

    scanned_set = set(scanned)
    current_set = set(current_norm)
    added = sorted(scanned_set - current_set)
    removed = sorted(current_set - scanned_set)

    # Update the header metadata. Replace `<!-- Assembled: ... -->` with
    # today + actor attribution, and `<!-- Sources: ... -->` with the
    # scanned task list.
    today = _today()
    new_assembled = f"<!-- Assembled: {today} by console re-assemble ({actor}) -->"
    new_sources = f"<!-- Sources: {', '.join(scanned)} -->" if scanned else "<!-- Sources: -->"

    text = re.sub(
        r"<!--\s*Assembled:[^>]*-->",
        new_assembled,
        original,
        count=1,
        flags=re.IGNORECASE,
    )
    if "<!-- Sources:" in text or "<!-- Sources " in text:
        text = re.sub(
            r"<!--\s*Sources:[^>]*-->",
            new_sources,
            text,
            count=1,
            flags=re.IGNORECASE,
        )
    else:
        # Insert under the existing Assembled line for consistency.
        text = text.replace(new_assembled, new_assembled + "\n" + new_sources, 1)

    # Build the History entry body.
    body_bits: list[str] = []
    if added:
        body_bits.append(f"- **Added sources:** {', '.join(added)}")
    if removed:
        body_bits.append(f"- **Removed sources:** {', '.join(removed)} (no active STRATEGY CONTENT tag found)")
    if not added and not removed:
        body_bits.append("- No source-list changes detected since last assembly.")
    body_bits.append(
        f"- {len(scanned)} active tagged task(s) scanned; full conflict-aware merge still requires "
        f"`/strategy assemble {doc.domain}` from Claude Code."
    )

    history_line = (
        f"- {_hhmm()} · **Re-assemble** (detection pass) · by {actor} · "
        f"under task {active_task_ids_[0]} · {len(scanned)} sources"
    )
    text = _append_history_line(text, actor, history_line)
    # Append the delta bullets under the same actor-entry (same date).
    # Simplest approach: add them as a follow-up line below the action line.
    for bit in body_bits:
        text = _append_history_line(text, actor, "  " + bit)

    tmp = abs_path.with_suffix(abs_path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(abs_path)

    return {
        "virtual_path": doc.virtual_path,
        "scanned_sources": scanned,
        "added_sources": added,
        "removed_sources": removed,
        "history_line": history_line,
        "actor": actor,
        "active_task_ids": list(active_task_ids_),
        "note": (
            "Detection pass only — no content merged. For full conflict-aware "
            f"assembly with interactive accept/withdraw/leave, run `/strategy "
            f"assemble {doc.domain}` from Claude Code; the resulting "
            f"> **Proposed change** callouts will then show up here for "
            f"per-proposal Accept / Reject / Modify."
        ),
    }


def perform_recategorize(
    repo_root: Path,
    doc: StrategyDoc,
    proposal: Proposal,
    new_domain: str,
    actor: str,
    active_task_ids_: list[str],
) -> dict:
    """LIVE execution of Re-categorize: the proposal was routed to the
    wrong strategy domain. Action:
      1. Strip the callout + STRATEGY PROPOSED marker from the current
         strategy doc (same teardown as Reject).
      2. Rewrite the source task's `<!-- STRATEGY CONTENT: <old_domain>, ... -->`
         tag to use `<new_domain>` instead, so future assemblies route it
         correctly. Best-effort: skips if the task file can't be located
         or the tag is ambiguous.
      3. Append a History entry to the strategy doc noting the move.
    """
    if not actor:
        raise RuntimeError("refusing to execute without resolved actor")
    if not active_task_ids_:
        raise RuntimeError("refusing to execute without an active task in `.state/`")
    if not new_domain or new_domain == doc.domain:
        raise RuntimeError(f"new_domain must differ from current domain {doc.domain!r}")

    abs_path = repo_root / doc.virtual_path
    original = abs_path.read_text(encoding="utf-8")
    lines = original.splitlines()

    proposals = _parse_proposals(original)
    target = next((p for p in proposals if p.idx == proposal.idx), None)
    if target is None:
        raise RuntimeError(f"proposal #{proposal.idx} no longer present in {doc.virtual_path}")

    # Step 1: strip the callout block + paired STRATEGY PROPOSED marker.
    start = target.start_line - 1
    end = target.end_line - 1
    drop_lines = set(range(start, end + 1))
    cursor = end + 1
    while cursor < len(lines) and lines[cursor].strip() == "":
        drop_lines.add(cursor)
        cursor += 1
    if cursor < len(lines) and re.match(
        r"^<!--\s*STRATEGY\s+PROPOSED:", lines[cursor], re.IGNORECASE
    ):
        drop_lines.add(cursor)
        cursor += 1
        if cursor < len(lines) and lines[cursor].strip() == "":
            drop_lines.add(cursor)
    kept = [ln for i, ln in enumerate(lines) if i not in drop_lines]

    history_line = (
        f"- {_hhmm()} · **Recategorize** · \"{target.heading or '(no heading)'}\" "
        f"({target.task_id or '?'}) → **{new_domain}** · by {actor} · "
        f"under task {active_task_ids_[0]}"
    )
    new_text = _append_history_line("\n".join(kept), actor, history_line)

    tmp = abs_path.with_suffix(abs_path.suffix + ".tmp")
    tmp.write_text(new_text, encoding="utf-8")
    tmp.replace(abs_path)

    # Step 2: rewrite the source task's STRATEGY CONTENT tag domain key.
    source_rewrite = _rewrite_source_task_domain(
        repo_root, target.task_id or "", doc.domain, new_domain
    )

    return {
        "virtual_path": doc.virtual_path,
        "history_line": history_line,
        "actor": actor,
        "active_task_ids": list(active_task_ids_),
        "from_domain": doc.domain,
        "to_domain": new_domain,
        "source_task_rewrite": source_rewrite,
    }


def _resolve_task_path(repo_root: Path, task_id: str) -> tuple[Path | None, str]:
    """Resolve a task reference to a file path. Accepts both:
      • `<folder>/NNN` (canonical v14+)
      • `NNN` (bare numeric — globbed across every actor folder)
    Returns `(path, canonical_id)` on success, `(None, reason)` on failure
    (where reason is a short string describing what went wrong)."""
    if "/" in task_id:
        folder, num = task_id.split("/", 1)
        if not num.isdigit():
            return None, f"malformed task id: {task_id!r}"
        cands = sorted((repo_root / "tasks" / folder).glob(f"{num}-*.md"))
        if len(cands) == 1:
            return cands[0], f"{folder}/{num}"
        return None, f"task file for {task_id} not found"
    # Bare numeric — search every actor folder.
    if not task_id.isdigit():
        return None, f"unrecognized task id: {task_id!r}"
    cands = sorted((repo_root / "tasks").glob(f"*/{task_id}-*.md"))
    if len(cands) == 1:
        canonical = f"{cands[0].parent.name}/{task_id}"
        return cands[0], canonical
    if len(cands) == 0:
        return None, f"no task file matches bare id {task_id!r}"
    folders = ", ".join(c.parent.name for c in cands)
    return None, f"bare id {task_id!r} matches multiple folders ({folders}) — ambiguous"


def _rewrite_source_task_domain(
    repo_root: Path, task_id: str, old_domain: str, new_domain: str
) -> dict:
    """Open the source task and replace `<!-- STRATEGY CONTENT: <old>, ... -->`
    with `<!-- STRATEGY CONTENT: <new>, ... -->`. Returns a diagnostic dict.
    Skips if multiple matching tags are present (ambiguous)."""
    p, resolved = _resolve_task_path(repo_root, task_id)
    if p is None:
        return {"status": "skipped", "reason": resolved}
    canonical_id = resolved
    text = p.read_text(encoding="utf-8")
    rx = re.compile(
        rf"(<!--\s*STRATEGY\s+CONTENT:\s*){re.escape(old_domain)}(\b)",
        re.IGNORECASE,
    )
    matches = list(rx.finditer(text))
    if not matches:
        return {
            "status": "skipped",
            "reason": f"no STRATEGY CONTENT tag with domain={old_domain!r} in {p.relative_to(repo_root)}",
        }
    # Multiple matches usually means the whole task's strategy contributions
    # belong to one domain (e.g. SUPERSEDED + CURRENT pair sharing a topic);
    # bulk-rewrite all of them so the task's authoritative routing flips
    # cleanly. Diagnostic includes the count for transparency.
    new_text = rx.sub(rf"\g<1>{new_domain}\g<2>", text)
    if new_text == text:
        return {"status": "skipped", "reason": "no change applied"}
    tmp = p.with_suffix(p.suffix + ".tmp")
    tmp.write_text(new_text, encoding="utf-8")
    tmp.replace(p)
    return {
        "status": "written",
        "task_path": str(p.relative_to(repo_root)),
        "resolved_task_id": canonical_id,
        "from_domain": old_domain,
        "to_domain": new_domain,
        "rewrites_applied": len(matches),
    }


_DOMAIN_PREFIXES = {
    "regulatory": "REG", "commercial": "COMM", "architecture": "ARCH",
    "development": "DEV", "testing": "TEST", "risk": "RISK",
    "postmarket": "POSTM", "operations": "OPS",
}


def _next_decision_id(repo_root: Path, doc: StrategyDoc, section_label: str) -> str:
    """Allocate the next D-<DOMAIN>-<SECTION>.<INDEX> id under the named
    section. Looks at every existing decision in the doc and finds
    max-index-in-section + 1 (never reuses a retired id)."""
    abs_path = repo_root / doc.virtual_path
    text = abs_path.read_text(encoding="utf-8")
    decisions = parse_decisions(text)
    prefix = _DOMAIN_PREFIXES.get(doc.domain.lower()) or doc.domain.upper()[:4]
    # Section index — take leading number from "## N. ..." or sequential.
    sec_idx = None
    m = re.match(r"^\s*(\d+)\.", section_label)
    if m:
        sec_idx = int(m.group(1))
    else:
        # Walk H2s in order and pick this one's position.
        seq = 0
        for line in text.splitlines():
            if line.startswith("## ") and not line.startswith("### "):
                heading = line[3:].strip()
                seq += 1
                if heading == section_label:
                    sec_idx = seq
                    break
    if sec_idx is None:
        raise RuntimeError(f"could not resolve section index for {section_label!r}")
    # Highest index in this section + 1.
    max_idx = 0
    pat = re.compile(rf"^D-{re.escape(prefix)}-{sec_idx}\.(\d+)$")
    for d in decisions:
        m2 = pat.match(d.id or "")
        if m2:
            max_idx = max(max_idx, int(m2.group(1)))
    return f"D-{prefix}-{sec_idx}.{max_idx + 1}"


def _find_decision_block(text: str, decision_id: str) -> tuple[int, int] | None:
    """Return (start_line_idx, end_line_idx) 0-based inclusive for the
    decision block matching `decision_id`, or None if not found."""
    lines = text.splitlines()
    start = None
    for i, line in enumerate(lines):
        m = _DECISION_START_LINE_RE.match(line)
        if m:
            meta = _parse_decision_metadata(m.group("meta"))
            if meta.get("id") == decision_id:
                start = i
                break
    if start is None:
        return None
    for j in range(start + 1, len(lines)):
        if _DECISION_END_LINE_RE.match(lines[j]):
            return (start, j)
    return None


def _rewrite_start_sentinel_meta(line: str, updates: dict) -> str:
    """Take a `<!-- DECISION:start id=... status=... -->` line and update
    the named keys (preserving order; appends new keys at the end)."""
    m = _DECISION_START_LINE_RE.match(line)
    if not m:
        return line
    meta = _parse_decision_metadata(m.group("meta"))
    for k, v in updates.items():
        meta[k] = v
    parts = []
    # Preserve canonical key order: id, status, source, created, last-edited,
    # supersedes, withdrawn-date, withdrawn-by, then any extras.
    canonical = ["id", "status", "source", "created", "last-edited",
                 "supersedes", "withdrawn-date", "withdrawn-by"]
    for k in canonical:
        if k in meta:
            parts.append(f"{k}={meta[k]}")
    for k, v in meta.items():
        if k not in canonical:
            parts.append(f"{k}={v}")
    return f"<!-- DECISION:start {' '.join(parts)} -->"


def perform_decision_edit(
    repo_root: Path,
    doc: StrategyDoc,
    decision_id: str,
    new_body: str,
    actor: str,
    active_task_ids_: list[str],
) -> dict:
    """LIVE: replace a decision's body in-place + bump last-edited."""
    if not actor or not active_task_ids_:
        raise RuntimeError("actor + active task required")
    if not new_body or not new_body.strip():
        raise RuntimeError("new_body cannot be empty")
    abs_path = repo_root / doc.virtual_path
    text = abs_path.read_text(encoding="utf-8")
    bounds = _find_decision_block(text, decision_id)
    if bounds is None:
        raise RuntimeError(f"decision {decision_id} not found in {doc.virtual_path}")
    s, e = bounds
    lines = text.splitlines()
    lines[s] = _rewrite_start_sentinel_meta(lines[s], {"last-edited": _today()})
    # Body = everything between start and end, including the H3.
    new_block = [lines[s], "", new_body.strip(), "", lines[e]]
    out = lines[:s] + new_block + lines[e + 1:]
    history_line = f"- {_hhmm()} · **Edit decision** · {decision_id} · by {actor} · under task {active_task_ids_[0]}"
    new_text = _append_history_line("\n".join(out), actor, history_line)
    tmp = abs_path.with_suffix(abs_path.suffix + ".tmp")
    tmp.write_text(new_text, encoding="utf-8")
    tmp.replace(abs_path)
    return {
        "decision_id": decision_id,
        "virtual_path": doc.virtual_path,
        "history_line": history_line,
        "actor": actor,
        "active_task_ids": list(active_task_ids_),
    }


def perform_decision_remove(
    repo_root: Path,
    doc: StrategyDoc,
    decision_id: str,
    actor: str,
    active_task_ids_: list[str],
) -> dict:
    """LIVE: flip a decision's status to `withdrawn` (kept for audit)."""
    if not actor or not active_task_ids_:
        raise RuntimeError("actor + active task required")
    abs_path = repo_root / doc.virtual_path
    text = abs_path.read_text(encoding="utf-8")
    bounds = _find_decision_block(text, decision_id)
    if bounds is None:
        raise RuntimeError(f"decision {decision_id} not found in {doc.virtual_path}")
    s, _ = bounds
    lines = text.splitlines()
    lines[s] = _rewrite_start_sentinel_meta(lines[s], {
        "status": "withdrawn",
        "withdrawn-date": _today(),
        "withdrawn-by": actor.replace(" ", "-"),
    })
    history_line = f"- {_hhmm()} · **Remove decision** · {decision_id} (withdrawn) · by {actor} · under task {active_task_ids_[0]}"
    new_text = _append_history_line("\n".join(lines), actor, history_line)
    tmp = abs_path.with_suffix(abs_path.suffix + ".tmp")
    tmp.write_text(new_text, encoding="utf-8")
    tmp.replace(abs_path)
    return {
        "decision_id": decision_id,
        "virtual_path": doc.virtual_path,
        "new_status": "withdrawn",
        "history_line": history_line,
        "actor": actor,
        "active_task_ids": list(active_task_ids_),
    }


def section_block(text: str, section_idx: int) -> tuple[int, int, str] | None:
    """Locate the H2 section whose leading number matches `section_idx`.
    Returns `(start_line_idx, end_line_idx_exclusive, label)` 0-based, or
    None if not found. The section spans from its `## ` line to the line
    BEFORE the next `## ` heading (or EOF)."""
    lines = text.splitlines()
    pat = re.compile(rf"^##\s+{section_idx}\.\s+(.+?)\s*$")
    start = None
    label = ""
    for i, line in enumerate(lines):
        m = pat.match(line)
        if m:
            start = i
            label = f"{section_idx}. {m.group(1)}"
            break
    if start is None:
        return None
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if lines[j].startswith("## ") and not lines[j].startswith("### "):
            end = j
            break
    return (start, end, label)


def section_md(text: str, section_idx: int) -> str:
    """Return the raw markdown for section `section_idx`."""
    bounds = section_block(text, section_idx)
    if bounds is None:
        return ""
    s, e, _ = bounds
    return "\n".join(text.splitlines()[s:e]).rstrip() + "\n"


def perform_section_edit(
    repo_root: Path,
    doc: StrategyDoc,
    section_idx: int,
    new_section_md: str,
    actor: str,
    active_task_ids_: list[str],
) -> dict:
    """LIVE: replace an entire H2 section with new content. The
    `new_section_md` may include `<!-- DECISION:start id=NEW ... -->` for
    decisions to add; we allocate real IDs (`D-<DOM>-<sec>.<idx>`) on
    write. Existing decision IDs are preserved verbatim."""
    if not actor or not active_task_ids_:
        raise RuntimeError("actor + active task required")
    if not new_section_md.strip():
        raise RuntimeError("new_section_md cannot be empty")

    abs_path = repo_root / doc.virtual_path
    text = abs_path.read_text(encoding="utf-8")
    bounds = section_block(text, section_idx)
    if bounds is None:
        raise RuntimeError(f"section {section_idx} not found in {doc.virtual_path}")
    s, e, _ = bounds

    # Collect existing decision IDs in this section so we can preserve any
    # the synthesis brought back AND track which ones were dropped.
    original_decisions = parse_decisions("\n".join(text.splitlines()[s:e]))
    original_ids = {d.id for d in original_decisions if d.id}

    # Allocate IDs for `id=NEW` placeholders. Compute next-available index
    # within this section; never reuse a retired ID.
    prefix = _DOMAIN_PREFIXES.get(doc.domain.lower()) or doc.domain.upper()[:4]
    pat_id = re.compile(rf"^D-{re.escape(prefix)}-{section_idx}\.(\d+)$")
    max_idx = 0
    # Walk the WHOLE doc for IDs in this section (catches retired/withdrawn too).
    for d in parse_decisions(text):
        m = pat_id.match(d.id or "")
        if m:
            max_idx = max(max_idx, int(m.group(1)))

    new_lines = new_section_md.splitlines()
    next_new_idx = max_idx
    new_ids_assigned: list[str] = []
    rewritten: list[str] = []
    for line in new_lines:
        m_start = re.match(
            r"^(<!--\s+DECISION:start\s+)(.+?)(\s+-->\s*)$", line
        )
        if m_start:
            meta = _parse_decision_metadata(m_start.group(2))
            if meta.get("id") in (None, "", "NEW"):
                next_new_idx += 1
                new_id = f"D-{prefix}-{section_idx}.{next_new_idx}"
                meta["id"] = new_id
                meta.setdefault("status", "active")
                meta.setdefault("created", _today())
                new_ids_assigned.append(new_id)
                # Re-serialize meta in canonical order.
                ordered = []
                for k in ("id", "status", "source", "created", "last-edited",
                         "supersedes", "withdrawn-date", "withdrawn-by"):
                    if k in meta:
                        ordered.append(f"{k}={meta[k]}")
                for k, v in meta.items():
                    if k not in ("id", "status", "source", "created",
                                 "last-edited", "supersedes", "withdrawn-date",
                                 "withdrawn-by"):
                        ordered.append(f"{k}={v}")
                rewritten.append(
                    f"{m_start.group(1)}{' '.join(ordered)}{m_start.group(3).rstrip()}"
                )
                continue
            # For existing IDs, bump last-edited.
            if "id" in meta and meta["id"] in original_ids:
                meta["last-edited"] = _today()
                ordered = []
                for k in ("id", "status", "source", "created", "last-edited",
                         "supersedes", "withdrawn-date", "withdrawn-by"):
                    if k in meta:
                        ordered.append(f"{k}={meta[k]}")
                rewritten.append(
                    f"{m_start.group(1)}{' '.join(ordered)}{m_start.group(3).rstrip()}"
                )
                continue
        m_end = re.match(r"^(<!--\s+DECISION:end\s+id=)NEW(\s*-->\s*)$", line)
        if m_end and new_ids_assigned:
            # Pair the most-recently-assigned NEW id with this end sentinel.
            # If multiple unpaired NEWs exist, pop FIFO via a counter.
            pass  # We'll pair below.
        rewritten.append(line)

    # Second pass: pair `DECISION:end id=NEW` with the immediately-prior
    # `DECISION:start` line that just got an allocated id.
    paired_new_ids = list(new_ids_assigned)
    for i in range(len(rewritten)):
        m_end = re.match(
            r"^(<!--\s+DECISION:end\s+)id=NEW(\s*-->\s*)$", rewritten[i]
        )
        if m_end and paired_new_ids:
            allocated = paired_new_ids.pop(0)
            rewritten[i] = f"{m_end.group(1)}id={allocated}{m_end.group(2).rstrip()}"

    new_section_text = "\n".join(rewritten).rstrip() + "\n"

    # Splice into the doc.
    pre = text.splitlines()[:s]
    post = text.splitlines()[e:]
    new_text_lines = pre + new_section_text.splitlines() + [""] + post
    final_text = "\n".join(new_text_lines)

    # Append history line.
    final_decisions = parse_decisions(new_section_text)
    final_ids = {d.id for d in final_decisions if d.id}
    added = sorted(final_ids - original_ids)
    removed = sorted(original_ids - final_ids)
    edited = sorted(original_ids & final_ids)
    summary_bits = []
    if added: summary_bits.append(f"added {', '.join(added)}")
    if removed: summary_bits.append(f"removed {', '.join(removed)}")
    if edited: summary_bits.append(f"edited {', '.join(edited)}")
    summary = "; ".join(summary_bits) or "no decision changes"
    history_line = (
        f"- {_hhmm()} · **Edit section** · section {section_idx} "
        f"({summary}) · by {actor} · under task {active_task_ids_[0]}"
    )
    final_text = _append_history_line(final_text, actor, history_line)

    tmp = abs_path.with_suffix(abs_path.suffix + ".tmp")
    tmp.write_text(final_text, encoding="utf-8")
    tmp.replace(abs_path)
    return {
        "virtual_path": doc.virtual_path,
        "section_idx": section_idx,
        "added_ids": added,
        "removed_ids": removed,
        "edited_ids": edited,
        "history_line": history_line,
        "actor": actor,
        "active_task_ids": list(active_task_ids_),
    }


def perform_decision_add(
    repo_root: Path,
    doc: StrategyDoc,
    section_label: str,
    heading: str,
    new_body: str,
    actor: str,
    active_task_ids_: list[str],
) -> dict:
    """LIVE: append a new active decision under the named section."""
    if not actor or not active_task_ids_:
        raise RuntimeError("actor + active task required")
    if not heading.strip() or not new_body.strip():
        raise RuntimeError("heading + new_body required")
    abs_path = repo_root / doc.virtual_path
    text = abs_path.read_text(encoding="utf-8")
    decision_id = _next_decision_id(repo_root, doc, section_label)
    # Locate end of the named section. End = next H2 (or EOF).
    lines = text.splitlines()
    sec_start = None
    for i, line in enumerate(lines):
        if line.startswith("## ") and not line.startswith("### ") and line[3:].strip() == section_label.strip():
            sec_start = i
            break
    if sec_start is None:
        raise RuntimeError(f"section {section_label!r} not found in {doc.virtual_path}")
    sec_end = len(lines)
    for j in range(sec_start + 1, len(lines)):
        if lines[j].startswith("## ") and not lines[j].startswith("### "):
            sec_end = j
            break
    # Numeric prefix `<sec>.<idx>` derived from the allocated decision_id.
    _id_tail = decision_id.rsplit("-", 1)[-1]   # e.g. "1.4"
    heading_clean = heading.strip()
    # If the user already typed the prefix, don't double-stamp.
    if not _NUMBER_PREFIX_RE.match(heading_clean):
        heading_clean = f"{_id_tail} {heading_clean}"
    new_block = [
        "",
        f"<!-- DECISION:start id={decision_id} status=active created={_today()} -->",
        f"### {heading_clean}",
        "",
        new_body.strip(),
        "",
        f"<!-- DECISION:end id={decision_id} -->",
        "",
    ]
    out = lines[:sec_end] + new_block + lines[sec_end:]
    history_line = f"- {_hhmm()} · **Add decision** · {decision_id} · \"{heading.strip()}\" · by {actor} · under task {active_task_ids_[0]}"
    new_text = _append_history_line("\n".join(out), actor, history_line)
    tmp = abs_path.with_suffix(abs_path.suffix + ".tmp")
    tmp.write_text(new_text, encoding="utf-8")
    tmp.replace(abs_path)
    return {
        "decision_id": decision_id,
        "virtual_path": doc.virtual_path,
        "section_label": section_label,
        "heading": heading.strip(),
        "history_line": history_line,
        "actor": actor,
        "active_task_ids": list(active_task_ids_),
    }


def perform_modify(
    repo_root: Path,
    doc: StrategyDoc,
    proposal: Proposal,
    new_body: str,
    actor: str,
    active_task_ids_: list[str],
) -> dict:
    """LIVE execution of Modify: replace the callout body with the user's
    edited text, keeping the proposal pending (still a blockquote, still
    paired with its `<!-- STRATEGY PROPOSED -->` marker). Appends a dated
    `## History` entry."""
    if not actor:
        raise RuntimeError("refusing to execute without resolved actor")
    if not active_task_ids_:
        raise RuntimeError("refusing to execute without an active task in `.state/`")
    if new_body is None or not new_body.strip():
        raise RuntimeError("modify requires a non-empty `new_body`")

    abs_path = repo_root / doc.virtual_path
    original = abs_path.read_text(encoding="utf-8")
    lines = original.splitlines()

    proposals = _parse_proposals(original)
    target = next((p for p in proposals if p.idx == proposal.idx), None)
    if target is None:
        raise RuntimeError(f"proposal #{proposal.idx} no longer present in {doc.virtual_path}")

    # Build the replacement callout:
    #   > **Proposed change** — <task> ("<heading>", <author>, <date>)   (preserved)
    #   > <new body, line by line, with > prefix>
    #   >
    #   > *Resolution: re-run /strategy assemble and pick accept / withdraw / leave.*
    hdr_line = lines[target.start_line - 1]  # keep the original header verbatim
    body_lines = [f"> {ln}" if ln else ">" for ln in new_body.strip().splitlines()]
    resolution = "> *Resolution: re-run /strategy assemble and pick accept / withdraw / leave.*"

    new_callout = [hdr_line, ">", *body_lines, ">", resolution]

    start = target.start_line - 1
    end = target.end_line - 1
    before = lines[:start]
    after = lines[end + 1:]
    kept = before + new_callout + after
    kept_text = "\n".join(kept)
    history_line = build_history_entry_preview("modify", target, actor, active_task_ids_)
    new_text = _append_history_line(kept_text, actor, history_line)

    tmp = abs_path.with_suffix(abs_path.suffix + ".tmp")
    tmp.write_text(new_text, encoding="utf-8")
    tmp.replace(abs_path)

    return {
        "virtual_path": doc.virtual_path,
        "lines_before": len(lines),
        "lines_after": new_text.count("\n") + 1,
        "new_body_preview": new_body.strip()[:200] + ("…" if len(new_body.strip()) > 200 else ""),
        "history_line": history_line,
        "actor": actor,
        "active_task_ids": list(active_task_ids_),
    }


def perform_reject(
    repo_root: Path,
    doc: StrategyDoc,
    proposal: Proposal,
    actor: str,
    active_task_ids_: list[str],
) -> dict:
    """LIVE execution of Reject: strip the proposal callout + its paired
    `<!-- STRATEGY PROPOSED: -->` marker from the strategy doc, then append
    a dated entry to the `## History` section.

    Safe because it only touches the strategy doc (not source task docs).
    Returns a summary dict with before/after line counts + the history line.
    Raises RuntimeError on any inconsistency before writing (no partial state).
    """
    if not actor:
        raise RuntimeError("refusing to execute without resolved actor")
    if not active_task_ids_:
        raise RuntimeError("refusing to execute without an active task in `.state/`")

    abs_path = repo_root / doc.virtual_path
    original = abs_path.read_text(encoding="utf-8")
    lines = original.splitlines()

    # Re-parse to locate the current line numbers for the target proposal.
    proposals = _parse_proposals(original)
    target = next((p for p in proposals if p.idx == proposal.idx), None)
    if target is None:
        raise RuntimeError(f"proposal #{proposal.idx} no longer present in {doc.virtual_path}")

    # Slice out the callout block (inclusive on both ends). Then also drop
    # any immediately-following blank lines + `<!-- STRATEGY PROPOSED -->`
    # marker that belongs to this proposal, so the doc reads cleanly.
    start = target.start_line - 1  # back to 0-based
    end = target.end_line - 1       # inclusive
    drop_lines = set(range(start, end + 1))
    # Trailing marker cleanup: skip blank lines, then if the next line is
    # the PROPOSED marker, drop it + one trailing blank.
    cursor = end + 1
    while cursor < len(lines) and lines[cursor].strip() == "":
        drop_lines.add(cursor)
        cursor += 1
    if cursor < len(lines) and re.match(
        r"^<!--\s*STRATEGY\s+PROPOSED:", lines[cursor], re.IGNORECASE
    ):
        drop_lines.add(cursor)
        cursor += 1
        # Optionally eat one trailing blank for tidy output.
        if cursor < len(lines) and lines[cursor].strip() == "":
            drop_lines.add(cursor)

    kept = [ln for i, ln in enumerate(lines) if i not in drop_lines]

    # Append the history entry. If `## History` section exists, insert the
    # line under today's entry (creating the entry if missing). Otherwise
    # create the section at the end of the doc.
    history_line = build_history_entry_preview("reject", target, actor, active_task_ids_)
    kept_text = "\n".join(kept)
    new_text = _append_history_line(kept_text, actor, history_line)

    # Atomic write via temp file in the same directory.
    tmp = abs_path.with_suffix(abs_path.suffix + ".tmp")
    tmp.write_text(new_text, encoding="utf-8")
    tmp.replace(abs_path)

    return {
        "virtual_path": doc.virtual_path,
        "lines_before": len(lines),
        "lines_after": len(kept) + (new_text.count("\n") - kept_text.count("\n")),
        "dropped_lines": sorted(drop_lines),
        "history_line": history_line,
        "actor": actor,
        "active_task_ids": list(active_task_ids_),
    }


_HISTORY_HEAD_RE = re.compile(r"^##\s+(?:Assembly\s+)?History\s*$", re.IGNORECASE | re.MULTILINE)
_TODAY_ENTRY_RE = None  # computed lazily per call


def _append_history_line(text: str, actor: str, line: str) -> str:
    """Insert `line` into today's `### YYYY-MM-DD — reviewed by <actor>` entry
    under `## History`, creating the section and/or entry if missing."""
    today = _today()
    m = _HISTORY_HEAD_RE.search(text)
    if not m:
        # No History section — append a new one at the end of the doc.
        suffix = "" if text.endswith("\n") else "\n"
        block = (
            f"{suffix}\n## History\n\n"
            f"### {today} — reviewed by {actor}\n\n{line}\n"
        )
        return text + block

    # Find the Assembly-History section body (between this `## History` heading
    # and the next `## ` heading). We'll place today's entry at the top of
    # that body so newest is first.
    head_end = m.end()
    # Identify the next `## ` heading (same level) AFTER this one.
    tail_iter = re.compile(r"^##\s+[^#]", re.MULTILINE)
    next_m = tail_iter.search(text, pos=head_end)
    sec_end = next_m.start() if next_m else len(text)
    section = text[head_end:sec_end]
    rest = text[sec_end:]

    # Look for an existing `### <today> — reviewed by <actor>` entry in the
    # section. If found, append `line` to its body. Else prepend a new entry.
    entry_head_re = re.compile(
        rf"^###\s+{re.escape(today)}\s+—\s+reviewed\s+by\s+{re.escape(actor)}\s*$",
        re.IGNORECASE | re.MULTILINE,
    )
    em = entry_head_re.search(section)
    if em:
        # Find end of this entry (next `### ` or end of section).
        next_h3 = re.search(r"^###\s+", section[em.end():], re.MULTILINE)
        entry_end = em.end() + (next_h3.start() if next_h3 else len(section) - em.end())
        # Insert our line just before entry_end, keeping any trailing blank line.
        body = section[em.end():entry_end].rstrip("\n")
        updated = section[:em.end()] + body + f"\n{line}\n\n" + section[entry_end:]
        return text[:head_end] + updated + rest

    # No entry for this actor today → prepend a new one at the top of the
    # section. Normalize surrounding whitespace to stay tidy.
    new_entry = f"\n\n### {today} — reviewed by {actor}\n\n{line}\n"
    return text[:head_end] + new_entry + section.lstrip("\n") + rest
