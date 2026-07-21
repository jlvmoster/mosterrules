# Minimum Necessary Complexity

> Build the smallest thing that meets a demonstrated need; add machinery only when reality earns it.

## Principle

Complexity is *necessary* when it's forced by the problem, and *accidental* when it comes from the solution. The principle is to pay the first and refuse the second: build the smallest thing that meets a need you can actually point to, and let each added abstraction, layer, dependency, or configuration knob earn its place by solving a problem that has *already appeared* — not one you imagine might.

The tell of accidental complexity is machinery justified by a hypothetical: the interface with one implementation, the factory that builds one product, the config option no caller sets, the generalization for a second case that never came. Each is code written against a future that may not arrive, and until it does, it is pure cost — surface to read, test, and maintain, with no need behind it.

The move is to **default to less and let need pull complexity in**, rather than defaulting to flexible and hoping it pays off. A working simple thing can grow the one joint it turns out to need; an elaborate thing built for imagined needs has to be *understood in full* before it can be safely cut back. Simple-then-grown beats complex-then-pruned.

## Why it matters for agentic development

Agents make complexity historically cheap to *produce* and just as expensive as ever to *own*. The economics that used to restrain over-building — writing code is slow — no longer bites.

- **Generation is nearly free; comprehension is not.** An agent emits a factory, an interface, and three layers of indirection as fast as it emits one function. The cost didn't vanish — it moved downstream to every future reader, human or agent, who must now hold all of it in their head to change anything.
- **Speculative flexibility is the default failure.** Asked for one thing, an agent readily builds the general version "to be safe." That extra surface is where the next agent gets lost, mis-wires a call, or duplicates what's already there because it couldn't find it under the machinery.
- **More surface, more blast radius.** Every layer is more places for a bug to hide and more interface an agent can misuse — the same instinct as [least-privilege](least-privilege.md) (grant no more than needed) and [anti-foot-gun](anti-foot-gun.md) (fewer sharp edges), applied to how much you *build at all*.
- **Agents can't feel bloat.** A human senses when a codebase has grown too clever to hold; an agent will cheerfully extend an over-engineered design further in its own idiom, compounding it.

## How to apply

- **Demand a present need.** Add an abstraction, dependency, or option only for a problem that has actually appeared. "We might need it" is a reason to wait, not to build — you can add the seam when the second case is real.
- **Reach for what already exists first.** The standard library, a platform feature, or a helper already in the codebase beats new machinery. Re-implementing what lives a few files over is the most common self-inflicted complexity.
- **Prefer the shorter working version.** Fewer moving parts, fewer files, one clear path over a configurable one — as long as it stays correct on the edge cases. Deletion is a legitimate, often superior, change.
- **Don't abstract on the first instance.** One case is a function; wait for the pattern to repeat before generalizing, or you'll abstract around a shape that turns out wrong and pay twice.
- **Name deliberate shortcuts.** When you knowingly take the simple path with a known ceiling, say so — a short note on what it doesn't handle and when to revisit — so "simple" reads as intent, not oversight.

## Trade-offs

Minimalism has a failure mode of its own: too little structure is also complexity, just relocated. Skipping an abstraction the problem genuinely needs yields duplication, tangled special cases, and a big painful refactor later — under-engineering and over-engineering are two ways to miss *necessary* complexity, from opposite sides. Some machinery must be built ahead of the need: security controls, input validation, error handling, and migration paths aren't "extra" and don't wait for an incident to earn their place. And "smallest" is about *essential* complexity, never about skimping on correctness, tests, or clarity to shrink a diff. The skill is telling forced complexity from self-inflicted — pay the first in full, refuse the second.

## Litmus test

> For each layer, option, and dependency here, can I name the concrete need it meets *today* — and if I deleted it, what real thing would break?

## Related

- [Least Privilege](least-privilege.md) — both are "no more than needed": Least Privilege bounds the *authority* granted, this bounds the *machinery built*. Excess of either is standing risk with no benefit.
- [Anti-Foot-Gun](anti-foot-gun.md) — less surface is fewer footguns; a smaller interface has fewer ways to be misused, so simplicity and safety pull the same direction.
- [Test-Driven Development](test-driven-development.md) — TDD is this rule's engine: the simplest-code-to-pass step and "the next test earns the next code" enforce YAGNI move by move, so nothing gets built that no test demands.

## References

- [Fred Brooks — No Silver Bullet](https://en.wikipedia.org/wiki/No_Silver_Bullet) — essential versus accidental complexity
- [John Ousterhout — A Philosophy of Software Design](https://web.stanford.edu/~ouster/cgi-bin/book.php) — complexity as the thing good design fights
- [Gall's Law](https://en.wikipedia.org/wiki/John_Gall_(author)#Gall's_law) — a working complex system evolves from a working simple one
- [YAGNI — You Aren't Gonna Need It](https://martinfowler.com/bliki/Yagni.html)
- [Ponytail](https://github.com/DietrichGebert/ponytail) — a "lazy senior dev" Claude Code plugin that operationalizes this principle as a review/guardrail against over-engineering
