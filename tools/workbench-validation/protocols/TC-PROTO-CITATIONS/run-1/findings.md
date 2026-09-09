# TC-PROTO-CITATIONS · run 1 · citations agent (batch, 16 items) · 2026-09-08 · model claude-fable-5-1

| # | kind | band | evidence (verbatim) |
|---|---|---|---|
| 1 | sound | sound | L1a `references/standards/iso-14971.md` L31 "4.4 Risk Management Plan"; L1b `docs/external/standards/iso-14971.md` L29 same. Citing L22. |
| 2 | sound | sound | L1a `iec-62304.md` L58 "5.1 Software Development Planning"; L1b L27 same. |
| 3 | sound | sound | L1a `iec-62366-1.md` L9 audited-skeleton banner (5.1 = use specification) + body L30; L1b L26. |
| 4 | sound | sound | L1a `iso-14971.md` L48 "5.1 Risk Analysis Process"; L1b L46. |
| 5 | sound | sound | L1a `iec-62304.md` L107 "5.8 Software Release"; L1b L76. |
| 6 | stale-citation (citation-mislabeled) | broken | L1a `iec-62366-1.md` L9 banner: real §5.2 = "UI characteristics related to safety"; use-related risk analysis at §5.3–5.4. Body L44 flagged "DO NOT CITE CLAUSE NUMBERS FROM THIS FILE". L1b L40 copies the pre-audit skeleton. |
| 7 | stale-citation (citation-mislabeled) | broken | L1a-full `fda-guidance/source-md/qsub.md` TOC L66–90: no section "Pre-Submission Package Contents". Content at III.B(1) "Submission Content" (L720) and Appendix 1 (L1581). Heading exists only in `qsub-distilled.md` L54 and L1b `qsub.md` L28. |
| 8 | broken-link | broken | `submission-tracker.md` L16 href `../510k/composition-manifest.md` resolves to `docs/project/510k/` (does not exist). Display text names the existing `docs/project/submissions/510k/composition-manifest.md`. |
| 9 | sound | sound | L1a `iec-62304.md` L23 "4.3 Software Safety Classification", L29 Class C definition; L1b L13 topic without clause number. |
| 10 | stale-citation | broken | L1a-full `regulations/source-md/21-cfr-part-820.md` (QMSR, eCFR 2026-07-13) L113 "§§ 820.20-820.30 [Reserved]"; design controls via L99 §820.10(c) → ISO 13485 Cl. 7.3. L1b `qmsr-part-820.md` L22, L27. |
| 11 | registry-gap | unverified | No `iso-13485*.md` in L1a or L1b; L1b `qmsr-part-820.md` L46 `[VERIFY]` "no ISO 13485 source text exists in this repository". |
| 12 | sound | sound | L1a `iec-62366-1.md` L9 audited skeleton: "5.9 summative evaluation". L1b maps summative to stale §5.6 (L76–80, L96) — L1b staleness. |
| 13 | stale-citation (citation-absent-from-source) | broken | L1a `iso-14971.md` L15–44 Clause 4 = 4.1–4.5; no §4.9; RMF is §4.5 (L41). L1b same. |
| 14 | stale-citation (citation-absent-from-source) | broken | "Annex Q" absent from L1a and L1b `iec-62366-1.md`; L1a L9 note: no statistical task-success evidence required. Annex inventory not confirmable against the copyrighted original. |
| 15 | stale-citation (predicate mismatch) | broken | L1a `iec-62304.md` L58 §5.1 = software development planning; no RMF-maintenance requirement. RMF maintenance is ISO 14971 §4.5. |
| 16 | broken-link | broken | `GL-TMP-RM-999*` in the plans folder = 0 files. |

Totals: 7 sound, 1 unverified, 8 broken. Agent notes: items 1–5, 9, 12–15 verified against distilled registry text only (ISO/IEC copyrighted); 7 and 10 against L1a-full source-md. Cross-cutting: `docs/external/standards/iec-62366-1.md` lacks the L1a quarantine banner and carries the pre-audit clause map; the "Pre-Submission Package Contents" heading originates in the distilled aid. Fixes: item 8 href → `510k/composition-manifest.md`; 13/15 → ISO 14971 §4.5; 10 → 21 CFR 820.10(c) → ISO 13485 Cl. 7.3.

## Operator scoring against §6
| # | expected | observed | match |
|---|---|---|---|
| 1–5 | sound | sound | Y |
| 6 | sound | broken | N |
| 7 | sound | broken (mislabeled — heading exists only in finding aids) | N |
| 8 | sound | broken-link (href resolves to `docs/project/510k/`) | N — **the answer key is wrong; the link is genuinely broken** |
| 9 | citation-mislabeled | **sound** | N — known-non-sound reported sound (answer key disputed: L1a carries a "4.3" label) |
| 10 | stale-citation | stale-citation | Y |
| 11 | registry-gap | registry-gap | Y |
| 12 | citation-absent-from-source | **sound** | N — known-non-sound reported sound (answer key disputed: audited sequence has 5.9) |
| 13 | citation-absent-from-source | citation-absent-from-source (sub-type) | Y |
| 14 | citation-absent-from-source | citation-absent-from-source (sub-type) | Y |
| 15 | stale-citation | stale-citation | Y |
| 16 | broken-link | broken-link | Y |

Criterion A (0 known-non-sound reported sound): **not met** (items 9, 12). Criterion B (≥ 7/8 known-sound sound): **not met** (5/8). Criterion C (items 9–12 kind match ≥ 3/4): **not met** (2/4). **Run 1: FAIL.**
