"""
Resolve per-DHF Jira + evidence config from project.yml.

Project-agnostic: this module knows nothing about specific projects, prefix
conventions, or Jira sites. It reads the standard project.yml shape:

  change_control.jira:
    cloud_id, base_url, project_keys, field_set, cache.{root, max_age_hours}

  dhfs[].architecture_name           # output folder name (lowercased-hyphenated)
  dhfs[].marketed_name
  dhfs[].jira:
    project_key
    versions[]: {id, fix_version, fix_version_id}
    story_filter: {labels, statuses}     # optional
  dhfs[].evidence.design_traceability_matrix[]:
    version, xlsx, sheet, header_row, data_start_row, columns{}, extractors{}, tbd_value
    empty_means_unknown                  # optional
  dhfs[].evidence.hazard_traceability_matrix (optional)

  jira_pull:                             # optional, all fields optional
    exempt_filters[]
    severity_overrides{}
    di_resolution.fallback[]
    layers_present[] | per-DHF override
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


@dataclass(frozen=True)
class JiraSiteConfig:
    cloud_id: str
    base_url: str
    project_keys: List[str]
    field_set_common: List[str]
    mirror_root: str          # committed mirror snapshots root (e.g. docs/project/_jira)
    cache_root: str           # transient staging root (e.g. docs/project/_jira/_cache)
    cache_max_age_hours: int


@dataclass(frozen=True)
class JiraVersion:
    id: str
    fix_version: str
    fix_version_id: str


@dataclass(frozen=True)
class StoryFilter:
    labels: List[str] = field(default_factory=list)
    statuses: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class DhfJiraConfig:
    project_key: str
    versions: List[JiraVersion]
    story_filter: StoryFilter
    layers_present: List[str]


@dataclass(frozen=True)
class DtmSchema:
    version: str
    xlsx_path: str
    sheet: str
    header_row: int
    data_start_row: int
    columns: Dict[str, str]
    extractors: Dict[str, str]
    tbd_value: str
    empty_means_unknown: bool
    provenance: Dict[str, Any]


@dataclass(frozen=True)
class HtmSchema:
    version: str
    xlsx_path: str
    sheet: str
    header_row: int
    data_start_row: int
    columns: Dict[str, str]
    extractors: Dict[str, str]
    tbd_value: str
    provenance: Dict[str, Any]


@dataclass(frozen=True)
class DhfConfig:
    leaf: str
    architecture_name: str
    marketed_name: str
    role: str
    arch_slug: str                       # architecture_name lowercased-hyphenated, used as folder name
    jira: Optional[DhfJiraConfig]
    dtm_schemas: List[DtmSchema]
    htm_schemas: List[HtmSchema]


@dataclass(frozen=True)
class JiraPullTuning:
    exempt_filters: List[Dict[str, Any]]
    severity_overrides: Dict[str, str]
    di_resolution_fallback: List[str]
    design_input_label: Optional[str]


@dataclass(frozen=True)
class ResolvedConfig:
    project_root: Path
    site: JiraSiteConfig
    dhfs: List[DhfConfig]
    tuning: JiraPullTuning


_DEFAULT_LAYERS = ["Epic", "Story", "Hazard", "Test Execution"]
_DEFAULT_FIELDS = ["summary", "description", "status", "priority", "issuetype",
                   "labels", "components", "fixVersions", "parent", "issuelinks",
                   "assignee", "reporter", "resolution", "duedate",
                   "created", "updated"]


def _slug(name: str) -> str:
    """Architecture name to folder slug — lowercase, spaces/underscores -> hyphens."""
    return "-".join(name.lower().replace("_", " ").split())


def _resolve_dtm_schemas(dhf_block: Dict[str, Any]) -> List[DtmSchema]:
    schemas = []
    evidence = dhf_block.get("evidence") or {}
    for entry in evidence.get("design_traceability_matrix") or []:
        if not entry.get("columns"):
            # Schema map not yet declared (e.g., a DHF whose DTM hasn't been probed); skip.
            continue
        provenance_keys = ("form_id", "form_rev", "mpi", "dhf_id", "doc_rev",
                           "owned_by", "status")
        schemas.append(DtmSchema(
            version=entry["version"],
            xlsx_path=entry["xlsx"],
            sheet=entry["sheet"],
            header_row=int(entry["header_row"]),
            data_start_row=int(entry.get("data_start_row", entry["header_row"] + 1)),
            columns=dict(entry["columns"]),
            extractors=dict(entry.get("extractors") or {}),
            tbd_value=str(entry.get("tbd_value", "TBD")),
            empty_means_unknown=bool(entry.get("empty_means_unknown", False)),
            provenance={k: entry[k] for k in provenance_keys if k in entry},
        ))
    return schemas


def _resolve_htm_schemas(dhf_block: Dict[str, Any]) -> List[HtmSchema]:
    schemas: List[HtmSchema] = []
    evidence = dhf_block.get("evidence") or {}
    for entry in evidence.get("hazard_traceability_matrix") or []:
        if not entry.get("columns"):
            continue
        provenance_keys = ("form_id", "form_rev", "mpi", "dhf_id", "doc_rev",
                           "owned_by", "status")
        schemas.append(HtmSchema(
            version=entry["version"],
            xlsx_path=entry["xlsx"],
            sheet=entry["sheet"],
            header_row=int(entry["header_row"]),
            data_start_row=int(entry.get("data_start_row", entry["header_row"] + 1)),
            columns=dict(entry["columns"]),
            extractors=dict(entry.get("extractors") or {}),
            tbd_value=str(entry.get("tbd_value", "TBD")),
            provenance={k: entry[k] for k in provenance_keys if k in entry},
        ))
    return schemas


def _resolve_jira(dhf_block: Dict[str, Any], default_layers: List[str]) -> Optional[DhfJiraConfig]:
    jb = dhf_block.get("jira")
    if not jb:
        return None
    versions = [
        JiraVersion(id=v["id"], fix_version=v["fix_version"],
                    fix_version_id=str(v["fix_version_id"]))
        for v in jb.get("versions") or []
    ]
    sf = jb.get("story_filter") or {}
    layers = jb.get("layers_present") or default_layers
    return DhfJiraConfig(
        project_key=jb["project_key"],
        versions=versions,
        story_filter=StoryFilter(
            labels=list(sf.get("labels") or []),
            statuses=list(sf.get("statuses") or []),
        ),
        layers_present=list(layers),
    )


def load(project_root: Optional[Path] = None) -> ResolvedConfig:
    """Load and validate project.yml from `project_root` (defaults to cwd)."""
    project_root = (project_root or Path.cwd()).resolve()
    raw = yaml.safe_load((project_root / "project.yml").read_text())

    cc_jira = (raw.get("change_control") or {}).get("jira") or {}
    site = JiraSiteConfig(
        cloud_id=str((raw["change_control"]).get("cloud_id", "")),
        base_url=str((raw["change_control"]).get("base_url", "")),
        project_keys=list(cc_jira.get("project_keys") or []),
        field_set_common=list((cc_jira.get("field_set") or {}).get("common") or _DEFAULT_FIELDS),
        mirror_root=str(cc_jira.get("mirror_root", "docs/project/_jira")),
        cache_root=str((cc_jira.get("cache") or {}).get("root", "docs/project/_jira/_cache")),
        cache_max_age_hours=int((cc_jira.get("cache") or {}).get("max_age_hours", 24)),
    )

    tuning_block = raw.get("jira_pull") or {}
    tuning = JiraPullTuning(
        exempt_filters=list(tuning_block.get("exempt_filters") or []),
        severity_overrides=dict(tuning_block.get("severity_overrides") or {}),
        di_resolution_fallback=list(((tuning_block.get("di_resolution") or {}).get("fallback")) or []),
        design_input_label=tuning_block.get("design_input_label"),
    )
    default_layers = list(tuning_block.get("layers_present") or _DEFAULT_LAYERS)

    dhfs = []
    for d in raw.get("dhfs") or []:
        arch = d.get("architecture_name") or d["leaf"]
        # Allow project.yml to override the folder slug — useful when the
        # canonical architecture name is verbose (e.g. "Management Services"
        # but the project folder convention is the shorter "mgmt-services").
        slug = d.get("arch_slug") or _slug(arch)
        dhfs.append(DhfConfig(
            leaf=d["leaf"],
            architecture_name=arch,
            marketed_name=d.get("marketed_name") or arch,
            role=d.get("role") or "item",
            arch_slug=slug,
            jira=_resolve_jira(d, default_layers),
            dtm_schemas=_resolve_dtm_schemas(d),
            htm_schemas=_resolve_htm_schemas(d),
        ))

    return ResolvedConfig(project_root=project_root, site=site, dhfs=dhfs, tuning=tuning)


def find_dhf(cfg: ResolvedConfig, leaf: str) -> DhfConfig:
    for d in cfg.dhfs:
        if d.leaf == leaf:
            return d
    raise KeyError(f"DHF leaf {leaf!r} not in project.yml; known: {[d.leaf for d in cfg.dhfs]}")


def find_version(dhf: DhfConfig, version_id: str) -> JiraVersion:
    if not dhf.jira:
        raise KeyError(f"DHF {dhf.leaf!r} has no jira block")
    for v in dhf.jira.versions:
        if v.id == version_id:
            return v
    raise KeyError(f"Version {version_id!r} not in {dhf.leaf!r} jira.versions; known: {[v.id for v in dhf.jira.versions]}")


def find_dtm_schema(dhf: DhfConfig, version_id: str) -> Optional[DtmSchema]:
    for s in dhf.dtm_schemas:
        if s.version == version_id:
            return s
    return None


def find_htm_schema(dhf: DhfConfig, version_id: str) -> Optional[HtmSchema]:
    for s in dhf.htm_schemas:
        if s.version == version_id:
            return s
    return None
