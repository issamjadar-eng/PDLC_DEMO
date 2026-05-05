#!/usr/bin/env python3
"""
/tracker generate — deterministic row inventory from source-of-truth inputs.

R9 from task ben/154 — first checkpoint (R9.1). Reads:
  * docs/project/milestones/regulatory.yml — milestone catalog with bindings
  * docs/project/_confluence/.taxonomy.yml — canonical-role mapping
  * project.yml dhfs[] + tracker config block — DHF metadata + ID schema
  * docs/project/dhf-manifest/<slug>-dhf-manifest.json — Tier 4 obligations
    (when present; obligation anchoring deferred to R8)

Produces a JSON inventory of rows the tracker SHOULD contain, with
deterministic IDs derived from the row_id_schema in project.yml.

Usage:
    python3 generate.py [--project-dir PATH] [--out PATH] [--md]

Options:
  --project-dir PATH   Project root (default: detected via CLAUDE.md walk)
  --out PATH           Write JSON to file (default: stdout)
  --md                 Emit markdown row table to stdout instead of JSON
                       (R9.2 — markdown emission; minimal for now)
  --dry-run            Show counts only; don't emit rows

Future iterations:
  R9.2 — full markdown emission (replacing hand-built submission-tracker.md)
  R9.3 — round-trip preservation via submission-tracker.human.json overlay
  R9.4 — composition manifest integration for (submission)-scope rows
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

# stdlib YAML — we use the same lightweight regex approach render.py uses
# rather than adding a yaml dependency. For deeper YAML parsing we shell
# out to python -c "import yaml..." with the project-console venv.


def find_project_dir(start=None):
    d = Path(start or os.getcwd())
    for _ in range(10):
        if (d / 'CLAUDE.md').exists():
            return d
        if d.parent == d:
            break
        d = d.parent
    return Path(os.getcwd())


def load_yaml(path):
    """Load YAML using PyYAML when available, fail loudly otherwise."""
    try:
        import yaml  # noqa: F401
    except ImportError:
        sys.stderr.write(
            f"ERROR: PyYAML not available. Install in the project-console venv:\n"
            f"  cd tools/project-console && uv add pyyaml\n"
            f"Or invoke this script via:\n"
            f"  uv run --project tools/project-console python {sys.argv[0]}\n"
        )
        sys.exit(2)
    import yaml
    with open(path) as f:
        return yaml.safe_load(f)


# ─── Row ID generation ───

def dhf_prefix(leaf, schema):
    """Resolve DHF leaf → ID prefix per project.yml row_id_schema."""
    dhf_map = (schema or {}).get('dhf_prefix_map', {}) or {}
    if leaf in dhf_map:
        return dhf_map[leaf]
    # Fallback strategy: first 2 letters of leaf, uppercased, dashes stripped
    cleaned = re.sub(r'[^a-zA-Z]', '', leaf)
    return (cleaned[:2] or 'XX').upper()


# R9.8: CANONICAL_ROLE_INDEX is the medtech-IEC-62304 default. Projects
# override via project.yml `tracker.canonical_role_index`. Pharma IND would
# replace with CTD-Module-shaped roles (m1-administrative=1, m2-summaries=2,
# m3-quality=3, m4-nonclinical=4, m5-clinical=5, ...). The skill ships a
# medtech default; pharma/IVD/etc. ship their own through project.yml.
DEFAULT_CANONICAL_ROLE_INDEX = {
    'architecture': 1,
    'requirements': 2,
    'design': 3,
    'vnv-plan': 4,
    'vnv-cases': 5,
    'vnv-results': 6,
    'vnv-defects': 7,
    'vnv-reliability': 8,
    'risk-management': 9,
    'trace-matrix-requirements': 10,
    'trace-matrix-hazard': 11,
    'cybersecurity': 12,
    'privacy': 13,
    'sbom': 14,
    'human-factors': 15,
    'tool-validation': 16,
    'plans-sdp': 17,
    'plans-deployment': 18,
    'plans-release': 19,
    'plans-version-id': 20,
    'plans-doc-level': 21,
    'plans-doc-overview': 22,
    'clinical': 23,
    'postmarket': 24,
    'user-needs': 25,
    'plans': 26,
    'vnv': 27,
    'trace-matrix': 28,
}

# Module-level mutable copy that load_project_role_index() updates from
# project.yml. Read by role_token() / generate_row_id().
CANONICAL_ROLE_INDEX = dict(DEFAULT_CANONICAL_ROLE_INDEX)


def load_project_role_index(tracker_cfg):
    """R9.8: Apply project.yml `tracker.canonical_role_index` overrides on
    top of the medtech default. Project may add new roles, replace existing
    indices, or leave the default in place."""
    overrides = (tracker_cfg or {}).get('canonical_role_index', {}) or {}
    if not overrides:
        return  # use default as-is
    # Reset and rebuild so removals are honored too (project.yml is the
    # canonical list when present)
    global CANONICAL_ROLE_INDEX
    if isinstance(overrides, dict):
        CANONICAL_ROLE_INDEX = dict(overrides)
    elif isinstance(overrides, list):
        # Support list-of-{role, index} form for ordered authoring
        CANONICAL_ROLE_INDEX = {entry['role']: entry['index'] for entry in overrides}


# R9.8: SYSTEM_DHF_ROLE_MAP is the medtech-IEC-62304 default folder layout.
# Projects override via project.yml `tracker.system_dhf_layout`. Pharma IND
# would map CTD module folders (m1-administrative/, m2-summaries/, m3-quality/,
# m4-nonclinical/, m5-clinical/) → canonical roles. Each entry: (sub_path,
# canonical_role, subkind). The skill ships a medtech default; non-medtech
# projects ship their own through project.yml.
DEFAULT_SYSTEM_DHF_ROLE_MAP = [
    ('design-controls/architecture', 'architecture', None),
    ('design-controls/plans', 'plans', None),
    ('design-controls/user-needs', 'user-needs', None),
    ('design-controls/requirements', 'requirements', None),
    ('design-controls/vnv', 'vnv', None),
    ('design-controls/trace-matrix', 'trace-matrix', None),
    ('design-controls/tool-validation', 'tool-validation', None),
    ('risk-management', 'risk-management', None),
    ('clinical', 'clinical', None),
    ('postmarket', 'postmarket', None),
    ('cybersecurity', 'cybersecurity', None),
]

SYSTEM_DHF_ROLE_MAP = list(DEFAULT_SYSTEM_DHF_ROLE_MAP)


def load_project_system_dhf_layout(tracker_cfg):
    """R9.8: Apply project.yml `tracker.system_dhf_layout` overrides. Each
    entry can be a dict {sub_path, canonical_role, subkind?} or a 2/3-tuple."""
    overrides = (tracker_cfg or {}).get('system_dhf_layout', None)
    if overrides is None:
        return
    global SYSTEM_DHF_ROLE_MAP
    layout = []
    for entry in overrides:
        if isinstance(entry, dict):
            layout.append((entry['sub_path'], entry['canonical_role'], entry.get('subkind')))
        elif isinstance(entry, (list, tuple)):
            sub_path = entry[0]
            canonical_role = entry[1]
            subkind = entry[2] if len(entry) > 2 else None
            layout.append((sub_path, canonical_role, subkind))
    SYSTEM_DHF_ROLE_MAP = layout


def role_token(canonical_role, subkind=None):
    """Build the role lookup token (matches CANONICAL_ROLE_INDEX keys)."""
    if subkind and canonical_role in ('vnv', 'plans', 'trace-matrix', 'sbom'):
        return f'{canonical_role}-{subkind}'
    return canonical_role


def generate_row_id(prefix, canonical_role, subkind=None, milestone_prefix=None):
    """Deterministic row ID: [<milestone-prefix>-]<dhf-prefix><role-index>"""
    token = role_token(canonical_role, subkind)
    idx = CANONICAL_ROLE_INDEX.get(token)
    if idx is None:
        # Unknown role — degrade gracefully with a hash-suffixed fallback
        idx = abs(hash(token)) % 99 + 90  # 90-188 range
    base = f'{prefix}{idx}'
    return f'{milestone_prefix}-{base}' if milestone_prefix else base


# ─── Source readers ───

def read_dhfs(project_yml_path):
    """Load dhfs[] from project.yml — leaf, architecture_name, marketed_name,
    role, dhf_organization, taxonomy_path, classification, etc."""
    pyl = load_yaml(project_yml_path)
    dhfs = pyl.get('dhfs', []) or []
    tracker_cfg = pyl.get('tracker', {}) or {}
    return dhfs, tracker_cfg


def read_milestones(milestones_yml_path):
    """Load milestones from milestones/regulatory.yml."""
    if not Path(milestones_yml_path).exists():
        return []
    cat = load_yaml(milestones_yml_path)
    return cat.get('milestones', []) or []


def read_engineering_milestones(engineering_yml_path):
    """R9.5: Load engineering milestones from milestones/engineering.yml.
    Returns [] when the file is absent (engineering catalog is optional;
    projects without cross-cutting engineering prereqs simply don't have
    one)."""
    if not Path(engineering_yml_path).exists():
        return []
    cat = load_yaml(engineering_yml_path)
    return cat.get('milestones', []) or []


def discover_engineering_rows(engineering_milestones, schema, display_cfg=None):
    """R9.5: Walk engineering milestones × bindings; emit ENG-prefixed rows.
    Engineering rows are project-specific cross-cutting capabilities that
    don't derive from DHF evidence — they're declared in engineering.yml and
    carry their own ID + status + unblocks list. The id is taken verbatim
    from the binding (already ENG-prefixed per project convention)."""
    eng_prefix = (schema or {}).get('engineering_prefix', 'ENG')
    rows = []
    for ms in engineering_milestones:
        # Engineering "milestone" links to a regulatory milestone via
        # prerequisites; the tracker treats that linked milestone as the
        # row's Phase. Default to first prerequisite found. Phase label
        # honors tracker.display.phase_label_overrides for HCLS portability.
        target_phase = 'engineering'
        target_milestone_id = ms.get('id', 'engineering')
        for prereq in ms.get('prerequisites', []) or []:
            target_milestone_id = prereq.get('milestone', target_milestone_id)
            target_phase = _phase_for_milestone(target_milestone_id, target_milestone_id, display_cfg)
            break
        for binding in ms.get('bindings', []) or []:
            rid = binding.get('id') or f'{eng_prefix}{len(rows) + 1}'
            rows.append({
                'id': rid,
                'milestone': target_milestone_id,
                'milestone_short': target_phase,
                'dhf': None,
                'scope': binding.get('scope', 'Suite'),
                'phase': target_phase,
                'canonical_role': 'engineering-prereq',
                'subkind': None,
                'name_token': binding.get('capability', ''),
                'version': 'current',
                'path': None,
                'required': True,
                'effort': binding.get('effort'),
                'unblocks': binding.get('unblocks', []) or [],
                'engineering_status': binding.get('status'),
                'notes': binding.get('notes'),
            })
    return rows


def read_taxonomy(taxonomy_yml_path):
    """Load canonical-role mappings from _confluence/.taxonomy.yml."""
    if not taxonomy_yml_path or not Path(taxonomy_yml_path).exists():
        return None
    return load_yaml(taxonomy_yml_path)


# ─── Model D: user-injected rows from the registry ───
#
# `tracker-user-rows.yml` holds rows that don't derive from the milestone
# catalog × composition manifests × DHF evidence pipeline. The registry is
# machine-managed (edited via /tracker add-row, /tracker update-row,
# /tracker remove-row, /tracker import-user-rows). Each entry carries an
# explicit `reason` plus auto-managed `_meta` block. Schema:
# `.claude/skills/tracker/schemas/user-row.schema.yml`.
#
# These rows merge into the row inventory alongside catalog-derived rows.
# Their `source_kind` is recorded in submission-tracker.row-source.json so
# render.py and downstream consumers can surface a "user-added" badge.

USER_ROWS_REL = 'docs/project/submissions/tracker-user-rows.yml'


def read_user_rows(project_dir, milestones=None):
    """Load `tracker-user-rows.yml` and convert each entry to the row shape
    that generate_rows() produces. Returns ([], None) when the registry is
    absent (projects with no user-injected rows). Returns (rows, raw_entries)
    where raw_entries is the original entry list (used by the row-source
    sidecar emitter for `reason` and `_meta` provenance).

    Honors `TRACKER_SKIP_USER_ROWS` env var: when set to '1' (validator
    collision-check uses this), returns ([], None) without reading the
    registry. This breaks the chicken-and-egg between validator
    collision-check and the merged generator inventory."""
    import os
    if os.environ.get('TRACKER_SKIP_USER_ROWS') == '1':
        return [], None
    path = Path(project_dir) / USER_ROWS_REL
    if not path.is_file():
        return [], None
    data = load_yaml(path)
    if not isinstance(data, dict):
        return [], None
    raw_entries = data.get('rows', []) or []
    if not isinstance(raw_entries, list):
        return [], None

    # Index milestones by short_label for phase → milestone_id resolution
    ms_by_short = {}
    if milestones:
        for m in milestones:
            short = m.get('short_label') or m.get('name')
            if short:
                ms_by_short[short] = m

    rows = []
    for entry in raw_entries:
        if not isinstance(entry, dict) or not entry.get('id'):
            continue
        phase_label = entry.get('phase', '') or ''
        ms = ms_by_short.get(phase_label, {})
        rows.append({
            'id': entry['id'],
            'milestone': ms.get('id', phase_label.lower().replace(' ', '-')),
            'milestone_short': phase_label,
            'dhf': None,                         # user rows don't bind to a DHF
            'scope': entry.get('scope', ''),
            'phase': phase_label,
            'canonical_role': 'user-injected',
            'subkind': entry.get('kind', 'deliverable'),
            'name_token': entry.get('name', ''),
            'name': entry.get('name', ''),
            'version': 'current',
            'path': entry.get('path'),
            'ref': entry.get('ref'),
            'effort': entry.get('effort'),
            'status': entry.get('status'),
            'required': True,
            # Provenance markers — read by emit_row_source_sidecar()
            'source_kind': 'user',
            'source_reason': entry.get('reason'),
            'source_kind_meta': entry.get('_meta'),
            'related_catalog_row': entry.get('related_catalog_row'),
            'linked_row_ids': entry.get('linked_row_ids', []) or [],
            'kind': entry.get('kind', 'deliverable'),
        })
    return rows, raw_entries


ROW_SOURCE_SIDECAR_REL = 'docs/project/submissions/submission-tracker.row-source.json'


def emit_row_source_sidecar(rows, project_dir):
    """Write submission-tracker.row-source.json: per-row `source_kind` so
    render.py can add a `data-source` attribute and a small "user-added"
    badge on user-injected rows. Catalog-derived rows are tagged `derived`
    with their (milestone, dhf) provenance for traceability."""
    sidecar = {}
    for r in rows:
        rid = r.get('id')
        if not rid:
            continue
        if r.get('source_kind') == 'user':
            sidecar[rid] = {
                'source_kind': 'user',
                'reason': r.get('source_reason'),
                '_meta': r.get('source_kind_meta'),
                'related_catalog_row': r.get('related_catalog_row'),
            }
        else:
            sidecar[rid] = {
                'source_kind': 'derived',
                'from_milestone': r.get('milestone'),
                'from_dhf': r.get('dhf'),
                'canonical_role': r.get('canonical_role'),
            }
    out_path = Path(project_dir) / ROW_SOURCE_SIDECAR_REL
    out_path.write_text(
        json.dumps({
            'schema_version': '0.1',
            'generated_by': '/tracker generate (Model D row-source sidecar)',
            'rows': sidecar,
        }, indent=2) + '\n',
        encoding='utf-8',
    )
    return out_path


# ─── R9.3: Composition manifest parsing ───
#
# Each `docs/project/submissions/<filing>/composition-manifest.md` lists the
# pieces packaged for a filing. Most rows in those manifests reference DHF or
# Confluence evidence already discovered by the milestone walk. A subset is
# *submission-authored* — content unique to the filing (cover letter, 510(k)
# Summary, PCCP narrative, etc.) that doesn't live under any DHF. R9.3 parses
# those and emits (submission)-scope rows with stable IDs from the
# `tracker.row_id_schema.scope_prefixes` map.

# R9.8: MANIFEST_SUBMISSION_SECTIONS is the medtech-510k+PCCP default. Projects
# override via project.yml `tracker.manifest_submission_sections`. Pharma IND
# would supply [{"header_match": "Module 1: Administrative", "scope_prefix_key":
# "ind_admin", "milestone_id": "ind-submission"}, {"header_match": "Module 2.5:
# Clinical Overview", "scope_prefix_key": "clin_overview", "milestone_id":
# "ind-submission"}, ...].
DEFAULT_MANIFEST_SUBMISSION_SECTIONS = [
    ('Administrative & cover', 'submission_admin', 'pccp-release'),
    ('PCCP-specific narrative', 'submission_narrative', 'pccp-release'),
]

MANIFEST_SUBMISSION_SECTIONS = list(DEFAULT_MANIFEST_SUBMISSION_SECTIONS)


def load_project_manifest_sections(tracker_cfg):
    """R9.8: Apply project.yml `tracker.manifest_submission_sections` overrides.
    Each entry can be a dict with keys {header_match, scope_prefix_key,
    milestone_id} or a 3-tuple/list."""
    overrides = (tracker_cfg or {}).get('manifest_submission_sections', None)
    if overrides is None:
        return
    global MANIFEST_SUBMISSION_SECTIONS
    sections = []
    for entry in overrides:
        if isinstance(entry, dict):
            sections.append((
                entry['header_match'],
                entry['scope_prefix_key'],
                entry['milestone_id'],
            ))
        elif isinstance(entry, (list, tuple)) and len(entry) >= 3:
            sections.append((entry[0], entry[1], entry[2]))
    MANIFEST_SUBMISSION_SECTIONS = sections


def find_composition_manifests(project_dir):
    """Return list of (filing_id, manifest_path) for each submission filing."""
    submissions_dir = Path(project_dir) / 'docs/project/submissions'
    if not submissions_dir.is_dir():
        return []
    out = []
    for filing_dir in sorted(submissions_dir.iterdir()):
        if not filing_dir.is_dir():
            continue
        manifest = filing_dir / 'composition-manifest.md'
        if manifest.is_file():
            out.append((filing_dir.name, manifest))
    return out


def parse_manifest_section_rows(manifest_path):
    """Walk a composition-manifest.md, yield (section_header, [row_cells]) for
    each markdown table found under a `### <Section>` heading."""
    text = manifest_path.read_text()
    lines = text.splitlines()

    sections = []
    current_header = None
    in_table = False
    table_rows = []
    pending_after_separator = False

    for line in lines:
        if line.startswith('## ') or line.startswith('### '):
            if current_header and table_rows:
                sections.append((current_header, table_rows))
            current_header = line.lstrip('#').strip()
            in_table = False
            table_rows = []
            pending_after_separator = False
            continue

        if not current_header:
            continue

        stripped = line.strip()
        if not in_table:
            if stripped.startswith('|') and stripped.endswith('|') and stripped.count('|') >= 2:
                in_table = True
                pending_after_separator = True
            continue
        if not (stripped.startswith('|') and stripped.endswith('|')):
            in_table = False
            pending_after_separator = False
            continue
        if pending_after_separator:
            pending_after_separator = False
            continue
        cells = [c.strip() for c in stripped.split('|')[1:-1]]
        if cells:
            table_rows.append(cells)

    if current_header and table_rows:
        sections.append((current_header, table_rows))

    return sections


def _strip_md_link(cell):
    """Extract display text from a markdown link cell. `[Cover letter](path)` →
    `Cover letter`. Plain text passes through."""
    m = re.match(r'^\[([^\]]+)\]\([^)]+\)(.*)$', cell.strip())
    if m:
        return (m.group(1) + m.group(2)).strip()
    return cell.strip()


def _extract_md_path(cell):
    """Extract URL from `[text](url)`, falling back to the first backticked
    `path/to/file.md` in the cell. Returns None if no path found."""
    m = re.search(r'\]\(([^)]+)\)', cell)
    if m:
        return m.group(1)
    m = re.search(r'`([^`]+\.md)`', cell)
    if m:
        return m.group(1)
    return None


def discover_submission_rows(project_dir, schema):
    """R9.3: Walk composition manifests; emit (submission)-scope rows for the
    submission-authored sections (admin/cover, PCCP narrative). Stable IDs from
    row_id_schema.scope_prefixes (PA1.., PC1..)."""
    scope_prefixes = (schema or {}).get('scope_prefixes', {}) or {}
    rows = []
    for filing_id, manifest_path in find_composition_manifests(project_dir):
        sections = parse_manifest_section_rows(manifest_path)
        seq_per_prefix = {}
        for header, table_rows in sections:
            match = next(
                (m for m in MANIFEST_SUBMISSION_SECTIONS if m[0].lower() in header.lower()),
                None,
            )
            if not match:
                continue
            _, prefix_key, milestone_id = match
            prefix = scope_prefixes.get(prefix_key, prefix_key.upper()[:2])
            for cells in table_rows:
                if len(cells) < 2:
                    continue
                piece_name = _strip_md_link(cells[0])
                if not piece_name or piece_name.lower() in ('piece', 'role'):
                    continue
                doc_path = _extract_md_path(cells[1]) if len(cells) > 1 else None
                purpose = cells[2] if len(cells) > 2 else ''
                seq_per_prefix[prefix] = seq_per_prefix.get(prefix, 0) + 1
                rid = f'{prefix}{seq_per_prefix[prefix]}'
                rows.append({
                    'id': rid,
                    'milestone': milestone_id,
                    'milestone_short': '510k+PCCP',
                    'dhf': None,
                    'scope': '(submission)',
                    'phase': '510k+PCCP',
                    'canonical_role': 'submission-authored',
                    'subkind': prefix_key,
                    'name_token': piece_name,
                    'version': 'current',
                    'path': doc_path,
                    'required': True,
                    'source_manifest': str(manifest_path.relative_to(project_dir)),
                    'source_section': header,
                    'purpose': purpose,
                })
    return rows


def discover_system_dhf_evidence(dhf, project_dir):
    """For an internal-mode (system) DHF, walk the canonical IEC-62304-shaped
    layout and yield (canonical_role, subkind, name, sub_path, versions[])
    for each folder that has substantive content (not just README).
    """
    base = (Path(project_dir) / dhf['path']) if not Path(dhf['path']).is_absolute() else Path(dhf['path'])
    if not base.is_dir():
        return []
    out = []
    for sub_path, canonical_role, subkind in SYSTEM_DHF_ROLE_MAP:
        folder = base / sub_path
        if not folder.is_dir():
            continue
        # Substantive content = at least one .md other than README.md
        md_files = sorted(p for p in folder.glob('*.md') if p.name.lower() != 'readme.md')
        # System DHF docs aren't versioned per file; treat folder as "current"
        if md_files:
            # Use the first non-README md as the canonical path; full set surfaced as evidence
            primary = md_files[0]
            versions = [{'id': 'current', 'path': str(primary.relative_to(project_dir))}]
            extra_paths = [str(p.relative_to(project_dir)) for p in md_files[1:]]
        else:
            # Folder exists but only README — emit row with status hint that content is missing
            versions = [{'id': 'current', 'path': str(folder.relative_to(project_dir)) + '/'}]
            extra_paths = []
        out.append({
            'canonical_role': canonical_role,
            'subkind': subkind,
            'name': folder.name,
            'sub_path': sub_path,
            'versions': versions,
            'extra_paths': extra_paths,
            'has_content': bool(md_files),
        })
    return out


def discover_evidence(dhf, taxonomy):
    """For an external-mode item DHF, walk path/discovery_root/ and yield
    (canonical_role, subkind, name, sub_path, versions[]) for each entry that
    maps to a canonical role per taxonomy. Returns [] for system DHFs or
    when the path doesn't exist.
    """
    if dhf.get('dhf_organization') != 'external':
        return []
    if not taxonomy:
        return []
    base = Path(dhf['path'])
    discovery_root = taxonomy.get('discovery_root', '')
    walk_dir = base / discovery_root if discovery_root else base
    if not walk_dir.is_dir():
        return []

    mappings = taxonomy.get('mappings', {}) or {}
    out = []
    for entry in sorted(walk_dir.iterdir()):
        name = entry.name
        m = mappings.get(name) or mappings.get(name.replace('.md', ''))
        if not m or 'unmapped' in m:
            continue
        canonical_role = m['canonical_role']
        subkind = m.get('subkind')
        # Detect available versions
        versions = []
        if entry.is_file() and entry.suffix == '.md':
            versions.append({'id': 'current', 'path': str(entry.relative_to(walk_dir.parent.parent.parent))})
        elif entry.is_dir():
            for v in sorted(entry.iterdir()):
                if v.name.endswith('.md') and v.name.startswith('v'):
                    vid = v.name.replace('.md', '')
                    versions.append({'id': vid, 'path': str(v.relative_to(walk_dir.parent.parent.parent))})
                elif v.is_dir() and v.name.startswith('v'):
                    # SDD-style folder — version is folder name
                    versions.append({'id': v.name, 'path': str(v.relative_to(walk_dir.parent.parent.parent))})
        if not versions:
            versions.append({'id': 'unknown', 'path': str(entry.relative_to(walk_dir.parent.parent.parent))})
        out.append({
            'canonical_role': canonical_role,
            'subkind': subkind,
            'name': name,
            'versions': versions,
        })
    return out


# ─── Generator ───

def generate_rows(project_dir):
    """Walk milestones × DHFs × evidence to produce row inventory."""
    project_dir = Path(project_dir)
    project_yml = project_dir / 'project.yml'
    milestones_yml = project_dir / 'docs/project/milestones/regulatory.yml'
    engineering_yml = project_dir / 'docs/project/milestones/engineering.yml'

    dhfs, tracker_cfg = read_dhfs(project_yml)
    milestones = read_milestones(milestones_yml)
    engineering_milestones = read_engineering_milestones(engineering_yml)
    schema = tracker_cfg.get('row_id_schema', {}) or {}
    display_cfg = tracker_cfg.get('display', {}) or {}
    # R9.8 portability: apply project.yml overrides for the three medtech-shaped
    # default lookup tables. Pharma/IVD/etc. supply their own canonical roles,
    # system-DHF folder layout, and manifest section labels via project.yml.
    load_project_role_index(tracker_cfg)
    load_project_system_dhf_layout(tracker_cfg)
    load_project_manifest_sections(tracker_cfg)

    # Index DHFs by leaf for quick lookup
    dhfs_by_leaf = {d['leaf']: d for d in dhfs}

    # Pre-load taxonomies (shared across DHFs typically)
    taxonomies = {}
    for d in dhfs:
        tx_path = d.get('taxonomy_path')
        if tx_path and tx_path not in taxonomies:
            taxonomies[tx_path] = read_taxonomy(project_dir / tx_path)

    rows = []

    # R9.3: (submission)-scope rows from composition manifests (admin/cover +
    # PCCP narrative). Emitted before the milestone walk so PA/PC IDs are
    # stable regardless of milestone walk ordering.
    rows.extend(discover_submission_rows(project_dir, schema))

    # R9.5: Engineering Prerequisites from milestones/engineering.yml.
    # Cross-cutting capabilities that one or more design-control rows depend
    # on; carry their own ENG-prefixed IDs and unblocks lists.
    rows.extend(discover_engineering_rows(engineering_milestones, schema, display_cfg))

    # Model D: user-injected rows from tracker-user-rows.yml.
    # Rows that don't derive from the catalog × manifest × evidence pipeline
    # but live in the registry (machine-managed via /tracker add-row etc.).
    # Merging here keeps them ordered after engineering and before per-DHF
    # walks — matches the canonical hand-curated tracker's row ordering.
    user_rows, _user_raw = read_user_rows(project_dir, milestones)
    rows.extend(user_rows)

    for ms in milestones:
        ms_id = ms.get('id', '')
        ms_short = ms.get('name', ms_id).split()[0]  # "QSub Release" → "QSub"
        ms_prefix_map = {
            'qsub-release': 'Q',
            'lmr1-release': 'L1',
            'lmr2-release': 'L2',
            # pccp-release uses no milestone prefix (it's the baseline; PS1, PP1, etc.)
        }
        ms_prefix = ms_prefix_map.get(ms_id, '')

        for binding in ms.get('bindings', []) or []:
            dhf_leaf = binding.get('dhf')
            doc_pattern = binding.get('doc_pattern', '')
            version = binding.get('version', 'current')
            required = binding.get('required', True)

            dhf = dhfs_by_leaf.get(dhf_leaf)
            if not dhf:
                continue
            prefix = dhf_prefix(dhf_leaf, schema)

            # Glob expansion: doc_pattern "**/*" → enumerate all evidence
            # via taxonomy walk (external mode) OR system-DHF folder walk
            # (internal mode / role: system)
            if doc_pattern in ('**/*', '*'):
                if dhf.get('role') == 'system' or dhf.get('dhf_organization') != 'external':
                    evidence = discover_system_dhf_evidence(dhf, project_dir)
                else:
                    tx = taxonomies.get(dhf.get('taxonomy_path'))
                    evidence = discover_evidence(dhf, tx)
                for ev in evidence:
                    # Match version filter (when binding pins version)
                    matched = [v for v in ev['versions'] if v['id'] == version or version == 'current']
                    if not matched and version != 'current':
                        # No matching version on disk; still emit row with status hint
                        matched = [{'id': version, 'path': None}]
                    for v in matched:
                        rid = generate_row_id(prefix, ev['canonical_role'], ev['subkind'], ms_prefix if ms_prefix else None)
                        rows.append({
                            'id': rid,
                            'milestone': ms_id,
                            'milestone_short': ms_short.replace('Release', '').strip() or ms_short,
                            'dhf': dhf_leaf,
                            'scope': dhf.get('architecture_name', dhf_leaf),
                            'phase': _phase_for_milestone(ms_id, ms_short.replace('Release', '').strip() or ms_short, display_cfg),
                            'canonical_role': ev['canonical_role'],
                            'subkind': ev['subkind'],
                            'name_token': ev['name'],
                            'version': v['id'],
                            'path': v.get('path'),
                            'required': required,
                        })
            else:
                # Explicit doc_pattern (e.g., "design-controls/architecture/system-sad.md")
                # Emit one row directly. canonical_role inferred from path if possible.
                rid = generate_row_id(prefix, doc_pattern.split('/')[-1].replace('.md', ''), None, ms_prefix if ms_prefix else None)
                rows.append({
                    'id': rid,
                    'milestone': ms_id,
                    'milestone_short': ms_short.replace('Release', '').strip() or ms_short,
                    'dhf': dhf_leaf,
                    'scope': dhf.get('architecture_name', dhf_leaf),
                    'phase': ms.get('name', ms_id),
                    'canonical_role': 'unknown',
                    'subkind': None,
                    'name_token': doc_pattern,
                    'version': version,
                    'path': doc_pattern,
                    'required': required,
                })

    return rows, dhfs, milestones


# ─── R9.4: Round-trip preservation via human sidecar overlay ───
#
# The generator owns the markdown's structural fields (id, scope, phase, dhf,
# version, path, canonical_role, source_section, etc.). Human-curated fields
# (Status, REF override, per-row notes) live in a sidecar JSON keyed by row ID,
# so re-running the generator never clobbers them.
#
# Sidecar path: docs/project/submissions/submission-tracker.human.json
# Schema:
#   {
#     "schema_version": "0.1",
#     "rows": {
#       "<row_id>": {
#         "status": "Approved:v1.0" | "...",   # human-curated lifecycle state
#         "ref": "21 CFR 807.92" | "...",       # human override of generator's REF pick
#         "notes": "free-form per-row text",
#         "updated_at": "2026-05-03T...",       # ISO8601; set by Capability 1
#         "updated_by": "BX"                    # author tag; set by Capability 1
#       },
#       ...
#     }
#   }
#
# Unrecognized row IDs in the sidecar are kept (and surfaced as a warning) so
# row-ID schema changes don't silently lose human work — operators can rename
# manually or wait for R9.7's reconciliation pass.

HUMAN_SIDECAR_REL = 'docs/project/submissions/submission-tracker.human.json'


def load_human_sidecar(project_dir):
    """Load the human sidecar JSON if present; return {} when absent or empty."""
    path = Path(project_dir) / HUMAN_SIDECAR_REL
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError as e:
        sys.stderr.write(f'WARN: human sidecar {HUMAN_SIDECAR_REL} is invalid JSON: {e}\n')
        return {}
    return data.get('rows', {}) or {}


def apply_human_overlay(rows, human_rows):
    """Merge human-curated fields onto generated rows. Returns (rows, orphan_ids)
    — rows is mutated in place; orphan_ids is a list of sidecar row IDs that
    didn't match any generated row (surfaced as warnings)."""
    rows_by_id = {r['id']: r for r in rows}
    orphans = []
    for rid, overlay in human_rows.items():
        target = rows_by_id.get(rid)
        if target is None:
            orphans.append(rid)
            continue
        # Carry the human payload as a nested block; keep the generator-owned
        # fields untouched. Renderer (R9.6) reads `human` to populate the
        # Status / REF / notes cells.
        target['human'] = {
            'status': overlay.get('status'),
            'ref': overlay.get('ref'),
            'notes': overlay.get('notes'),
            'updated_at': overlay.get('updated_at'),
            'updated_by': overlay.get('updated_by'),
        }
    return rows, orphans


# ─── R9.6: Full markdown emission ───
#
# Emits a complete `submission-tracker.<candidate>.md` that the existing
# render.py consumes (8-col deliverable rows + 7-col ENG rows + Phase/Scope
# subsections + Engineering Prerequisites + Status/Phase/Effort scale tables).
#
# Portability constraints (so the emitter works for any HCLS project):
#   * Phase ordering driven by the regulatory milestone catalog (not hardcoded
#     to QSub/PCCP/LMR1; pharma uses IND/Phase1/NDA, IVD uses CE-Mark/PMS, etc.)
#   * Per-phase scope subsections derived from rows themselves; the emitter
#     does not know which scopes exist until it sees the row inventory
#   * Scope subsection labels prefer `architecture_short` per project.yml
#     `display.architecture_short_overrides`, falling back to canonical
#     `architecture_name` (R6.5 portability rule)
#   * Status/Phase/Effort scale tables emitted only if the project supplies
#     them in `tracker.status_vocabulary` / `tracker.effort_vocabulary` blocks;
#     skill ships defaults but does not assume them
#   * No medtech-specific labels in code (no "510k", "PCCP", "FDA"); all
#     project-specific text comes from project.yml + milestone catalog


def _scope_short_label(scope_name, dhfs, display_cfg):
    """Apply R6.5 compactness rule. Returns the short label for table cells.
    Falls back to canonical scope when no override matches and length is OK."""
    overrides = (display_cfg or {}).get('architecture_short_overrides', {}) or {}
    # First check per-DHF override by leaf
    for d in dhfs:
        if d.get('architecture_name') == scope_name:
            override = overrides.get(d['leaf'])
            if override:
                return override
            short_field = d.get('architecture_short')
            if short_field:
                return short_field
    # No explicit override; apply length rule
    max_chars = (display_cfg or {}).get('scope_label_max_chars', 12)
    if len(scope_name) <= max_chars:
        return scope_name
    # Generic shortening: strip common suffixes
    for suffix, short in (('Services', 'Svc'), ('Module', 'Mod'), ('System', 'Sys')):
        if scope_name.endswith(suffix):
            return scope_name.replace(suffix, short).strip()
    return scope_name


def _phase_for_milestone(ms_id, ms_short, display_cfg):
    """Map milestone short label to dashboard Phase column value. Project may
    override via tracker.phase_label_overrides; defaults to ms_short."""
    overrides = (display_cfg or {}).get('phase_label_overrides', {}) or {}
    return overrides.get(ms_id, ms_short)


def _row_status(row):
    """Resolve the status to display: human overlay wins; falls back to
    engineering_status for ENG rows; otherwise blank (renderer treats as
    Not Started for backward compat)."""
    h = row.get('human') or {}
    if h.get('status'):
        return h['status']
    if row.get('engineering_status'):
        return row['engineering_status']
    return 'Not Started'


def _row_ref(row):
    """Resolve REF: human overlay override > generator's REF pick (TBD per
    R8 obligation-coverage analysis) > '—'."""
    h = row.get('human') or {}
    if h.get('ref'):
        return h['ref']
    return row.get('ref') or '—'


def _row_effort(row):
    """Effort value; defaults to '—' when generator can't derive it.
    Future: derive from canonical role complexity + lifecycle state per
    project.yml `tracker.effort_heuristics` (not yet implemented)."""
    return row.get('effort') or '—'


def _scope_sort_key(scope_name, dhfs):
    """Stable scope ordering: system DHFs first, then item DHFs in project.yml
    order, then non-DHF scopes (engineering, submission) alphabetically."""
    for i, d in enumerate(dhfs):
        if d.get('architecture_name') == scope_name:
            base = 0 if d.get('role') == 'system' else 100 + i
            return (base, scope_name)
    return (1000, scope_name)


def _phase_sort_key(phase_label, milestones):
    """Phase ordering follows milestone catalog order; unknown phases trail."""
    for i, ms in enumerate(milestones):
        ms_short = ms.get('name', ms.get('id', '')).split()[0]
        if phase_label == ms_short or phase_label == ms.get('id'):
            return (i, phase_label)
    return (1000, phase_label)


def _scope_subsection_label(scope_name, dhfs):
    """Build the `### <Scope> (<descriptor>)` heading. Descriptor pulled from
    DHF metadata when available (role + classification flags); empty for
    non-DHF scopes like (submission)."""
    for d in dhfs:
        if d.get('architecture_name') == scope_name:
            short = _scope_short_label(scope_name, dhfs, {})
            role = d.get('role', '')
            cls = d.get('classification', {}) or {}
            parts = []
            if role == 'system':
                parts.append('system DHF')
            else:
                parts.append('item DHF')
            if cls.get('samd'):
                parts.append(f"SaMD Class {cls.get('class', '?')}")
            if cls.get('iec62304'):
                parts.append(f"IEC 62304 Class {cls['iec62304']}")
            if cls.get('ai_enabled'):
                parts.append('AI-enabled')
            descriptor = ', '.join(parts)
            return f'{short} ({descriptor})'
    # Non-DHF scope: bare label
    return scope_name


def emit_phase_tables(rows, dhfs, milestones, display_cfg):
    """R9.6: Emit `## Phase: ...` sections with `### <Scope>` subsections.
    Returns a list of markdown lines."""
    out = []
    # Group rows by phase, then scope
    deliverable_rows = [r for r in rows if r['canonical_role'] != 'engineering-prereq']
    by_phase = {}
    for r in deliverable_rows:
        by_phase.setdefault(r['phase'], {}).setdefault(r['scope'], []).append(r)

    sorted_phases = sorted(by_phase.keys(), key=lambda p: _phase_sort_key(p, milestones))
    for phase in sorted_phases:
        out.append(f'## Phase: {phase}')
        out.append('')
        scopes = sorted(by_phase[phase].keys(), key=lambda s: _scope_sort_key(s, dhfs))
        for scope in scopes:
            scope_rows = by_phase[phase][scope]
            out.append(f'### {_scope_subsection_label(scope, dhfs)}')
            out.append('')
            out.append('| # | Deliverable | Scope | Phase | REF | Effort | Status | Path |')
            out.append('|---|---|---|---|---|---|---|---|')
            for r in scope_rows:
                short_scope = _scope_short_label(scope, dhfs, display_cfg)
                path = r.get('path') or '_(no path)_'
                path_cell = f'[`{Path(path).name}`]({path})' if path != '_(no path)_' else path
                out.append(
                    f"| {r['id']} | {r['name_token']} | {short_scope} | {r['phase']} | "
                    f"{_row_ref(r)} | {_row_effort(r)} | **{_row_status(r)}** | {path_cell} |"
                )
            out.append('')
        out.append('---')
        out.append('')
    return out


def emit_engineering_section(rows):
    """R9.6: Emit `## Engineering Prerequisites` with the 7-col ENG table."""
    eng_rows = [r for r in rows if r['canonical_role'] == 'engineering-prereq']
    if not eng_rows:
        return []
    out = ['## Engineering Prerequisites', '']
    out.append('Cross-cutting engineering capabilities required for filing readiness. '
               'Source: [`milestones/engineering.yml`](../milestones/engineering.yml). '
               'Each row lists the design-control rows it unblocks.')
    out.append('')
    out.append('| # | Prerequisite | Scope | Phase | Effort | Status | Unblocks |')
    out.append('|---|---|---|---|---|---|---|')
    for r in eng_rows:
        unblocks = ', '.join(r.get('unblocks', []) or [])
        out.append(
            f"| {r['id']} | {r['name_token']} | {r['scope']} | {r['phase']} | "
            f"{_row_effort(r)} | **{_row_status(r)}** | {unblocks} |"
        )
    out.append('')
    out.append('---')
    out.append('')
    return out


# ─── R9.7: Validation diff against canonical ───
#
# Compares the generator's row inventory against an existing hand-built
# tracker markdown. Produces a structured report (extras / missing / matched
# by-name) so the team can plan ID reconciliation before swapping the
# generator output in as the new canonical source.
#
# Reconciliation strategy (recorded in task ben/154 R9.7 changelog): we
# adopt the generator's deterministic semantic IDs as the new canonical;
# the validation report carries an old→new mapping (matched by name token
# + scope) so any human-edited Status / REF entries in
# `submission-tracker.human.json` can be renamed in-place.


def parse_canonical_rows(canonical_md_path, valid_prefixes=None):
    """Extract row IDs + name + scope from the hand-built tracker for diff
    purposes. Accepts only rows whose first cell matches an ID pattern AND
    starts with one of `valid_prefixes` (e.g., {'PS','PP','PI','PM','PA',
    'PC','Q','L1-','ENG'} from project.yml row_id_schema). Without
    valid_prefixes we fall back to a permissive shape filter that may catch
    table-of-contents rows (e.g., Phase Coverage Summary)."""
    if not Path(canonical_md_path).is_file():
        return []
    rows = []
    id_re = re.compile(r'^[A-Z]+[0-9]+$|^L[0-9]+-[A-Z]+[0-9]+$')
    for line in Path(canonical_md_path).read_text().splitlines():
        if not (line.startswith('| ') and line.rstrip().endswith(' |')):
            continue
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if len(cells) < 7:
            continue
        first = cells[0]
        if not id_re.match(first):
            continue
        if valid_prefixes and not any(first.startswith(p) for p in valid_prefixes):
            continue
        rows.append({
            'id': first,
            'name': cells[1] if len(cells) > 1 else '',
            'scope': cells[2] if len(cells) > 2 else '',
        })
    return rows


def validate_against_canonical(generated_rows, canonical_md_path, schema=None):
    """R9.7: Compare generator output against an existing canonical tracker.

    Returns dict with:
      - matched_id: rows present in both with same ID
      - matched_by_name: rows in both whose ID changed but name+scope still match
      - missing: canonical rows the generator did not produce (rows the
        human added by hand that aren't derivable from sources)
      - extras: generator rows not in canonical (new evidence the canonical
        hasn't caught up to)
      - id_migration: list of {old_id, new_id, name, scope} for matched-by-name
    """
    valid_prefixes = set()
    if schema:
        valid_prefixes.update((schema.get('dhf_prefix_map') or {}).values())
        valid_prefixes.update((schema.get('scope_prefixes') or {}).values())
        eng = schema.get('engineering_prefix')
        if eng:
            valid_prefixes.add(eng)
        # LMR-shaped milestone prefixes are templates ("L{n}-"); accept the
        # common forms L1- and L2- explicitly.
        valid_prefixes.update(['L1-', 'L2-'])
    canonical = parse_canonical_rows(canonical_md_path, valid_prefixes or None)
    canonical_by_id = {r['id']: r for r in canonical}
    generated_by_id = {r['id']: r for r in generated_rows}

    matched_id = []
    extras = []
    matched_by_name = []
    id_migration = []

    # Index canonical by (name, scope) for fuzzy ID rename detection
    def _norm(s):
        return re.sub(r'\s+', ' ', (s or '').strip().lower())

    canonical_by_namescope = {}
    for r in canonical:
        key = (_norm(r['name']), _norm(r['scope']))
        canonical_by_namescope.setdefault(key, []).append(r)

    consumed_canonical_ids = set()

    for gr in generated_rows:
        gid = gr['id']
        if gid in canonical_by_id:
            matched_id.append(gid)
            consumed_canonical_ids.add(gid)
            continue
        # Try fuzzy: generator's display name vs canonical name+scope
        gname = _norm(gr.get('name_token', ''))
        gscope = _norm(gr.get('scope', ''))
        candidates = canonical_by_namescope.get((gname, gscope), [])
        # Pick first un-consumed candidate
        match = next((c for c in candidates if c['id'] not in consumed_canonical_ids), None)
        if match:
            matched_by_name.append(gid)
            consumed_canonical_ids.add(match['id'])
            id_migration.append({
                'old_id': match['id'],
                'new_id': gid,
                'name': match['name'],
                'scope': match['scope'],
            })
        else:
            extras.append(gid)

    missing = [r['id'] for r in canonical if r['id'] not in consumed_canonical_ids]

    return {
        'canonical_count': len(canonical),
        'generated_count': len(generated_rows),
        'matched_id': sorted(matched_id),
        'matched_by_name': sorted(matched_by_name),
        'missing': sorted(missing),
        'extras': sorted(extras),
        'id_migration': sorted(id_migration, key=lambda m: m['old_id']),
    }


def emit_validation_report(report, canonical_path, candidate_summary):
    """R9.7: Render the validation diff as a markdown report."""
    out = ['# Submission Tracker — Generator Validation Report', '']
    out.append(f'_Auto-generated by `/tracker generate --validate`. '
               f'Compares generator output against the canonical hand-built '
               f'`{Path(canonical_path).name}`._')
    out.append('')
    out.append('## Summary')
    out.append('')
    out.append(f'- **Canonical rows**: {report["canonical_count"]}')
    out.append(f'- **Generated rows**: {report["generated_count"]}')
    out.append(f'- **Matched by ID** (no migration needed): {len(report["matched_id"])}')
    out.append(f'- **Matched by name+scope** (ID renamed): {len(report["matched_by_name"])}')
    out.append(f'- **Missing** (in canonical, not generated): {len(report["missing"])}')
    out.append(f'- **Extras** (generated, not in canonical): {len(report["extras"])}')
    out.append('')
    out.append('## ID Migration Map (matched by name + scope)')
    out.append('')
    out.append('Apply this map to `submission-tracker.human.json` so human-curated '
               'Status / REF / notes survive the row-ID renumbering.')
    out.append('')
    if report['id_migration']:
        out.append('| Old ID | New ID | Deliverable | Scope |')
        out.append('|---|---|---|---|')
        for m in report['id_migration']:
            out.append(f'| `{m["old_id"]}` | `{m["new_id"]}` | {m["name"]} | {m["scope"]} |')
    else:
        out.append('_(no name-matched rows requiring ID migration)_')
    out.append('')
    out.append('## Missing Rows (in canonical, generator did not produce)')
    out.append('')
    out.append('Each row here is either (a) hand-authored content the generator '
               'cannot derive from sources today, or (b) evidence the generator '
               'failed to discover and warrants a discovery-rule fix.')
    out.append('')
    if report['missing']:
        for rid in report['missing']:
            out.append(f'- `{rid}`')
    else:
        out.append('_(none)_')
    out.append('')
    out.append('## Extra Rows (generated, not in canonical)')
    out.append('')
    out.append('Each row here is new evidence the canonical hand-built file has '
               'not caught up to. Adopting the generator output replaces the '
               'canonical with these rows present.')
    out.append('')
    if report['extras']:
        for rid in report['extras']:
            out.append(f'- `{rid}`')
    else:
        out.append('_(none)_')
    out.append('')
    return '\n'.join(out)


def emit_full_markdown(rows, dhfs, milestones, tracker_cfg):
    """R9.6: Compose a candidate `submission-tracker.md` from generator output.

    Emits the data-driven sections only — Phase tables, Engineering
    Prerequisites. The boilerplate (intro, legends, REF priority, scale
    sections, Deliverable Details) is project-template content deferred to
    R9.6.5; for now the candidate file is a fragment intended for diff-review
    against the canonical hand-built file.

    Portable: scope labels driven by project.yml `display`; phase ordering
    driven by milestone catalog; no hardcoded medtech vocabulary."""
    display_cfg = tracker_cfg.get('display', {}) or {}
    out = []
    out.append('# Submission Package Tracker — Generator Candidate')
    out.append('')
    out.append('_Auto-generated by `/tracker generate` (R9.6 candidate)._ '
               'Compare against the canonical hand-built `submission-tracker.md` '
               'to validate row coverage, scope assignment, and ID stability.')
    out.append('')
    out.extend(emit_phase_tables(rows, dhfs, milestones, display_cfg))
    out.extend(emit_engineering_section(rows))
    return '\n'.join(out)


CANONICAL_TRACKER_MD = 'docs/project/submissions/submission-tracker.md'


def _is_canonical_md_path(out_path, project_dir):
    """True iff `out_path` resolves to the project's canonical tracker md."""
    if not out_path:
        return False
    try:
        out_resolved = Path(out_path).resolve()
        canonical = (Path(project_dir) / CANONICAL_TRACKER_MD).resolve()
        return out_resolved == canonical
    except Exception:
        return False


def _auto_regenerate_html(project_dir):
    """Lockstep invariant: any tool that produces the canonical
    submission-tracker.md must regenerate submission-tracker.html in the
    same step. Invokes render.py as a subprocess (avoids module-import
    coupling)."""
    import subprocess
    script = Path(__file__).parent / 'render.py'
    if not script.is_file():
        return False, f'render.py missing at {script}'
    try:
        r = subprocess.run(
            [sys.executable, str(script), '--project-dir', str(project_dir)],
            capture_output=True, text=True, timeout=60,
        )
        if r.returncode != 0:
            return False, r.stderr.strip() or 'render.py failed'
        return True, ''
    except Exception as e:
        return False, f'{type(e).__name__}: {e}'


def main():
    p = argparse.ArgumentParser(description='/tracker generate — row inventory (R9.1)')
    p.add_argument('--project-dir', help='Project root', default=None)
    p.add_argument('--out', help='Write to file (default: stdout)', default=None)
    p.add_argument('--md', action='store_true', help='Emit full markdown candidate instead of JSON')
    p.add_argument('--dry-run', action='store_true', help='Show counts only')
    p.add_argument('--validate', metavar='CANONICAL_PATH',
                   help='R9.7: Compare generator output against an existing canonical '
                        'tracker md; emit a validation report (markdown to --out or stdout).')
    p.add_argument('--no-render', action='store_true',
                   help='Skip the auto-render of submission-tracker.html that '
                        'normally fires when --out targets the canonical md path. '
                        'Use only for tests / candidate diffs.')
    p.add_argument('--candidate', action='store_true',
                   help='Convenience: with --md, write to '
                        'docs/project/submissions/submission-tracker.candidate.md '
                        '(safe iteration target). Use when you want to compare '
                        'generator output against the canonical without touching it.')
    p.add_argument('--write-canonical', action='store_true',
                   help='Required to write to the canonical submission-tracker.md '
                        'path. Without this flag, an --out targeting the canonical '
                        'is rejected — protects the live tracker from accidental '
                        'overwrite while generator-vs-canonical parity is incomplete '
                        '(see R9.7 reconciliation report).')
    args = p.parse_args()

    # Safety guard: --candidate sets --out to the candidate path; can't combine
    # with --write-canonical or an explicit --out.
    if args.candidate:
        if args.out or args.write_canonical:
            sys.stderr.write('ERROR: --candidate cannot combine with --out or --write-canonical\n')
            return 2
        if not args.md:
            sys.stderr.write('ERROR: --candidate requires --md (candidate is a markdown artifact)\n')
            return 2

    project_dir = Path(args.project_dir) if args.project_dir else find_project_dir()
    rows, dhfs, milestones = generate_rows(project_dir)
    # Re-load tracker_cfg for emitter (display block etc.); generate_rows
    # used schema only.
    _, tracker_cfg = read_dhfs(project_dir / 'project.yml')

    # R9.4: merge human sidecar overlay so re-runs preserve human edits
    human_rows = load_human_sidecar(project_dir)
    rows, orphans = apply_human_overlay(rows, human_rows)
    if orphans:
        sys.stderr.write(
            f'WARN: {len(orphans)} sidecar row IDs did not match any generated row: '
            f'{", ".join(sorted(orphans)[:5])}{"..." if len(orphans) > 5 else ""}\n'
        )

    # Model D: emit row-source sidecar on every run so render.py + downstream
    # consumers always see a fresh source_kind map. Side-effect-light: writes
    # one small JSON file alongside the existing tracker artifacts.
    try:
        emit_row_source_sidecar(rows, project_dir)
    except Exception as e:
        sys.stderr.write(f'WARN: row-source sidecar emit failed ({e}); badges may not render\n')

    if args.dry_run:
        n_user = sum(1 for r in rows if r.get('source_kind') == 'user')
        print(f'project_dir: {project_dir}')
        print(f'dhfs: {len(dhfs)}')
        print(f'milestones: {len(milestones)} ({", ".join(m["id"] for m in milestones)})')
        print(f'generated rows: {len(rows)} ({n_user} user-injected, {len(rows) - n_user} catalog-derived)')
        print(f'human-overlay rows: {len(human_rows)} ({len(orphans)} orphan)')
        from collections import Counter
        by_phase = Counter(r['milestone_short'] for r in rows)
        by_scope = Counter(r['scope'] for r in rows)
        print(f'  by phase: {dict(by_phase)}')
        print(f'  by scope: {dict(by_scope)}')
        return 0

    if args.validate:
        schema = (tracker_cfg or {}).get('row_id_schema', {}) or {}
        report = validate_against_canonical(rows, args.validate, schema=schema)
        out_text = emit_validation_report(report, args.validate, None)
        # Also print summary to stderr
        sys.stderr.write(
            f'Validation: canonical={report["canonical_count"]} '
            f'generated={report["generated_count"]} '
            f'matched_id={len(report["matched_id"])} '
            f'matched_by_name={len(report["matched_by_name"])} '
            f'missing={len(report["missing"])} '
            f'extras={len(report["extras"])}\n'
        )
    elif args.md:
        out_text = emit_full_markdown(rows, dhfs, milestones, tracker_cfg)
    else:
        out_text = json.dumps({
            'generated_by': '/tracker generate (R9.1)',
            'project_dir': str(project_dir),
            'row_count': len(rows),
            'rows': rows,
        }, indent=2)

    # --candidate convenience: route output to submission-tracker.candidate.md
    # Safety default (Model D): bare `--md` (no --out, --candidate, or
    # --write-canonical) auto-targets the candidate file. Without this
    # default, `--md` would print the candidate to stdout — useful for
    # piping but easy to mistake for "ready to overwrite canonical." Now
    # the safe path is the default; the canonical write requires both
    # --out <canonical_path> AND --write-canonical (the existing guard).
    out_path = args.out
    if args.candidate:
        out_path = str(project_dir / 'docs/project/submissions/submission-tracker.candidate.md')
    elif args.md and not args.out and not args.write_canonical:
        out_path = str(project_dir / 'docs/project/submissions/submission-tracker.candidate.md')
        sys.stderr.write(
            f'NOTE: --md without --out auto-targets the candidate file '
            f'({Path(out_path).name}). To overwrite the canonical, pass '
            f'--write-canonical --out <canonical_path>. To print to stdout, '
            f'pipe through a no-op like `--out /dev/stdout` (advanced).\n'
        )

    # Safety guard: refuse to overwrite canonical submission-tracker.md unless
    # --write-canonical is set. The generator and the canonical hand-built
    # tracker have not yet reached parity (see R9.7) — a naked --out to the
    # canonical path would clobber 80+ "Drafting" cells, the rich preamble,
    # the per-Phase Coverage Summary, and the Deliverable Details.
    if out_path and args.md and _is_canonical_md_path(out_path, project_dir) \
            and not args.write_canonical:
        sys.stderr.write(
            'ERROR: refusing to overwrite the canonical submission-tracker.md.\n'
            '  Generator and canonical have not reached parity (R9.7).\n'
            '  To iterate safely, use:  --candidate  (writes to submission-tracker.candidate.md)\n'
            '  To force the canonical write, pass:  --write-canonical\n'
        )
        return 2

    if out_path:
        Path(out_path).write_text(out_text)
        print(f'Wrote {out_path} ({len(out_text)} bytes)', file=sys.stderr)
        # Lockstep invariant — when the write produces the canonical
        # submission-tracker.md, regenerate submission-tracker.html in the
        # same step so the two files are always modified together.
        if args.md and not args.no_render and _is_canonical_md_path(out_path, project_dir):
            ok, err = _auto_regenerate_html(project_dir)
            if ok:
                print('Auto-rendered submission-tracker.html (lockstep)', file=sys.stderr)
            else:
                sys.stderr.write(f'WARN: auto-render failed — md and html may drift: {err}\n')
                return 1
    else:
        print(out_text)
    return 0


if __name__ == '__main__':
    sys.exit(main())
