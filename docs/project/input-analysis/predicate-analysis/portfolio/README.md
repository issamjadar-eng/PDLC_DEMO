# Predicate Analysis — Portfolio Devices

> _Demo sample data — not for clinical use._

Regulatory and device-master records for the released infusion portfolio (IP5000, PP3000, PP3500, SP6000, SP6500). These devices are retained as **predicate reference and portfolio context** for the PP3500 510(k) submission under K210345.

## Expected Content

- Per-device regulatory records (`DEV-<CODE>_regulatory_info.md`) — K-number, indications, device classification, applicable standards, known predicate chain
- Device master catalog (`device_master_catalog.md`) — cross-reference table spanning all portfolio devices
- Supporting assets (510(k) summaries, clearance letters) referenced from the regulatory records

## Conventions

- **Naming**: `DEV-<CODE>_regulatory_info.md` for per-device files (kebab-case code). The master catalog is `device_master_catalog.md`.
- Each `DEV-*_regulatory_info.md` carries a `device_code`, `k_number`, `predicate_chain`, and `clearance_date` in frontmatter — used by the `/trace-matrix` and `/tracker` skills.
- PP3500 is the **anchor device** for this project's DHF. Predicate devices (PP3000, etc.) feed the 510(k) substantial-equivalence narrative.
- Link any mentions of external FDA documents to the distilled markdown under `docs/external/fda-guidance/` rather than pasting verbatim text.

## Changelog

| Date | Author | Summary |
|------|--------|---------|
| 2026-04-20 | Ben Xavier | Initial version — created under task 018 to satisfy medtech-docs v17 README-every-docs-folder check. |
