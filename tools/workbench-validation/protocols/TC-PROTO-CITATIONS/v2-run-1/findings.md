# TC-PROTO-CITATIONS v2 · run 1 · citations agent (batch, 16 items) · 2026-09-08 · model claude-fable-5-1 · reference-audit 6 (deterministic band rule)

| # | kind | band | evidence (verbatim) |
|---|---|---|---|
| 1 | sound-by-distillation | sound | L1a `standards/iso-14971.md` L31 `4.4 Risk Management Plan`; L1b L29 agrees. No source-md (paywalled). |
| 2 | sound-by-distillation | sound | L1a `standards/iec-62304.md` L58; L1b L27 agrees. |
| 3 | ambiguous-source | unverified | L1a `standards/iec-62366-1.md` L9 + L1b L7 quarantine banner; body L30 shows `5.1 Use Specification` but the number cannot be confirmed locally. |
| 4 | sound-by-distillation | sound | L1a `iso-14971.md` L48 `5.1 Risk Analysis Process`; L1b L46 agrees. |
| 5 | sound-by-distillation | sound | L1a `iec-62304.md` L107 `5.8 Software Release`; L1b L76 agrees. |
| 6 | ambiguous-source | unverified | IEC 62366-1 quarantine banner blocks a verdict; audited sequence places UI-characteristics at 5.2, hazard work at 5.3–5.4 — likely wrong but not escalated on quarantined evidence. |
| 7 | citation-mislabeled | broken | source-md `qsub.md` has no heading "Pre-Submission Package Contents"; content at L720 III.B(1) and L1116 III.B(4)(a)(1). L1b `qsub.md` L28–30 confirms the label was invented. |
| 8 | sound | sound | `submission-tracker.md` L16 href `510k/composition-manifest.md` resolves to the existing file. |
| 9 | sound-by-distillation | sound | L1a `iec-62304.md` L23 `4.3 Software Safety Classification`, L29 Class C; L1b L13–21 + L165 agree. |
| 10 | stale-citation | broken | source-md `21-cfr-part-820.md` L113 `§§ 820.20-820.30 [Reserved]`; § 820.10(c) → ISO 13485 Clause 7.3 (L99); L1b `qmsr-part-820.md` L22–28. |
| 11 | registry-gap | unverified | No `iso-13485*.md` in either tier; both READMEs record the gap (L1a README L38, L1b README L54). |
| 12 | ambiguous-source | unverified | IEC 62366-1 quarantine; L1a body has no §5.9 (summative under invented `5.6`, L73–84); banner's audited sequence lists 5.9 but is non-authoritative. |
| 13 | citation-absent-from-source | broken | L1a `iso-14971.md` Clause 4 skeleton L17–44 runs 4.1–4.5; RMF is `4.5` (L41); L1b L39 agrees. |
| 14 | ambiguous-source | unverified | Neither tier inventories IEC 62366-1 annexes; only Annex C named (L1a L9). Absence in a finding aid is not proof of absence. |
| 15 | stale-citation | broken | L1a `iec-62304.md` L58–63 §5.1 = SDP, not RMF maintenance; RMF at §4.2 (L21), §4.3 (L37), Clause 7 (L120–127); L1b L27–32 agrees. |
| 16 | broken-link | broken | target does not exist; only `GL-TMP-RM-001-risk-management-plan.md` in that folder. |

Tally: 7 sound (6 by distillation, 1 internal), 4 unverified, 5 broken. Notes (verbatim gist): 3/6/12/14 capped deterministically by the IEC 62366-1 quarantine banner in both tiers; 10/11 share one line; 1/2/3/12 are frontmatter `note:` annotations; L1b blanket `[VERIFY]` markers do not cap the band but are why verdicts are `sound-by-distillation`.

## Operator scoring against protocol v2 §6
- S = {1,2,4,5,8,9} expected band sound → observed 6/6 sound. Criterion B (≥ 5/6): **met**.
- U = {3,6,11,12,14} expected band unverified (3/6/12/14 `ambiguous-source`, 11 `registry-gap`) → observed exactly. Criterion C (group-U band): **met**.
- B = {7,10,13,15,16} expected kinds mislabeled / stale / absent / stale / broken-link → observed exactly (5/5 ≥ 4/5). Criterion C (group-B kinds): **met**.
- Criterion A (0 U/B items reported sound): **met**.
- **Run 1 (v2): PASS.** Criterion D (band identical across runs) evaluated after runs 2–3.
