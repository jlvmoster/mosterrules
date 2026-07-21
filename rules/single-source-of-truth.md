# Single Source of Truth

> Give each fact one authoritative home; derive, link, or validate every other representation.

## Principle

A *single source of truth* (SSOT) means every fact — a version number, a config value, a schema, a business rule, a customer's address — has exactly one **authoritative** home. That home is where the fact is edited and read; everywhere else the same fact appears, it is *derived* from the source (generated, computed, imported), *linked* to it (a reference, not a copy), or *validated* against it (a check that fails when the two disagree) — never independently maintained.

The enemy is the **uncontrolled duplicate**: the second copy that someone updates while the first goes stale, so now there are two answers to one question and no way to tell which is current. A copy isn't automatically wrong — caches, replicas, and denormalized reads are essential — the rule is that a copy must have a *defined relationship* to its source (how it's refreshed, how staleness is detected) rather than a life of its own.

The move is to **make the copies unable to drift**: generate them from the source so they can't be edited by hand, or add a check that fails loudly when a copy and its source disagree — the choice this repo makes, where `validate_rules.py` blocks the turn if `rules/README.md` stops mirroring a rule's blockquote verbatim.

## Why it matters for agentic development

Agents run on context, and context is copies — a value pasted into a prompt, a fact recalled from a summary, a duplicated snippet of config. An agent has no way to tell a *current* copy from a *stale* one.

- **Stale context reads as confident truth.** An agent acts on the value in front of it with full conviction, whether it's fresh or three versions old. It can't feel the doubt that makes a human go "wait, is this still right?" — so a stale duplicate becomes a confident wrong action.
- **Agents multiply copies.** Summarizing, restating, and pasting facts across files and subagents is what agents *do* — each copy a new place to drift out of sync with the source.
- **Divergence is silent until it bites.** Two representations of one fact can disagree for a long time before anything notices; the agent building on the wrong one inherits the error with no signal.
- **A generated artifact edited by hand is the classic trap.** An agent "fixes" a value in a derived file (a lockfile, a build output, a mirrored index); the real source is untouched, the next regeneration reverts it, and the two now disagree — which is why edits belong to the tool that owns the artifact ([anti-foot-gun](anti-foot-gun.md)).

## How to apply

- **Name the authoritative home.** For each fact, decide the one place it's edited and read. If you can't point to it, that's the bug — an unowned fact is one nobody can keep correct.
- **Derive, don't duplicate.** Generate the other representations from the source (code from a schema, docs from the code, an index from the files) so a copy can't be edited independently of what it mirrors.
- **If you must copy, make drift fail loud.** A denormalized read or a mirrored value needs a check that fails when it diverges from the source — a validator, a test, a CI gate — turning silent drift into a caught error.
- **Link instead of restating.** Reference the source (a path, an ID, a URL) rather than pasting its contents, so there's one thing to update and nothing to fall behind.
- **Point agents at the source, not a snapshot.** Have tools read the current value at use time instead of baking a copy into a prompt or a cached summary that quietly ages.

## Trade-offs

Centralizing has real costs. A single home can become a bottleneck or a single point of failure, and deliberate duplication — caches, read replicas, denormalized tables, precomputed views — is often the right call for latency, availability, or decoupling; forbidding all copies is its own mistake. The discipline isn't "never copy," it's "no *uncontrolled* copies": every derived representation needs a defined refresh path and a way to detect staleness, which is machinery you have to build and maintain. And a source of truth can itself be wrong — one authoritative home concentrates the value but doesn't guarantee it's correct ([verifiability](verifiability.md) is a separate question). Spend the effort where a stale copy would silently mislead; accept managed duplication where the relationship to the source is explicit.

## Litmus test

> For this fact, can I name the one place it's authoritative — and if the copy in front of me had gone stale, would anything tell me, or would I act on it with full confidence?

## Related

- [Idempotency](idempotency.md) — Idempotency leans on durable state as the truth so one *operation* converges to a target; SSOT is about each *fact* having one home so its copies can't drift. Related instinct — trust one authority — on different objects: an operation's result versus a fact's representations.
- [Anti-Foot-Gun](anti-foot-gun.md) — routing edits of a generated artifact through the tool that owns it is SSOT made structural: the derived copy is un-editable by hand, so it can't diverge from its source.
- [Verifiability](verifiability.md) — SSOT gives a fact one *authoritative* home; Verifiability checks that home is *correct*. Authoritative isn't the same as right.

## References

- [Wikipedia — Single source of truth](https://en.wikipedia.org/wiki/Single_source_of_truth)
- [The Pragmatic Programmer — DRY: Don't Repeat Yourself](https://pragprog.com/tips/) — one authoritative, unambiguous representation of every piece of knowledge
- [Wikipedia — Database normalization](https://en.wikipedia.org/wiki/Database_normalization) — structuring data so each fact is stored once
