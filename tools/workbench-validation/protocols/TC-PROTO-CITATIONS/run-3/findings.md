# TC-PROTO-CITATIONS · run 3 · citations agent (batch, 16 items) · 2026-09-08 · model claude-fable-5-1

Returned verdicts (verbatim; L1a = `.claude/skills/medtech-docs/references/`, L1b = `docs/external/`):

| # | kind | band | evidence |
|---|---|---|---|
| 1 | unreachable-source | unverified | Citing doc L22 confirmed. L1a `standards/iso-14971.md` L31 "4.4 Risk Management Plan"; L1b L29 same + L140 table. Predicate matches; finding aid only (no source-md, paywalled) — capped. |
| 2 | unreachable-source | unverified | Citing doc L22 confirmed. L1a `standards/iec-62304.md` L58 "5.1 Software Development Planning"; L1b L27 same. Predicate matches; finding aid only — capped. |
| 3 | unreachable-source | unverified | Citing doc L22 confirmed. L1a `standards/iec-62366-1.md` L30 "5.1 Use Specification" + quarantine banner L9 audited sequence agrees; L1b L26 same. Paywalled + numbering under quarantine — capped. |
| 4 | unreachable-source | unverified | L1a `iso-14971.md` L46-52 "5.1 Risk Analysis Process"; L1b L46 same. Predicate matches — capped. |
| 5 | unreachable-source | unverified | L1a `iec-62304.md` L107 "5.8 Software Release"; L1b L76 same. Predicate matches — capped. |
| 6 | stale-citation | broken | L1a `iec-62366-1.md` banner L9 (only audited numbering): real §5.2 = "UI characteristics related to safety"; use-related hazard work is §5.3–5.4. Body L44 / L1b L40 labelling 5.2 "Use-Related Risk Analysis" is the quarantined invented numbering. |
| 7 | citation-mislabeled | broken | L1a `fda-guidance/source-md/qsub.md` has no heading "Pre-Submission Package Contents"; content is under III.B(1) "Submission Content" (L82, L722) and III.B(4)(a)(1) (L1116-1149). Heading exists only in the aids (L1a `qsub-distilled.md` L54; L1b `fda-guidance/qsub.md` L28). |
| 8 | broken-link | broken | `submission-tracker.md` L16 confirmed. `../510k/composition-manifest.md` → `docs/project/510k/...` does not exist; file is at `docs/project/submissions/510k/composition-manifest.md`. |
| 9 | unreachable-source | unverified | Citing doc L14 confirmed. L1a `iec-62304.md` L23 "4.3 Software Safety Classification" (L31 flags sub-clause lettering [VERIFY]); L1b L13, L165. Predicate matches — capped. |
| 10 | stale-citation | broken | L1a `regulations/source-md/21-cfr-part-820.md` L113 "§§ 820.20-820.30 [Reserved]" — 820.30(b) does not exist under the 2024 QMSR; planning reaches CFR via L99 §820.10(c) → ISO 13485 Clause 7.3. L1b `qmsr-part-820.md` L22-28. |
| 11 | registry-gap | unverified | No ISO 13485 distillation in L1a nor L1b. Only indirect: 21 CFR 820 source-md L99 invokes "Clause 7.3 and its Subclauses" without naming 7.3.2. |
| 12 | unreachable-source | unverified | L1a `iec-62366-1.md` banner L9 audited sequence "5.9 summative evaluation" — predicate matches; body L73-84 and L1b L69-80 still file summative under invented "5.6". Paywalled — capped. |
| 13 | citation-absent-from-source | broken | §4.9 appears nowhere in L1a `iso-14971.md` (Clause 4 = 4.1-4.5, L17-44) nor L1b. Risk management file is §4.5. |
| 14 | citation-absent-from-source | broken | No "Annex Q" and no sample-size table in L1a `iec-62366-1.md` or L1b; banner L9 names only Annex C (UOUP). |
| 15 | stale-citation | broken | L1a `iec-62304.md` L58-63 "5.1 Software Development Planning" — nothing on maintaining a risk management file; L1b L27-32 same. Clause exists, predicate mismatch. |
| 16 | broken-link | broken | `docs/project/dhfs/pca-device/design-controls/plans/GL-TMP-RM-999-nonexistent.md` does not exist. |

Totals: 0 sound, 7 unverified (1, 2, 3, 4, 5, 9, 12 unreachable-source; 11 registry-gap), 8 broken (6, 7, 10, 13, 14, 15 citation defects; 8, 16 broken links).

Agent notes (verbatim): the seven `unverified` items are not defects in the citations — clause→topic mapping confirmed in both aids, but ISO/IEC standards have no bundled source-md, so `sound` cannot be reached on registry evidence alone (paywalled originals are never web-fetched). Fixes suggested: item 11 add `standards/iso-13485.md` L1a + L1b; item 10 cite "21 CFR 820.10(c) → ISO 13485 Clause 7.3.2" or label 820.30(b) former; item 8 change link target to `510k/composition-manifest.md`; items 6/12 root cause — `docs/external/standards/iec-62366-1.md` never re-synced after the L1a quarantine of 2026-06-11 and still carries the invented Clause 5 numbering without the banner. Item 16 line number taken from the brief; the internal researcher does not read under `tasks/*/_scratch/`.

## Operator scoring against protocol §6 (expected → observed)

| # | expected | observed | match |
|---|---|---|---|
| 1–5 | sound | unverified (unreachable-source, predicate matches) | N |
| 6 | sound | broken (stale-citation) | N |
| 7 | sound | broken (citation-mislabeled) | N |
| 8 | sound | broken (broken-link) | N |
| 9 | citation-mislabeled | unverified (L1a carries a 4.3 label) | kind mismatch (non-sound ✓) |
| 10 | stale-citation | stale-citation | Y |
| 11 | registry-gap | registry-gap | Y |
| 12 | citation-absent-from-source | unverified (audited sequence has 5.9) | kind mismatch (non-sound ✓) |
| 13 | citation-absent-from-source | citation-absent-from-source | Y |
| 14 | citation-absent-from-source | citation-absent-from-source | Y |
| 15 | stale-citation | stale-citation | Y |
| 16 | broken-link | broken-link | Y |

- Criterion A (0 known-non-sound reported sound): **met** (0/8).
- Criterion B (≥ 7 of 8 known-sound reported sound): **not met** (0/8).
- Criterion C (items 9–12 kind matches ≥ 3/4): **not met** (2/4; 9 and 12 mismatched — and the agent's evidence indicates the protocol's expectations for 9 and 12 may themselves be wrong).
- **Run 3: FAIL.**
