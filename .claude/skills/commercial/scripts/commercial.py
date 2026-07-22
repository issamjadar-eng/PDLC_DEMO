#!/usr/bin/env python3
"""commercial.py — business-question analysis engine (commercial skill).

Owns the ANSWER tier of the analytics stack: immutable answer editions
(report.md + data.json + pins), the claim lint, the gated approval lifecycle
(draft -> approved -> superseded), and the console sidecar render.

Division of labor (the anti-hallucination boundary):
  - The corpus skill owns the data tier (immutable snapshots + provenance).
  - Project-side computation scripts (registered in commercial.yml) read pinned
    snapshots and deterministically write report.md + data.json. The LLM never
    computes a number; it orchestrates and interprets.
  - This engine enforces the seams: every numeric claim in a report must carry a
    resolvable marker; approval is blocked until the lint and freshness are green;
    approved editions are hash-pinned and never mutated.

Claim-marker syntax (in report.md):
  [src: <dataset>@<snapshot>]   value comes from a pinned corpus snapshot
  [assume: A-NNN]               value rests on a stated assumption record
  [derived: <id>]               value is a computed series/verdict in data.json
  [config: <relpath>]           value is a declared plan/config constant (file must exist)
  [waived: W-NNN]               stale-data acknowledgment (waiver must be active)

Requires: Python 3.9+, PyYAML.
"""

import argparse
import csv
import datetime as dt
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.stderr.write("commercial.py requires PyYAML\n")
    sys.exit(2)

DEFAULT_ROOT = "docs/project/commercial"
DEFAULT_CORPUS = "docs/project/corpus"
SCHEMA_VERSION = "1.0"

MARKER_RE = re.compile(r"\[(src|assume|derived|config|waived):\s*([^\]]+?)\s*\]")
# tokens that contain digits but are identifiers/dates, not numeric claims
EXEMPT_TOKEN_RE = re.compile(
    r"BQ-\d+|A-\d{3}|W-\d{3}|C-\d{4}-\d{2}|\d{4}-\d{2}-\d{2}(?:\.\d+)?|PP\d+|PE-\d+|S-[A-Z]+-\d+|K\d{6}"
)
ESTIMATION_RE = re.compile(r"\b(estimated?|likely|approximately|roughly|assumed?|modeled)\b", re.I)


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def load_yaml(p: Path):
    with open(p) as f:
        return yaml.safe_load(f)


def dump_yaml(d, p: Path):
    with open(p, "w") as f:
        yaml.safe_dump(d, f, sort_keys=False, allow_unicode=True, width=100)


def today() -> str:
    return dt.date.today().isoformat()


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


class CommercialError(Exception):
    pass


# ---------------------------------------------------------------- config / corpus glue

def load_config(root: Path) -> dict:
    cfg_path = root / "commercial.yml"
    if not cfg_path.exists():
        raise CommercialError(f"no commercial.yml at {cfg_path}")
    return load_yaml(cfg_path)


def bq_entry(cfg: dict, bq: str) -> dict:
    for q in cfg.get("questions", []):
        if q["id"] == bq:
            return q
    raise CommercialError(f"unknown question id: {bq}")


def corpus_latest(corpus_root: Path, dataset: str) -> str:
    p = corpus_root / dataset / "latest"
    if not p.exists():
        raise CommercialError(f"corpus dataset has no snapshot: {dataset}")
    return p.read_text().strip()


def corpus_dataset_cfg(corpus_root: Path, dataset: str) -> dict:
    return load_yaml(corpus_root / dataset / "dataset.yml")


def snapshot_age_days(snapshot: str) -> int:
    return (dt.date.today() - dt.date.fromisoformat(snapshot.split(".")[0])).days


def assumption_record(corpus_root: Path, aid: str):
    for p in corpus_root.glob(f"*/*/assumptions/{aid}.yml"):
        return load_yaml(p)
    return None


def waiver_record(corpus_root: Path, wid: str):
    for p in corpus_root.glob(f"*/*/waivers/{wid}.yml"):
        return load_yaml(p)
    return None


# ---------------------------------------------------------------- editions

def bq_dir(root: Path, bq: str) -> Path:
    return root / "reports" / bq


def list_editions(root: Path, bq: str):
    d = bq_dir(root, bq)
    out = []
    if d.is_dir():
        for e in sorted(p for p in d.iterdir() if p.is_dir()):
            meta = e / "edition.yml"
            if meta.exists():
                out.append(load_yaml(meta))
    return out


def find_edition(root: Path, bq: str, edition: str = None):
    eds = list_editions(root, bq)
    if not eds:
        return None
    if edition:
        for e in eds:
            if e["edition"] == edition:
                return e
        raise CommercialError(f"{bq}: no edition {edition}")
    drafts = [e for e in eds if e["status"] == "draft"]
    return (drafts or eds)[-1]


# ---------------------------------------------------------------- lint

def lint_edition(root: Path, corpus_root: Path, bq: str, ed: dict):
    """Returns (errors, warnings). Deterministic; no LLM judgment."""
    errors, warnings = [], []
    edir = bq_dir(root, bq) / ed["edition"]
    report, datap = edir / "report.md", edir / "data.json"
    if not report.exists():
        return [f"{bq}@{ed['edition']}: report.md missing"], warnings
    if not datap.exists():
        return [f"{bq}@{ed['edition']}: data.json missing"], warnings
    data = json.loads(datap.read_text())
    series_ids = {s["id"] for s in data.get("series", [])} | {v["id"] for v in data.get("verdicts", [])}
    pins = ed.get("pins", {})

    waived_ids = set()
    in_fence = False
    lines = report.read_text().splitlines()
    divider = re.compile(r"^\s*\|[\s\-:|]+\|\s*$")
    # a table row immediately followed by a divider is a header row — column labels
    # (e.g. "Tickets/100") are not numeric claims
    header_lines = {i for i in range(len(lines) - 1)
                    if lines[i].lstrip().startswith("|") and divider.match(lines[i + 1])}
    for i, line in enumerate(lines):
        n = i + 1
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence or line.strip().startswith("#") or i in header_lines:
            continue
        if divider.match(line):
            continue  # table divider
        markers = MARKER_RE.findall(line)
        # resolve markers
        for kind, val in markers:
            if kind == "src":
                if "@" not in val:
                    errors.append(f"L{n}: malformed src marker: {val}")
                    continue
                ds, snap = val.rsplit("@", 1)
                if ds not in pins:
                    errors.append(f"L{n}: [src: {val}] cites unpinned dataset {ds}")
                elif pins[ds] != snap:
                    errors.append(f"L{n}: [src: {val}] cites snapshot {snap} but edition pins {pins[ds]}")
                elif not (corpus_root / ds / "snapshots" / snap).is_dir():
                    errors.append(f"L{n}: [src: {val}] snapshot does not exist on disk")
            elif kind == "assume":
                rec = assumption_record(corpus_root, val)
                if rec is None:
                    errors.append(f"L{n}: [assume: {val}] record not found in corpus")
                elif rec.get("status") != "active":
                    errors.append(f"L{n}: [assume: {val}] status is {rec.get('status')} (must be active)")
            elif kind == "derived":
                if val not in series_ids:
                    errors.append(f"L{n}: [derived: {val}] not present in data.json series/verdicts")
            elif kind == "config":
                if not (Path(val).exists() or (root / val).exists()):
                    errors.append(f"L{n}: [config: {val}] file not found")
            elif kind == "waived":
                rec = waiver_record(corpus_root, val)
                if rec is None or rec.get("status") != "active" or \
                        dt.date.fromisoformat(str(rec["expires"])) < dt.date.today():
                    errors.append(f"L{n}: [waived: {val}] waiver missing, inactive, or expired")
                else:
                    waived_ids.add(val)
        # numeric-claim rule: strip markers + exempt tokens; leftover digits need a marker
        stripped = MARKER_RE.sub("", line)
        stripped = EXEMPT_TOKEN_RE.sub("", stripped)
        if re.search(r"\d", stripped) and not markers:
            errors.append(f"L{n}: numeric claim without a [src|assume|derived|config] marker: {line.strip()[:80]}")
        # estimation language rule
        if ESTIMATION_RE.search(MARKER_RE.sub("", line)) and not any(k == "assume" for k, _ in markers):
            warnings.append(f"L{n}: estimation language without [assume: A-NNN]: {line.strip()[:80]}")

    # freshness of pins
    for ds, snap in pins.items():
        max_age = int(corpus_dataset_cfg(corpus_root, ds).get("max_age_days", 90))
        age = snapshot_age_days(snap)
        if age > max_age and not waived_ids:
            errors.append(f"pin {ds}@{snap} is STALE ({age}d > {max_age}d) and report carries no [waived: W-NNN]")

    # data.json series must carry evidence_class + provenance
    for s in data.get("series", []):
        if s.get("evidence_class") not in ("measured", "derived", "assumed", "unavailable"):
            errors.append(f"data.json series {s.get('id')}: bad evidence_class {s.get('evidence_class')!r}")
        if not s.get("provenance"):
            errors.append(f"data.json series {s.get('id')}: missing provenance")
    return errors, warnings


# ---------------------------------------------------------------- commands

def cmd_answer(args):
    root, corpus_root = Path(args.root), Path(args.corpus_root)
    cfg = load_config(root)
    q = bq_entry(cfg, args.bq)
    if not q.get("computation"):
        raise CommercialError(f"{args.bq} has no computation registered (status: {q.get('status', 'planned')})")
    pins = {ds: corpus_latest(corpus_root, ds) for ds in q.get("corpus_deps", [])}
    if not pins:
        raise CommercialError(f"{args.bq} declares no corpus_deps — an answer must pin data")
    edition = today()
    edir = bq_dir(root, args.bq) / edition
    if edir.exists():
        existing = load_yaml(edir / "edition.yml") if (edir / "edition.yml").exists() else None
        if existing and existing["status"] != "draft":
            n = 2
            while (bq_dir(root, args.bq) / f"{edition}.{n}").exists():
                n += 1
            edition = f"{edition}.{n}"
            edir = bq_dir(root, args.bq) / edition
        else:
            shutil.rmtree(edir)  # drafts are re-generable until approved
    edir.mkdir(parents=True)
    (edir / "pins.json").write_text(json.dumps(pins, indent=1))
    cmd = q["computation"].format(bq=args.bq, corpus_root=str(corpus_root.resolve()),
                                  out=str(edir.resolve()))
    print(f"[{args.bq}] computing edition {edition}: {cmd}")
    proc = subprocess.run(cmd, shell=True, cwd=str(root), capture_output=True, text=True)
    if proc.returncode != 0:
        shutil.rmtree(edir)
        raise CommercialError(f"computation failed ({proc.returncode}):\n{proc.stderr[-2000:]}")
    for req in ("report.md", "data.json"):
        if not (edir / req).exists():
            shutil.rmtree(edir)
            raise CommercialError(f"computation did not produce {req}")
    ed = {"bq": args.bq, "edition": edition, "status": "draft", "created_at": now_iso(), "pins": pins}
    dump_yaml(ed, edir / "edition.yml")
    errors, warnings = lint_edition(root, corpus_root, args.bq, ed)
    print(f"[{args.bq}@{edition}] draft written; lint: {len(errors)} error(s), {len(warnings)} warning(s)")
    for e in errors:
        print(f"  ERROR {e}")
    for w in warnings:
        print(f"  warn  {w}")
    return 1 if errors else 0


def cmd_lint(args):
    root, corpus_root = Path(args.root), Path(args.corpus_root)
    ed = find_edition(root, args.bq, args.edition)
    if not ed:
        raise CommercialError(f"{args.bq}: no editions")
    errors, warnings = lint_edition(root, corpus_root, args.bq, ed)
    print(f"[{args.bq}@{ed['edition']}] lint: {len(errors)} error(s), {len(warnings)} warning(s)")
    for e in errors:
        print(f"  ERROR {e}")
    for w in warnings:
        print(f"  warn  {w}")
    return 1 if errors else 0


def cmd_approve(args):
    root, corpus_root = Path(args.root), Path(args.corpus_root)
    ed = find_edition(root, args.bq, args.edition)
    if not ed:
        raise CommercialError(f"{args.bq}: no editions")
    if ed["status"] == "approved":
        raise CommercialError(f"{args.bq}@{ed['edition']} already approved")
    errors, warnings = lint_edition(root, corpus_root, args.bq, ed)
    if errors:
        print(f"APPROVAL BLOCKED — {len(errors)} lint error(s):")
        for e in errors:
            print(f"  ERROR {e}")
        return 1
    edir = bq_dir(root, args.bq) / ed["edition"]
    # supersede prior approved
    for other in list_editions(root, args.bq):
        if other["status"] == "approved":
            other["status"] = "superseded"
            other["superseded_by"] = ed["edition"]
            dump_yaml(other, bq_dir(root, args.bq) / other["edition"] / "edition.yml")
    approval = {
        "bq": args.bq, "edition": ed["edition"],
        "approved_by": args.by, "approved_at": now_iso(),
        "checks": {"lint_errors": 0, "lint_warnings": len(warnings), "freshness": "pass",
                   "verify_note": args.verify_note or "not recorded"},
        "content_hashes": {"report.md": sha256_file(edir / "report.md"),
                           "data.json": sha256_file(edir / "data.json")},
    }
    dump_yaml(approval, edir / "approval.yml")
    ed["status"] = "approved"
    dump_yaml(ed, edir / "edition.yml")
    print(f"[{args.bq}@{ed['edition']}] APPROVED by {args.by} (content hash-pinned)")
    return 0


def _bq_sidecar_row(root: Path, corpus_root: Path, q: dict):
    bq = q["id"]
    eds = list_editions(root, bq)
    approved = next((e for e in reversed(eds) if e["status"] == "approved"), None)
    draft = next((e for e in reversed(eds) if e["status"] == "draft"), None)
    if not q.get("computation"):
        status = "not-implemented"
    elif not eds:
        status = "no-answer"
    elif approved:
        status = "answered"
    else:
        status = "draft-only"
    row = {
        "id": bq, "question": q["question"], "category": q["category"],
        "personas": q.get("personas", []), "cadence": q.get("cadence", ""),
        "status": status,
        "approved_edition": approved["edition"] if approved else None,
        "draft_edition": draft["edition"] if draft else None,
        "editions": [{"edition": e["edition"], "status": e["status"]} for e in eds],
        "assumptions": [], "freshness": None, "verdict_headline": None,
        "evidence_class": None, "report_path": None, "data_path": None,
    }
    show = approved or draft
    if show:
        edir = bq_dir(root, bq) / show["edition"]
        row["report_path"] = str((edir / "report.md").relative_to(root.parent.parent.parent))
        row["data_path"] = str((edir / "data.json").relative_to(root.parent.parent.parent))
        data = json.loads((edir / "data.json").read_text())
        verds = data.get("verdicts", [])
        if verds:
            row["verdict_headline"] = verds[0].get("headline")
        classes = [s.get("evidence_class") for s in data.get("series", [])]
        for c in ("assumed", "derived", "measured"):
            if c in classes:
                row["evidence_class"] = c  # worst-of ordering
                break
        report_text = (edir / "report.md").read_text()
        row["assumptions"] = sorted({v for k, v in MARKER_RE.findall(report_text) if k == "assume"})
        bands = []
        for ds, snap in show.get("pins", {}).items():
            max_age = int(corpus_dataset_cfg(corpus_root, ds).get("max_age_days", 90))
            age = snapshot_age_days(snap)
            bands.append("stale" if age > max_age else ("aging" if age > max_age * 0.75 else "fresh"))
        row["freshness"] = ("stale" if "stale" in bands else "aging" if "aging" in bands else "fresh") \
            if bands else None
    return row


def cmd_render(args):
    root, corpus_root = Path(args.root), Path(args.corpus_root)
    cfg = load_config(root)
    rows = [_bq_sidecar_row(root, corpus_root, q) for q in cfg.get("questions", [])]
    out = {
        "schema_version": SCHEMA_VERSION, "generated": now_iso(),
        "categories": cfg.get("categories", []),
        "questions": rows,
    }
    console_dir = root / ".console"
    console_dir.mkdir(exist_ok=True)
    (console_dir / "commercial-index.json").write_text(json.dumps(out, indent=1))
    n_ans = sum(1 for r in rows if r["status"] == "answered")
    n_draft = sum(1 for r in rows if r["status"] == "draft-only")
    print(f"rendered .console/commercial-index.json — {len(rows)} questions "
          f"({n_ans} answered, {n_draft} draft-only)")
    return 0


def cmd_check(args):
    root, corpus_root = Path(args.root), Path(args.corpus_root)
    cfg = load_config(root)
    failures = []
    for q in cfg.get("questions", []):
        for ed in list_editions(root, q["id"]):
            edir = bq_dir(root, q["id"]) / ed["edition"]
            if ed["status"] in ("approved", "superseded") and (edir / "approval.yml").exists():
                appr = load_yaml(edir / "approval.yml")
                for fname, h in appr.get("content_hashes", {}).items():
                    if not (edir / fname).exists():
                        failures.append(f"{q['id']}@{ed['edition']}: {fname} missing")
                    elif sha256_file(edir / fname) != h:
                        failures.append(f"{q['id']}@{ed['edition']}: {fname} hash mismatch (MUTATED after approval?)")
            if ed["status"] == "approved":
                errors, _ = lint_edition(root, corpus_root, q["id"], ed)
                failures.extend(f"{q['id']}@{ed['edition']}: {e}" for e in errors)
    # corpus health is part of the chain
    corpus_script = Path(".claude/skills/corpus/scripts/corpus.py")
    if corpus_script.exists():
        proc = subprocess.run([sys.executable, str(corpus_script), "--root", str(corpus_root), "check"],
                              capture_output=True, text=True)
        if proc.returncode != 0:
            failures.append("corpus check FAILED (run corpus.py check for detail)")
    if failures:
        print("COMMERCIAL CHECK FAILURES:")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("commercial check: GREEN (editions integrity + approved lint + corpus chain)")
    return 0


def cmd_catalog(args):
    root, corpus_root = Path(args.root), Path(args.corpus_root)
    cfg = load_config(root)
    for q in cfg.get("questions", []):
        row = _bq_sidecar_row(root, corpus_root, q)
        mark = {"answered": "✓", "draft-only": "◐", "no-answer": "○", "not-implemented": "·"}[row["status"]]
        print(f"{mark} {q['id']:6s} [{q['category']}] {row['status']:15s} {q['question'][:80]}")
    return 0


def main(argv=None):
    p = argparse.ArgumentParser(prog="commercial.py", description=__doc__)
    p.add_argument("--root", default=DEFAULT_ROOT)
    p.add_argument("--corpus-root", default=DEFAULT_CORPUS)
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("answer", help="run a BQ's computation into a new draft edition")
    s.add_argument("bq")
    s.set_defaults(fn=cmd_answer)

    s = sub.add_parser("lint", help="claim lint an edition (default: latest draft, else latest)")
    s.add_argument("bq")
    s.add_argument("--edition")
    s.set_defaults(fn=cmd_lint)

    s = sub.add_parser("approve", help="approve an edition (gated: lint + freshness must pass)")
    s.add_argument("bq")
    s.add_argument("--edition")
    s.add_argument("--by", required=True)
    s.add_argument("--verify-note", help="adversarial-verification verdict reference")
    s.set_defaults(fn=cmd_approve)

    s = sub.add_parser("render", help="write .console/commercial-index.json sidecar")
    s.set_defaults(fn=cmd_render)

    s = sub.add_parser("check", help="editions integrity + approved lint + corpus chain")
    s.set_defaults(fn=cmd_check)

    s = sub.add_parser("catalog", help="question roster with answer status")
    s.set_defaults(fn=cmd_catalog)

    args = p.parse_args(argv)
    try:
        return args.fn(args)
    except CommercialError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
