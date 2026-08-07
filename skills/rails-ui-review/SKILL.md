---
name: rails-ui-review
description: "Use after a UI change in a Rails app to confirm the page actually renders correctly — layout, spacing, empty/error/long-content states, responsive widths, console/JS errors — not just that specs pass. 'Review the UI', 'how does this look in the browser', 'screenshot the app', 'does this page render correctly', 'visual review'. Boots a throwaway instance in RAILS_ENV=test on a free port, seeds users and data for the session, drives a headless browser to screenshot the real pages, and assesses the render against the change or design. Catches what content-only system specs miss (unstyled pages, broken layout, 500s on untested views). Not for confirming a feature works mechanically (use verify), backend-only changes with no visible surface, or production — it runs the disposable test environment only."
---

# Rails UI Review

You are reviewing how a Rails change actually *looks and behaves in a browser*,
not whether its tests are green. System specs assert content (`have_text`), so
they sail past unstyled pages, broken grids, mispositioned elements, and even a
500 on a view no spec happens to render. The only way to catch those is to open
the real page, with real data, and look.

The core technique: **boot the app in `RAILS_ENV=test` on an unused port.** The
test database is disposable, so you can freely create users (any role, any
membership/permission state) and domain records for the session, screenshot the
pages those users see, then throw it all away — without touching the developer's
running server or polluting their dev data.

## When to use

- A change has a visible surface (a screen, form, table, modal, email-as-HTML)
  and you need to confirm it renders correctly, not just that specs pass.
- You want to see a page as a *specific kind of user* (admin vs member vs
  guest; a permission-limited role; a paid vs unpaid account).
- You need to inspect states that are awkward to assert in text: empty states,
  long-content overflow, error/validation styling, responsive breakpoints.

**Don't use** for: confirming a feature works end-to-end mechanically (use
`verify`), simply launching the app for the user to click around (just start
the dev server), pure backend/API/job changes with no visible output, or
anything against production. This skill runs the **test** environment only.

## Why `RAILS_ENV=test` on a free port (the whole idea)

- **Disposable data.** The test DB is meant to be wiped. Create exactly the
  users and records the review needs (`db:reset` afterward if you like). No risk
  to dev/prod data, no "please don't delete my test account."
- **No collision.** The developer's `bin/dev` is usually on the dev port (3000).
  Pick a free port so both can run at once and you never fight for the socket.
- **Real assets, real rendering.** It's the same stack the system specs drive,
  so the page renders exactly as it will — *provided the assets are built*
  (see the #1 gotcha below).
- **Seedable auth.** In most Rails apps, production SSO/OAuth is bypassed in
  dev/test in favor of a form login or a factory, so you can mint a user with a
  known password and log straight in.

## Process

### 1. Discover the project's setup (don't assume)
Read, in roughly this order:
- **Run + asset pipeline.** `Procfile.dev` / `bin/dev` / `package.json`. Is JS/CSS
  importmap (no build step) or **bundled** (jsbundling/cssbundling, esbuild/
  webpack + a `sass`/`tailwind` build)? Bundled apps **must** compile assets or
  every page looks unstyled — this is the most common failure.
- **Login mechanism.** `config/routes.rb` for `devise_for`, a sign-in path, or a
  dev/test-only login/impersonation/secret route. Note the exact path and the
  form field names.
- **User model + factories.** `spec/factories/*`, the `User` model — what fields
  drive role/permission/membership (an enum? a `role`? an external-id/type
  column?), and how a privileged user is built in tests (a `:admin` trait?).
- **Headless browser already present.** Check `Gemfile.lock` for **ferrum** /
  **cuprite** (Chrome via CDP — script it in pure Ruby, no install), or
  selenium; or `package.json` for playwright/puppeteer. Reuse the system-spec
  driver config (often `spec/support/cuprite.rb`) for window size + Chrome flags.

### 2. Prepare (assets + test DB + a free port)
- **Build assets first** (bundled apps): run the project's build (`yarn build &&
  yarn build:css`, `npm run build`, `rails assets:precompile`, etc.). Skipping
  this is why a page renders as raw HTML with no CSS — don't mistake that for the
  change being broken.
- **Prepare the test DB:** `RAILS_ENV=test bin/rails db:prepare` (or
  `db:test:prepare`). If you need a clean slate, `db:reset`.
- **Pick a free port** rather than hardcoding:
  `PORT=$(ruby -e 'require "socket"; s=TCPServer.new("127.0.0.1",0); print s.addr[1]; s.close')`

### 3. Boot the server in the background
`RAILS_ENV=test bin/rails server -p "$PORT" -b 127.0.0.1` — run it in the
background (the harness keeps it alive across turns) and poll `GET /up` (or any
200 route) until it answers before driving the browser. Remember the PID/port to
tear it down later. (If the test env sets `config.hosts`, add `127.0.0.1`/
`localhost`; if `config.public_file_server.enabled` is false in test, set
`RAILS_SERVE_STATIC_FILES=1`.)

### 4. Seed the session's users and data
Use a single `RAILS_ENV=test bin/rails runner` script. Create each user you need
with a **known password** and the role/state under review, plus any domain
records the page reads. Prefer the app's factories if loadable; plain
`Model.create!` is fine. Print the credentials/URLs you'll use so the browser
step is deterministic.

### 5. Drive the browser and screenshot
A real browser (not curl) so login/CSRF/JS just work. With Ferrum (preferred when
present) navigate to the login path, fill + submit the form, then visit each
target URL and save a full-page PNG. Capture the states that matter — **default,
empty, first-run (a brand-new record with no children yet), error/validation, long-content,
a wide desktop viewport (≥1680px), and a narrow viewport** — and collect any JS/console errors.

**The wide viewport is not optional and "wide" means ≥1680px.** A whole class of layout
bugs only appears wide: centered content with big side-margins, CSS-grid columns whose
`margin: auto` collapses a panel to its content width (shrink-wrap), elements that don't
reflow, popovers that flip at a screen edge. A mid width like 1400/1440 hides all of them —
size to a real desktop (and to the user's actual working width if you know it). Pair it
with the **empty / first-run** state: many of these bugs only exist when a surface has no
content yet (an insert row at the very top, a panel with nothing to size to).

**A default screenshot is only first paint — exercise the hidden content too.**
Anything behind an interaction (modals/dialogs, dropdown menus, tooltips/popovers,
accordions, tabs) and anything below the fold or lazy-loaded is *not* in the frame
unless you trigger it. For each page: **scroll to the bottom** to fire lazy-loaded
content and surface the footer/sticky elements, then **open every modal, dropdown,
tooltip, and collapsible** and screenshot each opened state — you're reviewing the
rendered UI, not just what happens to paint on load. (On a page with many repeated
menus, open a representative few; you're checking the component, not every instance.)

**For each opened overlay, confirm it is fully within the viewport — not clipped** by a
sticky header/topbar or an ancestor's `overflow`. This is the classic miss: a menu that
opens near a screen edge (or on an empty page where its trigger sits at the very top) gets
sliced off, yet the screenshot on a *populated* page or at a mid width looks fine. Open the
overlay in the state where its trigger is at an edge (e.g. the first-run/empty page), and if
a screenshot is ambiguous, verify in JS — `document.elementFromPoint(cx, cy)` at an item's
centre returns that item (not a covering ancestor), and its `getBoundingClientRect()` sits
inside the viewport.

**When the overlay renders a list (dropdown/combobox/menu), seed it across item counts —
empty, one, two, and many** (enough rows to fill or overflow its panel) — and screenshot the
*many* case, hit-testing a **lower/last** item. A 2–3 item list is above the clip line and
looks fine even when the panel is clipped one row down; the clip only appears when the list is
long. (This is exactly how a clipped dropdown ships green: the review seeded a short list.)

A reusable Ferrum template is in
[references/ferrum-template.md](references/ferrum-template.md) — size its wide
pass ≥1680px and adapt its selectors to the app's markup.

### 6. Review the screenshots
**Read each PNG** (the Read tool renders images) and judge it against the change
or the design:
- Layout & spacing — alignment, gaps, margins and paddings, element positions, things stretched
  full-width that shouldn't be, headings rendering at default browser sizes
  (a tell-tale sign a scoped stylesheet isn't matching the page). Check **sibling consistency**:
  panels/rows in the same column should share the same left/right insets (one missing its
  horizontal padding is a common miss).
- Width stability — the content width should be **stable regardless of how much content is
  present**. A panel that shrink-wraps to its content (narrow when near-empty, wider when full)
  is a bug — usually a grid/flex item with `margin: auto` and no `width`. Only visible wide.
- States — empty/first-run/error/loading/permission-limited actually styled, not raw. And the
  **interactive sub-states** a static design usually omits: dropdown-**open**, **selected**,
  **hover**, **focus**. A design typically shows only the closed/default state, so these are
  where native rendering slips in — open and shoot each one, don't assume it matches.
- **Native/default-rendered controls (a blocking defect, not polish)** — flag any element that
  renders with the browser's default look: an unstyled `<button>` (grey buttonface + a 3D/inset
  border), a native `<select>` arrow, a default focus outline, a raw checkbox/radio. This is the
  tell-tale that a **design-system class was applied to a different element than it was authored
  for** (e.g. option/row styles written for an `<a>` link, put on a `<button>`, keeping the
  button's UA chrome) or that a control was never styled. Open every menu/dropdown/picker and
  check its **option rows specifically** — "the panel is on-screen and hit-testable" does NOT
  mean its contents are styled. When unsure, measure the computed style (`background-color`,
  `border`, `appearance`) of a suspect option and compare it to how the same component renders
  elsewhere in the app.
- **Clipped decorative outsets** — a selection ring / focus halo / drop shadow drawn *outside*
  an element (`box-shadow: 0 0 0 Npx`, `outline`) is sheared by any ancestor with `overflow:
  hidden`/`auto` (and `overflow-y: auto` makes the browser clip the x-axis too). Select/focus an
  item at the **grid or container perimeter** — the top row, the outer column — where the clip
  actually shows, and confirm the full ring is visible on all four sides. An interior item hides
  the bug (its ring has sibling gaps to bleed into).
- Real-data stress — longest plausible string, zero, many.
- Responsive — what reflows/breaks at a narrow width AND what mis-lays-out (centering, side
  margins, shrink-wrap, overlay clipping) at a wide (≥1680px) width.
- Errors — any console/JS error, missing asset (404), or Rails error page.

### 7. Report
Findings with **severity + screenshot evidence + the `file:line`** of the view or
stylesheet to change (so a fix is one hop away). Distinguish "renders broken /
500 / unstyled" (blocking) from "spacing/polish" (minor). You **report**; fixing
is a separate step.

### 8. Tear down
Stop the background server (by PID/port). The test DB is disposable — reset it if
the seed data would confuse a later `rspec` run. Never leave a stray server bound
to the port.

## Critical gotchas (these are where reviews go wrong)
- **Unstyled page ≠ broken feature.** If everything looks like raw HTML, you
  almost certainly skipped the asset build (step 2) or a stylesheet is scoped to
  a selector the page doesn't match. Verify the compiled CSS exists and the
  page's wrapper id/class is covered before reporting "the design is broken."
- **A view that no spec renders can still 500.** That's exactly what this skill
  exists to catch — visit every changed view with realistic data.
- **Don't point the test server at the dev DB.** Keep `RAILS_ENV=test`
  everywhere (server, runner, db tasks) so you never write to dev data.
- **Background, then poll.** Don't `sleep` blindly — wait for a 200 from the
  server before the browser connects, or the first screenshot is a connection
  error.
- **Clean up.** Stop the server and reset the test DB; a leftover server holds
  the port and stale seed rows break later test runs.

## Validation — self-check before reporting
- [ ] Assets were built (or it's an importmap app) — an unstyled page was ruled
      out as an asset-build issue, not reported as a design defect.
- [ ] The server ran in `RAILS_ENV=test` on a confirmed-free port; the dev DB was
      never written to.
- [ ] Every **changed** view was actually visited and screenshotted with
      realistic data (so a no-spec-coverage 500 would surface).
- [ ] The states that matter (empty / first-run / error / long-content / a **wide ≥1680px**
      desktop / a narrow viewport) were captured, not just the happy default — and width was
      checked for stability (no shrink-wrap) at the wide size.
- [ ] Deferred/interactive content was revealed, not just first paint — scrolled to
      the bottom, and the page's modals, dropdowns, tooltips, and collapsibles were
      opened and screenshotted, **each confirmed fully within the viewport (not clipped)**
      including in the empty/first-run state where triggers sit at an edge.
- [ ] Every opened menu/dropdown/picker's **option rows** were checked for **native/default
      rendering** (unstyled `<button>`, native `<select>`, default focus ring) — not just that
      the panel is on-screen/hit-testable. Any element rendering with the browser default is a
      blocking defect (usually a component class on the wrong element).
- [ ] A **selected/focused item at the container perimeter** was checked so a selection
      ring / focus halo / shadow clipped by an ancestor `overflow` would surface.
- [ ] Console/JS errors and asset 404s were checked.
- [ ] Findings cite a screenshot + the `file:line` to change, with severity.
- [ ] The background server was stopped and the test DB left clean.

## Boundaries
- This skill **reviews and reports**; it does not fix the UI (hand findings to the
  implementer) and does not run against production.
- It runs the **test** environment with disposable data — never seed or screenshot
  real user data.
- Keep the server bound to `127.0.0.1`; don't expose the throwaway instance on a
  public interface.
