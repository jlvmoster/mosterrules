# Determinism

> Same inputs, same result — every time. Pin the versions, kill the hidden clocks and coin-flips, make behavior reproducible from what's recorded.

## Principle

A computation is *deterministic* when the same inputs always produce the same output. A build, a test, or a function is *reproducible* when anyone can re-run it from what's recorded — pinned versions, captured config, committed inputs — and get an identical result. One discipline: make the output a pure function of *declared* inputs, and eliminate the *undeclared* ones.

The undeclared inputs are what break it — the hidden dependencies a computation reads without saying so: the wall clock, the random seed, `now()`, an unpinned dependency resolved fresh each run, map iteration order, ambient environment variables, the response of a live network call. Each is a silent argument that changes between runs, so the "same" invocation quietly isn't.

The move is to **pull every hidden input into the open**: pass the clock and the seed as arguments, pin dependencies to exact versions in a lockfile, sort what has no inherent order, and record the inputs alongside the output so a run can be reproduced rather than merely re-attempted. This repo lives it — Python pinned to `3.14.3` in `.python-version`, dependencies frozen in `uv.lock`, the same `ruff`/`ty` gates on every machine.

## Why it matters for agentic development

An agent can't shrug off flakiness the way a human does. A person re-runs a failing test, sees it pass, and moves on; an agent has no instinct for "probably just flaky" and no memory that it saw green a moment ago.

- **Nondeterminism weakens verification.** A result that varies run to run has no stable target for an *exact-match* check ([verifiability](verifiability.md)) — you can still test invariants, ranges, or distributions, but the cheap, decisive "is it exactly this?" is gone. If "success" flickers, the agent can't tell a real regression from noise, and every downstream decision inherits the doubt.
- **Flaky signals train the wrong reflex.** Faced with an intermittently-failing gate, an agent learns to retry until green — laundering a real failure into a pass, exactly the [anti-foot-gun](anti-foot-gun.md) over-noisy-guardrail trap.
- **"Works here" doesn't transfer.** An agent generates code in one environment and it runs in another. Unpinned versions and ambient state mean the reproduction diverges from the original, and the bug that only appears in one is nearly impossible for an agent to chase.
- **Volume surfaces every hidden input.** A one-in-a-thousand ordering fluke a human never notices, an agent running the operation thousands of times will hit — and act on.

## How to apply

- **Pin what you run; range what you publish.** An application or test suite pins exact versions in a lockfile so one dependency graph resolves everywhere, this month and next — what `uv.lock` and a pinned interpreter buy this repo. A *published library* instead declares compatible ranges in its metadata and lets the consumer's lockfile do the pinning — a `requires-python = ">=3.14.3"`-style constraint is that range mechanism. Digests over floating tags either way.
- **Inject the clock and the randomness.** Pass `now` and the seed in as arguments (or a fixed seed in tests) instead of reaching for `datetime.now()` or an unseeded RNG mid-computation. A function that reads the wall clock has an invisible parameter.
- **Order what has no order.** Sort before you serialize or hash; don't depend on set/dict/filesystem iteration order or on concurrent completion order.
- **Isolate the impure edge.** Push network calls, time, and randomness to the boundary; keep the core a pure function of its arguments. Record real responses (scrubbed of secrets) so a rerun replays them instead of re-fetching.
- **Capture inputs with outputs — but redact first.** Log or commit the versions, config, and seed that produced a result, so "reproduce it" is possible from the record rather than from memory. A recorded response or captured config is a durable, replayable copy, so strip tokens, cookies, connection strings, and personal data — or store an opaque reference — before it lands ([leave-a-trace](leave-a-trace.md)). If a redacted value actually *drives* the output, you trade exact replay for the scoped reproducibility Trade-offs already allows.

| Hidden input | How it leaks | Make it declared |
|---|---|---|
| wall clock | `now()` mid-logic | pass `now` as an argument |
| randomness | unseeded RNG | inject a seed; fix it in tests |
| dependency drift | `^1.2` resolves fresh | lockfile with exact versions/digests |
| iteration order | set/dict/filesystem order | sort before serialize or hash |
| live network | fetch during compute | fetch at the edge; record and replay |

## Trade-offs

Full determinism isn't always reachable or worth it. Wall-clock time, real randomness (a UUID, a crypto nonce), and live external data are sometimes the *point* — the fix is to inject and record them, not to pretend they're constant. Pinning has a maintenance cost: frozen dependencies drift out of date and need deliberate, reviewed bumps, which is a feature (upgrades become intentional) with a real upkeep price. And reproducibility can be scoped — bit-for-bit identical builds are expensive; often "same observable result" is enough. Spend the rigor where a varying result would silently corrupt a decision, and let genuinely-random things be random, but *recorded*.

## Litmus test

> If I run this again next month on another machine, from only what's committed, do I get a byte-for-byte identical result — and if not, exactly which unrecorded input changed?

## Related

- [Idempotency](idempotency.md) — the sibling, on a different axis. Idempotency makes a repeated *side effect* harmless (a retried charge doesn't double); Determinism makes the same inputs produce the same *output*. One is about safe repetition of an effect, the other about reproducibility of a result — you can want either without the other.
- [Verifiability](verifiability.md) — an *exact-match* check needs a stable result, and Determinism is what gives it a fixed target; where output is legitimately variable, Verifiability falls back to checking invariants and properties instead.
- [Leave a Trace](leave-a-trace.md) — both record for later, to different ends: Determinism records inputs to *reproduce a result*; Leave a Trace records events to *reconstruct what happened*. Replay versus audit.
- [Test-Driven Development](test-driven-development.md) — red-green only carries information if the target holds still: a flaky test has no fixed red or green to drive from, so test-first quietly depends on a deterministic result to check against.

## References

- [Reproducible Builds](https://reproducible-builds.org/) — a set of practices for verifiable, bit-for-bit-identical builds
- [The Twelve-Factor App](https://12factor.net/) — factor II (explicitly declared, isolated dependencies)
- [Bazel — Hermeticity](https://bazel.build/basics/hermeticity) — builds as pure functions of their declared inputs
