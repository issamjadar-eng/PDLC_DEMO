# QMSR (21 CFR Part 820) — Project Applicability

_Demo sample data — not for clinical use._

**Regulation**: 21 CFR Part 820 — Quality Management System Regulation (QMSR)
**L1a source (authoritative text)**: [`.claude/skills/medtech-docs/references/regulations/21-cfr-part-820.md`](../../../.claude/skills/medtech-docs/references/regulations/21-cfr-part-820.md) (finding aid) → [`source-md/21-cfr-part-820.md`](../../../.claude/skills/medtech-docs/references/regulations/source-md/21-cfr-part-820.md) (faithful text, eCFR @ 2026-07-13)
**Scope of this file**: how the current Part 820 (QMSR) reaches the PP3500 program — and what the QSR→QMSR transition means for this program's existing citations. The L1a file says *what the rule requires*; this file says *what this program decided about it*.

---

## 1. Applicability determination

| Question | Determination |
|----------|---------------|
| Is the program in scope of Part 820? | **Yes.** PP3500 is a finished Class II device manufactured for U.S. distribution (§ 820.1(a)); the manufacturer must document a QMS complying with ISO 13485:2016 per § 820.10(a). |
| Do design-and-development requirements apply? | **Yes.** § 820.10(c) requires Class II manufacturers to comply with ISO 13485 **Clause 7.3** and its subclauses — the CFR anchor for this program's design controls / DHF. |
| Does the life-supporting traceability add-on (§ 820.10(d)) apply? | **[VERIFY — program decision]**: a PCA opioid pump failure "can be reasonably expected to result in a significant injury"; the Clause 7.5.9.2 traceability determination should be made explicitly by Quality/Regulatory and recorded here. |
| Which supplemental provisions bind us? | § 820.35 (complaint/servicing/UDI record content — feeds the postmarket complaint-handling and servicing procedures) and § 820.45 (labeling/packaging examination — feeds DI-028/DI-029 labeling controls). |

## 2. The QSR→QMSR citation-staleness decision (this program)

The QMSR (source: 89 FR 7523) **repealed the former QSR section inventory** — §§ 820.20–820.30, § 820.40, and Subparts C–O are `[Reserved]` in the current text. Former § 820.30 (design controls), **§ 820.75 (process validation)**, § 820.100 (CAPA), § 820.181/.184 (DMR/DHR), § 820.198 (complaint files) **no longer exist**.

**Program rule (decided 2026-07-14, task ben/105):** documents in this program cite current law —

1. **Process validation** → cite **ISO 13485:2016 §7.5.6 (process validation), incorporated by reference per 21 CFR 820.7/820.10** — not former § 820.75. `[VERIFY the §7.5.6 clause number against a licensed ISO 13485:2016 copy — the CFR names the standard, not the internal clause map]`
2. **Design controls** → ISO 13485 Clause 7.3 via § 820.10(c) (the DHF concept continues; the § 820.30(j) text is gone).
3. Legacy QSR numbers may appear only as explicitly historical citations ("former § 820.75 (pre-QMSR QSR)").
4. Existing QMS documents (`docs/internal/source-md/**`) that anchor on QSR numbers (e.g., GL-SOP-DC-007's "820.30(h)", qms-index anchors) are **not rewritten in this pass** — they are a QMS-owner remediation backlog item; new/updated DHF documents follow the rule above. `[VERIFY scope of the QMS remediation with Quality]`

First application: the pFMEA (`GL-TMP-RM-004-process-fmea.md`) process-validation citations were repaired from "21 CFR 820.75" to the ISO 13485 §7.5.6-via-§ 820.7 form (reference audit RA-gl-tmp-rm-004-process-fmea-001, finding E2).

## 3. Module mapping

| Obligation (current law) | Program home |
|---|---|
| § 820.10(a)+(c) QMS + Clause 7.3 design & development | The DHF trees under `docs/project/dhfs/` + design-controls SOPs (`docs/internal/source-md/design-controls/`) |
| § 820.35(a) complaint record content | `docs/project/dhfs/pca-device/postmarket/complaints/` + GL-SOP-PM complaint handling |
| § 820.35(b) servicing records | Serviceability path (DI-031 service menu; service procedures) |
| § 820.35(c) UDI recording | DI-028 (UDI/GUDID) |
| § 820.45 labeling/packaging examination | DI-028/DI-029 labeling controls; pFMEA FM-P-008 (UDI misprint) escape controls |

## 4. Open items

- `[VERIFY]` QMSR effective/compliance date narrative (widely stated Feb 2, 2026) against the final rule DATES section before use in a filed document.
- `[VERIFY]` ISO 13485:2016 internal clause numbers (7.5.6, 8.5.2/8.5.3, 4.2.5…) against a licensed copy — no ISO 13485 source text exists in this repository.
- QMS-document QSR-number remediation backlog (Section 2, rule 4) — owner: Quality Engineering.

## Changelog

| Date | Author | Summary |
|------|--------|---------|
| 2026-07-14 | AI assistant (task ben/105) | Initial applicability analysis — QMSR structure, citation-staleness program rule, pFMEA § 820.75 repair recorded. |
