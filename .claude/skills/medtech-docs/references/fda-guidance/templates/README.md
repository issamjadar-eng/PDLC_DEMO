# FDA Electronic Submission Templates (fillable PDF binaries)

Byte-correct archive of FDA's **fillable electronic-submission templates** — the eSTAR / PreSTAR dynamic PDF forms a submitter completes in Adobe Acrobat Pro and transmits via the CDRH Portal.

These are **not** grounding/citation text (that role belongs to the guidance triplet one level up: the distilled finding aid `../<name>-distilled.md`, the faithful full text `../source-md/<name>.md`, and the byte-correct guidance PDF `../source/<name>.pdf`). These template binaries are the **build targets** the eStar packaging tooling derives its section → attachment-slot / structured-field model from. Like `source/` originals, they are **excluded from semantic indexing** (a 5 MB dynamic form is not embeddable text).

## Contents

| File | Template | Version | Applies to | Notes |
|------|----------|---------|-----------|-------|
| `nIVD_eSTAR_7-0.pdf` | non-IVD eSTAR | v7.0 | 510(k) / De Novo / PMA content for **non-IVD** devices (incl. SaMD) | Released 2026-06-01; **mandatory 2026-08-03**. The build target for a non-IVD SaMD 510(k). |
| `IVD_eSTAR_7-0.pdf` | IVD eSTAR | v7.0 | In-vitro-diagnostic devices | Sibling reference; **not** the template for a non-IVD device. |
| `PreSTAR_3-0.pdf` | PreSTAR | v3.0 | Q-Submissions / Pre-Submissions | Companion to eSTAR v7.0; the Q-Sub electronic template (distinct workstream from the 510(k) eSTAR). |

## Version discipline

FDA revises these templates frequently (v5.5 Feb 2025 → v6.0 Oct 2025 → v6.1 Feb 2026 → **v7.0 Jun 2026, mandatory Aug 3 2026**). Field names, XFA node paths, and section layout shift between versions, so any derived section-map or fill dataset is **version-pinned**. When a newer version supersedes these, add the new binary here and re-derive; do not silently overwrite (keep the prior version for audit).

Download source: FDA eSTAR Program page — `https://www.fda.gov/medical-devices/how-study-and-market-your-device/estar-program`.

## Conventions

- **Project-agnostic** — these are FDA public templates; no project/device names appear here (registry-tracked skill rule).
- **Not indexed, not cited as text** — ground regulatory claims on the eSTAR *guidance* triplet, not on the template binary.
- **Format note** — eSTAR/PreSTAR are dynamic Adobe PDF forms (XFA + embedded JavaScript); their conditional logic and completeness self-check run only inside Acrobat Pro. Open-source PDF libraries cannot reliably read/fill them — see the eStar packaging tooling notes.

## Changelog

- 2026-07-01: Folder created. Archived nIVD/IVD eSTAR v7.0 + PreSTAR v3.0 (downloaded from the FDA eSTAR Program page).
