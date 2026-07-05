#!/usr/bin/env python3
"""test_slop.py — assertions for the AI-tells (slop) detector. No external deps."""
from __future__ import annotations
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPT = HERE.parent / "scripts" / "lint_slop.py"
passed = failed = 0


def check(name: str, cond: bool, detail: str = "") -> None:
    global passed, failed
    if cond:
        passed += 1
        print(f"  PASS  {name}")
    else:
        failed += 1
        print(f"  FAIL  {name}  {detail}")


def lint(text: str, *flags: str) -> dict:
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
        f.write(text)
        path = f.name
    try:
        out = subprocess.run([sys.executable, str(SCRIPT), path, "--json", *flags],
                             capture_output=True, text=True).stdout
        return json.loads(out)["results"][0]
    finally:
        Path(path).unlink()


def tags(res: dict) -> set[str]:
    return {f["tag"] for f in res["findings"]}


# --------------------------------------------------------------------------- #
SLOP = (
    "In today's fast-paced world, AI is not just a tool — it's a paradigm shift. "
    "It delves into the intricate tapestry of your data, underscoring its importance. "
    "This meticulous approach plays a crucial role. It serves as a testament to innovation. "
    "Moreover, it scales. Furthermore, it adapts. Additionally, it endures.\n"
)
print("slop sample — tells must fire")
s = lint(SLOP)
t = tags(s)
for want in ("aitell-emdash", "aitell-vocab", "aitell-construction", "aitell-opener", "aitell-signpost"):
    check(f"tag present: {want}", want in t, f"got {sorted(t)}")

# ultra-marker fires even once, in otherwise clean prose
print("\nultra-marker single occurrence")
u = lint("The report is short. We will delve into the results next quarter and report back.")
check("'delve' flagged as vocab", "aitell-vocab" in tags(u), f"got {sorted(tags(u))}")

# em-dash density threshold
print("\nem-dash density")
many = lint("A — b — c — d. " * 8)   # very high dash rate
check("high em-dash density flagged", "aitell-emdash" in tags(many), f"em/1k={many['em_per_1k']}")
clean = lint("The team shipped the release on time. Quality held. Reviews were short. "
             "Findings were few. The plan worked, and the customer was satisfied with it.")
check("clean low-dash prose NOT flagged for em-dash", "aitell-emdash" not in tags(clean),
      f"em/1k={clean['em_per_1k']}, tags={sorted(tags(clean))}")

# folklore is opt-in
print("\nfolklore gating")
fr = lint("The platform is robust and seamless, and we leverage it to navigate change.")
check("'robust/leverage' NOT flagged without --folklore", "aitell-folklore" not in tags(fr))
fr2 = lint("The platform is robust and seamless, and we leverage it to navigate change.", "--folklore")
check("folklore flagged WITH --folklore", "aitell-folklore" in tags(fr2), f"got {sorted(tags(fr2))}")

# skip zones: a tell inside a code fence is not prose
print("\nskip zones")
code = lint("Normal sentence here, nothing to see.\n\n```\ndelve tapestry meticulous\n```\n")
check("vocab inside code fence NOT flagged",
      not any("tapestry" in f["match"] or "delve" in f["match"] for f in code["findings"]),
      f"findings={[f['match'] for f in code['findings']]}")

# References section excluded (em-dashes there shouldn't count)
print("\nreferences section excluded")
refs = lint("Short clean body sentence with no dashes at all here.\n\n## References\n"
            "1. A — B — C — D — E — F — G — H — I — J — K\n")
check("em-dashes in References not counted", refs["em_per_1k"] == 0.0, f"em/1k={refs['em_per_1k']}")

# --------------------------------------------------------------------------- #
print(f"\n{passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
