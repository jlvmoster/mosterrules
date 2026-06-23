# Idempotency

> Make an operation safe to run again and safe to interrupt. Running it twice should be indistinguishable from running it once.

## Principle

An operation is *idempotent* when applying it more than once has the same effect as applying it once. A process is *disposable* when it can be killed at any moment and restarted without corrupting state or losing work. These are one discipline seen from two angles: design operations so that **repetition is harmless** and **interruption is recoverable**.

The enabler for both is **statelessness** — an operation that carries no hidden, in-process state between calls can be retried, resumed, parallelized, and restarted without coordination.

The key move is to make the *result* depend on the inputs and the target's current state, not on how many times the operation has run or whether a previous run finished. "Create user X" run twice should converge to one user X — not two, and not an error — via an upsert, a unique constraint, or a natural idempotency key, rather than blindly appending.

## Why it matters for agentic development

Agents retry. They act in volume, hit timeouts and partial failures, and their default recovery is to *run it again* — often without knowing whether the first attempt landed. An operation that is not safe to repeat turns every retry into a second side effect: a duplicate charge, a doubled message, a corrupted counter.

- **Retries are the norm, not the exception.** A tool call times out and the agent re-issues it. If the first call already succeeded server-side, a non-idempotent operation has now run twice. The agent feels no flicker of "wait — did that go through?"
- **Partial failure is invisible.** An agent that gets no response cannot tell "never happened" from "happened, response lost." Only an idempotent operation makes that ambiguity safe to resolve by simply retrying.
- **Interruption is routine.** Agent runs get cancelled, contexts reset, processes restart mid-task. Work that cannot resume safely from a partial state is lost or corrupted at every interruption.
- **Volume multiplies the cost.** A non-idempotent edge a human hits once and notices, an agent hits hundreds of times, silently.

So "make it safe to run twice" is not a niche distributed-systems nicety — it is what lets an agent recover from its own retries without doing damage.

## How to apply

- **Converge to a state; don't blindly apply a delta.** Prefer `set quantity = 5` over `add 1`, and upsert over insert. State-convergent operations are idempotent by construction.
- **Use idempotency keys for unavoidable side effects.** When the action genuinely creates something external (a payment, an email), let the caller pass a key the operation deduplicates on, so a retry with the same key is a no-op that returns the original result.
- **Keep operations stateless.** Hold no required state in process memory between calls; derive everything from inputs and durable storage.
- **Design for interruption.** Assume the process can die at any point. Use transactions or atomic writes so a partial run leaves no half-applied state, and checkpoint long work so it resumes instead of restarting from zero.
- **Make retry the safe default for tools you hand an agent.** A tool should be retryable without the caller having to remember whether it already ran — the safety lives in the operation, not in the caller's memory.
- **Isolate and guard the genuinely non-idempotent core.** Where an operation truly cannot be made idempotent, name that, and put [anti-foot-gun](anti-foot-gun.md) guardrails on it (explicit opt-in, confirmation) so a reflexive retry can't reach it.

## Anti-patterns

| Footgun | Idempotent |
|---------|------------|
| `balance += amount` applied per call | `balance` derived from durable state, or deduped on an idempotency key |
| `INSERT` that duplicates or errors on the second run | `UPSERT`, or insert guarded by a unique constraint |
| A `send_email(...)` tool an agent retries into duplicate sends | Dedup on a message key; a retry returns the original send |
| Required state held in process memory between calls | State in durable storage; the process carries none |
| A long job that restarts from zero after a crash | Checkpointed, transactional work that resumes from the last good point |
| "Don't run this twice" in a docstring | An operation that *is* safe to run twice |

## References

- [The Twelve-Factor App](https://12factor.net/) — esp. factor VI (stateless processes) and factor IX (disposability)
- [Idempotence — Wikipedia](https://en.wikipedia.org/wiki/Idempotence)
- [Stripe: Idempotent Requests](https://docs.stripe.com/api/idempotent_requests)
