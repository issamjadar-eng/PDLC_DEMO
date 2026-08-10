"""Strategy landing-page loader — per-domain summaries for the `/strategy` index.

Pure display-only projection. The strategy documents under
`docs/project/strategies/` stay canonical; nothing here is authored, cached to
disk, or written back. The `strategy` skill owns assembly; this only counts.

PARSERS ARE REUSED, NOT REWRITTEN. Every shape this module needs is already
parsed by `console.workflows.b3_strategy_reassembly` — `scan()` for the
per-doc header/status/proposal/history counts, `parse_decisions()` for the v15
`<!-- DECISION:start … -->` blocks. A second parser here would be a second
thing to keep in step with the strategy skill's format.

TWO DECISION FORMATS COEXIST, AND THEY MUST NOT BE SUMMED (HARD RULE).
As of 2026-08-06 exactly one of eight strategy docs (`commercial`) has been
migrated to the v15 DECISION-block format; `regulatory` and `architecture`
still carry their decisions as legacy `**Decision**:` prose lines. Counting
only v15 blocks reports those two as "0 decided", which is false. Summing the
two reports `commercial` as 18, which is also false — verified: all 9 of its
legacy lines sit *inside* its 9 v15 blocks, because the sentinels wrap the
prose rather than replacing it.

The rule is therefore `v15 if v15 else legacy`, and each domain reports which
`decision_format` it counted. The UI must surface that distinction rather than
flatten it: a v15 block carries a lifecycle `status=`; a legacy line carries
none, so a legacy doc has a decision COUNT but no status BREAKDOWN. Presenting
an empty breakdown as "0 approved" would invent a fact the document does not
state.
"""
from __future__ import annotations

import re
from pathlib import Path

from console.workflows import b3_strategy_reassembly as b3

_STRATEGIES_DIR = ("docs", "project", "strategies")

# A legacy decision: `**Decision**:` at the head of its own line. Anchored with
# MULTILINE rather than scanned per-line so an indented mention inside a
# blockquote or list does not count as a decision of the document's own.
_LEGACY_DECISION_RE = re.compile(r"^\*\*Decision\*\*:", re.MULTILINE)

# The doc's opening prose line — the card's one-line intent. Taken from the
# first non-blank, non-structural line after the H1, so the card says something
# about the domain instead of repeating its title.
_STRUCTURAL_PREFIXES = ("#", "<!--", "|", ">", "- ", "* ", "```", "_")

# Header status emitted by the strategy skill for a scaffolded-but-unwritten
# brief. Treated as the authoritative stub signal; a byte-size heuristic would
# disagree with the skill the moment a template grows.
_STUB_STATUS = "awaiting-content"

# Lifecycle states a v15 DECISION block can carry. Order is render order.
# `active` is the only one observed in this project so far; the rest are
# declared because the parser's default is `active` and an unseen state must
# render as itself rather than silently fall into the active bucket.
DECISION_STATES = ("active", "proposed-change", "superseded", "withdrawn")


def _root(repo_root: Path) -> Path:
    return repo_root.joinpath(*_STRATEGIES_DIR)


def discover(repo_root: Path) -> dict:
    """Nav-visibility probe (stat only). Wrapped by the caller in app.py —
    a raise inside a nav probe 500s every route in the console."""
    root = _root(repo_root)
    return {"has_any": root.is_dir() and any(root.glob("*-strategy.md"))}


def _first_prose(lines: list[str]) -> str:
    """First substantive prose line in `lines`, stopping at the next H2.

    Skips the italic `_…_` template-guidance line the strategy skill's
    templates put directly under each heading — that line describes what the
    section is FOR, not what this project decided, so surfacing it would make
    every domain card read identically.
    """
    for raw in lines:
        line = raw.strip()
        if line.startswith("## "):
            break
        if not line or line.startswith(_STRUCTURAL_PREFIXES):
            continue
        return line[:240] + ("…" if len(line) > 240 else "")
    return ""


def _intent_line(text: str) -> str:
    """The card's one-line summary of what this domain covers.

    Two document shapes exist in this project and the rule handles both by
    looking where each one actually keeps its framing:

    1. `## Scope & Approach` (the `default-strategy.md` template) — its body is
       written to be exactly this summary. Six of eight docs use it.
    2. No scope section (`regulatory-strategy.md` uses a custom template that
       goes H1 → `## Plans Informed` → numbered body) — fall back to preamble
       prose before the first H2.

    Returns "" when neither yields anything. That is the honest outcome and it
    renders as no line at all. An earlier unbounded scan returned the first
    `**Decision**:` line it met instead, which put a specific decision on the
    card in the place reserved for a general summary.
    """
    lines = text.splitlines()
    for i, raw in enumerate(lines):
        if re.match(r"^##\s+Scope\b", raw.strip(), re.IGNORECASE):
            found = _first_prose(lines[i + 1:])
            if found:
                return found
            break
    return _first_prose(lines[1:])


def _count_decisions(text: str) -> dict:
    """Decision counts for one document.

    `v15 if v15 else legacy` — never a sum. See the module docstring for why
    (the sentinels wrap the legacy prose; summing double-counts).
    """
    v15 = b3.parse_decisions(text)
    if v15:
        by_state: dict[str, int] = {}
        for d in v15:
            by_state[d.status or "active"] = by_state.get(d.status or "active", 0) + 1
        return {
            "total": len(v15),
            "format": "v15",
            "by_state": by_state,
            # A v15 doc can report a status breakdown because each block
            # declares one.
            "has_state_breakdown": True,
        }
    legacy = len(_LEGACY_DECISION_RE.findall(text))
    return {
        "total": legacy,
        "format": "legacy" if legacy else "none",
        "by_state": {},
        # Legacy prose carries no lifecycle marker. The absence of a breakdown
        # is a fact about the document, not a zero.
        "has_state_breakdown": False,
    }


def load_domains(repo_root: Path) -> list[dict]:
    """One summary dict per strategy document, in filename order.

    Deliberately does NOT render any document body. The index exists because
    the old single-route `/strategy` rendered every domain's full markdown,
    proposals, history and worktree diff on one page load; re-reading the
    bodies here would move that cost rather than remove it.
    """
    out: list[dict] = []
    for doc in b3.scan(repo_root):
        path = repo_root / doc.virtual_path
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            text = ""
        dec = _count_decisions(text)
        stub = doc.status == _STUB_STATUS
        out.append(
            {
                "slug": doc.slug,
                "title": doc.title,
                "domain": doc.domain,
                "path": doc.virtual_path,
                "status": doc.status,
                "stub": stub,
                "assembled_date": doc.assembled_date,
                "sources": list(doc.sources),
                "proposals": doc.proposal_count,
                "history": doc.history_count,
                "size_bytes": doc.size_bytes,
                "decisions": dec["total"],
                "decision_format": dec["format"],
                "decision_states": dec["by_state"],
                "has_state_breakdown": dec["has_state_breakdown"],
                "intent": "" if stub else _intent_line(text),
            }
        )
    return out


def load_rollup(repo_root: Path) -> dict:
    """Index-header roll-up.

    `live` counts documents the skill has not marked `awaiting-content` — i.e.
    docs with real content — rather than "docs that exist", because a
    scaffolded brief exists from the moment `/strategy init` runs and counting
    it as live would make the header read as progress that has not happened.
    """
    domains = load_domains(repo_root)
    live = [d for d in domains if not d["stub"]]
    states: dict[str, int] = {}
    for d in domains:
        for k, v in d["decision_states"].items():
            states[k] = states.get(k, 0) + v
    return {
        "total_domains": len(domains),
        "live": len(live),
        "stubs": len(domains) - len(live),
        "decisions": sum(d["decisions"] for d in domains),
        "proposals": sum(d["proposals"] for d in domains),
        "decision_states": states,
        # True when at least one doc still counts decisions the legacy way —
        # the index says so out loud rather than presenting mixed evidence
        # classes as one number.
        "mixed_formats": len({d["decision_format"] for d in live if d["decisions"]}) > 1,
        "domains": domains,
    }
