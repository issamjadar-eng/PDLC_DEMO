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
    # recency = creation time, NOT name: suffix reuse after a discarded draft can
    # make lexicographic order lie about which edition is newest
    out.sort(key=lambda e: (e.get("created_at") or "", e.get("edition") or ""))
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
    return eds[-1]  # newest by created_at (draft or approved)


# ---------------------------------------------------------------- lint

LINT_CHECKS = [
    ("artifacts", "Edition artifacts",
     "report.md and data.json exist for this edition"),
    ("numeric-coverage", "Numeric-claim coverage",
     "every numeric claim in the report carries a resolvable marker on its line"),
    ("marker-resolution", "Marker resolution",
     "every cited marker resolves — pinned snapshot on disk, active assumption, computed series, config file, active waiver"),
    ("estimation-language", "Estimation language",
     "estimation words (estimated / likely / modeled / approximately …) cite a stated assumption record"),
    ("pin-freshness", "Pin freshness",
     "every pinned snapshot is within its dataset's max_age_days, or a cited waiver is active"),
    ("series-hygiene", "Series hygiene",
     "every data.json series declares a valid evidence class and its provenance"),
    ("derivation-chain", "Derivation chain",
     "every derived series declares HOW it was derived — a method and its inputs (src/derived/config markers), so the data chain is walkable"),
    ("plan-currency", "Plan currency",
     "the question has an analysis plan and this edition was computed under its current version — a drifted or missing plan is called out, and intent-honoring is verified by an agent intent-check"),
]


def plan_path(root: Path, bq: str) -> Path:
    return root / "plans" / f"{bq}.md"


def plan_hash(root: Path, bq: str):
    p = plan_path(root, bq)
    return sha256_file(p) if p.exists() else None


def lint_edition(root: Path, corpus_root: Path, bq: str, ed: dict):
    """Returns (errors, warnings, detail). Deterministic; no LLM judgment.
    detail = {"references": [...], "freshness": [...], "checks": [...]} — the audit
    inventory, with findings itemized per named check."""
    errors, warnings = [], []
    detail = {"references": [], "freshness": []}
    _refs = {}
    _findings = {cid: [] for cid, _, _ in LINT_CHECKS}

    def err(cid, msg):
        errors.append(msg)
        _findings[cid].append({"severity": "error", "message": msg})

    def warn(cid, msg):
        warnings.append(msg)
        _findings[cid].append({"severity": "warning", "message": msg})

    def _ref(kind, value, resolved, note):
        _refs[(kind, value)] = {"kind": kind, "value": value, "resolved": resolved, "note": note}

    def _finish():
        detail["references"] = sorted(_refs.values(), key=lambda r: (r["kind"], r["value"]))
        detail["checks"] = []
        for cid, name, desc in LINT_CHECKS:
            fs = _findings[cid]
            status = "fail" if any(f["severity"] == "error" for f in fs) else \
                ("warn" if fs else "pass")
            detail["checks"].append({"id": cid, "name": name, "description": desc,
                                     "status": status, "findings": fs})
        return errors, warnings, detail

    edir = bq_dir(root, bq) / ed["edition"]
    report, datap = edir / "report.md", edir / "data.json"
    if not report.exists():
        err("artifacts", f"{bq}@{ed['edition']}: report.md missing")
    if not datap.exists():
        err("artifacts", f"{bq}@{ed['edition']}: data.json missing")
    if errors:
        return _finish()
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
                    err("marker-resolution", f"L{n}: malformed src marker: {val}")
                    _ref(kind, val, False, "malformed marker")
                    continue
                ds, snap = val.rsplit("@", 1)
                if ds not in pins:
                    err("marker-resolution", f"L{n}: [src: {val}] cites unpinned dataset {ds}")
                    _ref(kind, val, False, "dataset not pinned by this edition")
                elif pins[ds] != snap:
                    err("marker-resolution", f"L{n}: [src: {val}] cites snapshot {snap} but edition pins {pins[ds]}")
                    _ref(kind, val, False, f"edition pins {pins[ds]}")
                elif not (corpus_root / ds / "snapshots" / snap).is_dir():
                    err("marker-resolution", f"L{n}: [src: {val}] snapshot does not exist on disk")
                    _ref(kind, val, False, "snapshot missing on disk")
                else:
                    _ref(kind, val, True, "pinned immutable snapshot present on disk")
            elif kind == "assume":
                rec = assumption_record(corpus_root, val)
                if rec is None:
                    err("marker-resolution", f"L{n}: [assume: {val}] record not found in corpus")
                    _ref(kind, val, False, "record not found")
                elif rec.get("status") != "active":
                    err("marker-resolution", f"L{n}: [assume: {val}] status is {rec.get('status')} (must be active)")
                    _ref(kind, val, False, f"status {rec.get('status')}")
                else:
                    _ref(kind, val, True, f"active assumption ({rec.get('confidence', '?')} confidence)")
            elif kind == "derived":
                if val not in series_ids:
                    err("marker-resolution", f"L{n}: [derived: {val}] not present in data.json series/verdicts")
                    _ref(kind, val, False, "not in data.json")
                else:
                    _ref(kind, val, True, "computed series/verdict in this edition's data.json")
            elif kind == "config":
                if not (Path(val).exists() or (root / val).exists()):
                    err("marker-resolution", f"L{n}: [config: {val}] file not found")
                    _ref(kind, val, False, "file not found")
                else:
                    _ref(kind, val, True, "versioned configuration file present")
            elif kind == "waived":
                rec = waiver_record(corpus_root, val)
                if rec is None or rec.get("status") != "active" or \
                        dt.date.fromisoformat(str(rec["expires"])) < dt.date.today():
                    err("marker-resolution", f"L{n}: [waived: {val}] waiver missing, inactive, or expired")
                    _ref(kind, val, False, "waiver missing/inactive/expired")
                else:
                    waived_ids.add(val)
                    _ref(kind, val, True, f"active waiver, expires {rec.get('expires')}")
        # numeric-claim rule: strip markers + exempt tokens; leftover digits need a marker
        stripped = MARKER_RE.sub("", line)
        stripped = EXEMPT_TOKEN_RE.sub("", stripped)
        if re.search(r"\d", stripped) and not markers:
            err("numeric-coverage",
                f"L{n}: numeric claim without a [src|assume|derived|config] marker: {line.strip()[:80]}")
        # estimation language rule
        if ESTIMATION_RE.search(MARKER_RE.sub("", line)) and not any(k == "assume" for k, _ in markers):
            warn("estimation-language", f"L{n}: estimation language without [assume: A-NNN]: {line.strip()[:80]}")

    # freshness of pins
    for ds, snap in pins.items():
        max_age = int(corpus_dataset_cfg(corpus_root, ds).get("max_age_days", 90))
        age = snapshot_age_days(snap)
        band = "stale" if age > max_age else ("aging" if age > max_age * 0.75 else "fresh")
        detail["freshness"].append({"dataset": ds, "snapshot": snap, "age_days": age,
                                    "max_age_days": max_age, "band": band,
                                    "waived": bool(waived_ids and band == "stale")})
        if age > max_age and not waived_ids:
            err("pin-freshness",
                f"pin {ds}@{snap} is STALE ({age}d > {max_age}d) and report carries no [waived: W-NNN]")

    # plan currency: does a plan exist, and was this edition computed under it?
    pp = plan_path(root, bq)
    pinned = (ed.get("plan") or {}).get("sha256")
    if not pp.exists():
        warn("plan-currency", f"no analysis plan at plans/{bq}.md — run plan-init to scaffold one")
        detail["plan"] = {"path": f"plans/{bq}.md", "status": "missing", "pinned": pinned, "current": None}
    else:
        cur = sha256_file(pp)
        if not pinned:
            warn("plan-currency", "edition predates plan pinning — re-answer to pin the plan version")
            detail["plan"] = {"path": f"plans/{bq}.md", "status": "unpinned", "pinned": None, "current": cur}
        elif pinned != cur:
            warn("plan-currency", "plan has CHANGED since this edition was computed — review intent and re-answer")
            detail["plan"] = {"path": f"plans/{bq}.md", "status": "drifted", "pinned": pinned, "current": cur}
        else:
            detail["plan"] = {"path": f"plans/{bq}.md", "status": "in-sync", "pinned": pinned, "current": cur}

    # data.json series must carry evidence_class + provenance; while here, build the
    # data-availability inventory — what we HAVE, what rests on a stated ASSUMPTION,
    # and what is MISSING (the gap stated, never papered over)
    avail = {"have": [], "assumed": [], "missing": []}
    for s in data.get("series", []):
        ec = s.get("evidence_class")
        if ec not in ("measured", "derived", "assumed", "unavailable"):
            err("series-hygiene", f"data.json series {s.get('id')}: bad evidence_class {s.get('evidence_class')!r}")
        if not s.get("provenance"):
            err("series-hygiene", f"data.json series {s.get('id')}: missing provenance")
        prov = s.get("provenance") or {}
        src = (f"{prov['dataset']}@{prov.get('snapshot', '?')}" if prov.get("dataset")
               else prov.get("assumption") or prov.get("note", ""))
        entry = {"what": s.get("label", s.get("id", "")), "series": s.get("id"),
                 "evidence_class": ec, "source": src}
        deriv = s.get("derivation")
        if ec == "derived":
            if not (deriv and deriv.get("method") and deriv.get("inputs")):
                err("derivation-chain",
                    f"data.json series {s.get('id')}: evidence_class 'derived' without a derivation "
                    f"{{method, inputs[]}} — the chain must be stated")
            else:
                entry["derivation"] = deriv
        if ec in ("measured", "derived"):
            avail["have"].append(entry)
        elif ec == "assumed":
            avail["assumed"].append(entry)
        elif ec == "unavailable":
            entry["note"] = prov.get("note", "no data acquired")
            avail["missing"].append(entry)
    # assumptions cited anywhere in the report also count as substituted data
    for (kind, val), r in _refs.items():
        if kind == "assume" and not any(a.get("source") == val for a in avail["assumed"]):
            avail["assumed"].append({"what": f"figure(s) citing {val}", "series": None,
                                     "evidence_class": "assumed", "source": val})
    detail["data_availability"] = avail
    return _finish()


def write_quality(root: Path, corpus_root: Path, bq: str, ed: dict,
                  errors, warnings, detail):
    """Write/refresh the edition's quality.json audit surface. Machine-generated
    lint/reference/freshness sections are replaced; agent-recorded verifications
    are preserved across rewrites."""
    edir = bq_dir(root, bq) / ed["edition"]
    qpath = edir / "quality.json"
    existing = {}
    if qpath.exists():
        try:
            existing = json.loads(qpath.read_text())
        except json.JSONDecodeError:
            existing = {}
    q = {
        "bq": bq, "edition": ed["edition"], "generated_at": now_iso(),
        "lint": {"status": "fail" if errors else "pass",
                 "errors": errors, "warnings": warnings,
                 "checks": detail.get("checks", [])},
        "references": detail.get("references", []),
        "freshness": detail.get("freshness", []),
        "data_availability": detail.get("data_availability", {"have": [], "assumed": [], "missing": []}),
        "plan": detail.get("plan"),
        "verifications": existing.get("verifications", []),
    }
    qpath.write_text(json.dumps(q, indent=1))
    return q


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
            # never reuse a freed suffix — max+1 keeps name order = recency order
            used = [int(p.name.rsplit(".", 1)[1]) for p in bq_dir(root, args.bq).iterdir()
                    if p.is_dir() and p.name.startswith(edition + ".")
                    and p.name.rsplit(".", 1)[1].isdigit()]
            edition = f"{edition}.{(max(used) + 1) if used else 2}"
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
    ph = plan_hash(root, args.bq)
    if ph:
        ed["plan"] = {"path": f"plans/{args.bq}.md", "sha256": ph}
    dump_yaml(ed, edir / "edition.yml")
    errors, warnings, detail = lint_edition(root, corpus_root, args.bq, ed)
    write_quality(root, corpus_root, args.bq, ed, errors, warnings, detail)
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
    errors, warnings, detail = lint_edition(root, corpus_root, args.bq, ed)
    write_quality(root, corpus_root, args.bq, ed, errors, warnings, detail)
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
    errors, warnings, detail = lint_edition(root, corpus_root, args.bq, ed)
    write_quality(root, corpus_root, args.bq, ed, errors, warnings, detail)
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
        "latest_edition": eds[-1]["edition"] if eds else None,
        "editions": [{"edition": e["edition"], "status": e["status"]} for e in eds],
        "assumptions": [], "freshness": None, "verdict_headline": None,
        "evidence_class": None, "report_path": None, "data_path": None,
    }
    show = eds[-1] if eds else None  # newest edition carries the card's verdict/badges
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
                errors, _, detail = lint_edition(root, corpus_root, q["id"], ed)
                # grandfather: lint rules added AFTER an edition was approved must not
                # retroactively fail the immutable record — new rules gate the NEXT
                # approval. derivation-chain (added post-launch) is advisory here.
                grandfathered = {f["message"] for c in detail.get("checks", [])
                                 if c["id"] in ("derivation-chain",) for f in c["findings"]}
                failures.extend(f"{q['id']}@{ed['edition']}: {e}" for e in errors
                                if e not in grandfathered)
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


def cmd_audit(args):
    """(Re)generate quality.json for an edition without recomputing the answer."""
    root, corpus_root = Path(args.root), Path(args.corpus_root)
    ed = find_edition(root, args.bq, args.edition)
    if not ed:
        raise CommercialError(f"{args.bq}: no editions")
    errors, warnings, detail = lint_edition(root, corpus_root, args.bq, ed)
    q = write_quality(root, corpus_root, args.bq, ed, errors, warnings, detail)
    print(f"[{args.bq}@{ed['edition']}] quality.json written — lint {q['lint']['status']}, "
          f"{len(q['references'])} reference(s), {len(q['freshness'])} pin(s), "
          f"{len(q['verifications'])} verification(s) on record")
    return 0


def cmd_record_verification(args):
    """Record an agent-produced verification / red-team verdict into quality.json.
    The engine can't generate this deterministically — an independent agent re-derives
    or attacks the report; this files the outcome as auditable evidence."""
    root, corpus_root = Path(args.root), Path(args.corpus_root)
    ed = find_edition(root, args.bq, args.edition)
    if not ed:
        raise CommercialError(f"{args.bq}: no editions")
    edir = bq_dir(root, args.bq) / ed["edition"]
    qpath = edir / "quality.json"
    if not qpath.exists():
        errors, warnings, detail = lint_edition(root, corpus_root, args.bq, ed)
        write_quality(root, corpus_root, args.bq, ed, errors, warnings, detail)
    q = json.loads(qpath.read_text())
    q.setdefault("verifications", []).append({
        "type": args.type, "verdict": args.verdict, "by": args.by,
        "at": now_iso(), "summary": args.summary,
        "detail_ref": args.detail_ref,
    })
    qpath.write_text(json.dumps(q, indent=1))
    print(f"[{args.bq}@{ed['edition']}] recorded {args.type}: {args.verdict} (by {args.by})")
    return 0


CATEGORY_APPROACH_HINTS = {
    "field-ops": "State the operational definitions up front: what counts as completed / attempted / "
                 "failed, which date anchors the trailing windows, and which denominator each rate uses.",
    "field-safety": "State the denominator policy explicitly (installed-base source), the threshold "
                    "provenance (risk file vs stand-in), and how reporting lag / propensity are handled.",
    "board": "State which figures are contracted vs modeled vs aspiration, and the allocation "
             "methodology behind any cross-line comparison.",
    "market": "State the share/TCO estimation method and every place competitor data is assumed "
              "rather than public.",
    "roadmap": "State the public signals used (clearances, filings), the mapping judgment from signal "
               "to roadmap lane, and the scope limits of the product codes searched.",
    "economics": "State cost-allocation rules and which side (ours vs customer) each figure sits on.",
}


def cmd_plan_init(args):
    """Scaffold the question's analysis plan (prose contract: goal / approach /
    assumptions / data / assertions & limits). User-owned after creation — never
    overwritten; editions pin the plan's hash so drift is visible."""
    root = Path(args.root)
    cfg = load_config(root)
    q = bq_entry(cfg, args.bq)
    pp = plan_path(root, args.bq)
    if pp.exists():
        print(f"plan already exists: {pp} (user-owned; not overwritten)")
        return 0
    pp.parent.mkdir(exist_ok=True)
    hints = CATEGORY_APPROACH_HINTS.get(q.get("category", ""), "State definitions, windows, and denominators explicitly.")
    deps = "".join(f"- `{d}`\n" for d in q.get("corpus_deps", [])) or "- (none registered yet)\n"
    exps = "".join(f"- **{e['id']}** — {e['statement']} _(basis: {e['basis']})_\n"
                   for e in q.get("expectations", [])) or "- (none declared yet)\n"
    pp.write_text(f"""# Analysis plan — {args.bq}

_The analysis contract for this question: what the answer is FOR, how it is computed,
what it assumes, and what it does — and does not — assert. User-owned prose: edit
freely. Editions pin this file's hash; the quality audit calls out drift, and an agent
intent-check verifies the computed answer honors this plan._

## Question

{q.get('question')}

**Asked by**: {', '.join(q.get('personas', []))} · **cadence**: {q.get('cadence', '')}

## Goal — the decision this answer serves

[Edit: what decision changes based on this answer, and who makes it.]

## Approach

{hints}

[Edit: datasets, computations, definitions — the method a reviewer must know to judge the answer.]

## Data

Registered corpus dependencies:
{deps}
[Edit: data we have vs data we still need; how gaps are handled (stated, never faked).]

## Assumptions & expectations

{exps}
[Edit: what we assume where data does not exist, and which expectations the actuals are judged against.]

## Assertions & limits

[Edit: what this answer claims to establish — and explicitly what it does NOT
(comparisons it cannot support, precision it does not have, decisions it does not make).]
""")
    print(f"plan scaffolded: {pp} — edit freely; re-answer {args.bq} to pin it")
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

    s = sub.add_parser("audit", help="(re)generate an edition's quality.json audit surface")
    s.add_argument("bq")
    s.add_argument("--edition")
    s.set_defaults(fn=cmd_audit)

    s = sub.add_parser("record-verification", help="file an agent-produced verification/red-team verdict")
    s.add_argument("bq")
    s.add_argument("--edition")
    s.add_argument("--type", required=True,
                   choices=["adversarial-verify", "red-team", "reference-audit", "human-review", "intent-check"])
    s.add_argument("--verdict", required=True)
    s.add_argument("--by", required=True)
    s.add_argument("--summary", required=True)
    s.add_argument("--detail-ref", help="path to the full dossier/report")
    s.set_defaults(fn=cmd_record_verification)

    s = sub.add_parser("plan-init", help="scaffold a question's user-owned analysis plan")
    s.add_argument("bq")
    s.set_defaults(fn=cmd_plan_init)

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
