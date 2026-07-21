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

## How to apply

- **Safe defaults.** The default behavior is the correct, conservative one; the dangerous behavior requires an explicit, deliberate flag (`--force`, `--no-verify`, `allow_destructive=True`). A mutable default argument (`def f(x=[])`) is the failure in miniature — the unsafe form is the path of least resistance; `def f(x=None)` then `if x is None: x = []` makes the safe form the default, and a linter flags the unsafe one (Ruff's `B006`, for instance).
- **Make misuse a hard error.** Push violations as early as possible: a type error, a lint rule, a failing CI gate, a schema rejection. Earlier and louder beats later and quieter.
- **Constrain the interface.** Give agents and callers narrow, purpose-built tools instead of broad, powerful ones. A `delete_draft(id)` is safer than handing over raw SQL, and denying direct edits to a generated artifact (a lockfile, a build output) steers changes through the tool that owns it. Make illegal states unrepresentable — but only for invariants that genuinely never change, or it trades real flexibility for type-gymnastics.
- **Require explicit opt-in for irreversible actions.** Deleting, overwriting, publishing, or sending to the outside world should demand confirmation or a distinct, intentional call — never a default or a side effect.
- **Fail loud, not silently wrong.** The dangerous case is the *quietly wrong* result — return an error, not a plausible-looking empty value, so a bad value can't propagate down the chain.

| Footgun (easy, unsafe) | Why it bites an agent | Structural fix (safe by default) |
|---|---|---|
| `def f(x=[])` mutable default | shared state mutates across calls, silently | `def f(x=None)` + `if x is None: x = []`; Ruff `B006` flags it |
| "remember to close it" in a docstring | prose is out-of-context mid-task | scope-bound resource: context manager / `defer` / RAII |
| raw SQL / admin connection handed over | whatever the interface allows, an agent will do | narrow tool: `delete_draft(id)`, not arbitrary SQL |
| returns `[]` / `None` on a bad lookup | a quietly-wrong value propagates down the chain | raise or return an error — fail loud |
| destructive action as default or side effect | a reflexive call deletes or publishes | explicit opt-in: `--force`, `allow_destructive=True` |

## Trade-offs

Every guardrail has a false-positive cost. If the safe path is too noisy or the override too routine, callers — agents especially — reflexively reach for `--force` / `--no-verify`, and the footgun just moves to the override. Keep the escape hatch deliberate: scope a suppression to the single rule, not a wholesale silencing — a guardrail that's always bypassed is documentation with extra steps.

Failing loud is itself a per-component call: critical paths should fail fast, but graceful degradation, retries, and fallbacks are correct on non-critical ones — as long as the degradation stays *visible*, never a silently-swapped wrong answer.

## Litmus test

> If an agent ran this on autopilot, what's the worst it could do *by default* — and does the dangerous path demand a deliberate, explicit step (a flag, a distinct call, a confirmation)?

## Related

- [Idempotency](idempotency.md) — put guardrails on the genuinely non-idempotent core so a reflexive retry can't reach it.
- [Least Privilege](least-privilege.md) — the same interface-narrowing move, applied to *authority* rather than *shape*.
- [Distrust Input](distrust-input.md) — this narrows the interface's *shape*; Distrust Input validates the *values* that flow through it, and shares the fail-loud reflex.
- [Verifiability](verifiability.md) — fail-loud stops a quietly-wrong value from propagating; Verifiability is the up-front, closed-loop check that the value is right.
- [Single Source of Truth](single-source-of-truth.md) — routing edits of a generated artifact through the tool that owns it is that rule made structural: the derived copy can't be hand-edited, so it can't drift from its source.

## References

- [Avoiding Footguns — Matt Rickard](https://mattrickard.com/avoiding-footguns)
