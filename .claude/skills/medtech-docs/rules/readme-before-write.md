# Rule: Read folder READMEs before writing

Before creating or writing any file into a folder under `docs/`, you MUST read the **target folder's `README.md`** and its **parent folder's `README.md`**.

## Why

The `docs/` hierarchy uses two layers of README guidance:

- **Parent READMEs** define cross-cutting conventions — the document workflow (working markdown vs formal DOCX), information flow between subfolders, tier-level rules, and structural relationships. For example, `design-controls/README.md` defines the waterfall workflow and formal/working doc split that applies to all its children.
- **Leaf READMEs** define folder-specific rules — naming conventions (e.g., `company-device-name.md` vs `YYYY-MM-DD-type-topic.md`), expected content types, formatting and linking rules, and "For Claude" behavioral instructions.

Both layers matter. A file can have the right name for its leaf folder but violate a parent-level convention (e.g., putting a working draft in `formal/`). Misnamed or misplaced files create compliance risk in a regulated project.

## How to apply

1. **Identify the target folder** where the file will be written
2. **Read the parent folder's `README.md`** — look for cross-cutting conventions, information flow, and structural rules
3. **Read the target folder's `README.md`** — look for the Conventions, Expected Content, and For Claude sections
4. **Follow both sets of rules** — the parent conventions apply unless the leaf README explicitly overrides them
5. **Follow the naming convention** specified in the leaf README when choosing the filename
6. **Verify the file type belongs** in that folder per the Expected Content section
7. **Then write the file**

If the target folder is a top-level tier folder (e.g., `docs/external/`), reading just that folder's README is sufficient — there is no meaningful parent beyond `docs/README.md`.

This applies to every Write, Edit, or file creation under `docs/`. It does not apply to `tasks/`, `.claude/`, or other non-docs paths (those have their own conventions defined in their respective skills).

## When a README is missing

If the target folder has no `README.md`:

1. **Stop** — do not write to the folder yet
2. **Flag it to the user** — "This folder is missing a README.md"
3. **Create a README.md** using the meta-model from CLAUDE.md's README Convention section (Title → Structure → Expected Content → Conventions → Changelog). Use the closest sibling or parent README as a reference for style and content
4. **Then proceed** with the original write, now that the README exists to guide future work

This applies to both existing folders that lost their README and new folders being created for the first time. A missing README is a structural gap — every folder under `docs/` must have one per the medtech-docs skill and CLAUDE.md conventions.
