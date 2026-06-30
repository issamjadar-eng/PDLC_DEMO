from dataclasses import dataclass, field, replace
from pathlib import Path

import yaml


@dataclass(frozen=True)
class DomainAgent:
    name: str
    title: str
    description: str
    kind: str
    model: str | None
    sources: list[str]          # deprecated — see `core` (Phase 2 of task 099)
    core: list[str]             # Tier 2 grounding: paths, folders, or globs
    system_prompt: str
    members: list[str] = field(default_factory=list)
    moderator: str = "round-robin"
    path: Path | None = None
    group: str | None = None
    subagents: list[str] = field(default_factory=list)  # project subagents (.claude/agents/<name>.md) this agent may invoke via Task

    @property
    def is_panel(self) -> bool:
        return self.kind == "panel"

    @property
    def is_system(self) -> bool:
        return self.name.startswith("_")


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


def _parse_frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---"):
        raise ValueError("domain agent file must start with YAML frontmatter")
    _, frontmatter, body = text.split("---", 2)
    data = yaml.safe_load(frontmatter) or {}
    return data, body.lstrip("\n")


def load_from_file(path: Path) -> DomainAgent:
    meta, body = _parse_frontmatter(path.read_text(encoding="utf-8"))
    name = meta.get("name") or path.stem
    sources = list(meta.get("sources", []) or [])
    core = list(meta.get("core", []) or [])
    # Backwards compatibility: if an agent still uses the old `sources:`
    # glob list (pre task 099 Phase 2), treat it as a Tier 2 core list
    # so the agent keeps working with degraded behavior (cap-truncation
    # instead of tool-driven discovery) until it's migrated.
    if sources and not core:
        core = sources
    return DomainAgent(
        name=name,
        title=meta.get("title", name),
        description=meta.get("description", ""),
        kind=meta.get("kind", "solo"),
        model=meta.get("model"),
        sources=sources,
        core=core,
        system_prompt=body.strip(),
        members=list(meta.get("members", []) or []),
        moderator=meta.get("moderator", "round-robin"),
        path=path,
        subagents=list(meta.get("subagents", []) or []),
    )


def _load_group_meta(group_dir: Path) -> dict:
    meta_path = group_dir / "_group.md"
    if not meta_path.exists():
        return {}
    try:
        meta, _ = _parse_frontmatter(meta_path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return meta if isinstance(meta, dict) else {}


def _titleize(name: str) -> str:
    return " ".join(p.capitalize() for p in name.replace("_", "-").split("-"))


def load_all(directory: Path) -> tuple[dict[str, DomainAgent], list[Group]]:
    agents: dict[str, DomainAgent] = {}
    groups: list[Group] = []
    if not directory.exists():
        return agents, groups

    for group_dir in sorted(directory.iterdir()):
        if not group_dir.is_dir() or group_dir.name.startswith("."):
            continue
        group_meta = _load_group_meta(group_dir)
        group_agents: list[DomainAgent] = []
        for path in sorted(group_dir.glob("*.md")):
            if path.name == "_group.md":
                continue
            agent = replace(load_from_file(path), group=group_dir.name)
            agents[agent.name] = agent
            if not agent.is_system:
                group_agents.append(agent)
        if not group_agents and not group_meta:
            continue
        groups.append(
            Group(
                name=group_dir.name,
                title=group_meta.get("title") or _titleize(group_dir.name),
                description=group_meta.get("description", ""),
                order=int(group_meta.get("order", 100)),
                agents=group_agents,
            )
        )
    groups.sort(key=lambda g: (g.order, g.title))
    return agents, groups
