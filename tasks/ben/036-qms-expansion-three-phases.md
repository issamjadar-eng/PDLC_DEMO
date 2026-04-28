# 036 — QMS Expansion: Three-Phase Internal Source-MD Buildout

**ID**: 036
**Created**: 2026-04-27
**Status**: Complete
**Created By**: Ben Xavier
**Owner**: Ben Xavier
**Priority**: Medium

---

## PERMANENT RULES (do not remove)

This task document is the **session-recovery point** for this work.

1. Update at every meaningful checkpoint (HARD RULE).
2. Phase-end batching is OK; drift-batching is not.
3. A commit is not a substitute.
4. Resume-ready before any session boundary.
5. Capture strategy + lessons as they happen.

## Goals

Round out PDLC_DEMO's GlobalLogic QMS scaffold under `docs/internal/source-md/` from 55 docs (post-ben/022) → ~67 docs by adding 12 representative governance artifacts that fill topical gaps surfaced by comparing PDLC's QMS to a real medtech QMS (using arthrex-pccp as inspiration only — zero content copied).

After the new docs land, extend `docs/project/dhf-manifest/qms-manifest.md` with QMS records that cite the new procedures, then rerun the `/dhf-manifest` pipeline so the manifest's QMS-grounding column reflects the broader corpus.

## Anonymization commitment

- Authored from scratch using public ISO 13485 / ISO 14971 / IEC 62304 / IEC 81001-5-1 / FDA guidance language already in `docs/external/standards/` and `.claude/skills/dhf-manifest/data/`.
- Internal QMS docs legitimately name `GlobalLogic` as the QMS-owning organization — `docs/internal/source-md/` is project-local and was explicitly excluded from the ben/032 skill-tree anonymization scope. New docs follow the existing `GL-<TYPE>-<CATEGORY>-NNN` pattern and credit GlobalLogic as owner.
- Zero copying of arthrex/Arthrex content (logs, customer names, project names, identifying language) per user direction.

## ID assignment plan

`GL-<TYPE>-<CATEGORY>-NNN` where new type `STD` = standard.

| New ID | Doc | Phase |
|---|---|---|
| GL-STD-RM-001 | Risk Assessment Criteria (severity × probability scales + acceptance matrix) | 1 |
| GL-STD-RM-002 | Master Harms List | 1 |
| GL-FORM-DC-002 | Phase-Gate Review Checklist (one form covering all gates) | 1 |
| GL-SOP-QM-006 | Good Documentation Practices | 1 |
| GL-WI-QM-001 | Deviation Procedure | 1 |
| GL-WI-DC-001 | Design History File Process | 2 |
| GL-WI-DC-002 | Design Traceability Matrix | 2 |
| GL-WI-SW-003 | Threat Modeling | 2 |
| GL-WI-SW-004 | Software Verification and Validation | 2 |
| GL-SOP-RA-001 | Regulatory Operations | 3 |
| GL-WI-RA-001 | 510(k) Submission Process | 3 |
| (folder) `regulatory-affairs/` + README.md | Folder scaffold for new QMS category | 3 |

## Todos

- [x] Phase 1 — authored 5 docs: GL-STD-RM-001 (Risk Assessment Criteria), GL-STD-RM-002 (Master Harms List), GL-FORM-DC-002 (Phase-Gate Checklist), GL-SOP-QM-006 (Good Documentation Practices), GL-WI-QM-001 (Deviation Procedure).
- [x] Phase 2 — authored 4 docs: GL-WI-DC-001 (DHF Process), GL-WI-DC-002 (Trace Matrix), GL-WI-SW-003 (Threat Modeling), GL-WI-SW-004 (Software V&V).
- [x] Phase 3 — authored 3 docs + new folder: regulatory-affairs/README.md, GL-SOP-RA-001 (Regulatory Operations), GL-WI-RA-001 (510(k) Submission Process).
- [x] Updated `qms-index.md` with all 12 new entries; bumped to Rev 1.1; added changelog row. New `Standards` doc-class introduced. New `Regulatory Affairs` top-level category added to §2.
- [x] Added 6 new QMS records to `qms-manifest.md` citing the new procedures: QMS-ARCH-003 (DHF process), QMS-TRC-001 (trace matrix), QMS-CYB-001 (threat modeling), QMS-VER-002 (software V&V), QMS-RS-001 (regulatory operations), QMS-RS-002 (510(k) submission).
- [x] Reran `/dhf-manifest build-qms` → `build-manifest` → `dashboard` → `validate`. **Direct-QMS hits: 92/437 → 120/437 (21.1% → 27.5%)**; no-grounding cells: 61 → 39. Validate 12/12 PASS.
- [x] Commit + push pending.

## Notes

- These docs are **demo content**, not real QMS evidence. The `_Demo sample data — not for clinical use._` banner stays applicable at the top of each doc.
- Doc length target: ~80–150 lines each. Representative shape and substance, not exhaustive.

## Changelog

- 2026-04-27: Task created. User asked for a more representative QMS using arthrex-pccp for inspiration only (no content copying). Three-phase plan covers the most-cited gaps: risk standards (criteria + harms list), phase-gate checklists, document-practices SOP + deviation WI, DHF process + trace-matrix WIs, cybersecurity threat-modeling + software V&V WIs, and a new regulatory-affairs folder with operations SOP + 510(k) submission WI.
- 2026-04-27: All three phases complete. 12 new docs authored (Phase 1: 5 docs, Phase 2: 4 docs, Phase 3: 3 docs + new `regulatory-affairs/` folder). qms-index.md bumped to Rev 1.1 with new `Standards` doc-class and new `Regulatory Affairs` category. qms-manifest.md gained 6 new records grounding the new procedures. dhf-manifest pipeline reran clean: 17 QMS obligations across 13 topics, 27 regulatory refs across 20 OBL targets. **Direct-QMS hits jumped 92/437 → 120/437 (27.5%)**; no-grounding dropped 61 → 39. Validate 12/12 PASS. Task closed.
