# Agent & Skill Design Principles

Shared design principles for building agents and skills in this project. Referenced by the `/best-practices` audit and should be consulted when creating or reviewing any skill that evaluates, compares, routes, or classifies content.

## Principle 1: Two-Tier Evaluation (Programmatic + Semantic)

Any agent or skill that makes judgments about content should combine both mechanical and reasoned evaluation.

### Why

Programmatic checks alone miss cases where different wording expresses the same intent. "Filing Sequence Strategy" and "Submission Order and Timing" have zero word overlap but address the same decision. Semantic checks alone are expensive, non-deterministic, and unnecessary when a simple rule suffices.

### The Pattern

| Tier | Type | When It Fires | How It Works | Cost |
|------|------|---------------|-------------|------|
| 1 | Programmatic | Always | Pattern matching, word overlap, structural rules, keyword detection | Cheap, deterministic |
| 2 | Semantic | When Tier 1 is inconclusive or when content is scoped to the same category | Agent reads content and reasons about meaning, intent, equivalence | More expensive, uses LLM judgment |

### How to Apply

1. **Start with programmatic rules** — define the mechanical checks that catch obvious cases (exact matches, high word overlap, structural patterns)
2. **Define a scope boundary for semantic checks** — don't compare everything against everything. Use Tier 1 or structural routing to narrow the comparison set (e.g., "same output section", "same category", "same tag domain")
3. **Add semantic evaluation within that scope** — the agent reads content and assesses whether items that passed Tier 1 but landed in the same scope are truly related
4. **Document both tiers** in the skill's SKILL.md or agent prompt — what each tier catches, how they interact, and what triggers the semantic check

### Examples

**Strategy skill conflict detection:**
- Tier 1: >80% word overlap in `### ` heading text → conflict
- Tier 2: Two subsections from different tasks routed to the same output section with different headings → agent reads both, assesses if they address the same decision

**Future — lessons learned deduplication:**
- Tier 1: Identical lesson title → duplicate
- Tier 2: Two lessons in the same category with different titles → agent reads both, assesses if they capture the same insight

**Future — requirements traceability:**
- Tier 1: Explicit trace ID references (REQ-001 → TEST-001) → traced
- Tier 2: Requirements and test cases in the same functional area without explicit traces → agent reads both, assesses if implicit coverage exists

### Anti-Patterns

- **Semantic-only**: Running LLM reasoning on every comparison when simple rules would catch 90% of cases. Wasteful and slow.
- **Programmatic-only**: Relying entirely on word matching or regex. Misses semantically equivalent content with different wording.
- **Unscoped semantic checks**: Comparing every item against every other item semantically. Use structural boundaries (sections, categories, domains) to scope the comparison set.

## Principle 2: Interactive Resolution with Persistent State

When an agent detects an ambiguity or conflict that requires human judgment, it should:

1. **Surface the issue clearly** — show the user what was detected, with enough context to decide
2. **Offer concrete options** — not open-ended "what do you want to do?" but specific choices with defined outcomes
3. **Record the decision in source files** — using machine-readable markers that survive regeneration
4. **Re-prompt unresolved items** — deferred decisions are re-surfaced on the next run, not silently forgotten

### Why

Agents that silently make judgment calls create invisible drift. Agents that surface every issue once and then forget create a false sense of resolution. The pattern of "prompt → decide → record → re-prompt if unresolved" ensures nothing falls through the cracks while keeping the human in control.

### Examples

- Strategy assembler: conflict detected → prompt lead with 3 options → write review marker to source task → pending markers re-prompt next assembly
- Future — risk analysis: overlapping hazards detected → prompt risk manager → record resolution in risk register → unresolved items appear in next review

## Principle 3: Self-Contained Agent Prompts

Subagent prompts (in `agents/` directories) must be fully self-contained. They should include all conventions, rules, and context needed to execute — not rely on the parent session's context or SKILL.md being read first.

### Why

Subagents start with no context. If the prompt says "follow the tag convention" but doesn't define it, the subagent will guess or fail. Template variables (e.g., `{{DOMAIN_KEY}}`) allow the parent to inject runtime values while keeping the prompt self-contained.

### How to Apply

- Include all relevant conventions inline in the agent prompt
- Use template variables for runtime values the parent provides
- Test by reading the agent prompt in isolation — could you execute it without reading anything else?

## Documenting Design Tiers in Skills

Every skill that uses agents or makes evaluative judgments should include a section in its SKILL.md (or in its agent prompts) that documents:

1. **What decisions the skill makes** (conflict detection, routing, classification, deduplication, etc.)
2. **Tier 1 — Programmatic rules**: What mechanical checks are applied, their thresholds, and what they catch
3. **Tier 2 — Semantic evaluation**: What triggers the semantic check, how it's scoped, and what the agent assesses
4. **How they interact**: Does Tier 2 only fire when Tier 1 is inconclusive? Does Tier 1 narrow the scope for Tier 2?

This documentation is checked by the `/best-practices` audit.
