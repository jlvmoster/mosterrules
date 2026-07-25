---
name: new-rule
description: Scaffold a new Moster Rule with the canonical shape and register it in rules/README.md. Use when adding a rule to rules/.
disable-model-invocation: true
---

# new-rule

Create a new Moster Rule and wire it into the index in one step, matching the shape the
`validate_rules.py` hook enforces (see `.claude/hooks/validate_rules.py`).

## Steps

1. **Get the rule.** From the user's argument, settle on a Title and a kebab-case slug
   (e.g. `least-privilege`). If the user didn't give a one-sentence principle, ask for one —
   it becomes the `>` blockquote and is reused **verbatim** in the index, so it must stand
   alone.

2. **Write `rules/<slug>.md`** from the template below. Fill every section with real
   content — placeholders are not acceptable in a committed rule. Match the voice of the
   existing rules (`anti-foot-gun.md`, `idempotency.md`, `least-privilege.md`): define the
   term, state the core move, use concrete examples, keep a calibrated (not absolutist)
   tone. Add a markdown table or a mermaid diagram only where it beats prose.

3. **Register it in `rules/README.md`.** Append a row to the `## Rules` table, copying the
   blockquote **verbatim** into the Principle cell:
   `| [Title](slug.md) | <blockquote text> |`

4. **Cross-link.** Add the new rule to the `## Related` section of any rule it genuinely
   relates to, and link back from the new rule's own `## Related` (reciprocal where it makes
   sense).

5. **Validate.** A `Stop` hook runs `validate_rules.py` at the end of the turn. To check
   now, run `uv run python .claude/hooks/validate_rules.py` and fix any reported drift.

6. **Review (optional).** Dispatch the `rule-reviewer` subagent for a substance-and-style
   pass the structural hook can't do.

## Template

```markdown
# <Title>

> <One-sentence principle — copied verbatim into the README index.>

## Principle

<What the rule is. Define the term; state the core structural move.>

## Why it matters for agentic development

<Why agents make this acute — speed, volume, no instinctive caution, untrusted input.>

- **<Point>.** <...>

## How to apply

- **<Technique>.** <...>

## Trade-offs

<The honest cost and when to relax the rule — not a restatement of the principle.>

## Litmus test

> <One memorable question that operationalizes the rule.>

## Related

- [<Other Rule>](<other-slug>.md) — <why they connect>.

## References

- [<Source>](<url>)
```
