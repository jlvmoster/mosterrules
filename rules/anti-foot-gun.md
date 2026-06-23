# Anti-Foot-Gun

> Make the dangerous path hard to take by accident. Design footguns out — don't document around them.

## Principle

A *footgun* is any feature, API, command, or workflow that is easy to misuse in a way that hurts you — "shooting yourself in the foot." The anti-foot-gun principle is the discipline of shaping systems so the unsafe path is **hard, loud, or impossible**, while the safe path is the **default**.

The key move is structural, not advisory. A comment that says "don't call this without closing the connection" is not a guardrail — it's a footgun with a warning label. The fix is to make forgetting impossible (a context manager, a `defer`, an API that closes itself) or to make it fail immediately and loudly.

## Why it matters for agentic development

Agents amplify footguns. They act fast, in volume, and without the situational caution a human applies on instinct. A sharp edge a careful developer steps around once a month, an agent will hit at scale and without hesitation:

- **No instinctive caution.** An agent will happily run `rm -rf`, force-push, or drop a table if the interface lets it and nothing stops it. It does not feel the flicker of doubt a human feels.
- **Documentation is weak protection.** Prose warnings buried in a README or a docstring are routinely out-of-context for an agent mid-task. Constraints that live in *types, tools, and gates* travel with the code; prose does not.
- **Silent failure compounds.** An agent that gets a quietly-wrong result keeps building on it. A loud failure stops the chain; a silent one ships.
- **The interface is the contract.** Whatever a tool, function, or command *allows*, an agent will eventually *do*. Narrow the interface and the wrong action becomes unrepresentable.

So in agentic work, "make it hard to misuse" is not politeness — it's the primary safety mechanism, because the actor on the other end will take any path you leave open.

## How to apply

- **Safe defaults.** The default behavior is the correct, conservative one. The dangerous behavior requires an explicit, deliberate flag (`--force`, `--no-verify`, `allow_destructive=True`).
- **Make misuse a hard error.** Push violations as early as possible: a type error, a lint rule, a failing CI gate, a schema rejection. Earlier and louder beats later and quieter.
- **Constrain the interface.** Give agents and callers narrow, purpose-built tools instead of broad, powerful ones. A `delete_draft(id)` is safer than handing over raw SQL. Make illegal states unrepresentable.
- **Require explicit opt-in for irreversible actions.** Deleting, overwriting, publishing, or sending to the outside world should demand confirmation or a distinct, intentional call — never a default or a side effect.
- **Fail loud, never silent.** Raise, don't swallow. Return an error, not a plausible-looking empty result. A footgun you can see beats one you discover in production.
- **Guardrails over documentation.** If the only thing stopping misuse is a comment, it will be missed. Encode the rule where the work happens.

## Anti-patterns

| Footgun | Anti-foot-gun |
|---------|---------------|
| Mutable default argument: `def f(x=[])` | `def f(x=None)` then `x = x or []` — caught by lint (`B006`) |
| A tool/command that deletes with no confirmation | Confirmation prompt, dry-run default, or a soft-delete that's reversible |
| Catching an exception and returning `None` | Let it raise, or return an explicit typed error |
| One broad `run_sql(query)` tool exposed to an agent | Narrow, intent-specific operations the agent cannot misuse |
| "Don't forget to close the connection" in a docstring | A context manager that closes it for you |
| Type errors as warnings developers learn to ignore | A `type check` gate in the commit/edit path that must pass |

## In this project

The anti-foot-gun principle is already wired into how this repo is built:

- `ty check` runs in the post-edit hook and before commits, so type errors fail loud instead of sliding through.
- Suppression is narrowed to rule-specific `# ty: ignore[rule]` rather than blanket ignores — the escape hatch is deliberate and visible.
- `uv.lock` is denied to direct edits, so the lockfile can only change through the proper `uv` path.

## References

- [Avoiding Footguns — Matt Rickard](https://mattrickard.com/avoiding-footguns)
- [footgun — Wiktionary](https://en.wiktionary.org/wiki/footgun)
- [Footgun — GDQuest Glossary](https://school.gdquest.com/glossary/footgun)
