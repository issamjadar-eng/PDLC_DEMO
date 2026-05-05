"""
Raw-Jira → flat-mirror normalization + per-layer markdown rendering.

This module is the deterministic write side of `/jira-pull refresh`.

The MCP call (`mcp__atlassian__searchJiraIssuesUsingJql`) lives outside this
module — it must run inside Claude Code's tool loop. `actions/refresh.py`
in `--plan` mode emits the JQL/field tuples Claude needs to call MCP for;
Claude saves each raw response to a temp file; `--merge` mode then reads
those temp files and pipes them through this module.

Project-agnostic: the only project-specific values come in via the
caller-supplied prefix-extractor regexes (sourced from project.yml
`dhfs[].evidence.*.extractors`). Layer→issuetype defaults, mirror file
names, and column shapes are skill-side conventions.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional

# ─── Layer registry ──────────────────────────────────────────────────────
#
# Maps the project-agnostic layer key (used in mirror filenames and across
# CLI flags) to its Jira issuetype, the markdown heading prefix, and which
# id-prefix extractor (if any) decorates the markdown table.

LAYER_DEFAULTS: Dict[str, Dict[str, str]] = {
    "epics": {
        "issuetype": "Epic",
        "title": "Epics",
        "id_extractor": "design_input_id",
    },
    "stories": {
        "issuetype": "Story",
        "title": "Stories",
        "id_extractor": "",
    },
    "hazards": {
        "issuetype": "Hazard",
        "title": "Hazards",
        "id_extractor": "hazard_id",
    },
    "tests": {
        "issuetype": "Test Execution",
        "title": "Test Executions",
        "id_extractor": "",
    },
}

LAYER_FILES: Dict[str, str] = {
    "epics": "epics",
    "stories": "stories",
    "hazards": "hazards",
    "tests": "tests",
}


# ─── JQL composition ─────────────────────────────────────────────────────


def build_jql(
    project_key: str,
    fix_version: str,
    layer: str,
    story_filter: Optional[Dict[str, List[str]]] = None,
    *,
    cursor_after_key: Optional[str] = None,
) -> str:
    """Compose the JQL for one layer pull.

    **Always appends `ORDER BY key ASC`.** This turns the Jira issue key into
    a deterministic monotonic cursor — required because the wrapped Atlassian
    MCP search caps at 100 issues/page and does NOT expose `nextPageToken` in
    its response envelope. Without explicit ordering, Jira's default ordering
    is implementation-defined (usually `created` or relevance), so subsequent
    `key > <last>` filters cannot reliably page through the remaining issues.
    With `ORDER BY key ASC`, the last key on each page is the boundary; pass
    it back as `cursor_after_key` to fetch the next page.

    Quote-safe for fixVersion strings with spaces (e.g. 'Module Name
    v1.0.0'). The Story layer also applies the per-DHF `story_filter` clauses
    when set.
    """
    issuetype = LAYER_DEFAULTS[layer]["issuetype"]
    parts = [
        f'project = "{project_key}"',
        f'fixVersion = "{fix_version}"',
        f'issuetype = "{issuetype}"',
    ]
    if layer == "stories" and story_filter:
        labels = story_filter.get("labels") or []
        statuses = story_filter.get("statuses") or []
        if labels:
            parts.append("labels in (" + ", ".join(_quote(l) for l in labels) + ")")
        if statuses:
            parts.append("status in (" + ", ".join(_quote(s) for s in statuses) + ")")
    if cursor_after_key:
        parts.append(f'key > "{cursor_after_key}"')
    return " AND ".join(parts) + " ORDER BY key ASC"


def _quote(v: str) -> str:
    """JQL-quote a string value. JQL accepts double-quoted strings; escape
    embedded quotes the simple way."""
    return '"' + v.replace('"', '\\"') + '"'


# ─── Raw → flat issue ────────────────────────────────────────────────────
#
# MCP `searchJiraIssuesUsingJql` returns issues as a list under `.issues[]`,
# each with `key`, `fields{}`. We flatten the fields the skill cares about
# into a stable, alphabetically-sortable dict so downstream consumers
# (jira_client.load_state, drift_rules) get a uniform shape regardless of
# how Jira's API evolves.


def _name_of(obj: Any) -> str:
    """Pull a `name` (or `displayName`, or string) out of a Jira sub-object."""
    if obj is None:
        return ""
    if isinstance(obj, str):
        return obj
    if isinstance(obj, dict):
        return obj.get("displayName") or obj.get("name") or obj.get("value") or ""
    return str(obj)


def _names(seq: Any) -> List[str]:
    if not seq:
        return []
    return [_name_of(x) for x in seq if x is not None]


def normalize_issue(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Flatten a single raw Jira issue into the mirror's stable shape.

    Tolerates two response shapes:
      - MCP envelope: `{key, fields: {summary, status: {name}, ...}}`
      - REST GET: same shape
    Also tolerates already-flat dicts (idempotent on already-normalized
    issues — useful for tests).
    """
    if "fields" not in raw:
        # Already flat (e.g. already-normalized issue from a prior refresh).
        # Pass through unchanged so the operation is idempotent.
        return dict(raw)

    f = raw["fields"]

    parent = f.get("parent") or {}
    parent_key = parent.get("key") or ""
    parent_summary = ((parent.get("fields") or {}).get("summary")) or parent.get(
        "summary"
    ) or ""

    issuelinks_raw = f.get("issuelinks") or []
    issuelinks: List[Dict[str, str]] = []
    for il in issuelinks_raw:
        link_type = (il.get("type") or {}).get("name") or ""
        if il.get("outwardIssue"):
            other = il["outwardIssue"]
            direction = "outward"
            inward_outward = (il.get("type") or {}).get("outward") or ""
        elif il.get("inwardIssue"):
            other = il["inwardIssue"]
            direction = "inward"
            inward_outward = (il.get("type") or {}).get("inward") or ""
        else:
            continue
        issuelinks.append(
            {
                "type": link_type,
                "direction": direction,
                "relation": inward_outward,
                "key": other.get("key") or "",
                "summary": (other.get("fields") or {}).get("summary") or "",
            }
        )

    flat: Dict[str, Any] = {
        "key": raw.get("key") or "",
        "summary": f.get("summary") or "",
        "description": _description_to_plain(f.get("description")),
        "status": _name_of(f.get("status")),
        "priority": _name_of(f.get("priority")),
        "issuetype": _name_of(f.get("issuetype")),
        "labels": list(f.get("labels") or []),
        "components": _names(f.get("components")),
        "fix_versions": _names(f.get("fixVersions")),
        "parent_key": parent_key,
        "parent_summary": parent_summary,
        "issuelinks": issuelinks,
        "assignee": _name_of(f.get("assignee")),
        "reporter": _name_of(f.get("reporter")),
        "resolution": _name_of(f.get("resolution")),
        "duedate": f.get("duedate") or "",
        "created": f.get("created") or "",
        "updated": f.get("updated") or "",
    }
    return flat


def _description_to_plain(desc: Any) -> str:
    """Jira descriptions can come back as a string (when REST `?expand=renderedFields`),
    a wiki-markup string, or as an Atlassian Document Format (ADF) JSON tree
    (default for cloud). Best-effort extraction: pull text leaves out of ADF;
    leave strings alone; return empty for None.

    The mirror stores plain text — keeps diffs human-readable and lets the
    project-console drawer render it via white-space:pre-wrap. Rich formatting
    is intentionally lost; reviewers can chase the Jira browse-link if they
    need fidelity.
    """
    if desc is None:
        return ""
    if isinstance(desc, str):
        return desc
    if isinstance(desc, dict):
        # ADF tree — walk content[].
        out: List[str] = []
        _walk_adf(desc, out)
        return "\n\n".join(s for s in (chunk.strip() for chunk in out) if s)
    return str(desc)


def _walk_adf(node: Any, out: List[str]) -> None:
    if not isinstance(node, dict):
        return
    t = node.get("type")
    if t == "text":
        out.append(node.get("text") or "")
        return
    if t == "hardBreak":
        out.append("\n")
        return
    children = node.get("content") or []
    if t == "paragraph":
        # Buffer paragraph children into one chunk.
        buf: List[str] = []
        for c in children:
            _walk_adf(c, buf)
        out.append("".join(buf))
        return
    if t in ("bulletList", "orderedList"):
        for li in children:
            _walk_adf(li, out)
        return
    if t == "listItem":
        buf = []
        for c in children:
            _walk_adf(c, buf)
        out.append("• " + " ".join(s.strip() for s in buf if s.strip()))
        return
    if t in ("heading", "blockquote", "codeBlock"):
        buf = []
        for c in children:
            _walk_adf(c, buf)
        out.append("".join(buf))
        return
    # Unknown node — recurse into content if any.
    for c in children:
        _walk_adf(c, out)


# ─── Markdown rendering ──────────────────────────────────────────────────


def render_layer_md(
    layer: str,
    issues: List[Dict[str, Any]],
    *,
    fix_version: str,
    fix_version_id: str,
    pulled_at: str,
    base_url: str,
    extractors: Dict[str, str],
    arch_marketed_name: str,
) -> str:
    """Render a layer's GFM table. Columns mirror the SKILL.md design contract.

    Project-agnostic: the prefix-extractor regex (e.g. `^(DI-\\d+)`) comes
    from `project.yml` `dhfs[].evidence.*.extractors`. If no extractor is
    declared for the layer, the prefix column is omitted.
    """
    title = LAYER_DEFAULTS[layer]["title"]
    extractor_key = LAYER_DEFAULTS[layer]["id_extractor"]
    extractor_re = extractors.get(extractor_key) if extractor_key else None

    lines: List[str] = []
    lines.append(f"# {title} — {arch_marketed_name}")
    lines.append("")
    lines.append("_Auto-generated by `/jira-pull refresh`. Do not edit by hand._")
    lines.append("")
    lines.append(f"**Issue count:** {len(issues)}  ")
    lines.append(f"**Pulled at:** `{pulled_at}`  ")
    lines.append(f"**Fix version:** `{fix_version}` (id: `{fix_version_id}`)")
    lines.append("")

    if layer == "epics":
        header = (
            ["DI Prefix"] if extractor_re else []
        ) + ["Jira Key", "Summary", "Status", "Story Count", "Labels"]
        lines.append("| " + " | ".join(header) + " |")
        lines.append("|" + "|".join("---" for _ in header) + "|")
        # Story count is unknown without a second-pass cross-layer scan; for
        # now we emit the issuelinks count (parent edges captured via
        # parent_key are not in issuelinks). Refresh.py can do the cross-pass
        # later; keeping a stable column shape today.
        for it in sorted(issues, key=lambda x: x["key"]):
            row = []
            if extractor_re:
                row.append(_extract_prefix(it["summary"], extractor_re))
            row.extend([
                f'[{it["key"]}]({base_url}/browse/{it["key"]})',
                _md_escape(it["summary"]),
                it["status"],
                str(it.get("story_count", len(it.get("issuelinks") or []))),
                ", ".join(it.get("labels") or []),
            ])
            lines.append("| " + " | ".join(row) + " |")
    elif layer == "stories":
        header = ["Jira Key", "Summary", "Parent Epic", "Status", "Labels"]
        lines.append("| " + " | ".join(header) + " |")
        lines.append("|" + "|".join("---" for _ in header) + "|")
        for it in sorted(issues, key=lambda x: x["key"]):
            parent_label = it.get("parent_key") or ""
            if parent_label:
                parent_label = f'[{parent_label}]({base_url}/browse/{parent_label})'
            lines.append(
                "| "
                + " | ".join(
                    [
                        f'[{it["key"]}]({base_url}/browse/{it["key"]})',
                        _md_escape(it["summary"]),
                        parent_label,
                        it["status"],
                        ", ".join(it.get("labels") or []),
                    ]
                )
                + " |"
            )
    elif layer == "hazards":
        header = (
            ["PHA Prefix"] if extractor_re else []
        ) + ["Jira Key", "Summary", "Status", "Issuelink Count"]
        lines.append("| " + " | ".join(header) + " |")
        lines.append("|" + "|".join("---" for _ in header) + "|")
        for it in sorted(issues, key=lambda x: x["key"]):
            row = []
            if extractor_re:
                row.append(_extract_prefix(it["summary"], extractor_re))
            row.extend(
                [
                    f'[{it["key"]}]({base_url}/browse/{it["key"]})',
                    _md_escape(it["summary"]),
                    it["status"],
                    str(len(it.get("issuelinks") or [])),
                ]
            )
            lines.append("| " + " | ".join(row) + " |")
    elif layer == "tests":
        header = ["Jira Key", "Summary", "Verifies (Story)", "Status"]
        lines.append("| " + " | ".join(header) + " |")
        lines.append("|" + "|".join("---" for _ in header) + "|")
        for it in sorted(issues, key=lambda x: x["key"]):
            verifies = ""
            for il in it.get("issuelinks") or []:
                if (il.get("relation") or "").lower() in ("relates to", "tests", "verifies"):
                    verifies = il.get("key") or ""
                    break
            verifies_label = (
                f'[{verifies}]({base_url}/browse/{verifies})' if verifies else ""
            )
            lines.append(
                "| "
                + " | ".join(
                    [
                        f'[{it["key"]}]({base_url}/browse/{it["key"]})',
                        _md_escape(it["summary"]),
                        verifies_label,
                        it["status"],
                    ]
                )
                + " |"
            )
    else:
        raise ValueError(f"unknown layer: {layer!r}")

    lines.append("")
    return "\n".join(lines)


def _extract_prefix(summary: str, regex: str) -> str:
    """Apply the project's prefix regex; return the captured group or empty."""
    if not summary or not regex:
        return ""
    m = re.search(regex, summary)
    if not m:
        return ""
    return m.group(1) if m.groups() else m.group(0)


def _md_escape(s: str) -> str:
    """Just enough escaping to keep table cells safe — pipe + newline."""
    if not s:
        return ""
    return s.replace("|", "\\|").replace("\r", " ").replace("\n", " ")


# ─── _meta block builder ─────────────────────────────────────────────────


def build_meta(
    *,
    cloud_id: str,
    fix_version: str,
    fix_version_id: str,
    issuetype: str,
    jql: str,
    issue_count: int,
    field_set: List[str],
    enriched_with: Optional[List[str]] = None,
    schema_version: str = "1.1",
) -> Dict[str, Any]:
    """Build the `_meta` block written to the top of every `<layer>.json`.
    `enriched_with` records which optional fields were merged in this pull
    (e.g. `["description","assignee","reporter","resolution","duedate"]`).
    `schema_version` bumps when the on-disk shape changes meaningfully."""
    return {
        "cloud_id": cloud_id,
        "fix_version": fix_version,
        "fix_version_id": str(fix_version_id),
        "issue_count": int(issue_count),
        "issuetype": issuetype,
        "jql": jql,
        "pulled_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "schema_version": schema_version,
        "field_set": list(field_set),
        "enriched_with": list(enriched_with or []),
    }


# ─── Public re-exports ───────────────────────────────────────────────────

__all__ = [
    "LAYER_DEFAULTS",
    "LAYER_FILES",
    "build_jql",
    "build_meta",
    "normalize_issue",
    "render_layer_md",
]
