---
paths:
  - "**/*.js"
  - "**/*.jsx"
  - "**/*.erb"
  - "**/*.html"
  - "**/*.css"
  - "**/*.scss"
  - "**/*.sass"
---

# Rails — UI / frontend

Applies to any Ruby on Rails project when doing the ui/frontend part.

## Reuse the app's design
- Prefer the app's existing styles, components, and UI elements. Look for an established design system / shared partials / helper components and use them.
- When something genuinely new is needed, build it to match the app's existing design language — don't introduce a foreign look, hardcoded colors, or ad-hoc one-off styles.
- If an element looks slightly different from the matching app component, still use the component — don't rebuild a near-duplicate. Apply the difference as a page-specific style override in CSS (scoped under the page/section class), keeping the shared component intact.

## Never ship default browser rendering
- **Default/native browser styling is a bug, not a neutral fallback** — whether or not a design was provided. An unstyled `<button>` (grey buttonface + 3D border), a native `<select>` arrow, a default focus outline, a native scrollbar, or a box-shadow/ring sheared by an ancestor's `overflow` all read as "half-built." If an element renders with the browser's default look, style it to the design system before calling it done.
- **Reusing a component's classes on a *different element* than it was authored for keeps that element's native chrome.** The classic trap: a design-system option/row styled for an `<a>` link, applied to a `<button>` — the button retains its UA background/border because the link styles never needed to reset them. When you do this, reset the native appearance (`appearance: none` + strip `background`/`border`, `font: inherit`) *or* use the same element the component uses. Prefer matching the element.
- **When you override a reused component, don't blanket-reset a property it sets in stateful variants.** A base `background: transparent` at a higher specificity will silently clobber the component's `:hover` / `.is-selected` / `.is-active` backgrounds. Re-assert those state backgrounds at your selector's specificity so the shared hover/selected/active treatments still paint.
- **A provided design usually shows only the default/closed state — you own the interactive sub-states.** Dropdown-open, selected, hover, focus, empty, and error states are yours to style to the system even when the design is silent on them. "The design didn't show it" is never a reason to accept the browser default; it's where native rendering slips in, so scrutinize exactly those states.
- **Watch `overflow` clipping decorative outsets.** A selection ring / focus halo / drop shadow drawn *outside* an element (`box-shadow: 0 0 0 Npx`, `outline`) gets clipped by an ancestor with `overflow: hidden`/`auto` (and setting `overflow-y: auto` makes the browser clip the x-axis too). Give the scroll/clip container padding (compensate with a negative margin to keep alignment), or draw the ring inset — and always eyeball a selected/focused item at the container's **perimeter**, where the clip actually shows.

## Map design values to existing SCSS variables
- When a Figma design (via the Figma MCP) or raw CSS provides concrete values — colors, spacing, font sizes, radii, shadows — don't paste the raw values. Map them to the app's existing SCSS variables (e.g. `$color-primary`, `$spacing-md`).
- Read the app's SCSS variables / tokens first and match each design value to the closest existing one. A design's `#1A73E8` or `16px` almost always corresponds to a variable already defined — use it.
- Only introduce a new variable when no existing one is a reasonable match, and define it alongside the others following the same naming convention — never hardcode the literal value inline.

## Don't build markup in JavaScript
- If JS needs to insert a UI element, define that element as an HTML `<template>` or a Rails partial and have the JS clone/insert it. Don't construct DOM via string concatenation or long `createElement` chains.
- Especially when the same element already appears in ERB: extract it to a shared partial so the server-rendered and JS-inserted versions stay identical and DRY.
- Example: a list where clicking "Add" inserts a new row — render the row from a `<template>` (or partial), and have the Stimulus controller clone that node, instead of hardcoding the row's HTML in JS and use the same element in the erb for building the list.

## Use Stimulus for JavaScript
- Write behavior as Stimulus controllers (targets, actions, values) rather than loose scripts or inline `onclick` handlers.

## Keep Ruby out of ERB
- Don't write complex Ruby logic inline in `.erb` files. Extract it to a helper.
- Name the helper following Rails conventions, prefixed with a namespace and the model name (e.g. `crm_lead_status_badge`, `applicant_verification_summary`).
