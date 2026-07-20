# Least Privilege

> Grant the minimum access needed, for the minimum scope, for the minimum time — and no more. Default to deny; widen only on demonstrated need.

## Principle

The *principle of least privilege* (PoLP) holds that every actor — a user, a service, a credential, a tool, an agent — should operate with the **least authority required to do its job**, and no more. Privilege is scoped along three axes: **what** it can touch (which resources), **how** it can touch them (read vs. write vs. delete), and **how long** it holds the grant (permanent vs. time-bound).

The default is **deny**. Access is an allowlist you widen on demonstrated need, not a denylist you trim after an incident. A broad grant "to be safe" or "so it just works" inverts the principle — it optimizes for never being blocked instead of for limiting what a mistake or a compromise can reach.

The payoff is **blast radius**. When something goes wrong — a bug, a leaked token, a hijacked prompt — the damage is bounded by what that actor was allowed to do. Least privilege is what makes "went wrong" mean "small," not "catastrophic."

## Why it matters for agentic development

Agents are handed authority — API tokens, database credentials, tool access, shell — and then act on it fast, in volume, and on inputs you don't fully control. Their privileges *are* the ceiling on how much harm a confused, buggy, or manipulated agent can do.

- **The agent's authority is the attacker's authority.** An agent processes untrusted text — a web page, an issue, an email — and prompt injection can turn its tools against you. Whatever the agent *can* do, a successful injection *will* do. A read-only, single-scope token makes the worst case small; an admin key makes it unbounded.
- **Over-broad grants get used.** Just as "whatever a tool allows, an agent will do" ([anti-foot-gun](anti-foot-gun.md)), whatever access an agent *has*, it will eventually *exercise* — deleting, writing, or reaching a resource you never intended it to touch, because the credential let it.
- **Volume multiplies a single over-grant.** One over-privileged credential wired into an agent that runs thousands of times is thousands of chances to misuse it. A human might touch the dangerous scope once and stop; an agent has no such brake.
- **Standing privilege is a waiting liability.** Long-lived, broadly-scoped tokens sitting in an agent's environment are the thing that leaks — into logs, into context windows, into a subagent. Short-lived, narrow credentials are worth little if they escape and nothing if they've expired.

## How to apply

- **Default-deny, then allowlist.** Start from no access; grant named permissions on demonstrated need. An allowlist fails closed — a denylist fails open the moment a capability you forgot to exclude appears.
- **Scope credentials to the narrowest resource and action.** Read-only when only reading; one bucket, one table, one repo — not the whole account. A token that can do exactly one job can be misused for exactly one job.
- **Prefer short-lived and revocable over standing.** Ephemeral, auto-expiring credentials (scoped session tokens, workload identity) over long-lived static secrets. If it can't be revoked and doesn't expire, a leak is permanent.
- **Give agents narrow tools, not broad ones.** A `refund_order(id)` beats a database admin connection — constraining the interface in [anti-foot-gun](anti-foot-gun.md), applied to *authority* rather than *shape*. Hand each agent and subagent its own least-scoped identity, not a shared god-credential.
- **Separate identities and segment.** Distinct principals for distinct jobs, so one compromise doesn't inherit the others' access; segment resources so reaching one grants no path to the rest.
- **Drop privilege as soon as it's spent.** Don't run as root when a normal user works; don't hold write access during a read-only phase. Acquire narrowly, use, release.
- **Review and revoke.** Grants accrete; audit them and remove what's unused — an access nobody exercises is all blast radius, no benefit.
- **Calibrate, or least privilege becomes theater.** Scope so tight the safe path is constantly blocked and callers reach for the broad admin credential "just to unblock" — the same way an over-noisy guardrail trains a reflexive `--force` ([anti-foot-gun](anti-foot-gun.md)). Grant enough to do the real job in one deliberate step, not so little the workaround is a wildcard.

## References

- [Saltzer & Schroeder, *The Protection of Information in Computer Systems*](https://www.cs.virginia.edu/~evans/cs551/saltzer/) — the 1975 paper that named least privilege
- [NIST SP 800-53: AC-6 Least Privilege](https://csrc.nist.gov/projects/cprt/catalog#/cprt/framework/version/SP_800_53_5_1_1/home?element=AC-6)
- [AWS: Apply least-privilege permissions](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html#grant-least-privilege)
