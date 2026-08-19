# The plans index and the maintenance contract

A plan doc only stays useful if the repo knows how to keep it honest. Two things
carry that: an index at `docs/plans/README.md`, and a maintenance contract written
down where the executing session will actually read it.

## When to create the index

If this is the repo's **first** plan, offer to create `docs/plans/README.md` alongside
it. If the index already exists, add a row for the new plan and update the sequencing
section instead of rewriting it.

```markdown
# Plans

Living roadmaps for work that is not yet how this app works. Product and technical
docs describe current behavior; these describe how it should evolve.

| Plan | Status | What it covers |
|---|---|---|
| [{name}]({slug}.md) | Not started / Phase N shipped / Done | one line |

## Sequencing across plans

{Which plans run in parallel, which one goes first and why, and where two plans touch
the same code and must not be executed simultaneously. This is the part a reader
can't reconstruct from the individual plans.}

## Related quick wins

{Features already built and simply not connected, found while grounding the plans.
Each with a link and a one-line "what it would take". These are the cheapest value in
the repo and they vanish if they aren't written down.}

## How to execute a plan

Read the plan and every file it links for the phase you're doing. Confirm the
previous phase's checkpoint is checked (or explicitly skipped in the plan). Implement
that phase only. When it's done, check the checkpoint boxes, update the Status line,
and update the docs listed under "Docs to update when this ships" — in the same
change as the code.
```

## The maintenance contract

These rules belong in the plan or in the index — whichever the executing session is
more likely to read. Without them a plan silently drifts out of date and becomes
worse than no plan, because it still looks authoritative.

- **A phase's checkpoint gets checked in the same change as the code**, then the
  matching product/technical pages get updated. Not "later" — later never comes, and
  the next session can't tell shipped work from planned work.
- **Update the Status line as phases land**, and distinguish code that shipped from
  operator steps still pending.
- **Plans are not API docs or schema dumps.** Link, don't copy.
- **Annotate reversed decisions, don't delete them.** When a later plan partly
  reverses something in *Not doing* or a trap, note it in place. The record of why is
  the reason the doc is worth keeping.
- **Re-ground before executing a late phase.** A plan written months ago made claims
  about code and data that may have moved; the counts especially. Re-verify what the
  phase depends on before trusting it.
