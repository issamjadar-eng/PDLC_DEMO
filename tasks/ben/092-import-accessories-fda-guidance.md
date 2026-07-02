# 092 — Import Accessories FDA Guidance Into medtech-docs References

**ID**: 092
**Created**: 2026-06-22
**Status**: Complete
**Created By**: Ben Xavier
**Owner**: Ben Xavier
**Priority**: Medium

---

## PERMANENT RULES (do not remove)

This task document is the **session-recovery point** for this work. If the current session drops, is compacted, or ends, the next session must be able to load **this file alone** and continue where we left off. That is only possible if the doc is kept current in-flight.

1. **Update at every meaningful checkpoint (HARD RULE).** After each meaningful unit of work, update this task doc: tick the relevant Todo, add a dated Changelog line naming the concrete artifact, update progress counts.
2. **Phase-end batching is OK; drift-batching is not.**
3. **A commit is not a substitute.** Git records code; this doc records the narrative.
4. **Resume-ready before any session boundary.**
5. **Capture strategy + lessons as they happen.**

## Goals

Import the new FDA guidance **"Medical Device Accessories — Describing Accessories and Classification Pathways"** into the medtech-docs reference library (`.claude/skills/medtech-docs/references/fda-guidance/`) following the folder's three-artifact convention:

1. **Original archive** — PDF moved to `source/accessories.pdf` (byte-correct archive, not indexed).
2. **Faithful full text** — `source-md/accessories.md` (authoritative grounding + citation source; must be **source-equivalent**).
3. **Distilled finding aid** — `accessories-distilled.md` at the parent level, carrying the mandatory `🔎 Finding aid` banner + metadata header + scope + clause-by-clause sections.

Verify the work with subagents (source-equivalence of the source-md; convention/quality of the distilled).

## Todos

- [x] Move PDF → `source/accessories.pdf` (was untracked; plain `mv`)
- [x] Produce `source-md/accessories.md` (faithful full text — `pdftotext -layout`, byte-identical to extraction; 788 lines / 48122 bytes)
- [ ] Verify source-md equivalence with a subagent (against the PDF)
- [x] Author `accessories-distilled.md` (banner + metadata + scope + clause sections + cross-refs + distiller notes)
- [x] Verify distilled quality/convention-conformance with a subagent → **CONFORMANT**, all claims grounded, all 6 cross-refs exist, no fabrication
- [x] Apply verifier fix (added "(if applicable)" to the De Novo→predicate claim for byte-fidelity)
- [x] Update fda-guidance README — added "Distilled Guidances" table row + changelog entry
- [x] Ran folder-prescribed checker `scripts/verify-conversion.py` → **PASS, 0 invented words**
- [x] Run applicability — added `accessories-distilled.md` rubric trigger row to `/medtech-docs update-external-references` (SKILL.md); copied → `docs/external/fda-guidance/accessories.md` (verbatim); updated project README Active-Guidances table + changelog. No Step-2.5 exclusion conflict.
- [x] Close task (this doc → Complete; index moved to Completed)
- [ ] Push to project repo (PR → merge to main) + skill repo (`/sync-skills push` for medtech-docs SKILL.md + references changes)

## Verification results (2026-06-22)

- **source-md equivalence** (subagent, general-purpose): VERDICT **SOURCE-EQUIVALENT**. Independent `pdftotext -layout` re-extraction is **byte-identical** (`diff` empty, both 788 lines). Visual read of all 17 PDF pages confirms no fabrication / no dropped sections / no garbling; all spot-checks pass (title block, dates, docket, TOC I–VII+App1, four §IV definitions, support/supplement/augment examples, 85-day & 120-day clocks, footnotes 1–18). Only benign artifacts (split URLs, a source-PDF double-period, a source-PDF-truncated URL) — all faithful to the original.
- **distilled quality** (subagent, general-purpose): VERDICT **CONFORMANT**. Mandatory `🔎` banner present as plain-bold paragraph (not blockquote); structure H1→banner→metadata→Scope→TOC→clause sections; every fact grounded (dates, identifiers, statutes, clocks, two-prong test, definitions, SaMD boundary, contingencies); all 6 companion cross-refs exist; no `[VERIFY]` needed; no fabrication.
- **folder checker** `verify-conversion.py`: PASS — worst invented run 0 words (threshold 40).

## Final artifacts

- `.../references/fda-guidance/source/accessories.pdf` (452 KB, byte archive)
- `.../references/fda-guidance/source-md/accessories.md` (48122 B / 788 lines, faithful full text)
- `.../references/fda-guidance/accessories-distilled.md` (finding aid)
- `.../references/fda-guidance/README.md` (table row + changelog)

## Notes / Conventions confirmed

- references/fda-guidance three-artifact convention: `source/<base>.pdf` (byte archive, not indexed) · `source-md/<base>.md` (faithful full text = authoritative grounding+citation, raw `pdftotext -layout`, no added frontmatter) · `<base>-distilled.md` at parent (finding aid; MANDATORY `🔎 **Finding aid — NOT the authoritative source.**` plain-bold banner under H1).
- Base name chosen: `accessories` (matches short-kebab convention of siblings: mdds, mfd, cds…).
- Guidance facts: issued **Dec 20, 2017** (orig Dec 30, 2016); docket **FDA-2015-D-0025**; CDRH doc **1770**; OMB **0910-0823**; key statute **FDARA 2017** amending FD&C Act §513(f) — classify accessory on its OWN risk, notwithstanding parent class.

## Changelog

- 2026-06-22: Task created. Read medtech-docs + docflow SKILL.md and the references/README.md conventions; confirmed the three-artifact convention (source/ PDF, source-md/ faithful full text, parent-level distilled finding aid).
- 2026-06-22: Moved PDF → `source/accessories.pdf`; produced `source-md/accessories.md` (raw `pdftotext -layout` under docflow bypass marker, byte-identical to extraction); authored `accessories-distilled.md`. Two subagents verified (SOURCE-EQUIVALENT + CONFORMANT); applied one byte-fidelity nit; ran `verify-conversion.py` (PASS, 0 invented words). Added references README table row + changelog.
- 2026-06-22: Ran applicability — added accessories rubric trigger to `update-external-references` (SKILL.md); copied distilled → `docs/external/fda-guidance/accessories.md`; updated project applicability README. Marked task **Complete**. Next: push to project repo (PR→merge) + skill repo (sync-skills push).

