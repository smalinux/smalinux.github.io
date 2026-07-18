# Baseline: the fetch/ops boundary is covered, not yet confirmed

On 2026-07-17 the workspace was established and six explain-lessons (0001–0006)
mapped hn-enrich's entire live-fetch and operator path as *design decisions* —
the per-call/system boundary, check-then-use at the SSRF edge, Decorator over a
Port, Functional Core / Imperative Shell, and the Service Locator — closing with
a mixed-retrieval review. The user then requested the glossary and this record
directly. This matters because it fixes the baseline: the material has been
*covered*, but no understanding has been *demonstrated back* yet, and the teach
method treats those as different states.

## Evidence

None of the mastery kind so far: six "continue" requests, then a request for the
reference artifacts. If the 0006 mixed quiz or the free-recall cards were
attempted, the results were not reported to the teacher. So retention across
0001–0006 is presently unknown, not assumed.

## Implications

- **Treat 0001–0006 as covered-not-confirmed.** Before stacking new lessons on
  top, verify retention. Fastest probes: the user argues one standing open
  question (per-process `RateLimiter`; is `deploy_init`'s `ValueError` core or
  shell; what worker signatures would be if Prefect could pass objects), or
  re-takes the 0006 mixed quiz cold.
- **[[GLOSSARY]] is a reference, not a mastery record.** It was written on direct
  request as canonical language. The promote-on-use rule still applies to any
  *new* term introduced from here on.
- **The next move is a decision, not momentum.** Three doors, per [[MISSION]]:
  (1) the user demonstrates → aim the next lesson at the shown gap;
  (2) go wider into `repo.py` / workqueue / flows → these are out of mission
  scope, so do a mission check first;
  (3) switch from explain-mode to v5 build-mode — the actual mission — where
  lessons become "apply the [[GLOSSARY]] catalog to v5," not "read the code."
- Do **not** auto-generate a lesson 0007 on the next bare "continue"; surface the
  fork instead.
