#!/usr/bin/env python3
"""
/tracker enrich-details — context bundle builder.

Deterministic helper for the details-author agent fan-out. Walks the project
state (project.yml, milestone catalogs, composition manifests, dhf-manifest
catalog, taxonomy, resolved evidence paths) and emits one YAML context
bundle per tracker row. The orchestrator (Claude) reads these bundles and
dispatches one details-author agent per row-group in parallel.

Usage:
    # All rows → emit one bundle each to stdout (newline-separated YAML docs)
    python3 build-detail-context.py --all

    # One row → emit just that row's bundle
    python3 build-detail-context.py --row PP1

    # Write bundles to a directory (one .yaml per row) for the dispatcher
    python3 build-detail-context.py --all --out /tmp/tracker-detail-bundles/

    # Dry-run (counts only)
    python3 build-detail-context.py --all --dry-run

This script is deterministic and side-effect-light:
  - Reads only; never writes to project state.
  - The output bundle does NOT include the resolved evidence file's CONTENT
    (the agent reads its frontmatter itself with the path we provide). It
    does include the file's hash (sha256) so the agent can stamp the
    cache signature.
  - Each bundle declares `linked_row_ids` — rows that share the same
    artifact (same resolved evidence_path or same composition-manifest
    entry_text). The agent emits one entry attaching to all linked rows.
"""

import argparse
import hashlib
import importlib.util
import json
import re
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


def _sha256_text(s: str) -> str:
    h = hashlib.sha256()
    h.update(s.encode('utf-8'))
    return f'sha256:{h.hexdigest()}'


def _load_catalog(project_dir: Path) -> dict:
    """Load the dhf-manifest catalog. Returns {} if missing."""
    candidates = list((project_dir / 'docs/project/dhf-manifest').glob('*-dhf-manifest.json'))
    if not candidates:
        return {}
    return json.loads(candidates[0].read_text(encoding='utf-8'))


def _index_obligations_by_dhf_role(catalog: dict) -> dict:
    """Build {(dhf_leaf, canonical_role): [obligation_entries]} index."""
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
    """Same shape as build-help-context.py — the agent uses this to confirm
    the entry_text and to read the surrounding section heading."""
    src_manifest = row.get('source_manifest')
    if not src_manifest:
        return None
    name = row.get('name_token') or ''
    mf = project_dir / src_manifest if not Path(src_manifest).is_absolute() else Path(src_manifest)
    linked: list = []
    entry_line = ''
    section_text = ''
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
            # Capture the surrounding ### section heading + a hash of that
            # section's body for cache-signature use.
            section_text = _surrounding_section(text, entry_line) if entry_line else ''
        except Exception:
            pass
    return {
        'path': src_manifest,
        'section': row.get('source_section'),
        'entry_text': entry_line,
        'linked_docs': linked,
        'section_signature': _sha256_text(section_text) if section_text else None,
    }


def _surrounding_section(manifest_text: str, entry_line: str) -> str:
    """Return the body of the `### ...` section that contains entry_line."""
    if not entry_line:
        return ''
    lines = manifest_text.splitlines()
    section_start = -1
    section_end = len(lines)
    found_in = -1
    for i, ln in enumerate(lines):
        if ln.startswith('### '):
            if found_in == -1:
                section_start = i
            else:
                section_end = i
                break
        if ln.strip() == entry_line.strip() and found_in == -1:
            found_in = i
    if found_in == -1 or section_start == -1:
        return ''
    return '\n'.join(lines[section_start:section_end])


def _resolve_evidence_path(row: dict, project_dir: Path) -> Path | None:
    """Resolve the row's `path` field to an absolute filesystem path."""
    raw = (row.get('path') or '').strip()
    if not raw:
        return None
    # Path cells may be markdown links `[label](target)` — extract the target.
    m = re.search(r'\]\(([^)]+)\)', raw)
    if m:
        raw = m.group(1).strip()
    # Skip non-file targets (action buttons, external URLs, pure anchors).
    if not raw or raw.startswith(('http://', 'https://', '#', '<')):
        return None
    # Tracker row paths are written relative to the tracker file's home
    # (docs/project/submissions/); also try docs/project/ and repo root.
    candidates = [
        project_dir / 'docs/project/submissions' / raw,
        project_dir / 'docs/project' / raw,
        project_dir / raw,
    ]
    for c in candidates:
        try:
            rc = c.resolve()
        except Exception:
            continue
        if rc.is_file():
            return rc
    return None


def _row_path_str(row: dict) -> str:
    """Strip markdown link wrapping from the row's path column for grouping."""
    raw = (row.get('path') or '').strip()
    # `[label](target)` → target
    if raw.startswith('[') and '](' in raw and raw.endswith(')'):
        try:
            return raw.split('](', 1)[1][:-1]
        except Exception:
            return raw
    return raw


def _build_link_groups(rows: list, project_dir: Path) -> dict:
    """Group rows by shared artifact key. Returns {row_id: [linked_row_ids]}.

    Two rows share an artifact when:
      - Their resolved evidence path is the same (same file on disk), OR
      - They reference the same composition-manifest entry_text, OR
      - Their raw path strings (post-link-strip) are equal and non-empty.

    A row's own id is NOT included in its linked_row_ids list — the
    caller adds it as the primary.
    """
    keys: dict = {}  # key → [row_ids]
    row_keys: dict = {}  # row_id → set of keys it belongs to

    for r in rows:
        rid = r.get('id')
        if not rid:
            continue
        keys_for_row: set = set()

        ev = _resolve_evidence_path(r, project_dir)
        if ev:
            keys_for_row.add(('evidence', str(ev)))

        path_str = _row_path_str(r)
        if path_str:
            keys_for_row.add(('path', path_str))

        manifest = _composition_manifest_entry(r, project_dir)
        if manifest and manifest.get('entry_text'):
            keys_for_row.add(('manifest_entry', manifest['entry_text']))

        for k in keys_for_row:
            keys.setdefault(k, []).append(rid)
        row_keys[rid] = keys_for_row

    linked: dict = {}
    for rid, key_set in row_keys.items():
        peers: set = set()
        for k in key_set:
            peers.update(keys.get(k, []))
        peers.discard(rid)
        # Only include peers IF the linkage is via evidence/manifest_entry.
        # `path` linkage alone is reliable when paths are non-empty + equal,
        # but the shared-evidence and shared-manifest-entry are stronger
        # signals — keep them all but we already filtered noise above.
        linked[rid] = sorted(peers)
    return linked


def build_bundle_for_row(row: dict,
                         dhfs_meta: list,
                         obligations_index: dict,
                         linked_map: dict,
                         project_dir: Path) -> dict:
    """Build the per-row context bundle the details-author agent consumes."""
    iid = row.get('id')
    canonical_role = row.get('canonical_role') or ''
    dhf_leaf = row.get('dhf')
    bound = obligations_index.get((dhf_leaf, canonical_role), []) if dhf_leaf else []

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

    display_name = (
        row.get('display_name') or row.get('name')
        or row.get('name_token') or iid
    )

    return {
        'row': {
            'id': iid,
            'display_name': display_name,
            'canonical_role': canonical_role,
            'scope': row.get('scope', ''),
            'phase': row.get('phase', ''),
            'status': row.get('status', ''),
            'dhf_leaf': dhf_leaf,
            'path': _row_path_str(row) or None,
            'primary_ref': row.get('ref', ''),
            'evidence_path': evidence_rel,
            'evidence_hash': evidence_hash,
            'linked_row_ids': linked_map.get(iid, []),
            'composition_manifest': manifest,
            'bound_obligations': bound_slim,
        },
        'output_path': 'docs/project/submissions/submission-tracker.details.json',
    }


def main():
    p = argparse.ArgumentParser(
        description='/tracker enrich-details — per-row context bundle builder')
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
    # Option C: widen the inventory to every row that renders — including rows
    # hand-added directly to submission-tracker.md — so "if it renders, it can
    # be enriched" holds for details too.
    rows = gen.merge_md_only_rows(rows, project_dir)

    catalog = _load_catalog(project_dir)
    obligations_index = _index_obligations_by_dhf_role(catalog)
    linked_map = _build_link_groups(rows, project_dir)

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
        # Group count (de-duplicated dispatch units)
        seen_groups: set = set()
        for r in rows:
            rid = r.get('id')
            peers = linked_map.get(rid, [])
            group = tuple(sorted([rid, *peers]))
            seen_groups.add(group)
        print(f'rows: {len(rows)}')
        print(f'  with bound obligations: {with_bound}')
        print(f'  total bound-obligation entries: {bound_count}')
        print(f'  with resolved evidence path: {evidence_count}')
        print(f'  with composition-manifest entry: {manifest_count}')
        print(f'  unique row-groups (dispatch units): {len(seen_groups)}')
        return 0

    bundles = []
    for r in rows:
        b = build_bundle_for_row(r, dhfs_meta, obligations_index, linked_map, project_dir)
        bundles.append(b)

    if args.out:
        out_dir = Path(args.out)
        out_dir.mkdir(parents=True, exist_ok=True)
        try:
            import yaml  # type: ignore
            dump = lambda obj: yaml.safe_dump(obj, sort_keys=False, allow_unicode=True)
        except ImportError:
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
