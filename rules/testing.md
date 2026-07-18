# Testing

- **Every new feature must be covered with tests** unless the request explicitly says otherwise.
- Before finishing, **run the existing tests** and confirm they pass. If any fail, decide whether it's a bug in the new feature or an outdated/stale test.
- If it's a bug, **always fix the code rather than the test.** Only change a test when it's genuinely outdated and the code is correct.
- Every new page should be covered with an end-to-end test ui tests. If the page is simple and doesn't have complex interactions, a single test that verifies the main user flow may be sufficient. For more complex pages, consider adding additional tests to cover edge cases and different user interactions.

## Rules
- Test behavior, not implementation details
- Each test should verify one concept
- Tests should be independent — no shared mutable state between tests
- Every test name should read like a specification
- Keep in mind the testing pyramid: prefer unit tests for core logic, and use integration/feature tests for end-to-end flows and UI interactions.
- Keep in mind the possible flakiness of time-sensitive tests. If necessary, use time-mocking libraries to control time in tests.

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
