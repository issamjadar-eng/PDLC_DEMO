# Glossary

Shared terminology used across the PDLC_DEMO project. The definitions here are the working meanings — if a standard or regulation uses a term differently, the authoritative source (FDA guidance, ISO standard, etc.) wins and should be linked from the entry.

## Conventions

- Alphabetical by term.
- One-line definition first; optional note or reference line second.
- Add entries when a term shows up in a task, strategy doc, or deliverable and isn't yet listed. Prefer expanding acronyms at first use in the source doc and linking back here, rather than repeating definitions everywhere.

## Terms

- **CAPA** — Corrective And Preventive Action. The quality-system loop for investigating a nonconformance, correcting it, and preventing recurrence. See `docs/project/postmarket/capa/`.
- **DHF** — Design History File. The record of design activity for a device; required by 21 CFR 820.30(j). In this project every top-level DHF (pca-device, connectivity-adapter, cloud-suite) lives under `docs/project/dhfs/<name>/`. Nested DHFs (e.g., `cloud-suite/dhfs/drug-library-manager/`) follow the same shape.
- **DI** — Design Input. A requirement the device must meet. Traces up to one or more User Needs and down to Architecture elements + V&V.
- **FDA** — U.S. Food and Drug Administration. Primary regulator for PP3500 via the 510(k) pathway.
- **K-number** — FDA-assigned clearance number for a 510(k) submission. PP3500 is anchored on placeholder K210345; predicate PP3000 is K190567.
- **KOL** — Key Opinion Leader. Clinical voice used as a persona in the project-console chat sidebar. KOL personas are project-specific and live under `tools/project-console/agents/kol/`; they are not shipped with the project-console skill.
- **PCA** — Patient-Controlled Analgesia. The class of infusion device the lead product (PP3500) belongs to.
- **PCCP** — Predetermined Change Control Plan. FDA mechanism for pre-authorized post-market changes to a cleared device (especially SaMD) without re-filing. Referenced throughout the regulatory strategy.
- **PP3500** — PainEase PCA Advanced (model PP3500), the lead device of the demo project. Anchors the DHF and the 510(k) filing strategy.
- **Predicate** — A legally marketed device used to support a 510(k) substantial-equivalence claim. PP3500's predicate is PP3000 (K190567).
- **SaMD** — Software as a Medical Device. Software intended to perform a medical function without being part of a hardware medical device. Example in this project: the drug-library-manager under `cloud-suite/dhfs/drug-library-manager/`.
- **SiMD** — Software in a Medical Device. Embedded pump firmware on the pca-device DHF — medical-device software that runs on dedicated hardware, treated as a software item under IEC 62304 but not separately marketable.
- **UN** — User Need. A need from the clinical/operational environment that the device must serve. Traces down to Design Inputs.
- **V&V** — Verification and Validation. Verification shows the device meets its Design Inputs; validation shows it meets its User Needs in the intended environment.

## Changelog

| Date | Author | Summary |
|------|--------|---------|
| 2026-04-20 | Ben Xavier | Initial stub — 14 core terms (DHF, SaMD, SiMD, PCA, PP3500, predicate, UN, DI, V&V, CAPA, PCCP, KOL, FDA, K-number). Closes task ben/010 audit finding #6 (`glossary.md` missing). |
