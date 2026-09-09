#!/usr/bin/env python3
"""Tests for render-sentinels.py — focuses on the new variants/depth changes.

Run from project root:
    python3 .claude/skills/medtech-docs/tests/test_render_sentinels.py
"""

import importlib.util
import sys
import tempfile
import textwrap
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / 'scripts' / 'render-sentinels.py'

# Load the script as a module so we can call its functions directly.
spec = importlib.util.spec_from_file_location('render_sentinels', SCRIPT)
rs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rs)


PROJECT_YML = {
    'dhfs': [
        {
            'leaf': 'demo-suite',
            'architecture_name': 'Suite',
            'marketed_name': 'Demo Suite',
            'role': 'system',
            'filing': '510k',
            'dhf_purpose': 'System DDP, integrated risk file, system V&V',
        },
        {
            'leaf': 'demo-pre-op',
            'architecture_name': 'PreOp',
            'marketed_name': 'Demo Planning',
            'role': 'item',
            'filing': '510k',
            'classification': {
                'samd': True, 'class': 'II', 'iec62304': 'C', 'ai_enabled': True,
            },
            'dhf_purpose': 'Item DDP, SRS, SDS, item V&V, AI/ML records',
        },
        {
            'leaf': 'demo-mgmt',
            'architecture_name': 'Management',
            # No marketed_name → falls back to preserve / TODO
            'role': 'item',
            'filing': '510k',
            'classification': {
                'samd': False, 'class': 'I', 'iec62304': 'B', 'ai_enabled': False,
            },
        },
    ],
}


def _run(name, fn):
    try:
        fn()
        print(f"  ok  {name}")
        return True
    except AssertionError as e:
        print(f"FAIL  {name}: {e}")
        return False
    except Exception as e:
        print(f"FAIL  {name}: unexpected {type(e).__name__}: {e}")
        return False


# ─── dhf-table tests ─────────────────────────────────────────────────────

def test_dhf_table_default_reads_architecture_and_marketed_name():
    out = rs.render_dhf_table(target_file='unused', attrs={}, old_block_content='', project_yml=PROJECT_YML)
    assert '**Suite**' in out, f"architecture_name not used: {out}"
    assert 'Demo Suite' in out, f"marketed_name not read for system row: {out}"
    assert 'Demo Planning' in out, f"marketed_name not read for item row: {out}"
    assert '**PreOp**' in out, "PreOp architecture_name missing"
    # The mgmt DHF has no marketed_name and no preserved value → TODO
    assert 'TODO' in out, "TODO fallback missing for unset marketed_name"
    # Filing column present
    assert '510k' in out

def test_dhf_table_naming_variant_emits_4_columns():
    out = rs.render_dhf_table(
        target_file='unused',
        attrs={'variant': 'naming'},
        old_block_content='',
        project_yml=PROJECT_YML,
    )
    header = out.split('\n')[0]
    assert header == '| Architecture Name | Marketed Name | Classification | IEC 62304 |', f"naming header wrong: {header}"
    # No Filing column, no Role column
    assert ' Role ' not in header
    assert ' Filing ' not in header
    # Reads architecture_name
    assert '**PreOp**' in out
    assert '**Suite**' in out

def test_dhf_table_flat_multi_variant_emits_purpose_column():
    out = rs.render_dhf_table(
        target_file='unused',
        attrs={'variant': 'flat-multi'},
        old_block_content='',
        project_yml=PROJECT_YML,
    )
    header = out.split('\n')[0]
    assert header == '| DHF | `role` | Classification | Purpose |', f"flat-multi header wrong: {header}"
    # Reads dhf_purpose
    assert 'System DDP, integrated risk file, system V&V' in out
    assert 'Item DDP, SRS, SDS, item V&V, AI/ML records' in out
    # demo-mgmt has no dhf_purpose and no preserve → TODO
    assert 'TODO' in out
    # Uses leaf in DHF column with backticks
    assert '`demo-pre-op`' in out

def test_dhf_table_marketed_name_preserve_fallback():
    """When project.yml lacks marketed_name, fall back to old block's value."""
    old_block = textwrap.dedent("""\
        | Architecture Name | Marketed Name | Role | Classification | IEC 62304 | Filing |
        |---|---|---|---|---|---|
        | **Management** | Hand-Authored Mgmt | item | non-SaMD, Class I | Class B | 510k |
    """)
    out = rs.render_dhf_table(
        target_file='unused', attrs={}, old_block_content=old_block, project_yml=PROJECT_YML,
    )
    assert 'Hand-Authored Mgmt' in out, "preserve-column fallback failed for marketed_name"

def test_dhf_table_unknown_variant_raises():
    try:
        rs.render_dhf_table(
            target_file='unused',
            attrs={'variant': 'gibberish'},
            old_block_content='',
            project_yml=PROJECT_YML,
        )
        assert False, "expected RuntimeError for unknown variant"
    except RuntimeError as e:
        assert 'unknown variant' in str(e)


# ─── folder-tree depth tests ──────────────────────────────────────────────

def _make_temp_tree():
    """Create a temp dir tree:
        root/
          a/
            a1/
              a1file.txt
            a2.txt
          b/
            b1/
          c.txt
    """
    tmp = Path(tempfile.mkdtemp())
    (tmp / 'a' / 'a1').mkdir(parents=True)
    (tmp / 'a' / 'a1' / 'a1file.txt').write_text('x')
    (tmp / 'a' / 'a2.txt').write_text('x')
    (tmp / 'b' / 'b1').mkdir(parents=True)
    (tmp / 'c.txt').write_text('x')
    return tmp

def test_folder_tree_default_depth_1():
    tmp = _make_temp_tree()
    out = rs.render_folder_tree(target_file='unused', attrs={}, old_block_content='', project_root=tmp)
    # Top-level only — no a1, no b1, no a2.txt, no a1file.txt
    assert 'a/' in out
    assert 'b/' in out
    assert 'c.txt' in out
    assert 'a1/' not in out, f"depth=1 leaked a1: {out}"
    assert 'b1/' not in out, f"depth=1 leaked b1: {out}"
    assert 'a1file.txt' not in out

def test_folder_tree_depth_2_recurses_one_level():
    tmp = _make_temp_tree()
    out = rs.render_folder_tree(
        target_file='unused', attrs={'depth': '2'}, old_block_content='', project_root=tmp,
    )
    assert 'a/' in out
    assert 'a1/' in out, f"depth=2 missing a1: {out}"
    assert 'a2.txt' in out, f"depth=2 missing a2.txt: {out}"
    assert 'b1/' in out
    # depth=2 should NOT include 3rd level
    assert 'a1file.txt' not in out, f"depth=2 leaked level-3 file: {out}"
    # Tree connectors present
    assert '├──' in out or '└──' in out

def test_folder_tree_subset_default_depth_2():
    tmp = _make_temp_tree()
    out = rs.render_folder_tree_subset(
        target_file='unused', attrs={}, old_block_content='', project_root=tmp,
    )
    # Subset default is 2 → recurses one level
    assert 'a1/' in out, f"folder-tree-subset default depth should be 2: {out}"

def test_folder_tree_depth_caps_at_4():
    tmp = _make_temp_tree()
    out = rs.render_folder_tree(
        target_file='unused', attrs={'depth': '99'}, old_block_content='', project_root=tmp,
    )
    # Should still render, capped at 4 — for our tree, depth 4 is plenty
    assert 'a1file.txt' in out

def test_folder_tree_depth_invalid_raises():
    tmp = _make_temp_tree()
    try:
        rs.render_folder_tree(
            target_file='unused', attrs={'depth': 'abc'}, old_block_content='', project_root=tmp,
        )
        assert False, "expected RuntimeError"
    except RuntimeError as e:
        assert 'integer' in str(e).lower()

    try:
        rs.render_folder_tree(
            target_file='unused', attrs={'depth': '0'}, old_block_content='', project_root=tmp,
        )
        assert False, "expected RuntimeError"
    except RuntimeError as e:
        assert '>= 1' in str(e)


# ─── Idempotence: render twice → same output ──────────────────────────────

def test_dhf_table_idempotent():
    a = rs.render_dhf_table('unused', {'variant': 'naming'}, '', PROJECT_YML)
    b = rs.render_dhf_table('unused', {'variant': 'naming'}, a, PROJECT_YML)
    assert a == b, f"naming variant not idempotent:\nA={a!r}\nB={b!r}"

    a = rs.render_dhf_table('unused', {'variant': 'flat-multi'}, '', PROJECT_YML)
    b = rs.render_dhf_table('unused', {'variant': 'flat-multi'}, a, PROJECT_YML)
    assert a == b, f"flat-multi variant not idempotent:\nA={a!r}\nB={b!r}"


def main():
    tests = [
        ('dhf-table default reads architecture_name + marketed_name', test_dhf_table_default_reads_architecture_and_marketed_name),
        ('dhf-table naming variant emits 4 columns', test_dhf_table_naming_variant_emits_4_columns),
        ('dhf-table flat-multi variant emits Purpose', test_dhf_table_flat_multi_variant_emits_purpose_column),
        ('dhf-table marketed_name preserve fallback', test_dhf_table_marketed_name_preserve_fallback),
        ('dhf-table unknown variant raises', test_dhf_table_unknown_variant_raises),
        ('folder-tree default depth=1', test_folder_tree_default_depth_1),
        ('folder-tree depth=2 recurses', test_folder_tree_depth_2_recurses_one_level),
        ('folder-tree-subset default depth=2', test_folder_tree_subset_default_depth_2),
        ('folder-tree depth caps at 4', test_folder_tree_depth_caps_at_4),
        ('folder-tree depth=invalid raises', test_folder_tree_depth_invalid_raises),
        ('dhf-table variants idempotent', test_dhf_table_idempotent),
    ]
    passed = sum(_run(name, fn) for name, fn in tests)
    total = len(tests)
    print(f"\n{passed}/{total} passed")
    sys.exit(0 if passed == total else 1)


if __name__ == '__main__':
    main()
