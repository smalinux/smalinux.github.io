# Notes

## How this user wants to be taught

- **Simple English.** Short sentences. No jargon that has not been earned.
- **Name the pattern first.** Lead with the established design/architecture name
  (Decorator, Dependency Inversion, Null Object, Ports & Adapters), then explain
  it in plain words. The name is the handle they carry to the next problem.
- **Quote real code** from this repo, with `file:line`. Never paraphrase code
  that can be quoted, and never invent an example when the repo has one.
- **ASCII diagrams** over prose for anything with a shape.
- **Before/after prototypes** to make a design decision visible.

## Workspace

- Lives in `/src/hn-enrich/teach/` — deliberately *not* the repo root, so course
  material never mixes into the package or a commit. Decided 2026-07-17.
- The repo already carries the user's own `SMA:` margin notes in source
  (e.g. `ports.py:5`). Those are theirs — never commit them, never tidy them.

## Teaching state

- **Mission set 2026-07-17.** The user answered "all of the above" to the mission
  question (navigate / judge / design / rebuild). Those four nest rather than
  compete, so the mission is written as the outcome (rebuild v5 correctly) with
  the other three as the sub-skills. Worth re-confirming if lessons start to feel
  aimed at the wrong altitude.
- **No glossary yet.** Per GLOSSARY-FORMAT, terms get promoted only once the user
  can *use* them. Lessons 0001–0002 each end in a quiz that is the evidence gate.
  Candidate terms waiting on evidence: per-call policy, system capacity, the gate
  seam, fail-closed, check-then-use / TOCTOU, DNS rebinding, IP pinning, egress
  proxy, defense in depth, CGNAT range. (0002's reference already *lists* these
  as a glossary-in-waiting — promote to a real GLOSSARY.md once the user uses
  them back to me.)
- **No learning records yet.** Coverage is not learning; waiting for the quizzes.
- **quiz.js generalised (0002).** The widget now takes any two choice labels and
  optional `data-perfect` / `data-partial` flourish attrs; lesson 0001 pins its
  original copy via those attrs. Next lesson reuses it as-is.

## Lesson queue

1. ~~0001 — politeness.py vs limits.py: where does a rule live?~~ (written)
2. ~~0002 — The edge of the guard.~~ (written) Check-then-use / DNS rebinding;
   the two resolutions (`politeness.py:177` judges, `adapters.py:105` connects);
   why the fix is Smokescreen + egress rules, not more code; the CGNAT gap as the
   middle row of the ladder. Built on the buy-vs-build research. Shipped a new
   reference: `reference/ssrf-defense-in-depth.html`.
3. ~~0003 — Decorator over a Port.~~ (written) `PolitenessFetcher` is-a AND has-a
   `HttpFetcher`; before/after prototype (welded `if` vs decorator); the three
   seams table (Decorator / Dependency Inversion / Service Locator); quiz on
   "unit-testable with fakes?" that interleaves 0002 (rebinding below the seam)
   and the ports fake/real split. Reused the generalised quiz widget as-is.
4. ~~0004 — Pure plan, thin effect.~~ (written) Functional Core / Imperative
   Shell across `limits.py` + `teardown.py`; before/after on the destructive
   command; "which side of the line?" quiz (3 core / 3 shell, with the
   decide-the-message vs print-the-message pair as the crux); the recurring
   injected-effect seam table. Primary source: Bernhardt, *Boundaries*.
5. ~~0005 — The service locator, and its safe default.~~ (written) Service
   Locator + why it's forced (Prefect serializes task params to ids); the
   "honest step down" self-critique; the override seam (snapshots cache too);
   the inverted default (fake unless `use_real_*`) as safe-by-default, with the
   "a key alone selects nothing" / "credential is not consent" trap. Quiz:
   real-or-fake prediction (3 fake / 2 real, key-trap + fetcher-contrast).
   Primary counter-source: Seemann, "Service Locator is an Anti-Pattern."
6. ~~0006 — Mixed retrieval.~~ (written) Review, no new pattern. Two modes: free-
   recall cards (native `<details>`, new reusable `.recall` component — 5 cards,
   3 of them synthesis across two lessons) + a 9-item shuffled recognition quiz
   (no two consecutive from one lesson, answer-pairs vary so format gives no cue).
   Ends with the compression table and a hard push toward the user PRODUCING
   (arguing an open question) as the first real evidence gate.
7. FRONTIER IS NOW A DECISION, NOT A LESSON. Course has covered its mission scope
   (the fetch/ops boundary). Do NOT auto-continue to a 0007 on momentum. Next
   move depends on the user:
   - If they argue an open question → write GLOSSARY.md + LR-0001, then aim the
     next lesson at the demonstrated gap.
   - If they want to go wider → MISSION CHECK first (repo.py etc. are scoped out);
     confirm before expanding, possibly revise MISSION.
   - If they want to rebuild → shift from explain-mode to build-mode (the real
     mission); lessons become "apply the catalog to v5," not "read the code."

Fetch/ops path is now fully mapped (politeness, limits, ports, adapters,
teardown, deps + config). Off-path modules still untaught if the user wants to
go wider later: repo.py (the big one), workqueue.py, finalize.py, worker_run.py,
the flows/, inspect.py, view.py, models.py, source.py. Don't expand there without
a mission check — MISSION scopes those OUT until the fetch-path boundary is solid.

## Open questions raised (verify before teaching as fact)

- **Is `RateLimiter` per-process or truly global?** It uses `threading.Lock` +
  an in-memory dict, and `deps` caches one instance per process. Spacing holds
  across threads in one process, but if Prefect runs workers as separate
  processes, two workers could hit the same domain simultaneously — the
  docstring's "shared across every worker" would then be true only within a
  process. Raised as an *open question* in lesson 0003 (not asserted as a flaw).
  Resolve by checking the Prefect worker/task execution model for this repo
  before building any lesson that depends on the answer. If it IS per-process,
  that is a real finding for the v5 rebuild (the shared-limiter guarantee wants a
  shared backend — cf. pyrate-limiter's Redis/Postgres note in RESOURCES).

## Deferred artifacts

- ~~Patterns-catalog reference (`reference/seams-and-patterns.html`).~~ Built with
  0004: 6 patterns + injected-effect seam table + properties + anti-patterns,
  each row tagged with the lesson that teaches it. This is the v5 "moves to
  re-apply" card. Keep it in sync as later lessons add patterns.
- ~~GLOSSARY.md~~ — WRITTEN 2026-07-17 on the user's direct request (overriding the
  promote-on-use default). It is canonical-language reference, not a mastery
  record; the promote-on-use rule still applies to any NEW term from here.
- ~~First learning record~~ — LR-0001 WRITTEN 2026-07-17, on request. Written
  honestly: it records the baseline (0001–0006 covered-not-confirmed, no
  demonstrated understanding yet) rather than claiming mastery. Next real LR
  fires when the user actually demonstrates/discloses/corrects.
