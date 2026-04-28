# Action: `init`

Scaffold `docs/project/dhf-manifest/` in the project and confirm the `scope:` block in `project.yml`.

## Steps

1. **Verify `project.yml` has `scope:` block** — read `project.yml`. If `scope:` is absent, add the 9 standard flags with example defaults (hardware: false, cloud_hosted: true, tool_validation: true, multi_function_device: false, ota_updates: true, usability_hf: true, clinical_evaluation: literature, interoperability: true, geography: [us]). If present, confirm all 9 keys exist; add any missing with a `# TODO` comment.

2. **Scaffold `docs/project/dhf-manifest/` (flat layout)** — create the directory if not present, with only a `README.md` at its root. No subfolders; all manifest files (`qms-manifest.{md,json}`, `hiplink-manifest.{md,json}`, `hiplink-by-section.md`, `hiplink-dashboard.md`) sit flat under the root and are produced by subsequent build actions.

3. **Stub `qms-manifest.md`** — if the file is not present, write a starter with the top-level H1 + intro and no `<!-- QMS-DATA -->` blocks. Authors populate sections via `/dhf-manifest distill-qms` or by hand.

4. **Report** — list what was created vs. what already existed.

## Layout produced

```
docs/project/dhf-manifest/
├── README.md
└── qms-manifest.md          # starter stub, populated later
```

All other files are written by `/dhf-manifest build-qms`, `build-manifest`, and `dashboard`.

## 16 DHF topics (referenced by records in `qms-manifest.md`)

`architecture` `requirements` `design-outputs` `traceability` `risk-management` `verification` `validation` `software-lifecycle` `configuration-change` `design-reviews` `labeling-ifu` `human-factors` `cybersecurity` `clinical` `post-market` `regulatory-submission`
