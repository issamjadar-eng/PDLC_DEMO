r"""Journey loader — the two paths a project walks, evaluated live.

MAP vs STATE. The map is authored by `medtech-docs` at
`.claude/skills/medtech-docs/registry/journey.yaml`: per-phase `done_when`
predicates, `requires` edges, `producer` commands, `levels`, `derivations` and
a binding `rendering:` block. This module NEVER authors "done" — it evaluates
the authored predicates against the filesystem. A hardcoded phase table here
would make the console the author of the semantics it renders. Add a phase by
editing the yaml, not this file.

TITLES ARE NOT IN THE MAP, BY DESIGN. `new-project-bootstrap.md` is canonical
for standup phase numbers, titles and why-text; each phase's `anchor:` locates
its heading by PREFIX (headings carry parentheticals the map must not mirror).
Milestone names/order come from `docs/project/milestones/regulatory.yml`.
Restating either in the map would create exactly the drift
`.claude/rules/claude-md-references.md` exists to prevent.

NO GENERATED ARTIFACT, NO REFRESH BUTTON. Journey state is repo truth and every
probe is a stat(). A 2s private TTL coalesces the derivation across one page
load. This cache is deliberately NOT the Document Pipeline's 15s module-global:
sharing it would serve journey data up to 15s stale, and "run a skill command
in the terminal, alt-tab back" showing the old state is the one failure this
surface must not have.

DISCOVERY IS INVERTED HERE, ON PURPOSE — DO NOT "FIX" IT. `discover()` returns
True whenever the MAP exists, not when a producer artifact does. Every other
tab lights only once its data lands; this one must not, because a journey tab
that hides while the project is immature hides exactly when it is needed
(journey.yaml#rendering.always_discoverable).

ARTIFACT LANGUAGE, NOT COMPLETION LANGUAGE. Every predicate detects an
*artifact*, never *quality*. State labels say "artifacts present", never
"complete" and never a bare ✓ (journey.yaml#rendering.language). In a regulated
project a checkmark against a DHF role is a claim someone may be asked to
substantiate — keep it out of the UI.
"""
from __future__ import annotations

import re
import time
from pathlib import Path

MAP_REL = (".claude", "skills", "medtech-docs", "registry", "journey.yaml")

_CACHE: dict = {"at": 0.0, "data": None}
_CACHE_TTL_S = 2.0

# `(\S+)` rather than `(\d+)` is what makes the non-integer "6.5" heading parse.
_PHASE_HEAD = re.compile(r"^## Phase (\S+) — (.+)$")

# Lines that are structure, not prose — skipped when hunting a phase's why-text.
_NOT_PROSE = ("#", "|", "```", ">", "- ", "* ", "1.", "2.", "_", "!")


def map_path(repo_root: Path) -> Path:
    return repo_root.joinpath(*MAP_REL)


def discover(repo_root: Path) -> dict:
    """Nav probe. True whenever the map exists — see the inverted-discovery
    note above. Wrapped: a raise here would take down every route."""
    try:
        return {"has_any": map_path(repo_root).is_file()}
    except Exception:
        return {"has_any": False}


# ---------------------------------------------------------------------------
# readers
# ---------------------------------------------------------------------------
def _read_yaml(path: Path):
    try:
        import yaml

        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _read_json(path: Path):
    try:
        import json

        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _dig(data, dotted: str):
    """Resolve a dotted key, treating all-digit segments as list indices so
    `registries.0.repo` works."""
    cur = data
    for seg in dotted.split("."):
        if isinstance(cur, list) and seg.isdigit():
            i = int(seg)
            cur = cur[i] if 0 <= i < len(cur) else None
        elif isinstance(cur, dict):
            cur = cur.get(seg)
        else:
            return None
        if cur is None:
            return None
    return cur


def _parse_guide(repo_root: Path, rel: str) -> dict[str, dict]:
    """`{phase_id: {head, title, why}}` from the guide's `## Phase N — Title`
    headings. A missing guide degrades to `{}` — phases then render with their
    id only, never an exception."""
    try:
        lines = (repo_root / rel).read_text(encoding="utf-8").splitlines()
    except OSError:
        return {}
    out: dict[str, dict] = {}
    cur: dict | None = None
    fenced = False
    for line in lines:
        s = line.strip()
        if s.startswith("```"):
            # Track fences: a command inside one is not the section's why-text.
            fenced = not fenced
            continue
        if fenced:
            continue
        m = _PHASE_HEAD.match(line)
        if m:
            num, title = m.group(1).rstrip(":"), m.group(2).strip()
            cur = {"head": f"Phase {num} — {title}", "title": title, "why": ""}
            out[num] = cur
            continue
        if cur is None or cur["why"]:
            continue
        if not s or s.startswith(_NOT_PROSE) or s.endswith(":"):
            # Trailing-colon lines are list lead-ins ("This wires up:"), not
            # descriptions.
            continue
        cur["why"] = s[:280] + ("…" if len(s) > 280 else "")
    return out


def _guide_entry(guide: dict, phase_id: str, anchor: str) -> dict:
    """`anchor:` is a PREFIX locator, not a copy — the map carries
    "Phase 6 — Architecture & component strategy" while the guide heading may
    run longer. Prefix-match first, then the id, then a bare fallback."""
    if anchor:
        for e in guide.values():
            if e["head"].startswith(anchor):
                return e
    if phase_id in guide:
        return guide[phase_id]
    return {"head": f"Phase {phase_id}", "title": f"Phase {phase_id}", "why": ""}


# ---------------------------------------------------------------------------
# predicates
# ---------------------------------------------------------------------------
def _check_all_exist(repo_root: Path, paths: list) -> dict:
    missing = [p for p in paths if not (repo_root / p).exists()]
    n = len(paths)
    return {"kind": "all_exist", "label": f"{n - len(missing)}/{n} required paths present",
            "ok": not missing,
            "detail": ("missing: " + ", ".join(missing)) if missing else ", ".join(paths)}


def _check_any_exist(repo_root: Path, globs: list) -> dict:
    total = 0
    for g in globs:
        try:
            total += sum(1 for _ in repo_root.glob(g))
        except Exception:
            pass
    return {"kind": "any_exist", "label": f"{total} match" + ("" if total == 1 else "es"),
            "ok": total > 0, "detail": ", ".join(globs)}


def _check_yaml_nonempty(repo_root: Path, spec: dict) -> dict:
    f, key = spec.get("file", ""), spec.get("key", "")
    val = _dig(_read_yaml(repo_root / f), key) if f and key else None
    ok = bool(val)
    return {"kind": "yaml_nonempty", "label": f"{f}#{key}", "ok": ok,
            "detail": (str(val)[:120] if ok else "unset")}


def _check_file_contains(repo_root: Path, spec: dict) -> dict:
    f, pattern = spec.get("file", ""), spec.get("pattern", "")
    ok, detail = False, "file not found"
    try:
        ok = bool(re.search(pattern, (repo_root / f).read_text(encoding="utf-8")))
        detail = "matched" if ok else "no match"
    except OSError:
        pass
    except re.error as e:
        detail = f"bad pattern in map: {e}"
    return {"kind": "file_contains", "label": f"{f} ~ /{pattern}/", "ok": ok, "detail": detail}


# ---------------------------------------------------------------------------
# derivations — declared in the map, computed here
# ---------------------------------------------------------------------------
def _derive_registry_configured(repo_root: Path, spec: dict) -> dict:
    """At least one `registries[]` entry is a fetchable registry.

    Asks a SET question, not a positional one. `registries[0]` is
    conventionally the builtin (Anthropic) entry with no `repo` key, so a
    positional probe like `registries.0.repo` reports a correctly configured
    project as unconfigured — which is exactly what it did before this
    derivation replaced it.
    """
    want = str(spec.get("requires_type") or "github")
    data = _read_yaml(repo_root / "project.yml") or {}
    hits = [r for r in (data.get("registries") or [])
            if isinstance(r, dict) and r.get("type") == want and r.get("repo")]
    return {"kind": "derived", "name": "registry_configured",
            "label": f"a {want} skill registry is configured", "ok": bool(hits),
            "detail": (", ".join(str(r.get("repo")) for r in hits) if hits
                       else f"no registries[] entry with type: {want} and a repo")}


def _derive_claude_md_personalized(repo_root: Path, spec: dict) -> dict:
    """CLAUDE.md names the project rather than the init template's placeholder.

    The project name is READ FROM project.yml, never hardcoded — this file ships
    to every project using the toolchain.
    """
    name = _dig(_read_yaml(repo_root / "project.yml"), "project.name") or ""
    if not name:
        return {"kind": "derived", "name": "claude_md_personalized",
                "label": "CLAUDE.md personalized", "ok": False,
                "detail": "project.yml has no project.name to check against"}
    try:
        text = (repo_root / "CLAUDE.md").read_text(encoding="utf-8")
    except OSError:
        return {"kind": "derived", "name": "claude_md_personalized",
                "label": "CLAUDE.md personalized", "ok": False,
                "detail": "CLAUDE.md not found"}
    ok = name.lower() in text.lower()
    return {"kind": "derived", "name": "claude_md_personalized",
            "label": "CLAUDE.md personalized", "ok": ok,
            "detail": (f"names the project ({name})" if ok
                       else f"does not mention project.name ({name})")}


def _strategy_output_paths(repo_root: Path) -> dict[str, str]:
    """domain key → repo-relative path, from project.yml strategy_domains[].
    NEVER hardcode the filenames (audit-wiring-before-adding-fields)."""
    data = _read_yaml(repo_root / "project.yml") or {}
    out: dict[str, str] = {}
    for row in (data.get("strategy_domains") or []):
        if isinstance(row, dict) and row.get("key") and row.get("output_path"):
            out[str(row["key"])] = str(row["output_path"])
    return out


def _derive_strategy_pair(repo_root: Path, spec: dict) -> dict:
    """The named strategy domains exist and are non-stub.

    `non_stub` deliberately, not "has structured decisions": this project's
    strategy docs record decisions in two formats and only one domain has
    migrated to the structured one. Demanding structured decisions would report
    documents that are demonstrably written as not-yet-done.
    """
    want = [str(x) for x in (spec.get("domains") or [])]
    resolved = _strategy_output_paths(repo_root)
    try:
        from console.strategy.loader import load_domains

        by_slug = {d["slug"]: d for d in load_domains(repo_root)}
    except Exception:
        by_slug = {}
    rows, ok_count = [], 0
    for key in want:
        path = resolved.get(key)
        d = by_slug.get(key)
        row = {"key": key, "path": path,
               "exists": bool(path) and (repo_root / path).is_file(),
               "stub": bool(d["stub"]) if d else True,
               "decisions": (d or {}).get("decisions", 0)}
        row["ok"] = row["exists"] and not row["stub"]
        ok_count += 1 if row["ok"] else 0
        rows.append(row)
    missing = ", ".join(r["key"] for r in rows if not r["ok"])
    return {"kind": "derived", "name": "architecture_and_regulatory_strategy",
            "label": "architecture + regulatory strategy assembled",
            "ok": bool(want) and ok_count == len(want),
            "detail": (f"{ok_count}/{len(want)} assembled"
                       + (f" · awaiting: {missing}" if missing else "")),
            "rows": rows}


def _dhf_paths(repo_root: Path) -> list[str]:
    data = _read_yaml(repo_root / "project.yml") or {}
    return [str(r["path"]) for r in (data.get("dhfs") or [])
            if isinstance(r, dict) and r.get("path")]


def _derive_dhfs_scaffolded(repo_root: Path, spec: dict) -> dict:
    paths = _dhf_paths(repo_root)
    missing = [p for p in paths if not (repo_root / p).is_dir()]
    return {"kind": "derived", "name": "dhfs_scaffolded", "label": "DHF folders present",
            "ok": bool(paths) and not missing,
            "detail": (f"{len(paths) - len(missing)}/{len(paths)} declared DHFs on disk"
                       + (f" · missing: {', '.join(missing)}" if missing else ""))}


def _derive_dhfs_have_design_controls(repo_root: Path, spec: dict) -> dict:
    sub = spec.get("requires_subpath") or "design-controls"
    paths = _dhf_paths(repo_root)
    withdc = [p for p in paths
              if (repo_root / p / sub).is_dir()
              and any((repo_root / p / sub).iterdir())]
    return {"kind": "derived", "name": "dhfs_have_design_controls",
            "label": "design-control roles present",
            "ok": bool(paths) and len(withdc) == len(paths),
            "detail": f"{len(withdc)}/{len(paths)} DHFs carry a non-empty {sub}/ folder"}


_SYNC_DATE = re.compile(r"^##\s+(\d{4}-\d{2}-\d{2})", re.MULTILINE)


def _derive_sync_health(repo_root: Path, spec: dict) -> dict:
    """Steady-state health for the terminal standup phase — NOT completion."""
    skills = 0
    try:
        skills = sum(1 for _ in (repo_root / ".claude" / "skills").glob("*/SKILL.md"))
    except Exception:
        pass
    log = repo_root / (spec.get("sync_log") or ".claude/sync-log.md")
    last, age_days = "", None
    try:
        dates = _SYNC_DATE.findall(log.read_text(encoding="utf-8"))
        if dates:
            last = max(dates)
            age_days = (time.time() - time.mktime(time.strptime(last, "%Y-%m-%d"))) / 86400
    except Exception:
        pass
    return {"installed_skills": skills, "last_sync": last,
            "age_days": int(age_days) if age_days is not None else None,
            "log_present": log.is_file()}


def _derive_milestone_evidence(repo_root: Path, spec: dict, milestone_id: str) -> dict:
    """Evidence inventory for one milestone, from what /tracker PUBLISHES.

    Row attribution comes from the row-source sidecar (structural, unambiguous)
    and recorded status from the overlay (the tracker's own durable, curated
    home for status). The tracker's markdown table is deliberately NOT parsed:
    the tracker merges markdown with the overlay at render time and the overlay
    wins, so a second parse here would disagree with the dashboard the team
    actually reads — the exact fork this derivation exists to avoid.

    Consequently there is NO readiness verdict here. Readiness belongs to
    `/tracker assess`; when its sidecar is absent, this reports movement
    (rows that have left "Not Started") and says the verdict does not exist.
    """
    rs = _read_json(repo_root / (spec.get("row_source") or "")) or {}
    rows = rs.get("rows") if isinstance(rs, dict) else None
    if not isinstance(rows, dict):
        return {"kind": "derived", "name": "milestone_evidence", "ok": False,
                "label": "evidence inventory",
                "detail": "tracker row-source sidecar not found — run /tracker generate",
                "total": 0, "scoped_out": 0, "moved": 0, "not_started": 0,
                "unrecorded": 0, "readiness_available": False}

    ov_doc = _read_yaml(repo_root / (spec.get("overlay") or "")) or {}
    overlay = ov_doc.get("rows") if isinstance(ov_doc, dict) else None
    overlay = overlay if isinstance(overlay, dict) else {}

    scoped_out_set = {str(s) for s in (spec.get("scoped_out_statuses") or [])}
    not_started_set = {str(s) for s in (spec.get("not_started_statuses") or [])}

    total = scoped_out = moved = not_started = unrecorded = 0
    for rid, meta in rows.items():
        if not isinstance(meta, dict) or meta.get("from_milestone") != milestone_id:
            continue
        total += 1
        st = (overlay.get(rid) or {}).get("status") if isinstance(overlay.get(rid), dict) else None
        st = str(st).strip() if st is not None else ""
        if not st:
            # Status lives in the tracker markdown, which this view does not
            # parse. Counted as its own bucket rather than folded into
            # "not started" — which would assert a status nobody read.
            unrecorded += 1
        elif st in scoped_out_set:
            scoped_out += 1
        elif st in not_started_set:
            not_started += 1
        else:
            moved += 1

    in_scope = total - scoped_out
    readiness = repo_root / (spec.get("readiness_artifact") or "")
    return {
        "kind": "derived", "name": "milestone_evidence",
        "label": "evidence inventory",
        # `ok` means "this milestone has evidence in motion" — an artifact
        # signal, never a readiness verdict.
        "ok": moved > 0,
        "detail": (f"{total} tracker rows · {in_scope} in scope · {moved} in motion"
                   + (f" · {scoped_out} scoped out" if scoped_out else "")
                   + (f" · {unrecorded} status recorded in the tracker" if unrecorded else "")),
        "total": total, "in_scope": in_scope, "scoped_out": scoped_out,
        "moved": moved, "not_started": not_started, "unrecorded": unrecorded,
        "readiness_available": readiness.is_file(),
        "readiness_owner": spec.get("readiness_owner", "/tracker assess"),
    }


# ---------------------------------------------------------------------------
# phase evaluation
# ---------------------------------------------------------------------------
def _eval_predicates(repo_root: Path, spec: dict, ctx: dict, milestone_id="") -> list[dict]:
    """One check row per predicate key. Multiple keys on a phase are ANDed."""
    checks: list[dict] = []
    for key, val in (spec or {}).items():
        if key in ("id", "label"):
            continue
        if key == "all_exist":
            checks.append(_check_all_exist(repo_root, val or []))
        elif key == "any_exist":
            checks.append(_check_any_exist(repo_root, val or []))
        elif key == "yaml_nonempty":
            checks.append(_check_yaml_nonempty(repo_root, val or {}))
        elif key == "file_contains":
            checks.append(_check_file_contains(repo_root, val or {}))
        elif key == "derived":
            checks.append(_eval_derivation(repo_root, str(val), ctx, milestone_id))
        else:
            checks.append({
                "kind": "unknown", "label": f"unsupported predicate '{key}'", "ok": False,
                "detail": "the map declares a predicate this console does not "
                          "implement — update the Journey loader",
            })
    return checks


def _eval_derivation(repo_root: Path, name: str, ctx: dict, milestone_id="") -> dict:
    spec = (ctx["derivations"].get(name) or {})
    if name == "registry_configured":
        return _derive_registry_configured(repo_root, spec)
    if name == "claude_md_personalized":
        return _derive_claude_md_personalized(repo_root, spec)
    if name == "architecture_and_regulatory_strategy":
        return _derive_strategy_pair(repo_root, spec)
    if name == "dhfs_scaffolded":
        return _derive_dhfs_scaffolded(repo_root, spec)
    if name == "dhfs_have_design_controls":
        return _derive_dhfs_have_design_controls(repo_root, spec)
    if name == "milestone_evidence":
        return _derive_milestone_evidence(repo_root, spec, milestone_id)
    return {"kind": "derived", "name": name, "label": name, "ok": False,
            "detail": "the map declares a derivation this console does not "
                      "implement — update the Journey loader"}


def _eval_levels(repo_root: Path, levels: list, ctx: dict) -> tuple[list[dict], dict | None]:
    """Ordered and cumulative: the highest satisfied level wins. The map
    declares the ladder; this only walks it."""
    out = []
    for lv in levels or []:
        checks = _eval_predicates(repo_root, lv, ctx)
        out.append({"id": lv.get("id"), "label": lv.get("label", lv.get("id", "")),
                    "ok": bool(checks) and all(c["ok"] for c in checks), "checks": checks})
    reached = None
    for lv in out:
        if lv["ok"]:
            reached = lv
    return out, reached


def _build_phase(repo_root: Path, raw: dict, guide: dict, ctx: dict,
                 milestone_id="") -> dict:
    pid = str(raw.get("id", "?"))
    entry = _guide_entry(guide, pid, raw.get("anchor", ""))
    checks = _eval_predicates(repo_root, raw.get("done_when") or {}, ctx, milestone_id)
    levels, reached = _eval_levels(repo_root, raw.get("levels") or [], ctx)
    p = {
        "id": pid,
        "title": raw.get("title") or entry["title"],
        "heading": raw.get("title") or entry["head"],
        "why": raw.get("why") or entry["why"],
        "requires": [str(r) for r in (raw.get("requires") or [])],
        "producer": raw.get("producer", ""),
        "gate_source": raw.get("gate_source", ""),
        "unobservable_note": raw.get("unobservable_note", ""),
        "terminal": bool(raw.get("terminal")),
        "checks": checks,
        "satisfied": sum(1 for c in checks if c["ok"]),
        "total": len(checks),
        "levels": levels,
        "level_reached": reached,
        "gauge": None,
    }
    if p["terminal"] and raw.get("gauge", {}).get("derived") == "sync_health":
        p["gauge"] = _derive_sync_health(repo_root, ctx["derivations"].get("sync_health") or {})
    return p


def _resolve_states(phases: list[dict], state_model: str = "") -> str | None:
    """Assign each phase a state, then return the group's focus phase.

    Artifact presence is resolved for EVERY phase before any `requires` edge is
    read, so state never depends on the order phases appear in the yaml.

    `state_model: evidence-gauge` (the program group) never yields "present".
    A regulatory milestone completes when a package is filed and a regulator
    responds — unobservable from the repo. Only movement is observable, so a
    milestone reads in-motion / next-up / blocked. Under the default model,
    four milestones each holding a few drafting rows all rendered "artifacts
    present", i.e. the entire device program read as finished.
    """
    by_id = {p["id"]: p for p in phases}
    for p in phases:
        p["artifacts_present"] = bool(p["total"]) and p["satisfied"] == p["total"]

    if state_model == "evidence-gauge":
        for p in phases:
            ev = next((c for c in p["checks"] if c.get("name") == "milestone_evidence"), {})
            p["evidence"] = ev
            moved = int(ev.get("moved") or 0)
            prior_moving = all(
                int((by_id[r].get("evidence") or {}).get("moved") or 0) > 0
                for r in p["requires"] if r in by_id
            )
            if moved:
                p["state"] = "in-motion"
            elif prior_moving:
                p["state"] = "next-up"
            else:
                p["state"] = "blocked"
            p["blocked_by"] = [] if prior_moving else [
                r for r in p["requires"]
                if r in by_id and not int((by_id[r].get("evidence") or {}).get("moved") or 0)
            ]
        # Focus = the earliest milestone still awaiting movement; if every one
        # is moving, the earliest moving one is where attention belongs.
        return (next((p["id"] for p in phases if p["state"] == "next-up"), None)
                or next((p["id"] for p in phases if p["state"] == "in-motion"), None))

    for p in phases:
        p["blocked_by"] = [r for r in p["requires"]
                           if r in by_id and not by_id[r]["artifacts_present"]]
        requires_ok = not p["blocked_by"]
        if p["terminal"]:
            # A loop, never a checkbox.
            g = p["gauge"] or {}
            p["state"] = ("looping" if g.get("installed_skills")
                          else ("ready" if requires_ok else "blocked"))
        elif p["artifacts_present"]:
            p["state"] = "present"
        elif p["satisfied"]:
            p["state"] = "partial"
        else:
            p["state"] = "ready" if requires_ok else "blocked"
    focus = next((p["id"] for p in phases if p["state"] in ("ready", "partial")), None)
    if focus is None:
        focus = next((p["id"] for p in phases if p["state"] == "looping"), None)
    return focus


def _expand_milestones(repo_root: Path, group: dict, ctx: dict) -> list[dict]:
    """One phase per milestone, read straight from the milestones file.

    The map declares only WHERE the milestones live and what predicate to run;
    ids, names, descriptions and ORDER stay owned by that file, so adding a
    milestone there is enough — neither the map nor this loader changes.
    """
    rel = group.get("from_milestones") or ""
    doc = _read_yaml(repo_root / rel) or {}
    milestones = doc.get("milestones") if isinstance(doc, dict) else None
    if not isinstance(milestones, list):
        return []
    tmpl = group.get("phase_template") or {}
    out, prev = [], None
    for m in milestones:
        if not isinstance(m, dict) or not m.get("id"):
            continue
        mid = str(m["id"])
        desc = " ".join(str(m.get("description") or "").split())
        raw = {
            "id": mid,
            "title": m.get("name") or mid,
            "why": desc[:280] + ("…" if len(desc) > 280 else ""),
            # The chain follows the declared order in the milestones file.
            "requires": [prev] if prev else [],
            "done_when": tmpl.get("done_when") or {},
            "producer": tmpl.get("producer", ""),
        }
        p = _build_phase(repo_root, raw, {}, ctx, milestone_id=mid)
        p["short_label"] = m.get("short_label", "")
        p["posture"] = m.get("posture", "")
        out.append(p)
        prev = mid
    return out


def load_journey(repo_root: Path) -> dict:
    now = time.monotonic()
    if _CACHE["data"] is not None and now - _CACHE["at"] < _CACHE_TTL_S:
        return _CACHE["data"]

    m = _read_yaml(map_path(repo_root))
    if not isinstance(m, dict):
        data = {"present": False, "groups": [], "rendering": {},
                "hint": "journey map missing — expected " + "/".join(MAP_REL)}
        _CACHE.update(at=now, data=data)
        return data

    rendering = m.get("rendering") or {}
    ctx = {"derivations": m.get("derivations") or {}}
    prefixes = rendering.get("label_prefix") or {}

    groups = []
    for g in (m.get("groups") or []):
        gid = str(g.get("id", ""))
        if g.get("from_milestones"):
            phases = _expand_milestones(repo_root, g, ctx)
            source = g.get("from_milestones", "")
            source_present = (repo_root / source).is_file() if source else False
        else:
            source = g.get("source", "")
            guide = _parse_guide(repo_root, source) if source else {}
            source_present = bool(guide)
            phases = [_build_phase(repo_root, raw, guide, ctx)
                      for raw in (g.get("phases") or [])]
        focus = _resolve_states(phases, str(g.get("state_model") or ""))
        groups.append({
            "id": gid,
            "label": g.get("label", gid),
            "blurb": " ".join(str(g.get("blurb") or "").split()),
            "source": source,
            "source_present": source_present,
            "label_prefix": prefixes.get(gid, "Phase"),
            "phases": phases,
            "focus": focus,
            "state_model": str(g.get("state_model") or "phase"),
            "counts": {
                "total": len(phases),
                "present": sum(1 for p in phases if p["state"] == "present"),
                "in_motion": sum(1 for p in phases if p["state"] == "in-motion"),
                "blocked": sum(1 for p in phases if p["state"] == "blocked"),
            },
        })

    data = {
        "present": True,
        "map_path": "/".join(MAP_REL),
        "rendering": rendering,
        "groups": groups,
    }
    _CACHE.update(at=now, data=data)
    return data
