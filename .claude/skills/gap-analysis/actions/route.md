# Action: `route`

Print the recommended advisor agents for a topic.

## Usage

```
/gap-analysis route <topic>
```

## Arguments

- **`<topic>`** (required, positional) — canonical topic key or alias from `data/topic-advisor-map.yml`.

## Steps

1. **Lookup** `<topic>` in `data/topic-advisor-map.yml`:
   - Check `topics:` for an exact match.
   - If not found, check `aliases:` and resolve to the canonical topic.
   - If still not found, list available canonical topics + a fuzzy-match suggestion (string similarity) and exit non-zero.
2. **Render**:
   ```
   Topic: <canonical-topic>  (you asked for <topic>; resolved via alias <alias>)

   Description:
     <full description from data/topic-advisor-map.yml>

   Primary advisors:
     - risk-management          — ISO 14971 risk management; hazard identification; risk control; benefit-risk
     - <other primary>          — <one-line role>

   Consulting advisors:
     - regulatory-affairs       — FDA pathway, predicate, indications, classification
     - clinical-affairs         — clinical evaluation, KOL, user-needs validation

   Typical sources to ground against:
     - <list from typical_sources in the map>
   ```
   The one-line role descriptions for each advisor come from the advisor agent's own definition (`.claude/agents/<name>.md` `description:` field, first sentence) if available, otherwise from the map's own annotations.
3. **Exit zero**.

## Notes

- Advisor agent definitions live under `.claude/agents/<name>.md` (when present locally) or in the registry. The skill does not require local agent definitions to function — the map's `primary[]` / `consulting[]` lists are sufficient for routing recommendations.
- This action is informational. It does not invoke the advisors. Use `/gap-analysis fan-out <id>` to invoke the primary advisor with a specific gap-analysis file's context.

## Example

```
/gap-analysis route fmea
```

Resolves alias `fmea` → canonical topic `risk`. Prints the risk-management + regulatory-affairs + clinical-affairs trio with their descriptions and typical sources.
