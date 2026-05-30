# Rule: Read the Contract Before Reasoning About Behavior (HARD RULE)

When you reason about how another component behaves — a sibling skill, an agent, a schema, a config file, a script — **read its contract first**. The contract is whatever document defines its behavior: a SKILL.md, an agent prompt file, a JSON/YAML schema, a README, a docstring, a frontmatter block, source code at the load-bearing function. Do not reason from "components like this typically…", from memory of similar patterns, or from the component's name alone.

The principle in one line: a design built on an **invented premise** about another component's behavior is wallpaper over a wrong wall, even if the design itself is rigorous.

## Why this matters

LLM reasoning produces analyses that **look rigorous on top of any premise** — option tables, tradeoff matrices, leans, recommendations. The analytical scaffold doesn't expose the soundness of its foundation. If the foundation is invented, the option table is invented; if a "lean" is recommended on the wrong basis, the user spends real time evaluating an unreal choice.

Two biases compete with this rule in practice:

1. **"I can reason about this from pattern memory."** True for the well-known and the trivial; dangerous when the canonical contract disagrees with the pattern. The canonical source is always cheaper to consult than to recover from. Reading `SKILL.md` once is ~30 seconds; correcting a wrong analysis is multiple turns.
2. **"I'll sanity-check the premise at the end."** Almost never happens — by the time the analysis is written, the premise has framed every option and every tradeoff. Sanity-checking after the fact requires re-doing the whole analysis.

## How to apply

1. **Identify the contract.** Before writing any claim about how another component behaves, name the file that defines it (SKILL.md / README / schema / source / agent prompt / frontmatter). If you cannot name the contract, stop and find it.
2. **Read the load-bearing section.** Not the whole file — the specific section that governs the claim. Use grep to locate keywords first.
3. **Cite specific lines when describing behavior.** Write "per SKILL.md L207" or "per the schema's `status` enum at line N" — not "as I understand it" or "components like this usually…". The citation IS the evidence that the rule was followed.
4. **Treat absence of citation as the signal to go read.** When you find yourself writing a claim about another component without a line reference, stop and read before continuing.

## What counts as a "contract"

| Component type | Contract location |
|---|---|
| Skill | `SKILL.md` frontmatter + § Actions; sometimes `README.md` for design rationale |
| Agent | The agent's prompt file under `.claude/agents/` or `.claude/skills/<x>/agents/` |
| Config schema | The YAML/JSON file itself + any accompanying README that documents its fields |
| Script / tool | Module-level docstring, CLI `--help` output, or source-code entry point |
| Hook | The hook script + the SKILL.md section that registers and documents it |
| MCP server | Tool-list manifest + per-tool docstrings |
| Document template | The template file under `templates/` + the README that explains when it's used |
| Workflow / action | The specific § Action block in the owning skill's SKILL.md |

If the contract is genuinely missing (a component with no documented behavior), that's its own finding — flag it rather than inventing the contract from inference.

## Examples

❌ **Inventing behavior in an option table.** Writing "Option F: assume sibling skill regenerates wholesale, so apply fixes only to non-regenerated docs" without ever opening the sibling skill's SKILL.md. The whole option table inherits the unread premise.
✅ Open the sibling skill's SKILL.md, grep for `regenerate|overwrite|hand-edit|preserve`, read the load-bearing section, then write the option table on a foundation that includes "per SKILL.md L<N>, the assembler does X."

❌ **Designing an integration around an agent's behavior from its name.** Writing "the `risk-management` agent decides X based on hazard severity" without reading the agent's prompt file. The agent's prompt may not behave that way at all.
✅ Read `.claude/agents/risk-management.md`. Find the section that governs the claim. Cite the specific paragraph.

❌ **Reasoning about a schema's allowed values from prose memory.** Writing "the `status` field accepts `active | pending | superseded`" without reading the schema. The actual enum may differ — and the wrong value may have been silently accepted by a permissive parser.
✅ Open the schema or the controller code that validates the field. Quote the enum.

✅ **Appropriate inference — clearly labeled.** When a contract is silent on an edge case, *explicit inference* ("the contract is silent on case X; I'm inferring behavior Y from the surrounding pattern at lines A–B") is fine — the label warns the reader that this part is inferred, not authoritative, and the line range tells them where to look to verify.

## Sibling rule

[`audit-wiring-before-adding-fields.md`](audit-wiring-before-adding-fields.md) codifies the **authoring-time** counterpart: ground in canonical config before authoring new metadata/schema. This rule is the **design-time** counterpart: ground in canonical contracts before authoring integration design. Together they make "ground in the canonical source instead of inventing" the default for both kinds of work — declarative wiring and behavioral contracts.
