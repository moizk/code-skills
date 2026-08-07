---
paths:
  - "**/spec/**/*.rb"
  - "**/test/system/**/*.rb"
---

# Rails — system and feature specs

## UI / feature tests — assert what's actually visible, not just present in the DOM
System/feature specs assert content (`have_text`, `have_css`), so they pass on a
component that is present but **visually broken** — clipped, off-screen, collapsed, or
zero-size. Presence is not visibility. For interactive UI, add assertions the DOM check
misses:
- **Overlays (menus/dropdowns/popovers/tooltips/modals):** when you assert one opens, also
  assert it is **on-screen and hit-testable** — `document.elementFromPoint(cx, cy)` at an
  item's centre returns that item (not a covering ancestor / the sticky topbar), and its
  `getBoundingClientRect()` sits inside the viewport. Do it in the state where the trigger
  sits at a screen edge (an empty/first-run page), which is where clipping actually happens.
  A **list** overlay (dropdown/combobox/autocomplete/menu) is only clipped when its panel is
  tall enough to reach that edge, so drive it across item counts — **empty, one, two, and
  many** (enough to fill/overflow the panel's max-height) — and in the *many* case hit-test a
  **lower or last** rendered item, not just the first. A short list sits above the clip line,
  so a first-item check passes on a panel that is actually clipped one row down.
- **Keyboard & focus:** if a control has keyboard behavior, test it — focus lands where it
  should on open, arrow keys move an active/`.is-active` item, Enter/Escape do their thing.
  (Cuprite's `send_keys` is unreliable for arrows on inputs; dispatch a `KeyboardEvent` via
  `execute_script`, as the drag specs dispatch `DragEvent`s.)
- **Copying an existing component?** Mirror its existing spec's assertions too — if the
  source is tested for search/keyboard-nav/positioning and the copy isn't, the copy can
  silently drop those and still go green.
- Pixel-exact layout (margins, centering, shrink-wrap) is for `rails-ui-review`, not specs —
  don't assert exact pixels, but *do* assert the on-screen/hit-testable invariants above.
