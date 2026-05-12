"""Agent + overlay loader shared by the /advisors skill and project-console.

Reads CC-native subagent markdown files from `.claude/agents/`, parses the
`console:` extension block when present, merges per-project overlays from
`project.yml`, and returns `DomainAgent` objects compatible with the console's
existing rendering pipeline.

Three-tier sourcing model:
  1. Universal / shape-stable globs baked into the agent file (console.sources)
  2. Project overlay adds/excludes from project.yml advisors.overlays.<name>
  3. Reserved for future console-specific overrides (unimplemented in v1)
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Iterable

import yaml


@dataclass(frozen=True)
class DomainAgent:
    name: str
    title: str
    description: str
    kind: str
    model: str | None
    context: list[str]
    sources: list[str]
    system_prompt: str
    members: list[str] = field(default_factory=list)
    moderator: str = "round-robin"
    path: Path | None = None
    group: str | None = None
    tools: list[str] = field(default_factory=list)
    excludes: list[str] = field(default_factory=list)
    # Canonical-role grounding mode (opt-in). When `canonical_roles` is populated,
    # the renderer emits a 3-tier grounding block instead of literal-glob mode.
    # Shape: {"tier_1": [{"role": str, "dhfs": dict|str, "submissions": str}, ...],
    #         "tier_2": [...],
    #         "tier_3": {"researcher": str}}
    canonical_roles: dict | None = None
    researcher: str | None = None

    @property
    def is_panel(self) -> bool:
        return self.kind == "panel"

    @property
    def is_system(self) -> bool:
        return self.name.startswith("_")

    @property
    def is_canonical_role_mode(self) -> bool:
        return bool(self.canonical_roles)


@dataclass(frozen=True)
class Group:
    name: str
    title: str
    description: str
    order: int
    agents: list[DomainAgent]

    @property
    def panels(self) -> list[DomainAgent]:
        return [a for a in self.agents if a.is_panel]

    @property
    def solo(self) -> list[DomainAgent]:
        return [a for a in self.agents if not a.is_panel]


def _titleize(name: str) -> str:
    return " ".join(p.capitalize() for p in name.replace("_", "-").split("-"))


def _parse_frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---"):
        raise ValueError("agent file must start with YAML frontmatter")
    _, frontmatter, body = text.split("---", 2)
    data = yaml.safe_load(frontmatter) or {}
    return data, body.lstrip("\n")


def _as_list(value) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    return list(value)


def load_agent_file(path: Path) -> DomainAgent:
    """Load a single agent file. Accepts CC-native frontmatter with an optional
    `console:` extension block, and legacy console frontmatter (flat)."""
    meta, body = _parse_frontmatter(path.read_text(encoding="utf-8"))
    name = meta.get("name") or path.stem
    console_ext = meta.get("console") or {}

    # CC-native fields
    description = meta.get("description", "")
    tools_raw = meta.get("tools")
    if isinstance(tools_raw, str):
        tools = [t.strip() for t in tools_raw.split(",") if t.strip()]
    else:
        tools = _as_list(tools_raw)
    model = meta.get("model") or console_ext.get("model")

    # Console-only fields: prefer console: block, fall back to legacy flat
    # frontmatter (title/kind/sources/members at top level) for back-compat.
    title = console_ext.get("title") or meta.get("title") or _titleize(name)
    kind = console_ext.get("kind") or meta.get("kind", "solo")
    group = console_ext.get("group") or meta.get("group")
    context = _as_list(console_ext.get("context") or meta.get("context"))
    sources = _as_list(console_ext.get("sources") or meta.get("sources"))
    members = _as_list(console_ext.get("members") or meta.get("members"))
    moderator = (
        console_ext.get("moderator") or meta.get("moderator") or "round-robin"
    )

    # Canonical-role grounding (opt-in, three-tier mode).
    canonical_roles = console_ext.get("canonical_roles")
    if canonical_roles is not None and not isinstance(canonical_roles, dict):
        raise ValueError(f"console.canonical_roles must be a dict, got {type(canonical_roles).__name__}")
    researcher = None
    if isinstance(canonical_roles, dict):
        tier_3 = canonical_roles.get("tier_3") or {}
        if isinstance(tier_3, dict):
            researcher = tier_3.get("researcher")

    return DomainAgent(
        name=name,
        title=title,
        description=description,
        kind=kind,
        model=model,
        context=context,
        sources=sources,
        system_prompt=body.strip(),
        members=members,
        moderator=moderator,
        path=path,
        group=group,
        tools=tools,
        canonical_roles=canonical_roles,
        researcher=researcher,
    )


def apply_overlay(agent: DomainAgent, overlay: dict | None) -> DomainAgent:
    """Merge a project.yml overlay entry into an agent.

    overlay shape: {"add": [glob, ...], "exclude": [glob, ...]}
    Adds are appended to sources (deduped, order preserved). Excludes are
    stored on the agent for downstream filtering at file-resolution time.
    """
    if not overlay:
        return agent
    add = _as_list(overlay.get("add"))
    exclude = _as_list(overlay.get("exclude"))

    seen = set(agent.sources)
    merged = list(agent.sources)
    for glob in add:
        if glob not in seen:
            merged.append(glob)
            seen.add(glob)

    return replace(agent, sources=merged, excludes=list(exclude))


def _load_project_overlays(project_yml_path: Path | None) -> tuple[dict, list[str] | None]:
    """Return (overlays_by_name, enabled_list_or_None)."""
    if project_yml_path is None or not project_yml_path.exists():
        return {}, None
    try:
        data = yaml.safe_load(project_yml_path.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}, None
    advisors = data.get("advisors") or {}
    overlays = advisors.get("overlays") or {}
    enabled = advisors.get("enabled")
    if enabled is not None:
        enabled = list(enabled)
    return overlays if isinstance(overlays, dict) else {}, enabled


def _iter_agent_files(agents_dir: Path) -> Iterable[Path]:
    """Yield agent files from a flat `.claude/agents/` dir (preferred) or a
    legacy nested `<group>/*.md` layout (fallback)."""
    if not agents_dir.exists():
        return
    for path in sorted(agents_dir.glob("*.md")):
        if path.name.startswith("_"):
            continue
        yield path
    for sub in sorted(agents_dir.iterdir()):
        if not sub.is_dir() or sub.name.startswith("."):
            continue
        for path in sorted(sub.glob("*.md")):
            if path.name == "_group.md" or path.name.startswith("_"):
                continue
            yield path


def load_all(
    agents_dir: Path,
    project_yml_path: Path | None = None,
) -> tuple[dict[str, DomainAgent], list[Group]]:
    """Load every agent in `agents_dir`, apply project overlays, assemble groups.

    Groups are built from the `console.group` field on each agent. Enabled
    filter from `project.yml` is applied — disabled agents are still loaded
    into the dict (so panel members can reference them) but are excluded from
    the groups list returned to the UI.
    """
    overlays, enabled = _load_project_overlays(project_yml_path)

    agents: dict[str, DomainAgent] = {}
    for path in _iter_agent_files(agents_dir):
        try:
            agent = load_agent_file(path)
        except Exception:
            continue
        overlay = overlays.get(agent.name)
        if overlay:
            agent = apply_overlay(agent, overlay)
        # If group was not in frontmatter, derive from parent dir name (legacy)
        if agent.group is None and path.parent != agents_dir:
            agent = replace(agent, group=path.parent.name)
        agents[agent.name] = agent

    # Assemble groups from the group field
    groups_by_name: dict[str, list[DomainAgent]] = {}
    for agent in agents.values():
        if agent.is_system:
            continue
        if enabled is not None and agent.name not in enabled:
            continue
        key = agent.group or "ungrouped"
        groups_by_name.setdefault(key, []).append(agent)

    groups: list[Group] = []
    for order, (gname, members) in enumerate(sorted(groups_by_name.items())):
        groups.append(
            Group(
                name=gname,
                title=_titleize(gname),
                description="",
                order=order,
                agents=sorted(members, key=lambda a: a.name),
            )
        )

    return agents, groups


def resolve_effective_sources(agent: DomainAgent) -> tuple[list[str], list[str]]:
    """Return (context_globs, source_globs) for an agent after overlay.

    Context globs are always-read foundational docs. Source globs are
    triaged per-question. Excludes are not applied here — they're applied
    by the file resolver when walking matches.
    """
    return list(agent.context), list(agent.sources)
