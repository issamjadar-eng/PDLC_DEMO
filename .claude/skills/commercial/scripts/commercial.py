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
SCHEMA_VERSION = "1.5"

MARKER_RE = re.compile(r"\[(src|assume|derived|config|waived):\s*([^\]]+?)\s*\]")
# tokens that contain digits but are identifiers/dates, not numeric claims
EXEMPT_TOKEN_RE = re.compile(
    r"[A-Z]{1,2}Q-\d+|A-\d{3}|W-\d{3}|C-\d{4}-\d{2}|\d{4}-\d{2}-\d{2}(?:\.\d+)?|PP\d+|PE-\d+|S-[A-Z]+-\d+|K\d{6}"
    r"|E-\d+(?:\.\d+)?|FY\d{4}|\d{4}-Q[1-4]|\d{4}-H[12]|510\(k\)"
)
ESTIMATION_RE = re.compile(r"\b(estimated?|likely|approximately|roughly|assumed?|modeled)\b", re.I)


def project_lint_cfg(root: Path) -> dict:
    """Optional project-side lint extensions — commercial.yml `lint:` block:
      lint:
        exempt_patterns: ["<regex>", ...]        # extra digit-bearing identifier tokens
        estimation_exempt_terms: [modeled, ...]  # plan-defined vocabulary the
                                                 # estimation-language check ignores
    Extensions only relax the lint (exempt more) — they can never add findings."""
    try:
        cfg = load_config(root)
    except CommercialError:
        return {}
    lint = cfg.get("lint") or {}
    out = {"exempt_res": [], "estimation_exempt": set()}
    for pat in lint.get("exempt_patterns", []) or []:
        try:
            out["exempt_res"].append(re.compile(pat))
        except re.error:
            sys.stderr.write(f"warning: lint.exempt_patterns entry is not a valid regex, ignored: {pat}\n")
    out["estimation_exempt"] = {str(w).lower() for w in lint.get("estimation_exempt_terms", []) or []}
    return out


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

def catalog_path(root: Path) -> Path:
    """The domain's question catalog. `commercial.yml` is the historical name and
    still wins when present; any other domain root (docs/project/finance/,
    docs/project/manufacturing/, ...) names its catalog after its folder
    (`finance.yml`). One engine, N domains — the catalog name is the only thing
    that varies, and it is derived, never configured."""
    for name in ("commercial.yml", f"{root.name}.yml"):
        if (root / name).exists():
            return root / name
    raise CommercialError(f"no catalog at {root}/commercial.yml or {root}/{root.name}.yml")


def load_config(root: Path) -> dict:
    return load_yaml(catalog_path(root))


def domain_block(cfg: dict, root: Path) -> dict:
    """Identity of the domain this root answers for — emitted into the sidecar so
    the console can render one tab per domain without a hard-coded roster.
    Defaults derive from the folder name; a catalog `domain:` block overrides."""
    d = dict(cfg.get("domain") or {})
    key = root.name
    return {
        "key": key,
        "name": d.get("name") or key.replace("-", " ").title(),
        "nav_title": d.get("nav_title") or d.get("name") or key.replace("-", " ").title(),
        "tagline": d.get("tagline") or "business questions answered with data",
        "icon": d.get("icon") or key,
        "id_prefix": d.get("id_prefix") or (cfg.get("questions") or [{}])[0].get("id", "BQ-").split("-")[0],
    }


def sidecar_name(root: Path) -> str:
    """`.console/<domain>-index.json` — `commercial-index.json` for the historical
    root, `finance-index.json` for docs/project/finance/, etc."""
    return f"{root.name}-index.json"


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


# ---------------------------------------------------------------- code quality (soft gate)
#
# Audit layer for the PROJECT-SIDE analysis code: per-BQ modules, the shared
# computations.py, and corpus dataset generators (gen.py). Deterministic checks
# (static lint, poison-pattern scan, determinism replay) plus AI-review records
# live in an engine-managed store; `answer` pins the exact code bytes an edition
# was computed by. The gate is SOFT: statuses render as badges in quality.json /
# the sidecar and are printed by approve/check, but nothing ever blocks on them.
# The engines themselves (commercial.py, corpus.py) are out of scope — they are
# reviewed at registry level, not per project.

CQ_STORE_REL = "code-quality/records.yml"

CQ_POISON_RULES = [
    # (rule id, severity, regex) — poison patterns for deterministic analysis code.
    # error-severity hits fail the scan; warning-severity hits surface but don't.
    ("no-clocks", "error",
     re.compile(r"datetime\.now\s*\(|\bdate\.today\s*\(|\btime\.time\s*\(")),
    ("unseeded-random-ctor", "error", re.compile(r"\brandom\.Random\(\s*\)")),
    ("unseeded-random-call", "error",
     re.compile(r"\brandom\.(?:random|randint|choice|choices|shuffle|uniform|randrange|sample|gauss)\s*\(")),
    ("no-network", "error",
     re.compile(r"^\s*(?:import|from)\s+[\w., ]*\b(?:requests|urllib|http\.client|socket)\b")),
    ("abs-path-open", "warning", re.compile(r"open\(\s*[\"']/")),
]

CQ_STATUS_ORDER = ["checks-failed", "review-outdated", "unreviewed", "reviewed-current"]


def cq_store_path(root: Path) -> Path:
    return root / CQ_STORE_REL


def load_cq_store(root: Path) -> dict:
    """No store file is a valid state (nothing audited yet) — never an error."""
    p = cq_store_path(root)
    if not p.exists():
        return {"artifacts": {}}
    try:
        d = load_yaml(p) or {}
    except yaml.YAMLError:
        sys.stderr.write(f"warning: unreadable {p} — treating as empty store\n")
        return {"artifacts": {}}
    d.setdefault("artifacts", {})
    return d


def save_cq_store(root: Path, store: dict):
    p = cq_store_path(root)
    p.parent.mkdir(parents=True, exist_ok=True)
    dump_yaml(store, p)


def artifact_role(path: str) -> str:
    if path.startswith("corpus:"):
        return "generator"
    if path == "computations.py":
        return "shared"
    return "module"


def resolve_artifact_file(root: Path, corpus_root: Path, path: str) -> Path:
    if path.startswith("corpus:"):
        return corpus_root / path[len("corpus:"):]
    return root / path


def bq_module_relpath(bq: str) -> str:
    return "bq_modules/" + bq.lower().replace("-", "_") + ".py"


def compute_code_artifacts(root: Path, corpus_root: Path, q: dict):
    """The code artifacts behind a question's computation, at their CURRENT hashes:
    the per-BQ module (when it exists), the shared computations.py (always — helpers
    and inline computations), and each corpus dep's generator gen.py (when present).
    Paths are commercial-root-relative; generators use the corpus:<ds>/gen.py form."""
    out = []
    mod = root / bq_module_relpath(q["id"])
    if mod.exists():
        out.append({"path": bq_module_relpath(q["id"]), "sha256": sha256_file(mod)})
    comp = root / "computations.py"
    if comp.exists():
        out.append({"path": "computations.py", "sha256": sha256_file(comp)})
    for ds in q.get("corpus_deps", []) or []:
        g = corpus_root / ds / "gen.py"
        if g.exists():
            out.append({"path": f"corpus:{ds}/gen.py", "sha256": sha256_file(g)})
    return out


def edition_code_artifacts(root: Path, corpus_root: Path, q: dict, ed):
    """(artifacts, derived_from_current_files). Editions pinned by `answer` carry
    code_artifacts in edition.yml; older editions (and no-edition questions)
    degrade to current file hashes — flagged with a note, never an error."""
    arts = (ed or {}).get("code_artifacts")
    if arts:
        return arts, False
    return compute_code_artifacts(root, corpus_root, q), True


def cq_entry_for(store: dict, path: str, sha: str):
    """Newest store entry for (path, sha) — newest entry per sha wins."""
    entries = ((store.get("artifacts") or {}).get(path) or {}).get("entries") or []
    for e in reversed(entries):
        if e.get("sha256") == sha:
            return e
    return None


def cq_review_history(store: dict, path: str, current_sha: str, cap: int = 5):
    """Prior reviews of the same artifact path filed against OTHER shas —
    superseded code generations (schema 1.3, purely additive). Newest first
    (store entries append in time order), newest review per entry, capped.
    This is where the original pre-fix review findings stay visible after the
    code moves to a new (approved) sha."""
    entries = ((store.get("artifacts") or {}).get(path) or {}).get("entries") or []
    hist = []
    for e in reversed(entries):
        if e.get("sha256") == current_sha or not e.get("reviews"):
            continue
        rv = e["reviews"][-1]
        hist.append({"sha256_12": (e.get("sha256") or "")[:12],
                     "date": rv.get("date") or e.get("date"),
                     "verdict": rv.get("verdict"), "by": rv.get("by"),
                     "summary": rv.get("summary"),
                     "findings": rv.get("findings", []),
                     "detail_ref": rv.get("detail_ref"), "superseded": True})
        if len(hist) >= cap:
            break
    return hist


def cq_upsert(store: dict, path: str, sha: str, **fields):
    """Update the entry for (path, sha), creating it if absent. Only non-None
    fields are written, so a partial run never clobbers earlier check results."""
    art = store.setdefault("artifacts", {}).setdefault(path, {"entries": []})
    entry = None
    for e in reversed(art["entries"]):
        if e.get("sha256") == sha:
            entry = e
            break
    if entry is None:
        entry = {"sha256": sha, "date": today(), "reviews": []}
        art["entries"].append(entry)
    entry["date"] = today()
    for k, v in fields.items():
        if v is not None:
            entry[k] = v
    return entry


def cq_static_lint(f: Path, label: str) -> dict:
    """pyflakes when importable, else a py_compile syntax check — tool recorded."""
    import importlib.util
    tool = "pyflakes" if importlib.util.find_spec("pyflakes") else "py_compile"
    proc = subprocess.run([sys.executable, "-m", tool, str(f)],
                          capture_output=True, text=True)
    findings = [ln.replace(str(f), label) for ln in (proc.stdout + proc.stderr).splitlines()
                if ln.strip()]
    return {"status": "fail" if proc.returncode else "pass", "tool": tool, "findings": findings}


def cq_poison_scan(f: Path) -> dict:
    """Regex scan for the project poison patterns, with line numbers. Generators
    legitimately use SEEDED randomness — a file that seeds the global RNG
    (random.seed(...)) is not flagged for bare random.* calls; random.Random()
    with no seed argument is always flagged."""
    text = f.read_text()
    seeded = "random.seed(" in text
    hits, worst = [], "pass"
    for n, line in enumerate(text.splitlines(), 1):
        if line.lstrip().startswith("#"):
            continue
        for rid, sev, rx in CQ_POISON_RULES:
            if rid == "unseeded-random-call" and seeded:
                continue
            if rx.search(line):
                hits.append({"rule": rid, "severity": sev, "line": n,
                             "text": line.strip()[:100]})
                if sev == "error":
                    worst = "fail"
                elif worst == "pass":
                    worst = "warn"
    return {"status": worst, "hits": hits}


def cq_determinism(root: Path, corpus_root: Path, q: dict) -> dict:
    """Replay the question's computation twice against the latest edition's pins
    into two temp dirs and byte-compare report.md + data.json. Proof, not vibes.
    (There should be no timestamp fields in either file — a diff is a failure.)"""
    import tempfile
    ed = find_edition(root, q["id"])
    if not ed or not ed.get("pins"):
        return {"status": "not-run", "method": "no edition pins available to replay"}
    method = (f"double-run byte-compare of report.md+data.json replaying "
              f"edition {ed['edition']} pins")
    try:
        with tempfile.TemporaryDirectory() as t1, tempfile.TemporaryDirectory() as t2:
            for t in (t1, t2):
                (Path(t) / "pins.json").write_text(json.dumps(ed["pins"], indent=1))
                cmd = q["computation"].format(bq=q["id"],
                                              corpus_root=str(corpus_root.resolve()),
                                              out=str(Path(t)))
                proc = subprocess.run(cmd, shell=True, cwd=str(root),
                                      capture_output=True, text=True)
                if proc.returncode != 0:
                    return {"status": "fail",
                            "method": method + f" — replay run failed ({proc.returncode}): "
                                               f"{(proc.stderr or '').strip()[-200:]}"}
            for fname in ("report.md", "data.json"):
                a, b = Path(t1) / fname, Path(t2) / fname
                if not (a.exists() and b.exists()):
                    return {"status": "fail", "method": method + f" — replay did not produce {fname}"}
                if a.read_bytes() != b.read_bytes():
                    return {"status": "fail", "method": method + f" — {fname} differs between runs"}
    except (KeyError, OSError) as e:
        return {"status": "not-run", "method": method + f" — replay error: {e}"}
    return {"status": "pass", "method": method}


def code_quality_block(root: Path, corpus_root: Path, q: dict, ed):
    """The per-question `code:` block (quality.json + sidecar, schema 1.3).
    Per edition-pinned artifact: checks + the newest review (current = review filed
    against the pinned sha) + `review_history` — prior reviews filed against
    superseded shas of the same path (schema 1.3, additive). Question-level status ladder:
    checks-failed > review-outdated > unreviewed > reviewed-current.
    SOFT GATE — consumed as badges only; nothing blocks on it."""
    store = load_cq_store(root)
    arts, derived = edition_code_artifacts(root, corpus_root, q, ed)
    if not arts:
        return None
    rows = []
    any_fail = any_outdated = any_unreviewed = False
    for a in arts:
        path, sha = a["path"], a["sha256"]
        entry = cq_entry_for(store, path, sha)
        checks = {k: (entry or {}).get(k) for k in ("static_lint", "poison_scan", "determinism")}
        if any(c and c.get("status") == "fail" for c in checks.values()):
            any_fail = True
        review, current, rv = None, False, None
        if entry and entry.get("reviews"):
            rv, current = entry["reviews"][-1], True
        else:
            entries = ((store.get("artifacts") or {}).get(path) or {}).get("entries") or []
            for e in reversed(entries):
                if e.get("reviews"):
                    rv = e["reviews"][-1]
                    break
        if rv:
            review = {"verdict": rv.get("verdict"), "by": rv.get("by"), "date": rv.get("date"),
                      "current": current, "findings": rv.get("findings", []),
                      "detail_ref": rv.get("detail_ref")}
            if not current:
                any_outdated = True
        else:
            any_unreviewed = True
        rows.append({"path": path, "sha256_12": sha[:12], "role": artifact_role(path),
                     "static_lint": checks["static_lint"], "poison_scan": checks["poison_scan"],
                     "determinism": checks["determinism"], "review": review,
                     "review_history": cq_review_history(store, path, sha)})
    status = ("checks-failed" if any_fail else "review-outdated" if any_outdated
              else "unreviewed" if any_unreviewed else "reviewed-current")
    block = {"status": status, "artifacts": rows}
    if derived:
        block["note"] = ("no edition — status computed from current file hashes" if not ed
                         else "edition predates code pinning — status computed from current file hashes")
    return block


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


# ------------------------------------------------------- verification plan (declared gates)
#
# A plan's `## Verification plan` section DECLARES the quality/audit checks the
# analysis commits to, as checkbox lines `- [ ] <gate> — <note>`. The literal
# checkbox stays `[ ]` forever: done-marks are COMPUTED from the edition's actual
# records (lint results, filed verification records, code-quality status) — never
# hand-ticked. Plans are hash-pinned by editions, so ticking a box would register
# as artificial plan drift; this mirrors the expectations declared-vs-actual
# pattern. A plan without the section is grandfathered: verification_plan: null.

VP_MACHINE_GATES = ("claim-lint", "pin-freshness", "plan-currency", "code-audit")
VP_AGENT_GATES = ("adversarial-verify", "red-team", "intent-check",
                  "reference-audit", "human-review")

VP_HEADING_RE = re.compile(r"^##\s+verification\s+plan\s*$", re.I)
# `- [ ] gate-token — free-text note` (checkbox state tolerated but ignored;
# em/en dash, colon, or hyphen accepted as the token/note separator)
VP_ITEM_RE = re.compile(r"^\s*[-*]\s*\[[ xX]\]\s*`?([A-Za-z0-9][\w-]*)`?\s*(?:[—–:-]+\s*(.*?))?\s*$")


def parse_verification_plan(root: Path, bq: str):
    """Parse the plan's `## Verification plan` section. Tolerant by design:
    no plan file or no section -> None (grandfathered, never an error);
    section present -> [{gate, note}] in declaration order."""
    pp = plan_path(root, bq)
    if not pp.exists():
        return None
    in_section, out = False, None
    for line in pp.read_text().splitlines():
        stripped = line.strip()
        if re.match(r"^#{1,2}\s", stripped):
            if VP_HEADING_RE.match(stripped):
                in_section, out = True, []
            elif in_section:
                break  # next h1/h2 ends the section
            continue
        if in_section:
            m = VP_ITEM_RE.match(line)
            if m:
                out.append({"gate": m.group(1), "note": (m.group(2) or "").strip()})
    return out


def vp_gate_kind(gate: str) -> str:
    if gate in VP_MACHINE_GATES:
        return "machine"
    if gate in VP_AGENT_GATES:
        return "agent"
    return "custom"


def verification_plan_block(root: Path, bq: str, quality):
    """The computed checklist for quality.json + the sidecar (schema 1.4):
    [{gate, kind, note, done, evidence}]. `done` is derived from the edition's
    quality record — machine gates from the lint/freshness/plan/code sections,
    agent gates from filed verification records (carried ones included), custom
    gates done: null (declared, completion not machine-computable). Computed
    against the CURRENT plan file; plan drift is separately surfaced by the
    plan-currency check. SOFT everywhere — never blocks anything."""
    gates = parse_verification_plan(root, bq)
    if gates is None:
        return None
    lint = (quality or {}).get("lint") or {}
    vers = (quality or {}).get("verifications") or []
    out = []
    for g in gates:
        gate, kind = g["gate"], vp_gate_kind(g["gate"])
        done, evidence = None, ""
        if kind == "custom":
            evidence = "custom gate — completion not machine-computed (informational)"
        elif quality is None:
            evidence = "no quality record for this edition — run audit"
        elif kind == "machine":
            if gate == "claim-lint":
                done = lint.get("status") == "pass"
                evidence = (f"{len(lint.get('errors', []))} error(s) / "
                            f"{len(lint.get('warnings', []))} warning(s)")
            elif gate == "pin-freshness":
                fr = quality.get("freshness") or []
                done = not any(f.get("band") == "stale" and not f.get("waived") for f in fr)
                bands = {}
                for f in fr:
                    bands[f.get("band")] = bands.get(f.get("band"), 0) + 1
                evidence = ", ".join(f"{n} pin(s) {b}" for b, n in bands.items()) or "no pins"
                if any(f.get("waived") for f in fr):
                    evidence += " (waived)"
            elif gate == "plan-currency":
                st = (quality.get("plan") or {}).get("status")
                done = st == "in-sync"
                evidence = f"plan {st}" if st else "plan status not recorded"
            elif gate == "code-audit":
                st = (quality.get("code") or {}).get("status")
                done = st == "reviewed-current"
                evidence = f"code {st}" if st else "no code-quality record — run code-audit"
        else:  # agent gate: a filed verification record of this type on this edition
            recs = [v for v in vers if v.get("type") == gate]
            if recs:
                v = max(recs, key=lambda r: r.get("at") or "")
                done = True
                evidence = f"{v.get('verdict')} by {v.get('by')}, {(v.get('at') or '')[:10]}"
                if v.get("carried_from_replaced_draft"):
                    evidence += " (carried from replaced draft)"
            else:
                done = False
                evidence = f"no {gate} record filed on this edition"
        out.append({"gate": gate, "kind": kind, "note": g["note"],
                    "done": done, "evidence": evidence})
    return out


def lint_edition(root: Path, corpus_root: Path, bq: str, ed: dict):
    """Returns (errors, warnings, detail). Deterministic; no LLM judgment.
    detail = {"references": [...], "freshness": [...], "checks": [...]} — the audit
    inventory, with findings itemized per named check."""
    errors, warnings = [], []
    detail = {"references": [], "freshness": []}
    _refs = {}
    _findings = {cid: [] for cid, _, _ in LINT_CHECKS}
    lint_cfg = project_lint_cfg(root)
    exempt_res = [EXEMPT_TOKEN_RE] + lint_cfg.get("exempt_res", [])
    est_exempt = lint_cfg.get("estimation_exempt", set())

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
        for rx in exempt_res:
            stripped = rx.sub("", stripped)
        if re.search(r"\d", stripped) and not markers:
            err("numeric-coverage",
                f"L{n}: numeric claim without a [src|assume|derived|config] marker: {line.strip()[:80]}")
        # estimation language rule (project-exempt terms are plan-defined vocabulary)
        est_hits = [m.group(1).lower() for m in ESTIMATION_RE.finditer(MARKER_RE.sub("", line))
                    if m.group(1).lower() not in est_exempt]
        if est_hits and not any(k == "assume" for k, _ in markers):
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
        # a plan without a `## Verification plan` section is grandfathered
        # (verification_plan: null) but nudged — declared gates are the contract
        # the computed done-marks hang on. WARNING, never an error.
        if parse_verification_plan(root, bq) is None:
            warn("plan-currency",
                 f"plans/{bq}.md has no '## Verification plan' section — declare the "
                 f"quality gates this analysis commits to (done-marks are computed, "
                 f"never hand-ticked; see SKILL.md)")

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
        # join-heavy series may pin multiple datasets: provenance {datasets: [{dataset, snapshot}, ...]}
        # is accepted as an alternative to the single {dataset, snapshot} form
        if prov.get("datasets") is not None:
            items = prov.get("datasets") or []
            if not items or any(not (isinstance(d, dict) and d.get("dataset") and d.get("snapshot"))
                                for d in items):
                err("series-hygiene",
                    f"data.json series {s.get('id')}: provenance.datasets must be a non-empty "
                    f"list of {{dataset, snapshot}} entries")
            src = " + ".join(f"{d.get('dataset', '?')}@{d.get('snapshot', '?')}" for d in items)
        else:
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
                  errors, warnings, detail, carry_verifications=None):
    """Write/refresh the edition's quality.json audit surface. Machine-generated
    lint/reference/freshness sections are replaced; agent-recorded verifications
    are preserved across rewrites. `carry_verifications` re-files verification
    records rescued from a replaced same-day draft (each stamped
    carried_from_replaced_draft: true) so filed verdicts survive a re-answer."""
    edir = bq_dir(root, bq) / ed["edition"]
    qpath = edir / "quality.json"
    existing = {}
    if qpath.exists():
        try:
            existing = json.loads(qpath.read_text())
        except json.JSONDecodeError:
            existing = {}
    verifications = existing.get("verifications", [])
    for v in carry_verifications or []:
        v = dict(v)
        v.setdefault("carried_from_replaced_draft", True)
        verifications.append(v)
    q = {
        "bq": bq, "edition": ed["edition"], "generated_at": now_iso(),
        "lint": {"status": "fail" if errors else "pass",
                 "errors": errors, "warnings": warnings,
                 "checks": detail.get("checks", [])},
        "references": detail.get("references", []),
        "freshness": detail.get("freshness", []),
        "data_availability": detail.get("data_availability", {"have": [], "assumed": [], "missing": []}),
        "plan": detail.get("plan"),
        "verifications": verifications,
    }
    # code-quality soft-gate block (schema 1.3) — degrades to None if the catalog
    # can't be read or the question is unknown
    try:
        centry = bq_entry(load_config(root), bq)
        q["code"] = code_quality_block(root, corpus_root, centry, ed)
    except CommercialError:
        q["code"] = None
    # verification-plan checklist (schema 1.4) — declared gates from the plan's
    # `## Verification plan` section with done-marks computed from this record;
    # null when the plan has no section (grandfathered)
    q["verification_plan"] = verification_plan_block(root, bq, q)
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
    carried_verifications = []
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
            # drafts are re-generable until approved — but agent-filed verification
            # records are evidence, not machine output: rescue them before the
            # replaced draft's quality.json is deleted with the edition dir
            old_q = edir / "quality.json"
            if old_q.exists():
                try:
                    carried_verifications = json.loads(old_q.read_text()).get("verifications", [])
                except json.JSONDecodeError:
                    pass
            shutil.rmtree(edir)
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
    # pin the code bytes this edition was computed by (module, shared helpers,
    # dep generators) — purely additive; the code-quality layer resolves against it
    ed["code_artifacts"] = compute_code_artifacts(root, corpus_root, q)
    dump_yaml(ed, edir / "edition.yml")
    errors, warnings, detail = lint_edition(root, corpus_root, args.bq, ed)
    write_quality(root, corpus_root, args.bq, ed, errors, warnings, detail,
                  carry_verifications=carried_verifications)
    if carried_verifications:
        print(f"[{args.bq}@{edition}] carried {len(carried_verifications)} verification record(s) "
              f"from the replaced same-day draft")
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
    qrec = write_quality(root, corpus_root, args.bq, ed, errors, warnings, detail)
    # code-quality status is printed but NEVER gates approval (soft gate)
    try:
        cb = code_quality_block(root, corpus_root, bq_entry(load_config(root), args.bq), ed)
    except CommercialError:
        cb = None
    if cb:
        print(f"[{args.bq}@{ed['edition']}] code-quality: {cb['status']} "
              f"({len(cb['artifacts'])} artifact(s)) — soft gate, informational only")
    # verification-plan status is printed but NEVER gates approval (soft gate,
    # consistent with code-quality): X of Y computable gates satisfied + unmet list
    vp = qrec.get("verification_plan")
    if vp:
        computable = [g for g in vp if g.get("done") is not None]
        met = [g for g in computable if g["done"]]
        line = (f"[{args.bq}@{ed['edition']}] verification plan: {len(met)} of "
                f"{len(computable)} declared gates satisfied")
        n_info = len(vp) - len(computable)
        if n_info:
            line += f" (+{n_info} informational)"
        print(line + " — soft gate, informational only")
        for g in computable:
            if not g["done"]:
                print(f"  unmet {g['gate']}: {g['evidence']}")
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


def _resolve_terms(bq: str, refs, catalog: dict):
    """Resolve a question's `terms:` reference list against the catalog's top-level
    `terms:` dictionary (define once, reference per question). Each entry is either
    a string key into the dictionary or a one-off inline `{term: definition}` map.
    An unresolved key warns to stderr and is skipped — a definition is never
    fabricated by the engine."""
    out = []
    for ref in refs or []:
        if isinstance(ref, dict):
            for term, definition in ref.items():
                out.append({"term": str(term), "definition": str(definition)})
        elif ref in catalog:
            out.append({"term": str(ref), "definition": str(catalog[ref])})
        else:
            sys.stderr.write(f"warning: [{bq}] terms entry '{ref}' not found in the "
                             f"top-level terms dictionary — skipped\n")
    return out


def _bq_sidecar_row(root: Path, corpus_root: Path, q: dict, terms_catalog: dict = None):
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
        # schema 1.1 reader aids (plain-language, timeless — see SKILL.md):
        # explainers keyed by series id or reserved keys question/verdict/expectations,
        # copied verbatim from the catalog; terms resolved against the top-level
        # `terms:` dictionary. Purely additive — 1.0 consumers ignore unknown fields.
        "explainers": q.get("explainers") or {},
        "terms": _resolve_terms(bq, q.get("terms"), terms_catalog or {}),
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
    # schema 1.2+: per-question code-quality block (soft gate — badges only;
    # 1.3 adds per-artifact review_history — reviews on superseded shas)
    row["code"] = code_quality_block(root, corpus_root, q, show) \
        if (show or q.get("computation")) else None
    # schema 1.4: verification-plan checklist for the shown edition — declared
    # gates + done-marks read off the edition's quality.json audit surface
    # (regenerated by answer/lint/audit); null when there is no shown edition
    # or the plan has no `## Verification plan` section (grandfathered)
    row["verification_plan"] = None
    if show:
        qp = bq_dir(root, bq) / show["edition"] / "quality.json"
        quality = None
        if qp.exists():
            try:
                quality = json.loads(qp.read_text())
            except json.JSONDecodeError:
                quality = None
        row["verification_plan"] = verification_plan_block(root, bq, quality)
    return row


def cmd_render(args):
    root, corpus_root = Path(args.root), Path(args.corpus_root)
    cfg = load_config(root)
    terms_catalog = cfg.get("terms") or {}
    rows = [_bq_sidecar_row(root, corpus_root, q, terms_catalog) for q in cfg.get("questions", [])]
    out = {
        "schema_version": SCHEMA_VERSION, "generated": now_iso(),
        "domain": domain_block(cfg, root),
        "categories": cfg.get("categories", []),
        "questions": rows,
    }
    console_dir = root / ".console"
    console_dir.mkdir(exist_ok=True)
    (console_dir / sidecar_name(root)).write_text(json.dumps(out, indent=1))
    n_ans = sum(1 for r in rows if r["status"] == "answered")
    n_draft = sum(1 for r in rows if r["status"] == "draft-only")
    print(f"rendered .console/{sidecar_name(root)} — {len(rows)} questions "
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
    # code-quality soft-gate summary — informational count line, never a failure
    cq_counts = {}
    for q in cfg.get("questions", []):
        if not q.get("computation"):
            continue
        cb = code_quality_block(root, corpus_root, q, find_edition(root, q["id"]))
        if cb:
            cq_counts[cb["status"]] = cq_counts.get(cb["status"], 0) + 1
    if cq_counts:
        print("code-quality (soft gate, non-blocking): " +
              ", ".join(f"{cq_counts[s]} {s}" for s in CQ_STATUS_ORDER if s in cq_counts))
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
    print(f"{root.name} check: GREEN (editions integrity + approved lint + corpus chain)")
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
    report = edir / "report.md"
    q.setdefault("verifications", []).append({
        "type": args.type, "verdict": args.verdict, "by": args.by,
        "at": now_iso(), "summary": args.summary,
        "detail_ref": args.detail_ref,
        # tie the verdict to the byte-state it judged: short sha256 of report.md at filing time
        "report_sha256": sha256_file(report)[:12] if report.exists() else None,
    })
    # a newly filed record can flip a declared agent gate to done — recompute the
    # verification-plan checklist so quality.json stays self-consistent
    q["verification_plan"] = verification_plan_block(root, args.bq, q)
    qpath.write_text(json.dumps(q, indent=1))
    print(f"[{args.bq}@{ed['edition']}] recorded {args.type}: {args.verdict} (by {args.by})")
    return 0


def cmd_code_audit(args):
    """Run the DETERMINISTIC code-quality checks (static lint, poison-pattern scan,
    determinism replay) over a target's artifacts and upsert store entries keyed by
    each file's CURRENT sha. AI reviews are filed separately via record-code-review.
    Soft gate: findings are recorded and printed, exit stays 0."""
    root, corpus_root = Path(args.root), Path(args.corpus_root)
    cfg = load_config(root)
    questions = [q for q in cfg.get("questions", []) if q.get("computation")]
    targets = {}   # path -> resolved file
    det_jobs = []  # (question, owner artifact path for the determinism verdict)
    if args.all:
        qs = questions
    elif args.path:
        qs = []
        f = resolve_artifact_file(root, corpus_root, args.path)
        if not f.exists():
            raise CommercialError(f"artifact not found: {args.path}")
        targets[args.path] = f
        # a per-BQ module maps back to its question for the determinism replay;
        # for shared/generator paths only lint + poison run here
        for q in questions:
            if bq_module_relpath(q["id"]) == args.path:
                det_jobs.append((q, args.path))
    elif args.bq:
        qs = [bq_entry(cfg, args.bq)]
    else:
        raise CommercialError("code-audit needs a BQ id, --path, or --all")
    for q in qs:
        for a in compute_code_artifacts(root, corpus_root, q):
            targets.setdefault(a["path"], resolve_artifact_file(root, corpus_root, a["path"]))
        owner = bq_module_relpath(q["id"])
        if not (root / owner).exists():
            owner = "computations.py"  # inline computation — shared file owns the verdict
        det_jobs.append((q, owner))
    # determinism replays, aggregated per owner artifact (computations.py may own many)
    det_acc = {}
    for q, owner in det_jobs:
        r = cq_determinism(root, corpus_root, q)
        acc = det_acc.setdefault(owner, {"bqs": [], "fails": [], "notruns": []})
        acc["bqs"].append(q["id"])
        if r["status"] == "fail":
            acc["fails"].append(f"{q['id']}: {r['method']}")
        elif r["status"] == "not-run":
            acc["notruns"].append(f"{q['id']}: {r['method']}")
    det_results = {}
    for owner, acc in det_acc.items():
        status = "fail" if acc["fails"] else ("not-run" if acc["notruns"] else "pass")
        method = ("double-run byte-compare of report.md+data.json replaying "
                  "latest-edition pins for " + ", ".join(acc["bqs"]))
        for msg in acc["fails"] + acc["notruns"]:
            method += f"; {msg}"
        det_results[owner] = {"status": status, "method": method}
    store = load_cq_store(root)
    rows = []
    for path in sorted(targets):
        f = targets[path]
        sha = sha256_file(f)
        lint = cq_static_lint(f, path)
        poison = cq_poison_scan(f)
        det = det_results.get(path)
        if det is None and artifact_role(path) == "generator":
            # generators run at acquisition time, not per answer — determinism of
            # their outputs is the corpus tier's concern (seeded gen + hash pins)
            det = {"status": "n/a",
                   "method": "generator — replayed at acquisition time, not by code-audit"}
        cq_upsert(store, path, sha, static_lint=lint, poison_scan=poison, determinism=det)
        rows.append((path, sha[:12], lint, poison, det))
    save_cq_store(root, store)
    print(f"code-audit: {len(rows)} artifact(s) checked — store: {CQ_STORE_REL}")
    for path, sha12, lint, poison, det in rows:
        d = det["status"] if det else "-"
        print(f"  {path:60s} {sha12}  lint:{lint['status']:5s} poison:{poison['status']:5s} "
              f"determinism:{d}")
        for fl in lint["findings"][:5]:
            print(f"      lint: {fl}")
        for h in poison["hits"][:8]:
            print(f"      poison[{h['rule']}/{h['severity']}] L{h['line']}: {h['text']}")
    return 0


def cmd_record_code_review(args):
    """File an AI (or human) code review for an artifact's CURRENT bytes into the
    code-quality store — the review record for the failure classes deterministic
    checks can't see (plan conformance, denominator/basis choices, string-literal
    facts, median/rounding traps, status-set assumptions)."""
    root, corpus_root = Path(args.root), Path(args.corpus_root)
    f = resolve_artifact_file(root, corpus_root, args.path)
    if not f.exists():
        raise CommercialError(f"artifact not found: {args.path}")
    sha = sha256_file(f)
    store = load_cq_store(root)
    findings = []
    for i, spec in enumerate(args.finding or [], 1):
        parts = [s.strip() for s in spec.split("|", 2)]
        if len(parts) != 3:
            raise CommercialError(f"--finding must be 'severity|summary|disposition': {spec}")
        findings.append({"id": f"F-{i}", "severity": parts[0], "summary": parts[1],
                         "disposition": parts[2]})
    checks_pending = not (cq_entry_for(store, args.path, sha) or {}).get("static_lint")
    entry = cq_upsert(store, args.path, sha)
    entry.setdefault("reviews", []).append({
        "verdict": args.verdict, "by": args.by, "date": today(),
        "summary": args.summary, "findings": findings, "detail_ref": args.detail_ref,
    })
    save_cq_store(root, store)
    print(f"[{args.path}@{sha[:12]}] review filed: {args.verdict} (by {args.by}, "
          f"{len(findings)} finding(s))")
    if checks_pending:
        print("  note: deterministic checks have not run for this sha — run code-audit "
              "to complete the entry")
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

## Verification plan

_The quality gates this analysis commits to. Each line declares a gate; the
checkbox stays `[ ]` forever — done-marks are COMPUTED per edition from actual
records (lint results, filed verification records, code-quality status), never
hand-ticked (this plan is hash-pinned; ticking a box would register as plan
drift). Machine gates: claim-lint, pin-freshness, plan-currency, code-audit.
Agent gates: adversarial-verify, red-team, intent-check, reference-audit,
human-review. Any other token is carried as a custom (informational) gate._

- [ ] claim-lint — every numeric claim marker-cited; zero lint errors (every edition)
- [ ] pin-freshness — all pinned snapshots within max_age_days, or a cited active waiver (every edition)
- [ ] plan-currency — the edition was computed under the current version of this plan (every edition)
- [ ] code-audit — deterministic code checks green and the computation reviewed at its pinned bytes (each code change)
- [ ] adversarial-verify — independent pins-only re-derivation of the headline claims (each substantive re-answer)
- [ ] red-team — framing attack on the answer's presentation and emphasis (each substantive re-answer)
""")
    print(f"plan scaffolded: {pp} — edit freely; re-answer {args.bq} to pin it")
    return 0


def cmd_dependents(args):
    """Question ids whose corpus_deps match a dataset name or prefix — the seam a
    scheduled refresh uses to re-answer exactly the questions a re-snapshotted
    dataset feeds (`corpus refresh openfda-*` -> `dependents commercial/openfda-`)."""
    root = Path(args.root)
    cfg = load_config(root)
    needle = args.dataset
    hits = []
    for q in cfg.get("questions", []):
        if not q.get("computation"):
            continue
        deps = q.get("corpus_deps") or []
        if needle == "*" or any(d == needle or d.startswith(needle) for d in deps):
            hits.append(q["id"])
    print("\n".join(hits))
    return 0


def _pack_pick_edition(root: Path, bq: str, allow_draft: bool):
    """Newest APPROVED edition; with --include-drafts, fall back to the newest
    edition of any status (clearly flagged in the pack)."""
    eds = list_editions(root, bq)
    approved = [e for e in eds if e.get("status") == "approved"]
    if approved:
        return approved[-1], False
    if allow_draft and eds:
        return eds[-1], True
    return None, False


def cmd_pack(args):
    """Management Review Pack — one dated markdown pack assembling, per business
    domain, the latest approved answer edition of every question (verdict, expectation
    verdicts, materialized issues, open risks, pins + freshness), plus the roster of
    questions with no approved answer. The pack is an ASSEMBLY, never a computation:
    every figure it carries was emitted by a claim-linted edition, and each section
    cites the edition it came from. Standards clause references are deliberately
    absent here — the pack is an input set; the project's QMS names the review."""
    corpus_root = Path(args.corpus_root)
    parent = Path(args.root).parent
    domains = [d.strip() for d in args.domains.split(",") if d.strip()]
    as_of = args.as_of or dt.date.today().isoformat()
    out_dir = Path(args.out) / as_of
    out_dir.mkdir(parents=True, exist_ok=True)
    lines = [f"# Management Review Pack — {as_of}", "",
             "_Assembled by the commercial-skill engine from approved answer editions. "
             "Every figure below was emitted by a claim-linted edition of the cited question; "
             "this pack computes nothing._", ""]
    if args.include_drafts:
        lines += ["> ⚠️ **Includes unapproved drafts** (flagged `DRAFT` inline) — for internal "
                  "preview only; a review pack of record uses approved editions only.", ""]
    summary = {"as_of": as_of, "domains": [], "include_drafts": bool(args.include_drafts)}
    for dom in domains:
        root = parent / dom
        try:
            cfg = load_config(root)
        except CommercialError as e:
            lines += [f"## {dom}", "", f"_skipped: {e}_", ""]
            summary["domains"].append({"key": dom, "skipped": str(e)})
            continue
        dblock = domain_block(cfg, root)
        cats = {c["key"]: c.get("name", c["key"]) for c in cfg.get("categories", [])}
        lines += [f"## {dblock['name']}", ""]
        dsum = {"key": dom, "name": dblock["name"], "answered": [], "unanswered": [],
                "issues": 0, "risks": 0, "expectations": {"met": 0, "not-met": 0, "at-risk": 0,
                                                          "not-evaluable": 0}}
        unanswered = []
        for q in cfg.get("questions", []):
            ed, is_draft = _pack_pick_edition(root, q["id"], args.include_drafts)
            if ed is None:
                unanswered.append((q["id"], "not implemented" if not q.get("computation")
                                   else "no approved edition", q["question"]))
                continue
            edir = bq_dir(root, q["id"]) / ed["edition"]
            data = json.loads((edir / "data.json").read_text())
            rel = str((edir / "report.md").relative_to(parent.parent.parent))
            tag = " **DRAFT**" if is_draft else ""
            verd = (data.get("verdicts") or [{}])[0].get("headline", "—")
            lines += [f"### {q['id']} — {q['question']}{tag}", "",
                      f"_Category: {cats.get(q['category'], q['category'])} · edition "
                      f"`{ed['edition']}` ({ed.get('status')}) · report: `{rel}`_", "",
                      f"**Verdict:** {verd}", ""]
            exps = data.get("expectations") or []
            if exps:
                lines += ["| Expectation | Expected | Actual | Verdict |", "|---|---|---|---|"]
                for e in exps:
                    v = e.get("verdict", "not-evaluable")
                    dsum["expectations"][v] = dsum["expectations"].get(v, 0) + 1
                    lines.append(f"| {e.get('id')} {e.get('statement')} | {e.get('expected')} | "
                                 f"{e.get('actual')} | {v}{'' if e.get('validated') else ' (unvalidated)'} |")
                lines.append("")
            nar = data.get("narrative") or {}
            for grp, title in (("issues", "Issues"), ("risks", "Risks")):
                items = nar.get(grp) or []
                if items:
                    lines.append(f"**{title}:**")
                    for it in items:
                        lines.append(f"- {it.get('id')} ({it.get('severity', 'medium')}) — {it.get('statement')}")
                    lines.append("")
                    dsum[grp] += len(items)
            pins = ed.get("pins") or {}
            if pins:
                fr = []
                for ds, snap in pins.items():
                    try:
                        cfg_ds = corpus_dataset_cfg(corpus_root, ds)
                        age = (dt.date.fromisoformat(as_of) - dt.date.fromisoformat(snap.split(".")[0])).days
                        band = "stale" if age > int(cfg_ds.get("max_age_days", 90)) else "fresh"
                    except Exception:
                        age, band = "?", "unknown"
                    fr.append(f"`{ds}@{snap}` ({age}d, {band})")
                lines += ["_Pins: " + "; ".join(fr) + "_", ""]
            dsum["answered"].append({"id": q["id"], "edition": ed["edition"], "draft": is_draft})
        if unanswered:
            lines += ["### Not in this pack", "", "| Question | Why | |", "|---|---|---|"]
            for qid, why, text in unanswered:
                lines.append(f"| {qid} | {why} | {text} |")
            lines.append("")
            dsum["unanswered"] = [u[0] for u in unanswered]
        summary["domains"].append(dsum)
    (out_dir / "pack.md").write_text("\n".join(lines) + "\n")
    (out_dir / "pack.json").write_text(json.dumps(summary, indent=1))
    n_ans = sum(len(d.get("answered", [])) for d in summary["domains"])
    n_un = sum(len(d.get("unanswered", [])) for d in summary["domains"])
    print(f"pack written: {out_dir / 'pack.md'} — {n_ans} answered question(s), {n_un} not in pack, "
          f"domains: {', '.join(domains)}")
    return 0


def cmd_catalog(args):
    root, corpus_root = Path(args.root), Path(args.corpus_root)
    cfg = load_config(root)
    terms_catalog = cfg.get("terms") or {}
    for q in cfg.get("questions", []):
        row = _bq_sidecar_row(root, corpus_root, q, terms_catalog)
        mark = {"answered": "✓", "draft-only": "◐", "no-answer": "○", "not-implemented": "·"}[row["status"]]
        print(f"{mark} {q['id']:6s} [{q['category']}] {row['status']:15s} {q['question'][:80]}")
    return 0


def main(argv=None):
    p = argparse.ArgumentParser(prog="commercial.py", description=__doc__)
    p.add_argument("--root", default=DEFAULT_ROOT,
                   help=f"domain root holding the catalog + reports (default {DEFAULT_ROOT})")
    p.add_argument("--domain", default=None,
                   help="shorthand for --root docs/project/<domain> (finance, manufacturing, ...)")
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

    s = sub.add_parser("render", help="write .console/<domain>-index.json sidecar")
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

    s = sub.add_parser("code-audit",
                       help="deterministic code-quality checks (lint/poison/determinism) -> store (soft gate)")
    s.add_argument("bq", nargs="?")
    s.add_argument("--path", help="single artifact: commercial-root-relative, or corpus:<ds>/gen.py")
    s.add_argument("--all", action="store_true", help="audit every implemented question's artifacts")
    s.set_defaults(fn=cmd_code_audit)

    s = sub.add_parser("record-code-review", help="file an AI code-review verdict into the code-quality store")
    s.add_argument("path", help="artifact path: commercial-root-relative, or corpus:<ds>/gen.py")
    s.add_argument("--verdict", required=True)
    s.add_argument("--by", required=True)
    s.add_argument("--summary", required=True)
    s.add_argument("--finding", action="append",
                   help="repeatable: 'severity|summary|disposition'")
    s.add_argument("--detail-ref", help="path to the full review dossier")
    s.set_defaults(fn=cmd_record_code_review)

    s = sub.add_parser("plan-init", help="scaffold a question's user-owned analysis plan")
    s.add_argument("bq")
    s.set_defaults(fn=cmd_plan_init)

    s = sub.add_parser("catalog", help="question roster with answer status")
    s.set_defaults(fn=cmd_catalog)

    s = sub.add_parser("dependents", help="implemented question ids whose corpus_deps match a dataset name/prefix")
    s.add_argument("dataset", help="exact dataset name or prefix, e.g. commercial/openfda-; '*' = every implemented question")
    s.add_argument("--implemented-only", action="store_true", default=True)
    s.set_defaults(fn=cmd_dependents)

    s = sub.add_parser("pack", help="assemble a dated Management Review Pack from approved editions across domains")
    s.add_argument("--domains", default="commercial", help="comma-separated domain slugs (siblings of --root)")
    s.add_argument("--out", default="docs/project/management-review", help="pack root; a dated subfolder is created")
    s.add_argument("--as-of", help="pack date (default: today); also the freshness anchor")
    s.add_argument("--include-drafts", action="store_true", help="fall back to the newest draft where no approved edition exists (flagged)")
    s.set_defaults(fn=cmd_pack)

    args = p.parse_args(argv)
    if args.domain and args.root == DEFAULT_ROOT:
        args.root = str(Path(DEFAULT_ROOT).parent / args.domain)
    try:
        return args.fn(args)
    except CommercialError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
