---
pack_name: table-positional
version: 0.1-stub
applies_to_type: t-4
emit_mode: html
status: stub
---

# table-positional

**STATUS (2026-04-21)**: Phase A scaffold stub under task ben/089. Populated in Phase D.

## Purpose

See `references/table-rule-packs/README.md` for the full pack registry. This pack covers source-table type `t-4` with emit mode `html`.

## Current authoritative source

Today's rules for this table type live in `agents/converter.md` Phase 3 (Tables / R1 / T1 sub-sections). Phase D extracts the relevant sub-rules into this file without rewriting them. Until then, the orchestrator falls back to converter.md Phase 3 directly.

## Scope (to be populated in Phase D)

(stub)

## Source probe signature (to be populated in Phase D)

How `scripts/classify_tables.py` (Phase D) identifies this table type from `word/document.xml` / PDF table machinery.

## Emission template (to be populated in Phase D)

How `agents/interpret_table.md` (Phase D) emits this table type when the script can't resolve deterministically.

## Changelog

- 2026-04-21: Stub created during task ben/089 Phase A scaffolding.
