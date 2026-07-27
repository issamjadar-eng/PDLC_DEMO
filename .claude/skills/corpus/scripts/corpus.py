#!/usr/bin/env python3
"""corpus.py — versioned snapshot grounding engine (corpus skill).

Single CLI for the corpus tree: immutable dated snapshots of acquired data
(raw byte-pinned payloads + schema-validated normalized CSV + provenance.yml),
first-class assumption records (A-NNN) and freshness waivers (W-NNN).

Design rules enforced here:
  - Nothing writes on failure: snapshots are built in a staging dir and moved
    into place only after acquisition, normalization, schema validation and
    asserts all pass.
  - Snapshots are immutable: a snapshot id is never reused; same-day
    re-acquisition gets a numeric suffix (2026-07-22.2).
  - Every normalized file names its raw parents by sha256 in provenance.yml —
    the machine-walkable substantiation chain.

Requires: Python 3.9+, PyYAML.
"""

import argparse
import csv
import datetime as dt
import hashlib
import io
import json
import re
import shutil
import subprocess
import sys
import urllib.parse
import urllib.request
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.stderr.write("corpus.py requires PyYAML (pip install pyyaml / uv run --with pyyaml)\n")
    sys.exit(2)

OPENFDA_BASE = "https://api.fda.gov"
DEFAULT_ROOT = "docs/project/corpus"


# ---------------------------------------------------------------- helpers

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def load_yaml(path: Path):
    with open(path) as f:
        return yaml.safe_load(f)


def dump_yaml(data, path: Path):
    with open(path, "w") as f:
        yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True, width=100)


def today() -> str:
    return dt.date.today().isoformat()


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


class CorpusError(Exception):
    pass


def dataset_dir(root: Path, name: str) -> Path:
    d = root / name
    if not (d / "dataset.yml").exists():
        raise CorpusError(f"dataset '{name}' not found (no {d / 'dataset.yml'})")
    return d


def iter_datasets(root: Path):
    for cfg in sorted(root.glob("*/*/dataset.yml")):
        yield cfg.parent.relative_to(root).as_posix(), cfg.parent


def snapshot_ids(ds_dir: Path):
    snaps = ds_dir / "snapshots"
    if not snaps.is_dir():
        return []
    return sorted(p.name for p in snaps.iterdir() if p.is_dir() and not p.name.startswith("."))


def read_latest(ds_dir: Path):
    p = ds_dir / "latest"
    if p.exists():
        return p.read_text().strip() or None
    return None


def new_snapshot_id(ds_dir: Path) -> str:
    base = today()
    existing = set(snapshot_ids(ds_dir))
    if base not in existing:
        return base
    n = 2
    while f"{base}.{n}" in existing:
        n += 1
    return f"{base}.{n}"


def snapshot_date(snap_id: str) -> dt.date:
    return dt.date.fromisoformat(snap_id.split(".")[0])


def command_script_sha(cmd: str, ds_dir: Path):
    """If a command: references a dataset-local script (the gen.py pattern), return
    its sha256 so provenance records the exact code bytes that produced the
    snapshot. First .py/.sh token that resolves to a file in the dataset dir wins;
    None when the command references no local script."""
    for tok in (cmd or "").split():
        if tok.startswith(("-", "{", "'", '"')):
            continue
        cand = ds_dir / tok
        if cand.suffix in (".py", ".sh") and cand.is_file():
            return sha256_file(cand)
    return None


# ---------------------------------------------------------------- acquisition

def acquire_openfda(acq: dict, raw_dir: Path, log):
    """Paginate an openFDA endpoint into raw/page-NNN.json. Returns source records.

    With a `count:` field, runs a single openFDA count (aggregation) query instead of
    paginating rows — the right shape for high-volume endpoints like MAUDE events."""
    endpoint = acq["endpoint"]  # e.g. /device/510k.json
    params = {k: v for k, v in acq.get("params", {}).items()}
    if "search" in acq:
        params["search"] = acq["search"]
    if "count" in acq:
        params["count"] = acq["count"]
        if "count_limit" in acq:
            params["limit"] = str(int(acq["count_limit"]))
        url = f"{OPENFDA_BASE}{endpoint}?{urllib.parse.urlencode(params)}"
        retrieved_at = now_iso()
        req = urllib.request.Request(url, headers={"User-Agent": "corpus-skill/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                payload = resp.read()
        except urllib.error.HTTPError as e:
            raise CorpusError(f"openFDA HTTP {e.code} for {url}")
        if not json.loads(payload).get("results"):
            raise CorpusError("openFDA count query returned no results")
        out = raw_dir / "page-001.json"
        out.write_bytes(payload)
        log(f"  openFDA count query: {len(json.loads(payload)['results'])} terms")
        return [{
            "type": "openfda-count",
            "url": url,
            "retrieved_at": retrieved_at,
            "usage_rights": acq.get("usage_rights", "public-domain (openFDA)"),
        }], [out]
    limit = int(acq.get("limit", 100))
    max_records = int(acq.get("max_records", 1000))
    params["limit"] = str(limit)
    files, fetched, skip, page = [], 0, 0, 1
    retrieved_at = now_iso()
    first_url = None
    while fetched < max_records:
        params["skip"] = str(skip)
        url = f"{OPENFDA_BASE}{endpoint}?{urllib.parse.urlencode(params)}"
        first_url = first_url or url
        req = urllib.request.Request(url, headers={"User-Agent": "corpus-skill/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                payload = resp.read()
        except urllib.error.HTTPError as e:
            if e.code == 404 and page > 1:
                break  # ran past the last page
            raise CorpusError(f"openFDA HTTP {e.code} for {url}")
        doc = json.loads(payload)
        results = doc.get("results", [])
        if not results:
            break
        out = raw_dir / f"page-{page:03d}.json"
        out.write_bytes(payload)
        files.append(out)
        total = doc.get("meta", {}).get("results", {}).get("total", 0)
        fetched += len(results)
        log(f"  openFDA page {page}: {len(results)} records (total available: {total})")
        if fetched >= total or len(results) < limit:
            break
        skip += limit
        page += 1
    if not files:
        raise CorpusError("openFDA acquisition returned no results")
    return [{
        "type": "openfda",
        "url": first_url,
        "pages": len(files),
        "retrieved_at": retrieved_at,
        "usage_rights": acq.get("usage_rights", "public-domain (openFDA)"),
    }], files


def acquire_command(acq: dict, raw_dir: Path, ds_dir: Path, log):
    """Run a dataset-local command that writes files into {raw_dir}."""
    cmd = acq["command"].format(raw_dir=str(raw_dir), dataset_dir=str(ds_dir))
    retrieved_at = now_iso()
    log(f"  running: {cmd}")
    proc = subprocess.run(cmd, shell=True, cwd=str(ds_dir), capture_output=True, text=True)
    if proc.returncode != 0:
        raise CorpusError(f"acquisition command failed ({proc.returncode}):\n{proc.stderr[-2000:]}")
    files = sorted(p for p in raw_dir.rglob("*") if p.is_file())
    if not files:
        raise CorpusError("acquisition command produced no files in raw/")
    return [{
        "type": "command",
        "command": acq["command"],
        "system_of_record": acq.get("system_of_record", "unspecified"),
        "retrieved_at": retrieved_at,
        "usage_rights": acq.get("usage_rights", "internal"),
    }], files


def acquire_file(acq: dict, raw_dir: Path, ds_dir: Path, log):
    """Copy files from a path (internal export drop) into raw/."""
    src = (ds_dir / acq["path"]).resolve() if not Path(acq["path"]).is_absolute() else Path(acq["path"])
    if not src.exists():
        raise CorpusError(f"acquisition source not found: {src}")
    retrieved_at = now_iso()
    files = []
    srcs = [src] if src.is_file() else sorted(p for p in src.rglob("*") if p.is_file())
    for s in srcs:
        d = raw_dir / s.name
        shutil.copy2(s, d)
        files.append(d)
    if not files:
        raise CorpusError(f"no files found at {src}")
    return [{
        "type": "file",
        "path": str(src),
        "system_of_record": acq.get("system_of_record", "unspecified"),
        "retrieved_at": retrieved_at,
        "usage_rights": acq.get("usage_rights", "internal"),
    }], files


def normalize_openfda_flatten(norm: dict, raw_dir: Path, normalized_dir: Path, log):
    """Built-in: flatten openFDA page JSONs' results[] into one CSV via dot-path fields."""
    fields = norm["fields"]  # list of dot-paths, e.g. "openfda.device_name"
    out = normalized_dir / norm.get("output", "records.csv")
    rows = []
    for page in sorted(raw_dir.glob("page-*.json")):
        for rec in json.loads(page.read_text()).get("results", []):
            row = {}
            for fpath in fields:
                cur = rec
                for part in fpath.split("."):
                    if isinstance(cur, dict):
                        cur = cur.get(part)
                    elif isinstance(cur, list) and part.isdigit() and int(part) < len(cur):
                        cur = cur[int(part)]
                    else:
                        cur = None
                    if cur is None:
                        break
                if isinstance(cur, list):
                    cur = "; ".join(str(x) for x in cur)
                row[fpath.split(".")[-1]] = "" if cur is None else str(cur)
            rows.append(row)
    if not rows:
        raise CorpusError("openfda-flatten produced no rows")
    cols = [f.split(".")[-1] for f in fields]
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    log(f"  normalized {len(rows)} rows -> {out.name}")


def normalize_openfda_count(norm: dict, raw_dir: Path, normalized_dir: Path, log):
    """Built-in: openFDA count-query results ({term, count}) -> term,count CSV."""
    out = normalized_dir / norm.get("output", "records.csv")
    rows, skipped = [], 0
    for page in sorted(raw_dir.glob("page-*.json")):
        for rec in json.loads(page.read_text()).get("results", []):
            # term-counts use "term"; date-field counts use "time" (YYYYMMDD)
            term = str(rec.get("term", rec.get("time", ""))).strip()
            if not term:
                skipped += 1  # openFDA count buckets can include an empty term — unusable as a key
                continue
            rows.append({"term": term, "count": str(rec.get("count", ""))})
    if not rows:
        raise CorpusError("openfda-count produced no rows")
    if skipped:
        log(f"  skipped {skipped} empty-term count bucket(s) (recorded here, not in CSV)")
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["term", "count"])
        w.writeheader()
        w.writerows(rows)
    log(f"  normalized {len(rows)} count terms -> {out.name}")


def normalize_command(norm: dict, raw_dir: Path, normalized_dir: Path, ds_dir: Path, log):
    cmd = norm["command"].format(raw_dir=str(raw_dir), normalized_dir=str(normalized_dir),
                                 dataset_dir=str(ds_dir))
    log(f"  running: {cmd}")
    proc = subprocess.run(cmd, shell=True, cwd=str(ds_dir), capture_output=True, text=True)
    if proc.returncode != 0:
        raise CorpusError(f"normalize command failed ({proc.returncode}):\n{proc.stderr[-2000:]}")
    if not any(normalized_dir.iterdir()):
        raise CorpusError("normalize command produced no files in normalized/")


# ---------------------------------------------------------------- validation

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def schema_target(cfg: dict, normalized_dir: Path):
    """Resolve the schema's target CSV (declared file, or the single CSV present)."""
    schema = cfg.get("schema") or {}
    target = normalized_dir / schema.get("file", "records.csv")
    if not target.exists():
        csvs = list(normalized_dir.glob("*.csv"))
        if len(csvs) == 1:
            return csvs[0]
    return target


def validate_schema(cfg: dict, normalized_dir: Path, errors: list):
    schema = cfg.get("schema")
    if not schema:
        errors.append("dataset.yml has no schema: block (schema validation is mandatory)")
        return 0
    target = schema_target(cfg, normalized_dir)
    if not target.exists():
        errors.append(f"schema target not found: {target.name}")
        return 0
    with open(target, newline="") as f:
        reader = csv.DictReader(f)
        header = reader.fieldnames or []
        cols = {c["name"]: c for c in schema.get("columns", [])}
        for cname, cdef in cols.items():
            if cdef.get("required", False) and cname not in header:
                errors.append(f"required column missing: {cname}")
        keys = schema.get("key", [])
        seen, nrows = set(), 0
        for row in reader:
            nrows += 1
            if keys:
                k = tuple(row.get(k, "") for k in keys)
                if all(v == "" for v in k):
                    errors.append(f"row {nrows}: empty key {keys}")
                elif k in seen:
                    errors.append(f"row {nrows}: duplicate key {k}")
                seen.add(k)
            for cname, cdef in cols.items():
                v = row.get(cname, "")
                if v and cdef.get("type") == "date" and not DATE_RE.match(v):
                    errors.append(f"row {nrows}: {cname} not ISO date: {v!r}")
                if v and cdef.get("type") in ("int", "float"):
                    try:
                        (int if cdef["type"] == "int" else float)(v)
                    except ValueError:
                        errors.append(f"row {nrows}: {cname} not {cdef['type']}: {v!r}")
    return nrows


def run_asserts(cfg: dict, nrows: int, normalized_dir: Path, ds_dir: Path, errors: list):
    """Dataset-declared asserts, re-run on every acquire AND every validate.

    Supported keys under `asserts:`:
      min_rows / max_rows — row-count bounds on the schema target CSV.
      enums: {<col>: [allowed, ...]} — closed value sets per column (empty cells pass;
        use `required: true` in the schema to forbid empties).
      command: "<shell cmd>" — dataset-local check seam, run with the same substitution
        conventions as normalize ({raw_dir} / {normalized_dir} / {dataset_dir}, absolute
        paths, cwd = dataset dir); non-zero exit = failure. This is how a dataset proves
        its narrative/generator knobs actually landed in the data.
    """
    asserts = cfg.get("asserts") or {}
    min_rows = int(asserts.get("min_rows", 1))
    if nrows < min_rows:
        errors.append(f"assert min_rows: {nrows} < {min_rows}")
    if "max_rows" in asserts and nrows > int(asserts["max_rows"]):
        errors.append(f"assert max_rows: {nrows} > {asserts['max_rows']}")
    normalized_dir = normalized_dir.resolve()
    ds_dir = ds_dir.resolve()
    enums = asserts.get("enums") or {}
    if enums:
        target = schema_target(cfg, normalized_dir)
        if not target.exists():
            errors.append("assert enums: schema target CSV not found")
        else:
            with open(target, newline="") as f:
                reader = csv.DictReader(f)
                header = reader.fieldnames or []
                for col in enums:
                    if col not in header:
                        errors.append(f"assert enums: column not in CSV: {col}")
                bad = {col: {} for col in enums}
                for row in reader:
                    for col, allowed in enums.items():
                        v = row.get(col, "")
                        if v != "" and v not in allowed:
                            bad[col][v] = bad[col].get(v, 0) + 1
            for col, viol in bad.items():
                if viol:
                    detail = ", ".join(f"{v!r} x{n}" for v, n in sorted(viol.items())[:10])
                    errors.append(f"assert enums[{col}]: {sum(viol.values())} row(s) outside "
                                  f"allowed values: {detail}")
    if "command" in asserts:
        cmd = asserts["command"].format(raw_dir=str(normalized_dir.parent / "raw"),
                                        normalized_dir=str(normalized_dir),
                                        dataset_dir=str(ds_dir))
        proc = subprocess.run(cmd, shell=True, cwd=str(ds_dir), capture_output=True, text=True)
        if proc.returncode != 0:
            tail = (proc.stderr or proc.stdout or "").strip()[-500:]
            errors.append(f"assert command failed ({proc.returncode}): {cmd}" +
                          (f"\n    {tail}" if tail else ""))


# ---------------------------------------------------------------- commands

def log_print(msg):
    print(msg)


def cmd_init(args):
    root = Path(args.root)
    ds = root / args.dataset
    if (ds / "dataset.yml").exists():
        print(f"dataset already exists: {ds}")
        return 0
    (ds / "snapshots").mkdir(parents=True, exist_ok=True)
    (ds / "assumptions").mkdir(exist_ok=True)
    (ds / "waivers").mkdir(exist_ok=True)
    stub = {
        "dataset": args.dataset,
        "title": args.dataset.split("/")[-1].replace("-", " ").title(),
        "description": "TODO — one sentence: what this dataset holds and which questions consume it.",
        "internal": False,
        "max_age_days": 90,
        "acquisition": {
            "type": "command",
            "command": "echo TODO configure acquisition && exit 1",
            "system_of_record": "TODO — the source system this stands in for (internal datasets)",
            "usage_rights": "TODO — public-domain | licensed (no redistribution) | internal",
        },
        "normalize": {"command": "echo TODO configure normalization && exit 1"},
        "schema": {
            "file": "records.csv",
            "key": ["id"],
            "columns": [{"name": "id", "type": "str", "required": True}],
        },
        "asserts": {"min_rows": 1},
    }
    dump_yaml(stub, ds / "dataset.yml")
    (ds / "README.md").write_text(
        f"# Corpus dataset — `{args.dataset}`\n\n"
        "TODO: describe the dataset, its source, and which business questions consume it.\n\n"
        "## Conventions\n\n"
        "- Managed by the `corpus` skill (`corpus.py`). Snapshots under `snapshots/` are immutable —\n"
        "  never hand-edit; re-acquire instead. `dataset.yml` is the config; `latest` points at the\n"
        "  newest valid snapshot. Assumptions in `assumptions/A-NNN.yml`, waivers in `waivers/W-NNN.yml`.\n\n"
        "## Changelog\n\n"
        f"- {today()}: Dataset scaffolded by `corpus.py init`.\n"
    )
    print(f"scaffolded {ds}\nEdit {ds / 'dataset.yml'} (acquisition, normalize, schema) then run acquire.")
    return 0


def _acquire(root: Path, name: str, log=log_print, dry_run=False):
    # resolve absolute: command/file acquisition runs subprocesses with cwd=dataset dir,
    # so substituted {raw_dir}/{normalized_dir} paths must not be cwd-relative
    ds = dataset_dir(root, name).resolve()
    cfg = load_yaml(ds / "dataset.yml")
    snap_id = new_snapshot_id(ds)
    staging = ds / f".staging-{snap_id}"
    if staging.exists():
        shutil.rmtree(staging)
    raw_dir = staging / "raw"
    normalized_dir = staging / "normalized"
    raw_dir.mkdir(parents=True)
    normalized_dir.mkdir()
    try:
        acq = cfg.get("acquisition") or {}
        atype = acq.get("type")
        log(f"[{name}] acquiring snapshot {snap_id} (type={atype})")
        if atype == "openfda":
            sources, raw_files = acquire_openfda(acq, raw_dir, log)
        elif atype == "command":
            sources, raw_files = acquire_command(acq, raw_dir, ds, log)
        elif atype == "file":
            sources, raw_files = acquire_file(acq, raw_dir, ds, log)
        else:
            raise CorpusError(f"unknown acquisition.type: {atype!r}")

        norm = cfg.get("normalize") or {}
        if norm.get("type") == "openfda-flatten":
            normalize_openfda_flatten(norm, raw_dir, normalized_dir, log)
        elif norm.get("type") == "openfda-count":
            normalize_openfda_count(norm, raw_dir, normalized_dir, log)
        elif "command" in norm:
            normalize_command(norm, raw_dir, normalized_dir, ds, log)
        else:
            raise CorpusError("dataset.yml normalize: needs type: openfda-flatten | openfda-count, or command:")

        errors = []
        nrows = validate_schema(cfg, normalized_dir, errors)
        run_asserts(cfg, nrows, normalized_dir, ds, errors)
        # referenced assumptions must exist
        for aid in cfg.get("assumptions_referenced", []) or []:
            if not (ds / "assumptions" / f"{aid}.yml").exists():
                errors.append(f"referenced assumption record missing: {aid}")
        if dry_run:
            log(f"[{name}] DRY RUN — snapshot {snap_id} would contain {nrows} rows")
            if errors:
                log("  checks FAILED:")
                for e in errors[:20]:
                    log(f"    - {e}")
            else:
                log("  schema + asserts: all checks passed")
            shutil.rmtree(staging)
            log(f"[{name}] dry run complete — staging discarded, nothing landed")
            if errors:
                raise CorpusError("dry run: validation failed (see above)")
            return None
        if errors:
            raise CorpusError("validation failed:\n  - " + "\n  - ".join(errors[:20]))

        raw_entries = [{"path": f"raw/{p.relative_to(raw_dir)}", "sha256": sha256_file(p)}
                       for p in raw_files]
        norm_entries = [{"path": f"normalized/{p.relative_to(normalized_dir)}",
                         "sha256": sha256_file(p),
                         "parents": [e["sha256"] for e in raw_entries]}
                        for p in sorted(normalized_dir.rglob("*")) if p.is_file()]
        for s in sources:
            s["files"] = raw_entries
        provenance = {
            "dataset": name,
            "snapshot": snap_id,
            "created_at": now_iso(),
        }
        if cfg.get("data_through"):
            # machine-readable "data reflects the world through this date" — distinct
            # from the snapshot id (which is the acquisition date)
            provenance["as_of"] = str(cfg["data_through"])
        # pin the dataset-local script (gen.py pattern) that the acquisition or
        # normalize command ran — additive field; absent for non-script datasets
        # and for old snapshots, and validate never fails on its absence
        transform = {
            "step": "normalize",
            "spec": cfg.get("normalize"),
            "outputs": norm_entries,
        }
        script_sha = (command_script_sha(acq.get("command", ""), ds)
                      or command_script_sha(norm.get("command", ""), ds))
        if script_sha:
            transform["script_sha256"] = script_sha
        provenance.update({
            "sources": sources,
            "transforms": [transform],
            "assumptions_referenced": cfg.get("assumptions_referenced", []) or [],
            "checks": {"schema_valid": True, "asserts_passed": True, "row_count": nrows},
        })
        dump_yaml(provenance, staging / "provenance.yml")
        final = ds / "snapshots" / snap_id
        final.parent.mkdir(exist_ok=True)
        staging.rename(final)
        (ds / "latest").write_text(snap_id + "\n")
        log(f"[{name}] snapshot {snap_id} written ({nrows} rows); latest -> {snap_id}")
        return snap_id
    except Exception:
        if staging.exists():
            shutil.rmtree(staging)
        raise


def cmd_acquire(args):
    try:
        _acquire(Path(args.root), args.dataset, dry_run=getattr(args, "dry_run", False))
        return 0
    except CorpusError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


def _validate_snapshot(ds: Path, name: str, snap_id: str, errors: list):
    sdir = ds / "snapshots" / snap_id
    prov_path = sdir / "provenance.yml"
    if not prov_path.exists():
        errors.append(f"{name}@{snap_id}: provenance.yml missing")
        return
    prov = load_yaml(prov_path)
    for src in prov.get("sources", []):
        if not src.get("usage_rights"):
            errors.append(f"{name}@{snap_id}: source missing usage_rights")
        for fe in src.get("files", []):
            p = sdir / fe["path"]
            if not p.exists():
                errors.append(f"{name}@{snap_id}: raw file missing: {fe['path']}")
            elif sha256_file(p) != fe["sha256"]:
                errors.append(f"{name}@{snap_id}: raw hash mismatch (MUTATED?): {fe['path']}")
    raw_hashes = {fe["sha256"] for src in prov.get("sources", []) for fe in src.get("files", [])}
    for tr in prov.get("transforms", []):
        for oe in tr.get("outputs", []):
            p = sdir / oe["path"]
            if not p.exists():
                errors.append(f"{name}@{snap_id}: normalized file missing: {oe['path']}")
            elif sha256_file(p) != oe["sha256"]:
                errors.append(f"{name}@{snap_id}: normalized hash mismatch (MUTATED?): {oe['path']}")
            for parent in oe.get("parents", []):
                if parent not in raw_hashes:
                    errors.append(f"{name}@{snap_id}: orphan parent hash on {oe['path']}")
    for aid in prov.get("assumptions_referenced", []):
        if not (ds / "assumptions" / f"{aid}.yml").exists():
            errors.append(f"{name}@{snap_id}: referenced assumption missing: {aid}")
    cfg = load_yaml(ds / "dataset.yml")
    verrors = []
    nrows = validate_schema(cfg, sdir / "normalized", verrors)
    run_asserts(cfg, nrows, sdir / "normalized", ds, verrors)
    errors.extend(f"{name}@{snap_id}: {e}" for e in verrors)


def cmd_validate(args):
    root = Path(args.root)
    errors = []
    targets = [(args.dataset, dataset_dir(root, args.dataset))] if args.dataset else list(iter_datasets(root))
    validated = []
    for name, ds in targets:
        snap = args.snapshot or read_latest(ds)
        if not snap:
            errors.append(f"{name}: no snapshots")
            continue
        _validate_snapshot(ds, name, snap, errors)
        validated.append(f"{name}@{snap}")
    if errors:
        print("VALIDATION ERRORS:")
        for e in errors:
            print(f"  - {e}")
        return 1
    print(f"validate OK ({len(validated)} dataset(s)):")
    for t in validated:
        print(f"  - {t}")
    return 0


def freshness_band(age_days: int, max_age: int) -> str:
    if age_days > max_age:
        return "stale"
    if age_days > max_age * 0.75:
        return "aging"
    return "fresh"


def active_waiver(ds: Path, today_d: dt.date):
    for w in sorted((ds / "waivers").glob("W-*.yml")) if (ds / "waivers").is_dir() else []:
        wd = load_yaml(w)
        try:
            if wd.get("status", "active") == "active" and dt.date.fromisoformat(str(wd["expires"])) >= today_d:
                return wd["id"]
        except (KeyError, ValueError):
            continue
    return None


def cmd_check(args):
    root = Path(args.root)
    errors, warnings, rows = [], [], []
    today_d = dt.date.today()
    datasets = list(iter_datasets(root))
    if not datasets:
        print(f"no datasets under {root}")
        return 1
    for name, ds in datasets:
        cfg = load_yaml(ds / "dataset.yml")
        latest = read_latest(ds)
        if not latest:
            rows.append((name, "-", "NO SNAPSHOT", "-", ""))
            errors.append(f"{name}: no snapshots")
            continue
        _validate_snapshot(ds, name, latest, errors)
        age = (today_d - snapshot_date(latest)).days
        band = freshness_band(age, int(cfg.get("max_age_days", 90)))
        note = ""
        if band == "stale":
            wid = active_waiver(ds, today_d)
            if wid:
                note = f"waived ({wid})"
            else:
                errors.append(f"{name}: STALE ({age}d > {cfg.get('max_age_days', 90)}d) and no active waiver")
        a_files = sorted((ds / "assumptions").glob("A-*.yml")) if (ds / "assumptions").is_dir() else []
        n_assum = len(a_files)
        contradicted = []
        for af in a_files:
            ad = load_yaml(af) or {}
            status = ad.get("status", "active")
            if status == "contradicted":
                contradicted.append(af.stem)
            elif status == "active":
                # warn (never fail) on active-but-unfilled records: a deliberately
                # unquantified assumption may be doing its job by blocking a chart,
                # but it should stay visible until its TODOs are resolved
                probs = []
                todo = [k for k, v in ad.items() if isinstance(v, str) and "TODO" in v]
                if todo:
                    probs.append(f"TODO field(s): {', '.join(todo)}")
                if not ad.get("sources_consulted"):
                    probs.append("empty sources_consulted")
                if probs:
                    warnings.append(f"{name}: {af.stem} is active with {'; '.join(probs)}")
        if contradicted:
            errors.append(f"{name}: contradicted assumption(s) need review: {', '.join(contradicted)}")
        rows.append((name, latest, band, f"{age}d", note or (f"{n_assum} assumption(s)" if n_assum else "")))
    w = max(len(r[0]) for r in rows) + 2
    print(f"{'dataset'.ljust(w)}{'latest'.ljust(15)}{'freshness'.ljust(11)}{'age'.ljust(6)}notes")
    for r in rows:
        print(f"{r[0].ljust(w)}{r[1].ljust(15)}{r[2].ljust(11)}{r[3].ljust(6)}{r[4]}")
    if warnings:
        print("\nCHECK WARNINGS (non-blocking):")
        for wmsg in warnings:
            print(f"  - {wmsg}")
    if errors:
        print("\nCHECK FAILURES:")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("\ncorpus check: GREEN")
    return 0


def load_normalized(ds: Path, snap_id: str, cfg: dict):
    schema = cfg.get("schema", {})
    target = ds / "snapshots" / snap_id / "normalized" / schema.get("file", "records.csv")
    if not target.exists():
        csvs = list((ds / "snapshots" / snap_id / "normalized").glob("*.csv"))
        target = csvs[0] if len(csvs) == 1 else target
    keys = schema.get("key", [])
    out = {}
    with open(target, newline="") as f:
        for row in csv.DictReader(f):
            out[tuple(row.get(k, "") for k in keys)] = row
    return out


def cmd_diff(args):
    root = Path(args.root)
    ds = dataset_dir(root, args.dataset)
    cfg = load_yaml(ds / "dataset.yml")
    a, b = load_normalized(ds, args.a, cfg), load_normalized(ds, args.b, cfg)
    added = [k for k in b if k not in a]
    removed = [k for k in a if k not in b]
    changed = [k for k in b if k in a and a[k] != b[k]]
    print(f"# Delta — {args.dataset}: {args.a} -> {args.b}\n")
    print(f"- rows: {len(a)} -> {len(b)}  (+{len(added)} added, -{len(removed)} removed, ~{len(changed)} changed)\n")
    for label, keys in (("Added", added), ("Removed", removed), ("Changed", changed)):
        if keys:
            print(f"## {label} ({len(keys)})\n")
            for k in keys[: args.limit]:
                print(f"- `{' / '.join(k)}`")
            if len(keys) > args.limit:
                print(f"- … and {len(keys) - args.limit} more")
            print()
    return 0


def cmd_refresh(args):
    root = Path(args.root)
    names = [args.dataset] if args.dataset else [n for n, _ in iter_datasets(root)]
    rc = 0
    for name in names:
        ds = dataset_dir(root, name)
        prev = read_latest(ds)
        try:
            snap = _acquire(root, name)
        except CorpusError as e:
            print(f"ERROR [{name}]: {e}", file=sys.stderr)
            rc = 1
            continue
        if prev and prev != snap:
            cfg = load_yaml(ds / "dataset.yml")
            a, b = load_normalized(ds, prev, cfg), load_normalized(ds, snap, cfg)
            added = [k for k in b if k not in a]
            removed = [k for k in a if k not in b]
            changed = [k for k in b if k in a and a[k] != b[k]]
            lines = [f"# Delta report — {name}", "",
                     f"_{prev} -> {snap}, generated {now_iso()} by corpus.py refresh_", "",
                     f"- rows: {len(a)} -> {len(b)} (+{len(added)} / -{len(removed)} / ~{len(changed)})", ""]
            for label, keys in (("Added", added), ("Removed", removed), ("Changed", changed)):
                if keys:
                    lines.append(f"## {label} ({len(keys)})")
                    lines += [f"- `{' / '.join(k)}`" for k in keys[:50]]
                    if len(keys) > 50:
                        lines.append(f"- … and {len(keys) - 50} more")
                    lines.append("")
            actives = sorted(a.stem for a in (ds / "assumptions").glob("A-*.yml")
                             if load_yaml(a).get("status", "active") == "active")
            if actives:
                lines += ["## Assumptions to review against this delta", ""]
                lines += [f"- {a} — confirm still holds; set `status: contradicted` if the new data refutes it"
                          for a in actives]
                lines.append("")
            (ds / "snapshots" / snap / "delta-report.md").write_text("\n".join(lines))
            print(f"[{name}] delta report written: snapshots/{snap}/delta-report.md")
    return rc


def cmd_list(args):
    root = Path(args.root)
    today_d = dt.date.today()
    found = False
    for name, ds in iter_datasets(root):
        found = True
        cfg = load_yaml(ds / "dataset.yml")
        latest = read_latest(ds) or "-"
        band = "-"
        if latest != "-":
            band = freshness_band((today_d - snapshot_date(latest)).days, int(cfg.get("max_age_days", 90)))
        snaps = len(snapshot_ids(ds))
        n_assum = len(list((ds / "assumptions").glob("A-*.yml")))
        print(f"{name}  snapshots={snaps}  latest={latest}  freshness={band}  assumptions={n_assum}"
              f"  internal={cfg.get('internal', False)}")
    if not found:
        print(f"no datasets under {root}")
    return 0


def next_record_id(root: Path, prefix: str, subdir: str) -> str:
    """Globally unique across the whole corpus root — assumption/waiver ids are cited
    bare (A-NNN) by downstream analyses, so per-dataset numbering would collide."""
    ids = [int(m.group(1)) for p in root.glob(f"*/*/{subdir}/{prefix}-*.yml")
           if (m := re.match(rf"{prefix}-(\d+)$", p.stem))]
    return f"{prefix}-{(max(ids) + 1) if ids else 1:03d}"


def cmd_assume(args):
    root = Path(args.root)
    ds = dataset_dir(root, args.dataset)
    (ds / "assumptions").mkdir(exist_ok=True)
    aid = next_record_id(root, "A", "assumptions")
    rec = {
        "id": aid,
        "title": args.title,
        "needed_for": args.needed_for.split(",") if args.needed_for else [],
        "why_unavailable": args.why or "TODO",
        "estimation_method": args.method or "TODO",
        "value_or_range": args.value or "TODO",
        "confidence": args.confidence,
        "sources_consulted": list(args.source or []),
        "refresh_trigger": args.refresh_trigger or "next corpus refresh",
        "created": today(),
        "status": "active",
    }
    dump_yaml(rec, ds / "assumptions" / f"{aid}.yml")
    print(f"created {ds / 'assumptions' / (aid + '.yml')} — fill TODO fields before citing it")
    return 0


def cmd_waive(args):
    root = Path(args.root)
    ds = dataset_dir(root, args.dataset)
    (ds / "waivers").mkdir(exist_ok=True)
    wid = next_record_id(root, "W", "waivers")
    rec = {
        "id": wid,
        "reason": args.reason,
        "owner": args.owner,
        "created": today(),
        "expires": args.expires,
        "status": "active",
    }
    dump_yaml(rec, ds / "waivers" / f"{wid}.yml")
    print(f"created {ds / 'waivers' / (wid + '.yml')} — expires {args.expires}")
    return 0


# ---------------------------------------------------------------- main

def main(argv=None):
    p = argparse.ArgumentParser(prog="corpus.py", description=__doc__)
    p.add_argument("--root", default=DEFAULT_ROOT, help=f"corpus root (default: {DEFAULT_ROOT})")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("init", help="scaffold a new dataset")
    s.add_argument("dataset", help="<domain>/<name>, e.g. commercial/openfda-510k")
    s.set_defaults(fn=cmd_init)

    s = sub.add_parser("acquire", help="acquire a new immutable snapshot")
    s.add_argument("dataset")
    s.add_argument("--dry-run", action="store_true",
                   help="run the full acquire->normalize->validate pipeline in staging, "
                        "report results, then discard — nothing lands (no snapshot slot used)")
    s.set_defaults(fn=cmd_acquire)

    s = sub.add_parser("refresh", help="acquire + delta report vs previous latest")
    s.add_argument("dataset", nargs="?", help="omit to refresh all datasets")
    s.set_defaults(fn=cmd_refresh)

    s = sub.add_parser("validate", help="schema + provenance integrity for a snapshot")
    s.add_argument("dataset", nargs="?")
    s.add_argument("--snapshot", help="default: latest")
    s.set_defaults(fn=cmd_validate)

    s = sub.add_parser("diff", help="row-level delta between two snapshots")
    s.add_argument("dataset")
    s.add_argument("a")
    s.add_argument("b")
    s.add_argument("--limit", type=int, default=25)
    s.set_defaults(fn=cmd_diff)

    s = sub.add_parser("check", help="whole-corpus health: integrity + freshness + assumptions")
    s.set_defaults(fn=cmd_check)

    s = sub.add_parser("list", help="datasets with snapshot/freshness summary")
    s.set_defaults(fn=cmd_list)

    s = sub.add_parser("assume", help="scaffold an A-NNN assumption record")
    s.add_argument("dataset")
    s.add_argument("--title", required=True)
    s.add_argument("--why")
    s.add_argument("--method")
    s.add_argument("--value")
    s.add_argument("--confidence", default="low", choices=["high", "med", "low"])
    s.add_argument("--needed-for", help="comma-separated BQ ids / dataset names")
    s.add_argument("--refresh-trigger")
    s.add_argument("--source", action="append", default=[],
                   help="repeatable: URL or path consulted (fills sources_consulted at scaffold time)")
    s.set_defaults(fn=cmd_assume)

    s = sub.add_parser("waive", help="scaffold a W-NNN freshness waiver (expires!)")
    s.add_argument("dataset")
    s.add_argument("--reason", required=True)
    s.add_argument("--owner", required=True)
    s.add_argument("--expires", required=True, help="ISO date")
    s.set_defaults(fn=cmd_waive)

    args = p.parse_args(argv)
    try:
        return args.fn(args)
    except CorpusError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
