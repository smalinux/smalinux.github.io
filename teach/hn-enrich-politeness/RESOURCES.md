# Layer Boundaries & Live-Fetch Safety — Resources

Every entry below was opened and checked on 2026-07-17, not recalled.

## Knowledge

### Boundaries and module design

- [_A Philosophy of Software Design_ — John Ousterhout](https://web.stanford.edu/~ouster/cgi-bin/book.php)
  The source of the "deep module" idea this codebase is built on: powerful
  implementation behind a narrow interface. Use for: judging whether a seam is
  worth its cost, and why `politeness.py` exposing `fetch(url)` and nothing else
  is the point. The repo's docstrings are already written in this dialect.
- [Hexagonal Architecture ("Ports and Adapters") — Alistair Cockburn](https://alistair.cockburn.us/hexagonal-architecture)
  The originator's own page (concept from 1994, named "Ports and Adapters" in
  2005). Use for: why `ports.py` exists at all, and why an adapter is
  interchangeable. `ports.py:5` already tells you to google exactly this.
- [Hexagonal architecture — Wikipedia](https://en.wikipedia.org/wiki/Hexagonal_architecture_(software))
  Use for: a fast, neutral orientation and the term's history when Cockburn's
  own page is too terse.

### Live-fetch safety

- [OWASP: Server Side Request Forgery Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html)
  **The primary source for `politeness.py`.** Three of its rules are implemented
  almost verbatim in the module: disable redirect-following in the client;
  resolve a name to *all* its addresses (A + AAAA) and validate every one; deny
  loopback / RFC1918 / link-local / multicast. Use for: checking any change to
  the guard against the standard, and for the DNS-rebinding (TOCTOU) discussion
  that motivates the egress-proxy decision.
- [OWASP Top 10 2021 — A10: Server-Side Request Forgery](https://owasp.org/Top10/2021/A10_2021-Server-Side_Request_Forgery_(SSRF)/)
  Use for: the one-page framing of why this class of bug matters, if you need to
  justify the guard's cost to someone else.

### Patterns the codebase is built from

- [Gary Bernhardt — _Boundaries_ (SCNA 2012)](https://www.destroyallsoftware.com/talks/boundaries)
  The talk that named Functional Core / Imperative Shell. Use for: the pure-plan
  / thin-effect split in `limits.py` and `teardown.py` (lesson 0004), and why a
  functional core needs few or no test doubles.
- [Mark Seemann — "Service Locator is an Anti-Pattern"](https://blog.ploeh.dk/2010/02/03/ServiceLocatorisanAnti-Pattern/)
  The canonical case *against* the pattern `deps.py` uses. Use for: the honest
  counter-view (lesson 0005) — the charge is hidden dependencies; judge whether
  confining the locator to impure adapters answers it. Follow-ups: "violates
  SOLID" (2014), "violates encapsulation" (2015).

### The gate `limits.py` stands on

- [Prefect: `prefect.concurrency.sync` API reference](https://docs-3.prefect.io/v3/api-ref/python/prefect-concurrency-sync)
  Use for: the exact contract behind `live_fetch_gate`. Confirms `strict=True`
  raises `ConcurrencySlotAcquisitionError` when the limit was never registered —
  which is the whole argument in the `limits.py:148-155` comment.
- [Prefect: client orchestration API reference](https://docs-3.prefect.io/v3/api-ref/python/prefect-client-orchestration-__init__)
  Use for: `upsert_global_concurrency_limit_by_name` — "creates ... if one does
  not already exist ... otherwise update its limit if it is different". This is
  the source of `deploy_init`'s idempotency claim.

### Ready-made alternatives (the "buy" options)

- [Stripe Smokescreen — egress proxy](https://github.com/stripe/smokescreen)
  The canonical SSRF egress proxy, and the one already on this project's
  decision record. Resolves each requested hostname and refuses non-public IPs;
  also does in-flight concurrency limiting and token-bucket rate limiting at the
  proxy. Use for: the "buy" side of the SSRF guard — and note its own limit, the
  ACL "is only applied to hostnames as they appear in the request", which is why
  IP-range blocking still needs network-level egress rules on top (the CGNAT gap).
- [Advocate — SSRF-preventing requests wrapper](https://github.com/JordanMilne/Advocate)
  The best-known in-process approach. **Unmaintained**, and shipped a real
  DNS-rebinding advisory. Use for: the cautionary tale — an in-process guard
  cannot close TOCTOU, which is the whole argument for a proxy.
- [requests-hardened — Saleor](https://pypi.org/project/requests-hardened/)
  A maintained in-process SSRF filter (blocks private/loopback, can reject
  redirects). Use for: comparison — it is roughly what `politeness.py` already
  is, and it inherits the same rebinding limit.
- [pyrate-limiter](https://pypi.org/project/pyrate-limiter/) / [requests-ratelimiter](https://pypi.org/project/requests-ratelimiter/)
  Leaky-bucket rate limiter with per-key (per-host) buckets and pluggable
  Redis/Postgres backends. Use for: the "buy" side of `RateLimiter` if the
  per-domain spacing ever needs to be shared across machines, not just threads.
- [Scrapy — AutoThrottle & politeness settings](https://docs.scrapy.org/en/latest/topics/autothrottle.html)
  The whole-framework option: `CONCURRENT_REQUESTS_PER_DOMAIN`,
  `DOWNLOAD_DELAY`, AutoThrottle, `RobotsTxtMiddleware`, retry middleware. Use
  for: seeing what a mature politeness layer includes — but it is a Twisted-based
  crawling framework, does no SSRF, and would fight Prefect. Reference, not adopt.

## Wisdom (Communities)

Not yet discussed with the user — proposed, not endorsed. Raise once there is a
real question worth taking outside.

- [r/ExperiencedDevs](https://reddit.com/r/ExperiencedDevs)
  Use for: "is this seam worth it" design critique from people who maintain
  systems rather than start them. Moderated hard against career-advice noise.
- [Prefect Community Slack](https://prefect.io/slack)
  Use for: the questions only operators can answer — how global concurrency
  limits behave under worker crashes, and whether a slot can leak.

## Gaps

- **Nothing on rate-limiting etiquette as a norm** (crawl-delay, robots.txt,
  what target sites actually expect). `RateLimiter` implements a number that no
  cited source justifies. Scrapy's docs treat `DOWNLOAD_DELAY` ~2s as "polite",
  but that is convention, not a standard.
- **No primary account of Smokescreen's CGNAT gap.** The README confirms the ACL
  acts on hostnames as-requested (not resolved IPs), which is consistent with the
  decision record's open CGNAT gap — but a first-hand write-up of that specific
  failure mode is still missing.
