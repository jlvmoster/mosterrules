# Test-Driven Development

> Write the failing test first, watch it fail, then write the code that makes it pass. The test is the specification; the code is what satisfies it.

## Principle

Test-Driven Development inverts the usual order: the check comes *before* the code. You write a test that describes the behavior you want, run it and watch it fail for the reason you expect, then write the smallest code that turns it green — and only then, with a passing test as a safety net, do you refactor. Red, green, refactor, one small step at a time.

The discipline lives in the *ordering*, not in the tests themselves. A test written after the code tends to assert whatever the code already does — it documents the implementation instead of constraining it, and it can't tell you the code was ever wrong because it never saw red. A test written first is a specification: it fails until the behavior exists, so the moment it passes carries real information. Watching it fail isn't ceremony — it's how you learn the test *can* fail, and fails for the right reason rather than a typo in the test itself.

The move is to let the failing test *drive*: it names the next increment of behavior, gives the code a fixed target to hit, and — once green — becomes the fixture that lets you change the design without changing what it does.

## Why it matters for agentic development

An agent's strongest instinct is to emit code that looks finished. Test-first aims that instinct at a fixed target instead of a feeling: the work isn't done when it reads right, it's done when a specific test that was red goes green.

- **Red-first defeats the vacuous test.** An agent told to "add tests" will happily write one that passes against the current code without exercising anything — a test that never failed proves nothing. Demanding it fail first, for the stated reason, is the only thing that shows it can catch a regression at all.
- **The test is a spec a human can review.** For agent-written code a reviewer won't read line by line, the test states the intended behavior in a form they *can* check — and that re-runs on every future change, not just at review time.
- **Small red-green steps bound the blast radius.** An agent that writes a large change and tests it at the end can't tell which part turned the suite red. One failing test at a time keeps every increment attributable and every rollback cheap.
- **Green is the license to refactor.** An agent restructuring untested code is editing blind; a passing suite is the external signal that behavior survived the change, which is exactly what lets an agent simplify aggressively instead of leaving mess it's afraid to touch.

## How to apply

- **Write the test before the code, and run it red.** State the behavior as a failing test first, then watch it fail. An unexpected green isn't a green light: either the behavior already exists — so this step needs no new code — or, more often, the test isn't exercising what you think. Find out which before you move on; don't write code to force a red you didn't actually get.
- **Confirm it fails for the right reason.** Read the failure. A test that dies on an import error or a typo hasn't exercised the behavior; make it fail the way real broken code would, *then* make it pass.
- **Write the simplest code that goes green.** Build for the test in front of you, not the requirement you imagine next ([minimum-necessary-complexity](minimum-necessary-complexity.md)). The next test earns the next code.
- **Refactor only under green.** Restructure with the suite passing before and after; if it goes red, the refactor changed behavior. Never add behavior and refactor in the same red bar.
- **Test behavior, not implementation.** Assert the observable result — return value, emitted event, stored row — not the private steps taken to reach it. A test coupled to *how* the code works breaks on every refactor and stops being a safety net.
- **One test, one reason to fail.** Keep each test focused so a red bar points at a single cause; a test that checks five things tells you the least about which one broke.

## Trade-offs

Test-first is a real cost, not a free habit. It slows the first draft and forces you to commit to an interface before you've felt out the problem — for a genuine spike or throwaway exploration, writing tests first can be waste, and the honest move is to spike without them and delete the spike. Over-specified tests are their own trap: assert too much, or assert *how* instead of *what*, and the suite ossifies the design and screams on every legitimate refactor — a test that breaks when behavior didn't is negative value. And green is not correct: a suite of confident, wrong assertions (the weak-oracle problem [verifiability](verifiability.md)) buys false safety, which is worse than none because it ends scrutiny. Some behavior is genuinely hard to drive test-first — heavy UI, integration seams, real hardware — where the calibrated move is a thin test at the boundary plus manual verification, not a contortion to force red-green everywhere. Spend the discipline where a silent regression would cost the most.

## Litmus test

> Did I watch this test fail for the right reason before writing the code that makes it pass — and if I deleted the implementation, would the test go red?

## Related

- [Verifiability](verifiability.md) — the parent principle. Verifiability says define success and check it with independent evidence; TDD is the specific discipline that puts the check *first* and demands it fail before the code exists. Verifiability is the *what*; TDD is one disciplined *when* — you can verify without testing first, but you can't do TDD without verifying.
- [Determinism](determinism.md) — red-green only carries information if the target holds still. A flaky test has no fixed red or green, so it can't drive anything; test-first quietly depends on a deterministic result to test against.
- [Minimum Necessary Complexity](minimum-necessary-complexity.md) — TDD's engine for YAGNI: the simplest-code-to-pass step and the rule that the next test earns the next code keep you from building machinery no test demands.
- [Anti-Foot-Gun](anti-foot-gun.md) — watching a guard's test fail first proves the guard actually fires; a safety check you never saw reject bad input is a footgun that only looks safe.

## References

- [Kent Beck — Test-Driven Development: By Example](https://www.oreilly.com/library/view/test-driven-development/0321146530/) — the red-green-refactor loop from first principles
- [Kent Beck — Test Desiderata](https://kentbeck.github.io/TestDesiderata/) — the properties that make a test worth keeping
- [Freeman & Pryce — Growing Object-Oriented Software, Guided by Tests](http://www.growing-object-oriented-software.com/) — letting the tests drive the design
- [Ian Cooper — TDD, Where Did It All Go Wrong](https://www.youtube.com/watch?v=EZ05e7EMOLM) — test behavior, not implementation, so tests survive refactoring
