# TC-PROTO-CITATIONS v2 · run 3 · citations agent (batch, 16 items) · 2026-09-08 · model claude-fable-5-1 · reference-audit 6

| # | kind | band | evidence (verbatim) |
|---|---|---|---|
| 1 | sound-by-distillation | sound | L1a `iso-14971.md` L31; L1b L29 + table L140. |
| 2 | sound-by-distillation | sound | L1a `iec-62304.md` L58; L1b L27, table L142. |
| 3 | ambiguous-source | unverified | L1a `iec-62366-1.md` L9 quarantine banner (mirrored L1b L7, L9); body L30 says 5.1 but band rule caps. |
| 4 | sound-by-distillation | sound | L1a `iso-14971.md` L48; L1b L46. |
| 5 | sound-by-distillation | sound | L1a `iec-62304.md` L107; L1b L76, table L146. |
| 6 | ambiguous-source | unverified | Quarantine banner; body L44 vs banner sequence conflict. |
| 7 | citation-mislabeled | broken | source-md `qsub.md`: zero hits; real headings L720 III.B(1) and L1116–1117 III.B(4)(a)(1); distilled L54–56 and L1b L30 record the 2026-09-08 relabel. |
| 8 | sound | sound | href `510k/composition-manifest.md` resolves to the manifest (L8 H1; Draft status). |
| 9 | sound-by-distillation | sound | L1a `iec-62304.md` L23, L29; L1b L13–21; L1b L165 stub. |
| 10 | stale-citation | broken | source-md `21-cfr-part-820.md` L111–113 [Reserved]; § 820.10(c) → ISO 13485 7.3; L1b `qmsr-part-820.md` L24–28; citing line not labelled historical. |
| 11 | registry-gap | unverified | No `iso-13485*.md` in either tier; both READMEs record the gap (L1b README L54 names this citation). |
| 12 | ambiguous-source | unverified | Quarantine banner; banner sequence 5.9 vs body §5.6 (L100). |
| 13 | citation-absent-from-source | broken | L1a `iso-14971.md` Clause 4 = 4.1–4.5 (L17–L44); no §4.9; RMF §4.5 (L41); L1b mirrors. |
| 14 | ambiguous-source | unverified | Quarantine banner; no annex inventory; no "Annex Q" anywhere. |
| 15 | stale-citation | broken | L1a `iec-62304.md` §5.1 (L58–63) = SDP; RMF at ISO 14971 §4.5; 62304 §4.2 (L21) / Clause 7 (L120–127); L1b L174. |
| 16 | broken-link | broken | target does not exist. |

Tally: 7 sound, 5 unverified, 5 broken (the agent's note "6 broken … and 10" double-counted item 10). Notes (verbatim gist): all four IEC 62366-1 items land on the deterministic row-1 outcome; item 10 is the one real-document broken finding; caller's Standards Anchor line for item 1 is L43 not L42 in the current file.

## Operator scoring against protocol v2 §6
- S = {1,2,4,5,8,9} → 6/6 sound. **B met.**
- U = {3,6,11,12,14} → all unverified, expected kinds. **C (U) met.**
- B = {7,10,13,15,16} → all broken; kinds 5/5 as expected. **C (B) met.**
- **A met** (0 U/B items sound). **D met** — bands identical to runs 1 and 2 for all 16 items.
- **Run 3 (v2): PASS.**
