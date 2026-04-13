from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import yaml


@dataclass(frozen=True)
class Config:
    repo_root: Path
    console_root: Path
    domain_agents_dir: Path
    data_dir: Path
    project: dict

    @property
    def project_name(self) -> str:
        return self.project.get("name", "PDLC Project")

    @property
    def device(self) -> str:
        return self.project.get("device_family") or self.project.get("device", "")

    @property
    def regulatory_pathway(self) -> str:
        return self.project.get("regulatory_pathway", "")


@lru_cache(maxsize=1)
def get_config() -> Config:
    console_root = Path(__file__).resolve().parent.parent
    repo_root = console_root.parent.parent
    project_yml = repo_root / "project.yml"
    if not project_yml.exists():
        raise RuntimeError(f"project.yml not found at {project_yml}")
    data = yaml.safe_load(project_yml.read_text()) or {}
    return Config(
        repo_root=repo_root,
        console_root=console_root,
        domain_agents_dir=console_root / "domain_agents",
        data_dir=console_root / "data",
        project=data.get("project", {}),
    )
