# Labeling — pca-device

> _Demo sample data — not for clinical use._

Device labeling artifacts for the PainEase PCA Advanced (PP3500) per 21 CFR 801. Includes Instructions for Use (IFU), device markings, packaging artwork, symbols reference, and regional labeling variants.

## Expected Content

- `ifu.md` — Instructions for Use (source-of-truth markdown; authoring form)
- `device-markings.md` — what appears on the device itself (silkscreen, UDI, classification marks)
- `packaging-artwork.md` — outer and inner carton artwork and required content
- `symbols.md` — IEC 60601-1 + ISO 15223-1 symbols applied with rationale
- `regional/` — per-jurisdiction labeling variants (US, EU, CA, etc.) when applicable
- `formal/` — controlled deliverables for submission

## Conventions

- **Naming**: kebab-case filenames. Controlled artwork (PDF/AI) in `formal/` with version control.
- Every labeling claim cross-references the User Need / Design Input that supports it — no unsupported claims.
- UDI and classification marks are traceable to the device master record; any change triggers a labeling review.
- Linked to: 21 CFR 801, ISO 15223-1, IEC 60601-1 marking requirements.

## Changelog

| Date | Author | Summary |
|------|--------|---------|
| 2026-04-20 | Ben Xavier | Stub folder — created under task 018 so the 510(k) composition manifest's Labeling piece resolves. Awaiting content. |
