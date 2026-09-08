#!/usr/bin/env python3
"""
/tracker build-draft-context — per-row draft-context bundle builder (B6).

Deterministic helper for the draft-author agent (`agents/draft-author.md`).
Walks project state for one row and emits a YAML/JSON bundle the agent
consumes when proposing an outline. The agent itself decides what to read
beyond the bundle (it follows the discovery rubric in its system prompt).

Output bundle shape (YAML):

    row:
      id, display_name, canonical_role, scope, phase, status, dhf_leaf,
      evidence_path, composition_manifest, bound_obligations
    help_sidecar:           # if submission-tracker.help.json has an entry
      description, why_important_in_project, main_topics, regulatory_anchors
    detail_sidecar:         # if details.json has an entry (deterministic)
      ...
    discovery_seed:
      readme_index_paths:   [docs/**/README.md candidates relevant by scope]
      sibling_dhf_paths:    [resolved DHF roots from project.yml dhfs[]]
      strategy_domains:     [from project.yml strategy_domains[]]
      qms_search_roots:     [docs/internal/sops, docs/internal/templates]
      external_grounding_roots: [docs/external, .claude/skills/medtech-docs/references]
    output_target:
      staging_dir: _drafting
      tracker_md: docs/project/submissions/submission-tracker.md

Usage:
    python3 build-draft-context.py --row Q4
    python3 build-draft-context.py --row Q4 --out /tmp/draft-context.yaml
    python3 build-draft-context.py --row Q4 --json
"""

import argparse
import importlib.util
import json
import sys
from pathlib import Path


def _load_generate_module():
    here = Path(__file__).resolve().parent
    spec = importlib.util.spec_from_file_location('tracker_generate', here / 'generate.py')
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _load_help_sidecar(project_dir: Path) -> dict:
    p = project_dir / 'docs/project/submissions/submission-tracker.help.json'
    if not p.is_file():
        return {}
    try:
        return json.loads(p.read_text(encoding='utf-8'))
    except Exception:
        return {}


def _load_details_sidecar(project_dir: Path) -> dict:
    p = project_dir / 'docs/project/submissions/submission-tracker.details.json'
    if not p.is_file():
        return {}
    try:
        return json.loads(p.read_text(encoding='utf-8'))
    except Exception:
        return {}


def _load_catalog(project_dir: Path) -> dict:
    candidates = list((project_dir / 'docs/project/dhf-manifest').glob('*-dhf-manifest.json'))
    if not candidates:
        return {}
    try:
        return json.loads(candidates[0].read_text(encoding='utf-8'))
    except Exception:
        return {}


def _index_obligations_by_dhf_role(catalog: dict) -> dict:
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


def _read_project_yml(project_dir: Path) -> dict:
    p = project_dir / 'project.yml'
    if not p.is_file():
        return {}
    try:
        import yaml  # type: ignore
        return yaml.safe_load(p.read_text(encoding='utf-8')) or {}
    except Exception:
        return {}


def _readme_index_for_scope(project_dir: Path, dhf_leaf, scope: str) -> list:
    """Return README paths likely relevant for a row's scope. Best-effort —
    the agent may consult more during outline mode."""
    out = []
    candidates = [
        project_dir / 'docs/project/README.md',
        project_dir / 'docs/project/dhfs/README.md',
        project_dir / 'docs/project/submissions/README.md',
        project_dir / 'docs/project/strategies/README.md',
        project_dir / 'docs/project/input-analysis/README.md',
        project_dir / 'docs/internal/sops/README.md',
        project_dir / 'docs/internal/templates/README.md',
    ]
    if dhf_leaf:
        dhf_root = project_dir / 'docs/project/dhfs' / dhf_leaf
        candidates.extend([
            dhf_root / 'README.md',
            dhf_root / 'design-controls/README.md',
            dhf_root / 'risk-management/README.md',
            dhf_root / 'clinical/README.md',
            dhf_root / 'cybersecurity/README.md',
            dhf_root / 'postmarket/README.md',
        ])
    for c in candidates:
        if c.is_file():
            out.append(str(c.relative_to(project_dir)))
    return out


def _sibling_dhf_paths(proj_yml: dict) -> list:
    out = []
    for d in (proj_yml.get('dhfs') or []):
        path = d.get('path')
        if path:
            out.append({
                'leaf': d.get('architecture_name') or Path(path).name,
                'path': path,
                'role': d.get('role'),
            })
    return out


def _strategy_domains(proj_yml: dict) -> list:
    return [
        {
            'key': dom.get('key'),
            'name': dom.get('name'),
            'output_path': dom.get('output_path'),
        }
        for dom in (proj_yml.get('strategy_domains') or [])
        if dom.get('output_path')
    ]


def build_draft_bundle(row_id: str, project_dir: Path) -> dict:
    gen = _load_generate_module()
    rows, dhfs_meta, _ = gen.generate_rows(project_dir)
    # Same read-universe widening the help/detail builders use: rows hand-added
    # to submission-tracker.md render (and carry Create Draft buttons) but are
    # not pipeline rows, so without this merge every draft-eligible md-only row
    # fails with "not found in inventory". Invariant: if it renders, it can be
    # drafted.
    rows = gen.merge_md_only_rows(rows, project_dir)
    matches = [r for r in rows if r.get('id') == row_id]
    if not matches:
        raise SystemExit(f'ERROR: row {row_id!r} not found in inventory')
    row = matches[0]

    catalog = _load_catalog(project_dir)
    obligations = _index_obligations_by_dhf_role(catalog)
    dhf_leaf = row.get('dhf')
    bound = obligations.get((dhf_leaf, row.get('canonical_role') or ''), []) if dhf_leaf else []
    bound_slim = [
        {
            'id': o.get('id'),
            'title': o.get('title'),
            'reg_source': o.get('reg_source') or o.get('source'),
            'criticality': o.get('criticality'),
            'qms_grounding': o.get('qms_grounding'),
            'applies_to': o.get('applies_to'),
            'extracted_requirements': o.get('extracted_requirements') or [],
        }
        for o in bound
    ]

    help_map = _load_help_sidecar(project_dir)
    details_map = _load_details_sidecar(project_dir)
    proj_yml = _read_project_yml(project_dir)

    bundle = {
        'row': {
            'id': row_id,
            'display_name': row.get('display_name') or row.get('name') or row.get('name_token') or row_id,
            'canonical_role': row.get('canonical_role'),
            'scope': row.get('scope'),
            'phase': row.get('phase'),
            'status': row.get('status'),
            'dhf_leaf': dhf_leaf,
            'evidence_path': row.get('path') or None,
            'composition_manifest': {
                'path': row.get('source_manifest'),
                'section': row.get('source_section'),
            } if row.get('source_manifest') else None,
            'bound_obligations': bound_slim,
        },
        'help_sidecar': help_map.get(row_id),
        'detail_sidecar': details_map.get(row_id),
        'discovery_seed': {
            'readme_index_paths': _readme_index_for_scope(project_dir, dhf_leaf, row.get('scope') or ''),
            'sibling_dhf_paths': _sibling_dhf_paths(proj_yml),
            'strategy_domains': _strategy_domains(proj_yml),
            'qms_search_roots': ['docs/internal/sops', 'docs/internal/templates'],
            'external_grounding_roots': [
                'docs/external',
                '.claude/skills/medtech-docs/references',
                '.claude/skills/dhf-manifest/data',
            ],
            'confluence_mirror_root': 'docs/project/_confluence',
        },
        'output_target': {
            'staging_dir': '_drafting',
            'tracker_md': 'docs/project/submissions/submission-tracker.md',
        },
    }
    return bundle


def main():
    p = argparse.ArgumentParser(
        description='/tracker build-draft-context — per-row draft-context bundle (B6)'
    )
    p.add_argument('--project-dir', default=None,
                   help='Project root (default: auto-detect via CLAUDE.md)')
    p.add_argument('--row', required=True, help='Row ID, e.g., Q4')
    p.add_argument('--out', default=None,
                   help='Write bundle to this file (default: stdout)')
    p.add_argument('--json', action='store_true',
                   help='Emit JSON instead of YAML (always JSON if PyYAML is missing)')
    args = p.parse_args()

    gen = _load_generate_module()
    project_dir = Path(args.project_dir) if args.project_dir else gen.find_project_dir()
    bundle = build_draft_bundle(args.row, project_dir)

    if args.json:
        text = json.dumps(bundle, indent=2)
    else:
        try:
            import yaml  # type: ignore
            text = yaml.safe_dump(bundle, sort_keys=False, allow_unicode=True)
        except ImportError:
            text = json.dumps(bundle, indent=2)

    if args.out:
        Path(args.out).write_text(text, encoding='utf-8')
        print(f'Wrote bundle to {args.out}', file=sys.stderr)
    else:
        sys.stdout.write(text)
    return 0


if __name__ == '__main__':
    sys.exit(main())
