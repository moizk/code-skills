# Grounding a plan in the real system

Read this before investigating. It expands Step 2 of the `phased-plan` skill: what
counts as evidence for each finding, and how to get it cheaply. The output of this
step is the *Current state* and *Traps* sections of the plan — the parts that make
it worth more than a decomposition of the request.

The standard to hold yourself to: **every claim in the plan is either linked to a
file or backed by a number.** Anything else is a guess, and a guess in a plan gets
executed months later by someone who trusts it.

## 1. What exists that this reuses

Find the models, jobs, services, components, routes, and half-built precedents the
work will build on. Name each with a relative link from the plan's location, so a
fresh session can open it: `[Foo](../../app/models/foo.rb)`.

- **Reuse the pattern, not necessarily the mechanism.** If the repo already has an
  invite flow, a scheduled fan-out job, or a cached repository query, the plan
  follows that *pattern* and says so explicitly.
- **Say when you deliberately don't reuse the storage or mechanism, and why.** "The
  existing importer pattern applies; its per-row `find_or_create` does not, because
  this source arrives as a full snapshot." A silent departure from an established
  pattern reads as ignorance of it.
- **Look for the nearest thing someone already built.** `git log` / `git blame` on a
  similar file is usually the fastest route to the intended pattern *and* to the
  point where someone abandoned it.

## 2. What is half-built or dead

Systems that need a phased plan are usually systems with sediment. Dig for it —
this is the finding class that most often reshapes the phases:

- Commented-out code and feature flags that have been off for a year.
- Orphaned models whose backing tables were dropped, or tables nothing loads.
- Columns nothing reads, or that only a dead code path writes.
- Callbacks and hooks that have never fired correctly.
- Params silently dropped: a form or API sends a field, and nothing on the other
  side reads it. **A misspelled field on the wire is evidence nobody reads it** —
  that class of finding belongs in the plan.

**Verify dynamically where it's cheap.** Grep for readers, not just definitions;
check serializers and view templates for whether a field ever reaches a client;
check who actually calls a method. Static analysis proves a *reference* exists, not
that a code path *runs* — where that distinction matters, say which one you have.

## 3. Real counts, not vibes

Where a claim depends on data shape or on cost, measure it and put the numbers in a
table in *Current state*.

- **Data shape** — "most of this is write-only", "36k buildings are named
  `Chic Apartments`", "8% of rows have a null landlord". Query production-shaped
  data; don't infer distribution from the schema.
- **Cost** — timings, row counts, queue depth, coverage percentage.
- **Record it as a baseline.** The table is what later phases compare against, and
  the north star's success metric usually falls out of it. Note *when* and *against
  what* you measured, since the numbers age.

## 4. Traps

Anything that will bite the implementer, each as its own named subsection under
`## Traps`. Common classes:

- **Ordering traps** — a data migration must precede an enum change, in separate
  deploys, because the reverse order breaks every read. Where ordering *is* the
  trap, the fix ordering goes in the trap, not just in the phase.
- **Wire formats pinned by tests** — a rename that looks internal but is asserted
  against, or read by a client you don't control.
- **Deploy interactions** — a long-running job killed mid-flight by a deploy, work
  that isn't idempotent on retry, a cron that stacks up another full run each night.
- **Version pins** — a dependency pinned for a reason that isn't recorded.
- **Missing controls** — unauthenticated endpoints without rate limits,
  deliverability requirements on a new mail path, authorization that's incidental
  rather than enforced.
- **Look-alike columns** — two fields that appear interchangeable but are read by
  different clients.

## 5. House testing style

Read the project's testing docs and its existing tests, then state the actual
conventions in the plan so no phase introduces a foreign pattern:

- Fixtures vs. factories, and where test data lives.
- The mocking and HTTP-stubbing choice (a mocking library vs. recorded cassettes) —
  and whether the suite is allowed to touch the network at all.
- How jobs, mailers, and background work are asserted (the project's own helpers).
- Where system/end-to-end tests live and when they're expected.

The plan's *Testing* section then restates that style in one line and lists the
specific assertions per layer — including **a regression test named for each bug
the plan fixes**, and a **dedicated authorization suite** (not incidental coverage)
if the work touches cross-tenant data.

## Delegating the sweeps

Broad sweeps suit an exploration subagent: find-every-reader-of-this-column,
find-the-callers, what-does-the-serializer-expose, testing-convention scan,
when-was-this-last-touched. Give it a narrow question and ask for **conclusions
plus the file:line evidence** — keep those in the plan, not the file dumps.

## If grounding changes the premise

Sometimes the investigation invalidates the request: the data the feature assumes
doesn't exist, the bug has never actually fired, the precedent to extend is dead
code. **Say so at the top of *Current state* and reshape the phases around
reality.** Delivering a well-structured plan for the wrong problem is the most
expensive possible outcome of this skill.
