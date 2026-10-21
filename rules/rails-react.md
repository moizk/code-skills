---
paths:
  - "**/*.jsx"
  - "**/*.tsx"
  - "**/app/javascript/components/**/*.js"
  - "**/app/javascript/hooks/**/*.js"
  - "**/app/javascript/api/**/*.js"
---

# React in Rails — components, hooks, API layer, mounting, Vitest tests

Applies to Rails apps whose frontend is React. Repos on Hotwire follow the
Stimulus rule instead, and a repo never mixes the two for new work.

## Where things live
| Kind | Location | Owns |
|---|---|---|
| Component | `components/<Name>.jsx` or `components/<Name>/` | one piece of UI with its CSS module and test beside it |
| Page | `pages/` | a route-level component composed from components |
| Hook | `hooks/use<Thing>.js` | reusable stateful logic, no markup |
| API module | `api/<resource>.js` | every request for one resource, through `api/client` |
| Helper | `helpers/` | pure functions, no React, no DOM |
| Behavior | `behaviors/` | vanilla enhancement of server-rendered markup |

- **Co-locate test and styles with the component:** `DivInput.jsx`, `DivInput.test.jsx`, `DivInput.module.css`. A directory once a component has children of its own.
- **Dependencies point one way:** pages → components → hooks → api → client. Helpers are leaves. A hook never imports a component; a component never imports a page.

## Components
- **Function components with hooks, `PropTypes` on every component** (TypeScript types in `.tsx`). An untyped prop is a silent break at the next rename.
- **Props down, callbacks up.** A component owns its own UI state (open, hovered, draft). Shared state lives in the nearest common parent or a hook, never on `document` or `window`. A `document.getElementById` inside a component is a value that should be a prop.
- **Derive, don't sync.** Anything computable from props and state is computed during render, not copied into state by an effect.
- **Effects are for subscriptions and imperative work only:** listeners, timers, third-party widgets. Every effect that adds something returns the function that removes it. Fetching is not an effect; it goes through SWR.
- **Keys are record identities**, never the array index for a list that filters or reorders.
- **Interactive elements are real `<button>`, `<a>`, or inputs with labels.** `jsx-a11y` errors are fixed, never disabled.
- **Style through the co-located CSS module and `clsx`.** Inline style objects only for truly dynamic values; global class names only from the design system.

## Hooks
- **Starts with `use`, returns a small stable API, contains no JSX.**
- **Extract a hook when two components share stateful logic or one component's effects outgrow its render.** One-off logic stays inline.
- **Reuse the existing hooks first** (debounce, click-outside, draft state) before writing a new one with the same job.

## Data and the API layer
- **No `fetch` outside `api/`.** ESLint enforces it. One module per resource exporting named functions; `api/client` alone owns the token, CSRF, query serialization, cancellation, and the `ApiError` shape.
- **Reads go through SWR with array keys** (`['listing', id]`) registered in the read table. **Mutations are direct calls** to the api module so SWR never replays them, followed by `mutate` on the keys they changed.
- **Handle `ApiError` by status, and stay silent on `isAbortError`** when the component unmounted mid-request.
- **Each api module camel-cases only the subtree it returns.** The client never converts keys.

## Mounting into Rails
- **The view renders a mount node whose `data` attribute carries JSON props;** `application.jsx` mounts the component inside `ErrorBoundary`, `SWRConfig`, and `Suspense`. Views never inline a `<script>` to boot React.
- **Every mount is lazy** (`React.lazy` with a dynamic `import`) so a page downloads only the chunks it renders. New components join the mount table the same way.
- **Server-rendered markup that needs a little behavior gets a `behaviors/` module, not a component:** a data-attribute selector, an idempotent `activate`, registered through `registerBehavior`. React is for UI that owns state.

## Tests (Vitest + Testing Library)
- **Query by role and accessible name first** (`getByRole('button', { name: 'Save' })`), then by text. `container.querySelector` only for elements with no role, never for class names the test chose.
- **Drive with `userEvent`.** `fireEvent` only for events it can't produce, such as focus on a non-focusable shell.
- **Fake timers for debounce and animation; stub globals in `beforeEach` and restore them in `afterEach`.** A test leaves nothing behind.
- **Hooks test through `renderHook`; api modules test request shape and error mapping against a mocked client**, never a live server.
- **One behavior per `it`, named as the spec it checks.** Run Vitest on the touched files before finishing; the Ruby suite does not cover them.
