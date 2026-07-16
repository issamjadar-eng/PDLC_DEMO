"""Field-description catalog for the Setup → Project section.

The descriptions of `project.yml`'s configuration surface live HERE, in the
registry-shared skill — not per project — so every consuming project renders
the same explanations. A field the catalog doesn't know still renders (with
a "no description registered" note); that note is the signal to add the
field here so the whole registry benefits.

Two catalogs:

- `PROJECT_FIELDS` — the scalar identity/classification fields under the
  top-level `project:` block. These are the console-editable ones.
- `SECTIONS` — every known top-level `project.yml` section, each with a
  one-liner and where it's managed (a console section or an owning skill).
  Sections are read-only in the Project view: structured blocks have their
  own editors/owners.

Keep descriptions to one tight sentence — they render in row expansions.
"""
from __future__ import annotations

PROJECT_FIELDS: dict[str, str] = {
    "name": "Project identifier used across docs, dashboards, and tooling output.",
    "repo": "GitHub owner/repo of record — drives the access audit, registry operations, and PR links.",
    "type": "Project type; 'medtech' unlocks the medtech skill stack (the console refuses to run without it).",
    "regulatory_pathway": "FDA submission pathway the program targets (e.g. 510k, de-novo, pma).",
    "device_class": "FDA device classification (I, II, III) — drives documentation rigor expectations.",
    "device_family": "Short slug for the device family; used in classification prose and templates.",
    "lead_product": "The product the DHF anchors on — design controls, V&V, and submissions all reference it.",
    "portfolio_context": "Sibling products kept as portfolio/predicate context around the lead product.",
    "composition": "Device composition mix (e.g. samd, simd, hardware) — shapes which standards apply.",
    "capabilities": "Capability flags (AI/ML, EHR integration, …) that gate optional documentation and analyses.",
}

SECTIONS: dict[str, dict] = {
    "project": {
        "description": "Project identity and regulatory classification — the fields above.",
        "managed": "this section",
    },
    "scope": {
        "description": "Project scope vector — which regulatory/QMS obligation families apply; consumed by the DHF-manifest tooling.",
        "managed": "dhf-manifest skill",
    },
    "dhfs": {
        "description": "DHF roster — each entry is a Design History File with path, role, classification, and filing route.",
        "managed": "medtech-docs skill",
    },
    "team": {
        "description": "Team roster of record — active and inactive (offboarded) members.",
        "managed": "Setup → Team & Security",
    },
    "registries": {
        "description": "Approved skill registries — where skills are fetched from and audited against.",
        "managed": "Setup → Registries",
    },
    "security": {
        "description": "Security posture — approved email domains and the skill/MCP/plugin/agent allowlists the posture check audits.",
        "managed": "Setup → Skills/Agents/Plugins/Connectors",
    },
    "strategy_domains": {
        "description": "Strategy domain registry — the strategy documents the program maintains and what belongs in each.",
        "managed": "strategy skill",
    },
    "tracker": {
        "description": "Submission-tracker configuration — display labels and row-id schema for the readiness dashboard.",
        "managed": "tracker skill",
    },
    "advisors": {
        "description": "Enabled advisor personas (regulatory, clinical, quality, …) served in chat and panels.",
        "managed": "advisors skill",
    },
    "taxonomies": {
        "description": "Document-taxonomy roots — where .taxonomy.yml files govern regulated doctype mappings.",
        "managed": "medtech-docs skill",
    },
    "file_locator": {
        "description": "Semantic file-search corpus configuration — what the local search index includes and excludes.",
        "managed": "file-locator skill",
    },
    "usage_metrics": {
        "description": "Team token-usage telemetry configuration (collection and aggregation settings).",
        "managed": "usage-metrics skill",
    },
    "change_control": {
        "description": "Bridge configuration to regulated downstream systems (Confluence spaces, Jira, review tiers).",
        "managed": "change-control skill",
    },
}

UNKNOWN_FIELD_NOTE = (
    "No description registered for this field — add it to the project-console "
    "skill's project_meta.py catalog so every project gets the same explanation."
)
