# The Moster Rules

Principles for **Agentic Software Development** — building software *with* AI agents and *for* a world where agents read, write, and run your code.

Each rule lives in its own kebab-case file and follows the same shape: an opening one-sentence `>` blockquote, the principle, why it matters for agentic work, how to apply it, its trade-offs, a litmus test, related rules, and references. This file is the index — when you add a rule, add a row below and copy the rule's blockquote verbatim into its Principle cell.

## Rules

| Rule | Principle |
|------|-----------|
| [Anti-Foot-Gun](anti-foot-gun.md) | Make the dangerous path hard to take by accident. Design footguns out — don't document around them. |
| [Idempotency](idempotency.md) | Make an operation safe to run again and safe to interrupt. Running it twice should be indistinguishable from running it once. |
| [Least Privilege](least-privilege.md) | Grant the minimum access needed, for the minimum scope, for the minimum time — and no more. Default to deny; widen only on demonstrated need. |
