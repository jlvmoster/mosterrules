# Test-Driven Development

> Write the failing test first. The test is the specification; the code is what satisfies it.

## Principle

Test-Driven Development inverts the usual order: the check comes *before* the code. You write a test that describes the behavior you want, then the smallest code that makes it pass. The discipline lives in the *ordering*, not in the tests themselves. A test written after the code tends to assert whatever the code already does — it documents the implementation instead of constraining it.

The move is to let the failing test *drive*: it names the next increment of behavior, gives the code a fixed target to hit, and — once green — becomes the fixture that lets you change the design without changing what it does.

## Why it matters for agentic development

[Verifiability](verifiability.md) is the parent *what* — define success and check it with independent evidence. TDD is one disciplined *when*: write the check first. You can verify without testing first; you can't do TDD without verifying.

- **Red-first defeats the vacuous test.** An agent told to "add tests" will happily write one that passes against the current code without exercising anything. A test that never failed proves nothing; deleting the implementation and seeing red is how you know it can catch a regression.
- **The test is a spec a human can review.** For agent-written code a reviewer won't read line by line, the test states the intended behavior in a form they *can* check — and that re-runs on every future change, not just at review time.

## How to apply

- **Write the test before the code.** State the behavior as a failing test first. An unexpected green means either the behavior already exists — so this step needs no new code — or the test isn't exercising what you think. Find out which before you write more code.
- **Write the simplest code that goes green.** Build for the test in front of you, not the requirement you imagine next ([minimum-necessary-complexity](minimum-necessary-complexity.md)). The next test earns the next code.
- **Test behavior, not implementation.** Assert the observable result — return value, emitted event, stored row — not the private steps taken to reach it. A test coupled to *how* the code works breaks on every refactor and stops being a safety net.

## Trade-offs

Test-first is a real cost: it slows the first draft and forces you to commit to an interface before you've felt out the problem. For a genuine spike, write tests after and delete the spike. Over-specified tests are their own trap — assert *how* instead of *what* and the suite screams on every legitimate refactor. And green is not correct: a suite of confident, wrong assertions (the weak-oracle problem [verifiability](verifiability.md)) buys false safety. Some behavior is genuinely hard to drive test-first — heavy UI, integration seams, real hardware — where the calibrated move is a thin test at the boundary plus manual verification. Spend the discipline where a silent regression would cost the most.

## Litmus test

> If I deleted the implementation, would this test go red — and does it state intended behavior a reviewer can check without reading the code?

## Related

- [Verifiability](verifiability.md) — the parent principle. Verifiability is the *what* (define success, check it with independent evidence); TDD is one disciplined *when*.
- [Determinism](determinism.md) — red-green only carries information if the target holds still. A flaky test has no fixed red or green, so it can't drive anything.
- [Minimum Necessary Complexity](minimum-necessary-complexity.md) — TDD's engine for YAGNI: the simplest-code-to-pass step and the rule that the next test earns the next code keep you from building machinery no test demands.
- [Anti-Foot-Gun](anti-foot-gun.md) — a guard's test that goes red when the guard is removed proves it actually fires; a safety check that never rejected bad input is a footgun that only looks safe.

## References

- [Kent Beck — Test-Driven Development: By Example](https://www.oreilly.com/library/view/test-driven-development/0321146530/) — the red-green-refactor loop from first principles
- [Kent Beck — Test Desiderata](https://kentbeck.github.io/TestDesiderata/) — the properties that make a test worth keeping
- [Freeman & Pryce — Growing Object-Oriented Software, Guided by Tests](http://www.growing-object-oriented-software.com/) — letting the tests drive the design
- [Ian Cooper — TDD, Where Did It All Go Wrong](https://www.youtube.com/watch?v=EZ05e7EMOLM) — test behavior, not implementation, so tests survive refactoring
