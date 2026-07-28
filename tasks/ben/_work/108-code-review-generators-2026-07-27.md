# Code review — the eleven demo-data generators (commercial corpus)

**What was reviewed**: the eleven small programs that fabricate the demo business
datasets (device fleet, complaints, upgrade campaign, financials, revenue plan, sales
accounts, win/loss log, subscriptions, telemetry, regulatory docket, signal register).
Files: `docs/project/corpus/commercial/*/gen.py` plus each dataset's `dataset.yml` and
`README.md`.

- **Date**: 2026-07-27 (findings resolved same day)
- **Reviewer**: AI assistant (independent code-review pass, task ben/108)
- **Verdict in one line**: all eleven generators produce consistent, repeatable,
  correctly-labeled demo data; the review found one genuine data defect, one data-quality
  incoherence, and two guard-rail gaps — all four have since been fixed (with fresh data
  published where needed) and the remaining seven minor observations were accepted.

## Plain-language summary

We reviewed the programs that manufacture the fabricated demo datasets every business
answer is computed from. The key design promise is that several datasets describe the
same imaginary world — the same hospitals, the same device fleet — so they must stay
consistent with each other, and every documented property of the data (rates, planted
special records, cross-dataset ties) must actually hold. The review confirmed the
world-consistency promise held everywhere it is claimed, and confirmed the documented
properties on the real data files. It raised 11 issues: 3 moderate — a reference-number
collision that tied two safety signals to the same corrective action, sales prospects
whose region and market segment changed from row to row, and one dataset whose declared
column list was missing three real columns — and 8 minor. Since the review, all four
issues marked for fixing have been fixed: the two data defects were corrected and fresh
data published the same day, the missing columns were declared, and an automatic
consistency check now runs whenever the fleet dataset is rebuilt, so the world-consistency
promise is machine-enforced instead of relying on care. The seven remaining minor
observations were accepted with written reasons. Nothing remains unresolved.

## What we checked

- World consistency — the shared model code embedded in seven generators compared
  byte-for-byte against the master copy, and the resulting data files cross-checked row
  by row (subscriptions vs fleet, telemetry vs fleet, campaign targets vs fleet).
- Repeatability — fixed random seed only, no clock reads, so a rebuild reproduces the
  data exactly.
- Declared shape — every column a generator emits is declared in its dataset description.
- Documentation honesty — every rate, count, and planted special record the README claims
  was recomputed from the actual data files.
- The "not for clinical use" demo banner stamped into every raw output.
- Robustness — behavior under future knob changes (empty pools, division, id collisions).

## Findings

### F-SR-1 (medium) — two safety signals shared corrective-action reference numbers

**What's wrong:** in the signal register, the reference counter that numbers generated
corrective actions collided with two hand-planted reference numbers, so two unrelated
pairs of safety signals each pointed at the same upgrade item (an over-delivery signal
and a battery signal sharing one reference, twice).
**Why it matters:** any analysis tracing "which corrective action closed which safety
signal" would pick up unrelated records — the one genuine data defect found.
**Resolution:** FIXED — the planted references were renumbered outside the generated
range (now UPG-0101 and UPG-0102), the generator carries a comment explaining the reserved
range, and a fresh snapshot (2026-07-27.2) was published; the regenerated data has zero
duplicate references and the two planted over-delivery ties verified.

### F-WL-1 (medium) — sales prospects changed identity between rows

**What's wrong:** in the win/loss log, prospect accounts (PRO-NN ids) had their region and
market segment re-drawn independently every time they appeared, while their name was
cached from first sight — so 14 prospect accounts carried conflicting segments and 11
conflicting regions across their rows (e.g. a "University Medical Center" row labeled
community hospital).
**Why it matters:** any analysis grouping opportunities by account inherited contradictory
attributes.
**Resolution:** FIXED — each prospect id now gets one stable identity: region and segment
are drawn from a dedicated random stream seeded by the prospect id itself (fully
deterministic), so repeated opportunities at the same prospect always agree. A fresh
snapshot (2026-07-27.4) was published; the regenerated data has zero identity conflicts
and the README's documented rates were re-verified against it (win rate 45.8%, 55 of 120;
disruption-window and predictive-monitoring-gap knobs restated to the new data).

### F-CO-1 (medium) — the complaints dataset under-declared its own columns

**What's wrong:** the complaints data file contains site, device-model, and
firmware-version columns that its dataset description did not declare — so validation
never covered them, and the README's documented battery-complaint skew rides on exactly
those columns. (Same defect class an earlier sweep fixed on two sibling datasets;
complaints was missed.)
**Why it matters:** undeclared columns are invisible to the automatic shape checks.
**Resolution:** FIXED — `site_id`, `model`, and `firmware_version` are now declared as
required columns in `internal-complaints/dataset.yml` (configuration-only change; no data
regeneration needed, matching the earlier sweep's precedent).

### F-FL-1 (low) — nothing mechanically enforced the shared-model promise

**What's wrong:** seven generators embed a byte-for-byte copy of the fleet model, but
nothing checked the copies stay identical — the convention was an honor system, and this
review was the detection mechanism.
**Why it matters:** a future edit to one copy would silently split the shared world.
**Resolution:** FIXED — a checker script (`check_shared_model.py`) now lives in the fleet
dataset and is wired into the dataset's automatic validation (`asserts.command` in
`internal-fleet/dataset.yml`), so any rebuild or validation of the fleet dataset fails
loudly if any embedded copy drifts. Verified by running it: 6 embedding generators
checked, 0 drifts.

### F-CO-2 (low) — a knob change could crash the complaints generator

**What's wrong:** one re-roll step picks from the older device model's population and
would crash if a mix knob were ever pushed to make that population empty.
**Why it matters:** a future knob edit could break the data rebuild with a confusing
crash instead of a clear message.
**Resolution:** ACCEPTED — the population is ~198 devices at the locked seed; noted for
future knob edits.

### F-UC-1 (low) — rolled-back upgrades keep their completion date

**What's wrong:** the four rolled-back campaign rows retain a completion date and
duration, so a date-based completion count would over-count by four (status-based
consumers are correct).
**Why it matters:** a future analysis that counts completions by date instead of by
status would silently overstate campaign progress.
**Resolution:** ACCEPTED — defensible semantics (completed, then rolled back); document in
the README or blank the date at the next refresh.

### F-RP-1 (low) — the revenue plan duplicates the regional split constants

**What's wrong:** the plan's regional share values duplicate the financial model's
constants outside any marked shared block; a future region-mix change would leave the plan
behind.
**Why it matters:** the plan's regional split could silently drift out of step with the
actuals if the shared constants ever change.
**Resolution:** ACCEPTED — plan-vs-actuals joins are region-insensitive where it matters;
add a keep-in-sync comment at next touch.

### F-SA-1 (low) — two different segment conventions coexist

**What's wrong:** sales-account segments are derived from bed counts, not the shared
site-segment function used by telemetry and win/loss, so the same underlying site can
carry different segments across datasets (no key-level contradiction — the id spaces never
join directly).
**Why it matters:** an analysis that compared segment mixes across the two conventions
would draw conclusions from an apples-to-oranges join.
**Resolution:** ACCEPTED — account-level vs site-level entities differ by design; worth
one README sentence so analysis authors do not cross-tabulate segments across the two
conventions.

### F-SA-2 (low) — the account-name list has no wraparound guard

**What's wrong:** 56 name stems, 39 consumed; an index error only if the site count grew
about 40%.
**Why it matters:** a large future expansion of the fabricated world would crash the
generator instead of degrading gracefully.
**Resolution:** ACCEPTED — ample headroom at the locked region set.

### F-SU-1 (low) — sampling pools could shrink below the sample size

**What's wrong:** two fixed-size samples (attach-gap sites, churned sites) would crash if
future knob changes shrank their pools below the sample size (the telemetry generator has
the same pattern).
**Why it matters:** a future knob edit could break the data rebuild with an unexplained
crash rather than a clear message.
**Resolution:** ACCEPTED — pools are ~40+ at the locked seed; noted for knob edits.

### F-RD-1 (low) — docket record ids are emergent, not pinned

**What's wrong:** the specific record ids the READMEs and the complaints cross-reference
cite (MDR-2025-0007/0018, MDR-2026-0005) fall out of the seed-42 draw order rather than
being constructed; any seed/knob/count change silently renumbers them.
**Why it matters:** a regeneration with different settings would silently break the
documented cross-dataset ties the storyline depends on.
**Resolution:** ACCEPTED — verified correct at the locked seed; re-verify both READMEs and
the complaints tie in the same pass if the generator is ever re-knobbed.

## Terms used

- **Generator** — a small program that fabricates one demo dataset from a fixed random
  seed, so the data is reproducible.
- **Shared model** — the block of code (hospital sites + device fleet) embedded
  byte-identically in seven generators so their datasets describe the same imaginary
  world.
- **Snapshot / refresh** — a dated, immutable copy of a dataset's output; a refresh
  publishes a new snapshot (e.g. 2026-07-27.4) without altering older ones, so previously
  published answers stay reproducible.
- **Knob** — a tunable constant in a generator (rates, counts, planted records) whose
  intended effect the README documents.
- **Planted record** — a hand-authored special row (e.g. the over-delivery complaints)
  inserted deliberately to drive a storyline, as opposed to randomly drawn rows.
- **asserts.command** — a per-dataset validation hook: a command that must pass whenever
  the dataset is rebuilt or validated.
- **RNG stream** — an independent sequence of random draws; separate streams per concern
  mean appending new rows cannot shift previously drawn data.

## Technical appendix

Method at review time: static review of every generator against its `dataset.yml` schema
and README knob claims; byte-level extraction + hash comparison of every embedded shared
block; knob claims verified against the committed latest snapshots (read-only; no
regeneration during review). Contract: `.claude/skills/corpus/SKILL.md` v4 — generator
conventions incl. the shared-model honor system at SKILL.md L199–205 (now superseded by
the mechanical check below).

Shared-model identity matrix (canonical copies: `make_fleet` + `REGIONS` in
`internal-fleet/gen.py`; `site_segment` in telemetry/winloss; FINANCIAL MODEL block in
financials/sales-accounts):

| Generator | Fleet model + REGIONS | site_segment | FINANCIAL MODEL |
|---|---|---|---|
| internal-fleet | canonical (md5 f4ac0fe2d1) | — | — |
| internal-complaints | byte-identical, called first | — | — |
| internal-upgrade-campaign | byte-identical, first | — | — |
| internal-subscriptions | byte-identical, first | — | — |
| internal-telemetry-utilization | byte-identical, first | identical (365 B) | — |
| internal-winloss | byte-identical, first | identical | — |
| internal-sales-accounts | byte-identical, first | not embedded (F-SA-1) | identical |
| internal-financials | n/a (not fleet-linked) | — | canonical |
| internal-revenue-plan | n/a (no rng) | — | values duplicated (F-RP-1) |
| internal-regulatory-docket | n/a (not device-linked) | — | — |
| internal-signal-register | n/a (not device-linked) | — | — |

Notes: the FINANCIAL MODEL pair differs only in the one-line header comment naming the
sibling file (mutual-pointer convention, not drift; `quarterly_line_revenue` md5
ad66219a5d identical). A naive def-to-next-def extraction shows apparent `make_fleet`
"drift" — that is trailing module constants, not function drift; precise extraction
confirms all seven copies byte-identical.

Cross-dataset alignment verified on snapshots: subscriptions `pumps_connected` == fleet
per-site connected count for all 42 rows; telemetry device set == fleet connected set
exactly (331 == 331); campaign target set (389) == fleet PP3500 not on 3.4.0 (389).

Fix verification (2026-07-27, current files):

| Finding | Resolution | Where (current files) |
|---|---|---|
| F-SR-1 | fixed | `internal-signal-register/gen.py` L61–70 (planted UPG-0101/0102 + reserved-range comment); snapshot 2026-07-27.2 re-verified: 0 duplicate refs; SIG-2025-028→UPG-0101, SIG-2026-005→UPG-0102 |
| F-WL-1 | fixed | `internal-winloss/gen.py` L85–94 (per-id `Random(f"{seed}:pro:{acct_id}")` stream); snapshot 2026-07-27.4 re-verified: 0 region/segment conflicts across all PRO- rows; README knobs restated (win 45.8% = 55/120) |
| F-CO-1 | fixed | `internal-complaints/dataset.yml` L24–27 (`site_id`, `model`, `firmware_version` declared required) |
| F-FL-1 | fixed | `internal-fleet/dataset.yml` L30–35 (`asserts.command: python3 check_shared_model.py`) + `internal-fleet/check_shared_model.py`; run output: "shared-model check: 6 embedding generator(s), 0 drift(s)" |
| F-CO-2 | accepted | complaints PP3000 re-roll pool ~198 at locked seed |
| F-UC-1 | accepted | rollback keeps completed_date; status-based consumers correct |
| F-RP-1 | accepted | REGION_SHARE duplication; joins region-insensitive |
| F-SA-1 | accepted | beds-derived vs hash-derived segments; entity types differ by design |
| F-SA-2 | accepted | NAME_STEMS headroom (56 vs 39) |
| F-SU-1 | accepted | sample pools ~40+ at locked seed |
| F-RD-1 | accepted | docket ids emergent from seed-42; re-verify READMEs on re-knob |

Edition-pinning note: the BQ answer editions published 2026-07-27 pin the pre-fix
snapshots, which remain on disk untouched — those editions stay reproducible. The fixed
data lives in the new snapshots (signal-register 2026-07-27.2, winloss 2026-07-27.4,
now `latest`) and flows into the next answer refresh.

Machine-readable record (dispositions reflect actual outcomes):

```json
{
  "reviews": [
    {"path": "corpus:commercial/internal-fleet/gen.py", "verdict": "APPROVED",
     "summary": "Canonical shared-model owner; deterministic, no clocks, banner stamped, schema exact; 884/686/198/331 counts verified on snapshot; drift detection now mechanical.",
     "findings": [
       {"id": "F-FL-1", "severity": "low", "summary": "No mechanical drift detection for the embedded make_fleet copies (honor system)", "disposition": "fixed: check_shared_model.py wired as asserts.command; verified 6 generators, 0 drifts"}
     ]},
    {"path": "corpus:commercial/internal-complaints/gen.py", "verdict": "APPROVED-WITH-FINDINGS",
     "summary": "make_fleet byte-identical and called first; clean seed+1/seed+2 stream split; all rare-record README claims verified on snapshot; schema now complete.",
     "findings": [
       {"id": "F-CO-1", "severity": "medium", "summary": "CSV emitted site_id, model, firmware_version undeclared in dataset.yml", "disposition": "fixed: three columns declared required in dataset.yml (config-only, no regeneration)"},
       {"id": "F-CO-2", "severity": "low", "summary": "Battery-reroll PP3000 filter crashes on empty list if model-mix knob nears 1.0", "disposition": "accepted: ~198 PP3000 devices at locked seed; note for knob edits"}
     ]},
    {"path": "corpus:commercial/internal-upgrade-campaign/gen.py", "verdict": "APPROVED-WITH-FINDINGS",
     "summary": "make_fleet byte-identical and first; 389 targets equal fleet PP3500 non-3.4.0 exactly; EMEA-lag and hw_rev-B/3.1.2 cluster knobs verified.",
     "findings": [
       {"id": "F-UC-1", "severity": "low", "summary": "Rolled-back rows keep completed_date and duration_min; date-based counts would over-count by 4", "disposition": "accepted: status-based consumers correct; document or blank date at next refresh"}
     ]},
    {"path": "corpus:commercial/internal-financials/gen.py", "verdict": "APPROVED",
     "summary": "FINANCIAL MODEL canonical; deterministic trend + noise on one seeded stream; schema exact; FY2025 $80.5M / 7.9% subscription / FY2026H1 $46.3M verified.",
     "findings": []},
    {"path": "corpus:commercial/internal-revenue-plan/gen.py", "verdict": "APPROVED",
     "summary": "Literal plan table, no rng draws (documented); all plan totals and regulatory-dependency splits re-derived and correct; schema exact, 120 rows.",
     "findings": [
       {"id": "F-RP-1", "severity": "low", "summary": "REGION_SHARE values duplicate FINANCIAL MODEL constants outside any marked shared block", "disposition": "accepted: joins region-insensitive; add keep-in-sync comment at next touch"}
     ]},
    {"path": "corpus:commercial/internal-sales-accounts/gen.py", "verdict": "APPROVED-WITH-FINDINGS",
     "summary": "Both shared blocks byte-identical; fleet burned first, accounts on seed+1; reconciliation and concentration knobs reproduced exactly on snapshot.",
     "findings": [
       {"id": "F-SA-1", "severity": "low", "summary": "Segments beds-derived, not the shared site_segment hash - not row-comparable with winloss/telemetry", "disposition": "accepted: entity types differ by design; add README sentence for BQ authors"},
       {"id": "F-SA-2", "severity": "low", "summary": "NAME_STEMS indexing has no wraparound guard (56 stems, 39 used)", "disposition": "accepted: ample headroom at locked REGIONS"}
     ]},
    {"path": "corpus:commercial/internal-winloss/gen.py", "verdict": "APPROVED-WITH-FINDINGS",
     "summary": "make_fleet + site_segment byte-identical; fleet burned first; prospect identities now stable per id; knobs re-verified on refreshed snapshot 2026-07-27.4.",
     "findings": [
       {"id": "F-WL-1", "severity": "medium", "summary": "PRO-NN region/segment redrawn per opportunity: 14 conflicting segments, 11 conflicting regions across rows", "disposition": "fixed: per-id seeded rng stream gives one stable identity per prospect; refresh 2026-07-27.4 published, 0 conflicts, README knobs re-verified"}
     ]},
    {"path": "corpus:commercial/internal-subscriptions/gen.py", "verdict": "APPROVED",
     "summary": "make_fleet byte-identical, burned first; churned/attach-gap sites and per-site pumps_connected verified against fleet row-for-row on snapshot.",
     "findings": [
       {"id": "F-SU-1", "severity": "low", "summary": "rng2.sample pools (gap 4, churn 3) raise ValueError if knob changes shrink them below k", "disposition": "accepted: pools ~40+ at locked seed; note for knob edits"}
     ]},
    {"path": "corpus:commercial/internal-telemetry-utilization/gen.py", "verdict": "APPROVED",
     "summary": "make_fleet + site_segment byte-identical; device set equals fleet connected exactly; all six underused sites and utilization bands verified to the decimal.",
     "findings": []},
    {"path": "corpus:commercial/internal-regulatory-docket/gen.py", "verdict": "APPROVED",
     "summary": "Deterministic, no clocks, fixed DATA_THROUGH; exactly-2-late and open MDR-2026-0005 knobs verified, including the complaints cross-dataset id tie.",
     "findings": [
       {"id": "F-RD-1", "severity": "low", "summary": "Knob record ids (MDR-2025-0007/0018, MDR-2026-0005) emergent from seed-42 draws, not pinned", "disposition": "accepted: verified at locked seed; re-verify README + complaints tie on any regeneration"}
     ]},
    {"path": "corpus:commercial/internal-signal-register/gen.py", "verdict": "APPROVED-WITH-FINDINGS",
     "summary": "Deterministic; planted rows consume no rng (sound append hygiene); 16/40 died-in-spreadsheet knob verified; planted refs now outside the generated range.",
     "findings": [
       {"id": "F-SR-1", "severity": "medium", "summary": "UPG-0051/0052 each assigned to two signals: planted literals collided with counter-generated refs", "disposition": "fixed: planted refs renumbered UPG-0101/0102 outside the generated range; refresh 2026-07-27.2 published, 0 duplicate refs, ties re-verified"}
     ]}
  ]
}
```
