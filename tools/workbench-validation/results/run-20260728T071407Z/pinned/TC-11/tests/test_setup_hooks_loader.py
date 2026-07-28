"""Unit tests for hook-description extraction in the Automation section.

A registered hook's description of record is its script's leading header —
the `#` comment block after the shebang (shell) or the module docstring
(python); the `name.sh — description` first-line convention (stamped by the
skill-creator hook template) yields just the description side. Pins
`_script_summary`, `_hook_script_path`, and the full `load_rules_hooks`
row contract against a synthetic .claude tree.

Run from project root:
    python3 .claude/skills/project-console/tests/test_setup_hooks_loader.py
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

_TEST_DIR = Path(__file__).resolve().parent
_CONSOLE_PKG_ROOT = _TEST_DIR.parent  # .claude/skills/project-console/
sys.path.insert(0, str(_CONSOLE_PKG_ROOT))

from console.setup.loader import (  # noqa: E402
    _hook_script_path,
    _script_summary,
    load_rules_hooks,
)

SHELL_HOOK = """\
#!/bin/bash
# guard-thing.sh — Denies risky tool calls when no task is active.
#
# State file: per-session, under .state/.
# ── MULTI-HOOK COEXISTENCE ──
echo hi
"""

PY_HOOK = '''\
#!/usr/bin/env python3
"""
PreToolUse hook — nudges once per skill per session when frontmatter
is edited. Body-only edits are skipped.

Lifecycle details that belong to a second paragraph.
"""
print("hi")
'''

BARE_HOOK = "#!/bin/bash\necho no header\n"


class ScriptSummaryTest(unittest.TestCase):
    def _write(self, tmp: Path, name: str, text: str) -> Path:
        p = tmp / name
        p.write_text(text, encoding="utf-8")
        return p

    def test_shell_header_with_name_dash_convention(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = self._write(Path(tmp), "guard-thing.sh", SHELL_HOOK)
            s = _script_summary(p)
            self.assertTrue(s.startswith("Denies risky tool calls"))
            self.assertNotIn("guard-thing.sh", s)   # filename prefix stripped
            self.assertNotIn("MULTI-HOOK", s)       # stops at blank/divider

    def test_python_docstring_first_paragraph(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = self._write(Path(tmp), "watch.py", PY_HOOK)
            s = _script_summary(p)
            self.assertTrue(s.startswith("PreToolUse hook — nudges"))
            self.assertNotIn("Lifecycle details", s)  # second paragraph excluded

    def test_headerless_script_degrades_to_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = self._write(Path(tmp), "bare.sh", BARE_HOOK)
            self.assertEqual(_script_summary(p), "")

    def test_hook_script_path_extraction(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            hooks = root / ".claude" / "hooks"
            hooks.mkdir(parents=True)
            (hooks / "x.sh").write_text("#!/bin/bash\n", encoding="utf-8")
            cmd = '"$CLAUDE_PROJECT_DIR"/.claude/hooks/x.sh --flag'
            self.assertEqual(_hook_script_path(root, cmd), hooks / "x.sh")
            self.assertIsNone(_hook_script_path(root, "jq --version"))
            self.assertIsNone(_hook_script_path(root, '"$CLAUDE_PROJECT_DIR"/.claude/hooks/missing.sh'))


class LoadRulesHooksTest(unittest.TestCase):
    def test_hook_rows_carry_description_and_owner(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill_hooks = root / ".claude" / "skills" / "demo-skill" / "hooks"
            skill_hooks.mkdir(parents=True)
            (skill_hooks / "guard.sh").write_text(SHELL_HOOK, encoding="utf-8")
            hooks_dir = root / ".claude" / "hooks"
            hooks_dir.mkdir(parents=True)
            (hooks_dir / "demo-guard.sh").symlink_to("../skills/demo-skill/hooks/guard.sh")
            (root / ".claude" / "settings.json").write_text(json.dumps({
                "hooks": {"PreToolUse": [{
                    "matcher": "Edit|Write",
                    "hooks": [{"type": "command",
                               "command": '"$CLAUDE_PROJECT_DIR"/.claude/hooks/demo-guard.sh'}],
                }]}
            }), encoding="utf-8")
            rows = load_rules_hooks(root)["hooks"]
            self.assertEqual(len(rows), 1)
            h = rows[0]
            self.assertEqual(h["owner"], "demo-skill")
            self.assertTrue(h["description"].startswith("Denies risky tool calls"))
            self.assertEqual(h["event"], "PreToolUse")
            self.assertEqual(h["matcher"], "Edit|Write")


if __name__ == "__main__":
    unittest.main(verbosity=2)
