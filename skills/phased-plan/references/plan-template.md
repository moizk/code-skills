# Plan document skeleton

The structure for `docs/plans/<slug>.md`. Braced text is guidance — replace it, don't
ship it. Drop sections that genuinely don't apply, but drop them deliberately: *Not
doing*, *Traps*, and the per-phase *Checkpoint* are load-bearing and should survive
almost every plan.

```markdown
# Plan: {Name}

{2–4 sentence framing: the symptom, the root cause, and the shape of the fix.}

**Related:** [Plans index](README.md) · links to the technical/product docs this touches
**Status:** Not started

## North star

{What "done" looks like as observable behavior, not as a task list. "The queue drains
in hours, not days. A deploy does not reset it." Include the success metric you would
check in production, not just in tests.}

## Current state

{The grounded findings: what exists and is reused, what's dead or half-built and how
you verified it, the counts table with its baseline, and the root-cause analysis. If
N symptoms trace to fewer causes, say so — "four causes, not eleven problems" — and
diagram it. If grounding changed the premise of the request, say that here, first.}

| What | Count | Measured |
|---|---|---|
| {rows / calls / % coverage} | {number} | {when, against what} |

## Not doing

{Explicitly declined scope, recorded so it is not mistaken for an oversight. Each
item is a decision with an implied reason: "More worker threads as the first fix —
capacity already went 1→4." If a later plan partly reverses a decision, annotate it
rather than deleting it.}

## Traps

{One named subsection per trap. Include the fix ordering where the ordering *is* the
trap.}

### {Trap name}

{What bites, and what to do about it: "Data migration first, enum change second,
separate deploys — the reverse order breaks every read."}

Start a phase only when the previous checkpoint is done, or skip it explicitly here.

---

## Phase 0 — {only if needed: stop the bleeding / fix the data graph}

{Reserved for prerequisite ops or data work that everything else silently depends on
— backfills, draining a queue, reconciliation. If it involves an operator on
production, write the literal runbook steps and the exact commands. Flag it when it's
slow human work: "start early precisely because it is slow and unglamorous, and will
otherwise keep being deferred."}

## Phase N — {name that states the outcome}

### Goal

{One paragraph. Behavior, not tasks.}

### What we build

| Component | Source | Responsibility |
|---|---|---|
| [`path/to/file.rb`](../../path/to/file.rb) | create / modify / delete | one sentence |

{Call out behavior changes loudly: "Pagination is a behavior change; `per_page` is
the migration path." Where two patterns exist and one is wrong for this audience,
say which and why.}

### Checkpoint

- [ ] {Verifiable assertions, each checkable by a fresh session. Not "add pagination"
      but "the index paginates on every path, with per_page capped."}
- [ ] {For a phase that deletes: the measured evidence — "zero hits on the counter
      over two weeks" — not a static read-analysis.}

### Docs to update when this ships

{The specific product/technical pages that go stale.}

---

## Testing

{The house style restated in one line, then the specific assertions per layer: query
objects, jobs (the project's enqueue assertion), mailers, a regression test named for
each bug this plan fixes, authorization from both sides (A cannot read B's data,
through every route), and system tests where required. If the plan touches
cross-tenant data, authorization gets its own dedicated suite, not incidental
coverage.}

## What this does not cover

{Adjacent things a reader might reasonably assume are included. Prevents scope
confusion at execution time.}
```

## Notes on filling it

- **Status** is a live field, not decoration. It distinguishes "shipped in code" from
  operator steps still pending: "Phase 2 shipped; Phase 0's production drain still
  needs an operator."
- **Every path is a working relative link** from `docs/plans/`, so a fresh session
  can open it without searching.
- **Link, don't copy.** No schema dumps, no API reference, no pasted code beyond a
  signature — those go stale in place and start lying.
- **Phase numbering is stable.** If work gets inserted later, add `Phase 3b` rather
  than renumbering; the numbers appear in commits, tickets, and Status lines.
