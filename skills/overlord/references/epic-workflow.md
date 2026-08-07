# Working from an epic doc

How an overlord run sources itself from an `epic-runner` output
(`docs/epics/<slug>.md`, or an epic doc the user pasted or pointed to) instead of
a raw idea. The epic has already been sliced and the intent already established.

1. **Pick the slice.** Match the feature the user named in their prompt to a
   slice in the epic doc's slice table / per-slice briefs. If the prompt doesn't
   clearly name one (or the name is ambiguous), ask the user, listing the slices
   whose dependencies are met as options.
2. **Check dependencies.** Confirm the chosen slice's `Depends on` slices are
   marked **done** in the doc. If a dependency isn't done, stop and ask whether
   to build the dependency first or proceed anyway.
3. **Seed the pipeline from the doc, not from scratch.** Use the slice's
   per-slice brief as the run's intent and thread the epic's **shared shape /
   architecture** into the data-flow and build stages so the slice composes with
   the rest of the epic instead of diverging.
4. **Run the normal pipeline** (stages 1–6 as applicable) on that slice —
   **skipping or sharply shortening stage 1 by default**: the epic already
   established intent, and the per-slice brief stands in for the PM brief.
   Re-interview only if the brief leaves a genuine fork open.
5. **Mark it done.** Once the slice passes the review gate, **update the epic
   doc**: set the slice's **Status → done**, note what now works end to end, and
   link any artifacts it produced. If the doc has a "Shipped so far" section,
   append to it. Tell the user you updated the doc, and surface any new
   cross-slice risk or re-slicing need the work revealed (don't silently edit the
   plan beyond status).

The Status column is owned by this workflow: the overlord updates it as slices
ship; the user only touches it for work done outside the pipeline.
