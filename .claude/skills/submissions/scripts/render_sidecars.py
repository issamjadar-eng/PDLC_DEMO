#!/usr/bin/env python3
"""Render project-console JSON sidecars for the submissions package.

The project-console **Submission** section is a generic consumer: it never
parses submission prose. This script (the producer) walks
`docs/project/submissions/` and emits the JSON contract the console reads:

    docs/project/submissions/.console/submission-index.json   — roll-up of filings
    docs/project/submissions/<filing>/<filing>.submission.json — per-filing detail

A "filing" is any immediate subfolder of `submissions/` that contains a
`composition-manifest.md` (today: qsub / 510k / pccp / pma). The manifest is the
authoritative package-assembly artifact; this script projects it — plus the
content docs and their `_provenance/*.provenance.yml` sidecars — into JSON.

Loose-coupling rule (same as the gap-analysis / trace-matrix sidecars): if the
sidecars don't exist, the console degrades to an empty state with a hint to run
`/submissions render`. The console knows nothing about how the JSON was
produced — only the `schema_version` shape below.

Usage:
    python3 render_sidecars.py [--root <repo_root>] [--check] [--quiet]

    --root    Repo root (default: walk up from CWD to the dir holding project.yml)
    --check   Exit non-zero if any sidecar is stale/missing (no writes). For CI.
    --quiet   Suppress per-file logging.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SCHEMA_VERSION = "1.0"
SUBMISSIONS_DIR = ("docs", "project", "submissions")
CONSOLE_DIR = ".console"
INDEX_NAME = "submission-index.json"

# Filename → (display title, kind) for content docs across all filing-type
# profiles (qsub / 510k / pccp / pma). Unknown files fall back to a title-cased
# filename and kind "doc". Stems are profile-agnostic: the same parser serves
# every filing; the filing-type profile only decides which stems get scaffolded.
DOC_META = {
    "composition-manifest": ("Composition Manifest", "manifest"),
    "cover-letter": ("Cover Letter", "cover-letter"),
    "device-description": ("Device Description", "device-description"),
    "intended-use": ("Proposed Indications for Use", "intended-use"),
    "fda-questions": ("Questions for FDA", "fda-questions"),
    "pccp-summary": ("PCCP Summary", "pccp-summary"),
    "pccp-plan": ("Predetermined Change Control Plan (PCCP)", "pccp-plan"),
    "cybersecurity-scope-brief": ("Cybersecurity Scope Brief", "brief"),
    "mdds-rationale": ("MDDS Rationale Brief", "brief"),
    "postop-administrative-boundary": ("Administrative-Boundary Brief", "brief"),
    "modification-protocol-ai-template": ("AI Modification Protocol Template", "template"),
    "modification-protocol-non-ai-template": ("Non-AI Modification Protocol Template", "template"),
    "separation-argument": ("Architectural Separation Argument", "brief"),
    "predicate-comparison": ("Predicate Comparison", "predicate"),
    "accessory-samd-brief": ("Accessory SaMD Brief", "brief"),
    # 510(k) profile
    "indications-for-use": ("Indications for Use (Form FDA 3881)", "intended-use"),
    "510k-summary": ("510(k) Summary", "summary"),
    "substantial-equivalence": ("Substantial Equivalence Discussion", "predicate"),
    "performance-testing": ("Performance Testing Summary", "performance"),
    "truthful-accuracy-statement": ("Truthful & Accuracy Statement", "statement"),
    # PMA profile (placeholder set)
    "ssed-summary": ("Summary of Safety & Effectiveness Data (SSED)", "summary"),
    "nonclinical-studies": ("Nonclinical Laboratory Studies", "doc"),
    "clinical-studies": ("Clinical Investigations", "doc"),
    "manufacturing-information": ("Manufacturing Information", "doc"),
    "labeling": ("Proposed Labeling", "doc"),
}

# Reading order for the documents tab — the FDA-facing core first, then the
# supporting briefs/templates. Unlisted stems sort after, alphabetically.
DOC_ORDER = [
    "cover-letter",
    "device-description",
    "intended-use",
    "indications-for-use",
    "510k-summary",
    "ssed-summary",
    "predicate-comparison",
    "substantial-equivalence",
    "performance-testing",
    "nonclinical-studies",
    "clinical-studies",
    "manufacturing-information",
    "labeling",
    "pccp-plan",
    "pccp-summary",
    "fda-questions",
    "truthful-accuracy-statement",
]

FILING_META = {
    "qsub": "Q-Sub (Pre-Submission)",
    "510k": "510(k)",
    "pccp": "PCCP",
    "pma": "PMA (Premarket Approval)",
}

# Scope-routing label emojis (see the internal-vs-external-scope-labels rule).
SCOPE_LABELS = {
    "📤": "external",
    "📝": "internal",
    "⏸️": "deferred",
    "⏸": "deferred",
    "📖": "reference",
}


# --------------------------------------------------------------------------- #
# small parsing helpers (stdlib only)
# --------------------------------------------------------------------------- #
def _read(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def _posix_norm(p: str) -> str:
    """Lexically normalize a posix path (resolve `.`/`..` without touching the
    filesystem)."""
    parts: list[str] = []
    for seg in p.split("/"):
        if seg in ("", "."):
            continue
        if seg == "..":
            if parts:
                parts.pop()
        else:
            parts.append(seg)
    return "/".join(parts)


def _demph(s: str) -> str:
    """Strip markdown bold/italic emphasis markers from a table-cell string so
    it renders as plain text in the console (cells are shown verbatim)."""
    return re.sub(r"\*{1,3}([^*]*)\*{1,3}", r"\1", s).replace("`", "").strip()


def _strip_md_link(cell: str) -> tuple[str, str]:
    """Return (text, href) for a markdown cell that may be `[text](href)` or
    `` `code` `` or plain. href is '' when none."""
    cell = cell.strip()
    m = re.search(r"\[([^\]]+)\]\(([^)]+)\)", cell)
    if m:
        return m.group(1).strip(" `"), m.group(2).strip()
    return cell.strip(" `"), ""


def _frontmatter(text: str) -> tuple[dict, str]:
    """Parse a leading YAML frontmatter block (--- ... ---). Returns (dict, body).
    Tolerant scalar-only parser; no external yaml dependency required."""
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    raw = text[3:end]
    body = text[end + 4:].lstrip("\n")
    fm: dict[str, str] = {}
    for line in raw.splitlines():
        m = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if m:
            fm[m.group(1).strip()] = m.group(2).strip().strip('"').strip("'")
    return fm, body


def _tables(section: str) -> list[dict]:
    """Extract every pipe-table in a markdown chunk. Each table →
    {headers: [...], rows: [{header_lower: value}, ...]}."""
    tables = []
    lines = section.splitlines()
    i = 0
    while i < len(lines):
        if lines[i].lstrip().startswith("|") and i + 1 < len(lines) and re.match(
            r"^\s*\|[\s:|-]+\|\s*$", lines[i + 1]
        ):
            headers = [c.strip() for c in lines[i].strip().strip("|").split("|")]
            rows = []
            j = i + 2
            while j < len(lines) and lines[j].lstrip().startswith("|"):
                cells = [c.strip() for c in lines[j].strip().strip("|").split("|")]
                row = {}
                for k, h in enumerate(headers):
                    row[h.lower()] = cells[k] if k < len(cells) else ""
                rows.append(row)
                j += 1
            tables.append({"headers": headers, "rows": rows})
            i = j
        else:
            i += 1
    return tables


def _split_sections(text: str, level: int = 2) -> list[tuple[str, str]]:
    """Split markdown into [(heading_text, body), ...] at the given ATX level."""
    marker = "#" * level + " "
    out: list[tuple[str, str]] = []
    cur_head, cur_body = None, []
    for line in text.splitlines():
        if line.startswith(marker) or (level == 2 and re.match(r"^##\s", line) and not line.startswith("###")):
            if cur_head is not None:
                out.append((cur_head, "\n".join(cur_body)))
            cur_head = line[len(marker):].strip() if line.startswith(marker) else line.lstrip("# ").strip()
            cur_body = []
        elif cur_head is not None:
            cur_body.append(line)
    if cur_head is not None:
        out.append((cur_head, "\n".join(cur_body)))
    return out


def _scope_of(heading: str) -> str:
    for emoji, label in SCOPE_LABELS.items():
        if emoji in heading:
            return label
    return ""


def _clean_heading(heading: str) -> str:
    for emoji in SCOPE_LABELS:
        heading = heading.replace(emoji, "")
    return heading.strip()


def _first_paragraph(body: str) -> str:
    for block in re.split(r"\n\s*\n", body):
        b = block.strip()
        if not b:
            continue
        # skip banners / headings / blockquotes / html / tables / frontmatter
        if b.startswith(("#", ">", "<!--", "<", "|", "---", "_Demo")):
            continue
        b = re.sub(r"\s+", " ", b)
        return (b[:280] + "…") if len(b) > 280 else b
    return ""


# --------------------------------------------------------------------------- #
# parsers
# --------------------------------------------------------------------------- #
def parse_manifest(path: Path) -> dict:
    """Project composition-manifest.md into structured pieces + identification."""
    text = _read(path)
    out: dict = {
        "type": None,
        "filing_id": None,
        "milestone": None,
        "dhfs": None,
        "pieces": {"required": [], "supporting": [], "strengtheners": [], "excluded": []},
        "sign_off": [],
    }
    sections = _split_sections(text, 2)
    for head, body in sections:
        h = head.lower()
        if "filing identification" in h:
            for tbl in _tables(body):
                for row in tbl["rows"]:
                    field = (row.get("field") or "").lower()
                    val, _ = _strip_md_link(row.get("value") or "")
                    if field == "filing type":
                        out["type"] = val
                    elif field == "filing id":
                        out["filing_id"] = val
                    elif field == "milestone":
                        out["milestone"] = val
                    elif "dhfs spanned" in field:
                        out["dhfs"] = val
        elif "included pieces" in h:
            _collect_pieces(body, out["pieces"])
        elif "excluded pieces" in h:
            for tbl in _tables(body):
                for row in tbl["rows"]:
                    name, _ = _strip_md_link(row.get("piece") or "")
                    reason = row.get("why excluded") or row.get("reason") or ""
                    if name:
                        out["pieces"]["excluded"].append({"name": name, "reason": reason})
        elif "reviewer sign-off" in h or "sign-off" in h:
            for tbl in _tables(body):
                for row in tbl["rows"]:
                    if "role" in row:
                        out["sign_off"].append(
                            {
                                "role": row.get("role", ""),
                                "name": (row.get("name", "") or "").strip("_ "),
                                "date": (row.get("date", "") or "").strip("—- "),
                                "status": (row.get("signature", "") or "").strip("_ "),
                            }
                        )
    return out


def _collect_pieces(body: str, pieces: dict) -> None:
    """Walk the 'Included Pieces' body — bucket each table by the bold/### lead
    that precedes it (required / strengtheners / supporting)."""
    bucket = "required"
    chunk_lines: list[str] = []

    def flush(into: str) -> None:
        if not chunk_lines:
            return
        for tbl in _tables("\n".join(chunk_lines)):
            for row in tbl["rows"]:
                name, _ = _strip_md_link(row.get("piece") or "")
                if not name:
                    continue
                _, href = _strip_md_link(
                    row.get("path") or row.get("piece") or ""
                )
                purpose = _demph(row.get("purpose in q-sub") or row.get("purpose") or "")
                status = _demph(row.get("status") or "")
                entry = {
                    "name": name,
                    "path": href,
                    "purpose": purpose,
                    "tracker_row": row.get("tracker row") or row.get("tracker") or "",
                }
                if into == "strengtheners":
                    sl = status.lower()
                    entry["status"] = status
                    entry["blocking"] = (
                        "transmission-blocking" in sl
                        and "not transmission-blocking" not in sl
                        and "not-transmission-blocking" not in sl
                    )
                pieces[into].append(entry)
        chunk_lines.clear()

    for line in body.splitlines():
        low = line.lower()
        if line.startswith("### "):
            flush(bucket)
            bucket = "supporting" if "supporting" in low else "required"
        elif line.startswith("**") and "strengthener" in low:
            flush(bucket)
            bucket = "strengtheners"
        elif line.startswith("**") and line.strip().endswith("**"):
            # a non-strengthener bold sub-lead inside Required (e.g. "Formal FDA
            # submission deliverables") — flush into the current bucket, keep it.
            flush(bucket)
            if bucket == "strengtheners":
                bucket = "required"
        chunk_lines.append(line)
    flush(bucket)


def parse_doc(path: Path, repo_root: Path) -> dict:
    """One content doc → metadata + filed-body section list + provenance summary."""
    stem = path.stem
    title, kind = DOC_META.get(stem, (stem.replace("-", " ").title(), "doc"))
    text = _read(path)
    fm, body = _frontmatter(text)

    summary = fm.get("summary") or _first_paragraph(body)
    version = fm.get("version") or ""
    status = fm.get("status") or ""

    sections = []
    for head, _ in _split_sections(body, 2):
        if not head or head.lower().startswith(("changelog", "ai change", "document control")):
            continue
        sections.append({"title": _clean_heading(head), "label": _scope_of(head)})

    prov = _provenance(path, repo_root)

    return {
        "id": stem,
        "title": title,
        "kind": kind,
        "path": path.relative_to(repo_root).as_posix(),
        "version": version,
        "status": status,
        "summary": summary,
        "sections": sections,
        "provenance": prov,
    }


def _provenance(doc_path: Path, repo_root: Path) -> dict | None:
    p = doc_path.parent / "_provenance" / f"{doc_path.stem}.provenance.yml"
    if not p.is_file():
        return None
    text = _read(p)
    fm, _ = _frontmatter("---\n" + text + "\n---\n") if not text.startswith("---") else _frontmatter(text)
    # Count list entries for two well-known keys without a full YAML parse.
    claims = len(re.findall(r"^\s*-\s+claim:", text, re.MULTILINE))
    gaps = len(re.findall(r"^\s*-\s+", text[text.find("open_gaps:"):])) if "open_gaps:" in text else 0
    return {
        "path": p.relative_to(repo_root).as_posix(),
        "agent": fm.get("agent", ""),
        "task": fm.get("task", ""),
        "version": fm.get("version", ""),
        "claims": claims,
        "open_gaps": gaps,
    }


def parse_questions(path: Path) -> list[dict]:
    """fda-questions.md → [{id, topic, subject, position, label}]. Parses
    `### Q<n>.<m>[:|—] subject` headings grouped under `## Topic ...` headings."""
    if not path.is_file():
        return []
    text = _read(path)
    _, body = _frontmatter(text)
    questions: list[dict] = []
    topic = ""
    cur: dict | None = None
    buf: list[str] = []

    def flush() -> None:
        if cur is not None:
            cur["position"] = _question_position("\n".join(buf))
            questions.append(cur)

    for line in body.splitlines():
        if line.startswith("## "):
            flush()
            cur, buf[:] = None, []
            topic = _clean_heading(line[3:].strip())
        elif re.match(r"^###\s+Q\d", line):
            flush()
            buf[:] = []
            head = line[4:].strip()
            qm = re.match(r"^(Q\d+(?:\.\d+)?)\s*[:—-]?\s*(.*)$", head)
            qid = qm.group(1) if qm else head
            subject = (qm.group(2).strip() if qm else "")
            cur = {
                "id": qid,
                "topic": topic,
                "subject": _clean_heading(subject),
                "label": _scope_of(head),
                "position": "",
            }
        elif cur is not None:
            buf.append(line)
    flush()
    return questions


def _question_position(body: str) -> str:
    # Prefer an explicit "Preliminary position" / "Position" line (the label may
    # be wrapped in ** and the colon may sit inside or outside the emphasis).
    m = re.search(
        r"(?im)^\s*\**\s*(?:preliminary\s+position|position)\s*\**\s*:?\s*\**\s*:?\s*(.+)$",
        body,
    )
    txt = m.group(1) if m else _first_paragraph(body)
    txt = re.sub(r"\s+", " ", _demph(txt)).strip()
    return (txt[:240] + "…") if len(txt) > 240 else txt


# --------------------------------------------------------------------------- #
# build
# --------------------------------------------------------------------------- #
def find_root(explicit: str | None) -> Path:
    if explicit:
        return Path(explicit).resolve()
    cur = Path.cwd().resolve()
    for cand in [cur, *cur.parents]:
        if (cand / "project.yml").is_file():
            return cand
    return cur


def build_filing(folder: Path, repo_root: Path) -> dict:
    fid = folder.name
    manifest_path = folder / "composition-manifest.md"
    man = parse_manifest(manifest_path)
    ftype = man["type"] or FILING_META.get(fid, fid)

    documents = []
    for md in sorted(folder.glob("*.md")):
        if md.name in ("composition-manifest.md", "README.md"):
            continue
        documents.append(parse_doc(md, repo_root))

    def _doc_sort_key(doc: dict):
        stem = doc["id"]
        rank = DOC_ORDER.index(stem) if stem in DOC_ORDER else len(DOC_ORDER)
        return (rank, doc["title"])

    documents.sort(key=_doc_sort_key)

    # Resolve manifest piece paths (authored relative to the filing folder, e.g.
    # `./cover-letter.md` or `../../dhfs/...`) to repo-relative so the console can
    # link them directly into the Documents viewer.
    filing_rel = folder.relative_to(repo_root).as_posix()
    for grp in ("required", "supporting", "strengtheners"):
        for piece in man["pieces"].get(grp, []):
            href = piece.get("path") or ""
            if href and not href.startswith(("http://", "https://", "/", "#")):
                piece["path"] = _posix_norm(f"{filing_rel}/{href}")

    questions = parse_questions(folder / "fda-questions.md")

    counts = {
        "required": len(man["pieces"]["required"]),
        "supporting": len(man["pieces"]["supporting"]),
        "strengtheners": len(man["pieces"]["strengtheners"]),
        "excluded": len(man["pieces"]["excluded"]),
        "docs": len(documents),
        "questions": len(questions),
    }
    blocking = sum(1 for s in man["pieces"]["strengtheners"] if s.get("blocking"))
    status = _filing_status(man, documents)

    detail = {
        "schema_version": SCHEMA_VERSION,
        "meta": {
            "id": fid,
            "type": ftype,
            "title": f"{ftype} — {_device_name(repo_root)}",
            "device": _device_name(repo_root),
            "filing_id": man["filing_id"],
            "milestone": man["milestone"],
            "dhfs": man["dhfs"],
            "status": status,
            "folder": folder.relative_to(repo_root).as_posix(),
            "manifest_md": manifest_path.relative_to(repo_root).as_posix(),
            "default_advisor": "regulatory-affairs",
        },
        "pieces": man["pieces"],
        "documents": documents,
        "questions": questions,
        "sign_off": man["sign_off"],
        "counts": counts,
        "blocking": blocking,
    }
    return detail


def _filing_status(man: dict, documents: list[dict]) -> str:
    statuses = [d.get("status", "").lower() for d in documents if d.get("status")]
    if any("draft" in s for s in statuses):
        return "drafting"
    if documents:
        return "drafting"
    return "scaffold"


_DEVICE_CACHE: dict[str, str] = {}


def _device_name(repo_root: Path) -> str:
    key = str(repo_root)
    if key in _DEVICE_CACHE:
        return _DEVICE_CACHE[key]
    name = ""
    pj = _read(repo_root / "project.yml")
    # Prefer a marketed/lead product name; fall back to the project name.
    for pat in (r"^\s*lead_product:\s*(.+)$", r"^\s*marketed_name:\s*(.+)$", r"^\s*name:\s*(.+)$"):
        m = re.search(pat, pj, re.MULTILINE)
        if m:
            name = m.group(1).strip().strip('"').strip("'")
            break
    _DEVICE_CACHE[key] = name or "this device"
    return _DEVICE_CACHE[key]


def render(repo_root: Path, check: bool, quiet: bool) -> int:
    sub_root = repo_root.joinpath(*SUBMISSIONS_DIR)
    if not sub_root.is_dir():
        if not quiet:
            print(f"[submissions] no {'/'.join(SUBMISSIONS_DIR)} dir — nothing to render")
        return 0

    filings = []
    for folder in sorted(p for p in sub_root.iterdir() if p.is_dir()):
        if not (folder / "composition-manifest.md").is_file():
            continue
        filings.append(build_filing(folder, repo_root))

    console_dir = sub_root / CONSOLE_DIR
    stale = False

    def emit(path: Path, payload: dict) -> None:
        nonlocal stale
        new = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
        old = _read(path) if path.is_file() else None
        if old != new:
            stale = True
            if not check:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(new, encoding="utf-8")
                if not quiet:
                    print(f"[submissions] wrote {path.relative_to(repo_root).as_posix()}")
            elif not quiet:
                print(f"[submissions] STALE {path.relative_to(repo_root).as_posix()}")

    for f in filings:
        fid = f["meta"]["id"]
        emit(sub_root / fid / f"{fid}.submission.json", f)

    index = {
        "schema_version": SCHEMA_VERSION,
        "filings": [
            {
                "id": f["meta"]["id"],
                "type": f["meta"]["type"],
                "title": f["meta"]["title"],
                "status": f["meta"]["status"],
                "folder": f["meta"]["folder"],
                "manifest": f["meta"]["manifest_md"],
                "counts": f["counts"],
                "blocking": f["blocking"],
                "default_advisor": f["meta"]["default_advisor"],
            }
            for f in filings
        ],
    }
    emit(console_dir / INDEX_NAME, index)

    if not filings and not quiet:
        print("[submissions] no filings with a composition-manifest.md found")
    if check and stale:
        return 1
    return 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)
    root = find_root(args.root)
    return render(root, args.check, args.quiet)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
