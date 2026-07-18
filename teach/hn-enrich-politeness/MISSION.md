# Mission: The layer boundaries of hn-enrich

## Why

Rebuild hn-enrich (v5) with the boundaries right — re-applying the audit rules
from understanding rather than by copying files across. Copying a file carries
its code but not its reasons, and the reasons are the part that has to survive
the rebuild. The worked example is the `politeness.py` / `limits.py` pair, but
the skill being built is general: deciding where a seam goes and what lives on
each side of it.

## Success looks like

- Given a new rule ("wait 2s between hits on a domain", "cap live fetches at 8"),
  name the module that owns it and say why — without opening the repo.
- Redraw the `politeness.py` ↔ `limits.py` ↔ `deps.py` wiring from memory,
  including which way the import arrow points.
- State each audit rule as an invariant, not a patch — e.g. "every redirect hop
  is guarded before it is fetched" rather than "line 177 calls assert_public_url".
- Spot a boundary smell in a diff on `hn-enrich-review-01` and name what broke.
- Explain what `politeness.py` structurally *cannot* do, and why the egress
  proxy is the answer rather than more code inside the module.

## Constraints

- Simple English, real code quotes from this repo, before/after prototypes, and
  ASCII diagrams. See [NOTES.md](./NOTES.md).
- Lead with the established design-pattern name for a decision.
- `politeness.py` is frozen (see the SSRF egress-proxy decision) — lessons here
  explain and stress-test it; they do not propose edits to it.

## Out of scope

- Prefect operations (work pools, deployments, scheduling) beyond the one
  concurrency primitive `limits.py` stands on.
- The Postgres/repo layer, the workers, and the flows — until the fetch-path
  boundary is solid.
