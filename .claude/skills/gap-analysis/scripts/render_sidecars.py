#!/usr/bin/env python3
"""Render structured JSON sidecars from gap-analysis markdown.

The `gap-analysis` skill authors human/agent-shared markdown under
`docs/_analysis/<component>/<id>.md`. This script DERIVES a machine-readable
JSON projection of each analysis so downstream consumers — primarily the
project-console Gap Analysis view — can render it natively without parsing
prose. The markdown remains the single source of truth; the JSON is a
regenerated derivative (never hand-edited).

Contract mirrors the `trace-matrix` sidecar / `drift.json` pattern: the
producer emits a stable JSON shape; the consumer knows nothing about how it
was produced and only reads the contract.

Outputs (under `docs/_analysis/`):
  - <component>/<id>.gap.json   — per-analysis detail
  - index.json                  — roll-up array of all analyses (lightweight)

Pure standard library — no third-party deps, so it runs anywhere the skill
is installed. The frontmatter is a controlled subset of YAML (scalars + the
typed lists this skill authors), parsed by a minimal reader rather than
requiring PyYAML.

Schema version is `SCHEMA_VERSION`; bump it (and the SKILL.md / README note)
when the JSON shape changes so consumers can guard.

Usage:
    python3 render_sidecars.py [--root <repo_root>] [--check] [--quiet]

    --root    Repo root (default: walk up from CWD to the dir holding project.yml)
    --check   Don't write; exit non-zero if any sidecar is missing or stale.
    --quiet   Only print the summary line.

Exit codes: 0 ok; 1 nothing found / IO error; 2 --check drift detected.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SCHEMA_VERSION = "1.0"

ANALYSIS_DIR = ("docs", "_analysis")


# --------------------------------------------------------------------------
# repo-root discovery
# --------------------------------------------------------------------------
def find_repo_root(start: Path) -> Path | None:
    cur = start.resolve()
    for cand in (cur, *cur.parents):
        if (cand / "project.yml").is_file():
            return cand
    return None


# --------------------------------------------------------------------------
# minimal frontmatter reader (controlled subset of YAML)
# --------------------------------------------------------------------------
def split_frontmatter(text: str) -> tuple[str, str]:
    """Return (frontmatter_text, body_text). Empty frontmatter if absent."""
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            fm = text[3:end].lstrip("\n")
            body = text[end + 4 :]
            return fm, body
    return "", text


def _strip_comment(val: str) -> str:
    # Drop a trailing ` # comment` but keep '#' inside quotes/paths (paths
    # here never contain '#'; clause refs use '§' not '#').
    if " #" in val:
        val = val.split(" #", 1)[0]
    return val.strip()


def parse_frontmatter(fm: str) -> dict:
    """Parse the controlled frontmatter shape this skill authors.

    Handles: scalar `key: value`; block lists where each item is either
    `- scalar` or `- typedkey: value  # note`. Good enough for the
    gap-analysis template; not a general YAML parser.
    """
    out: dict = {}
    cur_key: str | None = None
    for raw in fm.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip())
        line = raw.strip()
        if line.startswith("- ") and cur_key is not None and indent >= 2:
            item = line[2:].strip()
            out[cur_key].append(_parse_list_item(item))
            continue
        m = re.match(r"^([A-Za-z0-9_]+):\s*(.*)$", line)
        if m and indent == 0:
            key, val = m.group(1), m.group(2)
            val = _strip_comment(val)
            if val == "":
                out[key] = []          # opens a block list
                cur_key = key
            else:
                out[key] = _scalar(val)
                cur_key = None
    return out


def _scalar(v: str):
    v = v.strip().strip('"').strip("'")
    if v.lower() in ("null", "~", "none", ""):
        return None
    return v


def _parse_list_item(item: str):
    """A frontmatter list item: `human:name`, or `typedkey: path  # note`."""
    item = item.rstrip()
    # typed pointer:  `dhf: docs/...   # note`
    m = re.match(r"^([A-Za-z0-9_]+):\s+(.*)$", item)
    if m:
        ptype, rest = m.group(1), m.group(2)
        note = ""
        if " #" in rest:
            rest, note = rest.split(" #", 1)
        return {"type": ptype, "value": rest.strip(), "note": note.strip()}
    # `human:name` / `agent:name` authored-by style
    if ":" in item and " " not in item.split(":", 1)[0]:
        k, v = item.split(":", 1)
        return {"type": k.strip(), "value": v.strip(), "note": ""}
    return {"type": "", "value": _strip_comment(item), "note": ""}


# --------------------------------------------------------------------------
# body section extraction
# --------------------------------------------------------------------------
def sections(body: str) -> dict[str, str]:
    """Split body into {h2_title: text} on `## ` headers."""
    out: dict[str, str] = {}
    cur = None
    buf: list[str] = []
    for line in body.splitlines():
        m = re.match(r"^##\s+(.*)$", line)
        if m and not line.startswith("###"):
            if cur is not None:
                out[cur] = "\n".join(buf).strip()
            cur = m.group(1).strip()
            buf = []
        else:
            if cur is not None:
                buf.append(line)
    if cur is not None:
        out[cur] = "\n".join(buf).strip()
    return out


def parse_assertions(sec: str) -> list[dict]:
    """Parse the Assertions markdown table → list of rows."""
    rows = []
    for line in sec.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 5:
            continue
        if cells[0] in ("#", "") or set(cells[0]) <= {"-", ":"}:
            continue  # header / separator
        if not re.match(r"^A\d+$", cells[0]):
            continue
        status_raw = cells[4]
        rows.append(
            {
                "id": cells[0],
                "assertion": cells[1],
                "clause": cells[2],
                "evidence": cells[3],
                "status": _norm_status(status_raw),
                "status_label": re.sub(r"\*\*", "", status_raw).strip(),
            }
        )
    return rows


def _norm_status(raw: str) -> str:
    t = raw.lower()
    if "confirm" in t:
        return "confirmed"
    if "refut" in t:
        return "refuted"
    if "partial" in t:
        return "partial"
    if "verify" in t:
        return "verify"
    return "open"


_FINDING_RE = re.compile(r"^###\s+(F-\d+):\s*(.*)$")


def parse_findings(sec: str) -> list[dict]:
    """Findings: {id, label, author, body_md}. Body kept as markdown so the
    consumer renders it (robust against prose-shape variation)."""
    findings: list[dict] = []
    cur: dict | None = None
    buf: list[str] = []
    for line in sec.splitlines():
        m = _FINDING_RE.match(line)
        if m:
            if cur is not None:
                cur["body_md"] = "\n".join(buf).strip()
                findings.append(cur)
            cur = {"id": m.group(1), "label": m.group(2).strip(), "author": "", "body_md": ""}
            buf = []
        else:
            if cur is not None:
                buf.append(line)
                am = re.match(r"^\s*-\s*\*\*Author:\*\*\s*(.+)$", line)
                if am and not cur["author"]:
                    cur["author"] = am.group(1).strip()
    if cur is not None:
        cur["body_md"] = "\n".join(buf).strip()
        findings.append(cur)
    return findings


def parse_ordered_items(sec: str) -> list[str]:
    """Numbered or bulleted top-level items → list of strings (first line each)."""
    items: list[str] = []
    for line in sec.splitlines():
        m = re.match(r"^\s*(?:\d+\.|[-*])\s+(.*)$", line)
        if m and (len(line) - len(line.lstrip())) <= 1:
            txt = m.group(1).strip()
            if txt and not txt.startswith("~~"):  # skip struck-through resolved
                items.append(txt)
    return items


# --------------------------------------------------------------------------
# agent contribution derivation
# --------------------------------------------------------------------------
def derive_agents(fm: dict, findings: list[dict], changelog_sec: str) -> list[dict]:
    """Who advised, their role, and what they contributed.

    role from `recommended_agents` order (first = primary); contribution
    finding-ids from each finding's Author; changelog_summary from the matching
    `agent:<name>` changelog row.
    """
    rec = [r["value"] for r in fm.get("recommended_agents", []) if r.get("value")]
    roles = {name: ("primary" if i == 0 else "consulting") for i, name in enumerate(rec)}

    # finding ids per author
    contrib: dict[str, list[str]] = {}
    for f in findings:
        a = f.get("author", "")
        name = a.split(":", 1)[1].strip() if ":" in a else a.strip()
        if name:
            contrib.setdefault(name, []).append(f["id"])

    # changelog one-liners per agent
    summaries: dict[str, str] = {}
    for line in changelog_sec.splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) >= 3 and cells[1].startswith("agent:"):
            summaries[cells[1].split(":", 1)[1].strip()] = cells[2]

    # union of recommended + actual contributors
    names: list[str] = list(rec)
    for n in contrib:
        if n not in names:
            names.append(n)

    agents = []
    for n in names:
        agents.append(
            {
                "name": n,
                "role": roles.get(n, "contributor"),
                "ran": n in contrib or n in summaries,
                "contributed_finding_ids": contrib.get(n, []),
                "changelog_summary": summaries.get(n, ""),
            }
        )
    return agents


# --------------------------------------------------------------------------
# per-file build
# --------------------------------------------------------------------------
def build_analysis(md_path: Path, repo_root: Path) -> dict | None:
    text = md_path.read_text(encoding="utf-8")
    fm_text, body = split_frontmatter(text)
    fm = parse_frontmatter(fm_text)
    if not fm.get("id"):
        return None  # not a gap-analysis (e.g., a stray doc / README)

    secs = sections(body)

    def find_sec(*needles: str) -> str:
        for title, content in secs.items():
            low = title.lower()
            if all(n in low for n in needles):
                return content
        return ""

    grounding = [
        {"type": g.get("type", ""), "path": g.get("value", ""), "note": g.get("note", "")}
        for g in fm.get("grounded_against", [])
    ]
    assertions = parse_assertions(find_sec("assertion"))
    findings = parse_findings(find_sec("finding"))
    agents = derive_agents(fm, findings, find_sec("changelog"))

    status_counts: dict[str, int] = {}
    for a in assertions:
        status_counts[a["status"]] = status_counts.get(a["status"], 0) + 1

    rel = md_path.relative_to(repo_root).as_posix()
    return {
        "schema_version": SCHEMA_VERSION,
        "meta": {
            "id": fm.get("id"),
            "title": fm.get("title"),
            "status": fm.get("status"),
            "topic": fm.get("topic"),
            "component": fm.get("component"),
            "created": fm.get("created"),
            "last_updated": fm.get("last_updated"),
            "superseded_by": fm.get("superseded_by"),
            "source_md": rel,
            "source_doc_url": f"/documents#path={rel}",
        },
        "authored_by": [
            f'{a.get("type", "")}:{a.get("value", "")}'.strip(":")
            for a in fm.get("authored_by", [])
            if a.get("value")
        ],
        "grounding": grounding,
        "agents": agents,
        "assertions": assertions,
        "findings": findings,
        "recommendations": parse_ordered_items(find_sec("recommendation")),
        "open_questions": parse_ordered_items(find_sec("open question")),
        "stats": {
            "grounding_count": len(grounding),
            "agent_count": len([a for a in agents if a["ran"]]),
            "assertion_count": len(assertions),
            "assertion_status_counts": status_counts,
            "finding_count": len(findings),
        },
    }


def index_entry(detail: dict) -> dict:
    m = detail["meta"]
    return {
        "id": m["id"],
        "title": m["title"],
        "status": m["status"],
        "topic": m["topic"],
        "component": m["component"],
        "last_updated": m["last_updated"],
        "source_md": m["source_md"],
        "sidecar": str(Path(m["source_md"]).with_suffix(".gap.json").as_posix()),
        "agents": [a["name"] for a in detail["agents"] if a["ran"]],
        "stats": detail["stats"],
    }


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------
def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)

    root = Path(args.root).resolve() if args.root else find_repo_root(Path.cwd())
    if root is None:
        print("error: could not find repo root (no project.yml found)", file=sys.stderr)
        return 1

    analysis_root = root.joinpath(*ANALYSIS_DIR)
    if not analysis_root.is_dir():
        print(f"error: {analysis_root} does not exist", file=sys.stderr)
        return 1

    md_files = sorted(
        p for p in analysis_root.glob("*/*.md") if p.name.lower() != "readme.md"
    )

    details: list[dict] = []
    drift = False
    written = 0
    for md in md_files:
        detail = build_analysis(md, root)
        if detail is None:
            continue
        details.append(detail)
        out_path = md.with_suffix(".gap.json")
        new_text = json.dumps(detail, indent=2, ensure_ascii=False) + "\n"
        old_text = out_path.read_text(encoding="utf-8") if out_path.is_file() else ""
        if new_text != old_text:
            drift = True
            if not args.check:
                out_path.write_text(new_text, encoding="utf-8")
                written += 1
                if not args.quiet:
                    print(f"  wrote {out_path.relative_to(root)}")

    if not details:
        print("no gap-analysis files found under docs/_analysis/", file=sys.stderr)
        return 1

    index = {
        "schema_version": SCHEMA_VERSION,
        "analyses": [index_entry(d) for d in details],
        "counts": {
            "total": len(details),
            "by_status": _count_by(details, lambda d: d["meta"]["status"]),
            "by_topic": _count_by(details, lambda d: d["meta"]["topic"]),
            "by_component": _count_by(details, lambda d: d["meta"]["component"]),
        },
    }
    index_path = analysis_root / "index.json"
    new_index = json.dumps(index, indent=2, ensure_ascii=False) + "\n"
    old_index = index_path.read_text(encoding="utf-8") if index_path.is_file() else ""
    if new_index != old_index:
        drift = True
        if not args.check:
            index_path.write_text(new_index, encoding="utf-8")
            written += 1
            if not args.quiet:
                print(f"  wrote {index_path.relative_to(root)}")

    if args.check:
        status = "DRIFT" if drift else "up-to-date"
        print(f"gap-analysis sidecars: {len(details)} analyses — {status}")
        return 2 if drift else 0

    print(f"gap-analysis sidecars: {len(details)} analyses, {written} file(s) written")
    return 0


def _count_by(details: list[dict], key) -> dict:
    out: dict[str, int] = {}
    for d in details:
        k = key(d) or "—"
        out[k] = out.get(k, 0) + 1
    return out


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
