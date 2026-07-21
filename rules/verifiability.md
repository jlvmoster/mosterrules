# Verifiability

> Define success before acting, then verify the result with independent, observable evidence — not the agent's own assertion.

## Principle

To *verify* is to close the loop: state what "done" means in advance, do the work, then confirm the result meets that definition using evidence you can observe from the outside. The two halves are inseparable. A success criterion with no check is a hope; a check with no pre-stated criterion is a rationalization written after the fact to fit whatever happened.

The evidence must be **independent** of the actor's claim. "I updated the file" is an assertion; reading the file back and seeing the new contents is evidence. "The tests pass" is an assertion; the runner's exit code and summary are evidence. The distinction is the whole rule: an actor's report of its own success is exactly the thing you can't trust, because a confused or mistaken actor reports success just as confidently as a correct one.

The move is to make the check *observable and prior*: decide the pass/fail signal before you act, then let the world — a test, a query, a fetched value, an exit code — return it, rather than judging your own work by whether it *feels* finished.

## Why it matters for agentic development

An agent's default failure mode is declaring victory. It will say "Done — the endpoint now returns the user's orders" without ever calling the endpoint, because generating a confident summary is the thing it is best at.

- **Fluent ≠ correct.** A model produces plausible prose about success as easily as the success itself. Confidence carries no information about whether the work landed; only an external check does.
- **Unverified errors compound.** An agent that trusts its own "it worked" builds the next step on a broken one, and the next on that. A closed loop stops the chain at the first failure; an open loop ships a tower of them.
- **The evidence has to be reachable.** Agents act through tools, so "observable" means observable *to a tool* — an exit code, a returned row, a status field, a re-read file — not a screenshot a human happens to glance at.
- **Volume rewards the loop.** A person spot-checks a handful of results and notices a pattern. An agent runs the operation hundreds of times; the only thing that catches the one run that silently failed is a check that runs every time.

## How to apply

- **Write the success criterion first.** Before acting, name the observable signal that will mean success — a specific returned value, an exit code, a row count, a re-read state. Deciding it after the fact is grading your own homework.
- **Verify through an independent channel.** Confirm the result some way *other* than the actor that produced it: re-read what you wrote, re-query what you inserted, run the tests rather than reasoning about them. Prefer the closed loop [anti-foot-gun](anti-foot-gun.md) already builds into this repo — the `ruff`/`ty` gates and the `validate_rules.py` Stop hook that fails the turn when a rule drifts.
- **Make the signal machine-checkable.** A boolean an agent can branch on beats prose it has to interpret. `exit 0`, a returned `200`, `rows == 1` — unambiguous evidence, not "looks right."
- **Prefer executable checks over inspected ones.** A test, an assertion, a schema validation re-runs every time for free; a manual look happens once and rots.
- **On a failed check, stop — don't narrate around it.** A verification that fails is a result, not an obstacle to explain away. Surface it and halt the chain.

## Trade-offs

Verification costs time and machinery, and not every step earns a full harness — re-reading a one-line config edit you can already see in the diff is ceremony. The sharper failure is a **weak oracle**: a check so shallow it passes on wrong output (asserting a function *returns* rather than returns the *right value*) buys false confidence, which is worse than none because it ends the scrutiny. And verification proves you hit the target you *named* — a wrong success criterion verifies perfectly while the real goal fails. Spend the effort where a silent-wrong result would cost the most, and aim the check at the outcome that matters, not the one that's easy to measure.

## Litmus test

> How would I know — from evidence outside the agent's own say-so — that this actually worked, and did I decide what that evidence was *before* I acted?

## Related

- [Anti-Foot-Gun](anti-foot-gun.md) — fail-loud keeps a wrong value from *propagating*; Verifiability is the up-front, closed-loop check that the value is *right* in the first place.
- [Determinism](determinism.md) — an exact-match check needs a result that doesn't change run to run; where it legitimately varies, verify by invariant, range, or property instead. Reproducible-but-wrong is still wrong — Determinism gives repeatability, Verifiability gives correctness.
- [Leave a Trace](leave-a-trace.md) — Verifiability proves success *now*, in the loop; Leave a Trace is the durable record that lets you reconstruct it *later*.
- [Single Source of Truth](single-source-of-truth.md) — SSOT makes a fact *authoritative*; Verifiability checks it's actually *correct* — one authoritative home can still hold a wrong value.
- [Test-Driven Development](test-driven-development.md) — its most direct specialization: Verifiability is the *what* (define success, check it with independent evidence); TDD is one disciplined *when* — write the check first and watch it fail before the code exists. You can verify without testing first; you can't do TDD without verifying.

## References

- [Kent Beck — Test-Driven Development: By Example](https://www.oreilly.com/library/view/test-driven-development/0321146530/) — state the failing check first, then make it pass
- [Google SRE Book — Monitoring Distributed Systems](https://sre.google/sre-book/monitoring-distributed-systems/) — observing a system from the outside
- [Hillel Wayne — The Oracle Problem](https://www.hillelwayne.com/post/hypothesis-oracles/) — how you know an output is *correct*, not just present
