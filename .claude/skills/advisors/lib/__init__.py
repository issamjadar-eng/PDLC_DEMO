"""Shared loader for the /advisors skill.

Consumed by the skill's own CLI actions and by project-console via a
symlink at tools/project-console/console/advisors_lib. Keep this module
dependency-light — stdlib plus PyYAML only.
"""

from .loader import (
    DomainAgent,
    Group,
    load_agent_file,
    load_all,
    apply_overlay,
    resolve_effective_sources,
)

__all__ = [
    "DomainAgent",
    "Group",
    "load_agent_file",
    "load_all",
    "apply_overlay",
    "resolve_effective_sources",
]
