#!/usr/bin/env python3
"""qsub_scope_lint — Q-Sub scope & reviewer-availability checks for a submission package.

The problem this solves (source-document-agnostic): a Q-Submission assembled from
510(k)-grade DHF artifacts inherits (a) references to documents the reviewer does NOT
receive (child SADs, per-module SRAs, threat models, SBOMs, item SRSs, internal QMS
SOP/FORM IDs) and (b) 🔒-container boundary defects where a visible `🔒 END INTERNAL`
marker diverges from the `</details>` tag — so a marker-keyed strip can leak deferred
content. Neither is caught by a link-based reference check or a leak (repo-path) scrub.

This linter is **tag-based** (it strips 🔒 `<details>…</details>` containers by balanced
tag, never by the fragile visible marker) and **prose-aware** (it greps the surviving
filed body for a denylist of non-transmitted doctypes). It is project-agnostic: the
transmitted set is read from the cover letter's Attachments list, not hard-coded.

Checks (each: PASS / WARN advisory / BLOCK under --transmit-gate):
  C1  container-integrity  — <details>/</details> balanced; every `🔒 END INTERNAL`
                             marker is adjacent to a </details> (marker⇄tag agreement).
  C2  reference-availability (T1) — filed-body prose references to non-transmitted
                             doctypes, minus an allowlist for approved forward-reference
                             phrasing ("… part of the 510(k) …", "… on request").
  C3  blocking-brief-anchor (T3) — a transmission-blocking brief must anchor at least
                             one ACTIVE (non-deferred) question.
  C4  manifest ⇄ cover-letter — section-aware three-state (transmitted / on-request /
                             grounding-only) reconciliation on path-aware doc identity.
  C5  altitude — a raw controlled DHF doc (`_confluence/**`) attached with no Q-Sub
                             scoping note/extract adjacent to its attachment line (WARN).

Usage:
  python3 qsub_scope_lint.py <qsub-dir> [--cover cover-letter.md] [--manifest composition-manifest.md]
                             [--questions fda-questions.md] [--transmit-gate] [--json]
Exit: 0 clean; 1 WARN present (advisory); 2 BLOCK present under --transmit-gate.
"""
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path

def docid(p: str) -> str:
    """Path-aware document identity — last two path components (minus .md). Distinguishes the
    many `v1.0.0.md` files that live in different `_confluence/<dhf>/…/<doctype>/` dirs, while
    still matching same-dir relative links (`./device-description.md`) by bare stem."""
    parts = [x for x in Path(p).parts if x not in (".", "..")]
    if len(parts) >= 2:
        return "/".join(parts[-2:])[:-3] if parts[-1].endswith(".md") else "/".join(parts[-2:])
    return Path(p).stem


# ── tag-based internal-zone stripping ──────────────────────────────────────────
DETAILS_OPEN = re.compile(r"<details\b", re.I)
DETAILS_CLOSE = re.compile(r"</details\s*>", re.I)


def strip_zones(text: str) -> tuple[str, list[str]]:
    """Return (filed_body, integrity_notes). Strips leading <!-- --> metadata and every
    balanced <details>…</details> container BY TAG (nesting-safe). Filed lines outside any
    open container survive; their original 1-based line numbers are preserved via a map."""
    lines = text.split("\n")
    # drop leading HTML-comment metadata block(s)
    depth = 0
    filed: list[tuple[int, str]] = []
    in_comment = False
    for i, ln in enumerate(lines, 1):
        s = ln
        if in_comment:
            if "-->" in s:
                in_comment = False
            continue
        if s.lstrip().startswith("<!--") and "-->" not in s:
            in_comment = True
            continue
        opens = len(DETAILS_OPEN.findall(s))
        closes = len(DETAILS_CLOSE.findall(s))
        if depth > 0:
            depth += opens - closes
            if depth < 0:
                depth = 0
            continue
        # depth == 0 here
        if opens > closes:
            depth += opens - closes
            continue  # the <details> opening line itself is internal
        filed.append((i, s))
    return "\n".join(f"{n}\t{t}" for n, t in filed), []


def _strip_html_comments(lines: list[str]) -> list[str]:
    """Blank out lines inside <!-- --> blocks so tag/marker counting ignores comment prose
    (an AI-CHANGELOG row may legitimately mention `</details>` or `🔒 END INTERNAL`)."""
    out, in_c = [], False
    for ln in lines:
        s = ln
        if in_c:
            out.append("")
            if "-->" in s:
                in_c = False
            continue
        if s.lstrip().startswith("<!--") and "-->" not in s:
            in_c = True
            out.append("")
            continue
        out.append(ln)
    return out


def check_container_integrity(text: str) -> list[dict]:
    findings = []
    lines = _strip_html_comments(text.split("\n"))
    depth = 0
    for i, ln in enumerate(lines, 1):
        depth += len(DETAILS_OPEN.findall(ln)) - len(DETAILS_CLOSE.findall(ln))
        if depth < 0:
            findings.append({"check": "C1", "sev": "BLOCK", "line": i,
                             "msg": "</details> without matching <details> (tag underflow)"})
            depth = 0
    if depth != 0:
        findings.append({"check": "C1", "sev": "BLOCK", "line": len(lines),
                         "msg": f"{depth} unclosed <details> container(s) — tags not balanced"})
    # marker ⇄ tag adjacency: every `🔒 END INTERNAL` must be within 3 lines of a </details>
    for i, ln in enumerate(lines, 1):
        if "🔒 END INTERNAL" in ln:
            window = "\n".join(lines[i - 1:i + 3])
            if not DETAILS_CLOSE.search(window):
                findings.append({"check": "C1", "sev": "BLOCK", "line": i,
                                 "msg": "`🔒 END INTERNAL` marker not adjacent to a </details> "
                                        "tag — a marker-keyed strip may diverge from the real "
                                        "container boundary (deferred-content leak risk)"})
    return findings


# ── T1 reference-availability ──────────────────────────────────────────────────
# Non-transmitted doctype patterns (generic medtech vocabulary — project-agnostic).
NONTRANSMITTED_PATTERNS = [
    (r"child\s+(Pre-?Op|Intra-?Op|Management Services|Mgmt Services)?\s*SADs?", "child SAD"),
    (r"(Management Services|Mgmt Services|Pre-?Op|Intra-?Op)\s+(Software\s+)?Architecture Document", "child SAD"),
    (r"\((?:Management Services|Mgmt Services|Pre-?Op|Intra-?Op)\s+SAD\)", "child SAD"),
    (r"\b(?:Management Services|Mgmt Services|Pre-?Op|Intra-?Op)\s+SADs?\b", "child SAD"),
    (r"per-module\s+(Software Risk Assessment|SRA)s?", "per-module SRA"),
    (r"\bper-module\s+SBOMs?\b", "per-module SBOM"),
    (r"per-module\s+threat models?", "per-module threat model"),
    (r"item\s+SRSs?\b|\b(Intra-?Op|Pre-?Op|Mgmt Services)\s+SRS\b", "item SRS"),
    (r"\bSOP-\d{4,}\b", "internal QMS SOP id"),
    (r"\bFORM-\d{4,}\b", "internal QMS FORM id"),
]
# Approved forward-reference phrasing that dispositions a T1 hit (same line).
ALLOWLIST = re.compile(
    r"510\(k\)\s+(technical\s+file|deliverable|submission)|part of the 510\(k\)"
    r"|accompan\w+\s+the\s+(planned\s+)?510\(k\)|available.*on request|committed\s+510\(k\)",
    re.I)


def check_reference_availability(filed_body: str, extra_targets: list[str]) -> list[dict]:
    findings = []
    pats = [(re.compile(p, re.I), lbl) for p, lbl in NONTRANSMITTED_PATTERNS]
    for tgt in extra_targets:  # grounding-only manifest stems
        pats.append((re.compile(re.escape(tgt), re.I), f"grounding-only doc ({tgt})"))
    for row in filed_body.split("\n"):
        if "\t" not in row:
            continue
        n, text = row.split("\t", 1)
        if ALLOWLIST.search(text):
            continue
        for rx, lbl in pats:
            m = rx.search(text)
            if m:
                findings.append({"check": "C2", "sev": "WARN", "line": int(n),
                                 "msg": f"filed-body reference to non-transmitted {lbl}: "
                                        f"…{text[max(0, m.start() - 25):m.end() + 25].strip()}…"})
                break
    return findings


# ── T3 blocking-brief anchors an active question ───────────────────────────────
def check_blocking_anchors(manifest: str, questions: str) -> list[dict]:
    findings = []
    if not manifest or not questions:
        return findings
    # deferred question ids (DQ-*) + their QK anchors from the questions doc
    deferred_qk = set(re.findall(r"###\s+DQ-\d+\s+\((QK-[A-Z0-9-]+)\)", questions))
    # transmission-blocking briefs: manifest rows containing "transmission-blocking" and a QK anchor
    for row in manifest.split("\n"):
        if "transmission-blocking" not in row.lower():
            continue
        if "not transmission-blocking" in row.lower() or "not a q-sub attachment" in row.lower():
            continue  # already downgraded
        qks = set(re.findall(r"QK-[A-Z0-9-]+", row))
        if qks and qks <= deferred_qk:
            findings.append({"check": "C3", "sev": "BLOCK", "line": 0,
                             "msg": f"transmission-blocking brief anchors only deferred question(s) "
                                    f"{sorted(qks)} — a blocker must anchor an active (transmitted) question"})
    return findings


def parse_attachments(cover: str) -> list[tuple[str, str]]:
    """(stem, raw-path) of the transmitted attachment set from the cover-letter `## Attachments`."""
    out, in_att = [], False
    for ln in cover.split("\n"):
        if ln.strip().startswith("## Attachments"):
            in_att = True
            continue
        if in_att and ln.startswith("## "):
            break
        if in_att:
            for m in re.finditer(r"\(([^)]+\.md)\)", ln):
                out.append((docid(m.group(1)), m.group(1)))
    return out


# ── C4 manifest ⇄ cover-letter reconciliation ─────────────────────────────────
GROUNDING = re.compile(r"not transmitted|not a q-?sub attachment|internal grounding"
                       r"|moved to the 510\(k\)|internal working source", re.I)


def parse_manifest_pieces(manifest: str) -> list[tuple[str, str, int]]:
    """(stem, state, line) for each manifest row carrying a `(path.md)` link, where state is
    'grounding' (marked not-transmitted) else 'transmitted' ('on-request' rows carry a cover-
    letter attachment too, so they group with transmitted for the attach match)."""
    out = []
    section_grounding = False  # true while under a "Grounding — not transmitted" header
    for i, ln in enumerate(manifest.split("\n"), 1):
        if ln.startswith("#"):  # a new header resets/sets section context
            section_grounding = bool(GROUNDING.search(ln))
            continue
        if not ln.lstrip().startswith("|"):
            continue
        m = re.search(r"\(([^)]+\.md)\)", ln)
        if not m:
            continue
        stem = docid(m.group(1))
        state = "grounding" if (section_grounding or GROUNDING.search(ln)) else "transmitted"
        out.append((stem, state, i))
    return out


def check_manifest_alignment(manifest: str, transmitted_stems: set) -> list[dict]:
    findings = []
    if not manifest:
        return findings
    pieces = parse_manifest_pieces(manifest)
    manifest_stems = {s for s, _, _ in pieces}
    for stem, state, line in pieces:
        if state == "transmitted" and stem not in transmitted_stems:
            findings.append({"check": "C4", "sev": "BLOCK", "line": line, "file": "composition-manifest.md",
                             "msg": f"manifest lists '{stem}' as a transmitted piece but it is NOT in the "
                                    f"cover-letter Attachments (mark it grounding/not-transmitted, or attach it)"})
        if state == "grounding" and stem in transmitted_stems:
            findings.append({"check": "C4", "sev": "WARN", "line": line, "file": "composition-manifest.md",
                             "msg": f"manifest marks '{stem}' grounding-only but it IS attached in the cover letter"})
    for stem in sorted(transmitted_stems):
        if stem.endswith("cover-letter") or stem == "cover-letter":
            continue
        if stem not in manifest_stems:
            findings.append({"check": "C4", "sev": "BLOCK", "line": 0, "file": "cover-letter.md",
                             "msg": f"cover-letter attaches '{stem}' but it has no composition-manifest entry"})
    return findings


# ── C5 altitude: controlled DHF doc attached raw (no Q-Sub scoping) ────────────
def check_altitude(attachments: list[tuple[str, str]], cover: str) -> list[dict]:
    findings = []
    # Specific scoping cues (NOT a bare "Q-Sub scope", which matches an unrelated brief title).
    scope_cue = re.compile(r"q-?sub extract|provided to frame|system architecture overview"
                           r"|q-?sub scoping note|scoped for (the )?q-?sub", re.I)
    lines = cover.split("\n")
    for stem, path in attachments:
        if "_confluence/" not in path:
            continue  # only raw controlled DHF-mirror docs (a generated extract lives elsewhere)
        # a scoping cue must appear on, or adjacent to, THIS attachment's own reference line(s)
        ref_idx = [i for i, l in enumerate(lines) if path in l]
        cued = any(scope_cue.search("\n".join(lines[max(0, i - 1):i + 2])) for i in ref_idx)
        if not cued:
            findings.append({"check": "C5", "sev": "WARN", "line": 0, "file": "cover-letter.md",
                             "msg": f"attachment '{stem}' is a raw controlled DHF doc ({path}) attached at full "
                                    f"altitude with no Q-Sub scoping note/extract — provide a Q-Sub extract "
                                    f"(gen_qsub_sad_extract.py) or a scoping preface"})
    return findings


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("qsub_dir")
    ap.add_argument("--cover", default="cover-letter.md")
    ap.add_argument("--manifest", default="composition-manifest.md")
    ap.add_argument("--questions", default="fda-questions.md")
    ap.add_argument("--transmit-gate", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    d = Path(a.qsub_dir)
    cover = (d / a.cover).read_text(encoding="utf-8") if (d / a.cover).exists() else ""
    manifest = (d / a.manifest).read_text(encoding="utf-8") if (d / a.manifest).exists() else ""
    questions = (d / a.questions).read_text(encoding="utf-8") if (d / a.questions).exists() else ""
    attachments = parse_attachments(cover)
    transmitted = {s for s, _ in attachments} | {docid(a.cover)}

    all_findings: list[dict] = []
    # C3 / C4 / C5 (package-level)
    all_findings += check_blocking_anchors(manifest, questions)
    all_findings += check_manifest_alignment(manifest, transmitted)
    all_findings += check_altitude(attachments, cover)
    # C1 + C2 per transmitted filed doc
    for md in sorted(d.glob("*.md")):
        if docid(str(md)) not in transmitted and md.stem not in transmitted:
            continue  # only lint what actually ships
        text = md.read_text(encoding="utf-8")
        c1 = check_container_integrity(text)
        filed, _ = strip_zones(text)
        c2 = check_reference_availability(filed, [])
        for f in c1 + c2:
            f["file"] = md.name
            all_findings.append(f)

    blocks = [f for f in all_findings if f["sev"] == "BLOCK"]
    warns = [f for f in all_findings if f["sev"] == "WARN"]
    if a.json:
        print(json.dumps({"findings": all_findings, "blocks": len(blocks), "warns": len(warns)}, indent=2))
    else:
        for f in all_findings:
            loc = f"{f.get('file','')}:{f['line']}" if f.get("line") else f.get("file", "package")
            print(f"  [{f['sev']}] {f['check']} {loc} — {f['msg']}")
        print(f"\nqsub-scope-lint: {len(blocks)} BLOCK, {len(warns)} WARN "
              f"(transmitted set: {len(transmitted)} docs)")
    if a.transmit_gate and blocks:
        return 2
    return 1 if warns or blocks else 0


if __name__ == "__main__":
    sys.exit(main())
