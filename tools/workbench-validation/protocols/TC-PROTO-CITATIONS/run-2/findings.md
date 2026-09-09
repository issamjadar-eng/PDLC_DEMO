# TC-PROTO-CITATIONS · run 2 · citations agent (batch, 16 items) · 2026-09-08 · model claude-fable-5-1

| # | kind | band | evidence (verbatim) |
|---|---|---|---|
| 1 | sound | sound | L1a `iso-14971.md` L31; L1b L29. Distilled only. |
| 2 | sound | sound | L1a `iec-62304.md` L58; L1b L27. |
| 3 | sound | sound | L1a `iec-62366-1.md` L30 + L9 audit banner; L1b L26. |
| 4 | unreachable-source | unverified | L1a `iso-14971.md` L46–52 matches predicate; L1b L44–50 same, but L167 carries a clause-number `[VERIFY]` caveat and the original is paywalled — capped. |
| 5 | sound | sound | L1a `iec-62304.md` L107; L1b L76. |
| 6 | stale-citation | broken | L1a L9 banner: real 5.2 = "UI characteristics related to safety"; body L44 is the disowned skeleton; L1b L40 repeats it under `[VERIFY]` (L124). |
| 7 | stale-citation (citation-mislabeled) | broken | source-md `qsub.md`: 0 hits for the heading; actual III.B(1) L82 and III.B(4)a L1116–17. Label copied from `qsub-distilled.md` L54 / L1b L28. |
| 8 | broken-link | broken | `../510k/composition-manifest.md` from `docs/project/submissions/` resolves to `docs/project/510k/…` — does not exist. |
| 9 | sound | sound | L1a `iec-62304.md` L23 "4.3 Software Safety Classification"; L1b L165. |
| 10 | stale-citation (citation-absent-from-source) | broken | source-md `21-cfr-part-820.md` L113 "§§ 820.20-820.30 [Reserved]"; §820.10(c) L99 → ISO 13485 Cl. 7.3; L1b L22. |
| 11 | registry-gap | unverified | No ISO 13485 distillation in L1a (`standards/README.md` L38) or L1b (`docs/external/standards/README.md` L54). |
| 12 | unreachable-source | unverified | L1a L9 banner places summative at 5.9 (matches) but under a do-not-cite quarantine; body L73–84 maps to invented "5.6"; L1b L117 no clause number. |
| 13 | stale-citation (citation-absent-from-source) | broken | Clause 4 = 4.1–4.5 only; RMF is 4.5. |
| 14 | ambiguous-source | unverified | Only Annex C named; no annex list; cannot deny from byte-correct text (no source-md). |
| 15 | stale-citation | broken | §5.1 = software development planning; RMF linkage at §4.2 / Clause 7. |
| 16 | broken-link | broken | file does not exist. |

Totals: 5 sound, 4 unverified, 7 broken. Notes (verbatim gist): item 7 heading propagates from both aids; items 6/12 hinge on the L1a quarantine banner contradicting the file's own body numbering; labels "citation-mislabeled"/"citation-absent-from-source" recorded as sub-types of `stale-citation`.

## Operator scoring against §6
| # | expected | observed | match |
|---|---|---|---|
| 1,2,3,5 | sound | sound | Y |
| 4 | sound | unverified | N |
| 6 | sound | broken | N |
| 7 | sound | broken | N |
| 8 | sound | broken-link | N (answer key wrong) |
| 9 | citation-mislabeled | **sound** | N — known-non-sound reported sound (answer key disputed) |
| 10 | stale-citation | stale-citation | Y |
| 11 | registry-gap | registry-gap | Y |
| 12 | citation-absent-from-source | unverified | kind mismatch (non-sound ✓) |
| 13,14 | citation-absent-from-source | 13 Y; 14 ambiguous-source (non-sound ✓, kind mismatch) | partial |
| 15,16 | as expected | as expected | Y |

Criterion A: **not met** (item 9). Criterion B: **not met** (4/8). Criterion C: **not met** (2/4). **Run 2: FAIL.**
