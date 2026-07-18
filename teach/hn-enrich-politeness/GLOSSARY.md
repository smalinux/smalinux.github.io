# hn-enrich Boundaries Glossary

The canonical language for this workspace: the design vocabulary behind
hn-enrich's live-fetch and operator path. Lessons and records use these terms and
these spellings. Definitions are tight on purpose, and use each other.

## Boundaries & module design

**Port**:
The smallest possible interface in front of an external effect — a one-method
`Protocol` the rest of the code depends on, instead of a concrete client.
_Avoid_: interface, abstraction

**Adapter**:
A concrete implementation of a **Port** — one *real* (reaches the world) and one
*fake* (serves canned data) per Port.
_Avoid_: driver, backend

**Decorator (over a Port)**:
An object that both *is-a* and *has-a* the same **Port**, adding behaviour around
the inner call. The move behind `PolitenessFetcher`.
_Avoid_: wrapper (a wrapper that only forwards is a **Pass-through**, not this)

**Dependency Inversion**:
The direction rule — the policy owns the **Port**, and the machinery depends on
it. The import arrow points toward the policy (`limits` → `politeness`, never the
reverse).
_Avoid_: dependency injection (that is the mechanism; this is the direction)

**Injected-effect seam**:
A `Callable` alias with a real default, overridable in tests — `Resolver`,
`GateFactory`, `UpsertLimit`, `DropSchema`, `Emit`. The concrete form dependency
injection takes here.
_Avoid_: hook, callback

**Functional Core, Imperative Shell**:
A pure core that decides and returns a **Verdict-as-data**, wrapped by a thin
shell that performs the **Injected-effect seam**. Gary Bernhardt's name.
_Avoid_: separation of concerns, business-logic layer

**Pure function**:
Plain values in, plain values out, nothing outside itself touched —
deterministic, and testable with literals.

**Total function**:
A function that returns a verdict for *every* input; no path forgets to answer,
and the default answer refuses. A **Total** guard cannot be slipped past by an
input its author did not picture.
_Avoid_: complete, exhaustive

**Verdict-as-data**:
The decision lifted out of control flow into a returned value (`TeardownPlan`,
`list[LimitSpec]`), so it can be tested without acting.

**Null Object**:
A do-nothing implementation of a seam (the open gate = `nullcontext()`) so
callers need no null check.
_Avoid_: no-op, empty stub

**Service Locator**:
A global registry you ask for a dependency by name, instead of receiving it
through a constructor. Forced here because Prefect tasks take only serializable
ids; accepted as "an honest step down."
_Avoid_: singleton, container

**Pass-through**:
A wrapper whose method forwards the call unchanged — a new layer with no new
abstraction, and a red flag (Ousterhout). The thing a **Decorator** must never
be. (This term exists to be avoided in code, not aspired to.)

**No drift**:
The property that a rule lives in exactly one place, so two callers cannot
diverge — one `_politeness` for both fetch and scan.

## The two modules

**Per-call policy**:
A rule answerable from the url alone — *may this one call go, and when.*
`politeness.py`'s job.
_Avoid_: limit, rate limit (a rate limit is one instance of this)

**System capacity**:
A cap on how many calls run at once across the whole system, or a relation
between two such caps. `limits.py`'s job.
_Avoid_: rate limit, throttle

**The gate**:
The seam where **Per-call policy** asks the **System capacity** for a slot — its
shape (`ConcurrencyGate`) defined by `politeness`, its width filled by `limits`.

**strict gate**:
A **gate** that raises if its limit was never registered, rather than running
un-capped (`strict=True`). "A cap that exists only sometimes is the bug."

**Per-domain spacing**:
The minimum interval enforced between two hits on the same domain (`RateLimiter`)
— **Per-call policy**, not **System capacity**.
_Avoid_: throttle, concurrency limit (a different axis)

## Live-fetch safety (SSRF)

**SSRF (Server-Side Request Forgery)**:
An attack that abuses a server into making requests to internal or private
addresses it should never reach.

**SSRF guard**:
The predicate that refuses any url whose scheme is not http(s) or whose host
resolves to a non-public address (`is_public_url` / `assert_public_url`).

**Fail-closed (safe by default)**:
The default answer is "no" — an unresolved name, an empty result, or any doubt
refuses. Shared by the **SSRF guard**, `plan_teardown`, and the fake-by-default
adapter selection.
_Avoid_: fail-safe (ambiguous about which way is safe)

**Check-then-use (TOCTOU)**:
Validate a thing, then use it, with a window between where it can change — so the
check no longer describes what was used.
_Avoid_: race condition (too broad)

**DNS rebinding**:
The attack that exploits the **Check-then-use** window on a hostname: the name
resolves public when the **SSRF guard** checks, internal when the transport
connects.

**Redirect walk**:
Following a redirect chain by hand, one unfollowed hop at a time, guarding every
hop before it is fetched (`walk_redirects`) — because a client that follows
redirects itself fetches hops the guard never judged.
_Avoid_: redirect following

**IP pinning**:
Connecting to the exact address the **SSRF guard** validated, so there is no
second lookup to poison — the real in-process fix for the **Check-then-use**
window, but fragile.

**Egress proxy**:
A forward proxy all outbound requests pass through, which validates and connects
with one resolution — closing the **Check-then-use** window in one shared place
(Smokescreen).

**Defense in depth**:
Stacked controls where each covers the edge the previous one cannot — forced here
(**SSRF guard** + **Egress proxy** + network egress rules), not optional caution.

**CGNAT range**:
`100.64.0.0/10` (RFC 6598) — *not* private by the RFC1918 test, so a
hostname-level control can miss it; the network-egress layer catches it. The
project's open gap.
_Avoid_: private range (it specifically is not one)
