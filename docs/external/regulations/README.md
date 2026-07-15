# Regulations (Project Applicability)

Project-specific applicability analysis for federal regulations that bind this device program — the **L1b tier** of the medtech-docs two-tier model. The authoritative regulatory text (L1a) lives in the registry at `.claude/skills/medtech-docs/references/regulations/`; **this folder records how PP3500 decides each regulation applies to its modules** — classification rationale, module mapping, `[VERIFY]` markers, and open Q-Sub questions.

Per the medtech-docs **cite-both mandate**, any external regulatory citation must reference *both* the L1a registry distillation (what the rule says) and the matching file here (what this program decided about it).

## Active Regulations

| Regulation | File | Full Title | Applies To | L1a Source |
|-----------|------|-----------|-----------|-----------|
| QMSR (21 CFR Part 820) | [qmsr-part-820.md](./qmsr-part-820.md) | Quality Management System Regulation | The whole program QMS — § 820.10 ISO 13485 QMS requirement + Clause 7.3 design controls (Class II); § 820.35/§ 820.45 record/labeling supplements; program citation rule for repealed QSR numbers (former § 820.75 et al.) | [`references/regulations/21-cfr-part-820.md`](../../../.claude/skills/medtech-docs/references/regulations/21-cfr-part-820.md) |
| HIPAA (45 CFR Part 164) | [hipaa.md](./hipaa.md) | Security & Privacy of Individually Identifiable Health Information | The connected SaMD/cloud path that handles ePHI — cloud-suite + connectivity-adapter (PP3500 acts as a **business associate**) | [`references/regulations/45-cfr-part-164.md`](../../../.claude/skills/medtech-docs/references/regulations/45-cfr-part-164.md) |

## Evaluated — Not Required

_(none yet)_

## Conventions

- **Naming**: `regulation-short-name.md` (e.g., `hipaa.md`), matching the sibling `industry-frameworks/` convention. The L1a registry uses the formal `NN-cfr-part-NNN.md` citation name; this L1b tier uses the common short name.
- Lead with an explicit **applicability determination** (does this regulation reach the device, and in what role) before any clause mapping.
- Map each load-bearing clause to **concrete modules and SRS requirement IDs**, not prose generalities — the mapping is the audit artifact.
- Flag every unverified or illustrative claim with `[VERIFY]`.
- This is demo content — carry the `_Demo sample data — not for clinical use._` banner.

## Changelog

- 2026-07-14: Added `qmsr-part-820.md` — QMSR applicability + the program rule for repealed-QSR-number citations (driven by reference audit RA-gl-tmp-rm-004-process-fmea-001 finding E2). (task ben/105)

| Date | Author | Summary |
|------|--------|---------|
| 2026-06-02 | BX | Folder created (task ben/076). First entry: `hipaa.md` — L1b applicability for the HIPAA Security Rule, mapping §164.312 technical safeguards to PP3500's ePHI-handling modules + SRS. Closes the missing-L1b half of the cite-both mandate for HIPAA; pairs with the L1a registry distillation added in ben/075. This is the first `docs/external/regulations/` tier in the project (previously only standards / fda-guidance / industry-frameworks L1b tiers existed). |
