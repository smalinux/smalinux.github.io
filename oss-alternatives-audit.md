# Is hn-enrich reinventing wheels? Mostly no — with two clean wins and two things to fix

> **Provenance note.** This audit came out of a ten-track research workflow (one agent per
> concept area) reconciled against an adversarial verifier pass. Three claims were refuted —
> all about `alembic-utils`, corrected below. The synthesis agent itself was killed by a
> session limit, so this was assembled directly from the completed tracks.
>
> One coverage caveat up front, in the interest of honesty: the adversarial verification pass
> completed for the `alembic-utils`/`respx`/`vcrpy`/`dlt`/Singer claims, but the skeptic agents
> for the biggest claims (the SSRF transport, the trafilatura benchmark, the Dagster partition
> ceiling, the `adblock` 3.12 wheel) were cut off at the 2am reset before they ran. Those claims
> were self-grounded by the researchers against primary sources — the SSRF one by reading the
> installed `.venv` Prefect source, the `adblock` one by actually pip-installing and running it
> on 3.12 — so they're well-supported, but they didn't get the independent second pass. Each is
> flagged below where it matters.

---

The honest headline: most of what you built is not available off the shelf, and the parts that
are, you already delegate. Your core — the cursor spine, `reprocess.py`'s version/generation/heal
axes, `partition.py`, the `enr_run` ledger, and `finalize.py`'s partial-success taxonomy — has no
drop-in replacement because every candidate framework either versions at the wrong granularity
(table/asset, not per-row-per-worker) or demands owning the control flow your hexagonal design
deliberately keeps. There are exactly two genuine "delete your code" wins (`trafilatura` for text
extraction, and assembling `Playwright` + `adblock` for the unbuilt `ads_count`), one security gap
worth fixing this week (the SSRF guard), and one real multi-process correctness bug (the per-domain
rate limiter). Everything else is either a correct thin wrapper you should keep, or a framework
that would cost far more than the code it replaces.

## Directly answering "could we just use Prefect fully?"

This is the most important negative result, so I'll put it first. Leaning harder on Prefect would
not eliminate your largest hand-rolled module. I had an agent fetch the Prefect 3 Assets docs
specifically to check: Prefect Assets give lineage and health, but they have no
`code_version`/`data_version`, no staleness/"unsynced" semantics, and no partitions or backfills.
That means Prefect cannot express `reprocess.py`'s central question — "which items are stale for
worker X because its VERSION moved?" Prefect's task caching (`cache_policy`, `cache_key_fn`) can
decide "is this one (worker, item) fresh?" at call time, but it gives you no bulk "SELECT the next
N stale rows" query and stores its cache in `~/.prefect/storage` as a second source of truth beside
`enr_run` — a split brain, not a simplification.

Where Prefect already earns its keep is exactly where you already use it: `limits.py` is a thin,
correct wrapper over Prefect's real global concurrency limits
(`upsert_global_concurrency_limit_by_name`, the `concurrency(tag, strict=False)` gate). That's not
reinvented — it's delegated. So "use Prefect fully" is already true for concurrency, and impossible
for staleness. The one Prefect feature you're not using that's relevant is work-queue priority —
discussed under RETHINK below.

## REPLACE — a maintained library does this better and drops in behind an existing seam

**1. HTML→text extraction: adopt `trafilatura`, replace the regex in `adapters.py`.** This is the
textbook win. Your `_html_to_text` is `re.sub(r"<[^>]+>", " ", html)`, which does no boilerplate
removal. In Zyte's article-extraction-benchmark, every plain tag-stripper (BeautifulSoup
`get_text`, html2text, inscriptis, html-text) sits at ~0.50 precision, while `trafilatura` scores
F1 0.958 — meaning your `word_count` worker is currently counting roughly one
nav/footer/cookie-banner word for every real article word. `trafilatura` (v2.1.0, June 2026) drops
in behind the unchanged `FetchResult(text, html, http_status)` port: swap the body of
`_html_to_text` for `trafilatura.extract(response.content, favor_precision=True,
include_comments=False)`, pass bytes so its bundled `charset_normalizer` does encoding detection
(fixing httpx's assume-UTF-8 `response.text`), and keep the raw `html` field so `has_source_code`'s
`<pre>` regex still works. Bonus: for the `ai_class` worker feeding Claude,
`output_format="markdown"` is a strictly better input shape than stripped text. One dependency, one
function changed, no worker or test touched. (Benchmark numbers are the researcher's, citing the
Zyte repo; the independent verifier for this claim didn't run before the reset — but the number is
checkable and the direction is not in doubt.)

**2. `ads_count` (currently an unimplemented stub): assemble `Playwright` + `adblock`, don't write a
scanner.** Since this worker doesn't exist yet, "don't reinvent" is maximally actionable. The right
shape is two ready-made pieces behind your existing `TrackerScanner` port: (a) a `Playwright`
headless-Chromium adapter that loads the URL and collects every request via `page.on("request", …)`
— a static HTML fetch structurally cannot see JS-injected third-party requests, so a real browser
is unavoidable here; (b) a pure, injectable classifier built on the `adblock` PyPI package (Brave's
`adblock-rust` bindings): load EasyList → `n_ads`, EasyPrivacy or the DuckDuckGo TDS blocklist →
`n_trackers`, via `Engine.check_network_urls(...).matched`. The classifier has no I/O, so it stays
hermetic behind the port and `FakeScanner` is untouched. Use `adblock`, not `braveblock` — the
researcher verified `braveblock` ships no CPython 3.12 wheel (pip fails), while `adblock`'s abi3
wheel installs and runs on 3.12. Use The Markup's Blacklight and DDG Tracker Radar as the spec for
what to count, not as code — both are Node/JS or NonCommercial-licensed data and would drag a second
runtime into a pure-Python app.

Two systemic costs to plan for with #2, both of which you half-anticipated in the code: a browser
scan is a second, much heavier fetch (hundreds of MB of Chromium per held slot), so it needs its own
small concurrency cap in `limits.py` — do not let it share the `live-fetch` gate, or N concurrent
browser slots will OOM the worker. And `ads_count.py` already documenting "does its own visit" means
the design is consistent; just gate it on the item URL.

## ADOPT ALONGSIDE — worth adding, but it doesn't delete existing code

**3. `respx` as a dev dependency, for one new test file.** Your real `HttpxFetcher.fetch` is marked
`# pragma: no cover - real network`, so the User-Agent header, `follow_redirects=True`, the timeout,
and `_html_to_text` have zero coverage. `respx` (0.23.1) patches below the httpx client (at
httpcore's connection pool), so it exercises the real adapter class end-to-end without a socket —
which your hand-written `FakeFetcher`, sitting above the httpx call, structurally cannot. This was
verified against respx's source. Prefer `respx` over `pytest-httpx`, which hard-pins `httpx==0.28.*`
(also verified) and would hold your httpx back; `respx` floors at `>=0.25`. Note the one weak spot
the verifier caught: respx doesn't exercise real timeout timing (you inject `httpx.TimeoutException`
as a side effect) — headers, redirects, and status are genuinely end-to-end.

**4. `alembic-utils-extended` for the `v_enriched` view — with a correction.** Every worker slice
currently makes you hand-write a `DROP VIEW` + `CREATE VIEW` pair and paste the previous view body
into the migration purely so `downgrade()` can restore it (`0008_enr_ai_class.py` literally carries
a full copy of `0007`'s body). `alembic-utils-extended` (a maintained fork, v1.3.1, July 2026;
upstream `olirice/alembic_utils` has been dormant since April 2025) teaches `alembic revision
--autogenerate` to emit those ops itself.

⚠️ Correction from the verifier — the researcher got the import path wrong. It is not
`alembic_utils`. The correct API is:

```python
# migrations/env.py
from alembic_utils_extended.pg_view import PGView
from alembic_utils_extended.replaceable_entity import register_entities

v_enriched = PGView(schema="public", signature="v_enriched", definition="SELECT ...")
register_entities([v_enriched])
```

Two more honest caveats the verifiers surfaced: this only removes the DDL half — your off-`Base`
`view_metadata` `Table` in `models.py` stays, because that's your typed SELECT surface, so the
CLAUDE.md worker-extension contract still says "add the Column to `models.v_enriched`." And the
fork's SQLAlchemy-2.0 support should be confirmed from its own CI, not from the Alembic 1.18.0
changelog (that note vouches for the upstream package, a different distribution — the researcher
conflated them). If a new dependency in the migration path is unwelcome, the Alembic cookbook
`ReplaceableObject` recipe (`replaces=`/`replace_with=`) is the zero-dep 80% fix: it kills the
pasted-old-body problem without autogenerate. Either way, stop pasting view bodies.

## KEEP — no package provides this; it's domain glue or a correct thin wrapper

- **The cursor spine, `reprocess.py`, `partition.py`, the ledger.** No framework subsumes these
  without a rewrite (details under greenfield). Your crash-safety invariant — `advance_cursor` + all
  `enr_*` upserts + ledger + `set_status` commit in one transaction, so the cursor can never be
  ahead of the work — is actually stronger than what dlt/Singer/Airbyte give (they persist state
  separately, yielding at-least-once). Document the invariant; keep the code.
- **`finalize.py`.** The `ok/na/skipped/failed/dead → success/partial/degraded/failed` fold is a
  domain taxonomy, not a queue primitive. No job queue provides it and none should get credit for
  it. The whole audit found nothing here.
- **`limits.py`.** Already Prefect (see above). ~40 lines of testable pure/effect split +
  degrade-to-no-op is the right amount of code.
- **The SSRF idea is wrong (see RETHINK), but the pure `is_public_url` predicate stays** as a cheap
  pre-flight — it usefully adds `is_reserved`/`is_multicast` rejection.
- **`config.py` (pydantic-settings), explicit constructor injection, argparse CLIs,
  `testcontainers`, the hand-written fakes.** All confirmed correct. A DI container
  (`dependency-injector`, `svcs`) would add indirection and remove the property you most want —
  mypy strict seeing every dependency edge — to save ~40 lines across 3 ports. `vcrpy` cassettes
  would lose to your 3-line `FakeFetcher` because your HTTP port fetches arbitrary third-party
  pages, not a versioned API with a contract to drift from. `testcontainers` is the only faithful
  option since your SQL leans on real Postgres (`ON CONFLICT`, a real `VIEW`, transactional cursor
  advance). Don't touch any of these.

## RETHINK — the concept, not the library, is the problem

**5. The SSRF guard is the wrong shape for your threat model — and there's a fix already
installed.** You fetch URLs submitted by HN users (attacker-influenced), yet `is_public_url` does
zero DNS resolution and only inspects the initial URL string, while `HttpxFetcher` runs
`follow_redirects=True`. The researcher audited the current code on Python 3.12.3 and found these
bypasses not caught: a hostname that resolves to `169.254.169.254` (AWS/GCP metadata → credential
theft — this is the dangerous one), a hostname resolving to `127.0.0.1`, a 30x redirect to an
internal address (the guard never sees the redirect target), `nip.io`/`localtest.me` names, and
decimal/octal/hex IP encodings. IP literals like `::1` and `0.0.0.0` are caught fine — it's
everything involving name resolution or redirects that's blind.

The cheap fix is already in your `.venv`: Prefect 3.7.8 ships `SSRFProtectedHTTPTransport` in
`prefect.utilities.urls` (the researcher verified this by reading
`.venv/.../prefect/utilities/urls.py`). It resolves via `getaddrinfo`, rejects private-resolving
addresses, and connects to the pinned IP so the backend can't re-resolve — closing DNS rebinding,
and because httpx re-invokes the transport per redirect hop, re-validating every redirect target.
Build `HttpxFetcher`'s client with `transport=SSRFProtectedHTTPTransport()`, gate the import behind
your existing lazy-Prefect pattern, keep `is_public_url` as defense-in-depth, and add a test
asserting a redirect-to-metadata URL is refused (it's under `prefect.utilities`, not a stable public
API, so pin the Prefect version). The OWASP-correct hard boundary is a network-level egress proxy
(Stripe's Smokescreen), but that's a sidecar — treat it as target state; the transport is the
in-tree fix for this week. (This whole finding is the researcher's own primary-source audit; the
independent verifier didn't run before the reset, so treat the specific claims as "well-grounded,
worth confirming yourself" — but the metadata-endpoint exposure is real and I'd act on it.)

**6. The per-domain `RateLimiter` doesn't hold across your partition processes.** Its docstring says
"shared across every worker that fetches," but it's a `threading.Lock` + in-process `_next_allowed`
dict — and `partition.py` deliberately runs N schedulers as separate OS processes. A
`threading.Lock` is process-local, so your "minimum interval per domain" is silently enforced per
process: with N partitions you can hit a domain up to N× faster than configured — a real ban-risk
defect, not a style nit. Fix it behind the unchanged `PolitenessFetcher`/`RateLimiter` seam by
swapping the body of `acquire()` to use `pyrate-limiter` with its `PostgresBucket` backend, which
gives a cross-process budget backed by the Postgres you already run — no new infra. While you're
there: you have no robots.txt handling at all — if you intend to be a polite crawler, add `Protego`
(Scrapy's parser, pure-Python, 0.6.2) behind a small `RobotsPort` and feed its `crawl_delay()` into
the limiter interval. (Verifiers for `pyrate-limiter`/`Protego` also didn't run before the reset;
both are well-known current libraries, but confirm the `PostgresBucket` API before committing.)

## The greenfield question, answered separately

Should you rewrite the working, tested code on a framework? No. No single framework subsumes the
stack, and the closest — Dagster — is a control-plane-owning, DB-owning, service-heavy runtime that
fights everything your hexagonal `python -m`-simple design is for. Critically, even a full Dagster
migration would not retire `repo.py`'s per-item tables and ledger, because modelling one HN item as
one partition blows past Dagster's documented ~100k-partition ceiling (millions of items), and
partitioned assets have a known open bug (#22553) where `code_version` staleness isn't detected. So
you'd rewrite the spine, operate three new services and a second Postgres schema, and still own most
of `repo.py`. That clears no bar.

If you were starting from scratch today, the answer partially flips. If you'd partition by id-range
or time (which `partition.py` already does) rather than per-item, then Dagster's
`@asset(code_version=...)` + `AutomationCondition.code_version_changed()` + concurrency pools +
run-priority tags genuinely replace the version axis, `partition.py`, and `limits.py`, and its event
log replaces the coarse ledger — at the cost of operating Dagster and still hand-rolling the
politeness/SSRF layer and the fine-grained per-item outcome fold. So: existing project — keep it,
harvest the six items above; greenfield — Dagster is a defensible foundation for the orchestration
third of the system, but not for the crawl politeness or the per-item partial-success ledger, which
stay yours either way.

---

## Suggested sequencing

SSRF transport (security) → trafilatura (correctness + tiny) → pyrate-limiter (correctness) →
ads_count assembly (new feature) → alembic-utils-extended and respx (ergonomics).
