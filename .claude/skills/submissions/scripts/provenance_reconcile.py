#!/usr/bin/env python3
"""provenance_reconcile — flag when a document's grounding SOURCES have drifted,
and when a factual claim is NOT grounded in the primary source it cites.

`check` runs two classes of check:

  (1) SOURCE DRIFT — each `_provenance/<doc>.provenance.yml` records the upstream
      sources a submission document reproduces or summarizes (path +
      sections/decisions/terms + how_used). This tool pins each *content* source to
      its **git blob SHA** at reconciliation time (`stamp`, written to a generated
      `<doc>.sources-lock.json`) and flags when a source's current blob SHA differs
      from the pinned baseline — the signal that the source moved on and the derived
      document's copied/summarized content may now be stale.

  (2) CLAIM GROUNDING — a `claims_to_source[]` entry may pin its evidence with
      `source_path` + `source_page` + a verbatim `quote`; the quote must resolve in
      that source snapshot (`ground`). This catches a factual claim asserted *about*
      a primary source (e.g. a predicate/cleared-filing PDF) that the source does not
      actually support, or that was written from a sibling summary while the source
      sat un-consulted. Grounding is opt-in per claim, so legacy free-text claim rows
      are unaffected. Both drift and ungrounded-claim are transmit-blocking.

Why a hash and not "just reference the source": a regulated document must stay readable
and self-contained — a reviewer cannot be sent out to hundreds of pages of upstream
material to understand it (the project's W12.1 rule: carry the gist inline; a reference
is for depth, not comprehension). So the document KEEPS its reproduced content, and drift
is caught by comparing source hashes rather than by gutting the document into pointers.

Design choices:
  - The baseline lives in a **generated** `<doc>.sources-lock.json` beside the sidecar, so
    the churny part (hashes) never forces a fragile edit of the intent-bearing, comment-
    carrying `.provenance.yml`.
  - `check` also surfaces **unresolved** source paths (a recorded path that no longer
    resolves — e.g., a tree was retired/moved). That is drift in the provenance itself and
    is exactly how the pinning silently rots if left unwatched.
  - Only *content* sources are tracked (entries carrying `sections`/`decisions`/`terms`);
    framing files consulted "per rule" (a project's root README/guide) are skipped.

Usage:
  provenance_reconcile.py check [<filing-dir>] [--json] [--transmit-gate]
  provenance_reconcile.py stamp <doc-basename|*.provenance.yml|*.md> [--filing-dir <dir>]
Exit: 0 clean; 1 drift/unresolved/unbaselined/ungrounded present; 2 under
      --transmit-gate with drift or ungrounded-claim. (Claim grounding needs `pypdf`
      for PDF sources; absent it, PDF quotes are skipped with a NOTE, not failed.)
"""
from __future__ import annotations
import argparse, datetime, json, subprocess, sys
from pathlib import Path
import yaml

# Consulted-as-framing (read per project rule), not reproduced content → not hash-tracked.
FRAMING_BASENAMES = {"README.md", "CLAUDE.md"}


def repo_root() -> Path:
    out = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                         capture_output=True, text=True)
    return Path(out.stdout.strip()) if out.returncode == 0 else Path.cwd()


def blob_sha(p: Path) -> str | None:
    """git blob SHA of a file's current content (None if the path does not resolve)."""
    if not p.is_file():
        return None
    out = subprocess.run(["git", "hash-object", str(p)], capture_output=True, text=True)
    return out.stdout.strip() if out.returncode == 0 else None


def load_prov(yml: Path) -> dict | None:
    """Parsed sidecar, or None if the YAML is malformed (caller emits a finding)."""
    try:
        return yaml.safe_load(yml.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError:
        return None


def tracked_sources(prov: dict) -> list[dict]:
    """Content sources worth pinning: an entry with a path that names specific content
    used (sections/decisions/terms) and is not a framing file."""
    out = []
    for s in prov.get("sources_consulted") or []:
        if not isinstance(s, dict) or not s.get("path"):
            continue
        if Path(s["path"]).name in FRAMING_BASENAMES:
            continue
        if not any(k in s for k in ("sections", "decisions", "terms")):
            continue
        out.append(s)
    return out


def lock_path(yml: Path) -> Path:
    base = yml.name[:-len(".provenance.yml")] if yml.name.endswith(".provenance.yml") else yml.stem
    return yml.with_name(f"{base}.sources-lock.json")


def stamp(yml: Path, root: Path, today: str) -> dict | None:
    prov = load_prov(yml)
    if prov is None:
        return None  # malformed YAML — caller reports
    lock = {"doc": prov.get("doc"), "generated_by": "provenance_reconcile stamp",
            "stamped": today, "note": "GENERATED — source blob-SHA baseline; re-stamp only "
            "after reconciling the document against the source.", "sources": {}}
    for s in tracked_sources(prov):
        lock["sources"][s["path"]] = blob_sha(root / s["path"])
    lp = lock_path(yml)
    lp.write_text(json.dumps(lock, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return lock


def check(filing: Path, root: Path) -> list[dict]:
    findings = []
    provdir = filing / "_provenance"
    if not provdir.is_dir():
        return findings
    for yml in sorted(provdir.glob("*.provenance.yml")):
        prov = load_prov(yml)
        if prov is None:
            findings.append({"doc": yml.name, "source": "(whole sidecar)", "kind": "malformed-yaml",
                             "sev": "WARN", "msg": "provenance sidecar is not valid YAML — cannot "
                             "track drift for this document until it is fixed"})
            continue
        lp = lock_path(yml)
        lock = json.loads(lp.read_text()) if lp.is_file() else None
        baseline = (lock or {}).get("sources", {})
        for s in tracked_sources(prov):
            path = s["path"]
            cur = blob_sha(root / path)
            if cur is None:
                findings.append({"doc": yml.name, "source": path, "kind": "unresolved-path",
                                 "sev": "WARN", "msg": "recorded source path does not resolve — "
                                 "the source moved or its tree was retired; fix the provenance path"})
            elif lock is None or path not in baseline:
                findings.append({"doc": yml.name, "source": path, "kind": "unbaselined",
                                 "sev": "WARN", "msg": f"source not pinned yet — run `stamp {yml.name}` "
                                 "once the document is reconciled against it"})
            elif baseline[path] != cur:
                findings.append({"doc": yml.name, "source": path, "kind": "drift", "sev": "WARN",
                                 "msg": f"source changed since last reconciliation "
                                 f"(pinned {str(baseline[path])[:10]} → now {cur[:10]}) — re-check the "
                                 f"derived content, then re-stamp", "how_used": s.get("how_used", "")})
    return findings


def _norm(t: str) -> str:
    import re
    # Fold typographic quotes/dashes so a straight-ASCII pinned quote still matches a
    # source that renders curly quotes / en–em dashes (common in PDF text extraction).
    t = (t or "").translate(str.maketrans({
        "“": '"', "”": '"', "‘": "'", "’": "'",
        "–": "-", "—": "-", " ": " "}))
    return re.sub(r"\s+", " ", t).lower()


def _source_text(p: Path, page) -> str | None:
    """Text of a primary source for quote grounding. PDFs need pypdf (returns ""
    if pypdf is absent, so the caller can emit a skip-notice rather than a false
    fail); markdown/text is read directly. None means the file does not resolve."""
    if not p.is_file():
        return None
    if p.suffix.lower() == ".pdf":
        try:
            from pypdf import PdfReader
        except ImportError:
            return ""  # signal: cannot verify PDFs here
        try:
            pages = PdfReader(str(p)).pages
        except Exception:
            return None
        if page and str(page).isdigit() and 1 <= int(page) <= len(pages):
            return pages[int(page) - 1].extract_text() or ""
        return "\n".join((pg.extract_text() or "") for pg in pages)
    try:
        return p.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def ground(filing: Path, root: Path) -> list[dict]:
    """Claim↔primary-source grounding — the check drift-pinning cannot do.

    A `claims_to_source[]` entry may pin its evidence structurally:
        - claim: "..."
          source_path: <repo-relative primary source, e.g. a cleared-filing PDF>
          source_page: <int, for PDFs>
          quote: "<verbatim substring of the source that supports the claim>"
    When those fields are present, the quote MUST resolve in that source snapshot.
    This catches a factual claim asserted *about* a primary source that the source
    does not actually support — or that was never opened (the claim written from a
    sibling summary while the source sat in `sources_not_consulted`). Grounding is
    opt-in per claim (entries without `quote`+`source_path` are skipped), so it does
    not disturb existing free-text `claims_to_source` rows.
    """
    findings = []
    provdir = filing / "_provenance"
    if not provdir.is_dir():
        return findings
    pypdf_warned = False
    for yml in sorted(provdir.glob("*.provenance.yml")):
        prov = load_prov(yml)
        if prov is None:
            continue  # malformed already reported by check()
        for c in prov.get("claims_to_source") or []:
            if not isinstance(c, dict):
                continue
            quote, spath = c.get("quote"), c.get("source_path")
            if not quote or not spath:
                continue
            claim = str(c.get("claim", ""))[:60]
            text = _source_text(root / spath, c.get("source_page"))
            if text is None:
                findings.append({"doc": yml.name, "source": spath, "kind": "unresolved-source",
                                 "sev": "WARN", "msg": f"claim's source_path does not resolve — "
                                 f"cannot ground claim {claim!r}"})
                continue
            if text == "" and (root / spath).suffix.lower() == ".pdf":
                if not pypdf_warned:
                    findings.append({"doc": yml.name, "source": spath, "kind": "grounding-skipped",
                                     "sev": "NOTE", "msg": "pypdf not installed — PDF claim quotes "
                                     "cannot be verified; `pip install pypdf` to enable grounding"})
                    pypdf_warned = True
                continue
            needle = " ".join(_norm(quote).split()[:8])
            if needle and needle not in _norm(text):
                loc = f" p{c['source_page']}" if c.get("source_page") else ""
                findings.append({"doc": yml.name, "source": f"{spath}{loc}", "kind": "ungrounded-claim",
                                 "sev": "WARN", "msg": f"pinned quote for claim {claim!r} not found in "
                                 f"its cited source — the claim is not grounded in the primary source; "
                                 f"re-verify against the source and fix the quote/page (or the claim)"})
    return findings


def resolve_yml(arg: str, filing: Path) -> Path | None:
    p = Path(arg)
    if p.suffix == ".yml" and p.exists():
        return p
    provdir = filing / "_provenance"
    base = Path(arg).name
    for cand in (base, base.removesuffix(".md"), base.removesuffix(".provenance.yml")):
        y = provdir / f"{cand}.provenance.yml"
        if y.exists():
            return y
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("action", choices=["check", "stamp"])
    ap.add_argument("target", nargs="?", help="filing dir (check) or doc/sidecar (stamp)")
    ap.add_argument("--filing-dir", default="docs/project/submissions/qsub")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--transmit-gate", action="store_true")
    a = ap.parse_args()
    root = repo_root()

    if a.action == "stamp":
        if not a.target:
            print("error: stamp needs a doc basename / *.md / *.provenance.yml", file=sys.stderr)
            return 2
        filing = Path(a.filing_dir)
        yml = resolve_yml(a.target, filing)
        if not yml:
            print(f"error: no provenance sidecar for '{a.target}' under {filing}/_provenance", file=sys.stderr)
            return 2
        today = datetime.date.today().isoformat()
        lock = stamp(yml, root, today)
        if lock is None:
            print(f"error: {yml.name} is malformed YAML — fix it before stamping", file=sys.stderr)
            return 2
        pinned = sum(1 for v in lock["sources"].values() if v)
        unresolved = [k for k, v in lock["sources"].items() if not v]
        print(f"stamped {yml.name}: pinned {pinned} source(s) → {lock_path(yml).name}")
        for u in unresolved:
            print(f"  ⚠ unresolved (not pinned): {u}")
        return 1 if unresolved else 0

    filing = Path(a.target or a.filing_dir)
    findings = check(filing, root) + ground(filing, root)
    drift = [f for f in findings if f["kind"] == "drift"]
    ungrounded = [f for f in findings if f["kind"] == "ungrounded-claim"]
    blocking = drift + ungrounded  # both are transmit-blocking
    if a.json:
        print(json.dumps({"findings": findings, "drift": len(drift),
                          "ungrounded": len(ungrounded), "total": len(findings)}, indent=2))
    else:
        for f in sorted(findings, key=lambda x: (x["doc"], x["kind"], x["source"])):
            print(f"  [{f['sev']}] {f['kind']} {f['doc']} :: {f['source']}\n      {f['msg']}")
            if f.get("how_used"):
                print(f"      derived use: {f['how_used'][:160]}")
        print(f"\nprovenance-reconcile: {len(drift)} drift, {len(ungrounded)} ungrounded-claim, "
              f"{len(findings)} total finding(s)")
    if a.transmit_gate and blocking:
        return 2
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
