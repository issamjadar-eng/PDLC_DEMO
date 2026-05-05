#!/usr/bin/env python3
"""
/tracker validate-user-rows — schema validator for tracker-user-rows.yml.

Reads the project's user-row registry, resolves project-adaptive vocabularies
(scope, phase, effort, status) from project.yml + regulatory.yml, and reports
every conformance issue. Exit code is non-zero if any error is found.

Usage:
    python3 validate-user-rows.py
    python3 validate-user-rows.py --project-dir /path/to/project
    python3 validate-user-rows.py --strict   # also error on warnings (CI mode)

The validator is deterministic and side-effect-free — it never writes.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path
from typing import Any


SKILL_DIR = Path(__file__).resolve().parent.parent
SCHEMA_PATH = SKILL_DIR / 'schemas' / 'user-row.schema.yml'

REGISTRY_REL = 'docs/project/submissions/tracker-user-rows.yml'

DEFAULT_EFFORT_VOCABULARY = ['Low', 'Med', 'High', 'V.High']
DEFAULT_KIND_VOCABULARY = ['deliverable', 'header', 'gap-tracker']

ID_PATTERN = re.compile(r'^[A-Z][A-Z0-9-]+$')


# ─────────────────────────────────────────────────────────────────────────────
# Project-context resolution (vocabularies)
# ─────────────────────────────────────────────────────────────────────────────

def find_project_dir() -> Path:
    """Walk up from cwd looking for CLAUDE.md (project root marker)."""
    p = Path.cwd().resolve()
    for cand in [p, *p.parents]:
        if (cand / 'CLAUDE.md').is_file() and (cand / 'project.yml').is_file():
            return cand
    raise SystemExit('ERROR: cannot find project root (no CLAUDE.md + project.yml in ancestors)')


def load_yaml(path: Path) -> Any:
    try:
        import yaml  # type: ignore
    except ImportError:
        sys.stderr.write('ERROR: PyYAML required (uv pip install pyyaml)\n')
        sys.exit(2)
    if not path.is_file():
        return None
    return yaml.safe_load(path.read_text(encoding='utf-8'))


def resolve_scope_vocabulary(project_yml: dict) -> list[str]:
    tracker = (project_yml or {}).get('tracker', {}) or {}
    if 'scope_vocabulary' in tracker and isinstance(tracker['scope_vocabulary'], list):
        return list(tracker['scope_vocabulary'])
    # Default: union of dhf names + standard non-DHF scopes
    dhfs = (project_yml or {}).get('dhfs', []) or []
    names = []
    for d in dhfs:
        for k in ('architecture_name', 'name', 'slug'):
            if d.get(k):
                names.append(str(d[k]))
                break
    standard = ['(submission)', 'Suite', 'Engineering']
    seen, out = set(), []
    for v in names + standard:
        if v not in seen:
            out.append(v); seen.add(v)
    return out


def resolve_phase_vocabulary(project_yml: dict, regulatory_yml: dict) -> list[str]:
    tracker = (project_yml or {}).get('tracker', {}) or {}
    if 'phase_vocabulary' in tracker and isinstance(tracker['phase_vocabulary'], list):
        return list(tracker['phase_vocabulary'])
    milestones = (regulatory_yml or {}).get('milestones', []) or []
    out = []
    for m in milestones:
        v = m.get('short_label') or m.get('name')
        if v:
            out.append(str(v))
    return out


def resolve_effort_vocabulary(project_yml: dict) -> list[str]:
    tracker = (project_yml or {}).get('tracker', {}) or {}
    if 'effort_vocabulary' in tracker and isinstance(tracker['effort_vocabulary'], list):
        return list(tracker['effort_vocabulary'])
    return list(DEFAULT_EFFORT_VOCABULARY)


def resolve_status_vocabulary(project_yml: dict) -> tuple[list[str], dict[str, str]]:
    """Returns (canonical_labels, alias_to_canonical)."""
    tracker = (project_yml or {}).get('tracker', {}) or {}
    states = (tracker.get('status_vocabulary', {}) or {}).get('states', []) or []
    canonical = []
    aliases: dict[str, str] = {}
    for s in states:
        label = s.get('display_label')
        if not label:
            continue
        canonical.append(label)
        aliases[label] = label
        for a in s.get('aliases', []) or []:
            aliases[str(a)] = label
    if not canonical:
        # Skill-default minimal vocabulary if project ships none
        canonical = ['Not Started', 'Drafting', 'Drafted', 'In Review',
                     'Needs Revision', 'Approved', 'N/A']
        for v in canonical:
            aliases[v] = v
    return canonical, aliases


# ─────────────────────────────────────────────────────────────────────────────
# Generator row inventory (for id-collision check)
# ─────────────────────────────────────────────────────────────────────────────

def load_generator_row_ids(project_dir: Path) -> set[str]:
    """Best-effort: load generate.py and call generate_rows. Returns empty
    set if anything goes wrong (validator is still useful without it).

    IMPORTANT: generate_rows() merges user rows from this same registry into
    its output, so a naive collision check would always self-collide. We set
    an env var that read_user_rows() honors as 'return empty', so the
    inventory we get back is catalog-only — the right baseline for the
    'does this user-row id collide with a generator id?' question."""
    import os
    os.environ['TRACKER_SKIP_USER_ROWS'] = '1'
    try:
        spec = importlib.util.spec_from_file_location(
            'tracker_generate', SKILL_DIR / 'scripts' / 'generate.py')
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        rows, _, _ = mod.generate_rows(project_dir)
        return {r.get('id') for r in rows if r.get('id')}
    except Exception as e:
        sys.stderr.write(f'WARN: could not load generator row IDs ({e}); '
                         'id-collision check skipped\n')
        return set()
    finally:
        os.environ.pop('TRACKER_SKIP_USER_ROWS', None)


# ─────────────────────────────────────────────────────────────────────────────
# Validation
# ─────────────────────────────────────────────────────────────────────────────

def validate(project_dir: Path, strict: bool = False) -> tuple[int, int]:
    """Returns (error_count, warning_count)."""
    errors: list[str] = []
    warnings: list[str] = []

    project_yml = load_yaml(project_dir / 'project.yml') or {}
    regulatory_yml = load_yaml(project_dir / 'docs/project/milestones/regulatory.yml') or {}
    registry_path = project_dir / REGISTRY_REL
    if not registry_path.is_file():
        warnings.append(f'registry not found at {REGISTRY_REL} — '
                        'no user rows to validate (this is fine for projects '
                        'with empty user-row sets)')
        return _report(errors, warnings, strict)
    registry = load_yaml(registry_path) or {}
    rows = registry.get('rows', []) or []

    scope_vocab = set(resolve_scope_vocabulary(project_yml))
    phase_vocab = set(resolve_phase_vocabulary(project_yml, regulatory_yml))
    effort_vocab = set(resolve_effort_vocabulary(project_yml))
    status_canonical, status_aliases = resolve_status_vocabulary(project_yml)
    generator_ids = load_generator_row_ids(project_dir)

    seen_ids: set[str] = set()
    for i, row in enumerate(rows):
        loc = f'rows[{i}] (id={row.get("id", "<missing>")})'
        if not isinstance(row, dict):
            errors.append(f'{loc}: not a mapping')
            continue

        # required
        for f in ('id', 'name', 'scope', 'phase', 'status', 'reason'):
            if not row.get(f):
                errors.append(f'{loc}: missing required field "{f}"')

        rid = row.get('id') or ''
        if rid:
            if not ID_PATTERN.match(rid):
                errors.append(
                    f'{loc}: id "{rid}" must match {ID_PATTERN.pattern}')
            if rid in seen_ids:
                errors.append(f'{loc}: duplicate id "{rid}"')
            seen_ids.add(rid)
            if rid in generator_ids:
                errors.append(
                    f'{loc}: id "{rid}" collides with a generator-derived row '
                    '(use a different id or remove the generator binding)')

        scope = row.get('scope')
        if scope and scope_vocab and scope not in scope_vocab:
            warnings.append(
                f'{loc}: scope "{scope}" not in resolved vocabulary '
                f'{sorted(scope_vocab)} — verify project.yml conventions')

        phase = row.get('phase')
        if phase and phase_vocab and phase not in phase_vocab:
            warnings.append(
                f'{loc}: phase "{phase}" not in resolved vocabulary '
                f'{sorted(phase_vocab)} — verify regulatory.yml short_labels')

        status = row.get('status')
        if status and status not in status_aliases:
            errors.append(
                f'{loc}: status "{status}" not in resolved vocabulary '
                f'(canonical: {sorted(status_canonical)})')

        effort = row.get('effort')
        if effort and effort_vocab and effort not in effort_vocab:
            warnings.append(
                f'{loc}: effort "{effort}" not in resolved vocabulary '
                f'{sorted(effort_vocab)}')

        kind = row.get('kind', 'deliverable')
        if kind not in DEFAULT_KIND_VOCABULARY:
            errors.append(
                f'{loc}: kind "{kind}" not in '
                f'{DEFAULT_KIND_VOCABULARY}')

        reason = row.get('reason') or ''
        if reason and len(reason.strip()) < 10:
            warnings.append(
                f'{loc}: reason is very short ({len(reason)} chars); '
                'explain why the row is user-injected vs catalog-derived')

        # path: warn if non-existent (Not Started rows often have planned paths)
        path = row.get('path')
        if path and isinstance(path, str):
            cands = [project_dir / 'docs/project' / path,
                     project_dir / path]
            if not any(c.exists() for c in cands):
                warnings.append(
                    f'{loc}: path "{path}" does not resolve to an existing '
                    'file or directory (acceptable for Not Started rows)')

        related = row.get('related_catalog_row')
        if related and generator_ids and related not in generator_ids:
            warnings.append(
                f'{loc}: related_catalog_row "{related}" not found in '
                'generator output (typo or stale reference)')

    return _report(errors, warnings, strict)


def _report(errors: list[str], warnings: list[str], strict: bool) -> tuple[int, int]:
    for w in warnings:
        sys.stderr.write(f'  WARN: {w}\n')
    for e in errors:
        sys.stderr.write(f'  ERR:  {e}\n')
    n_err, n_warn = len(errors), len(warnings)
    if strict:
        n_err += n_warn
    return n_err, n_warn


def main():
    p = argparse.ArgumentParser(description='/tracker validate-user-rows')
    p.add_argument('--project-dir', default=None)
    p.add_argument('--strict', action='store_true',
                   help='Exit non-zero on warnings as well as errors')
    args = p.parse_args()
    project_dir = Path(args.project_dir) if args.project_dir else find_project_dir()
    n_err, n_warn = validate(project_dir, strict=args.strict)
    print(f'validate-user-rows: {n_err} errors, {n_warn} warnings', file=sys.stderr)
    sys.exit(1 if n_err > 0 else 0)


if __name__ == '__main__':
    sys.exit(main() or 0)
