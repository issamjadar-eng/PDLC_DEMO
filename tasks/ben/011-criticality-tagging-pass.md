# 011 — Criticality Tagging Pass (CtS / CtF / CtC / CtP)

**ID**: 011
**Created**: 2026-04-14
**Status**: Not Started
**Created By**: Ben Xavier
**Owner**: Ben Xavier
**Priority**: High

---

## Goals

_Apply the criticality carve-out decided in task 006 to the existing PCA device user needs and design inputs. Every UN and DI gets one or more of CtS / CtF / CtC / CtP tags (or none, marking it commercial-only). The tag set drives 510(k) + PCCP filing scope and the V&V split._

- Define the four tag values formally in the project glossary or a new `criticality-tags.md` reference
- Tag all 22 UNs in `docs/project/dhfs/pca-device/design-controls/user-needs/user-needs.md`
- Tag all 34 DIs in `docs/project/dhfs/pca-device/design-controls/requirements/design-inputs.md`
- Add a "Filing Scope" column to `un-to-di-trace-matrix.md` derived from the tags (`In 510(k)`, `In PCCP envelope`, `Commercial-only`)
- Sanity-check: every CtS-tagged UN traces to at least one CtS-tagged DI (no orphan safety-critical needs)
- Surface any UN/DI that the tagging pass reveals as ambiguous → flag for review with the user

## References

| Ref | Description | Location |
|-----|-------------|----------|
| Source decision | Filing Strategy — Critical-Requirement Carve-out | `tasks/ben/006-architecture-regulatory-strategy.md` |
| User needs | 22 UNs in 9 functional groups | `docs/project/dhfs/pca-device/design-controls/user-needs/user-needs.md` |
| Design inputs | 34 DIs in 9 functional groups | `docs/project/dhfs/pca-device/design-controls/requirements/design-inputs.md` |
| Trace matrix | Bidirectional UN↔DI | `docs/project/dhfs/pca-device/design-controls/trace-matrix/un-to-di-trace-matrix.md` |

## Changelog

- 2026-04-14: Task created. Spawned from task 006 Filing Strategy decision.
