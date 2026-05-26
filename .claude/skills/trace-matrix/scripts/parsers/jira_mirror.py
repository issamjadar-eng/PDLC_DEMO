"""Shared `jira-mirror` adapter.

Parses the GFM tables emitted by the `jira-pull` skill under
`docs/project/_jira/<arch>/<version>/{epics,stories,hazards,tests}.md`.

Unlike the per-layer default parsers, a single adapter serves four layers
(design_inputs, software, vnv, risk) by auto-detecting the file shape from
the table headers. This lets a project wire item-DHF trace matrices
directly off Jira mirror data without per-layer customization.

Activated by setting `adapter: jira-mirror` on a layer in `trace-matrix.yml`.

Auto-detected shapes (header columns):

| Kind    | Required headers                                     | Maps to layer  |
|---------|------------------------------------------------------|----------------|
| epics   | `DI Prefix`, `Jira Key`, `Summary`                   | design_inputs  |
| stories | `Jira Key`, `Summary`, `Parent`/`Parent (DI)` col    | software       |
| hazards | `PHA Prefix` or `Hazard Prefix`, `Jira Key`          | risk           |
| tests   | `Jira Key`, `Summary`, `Verifies` col                | vnv            |

The adapter does not enforce that the configured `layer_key` matches the
auto-detected kind — it just emits nodes shaped for the detected file. The
build orchestrator places the nodes in whatever layer config invoked it.

ID resolution per kind (driven by `id_prefix` in layer_cfg):
- epics: use the `<id_prefix> Prefix` column when populated; rows where
  that cell is empty/dash are skipped (they are non-DI infrastructure
  epics, not design inputs).
- stories / tests: use the `Jira Key` column verbatim — `id_prefix` is
  expected to be the Jira project key (e.g. `PROJECT`) and is used only
  for the rational-check.
- hazards: use the `<id_prefix> Prefix` column when populated, else the
  Jira Key.

Cross-layer edges (stored in `traces_forward_ids` per the skill's
existing convention — "what this node references upstream"):
- stories → parent DI prefix (extracted from the Parent column)
- tests   → story Jira keys it verifies (extracted from Verifies cells)
- epics   → none (DIs are top of the item-DHF chain in this shape)
- hazards → none (overlay layer)

All cells that contain markdown links of the form `[KEY](URL)` are
flattened to `KEY` for trace-graph purposes; the original URL is captured
in `source_ref` so the project console can build browse-back links.
"""
from __future__ import annotations

import re
from pathlib import Path

from adapter_api import ParserResult
from parsers.markdown_table import parse_file


_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


def _flatten_link(cell: str) -> tuple[str, str | None]:
    """Return (text, url) for a `[text](url)` markdown link, or
    (cell, None) if no link is present. Trims whitespace.
    """
    cell = cell.strip()
    m = _LINK_RE.match(cell)
    if m:
        return m.group(1).strip(), m.group(2).strip()
    return cell, None


def _extract_keys(cell: str) -> list[str]:
    """Pull every Jira-key-shaped token out of a cell. Handles
    comma-separated `[KEY-1](url), [KEY-2](url)` and bare `KEY-1, KEY-2`.
    """
    if not cell:
        return []
    keys: list[str] = []
    for chunk in re.split(r"[,;]", cell):
        text, _ = _flatten_link(chunk)
        text = text.strip()
        if not text or text in {"—", "-", "–"}:
            continue
        m = re.match(r"^([A-Za-z][A-Za-z0-9]+[-\s]?\d+(?:\.\d+)*)$", text)
        if m:
            keys.append(text)
    return keys


def _norm_prefix_token(cell: str) -> str:
    """Normalize a prefix-column cell (e.g. `DI-0001`, `PHA 12`, `—`).
    Returns the canonical token, or empty string if the cell is a placeholder.
    """
    cell = cell.strip()
    if not cell or cell in {"—", "-", "–", "n/a", "N/A"}:
        return ""
    parts = cell.split()
    if len(parts) > 1 and parts[0].isalpha() and parts[1].lstrip("0").isdigit():
        return f"{parts[0]}-{parts[1]}"
    return cell


def _summarize(text: str, max_chars: int = 90) -> str:
    text = text.strip()
    if len(text) <= max_chars:
        return text
    cut = text[:max_chars].rsplit(" ", 1)[0]
    return cut + "…"


def _detect_kind(headers: list[str]) -> str | None:
    """Return one of {'epics', 'stories', 'hazards', 'tests'} or None."""
    hset = {h.strip() for h in headers}
    has_jira = "Jira Key" in hset
    if not has_jira:
        return None
    if any(h == "DI Prefix" for h in hset):
        return "epics"
    if any(h.startswith("PHA Prefix") or h == "Hazard Prefix" for h in hset):
        return "hazards"
    if any(h.startswith("Verifies") for h in hset):
        return "tests"
    if any(h.startswith("Parent") for h in hset):
        return "stories"
    return None


def _row_from_epic(row: dict, id_prefix: str) -> dict | None:
    prefix_col = f"{id_prefix} Prefix"
    raw_prefix = row.get(prefix_col, "") or row.get("DI Prefix", "")
    di_id = _norm_prefix_token(raw_prefix)
    if not di_id:
        return None  # non-DI infrastructure epic — not a design input
    jira_key, jira_url = _flatten_link(row.get("Jira Key", ""))
    summary = row.get("Summary", "").strip()
    return {
        "id": di_id,
        "summary": _summarize(summary),
        "full_text": summary,
        "category": None,
        "criticality": None,
        "group": None,
        "group_label": None,
        "source_ref": jira_url,
        "jira_key": jira_key or None,
        "status": row.get("Status", "").strip() or None,
        "labels": row.get("Labels", "").strip() or None,
        "traces_forward_ids": [],
    }


def _row_from_story(row: dict) -> dict:
    jira_key, jira_url = _flatten_link(row.get("Jira Key", ""))
    summary = row.get("Summary", "").strip()
    parent_col = next((k for k in row.keys() if k.startswith("Parent")), None)
    parent_text = row.get(parent_col, "") if parent_col else ""
    parent_ids: list[str] = []
    for tok in re.split(r"[,;]", parent_text):
        text, _ = _flatten_link(tok)
        norm = _norm_prefix_token(text)
        if norm:
            parent_ids.append(norm)
    return {
        "id": jira_key,
        "summary": _summarize(summary),
        "full_text": summary,
        "category": None,
        "criticality": None,
        "group": None,
        "group_label": None,
        "source_ref": jira_url,
        "status": row.get("Status", "").strip() or None,
        "labels": row.get("Labels", "").strip() or None,
        "traces_forward_ids": parent_ids,  # SW → DI (parent)
    }


def _row_from_hazard(row: dict, id_prefix: str) -> dict | None:
    prefix_col = next((k for k in row.keys() if k.endswith("Prefix")), None)
    raw_prefix = row.get(prefix_col, "") if prefix_col else ""
    norm = _norm_prefix_token(raw_prefix)
    jira_key, jira_url = _flatten_link(row.get("Jira Key", ""))
    hid = norm or jira_key
    if not hid:
        return None
    summary = row.get("Summary", "").strip()
    return {
        "id": hid,
        "summary": _summarize(summary),
        "full_text": summary,
        "category": None,
        "criticality": None,
        "group": None,
        "group_label": None,
        "source_ref": jira_url,
        "jira_key": jira_key or None,
        "status": row.get("Status", "").strip() or None,
        "traces_forward_ids": [],
    }


def _row_from_test(row: dict) -> dict:
    jira_key, jira_url = _flatten_link(row.get("Jira Key", ""))
    summary = row.get("Summary", "").strip()
    verifies_col = next((k for k in row.keys() if k.startswith("Verifies")), None)
    verifies_text = row.get(verifies_col, "") if verifies_col else ""
    story_keys = _extract_keys(verifies_text)
    return {
        "id": jira_key,
        "summary": _summarize(summary),
        "full_text": summary,
        "category": None,
        "criticality": None,
        "group": None,
        "group_label": None,
        "source_ref": jira_url,
        "status": row.get("Status", "").strip() or None,
        "verifies_story_ids": story_keys,
        "traces_forward_ids": story_keys,  # V&V → SW (verifies)
    }


def _load_richer_fields_from_json(md_path: Path) -> dict[str, dict]:
    """If a sibling `<basename>.json` exists alongside the markdown table
    (the rich JSON dump emitted by /jira-pull refresh), index it by Jira
    key and return only the fields the markdown table can't carry —
    today: `description`. Returns `{jira_key: {"description": str, ...}}`.

    The markdown table is intentionally narrow (4-6 columns) so it stays
    legible when committed and reviewed; the JSON sidecar is where richer
    per-issue metadata lives. The adapter merges them so the trace-matrix
    sidecar gets rich `full_text` + simple `summary` per item.
    """
    try:
        sibling = md_path.with_suffix(".json")
        if not sibling.is_file():
            return {}
        import json
        doc = json.loads(sibling.read_text(encoding="utf-8"))
        issues = doc.get("issues") if isinstance(doc, dict) else doc
        if not isinstance(issues, list):
            return {}
        idx: dict[str, dict] = {}
        for iss in issues:
            key = iss.get("key")
            if not key:
                continue
            payload = {}
            desc = iss.get("description")
            if isinstance(desc, str) and desc.strip():
                payload["description"] = desc.strip()
            # Lightweight ownership / scheduling fields. Each may or may not
            # be present in any given mirror generation; carried through only
            # when populated so the trace-matrix item dict stays sparse.
            #
            # User fields (`assignee`, `reporter`) may arrive as either a
            # string (display name) or a Jira user object — we project to
            # the human-readable name so the template stays simple. Same
            # for `resolution` (object → name).
            for k in ("assignee", "reporter"):
                v = iss.get(k)
                if isinstance(v, dict):
                    name = v.get("displayName") or v.get("name") or v.get("emailAddress")
                    if name:
                        payload[k] = name
                elif isinstance(v, str) and v.strip():
                    payload[k] = v.strip()
            res = iss.get("resolution")
            if isinstance(res, dict):
                rn = res.get("name") or res.get("id")
                if rn:
                    payload["resolution"] = rn
            elif isinstance(res, str) and res.strip():
                payload["resolution"] = res.strip()
            duedate = iss.get("duedate")
            if isinstance(duedate, str) and duedate.strip():
                payload["duedate"] = duedate.strip()
            if payload:
                idx[key] = payload
        return idx
    except Exception:
        return {}


def parse(path: Path, layer_cfg: dict) -> ParserResult:
    id_prefix = layer_cfg.get("id_prefix", "")
    if not path or not path.exists():
        return ParserResult(warnings=[f"source missing: {path}"])

    tables = parse_file(path)
    if not tables:
        return ParserResult(warnings=[f"no tables found in {path}"])

    rich = _load_richer_fields_from_json(path)

    nodes: list[dict] = []
    warnings: list[str] = []
    detected: str | None = None

    for table in tables:
        kind = _detect_kind(table.headers)
        if kind is None:
            continue
        detected = kind
        for row in table.rows:
            if kind == "epics":
                node = _row_from_epic(row, id_prefix or "DI")
            elif kind == "stories":
                node = _row_from_story(row)
            elif kind == "hazards":
                node = _row_from_hazard(row, id_prefix or "PHA")
            elif kind == "tests":
                node = _row_from_test(row)
            else:
                node = None
            if node is not None:
                # Merge richer fields keyed by Jira key. Description (when
                # present in the JSON sidecar) becomes `full_text`, leaving
                # the short summary intact for collapsed-row rendering.
                # Ownership / scheduling fields are passed through as-is
                # so the project-console template can surface them in the
                # row-expansion's "More metadata" disclosure.
                jkey = node.get("jira_key") or node.get("id")
                rich_fields = rich.get(jkey) or {}
                desc = rich_fields.get("description")
                if desc:
                    node["full_text"] = desc
                for k in ("assignee", "reporter", "resolution", "duedate"):
                    if rich_fields.get(k):
                        node[k] = rich_fields[k]
                nodes.append(node)

    if detected is None:
        warnings.append(
            f"jira-mirror adapter could not detect kind from headers in {path}"
        )

    return ParserResult(
        nodes=nodes,
        warnings=warnings,
        extras={"jira_mirror_kind": detected} if detected else {},
    )
