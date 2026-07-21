# The Moster Rules

Principles for **Agentic Software Engineering** — building software *with* AI agents and *for* a world where agents read, write, and run your code.

Each rule lives in its own kebab-case file and follows the same shape: an opening one-sentence `>` blockquote, the principle, why it matters for agentic work, how to apply it, its trade-offs, a litmus test, related rules, and references. This file is the index — when you add a rule, add a row below and copy the rule's blockquote verbatim into its Principle cell.

## Rules

| Rule | Principle |
|------|-----------|
| [Anti-Foot-Gun](anti-foot-gun.md) | Make the dangerous path hard to take by accident. Design footguns out — don't document around them. |
| [Determinism](determinism.md) | Same inputs, same result — every time. Pin the versions, kill the hidden clocks and coin-flips, make behavior reproducible from what's recorded. |
| [Distrust Input](distrust-input.md) | Treat everything crossing a trust boundary as hostile until proven safe. Validate at the edge, by structure — never trust that the caller, the file, or the upstream tool behaved. |
| [Idempotency](idempotency.md) | Make an operation safe to run again and safe to interrupt. Running it twice should be indistinguishable from running it once. |
| [Leave a Trace](leave-a-trace.md) | Make what happened legible after the fact. If you can't see what an actor did, you can't trust it, debug it, or contain it. |
| [Least Privilege](least-privilege.md) | Grant the minimum access needed, for the minimum scope, for the minimum time — and no more. Default to deny; widen only on demonstrated need. |
| [Minimum Necessary Complexity](minimum-necessary-complexity.md) | Build the smallest thing that meets a demonstrated need; add machinery only when reality earns it. |
| [Single Source of Truth](single-source-of-truth.md) | Give each fact one authoritative home; derive, link, or validate every other representation. |
| [Verifiability](verifiability.md) | Define success before acting, then verify the result with independent, observable evidence — not the agent's own assertion. |
