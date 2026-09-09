# TC-PROTO-CITATIONS v2 · run 2 · citations agent (batch, 16 items) · 2026-09-08 · model claude-fable-5-1 · reference-audit 6

| # | kind | band | evidence (verbatim) |
|---|---|---|---|
| 1 | sound-by-distillation | sound | L1a `iso-14971.md` L31; L1b L29; no quarantine; no source-md. |
| 2 | sound-by-distillation | sound | L1a `iec-62304.md` L58; L1b L27. |
| 3 | ambiguous-source | unverified | L1a `iec-62366-1.md` L9 quarantine; L1b L7/L9 same; body L30 says 5.1 but quarantine rule fires first. |
| 4 | sound-by-distillation | sound | L1a `iso-14971.md` L48; L1b L46. |
| 5 | sound-by-distillation | sound | L1a `iec-62304.md` L107; L1b L76. |
| 6 | ambiguous-source | unverified | Both tiers quarantined; body 5.2 vs banner's audited sequence — self-conflicting. |
| 7 | citation-mislabeled | broken | source-md `qsub.md`: no such heading; real headings L720 and L1116–1117; L1b `qsub.md` L30 states the label is not in the guidance. |
| 8 | sound | sound | `submission-tracker.md` L16 href `510k/composition-manifest.md` resolves. |
| 9 | sound-by-distillation | sound | L1a `iec-62304.md` L23; L1b L13–21 + L165; `project.yml` L36–47 `iec62304: C`. |
| 10 | stale-citation | broken | source-md `21-cfr-part-820.md` L113 [Reserved]; § 820.10(c) → ISO 13485 7.3; L1b `qmsr-part-820.md` L22–28. |
| 11 | registry-gap | unverified | No `iso-13485*.md` in either tier; READMEs record the gap. |
| 12 | ambiguous-source | unverified | Both tiers quarantined; bodies place summative under invented 5.6 (L1a L73–84, L1b L100). |
| 13 | citation-mislabeled | broken | L1a `iso-14971.md` L15–45 Clause 4 = 4.1–4.5; RMF at L41 4.5; L1b L15–39. |
| 14 | ambiguous-source | unverified | Both tiers quarantined, no annex list; no "Annex Q"/"sample size" anywhere. |
| 15 | stale-citation | broken | L1a `iec-62304.md` L58–63 § 5.1 = SDP; L1b L27–29; RMF at ISO 14971 § 4.5. |
| 16 | broken-link | broken | target absent under both resolutions. |

Tally: 6 sound + 1 internal sound = 7 sound, 5 unverified, 5 broken. Notes (verbatim gist): IEC 62366-1 items 3/6/12/14 land unverified deterministically (quarantine row fires first); item 7 broken on the label only; items 10/11 share a citing line; four researcher launches hit the 20-subagent cap and were re-dispatched; no web fetches.

## Operator scoring against protocol v2 §6
- S = {1,2,4,5,8,9} → 6/6 sound. Criterion B: **met**.
- U = {3,6,11,12,14} → all unverified with expected kinds. Criterion C (group U): **met**.
- B = {7,10,13,15,16} → all broken; kinds 7 mislabeled ✓, 10 stale ✓, 13 **mislabeled (expected citation-absent-from-source — kind confusion, same band)**, 15 stale ✓, 16 broken-link ✓ → 4/5 ≥ 4/5. Criterion C (group B): **met**.
- Criterion A: **met** (0 U/B items sound).
- Criterion D (band identical to run 1 for every item): **met** — 16/16 bands identical.
- **Run 2 (v2): PASS.**
