#!/usr/bin/env python3
"""
test_lint.py — assertions for the writing-well deterministic linter.

Runs lint_prose.py over fixtures and checks that:
  - mechanical tells in prose ARE flagged (recall),
  - clutter inside skip-zones (frontmatter, code, inline code, links, tables) is NOT
    flagged (precision),
  - exit codes honor the advisory-by-default / --strict contract,
  - --json, --only, --max-len behave.

No external deps. Run:  python3 test_lint.py   (or via run_tests.sh)
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPT = HERE.parent / "scripts" / "lint_prose.py"
FIX = HERE / "fixtures"

passed = 0
failed = 0


def run(args: list[str]) -> tuple[int, str]:
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True, text=True,
    )
    return proc.returncode, proc.stdout


def lint_json(path: Path, *extra: str) -> dict:
    code, out = run([str(path), "--json", "--no-color", *extra])
    return json.loads(out)


def check(name: str, cond: bool, detail: str = "") -> None:
    global passed, failed
    if cond:
        passed += 1
        print(f"  PASS  {name}")
    else:
        failed += 1
        print(f"  FAIL  {name}  {detail}")


def tags_in(payload: dict) -> set[str]:
    return {f["tag"] for r in payload["results"] for f in r["findings"]}


def matches_in(payload: dict) -> list[str]:
    return [f["match"].lower() for r in payload["results"] for f in r["findings"]]


def messages_in(payload: dict) -> str:
    return " || ".join(
        f["message"].lower() for r in payload["results"] for f in r["findings"]
    )


# --------------------------------------------------------------------------- #
print("tells.md — mechanical tells must be caught (recall)")
tells = lint_json(FIX / "tells.md")
want_tags = {"clutter", "hedge", "passive", "nominalization", "adverb", "opener", "length", "cliche"}
got_tags = tags_in(tells)
for t in want_tags:
    check(f"tag present: {t}", t in got_tags, f"got {sorted(got_tags)}")

msgs = messages_in(tells)
check("clutter 'in order to' caught", "in order to" in msgs)
check("clutter 'due to the fact that' caught", "due to the fact that" in msgs)
check("nominalization 'make a decision' caught", "make a decision" in msgs)
check("hedge 'very' caught", "'very'" in msgs)
check("cliche 'at the end of the day' caught", "at the end of the day" in msgs)
check("opener 'it is...that' or 'there is' caught", "empty opener" in msgs)
check("passive caught", "passive" in msgs)

# 'important' must NOT be mis-flagged as passive (the -nt false positive we fixed).
check("'is important' NOT flagged passive",
      "is important" not in [m for m in matches_in(tells)],
      f"matches={matches_in(tells)}")

# 'make a decision' must appear once (clutter+nominalization de-duped to one).
mad = [m for m in matches_in(tells) if m == "make a decision"]
check("'make a decision' reported once (deduped)", len(mad) == 1, f"count={len(mad)}")

# --------------------------------------------------------------------------- #
print("\nskipzones.md — clutter in skip-zones must NOT be flagged (precision)")
skip = lint_json(FIX / "skipzones.md")
sk_matches = matches_in(skip)
# The only prose is clean; every 'in order to' lives in a skip-zone or visible link text.
# Frontmatter, fenced/indented code, inline code, table cells, and bare URLs: zero hits.
n_clutter = sum(1 for r in skip["results"] for f in r["findings"] if f["tag"] == "clutter")
# Allow at most the ONE visible link-text 'in order to' (link text is real prose); everything
# else (code/frontmatter/table/url) must be silent.
check("skip-zone clutter suppressed (<=1 from visible link text)",
      n_clutter <= 1, f"clutter findings={n_clutter}, matches={sk_matches}")
check("no 'was decided' from fenced/indented/table code",
      "was decided" not in sk_matches, f"matches={sk_matches}")
check("no 'at the end of the day' from the bare URL",
      "at the end of the day" not in sk_matches)

# --------------------------------------------------------------------------- #
print("\npredicate-adjective passives must NOT fire (precision) + dependency nominalization (recall)")
import tempfile, os
_prose = (
    "The room was thrilled. The trophy is golden. She is happily married.\n"
    "The hills were green and the desk is wooden.\n"
    "The report was written by the analyst.\n"
    "The module has a dependency on the legacy service.\n"
)
with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as _tf:
    _tf.write(_prose)
    _tmp = _tf.name
try:
    adj = lint_json(Path(_tmp))
    passive_matches = [f["match"].lower() for r in adj["results"]
                       for f in r["findings"] if f["tag"] == "passive"]
    for w in ("thrilled", "golden", "married", "green", "wooden"):
        check(f"predicate adj '{w}' NOT flagged passive",
              not any(w in m for m in passive_matches), f"passive={passive_matches}")
    check("genuine passive 'was written' still flagged",
          any("written" in m for m in passive_matches), f"passive={passive_matches}")
    nom_matches = [f["match"].lower() for r in adj["results"]
                   for f in r["findings"] if f["tag"] == "nominalization"]
    check("nominalization 'has a dependency on' caught",
          any("dependency on" in m for m in nom_matches), f"nom={nom_matches}")
finally:
    os.unlink(_tmp)

# --------------------------------------------------------------------------- #
print("\nexit-code contract")
code_default, _ = run([str(FIX / "tells.md"), "--no-color"])
check("default exit 0 even with findings (advisory)", code_default == 0, f"exit={code_default}")
code_strict, _ = run([str(FIX / "tells.md"), "--strict", "--no-color"])
check("--strict exit 1 when findings exist", code_strict == 1, f"exit={code_strict}")
code_clean_strict, _ = run([str(FIX / "skipzones.md"), "--strict", "--no-color", "--only", "cliche"])
# every cliché in skipzones lives in a skip-zone → no cliche finding → strict still 0
check("--strict exit 0 when no findings", code_clean_strict == 0, f"exit={code_clean_strict}")

# --------------------------------------------------------------------------- #
print("\nflags")
only = lint_json(FIX / "tells.md", "--only", "clutter")
check("--only clutter yields only clutter", tags_in(only) <= {"clutter"}, f"got {tags_in(only)}")
maxlen = lint_json(FIX / "tells.md", "--max-len", "5")
check("--max-len 5 increases length flags",
      sum(1 for r in maxlen["results"] for f in r["findings"] if f["tag"] == "length") >= 2)

# --------------------------------------------------------------------------- #
print(f"\n{passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
