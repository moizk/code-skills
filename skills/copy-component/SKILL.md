---
name: copy-component
description: Faithfully copy, mirror, or port an existing component, screen, feature, or behavior from one place in the codebase to another — so the copy has the SAME behaviors and mechanism as its source, not merely the same look. Reads the source first, inventories every behavior (markup, styles, JS controller, library usage, keyboard/focus/aria, positioning, states), defaults to REUSING the source's mechanism rather than hand-rolling a simplified substitute, surfaces any omission as an explicit deviation, and diffs the result against the source before calling it done. Use whenever the instruction references an existing thing as the model to match. Triggers on "copy the X from Y", "mirror X", "port X", "clone X into …", "make it like the <existing screen/component>", "same as the course maker / the other page", "reuse the styles and js from X", "it works perfectly there — do it that way". NOT for a net-new component with no in-repo source to match, a one-line tweak, or designing something original (use ui-ux-plan).
---

# Copy Component — faithful port

Someone pointed at an existing thing in the codebase and said "make this new one like
that." The job is a **faithful copy**: the new thing must reproduce the source's
**behaviors and mechanism**, not just its appearance. The failure this skill exists to
prevent: copying the markup and the easy CSS, quietly *simplifying away* the parts that
made the original work (a positioning library, a keyboard/focus model, a shared editor),
shipping it green, and having the user come back with "why didn't you just copy it — it
works perfectly there?"

> **The target is fidelity to the source, not a plan.** A copy is "done" when it does
> what the source does — verified against the source. It is NOT done when it matches a
> freshly-written plan, because the plan is where behaviors get dropped.

## When to use

- The instruction names an **existing** component/screen/feature/behavior as the model:
  "copy X", "mirror X", "port X", "clone X", "make it like <existing>", "same as <existing>",
  "reuse the styles/js from X", "it works there — do it that way".
- You're recreating something the app already does, somewhere else in the app.

**Don't use** for a genuinely new component with no in-repo source (use `ui-ux-plan`), a
one-line tweak, or original design work. If there's no source to be faithful *to*, this
skill doesn't apply.

## The discipline

### 1. Read the source completely — inventory every behavior BEFORE writing anything
Open the actual source files and list what it does, from the files, not from memory. For a
UI component that means all of:
- **Markup & structure** — the element tree, roles, aria, the classes that carry behavior.
- **Styles** — the real CSS/SCSS, including the states (`:hover`, `.is-active`, `--modifier`,
  responsive rules) and *how* it's positioned (static? `position: fixed` via a library?).
- **JS** — the controller: targets, actions, every method. Note **library imports** (e.g.
  `@floating-ui/dom`, a shared rich-text editor, a sortable) — these ARE the mechanism.
- **Interaction model** — keyboard navigation, focus management, open/close, click-outside,
  escape, filtering/search, drag, autosave.
- **States & edge cases** — empty, first-run, long content, error, disabled, collapsed.

Write the inventory down (in the plan / a scratch note). This list is the definition of done.

### 2. Default to REUSE the mechanism — do not re-implement a simplified version
In priority order:
1. **Share it** — render the same partial / mount the same controller / call the same helper,
   parameterized. Best fidelity, least code.
2. **Copy it verbatim** — if sharing would over-couple, create a parallel copy that keeps the
   **same mechanism**: import the same library, mirror the same method shapes, reuse the same
   design tokens. A copy is a rename, not a rewrite.
3. **Never** substitute a hand-rolled simplification for the source's mechanism. Concrete tells
   from the real failure: a static CSS `bottom: 100%` in place of the source's Floating-UI
   positioning; a bare `contenteditable` in place of the shared rich-text editor; dropping the
   search box and keyboard nav "because there are only two items." Each of those passed tests and
   shipped a worse component the user had to send back.

### 3. Every omission is an explicit, user-approved deviation — never a silent "optional"
If you intend to leave out or simplify anything the source has, **say so and get sign-off**
before building. List it: "the source's menu has search + arrow-key nav + Floating-UI
positioning; I plan to include all three" — or, if cutting, "I plan to drop the search; ok?".
Words like "optional", "omitted", "port only a subset", "strip the engine", "single-item so no
need for X" in a plan are red flags: they're where fidelity leaks. A plan that enumerates a
subset of the source becomes the thing every later gate grades against, so the gap never surfaces.

### 4. Fidelity check before "done" — diff the copy against the SOURCE
Go back to the step-1 inventory and confirm each behavior is present in the copy:
- Does it have the same interactions (search, keyboard nav, drag, autosave, click-outside, escape)?
- Does it use the same mechanism (same library, same positioning, same shared component)?
- Same states (empty / first-run / collapsed / **one / two / long-many** / error)? For a list
  overlay, seed *many* items — clipping only shows when the panel is long.
- **Port every source declaration, even ones that look like no-op defaults** (`overflow: visible`,
  `flex: 0 0 auto`, `min-height: auto`). On the source these usually **override a shared base
  class** the copy *also* inherits; dropping them as "redundant" silently re-exposes the base
  behavior (a clipped dropdown, a collapsed/shrink-wrapped panel). Before omitting a rule that
  looks like a default, check what base class the element also carries.
- **For UI: screenshot the copy AND the source at the same viewport and the same state, and
  compare them side by side.** Do this at a real desktop width and in the empty/first-run state —
  positioning and layout bugs (clipping, shrink-wrap, edge-flip) hide at mid widths and in
  populated states. A behavior or affordance the source has and the copy lacks is a **defect**,
  not a scope cut.

## When running inside the overlord pipeline
- **Planning:** the plan's component section must carry the step-1 inventory and state "reuse the
  source's mechanism" as the approach; any cut is an explicit deviation surfaced to the user.
- **Review gate (stage 6):** add a **source-fidelity pass** — diff the built component against its
  source (behaviors + mechanism + a side-by-side screenshot). Missing source-behavior = a finding
  that gates, exactly like a correctness bug.

## Validation — self-check
- [ ] I read the actual source files and wrote a behavior/mechanism inventory before coding.
- [ ] The copy reuses the source's mechanism (shared, or copied verbatim incl. library imports) —
      no hand-rolled simplification stood in for the real thing.
- [ ] Every omission/simplification was surfaced and approved, not silently dropped or "optional".
- [ ] I diffed the finished copy against the source behavior-by-behavior; for UI, side-by-side
      screenshots at a real desktop width and in the empty/first-run state.
- [ ] Nothing the source does is missing from the copy without an explicit, approved reason.
