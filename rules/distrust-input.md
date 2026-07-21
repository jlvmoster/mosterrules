# Distrust Input

> Treat everything crossing a trust boundary as hostile until proven safe. Validate at the edge, by structure — never trust that the caller, the file, or the upstream tool behaved.

## Principle

A *trust boundary* is any point where data crosses from somewhere you don't control into somewhere you do — a request into a handler, a file into a parser, a web page or another tool's output into an agent's context. The principle is to treat every value crossing that line as **untrusted until validated**, and to validate **at the boundary, by structure**, before the value reaches any code that acts on it.

*By structure* means checking shape against an explicit schema — types, ranges, lengths, enumerated values, an allowlist of what's permitted — and rejecting everything else. An allowlist of what's valid fails **closed**; a denylist of what's bad fails **open** the moment an attacker finds a form you didn't think to block.

The strongest version makes invalid input *unrepresentable past the edge*: parse untrusted bytes once, at entry, into a typed value whose existence proves it passed the checks — then the interior can assume every value it holds is already safe. Validation that returns a boolean leaves the raw input in play; parsing returns a *narrower thing* and throws the unsafe input away. Parse, don't validate.

## Why it matters for agentic development

An agent runs on input it doesn't control and feeds it straight into tools that act. A person eyes a phishing email and hesitates; an agent reads it mid-task and calls a tool.

- **The input is the attack surface.** A web page, an issue, a code comment, or another tool's output carries instructions, and an agent that treats all text as equally trustworthy acts on them. Prompt injection is the case structural validation *can't* close: a payload that reads as perfectly valid natural language passes every schema, so the defense shifts from parsing to **isolation** — keep untrusted text out of the instruction channel, don't hand it your tools, and gate risky actions behind [least-privilege](least-privilege.md) and human approval. Whatever the agent *would do* with input, an attacker who controls that input can *direct*.
- **Untrusted text becomes trusted action.** The agent turns a value into a shell command, a SQL query, a file path, or a URL. Without a boundary check, a crafted value becomes injection, path traversal, or SSRF — the classic confusions, now reached automatically and at volume.
- **No instinctive smell test.** A human notices an "order quantity" of `-1` or `99999999`, or a name field full of markup. An agent has no reflex of suspicion; it validates only what the code makes it validate.
- **Volume turns rare into routine.** A malformed input a human hits once a month, an agent hits at scale — and its downstream tools inherit whatever the boundary let through.

## How to apply

- **Validate at the edge, once.** Check untrusted values where they enter, not scattered through the call chain. One boundary that produces a safe value beats ten interior callers each half-remembering to re-check.
- **Allowlist, don't denylist.** Enumerate what's permitted and reject the rest. Blocking known-bad patterns is a sieve you're forever patching; permitting known-good is a wall.
- **Parse into types, not booleans.** Turn the string into a validated `Email`, a bounded `Quantity`, an enum — so "is this valid?" is answered by the type system once, and no later code can forget to ask.
- **Keep data out of the command channel.** Parameterized queries, argument arrays over shell strings, structured tool calls over interpolated text. Injection is data smuggled into a place meant for code; keep the two channels separate and it can't.
- **Treat tool output and model output as input too.** A downstream tool's response, a retrieved document, another agent's message — all cross a trust boundary. Validate them before acting, exactly as you would a user's request.
- **Fail closed and loud.** Reject invalid input with an error; don't silently coerce it into a plausible-looking value that propagates downstream ([anti-foot-gun](anti-foot-gun.md)'s fail-loud, applied at the boundary).

| Untrusted source | Confusion it enables | Boundary fix |
|---|---|---|
| user string → SQL | injection | parameterized query, never string interpolation |
| user string → shell | command / option injection | argument array ending options with `--` (`["rm", "--", path]`), or a native file API |
| filename → path | traversal (`../../etc`) | resolve, then confirm it stays under an allowed root |
| web page / issue text → agent | prompt injection | treat as data, not instructions; don't hand it your tools |
| URL → server fetch | SSRF | allowlist hosts/schemes; deny internal ranges |

## Trade-offs

Validation can be too strict: reject input a caller legitimately needs and you've built a footgun that trains people to route around the boundary — the [anti-foot-gun](anti-foot-gun.md) over-noisy-guardrail failure, at the front door. There's a real tension with Postel's law ("be liberal in what you accept"): liberal acceptance eases interop but widens the attack surface, and decades of security bugs came from parsers being *too* forgiving. Structure has a ceiling, too: a schema check catches malformed *data* but never a well-formed *instruction*, so free-form text bound for a model — the prompt-injection case — needs isolation and least privilege, not a stricter parser. Calibrate by consequence — validate strictly what will steer a command, a query, or a path; be more lenient with inert display data — and keep each schema next to the code that consumes it so it can't drift out of sync with reality.

## Litmus test

> If a hostile actor controlled every byte of this input, what's the worst it could make the code do — and does a check *at the boundary* stop that before the value is ever used?

## Related

- [Least Privilege](least-privilege.md) — caps what a hijacked agent *can do*; Distrust Input governs what gets *in*. Together they are the security pair: bound the authority, and validate the input that might seize it.
- [Anti-Foot-Gun](anti-foot-gun.md) — narrows the interface's *shape*; Distrust Input validates the *values* flowing through it, and shares the fail-loud reflex.

## References

- [OWASP Input Validation Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html)
- [CWE-20: Improper Input Validation](https://cwe.mitre.org/data/definitions/20.html)
- [Alexis King — Parse, Don't Validate](https://lexi-lambda.github.io/blog/2019/11/05/parse-don-t-validate/)
- [Simon Willison — Prompt injection](https://simonwillison.net/series/prompt-injection/)
