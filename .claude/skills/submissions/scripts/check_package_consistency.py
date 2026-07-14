#!/usr/bin/env python3
"""check_package_consistency — cross-document "seam" checks for a submission package.

Per-document tooling (the leak/repo-path scrub, the authoring lint, qsub_scope_lint)
validates each document in isolation. A whole class of defect survives that scrutiny
because it does not live *in* any single document — it lives in the SEAM between two
documents, where a pointer in one document describes, numbers, or reaches for another.
Each side is internally clean; only the pair is wrong. See the companion note
`references/pre-sub-package-consistency.md` for the principle and the tiering model.

This checker is project-agnostic: it reads the transmitted set and the numbered contents
list(s) from the package's own cover letter — nothing is hard-coded. Three checks:

  S1  cross-reference accuracy (WARN) — a filed-body pointer that DESCRIBES a linked
        package doc as the "full / complete / comprehensive" predicate/SE analysis while
        the linked target's own opening self-describes as an ABBREVIATED / summary
        treatment (tier confusion). Deferral sentences ("the full analysis is a 510(k)
        deliverable") are exempt — they name the deferred artifact, not the attachment.
  S2  attachment-number consistency (FAIL) — a prose "attachment N" reference whose
        number matches NONE of the package's numbered contents/attachment lists for the
        doc it links; plus internal contiguity of each numbered list (gaps / duplicates).
        When two numbered lists number the same doc differently (e.g. one counts the
        cover letter as #1 and the other does not), prose "attachment N" is ambiguous —
        surfaced as WARN so the team unifies or documents the convention.
  S3  folder-boundary compliance (FAIL/WARN) — a TRANSMITTED attachment whose path
        escapes the filing folder (`../`) with no on-request / internal / grounding-only
        disposition on its line (FAIL); a filed-body `../../` link reaching outside the
        filing folder (WARN — should be grounding-only; confirm it implies no attachment).

Usage:
  python3 check_package_consistency.py <filing-dir> [--cover cover-letter.md]
                                       [--transmit-gate] [--json]
Exit: 0 clean; 1 WARN present (advisory); 2 FAIL present under --transmit-gate.
"""
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path

# Reuse the path-aware doc identity + tag-based internal-zone stripper from the sibling
# scope linter so both checkers agree on doc identity and on what counts as "filed body".
sys.path.insert(0, str(Path(__file__).resolve().parent))
from qsub_scope_lint import docid, strip_zones  # noqa: E402

MD_LINK = re.compile(r"\[([^\]]*)\]\(([^)]+\.md[^)]*)\)")
# Disposition markers that make an out-of-folder / non-transmitted pointer legitimate.
DISPOSITION = re.compile(
    r"provided on (fda )?request|on request|internal(?:\b|,| —| -| grounding)"
    r"|not transmitted|not a q-?sub attachment|grounding[- ]only|510\(k\) deliverable"
    r"|not included in this pre-?submission",
    re.I,
)
# Over-claim adjectives that assert a document is the *full* treatment.
OVERCLAIM = re.compile(r"\b(full|complete|comprehensive|entire|whole)\b", re.I)
# Nouns the over-claim adjective must be modifying for S1 to fire (predicate/SE context).
SE_NOUN = re.compile(
    r"\b(analysis|justification|comparison|mapping|argument|assessment|evaluation)\b", re.I
)
SE_CONTEXT = re.compile(r"predicat|substantial[- ]equiv|\bSE\b", re.I)
# A target doc self-describes as an abbreviated / summary treatment.
SUMMARY_SELF = re.compile(
    r"\babbreviated\b|\bsummary\b|\bhighlights\b|not the full|full .{0,40}\b(is|are)\b "
    r".{0,30}510\(k\)|full .{0,40}accompan\w+ .{0,20}510\(k\)",
    re.I,
)
FULL_SELF = re.compile(
    r"full (substantial[- ]equivalence|predicate|se) (analysis|argument)"
    r"|per-attribute (comparison|mapping)|complete substantial[- ]equivalence",
    re.I,
)


def link_stem(raw: str) -> str:
    """docid() of a markdown link target, stripping any #anchor."""
    return docid(raw.split("#", 1)[0])


# ── target self-tier (summary vs full) ─────────────────────────────────────────
def classify_self_tier(md_path: Path) -> str | None:
    """Read a package doc's filed body opening and classify its self-declared depth:
    'summary' | 'full' | None (unknown). Title + first ~60 filed lines only."""
    if not md_path.exists():
        return None
    text = md_path.read_text(encoding="utf-8")
    title = ""
    for ln in text.split("\n"):
        if ln.startswith("# "):
            title = ln
            break
    filed = strip_zones(text)[0]
    head = "\n".join(row.split("\t", 1)[1] for row in filed.split("\n")
                      if "\t" in row)[:4000]
    hay = title + "\n" + head
    if SUMMARY_SELF.search(title) or re.search(r"\bsummary\b|\babbreviated\b", title, re.I):
        return "summary"
    if SUMMARY_SELF.search(head):
        return "summary"
    if FULL_SELF.search(hay):
        return "full"
    return None


# A contrastive self-label on the same line ("abbreviated X … full Y later") means the
# over-claim adjective modifies the DEFERRED artifact, not the linked attachment.
CONTRASTIVE = re.compile(r"\babbreviated\b|\bsummary\b|\bhighlights\b|gates?\s+.{0,30}pending"
                         r"|pending (fda )?feedback", re.I)


# ── S1 cross-reference accuracy ────────────────────────────────────────────────
def check_cross_reference(tier: dict[str, str | None], docs: dict[str, Path]) -> list[dict]:
    findings = []
    for md in sorted(docs.values()):
        filed = strip_zones(md.read_text(encoding="utf-8"))[0]
        for row in filed.split("\n"):
            if "\t" not in row:
                continue
            n, text = row.split("\t", 1)
            if not SE_CONTEXT.search(text):
                continue
            om = OVERCLAIM.search(text)
            if not om or not SE_NOUN.search(text[om.start():om.start() + 60]):
                continue
            if DISPOSITION.search(text) or CONTRASTIVE.search(text):
                continue  # deferral / on-request / contrastive sentence names the deferred artifact
            for _, raw in MD_LINK.findall(text):
                stem = link_stem(raw)
                if tier.get(stem) == "summary":
                    findings.append({
                        "check": "S1", "sev": "WARN", "file": md.name, "line": int(n),
                        "msg": f"pointer calls '{stem}' the "
                               f"'{om.group(1).lower()}' predicate/SE treatment, but that "
                               f"target self-describes as an abbreviated/summary document "
                               f"— name the correct tier (summary vs. the full 510(k) analysis)"})
    return findings


# ── numbered contents / attachment lists ───────────────────────────────────────
TABLE_ROW = re.compile(r"^\|\s*(\d+)\s*\|.*?\(([^)]+\.md[^)]*)\)")
ORDERED_ITEM = re.compile(r"^\s*(\d+)\.\s+.*?\(([^)]+\.md[^)]*)\)")
LIST_HEADER = re.compile(r"attachment|package contents|enclosure|submission package", re.I)


def parse_numbered_lists(cover: str) -> list[dict]:
    """Return numbered entries {num, stem, path, line, kind}. `kind` is 'table' for
    `| N | … (path) |` rows and 'ordered' for `N. [title](path)` items appearing under a
    heading whose text matches attachment/contents/enclosure."""
    out, in_att_section = [], False
    for i, ln in enumerate(cover.split("\n"), 1):
        if ln.startswith("#"):
            in_att_section = bool(LIST_HEADER.search(ln))
            continue
        m = TABLE_ROW.match(ln)
        if m:
            out.append({"num": int(m.group(1)), "stem": link_stem(m.group(2)),
                        "path": m.group(2), "line": i, "kind": "table"})
            continue
        m = ORDERED_ITEM.match(ln)
        if m and in_att_section:
            out.append({"num": int(m.group(1)), "stem": link_stem(m.group(2)),
                        "path": m.group(2), "line": i, "kind": "ordered"})
    return out


PROSE_ATTACH = re.compile(r"attachments?\s+(\d+)(?:\s+and\s+(\d+))?", re.I)


def check_attachment_numbers(cover_text: str, entries: list[dict]) -> list[dict]:
    findings = []
    # (a) internal contiguity per list-kind
    for kind in ("table", "ordered"):
        nums = [e["num"] for e in entries if e["kind"] == kind]
        if not nums:
            continue
        seen, dupes = set(), set()
        for n in nums:
            (dupes if n in seen else seen).add(n)
        if dupes:
            findings.append({"check": "S2", "sev": "FAIL", "file": "cover-letter", "line": 0,
                             "msg": f"numbered {kind} list has duplicate number(s) {sorted(dupes)}"})
        expected = set(range(min(nums), max(nums) + 1))
        gaps = expected - set(nums)
        if gaps:
            findings.append({"check": "S2", "sev": "FAIL", "file": "cover-letter", "line": 0,
                             "msg": f"numbered {kind} list is non-contiguous — missing {sorted(gaps)}"})
    # (b) cross-list numbering disagreement for the same doc (ambiguity → WARN).
    # A UNIFORM offset across every shared doc is a single accepted convention (one list
    # counts the cover letter as #1, the other starts at the first enclosure) — collapse
    # to one WARN. A NON-uniform offset is real numbering drift — list each mismatch.
    by_stem: dict[str, dict[str, int]] = {}
    for e in entries:
        by_stem.setdefault(e["stem"], {})[e["kind"]] = e["num"]
    shared = {s: k for s, k in by_stem.items()
              if "table" in k and "ordered" in k and k["table"] != k["ordered"]}
    if shared:
        offsets = {s: k["table"] - k["ordered"] for s, k in shared.items()}
        if len(set(offsets.values())) == 1:
            off = next(iter(offsets.values()))
            findings.append({"check": "S2", "sev": "WARN", "file": "cover-letter", "line": 0,
                             "msg": f"the contents table and the attachments list are offset by a "
                                    f"uniform {off:+d} across all {len(shared)} shared docs (one list "
                                    f"counts the cover letter, the other starts at the first enclosure) "
                                    f"— prose 'attachment N' must reference ONE list; confirm which is "
                                    f"canonical for prose or unify the numbering"})
        else:
            for s, k in sorted(shared.items()):
                desc = ", ".join(f"{kind}={n}" for kind, n in sorted(k.items()))
                findings.append({"check": "S2", "sev": "WARN", "file": "cover-letter", "line": 0,
                                 "msg": f"two numbered lists number '{s}' differently ({desc}) with a "
                                        f"non-uniform offset — likely a numbering drift; reconcile"})
    # (c) prose "attachment N" (+ same-line doc link) must match some list's number for that doc
    stem_nums: dict[str, set[int]] = {}
    for e in entries:
        stem_nums.setdefault(e["stem"], set()).add(e["num"])
    for i, ln in enumerate(cover_text.split("\n"), 1):
        pm = PROSE_ATTACH.search(ln)
        if not pm:
            continue
        prose_nums = {int(g) for g in pm.groups() if g}
        links = [link_stem(raw) for _, raw in MD_LINK.findall(ln)]
        for stem in links:
            valid = stem_nums.get(stem)
            if valid and not (prose_nums & valid):
                findings.append({"check": "S2", "sev": "FAIL", "file": "cover-letter", "line": i,
                                 "msg": f"prose says attachment {sorted(prose_nums)} for '{stem}', "
                                        f"but the numbered list(s) place it at {sorted(valid)}"})
    return findings


# ── S3 folder-boundary compliance ──────────────────────────────────────────────
def escapes_folder(path: str, filing: Path) -> bool:
    """True if a package-relative link target resolves OUTSIDE the filing folder."""
    if path.startswith(("http://", "https://", "#")):
        return False
    resolved = (filing / path.split("#", 1)[0]).resolve()
    try:
        resolved.relative_to(filing.resolve())
        return False
    except ValueError:
        return True


def check_folder_boundary(filing: Path, cover_text: str, entries: list[dict],
                          docs: dict[str, Path]) -> list[dict]:
    findings = []
    cover_lines = cover_text.split("\n")
    # (a) transmitted attachment whose path escapes the filing folder w/o a disposition
    for e in entries:
        if not escapes_folder(e["path"], filing):
            continue
        line_txt = cover_lines[e["line"] - 1] if 0 < e["line"] <= len(cover_lines) else ""
        if DISPOSITION.search(line_txt):
            continue  # sanctioned out-of-folder pointer (on request / internal / grounding)
        findings.append({"check": "S3", "sev": "FAIL", "file": "cover-letter", "line": e["line"],
                         "msg": f"transmitted attachment '{e['stem']}' is sourced from OUTSIDE the "
                                f"filing folder ({e['path']}) with no on-request/internal/grounding "
                                f"disposition — bring a right-sized copy into the package or mark it "
                                f"provided-on-request"})
    # (b) filed-body ../ links reaching outside the filing folder (WARN)
    for md in sorted(docs.values()):
        filed = strip_zones(md.read_text(encoding="utf-8"))[0]
        for row in filed.split("\n"):
            if "\t" not in row:
                continue
            n, text = row.split("\t", 1)
            if DISPOSITION.search(text):
                continue
            for _, raw in MD_LINK.findall(text):
                if escapes_folder(raw, filing):
                    findings.append({"check": "S3", "sev": "WARN", "file": md.name, "line": int(n),
                                     "msg": f"filed-body link reaches outside the filing folder "
                                            f"({raw}) — reserve out-of-folder pointers for "
                                            f"grounding-only/on-request material and mark them so"})
                    break
    return findings


# ── S4 stable-key liveness: an anchor/support claim must name a LIVE question ───
# Root cause of recurring drift: a "spine" fact (a question's number or transmit
# status) changes in its home doc, and sibling docs that DECLARE they anchor/support
# it are not updated in lockstep. This catches a declaration that names a stable key
# (QK-*) which the questions doc has since deferred or dropped — the semantic seam a
# structural check (numbering/folder/tier) cannot see.
ANCHOR_VERB = re.compile(r"\b(anchor|anchors|anchored|anchoring|support|supports|supported|supporting)\b", re.I)
QK_REF = re.compile(r"QK-[A-Z0-9]+(?:-[A-Z0-9]+)*")
# Row of the fda-questions master map: `| QK-X | **Q1.2** or DQ-14 | topic | ✅/⏸️ … |`.
QK_ROW = re.compile(r"^\|\s*(QK-[A-Z0-9-]+)\s*\|\s*\*{0,2}\s*(Q\d+\.\d+|DQ-\d+)\s*\*{0,2}\s*\|[^|]*\|\s*(✅|⏸️)")
DEFER_CTX = re.compile(r"defer|DQ-\d|removed|no longer|dropped|not transmitted", re.I)


def parse_question_registry(filing: Path, questions_file: str) -> dict[str, dict]:
    """Read the questions doc's master map → {QK: {display, transmitted}}. Empty if absent."""
    qp = filing / questions_file
    if not qp.exists():
        return {}
    reg = {}
    for ln in qp.read_text(encoding="utf-8").split("\n"):
        m = QK_ROW.match(ln)
        if m:
            reg[m.group(1)] = {"display": m.group(2), "transmitted": m.group(3) == "✅"}
    return reg


CHANGELOG_ROW = re.compile(r"^\s*\|\s*\d{4}-\d{2}-\d{2}\s*\|")  # a dated changelog table row


def check_question_liveness(pkg_docs: dict[str, Path], registry: dict[str, dict],
                            questions_file: str) -> list[dict]:
    if not registry:
        return []
    findings = []
    for name, md in sorted(pkg_docs.items()):
        if md.name == questions_file:
            continue  # the registry doc itself legitimately lists every (deferred) key
        in_comment = False
        for i, ln in enumerate(md.read_text(encoding="utf-8").split("\n"), 1):
            # skip HTML-comment metadata (AI-CHANGELOG) and dated changelog rows — historical
            # provenance legitimately names superseded anchors and is not a current claim.
            if in_comment:
                if "-->" in ln:
                    in_comment = False
                continue
            if ln.lstrip().startswith("<!--") and "-->" not in ln:
                in_comment = True
                continue
            if CHANGELOG_ROW.match(ln):
                continue
            if not ANCHOR_VERB.search(ln):
                continue
            for m in QK_REF.finditer(ln):
                qk = m.group(0)
                # A disposition note ("deferred / → DQ-N / removed / not transmitted") often
                # trails a QK or a QK-list; look generously forward (and a little back) so a
                # correctly-dispositioned key is not mistaken for a live-anchor claim.
                ctx = ln[max(0, m.start() - 40):m.end() + 110]
                if DEFER_CTX.search(ctx):
                    continue
                info = registry.get(qk)
                if info is None:
                    findings.append({"check": "S4", "sev": "WARN", "file": md.name, "line": i,
                                     "msg": f"anchor/support declaration names '{qk}', which is not in "
                                            f"the questions master map — stale key or typo"})
                elif not info["transmitted"]:
                    findings.append({"check": "S4", "sev": "WARN", "file": md.name, "line": i,
                                     "msg": f"anchor/support declaration names '{qk}' ({info['display']}), "
                                            f"which is DEFERRED / not transmitted — a filed or apparatus "
                                            f"claim to anchor/support it is stale drift (renumber/de-scope "
                                            f"not propagated); reframe as deferred or drop it"})
    return findings


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("filing_dir")
    ap.add_argument("--cover", default="cover-letter.md")
    ap.add_argument("--questions", default="fda-questions.md")
    ap.add_argument("--transmit-gate", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    filing = Path(a.filing_dir)
    cover_path = filing / a.cover
    if not cover_path.exists():
        print(f"error: cover letter not found: {cover_path}", file=sys.stderr)
        return 2
    cover_text = cover_path.read_text(encoding="utf-8")

    entries = parse_numbered_lists(cover_text)
    # Transmitted filed bodies = cover letter + every IN-FOLDER numbered attachment. The
    # filed-body scans (S1 tier accuracy, S3b out-of-folder links) apply only to what ships
    # to FDA — internal assembly artifacts (e.g. the composition manifest) legitimately
    # reference upstream source paths and are out of scope.
    transmitted: dict[str, Path] = {docid(a.cover): cover_path.resolve()}
    for e in entries:
        p = filing / e["path"].split("#", 1)[0]
        if p.exists() and p.suffix == ".md" and not escapes_folder(e["path"], filing):
            transmitted[e["stem"]] = p.resolve()
    tier = {stem: classify_self_tier(p) for stem, p in transmitted.items()}

    # S4 scans the TRANSMITTED docs + the manifest (incl. their internal apparatus) — a
    # stale anchor/support claim there is drift. Deferred briefs that merely sit in the
    # folder (moved to the 510(k), not attached) are out of scope: their internal anchors
    # to their own deferred question are correct, not drift.
    registry = parse_question_registry(filing, a.questions)
    pkg_docs = dict(transmitted)
    manifest_p = filing / "composition-manifest.md"
    if manifest_p.exists():
        pkg_docs["composition-manifest.md"] = manifest_p.resolve()

    findings: list[dict] = []
    findings += check_cross_reference(tier, transmitted)
    findings += check_attachment_numbers(cover_text, entries)
    findings += check_folder_boundary(filing, cover_text, entries, transmitted)
    findings += check_question_liveness(pkg_docs, registry, a.questions)

    fails = [f for f in findings if f["sev"] == "FAIL"]
    warns = [f for f in findings if f["sev"] == "WARN"]
    if a.json:
        print(json.dumps({"findings": findings, "fails": len(fails), "warns": len(warns)}, indent=2))
    else:
        for f in sorted(findings, key=lambda x: (x["check"], x.get("file", ""), x.get("line", 0))):
            loc = f"{f.get('file','')}:{f['line']}" if f.get("line") else f.get("file", "package")
            print(f"  [{f['sev']}] {f['check']} {loc} — {f['msg']}")
        print(f"\ncheck-package-consistency: {len(fails)} FAIL, {len(warns)} WARN "
              f"({len(transmitted)} transmitted docs, {len(entries)} numbered entries)")
    if a.transmit_gate and fails:
        return 2
    return 1 if (fails or warns) else 0


if __name__ == "__main__":
    sys.exit(main())
