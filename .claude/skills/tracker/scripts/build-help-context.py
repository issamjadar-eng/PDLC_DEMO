#!/usr/bin/env python3
"""
/tracker enrich-help — context bundle builder.

Deterministic helper for the help-author agent fan-out. Walks the project
state (project.yml, milestone catalogs, composition manifests, dhf-manifest
catalog, taxonomy, resolved evidence paths) and emits one YAML context
bundle per tracker row. The orchestrator (Claude) reads these bundles and
dispatches one help-author agent per row in parallel.

Usage:
    # All rows → emit one bundle each to stdout (newline-separated YAML docs)
    python3 build-help-context.py --all

    # One row → emit just that row's bundle
    python3 build-help-context.py --row PP1

    # Write bundles to a directory (one .yaml per row) for the dispatcher
    python3 build-help-context.py --all --out /tmp/tracker-help-bundles/

    # Dry-run (counts only)
    python3 build-help-context.py --all --dry-run

This script is deterministic and side-effect-light:
  - Reads only; never writes to project state.
  - The output bundle does NOT include the resolved evidence file's CONTENT
    (the agent reads it itself with the path we provide). It does include
    the file's hash (sha256) so the agent can stamp the cache signature.
"""

import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path


def _load_generate_module():
    """Reuse generate.py's row inventory + project loaders (DRY)."""
    here = Path(__file__).resolve().parent
    spec = importlib.util.spec_from_file_location('tracker_generate', here / 'generate.py')
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _sha256_file(path: Path) -> str | None:
    if not path.is_file():
        return None
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return f'sha256:{h.hexdigest()}'


def _load_catalog(project_dir: Path) -> dict:
    """Load the dhf-manifest catalog. Returns {} if missing."""
    # Try the canonical project-prefixed name first; fall back to scanning.
    candidates = list((project_dir / 'docs/project/dhf-manifest').glob('*-dhf-manifest.json'))
    if not candidates:
        return {}
    return json.loads(candidates[0].read_text(encoding='utf-8'))


def _index_obligations_by_dhf_role(catalog: dict) -> dict:
    """Build {(dhf_leaf, canonical_role): [obligation_entries]} index from
    the dhf-manifest catalog. The catalog's per-DHF projection lives at
    `dhf_manifest.<leaf>` as a list of obligation entries. Each entry is
    passed through to the agent untouched."""
    idx: dict = {}
    dhfs = catalog.get('dhf_manifest', {}) or {}
    for dhf_leaf, items in dhfs.items():
        if not isinstance(items, list):
            continue
        for entry in items:
            if not isinstance(entry, dict):
                continue
            role = entry.get('canonical_role')
            if not role:
                continue
            idx.setdefault((dhf_leaf, role), []).append(entry)
    return idx


def _composition_manifest_entry(row: dict, project_dir: Path) -> dict | None:
    """For (submission)-scope rows the generator already records
    `source_manifest` + `source_section` on the row. Build the bundle entry
    directly from those — no need to re-search."""
    src_manifest = row.get('source_manifest')
    if not src_manifest:
        return None
    name = row.get('name_token') or ''
    mf = project_dir / src_manifest if not Path(src_manifest).is_absolute() else Path(src_manifest)
    linked: list = []
    entry_line = ''
    if mf.is_file():
        try:
            text = mf.read_text(encoding='utf-8')
            for line in text.splitlines():
                if name and name.lower() in line.lower() and '|' in line:
                    entry_line = line.strip()
                    import re
                    links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', line)
                    linked = [target for _, target in links]
                    break
        except Exception:
            pass
    return {
        'path': src_manifest,
        'section': row.get('source_section'),
        'entry_text': entry_line,
        'linked_docs': linked,
    }


def _resolve_evidence_path(row: dict, project_dir: Path) -> Path | None:
    """Resolve the row's `path` field to an absolute filesystem path.
    Generator paths may be:
      - relative to docs/project/  (e.g., `_confluence/.../v1.0.0.md`)
      - relative to project root   (e.g., `docs/project/submissions/...`)
    Try both bases. Return None if the file doesn't exist or path is empty."""
    raw = (row.get('path') or '').strip()
    if not raw:
        return None
    candidates = [
        project_dir / 'docs/project' / raw,
        project_dir / raw,
    ]
    for c in candidates:
        if c.is_file():
            return c.resolve()
    return None


def build_bundle_for_row(row: dict,
                         dhfs_meta: list,
                         obligations_index: dict,
                         project_dir: Path) -> dict:
    """Build the per-row context bundle the help-author agent consumes."""
    iid = row.get('id')
    canonical_role = row.get('canonical_role') or ''
    dhf_leaf = row.get('dhf')  # may be None for (submission) rows
    bound = obligations_index.get((dhf_leaf, canonical_role), []) if dhf_leaf else []

    # Slim-down obligation entries to the fields the agent needs
    bound_slim = []
    for o in bound:
        bound_slim.append({
            'id': o.get('id'),
            'title': o.get('title'),
            'reg_source': o.get('reg_source') or o.get('source'),
            'criticality': o.get('criticality'),
            'extracted_requirements': o.get('extracted_requirements') or [],
        })

    evidence_path = _resolve_evidence_path(row, project_dir)
    evidence_rel = (
        str(evidence_path.relative_to(project_dir)) if evidence_path else None
    )
    evidence_hash = _sha256_file(evidence_path) if evidence_path else None

    manifest = _composition_manifest_entry(row, project_dir)

    # Display name: use name_token (the generator's slug). If the project
    # ever populates a richer display name (e.g., via .taxonomy.yml
    # display_name field — open enrichment), prefer that.
    display_name = row.get('display_name') or row.get('name') or row.get('name_token') or iid

    return {
        'row': {
            'id': iid,
            'display_name': display_name,
            'canonical_role': canonical_role,
            'scope': row.get('scope', ''),
            'phase': row.get('phase', ''),
            'status': row.get('status', ''),
            'dhf_leaf': dhf_leaf,
            'evidence_path': evidence_rel,
            'evidence_hash': evidence_hash,
            'composition_manifest': manifest,
            'bound_obligations': bound_slim,
        },
        'output_path': 'docs/project/submissions/submission-tracker.help.json',
    }


def main():
    p = argparse.ArgumentParser(
        description='/tracker enrich-help — per-row context bundle builder')
    p.add_argument('--project-dir', default=None,
                   help='Project root (default: auto-detect)')
    p.add_argument('--row', default=None,
                   help='Build a bundle for one row ID only')
    p.add_argument('--all', action='store_true',
                   help='Build bundles for every row')
    p.add_argument('--out', default=None,
                   help='Directory to write per-row .yaml bundles into '
                        '(default: stdout)')
    p.add_argument('--dry-run', action='store_true',
                   help='Counts only; no bundle output')
    args = p.parse_args()

    if not (args.row or args.all):
        sys.stderr.write('ERROR: pass --row <id> or --all\n')
        return 2

    gen = _load_generate_module()
    project_dir = Path(args.project_dir) if args.project_dir else gen.find_project_dir()
    rows, dhfs_meta, _ = gen.generate_rows(project_dir)

    catalog = _load_catalog(project_dir)
    obligations_index = _index_obligations_by_dhf_role(catalog)

    if args.row:
        rows = [r for r in rows if r.get('id') == args.row]
        if not rows:
            sys.stderr.write(f'ERROR: row {args.row!r} not found in inventory\n')
            return 1

    if args.dry_run:
        def _key(r):
            return (r.get('dhf'), r.get('canonical_role', ''))
        bound_count = sum(len(obligations_index.get(_key(r), [])) for r in rows)
        with_bound = sum(1 for r in rows if obligations_index.get(_key(r)))
        evidence_count = sum(1 for r in rows if _resolve_evidence_path(r, project_dir))
        manifest_count = sum(1 for r in rows
                             if _composition_manifest_entry(r, project_dir))
        print(f'rows: {len(rows)}')
        print(f'  with bound obligations: {with_bound}')
        print(f'  total bound-obligation entries: {bound_count}')
        print(f'  with resolved evidence path: {evidence_count}')
        print(f'  with composition-manifest entry: {manifest_count}')
        return 0

    # Build bundles
    bundles = []
    for r in rows:
        b = build_bundle_for_row(r, dhfs_meta, obligations_index, project_dir)
        bundles.append(b)

    if args.out:
        out_dir = Path(args.out)
        out_dir.mkdir(parents=True, exist_ok=True)
        try:
            import yaml  # type: ignore
            dump = lambda obj: yaml.safe_dump(obj, sort_keys=False, allow_unicode=True)
        except ImportError:
            # Fall back to JSON if PyYAML isn't available
            dump = lambda obj: json.dumps(obj, indent=2)
        for b in bundles:
            iid = b['row']['id']
            (out_dir / f'{iid}.yaml').write_text(dump(b), encoding='utf-8')
        print(f'Wrote {len(bundles)} bundles to {out_dir}', file=sys.stderr)
    else:
        try:
            import yaml  # type: ignore
            for b in bundles:
                print('---')
                print(yaml.safe_dump(b, sort_keys=False, allow_unicode=True), end='')
        except ImportError:
            for b in bundles:
                print(json.dumps(b, indent=2))
                print()
    return 0


if __name__ == '__main__':
    sys.exit(main())
