#!/usr/bin/env python3
"""
render-sentinels.py — Regenerate AUTO:STRUCTURE sentinel blocks in markdown files.

Usage:
    python3 render-sentinels.py <path-to-file> [--dry-run] [--verbose]

Spec: .claude/rules/sentinel-blocks.md

Behavior:
  - Reads the target file.
  - Finds every <!-- AUTO:STRUCTURE kind=... source=... --> block.
  - Regenerates the content between each open/close sentinel.
  - Preserves content outside sentinels byte-for-byte.
  - Idempotent. Malformed sentinels abort with non-zero exit, file unchanged.

Exit codes:
  0 — success (wrote changes or dry-run succeeded)
  1 — malformed sentinel (mismatched open/close, unknown kind, unclosed block)
  2 — source data unavailable (project.yml missing, path doesn't exist)
  3 — unexpected error
"""

import argparse
import os
import re
import sys
from pathlib import Path

OPEN_RE = re.compile(r'<!--\s*AUTO:STRUCTURE\s+([^>]*?)-->\s*$')
CLOSE_RE = re.compile(r'<!--\s*/AUTO:STRUCTURE\s*-->\s*$')
ATTR_RE = re.compile(r'(\w[\w-]*)=(?:"([^"]*)"|(\S+))')

DEFAULT_EXCLUDE = {'formal', '.git', '.venv', '__pycache__', 'node_modules',
                   'images', '.staging', 'assets'}

PROJECT_ROOT = None  # Set at startup


def log(msg, verbose=False, err=False):
    """Write a diagnostic message."""
    if verbose or err:
        print(msg, file=sys.stderr)


def parse_attrs(attr_str):
    """Parse 'kind=foo source=bar path="some thing"' into a dict."""
    return {m.group(1): (m.group(2) if m.group(2) is not None else m.group(3))
            for m in ATTR_RE.finditer(attr_str)}


def find_project_root(start):
    """Walk up from start to find project root (contains project.yml)."""
    p = Path(start).resolve()
    if p.is_file():
        p = p.parent
    while p != p.parent:
        if (p / 'project.yml').exists():
            return p
        p = p.parent
    # Fallback: assume start is project root
    return Path(start).resolve().parent if Path(start).is_file() else Path(start).resolve()


def read_project_yml(root):
    """Read project.yml. Returns parsed dict or None if missing."""
    p = root / 'project.yml'
    if not p.exists():
        return None
    try:
        import yaml
    except ImportError:
        # Fallback: minimal parser for our needs
        return _parse_yml_minimal(p)
    with open(p) as f:
        return yaml.safe_load(f)


def _parse_yml_minimal(path):
    """Minimal YAML parser covering our needs (dhfs list + team dict).
    Used only when PyYAML is unavailable.
    """
    # Prefer subprocess call to python3 -c 'import yaml' but we're already in py.
    # If yaml isn't installed, fall back to a hand-rolled parser.
    # For robustness, just fail loudly — most python3 environments have yaml.
    raise RuntimeError("PyYAML not available; install pyyaml or use a venv with it.")


def render_subfolder_table(target_file, attrs, old_block_content):
    """Render kind=subfolder-table. Scans target_file's parent dir."""
    target = Path(target_file).resolve()
    if target.is_file():
        folder = target.parent
    else:
        folder = target

    excludes = set(DEFAULT_EXCLUDE)
    if 'exclude' in attrs:
        excludes |= set(g.strip() for g in attrs['exclude'].split(','))

    preserve_col = attrs.get('preserve-column', 'Purpose')

    # Scan subfolders
    subfolders = []
    for child in sorted(folder.iterdir()):
        if not child.is_dir():
            continue
        name = child.name
        if name in excludes or name.startswith('.'):
            continue
        subfolders.append(name)

    # Parse old block to preserve column values
    preserved = {}
    if old_block_content.strip():
        preserved = _parse_table_preserve(old_block_content, preserve_col)

    # Build new table
    lines = ['| Folder | Purpose |', '|--------|---------|']
    for name in subfolders:
        key = f'`{name}/`'
        purpose = preserved.get(key, preserved.get(name, 'TODO'))
        lines.append(f'| {key} | {purpose} |')

    return '\n'.join(lines) + '\n'


def _dhf_classification(dhf):
    """Return (classification_str, iec_str) for a DHF row."""
    role = dhf.get('role', 'unknown')
    if role == 'system':
        return 'device-level', 'n/a'
    c = dhf.get('classification') or {}
    samd = 'SaMD' if c.get('samd') else 'non-SaMD'
    cls = c.get('class', 'tbd')
    ai = 'AI-enabled' if c.get('ai_enabled') else ''
    # Skip "Class X" prefix when class isn't a Roman/Arabic numeral
    # (e.g., "non-device" for non-SaMD entries doesn't read well as "Class non-device")
    if str(cls).strip().lower().startswith('non-'):
        classification = samd + (f', {ai}' if ai else '')
    else:
        classification = f'{samd}, Class {cls}' + (f', {ai}' if ai else '')
    iec = f"Class {c.get('iec62304', 'tbd')}"
    return classification, iec


def render_dhf_table(target_file, attrs, old_block_content, project_yml):
    """Render kind=dhf-table from project.yml dhfs[].

    Three variants controlled by attrs['variant']:
      - default (no variant or variant=default):
          Architecture Name | Marketed Name | Role | Classification | IEC 62304 | Filing
      - naming:
          Architecture Name | Marketed Name | Classification | IEC 62304
      - flat-multi:
          DHF | role | Classification | Purpose

    Reads `architecture_name` and `marketed_name` from each dhfs[] entry.
    Falls back to `leaf` for architecture name; preserve-column lookup, then
    'TODO', for marketed name. The `flat-multi` variant reads `dhf_purpose`
    from each dhfs[] entry, falling back to preserve-column lookup.
    """
    if project_yml is None:
        raise RuntimeError("project.yml missing — required for dhf-table kind")

    dhfs = project_yml.get('dhfs', [])
    variant = attrs.get('variant', 'default')

    if variant == 'flat-multi':
        preserve_col = attrs.get('preserve-column', 'Purpose')
    else:
        preserve_col = attrs.get('preserve-column', 'Marketed Name')

    preserved = {}
    if old_block_content.strip():
        preserved = _parse_table_preserve(old_block_content, preserve_col)

    if variant == 'naming':
        lines = [
            '| Architecture Name | Marketed Name | Classification | IEC 62304 |',
            '|-------------------|---------------|----------------|-----------|',
        ]
        for dhf in dhfs:
            leaf = dhf.get('leaf', 'unknown')
            arch = dhf.get('architecture_name') or leaf
            classification, iec = _dhf_classification(dhf)
            marketed = (
                dhf.get('marketed_name')
                or preserved.get(arch, preserved.get(f'**{arch}**', 'TODO'))
            )
            lines.append(f'| **{arch}** | {marketed} | {classification} | {iec} |')
        return '\n'.join(lines) + '\n'

    if variant == 'flat-multi':
        lines = [
            '| DHF | `role` | Classification | Purpose |',
            '|-----|--------|----------------|---------|',
        ]
        for dhf in dhfs:
            leaf = dhf.get('leaf', 'unknown')
            role = dhf.get('role', 'unknown')
            classification, iec = _dhf_classification(dhf)
            cls_full = (
                f'{classification}, IEC 62304 {iec}'
                if iec != 'n/a' else classification.capitalize()
            )
            purpose = (
                dhf.get('dhf_purpose')
                or preserved.get(f'`{leaf}`', preserved.get(leaf, 'TODO'))
            )
            lines.append(f'| `{leaf}` | `{role}` | {cls_full} | {purpose} |')
        return '\n'.join(lines) + '\n'

    if variant in ('default', None):
        lines = [
            '| Architecture Name | Marketed Name | Role | Classification | IEC 62304 | Filing |',
            '|-------------------|---------------|------|----------------|-----------|--------|',
        ]
        for dhf in dhfs:
            leaf = dhf.get('leaf', 'unknown')
            arch = dhf.get('architecture_name') or leaf
            role = dhf.get('role', 'unknown')
            filing = dhf.get('filing') or 'tbd'
            classification, iec = _dhf_classification(dhf)
            marketed = (
                dhf.get('marketed_name')
                or preserved.get(f'**{arch}**', preserved.get(arch, 'TODO'))
            )
            lines.append(f'| **{arch}** | {marketed} | {role} | {classification} | {iec} | {filing} |')
        return '\n'.join(lines) + '\n'

    raise RuntimeError(f"unknown variant for dhf-table: {variant!r}")


def render_team_table(target_file, attrs, old_block_content, project_yml):
    """Render kind=team-table from project.yml team.active[]."""
    if project_yml is None:
        raise RuntimeError("project.yml missing — required for team-table kind")

    active = project_yml.get('team', {}).get('active', [])

    lines = [
        '| Name | Role | GitHub |',
        '|------|------|--------|',
    ]
    for member in active:
        name = member.get('name', 'unknown')
        role = member.get('role', '')
        gh = member.get('github', '')
        lines.append(f'| {name} | {role} | `{gh}` |')

    return '\n'.join(lines) + '\n'


DEPTH_CAP = 4  # Hard ceiling to prevent runaway output on deep trees.


def _walk_tree(folder, depth_remaining, prefix, excludes, lines):
    """Recursively append tree lines for `folder` into `lines`."""
    children = []
    for child in sorted(folder.iterdir()):
        if child.name in excludes or child.name.startswith('.'):
            continue
        children.append(child)

    for i, child in enumerate(children):
        is_last = (i == len(children) - 1)
        connector = '└──' if is_last else '├──'
        name = f'{child.name}/' if child.is_dir() else child.name
        lines.append(f'{prefix}{connector} {name}')
        if child.is_dir() and depth_remaining > 1:
            child_prefix = prefix + ('    ' if is_last else '│   ')
            _walk_tree(child, depth_remaining - 1, child_prefix, excludes, lines)


def _render_tree(target_file, attrs, old_block_content, project_root, default_depth):
    """Shared implementation for folder-tree and folder-tree-subset."""
    path = attrs.get('path', '.')
    base = (project_root / path).resolve()
    if not base.exists():
        raise RuntimeError(f"folder-tree path does not exist: {path}")

    excludes = set(DEFAULT_EXCLUDE)
    if 'exclude' in attrs:
        excludes |= set(g.strip() for g in attrs['exclude'].split(','))

    try:
        depth = int(attrs.get('depth', default_depth))
    except (TypeError, ValueError):
        raise RuntimeError(f"folder-tree depth must be an integer, got {attrs.get('depth')!r}")
    if depth < 1:
        raise RuntimeError(f"folder-tree depth must be >= 1, got {depth}")
    depth = min(depth, DEPTH_CAP)

    lines = ['```']
    lines.append(f'{base.name}/' if path == '.' else f'{path}/')
    _walk_tree(base, depth, '', excludes, lines)
    lines.append('```')
    return '\n'.join(lines) + '\n'


def render_folder_tree(target_file, attrs, old_block_content, project_root):
    """Render kind=folder-tree. Default depth=1 (top-level only)."""
    return _render_tree(target_file, attrs, old_block_content, project_root, default_depth=1)


def render_folder_tree_subset(target_file, attrs, old_block_content, project_root):
    """Render kind=folder-tree-subset. Default depth=2 (one level into subtree)."""
    return _render_tree(target_file, attrs, old_block_content, project_root, default_depth=2)


def render_strategy_domains(target_file, attrs, old_block_content, project_yml):
    """Render kind=strategy-domains from project.yml strategy_domains[].

    Three variants controlled by attrs['variant']:
      - expected-content: File | Purpose
      - registry (default): Domain Key | Domain Name | Scope | Output Path | Template | Plans Informed
      - init-briefs: Domain | What Belongs Here | Plans Table Rows
    """
    if project_yml is None:
        raise RuntimeError("project.yml missing — required for strategy-domains kind")

    domains = project_yml.get('strategy_domains', [])
    if not domains:
        raise RuntimeError("project.yml has no strategy_domains[] block")

    variant = attrs.get('variant', 'registry')

    if variant == 'expected-content':
        lines = ['| File | Purpose |', '|------|---------|']
        for d in domains:
            basename = os.path.basename(d.get('output_path', ''))
            purpose = d.get('scope_description', 'TODO')
            lines.append(f'| `{basename}` | {purpose} |')
        return '\n'.join(lines) + '\n'

    if variant == 'registry':
        lines = [
            '| Domain Key | Domain Name | Scope | Output Path | Template | Plans Informed |',
            '|-----------|------------|-------|-------------|----------|----------------|',
        ]
        for d in domains:
            key = d.get('key', 'unknown')
            name = d.get('name', 'TODO')
            scope = d.get('scope', 'shared')
            path = d.get('output_path', '')
            tmpl = d.get('template', 'default-strategy.md')
            plans = ', '.join(d.get('plans_informed', []) or []) or 'TODO'
            lines.append(f'| `{key}` | {name} | {scope} | `{path}` | `{tmpl}` | {plans} |')
        return '\n'.join(lines) + '\n'

    if variant == 'init-briefs':
        lines = [
            '| Domain | What Belongs Here | Plans Table Rows |',
            '|--------|------------------|-----------------|',
        ]
        for d in domains:
            key = d.get('key', 'unknown')
            belongs = '; '.join(d.get('what_belongs_here', []) or []) or 'TODO'
            plans_rows = d.get('plans_table', []) or []
            plans_cell = '; '.join(
                f"{r.get('name','?')} \\| {r.get('description','?')}"
                for r in plans_rows
            ) or 'TODO'
            lines.append(f'| `{key}` | {belongs} | {plans_cell} |')
        return '\n'.join(lines) + '\n'

    raise RuntimeError(f"unknown variant for strategy-domains: {variant!r}")


def _parse_table_preserve(block_content, preserve_col):
    """Parse a markdown table and return {first_col_value: preserve_col_value}."""
    lines = [l for l in block_content.strip().split('\n') if l.strip()]
    if len(lines) < 2:
        return {}

    # Find header row
    header_idx = None
    for i, line in enumerate(lines):
        if '|' in line and preserve_col in line:
            header_idx = i
            break
    if header_idx is None:
        return {}

    headers = [h.strip() for h in lines[header_idx].strip('|').split('|')]
    try:
        preserve_idx = headers.index(preserve_col)
    except ValueError:
        return {}

    preserved = {}
    # Skip header + separator
    for line in lines[header_idx + 2:]:
        if not line.strip().startswith('|'):
            continue
        cells = [c.strip() for c in line.strip('|').split('|')]
        if len(cells) <= preserve_idx:
            continue
        key = cells[0]
        val = cells[preserve_idx]
        preserved[key] = val
    return preserved


RENDERERS = {
    'subfolder-table': ('fs', render_subfolder_table),
    'dhf-table': ('project.yml:dhfs', render_dhf_table),
    'team-table': ('project.yml:team.active', render_team_table),
    'folder-tree': ('fs', render_folder_tree),
    'folder-tree-subset': ('fs', render_folder_tree_subset),
    'strategy-domains': ('project.yml:strategy_domains', render_strategy_domains),
}


def find_blocks(lines):
    """Return list of (open_idx, close_idx, attrs_dict) for each AUTO:STRUCTURE block.
    Raises ValueError on malformed structure.
    """
    blocks = []
    open_stack = []  # (idx, attrs)
    for i, line in enumerate(lines):
        om = OPEN_RE.search(line)
        cm = CLOSE_RE.search(line)
        if om and not cm:  # opening sentinel (close has precedence since it's more specific)
            attrs = parse_attrs(om.group(1))
            open_stack.append((i, attrs))
        elif cm:
            if not open_stack:
                raise ValueError(f"line {i+1}: close sentinel without matching open")
            open_idx, attrs = open_stack.pop()
            blocks.append((open_idx, i, attrs))
    if open_stack:
        idx, _ = open_stack[0]
        raise ValueError(f"line {idx+1}: open sentinel has no matching close")
    return blocks


def render_file(target_path, dry_run=False, verbose=False):
    """Render all sentinel blocks in target_path. Returns True if changed."""
    global PROJECT_ROOT

    target = Path(target_path).resolve()
    if not target.exists():
        raise RuntimeError(f"target file does not exist: {target_path}")

    PROJECT_ROOT = find_project_root(target)
    log(f"[render] target={target} project_root={PROJECT_ROOT}", verbose)

    with open(target) as f:
        original = f.read()

    lines = original.split('\n')
    blocks = find_blocks(lines)

    if not blocks:
        log(f"[render] no sentinel blocks in {target_path}", verbose)
        return False

    project_yml = read_project_yml(PROJECT_ROOT)

    # Process blocks in reverse order so line indices stay valid
    new_lines = lines[:]
    for open_idx, close_idx, attrs in reversed(blocks):
        kind = attrs.get('kind')
        source = attrs.get('source')
        if kind not in RENDERERS:
            raise ValueError(
                f"line {open_idx+1}: unknown kind '{kind}' "
                f"(known: {', '.join(RENDERERS.keys())})")

        expected_source, renderer = RENDERERS[kind]
        # Don't enforce source match — kind implies source but the attribute
        # is still useful as documentation for humans reading the file.

        old_block_content = '\n'.join(new_lines[open_idx+1:close_idx])

        try:
            if kind in ('subfolder-table',):
                new_block = renderer(target, attrs, old_block_content)
            elif kind in ('dhf-table', 'team-table', 'strategy-domains'):
                new_block = renderer(target, attrs, old_block_content, project_yml)
            elif kind in ('folder-tree', 'folder-tree-subset'):
                new_block = renderer(target, attrs, old_block_content, PROJECT_ROOT)
            else:
                raise ValueError(f"dispatch error for kind={kind}")
        except Exception as e:
            raise RuntimeError(f"line {open_idx+1}: render failed for kind={kind}: {e}")

        # Splice: keep open sentinel line, replace middle, keep close sentinel line
        block_lines = new_block.rstrip('\n').split('\n')
        new_lines[open_idx+1:close_idx] = block_lines

    new_content = '\n'.join(new_lines)

    if new_content == original:
        log(f"[render] no changes in {target_path}", verbose)
        return False

    if dry_run:
        print(new_content, end='' if new_content.endswith('\n') else '\n')
        log(f"[render] DRY-RUN: would update {target_path}", verbose)
        return True

    with open(target, 'w') as f:
        f.write(new_content)
    log(f"[render] updated {target_path}", verbose)
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Regenerate AUTO:STRUCTURE sentinel blocks in markdown files.")
    parser.add_argument('files', nargs='+', help='Markdown files to process')
    parser.add_argument('--dry-run', action='store_true',
                        help='Print proposed output to stdout without writing')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Print diagnostics to stderr')
    args = parser.parse_args()

    any_changed = False
    for path in args.files:
        try:
            if render_file(path, dry_run=args.dry_run, verbose=args.verbose):
                any_changed = True
        except ValueError as e:
            print(f"ERROR (malformed): {path}: {e}", file=sys.stderr)
            sys.exit(1)
        except RuntimeError as e:
            print(f"ERROR (source): {path}: {e}", file=sys.stderr)
            sys.exit(2)
        except Exception as e:
            print(f"ERROR (unexpected): {path}: {e}", file=sys.stderr)
            sys.exit(3)

    sys.exit(0 if any_changed or not args.files else 0)


if __name__ == '__main__':
    main()
