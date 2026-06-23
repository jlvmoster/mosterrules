# The Moster Rules

Principles for **Agentic Software Development** — building software *with* AI agents and *for* a world where agents read, write, and run your code.

Each rule lives in its own file and follows the same shape: a one-line statement, the principle, why it matters for agentic work, how to apply it, and anti-patterns to avoid. This file is the high-level index — keep it in sync when adding a rule.

## Rules

| # | Rule | Principle |
|---|------|-----------|
| 1 | [Anti-Foot-Gun](anti-foot-gun.md) | Make the dangerous path hard to take by accident; design footguns out instead of documenting around them. |
| 2 | [Idempotency](idempotency.md) | Make an operation safe to run again and safe to interrupt; running it twice equals running it once. |

## Conventions

- **One rule per file**, named in kebab-case after the principle (e.g. `anti-foot-gun.md`).
- Each rule opens with a `>` blockquote stating the rule in a single sentence.
- Add a row to the table above whenever you add a rule; keep the numbering stable.
