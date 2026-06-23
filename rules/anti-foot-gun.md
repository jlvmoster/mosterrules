# Anti-Foot-Gun

> Make the dangerous path hard to take by accident. Design footguns out — don't document around them.

## Principle

A *footgun* is any feature, API, command, or workflow that is easy to misuse in a way that hurts you — "shooting yourself in the foot." The anti-foot-gun principle is the discipline of shaping systems so the unsafe path is **hard, loud, or impossible**, while the safe path is the **default**.

The key move is structural, not advisory. A comment that says "don't call this without closing the connection" is not a guardrail — it's a footgun with a warning label. The fix is to make forgetting impossible — a scope-bound resource (a context manager, `defer`, RAII, try-with-resources) or an API that closes itself — or to make the mistake fail immediately and loudly.

## Why it matters for agentic development

Agents amplify footguns. They act fast, in volume, and without the situational caution a human applies on instinct. A sharp edge a careful developer steps around once a month, an agent will hit at scale and without hesitation:

- **No instinctive caution.** An agent will happily run `rm -rf`, force-push, or drop a table if the interface lets it and nothing stops it. It does not feel the flicker of doubt a human feels.
- **Documentation is weak protection.** Prose warnings buried in a README or a docstring are routinely out-of-context for an agent mid-task. Constraints that live in *types, tools, and gates* travel with the code; prose does not.
- **Silent failure compounds.** An agent that gets a quietly-wrong result keeps building on it. A loud failure stops the chain; a silent one ships.
- **The interface is the contract.** Whatever a tool, function, or command *allows*, an agent will eventually *do*. Narrow the interface and the wrong action becomes unrepresentable.

So in agentic work, "make it hard to misuse" is not politeness — it's the primary safety mechanism, because the actor on the other end will take any path you leave open.

## How to apply

- **Safe defaults.** The default behavior is the correct, conservative one. The dangerous behavior requires an explicit, deliberate flag (`--force`, `--no-verify`, `allow_destructive=True`).
- **Make misuse a hard error.** Push violations as early as possible: a type error, a lint rule, a failing CI gate, a schema rejection. Earlier and louder beats later and quieter. A check that is only a documented convention rather than an enforced gate is the weakest form of this — a post-hoc, loud signal still beats nothing, but a real gate beats a prose reminder.
- **Constrain the interface.** Give agents and callers narrow, purpose-built tools instead of broad, powerful ones. A `delete_draft(id)` is safer than handing over raw SQL. Make illegal states unrepresentable — but scope it to invariants that genuinely never change; pushed too far, it trades real flexibility for type-gymnastics around constraints the domain doesn't actually hold.
- **Require explicit opt-in for irreversible actions.** Deleting, overwriting, publishing, or sending to the outside world should demand confirmation or a distinct, intentional call — never a default or a side effect.
- **Fail loud, not silently wrong.** The dangerous case is the *quietly wrong* result — return an error, not a plausible-looking empty value, so a bad value can't propagate down the chain. This is not a blanket ban on recovery: graceful degradation, retries, and fallbacks are correct for non-critical paths. The rule is that degradation must be *visible*, never a silently-swapped wrong answer. Fail-fast vs. degrade-gracefully is a per-component call based on criticality.
- **Calibrate, or the guardrail becomes the footgun.** Every gate has a false-positive cost. If the safe path is too noisy or the override too routine, callers — agents especially — learn to reflexively reach for `--force` / `--no-verify`, and the footgun just moves to the override. "Whatever a tool allows, an agent will do" cuts both ways: the escape hatch is part of the interface too. A guardrail that's always bypassed is documentation with extra steps.
- **Keep the escape hatch deliberate and visible.** When you do provide an override or a suppression, narrow it to the specific case rather than a blanket bypass — a suppression scoped to a single rule, not a wholesale silencing — so each use is intentional and auditable.
- **Steer changes through the safe workflow.** Denying direct edits to generated artifacts (a lockfile, a build output) steers changes through the tool that owns them. Note the limit: a deny scoped to the editing path narrows the obvious door, not every door — a determined raw shell write can still get through, so treat it as a strong nudge, not an airtight seal.
- **Guardrails over documentation.** If the only thing stopping misuse is a comment, it will be missed. Encode the rule where the work happens.

## Anti-patterns

| Footgun | Anti-foot-gun |
|---------|---------------|
| Mutable default argument: `def f(x=[])` | `def f(x=None)` then `if x is None: x = []` — caught by lint (`B006`) |
| A tool/command that deletes with no confirmation | Confirmation prompt, dry-run default, or a soft-delete that's reversible |
| Catching an exception and returning `None` | Let it raise, or return an explicit typed error |
| One broad `run_sql(query)` tool exposed to an agent | Narrow, intent-specific operations the agent cannot misuse |
| "Don't forget to close the connection" in a docstring | A context manager that closes it for you |
| Type errors as warnings developers learn to ignore | A `type check` gate in the commit/edit path that must pass |
| A blanket suppression that silences a whole category | A suppression narrowed to a single rule at the exact site |
| A guardrail so noisy that `--force` becomes a reflex | A gate tuned to low false positives, with a rare, audited override |

## References

- [Avoiding Footguns — Matt Rickard](https://mattrickard.com/avoiding-footguns)
- [footgun — Wiktionary](https://en.wiktionary.org/wiki/footgun)
- [Footgun — GDQuest Glossary](https://school.gdquest.com/glossary/footgun)
