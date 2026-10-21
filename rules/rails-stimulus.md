---
paths:
  - "**/app/javascript/controllers/**/*.js"
  - "**/app/javascript/controllers/**/*.ts"
  - "**/*_controller.js"
  - "**/*_controller.ts"
---

# Stimulus in Rails — small controllers that enhance server-rendered HTML

Applies to Rails apps on Hotwire (Stimulus + Turbo). Repos on React follow the
React rule instead.

## One controller, one behavior
- **Name it after the behavior, not the page:** `accordion_controller.js`, `bulk_select_controller.js`, `copy_to_clipboard_controller.js`. A page controller that does six things is six controllers.
- **File name and identifier match:** `audio_waveform_controller.js` is `data-controller="audio-waveform"`. Controllers autoload from `controllers/`; never register one by hand.
- **Small and composable.** Several controllers on one element is normal (`data-controller="modal form-dirty"`). A controller past roughly 150 lines is hiding a second behavior or plain logic that belongs in `lib/`.
- **Shared plain JavaScript lives in `lib/` or `utils/`** as exported functions with no Stimulus import. Controllers import it; it never imports a controller.

## Declare the contract
- **Everything the controller touches is declared up front:** `static targets`, `static values` with types and defaults, `static classes`, `static outlets`. No `querySelector` for an element that should be a target, no raw `dataset` reads for what should be a value.
- **Configuration comes from the markup through values** (`data-accordion-open-value="true"`), never from `window`, globals, or per-page constants.
- **Controllers talk through outlets or dispatched events** (`this.dispatch('selected', { detail })`), never by reaching into another element's controller instance.

## Lifecycle
- **`connect` sets up, `disconnect` tears down, symmetrically.** Every listener on `window` or `document`, timer, observer, or third-party widget created in `connect` is removed in `disconnect`. Turbo caches and restores pages, so a leaked listener fires twice after navigation.
- **`connect` must be idempotent.** Turbo and morphing reconnect controllers; guard on state rather than re-wrapping markup.
- **Use `[name]TargetConnected` / `[name]TargetDisconnected`** when targets arrive later (Turbo Streams, pagination) instead of re-querying.

## Progressive enhancement
- **The server renders the complete, usable no-JS state first.** The controller improves it: hides the extra slides, reveals the richer control. Nothing critical waits for `connect`.
- **Markup is written in ERB, never built in JavaScript.** Clone a `<template>` target or let a Turbo Stream insert it; string-concatenated HTML is not acceptable (see the UI rule).
- **Prefer Turbo for server round-trips.** Forms and links go through Turbo Drive, Frames, or Streams. A controller reaches for `fetch` only for a JSON side-call, with the CSRF token from the meta tag.
- **Respect user settings:** `prefers-reduced-motion` disables auto-animation, keyboard focus pauses rotation, and every pointer-reachable control is keyboard-reachable.

## Style
- **Actions are verbs read from the markup:** `data-action="click->accordion#toggle keydown.esc->accordion#close"`. Use key filters and action params (`data-accordion-index-param`) instead of parsing the event by hand.
- **Explain the why at the top of the file**, including the ticket and any accessibility rule honored. The code says the what.
- **No jQuery, no inline `onclick`, no state on `window`.**

## Tests
- **Controllers are tested through system specs** that drive the real page (see the Rails testing rule): open state, keyboard path, and on-screen assertions. Pure functions moved into `lib/` get unit tests when the project has a JS runner; otherwise keep them small enough for the system spec to cover.
