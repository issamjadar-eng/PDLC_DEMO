#!/usr/bin/env python3
"""resolve_deps.py — skill dependency-closure resolver for /sync-skills.

Reads the `dependencies:` block from each skill's SKILL.md frontmatter and
computes the transitive closure of skills + the union of required agents, so a
puller who grabs one skill also learns what else must travel with it.

The dependency contract (authored in each SKILL.md frontmatter, documented by
the skill-creator skill) has this shape:

    dependencies:
      skills:
        - name: frontend-slides
          type: required        # required | optional   (default: required)
          reason: consumes the viewport contract + preset registry
        - name: docflow
          type: optional
      agents:
        - regulatory-affairs    # top-level agents that co-install with this skill
        - clinical-affairs

Semantics:
  - `dependencies.skills` — sibling skills this one needs. `required` edges are
    traversed transitively (they form the closure that MUST be co-installed).
    `optional` edges are reported one level deep but never force-pulled.
  - `dependencies.agents` — top-level agents that must be installed into the
    consumer's `.claude/agents/` for this skill to work. The OWNING skill lists
    its agents; a consumer that merely uses them depends on the owning *skill*
    (via `dependencies.skills`) rather than re-listing the agents. So the agent
    union is collected across the required-skill closure.
  - `shared` is an ordinary skill dependency — name it `shared` under
    `dependencies.skills` like any other.

This parser is intentionally dependency-free (no PyYAML): it hand-parses the
bounded, well-known shape above. Anything outside that shape is ignored rather
than erroring, so a malformed block degrades to "no declared deps" instead of
crashing a pull.

Usage:
    resolve_deps.py [--root DIR] [--json] [--missing-against DIR] SKILL [SKILL ...]
    resolve_deps.py [--root DIR] [--json] --all

  --root DIR            Directory containing `skills/<name>/SKILL.md`. Default:
                        the current directory. (sync.sh passes the hitachi path.)
  --all                 Resolve every skill under <root>/skills/.
  --json                Emit a JSON object instead of the text report.
  --missing-against DIR Treat DIR as the CONSUMER root (containing `.claude/skills`
                        and `.claude/agents`). The report flags which closure
                        members are not yet present there — i.e. what a pull
                        would still need to add.

Exit status: 0 on success (even when a requested skill has no deps); 2 on a
usage error or an unreadable/absent requested skill.
"""

import argparse
import json
import os
import sys


def _read_frontmatter(skill_md_path):
    """Return the raw text between the first two `---` fences, or '' if absent."""
    try:
        with open(skill_md_path, "r", encoding="utf-8") as fh:
            lines = fh.read().splitlines()
    except OSError:
        return ""
    if not lines or lines[0].strip() != "---":
        return ""
    body = []
    for line in lines[1:]:
        if line.strip() == "---":
            return "\n".join(body)
        body.append(line)
    return ""  # no closing fence → treat as no frontmatter


def _indent(line):
    return len(line) - len(line.lstrip(" "))


def parse_dependencies(skill_md_path):
    """Parse the `dependencies:` block from a SKILL.md.

    Returns {"skills": [{"name","type","reason"}...], "agents": [name...]}.
    Returns empty lists when the block is absent or malformed.
    """
    result = {"skills": [], "agents": []}
    fm = _read_frontmatter(skill_md_path)
    if not fm:
        return result
    lines = fm.splitlines()

    # Find the `dependencies:` top-level key.
    dep_start = None
    dep_indent = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped == "dependencies:" and _indent(line) == 0:
            dep_start = i + 1
            dep_indent = _indent(line)
            break
    if dep_start is None:
        return result

    # Collect the block: lines more indented than `dependencies:` until dedent.
    block = []
    for line in lines[dep_start:]:
        if line.strip() == "":
            block.append(line)
            continue
        if _indent(line) <= dep_indent:
            break
        block.append(line)

    # Walk the block looking for `skills:` and `agents:` sub-keys.
    section = None
    cur_skill = None
    for line in block:
        if line.strip() == "":
            continue
        ind = _indent(line)
        stripped = line.strip()

        if stripped in ("skills:", "agents:") and ind == 2:
            section = stripped[:-1]  # 'skills' or 'agents'
            cur_skill = None
            continue

        if section == "skills":
            if stripped.startswith("- "):
                # New list item. Either `- name: x` or `- x`.
                cur_skill = {"name": None, "type": "required", "reason": ""}
                rest = stripped[2:].strip()
                if rest.startswith("name:"):
                    cur_skill["name"] = rest[len("name:"):].strip()
                elif rest and ":" not in rest:
                    cur_skill["name"] = rest
                result["skills"].append(cur_skill)
            elif cur_skill is not None and ind >= 6:
                if stripped.startswith("name:"):
                    cur_skill["name"] = stripped[len("name:"):].strip()
                elif stripped.startswith("type:"):
                    val = stripped[len("type:"):].strip().lower()
                    cur_skill["type"] = "optional" if val == "optional" else "required"
                elif stripped.startswith("reason:"):
                    cur_skill["reason"] = stripped[len("reason:"):].strip()

        elif section == "agents":
            if stripped.startswith("- "):
                name = stripped[2:].strip()
                if name.startswith("name:"):
                    name = name[len("name:"):].strip()
                if name:
                    result["agents"].append(name)

    # Drop skill entries that never got a name (malformed) and de-dupe.
    seen = set()
    clean = []
    for s in result["skills"]:
        if s["name"] and s["name"] not in seen:
            seen.add(s["name"])
            clean.append(s)
    result["skills"] = clean
    # De-dupe agents preserving order.
    result["agents"] = list(dict.fromkeys(result["agents"]))
    return result


def skill_md(root, name):
    return os.path.join(root, "skills", name, "SKILL.md")


def skill_exists(root, name):
    return os.path.isfile(skill_md(root, name))


def resolve(root, requested):
    """Compute the dependency closure for `requested` skills.

    Returns a dict:
      requested:        the input skill names (those that exist)
      missing_requested: requested names with no SKILL.md under root
      required_skills:  transitive closure over required edges (excludes requested)
      optional_skills:  [{from, name, reason}] direct optional edges (not traversed)
      agents:           sorted union of dependencies.agents across requested+required
      edges:            [{from, name, type, reason}] every declared skill edge seen
      unresolved:       skill names referenced as deps but absent under root
    """
    requested = list(dict.fromkeys(requested))
    missing_requested = [n for n in requested if not skill_exists(root, n)]
    present_requested = [n for n in requested if skill_exists(root, n)]

    in_closure = set(present_requested)  # required-traversal visited set
    required_skills = []
    optional_skills = []
    edges = []
    unresolved = set()
    agents = []

    # BFS over required edges.
    frontier = list(present_requested)
    while frontier:
        cur = frontier.pop(0)
        deps = parse_dependencies(skill_md(root, cur))
        for a in deps["agents"]:
            if a not in agents:
                agents.append(a)
        for s in deps["skills"]:
            name = s["name"]
            edges.append({"from": cur, "name": name,
                          "type": s["type"], "reason": s["reason"]})
            if s["type"] == "optional":
                optional_skills.append({"from": cur, "name": name,
                                        "reason": s["reason"]})
                continue
            # required
            if not skill_exists(root, name):
                unresolved.add(name)
                continue
            if name not in in_closure:
                in_closure.add(name)
                required_skills.append(name)
                frontier.append(name)

    # Agents from the transitively-pulled required skills too.
    for name in required_skills:
        deps = parse_dependencies(skill_md(root, name))
        for a in deps["agents"]:
            if a not in agents:
                agents.append(a)

    # Optional entries that are actually already in the required closure or
    # requested set are not "extra" — drop them to avoid noise.
    known = in_closure
    optional_skills = [o for o in optional_skills if o["name"] not in known]

    return {
        "requested": present_requested,
        "missing_requested": missing_requested,
        "required_skills": sorted(required_skills),
        "optional_skills": optional_skills,
        "agents": sorted(agents),
        "edges": edges,
        "unresolved": sorted(unresolved),
    }


def _agent_present(consumer_root, name):
    """Is agent `name` installed in the consumer's .claude/agents/?"""
    p = os.path.join(consumer_root, ".claude", "agents", name + ".md")
    return os.path.exists(p)  # exists() follows symlinks; a dangling link → False


def _skill_present(consumer_root, name):
    p = os.path.join(consumer_root, ".claude", "skills", name, "SKILL.md")
    return os.path.isfile(p)


def annotate_missing(closure, consumer_root):
    """Add `missing` sub-lists: closure members absent in the consumer root."""
    missing_skills = [n for n in closure["required_skills"]
                      if not _skill_present(consumer_root, n)]
    missing_agents = [a for a in closure["agents"]
                      if not _agent_present(consumer_root, a)]
    closure["missing_required_skills"] = missing_skills
    closure["missing_agents"] = missing_agents
    return closure


def render_text(closure, consumer_root=None):
    out = []
    req = ", ".join(closure["requested"]) or "(none)"
    out.append(f"Dependency closure for: {req}")
    if closure["missing_requested"]:
        out.append(f"  ! requested skill(s) not found under root: "
                   f"{', '.join(closure['missing_requested'])}")

    rs = closure["required_skills"]
    if rs:
        out.append(f"\n  Required skills ({len(rs)}) — must co-install:")
        for n in rs:
            mark = ""
            if consumer_root is not None and n in closure.get("missing_required_skills", []):
                mark = "   [MISSING locally]"
            out.append(f"    - {n}{mark}")
    else:
        out.append("\n  Required skills: none")

    ag = closure["agents"]
    if ag:
        out.append(f"\n  Agents ({len(ag)}) — must co-install (separate sync surface):")
        for a in ag:
            mark = ""
            if consumer_root is not None and a in closure.get("missing_agents", []):
                mark = "   [MISSING locally]"
            out.append(f"    - {a}{mark}")
    else:
        out.append("\n  Agents: none")

    if closure["optional_skills"]:
        out.append(f"\n  Optional skills ({len(closure['optional_skills'])}) "
                   f"— listed, not auto-pulled:")
        for o in closure["optional_skills"]:
            why = f" — {o['reason']}" if o["reason"] else ""
            out.append(f"    - {o['name']} (from {o['from']}){why}")

    if closure["unresolved"]:
        out.append(f"\n  ! UNRESOLVED required deps (named but absent under root): "
                   f"{', '.join(closure['unresolved'])}")

    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(add_help=True, description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("skills", nargs="*", help="skill name(s) to resolve")
    ap.add_argument("--root", default=".", help="dir containing skills/<name>/SKILL.md")
    ap.add_argument("--all", action="store_true", help="resolve every skill under <root>/skills")
    ap.add_argument("--json", action="store_true", help="emit JSON")
    ap.add_argument("--missing-against", metavar="DIR",
                    help="consumer root; flag closure members absent there")
    args = ap.parse_args(argv)

    root = os.path.abspath(args.root)
    skills_dir = os.path.join(root, "skills")
    if not os.path.isdir(skills_dir):
        print(f"ERROR: no skills/ dir under root: {root}", file=sys.stderr)
        return 2

    if args.all:
        requested = sorted(
            d for d in os.listdir(skills_dir)
            if os.path.isfile(os.path.join(skills_dir, d, "SKILL.md"))
        )
    else:
        requested = args.skills

    if not requested:
        print("ERROR: name at least one skill, or pass --all", file=sys.stderr)
        return 2

    closure = resolve(root, requested)
    if args.missing_against:
        annotate_missing(closure, os.path.abspath(args.missing_against))

    if args.json:
        print(json.dumps(closure, indent=2, sort_keys=True))
    else:
        consumer = os.path.abspath(args.missing_against) if args.missing_against else None
        print(render_text(closure, consumer))

    # Non-fatal: a requested skill that doesn't exist is a usage problem.
    if closure["missing_requested"]:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
