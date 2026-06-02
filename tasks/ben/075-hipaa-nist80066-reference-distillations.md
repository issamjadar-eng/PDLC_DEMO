# 075 — HIPAA + NIST SP 800-66 Reference Distillations

**ID**: 075
**Created**: 2026-06-02
**Status**: In Progress
**Created By**: Ben Xavier
**Owner**: Ben Xavier
**Priority**: Medium

---

## PERMANENT RULES (do not remove)

This task document is the **session-recovery point** for this work. If the current session drops, is compacted, or ends, the next session must be able to load **this file alone** and continue where we left off. That is only possible if the doc is kept current in-flight.

1. **Update at every meaningful checkpoint (HARD RULE).** After each meaningful unit of work — a converted/adopted doc, a committed change, a launched batch, a completed phase, a decision, a discovered blocker, a design pivot — update this task doc:
   - tick the relevant Todo checkbox
   - add a dated Changelog line naming the concrete artifact (commit SHA, file path, decision, blocker)
   - update any progress counts/tables in Goals
2. **Phase-end batching is OK; drift-batching is not.**
3. **A commit is not a substitute.** Git history records code; this doc records the project narrative.
4. **Resume-ready before any session boundary.**
5. **Capture strategy + lessons as they happen.**

Success test for this doc: a fresh Claude session, given only this file, can re-enter the work without asking the user "what were we doing?"

## Goals

_Close the privacy/data-protection gap in the `medtech-docs` skill reference library._

The skill currently has **no HIPAA or GDPR references** (confirmed by grep — only incidental PHI/PII mentions inside OWASP, IEC 81001-5-1, and the AI-DSF guidance). For a connected PCA pump (PP3500) that handles ePHI through its SaMD/telemetry path, the HIPAA Security Rule is load-bearing and currently absent.

User chose **Option A**: scaffold the two "pull now" HIPAA-tier references into the **skill's registry library** (`.claude/skills/medtech-docs/references/`), not the project's `docs/external/`. GDPR deferred until an EU market path is real.

**Deliverables (2):**
1. `references/regulations/45-cfr-part-164.md` — HIPAA Security Rule (Subpart C §§164.302–318) as the anchor, with Breach Notification (Subpart D) + Privacy (Subpart E) noted/pointered. Federal reg → `regulations/` folder, `NN-cfr-part-NNN.md` convention, verbatim text from eCFR Title 45 public API.
2. `references/industry-frameworks/nist-sp-800-66.md` — NIST SP 800-66 Rev. 2 (Feb 2024) implementation guide / Security-Rule→CSF/800-53 crosswalk. Implementation guide → `industry-frameworks/` folder (next to `nist-csf.md`), NOT `regulations/`.

Plus README index updates for both folders + changelogs.

## Grounding established (this session)

- Read `references/regulations/README.md` + `21-cfr-part-880.md` → confirmed the regulations distillation format (citation block → scope → section index → verbatim blockquotes with eCFR footnote → distilled "why this matters" notes → Source Provenance → trailing `[VERIFY]`).
- Read `SKILL.md` import path → the `references/` library is **hand-authored, read-only registry content** (`update-external-references` only *copies* applicable bundled files into a project's `docs/external/`; it never fetches/distills). So new references are authored directly the way the 21 CFR files were. **No skill action to invoke** — direct authoring is correct.
- Confirmed the two docs split across two folders (reg vs implementation guide) per each README's own scope rules.

<!-- STRATEGY CONTENT: regulatory, privacy/data-protection coverage -->
HIPAA Security Rule (45 CFR 164 Subpart C) is the load-bearing privacy reg for a connected ePHI-handling device, more so than the Privacy Rule (Subpart E) which governs covered-entity practices. NIST SP 800-66 Rev. 2 is the highest-value companion because it crosswalks the Security Rule onto NIST CSF / 800-53 controls the project already touches for FDA premarket cybersecurity — one control catalog, two regulatory drivers. GDPR deferred: no point distilling EU data-protection law with no EU filing intent. The 2025 HHS Security Rule NPRM (Fed. Reg. Jan 6 2025) is pulled as forward-looking only, clearly marked not-yet-final.
<!-- /STRATEGY CONTENT -->

## Todos

- [x] Fetch verbatim 45 CFR 164 Subpart C text from eCFR Title 45 public API (eCFR latest issue 2026-05-29; got §§164.302–318 + Appendix A, 37 KB)
- [x] Author `references/regulations/45-cfr-part-164.md`
- [x] Update `references/regulations/README.md` index + changelog (broadened H1 "FDA"→"Federal" since HIPAA is HHS/OCR Title 45)
- [x] Fetch / confirm NIST SP 800-66 Rev. 2 structure from NIST CSRC (Feb 2024 final; structure + crosswalk concept from knowledge — specific 800-53 control IDs marked [VERIFY])
- [x] Author `references/industry-frameworks/nist-sp-800-66.md`
- [x] Update `references/industry-frameworks/README.md` index + changelog
- [x] Sister-project compat check — leakage scan clean (zero PP3500/project tokens in both files); sister checkout not present on this machine to diff, but files generalize by construction
- [ ] Push (PR → auto-merge → delete branch) per git-workflow rule, once user approves

## Open Questions

- Privacy Rule (Subpart E) depth — anchor doc points to it but does not distill it. Confirm Security-Rule-only scope is acceptable for v1 (assumed yes; Privacy is covered-entity practice, less device-relevant).

## Changelog
- 2026-06-02: **Both deliverables authored.** (1) `references/regulations/45-cfr-part-164.md` — HIPAA Security Rule, verbatim §§164.302–318 + Appendix A matrix pulled from eCFR Title 45 API (issue 2026-05-29); Subparts D/E summarized; 2025 NPRM noted as forward-looking. (2) `references/industry-frameworks/nist-sp-800-66.md` — NIST SP 800-66 Rev. 2 implementation guide + Security-Rule→CSF/800-53 crosswalk (control IDs marked [VERIFY]). Both folder READMEs updated (regulations H1 broadened "FDA"→"Federal Regulations" since HIPAA is HHS/OCR Title 45; both changelogs appended). Leakage scan clean. **Not yet committed/pushed** — awaiting user go-ahead.
- 2026-06-02: Task created. Grounding established (regulations README + 880 format, SKILL.md import path). Confirmed direct-authoring is the correct path (no skill action). Two deliverables scoped across regulations/ + industry-frameworks/.
