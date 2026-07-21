# Leave a Trace

> Make what happened legible after the fact. If you can't see what an actor did, you can't trust it, debug it, or contain it.

## Principle

To *leave a trace* is to emit a durable, readable record of what happened as it happens — what an actor did, when, on whose behalf, with what inputs, and to what result. The record outlives the run: it's there to be queried *after* the fact, by someone who wasn't watching, to answer "what did this do?" without re-running it.

A trace is only as good as it is legible. Unstructured text you have to `grep` and eyeball is a trace in name only; **structured** events — machine-parseable fields, a stable schema, correlation IDs that stitch one logical operation across many steps — are what let you actually reconstruct a sequence and answer a question the record wasn't explicitly designed for.

The move is to treat the record as a **first-class output of the work, not a debugging afterthought**: decide up front what a future reader will need to reconstruct events, and emit it every run — not just the happy path, and not only when someone remembers to turn logging up after something already went wrong.

## Why it matters for agentic development

An agent acts fast, in volume, and out of anyone's direct sight. The trace is often the *only* window into what it actually did.

- **Volume hides the one bad run.** An agent performs an operation thousands of times; the single run that misfired is invisible unless every run leaves a record you can search. There's no human in the loop to remember "that one looked off."
- **You can't reproduce what you can't see.** Debugging an agent's mistake means reconstructing the sequence that led to it — which inputs, which tool calls, which branch. Without a trace, the failure is a black box, and re-running rarely reproduces the exact conditions ([determinism](determinism.md) helps, but only what's recorded can be replayed).
- **Detection is the other half of containment.** [least-privilege](least-privilege.md) *limits* how far a compromised or confused agent can reach; the trace is how you *notice* it reached, and reconstruct the blast radius afterward. Prevention without detection means the one breach you didn't prevent goes unseen.
- **Attribution needs identity.** When many agents and subagents act, "who did this?" only has an answer if each action records the actor and the request it served.

## How to apply

- **Log structured events, not prose.** Emit key–value fields (actor, action, target, result, duration) in a stable schema a query can filter and aggregate — not a sentence a human has to parse. Treat logs as an event stream, not a scratch file.
- **Carry a correlation ID.** Thread one ID through every step of a logical operation — request, tool calls, subagents — so the whole causal chain reassembles from scattered records.
- **Record decisions and inputs, not just outcomes.** "Refunded order 123" is thin; "refunded order 123 because rule X matched, requested by Y, amount Z" is reconstructable. Capture the *why* and the inputs that drove the branch.
- **Make actions attributable.** Stamp each event with the actor and the request it served, so volume stays accountable and one compromised identity is traceable.
- **Emit on every path, especially failure.** The error path is the one you'll most need to reconstruct; log it at least as richly as success. A trace that only records the happy path is missing exactly the runs you'll investigate.
- **Put the trace beyond the actor's reach.** Write to append-only or tamper-evident storage the traced actor can't silently rewrite. A compromised agent that can edit its own logs forges or erases the very record you'd use to catch it — an audit trail an attacker can quietly alter is no audit trail.
- **Never trace secrets; minimize the rest.** Credentials, tokens, and keys never belong in a log — redact them at the source; a log is a durable copy, and a standing one is a [least-privilege](least-privilege.md) liability waiting to leak. Identifiers you *do* need for attribution are often personal data: record the least that answers "who?", prefer a pseudonymous or opaque ID over raw PII, protect it, and give it a retention limit.

## Trade-offs

Tracing isn't free: logs cost storage, throughput, and attention, and a firehose of low-signal events is its own failure — the one line that matters drowns, and cost balloons. Over-tracing also collides with privacy and security: every field written is a field that can leak, so a rich trace and a small secret-exposure surface pull against each other. And a trace records what happened, not whether it was *right* — it's evidence for reconstruction, not a correctness check. Calibrate the signal: log the events and fields a future investigator will actually query, sample or aggregate the high-volume rest, and redact aggressively — richer is not automatically better.

## Litmus test

> When this misbehaves on run #4,712 of 10,000, can I reconstruct exactly what it did and why — from the records it left, without re-running it?

## Related

- [Least Privilege](least-privilege.md) — Least Privilege *limits* the harm a bad run can do; Leave a Trace lets you *detect and reconstruct* it. Prevention and detection are the two halves of bounding blast radius.
- [Anti-Foot-Gun](anti-foot-gun.md) — fail-loud surfaces an error *in the moment*; the trace is the durable, queryable record you consult *afterward*.
- [Verifiability](verifiability.md) — Verifiability is the in-the-loop check that a step *succeeded now*; Leave a Trace is the record that lets you audit *what happened later*.
- [Determinism](determinism.md) — both record for later, to different ends: Leave a Trace records events to *reconstruct what happened*; Determinism records inputs to *reproduce the result*. Audit versus replay.

## References

- [The Twelve-Factor App](https://12factor.net/logs) — factor XI: treat logs as event streams
- [OpenTelemetry — Observability primer](https://opentelemetry.io/docs/concepts/observability-primer/) — traces, metrics, and structured context
- [NIST SP 800-53: AU — Audit and Accountability](https://csrc.nist.gov/projects/cprt/catalog#/cprt/framework/version/SP_800_53_5_1_1/home?element=AU) — the audit-log control family
